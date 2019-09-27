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

__all__ = ['ProjectedCompletionWdg', 'GetProjectedScheduleCmd']

import six
from dateutil import parser
from datetime import datetime
from pyasm.biz import TaskGenerator, Pipeline
from pyasm.common import SPTDate
from pyasm.command import Command
from pyasm.web import DivWdg
from pyasm.search import Search

from tactic.ui.common import BaseTableElementWdg


class ProjectedCompletionWdg(BaseTableElementWdg):
    '''predicts completion date of sobject'''

    ARGS_KEYS = {
        'start_column': {
            'description': 'Column containing schedule start date',
            'type': 'TextWdg',
            'order': '01'
        },
    }


    def init(self):
        self.dates = {}


    def is_editable(cls):
        return False
    is_editable = classmethod(is_editable)


    def get_data(self):

        tasks_by_code = {}
        pipelines_by_code = {}
        processes_by_pipeline = {}
        
        get_data = True
        if not get_data:
            return tasks_by_code, pipelines_by_code, processes_by_pipeline
        
        # Get tasks, pipelines and process sobjects.
        task_s = Search("sthpw/task")
        task_s.add_sobjects_filter(self.sobjects)
        tasks = task_s.get_sobjects()

        pipeline_s = Search("sthpw/pipeline")
        pipeline_codes = [x.get_value("pipeline_code") for x in self.sobjects]
        pipeline_s.add_filters("code", pipeline_codes)
        pipelines = pipeline_s.get_sobjects()

        process_s = Search("config/process")
        process_s.add_filters("pipeline_code", pipeline_codes)
        processes = process_s.get_sobjects()

        for task in tasks:
            search_code = task.get_value("search_code")
            if not tasks_by_code.get(search_code):
                tasks_by_code[search_code] = [task]
            else:
                tasks_by_code[search_code].append(task)

        for pipeline in pipelines:
            code = pipeline.get_code()
            pipelines_by_code[code] = pipeline
        
        for process in processes:
            pipeline_code = process.get_value("pipeline_code")
            if not processes_by_pipeline.get(pipeline_code):
                processes_by_pipeline[pipeline_code] = [process]
            else:
                processes_by_pipeline[pipeline_code].append(process)
            
        for pipeline_code in processes_by_pipeline:
            process_sobjects = {}
            processes = processes_by_pipeline.get(pipeline_code)
            for sobj in processes:
                process = sobj.get_value("process")
                process_sobjects[process] = sobj
            processes_by_pipeline[pipeline_code] = process_sobjects

        return tasks_by_code, pipelines_by_code, processes_by_pipeline


    def preprocess(self):

        tasks_by_code, pipelines_by_code, processes_by_pipeline = self.get_data()
        for sobj in self.sobjects:
        
            tasks = tasks_by_code.get(sobj.get_code())
            pipeline = pipelines_by_code.get(sobj.get_value("pipeline_code"))
            process_sobjects = processes_by_pipeline.get(pipeline.get_code())

            start_date = sobj.get_value("start_date")
            
            cmd = GetProjectedScheduleCmd(
                sobject=sobj,
                pipeline=pipeline,
                process_sobjects=process_sobjects,
                start_date=start_date,
                tasks=tasks
            )
            completion_date = cmd.execute().get("completion_date")
            self.dates[sobj.get_search_key()] = completion_date


    def get_display(self):
        
        sobject = self.get_current_sobject()
 
        value = self.dates.get(sobject.get_search_key())
        if not value:
            value = ""
         
        value_wdg = DivWdg()
        value_wdg.add(value)
        return value_wdg



class GetProjectedScheduleCmd(Command):

    def execute(self):
        '''Calculates the projected schedule for a given sobject'''
        sobject = self.kwargs.get("sobject")
        pipeline = self.kwargs.get("pipeline")
        tasks = self.kwargs.get("tasks")
        process_sobjects = self.kwargs.get("process_sobjects")

        if not pipeline:
            pipeline = Pipeline.get_by_sobject(sobject)

        completion_date = ""
        tasks = []

        if pipeline: 
            start_date = self.kwargs.get("start_date")
            today = self.kwargs.get("today") or datetime.today()
            
            if isinstance(start_date, six.string_types):
                start_date = parser.parse(start_date)
            
            if isinstance(today, six.string_types):
                today = parser.parse(today)
                

            generator = TaskGenerator(generate_mode="projected_schedule")
            tasks = generator.execute(
                sobject, 
                pipeline, 
                start_date=start_date, 
                today=today,
                existing_tasks=tasks,
                process_sobjects=process_sobjects
            )
            completion_date = generator.get_completion_date()
            
        self.info = {
            'completion_date': completion_date,
            'tasks': tasks        
        }
        return self.info
