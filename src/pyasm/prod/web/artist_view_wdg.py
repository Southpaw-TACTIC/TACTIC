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

__all__=['ArtistViewWdg']

from pyasm.common import Environment
from pyasm.search import Search
from pyasm.biz import StatusEnum, Pipeline, Project
from pyasm.web import Widget, WebContainer, SpanWdg
from pyasm.widget import CheckboxWdg



class ArtistViewWdg(SpanWdg):

    def init(my):
        my.add("Show assigned only: ")
        my.checkbox = CheckboxWdg("show_assigned_only")
        my.checkbox.set_option("value", "on")
        my.checkbox.set_persistence()
        my.checkbox.add_event("onclick", "document.form.submit()")
        my.add(my.checkbox)


        my.add_class("med")



    def is_supervisor(my):
        # if the user is a supervisor, look at all of the assets
        project = Project.get_project_name()
        security = Environment.get_security()
        return security.check_access("prod/%s" % project, "model/supervisor", "true")

    def is_artist(my):
        # if the user is a artist, look at all of the assets
        project = Project.get_project_name()
        security = Environment.get_security()
        return security.check_access("prod/%s" % project, "model/artist", "true")


    def alter_search(my, search):

        # get all of the relevant tasks to the user
        task_search = Search("sthpw/task")
        task_search.add_column("search_id")

        # only look at this project
        project = Project.get_project_name()
        task_search.add_filter("search_type", search.get_search_type())

        # figure out who the user is
        security = Environment.get_security()
        login = security.get_login()
        user = login.get_value("login")



        print "is_artist: ", my.is_artist()
        print "is_supervisor: ", my.is_supervisor()


        # do some filtering
        web = WebContainer.get_web()
        show_assigned_only = my.checkbox.get_value()
        show_process = web.get_form_values("process")
        if not show_process or show_process[0] == '':
            show_process = []

        show_task_status = web.get_form_values("task_status")
        if not show_task_status or show_task_status[0] == '':
            show_task_status = []


        if show_assigned_only == "on":
            task_search.add_filter("assigned", user)

        if show_process:
            where = "process in (%s)" % ", ".join( ["'%s'" % x for x in show_process] )
            task_search.add_where(where)

        if show_task_status:
            where = "status in (%s)" % ", ".join( ["'%s'" % x for x in show_task_status] )
            task_search.add_where(where)
        else:
            task_search.add_where("NULL")




        # record the tasks
        my.tasks = task_search.get_sobjects()

        # get all of the sobject ids
        sobject_ids = ["'%s'" % x.get_value("search_id") for x in my.tasks]

        # get all of the sobjects related to this task
        if sobject_ids:
            search.add_where( "id in (%s)" % ", ".join(sobject_ids) )

        




class SupervisorViewWdg(Widget):

    def init(my):
        my.add("Process: ")
        checkbox = CheckboxWdg("process")
        checkbox.set_option("value", "on")
        checkbox.set_persistence()
        checkbox.add_event("onclick", "document.form.submit()")
        my.add(checkbox)


    def filter_sobjects(my, orig_sobjects):

        # look for groups that are relevant
        groups = Environment.get_security().get_groups()
        login = Environment.get_security().get_login()


        # either we are user centric or process centric
        user = login.get_value("login")

       
        sobjects = []


        # filter out sobjects that do not have appropriate tasks
        if orig_sobjects:
            search_type = orig_sobjects[0].get_search_type()
            ids = [str(x.get_id()) for x in orig_sobjects]

            search = Search("sthpw/task")
            search.add_filter("search_type", search_type)
            search.add_where("search_id in (%s)" % ",".join(ids) )


            # get only tasks assigned to a user
            show_assigned_only = True
            if show_assigned_only:
                search.add_filter("assigned", user)
                search.add_where("status in ('Pending','In Progress')")
                search.add_where("status is NULL")

            tasks = search.get_sobjects()
            task_search_ids = [int(x.get_value("search_id")) for x in tasks]

            # once we have all of the tasks for this episode, we filter
            # out any assets that don't have these tasks
            for orig_sobject in orig_sobjects:
                search_id = orig_sobject.get_id()
                if search_id in task_search_ids:
                    sobjects.append(orig_sobject)


        return sobjects






