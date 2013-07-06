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

from pyasm.web import Widget, WebContainer, HtmlElement
from pyasm.widget import SiteMenuWdg, HeaderWdg
from pyasm.prod.site import MainTabWdg





class BaseIndexWdg(Widget):

    def init(my):

        web = WebContainer.get_web()

        my.add(HeaderWdg())

        menu = SiteMenuWdg()
        menu.add_style("float: right")
        menu.add_style("margin-top: -2px")
        my.add(menu)

        from pyasm.web import get_main_tab_wdg
        tab = get_main_tab_wdg()
        my.add(tab)



