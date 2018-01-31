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

__all__ = ['CheckinException', 'BaseCheckin']

import sys, string, os, time, shutil
from cStringIO import *

from pyasm.common import *
from pyasm.search import *
from pyasm.command import *
from pyasm.biz import *
from pyasm.prod.biz import ProdSetting

class CheckinException(TacticException):
    pass


class BaseCheckin(Command):
    '''defines the pipeline for checking in a snapshot'''

    def __init__(self, sobject):
        self.files = None
        self.snapshot = None
        self.snapshot_xml = None

        self.to_paths = []

        # these booleans should be undefined to start to prevent accidental commit in append checkin
        self.is_current = None
        self.is_latest = None

        self.is_revision = False
        self.version = None

        self.keep_file_name = False
        self.mode = None
        self.repo_type = 'tactic'

        self.file_objects = []
        super(BaseCheckin,self).__init__()

        # have to put this after because this is set to [] by Command
        self.sobject = sobject
        self.sobjects = [sobject]

        self.dir_naming = None
        self.file_naming = None
        self.naming = None

        # check project of sobject
        self.orig_project_code = None


        # This sets the project to the sobject's project. This ensure
        # that a check-in occurs alway in the project of the sobject
        project_code = sobject.get_project_code()
        # if it is task or note, find the project code attribute
        if project_code == 'admin' and sobject.has_value('project_code'):
            sobject_project_code = sobject.get_value('project_code')
            if sobject_project_code:
                self.orig_project_code = Project.get_project_code()
                Project.set_project(sobject_project_code)
        else:
            self.orig_project_code = Project.get_project_code()
            Project.set_project(project_code)

    def get_snapshot(self):
        return self.snapshot

    def get_file_objects(self):
        return self.file_objects

    def get_snapshot_xml(self):
        return self.snapshot_xml

    def set_description(self, description):
        '''set the description of what was actually checked in'''
        self.description = description

    def set_current(self, is_current):
        self.is_current = is_current

    def set_revision(self, is_revision):
        self.is_revision = is_revision


    def execute(self):
        try:
            self._execute()
        finally:
            if self.orig_project_code:
                Project.set_project(self.orig_project_code)


    def _execute(self):

        # check lock
        self.check_lock()

        # create files to be checked in
        self.files = self.create_files()

        # check that all of the files actually exist
        self.check_files(self.files)

        # register the files into the database
        self.file_objects = self.create_file_objects(self.files)

        # create the snapshot and commit (to get a snapshot code)
        self.snapshot_xml = self.create_snapshot_xml(self.file_objects)
        self.create_snapshot(self.snapshot_xml)
        self.postprocess_snapshot()

        # provide a mechanism to added extra dependencies. 
        self.add_dependencies(self.snapshot_xml)

        # update the files to reference back to the snapshot
        for idx, file_object in enumerate(self.file_objects):
            file_object.set_value("snapshot_code", self.snapshot.get_code())
            file_object.commit()
 
        # handle file naming conventions
        self.handle_file_naming()

        # preprocess any files before they go into the repository
        self.preprocess_files(self.files)

        # update metadata on check-in
        self.update_metadata(self.snapshot, self.files, self.file_objects)


        # handle all system commands
        self.handle_system_commands(self.files, self.file_objects)

        # update the versionless snapshot explicitly
        self.update_versionless("current")
        self.update_versionless("latest")


        # commit snapshot again due to changes made after file commit
        # SnapshotIsLatestTrigger is suppressed earlier when is_latest was
        # changed, so triggers here doesn't do much
        self.snapshot.commit(triggers=True)


        # add a note to the parent
        self.add_publish_note()
        
        self.call_triggers()

    def get_trigger_prefix(self):
        return "checkin"

    def call_triggers(self):

        # call the done trigger for checkin
        from pyasm.command import Trigger
        output = {}
        snapshot = self.get_snapshot()
        output['search_key'] = SearchKey.build_by_sobject(snapshot)
        output['update_data'] = snapshot.data.copy()
        output['snapshot'] = snapshot.get_sobject_dict()
        output['files'] = [x.get_sobject_dict() for x in self.file_objects]


        # DEPRECATED
        #Trigger.call(self, "checkin/done", output)
        prefix = self.get_trigger_prefix()
        # Add the checkin triggers
        base_search_type = self.sobject.get_base_search_type()
        Trigger.call(self, prefix, output)
        Trigger.call(self, "%s|%s" % (prefix, base_search_type), output)
        Trigger.call(self, "%s|%s|%s" % (prefix, base_search_type, self.context), output)
        
        # get the process (assumption here) and call both on process and process code
        process = self.process
        pipeline = None
        if process:
            Trigger.call(self, "%s|%s" % (prefix, base_search_type), output, process=process)
        
            pipeline_code = self.sobject.get_value("pipeline_code", no_exception=True)
            if pipeline_code:
                pipeline = Pipeline.get_by_code(pipeline_code)

            if pipeline and process:
                search = Search("config/process")
                search.add_filter("pipeline_code", pipeline_code)
                search.add_filter("process", process)
                process_sobj = search.get_sobject()
                if process_sobj:
                    process_code = process_sobj.get_code()
                    Trigger.call(self, "%s|%s" % (prefix, base_search_type), output, process=process_code)


    def update_metadata(self, snapshot, files, file_objects):

        record_metadata = True
        if not record_metadata:
            return

        # we don't need to update the metadata of secondary files, so ignore
        # icon and web
        metadata_files = []
        metadata_file_objects = []
        for file, file_object in zip(files, file_objects):
            file_type = file_object.get_value("type")
            if file_type in ['icon', 'web']:
                continue
            metadata_files.append(file)
            metadata_file_objects.append(file_object)


        search_type = snapshot.get_value("search_type")
        parser = SearchType.get(search_type).get_value("metadata_parser", no_exception=True)
        if parser:
            from metadata import CheckinMetadataHandler
            handler = CheckinMetadataHandler(snapshot=snapshot, files=metadata_files, file_objects=metadata_file_objects, commit=False, parser=parser)
            handler.execute()



    def rollback(self):
        for path in self.to_paths:
            if os.path.exists(path):
                os.unlink(path)


    def check_lock(self):
        # check if this is locked
        if Snapshot.is_locked(self.sobject, self.context):
            raise CheckinException("Context [%s] is locked." % self.context)



    def create_files(self):
        return []


    def create_file_objects(self, file_paths):

        file_objects = []

        for i, file_path in enumerate(file_paths):
            if self.mode in ['local','inplace']:
                requires_file = False
            else:
                requires_file = True

            file_type = self.file_types[i]

            # create file_object
            file_object = File.create(
                file_path,
                self.sobject.get_search_type(),
                self.sobject.get_id(),
                search_code=self.sobject.get_code(),
                requires_file=requires_file,
                repo_type=self.repo_type,
                file_type=file_type,
            )

            if not file_object:
                raise FileException("File object id=[%s] is None" % file_code)
            
            file_objects.append(file_object)

        return file_objects



    def handle_file_naming(self):
        # this is meant for SnapshotIsLatestTrigger to run smoothly
        # these booleans should be set in the post-insert time of snapshot creation
        
        Snapshot.set_booleans(self.sobject, self.snapshot, self.is_latest, self.is_current)

        if self.keep_file_name:
            return

        file_naming = Project.get_file_naming()
        file_naming.set_sobject(self.sobject)
        file_naming.set_snapshot(self.snapshot)
        file_naming.set_naming(self.file_naming)
        file_naming.set_checkin_type(self.checkin_type)

        # handle the file_naming conventions for each file
        count = 0
        for file_object in self.file_objects:

            file_path = self.files[count]

            # inplace does not use naming
            if self.mode in ['inplace']:
                new_file_path = file_path
                new_file_name = os.path.basename(file_path)

            else:

                file_naming.set_file_object(file_object)

                dir = os.path.dirname(file_path)
                new_file_name = file_naming.get_file_name()

                # if nothing is returned from the naming, just use the original
                # file
                if not new_file_name:
                    continue

                new_file_path = "%s/%s" % (dir, new_file_name)

            # set the new filenames
            if file_path != new_file_path:
                # There is no file to move on the repo when the mode is local.
                # Also, for move, copy mode, do not move the file because this
                # may cause conflicts.  The move/copy occurs later in 
                # handle_system_commands
                if self.mode not in ['local', 'copy', 'move']:
                    # remap the new file path and new file name in case
                    # it changed (ie. no #### in the naming convention)
                    ret_file_path = self.move_file(file_path, new_file_path)
                    if ret_file_path:
                        new_file_path = ret_file_path
                        new_file_name = os.path.basename(new_file_path)


                self.files[count] = new_file_path


            assert(new_file_name)

            file_object.set_value("file_name", new_file_name)
            file_object.commit(triggers=False)

            count += 1

        # Adjust the snapshot_xml to maintain backwards compatibility
        xml = self.snapshot.get_xml_value('snapshot')
        nodes = xml.get_nodes("snapshot/file")
        for node in nodes:
            file_code = Xml.get_attribute(node, "file_code")

            for file_object in self.file_objects:
                file_object_file_code = file_object.get_code()
                if file_object_file_code == file_code:
                    break
            else:
                continue


            file_name = file_object.get_value("file_name")
            Xml.set_attribute(node, "name", file_name)

        self.snapshot_xml = xml.to_string()
        self.snapshot.set_value("snapshot", self.snapshot_xml)

        # Commit is handled later
        #self.snapshot.commit(triggers=False, commit=False)


    def move_file(self, file_path, new_file_path):
        '''function to move files'''
        shutil.move( file_path, new_file_path )



    def check_files(self, file_paths):
        # don't bother checking in local mode because the files won't be there
        if self.mode in ['local','inplace']:
            return
        for file in file_paths:
            #if File.has_file_code(file):
            #    continue

            if not System().exists(file):
                raise CheckinException("File [%s] does not exist" % file)




    def create_snapshot(self, file_paths):
        pass

    def add_dependencies(self, snapshot_xml):
        pass

    def commit_snapshot(self, snapshot_xml):
        pass


    def preprocess_files(self, files):
        pass


    def handle_system_commands(self, file_paths, file_objects):
        pass


    def get_base_path(self):
        pass


    def add_publish_note(self):
        # DISABLING because this is too overbearing.  There are way
        # too many notes created
        return

        description = self.snapshot.get_value("description")
        process = self.snapshot.get_value("process")
        context = self.snapshot.get_value("context")
        version = self.snapshot.get_value("version")

        from pyasm.biz import Note
        if description:
            description = "Check-in [v%0.3d]: %s" % (version, description)

            Note.create(self.sobject, description, context=context, process=process)


    def update_versionless(self, snapshot_mode='current'):
        # if the version is 1, then no versionless is created.  This can be
        # overwridden in the process object or by having an versionless
        # entry in the database.  This is only applicable to Windows because
        # symlinks in linux provide no overhead
        #if os.name == 'nt':
        #    version = self.snapshot.get_value("version")
        #    if version == 1:
        #        return

        return self.snapshot.update_versionless(snapshot_mode, sobject=self.sobject, checkin_type=self.checkin_type, naming=self.naming)




