// -------------------------------------------------------------------------------------------------------------------
//
//   Copyright (c) 2010, Southpaw Technology Inc., All Rights Reserved
//   
//   PROPRIETARY INFORMATION.  This software is proprietary to Southpaw Technology Inc., and is not to be
//   reproduced, transmitted, or disclosed in any way without written permission.
//   
// -------------------------------------------------------------------------------------------------------------------


spt.validation = {};



spt.validation.onchange_cbk = function( evt, bvr )
{
    // assumes bvr.src_el is the input or select element that directly has a validation behavior
    var input_el = bvr.src_el;
    spt.validation.direct_input_element_check( input_el );
}


spt.validation.direct_input_element_check = function( input_el )
{
    var v_bvr_list = spt.behavior.get_bvrs_by_type( "validation", input_el );
    return spt.validation.check( input_el.value, v_bvr_list, input_el );
}


spt.validation.check = function( new_value, validation_bvr_list, display_target_el )
{
    if( ! validation_bvr_list || validation_bvr_list.length == 0 ) {
        return true;
    }

    var valid_flag = true;
    var v_msg = '';
    for( var c=0; c < validation_bvr_list.length; c++ ) {
        var v_bvr = validation_bvr_list[c];
        var v_js = v_bvr.cbjs_validation;
        if( v_js ) {
            var v_result = spt.validation._run_cbjs( v_js, new_value, display_target_el, v_bvr );

            if( v_result == null ) {
                // means an error occurred running the validation script!
                v_msg = 'ERROR running validation script ... see Web Client Output Log Console for details';
                valid_flag = false;
            } else {
                valid_flag = v_result;
                if( v_bvr.validation_warning ) {
                    v_msg = v_bvr.validation_warning;
                } else {
                    v_msg = "Entry not valid";
                }
            }
        }
    }
    if( ! valid_flag  ) {
        spt.validation.set_invalid_warning( display_target_el, v_msg );
        display_target_el.setAttribute( "title", v_msg );
    } else {
        spt.validation.clear_invalid_warning( display_target_el );
    }

    var table_top = display_target_el.getParent(".spt_table");
    // don't change color for table tds
    if (!table_top) {
        if (!valid_flag)
            display_target_el.setStyle('background','#A99');
        else
            display_target_el.setStyle('background','white');

    }
    // Special handling for Edit Panel ...
    //
    //
    var edit_top = display_target_el.getParent(".spt_edit_top");
    if( edit_top ) {

        // get insert button ...
        var btn_list = edit_top.getElements(".spt_button_top");
        var insert_btn = null;
        for( var c=0; c < btn_list.length; c++ ) {
            var btn = btn_list[c];
            var btn_label = btn.getElement('.spt_label').getProperty("spt_text_label");
            if( btn_label && ['Insert', 'Edit', 'Add', 'Save'].contains(btn_label) ) {
                insert_btn = btn;
                break;
            }
        }

        if( insert_btn ) {
            var failed_list = edit_top.getElements(".spt_input_validation_failed");
            if( failed_list.length ) {
                insert_btn.setStyle("visibility","hidden");
            } else {
                insert_btn.setStyle("visibility","visible");
            }

        }
    }

    return valid_flag;
}


spt.validation.has_invalid_entries = function( start_el, top_mt_search_str )
{
    var top_el = $(start_el).getParent( top_mt_search_str );
    if( ! top_el ) {
        return false;
    }

    var invalid_entries = top_el.getElements(".spt_input_validation_failed");
    if( invalid_entries.length ) {
        return true;
    }
    return false;
}


spt.validation._run_cbjs = function( validation_js_str, value, display_target_el, bvr )
{
    // First define the validation function wrapper around the validation js to be executed ...
    var fn_stmt = "var fn = function( value, display_target_el, bvr ) { " + validation_js_str + "; }";

    try {
        eval( fn_stmt );
    } catch(e) {
        spt.log_eval_error( e, fn_stmt, "spt.validation.run_cbjs", "error occurred in DEFINING validation function" );
        return null;
    }

    // Then run the validation function (defined above) to get the result of the validation ...
    var v_result = false;
    try {
        v_result = fn( value, display_target_el, bvr );
    } catch(e) {
        spt.log_eval_error( e, fn_stmt, "spt.validation.run_cbjs", "error occurred in RUNNING validation function" );
        return null;
    }

    return v_result;
}


spt.validation.set_invalid_warning = function( display_target_el, warning_msg )
{
    // this if statement is kept for backward compatibility only
    if( ! spt.css.has_look( "input_validation_failed", display_target_el ) ) {
        spt.css.add_looks( "input_validation_failed", display_target_el );
    }
    
    display_target_el.setStyle('background','#A99');
    display_target_el.setProperty( "title", warning_msg );
    display_target_el.addClass( "tactic_tip" );

    display_target_el.addClass( "spt_input_validation_failed" );
    display_target_el.setProperty("spt_validation_failed_msg", warning_msg);  // needed for DG-table td validations

}


spt.validation.clear_invalid_warning = function( display_target_el )
{
    if( spt.css.has_look( "input_validation_failed", display_target_el ) ) {
        spt.css.remove_looks( "input_validation_failed", display_target_el );
    }
    display_target_el.setProperty( "title", "" );
    display_target_el.removeClass( "tactic_tip" );

    display_target_el.removeClass( "spt_input_validation_failed" );

}


