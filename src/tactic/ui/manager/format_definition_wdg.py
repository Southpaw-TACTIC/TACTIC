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

__all__ = ['FormatDefinitionEditWdg']

import os

import tacticenv

from pyasm.search import Search, SearchType
from pyasm.web import DivWdg, SpanWdg, Table, WebContainer, HtmlElement
from pyasm.widget import SelectWdg

from tactic.ui.common import BaseRefreshWdg


class FormatDefinitionEditWdg(BaseRefreshWdg):
    '''Used in ElementDefinitionWdg to draw the options for simple display'''

    def get_args_keys(self):
        return {
        'prefix': 'prefix of the options',
        'name': 'name given to the widget',
        'option': 'option data provided by args_keys',
        'display_options': 'options provided by the config',
        }

    def get_display(self):
        top = DivWdg()
        top.add_class("spt_element_top")

        prefix = self.kwargs.get('prefix')
        # this should be name to be consistent with the BaseInputWdg interface
        widget_name = self.kwargs.get('name')
        if not widget_name:
            widget_name = 'data_type'

        display_options = self.kwargs.get('display_options')
        if not display_options:
            display_options = {}

        option = self.kwargs.get('option')
        if not option:
            option = {}



        # get the current value
        option_name = option.get('name')
        widget_type = display_options.get(option_name)

        select = SelectWdg(widget_name)
        top.add(select)
        select.add_style("width: 30%")
        select.add_style("display: inline-block")

        default = option.get('default')
        if default:
            select.set_value(default)
        else:
            select.add_empty_option('-- Select --')


        values = option.get('values')
        if not values:
            values = 'integer|float|percent|currency|date|time|scientific|boolean|text|timecode',
        select.set_option('values', values)


        if widget_type:
            select.set_value(widget_type)

        select.add_behavior( {
        'type': 'change',
        'cbjs_action': '''
        var value = bvr.src_el.value;
        var top = bvr.src_el.getParent(".spt_element_top");
        var selects = top.getElements(".spt_format");
        for (var i = 0; i < selects.length; i++) {
            var type = selects[i].getAttribute("spt_type");
            if (value == type) {
                selects[i].setStyle("display", "inline-block");
                selects[i].removeAttribute("disabled");
            }
            else {
                selects[i].setStyle("display", "none");
                selects[i].setAttribute("disabled", "disabled");
                selects[i].value = '';

            }
        }
        '''
        } )


        selects_values = {
            '':             [],
            'integer':      ['-1234',
                             '-1,234'],

            'float':        ['-1234.12',
                             '-1,234.12'],

            'percent':      ['-13%', 
                             '-12.95%'],

            'currency':     ['-$1,234',
                             '-$1,234.00',
                             '-$1,234.--',
                             '-1,234.00 CAD',
                             '($1,234.00)',
                             ],

            'date':         ['31/12/99',
                             'December 31, 1999',
                             '31/12/1999',
                             'Dec 31, 99', 
                             'Dec 31, 1999',
                             '31 Dec, 1999',
                             '31 December 1999',
                             'Fri, Dec 31, 99',
                             'Fri 31/Dec 99',
                             'Fri, December 31, 1999',
                             'Friday, December 31, 1999',
                             '12-31',
                             '99-12-31',
                             '1999-12-31',
                             '12-31-1999',
                             '12/99',
                             '31/Dec',
                             'December',
                             '52',
                             'DATE',
                             'DATETIME'],

            'time':         ['13:37',
                             '13:37:46',
                             '01:37 PM',
                             '01:37:46 PM',
                             '31/12/99 13:37',
                             '31/12/99 13:37:46',
                             'DATETIME',
                             'TIME_AGO'],

            'scientific':   ['-1.23E+03',
                             '-1.234E+03'],

            'boolean':      ['true|false', 'True|False', 'Checkbox'],

            'timecode':      ['MM:SS.FF',
                              'MM:SS:FF',
                              'MM:SS',
                              'HH:MM:SS.FF',
                              'HH:MM:SS:FF',
                              'HH:MM:SS'],
        }

        for key, select_values in selects_values.items():
            # skip the empty key
            if not key:
                continue

            # options for each
            if prefix:
                select = SelectWdg("%s|format" % prefix, for_display=False)
            else:
                select = SelectWdg("format", for_display=False)

            select.add_class("spt_format")
           
            select.add_attr("spt_type", key)

            value = display_options.get('format')
            if key == '':
                select.add_style("display", "none")
            elif widget_type == key:
                select.set_value(value)
            else:
                select.add_style("display", "none")
                select.add_attr("disabled", "disabled")

            select.add_style("width: 30%")

            select.set_option("values", select_values)
            select.add_empty_option("-- Format --")
            top.add(select)
  
            if key == 'timecode':
                if prefix:
                    select = SelectWdg("%s|fps" % prefix, for_display=False)
                else:
                    select = SelectWdg("fps", for_display=False)
                select.add_class("spt_format")
                select.add_attr("spt_type", key)

                value = display_options.get('fps')
                if widget_type == key:
                    select.set_value(value)
                else:
                    select.add_style("display", "none")
                select.set_option("values", "12|24|25|30|60")
                select.set_option("labels", "12 fps|24 fps|25 fps|30 fps|60 fps")
                select.add_empty_option("-- fps --")
                top.add(select)
                select.add_style("width: 30%")
               

        return top





