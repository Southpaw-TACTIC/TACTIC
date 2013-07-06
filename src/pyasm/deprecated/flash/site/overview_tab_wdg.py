##########################################################
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

__all__ = ['OverviewTabWdg']

from pyasm.web import *
from pyasm.widget import *
from pyasm.flash.widget import *
from pyasm.search import SearchType, Search
from pyasm.prod.web import *


class OverviewTabWdg(Widget):


    def init(my):

        tab = TabWdg(css=TabWdg.SMALL)
        tab.set_tab_key("overview_tab")

        tab.add(my.get_episode_wdg, "Episodes") 
        tab.add(my.get_milestone_wdg, "Milestones") 
        
        tab.add(my.get_completion_wdg, "Shots and Assets")
        tab.add(my.get_task_manager_wdg, "Tasks")
        tab.add(LayoutSummaryWdg, "Layout Summary")
        tab.add(AssetSummaryWdg, "Asset Summary")

        my.add(tab, 'tab')



    def get_episode_wdg(my):
        table = TableWdg("prod/episode", "completion")
        table.set_class("table")
        search = Search("prod/episode")
        table.set_search(search)
        return table


    def get_milestone_wdg(my):
        search = Search("sthpw/milestone")

        project = Project.get()
        search.add_filter("project_code", project.get_code() )

        widget = Widget()
        widget.set_search(search)

        table = TableWdg("sthpw/milestone")
        widget.add(table)

        return widget




    def get_shot_wdg(my):
        widget = Widget()

        div = DivWdg(css="filter_box")
        episode_filter = EpisodeFIlterWdg()
        div.add(episode_filter)
        widget.add(div)

        search = Search(FlashShot.SEARCH_TYPE)
        episode_filter.alter_search(search)
        widget.set_search(search)

        table = TableWdg(FlashShot.SEARCH_TYPE, "completion")
        widget.add(table)
        return widget



    def get_timecard_wdg(my):
        hours = Widget()
        search = Search("sthpw/task")
        hours.set_search(search)

        table = TableWdg("sthpw/task", "timecard")
        hours.add(table)
        return hours


    def get_completion_wdg(my):

        widget = Widget()

        div = DivWdg(css="filter_box")
        episode_filter = EpisodeFilterWdg()
        div.add(episode_filter)
        widget.add(div)

        # show shot completion
        widget.add(HtmlElement.h3("Shot Completion"))
        search = Search(FlashShot.SEARCH_TYPE)
        episode_filter.alter_search(search)
        table = TableWdg(FlashShot.SEARCH_TYPE, "completion")
        table.set_search(search)
        widget.add(table)

        # show asset completion
        widget.add(HtmlElement.h3("Asset Completion"))
        search = Search(FlashAsset.SEARCH_TYPE)
        episode_filter.alter_search(search)
        table = TableWdg(FlashAsset.SEARCH_TYPE, "completion")
        table.set_search(search)
        widget.add(table)


        return widget



    def get_task_manager_wdg(my):
        manager = TaskManagerWdg()
        manager.set_search_type("prod/shot")
        manager.set_show_all_task_approvals()
        manager.set_task_view("completion")
        manager.set_sobject_filter( EpisodeFilterWdg() )
        return manager



