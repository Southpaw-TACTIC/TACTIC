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

__all__ = ["ServiceException", "BaseXMLRPC", "CreateSetAssetsCmd"]

import shutil, os

from pyasm.common import System, TacticException
from pyasm.security import *
from pyasm.search import *
from pyasm.command import Command

from pyasm.checkin import FileGroupCheckin
from pyasm.prod.checkin import *
from pyasm.prod.biz import *
from pyasm.prod.load import *
from pyasm.prod.queue import Queue

from pyasm.web.app_server import XmlrpcServer
from pyasm.web import WebContainer
from pyasm.biz import Project, Snapshot

class ServiceException(Exception):
    pass

class BaseXMLRPC(XmlrpcServer):

    METHODS = ['get_loader_xml',       \
               'get_shot_loader_xml',  \
               'update_session',       \
               'create_assets',        \
               'get_update_xml',       \
               'create_set',           \
               'checkin_set',          \
               'checkin_shot_set',     \
               'get_instances_by_shot_xml', \
               'checkin_flash_shot',    \
               'set_project'            \
            ]


    def init(my, ticket):
        XmlRpcInit(ticket)

        # initialize the web environment object and register it
        adapter = my.get_adapter()
        
        WebContainer.set_web(adapter)
       
        my.set_templates()
        

    def set_project(my, project_code):
        my.project_code = project_code
        return True
    set_project.exposed = True

    def set_templates(my):
        pass


    def exposedMethods(my):
        return my.METHODS


    def get_loader_xml(my, ticket, project_code, snapshot_code, context="", options=""):
        '''uses the loader to generate an execute xml that can be
        used to load the assets'''
        try:
            my.init(ticket)
            Project.set_project(project_code)

            snapshot = Snapshot.get_by_code(snapshot_code)

            # get the loader implementation
            loader_context = ProdLoaderContext()
            loader_context.set_context(context)

            # pass on any message options for the loader
            if options != "":
                loader_context.set_options(options)

            loader = loader_context.get_loader(snapshot)
            loader.execute()

            execute_xml = loader.get_execute_xml()
            xml = execute_xml.get_xml()

        finally:
            DbContainer.close_all()
        
        return xml
    get_loader_xml.exposed = True
    
    def get_update_xml(my, ticket, project_code, snapshot_code, asset_code, instance, context='', options=''):
        '''an update xml to update node info'''
        try:
            my.init(ticket)
            Project.set_project(project_code)
            
            snapshot = Snapshot.get_by_code(snapshot_code)

            # get the loader implementation
            loader_context = ProdLoaderContext()
            loader_context.set_context(context)
            if options != "":
                loader_context.set_options(options)

            loader = loader_context.get_updater(snapshot, asset_code, instance)
            loader.execute()

            execute_xml = loader.get_execute_xml()
            xml = execute_xml.get_xml()

        finally:
            DbContainer.close_all()
        return xml

    get_update_xml.exposed = True
   

    def get_shot_loader_xml(my, ticket, project_code, snapshot_code, shot_code, instance_name, context="", options=""):
        '''uses the loader to generate an execute xml that can be
        used to load the assets'''
        try:
            my.init(ticket)
            Project.set_project(project_code)

            snapshot = Snapshot.get_by_code(snapshot_code)

            # get the shot
            shot = Shot.get_by_code(shot_code)
            if not shot:
                raise ServiceException("No shot [%s] exists" % shot_code)


            # get the loader implementation
            loader_context = ProdLoaderContext()
            loader_context.set_shot(shot)
            loader_context.set_context(context)

            # pass on any message options for the loader
            if options != "":
                loader_context.set_options(options)

            loader = loader_context.get_loader(snapshot)

            # just set the shot if we are loading the shot
            if shot_code == instance_name:
                loader.set_instance(shot)
            else:
                instance = ShotInstance.get_by_shot(shot, instance_name)
                if not instance:
                    raise TacticException('Asset Instance [%s] not found in shot [%s]'%(instance_name, shot.get_code()))
                loader.set_instance(instance)

            # setting all instances in anim to be loaded with the unique flag
            loader.set_unique()

            loader.execute()

            execute_xml = loader.get_execute_xml()
            xml = execute_xml.get_xml()

        finally:
            DbContainer.close_all()
        
        return xml

    get_shot_loader_xml.exposed = True


    def update_session(my, ticket, project_code, user, pid, data):

        try:
            my.init(ticket)
            Project.set_project(project_code) 
            # get the session sobject
            sobject = None
            search = Search("prod/session_contents", project_code=project_code)
            search.add_filter("login", user)
            search.add_filter("pid", pid)
            sobject = search.get_sobject()

            # if none exists, then create one
            if sobject == None:
                search_type = SearchType.build_search_type('prod/session_contents', project_code)
                sobject = SearchType.create(search_type)
                sobject.set_value("login", user)
                sobject.set_value("pid", pid)

            sobject.set_value("data", data)

            impl = search.get_database_impl()
            sobject.set_value("timestamp", impl.get_timestamp_now(), quoted=False)
            sobject.commit()

        finally:
            DbContainer.close_all()

        return True

    update_session.exposed = True


    def create_assets(my, ticket, project_code, set_code, names):

        try:
            my.init(ticket)
            Project.set_project(project_code)

            cmd = CreateSetAssetsCmd()
            cmd.set_set_code(set_code)
            cmd.set_names(names)
            Command.execute_cmd(cmd)
            asset_codes = cmd.get_asset_codes()
        finally:
            DbContainer.close_all()

        return asset_codes

    create_assets.exposed = True

       
    def create_set(my, ticket, project_code, set_name, cat_name, selected):
        '''an xml to create a new set node'''
        xml = ''
        asset_code = ''
        try:
            my.init(ticket)
            Project.set_project(project_code)
            cmd = MayaSetCreateCmd()
            cmd.set_set_name(set_name)
            cmd.set_cat_name(cat_name)
            
            Command.execute_cmd(cmd)
            
            asset_code = cmd.get_asset_code() 
            if asset_code:
                cmd = CreateSetNodeCmd()
                cmd.set_asset_code(asset_code)
                cmd.set_instance(set_name)
                cmd.set_contents(selected)
                cmd.execute()
                execute_xml = cmd.get_execute_xml()
                xml = execute_xml.get_xml()
                
        finally:
            DbContainer.close_all()
        
        return [xml, asset_code]

    create_set.exposed = True


    def checkin_set(my, ticket, project_code, asset_code, context):
        snapshot_code = ''
        try:
            my.init(ticket)
            Project.set_project(project_code)

            new_set = Asset.get_by_code(asset_code)
            checkin = MayaGroupCheckin(new_set)
            checkin.set_context(context)
            checkin.set_description("Initial Publish")
            Command.execute_cmd(checkin)
            snapshot_code = checkin.snapshot.get_code()
        finally:
            DbContainer.close_all()
          
        return snapshot_code

    checkin_set.exposed = True


    def checkin_shot_set(my, ticket, project_code, shot_code, process, context, \
             checkin_as, currency, unknown_ref, desc):
        snapshot_code = ''
        try:
            my.init(ticket)
            Project.set_project(project_code)

            shot = Shot.get_by_code(shot_code)
            checkin = ShotCheckin(shot)
            checkin.set_description(desc)
            checkin.set_process(process)
            checkin.set_context(context)

            is_current = True
            if currency == 'False':
                is_current = False
            is_revision = False
            if checkin_as == 'Revision':
                is_revision = True

            checkin.set_current(is_current)
            checkin.set_revision(is_revision)
            checkin.set_option("unknown_ref", unknown_ref)
            Command.execute_cmd(checkin)
            snapshot_code = checkin.snapshot.get_code()

        finally:
            DbContainer.close_all()
          
        
        return snapshot_code

    checkin_shot_set.exposed = True


    """
    def get_snapshot_file(my, search_key, context):
        '''gets the last checked in snapshot for this sobject and context
        and retrieves the files already checked in'''
    get_snapshot_file.exposed = True
    """




    def get_instances_by_shot_xml(my, ticket, project_code, shot_code, with_template=True, with_audio=True):
        ''' retrieve flash asset instances in a shot'''
        try:
            my.init(ticket)
            Project.set_project(project_code)
            
            shot = Shot.get_by_code(shot_code)
            if not shot:
                raise ServiceException("No shot [%s] exists" % shot_code)


            # get the instances and then get the latest assets
            instances = ShotInstance.get_all_by_shot(shot)

            asset_codes = SObject.get_values(instances, "asset_code", unique=True)

            search = Search(Asset)
            search.add_filters("code", asset_codes)
            assets = search.get_sobjects()

            uber_xml = []
            uber_xml.append("<execute>")

            if with_template:
                loader_context = ProdLoaderContext()
                # hard-coded in TemplateLoaderCmd for now
                #loader_context.set_option('instantiation', 'open')
                tmpl_loader = loader_context.get_template_loader(shot)
                tmpl_loader.execute()
                execute_xml = tmpl_loader.get_execute_xml()
                xml = execute_xml.get_xml()

                xml = Xml(string=xml)
                nodes =  xml.get_nodes("execute/*")
                for node in nodes:
                    uber_xml.append( "    %s" % xml.to_string(node, pretty=False) )

            if with_audio:
                shot_audio = ShotAudio.get_by_shot_code(shot_code)
                # assuming shot_audio uses 'publish' context
                if shot_audio:
                    context = "publish"
                    inst_mode = "import_media"
                    my._append_xml( shot_audio, context, inst_mode, uber_xml )

            for asset in assets:
                context = "publish"
                inst_mode = "import"
                my._append_xml( asset, context, inst_mode, uber_xml )

            
            loader_context = ProdLoaderContext()
            loader_context.set_context(context)
            loader_context.set_option('code', shot_code)

            # add publish instructions
            publisher = loader_context.get_publisher('flash')
            publisher.execute()
            xml = publisher.get_execute_xml().get_xml()
            
            xml = Xml(string=xml)
            nodes =  xml.get_nodes("execute/*")
            for node in nodes:
                uber_xml.append( "    %s" % xml.to_string(node, pretty=False) )


            uber_xml.append("</execute>")
            uber_xml = "\n".join(uber_xml)
        finally:
            DbContainer.close_all()

        return uber_xml
    get_instances_by_shot_xml.exposed = True


    def _append_xml(my, asset, context, inst_mode, uber_xml ):
        '''append xml to the uber_xml'''
        snapshot = Snapshot.get_latest_by_sobject(asset, context)
        loader_context = ProdLoaderContext()
        loader_context.set_context(context)
        loader_context.set_option('instantiation', inst_mode)
        loader = loader_context.get_loader(snapshot)
        loader.execute()

        execute_xml = loader.get_execute_xml()
        xml = execute_xml.get_xml()
        xml = Xml(string=xml)
        nodes =  xml.get_nodes("execute/*")
        for node in nodes:
            uber_xml.append( "    %s" % xml.to_string(node, pretty=False))


    def checkin_textures(my, ticket, project_code, asset_code, paths, file_ranges, node_names, attrs, use_handoff_dir=False, md5s=[]):
        '''creates a number of textures under a single asset'''
        new_paths = []
        try:
            my.init(ticket)
            Project.set_project(project_code)

            parent = Asset.get_by_code(asset_code)
            #parent = Search.get_by_search_key(search_key)
            context = 'publish'
            checkin = TextureCheckin(parent, context, paths, file_ranges, node_names, attrs, use_handoff_dir=use_handoff_dir, md5s=md5s)
            Command.execute_cmd(checkin)

            new_paths = checkin.get_texture_paths()
            #md5_list = checkin.get_texture_md5()
            file_code_list = checkin.get_file_codes()
            
            #loader_context = ProdLoaderContext()
            #updater = loader_context.get_updater(snapshot, asset_code, instance)
            #execute_xml = updater.get_execute_xml()
            #xml = execute_xml.to_string()
            
        finally:
            DbContainer.close_all()

        return new_paths, file_code_list
 
    checkin_textures.exposed = True



    def checkin_flash_shot(my, ticket, project_code,shot_code, context, comment):
            
        snapshot_code = ''
        try:
            my.init(ticket)
            Project.set_project(project_code)
            from pyasm.flash import FlashShotSObjectPublishCmd
            shot = Shot.get_by_code(shot_code)
            
            checkin = FlashShotSObjectPublishCmd(shot, context, comment)
            Command.execute_cmd(checkin)
            snapshot_code = checkin.snapshot.get_code()
        finally:
            DbContainer.close_all()
        
        return snapshot_code 

    checkin_flash_shot.exposed = True

    def get_queue(my, ticket):
        execute_xml = "<execute/>"
        try:
            my.init(ticket)

            from pyasm.prod.queue import Queue
            job = Queue.get_next_job()
            if job:
                job.execute()

                # need to get the execute xml
                command = job.get_command()
                execute_xml = command.get_execute_xml()

        finally:
            DbContainer.close_all()

        return execute_xml

    get_queue.exposed = True






 
    def get_upload_dir(my, ticket):
        '''simple function that returns a temporary path that files can be
        copied to'''
        tmp_dir = Environment.get_tmp_dir()
        upload_dir = "%s/upload/%s" % (tmp_dir, ticket)
        # TODO: upload_dir is not 
        System().makedirs(upload_dir)
        return upload_dir
    get_upload_dir.exposed = True




    def checkin_frames(my, ticket, project_code, queue_id):
        try:
            my.init(ticket)
            Project.set_project(project_code)

            cmd = CheckinFramesXMLRPC()
            cmd.set_args(ticket, queue_id)
            Command.execute_cmd(cmd)

        finally:
            DbContainer.close_all()

        return True
    checkin_frames.exposed = True




       
class CreateSetAssetsCmd(Command):
    '''This command checkins everything included in a set as a new asset'''
    def __init__(my):
        my.asset_codes = []


    def set_set_code(my, set_code):
        my.set_code = set_code

    def set_names(my, names):
        my.names = names
        my.description = "Created assets '%s'" % names


    def get_asset_codes(my):
        return my.asset_codes


    def execute(my):

        set = Asset.get_by_code(my.set_code)
        asset_library = set.get_value("name")

        # create the assets and check each in
        for name in my.names:
            description = name
            asset = Asset.create_with_autocode(name, asset_library, name)
            asset_code = asset.get_code()
            my.asset_codes.append(asset_code)

            # move the file created to a new name with the proper asset_code
            tmp_dir = Environment.get_tmp_dir()
            dir = "%s/upload" % tmp_dir
            shutil.move("%s/%s.ma" % (dir,name), "%s/%s.ma" % (dir,asset_code) )

            checkin = MayaAssetCheckin(asset_code)
            checkin.set_description("Initial checkin")
            checkin.set_context("proxy")
            checkin.execute()



class CheckinFramesXMLRPC(Command):

    def get_title(my):
        return "Checkin Frames"


    def set_args(my, ticket, queue_id):

        my.ticket = ticket


        # get the necessary data
        queue = Queue.get_by_id(queue_id)
        #data = queue.get_xml_value("data")
        data = queue.get_xml_value("serialized")
        search_key = data.get_value("data/search_key")

        my.sobject = Search.get_by_search_key(search_key)
        if not my.sobject:
            raise Exception("SObject with search_key: %s does not exist" % search_key)

        snapshot_code = data.get_value("data/snapshot_code")
        my.snapshot = Snapshot.get_by_code(snapshot_code)

        my.file_range = data.get_value("data/file_range")
        my.session = "<session/>"

        my.pattern = data.get_value("data/pattern")




    def execute(my):
        assert my.snapshot

        # assumes the files are already copied to the upload directory by
        # some other means (copying, for example)
        tmp_dir = Environment.get_tmp_dir()
        upload_dir = "%s/upload/%s" % (tmp_dir, my.ticket)

        file_name = my.pattern

        file_paths = ["%s/%s" % (upload_dir, file_name)]
        file_types = ["main"]

        # need to get session information
        if not my.session:
            my.session = "<session/>"

        # just add the next version
        version = -1

        render = Render.create(my.sobject, my.snapshot, my.session, my.file_range, version)
        file_range = FrameRange.get(my.file_range)
        checkin = FileGroupCheckin(render, file_paths, file_types, file_range)
        checkin.add_input_snapshot(my.snapshot)
        checkin.execute()

        my.description = "Checked in frames %s" % file_range.get_key()




