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

__all__ = ['ShotTabWdg']

from pyasm.web import *
from pyasm.widget import *
from pyasm.prod.web import *
from pyasm.flash import *
from pyasm.flash.widget import *




class ShotTabWdg(Widget):


    def init(my):
        WebContainer.add_js('PyFlash.js')
        my.add(PyFlashInit())

        tab = TabWdg(css=TabWdg.SMALL)
        tab.set_tab_key("shot_pipeline_tab")
        my.handle_tab(tab)
        my.add(tab, 'tab')


    def handle_tab(my, tab):
        tab.add(my.get_shot_list_wdg, "Scene List")
        tab.add(my.get_summary_wdg, "Summary")
        tab.add(my.get_task_entry_wdg, "Task")
        tab.add(FlashEpisodePlannerWdg, "Episode Planner")
        tab.add(FlashShotInstanceAdderWdg, "Scene Planner")
        tab.add(my.get_builder_wdg, "Builder")

        # for advanced productions
        #tab.add(FlashLayerInstanceAdderWdg, "Layer Planner")
        #tab.add(my.get_flash_anim_wdg, "Animation")

        tab.add(my.get_shot_wdg, "Scene")
        tab.add(my.get_shot_audio_wdg, "Scene Audio")
        tab.add(my.get_layer_wdg, "Layers")

        tab.add(my.get_render_wdg, "Render")
        tab.add(my.get_comp_wdg, "Composites")
        tab.add(my.get_episode_wdg, "Episodes")

        tab.add(my.get_notes_wdg, "Notes")


    def get_shot_list_wdg(my):

        widget = Widget()
        nav = DivWdg(css='filter_box')

        search_columns = ['code', 'description', 'episode_code']
        search_filter = SearchFilterWdg(columns=search_columns)
        nav.add(search_filter)

        asset_filter = EpisodeFilterWdg()
        nav.add(asset_filter)


        retired_filter = RetiredFilterWdg()
        nav.add(retired_filter)
        widget.add(nav)
        
        search = Search("flash/shot")
        if retired_filter.get_value() == 'on':
            search.set_show_retired_flag(True)
        widget.set_search(search)
        table = TableWdg("flash/shot", "manage")
        widget.add(table)

        return widget






    def get_summary_wdg(my):

        widget = Widget()
        widget.add(HelpItemWdg('Summary tab', '/doc/site/prod/summary_tab.html'))
        div = DivWdg()
        div.add_class("filter_box")
        nav = EpisodeNavigatorWdg()
        div.add(nav)
        widget.add(div)

        search_limit = SearchLimitWdg()
        search_limit.set_limit(50)
        nav.add(search_limit)

        episode_code = nav.get_value()

        search = Search("flash/shot")
        if episode_code != "":
            search.add_filter("episode_code", episode_code)
        widget.set_search(search)

        table = TableWdg("flash/shot", "summary")
        widget.add(table)

        return widget



    def get_task_entry_wdg(my):
        widget = Widget()
        widget.add(HelpItemWdg('Tasks tab', '/doc/site/prod/task_tab.html'))
        manager = TaskManagerWdg()
        widget.add(manager)
        manager.set_search_type("flash/shot")
        manager.set_sobject_filter( EpisodeFilterWdg() )
        return widget



    def get_shot_wdg(my):
        widget = Widget()
        search = Search(FlashShot.SEARCH_TYPE)

        #WebContainer.register_cmd("pyasm.flash.FlashAssetPublishCmd")
        widget.add(GeneralAppletWdg())
        search_type_wdg = HiddenWdg("search_type", "flash/shot")
        widget.add(search_type_wdg)
        uploaded_wdg = HiddenWdg(SObjectUploadCmd.FILE_NAMES)
        widget.add(uploaded_wdg)


        # add the episode navigation filter
        nav = Widget()

        search_columns = ['code', 'description', 'episode_code']
        search_filter = SearchFilterWdg(columns=search_columns)
        nav.add(search_filter)

        episode_filter = EpisodeFilterWdg()
        nav.add( episode_filter )

        approval_wdg = ApprovalManagerWdg()
        widget.add(approval_wdg)
        approval_wdg.set_search_type("flash/shot")
        approval_wdg.set_search_limit(20)
        approval_wdg.set_sobject_filter( nav )
        approval_wdg.set_view("shot_publish")

        return widget

    def get_shot_audio_wdg(my):
        widget = Widget()
        widget.add(HelpItemWdg('Scene Audio', 'The Scene Audio tab allows you to organize audio file for each shot. Only 1 entry is required to be [Inserted] for each shot. This audio can also be used for scene construction in Build.'))
        div = DivWdg(css="filter_box")
        episode_filter = EpisodeShotNavigatorWdg()
        div.add(episode_filter)
        widget.add(div)

        search_type = 'prod/shot_audio'
        table = TableWdg(search_type)
        widget.add(table)
        search = Search(search_type)

        shot_code = episode_filter.get_value()
        if shot_code:
            search.add_filter("shot_code", episode_filter.get_value())
        table.set_search(search)
        return widget

    def get_render_wdg(my):

        widget = Widget()
        search = Search(FlashLayer.SEARCH_TYPE)
        widget.set_search(search)

        # add some filters
        div = DivWdg(css="filter_box")
        navigator = EpisodeShotFilterWdg()
        navigator.remove_empty_option()
        navigator.add_none_option()

        div.add(navigator)
        widget.add(div)

        shot_code = navigator.get_value()
        navigator.alter_search(search)

        table = TableWdg(FlashLayer.SEARCH_TYPE, "render-tab")
        widget.add(table)
        return widget



    def get_flash_anim_wdg(my):

        widget = Widget()
        
        # create a general apoplet
        widget.add(GeneralAppletWdg())
        
        # add some filters
        filter = Widget()
        navigator = EpisodeShotFilterWdg()
        shot_code = navigator.get_value()

        filter.add(navigator)
        #filter.add(SearchLimitWdg(limit=20))

        search_type_wdg = HiddenWdg("search_type", FlashLayer.SEARCH_TYPE)
        widget.add(search_type_wdg)
        uploaded_wdg = HiddenWdg(SObjectUploadCmd.FILE_NAMES)
        widget.add(uploaded_wdg)

        value = uploaded_wdg.get_value()
        WebContainer.register_cmd("pyasm.flash.FlashLayerPublishCmd")
       
        # display the shot's approval manager
        '''
        table = TableWdg(Shot.SEARCH_TYPE)
        search = Search(Shot.SEARCH_TYPE)
        search.add_filter("code", shot_code)
        table.set_search(search)
        widget.add(table)
        '''
        approval_wdg = ApprovalManagerWdg()
        
        approval_wdg.set_sobject_filter(filter)
        approval_wdg.set_search_type("flash/shot")
        # Setting the pipeline name enables better sorting
        #approval_wdg.set_pipeline_name("shot")
        widget.add(approval_wdg)
        # display layers
        widget.add("<h3>Layers</h3>")

        table = TableWdg(Layer.SEARCH_TYPE)
        search = Search(Layer.SEARCH_TYPE)
        search.add_filter("shot_code", shot_code)
        table.set_search(search)
        widget.add(table)


        # add list of instances in this shot
        widget.add(HtmlElement.h3("Instances in Shot"))

        search = Search(ShotInstance.SEARCH_TYPE)
        search.add_filter("shot_code", shot_code)
        table = TableWdg(ShotInstance.SEARCH_TYPE)
        table.set_search(search)
        widget.add(table)

        return widget



    def get_layer_wdg(my):

        widget = Widget()
        
        # add some filters
        filter = DivWdg(css="filter_box")
        navigator = EpisodeShotFilterWdg()
        navigator.remove_empty_option()
        navigator.add_none_option()

        shot_code = navigator.get_value()
        filter.add(navigator)
        widget.add(filter)

        table = TableWdg(Shot.SEARCH_TYPE)
        search = Search(Shot.SEARCH_TYPE)
        search.add_filter("code", shot_code)
        table.set_search(search)
        widget.add(table)

        # display layers
        widget.add(HtmlElement.h3("Layers"))

        table = TableWdg(FlashLayer.SEARCH_TYPE, "render-tab")
        search = Search(Layer.SEARCH_TYPE)
        search.add_filter("shot_code", shot_code)
        table.set_search(search)
        widget.add(table)


        # add list of instances in this shot
        widget.add(HtmlElement.h3("Instances in Shot"))

        search = Search(ShotInstance.SEARCH_TYPE)
        search.add_filter("shot_code", shot_code)
        table = TableWdg(ShotInstance.SEARCH_TYPE)
        table.set_search(search)
        widget.add(table)

        return widget


    def get_comp_wdg(my):


        widget = Widget()

        search = Search(Composite.SEARCH_TYPE)
        widget.set_search(search)

        # add some filters
        div = DivWdg(css="filter_box")
        navigator = EpisodeShotNavigatorWdg()
        div.add(navigator)
        widget.add(div)

        table = TableWdg(Composite.SEARCH_TYPE)
        widget.add(table)
        return widget




    def get_shot_info_wdg(my):


        widget = Widget()
        search = Search("flash/shot")
        widget.set_search(search)


        nav = DivWdg(css="filter_box")
        episode_filter = EpisodeNavigatorWdg()
        episode_code = episode_filter.get_value()
        search.add_filter("episode_code", episode_code)
        nav.add( episode_filter )
        widget.add(nav)

        # add the upload/download widgets
        #action_wdg = sobjectactionwdg(search_type="flash/shot")
       
        action_wdg = SObjectActionWdg()
        action_wdg.set_upload_option("column", "snapshot")
        action_wdg.set_style("float: right; margin: 5px 0 5px 0")
        widget.add( action_wdg )

        widget.add(HtmlElement.br())
        table = TableWdg("flash/shot")
        table.set_class("table")
        widget.add(table)

        return widget



    def get_episode_wdg(my):


        widget = Widget()

        search = Search(Episode)
        widget.set_search(search)

        table = TableWdg(Episode)
        widget.add(table)
        return widget



    def get_notes_wdg(my):
        widget = Widget()

        div = DivWdg(css="filter_box")
        text = TextWdg("shot_search")
        text.set_persist_on_submit()
        div.add("Shot Search: ")
        div.add(text)

        episode_filter = EpisodeNavigatorWdg()
        episode_code = episode_filter.get_value()
        div.add(episode_filter)

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
        search = Search("prod/shot")
        text_value = text.get_value()
        if episode_code:
            search.add_filter("episode_code", episode_code)

        if text_value:
            filter = Search.get_filter(text_value, ['code', 'description'])
            search.add_where(filter)
        sobjects = search.get_sobjects()


        table = TableWdg("flash/shot", "prod_notes")
        table.set_class("table")
        table.set_sobjects(sobjects)
        widget.add(table)
        return widget



    def get_builder_wdg(my):
        widget = Widget()
        widget.add(GeneralAppletWdg())
        widget.add(FlashBuilderWdg())
        return widget



