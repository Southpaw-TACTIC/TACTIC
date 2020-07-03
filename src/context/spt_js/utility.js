// -------------------------------------------------------------------------------------------------------------------
//
//   Copyright (c) 2008, Southpaw Technology Inc., All Rights Reserved
//   
//   PROPRIETARY INFORMATION.  This software is proprietary to Southpaw Technology Inc., and is not to be
//   reproduced, transmitted, or disclosed in any way without written permission.
//   
// -------------------------------------------------------------------------------------------------------------------


// -------------------------------------------------------------------------------------------------------------------
//  Timers for debugging ...
// -------------------------------------------------------------------------------------------------------------------

spt.timer = {};

spt.timer._timers_by_name = {};

spt.timer._timer_names = [];


spt.timer.start = function( timer_name )
{
    var start_time_ms = (new Date()).getTime();

    if( ! spt.timer._timers_by_name.hasOwnProperty( timer_name ) ) {
        spt.timer._timers_by_name[ timer_name ] = [ { 'start': start_time_ms } ];
        spt.timer._timer_names.push( timer_name );
    } else {
        spt.timer._timers_by_name[ timer_name ].push( { 'start': start_time_ms } );
    }
}


spt.timer.stop = function( timer_name )
{
    var stop_time_ms = (new Date()).getTime();
    var start_time_found = false;

    if( spt.timer._timers_by_name.hasOwnProperty( timer_name ) ) {
        var num_timers =  spt.timer._timers_by_name[timer_name].length;
        if( num_timers > 0 ) {
            spt.timer._timers_by_name[ timer_name ][ num_timers - 1] [ 'stop' ] = stop_time_ms;
            start_time_found = true;
        }
    }
    
    if( ! start_time_found ) {
        spt.js_log.warning("WARNING: cannot register stop time for timer named '" + timer_name + "' ... " +
                            "no start time found for it.");
    }
}


spt.timer.print_timers = function()
{
    spt.js_log.debug( " " );
    for( var i=0; i < spt.timer._timer_names.length; i++ ) {
        var t_name = spt.timer._timer_names[i];
        var timer_list = spt.timer._timers_by_name[ t_name ];
        spt.js_log.debug( '[timer] "' + t_name + '" ran ' + timer_list.length + ' time(s) ...' );
        for( var t=0; t < timer_list.length; t++ ) {
            var timer = timer_list[t];
            var delta_str = "--undefined--";
            if( timer.stop ) {
                delta_str = "" + ((timer.stop - timer.start) / 1000.0) + " seconds";
            }
            spt.js_log.debug( "[timer]     " + delta_str );
        }
        spt.js_log.debug( " " );
    }
}


spt.timer.print_total_times = function()
{
    spt.js_log.debug( " " );
    for( var i=0; i < spt.timer._timer_names.length; i++ ) {
        var t_name = spt.timer._timer_names[i];
        var timer_list = spt.timer._timers_by_name[ t_name ];
        var timer_total_time = 0;
        for( var t=0; t < timer_list.length; t++ ) {
            var timer = timer_list[t];
            if( timer.stop ) {
                var delta = (timer.stop - timer.start) / 1000.0;
                timer_total_time = timer_total_time + delta;
            }
        }
        spt.js_log.debug( "[timer] '" + t_name + "' ran for a TOTAL TIME of " + timer_total_time + " seconds, " +
                            "over " + timer_list.length + " timer segments" );
        spt.js_log.debug( " " );
    }
}


spt.timer.clear_all = function()
{
    for( var t_name in spt.timer._timers_by_name ) {
        if( ! spt.timer._timers_by_name.hasOwnProperty( t_name ) ) { continue; }

        delete spt.timer._timers_by_name[ t_name ];
    }
    spt.timer._timer_names = null;
    spt.timer._timer_names = [];
}


// -------------------------------------------------------------------------------------------------------------------
//  Position and Size information tools ...
// -------------------------------------------------------------------------------------------------------------------

// Function to get the absolute top and left offsest of the given element within a document page
//
spt.get_absolute_offset = function( el )
{
    var abs_offset = { x: 0, y: 0 };
    if( el )
    {
        abs_offset.x = el.offsetLeft; 
        abs_offset.y = el.offsetTop; 
        
        var offset_p = el.offsetParent;
        var p_node = el.parentNode;

        var is_in_resize_scroll_wdg = false;

        while( offset_p ) {

            if( p_node.className.match( /SPT_RSW_/ ) ) {
                is_in_resize_scroll_wdg = true;
            }

            abs_offset.x += offset_p.offsetLeft;
            abs_offset.y += offset_p.offsetTop;

            if( offset_p != document.body && offset_p != document.documentElement) {
                abs_offset.x -= offset_p.scrollLeft;
                abs_offset.y -= offset_p.scrollTop;
            }

            if( spt.browser.is_Firefox() ) {
                // handle known issue in FireFox with offsetParent ...
                while( offset_p != p_node && p_node !== null) {
                    abs_offset.x -= p_node.scrollLeft;
                    abs_offset.y -= p_node.scrollTop;
                    p_node = p_node.parentNode;
                }    
            }

            p_node = offset_p.parentNode;
            offset_p = offset_p.offsetParent;
        }
    }

    if( spt.browser.is_IE() && is_in_resize_scroll_wdg ) {
        // further offset numbers to be applied when in IE and when an element is inside of
        // a resize scroll widget ... don't ask me why, it just is ... and I have no idea
        // why these numbers work, but they do ... crazy IE!
        abs_offset.x -= 10;
        abs_offset.y -= 31;
    }

    return abs_offset;
}


// -------------------------------------------------------------------------------------------------------------------
//  Element search tools ...
// -------------------------------------------------------------------------------------------------------------------

/* used for panel searching for refresh */
spt.get_parent_panel = function( src_el ) {
    var top = src_el.getParent('.spt_view_panel'); 
    if (!top)
        top = src_el.getParent('.spt_panel'); 
    if (!top) 
        top = src_el.getParent('.spt_main_panel'); 
    return top;
}

spt.get_parent = function( el, mt_search_str )
{
    el = document.id(el);  // be sure we have a mootools extended element
    var found_parent = el.getParent( mt_search_str );  // mt_search_str is something like ".SPT_BLAH_BLAH"
    if( ! found_parent ) {
        // if not immediately found, attempt to find through stub, in case it is within a popup PUW ...
        found_parent = spt.puw.get_parent_thru_stub( el, mt_search_str );
    }

    return found_parent;
}


spt.get_cousin = function( start_el, up_mt_search_str, down_mt_search_str, puw_ids )
{
    start_el = document.id(start_el);

    // first get top element to search down from ...
    var top_el = spt.get_parent( start_el, up_mt_search_str );
    if( ! top_el ) {
        // then see if we are in a PUW ...
        return null;
    }

    var cousin_el = top_el.getElement( down_mt_search_str );
    if( ! cousin_el && puw_ids != null ) {
        // if not immediately found in normal DOM heirarchy then look through PUW_STUBS ...
        // NOTE: if puw_ids is equal to null then it means we do not search through puw stubs
        var elements = spt.puw.get_elements_thru_stubs( top_el, down_mt_search_str, puw_ids );
        if( elements ) {
            cousin_el = elements[0];
        }
    }
    return cousin_el;
}


spt.get_cousins = function( start_el, up_mt_search_str, down_mt_search_str, puw_ids )
{
    start_el = document.id(start_el);

    // first get top element to search down from ...
    var top_el = spt.get_parent( start_el, up_mt_search_str );
    if( ! top_el ) {
        return null;
    }

    var cousins_list = top_el.getElements( down_mt_search_str );

    if( puw_ids != null ) {
        var elements = spt.puw.get_elements_thru_stubs( top_el, down_mt_search_str, puw_ids );
        if( elements ) {
            cousins_list = cousins_list.concat( elements );
        }
    }
    return cousins_list;
}


spt.get_element = function( top_el, mt_search_str, puw_ids )
{
    var found_el = document.id(top_el).getElement( mt_search_str );
    if( ! found_el ) {
        // if not immediately found in normal DOM heirarchy then look through PUW_STUBS ...
        var elements = spt.puw.get_elements_thru_stubs( top_el, mt_search_str, puw_ids );
        if( elements.length ) {
            found_el = elements[0];
        }
    }
    return found_el;
}


spt.get_elements = function( top_el, mt_search_str, puw_ids )
{
    var found_el_list = document.id(top_el).getElements( mt_search_str );
    var elements = spt.puw.get_elements_thru_stubs( top_el, mt_search_str, puw_ids );

    found_el_list.concat( elements );

    return found_el_list;
}


spt.ctags = {};


spt.ctags._match_tag = function( el_to_match, ctags_list )
{
    var el = document.id(el_to_match);

    for( var c=0; c < ctags_list.length; c++ ) {
        if( el.hasClass( ctags_list[c] ) ) {
            return true;
        }
    }

    return false;
}


spt.ctags._gather_elements = function( el, gather_match_list, ctags_list, boundary_tags_list, return_only_one )
{
    // get the children ...
    var children = document.id(el).getChildren();

    // check the children and recurse ...
    for( var c=0; c < children.length; c++ ) {
        var child = document.id(children[c]);

        if( spt.ctags._match_tag( child, boundary_tags_list ) ) {
            // STOP here ... skip this element ... don't recurse to it's children!
            continue;
        }

        if( spt.ctags._match_tag( child, ctags_list ) ) {
            gather_match_list.push(child);

            if( return_only_one ) {
                return true;
            }

            // if matched do not bother recursing to childer of this node ... for now we don't want to find
            // nested items ...
            continue;
        }

        // now recurse to children ...
        if( spt.ctags._gather_elements( child, gather_match_list, ctags_list, boundary_tags_list ) ) {
            return true;
        }
    }

    return false;
}


spt.ctags.find_elements = function( top_el, ctags_str, boundary_tags_str )
{
    var ctags_list = ctags_str.split( /\s+/ );
    var boundary_tags_list = boundary_tags_str.split( /\s+/ );

    var gather_match_list = [];
    spt.ctags._gather_elements( top_el, gather_match_list, ctags_list, boundary_tags_list, false );

    return gather_match_list;
}


spt.ctags.find_single_element = function( top_el, ctags_str, boundary_tags_str )
{
    var ctags_list = ctags_str.split( /\s+/ );
    var boundary_tags_list = boundary_tags_str.split( /\s+/ );

    var gather_match_list = [];
    spt.ctags._gather_elements( top_el, gather_match_list, ctags_list, boundary_tags_list, true );

    if( gather_match_list.length ) {
        return gather_match_list[0];
    }

    return null;
}


spt.ctags.find_parent = function( start_el, ctags_str, boundary_tags_str, allow_one_boundary_match )
{
    var ctags_list = ctags_str.split( /\s+/ );
    var boundary_tags_list = boundary_tags_str.split( /\s+/ );

    var matched_parent = null;
    var boundary_match_count = 0;

    var pnode = document.id(start_el.parentNode);
    while( pnode ) {

        if( pnode.get('tag') == 'body' ) {
            break;
        }

        if( spt.ctags._match_tag( pnode, ctags_list ) ) {
            matched_parent = pnode;
            break;
        }

        if( spt.ctags._match_tag( pnode, boundary_tags_list ) ) {
            if( allow_one_boundary_match && boundary_match_count == 0 ) {
                boundary_match_count ++;
            }
            else {
                // STOP here
                break;
            }
        }

        pnode = document.id(pnode.parentNode);
    }

    return matched_parent;
}


spt.get_prev_same_siblings = function( curr_el, class_name )
{
    // matches by tag
    var node_name = curr_el.nodeName;
    var prev_siblings = [];
    var prev_node = document.id(curr_el.previousSibling);
    while( prev_node ) {
        if( prev_node.nodeName == node_name ) {
            if( ! class_name || (class_name && prev_node.hasClass(class_name)) ) {
                prev_siblings.push( prev_node );
            }
        }
        prev_node = document.id(prev_node.previousSibling);
    }

    return prev_siblings;
}


spt.get_next_same_siblings = function( curr_el, class_name )
{
    // matches by tag
    var node_name = curr_el.nodeName;
    var next_siblings = [];
    var next_node = document.id(curr_el.nextSibling);
    while( next_node ) {
        if( next_node.nodeName == node_name ) {
            if( ! class_name || (class_name && next_node.hasClass(class_name)) ) {
                next_siblings.push( next_node );
            }
        }
        next_node = next_node.nextSibling;
    }

    return next_siblings;
}


spt.get_prev_same_sibling = function( curr_el, class_name )
{
    // matches by tag
    var node_name = curr_el.nodeName;
    var prev_node = document.id(curr_el.previousSibling);
    while( prev_node ) {
        if( prev_node.nodeName == node_name ) {
            if( ! class_name || (class_name && prev_node.hasClass(class_name)) ) {
                return prev_node;
            }
        }
        prev_node = document.id(prev_node.previousSibling);
    }
    return null;
}


spt.get_next_same_sibling = function( curr_el, class_name )
{
    // matches by tag
    var node_name = curr_el.nodeName;
    var next_node = document.id(curr_el.nextSibling);
    while( next_node ) {
        if( next_node.nodeName == node_name ) {
            if( ! class_name || (class_name && next_node.hasClass(class_name)) ) {
                return next_node;
            }
        }
        next_node = next_node.nextSibling;
    }
    return null;
}


spt.find_closest_sibling_by_tag = function( curr_el, direction_str, tag, optional_match_fn )
{
    // direction_str is either 'next' or 'previous'!

    tag = tag.toUpperCase();
    var node = curr_el;

    while( node ) {
        var stmt = "node = node." + direction_str + "Sibling;";
        eval(stmt);
        if( node && node.tagName && node.tagName == tag ){
            if( optional_match_fn && ! optional_match_fn(node) ) {
                continue;
            }
            break;
        }
    }
    return node;
}


spt.find_first_child_by_tag = function( curr_el, tag )
{
    tag = tag.toUpperCase();
    var children = curr_el.childNodes;

    for( var c=0; c < children.length; c++ ) {
        var child = children[c];
        if( child.tagName && child.tagName == tag ) {
            return child;
        }
    }
    return null;
}


spt.find_first_child_by_class = function( curr_el, cls )
{
    var regex = new RegExp( "\\b" + cls + "\\b" );
    var children = curr_el.childNodes;

    for( var c=0; c < children.length; c++ ) {
        var child = children[c];
        if( 'className' in child ) {
            if( child.className.match( regex ) ) {
                return child;
            }
        }
    }
    return null;
}


// -------------------------------------------------------------------------------------------------------------------
//  Miscellaneous tools ...
// -------------------------------------------------------------------------------------------------------------------


spt.FALSE_map = { 'false': 0, 'False': 0, 'FALSE': 0, 'n': 0, 'N': 0, 'no': 0, 'No': 0, 'NO': 0 };
spt.TRUE_map = { 'true': 1, 'True': 1, 'TRUE': 1, 'y': 1, 'Y': 1, 'yes': 1, 'Yes': 1, 'YES': 1 };

spt.is_FALSE = function( test_me )
{
    if( ! test_me || test_me in spt.FALSE_map ) {
        return true;
    }
    return false;
}


spt.is_TRUE = function( test_me )
{
    if( test_me in spt.TRUE_map || test_me == true ) {
        return true;
    }
    return false;
}


spt.get_style_map_from_str = function( styles_str )
{
    var style_map = {};
    var pairs = styles_str.split(';');
    for( var c=0; c < pairs.length; c++ ) {
        var pair = pairs[c].strip();
        if( pair ) {
            var bits = pair.split(':');
            var style = bits[0].strip();
            var value = bits[1].strip();
            style_map[ style ] = value;
            if( style == 'opacity' ) {
                // IE compat
                var op_value = parseInt( parseFloat(value) * 100.0 );
                style_map[ 'filter' ] = 'alpha(opacity=' + op_value + ')';
            }
        }
    }

    return style_map;
}


spt.zero_pad = function( num, padding ) {
    var num_str = ""+num;
    var length = num_str.length;

    for (var i = 0; i < padding - length; i++) {
        num_str = '0' + num_str;
    }

    return num_str;
}


spt.convert_to_alpha_numeric = function( value ) {
    var new_value = value.replace(/[\?\.!@#$%^&*()'",;\+=]/g, "");
    new_value = new_value.replace(/ /g, "_");
    new_value = new_value.toLowerCase();
    new_value = new_value.replace(/[\\_-]+/g, "_");
    return new_value
}



spt.generate_key = function(length) {
    if (!length) {
        length = 20;
    }

    var text = "";
    var possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
    for( var i=0; i < length; i++ ) {
        text += possible.charAt(Math.floor(Math.random() * possible.length));
    }

    return text;

    
}


// spt.get_typeof
//
// DO NOT use if argument x is expected to possibly be undefined ... passing in undefined will generate a Javascript
// error. Instead use 'if( typeof x == "undefined" ) {}' directly when testing to see if a variable is undefined.
//
spt.get_typeof = function( x )
{
    if (typeof(x) == "number" && isNaN(x)) {
        return "not-a-number";
    }
    // use mootools typeOf (Note the capital O)
    if ( typeOf(x) == 'elements' ) {
        return "array"
    }

    if( typeof(x) == "object" ) {
        if (x === null) return "null";
        if (x.constructor == (new Array).constructor) return "array";
        if (x.constructor == (new Date).constructor) return "date";
        if (x.constructor == (new RegExp).constructor) return "regex";
        return "object";
    }
    return typeof(x);
}


spt.reparent = function( el, new_parent_el )
{
    var curr_parent = el.parentNode;
    if( curr_parent ) {
        curr_parent.removeChild( el );
    }
    new_parent_el.appendChild( el );
}


spt.obj_is_empty = function( obj )
{
    for( var name in obj ) {
        if( obj.hasOwnProperty( name ) ) { return false; }
    }
    return true;
}


spt.unique_id = {};
spt.unique_id._current_id = 1;

spt.unique_id.get_next = function( label )
{
    if( ! label ) { label = ''; }
    else { label = label + '_'; }

    var id_str = ("spt_id_" + label + spt.unique_id._current_id);

    spt.unique_id._current_id ++;
    return id_str;
}


spt.has_class = function( el, cls )
{
    if( !el || !('className' in el) ) {
        return false;
    }

    var class_name;
    if (el.className.baseVal || el.className.baseVal != null) {
        class_name = el.className.baseVal;
    }
    else if (el.className) {
        class_name = el.className;
    }
    else {
        return false;
    }

    var regex = new RegExp( "\\b" + cls + "\\b" );
    if( class_name.match( regex ) ) {
        return true;
    }

    return false;
}


spt.add_class = function( el, cls )
{
    var regex = new RegExp( "\\b" + cls + "\\b" );
    if( ! el.className.match( regex ) ) {
        el.className = (el.className + " " + cls).trim();
    }
}


spt.remove_class = function( el, cls )
{
    var regex = new RegExp( "\\b" + cls + "\\b" );
    if( el.className && el.className.match( regex ) ) {
        el.className = el.className.replace(regex,'').replace(/\s+/,' ').trim();
    }
}


spt.replace_class = function( el, cls_to_replace, new_cls )
{
    var regex = new RegExp( "\\b" + cls_to_replace + "\\b" );
    if( el.className.match( regex ) ) {
        el.className = el.className.replace(regex,new_cls).replace(/\s+/,' ').trim();
    }
}


spt.get_event_target = function( evt )
{
    if( ! evt ) {
        return null;
    }

    if( spt.browser.is_IE() ) {
        if( 'srcElement' in evt ) {
            return document.id(evt.srcElement);
        }
        else if( evt && 'event' in evt && 'srcElement' in evt.event ) {
            // this is what IE is returning!
            return document.id(evt.event.srcElement);
        }
    }

    if( 'target' in evt ) {
        return document.id(evt.target);
    }

    // should never reach here!
    return null;
}


spt.halt_event_here = function( evt )
{
    // This function stops event from continuing on to any other elements, and also stops any default
    // behavior that the event might normally go through. Call this when you've handled the event
    // yourself and don't want anything else to get it.
    //
    if( evt.stopPropagation ) {
        evt.stopPropagation();   // dom level 2
    } else {
        evt.cancelBubble = true;   // ie
    }

    // Now prevent any default action.
    if( evt.preventDefault ) {
        evt.preventDefault();     // dom level 2
    } else {
        evt.returnValue = false;      // ie
    }
}


spt.has_attr = function( el, attr )
{
    // Use this for IE compatibility, as IE doesn't support the hasAttribute method ...
    //
    if( el.getAttribute(attr) == null || typeof(el.getAttribute(attr)) == "undefined" ) {
        return false;
    } else {
        return true;
    }
}


spt.get_style_result = function(el, style_prop)
{
    if( el.style[style_prop] ) {
        return el.style[style_prop];
    }
    else if (document.defaultView && document.defaultView.getComputedStyle) {
        return document.defaultView.getComputedStyle(el, null)[style_prop];
    } else if (el.currentStyle) {
        return el.currentStyle[style_prop];
    }
}


// TODO: deprecate this function -- use spt.get_render_display_width() below instead ...
spt.get_element_width = function( el )
{
    return spt.get_style_result( el, "width" );
}


// TODO: deprecate this function -- use spt.get_render_display_height() below instead ...
spt.get_element_height = function( el )
{
    return spt.get_style_result( el, "height" );
}


// TODO: deprecate this function -- use spt.get_render_display_width() below instead ...
spt.get_el_real_cwidth = function( el, ignore_padding, ignore_border )
{
    el = document.id(el);
    var cwidth = el.clientWidth;

    var border_left = parseInt( el.getStyle("border-left-width") );
    var border_right = parseInt( el.getStyle("border-right-width") );

    var padding_left = parseInt( el.getStyle("padding-left") );
    var padding_right = parseInt( el.getStyle("padding-right") );

    if( spt.browser.is_IE() ) {
        cwidth = cwidth + padding_left + padding_right;
    }
    cwidth = cwidth + border_left + border_right;

    if( ignore_padding ) {
        cwidth = cwidth - padding_left - padding_right;
    }
    if( ignore_border ) {
        cwidth = cwidth - border_left - border_right;
    }
    return cwidth;
}


// TODO: deprecate this function -- use spt.get_render_display_height() below instead ...
spt.get_el_real_cheight = function( el, ignore_padding, ignore_border )
{
    el = document.id(el);
    var cheight = el.clientHeight;

    var border_top = parseInt( el.getStyle("border-top-width") );
    var border_bottom = parseInt( el.getStyle("border-bottom-width") );

    var padding_top = parseInt( el.getStyle("padding-top") );
    var padding_bottom = parseInt( el.getStyle("padding-bottom") );

    if( spt.browser.is_IE() ) {
        cheight = cheight + padding_top + padding_bottom;
    }
    cheight = cheight + border_top + border_bottom;

    if( ignore_padding ) {
        cheight = cheight - padding_top - padding_bottom;
    }
    if( ignore_border ) {
        cheight = cheight - border_top - border_bottom;
    }
    return cheight;
}


spt.get_render_display_width = function( el )
{
    el = document.id(el);
    var w = el.clientWidth;  // will include padding in non-IE browsers

    var border_left = parseInt( el.getStyle("border-left-width") );
    var border_right = parseInt( el.getStyle("border-right-width") );

    // do not need to adjust for padding, as clientWidth will always include padding on any browser
    //
    return ( w + border_left + border_right );
}


spt.get_render_display_height = function( el )
{
    el = document.id(el);
    var h = el.clientHeight;  // will include padding in non-IE browsers

    var border_top = parseInt( el.getStyle("border-top-width") );
    var border_bottom = parseInt( el.getStyle("border-bottom-width") );

    // do not need to adjust for padding, as clientWidth will always include padding on any browser
    //
    return ( h + border_top + border_bottom );
}


spt.in_bounds = function( x, y, bounding_box )
{
    var bb = bounding_box;
    if( x >= bb.x0 && x <= bb.x1 && y >= bb.y0 && y <= bb.y1 ) {
        return true;
    }
    return false;
}


spt.convert_to_html_display = function( in_string )
{
    out_string = in_string;

    out_string = out_string.replace( /\x3C/g, "&lt;" );  // "<"
    out_string = out_string.replace( /\x3E/g, "&gt;" );  // ">"
    out_string = out_string.replace( /\x20\x20/g, "&nbsp;&nbsp;" );  // "  " (2 spaces)

    // convert anything that will have angle braces after the angle brace conversion above!
    out_string = out_string.replace( /\n/g, "<br/>" );

    return out_string;
}


spt.get_cursor_position = function( el )
{
    var pos = 0;

    if( document.selection )     // support for IE
    {
        // el.focus();  // do we need this? may run things through on_focus again ... might be bad!
        var selection_range = document.selection.createRange();
        selection_range.moveStart('character', -el.value.length);
        pos = selection_range.text.length;
    }
    else if( el.selectionStart )    // FireFox
    {
        pos = parseInt( el.selectionStart );
    }
    return pos;
}


spt.set_cursor_position = function( el, pos )
{
    if( el.setSelectionRange ) {
        // el.focus();
        el.setSelectionRange(pos,pos);
    }
    else if( el.createTextRange ) {
        var text_range = el.createTextRange();
        text_range.collapse(true);
        text_range.moveEnd('character',pos);
        text_range.moveStart('character',pos);
        text_range.select();
    }
}


// -------------------------------------------------------------------------
//  functions for disabling text selection on elements ...
// -------------------------------------------------------------------------

spt.disable_text_selection = function( el )
{
    el.onselectstart = function() {
        return false;
    };
    el.unselectable = "on";
    el.style.MozUserSelect = "none";

    // do not override el.style.cursor here ... will affect our other class cursor overrides elsewhere
}


spt.disable_text_selection_by_class = function( class_name, start_el )
{
    var el_list = [];
    if( start_el ) {
        el_list = document.id(start_el).getElements( ('.'+class_name) );
    } else {
        el_list = document.getElements( ('.'+class_name) );
    }

    for( var c = 0; c < el_list.length; c++ )
    {
        var el = el_list[c];
        if( el ) {
            spt.disable_text_selection( el );
        }
    }
}


spt.disable_text_selection_by_id = function( el_id )
{
    var el = document.getElementById( el_id );
    if( el ) {
        spt.disable_text_selection( el );
    }
}


// -------------------------------------------------------------------------
//  convenience functions for showing / hiding any HTML element
// -------------------------------------------------------------------------

spt.show = function( element )
{
    // element can be element ID or element itself ...
    var el = document.id(element);
    if( el ) {
        el.setStyle("display","");
        if (el.getStyle("opacity") == "0")
            el.setStyle("opacity", "1");

        if (el.getStyle("visibility") == "hidden") {
            //el.fade("in");
            el.setStyle("visibility", "visible");
            el.setStyle("opacity", "1");
        }
        if( el.hasClass("SPT_BVR") ) {
            var show_bvr_list = spt.behavior.get_bvrs_by_type("show", el);
            for( var c=0; c < show_bvr_list.length; c++ ) {
                var show_bvr = show_bvr_list[c];
                if( show_bvr.cbjs_action ) {
                    spt.behavior.run_cbjs( show_bvr.cbjs_action, show_bvr, {}, {} );
                }
            }
        }
    }

}

spt.show_block = function( element )
{
    // element can be element ID or element itself ...
    var el = document.id(element);
    if (el) {
        el.setStyle("display","block");
        if( el.hasClass("SPT_BVR") ) {
            var show_bvr_list = spt.behavior.get_bvrs_by_type("show", el);
            for( var c=0; c < show_bvr_list.length; c++ ) {
                var show_bvr = show_bvr_list[c];
                if( show_bvr.cbjs_action ) {
                    spt.behavior.run_cbjs( show_bvr.cbjs_action, show_bvr, {}, {} );
                }
            }
        }
    }

}


spt.hide = function( element )
{
    // element can be element ID or element itself ...
    var el = document.id(element);
    if (el) {
        el.setStyle("display","none");
        if( el.hasClass("SPT_BVR") ) {
            var hide_bvr_list = spt.behavior.get_bvrs_by_type("hide", el);
            for( var c=0; c < hide_bvr_list.length; c++ ) {
                var hide_bvr = hide_bvr_list[c];
                if( hide_bvr.cbjs_action ) {
                    spt.behavior.run_cbjs( hide_bvr.cbjs_action, hide_bvr, {}, {} );
                }
            }
        }
    }

}


spt.is_shown = function( element )
{
    if (!element) return false;
        
    var display = element.getStyle("display");
    if( display == "none" ) {
        return false;
    }
    return true;
}


spt.is_hidden= function( element )
{
    var display = element.getStyle("display");
    if( display == "none" ) {
        return true;
    }
    return false;
}


spt.toggle_show_hide = function( element )
{
    var el = document.id(element);
    if( spt.is_shown( el ) ) {
        spt.hide( el );
    } else {
        spt.show( el );
    }
}

spt.toggle_checkbox = function(bvr, filter, cb_name) {
    var top = bvr.src_el.getParent(filter);
    inputs = spt.api.Utility.get_inputs(top, cb_name);
    var me = bvr.src_el;
    if (me.checked)
    {
        for (k=0; k<inputs.length; k++)
            inputs[k].checked = false;
        me.checked = true;
    }
}


/* if bias_id is specified, its display will take precedence */
// DEPRECATED: only kept here for old SwapDisplayWdg
spt.swap_display = function(element1_id, element2_id, bias_id)
{
    var element1 = document.getElementById( element1_id )
    var element2 = document.getElementById( element2_id )
    if (element1 == null || element2 == null)
        return

    if ( element1.style.display == "none" || bias_id == element1_id )
    {
        element1.style.display = "inline"
        element2.style.display = "none"
    }
    else
    {
        element1.style.display = "none"
        element2.style.display = "inline"
    }

}



// -------------------------------------------------------------------------
//  function for toggling display ... hardcoded for proto left bookmarks nav
// -------------------------------------------------------------------------

spt.simple_display_toggle = function( element, kwargs )
{
    var elements;
    var type = spt.get_typeof(element);
    if (type == "string") {
        var top_el;
        if (!kwargs) {
            top_el = document;
        }
        else {
            top_el = document.id(kwargs.top_el);
        }
        elements = top_el.getElements(element);

        // try getting the element by tradional method
        if (elements.length == 0) {
            var element = document.getElementById(element);
            if (element != null) {
                elements = [document.id(element)];
            }
        }
    }
    else {
        elements = [element];
    }

    for (var i = 0; i < elements.length; i++) {
        var element = elements[i];
        // element.setStyle("border", "solid blue 1px")

        if( element.getStyle("display") == 'none' ) {
            spt.show( element );
            // element.setStyle("display",'');
        }
        else {
            spt.hide( element );
            // element.setStyle("display",'none');
        }
    }
}


// simple_display_hide: hide a given element
//
// kwargs:
//  top_el: the top element to search under

spt.simple_display_hide = function( element, kwargs )
{
    var elements;
    var type = spt.get_typeof(element);
    if (type == "string") {
        var top_el;
        if (!kwargs) {
            top_el = document;
        }
        else {
            top_el = document.id(kwargs.top_el);
        }
        elements = top_el.getElements(element);
    }
    else {
        elements = [element];
    }

    for (var i = 0; i < elements.length; i++) {
        var element = elements[i];
        spt.hide( element );
        // element.setStyle("display",'none');
    }

}

// simple_display_show: show a given element
//
// kwargs:
//  top_el: the top element to search under
spt.simple_display_show = function( element, kwargs )
{
    var elements;
    var type = spt.get_typeof(element);
    if (type == "string") {
        var top_el;
        if (!kwargs) {
            top_el = document;
        }
        else {
            top_el = document.id(kwargs.top_el);
        }
        elements = top_el.getElements(element);
    }
    else {
        elements = [element];
    }

    for (var i = 0; i < elements.length; i++) {
        var element = elements[i];
        spt.show( element );
        // element.setStyle("display",'');
    }
}






// -------------------------------------------------------------------------
//  function for transactions
// -------------------------------------------------------------------------

spt.transaction_panel = {}

spt.undo_cbk = function(evt, bvr)
{

    var title = 'Undo:';
    var msg = 'Undoing last transaction ...';
    spt.app_busy.show( title, msg );

    if( spt.browser.is_IE() ) {
        // FIXME: IE does not refresh the activating panel for now
        setTimeout( "spt.undo(); spt.panel.refresh('main_body'); spt.app_busy.hide();", 0 );
    } else {
        spt.undo();

        spt.app_busy.show( title, 'Finished' );
        // refresh the activating panel
        var activator = spt.smenu.get_activator(bvr);
        if (activator == null) {
            
            //spt.panel.refresh("main_body");
            spt.tab.set_main_body_tab();
            spt.tab.reload_selected();
        } 
        else {
            var panel = activator.getParent('.spt_panel');
            spt.dg_table.search_cbk( {}, {'panel': panel, 'src_el': activator} );
        }

        spt.app_busy.hide();
    }

}

spt.undo = function(transaction_id)
{
    try {
        var kwargs = {};
        var server = TacticServerStub.get();
        if (transaction_id){
            kwargs['transaction_id'] = transaction_id;
        }
        server.undo(kwargs);
    }
    catch(e){
        spt.alert(spt.exception.handler(e));
    }
    //spt.panel.refresh("main_body");
}

spt.redo_cbk = function(evt, bvr)
{
    var title = 'Redo:';
    var msg = 'Redoing last "Undone" transaction ...';
    spt.app_busy.show( title, msg );

    if( spt.browser.is_IE() ) {
        // FIXME: IE does not refresh the activating panel for now
        setTimeout( "spt.redo(); spt.panel.refresh('main_body'); spt.app_busy.hide();", 0 );
    } else {
        spt.redo();

        spt.app_busy.show( title, 'Finished' );
        // refresh the activating panel
        var activator = spt.smenu.get_activator(bvr);
        if (activator == null) {

            //spt.panel.refresh("main_body");
            spt.tab.set_main_body_tab();
            spt.tab.reload_selected();
        } 
        else {
            var panel = activator.getParent('.spt_panel');
            var layout = activator.getParent('.spt_layout');
            if (layout) {
                spt.dg_table.search_cbk( {}, {'panel': panel, 'src_el': activator} );
            }
            else {
                spt.panel.refresh(panel, {}, true);
            }
        }

        spt.app_busy.hide();
    }
}

spt.redo = function(transaction_id)
{
    try {
        var kwargs = {};
        var server = TacticServerStub.get();
        if (transaction_id){
            kwargs['transaction_id'] = transaction_id;
        }
        server.redo(kwargs);
    }
    catch(e){
        spt.alert(spt.exception.handler(e));
    }
}

spt.refresh_page = function()
{
    window.location.href = unescape(window.location.pathname);
}

// -------------------------------------------------------------------------
//   alert, error, info or confirm dialog
// -------------------------------------------------------------------------

spt._init_dialog = function(on_complete) {
    // FIXME: need better checking
    //var loading = spt.require.load("mooDialog/Overlay.js")
    //spt.require.load("mooDialog/MooDialog.js")
    //spt.require.load("mooDialog/MooDialog.Extra.js")

    spt.dom.load_js( ['mooDialog/Overlay.js'], function() {
        spt.dom.load_js( ['mooDialog/MooDialog.js'], function() {
            spt.dom.load_js( ['mooDialog/MooDialog.Extra.js'], function() {
                on_complete();
            })
        })
    });
}


spt.alert = function(msg, options){
    err = new Error();
    console.log(err.stack);
    
    var env = spt.Environment.get();
    if (env) {
        if (env.get_kiosk_mode() == true) {
            spt.js_log.critical("In kiosk mode - alert suppressed: " + msg);
            return;
        } 
    }
            
    if (!options) options = {};
    if (!options.title) options.title = 'Alert';
    options.autosize = true;
   
    spt._init_dialog( function() {
        new MooDialog.Alert(msg, options);
            
    } );
}

spt.prompt = function(msg, button_fn, options){
   
    if (!options) options = {};
    if (!options.title) options.title = 'Prompt';
    options.autosize = true;

    spt._init_dialog( function() {
        new MooDialog.Prompt(msg, button_fn, options);
    } );
}
spt.info = function(msg, options){
   
    if (!options) options = {};
    if (!options.title) options.title = 'Info';
    options.textPClass = 'MooDialogInfo';
    spt.alert(msg, options)
}

spt.error = function(msg, options){
   
    if (!options) options = {};
    if (!options.title) options.title = 'Error';
    options.autosize = true;
    options.fx = {
			type: 'tween',
			open: 1,
			close: 0,
			options: {
				property: 'opacity',
				duration: 50
			}
		};

    spt._init_dialog( function() {
        new MooDialog.Error(msg, options);
    } );

}

/* Control flow for MooDialog confirm. On OK, calls OK function with argument
 * ok_args  and on cancel, calls cancel function with cancel_args.
 * Example usage: 
 * var ok = function(ok_arg_list) {alert('passed in multiple arguments: ' + ok_arg_list)};
 * var cancel = function(cancel_arg) {alert('passed in one argument: ' + cancel_arg')}
 * spt.confirm("Continue? ", ok, cancel, {ok_args: ["one","two","three"], cancel_args: 'nothing'});
 */
spt.confirm = function(msg, button_fn1, button_fn2, options){
  
    if (!options) options = {};
    options.title = 'Confirm';
    options.closeOnOverlayClick = false,
    options.autosize = true,
    options.fx =  {
			type: 'tween',
			open: 1,
			close: 0,
			options: {
				property: 'opacity',
				duration: 50
			}
		}


    spt._init_dialog( function() {
        var confirm = new MooDialog.Confirm(msg, button_fn1, button_fn2, options);
    } );



    
}

// -------------------------------------------------------------------------
//  function for file download
// -------------------------------------------------------------------------

spt.download_file = function(file_name, el) 
{
    var iframe = document.createElement("iframe");

    iframe.src = file_name; 
    iframe.onload = function() {
        if (el)
            el.innerHTML = "Downloading. . .";
    }
    iframe.style.display = "none";
    document.body.appendChild(iframe);
}

// -------------------------------------------------------------------------
//  user input validation
// -------------------------------------------------------------------------

spt.input = {};

spt.input.has_special_chars = function(str)
{
    // xml friendly, no spaces, do not use the global g directive or it does not work every time
    var re = /[/\$\s,@#~`\%\*\^\&\(\)\+\=\[\]\[\}\{\;\:\'\"\<\>\?\|\\\!\.]/;
    return re.test(str)
}
     
spt.input.start_with_num = function(str)
{
    // xml friendly, no spaces, do not use the global g directive or it does not work every time
    var re = /^\d.*/;
    return re.test(str)
}

// save selected checkbox or other inputs into WidgetSettings 
spt.input.save_selected = function(bvr, name, key)
{
    var checkbox_grp = bvr.src_el.getParent('.spt_input_group');
    var values = spt.api.Utility.get_input_values(checkbox_grp, 'input[name=' + name + ']');
    var value_list = values[name];
    // use the same logic in WidgetSettings.set_key_values()
    var new_value_list = [];
    for (var i=0; i < value_list.length; i++){
        if (value_list[i])
            new_value_list.push(value_list[i]);
    }
    
    spt.api.Utility.save_widget_setting(key, new_value_list.join('||'));
}

spt.input.is_numeric = function(n) 
{
    return !isNaN(parseFloat(n)) && isFinite(n);
}
    
spt.input.is_integer = function(n) 
{
    return !isNaN(n) && (parseFloat(n,10) == parseInt(n,10)); 
}   
// -------------------------------------------------------------------------
//  Javascript-side JSON string parsing
// -------------------------------------------------------------------------

spt.json_parse = function(json_str){
    if (!json_str)
        json_str = '{}';
    // in case it is not a string, make it one
    var stmt = '' + json_str;
    stmt = stmt.replace(/\&quot\;/g, '"');
    var json_obj = JSON.parse(stmt);
    return json_obj;
}


// -------------------------------------------------------------------------
//  Javascript-side XML utilities
// -------------------------------------------------------------------------

// parses an XML string and returns an XML document object ...
spt.parse_xml = function( xml_str )
{
    if ( spt.browser.is_IE() ) {

        xmlDoc=new ActiveXObject("Microsoft.XMLDOM");
        xmlDoc.async="false";
        xmlDoc.loadXML( xml_str );
        return xmlDoc; 
    }
    else {
        parser=new DOMParser();
        xmlDoc=parser.parseFromString( xml_str, "text/xml" );
        return xmlDoc;
    }
}


// -------------------------------------------------------------------------
//  Exception handling functions
// -------------------------------------------------------------------------

spt.exception = {};

spt.exception.handle_fault_response = function( response_text )
{
    if (response_text.match(/\<name\>faultCode\<\/name\>/)) {
        if (response_text.match(/Cannot login with key/)) {
            // handle case where fault response is the result of login authentication expiring ...
            spt.refresh_page();
        }
        else {
            // otherwise, it's an error so just throw an exception with the response text XML ...
            //var m = response_text.match(/\<value\>\<string\>(\w+)\</string\>/);
            console.log(response_text);
            var m = response_text.match(/<value><string>(.*?)<\/string>/);
            var error = m ? m[1] : response_text;
            throw(error);
        }
    }
}


spt.exception.handler = function( ex )
{
    if( spt.get_typeof(ex) == "string" )
    {
        var ex_str = "*** Cannot parse exception string ***";
        if( ex.contains("<?xml version") ) {
            // IE COMPATIBILITY NOTES:
            // -----------------------
            //
            // (1) when getting an XML object node you must use ".getElementsByTagName()" to find child
            //     nodes by tag -- this is the only IE compatible method (you cannot use the singular
            //     version ".getElementByTagName()" -- it doesn't exist on the node)
            //
            // (2) also to get the text value in an XML node you must use ".firstChild.nodeValue" param
            //     in order to be IE compatible (do not use ".textContent" -- this is not available in
            //     IE7)
            //

            var ex_xml_obj = spt.parse_xml(ex);
            var member_node_list = ex_xml_obj.getElementsByTagName('member');
            for( var c=0; c < member_node_list.length; c++ ) {
                var member_node = member_node_list[c];
                var name_node = member_node.getElementsByTagName('name')[0];
                if( name_node.firstChild.nodeValue == 'faultString' ) {
                    var value_node = member_node.getElementsByTagName('value')[0];
                    var string_node = value_node.getElementsByTagName('string')[0];
                    if (string_node.firstChild)
                        ex_str = string_node.firstChild.nodeValue;
                    else
                        ex_str = 'Error'; //usually assert error from server
                }
            }
        }
        else {
            ex_str = ex;
        }
    }
    else {
        //from execute_cmd()
        if (ex.message){
            ex_str = ex.message;
        }
        else if (spt.get_typeof(ex) =='number') {
            ex_str = ex;
            if (ex == 502)
                ex_str = '502 Proxy Error. The request has exceeded the Timeout setting in the Web Server.'
        }
        else {
            spt.js_log.error( "ERROR: currently unable to handle exception of type '" + spt.get_typeof(ex) + "'" );
            ex_str = "*** Unknown exception type ***";
        }
    }

    return ex_str;
}


// -------------------------------------------------------------------------
//  "App Busy" utilities
// -------------------------------------------------------------------------

spt.redraw = function( el )
{
    if( spt.is_hidden(el) ) {
        return;
    }


    el = document.id(el);
    var saved_scroll = el.getScroll();
    el.scrollTo( saved_scroll.x+1, saved_scroll.y+1 );
    el.scrollTo( saved_scroll.x, saved_scroll.y );

}


spt.app_busy = {};

spt.app_busy.msg_block_size = { 'width': 350, 'height': 70 };


spt.app_busy.get_app_busy_container = function()
{
    var app_busy_container = document.id("app_busy_container");
    if( ! app_busy_container ) {

        var body = document.getElement("body");
        var b_dim = spt.get_dimensions( body );

        var cw = b_dim.sz.x;
        var ch = b_dim.sz.y;

        var w = b_dim.scroll_sz.x;
        var h = b_dim.scroll_sz.y;

        app_busy_container = new Element( 'div', {
                'id': 'app_busy_container',
                'styles': {
                    'display': 'none',
                    'position': 'absolute',
                    'top': '-8px',
                    'left': '-8px',
                    'width': w + 8 + 'px',
                    'height': h + 8 + 'px',
                    'z-index': '1000',
                    'background-color': '#777777',
                    'opacity': '.5',
                    'filter': 'alpha(opacity=50)'
                }
        } );

        var top0 = parseInt((ch - spt.app_busy.msg_block_size.height) / 2) + b_dim.scroll.y;
        var left0 = parseInt((cw - spt.app_busy.msg_block_size.width) / 2) + b_dim.scroll.x;

        var app_busy_msg_block = document.id("app_busy_msg_block");
        if (app_busy_msg_block) {
            app_busy_msg_block.setStyle("top", top0+'px');
            app_busy_msg_block.setStyle("left", left0+'px');
        }
        app_busy_container.inject( body, "top" );

        window.addEvent( 'resize', function(e){spt.app_busy.adjust_to_window_resize();} );
        window.addEvent( 'scroll', function(e){spt.app_busy.adjust_to_window_resize();} );
    }

    return app_busy_container;
}


spt.app_busy.show = function( title, msg)
{
    if (!msg) {
        msg = "";
    }

    var app_busy_container = spt.app_busy.get_app_busy_container();
    var app_busy_msg_block = document.id("app_busy_msg_block");

    spt.app_busy.set_msg_title_and_text( title, msg );

    app_busy_container.setStyle("display","");
    if (app_busy_msg_block) 
        app_busy_msg_block.setStyle("display","");

    /*
    if( options && ('use_for_touch_drag' in options) && options.use_for_touch_drag ) {
        app_busy_container.onmousedown = spt.touch_ui.drag.drop_cb_fn;
    } else {
        app_busy_container.onmousedown = spt.touch_ui.drag.do_nothing;
    }
    */

    spt.app_busy.adjust_to_window_resize();

    spt.redraw( app_busy_container );
    spt.redraw( app_busy_msg_block );
   
  
}


spt.app_busy.set_msg_title_and_text = function( title, msg )
{
    var app_busy_msg_block = document.id("app_busy_msg_block");

    var title_span = app_busy_msg_block.getElement(".spt_app_busy_title");
    title_span.innerHTML = title;

    var msg_span = app_busy_msg_block.getElement(".spt_app_busy_msg");
    msg_span.innerHTML = msg;
}


spt.app_busy.hide = function(func)
{
    var hide = function() {
        var app_busy_container = spt.app_busy.get_app_busy_container();
        var app_busy_msg_block = document.id("app_busy_msg_block");

        if (app_busy_msg_block) 
            app_busy_msg_block.setStyle("display","none");
        app_busy_container.setStyle("display","none");
    }

    if (func) 
        setTimeout(function() {func();hide();}, 100);
    else
        hide();
}


spt.app_busy.cancelled = false;
spt.app_busy.is_cancelled = function()
{
    return spt.app_busy.cancelled;
}

spt.app_busy.set_cancelled = function()
{
    spt.app_busy.cancelled = true;
}



spt.app_busy.adjust_to_window_resize = function()
{
    var app_busy_container = document.id("app_busy_container");
    if( spt.is_hidden( app_busy_container ) ) {
        return;
    }

    var body = document.getElement("body");

    var w = body.offsetWidth;
    if( body.scrollWidth > w ) {
        w = body.scrollWidth;
    }
    var h = body.offsetHeight;
    if( body.scrollHeight > h ) {
        h = body.scrollHeight;
    }

    var cw = body.clientWidth;
    var ch = body.clientHeight;

    app_busy_container.setStyle( 'width', (w + 'px') );
    app_busy_container.setStyle( 'height', (h + 'px') );

    var app_busy_msg_block = document.id("app_busy_msg_block");
    var offset = {x: 0, y: -60}
    spt.center_el_in_viewport( app_busy_msg_block , offset );
}


    

spt.print_moo_dimensions = function( el )
{
    el = document.id(el);
    var tag = el.tagName;
    var cls = el.className;
    var id = el.get('id');

    var size = el.getSize();
    var scroll_size = el.getScrollSize();
    var scroll = el.getScroll();
    var position = el.getPosition();
    var coords = el.getCoordinates();

    spt.js_log.debug( " " );

    var title_str = "[" + tag + "] ";
    if( id ) {
        title_str = title_str + "id='" + id + "', ";
    }
    title_str = title_str + "className='" + cls + "' ...";

    spt.js_log.debug( title_str );
    var dashes = [];
    for( var c=0; c < title_str.length; c++ ) {
        dashes.push('-');
    }
    spt.js_log.debug( dashes.join('') );

    spt.js_log.debug( "    size.x, size.y = " + size.x + ", " + size.y );
    spt.js_log.debug( "    scroll_size.x, scroll_size.y = " + scroll_size.x + ", " + scroll_size.y );
    spt.js_log.debug( "    scroll.x, scroll.y = " + scroll.x + ", " + scroll.y );
    spt.js_log.debug( "    position.x, position.y = " + position.x + ", " + position.y );
    spt.js_log.debug( "    coordinates:" );
    spt.js_log.debug( "        top = " + coords.top );
    spt.js_log.debug( "        left = " + coords.left );
    spt.js_log.debug( "        width = " + coords.width );
    spt.js_log.debug( "        height = " + coords.height );
    spt.js_log.debug( "        right = " + coords.right );
    spt.js_log.debug( "        bottom = " + coords.bottom );
    spt.js_log.debug( " " );
}


spt.get_dimensions = function( el )
{
    var size = el.getSize();
    var scroll_size = el.getScrollSize();
    var scroll = el.getScroll();
    var position = el.getPosition();
    var coords = el.getCoordinates();

    var dim = {};

    dim.sz = { 'x': size.x, 'y': size.y };
    dim.scroll_sz = { 'x': scroll_size.x, 'y': scroll_size.y };
    dim.scroll = { 'x': scroll.x, 'y': scroll.y };
    dim.pos = { 'x': position.x, 'y': position.y };
    dim.coords = {
        't': coords.top,
        'l': coords.left,
        'w': coords.width,
        'h': coords.height,
        'r': coords.right,
        'b': coords.bottom
    };

    return dim;
}


spt.center_el_in_viewport = function( el, offset)
{
    var body = document.getElement('body');

    var e_dim = spt.get_dimensions( el );
    var b_dim = spt.get_dimensions( body );

    var vp_top = 10;
    if( b_dim.sz.y > (e_dim.sz.y + 20) ) {
        vp_top = parseInt((b_dim.sz.y - e_dim.sz.y) / 2);
    }

    var vp_left = 10;
    if( b_dim.sz.x > (e_dim.sz.x + 20) ) {
        vp_left = parseInt((b_dim.sz.x - e_dim.sz.x) / 2);
    }

    var new_top = b_dim.scroll.y + vp_top;
    var new_left = b_dim.scroll.x + vp_left;

    if (offset) {
        new_top = new_top + offset.y;
        new_left = new_left + offset.x;
    }
    el.setStyle('top', new_top+'px');
    el.setStyle('left', new_left+'px');
}


// -------------------------------------------------------------------------
//  More element utilities ...
// -------------------------------------------------------------------------

spt.get_el_attribute_map = function( el )
{
    el = document.id(el);
    var attr_map = {};
    var attrs = el.attributes;
    for( var c=0; c < attrs.length; c++ ) {
        var attr_name = attrs[c].name;
        if( attr_name in { 'class':'class', 'style':'style', 'id':'id' } ) {
            continue;
        }
        var value = el.getAttribute(attr_name);
        if( spt.get_typeof(value) != "string" || ! value || value.indexOf("function(") == 0 ) {
            continue;
        }
        attr_map[ attr_name ] = value;
    }

    return attr_map;
}



// -------------------------------------------------------------------------
//  Widget utility functions ...
// -------------------------------------------------------------------------

spt.widget = {};

spt.widget.btn_wdg = {};

spt.widget.btn_wdg.set_btn_width = function( btn_top_el )
{
    var div_list = btn_top_el.getElements('div');
    var total_width = 0;
    for( var c=0; c < div_list.length; c++ ) {
        var div_el = div_list[c];
        var w = spt.get_render_display_width( div_el );
        total_width = total_width + w;
    }
    btn_top_el.setStyle("width", (total_width + 1) + "px");
}


// ---------------------------------------------------------------------------
//  Click-off checking utility funcitons ...
// ---------------------------------------------------------------------------

spt.click_off = {}

spt.click_off.fire_click_off_cbk = function( evt )
{
    spt.named_events.fire_event( 'APP_CLICK_OFF_EVENT', { 'options': {'click_target': spt.get_event_target(evt)} } );
}

spt.click_off.check = function( listen_bvr )
{
    if( spt.is_hidden( listen_bvr.src_el ) ) {
        return;
    }

    var click_target = listen_bvr.firing_data.click_target;

    var click_off_top = null;
    // not using MooTools .hasClass() here for IE compatibility reasons ...
    if( click_target.className && click_target.className.contains_word ) {
        if( click_target.className.contains_word( "APP_CLICK_OFF_TOP_EL" ) ) {
            click_off_top = click_target;
        }
    }

    if( ! click_off_top ) {
        click_off_top = click_target.getParent(".APP_CLICK_OFF_TOP_EL");
    }

    if( click_off_top ) {
        // we've clicked within the containing element of this listener, so it's not a "click-off", so
        // just ignore ...
        return;
    }

    if( listen_bvr.cbjs_click_off ) {
        spt.behavior.run_cbjs(  listen_bvr.cbjs_click_off, listen_bvr, {}, {} );
    }
}



// -------------------------------------------------------------------------------------------------------------------
//  Global variable needed for allowing child elements to force the default context menu when a
//  parent (or ancestor) element has a right click context menu override
// -------------------------------------------------------------------------------------------------------------------

spt.force_default_context_menu = false;



// -------------------------------------------------------------------------------------------------------------------
//  Javascript eval() error output utility
// -------------------------------------------------------------------------------------------------------------------

spt.log_eval_error = function( js_error, js_str, calling_function_str, extra_error_msg )
{
    spt.js_log.error( "___________________________________________________________________________________________" );
    spt.js_log.error( "Caught javascript ERROR: " + js_error );
    spt.js_log.error( "   [error occurred on call to 'eval()' in '" + calling_function_str + "()' function]" );
    if( extra_error_msg ) {
        spt.js_log.error( "   [" + extra_error_msg + "]" );
    }
    spt.js_log.error( "..........................................................................................." );
    spt.js_log.error( " " );
    spt.js_log.error( js_str );
    spt.js_log.error( " " );
    spt.js_log.error( "___________________________________________________________________________________________" );
}



// -------------------------------------------------------------------------
//  Path functions
// -------------------------------------------------------------------------

spt.path = {};

spt.path.get_basename = function(file_path) {
    //in case it's a dir, remove trailing slashes
    if (!file_path) {
        spt.alert("file_path is undefined, returning '' basename.");
        return '';
    }
    file_path = file_path.replace(/[\/\\]+$/, '');
    var parts = file_path.split(/[\/\\]/);
    var basename = parts[parts.length-1];
    return basename;
}

spt.path.get_dirname = function(file_path) {
    //in case it's a dir, remove trailing slashes
    if (!file_path) {
        spt.alert("file_path is undefined, returning '' directory name.");
        return '';
    }
    file_path = file_path.replace(/[\/\\]+$/, '');
    var parts = file_path.split(/[\/\\]/);
    parts.pop();
    return parts.join('/');
}

spt.path.get_filesystem_name = function(file_name) {
    file_name = file_name.replace(/[\s\/\|:=?]/g, "_");
    //lowercase the extension if applicable
    if (file_name.test(/\./)){
        var index = file_name.lastIndexOf('.');
        var ext = file_name.substring(index, file_name.length);
        ext = ext.toLowerCase();
        file_name = file_name.substring(0, index) + ext;
    }
    return file_name
}

spt.path.get_filesystem_path = function(file_path){
    var basename = spt.path.get_basename(file_path);
    var updated_file_name = spt.path.get_filesystem_name(basename);
    var m = file_path.match(/(.*)[\/\\]([^\/\\]+\.\w+)$/);
    if (m) {
        var base_dir = m[1];
        return base_dir + '/' + updated_file_name;
    }
    else {
        return file_path;
    }
}

// -------------------------------------------------------------------------
//  Tool Tips
// -------------------------------------------------------------------------
spt.Tips = function() {};
spt.Tips._tip = {};
spt.Tips.get = function(key) {
    if (key)
        return this._tip[key];
    else
    	return this._tip;
}

spt.Tips.set = function(key, tip_dict) {
    
    this._tip[key] = tip_dict;
}

spt.split_search_key = function(search_key) {
        
        var list = [];
        if (!search_key)
            return search_key;

        if (search_key.test(/&/))
            var tmps = search_key.split('&');
        else
            var tmps = search_key.split('?');
        var codes = tmps[1].split('=')
        //assert len(codes) == 2;
        list.push(tmps[0]);
        list.push(codes[1]);
        return list;
}






spt.file = {}

spt.file.expand_paths = function(path, file_range)
{
    //file_range = '1-100/3';
    //path = "/home/apache/frame####.png";

    parts = file_range.split(/[-\/]/);
    var start_frame = parts[0];
    start_frame = parseInt(start_frame);
    var end_frame = parts[1];
    end_frame = parseInt(end_frame);

    var by_frame;
    if (parts.length == 3) {
        by_frame = parts[2];
        by_frame = parseInt(by_frame);
    }
    else {
        by_frame = 1;
    }


    var start = path.indexOf("#");
    var end = path.lastIndexOf("#");
    var length = end - start + 1;

    var expanded_paths = [];

    for (var i = start_frame; i <= end_frame; i += by_frame) {

        var num = spt.zero_pad(i, length);

        expanded_path = path.replace(/#+/, num);
        expanded_paths.push(expanded_path);
    }

    return expanded_paths;

}

spt.url = {}

// check if a url file exists 
spt.url.exists = function(url){
    var request = window.XMLHttpRequest ? new XMLHttpRequest() : new ActiveXObject("Microsoft.XMLHTTP"); 
    request.open("HEAD", url, false);
    request.send();
    return (request.status==404) ? false : true;
}    





 

// dom function
//
spt.dom = {}
spt.dom.loaded_js = {};
spt.dom.load_js = function(js_files, cbk) {

        if (!cbk) cbk = function() {};
       
        var head = document.getElementsByTagName("head")[0];
        for (var i = 0; i < js_files.length; i++) {
            var js_file = js_files[i];
            // use full path if it's starting with /
            var url;
            if (js_file.substr(0,4) == "http") {
                url = js_file;
            } else if (js_file.substr(0,1) == "/") {
                url = js_file;
            } else {
                url = js_file.test(/^\//) ? js_file : "/context/spt_js/" + js_file;
            }

            if (spt.dom.loaded_js[url] == true) {
                cbk();
                continue;
            }
            var js_el = document.createElement("script");
            js_el.setAttribute("type", "text/javascript");
            js_el.setAttribute("src", url);

            head.appendChild(js_el);

            if (js_el.readyState) {
                js_el.onreadystatechange = function() {
                if ( js_el.readyState == "loaded"  || js_el.readyState == 'complete' ) {
                    js_el.onreadystatechange = null; 
                    cbk();
                    spt.dom.loaded_js[url] = true;
                }
                };
            } else {

                js_el.onload = function() {
                    cbk();
                    spt.dom.loaded_js[url] = true;
                };
                
            }
        }
        

    };

spt.command = {}


// store a list of commands that have been executed
spt.command.commands = [];
spt.command.command_index = -1;
spt.command.execute_cmd = function(cmd) {
    cmd.execute();
}


spt.command.add_to_undo = function(cmd) {
    for (var i=spt.command.commands.length;i>spt.command.command_index+1;i--) {
        spt.command.commands.pop();
    }

    spt.command.commands.push(cmd);
    spt.command.command_index += 1;
}


spt.command.undo_last = function() {
    if (spt.command.command_index == -1) {
        alert("Nothing to undo");
        return;
    }
    
    var cmd = spt.command.commands[spt.command.command_index];
    cmd.undo();
    spt.command.command_index -= 1;

    return cmd
    
}


spt.command.redo_last = function() {

    if (spt.command.command_index == spt.command.commands.length-1) {
        alert("Nothing to redo");
        return;
    }

    var cmd = spt.command.commands[spt.command.command_index+1];
    cmd.redo();
    spt.command.command_index += 1;
    return cmd
    
}



spt.command.undo_all = function() {
    for (var i = spt.command.commands.length-1; i >= 0; i--) {
        var cmd = spt.command.commands[i];
        cmd.undo();
    }
}


spt.command.test = function() {
    for (var i=0; i < 5; i++) {
        var cmd = new spt.command.command();
        spt.command.execute_cmd(cmd);
    }

    // undo all of the commands
    spt.command.undo_all()

}

spt.command.clear = function(){
	spt.command.commands = [];
    spt.command.command_index = -1;
}

