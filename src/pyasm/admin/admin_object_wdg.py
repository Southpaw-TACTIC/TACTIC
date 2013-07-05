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

__all__ = ['SearchObjectWdg', 'LoginWdg', 'LoginGroupWdg', 'NamespaceWdg', 'TriggerWdg']
            

from pyasm.common import Environment
from pyasm.search import Search
from pyasm.web import *
from pyasm.widget import TableWdg, BaseTableElementWdg, SelectWdg, \
    FilterSelectWdg, GeneralAppletWdg, HiddenWdg, RetiredFilterWdg
from pyasm.prod.web import SObjectUploadCmd, SObjectActionWdg, SearchFilterWdg
from pyasm.biz import Project


class SearchObjectWdg(Widget):

    def init(my):
        namespace = WebContainer.get_web().get_context_name()
        search = Search("sthpw/search_object")
        if namespace != "":
            search.add_where("\"namespace\"='%s'" % namespace)

        table = TableWdg("sthpw/search_object")
        table.set_search( search )
        my.add(table)




class LoginWdg(Widget):

    def init(my):

        search = Search("sthpw/login")

        license = Environment.get_security().get_license()
        namespace = WebContainer.get_web().get_form_value(NamespaceWdg.WDG_NAME)
        count = search.get_count()
        max_users = license.get_max_users()

        div = DivWdg(css='filter_box')
        
        my.add(div)

        # reinstantiate to show retired properly
        search = Search("sthpw/login")
        if namespace != "":
            search.add_where("\"namespace\"='%s'" % namespace)

        project_code = Project.get_project_code()
        if project_code == "admin":
            span = SpanWdg(css="med")
            project_filter = FilterSelectWdg("project_code")
            project_filter.add_empty_option("-- Select --")
            project_filter.set_option("query", "sthpw/project|code|code")
            span.add("Project: ")
            span.add(project_filter)
            div.add(span)
            project_select_value = project_filter.get_value()
        else:
            project_select_value = project_code

        if project_select_value:
            search.add_where( Project.get_project_filter(project_select_value) )

        search_columns = ['first_name', 'last_name', 'login']
        search_filter = SearchFilterWdg(name='user_search', \
                columns=search_columns, label='User Search: ')
        search_filter.alter_search(search)

        div.add(search_filter)

        retired_filter = RetiredFilterWdg()
        retired_filter.alter_search(search)
        div.add(retired_filter)
        div.add(HtmlElement.br(2))
        div.add("Active Users: %s " % count)
        div.add("(max users: %s)" % max_users)
        if max_users - count <= 1:
            div.add_style("color: red")

        table = TableWdg("sthpw/login")
        logins = search.get_sobjects()
        table.set_sobjects( logins )
        my.add(table)

class NamespaceWdg(BaseTableElementWdg):
    
    WDG_NAME = "namespace"
    
    def get_title(my):
        return my.WDG_NAME.capitalize()
    
    def get_prefs(my):
        span = SpanWdg(css='small')
        namespace = my.web.get_context_name()
        select = SelectWdg(my.WDG_NAME)
        
        select.set_option("values", "|%s" % namespace)
        select.set_option("labels", "-- All --|%s" % namespace)
        select.set_submit_onchange()
        select.set_persist_on_submit()
        span.add(select)
        return span
    
    def init(my):
        pass
    
    def get_display(my):
        sobject = my.get_current_sobject()
        widget = StringWdg(sobject.get_value('namespace'))
        
        return widget

   


class LoginGroupWdg(Widget):

    def init(my):
        namespace = WebContainer.get_web().get_form_value(NamespaceWdg.WDG_NAME)
        search = Search("sthpw/login_group")
        if namespace != "":
            search.add_where("\"namespace\"='%s'" % namespace)

        table = TableWdg("sthpw/login_group")
        table.set_search( search )
        my.add(table)




class TriggerWdg(Widget):

    def init(my):
        search = Search("sthpw/trigger")
        table = TableWdg("sthpw/trigger")
        table.set_search( search )
        my.add(table)
