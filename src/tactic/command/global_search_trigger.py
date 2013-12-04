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
__all__ = ['GlobalSearchTrigger', 'FolderTrigger']

import tacticenv

from pyasm.common import Common, Environment
from pyasm.biz import Project
from pyasm.search import SearchType, Search, SearchKey
from pyasm.command import Command, Trigger

import os

class GlobalSearchTrigger(Trigger):

    def get_title(my):
        return "Added entry to global search"

    def execute(my):

        input = my.get_input()
        search_key = input.get("search_key")
        sobj_id = input.get('id')
        search_code = input.get('search_code')
        assert(sobj_id)

        # it is possible that the id is not an integer (ie MongoDb)
        # In this case, search_id cannot be used and this id is considered
        # a code
        if not search_code and not isinstance(sobj_id, int):
            search_code = sobj_id

        search_type = SearchKey.extract_search_type(search_key)
        
        # find the old sobject
        if sobj_id != -1:
            search = Search("sthpw/sobject_list")
            search.add_filter( "search_type", search_type )
            if search_code:
                search.add_filter( "search_code", search_code )
            else:
                search.add_filter( "search_id", sobj_id )
            sobject = search.get_sobject()
        else:
            sobject = None
        
        
        if input.get("is_delete") == True:
            if sobject:
                sobject.delete()
            return

        if not sobject:
            sobject = SearchType.create("sthpw/sobject_list")


        if not search_type.startswith("sthpw/"):
            project_code = Project.extract_project_code(search_type)
        else:
            project = "admin"

        sobject.set_value("project_code", project_code)



        caller = my.get_caller()

        data = set()

        data.update( my.cleanup(caller.get_value("code", no_exception=True) ))
        data.update( my.cleanup(caller.get_value("name", no_exception=True) ))
        data.update( my.cleanup(caller.get_value("description", no_exception=True) ))
        data.update( my.cleanup(caller.get_value("keywords", no_exception=True) ))

        # extra columns to add
        columns = []
        for column in columns:
            data.append( my.cleanup(caller.get_value(column) ))

        
        keywords = " ".join(data)
        sobject.set_value("keywords", keywords)

        sobject.set_parent(caller)
        sobject.commit(triggers=False)



    def cleanup(my, data):
        #is_ascii = my.is_ascii(data)
        return Common.extract_keywords(data)
     



class FolderTrigger(Trigger):

    def execute(my):
        from pyasm.biz import Snapshot, Naming

        input = my.get_input()
        search_key = input.get("search_key")
        search_type = input.get('search_type')
        sobject = my.get_caller()
        assert search_type

        search_type_obj = SearchType.get(search_type)

        # FIXME: this should be in SearchType
        base_dir = Environment.get_asset_dir()

        root_dir = search_type_obj.get_value("root_dir", no_exception=True)
        if not root_dir:
            base_type = search_type_obj.get_base_key()
            parts = base_type.split("/")
            relative_dir = parts[1]


        # FIXME: need to use naming here
        file_type = 'main'
        snapshot_type = "file"
        process = "publish"

        virtual_snapshot = Snapshot.create_new()
        virtual_snapshot_xml = '<snapshot><file type=\'%s\'/></snapshot>' %(file_type)
        virtual_snapshot.set_value("snapshot", virtual_snapshot_xml)
        virtual_snapshot.set_value("snapshot_type", snapshot_type)

        # NOTE: keep these empty to produce a folder without process
        # or context ...
        # Another approach would be to find all the possible processes
        # and create folders for them

        # since it is a a file name based context coming in, use process
        #virtual_snapshot.set_value("process", process)
        #virtual_snapshot.set_value("context", process)

        # ???? Which is the correct one?
        virtual_snapshot.set_sobject(sobject)
        virtual_snapshot.set_parent(sobject)
        
        #naming = Naming.get(sobject, virtual_snapshot)
        #print "naming: ", naming.get_data()

        # Need to have a fake file because preallocated path also looks at
        # the file
        file_name = 'test.jpg'
        mkdirs = False
        ext = 'jpg'

        path = virtual_snapshot.get_preallocated_path(file_type, file_name, mkdirs, ext=ext, parent=sobject)
        dirname = os.path.dirname(path)

        if isinstance(path, unicode):
            path = path.encode('utf-8')
        else:
            path = unicode(path, errors='ignore').encode('utf-8')

        #dirname = "%s/%s/%s/" % (base_dir, project_code, root_dir)

        base_dir = Environment.get_asset_dir()
        relative_dir = dirname.replace(base_dir, "")
        relative_dir = relative_dir.strip("/")

        # create a file object
        file_obj = SearchType.create("sthpw/file")
        file_obj.set_sobject_value(sobject)
        file_obj.set_value("file_name", "")
        file_obj.set_value("relative_dir", relative_dir)
        file_obj.set_value("type", "main")
        file_obj.set_value("base_type", "sobject_directory")
        file_obj.commit(triggers=False)

        from pyasm.search import FileUndo
        if not os.path.exists(dirname):
            FileUndo.mkdir(dirname)





