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

__all__ = ["MyTacticTabWdg", "WorkHourSummaryWdg", 'CreateTabCmd', 'MyNotificationLogWdg']

from pyasm.biz import Project, Clipboard, Task, Timecard
from pyasm.search import SearchType, SObject
from pyasm.web import *
from pyasm.widget import *
from pyasm.prod.web import *
from pyasm.prod.biz import Shot
from tactic.ui.panel import TableLayoutWdg
from tactic.ui.common import BaseRefreshWdg



class MyTacticTabWdg(BaseTabWdg):


    def init(my):
        help = HelpItemWdg('My Tactic', 'My Tactic area lets users view tasks of interest to him on a weekly/monthly basis, fill in time cards, review notifications and set preferences.')
        my.add(help)
        my.setup_tab("my_tactic_tab", css=TabWdg.SMALL)


    def handle_tab(my, tab):
        tab.add(my.get_tasks_wdg, _("Tasks") )
        #tab.add(my.get_summary_wdg, _("Summary") )
        tab.add( my.get_watchlist_wdg, _("Watch Lists" ) )
        tab.add(my.get_notification_wdg, _("Notifications") )
        tab.add( WorkHourSummaryWdg, _("Work Hours" ) )
        tab.add( my.get_clipboard_wdg, _("Clipboards" ) )
        tab.add( PreferenceWdg, _("Preferences" ) )

        #from pyasm.admin.creator import SObjectCreatorWdg
        #tab.add( SObjectCreatorWdg, _("Custom Asset") )
        #tab.add( CustomViewAppWdg, _("Custom View" ) )




    def get_summary_wdg(my):

        widget = Widget()

        #project = Project.get()

        search = Search(Project)
        projects = search.get_sobjects()

        table = TableWdg("sthpw/project", "mytactic")
        #table.set_sobject(project)
        table.set_sobjects(projects)
        widget.add(table)

        return widget

    def get_week_filter(my):
        ''' a convenience week filter '''
        week_filter = FilterSelectWdg('week_filter', label='Preset Time: ', css='med')
        # don't store this value in db since the CalendarBarWdg takes precedence
        week_filter.persistence = False
        week_filter.set_persist_on_submit()
        values = []
        labels = ['last week' , 'this week', 'next week', '-----------------', 'last month', 'this month', 'next month']
        this_week = 0
        for day in [-7,0,7]:
            date = Date()
            date.add_days(day)
            value = '%s:%s:%s' %(date.get_year(), date.get_month(is_digit=False), date.get_week())
            values.append(value)
            if day == 0:
                this_week = value
        # for separator
        values.append('')
        for day in [-30,0,30]:
            date = Date()
            date.add_days(day)
            values.append('%s:%s' %(date.get_year(), date.get_month(is_digit=False)))

        week_filter.set_option('values', values)
        week_filter.set_option('labels', labels)
        week_filter.add_empty_option()

        week_filter.set_event('onchange', \
            "TacticCalendarLabel.set_range('cal_left_control_hid', this.value)")
        week_filter.add_event('onchange', \
            "TacticCalendarLabel.set_range('cal_right_control_hid', this.value) ")
        week_filter.set_submit_onchange()

        
        return week_filter

    def get_tasks_wdg(my):
        widget = Widget()
        help = HelpItemWdg('Tasks', 'Tasks tab lets users view tasks assigned to him from multiple projects. For convenience, you can select a Time Preset like [this week] or [this month] to view what tasks fall within the chosen time range. Alternatively, you can click on the year, month, or week labels of the calendar to set a time range.')
        widget.add(help)

        search = Search("sthpw/task")
        search.add_order_by("bid_start_date")
        
        div = DivWdg(css="filter_box")
        div = FilterboxWdg()

        week_filter = my.get_week_filter()
        div.add(week_filter)
       
        range_checkbox = FilterCheckboxWdg("all_tasks", label="Show All Assigned Tasks")
        range_flag = range_checkbox.get_value()
        
        div.add(range_checkbox)
        hint = HintWdg("If not checked, only the tasks that fall within the defined date range are displayed")
        div.add(hint)

        project_filter = ProjectFilterWdg()
        project_filter.get_navigator().set_submit_onchange(False)
        project_code = project_filter.get_value()
        div.add_advanced_filter(project_filter)
        div.add_advanced_filter(HtmlElement.br())

        task_filter = TaskStatusFilterWdg()
        div.add_advanced_filter(task_filter)
        
        search.add_project_filter(project_code)
        task_statuses = task_filter.get_processes()
        task_statuses_selected = task_filter.get_values()
         
        # one way to show tasks with obsolete statuses when the user
        # check all the task status checkboxes
        if task_statuses != task_statuses_selected:
            search.add_filters("status", task_filter.get_values() )


        widget.add(div)

        user = Environment.get_user_name()
        search.add_filter("assigned", user)

        # add a date filter

        # TODO: should somehow get this from CalendarBarWdg
        if not range_flag:
            from pyasm.widget import CalendarBarWdg
            left_bound_hid = HiddenWdg('cal_left_control_hid')
            left_bound_hid.set_persistence()
            cal_left = left_bound_hid.get_value()
            right_bound_hid = HiddenWdg('cal_right_control_hid')
            right_bound_hid.set_persistence()
            cal_right = right_bound_hid.get_value()


            if not cal_left or not cal_right:
                # TODO: should be this month
                start_year = "2007"
                start_month_str = "Jan"
                end_year = "2007"
                end_month_str = "Dec"
            else:
                start_year, start_month_str = cal_left.split(":")
                end_year, end_month_str = cal_right.split(":")

            months = CalendarBarWdg.MONTHS
            start_month = 1
            end_month = 12
            if not start_year:
                date = Date()
                start_year = date.get_year()
                end_year = date.get_year()
            try:
                start_month = months.index(start_month_str)+1
            except ValueError:
                pass
            try:
                end_month = months.index(end_month_str)+2
            except ValueError:
                pass
            if end_month == 13:
                end_month = 1
                end_year = int(end_year)+1


            start_date = "%s-%0.2d-01" % (start_year, start_month)
            end_date = "%s-%0.2d-01" % (end_year, end_month)

            preset_week = HiddenWdg('cal_week_hid').get_value()
            if preset_week:
                # handle cross-year scenario
                if int(preset_week) == 1 and start_month == 12:
                    start_year = int(start_year) + 1
                day_list = Calendar.get_monthday_time(\
                    start_year, int(preset_week), month_digit=True)[0]
                
                year = day_list[2][0]
                month = int(day_list[0])
                month_day = day_list[1]
                start_date = "%s-%0.2d-%s" % (year, month, month_day)
                
                start_date_obj = Date(db_date=start_date)
                start_date_obj.add_days(7)
                end_date = start_date_obj.get_db_date()
            
            search.add_where('''
                ( (bid_start_date >= '%s' and bid_start_date <= '%s') or 
                  (bid_end_date >= '%s' and bid_end_date <= '%s') or
                  (bid_start_date <= '%s' and bid_end_date >='%s'))
            ''' % (start_date, end_date, start_date, end_date, start_date, end_date) )



        table = TableWdg("sthpw/task", "my_task")
        sobjects = search.get_sobjects()
        sorted_tasks = Task.sort_tasks(sobjects)
        table.set_sobjects(sorted_tasks)
        widget.add(table)
        return widget







    def get_notification_wdg(my):

        widget = Widget()

        nav = DivWdg(css="filter_box")
        widget.add(nav)

        search_filter = SearchFilterWdg(columns=['subject', 'message'])
        nav.add(search_filter)

        project_code = Project.get_project_code()
        user_name = Environment.get_user_name()

        # get all the notifications that were sent to you
        search = Search("sthpw/notification_login")
        search.add_filter("login", user_name)
        search.add_filter("project_code", project_code)
        #search.add_filter("type", "to")
        notification_logins = search.get_sobjects()

        notification_ids = [x.get_value("notification_log_id") for x in notification_logins]


        table = TableWdg("sthpw/notification_log")
        search = Search("sthpw/notification_log")

        search.add_filter("project_code", project_code)
        search.add_filters("id", notification_ids)

        search_filter.alter_search(search)

        table.set_search(search)
        widget.add(table)

        return widget



    def get_watchlist_wdg(my):

        widget = Widget()
        WebContainer.register_cmd("pyasm.widget.ClipboardMoveToCategoryCbk")

        div = DivWdg(css="filter_box")

        select = FilterSelectWdg("clipboard_category",\
            label="Current Watch List: ", css='med')
        select.set_option("values", "watch_list|watch_list2|watch_list3")
        select.add_empty_option("-- Any Category --")
        div.add(select)

        search_type_sel = SearchTypeFilterWdg()
       
        div.add(search_type_sel)


        widget.add(div)

        div = DivWdg()
        from pyasm.prod.web import ProdIconSubmitWdg
        copy = ProdIconSubmitWdg(ClipboardMoveToCategoryCbk.COPY_BUTTON)
        copy.add_style("float: right")
        #clear = ProdIconSubmitWdg("Clear All")
        #clear.add_style("float: right")
        div.add(copy)
        #div.add(clear)
        div.add(HtmlElement.br(2))
        widget.add(div)

        # get all of the clipboard items
        value = select.get_value()
        search = Clipboard.get_search(category=value)
        search_type_sel.alter_search(search)
        table = TableWdg("sthpw/clipboard", "watch_list")
        table.set_search(search)
        widget.add(table)
        return widget


    def get_clipboard_wdg(my):

        widget = Widget()

        # get all of the clipboard items
        value = "select"
        clipboards = Clipboard.get_all(value)

        table = TableWdg("sthpw/clipboard", "select")
        table.set_sobjects(clipboards)
        widget.add(table)
        return widget



class WorkHourSummaryWdg(BaseRefreshWdg):


    def _has_user_wdg_access(my):
        ''' check if the user can see this user filter wdg '''
        security = Environment.get_security()
        key = 'UserFilterWdg'
        if security.check_access("secure_wdg", key, "view"):
            return True
        return False

    """
    def _get_filter_box(my, search):
        div = DivWdg(css='filter_box')
        login_filter = None

        if my._has_user_wdg_access():
            login_filter = UserFilterWdg()
            login_filter.navigator.set_submit_onchange()
    
        project_filter = ProjectFilterWdg()
        div.add(login_filter)

        work_date_selector = CalendarInputWdg(WeekTableElement.CAL_NAME, show_week=True)
        work_date_selector.set_persist_on_submit()
        selected_date = work_date_selector.get_value()
       
        work_date_selector.set_onchange_script('document.form.submit()')
        date = None
        if selected_date:
            date = Date(db_date = selected_date)
        else: # take today if not set
            date = Date() 
        selected_date = date.get_db_date()
        
        week_filter = WeekFilterWdg(selected_date, WeekTableElement.CAL_NAME)

        #web_state = WebState.get()
        #web_state.add_state("edit|week_filter", week_filter.get_value())
        selected_year = selected_date.split('-', 2)[0]
        if selected_year:
            search.add_filter('year', selected_year)

        if selected_date:
            week_value = date.get_week()
            search.add_filter('week', week_value)

        if login_filter:
            login_filter.alter_search(search)
        else:
            search.add_filter('login', Environment.get_user_name())

        project_filter.alter_search(search)
        
        
        date_span = SpanWdg("Date: ", css='med')
        date_span.add(work_date_selector)
        div.add(date_span)
        div.add(week_filter)
        div.add(project_filter)
        return div

    """ 

    def get_display(my):
        widget = DivWdg()

        my.set_as_panel(widget, class_name='spt_view_panel spt_panel')
 
        # create a table widget and set the sobjects to it
        table_id = "main_body_table" 
        filter = my.kwargs.get('filter')
        table = TableLayoutWdg(table_id=table_id, search_type="sthpw/timecard", \
                view="table", inline_search=True, filter=filter, search_view='search' ) 

       
        search_type = "sthpw/timecard"
        from tactic.ui.app import SearchWdg
        
        search_wdg = SearchWdg(search_type=search_type, view='search', filter=filter)
        
        widget.add(search_wdg)
        search = search_wdg.get_search()

        # FIX to current project timecard for now
        search.add_filter('project_code', Project.get_project_code())
        #search.add_project_filter()

        table.alter_search(search)
        print "SEA ", search.get_statement()
        sobjects = search.get_sobjects()
        print "SOB ", sobjects
        table.set_sobjects(sobjects, search)
        widget.add(table)
        #widget.add(SpecialDayWdg())
        return widget

class MyNotificationLogWdg(BaseRefreshWdg):

    def get_display(my):

        widget = DivWdg()
        my.set_as_panel(widget, class_name='spt_view_panel spt_panel')

        # create a table widget and set the sobjects to it
        table_id = "main_body_table" 
        table = TableLayoutWdg(table_id=table_id, search_type="sthpw/notification_log", \
                view="table", inline_search=True, search_view='search') 

        search_type = "sthpw/notification_log"
        
        from tactic.ui.app import SearchWdg
        
        search_wdg = SearchWdg(search_type=search_type, view='search')

        
        widget.add(search_wdg)
        search = search_wdg.get_search()
        table.alter_search(search)
        sobjects = search.get_sobjects()
        table.set_sobjects(sobjects, search)
        widget.add(table)

        return widget


