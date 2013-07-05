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

__all__ = ["UserTabWdg"]

from pyasm.search import Search, Sql
from pyasm.web import Widget
from pyasm.widget import TabWdg, TableWdg, SObjectGroupWdg

from pyasm.security import Login, LoginGroup, LoginInGroup, AccessRuleInGroup, AccessRule
from pyasm.admin import *


class UserTabWdg(Widget):

    def init(my):
        tab = TabWdg(css=TabWdg.SMALL)
        tab.set_tab_key("user_tab")
        my.handle_tab(tab)
        my.add(tab)



    def handle_tab(my, tab):
        tab.add( LoginWdg, "Users" )
        tab.add( LoginGroupWdg, "Groups" )
        tab.add( my.get_user_group_wdg, "Users -> Groups" )
        tab.add( my.get_group_user_wdg, "Groups -> Users" )
        tab.add( my.get_rules_wdg, "Access Rules" )
        tab.add( my.get_group_rule_wdg, "Groups -> Access Rules" )
        tab.add( my.get_rule_group_wdg, "Access Rules -> Groups" )
        tab.add( my.get_ticket_wdg, "Tickets" )


    def get_rules_wdg(my):
        widget = Widget()
        search = Search("sthpw/access_rule")
        sobjects = search.get_sobjects()
        table = TableWdg("sthpw/access_rule")
        table.set_sobjects(sobjects)
        widget.add(table)
        return widget

        


    def get_user_group_wdg(my):
        return SObjectGroupWdg(Login, LoginGroup, LoginInGroup)

    def get_group_user_wdg(my):
        return SObjectGroupWdg(LoginGroup, Login, LoginInGroup)

    def get_group_rule_wdg(my):
        return SObjectGroupWdg(LoginGroup, AccessRule, AccessRuleInGroup)

    def get_rule_group_wdg(my):
        return SObjectGroupWdg(AccessRule, LoginGroup, AccessRuleInGroup)




    def get_ticket_wdg(my):
        widget = Widget()

        div = DivWdg(css="filter_box")
        widget.add(div)

        from pyasm.prod.web import UserFilterWdg
        user_filter = UserFilterWdg()
        div.add(user_filter)

        search = Search("sthpw/ticket")
        user_filter.alter_search(search)

        search.add_where("(\"expiry\" > %s or \"expiry\" is NULL" % Sql.get_timestamp_now())

        table = TableWdg("sthpw/ticket")
        table.set_search(search)
        widget.add(table)
        return widget







from pyasm.search import SearchType, Search
from pyasm.web import DivWdg, HtmlElement, Widget
from pyasm.widget import SwapDisplayWdg, CheckboxWdg, WidgetConfig
from pyasm.prod.site import MainTabWdg

class DisplaySecurityWdg(Widget):

    def get_display(my):
        widget = Widget()

        search = Search("sthpw/project")
        projects = search.get_sobjects()

        div = DivWdg()
        for project in projects:
            project_code = project.get_code()
            project_type = project.get_value("type")

            project_div = DivWdg()
            swap = SwapDisplayWdg()
            swap.add_action_script("toggle_display('tab_block_%s')" % project_code)
            project_div.add(swap)

            checkbox = CheckboxWdg()
            project_div.add(checkbox)

            project_div.add(project_code)

            # for each project, get the tabs
            tab_div = DivWdg()
            tab_div.add_style("margin: 5px 30px 5px 30px")
            tab_div.set_id("tab_block_%s" % project_code)
            tab_div.add_style("display: none")

            inner_div = my.get_tab_wdg()
            tab_div.add(inner_div)

            project_div.add(tab_div)

            div.add(project_div)

            break

        return div
            


    def get_tab_wdg(my):

        widget = Widget()

        tab = MainTabWdg().get_widget("tab")
        tab_names = tab.get_tab_names()
        for tab_name in tab_names:
            tab_div = DivWdg()
            tab_div.set_id("%s_main_tab" % tab_name )

            swap = SwapDisplayWdg()
            tab_div.add(swap)

            checkbox = CheckboxWdg()
            tab_div.add(checkbox)

            tab_div.add(tab_name)

            element_div = DivWdg()
            element_div.add_style("margin: 5px 30px 5px 30px")
            inner_wdg = my.get_element_wdg()
            element_div.add(inner_wdg)
            tab_div.add(element_div)

            widget.add(tab_div)


        return widget



    def get_element_wdg(my):

        widget = Widget()

        # TODO: have to find the search type and view for each given tab,
        # if possible
        search_type = SearchType.get("prod/shot")
        config = WidgetConfig.get_by_search_type(search_type, "summary")
        element_names = config.get_element_names()

        for element_name in element_names:
            tab_div = DivWdg()
            tab_div.set_id("%s_main_tab" % element_name )

            swap = SwapDisplayWdg()
            tab_div.add(swap)

            checkbox = CheckboxWdg()
            tab_div.add(checkbox)

            tab_div.add(element_name)

            widget.add(tab_div)

        return widget




