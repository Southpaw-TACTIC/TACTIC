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

#__all__= ['AssetTabWdg', 'FlashHistoryWdg']
__all__= ['AssetTabWdg']
from pyasm.common import Environment
from pyasm.search import Search, SObject
from pyasm.biz import StatusEnum, Pipeline
from pyasm.web import *
from pyasm.widget import *
from pyasm.prod.web import SObjectActionWdg, SObjectUploadCmd, WebState, \
        ItemsNavigatorWdg, EpisodeNavigatorWdg, EpisodeFilterWdg, \
        TaskManagerWdg, ApprovalManagerWdg, AssetFilterWdg, RetiredFilterWdg

from pyasm.flash.widget import FlashStatusFilter
from pyasm.flash import *


class AssetTabWdg(BaseTabWdg):

    def init(my):
        
        WebContainer.add_js('PyFlash.js')
        my.add(PyFlashInit())
        my.setup_tab("asset_pipeline_tab", css=TabWdg.SMALL)


    def handle_tab(my, tab):
        tab.add(my.get_asset_list_wdg, "Asset List")
        tab.add(my.get_summary_wdg, "Summary")
        tab.add(my.get_task_entry_wdg, "Tasks")
        tab.add(my.get_artist_wdg, "Artist (Asset)")
        tab.add(my.get_asset_library_wdg, "Asset Libraries")
        tab.add(my.get_asset_type_wdg, "Asset Types")
        tab.add(my.get_notes_wdg, "Notes")



    def get_asset_list_wdg(my):

        widget = Widget()
        nav = DivWdg(css='filter_box')
        asset_filter = AssetFilterWdg()
        episode_filter = EpisodeFilterWdg()
        
        nav.add(episode_filter)
        nav.add(asset_filter)
        widget.add(nav)
        

        search = Search("prod/asset")
        asset_filter.alter_search(search)
        episode_filter.alter_search(search)
        

        table = TableWdg("prod/asset", "manage")
        table.set_search(search)
        widget.add(table)

        return widget




    def get_summary_wdg(my):

        widget = Widget()
        widget.add(HelpItemWdg('Summary tab', '/doc/site/prod/summary_tab.html'))
        nav = DivWdg(css='filter_box')
        widget.add(nav)

        episode_filter = EpisodeNavigatorWdg()
        nav.add( episode_filter )

        asset_filter = AssetFilterWdg()
        nav.add(asset_filter)
        #library_filter = FilterSelectWdg("asset_library")
        #search = Search("prod/asset_library")
        #library_filter.set_search_for_options(search, "code", "title")
        #library_filter.add_empty_option("- Select -")
        #WebState.get().add_state("edit|asset_library", library_filter.get_value())
        #span = SpanWdg(css="med")
        #span.add("Asset Library: ")
        #span.add(library_filter)
        #nav.add(span)

        #asset_library = library_filter.get_value()

        search_limit = SearchLimitWdg()
        search_limit.set_limit(50)
        nav.add(search_limit)


        search = Search("prod/asset")
        

        episode_code = episode_filter.get_value()
        if episode_code != "":
            search.add_filter("episode_code", episode_code)
        #if asset_library:
        #    search.add_filter("asset_library", asset_library)

        table = TableWdg("prod/asset", "summary")
        widget.set_search(search)
        widget.add(table)

        return widget




    def get_artist_wdg(my):

        widget = Widget()
        help = HelpItemWdg('Artist(Asset) Tab', 'You can load, import, or download asset'\
            '(image/general asset type) from this tab. If an asset is not importable, '\
            'the download icon will be shown instead. Media will be downloaded to the '\
            'local repo of your current project.')
        widget.add(help)

        # create a general apoplet
        widget.add(GeneralAppletWdg())

        search_type_wdg = HiddenWdg("search_type", "flash/asset")
        widget.add(search_type_wdg)
        uploaded_wdg = HiddenWdg(SObjectUploadCmd.FILE_NAMES)
        widget.add(uploaded_wdg)

        value = uploaded_wdg.get_value()

        # add the episode navigation filter
        nav = Widget()
        episode_filter = EpisodeFilterWdg()
        nav.add( episode_filter )

        asset_filter = AssetFilterWdg()
        nav.add( asset_filter )

        approval_wdg = ApprovalManagerWdg()
        widget.add(approval_wdg)
        
        approval_wdg.set_search_type("flash/asset")
        approval_wdg.set_search_limit(20)
        approval_wdg.set_sobject_filter( nav )
        return widget






    def _sort_approval(my, sobjects):

        approvals = {}

        for sobject in sobjects:
            status_attr = sobject.get_attr("status")
            context = status_attr.find_process(StatusEnum.IN_PROGRESS)
            context_name = context.get_name()

            if not approvals.has_key(context_name):
                approvals[context_name] = []

            approvals[context_name].append(sobject)


        what = approvals.items()
        what.sort()
        what.reverse()

        new_sobjects = []
        for context_name, cow in what:

            for sobject in cow:
                new_sobjects.append(sobject)

        return new_sobjects





    def get_task_entry_wdg(my):
        widget = Widget()
        widget.add(HelpItemWdg('Tasks tab', '/doc/site/prod/task_tab.html'))
        manager = TaskManagerWdg()
        widget.add(manager)
        manager.set_search_type("flash/asset")
        manager.set_sobject_filter( AssetFilterWdg() )
        return widget




    def get_asset_library_wdg(my):
        widget = Widget()
        search = Search("prod/asset_library")
        widget.set_search(search)
        table = TableWdg("prod/asset_library")
        widget.add(table)
        return widget

    def get_asset_type_wdg(my):
        widget = Widget()
        search = Search("prod/asset_type")
        widget.set_search(search)
        table = TableWdg("prod/asset_type")
        widget.add(table)
        return widget
 

    def get_pipeline_wdg(my):
        widget = Widget()
        search = Search("sthpw/pipeline")
        widget.set_search(search)
        table = TableWdg("sthpw/pipeline")
        widget.add(table)
        return widget

   

    def get_notes_wdg(my):
        widget = Widget()

        div = DivWdg(css='filter_box')
        asset_filter = AssetFilterWdg()
        div.add(asset_filter)
 
        search_limit = SearchLimitWdg()
        div.add(search_limit)

        context_select = FilterSelectWdg("discussion_context")
        context_select.set_option("setting", "notes_prod_context")
        context_select.add_empty_option("<- Any Context ->")
        span = SpanWdg(css="med")
        span.add("Notes Context: ")
        span.add(context_select)
        div.add(span)

        widget.add(div)


        # create a search
        search = Search("prod/asset")
        asset_filter.alter_search(search)
        sobjects = search.get_sobjects()

        table = TableWdg("prod/asset", "prod_notes")
        table.set_class("table")
        table.set_sobjects(sobjects)
        widget.add(table)
        return widget


   




"""
class FlashHistoryWdg(HistoryWdg):

    def set_select_options(my, select):
        
        select.set_option("labels", "---|Assets|Scenes|Instances|Layers")
        select.set_option("values", "|flash/asset|flash/shot|prod/shot_instance|prod/layer")
"""


        



