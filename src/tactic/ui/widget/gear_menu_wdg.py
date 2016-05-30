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
__all__ = ["DgTableGearMenuWdg","PageHeaderGearMenuWdg"]

from pyasm.common import Environment, Common
from pyasm.search import SearchType, Search
from pyasm.web import DivWdg, Widget
from pyasm.widget import IconWdg
from tactic.ui.common import BaseRefreshWdg
from tactic.ui.container import SmartMenu
from pyasm.biz import Project


class DgTableGearMenuWdg(BaseRefreshWdg):
    '''Gear Menu for DG Table Action widget'''

    def init(my):
        my.embedded_table = my.kwargs.get('embedded_table')
        my.ingest_data_view = my.kwargs.get("ingest_data_view")
        if not my.ingest_data_view:
            my.ingest_data_view = 'edit'
        my.ingest_custom_view = my.kwargs.get("ingest_custom_view")

        my.view_save_dialog = my.get_save_wdg()
        my.view_save_dialog_id = my.view_save_dialog.get_id()

        my.layout = my.kwargs.get("layout")
        search = Search("config/widget_config")
        search.add_filter("widget_type", "layout_tool")
        my.custom_tools = search.get_sobjects()
        my.is_admin = False

    def get_save_dialog(my):
        return my.view_save_dialog


    def get_save_wdg(my):

        from tactic.ui.container import DialogWdg
        dialog = DialogWdg(display=False, width=200, offset={'x':0,'y':50}, show_pointer=False)
        dialog_id = dialog.get_id()

        title = 'Save a New View'

        dialog.add_title(title)

        div = DivWdg()
        dialog.add(div)
        div.add_style("padding: 5 5 5 20")
        div.add_color("background", "background")

        my.table_id = my.kwargs.get("table_id")


        from tactic.ui.panel import ViewPanelSaveWdg
        save_wdg = ViewPanelSaveWdg(
            search_type=my.kwargs.get("search_type"),
            dialog_id=dialog_id,
            table_id=my.table_id
        )
        div.add(save_wdg)

        return dialog




    def get_args_keys(my):
        return {
            "custom_menus" : "Custom menus (an array of dictionaries)",
            "embedded_table": "boolean to show if it is part of an embedded table"
        }

    def get_access_keys_dict(my):

        from tactic.ui.startup import GearMenuSecurityWdg
        menu_names = GearMenuSecurityWdg.get_all_menu_names()

        project_code = Project.get_project_code()
        security = Environment.get_security()

        access_keys_dict = {}

        for key,value in menu_names:
            submenu = key
            for label in value.get('label'):
                
                access_keys = {'submenu': submenu, 'label': label, 'project': project_code}
                
                if security.check_access("gear_menu", access_keys, "allow"):
                    if not submenu in access_keys_dict:
                        access_keys_dict[submenu] = [label]
                    else:
                        access_keys_dict[submenu].append(label)

        return access_keys_dict

    def add_custom_menus(my, menus, menu_idx_map, custom_menus ):

        new_submenu_counter = 1
        for cmenu in custom_menus:
            if cmenu.has_key('add_to_submenu'):
                menu_label = cmenu.get('add_to_submenu')
                if menu_idx_map.has_key( menu_label ):
                    add_to_menu = menus[ menu_idx_map[menu_label] ]
                    add_to_menu.get("opt_spec_list").append( { 'type': 'separator' } )
                    submenu_items = cmenu.get("submenu_items")
                    for smenu_item in submenu_items:
                        add_to_menu.get("opt_spec_list").append( smenu_item )
                    width = cmenu.get('width')
                    if width:
                        add_to_menu['width'] = width
            else:
                # otherwise assume it's a new submenu ...
                if new_submenu_counter == 1:
                    menus[0].get("opt_spec_list").append( { 'type': 'separator' } )

                smenu_tag_suffix = "CUSTOM_%s" % new_submenu_counter
                smenu_label = cmenu.get('new_submenu')
                smenu_items = cmenu.get('submenu_items')
                smenu_items.insert( 0, { "type": "title", "label": smenu_label } )

                width = cmenu.get('width')
                if not width:
                    width = 150

                menus[0].get("opt_spec_list").append( { "type": "submenu", "label": smenu_label,
                                                        "submenu_tag_suffix": smenu_tag_suffix } )

                new_smenu = { "menu_tag_suffix": smenu_tag_suffix, "width": width,
                              "opt_spec_list": smenu_items }

                menus.append( new_smenu )

                new_submenu_counter += 1



    def get_menu_data(my):
        
        main_menu = my.get_main_menu()
        menus = [
            main_menu,
            my.get_edit_menu(),
            my.get_file_menu(),
            my.get_clipboard_menu(),
            my.get_view_menu(),
            my.get_print_menu(),
            my.get_chart_menu(),
            my.get_pipeline_menu(),
            my.get_task_menu(),
            my.get_note_menu(),
            my.get_checkin_menu()
        ]

        if my.custom_tools:
            menus.append(my.get_custom_menu())

        # Something to do with custom menus
        menu_idx_map = { 'Edit': 1, 'File': 2, 'Clipboard': 3, 'Task': 4, 'View': 5, 'Print': 6, 'Chart': 7, 'Pipeline': 8, 'Custom': 9 }


        # add custom gear menu items if specified in configuration ...
        config_custom_menus = my.kwargs.get("custom_menus")
        if config_custom_menus:
            custom_menu_error = False
            if config_custom_menus != "CONFIG-ERROR":
                try:
                    my.add_custom_menus( menus, menu_idx_map, config_custom_menus )
                except:
                    custom_menu_error = True
            else:
                custom_menu_error = True
            if custom_menu_error:
                menus = [ main_menu, 
                           my.get_edit_menu(),
                           my.get_file_menu(), 
                           my.get_clipboard_menu(),
                            my.get_view_menu(),
                            my.get_print_menu(),
                            my.get_chart_menu(),
                            my.get_pipeline_menu(),
                            my.get_task_menu(),
                            my.get_note_menu(),
                            my.get_checkin_menu()]

                menus[0].get("opt_spec_list").append( { "type": "title", "label": "*** <i>CUSTOM MENU CONFIG ERROR</i> ***" } )

        return menus

    def get_display(my):
        widget = Widget()
        # this is drawn in BaseTableLayoutWdg now
        #widget.add(my.view_save_dialog)

        return widget



    def get_main_menu(my):

        project_code = Project.get_project_code()
        security = Environment.get_security()
        
        access_keys_dict = my.get_access_keys_dict()
        if security.check_access("builtin", "view_site_admin", "allow"):
            my.is_admin = True
        else:
            my.is_admin = False
        
        if security.check_access("gear_menu",[{'submenu': "*", 'label': '*','project': project_code}], "allow"):
            my.is_admin = True

        if my.is_admin:
        
            opt_spec_list = [
            { "type": "submenu", "label": "Edit", "submenu_tag_suffix": "EDIT" },
            { "type": "submenu", "label": "File", "submenu_tag_suffix": "FILE" },
            { "type": "submenu", "label": "Clipboard", "submenu_tag_suffix": "CLIPBOARD" },
            { "type": "submenu", "label": "View", "submenu_tag_suffix": "VIEW" },
            { "type": "submenu", "label": "Print", "submenu_tag_suffix": "PRINT" },
            { "type": "submenu", "label": "Chart", "submenu_tag_suffix": "CHART" },
            ]

            


            if not my.layout or my.layout.can_add_columns():
                opt_spec_list.extend( [
                { "type": "separator"},
                { "type": "submenu", "label": "Tasks", "submenu_tag_suffix": "TASK" },
                { "type": "submenu", "label": "Notes", "submenu_tag_suffix": "NOTE" },
                { "type": "submenu", "label": "Check-ins", "submenu_tag_suffix": "CHECKIN" },
                ] )

                opt_spec_list.append( { "type": "submenu", "label": "Workflows", "submenu_tag_suffix": "PIPELINE" } )


            if my.custom_tools:
                opt_spec_list.append( { "type": "submenu", "label": "Custom Tools", "submenu_tag_suffix": "CUSTOM" } )

        else:
            opt_spec_list = []
            if access_keys_dict.get('Edit'):
                opt_spec_list.append(
                    { "type": "submenu", "label": "Edit", "submenu_tag_suffix": "EDIT" }
                )

            if access_keys_dict.get('File'):
                opt_spec_list.append(
                    { "type": "submenu", "label": "File", "submenu_tag_suffix": "FILE" }
                )

            if access_keys_dict.get('Clipboard'):
                opt_spec_list.append(
                    { "type": "submenu", "label": "Clipboard", "submenu_tag_suffix": "CLIPBOARD" }
                )

            if access_keys_dict.get('Print'):
                opt_spec_list.append(
                    { "type": "submenu", "label": "Print", "submenu_tag_suffix": "PRINT" }
                )

            if access_keys_dict.get('Chart'):
                opt_spec_list.append(
                    { "type": "submenu", "label": "Chart", "submenu_tag_suffix": "CHART" }
                )

            if access_keys_dict.get('View'):
                opt_spec_list.append(
                    { "type": "submenu", "label": "View", "submenu_tag_suffix": "VIEW" }
                )

            
            if not my.layout or my.layout.can_add_columns():
                if access_keys_dict.get('Tasks'):
                    opt_spec_list.append(
                        { "type": "submenu", "label": "Tasks", "submenu_tag_suffix": "TASK" }
                    )
                if access_keys_dict.get('Notes'):
                    opt_spec_list.append(
                        { "type": "submenu", "label": "Notes", "submenu_tag_suffix": "NOTE" },
                    )
                if access_keys_dict.get('Check-ins'):    
                    opt_spec_list.append(
                        { "type": "submenu", "label": "Check-ins", "submenu_tag_suffix": "CHECKIN" },
                    )

                if access_keys_dict.get('Pipelines'):
                    opt_spec_list.append(
                        { "type": "submenu", "label": "Workflows", "submenu_tag_suffix": "PIPELINE" }
                    )

        menu = { 'menu_tag_suffix': 'MAIN', 'width': 130, 'opt_spec_list': opt_spec_list }
        return menu

    

    def get_edit_menu(my):
        
        opt_spec_list = []
        security = Environment.get_security()
        project_code = Project.get_project_code()
        
        access_keys_dict = my.get_access_keys_dict()
        label_list = []
        if access_keys_dict.get('Edit'):
            label_list = access_keys_dict['Edit']

        

        if my.is_admin:
            access_keys = my._get_access_keys("retire_delete",  project_code)
            if security.check_access("builtin", access_keys, "allow"):
                if not my.layout or my.layout.can_select():
                    opt_spec_list.extend([
                
                        { "type": "action", "label": "Retire Selected Items",
                            "bvr_cb": {'cbjs_action': "spt.dg_table.gear_smenu_retire_selected_cbk(evt,bvr);"}
                        },

                        { "type": "action", "label": "Delete Selected Items",
                                "bvr_cb": {'cbjs_action': '''
                        spt.dg_table.gear_smenu_delete_selected_cbk(evt,bvr);
                        '''}
                        },

                        {"type": "separator"}

                    ])

            opt_spec_list.extend([

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
                    "bvr_cb": {'cbjs_action': "spt.undo_cbk(evt, bvr);"}
                },

                { "type": "action", "label": "Redo Last Server Transaction",
                    "bvr_cb": {'cbjs_action': "spt.redo_cbk(evt, bvr);"}
                },

            ])
            return { 'menu_tag_suffix': 'EDIT', 'width': 200, 'opt_spec_list': opt_spec_list}

        else:
            if 'Retire Selected Items' in label_list:
                opt_spec_list.append(
                    { "type": "action", "label": "Retire Selected Items",
                        "bvr_cb": {'cbjs_action': "spt.dg_table.gear_smenu_retire_selected_cbk(evt,bvr);"}
                    }
                )

            if 'Delete Selected Items' in label_list:
                opt_spec_list.extend([
                    { "type": "action", "label": "Delete Selected Items",
                        "bvr_cb": {'cbjs_action': "spt.dg_table.gear_smenu_delete_selected_cbk(evt,bvr);"}
                
                    },

                    {"type": "separator"}

                ])
            

            if 'Show Server Transaction Log' in label_list:
                opt_spec_list.extend([

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
                ])
            if 'Undo Last Server Transaction' in label_list:
                opt_spec_list.append(
                    { "type": "action", "label": "Undo Last Server Transaction",
                        "bvr_cb": {'cbjs_action': "spt.undo_cbk(evt, bvr);"}
                    }
                )

            if 'Redo Last Server Transaction' in label_list:
                opt_spec_list.append(
                    { "type": "action", "label": "Redo Last Server Transaction",
                    "bvr_cb": {'cbjs_action': "spt.redo_cbk(evt, bvr);"}
                    }
                )

            if opt_spec_list and opt_spec_list[-1] == { "type": "separator" }:
                opt_spec_list.pop()

            return { 'menu_tag_suffix': 'EDIT', 'width': 200, 'opt_spec_list': opt_spec_list}
        

    def get_file_menu(my):

        menu_items = []

        security = Environment.get_security()
        project_code = Project.get_project_code()

        access_keys_dict = my.get_access_keys_dict()
        label_list = []
        if access_keys_dict.get('File'):
            label_list = access_keys_dict['File']

        access_keys = my._get_access_keys("export_all_csv",  project_code)

        
        if security.check_access("builtin", access_keys, "allow") or 'Export All ...' in label_list:
            menu_items.append(
                { "type": "action", "label": "Export All ...",
                    "bvr_cb": { 'cbjs_action': 'spt.dg_table.gear_smenu_export_cbk(evt,bvr);',
                                "mode": 'export_all'}
                }
            )

        if not my.layout or my.layout.can_add_columns():
            if my.is_admin or 'Export Selected ...' in label_list:
                menu_items.append(
                    { "type": "action", "label": "Export Selected ...",
                        "bvr_cb": { 'cbjs_action': 'spt.dg_table.gear_smenu_export_cbk(evt,bvr);' ,
                                    'mode': 'export_selected'}
                    }
                )

        if my.is_admin or 'Export Matched ...' in label_list:
            menu_items.append( 
                 { "type": "action", "label": "Export Matched ...",
                    "bvr_cb": { 'cbjs_action': 'spt.dg_table.gear_smenu_export_cbk(evt,bvr);' ,
                                'mode': 'export_matched'}
                }
            )
        if my.is_admin or 'Export Displayed ...' in label_list:
            menu_items.append( 
                 { "type": "action", "label": "Export Displayed ...",
                    "bvr_cb": { 'cbjs_action': 'spt.dg_table.gear_smenu_export_cbk(evt,bvr);' ,
                                'mode': 'export_displayed'}
                }
            )

        access_keys = my._get_access_keys("import_csv",  project_code)
        if security.check_access("builtin", access_keys, "allow") or 'Import CSV' in label_list:
            menu_items.append( {"type": "separator"} )
            menu_items.append(
                { "type": "action", "label": "Import CSV",
                    "bvr_cb": { 'cbjs_action': 'spt.dg_table.gear_smenu_import_cbk(evt,bvr);' }
                } )


        access_keys = my._get_access_keys("ingest",  project_code)
        if security.check_access("builtin", access_keys, "allow") or 'Ingest Files' in label_list:
            menu_items.append( {"type": "separator"} )
            menu_items.append(
                { "type": "action", "label": "Ingest Files",
                    "bvr_cb": {'type': 'click_up',
                               'ingest_custom_view': my.ingest_custom_view,
                               'ingest_data_view': my.ingest_data_view,
                               'cbjs_action': '''
                    var activator = spt.smenu.get_activator(bvr);
                    var top = activator.getParent(".spt_table_top");
                    var table = top.getElement(".spt_table");
                    var search_type = table.getAttribute("spt_search_type");

                    var kwargs = {
                        search_type: search_type,
                        ingest_data_view: bvr.ingest_data_view
                    };
                    
                    if (bvr.ingest_custom_view) {
                        kwargs['view'] = bvr.ingest_custom_view;
                        var class_name = 'tactic.ui.panel.CustomLayoutWdg';
                    } else {
                        var class_name = 'tactic.ui.tools.IngestUploadWdg';
                    }
                    
                    var title = "Ingest Files";
                    spt.tab.set_main_body_tab();
                    spt.tab.add_new("ingest_" + search_type, title, class_name, kwargs);  
                                   '''}
                } )
        if security.check_access("builtin", access_keys, "allow") or 'Check-out Files' in label_list:
            menu_items.append(
                { "type": "action", "label": "Check-out Files",
                    "bvr_cb": { 'cbjs_action': '''
                    var class_name = 'tactic.ui.tools.CheckoutWdg';
                    var activator = spt.smenu.get_activator(bvr);

                    var layout = activator.getParent(".spt_layout");
                    spt.table.set_layout(layout)
                    var selected_search_keys = spt.table.get_selected_search_keys()
                    var kwargs = {
                        search_keys: selected_search_keys
                    };
                    //spt.tab.set_main_body_tab();
                    //spt.tab.add_new("Ingest", "Ingest", class_name, kwargs);
                    var title = "Check-out Files";
                    spt.panel.load_popup(title, class_name, kwargs);
                    '''
                 }
                } )



        return {'menu_tag_suffix': 'FILE', 'width': 180, 'opt_spec_list': menu_items}


    def get_clipboard_menu(my):
        
        menu_items = []

        access_keys_dict = my.get_access_keys_dict()
        label_list = []
        if access_keys_dict.get('Clipboard'):
            label_list = access_keys_dict['Clipboard']

        security = Environment.get_security()
        
        if my.is_admin or 'Copy Selected' in label_list:
            menu_items.append(
                { "type": "action", "label": "Copy Selected",
                    "bvr_cb": {
                    'cbjs_action': '''
                    var server = TacticServerStub.get();

                    var activator = spt.smenu.get_activator(bvr);
                    var top = activator.getParent(".spt_table_top");
                    var table = top.getElement(".spt_table");

                    spt.app_busy.show("Copying to Clipboard");

                    var search_keys;
                    var layout = activator.getParent(".spt_layout");
                    var version = layout.getAttribute("spt_version");
                    var table = layout.getElement(".spt_table");
                    if (version == "2") {
                        spt.table.set_table(table);
                        search_keys = spt.table.get_selected_search_keys();
                    }
                    else {
                        search_keys = spt.dg_table.get_selected_search_keys(table);
                    }

                    var class_name = 'tactic.command.clipboard_cmd.ClipboardCopyCmd';
                    var kwargs = {
                        search_keys: search_keys
                    }
                    server.execute_cmd(class_name, kwargs);

                    spt.app_busy.hide();

                    spt.notify.show_message("Copied ["+search_keys.length+"] items to the clipboard");

                    '''
                    }
                }
            )

        if my.is_admin or 'Paste' in label_list:
            menu_items.append(
                { "type": "action", "label": "Paste",
                    "bvr_cb": {
                    'cbjs_action': '''
                    var server = TacticServerStub.get();

                    var activator = spt.smenu.get_activator(bvr);
                    var top = activator.getParent(".spt_table_top");
                    var table = top.getElement(".spt_table");
                    var search_type = table.getAttribute("spt_search_type");

                    spt.app_busy.show("Pasting contents from Clipboard");

                    var class_name = 'tactic.command.sobject_copy_cmd.SObjectCopyCmd';
                   
                    // don't pass in context to get all current contexts automatically
                    var kwargs = {
                        dst_search_type: search_type,
                        source: 'clipboard',
                    }
                    try {
                        var rtn = server.execute_cmd(class_name, kwargs);
                        if (rtn.info.error)
                            spt.alert(rtn.info.error);
                    }
                    catch(e){
                        spt.alert(spt.exception.handler(e));
                    }

                    // refresh table
                    spt.table.run_search();
                    var event = "update|" + search_type;
                    kwargs = {
                        firing_element: activator
                    }
                    var input = {
                        kwargs: kwargs
                    }
                    var bvr2 = {};
                    bvr2.options = input;
                    try {
                        spt.named_events.fire_event(event, bvr2);
                    }
                    catch(e) {
                        spt.alert("Error firing event: " + event);
                    }

                    spt.app_busy.hide();
                    '''
                    }
                }
            )

        if my.is_admin or 'Connect' in label_list:
            menu_items.append(
                { "type": "action", "label": "Connect",
                    "bvr_cb": {
                    'cbjs_action': '''
                    var server = TacticServerStub.get();
                    var activator = spt.smenu.get_activator(bvr);
                    var top = activator.getParent(".spt_table_top");
                    var table = top.getElement(".spt_table");
                    var search_type = table.getAttribute("spt_search_type");
                    spt.app_busy.show("Reference contents from Clipboard");


                    var class_name = 'tactic.command.clipboard_cmd.ClipboardConnectCmd';
                    var search_keys;
                    var layout = activator.getParent(".spt_layout");
                    var version = layout.getAttribute("spt_version");
                    var table = layout.getElement(".spt_table");
                    if (version == "2") {
                        spt.table.set_table(table);
                        search_keys = spt.table.get_selected_search_keys();
                    }
                    else {
                        search_keys = spt.dg_table.get_selected_search_keys(table);
                    }
                    var kwargs = {
                        search_keys: search_keys
                    }
                    server.execute_cmd(class_name, kwargs);


                    // refresh table
                    spt.dg_table.search_cbk(table, bvr);
                    spt.app_busy.hide();

                    '''
                    }
                }
            )

            menu_items.append(
               { "type": "separator" }
            )
        
        if my.is_admin or 'Append Selected' in label_list:
            menu_items.append(
                { "type": "action", "label": "Append Selected",
                    "bvr_cb": {
                    'cbjs_action': '''
                    var server = TacticServerStub.get();

                    var activator = spt.smenu.get_activator(bvr);
                    var top = activator.getParent(".spt_table_top");
                    var table = top.getElement(".spt_table");
                    var layout = activator.getParent(".spt_layout");

                    var search_keys;
                    var layout = activator.getParent(".spt_layout");
                    var version = layout.getAttribute("spt_version");
                    var table = layout.getElement(".spt_table");
                    if (version == "2") {
                        spt.table.set_table(table);
                        search_keys = spt.table.get_selected_search_keys();
                    }
                    else {
                        search_keys = spt.dg_table.get_selected_search_keys(table);
                    }

                    spt.app_busy.show("Adding to Clipboard");

                    var class_name = 'tactic.command.clipboard_cmd.ClipboardAddCmd';
                    var kwargs = {
                        search_keys: search_keys
                    }
                    server.execute_cmd(class_name, kwargs);

                    spt.app_busy.hide();

                    spt.notify.show_message("Added ["+search_keys.length+"] items to the clipboard");

                    '''
                    }
                }
            )
            menu_items.append(
                { "type": "separator" }
            )

        if my.is_admin or 'Show Clipboard Contents' in label_list:
            menu_items.append(
                { "type": "action", "label": "Show Clipboard Contents",
                    "bvr_cb": {
                    'cbjs_action': '''
                    var server = TacticServerStub.get();
                    var activator = spt.smenu.get_activator(bvr);
                    var top = activator.getParent(".spt_table_top");
                    var table = top.getElement(".spt_table");

                    var expression = "@SOBJECT(sthpw/clipboard['login',$LOGIN])";
                    var class_name = 'tactic.ui.panel.FastTableLayoutWdg';
                    var kwargs = {
                      expression: expression,
                      search_type: 'sthpw/clipboard',
                      view: 'table',
                      show_insert: false,
                    }
                    spt.panel.load_popup("Clipboard", class_name, kwargs);
                    '''
                    }
                }
            )

        if menu_items and menu_items[-1] == { "type": "separator" }:
            menu_items.pop()

        return {'menu_tag_suffix': 'CLIPBOARD', 'width': 180, 'opt_spec_list': menu_items}


    def get_pipeline_menu(my):
        menu_items = []

        security = Environment.get_security()

        access_keys_dict = my.get_access_keys_dict()
        label_list = []
        if access_keys_dict.get('Pipelines'):
            label_list = access_keys_dict['Pipelines']


        if my.is_admin or 'Show Pipeline Code' in label_list:
            menu_items.append(
                {
                    "type": "action", "label": "Show Workflow Code",
                    "bvr_cb": {
                        'cbjs_action': '''
                        spt.app_busy.show("Adding Pipeline column to table");
                        var activator = spt.smenu.get_activator(bvr);
                        var layout = activator.getParent(".spt_layout");
                        var version = layout.getAttribute("spt_version");
                        var table = layout.getElement(".spt_table");
                        if (version == "2") {
                            spt.table.set_table(table);
                            spt.table.add_columns(["pipeline_code"]);
                        }
                        else {
                            spt.dg_table.toggle_column_cbk(table,'pipeline_code','1');
                        }
                        spt.app_busy.hide();
                        '''
                    }
                }
            )

        if my.is_admin or 'Edit Pipelines' in label_list:
            menu_items.append(
                {
                    "type": "action", "label": "Edit Workflows",
                    "bvr_cb": {
                        'cbjs_action': '''
                        spt.tab.set_main_body_tab();
                        var kwargs = {
                            'show_gear': 'false'
                        }
                        spt.tab.add_new("Workflows", "Workflows", "tactic.ui.tools.PipelineToolWdg", kwargs);
                        '''
                    }
                }
            )


        return {'menu_tag_suffix': 'PIPELINE', 'width': 210, 'opt_spec_list': menu_items}


    def get_task_menu(my):
        menu_items = []

        security = Environment.get_security()

        access_keys_dict = my.get_access_keys_dict()
        label_list = []
        if access_keys_dict.get('Tasks'):
            label_list = access_keys_dict['Tasks']
        
        if my.is_admin or 'Show Tasks' in label_list:
            menu_items.append(
                {
                    "type": "action", "label": "Show Tasks",
                    "bvr_cb": {
                        'cbjs_action': '''
                        spt.app_busy.show("Adding Tasks column to table");
                        var activator = spt.smenu.get_activator(bvr);
                        var layout = activator.getParent(".spt_layout");
                        var table = layout.getElement(".spt_table");
                        var version = layout.getAttribute("spt_version");
                        if (version == "2") {
                            spt.table.set_table(table);
                            spt.table.add_columns(["task_edit", "task_status_edit"]);
                        } 
                        else {
                            spt.dg_table.toggle_column_cbk(table,'task_status_edit','1');
                        }
                        spt.app_busy.hide();
                        '''
                    }
                }
            )
            menu_items.append(
                { "type": "separator" }
            )

        if my.is_admin or 'Add Tasks to Selected' in label_list:
            menu_items.append(
                {
                    "type": "action", "label": "Add Tasks to Selected",
                    "bvr_cb": {
                        'cbjs_action': "spt.dg_table.gear_smenu_add_task_selected_cbk(evt,bvr);"
                    }
                }
            )

        if my.is_admin or 'Add Tasks to Matched' in label_list:
            menu_items.append(
                {
                    "type": "action", "label": "Add Tasks to Matched",
                    "bvr_cb": {
                        'cbjs_action': "spt.dg_table.gear_smenu_add_task_matched_cbk(evt,bvr);"
                    }
                }
            )
        if menu_items and menu_items[-1] == { "type": "separator" }:
            menu_items.pop()

        return {'menu_tag_suffix': 'TASK', 'width': 210, 'opt_spec_list': menu_items}




    def get_note_menu(my):

        menu_items = []
        security = Environment.get_security()

        access_keys_dict = my.get_access_keys_dict()
        label_list = []
        if access_keys_dict.get('Notes'):
            label_list = access_keys_dict['Notes']

        if my.is_admin or 'Show Notes' in label_list:
            menu_items = [
                {
                    "type": "action", "label": "Show Notes",
                    "bvr_cb": {
                        'cbjs_action': '''
                        spt.app_busy.show("Adding Notes column to table");
                        var activator = spt.smenu.get_activator(bvr);
                        var layout = activator.getParent(".spt_layout");
                        var version = layout.getAttribute("spt_version");
                        var table = layout.getElement(".spt_table");
                        if (version == "2") {
                            spt.table.set_table(table);
                            spt.dg_table.toggle_column_cbk(table,'notes','1');
                            //spt.table.add_columns(["notes"]);
                        }
                        else {
                            spt.dg_table.toggle_column_cbk(table,'notes','1');
                        }
                        spt.app_busy.hide();
                        '''
                    }
                }
            ]

        return {'menu_tag_suffix': 'NOTE', 'width': 210, 'opt_spec_list': menu_items}




    def get_checkin_menu(my):

        menu_items = []

        security = Environment.get_security()

        access_keys_dict = my.get_access_keys_dict()
        label_list = []
        if access_keys_dict.get('Check-ins'):
            label_list = access_keys_dict['Check-ins']
        
        if my.is_admin or 'Show Check-in History' in label_list:
            menu_items.append(
                {
                    "type": "action", "label": "Show Check-in History",
                    "bvr_cb": {
                        'cbjs_action': '''
                        spt.app_busy.show("Adding Check-in History column to table");
                        var activator = spt.smenu.get_activator(bvr);
                        var layout = activator.getParent(".spt_layout");
                        var version = layout.getAttribute("spt_version");
                        var table = layout.getElement(".spt_table");
                        if (version == "2") {
                            spt.table.set_table(table);
                            //spt.table.add_columns(["history"]);
                            spt.dg_table.toggle_column_cbk(table,'history','1');
                        }
                        else {
                            spt.dg_table.toggle_column_cbk(table,'history','1');
                        }
                        spt.app_busy.hide();
                        '''
                    }
                }
            )
        
        if my.is_admin or 'Show General Check-in Tool' in label_list:
            menu_items.append(
                {
                    "type": "action", "label": "Show General Check-in Tool",
                    "bvr_cb": {
                        'cbjs_action': '''
                        spt.app_busy.show("Adding General Check-in tool to table");
                        var activator = spt.smenu.get_activator(bvr);
                        var layout = activator.getParent(".spt_layout");
                        var version = layout.getAttribute("spt_version");
                        var table = layout.getElement(".spt_table");
                        if (version == "2") {
                            spt.table.set_table(table);
                            //spt.table.add_columns(["general_checkin"]);
                            spt.dg_table.toggle_column_cbk(table,'general_checkin','1');
                        }
                        else {
                            spt.dg_table.toggle_column_cbk(table,'general_checkin','1');
                        }
                        spt.app_busy.hide();
                        '''
                    }
                }
            )

        return {'menu_tag_suffix': 'CHECKIN', 'width': 210, 'opt_spec_list': menu_items}



    def get_custom_menu(my):

        menu_items = []

        for tool in my.custom_tools:
            view = tool.get_value("view")
            title = tool.get_value("title")
            if not title:
                title = Common.get_display_title(view)

            menu_item = {
                "type": "action", "label": title,
                "bvr_cb": {
                    'title': title,
                    'view': view,
                    'cbjs_action': '''
                    var activator = spt.smenu.get_activator(bvr);
                    var layout = activator.getParent(".spt_layout");
                    var selected = spt.table.get_selected_search_keys();

                    var kwargs = {
                        view: bvr.view,
                        search_keys: selected
                    }

                    var class_name = 'tactic.ui.panel.CustomLayoutWdg';
                    try {
                        spt.panel.load_popup(bvr.title, class_name, kwargs);
                    } catch(e) {
                        spt.alert(spt.exception.handler(e));
                    }
                    '''
                }
            }
            menu_items.append(menu_item)


        return {'menu_tag_suffix': 'CUSTOM', 'width': 210, 'opt_spec_list': menu_items}







    def get_view_menu(my):

        menu_items = []

        security = Environment.get_security()

        access_keys_dict = my.get_access_keys_dict()
        label_list = []
        if access_keys_dict.get('View'):
            label_list = access_keys_dict['View']

        project_code = Project.get_project_code()

        search_type = my.kwargs.get("search_type")
        search_type_obj = SearchType.get(search_type)

        # Column Manager menu item ...
        access_keys = my._get_access_keys("view_column_manager",  project_code)
        if security.check_access("builtin", access_keys, "allow") or 'Column Manager' in label_list:
            menu_items.append( {
                "type": "action",
                "label": "Column Manager",
                 "bvr_cb": {
                    'cbjs_action': '''
                        var activator = spt.smenu.get_activator(bvr);
                        var layout = activator.getParent('.spt_layout');
                        var panel = activator.getParent('.spt_panel');
                        var table = layout.getElement('.spt_table');

                        if (layout.getAttribute("spt_version") == "2") {
                            spt.table.set_layout(layout);
                            element_names = spt.table.get_element_names();
                        }
                        else {
                            element_names = spt.dg_table.get_element_names(table); 
                        }
                        bvr.args.element_names = element_names;
                        bvr.args.target_id = panel.getAttribute('id');


                        class_name = 'tactic.ui.panel.AddPredefinedColumnWdg';

                        spt.panel.load_popup(bvr.args.title, class_name, bvr.args);
                     ''',
                     'args': {
                        'title': "Column Manager",
                        'search_type': search_type,
                    }

                }
            } )


        if my.is_admin or 'Create New Column' in label_list:
            menu_items.append( {
                "type": "action",
                "label": "Create New Column",
                "bvr_cb": {
                    'args' : {'search_type': search_type},
                    'options': {
                        'class_name': 'tactic.ui.manager.ElementDefinitionWdg',
                        'popup_id': 'edit_column_defn_wdg',
                        'title': 'Create New Column'
                    },
                    'cbjs_action':
                        '''
                        var activator = spt.smenu.get_activator(bvr);
                        bvr.args.element_name = activator.getProperty("spt_element_name");
                        bvr.args.view = activator.getParent('.spt_layout').getAttribute('spt_view');
                        bvr.args.is_insert = true;
                        var popup = spt.popup.get_widget(evt,bvr);
                        popup.activator = activator;
                        '''
                }
            } )


            menu_items.append( { "type": "separator" })

       
        view = my.kwargs.get("view")
        if my.is_admin or 'Save Current View' in label_list:
            menu_items.append(
                { "type": "action", "label": "Save Current View <i style='font-size: 10px; opacity: 0.7'>(%s)</i>" % view,
                    "bvr_cb": {
                        'cbjs_action': "spt.dg_table.view_action_cbk('save','',bvr);",
                        'is_admin': my.is_admin,
                        'is_table_embedded_smenu_activator': True
                  }
                }
            )


        # This is a lot of work, so hiding
        """
        menu_items.append(
            { "type": "action", "label": "Edit Simple Search",
                "bvr_cb": {
                    'cbjs_action': "alert('Simple Search')",
                    'is_admin': is_admin,
                    'is_table_embedded_smenu_activator': True
              }
            }
        )
        """



        access_keys = my._get_access_keys("view_save_my_view",  project_code)

        if not my.embedded_table and (security.check_access("builtin",  access_keys, "allow", default='allow') or 'Save a New View' in label_list):
            menu_items.insert( 4,
                { "type": "action", "label": 'Save a New View',
                  "bvr_cb": {
                      # FIXME: Does this even do anything anymore???
                      'is_table_embedded_smenu_activator': True,

                      'dialog_id': my.view_save_dialog_id,
                      'cbjs_action': "spt.show($(bvr.dialog_id));",
                    }
                }
            ) 
        if my.is_admin or 'Edit Current View' in label_list:
            
            if menu_items and menu_items[-1] != { "type": "separator" }:
                menu_items.append( { "type": "separator" } )

            menu_items.append( 
                    { "type": "action", "label": "Edit Current View <i style='font-size: 10px; opacity: 0.7'>(%s)</i>" % view,
                  "bvr_cb": {'cbjs_action': "spt.dg_table.view_action_cbk('edit_current_view','',bvr);",
                             'is_table_embedded_smenu_activator': True
                            }
                }
            )

        if my.is_admin or 'Edit Config XML' in label_list:
            menu_items.append( 
              { "type": "action", "label": "Edit Config XML <i style='font-size: 10px; opacity: 0.7'>(%s)</i>" % view,
              "bvr_cb": {'cbjs_action': '''
                var class_name = "tactic.ui.panel.EditWdg"
                var server = TacticServerStub.get();
                var expr = "@GET(config/widget_config['search_type','"+bvr.search_type+"']['view','"+bvr.view+"'].code)";
                var config_code = server.eval(expr);
                if (config_code == "") {
                    spt.alert("No database definition for this view ["+bvr.view+"]");
                    return;
                }

                var kwargs = {
                   search_type: "config/widget_config",
                   code: config_code
                };
                spt.panel.load_popup("Config Edit", class_name, kwargs);
                ''',
                'view': view,
                'search_type': search_type_obj.get_base_key(),
                'is_table_embedded_smenu_activator': True
                }
              }
            )

        if menu_items and menu_items[-1] == { "type": "separator" }:
            menu_items.pop()


        return {'menu_tag_suffix': 'VIEW', 'width': 210, 'opt_spec_list': menu_items}


    def get_print_menu(my):

        from tactic.ui.panel import TablePrintLayoutWdg
        menu_items = []

        security = Environment.get_security()
        project_code = Project.get_project_code()

        access_keys_dict = my.get_access_keys_dict()
        label_list = []
        if access_keys_dict.get('Print'):
            label_list = access_keys_dict['Print']

        if my.is_admin or 'Print Selected' in label_list:
            menu_items.append(
                { "type": "action", "label": "Print Selected",
                        "bvr_cb": { 'cbjs_action': TablePrintLayoutWdg.get_print_action_js("selected_items") }
                }
            )
        if my.is_admin or 'Print Displayed' in label_list:
            menu_items.append(
                { "type": "action", "label": "Print Displayed",
                        "bvr_cb": { 'cbjs_action': TablePrintLayoutWdg.get_print_action_js("page_matched_items") }
                }
            )
        if my.is_admin or 'Print Matched' in label_list:
            menu_items.append(
                { "type": "action", "label": "Print Matched",
                        "bvr_cb": { 'cbjs_action': TablePrintLayoutWdg.get_print_action_js("all_matched_items") }
                }
            )

        return {'menu_tag_suffix': 'PRINT', 'width': 180, 'opt_spec_list': menu_items}



    def get_chart_menu(my):

        from tactic.ui.panel import TablePrintLayoutWdg
        menu_items = []

        security = Environment.get_security()
        project_code = Project.get_project_code()
        
        access_keys_dict = my.get_access_keys_dict()
        label_list = []
        if access_keys_dict.get('Chart'):
            label_list = access_keys_dict['Chart']

        if my.is_admin or 'Chart Items' in label_list:
            menu_items.append(
                { "type": "action", "label": "Chart Items",
                "bvr_cb": { 'cbjs_action': '''
                var activator = spt.smenu.get_activator(bvr);
                var top = activator.getParent(".spt_table_top");
                var table = top.getElement(".spt_table");
                var search_type = top.getAttribute("spt_search_type")
                var layout = activator.getParent(".spt_layout");
                var version = layout.getAttribute("spt_version");
                
                var elements = spt.dg_table.get_element_names(table);
                
                if (version == "2") {
                    elements = spt.table.get_element_names();
                } else {
                    var table = top.getElement(".spt_table");
                    elements = spt.dg_table.get_element_names(table);
                }

                kwargs = {
                'search_type': search_type,
                'y_axis': elements,
                };
                var title = "Chart: " + search_type;
                spt.panel.load_popup(title, 'tactic.ui.chart.ChartBuilderWdg', kwargs)
                '''}
                }
            )
        
        if my.is_admin or 'Chart Selected' in label_list:
            menu_items.append(
                { "type": "action", "label": "Chart Selected",
                "bvr_cb": { 'cbjs_action': '''
                var activator = spt.smenu.get_activator(bvr);

                var top = activator.getParent(".spt_table_top");
                var search_type = top.getAttribute("spt_search_type")
                
                var layout = activator.getParent(".spt_layout");
                var version = layout.getAttribute("spt_version");
                
                var selected_tbodies = [];
                var elements = [];
                if (version == "2") {
                    selected = spt.table.get_selected_search_keys();
                    elements = spt.table.get_element_names();
                } else {
                    var table = top.getElement(".spt_table");
                    elements = spt.dg_table.get_element_names(table);
                    selected = spt.dg_table.get_selected_search_keys( table );
                }
                if (selected.length == 0) {
                    spt.alert("No items selected");
                }
                else {

                    kwargs = {
                    'search_type': search_type,
                    'y_axis': elements,
                    'search_keys': selected
                    };
                    var title = "Chart: " + search_type;
                    spt.panel.load_popup(title, 'tactic.ui.chart.ChartBuilderWdg', kwargs)
                }
                '''}
                }
            )
            
            #{ "type": "action", "label": "Chart This Page of Matched Items",
                #        "bvr_cb": { 'cbjs_action': TablePrintLayoutWdg.get_print_action_js("page_matched_items") }
                #},
                #{ "type": "action", "label": "Chart All Items Matching Search",
                #        "bvr_cb": { 'cbjs_action': TablePrintLayoutWdg.get_print_action_js("all_matched_items") }
                #}
        
        return {'menu_tag_suffix': 'CHART', 'width': 210, 'opt_spec_list': menu_items}


    def _get_access_keys(my, key, project_code):
        '''get access keys for a builtin rule'''
        access_key1 = {
            'key': key,
            'project': project_code
        }

        access_key2 = {
            'key': key 

        }
        access_keys = [access_key1, access_key2]
        return access_keys


class PageHeaderGearMenuWdg(BaseRefreshWdg):
    '''Gear Menu for Page Header'''

    def init(my):
        pass


    def get_args_keys(my):
        return {
        }


    def get_display(my):
        security = Environment.get_security()
        if security.check_access("builtin", "view_site_admin", "allow"):
            menus = [ my.get_main_menu(), my.get_add_menu(), my.get_edit_menu(), my.get_tools_menu(), my.get_help_menu() ]
        else:
            menus = [ my.get_main_menu(), my.get_edit_menu(), my.get_help_menu() ]


        """
        btn_dd = DivWdg()
        btn_dd.add_styles("width: 36px; height: 18px; padding: none; padding-top: 1px;")

        btn_dd.add( "<img src='/context/icons/common/transparent_pixel.gif' alt='' " \
                   # "title='TACTIC Actions Menu' class='tactic_tip' " \
                    "style='text-decoration: none; padding: none; margin: none; width: 4px;' />" )
        btn_dd.add( "<img src='/context/icons/silk/cog.png' alt='' " \
                "title='TACTIC Actions Menu' class='tactic_tip' " \
                    "style='text-decoration: none; padding: none; margin: none;' />" )
        btn_dd.add( "<img src='/context/icons/silk/bullet_arrow_down.png' alt='' " \
                "title='TACTIC Actions Menu' class='tactic_tip' " \
                    "style='text-decoration: none; padding: none; margin: none;' />" )
        """

        from tactic.ui.widget import SingleButtonWdg
        btn_dd = SingleButtonWdg(title='Global Options', icon="G_SETTINGS_GRAY", show_arrow=True)



        #btn_dd.add_behavior( { 'type': 'hover',
        #            'mod_styles': 'background-image: url(/context/icons/common/gear_menu_btn_bkg_hilite.png); ' \
        #                            'background-repeat: no-repeat;' } )
        smenu_set = SmartMenu.add_smart_menu_set( btn_dd, { 'DG_TABLE_GEAR_MENU': menus } )
        SmartMenu.assign_as_local_activator( btn_dd, "DG_TABLE_GEAR_MENU", True )
        return btn_dd


    def get_main_menu(my):

        security = Environment.get_security()
        if security.check_access("builtin", "view_site_admin", "allow"):

            return { 'menu_tag_suffix': 'MAIN', 'width': 110, 'opt_spec_list': [
                { "type": "submenu", "label": "Add", "submenu_tag_suffix": "ADD" },
                { "type": "submenu", "label": "Edit", "submenu_tag_suffix": "EDIT" },
                { "type": "submenu", "label": "Tools", "submenu_tag_suffix": "TOOLS" },
                { "type": "submenu", "label": "Help", "submenu_tag_suffix": "HELP" },
            ] }

        else:
            return { 'menu_tag_suffix': 'MAIN', 'width': 110, 'opt_spec_list': [
                { "type": "submenu", "label": "Edit", "submenu_tag_suffix": "EDIT" },
                { "type": "submenu", "label": "Help", "submenu_tag_suffix": "HELP" },
            ] }



    def get_add_menu(my):
        menu = {
            'menu_tag_suffix': 'ADD', 'width': 200
        }
        
        opt_spec_list = [
            { "type": "action", "label": "Add New sType",
                "bvr_cb": {
                    'cbjs_action': '''
                    var class_name = 'tactic.ui.app.SearchTypeCreatorWdg';
                    spt.panel.load_popup("Create New sType", class_name);
                    '''
                }
            },
        ]

        from pyasm.biz import Project
        project = Project.get()
        search_types = project.get_search_types()

        if search_types:
            opt_spec_list.append( { "type": "separator" } )

        for search_type_obj in search_types:
            title = search_type_obj.get_title()
            search_type = search_type_obj.get_value("search_type")

            opt_spec_list.append(
            { "type": "action", "label": "Add New %s" % title,
                "bvr_cb": {
                    'cbjs_action': '''
                    spt.tab.set_main_body_tab();
                    spt.tab.add_new("%(title)s", "%(title)s", "tactic.ui.panel.table_layout_wdg.FastTableLayoutWdg", { search_type: "%(search_type)s", view: "table" } );
                    spt.panel.load_popup("Add New Item", "tactic.ui.panel.EditWdg", { search_type: "%(search_type)s" } )
                    ''' % { 'title': title, 'search_type': search_type }
                }
            }
            )

        menu['opt_spec_list'] = opt_spec_list;

        return menu



    def get_edit_menu(my):
        return {
            'menu_tag_suffix': 'EDIT', 'width': 200, 'opt_spec_list': [

                # { "type": "title", "label": "Edit" },

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
                    "bvr_cb": {'cbjs_action': "spt.undo_cbk();"}
                },

                { "type": "action", "label": "Redo Last Server Transaction",
                    "bvr_cb": {'cbjs_action': "spt.redo_cbk();"}
                },

        ] }


    def get_tools_menu(my):
        menu_items = [
                # { "type": "title", "label": "Tools" },
                { "type": "action", "label": "Web Client Output Log",
                        "bvr_cb": {'cbjs_action': "spt.js_log.show(false);"} },
                { "type": "action", "label": "TACTIC Script Editor",
                        "bvr_cb": {'cbjs_action': 'spt.panel.load_popup("TACTIC Script Editor",\
                                    "tactic.ui.app.ShelfEditWdg", {}, {"load_once": true} );'} }
        ]
      

        return { 'menu_tag_suffix': 'TOOLS', 'width': 160, 'opt_spec_list': menu_items }


    def get_help_menu(my):
        return {
            'menu_tag_suffix': 'HELP', 'width': 180, 'opt_spec_list': [

                # { "type": "title", "label": "Help" },

                { "type": "action", "label": "Documentation",
                    "bvr_cb": {'cbjs_action': '''
                        spt.help.load_alias("main");
                    '''}
                },

                { "type": "action", "label": "TACTIC Community",
                    "bvr_cb": {'cbjs_action': "window.open('http://community.southpawtech.com/');"}
                }

        ] }


