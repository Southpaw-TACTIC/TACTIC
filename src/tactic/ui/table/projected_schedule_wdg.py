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

__all__ = ['ProjectedCompletionWdg', 'GetProjectedScheduleCmd', 'WorkflowSchedulePreviewWdg']

import six
from dateutil import parser
from datetime import datetime
from pyasm.biz import TaskGenerator, Pipeline, Project, ProjectSetting
from pyasm.common import SPTDate, Environment, jsonloads, Common
from pyasm.command import Command
from pyasm.web import DivWdg, HtmlElement
from pyasm.search import Search, SearchType

from tactic.ui.common import BaseTableElementWdg, BaseRefreshWdg

from tactic.ui.panel import ViewPanelWdg
import datetime


class WorkflowSchedulePreviewWdg(BaseRefreshWdg):
    '''Create a schedule preview for workflow created'''
    ARGS_KEYS = {
        'pipeline_code': {
            'description': 'the code of the pipeline that is previewing',
            'type': 'string'
        }
    }

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.pipeline_code = self.kwargs.get("pipeline_code")
        self.pipeline_xml = self.kwargs.get("pipeline_xml")
        self.nodes_properties = self.kwargs.get("nodes_properties")

    def get_styles(self):
        style = HtmlElement.style('''
        .spt_schedule_preview_top {
            padding: 3px 5px;

        }
        ''')

        return style


    def _create_virtual_pipeline(self, pipeline_xml, process_sobjects=None):
        new_process_sobjects = []
        pipeline = self.pipeline
        pipeline.set_pipeline(pipeline_xml)
        xml = pipeline.get_pipeline_xml()
        process_nodes = xml.get_nodes("/pipeline/process")
        for process_node in process_nodes:
            process_name = xml.get_attribute(process_node, "name")
            if process_sobjects:
                process_sobject = process_sobjects.get(process_name)
                if process_sobject:
                    new_process_sobjects.append(process_sobject)
            else:
                settings = xml.get_attribute(process_node, "settings")
                if not settings:
                    settings = self.nodes_properties[process_name]
                if settings:
                    if isinstance(settings, six.string_types):
                        settings = jsonloads(settings)
                        if isinstance(settings, six.string_types):
                            try:
                                import ast
                                settings = ast.literal_eval(settings)
                            except:
                                print("WARNING: could not process settings for %s.") % process_name
                                continue
                    subpipeline_code = settings.get("subpipeline_code") or None
                else:
                    subpipeline_code = None
                    settings = ""
                process_sobj = SearchType.create("config/process")
                process_sobj.set_value("process", process_name)
                process_sobj.set_value("pipeline_code", self.pipeline_code)
                if subpipeline_code:
                    process_sobj.set_value("subpipeline_code", subpipeline_code)
                process_sobj.set_value("workflow", settings)
                new_process_sobjects.append(process_sobj)
        return new_process_sobjects

    
    def get_display(self):
        top = DivWdg()
        style = self.get_styles()
        top.add(style)

        search = Search('sthpw/pipeline')
        search.add_filter("code", self.pipeline_code)
        self.pipeline = search.get_sobject()
        
        process_s = Search("config/process")
        process_s.add_filter("pipeline_code", self.pipeline_code)
        processes = process_s.get_sobjects()

        # if not processes:
        processes = self._create_virtual_pipeline(self.pipeline_xml)

        processes = {x.get_value("process"): x for x in processes}

        today = datetime.datetime.today()
        login = Environment.get_user_name()

        sobject = SearchType.create('sthpw/virtual')
        sobject.set_value("pipeline_code", self.pipeline_code)
        sobject.set_value('login', login)
        
        generator = TaskGenerator(generate_mode="schedule")
        tasks = generator.execute(
            sobject,
            self.pipeline, 
            start_date=today,
            today=today,
            process_sobjects=processes
        )
        completion_date = generator.get_completion_date()


        start_date = today
        due_date = completion_date
        task_processes = {}

        layout = ProjectSetting.get_value_by_key("workflow/workflow_schedule_preview") or 'open src'

        kwargs = {
                'mode': 'preview',
                'search_type': 'sthpw/task',
                'show_shelf': 'false',
                'sobjects': tasks,
                'height': 400,
                'order_by': 'search_code,bid_start_date,bid_end_date',
                'extra_data': {"single_line": "true"},
                'init_load_num': len(tasks),
                'processes': task_processes,
                'edit': False,
                'admin_edit': False,
                'is_editable': False
            }
        
        if layout == 'spt.tools.gantt.GanttLayoutWdg':
            for i, x in enumerate(tasks):
                x.set_value("status", "Assignment")
                x.set_value("id", "1")
                x.set_value("description", "")
                x.set_value("data", "")
                task_processes[x.get_value("process")] = x
            kwargs['layout'] = layout
            kwargs['element_names'] = 'process,status,days_due'
            kwargs['gantt_width'] = 400
        else:
            for i, x in enumerate(tasks):
                x.set_value("status", "Assignment")
                code = Common.generate_random_key()
                x.set_value("code", code)
                x.set_value("id", "1")
                task_processes[x.get_value("process")] = x
            kwargs['view'] = "table"
            kwargs['column_widths'] = "75,75,75,300"
            kwargs['element_names'] = 'process,status,days_due,schedule'

        
        table = ViewPanelWdg(**kwargs)

        top.add(table)


        return top


class ProjectedCompletionWdg(BaseTableElementWdg):
    '''predicts completion date of sobject'''

    ARGS_KEYS = {
        'start_column': {
            'description': 'Column for schedule start date',
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

        start_column = self.kwargs.get("start_column")
        if not start_column:
            start_column = "start_date"
        
        tasks_by_code, pipelines_by_code, processes_by_pipeline = self.get_data()
        for sobj in self.sobjects:
        
            tasks = tasks_by_code.get(sobj.get_code())
            pipeline = pipelines_by_code.get(sobj.get_value("pipeline_code"))
            process_sobjects = processes_by_pipeline.get(pipeline.get_code())

            start_date = sobj.get_value(start_column)
            
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
        if value:
            value = SPTDate.get_display_date(value) 
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
