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


__all__ = ["BarChartWdg"]

# DEPRECATED

from pyasm.common import Environment, Common, jsonloads
from pyasm.biz import Project
from pyasm.web import Widget, DivWdg, HtmlElement, WebContainer
from pyasm.widget import SelectWdg, TextWdg
from pyasm.search import Search, SearchType
from tactic.ui.common import BaseRefreshWdg

import types, six


from .chart_data import ChartData, ChartElement

class BarChartWdg(BaseRefreshWdg):
    ''' '''


    ARGS_KEYS = {
    'chart_type': 'line|bar|area - type of chart',
    'width': 'The starting width of the chart',
    'search_keys': 'List of search keys to display',
    'x_axis': 'The x_axis element',
    'y_axis': 'List of elements to put on the y_axis'
    }

    def preprocess(self):
        self.max_value = 0
        self.min_value = 0
        self.steps = 0

        web = WebContainer.get_web()
        self.width = web.get_form_value("width")
        if not self.width:
            self.width = self.kwargs.get("width")


        self.chart_type = web.get_form_value("chart_type")
        if not self.chart_type:
            self.chart_type = self.kwargs.get("chart_type")
        if not self.chart_type:
            self.chart_type = 'bar'


        self.x_axis = web.get_form_value("x_axis")
        if not self.x_axis:
            self.x_axis = self.kwargs.get("x_axis")
        if not self.x_axis:
            self.x_axis = 'code'


        # FIXME: which should override???
        self.y_axis = web.get_form_values("y_axis")
        if not self.y_axis:
            self.y_axis = self.kwargs.get("y_axis")

        if self.y_axis:
            self.elements = self.y_axis
        else:
            self.elements = self.kwargs.get("elements")
            if not self.elements:
                self.elements = web.get_form_value("elements")

        if isinstance(self.elements, six.string_types):
            if self.elements:
                self.elements = self.elements.split('|')
            else:
                self.elements = []




        self.search_type = web.get_form_value("search_type")
        if not self.search_type:
            self.search_type = self.kwargs.get("search_type")


        self.search_keys = self.kwargs.get("search_keys")
        if self.search_type and self.search_type.startswith("@SOBJECT("):
            self.sobjects = Search.eval(self.search_type)
        elif self.search_keys:
            if isinstance(self.search_keys, six.string_types):
                self.search_keys = eval(self.search_keys)
            self.sobjects = Search.get_by_search_keys(self.search_keys)
        else:
            search = Search(self.search_type)
            search.add_limit(100)
            self.sobjects = search.get_sobjects()

        # get the definition
        sobjects = self.sobjects
        if sobjects:
            sobject = sobjects[0]
            search_type = sobject.get_search_type()
            view = 'definition'

            from pyasm.widget import WidgetConfigView
            self.config = WidgetConfigView.get_by_search_type(search_type, view)
        else:
            self.config = None


        self.widgets = {}


    def get_data(self, sobject):

        values = []
        labels = []

        if not self.config:
            return values, labels


        for element in self.elements:

            if (element.startswith("{") and element.endswith("}")) or element.startswith("@"):
                expr = element.strip("{}")
                value = Search.eval(expr, sobject, single=True)
                labels.append(element)

            else:

                options = self.config.get_display_options(element)
                attrs = self.config.get_element_attributes(element)


                label = attrs.get('title')
                if not label:
                    label = Common.get_display_title(element)
                labels.append(label)

                widget = self.widgets.get(element)
                if not widget:
                    widget = self.config.get_display_widget(element)
                    self.widgets[element] = widget

                widget.set_sobject(sobject)

                try:
                    value = widget.get_text_value()
                except:
                    value = 0

            if isinstance(value, six.string_types):
                if value.endswith("%"):
                    value = float( value.replace("%",'') )
                else:
                    value = 0

            if not value:
                value = 0

            #expression = options.get("expression")
            #if not expression:
            #    value = 0
            #else:
            #    value = Search.eval(expression, sobject, single=True)

            if value > self.max_value:
                self.max_value = value

            values.append(value)        


        return values, labels



    def get_display(self):
        self.preprocess()

        if not self.x_axis:
            chart_labels = [x.get_code() for x in self.sobjects]
        else:
            try:
                chart_labels = [x.get_value(self.x_axis) for x in self.sobjects]
            except:
                # FIXME ... put in some special logic for users since it
                # is used so often in charting
                if self.search_type == 'sthpw/login':
                    chart_labels = [x.get_value("login") for x in self.sobjects]
                else:
                    chart_labels = [x.get_code() for x in self.sobjects]


        top = DivWdg()
        top.add_class("spt_chart")
        self.set_as_panel(top)

        element_data = []
        labels = []
        element_values = []
        for sobject in self.sobjects:
            values, labels = self.get_data(sobject)

            for i, value in enumerate(values):
                if i >= len(element_data):
                    element_values = []
                    element_data.append(element_values)
                else:
                    element_values = element_data[i]

                element_values.append(value)


        self.colors = self.kwargs.get("colors")
        if not self.colors:
            self.colors = [
                'rgba(0,255,0,0.5)',
                'rgba(0,0,255,0.5)',
                'rgba(255,0,0,0.5)',
                'rgba(255,255,0,0.5)',
                'rgba(0,255,255,0.5)',
                'rgba(255,0,255,0.5)',
            ]
 


        #from .chart_wdg import ChartWdg as XXChartWdg
        from .chart_js_wdg import ChartJsWdg as XXChartWdg

        from .chart_wdg import ChartData as XXChartData


        chart = XXChartWdg(
            height="400px",
            width="600px",
            chart_type=self.chart_type,
            labels=chart_labels,
            label_values=[i+0.5 for i,x in enumerate(chart_labels)],
            rotate_x_axis=True,
        )
        chart.add_color("background", "background")
        top.add(chart)

        count = 0
        for element_values in element_data:
            label = labels[count]
            data = XXChartData(
                label=label,
                color=self.colors[count%5],
                data=element_values,
                x_data=[i+0.5 for i,x in enumerate(chart_labels)]
            )
            chart.add(data)
            count += 1

        """
        data = XXChartData(
            color="rgba(0, 128, 0, 1.0)",
            chart_type='line',
            data=element_values,
            x_data=[i+0.5 for i,x in enumerate(chart_labels)]
        )
        chart.add(data)
        """


        return top

        





