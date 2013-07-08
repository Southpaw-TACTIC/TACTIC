###########################################################
#
# Copyright (c) 2009, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#
__all__ = ["EfficientTableExampleWdg"]

from pyasm.web import DivWdg, HtmlElement, SpanWdg, Table, WebContainer
from pyasm.widget import SelectWdg, WidgetConfig, IconWdg

from tactic.ui.container import SmartMenu

from base_example_wdg import BaseExampleWdg



class EfficientTableExampleWdg(BaseExampleWdg):

    def get_example_title(my):
        return "Distributed Drag Behaviors &amp; Smart Context Menus"


    def get_example_description(my):
        return "Example of using distributed drag behaviors and smart menus, that are defined once on a parent " \
                "element and then utilized by (and actions run on) various child elements that are 'tagged' to " \
                "use the drag behavior or 'tagged' to a given smart menu.<br/><br/>" \
                "There are only 2 drag behaviors specified here, both ont he 'table' element, but the actions " \
                "occur at the table cell level. You can drag and drop table cells (but not header cells) into " \
                "other table cells. Also, you can drag the right cell borders to resize columns.<br/><br/>" \
                "Additionally, there are two subsets of smart menus set up ... the whole smart menu set " \
                "(including both subsets) is attached to the div containing the table, and the activation " \
                "of each smart menu subset is assigned to the table cells (not the headers). Even column " \
                "cells will get the 'DOG' subset context menu, and the odd column cells will get the 'CAT' " \
                "subset context menu."
    
    
    def get_example_display(my):

        div = DivWdg()

        # Smart Menu data ...
        dog_menus = [ my.get_sm_dog_main_menu_details(),
                      my.get_sm_dog_submenu_one_details(),
                      my.get_sm_dog_submenu_two_details()
                    ]

        cat_menus = [ my.get_sm_cat_main_menu_details() ]

        SmartMenu.attach_smart_context_menu( div, { 'DOG': dog_menus, 'CAT': cat_menus }, False )



        table = Table(css="maq_view_table")
        table.set_id( "main_body_table" )
        table.add_class("spt_table")

        table.add_behavior( { "type": "smart_drag",
                              "bvr_match_class": "SPT_DO_RESIZE",
                              "cbjs_setup": 'spt.dg_table.resize_column_setup( evt, bvr, mouse_411 );',
                              "cbjs_motion": 'spt.dg_table.resize_column_motion( evt, bvr, mouse_411 );'
                             } )

        table.add_behavior( { "type": "smart_drag",
                              "bvr_match_class": "SPT_DO_DRAG",
                              "use_copy": 'true',
                              "use_delta": 'true', 'dx': 10, 'dy': 10,
                              "drop_code": 'TableExampleSwitchContents',
                              "cbjs_action": "spt.ui_play.drag_cell_drop_action( evt, bvr );",
                              "copy_styles": 'background: blue; opacity: .5; border: 1px solid black; text-align: left;'
                             } )

        row = table.add_row()
        for c in range(10):
            th = table.add_header()
            th.set_attr('col_idx', str(c))
            th.add_class("cell_left")
            th.add_styles("width: 150px; cursor: default;")

            # @@@
            th.add_behavior( {
                "type": "move",
                "cbjs_action": '''
                    // log.debug( "(x,y) = (" + mouse_411.curr_x + "," + mouse_411.curr_y + ")" );
                    spt.ui_play.header_half_move_cbk( evt, bvr, mouse_411 );
                ''',
                "cbjs_action_on": '''
                    // log.debug( "START MY MOVE!" );
                ''',
                "cbjs_action_off": '''
                    // log.debug( "DONE MY MOVE!" );
                    spt.ui_play.header_half_move_off_cbk( evt, bvr, mouse_411 );
                '''
            } )

            if (c%2):
                th.add("H%s (Cat)" % c)
            else:
                th.add("H%s (Dog)" % c)
            th_resize = table.add_cell()
            th_resize.set_attr('col_idx', str(c+1))
            th_resize.add_class("SPT_DO_RESIZE cell_right")
            th_resize.add_styles("width: 4px; cursor: col-resize;")

        for r in range(19):
            row = table.add_row()
            for c in range(10):
                col = table.add_cell()
                col.set_attr('col_idx', str(c))
                col.set_attr('SPT_ACCEPT_DROP', 'TableExampleSwitchContents')
                col.add_class("SPT_DO_DRAG cell_left")
                col.add_styles("cursor: pointer;")
                col.add("(%s,%s)" % (r,c))
                if (c % 2) == 0:
                    SmartMenu.assign_as_local_activator( col, "DOG" )
                else:
                    SmartMenu.assign_as_local_activator( col, "CAT" )
                resize = table.add_cell()
                resize.set_attr('col_idx', str(c+1))
                resize.add_class("SPT_DO_RESIZE cell_right")
                resize.add_styles("width: 6px; cursor: col-resize;")

        div.add( table )
        return div


    # menu_tag_suffix is 'MAIN' or 'SUB1' or 'SUB2', etc
    #
    def get_sm_dog_main_menu_details(my):
        return { 'menu_tag_suffix': 'MAIN', 'width': 200, 'opt_spec_list': [
            { "type": "action", "label": "Dog Launches JS Logger",
                    "bvr_cb": {'cbjs_action': "spt.js_log.show();"} },

            { "type": "action", "label": "Dog runs Command cbk",
                    "bvr_cb": {'cbjs_action': "spt.ctx_menu.option_clicked_cbk( evt, bvr );",
                               'options': {'inner_cbk': 'spt.ctx_menu.test'}} },

            { "type": "action", "label": "Dog Open File",
                    "bvr_cb": {'cbjs_action': "alert('Open File clicked!');"},
                    "icon": IconWdg.LOAD },

            { "type": "action", "label": "Dog Makes cell RED",
                    "bvr_cb": {'cbjs_action': "spt.smenu.get_activator(bvr).setStyle('background','#FF0000');"} },

            { "type": "separator" },

            { "type": "toggle", "label": "Dog's Silky Smooth Work-flow", "state": True },
            { "type": "toggle", "label": "Is Dog a Cool cat?", "state": False },

            { "type": "action", "label": "Dog shows Browser Info!",
                    "bvr_cb": {'cbjs_action': "spt.js_log.show(); spt.browser.show_info(); log.warning('DOG!');"},
                    "icon": IconWdg.INFO },

            { "type": "title", "label": "Crazy Dog Options" },

            { "type": "submenu", "label": "Sub-menu 1", "submenu_tag_suffix": "SUB_1" },
            { "type": "submenu", "label": "Sub-menu 2", "submenu_tag_suffix": "SUB_2" }
        ] }


    def get_sm_dog_submenu_one_details(my):
        return { 'menu_tag_suffix': 'SUB_1', 'width': 250, 'opt_spec_list': [
            { "type": "submenu", "label": "Nested Sub-menu", "submenu_tag_suffix": "SUB_2" },

            { "type": "separator" },

            { "type": "action", "label": "Sub-menu launch JS Logger",
                    "bvr_cb": {'cbjs_action': "spt.js_log.show();"} },
            { "type": "action", "label": "Open Folder",
                    "bvr_cb": {'cbjs_action': "alert('Sub-menu Open File clicked!');"}, "icon": IconWdg.LOAD },

            { "type": "separator" },

            { "type": "action", "label": "Make activator_el GREEN",
                    # -- NOTE: the example below shows how to get to the activator_el ... just use the convenience
                    #          function 'spt.ctx_menu.orig_activator(bvr)' ... you just need to provide the call
                    #          with the bvr. This works for sub-menus as well.
                    "bvr_cb": {'cbjs_action': "spt.smenu.get_activator(bvr).setStyle('background','#006600');"} },

            { "type": "action", "label": "Make Awesome Popup ...",
                    "bvr_cb": {'cbjs_action': "alert('Popping up Awesomeness!');"} },
            # { "type": "separator" },
            # { "type": "submenu", "label": "Additional Nested Sub-menu", "submenu_id": "CtxMenu_Mike_Submenu_Three" }
        ] }

    def get_sm_dog_submenu_two_details(my):
        return { 'menu_tag_suffix': 'SUB_2', 'width': 250, 'opt_spec_list': [
            { "type": "action", "label": "Make activator_el BLACK",
                    "bvr_cb": {'cbjs_action': "spt.smenu.get_activator(bvr).setStyle('background','#000000');"} },

            { "type": "title", "label": "A Nested Sub-menu" },
            { "type": "action", "label": "Sub-menu 2 launch JS Logger",
                    "bvr_cb": {'cbjs_action': "spt.js_log.show();"} },
            { "type": "action", "label": "Open Folder 2",
                    "bvr_cb": {'cbjs_action': "alert('Sub-menu 2 Open File clicked!');"}, "icon": IconWdg.LOAD },
            { "type": "action", "label": "Make Even More Awesome Popup ...",
                    "bvr_cb": {'cbjs_action': "alert('Popping up Much More Awesomeness!');"} }
        ] }


    def get_sm_cat_main_menu_details(my):
        return { 'menu_tag_suffix': 'MAIN', 'width': 200, 'opt_spec_list': [
            { "type": "title", "label": "Cell contains: {cell_contents}" },

            { "type": "separator", "weight": "heavy" },

            { "type": "action", "label": "Cat Launches JS Logger",
                    "bvr_cb": {'cbjs_action': "spt.js_log.show();"} },

            { "type": "action", "label": "Cat Open File",
                    "bvr_cb": {'cbjs_action': "alert('Open File clicked!');"},
                    "icon": IconWdg.LOAD },

            { "type": "action", "label": "Cat Makes cell Orange",
                    "enabled_check_setup_key" : "is_cat_entry_ok",
                    "bvr_cb": {'cbjs_action': "spt.smenu.get_activator(bvr).setStyle('background','orange');"} },

            { "type": "action", "label": "Cat Makes cell Red",
                    "enabled_check_setup_key" : "is_cat_entry_ok",
                    "hide_when_disabled" : True,
                    "bvr_cb": {'cbjs_action': "spt.smenu.get_activator(bvr).setStyle('background','red');"} },

            { "type": "action", "label": "Cat Makes cell Yellow",
                    "enabled_check_setup_key" : "is_cat_entry_ok",
                    "hide_when_disabled" : True,
                    "bvr_cb": {'cbjs_action': "spt.smenu.get_activator(bvr).setStyle('background','yellow');"} },

            { "type": "separator" },

            { "type": "action", "label": "Cat's Browser info!",
                    "bvr_cb": {'cbjs_action': "spt.js_log.show(); spt.browser.show_info(); log.warning('CAT!');"},
                    "icon": IconWdg.INFO }
            ],
            'setup_cbfn':  'spt.smenu.test.cat_menu_setup_cbk'
        }




