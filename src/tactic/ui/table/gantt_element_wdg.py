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

__all__ = [ 'GanttElementWdg', 'GanttCbk', 'GanttLegendWdg', 'GanttLegendCbk' ]

import re, time, types

from tactic.ui.common import BaseTableElementWdg, BaseRefreshWdg

from pyasm.common import Date, jsonloads, jsondumps, TacticException
from pyasm.command import DatabaseAction, Command
from pyasm.search import Search, SearchKey, SearchType
from pyasm.web import Widget, DivWdg, SpanWdg, HtmlElement, WebContainer, Table
from pyasm.widget import HiddenWdg, TextWdg, IconWdg
from pyasm.biz import ExpressionParser

from tactic.ui.widget import IconButtonWdg

import datetime
from dateutil import rrule
from dateutil import parser

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


class GanttElementWdg(BaseTableElementWdg):

    def init(my):
        my.divider_pos = []
        my.divider_html = None

        my.start_date = None
        my.end_date = None
        my.has_start_date = True
        my.hide_bar = False

        my.is_preprocessed = False

        my.legend_dialog_id = 0


    ARGS_KEYS = {
    'show_title' : {
        'description': 'true|false Determines whether the show title can be seen',
        'type': 'CheckboxWdg',
        'order': 0,
        'category': 'Display'
    },
    'options': {
        'type': 'TextAreaWdg',
        'description': 'A list of options for the various gantt bars',
        'order': 3,
        'category': 'Config'
    },
    'range_start_date': {
        'type': 'CalendarInputWdg',
        'description': 'The start date of the gantt widget',
        'order': 2,
        'category': 'Display'
    },
    'range_end_date': {
        'type': 'CalendarInputWdg',
        'description': 'The end date of the gantt widget',
        'order': 3,
        'category': 'Display'
    },
    'overlap': {
        'type': 'SelectWdg',
        'description': 'determines whether or not to overlap date ranges',
        'order': 5,
        'values': 'true|false',
        'category': 'Display',
    },
    'date_mode': {
        'type': 'SelectWdg',
        'description': 'The display modes for the dates: visible means that the dates are always visible, while hover means that the dates will only appear when hovering over the cell',
        'values': 'visible|hover|none',
        'order': 1,
        'category': 'Display'
    },
    'show_milestones': {
        'type': 'SelectWdg',
        'description': 'Determines which milestones to show for each task',
        'values': 'task|project',
        'order': 3,
        'category': 'Display'
    },
    'year_display': {
        'type': 'SelectWdg',
        'description': 'Determines whether or not to show the year',
        'values': 'none|default',
        'order': 4,
        'category': 'Display'
    },
    'week_display': {
        'type': 'SelectWdg',
        'description': 'Determines whether or not to show the week',
        'values': 'none|default',
        'order': 5,
        'category': 'Display'
    },
    'week_start': {
        'type': 'SelectWdg',
        'description': 'Day the week starts',
        'labels': 'MO|TU|WE|TH|FR|SA|SU',
        'values': '0|1|2|3|4|5|6',
        'order': 6,
        'category': 'Display'
    },
    'bar_height': {
        'type': 'SelectWdg',
        'description': 'Determines the height of the bars',
        'values': '6|12|18|24',
        'order': 7,
        'category': 'Display'
    },
    'color_mode': {
        'type': 'SelectWdg',
        'description': 'Special color mode for display of tasks',
        'values': 'status|process',
        'order': 8,
        'category': 'Display'
    },
    }

    def is_editable(cls):
        '''Determines whether this element is editable'''
        return False
    is_editable = classmethod(is_editable)


    def can_async_load(cls):
        return False
    can_async_load = classmethod(can_async_load)


    def get_colors(my, sobject, mode):
        # TODO: optimise
        if mode == 'status':
            pipeline_code = sobject.get_value("pipeline_code")
        else:
            parent = sobject.get_parent()
            pipeline_code = parent.get_value("pipeline_code")

        # get status
        from pyasm.biz import Pipeline

        colors = {}

        # fill in colors from default
        if mode == 'status':
            pipeline = Pipeline.get_by_code('task')
            process_names = pipeline.get_process_names()
            for process_name in process_names:
                #attrs = pipeline.get_process_attrs(process_name)
                #color = attrs.get("color")
                color = pipeline.get_process(process_name).get_color()
                if color:
                    colors[process_name] = color


        pipeline = Pipeline.get_by_code(pipeline_code)
        if pipeline:
            process_names = pipeline.get_process_names()
            for process_name in process_names:
                #attrs = pipeline.get_process_attrs(process_name)
                #color = attrs.get("color")
                color = pipeline.get_process(process_name).get_color()
                if color:
                    colors[process_name] = color

        return colors



    def preprocess(my):

        # how to specify in the config?
        '''
        <options>[
        {
            'start_date_col':   'bid_start_date',
            'end_date_col':     'bid_end_date',
            'color':            '#888',
            'edit':             'true'
        },
        {
            'start_date_col':   'actual_start_date',
            'end_date_col':     'actual_end_date',
            'color':            '#F0C956',
            'edit':             'true'
        },
        {
            'start_date_expr':  '@MIN(sthpw/task.bid_start_date)',
            'end_date_expr':    '@MAX(sthpw/task.bid_end_date)'
        }
        ]</options>

        '''

        my.options = my.get_option('options')
        if my.options:
            my.property_list = jsonloads(my.options)
        else: 
            my.property_list = [{
                'start_date_expr':   '@GET(sthpw/task.bid_start_date)',
                'end_date_expr':     '@GET(sthpw/task.bid_end_date)',
                'color':            '#888',
                'edit':             'true'
            }]
            #property_list.append( {
            #    'start_date_col':   'actual_start_date',
            #    'end_date_col':     'actual_end_date',
            #    'color':            '#F0C956',
            #    'edit':             'true'
            #} )


        print "options: ", my.options

        expr_parser = ExpressionParser()

        my.end_sobj_dates = []
        my.start_sobj_dates = []

        # fill in keys for all sobjects
        my.range_data = {}
        for sobject in my.sobjects:
            search_key = sobject.get_search_key()
            my.range_data[search_key] = []

        min_date = None
        max_date = None
        for index, properties in enumerate(my.property_list):

            sobject_expr = properties.get("sobject_expr")
            color_mode = my.kwargs.get("color_mode")

            start_date_col = properties.get("start_date_col")
            my.hide_bar = properties.get("hide_empty_bar") == 'true'
            if start_date_col:
                my.start_date_expr = '@GET(.%s)' % start_date_col
            else:
                my.start_date_expr = properties.get("start_date_expr")
                if not my.start_date_expr:
                    my.start_date_expr = '@GET(sthpw/task.bid_start_date)'
                    # provide a default so that the color for default task_schedule column works
                    if not sobject_expr:
                        sobject_expr = '@SOBJECT(sthpw/task)'
                        my.start_date_expr = '@GET(.bid_start_date)'
                
            end_date_col = properties.get("end_date_col")
            if end_date_col:
                my.end_date_expr = '@GET(.%s)' % end_date_col
            else:
                my.end_date_expr = properties.get("end_date_expr")
                if not my.end_date_expr:
                    my.end_date_expr = '@GET(sthpw/task.bid_end_date)'
                    # provide a default so that the color for default task_schedule column works
                    if not sobject_expr:
                        sobject_expr = '@SOBJECT(sthpw/task)'
                        my.end_date_expr = '@GET(.bid_end_date)'

            if sobject_expr:
                # the current parser doesn't support 2 separate calls due to the use of my.related_types. 
                # Just use one single call 
                gantt_data = expr_parser.eval(sobject_expr, my.sobjects, dictionary=True)
                #gantt_data = expr_parser.get_flat_cache(filter_leaf=True)   

                
            else:
                gantt_data = {}

            # get the start and end dates
            start_sobj_dates = []
            end_sobj_dates = []

            # go through each row sobject
            for sobject in my.sobjects:

                if sobject_expr:
                    search_key = sobject.get_search_key()
                    gantt_sobjects = gantt_data.get(search_key)
                    if not gantt_sobjects:
                        gantt_sobjects = []

                    xstart_values = expr_parser.eval(my.start_date_expr, gantt_sobjects, dictionary=True)
                    xend_values = expr_parser.eval(my.end_date_expr, gantt_sobjects, dictionary=True)

                    start_values = []
                    end_values = []
                    colors = []
                    for x in gantt_sobjects:
                        search_key = x.get_search_key()
                        start_values.extend( xstart_values.get(search_key) )
                        end_values.extend( xend_values.get(search_key) )

                        if color_mode:
                            value = x.get_value(color_mode)
                            xxcolors = my.get_colors(x, color_mode)
                            colors.append(xxcolors.get(value))

                else:
                    start_values = expr_parser.eval(my.start_date_expr, sobject, list=True)
                    end_values = expr_parser.eval(my.end_date_expr, sobject, list=True)
                    # getting the attribute directly from this sobject
                    colors = []
                    # only support getting the current column type of expression inferred above
                    # but not the user-provided type
                    if color_mode and start_date_col:
                        color_value = sobject.get_value(color_mode)
                        color_dict = my.get_colors(sobject, color_mode)
                        colors.append(color_dict.get(color_value))

                # handle condition where there are no results
                if not start_values:
                    start_values = [None]

                if not end_values:
                    end_values = [None]

                if not colors:
                    colors = [None for x in start_values]


                # NO longer used
                start_sobj_dates.append(start_values[0])
                end_sobj_dates.append(end_values[0])
                range_data = []

                for start_value, end_value, color in zip(start_values, end_values, colors):
                    search_key = sobject.get_search_key()
                    data = {}
                    data['start_date'] = start_value
                    data['end_date'] = end_value
                    data['color'] = color
                    range_data.append(data) 
                    if start_value and (not min_date or start_value < min_date):
                        min_date = start_value
                    if end_value and (not max_date or end_value > max_date):
                        max_date = end_value

                my.range_data.get(search_key).append(range_data)




            my.start_sobj_dates.append( start_sobj_dates )
            my.end_sobj_dates.append( end_sobj_dates )



        # get data from refresh
        web = WebContainer.get_web()
        gantt_data = web.get_form_value('gantt_data')

        # new way of passing in web_data
        if not gantt_data:
            # fast table 
            web_data = web.get_form_value('web_data')
            if web_data:
                gantt_data = web_data


        # override
        start_date_option = my.get_option("range_start_date")
        end_date_option = my.get_option("range_end_date")


        my.start_date = None
        my.end_date = None


        my.total_width = 1000
        my.offset_width = -300 
        my.visible_width = 500

        if my.kwargs.get("test"):
            test_width = my.kwargs.get("test")
            my.total_width = test_width
            my.offset_width = 0
            my.visible_width = test_width

        if gantt_data:
            gantt_data = jsonloads(gantt_data)
            #print "gantt_data: ", gantt_data
            # new way where the web_data is a list of different data for different widgets
            if isinstance(gantt_data, list):
                gantt_data = gantt_data[0]
                gantt_data = gantt_data.get('gantt_data')
                if gantt_data:
                    gantt_data = jsonloads(gantt_data)
                else:
                    gantt_data = None
        
        if gantt_data:

            #gantt_data = gantt_data.get('__data__')
            my.total_width = float(gantt_data.get('_width'))
            my.offset_width = float(gantt_data.get('_offset'))

            if gantt_data.get('_range_start_date'):
                my.start_date = parser.parse( gantt_data.get('_range_start_date') )
            if gantt_data.get('_range_end_date'):
                my.end_date = parser.parse( gantt_data.get('_range_end_date') )

        elif start_date_option and end_date_option:
            if start_date_option.startswith("{"):
                start_date_option = Search.eval(start_date_option)
            if end_date_option.startswith("{"):
                end_date_option = Search.eval(end_date_option)
            try:
                my.start_date = parser.parse( start_date_option )
                my.end_date = parser.parse( end_date_option )

                #buffer = 45
                buffer = 0

                # buffer start date and end date
                my.start_date = my.start_date - datetime.timedelta(days=buffer)
                my.end_date = my.end_date + datetime.timedelta(days=buffer)
            except:
                print "ERROR: could not parse either [%s] or [%s]" % (start_date_option, end_date_option)

        if not my.start_date or not my.end_date:
            # find the min and max
            if min_date:
                my.start_date = min_date
            if max_date:
                my.end_date = max_date

            if not my.start_date or my.start_date == 'None':
                my.start_date = datetime.datetime.now()
            if not my.end_date or my.end_date == 'None':
                my.end_date = datetime.datetime.now()


            diff = my.end_date - my.start_date
            days = diff.days
            if days == 0:
                buffer = 45
            else:
                buffer= int(days*1.2)


            # buffer start date and end date
            my.start_date = my.start_date - datetime.timedelta(days=buffer)
            my.end_date = my.end_date + datetime.timedelta(days=buffer)



        my.total_days = (my.end_date - my.start_date).days
        my.percent_width = 100 
        if my.total_days:
            my.percent_per_day = float(my.percent_width) / float(my.total_days)
        else:
            my.percent_per_day = 0

        my.is_preprocessed = True



        # handle the color
        my.color_results = []
        color_parser = ExpressionParser()
        for index, properties in enumerate(my.property_list):
            color_expr = properties.get('color')
            color_parser.eval(color_expr, my.sobjects)

            results = color_parser.get_result_by_sobject_dict()
            my.color_results.append(results)




    def handle_th(my, th, cell_index=None):
        th.add_style("width: %s" % my.visible_width)
        th.add_class("spt_table_scale")
        # this is for general classification, we need spt_input_type = gantt still
        th.add_attr('spt_input_type', 'inline')

        th.add_behavior( {
            'type': 'load',
            'width': my.total_width,
            'offset': my.offset_width,
            'cbjs_action': get_onload_js()
        } )


    def handle_td(my, td):

        # info sent over to drag callbacks
        info = {}
        info['percent_per_day'] = my.percent_per_day
       
        td.add_behavior( {
            "type": 'drag',
            "mouse_btn": 'LMB',
            "drag_el": '@',
            "cb_set_prefix": 'spt.gantt.drag_scroll',
            "mode": 'start',
            "info": info,
        } )

        td.add_behavior( {
            "type": 'drag',
            "mouse_btn": 'LMB',
            "modkeys": 'SHIFT',
            "drag_el": '@',
            "cb_set_prefix": 'spt.gantt.drag_scale',
            "mode": 'start',
            "info": info,
        } )



        td.add_attr('spt_input_type', 'gantt')
        td.add_class("spt_input_inline")

        
        if my.kwargs.get("date_mode") == 'hover':
            td.add_behavior( {
                'type': 'hover',
                'cbjs_action_over': '''
                var starts = bvr.src_el.getElements(".spt_start_date");
                var ends = bvr.src_el.getElements(".spt_end_date");
                for (var i = 0; i < starts.length; i++) {
                    spt.show(starts[i]);
                    spt.show(ends[i]);
                }
                ''',
                'cbjs_action_out': '''
                var starts = bvr.src_el.getElements(".spt_start_date");
                var ends = bvr.src_el.getElements(".spt_end_date");
                for (var i = 0; i < starts.length; i++) {
                    spt.hide(starts[i]);
                    spt.hide(ends[i]);
                }
                ''' 
            } )



    def get_title(my):
        if not my.is_preprocessed:
            my.preprocess()

        if my.get_option("show_title") == 'false':
            return DivWdg()

        top = DivWdg()
        top.add_class("spt_gantt_top")
        top.add_attr("spt_percent_per_day", my.percent_per_day)
        top.add_style("margin-left: -3px")
        top.add_style("margin-right: -6px")

        # left arrow
        left_div = DivWdg()
        #top.add(left_div)
        left_div.add("&lt;<br/>")
        left_div.add_style("float: left")
        left_div.add_behavior( {
            'type': 'click_up',
            'percent_per_day': my.percent_per_day,
            'cbjs_action': '''
            // get the start and end date of the current range
            var top = bvr.src_el.getParent(".spt_gantt_top");
            start_date = "2012-08-22"
            end_date = "2012-11-26"
            var el = top.getElement(".spt_gantt_day");
            while (el.hasChildNodes()) {
                el.removeChild(el.lastChild);
            }
            spt.gantt.fill_header_days(el, start_date, end_date, bvr.percent_per_day);

            var el = top.getElement(".spt_gantt_month");
            while (el.hasChildNodes()) {
                el.removeChild(el.lastChild);
            }
            spt.gantt.fill_header_months(el, start_date, end_date, bvr.percent_per_day);

            '''
        } )
        

        # Disabling for now
        #from tactic.ui.widget import CalendarWdg
        #calendar = CalendarWdg()
        ##calendar.add_style("display: none")
        #calendar.add_style("position: absolute")
        #nav.add(calendar)


        top.add(my.get_legend_dialog())



        dates_div = DivWdg()
        dates_div.add_class("spt_table_scale")
        dates_div.add_style("width: %s" % my.visible_width)

        dates_div.add_style("overflow: hidden")
        top.add(dates_div)

        inner_div = DivWdg()
        inner_div.add_style("width: %s" % my.total_width)
        inner_div.add_class("spt_gantt_scroll")
        inner_div.add_style("margin-left: %s" % my.offset_width)
        dates_div.add(inner_div)


        # find the pixels per day
        pixel_per_day = my.percent_per_day * my.total_width / 100;


        year_display = my.kwargs.get("year_display")
        if not year_display:
            year_display = 'none'
        if year_display != 'none':
            inner_div.add( my.get_year_wdg(my.start_date, my.end_date) )


        month_wdg = my.get_month_wdg(my.start_date, my.end_date)
        inner_div.add( month_wdg )
        inner_div.add( "<br clear=all'/>")

        week_display = my.kwargs.get("week_display")
        if not week_display:
            week_display = 'none'
        if week_display != 'none':
            week_wdg = my.get_week_wdg(my.start_date, my.end_date)
            inner_div.add( week_wdg )
            if pixel_per_day < 1.5:
                week_wdg.add_style("display", "none")


        #wday_wdg = my.get_wday_wdg(my.start_date, my.end_date)
        #inner_div.add( wday_wdg )
        #day_wdg = my.get_day_wdg(my.start_date, my.end_date)
        #inner_div.add( day_wdg )

        # only put in hour if the range is small enough
        #hour_wdg = my.get_hour_wdg(my.start_date, my.end_date)
        #inner_div.add( hour_wdg )
        """
        if pixel_per_day < 15:
            day_wdg.add_style("display", "none")
        else:
            #year_wdg.add_style("display", "none")
            pass
        if pixel_per_day > 1.5:
            wday_wdg.add_style("display", "none")
        """

        day_wdg = DivWdg()
        inner_div.add( day_wdg )
        day_wdg.add_class("spt_gantt_day");
        day_wdg.add_class("spt_gantt_scalable")

        if pixel_per_day < 10:
            #wday_wdg.add_style("display", "none")
            day_wdg.add_style("display", "none")
            #pass


        # replace day widget with javascript generated one
        color1 = inner_div.get_color("background", -15)
        color2 = inner_div.get_color("background", -30)
        day_wdg.add_attr("spt_color1", color1)
        day_wdg.add_attr("spt_color2", color2)
        day_wdg.add_behavior( {
        'type': 'load',
        'start_date': my.start_date.strftime("%Y-%m-%d"),
        'end_date': my.end_date.strftime("%Y-%m-%d"),
        'percent_per_day': my.percent_per_day,
        'color1': color1,
        'color2': color2,
        'cbjs_action': '''
        var el = bvr.src_el;
        var start_date = bvr.start_date;
        var end_date = bvr.end_date;
        var percent_per_day = bvr.percent_per_day;

        spt.gantt.fill_header_days(el, start_date, end_date, percent_per_day);

        '''
        } )

 

        return top


    def get_legend_dialog(my):

        # selection for color
        from tactic.ui.container import DialogWdg
        legend_dialog = DialogWdg(z_index=1000, show_pointer=False, display="false")
        my.legend_dialog_id = legend_dialog.get_unique_id()
        legend_dialog.add_title("Gantt Legend")
        legend_dialog.add_class("spt_color_top")
        legend_dialog.add_class("SPT_PUW")

        content = DivWdg()
        legend_dialog.add(content)
        content.add_class("spt_color_content")

        #legend_wdg = GanttLegendWdg()
        #legend_dialog.add(legend_wdg)

        return legend_dialog



    def get_year_wdg(my, start_date, end_date):

        dates = list(rrule.rrule(rrule.YEARLY, byyearday=1, dtstart=start_date, until=end_date))
        if not dates or dates[0] != start_date:
            dates.insert(0, start_date)
        if not dates or dates[-1] != end_date:
            dates.append(end_date)
           
        return my.get_dates_display(dates, "date.year", is_scalable=True, name='year')


    def get_month_wdg(my, start_date, end_date):

        dates = list(rrule.rrule(rrule.MONTHLY, bymonthday=1, dtstart=start_date, until=end_date))

        if not dates or dates[0] != start_date:
            dates.insert(0, start_date)
        if not dates or dates[-1] != end_date:
            dates.append(end_date)

        return my.get_dates_display(dates, "MONTHS[date.month-1]", is_scalable=True, name='month')



    def get_week_wdg(my, start_date, end_date):

        dates = list(rrule.rrule(rrule.WEEKLY, byweekday=0, dtstart=start_date, until=end_date))
        if not dates or dates[0] != start_date:
            dates.insert(0, start_date)
        if not dates or dates[-1] != end_date:
            dates.append(end_date)
           
        return my.get_dates_display(dates, "date.strftime('Wk.%W')", record_divider_pos=True,name='week', is_scalable=True)


    def get_day_wdg(my, start_date, end_date):

        dates = list(rrule.rrule(rrule.DAILY, dtstart=start_date, until=end_date))

        if not dates or dates[0] != start_date:
            dates.insert(0, start_date)
        if not dates or dates[-1] != end_date:
            dates.append(end_date)

        return my.get_dates_display(dates, "date.strftime('%d')",name='day')


    def get_wday_wdg(my, start_date, end_date):

        dates = list(rrule.rrule(rrule.DAILY, dtstart=start_date, until=end_date))

        if not dates or dates[0] != start_date:
            dates.insert(0, start_date)
        if not dates or dates[-1] != end_date:
            dates.append(end_date)

        return my.get_dates_display(dates, "date.strftime('%a')",name='wday')


    def get_hour_wdg(my, start_date, end_date):

        dates = list(rrule.rrule(rrule.HOURLY, dtstart=start_date, until=end_date))
        if not dates or dates[0] != start_date:
            dates.insert(0, start_date)
        if not dates or dates[-1] != end_date:
            dates.append(end_date)

        return my.get_dates_display(dates, "date.strftime('%H')",name='hour')




    def get_dates_display(my, dates, date_expr, record_divider_pos=False,name=None, is_scalable=False):
        top = DivWdg()
        if name:
            top.add_class("spt_gantt_%s" % name)
        top.add_style("margin: 0px")
        top.add_style("padding: 0px")
        top.add_style("text-align: center")
        top.add_class("spt_gantt_scalable")
        if is_scalable:
            top.add_class("hand")


        total_width = 0
        divider_widths = []

        # draw the intervals
        color1 = top.get_color("background", -15)
        color2 = top.get_color("background", -30)
        color = [color1, color2]
        count = 0
        total = 0
        for i, date in enumerate(dates[:-1]):
            date2 = dates[i+1]
            diff = date2 - date

            width = (diff.days + float(diff.seconds)/3600/24) * my.percent_per_day
            if total + width > 100:
                width = 100 - total
            total += width
            divider_widths.append(width)

            display = eval(date_expr)
          
            div = DivWdg()
            div.add_style("border-width: 0 0 1 0")
            div.add_style("border-style: solid")
            div.add_style("border-color: %s" % div.get_color("border") )
            top.add(div)
            div.add_class("spt_gantt_date_range")
            div.add_style("width: %s%%" % width)
            div.add_style("background: %s" % color[count % 2])
            div.add_style("font-size: 10px")
            #div.add_style("overflow: hidden")
            div.add_style("float: left")

            if not is_scalable:
                total_width += width
                count += 1
                div.add(display)
                continue

            div.set_attr("title", date.strftime("%b %Y"))


            # unscaled pixels
            pixels = (width/100) * my.total_width

            # to fit in the whole visible range, we need find the scale relative
            # to the visible width
            if pixels:
                scale = my.visible_width / pixels
            else:
                scale = 1

            # now that we have the scale, we have to push it back based on the
            # current total width
            click_offset = -(total_width/100*my.total_width) * scale
            click_width = scale * my.total_width


            # find the width and offset to
            div.add_attr("spt_gantt_width", click_width)
            div.add_attr("spt_gantt_offset", click_offset)

            # handle the contents of the display
            title_div = DivWdg(display)

            #title_div.add_style("padding-left: %spx")
            div.add(title_div)

            #div.add_event("onmouseover", "$(this).setStyle('border','dashed 1px blue')")
            #div.add_event("onmouseout", "$(this).setStyle('border-size','0px')")
            div.add_behavior( {
                'type': 'click_up',
                "cbjs_action": 'spt.gantt.date_clicked_cbk(evt, bvr)'
            } )

            total_width += width
            count += 1

        if record_divider_pos:
            my.divider_pos = divider_widths

        if not count:
            avg_width = 0
        else:
            avg_width = float(total_width) / count

        #if avg_width < 2:
        #    top.add_style("display: none")

        return top



    def calculate_widths(my, date1, date2):

        diff1 = (date1 - my.start_date)
        width1 = float(diff1.days) * my.percent_per_day
        if width1 < 0:
            width1 = 0
        
        one_day = datetime.timedelta(days=1)
        diff2 = (date2 - my.start_date + one_day )
        width2 = float(diff2.days) * my.percent_per_day
        if width2 < 0:
            width2 = 0
        return width1, width2




    def handle_layout_behavior(my, layout):
        pass

        """
        if editable:
            behavior = {
            "type": 'drag',
            "mouse_btn": 'LMB',
            "drag_el": '@',
            "cb_set_prefix": 'spt.gantt.drag2',
            "mode": 'shift',
            "info": info,
            }
            duration.add_behavior(behavior)


            behavior = {
            "type": 'drag',
            "mouse_btn": 'LMB',
            "modkeys": 'SHIFT',
            "drag_el": '@',
            "cb_set_prefix": 'spt.gantt.drag2',
            "mode": 'both',
            "info": info,
            }
            duration.add_behavior(behavior)


        else:
            behavior = {
                "type": 'click_up',
                "cbjs_action": "alert('Not editable in this view')"
                }
            duration.add_behavior(behavior)
        """



    def get_display(my):

        sobject = my.get_current_sobject()
        # FIXME: not sure why use_id = used here?
        my.search_key = SearchKey.get_by_sobject(sobject, use_id=True)

        top = DivWdg()
        top.add_class("spt_gantt_top")

        # this is for storing of all the data for GanttCbk
        value_wdg = HiddenWdg('gantt_data')
        #value_wdg = TextWdg('gantt_data')
        #value_wdg.add_style("width: 400px")
        value_wdg.add_class("spt_gantt_data")
        top.add(value_wdg)

        # set the initial values
        data = {
            '_range_start_date': my.start_date.strftime("%Y-%m-%d"),
            '_range_end_date': my.end_date.strftime("%Y-%m-%d"),
            '_offset': my.offset_width,
            '_width': my.total_width
        }
        # Need to set form value to false so that this info is not reused
        # on insert when draw FastTable.  This is probably a vestigial
        # feature to have set_value set the form value.
        value_wdg.set_value( jsondumps(data).replace('"', "&quot;"), set_form_value=False )


        # dummy for triggering the display of Commit button
        value_wdg = HiddenWdg(my.get_name())
        value_wdg.add_class("spt_gantt_value")
        top.add( value_wdg )

        top.add_style("margin: -3px")
 

        outer_div = DivWdg()
        top.add(outer_div)


        outer_div.add_class("spt_table_scale")
        outer_div.add_style("width: %s" % my.visible_width)
        outer_div.add_style("overflow: hidden")
        inner_div = DivWdg()
        inner_div.add_class("spt_gantt_scroll")
        inner_div.add_style("width: %s" % my.total_width)
        inner_div.add_style("margin-left: %s" % my.offset_width)
        inner_div.add_style("position: relative")
        outer_div.add(inner_div)
        inner_div.add_style("overflow: hidden")
        outer_div.add_class("spt_resizable")


        # draw the day widgets
        day_wdg = my.get_special_day_wdg()
        inner_div.add( day_wdg )


        height = my.kwargs.get("bar_height");
        if not height:
            height = 12
        else:
            height = int(height)



        #outer_div.add_style("height: 0%")
        outer_div.add_style("position: relative")
        outer_div.add_style("height: 100%")
        #inner_div.add_style("position: absolute")
        inner_div.add_style("min-height: %spx" % (height+6))

        # draw the dividers
        divider_wdg = my.get_divider_wdg()
        inner_div.add( divider_wdg )



        my.overlap = my.kwargs.get("overlap")
        if my.overlap in [True, "true"]:
            my.overlap = True
        else:
            my.overlap = False


        for index, properties in enumerate(my.property_list):
            color_results = my.color_results[index]
            color = color_results.get(sobject.get_search_key())
            if not color:
                color = properties.get("color")
                if not color:
                    color = "#555"

            key = properties.get('key')
            if not key:
                key = index

            editable = properties.get('edit')
            if editable != 'false':
                editable = True
            else:
                editable = False
            if my.overlap:
                editable = False

            default = properties.get('default')



            sobject = my.get_current_sobject()
            search_key = SearchKey.get_by_sobject(sobject)
            sobject_data = my.range_data.get(search_key)
            if sobject_data:
                sobject_data = sobject_data[index]
            if not sobject_data:
                sobject_data = []




            # get the data about the days in the range
            day_data = sobject.get_value("data", no_exception=True)
            if not day_data:
                day_data = {}
            else:
                day_data = jsonloads(day_data)


            for range_data in sobject_data:

                if range_data.get("color"):
                    cur_color = range_data.get("color")
                else:
                    cur_color = color

                bar = my.draw_bar(index, key, cur_color, editable, default=default, height=height, range_data=range_data, day_data=day_data)
                bar.add_style("z-index: 2")
                bar.add_style("position: absolute")
                bar.add_style("padding-top: 2px")
                bar.add_style("padding-bottom: 2px")
                #bar.add_style("border: solid 1px red")

                if not my.has_start_date and my.hide_bar:
                    pass
                else:
                    inner_div.add(bar)

                if not my.overlap:
                    inner_div.add("<br clear='all'>")
                else:
                    inner_div.add("<br class='spt_overlap' style='display: none' clear='all'>")


        #if not my.overlap:
        #    inner_div.add("<br clear='all'/>")
        return top


    def draw_bar(my, count, key, color='grey', editable=True, default='now', height=5, range_data=None, day_data={}):
        '''draw the Gantt bar with db col name and color'''

        if not default:
            default = 'now'

        show_dates = 'true'
        my.has_start_date = True

        widget = DivWdg()
        widget.add_style("width: 100%")
        widget.add_style("position: relative")
        widget.add_class("spt_gantt_range")
        if editable:
            widget.add_class("hand")

        #widget.add_style("border: solid 1px green")


        hidden = HiddenWdg('storage')
        hidden.add_class('spt_gantt_storage')
        widget.add(hidden)


        version = my.parent_wdg.get_layout_version()
        if version == "2":
            index = my.get_current_index()
        else:
            index = my.get_current_index() - 2

        #range_data = None
        if range_data:
            start_sobj_date = range_data.get('start_date')
            end_sobj_date = range_data.get('end_date')
        elif index < 0 or index >= len(my.start_sobj_dates[count]):
            start_sobj_date = None
            end_sobj_date = None
        else:
            start_sobj_date = my.start_sobj_dates[count][index]
            end_sobj_date = my.end_sobj_dates[count][index]


        # if there is none default, then get out
        if default == 'none' and not start_sobj_date and not end_sobj_date:
            return DivWdg()

        if not start_sobj_date:
            if default == 'now':
                start_sobj_date = datetime.datetime.now()
                my.has_start_date = False
            
        if not end_sobj_date:
            if default == 'now':
                end_sobj_date = datetime.datetime.now()

        # protect against None values from expresions (ie no @MIN becuase
        # it's all empty
        if not start_sobj_date and end_sobj_date:
            start_sobj_date = end_sobj_date
        elif not end_sobj_date and start_sobj_date:
            end_sobj_date = start_sobj_date
        elif not end_sobj_date and not start_sobj_date:
            return DivWdg()
            


        # why can these be strings??
        if isinstance(start_sobj_date, basestring):
            start_sobj_date = parser.parse(start_sobj_date)
        if isinstance(end_sobj_date, basestring):
            end_sobj_date = parser.parse(end_sobj_date)


        # build the display dates
        if show_dates != 'false':
            start_display_date = start_sobj_date.strftime("%b %d&nbsp;")
        else:
            start_display_date = start_sobj_date.strftime("&nbsp;")

        if show_dates != 'false':
            end_display_date = end_sobj_date.strftime("%b %d&nbsp;")
        else:
            end_display_date = end_sobj_date.strftime("&nbsp;")



        #if end_sobj_date < my.start_date:
        #    return widget
        
        # draw up all of the ranges
        info = {}
        width1, width2 = my.calculate_widths(start_sobj_date,end_sobj_date)
        
        info['width'] = [width1, width2]

        start_date_str = str(start_sobj_date)
        end_date_str = str(end_sobj_date)


        #info['key'] = 'bid'
        info['key'] = key
        info['index'] = count

        info['start_date'] = start_date_str
        info['end_date'] = end_date_str
        info['percent_per_day'] = my.percent_per_day
        info['max_width'] = my.total_width
        info['range_start_date'] = str(my.start_date)
        info['range_end_date'] = str(my.end_date)
        info['search_key'] = my.search_key
        start_width, end_width = info.get('width')


            
        # set the spacer: used for either the first or all in detail mode
        spacer = DivWdg()
        spacer.add_class("spt_gantt_spacer")
        spacer.add_style("height: 5px")
        spacer.add_style("float: left")
        spacer.add_style("text-align: right")
        spacer.add_style("width", "%s%%" % start_width)
        widget.add(spacer)

        start_div = DivWdg()
        if my.kwargs.get("date_mode") == "none" or not my.overlap:
            widget.add(start_div)
        start_div.add_style("float: left")
        start_div.add_style("margin-left: -42px")
        start_div.add_style('text-decoration: none')
        start_div.add_class("spt_gantt_start unselectable")
        #start_div.add_behavior( { 'type': 'hover', 'mod_styles': 'text-decoration: underline;' } )
        start_div.add(start_display_date)
        start_div.set_attr("spt_input_value", start_date_str)

        start_div.add_color("background", "background3")
        start_div.add_style("margin-top: 3px")
        start_div.add_border()
        start_div.set_round_corners(10, ["TL", "BL"])
        start_div.add_style("opacity: 0.4")

        start_div.add_class("spt_start_date")
        if my.kwargs.get("date_mode") == 'hover':
            start_div.add_style("display: none")

    
        if editable:
            behavior = {
            "type": 'drag',
            "mouse_btn": 'LMB',
            "drag_el": '@',
            "cb_set_prefix": 'spt.gantt.drag2',
            "mode": 'start',
            "info": info,
            }
            start_div.add_behavior(behavior)

            behavior = {
            "type": 'drag',
            "mouse_btn": 'LMB',
            "modkeys": 'SHIFT',
            "drag_el": '@',
            "cb_set_prefix": 'spt.gantt.drag2',
            "mode": 'start',
            "info": info,
            }
            start_div.add_behavior(behavior)


        else:
            behavior = {
                "type": 'click_up',
                "cbjs_action": "alert('Not editable in this view')"
                }
            start_div.add_behavior(behavior)
        #start_div.set_attr('title', start_date_col)
        # this is used for CalendarWdg initial date
        start_div.set_attr('date',  start_date_str)

        #from tactic.ui.widget import CalendarWdg
        #calendar = CalendarWdg()
        #calendar.add_style("display: none")
        #calendar.add_style("position: absolute")
        #widget.add(calendar)

        corners = ['TL','TR','BL','BR']


        duration_width = end_width - start_width
        diff = end_sobj_date - start_sobj_date


        my.days = round(float(diff.seconds)/3600/24) + diff.days + 1

        duration = my.get_duration_wdg( duration_width, color, height, corners=corners, day_data=day_data)
        widget.add(duration)
        #duration.add("%s days" % my.days)

        duration.set_attr("title", "%s - %s (%s days)" % (start_display_date, end_display_date, my.days) )


        if editable:
            behavior = {
            "type": 'drag',
            "mouse_btn": 'LMB',
            "drag_el": '@',
            "cb_set_prefix": 'spt.gantt.drag2',
            "mode": 'shift',
            "info": info,
            }
            duration.add_behavior(behavior)

            """
            behavior = {
            "type": 'drag',
            "mouse_btn": 'LMB',
            "modkeys": 'SHIFT',
            "drag_el": '@',
            "cb_set_prefix": 'spt.gantt.drag2',
            "mode": 'both',
            "info": info,
            }
            duration.add_behavior(behavior)
            """


        else:
            """
            behavior = {
                "type": 'click_up',
                "cbjs_action": "alert('Not editable in this view')"
                }
            duration.add_behavior(behavior)
            """



        end_div = DivWdg()
        if my.kwargs.get("date_mode") == "none" or not my.overlap:
            widget.add(end_div)

        end_div.add_style('float: left')
        end_div.add_style('padding-left: 2px')
        end_div.add_class("spt_gantt_end")
        end_div.set_attr("spt_input_value", end_date_str)
        end_div.add(end_display_date)


        end_div.add_color("background", "background3")
        end_div.add_style("margin-top: 3px")
        end_div.add_style("opacity: 0.4")
        end_div.add_border()
        end_div.set_round_corners(10, ["TR", "BR"])




        end_div.add_class("spt_end_date unselectable")
        if my.kwargs.get("date_mode") == 'hover':
                end_div.add_style("display: none")

        if editable:
            behavior = {
                "type": 'drag',
                "mouse_btn": 'LMB',
                "drag_el": '@',
                "cb_set_prefix": 'spt.gantt.drag2',
                "mode": 'end',
                "info": info,
     
            }
            end_div.add_behavior(behavior)


            behavior = {
            "type": 'drag',
            "mouse_btn": 'LMB',
            "modkeys": 'SHIFT',
            "drag_el": '@',
            "cb_set_prefix": 'spt.gantt.drag2',
            "mode": 'end_shift',
            "info": info,
            }
            end_div.add_behavior(behavior)



        else:
            behavior = {
                "type": 'click',
                "cbjs_action": "alert('Not editable in this view.')"
                }
            end_div.add_behavior(behavior)




        #duration_width = 3
        #colors = ['#F00', '#0F0', '#00f']
        #for i in range(0,3):
        #    widget.add( my.get_duration_wdg( duration_width+10, colors[i], height, top_margin=i*2, opacity=0.5, position='absolute', left=width1+i*3-10) )


        # TEST key up !!!
        dummy = TextWdg("foo")
        widget.add(dummy)
        dummy.add_class("spt_foo")
        dummy.add_style("position: absolute")
        dummy.add_style("left: -100000")
        widget.add_behavior( {
        'type': 'mouseover',
        'cbjs_action': '''
        var foo = bvr.src_el.getElement(".spt_foo");
        if (foo)
            foo.focus();
        '''
        } )
        widget.add_behavior( {
        'type': 'mouseleave',
        'cbjs_action': '''
        var foo = bvr.src_el.getElement(".spt_foo");
        if (foo)
            foo.blur();
        '''
        } )

        dummy.add_behavior( {
            'type': 'keyup',
            'cbjs_action': '''
            if (evt.control && evt.key == 'c') {
                var top = bvr.src_el.getParent(".spt_gantt_top");
                var duration = top.getElement(".spt_gantt_duration");
                duration.setStyle("border", "solid 1px red");
                spt.gantt.copy_selected(top);
            }
            else if (evt.control && evt.key == 'v') {
                var top = bvr.src_el.getParent(".spt_gantt_top");
                var duration = top.getElement(".spt_gantt_duration");
                duration.setStyle("border", "solid 1px blue");
                spt.gantt.paste_selected(top);
            }
            '''
        } )



        return widget



    def get_duration_wdg(my, duration_width, color, height, opacity=0.8, top_margin=0, position='relative', left=None, corners=['TL','TR','BL','BR'], day_data={}):


        duration = DivWdg()

        duration.add_attr("spt_days", my.days)
        duration.add_class("SPT_DTS")

        duration.add_style("position: %s" % position)
        if left:
            duration.add_style("left: %s%%" % left)


        duration.add_class("spt_gantt_duration")
        duration.add_style("background-color: %s" %color)
        duration.add_style("height: %spx" % height)
        duration.add_style("float: left")
        duration.add_style("vertical-align: middle")
        duration.add_style("overflow: hidden")
        duration.add_style("opacity: %s" % opacity)
        if duration_width == 0:
            duration.add_style("width", "1px")
        else:
            duration.add_style("width", "%s%%" % duration_width)

        duration.add_style("color: black")
        duration.add_style("font-size: 8px")
        duration.add_style("text-align: center")
        duration.add_style("margin-left: -1px")
        duration.add_style("margin-right: -1px")
        duration.add_border()


        duration.add_behavior( {
            'type': 'load',
            'days': my.days,
            'day_data': day_data,
            'cbjs_action': '''
            colors = bvr.day_data['colors'];
            labels = bvr.day_data['labels'];

            spt.gantt.fill_days(bvr.src_el, bvr.days, colors, labels);
            '''
        } )

        """
        duration.add_relay_behavior( {
            'type': 'dblclick',
            'legend_dialog_id': my.legend_dialog_id,
            'bvr_match_class': 'spt_duration_unit',
            'cbjs_action': '''
            alert('doubleclick');

            '''
        } )
        """



        sobject = my.get_current_sobject()
        if sobject:
            pipeline_code = sobject.get_value("pipeline_code", no_exception=True)
        else:
            pipeline_code = ""




        duration.add_relay_behavior( {
            'type': 'mouseup',
            'modkeys': 'SHIFT',
            'legend_dialog_id': my.legend_dialog_id,
            'pipeline_code': pipeline_code,
            'bvr_match_class': 'spt_duration_unit',
            'cbjs_action': '''

            var pos = bvr.src_el.getPosition();

            var top = bvr.src_el.getParent(".spt_gantt_top");
            if (! spt.gantt.is_selected(top) ) {
                spt.gantt.unselect_all();
                spt.gantt.select(top);

                var color_el = $(bvr.legend_dialog_id);
                spt.gantt.open_legend(color_el, bvr.pipeline_code, pos);
            }
            else {
                var state = bvr.src_el.getAttribute("spt_state");


                if (state == "on") {
                    bvr.src_el.setAttribute("spt_state", "off");

                    var color_el = $(bvr.legend_dialog_id);
                    spt.gantt.open_legend(color_el, bvr.pipeline_code, pos);

                    var color = color_el.getElement(".spt_color").value;
                    if (!color) {
                        color = '#FFF'
                    }
                    bvr.src_el.setStyle("background-color", color);
                    var label = color_el.getElement(".spt_label").value;
                    bvr.src_el.innerHTML = label;
                }
                else {
                    bvr.src_el.setAttribute("spt_state", "on");
                    bvr.src_el.setStyle("background-color", "");
                    bvr.src_el.innerHTML = "";
                }
            }
            '''
        } )


        
        return duration





    def get_special_day_wdg(my):
        # add in the divider
        day_wdg = DivWdg()

        # add todays divider
        #draw_div = my.get_day_bar_wdg(datetime.datetime.today(), "blue", opacity=1.0)
        #day_wdg.add(draw_div)



        # milestones
        show_milestones = my.kwargs.get("show_milestones")
        if show_milestones == "task":
            search = Search("sthpw/milestone")
            sobject = my.get_current_sobject()
            milestone_code = sobject.get_value("milestone_code")
            search.add_filter("code", milestone_code)
            milestones = search.get_sobjects()
        elif show_milestones == "project":
            search = Search("sthpw/milestone")
            search.add_project_filter()
            milestones = search.get_sobjects()
        else:
            milestones = []


        for milestone in milestones:
            due_date = milestone.get_value("due_date")
            color = milestone.get_value("color", no_exception=True)
            description = milestone.get_value("description")
            if not color:
                color = "#F00"

            if due_date:
                draw_div = my.get_day_bar_wdg(due_date, color)
                day_wdg.add(draw_div)
                draw_div.add_attr("title", "Milestone: %s [%s]" % (due_date, description))


        return day_wdg


    def get_divider_wdg(my):
        if my.divider_html:
            return my.divider_html

        # add in the divider
        divider_wdg = DivWdg()

        divider_wdg.add_style("width: 100%")
        divider_wdg.add_style("height: 100px")
        divider_wdg.add_style("z-index: 1")
        divider_wdg.add_style("position: absolute")

        mul = 1
        if len(my.divider_pos) > 50:
            mul = 3
        if len(my.divider_pos) > 100:
            return


        total_width = 0
        for i, divider_width in enumerate(my.divider_pos):
            total_width += divider_width
            if not (i % mul == 0):
                continue

            # draw a div with the border
            draw_div = DivWdg()
            draw_div.add_style("float: left")
            draw_div.add_style("position: absolute")
            draw_div.add_style("border-color: %s" % draw_div.get_color("border"))
            draw_div.add_style("border-width: 0px 0px 0px 1px")
            draw_div.add_style("border-style: dashed")
            draw_div.add_style("height: 100%")
            #draw_div.add_style("width: %s%%" % my.percent_per_day)
            draw_div.add_style("margin-left: %s%%" % total_width)


            #divider_div.add(draw_div)
            divider_wdg.add(draw_div)



        draw_div = my.get_day_bar_wdg(datetime.datetime.today(), "blue", opacity=0.5)
        divider_wdg.add(draw_div)



        # milestones
        show_milestone = False
        if show_milestone:
            search = Search("sthpw/milestone")
            sobject = my.get_current_sobject()
            milestone_code = sobject.get_value("milestone_code")
            search.add_filter("code", milestone_code)
            milestone = search.get_sobject()
            if milestone:
                due_date = milestone.get_value("due_date")
                if due_date:
                    color = "#F00"
                    draw_div = my.get_day_bar_wdg(due_date, color)
                    divider_wdg.add(draw_div)



        week_start = my.get_option('week_start') or "6"
        week_start = int(week_start) - 1
        if week_start == -1:
            week_start = 6

        dates = list(rrule.rrule(rrule.WEEKLY, byweekday=week_start, dtstart=my.start_date, until=my.end_date))


        if len(dates) > 75:
            dates = list(rrule.rrule(rrule.MONTHLY, bymonthday=1, dtstart=my.start_date, until=my.end_date))
        if len(dates) > 75:
            dates = list(rrule.rrule(rrule.YEARLY, byyearday=1, dtstart=my.start_date, until=my.end_date))

        for date in dates:
            color = '#999'
            draw_div = my.get_day_bar_wdg(date, color, opacity=0.15, days=2)
            divider_wdg.add(draw_div)




        my.divider_html = divider_wdg.get_buffer_display()
        return my.divider_html

        #return divider_wdg


    def get_day_bar_wdg(my, date, color, opacity=0.5, days=1):
        # this is required to fix the 1 day off issue
        one_day = datetime.timedelta(days=1)
        
        if isinstance(date, basestring):
            date = parser.parse(date)

        date = date - one_day
        tmp, width = my.calculate_widths(my.start_date, date)
        
        # draw a div with the border
        draw_div = DivWdg()
        draw_div.add_style("float: left")
        draw_div.add_style("position: absolute")
        draw_div.add_style("width: %s%%" % (my.percent_per_day * days))
        draw_div.add_style("height: 100%")
        draw_div.add_style("background: %s" % color)
        total_width = width
        draw_div.add_style("margin-left: %s%%" % total_width)
        draw_div.add_style("opacity: %s" % opacity)
        date = str(date).split(' ')
        #draw_div.add_attr("title", "Weekend: %s" %  date[0])

        return draw_div





    def get_group_bottom_wdg(my, sobjects):
        return

        # figure out the overlaps
        overlaps = []
        for sobject in sobjects:
            pass



        div = DivWdg()

        duration_width = 5
        color = "#F00"
        height = 12 

        for i in ['12', '24', '36', '48', '60']:
            color = "#900"
            duration = my.get_duration_wdg( duration_width, color, height, opacity=0.8, top_margin=0, position='relative', left=i)
            div.add(duration)

        #div.add( my.get_divider_wdg() )

        return div






class GanttCbk(DatabaseAction):
    '''Most straight forward date change should just use this option
       <options>[
        {
          "start_date_col":         "bid_start_date",
          "end_date_col":           "bid_end_date",
          "mode":                   "default"
        }]
        <options>
        '''
    def get_title(my):
        return "Dates Changed"

    def set_sobject(my, sobject):
        my.sobject = sobject


    def execute(my):
        web = WebContainer.get_web()
        if not my.sobject:
            return

        gantt_data = web.get_form_value("gantt_data")
        web_data = None
        if not gantt_data:
            # fast table 
            web_data = web.get_form_value("web_data")
            if web_data:
                gantt_data = web_data
            else:
                print("GanttCbk finds no data to update")
                return



        # get the options
        options = my.get_option("options")
        if options:
            options_list = jsonloads(options)
            expression = options_list[0].get("sobjects")
        else:
            # get the tasks
            options_list = [my.options]


        #tasks = Search.eval(expression, [my.sobject])

        if not web_data:
            gantt_data = jsonloads(gantt_data)
        else:
            gantt_data = gantt_data.get('gantt_data')
            if gantt_data:
                gantt_data = jsonloads(gantt_data)
            else:
                gantt_data = {}

        for key, data in gantt_data.items():
            if key == '__data__' or key.startswith("_"):
                continue

            index = data.get("index")
            if not index:
                index = 0
          
            try:
                options = options_list[index]
            except IndexError, e:
                raise TacticException('Missing option in the action class GanttCbk. Please check the Column Definition. The number of action options should match the number of editable bars.')
            
            expression = options.get("sobjects")
            if not expression:
                expression = "@SOBJECT(sthpw/task)"
            prefix = options.get("prefix")
            if not prefix:
                prefix = 'bid'

            # mode can be "cascade" or "default"
            # cascade would apply timedelta to each task
            mode = options.get("mode")

            # get the tasks
            tasks = Search.eval(expression, [my.sobject])
            start_date_col = options.get('start_date_col')
            if not start_date_col:
                start_date_col = '%s_start_date' % prefix;
            end_date_col = options.get('end_date_col')
            if not end_date_col:
                end_date_col = '%s_end_date' % prefix;


            start_date = data.get('start_date')
            end_date = data.get('end_date')
            orig_start_date = data.get('orig_start_date')
            orig_end_date = data.get('orig_end_date')

            colors = data.get('colors')
            labels = data.get('labels')

            day_data = {}
            day_data['colors'] = colors
            day_data['labels'] = labels
            day_data = jsondumps(day_data)

            # parsing the expression if any
            start_date = parser.parse(start_date)
            end_date = parser.parse(end_date)
            orig_start_date = parser.parse(orig_start_date)
            orig_end_date = parser.parse(orig_end_date)
           
            # cascade tries to shift all related tasks by the same delta range,
            # using start delta if available, or end delta as second choice
            if mode == 'cascade':
                start_delta = start_date - orig_start_date
                end_delta = end_date - orig_end_date
                # assuming start_delta takes preference, use end_delta if start_delta
                # is zero. but this logic is still strange, what if the user changes 
                # both the start and end date. 
                if start_delta.days == 0:
                    start_delta = end_delta

                for task in tasks:
                    old_start_date = parser.parse( task.get_value(start_date_col) )
                    old_end_date = parser.parse( task.get_value(end_date_col) )
                    new_start_date = old_start_date + start_delta
                    new_end_date = old_end_date + start_delta
                    task.set_value(start_date_col, new_start_date)
                    task.set_value(end_date_col, new_end_date)

                    task.set_value("data", day_data)

                    task.commit()
            else: # default to just change current date
                # usually only contain 1 task, the current task
                for task in tasks:
                    task.set_value(start_date_col, start_date)
                    task.set_value(end_date_col, end_date)
                    task.set_value("data", day_data)
                    task.commit()




class GanttLegendWdg(BaseRefreshWdg):

    def get_display(my):


        div = DivWdg()
        my.set_as_panel(div)

        div.add_color("background", "background")
        div.add_style("padding: 0px 20px 20px 20px")


        title_wdg = DivWdg()
        div.add(title_wdg)
        title_wdg.add("Current Color")
        title_wdg.add_style("padding: 10px")
        title_wdg.add_style("font-style: bold")
        title_wdg.add_style("margin: 0px -20px 10px -20px")
        title_wdg.add_color("background", "background3")
        title_wdg.add_border()



        table = Table()
        div.add(table)

        table.add_row()
        table.add_cell("Color: ")
        text = TextWdg("color")
        #from tactic.ui.input import ColorInputWdg
        #text = ColorInputWdg("color")
        table.add_cell(text)

        text.add_class("spt_color")
        text.set_value("red")

        table.add_row()
        table.add_cell("Label: ")
        text = TextWdg("label")
        table.add_cell(text)
        text.add_class("spt_label")
        text.set_value("")





        table = Table()
        div.add(table)
        table.set_max_width()


        table.add_relay_behavior( {
            'type': 'mouseup',
            'bvr_match_class': 'spt_process',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_color_top");
            var color = bvr.src_el.getAttribute("spt_color");
            var status = bvr.src_el.getAttribute("spt_status");
            var label = "";
            if (status && status != '__empty__') {
                parts = status.split(" ");
                for (var i = 0; i < parts.length; i++) {
                    label += parts[i].substr(0,1);
                }
            }

            var color_el = top.getElement(".spt_color");
            var label_el = top.getElement(".spt_label");

            color_el.value = color;
            label_el.value = label;
            '''
        } )

        table.add_relay_behavior( {
            'type': 'mouseover',
            'bvr_match_class': 'spt_process',
            'cbjs_action': '''
            bvr.src_el.setStyle("background-color", "#999");
            '''
        } )
        table.add_relay_behavior( {
            'type': 'mouseleave',
            'bvr_match_class': 'spt_process',
            'cbjs_action': '''
            bvr.src_el.setStyle("background-color", "");
            '''
        } )

        table.add_relay_behavior( {
            'type': 'dblclick',
            'bvr_match_class': 'spt_process',
            'cbjs_action': '''
            alert("Change color");
            '''
        } )


        """
        table.add_relay_behavior( {
            'type': 'mouseup',
            'bvr_match_class': 'spt_pipeline',
            'cbjs_action': '''
            var class_name = 'tactic.ui.panel.ViewPanelWdg';
            var search_key = bvr.src_el.getAttribute("spt_search_key");
            var kwargs = {
                search_type: 'config/process',
                view: 'table',
                show_shelf: false,
                search_key: search_key,
            };
            spt.panel.load_popup("Processes", class_name, kwargs);

            '''
        } )
        """


        cur_pipeline_code = my.kwargs.get("pipeline_code")
        if not cur_pipeline_code:
            cur_pipeline_code = 'task'

        search = Search("sthpw/pipeline")
        if cur_pipeline_code:
            search.add_filter("code", cur_pipeline_code)
        search.add_order_by("code")
        pipelines = search.get_sobjects()

        tr, td = table.add_row_cell()

        for pipeline in pipelines:
            pipeline_code = pipeline.get_code()

            pipeline_div = DivWdg()
            td.add(pipeline_div)

            pipeline_div.add_class("spt_pipeline")
            pipeline_div.add_attr("spt_pipeline", pipeline_code)
            pipeline_div.add_attr("spt_search_key", pipeline.get_search_key())

            if cur_pipeline_code and cur_pipeline_code != pipeline_code:
                pipeline_div.add_style("display: none")


            hidden = HiddenWdg("pipeline")
            pipeline_div.add(hidden)
            hidden.set_value(pipeline_code)

            
            title_wdg = DivWdg()
            pipeline_div.add(title_wdg)
            title_wdg.add_style("padding: 10px")
            title_wdg.add_style("font-style: bold")
            title_wdg.add_style("margin: 10px -20px 10px -20px")
            title_wdg.add_color("background", "background3")
            title_wdg.add_border()

            icon = IconButtonWdg(title="Save", icon=IconWdg.SAVE)
            title_wdg.add(icon)
            icon.add_style("float: right")
            icon.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_pipeline");
            var values = spt.api.get_input_values(top);
            var cmd = 'tactic.ui.table.GanttLegendCbk';
            var server = TacticServerStub.get();
            server.execute_cmd(cmd, values);
            '''
            } )

            title_wdg.add(pipeline_code)

            processes = Search.eval("@SOBJECT(config/process)", pipeline)
            if not processes:
                msg_wdg = DivWdg()
                pipeline_div.add(msg_wdg)
                msg_wdg.add("No process defined")
                msg_wdg.add_style("font-style: italic")


            from tactic.ui.container import DynamicListWdg
            list_wdg = DynamicListWdg()
            pipeline_div.add(list_wdg)

            list_wdg.add_template(my.get_process_wdg() )

            for process_sobj in processes:
                list_wdg.add_item( my.get_process_wdg( process_sobj) )


        return div



    def get_process_wdg(my, process_sobj=None):
        div = DivWdg()

        if process_sobj:
            process = process_sobj.get_value("process")
            color = process_sobj.get_value("color")
        else:
            color = ''
            process = '- empty -'

        if not color:
            color = "#0F0"

        div.add_class("spt_process")
        div.add_attr("spt_color", color)
        div.add_attr("spt_status", process)
        div.add_class("hand")


        from tactic.ui.input import ColorInputWdg
        hidden = TextWdg("color")
        hidden.add_style("width: 22px")
        hidden.add_style("height: 22px")
        if color:
            hidden.add_style("background-color", color)
            hidden.add_style("color", color)
            hidden.set_value(color)
        color_input = ColorInputWdg()
        color_input.set_input(hidden)
        div.add( color_input )
        color_input.add_style("float: left")
        color_input.add_style("margin-right: 10px")

        from tactic.ui.input import TextInputWdg
        process_text = TextInputWdg(name="process")
        div.add(process_text)
        if process:
            process_text.set_value(process)



        return div


class GanttLegendCbk(Command):

    def execute(my):

        pipeline_code = my.kwargs.get("pipeline")[0]
        pipeline = Search.get_by_code("sthpw/pipeline", pipeline_code)

        #print pipeline.get_process_names()



        process = my.kwargs.get("process")






def get_onload_js():
    return r'''

spt.gantt = {};

// Gantt chart functionality

//
// These are for moving the Calendar Gantt Widget dynamically.
//

spt.gantt.drag_data = {};

spt.gantt.ranges = [];

spt.gantt.reset = function()
{
    spt.gantt.start_date = null;
    spt.gantt.end_date = null;
    spt.gantt.start_offset = null;
    spt.gantt.end_offset = null;

    spt.gantt.drag_spacer = null;
    spt.gantt.drag_duration = null;
    spt.gantt.drag_start = null;
    spt.gantt.drag_end = null;
    spt.gantt.drag_start_x = null;

}

spt.gantt.init = function() {
    spt.gantt.reset();
    spt.gantt.width = bvr.width;
    spt.gantt.offset = bvr.offset;

    spt.gantt.orig_width = spt.gantt.width;
    spt.gantt.visible = 0;
}

spt.gantt.init();

// Date operations

spt.gantt.months = ['January','February','March','April','May','June','July','August','September','October','November','December']



// days functions
spt.gantt.fill_header_days = function(top, start_date, end_date, percent_per_day) {

    var color1 = top.getAttribute("spt_color1");
    var color2 = top.getAttribute("spt_color2");

    //require(["moment.min.js"], function() {
    spt.dom.load_js(["moment.min.js"], function() {

    var date = moment(start_date, "YYYY-MM-DD");
    end_date = moment(end_date, "YYYY-MM-DD");
    end_date.subtract('days', 1);

    var count = 0;
    while (true) {
        var el = $(document.createElement("div"));
        top.appendChild(el);
        el.setStyle("width", percent_per_day + "%");
        el.setStyle("height", "12px");
        el.setStyle("float", "left");
        el.setStyle("font-size", "10px");
        el.setStyle("text-align", "center");
        if (count % 2 == 0) {
            el.setStyle("background", color1);
        }
        else {
            el.setStyle("background", color2);
        }
        //var day = date.format('MMM-DD');
        var day = date.format('DD');
        var text = $(document.createTextNode(day));
        el.appendChild(text);

        date.add('days', 1);
        if (! (date < end_date)) {
            break;
        }
        //count +=1;
        //if (count > 2000) {
        //    alert("Hit max num of days");
        //    break;
        //}
    }

    }) // end require


}



spt.gantt.fill_header_months = function(top, start_date, end_date, percent_per_day) {

    var color1 = top.getAttribute("spt_color1");
    var color2 = top.getAttribute("spt_color2");
    var color1 = "#888"
    var color2 = "#AAA"

    //require(["moment.min.js"], function() {
    spt.dom.load_js(["moment.min.js"], function() {

    var date = moment(start_date, "YYYY-MM-DD");
    end_date = moment(end_date, "YYYY-MM-DD");
    end_date.subtract('days', 1);

    var count = 0;
    var day_count = 0;
    var item_count = 0;
    var last_month = '';
    var last_day = '';
    var last_one = false;

    while (true) {
        var month = date.format('MMM');
        var day = date.format('DD');
        if (month != last_month || last_one) {

            var el = $(document.createElement("div"));
            top.appendChild(el);
            var percent = percent_per_day*day_count;
            el.setStyle("width", percent + "%");
            el.setStyle("height", "12px");
            el.setStyle("float", "left");
            el.setStyle("font-size", "10px");
            el.setStyle("text-align", "center");
            if (item_count % 2 == 0) {
                el.setStyle("background", color1);
            }
            else {
                el.setStyle("background", color2);
            }

            var text = $(document.createTextNode(last_month));
            el.appendChild(text);

            last_month = month;
            day_count = 0;
            item_count += 1;
        }

        if (last_one) {
            break;
        }

        date.add('days', 1);
        if (date >= end_date) {
            last_one = true;
        }
        count +=1;
        day_count += 1;
        if (count > 200) {
            alert("Hit max num of days");
            break;
        }
    }

    }) // end require


}




spt.gantt.fill_days = function(top, days, colors, labels) {
    var percent = 100.0 / days;

    for (var i = 0; i <= days; i++) {
        var el = $(document.createElement("div"));
        top.appendChild(el);
        el.setStyle("width", percent + "%");
        el.setStyle("overflow", "hidden");
        el.setStyle("margin-left", (i*percent) + "%");
        el.setStyle("position", "absolute");
        el.setStyle("height", "100%");
        el.setStyle("float", "left");
        el.setStyle("border-style", "solid");
        el.setStyle("border-width", "0 1 0 0");
        el.setStyle("border-color", "#777");
        el.setStyle("font-size", "12px");
        el.setStyle("padding-top", "5px");
        el.setAttribute("spt_state", "on");
        //if (i%2 == 0 ) {
        //    el.setStyle("opacity", "0.2");
        //    el.setStyle("background", "#FFF");
        //}
        el.addClass("spt_duration_unit")

        var has_color = false;
        if (colors) {
            var color = colors[i];
            if (color) {
                el.setStyle("background", color);
                has_color = true;
                if (labels) {
                    var label = labels[i];
                    if (label) {
                        el.innerHTML = label;
                    }
                }
            }
        }

        /*
        if (! has_color) {
            if (i % 7 == 1 || i % 7 == 2) {
                el.setStyle("background", "#DDD");
                el.setStyle("border", "solid 1px #BBB");
            }
        }
        */

    }
}


spt.gantt.get_data = function(range) {
    var data = {};

    // gather the elements that contain the data
    data.drag_spacer = range.getElement(".spt_gantt_spacer");
    data.drag_duration = range.getElement(".spt_gantt_duration");
    data.drag_start = range.getElement(".spt_gantt_start");
    data.drag_end = range.getElement(".spt_gantt_end");


    var start_date_str = data.drag_start.getAttribute("spt_input_value");
    var end_date_str = data.drag_end.getAttribute("spt_input_value");
    data.start_date = start_date_str;
    data.end_date = end_date_str;


    var colors = [];
    var labels = [];
    var duration_units = data.drag_duration.getElements(".spt_duration_unit");
    for (var j = 0; j < duration_units.length; j++) {
        var color = duration_units[j].getStyle("background-color");
        colors.push(color);
        var label = duration_units[j].innerHTML
        labels.push(label);
    }

    data['colors'] = colors;
    data['labels'] = labels;
    data['num_days'] = duration_units.length;

    data['width'] = data.drag_duration.getStyle("width")
    data['offset'] = data.drag_spacer.getStyle("width");

    data.html = range.innerHTML;

    return data;
}


spt.gantt.clipboard = null;
spt.gantt.selected = [];


spt.gantt.select = function(top) {
    var duration = top.getElement(".spt_gantt_duration");
    duration.setStyle("border", "solid 1px red");
    top.setAttribute("spt_select", "true");

    spt.gantt.selected.push(top);
}

spt.gantt.is_selected = function(top) {
    var selected = top.getAttribute("spt_select");
    if (selected == "true") {
        return true;
    }
    else {
        return false;
    }
}

spt.gantt.unselect_all = function() {
    for (var i = 0; i < spt.gantt.selected.length; i++) {
        var top = spt.gantt.selected[i];
        var duration = top.getElement(".spt_gantt_duration");
        duration.setStyle("border", "solid 1px #AAA");
        top.setAttribute("spt_select", "false");
    }
    spt.gantt.selected = [];
}





spt.gantt.copy_selected = function(top) {
    spt.gantt.clipboard = [];
    var data = spt.gantt.get_data(top);
    spt.gantt.clipboard.push(data);

    spt.table.unselect_all_rows();
    var row = top.getParent(".spt_table_row");
    spt.table.select_row(row);

    return data;

}



spt.gantt.paste_selected = function(top) {
    var data = spt.gantt.clipboard[0];

    spt.table.unselect_all_rows();

    spt.behavior.replace_inner_html(top, data.html);

    var row = top.getParent(".spt_table_row");
    spt.table.select_row(row);

    return;

    /* NOTE: This is the peicewise way.  We may do this later for more complex
    copy and paste operations, so keeping this logic around

    var drag_duration = top.getElement(".spt_gantt_duration");
    var drag_spacer = top.getElement(".spt_gantt_spacer");
    var drag_start = top.getElement(".spt_gantt_start");
    var drag_end = top.getElement(".spt_gantt_end");

    // set the dates
    drag_start.innerHTML = data.start_date;
    drag_end.innerHTML = data.end_date;


    // set the position
    offset = data.offset;
    drag_spacer.setStyle("width", offset);

    // set the width
    width = data.width;
    drag_duration.setStyle("width", width);

    // set the start_date

    // set the end_date

    var node = drag_duration;
    while (node.hasChildNodes()) {
        node.removeChild(node.lastChild);
    }
    spt.gantt.fill_days(drag_duration, data['num_days'], data['colors'], data['labels']);
    */

}



spt.gantt.last_pipeline_code = null;
spt.gantt.open_legend = function(color_el, pipeline_code, pos) {

    var content = color_el.getElement(".spt_color_content")

    if (pipeline_code != spt.gantt.last_pipeline_code) {
        var class_name = 'tactic.ui.table.GanttLegendWdg';
        var kwargs = {
            pipeline_code: pipeline_code
        }
        spt.panel.load(content, class_name, kwargs);
    }

    spt.gantt.last_pipeline_code = pipeline_code;

    if (color_el.getStyle("display") == "none") {
        color_el.position({x: pos.x+400, y: pos.y-100});
        color_el.setStyle("display", "");
    }

    var pipeline_els = color_el.getElements(".spt_pipeline");
    for (var i = 0; i < pipeline_els.length; i++) {
        var pipeline_el_code = pipeline_els[i].getAttribute("spt_pipeline");
        if (pipeline_el_code == pipeline_code) {
            pipeline_els[i].setStyle("display", "");
        }
        else {
            pipeline_els[i].setStyle("display", "none");
        }
    }

}




// This is called when any date is clicked in the header
spt.gantt.date_clicked_cbk = function(evt, bvr, mouse_411) {
    var table = bvr.src_el.getParent('.spt_table');

    var date_range = bvr.src_el;
    var offset = date_range.getAttribute("spt_gantt_offset");
    offset = parseInt(offset);
    var width = date_range.getAttribute("spt_gantt_width");
    width = parseInt(width);

    var scroll_els = table.getElements('.spt_gantt_scroll');
    for (var i=0; i< scroll_els.length; i++) {
        var scroll_el = scroll_els[i];
        scroll_el.setStyle("width", width);
        scroll_el.setStyle("margin-left", offset);
    }

    spt.gantt.width = width;
    spt.gantt.offset = offset;

    // display the title at the proper scale levels.
    var gantt_top = bvr.src_el.getParent(".spt_gantt_top");
    var percent_per_day = gantt_top.getAttribute("spt_percent_per_day");
    var pixel_per_day = percent_per_day * spt.gantt.width / 100;
    spt.gantt._process_title(table, pixel_per_day);

    spt.gantt.set_data( table );

}




// This is the code to drag an individual date bar in the gantt wdg

spt.gantt.drag2_setup = function(evt, bvr, mouse_411)
{
    var info = bvr.info;

    var src_el = bvr.src_el;

    var top = bvr.src_el.getParent(".spt_gantt_top");
    spt.gantt.unselect_all();
    spt.gantt.select(top);
   

    var layout = src_el.getParent(".spt_layout");
    var version = layout.getAttribute("spt_version");

    if (version == "2") {
        var containers = spt.table.get_selected_rows(table);
        var container_css = '.spt_table_row';
        var table = bvr.src_el.getParent('.spt_table_table');
    }
    else {
        // get all of the selected rows
        var containers = spt.dg_table.get_selected_tbodies(table);
        var container_css = '.spt_table_tbody';
        var table = bvr.src_el.getParent('.spt_table');
    }
    spt.gantt.ranges = [];
    var search_keys = [];
    for (var i = 0; i < containers.length; i++) {
        var ranges = containers[i].getElements('.spt_gantt_range');
        var search_key = containers[i].getAttribute("spt_search_key");
        for (var j = 0; j < ranges.length; j++ ) {
            spt.gantt.ranges.push(ranges[j]);
            search_keys.push(search_key);
        }
    }


    // if none are selected, get the one that is dragged
    if (spt.gantt.ranges.length == 0) {
        var ghost_el = $(bvr.drag_el);
        var range = ghost_el.getParent(".spt_gantt_range");
        var search_key = ghost_el.getParent(container_css).getAttribute("spt_search_key");
        spt.gantt.ranges.push(range);
        search_keys.push(search_key);
    }


    for (var i=0; i<spt.gantt.ranges.length; i++)
    {
        var data = spt.gantt.drag_data[i];
        if (typeof(data) == 'undefined') {
            data = {};
            spt.gantt.drag_data[i] = data;
        }

        var range = spt.gantt.ranges[i];
        data.range = range;

        data.drag_start_x = mouse_411.curr_x;


        data.drag_spacer = range.getElement(".spt_gantt_spacer");
        data.drag_duration = range.getElement(".spt_gantt_duration");
        data.drag_start = range.getElement(".spt_gantt_start");
        data.drag_end = range.getElement(".spt_gantt_end");



        //spt.gantt.colors = data.drag_duration.innerHTML;
        // store the duration info
        spt.gantt.colors = [];
        spt.gantt.labels = [];
        var duration_units = data.drag_duration.getElements(".spt_duration_unit");
        for (var j = 0; j < duration_units.length; j++) {
            var color = duration_units[j].getStyle("background-color");
            spt.gantt.colors.push(color);
            var label = duration_units[j].innerHTML
            spt.gantt.labels.push(label);
        }




        data.start_date = data.drag_start.getAttribute('spt_input_value')
        if (data.start_date == null) {
            var start_date_str = info['start_date'];
            data.start_date = start_date_str;
        }

        data.end_date = data.drag_end.getAttribute('spt_input_value')
        if (data.end_date == null) {
            var end_date_str = info['end_date'];
            data.end_date = end_date_str;
        }

        data.orig_start_date = data.start_date;
        data.orig_end_date = data.end_date;


        // store the start and end widths
        var start_offset = data.drag_spacer.getStyle('width');
        data.start_offset = parseFloat( start_offset.replace('%', '') );
        var end_offset = data.drag_duration.getStyle('width');
        data.end_offset = parseFloat( end_offset.replace('%', '') );

        // set the search of the sobject
        data.search_key = search_keys[i];

    }



}


spt.gantt.HALF_DAY = 0.5*24*3600*1000;

spt.gantt.drag2_motion = function(evt, bvr, mouse_411)
{
    var info = bvr.info;
    var percent_per_day = info['percent_per_day'];
    var pixel_per_day = percent_per_day * spt.gantt.width / 100;

    var mode = bvr.mode;

    var ranges = spt.gantt.ranges;
    for (var i=0; i<ranges.length; i++)
    {
        var data = spt.gantt.drag_data[i];

        var pixel_diff = parseFloat(mouse_411.curr_x - data.drag_start_x);
        if (pixel_diff < 0) {
            pixel_diff = pixel_diff - (pixel_diff % pixel_per_day);
        }
        else {
            pixel_diff = pixel_diff - (pixel_diff % pixel_per_day) + pixel_per_day;
        }
        var calc_info = spt.gantt._drag2_get_calc_info(bvr, data.start_date, data.end_date, pixel_diff);

        var percent_diff = pixel_diff / spt.gantt.width * 100;
        var start_date_str = calc_info['start_value_date'];
        var end_date_str = calc_info['end_value_date'];


        var time_diff;


        if (mode == "start" || mode == 'start_shift') {

            //if (info.search_key != data.search_key) {
            //    continue;
            //}

            time_diff = calc_info.orig_end_date.getTime() - calc_info.start_date.getTime()
            if (time_diff <= -spt.gantt.HALF_DAY) {
                continue;
            }

            data.drag_start.innerHTML = calc_info['start_display_date'];

            var start_width = (data.start_offset + percent_diff) + "%";
            data.drag_spacer.setStyle("width", start_width);

            var end_width = (data.end_offset - percent_diff) + "%";
            data.drag_duration.setStyle("width", end_width);

            data.drag_start.setAttribute("spt_input_value", start_date_str);


            //if (info.search_key == data.search_key) {
            //    mode = 'both';
            //}

        }
        else if (mode == "end" || mode == 'end_shift') {

            if (mode == 'end_shift' && info.search_key != data.search_key) {
                continue;
            }

            time_diff = calc_info.end_date.getTime() - calc_info.orig_start_date.getTime();
            // not sure about this .... produces some strange behavior
            if (time_diff <= -spt.gantt.HALF_DAY) {
                continue;
            }

            data.drag_end.innerHTML = calc_info['end_display_date'];

            var start_width = (data.end_offset + percent_diff) + "%";
            data.drag_duration.setStyle("width", start_width);

            data.drag_end.setAttribute("spt_input_value", end_date_str);



            if (mode == 'end_shift' && info.search_key == data.search_key) {
                mode = 'both';
            }
        }
        else {
            data.drag_start.innerHTML = calc_info['start_display_date'];
            data.drag_end.innerHTML = calc_info['end_display_date'];


            var start_width = (data.start_offset + percent_diff) + "%";
            data.drag_spacer.setStyle("width", start_width);

            data.drag_start.setAttribute("spt_input_value", start_date_str);
            data.drag_end.setAttribute("spt_input_value", end_date_str);

            time_diff = calc_info.end_date.getTime() - calc_info.start_date.getTime();
        }

        // set the number of days
        days_diff = parseInt( time_diff / (24*3600*1000) ) + 1;
        data.drag_duration.innerHTML = days_diff + " days";
        data.drag_duration.setAttribute("spt_days", days_diff);


    } 


}


spt.gantt._drag2_get_date = function(date_str, milli_diff)
{
    // calculate date
    var parts = date_str.split(/[- :\.]/);
    var year = parseInt(parts[0]);
    var month = parseInt(parts[1].replace(/^0/,''))-1;
    var day = parseInt(parts[2].replace(/^0/,''));
    var orig_date = new Date(year, month, day);
    var new_date = new Date(orig_date.getTime() + milli_diff);

    return [orig_date, new_date];
}

spt.gantt._drag2_get_calc_info = function(bvr, start_date_str, end_date_str, pixel_diff)
{
    var info = bvr.info;

    var calc_info = {};

    //var percent_diff = pixel_diff / 10;
    var percent_diff = pixel_diff / spt.gantt.width * 100;

    var start_time;
    var end_time;
    var percent_per_day = info['percent_per_day'];
    var days_diff = percent_diff / percent_per_day;
    var milli_diff = days_diff * 24 * 3600 * 1000;
    calc_info['milli_diff'] = milli_diff;

    // calculate start date
    if (true) {
    var dates = spt.gantt._drag2_get_date(start_date_str, milli_diff);
    var orig_date = dates[0];
    var new_date = dates[1];
    calc_info['start_date'] = new_date;
    calc_info['orig_start_date'] = orig_date;

    start_time = new_date.getTime();
    var display_date_str = spt.gantt.months[new_date.getMonth()].substr(0,3) + " " + new_date.getDate();
    calc_info['start_display_date'] = display_date_str;

    var value_date_str = new_date.getFullYear() + "-" + (new_date.getMonth()+1) + "-" + new_date.getDate();
    calc_info['start_value_date'] = value_date_str;
    }

    // calculate end_date
    if (true) {
    var dates = spt.gantt._drag2_get_date(end_date_str, milli_diff);
    var orig_date = dates[0];
    var new_date = dates[1];
    calc_info['end_date'] = new_date;
    calc_info['orig_end_date'] = orig_date;

    var display_date_str = spt.gantt.months[new_date.getMonth()].substr(0,3) + " " + new_date.getDate();
    end_time = new_date.getTime();
    calc_info['end_display_date'] = display_date_str;

    var value_date_str = new_date.getFullYear() + "-" + (new_date.getMonth()+1) + "-" + new_date.getDate();
    calc_info['end_value_date'] = value_date_str;
    }


    return calc_info;

}


spt.gantt.drag2_action = function(evt, bvr, mouse_411)
{
    var info = bvr.info;
    var percent_per_day = info['percent_per_day'];
    var pixel_per_day = percent_per_day * spt.gantt.width / 100;

 
    // put in some cached data for the loop
    var table = spt.gantt.table;

    var layout = bvr.src_el.getParent(".spt_layout");
    var version = layout.getAttribute("spt_version");
        
    var selected_rows = version == 2 ? spt.table.get_selected_rows(): spt.dg_table.get_selected( table );
    var cached_data = {};
    cached_data['selected_rows'] = selected_rows;
    cached_data['multi'] = false;



    var ranges = spt.gantt.ranges;
    for (var i=0; i<ranges.length; i++)
    {
        var data = spt.gantt.drag_data[i];

        var start_date_str = data.drag_start.getAttribute("spt_input_value");
        var end_date_str = data.drag_end.getAttribute("spt_input_value");


        // remove and fill in the days
        var node = data.drag_duration;
        while (node.hasChildNodes()) {
            node.removeChild(node.lastChild);
        }
        var days = parseInt(node.getAttribute("spt_days"));
        spt.gantt.fill_days(node, days, spt.gantt.colors, spt.gantt.labels);


        var pixel_diff = parseFloat(mouse_411.curr_x - data.drag_start_x);
        if (pixel_diff < 1 && pixel_diff > -1) {
            return;
        }




        //value_wdg is for triggering the commit button
        var top_el = data.range.getParent(".spt_gantt_top");
        var value_wdg = top_el.getElement(".spt_gantt_value");
        var value = start_date_str + ":" + end_date_str;
        value_wdg.value = value;

        // the real data!
        var gantt_data_wdg = top_el.getElement(".spt_gantt_data");
        var gantt_value = gantt_data_wdg.value;
        if (gantt_value != '') {
            gantt_value = JSON.parse(gantt_value);
        }
        else {
            gantt_value = {};
            gantt_data_wdg.value = JSON.stringify(gantt_value);
        }

        // gather all of the gantt_data
        gantt_value[info.key] = {};
        var gantt_key_data = gantt_value[info.key];
        gantt_key_data['index'] = info.index;
        gantt_key_data['start_date'] = start_date_str;
        gantt_key_data['end_date'] = end_date_str;
        gantt_key_data['orig_start_date'] = data.orig_start_date;
        gantt_key_data['orig_end_date'] = data.orig_end_date;


        gantt_key_data['colors'] = spt.gantt.colors;
        gantt_key_data['labels'] = spt.gantt.labels;




        
        gantt_data_wdg.value = JSON.stringify(gantt_value);

        spt.dg_table.edit.widget = top_el;
        var key_code = spt.kbd.special_keys_map.ENTER;
        // what goes in here is just used to trigger the Commit btn
        if (version == '2'){
            // TODO: missing cached_data
            spt.table.set_layout(layout);
            spt.table.accept_edit(top_el, value_wdg.value, false);
        }
        else {
            spt.dg_table.inline_edit_cell_cbk( value_wdg, cached_data );
        }

    }


    // clear out the datastructures
    spt.gantt.reset();

}




// This method pushes the width and offset data.
spt.gantt.set_data = function(table) {

    // get all of the selected rows
    var tbodies = spt.has_class(table, 'spt_table_table') ?  spt.table.get_all_rows(): spt.dg_table.get_all_tbodies(table);
    var ranges = [];
    for (var i = 0; i < tbodies.length; i++) {
        // there can be many ranges in each cell.  Each range is a 
        // single date row within a cell
        var tbody_ranges = tbodies[i].getElements('.spt_gantt_range');
        for (var j = 0; j < tbody_ranges.length; j++ ) {
            ranges.push(tbody_ranges[j]);
        }
    }

    for (var i=0; i<ranges.length; i++)
    {

        var range = ranges[i];
        var top_el = range.getParent(".spt_gantt_top");

        // the real data!
        var gantt_data_wdg = top_el.getElement(".spt_gantt_data");
        var gantt_value = gantt_data_wdg.value;
        if (gantt_value != '') {
            gantt_value = JSON.parse(gantt_value);
        }
        else {
            gantt_value = {};
        }


        gantt_value['_width'] = spt.gantt.width;
        gantt_value['_offset'] = spt.gantt.offset;

        gantt_data_wdg.value = JSON.stringify(gantt_value);
    }

}




// This is the drag to scroll left or right
spt.gantt.drag_scroll_setup = function(evt, bvr, mouse_411)
{
    spt.gantt.drag_start_x = mouse_411.curr_x;

    spt.gantt.table = bvr.src_el.getParent('.spt_table_table');
    if (!spt.gantt.table)
        spt.gantt.table = bvr.src_el.getParent('.spt_table');

    spt.gantt.scroll_els = spt.gantt.table.getElements('.spt_gantt_scroll');
    spt.gantt.top_el = spt.gantt.table.getElement('.spt_gantt_top');

    var offset = spt.gantt.scroll_els[0].getStyle("margin-left");
    spt.gantt.offset = parseInt( offset.replace("px", "") );

    var width = spt.gantt.scroll_els[0].getStyle("width");
    spt.gantt.width = parseInt( width.replace("px", "") );

    var scale_el = bvr.src_el;
    var visible = scale_el.getStyle("width");
    spt.gantt.visible = parseInt( visible.replace("px", "") );


} 



spt.gantt.drag_scroll_motion = function(evt, bvr, mouse_411)
{

    var diff = parseFloat(mouse_411.curr_x - spt.gantt.drag_start_x);
    var offset = spt.gantt.offset + diff;

    if (offset > 0) {
        offset = 0;
    }
    if (offset < - spt.gantt.width + spt.gantt.visible) {
        offset = - spt.gantt.width + spt.gantt.visible;
    }

    // if the width is smaller than the visible, then scrolling is not possible
    if (spt.gantt.width < spt.gantt.visible) {
        offset = 0;
    }

    for (var i=0; i < spt.gantt.scroll_els.length; i++) {
        var scroll_el = spt.gantt.scroll_els[i];

        scroll_el.setStyle("margin-left", offset);
    }

}


spt.gantt.drag_scroll_action = function(evt, bvr, mouse_411)
{


    var diff = parseFloat(mouse_411.curr_x - spt.gantt.drag_start_x);

    // if no scroll has take place, then unselect all
    if (diff < 1 && diff > -1) {
        spt.gantt.unselect_all();
        return;
    }



    var offset = spt.gantt.offset + diff;
    if (offset > 0) {
        offset = 0;
    }
    else if (offset < - spt.gantt.width + spt.gantt.visible) {
        offset = - spt.gantt.width + spt.gantt.visible;
    }


    spt.gantt.offset = offset;

    var table = spt.gantt.table;
    spt.gantt.set_data( table );


    // clear out the datastructures
    spt.gantt.reset();
} 



spt.gantt.drag_scale_setup = function(evt, bvr, mouse_411)
{
    spt.gantt.drag_start_x = mouse_411.curr_x;

    spt.gantt.table = bvr.src_el.getParent('.spt_table_table');
    if (!spt.gantt.table)
        spt.gantt.table = bvr.src_el.getParent('.spt_table');

    spt.gantt.scroll_els = spt.gantt.table.getElements('.spt_gantt_scroll');

    var visible = spt.gantt.visible;

    var offset = spt.gantt.scroll_els[0].getStyle("margin-left");
    spt.gantt.offset = parseInt( offset.replace("px", "") );
    var width = spt.gantt.scroll_els[0].getStyle("width");
    spt.gantt.width = parseInt( width.replace("px", "") );
    spt.gantt.orig_width = parseInt( width.replace("px", "") );
    spt.gantt.percent = ((visible/2)-spt.gantt.offset) / spt.gantt.width;
}


spt.gantt.drag_scale_motion = function(evt, bvr, mouse_411)
{
    var scroll_els = spt.gantt.scroll_els;
    if (scroll_els.length > 0) {


        var diff = parseFloat(mouse_411.curr_x - spt.gantt.drag_start_x);

        var scale = 1 - (diff / 400);
        if (scale <= 0) {
            return;
        }
        var visible = spt.gantt.visible;

        var new_width = spt.gantt.orig_width / scale;
        var new_offset = - (spt.gantt.percent * new_width) + (visible/2);
        if (new_width < visible) {
            new_width = visible;
        }
        if (new_offset > 0) {
            new_offset = 0;
        }
        if (new_offset < -new_width+visible) {
            new_offset = -new_width+visible;
        }


        for (var i=0; i< scroll_els.length; i++) {
            var scroll_el = scroll_els[i];
            scroll_el.setStyle("width", new_width);
            scroll_el.setStyle("margin-left", new_offset);
        }

        spt.gantt.width = new_width;
        spt.gantt.offset = new_offset;
    }
}



spt.gantt.drag_scale_action = function(evt, bvr, mouse_411)
{
    var info = bvr.info;
    var percent_per_day = info['percent_per_day'];
    var pixel_per_day = percent_per_day * spt.gantt.width / 100;

    var table = spt.gantt.table;
  

    spt.gantt._process_title(table, pixel_per_day);

    spt.gantt.set_data( table );

    // clear out the datastructures
    spt.gantt.reset();
}

spt.gantt._process_title = function(table, pixel_per_day)
{
    // make week disappear after 7*1.5 = 11 pixels
    if (pixel_per_day < 1.5) {
        var week = table.getElement(".spt_gantt_week");
        if (week)
            spt.simple_display_hide( week );
    }
    else {
        var week = table.getElement(".spt_gantt_week");
        if (week)
            spt.simple_display_show( week );
    }
    if (pixel_per_day < 10) {
        var year = table.getElement(".spt_gantt_year");
        var day = table.getElement(".spt_gantt_day");
        //spt.simple_display_show( year );
        spt.simple_display_hide( day );
    }
    else {
        var year = table.getElement(".spt_gantt_year");
        var day = table.getElement(".spt_gantt_day");
        //spt.simple_display_hide( year );
        spt.simple_display_show( day );
    }
    if (pixel_per_day > 45) {
        var month = table.getElement(".spt_gantt_month");
        var wday = table.getElement(".spt_gantt_wday");
        //spt.simple_display_hide( month );
        spt.simple_display_show( wday );
    }
    else {
        var month = table.getElement(".spt_gantt_month");
        var wday = table.getElement(".spt_gantt_wday");
        //spt.simple_display_show( month );
        spt.simple_display_hide( wday );
    }
}




spt.gantt.accept_day = function(evt, bvr) {
    var src_el = bvr.src_el;
    src_el.setStyle("border", "solid 1px blue");
    var date_str = src_el.getAttribute('spt_date');
    //var cbk_vals = bvr.cbk_values;
   
    // rely on id for now
    var top_el = $(bvr.top_id);
    var json_dict = {};
    var json_el = top_el.getElement(".spt_json_data");
    if (json_el.value)
        json_dict = JSON.parse(json_el.value);
    
    if (bvr.col_name.test(/^bid/)) {
        if (bvr.col_name.test(/start/)){
            json_dict['bid_start_col'] =  bvr.col_name;
            json_dict['bid_start_value'] = date_str;
            
        }
        else {
            json_dict['bid_end_col'] =  bvr.col_name;
            json_dict['bid_end_value'] = date_str;
           
        }
    } else {
        if (bvr.col_name.test(/start/)){
            json_dict['actual_start_col'] =  bvr.col_name;
            json_dict['actual_start_value'] = date_str;
           
        }
        else {
            json_dict['actual_end_col'] =  bvr.col_name;
            json_dict['actual_end_value'] = date_str;
           
        }
    }
    //start is the corresponding element, TODO: change the Gantt Bar width
    var start = top_el.getElement('div[title='+bvr.col_name+']');
           
    var date_obj = spt.gantt._get_date(date_str);
    start.innerHTML = spt.gantt._get_label(date_obj);

    var key_code = spt.kbd.special_keys_map.ENTER;
    var value_wdg = top_el.getElement(".spt_gantt_value");
    value_wdg.value = date_str;

    json_el.value = JSON.stringify(json_dict);

    spt.dg_table.edit.widget = top_el;
    spt.dg_table.edit_cell_cbk( value_wdg, key_code );
    spt.popup.close('gantt_cal');

    //spt.panel.refresh(tbody, values, false);
}

    '''

