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

    def __init__(my, name, sobject):
        SObjectAttr.__init__(my, name, sobject)


    def init(my):
        my.pipelines = []
        pipeline_types = my.get_option("pipeline").split(",")
        for pipeline_type in pipeline_types:
            pipeline = Pipeline.get_by_name(pipeline_type)
            if pipeline == None:
                raise SetupException("Pipeline '%s' does not exist" % \
                    pipeline_type )
            my.pipelines.append(pipeline)
       
        my.level = 1


    def set_level(my, level):
        my.level = level


    def _get_seq_values(my):
        num_pipelines = len(my.pipelines)
        value = my.sobject.get_value(my.name)
        values = value.split(",")
        for i in range(len(values), num_pipelines):
            values.append("")
        return values




    def get_value(my):
        values = my._get_seq_values()
        return values[my.level]

    def set_value(my, value):
        values = my._get_seq_values()

        # when a child level is done, the parent level is pushed up one.
        processes = ['roughDesign','finalColor','colorKey','flashReady']
        if my.level != 0:
            if value == "publish":
                values[my.level-1] = processes[1]
                value = "artist"

            # when a child level is at the first level, the parent is
            # pushed down
            elif value == "artist":
                values[my.level-1] = processes[0]
                value = "check"


        values[my.level] = value
        current_value = ",".join(values)
        my.sobject.set_value(my.name, current_value)


    def get_web_display(my):
        values = my._get_seq_values()
        return values





    def get_pipeline(my):
        return my.pipelines[my.level]



    def set_status(my, status):
        my.set_value(status)


    def get_current_process(my):
        '''The current process is the process that we are currently at
        depending what level we are looking at'''
        pipeline = my.get_pipeline()
        if my.get_value() == "":
            return pipeline.get_processes()[0]
        else: 
            return pipeline.get_process(my.get_value() )



    def get_completion(my):
        '''finds the completion of this status. Returns a number from 0 to 1'''
        context = my.get_current_process()
        completion = context.get_completion()
        if completion != "":
            return float(completion)/100

        # calculate the completion of the asset if there are no percentages
        pipeline = my.get_pipeline()
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


    def get_percent_completion(my):
        return int(my.get_completion() * 100)





