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
    
from pyasm.admin.site import MainTabWdg


class BaseIndexWdg(Widget):

    def init(my):

        web = WebContainer.get_web()

        my.add(HeaderWdg('Tactic Admin Site'))

        undo_redo = HtmlElement.span()
        undo_redo.add_style("float", "right")
        undo_redo.add_style("margin-top", "-2px")
        undo_redo.add(SiteMenuWdg())

        my.add( undo_redo )

        tab = MainTabWdg()
        my.add(tab)




