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
__all__ = ['GlobalSearchTrigger']

import tacticenv

from pyasm.common import Common
from pyasm.biz import Project
from pyasm.search import SearchType, Search, SearchKey
from pyasm.command import Command, Trigger

import os

class GlobalSearchTrigger(Trigger):

   

    def execute(my):

        input = my.get_input()
        search_key = input.get("search_key")
        sobj_id = input.get('id')
        assert(sobj_id)


        search_type = SearchKey.extract_search_type(search_key)
        
        # find the old sobject
        if sobj_id != -1:
            search = Search("sthpw/sobject_list")
            search.add_filter( "search_type", search_type )
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
     



