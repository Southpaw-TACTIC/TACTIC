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

from pyasm.common import Environment, Common, jsonloads
from pyasm.biz import Project
from pyasm.web import Widget, DivWdg, HtmlElement, WebContainer
from pyasm.widget import SelectWdg, TextWdg
from pyasm.search import Search, SearchType
from tactic.ui.common import BaseRefreshWdg

import types

from chart_wdg import ChartWdg
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

    def preprocess(my):
        my.max_value = 0
        my.min_value = 0
        my.steps = 0

        web = WebContainer.get_web()
        my.width = web.get_form_value("width")
        if not my.width:
            my.width = my.kwargs.get("width")


        my.chart_type = web.get_form_value("chart_type")
        if not my.chart_type:
            my.chart_type = my.kwargs.get("chart_type")
        if not my.chart_type:
            my.chart_type = 'bar'


        my.x_axis = web.get_form_value("x_axis")
        if not my.x_axis:
            my.x_axis = my.kwargs.get("x_axis")
        if not my.x_axis:
            my.x_axis = 'code'


        # FIXME: which should override???
        my.y_axis = web.get_form_values("y_axis")
        if not my.y_axis:
            my.y_axis = my.kwargs.get("y_axis")

        if my.y_axis:
            my.elements = my.y_axis
        else:
            my.elements = my.kwargs.get("elements")
            if not my.elements:
                my.elements = web.get_form_value("elements")

        if isinstance(my.elements,basestring):
            if my.elements:
                my.elements = my.elements.split('|')
            else:
                my.elements = []




        my.search_type = web.get_form_value("search_type")
        if not my.search_type:
            my.search_type = my.kwargs.get("search_type")


        my.search_keys = my.kwargs.get("search_keys")
        if my.search_type and my.search_type.startswith("@SOBJECT("):
            my.sobjects = Search.eval(my.search_type)
        elif my.search_keys:
            if isinstance(my.search_keys, basestring):
                my.search_keys = eval(my.search_keys)
            my.sobjects = Search.get_by_search_keys(my.search_keys)
        else:
            search = Search(my.search_type)
            search.add_limit(100)
            my.sobjects = search.get_sobjects()

        # get the definition
        sobjects = my.sobjects
        if sobjects:
            sobject = sobjects[0]
            search_type = sobject.get_search_type()
            view = 'definition'

            from pyasm.widget import WidgetConfigView
            my.config = WidgetConfigView.get_by_search_type(search_type, view)
        else:
            my.config = None


        my.widgets = {}


    def get_data(my, sobject):

        values = []
        labels = []

        if not my.config:
            return values, labels


        for element in my.elements:

            if element.startswith("{") and element.endswith("}"):
                expr = element.strip("{}")
                value = Search.eval(expr, sobject, single=True)
                labels.append(element)

            else:

                options = my.config.get_display_options(element)
                attrs = my.config.get_element_attributes(element)


                label = attrs.get('title')
                if not label:
                    label = Common.get_display_title(element)
                labels.append(label)

                widget = my.widgets.get(element)
                if not widget:
                    widget = my.config.get_display_widget(element)
                    my.widgets[element] = widget

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

            if value > my.max_value:
                my.max_value = value

            values.append(value)        


        return values, labels



    def get_display(my):
        my.preprocess()

        if not my.x_axis:
            chart_labels = [x.get_code() for x in my.sobjects]
        else:
            try:
                chart_labels = [x.get_value(my.x_axis) for x in my.sobjects]
            except:
                # FIXME ... put in some special logic for users since it
                # is used so often in charting
                if my.search_type == 'sthpw/login':
                    chart_labels = [x.get_value("login") for x in my.sobjects]
                else:
                    chart_labels = [x.get_code() for x in my.sobjects]


        top = DivWdg()
        top.add_class("spt_chart")
        my.set_as_panel(top)

        element_data = []
        labels = []
        element_values = []
        for sobject in my.sobjects:
            values, labels = my.get_data(sobject)

            for i, value in enumerate(values):
                if i >= len(element_data):
                    element_values = []
                    element_data.append(element_values)
                else:
                    element_values = element_data[i]

                element_values.append(value)


        print "chart_labels: ", chart_labels
        print "element: ", element_values

        from chart2_wdg import ChartWdg as XXChartWdg
        from chart2_wdg import ChartData as XXChartData


        chart = XXChartWdg(
            height="400px",
            width="600px",
            chart_type=my.chart_type,
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
        if not my.max_value:
            my.max_value = 10

        exp = int( math.log10(my.max_value) ) -1
        top_value = math.pow(10, exp+1)
        steps = math.pow(10, exp) * 5

        while top_value < my.max_value*1.1:
            top_value += steps

        my.max_value = top_value
        if top_value / steps < 5:
            steps = steps / 5
        elif top_value / steps > 20:
            steps = steps * 2
        my.steps = steps




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
            'max': my.max_value,
            'min': my.min_value,
            'steps': my.steps,
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
            element = ChartElement(my.chart_type)
            element.set_values(element_values)
            chart_data.add_element(element)


            element.set_param("colour", color)
            element.set_param("text", label)


        # draw the chart
        chart = ChartWdg(chart=chart_data, width=my.width)
        top.add(chart)
        return top

        """





