// -------------------------------------------------------------------------------------------------------------------
//
//   Copyright (c) 2008, Southpaw Technology Inc., All Rights Reserved
//   
//   PROPRIETARY INFORMATION.  This software is proprietary to Southpaw Technology Inc., and is not to be
//   reproduced, transmitted, or disclosed in any way without written permission.
//   
// -------------------------------------------------------------------------------------------------------------------


// ---------------------------------------------------------------------
// Create container for "spt.smenu" ...
// ---------------------------------------------------------------------

spt.smenu = {};

spt.smenu.stack = [];


spt.smenu.pop = function()
{
    var menu_el = spt.smenu.stack.pop();
    spt.hide( menu_el );
    return menu_el;
}


spt.smenu.get_top = function()
{
    if( spt.smenu.is_active() ) {
        return spt.smenu.stack[ spt.smenu.stack.length-1 ];
    }

    return null;
}


spt.smenu.get_bottom = function()
{
    if( spt.smenu.is_active() ) {
        return spt.smenu.stack[ 0 ];
    }

    return null;
}


spt.smenu.clear = function()
{
    if( spt.smenu.stack.length ) {
        // means we have a context menu active (and possibly sub-menus for it) ...
        while( spt.smenu.stack.length ) {
            menu = spt.smenu.pop();
            menu.spt_smenu_stack_number = 0;
        }
    }
}


spt.smenu.clear_higher = function( curr_menu_num )
{
    if( spt.smenu.stack.length > curr_menu_num ) {
        var diff = spt.smenu.stack.length - curr_menu_num;
        for( var d=0; d < diff; d++ ) {
            menu = spt.smenu.pop();
            menu.spt_smenu_stack_number = 0;
        }
    }
}


spt.smenu.is_active = function()
{
    if( spt.smenu.stack.length ) {
        return true;
    }

    return false;
}


spt.smenu.click_off_check_cbk = function(evt)
{
    var target_el = spt.get_event_target(evt);
    var click_bvr_el = spt.get_first_el_with_bvr_type_from_target( "click", target_el );
    var click_up_bvr_el = spt.get_first_el_with_bvr_type_from_target( "click_up", target_el );

    if( click_bvr_el && click_bvr_el.get("tag") != "body" ) {
        return true;
    }
    if( click_up_bvr_el && click_up_bvr_el.get("tag") != "body" ) {
        return true;
    }

    if( spt.smenu.is_active() ) {
        var menu = spt.smenu.get_top();
        if( spt.smenu.use_defer_click_off ) {
            if( menu.hasOwnProperty("spt_defer_click_off") ) {
                var dco = menu.spt_defer_click_off;
                dco --;
                if( ! dco ) {
                    delete menu.spt_defer_click_off;
                }
                return false;
            }
        }
        spt.smenu.clear();
        spt.ctx_menu.clear();
    }
}


spt.smenu.get_activator = function( bvr )
{
    if (!bvr)
        return null;

    var smenu_subset = $(bvr.src_el).getParent('.SPT_SMENU_SUBSET');
    if (smenu_subset)
        return smenu_subset.activator_el;
    else
        return null;

}


spt.smenu.get_activator_by_el = function( el )
{
    var smenu_subset = $(el).getParent('.SPT_SMENU_SUBSET');
    return smenu_subset.activator_el;
}


spt.smenu.submenu_entry_over = function( evt, bvr, mouse_411 )
{
   
    var target = $(spt.get_event_target(evt));
    var cur_menu = target.getParent(".SPT_SMENU");

    if( spt.smenu.stack.length > cur_menu.spt_smenu_stack_number ) {
        var higher_menu = spt.smenu.stack[cur_menu.spt_smenu_stack_number];
        var submenu = spt.get_cousin( bvr.src_el, ".SPT_SMENU_SUBSET", ("." + bvr.submenu_tag), [] );

        if( higher_menu != submenu ) {
            // means the submenu is from a different entry ...
            spt.smenu.clear_higher( cur_menu.spt_smenu_stack_number );
            spt.smenu.show_on_submenu_activate_cbk( evt, bvr );
        }
    }
    else if( spt.smenu.stack.length == cur_menu.spt_smenu_stack_number ) {
        spt.smenu.show_on_submenu_activate_cbk( evt, bvr );
    }

    if( bvr.activator_mod_styles || bvr.activator_add_looks || bvr.activator_add_look_suffix ) {
        spt.smenu._apply_css_to_activator( bvr );
    }

}


spt.smenu.submenu_entry_out = function( evt, bvr, mouse_411 )
{
    if( bvr.activator_mod_styles || bvr.activator_add_looks || bvr.activator_add_look_suffix ) {
        spt.smenu._restore_activator_css( bvr );
    }
}


spt.smenu.entry_over = function( evt, bvr, mouse_411 )
{
    var target = $(spt.get_event_target(evt));
    var menu = target.getParent(".SPT_SMENU");
    if (!menu) return;

    spt.smenu.clear_higher( menu.spt_smenu_stack_number );

    if( bvr.activator_mod_styles || bvr.activator_add_looks || bvr.activator_add_look_suffix ) {
        spt.smenu._apply_css_to_activator( bvr );
    }

    if( bvr.cbjs_menu_entry_over_action ) {
        spt.behavior.run_cbjs( bvr.cbjs_menu_entry_over_action, bvr, evt, null );
    }
}


spt.smenu.entry_out = function( evt, bvr, mouse_411 )
{
    if( bvr.activator_mod_styles || bvr.activator_add_looks || bvr.activator_add_look_suffix ) {
        spt.smenu._restore_activator_css( bvr );
    }

    if( bvr.cbjs_menu_entry_out_action ) {
        spt.behavior.run_cbjs( bvr.cbjs_menu_entry_out_action, bvr, evt, null );
    }
}


// --- built in functionality to be able to highlight (mod css or look) the activator element on a given menu item

spt.smenu._apply_css_to_activator = function( bvr )
{
    var activator_el = spt.smenu.get_activator( bvr );

    if( bvr.affect_activator_relatives && ! ('spt_activator_relatives_for_hover' in activator_el) ) {
        activator_el.spt_activator_relatives_for_hover = [];
        for( var c=0; c < bvr.affect_activator_relatives.length; c++ ) {
            var rel_str = bvr.affect_activator_relatives[c];
            var relative_el = spt.behavior.get_bvr_element( activator_el, rel_str );
            if( relative_el ) {
                activator_el.spt_activator_relatives_for_hover.push( relative_el );
            }
        }
    }

    if( bvr.activator_mod_styles ) {
        if( spt.get_typeof( bvr.activator_mod_styles ) == 'string' ) {
            bvr.activator_mod_styles = spt.css.get_mod_styles_map( bvr.activator_mod_styles );
        }

        bvr._activator_styles_to_restore = spt.css.get_style_bkups( bvr.activator_mod_styles, activator_el );
        spt.css.apply_style_mods( bvr.activator_mod_styles, activator_el );

        if( 'spt_activator_relatives_for_hover' in activator_el ) {
            bvr._activator_relative_styles_to_restore = [];
            for( var c=0; c < activator_el.spt_activator_relatives_for_hover.length; c++ ) {
                var rel_el = activator_el.spt_activator_relatives_for_hover[c];
                bvr._activator_relative_styles_to_restore.push(
                                                spt.css.get_style_bkups( bvr.activator_mod_styles, rel_el ) );
                spt.css.apply_style_mods( bvr.activator_mod_styles, rel_el );
            }
        }
    }

    // check for look suffix ...
    if( bvr.activator_add_look_suffix ) {
        var look_suffix = bvr.activator_add_look_suffix;
        var target_look_order = bvr.target_look_order;

        var look_to_add = '';
        for( var c=0; c < target_look_order.length; c++ ) {
            var look_cls = "look_" + target_look_order[c];
            if( activator_el.hasClass(look_cls) ) {
                look_to_add = target_look_order[c] + "_" + look_suffix;
                break;
            }
        }

        bvr._activator_looks_added = [];
        bvr._activator_looks_added = spt.css.add_looks( look_to_add, activator_el );
    }
    else if( bvr.activator_add_looks ) {
        bvr._activator_looks_added = [];
        bvr._activator_looks_added = spt.css.add_looks( bvr.activator_add_looks, activator_el );

        if( 'spt_activator_relatives_for_hover' in activator_el ) {
            bvr._activator_relative_looks_added = [];
            for( var c=0; c < activator_el.spt_activator_relatives_for_hover.length; c++ ) {
                var rel_el = activator_el.spt_activator_relatives_for_hover[c];
                bvr._activator_relative_looks_added.push( spt.css.add_looks( bvr.activator_add_looks, rel_el ) );
            }
        }
    }
}


spt.smenu._restore_activator_css = function( bvr )
{
    var activator_el = spt.smenu.get_activator( bvr );

    if( bvr.activator_mod_styles ) {
        spt.css.apply_style_mods( bvr._activator_styles_to_restore, activator_el );
        delete bvr._activator_styles_to_restore;

        if( 'spt_activator_relatives_for_hover' in activator_el ) {
            for( var c=0; c < activator_el.spt_activator_relatives_for_hover.length; c++ ) {
                var rel_el = activator_el.spt_activator_relatives_for_hover[c];
                var restore_style_mods = bvr._activator_relative_styles_to_restore[c];
                spt.css.apply_style_mods( restore_style_mods, rel_el );
            }
            bvr._activator_relative_styles_to_restore = [];
            delete bvr._activator_relative_styles_to_restore;
        }
    }

    if( bvr.activator_add_looks || bvr.activator_add_look_suffix ) {
        spt.css.remove_looks( bvr._activator_looks_added, activator_el );
        delete bvr._activator_looks_added;

        if( 'spt_activator_relatives_for_hover' in activator_el ) {
            for( var c=0; c < activator_el.spt_activator_relatives_for_hover.length; c++ ) {
                var rel_el = activator_el.spt_activator_relatives_for_hover[c];
                var looks_added = bvr._activator_relative_looks_added[c];
                spt.css.remove_looks( looks_added, rel_el );
            }
            bvr._activator_relative_looks_added = [];
            delete bvr._activator_relative_looks_added;
        }
    }
}



spt.smenu._search_children_for_smenu_set = function( el )
{
    var cls = 'SPT_PUW_STUB';
    var regex = new RegExp( "\\b" + cls + "\\b" );
    var children = el.childNodes;

    var found_smenu_set = null;
    for( var c=0; c < children.length; c++ ) {
        var child = children[c];
        if( 'className' in child ) {
            if( child.className.match( regex ) && 'spt_puw_el' in child ) {
                if( child.spt_puw_el.hasClass( "SPT_SMENU_SET" ) ) {
                    found_smenu_set = child.spt_puw_el;
                    break;
                }
            }
        }
    }
    return found_smenu_set;
}


spt.smenu.get_main_menu = function( evt )
{
    var activator = $(spt.get_event_target(evt));
    if( ! activator.hasClass("SPT_SMENU_ACTIVATOR") ) {
        activator = activator.getParent(".SPT_SMENU_ACTIVATOR");
    }
    if( ! activator ) {
        return null;
    }

    // Either the activator immediately contains the smart menu set ...
    var smenu_set = spt.smenu._search_children_for_smenu_set( activator );
    if( ! smenu_set ) {
        // OR it is contained in an uber node
        var top_node = activator.getParent(".SPT_SMENU_CONTAINER");
        smenu_set = spt.smenu._search_children_for_smenu_set( top_node );
    }
    if( ! smenu_set ) {
        // TODO: big error message!
        spt.js_log.error( "ERROR: [spt.smenu.get_main_menu] NO smart-menu set found!" );
        return null;
    }

    var main_menu = null;
    var subset = null;

    // -- DO NOT SET activator_el on menu set, set it on subset
    // smenu_set.activator_el = activator;

    var subset_tag_suffix = activator.getProperty( "SPT_SMENU_SUBSET_TAG_SUFFIX" );
    if( subset_tag_suffix ) {
        subset = smenu_set.getElement( ".SPT_SMENU_SUBSET__" + subset_tag_suffix );
    } else {
        subset = smenu_set.getElement( ".SPT_SMENU_SUBSET__DEFAULT" );
    }

    if( ! subset ) {
        return null;
    }

    // plug the activator to the smenu subset ...
    subset.activator_el = activator;
    main_menu = subset.getElement( ".SPT_SMENU_MAIN" );

    return main_menu;
}


spt.smenu.show_on_context_click_cbk = function( evt )
{
    
    if( spt.force_default_context_menu ) {
        // not needed , plus it causes bugs in embedded table
        //spt.force_default_context_menu = false;
        return true;
    }
    var main_menu = spt.smenu.get_main_menu( evt );
    if( ! main_menu ) {
        return true;
    }
    spt.smenu.clear();
    spt.ctx_menu.clear();
    spt.smenu._show_action( evt, main_menu, "context", null );

    return false;
}


spt.smenu.show_on_dropdown_click_cbk = function( evt, activator_bvr )
{
    var menu = spt.smenu.get_bottom();
    spt.smenu.clear();
    spt.ctx_menu.clear();

    var main_menu = spt.smenu.get_main_menu( evt );
    if( ! main_menu ) {
        return;
    }

    if( ! menu || ( menu !== main_menu ) ) {
        spt.smenu._show_action( evt, main_menu, "dropdown", activator_bvr );
    }
}


spt.smenu.show_on_submenu_activate_cbk = function( evt, bvr )
{
    var submenu_tag = bvr.submenu_tag;
    var submenu = spt.get_cousin( bvr.src_el, ".SPT_SMENU_SUBSET", ("." + submenu_tag), [] );

    spt.smenu._show_action( evt, submenu, "submenu", bvr );
}


spt.smenu._setup_menu_items = function( menu )
{
    var activator = spt.smenu.get_activator_by_el( menu );

    var setup_info = {};
    if( menu.getProperty("SPT_SMENU_SETUP_CBFN") ) {
        var stmt = menu.getProperty("SPT_SMENU_SETUP_CBFN") + "( menu, activator );";
        setup_info = eval( stmt );

        if( ! setup_info ) {
            setup_info = {};
        }
        menu.spt_setup_info = setup_info;
    }

    var entry_tr_list = menu.getElements(".SPT_SMENU_ENTRY");
    for( var c=0; c < entry_tr_list.length; c++ ) {
        var tr = entry_tr_list[c];
        if( tr.getProperty("SPT_ENABLED_CHECK_SETUP_KEY") && menu.spt_setup_info ) {
            var hide_when_disabled = spt.is_TRUE( tr.getProperty("SPT_HIDE_WHEN_DISABLED") );

            var enabled_flag = true;

            var enabled_flag_var = tr.getProperty("SPT_ENABLED_CHECK_SETUP_KEY");
            // use | delimited setup key if more than 1 is given
            var enabled_flag_vars = enabled_flag_var.test(/|/) ? enabled_flag_var.split('|') : [enabled_flag_var];
            
            for (var k=0; k < enabled_flag_vars.length; k++) {
                enabled_flag_var = enabled_flag_vars[k];
                if( enabled_flag_var in menu.spt_setup_info ) {
                    enabled_flag = menu.spt_setup_info[ enabled_flag_var ];
                }
            }
            // Handle enabled/disabled state for the entry ...
            if( hide_when_disabled ) {
                if( enabled_flag ) { spt.show( tr ); }
                else { spt.hide( tr ); }
            }
            else {
                var entry_els = tr.getElements(".SPT_ENABLED_LOOK");
                for( var e=0; e < entry_els.length; e++ ) {
                    if( enabled_flag ) { spt.css.remove_looks( "smenu_disabled", entry_els[e] ); }
                    else { spt.css.add_looks( "smenu_disabled", entry_els[e] ); }
                }

                var icon_els = tr.getElements(".SPT_ENABLED_ICON_LOOK");
                for( var i=0; i < icon_els.length; i++ ) {
                    if( enabled_flag ) { spt.css.remove_looks( "smenu_icon_disabled", icon_els[i] ); }
                    else { spt.css.add_looks( "smenu_icon_disabled", icon_els[i] ); }
                }

                // disable hover and click behaviors ...
                if( enabled_flag ) {
                    spt.behavior.enable_by_type( [ "hover", "click", "click_up" ], tr );
                } else {
                    spt.behavior.disable_by_type( [ "hover", "click", "click_up" ], tr );
                }
            }
        }

        spt.smenu._replace_label_vars( tr, menu.spt_setup_info );
    }
}


spt.smenu._replace_label_vars = function( entry_tr, setup_info )
{
    var label_el = entry_tr.getElement(".SPT_LABEL")
    if( ! label_el ) { return; }

    var orig_label = label_el.getProperty( "SPT_ORIG_LABEL" )
    if( ! orig_label ) { return; }

    if( orig_label.indexOf("{") == -1 ) { return; }

    var new_label_arr = [];
    var start_idx = 0;
    var gathering = false;
    for( var i=0; i < orig_label.length; i++ )
    {
        var ch = orig_label.charAt(i);
        if( ch == '{' ) {
            start_idx = i;
            gathering = true;
        }
        else if( ch == '}' ) {
            var key = orig_label.substr( start_idx+1, i - start_idx - 1 );
            if( key in setup_info ) {
                new_label_arr.push( setup_info[ key ] );
            } else {
                new_label_arr.push( '{' + key + '}' );
            }
            gathering = false;
        } else {
            if( ! gathering ) {
                new_label_arr.push( ch );
            }
        }
    }

    label_el.innerHTML = new_label_arr.join('');
}


spt.smenu.test = {};

spt.smenu.test.cat_menu_setup_cbk = function( menu_el, activator_el )
{
    var s = activator_el.innerHTML;
    s.substr( 1, s.length - 2 );
    var bits = s.split(',');

    var row = parseInt(bits[0]);
    var col = parseInt(bits[1]);

    var cat_entry_enabled = false;
    if( col < 4 ) {
        cat_entry_enabled = true;
    }

    var setup_info = {
        'is_cat_entry_ok' : cat_entry_enabled,
        'cell_contents' : s
    }

    return setup_info;
}


// activation_type is 'context', 'dropdown' or 'submenu'
//
spt.smenu._show_action = function( evt, menu, activation_type, activator_bvr )
{
    if( ! evt ) { evt = window.event; }  // IE compat.

    var smenu_subset = menu.getParent(".SPT_SMENU_SUBSET");

    var activator_el = smenu_subset.activator_el;
    // var ctx_tag = smenu_subset.getProperty("SPT_CONTEXT_CLASS_TAG");

    var nudge_horiz = 0;
    if( activator_el.getProperty("spt_nudge_menu_horiz") ) {
        nudge_horiz = parseInt( activator_el.getProperty("spt_nudge_menu_horiz") );
    }
    var nudge_vert = 0;
    if( activator_el.getProperty("spt_nudge_menu_vert") ) {
        nudge_vert = parseInt( activator_el.getProperty("spt_nudge_menu_vert") );
    }

    // BEFORE we display the menu we want to run through any checks in the menu items for enable/disable
    // state, as well as any label variable replacement handling (based on possibly new activator element) ...
    //
    spt.smenu._setup_menu_items( menu );

    spt.show_block( menu );
    menu.setStyle("z-index", "1000" );

    if( "spt_defer_click_off" in menu ) {
        delete menu.spt_defer_click_off;
    }

    if( activation_type == 'dropdown' ) {
        var abs_offset = spt.get_absolute_offset(activator_el);
        menu.setStyle("left", (abs_offset.x + nudge_horiz));
        menu.setStyle("top" , (abs_offset.y + activator_el.clientHeight - 1 + nudge_vert));

        if( spt.smenu.use_defer_click_off ) {
            menu["spt_defer_click_off"] = 1;
        }
    }
    else if( activation_type == 'submenu' ) {
        var entry_el = activator_bvr.src_el;
        var abs_offset = spt.get_absolute_offset(entry_el);

        menu.setStyle("left", (abs_offset.x + entry_el.clientWidth + nudge_horiz));
        menu.setStyle("top" , (abs_offset.y + nudge_vert));
    }
    else {
        // assume context menu activation otherwise

        var cursor_pos = spt.mouse.get_abs_cusor_position(evt);
        menu.setStyle("left", (cursor_pos.x + nudge_horiz));
        menu.setStyle("top",  (cursor_pos.y + nudge_vert));
    }


    spt.smenu.stack.push( menu );
    menu.spt_smenu_stack_number = spt.smenu.stack.length;

    spt.halt_event_here( evt );

    // reposition if offscreen
    var size = menu.getSize();
    var pos = menu.getPosition();
    var win_size = $(document.body).getSize();

    var body = $(document.body);
    var scroll_top = body.scrollTop;
    var scroll_left = body.scrollLeft;

    if (pos.y+size.y-scroll_top > win_size.y) {
        menu.setStyle("top", win_size.y - size.y + scroll_top - 3);
    }
    if (pos.x+size.x-scroll_left > win_size.x) {
        menu.setStyle("left", win_size.x - size.x + scroll_left - 3);
    }

    return false;
}


spt.smenu._cbjs_action_info = {};
spt.smenu._cbjs_action_info.evt = null;
spt.smenu._cbjs_action_info.bvr = null;

spt.smenu.cbjs_action_wrapper = function( evt, bvr )
{
    spt.smenu.clear();
    spt.ctx_menu.clear();

    if( spt.browser.is_IE() ) {
        // because we are using setTimeout to run the actual command cbjs for the menu option, we need to
        // build a 'transitional' event object to store the event target of the originating event ...
        // the original event won't be valid when accessed at the different temporal point resulting from
        // using setTimeout ...
        var target = spt.get_event_target(evt);
        spt.smenu._cbjs_action_info.evt = { 'event': { 'srcElement': target } };
        spt.smenu._cbjs_action_info.bvr = bvr;
        setTimeout( "spt.smenu._cbjs_action_runner( " +
                        "spt.smenu._cbjs_action_info.evt, spt.smenu._cbjs_action_info.bvr );", 1 );
    } else {
        spt.smenu._cbjs_action_runner( evt, bvr );
    }
}


spt.smenu._cbjs_action_runner = function( evt, bvr )
{
    if( bvr.cbjs_action_for_menu_item ) {
        spt.behavior.run_cbjs( bvr.cbjs_action_for_menu_item, bvr, evt, null );
    }
}


