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

__all__ = ["ApprovalManagerWdg"]

from pyasm.biz import Pipeline
from pyasm.search import Search, SearchType, SObject
from pyasm.web import *
from pyasm.widget import *
from pyasm.prod.biz import Asset
from pyasm.prod.web import *

from task_manager_wdg import TaskStatusFilterWdg, SObjectStatusFilterWdg


class ApprovalManagerWdg(Widget):

    def __init__(self, name=None):
        self.search_type = None
        self.pipeline_name = None
        self.sobject_filter = None
        self.process_filter_name = 'process_filter'
        self.search_limit = 10     # default 10
        self.view = "table"
        super(ApprovalManagerWdg,self).__init__(name)

    def set_search_type(self, search_type):
        self.search_type = search_type

    def set_pipeline_name(self, pipeline_name):
        self.pipeline_name = pipeline_name

    def set_sobject_filter(self, sobject_filter):
        self.sobject_filter = sobject_filter

    def set_search_limit(self, limit):
        self.search_limit = limit

    def set_process_filter_name(self, filter_name):
        self.process_filter_name = filter_name

    def set_view(self, view):
        self.view = view

    def get_display(self):
        ''' this does not run do_search'''
        search_type = self.options.get("search_type")
        if search_type:
            self.search_type = search_type

        view = self.options.get("view")
        if view:
            self.view = view

        search_type = self.search_type
        pipeline_name = self.pipeline_name
        sobject_filter = self.sobject_filter


        assert search_type != None

        search = Search(search_type)

        widget = Widget()
        
        div = FilterboxWdg()
        widget.add(div)

       
        self.process_filter = ProcessFilterSelectWdg(label="Process: ", \
            search_type=search_type, css='med', name=self.process_filter_name)
        self.process_filter.set_submit_onchange(False)

        
        # get all of the sobjects related to this task
        taskless_filter = FilterCheckboxWdg('show_taskless_assets', \
            label='Show Taskless Assets', css='small')
        taskless_filter.set_submit_onchange(False)

        # add in the asset filter
        if sobject_filter:
            sobject_filter.alter_search(search)
            div.add(sobject_filter)


        # append the process filter and user filter
        div.add_advanced_filter(self.process_filter)
        

        # add a hint
        hint = HintWdg('You can select a single process or the &lt;&lt; heading &gt;&gt; '\
             'which will select the group of processes it contains.')
                
        div.add_advanced_filter(hint)

        if UserFilterWdg.has_restriction():
            user = Environment.get_user_name()
            self.user_filter = HiddenWdg('user_filter', user) 
            self.user_filter.set_persistence() 
        else:
            # it has a special colunn 'assigned'
            self.user_filter = UserFilterWdg(['user_filter', 'Assigned: '])
            self.user_filter.set_search_column('assigned')
        div.add_advanced_filter(self.user_filter)

        # add the show assets with no task option
        div.add_advanced_filter(taskless_filter)
        
        
        # add the task filter
        self.task_status_filter = TaskStatusFilterWdg()
        div.add_advanced_filter(self.task_status_filter)

        div.add_advanced_filter(HtmlElement.br())
        if search_type == 'prod/shot': 
            shot_filter = SObjectStatusFilterWdg()
            div.add_advanced_filter(shot_filter)
            shot_statuses = shot_filter.get_statuses()
            if shot_statuses:
                search.add_filters("status", shot_filter.get_values() )

        # add search limit
        search_limit = SearchLimitWdg()
        search_limit.set_limit(self.search_limit)
        div.add_bottom(search_limit)


        # only show shots that match the task filter
        if not taskless_filter.is_checked(False):
            # filter out the tasks
            search.add_column("id")
            tmp_sobjects = search.get_sobjects()
            sobjects = []
            if tmp_sobjects:

                # get all of the sobject ids corresponding to these tasks
                tasks = self.get_tasks(tmp_sobjects)
                sobject_ids = SObject.get_values(tasks, "search_id", unique=True)

                search = Search(search_type)
                search.add_filters("id", sobject_ids)
                search_limit.alter_search(search)
                sobjects = search.get_sobjects()

        else:
            search_limit.alter_search(search)
            tmp_sobjects = search.get_sobjects()
            sobjects = tmp_sobjects
            
            
        table = TableWdg(search_type, self.view)
        widget.add(HtmlElement.br())
        table.set_sobjects(sobjects)

        widget.add(table)
        return widget


    

    def get_tasks(self, sobjects=[]):


        # get all of the relevant tasks to the user
        task_search = Search("sthpw/task")
        task_search.add_column("search_id", distinct=True)


        if sobjects:
            task_search.add_filter("search_type", sobjects[0].get_search_type() )
            sobject_ids = SObject.get_values(sobjects, "id", unique=True)
            task_search.add_filters("search_id", sobject_ids)


        # only look at this project
        search_type = SearchType.get(self.search_type).get_full_key()
        task_search.add_filter("search_type", search_type)


        self.process_filter.alter_search(task_search)
        if isinstance(self.user_filter, UserFilterWdg):
            self.user_filter.alter_search(task_search)
        else:
            user = Environment.get_user_name()
            task_search.add_filter('assigned', user)
        
        status_filters = self.task_status_filter.get_values()
        
        if not status_filters:
            return []

        task_search.add_filters("status", status_filters)

        tasks = task_search.get_sobjects()
        
        return tasks










