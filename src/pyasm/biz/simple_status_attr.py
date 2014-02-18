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

__all__ = ["SimpleStatusAttr"]

import string, types

from pyasm.common import *
from pyasm.search import SObjectAttr, SObjectException

from pipeline import Pipeline
from status_attr import * 


class SimpleStatusAttr(SObjectAttr):
    '''Very simple status attribute that just sets the value directly into the
    database'''

    def __init__(my, name, sobject):
        SObjectAttr.__init__(my, name, sobject)


    def init(my):

        # get the pipeline
        if my.sobject.has_value("pipeline_code"):
            pipeline_code = my.sobject.get_value("pipeline_code")
            if pipeline_code == "":
                pipeline_code = my.get_option("pipeline")
        else:
            pipeline_code = my.get_option("pipeline")

        my.pipeline = Pipeline.get_by_code(pipeline_code, allow_default=True)

        if not my.pipeline:
            raise SetupException("Pipeline 'default' is required in the table [sthpw.pipeline]")


    def get_pipeline(my):
        return my.pipeline




    def set_status(my, status):
        my.set_value(status)


    def get_current_process(my):
        if my.get_value() == "":
            processes = my.pipeline.get_processes()
            if not processes:
                return None
            else:
                return my.pipeline.get_processes()[0]
        else: 
            return my.pipeline.get_process(my.get_value() )



    def get_completion(my):
        '''finds the completion of this status. Returns a number from 0 to 1'''
        context = my.get_current_process()
        completion = ""
        if context:
            completion = context.get_completion()
        else:
            # the processes defined in the pipeline must have changed
            return -1

        if completion != "" and completion != None:
            return float(completion)/100

        # calculate the completion of the asset if there are no percentages
        processes = my.pipeline.get_processes()
        percent = 0.0
        percent += processes.index(context)
        '''
        for process in processes:
            if context == process:
                break
            percent += 1.0
        '''
        if processes:
            percent = (percent + 1)/(len(processes))
        else:
            percent = 0
        return percent


    def get_percent_completion(my):
        return int(my.get_completion() * 100)





