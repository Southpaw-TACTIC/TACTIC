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

from pyasm.common import Common
from pyasm.search import Search, SearchKey
from pyasm.web import DivWdg, Table, HtmlElement
from pyasm.widget import ThumbWdg, IconWdg
from tactic.ui.container import SmartMenu

from table_layout_wdg import TableLayoutWdg
from tactic.ui.widget import SingleButtonWdg

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


        # NOTE: need to add this to fit as a table layout
        self.chunk_size = 10000
        self.edit_permission = True
        self.view_editable = True


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
        inner.add_color("background", "background")
        inner.add_color("color", "color")
        # NOTE: this is not the table and is called this for backwards
        # compatibility
        inner.add_class("spt_table")
        inner.add_class("spt_layout")


        # set the sobjects to all the widgets then preprocess
        for widget in self.widgets:
            widget.set_sobjects(self.sobjects)
            widget.set_parent_wdg(self)
            # preprocess the elements
            widget.preprocess()



        #is_refresh = self.kwargs.get("is_refresh")
        #if self.kwargs.get("show_shelf") not in ['false', False]:
        #    action = self.get_action_wdg()
        #    inner.add(action)


        # get all the edit widgets
        """
        if self.view_editable and self.edit_permission:
            edit_wdgs = self.get_edit_wdgs()
            edit_div = DivWdg()
            edit_div.add_class("spt_edit_top")
            edit_div.add_style("display: none")
            inner.add(edit_div)
            for name, edit_wdg in edit_wdgs.items():
                edit_div.add(edit_wdg)
        """

        inner.set_unique_id()
        inner.add_smart_style("spt_header", "vertical-align", "top")
        inner.add_smart_style("spt_header", "text-align", "left")
        inner.add_smart_style("spt_header", "width", "150px")
        inner.add_smart_style("spt_header", "padding", "5px")
        border = inner.get_color("table_border")
        #inner.add_smart_style("spt_header", "border", "solid 1px %s" % border)

        inner.add_smart_style("spt_cell_edit", "background-repeat", "no-repeat")
        inner.add_smart_style("spt_cell_edit", "background-position", "bottom right")
        inner.add_smart_style("spt_cell_edit", "padding", "5px")
        inner.add_smart_style("spt_cell_edit", "min-width", "200px")

        for i, sobject in enumerate(self.sobjects):

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


                # indicator that a cell is editable
                #td.add_event( "onmouseover", "$(this).setStyle('background-image', " \
                #                  "'url(/context/icons/silk/page_white_edit.png)')" )
                #td.add_event( "onmouseout",  "$(this).setStyle('background-image', '')")



        # extra stuff to make it work with ViewPanelWdg
        top.add_class("spt_table_top");
        class_name = Common.get_full_class_name(self)
        top.add_attr("spt_class_name", class_name)

        inner.add_class("spt_table_content");
        inner.add_attr("spt_search_type", self.kwargs.get('search_type'))
        inner.add_attr("spt_view", self.kwargs.get('view'))

        if self.kwargs.get("is_refresh") == 'true':
            return inner
        else:
            return top



