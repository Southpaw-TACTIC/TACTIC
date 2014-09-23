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

__all__ = ["ChartBuilderWdg"]

# DEPRECATED

from pyasm.common import Environment, Common, jsonloads
from pyasm.biz import Project
from pyasm.web import Widget, DivWdg, HtmlElement, WebContainer, Table
from pyasm.widget import SelectWdg, TextWdg
from pyasm.search import Search, SearchType
from tactic.ui.common import BaseRefreshWdg

import types
import random


from bar_chart_wdg import BarChartWdg

# DEPRECATED

class ChartBuilderWdg(BaseRefreshWdg):
    '''class that builds a chart from tabular data in a TableLayoutWdg'''

    ARGS_KEYS = {
    'search_type': 'the search type that this chart will be displaying',
    'chart_type': 'line|bar|area - the type of chart to draw',
    'x_axis': 'the x-axis element',
    'y_axis': 'the y-axis elements',
    'kwargs': 'JSON formatted data which will be translated into kwargs',
    'search_keys': 'list of search keys to display'
    }

    def get_display(my):

        data = my.kwargs.get('kwargs')
        if data:
            data = jsonloads(data)
            my.kwargs.update(data)


        my.search_type = my.kwargs.get("search_type")

        my.x_axis = my.kwargs.get("x_axis")
        if not my.x_axis:
            my.x_axis = 'code'

        my.y_axis = my.kwargs.get("y_axis")
        if type(my.y_axis) == types.ListType:
            my.y_axis = "|".join( my.y_axis )

        my.chart_type = my.kwargs.get("chart_type")
        if not my.chart_type:
            my.chart_type = 'bar'

        # get any search keys if any are passed in
        my.search_keys = my.kwargs.get("search_keys")


        top = DivWdg()
        top.add_class("spt_chart_builder")
        top.add_color("background", "background")
        top.add_border()



        from tactic.ui.app import HelpButtonWdg
        help_button = HelpButtonWdg(alias='charting')
        top.add( help_button )
        help_button.add_style("float: right")

        


        project = Project.get()
        search_types = project.get_search_types(include_sthpw=True)
        search_types = [x.get_value("search_type") for x in search_types]

        build_div = DivWdg()

        from pyasm.widget import SwapDisplayWdg
        swap_wdg = SwapDisplayWdg.get_triangle_wdg()
        swap_script = swap_wdg.get_swap_script()
        build_div.add(swap_wdg)

        build_div.add("<b>Chart Specifications</b>")
        build_div.add_style("margin-bottom: 5px")
        build_div.add_style("height: 25px")
        build_div.add_style("padding-top: 5px")
        build_div.add_gradient("background", "background", -10)
        build_div.add_color("color", "color")


        build_div.add_class("hand")
        build_div.add_class("SPT_DTS")
        top.add(build_div)
        build_div.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_chart_builder");
            var spec = top.getElement(".spt_chart_spec");
            //spt.api.toggle_show_hide(spec);
            spt.toggle_show_hide(spec);
            %s;
            ''' % swap_script
        } )

        spec_div = DivWdg()
        spec_div.add_color("color", "color3")
        spec_div.add_color("background", "background3")
        spec_div.add_class("spt_chart_spec")
        spec_div.add_border()
        spec_div.add_style("padding: 10px")
        spec_div.add_style("margin: 5px")
        spec_div.add_style("display: none")
        top.add(spec_div)

        table = Table()
        table.add_color("color", "color3")
        spec_div.add(table)

        # add the search type selector
        table.add_row()
        table.add_cell("Search Type: ")

        search_type_div = DivWdg()
        search_type_select = TextWdg("search_type")
        search_type_select.set_value(my.search_type)
        #search_type_select.set_option("values", search_types)
        search_type_div.add(search_type_select)
        table.add_cell(search_type_div)

        # add the chart type selector
        table.add_row()
        table.add_cell("Chart Type: ")

        type_div = DivWdg()
        #type_div.add_style("padding: 3px")
        type_select = SelectWdg("chart_type")
        type_select.set_option("values", "line|bar|area")
        if my.chart_type:
            type_select.set_value(my.chart_type)
        type_div.add(type_select)
        table.add_cell(type_div)

        # add the chart type selector
        table.add_row()
        table.add_cell("X-Axis: ")

        # need to find all expression widgets or use get_text_value()?
        x_axis_div = DivWdg()
        x_axis_text = TextWdg("x_axis")
        x_axis_text.set_value("code")
        x_axis_div.add(x_axis_text)
        table.add_cell(x_axis_div)



        # add the chart type selector
        table.add_row()
        td = table.add_cell("Y-Axis: ")
        td.add_style("vertical-align: top")

        y_axis_div = DivWdg()
        #y_axis_text = TextWdg("y_axis")
        #if my.y_axis:
        #    y_axis_text.set_value(my.y_axis)
        #y_axis_div.add(y_axis_text)
        td = table.add_cell(y_axis_div)

        # add in a list of entries
        from tactic.ui.container import DynamicListWdg
        list_wdg = DynamicListWdg()
        for value in my.y_axis.split("|"):
            item = TextWdg("y_axis")
            item.set_value(value, set_form_value=False)
            list_wdg.add_item(item)
        y_axis_div.add(list_wdg)



        spec_div.add("<br/>")
        from tactic.ui.widget import ActionButtonWdg
        button = ActionButtonWdg(title="Refresh")
        spec_div.add(button)
        spec_div.add(HtmlElement.br(2))
        button.add_style("float: left")

        button.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        var top = bvr.src_el.getParent(".spt_chart_builder");
        var chart = top.getElement(".spt_chart");
        var values = spt.api.get_input_values(top);
        //var values = spt.api.Utility.get_input_values(top);
        spt.panel.refresh(chart, values);
        '''
        } )

        #TODO: provide a field for user to type in the chart name
        """

        button = ActionButtonWdg(title="Save")
        spec_div.add(button)
        button.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        var top = bvr.src_el.getParent(".spt_chart_builder");
        var chart = top.getElement(".spt_chart");
        var values = spt.api.get_input_values(top);

        var login = 'admin';
        var search_type = 'SideBarWdg';
        var side_bar_view = 'project_view';
        var unique_el_name = 'chart_test'

        var kwargs = {};
        kwargs['login'] = null;
        //if (save_as_personal) 
        //    kwargs['login'] = login;
        kwargs['class_name'] = 'tactic.ui.chart.ChartBuilderWdg';

        var display_options = {};
        display_options['search_type'] = 'prod/asset'
        kwargs['display_options'] = display_options;
 
        kwargs['unique'] = true;
        //if (new_title)
        //    kwargs['element_attrs'] = {'title': new_title}; 

        var server = TacticServerStub.get()
        server.add_config_element(search_type, side_bar_view, unique_el_name, kwargs);
        spt.panel.refresh("side_bar");
        '''
        } )
        """

        width = '600px'
        kwargs = {
            'y_axis': my.y_axis,
            'chart_type': my.chart_type,
            'search_type': my.search_type,
            'width': width,
            'search_keys': my.search_keys
        }

        chart_div = DivWdg()
        chart = BarChartWdg(**kwargs)

        chart_div.add(chart)
        top.add(chart_div)


        #from chart2_wdg import SampleSObjectChartWdg
        #chart = SampleSObjectChartWdg(**kwargs)
        #chart_div.add(chart)





        return top


