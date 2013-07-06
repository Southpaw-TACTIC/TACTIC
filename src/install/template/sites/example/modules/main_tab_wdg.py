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

from pyasm.web import Widget, DivWdg, WebContainer
from pyasm.widget import TabWdg


class MainTabWdg(Widget):

    def init(my):
        tab = TabWdg()
        tab.set_tab_key("main_tab")
        my.handle_tab(tab)
        my.add(tab)




    def handle_tab(my, tab):
        tab.add(my.get_test_wdg, "Test")
        tab.add(my.get_test2_wdg, "Test2")



    def get_test_wdg(my):
        div = DivWdg("Hello World")
        return div


    def get_test2_wdg(my):
        div = DivWdg("Hello World2")
        return div





