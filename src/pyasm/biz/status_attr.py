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

__all__ = ["StatusAttrException", "StatusAttr", "StatusEnum", "StatusAttr2"]

import string, types

from pyasm.common import *
from pyasm.search import SObjectAttr

from pipeline import Pipeline


class StatusAttrException(Exception):
    pass



class StatusAttr(Base):

    def __init__(my, status_xml, pipeline):

        assert status_xml != None

        # FIXME: what is this
        #assert pipeline != None
        if not pipeline:
            pipeline = Pipeline.get_by_code("default")

        if status_xml == "":
            status_xml = "<status/>"

        my.status = Xml()
        my.status.read_string(status_xml)
        my.pipeline = pipeline


    def clear_status(my):
        status_xml = "<status/>"
        my.status = Xml()
        my.status.read_string(status_xml)


    def get_value(my):
        return my.status.get_xml()
 

    def get_web_display(my):
        current = my.get_current_process()
        return current.get_name().capitalize()


    def get_pipeline(my):
        return my.pipeline



    #
    # function make this behave like a serial process
    #

    def get_current_process(my):
        return my.pipeline.get_process(my.get_value() )


    def set_status(my, status):
        my.clear_status()
        my.set_process_status(status, StatusEnum.IN_PROGRESS)



    def push_status_forward(my, process ):

        # set process to complete
        my.set_process_status(process, StatusEnum.COMPLETE )

        # get forward processes
        forwards = my.pipeline.get_forward_processes(process)
        for forward in forwards:
            my.set_process_status(forward, StatusEnum.IN_PROGRESS )


    def push_status_backward(my, process ):

        # set process to complete
        my.set_process_status(process, StatusEnum.PENDING )

        # get forward processes
        backwards = my.pipeline.get_backward_processes(process)
        for backward in backwards:
            my.set_process_status(backward, StatusEnum.IN_PROGRESS )




    #
    # more generic process functions
    #

    def find_process(my, status_enum):

        status = StatusEnum.get(status_enum)

        # get the nodes
        process_names = my.status.get_values( \
            "status/process[@value='%s']/@name" % status )

        if len(process_names) > 1:
            raise StatusAttrException("Invalid status: more that one '%s' in status for a serial process" % status )

        # if this process is not there, get the first one in the pipeline
        if len(process_names) == 0:
            first_process = my.pipeline.get_processes()[0]
            my.add_process(first_process)
            return first_process
        else:
            process = my.pipeline.get_process( process_names[0] )
            return process


    def add_process(my, process):
        process_node = my.status.create_element("process")
        Xml.set_attribute( process_node, "name", process)
        root = my.status.get_root_node()
        root.appendChild(process_node)
        return process_node




    def set_process_status(my, process, status_enum):
        # check if this process is in the pipeline
        if my.pipeline.get_process(process) == "":
            raise StatusError( "Process [%s] does not exist" % process )

        process_node = my._get_process_node(process)

        # if there is no process node then dynamically create one.
        if process_node == None:
            process_node = my.add_process(process)

        Xml.set_attribute( process_node, "value", StatusEnum.get(status_enum))



    def get_status(my, process):
        process_node = my._get_process_node(process)
        if process_node == None:
            return "invalid"
        return Xml.get_attribute( process_node, "value")

    def get_status_enum(my, process):
        process_node = my._get_process_node(process)
        if process_node == None:
            return StatusEnum.INVALID
        value = Xml.get_attribute( process_node, "value")
        return StatusEnum.get_enum(value)




    # the following completion code assume a serial process
    def get_completion(my):
        '''finds the completion of this status. Returns a number from 0 to 1'''
        # find the in_progress widget to determine the current status
        context = my.find_process( StatusEnum.IN_PROGRESS )
        completion = context.get_completion()
        if completion != "":
            return float(completion)/100

        # calculate the completion of the asset
        processes = my.pipeline.get_processes()
        percent = 0.0
        for process in processes:
            percent += 1.0
            if context == process:
                break
            

        percent = percent/(len(processes))
        return percent


    def get_percent_completion(my):
        return int(my.get_completion() * 100)



    def _get_process_node(my, process):
        xpath = "status/process[@name='%s']" % process
        process_node = my.status.get_node(xpath)
        return process_node


    def get_xml(my):
        return my.status.get_xml()


    def dump(my):
        my.status.dump()




    






class StatusEnum:
    '''
    PENDING     - not ready to work on.  Waiting for a trigger
    READY       - ready to work
    IN_PROGRESS - work is currently being done
    COMPLETE    - work is completed
    INVALID     - status is not relevant

    When completed, all dependent process are made ready
    '''

    (PENDING, READY, IN_PROGRESS, COMPLETE) = range(0,4)
    INVALID = -1
    LEVELS = ("pending", "ready", "in_progress", "complete")

    def get_next( status_enum ):
        if status_enum > len(StatusEnum.LEVELS):
            raise StatusAttrException("Not a valid enum")
        return status_enum + 1
    get_next = staticmethod(get_next)


    def get_prev( status_enum ):
        if status_enum < 0:
            raise StatusAttrException("Not a valid enum")
        return status_enum - 1
    get_prev = staticmethod(get_prev)


    def get_enum( status ):
        '''returns the index of the status given'''
        index = 0
        for level in StatusEnum.LEVELS:
            if level == status:
                return index
            index += 1
        return -1
    get_enum = staticmethod(get_enum)


    def get( status_enum ):
        '''returns the string version of this enum'''
        if status_enum < 0 or status_enum > len(StatusEnum.LEVELS):
            raise StatusAttrException("Not a valid enum: '%s'" % status_enum)

        return StatusEnum.LEVELS[status_enum]
    get = staticmethod(get)


    def get_percentage(status_enum):
        '''gets the percentage as of doneness'''
        if status_enum == StatusEnum.INVALID:
            return 0
        return int( float(status_enum) / 3 * 100 )
    get_percentage = staticmethod(get_percentage)



class StatusAttr2(StatusAttr,SObjectAttr):

    def __init__(my, name, sobject):
        SObjectAttr.__init__(my, name, sobject)


    def init(my):
        status_xml = my.sobject.get_value(my.name)

        pipeline_type = my.get_option("pipeline")
        pipeline = Pipeline.get_by_name(pipeline_type)

        StatusAttr.__init__(my, status_xml, pipeline)




