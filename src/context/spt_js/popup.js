// -------------------------------------------------------------------------------------------------------------------
//
//   Copyright (c) 2008, Southpaw Technology Inc., All Rights Reserved
//   
//   PROPRIETARY INFORMATION.  This software is proprietary to Southpaw Technology Inc., and is not to be
//   reproduced, transmitted, or disclosed in any way without written permission.
//   
// -------------------------------------------------------------------------------------------------------------------


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
        spt.resize_scroll.adjust_for_scroll( rsw_content_box );
    }

    spt.popup.get_focus( popup );
}


spt.popup.close = function( popup_el_or_id )
{
    var popup = spt.popup._get_popup_from_popup_el_or_id( popup_el_or_id );
    if( ! popup ) { return; }

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





//
// NEW PopWindowWdg client side functionality ...
//
spt.popwin = {};
spt.resize_scroll = {};


spt.resize_scroll.resize = function( activating_el, dx, dy )
{
    var rsw_top_el = activating_el.getParent(".SPT_RSW_TOP");

    var content_box_el = rsw_top_el.getElement(".SPT_RSW_CONTENT_BOX");
    var content_el = content_box_el.getElement(".SPT_RSW_CONTENTS");

    var cb_w = content_box_el.clientWidth;
    var cb_h = content_box_el.clientHeight;

    var min_content_w = parseInt( rsw_top_el.getProperty("spt_min_content_w") );
    var min_content_h = parseInt( rsw_top_el.getProperty("spt_min_content_h") );

    var max_content_w = parseInt( rsw_top_el.getProperty("spt_max_content_w") );
    var max_content_h = parseInt( rsw_top_el.getProperty("spt_max_content_h") );

    var content_w = rsw_top_el.getProperty("spt_content_w");
    var content_h = rsw_top_el.getProperty("spt_content_h");
    if( content_w ) { content_w = parseInt( content_w ); }
    else { content_w = 0; }
    if( content_h ) { content_h = parseInt( content_h ); }
    else { content_h = 0; }

    display_content_w = spt.get_render_display_width( content_el );
    display_content_h = spt.get_render_display_height( content_el );

    if( ! content_w ) {
        content_w = display_content_w;
    }
    if( ! content_h ) {
        content_h = display_content_h;
    }

    var set_max_to_content_size = rsw_top_el.getProperty("spt_set_max_to_content_size");
    if( spt.is_TRUE( set_max_to_content_size ) ) {
        max_content_w = display_content_w;
        max_content_h = display_content_h;
    }

    var scr_left = content_box_el.scrollLeft;
    var scr_top = content_box_el.scrollTop;

    var top_el = rsw_top_el.getParent(".SPT_PWIN_TOP_DIV");
    if( ! top_el ) {
        top_el = rsw_top_el;
    }

    if( max_content_w && (cb_w + dx > max_content_w) ) {
        dx = max_content_w - cb_w;
    }
    var modify_w = false;
    if( dx && (cb_w+dx) >= min_content_w ) {
        modify_w = true;
        if( max_content_w && (cb_w + dx > max_content_w) ) {
            modify_w = false;
        }
    }
    if( modify_w ) {
        var dx_el_list = top_el.getElements(".spt_pwin_DX");
        if( top_el.hasClass("spt_pwin_DX") ) {
            dx_el_list.push( top_el );
        }
        for( var c=0; c < dx_el_list.length; c++ ) {
            var el = dx_el_list[c];
            var el_w = parseInt( el.getStyle("width") );
            el.setStyle("width", (el_w+dx) + "px");
        }

        if( scr_left && dx > 0 && cb_w + dx + scr_left > max_content_w ) {
            var new_scr_left = scr_left - dx;
            if( new_scr_left < 0 ) {
                new_scr_left = 0;
            }
            content_box_el.scrollLeft = new_scr_left;
        }
    }

    if( max_content_h && (cb_h + dy > max_content_h) ) {
        dy = max_content_h - cb_h;
    }
    var modify_h = false;
    if( dy && (cb_h+dy) >= min_content_h ) {
        modify_h = true;
        if( max_content_h && (cb_h + dy > max_content_h) ) {
            modify_h = false;
        }
    }
    if( modify_h ) {
        var dy_el_list = top_el.getElements(".spt_pwin_DY");
        if( top_el.hasClass("spt_pwin_DY") ) {
            dy_el_list.push( top_el );
        }
        for( var c=0; c < dy_el_list.length; c++ ) {
            var el = dy_el_list[c];
            var el_h = parseInt( el.getStyle("height") );
            el.setStyle("height", (el_h+dy) + "px");
        }

        if( scr_top && dy > 0 && cb_h + dy + scr_top > max_content_h ) {
            var new_scr_top = scr_top - dy;
            if( new_scr_top < 0 ) {
                new_scr_top = 0;
            }
            content_box_el.scrollTop = new_scr_top;
        }
    }

    spt.resize_scroll.adjust_scroll_draggables( activating_el );
}


// spt.resize_scroll.drag_resize_setup = function( evt, bvr, mouse_411 )
// {
// }


spt.resize_scroll.drag_resize_motion = function( evt, bvr, mouse_411 )
{
    var dx = mouse_411.curr_x - mouse_411.last_x;
    var dy = mouse_411.curr_y - mouse_411.last_y;

    spt.resize_scroll.resize( bvr.src_el, dx, dy );
}


spt.resize_scroll.drag_resize_action = function( evt, bvr, mouse_411 )
{
    spt.resize_scroll.adjust_for_scroll( bvr.src_el );
}


// spt.resize_scroll.drag_x_resize_setup = function( evt, bvr, mouse_411 )
// {
// }


spt.resize_scroll.drag_x_resize_motion = function( evt, bvr, mouse_411 )
{
    var dx = mouse_411.curr_x - mouse_411.last_x;
    var dy = 0;

    spt.resize_scroll.resize( bvr.src_el, dx, dy );
}


spt.resize_scroll.drag_x_resize_action = function( evt, bvr, mouse_411 )
{
    spt.resize_scroll.adjust_for_scroll( bvr.src_el );
}



// spt.resize_scroll.drag_y_resize_setup = function( evt, bvr, mouse_411 )
// {
// }


spt.resize_scroll.drag_y_resize_motion = function( evt, bvr, mouse_411 )
{
    var dx = 0;
    var dy = mouse_411.curr_y - mouse_411.last_y;

    spt.resize_scroll.resize( bvr.src_el, dx, dy );
}


spt.resize_scroll.drag_y_resize_action = function( evt, bvr, mouse_411 )
{
    spt.resize_scroll.adjust_for_scroll( bvr.src_el );
}



spt.resize_scroll.drag_x_scroll_draggable_motion = function( evt, bvr, mouse_411 )
{
    var rsw_top_el = bvr.src_el.getParent(".SPT_RSW_TOP");
    var dx = mouse_411.curr_x - mouse_411.last_x;

    var content_box = rsw_top_el.getElement(".SPT_RSW_CONTENT_BOX");
    var contents = content_box.getElement(".SPT_RSW_CONTENTS");
    var scr_x_drag_div = rsw_top_el.getElement(".SPT_SCROLL_X_DRAG");

    var cw = spt.get_render_display_width( contents );
    var cb_w = content_box.clientWidth;
    var sd_w = scr_x_drag_div.clientWidth;
    var sd_off_x = parseInt( scr_x_drag_div.getStyle("margin-left") );

    if( cb_w >= cw ) {
        return;
    }

    var max_off_x = cb_w - sd_w;
    var new_off_x = sd_off_x + dx;
    if( new_off_x < 0 ) { new_off_x = 0; }
    if( new_off_x > max_off_x ) { new_off_x = max_off_x; }

    // now map it back to the full scrollTop ...
    var new_scr_left = Math.floor( (1.0 * (new_off_x / cb_w) * cw) + 0.5 );
    content_box.scrollLeft = new_scr_left;

    // and set offset for the scroll draggable too ...
    scr_x_drag_div.setStyle("margin-left", new_off_x+"px");
}


spt.resize_scroll.drag_y_scroll_draggable_motion = function( evt, bvr, mouse_411 )
{
    var rsw_top_el = bvr.src_el.getParent(".SPT_RSW_TOP");
    var dy = mouse_411.curr_y - mouse_411.last_y;

    var content_box = rsw_top_el.getElement(".SPT_RSW_CONTENT_BOX");
    var contents = content_box.getElement(".SPT_RSW_CONTENTS");
    var scr_y_drag_div = rsw_top_el.getElement(".SPT_SCROLL_Y_DRAG");

    var ch = spt.get_render_display_height( contents );
    var cb_h = content_box.clientHeight;
    var sd_h = scr_y_drag_div.clientHeight;
    var sd_off_y = parseInt( scr_y_drag_div.getStyle("margin-top") );

    if( cb_h >= ch ) {
        return;
    }

    var max_off_y = cb_h - sd_h;
    var new_off_y = sd_off_y + dy;
    if( new_off_y < 0 ) { new_off_y = 0; }
    if( new_off_y > max_off_y ) { new_off_y = max_off_y; }

    // now map it back to the full scrollTop ...
    var new_scr_top = Math.floor( (1.0 * (new_off_y / cb_h) * ch) + 0.5 );
    content_box.scrollTop = new_scr_top;

    // and set offset for the scroll draggable too ...
    scr_y_drag_div.setStyle("margin-top", new_off_y+"px");
}


spt.resize_scroll.adjust_scroll_x_draggable = function( activating_el )
{
    var rsw_top_el = activating_el.getParent(".SPT_RSW_TOP");
    var content_box = rsw_top_el.getElement(".SPT_RSW_CONTENT_BOX");
    var contents = content_box.getElement(".SPT_RSW_CONTENTS");

    var cw = spt.get_render_display_width( contents );
    var cb_w = content_box.clientWidth;

    var scroll_x_div = rsw_top_el.getElement(".SPT_SCROLL_X")
    var scroll_x_drag_div = rsw_top_el.getElement(".SPT_SCROLL_X_DRAG")

    // adjust size of scroll draggable ...
    var w = 1.0 * (cb_w / cw) * cb_w;
    if( w < 6 ) {
        w = 6;
    }
    scroll_x_drag_div.setStyle("width",w+"px");
    scroll_x_drag_div.setStyle("height","40px");

    // adjust offset of scroll draggable ...
    var s_left = 1.0 * (content_box.scrollLeft / cw) * cb_w;
    scroll_x_drag_div.setStyle("margin-left", s_left+"px");
}


spt.resize_scroll.adjust_scroll_y_draggable = function( activating_el )
{
    var rsw_top_el = activating_el.getParent(".SPT_RSW_TOP");
    var content_box = rsw_top_el.getElement(".SPT_RSW_CONTENT_BOX");
    var contents = content_box.getElement(".SPT_RSW_CONTENTS");

    var ch = spt.get_render_display_height( contents );
    var cb_h = content_box.clientHeight;

    var scroll_y_div = rsw_top_el.getElement(".SPT_SCROLL_Y")
    var scroll_y_drag_div = rsw_top_el.getElement(".SPT_SCROLL_Y_DRAG")

    // adjust size of scroll draggable ...
    var h = 1.0 * (cb_h / ch) * cb_h;
    if( h < 6 ) {
        h = 6;
    }
    scroll_y_drag_div.setStyle("width","40px");
    scroll_y_drag_div.setStyle("height",h+"px");

    // compensate for a display artifact in Opera browser
    if( spt.browser.is_Opera() ) {
        scroll_y_div.setStyle("height", cb_h+"px");
    }

    // adjust offset of scroll draggable ...
    var s_top = 1.0 * (content_box.scrollTop / ch) * cb_h;
    scroll_y_drag_div.setStyle("margin-top", s_top+"px");
}


spt.resize_scroll.adjust_scroll_draggables = function( activating_el )
{
    spt.resize_scroll.adjust_scroll_x_draggable( activating_el );
    spt.resize_scroll.adjust_scroll_y_draggable( activating_el );
}


spt.resize_scroll.adjust_for_scroll = function( activating_el )
{
    var rsw_top_el = activating_el.getParent(".SPT_RSW_TOP");
    var content_box = rsw_top_el.getElement(".SPT_RSW_CONTENT_BOX");
    var contents = content_box.getElement(".SPT_RSW_CONTENTS");

    var cw = spt.get_render_display_width( contents );
    var ch = spt.get_render_display_height( contents );

    var cb_w = content_box.clientWidth;
    var cb_h = content_box.clientHeight;

    var scroll_x_div = rsw_top_el.getElement(".SPT_SCROLL_X")
    var scroll_x_drag_div = rsw_top_el.getElement(".SPT_SCROLL_X_DRAG")
    var scroll_y_div = rsw_top_el.getElement(".SPT_SCROLL_Y")
    var scroll_y_drag_div = rsw_top_el.getElement(".SPT_SCROLL_Y_DRAG")

    var scroll_bar_sz = parseInt( rsw_top_el.getProperty("spt_scroll_size") );

    var is_scroll_x_shown = true;
    if( spt.is_hidden(scroll_x_div) ) {
        is_scroll_x_shown = false;
    }
    var is_scroll_y_shown = true;
    if( spt.is_hidden(scroll_y_div) ) {
        is_scroll_y_shown = false;
    }

    var top_el = rsw_top_el;
    if( ! top_el.hasClass("SPT_RSW_OUTER_TOP") ) {
        top_el = rsw_top_el.getParent(".SPT_RSW_OUTER_TOP");
    }
    var scroll_expansion = rsw_top_el.getProperty("spt_scroll_expansion");

    var dy_adjust = 0;
    if( cw > cb_w ) {
        if( ! is_scroll_x_shown ) {
            // display x scroll ...
            dy_adjust = scroll_bar_sz;
            spt.resize_scroll.adjust_control_size( top_el, "DY", dy_adjust );

            spt.show( scroll_x_div );
            is_scroll_x_shown = true;
        }
        spt.resize_scroll.adjust_scroll_x_draggable( activating_el );
    } else {
        if( is_scroll_x_shown ) {
            // hide x scroll ...
            dy_adjust = 0 - scroll_bar_sz;
            spt.resize_scroll.adjust_control_size( top_el, "DY", dy_adjust );
            spt.hide( scroll_x_div );
            is_scroll_x_shown = false;
        }
    }

    if( dy_adjust ) {
        if( scroll_expansion == "outside" ) {
            var dy_el_list = top_el.getElements(".spt_pwin_DY");
            dy_el_list.push( top_el );
            for( var c=0; c < dy_el_list.length; c++ ) {
                var el = dy_el_list[c];
                if( el.className.contains("_B_2_i_") || el.className.contains("_B_2_i ") ) {
                    continue;
                }
                var el_h = parseInt( el.getStyle("height") );
                el.setStyle("height", (el_h+dy_adjust) + "px");
            }
        }
        else if( scroll_expansion == "inside" ) {
            var dy_el_list = rsw_top_el.getElements(".spt_pwin_DY");
            dy_el_list.push( rsw_top_el );
            for( var c=0; c < dy_el_list.length; c++ ) {
                var el = dy_el_list[c];
                if( el.className.contains("_B_2_i_") || el.className.contains("_B_2_i ") ) {
                    var el_h = parseInt( el.getStyle("height") );
                    el.setStyle("height", (el_h-dy_adjust) + "px");
                }
            }
        }
        else {
            log.warning("WARNING: unknown scroll_expansion value found ('" +  scroll_expansion + "')");
        }
    }

    var dx_adjust = 0;
    if( ch > cb_h ) {
        if( ! is_scroll_y_shown ) {
            // display y scroll ...
            dx_adjust = scroll_bar_sz;
            spt.resize_scroll.adjust_control_size( top_el, "DX", dx_adjust );

            spt.show( scroll_y_div );
            is_scroll_y_shown = true;
        }
        spt.resize_scroll.adjust_scroll_y_draggable( activating_el );
    } else {
        if( is_scroll_y_shown ) {
            // hide y scroll ...
            dx_adjust = 0 - scroll_bar_sz;
            spt.resize_scroll.adjust_control_size( top_el, "DX", dx_adjust );
            spt.hide( scroll_y_div );
            is_scroll_y_shown = false;
        }
    }

    if( dx_adjust ) {
        if( scroll_expansion == "outside" ) {
            var dx_el_list = top_el.getElements(".spt_pwin_DX");
            dx_el_list.push( top_el );
            for( var c=0; c < dx_el_list.length; c++ ) {
                var el = dx_el_list[c];
                if( el.className.contains("_B_2_i_a ") || el.className.contains("_B_2_ii_a ") ) {
                    continue;
                }
                if( el.hasClass("SPT_SCROLL_X") || el.hasClass("SPT_RESIZE_Y") ) {
                    continue;
                }
                var el_w = parseInt( el.getStyle("width") );
                el.setStyle("width", (el_w+dx_adjust) + "px");
            }
        }
        else if( scroll_expansion == "inside" ) {
            var dx_el_list = rsw_top_el.getElements(".spt_pwin_DX");
            dx_el_list.push( rsw_top_el );
            for( var c=0; c < dx_el_list.length; c++ ) {
                var el = dx_el_list[c];
                if( el.className.contains("_B_2_i_a ") || el.className.contains("_B_2_ii_a ") ) {
                    var el_w = parseInt( el.getStyle("width") );
                    el.setStyle("width", (el_w-dx_adjust) + "px");
                }
            }
        }
        else {
            log.warning("WARNING: unknown scroll_expansion value found ('" +  scroll_expansion + "')");
        }
    }

    var resize_img = top_el.getElement(".SPT_PWIN_RESIZE_IMG");
    if( resize_img ) {
        if( is_scroll_x_shown && is_scroll_y_shown ) {
            resize_img.setStyle("right","2px");
            resize_img.setStyle("bottom","2px");
        } else {
            resize_img.setStyle("right","4px");
            resize_img.setStyle("bottom","4px");
        }
    }
}


spt.resize_scroll.adjust_control_size = function( rsw_top_el, DX_or_DY, size_adj )
{
    var top_el = rsw_top_el;
    if( ! top_el.hasClass("SPT_RSW_OUTER_TOP") ) {
        top_el = rsw_top_el.getParent(".SPT_RSW_OUTER_TOP");
    }

    var el_list = top_el.getElements( ".spt_controls_" + DX_or_DY );
    var dim = "height";
    if( DX_or_DY == 'DX' ) {
        dim = "width";
    }
    for( var c=0; c < el_list.length; c++ ) {
        var el = el_list[c];
        el.setStyle( dim, parseInt(el.getStyle(dim)) + size_adj + "px" );
    }
}


spt.resize_scroll.wheel_scroll = function( evt, bvr, mouse_411 )
{
    var content_box = bvr.src_el;   // expects bvr to be assigned on the element with class "SPT_RSW_CONTENT_BOX"
    var contents = content_box.getElement(".SPT_RSW_CONTENTS");

    var ch = spt.get_render_display_height( contents );
    var cb_h = content_box.clientHeight;
    if( cb_h >= ch ) {
        return;
    }

    var max_scroll_top = ch - cb_h;

    var scroll_top = content_box.scrollTop;
    var delta = 30;
    if( evt.wheel < 0 ) {
        scroll_top += delta;
    } else {
        scroll_top -= delta;
    }

    if( scroll_top < 0 ) { scroll_top = 0; }
    if( scroll_top > max_scroll_top ) { scroll_top = max_scroll_top; }

    content_box.scrollTop = scroll_top;
    spt.resize_scroll.adjust_for_scroll( bvr.src_el );
}






