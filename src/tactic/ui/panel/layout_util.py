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
__all__ = ["LayoutUtil"]

from pyasm.widget import WidgetConfigView


class LayoutUtil(object):
    '''Class to define a bunch of standard views'''


    def get_layout_data(cls, **kwargs):

        search_type = kwargs.get("search_type")
        layout = kwargs.get("layout")
        if not layout:
            layout = "default"


        config = WidgetConfigView.get_by_search_type(search_type, "table")
        default_element_names = config.get_element_names()


        data = {}
        data['table'] = {
            'class_name': 'tactic.ui.panel.FastTableLayoutWdg',
            'view': 'table',
            'label': 'Table',
            'element_names': default_element_names,
        }

        data['tile'] = {
            'class_name': 'tactic.ui.panel.TileLayoutWdg',
            'view': 'tile',
            'label': 'Tile',
            'element_names': [],
        }

        data['list'] = {
            'class_name': 'tactic.ui.panel.FastTableLayoutWdg',
            'view': 'list',
            'label': 'List',
            'element_names': ['name'],
        }


        data['content'] = {
            'class_name': 'tactic.ui.panel.FastTableLayoutWdg',
            'view': 'content',
            'label': 'Content',
            'element_names': ['preview','code','name','description'],
        }


        data['navigate'] = {
            'class_name': 'tactic.ui.panel.FastTableLayoutWdg',
            'view': 'navigate',
            'label': 'Navigator',
            'element_names': ['show_related','detail','code','description'],
        }


        data['schedule'] = {
            'class_name': 'tactic.ui.panel.FastTableLayoutWdg',
            'view': 'schedule',
            'label': 'Navigator',
            'element_names': ['preview','code','name','description','task_pipeline_vertical','task_edit','notes'],
        }



        data['checkin'] = {
            'class_name': 'tactic.ui.panel.FastTableLayoutWdg',
            'view': 'checkin',
            'label': 'Check-in',
            'element_names': ['preview','code','name','general_checkin','file_list', 'history','description','notes'],
        }


        data['tool'] = {
            'class_name': 'tactic.ui.panel.ToolLayoutWdg',
            'view': 'tool',
            'label': 'Tools',
            'element_names': [],
        }

        data['browser'] = {
            'class_name': 'tactic.ui.panel.RepoBrowserLayoutWdg',
            'view': 'browser',
            'label': 'File Browser',
            'element_names': [],
        }

        data['card'] = {
            'class_name': 'tactic.ui.panel.CardLayoutWdg',
            'view': 'card',
            'label': 'Card',
            'element_names': [],
        }


        data['overview'] = {
            'class_name': 'tactic.ui.panel.FastTableLayoutWdg',
            'view': 'overview',
            'label': 'Overview',
            'element_names': ['preview','name','task_pipeline_report','summary','completion'],
        }


        return data.get(layout)


        # OLD DATA

        views = ['table', 'tile', 'list', 'content', 'navigate', 'schedule', 'checkin', 'tool', 'browser', 'card', 'overview']
        labels = ['Table', 'Tile', 'List', 'Content', 'Navigator', 'Task Schedule', 'Check-in', 'Tools', 'File Browser', 'Card', 'Overview']

        # this is fast table biased
        if my.kwargs.get("is_refresh") in ['false', False]:
            class_names = [
                'tactic.ui.panel.ViewPanelWdg',
                'tactic.ui.panel.ViewPanelWdg',
                'tactic.ui.panel.ViewPanelWdg',
                'tactic.ui.panel.ViewPanelWdg',
                'tactic.ui.panel.ViewPanelWdg',
                'tactic.ui.panel.ViewPanelWdg',
                'tactic.ui.panel.ViewPanelWdg',
                'tactic.ui.panel.ViewPanelWdg',
                'tactic.ui.panel.ViewPanelWdg',
                'tactic.ui.panel.ViewPanelWdg',
                'tactic.ui.panel.ViewPanelWdg',
            ]
        else:
            class_names = [
                'tactic.ui.panel.FastTableLayoutWdg',
                'tactic.ui.panel.TileLayoutWdg',
                'tactic.ui.panel.FastTableLayoutWdg',
                'tactic.ui.panel.FastTableLayoutWdg',
                'tactic.ui.panel.FastTableLayoutWdg',
                'tactic.ui.panel.FastTableLayoutWdg',
                'tactic.ui.panel.FastTableLayoutWdg',
                'tactic.ui.panel.tool_layout_wdg.ToolLayoutWdg',
                'tactic.ui.panel.tool_layout_wdg.RepoBrowserLayoutWdg',
                'tactic.ui.panel.tool_layout_wdg.CardLayoutWdg',
                'tactic.ui.panel.FastTableLayoutWdg',
            ]


        layouts = [
            'table',
            'tile',
            'default',
            'default',
            'default',
            'default',
            'default',
            'tool',
            'browser',
            'card',
            'default',
        ]

        element_names = [
            default_element_names,
            [],
            ['name'],
            ['preview','code','name','description'],
            ['show_related','detail','code','description'],
            ['preview','code','name','description','task_pipeline_vertical','task_edit','notes'],
            ['preview','code','name','general_checkin','file_list', 'history','description','notes'],
            [],
            [],
            [],
            ['preview','name','task_pipeline_report','summary','completion'],
	    ]

        if not SearchType.column_exists(my.search_type, 'name'):
            element_names = [
            default_element_names,
            [],
            ['code'],
            ['preview','code','description'],
            ['show_related','detail','code','description'],
            ['preview','code','description','task_pipeline_vertical','task_edit','notes'],
            ['preview','code','general_checkin','file_list', 'history','description','notes'],
            [],
            [],
            [],
            ['preview','code','task_pipeline_report','summary','completion'],
	    ]


    get_layout_data = classmethod(get_layout_data)

