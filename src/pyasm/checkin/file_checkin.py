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


__all__ = ['FileCheckin', 'FileAppendCheckin', 'FileGroupCheckin', 'FileGroupAppendCheckin','SingleSnapshotException']

import sys, string, os, shutil, time, types

from pyasm.common import *
from pyasm.biz import *
from pyasm.search import *

from .checkin import *
from .snapshot_builder import *

import six
basestring = six.string_types


class SingleSnapshotException(Exception):
    pass


class FileCheckin(BaseCheckin):
    '''Checks in a bunch of files to the repository.  The repo that these
    files gets checked into depends on the sobject and context
    '''

    def __init__(self, sobject, file_paths, file_types=['main'], \
            context="publish", snapshot_type="file", column="snapshot", \
            description="", is_current=True, source_paths=[],
            level_type=None, level_id=None, mode=None, keep_file_name=False,
            base_dir=None, is_revision=False, md5s=[], file_sizes=[],
            dir_naming=None, file_naming=None, context_index_padding=None,
            checkin_type='', version=None, single_snapshot=False, process=None
            ):

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
                determines how the source files are treated.  
                Accepted values: create, copy, move, local: 
                        create: default tactic check-in that uses upload/handoff dir; naming convention on, return to cache on undo
                        move and local performs a move. copy performs a copy
                        
                        inplace: check in the source_path as is without moving it; naming convention off
                        move: check in the source_path to the tactic repo via a move without going thru upload/handoff dir; naming convention on, return to src on undo
                        copy: check in the source_path to the tactic repo via a copy without going thru upload/handoff dir; naming convention on, return to cache on undo
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
                auto uses a looser naming conventions with the auto versionless
           version - force the version of the check-in
           single_snapshot - if set to True, it raises a SingleSnapshotException if an existing snapshot already exists.
            
        '''
        super(FileCheckin,self).__init__(sobject)
        self.snapshot_type = snapshot_type

        self.is_current = is_current
        self.is_revision = is_revision
        self.version = version

        if isinstance(file_paths, basestring):
            self.file_paths = [file_paths]
        else:
            self.file_paths = file_paths

        for i, file_path in enumerate(self.file_paths):
            if not os.path.isdir(file_path):
                self.file_paths[i] = file_path.rstrip("/")
            

        if source_paths: 
            if not isinstance(source_paths, basestring):
                self.source_paths = source_paths
            else:
                self.source_paths = [source_paths]
        else:
            self.source_paths = self.file_paths[:]
        for i, source_path in enumerate(self.source_paths):
            if not os.path.isdir(source_path):
                self.source_paths[i] = source_path.rstrip("/")


        self.sobject = sobject
        self.base_dir_alias = None

        # rather than complicate the internals with the individual logic
        # for scms, we will, on first implementation, treat an scm check-in
        # as an inplace checkin and have a separate repo_type variable
        if mode in ['perforce']:
            mode = 'inplace'
            self.repo_type = 'perforce'

        # if a base_dir is passed, then store this
        if self.repo_type == 'perforce':
            depot = sobject.get_project_code()
            base_dir = "//%s" % depot
        elif mode == "inplace" and not base_dir:
            # get base_dir_alias
            #alias_dict = Config.get_value("checkin", "base_dir_alias")
            alias_dict = Environment.get_asset_dirs()
            if alias_dict:
                for key, value in alias_dict.items():
                    asset_base_dir = alias_dict[key]
                    if self.file_paths[0].startswith(asset_base_dir):
                        base_dir = asset_base_dir
                        self.base_dir_alias = key
                        break
                else: # default to the main asset_base_dir
                    base_dir = Environment.get_asset_dir()
            else:
                base_dir = Environment.get_asset_dir()
        self.base_dir = base_dir
       

        if not isinstance(file_types, basestring):
            self.file_types = file_types
        else:
            self.file_types = [file_types]
        assert len(self.file_types) == len(self.file_paths)

        self.column = column
        if context == "" or context == None:
            self.context = Snapshot.get_default_context()
        else:
            self.context = context

        if self.context.find("/") == -1:
            parts = [self.context]
        else:
            parts = self.context.split("/")

        if not process:
            self.process = parts[0]
        else:
            self.process = process

        self.checkin_type = checkin_type

        if self.checkin_type and self.checkin_type not in ['strict','auto']:
            raise CheckinException("checkin_type can only be '', strict, or auto")

        self.dir_naming = dir_naming
        self.file_naming = file_naming

        # this must be after the above declaration, set the returned data
        return_data =  self.process_checkin_type(self.checkin_type, sobject, self.process, self.context,\
                self.file_paths[0], self.snapshot_type, is_revision=self.is_revision)
        if return_data.get('dir_naming'):
            self.dir_naming = return_data.get('dir_naming')
        
        if return_data.get('file_naming'):
            self.file_naming = return_data.get('file_naming')

        self.naming = return_data.get('naming')
        self.checkin_type = return_data.get('checkin_type')

        # use an index for the subcontext
        if context_index_padding:
            search = Search("sthpw/snapshot")
            search.add_sobject_filter(self.sobject)
            search.add_filter("context", "%s/%%" % self.context, op='like')
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
            self.context = expr % (self.context, last_index)

        

        self.level_type = level_type
        self.level_id = level_id

        self.description = description
        self.file_dict = {}
        # add some command info
        self.info['context'] = self.context
        self.info['revision'] = str(self.is_revision)

        self.mode = mode
        self.keep_file_name = keep_file_name
        
        if md5s:
            assert len(md5s) == len(file_paths)
        else:
            # Checkin may not provide md5s, make a None list
            md5s = [ None for x in range(len(file_paths))]
        self.md5s = md5s
        
        if file_sizes:
            assert len(file_sizes) == len(file_sizes)
        else:
            # Checkin may not provide md5s, make a None list
            file_sizes = [ None for x in range(len(file_paths))]
        self.file_sizes = file_sizes
        
        self.single_snapshot = single_snapshot




       


    def process_checkin_type(cls, checkin_type, sobject, process, context, filepath, snapshot_type,
            file_naming_expr=None, dir_naming_expr=None, is_revision=False):
        '''determine the checkin_type if it is specified to be empty'''

        dir_naming = None
        file_naming = None
        naming = None 
        return_data = {}
        if not checkin_type or checkin_type == 'auto':

            # if checkin_type is not provided, then create a virtual
            # snapshot to get the naming to getermine the checkin_type
            file_type = 'main'
            virtual_snapshot = Snapshot.create_new()
            virtual_snapshot_xml = '<snapshot><file type=\'%s\'/></snapshot>' %(file_type)
            virtual_snapshot.set_value("snapshot", virtual_snapshot_xml)
            virtual_snapshot.set_value("snapshot_type", snapshot_type)

            virtual_snapshot.set_value("process", process)
            # since it is a a file name based context coming in, use process
            virtual_snapshot.set_value("context", process)
            virtual_snapshot.set_sobject(sobject)

            naming = Naming.get(sobject, virtual_snapshot, file_path=filepath)
            if naming:
                
                # let the naming determine which check-in type is used
                name_checkin_type = naming.get_value("checkin_type", no_exception=True)
                if not checkin_type:
                    if name_checkin_type:
                        checkin_type = name_checkin_type
                    else:
                        checkin_type = 'strict'


            else:
                checkin_type = 'auto'
                if is_revision:
                    revision_part = '_r{revision}'
                else:
                    revision_part = ''
                # If it comes in as auto or empty, this will be set as default. 
                # it will be determined in postprocess_snapshot() whether to clear it
                if checkin_type =='auto':
                    if not file_naming_expr:

                        server = Config.get_value("install", "server")
                        if server:
                            # TODO: maybe need to add config to the naming expression
                            # language
                            file_naming = "{basefile}_{snapshot.process}_%s_v{version}%s.{ext}" % (server, revision_part)
                            
                        else:
                            file_naming = "{basefile}_{snapshot.process}_v{version}%s.{ext}" %revision_part

                    if not dir_naming_expr:
                        has_code = sobject.get_value("code", no_exception=True)

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

                        # icons don't have the need for this
                        if context != "icon":
                            parts.append("versions")

                        if subdir:
                            parts.append(subdir)

                        dir_naming = {
                            'default': "/".join(parts)
                        }

        return_data = {'naming': naming, 'file_naming': file_naming, 'dir_naming': dir_naming, 'checkin_type': checkin_type}
        return return_data

    process_checkin_type = classmethod(process_checkin_type)

    def get_checkin_type(self):
        return self.checkin_type

    
    def set_context(self, context):
        self.context = context


    def get_upload_dir(cls):
        from pyasm.web import WebContainer
        ticket = WebContainer.get_security().get_ticket().get_key()
        dir = "%s/upload/%s" % (Environment.get_tmp_dir(), ticket)
        return dir
    get_upload_dir = classmethod(get_upload_dir)


    

    def create_files(self):
        # no files to create
        return self.file_paths



    def create_snapshot_xml(self, file_objects, snapshot_xml=None):
        '''
        file_objects - list of file objects
        snapshot_xml - an existing snapshot to append
        '''

        builder = SnapshotBuilder(snapshot_xml)
        root = builder.get_root_node()
        Xml.set_attribute(root, "timestamp", time.asctime() )
        Xml.set_attribute(root, "context", self.context )

        search_key = SearchKey.build_by_sobject(self.sobject)
        Xml.set_attribute(root, "search_key", search_key)

        login = Environment.get_user_name()
        Xml.set_attribute(root, "login", login)

        Xml.set_attribute(root, "checkin_type", self.checkin_type)


        for i, file_object in enumerate(file_objects):

            file_type = self.file_types[i]
            file_path = self.file_paths[i]

            file_info = {}
            file_info['type'] = file_type
            #file_info['source_path'] = file_path
            if self.mode == 'inplace':
                file_info['use_naming'] = 'false'

            builder.add_file(file_object, file_info)

        return builder.to_string()



    def get_snapshot_type(self):
        return self.snapshot_type



    def create_snapshot(self, snapshot_xml):
        '''add the snapshot to the sobject'''

        snapshot_type = self.get_snapshot_type()

        if self.mode == 'local':
            is_latest = False
            is_synced = False
        else:
            is_latest = True
            is_synced = True


        self.is_latest = is_latest

        # copy the snapshot and put it in the snapshot history
        self.snapshot = Snapshot.create( self.sobject, snapshot_type,
            self.context, self.column, self.description, snapshot_xml,
            is_current=self.is_current, is_revision=self.is_revision,
            level_type=self.level_type, level_id=self.level_id, is_latest=is_latest,
            is_synced=is_synced, version=self.version, triggers="integral", set_booleans=False, process=self.process)

        if self.single_snapshot and self.snapshot.get_version() > 1:
            raise SingleSnapshotException("There is an existing snapshot for \
                    this sobject [%s] under the [%s] context."%(self.sobject.get_search_key(), self.context))
            

    def postprocess_snapshot(self):

        # do a post process on the snapshot xml.  This is because some
        # information is not known until after the snapshot is committed
        snapshot_xml = self.snapshot.get_xml_value("snapshot")

        version = self.snapshot.get_value("version")
        builder = SnapshotBuilder(snapshot_xml)
        root = builder.get_root_node()
        Xml.set_attribute(root, "version", version)


        naming = Naming.get(self.sobject, self.snapshot) 
        if naming and self.checkin_type:
            checkin_type = naming.get_value('checkin_type')
            if checkin_type and self.checkin_type != checkin_type:
                print("Mismatch checkin_type!")
                naming = None
            
        # find the path for each file
        for i, file_object in enumerate(self.file_objects):

            to_name = file_object.get_full_file_name()
            file_type = self.snapshot.get_type_by_file_name(to_name)

            file_node = snapshot_xml.get_node('snapshot/file[@name="%s"]' % to_name)
            assert file_node != None

            if i < len(self.source_paths):
                source_path = self.source_paths[i]
                file_object.set_value("source_path", source_path)

            if self.mode == "inplace":
                # if this is an inplace checkin, then the original path is the
                # checked in path
                file_path = self.file_paths[i]
                file_dir = os.path.dirname(file_path)
                file_object.set_value("checkin_dir", file_dir)

                # set the relative dir.  Replace the base dir passed in
                if self.repo_type == 'perforce':
                    relative_dir = os.path.dirname(source_path)
                    relative_dir = relative_dir.replace(self.base_dir, "")

                elif self.base_dir and file_dir.startswith(self.base_dir):
                    relative_dir = file_dir.replace(self.base_dir, "")
                    # strip any leading /
                else:
                      
                    # otherwise relative_dir is empty??
                    relative_dir = ''

                relative_dir = relative_dir.strip("/")
                file_object.set_value("relative_dir", relative_dir)
            else:
                if naming:
                    self.base_dir_alias = naming.get_value("base_dir_alias")
                    if self.base_dir_alias:
                        file_object.set_value("base_dir_alias", self.base_dir_alias)

                # all other modes use the lib dir
                lib_dir = self.snapshot.get_lib_dir(file_type=file_type, file_object=file_object, create=True, dir_naming=self.dir_naming)
                file_object.set_value("checkin_dir", lib_dir)

                # determine base_dir alias
                asset_dirs = Environment.get_asset_dirs()
                for name, asset_dir in asset_dirs.items():
                    # leave default blank (for now)
                    if name == 'default':
                        continue
                    if lib_dir.startswith("%s/" % asset_dir):
                        self.base_dir_alias = name
                        break


                # set the relative dir
                relative_dir = self.snapshot.get_relative_dir(file_type=file_type, file_object=file_object, create=True, dir_naming=self.dir_naming)
                relative_dir = relative_dir.strip("/")
                file_object.set_value("relative_dir", relative_dir)

                relative_dir = file_object.get_value("relative_dir")

            if self.base_dir_alias:
                file_object.set_value("base_dir_alias", self.base_dir_alias)

            # make sure checkin_dir and relative_dir are filled out
            checkin_dir = file_object.get_value("checkin_dir")
            assert(checkin_dir)

            file_object.commit()

        return self.snapshot

    def preprocess_files(self, files):
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
                except OSError as e:
                    # apache should be made a sudoer for this to work
                    print("Error changing owner. %s" %e.__str__())

    def handle_system_commands(self, files, file_objects):
        '''delegate the system commands to the appropriate repo.'''

        if self.mode == 'inplace':
            # TODO: ? MD5?
            return


        # get the repo set it up
        repo = self.sobject.get_repo(self.snapshot)
        repo.handle_system_commands(self.snapshot, files, file_objects, self.mode, self.md5s, self.source_paths)
       
        # Call the checkin/move pipeline event
        #event_caller = PipelineEventCaller(self, "checkin/move")
        #event_caller.run()
        trigger = PipelineEventTrigger()
        Trigger.append_trigger(self, trigger, "checkin/move")




    
    def get(cls, sobject, file_paths, file_types, \
            context="publish", snapshot_type="file", column="snapshot", \
            description="", mode=""):

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


        handler = handler_cls(sobject, file_paths, file_types, context=context, snapshot_type=snapshot_type, column=column, description=description, mode=mode)

        return handler

    get = classmethod(get)


    def get_preallocated_path(cls, snapshot, file_type='main', file_name='', file_range='', mkdir=True, protocol=None, ext='', parent=None, checkin_type=''):
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
        ext - extension
        parent - parent of snapshot
        checkin_type - strict, auto, or ''

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

        # if no file name is given, then we are just going to return a directory
        """
        if not file_name:
            file_name = parent.get_code()
            if not file_name:
                file_name = parent.get_name()
            if not file_name:
                file_name = "unknown"
        """

        # if there is no file name override, see if there is a file_object
        if file_type and not file_name:
            file_object = snapshot.get_file_by_type(file_type)
        else:
            file_object = None


        if file_object:
            naming_file_name = file_object.get_value("file_name")
        elif file_name:
            # if no file object exists the go through naming to find
            # the name
            file_object = SearchType.create("sthpw/file")
            file_object.set_value("file_name", file_name)
            file_object.set_value("type", file_type)
    
            # build the file name
            file_naming = Project.get_file_naming()
            file_naming.set_sobject(parent)
            file_naming.set_snapshot(snapshot)
            file_naming.set_file_object(file_object)
            file_naming.set_ext(ext)
            naming_file_name = file_naming.get_file_name()
        else:
            naming_file_name = None

        # if naming returns a file name, then use that one
        if naming_file_name:
            file_name = naming_file_name
        
            # update the file_name of the file_object from file_naming
            file_object.set_value("file_name", file_name)
      
        context = snapshot.get_context()
        process = snapshot.get_process()
        if not process:
            process = context

        # assume is_revision = False
        return_data = cls.process_checkin_type(checkin_type, parent, process,\
                context , file_name, snapshot.get_value('snapshot_type'))
        dir_naming = return_data.get('dir_naming')
        file_naming = return_data.get('file_naming')
        

        lib_dir = snapshot.get_lib_dir(file_type=file_type, create=True, file_object=file_object, dir_naming=dir_naming)
        if mkdir and not os.path.exists(lib_dir):
            System().makedirs(lib_dir)

        # get the client lib dir
        if protocol == "client_repo":
            client_lib_dir = snapshot.get_client_lib_dir(file_type=file_type, create=True, file_object=file_object, dir_naming=dir_naming)
        elif protocol =='sandbox':
            client_lib_dir = snapshot.get_sandbox_dir(file_type=file_type)
        else:
            client_lib_dir = snapshot.get_lib_dir(file_type=file_type, create=True, file_object=file_object, dir_naming=dir_naming)

        # put some protection in for ending slash
        client_lib_dir = client_lib_dir.rstrip("/")

        if file_name:
            path = "%s/%s" % (client_lib_dir, file_name)
        else:
            path = client_lib_dir
        return path

    get_preallocated_path = classmethod(get_preallocated_path)


from pyasm.command import Trigger
class PipelineEventTrigger(Trigger):
    def execute(self):
        caller = self.get_caller()
        event_caller = PipelineEventCaller(caller, "checkin/move")
        event_caller.run()



import threading
class PipelineEventCaller(threading.Thread):

    def __init__(self, command, event_name):
        self.command = command
        self.event_name = event_name
        super(PipelineEventCaller,self).__init__()


    def run(self):
        try:
            self.command.set_event_name(self.event_name)
            self.command.set_process(self.command.context)
            pipeline = Pipeline.get_by_sobject(self.command.sobject)
            if pipeline:
                self.command.set_pipeline_code(pipeline.get_code() )
                self.command.notify_listeners()
        except Exception as e:
            # print the stacktrace
            import traceback
            tb = sys.exc_info()[2]
            stacktrace = traceback.format_tb(tb)
            stacktrace_str = "".join(stacktrace)
            print("-"*50)
            print(stacktrace_str)
            print(str(e))
            print("-"*50)
            #raise TacticException(e)




    
        



class FileAppendCheckin(FileCheckin):
    '''Appends a bunch of files to an already existing snapshot'''
    def __init__(self, snapshot_code, file_paths, file_types,  mode=None, keep_file_name=True,source_paths=[], dir_naming=None, file_naming=None, checkin_type='strict', do_update_versionless=True):
        '''
        snapshot_code - the already existing snapshot to append to
        file_paths - array of all the files to checkin
        file_types - corresponding array of all the types for each file
 
        dir_naming - explicitly set the dir_naming expression to use
        file_naming - explicitly set the file_naming expression to use
        '''
        self.append_snapshot = Snapshot.get_by_code(snapshot_code)
        if not self.append_snapshot:
            raise CheckinException('Snapshot code [%s] is unknown') 
        sobject = self.append_snapshot.get_sobject()
        context = self.append_snapshot.get_value("context")
        snapshot_type = self.append_snapshot.get_value("snapshot_type")
        column = self.append_snapshot.get_value("column_name")
        
        super(FileAppendCheckin,self).__init__(sobject, file_paths, file_types, context, snapshot_type, column, mode=mode, keep_file_name=keep_file_name, source_paths=source_paths, dir_naming=dir_naming, file_naming=file_naming, checkin_type=checkin_type)

        self.is_latest = self.append_snapshot.get_value('is_latest')
        self.is_current = self.append_snapshot.get_value('is_current')

        self.do_update_versionless = do_update_versionless

        
    def create_snapshot_xml(self, file_objects):
        # take the current snapshot
        xml = self.append_snapshot.get_snapshot_xml()
        return super(FileAppendCheckin,self).create_snapshot_xml(file_objects,xml)


    def get_snapshot(self):
        return self.append_snapshot



    def create_snapshot(self, snapshot_xml):
        # copy the snapshot and put it in the snapshot history
        self.append_snapshot.set_value("snapshot", snapshot_xml)
        self.append_snapshot.commit()
        self.snapshot = self.append_snapshot

        return self.snapshot

    def get_trigger_prefix(self):
        return "add_file"

    def update_versionless(self, snapshot_mode='current'):
        if self.do_update_versionless:
            return self.snapshot.update_versionless(snapshot_mode, sobject=self.sobject, checkin_type=self.checkin_type, naming=self.naming)



class FileGroupCheckin(FileCheckin):
    '''Handles a group of files (such as frames) and treats them as a
    single entry.  This is useful for checking in large groups of related
    and similar files that are too cumbersome to treat as individual files'''

    def __init__(self, sobject, file_paths, file_types, file_range, \
            context="publish", snapshot_type="file", column="snapshot", \
            description="", keep_file_name=False, is_revision=False, mode=None, checkin_type='', version=None, process=None):

        super(FileGroupCheckin,self).__init__(sobject, file_paths, file_types, \
            context=context, snapshot_type=snapshot_type, column=column,\
            description=description, keep_file_name=keep_file_name, \
            is_revision=is_revision, mode=mode , checkin_type=checkin_type, \
            version=version, process=process)
       
        self.file_range = file_range
        self.expanded_paths = []
        self.input_snapshots = []


    def add_input_snapshot(self, snapshot):
        self.input_snapshots.append(snapshot)


    def check_files(self, file_paths):
        # do nothing here for now
        pass

    def get_expanded_paths(self):
        return self.expanded_paths

    def create_file_objects(self, files):

        file_objects = []

        for idx, file_path in enumerate(files):
            file_type = self.file_types[idx]

            # determine if this is a group or not
            if File.is_file_group(file_path):
                file_object = FileGroup.create(file_path, self.file_range, \
                    self.sobject.get_search_type(), self.sobject.get_id(), file_type=file_type )
            else:
                # create file_object
               
                file_object = File.create(file_path, \
                    self.sobject.get_search_type(), self.sobject.get_id(), file_type=file_type, st_size=self.file_sizes[idx] )
                    

            if file_object == None:
                raise FileException("File object id=[%s] is None" % file_code)

            file_objects.append(file_object)

        return file_objects




    def create_snapshot_xml(self, file_objects, snapshot_xml=None):

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
        Xml.set_attribute(root, "context", self.context )

        for i in range(0, len(file_objects)):

            file_object = file_objects[i]
            file_type = self.file_types[i]

            file_info = {}
            file_info['type'] = file_type
            if file_object.get_file_range():
                file_info['file_range'] = self.file_range.get_key()

            builder.add_file(file_object, file_info)

        for input_snapshot in self.input_snapshots:
            builder.add_ref_by_snapshot(input_snapshot)


        return builder.to_string()


    def move_file(self, file_path, new_file_path):
    
        if file_path.find('#') == -1 and file_path.find('%') == -1:
            shutil.move(file_path, new_file_path)
            return
            
        if new_file_path.find('#') == -1 and new_file_path.find('%') == -1:
            file_dir,file_ext = os.path.splitext(new_file_path)
            new_file_path = "%s.####%s" % (file_dir,file_ext)

            #raise CheckinException('The naming convention should be returning\
            #a path name with #### or %%0.4d notation in it. [%s] found instead.' % new_file_path)
        file_paths = FileGroup.expand_paths(file_path, self.file_range)
        new_file_paths = FileGroup.expand_paths(new_file_path, self.file_range)

        for i in range(0, len(file_paths)):
            file_path = file_paths[i]
            to_file_path = new_file_paths[i]
            shutil.move(file_path, to_file_path)

        return new_file_path


    def handle_system_commands(self, files, file_objects):
        '''move the tmp files in the appropriate directory'''
        if self.mode == 'inplace':
            # TODO: ? MD5?
            return
        if self.mode == 'copy':
            io_action = 'copy'
        elif self.mode  == 'preallocate':
            io_action = False
        else:
            io_action = True

        for i in range( 0, len(files) ):

            file_object = file_objects[i]
            # build the to paths
            to_name = file_object.get_full_file_name()
            file_type = self.snapshot.get_type_by_file_name(to_name)

            file_object.set_value('type', file_type)

            lib_dir = self.snapshot.get_lib_dir(file_type=file_type, file_object=file_object)
            if not os.path.exists(lib_dir):
                System().makedirs(lib_dir)
            to_path = "%s/%s" % (lib_dir, to_name )

            if file_object.get_file_range():
                from_expanded = FileGroup.expand_paths(files[i], self.file_range)
                to_expanded = FileGroup.expand_paths(to_path, self.file_range)
            else:
                from_expanded = [files[i]]
                to_expanded = [to_path]

                
            self.expanded_paths.extend(from_expanded)

            # iterate through each and copy to the lib

            for j in range(0, len(from_expanded) ):

                # check before copying
                if os.path.exists(to_expanded[j]) and self.mode not in ['inplace','preallocate']:
                    raise CheckinException('This path [%s] already exists'%to_expanded[j])
                '''
                if self.mode =='free_copy':
                    FlieUndo.copy(from_expanded[j], to_expanded[j])
                elif self.mode == 'free_move':
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
                    FileUndo.create( from_expanded[j], to_expanded[j], io_action=io_action, extra={ "md5": md5_checksum, "st_size": st_size } )

                else:
                    FileUndo.create( from_expanded[j], to_expanded[j], io_action=io_action )

                if self.mode == 'preallocate':
                    if not os.path.exists( from_expanded[j] ):
                        raise CheckinException("Source path does not exist [%s]" %from_expanded[j])
                    
                else:
                    # check to see that the file exists.
                    if not os.path.exists( to_expanded[j] ):
                        raise CheckinException("Failed copy [%s] to [%s]" % \
                        ( from_expanded[j], to_expanded[j] ) )




class FileGroupAppendCheckin(FileGroupCheckin):
    '''Appends a group of files to an already existing snapshot.
        Note: this is functionally the same as FileAppendCheckin but it 
        is derived from FileGroupCheckin
    '''
    def __init__(self, snapshot_code, file_paths, file_types, file_range, keep_file_name=False, mode=None, checkin_type='strict'):
        '''
        @params
        snapshot_code - the already existing snapshot to append to
        file_paths - array of all the files to checkin
        file_types - corresponding array of all the types for each file
        file_range - the file range of the paths
        mode - move, copy, preallocate, inplace
        '''
        self.append_snapshot = Snapshot.get_by_code(snapshot_code)
        sobject = self.append_snapshot.get_sobject()
        context = self.append_snapshot.get_value("context")
        snapshot_type = self.append_snapshot.get_value("snapshot_type")
        column = self.append_snapshot.get_value("column_name")

        super(FileGroupAppendCheckin,self).__init__(sobject, file_paths, file_types, file_range, context=context, snapshot_type=snapshot_type, column=column, keep_file_name=keep_file_name, mode=mode, checkin_type=checkin_type )


    def create_snapshot_xml(self, file_objects):
        # take the current snapshot
        xml = self.append_snapshot.get_snapshot_xml()
        return super(FileGroupAppendCheckin,self).create_snapshot_xml(file_objects,xml)



    def create_snapshot(self, snapshot_xml):

        # copy the snapshot and put it in the snapshot history
        self.append_snapshot.set_value("snapshot", snapshot_xml)
        self.append_snapshot.commit()
        self.snapshot = self.append_snapshot

        return self.snapshot

    def get_trigger_prefix(self):
        return "add_group"

