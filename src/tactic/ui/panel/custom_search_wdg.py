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

__all__ = ['CustomSearchWdg']


# DEPRECATED: this is possibly used in MMS and should not be used anywhere
# else.  It should be migrated to the mms tree

import os

from pyasm.common import Date, Environment
from pyasm.search import Search
from pyasm.web import DivWdg, SpanWdg, Table, WebContainer
from pyasm.widget import SelectWdg, TextWdg, HiddenWdg

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.filter import FilterData
from tactic.ui.widget import CalendarInputWdg, TextBtnSetWdg

from dateutil import parser


# TODO: this is specific to MMS and should be moved from here


class CustomSearchWdg(BaseRefreshWdg):

    def get_args_keys(my):
        return {
        'search_type': 'search type for this search widget'
        }


    def init(my):
        #my.handle_search()
        pass

    def handle_search(my):

        search_type = my.kwargs.get("search_type")
        my.search = Search(search_type)
        my.alter_search(my.search)
        return my.search

    def get_search(my):
        return my.search


    def alter_search(my, search):

        user = Environment.get_user_name()
        from pyasm.security import Login
        user = Login.get_by_login(user)
        search.add_filter("login", user.get_value("login"))


        import datetime
        from dateutil import parser
        filter_data = FilterData.get()
        values = filter_data.get_values_by_index("week", 0)
        date_string = values.get("calendar")
        if date_string:
            date = parser.parse(date_string)
        else:
            date = datetime.datetime.now()

        from tactic.ui.report import MMSUtility
        #start_wday, end_wday = my.get_week_range(date_string)
        start_wday, end_wday = MMSUtility.get_week_range(date)


        one_day = datetime.timedelta(days=1)

        column = "work_performed_date"

        # KEEP it simple for now
        search.add_op("begin")
        search.add_filter(column, start_wday, op='>=')
        search.add_filter(column, end_wday, op='<=')
        search.add_op("and")

        '''
        search.add_op("begin")
        search.add_filter(column, start_wday + one_day, op='>=')
        search.add_filter(column, end_wday - one_day, op='<=')
        search.add_op("and")

        search.add_op("begin")
        search.add_filter(column, start_wday, op='>=')
        search.add_filter(column, start_wday+one_day, op='<=')
        search.add_filter("shift", "pm", op='=')
        search.add_op("and")

        # FIXME: have to add this extra "or" because we don't support multiple
        # begins??
        search.add_op("or")
 
        search.add_op("begin")
        search.add_filter(column, end_wday, op='>=')
        search.add_filter(column, end_wday+one_day, op='<=')
        search.add_filter("shift", "am", op='=')
        search.add_op("and")
 
        search.add_op("or")
        '''


        search.add_order_by(column)
        search.add_order_by("work_start_time")
        search.add_order_by("shift")

        



    def get_display(my):


        from tactic.ui.report import MMSUtility
        import datetime
        date = datetime.datetime.now()
        start_wday, end_wday =  MMSUtility.get_week_range(date)

        my.prefix = 'week'
        top = DivWdg()
        top.add_class("spt_table_search")
        my.set_as_panel(top)

        from tactic.ui.container import RoundedCornerDivWdg
        inner = RoundedCornerDivWdg(corner_size=10, hex_color_code='949494')
        inner.set_dimensions(width_str="95%", content_height_str='95%', height_str="100%")
        inner.add_style("margin: 20px")
        top.add(inner)


        hidden = HiddenWdg("prefix", my.prefix)
        top.add(hidden)



        filter_data = FilterData.get()
        values = filter_data.get_values_by_index("week", 0)
        date_string = values.get("calendar")
        if not date_string:
            date_string = WebContainer.get_web().get_form_value("calendar")

        if date_string:
            date = parser.parse(date_string)
        else:
            date = datetime.datetime.now()

        week = 1


        table = Table()
        table.add_style("color: black")
        table.add_style("width: 600px")
        table.add_row()
        inner.add(table)


        #inner.add("Range: %s - %s<br/><br/>" % (start_wday, end_wday))


        table.add_cell("Week Of Date: <br/>")
        calendar = CalendarInputWdg('calendar')

        day_cbk = '''
        var top = spt.get_parent(bvr.src_el, '.spt_table_search');
        var week_el = top.getElement('.spt_calendar_week');
        var input_el = top.getElement('.spt_calendar_input');
        var value = input_el.value;
        var week = spt.date_util.ymd.get_week( value )
        week_el.innerHTML = week + '';
        '''
        calendar.add_day_cbk(day_cbk)


        #calendar.set_option("first_day_of_week", 4)
        calendar.set_value(date.strftime("%Y-%m-%d"))
        # TODO: set default
        table.add_cell( calendar )

        week = int(date.strftime("%W")) + 1

        table.add_cell("Week: ")
        #select = SelectWdg("week")
        #select.add_class("action inputfield")
        #select.set_option("values", range(1,53) )
        #select.set_value(week)
        #select.set_option( "size", "2" )
        text = DivWdg()
        text.add_class("spt_calendar_week")
        text.add_style("width", "25px")
        text.add(week)
        table.add_cell(text)

        table.add_cell( my.get_search_wdg() )

        return top



    def get_search_wdg(my):
        filter_div = DivWdg()

        buttons_list = [
                {'label': 'Run Search', 'tip': 'Run search with this criteria' },
                #{'label': 'Terminal View', 'tip': 'Launch Terminal View' },
                #{'label': 'Clear', 'tip': 'Clear all search criteria',
                #    'bvr': {'cbjs_action': 'spt.api.Utility.clear_inputs(bvr.src_el.getParent(".spt_search"))'} }
        ]

        txt_btn_set = TextBtnSetWdg( position='', buttons=buttons_list, spacing=6, size='small', side_padding=4 )

        # handle the search button
        run_search_bvr = {
            'type':         'click_up',
            'cbjs_action':  '''
            spt.dg_table.search_cbk(evt, bvr);
            //setTimeout( function() {
            //var top = bvr.src_el.getParent(".spt_table_search");
            //spt.panel.refresh(top);
            //}, 10);
            ''',
            'panel_id':     my.prefix
        }
        txt_btn_set.get_btn_by_label('Run Search').add_behavior( run_search_bvr )

        # handle the terminal button
        #terminal_bvr = {
        #    'type':         'click_up',
        #    'cbjs_action':  '''
        #    bvr.script_code = '784MMS';
        #    spt.CustomProject.custom_script(evt, bvr);
        #    ''',
        #}
        #txt_btn_set.get_btn_by_label('Terminal View').add_behavior( terminal_bvr )



        filter_div.add( txt_btn_set )
        return filter_div


