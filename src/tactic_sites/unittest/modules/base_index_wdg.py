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

__all__ = ["BaseIndexWdg"]

from pyasm.web import *
from pyasm.widget import *
from pyasm.prod.site import MainTabWdg



class BaseIndexWdg(Widget):

    def init(my):
        my.add(HeaderWdg())

        menu = SiteMenuWdg()
        menu.add_style("float: right")
        menu.add_style("padding: 4px 0 6px 0")
        menu.add_style("margin-top: -8px")
        my.add(menu)

        from pyasm.web import get_main_tab_wdg
        tab = get_main_tab_wdg()
        my.add(tab)




