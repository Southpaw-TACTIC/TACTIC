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
        search_code = input.get('search_code')

        sobj_id = input.get('id')
        sobj = Search.get_by_search_key(search_key)
        if not sobj_id:
            sobj_id = sobj.get_id()

        assert(sobj_id != None)

        # it is possible that the id is not an integer (ie MongoDb)
        # In this case, search_id cannot be used and this id is considered
        # a code
        if not search_code and not isinstance(sobj_id, int):
            search_code = sobj_id

        search_type = SearchKey.extract_search_type(search_key)

        input_search_type = input.get("search_type")
        base_search_type = input_search_type.split("?")[0]

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
                mode = "delete"
                stype_obj = SearchType.get(base_search_type)
                if stype_obj.get_value('type') == 'collection':
                    asset_in_asset_sobject = input.get("sobject")
                    asset_stypes = SearchType.get_related_types(base_search_type, direction="parent")
                    if asset_stypes:
                        my.update_collection_keywords(mode, asset_stypes[0], asset_in_asset_sobject)
                sobject.delete()
            return

        elif input.get("is_insert"):
            mode = "insert"

        if not sobject:
            sobject = SearchType.create("sthpw/sobject_list")
            sobject.set_auto_code()

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


        # Updates for adding changed user defined keywords into asset keywords_data column
        if sobj.column_exists("keywords_data") and "user_keywords" in input.get("update_data"):
            # On creating new Collections
            if input.get("update_data").get("_is_collection") and input.get("is_insert"):
                update_data = input.get("update_data")

                collection_keywords = update_data.get("user_keywords")
                collection_name = update_data.get("name")

                keywords_data = sobject.get_json_value("keywords_data", {})
                keywords_data['user'] = collection_keywords
                keywords_data['path'] = collection_name
                sobj.set_json_value("keywords_data", keywords_data)
                sobj.commit(triggers=False)

            # when user defined keywords column is changed 
            else:
                user_keywords = input.get("update_data").get("user_keywords")

                if not user_keywords:
                    user_keywords = ""
                my.update_user_keywords(sobj, user_keywords, base_search_type)

            my.set_searchable_keywords(sobj)

        # Collection relationships being created or added
        stype_obj = SearchType.get(base_search_type)
        if stype_obj.get_value('type') == 'collection':
            asset_in_asset_sobject = input.get("sobject")
            asset_stypes = SearchType.get_related_types(base_search_type, direction="parent")
            if asset_stypes:
                my.update_collection_keywords(mode, asset_stypes[0], asset_in_asset_sobject)

        
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
     
    def set_searchable_keywords(my, sobj):
        '''
        Used to set the keywords column. Reads from the keywords_data
        column.
        '''
        if not sobj.column_exists("keywords"):
            return

        keywords_data = sobj.get_json_value("keywords_data", {})

        if keywords_data:
            path = ""
            if 'path' in keywords_data:
                path = keywords_data.get('path')

            if 'user' in keywords_data:
                user = keywords_data.get('user')
                if not user:
                    user = ""

            collection_list = []
            if 'collection' in keywords_data:
                collection_keywords_data = keywords_data.get('collection')
                for collection_code in collection_keywords_data.keys():
                    collection_list.append(collection_keywords_data.get(collection_code))
                    
            searchable_keywords = "%s %s %s" %(path, user, " ".join(collection_list))

            sobj.set_value("keywords", searchable_keywords)
            sobj.commit(triggers=False)

    def update_user_keywords(my, sobj, user_keywords, search_type):

        search_key = sobj.get_search_key()
        keywords_data = sobj.get_json_value("keywords_data", {})

        keywords_data['user'] = user_keywords
        
        # If the collection's keywords column gets changed, all of its 
        # children's "collection" keywords_data needs to be updated
        if sobj.get('_is_collection'):

            child_codes = my.get_child_codes(sobj.get_code(), search_type)
            
            if child_codes:
                for child_code in child_codes:
                    child_nest_sobject = Search.get_by_code(search_type, child_code)
                    child_nest_collection_keywords_data = child_nest_sobject.get_json_value("keywords_data", {})
                    child_nest_collection_keywords_data['collection'][sobj.get_code()] = user_keywords

                    child_nest_sobject.set_json_value("keywords_data", child_nest_collection_keywords_data)
                    child_nest_sobject.commit(triggers=False)
                    my.set_searchable_keywords(child_nest_sobject)

        sobj.set_json_value("keywords_data", keywords_data)
        sobj.commit(triggers=False)

    def get_child_codes(my, parent_collection_code, search_type):

        from pyasm.biz import Project
        project = Project.get()
        sql = project.get_sql()
        impl = project.get_database_impl()
        search_codes = []

        parts = search_type.split("/")
        collection_type = "%s/%s_in_%s" % (parts[0], parts[1], parts[1])

        # Check if connection between asset and asset_in_asset is in place
        if collection_type not in SearchType.get_related_types(search_type):
            return search_codes

        var_dict = {
            'parent_collection_code': parent_collection_code,
            'collection_type': collection_type.split("/")[1],
            'search_type': search_type.split("/")[1]
        }
        stmt = impl.get_child_code_cte(var_dict)
        

        results = sql.do_query(stmt)
        for result in results:
            result = "".join(result)
            search_codes.append(result)

        return search_codes

    def update_collection_keywords(my, mode, asset_stype, asset_in_asset_sobject):
        
        parent_code = asset_in_asset_sobject.get("parent_code")
        search_code = asset_in_asset_sobject.get("search_code")
        
        parent_sobject = Search.get_by_code(asset_stype, parent_code)
        child_sobject = Search.get_by_code(asset_stype, search_code)
        
        # keywords of parent
        parent_collection_keywords = parent_sobject.get_value("user_keywords")

        collection_keywords_dict = {}
        parent_collection_keywords_dict = {}

        # Existing "collection" keywords in child's keywords_data
        child_keywords_data = child_sobject.get_json_value("keywords_data", {})

        # Existing "collection" keywords in parent's keywords_data
        parent_keywords_data = parent_sobject.get_json_value("keywords_data", {})

        if 'collection' in child_keywords_data:
            collection_keywords_dict = child_keywords_data.get('collection')

        if 'collection' in parent_keywords_data:
            parent_collection_keywords_dict = parent_keywords_data.get('collection')

        if mode == "insert":
            # Add parent's user defined keywords
            collection_keywords_dict[parent_code] = parent_collection_keywords

            # Also append parent's "collection" keywords_data
            collection_keywords_dict.update(parent_collection_keywords_dict)

            # Find all children that has [search_code] in their collection's keys
            # and update
            child_codes = my.get_child_codes(search_code, asset_stype)

            if child_codes:
                for child_code in child_codes:
                    child_nest_sobject = Search.get_by_code(asset_stype, child_code)
                    child_nest_collection_keywords_data = child_nest_sobject.get_json_value("keywords_data", {})
                    child_nest_collection_keywords = child_nest_collection_keywords_data['collection']
                    child_nest_collection_keywords.update(collection_keywords_dict)

                    child_nest_sobject.set_json_value("keywords_data", child_nest_collection_keywords_data)
                    child_nest_sobject.commit(triggers=False)
                    my.set_searchable_keywords(child_nest_sobject)
        elif mode == "delete":

            # Remove "collection" keywords_data from child with key matching parent_code
            del collection_keywords_dict[parent_code]

            # Also need to remove parent's "collection" keywords_data from child
            for key in parent_collection_keywords_dict.keys():
                del collection_keywords_dict[key]

            child_codes = my.get_child_codes(search_code, asset_stype)
            
            if child_codes:
                for child_code in child_codes:
                    child_nest_sobject = Search.get_by_code(asset_stype, child_code)
                    child_nest_collection_keywords_data = child_nest_sobject.get_json_value("keywords_data", {})
                    child_nest_collection_keywords = child_nest_collection_keywords_data['collection']
                    
                    del child_nest_collection_keywords[parent_code]

                    child_nest_sobject.set_json_value("keywords_data", child_nest_collection_keywords_data)
                    child_nest_sobject.commit(triggers=False)
                    my.set_searchable_keywords(child_nest_sobject)

        child_keywords_data['collection'] = collection_keywords_dict

        child_sobject.set_json_value("keywords_data", child_keywords_data)
        child_sobject.commit(triggers=False)

        my.set_searchable_keywords(child_sobject)
        


class FolderTrigger(Trigger):

    def execute(my):

        # DISABLING: this used to be needed for Repo Browser layout, but
        # is no longer needed
        return

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
        file_obj.set_auto_code()
        file_obj.set_sobject_value(sobject)
        file_obj.set_value("file_name", "")
        file_obj.set_value("relative_dir", relative_dir)
        file_obj.set_value("type", "main")
        file_obj.set_value("base_type", "sobject_directory")
        file_obj.commit(triggers=False)

        from pyasm.search import FileUndo
        if not os.path.exists(dirname):
            FileUndo.mkdir(dirname)





