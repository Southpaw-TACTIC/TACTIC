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
__all__ = ["PlannerLayoutWdg"]

import os, types, re
import cStringIO

from pyasm.common import Xml, XmlException, Common, TacticException, Environment
from pyasm.biz import Schema, ExpressionParser, Project
from pyasm.search import Search, SearchKey, WidgetDbConfig
from pyasm.web import DivWdg, SpanWdg, HtmlElement, Table, Widget, Html, WebContainer
from pyasm.widget import WidgetConfig, WidgetConfigView, IconWdg

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.container import SmartMenu, ResizableTableWdg
from tactic.ui.widget import ActionButtonWdg, SingleButtonWdg

from panel_wdg import ViewPanelWdg

class PlannerLayoutWdg(BaseRefreshWdg):

    ARGS_KEYS = {
    }


    def get_display(my):
        top = my.top

        table = ResizableTableWdg()
        table.add_color("color", "color")
        top.add(table)
        table.add_row()

        left_element_names = ['preview','login','name']
        left_search_type = 'sthpw/login'
        left_view = 'planner_left'

        right_element_names = ['preview','login_group','drop']
        right_search_type = 'sthpw/login_group'
        right_view = 'planner_right'



        left = table.add_cell()
        left.add_border()
        title_div = DivWdg()
        left.add(title_div)
        title_div.add_style("height: 20px")
        title_div.add_style("font-size: 14px")
        title_div.add_style("font-weight: bold")
        title_div.add_style("padding: 8px")
        title_div.add_color("background", "background", -10)
        title_div.add(left_search_type)

        left_div = DivWdg()
        left_div.add_style("width: 500px")
        left_div.add_class("spt_resizable")
        left_div.add_style("overflow-x: auto")
        left_div.add_style("height: 100%")
        left_div.add_style("min-height: 600px")
        left.add(left_div)
        left_layout = ViewPanelWdg(search_type=left_search_type, view=left_view, element_names=left_element_names, show_search_limit="false")
        left_div.add(left_layout)

        middle = table.add_cell(resize=False)
        middle.add( my.get_middle_wdg() )

        right = table.add_cell()
        right.add_border()

        title_div = DivWdg()
        right.add(title_div)
        title_div.add_style("height: 20px")
        title_div.add_style("font-size: 14px")
        title_div.add_style("font-weight: bold")
        title_div.add_style("padding: 8px")
        title_div.add_color("background", "background", -10)
        title_div.add(right_search_type)

        right_div = DivWdg()
        right_div.add_style("width: 500px")
        right_div.add_class("spt_resizable")
        right_div.add_style("overflow-x: auto")
        right.add_style("height: 100%")
        right.add_style("min-height: 600px")
        right.add(right_div)
        right_layout = ViewPanelWdg(search_type=right_search_type, view=right_view, element_names=right_element_names, show_search_limit="false")
        right_div.add(right_layout)


        return top




    def get_middle_wdg(my):
        div = DivWdg()
        #button = ActionButtonWdg(title="<<<")
        #div.add(button)

        div.add("<br/>")
        div.add("<br/>")
        div.add("<br/>")
        div.add("<br/>")

        div.add_color("background", "background")
        div.add_style("width: 35px")
        div.add_style("height: 100%")
        div.add_style("padding: 15px")

        button = SingleButtonWdg(icon=IconWdg.ARROW_RIGHT)
        div.add(button)


        return div





