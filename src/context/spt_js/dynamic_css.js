// -------------------------------------------------------------------------------------------------------------------
//
//   Copyright (c) 2009, Southpaw Technology Inc., All Rights Reserved
//   
//   PROPRIETARY INFORMATION.  This software is proprietary to Southpaw Technology Inc., and is not to be
//   reproduced, transmitted, or disclosed in any way without written permission.
//   
// -------------------------------------------------------------------------------------------------------------------


spt.css = {};


/** 
* Converts HSV to RGB value. 
* 
* @param {Integer} h Hue as a value between 0 - 360 degrees 
* @param {Integer} s Saturation as a value between 0 - 100 % 
* @param {Integer} v Value as a value between 0 - 100 % 
* @returns {Array} The RGB values  EG: [r,g,b], [255,255,255] 
*/  
spt.css.hsv_to_rgb = function(h,s,v) {  
  
    var s = s / 100,  
         v = v / 100;  
  
    var hi = Math.floor((h/60) % 6);  
    var f = (h / 60) - hi;  
    var p = v * (1 - s);  
    var q = v * (1 - f * s);  
    var t = v * (1 - (1 - f) * s);  
  
    var rgb = [];  
  
    switch (hi) {  
        case 0: rgb = [v,t,p];break;  
        case 1: rgb = [q,v,p];break;  
        case 2: rgb = [p,v,t];break;  
        case 3: rgb = [p,q,v];break;  
        case 4: rgb = [t,p,v];break;  
        case 5: rgb = [v,p,q];break;  
    }  
  
    var r = Math.min(255, Math.round(rgb[0]*256)),  
        g = Math.min(255, Math.round(rgb[1]*256)),  
        b = Math.min(255, Math.round(rgb[2]*256));  
  
    //return [r,g,b];  
    return {r:r, g:g, b:b};
  
}     
  
/** 
* Converts RGB to HSV value. 
* 
* @param {Integer} r Red value, 0-255 
* @param {Integer} g Green value, 0-255 
* @param {Integer} b Blue value, 0-255 
* @returns {Array} The HSV values EG: [h,s,v], [0-360 degrees, 0-100%, 0-100%] 
*/  
spt.css.rgb_to_hsv = function(r, g, b) {  
  
    var r = (r / 255),  
         g = (g / 255),  
     b = (b / 255);   
  
    var min = Math.min(Math.min(r, g), b),  
        max = Math.max(Math.max(r, g), b),  
        delta = max - min;  
  
    var value = max,  
        saturation,  
        hue;  
  
    // Hue  
    if (max == min) {  
        hue = 0;  
    } else if (max == r) {  
        hue = (60 * ((g-b) / (max-min))) % 360;  
    } else if (max == g) {  
        hue = 60 * ((b-r) / (max-min)) + 120;  
    } else if (max == b) {  
        hue = 60 * ((r-g) / (max-min)) + 240;  
    }  
  
    if (hue < 0) {  
        hue += 360;  
    }  
  
    // Saturation  
    if (max == 0) {  
        saturation = 0;  
    } else {  
        saturation = 1 - (min/max);  
    }  
 
    var h = Math.round(hue);
    var s = Math.round(saturation * 100);
    var v = Math.round(value * 100);  
    return {h:h, s:s, v:v};
    //return [Math.round(hue), Math.round(saturation * 100), Math.round(value * 100)];  
}  


// Calculate a color for a modifier

spt.css.modify_color_value = function(color, modifier) {
    var rgb = spt.css.get_color_rgb_values( color );
    var hsv = spt.css.rgb_to_hsv(rgb.r, rgb.g, rgb.b);
    var diff = 256*modifier/100;
    hsv.v = hsv.v + diff;
    var rgb = spt.css.hsv_to_rgb( hsv.h, hsv.s, hsv.v );
    return "rgb(" + rgb.r + "," + rgb.g + "," + rgb.b + ")";
}



spt.css.convert_hex_to_rgb_obj = function( hex_color_value )
{
    hex_color_value = hex_color_value.toUpperCase();

    var hex_map = { '0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
                    'A': 10, 'B': 11, 'C': 12, 'D': 13, 'E': 14, 'F': 15 };

    hex_clr = hex_color_value.strip().replace( /^\#/, '' );

    var r = 0;
    var g = 0;
    var b = 0;

    if( hex_clr.length == 3 ) {
        r = hex_map[ hex_clr.charAt(0) ] * 16 + hex_map[ hex_clr.charAt(0) ];
        g = hex_map[ hex_clr.charAt(1) ] * 16 + hex_map[ hex_clr.charAt(1) ];
        b = hex_map[ hex_clr.charAt(2) ] * 16 + hex_map[ hex_clr.charAt(2) ];
    }
    else if( hex_clr.length == 6 ) {
        r = hex_map[ hex_clr.charAt(0) ] * 16 + hex_map[ hex_clr.charAt(1) ];
        g = hex_map[ hex_clr.charAt(2) ] * 16 + hex_map[ hex_clr.charAt(3) ];
        b = hex_map[ hex_clr.charAt(4) ] * 16 + hex_map[ hex_clr.charAt(5) ];
    }
    else {
        log.warning( "WARNING: [spt.css.convert_to_rgb_obj] unable to convert hex color (#" + hex_clr + ") that has " +
                        hex_clr.length + " hex digits ... returning { 'r': 0, 'g': 0, 'b': 0 }" );
    }

    return { 'r': r, 'g': g, 'b': b };
}


spt.css.convert_hex_to_rgb_str = function( hex_color_value )
{
    var rgb = spt.css.convert_hex_to_rgb_obj( hex_color_value );
    return "rgb(" + rgb.r + "," + rgb.g + "," + rgb.b + ")";
}


spt.css.get_color_rgb_values = function( color_value )
{
    if( color_value.match( /^\#/ ) ) {
        // convert to rgb object and return it ...
        return spt.css.convert_hex_to_rgb_obj( color_value );
    }
    color_value = color_value.replace( /delta_rgb\(/, '' ).replace( /rgb\(/, '' ).replace( /\)/, '' ).strip();
    var color = {};

    var bits = color_value.split(",");
    color.r = Number( bits[0] );
    color.g = Number( bits[1] );
    color.b = Number( bits[2] );

    return color;
}


spt.css.apply_style_mods = function( style_mods_map, target_el )
{
    target_el = $(target_el);

    for( var style in style_mods_map ) {
        if( ! style_mods_map.hasOwnProperty( style ) ) { continue; }
        var value = style_mods_map[ style ];

        if( style.match( /\-color$/ ) && value.match( /^delta_rgb\(/ ) ) {
            var delta = spt.css.get_color_rgb_values( value );
            var el_rgb_str = target_el.getComputedStyle( style );

            if( el_rgb_str == 'transparent' ) {
                var done = false;
                var el = target_el;
                while( ! done ) {
                    el_rgb_str = null;
                    var el = el.parentNode;
                    if( ! el ) {
                        done = true;
                        continue;
                    }
                    el_rgb_str = el.getComputedStyle( style );
                    if( el_rgb_str.match( /^rgb\(/ ) ) {
                        done = true;
                        continue;
                    }
                }
            }
            if( ! el_rgb_str ) {
                log.warning( "WARNING: [spt.css.apply_style_mods] unable to find computed color for '" + style +
                             "' style." );
                continue;
            }

            var rgb = spt.css.get_color_rgb_values( el_rgb_str );
            rgb.r = rgb.r + delta.r;
            rgb.g = rgb.g + delta.g;
            rgb.b = rgb.b + delta.b;

            value = "rgb(" + rgb.r + "," + rgb.g + "," + rgb.b + ")";
        }
        target_el.setStyle( style, value );
    }
}


spt.css.get_style_bkups = function( mod_styles_map, el )
{
    var style_bkups_map = {};

    for( var style in mod_styles_map ) {
        if( ! mod_styles_map.hasOwnProperty( style ) ) { continue; }

        var real_style_arr = [];
        var do_cap = false;
        for( var c=0; c < style.length; c++ ) {
            if( style.charAt(c) == '-' ) {
                do_cap = true;
            } else {
                if( do_cap ) {
                    real_style_arr.push( style.charAt(c).toUpperCase() );
                    do_cap = false;
                } else {
                    real_style_arr.push( style.charAt(c) );
                }
            }
        }
        var real_style = real_style_arr.join('');
        var bkup_style_value = '';

        var stmt = 'bkup_style_value = el.style.' + real_style + ';';

        eval( stmt );
        if( bkup_style_value ) {
            style_bkups_map[ style ] = bkup_style_value;
        } else {
            style_bkups_map[ style ] = '';
        }
    }

    return style_bkups_map;
}


spt.css.get_el_style_map = function( el )
{
    el = $(el);
    var style_string = el.style.cssText;
    return spt.css.get_mod_styles_map( style_string );
}


spt.css.get_mod_styles_map = function( mod_styles_str )
{
    var bits = mod_styles_str.split(";");
    var mod_styles_map = {};

    for( var c=0; c < bits.length; c++ ) {
        var mod = bits[c];
        if( mod.indexOf(":") != -1 ) {
            var pair = mod.split(":");
            var style = pair[0].strip().toLowerCase();
                // make sure style is in lower-case! Otherwise MooTools ".setStyle()" method will not work properly
            var value = pair[1].strip();
            mod_styles_map[ style ] = value;
        }
    }

    return mod_styles_map;
}


spt.css.copy_styles =  function( from_el, to_el, override_styles_str )
{
    var styles_to_copy = spt.css.get_el_style_map( from_el );
    for( var style in styles_to_copy ) {
        if( ! styles_to_copy.hasOwnProperty(style) ) { continue; }
        to_el.setStyle( style, styles_to_copy[style] );
    }

    if( override_styles_str ) {
        var style_map = spt.get_style_map_from_str( override_styles_str );
        for( var style in style_map ) {
            if( ! style_map.hasOwnProperty(style) ) { continue; }
            to_el.setStyle( style, style_map[style] );
        }
    }
}


spt.css.has_look = function( look_to_check, el )
{
    if( el.hasClass( "look_" + look_to_check ) ) {
        return true;
    }
    return false;
}


spt.css.add_looks = function( looks_to_add, target_el )
{
    if( ! looks_to_add ) {
        return [];
    }

    var in_type = spt.get_typeof(looks_to_add);
    var looks = null;

    var looks_added = [];

    if( in_type == 'array' ) {
        looks = looks_to_add;
    }
    else if( in_type == 'string' ) {
        looks = looks_to_add.split(/\s+/);
    } else {
        log.error( "ERROR: [spt.css.add_looks] '" + in_type + "' is not supported for looks_to_add argument." );
        return [];
    }

    for( var c=0; c < looks.length; c++ ) {
        var look = looks[c].strip();
        if( look ) {
            var cls = "look_" + look;
            if( 'className' in target_el ) {
                // IE compatibility note: when dealing with an event target you are unable to use
                //                        MooTools methods ... so you cannot use ".hasClass()" and
                //                        ".addClass()" object methods ... so here we use raw Element
                //                        node properties ...
                if( ! target_el.className.contains_word(cls) ) {
                    spt.add_class( target_el, cls );
                    looks_added.push( look );
                }
            }
        }
    }

    return looks_added;
}


spt.css.remove_looks = function( looks_list, target_el )
{
    if( spt.get_typeof(looks_list) == 'string' ) {
        looks_list = looks_list.split(/\s+/);
    }
    if( ! looks_list ) {
        return;
    }

    for( var c=0; c < looks_list.length; c++ ) {
        var look = looks_list[c].strip();
        if( look ) {
            // see "IE compatibility note" above in 'spt.css.add_looks()' for more info
            var cls = "look_" + look;
            spt.remove_class( target_el, cls );
        }
    }
}


spt.css.reapply_hover = function( el )
{
    var hover_bvr_list = spt.behavior.get_bvrs_by_type( "hover", el );
    for( var c=0; c < hover_bvr_list.length; c++ ) {
        var h_bvr = hover_bvr_list[c];
        if( h_bvr._looks_added ) {
            spt.css.remove_looks( h_bvr._looks_added, el );
            delete h_bvr._looks_added;
            h_bvr._looks_added = spt.css.add_looks( h_bvr.add_looks, el );
        }
        if( h_bvr._styles_to_restore ) {
            spt.css.apply_style_mods( h_bvr._styles_to_restore, el );
            delete h_bvr._styles_to_restore;
            h_bvr._styles_to_restore = spt.css.get_style_bkups( h_bvr.mod_styles, el );
            spt.css.apply_style_mods( h_bvr.mod_styles, el );
        }
    }
}


spt.css._select_core = function( operation, el )
{
    var select_bvr_list = spt.behavior.get_bvrs_by_type( "select", el );
    if( ! select_bvr_list || select_bvr_list == 0 ) {
        log.error( "ERROR: [spt.css.select] No 'select' type behavior found on element ... aborting select. " +
                    "Element is ..." );
        log.error( el );
        return;
    }

    var is_selected = false;
    if( el.hasClass("SPT_SELECTED") ) {
        is_selected = true;
    }

    if( is_selected && operation == 'select' ) { return; }
    if( ! is_selected && operation == 'deselect' ) { return; }

    if( operation == 'toggle' ) {
        if( is_selected ) {
            operation = 'deselect';
        } else {
            operation = 'select';
        }
    }

    var bvr = select_bvr_list[0];  // should only be one select behavior on the element
    if( bvr.mod_styles ) {
        if( operation == 'select' ) {
            bvr._styles_to_restore = spt.css.get_style_bkups( bvr.mod_styles, el );
            spt.css.apply_style_mods( bvr.mod_styles, el );
            el.addClass("SPT_SELECTED");
        } else {
            // otherwise 'deselect' ...
            spt.css.apply_style_mods( bvr._styles_to_restore, el );
            delete bvr._styles_to_restore;
            el.removeClass("SPT_SELECTED");
        }
    }
    else if( bvr.add_looks ) {
        if( operation == 'select' ) {
            bvr._looks_added = spt.css.add_looks( bvr.add_looks, el );
            el.addClass("SPT_SELECTED");
        } else {
            // otherwise 'deselect' ...
            spt.css.remove_looks( bvr._looks_added, el );
            delete bvr._looks_added;
            el.removeClass("SPT_SELECTED");
        }
    }
    // This uses background setting on css as opposed to css classes.
    // This method is better suited for the palette system which determines
    // the color without using css files/definitions
    else if( bvr.add_color ) {
        if( operation == 'select' ) {
            //bvr._looks_added = spt.css.add_looks( bvr.add_looks, el );
            el.setAttribute("spt_last_background", el.getAttribute("spt_background") );
            el.setStyle("background", bvr.add_color);
            el.setAttribute("spt_background", bvr.add_color );
            el.addClass("SPT_SELECTED");
        } else {
            // otherwise 'deselect' ...
            //spt.css.remove_looks( bvr._looks_added, el );
            var last_background = el.getAttribute("spt_last_background");
            el.setStyle("background", last_background );
            el.setAttribute("spt_background", last_background );
            el.removeClass("SPT_SELECTED");
        }
    }



    spt.css.reapply_hover( el );
}



spt.css.deselect = function( el )
{
    spt.css._select_core( 'deselect', $(el) );
}



spt.css.select = function( el )
{
    spt.css._select_core( 'select', $(el) );
}



spt.css.toggle_select = function( el )
{
    spt.css._select_core( 'toggle', $(el) );
}



