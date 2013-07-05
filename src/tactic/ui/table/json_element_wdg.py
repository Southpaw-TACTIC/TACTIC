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


__all__ = ['JsonElementWdg']

from pyasm.common import TacticException, jsonloads

from tactic.ui.common import SimpleTableElementWdg
from pyasm.web import DivWdg


class JsonElementWdg(SimpleTableElementWdg):

    ARGS_KEYS = {
    'height': {
        'description': 'Set maximum height of of the cell'
    }
    }

    def is_sortable(my):
        return False

    def is_editable(my):
        return False


    def get_display(my):

        top = my.top

        height = my.get_option('height')
        if not height:
            height = 300

        inner = DivWdg()
        top.add(inner)
        inner.add_style("overflow-y: auto")
        inner.add_style("overflow-x: hidden")
        inner.add_style("min-width: 300px")
        inner.add_style("max-width: 300px")
        inner.add_style("max-height: %s" % height)
        inner.add_style("margin-right: -3px")
        
        sobject = my.get_current_sobject()

        data = sobject.get_json_value( my.get_name() )
        if not data:
            data = {}

        keys = data.keys()
        keys.sort()

        for key in keys:
            value = data.get(key)
            inner.add("%s = %s<br/>"% (key, value))



        return top


