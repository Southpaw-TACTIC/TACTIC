// -------------------------------------------------------------------------------------------------------------------
//
//   Copyright (c) 2009, Southpaw Technology Inc., All Rights Reserved
//   
//   PROPRIETARY INFORMATION.  This software is proprietary to Southpaw Technology Inc., and is not to be
//   reproduced, transmitted, or disclosed in any way without written permission.
//   
// -------------------------------------------------------------------------------------------------------------------


spt.ui_play = {};


spt.ui_play.show_example = function( example_class_path )
{
    var ex_div = document.id("UiExampleDisplayDiv");

    // alert( example_class_path );

    var server = TacticServerStub.get();
    var kwargs = {'args': {}};
    var widget_html = server.get_widget( example_class_path, kwargs );

    spt.behavior.replace_inner_html( ex_div, widget_html );
}


spt.ui_play.test_handoff = function( evt, bvr, mouse_411 )
{
    var dst_el = document.id(bvr.dst_el);
    var src_el = document.id(bvr.src_el);

    alert( "Handed off behavior executed! Element '" + src_el.get('id') + "' got handed off bvr. Element '" +
           dst_el.get('id') + "' is dst_el for bvr!" );
}


spt.ui_play.named_event_fire_preprocess = function( event_name, bvr )
{
    spt.js_log.debug("*** Got named event '" + event_name + "', now in 'spt.ui_play.named_event_fire_preprocess()'.");

    // You can find out if there are actually any registered listeners, like so ...
    var has_listeners = spt.named_events.has_listeners( event_name );
    if( has_listeners ) {
        spt.js_log.debug("    ... AND it DOES have registered listeners.");
    } else {
        spt.js_log.debug("    ... but it has NO registered listeners.");
    }

    // NOTE: Must return true if you want listeners to run their call-backs ...
    return true;
}


spt.ui_play.named_event_fire_postprocess = function( event_name, bvr, listeners_executed_flag )
{
    // NOTE: this callback will know whether or not the listeners were run (as decided by the pre-process)
    //       ... here you can decide to do some activity if the were run vs. if they were not.
    //
    if( listeners_executed_flag ) {
        spt.js_log.debug("*** Listeners HAVE run for named event '" + event_name + "', now in " +
                            "'spt.ui_play.named_event_fire_postprocess()'.")
    } else {
        spt.js_log.debug("*** Listeners NOT run for named event '" + event_name + "', now in " +
                            "'spt.ui_play.named_event_fire_postprocess()'.")
    }
}


spt.ui_play.named_event_listen_cbk = function( event_name, firing_element, firing_data, listener_el, listener_options )
{
    var msg = "Got listener (with ID '" + listener_el.get('id') + "') call-back on named event '" + event_name +
                "' fired by element with ID '" + firing_element.get('id') + "'";
    alert( msg );
}


spt.ui_play.dom_event_self_fire_action = function( evt, bvr, mouse_411 )  // call back on mouse click
{
    var el = document.id(bvr.src_el);
    var options = bvr.options;
    var event_name = bvr.options.event_name;

    spt.js_log.debug( "*** Firing a 'DOM event' for 'dom_listen' type behaviors registered" );

    el.set('id', 'DOMEventFiringElement');

    // Fire an event in the DOM event system ... note that only the same element that fires this arbitrary event can
    // listen for this arbitrary event ... (i.e. you can't send a message to listeners that are different elements
    // than the firer element -- use the 'spt.named_events' mechanism through the 'listen' behavior type
    //
    el.fireEvent( event_name, [ el, event_name, "Welcome!" ] );
}


spt.ui_play.dom_listen_cbk = function( firing_el, event_name, text )
{
    var msg = "Got listener call-back on DOM event '" + event_name +
                "' fired by, and received by, element with ID '" + firing_el.get('id') + "', and received text '" +
                text + "'";
    alert( msg );
}


spt.ui_play.set_bg_to_next_basic_color = function( el_to_color )
{
    var el = document.id(el_to_color);
    var bg_color = el.getStyle("background-color");

    var next_clr_map = { 'red': 'blue', 'blue': 'green', 'green': 'yellow', 'yellow': 'orange', 'orange': 'red' }
    if( bg_color in next_clr_map ) {
        next_color = next_clr_map[ bg_color ];
    } else {
        next_color = 'red';
    }

    el.setStyle("background-color", next_color);
}


spt.ui_play.drag_cell_drop_action = function( evt, bvr )
{
    var tmp_html = bvr.orig_evt_target.innerHTML;
    bvr.orig_evt_target.innerHTML = bvr.drop_on_el.innerHTML;
    bvr.drop_on_el.innerHTML = tmp_html;

    bvr.orig_evt_target.setStyle("background","blue");
    bvr.drop_on_el.setStyle("background","blue");
}


spt.ui_play.header_half_setup = function( bvr )
{
    var hdr_el = bvr.src_el;
    var abs_off = spt.get_absolute_offset( hdr_el );

    if( ! bvr._move_info ) {
        bvr._move_info = {};
    }
    bvr._move_info.header_off_x = abs_off.x;
    bvr._move_info.header_off_y = abs_off.y;
    bvr._move_info.header_width = hdr_el.clientWidth;

    var red_bar = spt.dg_table.get_col_reorder_indicator('show', spt.get_el_real_cheight(hdr_el));
    bvr._move_info.active = true;
}


spt.ui_play.header_half_move_cbk = function( evt, bvr, mouse_411 )
{
    if( ! bvr._move_info || ! bvr._move_info.active ) {
        spt.ui_play.header_half_setup( bvr );
    }

    var red_bar = spt.dg_table.get_col_reorder_indicator();

    var hx = bvr._move_info.header_off_x;
    var hy = bvr._move_info.header_off_y;
    var hw = bvr._move_info.header_width;

    var cx = mouse_411.curr_x;

    var pos_x = hx;  // left side
    red_bar.setAttribute( "spt_col_reorder_pos", "LEFT" );
    if( (cx - hx) > parseInt( hw / 2 ) ) {
        // right side!
        pos_x = hx + hw;
        red_bar.setAttribute( "spt_col_reorder_pos", "RIGHT" );
    }
    var pos_y = hy;

    red_bar.setStyle( 'top', (pos_y + 'px') );
    red_bar.setStyle( 'left', (pos_x + 'px') );

    // red_bar.setStyle( 'top', (mouse_411.curr_y + 'px') );
    // red_bar.setStyle( 'left', (mouse_411.curr_x - 5 + 'px') );
}

spt.ui_play.header_half_move_off_cbk = function( evt, bvr, mouse_411 )
{
    var red_bar = spt.dg_table.get_col_reorder_indicator('hide');

    if( bvr._move_info && bvr._move_info.active ) {
        bvr._move_info.active = false;
    }
}



