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


__all__ = ['SearchTypeInputWdg', 'SearchTypeWithPipelineInputWdg']

from pyasm.search import Search, SearchType
from pyasm.biz import Project, Schema
from pyasm.web import WebContainer, Widget, DivWdg
from pyasm.widget import BaseInputWdg, SelectWdg, TextWdg, IconButtonWdg, IconWdg



class SearchTypeInputWdg(SelectWdg):

    def get_display(my):

        #project = Project.get()
        schema = Schema.get()
        # no hierarchy to prevent all sthpw and parent sTypes 
        search_type_names = schema.get_search_types(hierarchy=False)
        search = Search('sthpw/search_object')
        search.add_filters('search_type', search_type_names)
        search_types = search.get_sobjects()

        task_search_type = SearchType.get("sthpw/task")
        search_types.append(task_search_type)

        values = [ x.get_value("search_type") for x in search_types]
        labels = []
        for x in search_types:
            label = "%s (%s)" % (x.get_value("title"), x.get_value("search_type"))
            labels.append(label)


        sobject = my.get_current_sobject()
        if not sobject:
            value = ""
        else:
            value = sobject.get_value(my.get_name() )

        my.set_option("values", values)
        my.set_option("labels", labels)
        my.add_empty_option("-- Select --")
        if value:
            my.set_value(value)

        return super(SearchTypeInputWdg, my).get_display()




class SearchTypeWithPipelineInputWdg(SelectWdg):

    def get_display(my):

        #project = Project.get()
        schema = Schema.get()
        # no hierarchy to prevent all sthpw and parent sTypes 
        search_type_names = schema.get_search_types(hierarchy=False)
        search = Search('sthpw/search_object')
        search.add_filters('search_type', search_type_names)
        search_types = search.get_sobjects()

        task_search_type = SearchType.get("sthpw/task")
        search_types.append(task_search_type)

        values = [ x.get_value("search_type") for x in search_types]
        filtered = []
        labels = []
        for x in search_types:
            base_type = x.get_base_key()
            exists = SearchType.column_exists(base_type, "pipeline_code")
            if not exists:
                continue

            label = "%s (%s)" % (x.get_value("title"), x.get_value("search_type"))
            labels.append(label)
            filtered.append(base_type)


        values = filtered

        sobject = my.get_current_sobject()
        if not sobject:
            value = ""
        else:
            value = sobject.get_value(my.get_name() )

        my.set_option("values", values)
        my.set_option("labels", labels)
        my.add_empty_option("-- Select --")
        if value:
            my.set_value(value)

        return super(SearchTypeWithPipelineInputWdg, my).get_display()






