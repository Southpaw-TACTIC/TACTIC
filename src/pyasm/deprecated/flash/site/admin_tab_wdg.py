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

__all__ = ['AdminTabWdg', 'FlashCustomizeTabWdg']

from pyasm.web import *
from pyasm.widget import TabWdg, TableWdg, SObjectGroupWdg
from pyasm.admin import *
from pyasm.admin.creator import *
from pyasm.command import *
from pyasm.prod.queue import QueueWdg
from pyasm.search import Search
from pyasm.security import Login, LoginGroup, LoginInGroup
from pyasm.biz import Notification, GroupNotification, Trigger, \
    CommandSObj, TriggerInCommand
from pyasm.prod.site import WorkHourSummaryWdg
from pyasm.admin.widget import CustomizeTabWdg


class AdminTabWdg(Widget):
    def __init__(my, database, schema):
        my.database = database
        my.schema = schema
        super(AdminTabWdg,my).__init__()


    def init(my):

        # FIXME: hack this in for now to handle "public"
        if my.schema == "public":
            my.namespace = my.database
        else:
            my.namespace = "%s/%s" % (my.database,my.schema)

        tab = TabWdg(css=TabWdg.SMALL)
        tab.set_tab_key("admin_tab")

        tab_value = tab.get_tab_value()

        asset = None
        edit = None
        edit2 = None
        retire = None
        security = None

        if not tab_value or tab_value == "Create Flash Asset":
            asset = SObjectCreatorWdg(my.database, my.schema)
        #elif tab_value == "Edit":
        #    edit = 
        #elif tab_value == "Edit2":
        #    edit2 = AssetEditorWdg(my.database, my.schema)

        
        
        tab.add( asset, "Create Flash Asset")
        tab.add( my.get_widget_config_wdg, "Widget Config" )
        #tab.add( edit2, "Edit2" )
        tab.add( my.get_group_notification_wdg, "Notification -> Group" )
        tab.add( my.get_notification_group_wdg, "Group -> Notification" )
        tab.add( PipelineEditorWdg, "Pipelines")
        tab.add( QueueWdg, "Queue" )
        tab.add( TemplateWdg, "Templates" )
        tab.add( my.get_naming_wdg(), "Naming" )
        tab.add( my.get_project_settings_wdg, "Project Settings" )
        tab.add( FlashCustomizeTabWdg, "Customize Tabs")
        my.add(tab, 'tab')
        WebContainer.add_js('wz_dragdrop.js')
        
    def get_time_card_wdg(my):
        table = TableWdg('sthpw/timecard')
        search = Search('sthpw/timecard')
        table.set_search(search)
        return table
    
    def get_widget_config_wdg(my):
        return SObjectEditorWdg(my.database, my.schema)
   
    def get_user_role_wdg(my):
        return SObjectGroupWdg(Login, LoginGroup, LoginInGroup)
    
  
    def get_notification_group_wdg(my):
        return SObjectGroupWdg(Notification, LoginGroup, GroupNotification)

    def get_group_notification_wdg(my):
        return SObjectGroupWdg(LoginGroup, Notification, GroupNotification)

    def get_trigger_in_command_wdg(my):
        return SObjectGroupWdg(Trigger, CommandSObj, TriggerInCommand)

    def get_project_settings_wdg(my):
        widget = Widget()

        search = Search("prod/prod_setting")
        
        table = TableWdg("prod/prod_setting")
        table.set_search(search)

        widget.add(table)
        return widget

    def get_naming_wdg(my):
        widget = Widget()
  
        table = TableWdg("prod/naming")
        search = Search("prod/naming")
        sobjects = search.get_sobjects()
        table.set_sobjects(sobjects)
        widget.add(table)
    
        return widget

class FlashCustomizeTabWdg(CustomizeTabWdg):

    def handle_tabs(my, div):
        from main_tab_wdg import MainTabWdg
        tab_wdg = MainTabWdg()
        div.add( my.get_tab_wdg(tab_wdg, "Main", is_main=True) )

        tabs = tab_wdg.get_widget("tab")
        main_tab_names = tabs.get_tab_names()

        for tab_name in main_tab_names:
            widget = tabs.wdg_dict.get(tab_name)
            widget = tabs.init_widget(widget)
            div.add( my.get_tab_wdg(widget, tab_name))

      
