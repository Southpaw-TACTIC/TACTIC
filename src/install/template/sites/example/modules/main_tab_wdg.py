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

    def init(self):
        tab = TabWdg()
        tab.set_tab_key("main_tab")
        self.handle_tab(tab)
        self.add(tab)




    def handle_tab(self, tab):
        tab.add(self.get_test_wdg, "Test")
        tab.add(self.get_test2_wdg, "Test2")



    def get_test_wdg(self):
        div = DivWdg("Hello World")
        return div


    def get_test2_wdg(self):
        div = DivWdg("Hello World2")
        return div





