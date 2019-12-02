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


__all__ = ['ChartJsWdg', 'SampleBarChartJsWdg']

from pyasm.common import Environment, Common, jsonloads
from pyasm.search import Search
from pyasm.biz import Project
from pyasm.web import Widget, DivWdg, HtmlElement, WebContainer, Canvas

from tactic.ui.common import BaseRefreshWdg

import six

from .chart_wdg import ChartData


class SampleBarChartJsWdg(BaseRefreshWdg):

    ARGS_KEYS = {
    'width': {
        'description': 'Width of widget',
        'category': 'Options',
        'order': 0
    },
    'height': {
        'description': 'Height of widget',
        'category': 'Options',
        'order': 1
    },
    }



    def get_display(self):

        top = self.top

        #top.add_gradient("background", "background", 5, -20)
        top.add_color("background", "background", -5)
        #top.add_style("padding-top: 10px")

        title = "Sample Chart"
        if title:
            date = "@FORMAT(@STRING($TODAY),'Dec 31, 1999')"
            date = Search.eval(date, single=True)

            title_wdg = DivWdg()
            top.add(title_wdg)
            title_wdg.add(title)
            title_wdg.add(" [%s]" % date)
            title_wdg.add_style("font-size: 1.1em")
            title_wdg.add_color("background", "background3")
            title_wdg.add_color("color", "color3")
            title_wdg.add_style("padding: 10px")
            title_wdg.add_style("font-weight: bold")
            title_wdg.add_style("text-align: center")



        #labels = ['chr001', 'chr002', 'chr003', 'chr004', 'prop001', 'prop002', 'cow001']
        labels = ['week 1', 'week 2', 'week 3', 'week 4', 'week 5', 'week 6', 'week 7', 'week 8']
        values = [1,2,4,5,6,7,8]

        width = self.kwargs.get("width")
        if not width:
            width = '800px'
        height = self.kwargs.get("height")
        if not height:
            height = '500px'


        if width:
            top.add_style("width", width)
        if height:
            top.add_style("height", height)


        chart_div = DivWdg()
        top.add(chart_div)
        chart_div.add_style("text-align: center")

        chart = ChartJsWdg(
            height=height,
            width=width,
            chart_type='bar',
            labels=labels
        )
        chart_div.add(chart)

        data = ChartData(
            label="First",
            color="rgba(255, 0, 0, 1.0)",
            data=[1.2, 5.5, 7.5, 14.3, 10.2, 1.1, 3.3],
            x_data=[1,3,3.1,3.2,3.3,3.4,3.5]
        )
        chart.add(data)

        data = ChartData(
            label="Second",
            color="rgba(0, 255, 0, 0.5)",
            data=[1.5, 4.3, 8.4, 6.2, 8.4, 2.2],
        )
        chart.add(data)


        data = ChartData(
            label="Third",
            color="rgba(0, 0, 255, 0.7)",
            data=[1.1, 3.5, 2.2, 6.6, 1.3, 9.4],
        )
        chart.add(data)


        data = [14.3, 17, 15.5, -3, 17, 16.8, 11.4]
        data = ChartData(
            label="Fourth",
            data=data,
            color="rgba(0, 0, 255, 0.3)"
        )
        chart.add(data)


        data = {
            "m": -2.5,
            "b": 17.3
        }
        data = ChartData(chart_type='function', data=data, color="rgba(128, 128, 128, 0.6)")
        chart.add(data)


        data = {
            "m": -3,
            "b": 13.3
        }
        data = ChartData(chart_type='function', data=data, color="rgba(128, 128, 128, 0.6)")
        chart.add(data)


        data = {
            "a": -2,
            "b": 1.3,
            "c": 10 
        }
        data = ChartData(chart_type='polynomial', data=data, color="rgba(128, 128, 128, 0.6)")
        chart.add(data)

        return top





class ChartJsWdg(BaseRefreshWdg):

    ARGS_KEYS = {
    'height': 'Height of the canvas',
    'width': 'Width of the canvas',
    }

    def init(self):
        top = self.top
        #top.add_gradient("background", "background", -5)

    def add_style(self, name, value):
        self.top.add_style(name, value)

    def add_color(self, name, value):
        self.top.add_color(name, value)

    def add_gradient(self, name, value, offset=0, gradient=-10):
        self.top.add_gradient(name, value, offset, gradient)


    def get_display(self):

        top = self.top
        top.add_style("position: relative")

        title = self.kwargs.get("title") or ""

        labels = self.kwargs.get("labels")
        if not labels:
            labels = []
        label_values = self.kwargs.get("label_values")

        width = self.kwargs.get("width")
        height = self.kwargs.get("height")

        default_chart_type = self.kwargs.get("chart_type")
        if not default_chart_type:
            default_chart_type = 'bar'

        canvas = Canvas()
        top.add(canvas)
        canvas.add("Your web-browser does not support the HTML 5 canvas element.")





        chart_type = self.kwargs.get("chart_type") or "bar"
        #chart_type = "horizontalBar"



        datasets = []
        for widget in self.widgets:
            # count the number of bar charts
            widget_chart_type = widget.get_chart_type()
            if not widget_chart_type:
                widget_chart_type = default_chart_type
                widget.set_chart_type(widget_chart_type)


            data = widget.get_data()

            color = widget.get_color()

            label = widget.get_label()

            dataset = {
                'type': widget_chart_type,
                'label': label,
                'data': data,
                'backgroundColor': color
            }


            if chart_type in ["pie", "doughnut"]:
                dataset['borderWidth'] = 2
            else:
                dataset['borderWidth'] = 1
                dataset['borderColor'] = '#666'

            datasets.append(dataset)


        if chart_type == "horizontalBar":
            for item in datasets:
                if chart_type == "horizontalBar":
                    item['type'] = 'horizontalBar'

        elif chart_type == "pie":
            for item in datasets:
                if chart_type == "pie":
                    item['type'] = 'pie'
        elif chart_type == "doughtnut":
            for item in datasets:
                if chart_type == "doughtnut":
                    item['type'] = 'doughtnut'


        options = {}


        if chart_type in ["stacked", "stacked_horizontal"]:

            options["scales"] = {
                "xAxes": [{
                    "stacked": True,
                }],
                "yAxes": [{
                    "stacked": True
                }]
            }
            for item in datasets:
                if chart_type == "stacked":
                    item['type'] = 'bar'
                elif chart_type == "stacked_horizontal":
                    item['type'] = 'horizontalBar'


            if chart_type == "stacked":
                chart_type = "bar"
            else:
                chart_type = "horizontalBar"

        elif chart_type in ["line"]:

            options["fill"] = False,
            options["scales"] = {
                "xAxes": [{
                    "type": 'time',
                    "display": True,
                    "scaleLabel": {
                        "display": True,
                        "labelString": "Date",
                    }
                }],
            }


        # initialize the canvas
        canvas.add_behavior( {
            'type': 'load',
            'chart_type': chart_type,
            'title': title,
            'options': options,
            'datasets': datasets,
            'labels': labels,
            'cbjs_action': '''
var labels = bvr.labels;
var data = bvr.data;

var datasets = bvr.datasets;

var chart_type = bvr.chart_type;

if (chart_type == "pie" || chart_type == "doughnut") {
    // FIXME: make this more automatic for pie charts
    datasets[0].backgroundColor = [
        window.chartColors.red,
        window.chartColors.orange,
        window.chartColors.yellow,
        window.chartColors.green,
        window.chartColors.blue,
        window.chartColors.red,
        window.chartColors.orange,
        window.chartColors.yellow,
        window.chartColors.green,
        window.chartColors.blue,
        window.chartColors.red,
        window.chartColors.orange,
        window.chartColors.yellow,
        window.chartColors.green,
        window.chartColors.blue,
        window.chartColors.red,
        window.chartColors.orange,
        window.chartColors.yellow,
        window.chartColors.green,
        window.chartColors.blue,
    ]
}





var color = Chart.helpers.color;
var barChartData = {
    labels: labels,
    datasets: datasets,
};


var title = bvr.title || ""

var options = bvr.options;

options.responsive = true;

options.legend = {
    position: 'top',
};


if (title) {
    options.title = {
        display: true,
        text: title
    }
}


options.plugins = {
    datalabels: {
        anchor: 'end',
        align: 'top',
        offset: -5
    }
}


var datasets = barChartData['datasets'][0];

if (!datasets['label']) options['legend']['display'] = false;

if (!datasets.data.some(v => v < 0)) options['scales'] = { yAxes: [{ticks: { beginAtZero:true }}]};

var ctx = bvr.src_el.getContext('2d');

window.myBar = new Chart(ctx, {
    type: chart_type,
    data: barChartData,
    options: options,
});

            '''
        } )


        return top


