// -------------------------------------------------------------------------------------------------------------------
//
//   Copyright (c) 2008, Southpaw Technology Inc., All Rights Reserved
//   
//   PROPRIETARY INFORMATION.  This software is proprietary to Southpaw Technology Inc., and is not to be
//   reproduced, transmitted, or disclosed in any way without written permission.
//   
// -------------------------------------------------------------------------------------------------------------------

// DEPRECATED: now inline in popup_wdg.py


spt.z_index = {};

spt.z_index.group_lists = {};


// based on "SPT_Z" class search-tag

spt.z_index.get_z_el = function( start_el )
{
    if( start_el.hasClass("SPT_Z") ) {
        return start_el;
    }

    return start_el.getElement(".SPT_Z");
}


spt.z_index.sort_z_grouping = function( z_start_str )
{
    var spt_z_list = document.getElements(".SPT_Z");

    var z_grp_list = [];
    for( var c=0; c < spt_z_list.length; c++ ) {
        var z_el = spt_z_list[c];
        var z_start_value = z_el.getProperty("spt_z_start");
        if( z_start_value == z_start_str ) {
            z_grp_list.push( z_el );
        }
    }

    var z_start_num = parseInt( z_start_str );

    var new_list = [];
    var numbered_list = [];
    var numbered_map = {};

    for( var c=0; c < z_grp_list.length; c++ )
    {
        var el = z_grp_list[c];
        var z_idx = parseInt( el.getStyle("z-index") );

        if( z_idx == z_start_num ) {
            new_list.push( el );
        } else {
            numbered_list.push( z_idx );
            numbered_map[ z_idx ] = el;
        }
    }

    var z_inc = z_start_num + 1;
    numbered_list.sort();

    for( var c=0; c < numbered_list.length; c++ ) {
        var el = numbered_map[ numbered_list[c] ];
        el.setStyle( "z-index", z_inc );
        z_inc ++;
    }

    for( var c=0; c < new_list.length; c++ ) {
        var el = new_list[c];
        el.setStyle( "z-index", z_inc );
        z_inc ++;
    }
}


spt.z_index.bring_forward_cbk = function( evt, bvr, mouse_411 )
{
    if( !evt ) { evt = window.event; }  // IE compat.
    spt.z_index.bring_forward( $(spt.get_event_target(evt)) );
}


spt.z_index.bring_forward = function( target )
{
    if( target && ! target.hasClass("SPT_Z") ) {
        target = target.getParent(".SPT_Z");
    }
    if( ! target ) { return; }

    var z_el = target;
    var z_start_str = "" + z_el.getProperty("spt_z_start");
    var z_start_num = parseInt( z_start_str );

    z_el.setStyle("z-index", z_start_num+99);

    spt.z_index.sort_z_grouping( z_start_str );
}


spt.popup = {};


spt.popup._get_popup_from_popup_el_or_id = function( popup_el_or_id, fn_name, suppress_errors )
{
    if( ! popup_el_or_id ) {
        if( ! suppress_errors ) {
            log.error( "ERROR in '" + fn_name + "' ... popup_el_or_id argument is null or empty" );
        }
        return null;
    }

    var popup = null;

    if( spt.get_typeof( popup_el_or_id ) == 'string' ) {
        popup = $(popup_el_or_id);
        if( ! popup ) {
            if( ! suppress_errors ) {
                log.error( "ERROR in '" + fn_name + "' ... NO popup found with ID '" + popup_el_or_id + "'" );
            }
            return null;
        }
    }
    else {
        popup = $(popup_el_or_id);
        if( ! popup ) {
            if( ! suppress_errors ) {
                log.error( "ERROR in '" + fn_name + "' ... could not obtain popup element from popup_el_or_id argument." );
            }
            return null;
        }
    }

    return popup
}


spt.popup.open = function( popup_el_or_id, use_safe_position )
{
    var popup = spt.popup._get_popup_from_popup_el_or_id( popup_el_or_id );
    if( ! popup ) { return; }

    spt.popup._position( popup, use_safe_position );
    spt.show( popup.getElement('.spt_popup_content') );

    spt.show( popup );

    // @@@
    var rsw_content_box = popup.getElement(".SPT_RSW_CONTENT_BOX");
    if( rsw_content_box ) {
        alert("WARNING: resize_scroll dependency");
        spt.resize_scroll.adjust_for_scroll( rsw_content_box );
    }

    spt.popup.get_focus( popup );
}


spt.popup.close = function( popup_el_or_id )
{
    var popup = spt.popup._get_popup_from_popup_el_or_id( popup_el_or_id );
    popup = popup ? popup : spt.popup.get_popup(popup_el_or_id);

    if (!popup) return;

    spt.hide( popup );
    spt.popup.hide_all_aux_divs( popup );

    if( popup == spt.popup._focus_el ) {
        spt.popup.release_focus( spt.popup._focus_el );
    }
}


spt.popup.toggle_display = function( popup_el_or_id, use_safe_position )
{
    var popup = spt.popup._get_popup_from_popup_el_or_id( popup_el_or_id );
    if( ! popup ) { return; }

    var display_style = popup.getStyle("display");
    if( display_style == "none" ) {
        spt.popup.open( popup, use_safe_position );
    } else {
        spt.popup.close( popup );
    }
}


spt.popup.hide_all_aux_divs = function( popup_el_or_id )
{
    var popup = $(popup_el_or_id);
    var aux_divs = popup.getElements('.SPT_AUX');
    for( var c=0; c < aux_divs.length; c++ )
    {
        var aux = aux_divs[c];
        spt.hide( aux );
    }
}


spt.popup._position = function( popup, use_safe_position )
{
    var popup_drag = spt.z_index.get_z_el(popup);

    var check_left = popup.getProperty('spt_last_scroll_left');
    var check_top  = popup.getProperty('spt_last_scroll_top');

    if( ! check_left ) {
        popup.setProperty('spt_last_scroll_left','0');
    }
    if( ! check_top ) {
        popup.setProperty('spt_last_scroll_top','0');
    }

    var last_scroll_left = parseInt( popup.getProperty('spt_last_scroll_left') );
    var last_scroll_top  = parseInt( popup.getProperty('spt_last_scroll_top') );

    var body = document.body;

    var scroll_left = body.scrollLeft;
    var scroll_top = body.scrollTop;

    var curr_left = parseInt( popup_drag.getStyle("left") );
    var curr_top = parseInt( popup_drag.getStyle("top") );

    var pos_left = 0;
    var pos_top = 0;

    if( use_safe_position ) {
        pos_left = scroll_left + 50;
        pos_top = scroll_top + 40;
    } else {
        if( scroll_left != last_scroll_left ) {
            pos_left = curr_left + (scroll - last_scroll_left);
        } else {
            pos_left = curr_left;
        }

        if( scroll_top != last_scroll_top ) {
            pos_top = curr_top + (scroll_top - last_scroll_top);
        } else {
            pos_top = curr_top;
        }
    }

    /*
    spt.js_log.debug( "curr_left = " + curr_left );
    spt.js_log.debug( "curr_top = " + curr_top );

    spt.js_log.debug( "pos_left = " + pos_left );
    spt.js_log.debug( "pos_top = "  + pos_top );
    */

    popup_drag.setStyle("left", pos_left);
    popup_drag.setStyle("top",  pos_top);

    popup.setProperty('spt_last_scroll_left', String(scroll_left));
    popup.setProperty('spt_last_scroll_top', String(scroll_top));
}


spt.popup.destroy = function( popup_el_or_id )
{
    var popup = $(popup_el_or_id);

    spt.popup.close( popup );
    spt.behavior.destroy_element( popup );
}


// Dynamically clones the template popup and fill it in with a dynamically
// loaded widget.  This acts as a behavior
// @param: load_once - load this only once if the popup is in view
spt.popup.get_widget = function( evt, bvr )
{
    if (typeof(bvr.options) == "undefined" || bvr.options == null) {
        bvr.options = {};
    }
    var options = bvr.options;


    var title = "-No Title-";
    if( bvr.options.hasOwnProperty("title") ) {
        title = bvr.options.title;
    }
    var class_name = null;
    if( bvr.options.hasOwnProperty("class_name") ) {
        class_name = bvr.options.class_name;
    } else {
        spt.js_log.warning("WARNING: No popup widget 'class_name' found in options for the following bvr ...");
        spt.js_log.warning( bvr );
        spt.js_log.warning("... ABORTING popup creation.");
        return;
    }

    var args = bvr.args;
    var kwargs = bvr.kwargs;

    // get the title
    var width = options["width"];
    var height = options["height"];

    // If bvr has 'popup_id' then check if it already exists and use it (instead of cloning)
    var popup = null;
    var popup_id = null;
    if( bvr.options.hasOwnProperty("popup_id") ) {
        popup_id = bvr.options.popup_id;
        popup = $(popup_id);
    }

    // if load_once is true, just show the existing one
    if (popup && kwargs && kwargs['load_once']) {
        spt.popup.open( popup );
        return;
    }
    // Otherwise, we create a clone of the popup template ...
    var popup_template = null;
    if( ! popup ) {
        // get the common popup, clone it and fill it in
        popup_template = $("popup_template");
        // var popup = spt.behavior.clone(popup_template);  // PREVIOUS (doesn't work well in IE)
        var popup = spt.behavior.duplicate_element(popup_template);

        if( popup_id ) {
            popup.set("id", popup_id);
        } else {
            popup.set("id", spt.unique_id.get_next() + "_popup");
        }

        // If bvr has 'popup_parent_el' then put the popup as child to that ... otherwise, just add it to the
        // existing default popup container available to the page
        var popup_parent = null;
        if( bvr.options.hasOwnProperty("popup_parent_id") ) {
            popup_parent = $(bvr.options.popup_parent_id);
        }

        if( popup_parent ) {
            popup.inject( popup_parent, 'bottom' );
        } else {
            popup.inject(  $("popup_container"), 'bottom' );
        }
        spt.puw.process_new( popup.parentNode );
    }

    // display the popup clone, and bring it forward on top of other popups ...
    spt.popup.open( popup );

    // add the place holder
    var content_wdg = popup.getElement(".spt_popup_content");
    spt.behavior.replace_inner_html( content_wdg, '<div style="font-size: 1.2em; margin: 20px; text-align: center">' +
                                '<img src="/context/icons/common/indicator_snake.gif" border="0"> Loading ...</div>' );

    // -- @@@ -- make this resizeable
    // -- disable popup resize for now until we can make it work properly
    // var resize_icon = popup.getElement(".spt_popup_resize");
    // content_wdg.makeResizable({handle:resize_icon});
    // content_wdg.setStyle("overflow", "hidden");


    // get the content container
    var width_wdg = popup.getElement(".spt_popup_width");
    width_wdg.setStyle("min-width", "200px");
    if (width != null) {
        width_wdg.setStyle("width", width);
    }
    if (height != null) {
        width_wdg.setStyle("height", height);
        width_wdg.setStyle("overflow", "auto");
    }


    // replace the title
    if (title != null) {
        var title_wdg = popup.getElement(".spt_popup_title");
        spt.behavior.replace_inner_html( title_wdg, title );
    }


    // -- NOTE: code below for mouse offset positioning had been commented out with the reason that it
    // -- was breaking in IE ... just uncommented it and tried it and it seems to work fine in IE now.
    // -- Possibly the previous error/break in IE was actually elsewhere that has since been fixed.
    // -- Leaving this uncommented ... and will just address any further IE compatibilities that arise
    // -- from it's re-inclusion ...

    // change position of popup to an offset from mouse position if offset options are provided in the bvr
    var pos = spt.mouse.get_abs_cusor_position(evt);
    if( bvr.options.hasOwnProperty("offset_x") ) {
        var offset_x = bvr.options.offset_x;
        popup.setStyle('left', pos.x + offset_x);
    }
    if( bvr.options.hasOwnProperty("offset_y") ) {
        var offset_y = bvr.options.offset_y;
        popup.setStyle('top', pos.y + offset_y);
    }


    // set the parameters for reload this popup
    content_wdg.setAttribute("spt_class_name", class_name);
    content_wdg.setAttribute("spt_kwargs", JSON.stringify(options));


    var widget_html = options.html;
    if ( widget_html != null) {
        spt.behavior.replace_inner_html( content_wdg, widget_html );
        return popup
    }

    // load the content
    var server = TacticServerStub.get();
    var values = {};
    if (bvr.values) {
        values = bvr.values;
    }
    var kwargs = {'args': args, 'values': values};
    var widget_html = server.get_widget(class_name, kwargs);
 
    // replace the popup html
    spt.behavior.replace_inner_html( content_wdg, widget_html );
    return popup;
}


spt.popup._css_suffixes = [ 'top_left', 'top_right', 'bottom_left', 'bottom_right', 'top', 'bottom', 'left', 'right' ];

spt.popup._focus_el = null;


spt.popup.get_focus = function( popup_el )
{
    if( spt.popup._focus_el == popup_el ) {
        return;
    }

    /*
    var shadow_list = popup_el.getElements('.SPT_POPUP_SHADOW');
    for( var c=0; c < shadow_list.length; c++ )
    {
        var el = shadow_list[c];
        for( var s=0; s < spt.popup._css_suffixes.length; s++ )
        {
            var css_shadow_name = "css_shadow_" + spt.popup._css_suffixes[s];
            var css_active_name = "css_active_" + spt.popup._css_suffixes[s];

            if( el.hasClass(css_shadow_name) ) {
                el.removeClass(css_shadow_name);
                el.addClass(css_active_name);
            }
        }
    }
    */

    if( spt.popup._focus_el ) {
        spt.popup.release_focus( spt.popup._focus_el );
    }
    spt.popup._focus_el = popup_el;

    spt.z_index.bring_forward( spt.z_index.get_z_el(popup_el) )
}


spt.popup.release_focus = function( popup_el )
{
    /*
    var shadow_list = popup_el.getElements('.SPT_POPUP_SHADOW');
    for( var c=0; c < shadow_list.length; c++ )
    {
        var el = shadow_list[c];
        for( var s=0; s < spt.popup._css_suffixes.length; s++ )
        {
            var css_shadow_name = "css_shadow_" + spt.popup._css_suffixes[s];
            var css_active_name = "css_active_" + spt.popup._css_suffixes[s];

            if( el.hasClass(css_active_name) ) {
                el.removeClass(css_active_name);
                el.addClass(css_shadow_name);
            }
        }
    }
    */

    spt.popup._focus_el = null;
}


spt.popup.get_popup = function( src_el )
{
    if (src_el == null) {
        return null;
    }

    if( src_el.hasClass('spt_popup') ) {
        return src_el;
    }
    return src_el.getParent('.spt_popup');
}


spt.popup.toggle_minimize = function( src_el )
{
    spt.toggle_show_hide( spt.get_cousin( src_el, '.spt_popup', '.spt_popup_content' ) );
}


spt.popup._check_focus_by_target = function( target )
{
    if( ! target ) {
        return;
    }
    var target = $(target);

    var popup = null;

    // -- ORIGINAL check was this:  if( target.hasClass('spt_popup') ) { ... }
    // -- but it fails in IE, the target object appears to contain MooTools methods, but they can't be
    // -- accessed for some reason ... not sure why it's this way in IE. To fix we use lower level calls to check
    // -- contained class name ...
    //
    if( target.className ) {
        if( target.className.contains_word('spt_popup') ) {  // DO NOT combine this if with outer if statement!!
            popup = target;
        }
    }

    if( ! popup ) {
        // FIXME: This is the same error as above.  IE does not return a mootools object with $(target).
        if (typeof(target.getParent) == 'undefined') {
            popup = null
        }
        else {
            popup = target.getParent('.spt_popup');
        }
    }

    if( popup ) {
        if( popup != spt.popup._focus_el ) {
            spt.popup.get_focus( popup );
        }
    } else {
        /*
        // Backing out click-off for the moment as it seems to have undesired behavior in some situations
        // ... will either investigate and resolve, or just remove this completely
        if( spt.popup._focus_el ) {
            // if there is a popup that has focus and a non-popup area was clicked on then that popup will
            // lose focus (this is a "click-off") ...
            spt.popup.release_focus( spt.popup._focus_el );
        }
        */
    }
}


spt.popup._check_focus_cbk = function( evt )
{
    if( ! evt ) { evt = window.event; }
    var target = spt.get_event_target(evt);

    spt.popup._check_focus_by_target( target )
}


spt.popup.remove_el_by_class = function( popup, class_tag )
{
    var el_to_rm = popup.getElement( "." + class_tag );
    if( el_to_rm ) {
        spt.behavior.destroy_element( el_to_rm );
    }
    else {
        log.warning( "Unable to find inner popup element with class_tag of '" + class_tag + "' for removal" );
    }
}


// returns the popup element ...
//
spt.popup.tear_off_el = function( el, title, popup_predisplay_fn, class_search_str )
{
    el = $(el);

    // First see if el is already a popup ...
    if( el.hasClass("SPT_IN_A_POPUP") ) {
        return el.getParent(".spt_popup")
    }

    // Otherwise continue on and process as a tear-away element ...
    var popup = null;

    // get the common popup, clone it and fill it in
    var popup_template = $("popup_template");
    // var popup = spt.behavior.clone(popup_template);  // PREVIOUS (doesn't work well in IE)
    var popup = spt.behavior.duplicate_element( popup_template );

    if( el.get("id") ) {
        popup_id = el.get("id") + "_popup";
    } else {
        popup_id = spt.unique_id.get_next() + "_popup";
    }
    popup.set( "id", popup_id );

    // Set title of popup ...
    var title_div = popup.getElement(".spt_popup_title")
    title_div.innerHTML = title

    var popup_parent = el.parentNode;
    if( ! popup_parent ) {
        log.error( "Unable to tear away element with ID '" + popup_id + "'" );
        return null;
    }

    spt.reparent( popup, popup_parent );
    spt.reparent( el, popup.getElement(".spt_popup_content") );

    spt.puw.process_new( popup.parentNode );

    if( popup_predisplay_fn ) {
        popup_predisplay_fn( popup, class_search_str );
    }

    // display the popup clone, and bring it forward on top of other popups ...
    spt.popup.open( popup );
}



// popup resize functionality
spt.popup.last_resize_pos = null;
spt.popup.last_size = null;
spt.popup.resize_drag_setup = function(evt, bvr, mouse_411) {

    var top = bvr.src_el.getParent(".spt_popup");
    var content = top.getElement(".spt_popup_content");

    spt.popup.last_resize_pos = { x: mouse_411.curr_x, y: mouse_411.curr_y };
    spt.popup.last_size = content.getSize();

}


spt.popup.resize_drag_motion = function(evt, bvr, mouse_411) {

    var top = bvr.src_el.getParent(".spt_popup");
    var content = top.getElement(".spt_popup_content");
    var diff = { x: mouse_411.curr_x - spt.popup.last_resize_pos.x, y: mouse_411.curr_y - spt.popup.last_resize_pos.y };

    content.setStyle("width", spt.popup.last_size.x+diff.x);
    content.setStyle("height", spt.popup.last_size.y+diff.y);

}



