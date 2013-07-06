// -------------------------------------------------------------------------------------------------------------------
//
//   Copyright (c) 2008, Southpaw Technology Inc., All Rights Reserved
//   
//   PROPRIETARY INFORMATION.  This software is proprietary to Southpaw Technology Inc., and is not to be
//   reproduced, transmitted, or disclosed in any way without written permission.
//   
// -------------------------------------------------------------------------------------------------------------------


// -------------------------------------------------------------------------------------------------------------------
//  Keyboard mapping constants ...
// -------------------------------------------------------------------------------------------------------------------

spt.key_const = {
    key_1: function() { return spt.key_const.get_keycode( 'KEY_1' ); },
    key_2: function() { return spt.key_const.get_keycode( 'KEY_2' ); },
    key_3: function() { return spt.key_const.get_keycode( 'KEY_3' ); },
    key_4: function() { return spt.key_const.get_keycode( 'KEY_4' ); },
    key_5: function() { return spt.key_const.get_keycode( 'KEY_5' ); },
    key_6: function() { return spt.key_const.get_keycode( 'KEY_6' ); },
    key_7: function() { return spt.key_const.get_keycode( 'KEY_7' ); },
    key_8: function() { return spt.key_const.get_keycode( 'KEY_8' ); },
    key_9: function() { return spt.key_const.get_keycode( 'KEY_9' ); },
    key_0: function() { return spt.key_const.get_keycode( 'KEY_0' ); },

    key_shift_1: function() { return spt.key_const.get_keycode( 'KEY_SHIFT_1' ); },
    key_shift_2: function() { return spt.key_const.get_keycode( 'KEY_SHIFT_2' ); },
    key_shift_3: function() { return spt.key_const.get_keycode( 'KEY_SHIFT_3' ); },
    key_shift_4: function() { return spt.key_const.get_keycode( 'KEY_SHIFT_4' ); },
    key_shift_5: function() { return spt.key_const.get_keycode( 'KEY_SHIFT_5' ); },
    key_shift_6: function() { return spt.key_const.get_keycode( 'KEY_SHIFT_6' ); },
    key_shift_7: function() { return spt.key_const.get_keycode( 'KEY_SHIFT_7' ); },
    key_shift_8: function() { return spt.key_const.get_keycode( 'KEY_SHIFT_8' ); },
    key_shift_9: function() { return spt.key_const.get_keycode( 'KEY_SHIFT_9' ); },
    key_shift_0: function() { return spt.key_const.get_keycode( 'KEY_SHIFT_0' ); }
};


// TODO: we can adjust key mappings here for non-North American keyboards ... for characters outside of the ASCII
//       (printable) character range, use the HTML code equivalent

spt.key_const.k = {
    'KEY_1': '1',
    'KEY_2': '2',
    'KEY_3': '3',
    'KEY_4': '4',
    'KEY_5': '5',
    'KEY_6': '6',
    'KEY_7': '7',
    'KEY_8': '8',
    'KEY_9': '9',
    'KEY_0': '0',

    'KEY_SHIFT_1': '!',
    'KEY_SHIFT_2': '@',
    'KEY_SHIFT_3': '#',
    'KEY_SHIFT_4': '$',
    'KEY_SHIFT_5': '%',
    'KEY_SHIFT_6': '^',
    'KEY_SHIFT_7': '&',
    'KEY_SHIFT_8': '*',
    'KEY_SHIFT_9': '(',
    'KEY_SHIFT_0': ')'
};


// TODO: we can adjust key mappings here for the given browser ...

spt.key_const._character_to_keycode = {
    '0': 48,
    '1': 49,
    '2': 50,
    '3': 51,
    '4': 52,
    '5': 53,
    '6': 54,
    '7': 55,
    '8': 56,
    '9': 57,

    '!': 33,
    '@': 64,
    '#': 35,
    '$': 36,
    '%': 37,
    '^': 94,
    '&': 38,
    '*': 42,
    '(': 40,
    ')': 41
};


spt.key_const.get_keycode = function( key_constant )
{
    if( key_constant in spt.key_const.k ) {
        var k = spt.key_const.k[ key_constant ];
        if( k in spt.key_const._character_to_keycode ) {
            var keycode = spt.key_const._character_to_keycode[ k ];
            return keycode;
        }
    }

    log.warning("WARNING: unable to map key_constant '" + key_constant + "' in spt.key.get_keycode()");
    return null;
}


// -------------------------------------------------------------------------------------------------------------------
//  Hot-key support ...
// -------------------------------------------------------------------------------------------------------------------
spt.hotkeys = {};


spt.hotkeys.handle_key_input_no_mods = function( key_info )
{
    var action_done = false;
    var key_code = spt.kbd.get_key_info_code( key_info );

    /*
    // DISABLING HOT KEY FOR ACTION BAR ... to be completely removed soon as we are deprecating the use of
    // the Action Bar, but keeping this code around for now until every thing is verified as working with
    // the new Gear Menus ...
    if( key_code == spt.key_const.key_2() && ! key_info.ctrl ) {
        // 2 ... toggle display of ACTION BAR popup ...
        spt.popup.toggle_display('ActionBarWdg_popup', false);
        action_done = true;
    }
    else if( key_code == spt.key_const.key_shift_2() && key_info.shift == true && ! key_info.ctrl ) {
        // SHIFT+2 for reset of ACTION BAR popup ...
        spt.popup.open('ActionBarWdg_popup', true);
        action_done = true;
    }
    */
    if( key_code == spt.key_const.key_9() && ! key_info.ctrl ) {
        // 9 ... toggle display of the TACTIC Script Editor popup ...
        var js_popup_id = "TACTIC Script Editor";
        var js_popup = $(js_popup_id);
        if( js_popup ) {
            spt.popup.toggle_display( js_popup_id, false );
        }
        else {
            spt.panel.load_popup(js_popup_id, "tactic.ui.app.ShelfEditWdg", {}, {"load_once": true} );
        }
        action_done = true;
    }
    else if( key_code == spt.key_const.key_shift_9() && key_info.shift == true && ! key_info.ctrl ) {
        // SHIFT+9 for reset of the TACTIC Script Editor popup ...
        var js_popup_id = "TACTIC Script Editor";
        spt.panel.load_popup(js_popup_id, "tactic.ui.app.ShelfEditWdg", {} );
        spt.popup.open(js_popup_id, true);
        action_done = true;
    }
    else if( key_code == spt.key_const.key_0() && ! key_info.ctrl ) {
        // open up help
        spt.named_events.fire_event("show_help")
        action_done = true;
    }
    else if( key_code == spt.key_const.key_shift_0() && key_info.shift == true && ! key_info.ctrl ) {
        // SHIFT+0 for reset of Web Output Console popup ...
    }

    else if( key_code == spt.key_const.key_1() && ! key_info.ctrl ) {
        // 1 toggles the side bar
        spt.named_events.fire_event("side_bar|toggle", {});
        action_done = true;
    }

    else if( key_code == spt.key_const.key_2() && ! key_info.ctrl ) {
        // 2 toggles the hotbox
        spt.named_events.fire_event("hotbox|toggle", {});
        action_done = true;
    }

    else if( key_code == spt.key_const.key_8() && ! key_info.ctrl ) {
        // 8 toggles the hotbox
        spt.js_log.show(true);
        action_done = true;
    }




    if( action_done ) {
        return true;
    }

    return false;
}


// -------------------------------------------------------------------------------------------------------------------
//  Keyboard handling mechanism ...
// -------------------------------------------------------------------------------------------------------------------

spt.kbd = {};

spt.kbd._hndlr_stack = [];


spt.kbd.push_handler_obj = function( handler_obj )
{
    spt.kbd._hndlr_stack.push( handler_obj );
}


spt.kbd.pop_handler_obj = function()
{
    return spt.kbd._hndlr_stack.pop();
}


spt.kbd.has_handler = function()
{
    if( spt.kbd._hndlr_stack.length > 0 ) {
        return true;
    }
    return false;
}


spt.kbd.get_top_handler_obj = function()
{
    if( spt.kbd.has_handler() ) {
        return spt.kbd._hndlr_stack[ spt.kbd._hndlr_stack.length-1 ];
    }
    return null;
}


spt.kbd.get_handler_count = function()
{
    return spt.kbd._hndlr_stack.length;
}


spt.kbd.clear_handler_stack = function()
{
    while( spt.kbd.get_handler_count() ) {
        spt.kbd.pop_handler_obj();
    }
}


// Mechanism for keyboard handler ...
//
// By default the keyboard_handler grabs the event and just passes it along, not doing anything with it.
// There will be a a handler registry for keyboard callbacks. Any element can register a keyboard handler object
// on the stack and the top one gets priority. The keyboard handler object can be any object, it just needs to
// have a member method/function that is called ".process_key()", which takes a single hash/dict object
// containing all the key input info from the event
//
spt.kbd._handler = function( evt )
{
    if( ! evt ) { evt = window.event; }   // IE compat

    var key_info = {};
    
    //use the real event for key and char code for complex manipulation
    key_info.key_code = evt.event.keyCode;
    key_info.char_code = evt.event.charCode;
    key_info.alt = evt.alt;
    key_info.shift = evt.shift;
    key_info.ctrl = evt.control;
    key_info.meta = evt.meta;


    // -- DEBUG ... uncomment code below to see what keyboard events are happening and the its MooTools attribute values
    //
    // spt.js_log.debug(">>> evt.key is [" + evt.key + "] ... evt.code is [" + evt.code + "]" +
    //                  " ... ctrl-key=" + evt.control + " ... alt-key=" + evt.alt + " ... shift-key=" + evt.shift );

    // -- DEBUG ... uncomment code below to see what keyboard event values are ...
    //
    // spt.js_log.debug(">>> key_info.key_code is [" + key_info.key_code + "] ... key_info.char_code is [" +
    //                  key_info.char_code + "]" +
    //                  " ... ctrl-key=" + key_info.ctrl + " ... alt-key=" + key_info.alt + " ... shift-key=" +
    //                  key_info.shift );


    // Here check to see if we have anything in the keyboard_handler stack, if so process the top element ...
    if( spt.kbd.has_handler() )
    {
        var handler = spt.kbd.get_top_handler_obj();

        var el = $(handler.text_edit_el);  // mootifying here to fix issue in IE
        var target = spt.get_event_target( evt );

        if( ! (el === target) )
        {
          

            //TODO: don't halt it, let the key pass thru so ppl can type
            spt.kbd.halt_key_event( evt );
            // Remko: disabling in IE until this is fixed
            if (!spt.browser.is_IE()) {
                el.focus();
            }
            var manual_modify = handler.process_key( key_info );
            if( manual_modify ) {
                var value = el.value;
                var key_code = spt.kbd.get_key_info_code( key_info );

                if( !(key_code in spt.kbd._special_keys_map_by_code) ) {
                    // add non-edit key to value ...
                    el.value = value + String.fromCharCode( key_code );
                }
                else if( key_code == spt.kbd.special_keys_map.BACKSPACE ) {
                    if( value.length ) {
                        // delete a character ...
                        el.value = value.substring( 0, value.length-1 );
                    }
                }
            }
            return;  // what should this return?
        }

        var bubble_event = handler.process_key( key_info );

        // after processing ... do not pass the event along!
        if( ! bubble_event ) {
            spt.kbd.halt_key_event( evt );
        }
    }
    else {
        var target = spt.get_event_target( evt );
        if( target.tagName == 'INPUT' || target.tagName == 'TEXTAREA' ) {
            // Make sure that INPUT and TEXTAREA elements that have focus get the key instead of a hotkey
            // ... this is to support previous input that isn't using the new keyboard handler
            return true;
        } else {
            // If no handler is found to run (and if no INPUT or TEXTAREA element needs the key input, then we check
            // for Tactic command hotkeys (straight keyboard keys, no CTRL or ALT modifiers -- can use SHIFT)
            // ... currently works on the key character of the event ... this may need some mapping for non-North
            // American keyboards at some point
            //
            if( spt.hotkeys.handle_key_input_no_mods( key_info ) ) {
                evt.stop();
                return false;
            }
        }
    }
}


spt.kbd.halt_key_event = function( evt )
{
    // Stop the event here and don't let anyone else see it ...
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


spt.kbd.special_keys_map = {

    'ENTER' : 13,
    'CTRL_ENTER' : 10,

    'SHIFT' : 17,
    'CTRL'  : 16,
    'ALT'   : 18,
    'META'  : 91,

    'F1' : 112, 'F2' : 113, 'F3' : 114, 'F4' : 115, 'F5' : 116, 'F6' : 117, 'F7' : 118, 'F8' : 119,
    'F9' : 120, 'F10' : 121, 'F11' : 122, 'F12' : 123, 'F13' : 124, 'F14' : 125, 'F15' : 126, 'F16' : 127,

    'ESC' : 27, 'TAB' : 9, 'CAPS_LOCK' : 20, /* 'NUM_LOCK' : ?? */ 
    'BACKSPACE' : 8, 'HELP' : 45, 'DEL' : 46, 'HOME' : 36, 'END' : 35, 'PAGE_UP' : 33, 'PAGE_DOWN' : 34,
    'ARROW_LEFT' : 37, 'ARROW_UP' : 38, 'ARROW_RIGHT' : 39, 'ARROW_DOWN' : 40

    // Number keypad keys?
}


spt.kbd._special_keys_map_by_code = {};

for( var name in spt.kbd.special_keys_map ) {
    if( ! spt.kbd.special_keys_map.hasOwnProperty(name) ) { continue; }
    spt.kbd._special_keys_map_by_code[ spt.kbd.special_keys_map[name] ] = name;
}


spt.kbd.is_digit = function( key_code )
{
    if( key_code >= "0".charCodeAt(0) && key_code <= "9".charCodeAt(0) ) {
        return true;
    }
    return false;
}


spt.kbd.is_arrow = function( key_code )
{
    if( key_code >= spt.kbd.code_for('ARROW_LEFT') && key_code <= spt.kbd.code_for('ARROW_DOWN') ) {
        return true;
    }
    return false;
}


spt.kbd.get_key_info_code = function( key_info )
{
    if( key_info.char_code ) { return key_info.char_code; }
    return key_info.key_code;
}


spt.kbd.code_for = function( key_str )
{
    if( key_str.length == 1 ) {
        return key_str.charCodeAt(0);
    }
    else if( key_str.toLocaleUpperCase() in spt.kbd.special_keys_map ) {
        return spt.kbd.special_keys_map[ key_str.toLocaleUpperCase() ];
    }

    return null;
}


spt.kbd.setup_handler = function()
{
    if( spt.browser.is_IE() || spt.browser.is_Safari() || spt.browser.is_Chrome() ) {
    // if( spt.browser.os_is_Windows() ) {
        document.addEvent( "keydown", spt.kbd._handler );
    }
    else {
        document.addEvent( "keypress", spt.kbd._handler );
    }
}


// ----------------------------------------------------------------------------------------------------------------
//
// spt.kbd.TextEditHandlerBase Base-Class
//
//   Core keyboard input handling for Text Input and Text Area elements. This is the Base Class that handles
//   a number of things to make it convenient for the application developer. Automatically handles ESC and
//   ENTER keys, canceling changes in text field on ESC and accepting changes in text field on ENTER.
//
//   Derive from this Class to create specific Text Edit handlers. See sub-classes below.
//
// ----------------------------------------------------------------------------------------------------------------

spt.kbd.TextEditHandlerBase = new Class({

    // Also pass in accept and cancel callbacks (use string names only) in a dictionary of values
    // e.g. { 'kbd_cbk_accept' : 'spt.dg_table.something_cbk', 'kbd_cbk_cancel' : 'spt.dg_table.something_else_cbk' }
    //
    initialize: function( text_edit_el, cbks, bvr )
    {
        this.text_value = "";
        this.text_edit_el = text_edit_el;
        this.cbks = cbks;
        this.text_edit_el.spt_text_edit_wdg = this;
        this.text_edit_el.addEvent( "focus", spt.kbd.TextEditHandlerBase._on_focus );
        this.text_edit_el.addEvent( "blur",  spt.kbd.TextEditHandlerBase._on_blur );

        this.bvr = bvr;

        this.edit_accepted = false;
        this.edit_accepted_default = false;
        this.allow_keys_by_default = false;

        this.multiline = false;
        if( this.text_edit_el.tagName == "TEXTAREA" ) {
            this.multiline = true;
        }

        this.is_active = false;
    },

    allow_by_default: function()
    {
        this.allow_keys_by_default = true;
    },

    pre_edit: function()
    {
        // save previous value (for cancel) ...
        this.text_value = this.text_edit_el.value;

        this.edit_accepted = this.edit_accepted_default;
        this.edit_done = false;
        this.is_active = true;
    },

    cancel: function()
    {
        if( this.cancel_action ) {
            // execute 'cancel' behavior of sub-class if it exists ...
            this.cancel_action();
        }

        this.edit_accepted = false;
        this.text_edit_el.value = this.text_value;
        this.edit_done = true;

        this.blur();
    },

    accept: function()
    {
        this.edit_accepted = true;
        this.edit_done = true;

        this.blur();

        if( this.accept_action ) {
            // execute 'accept' behavior of sub-class if it exists ...
            // do this after the blur so that we are certain that focus is handled properly before
            // other things occur!
            this.accept_action();
        }
    },

    blur: function()
    {
        this.text_edit_el.blur();
    },

    default_enter_key_handling: function( default_ret_value, key_info )
    {
        if( ! key_info.ctrl ) {
            this.accept();
            return false;
        }
        else if( this.multiline ) {
            // Demonstrates multi-line ... use ctrl-ENTER for new-line, regular ENTER (RETURN) accepts value
            var tvals = this.parse_selected_text();
            this.text_edit_el.value = tvals[0] + "\n" + tvals[1];
            spt.set_cursor_position( this.text_edit_el, tvals[0].length + 1 );
            return false;
        }

        return default_ret_value;
    },

    process_key: function( key_info )
    {
        var ret_val = this.allow_keys_by_default;
        var key_code = spt.kbd.get_key_info_code( key_info );
        this.key_code = key_code;

        if( key_code == spt.kbd.code_for('BACKSPACE') )
        {
            // First see if there is an override for the backspace key ...
            if( 'BACKSPACE' in this ) {
                return this.BACKSPACE( ret_val, key_info );
            }
            return true;  // let Backspace do it's thing ...
        }
        else if( key_code == spt.kbd.code_for('ESC') )
        {
            // Check for override for the ESC key ...
            if( 'ESC' in this ) {
                return this.ESC( ret_val, key_info );
            }

            // Default behavior for ESC is to cancel edit ...
            this.cancel();
            return false;
        }
        else if( key_code == spt.kbd.code_for('TAB') )
        {
            // accept edit on TAB off, and validate ...
            this.edit_accepted = true;
        }
        else if( key_code == spt.kbd.code_for('ENTER') ||
                 key_code == spt.kbd.code_for('CTRL_ENTER') )
        {
            if( key_code == spt.kbd.code_for('ENTER') ) {
                // On just ENTER key then accept edit and validate ...
                this.edit_accepted = true;
            }

            // Check for override for the ENTER key ...
            if( key_code == spt.kbd.code_for('ENTER') && ('ENTER' in this) ) {
                return this.ENTER( ret_val, key_info );
            }
            if( key_code == spt.kbd.code_for('CTRL_ENTER') && ('CTRL_ENTER' in this) ) {
                return this.CTRL_ENTER( ret_val, key_info );
            }
            return this.default_enter_key_handling( ret_val, key_info );
        }
        else if( spt.kbd.is_arrow( key_code ) ) {
            // Check override handlers for arrow key ...
            var key_name_str = spt.kbd._special_keys_map_by_code[ key_code ];
            if( key_name_str in this ) {
                var stmt = 'var tmp_ret = this.' + key_name_str + '( ret_val, key_info )';
                eval( stmt );
                return tmp_ret;
            }
            if( this.multiline == true ) {
                return true;
            } else {
                return true;
                /* comment this out for now since FF sees Shift+7 and Shift+9 as up and down arrow from pov of charCode
                // allow only left and right arrow if not multi-line ...
                if( key_code == spt.kbd.code_for('ARROW_LEFT') ||
                    key_code == spt.kbd.code_for('ARROW_RIGHT') ) {
                    return true;
                } else {
                    return false;
                }*/
            }
        }

        // if none of the above was handled then execute 'process_key' behavior of sub-class ...
        if( this.process_key_action ) {
            ret_val = this.process_key_action( key_info );
        }

        return ret_val;
    },

    parse_selected_text: function()
    {
        var text_value = this.text_edit_el.value;
        // this raises exceptions at times
        var sel_start = this.text_edit_el.selectionStart;
        var sel_end = this.text_edit_el.selectionEnd;

        if( sel_end == sel_start ) {
            return [ text_value.substr(0,sel_start), text_value.substr(sel_start) ];
        }

        var tval0 = text_value.substr( 0, sel_start );
        var tval1 = "";
        if( sel_end > sel_start ) {
            tval1 = text_value.substr( sel_end );
        }
        return [ tval0, tval1 ];
    }
});



spt.kbd.TextEditHandlerBase._on_focus = function( evt )
{
    if( !evt ) { evt = window.event; }

    var text_edit_el = spt.get_event_target( evt );
    spt.kbd.TextEditHandlerBase.startup_handler( text_edit_el );
}


spt.kbd.TextEditHandlerBase.startup_handler = function( text_edit_el )
{
    var spt_text_edit = text_edit_el.spt_text_edit_wdg;

    if( ! spt_text_edit.is_active || ! spt.kbd.has_handler() ) {
        spt.kbd.push_handler_obj( spt_text_edit );
        spt_text_edit.pre_edit();
    }
}


spt.kbd.TextEditHandlerBase._on_blur = function( evt )
{
    if( !evt ) { evt = window.event; }

    var text_edit_el = spt.get_event_target( evt );
    var spt_text_edit = text_edit_el.spt_text_edit_wdg;

    // default click-off to accept edit and validate ...
    spt_text_edit.edit_accepted = true;

    spt.kbd.pop_handler_obj();
    spt_text_edit.is_active = false;

    if( ! spt_text_edit.edit_done && spt_text_edit.blur_sub_action ) {
        spt_text_edit.blur_sub_action();
    }
}


// ----------------------------------------------------------------------------------------------------------------
//   Sub-classes derived from spt.kbd.TextEditHandlerBase Base-Class ...
// ----------------------------------------------------------------------------------------------------------------


// kbd_handler_name = 'FloatTextEdit'
//
spt.kbd.FloatTextEditHandler = new Class({

    Extends: spt.kbd.TextEditHandlerBase,

    process_key_action: function( key_info )
    {
        var key_code = spt.kbd.get_key_info_code( key_info );

        if( spt.kbd.is_digit( key_code ) ) {
            return this._handle_digit();
        }
        else if( key_code == spt.kbd.code_for(".") ) {
            return this._handle_decimal_point();
        }
        else if( key_code == spt.kbd.code_for("TAB") ) {
            // let TAB key continue on to the input element so that tabbing can bring the user to the next
            // input element available
            return true;
        }
        else {
            return false;  // does not let the kbd event continue on to the textarea element
        }

        return false;
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

    accept_action: function()
    {
        // do any special activity here, like send to database
    }

});


// kbd_handler_name = 'IntegerTextEdit'
//
spt.kbd.IntegerTextEditHandler = new Class({

    Extends: spt.kbd.FloatTextEditHandler,

    _handle_decimal_point: function()
    {
        return false;
    }

});


// kbd_handler_name = 'MultiLineTextEdit'
//
spt.kbd.MultiLineTextEditHandler = new Class({

    Extends: spt.kbd.TextEditHandlerBase,

    initialize: function( text_edit_el, cbks, bvr )
    {
        this.parent( text_edit_el, cbks, bvr );  // execute initialize method of super-class

        // now do initialize operations for this sub-class ...
        //
        this.allow_by_default();  // allow all keys by default, as it is open text editing
    }

});


spt.kbd.MultiLineOverrideExampleHandler = spt.kbd.MultiLineTextEditHandler.extend({

    _handle_arrow: function( default_ret_val, key_info, arrow_direction )
    {
        spt.js_log.debug( "*** Got " +  arrow_direction + " ARROW key override! ***" );
        return true;
    },

    BACKSPACE: function( default_ret_val, key_info ) {
        spt.js_log.debug( "*** Got BACKSPACE key override! Value 'false' is returned, so the " +
                            "TEXTAREA element does not get the key event ***" );
        return false;  // false will stop the event from reaching the element (so backspace will not occur
                       // in the TEXTAREA element)

        // NOTE: return true in order to send the key event to the TEXT input element
        //   or ...
        // return default_ret_val;  // you can return the default return value passed in
    },

    ENTER: function( default_ret_val, key_info ) {
        spt.js_log.debug( "*** Got ENTER key override! ... calling default enter key handling ***" );
        // return true;  // true will cascade event up to element (so backspace will occur in the TEXTAREA element)
        return this.default_enter_key_handling( default_ret_val, key_info );
    },

    ARROW_LEFT: function( default_ret_val, key_info ) {
        return this._handle_arrow( default_ret_val, key_info, 'LEFT' );
    },

    ARROW_UP: function( default_ret_val, key_info ) {
        return this._handle_arrow( default_ret_val, key_info, 'UP' );
    },

    ARROW_RIGHT: function( default_ret_val, key_info ) {
        return this._handle_arrow( default_ret_val, key_info, 'RIGHT' );
    },

    ARROW_DOWN: function( default_ret_val, key_info ) {
        return this._handle_arrow( default_ret_val, key_info, 'DOWN' );
    }

});



// kbd_handler_name = 'IntegerSubmit'
//
spt.kbd.IntegerSubmitHandler = new Class({
    Extends: spt.kbd.FloatTextEditHandler,

    _handle_decimal_point: function()
    {
        return false;
    },

    accept_action: function( default_ret_val, key_info )
    {
        spt.dg_table.search_cbk({}, this.bvr);
    }

});
spt.kbd.TextSearchHandler = new Class({
    Extends: spt.kbd.TextEditHandlerBase,

    process_key_action: function( key_info ) {
        return true;
    },

    accept_action: function( default_ret_val, key_info )
    {
        spt.dg_table.search_cbk({}, this.bvr);
    }

});




// @@@@
spt.kbd.CalendarInputKeyboardHandler = new Class({

    Extends: spt.kbd.TextEditHandlerBase,

    initialize: function( text_edit_el, cbks, bvr )
    {
        this.parent( text_edit_el, cbks, bvr );  // execute initialize method of super-class
        // now do initialize operations for this sub-class ...
        //
        this.allow_by_default();  // allow all keys by default, as it is open text editing

        this.edit_accepted_default = true;  // accept on click-off by default

        this.always_validate = true;

        var table_td = text_edit_el.getParent('.spt_table_td');
        if( table_td ) {
            this.in_dg_table = true;
        } else {
            this.in_dg_table = false;
        }
    },

    process_key_action: function( key_info )
    {
        var key_code = spt.kbd.get_key_info_code( key_info );
        if( key_code == spt.kbd.code_for('TAB') && this.in_dg_table ) {

            // handle TAB ...
            this.bvr.tab_key_pressed = true;

            var new_edit_cell = spt.dg_table.get_new_kbd_edit_cell_on_tab( this.bvr.src_el.getParent(".spt_table_td"),
                                                                           key_info.shift );

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
                return;
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
        else if( key_code == spt.kbd.code_for('TAB') ) {
            return true;
        }
        else {
            if( this.subclass_key_action ) {
                return this.subclass_key_action( key_info );
            }
        }

        return true;
    },

    cancel_action: function()
    {
        this.edit_accepted = false;
        if( this.in_dg_table ) {
            spt.dg_table.edit_cell_cbk( this.text_edit_el, spt.kbd.special_keys_map.ESC );
        }
        var cal_wdg_el = this.text_edit_el.getParent('.calendar_input_top').getElement('.spt_calendar_top');
        spt.hide(cal_wdg_el);
    },

    accept_action: function()
    {
        this.edit_accepted = true;

        // Revise value and put into format of ...


        if( this.in_dg_table ) {
            spt.dg_table.edit_cell_cbk( this.text_edit_el, this.key_code );
        }

        var cal_wdg_el = this.text_edit_el.getParent('.calendar_input_top').getElement('.spt_calendar_top');
        spt.hide(cal_wdg_el);
    },

    blur_sub_action: function()
    {
        // do nothing -- click off should take no action, as CalendarWdg pop-up needs to be able to be
        // clicked on
    }

});


