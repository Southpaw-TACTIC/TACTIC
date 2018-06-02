// -------------------------------------------------------------------------------------------------------------------
//
//   Copyright (c) 2008, Southpaw Technology Inc., All Rights Reserved
//   
//   PROPRIETARY INFORMATION.  This software is proprietary to Southpaw Technology Inc., and is not to be
//   reproduced, transmitted, or disclosed in any way without written permission.
//   
// -------------------------------------------------------------------------------------------------------------------


// ---------------------------------------------------------------------
// Create container for "spt.behavior" ...
// ---------------------------------------------------------------------

spt.behavior = {};

// ----------------------------------------------------------------------------------------------------------------

spt.cb = {};

spt.cb.change_color_action = function( evt, bvr_params )
{
    var dst_el = bvr_params.dst_el;
    if( dst_el ) {
        var color = dst_el.style.backgroundColor;
        if( color == "rgb(0, 68, 0)" || color == "#004400" ) {
            dst_el.style.backgroundColor = "#000044";
        } else if( color == "rgb(0, 0, 68)" || color == "#000044" ) {
            dst_el.style.backgroundColor = "#440000";
        } else {
            dst_el.style.backgroundColor = "#004400";
        }
    }
}


spt.cb.title_text_action = function( evt, bvr_params )
{
    var src_el = bvr_params.src_el;
    if( src_el ) {
        src_el.innerHTML = "Hello Springfield!";
    }
}


spt.cb.test_alert = function( evt, bvr_params )
{
    alert("test")
}

// ----------------------------------------------------------------------------------------------------------------


spt.get_first_el_with_bvr_type_from_target = function( bvr_type, target_el )
{
    var el = target_el;
    while( el ) {
        var bvr_list = spt.behavior.get_bvrs_by_type( bvr_type, el );
        if( bvr_list.length ) {
            return el;
        }
        el = el.parentNode;
    }
    return null;
}


spt.behavior.get_bvrs_by_type = function( bvr_type, el )
{
    if( el.spt_bvrs && (bvr_type in el.spt_bvrs) ) {
        return el.spt_bvrs[ bvr_type ];
    }
    return [];
}


spt.behavior.find_bvr_target = function( bvr_type, start_el )
{
    var el = start_el;

    while( el )
    {
        if( el.spt_bvrs && (bvr_type in el.spt_bvrs) ) { return el; }
        el = el.parentNode;
    }
    return null;
}


spt.behavior.drop_accepted = function( drag_bvr, drop_on_el )
{
    // do not accept drop if drop-source is the same element as the drop-target!
    if( drag_bvr.src_el === drop_on_el ) {
        return false;
    }

    var dc = drag_bvr.drop_code;
    if( ! dc ) {
        // must have a drop code to match against, otherwise bail!
        spt.js_log.debug("*** 'drop_code' NOT found in drag behavior spec!");
        return false;
    }

    // look for the correct SPT_ACCEPT_DROP up through parents of the event target el ...
    var match_drop_code_regex = new RegExp( "\\b" + dc + "\\b" );
    while( drop_on_el ) {
        // use 'getAttribute' instead of 'getProperty' here because the latter is only available
        // on mootified elements, and event targets for drag-and-drop could be anything!
        if( 'getAttribute' in drop_on_el ) {
            // check for existence of 'getAttribute' first since event target could be 'document', which
            // does not have it
            var accept_drop_str = drop_on_el.getAttribute("SPT_ACCEPT_DROP");
            if( accept_drop_str && accept_drop_str.match( match_drop_code_regex ) ) {
                return true;
            }
        }
        drop_on_el = drop_on_el.parentNode;
    }
    return false;
}


spt.behavior._map_mouse_button = function( mbtn_code )
{
    var mbtn_map = { 'LMB': 0, 'MMB': 1, 'RMB': 2 };
    var btn = 0;
    if( mbtn_code in mbtn_map ) { btn = mbtn_map[ mbtn_code.toUpperCase() ]; }
    return btn;
}


spt.behavior._map_modkeys = function( modkeys_str )
{
    var mask_map = { "SHIFT": 1, "CTRL": 2, "ALT": 4, "META": 8 };

    var bitmask = 0;
    var ms = modkeys_str.toUpperCase();

    if( ms.indexOf("SHIFT") != -1 ) { bitmask = bitmask | mask_map["SHIFT"]; }
    if( ms.indexOf("CTRL") != -1 ) { bitmask = bitmask | mask_map["CTRL"]; }
    if( ms.indexOf("ALT") != -1 ) { bitmask = bitmask | mask_map["ALT"]; }
    if( ms.indexOf("META") != -1 ) { bitmask = bitmask | mask_map["META"]; }

    return bitmask;
}


spt.behavior.get_bvr_element = function( curr_el, el_ref )
{
    var el = null;

    if( typeof(el_ref) == "string" )
    {
        if( el_ref.match( /\@/ ) ) {
            // This handles previous '@' and '@.parentNode' spec and also new ones where you can use MooTools search
            // methods like '@.getElement(".SPT_CLASS_TAG")' ...
            curr_el = $(curr_el);
            var stmt = "el = " + el_ref.replace( /\@/g, "curr_el" );
            eval(stmt)
        }
        else if( el_ref.match( /\document\./ ) || el_ref.match( /\$/ ) ) {
            var stmt = "el = " + el_ref;
            eval(stmt)
        }
        else {
            // if we get here, then we assume that it is an element ID string
            el = $(el_ref);
        }
    }
    else {
        el = el_ref;
    }

    return el;
}


spt.behavior.get_bvr_element_list = function( curr_el, el_ref_list )
{
    var el_list = [];
    for( var i=0; i < el_ref_list.length; i++ ) {
        el_list.push( spt.behavior.get_bvr_element( curr_el, el_ref_list[i] ) );
    }
    return el_list;
}


// spt.behavior._get_kbd_callbacks = function( bvr )  ...
//
// Internal function to extract any keyboard override callbacks (for particular points in the keyboard processing
// mechanism) ... currently supported is: { "kbd_cbk_accept": <cb_as_string>, "kbd_cbk_cancel": <cb_as_string> }
//
// Example of behavior specification:  { "kbd_cbk_accept": "spt.dg_table.edit_cell_accept_cbk",
//                                       "kbd_cbk_cancel": "spt.dg_table.edit_cell_accept_cbk" }
//
// Callback functions for these must take in 2 arguments:  element, key_code
//
//    element is the HTML element that originates the key event
//    key_info is the key event information dictionary from the keyboard handling mechanism
//
spt.behavior._get_kbd_callbacks = function( bvr )
{
    var re = new RegExp( "kbd_cbk_" );
    var ret_arr = [ '{' ];
    for( name in bvr ) {
        if( ! bvr.hasOwnProperty(name) ) {
            continue;
        }
        if( name.indexOf("kbd_cbk_") == 0 ) {
            var label = name.replace( re, "" );
            ret_arr.push( '"' + label + '" : "' + bvr[name] + '"' );
            ret_arr.push( ', ' );
        }
    }
    if( ret_arr.length > 1 ) {
        ret_arr.pop();
    }
    ret_arr.push( '}' );
    return ret_arr.join('');
}


spt.behavior.hover_propagate = {};


spt.behavior.propagate_hover_up = function( hover_type, start_el, evt )
{
    var p_el = start_el.parentNode;
    spt.behavior.hover_propagate.state = 'running';   // this is 'running' or 'stopped'

    while( p_el ) {
        // Does it have behaviors?
        if( p_el.spt_bvrs ) {
            var hover_bvr_list = p_el.spt_bvrs['hover'];
            if( hover_bvr_list ) {
                for( var i=0; i < hover_bvr_list.length; i++ ) {
                    if( spt.behavior.hover_propagate.state == 'running' ) {
                        spt.behavior.run_callback_fn( hover_type, evt, hover_bvr_list[i], null );
                    }
                }
            }
        }
        p_el = p_el.parentNode;
    }
}


spt.behavior.run_cbjs = function( cbjs_str, bvr, evt, mouse_411 )
{


    cbjs_str = 'var run_bvr = function() { '+cbjs_str+' }';

    eval( cbjs_str );
   
    // basically disable js_logger for this because we loose the origin
    // of the error and chrome handles it really well now
    if (true || spt.behavior.mode == "dev") {        
        run_bvr();
    }
    else {
        try {
            run_bvr();
        } catch(e) {
            spt.js_log.error( "___________________________________________________________________________________________" );
            spt.js_log.error( "Caught javascript ERROR: " + e );
            spt.js_log.error( "  -- error occurred while running call-back javascript in spt.behavior.run_cbjs()" );
            spt.js_log.error( "..........................................................................................." );
            spt.js_log.error( " " );
            spt.js_log.error( cbjs_str );
            spt.js_log.error( " " );
            spt.js_log.error( "___________________________________________________________________________________________" );
            throw(e);
        }
    }
}

spt.behavior.set_mode = function(mode) {
   spt.behavior.mode = mode;
}


spt.behavior.run_callback_fn = function( cb_type, evt, bvr, mouse_411 )
{
    // cb_type is one of [ 'setup', 'motion', 'action', 'over', 'out' ]
    //
    // NOTE: 'over' and 'out' are for hover functions
    var fn_ran = false;

    // First see if there is a cbfn_setup, cbfn_motion, cbfn_action function override ... if it exists
    // then run it instead of any function found with the cb_set_prefix ...
    //
    var suffix = cb_type.toLowerCase();
    var stmt = "if( bvr.cbfn_" + suffix + " ) { " +
               "    bvr.cbfn_" + suffix + "( evt, bvr, mouse_411 ); " +
               "    fn_ran = true; " +
               "}";
    eval(stmt);

    if( fn_ran ) { return; }  // bail out now if we've run the override function above.

    // If no override, then see if a corresponding function exists based on cb_set_prefix prefix ...
    //
    if( bvr.cb_set_prefix )
    {
        var fn_name = bvr.cb_set_prefix + "_" + suffix;
        stmt = "if( " + fn_name + " ) {" +
               "    " + fn_name + "( evt, bvr, mouse_411 ); " +
               "}";
        eval(stmt);
    }
}


spt.behavior.run_preaction_action_postaction = function( bvr, evt, mouse_411 )
{
    if (bvr.bvr_repeat_interval) {
        if (bvr.bvr_repeat_key) {
            key = "SPT_BVR_REPEAT_"+bvr.bvr_repeat_key;
        }
        else {
            key = "SPT_BVR_REPEAT_"+bvr.type;
        }
        if (bvr.src_el.hasClass(key)) {
            return;
        }
        bvr.src_el.addClass(key);
        var opacity = bvr.src_el.getStyle("opacity");
        bvr.src_el.setStyle("opacity", "0.6");
        setTimeout( function() {
            bvr.src_el.removeClass(key);
            bvr.src_el.setStyle("opacity", opacity);
        }, bvr.bvr_repeat_interval*1000 );
    }


    // Pre-action call-back ...
    if( bvr.cbjs_preaction ) {
        spt.behavior.run_cbjs( bvr.cbjs_preaction, bvr, evt, mouse_411 );
    }
    else if( bvr.cbfn_preaction ) {
        bvr.cbfn_preaction( evt, bvr );
    }

    // Action call-back ...
    if( bvr.cbjs_action ) {
        spt.behavior.run_cbjs( bvr.cbjs_action, bvr, evt, mouse_411 );
    }
    else if( bvr.cbfn_action ) {
        bvr.cbfn_action( evt, bvr );
    }

    // Post-action call-back ...
    if( bvr.cbjs_postaction ) {
        spt.behavior.run_cbjs( bvr.cbjs_postaction, bvr, evt, mouse_411 );
    }
    else if( bvr.cbfn_postaction ) {
        bvr.cbfn_postaction( evt, bvr );
    }
}


spt.behavior.set_default_cbs = function( type, spec )
{
    // Right now we only do this for default hover ...
    //
    if( type == 'hover' ) {

        spec.cb_set_prefix = 'spt.mouse.default_add_class_on_hover';

        // -- Alternatively, could specify this with:  (NOTE: below doesn't work!)
        // -- ... currently Hover behavior operates only on the ".cb_set_prefix" mechanism
        //
        // spec.cbfn_over = spt.mouse.default_add_class_on_hover_over; 
        // spec.cbfn_out  = spt.mouse.default_add_class_on_hover_out;
    }
}


spt.behavior.construct_behaviors_on_startup = function()
{
    var el_list = document.getElements( ".SPT_BVR" );
    spt.behavior._construct_behaviors( el_list );
}



// Clone an element with full copying of behaviors
spt.behavior.clone = function( element ) {
    var element = document.id(element)
    var clone = element.clone();

    var clone_el_list = clone.getElements( ".SPT_BVR" );
    spt.behavior._construct_behaviors( [clone] );
    spt.behavior._construct_behaviors( clone_el_list );
    return clone;
}


// Duplicate an element, including all behaviors ...
//
// NOTE: this function should be used instead of the above 'spt.behavior.clone()', which causes bugs in IE
//       due to IE's idiosyncratic behavior with the underlying .cloneNode() method call
//
spt.behavior.duplicate_element = function( el )
{
    el = $(el);
    var tag = el.get("tag");
    var dup_el = new Element( tag );
    var inner_html_to_copy = el.get("html");

    // duplicate entire contents of element ...
    dup_el.set("html", inner_html_to_copy);

    // duplicate attributes of element node ...
    var attr_map = spt.get_el_attribute_map( el );
    for( var name in attr_map ) {
        if( ! attr_map.hasOwnProperty(name) ) { continue; }
        dup_el.setAttribute( name, attr_map[name] );
    }

    // duplicate styles of element node ...
    spt.css.copy_styles( el, dup_el );

    // duplicate className string of element node ...
    dup_el.className = el.className;

    // process behaviors of element node and its descendents ...
    var bvr_el_list = dup_el.getElements( ".SPT_BVR" );
    if( dup_el.hasClass("SPT_BVR") ) {
        bvr_el_list.push( dup_el );
    }
    spt.behavior._construct_behaviors( bvr_el_list );

    return dup_el;
}


spt.behavior.replace_table_child_element = function(el, new_inner_html)
{
    // get the parent of the element
    var parent_node = el.parentNode;

    if( ! parent_node ) {
        spt.js_log.error( "ERROR: NO parent_node found in 'spt.behavior.replace_table_child_element()' ... here is element:" );
        spt.js_log.error( el );
        return null;
    }

    // create a temporary table element
   
    // IE only likes full tables
    var tmp_table;
    if (spt.browser.is_IE()) {
        new_inner_html = "<table>" + new_inner_html + "</table>"; 
        var tmp_div = document.createElement("div");
        tmp_div.innerHTML = new_inner_html;

        tmp_table = tmp_div.firstChild;
    }
    else {
        tmp_table = document.createElement("table")
        tmp_table.innerHTML = new_inner_html;
    }


    var children = $(tmp_table).getChildren()
    var first_child = null;

    for( var c=0; c < children.length; c++ ) {
        if( children[c].nodeType == 1 ) {
            first_child = children[c];
            break;
        }
    }

    if( ! first_child ) {
        spt.js_log.error( "ERROR: NO first child found in temporary table element in " +
                   "'spt.behavior.replace_table_child_element()'" );
        // FIXME: previously the check was comparing against node type 3 and so it was always going into
        //        this block, but the code below didn't seem to do anything. This error stuff should
        //        be generalized ...
        var error = first_child.getAttribute("spt_error")
        if (error == "true") {
            el = $("error_container")
            $("error_popup").setStyle("display", "block")
        }
        return null;
    }

    // remove tbody from table and then toss the tmp table
    first_child = tmp_table.removeChild( first_child );
    delete tmp_table;

    first_child.inject(el, 'after');;

    el = parent_node.removeChild(el);
    delete el;

    spt.show( first_child );

    return first_child;
}




// Provide a destroy function which cleans up the behaviors before destroying
spt.behavior.destroy = function( el ) {
    return spt.behavior.destroy_element(el)
}


spt.behavior.destroy_element = function( el )
{
    // call any unload behaviors
    try {
        spt.behavior.process_unload_behaviors( el );
    }
    catch(e) {
        // if an exception is thrown
        spt.js_log.warning(e);
    }


    // First do any behavior clean up needed in the DOM under the given element ...
    spt.behavior.deactivate_children( el );

    // ... as well, as cleaning up behaviors on the element itself ...
    spt.behavior.deactivate( el );

    // Then remove the element from the DOM and destroy it ...
    if( ! spt.browser.is_IE() ) {
        el.innerHTML = "";
    }
    if( el.parentNode ) {
        el.parentNode.removeChild( el );
    }

    // Mark all children elements that want notification as being destroyed
    // This is for instances when an array is holding the object
    // and needs to know if it is destroyed or not.
    var children = el.getElements(".spt_notify_destroyed");
    for (var i = 0; i < children.length; i++) {
        var child = children[i];
        el.addClass("spt_destroyed");
    }

    el.destroy();
    el = null;
}


spt.behavior.deactivate_children = function( el )
{
    el = $(el);
    if( ! el ) { return; }

    // Go through and remove events, listeners and stored data for any behaviors previously created on descendant
    // elements of the given element (el) ...
    //
    var bvr_el_list = el.getElements( ".SPT_BVR" );

    for( var c = 0; c < bvr_el_list.length; c ++ )
    {
        var bvr_el = bvr_el_list[c];
        spt.behavior.deactivate( bvr_el );
    }

    // Go through and remove linked PUWs by finding the PUW stubs contained under 'el' ... 'el' should never be
    // a PUW stub itself!
    //
    var puw_stub_list = el.getElements( ".SPT_PUW_STUB" );

    for( var c = 0; c < puw_stub_list.length; c ++ )
    {
        var stub = puw_stub_list[c];
        var puw_el = stub.spt_puw_el;
        if (!puw_el) {
            continue;
        }

        spt.behavior.destroy_element( puw_el );
    }
}


spt.behavior.deactivate = function( bvr_el )
{

    if (typeof(bvr_el) == 'undefined' || bvr_el == null) {
        alert('bvr_el is null');
        return;
    }

    // remove any events that were added to the behavior element ...
    bvr_el.removeEvents();

    // clean up the spt_bvrs object that had been added to the behavior element ...
    if( 'spt_bvrs' in bvr_el ) {
        spt.delete_object_property( bvr_el, 'spt_bvrs' );
    }

    // finally, clean up any entries for this behavior element in the named events registry ...
    if( spt.named_events.element_is_registered( bvr_el ) ) {
        spt.named_events.purge_listener_element( bvr_el );
    }
}




// Replace the children of el with a new html snippet
// 'el' is the parent
spt.behavior.replace_inner_html = function( el, new_inner_html, mode )
{
    /*
    if ( el.getElement(".spt_has_changes") || el.getElement(".spt_value_changed") ) {
        if (!confirm("Changes will be lost.  Continue?") ) {
            throw("Changes aborted");
        }
    }
    */
    if( ! el ) {
        spt.js_log.warning( "WARNING: spt.behavior.replace_inner_html() called with a null element." );
        return;
    }

    if ( new_inner_html == null ) {
        return;
    }


    if (mode == undefined) {
        if ( new_inner_html.substring(0,6) == '<tbody' ) {
            mode = 'self';
        }
        else {
            mode = 'parent';
        }
    }


    try {
        spt.behavior.process_unload_behaviors( el );
    }
    catch(e) {
        // if an exception is thrown
        spt.js_log.warning(e);
    }


    // First do any clean up needed for the DOM under the given element, clearing events on SPT_BVR elements
    // below the given element (el) -- we do not want to deactivate behaviors on the element itself!
    spt.behavior.deactivate_children( el );

    if (mode == 'parent') {
        el.innerHTML = new_inner_html;
    }
    else {
        // this gets run if we are replacing a TBODY element in a table ...

        // First deactivate this tbody element, to make sure listeners are cleaned up, etc.
        spt.behavior.deactivate( el );

        // Then call special replace function to swap out old tbody for new tbody html ...
        el = spt.behavior.replace_table_child_element(el, new_inner_html);
        spt.behavior._construct_behaviors( [ el ] );
    }

    // now create new behaviors for new innerHTML under "el" element ...
    //
    var bvr_el_list = el.getElements( ".SPT_BVR" );
    spt.behavior._construct_behaviors( bvr_el_list );

    // Now run through all elements that need to have text selection disabled ...
    //
    spt.disable_text_selection_by_class( "SPT_DTS", el );  // SPT_DTS = "Disable Text Select"

    // Process any new Page Utility Widgets that have come through ...
    spt.puw.process_new( el );
}


spt.behavior.null_cbk = function( evt, bvr, mouse_411 )
{
    spt.js_log.warning("WARNING: 'spt.behavior.null_cbk()' called, with bvr of type '" + bvr.type + "' ... here is " +
                       "the bvr object (to click on if Firebug console is active):");
    spt.js_log.warning( bvr );
}


spt.behavior._handoff_bvr = function( el, bvr_spec )
{
    var handoff_el = spt.behavior.get_bvr_element( el, bvr_spec._handoff_ );
    if( ! handoff_el ) {
        spt.js_log.warning( "WARNING: spt.behavior._handoff_bvr() got a null handoff element." );
        return;
    }

    // Remove the '_handoff_' property from the behavior spec and then generate the behavior on
    // the handoff_el (instead of the originating 'el' element) now ...
    //
    delete bvr_spec._handoff_;
    if( spt.get_typeof( handoff_el ) == "array" ) {
        // if we find an array of elements, then hand off the behavior to each one in list ...
        for( var c=0; c < handoff_el.length; c++ ) {
            spt.behavior._construct_bvr( handoff_el[c], bvr_spec );
        }
    }
    else {
        // otherwise assume it is a single element found ...
        spt.behavior._construct_bvr( handoff_el, bvr_spec );
    }
}


spt.behavior._CB_change = function( evt )
{
    if( ! evt ) { evt = window.event; }

    var change_el = spt.behavior.find_bvr_target( "change", spt.get_event_target(evt) );
    if( 'change' in change_el.spt_bvrs ) {
        var oc_bvrs = change_el.spt_bvrs['change'];
        for( var c=0; c < oc_bvrs.length; c++ ) {
            var bvr = oc_bvrs[c];
            if( bvr ) {
                spt.behavior.run_preaction_action_postaction( bvr, evt, null );
            }
        }
    }
}

spt.behavior._CB_blur = function( evt )
{
    if( ! evt ) { evt = window.event; }

    var blur_el = spt.behavior.find_bvr_target( "blur", spt.get_event_target(evt) );
    if( 'blur' in blur_el.spt_bvrs ) {
        var oc_bvrs = blur_el.spt_bvrs['blur'];
        for( var c=0; c < oc_bvrs.length; c++ ) {
            var bvr = oc_bvrs[c];
            if( bvr ) {
                spt.behavior.run_preaction_action_postaction( bvr, evt, null );
            }
        }
    }
}


spt.behavior._CB_focus = function( evt )
{
    if( ! evt ) { evt = window.event; }

    var focus_el = spt.behavior.find_bvr_target( "focus", spt.get_event_target(evt) );
    if( 'focus' in focus_el.spt_bvrs ) {
        var oc_bvrs = focus_el.spt_bvrs['focus'];
        for( var c=0; c < oc_bvrs.length; c++ ) {
            var bvr = oc_bvrs[c];
            if( bvr ) {
                spt.behavior.run_preaction_action_postaction( bvr, evt, null );
            }
        }
    }
}



spt.behavior._CB_scroll = function( evt )
{
    if( ! evt ) { evt = window.event; }

    var scroll_el = spt.behavior.find_bvr_target( "scroll", spt.get_event_target(evt) );
    if( 'scroll' in scroll_el.spt_bvrs ) {
        var oc_bvrs = scroll_el.spt_bvrs['scroll'];
        for( var c=0; c < oc_bvrs.length; c++ ) {
            var bvr = oc_bvrs[c];
            if( bvr ) {
                spt.behavior.run_preaction_action_postaction( bvr, evt, null );
            }
        }
    }
}





spt.behavior._mark_bvr_event_registered = function( el, bvr_type )
{
    // NOTE: cannot use 'hasOwnProperty' on an HTML element object as it is not supported in IE, that same
    //       property is supported on all other javascript objects in all browsers

    // previously used el.hasOwnProperty here ...
    if( ! ('_bvr_event_register_' in el) ) {
        el[ '_bvr_event_register_' ] = {};
    }

    // previously used el._bvr_event_register_.hasOwnProperty here ...
    if( !(bvr_type in el._bvr_event_register_) ) {
        el._bvr_event_register_[ bvr_type ] = true;
    }
}


spt.behavior._bvr_event_is_registered = function( el, bvr_type )
{
    // previously used el.hasOwnProperty here ...
    if( ! ('_bvr_event_register_' in el) ) {
        return false;
    }

    // previously used el._bvr_event_register_.hasOwnProperty here ...
    if( bvr_type in el._bvr_event_register_ ) {
        return true;
    }

    return false;
}


spt.behavior._register_bvr_event = function( el, bvr )
{
    if( bvr.type == 'listen' ) {
        // default unique == false
        if (bvr['unique'] == true)
            spt.named_events._process_listener_bvr( bvr, true );
        else
            spt.named_events._process_listener_bvr( bvr );
    }
    else if( bvr.type == 'dom_listen' ) {
        // For now, we allow multiple addEvent calls for callbacks on the same DOM event type ...
        // (NOT sure if this could be problematic or not) ...
        //
        el.addEvent( bvr.event_name, bvr.cbfn_action );
    }
    else {
        // THE following behavior types must only have an event registered for it ONCE per element ...
        if( bvr.type == 'click_up' ) {
            if( ! spt.behavior._bvr_event_is_registered( el, bvr.type ) ) {
                el.addEvent( "click", spt.mouse._CB_click_up_action );
                spt.behavior._mark_bvr_event_registered( el, bvr.type );
            }
        }
        else if( bvr.type == 'click' ) {
            if( ! spt.behavior._bvr_event_is_registered( el, bvr.type ) ) {
                el.addEvent( "mousedown", spt.mouse._CB_click_action );
                spt.behavior._mark_bvr_event_registered( el, bvr.type );
            }
        }
        else if( bvr.type == 'wheel' ) {
            if( ! spt.behavior._bvr_event_is_registered( el, bvr.type ) ) {
                el.addEvent( "mousewheel", spt.mouse._CB_wheel_action );
                spt.behavior._mark_bvr_event_registered( el, bvr.type );
            }
        }
        /*
        else if( bvr.type == "mousedown") {
            console.log("mousedown");
            if( ! spt.behavior._bvr_event_is_registered( el, bvr.type ) ) {
                el.addEvent( "mousedown", spt.mouse._CB_click_action );
                spt.behavior._mark_bvr_event_registered( el, bvr.type );
            }
        }
        */
        else if( bvr.type == 'double_click' ) {
            if( ! spt.behavior._bvr_event_is_registered( el, bvr.type ) ) {
                el.addEvent( "dblclick", spt.mouse._CB_double_click_action );
                spt.behavior._mark_bvr_event_registered( el, bvr.type );
            }
        }
        else if( bvr.type == 'drag' ) {
            if( ! spt.behavior._bvr_event_is_registered( el, bvr.type ) ) {
                el.addEvent( "mousedown", spt.mouse._CB_drag_setup );
                spt.behavior._mark_bvr_event_registered( el, bvr.type );
            }
        }
        else if( bvr.type == 'hover' ) {
            if( ! spt.behavior._bvr_event_is_registered( el, bvr.type ) ) {
                el.addEvent( "mouseenter", spt.mouse._CB_hover_over );
                el.addEvent( "mouseleave", spt.mouse._CB_hover_out );
                spt.behavior._mark_bvr_event_registered( el, bvr.type );
            }
        }
        else if( bvr.type == 'move' ) {
            if( ! spt.behavior._bvr_event_is_registered( el, bvr.type ) ) {
                el.addEvent( "mouseover", spt.mouse._CB_move_on );
                el.addEvent( "mousemove", spt.mouse._CB_move );
                el.addEvent( "mouseout", spt.mouse._CB_move_off );
                spt.behavior._mark_bvr_event_registered( el, bvr.type );
            }
        }
        else if( bvr.type == 'change' ) {
            if( ! spt.behavior._bvr_event_is_registered( el, bvr.type ) ) {
                el.addEvent( "change", spt.behavior._CB_change );
                spt.behavior._mark_bvr_event_registered( el, bvr.type );
            }
        }
        else if( bvr.type == 'blur' ) {
            if( ! spt.behavior._bvr_event_is_registered( el, bvr.type ) ) {
                el.addEvent( "blur", spt.behavior._CB_blur );
                spt.behavior._mark_bvr_event_registered( el, bvr.type );
            }
        }
        else if( bvr.type == 'focus' ) {
            if( ! spt.behavior._bvr_event_is_registered( el, bvr.type ) ) {
                el.addEvent( "focus", spt.behavior._CB_focus );
                spt.behavior._mark_bvr_event_registered( el, bvr.type );
            }
        }
        else if( bvr.type == 'scroll' ) {
            if( ! spt.behavior._bvr_event_is_registered( el, bvr.type ) ) {
                el.addEvent( "scroll", spt.behavior._CB_scroll );
                spt.behavior._mark_bvr_event_registered( el, bvr.type );
            }
        }
 
        else if( ['mouseleave','mouseenter','mouseover','mouseout'].contains(bvr.type) ) {
            if( ! spt.behavior._bvr_event_is_registered( el, bvr.type ) ) {
                el.addEvent( bvr.type, function(e, name) {
                    spt.mouse._CB(e, bvr.type)} );
                spt.behavior._mark_bvr_event_registered( el, bvr.type );
            }
        }
        else if( ['keyup','keydown'].contains(bvr.type) ) {
            if( ! spt.behavior._bvr_event_is_registered( el, bvr.type ) ) {
                el.addEvent( bvr.type, function(evt) {
                    spt.behavior.run_preaction_action_postaction( bvr, evt)} );
                spt.behavior._mark_bvr_event_registered( el, bvr.type );
            }
        }
        else if( bvr.type == 'keyboard' ) {
            if( ! spt.behavior._bvr_event_is_registered( el, bvr.type ) )
            {
                // behavior of type 'keyboard' REQUIRES a param called 'kbd_handler_name' which is the name of the
                // class for the handler minus the 'spt.kbd.' prefix and minus the 'Handler' suffix ...
                //
                if( bvr.hasOwnProperty('kbd_handler_name') )
                {
                    // get any override keyboard callbacks from behavior specification ...
                    var cbks = spt.behavior._get_kbd_callbacks( bvr );
                    var stmt = 'var handler_obj = new spt.kbd.' + bvr.kbd_handler_name +
                               'Handler( el, ' + cbks + ', bvr );';
                    eval(stmt);
                }

                spt.behavior._mark_bvr_event_registered( el, bvr.type );
            }
        }
        else if(bvr.type != "load" && bvr.type != "unload") {
            log.critical("Behavior event ["+bvr.type+"] not recognized");
        }
    }
}


spt.behavior._construct_bvr = function( el, bvr_spec )
{
    var bvr = {};

    if( bvr_spec.hasOwnProperty('_handoff_') ) {
        spt.behavior._handoff_bvr( el, bvr_spec );
        return;
    }

    if( bvr_spec.type == 'panning_scroll' ) {
        bvr_spec.modkeys = 'ALT';
    }

    var got_cb_specification = false;
    var type = null;

    for( var name in bvr_spec )
    {
        if( bvr_spec.hasOwnProperty(name) && bvr_spec[name] ) {
            if( name == 'type' ) {
                type = bvr_spec[name];
                bvr[name] = bvr_spec[name];
            }
            else if( name == 'drop_code' && bvr_spec['type'] == 'accept_drop' ) {
                var spt_accept_drop = el.getProperty("SPT_ACCEPT_DROP");
                if( ! spt_accept_drop ) {
                    spt_accept_drop = bvr_spec[name];
                } else {
                    if( ! spt_accept_drop.contains_word( bvr_spec[name] ) ) {
                        spt_accept_drop = spt_accept_drop + ' ' + bvr_spec[name];
                    }
                }
                el.setProperty("SPT_ACCEPT_DROP", spt_accept_drop);
                bvr[name] = bvr_spec[name];
            }
            else if( name == 'mouse_btn' ) {
                bvr.mouse_btn_num = spt.behavior._map_mouse_button( bvr_spec[name] );
            }
            else if( name == 'modkeys' ) {
                bvr.modkeys_bitmask = spt.behavior._map_modkeys( bvr_spec[name] );
            }
            else if( name == 'mod_styles' ) {
                // this is for hover style modification automation ...
                bvr['mod_styles'] = spt.css.get_mod_styles_map( bvr_spec[name] );
            }
            else if( name.match( /_el$/ ) ) {
                bvr[name] = spt.behavior.get_bvr_element( el, bvr_spec[name] );
            }
            else if( name.match( /_el_list$/ ) ) {
                bvr[name] = spt.behavior.get_bvr_element_list( el, bvr_spec[name] );
            }
            else if( name == 'cb_set_prefix' ) {
                bvr[name] = bvr_spec[name];
                got_cb_specification = true;
            }
            else if( name == 'cb_inline' ) {
                spt.js_log.warning("WARNING: found 'cb_inline' param in bvr spec, for the following element ... ");
                spt.js_log.warning("         ('cb_inline' has been deprecated, use 'cbjs_action' instead)" );
                spt.js_log.warning(el);
            }
            else if( name.match( /^cbfn_/ ) ) {
                // These can be used as overrides ...
                // will take precedence over 'cb_set_prefix' functions
                if( typeof(bvr_spec[name]) == 'string' ) {
                    var new_name = name.replace("cbfn_", "cbjs_");
                    bvr[new_name] = bvr_spec[name] + "(evt, bvr, mouse_411)";
                    /*
                    var stmt = 'bvr[name] = ' + bvr_spec[name] + ';';
                    try { eval(stmt); }
                    catch(e) { bvr[name] = null; }

                    if( bvr[name] == null ) {
                        spt.js_log.warning("WARNING: cannot find function '" + bvr_spec[name] + "' for bvr spec " +
                                            "for property '" + name + "'");
                        bvr[name] = spt.behavior.null_cbk;
                    }
                    */
                } else {
                    bvr[name] = bvr_spec[name];
                }
                got_cb_specification = true;
            }
            else if( name == 'use_default_cbs' ) {
                if( "Yes YES yes 1 True TRUE true".match( new RegExp( "\\b" + bvr_spec[name] + "\\b" ) ) ) {
                    bvr[name] = true;
                } else {
                    bvr[name] = false;
                }
            }
            else if( name == 'cb_fire_named_event' ) {
                // Set up central named event firing callback for this behavior, since it specifies
                // a named event to fire ...
                bvr['cbfn_action'] = spt.named_events.fire_cbk;

                // also be sure that event name is added to the bvr object too ...
                bvr[name] = bvr_spec[name];
            }
            else {
                // this handles all other spec parameters, including 'cbjs_' params ...
                bvr[name] = bvr_spec[name];
            }
        }
    }

    // Sanity check ...
    if( ! type ) {
        var el_id = "-- NO id --";
        var el_tag = "-- NO tag? --";
        if( 'id' in el ) { el_id = el.id; }
        if( 'tagName' in el ) { el_tag = el.tagName; }
        spt.js_log.warning( "WARNING: No type specified on behavior spec on element with id='" + el_id + "' and " +
                            " tagName='" + el_tag + "' ... skipping this behavior." );
        return;
    }

    if( type == 'panning_scroll' ) {
        bvr['cbfn_setup'] = spt.mouse.panning_scroll_setup;
        bvr['cbfn_motion'] = spt.mouse.panning_scroll_motion;
        bvr['cbfn_action'] = spt.mouse.panning_scroll_action;
        bvr['type'] = 'drag';
        type = 'drag';
        got_cb_specification = true;
    }

    if( type == 'smart_drag' ) {
        bvr['cbfn_setup'] = spt.mouse.smart_drag_setup;
        bvr['cbfn_motion'] = spt.mouse.smart_drag_motion;
        bvr['cbfn_action'] = spt.mouse.smart_drag_action;
        bvr['type'] = 'drag';
        type = 'drag';
        got_cb_specification = true;
    }

    if( type == 'smart_click_up' ) {
        // remember the original action
        bvr.orig_cbjs_action = bvr.cbjs_action;
        bvr.cbjs_action = "spt.mouse.smart_click_action(evt, bvr, mouse_411)";
        bvr.type = 'click_up';
        type = 'click_up';
        got_cb_specification = true;
    }


    // FIXME: this doesn't actually work.  Not sure if a smart hover is
    // even possible
    if( type == 'smart_hover' ) {
        // remember the original action
        bvr.orig_cbjs_action = bvr.cbjs_action;
        bvr.cbjs_action = "spt.mouse.smart_hover_action(evt, bvr, mouse_411)";
        bvr.type = 'hover';
        type = 'hover';
        got_cb_specification = true;
    }


    if( ! bvr.hasOwnProperty('use_default_cbs') ) {
        bvr.use_default_cbs = false;
        if( ! got_cb_specification ) {
            bvr.use_default_cbs = true;  // if no cbs are specified then assume defaults!
            spt.behavior.set_default_cbs( type, bvr );
        }
    }

    // Always set "src_el" to the behavior-originating element ... unless 'override_src_el' is provided!
    if( 'override_src_el' in bvr_spec ) {
        bvr.src_el = bvr_spec.override_src_el;
    } else {
        bvr.src_el = el;
    }



    // Ensure that 'mouse_btn' defaults to "LMB", if not specified in bvr spec (only needed for mouse btn bvrs) ...
    var mouse_btn_bvr_types = { 'click': true, 'click_up': true, 'drag': true };
    if( (type in mouse_btn_bvr_types) && (! bvr.hasOwnProperty('mouse_btn')) ) {
        bvr.mouse_btn_num = spt.behavior._map_mouse_button( "LMB" );
    }

    if( type == 'load' ) {
        el.addClass( "SPT_BVR_LOAD_PENDING" );
    }


    if( type == 'unload' ) {
        el.addClass( "SPT_BVR_UNLOAD_PENDING" );
    }



    // NOW REGISTER THE EVENT for this bvr ...
    //
    spt.behavior._register_bvr_event( el, bvr );


    // NOW add the behavior map to the element's 'spt_bvrs' map of behavior lists ...
    //
    if( ! ('spt_bvrs' in el) ) {
        el.spt_bvrs = {};
    }

    // NOTE: in above 'if' block ... in IE, MooTools extended element objects do not have a 'hasOwnProperty'
    //       method, so you must use the ('property_name' in element) notation instead! Using 'hasOwnProperty'
    //       here (as we did before) is not a problem in other browsers.


    if( ! el.spt_bvrs.hasOwnProperty(type) ) {
        el.spt_bvrs[ type ] = [];
    }

    el.spt_bvrs[ type ].push( bvr );


}

spt.count = {};


spt.behavior._construct_behaviors = function( el_list )
{
    // Add "spt_bvrs" map of lists of behaviors (by type of behavior) ...
    //
    // TODO: 
    // var val_list = el.getAttribute("SPT_BVR_LIST");
    // if (!val_list)
    //      continue
    // var bvr_spec_list = spt.json_parse(val_list);
    spt.count = {};
    for( var i=0; i < el_list.length; i++ )
    {
        var el = $(el_list[i]);

        if (el.bvr_spec_list) {
            var bvr_spec_list = el.bvr_spec_list;
        }
        else {
            var stmt = 'var bvr_spec_list = ' + el.getAttribute("SPT_BVR_LIST") + ';';
            stmt = stmt.replace(/\&quot\;/g, '"');
            eval(stmt);

            // FIXME: this doesn't work with clones
            /*
            el.bvr_spec_list = bvr_spec_list;
            el.removeAttribute("SPT_BVR_LIST");
            el.removeAttribute("SPT_BVR_TYPE_LIST");
            */
        }

        if (bvr_spec_list == null) {
            continue;
        }

        for( var j=0; j < bvr_spec_list.length; j++ )
        {
            var bvr_spec = bvr_spec_list[j];
            spt.behavior._construct_bvr( el, bvr_spec )
        }

    }

    //console.log(spt.count);

    // Piggy-back the call to the handler for processing load behaviors here at the end of _construct_behaviors
    // so that we only need to include it in one place ...
    //
    spt.behavior.process_load_behaviors( el_list );
}


// ------------------------------------------------------------------------------------------------------------------
//
// spt.behavior.add()
//
//   This function provides the ability to add behaviors to an element directly in Javascript ... i.e. dynamic
//   client-side behavior construction!
//
//   Params ...
//
//       el ... the HTML element to add the behavior or behaviors to
//
//       bvr_in ... this can be either a single bvr_spec object, or an array of bvr_spec objects for behavior(s)
//                  to add to the given element
//
// ------------------------------------------------------------------------------------------------------------------
spt.behavior.add = function( el, bvr_in )
{
    bvr_spec_list = [];
    if( spt.get_typeof(bvr_in) == "array" ) {
        bvr_spec_list = bvr_in
    } else {
        bvr_spec_list = [ bvr_in ];
    }

    for( var c=0; c < bvr_spec_list.length; c++ ) {
        spt.behavior._construct_bvr( el, bvr_spec_list[c] );
    }
}


spt.behavior.process_load_behaviors = function( el_list )
{
    // Function callback signature for cbfn_action of 'load' type behaviors is this:
    //
    //    cbfn_action_function_cbk( el, bvr )
    //

    // var el_list = document.getElements( ".SPT_BVR_LOAD_PENDING" );

    for( var c = 0; c < el_list.length; c++ )
    {
        var el = el_list[c];
        if( ! el.hasClass("SPT_BVR_LOAD_PENDING") ) {
            continue;
        }

        // get list of 'load' behaviors for this element ...
        //
        if( typeof(el.spt_bvrs) != 'undefined' && 'load' in el.spt_bvrs ) {
            var load_bvrs = el.spt_bvrs['load'];
            for( var i=0; i < load_bvrs.length; i++ ) {
                var bvr = load_bvrs[i];

                if( bvr.cbjs_action ) {
                    cbjs_action = bvr.cbjs_action;
                    spt.behavior.run_cbjs( bvr.cbjs_action, bvr, null, null );
                }
                else if( 'cbfn_action' in bvr ) {
                    var cbfn = bvr['cbfn_action'];
                    if( typeof cbfn == 'function' ) {
                        cbfn( el, bvr );
                    } else if( typeof cbfn == 'string' ) {
                        var stmt = cbfn + '( el, bvr )';
                        eval( stmt );
                    }
                }
            }
        }

        // done with running the onload callbacks for this element so remove the class
        // from it ...
        el.removeClass( "SPT_BVR_LOAD_PENDING" );
    }
}



spt.behavior.process_unload_behaviors = function( top_el )
{
    // Function callback signature for cbfn_action of 'unload' type behaviors is this:
    //
    //    cbfn_action_function_cbk( el, bvr )
    //
    if (!top_el) {
        return;
    }

    var el_list = top_el.getElements( ".SPT_BVR_UNLOAD_PENDING" );

    for( var c = 0; c < el_list.length; c++ )
    {
        var el = el_list[c];

        // get list of 'load' behaviors for this element ...
        //
        if( typeof(el.spt_bvrs) != 'undefined' && 'unload' in el.spt_bvrs ) {
            var load_bvrs = el.spt_bvrs['unload'];
            for( var i=0; i < load_bvrs.length; i++ ) {
                var bvr = load_bvrs[i];

                if( bvr.cbjs_action ) {
                    spt.behavior.run_cbjs( bvr.cbjs_action, bvr, null, null );
                }
                else if( 'cbfn_action' in bvr ) {
                    var cbfn = bvr['cbfn_action'];
                    if( typeof cbfn == 'function' ) {
                        cbfn( el, bvr );
                    } else if( typeof cbfn == 'string' ) {
                        var stmt = cbfn + '( el, bvr )';
                        eval( stmt );
                    }
                }
            }
        }

        // done with running the unload callbacks for this element
        // so remove the class from it ...
        top_el.removeClass( "SPT_BVR_UNLOAD_PENDING" );
    }
}






spt.behavior.get_element_to_drag = function( bvr )
{
    var drag_el = null;
    if( bvr.hasOwnProperty("drag_el") ) {
        return bvr.drag_el;
    }

    return bvr.src_el;
}


spt.behavior.get_bvr_src = function( bvr )
{
    if( bvr.bvr_match_class ) {
        var match_class = bvr.bvr_match_class;
        var t = bvr.orig_evt_target;
        if( t.hasClass(match_class) ) {
            return t;
        }
        return t.getParent( "." + match_class );
    }

    return bvr.src_el;
}


// -- The following are functions for the dynamic enabling/disabling of behaviors ...

// NOTE: Currently the dynamic disabling/enabling of behaviors is supported only in 'hover', 'click' and 'click_up'
//       type behaviors
//
spt.behavior._enable_disable_by_type = function( bvr_type_list, el, mode )
{
    if( spt.get_typeof( bvr_type_list ) == "string" ) {
        bvr_type_list = [ bvr_type_list ];
    }

    for( var t=0; t < bvr_type_list.length; t++ ) {
        var bvr_type = bvr_type_list[t];
        var bvr_list = spt.behavior.get_bvrs_by_type( bvr_type, el )
        for( var c=0; c < bvr_list.length; c++ ) {
            var bvr = bvr_list[c];
            if( mode == 'enable' ) {
                bvr.disabled = false;
            } else {
                bvr.disabled = true;
            }
        }
    }
}


spt.behavior.disable_by_type = function( bvr_type_list, el )
{
    spt.behavior._enable_disable_by_type( bvr_type_list, el, 'disable' );
}


spt.behavior.enable_by_type = function( bvr_type_list, el )
{
    spt.behavior._enable_disable_by_type( bvr_type_list, el, 'enable' );
}


