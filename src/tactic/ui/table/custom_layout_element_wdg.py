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

__all___ = ['CustomLayoutElementWdg', 'LayoutElementWdg']

import re, time, types

from pyasm.web import DivWdg, Table, SpanWdg

from tactic.ui.common import BaseTableElementWdg, BaseRefreshWdg
from tactic.ui.panel import CustomLayoutWdg, FreeFormLayoutWdg


class CustomLayoutElementWdg(CustomLayoutWdg, BaseTableElementWdg):

    ARGS_KEYS = {
        'search_key': 'Search key of the sobject to be displayed',
        # or
        #'search_type': 'search type of the sobject to be displayed',
        #'code': 'code of the sobject to be displayed',
        #'id': 'id of the sobject to be displayed',

        'state': 'state surrounding the widget',
        'view': {
            'description': 'The view defined in the widget config/Custom Layout Editor that contains the custom html',
            'type': 'TextWdg',
            'order': 0,
            'category': 'Required'
        },
        'show_resize_scroll': {
            'description': 'Determines whether to show the scroll resize widget on elements',
            'type': 'SelectWdg',
            'values': 'false|true',
            'order': 2
        },
        'html': {
            'description': 'Explicitly define the html layout',
            'type': 'TextAreaWdg',
            'order': 0,
        },
        'include_mako': {
            'description': 'Flag to turn on Mako templating engine',
            'type': 'SelectWdg',
            'values': 'false|true',
        }
    }

    def init(self):
        super(CustomLayoutElementWdg, self).init()
        self.is_table_element = True



class LayoutElementWdg(BaseTableElementWdg):
    '''A very simple non-editable table element widget which will layout
    a set of defined elements either horizontally or vertically.'''

    ARGS_KEYS = {
        'show_title': {
            'description': 'Determines whether or not to show the titles in each cell.',
            'type': 'SelectWdg',
            'values': 'true|false'
        },
        'elements': {
            'description': 'List of element names',
        },
        'layout': {
            'description': 'List of element names',
            'type': 'SelectWdg',
            'values': 'horizontal|vertical'
        }
    }

    def get_default_background(self):
        return None
        #return self.get_color("background")


    def get_display(self):
        #element_names = ['asset_library', 'name', 'submit','code', 'num_tasks']
        element_names = self.kwargs.get("elements")
        if element_names:
            element_names = element_names.split("|")
        else:
            element_names = []

        if not element_names:
            return "<i>No elements defined</i>"


        show_title = self.kwargs.get('show_title')
        if show_title == 'false':
            show_title = False
        else:
            show_title = True

        layout = self.kwargs.get('layout')
        if not layout:
            layout = 'vertical'


        layout_wdg = self.get_layout_wdg()

        sobject = self.get_current_sobject()

        div = DivWdg()

        table = Table()
        div.add(table)


        widgets = []
        for element_name in element_names:
            element = layout_wdg.get_widget(element_name)

            if not element:
                config = layout_wdg.get_config()
                element = config.get_display_widget(element_name)
                element.set_sobject(sobject)
                element.preprocess()

            widgets.append(element)

        if layout == 'horizontal':
            if show_title:
                table.add_row()
                for widget in widgets:
                    element_name = widget.get_name()
                    td = table.add_cell("<i>%s</i>: " % element_name)
                    td.add_style("text-align: left")
                    td.add_style("vertical-align: top")
                    td.add_style("padding-right: 10px")

            table.add_row()
            for widget in widgets:
                if not widget:
                    td = table.add_cell("&nbsp;")
                else:
                    td = table.add_cell(widget)
                td.add_style("vertical-align: top")

        elif layout == 'vertical':
            for widget in widgets:
                element_name = widget.get_name()
                table.add_row()
                if show_title:
                    td = table.add_cell("<i>%s</i>: " % element_name)
                    td.add_style("text-align: right")
                    td.add_style("vertical-align: top")
                    td.add_style("padding-right: 10px")

                if not widget:
                    table.add_cell("&nbsp;")
                else:
                    table.add_cell(widget)


        return div





class FreeFormLayoutElementWdg(FreeFormLayoutWdg, BaseTableElementWdg):

    ARGS_KEYS = {
        'search_key': 'Search key of the sobject to be displayed',
        # or
        #'search_type': 'search type of the sobject to be displayed',
        #'code': 'code of the sobject to be displayed',
        #'id': 'id of the sobject to be displayed',

        'state': 'state surrounding the widget',
        'view': {
            'description': 'The view that contains the custom html',
            'type': 'TextWdg',
            'order': 0,
        },
    }





