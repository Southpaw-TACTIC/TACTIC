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


__all__ = ["SampleChartWdg"]

from pyasm.common import Environment, Common
from pyasm.biz import Project
from pyasm.web import Widget, DivWdg, HtmlElement, WebContainer, Table
from pyasm.widget import SelectWdg, TextWdg
from pyasm.search import Search, SearchType
from tactic.ui.common import BaseRefreshWdg

import types, os

from chart_wdg import ChartWdg
from chart_data import ChartData, ChartElement


# DEPRECATED


class SampleChartWdg(BaseRefreshWdg):

    def get_display(my):

        top = DivWdg()
        top.add_class("spt_sample_chart_top")

        table = Table()
        table.add_row()
        left = table.add_cell()

        # add the chart
        chart_div = DivWdg()
        chart_div.add_class("spt_sample_chart")
        left.add(chart_div)
        chart_div.add_style("width: 600")
        chart_div.add_style("height: 400")
        chart_div.add_style("padding: 10px")

        data_file = 'bar-2.txt'
        chart = ChartWdg(data_file=data_file)
        chart_div.add(chart)


        # add navigator
        right = table.add_cell()
        right.add_style("text-align: top")

        top.add(table)

        base_dir = "%s/src" % Environment.get_install_dir()
        rel_dir = 'context/spt_js/ofc/data-files'

        files_div = DivWdg()
        files_div.add_style("height: 400")
        files_div.add_style("overflow: auto")
        files_div.add_style("padding: 3px")
        right.add(files_div)

        files = os.listdir("%s/%s" % (base_dir, rel_dir))
        for file in files:
            if not file.endswith(".txt"):
                continue


            explore_div = DivWdg()
            link = "/%s/%s" % (rel_dir, file)
            explore_div.add("<a target='_blank' href='%s'>(+)</a>&nbsp;&nbsp;" % link)
            explore_div.add_style("float: left")
            files_div.add(explore_div)


            file_div = DivWdg()
            file_div.add_style("padding: 2px")
            file_div.add_class("hand")
            file_div.add_event("onmouseover", "this.style.background='#696969'")
            file_div.add_event("onmouseout", "this.style.background='#444'")
            file_div.add(file)
            files_div.add(file_div)

            file_div.add_behavior( {
                'type': 'click_up',
                'cbjs_action': '''
                var value = bvr.src_el.innerHTML;
                var top = bvr.src_el.getParent(".spt_sample_chart_top");
                var chart = top.getElement(".spt_sample_chart");
                spt.panel.load(chart, 'tactic.ui.chart.ChartWdg', {data_file:value});
                '''
            } )


        return top






