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

    def __init__(my, sobject):
        my.files = None
        my.snapshot = None
        my.snapshot_xml = None

        my.to_paths = []

     
        # these booleans should be undefined to start to prevent accidental commit in append checkin
        my.is_current = None
        my.is_latest = None

        my.is_revision = False
        my.version = None

        my.keep_file_name = False
        my.mode = None
        my.repo_type = 'tactic'

        my.file_objects = []
        super(BaseCheckin,my).__init__()

        # have to put this after because this is set to [] by Command
        my.sobject = sobject
        my.sobjects = [sobject]

        my.dir_naming = None
        my.file_naming = None

        # check project of sobject
        my.orig_project_code = None


        # This sets the project to the sobject's project. This ensure
        # that a check-in occurs alway in the project of the sobject
        project_code = sobject.get_project_code()
        # if it is task or note, find the project code attribute
        if project_code == 'admin' and sobject.has_value('project_code'):
            sobject_project_code = sobject.get_value('project_code')
            if sobject_project_code:
                my.orig_project_code = Project.get_project_code()
                Project.set_project(sobject_project_code)
        else:
            my.orig_project_code = Project.get_project_code()
            Project.set_project(project_code)

    def get_snapshot(my):
        return my.snapshot

    def get_file_objects(my):
        return my.file_objects

    def get_snapshot_xml(my):
        return my.snapshot_xml

    def set_description(my, description):
        '''set the description of what was actually checked in'''
        my.description = description

    def set_current(my, is_current):
        my.is_current = is_current

    def set_revision(my, is_revision):
        my.is_revision = is_revision


    def execute(my):
        try:
            my._execute()
        finally:
            if my.orig_project_code:
                Project.set_project(my.orig_project_code)


    def _execute(my):

        # check lock
        my.check_lock()

        # create files to be checked in
        my.files = my.create_files()

        # check that all of the files actually exist
        my.check_files(my.files)

        # register the files into the database
        my.file_objects = my.create_file_objects(my.files)

        # create the snapshot and commit (to get a snapshot code)
        my.snapshot_xml = my.create_snapshot_xml(my.file_objects)
        my.create_snapshot(my.snapshot_xml)
        my.postprocess_snapshot()

        # provide a mechanism to added extra dependencies. 
        my.add_dependencies(my.snapshot_xml)

        # update the files to reference back to the snapshot
        for idx, file_object in enumerate(my.file_objects):
            file_object.set_value("snapshot_code", my.snapshot.get_code())
            file_object.commit()
 
        # handle file naming conventions
        my.handle_file_naming()

        # preprocess any files before they go into the repository
        my.preprocess_files(my.files)

        # update metadata on check-in
        my.update_metadata(my.snapshot, my.files, my.file_objects)


        # handle all system commands
        my.handle_system_commands(my.files, my.file_objects)

        # update the versionless snapshot explicitly
        my.update_versionless("current")
        my.update_versionless("latest")


        # commit snapshot again due to changes made after file commit
        # SnapshotIsLatestTrigger is suppressed earlier when is_latest was
        # changed, so triggers here doesn't do much
        my.snapshot.commit(triggers=True)


        # add a note to the parent
        my.add_publish_note()


        # call the done trigger for checkin
        from pyasm.command import Trigger
        output = {}
        snapshot = my.get_snapshot()
        output['search_key'] = SearchKey.build_by_sobject(snapshot)
        output['update_data'] = snapshot.data.copy()

        output['snapshot'] = snapshot.get_sobject_dict()
        output['files'] = [x.get_sobject_dict() for x in my.file_objects]


        # DEPRECATED
        #Trigger.call(my, "checkin/done", output)
        prefix = my.get_trigger_prefix()
        # Add the checkin triggers
        base_search_type = my.sobject.get_base_search_type()
        Trigger.call(my, prefix, output)
        Trigger.call(my, "%s|%s" % (prefix, base_search_type), output)
        Trigger.call(my, "%s|%s|%s" % (prefix, base_search_type, my.context), output)
        # get the process (assumption here)
        Trigger.call(my, "%s|%s" % (prefix, base_search_type), output, process=my.process)

    def update_metadata(my, snapshot, files, file_objects):

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


        from metadata import CheckinMetadataHandler
        handler = CheckinMetadataHandler(snapshot=snapshot, files=metadata_files, file_objects=metadata_file_objects, commit=False)
        handler.execute()



    def rollback(my):
        for path in my.to_paths:
            if os.path.exists(path):
                os.unlink(path)


    def check_lock(my):
        # check if this is locked
        if Snapshot.is_locked(my.sobject, my.context):
            raise CheckinException("Context [%s] is locked." % my.context)



    def create_files(my):
        return []


    def create_file_objects(my, file_paths):

        file_objects = []

        for i, file_path in enumerate(file_paths):
            if my.mode in ['local','inplace']:
                requires_file = False
            else:
                requires_file = True

            
            file_type = my.file_types[i]

            # create file_object
            file_object = File.create(
                file_path,
                my.sobject.get_search_type(),
                my.sobject.get_id(),
                search_code=my.sobject.get_code(),
                requires_file=requires_file,
                repo_type=my.repo_type,
                file_type=file_type
            )

            if not file_object:
                raise FileException("File object id=[%s] is None" % file_code)
            
            file_objects.append(file_object)

        return file_objects



    def handle_file_naming(my):
      
        # this is meant for SnapshotIsLatestTrigger to run smoothly
        # these booleans should be set in the post-insert time of snapshot creation
        
        Snapshot.set_booleans(my.sobject, my.snapshot, my.is_latest, my.is_current)

        if my.keep_file_name:
            return

        file_naming = Project.get_file_naming()
        file_naming.set_sobject(my.sobject)
        file_naming.set_snapshot(my.snapshot)
        file_naming.set_naming(my.file_naming)

        # handle the file_naming conventions for each file
        count = 0
        for file_object in my.file_objects:
            file_naming.set_file_object(file_object)

            file_path = my.files[count]
            dir = os.path.dirname(file_path)
            new_file_name = file_naming.get_file_name()

            # if nothing is returned from the naming, just use the original
            # file
            if not new_file_name:
                continue

            if my.mode in ['inplace']:
                new_file_path = file_path
            else:
                new_file_path = "%s/%s" % (dir, new_file_name)

            # set the new filenames
            if file_path != new_file_path:
                # There is no file to move on the repo when the mode is local.
                # Also, for free-form mode, do not move the file because this
                # may cause conflicts.  The move occurs later in 
                # handle_system_commands
                if my.mode not in ['local', 'free_copy', 'free_move']:
                    # remap the new file path and new file name in case
                    # it changed (ie. no #### in the naming convention)
                    ret_file_path = my.move_file(file_path, new_file_path)
                    if ret_file_path:
                        new_file_path = ret_file_path
                        new_file_name = os.path.basename(new_file_path)


                my.files[count] = new_file_path

            file_object.set_value("file_name", new_file_name)
            file_object.commit(triggers=False)

            count += 1

        # Adjust the snapshot_xml to maintain backwards compatibility
        xml = my.snapshot.get_xml_value('snapshot')
        nodes = xml.get_nodes("snapshot/file")
        for node in nodes:
            file_code = Xml.get_attribute(node, "file_code")

            for file_object in my.file_objects:
                file_object_file_code = file_object.get_code()
                if file_object_file_code == file_code:
                    break
            else:
                continue


            file_name = file_object.get_value("file_name")
            Xml.set_attribute(node, "name", file_name)

        my.snapshot_xml = xml.to_string()
        my.snapshot.set_value("snapshot", my.snapshot_xml)

        # Commit is handled later
        #my.snapshot.commit(triggers=False, commit=False)


    def move_file(my, file_path, new_file_path):
        '''function to move files'''
        shutil.move( file_path, new_file_path )



    def check_files(my, file_paths):
        # don't bother checking in local mode because the files won't be there
        if my.mode in ['local','inplace']:
            return

        for file in file_paths:
            if File.has_file_code(file):
                continue

            if not System().exists(file):
                raise CheckinException("File [%s] does not exist" % file)




    def create_snapshot(my, file_paths):
        pass

    def add_dependencies(my, snapshot_xml):
        pass

    def commit_snapshot(my, snapshot_xml):
        pass


    def preprocess_files(my, files):
        pass


    def handle_system_commands(my, file_paths, file_objects):
        pass


    def get_base_path(my):
        pass


    def add_publish_note(my):
        # DISABLING because this is too overbearing.  There are way
        # too many notes created
        return

        description = my.snapshot.get_value("description")
        process = my.snapshot.get_value("process")
        context = my.snapshot.get_value("context")
        version = my.snapshot.get_value("version")

        from pyasm.biz import Note
        if description:
            description = "Check-in [v%0.3d]: %s" % (version, description)

            Note.create(my.sobject, description, context=context, process=process)


    def update_versionless(my, snapshot_mode='current'):
        # if the version is 1, then no versionless is created.  This can be
        # overwridden in the process object or by having an versionless
        # entry in the database.  This is only applicable to Windows because
        # symlinks in linux provide no overhead
        #if os.name == 'nt':
        #    version = my.snapshot.get_value("version")
        #    if version == 1:
        #        return

        return my.snapshot.update_versionless(snapshot_mode, sobject=my.sobject, checkin_type=my.checkin_type)




