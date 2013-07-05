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

__all__ = ["DebugLogWdg"]

from pyasm.search import Search
from pyasm.web import Widget, DivWdg, SpanWdg
from pyasm.widget import TableWdg
from pyasm.prod.web import UserFilterWdg

class DebugLogWdg(Widget):

    def get_display(my):
        widget = Widget()

        div = DivWdg(css="filter_box")
        user_filter = UserFilterWdg()
        div.add(user_filter)
        widget.add(div)
        
        search = Search("sthpw/debug_log")
        search.add_order_by("timestamp desc")
        user_filter.alter_search(search)

        table = TableWdg("sthpw/debug_log")
        table.set_search(search)
        table.do_search()
        widget.add(table)
        return widget




