###########################################################
#
# Copyright (c) 2010, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#
__all__ = ["DynByFoundValueSmartSelectWdg"]

from pyasm.biz import ExpressionParser

from pyasm.web import DivWdg, HtmlElement, SpanWdg, Table, WebContainer
from pyasm.widget import SelectWdg, WidgetConfig, IconWdg

from tactic.ui.common import BaseRefreshWdg


class DynByFoundValueSmartSelectWdg(BaseRefreshWdg):

    def get_args_keys(my):
        return {
        }


    def init(my):

        list_item_table = ''
        my.full_item_list = []
        if my.kwargs.has_key( 'list_item_table' ):
            list_item_table = my.kwargs.get( 'list_item_table' )
            expr = '@SOBJECT(MMS/%s)' % list_item_table
            parser = ExpressionParser()
            my.full_item_list = parser.eval(expr)

        my.el_name = ''
        if my.kwargs.has_key( 'element_name' ):
            my.el_name = my.kwargs.get( 'element_name' )

        my.input_el_name = ''
        if my.kwargs.has_key( 'input_element_to_find' ):
            my.input_el_name = my.kwargs.get( 'input_element_to_find' )

        my.col_to_match = ''
        if my.kwargs.has_key( 'column_to_match_value' ):
            my.col_to_match = my.kwargs.get( 'column_to_match_value' )

        my.col_for_label = ''
        if my.kwargs.has_key( 'column_for_label' ):
            my.col_for_label = my.kwargs.get( 'column_for_label' )

        my.select_element = HtmlElement('select')


    def force_default_context_menu(my):
        pass


    def add_behavior(my, bvr):
        my.select_element.add_behavior( bvr )


    def add_no_option(my, sel_el):
        option = HtmlElement('option')
        option.set_attr( "value", "" )
        option.add( "-- No Options Found --" )
        sel_el.add( option )

        option = HtmlElement('option')
        option.set_attr( "value", "" )
        no_value_label = "-- No Filter Value Found --"
        if my.kwargs.get('no_value_found_label'):
            no_value_label = my.kwargs.get('no_value_found_label')
        option.add( no_value_label )
        sel_el.add( option )


    def get_display(my):
        
        sel_el = my.select_element

        sel_el.add_class("inputfield")
        sel_el.add_class("spt_input")
        sel_el.set_attr("name", my.el_name)

        # NOTE: make this javascript dynamic (much less effecient), but need
        # to isolate for now and will optimize if necessary
        sel_el.add_behavior( {
            'type': 'load',
            'cbjs_action': my.get_onload_js()
        } )



        options_arr = []

        '''
        my.add_no_option( sel_el )
        '''
        options_arr.append( "||%s" % ("-- No Options Found --") )
        no_value_label = "-- No Filter Value Found --"
        if my.kwargs.get('no_value_found_label'):
            no_value_label = my.kwargs.get('no_value_found_label')
        options_arr.append( "||%s" % (no_value_label) )

        if my.full_item_list and my.el_name and my.input_el_name and my.col_to_match and my.col_for_label:
            for item in my.full_item_list:
                '''
                option = HtmlElement('option')
                label = item.get_value(my.col_for_label)
                option.set_attr( "value", label )
                option.add( label )

                option.add_class( "match_%s" % item.get_value( my.col_to_match ) )

                sel_el.add( option )
                '''
                match_tag = item.get_value( my.col_to_match )
                label = item.get_value(my.col_for_label)
                options_arr.append( "%s|%s|%s" % (match_tag, label, label) )
                pass

        sel_el.set_attr("spt_smart_select_options", '###'.join(options_arr))
        sel_el.add_event("onfocus","spt.smart_select.find_match_value_in_tbody(this,'%s');" % my.input_el_name)
        return sel_el



    def get_onload_js(my):

        return r'''

spt.smart_select = {};

spt.smart_select.find_match_value_in_tbody = function( select_el, element_to_find ) 
{
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
        '''



