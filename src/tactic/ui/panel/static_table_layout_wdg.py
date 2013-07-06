###########################################################
#
# Copyright (c) 2009, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#
__all__ = ["StaticTableLayoutWdg"]

from pyasm.common import Common
from pyasm.search import Search, SearchKey
from pyasm.web import DivWdg, Table
from pyasm.widget import ThumbWdg, IconWdg

from table_layout_wdg import FastTableLayoutWdg
from tactic.ui.widget import SingleButtonWdg

class StaticTableLayoutWdg(FastTableLayoutWdg):

    ARGS_KEYS = {

        "mode": {
            'description': "Determines whether to draw with widgets or just use the raw data",
            'type': 'SelectWdg',
            'values': 'widget|raw',
            'order': 0,
            'category': 'Required'
        },

        "search_type": {
            'description': "search type that this panels works with",
            'type': 'TextWdg',
            'order': 1,
            'category': 'Required'
        },
        "view": {
            'description': "view to be displayed",
            'type': 'TextWdg',
            'order': 2,
            'category': 'Required'
        },
        "element_names": {
            'description': "Comma delimited list of elemnent to view",
            'type': 'TextWdg',
            'order': 0,
            'category': 'Optional'
        },
        "show_shelf": {
            'description': "Determines whether or not to show the action shelf",
            'type': 'SelectWdg',
            'values': 'true|false',
            'order': 1,
            'category': 'Optional'
        },



    } 


    def get_display(my):
        #my.chunk_size = 10000

        if my.kwargs.get("do_search") != "false":
            my.handle_search()

        my.mode = my.kwargs.get("mode")
        if my.mode != 'raw':
            my.mode = 'widget'


        # extraneous variables inherited from TableLayoutWdg
        my.edit_permission = False

        top = DivWdg()
        my.set_as_panel(top)
        top.add_class("spt_sobject_top")


        inner = DivWdg()
        top.add(inner)
        inner.add_color("background", "background")
        inner.add_color("color", "color")
        inner.add_class("spt_table")
        inner.add_class("spt_layout")
        inner.add_attr("spt_version", "2")
        
        table = my.table
        table.add_class("spt_table_table")
        # set the sobjects to all the widgets then preprocess
        if my.mode == 'widget':
            for widget in my.widgets:
                widget.handle_layout_behaviors(table)
                widget.set_sobjects(my.sobjects)
                widget.set_parent_wdg(my)
                # preprocess the elements
                widget.preprocess()
        else:
            for i, widget in enumerate(my.widgets):
                #widget.handle_layout_behaviors(table)
                widget.set_sobjects(my.sobjects)
                #widget.set_parent_wdg(my)
                # preprocess the elements
                widget.preprocess()




        is_refresh = my.kwargs.get("is_refresh")
        if my.kwargs.get("show_shelf") not in ['false', False]:
            action = my.get_action_wdg()
            inner.add(action)

        index = 0

        table.add_attr("spt_view", my.kwargs.get("view") )
        table.set_attr("spt_search_type", my.kwargs.get('search_type'))
       
        table.set_id(my.table_id)
        
        table.add_style("width: 100%")
        inner.add(table)
        table.add_color("color", "color")

        # initialize the spt.table js
        my.handle_table_behaviors(table)

        my.handle_headers(table)

        border_color = table.get_color("table_border", default="border")
        for row, sobject in enumerate(my.sobjects):
            tr = table.add_row()
            if row % 2:
                background = tr.add_color("background", "background")
            else:
                background = tr.add_color("background", "background", -7)

            tr.add_class("spt_table_row")
            tr.add_attr("spt_search_key", sobject.get_search_key())

            for widget in my.widgets:

                value_div = DivWdg()
                value_div.add_style("padding: 3px")
                td = table.add_cell(value_div)
                td.add_style("vertical-align: top")
                td.add_style("border: solid 1px %s" % border_color)

                if my.mode == 'widget':
                    widget.set_current_index(row)
                    value_div.add(widget.get_buffer_display())
                else:
                    element_name = widget.get_name()
                    value = sobject.get_value(element_name, no_exception=True)
                    value_div.add(value)


        top.add_class("spt_table_top");
        class_name = Common.get_full_class_name(my)
        top.add_attr("spt_class_name", class_name)

        table.add_class("spt_table_content");
        inner.add_attr("spt_search_type", my.kwargs.get('search_type'))
        inner.add_attr("spt_view", my.kwargs.get('view'))

        # extra ?? Doesn't really work to keep the mode
        inner.add_attr("spt_mode", my.mode)
        top.add_attr("spt_mode", my.mode)

        inner.add("<br clear='all'/>")


        if my.kwargs.get("is_refresh") == 'true':
            return inner
        else:
            return top


    def handle_headers(my, table):

        # Add the headers
        tr = table.add_row()
        tr.add_class("spt_table_header_row")
        for i, widget in enumerate(my.widgets):
            widget_name = widget.get_name()
            th = table.add_header()
            th.add_style("text-align: left")
            th.add_attr("spt_element_name", widget_name)
            header_div = DivWdg()
            th.add(header_div)
            th.add_style("padding: 3px")
            th.add_gradient("background", "background", -10)
            th.add_border()

            if my.mode == 'widget':
                value = widget.get_title()
            else:
                element = widget_name
                value = Common.get_display_title(element)
            header_div.add(value)

            widget.handle_th(th, i)


