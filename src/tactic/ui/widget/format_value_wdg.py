###########################################################
#
# Copyright (c) 2005-2008, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#


__all__ = ['FormatValueWdg']

import re

from pyasm.common import TimeCode, FormatValue
from pyasm.web import DivWdg
from pyasm.widget import HiddenWdg, IconWdg

from tactic.ui.common import BaseRefreshWdg


from dateutil import parser

class FormatValueWdg(BaseRefreshWdg):


    ARGS_KEYS = {
    }

    def get_display(self):

        top = DivWdg()

        format_str = self.kwargs.get('format')
        value = self.kwargs.get('value')


        format = FormatValue()
        display_value = format.get_format_value( value, format_str )

        widget = self.get_format_wdg(value, format_str, display_value)
        top.add(widget)

        return top


    def get_format_wdg(self, value, format, display_value):
        div = DivWdg()

        if format not in ['Checkbox'] and value == '':
            return div

        if format == 'Checkbox':

            div.add_style("width: 100%")
            div.add_class("spt_boolean_top")
            from pyasm.widget import CheckboxWdg
            checkbox = CheckboxWdg(self.get_name())
            checkbox.set_option("value", "true")
            if value:
                checkbox.set_checked()
            div.add(checkbox)
            checkbox.add_behavior( {
            'type': 'click_up',
            'propagate_evt': True,
            'cbjs_action': '''

            var cached_data = {};
            var value_wdg = bvr.src_el;
            var top_el = bvr.src_el.getParent(".spt_boolean_top");
            spt.dg_table.edit.widget = top_el;
            var key_code = spt.kbd.special_keys_map.ENTER;
            spt.dg_table.inline_edit_cell_cbk( value_wdg, cached_data );
            '''
            } )

        elif format == '-$1,234.00':
            if value < 0:
                div.add_style("color: red")
                div.add("(%s)" % display_value.replace("-", ""))
            else:
                div.add_style("color: black")
                div.add(display_value)

        else:
            div.add(display_value)

        return div

