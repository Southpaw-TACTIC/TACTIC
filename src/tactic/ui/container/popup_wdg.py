############################################################
#
# Copyright (c) 2005, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#
__all__ = ["PopupWdg"]

from pyasm.common import Common, Container
from pyasm.web import *
from pyasm.widget import IconWdg

from tactic.ui.common import BaseRefreshWdg


class PopupWdg(BaseRefreshWdg):
    '''Container widget which creates a popup on the screen.  This popup
    window current has a title widget and a content widget

    Popup contains special functionality regarding the existence of a
    "spt_popup_body" class in combination with a "spt_popup_header"
    and/or "spt_popup_footer" class within an html body.

    When "spt_popup_body" and one or both of "spt_popup_header"
    "spt_popup_footer" exist, popup applies a scrollbar to the div
    containing spt_popup_body as opposed to the container div. 

    It should be noted that popup will not rearrange or separate the
    header and footer, meaning that the order in which you add the 
    elements still matters. 

    @usage
    popup = PopupWdg(id='name')
    popup.add("My Title", "title")
    popup.add("This is Content", "content")
    '''
    RIGHT = 'right'
    BOTTOM = 'bottom'

    def get_args_keys(my):
        return {
            'id': 'The id of the top widget',
            'width': 'The width of the popup',
            'opacity': 'Float value (0.0 to 1.0) to set opacity to, for page blocking background',
            'allow_page_activity': 'Flag to specify whether or not to use a background to block and disable page ' \
                                   ' while popup is open. This flag is False by default.',
            'z_start': 'Integer value equal to one of: 100, 200, 300, 400, 500, etc. ... this now defaults to 200 ' \
                       'which is what most popup windows should be set to.',
            'destroy_on_close': 'Boolean value, if True then the close button destroys the popup instead of just ' \
                                'hiding it.',
            'aux_position': 'position of the auxilliary panel',
            'display': 'true|false - determines whether to display the popup initially',
            'allow_close': 'true|false - determines whether this popup can be explicitly closed by the user'
        }


    def init(my):
        my.name = my.kwargs.get('id')
        if not my.name:
            my.name = 'popup'

        my.allow_page_activity = False
        if my.kwargs.get('allow_page_activity'):
            my.allow_page_activity = True

        my.z_start = 200
        if my.kwargs.get('z_start'):
            my.z_start = my.kwargs.get('z_start')


        # TODO: make 'destroy_on_close' the default behavior for popups ... do this when there is a chance to go
        #        through and convert all uses of PopupWdg, making sure that ones that need to not be destroyed
        #        can changed appropriately. Currently default is for the popup to be hidden only on 'close'.
        #
        #        NOTE: destroy_on_close will lose the popup window's last position ... do we really want to
        #              make it the default?
        #
        my.destroy_on_close = False


        if my.kwargs.get('destroy_on_close'):
            my.destroy_on_close = True

        my.allow_close = True
        if my.kwargs.get('allow_close') in ['false', 'False', False]:
            my.allow_close = False


        my.aux_position = my.kwargs.get('aux_position')
        if my.aux_position:
            assert my.aux_position in [my.RIGHT, my.BOTTOM]
        
        my.content_wdg = Widget()
        my.title_wdg = Widget()
        my.aux_wdg = Widget()

    def get_cancel_script(my):

        #TODO: when the add_named_listener is fixed, will add these closing function into the listener
        cbjs_action = '''
            var popup=spt.popup.get_popup( bvr.src_el );
            var popup_id = popup.id;
            spt.named_events.fire_event('preclose_' + popup_id, {});
        '''

        if my.destroy_on_close:
            cbjs_action = '%s; spt.popup.destroy( popup );'% cbjs_action
        else:
            cbjs_action = '%s; spt.popup.close( spt.popup.get_popup( popup ) );'% cbjs_action

        return cbjs_action

    def get_show_script(my):
        cbjs_action = 'spt.popup.open( spt.popup.get_popup( bvr.src_el ) );'
        return cbjs_action

    def get_show_aux_script(my):
        cbjs_action = "spt.show('%s')" % my.get_aux_id()
        return cbjs_action

    def get_cancel_aux_script(my):
        cbjs_action = "spt.hide('%s')" % my.get_aux_id()
        return cbjs_action

    def get_aux_id(my):
        return '%s_Aux' % my.name

    def add_title(my, widget):
        my.title_wdg.add(widget)

    def add_aux(my, widget):
        my.aux_wdg.add(widget)

    def add(my, widget, name=None):
        if name == 'content':
            my.content_wdg = widget
        elif name == 'title':
            my.title_wdg = widget
        else:
            my.content_wdg.add(widget, name)
        

    def get_display(my):

        div = DivWdg()

        if not Container.get_dict("JSLibraries", "spt_popup"):
            div.add_style("position: fixed")
            div.add_style("top: 0px")
            div.add_style("left: 0px")
            div.add_style("opacity: 0.4")
            div.add_style("background", "#000")
            div.add_style("padding: 100px")
            div.add_style("height: 100%")
            div.add_style("width: 100%")
            div.add_class("spt_popup_background")
            div.add_style("display: none")
            div.add_style("z-index: 2")
            div.add_behavior( {
                'type': 'click_up',
                'cbjs_action': '''
                spt.hide(bvr.src_el);
                '''
            } ) 

        Container.put("PopupWdg:background", True)


        widget = DivWdg()
        div.add(widget)
        widget.add_class("spt_popup")



        if not Container.get_dict("JSLibraries", "spt_popup"):
            widget.add_behavior( {
                'type': 'load',
                'cbjs_action': my.get_onload_js()
            } )


        width = my.kwargs.get("width")
        if not width:
            width = 10

        web = WebContainer.get_web()


        widget.set_id(my.name)
        if my.kwargs.get("display") == "true":
            pass
        else:
            widget.add_style("display: none")

        widget.add_style("position: absolute")
        widget.add_style("left: 400px")
        widget.add_style("top: 100px")

        widget.add_border()
        widget.add_color("background", "background")

        #widget.set_box_shadow(color="#000")
        widget.set_box_shadow()


        table = Table()
        table.add_behavior( {
        'type': 'load',
        'width': width,
        'cbjs_action': '''
        bvr.src_el.setStyle("width", bvr.width)

        var popup = bvr.src_el.getParent(".spt_popup");
        var window_size = $(window).getSize();
        var size = bvr.src_el.getSize();
        var left = window_size.x/2 - size.x/2;
        var top = window_size.y/2 - size.y/2;
        popup.setStyle("left", left);
        //popup.setStyle("top", top);

        var content = popup.getElement(".spt_popup_content");
        content.setStyle("max-height", window_size.y - 100);
        content.setStyle("overflow-y", "auto");

        '''
        } )



        table.add_row()

        content_td = table.add_cell()
        content_td.add_class("css_shadow_td")

        drag_div = DivWdg()

        #from tactic.ui.container import ArrowWdg
        #arrow = ArrowWdg()
        #drag_div.add(arrow)


        my.add_header_context_menu(drag_div)


        # create the 'close' button ...
        if my.allow_close:
            close_wdg = SpanWdg(css='spt_popup_close')
            #close_wdg.add( IconWdg("Close", IconWdg.POPUP_WIN_CLOSE) )
            close_wdg.add( IconWdg("Close", "BS_REMOVE") )
            close_wdg.add_style("margin: 5px 1px 3px 1px")
            close_wdg.add_style("float: right")
            close_wdg.add_class("hand")

            close_wdg.add_behavior({
                'type': 'click_up',
                'cbjs_action': my.get_cancel_script()
            })

            drag_div.add(close_wdg)


            # create the 'minimize' button ...
            minimize_wdg = SpanWdg(css='spt_popup_min')
            minimize_wdg.add_style("margin: 5px 1px 3px 1px")
            #minimize_wdg.add( IconWdg("Minimize", IconWdg.POPUP_WIN_MINIMIZE) )
            minimize_wdg.add( IconWdg("Minimize", "BS_MINUS") )
            minimize_wdg.add_style("float: right")
            minimize_wdg.add_class("hand")
            behavior = {
                'type': 'click_up',
                'cbjs_action': "spt.popup.toggle_minimize( bvr.src_el );"
            }
            minimize_wdg.add_behavior( behavior );
            drag_div.add(minimize_wdg)

        #-- TO ADD SOON -- create the 'refresh' button ...
        #   refresh_wdg = SpanWdg()
        #   refresh_wdg.add( IconWdg("Refresh Popup", IconWdg.POPUP_WIN_REFRESH) )
        #   refresh_wdg.add_style("float: right")
        #   refresh_wdg.add_class("hand")
        #   behavior = {
        #       'type': 'click_up',
        #       'cbjs_action': "spt.popup.toggle_minimize( bvr.src_el );"
        #   }
        #   refresh_wdg.add_behavior( behavior );
        #   drag_div.add(refresh_wdg)

        width = my.kwargs.get("width")

        # style
        drag_div.add_style("font-size: 1.1em")

        drag_div.add_style("text-align: left")
        drag_div.add_class("spt_popup_width")

        drag_handle_div = DivWdg(id='%s_title' %my.name)
        drag_handle_div.add_style("padding: 6px;")
        #drag_handle_div.add_gradient("background", "background", +10)
        drag_handle_div.add_color("background", "background", -5)
        drag_handle_div.add_color("color", "color")
        drag_handle_div.add_style("font-weight", "bold")
        drag_handle_div.add_style("font-size", "12px")


        # add the drag capability.
        # NOTE: need to use getParent because spt.popup has not yet been
        # initialized when this is processed
        shadow_color = drag_div.get_color("shadow")
        drag_div.add_behavior( {
            'type':'smart_drag',
            'shadow_color': shadow_color,
            'drag_el': "@.getParent('.spt_popup')",
            'bvr_match_class': 'spt_popup_title',
            'options': {'z_sort': 'bring_forward'},
            'ignore_default_motion': 'true',
            "cbjs_setup": '''
              if (spt.popup.is_minimized(bvr.src_el)) {
                return;
              }

              if (spt.popup.is_background_visible) {
                  spt.popup.offset_x = document.body.scrollLeft;
                  spt.popup.offset_y = document.body.scrollTop;
                  spt.popup.hide_background();
                  var parent = bvr.src_el.getParent(".spt_popup");
                  parent.setStyle("box-shadow","0px 0px 20px " + bvr.shadow_color);
              }
              else {
                  spt.popup.offset_x = 0;
                  spt.popup.offset_y = 0;
              }
            ''',
            "cbjs_motion": '''
              if (spt.popup.is_minimized(bvr.src_el)) {
                return;
              }

              mouse_411.curr_x += spt.popup.offset_x;
              mouse_411.curr_y += spt.popup.offset_y;
              spt.mouse.default_drag_motion(evt, bvr, mouse_411);
            ''',
            "cbjs_action": ''
        } )


        
        title_wdg = my.title_wdg
        if not title_wdg:
            title_wdg = "No Title"
        #else:
        #    title_wdg = title_wdg

        drag_handle_div.add_behavior({
            'type': 'double_click',
            'cbjs_action': my.get_cancel_script()
        })


        drag_handle_div.add(title_wdg)
        drag_handle_div.add_class("spt_popup_title")


        # add a context menu
        from tactic.ui.container.smart_menu_wdg import SmartMenu
        SmartMenu.assign_as_local_activator( drag_handle_div, 'HEADER_CTX' )
        drag_handle_div.add_attr("spt_element_name", "Test Dock")



        # add the content
        content_div = DivWdg()
        content_div.add_color("color", "color2")
        #content_div.add_color("background", "background2")
        from pyasm.web.palette import Palette
        palette = Palette.get()
        content_div.add_color("color", "color2")
        content_div.add_color("background", "background2")

        content_div.add_style("margin", "0px, -1px -0px -1px")

        content_div.set_id("%s_content" % my.name)
        content_div.add_class("spt_popup_content")
        content_div.add_style("overflow: hidden")
        content_div.add_style("display: block")
        #content_div.add_style("padding: 10px")
        if not my.content_wdg:
            my.content_wdg = "No Content"
        content_div.add_color("background", "background")

        content_div.add(my.content_wdg)

        drag_div.add( drag_handle_div )
        my.position_aux_div(drag_div, content_div)
        content_td.add(drag_div)
        widget.add(table)

        # ALWAYS make the Popup a Page Utility Widget (now processed client side)
        widget.add_class( "SPT_PUW" )

        if my.z_start:
            widget.set_z_start( my.z_start )
            widget.add_style("z-index: %s" % my.z_start)
        else:
            widget.add_style("z-index: 102")


        # add the resize icon
        icon = IconWdg( "Resize", IconWdg.RESIZE_CORNER )
        icon.add_style("cursor: nw-resize")
        icon.add_style("z-index: 1000")
        icon.add_class("spt_popup_resize")
        #icon.add_style("float: right")
        icon.add_style("position: absolute")
        icon.add_style("bottom: 0px")
        icon.add_style("right: 0px")
        #icon.add_style("margin-top: -15px")
        icon.add_behavior( {
        'type': 'drag',
        "drag_el": '@',
        "cb_set_prefix": 'spt.popup.resize_drag'
        } )

        content_td.add(icon)

        #return widget
        return div



    def add_header_context_menu(my, widget):
        from menu_wdg import Menu, MenuItem
        menu = Menu(width=180)
        menu.set_allow_icons(False)
        menu.set_setup_cbfn( 'spt.smenu_ctx.setup_cbk' )


        menu_item = MenuItem(type='title', label='Actions')
        menu.add(menu_item)

        menu_item = MenuItem(type='action', label='Reload')
        menu.add(menu_item)
        menu_item.add_behavior( {
            'cbjs_action': '''
            var header = spt.smenu.get_activator(bvr);
            var top = header.getParent(".spt_popup");
            var content_top = top.getElement(".spt_popup_content");
            var content = content_top.getElement(".spt_panel");
            spt.panel.refresh(content);
            '''
        } )


        menu_item = MenuItem(type='separator')
        menu.add(menu_item)

        menu_item = MenuItem(type='action', label='Dock Window')
        menu_item.add_behavior( {
            'cbjs_action': '''
            var header = spt.smenu.get_activator(bvr);
            var top = header.getParent(".spt_popup");
            var content = top.getElement(".spt_popup_content");
            var title = top.getElement(".spt_popup_title")
            var title = title.innerHTML;
            //var element_name = header.getAttribute("spt_element_name");

            spt.tab.set_main_body_tab();

            var html = content.innerHTML;

            spt.tab.add_new(title, title);
            spt.tab.load_html(title, html);

            spt.popup.close(top);
            '''
        } )
        menu.add(menu_item)


        menu_item = MenuItem(type='action', label='Open in Browser')
        menu.add(menu_item)
        menu_item.add_behavior( {
            'cbjs_action': '''
            var header = spt.smenu.get_activator(bvr);
            var top = header.getParent(".spt_popup");
            var content = top.getElement(".spt_popup_content");

            var html = content.innerHTML;
            var url = spt.Environment.get().get_server_url();
            var project = spt.Environment.get().get_project();
            var url = url + "/tactic/"+project+"/#//widget/tactic.ui.container.EmptyWdg";

            spt.app_busy.show("Copying to new browser window");
            var win = window.open(url);
            setTimeout( function() {
                var empty_el = $(win.document).getElement(".spt_empty_top");
                spt.behavior.replace_inner_html(empty_el, html);
                spt.app_busy.hide();
            }, 2000 );

            //spt.popup.close(top);
            '''
        } )







        menus = [menu.get_data()]
        menus_in = {
            'HEADER_CTX': menus,
        }
        from tactic.ui.container.smart_menu_wdg import SmartMenu
        SmartMenu.attach_smart_context_menu( widget, menus_in, False )




    def position_aux_div(my, drag_div, content_div):
        # add the aux div
        # add optional aux div
        if not my.aux_position:
            drag_div.add(content_div)
            return
        content_table = Table()
        content_table.add_row()

        aux_div = DivWdg(id=my.get_aux_id())
        aux_div.add_style("display: none")

        aux_div_content = DivWdg(id='%s_Content' %my.get_aux_id())
        aux_div_content.add(my.aux_wdg)
        aux_div.add( aux_div_content )

        if my.aux_position == my.RIGHT:
            content_table.add_cell(content_div)
            content_table.add_cell(aux_div)
            drag_div.add(content_table)
        elif my.aux_position == my.BOTTOM:
            drag_div.add(content_div)
            drag_div.add(aux_div)
        else:
            drag_div.add(content_div)
            drag_div.add(aux_div)


    def get_onload_js(my):
        return r'''

if (spt.z_index) {
    return;
}


spt.Environment.get().add_library("spt_popup");


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

    spt.popup.show_background();


    // @@@
    var rsw_content_box = popup.getElement(".SPT_RSW_CONTENT_BOX");
    if( rsw_content_box ) {
        alert("WARNING: resize_scroll dependency");
        spt.resize_scroll.adjust_for_scroll( rsw_content_box );
    }

    spt.popup.get_focus( popup );
}


spt.popup.close = function( popup_el_or_id , fade, close_fn)
{
    var popup = spt.popup._get_popup_from_popup_el_or_id( popup_el_or_id );
    popup = popup ? popup : spt.popup.get_popup(popup_el_or_id);

    if (!popup) return;

    if (fade) {
        popup.fade('out').get('tween').chain(
        function(){ 
            spt.hide( popup );
            if (close_fn) close_fn();
        });
    }
    else {
        spt.hide( popup );
    }
    spt.popup.hide_all_aux_divs( popup, fade );


    if( popup == spt.popup._focus_el ) {
        spt.popup.release_focus( spt.popup._focus_el );
    }
    spt.popup.hide_background();
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


spt.popup.hide_all_aux_divs = function( popup_el_or_id, fade )
{
    var popup = $(popup_el_or_id);
    var aux_divs = popup.getElements('.SPT_AUX');
    for( var c=0; c < aux_divs.length; c++ )
    {
        var aux = aux_divs[c];
        if (fade)
            aux.fade('out');
        else
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


spt.popup.destroy = function( popup_el_or_id, fade )
{
    var popup = $(popup_el_or_id);

    var is_minimized = popup.hasClass("spt_popup_minimized");

    var destroy_fn = function() {
        spt.behavior.destroy_element( popup );
    }
    if (fade) {
        spt.popup.close( popup, fade, destroy_fn );
    }
    else {
        spt.popup.close( popup);
        console.log(spt.behavior.destroy_element);
        spt.behavior.destroy_element( popup );
        //destroy_fn();
    }

    if (is_minimized) { 
        var els = $(document.body).getElements(".spt_popup_minimized");
        for (var i = 0; i < els.length; i++) {
            els[i].setStyle("left", i*205);
        }
    }

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
    var resize = options["resize"];
    var on_close = options["on_close"];
    var allow_close = options["allow_close"];

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

    var close_wdg = popup.getElement('.spt_popup_close');
    var min_wdg = popup.getElement('.spt_popup_min');
    if ([false, 'false'].contains(allow_close)) {
        spt.hide(close_wdg);
        spt.hide(min_wdg);
    }
    else {
        spt.show(close_wdg);
        spt.show(min_wdg);
    }
    // display the popup clone, and bring it forward on top of other popups ...
    // but put it off screen first
    popup.setStyle("left", "-10000px");
    var cbjs_action;
    if (typeof on_close == "function") {
        cbjs_action = String(on_close) + "; on_close();";
    }
    else {
        cbjs_action = on_close;
    }
    spt.behavior.add(popup, {'type':'listen', 'event_name':"preclose_" + popup_id, 'cbjs_action': cbjs_action});
    spt.popup.open( popup );

    // add the place holder
    var content_wdg = popup.getElement(".spt_popup_content");
    spt.behavior.replace_inner_html( content_wdg, '<div style="font-size: 1.2em; margin: 20px; text-align: center">' +
                                '<img src="/context/icons/common/indicator_snake.gif" border="0"> Loading ...</div>' );


    // get the content container
    var width_wdg = popup.getElement(".spt_popup_width");
    width_wdg.setStyle("min-width", "200px");
    if (width != null) {
        //width_wdg.setStyle("width", width);
        var content = popup.getElement(".spt_popup_content");
        content.setStyle("width", width);
    }
    if (height != null) {
        width_wdg.setStyle("height", height);
        width_wdg.setStyle("overflow", "auto");
    }
   
    // If specified, turn off ability to resize
    var resize_icon = popup.getElement(".spt_popup_resize");
    if (resize == "false" || resize == false) {
        resize_icon.setStyle("display", "none");
    }

    // replace the title
    if (title != null) {
        var title_wdg = popup.getElement(".spt_popup_title");
        spt.behavior.replace_inner_html( title_wdg, title );
    }


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


     var callback = function() {

        // place in the middle of the screen
        var size = popup.getSize();
        var body = document.body;
        var win_size = $(window).getSize();
        var offset = $(window);
        var xpos = win_size.x / 2 - size.x / 2 + 0*body.scrollLeft;
        var ypos = win_size.y / 2 - size.y / 2 + 0*body.scrollTop;
        if (xpos < 0) {
            xpos = 0;
        }
        if (ypos < 0) {
            ypos = 0;
        }
        popup.setStyle("top", ypos);
        popup.setStyle("left", xpos);
        popup.setStyle("margin-left", 0);
        popup.setStyle("position", "fixed");

        spt.popup.show_background();

    };

    var widget_html = options.html;
    if ( widget_html != null) {
        spt.behavior.replace_inner_html( content_wdg, widget_html );
        popup.setStyle("margin-left", 0);
        callback();
        return popup
    }

    // load the content
    var server = TacticServerStub.get();
    var values = {};
    if (bvr.values) {
        values = bvr.values;
    }
    var kwargs = {'args': args, 'values': values};


    //the following code deals with a specified header/footer + body
    var widget_html = server.get_widget(class_name, kwargs);

    spt.behavior.replace_inner_html( content_wdg, widget_html );

    var popup_header = content_wdg.getElement(".spt_popup_header");
    var popup_body = content_wdg.getElement(".spt_popup_body");
    var popup_footer = content_wdg.getElement(".spt_popup_footer");

    var popup_header_height = 0;
    var popup_footer_height = 0;

    var window_size = $(window).getSize();

    if (popup_body && (popup_header || popup_footer)) {
        if (popup_header) {
            popup_header_height = $(popup_header).getSize().y;
        }
        if (popup_footer) {
            popup_footer_height = $(popup_footer).getSize().y;
        }

        var window_size = $(window).getSize();
        content_wdg.setStyle("overflow-y","hidden");
        content_wdg.setStyle("max-height", "auto");
        popup_body.setStyle("overflow-y","auto");
        popup_body.setStyle("overflow-x", "hidden");
        var max_height = window_size.y - 200 - popup_header_height - popup_footer_height;
        popup_body.setStyle("max-height", max_height);
    }

    setTimeout(function(){callback()}, 10);

    return popup;
}


spt.popup.is_background_visible = false;

spt.popup.show_background = function() {
    spt.popup.is_background_visible = true;
    var bkg = $(document.body).getElements(".spt_popup_background");
    spt.show( bkg[bkg.length-1] );
}

spt.popup.hide_background = function() {
    spt.popup.is_background_visible = false;
    var bkg = $(document.body).getElements(".spt_popup_background");
    spt.hide( bkg[bkg.length-1] );
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


spt.popup.is_minimized = function( src_el ) {
    var popup = spt.popup.get_popup(src_el);
    return popup.hasClass("spt_popup_minimized");
}


spt.popup.toggle_minimize = function( src_el )
{
    spt.toggle_show_hide( spt.get_cousin( src_el, '.spt_popup', '.spt_popup_content' ) );

    var popup = spt.popup.get_popup(src_el);
    var resize = popup.getElement(".spt_popup_resize");

    if (spt.popup.is_minimized(popup)) {

        popup.setStyle("bottom", "");
        popup.setStyle("right", "");

        popup.setStyle("top", popup.last_top);
        popup.setStyle("left", popup.last_left);

        popup.removeClass("spt_popup_minimized");
        spt.popup.show_background();

        resize.setStyle("display", "");

    }
    else {

        popup.last_top = popup.getStyle("top");
        popup.last_left = popup.getStyle("left");

        popup.setStyle("top", "");
        popup.setStyle("right", "");
        popup.setStyle("bottom", "2px");

        var minimized = $(document.body).getElements(".spt_popup_minimized");
        var num = minimized.length * 205;

        popup.setStyle("left", num+"px");

        resize.setStyle("display", "none");

        popup.addClass("spt_popup_minimized");
        spt.popup.hide_background();
    }

}


spt.popup._check_focus_by_target = function( target )
{
    if( ! target ) {
        return;
    }
    var target = $(target);

    var popup = null;

    //if( target.hasClass('spt_popup') ) {
    if( spt.has_class(target, 'spt_popup') ) {
        popup = target;
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

    // remove the max height requirement
    content.setStyle("max-height", "");
    content.setStyle("overflow-y", "auto");

}


spt.popup.resize_drag_motion = function(evt, bvr, mouse_411) {

    var top = bvr.src_el.getParent(".spt_popup");
    var content = top.getElement(".spt_popup_content");
    var diff = { x: mouse_411.curr_x - spt.popup.last_resize_pos.x, y: mouse_411.curr_y - spt.popup.last_resize_pos.y };

    content.setStyle("width", spt.popup.last_size.x+diff.x);
    content.setStyle("height", spt.popup.last_size.y+diff.y);

}

        '''



            
