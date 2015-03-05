###########################################################
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

__all__ = ['FingerMenuWdg', 'MenuWdg', 'GearMenuWdg','Menu','MenuItem']

from pyasm.common import Common, TacticException
from pyasm.web import HtmlElement, SpanWdg, DivWdg, FloatDivWdg, WebContainer, Widget, Table

from tactic.ui.common import BaseRefreshWdg

from smart_menu_wdg import SmartMenu


class FingerMenuWdg(BaseRefreshWdg):
    '''Container widget contains a menu.  Each child widget is a selection
    item. Best used for a small menu for individual table element widgets

    @usage
    menu = FingerMenuWdg(mode='horizontal', width=40, height =18,  top_class='note_edit_panel')
    menu_item = MenuItem('action', label='edit')
    menu_item.add_behavior({'type': 'click', 'cbjs_action': 'spt.alert(123)'})
    menu.add(menu_item)
    '''
    def __init__(my, **kwargs):
        super(FingerMenuWdg, my).__init__(**kwargs)
        my.items = []
        # this css class identifies a container for the MenuWdg in which one can store hidden input and other info
        my.menu_top_class = kwargs.get('top_class')
        assert my.menu_top_class

    def get_args_keys(my):
        return {
        'id': 'The id of the top widget',
        'width': 'The width of the popup',
        'background': 'style of background',
        'font_size': 'font size of menu item',
        'mode': 'horizontal|veritcal',
        'top_class': "a css class that uniquely identifies this menu's container",
        'force': 'left|right'
        }

    def add(my, menu_item):
        my.items.append(menu_item)

    def _add_spacer_row(my, menu_table, height, label_width):
        tbody = menu_table.add_tbody()
        tbody.add_style("display","table-row-group")
        tr = menu_table.add_row()
        tr.add_looks( "smenu" )

        # label
        td = menu_table.add_cell()
        td.add_style("width", ("%spx" % label_width))
        td.add_style("height", ("%spx" % height))

     
    def init(my):
        my.mode = my.kwargs.get('mode')
        if not my.mode:
            my.mode = 'vertical'

   

    def set_activator_over(my, item, activator_match_class, activator_parent_class='', js_action='', top_class='', offset={'x':0, 'y':0}):
        '''usually called in handle_layout_behaviours() for best relay expectation 
        
            @item: the layout widget (i.e. TableLayoutWdg) to add this behavior to
            @activator_match_class: class of the element to appear beside when the mouse fires mouseover
            @activator_parent_class: (optional) class of the element assigned to menu.activator_el 
                (a close parent of the element with activator_match_class). It could be more precise when used as position reference
            @top_class: a common top class for all: this defaults to spt_table
            @js_action: extra js action one can run when the mouse is over the activator'''


        main_action = '''
            var menu_top = bvr.src_el.getParent('.' + bvr.top_class).getElement('.' + bvr.menu_top_class);
            var menu = menu_top.getElement('.spt_menu_top');
            // don't use getSize()
    
            var menu_width = 100;
            var finger_div = menu.getElement('.spt_finger_menu');
            if (finger_div) 
                menu_width = parseInt(finger_div.getStyle('width'), 10);

            var activator_parent = bvr.activator_parent_class ? bvr.src_el.getParent('.' + bvr.activator_parent_class) : bvr.src_el;

            var panel = bvr.src_el.getParent(".spt_popup");

            var pos = bvr.src_el.getPosition();

            var body = $(document.body);
            var scroll_top = body.scrollTop;
            var scroll_left = body.scrollLeft;
            pos.x = pos.x - scroll_left;
            pos.y = pos.y - scroll_top;


            var size = activator_parent.getSize();
            var x_offset = size ?  size.x : 400;
            var client_width = document.body.clientWidth;
            /*
            console.log("offset_X " + x_offset)
            console.log("pos X " + pos.x)
            console.log("menu width" + menu_width)
            */
            var is_left;
            var force = finger_div.getAttribute("spt_finger_force");
            if (force) {
                is_left = force == "left"; 
            }
            else if ((x_offset+ pos.x + menu_width) > client_width ) {
                is_left = true;
            }
            
            // store the variable for activator out calculation
            menu_top.is_left = is_left;

            if (is_left) {
                pos.x = pos.x - menu_width + 3;
                if (finger_div) {
                    finger_div.setStyle("border-width", "1px 0px 1px 1px");
                    finger_div.setStyle("border-radius", "12px 0px 0px 12px");
                    finger_div.setStyle("padding-left", "10px");
                    finger_div.setStyle("padding-right", "0px");
                }
            }
            else {
                pos.x = pos.x + x_offset;
                if (finger_div) {
                    finger_div.setStyle("border-width", "1px 1px 1px 0px");
                    finger_div.setStyle("border-radius", "0px 12px 12px 0px");
                    finger_div.setStyle("padding-left", "0px");
                    finger_div.setStyle("padding-right", "10px");
                }
            }




            if (menu_top) {
                //for refresh purpose called by the menu_item's cbjs_action
                menu.activator_el = activator_parent;
                menu_top.position({position: 'upperLeft', relativeTo: body, offset: pos});

                //menu_top.setStyle("left", left_pos);
                //menu_top.setStyle("top", pos.y );
                menu_top.setStyle("z-index", 1000);
                spt.show(menu_top);
                spt.show(menu);
                spt.body.add_focus_element(menu_top);
            }
        '''

        if not top_class:
            top_class = "spt_table"

        if js_action:
            main_action = '''%s
                            %s'''%(main_action, js_action)
        item.add_relay_behavior({
             'type': 'mouseover',
                'bvr_match_class': activator_match_class,
                'activator_parent_class': activator_parent_class,
                'top_class': top_class,
                'menu_top_class': my.menu_top_class,
                'cbjs_action': main_action,
                'offset': offset
                })
        
    def set_activator_out(my, item, activator_match_class, top_class='', js_action=''):
        ''' usually called in handle_layout_behaviours() for best relay performance 
        
            @item: the layout widget (i.e. TableLayoutWdg) to add this behavior to
            @activator_match_class: class of the elemnent from which the mouse fires mouseleave to hide the menu
            @top_class: a common top class for all: this defaults to spt_table
            @js_action: extra js action one can run when the mouse is leaving the activator'''

        main_action =  '''

                 var target = spt.get_event_target( evt );

                 var edit_menu = bvr.src_el.getParent('.'+bvr.top_class).getElement('.' + bvr.menu_top_class);
                 if (!edit_menu) {
                     log.critical('edit_menu not found!')
                     //return;
                 }
                 else {
                     var menu_pos = edit_menu.getPosition();
                     
                     // when is_left, evt.x tends to be 80 pixels bigger, so increase the tolerance
                     var tolerance =  edit_menu.is_left ? 5000 : 1500;

                     var diff = (menu_pos.x - evt.page.x) * (menu_pos.y - evt.page.y);
                     if (Math.abs(diff) > tolerance) {
                         spt.hide(edit_menu);
                     }
                     else {
                         spt.finger_menu.timeout_id = setTimeout( function() {
                             spt.hide(edit_menu);
                         }, 500 )
                    }
                }
                '''

        if not top_class:
            top_class = "spt_table"

        if js_action:
            main_action = '''%s
                            %s'''%(main_action, js_action)
        item.add_relay_behavior({
                'type': 'mouseleave',
                'bvr_match_class': activator_match_class,
                'menu_top_class': my.menu_top_class,
                'top_class': top_class,
                'cbjs_action': main_action
            } )



    def get_display(my):

        #content.add_event("oncontextmenu", "spt.side_bar.manage_context_menu_action_cbk(); return false")
        context_menu = DivWdg()
        context_menu.add_class('spt_menu_top')
        context_menu.add_behavior( {
            'type': 'load',
            'cbjs_action': '''
            spt.finger_menu = {};
            spt.finger_menu.timeout_id = -1;
            '''
        } )
        context_menu.add_behavior( {
            'type': 'mouseover',
            'cbjs_action': '''
            if (spt.finger_menu.timeout_id != -1) {
                clearTimeout(spt.finger_menu.timeout_id);
                spt.finger_menu.timeout_id = -1;
            }
            '''
        } )

 


        #context_menu.set_box_shadow(color='#fff')
        # this may not be needed as it is set in JS
        context_menu.add_style("z-index: 200")

        # set up what happens when the mouse leaves the actual menu
        my._set_menu_out(context_menu)


        width = my.kwargs.get('width')
        height = my.kwargs.get('height')
        if not height:
            height = 20
        if not width:
            width = 35
        font_size = my.kwargs.get('font_size')
        if not font_size:
            font_size = 'smaller'


        force = my.kwargs.get("force")

        if my.mode == 'horizontal':
            div = DivWdg(css='spt_finger_menu')
            if force:
                div.add_attr("spt_finger_force", force)

            div.add_style("border-color: #aaa")
            div.add_style("border-style: solid")

            if force == "left":
                div.add_style("border-width: 1px 0px 1px 1px")
                div.add_style("border-radius: 12px 0px 0px 12px")
            else:
                div.add_style("border-width: 1px 1px 1px 0px")
                div.add_style("border-radius: 0px 12px 12px 0px")


            div.set_box_shadow(value="0px 0px 2px 1px")
            #div.add_style("z-index: 1000")

            total_width = width * len(my.items) + 15
            div.add_style('width', total_width)
            div.add_styles('height: %spx; padding: 2px;' %height)
            context_menu.add(div)

            div.add_color('background','background', -10)
            palette = div.get_palette()

            sb_title_bg = palette.color('side_bar_title')
            bg_color = div.get_color('background', -10)
            color = div.get_color('color')
            
            for item in my.items:
                mouse_enter_bvr = {'type':'mouseenter', 'cbjs_action': '''
                    bvr.src_el.setStyles({'background': '%s', 'color': 'white'})''' %sb_title_bg}
                mouse_leave_bvr = {'type':'mouseleave', 'cbjs_action': '''
                    bvr.src_el.setStyles({'background': '%s', 'color': '%s'})''' %(bg_color, color)}

                menu_item = FloatDivWdg(css='unselectable hand')
                menu_item.add_color('background','background', -10)
                menu_item.add(item.get_option('label'))

                menu_item.add_behavior( mouse_enter_bvr )
                menu_item.add_behavior( mouse_leave_bvr )

                # add the passed-in bvr
                bvr = item.get_option('bvr_cb')
                menu_item.add_behavior(bvr )


                menu_item.add_styles('margin: 0px 0 0 0; padding: 2px 0 2px 0; text-align: center; font-size: %s; width: %s; height: %spx'%(font_size, width, height-4))
                menu_item.add_behavior({'type': 'click_up',
                    'cbjs_action': '''var menu = bvr.src_el.getParent('.spt_menu_top'); spt.hide(menu);'''})
                div.add(menu_item)
        
        else:
            # this width only matters in vertical mode
            context_menu.add_style("width: %s" %width)
            menu_table = Table()
            menu_table.add_styles( "text-align: left; text-indent: 4px; border-collapse: collapse; cell-padding: 8px; border-radius: 32px;" )
            context_menu.add(menu_table)
            my._add_spacer_row(menu_table, 3, width)
            for widget in my.widgets:
                tbody = menu_table.add_tbody()
                tbody.add_style("display","table-row-group")

               
                tr = menu_table.add_row()
                tr.add_looks( "smenu" )
                #tr.add_class( "SPT_SMENU_ENTRY" )
                hover_bvr = {'type':'hover', 'add_looks': 'smenu_hilite'}
                                 #'cbjs_action_over': 'spt.smenu.entry_over( evt, bvr );',
                                 #'cbjs_action_out': 'spt.smenu.entry_out( evt, bvr );' }
                tr.add_behavior( hover_bvr )


                menu_item = menu_table.add_cell()
                font_size = '4px'
                menu_item.add_styles('padding: 0px 0 0 6px; font-size: %s; width: %s; height: 16px'%(font_size, width))
                menu_item.add_behavior({'type': 'click_up',
                    'cbjs_action': '''var menu = bvr.src_el.getParent('.spt_menu_top'); spt.hide(menu);'''})
                menu_item.add(widget)

               

            my._add_spacer_row(menu_table, 3, width)

        return context_menu

    def _set_menu_out(my, item):
        ''' set up what happens when the mouse leaves the actual menu. It stays on for 4 secs'''
        item.add_behavior({
               'type': 'mouseleave',
                'cbjs_action': '''
                var edit_menus = document.getElements('.spt_menu_top');

                setTimeout(function(){
                   for (var i = 0; i < edit_menus.length; i++) {
                        
                       var edit_menu = edit_menus[i];
                       var menu_pos = edit_menu.getPosition();
                       var diff = (menu_pos.x - evt.page.x) * (menu_pos.y - evt.page.y);

                       // smaller tolerance here, but with 4 seconds delay
                       if (Math.abs(diff) > 500) {
                           spt.hide(edit_menu);
                       }
                    }
                }, 4000);

              
                '''
                })





# DEPRECATED: use FingerMenuWdg
class MenuWdg(FingerMenuWdg):
    pass






class GearMenuWdg(BaseRefreshWdg):

    def init(my):
        my.btn_dd = DivWdg()
        my.menus = []

    def add_style(my, name, value=None):
        my.btn_dd.add_style(name, value)


    def add(my, menu):
        my.menus.append(menu.get_data())


    def get_display(my):


        # create the gear menu
        btn_dd = my.btn_dd
        btn_dd.add_styles("width: 36px; height: 18px; padding: none; padding-top: 1px;")

        btn_dd.add( "<img src='/context/icons/common/transparent_pixel.gif' alt='' " \
                    "title='TACTIC Actions Menu' class='tactic_tip' " \
                    "style='text-decoration: none; padding: none; margin: none; width: 4px;' />" )
        btn_dd.add( "<img src='/context/icons/silk/cog.png' alt='' " \
                    "title='TACTIC Actions Menu' class='tactic_tip' " \
                    "style='text-decoration: none; padding: none; margin: none;' />" )
        btn_dd.add( "<img src='/context/icons/silk/bullet_arrow_down.png' alt='' " \
                    "title='TACTIC Actions Menu' class='tactic_tip' " \
                    "style='text-decoration: none; padding: none; margin: none;' />" )

        btn_dd.add_behavior( { 'type': 'hover',
                    'mod_styles': 'background-image: url(/context/icons/common/gear_menu_btn_bkg_hilite.png); ' \
                                    'background-repeat: no-repeat;' } )
        smenu_set = SmartMenu.add_smart_menu_set( btn_dd, { 'DG_TABLE_GEAR_MENU': my.menus } )
        SmartMenu.assign_as_local_activator( btn_dd, "DG_TABLE_GEAR_MENU", True )
        return btn_dd






class Menu(object):
    def __init__(my, menu_tag_suffix='MAIN', width=110, allow_icons=False):
        my.opt_spec_list = []
        my.data = { 'menu_tag_suffix': menu_tag_suffix, 'width': width, 'opt_spec_list': my.opt_spec_list}

    def add(my, menu_item):
        options = menu_item.get_options()
        my.opt_spec_list.append(options)

    def set_menu_tag_suffix(my, suffix):
        my.data['menu_tag_suffix'] = suffix


    def get_data(my):
        return my.data

    def add_option(name, value):
        my.data[name] = value

    def set_allow_icons(my, flag=True):
        my.data['allow_icons'] = flag

    def set_setup_cbfn(my, func):
        my.data['setup_cbfn'] = func




class MenuItem(object):
    def __init__(my, type, label="Label", icon=None):

        assert type in ['title', 'action', 'submenu', 'separator']

        if type == 'separator':
            my.options = { "type": type }
        else:
            if icon:

                my.options = { "type": type, "label": label, "icon": icon }
            else:
                my.options = { "type": type, "label": label }

    def get_options(my):
        return my.options

    def get_option(my, key):
        return my.options.get(key)

    def set_option(my, key, value):
        my.options[key] = value


    def set_type(my, type):
        my.options['type'] = type
        
    def set_label(my, label):
        my.options['label'] = label
        
    def set_icon(my, icon):
        my.options['icon'] = icon
        
    def set_behavior(my, behavior):
        my.options['bvr_cb'] = behavior

    def add_behavior(my, behavior):
        my.options['bvr_cb'] = behavior
 

    def set_submenu_tag_suffix(my, suffix):
        my.options['submenu_tag_suffix'] = suffix



