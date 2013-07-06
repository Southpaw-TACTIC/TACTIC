// -----------------------------------------------------------------------------
//
//   Copyright (c) 2008, Southpaw Technology Inc., All Rights Reserved
//   
//   PROPRIETARY INFORMATION.  This software is proprietary to Southpaw Technology Inc., and is not to be
//   reproduced, transmitted, or disclosed in any way without written permission.
//   
// 
// -----------------------------------------------------------------------------

spt.gantt = {};


// Gantt chart functionality

//
// These are for moving the Calendar Gantt Widget dynamically.
//

spt.gantt.drag_data = {};

spt.gantt.ranges = [];

spt.gantt.start_date = null;
spt.gantt.end_date = null;
spt.gantt.start_offset = null;
spt.gantt.end_offset = null;

spt.gantt.drag_spacer = null;
spt.gantt.drag_duration = null;
spt.gantt.drag_start = null;
spt.gantt.drag_end = null;


spt.gantt.drag_start_x = null;
spt.gantt.orig_width = 1000;
spt.gantt.width = 1000;
spt.gantt.offset = 0;
spt.gantt.visible = 500;

spt.gantt.months = ['January','February','March','April','May','June','July','August','September','October','November','December']


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
    //for (var i=ranges.length-1; i>=0; i--)
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
        //var percent_diff = pixel_diff / 10;
        //
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
        gantt_data_wdg.setStyle("border", "solid 1px blue");

        // FIXME: Make this settable
        gantt_value[info.key] = {};
        var gantt_key_data = gantt_value[info.key];
        gantt_key_data['index'] = info.index;
        gantt_key_data['start_date'] = start_date_str;
        gantt_key_data['end_date'] = end_date_str;
        gantt_key_data['orig_start_date'] = data.orig_start_date;
        gantt_key_data['orig_end_date'] = data.orig_end_date;

        // some general data
        /*
        var gantt_data = gantt_value['__data__'];
        if (!gantt_data) {
            gantt_data = {};
            gantt_value['__data__'] = gantt_data;
        }
        gantt_data['width'] = spt.gantt.width;
        gantt_data['offset'] = spt.gantt.offset;
        gantt_data['start_date'] = info.range_start_date;
        gantt_data['end_date'] = info.range_end_date;
        */

        
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

    for (var i=0; i < spt.gantt.scroll_els.length; i++) {
        var scroll_el = spt.gantt.scroll_els[i];

        scroll_el.setStyle("margin-left", offset);
    }

}


spt.gantt.drag_scroll_action = function(evt, bvr, mouse_411)
{


    var diff = parseFloat(mouse_411.curr_x - spt.gantt.drag_start_x);
    var offset = spt.gantt.offset + diff;
    if (offset > 0) {
        offset = 0;
    }
    else if (offset < - spt.gantt.width + spt.gantt.visible) {
        offset = - spt.gantt.width + spt.gantt.visible;
    }



    /* This was an attempt at moving the month headers so they are in
     * view as much as possible.  However, it often causes the months
     * to disappear due to a calculation error somewhere
     * DISABLING
     
    var visible = spt.gantt.visible;
    var row_elements = spt.gantt.top_el.getElements(".spt_gantt_scalable");
    for (var j = 0; j < row_elements.length; j++) {
        var row_element = row_elements[j];

        var elements = row_element.getElements(".spt_gantt_date_range");
        for (var i = 0; i < elements.length; i++) {
            var element = elements[i];
            var pixels_start = parseInt( element.getAttribute("spt_gantt_pixels_start"));
            var pixels_end = parseInt( element.getAttribute("spt_gantt_pixels_end"));
            var width = (pixels_end - pixels_start);
            if (width < (visible/4)) {
                continue;
            }

            //console.log("pixels_start: " + pixels_start)
            //console.log("pixels_end: " + pixels_end)
            //console.log("offset: " + offset);
            //console.log("width: " + width);
            if (pixels_start + offset < 0) {
                var padding = -offset - pixels_start + 15;
                element.setStyle('text-align', 'left');
                var child = element.getChildren()[0];
                child.setStyle('text-align', 'left');
                child.setStyle('padding-left', padding);
            }
            else if (pixels_start+width/2 > -offset+visible ) {
                var padding = 15 + "px";
                var child = element.getChildren()[0];
                element.setStyle('text-align', 'left');
                child.setStyle('text-align', 'left');
                child.setStyle('padding-left', padding);
            }
        }
    }
    */


    spt.gantt.offset = offset;

    var table = spt.gantt.table;
    spt.gantt.set_data( table );


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
    if (pixel_per_day < 15) {
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





