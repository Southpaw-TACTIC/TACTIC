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
from pyasm.search import SearchType, Search
from pyasm.prod.web import *
from pyasm.biz import Project

class OverviewTabWdg(BaseTabWdg):


    def init(self):

        help = HelpItemWdg('Overview', 'The Overview area lets you view the progress of shots, asset, or the specific tasks assigned for them in differernt formats.', False)
        self.add(help)

        self.setup_tab("overview_tab", css=TabWdg.SMALL)

    def handle_tab(self, tab):
        tab.add(self.get_sequence_wdg, _("Sequences") )
        tab.add(self.get_milestone_wdg, _("Milestones") )
        
        tab.add(self.get_completion_wdg, _("Shots and Assets") )
        tab.add(self.get_asset_task_manager_wdg, _("Tasks (Assets)") )
        tab.add(self.get_shot_task_manager_wdg, _("Tasks (Shots)") )
        tab.add(LayoutSummaryWdg, _("Layout Summary") )
        tab.add(AssetSummaryWdg, _("Asset Summary") )
        tab.add(DependencySummaryWdg, _("Dependency Summary") )

        tab.add(self.get_user_schedule_wdg, _("User Schedule") )



    def get_sequence_wdg(self):
        table = TableWdg("prod/sequence", "completion")
        table.set_class("table")
        search = Search("prod/sequence")
        table.set_search(search)
        return table


    def get_milestone_wdg(self):
        search = Search("sthpw/milestone")

        project = Project.get()
        search.add_filter("project_code", project.get_code() )

        widget = Widget()
        widget.set_search(search)

        table = TableWdg("sthpw/milestone")
        widget.add(table)

        return widget




    def get_shot_wdg(self):
        ''' this is not used now'''
        widget = Widget()

        div = DivWdg(css="filter_box")
        sequence_filter = SequenceFilterWdg()
        div.add(sequence_filter)
        widget.add(div)

        search = Search(Shot.SEARCH_TYPE)
        sequence_filter.alter_search(search)
        widget.set_search(search)

        table = TableWdg(Shot.SEARCH_TYPE, "completion")
        widget.add(table)
        return widget





    def get_completion_wdg(self):

        widget = Widget()
        
        sequence_filter = SequenceFilterWdg()
        div = DivWdg(sequence_filter, css="filter_box")
        widget.add(div)

        # show shot completion
        widget.add(HtmlElement.h3("Shot Completion"))
        search = Search(Shot.SEARCH_TYPE)
        sequence_filter.alter_search(search)
        
        table = TableWdg(Shot.SEARCH_TYPE, "completion")
        table.set_search(search)
        widget.add(table)

        # show asset completion
        widget.add(HtmlElement.h3("Asset Completion"))
        search = Search(Asset.SEARCH_TYPE)
        table = TableWdg(Asset.SEARCH_TYPE, "completion")
        table.set_search(search)
        widget.add(table)


        return widget



    def get_shot_task_manager_wdg(self):
        manager = TaskManagerWdg()
        manager.set_search_type("prod/shot")
        manager.set_show_all_task_approvals()
        manager.set_task_view("completion")

        filter = SpanWdg()
        filter.add( SequenceFilterWdg() )
        search_columns = Shot.get_search_columns()
        search_filter = SearchFilterWdg(name="shot_search",columns=search_columns)
        filter.add(search_filter)

        manager.set_sobject_filter( filter )
        return manager

    def get_asset_task_manager_wdg(self):
        manager = TaskManagerWdg()
        manager.set_search_type("prod/asset")
        manager.set_show_all_task_approvals()
        manager.set_task_view("completion")

        filter = SpanWdg()
        filter.add( AssetFilterWdg() )
        search_columns = Asset.get_search_columns()

        manager.set_sobject_filter( filter )
        return manager







    def get_test_report_wdg(self):
        
        widget = Widget()

        search_type_filter = TextWdg("search_type_filter")
        widget.add("Search Type: ")
        widget.add(search_type_filter)

        # look at the config file and generate one
        search_type = "prod/asset"
        search_type_obj = SearchType.get(search_type)
        config = WidgetConfigView.get_by_search_type(search_type_obj, "table")
        element_names = config.get_element_names()
        print "element: ", element_names

        config = '''
        <config>
        <table>
            <element name="code"/>
            <element name="name"/>
            <element name="description"/>
        </table>
        </config>
        '''
        xml = Xml()
        xml.read_string(config)
        config = WidgetConfig(view="table", xml=xml)


        table = TableWdg(search_type)
        search = Search(search_type)
        sobjects = search.get_sobjects()
        table.set_sobjects(sobjects)

        widget.add(table)


        return widget


    def get_user_schedule_wdg(self):
        widget = Widget()
        div = FilterboxWdg()
        widget.add(div)

        start_date_wdg = CalendarInputWdg("start_date_filter", label="From: ", css='med')

        start_date = Date()
        start_date.subtract_days(120) 
        start_date_value = start_date.get_db_date()
        start_date_wdg.set_option('default', start_date_value)
        start_date_wdg.set_persist_on_submit()

        div.add(start_date_wdg)
        end_date_wdg = CalendarInputWdg("end_date_filter", label="To: ", css='med')
        end_date = Date()
        end_date.add_days(120) 
        end_date_value = end_date.get_db_date()
        end_date_wdg.set_option('default', end_date_value)
        end_date_wdg.set_persist_on_submit()
        div.add(end_date_wdg)
        hint = HintWdg('The date range defines which period of the user schedule is displayed')
        div.add(hint)
        search = Search("sthpw/login")
        table = TableWdg("sthpw/login", "schedule")
        table.set_search(search)
        widget.add(table)
        return widget

