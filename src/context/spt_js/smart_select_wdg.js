// -------------------------------------------------------------------------------------------------------------------
//
//   Copyright (c) 2010, Southpaw Technology Inc., All Rights Reserved
//   
//   PROPRIETARY INFORMATION.  This software is proprietary to Southpaw Technology Inc., and is not to be
//   reproduced, transmitted, or disclosed in any way without written permission.
//   
// -------------------------------------------------------------------------------------------------------------------


spt.smart_select = {};

spt.smart_select.find_match_value_in_tbody = function( select_el, element_to_find ) 
{
    alert("smart_select.js is Deprecated");
    select_el = $(select_el);

    // first clear all the options ...
    var option_el_list = select_el.getElements("option");
    for( var c=0; c < option_el_list.length; c++ ) {
        select_el.removeChild( option_el_list[c] );
    }

    var tbody = select_el.getParent('.spt_table_tbody');
    var td_list = tbody.getElements('.spt_table_td');
    var input_value = '';
    for( var c=0; c < td_list.length; c++ ) {
        var td = td_list[c];
        var element_name = td.getProperty("spt_element_name");
        if( element_name == element_to_find ) {
            input_value = td.getProperty("spt_input_value");
            break;
        }
    }

    if( ! ('spt_options_info_list' in select_el) ) {
        select_el.spt_options_info_list = [];
        var spt_options_str = select_el.getProperty("spt_smart_select_options");
        var opts = spt_options_str.split("###");
        for( var c=0; c < opts.length; c++ ) {
            var bits = opts[c].split("|");
            var match_tag = bits[0];
            var value = bits[1];
            var label = bits[2];
            select_el.spt_options_info_list.push( { 'match_tag': match_tag, 'value': value, 'label': label } );
        }
        select_el.removeProperty('spt_smart_select_options');
    }

    var spt_options = select_el.spt_options_info_list;

    if( ! input_value || input_value == "[]" ) {
        // No value found ...
        var option = document.createElement("option");
        option.setAttribute("value","");

        option.innerHTML = spt_options[1].label;
        select_el.appendChild( option );
        select_el.setProperty("size","2");
    }
    else {
        // gather list of matches ...
        var matched_idx_list = [];
        for( var c=0; c < spt_options.length; c++ ) {
            var match_tag = spt_options[c].match_tag;
            var value = spt_options[c].value;
            var label = spt_options[c].label;

            if( match_tag == input_value ) {
                matched_idx_list.push( c );
            }
        }

        if( ! matched_idx_list.length ) {
            // No options found ...
            var option = document.createElement("option");
            option.setAttribute("value","");
            option.innerHTML = spt_options[0].label;
            select_el.appendChild( option );
            select_el.setProperty("size","2");
        } else {
            for( var c=0; c < matched_idx_list.length; c++ ) {
                var idx = matched_idx_list[c];
                var opt_map = spt_options[ idx ];

                var option = document.createElement("option");
                option.setAttribute("value", "" + opt_map.value);
                option.innerHTML = opt_map.label;
                select_el.appendChild( option );
            }
            var matched_len = matched_idx_list.length;
            if( matched_len < 2 ) {
                matched_len = 2;
            }
            select_el.setProperty("size","" + matched_idx_list.length);
        }
    }

    if( spt.browser.is_IE() ) {
        spt.smart_select.set_size_for_IE( select_el );
    }
}


spt.smart_select.set_size_for_IE = function( select_el )
{
    alert("smart_select.js is Deprecated");
    var mult = 15;
    var td = select_el.getParent(".spt_table_td");
    var size = td.getSize()

    if( spt.browser.is_IE() ) {
        if (size.y < (input.size * mult)) {
            edit_wdg.setStyle( "height", (input.size * mult) + 'px');
        }
        else {
            edit_wdg.setStyle( "height", size.y+'px');
        }
    }

    if( size.x < 200 ) {
        select_el.setStyle("width","200px");
    }
}


