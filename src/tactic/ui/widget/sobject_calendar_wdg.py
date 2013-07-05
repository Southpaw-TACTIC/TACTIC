###########################################################
#
# Copyright (c) 2005-2008, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#

# Large calendar to display sobjects in

__all__ = ['SObjectCalendarWdg', 'BaseCalendarDayWdg', 'TaskCalendarDayWdg', 'SupervisorCalendarDayWdg', 'WorkHourCalendarDayWdg']

from pyasm.common import Common, jsonloads
from pyasm.biz import Pipeline
from pyasm.search import Search
from pyasm.web import Table, DivWdg, SpanWdg, WebContainer, Widget
from pyasm.widget import IconWdg, IconButtonWdg, BaseInputWdg, TextWdg
from tactic.ui.common import BaseRefreshWdg
from calendar_wdg import CalendarWdg

from dateutil import parser, rrule
from datetime import datetime, timedelta



class BaseCalendarDayWdg(BaseRefreshWdg):

    def __init__(my, **kwargs):
        super(BaseCalendarDayWdg, my).__init__(**kwargs)
        my.sobjects_index = []
        my.date = datetime.today()
        my.current_week = 0

    # FIXME: these are a bit wonky
    def set_sobjects_index(my, indexes):
        my.sobjects_index = indexes


    def set_current_week(my, current_week):
        my.current_week = current_week


    def get_week_left_wdg(my, week):
        pass

    def get_week_right_wdg(my, week):
        pass

    def set_date(my, date):
        my.date = date

    def get_display(my):
        div = DivWdg()
        return div


class TaskCalendarDayWdg(BaseCalendarDayWdg):

    def init(my):
        my.sobjects_drawn = {}
        my.date = datetime.today()
        my.sobject_display_expr = my.kwargs.get('sobject_display_expr')

    # FIXME: these are a bit wonky
    def set_sobjects_index(my, indexes):
        my.sobjects_index = indexes

    def set_date(my, date):
        my.date = date

    def get_display(my):
        top = DivWdg()

        # check if it is the first day of the week and then try to cascade
        # the indexes up
        wday = my.date.strftime("%w")
        if wday == "0":
            first_day = True
        else:
            first_day = False

        num_today = 0
        for index, sobject in enumerate(my.sobjects_index):
            if sobject not in my.sobjects:
                continue
            num_today += 1

        if not num_today:
            no_tasks = DivWdg()
            no_tasks.add_style("height: 60px")
            no_tasks.add_style("width: 60px")
            no_tasks.add("&nbsp;")
            top.add(no_tasks)

            color = top.get_color("background", [-2, -10, -10])
            top.add_style("background: %s" % color)
            top.add_style("opacity: 0.5")

        else:
            for index, sobject in enumerate(my.sobjects_index):

                content_wdg = DivWdg()
                content_wdg.add_style("margin: 1px 0px 1px 0px")
                content_wdg.add_style("padding: 1px 3px 1px 3px")
                top.add(content_wdg)

                if sobject not in my.sobjects:
                    content_wdg.add("&nbsp;")
                    continue

                if not first_day and my.sobjects_drawn.get(sobject) == True:
                    display_value = "&nbsp;"
                else:
                    if my.sobject_display_expr:
                        display_value = Search.eval(my.sobject_display_expr, [sobject], single=True)
                    else:
                        display_value = my.get_display_value(sobject)
                    my.sobjects_drawn[sobject] = True

                color = my.get_color(sobject, index)
                content_wdg.add_style("background: %s" % color)

                content_wdg.add(display_value)


        return top



    def get_display_value(my, sobject):

        # how to display empty if none existant
        # this expression cuts off after 30 chars doesn't work with non ASCII char
        # as it induces unexpected end of data error
        expression = '''
        {@GET(.process)}
        {@IF( @GET(.completion)>0, '('+@GET(.completion)+')', '')}
        {@IF( @GET(.description)=='', '', ': '+@GET(.description)),|^(.{30})|}
        '''
        expression = None
        if expression:
            value = Search.eval(expression, sobject, single=True)
        else:
            context = sobject.get_value('context')
            if not context:
                context = "[no context]"

            description = sobject.get_value('description')
            completion = sobject.get_value('completion')
            if completion:
                completion = "%s%%" % completion

            if len(description) > 30:
                description = "%s ..." % description[:30]
            if completion:
                value = "%s (%s): %s" % (context, completion, description)
            else:
                value = "%s: %s" % (context, description)

        return value



    def get_color(my, sobject, index):

        colors = ['#666','#777','#888']
        default_color = colors[index%3]

        parent = sobject.get_parent()
        if not parent:
            return default_color


        pipeline_code = parent.get_value("pipeline_code", no_exception=True)
        if not pipeline_code:
            return default_color

        pipeline = Pipeline.get_by_code(pipeline_code)
        if not pipeline:
            return default_color

        process_name = sobject.get_value("process")
        if not process_name:
            process_name = sobject.get_value("context")

        # get the process
        process = pipeline.get_process(process_name)
        if not process:
            return default_color

        color = process.get_color()
        if not color:
            return default_color



        return color

    def get_week_left_wdg(my, week):
        pass


    def alter_search(my, search):
        '''default to just filter by assigned'''
        assigned = my.kwargs.get("assigned")
        supervisor = my.kwargs.get("supervisor")

        if assigned:
            search.add_filter("assigned", assigned)

        elif supervisor:
            search.add_filter("supervisor", assigned)

        else:
            search.add_user_filter(column='assigned')



class WorkHourCalendarDayWdg(BaseCalendarDayWdg):

    def init(my):
        my.week_totals = {}

    def get_display(my):
        div = DivWdg()


        total_straight = 0
        for index, sobject in enumerate(my.sobjects):
            straight = sobject.get_value("straight_time")
            if straight:
                total_straight += float(straight)

        straight_div = DivWdg()
        div.add(straight_div)
        straight_div.add("%s" % total_straight)
        if not total_straight:
            straight_div.add_style("opacity: 0.3")
        else:
            week_total = my.week_totals.get(my.current_week)
            if week_total == None:
                week_total = 0
            week_total += total_straight
            my.week_totals[my.current_week] = week_total


        div.add_style("padding: 5px")
        div.add_style("text-align: right")
        div.add_style("width: 90")


        if not total_straight:
            color = div.get_color("background", [10, -10, -10])
            div.add_style("background: %s" % color)
            div.add_style("opacity: 0.5")
            div.add_style("font-style: italic")
        else:
            color = div.get_color("background", [-20, 30, -20])
            div.add_style("background: %s" % color)
            div.add_style("font-weight: bold")

        return div


    def alter_search(my, search):

        login = my.kwargs.get("login")
        if login:
            search.add_filter("login", login)



    def get_week_left_wdg(my, week):
        top = DivWdg()
        top.add_style("margin-top: 28px")

        for category in ['hours']:

            content_wdg = DivWdg()
            content_wdg.add("%s: " % category)
            content_wdg.add_style("margin-right: 8px")

            #content_wdg.add_style("width: 120px")

            top.add(content_wdg)

        return top


    def get_week_right_wdg(my, week):
        top = DivWdg()
        #top.add("total: %s" % week)
        return top

class SupervisorCalendarDayWdg(TaskCalendarDayWdg):

    def get_color(my, sobject, index):

        assigned = sobject.get_value("assigned")
        color = my.get_color_by_login(assigned)

        if not color:
            colors = ['#666','#777','#888']
            color = colors[index%3]
        return color


    def get_color_by_login(my, login):
        colors = {
            'garth': '#644',
            'cindy': '#464',
            'gary':  '#446',
            'albert':'#466',
            'joe':'#646',
        }
        color = colors.get(login)
        return color


    def get_week_left_wdg(my, week):
        top = DivWdg()

        for assigned in ['albert', 'joe', 'garth']:

            content_wdg = DivWdg()
            content_wdg.add_style("margin: 1px 0px 1px 0px")
            content_wdg.add_style("padding: 1px 3px 1px 3px")
            content_wdg.add(assigned)

            color = my.get_color_by_login(assigned)
            content_wdg.add_style("background: %s" % color)
            content_wdg.add_style("width: 120px")

            top.add(content_wdg)

        return top


    def alter_search(my, search):
        search.add_order_by('assigned')
        search.add_user_filter(column='supervisor')



      



class SObjectCalendarWdg(CalendarWdg):

    ARGS_KEYS = {
        #'expression': 'expression used to get the tasks'
        'start_date_col': 'Start date column',
        'end_date_col': 'End date column',
        'handler': 'handler class to display each day',
        'search_type': 'search type to search for'
    }



    def handle_search(my):

        my.search_type = my.kwargs.get("search_type")
        if not my.search_type:
            my.search_type = 'sthpw/task'

        my.op_filters = my.kwargs.get("filters")
        if my.op_filters:
            if isinstance(my.op_filters, basestring):
                my.op_filters = eval(my.op_filters)


        my.start_column = my.kwargs.get('start_date_col')
        if not my.start_column:
            my.start_column = 'bid_start_date'

        my.end_column = my.kwargs.get('end_date_col')
        if not my.end_column:
            my.end_column = 'bid_end_date'

       
        search = Search(my.search_type)
        if my.op_filters:
            search.add_op_filters(my.op_filters)
        search.add_op('begin')

        if my.handler:
            my.handler.alter_search(search)

        search.add_op('or')




        my.start_date = datetime(my.year, my.month, 1)
        next_month = my.month+1
        next_year = my.year
        if next_month > 12:
            next_month = 1
            next_year += 1

        my.end_date = datetime(next_year, next_month, 1)
        my.end_date = my.end_date - timedelta(days=1)


        # outer begin
        search.add_op('begin')
        
        search.add_op('begin')
        search.add_date_range_filter(my.start_column, my.start_date, my.end_date)
        search.add_date_range_filter(my.end_column, my.start_date, my.end_date)

        search.add_op('or')
        search.add_op('begin')
        search.add_filter(my.start_column, my.start_date, op='<=')
        search.add_filter(my.end_column, my.end_date, op='>=')
        search.add_op('and')
        
        search.add_op('or')


        search.add_order_by(my.start_column)

        my.sobjects = search.get_sobjects()



    def init(my):
        super(SObjectCalendarWdg,my).init()

        custom_view = my.kwargs.get('view')
        my.custom_layout = None
        if custom_view:
            from tactic.ui.panel import CustomLayoutWdg
            #custom_kwargs = my.kwargs.copy()
            custom_kwargs = my.kwargs.get("kwargs")
            if not custom_kwargs:
                custom_kwargs = {}
            elif isinstance(custom_kwargs, basestring):
                custom_kwargs = eval(custom_kwargs)
            custom_kwargs['view'] = custom_view
            my.custom_layout = CustomLayoutWdg(**custom_kwargs)
            class_name = "tactic.ui.widget.BaseCalendarDayWdg"

        else:


            class_name = my.kwargs.get('handler')
            if not class_name:
                class_name = 'tactic.ui.widget.TaskCalendarDayWdg'

            my.custom_layout = None

        my.handler = Common.create_from_class_path(class_name, [], my.kwargs)


        my.sobject_display_expr = my.kwargs.get('sobject_display_expr')

        # set the border style
        my.kwargs['border_type'] = 'all'



        my.handle_search()

        my.width = my.kwargs.get("cell_width")
        if not my.width:
            my.width = '120px'
        my.height = my.kwargs.get("cell_height")
        if not my.height:
            my.height = '120px'


        my.top_wdg.add_style("width: 100%")


        # preprocess the sobjects so that they are order by date
        my.date_sobjects = {}

        # get all of the weeks in this month
        my.sobjects_week_index = []
        for i in my.weeks:
            my.sobjects_week_index.append([])

        for index, sobject in enumerate(my.sobjects):

            start_date = sobject.get_value(my.start_column)
            if not start_date:
                continue
            start_date = parser.parse(start_date)

            end_date = sobject.get_value(my.end_column)
            if not end_date:
                continue
            end_date = parser.parse(end_date)

            for i, week in enumerate(my.weeks):
                first_day = week[0]
                first_day = datetime(first_day.year, first_day.month, first_day.day)
                last_day = week[6] + timedelta(days=1)
                last_day = datetime(last_day.year, last_day.month, last_day.day)

                is_in_week = False

                # if this sobject falls in this week
                if start_date >= first_day and start_date < last_day:
                    is_in_week = True
                elif end_date >= first_day and end_date < last_day:
                    is_in_week = True
                elif start_date < first_day and end_date > last_day:
                    is_in_week = True

                if is_in_week:
                    my.sobjects_week_index[i].append(sobject)



            # for each day in the sobject's timeline, add it to the appropriate
            # day list
            days = list(rrule.rrule(rrule.DAILY, dtstart=start_date, until=end_date))
            for date in days:

                date_str = date.strftime("%Y-%m-%d")

                sobj_list = my.date_sobjects.get(date_str)
                if not sobj_list:
                    # create a new list for that day
                    sobj_list = []
                    my.date_sobjects[date_str] = sobj_list 

                sobj_list.append(sobject)


        my.current_week = -1



    def get_header_wdg(my):
        div = DivWdg()
        div.add_gradient("background", "background", 0, -10)
        div.add_style("font-size: 14px")
        div.add_style("font-weight: bold")
        div.add_style("padding: 2px")

        table = Table()
        table.add_style("margin-left: auto")
        table.add_style("margin-right: auto")
        table.add_color("color", "color")

        table.add_row()

        # add the month navigators
        date_str = "%s, %s" % (my.MONTHS[my.month-1], my.year)
        month_wdg = DivWdg()
        month_wdg.add_style("font-size: 14px")
        month_wdg.add_style("width: 150px")
        month_wdg.add(date_str)


        prev_month_wdg = my.get_prev_month_wdg()
        next_month_wdg = my.get_next_month_wdg()

        table.add_cell(prev_month_wdg)
        td = table.add_cell(month_wdg)
        td.add_style("text-align: center")
        table.add_cell(next_month_wdg)

        div.add(table)

        return div



    def get_week_left_wdg(my, week):
        return my.handler.get_week_left_wdg(week)


    def get_week_right_wdg(my, week):
        return my.handler.get_week_right_wdg(week)






    def get_day_wdg(my, month, day):

        # find the day of the week
        wday = day.strftime("%w")
        # if it's the first day ...
        if wday == "0":
            my.current_week += 1

        sobjects_week_index = my.sobjects_week_index[my.current_week]
        my.handler.set_sobjects_index( sobjects_week_index )
        my.handler.set_current_week(my.current_week)

        sobjects = my.date_sobjects.get(str(day))

        div = DivWdg()
       
        #color = ['#333', '#353535']
        #div.add_style("background: %s" % color[day.day % 2])
        div.add_styles("vertical-align: top")
        div.add_class("spt_calendar_day")
        div.add_class("hand")
        if my.custom_layout:
            my.custom_layout.kwargs['day_obj'] = day
            my.custom_layout.kwargs['day'] = str(day)
            if sobjects:
                # this causes mako processing error complaining about timestamp
                # send in just the search_keys for the day for now

                #sobject_dict_list = [ x.get_sobject_dict() for x in sobjects]
                #my.custom_layout.kwargs['search_objects'] = sobject_dict_list 
                sobject_keys = [ x.get_search_key() for x in sobjects]
                my.custom_layout.kwargs['search_keys'] = sobject_keys
            wdg = my.custom_layout.get_buffer_display()
            my.custom_layout.kwargs['search_keys'] = []
            div.add(wdg)
            return div


        day_div = DivWdg()
        day_div.add(day.day)
        day_div.add_style("font-size: 14px")
        day_div.add_style("padding: 3px 0 3px 5px")
        div.add( day_div )

        #div.add_style("text-align: center")
        #div.add_style("text-align: left")
        div.add_style("width: %s" % my.width);
        div.add_style("min-height: %s" % my.height);
        div.add_style("overflow: hidden");
        div.add_style("padding: 2px 0 2px 0")

        div.add_color("color", "color")
        div.add_style("vertical-align: top")

        

        if sobjects:
            #ids = "".join( [ "['id','%s']" % x.get_id() for x in sobjects ])
            ids = [ str(x.get_id()) for x in sobjects ]
            ids_filter = "['id' ,'in', '%s']" %'|'.join(ids) 
            expression = "@SOBJECT(sthpw/task%s)" % ids_filter
            div.add_behavior( {
                'type': "click_up",
                'cbjs_action': '''
                var class_name = 'tactic.ui.panel.FastTableLayoutWdg';
                var title = '%s';
                var kwargs = {
                    'search_type': '%s',
                    'view': 'table',
                    'show_insert': 'false',
                    'expression': "%s"
                };
                spt.app_busy.show("Loading...")
                setTimeout(function() {
                    spt.panel.load_popup( title, class_name, kwargs );
                    spt.app_busy.hide();
                }, 100)

                ''' % (str(day),my.search_type, expression ),
            } )


            content = DivWdg()
            content.add_style("vertical-align: top")
            content.add_class("spt_calendar_day_content")

            content.add_style("height: 100%")
            content.add_style("width: 400px")
            content.add_style("min-height: %s" % my.height);

            my.handler.set_sobjects(sobjects)
        else:
            content = DivWdg()
            content.add_style("vertical-align: top")
            content.add_style("height: 100%")
            content.add_style("width: 400px")
            content.add_style("min-height: %s" % my.height);

            my.handler.set_sobjects([])


        my.handler.set_date(day)

        content.add( my.handler.get_buffer_display() )

        div.add(content)



        # put a different color for days that are not in the current month
        if day.month != month:
            div.add_style("color: #c22")
            div.add_style("opacity: 0.5")


        today = datetime.today()
       

        # store date like the database does YYYY-MM-DD
        date_str = "%04d-%02d-%02d" % (day.year, day.month, day.day)
        div.add_attr('spt_date', date_str)
        div.add_class('spt_date_day')


        color1 = div.get_color("background")
        color2 = div.get_color("background", -10)

        if day.year == today.year and day.month == today.month and day.day == today.day:
            div.add_color("background", "background", [-10, -10, 20])
            color1 = div.get_color("background", [-10, -10, 20])

        

        div.add_event("onmouseover", "$(this).setStyle('background','%s')" % color2)
        div.add_event("onmouseout", "$(this).setStyle('background','%s')" % color1)

        return div


__all__.append("ActivityCalendarWdg")
class ActivityCalendarWdg(SObjectCalendarWdg):

    def handle_search(my):
        login = my.kwargs.get("login")
        #login = None


        my.start_date = datetime(my.year, my.month, 1)
        next_month = my.month+1
        next_year = my.year
        if next_month > 12:
            next_month = 1
            next_year += 1

        my.end_date = datetime(next_year, next_month, 1)


        search = Search("sthpw/task")
        if login:
            search.add_filter("assigned", login)
        search.add_filter("bid_end_date", my.start_date, op=">")
        search.add_filter("bid_end_date", my.end_date, op="<")
        my.task_count = search.get_count()
        my.tasks = search.get_sobjects()
        my.tasks_count = {}
        for task in my.tasks:
            date = task.get_value("bid_end_date")
            date = parser.parse(date)
            date = datetime(date.year, date.month, date.day)

            count = my.tasks_count.get(str(date))
            if not count:
                count = 0

            count += 1
            my.tasks_count[str(date)] = count



        search = Search("sthpw/snapshot")
        if login:
            search.add_filter("login", login)
        search.add_filter("timestamp", my.start_date, op=">")
        search.add_filter("timestamp", my.end_date, op="<")
        my.snapshot_count = search.get_count()
        my.snapshots = search.get_sobjects()
        my.snapshots_count = {}
        for snapshot in my.snapshots:
            date = snapshot.get_value("timestamp")
            date = parser.parse(date)
            date = datetime(date.year, date.month, date.day)

            count = my.snapshots_count.get(str(date))
            if not count:
                count = 0
            count += 1
            my.snapshots_count[str(date)] = count




        search = Search("sthpw/task")
        if login:
            search.add_filter("assigned", login)
        search.add_filter("timestamp", my.start_date, op=">")
        search.add_filter("timestamp", my.end_date, op="<")
        my.task_count = search.get_count()




        search = Search("sthpw/note")
        if login:
            search.add_filter("login", login)
        search.add_filter("timestamp", my.start_date, op=">")
        search.add_filter("timestamp", my.end_date, op="<")
        my.note_count = search.get_count()
        my.notes = search.get_sobjects()
        my.notes_count = {}
        for note in my.notes:
            date = note.get_value("timestamp")
            date = parser.parse(date)
            date = datetime(date.year, date.month, date.day)

            count = my.notes_count.get(str(date))
            if not count:
                count = 0
            count += 1
            my.notes_count[str(date)] = count




        search = Search("sthpw/work_hour")
        if login:
            search.add_filter("login", login)
        search.add_filter("day", my.start_date, op=">=")
        search.add_filter("day", my.end_date, op="<=")
        my.work_hour_count = search.get_count()
        my.work_hours = search.get_sobjects()
        my.work_hours_count = {}
        for work_hour in my.work_hours:
            date = work_hour.get_value("day")
            date = parser.parse(date)
            date = datetime(date.year, date.month, date.day)

            total = my.work_hours_count.get(str(date))
            if not total:
                total = 0

            straight_time = work_hour.get_value("straight_time")
            if straight_time:
                total += straight_time
            my.work_hours_count[str(date)] = straight_time




    def get_day_wdg(my, month, day):

        div = DivWdg()
        div.add_style("width: 120px")
        div.add_style("height: 150px")
        div.add_style("padding: 5px")


        # disabled until further development is done on WeekWdg
        """
        div.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var class_name = 'tactic.ui.widget.week_wdg.WeekWdg';
            spt.panel.load_popup("Week", class_name);
            '''
        } )
        """

        # if the day is today
        today = datetime.today()
        if day.year == today.year and day.month == today.month and day.day == today.day:
            div.add_color("background", "background", [-20, -20, 20])
            div.add("[%s]" % day.day)

        elif day.weekday() in [5, 6]:
            div.add_color("background", "background", -3)
            if day.month != my.month:
                div.add("<i style='opacity: 0.3'>[%s]</i>" % day.day)
            else:
                div.add("[%s]" % day.day)

        # if the month is different than today
        elif day.month != my.month:
            #div.add_color("background", "background", [-5, -5, -5])
            div.add("<i style='opacity: 0.3'>[%s]</i>" % day.day)


        else:
            div.add("[%s]" % day.day)


        div.add("<br/>")
        div.add("<br/>")


        key = "%s-%0.2d-%0.2d 00:00:00" % (day.year, day.month, day.day)


        line_div = DivWdg()
        div.add(line_div)
        line_div.add_style("padding: 3px")
        icon = IconWdg("Number of task due", IconWdg.CALENDAR)
        line_div.add(icon)
        num_tasks = my.tasks_count.get(key)
        if not num_tasks:
            num_tasks = 0
            line_div.add_style("opacity: 0.15")
            line_div.add_style("font-style: italic")
        line_div.add("%s task/s due<br/>" % num_tasks)




        line_div = DivWdg()
        div.add(line_div)
        line_div.add_style("padding: 3px")
        icon = IconWdg("Number of check-ins", IconWdg.PUBLISH)
        line_div.add(icon)
        num_snapshots = my.snapshots_count.get(key)
        if not num_snapshots:
            num_snapshots = 0
            line_div.add_style("opacity: 0.15")
            line_div.add_style("font-style: italic")
        line_div.add("%s check-in/s<br/>" % num_snapshots )


        line_div = DivWdg()
        div.add(line_div)
        line_div.add_style("padding: 3px")
        icon = IconWdg("Number of notes", IconWdg.NOTE)
        line_div.add(icon)
        num_notes = my.notes_count.get(key)
        if not num_notes:
            num_notes = 0
            line_div.add_style("opacity: 0.15")
            line_div.add_style("font-style: italic")
        line_div.add("%s note/s<br/>" % num_notes)


        line_div = DivWdg()
        div.add(line_div)
        line_div.add_style("padding: 3px")
        icon = IconWdg("Work Hours", IconWdg.CLOCK)
        line_div.add(icon)
        work_hours = my.work_hours_count.get(key)
        if not work_hours:
            work_hours = 0
            line_div.add_style("opacity: 0.15")
            line_div.add_style("font-style: italic")
        line_div.add("%s work hours<br/>" % work_hours)


        #div.add("%s tasks completed<br/>" % my.task_count)
        #div.add("%s notes entered<br/>" % my.notes_count)
        #div.add("%s work hours<br/>" % my.work_hours_count)


        return div






