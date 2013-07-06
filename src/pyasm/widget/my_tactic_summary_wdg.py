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


__all__ = ['MyTacticSummaryWdg']

from pyasm.common import *
from pyasm.search import *
from pyasm.biz import *
from pyasm.web import Widget, DivWdg
from pyasm.widget import TableWdg, BaseTableElementWdg


class MyTacticSummaryWdg(BaseTableElementWdg):
    def __init__(my, project_code=None):
        super(MyTacticSummaryWdg,my).__init__()
        if project_code:
            my.project_code = project_code
        else:
            my.project_code = Project.get_project_code()


    def get_display(my):
        widget = DivWdg()
        widget.add_style("font-size: 1.2em")

        widget.add( MyTacticNotificationWdg(my.project_code) )
        widget.add( MyTacticCheckinWdg(my.project_code) )
        widget.add( MyTacticStatusWdg(my.project_code) )
        widget.add( MyTacticTaskWdg(my.project_code) )


        return widget

class MyTacticBaseWdg(Widget):
    def __init__(my, project_code=None):
        super(MyTacticBaseWdg,my).__init__()
        if project_code:
            my.project_code = project_code
        else:
            my.project_code = Project.get_project_code()

    def set_project(my, project_code):
        my.project_code = project_code



class MyTacticNotificationWdg(MyTacticBaseWdg):

    def get_display(my):

        widget = DivWdg()

        # get the current project
        user = Environment.get_user_name()

        widget.add("Notifications received: ")

        for time in ('1 hour', 'today', '1 week'):
            search = Search("sthpw/notification_login")
            search.add_filter("project_code", my.project_code)
            search.add_filter("login", user)

            search.add_interval_filter("timestamp", time)

            count = search.get_count()

            widget.add("%s (%s new) " % (time,count))
        return widget




class MyTacticCheckinWdg(MyTacticBaseWdg):

    def get_display(my):

        widget = DivWdg()

        # get the current project
        user = Environment.get_user_name()

        widget.add("Checkins: ")
        for time in ('1 hour', 'today', '1 week'):
            search = Search("sthpw/snapshot")
            search.add_filter("login", user)

            # TODO: snapshot really should have a project code
            search.add_regex_filter("search_type", 'project=%s'% my.project_code, op='EQ')

            search.add_interval_filter("timestamp", time)

            count = search.get_count()

            widget.add("%s (%s new) " % (time,count))
        return widget





class MyTacticStatusWdg(MyTacticBaseWdg):

    def get_display(my):

        widget = DivWdg()

        # get the current project
        user = Environment.get_user_name()

        times = ['1 hour', 'today', '1 week']
        counts = []
        messages = []
        for time in times:
            search = Search("sthpw/status_log")
            search.add_filter("login", user)
            search.add_filter("project_code", my.project_code)
            search.add_where(Select.get_interval_where(time))
            count = search.get_count()
            counts.append(count)

            messages.append("%s (%s set)" % (time, count) )


        widget.add("Status Changes - %s" % (messages) )

        return widget




class MyTacticTaskWdg(Widget):

    def get_display(my):

        widget = DivWdg()

        # get the current project
        project_code = Project.get_project_name()
        user = Environment.get_user_name()

        pipeline = Pipeline.get_by_code("task")
        process_names = pipeline.get_process_names()

        widget.add("Tasks Assigned: ")
        for status in process_names:
            search = Search("sthpw/task")
            #search.add_filter("project_code", project_code)
            search.add_filter("assigned", user)
            search.add_filter("status", status)

            #search.add_where("now() - timestamp < '1 day'")

            count = search.get_count()
            if not count:
                continue

            widget.add("%s (%s) " % (status,count))
        return widget







        




