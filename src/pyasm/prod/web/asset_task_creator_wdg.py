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

__all__ = ['ShotTaskCreatorAction', 'ShotPipelineWdg']

from pyasm.search import Search, SearchType
from pyasm.command import DatabaseAction
from pyasm.web import Widget, DivWdg, SpanWdg, WebContainer, HtmlElement
from pyasm.widget import BaseInputWdg, CheckboxWdg, SelectWdg
from pyasm.biz import Task, Pipeline, Project



class ShotPipelineWdg(BaseInputWdg):

    def get_display(my):

        div = DivWdg()
        div.add_style("padding: 10px 0px 10px 0px")

        behavior = {
            'type': 'keyboard',
            'kbd_handler_name': 'DgTableMultiLineTextEdit'
        }
        div.add_behavior(behavior)


        project_code = None
        sobject = my.get_current_sobject()
        if sobject:
            project_code = sobject.get_project_code()
        project_filter = Project.get_project_filter(project_code)

        query_filter = my.get_option("query_filter")
        if not query_filter:
            # try getting it from the search_type
            web = WebContainer.get_web()
            search_type = web.get_form_value("search_type")
            if search_type:
                search_type_obj = SearchType.get(search_type)
                base_search_type = search_type_obj.get_base_search_type()
                query_filter = "search_type = '%s'" % base_search_type

        # add the project filter
        if query_filter:
            query_filter = "%s and %s" % (query_filter, project_filter)
        else:
            query_filter = project_filter

        my.set_option("query_filter", query_filter)

        select = SelectWdg()
        select.add_empty_option("-- Select --")
        select.copy(my)

        select.add_event("onchange", "alert('cow')")
        div.add(select)

        span = SpanWdg(css="med")
        span.add( "Add Initial Tasks: " )
        checkbox = CheckboxWdg("add_initial_tasks")
        checkbox.set_persistence()
        if checkbox.is_checked(False):
            checkbox.set_checked()
        span.add( checkbox )
        div.add(span)



        # list all of the processes with checkboxes
        pipeline_code = select.get_value()
        if pipeline_code:
            pipeline = Pipeline.get_by_code(pipeline_code)
            if not pipeline:
                print "WARNING: pipeline '%s' does not exist" %  pipeline_code
                return
            process_names = pipeline.get_process_names(recurse=True)

            process_div = DivWdg()
            for process in process_names:
                checkbox = CheckboxWdg("add_initial_tasks")
                process_div.add(checkbox)
                process_div.add("&nbsp;")
                process_div.add(process)
                process_div.add(HtmlElement.br())
            div.add(process_div)

        return div





class ShotTaskCreatorAction(DatabaseAction):
    '''creates the tasks that are part of the pipeline'''

    def execute(my):
        my.is_edit = not my.sobject.is_insert()
        super(ShotTaskCreatorAction,my).execute()


    def postprocess(my):
        web = WebContainer.get_web()
        add_initial_tasks = web.get_form_value("add_initial_tasks")

        if add_initial_tasks != "on":
            return

        Task.add_initial_tasks(my.sobject)


