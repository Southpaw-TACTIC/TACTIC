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


__all__ = ['SearchTypeInputWdg']

from pyasm.search import Search, SearchType
from pyasm.biz import Project
from pyasm.web import WebContainer, Widget, DivWdg
from pyasm.widget import BaseInputWdg, SelectWdg, TextWdg, IconButtonWdg, IconWdg



class SearchTypeInputWdg(SelectWdg):

    def get_display(my):

        project = Project.get()
        search_types = project.get_search_types()

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




