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

#__all__ = [ 'MilestoneTableElement', 
#    'MilestoneWdg', 'MilestoneSetCmd']
__all__ = ['TimecardWdg', 'TimecardHourCmd', 'TimecardTaskRowWdg',
          'TimecardCmd','TimecardCreateCmd',
         'SpecialDayWdg', 'WeekTableElement', 'TimecardInfoTableElement', 
         'WeekHourInputWdg']
            

from pyasm.command import Command, CommandExitException, DatabaseAction
from pyasm.search import Search, SObjectFactory, SObject, Sql
from pyasm.biz import Pipeline, Timecard, Project, Task
from pyasm.web import *
from pyasm.widget import IconSubmitWdg, HiddenWdg, WidgetConfig, HintWdg, ExpandableTextWdg, CalendarInputWdg
from pyasm.common import *
from input_wdg import TextWdg, CalendarWdg, SelectWdg, ActionSelectWdg, FilterSelectWdg
from table_element_wdg import BaseTableElementWdg
from icon_wdg import IconWdg
from file_wdg import ThumbWdg
from custom_info_wdg import CustomInfoInputWdg

def _get_div(width):
    ''' just to get a div to draw this widget '''
    return FloatDivWdg(width=width)
    
class TimecardTaskRowWdg(AjaxWdg):

    def init(my):
        ''' initializes a few variables ''' 
        today = Date()
        my.week = int(today.get_week())
         
        my.year = int(today.get_year())
        my.process_len = 0
        my.week_element_name = ''
        my.year_element_name = ''
        my.task = None
        my.cmd = None
        my.overtime_dict = {}
        
    
    def init_cgi(my):
        # get the sobject
        keys = my.web.get_form_keys()
        search_key = ''
        
        for key in keys:
            if key.startswith('skey_TimecardWdg_'):
                search_key = my.web.get_form_value(key)
                continue
            if key.startswith('week_'):
                my.week_element_name = key
                my.week = my.web.get_int_form_value(key)
                continue
            if key.startswith('year_'):
                my.year_element_name = key
                my.year = my.web.get_int_form_value(key)
                continue
        if search_key:
            sobject = Search.get_by_search_key(search_key)
            my.task = sobject
            
            my.init_setup()
        
        
            my.add_inputs()
       
    def add_inputs(my):
        ''' register the inputs '''
        if not my.task:
            return
        hidden = HiddenWdg('skey_TimecardWdg_%s' %my.task.get_id())
        my.add_ajax_input(hidden)
        
        week_text = TextWdg('week_%s' %my.task.get_search_key())
        my.add_ajax_input(week_text) 

        year_text = HiddenWdg('year_%s' %my.task.get_search_key())
        my.add_ajax_input(year_text) 
       
    def init_setup(my):
        ''' set up the ajax top and the ajax command '''
        div_id = 'main_div_general'
        cmd_id = 'cal_general'

        if my.task:
            div_id = 'main_div_%s' %my.task.get_id()
            cmd_id = 'cal_%s' %my.task.get_id()
            
        my.main_div = DivWdg(id=div_id)
        my.set_ajax_top(my.main_div)
        
        my.cmd = AjaxCmd(cmd_id)
        my.cmd.add_element_name(my.week_element_name) 
        my.cmd.add_element_name(my.year_element_name) 
        

    def set_task(my, task):
        my.task = task
        my.init_setup()
       
    def get_cmd(my):
        return my.cmd
        
    def get_script(week_name, year_name, add=True):
        ''' if add==True, we are advancing to the next week '''
        if add:
            return "Timecard.update_date('%s','%s','forward')"%(week_name, year_name) 
        else:
            return "Timecard.update_date('%s','%s','backward')"%(week_name, year_name) 

    get_script =staticmethod(get_script)
    
   
        
       
    def get_display(my):
       
        if not my.is_from_ajax():
            return my.main_div

        my.process_len = TimecardWdg.get_process_width(my.task)
        if my.process_len > TimecardWdg.PROCESS_WIDTH:
            main_width = 50 * my.process_len / TimecardWdg.PROCESS_WIDTH
            my.main_div.add_style('width', '%sem' %main_width)
        my.add_control(my.main_div)
        
        my.main_div.add(HtmlElement.br(2))
        
        my.add_unregistered_hours(my.main_div)
        my.main_div.add(HtmlElement.br())
        my.add_overtime_hours(my.main_div)
        
        return my.main_div
   
    def add_control(my, main_div):
        ''' add the control for adjusting time card hours'''
        weekday_list = Calendar.get_monthday_time(my.year, my.week)
        month_list = []
        for item in weekday_list:  
             month, day, time = item
             if month not in month_list:
                 month_list.append(month)
       
        today = Date()
        current_week = int(today.get_week())
        current_year = int(today.get_year())

        today_div = _get_div(TimecardWdg.PROCESS_WIDTH)
        today_div.add(my._get_this_week_link(current_week, current_year))
        main_div.add(today_div)
        title_div = _get_div(270)
        #title_div.add_style('color: #6869a3')
        title_div.add_class('right_content')
        
        main_div.add(title_div)
        
        # show the year and month
        month = ' / '.join(month_list)
        year = my.year
        title_div.add(SpanWdg(month, css='small'))
        title_div.add('&middot;')
        title_div.add(SpanWdg(year, css='small'))
        
        if not my.task or not my.week:
            main_div.add('Invalid task info or undetermined week found!')
            return main_div

        main_div.add(HtmlElement.br(2))

        process_div = _get_div(my.process_len)
        process_div.add('&nbsp;')
        main_div.add(process_div)
        
        for idx, weekday in enumerate(TimecardWdg.WEEK_CALENDAR):
            div = _get_div(50)
            div.add(weekday.capitalize()[0:1])
            month, day, time = weekday_list[idx]
            div.add(SpanWdg(day, css='med'))
            main_div.add(div)
            
        main_div.add(HtmlElement.br())
        process_div_container = _get_div(my.process_len)
        
        process = 'general'
        if isinstance(my.task, Task):
            process = my.task.get_process()
        process_div = FloatDivWdg(process, css='timecard_process')
        process_div.add_style("padding-right: 6px")
        process_div_container.add(process_div)
       
        main_div.add(process_div_container)
       
        
        # register cmd 
        my.cmd.register_cmd("TimecardHourCmd")

        # query the db values
        timecard = Timecard.get(my.task.get_search_key(), my.week, my.year,\
            login=Environment.get_user_name())
        if timecard:
            timecard = timecard[0]
        
       
        # add the progress icon
        progress = my.cmd.generate_div()
        progress.add("&nbsp;")
        progress.add_style('width: 20px')
        progress.add_style('float: left')
       
        progress.set_post_ajax_script(my.get_refresh_script(show_progress=False))
        process_div_container.add(progress)

        today_time = Date().get_struct_time()
        for idx, weekday in enumerate(TimecardWdg.WEEK_CALENDAR):
            div = _get_div(50)
            month, day, time = weekday_list[idx]
            
            select = ActionSelectWdg(weekday)
            select.add_empty_option()

            # disable setting time cards in the future
            if time > today_time:
                select.set_attr('disabled','')
            else:    
                # using the MAX_HOUR
                hours = ['%0.1f'%x for x in xrange(0, TimecardWdg.MAX_HOUR  + 1)]
                select.set_option('values', hours)
                if timecard:
                    select.set_value( timecard.get_value(weekday))
                my.cmd.set_option('search_key', my.task.get_search_key())
                my.cmd.set_option('attr_name',  weekday)
                my.cmd.set_option('project_code', Project.get_project_code())
                
                select.add_event("onchange", my.cmd.get_on_script() )
            div.add(select)
            main_div.add(div)
            
    def _get_this_week_link(my, week, year):
        if my.week != week:
            # add the today link
            week_name = 'week_%s' %my.task.get_search_key()
            year_name = 'year_%s' %my.task.get_search_key()
            script = ["document.form.elements['%s'].value='%s';" \
                    "document.form.elements['%s'].value='%s'" %(week_name, week, year_name, year)]
            script.append(my.get_refresh_script())
            link = HtmlElement.js_href(';'.join(script), '[this week]')
            span = SpanWdg(link, css='small')
        else:
            span = SpanWdg('[this week]&nbsp;', css='small')
            span.add_style('color','#bbb')
            
        return span
    
    def add_unregistered_hours(my, main_div):
        '''draw the unregistered hours'''
        row_div = FloatDivWdg()
        row_div.add_style("margin-bottom: 4px")
        main_div.add(row_div)
        process_div =  _get_div(my.process_len)
        process_div.add("unregistered hours")
        #process_div.add_style('color: #999')
        row_div.add(process_div)
        
        for i in TimecardWdg.WEEK_CALENDAR:
            unreg_hours = 0.0
            div = _get_div(50)
            row_div.add(div)
            div.add_class('center_content')
            span = SpanWdg()
            div.add(span)
            span.add_style('padding: 0 6px 0 6px')

            max_hours = Project.get_reg_hours()
            if not max_hours:
                max_hours = TimecardWdg.MAX_REG_HOURS
            max_hours = float(max_hours)

            # get all the timecards for the week and hours 
            reg_hours = Timecard.get_registered_hours(None, my.week, i, my.year)
                    
            unreg_hours = max_hours-reg_hours
            if unreg_hours <= 0:
                my.overtime_dict[i] = abs(unreg_hours)
                unreg_hours = IconWdg(icon=IconWdg.GOOD)
            else:
                my.overtime_dict[i] = ''
                unreg_hours = str(unreg_hours)
            span.add(unreg_hours)
            
       
    def add_overtime_hours(my, main_div):
        '''draw the unregistered hours'''
        row_div = FloatDivWdg()
        main_div.add(row_div)
        process_div =  _get_div(my.process_len)
        process_div.add("overtime hours")
        #process_div.add_style('color: #999')
        row_div.add(process_div)
        for i in TimecardWdg.WEEK_CALENDAR:
            div = _get_div(50)
            div.add_class('center_content')
            row_div.add(div)
            span = SpanWdg()
            div.add(span)
            span.add_style('padding: 0 6px 0 6px')
            hour = my.overtime_dict.get(i)
            if hour:
                span.add(hour)
                span.add_class('timecard_overtime')
            else:
                span.add('&nbsp;')
        
class TimecardWdg(AjaxWdg):

    WEEK_CALENDAR = ["mon","tue","wed","thu","fri","sat","sun"]
    MAX_HOUR = 12
    MAX_REG_HOURS = 10
    PROCESS_WIDTH = 120
   
    def init(my):
        my.task = None
        my.week = None
        my.year = None
        my.main_div = DivWdg()
   
    def init_cgi(my):
        # get the sobject
        keys = my.web.get_form_keys()
        search_key = ''
        
        for key in keys:
            if key.startswith('skey_TimecardWdg_'):
                search_key = my.web.get_form_value(key)
                continue
            if key.startswith('week_'):
                my.week = my.web.get_int_form_value(key)
                continue
            if key.startswith('year_'):
                my.year = my.web.get_int_form_value(key)
                continue
        if search_key:
            sobject = Search.get_by_search_key(search_key)
            my.task = sobject
            my.init_setup()

       

    def init_setup(my):
        '''set the ajax top and register some inputs'''
        div_id = 'timecard_%s' %my.task.get_id()
        my.main_div = DivWdg(id=div_id)
        my.set_ajax_top(my.main_div)

        # register the inputs first
        hidden = HiddenWdg('skey_TimecardWdg_%s' %my.task.get_id())
        my.add_ajax_input(hidden)

        week_text = TextWdg('week_%s' %my.task.get_search_key())
        my.add_ajax_input(week_text) 

        year_text = HiddenWdg('year_%s' %my.task.get_search_key())
        my.add_ajax_input(year_text) 
        
    def set_task(my, task):
        my.task = task
        my.init_setup()
        
                
    def get_display(my):
       
        main_div = my.main_div
        
        if not my.week:
            today = Date()
            my.week = today.get_week()
            my.year = today.get_year()

 
        task_row = TimecardTaskRowWdg()
        task_row.set_task(my.task)
      
        if my.task:
            hidden = HiddenWdg('skey_TimecardWdg_%s' %my.task.get_id(), my.task.get_search_key())
            main_div.add(hidden)
        else:
            return "There was a problem reading task data. Refresh"

        my._add_week(main_div, my.week, task_row)
        my._add_year(main_div, my.year, task_row)

        main_div.add(task_row)
            
        main_div.add(HtmlElement.br(2))
       
       
        # draw the processing icon
        process_div =  _get_div(1)
        process_div.add("&nbsp;")
        main_div.add(process_div)
     
        main_div.add(HtmlElement.br())

        return main_div
        
  
    def _add_year(my, main_div, year, widget):
        '''add year display'''
        name = 'year_%s' %my.task.get_search_key()
        year_text = HiddenWdg(name, year)
        main_div.add(year_text)
        widget.get_cmd().add_element_name(name)

        
    def _add_week(my, main_div, week, widget):
        '''add week display'''
        week_name = 'week_%s' %my.task.get_search_key()
        year_name = 'year_%s' %my.task.get_search_key()

        weeks = [i for i in xrange(1, 53)]
        week_filter = SelectWdg(week_name)
        week_filter.add_class('med')
        week_filter.set_option('values', weeks)

        week_filter.set_value(week)
        
        #widget.add_ajax_input(week_text)
        # add the name to the TimecardHourCmd
        widget.get_cmd().add_element_name(week_name)
        refresh_script = widget.get_refresh_script()
       
        week_filter.add_event('onchange', refresh_script)

        script = [TimecardTaskRowWdg.get_script(week_name, year_name, add=False)]
        script.append(refresh_script)
        img = IconWdg(icon=IconWdg.ARROW_LEFT)
        link = HtmlElement.js_href(';'.join(script), data=img)
        div = _get_div(20)
        div.add(link)
        main_div.add(div)
        div = _get_div(70)
        div.add("Wk&nbsp;")
        
        div.add(week_filter)
        
        main_div.add(div)
        div = _get_div(20)
        
        script = [TimecardTaskRowWdg.get_script(week_name, year_name, add=True)]
        script.append(refresh_script)

        img = IconWdg(icon=IconWdg.ARROW_RIGHT)
        link = HtmlElement.js_href(';'.join(script), data=img)
        div.add(link)
        
        main_div.add(div)
        
        
    

    # static functions
    def get_process_width(task):
        ''' get the width for the process div depending on the length of the process'''
        return max(TimecardWdg.PROCESS_WIDTH, (len(task.get_process()) + 1) * 9)
       
    get_process_width = staticmethod(get_process_width)


class SpecialDayWdg(TimecardWdg):

    def get_display(my):
       
        main_div = my.main_div
        
        if not my.week:
            today = Date()
            my.week = today.get_week()
            my.year = today.get_year()

 
        task_row = TimecardTaskRowWdg()
        task_row.set_task(my.task)
        hidden = HiddenWdg('skey_SpecialDayWdg_%s' %my.task.get_id(), my.task.get_search_key())
        main_div.add(hidden)
            
        my._add_week(main_div, my.week, task_row)
        my._add_year(main_div, my.year, task_row)

        main_div.add(task_row)
        main_div.add(HtmlElement.br(2))
       
        # draw the processing icon
        process_div =  _get_div(1)
        process_div.add("&nbsp;")
        main_div.add(process_div)
     
        main_div.add(HtmlElement.br())

        return main_div


class WeekTableElement(BaseTableElementWdg):

    CAL_NAME = "work_date_selector"
    DAY_TITLE_WIDTH = 15
    WEEK_TITLE_WIDTH = 80
    def preprocess(my):
        my.hours_dict = {}

    def init(my):
        my.weekday = None
        my.mode = 'week'
        my.sel = FilterSelectWdg('time_card_mode', label='View: ')
        my.sel.set_option('values', 'week|day')
        my.prefix = "timecard_filter" 
    
    def get_prefs(my):
        my.sel = FilterSelectWdg('time_card_mode', label='View: ')
        my.sel.set_option('values', 'week|day')
        return my.sel

    def get_title(my):
        from tactic.ui.filter import FilterData
        values = FilterData.get().get_values_by_index(my.prefix, 0)
        selected_year = ''
        date = None
        selected_date_value = values.get(my.CAL_NAME)
 
        work_date_selector = CalendarInputWdg(my.CAL_NAME)
        if selected_date_value:
            selected_date = Date(db_date=selected_date_value)
        else:
            selected_date = Date()
        #my.mode = my.sel.get_value()

        week = int(selected_date.get_week())

        year = int(selected_date.get_year())
        weekday_list = Calendar.get_monthday_time(year, week)

        div = DivWdg() 
        if my.mode == 'day':
            spacer = FloatDivWdg('&nbsp;', width=my.DAY_TITLE_WIDTH)
            div.add(spacer)
            my.weekday = int(selected_date.get_weekday(is_digit=True))
            month = selected_date.get_month(is_digit=False)
            month_div = FloatDivWdg(css='center_content')          
            month_div.add(month)
            div.add_style('width: 15em')
        else:
            month_list = []
            for item in weekday_list:  
                 month, day, time = item
                 if month not in month_list:
                     month_list.append(month)

            month_div = FloatDivWdg(width=my.WEEK_TITLE_WIDTH, css='right_content')
            month_div.add(' / '.join(month_list))
            div.add_style('width: 45em')
       
        div.add(month_div)

        for idx, i in enumerate(TimecardWdg.WEEK_CALENDAR):
            if my.weekday != None and idx != my.weekday:
                continue
            total = FloatDivWdg(width=50, css='center_content')
            span = SpanWdg(weekday_list[idx][1])
            if i in ["sat", "sun"]:
                span.add_style('color', '#995151')
            span.add(HtmlElement.br())

            weekday_span = SpanWdg('%s' %i.capitalize(), css='smaller')
            span.add(weekday_span)
            total.add(span)
            div.add(total)
        
        return div

    def get_display(my):
        mode = my.sel.get_value()
        div = DivWdg()
        if my.mode == 'day':
            spacer = FloatDivWdg('&nbsp;', width=my.DAY_TITLE_WIDTH)
        else:
            spacer = FloatDivWdg('&nbsp;', width=my.WEEK_TITLE_WIDTH)
        div.add(spacer)
        timecard = my.get_current_sobject()
        for idx, i in enumerate(TimecardWdg.WEEK_CALENDAR):
            if my.weekday != None and idx != my.weekday:
                continue
            total = FloatDivWdg(width=50, css='center_content')
            hours = timecard.get_value(i)
            hours_label = hours
            if not hours:
                hours = 0
                hours_label = '-'

            span = SpanWdg(hours_label)
            cur_val = my.hours_dict.get(i)
            if not cur_val:
                cur_val = 0
            my.hours_dict[i] = cur_val + float(hours)

            total.add(span)
            div.add(total)
       
        return div 

    def get_bottom_wdg(my):
        div = DivWdg()
        if my.mode == 'day':
            spacer = FloatDivWdg('Daily Total: ', width=my.DAY_TITLE_WIDTH, css='right_content')
        else:
            spacer = FloatDivWdg('Weekly Total: ', width=my.WEEK_TITLE_WIDTH, css='right_content')
        div.add(spacer)

        weekly_hours = 0
        timecard = my.get_current_sobject()
        for idx, i in enumerate(TimecardWdg.WEEK_CALENDAR):
            if my.weekday != None and idx != my.weekday:
                continue
            total = FloatDivWdg(width=50, css='center_content')
            hours = my.hours_dict.get(i)
            hours_label = hours
            if not hours:
                hours = 0
                hours_label = '-'

            span = SpanWdg(hours_label)

            
            weekly_hours += float(hours)
            if my.weekday == None:
                total.add(span)
                div.add(total)
    
        weekly_total = FloatDivWdg(width=60, css='center_content')
        weekly_total.add(HtmlElement.b(weekly_hours))
        div.add(weekly_total)
        return div


class TimecardCreateCmd(DatabaseAction):
     
    def __init__(my):
        super(TimecardCreateCmd, my).__init__()
        my.desc = None
        my.date = None
        my.project_code = None
   
    
    def get_title(my):
        return "TimecardCreateCmd"


    def check(my):
        my.web = WebContainer.get_web()
        search_type = my.sobject.get_search_type_obj()
        
        config = WidgetConfig.get_by_search_type(search_type, "insert", local_search=True)
        columns = config.get_element_names()

        if len(columns) != 3:
            raise TacticException('The command is expecting 3 fields only.')
      
        my.date = my.web.get_form_value('edit|%s' % columns[0])
        my.desc =  my.web.get_form_value('edit|%s'% columns[1])
        date = Date(db_date=my.date)
        my.year = date.get_year()
        my.week = date.get_week()
        my.project_code =  my.web.get_form_value('edit|%s'% columns[2])
         
        if not my.desc or not my.date or not my.project_code:
            raise UserException('One or more fields are empty.')
        Project.set_project(my.project_code)
        return True

    def execute(my):
        cards = Timecard.get(None, week=my.week, year=my.year, \
            desc=my.desc, project=my.project_code)
        if not cards:
            # this has been set in the EditCmd
            timecard = my.sobject
            timecard.set_value('login', Environment.get_user_name())
            timecard.set_value('project_code', my.project_code)
            timecard.set_value("year", my.year)
            timecard.set_value("week", my.week)
            timecard.set_value("description", my.desc)
            timecard.commit()

        else:
            raise UserException('This time card already exists. '\
                    'Please edit the existing one instead.')

''' deprecated 
class TimecardTableElement(BaseTableElementWdg):

    def get_title(my):
        # TODO: this is not the proper way to call class_init, but it is
        # broken now
        widget = Widget()
        init = my._class_init()
        widget.add(init)

        # have to put this here because of the broken class init
        WebContainer.register_cmd("TimecardCmd")

        div = DivWdg()
        week = DivWdg('Week')
        week.set_style("width: 50px; float: left")
        div.add(week)
        for i in ("mon","tue","wed","thu","fri","sat","sun"):
            total = DivWdg()
            total.add_style("width: 50px")
            total.add_style("float: left")
            total.add(i.capitalize())
            div.add(total)

        ids = [ str(x.get_id()) for x in my.sobjects ]
        ids_str = ", ".join(ids)
        script = HtmlElement.script("timecard_ids = [%s]" % ids_str)

        widget.add(div)
        widget.add(script)

        return widget



    def _class_init(my):
        script = HtmlElement.script("""
        timecard_ids = []

        add = function(id) {
            var total = 0
            var days = ["mon","tue","wed","thu","fri","sat","sun"]
            for ( var i = 0; i < 7; i++ ) {
                day = days[i]
                var name = "timecard|"+id+"|"+day
                timecard_elem = document.getElementById("timecard|"+id+"|"+day)
                timecard = timecard_elem.value
                if ( timecard == "" ) continue
               
                timecard = parseInt(timecard*10)/10
                if ( isNaN(timecard) ) {
                    alert("You must enter a number")
                    return
                }

                total = total + timecard
            }
            total_elem = document.getElementById("timecard|total|"+id)
            total_elem.innerHTML = total

            // calculate day total
            for ( var i = 0; i < 7; i++ ) {
                day = days[i]
                day_total_elem = document.getElementById( "timecard|total|" + day)
                day_total = 0
                for (j in timecard_ids)
                {
                    tmp = timecard_ids[j]
                    timecard_elem = document.getElementById("timecard|"+tmp+"|"+day)
                    timecard = timecard_elem.value
                    if ( timecard == "" ) continue
                    timecard = parseInt(timecard*10)/10

                    day_total = day_total + timecard
                }
                day_total_elem.innerHTML = day_total

            }


        }
        """)
        #my.add(script)
        return script


    def get_display(my):

        sobject = my.get_current_sobject()

        # get the timecard object
        search = Search("sthpw/timecard")
        search.add_sobject_filter(sobject)
        #search.add_filter("week", week)
        timecard = search.get_sobject()


        widget = DivWdg()


        widget.add_style("text-align: left")
        widget.add(DivWdg(sobject.get_value('week')))
        
        for i in ("mon","tue","wed","thu","fri","sat","sun"):

            name = "timecard|%s|%s" % (sobject.get_id(), i)
            hours_wdg = TextWdg("timecard|%s|%s" % (sobject.get_id(), i) )

            if timecard != None:
                hours_wdg.set_value( timecard.get_value(i) )

            div = DivWdg()
            div.add_style("width: 50px")
            div.add_style("float: left")

            hours_wdg.set_id(name)
            hours_wdg.set_attr("size", "3")
            hours_wdg.add_event("onchange", "add(%s)" % sobject.get_id() )

            div.add( hours_wdg )

            widget.add(div)

        name = "timecard|total|%s" % sobject.get_id()
        total = SpanWdg()
        total.add( "0" )
        total.add_style("font-size: 1.2em")
        total.add_style("font-weight: bold")
        total.set_id(name)
        widget.add( " = " )
        widget.add( total )
        widget.add( " hours" )


        return widget


    def get_bottom(my):
        div = DivWdg()
        for day in ("mon","tue","wed","thu","fri","sat","sun"):
            total = DivWdg()
            total.set_id("timecard|total|%s" % day)
            total.add_style("width: 50px")
            total.add_style("float: left")
            total.add_style("font-size: 1.2em")
            total.add_style("font-weight: bold")
            total.add("0")

            div.add(total)

        return div
'''

class TimecardHourCmd(Callback):
     
    def __init__(my):
        super(TimecardHourCmd,my).__init__()
        my.search_key = None
        my.attr_name = None
        my.sobject = None
        my.value = None
        my.week = None
        my.year = None
        my.project_code = ''
    
    def get_title(my):
        return "TimecardHourCmd"


    def check(my):
        my.web = WebContainer.get_web()
        my.value = my.web.get_form_value('value')
        my.search_key =  my.web.get_form_value('search_key')
        my.attr_name =  my.web.get_form_value('attr_name')
        my.project_code =  my.web.get_form_value('project_code')
        if my.project_code:
            Project.set_project(my.project_code)

        keys = my.web.get_form_keys()
        for key in keys:
            if key.startswith('week_'):
                my.week = my.web.get_form_value(key)
                continue
        
            if key.startswith('year_'):
                my.year = my.web.get_form_value(key)
                continue

        if  not my.value or not my.attr_name or not my.week or not my.year:
            raise CommandExitException()
            
        return True

    def execute(my):
        if my.search_key: 
            search_type, search_id = my.search_key.split('|')
        
        timecard = Timecard.get(my.search_key, my.week, my.year)
        if not timecard:
            timecard = my._create_timecard(search_type, search_id)
        else:
            timecard = timecard[0]
       
        timecard.set_value(my.attr_name, my.value)
        # set week
        timecard.set_value('week', my.week)
        # set year
        timecard.set_value('year', my.year)
        
        timecard.commit()
            
        sobj = Search.get_by_search_key(my.search_key)
            
        my.description = "Set timecard %shr for [%s]"%(my.value, sobj.get_code())

    def _create_timecard(my, search_type, search_id):
        '''create an entry in the timecard table'''
        timecard = SObjectFactory.create("sthpw/timecard")
        timecard.set_value("search_type", search_type)
        timecard.set_value("search_id", search_id)
        timecard.set_value('login', Environment.get_user_name())
        timecard.set_value('project_code', Project.get_project_name()) 
        return timecard


class TimecardCmd(Command):

    def execute(my):

        web = WebContainer.get_web()
        if web.get_form_value("Register") == "":
            raise CommandExitException()



        # hard code this to tasks for now
        search_type = "sthpw/task"

        info = {}
        for key in web.get_form_keys():

            # filter out unwanted keys
            if not key.startswith("timecard|"):
                continue

            value = web.get_form_value(key)
            if value == "":
                continue

            tmp, search_id, col = key.split("|")
            if not info.has_key(search_id):
                info[search_id] = []

            info[search_id].append( (col,value) )


        for search_id, values in info.items():
            timecard = SObjectFactory.create("sthpw/timecard")
            timecard.set_value("search_type", search_type)
            timecard.set_value("search_id", search_id)

            for value in values:
                timecard.set_value(value[0],value[1])

            timecard.commit()



class TimecardInfoTableElement(BaseTableElementWdg):
    ''' Info about the time card '''

    def get_prefs(my):

        span = SpanWdg(css='med')
        my.select = FilterSelectWdg('timecard_view', label='View: ')
        my.select.set_option('values','compact|detailed')
        my.select.set_option('default', 'compact')
        span.add(my.select)
        return span

    def init(my):
        my.select = FilterSelectWdg('timecard_view', label='View: ')
        my.select.set_option('values','compact|detailed')
        my.select.set_option('default', 'compact')
        my.info_dict = {}
        my.is_preprocessed = False

    def preprocess(my):
        if not my.sobjects:
            return
       
        task_dict = {}
        misc_cards = []
        my.info_dict = {}
        for timecard in my.sobjects:
            if timecard.get_value('search_type') == Task.SEARCH_TYPE:
                task_dict[timecard.get_value('search_id')] = timecard.get_id()
            else:
                misc_cards.append(timecard)

        tasks = Search.get_by_id(Task.SEARCH_TYPE, task_dict.keys())
        if not tasks:
            return 
        for task in tasks:
            
            my.info_dict[ task_dict.get(task.get_id()) ] = task
        
        # store the rest of the timecards which do not have an associated task
        # or have association with some other sobjects (not implemented yet)
        for card in misc_cards:
            my.info_dict[card.get_id()] = card

    def get_display(my):
        if not my.is_preprocessed:
            my.preprocess()
            my.is_preprocessed = True

        card = my.get_current_sobject()
        div  = DivWdg()
        
        sobj = my.info_dict.get(card.get_id())
        if isinstance(sobj, Timecard):
            # add basic timecard info
            if sobj.get_value('search_type'):
                # this is still valid
                div.add("Timecard for [%s] is not implemented yet" %  sobj.get_value('search_type'))     
            else:
                div.add("General")
            return div
        elif isinstance(sobj, Task):
            # add task info
            if my.select.get_value() =='detailed':
                return my.get_detailed(sobj)
            else:
                return my.get_compact(sobj)
        
            
   
    def get_compact(my, sobj):
        table = Table(css='embed')
        col = table.add_col()
        col.add_style("width: 80px")
        table.add_col(css='med')
        table.add_col(css='large')
        table.add_style("width: 200px")
        table.add_row()
        
        src_sobj = sobj.get_parent()
        thumb = ThumbWdg()
        thumb.set_icon_size(40)
        thumb.set_sobject(src_sobj)
        table.add_cell(thumb)
        
        table.add_cell(src_sobj.get_code())
        table.add_data(SpanWdg(HtmlElement.b(sobj.get_process()), css='small'))
        #table.add_row()
        
        expand = ExpandableTextWdg()
        expand.set_max_length(20)
        desc = sobj.get_value("description")
        if not desc:
            desc = '&nbsp;'
        expand.set_value(desc)
        table.add_row_cell(expand)
        return table
        
    def get_detailed(my, sobj):
        table = Table(css='embed')
        table.add_style("width: 200px")
        col = table.add_col()
        col.add_style("width: 80px")
        table.add_col(css='large')
        table.add_col(css='large')

        src_sobj = sobj.get_parent()
        thumb = ThumbWdg()
        thumb.set_icon_size(40)
        thumb.set_sobject(src_sobj)
        table.add_row()
        td = table.add_cell(thumb)
        td.set_attr('rowspan','2')
        my._add_code(table, src_sobj)
        my._add_process(table, sobj)
        my._add_desc(table, sobj)

        return table
    
    def _add_code(my, table, sobj):
        
        table.add_cell(HtmlElement.i("%s Code: " % sobj.get_search_type_obj().get_title()))
        table.add_cell( HtmlElement.b(sobj.get_code()))

    def _add_process(my, table, sobj):
        table.add_row()
        table.add_cell(HtmlElement.i("Process: "))
        table.add_cell( sobj.get_value("process") )

    def _add_desc(my, table, sobj):
        tr = table.add_row()
        #tr.set_attr('colspan', '3') 
        table.add_cell(HtmlElement.i("Desc: "))
        expand = ExpandableTextWdg()
        expand.set_max_length(40)
        desc = sobj.get_value("description")
        if not desc:
            desc = '&nbsp;'
        expand.set_value(desc)
        td = table.add_cell( expand )
        td.set_attr('colspan', '2') 




class WeekHourInputWdg(CustomInfoInputWdg):
   
   
    def preprocess(my):
        sobject = my.get_current_sobject()
        my.day_list = []
        
        if sobject:
            year = sobject.get_value('year')
            week = sobject.get_value('week')
        if year and week:
            my.day_list = Calendar.get_monthday_time(year, week)
        


    def process_widget(my, idx, widget, sobject):
        ''' process each widget in the CustomInfoInputWdg''' 
        if not my.day_list:
            return
        
        today = Date()
        month, day, time = my.day_list[idx]
        if time > today.get_struct_time():
            widget.set_attr('readonly', 'readonly') 
            widget.add_class('disabled')

"""
class MilestoneTableElement(BaseTableElementWdg):

    TRIGGER = "set_milestone"
    CMD_INPUT = "milestone_cmd"
    BID_START_DATE = "bid_start_date"
    BID_END_DATE = "bid_end_date"
    ACTUAL_START_DATE = "actual_start_date"
    ACTUAL_END_DATE = "actual_end_date"
    
    def init(my):
        WebContainer.register_cmd("pyasm.widget.MilestoneSetCmd")
        
    def get_title(my):
        wdg = IconSubmitWdg(my.TRIGGER, icon=IconWdg.TABLE_UPDATE_ENTRY, long=True)
        wdg.set_text("Set Milestone")
        return wdg

    def get_input(my):
        return Container.get("MilestoneTableElement:" + my.CMD_INPUT)
        
    def store_input(my, value):
        hidden = my.get_input()
        if not hidden:
            Container.put("MilestoneTableElement:" + my.CMD_INPUT, [value])
        else:
            hidden.append(value)
            
    def get_display(my):

        table = Table()
        table.add_row()
        current_sobject = my.get_current_sobject()
        start_select = CalendarWdg(name=my.ACTUAL_START_DATE, id="%s|%s,%s" \
            % (my.name, my.ACTUAL_START_DATE, current_sobject.get_search_key() ))
        start_select.set_sobject(current_sobject)

        my.store_input(start_select.get_id())
        
        table.add_cell("Start: ")
        td = table.add_cell(start_select)
        td.add_style('white-space','nowrap')
        
        table.add_row()
        end_select = CalendarWdg(name=my.ACTUAL_END_DATE, id="%s|%s,%s" \
            % (my.name, my.ACTUAL_END_DATE, current_sobject.get_search_key() ))
        end_select.set_sobject(current_sobject)

        my.store_input(end_select.get_id())
        
        td2 = table.add_cell("End: ")
        td2.add_style('white-space','nowrap')
            
        widget = Widget()
        widget.add(end_select)
        table.add_cell(widget)
        
        # store all the input names in one hidden input
        if my.get_current_index() == len(my.sobjects) - 1:
            hidden_wdg = HiddenWdg(my.CMD_INPUT, ':'.join(my.get_input()) )
            widget.add(hidden_wdg)

        return table



class MilestoneWdg(Widget):
    
    def get_display(my):

        pipeline = Pipeline.get_by_name("shot")
        processes = pipeline.get_process_names()

        # get the users
        search = Search("sthpw/login")
        users = search.get_sobjects()
        user_labels = [user.get_full_name() for user in users]
        user_values = [user.get_value("login") for user in users]

        table = Table()
        table.set_style("minimal")
        table.add_row()
        table.add_header("Process")
        table.add_header("Artist")
        table.add_header("Start Date")
        table.add_header("End Date")
        for process in processes:
            table.add_row()

            table.add_cell(process)

            user_select = SelectWdg("%s|user" % process )
            user_select.set_option("values", user_values)
            user_select.set_option("labels", user_labels)
            user_select.add_empty_option()
            table.add_cell(user_select)

            start_select = CalendarWdg("%s|start_select" % process )
            end_select = CalendarWdg("%s|end_select" % process )

            table.add_cell(start_select)
            table.add_cell(end_select)

        return table




class MilestoneSetCmd(Command):
    
    NONE_VAL = '__NONE__'

    def get_title(my):
        return MilestoneTableElement.TRIGGER


    def check(my):
        web = WebContainer.get_web()
        if web.get_form_value(MilestoneTableElement.TRIGGER) != "":
            return True

    def execute(my):

        web = WebContainer.get_web()
        
        # get the input names
        input_names = web.get_form_value(MilestoneTableElement.CMD_INPUT).split(':')
               
        for input_name in input_names:
            value = web.get_form_value(input_name)
            if value != my.NONE_VAL:
                if MilestoneTableElement.ACTUAL_START_DATE in input_name:
                    my.store(input_name.split(',')[1], 'actual_start_date', \
                        web.get_form_value(input_name))
                elif MilestoneTableElement.ACTUAL_END_DATE in input_name:
                    my.store(input_name.split(',')[1], 'actual_end_date', \
                        web.get_form_value(input_name))
            
      
    def store(my, key, column, value):
        ''' commit the values ''' 
        sobject = Search.get_by_search_key(key)
        sobject.set_value(column, value )
        
        update_column = 'timestamp'
        
        sobject.set_value(update_column, Sql.get_timestamp_now(), quoted=False)
        sobject.commit()


"""


