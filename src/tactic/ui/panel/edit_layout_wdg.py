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
__all__ = ["EditLayoutWdg"]

from pyasm.common import Common, FormatValue, SPTDate
from pyasm.search import Search, SearchKey
from pyasm.web import DivWdg, Table, HtmlElement
from pyasm.widget import ThumbWdg, IconWdg, WidgetConfigView
from tactic.ui.container import SmartMenu
from pyasm.biz import Task, Pipeline, ProjectSetting

from .table_layout_wdg import TableLayoutWdg
from tactic.ui.widget import SingleButtonWdg

import os


class EditLayoutWdg(TableLayoutWdg):

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
            'description': "Comma delimited list of elements to view",
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
        "is_responsive": {
            'description': "Determines whether using a table layout or grid layout. 0 or None indicates table layout, 1 indicates grid layout with 1 item per row, similarily for 2, 3, ...",
            'type': 'TextWdg',
            'values': 'numbers',
            'order': 1,
            'category': 'Optional'
        },



    } 



    def get_display(self):

        styles = ""

        # NOTE: need to add this to fit as a table layout
        self.chunk_size = 10000
        self.edit_permission = True
        self.view_editable = True
        is_responsive = self.kwargs.get("is_responsive") or None


        search_key = self.kwargs.get("search_key")
        if search_key:
            sobject = Search.get_by_search_key(search_key)
            self.sobjects = [sobject]

        elif self.kwargs.get("do_search") != "false":
            self.handle_search()


        top = DivWdg()
        self.top = top
        self.set_as_panel(top)
        top.add_class("spt_sobject_top")

        inner = DivWdg()
        top.add(inner)
        if (not is_responsive) or (is_responsive == 0):
            inner.add_class("spt_table")
        inner.add_class("spt_layout")


        # set the sobjects to all the widgets then preprocess
        for widget in self.widgets:
            widget.set_sobjects(self.sobjects)
            widget.set_parent_wdg(self)
            # preprocess the elements
            widget.preprocess()



        inner.set_unique_id()
        inner.add_smart_style("spt_header", "vertical-align", "top")
        inner.add_smart_style("spt_header", "text-align", "left")
        inner.add_smart_style("spt_header", "width", "150px")
        inner.add_smart_style("spt_header", "padding", "5px")
        border = inner.get_color("table_border")

        inner.add_smart_style("spt_cell_edit", "background-repeat", "no-repeat")
        inner.add_smart_style("spt_cell_edit", "background-position", "bottom right")
        inner.add_smart_style("spt_cell_edit", "padding", "5px")
        inner.add_smart_style("spt_cell_edit", "min-width", "200px")


        for i, sobject in enumerate(self.sobjects):

            if (not is_responsive) or (is_responsive == 0):
                table = Table()
                table.add_color("color", "color")
                table.add_style("padding: 10px")
                #table.add_style("margin-bottom: 10px")
                table.add_style("width: 100%")
                inner.add(table)
                for j, widget in enumerate(self.widgets):

                    name = widget.get_name()
                    if name == 'preview':
                        continue

                    widget.set_current_index(i)
                    title = widget.get_title()

                    tr = table.add_row()
                    if isinstance(title, HtmlElement):
                        title.add_style("float: left")
                    th = table.add_header(title)
                    th.add_class("spt_header")
                    td = table.add_cell(widget.get_buffer_display())
                    td.add_class("spt_cell_edit")


                    if j % 2 == 0:
                        tr.add_color("background-color", "background", -1)
                    else:
                        tr.add_color("background-color", "background")


            elif is_responsive == "custom":
                grid_container = HtmlElement.ul()
                grid_container.add_class("spt_grid_container")
                grid_container.set_unique_id()

                inner.add(grid_container)
               
                for j, widget in enumerate(self.widgets):
                    attr = widget.get_name()
                    if not attr:
                        continue
                    
                    value = widget.get_buffer_display()
                    if not value:
                        continue
                    
                    title = widget.get_title()
                    title_div = DivWdg(title)
                    if not title:
                        title = DivWdg(attr)
                    
                    title_div.add_class("spt_widget_title")
                    
                    
                    value_div = DivWdg(value)
                   
                    value_div.add_class("spt_widget_value")
                    
                    grid_item = HtmlElement("a")
                    grid_item.add_class("spt_widget_container")
                   
                    grid_item_inner = DivWdg()
                    grid_item.add(grid_item_inner)
                    grid_item_inner.add_class("spt_widget_container_inner")

                    grid_item_inner.add(title_div)
                    grid_item_inner.add(value_div)
                    
                    grid_container.add(grid_item)
            
            else:
                grid_container = DivWdg()
                grid_container.add_class("spt_grid_container")
                grid_container.set_unique_id()

                inner.add(grid_container)
               
                num_columns = "auto "*int(is_responsive)
                styles += """
                
                    .spt_grid_container {
                        display: grid;
                        padding: 0px;
                        width: 100%%;
                        grid-template-columns: %s;
                    }
                    
                """ % num_columns
                
                styles += """
                    
                    .spt_grid_cell_attr {
                        font-weight: bold;
                        min-width: 100px;
                        padding-right: 5px;
                    }

                    .spt_grid_cell_value {
                        text-align: right;
                    }
                    
                    .spt_widget_title {
                        font-weight: bold;
                        padding-right: 10px;
                        min-width: 80px;
                    }
                    
                    .spt_widget_value {
                        padding-top: 6px;
                        text-align: right;
                        width: -webkit-fill-available;
                    }
                    
                    .spt_widget_container {
                        display: inline-flex;
                        min-width: 150px;
                        padding: 0px 10px;
                        font-size: 12px;
                    }

                """

                
                for j, widget in enumerate(self.widgets):
                    attr = widget.get_name()
                    if not attr:
                        continue
                    
                    value = widget.get_buffer_display()
                    if not value:
                        continue
                    
                    title = widget.get_title()
                    title_div = DivWdg(title)
                    if not title:
                        title = DivWdg(attr)
                    
                    title_div.add_class("spt_widget_title")
                    
                    
                    value_div = DivWdg(value)
                   
                    value_div.add_class("spt_widget_value")
                    
                    grid_item = DivWdg()
                    grid_item.add_class("spt_widget_container")
                    
                    grid_item.add(title_div)
                    grid_item.add(value_div)
                    
                    grid_container.add(grid_item)



        # extra stuff to make it work with ViewPanelWdg
        top.add_class("spt_table_top")
        class_name = Common.get_full_class_name(self)
        top.add_attr("spt_class_name", class_name)

        inner.add_class("spt_table_content")
        inner.add_attr("spt_search_type", self.kwargs.get('search_type'))
        inner.add_attr("spt_view", self.kwargs.get('view'))

        inner.add(HtmlElement.style(styles))

        if self.kwargs.get("is_refresh") == 'true':
            return inner
        else:
            return top



