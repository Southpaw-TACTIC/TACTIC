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
__all__ = ['Event', 'EventContainer']

from pyasm.common import Base, Container
from pyasm.web import WebContainer
from widget import *

import time, random


# DEPRECATED: these clases are no longer used as of 2.5.0+


class Event(Base):
    '''This class is a wrapper around a simple event architecture in javascript

    General usage:

    To add an event caller:

    span = SpanWdg()
    span.add("push me")
    event_container = WebContainer.get_event_container()
    caller = event_container.get_event_caller('event_name')
    span.add_event("onclick", caller)


    To add a listener:
    event_container = WebContainer.get_event_container()
    event_contaner.add_listener('event_name', 'alert("cow") )

    When an event is called, all of the registered listeners will be executed
    '''


    '''Event object that is convenient to pass around to add listener
    functions'''

    def __init__(self, event_name):
        self.event_name = event_name
        self.event_container = WebContainer.get_event_container()

    def add_listener(self, script_text, replace=False):
        self.event_container.add_listener(self.event_name, script_text, replace)

    def add_listener_func(self, function_name, replace=False):
        self.event_container.add_listener_func(self.event_name, function_name, replace)

    def get_caller(self):
        return self.event_container.get_event_caller(self.event_name)




class EventContainer(Widget):

    DYNAMIC = 'dynamic'    
    def __init__(self):
        super(EventContainer,self).__init__()
 
        from html_wdg import HtmlElement
        self.script = HtmlElement.script()
        self.add_widget(self.script)


    def get_event(self, event_name):
        return Event(event_name)

    def set_mode(self, value):
        self.script.set_attr('mode', value)

    def add_listener(self, event_name, script_text, replace=False):
        # generate a unique function name
        ref_count = Container.get("EventContainer:ref_count")
        if ref_count == None:
            cur_time = str(int(time.time()))
            # the last few digits of the current time
            ref_count = int(cur_time[-5:])

        function = "event_listener_%s" % ref_count
        Container.put("EventContainer:ref_count", ref_count + 1 )

        self.script.add("function %s() { %s }\n" % (function, script_text) )
        self.add_listener_func( event_name, function, replace )

    def add_listener_func(self, event_name, function_name, replace=False):
        
        replace_state = "false"
        if replace:
             replace_state = "true"
        self.script.add("EventContainer.get().register_listener('%s', %s, %s);\n" \
            % (event_name, function_name, replace_state) )

    def add_refresh_listener(self, event_name):
        self.add_listener(event_name, self.get_refresh_caller() )



    def get_unique_event_name(self):
        # generate a unique function name
        ref_count = Container.get("EventContainer:ref_count")
        if ref_count == None:
            ref_count = 0

        event_name = "event_name_%s" % ref_count
        Container.put("EventContainer:ref_count", ref_count + 1 )

        return event_name


    def get_event_caller(self, event_name):
        '''gets the event caller function'''
        return "EventContainer.get().call_event('%s')" % event_name


    def get_display(self):
        if len(self.script.get_children() ) == 0:
            return ""
         
        return super(EventContainer,self).get_display()


    # event names
    DATA_EDIT = "refresh|data_edit"
    DATA_INSERT = "refresh|data_insert"

    def get_data_insert_caller(self):
        return self.get_event_caller( self.DATA_INSERT )

    def get_data_update_caller(self):
        return self.get_event_caller( self.DATA_EDIT )

    def get_refresh_caller(self):
        return "document.form.submit()"
    




