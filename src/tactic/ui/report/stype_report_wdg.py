###########################################################
#
# Copyright (c) 2012, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#

__all__ = ['STypeReportWdg']


from pyasm.search import Search, SearchType
from pyasm.biz import Pipeline, Project
from pyasm.web import DivWdg

from tactic.ui.common import BaseRefreshWdg


class STypeReportWdg(BaseRefreshWdg):

    def get_display(self):

        top = self.top
        #top.add_color("background", "background" )
        top.add_gradient("background", "background", 0, -10 )

        search_type = self.kwargs.get("search_type")
        assert(search_type)

        search_type_obj = SearchType.get(search_type)


        title = self.kwargs.get("title")
        if not title:
            title = search_type_obj.get_title()

        if title:
            date = "@FORMAT(@STRING($TODAY),'Dec 31, 1999')"
            date = Search.eval(date, single=True)

            title_wdg = DivWdg()
            top.add(title_wdg)
            title_wdg.add(title)
            title_wdg.add(" [%s]" % date)
            title_wdg.add_style("font-size: 14")
            title_wdg.add_color("background", "background3")
            title_wdg.add_color("color", "color3")
            title_wdg.add_style("padding: 10px")
            title_wdg.add_style("font-weight: bold")
            title_wdg.add_style("text-align: center")


        search = Search("sthpw/task")
        full_search_type = Project.get_full_search_type(search_type)
        search.add_filter("search_type", full_search_type)
        tasks = search.get_sobjects()

        # organize by search_key
        tasks_dict = {}
        for task in tasks:
            parent_search_type = task.get_value("search_type")
            parent_search_id = task.get_value("search_id")
            key = "%s|%s" % (parent_search_type, parent_search_id)

            task_list = tasks_dict.get(key)
            if task_list == None:
                task_list = []
                tasks_dict[key] = task_list

            task_list.append(task)



        # go through each sobject and find out where it is "at"
        search = Search(search_type)
        sobjects = search.get_sobjects()
        sobject_statuses = {}
        for sobject in sobjects:
            # get all the tasks for this sobject

            sobject_search_type = sobject.get_search_type()
            sobject_search_id = sobject.get_id()
            key = "%s|%s" % (sobject_search_type, sobject_search_id)

            tasks = tasks_dict.get(key)
            if not tasks:
                tasks = []

            # figure out where in the pipeline this sobject is based
            # on the statuses
            process_statuses = {}
            for task in tasks:
                actual_end_date = task.get_value("actual_end_date")
                if actual_end_date:
                    is_complete = True
                else:
                    is_complete = False

                process = task.get_value("process")
                process_statuses[process] = is_complete


            pipeline_code = sobject.get_value("pipeline_code")
            pipeline = Pipeline.get_by_code(pipeline_code)
            if not pipeline:
                process_names = []
            else:
                process_names = pipeline.get_process_names()
            sobject_status = None
            none_complete = True
            for process_name in process_names:
                is_complete = process_statuses.get(process_name)
                if is_complete == None:
                    continue
                if is_complete == False:
                    sobject_status = process_name
                    break

                none_complete = False


            if sobject_status == None:
                if none_complete:
                    if process_names:
                        sobject_status = process_names[0]
                    else:
                        sobject_status = "No process"
                else:
                    sobject_status = "Complete"


            sobject_statuses[key] = sobject_status



        # count the number of sobjects in each process
        count_dict = {}
        for key, process in sobject_statuses.items():

            count = count_dict.get(process)
            if count == None:
                count = 1
            else:
                count += 1

            count_dict[process] = count


        # find the pipelines
        search = Search("sthpw/pipeline")
        search.add_filter("search_type", search_type)
        pipelines = search.get_sobjects()

        chart_div = DivWdg()
        top.add(chart_div)
        chart_div.add_border()
        chart_div.add_style("width: 900")
        #chart_div.set_box_shadow("0px 0px 3px 3px")
        chart_div.center()
        chart_div.add_style("margin-top: 30px")
        chart_div.add_style("margin-bottom: 30px")
        #chart_div.add_gradient("background", "background", 0, -10 )
        chart_div.add_color("background", "background")


        # go through each process and find out how many sobjects are in each
        for pipeline in pipelines:
            process_names = pipeline.get_process_names()
            process_names.append("Complete")

            data_values = []
            for process in process_names:

                count = count_dict.get(process)
                data_values.append(count)



            from tactic.ui.chart.chart2_wdg import ChartWdg as ChartWdg
            from tactic.ui.chart.chart2_wdg import ChartData as ChartData

            width = 800
            height = 500
            chart_labels = process_names
            x_data=[i+0.5 for i,x in enumerate(chart_labels)]

            chart = ChartWdg(
                width=width,
                height=height,
                chart_type='bar',
                labels=chart_labels,
                label_values=x_data
            )
            chart_div.add(chart)



            chart_data = ChartData(
                #chart_type=chart_type,
                data=data_values,
                color="#00F",
                x_data=x_data
            )
            chart.add(chart_data)

        top.add("<br clear='all'/>")


        return top


