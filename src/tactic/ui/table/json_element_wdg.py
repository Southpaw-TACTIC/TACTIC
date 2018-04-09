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

import json


class JsonElementWdg(SimpleTableElementWdg):

    ARGS_KEYS = {
    'height': {
        'description': 'Set maximum height of of the cell'
    }
    }

    def is_sortable(self):
        return False

    def is_editable(self):
        return True


    def get_display(self):

        top = self.top

        height = self.get_option('height')
        if not height:
            height = 300

        inner = DivWdg()
        top.add(inner)
        inner.add_style("overflow-y: auto")
        inner.add_style("overflow-x: hidden")
        inner.add_style("min-width: 300px")
        inner.add_style("max-height: %s" % height)
        inner.add_style("margin-right: -3px")
        inner.add_style("font-family: courier")
        inner.add_style("white-space: pre")
        
        sobject = self.get_current_sobject()

        data = sobject.get_json_value( self.get_name() )
        if data:
            value = json.dumps(data, indent=2, sort_keys=True)
            inner.add(value)


        """
        keys = data.keys()
        keys.sort()

        for key in keys:
            value = data.get(key)
            inner.add("%s = %s<br/>"% (key, value))

        """



        return top







