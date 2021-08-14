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

    def get_args_keys(self):
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


    def init(self):
        self.name = self.kwargs.get('id')
        if not self.name:
            self.name = 'popup'

        self.allow_page_activity = False
        if self.kwargs.get('allow_page_activity'):
            self.allow_page_activity = True

        self.z_start = 200
        if self.kwargs.get('z_start'):
            self.z_start = self.kwargs.get('z_start')


        # TODO: make 'destroy_on_close' the default behavior for popups ... do this when there is a chance to go
        #        through and convert all uses of PopupWdg, making sure that ones that need to not be destroyed
        #        can changed appropriately. Currently default is for the popup to be hidden only on 'close'.
        #
        #        NOTE: destroy_on_close will lose the popup window's last position ... do we really want to
        #              make it the default?
        #
        self.destroy_on_close = False


        if self.kwargs.get('destroy_on_close'):
            self.destroy_on_close = True

        self.allow_close = True
        if self.kwargs.get('allow_close') in ['false', 'False', False]:
            self.allow_close = False


        self.aux_position = self.kwargs.get('aux_position')
        if self.aux_position:
            assert self.aux_position in [self.RIGHT, self.BOTTOM]
        
        self.content_wdg = Widget()
        self.title_wdg = Widget()
        self.aux_wdg = Widget()

    def get_cancel_script(self):
        
        #TODO: when the add_named_listener is fixed, will add these closing function into the listener
        cbjs_action = '''
            var popup=spt.popup.get_popup( bvr.src_el );
            var popup_id = popup.id;
            spt.named_events.fire_event('preclose_' + popup_id, {});
        '''

        if self.destroy_on_close:
            cbjs_action = '%s; spt.popup.destroy( popup );'% cbjs_action
        else:
            cbjs_action = '%s; spt.popup.close( spt.popup.get_popup( popup ) );'% cbjs_action

        return cbjs_action

    def get_show_script(self):
        cbjs_action = 'spt.popup.open( spt.popup.get_popup( bvr.src_el ) );'
        return cbjs_action

    def get_show_aux_script(self):
        cbjs_action = "spt.show('%s')" % self.get_aux_id()
        return cbjs_action

    def get_cancel_aux_script(self):
        cbjs_action = "spt.hide('%s')" % self.get_aux_id()
        return cbjs_action

    def get_aux_id(self):
        return '%s_Aux' % self.name

    def add_title(self, widget):
        self.title_wdg.add(widget)

    def add_aux(self, widget):
        self.aux_wdg.add(widget)

    def add(self, widget, name=None):
        if name == 'content':
            self.content_wdg = widget
        elif name == 'title':
            self.title_wdg = widget
        else:
            self.content_wdg.add(widget, name)
        

    def get_bootstrap_styles(self):
              
        style = HtmlElement.style(""" 
     
        /* HACK */
        .spt_popup_top.spt_popup {
            overflow: unset;
        }
        
        .modal-backdrop {
            z-index: 150 !important;
        }

        .spt_popup_top.spt_popup_minimized {
            top: unset;
            right: unset;
        }

        .spt_popup_top .spt_popup_title_top { 
            display: flex;
            align-items: center;
            justify-content: space-between;
            cursor: move;
        }
    
        @media (min-width: 576px) {
            .spt_popup_top .spt_popup_title {
                margin: .25rem;
            }
            
            .spt_popup_top.spt_popup {
                width: fit-content;
                height: fit-content;
            }

            .spt_popup_top .modal-dialog {
                margin: 0; 
                pointer-events: unset;
                max-width: fit-content;
            }

            .spt_popup_top .spt_popup_width {
                width: fit-content;
            }

        }
 
  
        @media (max-width: 575.98px) { 
            .spt_popup_top.spt_popup {
                top: 0 !important;
                left: 0 !important;
            }

            .spt_popup_top .spt_popup_title_top { 
                padding: 1rem;
                border-bottom: 1px solid #e9ecef;
                border-top-left-radius: .3rem;
                border-top-right-radius: .3rem;
            }
        }
                """)
        
        return style 


    def get_styles(self):
        
        # Style of title_div
        div = DivWdg()
        palette = div.get_palette()
        background = palette.color("background", -5)

        text_color = palette.color("color")
        
        style = HtmlElement.style()
        style.add('''
        
            .spt_popup_title {
                font-weight: bold;
                font-size: 12px;
                padding: 6px;
                color: %s;    
                background: %s;
            }
        
        ''' % (text_color, background))
       
            
        style.add('''
            .spt_popup_close {
                margin: 8px 1px 3px 2px;
            }

        ''')
        
       
        border_color = palette.color("border")

        style.add('''
            .spt_popup {
                border-style: solid;
                border-width: 1px;
                border-color: %s;
                position: absolute;
                background: rgb(255, 255, 255);
                box-shadow: rgba(0, 0, 0, 0.1) 0px 0px 20px;
                margin-left: 0px;
            }

        ''' % border_color)

        style.add('''

            .spt_popup_background {
                position: fixed;
                top: 0px;
                left: 0px;
                opacity: 0.4;
                background: rgb(0, 0, 0);
                padding: 100px;
                height: 100%;
                width: 100%;
                z-index: 2;
            }
        ''')


        style.add(''' 
        
            .spt_popup_content { 
                color: rgb(51, 51, 51);
                background: rgb(255, 255, 255);
                margin: 0px -1px;
                width: 100%;
                overflow: hidden auto;
            }        
        ''')


        style.add('''
        
        .spt_popup_width {
            font-size: 1.1em;
            text-align: left;
            min-width: 200px;
        }

        ''')


        return style 


    def get_display(self):

        div = DivWdg()

        if not Container.get_dict("JSLibraries", "spt_popup"):
            #TODO: Remove
            div.add_class("spt_popup_background")
            div.add_style("display: none")
            div.add_behavior( {
                'type': 'click_up',
                'cbjs_action': '''
                spt.hide(bvr.src_el);
                '''
            } ) 

        Container.put("PopupWdg:background", True)


        widget = DivWdg()
        div.add(widget)
       
        #widget.add_class("spt_popup_top")
        widget.add_class("spt_popup_top")
        widget.add_class("modal")
        widget.add_attr("data-backdrop", "static")
        widget.add_class("spt_popup")
        
        


        if not Container.get_dict("JSLibraries", "spt_popup"):
            widget.add_behavior( {
                'type': 'load',
                'cbjs_action': self.get_onload_js()
            } )


        width = self.kwargs.get("width")
        if not width:
            width = 10

        web = WebContainer.get_web()


        widget.set_id(self.name)
        if self.kwargs.get("display") == "true":
            pass
        else:
            widget.add_style("display: none")

        content_td = DivWdg()
        content_td.add_class("css_shadow_td")
        content_td.add_class("modal-dialog")
 
        drag_div = DivWdg()
        drag_div.add_class("spt_popup_width")
        drag_div.add_class("modal-content")

        self.add_header_context_menu(drag_div)
     
        popup_title_top = DivWdg()
        drag_div.add(popup_title_top)
        popup_title_top.add_class("spt_popup_title_top")
        
        drag_handle_div = DivWdg(id='%s_title' %self.name)
        popup_title_top.add(drag_handle_div)

        # create the 'close' button ...
        if self.allow_close:

            button_wdg = DivWdg()
            button_wdg.add_class("d-flex")
            popup_title_top.add(button_wdg)

            from tactic.ui.widget import ButtonNewWdg
            close_wdg = DivWdg()
            close_wdg.add_class("spt_popup_close")

            close_btn = ButtonNewWdg(title="Close", icon="FAS_WINDOW_CLOSE")
            close_wdg.add(close_btn)

            close_wdg.add_behavior({
                'type': 'click_up',
                'cbjs_action': self.get_cancel_script()
            })



            # create the 'minimize' button ...
            minimize_wdg = DivWdg()
            minimize_wdg.add_class("spt_popup_min")
            
            minimize_btn = ButtonNewWdg(title="Minimize", icon="FAS_WINDOW_MINIMIZE")
            minimize_btn.add_class("spt_minimize", redirect=False)
           
            maximum_wdg = DivWdg()
            maximize_btn = ButtonNewWdg(title="Maximize", icon="FAS_WINDOW_MAXIMIZE")
            maximize_btn.add_class("spt_maximize", redirect=False)
            maximize_btn.add_style("display: none")

            minimize_wdg.add( minimize_btn )
            minimize_wdg.add( maximize_btn )
            minimize_wdg.add_style("float: right")
            minimize_wdg.add_class("hand")
            behavior = {
                'type': 'click_up',
                'cbjs_action': "spt.popup.toggle_minimize( bvr.src_el );"
            }
            minimize_wdg.add_behavior( behavior )
            
            
            
            button_wdg.add(minimize_wdg)
            button_wdg.add(close_wdg)





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

        width = self.kwargs.get("width")

        # style


        # add the drag capability.
        # NOTE: need to use getParent because spt.popup has not yet been
        # initialized when this is processed
        drag_div.add_behavior( {
            'type':'smart_drag',
            'drag_el': "@.getParent('.spt_popup')",
            'bvr_match_class': 'spt_popup_title_top',
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
              } else {
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


        
        title_wdg = self.title_wdg
        if not title_wdg:
            title_wdg = "No Title"

        drag_handle_div.add_behavior({
            'type': 'double_click',
            'cbjs_action': self.get_cancel_script()
        })


        drag_handle_div.add(title_wdg)
        drag_handle_div.add_class("spt_popup_title")


        # add a context menu
        from tactic.ui.container.smart_menu_wdg import SmartMenu
        SmartMenu.assign_as_local_activator( drag_handle_div, 'HEADER_CTX' )
        drag_handle_div.add_attr("spt_element_name", "Test Dock")



        # add the content
        content_div = DivWdg()
        content_div.set_id("%s_content" % self.name)
        content_div.add_class("spt_popup_content")
        if not self.content_wdg:
            self.content_wdg = "No Content"

        content_div.add(self.content_wdg)

        self.position_aux_div(drag_div, content_div)
        content_td.add(drag_div)
        widget.add(content_td)

        # ALWAYS make the Popup a Page Utility Widget (now processed client side)
        widget.add_class( "SPT_PUW" )

        if self.z_start:
            widget.set_z_start( self.z_start )
            widget.add_style("z-index: %s" % self.z_start)
        else:
            widget.add_style("z-index: 102")

        # add the resize icon
        icon = IconWdg( "Resize", IconWdg.RESIZE_CORNER )
        icon.add_style("cursor: nw-resize")
        icon.add_style("z-index: 1000")
        icon.add_class("spt_popup_resize")
        icon.add_style("position: absolute")
        icon.add_style("bottom: 0px")
        icon.add_style("right: 0px")
        icon.add_behavior( {
        'type': 'drag',
        "drag_el": '@',
        "cb_set_prefix": 'spt.popup.resize_drag'
        } )

        content_td.add(icon)

        if self._use_bootstrap():
            div.add(self.get_bootstrap_styles())
        else:
            div.add(self.get_styles())
        
        return div



    def add_header_context_menu(self, widget):
        from .menu_wdg import Menu, MenuItem
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
                var empty_el = document.id(win.document).getElement(".spt_empty_top");
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




    def position_aux_div(self, drag_div, content_div):
        # add the aux div
        # add optional aux div
        if not self.aux_position:
            drag_div.add(content_div)
            return
        content_table = Table()
        content_table.add_row()

        aux_div = DivWdg(id=self.get_aux_id())
        aux_div.add_style("display: none")

        aux_div_content = DivWdg(id='%s_Content' %self.get_aux_id())
        aux_div_content.add(self.aux_wdg)
        aux_div.add( aux_div_content )

        if self.aux_position == self.RIGHT:
            content_table.add_cell(content_div)
            content_table.add_cell(aux_div)
            drag_div.add(content_table)
        elif self.aux_position == self.BOTTOM:
            drag_div.add(content_div)
            drag_div.add(aux_div)
        else:
            drag_div.add(content_div)
            drag_div.add(aux_div)


    def get_onload_js(self):
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
    spt.z_index.bring_forward( document.id(spt.get_event_target(evt)) );
}


spt.z_index.bring_forward = function( target )
{
    if( target && ! target.hasClass("SPT_Z") ) {
        target = target.getParent(".SPT_Z");
    }
    if( ! target ) { return; }

    let z_el = target;
    let z_start_str = "" + z_el.getProperty("spt_z_start");
    let z_start_num = parseInt( z_start_str );

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

    let popup = null;

    if( spt.get_typeof( popup_el_or_id ) == 'string' ) {
        popup = document.id(popup_el_or_id);
        if( ! popup ) {
            if( ! suppress_errors ) {
                log.error( "ERROR in '" + fn_name + "' ... NO popup found with ID '" + popup_el_or_id + "'" );
            }
            return null;
        }
    }
    else {
        popup = document.id(popup_el_or_id);
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

    let popup = spt.popup._get_popup_from_popup_el_or_id( popup_el_or_id );
    if( ! popup ) { return; }
    $(popup_el_or_id).modal("show");

    backdrop = document.getElement(".modal-backdrop");
    if (backdrop) {
        bvr = {
            'type': 'click',
            'cbjs_action': 'bvr.src_el.destroy();'
        }
        spt.behavior.add(backdrop, bvr);
    }


    /* Disapper on click out
    popup.on_complete = function(el) {
        spt.popup.close(el);
    }
    popup.addClass("spt_popup_focus");
    spt.body.add_focus_element(popup);
    */

    return;

}


spt.popup.close = function( popup_el_or_id , fade, close_fn)
{
    
    
    let popup = spt.popup._get_popup_from_popup_el_or_id( popup_el_or_id );
    popup = popup ? popup : spt.popup.get_popup(popup_el_or_id);

    if (!popup) return;

    $(popup).modal("hide");

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
    let popup = spt.popup._get_popup_from_popup_el_or_id( popup_el_or_id );
    if( ! popup ) { return; }

    let display_style = popup.getStyle("display");
    if( display_style == "none" ) {
        spt.popup.open( popup, use_safe_position );
    } else {
        spt.popup.close( popup );
    }
}


spt.popup.hide_all_aux_divs = function( popup_el_or_id, fade )
{
    var popup = document.id(popup_el_or_id);
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
    let popup_drag = spt.z_index.get_z_el(popup);

    let check_left = popup.getProperty('spt_last_scroll_left');
    let check_top  = popup.getProperty('spt_last_scroll_top');

    if( ! check_left ) {
        popup.setProperty('spt_last_scroll_left','0');
    }
    if( ! check_top ) {
        popup.setProperty('spt_last_scroll_top','0');
    }

    let last_scroll_left = parseInt( popup.getProperty('spt_last_scroll_left') );
    let last_scroll_top  = parseInt( popup.getProperty('spt_last_scroll_top') );

    let body = document.body;

    let scroll_left = body.scrollLeft;
    let scroll_top = body.scrollTop;

    let curr_left = parseInt( popup_drag.getStyle("left") );
    let curr_top = parseInt( popup_drag.getStyle("top") );

    let pos_left = 0;
    let pos_top = 0;

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


    popup_drag.setStyle("left", pos_left);
    popup_drag.setStyle("top",  pos_top);

    popup.setProperty('spt_last_scroll_left', String(scroll_left));
    popup.setProperty('spt_last_scroll_top', String(scroll_top));
}


spt.popup.destroy = function( popup_el_or_id, fade )
{
    var popup = document.id(popup_el_or_id);
    if (!popup) return; 
    $(popup).modal("hide");

    var is_minimized = popup.hasClass("spt_popup_minimized");

    var destroy_fn = function() {
        spt.behavior.destroy_element( popup );
    }
    if (fade) {
        spt.popup.close( popup, fade, destroy_fn );
    }
    else {
        spt.popup.close( popup);
        spt.behavior.destroy_element( popup );
        //destroy_fn();
    }

    if (is_minimized) { 
        var els = document.id(document.body).getElements(".spt_popup_minimized");
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
    let options = bvr.options;


    let popup = null;


    let title = "-No Title-";
    if( bvr.options.hasOwnProperty("title") ) {
        title = bvr.options.title;
    }


    // replace the title
    let popup_id = bvr.options.popup_id;
    let display_title;
    if (!title) {
        display_title = "";
        title = "__COMMON__";
        if (!popup_id) {
            popup_id = "__COMMON__";
        }
    }
    else {
        display_title = title;
    }

    // If bvr has 'popup_id' then check if it already exists and use it (instead of cloning)
    if (popup_id) {
        popup = document.id(popup_id);
    }


    let class_name = null;
    if( bvr.options.hasOwnProperty("class_name") ) {
        class_name = bvr.options.class_name;
    } else {
        spt.js_log.warning("WARNING: No popup widget 'class_name' found in options for the following bvr ...");
        spt.js_log.warning( bvr );
        spt.js_log.warning("... ABORTING popup creation.");
        return;
    }

    let args = bvr.args;
    let kwargs = bvr.kwargs;

    let width = options["width"];
    let height = options["height"];
    let resize = options["resize"];
    let on_close = options["on_close"];
    let allow_close = options["allow_close"];
    let top_class = options["top_class"];


    // if load_once is true, just show the existing one
    if (popup && kwargs && kwargs['load_once']) {
        spt.popup.open( popup );
        return;
    }
    // Otherwise, we create a clone of the popup template ...
    let popup_template = null;
    if( ! popup ) {
        // get the common popup, clone it and fill it in
        let popup_template = document.id("popup_template");
        popup = spt.behavior.clone(popup_template);

        if( popup_id ) {
            popup.set("id", popup_id);
        } else {
            popup.set("id", spt.unique_id.get_next() + "_popup");
        }

        // If bvr has 'popup_parent_el' then put the popup as child to that ... otherwise, just add it to the
        // existing default popup container available to the page
        let popup_parent = null;
        if( bvr.options.hasOwnProperty("popup_parent_id") ) {
            popup_parent = document.id(bvr.options.popup_parent_id);
        }

        if( popup_parent ) {
            popup.inject( popup_parent, 'bottom' );
        } else {
            popup.inject(  document.id("popup_container"), 'bottom' );
        }
        spt.puw.process_new( popup.parentNode );
    }

    if (top_class) popup.addClass(top_class);

    let close_wdg = popup.getElement('.spt_popup_close');
    let min_wdg = popup.getElement('.spt_popup_min');
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
    let cbjs_action;
    if (typeof on_close == "function") {
        cbjs_action = String(on_close) + "; on_close();";
    }
    else {
        cbjs_action = on_close;
    }
    spt.behavior.add(popup, {'type':'listen', 'event_name':"preclose_" + popup_id, 'cbjs_action': cbjs_action});
    spt.popup.open( popup );

    // add the place holder
    let content_wdg = popup.getElement(".spt_popup_content");
    spt.behavior.replace_inner_html( content_wdg, '<div style="font-size: 1.2em; margin: 20px; text-align: center">' +
                                '<img src="/context/icons/common/indicator_snake.gif" border="0"> Loading ...</div>' );


    // get the content container
    let width_wdg = popup.getElement(".spt_popup_width");
    if (width != null) {
        //width_wdg.setStyle("width", width);
        let content = popup.getElement(".spt_popup_content");
        content.setStyle("width", width);
    }
    if (height != null) {
        width_wdg.setStyle("height", height);
        width_wdg.setStyle("overflow", "auto");
    }
   
    // If specified, turn off ability to resize
    let resize_icon = popup.getElement(".spt_popup_resize");
    if (resize == "false" || resize == false) {
        resize_icon.setStyle("display", "none");
    }
    let title_wdg = popup.getElement(".spt_popup_title");
    spt.behavior.replace_inner_html( title_wdg, display_title );


    // change position of popup to an offset from mouse position if offset options are provided in the bvr
    let pos = spt.mouse.get_abs_cusor_position(evt);
    if( bvr.options.hasOwnProperty("offset_x") ) {
        let offset_x = bvr.options.offset_x;
        popup.setStyle('left', pos.x + offset_x);
    }
    if( bvr.options.hasOwnProperty("offset_y") ) {
        let offset_y = bvr.options.offset_y;
        popup.setStyle('top', pos.y + offset_y);
    }


    // set the parameters for reload this popup
    content_wdg.setAttribute("spt_class_name", class_name);
    content_wdg.setAttribute("spt_kwargs", JSON.stringify(options));


    var callback = function() {

        // place in the middle of the screen
        let size = popup.getSize();
        let body = document.body;
        let win_size = document.id(window).getSize();
        let offset = document.id(window);
        let xpos = win_size.x / 2 - size.x / 2 + 0*body.scrollLeft;
        let ypos = win_size.y / 2 - size.y / 2 + 0*body.scrollTop;
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

        spt.z_index.bring_forward( spt.z_index.get_z_el(popup) )


        let content_size = content_wdg.getSize();
        let window_size = document.id(window).getSize();
        let max_height = window_size.y - 100;
        content_wdg.setStyle("max-height", max_height);
        if (content_size.y > max_height) {
            content_wdg.setStyle("height", max_height);
        }
        content_wdg.setStyle("max-height", max_height);

        let popup_body = content_wdg.getElement(".spt_popup_body");
        if (!popup_body) {
            content_wdg.setStyle("overflow-y", "auto");
        }


        spt.popup.show_background();

    };

    let widget_html = options.html;
    if ( widget_html != null) {
        spt.behavior.replace_inner_html( content_wdg, widget_html );
        popup.setStyle("margin-left", 0);
        callback();
        return popup
    }

    // load the content
    let server = TacticServerStub.get();
    let values = {};
    if (bvr.values) {
        values = bvr.values;
    }
    let content_kwargs = {'args': args, 'values': values};


    //the following code deals with a specified header/footer + body
    widget_html = server.get_widget(class_name, content_kwargs);

    spt.behavior.replace_inner_html( content_wdg, widget_html );

    var popup_header = content_wdg.getElement(".spt_popup_header");
    var popup_body = content_wdg.getElement(".spt_popup_body");
    var popup_footer = content_wdg.getElement(".spt_popup_footer");

    if (popup_header) popup_header.addClass("modal-header");
    if (popup_body) popup_body.addClass("modal-body");
    if (popup_footer) popup_footer.addClass("modal-footer")

    var popup_header_height = 0;
    var popup_footer_height = 0;

    var window_size = document.id(window).getSize();

    if (popup_body && (popup_header || popup_footer)) {
        if (popup_header) {
            popup_header_height = document.id(popup_header).getSize().y;
        }
        if (popup_footer) {
            popup_footer_height = document.id(popup_footer).getSize().y;
        }

        var window_size = document.id(window).getSize();
        content_wdg.setStyle("overflow","hidden");
        content_wdg.setStyle("max-height", "auto");
        popup_body.setStyle("overflow-y","auto");
        popup_body.setStyle("overflow-x", "hidden");

        var max_height = window_size.y - 150 - popup_header_height - popup_footer_height;
        popup_body.setStyle("max-height", max_height);
    }
    else {
        var max_height = window_size.y - 100;
        content_wdg.setStyle("max-height", max_height);
    }

    setTimeout(function(){callback()}, 10);

    return popup;
}


spt.popup.is_background_visible = false;

spt.popup.show_background = function() {
    spt.popup.is_background_visible = true;
    var bkg = document.id(document.body).getElements(".spt_popup_background");
    spt.show( bkg[bkg.length-1] );
}

spt.popup.hide_background = function() {
    spt.popup.is_background_visible = false;
    var bkg = document.id(document.body).getElements(".spt_popup_background");
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

    var header = popup.getElement(".spt_popup_min");

    min_icon = header.getElement(".spt_minimize")
    max_icon = header.getElement(".spt_maximize")

    if (spt.popup.is_minimized(popup)) {

        popup.setStyle("bottom", "");
        popup.setStyle("right", "");

        popup.setStyle("top", popup.last_top);
        popup.setStyle("left", popup.last_left);

        popup.removeClass("spt_popup_minimized");
        spt.popup.show_background();

        resize.setStyle("display", "");

        min_icon.setStyle("display", "inline-block")
        max_icon.setStyle("display", "none")


    }
    else {

        popup.last_top = popup.getStyle("top");
        popup.last_left = popup.getStyle("left");

        popup.setStyle("top", "");
        popup.setStyle("right", "");
        popup.setStyle("bottom", "2px");

        var minimized = document.id(document.body).getElements(".spt_popup_minimized");
        var num = minimized.length * 205;

        popup.setStyle("left", num+"px");

        resize.setStyle("display", "none");

        popup.addClass("spt_popup_minimized");
        spt.popup.hide_background();


        min_icon.setStyle("display", "none")
        max_icon.setStyle("display", "inline-block")
    }

}


spt.popup._check_focus_by_target = function( target )
{
    if( ! target ) {
        return;
    }
    var target = document.id(target);

    var popup = null;

    //if( target.hasClass('spt_popup') ) {
    if( spt.has_class(target, 'spt_popup') ) {
        popup = target;
    }

    if( ! popup ) {
        // FIXME: This is the same error as above.  IE does not return a mootools object with document.id(target).
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
    el = document.id(el);

    // First see if el is already a popup ...
    if( el.hasClass("SPT_IN_A_POPUP") ) {
        return el.getParent(".spt_popup")
    }

    // Otherwise continue on and process as a tear-away element ...
    var popup = null;

    // get the common popup, clone it and fill it in
    var popup_template = document.id("popup_template");
    // var popup = spt.behavior.clone(popup_template);  // PREVIOUS (doesn't work well in IE)
    //var popup = spt.behavior.duplicate_element( popup_template );
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



            
