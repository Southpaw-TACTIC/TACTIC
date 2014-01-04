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


__all__ = ['FileCheckin', 'FileAppendCheckin', 'FileGroupCheckin', 'FileGroupAppendCheckin']

import sys, string, os, shutil, time, types
from cStringIO import StringIO

from pyasm.common import *
from pyasm.biz import *
from pyasm.search import *

from checkin import *
from snapshot_builder import *



class FileCheckin(BaseCheckin):
    '''Checks in a bunch of files to the repository.  The repo that these
    files gets checked into depends on the sobject and context
    '''

    def __init__(my, sobject, file_paths, file_types=['main'], \
            context="publish", snapshot_type="file", column="snapshot", \
            description="", is_current=True, source_paths=[],
            level_type=None, level_id=None, mode=None, keep_file_name=False,
            base_dir=None, is_revision=False, md5s=[], file_sizes=[],
            dir_naming=None, file_naming=None, context_index_padding=None,
            checkin_type='strict', version=None):
        '''sobject - the sobject that this checkin belongs to
           file_paths - array of all the files to checkin
           file_types - corresponding array of all the types for each file
           context - the context this checkin is published with
           snapshot_type - the type of snapshot
           column - the column where this data is to be stored
           is_current - determines whether to set this checkin as the current
           source_paths - the source paths of the file
           level_type - all checkins can be made into a level of some other
               sobject.  This defines the search_type of the level
           level_id - this is complimentary to level type to specify the
               parent level of this checkin
           mode - determines what mode the checkin is.  This basically
                determines how the source files are treated.  Accepted
                values are: copy, move, inplace
           keep_file_name - determines whether the checked in file name is
                kept as is or goes through naming conventions
           base_dir - DEPRECATED: this base directory determines the root that was used for inplace checkins
           is_revision - flag to set this checkin to a revision
           md5s - md5 list of the file_paths to cut down md5 generation time (optional)
           file_sizes - list of the file sizes. Used as a quick check to verify file
           dir_naming - explicitly set the dir_naming expression to use
           file_naming - explicitly set the file_naming expression to use

           checkin_type - auto or strict: specifies how defaults are handled
                strict uses strict naming conventions with explicit versionless
                auto uses looser naming conventions with auto versionless
            version - force the version of the check-in
            
        '''
        super(FileCheckin,my).__init__(sobject)

        my.snapshot_type = snapshot_type

        my.is_current = is_current
        my.is_revision = is_revision
        my.version = version

        if type(file_paths) in types.StringTypes:
            my.file_paths = [file_paths]
        else:
            my.file_paths = file_paths

        if source_paths: 
            if type(source_paths) != types.StringType:
                my.source_paths = source_paths
            else:
                my.source_paths = [source_paths]
        else:
            my.source_paths = my.file_paths[:]



        my.sobject = sobject
        my.base_dir_alias = None

        # rather than complicate the internals with the individual logic
        # for scms, we will, on first implementation, treat an scm check-in
        # as an inplace checkin and have a separate repo_type variable
        if mode in ['perforce']:
            mode = 'inplace'
            my.repo_type = 'perforce'

        # if a base_dir is passed, then store this
        if my.repo_type == 'perforce':
            depot = sobject.get_project_code()
            base_dir = "//%s" % depot
        elif mode == "inplace" and not base_dir:
            # get base_dir_alias
            alias_dict = Config.get_value("checkin", "base_dir_alias")
            if alias_dict:
                alias_dict = eval(alias_dict)
                for key, value in alias_dict.items():
                    asset_base_dir = alias_dict[key]['asset_base_dir']
                    if my.file_paths[0].startswith(asset_base_dir):
                        base_dir = asset_base_dir
                        my.base_dir_alias = key
                        break
                else: # default to the main asset_base_dir
                    base_dir = Environment.get_asset_dir()
            else:
                base_dir = Environment.get_asset_dir()
        my.base_dir = base_dir
       

        if type(file_types) != types.StringType:
            my.file_types = file_types
        else:
            my.file_types = [file_types]
        assert len(my.file_types) == len(my.file_paths)

        my.column = column
        if context == "" or context == None:
            my.context = Snapshot.get_default_context()
        else:
            my.context = context

        if my.context.find("/") == -1:
            parts = [my.context]
        else:
            parts = my.context.split("/")
        my.process = parts[0]
        my.checkin_type = checkin_type
        my.dir_naming = dir_naming
        my.file_naming = file_naming

        # this must be after the above declaration
        my.process_checkin_type(sobject, my.process, my.context, my.file_paths[0])

        # use an index for the subcontext
        if context_index_padding:
            search = Search("sthpw/snapshot")
            search.add_sobject_filter(my.sobject)
            search.add_filter("context", "%s/%%" % my.context, op='like')
            search.add_order_by("context desc")
            last_snapshot = search.get_sobject()
            if not last_snapshot:
                last_index = 1
            else:
                last_context = last_snapshot.get_value("context")
                if last_context.find("/") != -1:
                    try:
                        parts = last_context.split("/")
                        last_index = parts[1].lstrip("0")
                        if last_index == '':
                            last_index = 1
                        else:
                            last_index = int( last_index )
                            last_index += 1
                    except:
                        last_index = 1

                else:
                    last_index = 1

            expr = "%%s/%%0.%sd" % context_index_padding
            my.context = expr % (my.context, last_index)

        

        my.level_type = level_type
        my.level_id = level_id

        my.description = description
        my.file_dict = {}
        # add some command info
        my.info['context'] = my.context
        my.info['revision'] = str(my.is_revision)

        my.mode = mode
        my.keep_file_name = keep_file_name
        
        if md5s:
            assert len(md5s) == len(file_paths)
        else:
            # Checkin may not provide md5s, make a None list
            md5s = [ None for x in xrange(len(file_paths))]
        my.md5s = md5s
        
        if file_sizes:
            assert len(file_sizes) == len(file_sizes)
        else:
            # Checkin may not provide md5s, make a None list
            file_sizes = [ None for x in xrange(len(file_paths))]
        my.file_sizes = file_sizes





       


    def process_checkin_type(my, sobject, process, context, filepath):
        '''determine the checkin_type if it is specified to be empty'''

        if not my.checkin_type:

            # if checkin_type is not provided, then create a virtual
            # snapshot to get the naming to getermine the checkin_type
            file_type = 'main'
            virtual_snapshot = Snapshot.create_new()
            virtual_snapshot_xml = '<snapshot><file type=\'%s\'/></snapshot>' %(file_type)
            virtual_snapshot.set_value("snapshot", virtual_snapshot_xml)
            virtual_snapshot.set_value("snapshot_type", my.snapshot_type)

            virtual_snapshot.set_value("process", process)
            # since it is a a file name based context coming in, use process
            virtual_snapshot.set_value("context", process)
            virtual_snapshot.set_sobject(sobject)
            
            naming = Naming.get(sobject, virtual_snapshot, file_path=filepath)
            if naming:
                my.file_naming = None
                my.dir_naming = None

                # let the naming determine which check-in type is used
                my.checkin_type = naming.get_value("checkin_type", no_exception=True)
                if not my.checkin_type:
                    my.checkin_type = 'strict'

                # NOTE: not sure why this is here
                #my.context = process

            else:
                my.checkin_type = 'auto'
           
        # If it comes in as auto or empty, this will be set as default. 
        # it will be determined in postprocess_snapshot() whether to clear it
        if my.checkin_type =='auto':
            if not my.file_naming:

                server = Config.get_value("install", "server")
                if server:
                    # TODO: maybe need to add config to the naming expression
                    # language
                    my.file_naming = "{basefile}_{snapshot.process}_%s_v{version}.{ext}" % server
                else:
                    my.file_naming = "{basefile}_{snapshot.process}_v{version}.{ext}"


            if not my.dir_naming:
                has_code = my.sobject.get_value("code", no_exception=True)

                # break apart the context
                parts = context.split("/")
                if len(parts) > 2:
                    subdir = "/".join( parts[1:-1] )
                else:
                    subdir = ""


                # build dir_naming
                parts = []
                parts.append("{project.code}")
                parts.append("{search_type.table_name}")
                if has_code:
                    parts.append("{code}")
                else:
                    parts.append("{id}")
                parts.append("{snapshot.process}")
                parts.append(".versions")

                if subdir:
                    parts.append(subdir)

                my.dir_naming = {
                    'default': "/".join(parts)
                }


    def get_checkin_type(my):
        return my.checkin_type

    
    def set_context(my, context):
        my.context = context


    def get_upload_dir(cls):
        from pyasm.web import WebContainer
        ticket = WebContainer.get_security().get_ticket().get_key()
        dir = "%s/upload/%s" % (Environment.get_tmp_dir(), ticket)
        return dir
    get_upload_dir = classmethod(get_upload_dir)


    

    def create_files(my):
        # no files to create
        return my.file_paths



    def create_snapshot_xml(my, file_objects, snapshot_xml=None):
        '''
        file_objects - list of file objects
        snapshot_xml - an existing snapshot to append
        '''

        builder = SnapshotBuilder(snapshot_xml)
        root = builder.get_root_node()
        Xml.set_attribute(root, "timestamp", time.asctime() )
        Xml.set_attribute(root, "context", my.context )

        search_key = SearchKey.build_by_sobject(my.sobject)
        Xml.set_attribute(root, "search_key", search_key)

        login = Environment.get_user_name()
        Xml.set_attribute(root, "login", login)

        Xml.set_attribute(root, "checkin_type", my.checkin_type)


        for i, file_object in enumerate(file_objects):

            file_type = my.file_types[i]
            file_path = my.file_paths[i]

            file_info = {}
            file_info['type'] = file_type
            #file_info['source_path'] = file_path
            if my.mode == 'inplace':
                file_info['use_naming'] = 'false'

            builder.add_file(file_object, file_info)

        return builder.to_string()



    def get_snapshot_type(my):
        return my.snapshot_type



    def create_snapshot(my, snapshot_xml):
        '''add the snapshot to the sobject'''

        snapshot_type = my.get_snapshot_type()

        if my.mode == 'local':
            is_latest = False
            is_synced = False
        else:
            is_latest = True
            is_synced = True


        my.is_latest = is_latest

        # copy the snapshot and put it in the snapshot history
        my.snapshot = Snapshot.create( my.sobject, snapshot_type,
            my.context, my.column, my.description, snapshot_xml,
            is_current=my.is_current, is_revision=my.is_revision,
            level_type=my.level_type, level_id=my.level_id, is_latest=is_latest,
            is_synced=is_synced, version=my.version, triggers="integral", set_booleans=False)


    def postprocess_snapshot(my):

        # do a post process on the snapshot xml.  This is because some
        # information is not known until after the snapshot is committed
        snapshot_xml = my.snapshot.get_xml_value("snapshot")

        version = my.snapshot.get_value("version")
        builder = SnapshotBuilder(snapshot_xml)
        root = builder.get_root_node()
        Xml.set_attribute(root, "version", version)
    
     

        # find the path for each file
        for i, file_object in enumerate(my.file_objects):

            to_name = file_object.get_full_file_name()
            file_type = my.snapshot.get_type_by_file_name(to_name)
            file_node = snapshot_xml.get_node("snapshot/file[@name='%s']" % to_name)
            assert file_node != None

            if i < len(my.source_paths):
                source_path = my.source_paths[i]
                file_object.set_value("source_path", source_path)

            if my.mode == "inplace":
                # if this is an inplace checkin, then the original path is the
                # checked in path
                file_path = my.file_paths[i]
                file_dir = os.path.dirname(file_path)
                file_object.set_value("checkin_dir", file_dir)

                # set the relative dir.  Replace the base dir passed in
                if my.repo_type == 'perforce':
                    relative_dir = os.path.dirname(source_path)
                    relative_dir = relative_dir.replace(my.base_dir, "")

                elif my.base_dir and file_dir.startswith(my.base_dir):
                    relative_dir = file_dir.replace(my.base_dir, "")
                    # strip any leading /
                else:
                      
                    # otherwise relative_dir is empty??
                    relative_dir = ''

                relative_dir = relative_dir.strip("/")
                file_object.set_value("relative_dir", relative_dir)
                if my.base_dir_alias:
                    file_object.set_value("base_dir_alias", my.base_dir_alias)

            else:
                # TODO: maybe we need to support multiple base dirs
                # This will allow another directory to be incorporated
                # into TACTIC ... the only requirement is that base dir
                # is registered in TACTIC

                # all other modes use the lib dir
                lib_dir = my.snapshot.get_lib_dir(file_type=file_type, file_object=file_object, create=True, dir_naming=my.dir_naming)
                file_object.set_value("checkin_dir", lib_dir)

                # set the relative dir
                relative_dir = my.snapshot.get_relative_dir(file_type=file_type, file_object=file_object, create=True, dir_naming=my.dir_naming)
                relative_dir = relative_dir.strip("/")
                file_object.set_value("relative_dir", relative_dir)

                relative_dir = file_object.get_value("relative_dir")
                assert(relative_dir)


            # make sure checkin_dir and relative_dir are filled out
            checkin_dir = file_object.get_value("checkin_dir")
            assert(checkin_dir)

            file_object.commit()

        return my.snapshot

    def preprocess_files(my, files):
        # change the user and group owner of the file to apache or what TACTIC
        # is run as. Only applicable for Linux os
        if Config.get_value("checkin", "sudo_no_password") == 'true': 
            if os.name != 'nt':
                uid = os.getuid()
                gid = os.getgid()
                try:
                    # assuming the OS has sudo installed, otherwise it will not work
                    for file in files:
                        #os.chown(file, uid, gid)
                        os.system('sudo chown %s.%s \"%s\"'%(uid, gid, file))
                except OSError, e:
                    # apache should be made a sudoer for this to work
                    print "Error changing owner. %s" %e.__str__()

    def handle_system_commands(my, files, file_objects):
        '''delegate the system commands to the appropriate repo.'''

        if my.mode == 'inplace':
            # TODO: ? MD5?
            return


        # get the repo set it up
        repo = my.sobject.get_repo(my.snapshot)
        repo.handle_system_commands(my.snapshot, files, file_objects, my.mode, my.md5s, my.source_paths)
       
        # Call the checkin/move pipeline event
        #event_caller = PipelineEventCaller(my, "checkin/move")
        #event_caller.run()
        trigger = PipelineEventTrigger()
        Trigger.append_trigger(my, trigger, "checkin/move")




    
    def get(cls, sobject, file_paths, file_types, \
            context="publish", snapshot_type="file", column="snapshot", \
            description=""):

        handler_cls = FileCheckin

        # allow the pipeline of an sobject determine the handler for checkin in
        if sobject.has_value("pipeline_code"):
            # figure out which checkin to use based on 

            pipeline_code = sobject.get_value("pipeline_code")
            pipeline = Pipeline.get_by_code(pipeline_code)
            if pipeline:
                # NOTE: assumption of process == context
                process = pipeline.get_process(context)
                if process:
                    handler_cls_name = process.get_action_handler("checkin", scope="current")
                    if handler_cls_name:
                        exec( Common.get_import_from_class_path(handler_cls_name) )
                        handler_cls = eval(handler_cls_name)


        handler = handler_cls(sobject, file_paths, file_types, context=context, snapshot_type=snapshot_type, column=column, description=description)

        return handler

    get = classmethod(get)


    def get_preallocated_path(cls, snapshot, file_type='main', file_name='', file_range='', mkdir=True, protocol=None, ext='', parent=None):
        '''Get a preallocated directory for this snapshot.  This will run a
        virtual checkin through the naming convention and construct a path
        that Tactic expects the checked in file to go to

        @params
        snapshot - the snapshot that the files will be added to
        file_type - the type of file that will be added.  The need for this
            will depend on the particular implementation of the naming
            conventions
        file_name - the desired name of the file - most naming conventions
            will ignore this, but some will that the file name as a base
        file_range - if the file name is a range, then specify the range
        mkdir - an option which determines whether the directory of the
            preallocation should be created
        protocol - the protocol of the path returned

        @return
        returns a preallocated path
        '''

        # we need a dummy file_code and range
        #file_code = '123UNI'
        #if not file_range:
        #    file_range = "1-30"

        if not parent:
            parent = snapshot.get_parent()
        assert parent
        if not file_name:
            file_name = parent.get_code()
            if not file_name:
                file_name = parent.get_name()
            if not file_name:
                file_name = "unknown"

        file_object = SearchType.create("sthpw/file")
        file_object.set_value("file_name", file_name)
        file_object.set_value("type", file_type)
        #file_object.set_value("code", file_code)
        #file_object.set_value("range", file_range)
        
        # build the file name
        file_naming = Project.get_file_naming()
        file_naming.set_sobject(parent)
        file_naming.set_snapshot(snapshot)
        file_naming.set_file_object(file_object)
        file_naming.set_ext(ext)
        file_name = file_naming.get_file_name()
        
        # update the file_name of the file_object from file_naming
        file_object.set_value("file_name", file_name)
        
        lib_dir = snapshot.get_lib_dir(file_type=file_type, create=True, file_object=file_object)
        if mkdir and not os.path.exists(lib_dir):
            System().makedirs(lib_dir)

        # get the client lib dir
        if protocol == "client_repo":
            client_lib_dir = snapshot.get_client_lib_dir(file_type=file_type, create=True, file_object=file_object)
        elif protocol =='sandbox':
            client_lib_dir = snapshot.get_sandbox_dir(file_type=file_type)
        else:
            client_lib_dir = snapshot.get_lib_dir(file_type=file_type, create=True, file_object=file_object)

        # put some protection in for ending slash
        client_lib_dir = client_lib_dir.rstrip("/")
        path = "%s/%s" % (client_lib_dir, file_name)
        return path

    get_preallocated_path = classmethod(get_preallocated_path)


from pyasm.command import Trigger
class PipelineEventTrigger(Trigger):
    def execute(my):
        caller = my.get_caller()
        event_caller = PipelineEventCaller(caller, "checkin/move")
        event_caller.run()



import threading
class PipelineEventCaller(threading.Thread):

    def __init__(my, command, event_name):
        my.command = command
        my.event_name = event_name
        super(PipelineEventCaller,my).__init__()


    def run(my):
        try:
            my.command.set_event_name(my.event_name)
            my.command.set_process(my.command.context)
            pipeline = Pipeline.get_by_sobject(my.command.sobject)
            if pipeline:
                my.command.set_pipeline_code(pipeline.get_code() )
                my.command.notify_listeners()
        except Exception, e:
            # print the stacktrace
            import traceback
            tb = sys.exc_info()[2]
            stacktrace = traceback.format_tb(tb)
            stacktrace_str = "".join(stacktrace)
            print "-"*50
            print stacktrace_str
            print str(e)
            print "-"*50
            #raise TacticException(e)




    
        



class FileAppendCheckin(FileCheckin):
    '''Appends a bunch of files to an already existing snapshot'''
    def __init__(my, snapshot_code, file_paths, file_types,  mode=None, keep_file_name=True,source_paths=[], dir_naming=None, file_naming=None, checkin_type='strict'):
        '''
        snapshot_code - the already existing snapshot to append to
        file_paths - array of all the files to checkin
        file_types - corresponding array of all the types for each file
 
        dir_naming - explicitly set the dir_naming expression to use
        file_naming - explicitly set the file_naming expression to use
        '''
        my.append_snapshot = Snapshot.get_by_code(snapshot_code)
        if not my.append_snapshot:
            raise CheckinException('Snapshot code [%s] is unknown') 
        sobject = my.append_snapshot.get_sobject()
        context = my.append_snapshot.get_value("context")
        snapshot_type = my.append_snapshot.get_value("snapshot_type")
        column = my.append_snapshot.get_value("column_name")
        
        super(FileAppendCheckin,my).__init__(sobject, file_paths, file_types, context, snapshot_type, column, mode=mode, keep_file_name=keep_file_name, source_paths=source_paths, dir_naming=dir_naming, file_naming=file_naming, checkin_type=checkin_type)

        my.is_latest = my.append_snapshot.get_value('is_latest')
        my.is_current = my.append_snapshot.get_value('is_current')

        
    def create_snapshot_xml(my, file_objects):
        # take the current snapshot
        xml = my.append_snapshot.get_snapshot_xml()
        return super(FileAppendCheckin,my).create_snapshot_xml(file_objects,xml)


    def get_snapshot(my):
        return my.append_snapshot



    def create_snapshot(my, snapshot_xml):
        # copy the snapshot and put it in the snapshot history
        my.append_snapshot.set_value("snapshot", snapshot_xml)
        my.append_snapshot.commit()
        my.snapshot = my.append_snapshot

        return my.snapshot

    def get_trigger_prefix(my):
        return "add_file"





class FileGroupCheckin(FileCheckin):
    '''Handles a group of files (such as frames) and treats them as a
    single entry.  This is useful for checking in large groups of related
    and similar files that are too cumbersome to treat as individual files'''

    def __init__(my, sobject, file_paths, file_types, file_range, \
            context="publish", snapshot_type="file", column="snapshot", \
            description="", keep_file_name=False, is_revision=False, mode=None):

        super(FileGroupCheckin,my).__init__(sobject, file_paths, file_types, \
            context=context, snapshot_type=snapshot_type, column=column,\
            description=description, keep_file_name=keep_file_name, \
            is_revision=is_revision, mode=mode )
       
        my.file_range = file_range
        my.expanded_paths = []
        my.input_snapshots = []


    def add_input_snapshot(my, snapshot):
        my.input_snapshots.append(snapshot)


    def check_files(my, file_paths):
        # do nothing here for now
        pass

    def get_expanded_paths(my):
        return my.expanded_paths

    def create_file_objects(my, files):

        file_objects = []

        for idx, file_path in enumerate(files):
            file_type = my.file_types[idx]

            # determine if this is a group or not
            if File.is_file_group(file_path):
                file_object = FileGroup.create(file_path, my.file_range, \
                    my.sobject.get_search_type(), my.sobject.get_id(), file_type=file_type )
            else:
                # create file_object
                file_object = File.create(file_path, \
                    my.sobject.get_search_type(), my.sobject.get_id(), file_type=file_type, st_size=my.file_sizes[i] )
                    

            if file_object == None:
                raise FileException("File object id=[%s] is None" % file_code)

            file_objects.append(file_object)

        return file_objects




    def create_snapshot_xml(my, file_objects, snapshot_xml=None):

        builder = SnapshotBuilder(snapshot_xml)
        root = builder.get_root_node()
        from pyasm.search.sql import DbContainer
        from pyasm.biz import Project
        project = Project.get()
        db_resource = project.get_project_db_resource()
        sql = DbContainer.get(db_resource)

        if sql.get_database_type() == 'SQLServer':
            import datetime
            Xml.set_attribute(root, "timestamp", datetime.datetime.now())
        else:
            Xml.set_attribute(root, "timestamp", time.asctime() )
        Xml.set_attribute(root, "context", my.context )

        for i in range(0, len(file_objects)):

            file_object = file_objects[i]
            file_type = my.file_types[i]

            file_info = {}
            file_info['type'] = file_type
            if file_object.get_file_range():
                file_info['file_range'] = my.file_range.get_key()

            builder.add_file(file_object, file_info)

        for input_snapshot in my.input_snapshots:
            builder.add_ref_by_snapshot(input_snapshot)


        return builder.to_string()


    def move_file(my, file_path, new_file_path):
        if file_path.find('#') == -1 and file_path.find('%') == -1:
            shutil.move(file_path, new_file_path)
            return
        if new_file_path.find('#') == -1 and new_file_path.find('%') == -1:
            new_file_path = "%s.####" % new_file_path
            #raise CheckinException('The naming convention should be returning\
            #a path name with #### or %%0.4d notation in it. [%s] found instead.' % new_file_path)
        file_paths = FileGroup.expand_paths(file_path, my.file_range)
        new_file_paths = FileGroup.expand_paths(new_file_path, my.file_range)

        for i in range(0, len(file_paths)):
            file_path = file_paths[i]
            to_file_path = new_file_paths[i]
            shutil.move(file_path, to_file_path)

        return new_file_path


    def handle_system_commands(my, files, file_objects):
        '''move the tmp files in the appropriate directory'''
        if my.mode == 'inplace':
            # TODO: ? MD5?
            return

        for i in range( 0, len(files) ):

            file_object = file_objects[i]
            # build the to paths
            to_name = file_object.get_full_file_name()
            file_type = my.snapshot.get_type_by_file_name(to_name)

            file_object.set_value('type', file_type)

            lib_dir = my.snapshot.get_lib_dir(file_type=file_type, file_object=file_object)
            if not os.path.exists(lib_dir):
                System().makedirs(lib_dir)
            to_path = "%s/%s" % (lib_dir, to_name )

            if file_object.get_file_range():
                from_expanded = FileGroup.expand_paths(files[i], my.file_range)
                to_expanded = FileGroup.expand_paths(to_path, my.file_range)
            else:
                from_expanded = [files[i]]
                to_expanded = [to_path]

                
            my.expanded_paths.extend(from_expanded)

            # iterate through each and copy to the lib
            for j in range(0, len(from_expanded) ):

                # check before copying
                if os.path.exists(to_expanded[j]) and my.mode not in ['inplace','preallocate']:
                    raise CheckinException('This path [%s] already exists'%to_expanded[j])
                '''
                if my.mode =='free_copy':
                    FlieUndo.copy(from_expanded[j], to_expanded[j])
                elif my.mode == 'free_move':
                    FlieUndo.move(from_expanded[j], to_expanded[j])
                else:
                ''' 


                # calculate the md5 signature of this file if it is a single
                if len(from_expanded) == 1:
                    md5_checksum = File.get_md5(to_path)
                    if md5_checksum:
                        file_object.set_value("md5", md5_checksum)
                        file_object.commit()
                    st_size = file_object.get_value("st_size")
                    FileUndo.create( from_expanded[j], to_expanded[j], { "md5": md5_checksum, "st_size": st_size } )

                else:
                    FileUndo.create( from_expanded[j], to_expanded[j] )

                # check to see that the file exists.
                if not os.path.exists( to_expanded[j] ):
                    raise CheckinException("Failed copy [%s] to [%s]" % \
                    ( from_expanded[j], to_expanded[j] ) )




class FileGroupAppendCheckin(FileGroupCheckin):
    '''Appends a group of files to an already existing snapshot.
        Note: this is functionally the same as FileAppendCheckin but it 
        is derived from FileGroupCheckin
    '''
    def __init__(my, snapshot_code, file_paths, file_types, file_range, keep_file_name=False, mode=None):
        '''
        @params
        snapshot_code - the already existing snapshot to append to
        file_paths - array of all the files to checkin
        file_types - corresponding array of all the types for each file
        file_range - the file range of the paths
        mode - move, copy, preallocate, inplace
        '''
        my.append_snapshot = Snapshot.get_by_code(snapshot_code)
        sobject = my.append_snapshot.get_sobject()
        context = my.append_snapshot.get_value("context")
        snapshot_type = my.append_snapshot.get_value("snapshot_type")
        column = my.append_snapshot.get_value("column_name")

        super(FileGroupAppendCheckin,my).__init__(sobject, file_paths, file_types, file_range, context=context, snapshot_type=snapshot_type, column=column, keep_file_name=keep_file_name, mode=mode )


    def create_snapshot_xml(my, file_objects):
        # take the current snapshot
        xml = my.append_snapshot.get_snapshot_xml()
        return super(FileGroupAppendCheckin,my).create_snapshot_xml(file_objects,xml)



    def create_snapshot(my, snapshot_xml):

        # copy the snapshot and put it in the snapshot history
        my.append_snapshot.set_value("snapshot", snapshot_xml)
        my.append_snapshot.commit()
        my.snapshot = my.append_snapshot

        return my.snapshot

    def get_trigger_prefix(my):
        return "add_group"

