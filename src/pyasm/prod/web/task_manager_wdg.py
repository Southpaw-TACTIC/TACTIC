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

__all__ = ["TaskManagerWdg", "TaskStatusFilterWdg", "SObjectStatusFilterWdg"]

from pyasm.common import Date, Common, Environment
from pyasm.biz import Pipeline, Task, Project
from pyasm.search import Search, SObject
from pyasm.web import *
from pyasm.widget import *
from prod_input_wdg import *
from asset_filter_wdg import SearchFilterWdg, UserFilterWdg
from pyasm.prod.biz import ProdSetting

class TaskManagerWdg(Widget):
    
    INVALID = "INVALID"
    #def __init__(self, name=None):
    def __init__(self, **kwargs):

        name = kwargs.get('name')
        self.search_type = kwargs.get('search_type')
        #self.show_all_task_approvals = kwargs.get('show_all_task_approvals')

        self.sobject_filter = None
        super(TaskManagerWdg,self).__init__(name)
        self.process_filter_name = 'process_filter'
        self.show_all_task_approvals = False
        self.task_view = None

        self.calendar_options = {}


    def set_search_type(self, search_type):
        self.search_type = search_type

    def set_sobject_filter(self, filter):
        self.sobject_filter = filter

    def set_process_filter_name(self, filter_name):
        self.process_filter_name = filter_name

    def set_show_all_task_approvals(self):
        self.show_all_task_approvals = True

    def set_task_view(self, view):
        self.task_view = view

    def set_calendar_option(self, name, value):
        self.calendar_options[name] = value

    def get_display(self):
        web = WebContainer.get_web()
        
        widget = Widget() 

        if not self.search_type:
            self.search_type = self.options.get("search_type")
        assert self.search_type


        sobject_filter = self.sobject_filter

        web_state = WebState.get()
        web_state.add_state("ref_search_type", self.search_type)

        div = FilterboxWdg()
        widget.add(div)


        # add the sobject filter
        if self.sobject_filter:
            div.add(self.sobject_filter)
      
        # add a milestone filter
        milestone_filter = FilterSelectWdg("milestone_filter", label="Milestone: ")
        milestones = Search("sthpw/milestone").get_sobjects()
        milestone_filter.set_sobjects_for_options(milestones, "code", "code")
        milestone_filter.add_empty_option(label='-- Any Milestones --')
        milestone_filter.set_submit_onchange(False)
        milestone = milestone_filter.get_value()
        
    
        div.add_advanced_filter(milestone_filter)

        # add a process filter
        process_filter = ProcessFilterSelectWdg(name=self.process_filter_name, label='Process: ')
        process_filter.set_search_type(self.search_type)
        process_filter.set_submit_onchange(False)
        
        div.add_advanced_filter(process_filter)


        user_filter = None
        user = Environment.get_user_name()
        # it has a special colunn 'assigned'
        if not UserFilterWdg.has_restriction():
            user_filter = UserFilterWdg() 
            user_filter.set_search_column('assigned')
            user = user_filter.get_value()
            div.add_advanced_filter(user_filter)

        
        # add a task properties search
        search_columns = ['status', 'description']
        task_search_filter = SearchFilterWdg(name='task_prop_search', \
                columns=search_columns, label='Task Search: ')
        div.add_advanced_filter(task_search_filter)

        # add a retired filter
        retired_filter = RetiredFilterWdg()
        div.add_advanced_filter(retired_filter)

        # set a limit to only see set amount of sobjects at a time
        search_limit = SearchLimitWdg()
        search_limit.set_limit(50)
        search_limit.set_style(SearchLimitWdg.LESS_DETAIL)
        div.add_bottom(search_limit)
        
        div.add_advanced_filter(HtmlElement.br(2))
        start_date_wdg = CalendarInputWdg("start_date_filter", label="From: ", css='med')
        start_date_wdg.set_persist_on_submit()
        div.add_advanced_filter(start_date_wdg)

        start_date = start_date_wdg.get_value()

        # these dates are actually used for search filtering
        processed_start_date = None
        processed_end_date = None
        if start_date:
            date = Date(db_date=start_date)
            # this guarantees a valid date( today ) is invalid input is detected
            processed_start_date = date.get_db_date()
            if start_date != processed_start_date:
                start_date_wdg.set_value(self.INVALID)
        # add hints
        hint = HintWdg("The 'From' and 'To' dates apply to bid dates.")
        #span.add(hint)
        
        end_date_wdg = CalendarInputWdg("end_date_filter", label="To: ", css='med')
        end_date_wdg.set_persist_on_submit()
        div.add_advanced_filter(end_date_wdg)
        div.add_advanced_filter(hint)

        end_date = end_date_wdg.get_value()
        if end_date:
            date = Date(db_date=end_date)
            processed_end_date = date.get_db_date()
            if end_date != processed_end_date:
                end_date_wdg.set_value(self.INVALID)
      
        # show sub task checkbox
        sub_task_cb = FilterCheckboxWdg('show_sub_tasks', label='show sub tasks', css='med')
        div.add_advanced_filter(sub_task_cb)

        div.add_advanced_filter(HtmlElement.br(2))
        task_filter = TaskStatusFilterWdg()
        div.add_advanced_filter(task_filter)
       
        shot_filter = None
        if self.search_type == 'prod/shot': 
            shot_filter = SObjectStatusFilterWdg()
            div.add_advanced_filter(shot_filter)

        # add refresh icon
        '''
        refresh = IconRefreshWdg(long=False)
        calendar_div.add(refresh)
        calendar_div.add(SpanWdg('&nbsp;', css='small'))
        '''
        

        

        # get all of the assets
        search = Search(self.search_type)
        
        if sobject_filter:
            sobject_filter.alter_search(search)

        if shot_filter:
            shot_statuses = shot_filter.get_statuses()
            shot_statuses_selected = shot_filter.get_values()
            if shot_statuses != shot_statuses_selected:
                search.add_filters("status", shot_filter.get_values() )

        assets = search.get_sobjects()
        
        if not assets:
            # drawing the empty table prevents the loss of some prefs data
            table = TableWdg("sthpw/task", self.task_view)
            #widget.add(HtmlElement.h3("No assets found"))
            widget.add(table)
            return widget

        # this assumes looking at one project only
        project_search_type = assets[0].get_search_type()
        
        ids = SObject.get_values(assets, 'id')

        # get all of the tasks
        search = Search("sthpw/task")
        if processed_start_date and start_date_wdg.get_value(True) != self.INVALID:
            search.add_where("(bid_start_date >= '%s' or actual_start_date >='%s')" \
                % (processed_start_date, processed_start_date))
        if processed_end_date and end_date_wdg.get_value(True) != self.INVALID:
            search.add_where("(bid_end_date <= '%s' or actual_end_date <='%s')" \
                % (processed_end_date, processed_end_date))

        # filter out sub pipeline tasks
        if not sub_task_cb.is_checked():
            search.add_regex_filter('process', '/', op='NEQ')

        search.add_filter("search_type", project_search_type)
        search.add_filters("search_id", ids )

        # order by the search ids of the asset as the were defined in the
        # previous search
        search.add_enum_order_by("search_id", ids)


        if user != "":
            search.add_filter("assigned", user)
        if milestone != "":
            search.add_filter("milestone_code", milestone)
        
        process_filter.alter_search(search)
        
        task_search_filter.alter_search(search)
       
        if not self.show_all_task_approvals:
            #task_filter = TaskStatusFilterWdg(task_pipeline="task")
            #widget.add(task_filter)
            task_statuses = task_filter.get_processes()
            task_statuses_selected = task_filter.get_values()
           
            # one way to show tasks with obsolete statuses when the user
            # check all the task status checkboxes
            if task_statuses != task_statuses_selected:
                search.add_filters("status", task_filter.get_values() )

            


        # filter for retired ...
        # NOTE: this must be above the search limit filter
        # because it uses a get count which commits the retired flag
        if retired_filter.get_value() == 'true':
            search.set_show_retired(True)

        
        # alter_search() will run set_search() implicitly
        search_limit.alter_search(search)

        # define the table
        table = TableWdg("sthpw/task", self.task_view)

        # get all of the tasks
        tasks = search.get_sobjects()
        sorted_tasks = self.process_tasks(tasks, search)

        widget.add( HtmlElement.br() )

        table.set_sobjects(sorted_tasks)

        # make some adjustments to the calendar widget
        calendar_wdg = table.get_widget("schedule")
        for name,value in self.calendar_options.items():
            calendar_wdg.set_option(name, value)

        widget.add(table)

        return widget

    def process_tasks(self, tasks, search):
        '''ensure that all the tasks of an sobject are shown either in this or next Page.
           sort the tasks according to pipeline within each sobject'''
        if tasks:
            task_ids = set()
            for task in tasks:
                task_ids.add(task.get_id())

            # reset the search limits to reuse the search
            search.set_offset(0)
            search.set_limit(0)
 
            
            # do the last sobject, reusing the last search
            sobject = tasks[-1].get_parent()
            search.add_filter("search_type", sobject.get_search_type())
            search.add_filter("search_id", sobject.get_id())
            sobject_tasks = search.do_search(redo=True)
            
            for sobject_task in sobject_tasks:
                task_id = sobject_task.get_id()
                if task_id not in task_ids:
                    tasks.append(sobject_task)
                    task_ids.add(task_id)
          
            tasks_to_remove = set()
            tasks_to_insert = []
            task_ids_to_remove = set()
            first_sobject_tasks = []

            # find the task candidates to be removed
            if len(tasks) > 1:
                last_search_id = tasks[0].get_value('search_id')
                for task in tasks:
                    search_type = task.get_value('search_type')
                    search_id = task.get_value('search_id')
                    if last_search_id == search_id:
                        tasks_to_remove.add(task)
                        task_ids_to_remove.add(task.get_id())

                # do the first sobject, reusing the last search
                sobject = tasks[0].get_parent()
                search.add_filter("search_type", sobject.get_search_type())
                search.add_filter("search_id", sobject.get_id())
                first_sobject_tasks = search.do_search(redo=True)
                
                for sobject_task in first_sobject_tasks:
                    task_id = sobject_task.get_id()
                    if task_id not in task_ids:
                        tasks_to_insert.append(sobject_task)
                        
                            
            # remove the first set of tasks if it is incomplete and has been
            # shown before. Note: this is still not perfect if the search limit is set
            # too low like below 20
            if len(tasks_to_remove) < len(first_sobject_tasks) :
                # or len(tasks_to_remove) > search_limit.get_limit() :
                for task_to_remove in tasks_to_remove:
                    tasks.remove(task_to_remove)

                
                # these ids are not used for now
                task_ids = task_ids - task_ids_to_remove
            else:
                for task_to_insert in tasks_to_insert:
                    tasks.insert(0, task_to_insert)
            
        sorted_tasks = Task.sort_tasks(tasks)
        #sorted_tasks = tasks

        return sorted_tasks


    




class TaskStatusFilterWdg(BaseInputWdg):

    def __init__(self, name='task_status', task_pipeline=None):
        '''by default, it should grab all sthpw/task pipelines'''
        if not task_pipeline:
            project_code = Project.get_project_code()
            task_pipeline = Pipeline.get_by_search_type('sthpw/task', project_code)
        if isinstance(task_pipeline, list):
            self.task_pipelines = task_pipeline
        else:
            self.task_pipelines = [Pipeline.get_by_code(task_pipeline)]

        self.process_names = []
        self.checkbox_control = None
        super(TaskStatusFilterWdg,self).__init__(name)
        self.label = "Task Status Filter: "
        self.set_persistence()

    def init(self):
        # dummy checkbox
        # it is required otherwise, it won't detect the value on first page load
        self.cb = CheckboxWdg('task_status')
        self.cb.set_persistence()
        for pipeline in self.task_pipelines:
            process_names = pipeline.get_process_names()
            self.process_names.extend(process_names)
        self.process_names = Common.get_unique_list(self.process_names)
        self.cb.set_option('default', self.process_names)
        
    def get_display(self):
        table = Table()
        table.add_style('margin','10px 0 0 10px')
        for pipeline in self.task_pipelines:
            table.add_row(css='prefs_row')
            table.add_cell(self.get_pipe_label(pipeline))
            table.add_cell(self.get_status_filter(pipeline))
        self.add(table)
        return super(TaskStatusFilterWdg, self).get_display()

    def get_pipe_label(self, pipeline):

        complete_label = '%s (%s)' %(self.label, pipeline.get_code())
        task_div = DivWdg(complete_label)
        task_div.add_style("text-align: left")
       
        if not pipeline:
            BaseAppServer.add_onload_script(IframeWdg.get_popup_script(\
                "The pipeline 'task' is required in the table [sthpw/pipeline]"))
            return

        # add a check-all toggle control
        self.checkbox_control = CheckboxWdg("task_status_control")
        self.checkbox_control.add_event("onclick", "get_elements('task_status').toggle_all("\
                "this,'pipe','%s')"% pipeline.get_code() )
              
        task_div.add(self.checkbox_control)
        
        return task_div

    def get_status_filter(self, pipeline):
        checked_all_status = True
        widget = Widget()
        process_names = pipeline.get_process_names()
        self.process_names.extend(process_names)
        for process_name in process_names:
            span = SpanWdg(css="med")
            checkbox = CheckboxWdg("task_status")
            checkbox.set_persistence()
            checkbox.set_attr('pipe', pipeline.get_code())
            checkbox.set_option("value", process_name)
            
            if checked_all_status and not checkbox.is_checked():
                checked_all_status = False
            
            span.add(checkbox)
            span.add(process_name)
            widget.add(span)
        
        if checked_all_status:
            self.checkbox_control.set_checked()
        return widget

    
    def get_values(self):
        values = self.cb.get_values()
        return values
    
    def get_processes(self):
        return self.process_names









class SObjectStatusFilterWdg(BaseInputWdg):

    def __init__(self, name="sobj_status", shot_status_setting="shot_status"):
        self.shot_status_setting = shot_status_setting
        self.statuses = ProdSetting.get_seq_by_key(self.shot_status_setting)
        super(SObjectStatusFilterWdg,self).__init__(name)
        self.set_persistence()
        self.label = "Shot Status Filter: "
        
    def init(self):
        # dummy checkbox
        self.cb = CheckboxWdg('sobj_status')
        self.cb.set_persistence()
   
        self.cb.set_option('default', self.statuses)

    def get_display(self):
        
        task_div = DivWdg(self.label)
        task_div.add_style("text-align: left")
        task_div.add_style('margin-left','10px')
        setting = ProdSetting.get_by_key(self.shot_status_setting)
        if not setting:
            BaseAppServer.add_onload_script(IframeWdg.get_popup_script(\
                "The Project Setting [%s] is required to be set."%self.shot_status_setting))
            return

        # add a check-all toggle control
        checkbox_control = CheckboxWdg("sobj_status_control")
        checkbox_control.add_event("onclick", "get_elements('sobj_status').toggle_all(this);")
        task_div.add(checkbox_control)
        
        

        checked_all_status = True
        for status in self.statuses:
            span = SpanWdg(css="med")
            checkbox = CheckboxWdg("sobj_status")
            checkbox.set_persistence()
            
            checkbox.set_option("value", status)

            if checked_all_status and not checkbox.is_checked():
                checked_all_status = False
            
            span.add(checkbox)
            span.add(status)
            task_div.add(span)
        
        if checked_all_status:
            checkbox_control.set_checked()
        return task_div

    def get_statuses(self):
        return self.statuses

    def get_values(self):
        return self.cb.get_values()

