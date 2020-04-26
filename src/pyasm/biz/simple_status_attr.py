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

    def __init__(self, name, sobject):
        SObjectAttr.__init__(self, name, sobject)


    def init(self):

        # get the pipeline
        if self.sobject.has_value("pipeline_code"):
            pipeline_code = self.sobject.get_value("pipeline_code")
            if pipeline_code == "":
                pipeline_code = self.get_option("pipeline")
        else:
            pipeline_code = self.get_option("pipeline")

        self.pipeline = Pipeline.get_by_code(pipeline_code, allow_default=True)

        if not self.pipeline:
            raise SetupException("Pipeline 'default' is required in the table [sthpw.pipeline]")


    def get_pipeline(self):
        return self.pipeline




    def set_status(self, status):
        self.set_value(status)


    def get_current_process(self):
        if self.get_value() == "":
            processes = self.pipeline.get_processes()
            if not processes:
                return None
            else:
                return self.pipeline.get_processes()[0]
        else: 
            return self.pipeline.get_process(self.get_value() )



    def get_completion(self):
        '''finds the completion of this status. Returns a number from 0 to 1'''
        context = self.get_current_process()
        completion = ""
        if context:
            completion = context.get_completion()
        else:
            # the processes defined in the pipeline must have changed
            return -1

        if completion != "" and completion != None:
            return float(completion)/100

        # calculate the completion of the asset if there are no percentages
        processes = self.pipeline.get_processes()
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


    def get_percent_completion(self):
        return int(self.get_completion() * 100)





