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

__all__ = ['MainTabWdg']

from pyasm.web import *
from pyasm.search import SearchType
from pyasm.widget import *
from pyasm.admin import *

from preprod_tab_wdg import *
from asset_tab_wdg import *
from shot_tab_wdg import *
from overview_tab_wdg import *
from admin_tab_wdg import *
from pyasm.prod.site import EditorialTabWdg, MyTacticTabWdg



class MainTabWdg(BaseTabWdg):
    TAB_KEY = "main_tab"
    def init(my):
        #tab = TabWdg()
        #tab.set_tab_key("main_tab")
        #my.handle_tab(tab)
        my.setup_tab( my.TAB_KEY)
        my.add(ProgressWdg())
        #my.add(tab, "tab")
        




    def handle_tab(my, tab):
        tab.add(MyTacticTabWdg, _("My Tactic"))
        tab.add(PreprodTabWdg, _("Preproduction"))
        tab.add(AssetTabWdg, _("Asset Pipeline"))
        tab.add(ShotTabWdg, _("Scene Pipeline"))
        tab.add(OverviewTabWdg, _("Overview"))

        tab.add(EditorialTabWdg, _("Editorial"))

        tab.add(my.get_admin_wdg, _("Admin"))
        tab.add(my.get_undo_wdg, _("Undo"))
        
       


    def get_undo_wdg(my):
        widget = UndoLogWdg()
        return widget


    def get_episode_wdg(my):
        return Widget()


    def get_shot_wdg(my):
        widget = Widget()

        div = DivWdg()
        div.add_style("text-align: center")
        widget.add(div)
        
        search = Search("prod/shot")
        widget.set_search(search)

        table = TableWdg("prod/shot")
        widget.add(table)

        return widget



    def get_admin_wdg(my):
        database = WebContainer.get_web().get_context_name()
        admin = AdminTabWdg(database, "public")
        return admin






