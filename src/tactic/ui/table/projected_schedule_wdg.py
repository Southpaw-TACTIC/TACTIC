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


    def preprocess(self):
         
        for sobj in self.sobjects:
        
            start_date = sobj.get_value("start_date")
            
            cmd = GetProjectedScheduleCmd(
                sobject=sobj,
                start_date=start_date,
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
            tasks = generator.execute(sobject, pipeline, start_date=start_date, today=today)
            completion_date = generator.get_completion_date()
            
        self.info = {
            'completion_date': completion_date,
            'tasks': tasks        
        }
        return self.info
