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


    def get_display(self):
        #self.chunk_size = 10000

        if self.kwargs.get("do_search") != "false":
            self.handle_search()

        self.mode = self.kwargs.get("mode")
        if self.mode != 'raw':
            self.mode = 'widget'


        # extraneous variables inherited from TableLayoutWdg
        self.edit_permission = False

        top = DivWdg()
        self.set_as_panel(top)
        top.add_class("spt_sobject_top")


        inner = DivWdg()
        top.add(inner)
        inner.add_color("background", "background")
        inner.add_color("color", "color")
        inner.add_class("spt_table")
        inner.add_class("spt_layout")
        inner.add_attr("spt_version", "2")
        
        table = self.table
        table.add_class("spt_table_table")
        # set the sobjects to all the widgets then preprocess
        if self.mode == 'widget':
            for widget in self.widgets:
                widget.handle_layout_behaviors(table)
                widget.set_sobjects(self.sobjects)
                widget.set_parent_wdg(self)
                # preprocess the elements
                widget.preprocess()
        else:
            for i, widget in enumerate(self.widgets):
                #widget.handle_layout_behaviors(table)
                widget.set_sobjects(self.sobjects)
                #widget.set_parent_wdg(self)
                # preprocess the elements
                widget.preprocess()


        self.process_groups()
        self.order_sobjects(self.sobjects, self.group_columns)
        self.remap_sobjects()


        self.attributes = []
        for i, widget in enumerate(self.widgets):
            element_name = widget.get_name()

            if element_name and element_name != "None":
                attrs = self.config.get_element_attributes(element_name)
            else:
                attrs = {}
            
            self.attributes.append(attrs)
 


        is_refresh = self.kwargs.get("is_refresh")
        if self.kwargs.get("show_shelf") not in ['false', False]:
            action = self.get_action_wdg()
            inner.add(action)

        index = 0

        table.add_attr("spt_view", self.kwargs.get("view") )
        table.set_attr("spt_search_type", self.kwargs.get('search_type'))
       
        table.set_id(self.table_id)
        
        table.add_style("width: 100%")
        inner.add(table)
        table.add_color("color", "color")

        # initialize the spt.table js
        #self.handle_table_behaviors(table)

        self.handle_headers(table)

        border_color = table.get_color("table_border", default="border")
        for row, sobject in enumerate(self.sobjects):

            # put in a group row
            if self.is_grouped:
                self.handle_groups(table, row, sobject)

            tr = table.add_row()
            if row % 2:
                background = tr.add_color("background", "background")
            else:
                background = tr.add_color("background", "background", -1)

            tr.add_class("spt_table_row")
            tr.add_attr("spt_search_key", sobject.get_search_key())



            for i, widget in enumerate(self.widgets):

                value_div = DivWdg()
                value_div.add_style("padding: 3px")
                td = table.add_cell(value_div)
                td.add_style("vertical-align: top")
                td.add_style("border: solid 1px %s" % border_color)

                if self.mode == 'widget':
                    widget.set_current_index(row)
                    value_div.add(widget.get_buffer_display())
                else:
                    element_name = widget.get_name()
                    value = sobject.get_value(element_name, no_exception=True)
                    value_div.add(value)


        top.add_class("spt_table_top");
        class_name = Common.get_full_class_name(self)
        top.add_attr("spt_class_name", class_name)

        table.add_class("spt_table_content");
        inner.add_attr("spt_search_type", self.kwargs.get('search_type'))
        inner.add_attr("spt_view", self.kwargs.get('view'))

        # extra ?? Doesn't really work to keep the mode
        inner.add_attr("spt_mode", self.mode)
        top.add_attr("spt_mode", self.mode)

        inner.add("<br clear='all'/>")


        if self.kwargs.get("is_refresh") == 'true':
            return inner
        else:
            return top


    def handle_headers(self, table):

        # this comes from refresh
        widths = self.kwargs.get("column_widths")


        # Add the headers
        tr = table.add_row()
        tr.add_class("spt_table_header_row")
        for i, widget in enumerate(self.widgets):
            widget_name = widget.get_name()
            th = table.add_header()
            th.add_style("text-align: left")
            th.add_attr("spt_element_name", widget_name)
            header_div = DivWdg()
            th.add(header_div)
            th.add_style("padding: 3px")
            th.add_color("background", "background", -5)
            th.add_border()

            if self.mode == 'widget':
                value = widget.get_title()
            else:
                element = widget_name
                value = Common.get_display_title(element)
            header_div.add(value)


            if widths and len(widths) > i:
                th.add_style("width", widths[i])
                width_set = True
                width = widths[i]

            else: # get width from definition 
                width = self.attributes[i].get("width")
                if width:
                     th.add_style("width", width)
                     width_set = True
            if width:
                th.add_style("min-width", width)
            else:
                th.add_style("overflow","hidden")


            widget.handle_th(th, i)



    def handle_group(self, table, i, sobject, group_name, group_value):

        tr, td = table.add_row_cell()
        tr.add_color("background", "background3", 5)
        tr.add_color("color", "color3")

        if group_value == '__NONE__':
            label = '---'
        else:
            label = Common.process_unicode_string(group_value)

        td.add(label)

        td.add_style("height: 25px")
        td.add_style("padding-left: %spx" % (i*15+5))
        td.add_style("border-style: solid")
        border_color = td.get_color("border")
        td.add_style("border-width: 0px 0px 0px 1px")
        td.add_style("border-color: %s" % border_color)
        td.add_style("font-weight: bold")





