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
__all__ = ["ActionBarWdg"]

from pyasm.web import *
from pyasm.common import Environment
from tactic.ui.common import BaseRefreshWdg
from tactic.ui.container import PopupWdg
from tactic.ui.activator import ButtonForDropdownMenuWdg

from pyasm.widget import ButtonWdg

class ActionBarWdg(BaseRefreshWdg):
    '''Set of menus making different sets of tools available in one place'''

    def init(self):
        pass


    def get_args_keys(self):
        return {
            'table_id': 'id of the table that this action operates on'
        }


    def get_display(self):

        self.table_id = self.kwargs.get('table_id')
        if not self.table_id:
            self.table_id = 'main_body_table'

        action_bar_top_div = DivWdg()
        action_bar_top_div.set_id("ActionBarWdg")

        inner_div = DivWdg()
        inner_div.set_style("background: #2f2f2f; color: #000000; border: 1px solid #000000; padding: 2px;")

        # Fill out content div here!

        btn_info_list = [
                # {'id': 'ActionBar_FileMenu_Btn', 'title': 'File', 'menus': [ self.get_file_menu() ], 'match_w': False},
                {'id': 'ActionBar_ViewMenu_Btn', 'title': 'View', 'menus': [ self.get_view_menu() ], 'match_w': False},
                # {'id': 'ActionBar_EditMenu_Btn', 'title': 'Edit', 'menus': [ self.get_edit_menu() ], 'match_w': False},
                # {'id': 'ActionBar_ItemsMenu_Btn', 'title': 'Items', 'menus': [ self.get_items_menu() ], 'match_w': False},
                {'id': 'ActionBar_ToolsMenu_Btn', 'title': 'Tools', 'menus': [ self.get_tools_menu() ], 'match_w': False}
                #{'id': 'ActionBar_ProjectMenu_Btn', 'title': 'Project', 'menus': [ self.get_project_menu() ], 'match_w': False},
        ]

        table = Table()
        table.add_row()

        for btn_info in btn_info_list:
            dd_button = ButtonForDropdownMenuWdg( id = btn_info['id'],
                                                  title = btn_info['title'],
                                                  menus = btn_info['menus'],
                                                  width = 120,
                                                  match_width = btn_info['match_w'],
                                                  nudge_menu_horiz = 0 )
            td = table.add_cell()
            td.add( dd_button )

        # -- example of how to set this widget up as a tear_off (leaving here for reference for now)
        # --
        # tear_off = SpanWdg()
        # tear_off.add( "[tear-off]" )
        # tear_off.add_class( "SPT_TEAR_OFF_ACTIVATOR" )
        # tear_off.add_styles( "cursor: pointer;" )
        # tear_off.add_behavior( { 'type': 'click_up',
        #     'cbjs_action': 'spt.popup.tear_off_el( $("%s"), "%s", %s, "%s" );' %
        #                     (action_bar_id, popup_title, 'spt.popup.remove_el_by_class', 'SPT_TEAR_OFF_ACTIVATOR')
        # } )
        # td = table.add_cell()
        # td.add( tear_off )

        inner_div.add( table )

        # Finished generating tools for Action Bar ...
        action_bar_top_div.add(inner_div)

        aux_div = DivWdg()
        aux_div.set_id("ActionBar_Aux")
        aux_div.add_class("SPT_AUX")
        aux_div.add_styles("display: none;")

        aux_div_title = DivWdg()
        aux_div_title.add_looks("popup fnt_text")  # look shouldn't be "popup" here!
        aux_div_title.set_id("ActionBar_Aux_Title")
        aux_div_content = DivWdg()
        aux_div_content.set_id("ActionBar_Aux_Content")


        aux_div.add( "<div>&nbsp;</div>" )
        aux_div.add( aux_div_title )
        # add spacing
        aux_div.add(HtmlElement.br(2))
        aux_div.add( aux_div_content )
        aux_div.add( "<div>&nbsp;</div>" )

        action_bar_top_div.add(aux_div)

        return action_bar_top_div


    def get_view_menu(self):
        is_admin = False
        security = Environment.get_security()
        if security.check_access("builtin", "view_site_admin", "allow"):
            is_admin = True
        menu_items = [
                { "type": "action", "label": "Save Current View",
                    "bvr_cb": {'cbjs_action': "spt.dg_table.view_action_cbk('save','%s', bvr);" % self.table_id, 
                               'is_admin': is_admin} },
                
                { "type": "action", "label": "Save My View As...",
                    "bvr_cb": {'cbjs_action': "spt.dg_table.view_action_cbk('add_my_view','%s', bvr);" % self.table_id} },
        ]

        
        if is_admin:
            menu_items.insert(2, { "type": "action", "label": "Save Project View As ...", "bvr_cb": {'cbjs_action': "spt.dg_table.view_action_cbk('save_project_view','%s', bvr);" % self.table_id} })

        return {'menu_id': 'ActionBar_ViewMenu_Main', 'width': 150, 'allow_icons': False,
                'opt_spec_list': menu_items}



    def get_file_menu(self):

        menu_items = [
                { "type": "action", "label": "Export All...", "bvr_cb": {
                  'cbfn_action': "spt.dg_table_action.set_actionbar_aux_content",
                        'class_name': 'tactic.ui.widget.CsvExportWdg',
                        'args': {"table_id": "%s" %self.table_id, \
                                 "is_export_all": "true"}}},


                { "type": "action", "label": "Export Selected", "bvr_cb": {
                    'cbfn_action': "spt.dg_table_action.set_actionbar_aux_content",
                        'class_name': 'tactic.ui.widget.CsvExportWdg',
                        'args': {"table_id": "%s" %self.table_id}}},
                

                { "type": "separator" },
                { "type": "action", "label": "Sign Out", "bvr_cb": {'cbjs_action': "alert('File->Sign Out');"} }
        ]

        security = Environment.get_security()
        if security.check_access("builtin", "view_site_admin", "allow"):
            menu_items.insert(0, { "type": "action", "label": "Import CSV", "bvr_cb": {
                    'cbfn_action':  "spt.dg_table_action.set_actionbar_aux_content",
                        'class_name': 'tactic.ui.widget.CsvImportWdg',
                        'args': {"table_id": "%s" %self.table_id} }})

        return {'menu_id': 'ActionBar_FileMenu_Main', 'width': 150, 'allow_icons': False,
                'opt_spec_list': menu_items}


    def get_edit_menu(self):
        return {
            'menu_id': 'ActionBar_EditMenu_Main', 'width': 200, 'allow_icons': False,
            'opt_spec_list': [
                { "type": "action", "label": "Show Server Transaction Log",
                    "bvr_cb": {
                        'cbjs_action': "spt.popup.get_widget(evt, bvr)",
                        'options': {
                            'class_name': 'tactic.ui.popups.TransactionPopupWdg',
                            'title': 'Transaction Log',
                            'popup_id': 'TransactionLog_popup'
                        }

                    }
                },
                { "type": "separator" },
                { "type": "action", "label": "Undo Last Server Transaction",
                        "bvr_cb": {'cbjs_action': "spt.undo();"} },
                { "type": "action", "label": "Redo Last Server Transaction",
                        "bvr_cb": {'cbjs_action': "spt.redo();"} },

                # FIXME: can't do this yet because the Action bar is not
                # specific to the view.
                #{ "type": "action", "label": "Add Columns",
                #    "bvr_cb": {
                #        'cbfn_action': 'spt.dg_table_action.get_popup_wdg',
                #        'class_name': 'tactic.ui.panel.AddPredefinedColumnWdg',
                #        'args': { 'search_type': self.search_type },
                #        'element_id':   'predefined_column_wdg',
                #    }
                #}, 
                #'''


                #{ "type": "action", "label": "Search Type Manager",
                #        "bvr_cb": {'cbjs_action': "spt.panel.load('main_body','tactic.ui.panel.SearchTypeManagerWdg')"} },

            ]
        }


    def get_items_menu(self):
        return {
            'menu_id': 'ActionBar_ItemsMenu_Main', 'width': 140, 'allow_icons': False,
            'opt_spec_list': [
                #{ "type": "action", "label": "Add New Item",
                        # NOTE: this only works for main_body!!
                #        "bvr_cb": {'cbjs_action': "spt.dg_table.add_item_cbk('main_body_table');"} },
                #{ "type": "separator" },
                { "type": "action", "label": "Retire Selected Items",
                        "bvr_cb": {'cbjs_action': "spt.dg_table.retire_selected('%s');" % self.table_id} },
                { "type": "action", "label": "Delete Selected Items",
                        "bvr_cb": {'cbjs_action': "spt.dg_table.delete_selected('%s');" % self.table_id} },
            ]
        }


    def get_tools_menu(self):
        menu_items = [

                #{ "type": "action", "label": "Search Types Manager",
                #        "bvr_cb": {'cbjs_action': "spt.panel.load('main_body','tactic.ui.panel.SearchTypeManagerWdg')"} },
                #{ "type": "separator" },
               
                
                { "type": "action", "label": "Web Client Output Log",
                        "bvr_cb": {'cbjs_action': "spt.js_log.show(false);"} },
                { "type": "action", "label": "TACTIC Script Editor",
                        "bvr_cb": {'cbjs_action': 'spt.panel.load_popup("TACTIC Script Editor",\
                                "tactic.ui.app.ShelfEditWdg", {}, {"load_once": true} );'} }
               

            ]
        security = Environment.get_security()
        if security.check_access("builtin", "view_site_admin", "allow"):
            menu_items.insert(0,  {"type": "action", "label": "Create New Project",
                        "bvr_cb": { 'cbjs_action': "spt.popup.open('create_project_wizard'); Effects.fade_in($('create_project_wizard'), 200);"}})
            menu_items.insert(1, { "type": "separator" })

        return {
            'menu_id': 'ActionBar_ToolsMenu_Main', 'width': 140, 'allow_icons': False,
            'opt_spec_list': menu_items
        }

    def get_project_menu(self):
        return {
            'menu_id': 'ActionBar_ProjectMenu_Main', 'width': 200, 'allow_icons': False,
            'opt_spec_list': [
            {
                "type": "action",
                "label": "Create New Project",
                "bvr_cb": { 'cbjs_action': "spt.popup.open('create_project_wizard');" }
            } ]
            }
