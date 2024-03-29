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


__all__ = ['WorkHoursElementWdg', 'WorkHoursElementAction']

from pyasm.common import TacticException, jsonloads, jsondumps, Common, Environment
from pyasm.search import Search, SearchType, SearchKey
from pyasm.web import DivWdg, HtmlElement, Table, Widget, WebContainer, FloatDivWdg
from pyasm.widget import TextWdg, IconWdg, HiddenWdg
from pyasm.command import Command, DatabaseAction

from tactic.ui.common import SimpleTableElementWdg, BaseRefreshWdg
from tactic.ui.panel import *
from tactic.ui.widget import IconButtonWdg
from pyasm.biz import Task

from dateutil import rrule, parser
import datetime



class WorkHoursHeaderWdg(BaseRefreshWdg):

    def get_display(self):
        pass


class WorkHoursElementWdg(SimpleTableElementWdg):

    LEFT_WIDTH = 20
    DAY_WIDTH = 35
    MONTH_WIDTH = 25
    OT = 'overtime'
    ST = 'regular'
    STT = 'regular_stt'
    ENT = 'regular_ent'
    OT_ROW = 'overtime_row'
    ST_ROW = 'regular_row'
    STT_ROW = 'starttime_row'
    ENT_ROW = 'endtime_row'
    ROW_DICT = {OT_ROW: OT, ST_ROW: ST, STT_ROW: STT, ENT_ROW: ENT}
    UNIT_DICT = {'hour' : 3600, 'minute': 60}

    ARGS_KEYS = SimpleTableElementWdg.ARGS_KEYS.copy()

    ARGS_KEYS['show_all_users'] = {
        'type': 'SelectWdg',
        'description': 'show work hours of all users. text fields will become read-only',
        'values': 'true|false',
        'order': 2,
        'category': 'Display'
        }


    ARGS_KEYS['show_overtime'] = {
        'type': 'SelectWdg',
        'description': 'Display a row to input overtime hours',
        'values': 'true|false',
        'order': 2,
        'category': 'Display'
        }

    ARGS_KEYS['use_straight_time'] = {
        'type': 'SelectWdg',
        'description': 'use straight_time to enter daily hours',
        'values': 'true|false',
        'order': 3,
        'category': 'Display'
        }
    ARGS_KEYS['unit'] = {
        'type': 'SelectWdg',
        'values': 'minute|hour',
        'description': 'unit for straight time when using start/end entry mode',
        'order': 4,
        'category': 'Display'
        }
    ARGS_KEYS['day_width'] = {
        'type': 'TextWdg',
        'description': 'Width of each cell to enter time or hours',
        'order': 5,
        'category': 'Display'
        }
    ARGS_KEYS['width'] = {
        'type': 'TextWdg',
        'description': 'Width of overall widget',
        'order': 6,
        'category': 'Display'
        }
    ARGS_KEYS['days_per_page'] = {
        'type': 'TextWdg',
        'description': 'Number of days to show per page',
        'order': 7,
        'category': 'Display'
        }


    def get_width(self):
        return 380


    def init(self):
        self.preprocessed = False
        self.is_refresh = self.kwargs.get("is_refresh")

        self.use_straight_time = self.kwargs.get("use_straight_time")
        if self.use_straight_time == 'false':
            self.use_straight_time = False
        else:
            self.use_straight_time = True


        self.start_date = None
        self.summary_st = {}
        self.summary_ot = {}
        self.show_overtime = self.kwargs.get("show_overtime")

        self.unit = self.kwargs.get("unit")
        if not self.unit:
            self.unit = "hour"

        self.days_per_page = self.kwargs.get("days_per_page")
        self.day_width = self.kwargs.get("day_width")
        self.table_width = self.kwargs.get("width")
        if not self.table_width and self.use_straight_time:
            self.table_width = 360

        if not self.day_width:
            self.day_width = self.DAY_WIDTH
        else:
            self.day_width = int(self.day_width)

        if not self.days_per_page:
            self.days_per_page = 7
        else:
            self.days_per_page = int(self.days_per_page)

        if not self.table_width:
            self.table_width = self.days_per_page * self.day_width * 2.2

        if self.show_overtime in [True, "true"]:
            self.show_overtime = True
        else:
            self.show_overtime = False

    def _get_date_obj(self, date_str):
        start_y, start_m, start_d = date_str.split('-')
        start_date = datetime.date(int(start_y), int(start_m), int(start_d))
        return start_date

    def get_required_columns(self):
        '''method to get the require columns for this'''
        return []

    def preprocess(self):
        self.preprocessed = True
        self.today = datetime.date.today()
        wday = int(self.today.strftime("%w"))

        web = WebContainer.get_web()
        start_date = web.get_form_value('start_date')
        web_data = web.get_form_value('web_data')

        if web_data:
            web_data = jsonloads(web_data)
        workhour_data = None
        if web_data:
            web_data = web_data[0]
            workhour_data = web_data.get('workhour_data')
        if start_date:
            start_date = self._get_date_obj(start_date)
        elif workhour_data:
            workhour_data = jsonloads(workhour_data)
            start_date = workhour_data.get('start_date')
            start_date = self._get_date_obj(start_date)
        else:
            if self.days_per_page < 7:
                start_date = self.today
            else:
                start_date = self.today - datetime.timedelta(days=wday)

        self.start_date = start_date
        end_date = start_date + datetime.timedelta(days=self.days_per_page -1)
        # this may not be necessary any more
        """
        if not self.sobjects:
            sk = self.kwargs.get('search_key')
            task = SearchKey.get_by_search_key(sk)
            self.sobjects = [task]
        """
        task_codes = [x.get_code() for x in self.sobjects]

        search = Search("sthpw/work_hour")

        if self.kwargs.get('show_all_users') != 'true':

            search.add_user_filter()

        search.add_filter("day", start_date, ">=")
        search.add_filter("day", end_date, "<=")
        search.add_filters("task_code", task_codes)
        entries = search.get_sobjects()

        # NOTE:
        # This widget assumes one entry per day.  This is not the case
        # when time for each entry must be recorded and you may have
        # multiple entries per day

        # organize into days
        self.entries = {}
        for entry in entries:
            day = entry.get_value("day")
            if not day:
                continue
            day = parser.parse(day)
            day = day.strftime("%Y_%m_%d")

            task_code = entry.get_value("task_code")
            task_entries = self.entries.get(task_code)
            if task_entries == None:
                task_entries = {}
                self.entries[task_code] = task_entries

            entry_list = task_entries.get(day)
            if entry_list == None:
                entry_list = []
                task_entries[day] = entry_list
            entry_list.append(entry)

        # break into 2 categories
        for key, sub_dict in self.entries.items():
            if self.use_straight_time:
                for key2, entry_list in sub_dict.items():
                    entry_list_dict = {self.OT: [], self.ST: []}
                    for entry in entry_list:
                        if entry.get_value('category') == self.OT:
                            entry_list_dict[self.OT].append(entry)
                        elif entry.get_value('category') == self.ST:
                            entry_list_dict[self.ST].append(entry)
                        else:
                            # in case they haven't run the upgrade script
                            # (potentially include some custom-entered category)
                            entry_list_dict[self.ST].append(entry)

                    sub_dict[key2] = entry_list_dict

            else:
                for key2, entry_list in sub_dict.items():
                    entry_list_dict = {self.STT: [], self.ENT: []}
                    for entry in entry_list:
                        entry_list_dict[self.STT].append(entry)
                        entry_list_dict[self.ENT].append(entry)

                    sub_dict[key2] = entry_list_dict



        self.dates = list(rrule.rrule(rrule.DAILY, dtstart=start_date, until=end_date))

        for idx in range(0,8):
            self.summary_st[idx] = {}

        for idx in range(0,8):
            self.summary_ot[idx] = {}

    def get_default_cbk(self):
        return "tactic.ui.table.WorkHoursElementAction"

    def handle_th(self, th, wdg_idx=None):
        th.add_attr('spt_input_type', 'inline')

    def handle_td(self, td):
        td.add_class("spt_input_inline")
        td.add_attr('spt_input_type', 'work_hour')

    def is_editable(cls):
        return False
    is_editable = classmethod(is_editable)

    def get_onload_js(self):
        return '''
    spt.work_hour = {};
    spt.work_hour.update_total = function(bvr, spt_day_type) {
            var top = bvr.src_el.getParent(".spt_work_hours_top");
            var days = top.getElements(spt_day_type);

            var total = 0;
            for (var i = 0; i < days.length; i++) {
                var value = days[i].value;
                if (value != '') {
                    total += parseFloat(value);
                }
            }
            var el;
            if (spt_day_type == '.spt_dayot') {
                el = top.getElement(".spt_totalot");
            }
            else {
                el = top.getElement(".spt_total");
            }
            if (el)
                el.value = total;
    }

        '''

    def get_title(self):

        div = DivWdg()
        div.add_behavior({'type': 'load',
            'cbjs_action': self.get_onload_js()})
        # for csv export
        hid = HiddenWdg('start_date', self.start_date)
        div.add(hid)

        mday = self.today.strftime("%d")
        mmonth = self.today.strftime("%m")

        self.weekday_dict = {}
        days = []
        for idx, date in enumerate(self.dates):
            day_div = DivWdg()
            days.append( day_div )
            week_day = date.strftime("%a")
            day_div.add( "%s<br/>%s" % (week_day, date.strftime("%d") ))
            self.weekday_dict[idx] = week_day

        table = Table()
        div.add(table)
        table.add_row()
        table.add_color("color", "color")
        table.add_style("width: %spx"%self.table_width)
        table.add_style("float: left")

        month_div = FloatDivWdg(self.start_date.strftime("%b"))
        month_div.add_style('font-weight: 600')
        td = table.add_cell(month_div)
        td.add_style('width', '%spx'%self.MONTH_WIDTH)

        icon = IconButtonWdg(tip="Previous Week", icon="FA_CHEVRON_LEFT")
        td = table.add_cell(icon)
        offset = 0
        if not self.use_straight_time:
            offset = 12
        td.add_style("width: %spx" % (self.LEFT_WIDTH + offset) )

        display_days = self.days_per_page
        next_start_date = self.start_date + datetime.timedelta(days=display_days)
        prev_start_date = self.start_date + datetime.timedelta(days=-display_days)


        icon.add_behavior( {
        'type': 'click_up',
        'start_date': prev_start_date.__str__(),
        'cbjs_action': '''
           spt.app_busy.show('Loading previous week...');
           var header = bvr.src_el.getParent('.spt_table_header');
           if (!header) {
                spt.alert('Work hour widget requires the new Fast Table Layout to scroll to previous week. You can do so in [Manage Side Bar].');
                spt.app_busy.hide();
                return;
           }
           var cur_name = spt.table.get_element_name_by_header(header);
           var values = {'start_date': bvr.start_date};
           spt.table.refresh_column(cur_name, values);

           spt.app_busy.hide();
        '''
        } )

        for day in days:
            day_wdg = DivWdg()
            day_wdg.add(day)

            td = table.add_cell()
            td.add(day_wdg)
            td.add_styles("text-align: center; padding-left: 2px;min-width: %spx"%self.day_width)

        icon = IconButtonWdg(tip="Next Week", icon="FA_CHEVRON_RIGHT")
        icon.add_behavior( {
            'type': 'click_up',
            'start_date': next_start_date.__str__(),
            'cbjs_action': '''
            spt.app_busy.show('Loading next week...');
            var header = bvr.src_el.getParent('.spt_table_header');
            if (!header) {
                spt.alert('Work hour widget requires the new Fast Table Layout to scroll to next week. You can do so in [Manage Side Bar].');
                spt.app_busy.hide();
                return;
            }
            var cur_name = spt.table.get_element_name_by_header(header);
            var values = {'start_date': bvr.start_date};
            spt.table.refresh_column(cur_name, values);
            spt.app_busy.hide();


            '''
        } )
        td = table.add_cell(icon)
        td.add_style('width: %spx'%self.day_width)
        # empty total cell
        td = table.add_blank_cell()
        td.add_style('width: 100%')

        return div

    def get_time_value(self, entry, row):
        '''get the time value and delta of hours. It returns minutes for delta if it's for start/end time'''
        value = ''
        delta = 0

        if self.use_straight_time:
            value = entry.get_value("straight_time")
            delta = value
        else:
            end_time_obj = None
            if row == self.STT_ROW:
                value = entry.get_value('start_time')
            else:
                value = entry.get_value('end_time')
                st_value = entry.get_value('start_time')
                end_time_obj = parser.parse(value)
                st_time_obj = parser.parse(st_value)
                delta = (end_time_obj - st_time_obj).seconds / self.UNIT_DICT[self.unit]
            if value:
                if end_time_obj:
                    value = end_time_obj.strftime("%H%M")
                else:
                    day = parser.parse(value)
                    value = day.strftime("%H%M")


        return value, delta

    def get_display(self):

        if not self.preprocessed:
            self.preprocess()

        if self.is_refresh:
            top = Widget()
        else:
            top = DivWdg()
            top.add_class("spt_work_hours_top")

            hidden = HiddenWdg('workhour_data')
            hidden.add_class('spt_workhour_data')

            header_data = {'start_date': str(self.start_date)}
            header_data = jsondumps(header_data).replace('"', "&quot;")
            hidden.set_value(header_data, set_form_value=False )
            top.add(hidden)

        days = []
        for date in self.dates:
            days.append( date.strftime("%Y_%m_%d") )
        today = self.today.strftime("%Y_%m_%d")
        task = self.get_current_sobject()

        if not self.is_refresh:
            self.set_as_panel(top)

        entries = self.entries.get(task.get_code())
        if isinstance(task, Task):
            parent = task.get_parent()
            if not parent:
                disabled = True
            else:
                disabled = False
        else:
            disabled = False

        if not entries:
            entries = {}

        table = Table()
        top.add(table)


        table.add_behavior( {
            "type": 'mouseenter',
            'cbjs_action': '''
            var td = bvr.src_el.getParent(".spt_cell_edit");
            if (td) {
                td.html = td.innerHTML;
            }
            '''
        } )



        if self.use_straight_time:
            row_list = [self.ST_ROW]
            if self.show_overtime:
                row_list.append(self.OT_ROW)
            prefix_list = ['','ot']
        else:
            row_list = [self.STT_ROW, self.ENT_ROW]
            prefix_list = ['stt','ent']
        text = HiddenWdg(self.get_name() )
        text.add_class("spt_data")

        table.add_color("color", "color")
        table.add_styles("width: %spx; float: left"%self.table_width)
        for row_to_draw in row_list:
            tr = table.add_row()
            tr.add_style('line-height','8px')

            td = table.add_blank_cell()
            offset_width = self.MONTH_WIDTH + self.LEFT_WIDTH+8
            td.add_style("min-width: %spx" % offset_width)
            td.add(text)

            # go through each day and draw an input for overtime
            total_hours_st = 0
            total_hours_ot = 0
            search_key = task.get_search_key()

            # Add a label to indicate if the row is straight time or overtime

            time_prefix = ''
            if row_to_draw == self.OT_ROW:
                time_prefix = 'ot'
                div = DivWdg()
                div.add("OT")
                div.add_styles('text-align: right; margin-right: 4px')
                td.add(div)
            elif row_to_draw == self.STT_ROW:
                time_prefix = 'stt'
                div = DivWdg()
                div.add("ST")

                div.add_styles('text-align: right; margin: 0 4px 4px 0')
                td.add(div)
            elif row_to_draw == self.ENT_ROW:
                time_prefix = 'ent'
                div = DivWdg()
                div.add("ET")

                div.add_styles('text-align: right; margin: 0 4px 4px 0')
                td.add(div)


            for idx, day in enumerate(days):
                day_wdg = DivWdg()
                day_wdg.add(day)

                td = table.add_cell()
                td.add_style("width: %spx" % self.day_width)


                text = TextWdg('%sday_%s' % (time_prefix, day))

                if disabled:
                    text.set_option('read_only','true')
                    text.set_attr('disabled','disabled')

                td.add(text)
                text.add_class('spt_day%s' % (time_prefix))
                text.add_styles("width: %spx;text-align: right;padding-left: 2px" %(self.day_width-2))
                #text.add_styles("width: 100%;text-align: right;padding-left: 2px")
                #if day == today:
                #    text.add_style("border: solid 1px black")
                #else:
                #    text.add_border()
                text.add_border()
                text.add_style("box-sizing: border-box")

                week_day = self.weekday_dict[idx]
                if week_day in ['Sat','Sun']:
                    # MAIN: Overtime, weekend
                    if row_to_draw == self.OT_ROW:
                        text.add_color("background", "background2", modifier=[-15,0,5])
                    else:
                        text.add_color("background", "background2", modifier= [0,15,20])

                text.add_style("margin: 0px 1px")
                text.add_style("padding: 2px 3px")

                if row_to_draw == self.OT_ROW:
                    text.add_attr('input_field_type', 'ot')
                else:
                    text.add_attr('input_field_type', 'st')

                if self.kwargs.get('show_all_users')=='true':
                    text.set_option('read_only','true')

                #TODO: while we may have multiple entries per task, we will only use the latest one here
                # for now, making the UI cleaner

                # if a corresponding entry exists, display its value
                entry_list_dict = entries.get(day)
                daily_sum = 0
                value = 0
                entry_list = []
                if entry_list_dict:
                    row_key = self.ROW_DICT.get(row_to_draw)
                    entry_list = entry_list_dict.get(row_key)
                if entry_list:

                    for entry in entry_list:
                        # Check if there is something in the category column.
                        category = entry.get_value("category")
                        if row_to_draw == self.OT_ROW:
                            # Skip if the category field does not have a 'ot' indicated.
                            if not category:
                                print("Warning this work_hour entry has no category [%s]" % entry.get_code())
                                continue

                        # Check if there exist a value in the straight_time column
                        value, delta = self.get_time_value(entry, row_to_draw)
                        if value:

                            text.set_value(value)
                            text.add_attr('orig_input_value', value)

                            if row_to_draw == self.OT_ROW:
                                total_hours_ot += float(delta)
                            else:
                                total_hours_st += float(delta)

                            daily_sum += delta


                # we only use value instead of the sum "daily_sum" for now
                if row_to_draw == self.OT_ROW:
                    self.summary_ot[idx].update({search_key: daily_sum})
                else:
                    self.summary_st[idx].update({search_key: daily_sum})

                script = '''
                        var orig_value = bvr.src_el.getAttribute("orig_input_value");
                        var input_field_type = bvr.src_el.getAttribute("input_field_type");

                        bvr.src_el.value = bvr.src_el.value.strip();
                        if (bvr.src_el.value == '') {
                            if (orig_value) {
                                bvr.src_el.value = 0;
                            }
                            else {
                                return;
                            }
                        }
                        else if (bvr.src_el.value == orig_value) {
                            return;
                        }


                        bvr.prefix_list.splice( bvr.prefix_list.indexOf(bvr.time_prefix),1)
                        var other_time_prefix = bvr.prefix_list[0];
                        spt.work_hour.update_total(bvr, '.spt_day' + bvr.time_prefix);

                        // register this as changed item
                        var all_top_el = bvr.src_el.getParent(".spt_work_hours_top");

                        var values1 = spt.api.Utility.get_input_values(all_top_el, '.spt_day'+ bvr.time_prefix, false);
                        var values2 = spt.api.Utility.get_input_values(all_top_el, '.spt_day'+ other_time_prefix, false);

                        // Merge values from straight time and overtime fields in values variable.
                        for (var attr in values2) {
                            values1[attr] = values2[attr];
                        }

                        for (val in values1) {
                            if (values1[val] && isNaN(values1[val])) {
                                spt.error('You have non-numeric values in your work hours. Please correct it: ' + values[val]);
                                return;
                            }
                        }
                        delete values1.data;
                        var value_wdg = all_top_el.getElement(".spt_data");

                        var value = JSON.stringify(values1);
                        value_wdg.value = value;

                        var layout = bvr.src_el.getParent(".spt_layout");
                        var version = layout.getAttribute("spt_version");
                        if (version == "2") {
                            spt.table.set_layout(layout);
                            var undo = {
                                new_value: value,
                                type: 'work_hour',
                                get_data: function() {
                                    return
                                },
                                get_extra_data: function() {
                                    alert("get_extra_data on work hours");

                                },
                            }
                            spt.table.accept_edit(all_top_el, value, false, {undo: undo});
                        }
                        else {
                            var cached_data = {};
                            spt.dg_table.edit.widget = all_top_el;
                            spt.dg_table.inline_edit_cell_cbk( value_wdg, cached_data );
                        }
                        '''
                # accept on pressing Enter
                behavior = {
                   'type': 'keydown',
                   'time_prefix': time_prefix,
                   'prefix_list': prefix_list,
                   'cbjs_action': '''
                   if (evt.key=='enter') {
                       %s
                    }

                '''%script}

                text.add_behavior(behavior)

                behavior = {
                   'type': 'blur',
                   'time_prefix': time_prefix,
                   'prefix_list': prefix_list,
                   'cbjs_action': '''
                        %s

                '''%script}
                text.add_behavior(behavior)


            text = TextWdg("total")
            td = table.add_cell(text)
            td.add_style("width: 35px")
            text.add_style("box-sizing: border-box")


            text.add_attr('spt_total', '.spt_total%s' % (time_prefix))
            text.add_class('spt_total%s' % (time_prefix))
            text.add_styles("width: %spx; text-align: right; padding-right: 3px; margin-left: 5px;"%self.day_width)
            text.set_attr("readonly", "readonly")
            text.add_border()


            # MAIN: Overtime, total.
            if row_to_draw == self.OT_ROW:
                text.add_color("background", "background2", modifier=[5,-15,0])
                if total_hours_ot:
                    text.set_value("%0.1f" % total_hours_ot)
                self.summary_ot[7].update({search_key: total_hours_ot})
            else:
                text.add_color("background", "background2", modifier=[20,0,15])
                if total_hours_st:
                    text.set_value("%0.1f" % total_hours_st)
                self.summary_st[7].update({search_key: total_hours_st})
            td = table.add_blank_cell()
            td.add_style('width: 100%')

        return top


    def get_text_value(self):
        if not self.preprocessed:
            self.preprocess()

        days = []
        for date in self.dates:
            days.append( date.strftime("%Y_%m_%d") )
        today = self.today.strftime("%Y_%m_%d")
        task = self.get_current_sobject()

        entries = self.entries.get(task.get_code())
        if isinstance(task, Task):
            parent = task.get_parent()
            if not parent:
                disabled = True
            else:
                disabled = False
        else:
            disabled = False

        if not entries:
            entries = {}



        if self.use_straight_time:
            row_list = [self.ST_ROW]
            if self.show_overtime:
                row_list.append(self.OT_ROW)
        else:
            row_list = [self.STT_ROW, self.ENT_ROW]

        total_hours_ot = 0
        total_hours_st = 0

        month_dict_ot = {}
        month_dict_st = {}
        for idx, day in enumerate(days):
            month = day.split('_')[1]
            month_dict_ot[month] = []
            month_dict_st[month] = []

        for row_to_draw in row_list:


            # go through each day and draw an input for overtime

            search_key = task.get_search_key()

            # Add a label to indicate if the row is straight time or overtime

            time_prefix = ''
            if row_to_draw == self.OT_ROW:
                time_prefix = 'ot'
                total_hours_ot = 0
            else:
                total_hours_st = 0




            for idx, day in enumerate(days):

                month = day.split('_')[1]
                # if a corresponding entry exists, display its value
                entry_list_dict = entries.get(day)
                #daily_sum = 0
                value = 0
                entry_list = []
                if entry_list_dict:
                    row_key = self.ROW_DICT.get(row_to_draw)
                    entry_list = entry_list_dict.get(row_key)
                if entry_list:

                    for entry in entry_list:
                        # Check if there is something in the category column.
                        category = entry.get_value("category")
                        if row_to_draw == self.OT_ROW:
                            # Skip if the category field does not have a 'ot' indicated.
                            if not category:
                                print("Warning this work_hour entry has no category [%s]" % entry.get_code())
                                continue

                        # Check if there exist a value in the straight_time column
                        value, delta = self.get_time_value(entry, row_to_draw)
                        if value:


                            if row_to_draw == self.OT_ROW:
                                #total_hours_ot += float(value)
                                hours_list = month_dict_ot.get(month)
                                hours_list.append(float(value))
                            else:
                                #total_hours_st += float(value)
                                hours_list = month_dict_st.get(month)
                                hours_list.append(float(value))




                            #daily_sum += value

                # we only use value instead of the sum "daily_sum" for now
                """
                if row_to_draw == self.OT_ROW:
                    self.summary_ot[idx].update({search_key: value})
                else:
                    self.summary_st[idx].update({search_key: value})
                """



        final_display = []
        month_keys = sorted(month_dict_st.keys())
        month_label_dict = {'01':'Jan', '02': 'Feb', '03':'Mar', '04': 'Apr', '05':'May', '06': 'Jun', '07':'Jul', '08': 'Aug', '09':'Sep', '10': 'Oct', '11':'Nov', '12': 'Dec'}

        final_sum = 0

        if self.show_overtime:

            for month in month_keys:
                label = month_label_dict.get(month)
                # for now, show the total sum
                final_sum = sum(month_dict_ot[month]) +  sum(month_dict_st[month])
            final_sum = str(final_sum)
            final_display.append(final_sum)
        else:
            for month in month_keys:
                label = month_label_dict.get(month)
                final_sum = sum(month_dict_ot[month]) +  sum(month_dict_st[month])
            final_sum = str(final_sum)
            final_display.append(final_sum)
        return ''.join(final_display)


    def get_group_bottom_wdg(self, sobjects):
        sks = []
        for sobj in sobjects:
            sks.append(sobj.get_search_key())

        return self.get_bottom_wdg(sks)


    def get_bottom_wdg(self, search_keys=[]):
        # check if the user has enabled it
        info = self.check_bottom_wdg()

        if info.get('check') == False:
            return None

        if info.get('mode') != 'total':
            top = DivWdg()
            top.add("Only [total] is supported. Please change it in Edit Column Definition")
            return top

        self.today = datetime.date.today()

        if self.is_refresh:
            top = Widget()
        else:
            top = DivWdg()

        days = []
        for date in self.dates:
            days.append( date.strftime("%Y_%m_%d") )

        today = self.today.strftime("%Y_%m_%d")

        table = Table()
        top.add(table)

        row_list = [self.ST_ROW]
        if self.show_overtime:
            row_list.append( self.OT_ROW)

        for row_to_draw in row_list:

            table.add_row()
            table.add_color("color", "color")
            table.add_styles("width: %spx; float: left"%self.table_width)

            td = table.add_blank_cell()
            td.add_style("min-width: %spx" % (self.MONTH_WIDTH + self.LEFT_WIDTH+8))
            time_prefix = ''
            if row_to_draw == self.OT_ROW:
                time_prefix = 'ot'
                div = DivWdg()
                div.add("OT")

                div.add_styles('text-align: right; margin-right: 4px; margin-bottom: 6px')
                td.add(div)
            elif row_to_draw == self.STT_ROW:
                time_prefix = 'stt'
                div = DivWdg()
                div.add("ST")

                div.add_styles('text-align: right; margin-right: 4px; margin-bottom: 6px')
                td.add(div)
            elif row_to_draw == self.ENT_ROW:
                time_prefix = 'ent'
                div = DivWdg()
                div.add("ET")

                div.add_styles('text-align: right; margin-right: 4px; margin-bottom: 6px')
                td.add(div)


            for idx, day in enumerate(days):
                day_wdg = DivWdg()
                day_wdg.add(day)

                td = table.add_cell()
                td.add_style("width: %spx" % self.day_width)
                # keep it as text input for consistent alignment
                text = TextWdg("%sday_%s" % (time_prefix, day) )

                if row_to_draw == self.OT_ROW:
                    sobj_daily_dict = self.summary_ot[idx]
                else:
                    sobj_daily_dict = self.summary_st[idx]

                if search_keys:
                    sobj_daily_sub_dict = Common.subset_dict(sobj_daily_dict, search_keys)
                else:
                    sobj_daily_sub_dict = sobj_daily_dict

                daily_total = 0
                for value in sobj_daily_sub_dict.values():
                    if value:
                        daily_total += value

                text.set_value(daily_total)
                td.add(text)

                text.add_class("spt_day%s" % (time_prefix))
                text.add_style("width: %spx"%(self.day_width-2))
                #text.add_style("width: 100%")
                text.add_style("text-align: right")
                text.add_style("padding: 2px 3px")
                text.add_style('font-weight: 500')
                text.set_attr("readonly", "readonly")
                text.add_style("box-sizing: border-box")
                # grey out the text color
                text.add_color('color', 'color', +40)
                text.add_style("margin: 0px 1px")

                text.add_border()

                if day == today:
                    #text.add_style("border: solid 1px black")
                    pass
                elif idx in [0,6]:
                    if row_to_draw == self.OT_ROW:
                        # FOOTER: Overtime, weekends
                        text.add_color("background", "background2", modifier=[-15,0,5])
                    else:
                        # FOOTER: Straight time, weekends
                        text.add_color("background", "background2", modifier=[0,15,20])


            text = TextWdg("total")
            daily_total = 0
            if row_to_draw == self.OT_ROW:
                sobj_daily_dict = self.summary_ot[7]
            else:
                sobj_daily_dict = self.summary_st[7]

            if search_keys:
                sobj_daily_sub_dict = Common.subset_dict(sobj_daily_dict, search_keys)
            else:
                sobj_daily_sub_dict = sobj_daily_dict
            for value in sobj_daily_sub_dict.values():
                if value:
                    daily_total += value
            text.set_value(daily_total)

            td = table.add_cell(text)
            text.add_class("spt_total%s" % (time_prefix))
            td.add_style("width: %spx"%self.day_width)
            text.add_styles("font-weight: 500;width: %spx; text-align: right; padding-left: 2px; margin-left: 5px"%(self.day_width))
            text.add_style("box-sizing: border-box")


            text.set_attr("readonly", "readonly")
            text.add_color('color', 'color', +40)
            text.add_border()

            if row_to_draw == self.OT_ROW:
                # FOOTER: Overtime, total.
                text.add_color("background", "background2", modifier=[5,-15,0])
            else:
                # FOOTER: Straight time, total
                text.add_color("background", "background2", modifier=[20,0,15])

            td = table.add_blank_cell()
            td.add_style('width','100%')

        return top



class WorkHoursElementAction(DatabaseAction):

    def execute(self):

        value = self.get_value()
        if value:
            data = jsonloads(value)
        else:
            data = {}

        task = self.sobject
        parent = task.get_parent()

        self.unit = self.get_option("unit")
        if not self.unit:
            self.unit = "hour"

        self.use_straight_time = self.get_option("use_straight_time")
        #self.use_straight_time = 'false'
        if self.use_straight_time == 'false':
            self.use_straight_time = False
        else:
            self.use_straight_time = True

        # Do this for now. EXIT if the parent of task can't be found..
        if not parent:
            return

        # TODO: make it work if self.sobject is not an instance of a Task
        use_task_code = True

        # match assigned to avoid deleting work hours entries made on the same task by other users
        user = Environment.get_user_name()
        entries = parent.get_related_sobjects("sthpw/work_hour")

        # filter out just for this task
        if use_task_code:
            entries = [x for x in entries if x.get_value('task_code') == task.get_code() and x.get_value('login') == user]

        entry_dict = {}
        for key, value in data.items():
            if self.use_straight_time:
                if not (key.startswith("day_") or key.startswith("otday_")):
                    continue
            else:
                if not (key.startswith("day_") or key.startswith("sttday_") or key.startswith("entday_")):
                    continue
                start_value = data


            tmp, year, month, day = key.split("_")
            date = "%s-%s-%s 00:00:00" % (year,month,day)
            #OVER_TIME_TYPE = 'ot'

            exists = False
            # TODO: we should allow multiple entiries per task per day and just
            # have a special UI to edit individual entries post creation.
            for entry in entries:
                entry_day = entry.get_value("day")
                if entry_day == date:
                    if self.use_straight_time:

                        if key.startswith("day_"):
                            if entry.get_value("category") in ['',WorkHoursElementWdg.ST] :
                                exists = True
                                break
                        if key.startswith("otday_"):
                            if WorkHoursElementWdg.OT == entry.get_value("category"):
                                exists = True
                                break
                    else:
                         # only supports regular hours for start and end time
                         if key.startswith("sttday_"):
                            if entry.get_value("category") in ['',WorkHoursElementWdg.ST] :
                                exists = True
                                break
                         elif key.startswith("entday_"):
                            if entry.get_value("category") in ['',WorkHoursElementWdg.ST] :
                                exists = True
                                break


            if not exists:
                entry = entry_dict.get(date)
                if not entry:
                    # create a new one
                    entry = SearchType.create("sthpw/work_hour")
                    if parent:
                        entry.set_parent(parent)
                    entry.set_value("task_code", task.get_code() )
                    entry.set_value("process", task.get_value('process'))
                    entry.set_value("day", date)
                    entry.set_user()
                    entry.set_project()

            if not self.use_straight_time:
                # only enter standard time for now
                entry.set_value("project_code", task.get_value('project_code'))
                entry.set_value("category", WorkHoursElementWdg.ST)
                if not value:
                    continue

                date_part = ''
                if key.startswith("entday_"):
                    date_part = key.replace('entday_','')
                    date_part = date_part.replace('_','-')
                    value = value.zfill(4)
                    time = parser.parse('%s %s' %(date_part, value))
                    entry.set_value("end_time", time)

                elif key.startswith("sttday_"):
                    date_part = key.replace('sttday_','')
                    date_part = date_part.replace('_','-')
                    value = value.zfill(4)
                    time = parser.parse('%s %s' %(date_part, value))
                    entry.set_value("start_time", time)

                entry_dict[date] = entry

                #entry.commit()

            else:
                if value == '' or value == '0':
                    if exists:
                        entry.delete()

                elif value == '%s'% entry.get_value('straight_time'):
                    # prevent commit the same value again
                    continue
                else:
                    #
                    entry.set_value("straight_time", value)
                    entry.set_value("project_code", task.get_value('project_code'))

                    if key.startswith("otday_"):
                        entry.set_value("category", WorkHoursElementWdg.OT)
                    else:
                        entry.set_value("category", WorkHoursElementWdg.ST)


                    entry.commit()

            for key, entry in entry_dict.items():

                # set the straight_time as well
                st_time = str(entry.get_value('start_time'))
                end_time = str(entry.get_value('end_time'))
                if st_time and end_time:
                    st_time_obj = parser.parse(st_time)
                    end_time_obj = parser.parse(end_time)

                    delta = (end_time_obj - st_time_obj).seconds / WorkHoursElementWdg.UNIT_DICT[self.unit]
                    entry.set_value("straight_time", delta)

                entry.commit()








