###########################################################
#
# Copyright (c) 2005, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#

__all__ = ['LoaderException', 'LoaderContext', 'ProdLoaderContext']


from pyasm.common import *
from pyasm.search import SearchType, Search
from pyasm.biz import *
from pyasm.prod.biz import *
from pyasm.prod.checkin import *
import os, types

from loader import *


class LoaderException(Exception):
    pass



# sample get_loader function
class LoaderContext(Base):
    '''contains all of the production logic for various process'''

    def __init__(my):
        my.context = None
        my.options = {}


    def set_options(my, options):
        if not options:
            return
        pairs = options.split("|")
        for pair in pairs:
            name, value = pair.split("=")
            my.options[name] = value


    def set_option(my, name, value):
        my.options[name] = value


    def get_option(my, name):
        if my.options.has_key(name):
            return my.options[name]
        else:
            return ""


    def set_context(my, context):
        my.context = context

    def get_context(my):
        return my.context

    # virtual methods
    def is_instance_culled(my, ref_instance):
        raise LoaderException("Must overload this function")


    def get_snapshot(my, ref_node, context=None, latest=True):
        raise LoaderException("Must overload this function")

    def get_loader(my, snapshot, context=None):
        raise LoaderException("Must overload this function")




class ProdLoaderContext(LoaderContext):
    '''The context which productions assets are loaded.  This class contains
    all of the nasty details about context loading'''

    LATEST = '-- LATEST --'

    def __init__(my):
        super(ProdLoaderContext,my).__init__()
        my.shot = None
        my.shot_search_type = 'prod/shot'

    def set_shot(my, shot):
        my.shot = shot


    def set_shot_search_type(my, stype):
        my.shot_search_type = stype

    def get_defined_model_contexts(my):
        pipes = Pipeline.get_by_search_type('prod/asset',\
            Project.get_project_code())
        contexts = []
        for pipe in pipes:
            # NOTE: only add a separator within the model pipelines
            # there shouldn't be any between model and anim pipeline
            contexts.append('')
            contexts.extend(pipe.get_process_names())
            

        # in the model pipeline, there is a publish context
        contexts.append('publish')
        return contexts

    def get_defined_anim_contexts(my):
        pipes = Pipeline.get_by_search_type('prod/shot',\
            Project.get_project_code())
        contexts = []
        for pipe in pipes:
            contexts.extend(pipe.get_process_names())
        return contexts




    def is_instance_culled(my, ref_instance):

        # if there is no shot, then it cannot be culled 
        if my.shot == None:
            return False

        # get latest cull snapshot
        instance = ShotInstance.get_by_shot(my.shot,"cull")
        if not instance:
            return False

        cull_snapshot = Snapshot.get_latest_by_sobject(instance)

        # a cull is a snapshot in a shot
        #cull_snapshot = Snapshot.get_latest_by_sobject(my.shot,"cull")
        if cull_snapshot == None:
            return False

        xml = cull_snapshot.get_xml_value("snapshot")
        cull_instances = xml.get_values("snapshot/ref/@instance")

        if ref_instance in cull_instances:
            return True
        else:
            return False





    def get_snapshot(my, ref_node, context=None, latest=True, recurse=False):
        '''get a snapshot based on a reference node in the snapshot'''

        # if there is an explicit snapshot given, then just use that
        snapshot_code = Xml.get_attribute(ref_node,"snapshot_code")
        if snapshot_code != "":
            snapshot = Snapshot.get_by_code(snapshot_code)
            return snapshot

        # if no context is specified, use the loading context
        if context == None:
            context = my.context


        # determine if this should be replaced with a proxy snapshot
        proxiable_contexts = my.get_defined_model_contexts()
        if my.get_option("proxy") == "yes" and context in proxiable_contexts:
            context = "proxy"

        # check if getting the latest
        if latest == True:
            version = -1
            revision = -1
        else:
            version = Xml.get_attribute(ref_node,"version")
            revision = Xml.get_attribute(ref_node,"revision")


        # get the snapshot that was explicitly asked for
        search_type = Xml.get_attribute(ref_node,"search_type")
        search_id = Xml.get_attribute(ref_node,"search_id")

        sobject = Search.get_by_id(search_type, search_id)

        # if the context is a shot context, then load the instance, otherwise
        # load the asset
        if isinstance(sobject, Asset) and \
                context in my.get_defined_anim_contexts():
            asset = Asset.get_by_id(search_id)

            instance_name = Xml.get_attribute(ref_node,"instance")
            ref_snapshot = my.get_snapshot_by_sobject(sobject,context,version,revision,recurse)

        else:
            ref_snapshot = my.get_snapshot_by_sobject(sobject,context,version,revision,recurse)
        return ref_snapshot


    def get_snapshot_by_search_type(my, search_type, search_id, \
            context,version=-1, recurse=False):
        sobject = Search.get_by_search_type(search_type, search_id, recurse)
        return my.get_snapshot_by_sobject(sobject, context, version)




    def get_snapshot_by_sobject(my, sobject, context, version=-1, revision=-1,\
            recurse=False):
        '''get the snapshot by sobject info'''

        search_type = sobject.get_search_type()
        search_id = sobject.get_id()

        if context == my.LATEST:
            context = None
        # find the reference snapshot
        ref_snapshot = Snapshot.get_by_version( \
                search_type, search_id, context, version)


        if recurse and not ref_snapshot:
            # FIXME: assume process == context for now and remove hard coded
            # assumption
            process = context
            if process == "publish":
                process = "rig"

            # store the instance if it is one
            if isinstance(sobject, ShotInstance):
                my.shot_instance = sobject
            else:
                my.shot_instance = None

            ref_snapshots = my.get_input_snapshots(sobject, process, recurse)
            if ref_snapshots:
                ref_snapshot = ref_snapshots[0]

        return ref_snapshot




    def get_output_snapshots(my, sobject, process, recurse=False):
        return my.get_snapshots(sobject, process, mode="output")


    def get_input_snapshots(my, sobject, process, recurse=False):
        return my.get_snapshots(sobject, process, mode="input", recurse=False)



    def get_snapshots(my, sobject, process, mode="input", recurse=False):
        '''recursive functions that goes back in the pipeline to find
        snapshots'''

        assert mode in ['input', 'output']
       
        # process not selected
        if not process:
            return []
        # HACK: add this to make it work
        # store the instance if it is one
        if isinstance(sobject, ShotInstance):
            my.shot_instance = sobject
        else:
            my.shot_instance = None

        
        # TOOD: the sobject should define the pipeline
        # determine the pipeline of the sobject
        if my.shot_instance:
            pipeline_sobject = my.shot_instance.get_parent(my.shot_search_type)
        else:
            pipeline_sobject = sobject

        if not pipeline_sobject:
            return []

        pipeline_code = pipeline_sobject.get_value("pipeline_code")
        pipeline = Pipeline.get_by_code(pipeline_code)
        if not pipeline and not my.shot_instance:
            Environment.add_warning("No pipeline %s" %sobject.get_code(),\
                "No pipeline exists for [%s]" % sobject.get_code() )
            # we will try to return the snapshot below for output in this case
            if mode == 'input':
                return []
        
        # get the dependent processes and contexts
        if pipeline:
            process_names = pipeline.get_process_names()
            if not process_names:
                return []
            if mode == "input":
                #process_objs = pipeline.get_input_processes(process)
                #processes = [p_obj.get_name() for p_obj in process_objs]
                processes = pipeline.get_backward_connects(process)
                contexts = pipeline.get_input_contexts(process)
            else:
                contexts = pipeline.get_output_contexts(process)
                c = []
                for context in contexts:
                    if context not in c:
                        c.append(context)
                contexts = c
                processes = [process for x in contexts]
        else: # if pipeline code is missing or outdated
            processes = [process]
            contexts = [process]

        # first process of a pipeline may not have an input
        
        is_input_first_process = (pipeline \
            and process == process_names[0]) \
            and (mode== 'input')

        if not is_input_first_process and not processes:
            Environment.add_warning("Process not found %s" %sobject.get_code(),\
                "No %s processes for process [%s]" % (mode, process))
            return []


        # go through each process and context and find input or output snapshots
        ref_snapshots = []
        for i in range(0, len(processes)):

            # TODO: should get this from connect object
            back_process = processes[i]
            back_context = contexts[i]

            # prevent infinite loops
            #if mode == "input" and process == back_process:
            #    raise LoaderException("Infinite Loop: process '%s' is dependent on itself" % process)

            # if there is no context, then use the process
            if not back_context:
                back_context = back_process


            # if there is a / in the process, then this process is from another
            # pipeline
            # FIXME: Big assumption that a reference process to another pipeline
            # has a prod/asset sobject
            tmp_sobj = sobject
            if back_process.find("/") != -1:
                pipeline_code, process = back_process.split("/")
                if my.shot_instance:
                    tmp_sobj = my.shot_instance.get_parent("prod/asset")

            if not tmp_sobj:
                continue

            search_type = tmp_sobj.get_search_type()
            search_id = tmp_sobj.get_id()


            if mode == "input":
                # get the current snapshot back snapshot
                ref_snapshot = Snapshot.get_current(search_type,search_id,back_context)

                if not ref_snapshot:
                    ref_snapshot = Snapshot.get_latest(search_type,search_id,back_context)
            else:
                # output always gets the latest snapshot back snapshot
                ref_snapshot = Snapshot.get_latest(search_type,search_id,back_context)


            # if there is no snapshot, then recurse down
            #if recurse and not ref_snapshot:
            #    ref_snapshot = my._get_back_snapshot(sobject, back_process, back_context)

            if ref_snapshot:
                ref_snapshots.append(ref_snapshot)

        return ref_snapshots









    def get_updater(my, snapshot, asset_code, namespace, context=None):
        assert snapshot != None

        if context == None:
            context = my.context
        updater = None
        snapshot_type = snapshot.get_snapshot_type()
        if snapshot_type == "set":
            updater = MayaGroupUpdaterCmd()
        elif snapshot_type in ["anim", "anim_export"]:
            updater = MayaAnimUpdaterCmd()
        elif snapshot_type == "asset":
            updater = MayaAssetUpdaterCmd()
        elif snapshot_type == "shot":
            updater = MayaShotUpdaterCmd()
        '''
        # not implemented yet
        elif snapshot_type == "layer":
            updater = MayaLayerUpdaterCmd()
        elif snapshot_type == "file":
            updater = MayaFileUpdaterCmd()
        
        else:
            raise LoaderException("No loader for snapshot [%s]" % \
                snapshot.get_code() )
        '''
        # NOTE: updater can be None for texture type snapshot
        # set the updater context here for now

        if updater:
            updater.set_loader_context(my)
            updater.set_snapshot(snapshot)
            updater.set_asset_code(asset_code)
            updater.set_namespace(namespace)

        return updater

    def get_template_loader(my, sobject, context=None):
        from pyasm.flash import FlashLoad

        loader = TemplateLoaderCmd()
        if context == None:
            context = my.context
        loader.set_loader_context(my)
        flash_load = FlashLoad(sobject)
        template = flash_load.get_template()
        tmpl_fla_link, tmpl_fla = flash_load._get_file_info(template)
        
        default_template = "flash-shot_default.fla"
        if sobject.get_base_search_type() == 'flash/asset':
            "flash-asset_default.fla"
        if not tmpl_fla_link:
            tmpl_fla_link, tmpl_fla = flash_load.get_default_template(default_template)
            loader.file_path = tmpl_fla_link
        else:
            snapshot = Snapshot.get_latest_by_sobject(template)
            loader.set_snapshot(snapshot)
        return loader

    def get_loader(my, snapshot, context=None):

        assert snapshot != None

        if context == None:
            context = my.context

        snapshot_type = snapshot.get_snapshot_type()
        if snapshot_type == "set":
            loader = MayaGroupLoaderCmd()
        elif snapshot_type == "anim":
            loader = MayaAnimLoaderCmd()
        elif snapshot_type == "anim_export":
            loader = MayaAnimExportLoaderCmd()
        elif snapshot_type == "asset":
            loader = MayaAssetLoaderCmd()
        elif snapshot_type == "layer":
            loader = MayaGroupLoaderCmd()
        elif snapshot_type == "file":
            loader = MayaFileLoaderCmd()
        elif snapshot_type == "shot":
            loader = MayaShotLoaderCmd()
        elif snapshot_type == "flash":
            loader = FlashAssetLoaderCmd()
        else:
            loader = MayaAssetLoaderCmd()
            #raise LoaderException("No server loader defined for snapshot [%s] with snapshot_type [%s]" % (snapshot.get_code(), snapshot_type) )

        # set the loader context here for now
        loader.set_loader_context(my)
        loader.set_snapshot(snapshot)

        return loader


    def get_publisher(my, type):
        publisher = None
        if type == 'flash':
            publisher = FlashAssetPublisherCmd()
            
        publisher.set_asset_code(my.get_option('code'))

        return publisher




