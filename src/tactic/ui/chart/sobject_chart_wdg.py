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


__all__ = ["SObjectChartWdg", "CalendarChartWdg"]

from pyasm.common import Environment, Common, jsonloads
from pyasm.biz import Project
from pyasm.web import Widget, DivWdg, HtmlElement, WebContainer, Table
from pyasm.widget import SelectWdg, TextWdg
from pyasm.search import Search, SearchType
from tactic.ui.common import BaseRefreshWdg

import types

from chart_wdg import ChartWdg as ChartWdg
from chart_wdg import ChartData as ChartData


class BaseChartWdg(BaseRefreshWdg):

    def get_title_wdg(self, title):
        #date = "@FORMAT(@STRING($TODAY),'Dec 31, 1999')"
        #date = Search.eval(date, single=True)

        title_wdg = DivWdg()
        title_wdg.add(title)
        #title_wdg.add(" [%s]" % date)
        title_wdg.add_style("font-size: 1.33em")
        title_wdg.add_color("background", "background3")
        title_wdg.add_color("color", "color3")
        title_wdg.add_style("padding: 10px")
        title_wdg.add_style("font-weight: bold")
        title_wdg.add_style("text-align: center")
        return title_wdg






class SObjectChartWdg(BaseChartWdg):
    ''' '''


    ARGS_KEYS = {
    'chart_type': 'line|bar|bar3d - type of chart',
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
            while len(self.elements) >= len(self.colors):
                self.colors.extend(self.colors)
        else:
            if isinstance(self.colors,basestring):
                self.colors = self.colors.split("|")


        chart_type = self.kwargs.get("chart_type")
        if chart_type:
            self.chart_types = [chart_type for x in self.elements]
        else:
            self.chart_types = self.kwargs.get("chart_types")
            if not self.chart_types:
                self.chart_types = ['bar' for x in self.elements]



        expression = web.get_form_value("expression")
        if not expression:
            expression = self.kwargs.get("expression")



        self.search_type = web.get_form_value("search_type")
        if not self.search_type:
            self.search_type = self.kwargs.get("search_type")

        self.search_keys = self.kwargs.get("search_keys")


        if expression:
            self.sobjects = Search.eval(expression)
        elif self.search_type and self.search_type.startswith("@SOBJECT("):
            self.sobjects = Search.eval(self.search_type)
        elif self.search_keys:
            if isinstance(self.search_keys, basestring):
                self.search_keys = eval(self.search_keys)
            self.sobjects = Search.get_by_search_keys(self.search_keys)
        else:
            search = Search(self.search_type)
            search.add_limit(100)
            self.sobjects = search.get_sobjects()


        if not self.sobjects:
            return

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
        top.add_style("position: relative")

        title = self.kwargs.get("title")
        if title:
            title_wdg = self.get_title_wdg(title)
            top.add(title_wdg)


        if not self.sobjects:
            top.add("No results found")
            return top



        element_data = {}

        chart_labels = []
        element_values = []

        # get the labels and values for each sobject
        for sobject in self.sobjects:

            chart_labels.append( sobject.get_code() )

            values, labels = self.get_data(sobject)
            for value, label in zip(values, labels):

                data = element_data.get(label)
                if data == None:
                    data = []
                    element_data[label] = data
                data.append(value)



        width = self.kwargs.get("width")
        if not width:
            width = '800px'
        height = self.kwargs.get("height")
        if not height:
            height = '500px'


        chart_div = DivWdg()
        chart_div.add_style("width", width)
        chart_div.add_style("height", height)
        chart_div.center()

        if not self.sobjects:
            msg_div = DivWdg()
            msg_div.add_style("position: absolute")
            chart_div.add(msg_div)
            msg_div.add_style("width: 200px")
            msg_div.add_style("height: 15px")
            msg_div.add_style("padding: 50px")
            msg_div.add_style("margin-top: 200px")
            msg_div.add("<b>No results found</b>")
            msg_div.add_border()
            msg_div.add_color("color", "color3")
            msg_div.add_color("background", "background3")
            msg_div.add_style("top: 0px")
            msg_div.add_style("left: 350")
            msg_div.add_style("z-index: 100")
            msg_div.add_style("text-align: center")


        chart = ChartWdg(
            width=width,
            height=height,
            chart_type='bar',
            #legend=self.elements,
            labels=chart_labels,
            label_values=[i+0.5 for i,x in enumerate(chart_labels)]
        )
        chart_div.add(chart)

        top.add(chart_div)
        top.add_color("background", "background")
        top.add_color("color", "color")



        # draw a legend
        from chart_wdg import ChartLegend
        legend = ChartLegend(labels=self.elements)
        top.add(legend)
        #legend.add_style("width: 200px")
        legend.add_style("position: absolute")
        legend.add_style("top: 0px")
        legend.add_style("left: 0px")



        for i, key in enumerate(element_data.keys()):

            if self.colors:
                color = self.colors[i]
            else:
                color = 'rgba(128, 0, 0, 1.0)'

            element_values = element_data.get(key)

            chart_data = ChartData(
                chart_type=self.chart_types[i],
                color=color,
                data=element_values,
                x_data=[i+0.5 for i,x in enumerate(chart_labels)]
            )
            chart.add(chart_data)


        return top



from dateutil import parser, rrule
from datetime import datetime, timedelta


class CalendarChartWdg(BaseChartWdg):

    ARGS_KEYS = {
    'title': {
        'description': '',
        'type': 'TextWdg',
        'category': 'Display'
    },
    'interval': {
        'description': 'Interval between each time period to collate data',
        'type': 'TextWdg',
        'category': 'Display'
    },
    'chart_data': {
        'description': 'Chart description for each data set',
        'type': 'TextAreaWdg',
        'category': 'Advanced'
    },
    'x_title': {
        'description': 'X Axis Title',
        'type': 'TextWdg',
        'category': 'Display'
    },
    'y_title': {
        'description': 'Y Axis Title',
        'type': 'TextWdg',
        'category': 'Display'
    },
    'start_date': {
        'description': 'Expression for start date',
        'type': 'TextWdg',
        'category': 'Display'
    },
    'end_date': {
        'description': 'Expression for start date',
        'type': 'TextWdg',
        'category': 'Display'
    },
    'expression': {
        'description': 'Expression to search for sobjects',
        'type': 'TextWdg',
        'category': 'Display'
    },

    'column': {
        'description': 'Column to collate sobjects into date intervals',
        'type': 'TextWdg',
        'category': 'Display'
    },


    'chart_type': {
        'description': 'Type of chart to display',
        'type': 'SelectWdg',
        'values': 'line|bar|bar3d',
        'category': 'Display'
    }

    }





    def postprocess_sobjects(self, sobjects):
        return sobjects


    """
    def postprocess_sobjects(self, sobjects):
        # custom
        for sobject in sobjects:
            data = sobject.get_json_value("data")
            for key, value in data.items():
                new_sobject = SearchType.create("sthpw/virtual")
                new_sobject.set_value("date", key)
                new_sobject.set_value("value", value)
                new_sobjects.append(sobject)
        return new_sobjects
    """



    def get_display(self):

        top = self.top

        top.add_color("background", "background")
        top.add_gradient("color", "color")

        #top.add_style("background", "#000")
        #top.add_style("opacity: 0.95")
        #top.add_style("color: #FFF")

        #top.add_style("padding-top: 10px")
        top.add_style("position: relative")

        title = self.kwargs.get("title")
        if title:
            title_wdg = self.get_title_wdg(title)
            top.add(title_wdg)

        # get the column to use as a date for searching
        self.column = self.kwargs.get("column")
        if not self.column:
            self.column = 'timestamp'


        # elements
        elements = self.kwargs.get("elements")
        if elements:
            if isinstance(elements, basestring):
                elements = elements.split("|")
        elif self.kwargs.get("chart_data"):
            elements = []
        else:
            elements = ['{@COUNT()}']


        # set some start and end dates
        start_date = self.kwargs.get("start_date")
        if not start_date:
            start_date = None
        else:
            if start_date.startswith("{") and start_date.endswith("}"):
                start_date = Search.eval(start_date)

            start_date = parser.parse(start_date)

        end_date = self.kwargs.get("end_date")
        if not end_date:
            end_date = None
        else:
            if end_date.startswith("{") and end_date.endswith("}"):
                end_date = Search.eval(end_date)
            end_date = parser.parse(end_date)


        expression = self.kwargs.get("expression")
        search_type = self.kwargs.get("search_type")
        if expression:
            sobjects = Search.eval(expression)
        elif search_type:
            search = Search(search_type)
            if start_date:
                search.add_filter(self.column, start_date, op=">")
            if end_date:
                search.add_filter(self.column, end_date, op="<")
            sobjects = search.get_sobjects()

        else:
            sobjects = []



        # Is this a plot or a chart
        # A plot puts the X-axis at the right place.
        # A chart has a interval in which data is combined

        self.interval = self.kwargs.get("interval")
        if not self.interval:
            self.interval = 'weekly'
            #self.interval = 'monthly'


        if not sobjects:
            if not start_date:
                min_date = datetime.today() - timedelta(days=30)
            else:
                min_date = start_date

            if not end_date:
                max_date = datetime.today() + timedelta(days=30)
            else:
                max_date = end_date
        else:
            min_date = start_date
            max_date = end_date


        for sobject in sobjects:
            timestamp = sobject.get_value(self.column)
            timestamp = parser.parse(timestamp)
            if min_date == None or timestamp < min_date:
                min_date = timestamp
            if max_date == None or timestamp > max_date:
                max_date = timestamp


        # defined the buckets based on interval
        dates = []
        if self.interval == 'weekly':
            min_date = datetime(min_date.year, min_date.month, min_date.day)
            max_date = datetime(max_date.year, max_date.month, max_date.day)
            min_date = min_date - timedelta(days=8)
            max_date = max_date + timedelta(days=8)

            dates = list(rrule.rrule(rrule.WEEKLY, byweekday=0, dtstart=min_date, until=max_date))


        elif self.interval == 'daily':
            min_date = datetime(min_date.year, min_date.month, min_date.day)
            max_date = datetime(max_date.year, max_date.month, max_date.day)
            min_date = min_date - timedelta(days=1)
            #max_date = max_date + timedelta(days=1)

            dates = list(rrule.rrule(rrule.DAILY, dtstart=min_date, until=max_date))


        elif self.interval == 'monthly':
            min_date = datetime(min_date.year, min_date.month, 1)
            if max_date.month == 12:
                year = max_date.year+1
                month = 1
            else:
                year = max_date.year
                month = max_date.month + 1

            max_date = datetime(year, month, 1)
            dates = list(rrule.rrule(rrule.MONTHLY, bymonthday=1, dtstart=min_date, until=max_date))


        self.dates_dict = {}
        for date in dates:
            self.dates_dict[str(date)] = []


        sobjects = self.postprocess_sobjects(sobjects)



        # put the appropriate sobjects in each date_dict item
        for sobject in sobjects:

            timestamp = sobject.get_value(self.column)
            timestamp = parser.parse(timestamp)

            if self.interval == "weekly":
                # put in the week
                timestamp = list(rrule.rrule(rrule.WEEKLY, byweekday=0, dtstart=timestamp-timedelta(days=7), count=1))
                timestamp = timestamp[0]
                timestamp = datetime(timestamp.year,timestamp.month,timestamp.day)
            elif self.interval == "daily":
                timestamp = datetime(timestamp.year,timestamp.month,timestamp.day)

            else:
                timestamp = datetime(timestamp.year,timestamp.month,1)

            if self.dates_dict:
                interval_sobjects = self.dates_dict[str(timestamp)]
                interval_sobjects.append(sobject)



        # get all the chart labels
        chart_labels = []
        for date in dates:
            if self.interval == 'weekly':
                #chart_labels.append("Week %s" % date.strftime("%W"))
                label = (date + timedelta(days=6)).strftime("%d")
                chart_labels.append("%s - %s" % (date.strftime("%b %d"), label))
            elif self.interval == 'daily':
                chart_labels.append(date.strftime("%b %d"))
            else:
                chart_labels.append(date.strftime("%b %Y"))


        self.sobjects = sobjects


        width = self.kwargs.get("width")
        if not width:
            width = "800px"

        height = self.kwargs.get("height")
        if not height:
            height = "500px"


        x_title = self.kwargs.get("x_title")
        #x_title = Search.eval(x_title)
        y_title = self.kwargs.get("y_title")
        #y_title = Search.eval(y_title)




        # draw a legend
        legend = None
        from chart_wdg import ChartLegend
        labels = self.kwargs.get("labels")
        if labels:
            legend = ChartLegend()
            labels = labels.split("|")
            legend.set_labels(labels)
            top.add(legend)
            legend.add_style("width: %s" % str(len(labels)*200))
            legend.add_style("margin-left: auto")
            legend.add_style("margin-right: auto")
            legend.add_style("margin-top: 5px")

            #legend.add_style("width: 200px")
            #legend.add_style("position: absolute")
            #legend.add_style("top: 40px")
            #legend.add_style("left: 300px")




        table = Table()
        table.add_color("color", "color")
        top.add(table)
        table.add_row()
        table.center()
        table.add_style("width: 1%")


        if y_title:
            y_title = y_title.replace(" ", "&nbsp;")

            y_axis_div = DivWdg()
            td = table.add_cell(y_axis_div)
            td.add_style("vertical-align: middle")
            td.add_style("width: 1%")
            y_axis_div.add(y_title)
            y_axis_div.add_style("-moz-transform: rotate(-90deg)")
            y_axis_div.add_style("-webkit-transform: rotate(-90deg)")
            y_axis_div.add_style("font-size: 1.33em")
            y_axis_div.add_style("height: 100%")
            y_axis_div.add_style("width: 30px")



        rotate_x_axis = self.kwargs.get("rotate_x_axis")
        y_axis_mode = self.kwargs.get("y_axis_mode")

        chart = ChartWdg(
            width=width,
            height=height,
            chart_type='bar',
            #legend=self.elements,
            labels=chart_labels,
            label_values=[i+0.5 for i,x in enumerate(chart_labels)],
            rotate_x_axis=rotate_x_axis,
            y_axis_mode=y_axis_mode
        )
        table.add_cell(chart)


        chart_type = self.kwargs.get("chart_type")
        if not chart_type:
            chart_type = 'bar'



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
            #while len(self.elements) >= len(self.colors):
            #    self.colors.extend(self.colors)
        else:
            if isinstance(self.colors,basestring):
                self.colors = self.colors.split("|")


        if legend:
            legend.set_colors(self.colors)


        element_count = 0

        x_data=[i+0.5 for i,x in enumerate(chart_labels)]
        for i, element in enumerate(elements):


            data_values = self.get_data_values(self.dates_dict, dates, element, self.sobjects)

            chart_data = ChartData(
                chart_type=chart_type,
                data=data_values,
                color=self.colors[element_count],
                x_data=x_data
            )
            chart.add(chart_data)
            element_count += 1



        # add in individual charts
        chart_data = self.kwargs.get("chart_data")
        if chart_data and isinstance(chart_data, basestring):
            chart_data = jsonloads(chart_data)

        if not chart_data:
            chart_data = []
        else:
            # draw back to front
            chart_data.reverse()

        for options in chart_data:

            column = options.get("column")
            if not column:
                column = self.column


            expression = options.get("expression")
            if expression:

                # extra filters
                extra = {}
                #extra['sthpw/task'] = []
                #if start_date:
                #    extra['sthpw/task'].append([column, '>', start_date])
                #if end_date:
                #    extra['sthpw/task'].append([column, '<', end_date])


                sobjects = Search.eval(expression, extra_filters=extra)
                dates_dict = self.get_dates_dict(sobjects, dates, column)
            else:
                sobjects = self.sobjects
                dates_dict = self.dates_dict

            data = self.get_data_values(dates_dict, dates, options['element'], sobjects)


            options['data'] = data
            options['x_data'] = x_data
            if not options.get("color"):
                options['color'] = self.colors[element_count]

            if not options.get("chart_type"):
                options['chart_type'] = chart_type

            str_options = {}
            for x, y in options.items():
                str_options[str(x)] = y

            chart_data = ChartData(**str_options)

            chart.add(chart_data)

            element_count += 1


        table.add_row()


        # add the x-axis title
        if x_title:
            x_title = x_title.replace(" ", "&nbsp;")

            x_axis_div = DivWdg()
            td = table.add_cell(x_axis_div)
            td.add_style("text-align: center")
            td.add_style("width: 1%")
            x_axis_div.add(x_title)
            x_axis_div.add_style("font-size: 1.33em")
            x_axis_div.add_style("width: 100%")
            x_axis_div.add_style("height: 30px")


        return top






    def get_dates_dict(self, sobjects, dates, column):

        dates_dict = {}
        for date in dates:
            dates_dict[str(date)] = []


        for sobject in sobjects:
            timestamp = sobject.get_value(column)
            timestamp = parser.parse(timestamp)

            if self.interval == "weekly":
                # put in the week
                timestamp = list(rrule.rrule(rrule.WEEKLY, byweekday=0, dtstart=timestamp-timedelta(days=7), count=1))
                timestamp = timestamp[0]
                timestamp = datetime(timestamp.year,timestamp.month,timestamp.day)


            elif self.interval == "daily":

                timestamp = list(rrule.rrule(rrule.DAILY, dtstart=timestamp-timedelta(days=1), count=1))
                timestamp = timestamp[0]
                timestamp = datetime(timestamp.year,timestamp.month,timestamp.day)

            else:
                timestamp = datetime(timestamp.year,timestamp.month,1)

            interval_sobjects = dates_dict.get(str(timestamp))
            if interval_sobjects == None:
                interval_sobjects = []
                dates_dict[str(timestamp)] = interval_sobjects

            interval_sobjects.append(sobject)

        #for key, x in dates_dict.items():
        #    print key, len(x)

        return dates_dict


    def get_data_values(self, dates_dict, dates, element, all_sobjects):
        element_values = []

        if element.startswith("{") and element.endswith("}"):
            expr = element.lstrip("{")
            expr = expr.rstrip("}")
        else:
            expr = element


        vars = {}
        if self.kwargs.get("total"):
            total = Search.eval(self.kwargs.get("total"), sobjects=all_sobjects, single=True, vars=vars)
            vars['total'] = total
        vars['running'] = 0


        for date in dates:
            sobjects = dates_dict.get(str(date))

            if expr:
                value = Search.eval(expr, sobjects=sobjects, single=True, vars=vars)
            else:
                value = len(sobjects)


            # add the display value
            element_values.append(value)

            if self.kwargs.get("running"):
                running = Search.eval(self.kwargs.get("running"), sobjects=sobjects, single=True, vars=vars)
                if not running:
                    running = 0
                vars['running'] = running


        return element_values

