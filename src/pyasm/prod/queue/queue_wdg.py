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

_all__ = ['QueueWdg']


from pyasm.search import Search
from pyasm.web import Widget, DivWdg, SpanWdg
from pyasm.widget import SelectWdg, TableWdg, SearchLimitWdg, TextWdg
from pyasm.prod.web import SearchFilterWdg

from queue import Queue



class QueueWdg(Widget):

    def init(my):

        search = Search("sthpw/queue")
        search.add_order_by("priority desc")
        search.add_order_by("timestamp desc")

        widget = Widget()

        div = DivWdg(css="filter_box")

        span = SpanWdg(css="med")
        search_filter = SearchFilterWdg(columns=Queue.get_search_columns())
        search_filter.alter_search(search)
        span.add(search_filter)
        div.add(span)


        span = SpanWdg(css="med")
        priority_wdg = TextWdg("priority_search")
        priority_wdg.set_persistence()
        priority = priority_wdg.get_value()
        if priority:
            search.add_filter("priority", priority)
        span.add("Priority: ")
        span.add(priority_wdg)
        div.add(span)


        select = SelectWdg("queue_state")
        select.set_option("values", "|pending|locked|error|done")
        select.set_option("labels", "All|pending|locked|error|done")
        select.add_event("onchange", "document.form.submit()")
        select.set_persistence()

        span = SpanWdg(css="med")
        span.add("State: ")
        span.add(select)
        div.add(span)
        queue_state = select.get_value()
        if queue_state != "":
            search.add_filter("state", queue_state)

        user_select = SelectWdg("user_select")
        user_select.add_empty_option()

        user_search = Search("sthpw/login")
        user_select.set_search_for_options(user_search,"login", "login")
        user_select.add_event("onchange", "document.form.submit()")
        user_select.set_persistence()

        div.add("User: ")
        div.add(user_select)
        queue_user = user_select.get_value()
        if queue_user != "":
            search.add_filter("login", queue_user)


        search_limit = SearchLimitWdg()
        search_limit.set_limit(10)
        div.add(search_limit)
        search_limit.alter_search(search)


        widget.add(div)

        sobjects = search.get_sobjects()

        table = TableWdg("sthpw/queue")
        table.set_sobjects(sobjects)
        widget.add(table)

        my.add(widget)



