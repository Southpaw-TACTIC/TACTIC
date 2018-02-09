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

__all__ = ['LayoutSummaryWdg', 'AssetSummaryWdg', 'AssetsInShotWdg', 'AssignedShotWdg', 'TasksInSObjectWdg', 'DependencySummaryWdg']

from pyasm.common import Environment
from pyasm.search import Search, SObject
from pyasm.web import Widget, DivWdg, Table, SpanWdg, WikiUtil, HtmlElement
from pyasm.biz import Task, Project, Snapshot
from pyasm.prod.biz import Episode, ShotInstance, Asset, Shot, Sequence
from pyasm.widget import *

from asset_filter_wdg import *
from asset_info_wdg import ShotInfoWdg
#from prod_input_wdg import ProcessFilterSelectWdg

class LayoutSummaryWdg(Widget):

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        super(LayoutSummaryWdg,self).__init__()

    def init(self):

        thumb_cache = {}
        div = DivWdg()

        # get all of the shots
        filter_div = DivWdg(css='filter_box')
        unit = 'an Episode'
        filter = shot_container = None
        search_columns = []
        # pick the navigator depending on what project type
        if Project.get().get_type() == 'flash':
            # these navigators will have their empty option removed
            # and should have a different name so that if the user
            # comees from a tab with the same navigator, it won't 
            # use the previous empty value if chosen
            filter = EpisodeFilterWdg('unique_episode_code')
            # set a default value which is used if there is nothing
            # stored in wdg_settings
            filter.set_option('default', SelectWdg.NONE_MODE)
            episode_code = filter.get_value()
            episode = Episode.get_by_code(episode_code)
            shot_container = episode
            search_columns = ['code', 'description', 'episode_code']
        elif Project.get().get_type() == 'prod':
            filter = SequenceFilterWdg('unique_sequence_code')
            filter.set_option('default', SelectWdg.NONE_MODE)
            epi_code, seq_code = filter.get_value()
            seq = Sequence.get_by_code(seq_code)
            shot_container = seq
            unit = 'a Sequence'
            search_columns = ['code', 'description', 'sequence_code'] 
        # name the empty option properly at least
        filter.get_navigator().get_select().add_empty_option(\
            '-- Select %s --' % unit)

        #filter.remove_empty_option()
        #filter.add_none_option()
        filter_div.add(filter)

        search_filter = SearchFilterWdg(columns=search_columns)
        search_filter_value = search_filter.get_value()
        filter_div.add(search_filter)

        div.add(filter_div)
        self.add(div)
        if not shot_container and not search_filter_value:
            return
    
        
        search = Search(Shot.SEARCH_TYPE)
        if shot_container:
            key = shot_container.get_foreign_key()
            code = shot_container.get_code()
            search.add_filter(key,code)
        if search_filter_value:
            search_filter.alter_search(search)
        shots = search.get_sobjects()

        table = TableWdg(Shot.SEARCH_TYPE, 'layout_summary')
        table.set_sobjects(shots)
        self.add(table)
        


class AssetSummaryWdg(Widget):
    '''displays shot information about each asset'''

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        super(AssetSummaryWdg,self).__init__()

    def init(self):

        widget = Widget()
        search = Search("prod/asset")

        div = DivWdg(css="filter_box")
        filter = AssetFilterWdg()
        div.add(filter)

        filter.alter_search(search)
        assets = search.get_sobjects()

        widget.add(div)

        table = TableWdg("prod/asset", "shots_in_asset")
        table.set_sobjects(assets)
        widget.add(table)

        self.add(widget)



class AssetsInShotWdg(BaseTableElementWdg):

    def init(self):
        self.thumb_cache = {}

    def get_display(self):

        shot = self.get_current_sobject()

        # TODO: this is highly inefficient
        self.asset_instances = shot.get_all_children(ShotInstance.SEARCH_TYPE)

        instance_div = DivWdg()

        assets = []

        for instance in self.asset_instances:
            asset = instance.get_reference("prod/asset")
            assets.append(asset)



        instance_div = DivWdg()
        table = TableWdg("prod/asset", "summary_small", css='collapse')
        table.set_no_results_wdg("<i>No instances planned</i>")
        table.set_show_header(False)
        table.set_show_property(False)
        table.set_content_width('auto')
        table.set_sobjects(assets) 

        instance_div.add(table)
        return instance_div



class AssignedShotWdg(BaseTableElementWdg):

    """
    def get_summary(self):
        '''provides classes using this class to query how many results
        there are'''
        return "%s" % len(self.asset_instances)
    """

    def init(self):
        self.is_preprocessed = False

    def preprocess(self):
       
        self.is_preprocessed = True
        # get all of the instances

        search = Search("prod/shot_instance")

        # if not used in a TableWdg, only get the shot instances for one asset
        if not self.parent_wdg:
            search.add_filter('asset_code', self.get_current_sobject().get_code())

        search.add_order_by("shot_code")
        instances = search.get_sobjects()

        self.asset_instances = instances

        self.instances = {}
        for instance in instances:
            asset_code = instance.get_value("asset_code")
            
            list = self.instances.get(asset_code)
            if not list:
                list = []
                self.instances[asset_code] = list

            list.append(instance)
       
        search = Search("prod/shot")
        search.add_filters( "code", [x.get_value('shot_code') for x in instances] )
        shots = search.get_sobjects()
        self.shots = SObject.get_dict(shots, ["code"])
        self.shots_list = shots


            
    def get_display(self):

        if not self.is_preprocessed:
            self.preprocess()

        asset = self.get_current_sobject()

        self.asset_instances = self.instances.get(asset.get_code())
        if not self.asset_instances:
            span = SpanWdg('-- not planned --')
            span.add_style('color: #CCC')
            return span

        # put this into a table widget ...
        # NOTE: this is now assets, not instances ... not sure this is what
        # we want, but we can now drop down the asset/shot details indefinitely.
        div = DivWdg()
        table = TableWdg("prod/shot", "summary_small", css="collapse")
        table.set_show_header(False)
        table.set_content_width('auto')
        table.set_show_property(False)
        table.set_sobjects(self.shots_list)
        div.add(table)
        return div

        """
        instances_per_shot_dict = {}
        shot_codes = []
        for instance in self.asset_instances:
            
            shot_code = instance.get_value("shot_code")
            count = instances_per_shot_dict.get(shot_code)
            if not count:
                count = 0
            count += 1
            
            shot = self.shots.get(shot_code)
            if not shot:
                Environment.add_warning("Missing shot", "Instance has shot '%s' which does not exist or is retired" % shot_code)
                continue

            instances_per_shot_dict[shot_code] = count 
            if shot_code not in shot_codes:
                shot_codes.append(shot_code)
        """


        '''
        table = Table(css='collapse')
        table.add_style("width: 400px")
        for shot_code in shot_codes:
            count = instances_per_shot_dict[shot_code]
            table.add_row()
            shot = self.shots.get(shot_code)

            toggle = HiddenRowToggleWdg()
            toggle.set_option("dynamic", "pyasm.prod.web.AssetDetailWdg")
            table.add_cell(toggle)

            description = shot.get_value("description")

            thumb = ThumbWdg()
            thumb.set_icon_size(60)
            thumb.set_sobject(shot)
            td = table.add_cell()
            td.add(thumb)
            #td.add_style("border-bottom: 1px")
            #td.add_style("border-style: solid")
            td.add_style("width: 80px")
            td.add_style("vertical-align: top")

            td = table.add_cell()
            td.add("<b>%s</b> (x%d)<br/>" % (shot_code, count) )
            td.add( WikiUtil().convert(description) )
            td.add_style("vertical-align: top")
            #td.add_style("border-bottom: 1px")
            #td.add_style("border-style: solid")

            status_wdg = ParallelStatusWdg()
            status_wdg.set_sobject(shot)
            status_wdg.set_option("bar_height", "1")
            status_wdg.set_option("label_format", "small")
            status_wdg.get_prefs()
            status_wdg.preprocess()
            td = table.add_cell(status_wdg)
        '''
                

        return table 
        



class TasksInSObjectWdg(BaseTableElementWdg):

    def preprocess(self):

        # get the tasks and reorder by search_key
        tasks = Task.get_by_sobjects(self.sobjects)
        self.tasks_dict = {}
        for task in tasks:
            search_type = task.get_value("search_type")
            search_id = task.get_value("search_id")
            search_key = "%s|%s" % (search_type, search_id)

            sobject_tasks = self.tasks_dict.get(search_key)
            if not sobject_tasks:
                sobject_tasks = []
                self.tasks_dict[search_key] = sobject_tasks

            sobject_tasks.append(task)



    def get_display(self):
        sobject = self.get_current_sobject()
        task_table = Table(css="minimal")
        task_table.add_style("width: 300px")
        search_key = sobject.get_search_key()
        tasks = self.tasks_dict.get(search_key)
        if tasks:
            for task in tasks:
                task_table.add_row()
                process = task.get_value("process")
                td = task_table.add_cell(HtmlElement.i(process))
                task_table.add_data(':')
                td.add_style("vertical-align: top")
                td.add_style("text-align: right")
                td.add_style("width: 75px")
                td.add_style("padding: 2px")
                task_table.add_cell( task.get_value("description") )

        return task_table




class DependencySummaryWdg(Widget):

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        super(DependencySummaryWdg,self).__init__()

    def init(self):

        search_type = "prod/shot"

        widget = Widget()
        search = Search(search_type)

        div = DivWdg(css="filter_box")
        filter = SequenceFilterWdg()
        div.add(filter)

        #context_filter = ContextFilterWdg(label="Context: ", search_type=)
        #context_filter.set_search_type(search_type)
        #div.add(context_filter)

        context_wdg = TextWdg("context")
        context_wdg.set_persistence()
        span = SpanWdg(css="med")
        span.add("Context: ")
        span.add(context_wdg)
        div.add(span)
        self.context = context_wdg.get_value()

        if not self.context:
            self.context = None

        mode = "latest"

        filter.alter_search(search)
        sobjects = search.get_sobjects()

        widget.add(div)

        table = Table(css="table")
        table.add_style("width: 100%")
        for sobject in sobjects:
            table.add_row()

            thumb = ThumbWdg()
            thumb.set_sobject(sobject)
            table.add_cell(thumb)

            table.add_cell( sobject.get_code() )
            td = table.add_cell( WikiUtil().convert(sobject.get_value("description") ))
            td.add_style("width: 300px")

            if mode == "latest":
                snapshot = Snapshot.get_latest_by_sobject(sobject, self.context)
            else:
                snapshot = Snapshot.get_current_by_sobject(sobject, self.context)

            if not snapshot:
                table.add_cell("<i>No snapshot found</i>")
                continue

            dependency = DependencyWdg()
            dependency.set_show_title(False)
            dependency.set_sobject(snapshot)
            table.add_cell(dependency)

        widget.add(table)
        self.add(widget)




