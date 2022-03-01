###########################################################
#
# Copyright (c) 2014, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#


__all__ = ['GanttLayoutWdg', 'GanttTableElementWdg', 'GanttCbk', 'GanttHeaderWdg', 'GanttWdg', 'GanttTestWdg', 'GanttTest2Wdg']


from tactic.ui.common import BaseRefreshWdg, BaseTableElementWdg
from tactic.ui.panel import TableLayoutWdg

from pyasm.common import jsonloads, jsondumps, SPTDate
from pyasm.biz import Pipeline, ExpressionParser, ProdSetting, Task
from pyasm.web import DivWdg, Canvas, WebContainer, Table, HtmlElement
from pyasm.command import DatabaseAction
from pyasm.search import Search, SearchType
from pyasm.widget import HiddenWdg, TextWdg, IconWdg

from tactic.ui.widget import IconButtonWdg
from tactic.ui.panel import ToolLayoutWdg


from tactic.ui.table import GanttElementWdg

import dateutil
from dateutil import parser, rrule
from dateutil.relativedelta import *
from datetime import datetime, timedelta

import six
basestring = six.string_types



class GanttLayoutWdg(ToolLayoutWdg):

    #ARGS_KEYS = CustomLayoutWdg.ARGS_KEYS.copy()
    #ARGS_KEYS['search_type'] = 'search type of the sobject to be displayed'


    def get_kwargs_keys(cls):
        return ['task_expression', 'edit', 'special_days', 'handler', 'start_column', 'end_column', 'range_start_date', 'range_end_date', 'show_header_shelf', 'gantt_class','auto_grouping','document_mode', 'fixed_table','window_resize_offset', 'resizable_mode', 'use_mouse_wheel', 'left_width', 'parent_key', 'show_grid','show_week_hightlight','show_month_highlight', 'show_time', 'processes']
    get_kwargs_keys = classmethod(get_kwargs_keys)




    def can_use_gear(self):
        return False

    def can_save(self):
        return True

    def get_content_wdg(self):

        edit = self.kwargs.get("edit")
        if edit in [False, 'false']:
            edit = False
        else:
            edit = True


        height = self.kwargs.get("height")
        if not height:
            height = "auto"


        top = DivWdg()

        # draw the outer table

        self.resizable_mode = self.kwargs.get("resizable_mode")
        if not self.resizable_mode:
            self.resizable_mode = "table"

        # This only matters with flex
        left_width = 0
        resizable_min_width = 0
        tab_vertical_scroll = True
        gantt_width = 0
        show_grid = True

        #self.resizable_mode = "flex"

        if self.resizable_mode == "fixed":
            table = Table()
            table.add_row()
            left = table.add_cell()
            right = table.add_cell()

            left.add_style("width: 1%")

        elif self.resizable_mode == "flex":

            table = DivWdg()
            table.add_style("display: flex")
            table.add_style("align-items: stretch")
            table.add_style("align-content: stretch")
            table.add_style("box-sizing: border-box")
            table.add_style("width: 100%")
            table.add_style("height: auto")

            table.add_class("spt_resizable_cell")

            left_width = self.kwargs.get("left_width") or 285
            resizable_min_width = 510
            tab_vertical_scroll = False

            left = DivWdg()
            table.add(left)

            show_grid = self.kwargs.get("show_grid")
            if show_grid in ['false', False]:
                show_grid = False
            else:
                show_grid = True
            if not show_grid:
                left.add_style("display: none")

            left.add_style("width: %s" % left_width)
            left.add_style("min-width: %s" % left_width)
            left.add_style("box-sizing: border-box")


            right = DivWdg()
            table.add(right)
            right.add_style("width: auto")
            right.add_class("spt_resizable_cell")
            right.add_style("box-sizing: border-box")

            gantt_width = self.kwargs.get("gantt_width") or 0
            #gantt_width = 2000
            if gantt_width:
                # TEST TEST
                inner = DivWdg()
                inner.add_class("spt_gantt_scroll")
                right.add(inner)
                inner.add_style("width: %s" % gantt_width)
                right.add_style("overflow-x: auto")
                right = inner
            else:
                right.add_class("spt_gantt_scroll")




        elif self.resizable_mode == "table":
            from tactic.ui.container import ResizableTableWdg
            table = ResizableTableWdg()
            table.add_row()
            left = table.add_cell()
            right = table.add_cell()

            left.add_style("width: 1%")

        else:
            raise Exception("Resizable mode [%s] not supported" % self.resizable_mode)


        if gantt_width:
            top.add_attr("spt_gantt_width", gantt_width)



        top.add(table)



        top.add_class("spt_gantt_layout_top")
        table.add_style("border-collapse: collapse")
        table.add_style("width: 100%")

        table.add_behavior( {
            'type': 'load',
            'tab_vertical_scroll': tab_vertical_scroll,
            'resizable_mode': self.resizable_mode,
            'cbjs_action': '''
            if (window.onresize) {
                window.onresize()
            }

            // supress tab vertical scroll
            if (! bvr.tab_vertical_scroll) {
                var tab_content = bvr.src_el.getParent(".spt_tab_content");
                if (tab_content) {
                    tab_content.setStyle("overflow", "");
                    tab_content.setStyle("overflow-x", "hidden");
                    tab_content.setStyle("overflow-y", "hidden");
                }
            }

            // This messes up the width
            /*
            if (bvr.resizable_mode == "table") {
                setTimeout( function() {
                    spt.table.set_column_widths(75);
                }, 250 )
            }
            */
            '''
        } )


        left.add_class("spt_resizable")

        left.add_style("vertical-align: top")
        left.add_style("overflow-x: auto")
        left.add_class("spt_gantt_layout_left")
        right.add_style("vertical-align: top")
        right.add_class("spt_gantt_layout_right")


        border_color = left.get_color("table_border")
        left.add_border(color=border_color)
        right.add_border(color=border_color)
        left.add_style("overflow: hidden")


        # draw the table
        kwargs = self.kwargs.copy()
        if self.kwargs.get("view"):
            kwargs['view'] = self.kwargs.get("view")
        elif not self.kwargs.get("element_names"):
            kwargs['element_names'] = ['parent','process','description','status', 'assigned','bid_start_date','bid_end_date', 'days_due']
        else:
            kwargs['element_names'] = self.kwargs.get("element_names")
        kwargs['show_shelf'] = False
        kwargs['is_inner'] = True
        kwargs['show_search_limit'] = False

        kwargs['height'] = height
        #kwargs['group_elements'] = ['process']
        kwargs['layout'] = 'table'

        # need to pass this through so the table uses the same id
        kwargs['table_id'] = self.table_id


        # FIXME: this is very WONKY --- need to clean this up.
        # Basically, the search criteria from spt.dg_table.search_cbk has to be
        # passed into TableLayouWdg directly in order for it to be respected
        # ie: otherwise grouping doesn't work
        from tactic.ui.filter import FilterData
        filter_data = FilterData()
        filter_data = FilterData.get_from_cgi()

        from pyasm.web import WebContainer
        web = WebContainer.get_web()
        values = web.get_form_value("json")
        kwargs['filter'] = values
        kwargs['expand_on_load'] = True
        kwargs['width'] = "100%"

        kwargs['window_resize_offset'] = self.kwargs.get("window_resize_offset")


        from tactic.ui.panel import ViewPanelWdg
        #layout = ViewPanelWdg(**kwargs)
        layout = TableLayoutWdg(**kwargs)
        layout.set_sobjects(self.sobjects)

        #layout.add_style("margin: -1px -1px -1px -1px")

        if self.kwargs.get("temp") == True:
            return layout

        layout_html = layout.get_buffer_display()
        left.add(layout_html)

        # table layout will reorder the sobjects
        self.sobjects = layout.get_sobjects()

        group_rows = layout.group_rows
        if not group_rows:
            groups_rows = []


        expression = self.kwargs.get("task_expression")
        if not expression:
            tasks = self.sobjects
            parser = None
        else:
            parser = ExpressionParser()
            tasks = parser.eval(expression, self.sobjects)


        # draw the gantt
        #right.add_style("min-width: 600px")

        min_date = self.kwargs.get("range_start_date")
        max_date = self.kwargs.get("range_end_date")


        if not min_date or not max_date:
            task_min_date, task_max_date = self.get_date_range(tasks)
            if not min_date:
                min_date = task_min_date
            if not max_date:
                max_date = task_max_date


        kwargs['range_start_date'] = min_date
        kwargs['range_end_date'] = max_date


        kwargs['start_column'] = self.kwargs.get("start_column") or "bid_start_date"
        kwargs['end_column'] = self.kwargs.get("end_column") or "bid_end_date"



        show_time = self.kwargs.get("show_time")
        if show_time in ['false', False]:
            show_time = False
        else:
            show_time = True



        show_header_shelf = self.kwargs.get("show_header_shelf")

        header_div = DivWdg()
        right.add(header_div)
        header_div.add_style("height: 30px")
        header = GanttHeaderWdg(
                range_start_date=kwargs.get("range_start_date"),
                range_end_date=kwargs.get("range_end_date"),
                show_header_shelf=show_header_shelf,
                window_resize_offset=kwargs.get("window_resize_offset"),
                min_width=resizable_min_width,
                show_time=show_time,
        )
        header_div.add_class("spt_resizable")
        header_div.add(header)
        header_div.add_style("margin-top: -1px")
        border_color = header_div.get_color("table_border")
        header_div.add_border(color=border_color, size="1px 0px 1px 0px")
        header_div.add_style("overflow: hidden")

        if resizable_min_width:
            header_div.add_style("min-width: %s" % resizable_min_width)


        # FIXME: even if this behvaior works with task, it shouldn't be here.
        """
        header_div.add_behavior( {
            'type': 'listen',
            'event_name': 'update|sthpw/task',
            'cbjs_action': '''

            var layout = bvr.src_el.getParent(".spt_layout");
            var top = bvr.src_el.getParent(".spt_gantt_layout_top");
            var ranges = top.getElements(".spt_range_top");

            // change the background color to match the table
            for (i = 0; i < ranges.length; i++) {
                ranges[i].setStyle("background", "");
            }
            '''
        } )
        """




        header_div.add_behavior( {
            'type': 'listen',
            'event_name': 'insert|tableId|%s' % self.table_id,
            'cbjs_action': '''

            if (! bvr.src_el.isVisible()) {
                return;
            }

            var layout = bvr.src_el.getParent(".spt_layout");
            var gantt_top = layout.getElement(".spt_gantt_top");
            spt.gantt.set_top( gantt_top );

            var firing_element = bvr.firing_element;
            var insert_location = bvr.firing_data.insert_location;

            var gantt_rows = gantt_top.getElements(".spt_gantt_row_item");

            if (firing_element.hasClass("spt_table_insert_row")) {
                var gantt_type = "range";
            }
            else {
                var gantt_type = "group";
            }

            var row = bvr.firing_element;

            // FIXME: why is this NULL!!!!!
            var group_level = row.getAttribute("spt_group_level");
            if (group_level == null) {
                group_level = 2;
            }

            var index = row.rowIndex;

            var gantt_el = gantt_rows[index-1];
            var gantt_row = spt.gantt.add_new_row(gantt_el, gantt_type, null, insert_location);
            gantt_row.setAttribute("spt_group_level", group_level);

            if (group_level) {
                var inside = gantt_row.getElement(".spt_range");
                if (inside) {
                    inside.setAttribute("spt_group_level", group_level);
                }
            }

            // get all of the ranges
            var gantt_ranges = gantt_row.getElements(".spt_range");

            var data = {}
            for (var i = 0; i < gantt_ranges.length; i++) {

                var gantt_range = gantt_ranges[i];

                var update_key = gantt_range.getAttribute("spt_update_key");
                var search_key = null;

                data[update_key] = {
                    bid_start_date: gantt_range.getAttribute("spt_start_date"),
                    bid_end_date: gantt_range.getAttribute("spt_end_date"),
                    //bid_duration: info.duration,
                }
                var json_data = JSON.stringify(data);


                // FIXME: make this more explicit
                if (update_key == search_key) {
                    spt.table.add_extra_value(row, start_column, info.start_date)
                    spt.table.add_extra_value(row, end_column, info.end_date)
                }
                else {
                    var data_column = "data";
                    spt.table.add_extra_value(row, data_column, json_data)
                }

            }


            '''
        } )


        header_div.add_behavior( {
            'type': 'listen',
            'event_name': 'reorderX|%s' % self.search_type,
            'cbjs_action': '''

            var row = bvr.firing_element;
            var data = bvr.firing_data;

            var index = data.index;
            var prev_index = data.prev_index;
            var inject_el_index = data.inject_el_index;

            var layout = bvr.src_el.getParent(".spt_layout");
            var gantt_top = layout.getElement(".spt_gantt_top");
            spt.gantt.set_top( gantt_top );

            var gantt_rows = gantt_top.getElements(".spt_gantt_row_item");

            var gantt_row = gantt_rows[prev_index];
            var inject_el = gantt_rows[inject_el_index];

            // bring along all group_levels higher than this one
            var group_level = gantt_row.getAttribute("spt_group_level");
            var rows_to_move = [];
            rows_to_move.push(gantt_row);

            var sibling = gantt_row.getNext();
            while (sibling != null) {
                var sibling_group_level = sibling.getAttribute("spt_group_level");

                if (sibling_group_level > group_level) {
                    rows_to_move.push(sibling);
                } else {
                    break;
                }
                sibling = sibling.getNext();

            }
            rows_to_move.reverse();

            // Move rows after inject_el
            for (var i = 0; i < rows_to_move.length; i++) {
                rows_to_move[i].inject(inject_el, "after");
            }

            /*
            var group_ranges = spt.gantt.get_group_ranges(gantt_row);
            for (var j = 0; j < group_ranges.length; j++) {
                var group_range = group_ranges[j];
                spt.gantt.update_group(group_range);
            }*/

            spt.gantt.update_all_groups();



            '''
        } )



        header_div.add_behavior( {
            'type': 'load',
            'num_rows': len(self.sobjects),
            'resizable_mode': self.resizable_mode,
            'resizable_xoffset': left_width,
            'show_grid': show_grid,
            'cbjs_action': '''
            var count = 0;

            var layout = bvr.src_el.getParent(".spt_layout");
            var content = layout.getElement(".spt_table_content");
            var scroll = layout.getElement(".spt_table_scroll");
            if (!scroll) {
                scroll = content;
            }
            var header = layout.getElement(".spt_table_header_row");


            var top = bvr.src_el.getParent(".spt_gantt_layout_top");
            var gantt_top = top.getElement(".spt_gantt_top");
            var gantt_scroll = gantt_top.getElement(".spt_gantt_scroll");
            var gantt_items_top = gantt_top.getElement(".spt_gantt_items_top");
            var ranges = top.getElements(".spt_range_top");
            var groups = top.getElements(".spt_group_range_top");

            var gantt_width = top.getAttribute("spt_gantt_width");
            var resizable_mode = bvr.resizable_mode;
            var resizable_xoffset = bvr.resizable_xoffset;
            var resizable_top = gantt_top.getParent(".spt_resizable_cell")
            if (resizable_top) {
                var resizable_els = resizable_top.getElements(".spt_resizable");
                var last_top_size = resizable_top.getSize();
            }
            var show_grid = bvr.show_grid;

            var canvas = gantt_top.getElement(".spt_gantt_canvas");

            // do this right away first
            var rows = layout.getElements(".spt_table_row");
            var insert_rows = layout.getElements(".spt_table_insert_row");
            var group_rows = layout.getElements(".spt_table_group_row");

            var row_items = content.getElements(".spt_table_row_item");
            var gantt_items = gantt_items_top.getElements(".spt_gantt_row_item");

            // make sure the canvas width is in sync with the css width
            var width = canvas.getStyle("width");
            canvas.setAttribute("width", width);

            setTimeout( function() {
                spt.gantt.set_top(gantt_top);
                spt.gantt.clear();
                spt.gantt.draw_grid();
                spt.gantt.draw_connects();
            }, 100);



            // re-find get all of the rows in case it changes
            var rows_interval_id = setInterval( function() {
                if (! layout.isVisible()) {
                    return;
                }

                rows = layout.getElements(".spt_table_row");
                insert_rows = layout.getElements(".spt_table_insert_row");
                group_rows = layout.getElements(".spt_table_group_row");

                ranges = top.getElements(".spt_range_top");
                groups = top.getElements(".spt_group_range_top");

                row_items = content.getElements(".spt_table_row_item");
                gantt_items = gantt_items_top.getElements(".spt_gantt_row_item");


            }, 2000);
            bvr.src_el.rows_interval_id = rows_interval_id;



            // FIXME: this probably should be put in a general location

            var hexToRGB = function(hex, alpha) {
                var r = parseInt(hex.slice(1, 3), 16),
                    g = parseInt(hex.slice(3, 5), 16),
                    b = parseInt(hex.slice(5, 7), 16);

                if (alpha) {
                    return "rgba(" + r + ", " + g + ", " + b + ", " + alpha + ")";
                } else {
                    return "rgb(" + r + ", " + g + ", " + b + ")";
                }
            }



            // set the initial size
            if (resizable_mode == "table") {
                if ( resizable_top) {
                    var top_size = resizable_top.getSize();
                    if (top_size.x != last_top_size.x) {
                        for (var i = 0; i < resizable_els.length; i++) {
                            resizable_els[i].setStyle("width", top_size.x - 5);
                            last_top_size = top_size.x - 5;
                        }
                    }
                }
            }
            else if (resizable_mode == "flex") {
                var top_size = document.id(document.body).getSize();
                var gantt_width = top.getAttribute("spt_gantt_width");
                if (top_size.x != last_top_size.x) {
                    for (var i = 0; i < resizable_els.length; i++) {

                    if (gantt_width) {
                        resizable_els[i].setStyle("width", gantt_width);
                    }
                    else {
                        var extra_offset = 10;
                        resizable_els[i].setStyle("width", top_size.x - resizable_xoffset - extra_offset);
                    }
                    last_top_size = top_size.x;
                    }
                }
            }





            var interval_id = setInterval( function() {

                if (! top.isVisible()) {
                    return;
                }
                if (!rows) {
                    return;
                }

                spt.gantt.set_top(gantt_top);

                if (show_grid) {
                    var header_height = header.getStyle("height");
                    bvr.src_el.setStyle("height", header_height);
                }

                gantt_scroll.setStyle("margin-top", "0");

                if (row_items.length != gantt_items.length) {
                    //console.log(row_items.length + " : " + gantt_items.length);
                    return;
                }


                handled_search_keys = [];
                var j = 0;
                for (var i = 0; i < row_items.length; i++) {

                    var range = gantt_items[j];

                            j++;

                    if (!range) {
                    continue;
                    }

                    var row = row_items[i];

                    if (row.hasClass("spt_row_changed") || row.hasClass("spt_table_insert_row") || row.hasClass("spt_row_hover") || row.hasClass("spt_table_selected") ) {
                        var background = row.getStyle("background-color");
                        range.setStyle("background-color", background);
                    }
                    else {
                        range.setStyle("background-color", "");
                    }



                    if (row.hasClass("spt_table_group_row")) {
                        var background = row.getStyle("background-color");
                        var rgb = hexToRGB(background, 0.5);
                        range.setStyle("background-color", rgb);
                    }



                    if (!show_grid) {
                        var row_height = 40;
                    }
                    else {
                        var row_height = row.getSize().y;
                    }

                    if (!row_height) {
                        var display = row.getStyle("display");
                        if (display == "none") {
                            range.setStyle("display", "none");
                        }
                    }
                    else {
                        range.setStyle("height", row_height);
                        range.setStyle("display", "");
                    }
                }

/*
                for (var i = 0; i < group_rows.length; i++) {
                    var row_height = group_rows[i].getSize().y;
                    var group = groups[i];
                    if (!group) {
                        continue;
                    }

                    if (!row_height) {
                        groups[i].setStyle("display", "none");
                    }
                    else {
                        groups[i].setStyle("display", "");
                        groups[i].setStyle("height", row_height);
                    }
                }
*/





                // resize all of the resizable elements
                if (resizable_mode == "table") {
                /*
                    if ( resizable_top) {
                        var top_size = resizable_top.getSize();
                        if (top_size.x != last_top_size.x) {
                            for (var i = 0; i < resizable_els.length; i++) {
                                resizable_els[i].setStyle("width", top_size.x - 5);
                                last_top_size = top_size.x - 5;
                            }
                        }
                    }
                */
                }
                else if (resizable_mode == "flex") {
                    var top_size = document.id(document.body).getSize();
                    var gantt_width = top.getAttribute("spt_gantt_width");
                    if (top_size.x != last_top_size.x) {
                        for (var i = 0; i < resizable_els.length; i++) {

                            if (gantt_width) {
                                resizable_els[i].setStyle("width", gantt_width);
                            }
                            else {
                                var extra_offset = 10;
                                resizable_els[i].setStyle("width", top_size.x - resizable_xoffset - extra_offset);
                            }
                            last_top_size = top_size.x;
                        }
                    }
                }



                // make sure the canvas width is in sync with the css width
                var width = canvas.getStyle("width");
                var attr_width = canvas.getAttribute("width");

                if (width != attr_width) {
                    canvas.setAttribute("width", width);
                }

                // any asynchronous action that modifies DOM positions (in this case, header height
                // change), needs to re-draw arrows
                /*
                spt.gantt.clear();
                spt.gantt.draw_grid();
                */
                spt.gantt.clear("connector");
                spt.gantt.draw_connects();


                count += 1;

                var scroll_top = content.getParent().scrollTop;
                gantt_scroll.setStyle("margin-top", "-"+scroll_top);

            }, 50);

            bvr.src_el.interval_id = interval_id;
            
            '''
        } )

        header_div.add_behavior( {
            'type': 'unload',
            'cbjs_action': '''
            var interval_id = bvr.src_el.interval_id;
            clearInterval(interval_id);
            //var scroll_interval_id = bvr.src_el.scroll_interval_id;
            //clearInterval(scroll_interval_id);
            var rows_interval_id = bvr.src_el.rows_interval_id;
            clearInterval(rows_interval_id);

            '''
        }
        )



        if self.kwargs.get("temp") == True:
            return top


        special_days = self.kwargs.get("special_days") or []
        if special_days and isinstance(special_days, basestring):
            special_days = special_days.replace("'", '"')
            special_days = jsonloads(special_days) or []


        search_type = self.kwargs.get("search_type")

        handler = self.kwargs.get("handler")
        if not handler:
            handler = "task"


        gantt_width = 300

        gantt_kwargs = {
                "search_type": search_type,
                "sobjects": self.sobjects,
                "range_start_date": kwargs.get("range_start_date"),
                "range_end_date": kwargs.get("range_end_date"),
                "width": gantt_width,
                "height": height,
                "group_rows": group_rows,
                "parser": parser,
                "edit": edit,
                "special_days": special_days,
                "handler": handler,
                "start_column": kwargs.get("start_column"),
                "end_column": kwargs.get("end_column"),
                "auto_grouping": kwargs.get("auto_grouping"),
                "window_resize_offset": kwargs.get("window_resize_offset"),
                "min_width": resizable_min_width,
                "use_mouse_wheel": kwargs.get("use_mouse_wheel"),
                "parent_key": kwargs.get("parent_key"),
                "extra_data": kwargs.get("extra_data"),
                "show_month_highlight": kwargs.get("show_month_highlight"),
                "mode": self.kwargs.get("mode") or None,
                "processes": self.kwargs.get("processes") or None
        }


        gantt_class = self.kwargs.get("gantt_class") or "gantt"
        if not gantt_class or gantt_class == "gantt":
            gantt = GanttWdg(**gantt_kwargs)

        else:
            from pyasm.common import Common
            gantt = Common.create_from_class_path(gantt_class, [], gantt_kwargs)

        right.add(gantt)
        gantt.add_style("overflow: hidden")
        gantt.add_class("spt_resizable")


        right.add_style("position: relative")


        widget_div = DivWdg()
        right.add(widget_div)
        widget_div.add_class("spt_gantt_widgets_top")

        month_highlight = DivWdg()
        month_highlight.add_class("spt_gantt_trans_layer")
        month_highlight.add_class("month_highlight")
        month_highlight.add_style("position: absolute")
        month_highlight.add_style("height: 100%")
        month_highlight.add_style("top: 0px")
        month_highlight.add_style("opacity: 0.3")
        month_highlight.add_style("background: #19bbFF")
        month_highlight.add_style("pointer-events: none")

        week_highlight = DivWdg()
        week_highlight.add_class("spt_gantt_trans_layer")
        week_highlight.add_class("week_highlight")
        week_highlight.add_style("position: absolute")
        week_highlight.add_style("height: 100%")
        week_highlight.add_style("top: 0px")
        week_highlight.add_style("opacity: 0.3")
        week_highlight.add_style("background: #19bbFF")
        week_highlight.add_style("pointer-events: none")

        right.add(month_highlight)
        right.add(week_highlight)


        if self.resizable_mode == "table":
            gantt.add_behavior( {
                'type': 'load',
                'cbjs_action': '''
                var parent = bvr.src_el.getParent("td");
                var size = parent.getSize();
                bvr.src_el.setStyle("width", size.x);
                '''
            } )

            header_div.add_behavior( {
                'type': 'load',
                'cbjs_action': '''
                var parent = bvr.src_el.getParent("td");
                var size = parent.getSize();
                var children = parent.getElements(".spt_resizable");
                for (var i = 0; i < children.length; i++) {
                    children[i].setStyle("width", size.x);
                }
                '''
            } )







        # FIXME: this unselects after a drag as well
        gantt.add_behavior( {
            'type': 'click',
            'cbjs_action': '''
            var layout = bvr.src_el.getParent(".spt_layout");
            spt.table.set_layout(layout);

            spt.table.unselect_all_rows();
            '''
        } )


        # FIXME: this unselects after a drag as well
        gantt.add_relay_behavior( {
            'type': 'click',
            'bvr_match_class': 'spt_rangeX',
            'cbjs_action': '''
            var layout = bvr.src_el.getParent(".spt_layout");
            spt.table.set_layout(layout);

            var search_key = bvr.src_el.getAttribute("spt_search_key");

            var row = spt.table.get_row_by_search_key(search_key);

            spt.table.unselect_all_rows();
            spt.table.select_row(row);

            '''
        } )


        # FIXME: this unselects after a drag as well
        """
        gantt.add_relay_behavior( {
            'type': 'click',
            'bvr_match_class': 'spt_range',
            'cbjs_action': '''

            var top = bvr.src_el.getParent(".spt_range_top");
            var ranges = bvr.src_el.getElements(".spt_range");
            for (var i = 0; i < ranges.length; i++) {
                ranges[i].setStyle("z-index", "0");
            }

            bvr.src_el.setStyle("z-index", "100");


            '''
        } )
        """


        return top




    def get_date_range(self, tasks, padding=8):
        start_column = self.kwargs.get("start_column") or "bid_start_date"
        end_column = self.kwargs.get("end_column") or "bid_end_date"

        if tasks:
            min_date = min([task.get_value(start_column) for task in tasks])
            max_date = max([task.get_value(end_column) for task in tasks])
        else:
            min_date = None
            max_date = None

        if min_date and isinstance(min_date, basestring):
            min_date = parser.parse(min_date)
        if max_date and isinstance(max_date, basestring):
            max_date = parser.parse(max_date)

        if min_date:
            pass
        else:
            min_date = datetime.today() - timedelta(days=30)

        if max_date:
            max_date = max_date + timedelta(days=1)
        else:
            max_date = datetime.today() + timedelta(days=30)

        min_date = min_date - timedelta( days=padding)
        max_date = max_date + timedelta( days=padding)

        min_date = min_date.strftime("%Y-%m-%d")
        max_date = max_date.strftime("%Y-%m-%d")

        return min_date, max_date






#class GanttTableElementWdg(BaseTableElementWdg):
class GanttTableElementWdg(GanttElementWdg):

    def init(self):
        self.width = self.get_width()
        self.kwargs['test'] = self.width

        min_date = None
        max_date = None
        for sobject in self.sobjects:
            bid_start_date = self.kwargs.get("bid_start_date")
            if min_date == None or bin_start_date < min_date:
                min_date = bid_start_date

            bid_end_date = self.kwargs.get("bid_end_date")
            if max_date == None or bid_end_date > max_date:
                max_date = bid_end_date

        if not min_date:
            min_date = datetime.today() - timedelta(days=30)
        else:
            min_date = parser.parse(min_date) - timedelta(days=7)
        min_date = min_date.strftime("%D")

        if not max_date:
            max_date = datetime.today() + timedelta(days=30)
        else:
            max_date = parser.parse(max_date) - timedelta(days=7)
        max_date = max_date.strftime("%D")


        self.kwargs['range_start_date'] = min_date
        self.kwargs['range_end_date'] = max_date

        super(GanttTableElementWdg, self).init()

    def get_width(self):
        return 800


    def get_default_action(cls):
        #return "tactic.ui.table.GanttCbk"
        return "tactic.ui.gantt.GanttCbk"
    get_default_action = classmethod(get_default_action)


    #def handle_th(self, th, cell_index=None):
    #    # this is for general classification, we need spt_input_type = gantt still
    #    th.add_attr('spt_input_type', 'inline')



    def handle_td(self, td):
        index = self.get_current_index()
        if index == 0:
            num = len(self.sobjects)
            td.add_attr("rowspan", num)
            #td.add_attr("rowspan", 4)
            td.add_style("padding: 0px")
            td.add_color("background", "background")

        td.add_attr('spt_input_type', 'inline')
        td.add_class("spt_input_inline")

        td.add_style("padding: 0px")


    def get_title(self):
        div = DivWdg()

        header = GanttHeaderWdg(
                range_start_date=self.kwargs.get("range_start_date"),
                range_end_date=self.kwargs.get("range_end_date"),
        )
        div.add(header)

        return div



    def get_display(self):
        if not self.is_preprocessed:
            self.preprocess()


        top = DivWdg()

        if self.get_current_sobject().is_insert():
            top.add("No insert yet")
            return top




        hidden = HiddenWdg("my_data")
        top.add(hidden)
        #hidden.set_value( jsondumps( {'a': 1, 'b': 2} ).replace('"',"&quot;") )


        index = self.get_current_index()
        if index > 0:
            top.add("test")
            return top


        top.add_style("margin-top: -1px")

        gantt = GanttWdg(
                sobjects=self.sobjects,
                range_start_date=self.kwargs.get("range_start_date"),
                range_end_date=self.kwargs.get("range_end_date"),
                width=self.get_width(),
        )
        top.add(gantt)

        return top



class GanttCbk(DatabaseAction):

    def execute(self):
        web = WebContainer.get_web()
        if not self.sobject:
            return

        input_name = self.get_input_name()

        if self.data:
            data = jsonloads(self.data)
            for name, value in data.items():
                self.sobject.set_value(name, value)

        options = self.get_options()


class GanttTestWdg(BaseRefreshWdg):

    def get_display(self):

        top = self.top

        layout = TableLayoutWdg(
                search_type="sthpw/task",
                element_names="process,assigned,status,bid_start_date,bid_duration,bid_end_date,gantt_test",
                show_shelf=False,
        )
        top.add(layout)
        layout.add_style("width", "100%")
        layout.add_style("height", "800px")

        return top



class GanttTest2Wdg(BaseRefreshWdg):

    def get_display(self):

        top = self.top

        layout = TableLayoutWdg(
                search_type="sthpw/task",
                element_names="process,assigned,status,bid_start_date,bid_duration,bid_end_date,gantt_test",
                show_shelf=False,
        )
        top.add(layout)
        layout.add_style("width", "100%")
        layout.add_style("height", "800px")

        layout.add_behavior( {
            'type': 'load',
            'cbjs_action': '''
            spt.table.set_layout( bvr.src_el );
            for (var i = 0; i < 20; i++) {
                spt.table.add_new_item();
            }
            '''
        } )

        return top





class GanttHeaderWdg(BaseRefreshWdg):


    def init(self):
        self.min_date = self.kwargs.get("range_start_date")
        self.max_date = self.kwargs.get("range_end_date")

        self.width = self.kwargs.get("width")
        if not self.width:
            #self.width = 100  # some arbitrary small number
            self.width = "100%"
            self.kwargs["width"] = self.width


        self.start_date = parser.parse(self.min_date)
        self.end_date = parser.parse(self.max_date)

        diff = self.end_date - self.start_date

        self.total_days = diff.days + float(diff.seconds)/(24*3600)

        #dates = list(rrule.rrule(rrule.DAILY, dtstart=self.start_date, until=self.end_date))
        #self.total_days = (self.end_date - self.start_date).days + 1


        self.percent_width = 100
        if self.total_days:
            self.percent_per_day = float(self.percent_width) / float(self.total_days)
        else:
            self.percent_per_day = 0








    # NOTE: copied from GanttWdg
    def get_percent(self, start_date, end_date):
        # calculates the percentage position of a date based on the
        # min/max range
        if isinstance(start_date, basestring):
            start_date = parser.parse(start_date)
        if isinstance(end_date, basestring):
            end_date = parser.parse(end_date)

        diff = end_date - start_date

        days = float(diff.days) + float(diff.seconds)/(24*3600)
        return self.percent_per_day * days


    def get_button_shelf(self):
        div = DivWdg()

        # stop the button shelf from disappearing
        div.add_behavior( {
            'type': 'mouseenter',
            'cbjs_action': '''
            var timeout_id = bvr.src_el.timeout_id;
            if (timeout_id) {
                clearInterval(timeout_id);
            }
            '''
        } )

        if self.kwargs.get("is_refresh") not in [True, 'true']:
            div.add_style("display: none")

        div.add_class("spt_shelf")

        height = "30px"
        div.add_style("height: %s" % height)

        diff = self.total_days * 0.1
        diff = timedelta(days=diff)

        sdiff = timedelta(days=self.total_days*0.10)
        if sdiff < timedelta(days=1):
            sdiff = timedelta(hours=4)

        nav_action = '''
        var layout = bvr.src_el.getParent(".spt_layout");
        spt.gantt.set_top( layout.getElement(".spt_gantt_top"));

        var range_start_date = bvr.src_el.getAttribute("spt_range_start_date");
        var range_end_date = bvr.src_el.getAttribute("spt_range_end_date");
        spt.gantt.redraw_header({range_start_date, range_end_date});
        spt.gantt.redraw(range_start_date, range_end_date);
        '''

        button = IconButtonWdg(name="Go Left", icon="FAS_CHEVRON_LEFT")
        div.add(button)
        button.add_style("display: inline-block")
        button.add_class("spt_gantt_left")
        button.add_attr("spt_range_start_date", SPTDate.strip_time(self.start_date + diff))
        button.add_attr("spt_range_end_date", SPTDate.strip_time(self.end_date + diff) + timedelta(days=1))
        
        button.add_behavior( {
            'type': 'click',
            'cbjs_action': nav_action
        } )




        button = IconButtonWdg(name="Zoom In", icon="FAS_SEARCH_PLUS")
        div.add(button)
        button.add_style("display: inline-block")
        button.add_class("spt_gantt_zoom_in")
        button.add_attr("spt_range_start_date", SPTDate.strip_time(self.start_date + diff))
        button.add_attr("spt_range_end_date", SPTDate.strip_time(self.end_date - sdiff) + timedelta(days=1))

        button.add_behavior( {
            'type': 'click',
            'cbjs_action': nav_action
        } )






        button = IconButtonWdg(name="Zoom Out", icon="FAS_SEARCH_MINUS")
        div.add(button)
        button.add_style("display: inline-block")
        button.add_class("spt_gantt_zoom_out")
        button.add_attr("spt_range_start_date", SPTDate.strip_time(self.start_date - sdiff))
        button.add_attr("spt_range_end_date", SPTDate.strip_time(self.end_date + sdiff) + timedelta(days=1))

        button.add_behavior( {
            'type': 'click',
            'cbjs_action': nav_action
        } )





        button = IconButtonWdg(name="Go Right", icon="FAS_CHEVRON_RIGHT")
        div.add(button)
        button.add_style("display: inline-block")
        button.add_class("spt_gantt_right")
        button.add_attr("spt_range_start_date", SPTDate.strip_time(self.start_date - diff))
        button.add_attr("spt_range_end_date", SPTDate.strip_time(self.end_date - diff) + timedelta(days=1))
        
        button.add_behavior( {
            'type': 'click',
            'cbjs_action': nav_action
        } )


        spacer = DivWdg()
        div.add(spacer)
        spacer.add_style("display: inline-block")
        spacer.add_style("margin: 0px 10px")
        spacer.add_style("vertical-align: middle")
        spacer.add_style("border-right: solid 1px #CCC")
        spacer.add("&nbsp;")


        button = IconButtonWdg(name="Undo", icon="FAS_UNDO")
        div.add(button)
        button.add_style("display: inline-block")
        kwargs = self.kwargs.copy()
        button.add_behavior( {
            'type': 'click',
            'cbjs_action': '''
            var layout = bvr.src_el.getParent(".spt_layout");
            spt.gantt.set_top( layout.getElement(".spt_gantt_top"));
            spt.gantt.undo();
            '''
        } )


        button = IconButtonWdg(name="Redo", icon="FAS_REPEAT")
        div.add(button)
        button.add_style("display: inline-block")
        kwargs = self.kwargs.copy()
        button.add_behavior( {
            'type': 'click',
            'cbjs_action': '''
            var layout = bvr.src_el.getParent(".spt_layout");
            spt.gantt.set_top( layout.getElement(".spt_gantt_top"));
            spt.gantt.redo();
            '''
        } )


        return div



    def get_display(self):

        top = self.top
        top.add_style("position: relative")
        top.add_class("spt_gantt_header_top")
        top.add_style("width: %s" % self.width)
        top.add_style("margin: 0px 0px 0px 0px")
        #top.add_style("overflow-x: hidden")
        self.set_as_panel(top)
        top.add_class("spt_resizable")

        min_width = self.kwargs.get("min_width")
        if min_width:
            top.add_style("min-width: %s" % min_width)

        inner = DivWdg()
        top.add(inner)
        inner.add_style("font-size: 0.8em")


        inner.add_attr("spt_start_date", self.min_date)
        inner.add_attr("spt_end_date", self.max_date)


        import json
        state_data = {
                'min_date': self.min_date,
                'max_date': self.max_date
        }
        state_data_str = json.dumps(state_data).replace('"', '&quot;')

        inner.add_class("spt_state_save")
        inner.add_attr("spt_state_name", "gantt")
        inner.add_attr("spt_state_data", state_data_str)


        # add a button shelf
        show_header_shelf = self.kwargs.get("show_header_shelf")
        if show_header_shelf not in ['false', False]:
            button_shelf = self.get_button_shelf()
            inner.add(button_shelf)
            button_shelf.add_style("position: absolute")
            button_shelf.add_style("top: 0px")
            button_shelf.add_style("left: 0px")
            button_shelf.add_color("background", "background")
            button_shelf.add_border()

            inner.add_behavior( {
                'type': 'mouseenter',
                'cbjs_action': '''
                var el = bvr.src_el.getElement(".spt_shelf");
                el.setStyle("display", "");

                var timeout_id = setTimeout( function() {
                    el.setStyle("display", "none");
                }, 2000 )
                el.timeout_id = timeout_id;

                '''
            } )
            inner.add_behavior( {
                'type': 'mouseleave',
                'cbjs_action': '''
                var el = bvr.src_el.getElement(".spt_shelf");
                el.setStyle("display", "none");
                '''
            } )




        start_date = parser.parse(self.min_date )
        end_date = parser.parse(self.max_date )


        show_time = self.kwargs.get("show_time")
        if show_time in ['false', False]:
            show_time = False
        else:
            show_time = True

        inner.add_relay_behavior( {
            'type': 'click',
            'bvr_match_class': 'spt_gantt_header_range',
            'cbjs_action': '''

            var layout = bvr.src_el.getParent(".spt_gantt_layout_top");
            spt.gantt.set_top( layout.getElement(".spt_gantt_top"));

            var start_date = bvr.src_el.getAttribute("spt_start_date");
            var end_date = bvr.src_el.getAttribute("spt_end_date");

            var diff = moment.duration(moment(end_date).diff(moment(start_date)));
            var range = diff / (2*1000);

            var start_date = moment(start_date).subtract(range, 'second').format("YYYY-MM-DD");
            var end_date = moment(end_date).add(range, 'second').format("YYYY-MM-DD");

            spt.gantt.redraw_layout(start_date, end_date, {show_time: "%s"});
            ''' % (show_time)
        } )


        inner.add_relay_behavior( {
            'type': 'mouseenter',
            'bvr_match_class': 'spt_gantt_header_range',
            'cbjs_action': '''
            var background = bvr.src_el.getStyle("background");
            bvr.src_el.background = background;
            bvr.src_el.setStyle("background", "#CCC");
            '''
        } )

        inner.add_relay_behavior( {
            'type': 'mouseleave',
            'bvr_match_class': 'spt_gantt_header_range',
            'cbjs_action': '''
            var background = bvr.src_el.background;
            bvr.src_el.setStyle("background", background);
            '''
        } )




        height = "50%"



        inner.set_id(self.generate_unique_id())
        inner.add_smart_style("spt_gantt_header_center", "display", "flex")
        inner.add_smart_style("spt_gantt_header_center", "width", "100%")
        inner.add_smart_style("spt_gantt_header_center", "height", "100%")
        inner.add_smart_style("spt_gantt_header_center", "justify-content", "center")
        inner.add_smart_style("spt_gantt_header_center", "align-items", "center")





        # yearly
        dates = list(rrule.rrule(rrule.MONTHLY, byyearday=1, dtstart=start_date, until=end_date))
        if not dates or dates[0] != start_date:
            dates.insert(0, start_date)
        if not dates or dates[-1] != end_date:
            dates.append(end_date)

        years_div = DivWdg()
        inner.add(years_div)
        years_div.add_class("spt_gantt_header_redraw")
        years_div.add_style("width: 100%")
        years_div.add_style("overflow-x: hidden")
        years_div.add_style("white-space: nowrap")


        dates.pop()
        for i, date in enumerate(dates):

            year_div = DivWdg()
            years_div.add(year_div)
            year_div.add_class("spt_gantt_header_range")


            sdate = date + relativedelta(day=1)
            edate = date + relativedelta(day=1, years=1)

            year_div.add_attr("spt_start_date", sdate.strftime("%Y-%m-%d"))
            year_div.add_attr("spt_end_date", edate.strftime("%Y-%m-%d"))

            if len(dates) == 1:
                year_div.add_style("width: 100%")
            else:
                if i == 0:
                    diff = dates[i+1] - start_date

                elif i == len(dates) - 1:
                    diff = end_date - date
                else:
                    diff = dates[i+1] - date

                days = diff.days + float(diff.seconds)/(24*3600)

                year_div.add_style("width: %s%%" % (self.percent_per_day*days))


            year_div.add_style("text-align: center")
            year_div.add_style("display: inline-block")
            year_div.add_style("box-sizing: border-box")
            year_div.add_style("overflow: hidden")
            year_div.add_class("hand")
            year_div.add_border(size="0px 1px 1px 0px", color="table_border")
            year_div.add_style("height: 100%")

            if i == 0 or i % 2 == 0:
                year_div.add_style("background", "#FFF")
            else:
                year_div.add_style("background", "#FFF")

            t = DivWdg()
            year_div.add(t)
            year = date.strftime("%Y")

            t.add_class("spt_gantt_header_center")
            t.add(year)




        # monthly
        dates = list(rrule.rrule(rrule.MONTHLY, bymonthday=1, dtstart=start_date, until=end_date))


        if not dates or dates[0] != start_date:
            dates.insert(0, start_date)
        if not dates or dates[-1] != end_date:
            dates.append(end_date)


        months_div = DivWdg()
        inner.add(months_div)
        months_div.add_class("spt_gantt_header_redraw")
        months_div.add_style("width: 100%")
        months_div.add_style("overflow-x: hidden")
        months_div.add_style("white-space: nowrap")


        dates.pop()
        for i, date in enumerate(dates):

            month_div = DivWdg()
            months_div.add(month_div)
            month_div.add_class("spt_gantt_header_range")


            sdate = date + relativedelta(day=1)
            edate = date + relativedelta(day=1, months=1)

            month_div.add_attr("spt_start_date", sdate.strftime("%Y-%m-%d"))
            month_div.add_attr("spt_end_date", edate.strftime("%Y-%m-%d"))

            if len(dates) == 1:
                month_div.add_style("width: 100%")
            else:
                if i == 0:
                    diff = dates[i+1] - start_date

                elif i == len(dates) - 1:
                    diff = end_date - date
                else:
                    diff = dates[i+1] - date

                days = diff.days + float(diff.seconds)/(24*3600)

                month_div.add_style("width: %s%%" % (self.percent_per_day*days))


            month_div.add_style("text-align: center")
            month_div.add_style("display: inline-block")
            month_div.add_style("box-sizing: border-box")
            month_div.add_style("overflow: hidden")
            month_div.add_class("hand")
            month_div.add_class("spt_gantt_header_month")
            month_div.add_border(size="0px 1px 1px 0px", color="table_border")
            month_div.add_style("height: 100%")

            if i == 0 or i % 2 == 0:
                month_div.add_style("background", "#FFF")
            else:
                month_div.add_style("background", "#EEE")

            t = DivWdg()
            month_div.add(t)
            t.add_class("spt_gantt_header_center")
            month = date.strftime("%b").upper()

            if self.total_days > 1800:
                month = month[0]

            t.add(month)




        # weekly
        weeks_div = DivWdg()
        if self.total_days < 350 and self.total_days >= 50:

            height = "33.33%"

            #dates = list(rrule.rrule(rrule.WEEKLY, dtstart=start_date, until=end_date))
            dates = list(rrule.rrule(rrule.WEEKLY, dtstart=start_date-timedelta(days=6), until=end_date, byweekday=(MO)))

            inner.add(weeks_div)
            weeks_div.add_class("spt_gantt_header_redraw")
            weeks_div.add_style("width: 100%")
            weeks_div.add_style("overflow-x: hidden")
            weeks_div.add_style("white-space: nowrap")

            for i, date in enumerate(dates):
                week_div = DivWdg()
                weeks_div.add(week_div)
                week_div.add_class("spt_gantt_header_range")
                week_div.add_class("hand")


                sdate = date + relativedelta(weekday=1)
                edate = date + relativedelta(weekday=1, weeks=1)

                week_div.add_attr("spt_start_date", sdate.strftime("%Y-%m-%d"))
                week_div.add_attr("spt_end_date", edate.strftime("%Y-%m-%d"))


                if len(dates) == 1:
                    week_div.add_style("width: 100%")
                else:

                    if i == 0:
                        diff = dates[i+1] - start_date
                    elif i == len(dates) - 1:
                        diff = end_date - date
                    else:
                        diff = dates[i+1] - date

                    days = diff.days + float(diff.seconds)/(24*3600)

                    width = self.percent_per_day*days

                    week_div.add_style("width: %s%%" % width)



                week_div.add_style("text-align: center")
                week_div.add_style("display: inline-block")
                week_div.add_style("box-sizing: border-box")
                week_div.add_style("overflow: hidden")
                week_div.add_border(size="0px 1px 1px 0px")
                week_div.add_style("height: 100%")

                if i == 0 or i % 2 == 0:
                    week_div.add_style("background", "#FFF")


                wday = date.strftime("%d")
                date2 = date + timedelta(days=6)
                wday2 = date2.strftime("%d")

                t = DivWdg()
                week_div.add(t)

                t.add_class("spt_gantt_header_center")


                t.add("%s-%s" % (wday, wday2))



        days_div = DivWdg()
        if self.total_days < 50:

            height = "25%"

            #dates = list(rrule.rrule(rrule.DAILY, dtstart=start_date, until=end_date, byweekday=(MO,TU,WE,TH,FR)))
            dates = list(rrule.rrule(rrule.DAILY, dtstart=start_date, until=end_date))

            inner.add(days_div)
            days_div.add_class("spt_gantt_header_redraw")
            days_div.add_style("width: 100%")

            for i, date in enumerate(dates):
                day_div = DivWdg()
                days_div.add(day_div)

                if len(dates) == 1:
                    day_div.add_style("width: 100%")
                else:
                    if i == 0:
                        diff = dates[i+1] - start_date
                    elif i == len(dates) - 1:
                        diff = end_date - date
                    else:
                        diff = dates[i+1] - date

                    days = diff.days + float(diff.seconds)/(24*3600)
                    if days == 0:
                        continue

                    day_div.add_style("width: %s%%" % (self.percent_per_day*days))


                day_div.add_style("text-align: center")
                day_div.add_style("display: inline-block")
                day_div.add_style("box-sizing: border-box")
                day_div.add_style("overflow: hidden")
                day_div.add_border(size="0px 1px 1px 0px")

                if i == 0 or i % 2 == 0:
                    day_div.add_style("background", "#FFF")


                mday = date.strftime("%d")
                wday = date.strftime("%a")[:2]
                day_div.add(mday)
                day_div.add("<br/>")
                day_div.add(wday)

        hours_div = DivWdg()
        if show_time and self.total_days < 21:

            dates = list(rrule.rrule(rrule.HOURLY, dtstart=start_date, until=end_date))

            if self.total_days > 10:
                dates = dates[::8]
            elif self.total_days > 2:
                dates = dates[::4]


            inner.add(hours_div)
            hours_div.add_class("spt_gantt_header_redraw")
            hours_div.add_style("width: 100%")
            hours_div.add_style("font-size: 0.8em")

            for i, date in enumerate(dates):

                hour = date.strftime("%H")

                hour_div = DivWdg()
                hours_div.add(hour_div)


                if len(dates) == 1:
                    hour_div.add_style("width: 100%")
                else:

                    if i == 0:
                        diff = dates[i+1] - start_date
                    elif i == len(dates) - 1:
                        diff = end_date - date
                    else:
                        diff = dates[i+1] - date

                    days = diff.days + float(diff.seconds)/(24*3600)

                    width = self.percent_per_day*days
                    if width == 0:
                        continue

                    hour_div.add_style("width: %s%%" % width)


                hour_div.add_style("text-align: center")
                hour_div.add_style("display: inline-block")
                hour_div.add_style("box-sizing: border-box")
                hour_div.add_style("overflow: hidden")
                hour_div.add_border(size="0px 1px 1px 0px")


                if i == 0 or i % 2 == 0:
                    hour_div.add_style("background", "#FFF")
                else:
                    hour_div.add_style("background", "#FFF")


                hour_div.add(hour)



        years_div.add_style("height: %s" % height)
        months_div.add_style("height: %s" % height)
        weeks_div.add_style("height: %s" % height)
        days_div.add_style("height: %s" % height)
        hours_div.add_style("height: %s" % height)




        if self.kwargs.get("is_refresh") in [True, 'true']:
            return inner
        else:
            return top




class GanttWdg(BaseRefreshWdg):

    def init(self):

        search_keys = self.kwargs.get("search_keys")
        if search_keys:
            self.sobjects = Search.get_by_search_keys(search_keys)
        else:
            self.sobjects = self.kwargs.get("sobjects")

        self.index = None

        self.min_date = self.kwargs.get("range_start_date")
        self.max_date = self.kwargs.get("range_end_date")
        self.width = self.kwargs.get("width")
        if not self.width:
            self.width = 800

        self.min_width = self.kwargs.get("min_width")


        start_date = parser.parse(self.min_date)
        end_date = parser.parse(self.max_date)


        dates = list(rrule.rrule(rrule.DAILY, dtstart=start_date, until=end_date))
        self.total_days = (end_date - start_date).days + 1
        self.total_days = (end_date - start_date).days
        self.percent_width = 100
        if self.total_days:
            self.percent_per_day = float(self.percent_width) / float(self.total_days)
        else:
            self.percent_per_day = 0


        self.nobs_mode = self.kwargs.get("nobs_mode") or "hover"

        self.range_index = 0

        self.search_type = self.kwargs.get("search_type")
        if not self.search_type:
            self.search_type = "sthpw/task"

    
    
    def get_color_maps(self, element_name):

        # get the color maps
        from pyasm.widget import WidgetConfigView
        color_config = WidgetConfigView.get_by_search_type(self.search_type, "color")
        color_xml = color_config.configs[0].xml
        self.color_maps = {}
        
        xpath = "config/color/element[@name='%s']/colors" % element_name
        text_xpath = "config/color/element[@name='%s']/text_colors" % element_name
        bg_color_node = color_xml.get_node(xpath)
        bg_color_map = color_xml.get_node_values_of_children(bg_color_node)

        text_color_node = color_xml.get_node(text_xpath)
        text_color_map = color_xml.get_node_values_of_children(text_color_node)

        # use old weird query language
        query = bg_color_map.get("query")
        query2 = bg_color_map.get("query2")
        if query:
            bg_color_map = {}

            search_type, match_col, color_col = query.split("|")
            search = Search(search_type)
            sobjects = search.get_sobjects()

            # match to a second atble
            if query2:
                search_type2, match_col2, color_col2 = query2.split("|")
                search2 = Search(search_type2)
                sobjects2 = search2.get_sobjects()
            else:
                sobjects2 = []

            for sobject in sobjects:
                match = sobject.get_value(match_col)
                color_id = sobject.get_value(color_col)

                for sobject2 in sobjects2:
                    if sobject2.get_value(match_col2) == color_id:
                        color = sobject2.get_value(color_col2)
                        break
                else:
                    color = color_id


                bg_color_map[match] = color
        
        return bg_color_map, text_color_map




    def get_percent(self, start_date, end_date):
        # calculates the percentage position of a date based on the
        # min/max range
        if isinstance(start_date, basestring):
            start_date = parser.parse(start_date)
        if isinstance(end_date, basestring):
            end_date = parser.parse(end_date)

        if not start_date:
            start_date = datetime.today()
        if not end_date:
            end_date = datetime.today()

        diff = end_date - start_date

        days = float(diff.days) + float(diff.seconds)/(24*3600)
        return self.percent_per_day * days


    def get_template_wdg(self, start_date, end_date):
        div = DivWdg()

        # add a dummy tempalte
        template = DivWdg()
        div.add(template)

        template.add_class("spt_gantt_row_item")
        template.add_attr("spt_gantt_type", "TEST")

        template.add_style("border: solid 1px blue")
        template.add("this is the first template")



        # add a task row template
        sobject = SearchType.create(self.search_type)
        tasks = [SearchType.create("sthpw/task")]
        group_level = 0

        task_start_date = datetime.today().strftime("%Y-%m-%d")
        task_end_date = (datetime.today() + timedelta(days=5)).strftime("%Y-%m-%d")
        for task in tasks:
            task.set_value("bid_start_date", task_start_date)
            task.set_value("bid_end_date", task_end_date)


        row_wdg = self.get_task_wdg(sobject, tasks, start_date, end_date, group_level=group_level, is_template=True)
        div.add(row_wdg)

        return div




    def get_display(self):

        top = self.top
        top.add_style("position: relative")
        self.set_as_panel(top)

        top.add_class("spt_gantt_top")
        self.unique_id = self.generate_unique_id("gantt")
        top.set_id(self.unique_id)

        top.add_style("width: %s" % self.width)

        height = self.kwargs.get("height")
        if not height:
            height = "500px"

        window_resize_offset = self.kwargs.get("window_resize_offset")
        if window_resize_offset:
            top.add_class("spt_window_resize")
            top.add_attr("spt_window_resize_offset", window_resize_offset)


        top.add_style("height: %s" % height)

        top.add_style("overflow-y: hidden")
        """
        scroll.add_behavior( {
            'type': 'load',
            'cbjs_action': '''
            new Scrollable(bvr.src_el, null);
            '''
        } )
        """



        #top.add_class("spt_timeline_top");


        # organize tasks by parent_key
        expr_parser = self.kwargs.get("parser")
        if not expr_parser:
            tasks = self.sobjects
            cache = {}
        else:
            tasks = expr_parser.get_result()
            cache = expr_parser.get_flat_cache()




        hot_key_div = DivWdg()
        top.add(hot_key_div)
        hot_key_div.add("<input type='text' class='spt_gantt_hot_key_input'/>")
        hot_key_div.add_style("position: absolute")
        hot_key_div.add_style("left: -5000px")

        top.add_behavior( {
            'type': 'mouseenter',
            'cbjs_action': '''
            var input = bvr.src_el.getElement(".spt_gantt_hot_key_input");
            input.focus( { preventScroll: true } );
            '''
        } )

        top.add_behavior( {
            'type': 'click',
            'cbjs_action': '''
            var input = bvr.src_el.getElement(".spt_gantt_hot_key_input");
            input.focus( { preventScroll: true } );
            '''
        } )


        top.add_behavior( {
            'type': 'mouseleave',
            'cbjs_action': '''
            var input = bvr.src_el.getElement(".spt_gantt_hot_key_input");
            input.blur();
            '''
        } )


        use_mouse_wheel = self.kwargs.get("use_mouse_wheel")
        if use_mouse_wheel in ['true', True]:
            use_mouse_wheel = True
        else:
            use_mouse_wheel = False

        if use_mouse_wheel or not height or height != "auto":
            top.add_behavior( {
                'type': 'wheel',
                'cbjs_action': '''
                var layout = bvr.src_el.getParent(".spt_layout");
                var table = layout.getElement(".spt_table_table");
                var scroll = table.getElement(".spt_table_scroll")

                scroll.scrollTop = scroll.scrollTop - evt.wheel*15;
                '''
            } )



        top.add_behavior( {
            'type': 'keyup',
            'cbjs_action': '''

            spt.gantt.set_top(bvr.src_el);

            var data = spt.gantt.get_layout_date_range();

            var start_date = data.start_date;
            var end_date = data.end_date;

            var diff = moment.duration(moment(end_date).diff(moment(start_date)));
            var duration = diff.asSeconds();

            var key = evt.key;

            if (evt.shift == true) {
                shift_interval = 50;
                scale_interval = 1.5;
            }
            else {
                shift_interval = 10;
                scale_interval = 1.1;
            }

            if (key == "up") {
                spt.gantt.resize_layout( duration * scale_interval / 2 );
            }
            else if (key == "down") {
                spt.gantt.resize_layout( duration / scale_interval / 2 );
            }

            else if (key == "left") {
                spt.gantt.shift_layout_by_percent(-shift_interval);
            }

            else if (key == "right") {
                spt.gantt.shift_layout_by_percent(shift_interval);
            }


            else if (key == "f") {
                var search_keys = spt.table.get_selected_search_keys();
                spt.gantt.fit_layout( { visible_only: true, search_keys, search_keys } );

            }
            else if (evt.control == true &&  key == "z") {
                spt.gantt.undo();
            }
            else if (evt.control == true &&  key == "y") {
                spt.gantt.undo();
            }

            else if (key == "esc") {
                spt.table.unselect_all_rows();
            }
 




            '''
        } )



        gantt_div = DivWdg()
        top.add(gantt_div)
        #gantt_div.add_style("height: 100%")
        gantt_div.add_class("spt_gantt_scroll")
        gantt_div.add_style("position: relative")


        """
        gantt_div.add_behavior( {
            'type': 'clickX',
            'cbjs_action': '''
            spt.body.hide_focus_elements(evt);
            spt.table.unselect_all_rows();
            '''
        } )
        """


        gantt_div.add_behavior( {
        "type": 'drag',
        "mouse_btn": 'LMB',
        "drag_el": '@',
        "cb_set_prefix": 'spt.gantt.canvas_drag'
        } )


        canvas = Canvas()
        canvas.add_class("spt_gantt_canvas")
        canvas.add_class("spt_resizable")
        gantt_div.add(canvas)
        canvas.add_style("position", "absolute")
        canvas.add_style("top: 0px")
        canvas.add_style("left: 0px")
        canvas.add_style("width: 100%")
        canvas.add_style("z-index", "0")



        canvas.add_behavior( {
        "type": 'smart_drag',
            "bvr_match_class": 'spt_gantt_row_item',
            "cb_set_prefix": 'spt.gantt.canvas_drag'
        } )



        connector_canvas = Canvas()
        connector_canvas.add_class("spt_gantt_connector_canvas")
        connector_canvas.add_class("spt_resizable")
        gantt_div.add(connector_canvas)
        connector_canvas.add_style("position", "absolute")
        connector_canvas.add_style("top: 0")
        connector_canvas.add_style("left: 0")
        connector_canvas.add_style("width: 100%")
        connector_canvas.add_style("z-index", "0")
        connector_canvas.add_style("background", "transparent")



        connector_canvas.add_behavior( {
        "type": 'smart_drag',
            "bvr_match_class": 'spt_gantt_row_item',
            "cb_set_prefix": 'spt.gantt.canvas_drag'
        } )




        if self.min_width:
            top.add_style("min-width: %s" % self.min_width)
            gantt_div.add_style("min-width: %s" % self.min_width)
            canvas.add_style("min-width: %s" % self.min_width)
            connector_canvas.add_style("min-width: %s" % self.min_width)


        # Make it really big as it is hidden
        gantt_div.add_style("height: 10000%")


        """
        today = datetime.today()
        today_offset = self.get_percent(self.min_date, today)
        today_width = self.get_percent(today, today + timedelta(days=1))

        canvas.add_behavior( {
        "type": "load",
        "offset": today_offset,
        "width": today_width,
        "cbjs_action": '''
            var top = bvr.src_el.getParent(".spt_gantt_top");

            var div = document.createElement("div");
            top.appendChild(div);
            div = document.id(div);
            div.setStyle("position", "absolute");
            div.setStyle("width", bvr.today_width + "%");
            div.setStyle("height", "100%");
            div.setStyle("left", bvr.today_offset + "%");
            div.setStyle("top", 30);
            div.setStyle("opacity", "0.2");
            div.setStyle("background", "#00F");
            div.setStyle("z-index", 100);

            bvr.src_el.pos_el = div;
        ''' } )
        """





        canvas.add_behavior( {
            'type': 'load',
            'cbjs_action': self.get_onload_js()
        })

        special_days = self.kwargs.get("special_days") or []


        show_month_highlight = self.kwargs.get("show_month_highlight")
        if show_month_highlight in [True, 'true']:
            show_month_highlight = True
        else:
            show_month_highlight = False


        canvas.add_behavior( {
            'type': 'load',
            'width': self.width,
            'percent_per_day': self.percent_per_day,
            'min_date': self.min_date,
            'max_date': self.max_date,
            'special_days': special_days,
            'show_month_highlight': show_month_highlight,
            'cbjs_action': '''
            var parent = bvr.src_el.getParent();
            var size = parent.getSize();
            size = {x: bvr.width, y: 1500};
            bvr.src_el.setAttribute("width", size.x);



            // FIXME: moment takes some time to initialize
            setTimeout( function() {


            var top = bvr.src_el.getParent(".spt_gantt_top");
            spt.gantt.set_top( top );

            var canvas_names = ['grid', 'connector'];
            canvas_names.forEach( function(canvas_name) {
                var canvas = spt.gantt.get_canvas(canvas_name);

                canvas.setAttribute("height", 5000);
                canvas.setStyle("height", 5000);

                // make sure the canvas width is in sync with the css width
                var width = canvas.getStyle("width");
                canvas.setAttribute("width", width);
            } )






            spt.gantt.percent_per_day = bvr.percent_per_day;
            spt.gantt.min_date = bvr.min_date;
            spt.gantt.max_date = bvr.max_date;
            spt.gantt.special_days = bvr.special_days;


            info = spt.gantt.get_info();
            info.percent_per_day = bvr.percent_per_day;
            info.min_date = bvr.min_date;
            info.max_date = bvr.max_date;
            info.special_days = bvr.special_days;
            info.curr_month_highlights = bvr.show_month_highlight;


            spt.gantt.set_top( top );

            spt.gantt.draw_grid();


            var ranges = spt.gantt.get_all_ranges();
            var rows = spt.table.get_all_rows();
            for (var i = 0; i < ranges.length; i++) {
                var parent = ranges[i].getParent();
                var row = rows[i];
                if (!row) {
                    continue;
                }
                var size = row.getSize();
                parent.setStyle("height", size.y);
            }


            spt.gantt.draw_connects();

            }, 100 );



        '''
        } )




        items_div = DivWdg()
        gantt_div.add(items_div)
        #items_div.add_style("z-index: 0")
        items_div.add_style("position", "absolute")
        items_div.add_style("top: 0px")
        items_div.add_style("left: 0px")
        #items_div.add_style("width", self.width)
        items_div.add_style("width", "100%")
        items_div.add_style("height", "100%")
        items_div.add_style("overflow-x", "hidden")
        items_div.add_style("overflow-y", "hidden")
        items_div.add_style("position", "relative")
        items_div.add_class("spt_gantt_items_top")




        edit = self.kwargs.get("edit")
        if edit in [False, 'false']:
            edit = False
        else:
            edit = True

        items_div.add_behavior( {
            'type': 'smart_drag',
            'bvr_match_class': 'spt_gantt_row_item',
            'ignore_default_motion' : True,
            "cbjs_setup": 'spt.gantt.canvas_drag_setup( evt, bvr, mouse_411 );',
            "cbjs_motion": 'spt.gantt.canvas_drag_motion( evt, bvr, mouse_411 );',
            "cbjs_action": 'spt.gantt.canvas_drag_action( evt, bvr, mouse_411 );'
        } )



        if edit:

            items_div.add_behavior( {
                'type': 'smart_drag',
                'bvr_match_class': 'spt_range',
                'ignore_default_motion' : True,
                "cbjs_setup": 'spt.gantt.drag_setup( evt, bvr, mouse_411 );',
                "cbjs_motion": 'spt.gantt.drag_motion( evt, bvr, mouse_411 );',
                "cbjs_action": 'spt.gantt.drag_action( evt, bvr, mouse_411 );'
            } )


            items_div.add_behavior( {
                'type': 'smart_drag',
                'bvr_match_class': 'spt_nob',
                'ignore_default_motion' : True,
                "cbjs_setup": 'spt.gantt.drag_setup( evt, bvr, mouse_411 );',
                "cbjs_motion": 'spt.gantt.drag_motion( evt, bvr, mouse_411 );',
                "cbjs_action": 'spt.gantt.drag_action( evt, bvr, mouse_411 );'
            } )



            items_div.add_behavior( {
                'type': 'smart_drag',
                'bvr_match_class': 'spt_group_range',
                'ignore_default_motion' : True,
                "cbjs_setup": 'spt.gantt.group_drag_setup( evt, bvr, mouse_411 );',
                "cbjs_motion": 'spt.gantt.group_drag_motion( evt, bvr, mouse_411 );',
                "cbjs_action": 'spt.gantt.group_drag_action( evt, bvr, mouse_411 );'
            } )


            items_div.add_relay_behavior( {
                'type': 'click',
                'bvr_match_class': 'spt_group_range',
                'cbjs_action': '''
                var top = bvr.src_el.getParent(".spt_group_range_top");
                var search_keys = top.getAttribute("spt_search_keys");
                search_keys = search_keys.split(",");

                spt.table.unselect_all_rows();
                for (var i = 0; i < search_keys.length; i++) {
                    var search_key = search_keys[i];
                    var row = spt.table.get_row_by_search_key(search_key);
                    spt.table.select_row(row);
                }

                '''
            } )




        num = len(self.sobjects)


        start_date = self.kwargs.get("range_start_date")
        end_date = self.kwargs.get("range_end_date")


        # create a place for for getting templates
        template_div = DivWdg()
        top.add(template_div)
        template_div.add_class("spt_gantt_template_top")
        template_div.add( self.get_template_wdg(start_date, end_date) )
        template_div.add_style("visibility: hidden")
        template_div.add_style("width: 0")
        template_div.add_style("height: 0")
        template_div.add_style("margin: 0")
        template_div.add_style("padding: 0")
        template_div.add_style("position: absolute")
        template_div.add_style("top: 0")
        template_div.add_style("left: 0")


        # 



        # create and add a detail_span to gantt_top for all tooltips
        detail_span = DivWdg()
        top.add(detail_span)
        detail_span.add_class("spt_range_detail")
        detail_span.add_style("visibility: hidden")
        detail_span.add_style("font-size: 1.2em")
        detail_span.add_style("width: 200px")
        detail_span.add_style("min-width: 200px")
        detail_span.add_style("margin-top: 3px")
        detail_span.add_border()
        detail_span.add_style("padding: 5 10px")
        detail_span.add_style("z-index: 100")
        detail_span.add_style("background: #FFF")
        detail_span.add_style("position: absolute")
        detail_span.add_style("opacity: 0.8")
        detail_span.add_style("top: 0")
        detail_span.add_style("left: 0")
        detail_span.add_attr("spt_search_key", "")
        detail_span.add_attr("spt_range_active", "false")
        detail_span.add_attr("spt_detail_active", "false")

        detail_span.add_style("pointer-events: none")

        """
        button = IconButtonWdg(name="Edit", icon="FAS_EDIT")
        detail_span.add(button)
        button.add_class("spt_range_edit")
        button.add_style("float: right")
        button.add_style("margin-top: 12px")
        button.add_style("margin-right: -5px")

        detail_span.add_relay_behavior( {
            'type': 'click',
            'bvr_match_class': 'spt_range_edit',
            'cbjs_action': '''
            var detail_span = bvr.src_el.getParent(".spt_range_detail");
            var search_key = detail_span.getAttribute("spt_search_key");

            var class_name = 'tactic.ui.panel.EditWdg';
            var kwargs = {
                search_type: "sthpw/task",
                search_key: search_key,
            }
            spt.panel.load_popup("Edit Task", class_name, kwargs);

            '''
        } )

        top.add_relay_behavior( {
                'type': 'mouseenter',
                'bvr_match_class': "spt_range_detail",
                'cbjs_action': '''

                // if the item is being dragged, we want to disable mouseenter event.
                drag = bvr.src_el.getAttribute("drag");
                if (drag == "true") {
                    return;
                }
                bvr.src_el.setAttribute("spt_detail_active", "true");


                '''
            } )

        top.add_relay_behavior( {
                'type': 'mouseleave',
                'bvr_match_class': "spt_range_detail",
                'cbjs_action': '''

                var top = bvr.src_el.getParent(".spt_gantt_top");
                var detail_span = top.getElement(".spt_range_detail");

                detail_span.setAttribute("spt_detail_active", "false");

                setTimeout(function() {
                    var detail_active = detail_span.getAttribute("spt_detail_active");
                    var range_active = detail_span.getAttribute("spt_range_active");
                    if (detail_active == "true" || range_active == "true") {
                        return;
                    }
                    detail_span.setStyle("visibility", "hidden");
                }, 1000);

                '''
            } )
        """


        detail_span.add_style("font-size: 0.8px")

        table = Table()
        detail_span.add(table)

        table.add_row()
        td = table.add_cell("Process: ")
        td.add_style("width: 75px")
        td.add_style("vertical-align: top")
        process_div = DivWdg()
        table.add_cell(process_div)
        process_div.add_class("spt_range_detail_process")

        table.add_row()
        td = table.add_cell("Description")
        td.add_style("vertical-align: top")
        description_div = DivWdg()
        table.add_cell(description_div)
        description_div.add_class("spt_range_detail_description")

        table.add_row()
        td = table.add_cell("Assigned")
        td.add_style("vertical-align: top")
        assigned_div = DivWdg()
        td = table.add_cell(assigned_div)
        assigned_div.add_class("spt_range_detail_assigned")

        table.add_row()
        td = table.add_cell("Status")
        td.add_style("vertical-align: top")
        status_div = DivWdg()
        table.add_cell(status_div)
        status_div.add_class("spt_range_detail_status")

        table.add_row()
        td = table.add_cell("Length")
        td.add_style("vertical-align: top")
        length_div = DivWdg()
        table.add_cell(length_div)
        length_div.add_class("spt_range_detail_length")


        # build up an assigned dictionary of all of the tasks
        tasks_dict = {}
        assigned_dict = {}
        self.vacations = {}



        if self.search_type == "sthpw/task":

            for task in tasks:
                # bit hacky because not all are tasks
                if task.get_base_search_type() != "sthpw/task":
                    continue


                process = task.get_value("process")
                try:
                    parent_key = "%s&code=%s" % (task.get("search_type"), task.get("search_code") )
                    task_list = tasks_dict.get(parent_key)
                    if task_list == None:
                        task_list = []
                        tasks_dict[parent_key] = task_list
                    task_list.append(task)
                except:
                    print("Warning: Missing search type or search code for tasks")
                assigned = task.get_value("assigned")
                if assigned:
                    assigned_dict[assigned] = {}


            # get special tasks
            search = Search("sthpw/task")
            search.add_filters("assigned", assigned_dict.keys() )
            search.add_filters("process", ["vacation","sick"])
            search.add_filter("bid_start_date", start_date, op=">=")
            search.add_filter("bid_end_date", end_date, op="<=")
            vacation_tasks = search.get_sobjects()

            for vacation in vacation_tasks:
                login = vacation.get_value("assigned")

                vacation_list = self.vacations.get(login)
                if vacation_list == None:
                    vacation_list = []
                    self.vacations[login] = vacation_list

                vacation_list.append(vacation)


            items_div.add_relay_behavior( {
                'type': 'click',
                'bvr_match_class': 'spt_vacation',
                'cbjs_action': '''
                '''
            } )


        if self.nobs_mode == "hover":

            hover_class = ProdSetting.get_value_by_key("gantt_range_hover_class")

            # group range hover behavior (mouseenter)
            items_div.add_relay_behavior( {
                'type': 'mouseenter',
                'bvr_match_class': "spt_group_range",
                'cbjs_action': '''
                var nobs = bvr.src_el.getElements(".spt_nob");
                for (var i = 0; i < nobs.length; i++) {
                    nobs[i].setStyle("display", "");
                }

                '''
            } )

            # group range hover behavior (mouseleave)
            items_div.add_relay_behavior( {
                'type': 'mouseleave',
                'bvr_match_class': "spt_group_range",
                'cbjs_action': '''
                var nobs = bvr.src_el.getElements(".spt_nob");
                for (var i = 0; i < nobs.length; i++) {
                    nobs[i].setStyle("display", "none");
                }

                '''
            } )

            items_div.add_relay_behavior( {
                'type': 'mouseenter',
                'bvr_match_class': "spt_range",
                'hover_class': hover_class,
                'cbjs_action': '''


                // Retrieve all template/tooltips divs
                var top = bvr.src_el.getParent(".spt_gantt_top");
                var detail_span = top.getElement(".spt_range_detail");
                detail_span.setAttribute("spt_range_active", "true");

                // if the item is being dragged, we want to disable mouseenter event.
                drag = detail_span.getAttribute("drag");
                if (drag == "true") {
                    return;
                }

                var nobs = bvr.src_el.getElements(".spt_nob");
                for (var i = 0; i < nobs.length; i++) {
                    nobs[i].setStyle("display", "");
                }



                var process_div = detail_span.getElement(".spt_range_detail_process");
                var description_div = detail_span.getElement(".spt_range_detail_description");
                var assigned_div = detail_span.getElement(".spt_range_detail_assigned");
                var status_div = detail_span.getElement(".spt_range_detail_status");
                var length_div = detail_span.getElement(".spt_range_detail_length");


                // Retrieve all data from hovered-over element
                var search_key = bvr.src_el.getAttribute("spt_search_key");
                var process = bvr.src_el.getAttribute("spt_process");
                var description = bvr.src_el.getAttribute("spt_description");
                var status = bvr.src_el.getAttribute("spt_status");
                var assigned = bvr.src_el.getAttribute("spt_assigned");
                var length = bvr.src_el.getAttribute("spt_length");
                var start_display = bvr.src_el.getAttribute("spt_start_display");
                var end_display = bvr.src_el.getAttribute("spt_end_display");
                var has_nobs = bvr.src_el.getAttribute("spt_has_nobs");
                var pos = bvr.src_el.getBoundingClientRect();
                var top_pos = top.getBoundingClientRect();


                // Set all data into tooltip divs
                detail_span.setAttribute("spt_search_key", search_key);
                if (process_div) {
                    process_div.innerHTML = (process) ? process : "N/A";
                    description_div.innerHTML = (description) ? description: "N/A";
                    assigned_div.innerHTML = (assigned) ? assigned : "N/A";
                    status_div.innerHTML = (status) ? status : "N/A";
                    length_div.innerHTML = (length) ? length + " days" : "N/A";
                }

                // Position and display the main tooltip
                detail_span.setStyle("top", pos.bottom - top_pos.top );
                detail_span.setStyle("left", pos.left - top_pos.left);

                // Boundary checks and adjustments
                var detail_pos = detail_span.getBoundingClientRect();
                if (detail_pos.bottom > top_pos.bottom) {
                    detail_span.setStyle("top", pos.top - top_pos.top - detail_pos.height);
                }
                if (detail_pos.right > top_pos.right) {
                    detail_span.setStyle("left", pos.right - top_pos.left - detail_pos.width);
                }

                detail_span.setStyle("visibility", "visible");

                '''
            } )

            items_div.add_relay_behavior( {
                'type': 'mouseleave',
                'bvr_match_class': "spt_range",
                'cbjs_action': '''
                var nobs = bvr.src_el.getElements(".spt_nob");

                bvr.src_el.setAttribute("active", "false");
                var top = bvr.src_el.getParent(".spt_gantt_top");
                var detail_span = top.getElement(".spt_range_detail");
                detail_span.setAttribute("spt_range_active", "false");

                setTimeout(function() {
                    var detail_active = detail_span.getAttribute("spt_detail_active");
                    var range_active = detail_span.getAttribute("spt_range_active");
                    if (detail_active == "true" || range_active == "true") {
                        return;
                    }

                    detail_span.setStyle("visibility", "hidden");

                    for (var i = 0; i < nobs.length; i++) {
                        nobs[i].setStyle("display", "none");
                    }




                }, 1000);


                '''
            } )





        self.group_rows = self.kwargs.get("group_rows")
        group_index = 0
        if self.group_rows:
            self.group_rows.reverse()
            current_group = self.group_rows[0]
        else:
            current_group = None


        """
        for i, sobject in enumerate(self.sobjects):
            search_key = sobject.get_search_key()
            sobject_tasks = tasks_dict.get(search_key)
            print("search_key: ", search_key)
            print("tasks: ", sobject_tasks)
        """

        # auto group detection
        auto_grouping = self.kwargs.get("auto_grouping")
        if auto_grouping == None:
            auto_grouping = True

        group_level = 0

        first_group = True
        for j, sobject in enumerate(self.sobjects):

            if not auto_grouping:
                group_level = sobject.get_value("group_level", no_exception=True)

            else:
                while True:

                    has_new_group = False

                    # handle groups
                    if current_group:
                        if first_group:
                            has_new_group = True
                            current_group = self.group_rows[0]
                            first_group = False

                        elif group_index < len(self.group_rows) - 1:

                            next_group = self.group_rows[group_index+1]
                            next_group_sobjects = next_group.get_sobjects()
                            if next_group_sobjects:
                                next_first_sobject = next_group_sobjects[0]
                                if sobject.get_search_key() == next_first_sobject.get_search_key():
                                    has_new_group = True
                                    group_index += 1
                                    current_group = self.group_rows[group_index]

                            # if there are no element in the next group, then create a group
                            else:
                                has_new_group = True
                                group_index += 1
                                current_group = self.group_rows[group_index]



                    if not has_new_group:
                        break
                    else:
                        group_sobjects = current_group.get_sobjects()
                        group_level = current_group.group_level

                        group_div = self.get_group_wdg(group_level, group_sobjects, start_date, end_date, "#111")
                        items_div.add(group_div)

                group_level += 1



            if cache:
                items = cache.get( sobject.get_search_key() )
            else:
                items = [sobject]

            if not items:
                items = []

            handler = self.kwargs.get("handler")
            if handler in ['task']:
                tasks = items
                items_wdg = self.get_task_wdg(sobject, tasks, start_date, end_date, group_level=group_level)

            elif handler in ['sobject']:
                self.index = j
                items = [sobject]
                items_wdg = self.get_sobject_wdg(sobject, items, start_date, end_date, group_level=group_level)
            else:
                items_wdg = self.get_custom_wdg(sobject, items, start_date, end_date, group_level=group_level)


            #items_wdg.add_style("border: none")
            items_wdg.add_style("box-sizing: border-box")

            # TODO: the alignment issue is due to improper scaling in windows
            # Chrome
            #items_wdg.add_style("margin-bottom: -0.4px")
            # Firefox
            #items_wdg.add_style("margin-bottom: -0.15px")

            items_div.add_style("margin-top: -1px")


            items_div.add(items_wdg)



        if self.kwargs.get("is_refresh"):
            return gantt_div
        else:
            return top



    def get_group_wdg(self, group_level, group_sobjects, start_date, end_date, color=None):

        #group_sobjects = current_group.get_sobjects()
        #group_level = current_group.group_level
        if not color:
            color = "#999"

        group_div = DivWdg()
        group_div.add_class("spt_gantt_row_item")
        group_div.add_class("spt_group_range_top")
        group_div.add_style("height: 28px")
        group_div.add_style("box-sizing: border-box")
        group_div.add_style("width: 100%")
        group_div.add_style("position: relative")
        group_div.add_style("background: rgba(224, 224, 224, 0.3)")
        group_div.add_style("border-bottom: solid 1px #EEE")

        group_div.add_attr("spt_group_level", group_level)

        start_column = self.kwargs.get("start_column") or "bid_start_date"
        end_column = self.kwargs.get("end_column") or "bid_end_date"

        # find the range of the group
        group_start_date = None
        group_end_date = None

        group_search_keys = []
        for group_sobject in group_sobjects:
            bid_start_date = group_sobject.get_value(start_column, no_exception=True)
            bid_end_date = group_sobject.get_value(end_column, no_exception=True)


            if not bid_start_date or not bid_end_date:
                continue

            group_search_key = group_sobject.get_search_key()
            group_search_keys.append(group_search_key)


            if not group_start_date or bid_start_date < group_start_date:
                group_start_date = bid_start_date
            if not group_end_date or bid_end_date > group_end_date:
                group_end_date = bid_end_date

            if not group_end_date:
                group_end_date = group_start_date


        group_div.add_attr("spt_search_keys", ",".join(group_search_keys) )

        snap_mode = "day"
        if snap_mode == "day" and group_start_date and group_end_date:
            group_start_date = SPTDate.strip_time(group_start_date)

            group_end_date = SPTDate.strip_time(group_end_date) + timedelta(days=1) - timedelta(seconds=1)



        #print("group_start_date: ", group_start_date)
        #print("group_end_date: ", group_end_date)
        #print("---")

        # FiXME: not sure why expressions are so much slower here than the
        # above code
        """
        group_start_date = Search.eval("@MIN(.bid_start_date)", group_sobjects)
        group_end_date = Search.eval("@MAX(.bid_end_date)", group_sobjects)

        print("group_start_date: ", group_start_date)
        print("group_end_date: ", group_end_date)
        """

        group_offset = self.get_percent(start_date, group_start_date)
        if group_offset < 0:
            group_offset = 0


        group_width = self.get_percent(group_start_date, group_end_date)

        group_item = DivWdg()
        group_div.add(group_item)
        group_item.add_style("height: 5px")
        group_item.add_style("width: %s%%" % group_width)
        group_item.add_style("left: %s%%" % group_offset)
        group_item.add_style("position: absolute")
        group_item.add_style("top: 5px")
        group_item.add_class("hand")

        group_item.add_style("background: " + color)
        #group_item.add_gradient("background", "#BBCCBB", -10)


        group_item.add_class("spt_gantt_element")
        group_item.add_class("spt_group_range")
        group_item.add_attr("spt_start_date", group_start_date)
        group_item.add_attr("spt_end_date", group_end_date)
        group_item.add_attr("spt_group_level", group_level)


        left_group_nob = DivWdg()
        group_item.add(left_group_nob)
        left_group_nob.add_style("position: absolute")
        left_group_nob.add_style("left: -3px")
        left_group_nob.add_style("height: 0px")
        left_group_nob.add_style("width: 0px")
        left_group_nob.add_style("border-left: 5px solid transparent")
        left_group_nob.add_style("border-right: 5px solid transparent")
        left_group_nob.add_style("border-top: 18px solid" + color)


        right_group_nob = DivWdg()
        group_item.add(right_group_nob)
        right_group_nob.add_style("position: absolute")
        right_group_nob.add_style("right: -3px")
        right_group_nob.add_style("height: 0px")
        right_group_nob.add_style("width: 0px")
        right_group_nob.add_style("border-left: 5px solid transparent")
        right_group_nob.add_style("border-right: 5px solid transparent")
        right_group_nob.add_style("border-top: 18px solid" + color)

        nob_background = "#FFF"
        border_color = "rgb(137, 137, 137)"



        if isinstance(group_start_date, basestring):
            group_start_date = parser.parse(group_start_date)
        if isinstance(group_end_date, basestring):
            group_end_date = parser.parse(group_end_date)



        left = DivWdg()
        group_item.add(left)
        left.add_class("spt_nob")
        left.add_class("spt_nob_update")
        left.add_style("display: none")
        left.add_style("position: absolute")
        left.add_style("height: 12px")
        left.add_style("width: 80px")
        left.add_style("box-shadow: 0px 0px 15px rgba(0,0,0,0.5)")
        left.add_style("border: solid 1px %s" % border_color)
        left.add_style("left: -33px")
        left.add_style("top: -22px")
        left.add_style("padding: 2px")
        left.add_style("text-align: center")
        left.add_style("background", nob_background)
        left.add_style("line-height: 12px")

        if group_start_date:
            start_display = group_start_date.strftime("%b %d")
            left.add(start_display)


        right = DivWdg()
        group_item.add(right)
        right.add_class("spt_nob")
        right.add_class("spt_nob_update")
        right.add_style("display: none")
        right.add_style("position: absolute")
        right.add_style("height: 12px")
        right.add_style("width: 80px")
        right.add_style("box-shadow: 0px 0px 15px rgba(0,0,0,0.5)")
        right.add_style("border: solid 1px %s" % border_color)
        right.add_style("right: -33px")
        right.add_style("top: -22px")
        right.add_style("padding: 2px")
        right.add_style("text-align: center")
        right.add_style("background", nob_background)
        right.add_style("line-height: 12px")

        if group_end_date:
            end_display = group_end_date.strftime("%b %d")
            right.add(end_display)

        group_div.nobs_mode = "hover"


        return group_div





    """
    def get_task_wdg(self, sobject, tasks, start_date, end_date, group_level=0):

        search_key = sobject.get_search_key()


        # this is the actual outside of the row
        item_div = DivWdg()
        item_div.add_class("spt_gantt_row_item")
        item_div.add_attr("spt_search_key", search_key)
        item_div.add_class("spt_range_top")

        item_div.add_attr("SPT_ACCEPT_DROP", "spt_range_top")

        item_div.add_style("height: 23px")
        item_div.add_style("width: 100%")
        item_div.add_style("position: relative")
        item_div.add_style("z-index: %s" % (100-self.range_index))
        self.range_index += 1

        item_div.add_style("border-style", "solid")
        item_div.add_style("border-width", "0px 1px 1px px")
        item_div.add_color("border-color", "#EEE")

        item_div.add_style("box-sizing", "border-box")





        # draw all the items inside this "row"
        for i, task in enumerate(tasks):

            task_key = task.get_search_key()

            assigned = task.get_value("assigned")
            status = task.get_value("status")

            # incorporate workflow dependency

            task_pipeline_code = task.get_value("pipeline_code")
            if not task_pipeline_code:
                task_pipeline_code = "task"
            task_pipeline = Pipeline.get_by_code(task_pipeline_code)


            depend_keys = self.get_depend_keys(task)


            process = task.get_value("process")


            # set the color by status
            status = task.get_value("status")
            color = None
            if task_pipeline:
                status_obj = task_pipeline.get_process(status)
                if status_obj:
                    color = status_obj.get_color()
            if not color:
                color = "rgba(207,215,188,1.0)"


            bid_start_date = task.get_datetime_value("bid_start_date")
            bid_end_date = task.get_datetime_value("bid_end_date")
            bid_duration = task.get_value("bid_duration")


            top_margin = 4

            if not bid_start_date:
                today = datetime.today()
                bid_start_date = datetime(today.year, today.month, today.day)

            if not bid_end_date:
                bid_end_date = bid_start_date + timedelta(days=1)
                bid_end_date = datetime(bid_end_date.year, bid_end_date.month, bid_end_date.day)


            # set the time for full days
            snap_mode = "day"
            if snap_mode == "day":
                bid_start_date = SPTDate.strip_time(bid_start_date)
                bid_end_date = SPTDate.strip_time(bid_end_date) + timedelta(days=1) - timedelta(seconds=1)



            offset = self.get_percent(start_date, bid_start_date)
            if offset < 0:
                offset = 0

            width = self.get_percent(bid_start_date, bid_end_date)


            # deal with vacations
            # TODO: move this outside this function
            if assigned:
                vacation_list = self.vacations.get(assigned) or []

                for vacation in vacation_list:
                    vacation_start_date = vacation.get("bid_start_date")
                    vacation_end_date = vacation.get("bid_end_date")


                    vacation_offset = self.get_percent(start_date, vacation_start_date)
                    if vacation_offset < 0:
                        vacation_offset = 0

                    vacation_width = self.get_percent(vacation_start_date, vacation_end_date)


                    vacation_div = DivWdg()
                    item_div.add(vacation_div)
                    vacation_div.add_class("spt_gantt_element")
                    vacation_div.add_attr("spt_start_date", vacation_start_date)
                    vacation_div.add_attr("spt_end_date", vacation_end_date)

                    vacation_div.add_style("position: absolute")
                    vacation_div.add_style("top: 0px")
                    vacation_div.add_style("left: %s%%" % vacation_offset)
                    vacation_div.add_style("width: %s%%" % vacation_width)
                    vacation_div.add_style("height: 12px")
                    vacation_div.add_style("background: #A66")
                    vacation_div.add_style("color: #FFF")
                    vacation_div.add_style("font-size: 0.8em")
                    vacation_div.add_style("vertical_align: middle")
                    vacation_div.add_style("text-align: center")
                    vacation_div.add_style("overflow: hidden")

                    vacation_process = vacation.get_value("process")

                    vacation_div.add(vacation_process)





            # draw the individual element
            range_div = DivWdg()
            item_div.add(range_div)
            range_div.add_class("spt_range")
            range_div.add_class("spt_gantt_element")
            range_div.add_attr("spt_search_key", task_key)



            range_div.add_update( {
                'search_key': search_key,
                'column': 'bid_start_date',
                'return': 'sobject',
                'cbjs_action': '''
                // check to see if the range has been changed
                if (bvr.src_el.hasClass("spt_changed")) {
                    //bvr.src_el.setStyle("background-color", "#F00");
                    //bvr.src_el.setStyle("color", "#FFF");
                }
                else {
                    var sobject = bvr.value;
                    spt.gantt.set_date(bvr.src_el, sobject.bid_start_date, sobject.bid_end_date);
                }
                '''

            } )





            if depend_keys:
                range_div.add_attr("spt_depend_keys", ",".join(depend_keys) )


            bid_start_date_str = bid_start_date.strftime("%Y-%m-%d %H:%M")
            bid_end_date_str = bid_end_date.strftime("%Y-%m-%d %H:%M")
            range_div.add_attr("spt_start_date", bid_start_date_str)
            range_div.add_attr("spt_end_date", bid_end_date_str)
            range_div.add_style("z-index: 10")



            range_div.add_style("opacity: 0.8")
            range_div.add_attr("spt_duration", bid_duration)

            # position the range
            range_div.add_style("position", "absolute")
            range_div.add_style("left: %s%%" % offset)



            # draw the range shape
            border_color = range_div.get_color("border")


            description = task.get_value("description")
            if not description:
                description = task.get_value("process")

            #range_div.add_style("font-size: 0.8em")


            task_type = task.get_value("task_type", no_exception=True)
            if task_type in ["milestone", "delivery"]:

                range_div.add_attr("spt_range_type", "milestone")

                milestone_wdg = self.get_milestone_wdg(sobject, color)
                range_div.add( milestone_wdg )
                milestone_wdg.add_style("pointer-events: none")

                range_div.add("<div style='font-weight: bold; height: 100%%; width: auto; max-width: 150px; text-overflow: ellipsis; white-space: nowrap; overflow: hidden; pointer-events: none; margin-top: -13px; margin-left: 25px;'>%s</div>" % description)
                range_div.add_style("margin-top: %spx" % top_margin)
                has_nobs = False

            else:
                range_div.add_attr("spt_range_type", "range")


                range_div.add_class("hand")
                range_div.add_style("margin-top: %spx" % top_margin)
                range_div.add_style("height: 18px")


                range_div.add_style("border-style: solid")
                range_div.add_style("border-width: 1px")
                range_div.add_style("border-color: %s" % border_color)

                range_div.add_style("width: %s%%" % width)

                range_div.add_style("background: %s" % color)

                has_nobs = True






                task_diff = bid_end_date - bid_start_date
                task_duration = float(task_diff.days) + float(task_diff.seconds)/(24*3600)

                task_breaks = [
                        { 'offset': 1, 'duration': 2, 'color': '#FFF' },
                        { 'offset': 5, 'duration': 2, 'color': '#FFF' } ,
                        { 'offset': 2, 'duration': 0.5, 'color': '#0FF' }
                ]
                task_breaks = []

                task_data = task.get_json_value("data") or {}
                if task_data:
                    task_breaks = task_data.get("break") or {}



                #task_breaks = []

                if task_breaks:

                    # add some breaks
                    days_div = DivWdg()
                    range_div.add(days_div)
                    days_div.add_style("position: absolute")
                    days_div.add_style("z-index: 10")
                    days_div.add_style("top: 0px")
                    days_div.add_style("height: 100%")
                    days_div.add_style("width: 100%")
                    days_div.add_style("overflow: hidden")
                    days_div.add_style("pointer-events: none")



                    for task_break in task_breaks:

                        day_div = DivWdg()
                        days_div.add(day_div)

                        break_offset = float(task_break.get("offset")) / task_duration * 100
                        break_duration = float(task_break.get("duration")) / task_duration * 100
                        break_color = task_break.get("color") or "#FFF"


                        day_div.add_style("display: inline-block")
                        day_div.add_style("position: absolute")
                        day_div.add_style("box-sizing: border-box")
                        day_div.add_style("height: 100%")
                        day_div.add_style("width: %s%%" % break_duration)
                        day_div.add_style("top: 0px")
                        day_div.add_style("left: %s%%" % break_offset)
                        day_div.add("&nbsp;")

                        day_div.add_style("background: %s" % break_color)





                show_description = True
                if show_description:


                    # add a description

                    text_div = DivWdg()
                    range_div.add(text_div)
                    text_div.add_style("position: relative")
                    text_div.add_style("height: 100%")
                    text_div.add_style("z-index: 100")
                    text_div.add_style("text-overflow: ellipsis")
                    text_div.add_style("white-space: nowrap")
                    text_div.add_style("overflow: hidden")
                    text_div.add_style("pointer-events: none")
                    text_div.add_style("margin: 0px 3px")
                    text_div.add(description)


            if process:
                range_div.add_attr("spt_process", process)
                #detail_span.add("Process: %s" % process)


            #detail_span.add("<br clear='all'/>")
            if description and description != process:
                range_div.add_attr("spt_description", description)
                #detail_span.add("Description: %s" % description)
                #detail_span.add("<br clear='all'/>")

            if assigned:
                user = Search.get_by_code("sthpw/login", assigned)
                name = assigned
                if user:
                    name = user.get_value("display_name")
                    if not name:
                        name = user.get_value("login")
                range_div.add_attr("spt_assigned", name)
                #detail_span.add("Assigned: %s" % name)
                #detail_span.add("<br clear='all'/>")


            if status:
                range_div.add_attr("spt_status", status)
                #detail_span.add("Status: %s" % status)
                #detail_span.add("<br clear='all'/>")


            days = (bid_end_date - bid_start_date).days + 1
            range_div.add_attr("spt_length", days)
            #detail_span.add("Length: %s days" % days)
            #detail_span.add("<br clear='all'/>")



            start_display = bid_start_date.strftime("%b %d")
            end_display = bid_end_date.strftime("%b %d")

            range_div.add_attr("spt_start_display", start_display)
            range_div.add_attr("spt_end_display", end_display)

            if self.nobs_mode != "none" and has_nobs:
                range_div.add_attr("spt_has_nobs", True)
            else:
                range_div.add_attr("spt_has_nobs", False)

        return item_div




    def get_depend_keys(self, task):

        process = task.get("process")

        # TODO: this may be slow to do for every task.  Maybe better to do
        # in bulk.  Also, this may be better done at initial task creation.
        parent = task.get_parent()



        # get the main pipeline
        pipeline_code = parent.get_value("pipeline_code", no_exception=True)
        if pipeline_code:
            pipeline = Pipeline.get_by_code(pipeline_code)
        else:
            pipeline = None


        if not pipeline:
            return []


        # remamp pipeline process and pipeline
        parent_process = None
        if process.find("/") != -1:
            parts = process.split("/")
            parent_process = parts[0]
            process = parts[1]

            s = Search("config/process")
            s.add_filter("pipeline_code", pipeline_code)
            s.add_filter("process", parent_process)
            process_sobj = s.get_sobject()

            pipeline_code = process_sobj.get("subpipeline_code")
            if pipeline_code:
                pipeline = Pipeline.get_by_code(pipeline_code)



        process_obj = pipeline.get_process(process)


        depend_keys = []


        # need to build a dependency tree ...
        output_processes = pipeline.get_output_processes(process)


        # get the task key that this is dependent
        from pyasm.biz import Task
        for output_process in output_processes:
            output_process_name = output_process.get_name()

            output_process_type = output_process.get_type()

            if output_process_type == "hierarchy":
                s = Search("config/process")
                s.add_filter("pipeline_code", pipeline_code)
                s.add_filter("process", output_process_name)
                output_process_sobj = s.get_sobject()

                if output_process_sobj:
                    subpipeline_code = output_process_sobj.get("subpipeline_code")
                else:
                    subpipeline_code = None


                if subpipeline_code:
                    subpipeline = Pipeline.get_by_code(subpipeline_code)
                    subpipeline_process_names = subpipeline.get_process_names()
                    if subpipeline_process_names:
                        first = subpipeline_process_names[0]
                        output_process_name = "%s/%s" % (output_process_name, first)


            if parent_process:
                output_process_name = "%s/%s" % (parent_process, output_process_name)


            # FIXME: this is slow ... should get from a cache
            output_tasks = Task.get_by_sobject(parent, process=output_process_name)
            output_keys = [x.get_search_key() for x in output_tasks]
            depend_keys.extend(output_keys)


        return depend_keys
    """



    """
    def get_milestone_wdg(self, sobject, color):

        top = DivWdg()
        top.add_class("spt_milestone")
        border_color = top.get_color("border")

        div1 = DivWdg()
        top.add(div1)
        unique_id = div1.set_unique_id()

        size = 10

        style = HtmlElement.style()
        self.top.add(style)
        style.add('''
#%(unique_id)s {
    width: 0;
    height: 0;
    border: %(size)spx solid transparent;
    border-bottom-color: %(color)s;
    position: relative;
    top: -%(size)spx;
}

#%(unique_id)s:after {
    content: '';
    position: absolute;
    left: -%(size)spx;
    top: %(size)spx;
    width: 0;
    height: 0;
    border: %(size)spx solid transparent;
    border-top-color: %(color)s;
}
        ''' % {"unique_id": unique_id, "size": size, "color": border_color} )


        size = 8

        div2 = DivWdg()
        top.add(div2)
        unique_id = div2.set_unique_id()
        div2.add_style("margin-top: -%spx" % (size*2+2))
        div2.add_style("margin-left: 2px")


        style = HtmlElement.style()
        self.top.add(style)
        style.add('''
#%(unique_id)s {
    width: 0;
    height: 0;
    border: %(size)spx solid transparent;
    border-bottom-color: %(color)s;
    position: relative;
    top: -%(size)spx;
}

#%(unique_id)s:after {
    content: '';
    position: absolute;
    left: -%(size)spx;
    top: %(size)spx;
    width: 0;
    height: 0;
    border: %(size)spx solid transparent;
    border-top-color: %(color)s;
}
        ''' % {"unique_id": unique_id, "size": size, "color": color} )



        return top

    """





    def get_onload_js(self):

        return r'''

if (spt.gantt) {
//    return;
}

spt.Environment.get().add_library("spt_gantt");


spt.gantt = {};
spt.gantt.top = null;

spt.gantt.percent_per_day = null;

spt.gantt.hours_in_day = 8;
spt.gantt.start_of_day = "9:00:00";
spt.gantt.end_of_day = "5:00:00";
spt.gantt.min_date = null;
spt.gantt.max_date = null;
spt.gantt.special_days = [];


spt.gantt.set_top = function( el ) {

    spt.gantt.top = el;

    var info = spt.gantt.get_info();
    spt.gantt.percent_per_day = info.percent_per_day;
    spt.gantt.min_date = info.min_date;
    spt.gantt.max_date = info.max_date;
    spt.gantt.special_days = info.special_days;
}


spt.gantt.get_top = function() {
    return spt.gantt.top;
}

spt.gantt.set_month_highlight = function() {
    var highlight = spt.gantt.get_top().getParent().getChildren(".month_highlight")[0];
    var canvas = spt.gantt.get_canvas();
    var width = canvas.width;
    var min_date = moment(spt.gantt.min_date);
    var percent_per_day = spt.gantt.percent_per_day;
    var day_pos = 1 * percent_per_day * width / 100;

    var start_of_month = moment().startOf('month');
    var curr_month_width = moment().daysInMonth() * percent_per_day * width / 100;
    var month_offset = spt.gantt.get_diff(min_date, start_of_month);
    month_offset = parseInt(month_offset);
    var month_start = month_offset*day_pos;
    if (month_start < 0) { month_start = 0; }
    var month_end = month_offset*day_pos+curr_month_width;
    if (month_end > width) { month_end = width; }
    var month_size = month_end - month_start;
    if (month_end < 0 || month_start > width) { month_size = 0; }

    highlight.setStyle("left", month_start);
    highlight.setStyle("width", month_size);
}

spt.gantt.get_month_highlight = function() {
    var highlight = spt.gantt.get_top().getParent().getChildren(".month_highlight")[0];
    return highlight;
}

spt.gantt.set_week_highlight = function() {
    var highlight = spt.gantt.get_top().getParent().getChildren(".week_highlight")[0];
    var canvas = spt.gantt.get_canvas();
    var width = canvas.width;
    var min_date = moment(spt.gantt.min_date);
    var percent_per_day = spt.gantt.percent_per_day;
    var day_pos = 1 * percent_per_day * width / 100;

    var start_of_week = moment().startOf('isoWeek');
    var week_width = 7 * percent_per_day * width / 100;
    var week_offset = spt.gantt.get_diff(min_date, start_of_week);
    week_offset = parseInt(week_offset);
    var week_start = week_offset*day_pos;
    if (week_start < 0) { week_start = 0; }
    var week_end = week_offset*day_pos+week_width;
    if (week_end > width) { week_end = width; }
    var week_size = week_end - week_start;
    if (week_end < 0 || week_start > width) { week_size = 0; }

    highlight.setStyle("left", week_start);
    highlight.setStyle("width", week_size);
}

spt.gantt.get_week_highlight = function() {
    var highlight = spt.gantt.get_top().getParent().getChildren(".week_highlight")[0];
    return highlight;
}

spt.gantt.set_info = function(new_info) {
    var top = spt.gantt.top;
    var info = top.info;
    var updated_info = Object.assign(info, new_info);
    top.info = updated_info;
    return updated_info;
}


spt.gantt.get_info = function(name) {
    var top = spt.gantt.top;
    var info = top.info;
    if (!info) {
        info = {
            percent_per_day: null,
            min_date: null,
            max_date: null,
            special_days: [],

            hours_in_day: 8,
            start_of_day: "9:00:00",
            end_of_day: "5:00:00",

            weekend_highlights: false,
            curr_month_highlights: true,
            curr_week_highlights: false,
            month_lines: false,
            week_lines: false,
            day_lines: false,
            special_days_highlights: true,

            toggle_ghost: true,

            curr_layout: 'Year',
            toggle_weekend: true,

            hide_out_of_range: false,

            undo_queue: [],
            undo_index: -1,
            undo_current: null,
        }
        top.info = info;
    }

    if (name) {
        return info[name];
    }

    return info;
}


spt.gantt.get_context = function(name) {
    var top = spt.gantt.top;
    var canvas = spt.gantt.get_canvas(name);
    var context = canvas.getContext("2d");
    return context;
}

spt.gantt.get_canvas = function(name) {
    var top = spt.gantt.top;

    if (!name || name == "grid") {
        var canvas = top.getElement(".spt_gantt_canvas")
    }
    else {
        var canvas = top.getElement(".spt_gantt_"+name+"_canvas")
    }

    return canvas;
}

spt.gantt.clear = function(name) {

    if (name) {
        var canvas = spt.gantt.get_canvas(name);
        var context = canvas.getContext("2d");
        context.clearRect(0, 0, canvas.width, canvas.height);
    }
    else {
        var canvas = spt.gantt.get_canvas("grid");
        var context = canvas.getContext("2d");
        context.clearRect(0, 0, canvas.width, canvas.height);

        var canvas = spt.gantt.get_canvas("connector");
        var context = canvas.getContext("2d");
        context.clearRect(0, 0, canvas.width, canvas.height);

    }
}




spt.gantt.reload = function(start_date, end_date) {
    var search_keys = spt.gantt.get_all_search_keys();


    var canvas = spt.gantt.get_canvas();
    var width = canvas.width;

    var top = spt.gantt.top;
    var class_name = 'tactic.ui.gantt.GanttWdg';
    var kwargs = {
        search_keys: search_keys,
        range_start_date: spt.gantt.min_date,
        range_end_date: spt.gantt.max_date,
        width: width,

    }

    spt.panel.load(top, class_name, kwargs);
}



spt.gantt.add_new_row = function(range_top, gantt_type, search_key, insert_location) {

    var top = spt.gantt.top;

    var template_top = top.getElement(".spt_gantt_template_top");

    var template = null;
    var templates = template_top.getElements(".spt_gantt_row_item");


    for (var i = 0; i < templates.length; i++) {
        var item_type = templates[i].getAttribute("spt_gantt_type");
        if (item_type == gantt_type) {
            template = templates[i];
            break;
        }
    }

    if ( !template ) {
        template = templates[0];
    }


    var clone = spt.behavior.clone(template);

    if (insert_location == "top") {
        gantt_top = spt.gantt.get_top();
        items_top = gantt_top.getElement(".spt_gantt_items_top");
        items_top.insertBefore(clone, items_top.childNodes[0]);
    } else {
        clone.inject(range_top, "after");
    }

    if (search_key) {
        clone.setAttribute("spt_search_key", search_key)
    }


    // resize the group
    var group_ranges = spt.gantt.get_group_ranges(clone);
    for (var j = 0; j < group_ranges.length; j++) {
        var group_range = group_ranges[j];
        spt.gantt.update_group(group_range);
    }


    return clone;
}



spt.gantt.add_new_item = function(row, gantt_type) {

    var top = spt.gantt.top;

    var template_top = top.getElement(".spt_gantt_template_top");

    var template = null;
    var templates = template_top.getElements(".spt_gantt_row_item");
    for (var i = 0; i < templates.length; i++) {
        var item_type = templates[i].getAttribute("spt_gantt_type");
        if (item_type == gantt_type) {
            template = templates[i];
            break;
        }
    }

    if (template == null) {
        var templates = template_top.getElements(".spt_template_item");
        for (var i = 0; i < templates.length; i++) {
            var item_type = templates[i].getAttribute("spt_gantt_type");
            if (item_type == gantt_type) {
                template = templates[i];
                break;
            }
        }
    }

    if (!template) {
        throw("Could not find template for gantt type ["+gantt_type+"]");
    }


    var clone = spt.behavior.clone(template);
    clone.removeClass(".spt_template_item");

    clone.inject(row, "bottom");

    // resize the group
    var group_ranges = spt.gantt.get_group_ranges(clone);
    for (var j = 0; j < group_ranges.length; j++) {
        var group_range = group_ranges[j];
        spt.gantt.update_group(group_range);
    }



    return clone;

}







// get all of the elements on the canvas
spt.gantt.get_all_elements = function() {
    var top = spt.gantt.top;
    var item_top = top.getElement(".spt_gantt_items_top");
    var elements = item_top.getElements(".spt_gantt_element");
    return elements;
}


// range functions
spt.gantt.get_all_ranges = function() {
    var top = spt.gantt.top;
    var item_top = top.getElement(".spt_gantt_items_top");
    var els = item_top.getElements(".spt_range");
    return els;
}

spt.gantt.get_range_by_search_key = function(search_key) {
    var top = spt.gantt.top;
    var els = top.getElements(".spt_range");
    for (var i = 0; i < els.length; i++) {
        var el_search_key = els[i].getAttribute("spt_search_key");
        if (el_search_key == search_key) {
            return els[i];
        }
    }

    return null;
}


spt.gantt.get_range_by_name = function(name) {
    var top = spt.gantt.top;
    var els = top.getElements(".spt_range");
    for (var i = 0; i < els.length; i++) {
        var el_name = els[i].getAttribute("spt_process");
        if (el_name == name) {
            return els[i];
        }
    }

    return null;
}


spt.gantt.get_ranges_by_search_keys = function(search_keys) {
    var top = spt.gantt.top;
    var els = top.getElements(".spt_range");

    var ranges = [];
    for (var i = 0; i < els.length; i++) {
        var el_search_key = els[i].getAttribute("spt_search_key");
        if (search_keys.indexOf(el_search_key) != -1) {
            ranges.push( els[i] );
        }
    }

    return ranges;
}




spt.gantt.get_value = function(search_key, column) {
    var range = spt.gantt.get_range_by_search_key(search_key);

    var info = spt.gantt.get_dates_from_range(range);
    var value = info[column];
    return value;
}



// group methdods
spt.gantt.get_all_group_ranges = function() {
    var top = spt.gantt.top;
    var els = top.getElements(".spt_group_range");
    return els;
}


spt.gantt.get_all_ranges_in_group = function(group) {
    if (! group.hasClass(".spt_group_range_top")) {
        group = group.getParent(".spt_group_range_top");
    }

    var search_keys = group.getAttribute("spt_search_keys");
    search_keys = search_keys.split(",");

    var ranges = []
    for (var i = 0; i < search_keys.length; i++) {
        var search_key = search_keys[i];
        var range = spt.gantt.get_range_by_search_key(search_key);
        ranges.push(range);
    }

    return ranges;
}





// range functions
spt.gantt.get_all_search_keys = function() {
    var top = spt.gantt.top;
    var els = top.getElements(".spt_range_top");
    var search_keys = [];
    for (var i = 0; i < els.length; i++) {
        var search_key = els[i].getAttribute("spt_search_key");
        search_keys.push(search_key);
    }
    return search_keys;
}





spt.gantt.get_dates_from_range = function(el, format) {

    var start_date = el.getAttribute("spt_start_date");
    var end_date = el.getAttribute("spt_end_date");

    if (start_date && end_date) {
        var diff = moment.duration(moment(end_date).diff(moment(start_date)));
        var duration = diff.asSeconds() / (24*3600);
    }
    else {
        var duration = 0;
    }


    return {
        start_date: start_date,
        end_date: end_date,
        duration: duration,
    }

}


spt.gantt.get_dates_by_size = function(el, format) {

    var parent = el.getParent();
    var pos = el.getPosition(parent);
    var size = el.getSize();


    var canvas = spt.gantt.get_canvas();
    var width = canvas.getSize().x;

    var min_date = spt.gantt.min_date;

    var percent_per_day = spt.gantt.percent_per_day;

    var start_percent = pos.x / width * 100;
    var end_percent = (pos.x+size.x) / width * 100;
    var duration_percent = size.x / width * 100;

    var start_days = parseInt( start_percent / percent_per_day ) + 0.5;
    var start_date = moment(min_date).add(start_days*24, 'hour');

    var end_days = parseInt( end_percent / percent_per_day ) - 0.5;
    var end_date = moment(min_date).add(end_days*24, 'hour');

    // TODO: account for weekends?
    var hours_in_day = spt.gantt.hours_in_day;
    var duration = duration_percent / percent_per_day * hours_in_day;

    if (!format) {
        format = "";
    }

    return {
        start_date: start_date.format(format),
        end_date: end_date.format(format),
        duration: duration,
    }

}




spt.gantt.set_date = function(el, start_date, end_date) {
    var min_date = moment(spt.gantt.min_date);
    var start_date = moment(start_date);
    var end_date = moment(end_date);

    var mseconds_in_day = 24 * 3600 * 1000;

    var start_percent = (start_date - min_date) * spt.gantt.percent_per_day / mseconds_in_day;
    var width_percent = (end_date - start_date) * spt.gantt.percent_per_day / mseconds_in_day;


    // do not draw if this element is not visible
    var info = spt.gantt.get_info();
    if (info.hide_out_of_range) {
        if (start_percent > 100) {
            el.setStyle("display", "none");
            return;
        }
        else if (start_percent + width_percent < 0) {
            el.setStyle("display", "none");
            return;
        }
        else {
            el.setStyle("display", "inline-block");
        }
    }




    el.setStyle("left", start_percent + "%");

    if (el.getAttribute("spt_range_type") == "milestone") {
        // do nothing
    }
    else {
        el.setStyle("width", width_percent + "%");
    }
}



spt.gantt.get_selected_ranges = function() {

    var gantt_top = spt.gantt.get_top();
    var gantt_items_top = gantt_top.getElement(".spt_gantt_items_top");
    var gantt_items = gantt_items_top.getElements(".spt_gantt_row_item");

    var rows = spt.table.get_selected_rows();

    var gantt_ranges = [];
    for ( var i = 0; i < rows.length; i++) {
        var index = rows[i].rowIndex;

        var gantt_item = gantt_items[index];

        var ranges = gantt_item.getElements(".spt_range");
        for (var j = 0; j < ranges.length; j++) {
            gantt_ranges.push(ranges[j]);
        }

    }

    return gantt_ranges;


/*
    var search_keys = spt.table.get_selected_search_keys(false);
    var ranges = spt.gantt.get_ranges_by_search_keys(search_keys);
    return ranges;
*/
}



//
// Drawing methods
//


spt.gantt.redraw_layout = function(start_date, end_date, kwargs={}) {
    var top = spt.gantt.top;

    var info = spt.gantt.get_info();

    kwargs.is_refresh = true;
    kwargs.range_start_date = start_date;
    kwargs.range_end_date = end_date;

    var layout = top.getParent(".spt_gantt_layout_top");

    var header_top = layout.getElement(".spt_gantt_header_top");
    var class_name = 'tactic.ui.gantt.GanttHeaderWdg';
    spt.gantt.redraw_header(kwargs);
    //spt.panel.load(header_top, class_name, kwargs, null, {show_loading: false, async: true});
    //spt.panel.refresh_element(header_top, {range_start_date: start_date, range_end_date: end_date});
    spt.gantt.redraw(start_date, end_date);
}

spt.gantt.redraw_header = function(kwargs={}, gantt_header_top=null) {
    const MS_IN_DAY = 1000*60*60*24;
    // set gantt header inner top
    var top = gantt_header_top;
    if (top == null) {
        var gantt_top = spt.gantt.top;
        var layout = gantt_top.getParent(".spt_gantt_layout_top");
        top = layout.getElement(".spt_gantt_header_top");
    }

    var elements = top.elements;
    if (!elements) {
        elements = {};
        top.elements = elements;
        elements.inner = top.getElement(".spt_state_save");

        inner = elements.inner;
        elements.btn_shelf = inner.getElement(".spt_shelf");
        var btn_shelf = elements.btn_shelf;
        elements.btn_left = btn_shelf.getElement(".spt_gantt_left");
        elements.btn_right = btn_shelf.getElement(".spt_gantt_right");
        elements.btn_zoom_in = btn_shelf.getElement(".spt_gantt_zoom_in");
        elements.btn_zoom_out = btn_shelf.getElement(".spt_gantt_zoom_out");
    }


    //var inner = top.getElement(".spt_state_save");
    var inner = elements.inner;

    // init
    var min_date = kwargs.range_start_date;
    var max_date = kwargs.range_end_date;

    var width = kwargs.width? kwargs.width : "100%";

    var start_date = Date.parse(min_date);
    var end_date = Date.parse(max_date);

    var diff = end_date - start_date;

    // don't navigate to an invalid date range
    if (diff == 0) {
        return;
    }

    var total_days = diff/MS_IN_DAY;
    var percent_width = 100;
    var percent_per_day = (total_days != 0)? (percent_width/total_days) : 0;


    // set state data
    inner.setAttribute("spt_start_date", min_date);
    inner.setAttribute("spt_end_date", max_date)
    var state_data = {min_date: min_date, max_date: max_date}
    var state_data_str = JSON.stringify(state_data);
    inner.setAttribute("spt_state_data", state_data_str);

    // remove old date elements
    var redraw_els = inner.getElements(".spt_gantt_header_redraw");
    //var redraw_els = elements.redraw_els;

    for (var i = 0; i < redraw_els.length; i++) {
        inner.removeChild(redraw_els[i]);
    }

    var height = "50%";

    // not sure what this is supposed to do in python:
    // inner.set_id("self.generate_unique_id())


    // refresh button kwargs
    var temp_date, temp_string;
    //var btn_shelf = inner.getElement(".spt_shelf");
    var btn_shelf = elements.btn_shelf;
    diff = total_days * 0.1;

    // left/right buttons should always move date range at least one day

    var lr_diff = diff;
    if (lr_diff < 1) {
        lr_diff = 1;
    }

    // left button
    //var btn_left = btn_shelf.getElement(".spt_gantt_left");
    var btn_left = elements.btn_left;
    spt.gantt.adjust_button_date(btn_left, start_date, end_date, lr_diff, lr_diff);

    // right button
    //var btn_right = btn_shelf.getElement(".spt_gantt_right");
    var btn_right = elements.btn_right;
    spt.gantt.adjust_button_date(btn_right, start_date, end_date, -lr_diff, -lr_diff);

    if (diff < 1) {
        diff = 1/6;
    }

    // zoom in button
    //var btn_zoom_in = btn_shelf.getElement(".spt_gantt_zoom_in");
    var btn_zoom_in = elements.btn_zoom_in;
    spt.gantt.adjust_button_date(btn_zoom_in, start_date, end_date, diff, -diff);

    // zoom out button
    //var btn_zoom_out = btn_shelf.getElement(".spt_gantt_zoom_out");
    var btn_zoom_out = elements.btn_zoom_out;
    spt.gantt.adjust_button_date(btn_zoom_out, start_date, end_date, -diff, diff);

    // yearly
    var dates = new RRule({freq: RRule.MONTHLY, byyearday: 1, dtstart: start_date, until: end_date}).all();
    if (dates.length == 0 || dates[0] != start_date) {
        // unshift might be slow
        dates.unshift(start_date);
    }
    if (dates.length == 0 || dates[dates.length - 1] != end_date) {
        dates.push(end_date);
    }
    
    var years_div = document.createElement("div");
    inner.appendChild(years_div);
    years_div.addClass("spt_gantt_header_redraw");
    years_div.setStyle("width", "100%");
    years_div.setStyle("overflow-x", "hidden");
    years_div.setStyle("white-space", "nowrap");
    
    dates.pop();
    dates.forEach(function(date, i) {
        var year_div = document.createElement("div");
        years_div.appendChild(year_div);
        year_div.addClass("spt_gantt_header_range");

        var sdate = new Date(date);
        sdate.setDate(1);

        var edate = new Date(date);
        edate.setDate(1);
        edate.setYear(edate.getFullYear() + 1);

        year_div.setAttribute("spt_start_date", sdate.toLocaleDateString("en-CA"));
        year_div.setAttribute("spt_end_date", edate.toLocaleDateString("en-CA"));

        if (dates.length == 1) {
            year_div.setStyle("width", "100%");
        } else {
            if (i == 0) {
                diff = dates[i+1] - start_date;
            } else if (i == (dates.length - 1)) {
                diff = end_date - date;
            } else {
                diff = dates[i+1] - date;
            }

            var days = diff/MS_IN_DAY;
            year_div.setStyle("width", percent_per_day*days + "%");
        }

        year_div.setStyle("text-align", "center");
        year_div.setStyle("display", "inline-block");
        year_div.setStyle("box-sizing", "border-box");
        year_div.setStyle("overflow", "hidden");
        year_div.addClass("hand");
        year_div.setStyle("border-style", "solid");
        year_div.setStyle("border-width", "0px 1px 1px 0px");
        year_div.setStyle("border-color", spt.Environment.get().get_colors().table_border);
        year_div.setStyle("height", "100%");
        year_div.setStyle("background", "#FFF");

        var t = document.createElement("div");
        year_div.appendChild(t);
        
        t.addClass("spt_gantt_header_center");
        t.innerHTML = date.getFullYear().toString();
    });

    // monthly
    dates = new RRule({freq: RRule.MONTHLY, bymonthday: 1, dtstart: start_date, until: end_date}).all();

    if (dates.length == 0 || dates[0] != start_date) {
        dates.unshift(start_date);
    }
    if (dates.length == 0 || dates[dates.length - 1] != end_date) {
        dates.push(end_date);
    }

    var months_div = document.createElement("div");
    inner.appendChild(months_div);
    months_div.addClass("spt_gantt_header_redraw");
    months_div.setStyle("width", "100%");
    months_div.setStyle("overflow-x", "hidden");
    months_div.setStyle("white-space", "nowrap");

    dates.pop();
    dates.forEach(function(date, i) {
        var month_div = document.createElement("div");
        months_div.appendChild(month_div);
        month_div.addClass("spt_gantt_header_range");

        var sdate = new Date(date);
        sdate.setDate(1);

        var edate = new Date(date);
        edate.setDate(1);
        edate.setMonth(edate.getMonth() + 1);

        month_div.setAttribute("spt_start_date", sdate.toLocaleDateString("en-CA"));
        month_div.setAttribute("spt_end_date", edate.toLocaleDateString("en-CA"));

        if (dates.length == 1) {
            month_div.setStyle("width", "100%");
        } else {
            if (i == 0) {
                diff = dates[i+1] - start_date;
            } else if (i == (dates.length - 1)) {
                diff = end_date - date;
            } else {
                diff = dates[i+1] - date;
            }

            var days = diff/MS_IN_DAY;
            month_div.setStyle("width", percent_per_day*days + "%");
        }

        month_div.setStyle("text-align", "center");
        month_div.setStyle("display", "inline-block");
        month_div.setStyle("box-sizing", "border-box");
        month_div.setStyle("overflow", "hidden");
        month_div.addClass("hand");
        month_div.addClass("spt_gantt_header_month");
        month_div.setStyle("border-style", "solid");
        month_div.setStyle("border-width", "0px 1px 1px 0px");
        month_div.setStyle("border-color", spt.Environment.get().get_colors().table_border);
        month_div.setStyle("height", "100%");

        if (i == 0 || i % 2 == 0) {
            month_div.setStyle("background", "#FFF");
        } else {
            month_div.setStyle("background", "#EEE");
        }

        var t = document.createElement("div");
        month_div.appendChild(t);
        
        t.addClass("spt_gantt_header_center");
        t.innerHTML = date.getFullYear().toString();
        var month = date.toLocaleString('en-us', {month: 'short'}).toUpperCase();

        if (total_days > 1800) {
            month = month[0];
        }

        t.innerHTML = month;
    });

    // weekly
    var weeks_div = document.createElement("div");
    if (total_days < 350 && total_days >= 50) {
        height = "33.33%";

        var temp_date = new Date(start_date);
        temp_date.setDate(temp_date.getDate() - 6);
        dates = new RRule({freq: RRule.WEEKLY, dtstart: temp_date, until: end_date, byweekday: [RRule.MO]}).all();

        inner.appendChild(weeks_div);
        weeks_div.addClass("spt_gantt_header_redraw");
        weeks_div.setStyle("width", "100%");
        weeks_div.setStyle("overflow-x", "hidden");
        weeks_div.setStyle("white-space", "nowrap");

        dates.forEach(function(date, i) {
            var week_div = document.createElement("div");
            weeks_div.appendChild(week_div);
            week_div.addClass("spt_gantt_header_range");
            week_div.addClass("hand");

            var sdate = new Date(date);
            sdate.setDate(sdate.getDate() + (2 + 7 - sdate.getDay()) % 7);
            
            var edate = new Date(date);
            edate.setDate(edate.getDate() + 7);
            edate.setDate(edate.getDate() + (2 + 7 - edate.getDay()) % 7);

            week_div.setAttribute("spt_start_date", sdate.toLocaleDateString("en-CA"));
            week_div.setAttribute("spt_end_date", edate.toLocaleDateString("en-CA"));

            if (dates.length == 1) {
                week_div.setStyle("width", "100%");
            } else {
                if (i == 0) {
                    diff = dates[i+1] - start_date;
                } else if (i == (dates.length - 1)) {
                    diff = end_date - date;
                } else {
                    diff = dates[i+1] - date;
                }

                var days = diff/MS_IN_DAY;
                week_div.setStyle("width", percent_per_day*days + "%");
            }

            week_div.setStyle("text-align", "center");
            week_div.setStyle("display", "inline-block");
            week_div.setStyle("box-sizing", "border-box");
            week_div.setStyle("overflow", "hidden");
            week_div.setStyle("border-style", "solid");
            week_div.setStyle("border-width", "0px 1px 1px 0px");
            week_div.setStyle("border-color", "#BBB");
            week_div.setStyle("height", "100%");

            if (i == 0 || i % 2 == 0) {
                week_div.setStyle("background", "#FFF");
            }

            var wday = ('0' + date.getDate()).slice(-2);
            var date2 = new Date(date);
            date2.setDate(date2.getDate() + 6);
            var wday2 = ('0' + date2.getDate()).slice(-2);

            var t = document.createElement("div");
            week_div.appendChild(t);
            t.addClass("spt_gantt_header_center");
            t.innerHTML = wday + "-" + wday2;
        });
    }

    var days_div = document.createElement("div");

    if (total_days < 50) {
        height = "25%";

        dates = new RRule({freq: RRule.DAILY, dtstart: start_date, until: end_date}).all();

        inner.appendChild(days_div);
        days_div.addClass("spt_gantt_header_redraw");
        days_div.setStyle("width", "100%");

        dates.forEach(function(date, i) {
            var day_div = document.createElement("div");
            days_div.appendChild(day_div);

            if (dates.length == 1) {
                day_div.add_style("width", "100%");
            } else {
                if (i == 0) {
                    diff = dates[i+1] - start_date;
                } else if (i == (dates.length - 1)) {
                    diff = end_date - date;
                } else {
                    diff = dates[i+1] - date;
                }

                var days = diff/MS_IN_DAY;

                if (days == 0) {
                    return;
                }

                day_div.setStyle("width", percent_per_day*days + "%");
            }

            day_div.setStyle("text-align", "center");
            day_div.setStyle("display", "inline-block");
            day_div.setStyle("box-sizing", "border-box");
            day_div.setStyle("overflow", "hidden");
            day_div.setStyle("border-style", "solid");
            day_div.setStyle("border-width", "0px 1px 1px 0px");
            day_div.setStyle("border-color", "#BBB");

            if (i == 0 || i % 2 == 0) {
                day_div.setStyle("background", "#FFF");
            }

            var mday = ('0' + date.getDate()).slice(-2);
            var wday = date.toLocaleDateString("en-us", {weekday: 'short'}).substring(0,2);
            day_div.innerHTML= mday + "<br/>" + wday;
        });
    }

    // TODO: make sure show_time value is preserved from initial load,
    // currently not passed in anywhere!
    var show_time = kwargs.show_time;

    if (show_time == 'false' || show_time == false || show_time == "False") {
        show_time = false;
    } else {
        show_time = true;
    }

    var hours_div = document.createElement("div");


    if (show_time && total_days < 21) {
        dates = new RRule({freq: RRule.HOURLY, dtstart: start_date, until: end_date}).all();

        if (total_days > 10) {
            dates = dates.filter(function(date, i) {return (i % 8) == 0});
        } else if (total_days > 2) {
            dates = dates.filter(function(date, i) {return (i % 4) == 0});
        }

        inner.appendChild(hours_div);
        hours_div.addClass("spt_gantt_header_redraw");
        hours_div.setStyle("width", "100%");
        hours_div.setStyle("font-size", "0.8em");

        dates.forEach(function(date, i) {
            var hour = ('0' + date.getHours()).slice(-2);

            hour_div = document.createElement("div");
            hours_div.appendChild(hour_div);

            if (dates.length == 1) {
                hour_div.add_style("width", "100%");
            } else {
                if (i == 0) {
                    diff = dates[i+1] - start_date;
                } else if (i == (dates.length - 1)) {
                    diff = end_date - date;
                } else {
                    diff = dates[i+1] - date;
                }

                var days = diff/MS_IN_DAY;

                var width_val = percent_per_day*days;

                if (width_val == 0) {
                    return;
                }

                hour_div.setStyle("width", width_val + "%");
            }

            hour_div.setStyle("text-align", "center");
            hour_div.setStyle("display", "inline-block");
            hour_div.setStyle("box-sizing", "border-box");
            hour_div.setStyle("overflow", "hidden");
            hour_div.setStyle("border-style", "solid");
            hour_div.setStyle("border-width", "0px 1px 1px 0px");
            hour_div.setStyle("border-color", "#BBB");

            hour_div.setStyle("background", "#FFF");

            hour_div.innerHTML = hour;
        });

    }

    years_div.setStyle("height", height);
    months_div.setStyle("height", height);
    weeks_div.setStyle("height", height);
    days_div.setStyle("height", height);
    hours_div.setStyle("height", height);

    return;
}

spt.gantt.adjust_button_date = function(button, start_date, end_date, start_diff, end_diff) {
    var start_date = new Date(start_date);
    var end_date = new Date(end_date);

    start_date.setDate(start_date.getDate() + start_diff);
    end_date.setDate(end_date.getDate() + end_diff);

    var start_string = start_date.toLocaleDateString("en-ca") + " 00:00:00";
    var end_string = end_date.toLocaleDateString("en-ca") + " 00:00:00";

    button.setAttribute("spt_range_start_date", start_string);
    button.setAttribute("spt_range_end_date", end_string);

    return button;
};


spt.gantt.resize_layout = function( seconds, kwargs={} ) {

    var new_diff = seconds * 1000;

    var data = spt.gantt.get_layout_date_range();
    var start_date = data.start_date;
    var end_date = data.end_date;

    start_date = moment(start_date);
    end_date = moment(end_date)

    var diff = moment.duration(moment(end_date).diff(moment(start_date)));
    var duration = diff.asSeconds() / (24*3600);


    var midpoint = start_date + (diff/2);

    var new_start_date = moment(midpoint - new_diff);
    var new_end_date = moment(midpoint + new_diff);

    spt.gantt.redraw_layout(new_start_date.format(), new_end_date.format(), kwargs)

}




spt.gantt.set_gantt_scroll = function(offset) {

    var top = spt.gantt.top;
    var scroll = top.getParent(".spt_gantt_scroll");
    var scroll = top.getParent(".spt_resizable_cell");
    scroll.scrollLeft = offset;
}



spt.gantt.set_gantt_width = function(width) {

    var top = spt.gantt.top;
    var scroll = top.getParent(".spt_gantt_scroll");
    scroll.setStyle("width", width);

    var layout_top = top.getParent(".spt_gantt_layout_top");
    layout_top.setAttribute("spt_gantt_width", width);
}


/*
spt.gantt_get_screen_date_range = function(start_date, end_date) {

    var top = spt.gantt.top;
    var scroll = top.getParent(".spt_resizable_cell");
    var scroll_size = scroll.getSize();
    var scroll_left = scroll.scrollLeft;
    var gantt_size = top.getSize();

}
*/






spt.gantt.fit_layout = function(kwargs) {

    if (!kwargs) kwargs = {};

    var top = spt.gantt.top;
    var elements = spt.gantt.get_all_elements();

    var start_date = null;
    var end_date = null;

    var fit_search_keys = kwargs.search_keys;
    if (fit_search_keys) fit_search_keys = [];

    var search_keys = spt.table.get_selected_search_keys(false)

    for (var i = 0; i < elements.length; i++) {

        var element = elements[i];

        var search_key = element.getAttribute("spt_search_key");

        if (fit_search_keys && fit_search_keys.length > 0) {
            if (! fit_search_keys.includes(search_key)) {
                continue;
            } 


        }


        if (kwargs.visible_only == true ) {
            if (search_keys.length && search_keys.indexOf(search_key) == -1) {
                continue;
            }
        }



        var info = spt.gantt.get_dates_from_range(elements[i]);

        if (info.start_date == "None" || info.end_date == "None") {
            continue;
        }

        if (!start_date || info.start_date < start_date) {
            start_date = info.start_date;
        }
        if (!end_date || info.end_date > end_date) {
            end_date = info.end_date;
        }
    }

    if (start_date == null || end_date == null) {
        return;
    }




    start_date = moment(start_date);
    end_date = moment(end_date)

    var diff = moment.duration(end_date.diff(start_date));

    var new_start_date = moment(start_date - diff/20);
    var new_end_date = moment(end_date + diff/20);

    spt.gantt.redraw_layout(new_start_date.format(), new_end_date.format());

}



spt.gantt.shift_layout_to_date = function( date ) {

    var data = spt.gantt.get_layout_date_range();
    var start_date = data.start_date;
    var end_date = data.end_date;

    start_date = moment(start_date);
    end_date = moment(end_date)

    var diff = moment.duration(moment(end_date).diff(moment(start_date))) / 2;

    var midpoint = moment(date);

    var new_start_date = moment(midpoint - diff);
    var new_end_date = moment(midpoint + diff);

    spt.gantt.redraw_layout(new_start_date.format(), new_end_date.format())

}


spt.gantt.shift_layout_to_today = function() {
    var today = new Date();
    var dd = today.getDate();
    var mm = today.getMonth()+1; //January is 0!
    var yyyy = today.getFullYear();

    spt.gantt.shift_layout_to_date(yyyy + "-" + mm + "-" + dd );
}


spt.gantt.shift_layout = function( diff, kwargs={} ) {

    var data = spt.gantt.get_layout_date_range();
    var start_date = data.start_date;
    var end_date = data.end_date;

    start_date = moment(start_date);
    end_date = moment(end_date)

    var new_start_date = moment(start_date).add(diff, 'seconds');
    var new_end_date = moment(end_date).add(diff, 'seconds');

    spt.gantt.redraw_layout(new_start_date.format(), new_end_date.format(), kwargs)
}



spt.gantt.shift_layout_by_percent = function( percent ) {

    var data = spt.gantt.get_layout_date_range();
    var start_date = data.start_date;
    var end_date = data.end_date;

    start_date = moment(start_date);
    end_date = moment(end_date)

    var diff = moment.duration(moment(end_date).diff(moment(start_date))) / 2000;

    var shift = diff * percent / 100;

    spt.gantt.shift_layout(shift);
}




spt.gantt.get_layout_date_range = function() {
    var top = spt.gantt.top;
    var layout = top.getParent(".spt_gantt_layout_top");
    var header_top = layout.getElement(".spt_gantt_header_top");

    var start_date = header_top.getAttribute("spt_range_start_date");
    var end_date = header_top.getAttribute("spt_range_end_date");

    var data = {
        start_date: start_date,
        end_date: end_date,
        //duration: duration,
    }

    return data;



}



spt.gantt.redraw = function(start_date, end_date) {

    var gantt_top = spt.gantt.get_top();

    if (spt.gantt.cached_ranges == null) {
        var ranges = spt.gantt.get_all_elements();
        gantt_top.cached_ranges = ranges;
    }
    var ranges = gantt_top.cached_ranges;

    setTimeout( function() {
        gantt_top.cached_ranges = null;
    }, 10000 )

    //var ranges = spt.gantt.get_all_elements();

    var ranges_info = [];
    for (var i = 0; i < ranges.length; i++) {
        var range = ranges[i];
        var info = spt.gantt.get_dates_from_range(range);
        ranges_info.push(info);
    }


    spt.gantt.min_date = start_date;
    spt.gantt.max_date = end_date;

    var layout = gantt_top.getParent(".spt_gantt_layout_top");
    var header_top = layout.getElement(".spt_gantt_header_top");
    header_top.setAttribute("spt_range_start_date", start_date);
    header_top.setAttribute("spt_range_end_date", end_date);



    var diff = spt.gantt.get_diff( start_date, end_date);
    spt.gantt.percent_per_day = 100 / diff;

    var info = spt.gantt.get_info();
    info.min_date = start_date;
    info.max_date = end_date;
    info.percent_per_day = 100 / diff;


    var last_group_level = "0";

    for (var i = 0; i < ranges.length; i++) {
        var range = ranges[i];
        var range_info = ranges_info[i];
        spt.gantt.set_date(range, range_info.start_date, range_info.end_date);

        var group_level = range.getAttribute("spt_group_level");
        if (group_level == last_group_level) {
            continue;
        }
        last_group_level = group_level;


        // resize the group
        var group_ranges = spt.gantt.get_group_ranges(range);
        for (var j = 0; j < group_ranges.length; j++) {
            var group_range = group_ranges[j];
            spt.gantt.update_group(group_range);
        }

    }

    spt.gantt.clear();
    spt.gantt.draw_grid();
    spt.gantt.draw_connects();


}


spt.gantt.draw_connect = function(start, end, next, color) {

    //var context = spt.gantt.get_context();

    var top = spt.gantt.top;
    var canvas = top.getElement(".spt_gantt_connector_canvas")
    var context = canvas.getContext("2d");

    context.beginPath();
    context.setLineDash([]);
    context.lineWidth = 1;

    if (!color) {
        color = "#000";
    }
    if (start.x > end.x) {
        color = "#000";
    }

    context.strokeStyle = color;

    context.moveTo(start.x, start.y);

    if (start.x < end.x){
        //context.lineTo(0.1*end.x + 0.9*start.x, start.y);
        //context.lineTo(0.1*end.x + 0.9*start.x, end.y);
        context.lineTo(start.x + 10, start.y);
        context.lineTo(start.x + 10, end.y);
    }

    else{
        context.lineTo(start.x + 10, start.y);
        context.lineTo(start.x + 10, start.y + (end.y - start.y) / 2);
        context.lineTo(end.x - 10, start.y - (start.y - end.y) / 2);
        context.lineTo(end.x - 10, end.y);


    }
    context.lineTo(end.x, end.y);
    context.lineTo(end.x - 3, end.y - 3);
    context.lineTo(end.x - 2, end.y);
    context.lineTo(end.x - 3, end.y + 3);
    context.lineTo(end.x, end.y);


    //context.moveTo(start.x, start.y);
    //context.lineTo(end.x, end.y);
    //context.lineTo(next, start.y + 6);
    //context.lineTo(next, end.y);
    //context.lineTo(end.x - 6, end.y + 12);
    //context.lineTo(end.x - 6, end.y + 24);
    //context.lineTo(next, end.y + 24);
    context.stroke();
}

spt.gantt.draw_direct_connect = function(start, end, color) {
    var context = spt.gantt.get_context();
    context.beginPath();
    context.lineWidth = 1;

    if (!color) {
        color = "#F00";
    }
    context.strokeStyle = color;

    context.moveTo(start.x, start.y);
    context.lineTo(end.x, end.y);
    context.stroke();
}



spt.gantt.get_dependent_ranges = function(range) {

    var depend_keys = range.getAttribute("spt_depend_keys");
    if (!depend_keys) {
        return [];
    }

    depend_keys = depend_keys.split(",");

    var top = spt.gantt.top;
    var mode = top.getAttribute("spt_mode");

    var depend_ranges = [];
    for (var i = 0; i < depend_keys.length; i++) {
        if (mode == 'preview'){
            var depend_range = spt.gantt.get_range_by_name(depend_keys[i]);
        } else {
            var depend_range = spt.gantt.get_range_by_search_key(depend_keys[i]);
        }
        depend_ranges.push(depend_range);
    }

    return depend_ranges;
}



spt.gantt.draw_connects = function() {

    var ranges = spt.gantt.get_all_ranges();
    var top = spt.gantt.get_top();

    if (!top.isVisible()) {
        return;
    }


    for (var i = 0; i < ranges.length-1; i++) {

        // find the range that this connects to
        var depend_ranges = spt.gantt.get_dependent_ranges(ranges[i]);

        var start_el = ranges[i];

        var range_type = start_el.getAttribute("spt_range_type");
        if (!range_type) {
            range_type = "range";
        }


        for (var j = 0; j < depend_ranges.length; j++) {

            var end_el = depend_ranges[j];
            if (!end_el) {
                continue;
            }

            var start_pos = start_el.getPosition(top);
            var end_pos = end_el.getPosition(top);
            var start_size = start_el.getSize();
            var end_size = end_el.getSize();
            var next = end_pos.x + end_el.getSize().x/10;

            if (range_type == "milestone") {
                var start = {x: start_pos.x + 12, y: start_pos.y+start_size.y/2};
                var end = {x: end_pos.x, y: end_pos.y+10};
            }
            else {
                var start = {x: start_pos.x + start_size.x, y: start_pos.y+start_size.y/2};
                var end = {x: end_pos.x, y: end_pos.y+end_size.y/2};
            }


            spt.gantt.draw_connect(start, end, next);
        }

    }

}


spt.gantt.draw_connect_to_pos = function(start_el, pos) {
    var top = spt.gantt.get_top();
    var start_pos = start_el.getPosition(top);
    var start_size = start_el.getSize();
    var start = {x: start_pos.x+start_size.x/2, y: start_pos.y+start_size.y/2};
    spt.gantt.draw_direct_connect(start, pos, "#0F0");
}



spt.gantt.draw_grid = function() {

    var context = spt.gantt.get_context();
    var canvas = spt.gantt.get_canvas()

    if (!canvas.isVisible()) {
        return;
    }

    var min_date = moment(spt.gantt.min_date);
    var max_date = moment(spt.gantt.max_date);

    var weekday = min_date.weekday();
    var next_weekend = 6 - weekday;


    var height = canvas.height;
    var width = canvas.width;

    var unit = "day"

    var percent_per_day = spt.gantt.percent_per_day;


    var month_width =  30 * percent_per_day * width / 100;


    var week_pos = 7 * percent_per_day * width / 100;
    var week_width = 2 * percent_per_day * width / 100;
    var offset = next_weekend * percent_per_day * width / 100;

    var day_pos = 1 * percent_per_day * width / 100;
    var day_width = 1 * percent_per_day * width / 100;

    if (month_width < 40) {
        spt.gantt.set_info({month_lines: true});
        spt.gantt.set_info({week_lines: false});
    } else if (week_width > 5) {
        spt.gantt.set_info({month_lines: false});
        spt.gantt.set_info({weekend_highlights: true});
    } else if (week_width > 4){
        spt.gantt.set_info({month_lines: false});
        spt.gantt.set_info({weekend_highlights: false});
        spt.gantt.set_info({week_lines: true});
    }

    if (day_width > 5) {
        spt.gantt.set_info({day_lines: true});
    } else {
        spt.gantt.set_info({day_lines: false});
    }


    if (spt.gantt.get_info("month_lines")) {
        var year = min_date.year();
        var month = min_date.month();

        var num_months = max_date.diff((min_date), 'months', true)

        for (var i = 0; i < num_months; i++) {

            month += 1;
            if (month == 13) {
                month = 1;
                year += 1;
            }

            if ( month < 10) {
                var date = year + "-0" + month + "-01";
            }
            else {
                var date = year + "-" + month + "-01";
            }
            var current = moment(date);

            var diff = moment.duration(current.diff(min_date)).asSeconds();
            var pos = diff / (3600 * 24) * percent_per_day * width / 100;
            context.lineWidth = 1;
            context.moveTo(pos, 0);
            context.fillStyle = "#F0F0F0";
            context.fillRect(pos, 0, 1, canvas.height);
        }



    }


    // draw weekends
    spt.gantt.set_info({weekend_highlights: true});
    if (spt.gantt.get_info("weekend_highlights") && spt.gantt.get_info("toggle_weekend")) {

        var num_weeks = max_date.diff((min_date), 'weeks', true);

        for (var i = 0; i < num_weeks; i++) {
            var start = {x: offset+i*week_pos, y: 0};
            var end   = {x: offset+i*week_pos+week_width, y: canvas.height};
            var size = {x: end.x-start.x, y: end.y-start.y};

            context.lineWidth = 1;
            context.moveTo(start.x, start.y);
            context.fillStyle = "#F0F0F0";
            context.fillRect(start.x,start.y,size.x, size.y);
        }

    }


    if (spt.gantt.get_info("week_lines")){

        var num_weeks = max_date.diff((min_date), 'weeks', true);

        // draw weekends lines
        for (var i = 0; i < num_weeks; i++) {
            var start = {x: offset+i*week_pos, y: 0};
            var end   = {x: offset+i*week_pos+week_width, y: canvas.height};
            var size = {x: end.x-start.x, y: end.y-start.y};


            context.lineWidth = 1;
            context.moveTo(start.x, start.y);
            context.fillStyle = "#F0F0F0";
            context.fillRect(start.x,start.y,1, size.y);
        }

    }

    // draw days
    if (spt.gantt.get_info("day_lines")) {
        var offset = 0;

        var num_days = max_date.diff((min_date), 'days', true);

        for (var i = 0; i < num_days; i++) {
            var start = {x: offset+i*day_pos, y: 0};
            var end   = {x: offset+i*day_pos+day_width, y: canvas.height};
            var size = {x: end.x-start.x, y: end.y-start.y};

            context.lineWidth = 1;
            context.moveTo(start.x, start.y);
            context.fillStyle = "#E9E9E9";
            context.fillRect(start.x,start.y, 1, size.y);
        }
    }

    // draw current  month
    var show_month = spt.gantt.get_info("curr_month_highlights");
    spt.gantt.set_month_highlight();
    var month_highlight = spt.gantt.get_month_highlight();
    if (!show_month) {
        month_highlight.setStyle("display", "none");
    } else if (show_month) {
        month_highlight.setStyle("display", "inline-block");
    }

    //draw current week
    var show_week = spt.gantt.get_info("curr_week_highlights");
    spt.gantt.set_week_highlight();
    var week_highlight = spt.gantt.get_week_highlight();
    if (!show_week) {
        week_highlight.setStyle("display", "none");
    } else if (show_week) {
        week_highlight.setStyle("display", "inline-block");
    }


    var special_days = [];

    // draw today
    var today = moment();
    today = today.hour(12);
    today = today.minute(0);
    today = today.second(0);

    special_days.push( {
        name: 'Today',
        date: spt.gantt.today,
        color: "#1494ca",
        style: "dotted"
    } );

    for (var i = 0; i < spt.gantt.special_days.length; i++) {
        special_days.push( spt.gantt.special_days[i] );
    }

    if (spt.gantt.get_info("special_days_highlights")) {
        for (var i = 0; i < special_days.length; i++) {



            var info = special_days[i];

            var offset = spt.gantt.get_diff(min_date, info.date);
            offset = parseInt(offset);

            var start = {x: offset*day_pos, y: 0};
            var end   = {x: offset*day_pos+day_width, y: canvas.height};
            var size = {x: end.x-start.x, y: end.y-start.y};

            switch(info.style) {
                case 'dotted':
                    context.beginPath();
                    context.setLineDash([10, 10]);
                    context.moveTo(start.x + (size.x / 2), start.y);
                    context.lineTo(start.x + (size.x / 2), end.y);
                    context.lineWidth = 2;
                    context.strokeStyle = info.color;
                    context.stroke();
                    break;
                case 'solid':
                    context.beginPath();
                    context.setLineDash([]);
                    context.moveTo(start.x + (size.x / 2), start.y);
                    context.lineTo(start.x + (size.x / 2), end.y);
                    context.lineWidth = 2;
                    context.strokeStyle = info.color;
                    context.stroke();
                    break;
                default:
                    context.beginPath();
                    context.setLineDash([]);
                    context.moveTo(start.x + (size.x / 2), start.y);
                    context.lineTo(start.x + (size.x / 2), end.y);
                    context.lineWidth = 2;
                    context.strokeStyle = info.color;
                    context.stroke();
                    break;
            }
        }
    }

}

spt.gantt.add_special_day = function(name, date, color, style) {
    var special_day = {name: name, date: date, color: color, style: style};
    spt.gantt.special_days.push(special_day);
}


// some time methods
spt.gantt.get_start_date = function(start_date, direction) {

    var start_date = moment(start_date);

    // skip holidays at the start
    while(true) {
        if (spt.gantt.is_holiday(start_date)) {
            if (direction == "back") {
                start_date.subtract(1, 'day');
            }
            else {
                start_date.add(1, 'day');
            }
            continue;
        }
        break;
    }


    return start_date.format();
}


spt.gantt.get_end_date = function(start_date, duration) {

    var hours_in_day = spt.gantt.hours_in_day;

    var end_date = moment(start_date);
    var days = parseInt((duration-0.00001) / hours_in_day);
    var hours = duration - (days * hours_in_day);

    // skip holidays at the start
    while(true) {
        if (spt.gantt.is_holiday(end_date)) {
            end_date.add(1, 'day');
            continue;
        }
        break;
    }


    var day_count = 0;
    for (var i = 0; i < days; ) {
        end_date.add(1, 'day');

        // skip holidayes
        if (spt.gantt.is_holiday(end_date)) {
            continue;
        }

        i += 1;

    }

    end_date = end_date.add(hours, 'hour');

    return end_date.format();

}






spt.gantt.is_holiday = function(date) {


    return false;


    var date = moment(date);
    var day = date.weekday();

    var weekend_days = [0,6];
    for (var i = 0; i < weekend_days.length; i++) {
        if (day == weekend_days[i]) {
            return "weekend";
        }
    }


    var statutory_holidays = [
        '2013-04-02',
        '2013-07-04'
    ];
    for (var i = 0; i < weekend_days.length; i++) {
        if (date.isSame(statutory_holidays[i])) {
            return "statutory";
        }
    }


    return false;

}


spt.gantt.get_diff = function(start_date, end_date) {
    var start_date = moment(start_date);
    var end_date = moment(end_date);
    var diff = end_date - start_date;
    return diff / 3600 / 1000 / 24;

}



spt.gantt.drag_canvas_el = null;

spt.gantt.canvas_drag_setup = function(evt, bvr, mouse_411) {
    var scroll = bvr.src_el.getParent(".spt_resizable_cell");
    spt.gantt.drag_canvas_el = scroll;

    spt.gantt.mouse_start_x = mouse_411.curr_x;
    spt.gantt.mouse_start_y = mouse_411.curr_y;

    spt.gantt.scroll_left = scroll.scrollLeft;

}

spt.gantt.canvas_drag_motion = function(evt, bvr, mouse_411) {
    var scroll = spt.gantt.drag_canvas_el;
    var size = scroll.getSize();

    var dx = mouse_411.curr_x - spt.gantt.mouse_start_x;
    var dy = mouse_411.curr_y - spt.gantt.mouse_start_y;


    var percent = - (dx / size.x) * 100


    scroll.scrollLeft = spt.gantt.scroll_left - dx;

    // FIXME: handle this to move by pixel
    spt.gantt.shift_layout_by_percent(percent);

    spt.gantt.mouse_start_x = mouse_411.curr_x;
}


spt.gantt.canvas_drag_action = function(evt, bvr, mouse_411) {
    spt.gantt.drag_cnavas_el = null;
}




// FIXME: undo is global ... need to scope per gantt chart or tool or something
/*
spt.gantt.undo_queue = [];
spt.gantt.undo_index = -1;
spt.gantt.undo_current = null;
*/



spt.gantt.drag_init = function() {
    spt.gantt.mouse_start_x = null;
    spt.gantt.mouse_start_y = null;

    spt.gantt.el = null;
    spt.gantt.el_start_x = null;
    spt.gantt.el_size = null;

    spt.gantt.els_start_x = [];
    spt.gantt.els_size = [];

    spt.gantt.mode = "move";

    spt.gantt.drag_ranges = [];
    spt.gantt.drag_info = [];

}
spt.gantt.drag_init()

spt.gantt.drag_setup = function(evt, bvr, mouse_411) {
    spt.gantt.drag_init();

    var top = bvr.src_el.getParent(".spt_gantt_top");
    spt.gantt.set_top(top);
    var src_el = spt.behavior.get_bvr_src( bvr );
    if (src_el.hasClass("spt_nob")) {
        src_el = src_el.getParent(".spt_range");
    }


    spt.gantt.drag_ranges = spt.gantt.get_selected_ranges();
    if (spt.gantt.drag_ranges.length == 0) {
        spt.gantt.drag_ranges = [src_el];

    }


    var info = spt.gantt.get_info();

    var undo = [];
    info.undo_current = undo;

    // remove everything after the current index
    var info = spt.gantt.get_info();
    info.undo_queue.push(undo);
    info.undo_index += 1;


    // add to the table undo queue
    var layout = spt.table.get_layout();
    var layout_top = bvr.src_el.getParent(".spt_layout_top");
    var undo_queue = layout_top.undo_queue;
    if (!undo_queue) {
        undo_queue = [];
        layout_top.undo_queue = undo_queue;
        layout_top.redo_queue = [];
    }
    undo_queue.push( {
        element_name: "gantt",
        data: undo,
        search_key: src_el.getAttribute("spt_search_key"),
        type: 'gantt',
        undo: function() {
            spt.gantt.undo();
        },
        redo: function() {
            spt.gantt.redo();
        },
        get_data: function() {
            return {};
        },
        get_extra_data: function() {
            console.log("Saving gantt...");
            console.log(this.data);
            console.log(this.data.length);

            // only use the first one for now
            var save_data = {
                bid_start_date: this.data[0].new_start_date,
                bid_end_date:   this.data[0].new_end_date,
            }
            return save_data;

        }

    });




    for (var i = 0; i < spt.gantt.drag_ranges.length; i++) {
        // make all the nobs appear
        var range = spt.gantt.drag_ranges[i];
        var nobs = range.getElements(".spt_nob");
        for (var j = 0; j < nobs.length; j++) {
            nobs[j].setStyle("display", "");
        }


        var els = range.getElements(".spt_gantt_range_click");
        for (var j = 0; j < els.length; j++) {
            els[j].setStyle("display", "");
        }


        // remember the start_x and size
        var pos = range.getPosition(top)
        var pos_x = pos.x;

        spt.gantt.els_start_x.push(pos_x);
        spt.gantt.els_size.push(range.getSize());


        // push to the undo queue
        var start_date = range.getAttribute("spt_start_date");
        var end_date = range.getAttribute("spt_end_date");

        var range_undo = {
            range: range,
            start_date: start_date,
            end_date: end_date,
        }
        undo.push(range_undo);
    }


    spt.gantt.el = src_el;


    spt.gantt.mouse_start_x = mouse_411.curr_x;
    spt.gantt.mouse_start_y = mouse_411.curr_y;
    var pos = src_el.getPosition(top)
    var pos_x = pos.x;
    spt.gantt.el_start_x = pos_x;

    spt.gantt.el_size = src_el.getSize();


    //var mode_width = 15;
    var mode_width = 3;

    spt.gantt.mode = spt.gantt.el.getAttribute("spt_drag_mode");
    if (!spt.gantt.mode) {
        var top_pos = top.getPosition();
        var mouse_pos = {x: mouse_411.curr_x-top_pos.x, y: mouse_411.curr_y-top_pos.y};
        if (mouse_pos.x - spt.gantt.el_start_x < mode_width) {
            spt.gantt.mode = "left";
        }
        else if (mouse_pos.x - spt.gantt.el_start_x  > spt.gantt.el_size.x - mode_width) {
            spt.gantt.mode = "right";
        }
        else {
            spt.gantt.mode = "move";
        }
    }

    // hide detail span here (we don't want them while dragging)

    spt.gantt.el.setAttribute("spt_detail_active", "false");

    var top = spt.gantt.el.getParent(".spt_gantt_top");
    var detail_span = top.getElement(".spt_range_detail");


    //left_nob_div = top.getElement(".spt_nob_left");
    //right_nob_div = top.getElement(".spt_nob_right");
    //left_nob_div.setStyle("visibility", "hidden");
    //right_nob_div.setStyle("visibility", "hidden");

    detail_span.setStyle("visibility", "hidden");

    // We want to set the flag to be true. This will be used in the mouseenter
    // event to check if the item is being dragged.
    detail_span.setAttribute("drag", "true");

}


spt.gantt.drag_motion = function(evt, bvr, mouse_411) {
    var src_el = spt.behavior.get_bvr_src( bvr );
    if (src_el.hasClass("spt_nob")) {
        src_el = src_el.getParent(".spt_range");
    }
    var dx = mouse_411.curr_x - spt.gantt.mouse_start_x;
    var dy = mouse_411.curr_y - spt.gantt.mouse_start_y;


    var percent_per_day = spt.gantt.percent_per_day;

    // make sure only increments of days
    var top = spt.gantt.top;
    var canvas = top.getElement(".spt_gantt_canvas")
    var size = canvas.getSize();

    var days = 100 / spt.gantt.percent_per_day;
    var size_per_day = size.x / days;

    dx = parseFloat(parseInt(dx / size_per_day) * size_per_day);


    var top = spt.gantt.get_top();
    var top_pos = top.getPosition();

    // draw a new line
    /*
    if (Math.abs(dy) > 10) {
        var pos = {
            x: mouse_411.curr_x - top_pos.x,
            y: mouse_411.curr_y - top_pos.y,
        };
        spt.gantt.draw_connect_to_pos(src_el, pos);
        return;

    }
    */

    /*
    if (Math.abs(dx) < 10) {
        return;
    }
    */



    for (var i = 0; i < spt.gantt.drag_ranges.length; i++) {

        spt.gantt.el = spt.gantt.drag_ranges[i];
        src_el = spt.gantt.drag_ranges[i];

        var el_start_x = spt.gantt.els_start_x[i];
        var el_size = spt.gantt.els_size[i];

        src_el.addClass("spt_changed");

        if (spt.gantt.mode == "right" && i == 0) {
            if (i == 0) {
                var new_size_x = (el_size.x + dx)/size.x*100;
                src_el.setStyle("width", new_size_x+"%");
            }

        }
        else if (spt.gantt.mode == "left") {
            var pos_x = (el_start_x + dx)/size.x*100;
            var new_size_x = (el_size.x - dx)/size.x*100;
            src_el.setStyle("width", new_size_x+"%");
            src_el.setStyle("left", pos_x+"%");
        }
        else {
            var pos_x = (el_start_x + dx)/size.x*100;
            src_el.setStyle("left", pos_x+"%");
        }


        var nobs = spt.gantt.el.getElements(".spt_nob_update");
        if (nobs.length != 0) {
            var info = spt.gantt.get_dates_by_size(src_el, "MMM DD");
            nobs[0].innerHTML = info.start_date;
            nobs[1].innerHTML = info.end_date;
        }

        var info = spt.gantt.get_dates_by_size(src_el);
        spt.gantt.el.setAttribute("spt_start_date", info.start_date);
        spt.gantt.el.setAttribute("spt_end_date", info.end_date);


        // resize the group
        var group_ranges = spt.gantt.get_group_ranges(src_el);
        for (var j = 0; j < group_ranges.length; j++) {
            var group_range = group_ranges[j];
            spt.gantt.update_group(group_range);
        }

    }


    if (src_el.getAttribute("spt_range_type") == "milestone") {
	var hex = src_el.getChildren()[0].getChildren()[2];
        if (hex) {
            hex.classList.add("hovered");
        }
    }

    //spt.gantt.clear();
    //spt.gantt.draw_grid();
    spt.gantt.clear("connector");
    spt.gantt.draw_connects();


}



spt.gantt.drag_action = function(evt, bvr, mouse_411) {

    var dx = mouse_411.curr_x - spt.gantt.mouse_start_x;
    if (Math.abs(dx) < 3) {
        return;
    }


    var layout = bvr.src_el.getParent(".spt_layout");
    spt.table.set_layout(layout);



    var src_el = spt.behavior.get_bvr_src( bvr );
    if (src_el.hasClass("spt_nob")) {
        src_el = src_el.getParent(".spt_range");
    }
    var parent = src_el.getParent(".spt_range_top");


    var info = spt.gantt.get_info();
    var undo = info.undo_current;


    for (var i = 0; i < spt.gantt.drag_ranges.length; i++) {

        spt.gantt.el = spt.gantt.drag_ranges[i];
        var src_el = spt.gantt.drag_ranges[i];
        var parent = src_el.getParent(".spt_range_top");


        var start_column = src_el.getAttribute("spt_start_column");
        if (!start_column) {
            start_column = "bid_start_date";
        }
        var end_column = src_el.getAttribute("spt_end_column");
        if (!end_column) {
            end_column = "bid_end_date";
        }


        // change the background color to match the table
        if (parent) {
            parent.setStyle("background-color", "rgba(207, 215, 188, 0.6)");
        }
        else {
            parent = src_el.getParent(".spt_group_range_top");
        }


        var el_start_x = spt.gantt.els_start_x[i];
        var el_size = spt.gantt.els_size[i];

        var search_key = src_el.getAttribute("spt_search_key")

        var info = spt.gantt.get_dates_by_size(src_el);

        var update_key = src_el.getAttribute("spt_update_key")
        if (!update_key) {
            update_key = search_key
        }

        src_el.setAttribute("spt_duration", info.duration);


        spt.gantt.el.setAttribute("spt_start_date", info.start_date);
        spt.gantt.el.setAttribute("spt_end_date", info.end_date);


        // find index of this item
        var index = 0;
        var item = parent;
        while ( (item = item.previousSibling) != null)
            index++;


        // get the row based on index
        var content = layout.getElement(".spt_table_content");
        var row_items = content.getElements(".spt_table_row_item");
        var row = row_items[index];
        if (row == null) {
            continue;
        }

        // NOTE: this doesn't work because of a bug that doesn't get the first loaded
        // rows due to embedded table
        //var row = spt.table.get_row_by_search_key(search_key);


        var data = row.update_data;
        if (!data) {
            data = {};
            row.update_data = data;
        }

        data[update_key] = {
            bid_start_date: info.start_date,
            bid_end_date: info.end_date,
            bid_duration: info.duration,
        }


        var json_data = JSON.stringify(data);


        row.addClass("spt_row_changed");

        // FIXME: make this more explicit
        if (update_key == search_key) {
            spt.table.add_extra_value(row, start_column, info.start_date)
            spt.table.add_extra_value(row, end_column, info.end_date)
        }
        else {
            var data_column = "data";
            spt.table.add_extra_value(row, data_column, json_data)
        }

        row.setStyle("background-color", "rgba(207, 215, 188, 0.6)");
        row.setAttribute("spt_last_background", "rgba(207, 215, 188, 0.6)");


        var range_undo = undo[i];
        range_undo.new_start_date = info.start_date;
        range_undo.new_end_date = info.end_date;

    }


    // make the nobs disappear
    for (var i = 0; i < spt.gantt.drag_ranges.length; i++) {

        spt.gantt.el = spt.gantt.drag_ranges[i];
        var nobs = spt.gantt.el.getElements(".spt_nob");
        for (var j = 0; j < nobs.length; j++) {
            nobs[j].setStyle("display", "none");
        }

        // *********************************************
        // Hide the nobs (left and right), and detail span
        var top = spt.gantt.el.getParent(".spt_gantt_top");
        var detail_span = top.getElement(".spt_range_detail");

        /*
        left_nob_div = top.getElement(".spt_nob_left");
        right_nob_div = top.getElement(".spt_nob_right");
        left_nob_div.setStyle("visibility", "hidden");
        right_nob_div.setStyle("visibility", "hidden");
        */

        detail_span.setStyle("visibility", "hidden");

        // We want to set the flag to false. This will be used in the mouseenter
        // event to check if the item is being dragged. Since we are done dragging,
        // we are setting it back to false.
        detail_span.setAttribute("drag", "false");

    }

    if (src_el.getAttribute("spt_range_type") == "milestone") {
        var hex = src_el.getChildren()[0].getChildren()[2];
        if (hex) {
            hex.classList.remove("hovered");
        }
    }


    var date_range = spt.gantt.get_layout_date_range();
    if (info.start_date < date_range.start_date) {
        var d = moment.duration(moment(date_range.end_date).diff(moment(date_range.start_date)));
        var n = moment.duration(moment(info.start_date).diff(moment(date_range.start_date)));
        var diff =  (n - (d*0.05)) / 1000;
        spt.gantt.shift_layout(diff);
        //spt.gantt.fit_layout();
    }
    else if (info.end_date > date_range.end_date) {
        var d = moment.duration(moment(date_range.end_date).diff(moment(date_range.start_date)));
        var n = moment.duration(moment(info.end_date).diff(moment(date_range.end_date)));
        var diff =  (n + (d*0.05)) / 1000;
        spt.gantt.shift_layout(diff);
        //spt.gantt.fit_layout();
 
    }
    else {
        spt.gantt.clear();
        spt.gantt.draw_grid();
        spt.gantt.draw_connects();
    }

}



spt.gantt.undo = function() {

    var info = spt.gantt.get_info();

    if (info.undo_index < 0) {
        spt.notify.show_message("No changes to undo");
        return;
    }

    var undo = info.undo_queue[info.undo_index];

    for ( var i = 0; i < undo.length; i++) {
        var undo_range = undo[i];
        spt.gantt.set_date(undo_range.range, undo_range.start_date, undo_range.end_date);

        // resize the group
        var group_ranges = spt.gantt.get_group_ranges(undo_range.range);
        for (var j = 0; j < group_ranges.length; j++) {
            var group_range = group_ranges[j];
            spt.gantt.update_group(group_range);
        }


    }

    info.undo_index -= 1;


    spt.gantt.clear();
    spt.gantt.draw_grid();
    spt.gantt.draw_connects();


}



spt.gantt.redo = function() {
    var info = spt.gantt.get_info();

    if (info.undo_index >= info.undo_queue.length) {
        spt.notify.show_message("No changes to redo");
        return;
    }

    var undo = info.undo_queue[info.undo_index+1];

    for ( var i = 0; i < undo.length; i++) {
        var undo_range = undo[i];
        spt.gantt.set_date(undo_range.range, undo_range.new_start_date, undo_range.new_end_date);


        // resize the group
        var group_ranges = spt.gantt.get_group_ranges(undo_range.range);
        for (var j = 0; j < group_ranges.length; j++) {
            var group_range = group_ranges[j];
            spt.gantt.update_group(group_range);
        }


    }

    info.undo_index += 1;

    spt.gantt.clear();
    spt.gantt.draw_grid();
    spt.gantt.draw_connects();


}





spt.gantt.group_drag_setup = function(evt, bvr, mouse_411) {


    spt.gantt.drag_init();

    var top = bvr.src_el.getParent(".spt_gantt_top");
    spt.gantt.set_top(top);
    var src_el = spt.behavior.get_bvr_src( bvr );

    spt.table.unselect_all_rows();

    spt.gantt.select_group_rows(src_el);

    var selected_drag_ranges = spt.gantt.get_selected_ranges();

    spt.gantt.drag_ranges = selected_drag_ranges;
    spt.gantt.drag_ranges.push(src_el);

    var group_level = src_el.getAttribute("spt_group_level");
    group_level = parseInt(group_level);

    // get all of the sub groups (Not needed anymore
    /*
    var range_top = src_el.getParent(".spt_group_range_top");
    var last_item = range_top;
    while (true) {
        item = last_item.getNext();
        if (!item) break;


        if (item.hasClass("spt_group_range_top")) {
            var group_range = item.getElement(".spt_group_range");
            if (group_range) {
                var sub_group_level = group_range.getAttribute("spt_group_level");
                sub_group_level = parseInt(sub_group_level);

                if (sub_group_level <= group_level) {
                    break;
                }
                else {
                    spt.gantt.drag_ranges.push(group_range);
                }
            }
        }


        last_item = item;
    }
    */


    var info = spt.gantt.get_info();

    var undo = [];
    info.undo_current = undo;

    // remove everything after the current index
    //info.undo_queue.length = info.undo_index+1;

    info.undo_queue.push(undo);
    info.undo_index += 1;


    for (var i = 0; i < spt.gantt.drag_ranges.length; i++) {
        // make all the nobs appear
        var range = spt.gantt.drag_ranges[i];
        var nobs = range.getElements(".spt_nob");
        for (var j = 0; j < nobs.length; j++) {
            nobs[j].setStyle("display", "");
        }

        // remember the start_x and size
        var pos = range.getPosition(top)
        var pos_x = pos.x;
        spt.gantt.els_start_x.push(pos_x);

        spt.gantt.els_size.push(range.getSize());


        // push to the undo queue
        var start_date = range.getAttribute("spt_start_date");
        var end_date = range.getAttribute("spt_end_date");

        var range_undo = {
            range: range,
            start_date: start_date,
            end_date: end_date,
        }
        undo.push(range_undo);
    }


    spt.gantt.el = src_el;


    spt.gantt.mouse_start_x = mouse_411.curr_x;
    spt.gantt.mouse_start_y = mouse_411.curr_y;
    var pos = src_el.getPosition(top)

    var pos_x = pos.x;
    spt.gantt.el_start_x = pos_x;

    spt.gantt.el_size = src_el.getSize();


    var top_pos = top.getPosition();
    var mouse_pos = {x: mouse_411.curr_x-top_pos.x, y: mouse_411.curr_y-top_pos.y};
    if (mouse_pos.x - spt.gantt.el_start_x < 10) {
        spt.gantt.mode = "left";
    }
    else if (mouse_pos.x - spt.gantt.el_start_x  > spt.gantt.el_size.x - 10) {
        spt.gantt.mode = "right";
    }
    else {
        spt.gantt.mode = "move";
    }


}



spt.gantt.group_drag_motion = function(evt, bvr, mouse_411) {
    return spt.gantt.drag_motion(evt, bvr, mouse_411);
}



spt.gantt.group_drag_action = function(evt, bvr, mouse_411) {

    // make all the nobs disappear
    for (var i = 0; i < spt.gantt.drag_ranges.length; i++) {
        var range = spt.gantt.drag_ranges[i];
        var nobs = range.getElements(".spt_nob");
        for (var j = 0; j < nobs.length; j++) {
            nobs[j].setStyle("display", "none");
        }
    }

    spt.gantt.drag_action(evt, bvr, mouse_411);
    spt.table.unselect_all_rows();
}




spt.gantt.get_group_ranges = function(range) {

    if (! range.hasClass("spt_gantt_row_item")) {
        var row = range.getParent(".spt_gantt_row_item");
    }
    else {
        var row = range;
    }

    if (row == null) {
        return [];
    }


    var group_level = row.getAttribute("spt_group_level");


    if (row == null) {
        return [];
    }

    var group_ranges = [];

    var lowest_group_level = group_level;
    while (true) {

        var group = row.getPrevious(".spt_group_range_top");
        if (!group) {
            break;
        }


        if ( group.getAttribute("spt_group_level") >= lowest_group_level ) {
            row = group;
            continue
        }


        lowest_group_level = group.getAttribute("spt_group_level");

        var group_range = group.getElement(".spt_group_range");
        if (group_range) {
            group_ranges.push(group_range);
        }


        row = group;

    }

    return group_ranges;
}



spt.gantt.get_group_search_keys = function(row) {
    if ( row.hasClass("spt_group_range_top")) {
        var top = row;
    }
    else {
        var top = row.getParent(".spt_group_range_top");
    }
    var search_keys = top.getAttribute("spt_search_keys");
    search_keys = search_keys.split(",");
    return search_keys;
}


spt.gantt.get_group_rows = function(row) {

    if (! row.hasClass("spt_gantt_row_item") ) {
        row = row.getParent(".spt_gantt_row_item");
    }

    var group_level = row.getAttribute("spt_group_level");
    var sibling = row.getNext();

    var children = [];

    while (sibling) {
        var sibling_group_level = sibling.getAttribute("spt_group_level");

        if (group_level == null || sibling_group_level == null) {
            children.push(sibling);
        }

        else if (parseInt(sibling_group_level) > parseInt(group_level)) {
            children.push(sibling);
        }
        else {
            break;
        }

        sibling = sibling.getNext();
    }



    return children;


/*
    var search_keys = spt.gantt.get_group_search_keys(row);

    var rows = [];
    for (var i = 0; i < search_keys.length; i++) {
        var search_key = search_keys[i];
        var row = spt.table.get_row_by_search_key(search_key);
        rows.push(row);
    }

    return rows;
*/


}


spt.gantt.get_ranges_in_group = function(row) {

    if (! row.hasClass("spt_gantt_row_item") ) {
        row = row.getParent(".spt_gantt_row_item");
    }

    var group_level = row.getAttribute("spt_group_level");
    var sibling = row.getNext();

    var ranges = [];

    while (sibling) {
        var sibling_group_level = sibling.getAttribute("spt_group_level");

        if (group_level == null || sibling_group_level == null) {
            var items = sibling.getElements(".spt_range");
            for (var i = 0; i < items.length; i++) {
                ranges.push(items[i]);
            }
        }

        else if (parseInt(sibling_group_level) > parseInt(group_level)) {
            var items = sibling.getElements(".spt_range");
            for (var i = 0; i < items.length; i++) {
                ranges.push(items[i]);
            }
        }
        else {
            break;
        }

        sibling = sibling.getNext();
    }



    return ranges;


// Old way
/*

    var search_keys = spt.gantt.get_group_search_keys(row);
    var ranges = spt.gantt.get_ranges_by_search_keys(search_keys);
    return ranges;
*/
}



spt.gantt.select_group_rows = function(row) {

    var ranges = spt.gantt.get_ranges_in_group(row);

    var layout = spt.table.get_layout();
    var content = layout.getElement(".spt_table_content");
    var rows = content.getElements(".spt_table_row_item");

    var items = [];

    for (var i = 0; i < ranges.length; i++) {

        var gantt_item = ranges[i].getParent(".spt_gantt_row_item");

        // find index of this item
        var index = 0;
        var child = gantt_item;
        while ( (child = child.previousSibling) != null)
            index++;

        //var index = gantt_item.rowIndex;

        var item = rows[index];
        if (!item) {

        }

        //var search_key = item.getAttribute("spt_search_key");
        //var item = spt.table.get_row_by_search_key(search_key);

        spt.table.select_row(item);
        items.push(item);
    }

    return items;

}



spt.gantt.update_group = function(row) {
    var ranges = spt.gantt.get_ranges_in_group(row);

    var start_date = null;
    var end_date = null;
    for (var i = 0; i < ranges.length; i++) {

        //var info = spt.gantt.get_dates_by_size(ranges[i]);

        var info = {
            "start_date": ranges[i].getAttribute("spt_start_date"),
            "end_date": ranges[i].getAttribute("spt_end_date")
        }

        if (!start_date || info.start_date < start_date) {
            start_date = info.start_date;
        }
        if (!end_date || info.end_date > end_date) {
            end_date = info.end_date;
        }
    }

    if (start_date == null || end_date == null) {
        return;
    }

    spt.gantt.set_date(row, start_date, end_date);

    // update the nobs
    var nobs = row.getElements(".spt_nob_update");
    if (nobs.length != 0 && info.start_date && info.end_date) {
        nobs[0].innerHTML = moment(info.start_date).format("MMM DD");
        nobs[1].innerHTML = moment(info.end_date).format("MMM DD");
    }


}





spt.gantt.update_all_groups = function() {

    var top = spt.gantt.get_top();
    var group_rows = top.getElements(".spt_group_range_top");
    group_rows.reverse();

    for (var i = 0; i < group_rows.length; i++) {

        var group_row = group_rows[i];
        var range = group_row.getElement(".spt_group_range");
        //range.setStyle("box-shadow", "0px 0px 15px red");
        spt.gantt.update_group(range);
    }
}


spt.gantt.toggle_ghosts = function() {
    var top = spt.gantt.top;
    var ghosts = top.getElements(".spt_ref_range");
    var toggle = spt.gantt.get_info("toggle_ghost");
    var display = !toggle ? "inline-block" : "none";
    for (var i=0; i<ghosts.length; i++) {
        ghosts[i].setStyle("display", display);
    }
}

spt.gantt.toggle_info = function(key) {
    show = !spt.gantt.get_info(key);
    var update = {};
    update[key] = show;
    spt.gantt.set_info(update);
}
        '''








    def get_custom_wdg(self, sobject, items, start_date, end_date, group_level=0):

        search_key = sobject.get_search_key()

        item_div = DivWdg()
        item_div.add_attr("spt_search_key", search_key)
        item_div.add_class("spt_range_top")

        item_div.add_attr("SPT_ACCEPT_DROP", "spt_range_top")

        item_div.add_style("height: 21px")
        #item_div.add_style("margin-top: -1px")
        #item_div.add_style("width: %s" % self.width)
        item_div.add_style("width: 100%")
        item_div.add_style("position: relative")
        item_div.add_style("z-index: %s" % (100-self.range_index))
        self.range_index += 1

        item_div.add_style("border-style", "solid")
        item_div.add_style("border-width", "0px 1px 1px 1px")
        item_div.add_color("border-color", "#EEE")

        item_div.add_style("box-sizing: border-box")


        item_div.add_relay_behavior( {
            'type': 'click',
            'bvr_match_class': "spt_one_top",
            'cbjs_action': '''
            spt.notify.show_message("Clicked ...");
            bvr.src_el.addClass("spt_selected");

            var top = bvr.src_el.getParent(".spt_gantt_top");
            var items = top.getElements(".spt_one_top");

            var start = false;
            var count = 0;
            for (var i = 0; i < items.length; i++) {
                if (items[i] == bvr.src_el) {
                    start = true;
                }
                if (!start) {
                    continue;
                }

                if (items[i].getStyle("display") != "none") {
                    items[i].setStyle("background", "#0B3");
                }
                count += 1;

                if (count > 10) {
                    break;
                }
            }

            '''
        } )


        item_div.add_behavior( {
            'type': 'mouseleaveX',
            'cbjs_action': '''

            var data = {};
            var ones = bvr.src_el.getElements(".spt_one_top");
            for (var i = 0; i < ones.length; i++) {
                var value = ones[i].getAttribute("spt_value");
                var key = ones[i].getAttribute("spt_key");

                try {
                    var value = parseInt(value);
                    if (isNaN(value)) value = 0;
                }
                catch(e) { value = 0; }

                if (value) {
                    data[key] = value;
                }
            }


            var search_key = bvr.src_el.getAttribute("spt_search_key");

            var layout = bvr.src_el.getParent(".spt_layout");
            spt.table.set_layout(layout);

            // this loops through every row
            var rows = layout.getElements(".spt_table_row");
            var row = null;
            for (var j = 0; j < rows.length; j++) {
                var row_search_key = rows[j].getAttribute("spt_search_key_v2");
                if (search_key == row_search_key) {
                    row = rows[j];
                    break;
                }
            }


            // NOTE: this doesn't work because of a bug that doesn't get the first loaded
            // rows due to embedded table
            //var row = spt.table.get_row_by_search_key(search_key);

            row.addClass("spt_row_changed");

            spt.table.add_extra_value(row, "data", data)


            '''
        } )



        item_div.add_relay_behavior( {
            'type': 'mouseenter',
            'bvr_match_class': 'spt_one_top',
            'cbjs_action': '''
            var el = bvr.src_el.getElement("input");
            el.value = "";
            el.focus();
            bvr.src_el.setStyle("border", "solid 1px #000");

            var top = bvr.src_el.getParent(".spt_timeline_top");
            if (!top) return;

            var pos = bvr.src_el.getPosition(top);
            var size = bvr.src_el.getSize();


            var div = document.createElement("div");
            top.appendChild(div);
            div = document.id(div);
            div.setStyle("position", "absolute");
            div.setStyle("width", size.x);
            div.setStyle("height", "100%");
            div.setStyle("left", pos.x );
            div.setStyle("top", 0);
            div.setStyle("opacity", "0.2");
            div.setStyle("background", "#C33");

            bvr.src_el.pos_el = div;


            '''
        } )


        item_div.add_relay_behavior( {
            'type': 'mouseleave',
            'bvr_match_class': 'spt_one_top',
            'cbjs_action': '''
            var el = bvr.src_el.getElement("input");
            var value_el = bvr.src_el.getElement(".spt_value");
            el.value = "";

            bvr.src_el.setStyle("border", "solid 1px transparent");

            var pos_el = bvr.src_el.pos_el;
            if (pos_el) {
               pos_el.destroy();
            }
            '''
        } )


        # editing
        item_div.add_relay_behavior( {
            'type': 'keyup',
            'bvr_match_class': 'spt_one_top',
            'cbjs_action': '''


            if (evt.code < 48 || evt.code > 57) {
                return;
            }

            var num_el = bvr.src_el.getElement("div");
            var input = bvr.src_el.getElement("input");

            num_el.innerHTML = input.value;
            bvr.src_el.setAttribute("spt_value", input.value);

            bvr.src_el.setStyle("background", "#C66");
            //bvr.src_el.setStyle("border", "solid 1px #666")
            '''

        } )



        start_date = dateutil.parser.parse(start_date)
        end_date = dateutil.parser.parse(end_date)


        column = "data"


        ones_data = sobject.get_json_value(column) or {}
        keys = ones_data.keys()
        keys.sort()

        # go through the entire visible reange
        #for i in range(0, 150):
        for key in keys:

            value = ones_data.get(key)
            if value == 0:
                continue

            o_start_date = parser.parse(key)
            o_end_date = o_start_date + timedelta(days=7)


            # for editing
            """
            value = 0
            for date_str, data_value in ones_data.items():
                date = dateutil.parser.parse(date_str)
                if date >= o_start_date and date < o_end_date:
                    value = data_value
                    break


            edit = False
            if not edit and value == 0:
                o_start_date = o_end_date + timedelta(days=0)
                o_end_date = o_start_date + timedelta(days=7)
                continue
            """



            outer = DivWdg()
            item_div.add(outer)


            outer.add_style("position: absolute")
            outer.add_style("display: inline-block")
            outer.add_style("box-sizing: border-box")


            outer.add_class("spt_gantt_element")
            outer.add_attr("spt_start_date", o_start_date)
            outer.add_attr("spt_end_date", o_end_date)

            #one_sobj = {}
            #value = one_sobj.get("value")
            #week = one_sobj.get("week")
            #color = one_sobj.get("color") # ???

            offset = self.get_percent(start_date, o_start_date)
            #if offset < 0:
            #    offset = 0

            width = self.get_percent(o_start_date, o_end_date)

            outer.add_style("top: 1px")
            outer.add_style("width: %s%%" % width)
            outer.add_style("left: %s%%" % offset)
            outer.add_style("height: 100%")


            one_div = DivWdg()
            outer.add(one_div)
            one_div.add_class("spt_one_top")
            one_div.add_style("box-sizing: border-box")
            one_div.add_style("vertical-align: middle")


            one_div.add_style("text-align: center")
            one_div.add_style("height: 25px")
            one_div.add_style("margin: 2px 0px")

            one_div.add_style("opacity: 0.8")

            value_div = DivWdg()
            value_div.add_class("spt_value")
            value_div.add_style("margin: 3px 0px")

            one_div.add(value_div)
            one_div.add_style("color: #FFF")
            one_div.add_style("border: solid 1px transparent")

            if value > 0:
                #one_div.add_style("border: solid 1px #666")
                one_div.add_style("background: #666")
                value_div.add(value)
            else:
                one_div.add_style("background: transpaarent")
                value_div.add(" ")

            o_start_date = o_end_date + timedelta(days=0)
            o_end_date = o_start_date + timedelta(days=7)

            one_div.add_class("hand")
            #one_div.add_class("tactic_hover")



            o_start_date_str = o_start_date.strftime("%Y-%m-%d")
            one_div.add('''
            <input type="number" style="margin-top: -100px"/>
            ''')
            one_div.add_style("overflow: hidden")

            one_div.add_attr("spt_key", "%s" % (o_start_date_str))
            one_div.add_attr("spt_value", value)




        return item_div



    def get_task_wdg(self, sobject, tasks, start_date, end_date, group_level=0, is_template=False):

        # handle if an item is a group

        if sobject.get_value("is_group", no_exception=True):

            group_level = sobject.get_value("group_level") or 0

            umb_color = "#111"

            group_sobjects = sobject.sobjects
            if group_sobjects:
                group_wdg = self.get_group_wdg(group_level, group_sobjects, start_date, end_date, umb_color)
                return group_wdg
            else:
                group_wdg = self.get_group_wdg(group_level, group_sobjects, start_date, end_date, umb_color)
                return group_wdg



        start_column = self.kwargs.get("start_column") or "bid_start_date"
        end_column = self.kwargs.get("end_column") or "bid_end_date"




        # First attempt at javascript creation of gantt
        if False and not is_template:
            bid_start_date = sobject.get_value(start_column)
            bid_end_date = sobject.get_value(end_column)

            item = DivWdg()
            item.add_behavior( {
                'type': 'load',
                'search_key': sobject.get_search_key(),
                'bid_start_date': bid_start_date,
                'bid_end_date': bid_end_date,
                'cbjs_action': '''
                setTimeout( function() {
                var gantt_top = bvr.src_el.getParent(".spt_gantt_top");
                spt.gantt.set_top(gantt_top);
                var row = spt.gantt.add_new_row(gantt_top, "task", bvr.search_key, "top");
                var range = row.getElement(".spt_range");
                if (range) {
                    //range.setStyle("background", "#F0F");
                    spt.gantt.set_date(range, bvr.bid_start_date, bvr.bid_end_date);
                }
                }, 1000);
                '''
            } )
            item.add_style("spt_group_level", group_level)
            return item






        from .gantt_task_item_wdg import GanttTaskRowWdg
        item = GanttTaskRowWdg(
            search_key=sobject.get_search_key(),
            task_keys=[x.get_search_key() for x in tasks],
            percent_per_day=self.percent_per_day,
            nobs_mode=self.nobs_mode,
            start_date=start_date,
            end_date=end_date,
            start_column=start_column,
            end_column=end_column,
            group_level=group_level,
            sobject=sobject,
            mode=self.kwargs.get("mode") or None,
            processes=self.kwargs.get("processes") or None
        )
        item.add_style("spt_group_level", group_level)


        return item





    def get_sobject_wdg(self, sobject, sobjects, start_date, end_date, group_level=0):

        search_key = sobject.get_search_key()

        item_div = DivWdg()
        item_div.add_attr("spt_search_key", search_key)
        item_div.add_class("spt_range_top")

        item_div.add_class("spt_gantt_row_item")

        item_div.add_attr("SPT_ACCEPT_DROP", "spt_range_top")

        item_div.add_style("height: 23px")
        #item_div.add_style("margin-top: -1px")
        #item_div.add_style("width: %s" % self.width)
        item_div.add_style("width: 100%")
        item_div.add_style("position: relative")
        item_div.add_style("z-index: %s" % (100-self.range_index))
        self.range_index += 1

        item_div.add_style("border-style", "solid")
        item_div.add_style("border-width", "0px 1px 1px 0px")
        item_div.add_color("border-color", "#EEE")
        item_div.add_color("box-sizing", "border-box")

        start_column = self.kwargs.get("start_column") or "bid_start_date"
        end_column = self.kwargs.get("end_column") or "bid_end_date"


        for i, sobject in enumerate(sobjects):

            sobject_key = sobject.get_search_key()

            bid_start_date = sobject.get_datetime_value(start_column)
            bid_end_date = sobject.get_datetime_value(end_column)


            top_margin = 4

            if not bid_start_date:
                today = datetime.today()
                bid_start_date = datetime(today.year, today.month, today.day)

            if not bid_end_date:
                bid_end_date = bid_start_date + timedelta(days=1)
                bid_end_date = datetime(bid_end_date.year, bid_end_date.month, bid_end_date.day)


            # set the time for full days
            snap_mode = "day"
            if snap_mode == "day":
                bid_start_date = SPTDate.strip_time(bid_start_date)
                bid_end_date = SPTDate.strip_time(bid_end_date) + timedelta(days=1) - timedelta(seconds=1)



            offset = self.get_percent(start_date, bid_start_date)
            width = self.get_percent(bid_start_date, bid_end_date)



            range_div = DivWdg()
            item_div.add(range_div)
            range_div.add_class("spt_range")
            range_div.add_class("spt_gantt_element")
            range_div.add_attr("spt_search_key", sobject_key)

            statuses = Task.get_status_colors().get("task")

            if self.search_type == "workflow/job":
                bg_color_map, text_color_map = self.get_color_maps("status")
                statuses = bg_color_map
            else:
                statuses = Task.get_status_colors().get("task")

            cbjs_action = '''
                var statuses = %s;

                if (bvr.src_el.hasClass("spt_changed")) {
                    var sobject = bvr.value;
                    var status = sobject["status"];
                    var background = statuses[status];
                    var nob_updates = bvr.src_el.getElements(".spt_nob");
                    bvr.src_el.setStyle("background", background);
                    nob_updates[0].setStyle("background", background);
                    nob_updates[1].setStyle("background", background);

                } else {
                    var sobject = bvr.value;
                    var start_date = sobject.start_date;
                    var due_date = sobject.due_date;
                    spt.gantt.set_date(bvr.src_el, start_date, due_date);
                    
                    var status = sobject["status"];
                    
                    var background = statuses[status];

                    var nob_updates = bvr.src_el.getElements(".spt_nob");
                    start_date = moment(start_date).format("MMM D");
                    due_date = moment(due_date).format("MMM D");
                    bvr.src_el.getElement("div").setStyle("background", background);
                    nob_updates[0].setStyle("background", background);
                    nob_updates[0].innerHTML = start_date;
                    nob_updates[1].setStyle("background", background);
                    nob_updates[1].innerHTML = due_date;
                }
                
            ''' % statuses

            range_div.add_update( {
                'search_key': sobject_key,
                'return': 'sobject',
                'cbjs_action': cbjs_action
            } )


            bid_start_date_str = bid_start_date.strftime("%Y-%m-%d %H:%M")
            bid_end_date_str = bid_end_date.strftime("%Y-%m-%d %H:%M")
            range_div.add_attr("spt_start_date", bid_start_date_str)
            range_div.add_attr("spt_end_date", bid_end_date_str)
            range_div.add_attr("spt_start_column", start_column)
            range_div.add_attr("spt_end_column", end_column)
            range_div.add_style("z-index: 10")


            days = (bid_end_date - bid_start_date).days + 1


            range_div.add_style("opacity: 0.8")

            # position the range
            range_div.add_style("position", "absolute")
            range_div.add_style("left: %s%%" % offset)




            sobject_type = sobject.get_value("timeline_type", no_exception=True) or ""
            if sobject_type == "milestone":

                color = "#EEE"

                description = sobject.get_value("description")
                if not description:
                    description = sobject.get_value("name")


                range_div.add_class("hand")
                range_div.add_attr("spt_range_type", "milestone")
                range_div.add_attr("spt_drag_mode", "move")

                milestone_wdg = self.get_milestone_wdg(sobject, color)
                range_div.add( milestone_wdg )
                milestone_wdg.add_style("pointer-events: none")

                range_div.add("<div style='font-weight: bold; height: 100%%; width: auto; max-width: 150px; text-overflow: ellipsis; white-space: nowrap; overflow: hidden; pointer-events: none; margin-top: -13px; margin-left: 25px; position: absolute;'>%s</div>" % description)
                range_div.add_style("margin-top: %spx" % top_margin)
                has_nobs = False

            else:
                has_nobs = True



                # draw the range shape
                border_color = range_div.get_color("border")



                start_display = bid_start_date.strftime("%b %d")
                end_display = bid_end_date.strftime("%b %d")

                range_div.add_style("font-size: 1.0em")

                border_color = "#999"
                color = "#EEE"
                height = 18
                status = sobject.get_sobject_dict().get("status") or None
                if status:
                    color = statuses[status]

                range_div.add_class("hand")
                range_div.add_style("margin-top: %spx" % top_margin)
                range_div.add_style("height: %spx" % height)


                range_div.add_style("border-style: solid")
                range_div.add_style("border-width: 1px")
                range_div.add_style("border-color: %s" % border_color)

                range_div.add_style("width: %s%%" % width)

                range_div.add_style("background: %s" % color)



                range_div.add_style("text-align: center")







                # TEST Layers of content


                # percent done
                range_content = DivWdg()
                range_div.add(range_content)
                range_content.add_style("width: 100%")
                range_content.add_style("pointer-events: none")
                range_content.add_style("position: absolute")
                range_content.add_style("top: 0px")
                range_content.add_style("left: 0px")
                range_content.add_style("font-size: 0.8em")
                range_content.add_style("color: #666")
                range_content.add_style("height: 100%")
                range_content.add_style("display: flex")



                mode = "completion"
                mode = "diff"


                if mode == "diff":

                    # diff
                    scenario_ref_code = sobject.get_value("scenario_ref_code", no_exception=True)
                    if not scenario_ref_code:
                        # new item
                        range_content.add_style("background", color)

                    else:
                        ref_sobject = Search.get_by_code(self.search_type, scenario_ref_code)
                        if not ref_sobject:
                            range_content.add_gradient("background", "#F00")

                        else:

                            ref_start_date = ref_sobject.get_datetime_value("bid_start_date")
                            ref_start_date = SPTDate.strip_time(ref_start_date)

                            ref_end_date = ref_sobject.get_datetime_value("bid_end_date")
                            ref_end_date = SPTDate.strip_time(ref_end_date) + timedelta(days=1) - timedelta(seconds=1)

                            ref_width = self.get_percent(ref_start_date, ref_end_date)
                            ref_offset = self.get_percent(start_date, ref_start_date)

                            ref_range = DivWdg()
                            item_div.add(ref_range)
                            ref_range.add_class("spt_range")
                            ref_range.add_class("spt_ref_range")
                            ref_range.add_style("position", "absolute")
                            ref_range.add_style("top", "4px")
                            ref_range.add_style("left", "%s%%" % ref_offset)
                            ref_range.add_style("width", "%s%%" % ref_width)
                            ref_range.add_style("height", "18px")
                            ref_range.add_style("background", "#e0ddff")
                            ref_range.add_style("border-radius", "10px")
                            ref_range.add_style("border", "1px solid #e0ddff")
                            ref_range.add_style("opacity", "0.5")
                            ref_range.add(" ")

                            ref_start_date_str = ref_start_date.strftime("%Y-%m-%d %H:%M")
                            ref_end_date_str = ref_end_date.strftime("%Y-%m-%d %H:%M")
                            ref_range.add_attr("spt_start_date", ref_start_date_str)
                            ref_range.add_attr("spt_end_date", ref_end_date_str)
                            ref_range.add_style("z-index: 9")




                            range_content.add_gradient("background", "#44F")



                else:
                    percent_done = 0
                    percent_todo = 100 - percent_done

                    range_done = DivWdg()
                    range_content.add(range_done)
                    #range_done.add_style("background: #0B0")
                    range_done.add_gradient("background", "#17A7E4", 20)
                    range_done.add_style("width: %s%%" % percent_done)
                    range_done.add_style("display: inline-block")
                    range_done.add_style("text-align: left")
                    range_done.add_style("vertical-align: middle")
                    range_done.add("&nbsp;%s%%" % percent_done)

                    range_todo = DivWdg()
                    range_content.add(range_todo)
                    range_todo.add_style("background: #9F9")
                    range_todo.add_gradient("background", "#17A7E4", 20, 50)
                    range_todo.add_style("width: %s%%" % percent_todo)
                    range_todo.add_style("display: inline-block")
                    range_todo.add_style("vertical-align: middle")
                    range_todo.add("&nbsp;")


                # title
                show_title = False
                if show_title:
                    range_content = DivWdg()
                    range_div.add(range_content)
                    range_content.add_style("width: 100%")
                    range_content.add_style("pointer-events: none")
                    range_content.add_style("position: absolute")
                    range_content.add_style("top: 0px")
                    range_content.add_style("left: 0px")
                    range_content.add(sobject.get_code() )


            # range detail


            detail_span = DivWdg()
            range_div.add(detail_span)
            detail_span.add_style("display: none")
            detail_span.add_class("spt_range_detail")
            detail_span.add_style("width: 200px")
            detail_span.add_style("min-width: 200px")
            detail_span.add_style("margin-top: 20px")
            detail_span.add_border()
            detail_span.add_style("padding: 5 10px")
            detail_span.add_style("z-index: 100")
            detail_span.add_style("background: #FFF")
            detail_span.add_style("position: absolute")
            detail_span.add_style("box-shadow: 0px 0px 15px rgba(0,0,0,0.4)")


            detail_span.add("<br clear='all'/>")
            detail_span.add("<br clear='all'/>")
            detail_span.add("Length: %s days" % days)
            detail_span.add("<br clear='all'/>")
            detail_span.add("<br clear='all'/>")
            detail_span.add("<br clear='all'/>")







            # add some nobs
            if self.nobs_mode != "none" and has_nobs:
                left = DivWdg()
                range_div.add(left)
                left.add_class("spt_nob")
                left.add_class("spt_nob_update")
                left.add_style("display: none")
                left.add_style("position: absolute")
                #left.add_style("width: 10px")
                left.add_style("height: 10px")
                left.add_style("border: solid 1px %s" % border_color)
                left.add_style("border-radius: 10px 0px 0px 10px")
                left.add_style("left: -33px")
                left.add_style("top: -1px")
                left.add_style("padding: 2px")
                left.add_style("background", color)
                left.add_style("opacity", 0.75)
                left.add(start_display)

                right = DivWdg()
                range_div.add(right)
                right.add_class("spt_nob")
                right.add_class("spt_nob_update")
                right.add_style("display: none")
                right.add_style("position: absolute")
                #right.add_style("width: 10px")
                right.add_style("height: 10px")
                right.add_style("border: solid 1px %s" % border_color)
                right.add_style("border-radius: 0px 10px 10px 0px")
                right.add_style("right: -33px")
                right.add_style("top: -1px")
                right.add_style("padding: 2px")
                right.add_style("background", color)
                right.add_style("opacity", 0.75)
                right.add(end_display)



        return item_div


