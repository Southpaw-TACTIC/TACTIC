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

__all__ = ["MainTabWdg", "RenewLicenseCbk"]


import os, shutil
from pyasm.command import FileUpload
from pyasm.search import Search, FileUndo
from pyasm.web import Widget, DivWdg, SpanWdg, HtmlElement, WebContainer, Callback
from pyasm.widget import TabWdg, TableWdg, FilterSelectWdg, FilterCheckboxWdg, SearchLimitWdg, SimpleUploadWdg, HiddenWdg, HelpItemWdg
from pyasm.prod.web import DateFilterWdg, ProdIconSubmitWdg
from pyasm.admin import UndoLogWdg
from pyasm.admin.widget import DebugLogWdg

from pyasm.biz import PrefList
from pyasm.admin.creator import *
from pyasm.common import Environment, TacticException
from user_tab_wdg import *
from trigger_tab_wdg import *
from notification_tab_wdg import *


class MainTabWdg(Widget):

    def init(my):
        tab = TabWdg()
        tab.set_tab_key("admin_main_tab")
        my.handle_tab(tab)
        my.add(tab)

        my.add(WebContainer.add_js('wz_dragdrop.js'))



    def handle_tab(my, tab):
        tab.add(my.get_project_wdg, _("Projects") )
        tab.add(my.get_project_type_wdg, _("Project Types") )
        tab.add( my.get_schema_wdg, _("Schema" ) )
        tab.add( UserTabWdg, _("Users") )
        tab.add( my.get_snapshot_type_wdg(), _("Snapshot Types" ) )
        tab.add( my.get_pipeline_wdg, _("Pipelines" ) )
        tab.add( PipelineEditorWdg, _("Pipelines (old)" ) )
        tab.add( TriggerTabWdg, _("Triggers") )
        tab.add( NotificationTabWdg, _("Notifications") )
        # just reactivate sobjects in Asset List or Shot List tab
        tab.add( my.get_exception_wdg, _("Exception Log") )
        tab.add( DebugLogWdg, _("Debug Log") )
        tab.add( my.get_remote_repo_wdg, _("Remote Repo") )
        tab.add( my.get_translation_wdg, _("Translations") )
        tab.add( my.get_pref_wdg, _("Preferences") )
        tab.add(my.get_undo_wdg, _("Undo Browser") )



    def get_pref_wdg(my):
        widget = Widget()

        search = Search("sthpw/pref_list")
        sobjects = search.get_sobjects()
        table = TableWdg("sthpw/pref_list")
        table.set_sobjects(sobjects)
        widget.add(table)

        return widget


    def get_translation_wdg(my):
        widget = Widget()

        div = DivWdg(css="filter_box")

       
    
        select = FilterSelectWdg("language", label='%s: ' %_("Language"), css='med')
        pref_val = PrefList.get_value_by_key("language") 
        if not pref_val:
            pref_val = "ja|fr|zh-CN"
        select.set_option("values", pref_val)
        #select.set_option("labels", "Japanese|French|Chinese(PRC)")
        div.add(select)

        language = select.get_value()

        span = SpanWdg(css="med")
        span.add(_("Show only untranslated"))
        span.add(":")
        checkbox = FilterCheckboxWdg("untranslated")
        span.add(checkbox)
        div.add(span)


        untranslated = checkbox.get_value()

        '''
        search_limit = SearchLimitWdg()
        search_limit.set_limit(50)
        div.add(search_limit)
        '''

        widget.add(div)

        search = Search("sthpw/translation")
        search.add_filter("language", language)
        #search.add_order_by("timestamp desc")


        if untranslated == "on":
            search.add_where("(msgstr is NULL or msgstr = '')")


        #search_limit.alter_search(search)
        #sobjects = search.get_sobjects()
        table = TableWdg("sthpw/translation")
        table.set_search(search)
        widget.add(table)

        return widget





    def get_undo_wdg(my):
        widget = UndoLogWdg()
        widget.set_admin()
        return widget


    def get_exception_wdg(my):
        widget = Widget()

        div = DivWdg(css="filter_box")
        span = SpanWdg(css="med")
        span.add(_("User")+": ")
        user_select = FilterSelectWdg("user")
        user_select.set_option("query", "sthpw/login|login|login")
        user_select.add_empty_option()
        user_select.add_event("onselect", "document.form.submit()")
        span.add(user_select)
        div.add(span)
        widget.add(div)

        user = user_select.get_value()
        date_filter = DateFilterWdg()
        div.add(date_filter)
        
        search = Search("sthpw/exception_log")
        search.add_order_by("timestamp desc")
        if user:
            search.add_filter("login", user)

        date_filter.alter_search(search)
        table = TableWdg("sthpw/exception_log")
        
        table.set_search(search)
        widget.add(table)
        return widget




    def get_project_wdg(my):

        widget = Widget()

        event = WebContainer.get_event_container()
        event.add_refresh_listener(event.DATA_INSERT)

        widget.add(HelpItemWdg('Projects tab', 'In the Projects tab, you can renew your TACTIC license, insert new projects, compare database schema, or edit current project settings.'))
        widget.add(SpanWdg("Renew your license here:"))
        widget.add(HtmlElement.br())

        file = SimpleUploadWdg(RenewLicenseCbk.INPUT_NAME)
        widget.add(file)
        button = ProdIconSubmitWdg(RenewLicenseCbk.BUTTON_NAME)
        button.add_event('onclick', "if (!confirm('License to be renewed. Continue?')) return")
        WebContainer.register_cmd('pyasm.admin.site.RenewLicenseCbk')
        widget.add(button)
        hidden = HiddenWdg('Renewal')
        widget.add(hidden)
        if hidden.get_value() == 'Success':
            span = SpanWdg("License renewal completed!!", css='large')
            span.add_style('font-weight: bolder')
            widget.add(span)
        widget.add(HtmlElement.br(2))
        search = Search("sthpw/project")
        # don't show the sthpw and admin as projects
        search.add_where("code not in ('admin')")
        widget.set_search(search)
        table = TableWdg("sthpw/project")
        widget.add(table)
        return widget


    def get_project_type_wdg(my):
        search = Search("sthpw/project_type")
        widget = Widget()
        widget.set_search(search)
        table = TableWdg("sthpw/project_type")
        widget.add(table)
        return widget

    def get_schema_wdg(my):
        search = Search("sthpw/schema")
        widget = Widget()
        table = TableWdg("sthpw/schema", "manage")
        table.set_search(search)
        widget.add(table)
        return widget


    def get_pipeline_wdg(my):

        widget = Widget()
        filter_div = DivWdg(css='filter_box')
        from pyasm.prod.web import ProjectFilterWdg
        from pyasm.widget import ProdIconSubmitWdg
        project_filter = ProjectFilterWdg()
        filter_div.add(project_filter)

        filter_div.add( ProdIconSubmitWdg("Search") )
        widget.add(filter_div)

 

        search = Search("sthpw/pipeline")
        project_filter.alter_search(search)
        widget.set_search(search)
        table = TableWdg("sthpw/pipeline", "manage")
        widget.add(table)
        return widget


    def get_snapshot_type_wdg(my):

        widget = Widget()

        filter_div = DivWdg(css='filter_box')
        from pyasm.prod.web import ProjectFilterWdg
        from pyasm.widget import ProdIconSubmitWdg
        project_filter = ProjectFilterWdg()
        filter_div.add(project_filter)

        filter_div.add( ProdIconSubmitWdg("Search") )
        widget.add(filter_div)

        search = Search("sthpw/snapshot_type")
        project_filter.alter_search(search)


        widget.set_search(search)
        table = TableWdg("sthpw/snapshot_type")
        widget.add(table)
        return widget




    def get_remote_repo_wdg(my):
        widget = Widget()
        widget.add(HelpItemWdg('Remote Repo Tab', '/doc/admin/remote_repo.html', is_link=True))
        search = Search("sthpw/remote_repo")
        widget.set_search(search)
        table = TableWdg("sthpw/remote_repo")
        widget.add(table)
        return widget



class RenewLicenseCbk(Callback):
    ''' Renew License Callback'''

    INPUT_NAME="Renew_License"
    BUTTON_NAME = "Renew License"

    def check(my):
        from pyasm.web import WebContainer
        web = WebContainer.get_web()
        if web.get_form_value(my.BUTTON_NAME):
            return True
        else:
            return False
    
    def get_title(my):
        return "Renew License"

    def get_web(my):
        from pyasm.web import WebContainer
        web = WebContainer.get_web()
        return web

    def execute(my):
        web = my.get_web()
        field_storage = web.get_form_value(my.INPUT_NAME)

        # if no files have been uploaded, don't do anything
        if field_storage.value == "":
           raise TacticException("The license file path is empty")

        # process and get the uploaded files
        upload = FileUpload()
        upload.set_field_storage(field_storage)
        upload.execute()
        my.files = upload.get_files()
        license_file = ''
        if my.files:
            license_file = my.files[0]
        if not license_file:
            raise TacticException("Error retrieving the license file")

        std_name = 'tactic-license.xml'
        if license_file:
            head, file_name = os.path.split(license_file)
            # no restrictions for license file
            #if file_name != std_name:
            #    raise TacticException("License file name should be named tactic-license.xml. The file given is [%s]" %file_name)

            current_license = "%s/config/%s" %(Environment.get_site_dir(), std_name)
            if os.path.exists(current_license):
                FileUndo.remove(current_license)
            FileUndo.move(license_file, current_license)

            my.add_description('Renewed license file')

    def postprocess(my):
        web = my.get_web()
        web.set_form_value('Renewal', 'Success')


