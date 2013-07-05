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


__all__ = ['UndoLogWdg']

from pyasm.common import Date, Xml, Common, Environment
from pyasm.command import Command, CommandExitException
from pyasm.search import TransactionLog, SearchType, Search
from pyasm.web import DivWdg, Table, SpanWdg, WebContainer
from pyasm.widget import FilterSelectWdg, IconRefreshWdg, CheckboxWdg, DateSelectWdg, DateTimeWdg
from pyasm.biz import Project
from pyasm.prod.web import DateFilterWdg



class UndoLogWdg(DivWdg):
    def __init__(my, is_refresh=False):
        super(UndoLogWdg,my).__init__()
        my.all_users_flag = False
        my.all_namespaces_flag = False
        my.add_class("spt_panel")
        my.add_attr("spt_class_name", Common.get_full_class_name(my) )

    def set_all_namespaces(my, flag=True):
        my.all_namespaces_flag = flag

    def set_all_users(my, flag=True):
        my.all_users_flag = flag
        

    def set_admin(my):
        my.set_all_namespaces()
        my.set_all_users()


    def get_display(my):

        #WebContainer.register_cmd("pyasm.admin.UndoLogCbk")

        # add a time filter
        div = DivWdg()
        div.add_color('background','background', -10)
        div.add_color('color','color')
        div.add_style("padding: 15px")
        div.add_border()
        project = ''
        # add a project filter
        if my.all_namespaces_flag:
            span = SpanWdg("Project: ")
            span.add_color('color','color')
            project_select = FilterSelectWdg("project")
            project_select.add_empty_option(label="-- All Projects --")
            project_select.set_option("query", "sthpw/project|code|title")
            span.add(project_select)
            div.add(span)

            project = project_select.get_value()
        else:
            from pyasm.biz import Project
            project = Project.get_global_project_code()


        # add a time filter
        div.add("Show Transaction Log  from:")

        select = DateFilterWdg("undo_time_filter", label="")
        select.set_label(["1 Hour Ago", "6 Hours Ago", "12 Hours Ago", "1 Day Ago", "1 Week Ago", "1 Month Ago"])
        select.set_value(["1 Hour", "6 Hour", '12 Hour',"1 Day", "1 Week", "1 Month"])
        select.set_option("default", "1 Hour")
        div.add(select)

        time_interval = select.get_value() 
        
        # phase out today
        if time_interval == 'today':
            time_interval = '6 Hour'
        elif time_interval == 'NONE':
            time_interval = ''
        my.add(div)

        if not my.all_users_flag:
            user = Environment.get_user_name()
        else:
            span = SpanWdg(css="med")
            span.add("User: ")
            user_select = FilterSelectWdg("user")
            user_select.set_option("query", "sthpw/login|login|login")
            user_select.add_empty_option()
            span.add(user_select)
            div.add(span)

            user = user_select.get_value()

        #transaction_log = TransactionLog.get( user_name=user, \
        #    namespace=project, time_interval=time_interval)

        from tactic.ui.panel import ViewPanelWdg
        
        
        filter = '''[{"prefix":"filter_mode","filter_mode":"and"},{"prefix":"quick","quick_enabled":"","quick_search_text":""},
        {"prefix":"main_body","main_body_enabled":"on","main_body_column":"timestamp","main_body_relation":"is newer than","main_body_select":"%(time)s","main_body_value":""},
        {"prefix":"main_body","main_body_enabled":"on","main_body_column":"login","main_body_relation":"is","main_body_value":"%(user)s"},
        {"prefix":"main_body","main_body_enabled":"on","main_body_column":"namespace","main_body_relation":"is","main_body_value":"{$PROJECT}"},
        {"prefix":"search_ops","levels":[0,0],"ops":["and","and"],"modes":["sobject","sobject"]},
        {"prefix":"search_limit","Showing":"1 - 30","search_limit":"30","limit_select":"30","custom_limit":"","Showing_last_search_offset":"0"},
        {"prefix":"group","group":"","interval":"","order":"","show_retired":""},{}]'''% {'user': user, 'time': time_interval}

        table = ViewPanelWdg(search_type="sthpw/transaction_log", view="table", show_shelf='false', show_select="false", filter=filter)
     
        my.add(table)

        return super(UndoLogWdg, my).get_display()


# TODO: this code is commented out until such a time as a better solution is
# found.  It is hightly questionable whether it is desireable to allow users
# to undo a previous command outside the order of the stack.  This may leave
# the database in an unstable state (deleting sobjects that have dependencies
# on them)
"""
class UndoLogCbk(Command):

    def get_title(my):
        return "Undo Log Command"

    def check(my):
        web = WebContainer.get_web()
        return True

    def execute(my):
        
        web = WebContainer.get_web()
        transaction_ids = web.get_form_values("transaction_log_id")
        if not transaction_ids:
            return

        search = Search(TransactionLog.SEARCH_TYPE)
        search.add_filters("id", transaction_ids)
        transactions = search.get_sobjects()

        # start with just the first one
        transaction = transactions[0]

        transaction.undo()

        my.description = "Undo #%s: %s" % (transaction.get_id(), transaction.get_value("description") )
"""
        


        

         








