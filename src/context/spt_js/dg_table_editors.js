// -------------------------------------------------------------------------------------------------------------------
//
//   Copyright (c) 2008, Southpaw Technology Inc., All Rights Reserved
//   
//   PROPRIETARY INFORMATION.  This software is proprietary to Southpaw Technology Inc., and is not to be
//   reproduced, transmitted, or disclosed in any way without written permission.
//   
// -------------------------------------------------------------------------------------------------------------------


// Assumes that 'spt.dg_table' is already defined ...


// Specific Keyboard Handlers for Data-grid Table (dg_table)

spt.kbd.DgTableKeyboardHandlerBase = new Class({

    Extends: spt.kbd.TextEditHandlerBase,

    initialize: function( text_edit_el, cbks, bvr )
    {
        this.parent( text_edit_el, cbks, bvr );  // execute initialize method of super-class
        // now do initialize operations for this sub-class ...
        //
        this.allow_by_default();  // allow all keys by default, as it is open text editing

        this.edit_accepted_default = true;  // accept on click-off by default
    },

    process_key_action: function( key_info )
    {
        var key_code = spt.kbd.get_key_info_code( key_info );
        if( key_code == spt.kbd.code_for('TAB') ) {

            // handle TAB ...
            this.bvr.tab_key_pressed = true;

            var table_td = this.bvr.src_el.getParent(".spt_table_td");
            if( ! table_td ) {
                // not in DG table cell, so likely being used in EditWdg ... so just return true to let the key
                // do it's thing ...
                return true;
            }
            var new_edit_cell = spt.dg_table.get_new_kbd_edit_cell_on_tab( table_td, key_info.shift );

            if( this.special_accept_handling ) {
                this.special_accept_handling();
            } else {
                if( this.edit_accepted_default ) {
                    spt.dg_table.edit_cell_cbk( this.text_edit_el, spt.kbd.special_keys_map.ENTER );
                } else {
                    spt.dg_table.edit_cell_cbk( this.text_edit_el, spt.kbd.special_keys_map.ESC );
                }
            }

            if( ! new_edit_cell ) {
                return false;
            }

            var click_up_bvrs = spt.behavior.get_bvrs_by_type( "click_up", new_edit_cell );
            var click_up_bvr = null;
            for( var c = 0; c < click_up_bvrs.length; c++ ) {
                var bvr = click_up_bvrs[c];
                if( bvr.cbfn_action && bvr.cbfn_action === spt.dg_table.select_cell_for_edit_cbk ) {
                    click_up_bvr = bvr;
                    break;
                }
            }

            spt.dg_table.select_cell_for_edit_cbk( {}, click_up_bvr );
            return false;
        }
        else {
            if( this.subclass_key_action ) {
                return this.subclass_key_action( key_info );
            }
        }

        return true;
    },

    blur_sub_action: function()
    {
        // On click-off, accept any edits ...
        if( ! this.bvr.tab_key_pressed ) {
            if( this.special_accept_handling ) {
                this.special_accept_handling();
            } else {
                if( this.edit_accepted_default ) {
                    spt.dg_table.edit_cell_cbk( this.text_edit_el, spt.kbd.special_keys_map.ENTER );
                }
            }
        }
        else {
            this.bvr.tab_key_pressed = false;
        }
    }

});


// kbd_handler_name = 'DgTableMultiLineTextEdit'
//


spt.kbd.DgTableMultiLineTextEditHandler = new Class({

    Extends: spt.kbd.DgTableKeyboardHandlerBase,

    cancel_action: function()
    {
        this.edit_accepted = false;
        spt.dg_table.edit_cell_cbk( this.text_edit_el, spt.kbd.special_keys_map.ESC );
    },

    accept_action: function()
    {
        this.edit_accepted = true;
        spt.dg_table.edit_cell_cbk( this.text_edit_el, this.key_code );
    },

    blur_sub_action: function()
    {
        // On click-off, accept any edits ...
        if( ! this.bvr.tab_key_pressed ) {
            spt.dg_table.edit_cell_cbk( this.text_edit_el, spt.kbd.special_keys_map.ENTER );
        }
        else {
            this.bvr.tab_key_pressed = false;
        }
    }

});


spt.kbd.DgTableFloatTextEditHandler = new Class({

    Extends: spt.kbd.DgTableKeyboardHandlerBase,

    subclass_key_action: function( key_info )
    {
        var key_code = spt.kbd.get_key_info_code( key_info );

        if( spt.kbd.is_digit( key_code ) ) {
            return this._handle_digit();
        }
        else if( key_code == spt.kbd.code_for(".") ) {
            return this._handle_decimal_point();
        }
        else {
            return true;  //allow typing alpha for now b4 this cannot-type bug is fixed
        }
        return true;
    },

    _handle_digit: function()
    {
        var tvals = this.parse_selected_text();
        return true;
    },

    _handle_decimal_point: function()
    {
        // if decimal place is within selected area, i.e. the area to be replaced by what is typed,
        // then allow decimal to replace selected text ... otherwise if decimal is in non-selected
        // area then do not allow another decimal ...
        //
        var tvals = this.parse_selected_text();

        if( tvals[0].indexOf(".") == -1 && tvals[1].indexOf(".") == -1 ) {  // if no decimal, then allow a decimal
            return true;
        } else {
            return false;
        }
    },

    cancel_action: function()
    {
        this.edit_accepted = false;
        spt.dg_table.edit_cell_cbk( this.text_edit_el, spt.kbd.special_keys_map.ESC );
    },

    accept_action: function()
    {
        this.edit_accepted = true;
        spt.dg_table.edit_cell_cbk( this.text_edit_el, this.key_code );
    },

    blur_sub_action: function()
    {
        // On click-off, accept any edits ...
        spt.dg_table.edit_cell_cbk( this.text_edit_el, spt.kbd.special_keys_map.ENTER );
    }

});


spt.kbd.DgTableIntegerTextEditHandler = new Class({

    Extends: spt.kbd.DgTableFloatTextEditHandler,

    _handle_decimal_point: function()
    {
        return false;
    }

});


// kbd_handler_name = 'DgTableSelectWidgetKeyInput'
//
spt.kbd.DgTableSelectWidgetKeyInputHandler = new Class({

    Extends: spt.kbd.DgTableKeyboardHandlerBase,

    /*
    subclass_key_action: function( key_info )
    {
        var key_code = spt.kbd.get_key_info_code( key_info );
        log.debug( "in subclass_key_action for select widget" );
        return true;
    },
    */

    special_accept_handling: function()
    {
        
        //if( ! this.bvr.src_el.value ) {
            // comment this out for now so Selectwdg cam accept empty value
            // this.edit_accepted = false;
            // spt.dg_table.edit_cell_cbk( this.text_edit_el, spt.kbd.special_keys_map.ESC );
        //}
        if ( this.bvr.src_el.value=='[label]'){
            alert('A label was selected. Please choose a valid value.');
            this.cancel_action();
        }
        else {
            this.edit_accepted = true;
            spt.dg_table.edit_cell_cbk( this.text_edit_el, spt.kbd.special_keys_map.ENTER );
        }
    },

    cancel_action: function()
    {
        this.edit_accepted = false;
        spt.dg_table.edit_cell_cbk( this.text_edit_el, spt.kbd.special_keys_map.ESC );
    },

    accept_action: function()
    {
        this.special_accept_handling();
    }

});



