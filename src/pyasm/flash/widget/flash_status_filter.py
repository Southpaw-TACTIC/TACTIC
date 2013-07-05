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
__all__ = ['FlashStatusFilter','FlashStatusViewFilter']

from pyasm.common import SetupException
from pyasm.biz import *
from pyasm.web import *
from pyasm.widget import *
from pyasm.search import Search

class FlashStatusFilter(Widget):

    def __init__(my, pipeline_name="dept"):
        my.pipeline_name = pipeline_name
        my.pipeline = Pipeline.get_by_name(pipeline_name)

        super(FlashStatusFilter,my).__init__(my)

    def init(my):
        if my.pipeline == None:
            raise SetupException("Pipeline [%s] does not exist" % my.pipeline_name)
        
        processes = my.pipeline.get_process_names()
        processes.append("all")

        # copy for labels and add an "All"
        labels = [x.capitalize() for x in processes]

        my.status_select = SelectWdg("status_filter")
        my.status_select.add_style("font-size: 0.9em")
        my.status_select.set_option("values", processes)
        my.status_select.set_option("labels", labels)
        my.status_select.set_persistence()
        my.status_select.set_submit_onchange()
        status = my.status_select.get_value()
       

        my.add(HtmlElement.b("Status:"))
        my.add( my.status_select )
        state = WebState.get()
        state.add_state("status_filter", status)
    
    def alter_search(my, search):
        status_value = my.get_value()
        if status_value == "artist":
            where = "(status is NULL or %s)" \
                % Search.get_regex_filter('status', status_value)
            search.add_where( where )
        elif status_value != 'all':
            where = Search.get_regex_filter('status', status_value)
            search.add_where( where )
    
    def get_value(my):
        value = my.status_select.get_value()
        return value





class FlashStatusViewFilter(FlashStatusFilter):
    '''A filter for the different view of the Serial Status Wdg'''
    
    def init(my):
        
        filter_vals = [SerialStatusWdg.CONNECTION_VIEW, SerialStatusWdg.SIMPLE_VIEW]
       
        labels = [x.capitalize() for x in filter_vals]

        my.status_select = SelectWdg("status_view_filter")
        my.status_select.add_style("font-size: 0.9em")
        my.status_select.set_option("values", filter_vals)
        my.status_select.set_option("labels", labels)
        my.status_select.set_option("default", SerialStatusWdg.SIMPLE_VIEW)
        my.status_select.set_persistence()
        my.status_select.set_submit_onchange()
        my.status_select.get_value()

        span = SpanWdg(HtmlElement.b("View:"), css='small')
        span.add(my.status_select)
        my.add(span)
       
    def alter_search(my, search):
        pass


