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

__all__ = ["NotificationTabWdg", "RecipientElementWdg"]

from pyasm.biz import Project
from pyasm.web import Widget, DivWdg, SpanWdg
from pyasm.widget import TabWdg, TableWdg, SObjectGroupWdg, SearchLimitWdg, TextWdg, FilterSelectWdg
from pyasm.search import Search

from pyasm.security import Login, LoginGroup, LoginInGroup
from pyasm.admin import *
from pyasm.biz import Notification, GroupNotification

class NotificationTabWdg(Widget):

    def init(my):
        tab = TabWdg(css=TabWdg.SMALL)
        tab.set_tab_key("notification_tab")
        my.handle_tab(tab)
        my.add(tab)

    def handle_tab(my, tab):
        tab.add( my.get_notification_wdg, "Notification Rules" )
        tab.add( my.get_group_notification_wdg, "Notification -> Group" )
        tab.add( my.get_notification_group_wdg, "Group -> Notification" )
        tab.add( my.get_notification_log_wdg, "Notification Log" )


    def get_notification_wdg(my):
        table = TableWdg("sthpw/notification")
        search = Search("sthpw/notification")
        table.set_search(search)
        return table


    def get_group_notification_wdg(my):
        return SObjectGroupWdg(Notification, LoginGroup, GroupNotification)


    def get_notification_group_wdg(my):
        return SObjectGroupWdg(LoginGroup, Notification, GroupNotification)

    def get_notification_log_wdg(my):

        widget = Widget()

        nav = DivWdg(css="filter_box")
        widget.add(nav)

        search_limit = SearchLimitWdg()
        nav.add(search_limit)

        project_wdg = FilterSelectWdg("project_code")
        project_wdg.set_option("query", "sthpw/project|code|title")
        nav.add("Project: ")
        nav.add(project_wdg)
        project_code = project_wdg.get_value()

        #text = TextWdg('notification_search')
        #span = SpanWdg(css="med")
        #span.add("Search: ")
        #span.add(text)
        #nav.add(span)
        #text_value = text.get_value()


        table = TableWdg("sthpw/notification_log")
        search = Search("sthpw/notification_log")
        search_limit.alter_search(search)

        search.add_filter("project_code", project_code)


        table.set_search(search)
        widget.add(table)

        return widget


from pyasm.web import Table
from pyasm.widget import BaseTableElementWdg
class RecipientElementWdg(BaseTableElementWdg):

    def get_logins(my):
        sobject = my.get_current_sobject()
        id = sobject.get_id()

        search = Search("sthpw/notification_login")
        search.add_filter('notification_log_id', id)
        notification_logins = search.get_sobjects()
        return notification_logins
    
    def get_display(my):
        notification_logins = my.get_logins()

        table = Table()
        table.add_color("color", "color")

        for notification_login in notification_logins:
            type = notification_login.get_value("type")
            user = notification_login.get_value("login")
            table.add_row()
            table.add_cell(type)
            table.add_cell(user)

        return table

    def get_text_value(my):
        name_list = []
        notification_logins = my.get_logins()
        for notification_login in notification_logins:
            type = notification_login.get_value("type")
            user = notification_login.get_value("login")
            name_list.append('%s: %s' %(type, user))

        return '\n'.join(name_list)


