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

__all__ = ["CustomProjectTabWdg"]

from pyasm.biz import Project
from pyasm.search import Search
from pyasm.web import Widget, DivWdg, SpanWdg
from pyasm.widget import BaseTabWdg, HelpItemWdg, TabWdg, FilterSelectWdg, TableWdg, TextWdg, SelectWdg
# FIXME: move this to pyasm.admin ...
from pyasm.widget import CustomViewAppWdg
from pyasm.admin.widget import CustomizeTabWdg
from pyasm.admin.creator import SObjectCreatorWdg


class CustomProjectTabWdg(BaseTabWdg):

    def init(my):
        my.add(HelpItemWdg('Customize Project', 'Customze Project contains a collection of tabs that allow for the creation of new container types, new tabs and new interfaces', False))
        my.setup_tab("customize_project_tab", css=TabWdg.SMALL)



    def handle_tab(my, tab):
       
        tab.add( CustomizeTabWdg, _("Tab Visibility") )
        tab.add( SObjectCreatorWdg, _("Search Type Creation") )
        tab.add( CustomViewAppWdg, _("Manage Views" ) )
        tab.add(my.get_extend_wdg, _("Extend Widgets") )
        tab.add(my.get_config_wdg, _("Configure Widgets") )
        tab.add( my.get_naming_wdg, _("Naming") )


    def get_extend_wdg(my):
        widget = Widget()
        search = Search("sthpw/widget_extend")

        div = DivWdg(css="filter_box")

        # add key filter
        span = SpanWdg(css="med")
        key_select = FilterSelectWdg("key")
        key_select.add_empty_option("-- Any Key --")
        key_select.set_option("query", "sthpw/widget_extend|key|key")
        span.add("Key: ")
        span.add(key_select)
        div.add(span)

 
        # add type filter
        span = SpanWdg(css="med")
        select = FilterSelectWdg("extend_type")
        select.add_empty_option("-- Any Type --")
        select.set_option("values", "TabWdg|TableWdg")
        span.add("Widget Extend Type: ")
        span.add(select)
        div.add(span)

        widget.add(div)

        extend_type = select.get_value()
        if extend_type:
            search.add_filter("type", extend_type)

        key = key_select.get_value()
        if key:
            search.add_filter("key", key)

        # add project filter
        #search.add_where( Project.get_project_filter() )

        table = TableWdg("sthpw/widget_extend")
        table.set_search( search )

        widget.add(table)

        return widget


    def get_config_wdg(my):
        widget = Widget()

        search = Search("sthpw/widget_config")

        div = DivWdg(css="filter_box")

        span = SpanWdg(css="med")
        span.add("Search Type: ")

        select = FilterSelectWdg("config_search_type")
        select.add_empty_option("-- Select --")
        search_type_search = Search("sthpw/search_object")
        search_type_search.add_order_by("search_type")
        span.add(select)
        project = Project.get()
        project_type = project.get_base_type()
        filter = search.get_regex_filter("search_type", "login|task|note|timecard", "EQ")
        search_type_search.add_where('''
        namespace = '%s' or namespace = '%s' or %s
        ''' % (project_type, project.get_code(), filter) )
        select.set_search_for_options(search_type_search, value_column='search_type' )
        div.add(span)

        search_type_value = select.get_value()

        span = SpanWdg()
        view_text = TextWdg("view")
        view_text.set_persist_on_submit()
        span.add("View: ")
        span.add(view_text)
        div.add(span)
        widget.add(div)
        view = view_text.get_value()
        if view:
            search.add_filter("view", view)
        if search_type_value:
            search.add_filter("search_type", search_type_value)

        table = TableWdg("sthpw/widget_config")
        table.set_search( search )

        widget.add(table)

        return widget


    def get_naming_wdg(my):
        widget = Widget()
        #div = DivWdg(css="filter_box")
        #widget.add(div)

        table = TableWdg("prod/naming")
        search = Search("prod/naming")
        sobjects = search.get_sobjects()
        table.set_sobjects(sobjects)
        widget.add(table)
    
        return widget

