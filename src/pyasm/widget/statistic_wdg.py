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

__all__ = ['TaskCompletionWdg', 'CompletionBarWdg', 'CalendarBarWdg', 'CalendarSetCmd', 'TaskGroupCompletionWdg']

from pyasm.common import Date, Calendar, Common, jsonloads
from pyasm.search import *
from pyasm.web import *
from pyasm.biz import *
from pyasm.widget import FilterSelectWdg, FilterCheckboxWdg, IconButtonWdg, IconWdg

from input_wdg import HiddenWdg, CalendarInputWdg
from layout_wdg import TableWdg

import datetime, re
from pyasm.widget import BaseTableElementWdg
#from tactic.ui.common import BaseTableElementWdg

'''DEPRECATED: use the one in tactic.ui.table.TaskCompletionWdg'''
class TaskCompletionWdg(BaseTableElementWdg):

    def init(my):
        my.is_preprocessed = False
        my.data = {}
        my.cal_sub_task = None
        my.cal_sub_task_value = False


    def preprocess(my):
        my.total_completion = 0.0
        my.num_sobjects = 0
        if my.sobjects:
            tasks = Task.get_by_sobjects(my.sobjects)
            # create a data structure
            for task in tasks:
                search_type = task.get_value("search_type")
                search_id = task.get_value("search_id")
                search_key = SearchKey.build_search_key(search_type, search_id, column='id')
                sobject_tasks = my.data.get(search_key)
                if not sobject_tasks:
                    sobject_tasks = []
                    my.data[search_key] = sobject_tasks

                sobject_tasks.append(task)
        my.is_preprocessed = True

    def get_prefs(my):
        my.cal_sub_task = FilterCheckboxWdg('calculate_sub_task', \
            label='include sub tasks', css='small')
        my.cal_sub_task_value = my.cal_sub_task.is_checked()
        return my.cal_sub_task

    def get_width(my):
        '''not used I think'''
        width = my.kwargs.get("width")

        if not width:
            width = 400
        return int(width)

    def get_text_value(my):
        if not my.is_preprocessed:
            my.preprocess()
        sobject = my.get_current_sobject()
        completion = my.get_completion(sobject)
        if not completion:
            completion = 0
        return "%0.1d%%" % completion

    def get_display(my):
        sobject = my.get_current_sobject()
        completion = my.get_completion(sobject)
        
        # completion is compared to None, because a 0% completion is valid
        if completion == None:
            div = DivWdg("<i>No tasks</i>")
            div.add_style("color: #aaa")
            return div

        widget = DivWdg()
        width = my.get_width()
        bar_wdg = CompletionBarWdg(completion, width )
        widget.add(bar_wdg)

        # keep a running tab of the total
        my.total_completion += completion
        my.num_sobjects += 1
        
        return widget


    def get_bottom_wdg(my):
        width = my.get_width()
        
        if my.num_sobjects:
            completion = my.total_completion / my.num_sobjects
            bar_wdg = CompletionBarWdg(completion, width)
        else:
            bar_wdg = "n/a"
        div = DivWdg()
        div.add("Total")
        div.add("<hr>")
        
        div.add(bar_wdg)
        return div


    def get_tasks(my, sobject):
        ''' if the sobject is a task, then just return the sobject, since tasks
         do not have tasks. Account for subtask based on preferences. Also
         filters out tasks belonging to obsolete processes'''
        if isinstance(sobject, Task):
            return [sobject]
        
        tasks = my.data.get( SearchKey.get_by_sobject(sobject, use_id=True) )
        if tasks == None:
            tasks = Task.get_by_sobjects([sobject])
        # make sure we only take tasks in the pipeline into account

        pipeline = Pipeline.get_by_sobject(sobject)
        recurse = False
        if my.cal_sub_task_value:
            recurse = True
        if pipeline:
            processes = pipeline.get_process_names(recurse=recurse)

            filtered_tasks = []
            for task in tasks:
                if task.get_value("process") not in processes:
                    continue
                filtered_tasks.append(task)

            return filtered_tasks

        else:
            return tasks




    def get_completion(my, sobject):
        my.tasks = my.get_tasks(sobject)

        percent = 0
        # count the tasks with invalid or obsolete status
        #invalid_count = 0
        for task in my.tasks:
            status_attr = task.get_attr("status")
            task_percent = status_attr.get_percent_completion()
            if task_percent < 0:
                task_percent = 0
                #invalid_count += 1
            percent += task_percent

        if my.tasks:
            # NOT sure if I should subtract total # of tasks by invalid
            # task, leave it for now
            percent = int(percent / len(my.tasks))
        else:
            return None

        return percent

    def handle_td(my, td):
        td.add_style('vertical-align','middle')
        sobject = my.get_current_sobject()
        completion = my.get_completion(sobject)
        td.add_attr("spt_input_value", completion)



class TaskGroupCompletionWdg(TaskCompletionWdg):

    ARGS_KEYS = {
        'options': {
            'type': 'TextAreaWdg',
            'description': 'A list of options for the various completion bars. e.g. [{"label":"MODEL", "context": ["model","rig"]}] '
        },

    }
    def preprocess(my):
        my.options = my.get_option('options')
        if my.options:
            try:
                my.group_list = jsonloads(my.options)
            except:
                my.group_list = [{'label': 'Syntax Error', 'context':[]}]
        else:
            my.group_list = [{'label':'default', 'context': []}]

        super(TaskGroupCompletionWdg, my).preprocess()

    def init(my):
        # these 2 are used for bottom summary
        my.total_completion_dict = {}
        my.num_sobjects = 0
        super(TaskGroupCompletionWdg, my).init()

    def get_bottom_wdg(my):
        if my.total_completion_dict:
            table = Table()
            col = table.add_col()
            col = table.add_col()
            col.add_style('width','80%')
            for group in my.group_list:
                group_label = group.get('label')
                completion = my.total_completion_dict.get(group_label)/ my.num_sobjects
            
                group_contexts = group.get('context')
                if group_contexts:
                    group_contexts = ', '.join(group_contexts)


                width = my.get_width()
                bar_wdg = CompletionBarWdg(completion, width)
                label_div = FloatDivWdg('%s: ' %group_label)
                label_div.add_style('margin-right: 4px')
                label_div.add_tip(group_contexts, group_contexts)
                table.add_row()
                table.add_cell(label_div)
                table.add_cell(bar_wdg)
            return table

        width = my.get_width()
        completion = 0
        if my.num_sobjects:
            completion = my.total_completion / my.num_sobjects
        div = DivWdg()
        div.add("Total")
        div.add("<hr>")
        bar_wdg = CompletionBarWdg(completion, width)
        div.add(bar_wdg)
        return div
    
    def get_group_completion(my, items):
        '''get the avg completion'''
        sum = 0
        if not items:
            return 0
        for item in items:
            sum += item
        avg = sum / len(items)
        return avg

    def get_text_value(my):
        sobject = my.get_current_sobject()
        if sobject.get_id() == -1:
            return ''
        my.calculate(sobject)

        output = []
        for group in my.group_list:
            group_label = group.get('label')
            group_contexts = group.get('context')
            if group_contexts:
                group_contexts = ', '.join(group_contexts)
            group_completion = my.completion_dict.get(group_label)
            completion = my.get_group_completion(group_completion)
            output.append('%s: %s%%'%(group_label, completion))

        return '\n'.join(output)

    def calculate(my, sobject):
        '''do the calculation'''
        tasks = my.get_tasks(sobject)


        completion = '' 
        my.completion_dict = {}
        for group in my.group_list:
            group_label = group.get('label')
            group_contexts = group.get('context')
            if not group_label:
                continue
            for task in tasks:
                context = task.get_value('context')
                if context in group_contexts:
                    completion = my.get_completion(task)
                    group_completion = my.completion_dict.get(group_label)
                    if group_completion == None:
                        my.completion_dict[group_label] = [completion]
                    else:
                        group_completion.append(completion)

    def get_display(my):
        sobject = my.get_current_sobject()
        if sobject.get_id() == -1:
            return ''
        my.calculate(sobject)
        
             
        # completion is compared to None, because a 0% completion is valid
        if not my.completion_dict:
            if my.group_list and my.group_list[0].get('label')=='Syntax Error':
                div = DivWdg("<i>Syntax Error in Column Definition</i>")
            elif my.group_list and my.group_list[0].get('label')=='default':
                div = DivWdg("<i>Fill in the options e.g. [{'label':'MODEL', 'context': ['model','rig']}] </i>")
            else:
                div = DivWdg("<i>No tasks</i>")
            div.add_style("color: #aaa")
            return div

        table = Table()
        col = table.add_col()
        col = table.add_col()
        col.add_style('width','80%')
        for group in my.group_list:
            group_label = group.get('label')
            group_contexts = group.get('context')
            if group_contexts:
                group_contexts = ', '.join(group_contexts)
            group_completion = my.completion_dict.get(group_label)
            completion = my.get_group_completion(group_completion)


            width = my.get_width()
            bar_wdg = CompletionBarWdg(completion, width)
            label_div = FloatDivWdg('%s: ' %group_label)
            label_div.add_style('margin-right: 4px')
            label_div.add_tip(group_contexts, group_contexts)
            table.add_row()
            table.add_cell(label_div)
            table.add_cell(bar_wdg)
            #widget.add(HtmlElement.br())
            completed_summary = my.total_completion_dict.get(group_label)
            if not completed_summary:
                completed_summary = 0
	    my.total_completion_dict[group_label] = completion + completed_summary
        my.num_sobjects += 1

        return table


class CompletionBarWdg(DivWdg):

    def __init__(my, percent, length):
        if not percent:
            percent = 0
        my.percent = percent
        #my.percent = 100
        my.length = length
        super(CompletionBarWdg, my).__init__()

    def init(my):
        #my.add_style("width", my.length + 50)
        my.add_style("font-size", "0.8em")

        width = int(my.length*(float(my.percent)/100))
        if width == 0:
            width = 1

        percent_str = HtmlElement.span("%s%%&nbsp" % my.percent )
        percent_str.add_style("float: right")
        percent_str.add_style("color: white")

        bar = FloatDivWdg()
        bar.add("&nbsp;")
        #bar.add_style("width", width)
        bar.add_style("width", "%s%%" % (70*my.percent/100))
        bar.add_style("border: 1px solid #aaa")
        color_code = my._get_color_code(my.percent)
        bar.add_class("completion %s" % my._get_bar_color_code(my.percent) )
        bar.add_style("background-color", color_code)
        bar.add_style("float", "left")

        my.add(bar)
        percent = FloatDivWdg("%0.1f%%" % my.percent, css='larger')
        percent.add_style('padding', '2px 0 0 4px')
        my.add( percent )



    def _get_bar_color_code(my, percent):
        ''' get a color code based on percentage of task completion '''
        color = "grey"
        if percent == 100:
            color = "green"
        elif percent >= 80:
            color = "blue"
        elif percent >= 40:
            color = "yellow"
        elif percent >= 20:
            color = "red"
        return color


    def _get_color_code(my, percent):
        ''' get a color code based on percentage of task completion '''
        color = "#ddd"
        if percent == 100:
            color = "#b5e868"
        elif percent > 80:
            color = "#b5e868"
        elif percent > 50:
            color = "#e8e268"
        elif percent > 30:
            color = "#e8c268"
        elif percent > 10:
            color = "#e86868"
        return color


class CalendarBarWdg(BaseTableElementWdg):
    MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    LEFT_MARGIN = 60
    CAL_INPUT = "calendar"

    def __init__(my):
        my.calendar = None
        my.always_recal = False
        my.user_defined_bound = True
        my.show_days = False
        my.valid_date = True
        my.statuses = {}

        super(CalendarBarWdg, my).__init__()


    def get_text_value(my):
        sobject = my.get_current_sobject()

        """
        start_value = sobject.get_value("bid_start_date")
        end_value = sobject.get_value("bid_end_date")
        if start_value:
            start = Date(start_value)
            start_display = start.get_display_date()
        else:
            start_display = ""

        if end_value:
            end = Date(end_value)
            end_display = end.get_display_date()
        else:
            end_display = ""

        return "%s - %s" % (start_display, end_display)
        """


        start_date = sobject.get_value("bid_start_date")
        start = ''
        end = ''
        if start_date:
            start = Date(start_date).get_display_date()
        end_date = sobject.get_value("bid_end_date")
        
        if end_date:
            end = Date(end_date).get_display_date()
        # if bid end date does not exist, try bid duration
        if start_date != "" and end_date == "":
            bid_duration = sobject.get_value("bid_duration")
            if bid_duration != "":
                date = Date(start_date)
                date.add_days(bid_duration)
                end_date = date.get_db_time()
                end = Date(end_date).get_display_date()

        return "%s - %s" % (start, end)



  
    def get_info(my):
        # when used strictly as a BaseTableElement, there is no need to recalculate
        if not my.always_recal and hasattr(my, "start_year") and hasattr(my, "end_year"):
            return

        # create the calendar only if it is needed
        # create only if necessary since the on script is linked to the
        # cal_name of the CalendarInputWdg
        if not my.calendar:
            my.calendar = CalendarInputWdg(my.CAL_INPUT)
            my.calendar.set_show_on_wdg(False)
            my.calendar.set_show_value(False)
        # if this is in ajax, then try to recreate the widget
        web = WebContainer.get_web()


        # TODO: this code should be put into an ajax class
        ajax_class = web.get_form_value("widget")
        my.is_ajax = False
        is_tbody_swap = False

        if ajax_class and web.get_form_value("ajax") == "true":
            from pyasm.common import Common
            module, class_name = Common.breakup_class_path(ajax_class)

            if class_name == my.__class__.__name__:
                my.is_ajax = True
            elif class_name == 'TbodyWdg':
                is_tbody_swap = True

        if my.is_ajax:
            search_key = web.get_form_value("search_key")
            sobject = Search.get_by_search_key(search_key)
            my.set_sobject(sobject)
            my.actual_edit = web.get_form_value("actual_edit")
            my.bid_edit = web.get_form_value("bid_edit")
            
            my.start_year = web.get_int_form_value("start_year")
            my.end_year = web.get_int_form_value("end_year")
            my.start_month = web.get_int_form_value("start_month")
            my.end_month = web.get_int_form_value("end_month")
            my.width = web.get_int_form_value("calendar_width")
            my.cal_margin = web.get_int_form_value("calendar_margin")
        else:
            my.bid_edit = my.get_option("bid_edit")
            my.actual_edit = my.get_option("actual_edit")
            my.width = my.get_option("width")
            
            if my.width == "":
                my.width = 400
            else:
                my.width = int(my.width)

            my.cal_margin = my.get_option("cal_margin")
            if not my.cal_margin:
                my.cal_margin = 1
            else:     
                my.cal_margin = int(my.cal_margin)

            # determine date ranges
            start_date = None
            end_date = None
            for sobject in my.sobjects:
                bid_start_date = str(sobject.get_value("bid_start_date"))
                if bid_start_date != "":
                    if not start_date or bid_start_date < start_date:
                        start_date = bid_start_date

                actual_start_date = str(sobject.get_value("actual_start_date",no_exception=True))
                if actual_start_date != "":
                    if actual_start_date < start_date:
                        start_date = actual_start_date
                
                bid_end_date = sobject.get_value("bid_end_date")

                # if bid end date does not exist, try bid duration
                if bid_start_date != "" and bid_end_date == "":
                    bid_duration = sobject.get_value("bid_duration")
                    if bid_duration != "":
                        date = Date(bid_start_date)
                        date.add_days(bid_duration)
                        bid_end_date = date.get_db_time()

                if bid_end_date:
                    # necessary to check for None end_date
                    if not end_date or str(bid_end_date) > str(end_date):
                        end_date = bid_end_date

                actual_end_date = sobject.get_value("actual_end_date",no_exception=True)
                if actual_end_date:
                    if str(actual_end_date) > str(end_date):
                        end_date = actual_end_date
            
                
            if start_date and end_date and my.sobjects:
                
                start_date, time = str(start_date).split(" ")
                my.start_year, my.start_month, tmp = [int(x) for x in start_date.split("-")]
                end_date, time = str(end_date).split(" ")
                my.end_year, my.end_month, tmp = [int(x) for x in end_date.split("-")]

            else:
                my.start_year = datetime.date.today().year
                my.start_month = 1

                my.end_year = datetime.date.today().year
                my.end_month = 12

            # the calendar boundaries can be overriden thru the left/right arrows control
            # this is not needed when it is part of the SObjectTaskTableElement
            if my.user_defined_bound:
                my.left_bound_hid = HiddenWdg('cal_left_control_hid')
                my.left_bound_hid.set_persistence()
                my.right_bound_hid = HiddenWdg('cal_right_control_hid')
                my.right_bound_hid.set_persistence()
                my.week_hid_wdg = HiddenWdg('cal_week_hid')
                 
                left_bound = my.left_bound_hid.get_value()
                right_bound = my.right_bound_hid.get_value()
                if left_bound and re.match(r'\d{4}:\w{3}', left_bound):
                    left_bound = left_bound.split(':')
                    my.start_year = int(left_bound[0])
                    my.start_month = my.MONTHS.index(left_bound[1]) + 1
                if right_bound and re.match(r'\d{4}:\w{3}', right_bound):
                    right_bound = right_bound.split(':')
                    my.end_year = int(right_bound[0])
                    my.end_month = my.MONTHS.index(right_bound[1]) + 1
       
        # determine the month range for tbody swap
        if is_tbody_swap:
            month_info = web.get_form_value('months_info')
            my.num_months, my.first_month, my.left_year_bound = month_info.split(':') 
            my.num_months = int(my.num_months)
            my.left_year_bound = int(my.left_year_bound)
            return 
     
        my.week_hid = web.get_int_form_value("cal_week_hid")
        # my.months store a list of (month, year) names to be drawn at the title area
        my.months = []
        left_month_bound = my.start_month - 1 - my.cal_margin
        right_month_bound = my.end_month -1 + my.cal_margin
       
        # my.start_year is preserved for ajax while my.left_year_bound
        # is recalulated every time
        my.left_year_bound =  my.start_year
        my.right_year_bound = my.end_year + 1
        while left_month_bound < 0:
            left_month_bound += 12
            my.left_year_bound -= 1
        
        while right_month_bound > 11:
            right_month_bound -= 12
            my.right_year_bound += 1

        for year in range(my.left_year_bound, my.right_year_bound):
            
            for i in range(left_month_bound, len(CalendarBarWdg.MONTHS)):
                month = CalendarBarWdg.MONTHS[i]
                my.months.append((month, year))
                if year == my.right_year_bound - 1 and i >= right_month_bound:
                    break
                

            # reset month index
            left_month_bound = 0

        # prepare values used for calculating the bar width and start position
        # my.left_year_bound above is one of them
        if not my.months:
            for i in range(0,11):
                my.months.append((CalendarBarWdg.MONTHS[i],2007))
        my.num_months = len(my.months)
        my.first_month = my.months[0][0] 

    def get_prefs(my):
        span = SpanWdg("width: ", css="med")
        my.width_select = FilterSelectWdg("calendar_width")
        my.width_select.set_option("values", "200|400|620|800|1000")
        my.width_select.add_empty_option("default")

        value = my.width_select.get_value()
        if value != "":
            my.set_option("width", value)
           
        
        span.add(my.width_select)
        span.add("px")

       
        span2 = SpanWdg("margin: ", css='med')
        my.margin_select = FilterSelectWdg("calendar_margin")
        my.margin_select.set_option("values", "0|1|2|3|4")

        value = my.margin_select.get_value()
        if value != "":
            my.set_option("cal_margin", value)
        span2.add(my.margin_select)
        span2.add('months')
        span.add(span2)


        pref_show_day = FilterCheckboxWdg('show_days', label='Show days')
        if pref_show_day.get_value():
            my.show_days = True

        span.add(pref_show_day)
        return span

        
    def get_calendar(my):
        '''this can be called to return a crucial component for this 
        widget to function if not used directly as a BaseTableElement'''
        my.get_info()
        widget = Widget() 
        hidden = HiddenWdg("calendar_column", "")
        widget.add(hidden)
        widget.add(my.calendar)
        return widget

    def set_always_recal(my, recal):
        my.always_recal = recal
    
    def set_user_defined_bound(my, bound):
        my.user_defined_bound = bound

    def _get_control_div(my, control_id, other_control_id, control_hidden, other_control_hidden,\
            bound):
        ''' get a control div to set the range of calendar to display '''
        left_div = FloatDivWdg(width =my.LEFT_MARGIN, css='center_content')
        
        left_div.add(control_hidden)
        control_name = control_hidden.get_input_name()
        other_control_name = other_control_hidden.get_input_name()

        left_bound_val = control_hidden.get_value()
        if not left_bound_val:
            default_value = ''
            if bound == 'left':
                default_value = '%s:%s' %(my.months[0][1], my.months[0][0])
            else:
                default_value = '%s:%s' %(my.months[-1][1], my.months[-1][0])
            left_bound_val = default_value

        left_info = DivWdg(left_bound_val, id=control_id, css='hand')
        left_info.add_class("calendar_nav")
        left_info.add_event('onclick', 'document.form.submit()')
        left_div.add(left_info)
        icon = IconButtonWdg(name='prev month', icon=IconWdg.ARROW_LEFT)
        icon.add_event('onclick', "TacticCalendarLabel.update_range('%s', '%s', '%s', '%s', 'backward', '%s')" \
            %(control_id, other_control_id, control_name, other_control_name, bound)) 
        left_div.add(icon)
        
        icon = IconButtonWdg(name='next month', icon=IconWdg.ARROW_RIGHT)
        icon.add_event('onclick', "TacticCalendarLabel.update_range('%s', '%s', '%s', '%s', 'forward', '%s')" \
            %(control_id, other_control_id, control_name, other_control_name, bound))

        left_div.add(icon)

        return left_div

    def get_title(my):
        # initialtize
        my.get_info() 
        
        # division round out error, 3px
        margin_error = 3.0

        main_div = FloatDivWdg()
       
        main_width = my.width + (my.LEFT_MARGIN * 2) + margin_error
        main_div.add_style("width", main_width)

        # add the left control
        left_div = my._get_control_div('cal_left_control_id', 'cal_right_control_id', \
            my.left_bound_hid, my.right_bound_hid, 'left')
       
        main_div.add(my.week_hid_wdg)
        main_div.add(left_div)
        
        # create the calendar label area
        div = FloatDivWdg(id='cal_label_area')

        # this width seems irrelevant
        
        div.add_style("width", my.width + margin_error)
        div.add_style("font-size: 0.8em")
        main_div.add(div)
        # write some hidden calendar info
        div.add(my.get_calendar())

        # add the right control
        right_div = my._get_control_div('cal_right_control_id', 'cal_left_control_id',\
            my.right_bound_hid, my.left_bound_hid, 'right')

        main_div.add(right_div)

        # months_info is used for remembering what the calendar range is like
        # for tbody replacement
        div.add(HiddenWdg('months_info', '%s:%s:%s' \
            %(my.num_months, my.first_month, my.left_year_bound)))

        # draw year divs container
        year_main_div = Widget()
        #year_main_div.add_stylcal_right_control_ide('width', my.width + margin_error)
        div.add(year_main_div)


        div.add(HtmlElement.br())
   
        # this is less stringent and different from my.is_ajax which is 
        # used when the CalendarBarWdg is updated
        is_ajax = CalendarBarWdg.is_ajax(check_name=False)
        # draw months 
        year_widths = []
        year_width = 0

        # NOTE: my.months is a list of tuple (month, year)
        last_year = my.months[0][1]
        for idx, month in enumerate(my.months):
            
            year = month[1]

            # accurate decimals are necessary
            month_width = '%.2f' %(float(my.width)/my.num_months)
            month_width = float(month_width)

            # collect the required year_div's width for later
            if year != last_year: 
                last_year = year
                year_widths.append(year_width)
                year_width = 0 

            if idx == len(my.months) - 1:
                year_width += float(month_width)
                year_widths.append(year_width)

            month_id = '%s_%s' %(year, month[0])
            label = SpanWdg(month[0], id = month_id, css='label_out')
            label.add_event('onmouseover',"Effects.color('%s','label_over')" %month_id)
            label.add_event('onmouseout',"Effects.color('%s','label_out')" %month_id)
            month_span = FloatDivWdg(label)
             
            year_width += month_width
                
            month_span.add_event('onclick', "var x=get_elements('week_filter'); if(x) x.set_value('')")
            month_span.add_event("onclick", "get_elements('cal_left_control_hid').set_value('%s:%s');get_elements('cal_right_control_hid').set_value('%s:%s');document.form.submit()" % (year,month[0], year, month[0]) )
            month_span.add_class("hand")

            # add a little bit more space using part of the margin_error
            month_span.add_style("width: %.1fpx" % (month_width + margin_error/len(my.months)/4))
            month_span.add_style("float: left")
            month_span.add_style("text-align: center")
            
            if idx % 2 == 0:
                month_span.add_class("calendar_month_even")
            else:
                month_span.add_class("calendar_month_odd")
                
            
            # draw weeks, days only if the user has chosen a very narrow boundary
            if my.num_months <= 2 or my.show_days: 
                my._draw_weeks(month_span, month_width, month, idx)
            if my.num_months == 1 or (my.num_months == 2 and my.width >= 800)\
                or my.show_days:
                    my._draw_days(month_span, month_width, month, idx)
            div.add(month_span)

            # add divider
            if not is_ajax:
                divider = my._get_divider(idx * float(my.width)/my.num_months)
                div.add(divider)
        
        # add individual year div back into year_main_div
        year_index = 0
        for year in xrange(my.left_year_bound, my.right_year_bound):

            year_span = SpanWdg(year)

            year_div = FloatDivWdg(year_span, css='center_content',\
                    width=year_widths[year_index])
            year_div.add_event('onclick', "var x=get_elements('week_filter'); if(x) x.set_value('')")
            year_div.add_event("onclick", "get_elements('cal_left_control_hid').set_value('%s:Jan');get_elements('cal_right_control_hid').set_value('%s:Dec');document.form.submit()" % (year,year) )
            year_div.add_class("hand")
            if year % 2 == 0:
                year_div.add_class("calendar_year_even")
            else:
                year_div.add_class("calendar_year_odd")

            
            year_main_div.add(year_div)
            year_index += 1

        # add the last divider
        if not is_ajax:
            divider = my._get_divider(my.width)
            div.add(divider)
        # readjust the lines on load both vertically and horizontally
        ref_table_id = my.parent_wdg.table.get_id()
        y_offset = 30
        
        AppServer.add_onload_script("TacticCalendarLabel.realign('calendar_divider','cal_label_area',"\
          "'%s', %s)" %(ref_table_id, y_offset))
        
        
        script = my.get_show_cal_script()
        main_div.add(script)
        return main_div
   
    def get_show_cal_script(my):
        script = HtmlElement.script('''
        function show_task_cal(input_name, element, date_string, column, script ) {
            get_elements('calendar_column').set_value(column);
            calendar_tactic.show_calendar(input_name, element, date_string)
            calendar_tactic.cal.onClose = function() { if (!calendar_tactic.check(input_name)) return; eval(script)  }
        }
        ''') 
        return script

    def _get_divider(my, left_pos, css='calendar_divider'):
        '''get divider for each week'''
        inside = DivWdg(css=css)
        #inside.set_attr('name', 'cal_divider')
        inside.add_style("position: absolute")
        inside.add_style("float: left")
        inside.add_style("border-style: dashed")
        inside.add_style("border-width: 0px 1px 0px 0px")
        inside.add_style("height: 100%")

        inside.add_style("width: 1px" )
        inside.add_style("left: %spx" %left_pos )
        return inside


    def _get_month_days(my, year, week):
        num_days_list = Calendar.get_monthday_time(year, week, month_digit=True)
        
        month_days = [ (int(i[0]), int(i[1])) for i in num_days_list ]
        return month_days

    def _draw_weeks(my, div, width, monthyear, month_idx):
        month, year = monthyear[0], monthyear[1]
        month_digit = CalendarBarWdg.MONTHS.index(month) + 1
        week_width_list = [] 
        week_width = 0.0
  
        num_days = Calendar.get_num_days(year, month_digit)
        
        week = my.week_hid
       
        db_date = '%s-%s-01' %(year, month_digit)
        date = Date(db_date=db_date)
        current_week = date.get_week()
        day_width = float(width) / num_days
        if week:
            week_width_list.append((week, width))
        else:
            last_date = db_date
            append_extra = False
            for day in xrange(1, num_days+1):
                if current_week != date.get_week():
                    week_width_list.append((current_week, week_width))
                    current_week = date.get_week()
                    week_width = 0.0
               
                date.add_days(1)
                # BUG: To circumvent a bug, it doesn't work on 2007-11-04
                if date.get_db_date() == last_date:
                    last_date = date.get_db_date()
                    append_extra = True
                    continue
                week_width += day_width
                last_date = date.get_db_date()
            # last week
            if append_extra:
                week_width += day_width
            week_width_list.append((current_week, week_width))
        
        for week, week_width in week_width_list:
            week_div = FloatDivWdg(week, width = week_width, css='calendar_week_out')
            week_id = 'cal_week_%s'%week
            week_div.set_id(week_id)
            week_div.add_event('onclick', "get_elements('cal_week_hid').set_value('%s')" % week)
            week_div.add_event('onclick', "var x =get_elements('week_filter'); if(x) x.set_value('')")
            week_div.add_event('onmouseover',"Effects.css_morph('%s','calendar_week_over')" %week_id)
            week_div.add_event('onmouseout',"Effects.css_morph('%s','calendar_week_out')" %week_id)

            div.add(week_div)

        div.add(HtmlElement.br())

    def _draw_days(my, div, width, monthyear, month_idx):
        '''draw the days for each month'''
        div.add(HtmlElement.br())
        month, year = monthyear[0], monthyear[1]
        month_digit = CalendarBarWdg.MONTHS.index(month) + 1
        
        num_days = Calendar.get_num_days(year, month_digit)
        day_range =  xrange(1, num_days + 1)
        week = my.week_hid
        if week:
            # handle the cross-year scenario
            if int(week) == 1 and month_digit == 12:
                year += 1
            num_days_list = Calendar.get_monthday_time(year, week)
            month_days = my._get_month_days(year, week)
            day_range = month_days
        for day in day_range:
            if isinstance(day, tuple):
                month_digit, day = day[0], day[1]
            weekday = Calendar.get_weekday(year, month_digit, day)
            # show every day 
            # add divider for days
            #divider = my._get_divider(day, float(width) / num_days)
            #div.add(divider)

            # show divider every week
            if weekday == 6 and not week:
                left_pos = float(width) / len(day_range) * day + width * month_idx
                divider = my._get_divider( left_pos )
                div.add(divider)
            
            day_div = FloatDivWdg(day, css='smaller')
            # grey out weekends
            if weekday > 4:
                day_div.add_style('background', '#bbb')

            # try to get up to 2 decimal point for the width
            day_div.add_style('width', '%.2fpx' %(width / len(day_range)))

            font_size = int(width/num_days*0.75)
            if font_size > 10:
                font_size = 10
            day_div.add_style('font-size: %spx' % font_size )

            div.add(day_div)

    def get_display(my):
        # TODO: configure a different color for a different login
        color = "orange"
        my.get_info()
        sobject = my.get_current_sobject()

        # this changes depending on whether it is in ajax mode
        div = None

        if not my.is_ajax:
            div = DivWdg()
            if my.user_defined_bound:
                div.add_style('margin-left', my.LEFT_MARGIN)
            div.set_id("calendar_range_%s" % sobject.get_id() )
            div.add_style("display: block")
        else:
            div = Widget()
            div.add(HiddenWdg('cal_week_hid', my.week_hid))

        # until "hsl(120, 50%, 50%)" is supprted by all browsers, use literal color names
        div1 = my.get_date_range_wdg("bid_start_date", "bid_end_date", color)
        if not div1:
            span = SpanWdg("<i>No Dates Set</i>")
            span.add_class("cal_in_bound")
            div.add(span)
            return div

        div.add(div1)
        if not my.valid_date:
            msg = HtmlElement.blink('invalid')
            msg.add_style('color', 'red')
            msg.add_class('small')
            div.add(SpanWdg(msg, css='small'))
            # reset it
            my.valid_date = True

        if my.get_option("actual_display") == "true":
            div.add(HtmlElement.br())
            div.add(my.get_status_history_wdg(sobject))

        if my.get_option("checkin_display") == "true":
            div.add(HtmlElement.br())
            div.add(my.get_checkin_history_wdg(sobject))

        return div



    def get_date_range_wdg(my,start_date_col,end_date_col,color):

        if start_date_col == "bid_start_date":
            type = "bid"
        else:
            type = "actual"

        edit = True
        if eval("my.%s_edit" % type)== "false":
            edit = False
        sobject = my.get_current_sobject()

        start_date = sobject.get_value(start_date_col)
        end_date = sobject.get_value(end_date_col)

        if end_date and str(start_date) > str(end_date):
            my.valid_date = False
        # determine dependency: not very efficient!!!
        if my.get_option("dependent_display") == "true":
            is_dependent = sobject.get_value("depend_id")
            has_dependents = False
            for tmp_sobj in my.sobjects:
                if tmp_sobj == sobject:
                    continue
                if tmp_sobj.get_value("depend_id") == sobject.get_id():
                    has_dependents = True
                    break
        else:
            is_dependent = False
            has_dependents = False
        



        # special case for the value of bid_end_date, we can use duration
        if type == "bid" and start_date == "":
            bid_duration = sobject.get_value("bid_duration")
            if bid_duration != "":
                div = DivWdg("%s days" % bid_duration)
                return div

        if type == "bid" and end_date == "":
            bid_duration = sobject.get_value("bid_duration")
            if bid_duration != "":
                bid_start_date = sobject.get_value("bid_start_date")
                if bid_start_date != "":
                    date = Date(db=bid_start_date)
                    date.add_days(bid_duration)
                    end_date = date.get_db_time()




        # handle cases where there are no dates or dates missing
        no_label_flag = False
        if start_date == "" and end_date == "":
            if not edit:
                return None
            
            # get today's date
            date = Date()
            start_date = date.get_db_time()
            end_date = date.get_db_time()
            no_label_flag = True

        elif start_date == "":
            start_date = end_date

        elif end_date == "":
            end_date = start_date

        # this conversion is needed for the js calenadar
        start_date, time = str(start_date).split(" ")
        end_date, time = str(end_date).split(" ")

        info = my.calculate_widths(start_date, end_date)
        start_width, end_width = info.get('width')
        s_month_label, s_day = info.get('s_label')
        e_month_label, e_day = info.get('e_label')

        # create the labels
        if no_label_flag:
            start_width = int(my.width / 2)
            end_width = int(my.width / 2)
            start_label = SpanWdg("---&nbsp;")
            start_label.set_class("cal_in_bound")
            end_label = SpanWdg("&nbsp;---")
            end_label.set_class("cal_in_bound")
        else:
            start_label = SpanWdg("%s-%s&nbsp;" %(s_month_label, s_day))
            start_label.set_class("cal_in_bound")
            end_label = SpanWdg("&nbsp;%s-%s" %(e_month_label, e_day))
            end_label.set_class("cal_in_bound")
        # check for boundary
        if start_width > my.width:
            start_width = my.width
            start_label.set_class('cal_out_bound')
        elif start_width < 0:
            start_width = 0
            start_label.set_class('cal_out_bound')
        
        if end_width > my.width:
            end_width = my.width
            end_label.set_class('cal_out_bound')
        elif end_width < 0:
            end_width = 0
            end_label.set_class('cal_out_bound')



        # calculate the length of the duration width
        #   offset for the border thickness
        offset = 5
        duration_width = end_width - start_width - offset
        if duration_width < 0:
            duration_width = 0



        # Create the actual interface using a top level Widget.
        # NOTE: This should not be a div, otherwise it will be duplicated
        # on ajax load
        widget = Widget()
       
        spacer = DivWdg()
        spacer.add_style("height: 5px")
        spacer.add_style("float: left")
        spacer.add_style("text-align: right")
        # width can be zero if it is out of bound
        spacer.add_style("width", start_width)
        start_div = DivWdg(start_label)
        start_div.set_id("%s_%s" % ( start_date_col, sobject.get_id()) )
        start_div.set_style("float: right; white-space: nowrap")
        spacer.add(start_div)
        widget.add(spacer)

        if duration_width:

            if is_dependent and not no_label_flag:
                depend_div = DivWdg()
                depend_div.add_style("float: left")
                depend_div.add("&nbsp;")
                depend_div.add_style("width: 0px")
                depend_div.add_style("height: 10px")
                depend_div.add_style("border-style: solid")
                depend_div.add_style("border-width: 0 1px 0 0")
                depend_div.add_class('cal_depend')
                widget.add(depend_div)



            duration_info = []
            duration_info.append( [int(duration_width), color] )

            for info in duration_info:
                
                duration_width, color = info

                # draw the duration 
                duration = DivWdg("&nbsp;")
                if type == 'bid':
                    duration.add_class('cal_duration')
                    duration.add_style("height: 4px")
                else:
                    duration.add_style("background-color: %s" % color)
                    duration.add_style("height: 5px")
                # for IE
                duration.add_style("font-size: 5px" )
                duration.add_style("margin-top: 4px")
                duration.add_style("float: left")
                duration.add_style("width", duration_width)
                widget.add(duration)


            # draw the end dependency
            if has_dependents and not no_label_flag:
                depend_div = DivWdg()
                depend_div.add_style("float: left")
                depend_div.add("&nbsp;<br/>&nbsp;")
                depend_div.add_style("width: 0px")
                depend_div.add_style("height: 30px")
                depend_div.add_style("border-style: solid")
                depend_div.add_style("border-width: 0 1px 0 0")
                depend_div.add_class('cal_depend')
                widget.add(depend_div)

        else:
            spacer = SpanWdg("|")
            spacer.add_style("color: #aaa")
            spacer.add_style("float: left")
            widget.add(spacer)


        end_div = DivWdg(end_label, css='small')
        end_div.set_id("%s_%s" % (end_date_col,sobject.get_id() ) )
        end_div.add_style("float: left")
        end_div.add_style("white-space: nowrap")
        widget.add(end_div)


        if not edit:
            return widget

        # change the cursor icon
        start_div.add_class("hand")
        end_div.add_class("hand")

        # add the ajax object
        wdg_name = "calendar_range_%s" % sobject.get_id()
        ajax = AjaxLoader(wdg_name)
        ajax.register_cmd("pyasm.widget.CalendarSetCmd")
        ajax.set_load_class("pyasm.widget.CalendarBarWdg")
        ajax.set_option("search_key", sobject.get_search_key() )
        ajax.set_option("start_year", my.start_year)
        ajax.set_option("end_year", my.end_year)
        ajax.set_option("start_month", my.start_month)
        ajax.set_option("end_month", my.end_month)
        ajax.set_option("calendar_width", my.width)
        ajax.set_option("calendar_margin", my.cal_margin)
        ajax.set_option("bid_edit" , my.bid_edit)
        ajax.set_option("actual_edit" , my.actual_edit)
        ajax.set_option("cal_week_hid" , my.week_hid)

        ajax.add_element_name("calendar_column")
        ajax.add_element_name(my.calendar.get_input_name())
        on_script = Common.escape_quote(ajax.get_on_script())


        start_div.add_event("onclick", "show_task_cal('%s',this, '%s','%s','%s')" \
            % ( my.CAL_INPUT, start_date, start_date_col, on_script) )
        start_div.add_event("onmouseover", "this.style.fontWeight = 'bold'" )
        start_div.add_event("onmouseout", "this.style.fontWeight = 'normal'" )
        end_div.add_event("onclick", "show_task_cal('%s', this, '%s','%s','%s')" \
            % ( my.CAL_INPUT, end_date, end_date_col, on_script) )
        end_div.add_event("onmouseover", "this.style.fontWeight = 'bold'" )
        end_div.add_event("onmouseout", "this.style.fontWeight = 'normal'" )

        return widget



    def calculate_widths(my, start_date, end_date):
        '''calculate the pixel width for the dates, returns a dict of info
            ['width'], ['s_label'], ['e_label']'''
        if str(start_date).count(" "):
            start_date, time = str(start_date).split(" ")
        if str(end_date).count(" "):
            end_date, time = str(end_date).split(" ")

        month_unit = float(my.width)/ my.num_months
        leftmost_day = 1
       
        # in case a particular week is selected
        week = my.week_hid
        num_days = 30.5
        
        # calculate pixels
        s_year,s_month,s_day = [int(x) for x in str(start_date).split("-")]
        e_year,e_month,e_day = [int(x) for x in str(end_date).split("-")]

        s_month_label = my.MONTHS[s_month-1]
        leftmost_month = CalendarBarWdg.MONTHS.index(my.first_month) + 1
        
        # check if only 1 week is shown
        s_diff_month = (s_year - my.left_year_bound) * 12 - leftmost_month
        e_diff_month = (e_year - my.left_year_bound) * 12 - leftmost_month

        if week:
            num_days = 7.0
            year = my.months[0][1] 
            left_year_bound = my.left_year_bound
            first_adjust = False
            # handle the cross year scenario, when user clicks on the portion of 
            # week 1 of next year that spans a few days of the previous year
            if int(week) == 1 and leftmost_month == 12:
                year += 1
                first_adjust = True
            leftmost_month, leftmost_day = my._get_month_days(year, week)[0] 
          
            # must do it again with the updated leftmost_month
            # the user clicks on the first week of a new year that started in the
            # previous year
            if int(week) == 1 and leftmost_month == 12 and not first_adjust:
                left_year_bound = my.left_year_bound - 1 
            
            rightmost_month, rightmost_day =  my._get_month_days(year, week)[6]  
            s_date = Date(db_date=start_date)
            e_date = Date(db_date=end_date)

            # boolean to show if a date is within the boundary of the defined calendar
            in_bound_date = True

            rightmost_date = Date(db_date='%s-%s-%s' %(year,rightmost_month, rightmost_day) )
      
            
            if s_date.get_db_date() > rightmost_date.get_db_date():
                # this +12 is just arbitrary to make it out of bound
                # TODO: calculate the real s_month and e_month
                in_bound_date = False
                s_diff_month +=12
            else:
                s_diff_month = (s_year - left_year_bound) * 12 - leftmost_month
            
            if e_date.get_db_date() > rightmost_date.get_db_date():
                # this +12 is just arbitrary to make it out of bound
                # TODO: calculate the real s_month and e_month
                in_bound_date = False
                e_diff_month +=12
            else:
                e_diff_month = (e_year - left_year_bound) * 12 - leftmost_month
        
        
        date = Date(db_date=start_date)
        
        date.add_days(31)
        current_date = Date(db_date='%s-01-01' %my.left_year_bound)
        recent = False
        if date.get_db_date() > current_date.get_db_date():
            recent = True
       
        # s_month is re-enumerated according to the length of the displayed months
        s_month += s_diff_month 
        
        day_unit = month_unit / num_days
        start_width = -1
        diff_day = s_day - leftmost_day

        if diff_day < 0 and s_month > 0 and in_bound_date:
            diff_day += Calendar.get_num_days(left_year_bound, leftmost_month)
            month_unit = 0
        if s_month >= 0:
            start_width = float('%.1f' %(s_month*month_unit + (diff_day)*day_unit))
        
        e_month_label = my.MONTHS[e_month-1]
        end_width = -1
        e_month += e_diff_month

        # -leftmost_day since we are using it as a ref. point 
        diff_day = e_day-leftmost_day
        if diff_day < 0 and e_month > 0 and in_bound_date:
            diff_day += Calendar.get_num_days(left_year_bound, leftmost_month)
            # month_unit is not needed in cross-month situation
            month_unit = 0
        if e_month >= 0:
            end_width = float('%.1f' %(e_month*month_unit + (diff_day + 1)*day_unit))
        info = {}
        info['width'] = (start_width, end_width)
        info['s_label'] = (s_month_label, s_day)
        info['e_label'] = (e_month_label, e_day)
        return info
        


    # handle status history display

    def preprocess_status(my):
        if not my.sobjects:
            return

        if my.statuses:
            return

        search = Search("sthpw/status_log")
        search_type = my.sobjects[0].get_search_type()
        search.add_filter("search_type", search_type)
        search.add_filters("search_id", SObject.get_values(my.sobjects, "id") )
        search.add_order_by("timestamp")
        status_changes = search.get_sobjects()

        for status_change in status_changes:
            key = "%s|%s" % (status_change.get_value("search_type"), status_change.get_value("search_id") )
            changes = my.statuses.get(key)
            if not changes:
                changes = []
                my.statuses[key] = changes

            changes.append(status_change)



    def get_status_history_wdg(my,sobject):

        my.preprocess_status()

        mode = my.get_option("actual_mode")
        if not mode:
            #mode = "single"
            mode = "detail"

        widget = Widget()

        status_changes = my.statuses.get( sobject.get_search_key() )
        if not status_changes:
            widget.add("...")
            return widget

        pipeline = Pipeline.get_by_sobject(sobject)
        if not pipeline:
            pipeline = Pipeline.get_by_code("task")

        # calculate the range
        changes = []
        last_timestamp = None
        status_changes.reverse()
        for status_change in status_changes:
            change = []

            timestamp = str(status_change.get_value("timestamp"))
            to_status = str(status_change.get_value("to_status"))
            user = str(status_change.get_value("login"))

            process = pipeline.get_process(to_status)

            if not last_timestamp:
                last_timestamp = timestamp
                tmp = Date(db=last_timestamp)
            else:
                # remove a day from the last timestamp
                tmp = Date(db=last_timestamp)
                tmp.add_days(-1)

            change = [timestamp, tmp.get_db_date(), process, to_status, user]

            changes.append(change)

            last_timestamp = timestamp


        # draw all of the bars

        count = 0
        changes.reverse()
        last_change = False
        for change in changes:

            if count == len(changes)-1:
                last_change = True

            start_date, end_date, process, to_status, user = change

            color = 'grey'
            if process:
                process_color = process.get_color()
                if process_color:
                    color = process_color

            #to_status = process.get_name()

            start_width, end_width = my.calculate_widths(start_date,end_date).get('width')
            if start_width < 0:
                start_width = 0
            elif start_width > my.width:
                start_width = my.width

            if end_width > my.width:
                end_width = my.width

            # set the spacer: used for either the first or all in detail mode
            if mode == "detail" or not count:
                spacer = DivWdg()
                spacer.add_style("height: 5px")
                spacer.add_style("float: left")
                spacer.add_style("text-align: right")
                spacer.add_style("width", start_width)
                widget.add(spacer)

            duration = DivWdg()
            #duration.add_style("border: 1px dotted %s" % color)
            #duration.add_style("height: 4px")
            duration.add_style("background-color: %s" % color)
            duration.add_style("height: 5px")

            height = 4
            duration_width = end_width - start_width + 1
            if last_change:
                duration_width =  8
                height = 5 
            duration.add_style("height: %spx" % height)

                

            # for IE
            duration.add_style("font-size: 5px" )
            duration.add_style("margin-top: 4px")
            duration.add_style("float: left")
            duration.add_style("width", duration_width)
            widget.add(duration)

            start_display_date = Date(db=start_date).get_display("%b %d")
            display_date = Date(db=end_date).get_display("%b %d")

            # add a tip
            duration.add_tip("Date: %s to %s<br/>Status: %s<br/>User: %s<br/>" % (start_display_date, display_date, to_status, user) )

            if mode == "detail" or last_change:
                widget.add( "<i style='font-size: 0.8em; '>&nbsp;%s (%s)</i>" % (display_date, to_status) )

            if mode == "detail":
                widget.add( HtmlElement.br() )

            count += 1

        return widget




    def get_checkin_history_wdg(my,sobject):

        widget = Widget()

        # calculate all of the ranges and percentages
        parent = sobject.get_parent()

        # FIXME: big assumption that context == process
        process = sobject.get_value("process")
        snapshots = Snapshot.get_by_sobject(parent,process)
        snapshots.reverse()

        for snapshot in snapshots:
            start_date = snapshot.get_value("timestamp")
            end_date = start_date
            # draw up all of the ranges
            #start_width, end_width = my.calculate_widths(start_date,end_date).get('width')
            start_width, end_width = my.calculate_widths(start_date,end_date).get('width')
            if start_width < 0:
                start_width = 0
            elif start_width > my.width:
                start_width = my.width

            if end_width > my.width:
                end_width = my.width

            # set the spacer: used for either the first or all in detail mode
            spacer = DivWdg()
            spacer.add_style("height: 5px")
            spacer.add_style("float: left")
            spacer.add_style("text-align: right")
            spacer.add_style("width", start_width)
            widget.add(spacer)

            duration = DivWdg()
            duration.add_style("background-color: grey")
            duration.add_style("height: 5px")
            duration.add_style("float: left")
            duration.add_style("text-align: right")
            duration.add_style("vertical-align: middle")
            duration.add_style("width", "5px")
            widget.add(duration)


            start_display_date = Date(db=start_date).get_display("%b %d")
            display_date = Date(db=end_date).get_display("%b %d")

            version = snapshot.get_value("version")
            context = snapshot.get_value("context")
            user = snapshot.get_value("login")

            duration.add_tip("Date: %s<br/>Context: %s<br/>Version: %s<br/>User: %s<br/>" % (display_date, context, version, user) )

            widget.add(" <i style='font-size: 0.8em;'>%s (v%0.2d %s)</i>" % (display_date, int(version), context))
            
            widget.add( HtmlElement.br() )

        return widget





    def get_resource_usage_wdg(my,sobject):

        month_unit = float(my.width)/ my.num_months
        day_unit = month_unit / 30.5
        # calculate pixels
        
        s_year,s_month,s_day = [int(x) for x in str(start_date).split("-")]
        # get all of the tasks
        tasks = my.sobjects

        widget = Widget()

        # calculate all of the ranges and percentages
        for task in tasks:
            bid_start_date = my.get_value("bid_start_date")
            bid_end_date = my.get_value("bid_end_date")

        # draw up all of the ranges
        #start_width, end_width = my.calculate_widths(start_date,end_date).get('width')




from pyasm.command import Command, CommandExitException
class CalendarSetCmd(Command):

    def get_title(my):
        return "Set Task Date"

    def check(my):
        return True

    def execute(my):
        web = WebContainer.get_web()
        search_key = web.get_form_value("search_key")
        sobject = Search.get_by_search_key(search_key)

        date = web.get_form_value(CalendarBarWdg.CAL_INPUT)
        # date can be empty to clear the value
        if date == "__NONE__":
            raise CommandExitException()

        column = web.get_form_value("calendar_column")

        sobject.set_value(column, date)

        # make sure end date is not before start date
        if column.endswith("end_date"):
            start_date = sobject.get_value( column.replace("end", "start") )
            if start_date and str(start_date) > date and date:
                sobject.set_value( column.replace("end","start"), date)
        # make sure end date is not before start date
        elif column.endswith("start_date"):
            end_date = sobject.get_value( column.replace("start", "end") )
            # dates can be empty
            if end_date and str(end_date) < date and date:
                sobject.set_value( column.replace("start","end"), date)


        sobject.commit()

        sobject.update_dependent_tasks()


        my.description = "Set %s to '%s'" % (column, date)





