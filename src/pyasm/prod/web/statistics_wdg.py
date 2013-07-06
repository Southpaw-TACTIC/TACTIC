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


__all__= ['EpisodeCompletionWdg', 'FrameCompletionWdg']

from pyasm.search import Search, SObject, SearchType
from pyasm.web import Widget, Table
from pyasm.widget import BaseTableElementWdg, TaskCompletionWdg
from pyasm.biz import Task
from pyasm.prod.biz import ProdSetting


class EpisodeCompletionWdg(TaskCompletionWdg):
    '''Shows the task completion for each episode'''

    def get_tasks(my, sobject):

        search_type = SearchType.get("prod/shot").get_full_key()

        # get all of the shots in the episode
        shots = sobject.get_all_children("prod/shot")
        ids = SObject.get_values(shots, "id")

        search = Search("sthpw/task")
        search.add_filter("search_type", search_type)
        search.add_filters("search_id", ids)
        return search.get_sobjects()




class FrameCompletionWdg(BaseTableElementWdg):
    '''Shows the frame completion for each episode'''

    def get_display(my):

        sobject = my.get_current_sobject()

        shots = sobject.get_all_children("prod/shot")
       
        task_dict = {}
        tasks = Task.get_by_sobjects(shots)
        for task in tasks:
            search_type = task.get_value("search_type")
            search_id = task.get_value("search_id")
            key = '%s|%s' % (search_type, search_id)

            task_array = task_dict.get(key)
            if not task_array:
                task_array = []
                task_dict[key] = task_array
            task_array.append(task)
            


        # TODO: get rid of this hard code
        approved = ['Complete', 'Approved', 'Final']

        widget = Widget()

        total = 0
        completion = {}
        # get all of the tasks in a shot
        for shot in shots:
            key = shot.get_search_key()
            tasks = task_dict.get(key)
            if not tasks:
                tasks = []

            frame_range = shot.get_frame_range()
            frames = frame_range.get_num_frames()

            total += frames

            is_complete = {}
            for task in tasks:
                process = task.get_value("process")
                status = task.get_value("status")

                if not completion.get(process):
                    completion[process] = 0

                if status not in approved:
                    is_complete[process] = False
                elif not is_complete.get(process):
                    is_complete[process] = True
                # only set to true, if no other process has set it to false
                elif is_complete.get(process) != False:
                    is_complete[process] = True

            for process, flag in is_complete.items():
                if flag:
                    completion[process] += frames

        table = Table(css="minimal")
        table.add_style("width: 100%")
        processes = completion.keys()

        table.add_row()
        for process in processes:
            time = my.convert_to_time(completion[process])
            td = table.add_cell("%s (%s)" % (time, completion[process]))
            if completion[process] == 0:
                td.add_style("color: #ccc")

        table.add_cell("%s (%s)" % (my.convert_to_time(total), total) )


        table.add_row_cell("<hr size='1'/>")
        table.add_row()
        for process in processes:
            td = table.add_cell("%s" % process)
            if completion[process] == 0:
                td.add_style("color: #ccc")
        table.add_cell("total")

        widget.add(table)
        return widget



    def convert_to_time(my, frames):
        fps = ProdSetting.get_value_by_key("fps")
        if not fps:
            fps = 24
        else:
            fps = int(fps)

        minutes = frames / (60*fps)
	frames = frames - (minutes*60*fps)
        seconds = frames / fps
        extra = frames % fps

        time = "%0.2dm:%0.2ds.%0.2d" % (minutes, seconds, extra)
        return time
