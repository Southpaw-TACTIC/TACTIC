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

__all__ = ["AssetTabWdg"]

from pyasm.biz import Project
from pyasm.web import *
from pyasm.widget import *
from pyasm.prod.web import *
from pyasm.widget import FilterSelectWdg

from texture_tab_wdg import TextureTabWdg


class AssetTabWdg(BaseTabWdg):

    def init(my):
        my.add(HelpItemWdg('Asset Pipeline', 'Asset Pipeline contains a collection of tabs that define different aspects of the asset pipeline.', False))
        my.setup_tab("asset_pipeline_tab", css=TabWdg.SMALL)



    def handle_tab(my, tab):
        
        tab.add(my.get_asset_list_wdg, _("Asset List") )
        tab.add(my.get_summary_wdg, _("Summary") )
        tab.add(my.get_task_manager_wdg, _("Tasks") )
        tab.add(my.get_asset_artist_wdg, _("Artist (3D Assets)") )
        tab.add(my.get_asset_supe_wdg, _("Supe (3D Assets)") )
        tab.add(TextureTabWdg, _("2D Assets") )
        tab.add(my.get_render_log_wdg, _("Render Log") )
        tab.add(my.get_library_type_wdg, _("Asset Libraries") )
        tab.add(my.get_notes_wdg, _("Notes") )


    def get_asset_list_wdg(my):

        widget = Widget()
        widget.add(HelpItemWdg('Asset List Tab', '/doc/production/asset_list.html', is_link=True))

        nav = DivWdg(css='filter_box')
        widget.add(nav)
        asset_filter = AssetFilterWdg()
        nav.add(asset_filter)

        
        #nav.add(search_limit)


        search = Search("prod/asset")
        # search_limit.alter_search(search)

        asset_filter.alter_search(search)
        table = TableWdg("prod/asset", "manage")
        table.set_search(search)
        widget.add(table)

        return widget



    def get_summary_wdg(my):

        widget = Widget()
        #widget.add(HelpItemWdg('Summary tab', '/doc/site/prod/summary_tab.html'))
        widget.add(HelpItemWdg('Summary tab', '/doc/production/summary.html', is_link=True))
        
        nav = DivWdg(css='filter_box')
        asset_filter = AssetFilterWdg()
        nav.add(asset_filter)

        widget.add(nav)
        
        search = Search("prod/asset")
        asset_filter.alter_search(search)
        

        table = TableWdg("prod/asset", "summary")
        table.set_search(search)
        table.set_search_limit(15)

        widget.add(table)

        return widget


    def get_task_manager_wdg(my):
       
        widget = Widget()
        help = HelpItemWdg('Tasks tab', 'The Task Manager lets the coordinator set up tasks for each individual asset. Once created, the tasks can be assigned to different users. Settings such as bid date, duration, and milestone can be customized at any time.')
        widget.add(help)
        manager = TaskManagerWdg()
        widget.add(manager)
        manager.set_search_type("prod/asset")
        manager.set_sobject_filter( AssetFilterWdg() )
        return widget



    def get_asset_artist_wdg(my):
        widget = Widget()
        approval_wdg = ApprovalManagerWdg()
        widget.add(approval_wdg)
        approval_wdg.set_search_type("prod/asset")
        approval_wdg.set_sobject_filter( AssetFilterWdg() )
        
        help = HelpItemWdg('Artist tab', 'The Artist tab lets the artist to set the status of his assigned tasks, leave notes, publish, and view all sorts of info related to various assets')
        widget.add(help)
        return widget

    def get_asset_supe_wdg(my):
        widget = Widget()
        approval_wdg = ApprovalManagerWdg()
        widget.add(approval_wdg)
        approval_wdg.set_search_type("prod/asset")
        approval_wdg.set_sobject_filter( AssetFilterWdg() )
        approval_wdg.set_view('supe')
    
        help = HelpItemWdg('Supe tab', 'In addition to what the Artist tab does, The Supe tab lets the supervisor assign existing tasks to differernt users, and modify the estimated date range for each task.')
        widget.add(help)
        return widget


    def get_texture_wdg(my):

        search = Search(Texture.SEARCH_TYPE)

        widget = Widget()
        widget.set_search(search)

        span = SpanWdg()
        span.add_style("float: right")
        upload = SObjectActionWdg()
        span.add(upload)
        widget.add(span)

        filter = TextureFilterWdg()
        widget.add(filter)

        table = TableWdg(Texture.SEARCH_TYPE, "summary")

        widget.add(table)
        return widget




    def get_source_wdg(my):

        search = Search(TextureSource.SEARCH_TYPE)

        widget = Widget()
        widget.set_search(search)

        span = SpanWdg()
        span.add_style("float: right")
        upload = SObjectActionWdg()
        span.add(upload)
        widget.add(span)

        filter = TextureFilterWdg()
        widget.add(filter)

        table = TableWdg(TextureSource.SEARCH_TYPE)

        widget.add(table)
        return widget





    def get_render_log_wdg(my):

        widget = Widget()

        div = DivWdg()
        div.add_class("filter_box")

        select = SelectWdg("time_filter")
        select.set_persistence()
        select.set_option("labels","1 Hour Ago|1 Day|1 Week Ago|1 Month Ago|All")
        select.set_option("values","1 Hour|1 Day|1 Week|1 Month|")
        select.add_event("onChange", "document.form.submit()")
        div.add("<b>Show Renders From: </b>")
        div.add(select)
        time_filter = select.get_value()

        widget.add(div)


        search = Search(Render.SEARCH_TYPE)
        if time_filter != "":
            search.add_where("now()-timestamp <= '%s'::interval" % time_filter)
        search.add_order_by("timestamp desc")
        widget.set_search(search)
        table = TableWdg(Render.SEARCH_TYPE)
        widget.add(table)

        return widget




    def get_library_type_wdg(my):

        widget = Widget()
        search = Search("prod/asset_library")
        widget.set_search(search)
        table = TableWdg("prod/asset_library")
        widget.add(table)
        return widget


 

    def get_notes_wdg(my):
        widget = Widget()

        help = HelpItemWdg('Notes tab', 'The Notes tab focuses on the display of notes. It includes both asset notes and submission notes for each asset.')
        widget.add(help)

        div = DivWdg(css='filter_box')
        asset_filter = AssetFilterWdg()
        div.add(asset_filter)
 
        config_base = 'asset_prod_notes' 

        context_select = ProcessFilterSelectWdg(name="%s_discussion_context" %config_base,\
                has_empty=False, search_type='prod/asset' )

        context_select.add_empty_option("-- Any Context --")
        context_select._add_options()
        setting = "notes_asset_prod_context"
        values_option = ProdSetting.get_seq_by_key(setting) 
        if not values_option:
            data_dict = {'key': setting}
            prod_setting = ProdSetting.get_by_key(setting)
            ps_id = -1
            if prod_setting:
                ps_id = prod_setting.get_id()
            context_select._set_append_widget(ps_id, data_dict)
        labels, values = context_select.get_select_values()
       
        if values_option:
            context_select.append_option('','')
            context_select.append_option('&lt;&lt; %s &gt;&gt;' %setting, ','.join(values_option))
        for value in values_option:
            if value not in values:
                context_select.append_option(value, value)

        context_select.set_dom_options()
        span = SpanWdg(css="med")
        span.add("Notes Context: ")
        span.add(context_select)
        hint = HintWdg('Submission notes for each asset are also included here')
        span.add(hint)
        div.add(span)

        div.add(IconRefreshWdg(long=False))
        #search_limit = SearchLimitWdg()
        #div.add(search_limit)

        widget.add(div)


        # create a search
        search = Search("prod/asset")
        asset_filter.alter_search(search)
        #search_limit.alter_search(search)
        #sobjects = search.get_sobjects()

        table = TableWdg("prod/asset", config_base)
        table.set_search(search)
        widget.add(table)
        return widget


 



