// -------------------------------------------------------------------------------------------------------------------
//
//   Copyright (c) 2008, Southpaw Technology Inc., All Rights Reserved
//   
//   PROPRIETARY INFORMATION.  This software is proprietary to Southpaw Technology Inc., and is not to be
//   reproduced, transmitted, or disclosed in any way without written permission.
//   
// -------------------------------------------------------------------------------------------------------------------


// ---------------------------------------------------------------------
// Create container for "spt.ctx_menu" ...
// ---------------------------------------------------------------------

spt.ctx_menu = {};

spt.ctx_menu.stack = [];

spt.ctx_menu.use_defer_click_off = false;


spt.ctx_menu.pop = function()
{
    var menu_el = spt.ctx_menu.stack.pop();
    menu_el.style.display = "none";
}


spt.ctx_menu.get_top = function()
{
    if( spt.ctx_menu.is_active() ) {
        return spt.ctx_menu.stack[ spt.ctx_menu.stack.length-1 ];
    }

    return null;
}


spt.ctx_menu.get_bottom = function()
{
    if( spt.ctx_menu.is_active() ) {
        return spt.ctx_menu.stack[ 0 ];
    }

    return null;
}


spt.ctx_menu.clear = function()
{
    if( spt.ctx_menu.stack.length ) {
        // means we have a context menu active (and possibly sub-menus for it) ...
        while( spt.ctx_menu.stack.length ) {
            spt.ctx_menu.pop();
        }
    }
}


spt.ctx_menu.clear_higher = function( curr_menu_num )
{
    if( spt.ctx_menu.stack.length > curr_menu_num ) {
        var diff = spt.ctx_menu.stack.length - curr_menu_num;
        for( var d=0; d < diff; d++ ) {
            spt.ctx_menu.pop();
        }
    }
}


spt.ctx_menu.is_active = function()
{
    if( spt.ctx_menu.stack.length ) {
        return true;
    }

    return false;
}


// each context menu gets added as a utility div ... and the top div of the context menu widget must be provided
// with the class name "SPT_CTX_MENU" and must be given a unique ID for the page!


spt.ctx_menu.click_off_check_cbk = function(evt)
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

    if( spt.ctx_menu.is_active() ) {
        var menu = spt.ctx_menu.get_top();
        if( spt.ctx_menu.use_defer_click_off ) {
            if( menu.hasOwnProperty("spt_defer_click_off") ) {
                var dco = menu.spt_defer_click_off;
                dco --;
                if( ! dco ) {
                    delete menu.spt_defer_click_off;
                }
                return false;
            }
        }
        spt.ctx_menu.clear();
        spt.smenu.clear();
    }
}


spt.ctx_menu.test = function( evt, bvr )
{
    spt.js_log.debug( "---------------------------------------------------------------------------------" );
    spt.js_log.debug( "*** GOT call to spt.ctx_menu.test()" );
    spt.js_log.debug( "---------------------------------------------------------------------------------" );
}


spt.ctx_menu.submenu_entry_over = function( evt, bvr, mouse_411 )
{
    spt.mouse.default_add_class_on_hover_over( evt, bvr, mouse_411 );

    var target = document.id(spt.get_event_target(evt));
    var menu = target.getParent(".SPT_CTX_MENU");

    if( spt.ctx_menu.stack.length > menu.spt_ctx_menu_stack_number ) {
        var higher_menu = spt.ctx_menu.stack[menu.spt_ctx_menu_stack_number];
        if( higher_menu.id != bvr.options.submenu_id ) {
            // means the submenu is from a different entry ...
            spt.ctx_menu.clear_higher( menu.spt_ctx_menu_stack_number );
        }
    }

    if( spt.ctx_menu.stack.length == menu.spt_ctx_menu_stack_number ) {
        spt.ctx_menu.show_on_submenu_activate_cbk( evt, bvr );
    }
}


spt.ctx_menu.submenu_entry_out = function( evt, bvr, mouse_411 )
{
    spt.mouse.default_add_class_on_hover_out( evt, bvr, mouse_411 );
}


spt.ctx_menu.entry_over = function( evt, bvr, mouse_411 )
{
    spt.mouse.default_add_class_on_hover_over( evt, bvr, mouse_411 );

    var target = document.id(spt.get_event_target(evt));
    var menu = target.getParent(".SPT_CTX_MENU");
    spt.ctx_menu.clear_higher( menu.spt_ctx_menu_stack_number );
}


spt.ctx_menu.entry_out = function( evt, bvr, mouse_411 )
{
    spt.mouse.default_add_class_on_hover_out( evt, bvr, mouse_411 );
}


spt.ctx_menu.option_clicked_cbk = function( evt, bvr )
{
    // This is a wrapper function to call that ensures the context menus are cleared from view
    // before the actual action occurs in the desired inner call-back specified in the 'options'
    // value of the bvr spec ...
    //
    spt.ctx_menu.clear();
    spt.smenu.clear();

    if( ('options' in bvr) && ('inner_cbk' in bvr['options']) ) {
        var stmt = 'var ret = ' + bvr.options.inner_cbk + '(evt,bvr)';
        eval( stmt );
        return ret;
    }

    return false;
}


spt.ctx_menu.show_on_context_click_cbk = function( evt, menu_id )
{
    spt.ctx_menu.clear();
    spt.smenu.clear();
    spt.ctx_menu._show_action( evt, menu_id, null, false );
}


spt.ctx_menu.show_on_dropdown_click_cbk = function( evt, bvr )
{
    var menu = spt.ctx_menu.get_bottom();

    spt.ctx_menu.clear();
    spt.smenu.clear();
    menu_id = bvr.options.menu_id;

    if( ! menu || ( menu.get('id') != menu_id ) ) {
        spt.ctx_menu._show_action( evt, menu_id, bvr, true );
    }
}


spt.ctx_menu.show_on_submenu_activate_cbk = function( evt, bvr )
{
    if( spt.force_default_context_menu ) {
        spt.force_default_context_menu = false;
        return true;
    }

    menu_id = bvr.options.menu_id;
    spt.ctx_menu._show_action( evt, menu_id, bvr, false );

    return false;
}


spt.ctx_menu._show_action = function( evt, menu_id, bvr, is_dropdown )
{
    if( ! evt ) { evt = window.event; }  // IE compat.

    var activator_el = null;
    var popup = null;
    if( bvr ) {
        activator_el = document.id(bvr.src_el);
        
    } else {
        activator_el = document.id(spt.get_event_target( evt ));
    }

    

    var nudge_horiz = 0;
    if( activator_el.getProperty("spt_nudge_menu_horiz") ) {
        nudge_horiz = parseInt( activator_el.getProperty("spt_nudge_menu_horiz") );
    }
    var nudge_vert = 0;
    if( activator_el.getProperty("spt_nudge_menu_vert") ) {
        nudge_vert = parseInt( activator_el.getProperty("spt_nudge_menu_vert") );
    }

    var menu = document.id(menu_id);
    menu.setStyle("display", "block");
    
    popup = activator_el.getParent('.SPT_Z');
    // move the zIndex of context menu up for popup menu
    if (popup) {
        menu.setStyle("zIndex", parseInt(popup.getProperty('spt_z_start')) + 101);
    }
    if( "spt_defer_click_off" in menu ) {
        delete menu.spt_defer_click_off;
    }

    if( bvr ) {
        if( is_dropdown ) {
            var activator = document.id(bvr.src_el);
            var abs_offset = spt.get_absolute_offset(activator);
            menu.setStyle("left", (abs_offset.x + nudge_horiz));
            menu.setStyle("top" , (abs_offset.y + activator.clientHeight - 1 + nudge_vert));

            if( spt.ctx_menu.use_defer_click_off ) {
                menu["spt_defer_click_off"] = 1;
            }
        }
        else {
            var entry_el = bvr.src_el;
            var abs_offset = spt.get_absolute_offset(entry_el);

            menu.setStyle("left", (abs_offset.x + entry_el.clientWidth + nudge_horiz));
            menu.setStyle("top" , (abs_offset.y + nudge_vert));
        }
    }
    else {
        var cursor_pos = spt.mouse.get_abs_cusor_position(evt);

        menu.setStyle("left", (cursor_pos.x + nudge_horiz));
        menu.setStyle("top",  (cursor_pos.y + nudge_vert));
    }

    // Attach the activating element, that generated the event causing this menu to open, to the menu top element ...
    //
    menu.spt_ctx_menu_source = activator_el;

    spt.ctx_menu.stack.push( menu );
    menu.spt_ctx_menu_stack_number = spt.ctx_menu.stack.length;

    spt.halt_event_here( evt );


    // reposition if offscreen
    var size = menu.getSize();
    var pos = menu.getPosition();
    var win_size = document.id(document.body).getSize();

    var body = document.id(document.body);
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


spt.ctx_menu.get_activator = function( bvr )
{
    var menu = document.id(bvr.src_el).getParent('.SPT_CTX_MENU');
    var activator = null;

    while( true ) {
        var source = menu.spt_ctx_menu_source;
        if( ! source.hasClass("SPT_CTX_MENU_SUBMENU") ) {
            activator = source;
            break;
        }

        // otherwise keep looping ...
        menu = source.getParent('.SPT_CTX_MENU');
    }

    return activator;
}

// ----------------------------------------------------------------------------------------------------------------
//  Smart Context menu dynamic menu-entry info setup call-backs
// ----------------------------------------------------------------------------------------------------------------
//
spt.smenu_ctx = {};


spt.smenu_ctx.setup_cbk = function( menu_el, activator_el )
{
    var el_name = activator_el.getProperty("spt_element_name");
    if (el_name == null) {
        el_name = 'no_name';
    }

    var setup_info = {
        'is_groupable' : spt.is_TRUE( activator_el.getProperty("spt_widget_is_groupable") ),
        'is_time_groupable' : spt.is_TRUE( activator_el.getProperty("spt_widget_is_time_groupable") ),
        'is_sortable' : spt.is_TRUE( activator_el.getProperty("spt_widget_is_sortable") ),
        'is_searchable' : spt.is_TRUE( activator_el.getProperty("spt_widget_is_searchable") ),
        'element_name' : el_name.substr(0,1).toUpperCase() + el_name.substr(1),
        'sort_prefix': activator_el.getProperty("spt_widget_sort_prefix"),
        'has_related' : spt.is_TRUE( activator_el.getProperty("spt_widget_has_related") ),
    };


    return setup_info;
}



