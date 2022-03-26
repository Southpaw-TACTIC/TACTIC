###########################################################
#
# Copyright (c) 2014, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#


__all__ = ['GanttTaskRowWdg']



from pyasm.common import SPTDate
from pyasm.search import Search, SearchType
from pyasm.security import Sudo
from pyasm.biz import Pipeline, Task
from pyasm.web import DivWdg

from datetime import datetime, timedelta

import dateutil

from .gantt_item_wdg import BaseGanttRowWdg, BaseGanttRangeWdg

import six
basestring = six.string_types


class GanttTaskRowWdg(BaseGanttRowWdg):


    def get_display(self):

        row_search_key = self.kwargs.get("search_key")

        mode = self.kwargs.get("mode")

        task_keys = self.kwargs.get("task_keys")
        if mode != "preview":
            if task_keys != None:
                sobjects = Search.get_by_search_keys(task_keys)
                if sobjects:
                    sobject = sobjects[0]
                    search_key = sobject.get_search_key()
                else:
                    sobject = None
                    search_key = None
            else:
                sobject = self.sobject
                sobjects = [sobject]
                search_key = None
        else:
            sobject = self.kwargs.get('sobject')
            sobjects = [sobject]
            search_key = sobject.get_search_key()

        start_date = self.kwargs.get("start_date")
        end_date = self.kwargs.get("end_date")
        group_level = self.kwargs.get("group_level")

        is_template = self.kwargs.get("is_template")



        self.range_index = 0
        self.vacations = {}






        # this is the actual outside of the row
        item_div = self.top
        item_div.add_class("spt_gantt_row_item")
        item_div.add_attr("spt_search_key", search_key)
        item_div.add_class("spt_range_top")
        item_div.add_attr("spt_gantt_type", "task")

        item_div.add_attr("SPT_ACCEPT_DROP", "spt_range_top")

        item_div.add_style("height: 23px")
        item_div.add_style("width: 100%")
        item_div.add_style("position: relative")
        item_div.add_style("z-index: %s" % (100-self.range_index))
        self.range_index += 1

        item_div.add_style("border-style", "solid")
        item_div.add_style("border-width", "0px 0px 1px 0px")
        theme = item_div.get_color("theme")
        if theme == "dark":
            item_div.add_color("border-color", "#000")
        else:
            item_div.add_color("border-color", "#EEE")

        item_div.add_style("box-sizing", "border-box")


        for index, sobject in enumerate(sobjects):

            kwargs = {
                "row_search_key": row_search_key,
                "sobject": sobject,
                "start_date": start_date,
                "end_date": end_date,
                "group_level": group_level,
                "index": index,
                "percent_per_day": self.percent_per_day,
                "nobs_mode": self.nobs_mode,
                "mode": self.kwargs.get("mode") or None,
                "processes": self.kwargs.get("processes") or None
            }



            task_type = sobject.get_value("task_type", no_exception=True) or "task"

            # delegate a range handler
            if task_type == "milestoneX":
                # FIXME: for some reason, this doesn't work to drag
                range_wdg = GanttTaskMilestoneWdg(**kwargs)
            else:
                range_wdg = GanttTaskRangeWdg(**kwargs)

            item_div.add(range_wdg)

        return item_div





class GanttTaskRangeWdg(BaseGanttRangeWdg):

    def get_display(self):
        sobject = self.kwargs.get("sobject")
        start_date = self.kwargs.get("start_date")
        end_date = self.kwargs.get("end_date")
        group_level = self.kwargs.get("group_level")
        
        self.range_index = self.kwargs.get("index")
        self.vacations = {}

        self.percent_per_day = self.kwargs.get("percent_per_day")
        self.nobs_mode = self.kwargs.get("nobs_mode")


        is_template = self.kwargs.get("is_template")

        search_key = sobject.get_search_key()


        task = sobject

        task_key = task.get_search_key()

        assigned = task.get_value("assigned")
        status = task.get_value("status")

        # incorporate workflow dependency

        task_pipeline_code = task.get_value("pipeline_code")
        if not task_pipeline_code:
            task_pipeline_code = "task"
        task_pipeline = Pipeline.get_by_code(task_pipeline_code)

        depend_keys = self.get_depend_keys(task)


        process = task.get_value("process")


        # set the color by status
        status = task.get_value("status")
        color = None
        if task_pipeline:
            status_obj = task_pipeline.get_process(status)
            if status_obj:
                color = status_obj.get_color()
        if not color:
            color = "rgba(207,215,188,1.0)"


        bid_start_date = task.get_datetime_value("bid_start_date")
        bid_end_date = task.get_datetime_value("bid_end_date")
        bid_duration = task.get_value("bid_duration")


        top_margin = 4

        if not bid_start_date:
            today = datetime.today()
            bid_start_date = datetime(today.year, today.month, today.day)

        if not bid_end_date:
            bid_end_date = bid_start_date + timedelta(days=1)
            bid_end_date = datetime(bid_end_date.year, bid_end_date.month, bid_end_date.day)


        # set the time for full days
        snap_mode = "day"
        if snap_mode == "day":
            bid_start_date = SPTDate.strip_time(bid_start_date)
            bid_end_date = SPTDate.strip_time(bid_end_date) + timedelta(days=1) - timedelta(seconds=1)



        offset = self.get_percent(start_date, bid_start_date)
        if offset < 0:
            offset = 0

        width = self.get_percent(bid_start_date, bid_end_date)


        # deal with vacations
        # TODO: move this outside this function
        #if assigned:
        """
        if False:
            vacation_list = self.vacations.get(assigned) or []

            for vacation in vacation_list:
                vacation_start_date = vacation.get("bid_start_date")
                vacation_end_date = vacation.get("bid_end_date")


                vacation_offset = self.get_percent(start_date, vacation_start_date)
                if vacation_offset < 0:
                    vacation_offset = 0

                vacation_width = self.get_percent(vacation_start_date, vacation_end_date)


                vacation_div = DivWdg()
                item_div.add(vacation_div)
                vacation_div.add_class("spt_gantt_element")
                vacation_div.add_attr("spt_start_date", vacation_start_date)
                vacation_div.add_attr("spt_end_date", vacation_end_date)

                vacation_div.add_style("position: absolute")
                vacation_div.add_style("top: 0px")
                vacation_div.add_style("left: %s%%" % vacation_offset)
                vacation_div.add_style("width: %s%%" % vacation_width)
                vacation_div.add_style("height: 12px")
                vacation_div.add_style("background: #A66")
                vacation_div.add_style("color: #FFF")
                vacation_div.add_style("font-size: 0.8em")
                vacation_div.add_style("vertical_align: middle")
                vacation_div.add_style("text-align: center")
                vacation_div.add_style("overflow: hidden")

                vacation_process = vacation.get_value("process")

                vacation_div.add(vacation_process)
        """





        # draw the individual element
        range_div = DivWdg()
        range_div.add_class("spt_range")
        range_div.add_class("spt_gantt_element")


        row_search_key = self.kwargs.get("row_search_key")
        if not row_search_key:
            range_div.add_attr("spt_search_key", task_key)
        else:
            range_div.add_attr("spt_search_key", row_search_key)
            range_div.add_attr("spt_update_key", task_key)

 
        """
        if is_template in [True, 'true']:
            range_div.add_behavior( {
            'type': 'loadX',
            'cbjs_action': '''
            var el = bvr.src_el;
            el.copy_template = function() {

                var clone = spt.behavior.clone(el);

            }

            '''
            } )
        """

        statuses = Task.get_status_colors().get("task")

        cbjs_action = '''
            var statuses = %s;

            if (bvr.src_el.hasClass("spt_changed")) {
                var sobject = bvr.value;
                var status = sobject["status"];
                var background = statuses[status];
                var nob_updates = bvr.src_el.getElements(".spt_nob");
                bvr.src_el.setStyle("background", background);
                bvr.src_el.getElement("div").setStyle("background", background);
                nob_updates[0].setStyle("background", background);
                nob_updates[1].setStyle("background", background);

            } else {
                var sobject = bvr.value;
                var start_date = sobject.start_date;
                var due_date = sobject.due_date;
                spt.gantt.set_date(bvr.src_el, sobject.bid_start_date, sobject.bid_end_date);
                
                var status = sobject["status"];
                
                var background = statuses[status];

                var nob_updates = bvr.src_el.getElements(".spt_nob");
                start_date = moment(start_date).format("MMM D");
                due_date = moment(due_date).format("MMM D");
                bvr.src_el.getElement("div").setStyle("background", background);
                bvr.src_el.setStyle("background", background);
                nob_updates[0].setStyle("background", background);
                nob_updates[0].innerHTML = start_date;
                nob_updates[1].setStyle("background", background);
                nob_updates[1].innerHTML = due_date;
            }
            
            
        ''' % statuses


        range_div.add_update( {
            'search_key': search_key,
            'return': 'sobject',
            'cbjs_action': cbjs_action
        } )
    



        if depend_keys:
            range_div.add_attr("spt_depend_keys", ",".join(depend_keys) )


        bid_start_date_str = bid_start_date.strftime("%Y-%m-%d %H:%M")
        bid_end_date_str = bid_end_date.strftime("%Y-%m-%d %H:%M")
        range_div.add_attr("spt_start_date", bid_start_date_str)
        range_div.add_attr("spt_end_date", bid_end_date_str)
        range_div.add_style("z-index: 10")



        range_div.add_style("opacity: 0.8")
        range_div.add_attr("spt_duration", bid_duration)

        # position the range
        range_div.add_style("position", "absolute")
        range_div.add_style("left: %s%%" % offset)



        # draw the range shape
        border_color = range_div.get_color("border", -20)


        description = task.get_value("description")
        if not description:
            description = task.get_value("process")

        #range_div.add_style("font-size: 0.8em")


        task_type = task.get_value("task_type", no_exception=True)

        if task_type in ["milestone", "delivery"]:

            range_div.add_attr("spt_range_type", "milestone")
            range_div.add_attribute("spt_drag_mode", "move")

            milestone_wdg = self.get_milestone_wdg(sobject, color)
            range_div.add( milestone_wdg )
            milestone_wdg.add_style("pointer-events: none")

            #range_div.add("<div style='font-weight: bold; height: 100%%; width: auto; max-width: 150px; text-overflow: ellipsis; white-space: nowrap; overflow: hidden; pointer-events: none; margin-top: -13px; margin-left: 25px;'>%s</div>" % description)
            range_div.add("<div style='font-size: 0.8em; font-weight: bold; height: 100%%; width: auto; max-width: 150px; text-overflow: ellipsis; white-space: nowrap; overflow: hidden; pointer-events: none; margin-top: -15px; margin-left: 22px; background: #FFF; border: solid 1px #DDD; border-radius: 5px; padding: 2px;'>%s</div>" % description)
            range_div.add_style("margin-top: %spx" % top_margin)
            has_nobs = False

        else:
            range_div.add_attr("spt_range_type", "range")


            range_div.add_class("hand")
            range_div.add_style("margin-top: %spx" % top_margin)
            range_div.add_style("height: 18px")


            range_div.add_style("border-style: solid")
            range_div.add_style("border-width: 1px")
            range_div.add_style("border-color: %s" % border_color)

            range_div.add_style("width: %s%%" % width)

            range_div.add_style("background: %s" % color)

            has_nobs = True






            task_diff = bid_end_date - bid_start_date
            task_duration = float(task_diff.days) + float(task_diff.seconds)/(24*3600)

            task_breaks = [
                    { 'offset': 1, 'duration': 2, 'color': '#FFF' },
                    { 'offset': 5, 'duration': 2, 'color': '#FFF' } ,
                    { 'offset': 2, 'duration': 0.5, 'color': '#0FF' }
            ]
            task_breaks = []

            task_data = task.get_json_value("data") or {}
            if task_data:
                task_breaks = task_data.get("break") or {}



            #task_breaks = []

            if task_breaks:

                # add some breaks
                days_div = DivWdg()
                range_div.add(days_div)
                days_div.add_style("position: absolute")
                days_div.add_style("z-index: 10")
                days_div.add_style("top: 0px")
                days_div.add_style("height: 100%")
                days_div.add_style("width: 100%")
                days_div.add_style("overflow: hidden")
                days_div.add_style("pointer-events: none")



                for task_break in task_breaks:

                    day_div = DivWdg()
                    days_div.add(day_div)

                    break_offset = float(task_break.get("offset")) / task_duration * 100
                    break_duration = float(task_break.get("duration")) / task_duration * 100
                    break_color = task_break.get("color") or "#FFF"


                    day_div.add_style("display: inline-block")
                    day_div.add_style("position: absolute")
                    day_div.add_style("box-sizing: border-box")
                    day_div.add_style("height: 100%")
                    day_div.add_style("width: %s%%" % break_duration)
                    day_div.add_style("top: 0px")
                    day_div.add_style("left: %s%%" % break_offset)
                    day_div.add("&nbsp;")

                    day_div.add_style("background: %s" % break_color)





            show_description = True
            if show_description:


                # add a description

                text_div = DivWdg()
                range_div.add(text_div)
                text_div.add_style("position: relative")
                text_div.add_style("height: 100%")
                text_div.add_style("z-index: 100")
                text_div.add_style("text-overflow: ellipsis")
                text_div.add_style("white-space: nowrap")
                text_div.add_style("overflow: hidden")
                text_div.add_style("pointer-events: none")
                text_div.add_style("margin: 0px 3px")
                text_div.add(description)


        if process:
            range_div.add_attr("spt_process", process)
            #detail_span.add("Process: %s" % process)


        #detail_span.add("<br clear='all'/>")
        if description and description != process:
            range_div.add_attr("spt_description", description)
            #detail_span.add("Description: %s" % description)
            #detail_span.add("<br clear='all'/>")

        if assigned:
            sudo = Sudo()
            try:
                user = Search.get_by_code("sthpw/login", assigned)
            finally:
                sudo.exit()
            name = assigned
            if user:
                name = user.get_value("display_name")
                if not name:
                    name = user.get_value("login")
            range_div.add_attr("spt_assigned", name)
            #detail_span.add("Assigned: %s" % name)
            #detail_span.add("<br clear='all'/>")


        if status:
            range_div.add_attr("spt_status", status)
            #detail_span.add("Status: %s" % status)
            #detail_span.add("<br clear='all'/>")


        days = (bid_end_date - bid_start_date).days + 1
        range_div.add_attr("spt_length", days)
        #detail_span.add("Length: %s days" % days)
        #detail_span.add("<br clear='all'/>")



        start_display = bid_start_date.strftime("%b %d")
        end_display = bid_end_date.strftime("%b %d")

        range_div.add_attr("spt_start_display", start_display)
        range_div.add_attr("spt_end_display", end_display)

        if self.nobs_mode != "none" and has_nobs:
            range_div.add_attr("spt_has_nobs", True)
        else:
            range_div.add_attr("spt_has_nobs", False)




        # add some nobs
        if self.nobs_mode != "none" and has_nobs:
            left = DivWdg()
            range_div.add(left)
            left.add_class("spt_nob")
            left.add_class("spt_nob_update")
            left.add_style("display: none")
            left.add_style("position: absolute")
            #left.add_style("width: 10px")
            #left.add_style("height: 10px")
            left.add_style("border: solid 1px %s" % border_color)
            left.add_style("border-radius: 10px 0px 0px 10px")
            left.add_style("left: -39px")
            left.add_style("top: -1px")
            left.add_style("padding: 2px 3px")
            left.add_style("background", color)
            left.add_style("font-size", "0.8em")
            #left.add_style("opacity", 0.75)
            left.add(start_display)

            right = DivWdg()
            range_div.add(right)
            right.add_class("spt_nob")
            right.add_class("spt_nob_update")
            right.add_style("display: none")
            right.add_style("position: absolute")
            #right.add_style("width: 10px")
            #right.add_style("height: 10px")
            right.add_style("border: solid 1px %s" % border_color)
            right.add_style("border-radius: 0px 10px 10px 0px")
            right.add_style("right: -39px")
            right.add_style("top: -1px")
            right.add_style("padding: 2px 3px")
            right.add_style("background", color)
            right.add_style("font-size", "0.8em")
            #right.add_style("opacity", 0.75)
            right.add(end_display)


        return range_div




    def get_depend_keys(self, task):

        process = task.get("process")
        mode = self.kwargs.get("mode")

        # TODO: this may be slow to do for every task.  Maybe better to do
        # in bulk.  Also, this may be better done at initial task creation.
        if mode != 'preview':
            try:
                parent = task.get_parent()
            except Exception as e:
                print("WARNING: Error finding parent for task [%s]" % task.get_code(), task.get("search_code"))
                parent = None
 
            if not parent:
                return []
            pipeline_code = parent.get_value("pipeline_code", no_exception=True)
        else:
            pipeline_code = task.get_value('pipeline_code')
            parent = SearchType.create('workflow/job')
            parent.set_value("pipeline_code", pipeline_code)
            parent.set_value('job_code', 'TMP00001')
        

        if pipeline_code:
            pipeline = Pipeline.get_by_code(pipeline_code)
        else:
            pipeline = None

        if not pipeline:
            return []


        # Attempt to remap pipeline process and pipeline
        # FIXME: This should be improved
        parent_process = None
        parent_pipeline = pipeline

        if process.find("/") != -1:
            parts = process.split("/")
            parent_process = parts[0]

            s = Search("config/process")
            s.add_filter("pipeline_code", pipeline_code)
            s.add_filter("process", parent_process)
            parent_process_sobj = s.get_sobject()

            if parent_process_sobj:
                process = parts[1]
                pipeline_code = parent_process_sobj.get("subpipeline_code")
                if pipeline_code:
                    pipeline = Pipeline.get_by_code(pipeline_code)



        process_obj = pipeline.get_process(process)


        depend_keys = []


        # need to build a dependency tree ...
        output_processes = pipeline.get_output_processes(process)


        last_hierarchy_node  = False
        if parent_process and not output_processes:
            processes = parent_pipeline.get_processes()
            index = 0
            last_hierarchy_node = True

            for i in range(len(processes)):
                process = processes[i]
                process_type = process.get_type()

                if process_type == "hierarchy":
                    index = min(i + 1, len(processes))

            output_processes = [processes[index]]   


        # get the task key that this is dependent
        for output_process in output_processes:
            output_process_name = output_process.get_name()
            output_process_type = output_process.get_type()

            if output_process_type == "hierarchy":
                s = Search("config/process")
                s.add_filter("pipeline_code", pipeline_code)
                s.add_filter("process", output_process_name)
                output_process_sobj = s.get_sobject()

                if output_process_sobj:
                    subpipeline_code = output_process_sobj.get("subpipeline_code")
                else:
                    subpipeline_code = None


                if subpipeline_code:
                    subpipeline = Pipeline.get_by_code(subpipeline_code)
                    subpipeline_process_names = subpipeline.get_process_names()
                    if subpipeline_process_names:
                        first = subpipeline_process_names[0]
                        output_process_name = "%s/%s" % (output_process_name, first)


            if parent_process and not last_hierarchy_node:
                output_process_name = "%s/%s" % (parent_process, output_process_name)


            # FIXME: this is slow ... should get from a cache
            if mode == "preview":
                processes = self.kwargs.get("processes") or None
                is_visited = []
                if isinstance(output_process_name, list):
                    output_process_names = output_process_name
                elif isinstance(output_process_name, basestring):
                    output_process_names = [output_process_name]
                else:
                    output_process_names = []

                output_keys = [output_process_name]
                if output_process_name and output_process_name not in processes.keys():
                    output_keys = []
                    while output_process_names:
                        try:
                            output_process_name = output_process_names.pop()
                        except IndexError:
                            break
                        if output_process_name not in is_visited:
                            if output_process_name in processes.keys():
                                output_keys.append(output_process_name)
                            else:
                                output_processes = pipeline.get_output_processes(output_process_name)
                                for x in output_processes:
                                    output_process_names.insert(0, x.get_name())
                            is_visited.append(output_process_name)

            else:
                output_tasks = Task.get_by_sobject(parent, process=output_process_name)

                if output_tasks == []:
                    output_tasks = self.get_nearest_child_tasks(pipeline, parent, output_process_name, set([process]))
                output_keys = [x.get_search_key() for x in output_tasks]
            depend_keys.extend(output_keys)

        return depend_keys


    def get_nearest_child_tasks(self, pipeline, tasks_parent, process_name, visited):
        output_tasks = []
        # detect repeated cycle        
        if process_name in visited:
            return output_tasks
        visited.add(process_name)
        output_processes = pipeline.get_output_processes(process_name)
        for output_process in output_processes:
            output_process_name = output_process.get_name()
            output_tasks_subset = Task.get_by_sobject(tasks_parent, process=output_process_name)
            if output_tasks_subset == []:
                output_tasks_subset = self.get_nearest_child_tasks(pipeline, tasks_parent, output_process_name, visited)
            output_tasks.extend(output_tasks_subset)
        return output_tasks



    def get_milestone_wdg(cls, sobject, color="#FFF", accent="#333", size=10):

        top = DivWdg()
        top.add_class("spt_milestone")
        border_color = top.get_color("border")
        border_color = "#000"

        top.add_style("height: 100%")

        inner = DivWdg()
        top.add(inner)
        inner.add_class("spt_milestone_display")
        inner.add_style("height: %s" % size)
        inner.add_style("width: %s" % size)
        inner.add_style("background: %s" % color)
        inner.add_style("border: solid 1px %s" % border_color)
        inner.add_style("transform: rotate(45deg)")
        inner.add_style("margin-top: 3px")

        inner.add_attr("spt_hover_color", accent)

        return top

    get_milestone_wdg = classmethod(get_milestone_wdg)





class GanttTaskMilestoneWdg(BaseGanttRangeWdg):

    def get_display(self):


        sobject = self.kwargs.get("sobject")
        start_date = self.kwargs.get("start_date")
        end_date = self.kwargs.get("end_date")
        group_level = self.kwargs.get("group_level")
        
        self.range_index = self.kwargs.get("index")
        self.vacations = {}

        self.percent_per_day = self.kwargs.get("percent_per_day")
        self.nobs_mode = self.kwargs.get("nobs_mode")


        is_template = self.kwargs.get("is_template")

        task = sobject
        task_key = task.get_search_key()

        bid_start_date = task.get_datetime_value("bid_start_date")
        bid_end_date = task.get_datetime_value("bid_end_date")
        bid_duration = task.get_value("bid_duration")


        description = task.get_value("description")
        if not description:
            description = task.get_value("process")



        if not bid_start_date:
            today = datetime.today()
            bid_start_date = datetime(today.year, today.month, today.day)

        if not bid_end_date:
            bid_end_date = bid_start_date + timedelta(days=1)
            bid_end_date = datetime(bid_end_date.year, bid_end_date.month, bid_end_date.day)


        offset = self.get_percent(start_date, bid_start_date)
        if offset < 0:
            offset = 0

        width = self.get_percent(bid_start_date, bid_end_date)










        # draw the individual element
        range_div = DivWdg()
        range_div.add_class("spt_range")
        range_div.add_class("spt_gantt_element")
        range_div.add_class("hand")
        range_div.add_attr("spt_search_key", task_key)


        bid_start_date_str = bid_start_date.strftime("%Y-%m-%d %H:%M")
        bid_end_date_str = bid_end_date.strftime("%Y-%m-%d %H:%M")
        range_div.add_attr("spt_start_date", bid_start_date_str)
        range_div.add_attr("spt_end_date", bid_end_date_str)
        #range_div.add_style("z-index: 10")




        range_div.add_style("opacity: 0.8")
        range_div.add_attr("spt_duration", bid_duration)

        # position the range
        range_div.add_style("position", "absolute")
        range_div.add_style("left: %s%%" % offset)



        # get the task pipelne
        task_pipeline_code = task.get_value("pipeline_code")
        if not task_pipeline_code:
            task_pipeline_code = "task"
        task_pipeline = Pipeline.get_by_code(task_pipeline_code)

        # set the color by status
        status = task.get_value("status")
        color = None
        if task_pipeline:
            status_obj = task_pipeline.get_process(status)
            if status_obj:
                color = status_obj.get_color()
        if not color:
            color = "rgba(207,215,188,1.0)"


        milestone = self.get_milestone_wdg(sobject, color=color)
        range_div.add(milestone)

        range_div.add("<div style='font-weight: bold; height: 100%%; width: auto; min-width: 150px; max-width: 150px; text-overflow: ellipsis; white-space: nowrap; overflow: hidden; pointer-events: none; margin-top: -13px; margin-left: 18px;'>%s</div>" % description)

        return range_div




    def get_milestone_wdg(cls, sobject, color="#FFF", accent="#333", size=10):

        top = DivWdg()
        top.add_class("spt_milestone")
        border_color = top.get_color("border")
        border_color = "#000"

        top.add_style("height: 100%")

        inner = DivWdg()
        top.add(inner)
        inner.add_class("spt_milestone_display")
        inner.add_style("height: %s" % size)
        inner.add_style("width: %s" % size)
        inner.add_style("background: %s" % color)
        inner.add_style("border: solid 1px %s" % border_color)
        inner.add_style("transform: rotate(45deg)")
        inner.add_style("margin-top: 5px")

        inner.add_attr("spt_hover_color", accent)

        return top

    get_milestone_wdg = classmethod(get_milestone_wdg)



