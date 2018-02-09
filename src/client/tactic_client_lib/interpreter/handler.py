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

    def __init__(self, process_name=None):
        self.server = None
        self.input = {}
        self.output = {}
        self.options = {}

        self.status = "pending"
        self.event = None

        self.package = {}
        self.pipeline = None
        self.process_name = process_name
        self.next_processes = []
        self.description = ''

    def get_title(self):
        return self.__class__.__name__

    def get_event(self):
        '''get the event of this handler'''
        return self.event

    def set_event(self, event):
        '''set the event of this handler'''
        self.event = event

    def get_status(self):
        '''get the current status of this handler'''
        return self.status

    def set_status(self, status):
        '''set the current status of this handler'''
        self.status = status


    def set_process_name(self, process_name):
        '''sets the process name that is the parent of this handler'''
        self.process_name = process_name

    def get_process_name(self):
        '''gets the process name that is the parent of this handler'''
        return self.process_name

    def set_description(self, description):
        self.description = description

    def get_description(self):
        return self.description

    def set_package(self, package):
        '''set the deliverable package to this handler'''
        self.package = package


    # DEPRECATED: This is not really useful.  It is better to use
    # TacticServerStub.get() or create your own instance if ncecessary
    def set_server(self, server):
        '''holds a reference to the Tactic server stub'''
        self.server = server

    # DEPRECATED: This is not really useful.  It is better to use
    # TacticServerStub.get() or create your own instance if ncecessary
    def get_server(self):
        return self.server


    def set_pipeline(self, pipeline):
        self.pipeline = pipeline

    def get_pipeline(self):
        return self.pipeline


    def get_input_process_names(self):
        '''get the input processes as defined by the pipeline'''
        return self.pipeline.get_input_process_names(self.process_name)

    def get_output_process_names(self):
        '''get the output processes as defined by the pipeline'''
        return self.pipeline.get_output_process_names(self.process_name)


    def get_input(self):
        return self.input



    def get_value(self, path):
        parts = path.split("/")
        current = self.package
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

    def get_output(self):
        return self.output

    def set_input(self, input):
        self.input = input

    def set_output(self, output):
        # copy the data structure
        self.output = output.copy()


    def get_option_value(self, name):
        '''get the options set for this widget.  Options are set in the
        definition of the widget so that behaviour of the widget can
        be altered'''
        return self.options.get(name)

    def set_option_value(self, name, value):
        '''set the options for this widget.  This is usually set by the pipeline
        interpreter'''
        self.options[name] = value

    def set_options(self, options):
        '''set all of the options explicitly'''
        self.options = options



    #
    # Flow control functions: these functions allow processes to control
    # the flow
    #

    def add_next_process(self, next_process, recurse=False):
        '''Method that allows a pipeline to determine what the next process is

        @params:
        next_process: the process name that this handler will deliver to
        
        '''
        if not recurse and next_process == self.process_name:
            raise HandlerException("Circular process flow not permitted for process [%s]" % self.process_name)
        self.next_processes.append(next_process)

    
    def get_next_processes(self):
        return self.next_processes

    def stop(self):
        self.next_processes = None



    #
    # Data accessor methods
    #
    def get_input_data(self):
        return self.input

    def get_input_value(self, name):
        return self.input.get(name)


    def get_ouput_data(self):
        return self.ouput

    def get_output_value(self, name):
        return self.output[name]

    def set_output_value(self, name, value):
        self.output[name] = value


    def clear_output(self):
        '''clear the output package'''
        self.output = {}


    def get_package_value(self, path):
        return self.get_value(path)


    #
    # Implementation methods
    #

    def execute(self):
        '''method that does all of the work'''
        self.status = "complete"

    def undo(self):
        '''method that undos what execute just did'''
        pass




