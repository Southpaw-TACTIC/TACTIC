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
__all__ = ["ViewManagerWdg", 'ManageViewNewItemWdg']

import os, types
import math

from pyasm.common import Xml, Environment, Common
from pyasm.command import Command
from pyasm.search import Search, SearchType, SObject
from pyasm.biz import Project
from pyasm.web import DivWdg, HtmlElement, SpanWdg, Table, WebContainer, Widget
from pyasm.widget import SelectWdg, WidgetConfig, IconWdg, CheckboxWdg, HiddenWdg
from pyasm.widget import TextAreaWdg, TextWdg, ButtonWdg, ProdIconButtonWdg, HintWdg, WidgetConfigView

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.activator import ButtonForDropdownMenuWdg
from tactic.ui.widget import SearchTypeSelectWdg, TextBtnWdg, TextBtnSetWdg, IconChooserWdg, ActionButtonWdg
from tactic.ui.container import HorizLayoutWdg, PopupWdg, RoundedCornerDivWdg


# TODO: move this to ../manager ... if it is not already done

class ViewManagerWdg(BaseRefreshWdg):
    '''Panel to manage views ... this is mean to be a generic interface for
    manipulating the side bar views'''

    def get_args_keys(my):
        return {
        'search_type': 'search type of the view',
        'view': 'view to be edited'
        }


    def init(my):
        my.search_type = my.kwargs.get('search_type')
        my.view = my.kwargs.get('view')

        web = WebContainer.get_web()
        if not my.search_type:
            my.search_type = web.get_form_value('search_type')
        if not my.view:
            my.view = web.get_form_value('view')

        if not my.view:
            my.view = 'table'

        my.refresh = web.get_form_value('is_refresh')=='true'



    def get_display(my):
        div = DivWdg()
        div.add_class( "spt_view_manager_top" )
        my.set_as_panel(div)

        if not my.search_type or not my.view:
            return div



        div.add( my.get_action_wdg() )

        div.add(HtmlElement.br(2))

        tool_bar = my.get_tool_bar()
        div.add(tool_bar)
 
        div.add(HtmlElement.br())


        # add the template view containing the possible items to be added
        # ie: New Folder, New Entry, New Separator
        menu_div = DivWdg()
        menu_div.set_id("menu_item_template")
        menu_div.add_style("display: none")
        menu_div.add( my.get_section_wdg("_template", editable=False) )
        div.add(menu_div)


        table = Table()
        table.add_row()

        # add the section
        td = table.add_cell()
        project_view = DivWdg()
        project_view.set_id("menu_item_list")
        project_view.add( my.get_section_wdg(my.view ))
        td.add(project_view)
        td.add_style("vertical-align: top")
        #td.add_attr("rowspan", "2")

        tool_bar = my.get_tool_bar()
        td.add(tool_bar)

        td.add("<br/>")

        # add detail information
        td = table.add_cell( my.get_detail_wdg() )


        # FIXME: get rid of hard coded classes
        # set the panel information
        td.set_id("manage_side_bar_detail")
        td.add_class("spt_view_manager_detail")
        td.add_style("display", "table-cell")
        td.add_attr("spt_class_name", "tactic.ui.panel.ManageSideBarDetailWdg")
        td.add_attr("spt_search_type", my.search_type)

        td.add_style("padding: 0 20px 20px 20px")
        td.add_style("vertical-align: top")


        div.add(table)
        return div



    def get_tool_bar(my):
        widget = Widget()
        trash_div = SpanWdg()
        # reset some global variables on load
        trash_div.add_behavior({'type':'load', 'cbjs_action':'spt.side_bar.trashed_items=[]; spt.side_bar.changed_views={}'})

        trash_div.set_id('trash_me')

        trash_div.add(IconWdg('Trash', IconWdg.TRASH))
        trash_div.add("TRASH!")
        trash_div.add_class("hand")
        trash_div.add_class("spt_side_bar_trash")
      
        trash_div.set_attr("SPT_ACCEPT_DROP", "manageSideBar")
        bvr = { "type": "click_up",\
                'cbjs_action': "alert('Drag and drop link or folder here to remove it.')"}
        trash_div.add_behavior(bvr)

        widget.add(trash_div)
        
        save_div = SpanWdg(css='med hand spt_side_bar_trash')
        save_div.add(IconWdg('Save Ordering', IconWdg.SAVE))
      
        # FIXME: is_personal???
        is_personal = 'false'
        bvr = { "type": "click_up",\
                'cbjs_action': "spt.side_bar.manage_section_action_cbk({'value':'save'},'%s',%s);" % (my.view, is_personal)} 
        save_div.add_behavior(bvr)
        widget.add(save_div)
        return widget




    def get_detail_wdg(my):
        return "<<-- Click on a link for the detail to appear"



    def get_menu_item(my, element_name, display_handler):

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


    def get_action_menu_details(my):
        '''method to override the details of the action menu'''
        return {
            'menu_id': 'ManageViewPanelWdg_DropdownMenu',
            'width': 250,
            'allow_icons': False,
            'opt_spec_list': [
                { "type": "action", "label": "Test",
                    "bvr_cb": {'cbjs_action': "alert('test')" }
                }
            ]
        }


    def get_action_wdg(my):
        div = DivWdg()
        menus = [ my.get_action_menu_details() ]
        dd_activator = ButtonForDropdownMenuWdg( id="SideBarManagerActionDropDown", title="-- Action --", menus=menus,
                                                 width=150, match_width=True)
        div.add( dd_activator )

        return div




    def get_section_wdg(my, view, editable=True, default=False):
        from panel_wdg import SideBarBookmarkMenuWdg

        title = ""
        target_id = "sobject_relation"
        if editable:
            edit_mode = 'edit'
        else:
            edit_mode = 'read'
        kwargs = {
            'title': title,
            'config_search_type': my.search_type,
            'view': view,
            'target_id': target_id,
            'width': '300',
            'prefix': 'manage_side_bar',
            'mode': edit_mode,
            'default': str(default)
        }
        if view in ["definition", "custom_definition"]:
            kwargs['recurse'] = "false"
            kwargs['sortable'] = "true"

        section_wdg = SectionListWdg(**kwargs)
        class_path = Common.get_full_class_name(section_wdg)

        # FIXME: get rid of this id
        id = "ManageSideBarBookmark_" + view
        section_div = DivWdg(id=id)
        section_div.add_style("display: block")
        section_div.set_attr('spt_class_name', class_path)
        for name, value in kwargs.items():
            if name == "config":
                continue
            section_div.set_attr("spt_%s" % name, value)

        section_div.add(section_wdg)
        return section_div




from panel_wdg import SideBarBookmarkMenuWdg
class SectionListWdg(SideBarBookmarkMenuWdg):

    def get_config(cls, config_search_type, view,  default=False, personal=False):
        config = WidgetConfigView.get_by_search_type(config_search_type, view)

        return config


    def get_detail_class_name(my):
        return "tactic.ui.panel.element_definition_wdg.ElementDefinitionWdg"

    #
    # behavior functions
    #
    def add_separator_behavior(my, separator_wdg, element_name, config, options):
        if my.mode == 'edit':
            # add the drag/drop behavior
            behavior = {
                "type": 'drag',
                "drag_el": 'drag_ghost_copy',
                "drop_code": 'manageSideBar',
                "cb_set_prefix": 'spt.side_bar.pp',
            }
            separator_wdg.add_behavior(behavior)
            separator_wdg.set_attr("SPT_ACCEPT_DROP", "manageSideBar")



    def add_folder_behavior(my, folder_wdg, element_name, config, options):
        '''this method provides the changed to add behaviors to a folder'''

        # determines whether the folder opens on click
        recurse = my.kwargs.get("recurse")!= "false"

        # edit behavior
        edit_allowed = True
        if my.mode == 'edit' and edit_allowed:
            # IS EDITABLE ...

            # add the drag/drop behavior
            behavior = {
                "type": 'drag',
                "drag_el": 'drag_ghost_copy',
                "drop_code": 'manageSideBar',
                "cb_set_prefix": 'spt.side_bar.pp'
            }
            if recurse:
                behavior['cbjs_action_onnomotion'] = 'spt.side_bar.toggle_section_display_cbk(evt,bvr); ' \
                                                     'spt.side_bar.display_element_info_cbk(evt,bvr);'
            else:
                behavior['cbjs_action_onnomotion'] = 'spt.side_bar.display_element_info_cbk(evt,bvr);'
            behavior['class_name'] = my.get_detail_class_name()
           
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



    def add_link_behavior(my, link_wdg, element_name, config, options):
        '''this method provides the changed to add behaviors to a link'''

        # check security
        #default_access = "view"
        #security = Environment.get_security()
        #if not security.check_access("side_bar", element_name, "edit", default=default_access):
        #    return

        # make it draggable
        
        edit_allowed = True
        if my.mode == 'edit' and edit_allowed:
                # add the drag/drop behavior
            behavior = {
                "type": 'drag',
                "drag_el": 'drag_ghost_copy',
                "drop_code": 'manageSideBar',
                "cb_set_prefix": 'spt.side_bar.pp',
                'cbjs_action_onnomotion':  'spt.side_bar.display_element_info_cbk(evt,bvr);',
                'class_name':   my.get_detail_class_name()
            }
           
                
            link_wdg.add_behavior(behavior)

            link_wdg.set_attr("SPT_ACCEPT_DROP", "manageSideBar")
        
        




class NewLinkViewSelectWdg(BaseRefreshWdg):
    '''A widget for the view select when creating a new link'''            
    def init(my):
        web = WebContainer.get_web()
        my.search_type = web.get_form_value('search_type')
        my.refresh = web.get_form_value('is_refresh')=='true'

    def get_display(my):
        widget = DivWdg(id='link_view_select')
        widget.add_class("link_view_select")
        if my.refresh:
            widget = Widget()
        else:
            my.set_as_panel(widget)
        
        views = []
        if my.search_type:
            from pyasm.search import WidgetDbConfig
            search = Search( WidgetDbConfig.SEARCH_TYPE )
            search.add_filter("search_type", my.search_type)
            search.add_regex_filter("view", "link_search:|saved_search:", op="NEQI")
            search.add_order_by('view')
            widget_dbs = search.get_sobjects()
            views = SObject.get_values(widget_dbs, 'view')
        
        labels = [view for view in views]

        views.insert(0, 'table')
        labels.insert(0, 'table (Default)')
        st_select = SelectWdg('new_link_view', label='View: ')
        st_select.set_option('values', views)
        st_select.set_option('labels', labels)
        widget.add(st_select)
        return widget

class ManageViewNewItemWdg(BaseRefreshWdg):

    def init(my):
        my.type = my.kwargs.get('type')
        my.view = my.kwargs.get('view')
        my.is_personal = False
        if 'my_view' in my.view:
            my.is_personal = True

    def get_display(my):
        widget = DivWdg(id='new_item_panel')
        widget.add_class("new_item_panel")
        widget.add_class("spt_new_item_top")

        div = DivWdg()
        div.add_color("background", "background")
        div.add_color("color", "color")
        div.add_style("padding", "5px")
        div.add_border()

        if my.is_personal:
            is_personal = 'true'
        else:
            is_personal = 'false'

        if my.type == 'new_folder':
            #div.set_attr('spt_view', 'new_folder')
            div.add(HtmlElement.b('Create New Folder'))
            div.add(HtmlElement.br(2))
            """
            # add exisiting views in the div for checking with client's input
             # add exiting views:
            from panel_wdg import ViewPanelSaveWdg
            views = ViewPanelSaveWdg.get_existing_views(my.is_personal)
            hidden = HiddenWdg('existing_views', '|'.join(views))
            div.add(hidden)
            """
            text2 = TextWdg("new_title")
            text2.add_class("spt_new_item_title")
            span = SpanWdg("Title: ")
            span.set_id('create_new_title')
            #span.add_style('display: none')
            span.add_style('padding-left: 8px')
            span.add(text2)
            div.add(span)
            div.add(HtmlElement.br(2))

            div.add_style("width: 350px")


            action = '''
            var top = bvr.src_el.getParent(".spt_new_item_top");
            var name_el = top.getElement(".spt_new_item_name");
            var title = bvr.src_el.value;
            var name = title.replace(/[\?.!@#$%^&*()'"]/g, "");
            name = name.replace(/ /g, "_");
            name = name.toLowerCase();
            name_el.value = name;
            '''


            # change the name based on the title
            text2.add_behavior( {
            'type': 'change',
            'cbjs_action': action
            } )

            div.add("The name of the folder is a hidden name that is used by other elements to refer to uniquely to this item.<br/><br/>")
            text = TextWdg('new_name')
            text.add_class("spt_new_item_name")
            span = SpanWdg('Name: ')
            span.add(text)
            div.add(span)

            div.add(HtmlElement.br(2))
            
            #script = "spt.side_bar.manage_section_action_cbk({'value':'predefined'},'project_view');"
            #link = HtmlElement.js_href(script, data='[ Predefined View ]')
            #div3 = DivWdg('Optional: drag existing elements from Project Views or %s into this new folder' %link.get_buffer_display())
            #div.add(div3)
            #item_div = DivWdg(css='spt_new_item spt_side_bar_content')
            #div.add(item_div)

            div.add("<hr/>")

           
            #save_div = SpanWdg(css='med hand')
            #div.add(save_div)
            #save_div.add(IconWdg('Save Folder', IconWdg.SAVE))

            save_button = ActionButtonWdg(title='Create', tip='Create a new folder')
            div.add(save_button)
       
            bvr = {
            "type": "click_up",
            "view": my.view,
            "is_personal": is_personal == 'true',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_new_item_top");
            var name_el = top.getElement(".spt_new_item_name");
            var name_value = name_el.value;
            if (name_value == "") {
                var title_el = top.getElement(".spt_new_item_title");
                var title = title_el.value;
                var name = spt.convert_to_alpha_numeric(title);
                name_el.value = name;
            }
            if (name_value == "") {
                spt.alert("Please fill in a value for name.");
                return;
            }
            spt.side_bar.manage_section_action_cbk(
                    { 'value':'save_folder'}, bvr.view, bvr.is_personal);
            ''' }
            save_button.add_behavior(bvr)
            div.add(HtmlElement.br())


        elif my.type == 'new_link':

            div.set_attr('spt_view', 'new_link')
            div.add(HtmlElement.b('Create New Link'))
            div.add(HtmlElement.br())
         
            item_div = DivWdg(css='spt_new_item')
            item_div.add_style('display: none')
            div.add(HtmlElement.br())
            div.add(item_div)
            
            text = TextWdg('new_link_title')
            span = SpanWdg('Title: ')
            span.add(text)
            div.add(span)
            
            div.add(HtmlElement.br(2))
            cb = CheckboxWdg('include_search_view', label='Include Saved Search')
            cb.set_default_checked()
            div.add(cb)

            div.add(HtmlElement.br(2))
            div.add("Select a search type and view of this link")
            div.add(HtmlElement.br())

           
            select = SelectWdg("new_search_type")
            select.add_empty_option("-- Select Search type --")
    
            security = Environment.get_security()
            if security.check_access("builtin", "view_site_admin", "allow"):
                search_types = Project.get().get_search_types(include_sthpw=True, include_config=True)
            else:
                search_types = Project.get().get_search_types()

            values = [x.get_value("search_type") for x in search_types]
            labels = ["%s (%s)" % (x.get_value("search_type"), x.get_title()) for x in search_types]
            values.append("CustomLayoutWdg")
            labels.append("CustomLayoutWdg")
            select.set_option("values", values)
            select.set_option("labels", labels)

    
            #security = Environment.get_security()
            #if security.check_access("builtin", "view_site_admin", "allow"):
            #    select_mode =  SearchTypeSelectWdg.ALL
            #else:
            #    select_mode =  SearchTypeSelectWdg.ALL_BUT_STHPW
            #select = SearchTypeSelectWdg(name='new_search_type', \
            #    mode=select_mode)

            select.add_behavior({'type': 'change',
            'cbjs_action': '''
                var top = bvr.src_el.getParent(".new_item_panel");
                var link_view_select = top.getElement(".link_view_select");
                var input = spt.api.Utility.get_input(top, 'new_search_type'); var values = {'search_type': input.value, 
                'is_refresh': 'true'}; 
                spt.panel.refresh(link_view_select, values);'''
            })
            div.add(HtmlElement.br())
            div.add(select)
      

            div.add(HtmlElement.br())
                  
            
            
            link_view_sel = NewLinkViewSelectWdg()
            div.add(HtmlElement.br())
            div.add(link_view_sel)

            div.add(HtmlElement.br())
            #select.add_behavior('change')
            div.add(HtmlElement.hr())
            div.add(HtmlElement.br())
            
            #save_div = DivWdg(css='med hand')
            #div.add(save_div)
            #save_button = ProdIconButtonWdg('Save Link', IconWdg.SAVE)
            #save_div.add(save_button)

            save_button = ActionButtonWdg(title='Create', tip='Create a new link')
            div.add(save_button)
            bvr = { "type": "click_up",
                'cbjs_action': "spt.side_bar.manage_section_action_cbk({"\
                "'value':'save_link'},'%s', %s);" %(my.view, is_personal)}
            save_button.add_behavior(bvr)
            div.add(HtmlElement.br(1))

        elif my.type == 'new_separator':
            div.set_attr('spt_view', 'new_separator')
            div.add(HtmlElement.b('Creating New Separator. . .'))
            div.add(HtmlElement.br())
           
            item_div = DivWdg(css='spt_new_item')
            item_div.add_style('display: none')
            div.add(HtmlElement.br())
            div.add(item_div)
            # since it's automated, this button is not needed
            """ 
            save_div = SpanWdg(css='med hand')
            save_div.add(IconWdg('Save', IconWdg.SAVE))
        
            bvr = { "type": "click_up",\
                'cbjs_action': "spt.side_bar.manage_section_action_cbk({"\
                "'value':'save_separator'},'%s');" %my.view}
            save_div.add_behavior(bvr)
            div.add(save_div)
            """
        widget.add(div)
        return widget

class ManageSideBarDetailCbk(Command):

    def get_args_key(my):
        return {
        'search_type': 'search_type of the element',
        'element_name': 'name of the element to get information from',
        'view': 'a view it is changing. it could be any view including the definition view',
        'login': 'login for config filtering. <user> for personal view'
        }

    def get_title(my):
        return "ManageSideBarDetailCbk in View Manager"

    def execute(my):

        web = WebContainer.get_web()
        if web.get_form_value("update") != "true":
            return

        my.element_name = my.kwargs.get("element_name")
        #my.view = my.kwargs.get("view")
        my.view = "definition"
        my.login = my.kwargs.get("login")
        if my.login == 'None' or not my.login:
            my.login = None
        my.handle_config()


    def handle_config(my):
        web = WebContainer.get_web()

        search_type = my.kwargs.get("search_type")
        view = my.view
        config_search_type = "config/widget_config"
        
        search = Search(config_search_type)
        search.add_filter("search_type", search_type)
        search.add_filter("view", view)
        search.add_filter("login", my.login)
        config = search.get_sobject()
        if not config:
            config = SearchType.create(config_search_type)
            config.set_value("search_type", search_type )
            config.set_value("view", view )
            if my.login:
                 config.set_value("login", my.login )
            xml = config.get_xml_value("config", "config")
            root = xml.get_root_node()
            # reinitialize
            config._init()

            # build a new config
            view_node = xml.create_element(view)
            root.appendChild(view_node)

        config_mode = web.get_form_value("config_mode")
        if config_mode == "advanced":
            config_string = web.get_form_value("config_xml")
        else:
            config_title = web.get_form_value("config_title")
            config_icon = web.get_form_value("config_icon")
            config_icon2 = web.get_form_value("config_icon2")
            if config_icon2:
                config_icon = config_icon2

            # TAKEN FROM API: should be centralized or something
            from tactic.ui.panel import SideBarBookmarkMenuWdg
            config_view = SideBarBookmarkMenuWdg.get_config(search_type, view)
            node = config_view.get_element_node(my.element_name)
            if node:
                config_xml = config_view.get_xml()

                node = config_view.get_element_node(my.element_name)
                Xml.set_attribute(node, "title", config_title)
                Xml.set_attribute(node, "icon", config_icon)

                config_string = config_xml.to_string(node)
            else:
                config_string = '''
                <element name="%s" title="%s" icon="%s"/>
                ''' %(my.element_name, config_title, config_icon)

        config.append_xml_element(my.element_name, config_string)
        config.commit_config()



class ManageSideBarSecurityCbk(Command):

    def get_args_key(my):
        return {
        'search_type': 'search_type of the element',
        'element_name': 'name of the element to get information from',
        }


    def execute(my):

        web = WebContainer.get_web()
        if web.get_form_value("update") != "true":
            return

        my.element_name = my.kwargs.get("element_name")

        security_groups = web.get_form_values("security")
        from pyasm.security import AccessRuleBuilder, AccessManager

        rule_group = "side_bar"

        # get all of the groups
        search = Search("sthpw/login_group")
        login_groups = search.get_sobjects()

        for login_group in login_groups:

            access_rules = login_group.get_xml_value("access_rules")

            # add the rule to each group
            builder = AccessRuleBuilder(access_rules)

            code = login_group.get_value("login_group")
            if code in security_groups:
                builder.remove_rule(rule_group, my.element_name)
            else:
                builder.add_rule(rule_group, my.element_name, "deny")

            login_group.set_value("access_rules", builder.to_string())
            login_group.commit()






