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

__all__ = ["HierarchicalStatusAttr"]

import string, types

from pyasm.common import *
from pyasm.search import SObjectAttr

from pipeline import Pipeline
from status_attr import * 



class HierarchicalStatusAttr(SObjectAttr):
    '''A more complex attribute that uses any number of pipelines'''

    def __init__(self, name, sobject):
        SObjectAttr.__init__(self, name, sobject)


    def init(self):
        self.pipelines = []
        pipeline_types = self.get_option("pipeline").split(",")
        for pipeline_type in pipeline_types:
            pipeline = Pipeline.get_by_name(pipeline_type)
            if pipeline == None:
                raise SetupException("Pipeline '%s' does not exist" % \
                    pipeline_type )
            self.pipelines.append(pipeline)
       
        self.level = 1


    def set_level(self, level):
        self.level = level


    def _get_seq_values(self):
        num_pipelines = len(self.pipelines)
        value = self.sobject.get_value(self.name)
        values = value.split(",")
        for i in range(len(values), num_pipelines):
            values.append("")
        return values




    def get_value(self):
        values = self._get_seq_values()
        return values[self.level]

    def set_value(self, value):
        values = self._get_seq_values()

        # when a child level is done, the parent level is pushed up one.
        processes = ['roughDesign','finalColor','colorKey','flashReady']
        if self.level != 0:
            if value == "publish":
                values[self.level-1] = processes[1]
                value = "artist"

            # when a child level is at the first level, the parent is
            # pushed down
            elif value == "artist":
                values[self.level-1] = processes[0]
                value = "check"


        values[self.level] = value
        current_value = ",".join(values)
        self.sobject.set_value(self.name, current_value)


    def get_web_display(self):
        values = self._get_seq_values()
        return values





    def get_pipeline(self):
        return self.pipelines[self.level]



    def set_status(self, status):
        self.set_value(status)


    def get_current_process(self):
        '''The current process is the process that we are currently at
        depending what level we are looking at'''
        pipeline = self.get_pipeline()
        if self.get_value() == "":
            return pipeline.get_processes()[0]
        else: 
            return pipeline.get_process(self.get_value() )



    def get_completion(self):
        '''finds the completion of this status. Returns a number from 0 to 1'''
        context = self.get_current_process()
        completion = context.get_completion()
        if completion != "":
            return float(completion)/100

        # calculate the completion of the asset if there are no percentages
        pipeline = self.get_pipeline()
        processes = pipeline.get_processes()
        if len(processes) == 1:
            return 1


        percent = 0.0
        for process in processes:
            if context == process:
                break
            percent += 1.0

        percent = percent/(len(processes)-1)
        return percent


    def get_percent_completion(self):
        return int(self.get_completion() * 100)





