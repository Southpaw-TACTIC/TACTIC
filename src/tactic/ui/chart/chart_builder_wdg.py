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


from pyasm.common import Environment, Common, jsonloads
from pyasm.biz import Project
from pyasm.web import Widget, DivWdg, HtmlElement, WebContainer, Table
from pyasm.widget import SelectWdg, TextWdg
from pyasm.search import Search, SearchType
from tactic.ui.common import BaseRefreshWdg
from tactic.ui.input import TextInputWdg
from tactic.ui.widget import ActionButtonWdg
from tactic.ui.container import DynamicListWdg

import types

from .bar_chart_wdg import BarChartWdg


class ChartBuilderWdg(BaseRefreshWdg):
    '''class that builds a chart from tabular data in a TableLayoutWdg'''

    ARGS_KEYS = {
    'search_type': 'the search type that this chart will be displaying',
    'chart_type': 'line|bar|area - the type of chart to draw',
    'x_axis': 'the x-axis element',
    'y_axis': 'the y-axis elements',
    'kwargs': 'JSON formatted data which will be translated into kwargs',
    'search_keys': 'list of search keys to display',
    'document': 'document to be charted',
    }


    def get_styles(self):

        style = HtmlElement.style()
        style.add('''
        .spt_graph_option {
            margin-top: 10px;
        }

        .fa-plus-square-o {
            font-size: 15px;
            margin-top: 10px;
            margin-left: 10px;
        }

        .fa-minus-square-o {
            font-size: 15px;
            margin-top: 10px;
            margin-left: 3px;

        }

        .spt_graph_option_menu {
            display: flex;
        }

        .spt_chart_column_select {
            margin-bottom: 10px;
        }
        ''')

        return style


    def get_chart_type_select(self, category=None):

        category_type_dict = {'Simple': "bar|horizontalBar|stacked|stacked_horizontal",
                              'Time Scale': "line|bar",
                              'Categorization': "pie|doughnut" }
        chart_type_div = DivWdg()
        chart_type_div.add_class("hidden")
        chart_type_div.add_class("spt_chart_type_select")
        chart_type_div.add_class("spt_" + category.lower().replace(" ", "_") + "_chart_type")
        chart_type_div.add("<p class='spt_graph_option'>Chart Type:</p>")
        
        chart_select_div = SelectWdg("chart_type")
        chart_select_div.set_option("values", category_type_dict.get(category))
        chart_select_div.add_empty_option("-- Select --")

        onchange_action = '''
        
        let top = bvr.src_el.getParent(".spt_chart_builder");
        let detail = top.getElement(".spt_chart_detail");
        top.chart_type = bvr.src_el.value;

        '''
        chart_select_div.set_option("onchange", onchange_action)

        if self.chart_type:
            chart_select_div.set_value(self.chart_type)

        chart_type_div.add(chart_select_div)

        if category == "Simple":
            details = self.get_bar_chart_options()
            chart_type_div.add(details)
        elif category == "Categorization":
            details = self.get_categorization_chart_options()
            chart_type_div.add(details)
        elif category == "Time Scale":
            details = self.get_time_scale_chart_options()
            chart_type_div.add(details)

        return chart_type_div



    def get_bar_chart_options(self):

        # detail for bar charts
        detail_div = DivWdg()
        detail_div.add_class("spt_chart_detail")
        detail_div.add_class("spt_bar_chart_detail")

        container = DivWdg()
        container.add_class("spt_graph_option_menu")
        detail_div.add(container)
        container.add("<p class='spt_graph_option'>Y-Axis:</p>")
        plus_button = DivWdg()
        plus_button.add('<i class="option-buttons fa hand fa-plus-square-o"> </i>')

        plus_button.add_behavior( {
        'type': 'load',
        'cbjs_action': '''
        let top = bvr.src_el.getParent(".spt_chart_builder"); 
        let detail = top.getElement(".spt_bar_chart_detail");
        
        '''
        } )
        
        plus_button.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        let top = bvr.src_el.getParent(".spt_chart_builder"); 
        let select = top.getElement(".spt_chart_column_select");
        let detail = top.getElement(".spt_bar_chart_detail");
        
        let clone = spt.behavior.clone(select);
        detail.appendChild(clone);
        '''
        } )

        container.add(plus_button)

        minus_button = DivWdg()
        minus_button.add('<i class="option-buttons fa hand fa-minus-square-o"> </i>') 

        minus_button.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        let top = bvr.src_el.getParent(".spt_chart_builder"); 
        let selects = top.getElementsByClassName("spt_chart_column_select");
      
        if (selects.length > 1) {
            spt.behavior.destroy(selects[selects.length - 1]);
        }
        '''
        } )
        container.add(minus_button)

        column_select_div = SelectWdg("y_axis")
        column_select_div.set_option("values", self.columns)
        column_select_div.add_empty_option("-- Select --")
        column_select_div.add_class("spt_chart_column_select")

        onchange_action = '''
        let top = bvr.src_el.getParent(".spt_chart_builder");
        let expr = top.getElement(".spt_expression_div");

        if (bvr.src_el.value == "expression") {
            if (expr.hasClass("hidden")) expr.removeClass("hidden");
        } else {
            if (!expr.hasClass("hidden")) expr.addClass("hidden");
        }
        '''

        column_select_div.set_option("onchange", onchange_action)
        detail_div.add(column_select_div)

        expression_div = DivWdg()
        expression_div.add_class("spt_expression_div")
        expression_div.add_class("hidden")

        expression_div.add("<p class='spt_graph_option'>Expression:</p>")
        expr_input= TextInputWdg(name="expression")
        expr_input.add_style("width", "100%")
        expression_div.add(expr_input)
        detail_div.add(expression_div)

        return detail_div 




    def get_categorization_chart_options(self):

        detail_div = DivWdg()
        detail_div.add_class("spt_chart_detail")
        detail_div.add_class("spt_categorization_chart_detail")
        detail_div.add("<p class='spt_graph_option'>Category:</p>")

        column_select_div = SelectWdg("y_axis")
        column_select_div.set_option("values", self.columns)
        column_select_div.add_empty_option("-- Select --")

        detail_div.add(column_select_div)
        
        return detail_div



    def get_time_scale_chart_options(self):

        detail_div = DivWdg()
        detail_div.add_class("spt_chart_detail")
        detail_div.add_class("spt_time_scale_chart_detail")
        detail_div.add("<p class='spt_graph_option'>Category:</p>")

        column_select_div = SelectWdg("y_axis")
        column_select_div.set_option("values", self.columns)
        column_select_div.add_empty_option("-- Select --")

        detail_div.add(column_select_div)
        
        return detail_div



    def get_display(self):

        data = self.kwargs.get('kwargs')
        if data:
            data = jsonloads(data)
            self.kwargs.update(data)

        self.search_type = self.kwargs.get("search_type")

        self.x_axis = self.kwargs.get("x_axis")
        if not self.x_axis:
            self.x_axis = 'code'

        self.y_axis = self.kwargs.get("y_axis")
        if isinstance(self.y_axis, list):
            self.y_axis = "|".join( self.y_axis )

        self.chart_type = self.kwargs.get("chart_type")
        
        # get any search keys if any are passed in
        self.search_keys = self.kwargs.get("search_keys")
        self.document = self.kwargs.get("document")

        columns = SearchType.get_columns(self.search_type)
        cols_str = ""
        for col in columns:
            cols_str = cols_str + col + "|"
        cols_str += "expression"
        self.columns = cols_str

        top = DivWdg()
        top.add_class("spt_chart_builder")
        top.add_color("background", "background")
        top.add_border()

        top.add(self.get_styles())
        top.add_style("min-width: 600px")
        top.add_style("min-height: 400px")
        
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
        build_div.add_color("color", "color")

        build_div.add("<hr/>")


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
        spec_div.add_color("background", "background", -3)
        spec_div.add_class("spt_chart_spec")
        spec_div.add_border()
        spec_div.add_style("padding: 10px")
        spec_div.add_style("margin: 5px")
        spec_div.add_style("display: none")
        top.add(spec_div)


        # category select
        category_div = DivWdg()
        category_div.add("<p>Chart Category:</p>")
        category_select = SelectWdg()
        category_select.set_option("values", "Simple|Time Scale|Categorization")
        category_select.add_empty_option("-- Select --")
        category_div.add(category_select)
        spec_div.add(category_div)

        onchange_action = '''
        let value = bvr.src_el.value;

        let top = bvr.src_el.getParent(".spt_chart_builder");
        let category = "spt_" + value.toLowerCase().replace(" ", "_") + "_chart_type";
        let categories = top.getElementsByClassName("spt_chart_type_select");
        let details = top.getElementsByClassName("spt_chart_detail");

        top.chart_type = null;
        top.y_axis = null;

        for (let i = 0; i < categories.length; i++) {
            categories[i].addClass("hidden");
            if (categories[i].hasClass(category)) categories[i].removeClass("hidden");
        }


        '''
        category_select.set_option("onchange", onchange_action)



        # chart type select
        simple_chart_type_div = self.get_chart_type_select(category="Simple")
        time_chart_type_div = self.get_chart_type_select(category="Time Scale")
        categorization_chart_type_div = self.get_chart_type_select(category="Categorization")

        spec_div.add(simple_chart_type_div)
        spec_div.add(time_chart_type_div)
        spec_div.add(categorization_chart_type_div)



        spec_div.add("<br/>")
        button = ActionButtonWdg(title="Refresh")
        spec_div.add(button)
        spec_div.add(HtmlElement.br(2))
        button.add_style("float: left")

        button.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        let top = bvr.src_el.getParent(".spt_chart_builder");
        let chart = top.getElement(".spt_chart");
        let values = spt.api.get_input_values(top);
        
        if (values.expression) values.y_axis = values.expression;

        let y_axis = values.y_axis.join();
        let chart_type = values.chart_type.join();

        if (!y_axis || y_axis[y_axis.length - 1] == ',' || !chart_type) {
            spt.alert("Select all options before refreshing.");
            return;
        }

        spt.panel.refresh(chart, values);
        '''
        } )

        width = '600px'
        kwargs = {
            'y_axis': self.y_axis,
            'chart_type': self.chart_type,
            'search_type': self.search_type,
            'width': width,
            'search_keys': self.search_keys,
            'document': self.document,
        }

        chart_div = DivWdg()

        chart = BarChartWdg(**kwargs)
        chart_div.add(chart)
        top.add(chart_div)


        return top


