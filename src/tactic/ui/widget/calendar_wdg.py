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

# This module contains a collection of generalized utility widgets

__all__ = ['CalendarWdg', 'CalendarMonthWdg', 'CalendarTimeWdg', 'CalendarInputWdg', 'TimeInputWdg', 'CalendarIntervalInputWdg']

import locale
from pyasm.common import Date, Common, Config, Container, SPTDate
from pyasm.biz import NamingUtil, ProdSetting
from pyasm.web import Widget, Table, DivWdg, SpanWdg, WebContainer, FloatDivWdg, HtmlElement
from pyasm.widget import IconWdg, IconButtonWdg, TextWdg, HiddenWdg, BaseInputWdg, SelectWdg, ProdIconButtonWdg
from pyasm.search import SObject
from tactic.ui.common import BaseRefreshWdg

from .button_new_wdg import IconButtonWdg, ButtonNewWdg

from datetime import datetime, timedelta
from dateutil import parser

try:
    from calendar import Calendar
    HAS_CALENDAR = True
except ImportError as e:
    HAS_CALENDAR = False 
    
import calendar



class CalendarWdg(BaseRefreshWdg):

    WEEKDAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday','Saturday','Sunday']

    MONTHS = ['January','February','March','April','May','June','July','August','September','October','November','December']

    ARGS_KEYS = {
        'year': 'The starting year of the calendar',
        'month': 'The starting month of the calendar',
        'size': 'full|abbr|letter - determines the # of letters displayed on the month',
        'is_refresh': 'true|false - determines whether to draw the top node or not',
        'day_cbk': 'callback when a day is clicked',
        'name': 'name of the hidden input that is set',
        'search_key' : 'search_key for sobject that contains this date',
        'tbody_id':  'tbody_id',
        'col_name': 'col_name for this date entry',

        'first_day_of_week': 'integer indicating first day of the week',
        'layout_version': '1 or 2'
       
               
    }

    def init(self):
        web = WebContainer.get_web()

        self.is_refresh = False
        is_refresh = web.get_form_value("is_refresh")
        if not is_refresh:
            is_refresh = self.kwargs.get('is_refresh')
        if is_refresh in  ["true", True]:
            self.is_refresh = True

        
        self.top_wdg = DivWdg()
        self.top_wdg.add_style("z-index: 100")
        css_class = self.kwargs.get('css_class')

        if not css_class:
            css_class = "spt_calendar_top"
        self.top_wdg.add_class(css_class)
        self.top_wdg.add_style("border-radius: 10px")
        self.top_wdg.add_style("padding: 5px;")
        self.top_wdg.add_style("box-shadow: 0px 10px 15px #aaa")
        self.top_wdg.add_style("-moz-user-select: none")

        #self.top_wdg.add_style("background: #444")
        self.top_wdg.add_color("background", "background")
        self.top_wdg.add_color("color", "color")
        #self.top_wdg.add_style("padding: 3px")
        self.top_wdg.set_id('calendar')
        self.set_as_panel(self.top_wdg)

        self.day_cbks = []
        day_cbk = self.kwargs.get("day_cbk")
        if day_cbk:
            self.day_cbks.insert(0, day_cbk)



        date = Date()
        

        # the 3 cbk_values are search_key, tbody_id, col_name
        self.search_key = web.get_form_value("search_key")
        self.top_id = web.get_form_value("top_id")
        self.col_name = web.get_form_value("col_name")
        self.date = web.get_form_value("date")

        if not self.date:
            self.date = self.kwargs.get("date")

        self.year, self.month = '', ''
        if self.date:
            date = Date(self.date)
            self.year = date.get_year()
            self.month = date.get_month()
        if not self.year:    
            self.year = web.get_form_value("year")
        if not self.year:
            self.year = self.kwargs.get('year')
        if not self.year:
            self.year = date.get_year()
        
        
        if not self.month:
            self.month = web.get_form_value("month")
        if not self.month:
            self.month = self.kwargs.get('month')
        if not self.month:
            # PREV (this caused bug of cal wdg being a month in the future):  self.month = int(date.get_month())+1
            self.month = int(date.get_month())
        
        self.year = int(self.year)    
        self.month = int(self.month)

        self.weeks = self.get_weeks(self.year, self.month)



    def add_style(self, style):
        self.top_wdg.add_style(style)


    def add_day_cbk(self, cbk):
        self.day_cbks.append(cbk)


    # HACK to get it to be an input!!
    def get_option(self, name):
        return self.kwargs.get(name)

    def get_title(self):
        return self.get_name()


   

    def get_display(self):
        # handle size
        size_str = self.kwargs.get("size")
        if size_str == "full":
            self.size = 0
        elif size_str == 'abbr':
            self.size = 2
        elif size_str == 'letter':
            self.size = 1
        else:
            self.size = 2


        # add some boundary conditions
        if self.month < 1:
            self.month = 12
            self.year -= 1

        elif self.month > 12:
            self.month = 1
            self.year += 1

        # remember the new values
        self.kwargs['year'] = self.year
        self.kwargs['month'] = self.month
        calendar = self.get_calendar_wdg(self.year, self.month)
        if self.is_refresh:
            return calendar

        style = HtmlElement.style('''
        .spt_calendar_day:hover {
            background: #eee;
        }

        .spt_month_wdg:hover {
            background: #eee;
        }
        ''')
        self.top_wdg.add(style)
        inner = DivWdg()
        self.top_wdg.add(inner)
      
        inner.add( calendar )

        if not Container.get_dict("JSLibraries", "spt_calendar"):
            self.top_wdg.add_behavior( {
                'type': 'load',
                'cbjs_action': '''
            spt.calendar = {}

            // for now, refresh is always set to true by default when spt.calendar.get() is called to
            // get a new calendar
            spt.calendar.current;
            spt.calendar.get = function(refresh) {
                if ( typeof(refresh) == 'undefined' )
                    refresh = true;
                if (!refresh && spt.calendar.current) {
                    return spt.calendar.current;
                }
                var temp = document.getElement('.spt_calendar_template_top');
                var new_cal;
                if (temp) { 
                    new_cal = spt.behavior.clone(temp);
                    new_cal.removeClass('spt_calendar_template_top');
                    new_cal.addClass('spt_calendar_top');
                    new_cal.setStyle("position","absolute");
                    spt.calendar.current = new_cal
                }
                return new_cal;
            }

            spt.Environment.get().add_library("spt_calendar");
                ''' } )



        """NOTE: comment this out for now, doesn't seem to be used
        self.top_wdg.add_relay_behavior( {
            'type': 'click',
            'bvr_match_class': 'spt_calendar_day',
            'cbjs_action': '''
        spt.calendar.set_day = function(evt, bvr)
        {
            var src_el = bvr.src_el;
            var value = src_el.getAttribute("spt_date");
            input = spt.get_cousin(src_el, ".spt_calendar_top", ".spt_calendar_date")
            input.value = value;

            var top = spt.get_parent(src_el, ".spt_calendar_top");
            top.setStyle("display", "none");
        }
        '''
        })
        """


        if self.kwargs.get("is_refresh") in [True, 'true']:
            return inner
        else:
            return self.top_wdg




    def get_weeks(self, year, month):
        #HAS_CALENDAR = False

        if HAS_CALENDAR:
            """
            first_day_of_week = self.kwargs.get("first_day_of_week")
            if first_day_of_week or first_day_of_week == 0:
                first_day_of_week = int(first_day_of_week)
            else:
                first_day_of_week = Config.get_value("install","first_day_of_week")
                if first_day_of_week == '':
                    first_day_of_week = 6
                else:
                    first_day_of_week = int(first_day_of_week)

            self.cal = Calendar(first_day_of_week)
            weeks = self.cal.monthdatescalendar(self.year, month)
            print("weeks: ", weeks)
            print
            """

            from dateutil.rrule import rrule, DAILY, MO, TU, WE, TH, FR
            from datetime import date, datetime, timedelta
            start = datetime(year=year, month=month, day=1)
            weekday = start.weekday()
            start = start - timedelta(days=weekday+1)

            days_in_week = 7
            num_weeks = 6
            days = list(rrule(freq=DAILY, count=days_in_week*num_weeks, dtstart=start))
            weeks = []
            for i in range(0, num_weeks):
                week = days[i*days_in_week:i*days_in_week+days_in_week]
                date_week = []
                for day in week:
                    day = date(day.year,day.month,day.day)
                    date_week.append(day)

                weeks.append(date_week)


        else:
            # for Python 2.4, build it up manually
            class Day(object):
                def weekday(self):
                    if self.day == 0:
                        return 0
                    weekday = self.day - 1
                    return weekday

            weeks_old = calendar.monthcalendar(self.year, month)
            weeks = []
            for week_old in weeks_old:
                week = []
                for day_old in week_old:
                    day = Day()
                    if day_old == 0:
                        day.month = 0
                        day.day = 0
                    else:
                        day.month = month
                        day.day = day_old
                    day.year = year

                    week.append(day)
                weeks.append(week)

        return weeks


    def get_legend_wdg(self):
        return None


    def get_calendar_wdg(self, year, month):
        self.year = year
        self.month = month

        weeks = self.weeks

        widget = DivWdg()

        # add the header widget
        if self.kwargs.get("show_header") not in ['false', False]:
            header = self.get_header_wdg()
            widget.add(header)


        legend_wdg = self.get_legend_wdg()
        if legend_wdg:
            widget.add(legend_wdg)
            legend_wdg.add_border()
            legend_wdg.add_style("margin-top: -1px")



        # add the main table
        table = Table()
        widget.add(table)
        table.add_row()
        table.add_color("color", "color")
        table.add_style("width: 100%")
        table.add_style("table-layout: fixed")
        table.add_style("font-size: inherit")

        #table.add_style("margin-left: auto")
        #table.add_style("margin-right: auto")

        if self.kwargs.get("show_header") not in ['false', False]:
            table.add_style("margin-top: -1px")


        # get all of the day widgets
        day_wdgs = []

        # get the various left widgets
        left_wdgs = []
        has_left_wdgs = False
        for week in weeks:
            left_wdg = self.get_week_left_wdg(week)
            if left_wdg:
                has_left_wdgs = True
            left_wdgs.append(left_wdg)

        # get the various left widgets
        right_wdgs = []
        has_right_wdgs = False
        for week in weeks:
            right_wdg = self.get_week_right_wdg(week)
            if right_wdg:
                has_right_wdgs = True
            right_wdgs.append(right_wdg)



        # add the various cells of the month
        week = weeks[0]
        if has_left_wdgs:
            table.add_cell("&nbsp;")
        for day in week:
            td = table.add_cell()
            td.add(self.get_day_header_wdg(day) )

        if has_right_wdgs:
            table.add_cell("&nbsp;")

        border_type = self.kwargs.get("border_type")
        if not border_type:
            border_type = 'bottom'

        # add day_cbks
        for cbk in self.day_cbks:
            behavior = {
                'type': 'click_up',
                'cbjs_action': cbk, 
                'bvr_match_class': 'spt_calendar_day', 
                'search_key' : self.search_key,
                'top_id' : self.top_id,
                'col_name': self.col_name
            }
            table.add_relay_behavior(behavior)
        
        for i, week in enumerate(weeks):
            table.add_row()
            
            if has_left_wdgs:
                left_wdg = left_wdgs[i]
                if left_wdg:
                    td = table.add_cell(left_wdg)
                    td.add_style('vertical-align: middle')
                    td.add_style("width: 1px")
                else:
                    td.add_cell("&nbsp;")

            for day in week:
                td = table.add_cell()
                td.add_style("padding: 0px")
                td.add(self.get_day_wdg(month, day))
                td.add_style("vertical-align: middle")
                td.add_style("width: 28px")
                td.add_style("height: 28px")
                #td.add_style("display: block")
                # td.add_style("float: left")
                #td.add_style("overflow: hidden")

            if has_right_wdgs:
                right_wdg = right_wdgs[i]
                if right_wdg:
                    td = table.add_cell(right_wdg)
                    td.add_style('vertical-align: top')
                else:
                    td.add_cell("&nbsp;")




        return widget



    def get_header_wdg(self):

        month = self.month
        year = self.year

        header = DivWdg()
        header.add_style("display: flex")
        header.add_color("color", "color")
        header.add_style("margin: 5px 0px")
        header.add_style("align-items: center")
        header.add_style("justify-content: space-between")



        # add the month navigators
        prev_month_wdg = self.get_prev_month_wdg()
        next_month_wdg = self.get_next_month_wdg()


        # add the today icon
        today_icon = self.get_today_icon()
        header.add( today_icon )



        date_str = "%s %s" % (self.MONTHS[month-1], self.year)
        month_wdg = DivWdg()
        month_wdg.add_class("btn spt_month_wdg hand")
        month_wdg.add_color("color", "color")
        month_wdg.add(date_str)


        month_wdg.add_behavior({
            'type': 'click_up',
            'name': self.col_name,
            'year': self.year,
            'month': self.month,
            'cbjs_action': '''
            var el = bvr.src_el.getParent('.spt_calendar_top');
            var class_name = 'tactic.ui.widget.CalendarMonthWdg';
            var kwargs = {
                name: bvr.name,
                month: bvr.month,
                year: bvr.year
            };
            spt.panel.load(el, class_name, kwargs);
            '''
        })


        # add the navigator
        td = DivWdg()
        header.add(td)
 
        month_nav = DivWdg()
        month_nav.add_style("margin: auto")
        month_nav.add_style("display: flex")
        month_nav.add_style("justify-content: space-between")
        month_nav.add_style("align-items: center")
        td.add(month_nav)
        month_nav.add(prev_month_wdg)
        month_nav.add(month_wdg)
        month_wdg.add_style("text-align: center")
        month_wdg.add_style("width: 100px")
        month_wdg.add_style("font-weight: bold")
        month_wdg.add_style("border-radius: 5px")
        month_nav.add( next_month_wdg)



        # add the close icon
        close_icon = self.get_close_icon()
        header.add( close_icon )
        close_icon.add_style("padding-right: 0px")

        return header



    def get_prev_month_wdg(self):
        prev_month = self.month - 1
        prev_year = self.year
        if prev_month < 1:
            prev_month = 12
            prev_year -= 1


        prev_month_wdg = ButtonNewWdg( title="Prev Month", icon="FAS_CHEVRON_LEFT", width=25 )

        prev_month_wdg.add_behavior( {
            'type': "click_up",
            'cbjs_action':  '''
                var kwargs = {async: false, fade: false};
                var el = bvr.src_el.getParent('.spt_calendar_top');
                spt.panel.refresh(el, {year: '%s', month: '%s', is_refresh: 'true', 
                        'search_key': '%s', 'top_id': '%s',
                    'col_name': '%s'}, kwargs );
            ''' % (prev_year, prev_month, self.search_key, self.top_id, self.col_name )
        })
        return prev_month_wdg


    def get_next_month_wdg(self):
        next_month = self.month + 1
        next_year = self.year
        if next_month > 12:
            next_month = 1
            next_year += 1


        next_month_wdg = ButtonNewWdg( icon="FAS_CHEVRON_RIGHT", title="Next Month", width=25 )

        next_month_wdg.add_behavior( {
            'type': "click_up",
            'cbjs_action':  '''
                var kwargs = {async: false, fade: false};
                var el = bvr.src_el.getParent('.spt_calendar_top');
                spt.panel.refresh(el, {year: '%s', month: '%s', is_refresh: 'true', 
                        'search_key': '%s', 'top_id': '%s',
                    'col_name': '%s'}, kwargs);
            ''' % (next_year, next_month, self.search_key, self.top_id, self.col_name )
        })
        return next_month_wdg
       

    def get_today_icon(self):

        today_icon = IconWdg("Today", icon="BS_CALENDAR")
        today_icon.add_class('hand')

        # button to set calendar input to today's date ...
        today_icon.add_behavior( {
            "type": "click_up",
            "cbjs_action": '''
                var top = spt.get_parent(bvr.src_el, '.spt_calendar_top');
                spt.hide( top );
                var date_obj = new Date();
                var value = date_obj.getFullYear() + '-' + spt.zero_pad(date_obj.getMonth()+1, 2) +
                            '-' + spt.zero_pad(date_obj.getDate(), 2);
                var input_top = bvr.src_el.getParent('.calendar_input_top');
                
                if (input_top) {
                    var el = input_top.getElement('.spt_calendar_input');
                    // add timezone info
                    value = value + " -00:00 " + spt.api.Utility.get_user_timezone_offset();
                    el.value = value;
                     
                    var layout = bvr.src_el.getParent(".spt_layout");
                    var version = layout ? layout.getAttribute("spt_version"): 1;
                    if (version == "2") {
                        spt.table.set_layout(layout);
                        spt.table.accept_edit(input_top, value);
                    }
                    else {
                        // A CellEditWdg containing a Calendar widget will be a detached PUW, so use 'spt.get_parent()'
                        var td = spt.get_parent( el, '.spt_table_td' );
                        if( td ) {
                            // don't set the td 'spt_input_value' here! Not necessary and might be more complex widget!
                            el.spt_text_edit_wdg.accept_edit = true;
                            spt.dg_table.edit_cell_cbk(el, spt.kbd.special_keys_map.ENTER);
                        } else {
                            spt.validation.direct_input_element_check( el );
                            el.spt_text_edit_wdg.accept_edit = true;
                        }
                    }
                }
            '''
        } )
        return today_icon
        

    def get_close_icon(self):

        close_icon = ButtonNewWdg(title="Close", icon="FA_TIMES", size=16, width=25)
        close_icon.add_class('hand')

        # button to close calendar popup ...
        close_icon.add_behavior( {
            "type": "click_up",
            "cbjs_action": '''
                var top = spt.get_parent(bvr.src_el, '.spt_calendar_top');
                var el = bvr.src_el.getParent('.calendar_input_top').getElement('.spt_calendar_input');

                // A CellEditWdg containing a Calendar widget will be a detached PUW, so use 'spt.get_parent()'
                var td = spt.get_parent( top, '.spt_cell_edit' );
                if( td ) {
                    el.spt_text_edit_wdg.accept_edit = true;
                    spt.dg_table.edit_cell_cbk(el, spt.kbd.special_keys_map.ENTER);
                    var input_top = spt.get_parent(bvr.src_el, '.calendar_input_top');
                    spt.behavior.destroy_element( input_top );
                    //spt.hide( input_top );
                    spt.table.accept_edit(td, null)
                } else {
                    el.spt_text_edit_wdg.accept_edit = true;
                    spt.hide( top );
                }
            '''
        } )

        return close_icon




    def get_week_left_wdg(self, week):
        return None

    def get_week_right_wdg(self, week):
        return None


    def get_day_header_wdg(self, day):
        if self.size:
            weekday = self.WEEKDAYS[day.weekday()][0:self.size]
        else:
            weekday = self.WEEKDAYS[day.weekday()]

        div = DivWdg()
        #div.add_style("border-bottom: solid 1px %s" % div.get_color("border"))

        div.add_style("font-weight: bold")
        div.add_style("padding: 3px 0px 3px 0px")
        div.add_style("text-align: center")
        div.add( weekday )
        return div


    def get_day_wdg(self, month, day):
        div = DivWdg()
        div.add_class("SPT_DAY_CBK")
        div.add( day.day )
        div.add_style("text-align: center")
        div.add_class("spt_calendar_day hand")
        div.add_style("margin: auto")
        div.add_style("height: 28px")
        div.add_style("line-height: 28px")
        div.add_style("white-space: nowrap")
        div.add_style("border-radius: 28px")
        div.add_style("width: 28px")

        # NOTE: The bvr below is now added thru relay behavior

        """
        for cbk in self.day_cbks:
            behavior = {
                'type': 'click_up',
                'cbjs_action': cbk, 
                'search_key' : self.search_key,
                'top_id' : self.top_id,
                'col_name': self.col_name
            }
            div.add_behavior(behavior)
        """


        today = datetime.today()
        no_selection = self.kwargs.get("no_selection")
        if today.year == day.year and today.month == day.month and today.day == day.day:
            if not no_selection:
                div.add_color("background", "background", [-10, -10, 20])


        # put a different color for days that are not in the current month
        if day.month != month: 
            div.add_style("color: #bbb")

        # store date like the database does YYYY-MM-DD
        date_str = "%04d-%02d-%02d" % (day.year, day.month, day.day)
        div.add_attr('spt_date', date_str)
        div.add_class('spt_date_day')

        return div
        


class CalendarInputWdg(BaseInputWdg):

    ARGS_KEYS = {

         "first_day_of_week": {
            'description': "Integer representing first day of the week (6=Sunday, 0=Monday)",
            'type': 'SelectWdg',
            'labels': 'Sunday|Monday',
            'values': '6|0',
            'empty': 'true',
            'order': 0,
            'category': 'Display'
         },
        "show_time": {
            'description': "Determines whether or not a time value is entered.",
            'type': 'SelectWdg',
            'values': 'true|false',
            'order': 1,
            'category': 'Display'
        },
        "show_calendar": {
            'description': "Determines whether or not the calendar is shown.",
            'type': 'SelectWdg',
            'values': 'true|false',
            'category': 'Display'
        },
        "show_activator": {
            'description': "Determines whether or not to show the default activator for this widget",
            'type': 'SelectWdg',
            'values': 'true|false',
            'empty': 'true',
            'order': 1,
            'category': 'internal'
        },
        "read_only": {
            'description': "Sets the widget to be read only. In this case, the calendar will not show up and only a text box with the date value will be visible.",
            'type': 'SelectWdg',
            'values': 'true|false',
            'empty': 'true',
            'order': 1,
            'category': 'Display'
        },

        "date_format": {
            'description': "format of the date on clicking on a day in the Calendar, e.g. %m-%d-%Y or default to the project setting DATETIME or DATE",
            'type': 'TextWdg',
            'category': 'Display',
            'order': 8,
        },
        
        "display_format" : {
            'description': "display format like YYYY/MM/DD HH:MM AM or default to the project setting DATETIME or DATE",
            'type': 'TextWdg',
            'category': 'Display',
            'order': 9,
        },

        "hint_text" : {
            'description': "hint_text can be used to tell users why the calendar input is read only",
            'type': 'TextWdg',
            'category': 'Display',
        },
        

        'default': {
        'description': 'The default selection value in an edit form. Can be a TEL variable.',
        'type': 'TextWdg',
        'category': 'Display',
        'order': 2,
        },
        'search_key': {
        'description': 'The search key from which to extract data from',
        'type': 'TextWdg',
        'category': 'internal'
        },
        "time_input_default": {
        'description': 'The default for time applicable when show_time is true or false. e.g. 5:00 PM',
        'type': 'TextWdg',
        'category': 'Display',
        'order': 3
        },

        "offset" : {
            'description': "offset the calendar, e.g. x,y",
            'type': 'TextWdg',
            'category': 'Display',
            'order': 10,
        },
        "display_mode": {
            'description': "Determines whether to use the TACTIC calendar or the browser calendar",
            'type': 'SelectWdg',
            'values': 'browser|inline',
            'category': 'Display',
            'order': 3
        },
    }

    def __init__(self, name=None, **kwargs):
        super(CalendarInputWdg,self).__init__(name, "calendar", **kwargs)


    def init(self):
        self.top = DivWdg()
        self.value = ''
        self.cbjs_validation = ''
        self.validation_warning = ''

        self.day_cbks = []


    def get_top(self):
        return self.top



    def add_day_cbk(self, cbk):
        self.day_cbks.append(cbk)


    def set_validation(self, validation, validation_warning):
        self.cbjs_validation = validation
        self.validation_warning = validation_warning
   
     

    def get_display(self):

        # should not have float by default
        #self.top.add_style("float: left")
        self.top.add_class("calendar_input_top")
        self.top.add_class("spt_calendar_input_top")
        # TODO: start week with Sunday
        # May want to globalize in config for all calendars?
        first_day_of_week = self.get_option('first_day_of_week')
        if first_day_of_week == '':
            first_day_of_week = 6


        #state = self.get_state()
        #state['calendar'] = self.get_value()

        # assign validation bvr
        self.validation_script_path = self.get_option('validation_script_path') or ''
        self.validation_warning = self.get_option('validation_warning') or ''

        from tactic.ui.panel import EditWdg
        show_activator = self.get_option('show_activator')

        if show_activator in [True, 'true']:
            show_activator = True
        else:
            show_activator = False
        
        if isinstance(self.parent_wdg, EditWdg):
            if show_activator != 'false':
                show_activator = True
            else:
                show_activator = False


        if show_activator:
            activator = "BS_CALENDAR"
        else:
            activator = None



        show_calendar = self.get_option('show_calendar')
        if show_calendar in [True, 'true']:
            show_calendar = True
        else:
            show_calendar = False


        name = self.get_input_name()
        read_only = self.get_option('read_only')
        required = self.get_option('required')


        width = self.get_option('width')

        title = self.get_display_title()
        
        from tactic.ui.input import TextInputWdg
        # read_only is passed in so it gets darker bg color

        show_time = self.get_option("show_time") in [True, 'true']

        value = self.get_value()

        #display_mode = "inline"


        display_mode = self.get_option("display_mode")
        if not display_mode:
            display_mode = ProdSetting.get_value_by_key("calendar_display_mode")
        if not display_mode:
            display_mode = Config.get_value("global_setting","calendar_display_mode")
        if not display_mode:
            display_mode = "browser"


        if display_mode == "table":
            input = TextWdg(name=name, required=required)
            text = input
            text.add_class("spt_calendar_input") 
            if value:
                input.set_value(value)

        elif display_mode == "browser":

            if show_time:
                input = TextInputWdg(name=name, type="datetime-local", required=required, read_only=read_only)
            else:
                input = TextInputWdg(name=name, type="date", required=required, read_only=read_only)
            text = input.get_text()
            text.add_class("spt_calendar_input") 

            if value:
                input.set_value(value)


            input_div = DivWdg()
            input_div.add(input)
            self.top.add(input_div)
            return self.top


        else:
            # TODO: add a kwarg - hint_text
            hint_text = self.get_option('hint_text')
            if not hint_text:
                hint_text = None
            input = TextInputWdg( name=name, read_only=read_only, hint_text=hint_text, required=required, icon=activator, width=width)
            text = input.get_text()
            text.add_class("spt_calendar_input") 

            if value:
                input.set_value(value)



        if read_only == True:
            read_only = 'true'
        elif read_only == False:
            read_only = 'false'


        time_input_default = self.get_option('time_input_default')
        if show_time:
            #if not width:
            #    input.add_style("width: 130px")
            self.top.add_attr("show_time", "true")
            show_time = True
        else:
            if not width:
                input.add_style("width: 100px")
            self.top.add_attr("show_time", "false")
            show_time = False
            if time_input_default:
                input.add_style("width: 120px")


        input.add_style("text-left: center")

        input_div = DivWdg()
        input_div.add(input)
        self.top.add(input_div)

        offset_x = 0
        offset_y = 0

        offset = self.get_option('offset')
        offsets = offset.split(",")
        if len(offsets) > 1:
            offset_x = offsets[0]
            offset_y = offsets[1]


        # explicity true means no calendar on click
        if read_only == 'true':
            text.set_option("read_only", read_only)
        elif read_only != 'false':
            # this is an implicit read_only
            read_only = 'true'
            # let TextInputWdg set this attribute
            #text.set_option("read_only", read_only)
            text.set_disabled_look(False)
            # This is needed because of lack of support for behaviors
            text.add_event('onclick', '''
                    var el = document.id(this).getParent('.calendar_input_top').getElement('.spt_calendar_top');
                    if (el)
                        spt.show(el);
                  
                    spt.show(el);
                    spt.body.add_focus_element(el); 
                    event.stopPropagation();
            ''')

            text.add_behavior( {
                'type': 'focus', 
                'cbjs_action': 
                    '''var el = bvr.src_el.getParent('.calendar_input_top').getElement('.spt_calendar_top'); 
                    if (!el)  {
                        el = spt.calendar.get(); 
                        el.setStyle("width", "220px");
                       
                        var top = bvr.src_el.getParent('.calendar_input_top');
                        top.appendChild(el);
                        el.position({position: 'upperleft', relativeTo: bvr.src_el, offset: {x:bvr.offset_x, y:bvr.offset_y}});
                    }
                    
                    spt.show(el);
                    spt.body.add_focus_element(el); 
                    //evt.stopPropagation();
                    ''', 
                    'offset_x' : offset_x,
                    'offset_y' : offset_y
                })

            """
            # FIXME: keyup 'tab' occurs after blur
            text.add_behavior({'type': 'keyupX', 'cbjs_action': 
                    '''
                    if (evt.key == 'tab') {
                        var el = bvr.src_el.getParent('.calendar_input_top').getElement('.spt_calendar_top'); 
                        spt.hide(el);
                    }
                    '''
                    })
            """

            # TODO: this onblur is nice because it hides the calendar,
            # but it stops the input from functioning
            # input.add_event('onblur', '''var el = document.id(this).getParent('.calendar_input_top').getElement('.spt_calendar_top'); spt.hide(el);''')

            # TODO: focus behavior not supported yet
            #input.add_behavior( {
            #'type': 'focus',
            #'cbjs_action': '''
            #var el = bvr.src_el.getParent('.calendar_input_top').getElement('.spt_calendar_top');
            #spt.show(el);'''
            #} )






        kbd_bvr = {
            'type': 'keyboard',
            'kbd_handler_name': 'CalendarInputKeyboard',
        }
        input.add_behavior( kbd_bvr )

        if self.cbjs_validation or self.validation_script_path:
            if self.validation_warning:
                v_warning = self.validation_warning
            else:
                v_warning = "Date entry is not valid"
            from tactic.ui.app import ValidationUtil
            v_util = ValidationUtil( direct_cbjs=self.cbjs_validation, validation_script_path=self.validation_script_path, warning=v_warning )
            v_bvr = v_util.get_validation_bvr()
            if v_bvr:
                input.add_behavior( v_bvr )
                input.add_behavior( v_util.get_input_onchange_bvr() )




        cbks = []
        date_format = self.get_option('date_format')
      
        if not date_format:

            if show_time:
                key = 'DATETIME'
            else:
                key = 'DATE'

            setting = ProdSetting.get_value_by_key(key)
            if setting:
                date_format = setting

        if show_activator:
            
            day_cbk='''
            var top = spt.get_parent(bvr.src_el, '.spt_calendar_top');
            var input_top = spt.get_parent(bvr.src_el, '.calendar_input_top');
            //spt.hide( top );
             
            var value = bvr.src_el.getAttribute('spt_date');
            if (bvr.date_format && value) {
                var date_obj = new Date().parse(value)
                value = date_obj.format(bvr.date_format);
               
            }

            var el = input_top.getElement('.spt_calendar_input');
            var old_value = el.value;
            el.value = value;

            var layout = bvr.src_el.getParent(".spt_layout");
            var version = layout ? layout.getAttribute("spt_version"): 1;

           
            var show_time = input_top.getAttribute("show_time");
            if (show_time == 'true') {
                // keep the time (FIXME: this is not right because AM/PM
                // introduces uncertainty in what all the parts are
                var parts = old_value.split(" ");
                var time;
                if (parts.length == 3) {
                    time = parts[1] + " " + parts[2];
                }
                else if (parts.length == 2) {
                    if (parts[1] == 'AM' || parts[1] == 'PM') {
                        time = parts[0] + " " + parts[1];
                    }
                    else {
                        time = parts[1];
                    }
                }
                else if (bvr.time_input_default) {
                    time = bvr.time_input_default;
                }
                else {
                    time = "12:00";
                }
                parts = value.split(" ");
                var date = parts[0];

                value = date + " " + time;
                var class_name = 'tactic.ui.widget.CalendarTimeWdg';
                var options = {
                    name: bvr.name,
                    date: value,
                    date_format: bvr.date_format,
                };

                var kwargs = {fade: false, show_loading: false};

                spt.panel.load(top, class_name, options, null, kwargs);
            }
            else {
                spt.hide( top );
                if (bvr.time_input_default) {
                    value = value + ' ' + bvr.time_input_default;
                    el.value = value;
                }
                var version = layout ? layout.getAttribute("spt_version"): 1;
                if (version == "2") {
                    spt.table.set_layout(layout);
                    spt.table.accept_edit(top, value);
                } else {
                    // A CellEditWdg containing a Calendar widget will be a detached PUW, so use 'spt.get_parent()'
                    var td = spt.get_parent( el, '.spt_table_td' );
                    if( td ) {
                        // don't set the td 'spt_input_value' here! Not necessary and might be more complex widget!
                        el.spt_text_edit_wdg.accept_edit = true;
                        spt.dg_table.edit_cell_cbk(el, spt.kbd.special_keys_map.ENTER);
                    } else {
                        el.spt_text_edit_wdg.accept_edit = true;
                        spt.validation.direct_input_element_check( el );
                    }
                }
            }
            '''
            cbks.append(day_cbk)

            for more_cbk in self.day_cbks:
                day_cbk = "%s\n%s" % (day_cbk, more_cbk)
                cbks.append(day_cbk)

            #calendar = CalendarWdg( name=name, first_day_of_week=first_day_of_week)

        else:
            
            day_cbk='''
            var top = spt.get_parent(bvr.src_el, '.spt_calendar_top');

            var value = bvr.src_el.getAttribute('spt_date');
            if (bvr.date_format) {
                var date_obj = new Date().parse(value)
                //%m-%d-%Y
                value = date_obj.format(bvr.date_format);
            }
            var el = bvr.src_el.getParent('.calendar_input_top').getElement('.spt_calendar_input');
            var old_value = el.value;

            // add timezone info
            value = value + " -00:00 " + spt.api.Utility.get_user_timezone_offset();

            el.value = value;

            var input_top = spt.get_parent(bvr.src_el, '.calendar_input_top');
            var show_time = input_top.getAttribute("show_time");
            if (show_time == 'true') {
                // keep the time (FIXME: this is not right because AM/PM
                // introduces uncertainty in what all the parts are
                var parts = old_value.split(" ");
                var time;
                if (parts.length == 3) {
                    time = parts[1] + " " + parts[2];
                }
                else if (parts.length == 2) {
                    if (parts[1] == 'AM' || parts[1] == 'PM') {
                        time = parts[0] + " " + parts[1];
                    }
                    else {
                        time = parts[1];
                    }
                }
                else if (bvr.time_input_default) {
                    time = bvr.time_input_default;
                }
                else {
                    time = "12:00";
                }
                parts = value.split(" ");
                var date = parts[0];

                value = date + " " + time;

                var class_name = 'tactic.ui.widget.CalendarTimeWdg';
                var options = {
                    name: bvr.name,
                    date: value,
                    date_format: bvr.date_format,
                };

                var kwargs = {fade: false, show_loading: false};
                spt.panel.load(top, class_name, options, null, kwargs);
            }
            else {

                spt.hide( top );
                if (bvr.time_input_default) {
                    value = value + ' ' + bvr.time_input_default;
                    el.value = value;
                   
                }
                var layout = bvr.src_el.getParent(".spt_layout");
                var version = layout ? layout.getAttribute("spt_version"): 1;
                if (version == "2") {
                    spt.table.set_layout(layout);
                    spt.table.accept_edit(top, value);
                }
                else {
                    var td = spt.get_parent( el, '.spt_table_td' );
                    if( td ) {
                        // don't set the td 'spt_input_value' here! Not necessary and might be more complex widget!
                        el.spt_text_edit_wdg.accept_edit = true;
                        spt.dg_table.edit_cell_cbk(el, spt.kbd.special_keys_map.ENTER);
                    } else {
                        el.spt_text_edit_wdg.accept_edit = true;
                        spt.validation.direct_input_element_check( el );
                    }
                }

            }
            '''
            cbks.append(day_cbk)
            for more_cbk in self.day_cbks:
                day_cbk = "%s\n%s" % (day_cbk, more_cbk)
                cbks.append(day_cbk)

            #calendar = CalendarWdg( name=name, first_day_of_week=first_day_of_week)


        # add all of the callbacks to the top widget
        for day_cbk in cbks:
            self.top.add_relay_behavior( {
                'type': 'click',
                'bvr_match_class': 'spt_calendar_day',
                'cbjs_action': day_cbk,
                'name': name,
                'date_format': date_format,
                'time_input_default': time_input_default
            } )

        """
        show_text = False
        if not show_text:
            calendar.add_style("display: none")
        """
        #calendar.add_style("position: absolute")
        #self.top.add(calendar)
        #self.top.add_class("spt_no_alter")
        return self.top




    def get_value(self):


        # has to use self.value instead of self.get_value() 
        # to avoid a display bug with multiple inputs
        default = self.get_option("default")

        value = ""
        if not self.value and default:
            default_value = NamingUtil.eval_template(default)
            value = default_value
            if value:
                value = parser.parse(value)
                # NOTE: it's better not to do auto-convert for passed in value 
                # since it could be already in local time
                #if not SObject.is_day_column(self.get_name()):
                #    value = SPTDate.convert_to_local(value)

        current = self.get_current_sobject()
        
        if current and not current.is_insert():
            column = self.get_option("column")
            if not column:
                column = self.get_name()

            db_date = current.get_value(column, no_exception=True)
            
            if db_date:
                # This date is assumed to be GMT
                try:
                    value = parser.parse(db_date)
                except:
                    value = datetime.now()
                

                #from pyasm.common import SPTDate
                #from pyasm.search import SObject
                if not SObject.is_day_column(self.get_name()):
                    date = self.get_timezone_value(value)
                    
                try:
                    encoding = locale.getlocale()[1]
                    value = date.strftime("%b %d, %Y - %H:%M").decode(encoding)
                except:
                    value = date.strftime("%b %d, %Y - %H:%M")
               


        show_time = self.get_option("show_time") in [True, 'true']
        if show_time:
            key = 'DATETIME'
        else:
            key = 'DATE'
       
        if not value:
            value = self.value

            
        if value:
            format = self.get_option("display_format")

            if not format:
                format = key
            
            from pyasm.common import FormatValue
            f = FormatValue()
            value = f.get_format_value(value, format)

        return value




class CalendarMonthWdg(BaseRefreshWdg):
    MONTHS = ['January','Febuary','March','April','May','June','July','August','September','October','November','December']

    def get_display(self):

        style = HtmlElement.style('''
        .spt_month_top .spt_date:hover {
            background: #eee;
        }
        ''')

        cur_year = self.kwargs.get("year")
        cur_month = self.kwargs.get("month")
        name = self.kwargs.get('name')


        if not cur_year:
            now = datetime.now()
            cur_year = now.year
            cur_month = now.month

        top = self.top
        top.add(style)
        top.add_style("width: 180px")
        top.add_style("height: 150px")
        top.add_style("margin: auto")
        top.add_class("spt_month_top")


        header = DivWdg()
        top.add(header)
        header.add_style("width: 100%")
        header.add_style("justify-content: space-between")
        header.add_style("align-items: center")
        header.add_style("display: flex")

        prev_year_wdg = ButtonNewWdg( title="Prev Year", icon="FAS_CHEVRON_LEFT" )
        header.add(prev_year_wdg)
        prev_year_wdg.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_month_top");
            var year_el = top.getElement(".spt_year");
            year_el.innerHTML = parseInt(year_el.innerHTML) - 1;
            '''
        } )

        year_div = DivWdg()
        year_div.add_class("spt_year")
        header.add(year_div)

        next_year_wdg = ButtonNewWdg( title="Next Year", icon="FAS_CHEVRON_RIGHT" )
        header.add(next_year_wdg)
        next_year_wdg.add_style("text-align: right")
        next_year_wdg.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_month_top");
            var year_el = top.getElement(".spt_year");
            year_el.innerHTML = parseInt(year_el.innerHTML) + 1;
            '''
        } )



        year_div.add(cur_year)
        year_div.add_style("text-align: center")
        year_div.add_style("padding: 3px")
        year_div.add_style("font-weight: bold")

        top.add_relay_behavior( {
            'type': 'click',
            'name': name,
            'bvr_match_class': 'spt_date',
            'cbjs_action': '''
            var month = bvr.src_el.getAttribute("spt_month");
            var top = bvr.src_el.getParent(".spt_month_top");
            var year_el = top.getElement(".spt_year");
            var year = parseInt(year_el.innerHTML);

            var class_name = 'tactic.ui.widget.CalendarWdg';
            var kwargs = {
                col_name: bvr.name,
                year: year,
                month: month,
                is_refresh: true
            };
            var top = spt.get_parent(bvr.src_el, '.spt_calendar_top');
            spt.panel.load(top, class_name, kwargs);
            
            '''
        } )



        month_top = DivWdg()
        month_top.add_class("hand")
        month_top.add_style("display: grid")
        month_top.add_style("grid-template-columns: 1fr 1fr 1fr 1fr")
        month_top.add_style("margin: auto")
        top.add(month_top)
        for i, month in enumerate(self.MONTHS):
            month_div = DivWdg()
            month_top.add(month_div)
            month_div.add(month[:3])
            month_div.add_class("spt_date")
            month_div.add_attr("spt_month", i+1)
            month_div.add_style("float: left")
            month_div.add_style("width: 40px")
            month_div.add_style("height: 40px")
            month_div.add_style("text-align: center")
            month_div.add_style("line-height: 40px")
            month_div.add_style("border-radius: 40px")

            if i+1 == cur_month:
                month_div.add_color("background", "background3")

        return top



class CalendarTimeWdg(BaseRefreshWdg):

    def get_display(self):
        top = self.top
        top.add_style("width: 180px")
        top.add_style("height: 150px")
        top.add_style("padding: 5px")
        top.add_class("spt_time_top")

        date_format = self.kwargs.get('date_format')
        if not date_format:
            setting = ProdSetting.get_value_by_key('DATE')
            if setting:
                date_format = setting
            else:
                date_format = "%Y-%m-%d"

        
        date = self.kwargs.get("date")
        time = self.kwargs.get("time")

        if time:
            time = parser.parse(time)
            hours = time.hour
            minutes = time.minute
            date = None

        elif date:
            try:
                if date_format:
                    if date_format.startswith('%m'):
                        date = parser.parse(date, dayfirst=False)
                    else:
                        date = datetime.strptime(date, date_format)

                else:
                    date = parser.parse(date)
            except:
                # this seems redundant but required.
                # usually caused by the time in the date string, so try stripping it
                print("Error parsing: %s. Reparsing without time." %date)
                if date.find(' ') != -1:
                    tmps = date.split(' ')
                    if tmps[1].find(':') != -1:
                        date = tmps[0]
                
                try:
                    if date_format.startswith('%m'):
                        date = parser.parse(date, dayfirst=False)
                    else:
                        date = datetime.strptime(date, date_format)
                except:
                    date = datetime.now()

            hours = date.hour
            minutes = date.minute

        else:
            hours = self.kwargs.get("hours")
            if not hours:
                hours = 0
            minutes = self.kwargs.get("minutes")
            if not minutes:
                minutes = 0

        mode = self.kwargs.get("mode")
        if not mode:
            mode = "12 hour"
        if mode == "12 hour":
            if hours > 12:
                hours = hours - 12
                am_pm = "PM"
            else:
                am_pm = "AM"


        title_div = DivWdg(css='hand')
        title_div.add_style('text-align: left')
        top.add(title_div)
        if date:
            title_div.add(date.strftime("%a - %b %d, %Y"))

            title_div.add_behavior( {
                'type': 'click_up',
                'cbjs_action': '''
                var top = spt.get_parent(bvr.src_el, '.spt_calendar_top');

                var value = bvr.src_el.getAttribute('spt_date');
                var el = bvr.src_el.getParent('.calendar_input_top').getElement('.spt_calendar_input');
                // if time reset is desired, uncomment this
                //el.value = value;

                var class_name = 'tactic.ui.widget.CalendarWdg';
                var options = {
                    date: value,
                    is_refresh: true,
                };
                var kwargs = {fade: false};
                spt.panel.load(top, class_name, options, null, kwargs);
                ''' } )
        else:
            title_div.add("Set Time")




        name = self.kwargs.get("name")
        interval = 5
       
        top.add_behavior( {
            'type': 'load',
            'interval': interval,
            'mode': mode,
            'cbjs_action': '''
            spt.time_input = {};
            spt.time_input.drag_start_x = null;
            spt.time_input.drag_start_value = null;
            spt.time_input.mode = bvr.mode;

            spt.time_input.drag_setup = function(evt, bvr, mouse_411) {
                spt.time_input.drag_start_x = mouse_411.curr_x;
                var src_el = spt.behavior.get_bvr_src( bvr );
                if (!src_el.value) {
                    src_el.value = 0;
                }
                spt.time_input.drag_start_value = src_el.value;
                src_el.focus();
                src_el.select();
            }
            spt.time_input.drag_motion = function(evt, bvr, mouse_411) {
                var start_value = spt.time_input.drag_start_value; 
                if (isNaN(parseInt(start_value))) {
                    return;
                }
                var dx = mouse_411.curr_x - spt.time_input.drag_start_x;

                var src_el = spt.behavior.get_bvr_src( bvr );
                var unit = src_el.getAttribute("spt_unit");
                var max = 24;
                var start = "12";
                var px_interval = 10;
                var interval = 1;
                if (unit == 'minute') {
                    max = 60;
                    start = "00"
                    px_interval = 5;
                    interval = 5;
                }
                else if (spt.time_input.mode == '12 hour') {
                    max = 12;
                }

                var diff = parseInt(dx / px_interval);
                diff = diff % max + 1;
                if (diff < 0) {
                    diff = max + diff + 1;
                }
                diff = spt.zero_pad(diff, 2);


                src_el.value = diff;
            }
            '''
        } )

        top.add_behavior( {
            'type': 'smart_drag',
            'bvr_match_class': 'spt_time_element',
            'ignore_default_motion' : True,
            "cbjs_setup": 'spt.time_input.drag_setup( evt, bvr, mouse_411 );',
            "cbjs_motion": 'spt.time_input.drag_motion( evt, bvr, mouse_411 );'
        } )

        top.add_relay_behavior( {
        'type': 'keyup',
        'mode': mode,
        'bvr_match_class': 'spt_time_element',
        'cbjs_action': '''
            var key = evt.key;
            var unit = src_el.getAttribute("spt_unit");
            if (unit == 'am_pm') {
                if (key.match(/[aA]/)) {
                    bvr.src_el.value = "AM";
                }
                else if (key.match(/[pP]/)) {
                    bvr.src_el.value = "PM";
                }
                bvr.src_el.select()
            }
            else if (key == 'enter') {
                // do nothing for now until spt.table.accept_edit() works with this
                //spt.named_events.fire_event(bvr.evt_name, bvr);
            }
            else if (!key.match(/[0123456789]/)) {
                if (key == 'tab') {

                }
                else {
                    evt.stopPropagation();
                    value = bvr.src_el.value;
                    value = value.substr(0, value.length-1 );
                    value = value.replace(/[^0-9]/g, '')
                    bvr.src_el.value = value;
                }
            }
            else {
                var value = bvr.src_el.value;
                var test = parseInt(value, 10);
                var unit = src_el.getAttribute("spt_unit");
                var max;
                var trimmed = false;
                if (Math.abs(test) < 10) {

                }
                else {
                    if (unit == 'minute') {
                        min = 0;
                        max = 59;
                    } else if (bvr.mode == '12 hour') {
                        min = 1;
                        max = 12;
                    }
                    else {
                        min = 1;
                        max = 24;
                    }
                    if ( test > max) {
                        value = value.substr(0, value.length-1 );
                        if (value.length > 2)
                            value = value.substr(value.length-2, value.length );
                        bvr.src_el.value = value;
                        trimmed = true;
                    }
                   
                }
                if (!trimmed && value.length > 2){
                    bvr.src_el.value = value.substr(value.length-2, value.length );
                }
            }
        '''
        } )


        table = Table()
        top.add(table)
        table.add_row()
        table.add_style("font-size: 20px")
        table.add_style("font-weight: bold")
        table.add_style("margin: 20px auto")

        hours_input = TextWdg("%s|hours" % name)
        hours_input.add_class("spt_time_element")
        hours_input.add_attr("spt_unit", "hour")
        hours_input.add_style("height: 50px")
        hours_input.add_style("width: 50px")
        hours_input.add_style("font-size: 20px")
        hours_input.add_style("text-align: center")
        hours_input.set_value("%0.2d" % hours)

        minutes_input = TextWdg("%s|minutes" % name)
        minutes_input.add_class("spt_time_element")
        minutes_input.add_attr("spt_unit", "minute")
        minutes_input.add_style("height: 50px")
        minutes_input.add_style("width: 50px")
        minutes_input.add_style("text-align: center")
        minutes_input.add_style("font-size: 20px")
        minutes_input.set_value("%0.2d" % minutes)

        left = table.add_cell()
        left.add(hours_input)

        middle = table.add_cell(":")
        middle.add_style("width: 15px")
        middle.add_style("text-align: center")

        right = table.add_cell()
        right.add(minutes_input)

        if mode == "12 hour":
            am_pm_td = table.add_cell()
            am_pm_text = TextWdg("am_pm")
            am_pm_td.add(am_pm_text)


            am_pm_text.add_class("spt_time_element hand")
            am_pm_text.add_attr("spt_unit", "am_pm")
            am_pm_text.set_option("read_only", "true")
            am_pm_text.add_style("font-size: 20px")
            am_pm_text.set_option("values", "AM|PM")
            am_pm_text.add_style("height", "50px")
            am_pm_text.add_style("width", "40px")
            am_pm_text.add_style("padding", "0px 0px 3px 0px")
            am_pm_text.set_value(am_pm)
            am_pm_text.add_behavior( {
                'type': 'click_up',
                'cbjs_action': '''
                var value = bvr.src_el.value;
                if (value == 'AM' || value == '') {
                    value = 'PM';
                }
                else {
                    value = 'AM';
                }
                bvr.src_el.value = value;

                '''
            })





        ok_div = DivWdg()
        top.add(ok_div)
        ok_div.add_style("float: right")
        from tactic.ui.widget import ActionButtonWdg
        button = ActionButtonWdg(title="Accept")
        ok_div.add(button)

        if not date:
            date_str = ""
        else:
            date_str = date.strftime(date_format)
        
      
        button.add_behavior( {
            'type': 'click_up',
            'date': date_str,
            'cbjs_action': '''
            var target = bvr.src_el;
            var top = target.getParent('.spt_time_top');
            var time_els = top.getElements('.spt_time_element');
            var hour = time_els[0].value;
            hour = spt.zero_pad(hour, 2);
            var mins = time_els[1].value;
            mins = spt.zero_pad(mins, 2)
            var am_pm;
            if (time_els.length == 3) {
                am_pm = " " + time_els[2].value;
            }
            else {
                am_pm = "";
            }

            var value;
            if (bvr.date) {
                var tmps = bvr.date.split(' ');
                // keep the date portion
                if (tmps.length > 1)
                    bvr.date = tmps[0];
                value = bvr.date + " " + hour + ":" + mins + am_pm;
            }
            else {
                value = hour + ":" + mins + am_pm;
            }
            
            // add timezone info
            value = value + " " + spt.api.Utility.get_user_timezone_offset();

            var input_top = target.getParent('.calendar_input_top');
            var el = input_top.getElement('.spt_calendar_input');
            el.value = value;

            var calendar_top = target.getParent('.spt_calendar_top');
            // don't hide the top or it will be not functional on next click
            if (calendar_top) {
                spt.hide( calendar_top );
            }
            // only support version 2 of table layout
            var layout = target.getParent(".spt_layout");
            if (layout) {
                spt.table.set_layout(layout);
                spt.table.accept_edit(top, value);
            } 

            '''
        } )

        """
        #TODO: fire the event. but it is not compatible when it's used in a TableLayoutWdg with spt.table.accept_edit().
        ok_div.add_behavior({'type':'click_up',
            'cbjs_action': '''spt.named_events.fire_event('%s', bvr);'''%evt_name})
        """
        top.add("<br clear='all'/>")
        #top.add_class("spt_no_alter")

        return top

 



__all__.extend(["DateDatabaseAction", "TimeDatabaseAction"])
from pyasm.command import DatabaseAction
class DateDatabaseAction(DatabaseAction):

    def execute(self):
        name = self.get_name()

        column = self.get_option("column")
        if not column:
            column = name

        columns = column.split("|")
        for column in columns:

            value = self.get_value()
            if value:
                value = parser.parse(value)
                day = value.day
                month = value.month
                year = value.year

            else:
                return


            sobject = self.sobject
            cur_value = sobject.get_value(column)

            if cur_value and isinstance(cur_value, basestring):
                cur_value = parser.parse(cur_value)

            if cur_value:
                column_info = sobject.get_column_info(column)
                if column_info.get("data_type") in ['timestamp','datetime2']:
                    cur_value = cur_value.replace(year=year, month=month, day=day)
                else:
                    cur_value = value
            else:
                cur_value = value

            sobject.set_value(column, cur_value)

        return name




class TimeDatabaseAction(DatabaseAction):

    def execute(self):
        name = self.get_name()

        column = self.get_option("column")
        if not column:
            column = name

        value = self.get_value()
        if value:
            value = parser.parse(value)
            hour = value.hour
            minute = value.minute
        else:
            hour = 12
            minute = 0

        sobject = self.sobject
        cur_value = sobject.get_value(column)
        if cur_value:
            if isinstance(cur_value, basestring):
                cur_value = parser.parse(cur_value)
        else:
            cur_value = datetime.now()

        column_info = sobject.get_column_info(column)
        if column_info.get("data_type") in ['timestamp']:
            cur_value = cur_value.replace(hour=hour, minute=minute)
        else:
            cur_value = value

        sobject.set_value(column, cur_value)

        return name



class TimeInputWdg(BaseInputWdg):

    ARGS_KEYS = {
       "interval": {
            'description': "Interval for minutes, default to 10",
            'type': 'SelectWdg',
            'values': '1|5|10|20|30',
            'empty': 'true',
            'order': 1,
            'category': 'Display'
        },
       "default": {
            'description': "Default time",
            'type': 'TextWdg',
            'order': 2,
            'category': 'Display',
        }
 
    }

    def init(self):
        self.top = DivWdg()

 
    def get_display(self):
        top = self.top
        top.add_class("calendar_input_top")

        name = self.get_input_name()


        from tactic.ui.input import TextInputWdg
        input = TextInputWdg( name=name )
        top.add(input)
        input.add_class("spt_calendar_input")
        input.add_style("width: 100px")
        text = input.get_text()
        text.add_event('onfocus', '''var el = document.id(this).getParent('.calendar_input_top').getElement('.spt_calendar_top'); spt.show(el); spt.body.add_focus_element(el); var el = el.getElement('.spt_time_element'); el.focus(); el.select();''')
        text.add_event('onclick', '''event.stopPropagation();''')

        div = DivWdg()
        div.add_class("spt_calendar_top")
        top.add(div)
        div.add_style("display: none")
        div.add_style("margin-top: -25px")
        div.add_style("z-index: 1000")
        div.add_style("position: absolute")

        div.add_border()
        div.set_box_shadow("2px 2px 2px 2px")
        div.add_color("background", "background")
        div.add_color("color", "color")

        mode = self.get_option("mode")
        if not mode:
            mode = "24 hour"
        mode = "12 hour"


        time = self.get_option("time")
        if not time:
            time = self.get_option("default")
        if not time:
            time = "12:00 PM"
        time_input = CalendarTimeWdg(name=name, date="", mode=mode, time=time)
        div.add(time_input)
 
        return top




class CalendarIntervalInputWdg(BaseRefreshWdg):

    def add_class(self, class_name):
        self.top.add_class(class_name)
    
    def add_style(self, style):
        self.top.add_style(style)
    
    def get_display(self):

        top = DivWdg()
        self.top = top
        top.add_class("spt_calendar_interval_top")
        top.add_style("z-index", "4")

        start_date = self.kwargs.get("start_date") or ""
        end_date = self.kwargs.get("end_date") or ""

        calendar = CalendarWdg(no_selection=True)
        top.add(calendar)
        calendar.add_behavior({
            'type': 'load',
            'start_date': start_date,
            'end_date': end_date,
            'cbjs_action': '''
            spt.calendar = {}
            spt.calendar.interval = {}
            spt.calendar.interval.selection_start = false;
            spt.calendar.interval.start_date = bvr.start_date || "";
            spt.calendar.interval.end_date = bvr.end_date || "";

            '''
        })
        calendar.add_relay_behavior({
            'type': 'click',
            'bvr_match_class': 'spt_calendar_day',
            'cbjs_action':'''
            var selected_date = bvr.src_el.getAttribute("spt_date");
            
            if (spt.calendar.interval.selection_start) {
                if (selected_date < spt.calendar.interval.start_date) {
                    return;
                } else if (selected_date == spt.calendar.interval.start_date) {
                    spt.calendar.interval.end_date = selected_date;
                    return;
                }
                bvr.src_el.setStyle("background", "#dbdbFF");
                spt.calendar.interval.end_date = selected_date;
                var el_td = bvr.src_el.getParent("td")
                el_td.setStyle("background", "#eaeafd");

                var el = spt.calendar.interval.start_element;
                el.setStyle("border-radius", "28px 0px 0px 28px");
                el.setStyle("background", "#eaeafd");
                while (el != el_td) {
                    var prev_el = el;
                    var el = el.getNext();
                    if (!el) {
                        var tr = prev_el.getParent("tr");
                        var next_tr = tr.getNext();
                        if (!next_tr) {
                            var next_tr = spt.calendar.interval.next_tr;
                        }
                        el = next_tr.getFirst();
                    }
                    if (el == el_td) {
                        el.setStyle("border-radius", "0px 28px 28px 0px");
                    } else {
                        el.setStyle("border-radius", "");
                        el.getElement(".spt_calendar_day").setStyle("background", "");
                    }
                    el.setStyle("background", "#eaeafd");
                }
                spt.calendar.interval.selection_start = false;
                spt.named_events.fire_event('interval_input|finish', {});
            } else {
                bvr.src_el.setStyle("background", "#dbdbFF");
                spt.calendar.interval.selection_start = true;
                spt.calendar.interval.start_date = selected_date;
                spt.calendar.interval.start_element = bvr.src_el.getParent("td");
            }
            '''
        })

        calendar.add_relay_behavior({
            'type': 'click',
            'bvr_match_class': 'btn',
            'cbjs_action':'''
            var cancel = bvr.src_el.getElement(".fa-times");
            if (cancel) {
                return;
            }

            var top = bvr.src_el.getParent(".spt_calendar_top");
            var els = top.getElements(".spt_calendar_day");
            els.forEach(function(el) {
                if (el.innerHTML == 1) {
                    spt.calendar.interval.next_tr = el;
                    break;
                }
            })
            '''
        })

        calendar.add_relay_behavior({
            'type': 'mouseenter',
            'bvr_match_class': 'spt_calendar_day',
            'cbjs_action':'''
            if (!spt.calendar.interval.selection_start) {
                return;
            }

            var hover_date = bvr.src_el.getAttribute("spt_date");
            if (hover_date <= spt.calendar.interval.start_date) {
                return;
            }

            var top = bvr.src_el.getParent(".spt_calendar_top");
            var els = top.getElements(".spt_calendar_day");

            els.forEach( function(el) {
                var date = el.getAttribute("spt_date");
                var td = el.getParent("td");
                if ((date >= spt.calendar.interval.start_date) && (date < bvr.src_el.getAttribute("spt_date"))) {
                    td.setStyle("background", "#eaeafd");
                } else if (date == bvr.src_el.getAttribute("spt_date")) {
                    td.setStyle("border-radius", "0px 28px 28px 0px");
                    td.setStyle("background", "#eaeafd");
                } else {
                    td.setStyle("background", "");
                    td.setStyle("border-radius", "");
                    el.setStyle("background", "");
                }
            })
            '''
        })

        return top

