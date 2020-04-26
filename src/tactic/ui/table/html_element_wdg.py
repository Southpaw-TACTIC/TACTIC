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


__all__ = ['HtmlElementWdg']

from pyasm.common import TacticException, jsonloads

from tactic.ui.common import SimpleTableElementWdg
from pyasm.web import DivWdg


class HtmlElementWdg(SimpleTableElementWdg):

    ARGS_KEYS = {
    'column': {
        'description': 'The column to look at'
    },
    'height': {
        'description': 'Set maximum height of of the cell'
    }
    }

    def is_sortable(self):
        return False

    def is_editable(self):
        return False


    def get_display(self):

        top = self.top

        height = self.get_option('height')
        if not height:
            height = 300

        inner = DivWdg()
        top.add(inner)
        inner.add_style("overflow-y: auto")
        inner.add_style("overflow-x: hidden")
        inner.add_style("width: 100%")
        inner.add_style("max-height: %s" % height)
        inner.add_style("margin-right: -3px")
        
        sobject = self.get_current_sobject()

        column = self.get_option("column")
        if not column:
            column = self.get_name()

        if sobject:
            html = sobject.get_json_value( column ) or ""
        else:
            html = ""


        inner.add(html)

        return top


