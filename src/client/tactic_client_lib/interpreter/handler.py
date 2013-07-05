###########################################################
#
# Copyright (c) 2008, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#


__all__ = ['Handler']

import types


class HandlerException(Exception):
    pass
    


class Handler(object):

    def __init__(my, process_name=None):
        my.server = None
        my.input = {}
        my.output = {}
        my.options = {}

        my.status = "pending"
        my.event = None

        my.package = {}
        my.pipeline = None
        my.process_name = process_name
        my.next_processes = []
        my.description = ''

    def get_title(my):
        return my.__class__.__name__

    def get_event(my):
        '''get the event of this handler'''
        return my.event

    def set_event(my, event):
        '''set the event of this handler'''
        my.event = event

    def get_status(my):
        '''get the current status of this handler'''
        return my.status

    def set_status(my, status):
        '''set the current status of this handler'''
        my.status = status


    def set_process_name(my, process_name):
        '''sets the process name that is the parent of this handler'''
        my.process_name = process_name

    def get_process_name(my):
        '''gets the process name that is the parent of this handler'''
        return my.process_name

    def set_description(my, description):
        my.description = description

    def get_description(my):
        return my.description

    def set_package(my, package):
        '''set the deliverable package to this handler'''
        my.package = package


    # DEPRECATED: This is not really useful.  It is better to use
    # TacticServerStub.get() or create your own instance if ncecessary
    def set_server(my, server):
        '''holds a reference to the Tactic server stub'''
        my.server = server

    # DEPRECATED: This is not really useful.  It is better to use
    # TacticServerStub.get() or create your own instance if ncecessary
    def get_server(my):
        return my.server


    def set_pipeline(my, pipeline):
        my.pipeline = pipeline

    def get_pipeline(my):
        return my.pipeline


    def get_input_process_names(my):
        '''get the input processes as defined by the pipeline'''
        return my.pipeline.get_input_process_names(my.process_name)

    def get_output_process_names(my):
        '''get the output processes as defined by the pipeline'''
        return my.pipeline.get_output_process_names(my.process_name)


    def get_input(my):
        return my.input



    def get_value(my, path):
        parts = path.split("/")
        current = my.package
        for part in parts:
            current = current.get(part)
            # explict None comparison: empty string should go through
            if current == None:
                raise HandlerException("Part [%s] does not exist in package" % part)

        # if this is still a dictionary and it has __VALUE__ in it, the
        # get that value
        if type(current) == types.DictionaryType and current.has_key("__VALUE__"):
            current = current.get("__VALUE__")

        if type(current) == types.ListType:
            return current[0]
        else:
            return current

    def get_output(my):
        return my.output

    def set_input(my, input):
        my.input = input

    def set_output(my, output):
        # copy the data structure
        my.output = output.copy()


    def get_option_value(my, name):
        '''get the options set for this widget.  Options are set in the
        definition of the widget so that behaviour of the widget can
        be altered'''
        return my.options.get(name)

    def set_option_value(my, name, value):
        '''set the options for this widget.  This is usually set by the pipeline
        interpreter'''
        my.options[name] = value

    def set_options(my, options):
        '''set all of the options explicitly'''
        my.options = options



    #
    # Flow control functions: these functions allow processes to control
    # the flow
    #

    def add_next_process(my, next_process, recurse=False):
        '''Method that allows a pipeline to determine what the next process is

        @params:
        next_process: the process name that this handler will deliver to
        
        '''
        if not recurse and next_process == my.process_name:
            raise HandlerException("Circular process flow not permitted for process [%s]" % my.process_name)
        my.next_processes.append(next_process)

    
    def get_next_processes(my):
        return my.next_processes

    def stop(my):
        my.next_processes = None



    #
    # Data accessor methods
    #
    def get_input_data(my):
        return my.input

    def get_input_value(my, name):
        return my.input.get(name)


    def get_ouput_data(my):
        return my.ouput

    def get_output_value(my, name):
        return my.output[name]

    def set_output_value(my, name, value):
        my.output[name] = value


    def clear_output(my):
        '''clear the output package'''
        my.output = {}


    def get_package_value(my, path):
        return my.get_value(path)


    #
    # Implementation methods
    #

    def execute(my):
        '''method that does all of the work'''
        my.status = "complete"

    def undo(my):
        '''method that undos what execute just did'''
        pass




