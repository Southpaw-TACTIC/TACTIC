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

import types


from chart_data import ChartData, ChartElement

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

        if isinstance(self.elements,basestring):
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
            if isinstance(self.search_keys, basestring):
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

            if element.startswith("{") and element.endswith("}"):
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

            if isinstance(value, basestring):
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


        print "chart_labels: ", chart_labels
        print "element: ", element_values

        from chart_wdg import ChartWdg as XXChartWdg
        from chart_wdg import ChartData as XXChartData


        chart = XXChartWdg(
            height="400px",
            width="600px",
            chart_type=self.chart_type,
            labels=chart_labels,
            label_values=[i+0.5 for i,x in enumerate(chart_labels)]
        )
        chart.add_gradient("background", "background", 5, -20)
        top.add(chart)

        data = XXChartData(
            color="rgba(128, 0, 0, 1.0)",
            data=element_values,
            x_data=[i+0.5 for i,x in enumerate(chart_labels)]
        )
        chart.add(data)

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

        

        """
        # look at the max value and adjust
        import math
        if not self.max_value:
            self.max_value = 10

        exp = int( math.log10(self.max_value) ) -1
        top_value = math.pow(10, exp+1)
        steps = math.pow(10, exp) * 5

        while top_value < self.max_value*1.1:
            top_value += steps

        self.max_value = top_value
        if top_value / steps < 5:
            steps = steps / 5
        elif top_value / steps > 20:
            steps = steps * 2
        self.steps = steps




        rotate = 45
        if rotate:
            chart_labels = [{'colour': '#999999', 'text': x, 'rotate': rotate} for x in chart_labels]

        chart_data = ChartData()
        x_axis = {
            "labels": {
              "labels": chart_labels
            },
            'colour': '#999999',
        }
        chart_data.set_value('x_axis', x_axis)

        y_axis = {
            'max': self.max_value,
            'min': self.min_value,
            'steps': self.steps,
            'colour': '#999999',
        }
        chart_data.set_value('y_axis', y_axis)


        # create an element in the chart

        colors = ['#000099', '#009900', '#999900', '#009999', '#990099', '#990000', '#009900', '#000099', '#999900', '#990000']
        while len(element_data) >= len(colors):
            colors.extend(colors)


        for i, element_values in enumerate(element_data):
            color = colors[i]
            label = labels[i]

            # create the element
            element = ChartElement(self.chart_type)
            element.set_values(element_values)
            chart_data.add_element(element)


            element.set_param("colour", color)
            element.set_param("text", label)


        # draw the chart
        chart = ChartWdg(chart=chart_data, width=self.width)
        top.add(chart)
        return top

        """





