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

__all__ = ["AdminTabWdg" ]

from pyasm.web import Widget, WebContainer
from pyasm.search import Search, SObjectFactory, SObject, SearchType
from pyasm.widget import TabWdg, SObjectGroupWdg, TableWdg, HelpItemWdg, BaseTabWdg
from pyasm.admin import LoginWdg, LoginGroupWdg
from pyasm.admin.creator import *
from pyasm.prod.queue import QueueWdg
from pyasm.prod.web import *
from pyasm.security import Login, LoginGroup, LoginInGroup
from pyasm.biz import Notification, GroupNotification, Timecard, Project

from custom_project_tab_wdg import CustomProjectTabWdg


class AdminTabWdg(BaseTabWdg):
    
    def __init__(self, database="sthpw", schema="public"):
        self.database = database
        self.schema = schema
        super(AdminTabWdg,self).__init__()
    

    def init(self):
        # FIXME: hack this in for now to handle "public"
        if self.schema == "public":
            self.namespace = self.database
        else:
            self.namespace = "%s/%s" % (self.database,self.schema)

        self.setup_tab("admin_tab", css=TabWdg.SMALL)
       

    def handle_tab(self, tab):
        # Hide this for now
        #tab.add( self.get_create_wdg, "Create")
        #tab.add( self.get_edit_wdg, "Edit" )
        tab.add( LoginWdg, _("Users") )
        tab.add( LoginGroupWdg, _("Groups") )
        tab.add( self.get_user_group_wdg, _("Users -> Groups")) 
        tab.add( self.get_group_user_wdg, _("Groups -> Users") )
        tab.add( QueueWdg, _("Queue") )
        tab.add( self.get_render_policy_wdg, _("Render Policy") )
        #tab.add( PipelineEditorWdg, _("Pipelines") )
        tab.add( self.get_pipeline_wdg, _("Pipelines") )
        tab.add( self.get_group_notification_wdg, _("Notification -> Group") )
        tab.add( self.get_notification_group_wdg, _("Group -> Notification" ) )


        tab.add( self.get_milestone_wdg, _("Project Milestones") )
        tab.add( self.get_project_settings_wdg, _("Project Settings") )
        
        tab.add( CustomProjectTabWdg, _("Customize Project") )


        from setup_tab_wdg import SetupTabWdg
        tab.add( SetupTabWdg, _("Setup Wizard")) 


        tab.add(self.get_import_wdg, _("Import Data") )
        WebContainer.add_js('wz_dragdrop.js')



    def get_pipeline_wdg(self):
        search = Search("sthpw/pipeline")
        widget = Widget()
        widget.set_search(search)
        table = TableWdg("sthpw/pipeline", "manage")
        widget.add(table)
        return widget

    def get_user_group_wdg(self):
        return SObjectGroupWdg(Login, LoginGroup, LoginInGroup)

    def get_group_user_wdg(self):
        return SObjectGroupWdg(LoginGroup, Login, LoginInGroup)


    def get_create_wdg(self):
        asset = SObjectCreatorWdg(self.database, self.schema)
        return asset


    def get_edit_wdg(self):
        edit = SObjectEditorWdg(self.database, self.schema)
        return edit


    def get_group_notification_wdg(self):
        # TODO: should filter out for this project only
        return SObjectGroupWdg(Notification, LoginGroup, GroupNotification)

    def get_notification_group_wdg(self):
        # TODO: should filter out for this project only
        return SObjectGroupWdg(LoginGroup, Notification, GroupNotification)


    def get_milestone_wdg(self):
        widget = Widget()

        search = Search("sthpw/milestone")
        
        table = TableWdg("sthpw/milestone")
        table.set_search(search)

        widget.add(table)
        return widget



    def get_project_settings_wdg(self):
        widget = Widget()

        search = Search("prod/prod_setting")
        
        table = TableWdg("prod/prod_setting")
        table.set_search(search)

        widget.add(table)
        return widget



    def get_render_policy_wdg(self):
        widget = Widget()
        #div = DivWdg(css="filter_box")
        #widget.add(div)

        table = TableWdg("prod/render_policy")
        search = Search("prod/render_policy")
        sobjects = search.get_sobjects()
        table.set_sobjects(sobjects)
        widget.add(table)
    
        return widget

    def get_import_wdg(self):
        return CsvImportWdg()



