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

__all__ = ["BaseTabWdg"]

from pyasm.common import Container
from pyasm.web import Widget
from pyasm.widget import TabExtendWdg

from tab_wdg import TabWdg


class BaseTabWdg(Widget):

    def init(my):
        tab_path = Container.get("tab_path")
        if not tab_path:
            tab_path = my.name
            Container.put("tab_path", tab_path)

        if len(tab_path.split("/")) > 0:
            my.setup_tab(tab_path, css=TabWdg.SMALL)
        else:
            my.setup_tab(tab_path)

    def setup_tab(my, tab_key, css=TabWdg.REG, tab=None):
        if not tab:
            tab = TabWdg(tab_key=tab_key, css=css)
        my.handle_tab(tab)

        # Ability to dynamically add tabs from the database.
        extend_tab = TabExtendWdg()
        extend_tab.set_tab(tab)
        extend_tab.get_display()
        my.add(tab, "tab")


    def handle_tab(my, tab):
        pass

