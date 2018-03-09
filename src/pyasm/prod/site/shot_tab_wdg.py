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

__all__ = ["ShotTabWdg"]

from pyasm.web import *
from pyasm.search import *
from pyasm.widget import *
from pyasm.prod.web import *
from pyasm.prod.biz import Shot, ProdSetting
from pyasm.biz import Project

from maya_tab_wdg import *


class ShotTabWdg(BaseTabWdg):

    def init(self):
        help = HelpItemWdg('Shot Pipeline', 'Shot Pipeline contains a collection of tabs that define different aspects of the shot pipeline. Shots are inserted here and the status of each shot can be tracked.', False)
        self.add(help)

        self.setup_tab("shot_pipeline_tab", css=TabWdg.SMALL)

    def handle_tab(self, tab):
        tab.add(self.get_shot_list_wdg, _("Shot List") )
        tab.add(self.get_summary_wdg, _("Summary") )
        tab.add(self.get_milestone_wdg, _("Milestones") )
        tab.add(MultiPlannerWdg, _("Planners") )
        tab.add(self.get_task_manager_wdg, _("Tasks") )
        #tab.add(ShotParentWdg, "Shot Parenting") )
        tab.add(self.get_artist_wdg, _("Artist (Shots)") )
        tab.add(self.get_supe_wdg, _("Supe (Shots)") )
        tab.add(self.get_layer_wdg, _("Layers") )
        tab.add(self.get_comp_wdg, _("Composites") )
        tab.add(self.get_render_log_wdg, _("Render Log") )
        tab.add(self.get_seq_wdg, _("Sequences") )
        if ProdSetting.get_value_by_key('shot_hierarchy') == 'episode_sequence':
            tab.add(self.get_episode_wdg, _("Episodes") )
        tab.add(self.get_notes_wdg, _("Notes") )


    def get_shot_list_wdg(self):

        widget = Widget()
        help = HelpItemWdg('Shot List', 'The Shot List tab allows you to insert new shots, define frame range, amd set differernt statuses for your shot. It also provides a button for media submission.')
        widget.add(help)
        nav = DivWdg(css='filter_box')

        search_columns = Shot.get_search_columns()
        search_filter = SearchFilterWdg(name="shot_search", columns=search_columns)
        nav.add(search_filter)

        seq_filter = SequenceFilterWdg()
        nav.add(seq_filter)

        status_select = FilterSelectWdg("status_select", label='Status: ')
        status_select.add_empty_option("-- Any Status --")
        status_select.set_option("setting", "shot_status")
        status_value = status_select.get_value()
        nav.add(status_select)

        pipeline_filter = PipelineFilterWdg()
        pipeline_filter.set_search_type('prod/shot')
        nav.add(pipeline_filter)

        scan_status_select = FilterSelectWdg("scan_status_select", label='Scan Status: ')
        scan_status_select.add_empty_option("-- Any Scan Status --")
        scan_status_select.set_option("setting", "shot_scan_status")
        scan_status_value = scan_status_select.get_value()
        nav.add(scan_status_select)

        widget.add(nav)
       
        order = Sequence.get_order()

        search = Search("prod/shot")
        search.add_enum_order_by('sequence_code', order)
        search.add_order_by('code')

        seq_filter.alter_search(search)
        pipeline_filter.alter_search(search)
        if status_value:
            search.add_filter("status", status_value)
        
        if scan_status_value:
            search.add_filter("scan_status",  scan_status_value)

        widget.set_search(search)
        table = TableWdg("prod/shot", "manage")
        widget.add(table)

        return widget



    def get_summary_wdg(self):
        widget = Widget()

        nav = DivWdg(css="filter_box")
        search_columns = Shot.get_search_columns()


        search_filter = SearchFilterWdg(name="shot_search", columns=search_columns)
        nav.add(search_filter)

        status_select = FilterSelectWdg("status_select", label='Status:', css='med')
        status_select.add_empty_option("-- Any Status --")
        status_select.set_option("setting", "shot_status")
        status_value = status_select.get_value()
        nav.add(status_select)

        filter = SequenceFilterWdg()
        nav.add(filter)

        widget.add(nav)

        search = Search("prod/shot")
        search_filter.alter_search(search)
        filter.alter_search(search)
        if status_value:
            search.add_filter("status", status_value)
        
        table = TableWdg("prod/shot", "summary")
        table.set_search_limit(10)
        table.set_search(search)
        widget.add(table)

        return widget



    def get_task_manager_wdg(self):
        manager = TaskManagerWdg()
        manager.set_search_type("prod/shot")
        manager.set_process_filter_name("shot_process_filter")
        filter = SpanWdg()
        filter.add( SequenceFilterWdg() )
        search_columns = Shot.get_search_columns()
        search_filter = SearchFilterWdg(name="shot_search",columns=search_columns)
        filter.add(search_filter)
        '''
        search_hint = HintWdg('You can enter any of %s of a shot.' % search_columns)  	 	 
        filter.add(search_hint) 
        '''
        manager.set_sobject_filter( filter )
        return manager




    def get_artist_wdg(self):
        widget = Widget()
        help = HelpItemWdg('Artist tab', 'The Artist tab lets the artist to set the status of his assigned tasks, leave notes, publish, and view all sorts of info related to various shots.')
        widget.add(help)

        # add some filters
        filter = Widget()

        seq_filter = SequenceFilterWdg()
        text_field = ShotFilterWdg()

        filter.add(seq_filter)
        filter.add(text_field)
        approval_wdg = ApprovalManagerWdg()
        approval_wdg.set_search_limit(10)
        approval_wdg.set_search_type("prod/shot")
        approval_wdg.set_sobject_filter(filter)
        approval_wdg.set_pipeline_name("shot")
        approval_wdg.set_process_filter_name('shot_process_filter')
        widget.add(approval_wdg)
        
        return widget

    def get_supe_wdg(self):
        widget = Widget()
        help = HelpItemWdg('Supe tab', 'In addition to what the Artist tab does, The Supe tab lets the supervisor assign existing tasks to differernt users, and modify the estimated date range for each task.')
        widget.add(help)
        
        # add some filters
        filter = Widget()
        navigator = SequenceShotFilterWdg('sequence_code_nav')

        filter.add(navigator)
        filter.add(HtmlElement.br(2))
        text_field = ShotFilterWdg()
        filter.add(text_field)
        approval_wdg = ApprovalManagerWdg()
        approval_wdg.set_view('supe')
        approval_wdg.set_search_limit(10)
        approval_wdg.set_search_type("prod/shot")
        approval_wdg.set_sobject_filter(filter)
        approval_wdg.set_process_filter_name('shot_process_filter')
        # this does not have any effect right now
        approval_wdg.set_pipeline_name("shot")
    
        widget.add(approval_wdg)
        
        return widget



    def get_layer_wdg(self):

        widget = Widget()

        # add some filters
        div = DivWdg(css="filter_box")
        shot_navigator = ShotNavigatorWdg()
        shot = shot_navigator.get_shot()
        div.add(shot_navigator)
        widget.add(div)

        if not shot:
            return widget

       

        widget.add("<h3>Layers</h3>")

        table = TableWdg(Layer.SEARCH_TYPE)
        search2 = Search(Layer.SEARCH_TYPE)
        search2.add_filter(shot.get_foreign_key(), shot.get_code())
        search2.add_order_by('sort_order')
        search2.add_order_by('name')
        table.set_sobjects(search2.get_sobjects())
        widget.add(table)

        # display the shot
        table = TableWdg(Shot.SEARCH_TYPE, "animation")
        table.set_sobject(shot)
        widget.add(table)

        return widget



    def get_comp_wdg(self):

        widget = Widget()

        # add some filters
        div = DivWdg(css="filter_box")
        shot_navigator = ShotNavigatorWdg()
        shot = shot_navigator.get_shot()
        div.add(shot_navigator)
        widget.add(div)

        if not shot:
            return widget

        # display the shot
        table = TableWdg(Shot.SEARCH_TYPE, "composite")
        table.set_sobject(shot)
        widget.add(table)

        widget.add("<h3>Composites</h3>")

        if not Container.get('GeneralAppletWdg'):
            widget.add( GeneralAppletWdg() )
            Container.put('GeneralAppletWdg', True)

        search = Search(Composite.SEARCH_TYPE)
        search.add_filter("shot_code", shot.get_code() )

        table = TableWdg(Composite.SEARCH_TYPE)
        table.set_search(search)
        widget.add(table)
        return widget




    def get_render_log_wdg(self):

        widget = Widget()

        div = DivWdg(css='filter_box')
        div.add_style("text-align: center")

        select = DateFilterWdg(['time_filter', 'Show Render Container From: '])
        select.set_option("labels","1 Hour Ago|1 Day|1 Week Ago|1 Month Ago|All")
        select.set_option("values","1 Hour|1 Day|1 Week|1 Month|")
        div.add(select)
        time_filter = select.get_value()

        widget.add(div)


        search = Search(Render.SEARCH_TYPE)
        
        select.alter_search(search)

        search.add_order_by("timestamp desc")
        widget.set_search(search)
        table = TableWdg(Render.SEARCH_TYPE)
        widget.add(table)

        return widget



    def get_seq_wdg(self):
        
        
        widget = Widget()
        help = HelpItemWdg('Sequences tab', 'The Sequences tab lets you create sequences which can be used to relate to shots. Each shot has a sequence code attribute which you can assign to.')
        widget.add(help)
        div = DivWdg(css='filter_box')
        search_columns = Sequence.get_search_columns()
        search_filter = SearchFilterWdg(name="sequence_search", columns=search_columns) 
        div.add(SpanWdg(search_filter, css='med'))
        search = Search("prod/sequence")
        search_filter.alter_search(search)

        
        widget.add(div)
        view = 'table'
        if ProdSetting.get_value_by_key('shot_hierarchy') == 'episode_sequence':
            view ='table_episode'
        table = TableWdg("prod/sequence", view)
        table.set_search(search)
        widget.add(table)

        return widget

    def get_episode_wdg(self):
        
        widget = Widget()
        help = HelpItemWdg('Episodes tab', 'The Episodes tab lets you create episodes which can be used to relate to sequences. Each sequence has a episode code attribute which you can assign to.')
        widget.add(help)
        div = DivWdg(css='filter_box')
        search_columns = Episode.get_search_columns()
        search_filter = SearchFilterWdg(name="episode_search", columns=search_columns) 
        div.add(search_filter)
        search = Search("prod/episode")
        search_filter.alter_search(search)
        widget.add(div)
        table = TableWdg("prod/episode")
        table.set_search(search)
        widget.add(table)

        return widget




    def get_milestone_wdg(self):
        search = Search("sthpw/milestone")
        project = Project.get()
        search.add_project_filter( project.get_code() )

        widget = Widget()
        widget.set_search(search)

        table = TableWdg("sthpw/milestone")
        widget.add(table)

        return widget




    def get_notes_wdg(self):
        widget = Widget()
        help = HelpItemWdg('Notes tab', 'The Notes tab focuses on the display of notes. It includes both shot notes and submission notes for each shot.')
        widget.add(help)
        div = DivWdg(css="filter_box")
        text = TextWdg("shot_search")
        text.set_persist_on_submit()
        div.add("Shot Search: ")
        div.add(text)

        sequence_filter = SequenceFilterWdg()
        
        div.add(sequence_filter)

        # add Note Context dropdown
        # scope with config base, also used in DiscussionWdg and SObjectTaskTableElement
        config_base = 'prod_notes' 
        context_select = ProcessFilterSelectWdg(name="%s_discussion_context" %config_base,\
                has_empty=False, search_type='prod/shot', label='Note Context: ' )

        context_select.add_empty_option("-- Any Context --")
        context_select._add_options()
        setting = "notes_prod_context"
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

        div.add(context_select)
        hint = HintWdg('Submission notes for each shot are also included here')
        div.add(hint)

        div.add(IconRefreshWdg(long=False))
        search_limit = SearchLimitWdg()
        div.add(search_limit)

        widget.add(div)


        # create a search
        search = Search("prod/shot")
        text_value = text.get_value()
        sequence_filter.alter_search(search)  

        if text_value:
            filter = Search.get_compound_filter(text_value, ['code', 'description'])
            search.add_where(filter)
        search_limit.alter_search(search)
        sobjects = search.get_sobjects()


        table = TableWdg("prod/shot", config_base)
        table.set_class("table")
        table.set_sobjects(sobjects)
        widget.add(table)
        return widget



