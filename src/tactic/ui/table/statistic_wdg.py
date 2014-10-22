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

__all__ = ['TaskCompletionWdg', 'TaskGroupCompletionWdg', 'MilestoneCompletionWdg']

from pyasm.common import Date, Calendar, Common, jsonloads
from pyasm.search import *
from pyasm.web import *
from pyasm.biz import *
from pyasm.widget import FilterSelectWdg, FilterCheckboxWdg, IconButtonWdg, IconWdg

#from input_wdg import HiddenWdg, CalendarInputWdg
#from layout_wdg import TableWdg

import datetime, re
from dateutil import parser
from tactic.ui.common import BaseTableElementWdg


class TaskCompletionWdg(BaseTableElementWdg):

    ARGS_KEYS = {

        "task_expr": {
            'description': "an expression that retrieves the tasks e.g. @SOBJECT(sthpw/task['context','anim'])",
            'type': 'TextAreaWdg',
            'order': 0,
            'category': 'Display'
        }
    }
    def init(my):
        my.is_preprocessed = False
        my.data = {}
        my.cal_sub_task = None
        my.cal_sub_task_value = False

        # this is meant for handle_td()
        my.row_completion = 0
        my.expression = None


    def get_width(my):
        return 200


    def is_editable(cls):
        '''Determines whether this element is editable'''
        return False
    is_editable = classmethod(is_editable)

    def preprocess(my):
        my.total_completion = 0.0
        my.num_sobjects = 0
        my.expression = my.kwargs.get('task_expr')
        if my.sobjects and  not my.expression:
            if my.expression:
                tasks = Search.eval(my.expression, sobjects=my.sobjects)
            else:
                tasks = Task.get_by_sobjects(my.sobjects)
            # create a data structure
            for task in tasks:
                search_type = task.get_value("search_type")
                search_code = task.get_value("search_code")
                search_key = SearchKey.build_search_key(search_type, search_code, column='code')
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
        sobject = my.get_current_sobject()
        if sobject.is_insert():
            return ''

        if not my.is_preprocessed:
            my.preprocess()

        sobject = my.get_current_sobject()
        completion = my.get_completion(sobject)
        if not completion:
            completion = 0
        return "%0.1f%%" % completion

    def get_display(my):

        sobject = my.get_current_sobject()
        if sobject.is_insert():
            return ''

        completion = my.get_completion(sobject)
        my.row_completion = completion

        # completion is compared to None, because a 0% completion is valid
        if completion == None:
            div = DivWdg("<i>No tasks</i>")
            div.add_style("color: #aaa")
            return div

        widget = DivWdg()
        width = my.get_width()
        bar_wdg = CompletionBarWdg(completion, width )
        widget.add(bar_wdg)

        # keep a running tab of the total if there is at least one task for this sobject
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
        
        if my.expression:
            tasks = Search.eval(my.expression, sobjects=[sobject])
            return tasks

        tasks = my.data.get( SearchKey.get_by_sobject(sobject, use_id=False) )
        if tasks == None:
            tasks = Task.get_by_sobjects([sobject])

        return tasks
        # make sure we only take tasks in the pipeline into account

        #TURN OFF this filtering for now, will add it back as an optional filtering feature.
        """
        parent = sobject

        pipeline = Pipeline.get_by_sobject(parent)
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
        """



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
            percent = float(percent) / len(my.tasks)
        else:
            return None

        return percent

    def handle_td(my, td):
        td.add_style('vertical-align','middle')
        sobject = my.get_current_sobject()
        if sobject.is_insert():
            return
        td.add_attr("spt_input_value", my.row_completion)



class TaskGroupCompletionWdg(TaskCompletionWdg):

    ARGS_KEYS = {

        'options': {
            'type': 'TextAreaWdg',
            'description': '''A list of options for the various completion bars. e.g. [{"label":"MODEL", "context": ["model","rig"]}] ''',
            'order': 0,
            'category': 'Display'
        },
        
        "task_expr": {
            'description': "an expression that retrieves the tasks e.g. @SOBJECT(sthpw/task['context','anim'])",
            'type': 'TextAreaWdg',
            'order': 1,
            'category': 'Display'
        }

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
            table.add_color("color", "color")
            col = table.add_col()
            col = table.add_col()
            col.add_style('width','80%')
            for group in my.group_list:
                group_label = group.get('label')
                # FIXME is that right?. should we get my.num_sobjects per group?
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
        if sobject.is_insert():
            return ''
        my.calculate(sobject)
        
             
        # completion is compared to None, because a 0% completion is valid
        if not my.completion_dict:
            if my.group_list and my.group_list[0].get('label')=='Syntax Error':
                div = DivWdg("<i>Syntax Error in Column Definition</i>")
            elif my.group_list and my.group_list[0].get('label')=='default':
                div = DivWdg('<i>Fill in the options e.g. [{"label":"MODEL", "context": ["model","rig"]}] </i>')
            else:
                div = DivWdg("<i>No tasks</i>")
            div.add_style("color: #aaa")
            return div

        table = Table()
        table.add_color("color", "color")
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


class MilestoneCompletionWdg(TaskCompletionWdg):

    def get_tasks(my, sobject):
        milestone = sobject.get_code()
        search = Search("sthpw/task")
        search.add_filter("milestone_code", milestone)
        return search.get_sobjects()



__all__.append("TaskDaysDueElementWdg")
class TaskDaysDueElementWdg(BaseTableElementWdg):

    def is_editable(my):
        return False

    def is_groupable(my):
        return True

    def get_display(my):

        div = DivWdg()

        sobject = my.get_current_sobject()
        value = sobject.get_value("bid_end_date")
        if not value:
            return div

        status = sobject.get_value("status")

        due_date = parser.parse(value)

        # get today's date
        from pyasm.common import SPTDate
        today = SPTDate.start_of_today()

        # get the difference
        delta = due_date - today
        diff = delta.days


        if diff < 0:
            if status.lower() in ["approved", "complete", "done"]:
                mode = "done"
            else:
                mode = "critical"
        elif diff >= 0 and diff < 1:
            mode = "today"
        else:
            mode = "due"

        if mode == "critical":
            div.add_style("background: #e84a4d")
            div.add_style("color: #FFF")
            msg = "%s Days" % (-diff)
            div.add_attr("title", msg)
            if diff == -1:
                div.add("Yesterday")
            else:
                div.add(msg)
        elif mode == "today":
            div.add_style("background: #a3d991")
            div.add_style("color: #FFF")
            div.add_attr("title", "Due today")
            div.add("Today")
        elif mode == "done":
            #div.add_style("background: #0F0")
            #div.add_style("color: #000")
            #div.add_attr("title", "Done")
            #div.add("Done")
            pass
        else:
            div.add_style("background: #FFF")
            div.add_style("color: #000")
            div.add_attr("title", "Due in %s days" % diff)
            if diff == 1:
                div.add("Tomorrow")
            else:
                div.add("%s Days" % diff)


        div.add_style("padding: 3px")
        div.add_style("text-align: center")
        div.add_style("margin: -3px")

        return div







