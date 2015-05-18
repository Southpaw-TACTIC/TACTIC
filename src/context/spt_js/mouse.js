// -------------------------------------------------------------------------------------------------------------------
//
//   Copyright (c) 2008, Southpaw Technology Inc., All Rights Reserved
//   
//   PROPRIETARY INFORMATION.  This software is proprietary to Southpaw Technology Inc., and is not to be
//   reproduced, transmitted, or disclosed in any way without written permission.
//   
// -------------------------------------------------------------------------------------------------------------------


spt.mouse = {};


spt.mouse.get_mouse_btn = function( evt )
{
    var btn = evt.button;
    if( spt.browser.is_IE() ) {
        if( btn | 1 ) { btn = 0; }          // left mouse button mask is set
        else if( btn | 2 ) { btn = 1; }     // middle mouse button mask is set
        else if( btn | 4 ) { btn = 2; }     // right mouse button mask is set
    }

    return btn;
}


spt.mouse.get_modkeys_bitmask = function( evt )
{
    // SHIFT  CTRL  ALT  META
    //   1     2     4    8

    var bitmask = 0;
    if( evt.shift ) { bitmask = bitmask | 1; }
    if( evt.alt ) { bitmask = bitmask | 4; }

    // support for control modifier key, but use 'meta' on Mac OSX for control key ...
    if( spt.browser.os_is_MacOsx() ) {
        if( evt.meta) { bitmask = bitmask | 2; }
    }
    else {
        if( evt.control ) { bitmask = bitmask | 2; }
    }

    return bitmask;
}


spt.mouse.validate_input_for_action = function( evt_mouse_btn_num, evt_modkeys_bitmask, bvr )
{
    if( bvr.mouse_btn_num != evt_mouse_btn_num ) {
        
        return false;
    }
    if( bvr.modkeys_bitmask && (bvr.modkeys_bitmask != evt_modkeys_bitmask) ) {
        return false;
    }
    if( ! bvr.modkeys_bitmask && evt_modkeys_bitmask ) {
        return false;
    }
    return true;
}


spt.mouse._CB_wheel_action = function( evt )
{
    if( !evt ) { evt = window.event; }  // IE support

    // First find the "wheel" behavior target at the point where the wheel behavior occurred ...
    var bvr_type = "wheel";
    var target_el = spt.behavior.find_bvr_target(bvr_type, spt.get_event_target( evt ));

    if( ! target_el ) { return; }

    var bvrs = spt.mouse.find_behaviors( target_el );
    if( bvrs && (bvr_type in bvrs) ) {
        var bvr_list = bvrs[ bvr_type ];
        for( var b=0; b < bvr_list.length; b++ ) {
            var bvr = bvr_list[b];
            if( bvr.cbjs_action ) {
                spt.behavior.run_cbjs( bvr.cbjs_action, bvr, evt, null );
            }
            else if( bvr.cbfn_action ) {
                bvr.cbfn_action( evt, bvr );
            }
        }

        // stop the current wheel event since we've handled it ... don't want anything else to get it
        spt.halt_event_here( evt );
    }
}


spt.mouse.find_behaviors = function( start_el )
{
    var curr_el = start_el;

    while ( curr_el && !('spt_bvrs' in curr_el ) ) {
        curr_el = curr_el.parentNode;
    }
    if( curr_el ) {
        return curr_el.spt_bvrs;
    }
    return null;
}



// internal variables used for touch device support, used to help determine when to stop propagation
// of the touch device click ("tap") -- on iPad, for example, 'spt.halt_event_here(evt)' doesn't
// seem to work (event keeps going to cell tds behind pop-up)
//
spt.mouse._last_click_time = 0;
spt.mouse._click_time_tolerance = 100;



spt.mouse._click_core_action = function( evt, bvr_type )
{
    if( !evt ) { evt = window.event; }  // IE support

    // touch device support
    if( spt.browser.is_touch_device() ) {
        var this_click_time = (new Date()).getTime();
        if( (this_click_time - spt.mouse._last_click_time) < spt.mouse._click_time_tolerance ) {
            return;
        }
    }

    var target_el = spt.get_event_target( evt );

    // -- DISABLING FOR NOW -- Check for popup focus for this click ...
    // spt.popup._check_focus_by_target( target_el );

    target_el = spt.behavior.find_bvr_target( bvr_type, target_el )

    if( ! target_el ) { return; }


    var mouse_411 = {}
    var cursor_pos = spt.mouse.get_abs_cusor_position(evt);
    mouse_411.curr_x = evt.client.x + document.body.scrollLeft;
    mouse_411.curr_y = evt.client.y + document.body.scrollTop;


    var menu_activator_click_occurred = false;
    var bvrs = spt.mouse.find_behaviors( target_el );

    if( bvrs && (bvr_type in bvrs) )
    {
        var bvr_list_ok;
        if (bvr_type == 'double_click') {
            bvr_list_ok = bvrs[bvr_type];
        }
        else {
            bvr_list_ok = spt.mouse.get_input_validated_bvr_list( evt, bvrs[ bvr_type ] );
        }


        for( var b=0; b < bvr_list_ok.length; b++ )
        {
            var bvr = bvr_list_ok[b];
            if (typeof(bvr) == 'undefined') {
                continue;
            }

            if( bvr.disabled ) {
                continue;
            }

            if( bvr.activator_type && (bvr.activator_type == 'smart_menu' || bvr.activator_type == 'ctx_menu') ) {
                menu_activator_click_occurred = true;
            }

            spt.behavior.run_preaction_action_postaction( bvr, evt, mouse_411 );
        }

        // This comment: "DO NOT halt the event here or else TACTIC context menu doesn't go away properly!"
        // ... was here previously. Not sure if other things changed that now allow the event to be halted
        // here, but this seems to work now (it doesn't mess up the context menu), and halting the event
        // resolves some bugs related to a call-back from a single bvr being called multiple times
        //
        if( typeof(bvr) == 'undefined' || ! bvr.propagate_evt ) {
            spt.halt_event_here(evt);

            // touch device support
            if( spt.browser.is_touch_device() ) {
                spt.mouse._last_click_time = (new Date()).getTime();
            }
        }

        // use { 'propagate_evt' : True } in your bvr on the server side to allow the click to pass through
        // to other things
    }

    if( ! menu_activator_click_occurred ) {
        spt.ctx_menu.clear();
        spt.smenu.clear();
    }

    // -- COMMENT OUT fire a click off named event for now ...
    // spt.click_off.fire_click_off_cbk( evt );
}


spt.mouse._CB_click_action = function( evt )
{
    spt.mouse._click_core_action( evt, 'click' );
}


spt.mouse._CB_click_up_action = function( evt )
{
    spt.mouse._click_core_action( evt, 'click_up' );
}

spt.mouse._CB_double_click_action = function( evt )
{
    spt.mouse._click_core_action( evt, 'double_click' );
}



spt.mouse.get_input_validated_bvr_list = function( evt, bvr_list )
{
    if( ! bvr_list || bvr_list.length == 0 ) { return []; }

    var bvr_list_ok = [];

    var evt_mouse_btn_num = spt.mouse.get_mouse_btn( evt );
    var evt_modkeys_bitmask = spt.mouse.get_modkeys_bitmask( evt );
    for( var b=0; b < bvr_list.length; b++ )
    {
        var bvr = bvr_list[b];
        if( spt.mouse.validate_input_for_action( evt_mouse_btn_num, evt_modkeys_bitmask, bvr ) ) {
            bvr_list_ok.push( bvr );
        }
    }

    return bvr_list_ok;
}


spt.mouse.panning_scroll_setup = function( evt, bvr, mouse_411 )
{
    bvr.prev_client_x = evt.clientX;
    bvr.prev_client_y = evt.clientY;

    if( bvr.cbjs_setup ) {
        spt.behavior.run_cbjs( bvr.cbjs_setup, bvr, evt, mouse_411 );
    }
}


spt.mouse.panning_scroll_motion = function( evt, bvr, mouse_411 )
{
    var el_to_pan = bvr.src_el;
    var scrolling_el = null;

    // the drag_el or dst_el (or bvr.src_el if nothing is specified) is the element that is dragged and
    // moved around for panning ... the actual manipulation however is on the parent node of the panning
    // element ...
    //
    if( bvr.drag_el ) {
        scrolling_el = bvr.drag_el;
    } else if( bvr.dst_el ) {
        scrolling_el = bvr.dst_el;
    } else {
        scrolling_el = bvr.src_el;
    }

    scrolling_el = scrolling_el.parentNode;

    var etp_ch = el_to_pan.clientHeight;
    var etp_cw = el_to_pan.clientWidth;

    var dx = evt.clientX - bvr.prev_client_x;
    var dy = evt.clientY - bvr.prev_client_y;

    bvr.prev_client_x = evt.clientX;
    bvr.prev_client_y = evt.clientY;

    if( isNaN( dx ) || isNaN( dy ) ) {
        return;
    }

    var curr_scroll_top = scrolling_el.scrollTop;
    var new_scroll_top = curr_scroll_top - dy;
    if( ! (new_scroll_top < 0 || new_scroll_top > etp_ch) ) {
        scrolling_el.scrollTop = new_scroll_top;
    }

    var curr_scroll_left = scrolling_el.scrollLeft;
    var new_scroll_left = curr_scroll_left - dx;
    if( ! (new_scroll_left < 0 || new_scroll_left > etp_cw) ) {
        scrolling_el.scrollLeft = new_scroll_left;
    }

    if( bvr.cbjs_motion ) {
        spt.behavior.run_cbjs( bvr.cbjs_motion, bvr, evt, mouse_411 );
    }
}


spt.mouse.panning_scroll_action = function( evt, bvr, mouse_411 )
{
    if( bvr.cbjs_action ) {
        spt.behavior.run_cbjs( bvr.cbjs_action, bvr, evt, mouse_411 );
    }
}


spt.mouse.default_drag_setup = function( evt, bvr, mouse_411 )
{
     // log.debug( "spt.mouse.default_drag_setup()" );
}


spt.mouse.default_drag_motion = function( evt, bvr, mouse_411 )
{
    // move the element to the current mouse position, ajdusted as
    // necessary by the offset of the inital mouse-click
    //

    var new_x = mouse_411.curr_x - mouse_411.orig_offset_x;
    var new_y = mouse_411.curr_y - mouse_411.orig_offset_y;

    var drag_el = spt.behavior.get_element_to_drag( bvr );
    var offset = drag_el.getPosition();

    if( new_x > 0 ) {
        //drag_el.style.left = new_x + "px";
        offset.x = new_x;
    }
    if( new_y > 0 ) {
        //drag_el.style.top  = new_y + "px";
        offset.y = new_y;
    }

    var body = spt.mouse._get_body();
    var scroll_top = body.scrollTop;
    var scroll_left = body.scrollLeft;
    offset.y = offset.y - scroll_top;
    offset.x = offset.x - scroll_left;
    drag_el.position( { position: 'upperLeft', relativeTo: body, offset: offset } );

}


spt.mouse.default_drag_action = function( evt, bvr, mouse_411 )
{
     // log.debug( "spt.mouse.default_drag_action()" );
}


spt.mouse.get_abs_cusor_position = function( evt )
{
    var cursor_pos = { x: 0, y: 0 };

    // in IE, evt could be two different structures (not sure why) ... so need to deal with it
    // here ...

    if( ('client' in evt) && ('x' in evt.client) ) {
        if(!document.all) {
            cursor_pos.x = evt.page.x
            cursor_pos.y = evt.page.y
        }
        else {
            cursor_pos.x = evt.client.x + document.body.scrollLeft;
            cursor_pos.y = evt.client.y + document.body.scrollTop;
        }
    }
    else {
        // NOTE: This is the CORRECT CODE to use to get current mouse position on page that
        //       ALSO compensates for scrolled page ...
        //
        if(!document.all) {
            cursor_pos.x = evt.pageX;
            cursor_pos.y = evt.pageY;
        }
        else {
            cursor_pos.x = evt.clientX + document.body.scrollLeft;
            cursor_pos.y = evt.clientY + document.body.scrollTop;
        }
    }

    return cursor_pos;
}


spt.mouse._current_drag = {
    'default_move_time_tolerance': 0,
    'dragging': false,
    'bvr': null
};

spt.mouse.is_dragging = function()
{
    return spt.mouse._current_drag.dragging;
}

spt.mouse.get_drag_bvr = function()
{
    return spt.mouse._current_drag.bvr;
}


spt.mouse._CB_drag_setup = function( evt )
{
    if( !evt ) { evt = window.event; }

    // Used to bring popup forward when clicking on drag title bar ...
    spt.popup._check_focus_by_target( spt.get_event_target(evt) );

    // Need to make sure we clear any menus here!
    spt.ctx_menu.clear();
    spt.smenu.clear();

    // -- COMMENT OUT fire a click off named event for now ...
    // spt.click_off.fire_click_off_cbk( evt );


    // default is to use specified "src_el" as the draggable element
    // default is to use specified "dst_el" as the drop-on element
    //
    var target_el = spt.behavior.find_bvr_target('drag', spt.get_event_target( evt ));
    var orig_evt_target = spt.get_event_target( evt );

    // bail out if no validated 'SPT_BVR' behaviors are found
    //
    if( ! target_el.hasClass("SPT_BVR") ) {
        return;
    }

    var bvrs = spt.mouse.find_behaviors( target_el );
    if( bvrs && ('drag' in bvrs) )
    {
        var bvr_list_ok = spt.mouse.get_input_validated_bvr_list( evt, target_el.spt_bvrs['drag'] );

        if( ! bvr_list_ok || bvr_list_ok.length == 0 ) { return; } 
    }

    var bvr = null;

    if( bvr_list_ok.length == 1 ) {
        // Most drag behaviors will be set up with only one per element ...
        var bvr = bvr_list_ok[0];
        if( bvr.bvr_match_class ) {

            if( ! orig_evt_target.className ) {
                return;
            }
            //if( ! orig_evt_target.className.contains_word( bvr.bvr_match_class ) ) {
            if( ! spt.has_class( orig_evt_target, bvr.bvr_match_class ) ) {
                return;
            }
            bvr.orig_evt_target = orig_evt_target;
        }
    }
    else {
        // If there are more than 1 drag behaviors found on the bvr target then assume that there are overloaded
        // drag behaviors for efficiency ... in this case each of the drag behaviors MUST have a 'bvr_match_class'
        // to determine which one actually gets set into motion based on the original event target hit ...
        for( var c=0; c < bvr_list_ok.length; c++ ) {
            var tmp_bvr = bvr_list_ok[c];
            if( tmp_bvr.bvr_match_class && orig_evt_target.hasClass( tmp_bvr.bvr_match_class ) ) {
                bvr = tmp_bvr;
                bvr.orig_evt_target = orig_evt_target;
                break;
            }
        }
    }

    if( ! bvr ) {
        return;
    }

    if( bvr.disabled ) {
        return;
    }

    // Compute the distance between the upper-left corner of the element and the mouse-click.
    // The moveHandler function below needs these values.
    //
    var cursor_pos = spt.mouse.get_abs_cusor_position(evt);
    var mouse_411 = {};
    mouse_411.last_x = cursor_pos.x;
    mouse_411.last_y = cursor_pos.y;

    mouse_411.curr_x = cursor_pos.x;
    mouse_411.curr_y = cursor_pos.y;

    var drag_el = spt.behavior.get_element_to_drag( bvr );

    // set up mouse position information ...
    var el_off = spt.get_absolute_offset( drag_el );
    mouse_411.orig_offset_x = cursor_pos.x - el_off.x;
    mouse_411.orig_offset_y = cursor_pos.y - el_off.y;

    mouse_411.dx = 0;
    mouse_411.dy = 0;


    /*
    if( spt.browser.is_touch_device() ) {
        spt.touch_ui.drag.current_drag_bvr = bvr;
        spt.touch_ui.drag.info = {
            'mouse_411': mouse_411
        };
        spt.app_busy.show( "Drag action on Touch Device ...",
                           "<br/>Please tap on the destination for this drag action",
                           {'use_for_touch_drag': true} );
        return;
    }
    */

    // set up tracking information for the current, in-progress drag behavior ...
    spt.mouse._current_drag.bvr = bvr;
    spt.mouse._current_drag.dragging = true;
    spt.mouse._current_drag.has_moved = false;
    spt.mouse._current_drag.start_time_ms = (new Date()).getTime();
    spt.mouse._current_drag.move_time_tolerance = spt.mouse._current_drag.default_move_time_tolerance;
    if( bvr.move_time_tolerance ) {
        spt.mouse._current_drag.move_time_tolerance = bvr.move_time_tolerance;
    }

    var defer_setup = false;

    if( bvr.cbfn_action_onnomotion || bvr.cbjs_action_onnomotion ) {
        // if there is "onnomotion" action specified then we defer setup ...
        defer_setup = true;
    }
    else {
        // otherwise, run 'setup' phase call-backs (default cbs are used if flag is set in bvr spec) ...
        if( bvr.use_default_cbs ) {
            spt.mouse.default_drag_setup( evt, bvr, mouse_411 );
        }
        else {
            spt.behavior.run_callback_fn( 'setup', evt, bvr, mouse_411 );
        }
    }

    // Register the event handlers that will respond to the mousemove events
    // and the mouseup event that follow this mousedown event.
    //
    if( document.addEventListener )  // DOM Level 2 Event Model
    {
        // Register capturing event handlers
        document.addEventListener( "mousemove", move_handler, true );
        document.addEventListener( "mouseup", up_handler, true );
    }
    else if( document.attachEvent )  // IE 5+ Event Model
    {
        // In the IE event model, we capture events by calling setCapture() on the element to capture them.
        drag_el.attachEvent( "onmousemove", move_handler );
        drag_el.attachEvent( "onmouseup", up_handler );
        drag_el.setCapture();
    }
    else  // IE 4 Event Model
    {
        // In IE 4 we can't use attachEvent(), so assign the event handlers directly after storing any
        // previously assigned handlers, so they can be restored. Note that this also relies on
        // event bubbling.
        var oldmovehandler = document.onmousemove;
        var olduphandler = document.onmouseup;

        document.onmousemove = move_handler;
        document.onmouseup = up_handler;
    }

    // We've handled this event. don't let anybody else see it
    spt.halt_event_here( evt );

    function move_handler(e)
    {
        if( !e ) { e = window.event; }      // ie Event Model

        if( ! spt.mouse._current_drag.has_moved ) {
            var time_ms = (new Date()).getTime();
            if( time_ms - spt.mouse._current_drag.start_time_ms < spt.mouse._current_drag.move_time_tolerance ) {
                return;
            }
            spt.mouse._current_drag.has_moved = true;
        }

        if( defer_setup ) {
            // Run 'setup' phase call-backs (default cbs are used if flag is set in bvr spec) ...
            if( bvr.use_default_cbs ) {
                spt.mouse.default_drag_setup( evt, bvr, mouse_411 );
            }
            else {
                spt.behavior.run_callback_fn( 'setup', evt, bvr, mouse_411 );
            }
            defer_setup = false;
            return;
        }

        var cursor_pos = spt.mouse.get_abs_cusor_position(e);
        mouse_411.curr_x = cursor_pos.x;
        mouse_411.curr_y = cursor_pos.y;

        if( bvr.use_default_cbs ) {
            spt.mouse.default_drag_motion( e, bvr, mouse_411 );
        }
        else {
            spt.behavior.run_callback_fn( 'motion', e, bvr, mouse_411 );
        }

        mouse_411.last_x = cursor_pos.x;
        mouse_411.last_y = cursor_pos.y;

        // COMMENTING OUT the following code as we need the 'onmousemove' event to be passed on to
        // other elements wanting access to mouse move (we do some visual indicators on mouse move now)
        /*
        // and don't let anyone else see this event.
        if( e.stopPropagation ) { e.stopPropagation(); }    // DOM Level 2
        else { e.cancelBubble = true; }     // ie
        */
    }

    function up_handler(e)
    {
        if( !e ) { e = window.event; }      // ie Event Model

        // unregister the capturing event handlers.
        if( document.removeEventListener )  // DOM Event Model
        {
            document.removeEventListener( "mouseup", up_handler, true );
            document.removeEventListener( "mousemove", move_handler, true );
        }
        else if( document.detachEvent )  // IE 5+ Event Model
        {
            drag_el.detachEvent( "onmouseup", up_handler );
            drag_el.detachEvent( "onmousemove", move_handler );
            drag_el.releaseCapture();
        }
        else    // IE 4 Event Model
        {
            document.onmouseup = olduphandler;
            document.onmousemove = oldmovehandler;
        }

        // First check to see if we have an overloaded 'drag' behavior, where a straight click executes a special
        // action call-back (specified using 'cbjs_action_onnomotion' or 'cbfn_action_onnomotion') if there has
        // been no dragging motion after mouse down ...
        //
        if( (bvr.cbfn_action_onnomotion || bvr.cbjs_action_onnomotion) && ! spt.mouse._current_drag.has_moved ) {
            if( bvr.cbjs_action_onnomotion ) {
                spt.behavior.run_cbjs( bvr.cbjs_action_onnomotion, bvr, e, mouse_411 );
            }
            else if( bvr.cbfn_action_onnomotion ) {
                bvr.cbfn_action_onnomotion( evt, bvr );
            }
        }
        else {
            if( bvr.use_default_cbs ) {
                spt.mouse.default_drag_action( e, bvr, mouse_411 );
            }
            else {
                spt.behavior.run_callback_fn( 'action', e, bvr, mouse_411 );
            }
        }

        if( bvr.orig_evt_target ) {
            bvr.orig_evt_target = null;
            delete bvr.orig_evt_target;
        }


        spt.mouse._current_drag.bvr = null;
        spt.mouse._current_drag.dragging = false;

        // And don't let the event propagate any further.
        if( e.stopPropagation ) { e.stopPropagation(); }    // DOM Level 2
        else { e.cancelBubble = true; }     // IE
    }

}   // end of method begin_drag()


spt.mouse.find_hover_target = function( start_el )
{
    var el = start_el;

    while( el )
    {
        if( el.spt_bvrs && ('hover' in el.spt_bvrs) ) { return el; }
        el = el.parentNode;
    }
    return null;
}


spt.mouse._hover_mod_styles = function( hover_el, hover_bvr, drag_drop_codes )
{
    if( drag_drop_codes ) {
        if( ! spt.mouse.is_dragging() ) {
            return;
        }
        var drop_code = spt.mouse.get_drag_bvr().drop_code;
        if( ! drag_drop_codes.contains_word( drop_code ) ) {
            return;
        }
    }

    hover_bvr._styles_to_restore = spt.css.get_style_bkups( hover_bvr.mod_styles, hover_el );
    spt.css.apply_style_mods( hover_bvr.mod_styles, hover_el );
}


spt.mouse._hover_restore_styles = function( hover_el, hover_bvr )
{
    spt.css.apply_style_mods( hover_bvr._styles_to_restore, hover_el );
    delete hover_bvr._styles_to_restore;
}


spt.mouse._hover_add_looks = function( hover_el, hover_bvr, drag_drop_codes )
{
    hover_bvr._looks_added = [];
    if( drag_drop_codes ) {
        if( ! spt.mouse.is_dragging() ) {
            return;
        }
        var drop_code = spt.mouse.get_drag_bvr().drop_code;
        if( ! drag_drop_codes.contains_word( drop_code ) ) {
            return;
        }
    }

    // check for look suffix ...
    if( hover_bvr.add_look_suffix ) {
        var look_suffix = hover_bvr.add_look_suffix;
        var target_look_order = hover_bvr.target_look_order;

        for( var c=0; c < target_look_order.length; c++ ) {
            var look_cls = "look_" + target_look_order[c];
            if( hover_bvr.src_el.hasClass(look_cls) ) {
                hover_bvr.src_el.addClass( look_cls + "_" + look_suffix );
                break;
            }
        }
    }
    else if( hover_bvr.add_looks ) {
        // otherwise just execute add looks ...
        hover_bvr._looks_added = spt.css.add_looks( hover_bvr.add_looks, hover_el );
    }
}


spt.mouse._hover_remove_looks = function( hover_el, hover_bvr )
{
    // check for look suffixes to remove ...
    if( hover_bvr.add_look_suffix ) {
        var look_suffix = hover_bvr.add_look_suffix;
        var target_look_order = hover_bvr.target_look_order;
        for( var c=0; c < target_look_order.length; c++ ) {
            var look_cls = "look_" + target_look_order[c];
            if( hover_el.hasClass( look_cls + "_" + look_suffix ) ) {
                hover_el.removeClass( look_cls + "_" + look_suffix );
            }
        }
    }
    else if( hover_bvr.add_looks ) {
        // otherwise just execute removal of add looks ...
        spt.css.remove_looks( hover_bvr._looks_added, hover_el );
    }

    delete hover_bvr._looks_added;
}


spt.mouse._CB_hover_over = function( evt )
{
    if( !evt ) { evt = window.event; }

    var hover_el = spt.mouse.find_hover_target( spt.get_event_target( evt ) );
    if( !hover_el ) { return; }

    var hover_bvr_list = hover_el.spt_bvrs['hover'];
    if( hover_bvr_list ) {
        for( var i=0; i < hover_bvr_list.length; i++ ) {
            var hover_bvr = hover_bvr_list[i];

            // use 'disabled' property on bvr to dynamically disable and re-enable a hover behavior
            if( hover_bvr.disabled ) {
                continue;
            }

            var drag_drop_codes = null;
            if( hover_bvr.drag_drop_codes ) {
                drag_drop_codes = hover_bvr.drag_drop_codes;
            }

            // Add styles on over.  This is a list of ";" delimited styles
            if( hover_bvr.mod_styles ) {
                spt.mouse._hover_mod_styles( hover_el, hover_bvr, drag_drop_codes );
            }
            else if( hover_bvr.add_looks || hover_bvr.add_look_suffix ) {
                spt.mouse._hover_add_looks( hover_el, hover_bvr, drag_drop_codes );
            }
            else {
                spt.behavior.run_callback_fn( 'over', evt, hover_bvr, null );
            }

            if( hover_bvr.cbjs_action_over ) {
                if( drag_drop_codes ) {
                    if( ! spt.mouse.is_dragging() ) { continue; }
                    var drop_code = spt.mouse.get_drag_bvr().drop_code;
                    if( ! drag_drop_codes.contains_word( drop_code ) ) { continue; }
                }
                spt.behavior.run_cbjs( hover_bvr.cbjs_action_over, hover_bvr, evt, {} );
            }
        }
    }

    spt.behavior.propagate_hover_up( 'over', hover_el, evt );
}


spt.mouse._CB_hover_out = function( evt )
{
    if( !evt ) { evt = window.event; }

    var hover_el = spt.mouse.find_hover_target( spt.get_event_target( evt ) );
    if( !hover_el ) { return; }

    var hover_bvr_list = hover_el.spt_bvrs['hover'];
    if( hover_bvr_list ) {
        // process in reverse for restoring states ...
        for( var i = hover_bvr_list.length - 1; i >= 0; i-- ) {
            var hover_bvr = hover_bvr_list[i];

            // use 'disabled' property on bvr to dynamically disable and re-enable a hover behavior
            if( hover_bvr.disabled ) {
                continue;
            }

            if( hover_bvr.mod_styles ) {
                spt.mouse._hover_restore_styles( hover_el, hover_bvr );
            }
            else if( hover_bvr.add_looks || hover_bvr.add_look_suffix ) {
                spt.mouse._hover_remove_looks( hover_el, hover_bvr );
            }
            else {
                spt.behavior.run_callback_fn( 'out', evt, hover_bvr, null );
            }

            if( hover_bvr.cbjs_action_out ) {
                spt.behavior.run_cbjs( hover_bvr.cbjs_action_out, hover_bvr, evt, {} );
            }
        }
    }

    spt.behavior.propagate_hover_up( 'out', hover_el, evt );
}


// -------------------------------------------------------------------------------------------------------------------
//
//   Default 'hover' behavior call-backs - used for highlighting, by adding a class on hover, a given element or for
//   highlighting ancestor elements when you move your mouse within any descendent element ... e.g. highlight a row
//   if you hover over a TD or div within a TD in that row.
//
//   IMPORTANT: To use this properly you must specify two classes the element to hover over, where the first class is
//              assigned in the element tag in the HTML, and the second class is the highlight style when hovering
//              over the element. The second class name MUST be the name of the first class with a "_hover" suffix
//              appended to it, for example:
//
//                  TR.datagrid_row {
//                      background: #444444;
//                  }
//
//                  TR.datagrid_row_hover {
//                      background: #777777;
//                  }
//
//             Also, if your element can have a "selected state" (e.g. selected rows in table) then you need to
//             use a class to specify the selected state, and another class to specify the hover style of the
//             selected state, like so:
//
//                  TR.datagrid_row_selected {
//                      background: #004400;
//                  }
//
//                  TR.datagrid_row_selected_hover {
//                      background: #007700;
//                  }
//
//
// -------------------------------------------------------------------------------------------------------------------
spt.mouse.default_add_class_on_hover_over = function( evt, bvr, _ignore_ )
{
    var el = $(spt.get_event_target(evt));
    var hover_class = bvr.hover_class;  // hover class-name should always have "_hover" suffix
    if( hover_class ) {
        var class_to_find = hover_class.replace( /_hover/, '' );
        var class_selected = class_to_find +  '_selected';
        var hover_el = null;
        if( spt.has_class( el, class_to_find ) ) { hover_el = el; }
        else { hover_el = el.getParent("."+class_to_find); }
        if( hover_el ) {
            if( spt.has_class( hover_el, class_selected ) ) {
                hover_class = class_to_find + '_selected_hover';
            }
            spt.add_class( hover_el, hover_class );
        }
    }
}


spt.mouse.default_add_class_on_hover_out = function( evt, bvr, _ignore_ )
{
    var el = spt.get_event_target(evt);

    var hover_class = bvr.hover_class;  // hover class-name should always have "_hover" suffix
    if( hover_class ) {
        var class_to_find = hover_class.replace( /_hover/, '' );
        var class_selected_hover = class_to_find +  '_selected_hover';
        var hover_el = null;
        if( spt.has_class( el, class_to_find ) ) { hover_el = el; }
        else { hover_el = el.getParent("."+class_to_find); }
        if( hover_el ) {
            spt.remove_class( hover_el, hover_class );
            spt.remove_class( hover_el, class_selected_hover );
        }
    }
}


// This replaces the default behavior for the TableLayoutWdg
spt.mouse.table_layout_hover_over = function( evt, bvr, _ignore_) {
    var el = spt.get_event_target(evt);

    var hover_el;
    if (typeof(bvr.hover_class) != 'undefined') {
        hover_el = el.getParent("."+bvr.hover_class);
    }
    else {
        hover_el = bvr.src_el;
    }

    // check over
    var state = hover_el.getAttribute("spt_hover_state");
    if (state == "over") {
        return;
    }
    hover_el.setAttribute("spt_hover_state", "over");

    if (!bvr.add_color_modifier) {
        bvr.add_color_modifier = -10;
    }

    // remember the current background color and store this color
    var background = hover_el.getStyle("background-color");
    hover_el.setAttribute("spt_background", background);

    var rgb = spt.css.get_color_rgb_values( background );
    var hsv = spt.css.rgb_to_hsv(rgb.r, rgb.g, rgb.b);
    var diff = 256 * bvr.add_color_modifier / 100;
    hsv.v = hsv.v + diff;
    var rgb = spt.css.hsv_to_rgb( hsv.h, hsv.s, hsv.v );
    var color = "rgb("+rgb.r+","+rgb.g+","+rgb.b+")";

    //hover_el.setStyle("border", "solid 1px "+color);
    hover_el.setStyle("background-color", color);
    //hover_el.setStyle("background", color);

}



spt.mouse.table_layout_hover_out = function( evt, bvr, _ignore_) {
    var el = spt.get_event_target(evt);
    var hover_el;
    if (typeof(bvr.hover_class) != 'undefined') {
        hover_el = el.getParent("."+bvr.hover_class);
    }
    else {
        hover_el = bvr.src_el;
    }


    var background = hover_el.getAttribute("spt_background");
    hover_el.setStyle("background-color", background);
    hover_el.setAttribute("spt_hover_state", "");

}



// -----------------------------------------------------------------------------
//
//   SMART click up mechanism ...
//
// -----------------------------------------------------------------------------

spt.mouse.smart_click_action = function( evt, bvr, mouse_411 ) {
    var src_el = bvr.src_el;
    var target_el = spt.get_event_target( evt );
    //target_el.setStyle("border", "solid 1px red");
    var match_class = bvr.bvr_match_class;
    if (! target_el.hasClass(match_class) ) {
        target_el = target_el.getParent("."+match_class);
    }

    if (target_el == null) {
        return;
    }


    // create a new bvr remapped to how the callback expects it
    var new_bvr = {
        'type': bvr.type,
        'cbjs_action': bvr.orig_cbjs_action,
        'src_el': target_el,
        'firing_el': bvr.src_el
    }

    //console.log(new_bvr.type);
    spt.behavior.run_cbjs( new_bvr.cbjs_action, new_bvr, evt, mouse_411 );

}


// TEST
spt.mouse.smart_hover_action = function( evt, bvr, mouse_411 ) {
    //console.log(bvr);
}



// -------------------------------------------------------------------------------------------------------------------
//
//   SMART drag mechanism ...
//
// -------------------------------------------------------------------------------------------------------------------

// bvr = { 'type': 'smart_drag',
//         'drag_el': @,
//         'use_copy': 'true', 
//         'use_delta': 'true',
//         'dx': 10,
//         'dy': 5,
//         'copy_styles': 'background-color: #ff6699; border: 1px dashed red; opacity: .45;',
//         'ignore_default_motion': 'false', 
//         'cbjs_setup': 'spt.my_test.do_drop_setup( evt, bvr );'
//         'cbjs_motion': 'spt.my_test.do_drop_motion( evt, bvr );'
//         'cbjs_action': 'spt.my_test.do_drop_action( evt, bvr );'
//         'cbjs_pre_action': 'spt.my_test.do_drop_pre_action( evt, bvr );'
//         'cbjs_post_action': 'spt.my_test.do_drop_post_action( evt, bvr );'
// };


spt.mouse._get_body = function() 
{ 
    if (typeof(spt.mouse.body) == 'undefined') { 
        spt.mouse.body = $(document.body); 
    } 
    return spt.mouse.body; 
 
} 


spt.mouse._create_drag_copy = function( el_to_copy, extra_styling )
{
    var pad_left = parseInt(el_to_copy.getStyle("padding-left"));
    var pad_right = parseInt(el_to_copy.getStyle("padding-right"));
    var pad_top = parseInt(el_to_copy.getStyle("padding-top"));
    var pad_bottom = parseInt(el_to_copy.getStyle("padding-bottom"));

    var copy = spt.behavior.duplicate_element(el_to_copy);
    
    //copy.inject(drag_copy, "bottom");

    var override_styles = "padding-left: " + pad_left + "px; padding-right: " + pad_right + "px; " +
                          "padding-top: " + pad_top + "px; padding-bottom: " + pad_bottom + "px;";

    spt.css.copy_styles( el_to_copy, copy, override_styles );

    // apply any extra styles (extra_styling is a CSS string) ...
    if (extra_styling) {
        var style_map = spt.get_style_map_from_str( extra_styling );

        for( var style in style_map ) {
            if( ! style_map.hasOwnProperty(style) ) { continue; }
            copy.setStyle( style, style_map[style] );
        }
    }

    copy.setStyle( "position", "absolute" );
    spt.show_block( copy );

    var global_container = $("global_container");
    copy.inject( global_container, "bottom" );
    return copy;
}


spt.mouse._delete_drag_copy = function( drag_copy_el )
{
    var parent_node = drag_copy_el.parentNode;
    parent_node.removeChild( drag_copy_el );
    delete drag_copy_el;
    drag_copy_el = null;
}


spt.mouse.smart_drag_setup = function( evt, bvr, mouse_411 )
{
    if( bvr.cbjs_setup) {
        spt.behavior.run_cbjs( bvr.cbjs_setup, bvr, evt, mouse_411 );
    }

    if( spt.browser.is_touch_device() ) {
        // On a touch device, run any pre_motion_setup here since motion callbacks won't occur
        if( bvr.cbjs_pre_motion_setup && ! bvr._pre_motion_setup_done ) {
            spt.behavior.run_cbjs( bvr.cbjs_pre_motion_setup, bvr, evt, mouse_411 );
            bvr._pre_motion_setup_done = true;
        }
    }
}


spt.mouse.smart_drag_motion = function( evt, bvr, mouse_411 )
{
    if( spt.is_FALSE( bvr.ignore_default_motion ) ) {
        spt.mouse._smart_default_drag_motion( evt, bvr, mouse_411 );
    }

    if( bvr.cbjs_motion ) {
        spt.behavior.run_cbjs( bvr.cbjs_motion, bvr, evt, mouse_411 );
    }
}


spt.mouse._smart_default_drag_motion = function( evt, bvr, mouse_411 )
{
    var drag_el = bvr.drag_el;
    if( ! drag_el ) {
        drag_el = spt.behavior.get_bvr_src( bvr );
    }
    if( bvr.cbjs_pre_motion_setup && ! bvr._pre_motion_setup_done ) {
        spt.behavior.run_cbjs( bvr.cbjs_pre_motion_setup, bvr, evt, mouse_411 );
        bvr._pre_motion_setup_done = true;
    }

    // determine if we are going to make a copy of an element to drag or just drag the "drag_el"
    if( spt.is_TRUE(bvr.use_copy) )
    {
        if( ! bvr._drag_copy_el )
        {
            var extra_styles = "";
            if( bvr.copy_styles ) { extra_styles = bvr.copy_styles; }

            bvr._drag_copy_el = spt.mouse._create_drag_copy( drag_el, extra_styles );
        }

        drag_el = bvr._drag_copy_el;
    }

    var offset = drag_el.getPosition();

    if( spt.is_TRUE(bvr.use_delta) )
    {
        var dx = 10;
        var dy = 10;

        if( 'dx' in bvr ) { dx = parseInt(bvr.dx); }
        if( 'dy' in bvr ) { dy = parseInt(bvr.dy); }


        // with off-set ...
        // Position the ghost div & compensate for scrolled page ...
        if( evt.pageX ) {
            //drag_el.setStyle( "left", evt.clientX + (evt.pageX - evt.clientX) + dx );
            offset.x = evt.clientX + (evt.pageX - evt.clientX) + dx;

        } else {
            //drag_el.setStyle( "left", evt.clientX + dx );
            offset.x = evt.clientX + dx
        }

        if( evt.pageY ) {
            //drag_el.setStyle( "top", evt.clientY + (evt.pageY - evt.clientY) + dy );
            offset.y = evt.clientY + (evt.pageY - evt.clientY) + dy;
        } else {
            //drag_el.setStyle( "top", evt.clientY + dy );
            offset.y = evt.clientY + dy;
        }
    }
    else
    {
        // without off-set ...

        // move the element to the current mouse position, ajdusted as
        // necessary by the offset of the inital mouse-click
        //

        var new_x = mouse_411.curr_x - mouse_411.orig_offset_x;
        var new_y = mouse_411.curr_y - mouse_411.orig_offset_y;

        if( new_x > 0 ) {
            drag_el.setStyle( "left", new_x );
            offset.x = new_x;
        }
        if( new_y > 0 ) {
            drag_el.setStyle( "top", new_y );
            offset.y = new_y;
        }
    }


    var body = spt.mouse._get_body(); 
    var scroll_top = body.scrollTop; 
    var scroll_left = body.scrollLeft; 
    offset.y = offset.y - scroll_top; 
    offset.x = offset.x - scroll_left; 
    drag_el.position( { position: 'upperLeft', relativeTo: body, offset: offset } ); 

    if( spt.is_hidden( drag_el ) ) {
        spt.show_block( drag_el );
    }
}

spt.mouse.check_parent = function(target_el, drop_code)
{
     var max = 4;
     var i = 0;
     while( target_el && i < max) {
        if( !('getAttribute' in target_el) ) {
            break;
        }
        accept_drop = target_el.getAttribute("SPT_ACCEPT_DROP");
        if( accept_drop == drop_code ) {
            return target_el;
            break;
        }
        i += 1;
        target_el = target_el.parentNode;
    }
    return false
}

spt.mouse.smart_drag_action = function( evt, bvr, mouse_411 )
{
    // First clean up copy, if copy was used ...
    if( bvr._drag_copy_el ) {

        spt.mouse._delete_drag_copy( bvr._drag_copy_el );
        bvr._drag_copy_el = null;
    }

    // Reset any pre-motion setup that occurred ...
    if( bvr._pre_motion_setup_done ) {
        bvr._pre_motion_setup_done = false;
    }

    bvr.drop_accepted = false;

    // DETERMINE DROP_ON_EL ...
    //
    var target_el = spt.get_event_target(evt);
    var drop_on_el = null;
    var accept_drop = false;
    var drop_code = bvr.drop_code;

    if( !drop_code && bvr.cbjs_action) {
        // if no drop code is specified then run cbjs_action
        spt.behavior.run_cbjs( bvr.cbjs_action, bvr, evt, mouse_411 );
        return;
    }




    // if the immediate target element is not the element designated to accept a drop then go up
    // through parent nodes to see which element (if any) up the DOM heirarchy is supposed to
    // accept the drop ...
    //
    while( target_el ) {
        if( !('getAttribute' in target_el) ) {
            break;
        }
        accept_drop = target_el.getAttribute("SPT_ACCEPT_DROP");
        if( accept_drop && drop_code ) {
            if( spt.behavior.drop_accepted( bvr, target_el ) )
            {
                drop_on_el = $(target_el);
                break;
            }
        }
        target_el = target_el.parentNode;
    }

    if( ! drop_on_el ) {
        // Clean up temporary bvr params ...
        if( bvr.drop_on_el ) {
            bvr.drop_on_el = null;
            delete bvr.drop_on_el;
        }
        if( bvr.drop_accepted ) {
            delete bvr.drop_accepted;
        }
        return;
    }


    bvr.drop_on_el = drop_on_el;
    bvr.drop_accepted = true;

    if( bvr.cbjs_pre_action ) {
        spt.behavior.run_cbjs( bvr.cbjs_pre_action, bvr, evt, mouse_411 );
    }


    // First check to see if the drop-on-element has one or more "accept_drop" behaviors specified, and
    // if they match the given 'drop_code', then execute them (if any of these 'accept_drop' behaviors run
    // then they will override the 'cbjs_action' of the dragging element's smart drag behavior) ...
    //
    var accept_drop_bvrs_list = spt.behavior.get_bvrs_by_type( "accept_drop", drop_on_el );
    var accept_drop_bvrs_have_run = false;
    if( accept_drop_bvrs_list && accept_drop_bvrs_list.length ) {
        for( var c=0; c < accept_drop_bvrs_list.length; c++ ) {
            var accept_drop_bvr = accept_drop_bvrs_list[c];
            if( accept_drop_bvr.drop_code == drop_code ) {
                if( accept_drop_bvr.cbjs_action ) {
                    accept_drop_bvr._drop_source_bvr = bvr; 
                    spt.behavior.run_cbjs( accept_drop_bvr.cbjs_action, accept_drop_bvr, evt, mouse_411 );
                    accept_drop_bvrs_have_run = true;
                }
            }
        }
    }

    if( bvr.cbjs_action && ! accept_drop_bvrs_have_run ) {
        spt.behavior.run_cbjs( bvr.cbjs_action, bvr, evt, mouse_411 );
    }


    if( bvr.cbjs_post_action ) {
        spt.behavior.run_cbjs( bvr.cbjs_post_action, bvr, evt, mouse_411 );
    }

    // Clean up temporary bvr params ...
    bvr.drop_on_el = null;
    delete bvr.drop_on_el;
    delete bvr.drop_accepted;
}



// -------------------------------------------------------------------------------------------------------------------
//
//   MOVE (onmousemove) behavior support ...
//
// -------------------------------------------------------------------------------------------------------------------

spt.mouse._move_core = function( evt, move_phase )
{
    // move_phase parameter is one of:  'on', 'action' or 'off'

    var evt_target_el = spt.get_event_target( evt );
    var bvr_target_el = spt.behavior.find_bvr_target( "move", evt_target_el );

    if( ! bvr_target_el ) {
        return;
    }

    var mouse_411 = {};

    var cursor_pos = spt.mouse.get_abs_cusor_position(evt);
    // mouse_411.curr_x = cursor_pos.x;
    // mouse_411.curr_y = cursor_pos.y;

    mouse_411.curr_x = evt.client.x + document.body.scrollLeft;
    mouse_411.curr_y = evt.client.y + document.body.scrollTop;

    var bvrs = spt.mouse.find_behaviors( bvr_target_el );
    if( bvrs && ('move' in bvrs) )
    {
        var bvr_list = bvrs['move'];

        for( var b=0; b < bvr_list.length; b++ )
        {
            var bvr = bvr_list[b];
            if( bvr.disabled ) {
                continue;
            }

            if( bvr.drag_drop_codes ) {
                if( ! spt.mouse.is_dragging() ) {
                    continue;
                }
                var drop_code = spt.mouse.get_drag_bvr().drop_code;
                if( ! bvr.drag_drop_codes.contains_word( drop_code ) ) {
                    continue;
                }
            }

            if( move_phase == 'on' ) {
                if( bvr.cbjs_action_on ) {
                    spt.behavior.run_cbjs( bvr.cbjs_action_on, bvr, evt, mouse_411 );
                }
            }
            else if( move_phase == 'action' ) {
                spt.behavior.run_preaction_action_postaction( bvr, evt, mouse_411 );
            }
            else if( move_phase == 'off' ) {
                if( bvr.cbjs_action_off ) {
                    spt.behavior.run_cbjs( bvr.cbjs_action_off, bvr, evt, mouse_411 );
                }
            }
        }
    }
}

// for generic mouse events
spt.mouse._general_action = function( evt, move_phase )
{
    // move_phase parameter is one of:  'mouseenter', 'mouseleave' , 'mouseout, 'mouseover'

    var evt_target_el = spt.get_event_target( evt );
    var key = move_phase;

    var bvr_target_el = spt.behavior.find_bvr_target( key, evt_target_el );
    if( ! bvr_target_el ) {
        return;
    }

    var mouse_411 = {};

    var cursor_pos = spt.mouse.get_abs_cusor_position(evt);

    mouse_411.curr_x = evt.client.x + document.body.scrollLeft;
    mouse_411.curr_y = evt.client.y + document.body.scrollTop;

    var bvrs = spt.mouse.find_behaviors( bvr_target_el );
    if( bvrs  )
    {
        var bvr_list = bvrs[move_phase];

        for( var b=0; b < bvr_list.length; b++ )
        {
            var bvr = bvr_list[b];
            if( bvr.disabled ) {
                continue;
            }

            if( bvr.drag_drop_codes ) {
                if( ! spt.mouse.is_dragging() ) {
                    continue;
                }
                var drop_code = spt.mouse.get_drag_bvr().drop_code;
                if( ! bvr.drag_drop_codes.contains_word( drop_code ) ) {
                    continue;
                }
            }

            spt.behavior.run_preaction_action_postaction( bvr, evt, mouse_411 );
        }
    }
}

spt.mouse._CB_move_off = function( evt )
{
    spt.mouse._move_core( evt, 'off' );
}


spt.mouse._CB_move_on = function( evt )
{
    spt.mouse._move_core( evt, 'on' );
}


spt.mouse._CB_move = function( evt )
{
    spt.mouse._move_core( evt, 'action' );
}

// general callback. 
// Have a name arg here since name is not necessarily the same as evt.type like mouseleave vs mouseout
spt.mouse._CB = function( evt, name )
{
    spt.mouse._general_action( evt, name );
}


