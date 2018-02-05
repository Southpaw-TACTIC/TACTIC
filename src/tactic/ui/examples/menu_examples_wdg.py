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
__all__ = ["AllMenuExamplesWdg"]

from pyasm.web import DivWdg, HtmlElement, SpanWdg, Table, WebContainer
from pyasm.widget import SelectWdg, WidgetConfig, IconWdg

from tactic.ui.activator import ButtonForDropdownMenuWdg, AttachContextMenuWdg
from tactic.ui.container import SmartMenu

from base_example_wdg import BaseExampleWdg


class AllMenuExamplesWdg(BaseExampleWdg):

    def get_example_title(self):
        return "Menu and Smart Menu Examples"


    def get_example_description(self):
        return "Here are a number of examples demonstrating the original context and drop-down menu " \
                "implementations, along with the newer SmartMenu versions."


    def get_example_display(self):
        div = DivWdg()

        # ----------------------------- Smart Menu data ----------------------------------------------------------

        menus = [ self.get_smart_menu_main_menu_details(),
                  self.get_smart_menu_submenu_one_details(),
                  self.get_smart_menu_submenu_two_details()
                ]


        # ----------------------------- Smart Context Menu example -----------------------------------------------

        self.setup_next_example( div, "Smart Context Menu example ..." )

        ctx_click_div = DivWdg()
        ctx_click_div.add_styles("background: orange; color: white; border: 1px solid black; " \
                                 "padding: 10px; width: 100px;")
        ctx_click_div.add( "Right Click" )
        SmartMenu.attach_smart_context_menu( ctx_click_div, menus )

        div.add(ctx_click_div)

        # ----------------------------- Smart Drop-down Button Menu example --------------------------------------

        self.setup_next_example( div, "Smart Drop-down Button Menu example ..." )

        btn_dd = SmartMenu.get_smart_button_dropdown_wdg( "Hello", menus, 150 )
        div.add(btn_dd)

        # ----------------------------- Original Context Menu examples -------------------------------------------

        self.setup_next_example( div, "Original Context Menu examples ..." )

        # Create the element to right click on for the given main context menu ...
        activator = DivWdg()

        activator.add_style( "width: 300px" )
        activator.add_style( "height: 50px" )
        activator.add_style( "background: #660000" )
        activator.add_style( "text-align: center" )
        activator.add( "<br/>Right click on me!<br/>(this widget creates the context menus)" )

        s_menu_2 = self.get_ctx_sub_menu_two_details()
        s_menu_3 = {}
        s_menu_3.update( s_menu_2 )
        s_menu_3.update( { 'menu_id': "CtxMenu_Mike_Submenu_Three" } )

        ctx_menu = self.get_ctx_menu_details()
        menus = [ ctx_menu, self.get_ctx_sub_menu_details(), s_menu_2, s_menu_3 ]
        attach_ctx_menu_wdg = AttachContextMenuWdg( activator_wdg=activator, menus=menus )
        div.add( attach_ctx_menu_wdg )

        div.add( activator )
        div.add( "<br/><br/>" )

        # Create second context menu activator, but one that attaches to the already created context menus that
        # were generated above for the first activator. This allows for efficient use of context menus -- e.g.
        # you only need to actually generate one set, but still be able to use that same set of context menus
        # for all, say, edit cells of a DG table ...
        #
        activator2 = DivWdg()

        activator2.add_style( "width: 300px" )
        activator2.add_style( "height: 50px" )
        activator2.add_style( "background: #000066" )
        activator2.add_style( "text-align: center" )
        activator2.add( "<br/>Right click on me!<br/>(this widget attaches to already created context menus)" )

        AttachContextMenuWdg.attach_by_menu_id( activator2, ctx_menu.get('menu_id') )

        div.add( activator2 )

        # -------------------- Drop-down Button Menu example ------------------------------------------------------

        self.setup_next_example( div, "Original Drop-down Menu Button example ..." )

        menus = [ self.get_dd_plain_menu(), self.get_dd_plain_submenu_1() ]
        dd_button = ButtonForDropdownMenuWdg( id="MikeDropDownBtn", title="LMB on Me For Menu", menus=menus,
                                                 width=150, match_width=True)
        div.add( dd_button )

        return div


    # menu_tag_suffix is 'MAIN' or 'SUB1' or 'SUB2', etc
    #
    def get_smart_menu_main_menu_details(self):
        return { 'menu_tag_suffix': 'MAIN', 'width': 200, 'opt_spec_list': [
            { "type": "action", "label": "Launch JS Logger",
                    "bvr_cb": {'cbjs_action': "spt.js_log.show();"} },

            { "type": "action", "label": "Command cbk",
                    "bvr_cb": {'cbjs_action': "spt.ctx_menu.option_clicked_cbk( evt, bvr );",
                               'options': {'inner_cbk': 'spt.ctx_menu.test'}},
                    "hover_bvr_cb": {'activator_mod_styles':
                                        'background-color: black; color: blue; border: 1px solid red;'} },

            { "type": "action", "label": "Open",
                    "bvr_cb": {'cbjs_action': "alert('Open File clicked!');"},
                    "icon": IconWdg.LOAD },

            { "type": "action", "label": "Make activator_el RED",
                    # -- NOTE: the example below shows how to get to the activator_el ... just use the convenience
                    #          function 'spt.semnu.get_activator(bvr)' ... you just need to provide the call
                    #          with the bvr. This works for sub-menus as well.
                    "bvr_cb": {'cbjs_action': "spt.smenu.get_activator(bvr).setStyle('background','#FF0000');"} },

            { "type": "separator" },

            { "type": "toggle", "label": "Use Silky Smooth Work-flow", "state": True },
            { "type": "toggle", "label": "Have a Not Cool Day!", "state": False },

            { "type": "action", "label": "Get Information!",
                    "bvr_cb": {'cbjs_action': "spt.js_log.show();"},
                    "icon": IconWdg.INFO },

            { "type": "title", "label": "Crazy Options" },

            { "type": "submenu", "label": "Sub-menu 1", "submenu_tag_suffix": "SUB_1",
                    "hover_bvr_cb": {'activator_mod_styles': 'border: 1px red solid; background: blue;'}},
            { "type": "submenu", "label": "Sub-menu 2", "submenu_tag_suffix": "SUB_2" }
        ] }


    def get_smart_menu_submenu_one_details(self):
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


    def get_smart_menu_submenu_two_details(self):
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



    def get_ctx_menu_details(self):
        return { 'menu_id': 'CtxMenu_Mike_Main', 'width': 200, 'opt_spec_list': [
            { "type": "action", "label": "Launch JS Logger",
                    "bvr_cb": {'cbjs_action': "spt.js_log.show();"} },

            { "type": "action", "label": "Command cbk",
                    "bvr_cb": {'cbfn_action': "spt.ctx_menu.option_clicked_cbk",
                               'options': {'inner_cbk': 'spt.ctx_menu.test'}} },

            { "type": "action", "label": "Open",
                    "bvr_cb": {'cbjs_action': "alert('Open File clicked!');"},
                    "icon": IconWdg.LOAD },

            { "type": "action", "label": "Make activator_el WHITE",
                    # -- NOTE: the example below shows how to get to the activator_el ... just use the convenience
                    #          function 'spt.ctx_menu.orig_activator(bvr)' ... you just need to provide the call
                    #          with the bvr. This works for sub-menus as well.
                    "bvr_cb": {'cbjs_action': "spt.ctx_menu.get_activator(bvr).setStyle('background','#FFFFFF');"} },

            { "type": "separator" },

            { "type": "toggle", "label": "Use Silky Smooth Work-flow", "state": True },
            { "type": "toggle", "label": "Have a Not Cool Day!", "state": False },

            { "type": "action", "label": "Get Information!",
                    "bvr_cb": {'cbjs_action': "spt.js_log.show();"},
                    "icon": IconWdg.INFO, "disabled": True },

            { "type": "separator" },

            { "type": "title", "label": "Crazy Options" },

            { "type": "submenu", "label": "Sub-menu", "submenu_id": "CtxMenu_Mike_Submenu_One", "disabled": False },
            { "type": "submenu", "label": "Disabled Sub-menu", "submenu_id": "Goodbye", "disabled": True }
        ] }


    def get_ctx_sub_menu_details(self):
        return { 'menu_id': 'CtxMenu_Mike_Submenu_One', 'width': 250, 'opt_spec_list': [
            { "type": "submenu", "label": "Nested Sub-menu", "submenu_id": "CtxMenu_Mike_Submenu_Two" },
            { "type": "separator" },
            { "type": "action", "label": "Sub-menu launch JS Logger",
                    "bvr_cb": {'cbjs_action': "spt.js_log.show();"} },
            { "type": "action", "label": "Open Folder",
                    "bvr_cb": {'cbjs_action': "alert('Sub-menu Open File clicked!');"}, "icon": IconWdg.LOAD },

            { "type": "action", "label": "Make activator_el GREEN",
                    # -- NOTE: the example below shows how to get to the activator_el ... just use the convenience
                    #          function 'spt.ctx_menu.orig_activator(bvr)' ... you just need to provide the call
                    #          with the bvr. This works for sub-menus as well.
                    "bvr_cb": {'cbjs_action': "spt.ctx_menu.get_activator(bvr).setStyle('background','#006600');"} },

            { "type": "action", "label": "Make Awesome Popup ...",
                    "bvr_cb": {'cbjs_action': "alert('Popping up Awesomeness!');"} },
            { "type": "separator" },
            { "type": "submenu", "label": "Additional Nested Sub-menu", "submenu_id": "CtxMenu_Mike_Submenu_Three" }
        ] }


    def get_ctx_sub_menu_two_details(self):
        return { 'menu_id': 'CtxMenu_Mike_Submenu_Two', 'width': 250, 'opt_spec_list': [
            { "type": "action", "label": "Make activator_el BLACK",
                    "bvr_cb": {'cbjs_action': "spt.ctx_menu.get_activator(bvr).setStyle('background','#000000');"} },
            { "type": "separator" },
            { "type": "title", "label": "A Nested Sub-menu" },
            { "type": "action", "label": "Sub-menu 2 launch JS Logger",
                    "bvr_cb": {'cbjs_action': "spt.js_log.show();"} },
            { "type": "action", "label": "Open Folder 2",
                    "bvr_cb": {'cbjs_action': "alert('Sub-menu 2 Open File clicked!');"}, "icon": IconWdg.LOAD },
            { "type": "action", "label": "Make Even More Awesome Popup ...",
                    "bvr_cb": {'cbjs_action': "alert('Popping up Much More Awesomeness!');"} }
        ] }


    def get_dd_plain_menu(self):
        return { 'menu_id': 'DropdownMenu_Plain', 'width': 200, 'opt_spec_list': [
            { "type": "action", "label": "New Window",
                    "bvr_cb": {'cbjs_action': "alert('File->New Window');"} },

            { "type": "action", "label": "New Tab",
                    "bvr_cb": {'cbjs_action': "alert('File->New Tab');"} },

            { "type": "action", "label": "Open Location...",
                    "bvr_cb": {'cbjs_action': "alert('File->Open Location...');"} },

            { "type": "action", "label": "Open File...", "icon": IconWdg.LOAD,
                    "bvr_cb": {'cbjs_action': "alert('File->Open File...');"} },

            { "type": "action", "label": "Close",
                    "bvr_cb": {'cbjs_action': "alert('File->Close');"} },

            { "type": "separator" },

            { "type": "action", "label": "Save Page As...",
                    "bvr_cb": {'cbjs_action': "alert('File->Save Page As...');"} },

            { "type": "action", "label": "Send Link...",
                    "bvr_cb": {'cbjs_action': "alert('File->Send Link...');"} },

            { "type": "separator" },

            { "type": "action", "label": "Page Setup...",
                    "bvr_cb": {'cbjs_action': "alert('File->Page Setup...');"} },

            { "type": "action", "label": "Print...",
                    "bvr_cb": {'cbjs_action': "alert('File->Print...');"} },

            { "type": "submenu", "label": "Other Tools", "submenu_id": "DropdownMenu_Plain_Submenu_1" }

        ] }


    def get_dd_plain_submenu_1(self):
        return { 'menu_id': 'DropdownMenu_Plain_Submenu_1', 'width': 250, 'opt_spec_list': [
            { "type": "title", "label": "A Nested Sub-menu" },
            { "type": "separator" },
            { "type": "action", "label": "Sub-menu 2 launch JS Logger",
                    "bvr_cb": {'cbjs_action': "spt.js_log.show();"} },
            { "type": "action", "label": "Open Folder 2",
                    "bvr_cb": {'cbjs_action': "alert('Sub-menu 2 Open File clicked!');"}, "icon": IconWdg.LOAD },
            { "type": "action", "label": "Make Even More Awesome Popup ...",
                    "bvr_cb": {'cbjs_action': "alert('Popping up Much More Awesomeness!');"} }
        ] }



