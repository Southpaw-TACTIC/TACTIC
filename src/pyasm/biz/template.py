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

__all__ = ["Template"]


from pyasm.search import Search, SObject, SearchType


class Template(SObject):

    SEARCH_TYPE = "sthpw/template"
    
    def get(code, project_code):
        search = Search(Template.SEARCH_TYPE)
        search.add_filter("code", code)
        search.add_filter("project_code", project_code)
        return search.get_sobject()
    get = staticmethod(get)

    def get_by_search_type(search_type):

        search = Search(Template.SEARCH_TYPE)
        search.add_filter("search_type", search_type)

        search.add_order_by("timestamp desc")

        return search.do_search()
    get_by_search_type = staticmethod(get_by_search_type)

    def get_latest(search_type, category=None, project=None):
        search = Search(Template.SEARCH_TYPE)
        search.add_filter("search_type", search_type)
        
        if category:
            search.add_filter("category", category)
        
        if not project:
            project = SearchType.get_project()
        search.add_filter("project_code", project)    
        
        search.add_order_by("code desc")    
        return search.get_sobject() 
    get_latest = staticmethod(get_latest)

    



