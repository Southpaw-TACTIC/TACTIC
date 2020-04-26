###########################################################
#
# Copyright (c) 2005-2010, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#

# 



__all__ = ['TaskStatusCountReportWdg']

from pyasm.common import Date, Common, Container, TacticException
from pyasm.search import Search, SearchKey, SearchType
from pyasm.biz import ExpressionParser, Pipeline, Project
from pyasm.web import Table, DivWdg, SpanWdg, WebContainer
from pyasm.widget import IconWdg, IconButtonWdg, TextWdg
from tactic.ui.common import BaseRefreshWdg, BaseTableElementWdg

class TaskStatusCountReportWdg(BaseRefreshWdg):

    def get_display(self):

        self.search_type = self.kwargs.get("search_type")
        if not self.search_type:
            self.search_type = 'sthpw/task'

        self.column = self.kwargs.get("column")
        if not self.column:
            self.column = 'status'


        self.project_code = self.kwargs.get("project_code")
        if not self.project_code:
            self.project_code = Project.get_project_code()

        self.bar_width = self.kwargs.get("bar_width")
        if not self.bar_width:
            self.bar_width = 200


        values = self.kwargs.get("values")
        if values:
            values = values.split("|")

        else:
            pipeline_code = self.kwargs.get("pipeline_code")
            if pipeline_code:
                pipeline = Pipeline.get_by_code(pipeline_code)
                values = pipeline.get_process_names()
            else:    
                search = Search(self.search_type)
                search.add_filter("project_code", self.project_code)
                search.add_column(self.column, distinct=True)
                xx = search.get_sobjects()
                values = [x.get_value(self.column) for x in xx]


        search = Search(self.search_type)
        search.add_filter("project_code", self.project_code)
        search.add_filters(self.column, values)
        total = search.get_count()




        colors = ['#900', '#090', '#009', '#990', '#099', '#909', '#900', '#090', '#009', '#990']
        while len(values) > len(colors):
            colors.extend(colors)

        top = DivWdg()
        top.add_color("background", "background")

        date = "@FORMAT(@STRING($TODAY),'Dec 31, 1999')"
        date = Search.eval(date, single=True)
        title = "Tasks Status Chart"

        title_wdg = DivWdg()
        top.add(title_wdg)
        title_wdg.add(title)
        title_wdg.add(" [%s]" % date)
        title_wdg.add_style("font-size: 14")
        title_wdg.add_color("background", "background3")
        title_wdg.add_color("color", "color3")
        title_wdg.add_style("padding: 10px")
        title_wdg.add_style("font-weight: bold")
        title_wdg.add_style("text-align: center")


        inner = DivWdg()
        top.add(inner)
        inner.center()
        inner.add_style("width: 500px")
        inner.add_style("padding: 30px")


        for i,status in enumerate(values):

            if not status:
                continue

            count = self.get_count(status)
            div = self.get_div(status, count, total, colors[i])
            inner.add( div.get_buffer_display() )
            inner.add( "<br clear='all'/>")

        inner.add("<hr/>")

        div = self.get_div("Total", total, total, "gray")
        inner.add( div.get_buffer_display() )
        inner.add("<br clear='all'/>")


        return top


    def get_count(self, status):
        search = Search(self.search_type)
        search.add_filter("project_code", self.project_code)
        search.add_filter(self.column, status)
        count = search.get_count()
        return count


    def get_div(self, name, value, total, color):
        if total:
            width = int(self.bar_width) * float(value) / float(total)
        else:
            width = 0

        if width < 1:
            width = 1
        div = DivWdg()
        div.add_style("margin: 5px")

        title_div = DivWdg()
        title_div.add(name)
        title_div.add_style("float: left")
        title_div.add_style("width: 150px")
        div.add(title_div)

        bar_div = DivWdg()
        bar_div.add(" ")
        bar_div.add_style("float: left")
        bar_div.add_style("height: 20px")
        bar_div.add_style("width: %spx" % width)
        bar_div.add_style("background-color: %s" % color)
        div.add(bar_div)

        value_div = DivWdg()
        value_div.add_style("float: left")
        value_div.add_style("margin-left: 5px")
        value_div.add('%s' % value)
        div.add(value_div)

        return div



__all__.append("ValueBarReportWdg")
class ValueBarReportWdg(BaseTableElementWdg):
    '''class to display a series of values as bar graphs'''

    ARGS_KEYS = {
        'elements': 'A list of elements to display on the graph'
    }


    def preprocess(self):
        self.elements = self.kwargs.get("elements")
        if self.elements:
            self.elements = self.elements.split('|')
        else:
            self.elements = []

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




    def get_data(self, sobject):

        values = []
        labels = []

        if not self.config:
            return values, labels



        for element in self.elements:
            options = self.config.get_display_options(element)
            attrs = self.config.get_element_attributes(element)


            label = attrs.get('title')
            if not label:
                label = Common.get_display_title(element)
            labels.append(label)



            expression = options.get("expression")
            if not expression:
                value = 0
            else:
                value = Search.eval(expression, sobject, single=True)

            values.append(value)        


        return values, labels



    def get_display(self):

        
        sobject = self.get_current_sobject()
        values, labels = self.get_data(sobject)



        # extend the colors if necessary
        colors = ['#339','#933','#393','#993','#939','#399']
        if len(values) > len(colors):
            colors.extend(colors)

        total = 0;

        top = DivWdg()

        for i, value in enumerate( values ):
            # get the color and label
            label = labels[i]
            color = colors[i]

            total += value

            title = "<div style='width: 150px; float: left'>%s</div>" % label
            top.add(title)
            div = "<div style='background-color: %s; width: %spx; min-width: 1px; float: left; margin-top: 3px'>&nbsp;</div>" % (color, value*5)
            top.add(div)
            top.add("&nbsp;%s<br clear='all'/>" % value)

            total += value

        top.add(' %s' % total)

        return top







