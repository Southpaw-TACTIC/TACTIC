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

__all__ = ["MainTabWdg"]


from pyasm.web import *
from pyasm.widget import *
from pyasm.search import Search

from concept_tab_wdg import *
from asset_tab_wdg import *
from shot_tab_wdg import *
from overview_tab_wdg import *
from preprod_tab_wdg import *
from editorial_tab_wdg import *
from client_tab_wdg import *
from my_tactic_tab_wdg import *
from maya_tab_wdg import *
from tactic.ui.app import UndoLogWdg


class MainTabWdg(BaseTabWdg):
    '''This is the main tab for the Production application'''

    TAB_KEY = "main_tab"
    def init(self):
        self.setup_tab( self.TAB_KEY)



    def handle_tab(self, tab):
        tab.add(MyTacticTabWdg, _("My Tactic"))

        #from pyasm.alpha.sobject_navigator_wdg import SObjectNavigatorLayoutWdg
        #tab.add(SObjectNavigatorLayoutWdg, _("Browser"))

        tab.add(PreprodTabWdg, _("Preproduction"))
        #tab.add(ConceptTabWdg, _("Concept Pipeline"))
        tab.add(AssetTabWdg, _("Asset Pipeline"))
        tab.add(ShotTabWdg, _("Shot Pipeline"))
        tab.add(EditorialTabWdg, EditorialTabWdg.TAB_NAME)
        tab.add(OverviewTabWdg, _("Overview"))
        tab.add(ClientTabWdg, _("Client"))
        #tab.add(MayaTabWdg, _("Application"))
        tab.add(self.get_undo_wdg, _("Undo"))

        tab.add(AdminTabWdg, _("Admin"))



    def get_undo_wdg(self):
        widget = UndoLogWdg()
        return widget


    def get_episode_wdg(self):
        return Widget()





