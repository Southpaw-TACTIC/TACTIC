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

from pyasm.web import *
from pyasm.widget import *
from pyasm.admin import *



class CustomTabWdg(Widget):

    def init(my):
        tab = TabWdg()
        tab.set_tab_key("custom_tab")
        my.handle_tab(tab)
        my.add(tab)




    def handle_tab(my, tab):
        search = Search( SearchType.SEARCH_TYPE )
        search.add_filter("namespace", "bar")
        search_types = search.get_sobjects()

        tab_value = tab.get_tab_value()
        for search_type in search_types:
            title = search_type.get_title()

            if tab_value == title:
                wdg = my._get_tab_wdg(search_type)
                tab.add(wdg, title)
            else:
                tab.add(None, title)



    def _get_tab_wdg(my, search_type):

        widget_config = WidgetConfig.get_by_search_type(search_type,"default")

        div = DivWdg()
        div.add_style("background-color: white")
        div.add_style("text-align: center")

        filter = TextWdg("search")
        filter.set_persistence()
        filter_value = filter.get_value()
        filter_value = filter_value.lower()

        div.add("<b>Search:</b> ")

        category_names = widget_config.get_element_names("category")
        if category_names:
            select = SelectWdg("column")
            select.set_option("values", "|".join(category_names) )
            select.set_option("labels", "|".join(category_names) )
            select.add_empty_option()
            div.add(select)


        div.add(filter)
        div.add(IconRefreshWdg())

        key = search_type.get_full_key()
        table = TableWdg(key,"default")
        search = Search(key)


        # get the columns to search under
        if filter_value != "":
            columns = widget_config.get_element_names("category")
            expressions = []
            for column in columns:
                expression = "lower(%s) like '%%%s%%'" % (column, filter_value)
                expressions.append(expression)

            if expressions:
                search.add_where("( %s )" % " or ".join(expressions))
            else:
                search.add_where("NULL")


        table.set_search(search)

        div.add(table)


        return div







