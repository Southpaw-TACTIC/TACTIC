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
__all__ = ["ViewManagerWdg"]

import os, types
import math

from pyasm.common import Xml, Environment, Common
from pyasm.command import Command
from pyasm.search import Search, SearchType, SObject, SearchException
from pyasm.biz import Project
from pyasm.web import DivWdg, HtmlElement, SpanWdg, Table, WebContainer, Widget
from pyasm.widget import SelectWdg, WidgetConfig, IconWdg, CheckboxWdg, HiddenWdg
from pyasm.widget import TextAreaWdg, TextWdg, ButtonWdg, ProdIconButtonWdg, HintWdg, WidgetConfigView, IconButtonWdg

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.activator import ButtonForDropdownMenuWdg
from tactic.ui.widget import SearchTypeSelectWdg, TextBtnWdg, TextBtnSetWdg, IconChooserWdg
from tactic.ui.container import HorizLayoutWdg, PopupWdg
from tactic.ui.widget import ActionButtonWdg


class ViewManagerWdg(BaseRefreshWdg):
    '''Panel to manage views ... this is mean to be a generic interface for
    manipulating the side bar views'''

    def get_args_keys(my):
        return {
        'search_type': 'search type of the view',
        'view': 'view to be edited'
        }


    def init(my):
        web = WebContainer.get_web()
        my.search_type = web.get_form_value('search_type')
        my.kwargs_search_type = my.kwargs.get('search_type')

        my.view = web.get_form_value('view')

        if not my.search_type:
            my.search_type = my.kwargs.get('search_type')
        else:
            my.kwargs['search_type'] = my.search_type

        if my.search_type != my.kwargs_search_type:
            my.view = ''
        elif not my.view:
            my.view = my.kwargs.get('view')
        else:
            my.kwargs['view'] = my.view

        if not my.view:
            my.view = 'table'

        my.refresh = web.get_form_value('is_refresh')=='true'



    def get_display(my):
        div = DivWdg()
        div.add_class( "spt_view_manager_top" )
        my.set_as_panel(div)

        inner = DivWdg()
        div.add(inner)
        inner.add_color("background", "background")
        inner.add_color("color", "color")
        inner.add_border()
        inner.add_style("padding: 10px")


        # try to get the search objct
        try:
            search_type_sobj = SearchType.get(my.search_type)
        except SearchException:
            if my.kwargs.get("show_create") in [True, 'true']:
                inner.add("<b>Create New Search Type</b><br/><br/>")
                inner.add("Search Type [%s] does not yet exist.<br/>Fill out the following form to register this Search Type.<br/>" % my.search_type)
                from tactic.ui.app import SearchTypeCreatorWdg
                creator = SearchTypeCreatorWdg(search_type=my.search_type)
                inner.add(creator)
                return div


        #title_wdg = DivWdg()
        #title_wdg.add_style("font-size: 18px")
        #title_wdg.add("Config View Manager")
        #inner.add(title_wdg)

        inner.add (my.get_filter_wdg() )


        if not my.search_type or not my.view:
            return div

        inner.add(HtmlElement.br())

        tool_bar = my.get_tool_bar()
 
        inner.add(tool_bar)


        # add the template view containing the possible items to be added
        # ie: New Folder, New Entry, New Separator
        menu_div = DivWdg()
        inner.add(menu_div)
        menu_div.add_class("spt_menu_item_template")
        menu_div.add_style("display: none")
        menu_div.add( my.get_section_wdg("_template", editable=False) )


        table = Table()
        inner.add(table)
        table.add_row()
        table.add_color("color", "color")

        # add the section
        td = table.add_cell()
        view_list_wdg = DivWdg()
        view_list_wdg.add_style('min-width: 250px')
        view_list_wdg.add_class("spt_menu_item_list")
        view_list_wdg.add( my.get_section_wdg(my.view ))
        td.add(view_list_wdg)
        td.add_style("vertical-align: top")
        #td.add_attr("rowspan", "2")

        td.add("<br/>")

        # add the definition section
        if my.view != 'definition':
            def_list_wdg = DivWdg()
            #def_list_wdg.add( my.get_section_wdg("default_definition" ))
            def_list_wdg.add( my.get_section_wdg("definition" ))
            td.add(def_list_wdg)
 
            td.add("<br/>")

            # HACK: we need to figure out how this default definition
            # fits in
            if my.search_type.startswith('prod/') or my.search_type.startswith('sthpw/'):
                def_list_wdg = DivWdg()
                def_list_wdg.add( my.get_section_wdg("default_definition" ))
                td.add(def_list_wdg)
                td.add("<br/>")

        # add detail information
        td = table.add_cell( my.get_detail_wdg() )


        # set the panel information
        td.add_class("spt_view_manager_detail")
        td.add_style("display", "table-cell")
        td.add_attr("spt_search_type", my.search_type)

        td.add_style("padding: 0 20px 20px 20px")
        td.add_style("vertical-align: top")


        return div


    def get_filter_wdg(my):

        div = DivWdg()
        div.add_style("padding: 10px")
        div.add_style("margin: -10 -10 10 -10")
        div.add_style("min-width: 600px")
        div.add_class("spt_view_manager_filter")



        from tactic.ui.app import HelpButtonWdg
        help_wdg = HelpButtonWdg(alias="view-manager|what-are-views")
        div.add(help_wdg)
        help_wdg.add_style("float: right")





        div.add('<b>Search Type:</b> ')

        div.add_gradient("background", "background", -10)


        security = Environment.get_security()
        project = Project.get()
        if security.check_access("builtin", "view_site_admin", "allow"):
            search_type_objs = project.get_search_types(include_sthpw=True, include_config=True)
        else:
            search_type_objs = project.get_search_types()

        search_types = [x.get_value("search_type") for x in search_type_objs]
        titles = ["%s (%s)" % (x.get_value("search_type"), x.get_value("title")) for x in search_type_objs]


        select = SelectWdg(name='search_type')
        select.set_option('values', search_types)
        select.set_option('labels', titles)
        select.add_empty_option('-- Select --')
        select.set_persistence()
        #select.set_persist_on_submit()


        #security = Environment.get_security()
        #if security.check_access("builtin", "view_site_admin", "allow"):
        #    select_mode =  SearchTypeSelectWdg.ALL
        #else:
        #    select_mode =  SearchTypeSelectWdg.ALL_BUT_STHPW
        #select = SearchTypeSelectWdg(name='search_type', \
        #    mode=select_mode)

        behavior = {'type': 'change', 'cbjs_action': '''
            var manager_top = bvr.src_el.getParent(".spt_view_manager_top");

            var input = spt.api.Utility.get_input(manager_top, 'search_type');
            var view_input = spt.api.Utility.get_input(manager_top, 'view');
            var view_input_value = '';
            if (view_input != null) {
                view_input_value = view_input.value;
            }
            var values = {'search_type': input.value, 'view': view_input_value, 'is_refresh': 'true'}; 
            spt.panel.refresh(manager_top, values);'''
            #//spt.panel.refresh(manager_top, values);'''
        }
        select.add_behavior(behavior)
        select.set_value(my.search_type)
        div.add(select)

        if not my.search_type:
            content = DivWdg()
            content.add_style("width: 400px")
            content.add_style("height: 400px")
            div.add(content)
            content.add_style("padding: 20px")
            content.add( IconWdg("WARNING", IconWdg.WARNING) )
            content.add("No Search Type Selected")
            content.add_border()
            content.add_style("margin-top: 20px")
            content.add_color("background", "background")
            content.add_style("font-weight: bold")

            return div

        div.add('&nbsp;&nbsp;&nbsp;')
        div.add('<b>View: </b>')
        view_wdg = SelectWdg("view")
        view_wdg.set_value(my.view)
        view_wdg.add_empty_option("-- Select --")
        view_wdg.add_behavior(behavior)
        div.add(view_wdg)


        search = Search("config/widget_config")
        search.add_filter("search_type", my.search_type)
        db_configs = search.get_sobjects()


        views = set()
        for db_config in db_configs:
            view = db_config.get_value("view")
            if view.startswith('link_search:'):
                continue
            views.update([view])

        #print("search_type: ", my.search_type)
        #print("view: ", views, my.view)

        if my.search_type and my.view:
            config_view = WidgetConfigView.get_by_search_type(my.search_type, my.view)

            configs = config_view.get_configs()
            for x in configs:
                view = x.get_view()
                file_path = x.get_file_path()
                if view != my.view:
                    continue
                if file_path and file_path.endswith("DEFAULT-conf.xml"):
                    continue
                config_views = x.get_all_views()
                views.update(config_views)

        views_list = list(views)
        views_list.sort()
        view_wdg.set_option("values", views_list)


        return div





    def get_tool_bar(my):
        widget = DivWdg()
        widget.add_style("width: 250px")


        refresh = IconButtonWdg("Refresh", IconWdg.REFRESH)
        refresh.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_panel");
            spt.panel.refresh(top);
            '''
        } )



        widget.add( refresh )
        widget.add("&nbsp;&nbsp;&nbsp;")

        trash_div = SpanWdg()
        # reset some global variables on load
        trash_div.add_behavior({'type':'load', 'cbjs_action':'spt.side_bar.trashed_items=[]; spt.side_bar.changed_views={}'})

        trash_div.set_id('trash_me')

        trash_div.add(IconWdg('Trash', IconWdg.TRASH))
        trash_div.add_class("hand")
        trash_div.add_class("spt_side_bar_trash")
      
        trash_div.set_attr("SPT_ACCEPT_DROP", "manageSideBar")
        bvr = { "type": "click_up",\
                'cbjs_action': "alert('Drag and drop link or folder here to remove it.')"}
        trash_div.add_behavior(bvr)

        widget.add(trash_div)
        
        save_div = SpanWdg(css='med hand spt_side_bar_trash')
        save_div.add(IconWdg('Save Ordering', IconWdg.SAVE))
      
        bvr = {
            "type": "click_up",
            "search_type": my.search_type,
            "view": my.view,
            'cbjs_action': '''
            if (confirm("Save ordering of this view [" + bvr.view + "] ?") ) {

                var top = bvr.src_el.getParent(".spt_view_manager_top");
                var list_top = top.getElement(".spt_menu_item_list");

                var server = TacticServerStub.get();
                server.start({"title": "Updating views"});

                var is_personal = false;
                spt.app_busy.show("Saving", "Saving view ["+bvr.view+"]");
                spt.side_bar.save_view(bvr.search_type, bvr.view, is_personal, list_top);
                server.finish();

                spt.app_busy.hide();
            }
            '''
        }



        save_div.add_behavior(bvr)
        widget.add(save_div)


        gear = my.get_gear_menu()
        gear.add_style("float: right")


        widget.add( gear )


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




    def get_gear_menu(my):

        top = DivWdg()

        # FIXME: the gear menu widget should be here
        from tactic.ui.container import GearMenuWdg, Menu, MenuItem
        menu = Menu(width=180)

        menu_item = MenuItem(type='title', label='Actions')
        menu.add(menu_item)


        # create a new element
        menu_item = MenuItem(type='action', label='New Element')
        behavior = {
        'options': {
          'is_insert': 'true',
          'search_type': my.search_type,
          'view':        my.view
        },
        'cbjs_action': '''

        var activator = spt.smenu.get_activator(bvr);
        var top = activator.getParent(".spt_view_manager_top");
        var detail_panel = top.getElement(".spt_view_manager_detail");

        var class_name = 'tactic.ui.manager.ElementDefinitionWdg';
        var options = bvr.options
        var values = {};
        spt.panel.load(detail_panel, class_name, options, values, false);
        '''}
        menu_item.add_behavior(behavior)
        menu.add(menu_item)

        menu_item = MenuItem(type='separator')
        menu.add(menu_item)





        # Show preview of the view
        menu_item = MenuItem(type='action', label='Show Preview')
        behavior = {
        'search_type': my.search_type,
        'view':        my.view,
        'cbjs_action': '''
        var kwargs = {
          search_type: bvr.search_type,
          view: bvr.view
        };
        var title = "Search Type: [" + bvr.search_type + "], View [" + bvr.view + "]";
        spt.panel.load_popup(title, 'tactic.ui.panel.ViewPanelWdg', kwargs);
        '''}
        menu_item.add_behavior(behavior)
        menu.add(menu_item)



        # Show preview of the view
        menu_item = MenuItem(type='action', label='Show Full XML Config')
        behavior = {
        'search_type': my.search_type,
        'view':        my.view,
        'cbjs_action': '''
        var kwargs = {
          search_type: 'config/widget_config',
          view: 'table',
          expression: "@SOBJECT(config/widget_config['search_type','"+bvr.search_type+"']['view','"+bvr.view+"'])",
          filter: [{}]
        };
        var title = "Widget Config - ["+bvr.search_type+"] ["+bvr.view+"]";
        spt.panel.load_popup(title, 'tactic.ui.panel.ViewPanelWdg', kwargs);
        '''}
        menu_item.add_behavior(behavior)
        menu.add(menu_item)


        menu_item = MenuItem(type='separator')
        menu.add(menu_item)




        # New view popup
        new_view_wdg = DivWdg()
        new_view_wdg.add_class("spt_new_view")
        new_view_wdg.add_style("display: none")
        new_view_wdg.add_style("position: absolute")
        new_view_wdg.add_color("background", "background")
        new_view_wdg.add_style("z-index: 100")
        new_view_wdg.add_border()
        new_view_wdg.set_round_corners()
        new_view_wdg.set_box_shadow()
        new_view_wdg.add_style("padding: 30px")
        new_view_wdg.add("New View Name: ")
        new_view_text = TextWdg("new_view")
        new_view_text.add_class("spt_new_view_text")
        new_view_wdg.add(new_view_text)
        new_view_wdg.add(HtmlElement.br(2))

        #new_view_button = ProdIconButtonWdg('Save New View')
        new_view_button = ActionButtonWdg(title='Save', tip='Save New View')
        new_view_button.add_style("float: left")
        new_view_wdg.add(new_view_button)
        new_view_button.add_behavior( {
            'type': 'click_up',
            'search_type': my.search_type,
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_view_manager_top");
            var new_view_wdg = bvr.src_el.getParent(".spt_new_view");
            var new_view_text = new_view_wdg.getElement(".spt_new_view_text");
            var view = new_view_text.value;
            if (view != '') {
                var server = TacticServerStub.get()
                server.update_config(bvr.search_type, view, []);
                var values = {
                    search_type: bvr.search_type,
                    view: view
                };
                spt.panel.refresh(top, values);
                spt.hide(new_view_wdg);
            }
            else {
                alert("Must supply view name");
            }

            '''
        } )
        #new_view_cancel_button = ProdIconButtonWdg('Cancel')
        new_view_cancel_button = ActionButtonWdg(title='Cancel', tip='Cancel Save')
        new_view_cancel_button.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var new_view_wdg = bvr.src_el.getParent(".spt_new_view");
            spt.hide(new_view_wdg);
            '''
        } )
        new_view_wdg.add(new_view_cancel_button)
        top.add(new_view_wdg)


        #TODO: to be implemented.. no more xx please!
        """
        # Save to Project View
        menu_item = MenuItem(type='action', label='xx Save to Project View')
        behavior = {
        'options': {
            'search_type': 'SideBarWdg',
            'view':        'project_view'
        },
        'cbjs_action': '''
        spt.panel.load_popup('SideBar Section', 'tactic.ui.manager.SideBarSectionWdg', bvr.options);
        '''}
        menu_item.add_behavior(behavior)
        menu.add(menu_item)
        """

        # Create a new view
        menu_item = MenuItem(type='action', label='Create New View')
        behavior = {
        'search_type': my.search_type,
        'view':       my.view,
        'cbjs_action': '''
        var activator = spt.smenu.get_activator(bvr);
        var top = activator.getParent(".spt_view_manager_top");
        var new_view_wdg = top.getElement(".spt_new_view");
        spt.show(new_view_wdg);

        '''}
        menu_item.add_behavior(behavior)
        menu.add(menu_item)


        # Clear the current view
        menu_item = MenuItem(type='action', label='Clear View')
        behavior = {
        'options': {
          'is_insert': 'true',
          'search_type': my.search_type,
          'view':       my.view
        },
        'cbjs_action': '''
        if (confirm("Are you sure you wih to clear this view?")) {
            var activator = spt.smenu.get_activator(bvr);
            var top = activator.getParent(".spt_view_manager_top");
            var list_top = top.getElement(".spt_menu_item_list");
            var elements = spt.side_bar.get_elements(bvr.view,list_top);
            for (var i=0; i<elements.length; i++) {
                var element = elements[i];
                if (element.hasClass("spt_side_bar_dummy")) {
                    continue;
                }
                element.destroy();

            }
        }
        '''}
        menu_item.add_behavior(behavior)
        menu.add(menu_item)



        gear_menu = GearMenuWdg()
        gear_menu.add(menu)

        top.add(gear_menu)
        return top



    def get_section_wdg(my, view, editable=True, default=False):

        title = ""
        if editable:
            edit_mode = 'edit'
        else:
            edit_mode = 'read'
        kwargs = {
            'title': title,
            'config_search_type': my.search_type,
            'view': view,
            'width': '300',
            'mode': edit_mode,
            'default': str(default)
        }
        if view in ["definition", "custom_definition"]:
            kwargs['recurse'] = "false"

        from view_section_wdg import ViewSectionWdg
        section_wdg = ViewSectionWdg(**kwargs)
        class_path = Common.get_full_class_name(section_wdg)


        section_div = DivWdg(css='spt_panel')
        section_div.add_style("display: block")
        section_div.set_attr('spt_class_name', class_path)
        for name, value in kwargs.items():
            if name == "config":
                continue
            section_div.set_attr("spt_%s" % name, value)

        section_div.add(section_wdg)
        return section_div






