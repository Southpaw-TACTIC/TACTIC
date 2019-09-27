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

"""
import re, time, types
from dateutil import rrule
from dateutil import parser
import datetime
import functools

from pyasm.common import jsonloads, jsondumps, Common, Environment, TacticException, SPTDate
from pyasm.biz import ExpressionParser, Snapshot, Pipeline, Project, Task, Schema, ProjectSetting
from pyasm.search import SearchKey, Search, SObject, SearchException, SearchType
from pyasm.security import Sudo
from pyasm.widget import IconWdg, SelectWdg, HiddenWdg, TextWdg, CheckboxWdg

from .button_wdg import ButtonElementWdg


from tactic.ui.filter import FilterData, BaseFilterWdg, GeneralFilterWdg
from tactic.ui.widget import IconButtonWdg, RadialProgressWdg

from .table_element_wdg import CheckinButtonElementWdg, CheckoutButtonElementWdg

import six
basestring = six.string_types
"""

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
            self.dates[sobj.get_search_key()] = sobj.get_value("due_date")


    def get_display(self):
        
        sobject = self.get_current_sobject()
 
        value = self.dates[sobject.get_search_key()]
         
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

        start_date = self.kwargs.get("start_date")
        
        from dateutil import parser
        start_date = parser.parse(start_date)

        today = self.kwargs.get("today")

        generator = TaskGenerator(generate_mode="projected_schedule")
        tasks = generator.execute(sobject, pipeline, start_date=start_date, today=today)
        completion_date = generator.get_completion_date()
        print completion_date
        
        completion_date = None
        tasks = []
        self.info = {
            'completion_date': completion_date,
            'tasks': tasks        
        }
        return self.info
