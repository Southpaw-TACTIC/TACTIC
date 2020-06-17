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
__all__ = ["ManageViewPanelWdg", "ManageSideBarDetailWdg", "ManageSideBarBookmarkMenuWdg", "ManageSideBarDetailCbk", "ManageSideBarSecurityCbk"]

import os, types
import math

from pyasm.common import Xml, Environment, Common, UserException, XmlException
from pyasm.command import Command
from pyasm.search import Search, SearchType, SObject
from pyasm.biz import Project
from pyasm.web import DivWdg, HtmlElement, SpanWdg, Table, WebContainer, Widget, FloatDivWdg
from pyasm.widget import SelectWdg, WidgetConfig, IconWdg, CheckboxWdg, HiddenWdg
from pyasm.widget import TextAreaWdg, TextWdg, ButtonWdg, ProdIconButtonWdg, HintWdg
from pyasm.security import AccessRuleBuilder
from tactic.ui.common import BaseRefreshWdg
from tactic.ui.activator import ButtonForDropdownMenuWdg
from tactic.ui.input import TextInputWdg
from tactic.ui.widget import SearchTypeSelectWdg, TextBtnWdg, TextBtnSetWdg, IconChooserWdg, ButtonRowWdg, ButtonNewWdg, ActionButtonWdg
from tactic.ui.container import HorizLayoutWdg, PopupWdg, RoundedCornerDivWdg, Menu, MenuItem, SmartMenu


class ManageViewPanelWdg(BaseRefreshWdg):
    '''Panel to manage views ... this is mean to be a generic interface for
    manipulating the side bar views'''

    def get_args_keys(self):
        return {
        'search_type': 'search type of the view',
        'view': 'view to be edited'
        }

   

    def init(self):
        self.search_type = self.kwargs.get('search_type')
        if not self.search_type:
            self.search_type = "SideBarWdg"

        self.view = self.kwargs.get('view')
        if not self.view:
            self.view = "project_view"

        self.base_view = self.view  # should be either 'project_view' or 'my_view'

        # for Manage self views
        self.login = None
        # Do not take the view as is, a user can only change his own view
        if self.view.startswith('my_view'):
            self.view = 'my_view_%s' %Environment.get_user_name()
            self.login = Environment.get_user_name()
            self.is_personal = 'true'
        else:
            self.is_personal = 'false'


    def get_tool_bar(self):

        widget = DivWdg()

        button_row = ButtonRowWdg()
        widget.add(button_row)
        button_row.add_style("float: left")
        widget.add_style("height: 40px")
        button_row.add_style("margin-right: 50px")

        # refresh button
        refresh_button = ButtonNewWdg(title="Refresh", icon="FA_REFRESH")
        button_row.add(refresh_button)
        refresh_button.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            spt.app_busy.show("Refreshing Side Bar Manager");
            var top = bvr.src_el.getParent(".spt_view_manager_top" );
            spt.panel.refresh(top);
            spt.app_busy.hide();
            '''
        } )



        trash_div = SpanWdg()
        # reset some global variables on load
        trash_div.add_behavior({'type':'load', 'cbjs_action':'spt.side_bar.trashed_items=[]; spt.side_bar.changed_views={}'})

        trash_div.set_id('trash_me')

        bvr = { 
            "type": "click_up",
            'cbjs_action': '''alert('Drag and drop link or folder here to remove it.')'''
        }


        trash_button = ButtonNewWdg(title="Drag to Trash", icon="FA_TRASH")
        button_row.add(trash_button)
        trash_button.add_behavior(bvr)
        trash_button.add_class("spt_side_bar_trash")
        trash_button.set_attr("SPT_ACCEPT_DROP", "manageSideBar")

        bvr = { "type": "click_up",\
                'cbjs_action': "spt.side_bar.manage_section_action_cbk({'value':'save'},'%s',%s);" % (self.view, self.is_personal)} 


        # save button
        save_button = ButtonNewWdg(title="Save Order of Elements to Side Bar", icon="FA_SAVE")
        button_row.add(save_button)
        save_button.add_behavior(bvr)




        #button_row = ButtonRowWdg()
        #widget.add(button_row)

        # new link button
        link_button = ButtonNewWdg(title="Add New Link", icon="FA_PLUS")
        button_row.add(link_button)
        link_button.add_behavior( {
        'type': 'click_up',
        'kwargs': {
            'view': self.view,
            'element_name': '',
            'is_personal': self.is_personal,
        },
        'cbjs_action': '''
        var top = bvr.src_el.getParent(".spt_view_manager_top");
        var detail = top.getElement(".spt_view_manager_detail");
        var class_name = "tactic.ui.panel.ManageSideBarDetailWdg";
        spt.panel.load(detail, class_name, bvr.kwargs);
        '''
        } )

        folder_button = ButtonNewWdg(title="New Folder", icon="FA_FOLDER")
        button_row.add(folder_button)
        folder_button.add_behavior( {
            'type': 'click_up',
            'cbjs_action': "spt.side_bar.manage_section_action_cbk({'value':'new_folder'},'%s',%s);" % (self.view,self.is_personal)
            } )


    
        # action button
        action_button = ButtonNewWdg(title="Extra Options", icon="FA_COG", show_arrow=True)
        button_row.add(action_button)

        from tactic.ui.container import SmartMenu
        smenu_set = SmartMenu.add_smart_menu_set( action_button.get_button_wdg(), { 'BUTTON_MENU': self.get_action_menu_xxx() } )
        SmartMenu.assign_as_local_activator( action_button.get_button_wdg(), "BUTTON_MENU", True )


        from tactic.ui.app import HelpButtonWdg
        help_button = HelpButtonWdg(alias='managing-sidebar')
        widget.add( help_button )


        return widget


    def get_display(self):
        div = self.top

        div.add_color("background", "background")
        div.add_color("color", "color")
        self.set_as_panel(div)

        div.add_class( "SPT_VIEW_MANAGER_TOP" )
        div.add_class( "spt_view_manager_top" )
        div.set_attr( "spt_base_view", self.base_view )

        # check for potential multiple definitions for SideBarWdg
        search = Search("config/widget_config")
        search.add_filter("search_type", 'SideBarWdg')
        search.add_filter("view", "definition")
        search.add_op('begin')
        search.add_filter('login', None)
        user = Environment.get_user_name()
        search.add_filter('login', user)
        search.add_op('or')

        configs = search.get_sobjects()
        if len(configs) > 2:
            div.add(HtmlElement.hr())
            codes = SObject.get_values(configs, 'code')
            span = SpanWdg("WARNING: More than 1 definition view found for SideBarWdg where code = [%s].\
                    Please make sure you do not have more than 1 defined or results \
                    may be unpredictable. " %', '.join(codes))
            span.add_style('color', 'red')
            div.add(span)



        # add the template view containing the possible items to be added
        # ie: New Folder, New Entry, New Separator
        menu_div = DivWdg()
        menu_div.set_id("menu_item_template")
        menu_div.add_style("display: none")
        menu_div.add( self.get_section_wdg("_template", editable=False) )
        div.add(menu_div)


        table = Table()
        table.add_color("color", "color")
        table.add_row()
        table.add_style("width: 100%")

        td = table.add_cell()

        
        tool_bar = self.get_tool_bar()
        td.add(tool_bar)
        tool_bar.add_color("background", "background2")
        tool_bar.add_style("padding: 5px 5px 3px 5px")
        tool_bar.add_style("border-bottom: solid 1px %s" % tool_bar.get_color("border"))



        table.add_row()


        # add the section
        td = table.add_cell()
        td.add_class("SPT_CHANGE")
        #td.add_border()
        td.add_style("padding: 10px 30px 30px 30px")
        td.add_style("max-width: 200px")
        td.add_style("width: 200px")
        td.add_style("vertical-align: top")
        td.add_color("background", "background", -10)

        title_div = DivWdg()
        td.add(title_div)
        title_div.add_color("background", "background2")
        title_div.add_color("color", "color2")
        title_div.add("Side Bar Preview")
        #td.add("<b>Preview of Side Bar</b><hr/>")
        title_div.add_style("font-weight: bold")
        title_div.add_style("font-size: 16px")
        title_div.add_style("padding: 10px")
        title_div.add_style("margin: -11px -30px 10px -10px")



        # Test for changes
        """
        changes = DivWdg()
        td.add(changes)
        changes.add_class("SPT_CHANGE")
        changes.add_attr("spt_change", "false")

        test = DivWdg()
        changes.add(test)
        test.add("test")
        test.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        var el = bvr.src_el;
        while (true) {
            var change_el = el.getParent(".SPT_CHANGE");
            if (change_el == null) break;

            change_el.setAttribute("spt_change", "true");
            change_el.setStyle("border", "solid 1px blue");

            el = change_el;
        }
        '''
        } )
        """




        project_view = DivWdg()
        project_view.set_id("menu_item_list")
        project_view.add( self.get_section_wdg(self.view))
        td.add(project_view)



        # add detail information
        no_item = DivWdg()
        td = table.add_cell(no_item)
        no_item.add("<-- Select item on the left side to view details.")
        no_item.add_style("padding: 10px")
        no_item.add_style("padding-top: 100px")
        no_item.add_style("width: 400px")
        no_item.add_style("height: 300px")
        no_item.add_border()
        no_item.add_color("background", "background", -10)
        
        # this is an old way of setting up the panel where we don't call
        # set_panel_as() within the class
        # set the panel information
        td.set_id("manage_side_bar_detail")
        td.add_class("spt_view_manager_detail")
        td.add_style("display", "table-cell")
        td.add_attr("spt_class_name", "tactic.ui.panel.ManageSideBarDetailWdg")
        td.add_attr("spt_search_type", self.search_type)
        td.add_attr("spt_personal", self.is_personal)
        td.add_attr("spt_login", self.login)

        td.add_style("vertical-align: top")
        td.add_style("width: 300px")
        td.add_style("padding: 20px 50px 50px 50px")
        td.add_color("background", "background", -5)

     


        # Add Icon Chooser, for use in the simple widget of the detail widget ... we add it here
        # so that it is not always being generated each time the detail simple widget gets refreshed
        icon_chooser = IconChooserWdg( is_popup=True )
        div.add( icon_chooser )

        td.add("<br/>")

        div.add(table)


        # add the predefined list
        predefined = self.get_predefined_wdg()
        div.add(predefined)
        

        return div


    def get_predefined_wdg(self):
        project = Project.get()
        project_type = project.get_type()

        from tactic.ui.container import PopupWdg
        popup = PopupWdg(id="predefined_side_bar", allow_page_activity=True, width="320px")
        popup.add_title("Predefined Side Bar Elements")
        popup.add( self.get_section_wdg(view=project_type, default=True))

        return popup



    def get_menu_item(self, element_name, display_handler):

        content = DivWdg()
        content.add_attr("spt_element_name", element_name)
        content.add_class("hand")

        # add the drag/drop behavior
        behavior = {
            "type": 'drag',
            "mouse_btn": 'LMB',
            "modkeys": '',
            "src_el": '@',
            "cbfn_setup": 'spt.side_bar.pp_setup',
            "cbfn_motion": 'spt.side_bar.pp_motion',
            "cbfn_action": 'spt.side_bar.pp_action',
        }
        content.add_behavior(behavior)

        content.set_id("manage_%s" % element_name)
        content.add_style("position: relative")
        content.add_style("margin: 3px")
        content.add_style("left: 0")
        content.add_style("top: 0")
        content.add_style("z-index: 100")
        if display_handler == "SeparatorWdg":
            content.add( HtmlElement.hr() )
        else:
            content.add(element_name)

        return content



    def get_action_menu_xxx(self):


        if self.is_personal=='true':
            is_personal = 'true'
        else:
            is_personal = 'false'

        security = Environment.get_security() 
 

        menu = Menu(width=180)
        menu.set_allow_icons(False)


        menu_item = MenuItem(type='title', label='Actions')
        menu.add(menu_item)


        if security.check_access("builtin", "view_site_admin", "allow"):

            # add predefined columns
            menu_item = MenuItem(type='action', label='New Link')
            menu.add(menu_item)
            #menu_item.add_behavior( {
            #    'cbjs_action': "spt.side_bar.manage_section_action_cbk({'value':'new_link'},'%s',%s);" % (self.view,is_personal)
            #} )

            menu_item.add_behavior( {
            'kwargs': {
                'view': self.view,
                'element_name': '',
                'is_personal': self.is_personal,
            },
            'cbjs_action': '''
            var activator = spt.smenu.get_activator(bvr);
            var top = activator.getParent(".spt_view_manager_top");
            var detail = top.getElement(".spt_view_manager_detail");
            var class_name = "tactic.ui.panel.ManageSideBarDetailWdg";
            spt.panel.load(detail, class_name, bvr.kwargs);
            '''
            } )



            menu_item = MenuItem(type='action', label='New Folder')
            menu.add(menu_item)
            menu_item.add_behavior( {
                'cbjs_action': "spt.side_bar.manage_section_action_cbk({'value':'new_folder'},'%s',%s);" % (self.view,is_personal)
            } )

            menu_item = MenuItem(type='action', label='New Separator')
            menu.add(menu_item)
            menu_item.add_behavior( {
                'cbjs_action': "spt.side_bar.manage_section_action_cbk({'value':'new_separator'},'%s',%s);" % (self.view,is_personal)
            } )



            menu_item = MenuItem(type='separator')
            menu.add(menu_item)


        if is_personal == 'false':
            menu_item = MenuItem(type='action', label='Show Predefined')
            menu.add(menu_item)
            menu_item.add_behavior( {
                'cbjs_action': "spt.side_bar.manage_section_action_cbk({'value':'predefined'},'%s',%s);" % (self.view,is_personal)
            } )

        menu_item = MenuItem(type='action', label='Save Side Bar')
        menu.add(menu_item)
        menu_item.add_behavior( {
            'cbjs_action': "spt.side_bar.manage_section_action_cbk({'value':'save'},'%s',%s);" % (self.view,is_personal)
        } )

        return menu




    def get_section_wdg(self, view, editable=True, default=False):

        from .panel_wdg import SideBarBookmarkMenuWdg

        title = ""
        target_id = "sobject_relation"
        if editable:
            edit_mode = 'edit'
        else:
            edit_mode = 'read'
        kwargs = {
            'title': title,
            'view': view,
            'target_id': target_id,
            'width': '200',
            'prefix': 'manage_side_bar',
            'mode': edit_mode,
            'personal': self.is_personal,
            'default': str(default)
        }
        if view in ["definition", "custom_definition"]:
            kwargs['recurse'] = "false"
            kwargs['sortable'] = "true"

        id = "ManageSideBarBookmark_%s" % view
        section_div = DivWdg(id=id)
        section_div.add_class("spt_view_manager_section");
        section_div.add_style("display: block")
        section_div.set_attr('spt_class_name', "tactic.ui.panel.ManageSideBarBookmarkMenuWdg")
        for name, value in kwargs.items():
            if name == "config":
                continue
            section_div.set_attr("spt_%s" % name, value)

        section_wdg = ManageSideBarBookmarkMenuWdg(**kwargs)
        section_div.add(section_wdg)
        return section_div


from .panel_wdg import SideBarBookmarkMenuWdg
class ManageSideBarBookmarkMenuWdg(SideBarBookmarkMenuWdg):
   

    def get_detail_class_name(self):
        return "tactic.ui.panel.ManageSideBarDetailWdg"


    #
    # behavior functions
    #
    def add_separator_behavior(self, separator_wdg, element_name, config, options):
        # FIXME: this edit_allowed variable seems redundant
        edit_allowed = True
        if self.mode == 'edit' and edit_allowed:
            # add the drag/drop behavior
            behavior = {
                "type": 'drag',
                "drag_el": 'drag_ghost_copy',
                "drop_code": 'manageSideBar',
                "cb_set_prefix": 'spt.side_bar.pp',
            }
            separator_wdg.add_behavior(behavior)
            separator_wdg.set_attr("SPT_ACCEPT_DROP", "manageSideBar")



    def add_folder_behavior(self, folder_wdg, element_name, config, options):
        '''this method provides the changed to add behaviors to a folder'''

        # determines whether the folder opens on click
        recurse = self.kwargs.get("recurse")!= "false"

        # edit behavior
        edit_allowed = True
        if self.mode == 'edit' and edit_allowed:
            # IS EDITABLE ...

            # add the drag/drop behavior
            behavior = {
                "type": 'drag',
                "drag_el": 'drag_ghost_copy',
                "use_copy": True,
                "drop_code": 'manageSideBar',
                "cb_set_prefix": 'spt.side_bar.pp'
            }
            if recurse:
                behavior['cbjs_action_onnomotion'] = '''
                    spt.side_bar.toggle_section_display_cbk(evt,bvr);
                    spt.side_bar.display_element_info_cbk(evt,bvr);
                '''
            else:
                behavior['cbjs_action_onnomotion'] = 'spt.side_bar.display_element_info_cbk(evt,bvr);'
            behavior['class_name'] = self.get_detail_class_name()
           
            folder_wdg.add_behavior(behavior)
            folder_wdg.set_attr("SPT_ACCEPT_DROP", "manageSideBar")
        else:
            # IS NOT EDITABLE ...
            if recurse:
                behavior = {
                    'type':         'click_up',
                    'cbfn_action':  'spt.side_bar.toggle_section_display_cbk',
                }
                folder_wdg.add_behavior( behavior )

        SmartMenu.assign_as_local_activator( folder_wdg, 'LINK_CTX' )



    def add_title_behavior(self, title_wdg, element_name, config, options):
        '''this method provides the changed to add behaviors to a title'''

        # make it draggable
        edit_allowed = True
        if self.mode == 'edit' and edit_allowed:
                # add the drag/drop behavior
            behavior = {
                "type": 'drag',
                "drag_el": 'drag_ghost_copy',
                "drop_code": 'manageSideBar',
                "cb_set_prefix": 'spt.side_bar.pp',
                'cbjs_action_onnomotion':  'spt.side_bar.display_element_info_cbk(evt,bvr);',
                'class_name':   self.get_detail_class_name()
            }
           
                
            title_wdg.add_behavior(behavior)

            title_wdg.set_attr("SPT_ACCEPT_DROP", "manageSideBar")
        
 

    def add_link_behavior(self, link_wdg, element_name, config, options):
        '''this method provides the changed to add behaviors to a link'''

        # check security
        #default_access = "view"
        #security = Environment.get_security()
        #if not security.check_access("side_bar", element_name, "edit", default=default_access):
        #    return

        # make it draggable
        edit_allowed = True
        if self.mode == 'edit' and edit_allowed:
                # add the drag/drop behavior
            behavior = {
                "type": 'drag',
                "drag_el": 'drag_ghost_copy',
                "drop_code": 'manageSideBar',
                "cb_set_prefix": 'spt.side_bar.pp',
                'cbjs_action_onnomotion':  'spt.side_bar.display_element_info_cbk(evt,bvr);',
                'class_name':   self.get_detail_class_name()
            }
           
                
            link_wdg.add_behavior(behavior)

            link_wdg.set_attr("SPT_ACCEPT_DROP", "manageSideBar")

            SmartMenu.assign_as_local_activator( link_wdg, 'LINK_CTX' )



    def add_link_context_menu(self, widget):
        menu = Menu(width=180)
        menu.set_allow_icons(False)

        menu_item = MenuItem(type='title', label='Actions')
        menu.add(menu_item)


        menu_item = MenuItem(type='action', label='Remove')
        menu.add(menu_item)
        menu_item.add_behavior({ 
            'type': 'click_up',
            'cbjs_action': '''
            var activator = spt.smenu.get_activator(bvr);

            if (! activator.hasClass("spt_side_bar_element")) {
                activator = activator.getParent('.spt_side_bar_element');
            }
            if (activator.hasClass("spt_side_bar_element")) {
                var name = activator.getAttribute('spt_element_name');
                var view = activator.getAttribute('spt_view');
                spt.side_bar.changed_views[view] = true;
                spt.side_bar.trashed_items.push(name);
                spt.behavior.destroy_element(activator);
            }
        ''' } )


        menus = [menu.get_data()]
        menus_in = {
            'LINK_CTX': menus,
        }
        SmartMenu.attach_smart_context_menu( widget, menus_in, False )

        return menu

        


class ManageSideBarDetailWdg(BaseRefreshWdg):
    '''Display the advanced xml value or simple name and title of each element'''
    def get_args_keys(self):
        return {
        'element_name': 'name of the element to get information from',
        'path': 'path of the side bar link',
        'search_type': 'search_type of the view',
        'view': 'view of the element',
        'mode': 'mode of the detail widget',
        'config_mode': 'config mode',
        'default': 'default for getting config',
        'login': 'login of this view if personal',
        'personal': 'True if it is a personal view'
        }


    def get_config(self, search_type, view, default=False):
        config = ManageSideBarBookmarkMenuWdg.get_config(search_type, view, default, personal=self.personal)
        return config

    def init(self):
        self.user_error = None
        self.search_type = self.kwargs.get('search_type')
        if not self.search_type:
            self.search_type = "SideBarWdg"
        
        self.element_name = self.kwargs.get('element_name')
        if not self.element_name:
            web = WebContainer.get_web()
            self.element_name = web.get_form_value("config_element_name")
        

        self.config_mode = self.kwargs.get('config_mode')
        self.default = self.kwargs.get('default')
        self.login = self.kwargs.get('login')
        self.personal = self.kwargs.get('personal')=='true'
        # it's important that self.login is explicit
        if self.login == 'None' or not self.login:
            self.login = None

        self.view = self.kwargs.get('view')
        assert self.view


        try:
            # save the display definition
            cbk = ManageSideBarDetailCbk(search_type=self.search_type,element_name=self.element_name, view=self.view, login=self.login)
            Command.execute_cmd(cbk)
        except UserException as e:
            self.user_error = e.__str__()
        except XmlException as e:
            self.user_error = e.__str__()
            

        # save the security settings
        cbk = ManageSideBarSecurityCbk(search_type=self.search_type,element_name=self.element_name)
        Command.execute_cmd(cbk)

        self.config_string = ""
        self.title_string = ""
        self.icon_string = ""
        self.name_string = ""
        self.widget_string = ""
        self.state_string = ""
        self.visible_string = ""

        if self.element_name:
            self.config = self.get_config(self.search_type, self.view )
            node = self.config.get_element_node(self.element_name)
            if node is not None:

                config_xml = self.config.get_xml()
                self.config_string = config_xml.to_string(node)
            attributes = self.config.get_element_attributes(self.element_name)
            self.title_string = attributes.get("title")
            self.icon_string = attributes.get("icon")
            if self.icon_string:
                self.icon_string = self.icon_string.upper()
            self.name_string = attributes.get("name")
            self.state_string = attributes.get("state")
            self.visible_string = attributes.get("is_visible")

            self.widget_string = self.config.get_display_handler(self.element_name)
        else:
            self.config = None


    def get_display(self):

        # determine if this is a new entry
        if not self.element_name:
            self.is_new = True
        else:
            self.is_new = False


        # add the detail widget
        from tactic.ui.container import RoundedCornerDivWdg
        detail_wdg = DivWdg()
        detail_wdg.add_style("width: 600px")
        if self.user_error:
            detail_wdg.add_behavior({'type':'load',
                'cbjs_action': 'alert(bvr.user_error)',
                'user_error': self.user_error})

        self.set_as_panel(detail_wdg)

        if self.kwargs.get("mode") == "empty":
            overlay = DivWdg()
            detail_wdg.add(overlay)

        detail_wdg.add_border()
        detail_wdg.add_color("color", "color")
        detail_wdg.add_color("background", "background", -10)
        detail_wdg.add_style("padding: 10px")

        detail_wdg.set_id('side_bar_detail')
        detail_wdg.add_class('spt_side_bar_detail_top')

        # FIXME: is this needed here?  This is being mixed up with
        # ElementDefinitionWdg
        detail_wdg.add_class('spt_element_top')

        title_div = DivWdg()
        if self.is_new:
            icon = IconWdg("New Element", IconWdg.NEW)
            title_div.add(icon)
            title_div.add("Create New Side Bar Link")
        else:
            title_div.add("Side Bar Link Detail")
        title_div.add_color("background", "background3")
        title_div.add_style("padding: 8px")
        title_div.add_style("margin: -11px -11px 10px -11px")
        title_div.add_style("font-weight: bold")
        title_div.add_border()
        detail_wdg.add(title_div)

        detail_wdg.add("<br/>")


        button = ActionButtonWdg(title='Save')
        button.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            spt.app_busy.show("Saving Definition");
            spt.side_bar.save_definition_cbk(bvr);
            spt.app_busy.hide();
            '''
        } )
        button.add_style("float: right")
        button.add_style("margin-top: -3px")
        detail_wdg.add(button)


        # put in the selection for simple or advanced
        detail_wdg.add("Mode: ")
        select = SelectWdg("config_mode")
        select.add_style("width: 125px")
        values = ['simple', 'advanced']
        select.set_option("values", values)
        
        #if self.config_mode:
        #    select.set_value(self.config_mode)
        select.set_persistence()
        scripts = []
        scripts.append('''
        var top = bvr.src_el.getParent(".spt_side_bar_detail_top");
        var simple = top.getElement(".spt_config_simple");
        var advanced = top.getElement(".spt_config_advanced");
        var definition = top.getElement(".spt_config_definition");
        spt.simple_display_toggle( simple )
        spt.simple_display_toggle( advanced )
        spt.simple_display_toggle( definition )
        ''')
        scripts.append(select.get_save_script())
        select.add_behavior({'type': 'change',
                'cbjs_action': ';'.join(scripts)})
        
        select.add_class('spt_config_mode')
        mode = select.get_value()

        #if self.icon_string:
        #    select.set_value(self.icon_string)
        #select.add_empty_option("-- Select --")
        detail_wdg.add(select)

        detail_wdg.add(HtmlElement.br(2))

        simple_wdg = self.get_simple_definition_wdg()
        simple_wdg.add_class("spt_config_simple")
        detail_wdg.add( simple_wdg )

        advanced_wdg = self.get_advanced_definition_wdg()
        advanced_wdg.add_class("spt_config_advanced")
        detail_wdg.add( advanced_wdg )

        detail_wdg.add(HtmlElement.br(1))

        display_wdg = self.get_display_definition_wdg()
        detail_wdg.add( display_wdg )


        if mode != "advanced":
            simple_wdg.add_style("display", "block")
            display_wdg.add_style("display", "block")
            advanced_wdg.add_style("display", "none")
        else:
            simple_wdg.add_style("display", "none")
            display_wdg.add_style("display", "none")
            advanced_wdg.add_style("display", "block")

        detail_wdg.add(HtmlElement.br(1))


        if not self.personal:
            security_wdg = self.get_security_wdg()
            detail_wdg.add(security_wdg)


        button_div = DivWdg()
        button_div.add_style("padding: 10px")
        button_div.add_style("text-align: center;")


        button = ActionButtonWdg(title='Save')
        button.add_behavior( {
            'type': 'click_up',
            'cbjs_action': 'spt.side_bar.save_definition_cbk(bvr)'
        } )
        button_div.add(button)
        button_div.add_style("float: right")

        detail_wdg.add(button_div)

        detail_wdg.add(HiddenWdg('view', self.view))
        detail_wdg.add("<br clear='all'/>")

        return detail_wdg



    def get_display_definition_wdg(self):
        '''Attempt to display this Xml is UI form. but since these classes like
        LinkWdg and SideBarSectionWdg are not real classes, disable drawing of this for now'''
        def_wdg = DivWdg()
        def_wdg.add_class( "SPT_SIMPLE_DEFINITION_WDG" )
        def_wdg.add_class( "spt_config_definition" )
        def_wdg.add_style("margin-top: 10px")
        def_wdg.add_style("padding: 10px")
        def_wdg.add_border()
        def_wdg.add_color("background", "background", -8)
        def_wdg.add_color("color", "color")
        title = DivWdg()
        title.add("Display Definition")
        title.add_style("margin-top: -23px")
        def_wdg.add(title)

        if self.is_new:
            widget_key = None
            display_options = {}
            display_class = "LinkWdg"
        elif not self.config:
            def_wdg.add("<br/>-- No options --<br/>")
            return def_wdg
        else:
            widget_key = None
            display_options = self.config.get_display_options(self.element_name)
            display_class = self.config.get_display_handler(self.element_name)

        def_wdg.add("<br/>")

        # DO NOT USE class_name as these classes are defined in the display_handler


        # Put in a hack here for Sidebar definition which uses a slightly
        # non standard config.  <display class='xxx'> is used to differentiate
        # between links, separators and folders.  The real class is
        # embedded in the <class_name> tag
        if display_class in ['LinkWdg']:
            display_class = display_options.get("class_name")
            widget_key = display_options.get("widget_key")
            if not display_class and not widget_key:
                widget_key = 'view_panel'

            from tactic.ui.manager import WidgetClassSelectorWdg
            class_labels = ['Layout with Search', 'Custom Layout', 'Edit Layout', 'Tile Layout', 'Fast Table Layout', '-- Class Path --']
            class_values = ['view_panel', 'custom_layout', 'edit_layout', 'tile_layout', 'fast_layout', '__class__']
            default_class='view_panel'
            class_selector = WidgetClassSelectorWdg(display_class=display_class,widget_key=widget_key,display_options=display_options,class_values=class_values,class_labels=class_labels, default_class=default_class, show_action=False, mode="layout")
            def_wdg.add(class_selector) 

        elif display_class in ['TitleWdg']:
            def_wdg.add("<i>-- Titles do not have any configurable attributes --</i>")
        elif display_class in ['SideBarSectionLinkWdg','FolderWdg']:
            def_wdg.add("<i>-- Folders do not have any configurable attributes --</i>")
        else:
            def_wdg.add("<i>Definition cannot be found. Please redefine it or drag the link to Trash.</i>")

            display_class = display_options.get("class_name")
            widget_key = display_options.get("widget_key")
            if not display_class and not widget_key:
                widget_key = 'view_panel'

            from tactic.ui.manager import WidgetClassSelectorWdg
            class_labels = ['Table with Search Layout', 'Custom Layout', 'Edit Layout', 'Tile Layout', '-- Class Path --']
            class_values = ['view_panel', 'custom_layout', 'edit_layout', 'tile_layout', '__class__']
            default_class='view_panel'
            class_selector = WidgetClassSelectorWdg(display_class=display_class,widget_key=widget_key,display_options=display_options,class_values=class_values,class_labels=class_labels, default_class=default_class, mode="layout")
            def_wdg.add(class_selector) 

        return def_wdg



    def get_simple_definition_wdg(self):

        detail_wdg = DivWdg()
        detail_wdg.add_class( "SPT_SIMPLE_DEFINITION_WDG" ) # DEPRECATED
        detail_wdg.add_class( "spt_simple_definition_top" )
        detail_wdg.add_style("margin-top: 10px")
        detail_wdg.add_style("padding: 10px")
        detail_wdg.add_border()
        detail_wdg.add_color("background", "background", -8)
        detail_wdg.add_color("color", "color")
        title = DivWdg()
        title.add_style("color", "color")
        title.add("Attributes")
        title.add_style("margin-top: -23px")
        detail_wdg.add(title)

        detail_wdg.add(HtmlElement.br())


        # add a title entry
        title_label = SpanWdg()
        title_label.add("Title: ")
        detail_wdg.add(title_label)
        input = TextInputWdg(name="config_title")
        input.set_id("config_title")
        input.add_style("width: auto")
        if self.title_string:
            input.set_value(self.title_string)
        detail_wdg.add(input)

        if self.is_new:
            input.add_behavior( {
            'type': 'change',
            'cbjs_action': '''
            var value = bvr.src_el.value;
            var top = bvr.src_el.getParent(".spt_simple_definition_top");
            var element = top.getElement(".spt_simple_definition_name");

            var new_value = element.value;
            if (new_value == "") {
                new_value = spt.convert_to_alpha_numeric(value);
                element.value = new_value;
            }
            '''
            } )


        detail_wdg.add(HtmlElement.br(2))


        # add a name entry
        name_label = SpanWdg()
        name_label.add("Name: ")
        detail_wdg.add(name_label)
        if self.is_new:
            input = TextWdg("config_element_name")
            input.add_class("spt_simple_definition_name")
            input.set_value(self.name_string)
            detail_wdg.add(input)
        else:
            input = HiddenWdg("config_element_name")
            input.set_value(self.name_string)
            detail_wdg.add(input)

            input = SpanWdg()
            input.add_style('padding-top: 6px')
            input.set_id("config_element_name")
            input.add(HtmlElement.b(self.name_string))
            detail_wdg.add(input)

        detail_wdg.add(HtmlElement.br(2))


        # add a icon entry
        icon_label = DivWdg()
        icon_label.add("<div style='margin-right: 10px'>Icon:</div>")

        icon_entry_text = TextInputWdg(name="config_icon")
        icon_entry_text.set_id("config_icon")
        icon_entry_text.set_option("size", "30")
        icon_entry_text.add_class( "SPT_ICON_ENTRY_TEXT" )
        icon_entry_text.add_color("color", "color3")
        icon_entry_text.add_color("background", "background3")

        #button = ActionButtonWdg(title='Choose',tip='Click to select an icon')
        #button.add_behavior({
        #    'type': 'click_up',
        #    'cbjs_action': 'spt.popup.open( "Icon Chooser", false);'
        #} )


        icon_img = HtmlElement.img()
        icon_img.add_class( "SPT_ICON_IMG" )

        if self.icon_string:
            icon_path = IconWdg.get_icon_path(self.icon_string)
            if icon_path:
                icon_img.set_attr("src", icon_path)
            else:
                icon_img.set_attr("src", IconWdg.get_icon_path("TRANSPARENT"))

            icon_entry_text.set_value( self.icon_string )
        else:
            icon_entry_text.set_value( "" )
            icon_img.set_attr("src", IconWdg.get_icon_path("TRANSPARENT"))

        named_event_name = "ICON_CHOOSER_SELECTION_MADE"
        icon_entry_text.add_behavior({
            'type': 'listen',
            'event_name': named_event_name,
            'cbjs_action': '''
            // like it or not, the chooser is global
            var top = document.id("IconChooserPopup");
            var chooser = spt.get_element(top, ".SPT_ICON_CHOOSER_WRAPPER_DIV");

            var icon_name = chooser.getProperty("spt_icon_selected");
            var icon_path = chooser.getProperty("spt_icon_path");
            // bvr.src_el.innerHTML = icon_name;
            bvr.src_el.value = icon_name;
            if( spt.is_hidden( bvr.src_el ) ) { spt.show( bvr.src_el ); }
            var img_el = spt.get_cousin( bvr.src_el, ".SPT_SIMPLE_DEFINITION_WDG",
                                          ".SPT_ICON_IMG" );
            if( icon_path ) {
                img_el.setProperty("src", icon_path);
            } else {
                img_el.setProperty("src","/context/icons/common/transparent_pixel.gif");
            }
           ''' } )

        icon_wdg = DivWdg()
        detail_wdg.add(icon_wdg)
        icon_wdg.add_style("display: flex")
        icon_wdg.add_style("align-items: center")
        icon_wdg.add_style("justify-content: flex-start")
        icon_wdg.add_style("width: 100%")
        icon_wdg.add(icon_label)
        icon_wdg.add(icon_img)
        icon_wdg.add(icon_entry_text)
        #icon_wdg.add(button)

        detail_wdg.add("<br/>")


        detail_wdg.add("Is Visible? ")
        checkbox = CheckboxWdg("config_visible")
        if self.visible_string != 'false':
            checkbox.set_checked()
        detail_wdg.add(checkbox)
        detail_wdg.add("<br/>"*2)



        if self.config:
            display_class = self.config.get_display_handler(self.element_name)
        else:
            display_class = ""

        if display_class in ["SideBarSectionLinkWdg", "FolderWdg"]:

            state_wdg = DivWdg()
            detail_wdg.add(state_wdg)
            title = DivWdg("Initial State:&nbsp;&nbsp;")
            title.add_style("float: left")
            state_wdg.add(title)
            select = SelectWdg("config_state")
            detail_wdg.add(select)
            if self.state_string:
                select.set_value(self.state_string)
            select.set_option("labels", "closed|open")
            select.set_option("values", "|open")

        return detail_wdg


    def get_advanced_definition_wdg(self):

        detail_wdg = DivWdg()

        # add the advanced entry
        advanced = DivWdg()
        advanced.add_style("margin-top: 10px")
        advanced.add_style("padding: 10px")
        advanced.add_border()
        title = DivWdg()
        title.add_color("color", "color")
        title.add("Advanced - XML Config Definition")
        title.add_style("margin-top: -23")
        advanced.add(title)


        input = TextAreaWdg("config_xml")
        input.set_id("config_xml")
        input.set_option("rows", "10")
        input.set_value(self.config_string)
        advanced.add(input)
        input.add_style("width: 100%")

        detail_wdg.add(advanced)

        return detail_wdg






    def get_security_wdg(self):
        project_code = Project.get_project_code()

        content = DivWdg()
        content.add_style('width','100%')

        group_wdg = DivWdg()
        group_wdg.add_border()
        group_wdg.add_style("padding: 10px")
        group_wdg.add_color("color", "color")
        group_wdg.add_color("background", "background")
        group_wdg.add_style("margin-top: 10px")

        title = DivWdg("Security Settings")
        title.add_style("margin-top: -23")
        group_wdg.add(title)

        search = Search("sthpw/login_group")
        groups = search.get_sobjects()

        div = DivWdg()
        head1 = FloatDivWdg('Group', width='300')
        head1.add_style('margin: 4px 0 0 4px')
        #head2 = FloatDivWdg('Group default', width='100')
        #head2.add_style('margin: 4px 0 0 -4px')

        div.add(HtmlElement.b(head1))
        #div.add(HtmlElement.b(head2))
        div.add('<br/>')
        group_wdg.add(div)

        from pyasm.security import AccessManager, get_security_version
        from tactic.ui.widget import LimitedTextWdg

        for group in groups:
            width = 300
            group_div = DivWdg()
            div.add(group_div)
            group_div.add_style("width: 300")
            group_div.add_style("margin: 10px 5px 10px 5px")

            login_group = group.get_value("login_group")
            if login_group == 'admin':
                continue

            access_rules = group.get_xml_value("access_rules")

            checkbox = CheckboxWdg("security")
            checkbox.set_option("value", login_group)
            group_div.add(checkbox)

            #xml = Xml()
            ##xml.read_string('''
            #<rules>
            #<rule group='side_bar' key='/Preproduction' access='allow'/>
            #</rules>
            #''')

            access_manager = AccessManager.get_by_group(group)
            security_version = get_security_version()

            if security_version == 1:
                default_access = "allow"
                # project specific key
                key = {'project': project_code, 'element': self.name_string}

                allowed = access_manager.check_access("side_bar", key , "view", default=default_access)
            else:
                default_access = "deny"
                # project specific key
                key = {'project': project_code, 'element': self.name_string}
                allowed = access_manager.check_access("link", key , "view", default=default_access)

            if allowed:
                checkbox.set_checked()
            login_group_span = LimitedTextWdg(text=login_group, length=40)
            group_div.add(login_group_span)



            """
            default_div = FloatDivWdg(css='spt_group_default hand')
            
            hidden = HiddenWdg('group_default_%s'%login_group)
            hidden.add_class('group_input')


            # add the rule to each group
            builder = AccessRuleBuilder(access_rules)
            default_attr = builder.get_default('side_bar')
            if not default_attr or default_attr =='view':
                default_attr = 'allow'

            hidden.set_value(default_attr)
            span = SpanWdg('%s all'%default_attr, css='default')
            if default_attr in ['allow','view']:
                span.add_style('color: #00268A')
            else:
                span.add_style('color: #7D0000')

            span.add_behavior({'type': 'click',
                'cbjs_action': '''var hidden = bvr.src_el.getParent('.spt_group_default').getElement('.group_input');
                
                if (hidden.value=='allow') {
                    hidden.value ='deny';
                    bvr.src_el.innerHTML = 'deny all';
                    bvr.src_el.setStyle('color', '#7D0000');
                    }
                else {
                    hidden.value='allow';
                    bvr.src_el.innerHTML = 'allow all';
                    bvr.src_el.setStyle('color', '#00268A');
                    }'''})
            default_div.add(span)
            default_div.add(hidden)
            
            div.add("<br/>")
            div.add(group_div)
            
            div.add(default_div)
            div.add("<br/>")
            """


        content.add(group_wdg)
        return content





class ManageSideBarDetailCbk(Command):

    def get_args_key(self):
        return {
        'search_type': 'search_type of the element',
        'element_name': 'name of the element to get information from',
        'login': 'login for config filtering. <user> for personal view'
        }

    def get_title(self):
        return "Side Bar Manager"

    def execute(self):

        web = WebContainer.get_web()
        if web.get_form_value("update") != "true":
            return

        self.element_name = self.kwargs.get("element_name")

        # Hard code definition view
        self.login = self.kwargs.get("login")
        if self.login == 'None' or not self.login:
            self.login = None

        # handle the definition
        self.handle_definition_config()

        # handle the view
        self.handle_view_config()

        self.description = 'Altered definition of [%s]' % self.element_name


    def handle_view_config(self):
        web = WebContainer.get_web()
        search_type = "SideBarWdg"

        view = self.kwargs.get("view")
        assert(view)
        #if not view:
        #    view = 'project_view'

        self.element_name = self.kwargs.get("element_name")

        search_type = self.kwargs.get("search_type")
        element_attrs = {}
        from pyasm.search import WidgetDbConfig
        WidgetDbConfig.append(search_type, view, self.element_name, element_attrs={}, login=self.login)


    def handle_definition_config(self):
        web = WebContainer.get_web()
        view = "definition"

        search_type = self.kwargs.get("search_type")
        config_search_type = "config/widget_config"
        search = Search(config_search_type)
        search.add_filter("search_type", search_type)
        search.add_filter("view", view)
        search.add_filter("login", self.login)
        config = search.get_sobject()
        if not config:
            config = SearchType.create(config_search_type)
            config.set_value("search_type", search_type )
            config.set_value("view", view )
            if self.login:
                 config.set_value("login", self.login )
            xml = config.get_xml_value("config", "config")
            root = xml.get_root_node()
            # reinitialize
            config._init()

            # build a new config
            view_node = xml.create_element(view)
            xml.append_child(root, view_node)

        config_mode = web.get_form_value("config_mode")
        if config_mode == "advanced":
            config_string = web.get_form_value("config_xml")
        else:
            config_title = web.get_form_value("config_title")
            config_icon = web.get_form_value("config_icon")
            config_icon2 = web.get_form_value("config_icon2")
            if config_icon2:
                config_icon = config_icon2
            config_state = web.get_form_value("config_state")
            config_visible = web.get_form_value("config_visible")
            if config_visible != 'on':
                config_visible = 'false'

            # TAKEN FROM API: should be centralized or something
            from tactic.ui.panel import SideBarBookmarkMenuWdg
            config_view = SideBarBookmarkMenuWdg.get_config(search_type, view)
            if not self.element_name:
                raise UserException('Element name is empty. You need to click on an element on the left first')
            element_node = config_view.get_element_node(self.element_name)

            config_xml = config_view.get_xml()
            if element_node == None:
                # create a new node
                element_node = config_xml.create_element("element")
                Xml.set_attribute(element_node, "name", self.element_name)

            Xml.set_attribute(element_node, "title", config_title)
            Xml.set_attribute(element_node, "icon", config_icon)
            Xml.set_attribute(element_node, "state", config_state)
            Xml.set_attribute(element_node, "is_visible", config_visible)

            # if a display class is defined, then put in the full definition
            widget_key = web.get_form_value("xxx_option|widget_key")
            display_class = web.get_form_value("xxx_option|display_class")

            if display_class or widget_key:
                # get the old display node
                old_display_node = None
                children = Xml.get_children(element_node)
                for child in children:
                    if Xml.get_node_name(child) == 'display':
                        old_display_node = child
                        break

                # create a new one
                display_node = config_xml.create_element("display")
                Xml.set_attribute(display_node, "class", "LinkWdg")

                if old_display_node == None:
                    config_xml.append_child(element_node, display_node)
                else:
                    config_xml.replace_child(element_node, old_display_node, display_node)


                if widget_key and widget_key != '__class__':
                    option_node = config_xml.create_text_element("widget_key", widget_key)
                else:
                    option_node = config_xml.create_text_element("class_name", display_class)
                config_xml.append_child(display_node, option_node)

                # get all of the options
                keys = web.get_form_keys()
                options = {}
                for key in keys:
                    if key.startswith("option|"):
                        parts = key.split("|")
                        name = parts[1]

                        # HACK: skip the class names
                        if name in ['widget_key', 'class_name', 'display_class']:
                            continue

                        value = web.get_form_value(key)
                        if value != '':
                            options[name] = web.get_form_value(key)


                for name, value in options.items():
                    option_node = config_xml.create_text_element(name, value)
                    config_xml.append_child(display_node, option_node)


            config_string = config_xml.to_string(element_node)


        if not config_string:
            raise UserException('Xml config definition is empty. You need to click on an element first on the left')

        try:
            xml = Xml()
            xml.read_string(config_string)
            new_root_node = xml.get_root_node()
            xpath = "element[@name='%s']" % (self.element_name)
            node = xml.get_node(xpath)
            if node is None:
                raise UserException('There is a mismatch in the element name of the XML you have entered. You are changing the element [%s] but it is not found in the XML.' %self.element_name)
        except XmlException as e:
            raise XmlException("Improper syntax in XML: %s"%e.__str__())
        

        config.append_xml_element(self.element_name, config_string)
        config.commit_config()





    def get_options(self):
        # use this as a utility
        from tactic.ui.manager import SimpleElementDefinitionCbk
        cbk = SimpleElementDefinitionCbk()

        options = cbk.get_options("option")

        for name, value in options.items():
            option_node = element_xml.create_text_element(name, value)
            element_xml.append_child(display_node, option_node)











class ManageSideBarSecurityCbk(Command):

    def get_args_key(self):
        return {
        'search_type': 'search_type of the element',
        'element_name': 'name of the element to get information from',
        }

    def get_title(self):
        return "Side Bar Security Callback"
    
    def execute(self):


        web = WebContainer.get_web()
        if web.get_form_value("update") != "true":
            return

        self.element_name = self.kwargs.get("element_name")
        project_code = Project.get_project_code()

        security_groups = web.get_form_values("security")


        from pyasm.security import AccessRuleBuilder, get_security_version


        version = get_security_version()


        # get all of the groups
        search = Search("sthpw/login_group")
        login_groups = search.get_sobjects()


        if version == 1:
            key = {'project': project_code, 'element': self.element_name}

            rule_group = "side_bar"
            for login_group in login_groups:

                code = login_group.get_value("login_group")
                access_rules = login_group.get_xml_value("access_rules")

                group_default = web.get_form_value('group_default_%s'%code)

                builder = AccessRuleBuilder(access_rules)

                # add the rule to each group
                # DEPRECATED
                #####
                if group_default in ['allow','deny']:
                    builder.add_default_rule(rule_group, group_default)
                #####


                default_attr = builder.get_default(rule_group)
                if code in security_groups:
                    if default_attr == 'deny':
                        builder.add_rule(rule_group, key, "allow")
                    else:
                        builder.remove_rule(rule_group, key)
                else:
                    if default_attr == 'deny':
                        builder.remove_rule(rule_group, key)
                    else:
                        builder.add_rule(rule_group, key, "deny")

                login_group.set_value("access_rules", builder.to_string())
                login_group.commit()

        elif version == 2:

            rule_group = "link"

            key = {'project': project_code, 'element': self.element_name}

            for login_group in login_groups:
                code = login_group.get_value("login_group")
                access_rules = login_group.get_xml_value("access_rules")
                
                if code not in security_groups:
                    # remove the entry
                    builder = AccessRuleBuilder(access_rules)
                    builder.remove_rule(rule_group, key)
                    login_group.set_value("access_rules", builder.to_string())
                    login_group.commit()
                    continue


                builder = AccessRuleBuilder(access_rules)
                builder.remove_rule(rule_group, key)
                builder.add_rule(rule_group, key, "allow")

                login_group.set_value("access_rules", builder.to_string())
                login_group.commit()




