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

__all__ = ['TaskCompletionWdg', 'TaskGroupCompletionWdg', 'MilestoneCompletionWdg','TaskDaysDueElementWdg']

from pyasm.common import Date, Calendar, Common, jsonloads
from pyasm.search import *
from pyasm.web import *
from pyasm.biz import *
from pyasm.widget import FilterSelectWdg, FilterCheckboxWdg, IconButtonWdg, IconWdg

#from input_wdg import HiddenWdg, CalendarInputWdg
#from layout_wdg import TableWdg

import datetime, re, six
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
    def init(self):
        self.is_preprocessed = False
        self.data = {}
        self.cal_sub_task = None
        self.cal_sub_task_value = False

        # this is meant for handle_td()
        self.row_completion = 0
        self.expression = None


    def get_width(self):
        return 200


    def is_editable(cls):
        '''Determines whether this element is editable'''
        return False
    is_editable = classmethod(is_editable)

    def preprocess(self):
        self.total_completion = 0.0
        self.num_sobjects = 0
        self.expression = self.kwargs.get('task_expr')
        if self.sobjects and  not self.expression:
            if self.expression:
                tasks = Search.eval(self.expression, sobjects=self.sobjects)
            else:
                tasks = Task.get_by_sobjects(self.sobjects)
            # create a data structure
            for task in tasks:
                search_type = task.get_value("search_type")
                search_code = task.get_value("search_code")
                search_key = SearchKey.build_search_key(search_type, search_code, column='code')
                sobject_tasks = self.data.get(search_key)
                if not sobject_tasks:
                    sobject_tasks = []
                    self.data[search_key] = sobject_tasks

                sobject_tasks.append(task)

        self.is_preprocessed = True

    def get_prefs(self):
        self.cal_sub_task = FilterCheckboxWdg('calculate_sub_task', \
            label='include sub tasks', css='small')
        self.cal_sub_task_value = self.cal_sub_task.is_checked()
        return self.cal_sub_task

    def get_width(self):
        '''not used I think'''
        width = self.kwargs.get("width")

        if not width:
            width = 400
        return int(width)

    def get_text_value(self):
        sobject = self.get_current_sobject()
        if sobject.is_insert():
            return ''

        if not self.is_preprocessed:
            self.preprocess()

        sobject = self.get_current_sobject()
        completion = self.get_completion(sobject)
        if not completion:
            completion = 0
        return "%0.1f%%" % completion

    def get_display(self):

        sobject = self.get_current_sobject()
        if sobject.is_insert():
            return ''

        completion = self.get_completion(sobject)
        self.row_completion = completion

        # completion is compared to None, because a 0% completion is valid
        if completion == None:
            div = DivWdg("<i>No tasks</i>")
            div.add_style("color: #aaa")
            return div

        widget = DivWdg()
        width = self.get_width()
        bar_wdg = CompletionBarWdg(completion, width )
        widget.add(bar_wdg)

        # keep a running tab of the total if there is at least one task for this sobject
        self.total_completion += completion
        self.num_sobjects += 1

        return widget


    def get_bottom_wdg(self):
        width = self.get_width()
        
        if self.num_sobjects:
            completion = self.total_completion / self.num_sobjects
            bar_wdg = CompletionBarWdg(completion, width)
        else:
            bar_wdg = "n/a"
        div = DivWdg()
        div.add("Total")
        div.add("<hr>")
        
        div.add(bar_wdg)
        return div


    def get_tasks(self, sobject):
        ''' if the sobject is a task, then just return the sobject, since tasks
         do not have tasks. Account for subtask based on preferences. Also
         filters out tasks belonging to obsolete processes'''
        if isinstance(sobject, Task):
            return [sobject]
        
        if self.expression:
            tasks = Search.eval(self.expression, sobjects=[sobject])
            return tasks

        tasks = self.data.get( SearchKey.get_by_sobject(sobject, use_id=False) )
        if tasks == None:
            tasks = Task.get_by_sobjects([sobject])

        return tasks
        # make sure we only take tasks in the pipeline into account

        #TURN OFF this filtering for now, will add it back as an optional filtering feature.
        """
        parent = sobject

        pipeline = Pipeline.get_by_sobject(parent)
        recurse = False
        if self.cal_sub_task_value:
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



    def get_completion(self, sobject):
        self.tasks = self.get_tasks(sobject)
        
        percent = 0
        # count the tasks with invalid or obsolete status
        #invalid_count = 0
        for task in self.tasks:
            status_attr = task.get_attr("status")
            task_percent = status_attr.get_percent_completion()
            if task_percent < 0:
                task_percent = 0
                #invalid_count += 1
            percent += task_percent

        if self.tasks:
            # NOT sure if I should subtract total # of tasks by invalid
            # task, leave it for now
            percent = float(percent) / len(self.tasks)
        else:
            return None

        return percent

    def handle_td(self, td):
        td.add_style('vertical-align','middle')
        sobject = self.get_current_sobject()
        if sobject.is_insert():
            return
        td.add_attr("spt_input_value", self.row_completion)



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
    def preprocess(self):
        self.options = self.get_option('options')
        if self.options:
            try:
                self.group_list = jsonloads(self.options)
            except:
                self.group_list = [{'label': 'Syntax Error', 'context':[]}]
        else:
            self.group_list = [{'label':'default', 'context': []}]

        super(TaskGroupCompletionWdg, self).preprocess()

    def init(self):
        # these 2 are used for bottom summary
        self.total_completion_dict = {}
        self.num_sobjects = 0
        super(TaskGroupCompletionWdg, self).init()

    def get_bottom_wdg(self):
        if self.total_completion_dict:
            table = Table()
            table.add_color("color", "color")
            col = table.add_col()
            col = table.add_col()
            col.add_style('width','80%')
            for group in self.group_list:
                group_label = group.get('label')
                # FIXME is that right?. should we get self.num_sobjects per group?
                completion = self.total_completion_dict.get(group_label)/ self.num_sobjects
            
                group_contexts = group.get('context')
                if group_contexts:
                    group_contexts = ', '.join(group_contexts)


                width = self.get_width()
                bar_wdg = CompletionBarWdg(completion, width)
                label_div = FloatDivWdg('%s: ' %group_label)
                label_div.add_style('margin-right: 4px')
                label_div.add_tip(group_contexts, group_contexts)
                table.add_row()
                table.add_cell(label_div)
                table.add_cell(bar_wdg)
            return table

        width = self.get_width()
        completion = 0
        if self.num_sobjects:
            completion = self.total_completion / self.num_sobjects
        div = DivWdg()
        div.add("Total")
        div.add("<hr>")
        bar_wdg = CompletionBarWdg(completion, width)
        div.add(bar_wdg)
        return div
    
    def get_group_completion(self, items):
        '''get the avg completion'''
        sum = 0
        if not items:
            return 0
        for item in items:
            sum += item
        avg = sum / len(items)
        return avg

    def get_text_value(self):
        sobject = self.get_current_sobject()
        if sobject.get_id() == -1:
            return ''
        self.calculate(sobject)

        output = []
        for group in self.group_list:
            group_label = group.get('label')
            group_contexts = group.get('context')
            if group_contexts:
                group_contexts = ', '.join(group_contexts)
            group_completion = self.completion_dict.get(group_label)
            completion = self.get_group_completion(group_completion)
            output.append('%s: %s%%'%(group_label, completion))

        return '\n'.join(output)

    def calculate(self, sobject):
        '''do the calculation'''
        tasks = self.get_tasks(sobject)


        completion = '' 
        self.completion_dict = {}
        for group in self.group_list:
            group_label = group.get('label')
            group_contexts = group.get('context')
            if not group_label:
                continue
            for task in tasks:
                context = task.get_value('context')
                if context in group_contexts:
                    completion = self.get_completion(task)
                    group_completion = self.completion_dict.get(group_label)
                    if group_completion == None:
                        self.completion_dict[group_label] = [completion]
                    else:
                        group_completion.append(completion)

    def get_display(self):
        sobject = self.get_current_sobject()
        if sobject.is_insert():
            return ''
        self.calculate(sobject)
        
             
        # completion is compared to None, because a 0% completion is valid
        if not self.completion_dict:
            if self.group_list and self.group_list[0].get('label')=='Syntax Error':
                div = DivWdg("<i>Syntax Error in Column Definition</i>")
            elif self.group_list and self.group_list[0].get('label')=='default':
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
        for group in self.group_list:
            group_label = group.get('label')
            group_contexts = group.get('context')
            if group_contexts:
                group_contexts = ', '.join(group_contexts)
            group_completion = self.completion_dict.get(group_label)
            completion = self.get_group_completion(group_completion)


            width = self.get_width()
            bar_wdg = CompletionBarWdg(completion, width)
            label_div = FloatDivWdg('%s: ' %group_label)
            label_div.add_style('margin-right: 4px')
            label_div.add_tip(group_contexts, group_contexts)
            table.add_row()
            table.add_cell(label_div)
            table.add_cell(bar_wdg)
            #widget.add(HtmlElement.br())
            completed_summary = self.total_completion_dict.get(group_label)
            if not completed_summary:
                completed_summary = 0
            self.total_completion_dict[group_label] = completion + completed_summary
        self.num_sobjects += 1

        return table


class CompletionBarWdg(DivWdg):

    def __init__(self, percent, length):
        if not percent:
            percent = 0
        self.percent = percent
        #self.percent = 100
        self.length = length
        super(CompletionBarWdg, self).__init__()

    def init(self):
        #self.add_style("width", self.length + 50)
        self.add_style("font-size", "0.8em")

        width = int(self.length*(float(self.percent)/100))
        if width == 0:
            width = 1

        percent_str = HtmlElement.span("%s%%&nbsp" % self.percent )
        percent_str.add_style("float: right")
        percent_str.add_style("color: white")

        bar = FloatDivWdg()
        bar.add("&nbsp;")
        #bar.add_style("width", width)
        bar.add_style("width", "%s%%" % (70*self.percent/100))
        bar.add_style("border: 1px solid #aaa")
        color_code = self._get_color_code(self.percent)
        bar.add_class("completion %s" % self._get_bar_color_code(self.percent) )
        bar.add_style("background-color", color_code)
        bar.add_style("float", "left")

        self.add(bar)
        percent = FloatDivWdg("%0.1f%%" % self.percent, css='larger')
        percent.add_style('padding', '2px 0 0 4px')
        self.add( percent )



    def _get_bar_color_code(self, percent):
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


    def _get_color_code(self, percent):
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

    def get_tasks(self, sobject):
        milestone = sobject.get_code()
        search = Search("sthpw/task")
        search.add_filter("milestone_code", milestone)
        return search.get_sobjects()



class TaskDaysDueElementWdg(BaseTableElementWdg):

    DAY = 86400
    HOUR = 3600

    
    ARGS_KEYS = {

        "due_date_col": {
            'description': "column name that specifies the due_date_col. Defaults to bid_end_date",
            'type': 'TextWdg',
            'order': 0,
            'category': 'Optional'
        }
    }


    def is_editable(self):
        return False

    def is_groupable(self):
        return True

    def init(self):
        self.due_date_col = self.kwargs.get('due_date_col')
        if not self.due_date_col:
            self.due_date_col = 'bid_end_date'
        self.mode = ''

        self.set_option('filter_name', self.due_date_col)



    def add_value_update(self, value_wdg, sobject, name):
        value_wdg.add_update( {
            'search_key': sobject.get_search_key(),
            'column': name,
            'interval': 2,
            'cbjs_action': '''
            spt.panel.refresh_element(bvr.src_el, {}, {
              callback: function() {
                var td = bvr.src_el.getParent("td");
                var el = bvr.src_el.getElement(".spt_background");
                if (!td || !el) return;
                var color = el.getAttribute("spt_color");
                var background = el.getAttribute("spt_background");
                td.setStyle("color", color);
                td.setStyle("background", background);
              }
            } );
            '''
        } )

    def get_value(self):
        sobject = self.get_current_sobject()
        if not sobject:
            sobject = self.sobject


        # get value directly from sobject (ie: don't calculate)
        mode = self.get_option("data_mode") or ""

        # we need a mode that gets the value directly from the sobject
        if mode == "report":
            value = sobject.get_value(self.get_name(), no_exception=True) or ""
        else:
            value = sobject.get_value(self.due_date_col)

        return value


    def init_data(self):

        sobject = self.get_current_sobject()
        if not sobject:
            sobject = self.sobject

        value = self.get_value()
        if not value:
            self.mode = ""
            self.diff = ""
            self.date_today = None
            self.date_due = None
            return

        DAY = self.DAY
        HOUR = self.HOUR
        status = sobject.get_value("status") or ""

        if isinstance(value, six.string_types):
            due_date = parser.parse(value)
        else:
            due_date = value

        import calendar
        from datetime import datetime, timedelta

        # convert the due date from UTC to local time
        timestamp = calendar.timegm(due_date.timetuple())
        local_dt = datetime.fromtimestamp(timestamp)
        due_date = local_dt.replace(microsecond=due_date.microsecond)

        # get today's date
        from pyasm.common import SPTDate
        import datetime
        import time
        now = datetime.datetime.now()

        # get the difference
        delta = due_date - now
        diff = (delta.days * DAY) + delta.seconds

        date_today = now.date()
        date_due = due_date.date()

        if diff < 0:
            if status.lower() in ["approved", "complete", "done"]:
                mode = "done"
            else:
                mode = "critical"
        elif diff > (HOUR*2) and date_today == date_due:
            mode = "today"
        elif diff > HOUR and diff <= (HOUR*2):
            mode = "warning_1"
        elif diff > 0 and diff <= HOUR:
            mode = "warning_2"
        else:
            mode = "due"
        
        self.mode = mode
        self.diff = diff
        self.date_today = date_today
        self.date_due = date_due



    def get_colors(self):

        self.init_data()

        color = self.top.get_color("color")

        if self.mode == 'critical':
            background = "#e84a4d"
            color = "#FFF"
        elif self.mode == 'today':
            background = "#a3d991"
            color = "#FFF"
        elif self.mode == 'warning_1':
            background = "#e9e386"
        elif self.mode == 'warning_2':
            background = "#ecbf7f"
        elif self.mode == 'done':
            background = ""
        else:
            background = ""

        return color, background 


    def handle_td(self, td):
        '''background color is better handled on td directly'''

        self.init_data()

        if self.mode == 'critical':
            td.add_style("background: #e84a4d")
        elif self.mode == 'today':
            td.add_style("background: #a3d991")
        elif self.mode == 'warning_1':
            td.add_style("background: #e9e386")
        elif self.mode == 'warning_2':
            td.add_style("background: #ecbf7f")
        elif self.mode == 'done':
            pass
        #else:
        #    td.add_style("background: #FFF")

        td.add_attr("spt_input_value", self.get_value())


        super(TaskDaysDueElementWdg, self).handle_td(td)
           

    def get_text_value(self):
        self.init_data()

        sobject = self.get_current_sobject()
        value = sobject.get_value(self.due_date_col)
        if not value:
            return "no date"

        mode = self.mode
        date_today = self.date_today
        date_due = self.date_due


        if mode == "critical":
            days = abs((date_due - date_today).days)
            msg = "%s Days Overdue" % (days)
            if days == 0:
                value = "Today"
            elif days == 1:
                value = "1 Day Overdue"
            else:
                value = msg
        elif mode == "today":
            value = "Today"
        elif mode == "warning_1":
            value = "< 2 Hours"
        elif mode == "warning_2":
            value = "< 1 Hour"
        elif mode == "done":
            value = ""
        else:
            days = abs((date_due - date_today).days)
            if days == 1:
                value = "1 Day"
            else:
                value = "%s Days" % days

        return value


    def get_display(self):

        sobject = self.get_current_sobject()
        if not sobject:
            search_key = self.kwargs.get("search_key")
            sobject = Search.get_by_search_key(search_key)
        else:
            search_key = sobject.get_search_key()
            self.kwargs['search_key'] = search_key

        self.sobject = sobject

        div = DivWdg()
        self.set_as_panel(div)

        color, background = self.get_colors()
        div.add_attr("spt_background" , background)
        div.add_attr("spt_color", color)
        div.add_class("spt_background")

        div.add_style("color", color)
        div.add_style("background", background)

        #self.init_data()

        value = self.get_value()
        if not value:
            div.add("<div style='margin: 0px auto; opacity: 0.3; text-align: center'>no date</div>")
            return div

        status = sobject.get_value("status")

        mode = self.mode
        diff = self.diff
        date_today = self.date_today
        date_due = self.date_due

        self.add_value_update(div, sobject, self.due_date_col)

        if mode == "critical":
            div.add_style("color: #FFF")
            days = abs((date_due - date_today).days)
            msg = "%s Days Overdue" % (days)
            div.add_attr("title", msg)
            if days == 0:
                div.add("Today")
            elif days == 1:
                div.add("1 Day Overdue")
            else:
                div.add(msg)
        elif mode == "today":
            div.add_style("color: #FFF")
            div.add_attr("title", "Due Today")
            div.add("Today")
        elif mode == "warning_1":
            div.add_style("color: #000")
            div.add_attr("title", "Due in 2 Hours")
            div.add("< 2 Hours")
        elif mode == "warning_2":
            div.add_style("color: #000")
            div.add_attr("title", "Due in 1 Hour")
            div.add("< 1 Hour")
        elif mode == "done":
            pass
        else:
            div.add_style("color: %s" % color)
            days = abs((date_due - date_today).days)
            div.add_attr("title", "Due in %s Day(s)" % days)
            if days == 1:
                div.add("1 Day")
            else:
                div.add("%s Days" % days)


        div.add_style("padding: 3px")
        div.add_style("text-align: center")
        div.add_style("margin: -3px")

        return div




