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

__all__ = ["ClientTabWdg"]

from pyasm.search import *
from pyasm.web import *
from pyasm.widget import *
from pyasm.prod.web import *
from editorial_tab_wdg import *


class ClientTabWdg(BaseTabWdg):
    
    TAB_NAME = "Client"     # 1st level tab name
    TAB_KEY = "client_tab"
    CLIENT_TAB = "Review"

    def init(my):
        my.setup_tab(my.TAB_KEY, css=TabWdg.SMALL)

    def handle_tab(my, tab):
        tab.add(my.get_client_wdg, my.CLIENT_TAB)

    def _get_aux_data(my, sobjs):
        info = SubmissionInfo(sobjs)
        aux_data = info.get_info()
        return aux_data 


    def get_client_wdg(my):

        widget = Widget()
    
        nav = DivWdg(css='filter_box')
       
        span = SpanWdg(css="med")
        span.add("Bin: ")
        bin_select = FilterSelectWdg("client_bin_select")
        bin_select.add_empty_option(label='-- Any Client Bin --', \
            value=SelectWdg.NONE_MODE)

        search = Search(Bin)
        search.add_filter("type", "client")
        search.add_order_by('code desc')
        bins = search.get_sobjects()
        bin_select.set_sobjects_for_options(bins, "id", "get_label()")
        if bins:
            bin_select.set_option("default", bins[0].get_id())
        span.add(bin_select)
        nav.add(span)


        span = SpanWdg(css="med")
        span.add("Status: ")
        status_filter = FilterSelectWdg("client_status_select")
        status_filter.add_empty_option("-- Any Status --")
        status_filter.set_option("setting", "client_submission_status")
        span.add(status_filter)
        nav.add(span)
       
     

        # create a search for the submissions
        search = Search(Submission)

         
        retired = RetiredFilterWdg()
        retired.alter_search(search)

        bin_id = bin_select.get_value()
        if not bin_id or bin_id == SelectWdg.NONE_MODE:
            search.add_where("id in (select submission_id from " \
             " submission_in_bin"\
             " where bin_id in (select id from bin where type = 'client'))")
        elif bin_id:
            
           search.add_where("id in (select submission_id from "\
            " submission_in_bin"\
            " where bin_id = %s)" %bin_id)
        else:
            search.add_where("NULL")
        search.add_order_by('timestamp desc')

        all_sobjs = search.get_sobjects()
        all_aux_data = my._get_aux_data(all_sobjs)

        status_filter_value = status_filter.get_value()
        if status_filter_value:
            search.add_filter("status", status_filter_value)

        table = TableWdg(Submission.SEARCH_TYPE, "client")
        
        filter_span = SubmissionItemFilterWdg(all_aux_data, all_sobjs)
        filter_span.alter_search(search)

        # add a search limit
        search_limit = SearchLimitWdg()
        search_limit.set_limit(50)
        search_limit.alter_search(search)
       
        # only get sobjects if there are actually bins
        if bins:
            sobjs = search.get_sobjects(redo=True)
        else:
            sobjs = []


        table.set_sobjects(sobjs)

     
        aux_data = my._get_aux_data(sobjs)
        table.set_aux_data(aux_data)
        widget.add(nav)
        
        
        nav.add(filter_span)
        nav.add(retired)
        nav.add(search_limit)
        widget.add(table)
    
        return widget
        



    def get_undo_wdg(my):
        widget = UndoLogWdg()
        return widget







