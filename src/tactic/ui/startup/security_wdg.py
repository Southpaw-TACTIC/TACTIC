###########################################################
#
# Copyright (c) 2010, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#

__all__ = ['UserAssignWdg', 'UserAssignCbk', 'GroupAssignWdg', 'GroupAssignCbk', 'SecurityWdg','TaskSecurityCbk','ProjectSecurityWdg','UserSecurityWdg','LinkSecurityWdg','GearMenuSecurityWdg','SearchTypeSecurityWdg','ProcessSecurityWdg','TaskSecurityWdg','SecurityBuilder']



import tacticenv

from pyasm.common import Environment, Common, Xml, jsonloads, Container, TacticException
from pyasm.search import Search, SearchType
from pyasm.security import LoginGroup, LoginInGroup
from pyasm.biz import Project
from pyasm.web import DivWdg, HtmlElement, SpanWdg, Table, Widget
from pyasm.widget import IconWdg, TextWdg, HiddenWdg
from pyasm.command import Command

import os
import six

from pyasm.web import WebContainer
from pyasm.widget import CheckboxWdg
from tactic.ui.common import BaseRefreshWdg
from tactic.ui.widget import ActionButtonWdg, IconButtonWdg

from tactic.ui.panel import SideBarBookmarkMenuWdg

class UserAssignWdg(BaseRefreshWdg):


    def get_display(self):
        top = self.top
        top.add_class("spt_groups_top")

        search_key = self.kwargs.get("search_key")

        group = Search.get_by_search_key(search_key)
        group_name = group.get_value("login_group")

        hidden = HiddenWdg("search_key", search_key)
        top.add(hidden)


        title = DivWdg()
        title.add( group.get_value("login_group") )
        top.add(title)
        title.add_gradient("background", "background3")
        title.add_style("padding: 10px")
        title.add_style("font-weight: bold")


        top.add_style("width: 300px")
        top.add_style("min-height: 300px")
        top.add_color("color", "color")
        top.add_color("background", "background")

        group_users = group.get_logins()
        group_users = [x.get_value("login") for x in group_users]

        search = Search("sthpw/login")
        logins = search.get_sobjects()


        action_button = ActionButtonWdg(title="Save >>")
        top.add(action_button)
        action_button.add_style("float: right")
        action_button.add_behavior( {
            'type': 'click_up',
            'group_name': group.get_value("login_group"),
            'cbjs_action': '''

            spt.app_busy.show("Saving Group Assignment")

            var top = bvr.src_el.getParent(".spt_groups_top");

            var values = spt.api.Utility.get_input_values(top);
            var kwargs = {
                values: values
            }

            var cmd = 'tactic.ui.startup.UserAssignCbk';
            var server = TacticServerStub.get();
            server.execute_cmd(cmd, kwargs)

            //spt.notify.show_mesage(bvr.full_name + " now belongs to the following groups: ");

            var top = bvr.src_el.getParent(".spt_panel_user_top");
            spt.panel.refresh(top);


            var popup = bvr.src_el.getParent( ".spt_popup" );
            if (popup)
                spt.popup.close(popup);
 
            spt.app_busy.hide()
            '''
        } )




        logins_div = DivWdg()
        logins_div.add_style("padding: 20px")
        top.add(logins_div)
        logins_div.add("<b>Users</b><br/>")

        for login in logins:
            login_name = login.get_value("login")
            if login_name == 'admin':
                continue

            display_name = login.get("display_name")
            if not display_name:
                display_name = login.get_full_name()
            if not display_name:
                display_name = login.get_code()

            login_div = DivWdg()
            logins_div.add(login_div)
            login_div.add_style("padding: 2px")
            login_div.add_style("margin: 3px")

            checkbox = CheckboxWdg("login_name")
            login_div.add(checkbox)
            checkbox.add_attr("multiple", "true")
            checkbox.set_attr("value", login_name)
            if login_name in group_users:
                checkbox.set_checked()
                login_div.add_color("background", "background", -10)
                login_div.set_box_shadow("1px 1px 1px 1px")
            login_div.set_round_corners()

            login_div.add("&nbsp;")
            login_div.add(display_name)

        return top



class UserAssignCbk(Command):

    def execute(self):

        web = WebContainer.get_web()
        values = self.kwargs.get("values")
        login_names = values.get("login_name")

        search_key = values.get("search_key")[0]
        group = Search.get_by_search_key(search_key)

        # find all the groups that this user current is in
        search = Search("sthpw/login_in_group")
        search.add_filter("login_group", group.get_value("login_group"))
        login_in_groups = search.get_sobjects()
        current_logins = set()

        for x in login_in_groups:
            if x.get_value("login") not in login_names:
                x.delete()
            else:
                current_logins.add( x.get_value("login") )

        for login_name in login_names:
            if not login_name:
                continue

            # don't add again
            if login_name in current_logins:
                continue

            sobject = SearchType.create("sthpw/login_in_group")
            sobject.set_value("login", login_name )
            sobject.set_value("login_group", group.get_value("login_group"))
            sobject.commit()




class GroupAssignWdg(BaseRefreshWdg):


    def get_display(self):
        top = self.top
        top.add_class("spt_groups_top")
        self.set_as_panel(top)

        search_key = self.kwargs.get("search_key")
        show_add_group = self.kwargs.get("show_add_group")

        login = Search.get_by_search_key(search_key)
        user = login.get_value("login")

        hidden = HiddenWdg("search_key", search_key)
        top.add(hidden)


        title = DivWdg()
        title.add( "User: %s" % login.get_full_name() )
        top.add(title)
        title.add_gradient("background", "background3")
        title.add_style("padding: 10px")
        title.add_style("margin-bottom: 5px")
        title.add_style("font-weight: bold")


        top.add_style("width: 400px")
        top.add_style("min-height: 300px")
        top.add_color("color", "color")
        top.add_color("background", "background")

        user_groups = LoginGroup.get_group_names(login_name=user)

        #search = Search("sthpw/login_group")
        #groups = search.get_sobjects()
        groups = LoginGroup.get_by_project()
        group_names = [x.get_value("login_group") for x in groups]


        add_button = ActionButtonWdg(title="+", size='small', tip="Add New Groups")
        top.add(add_button)
        add_button.add_style("float: left")
        top.add( self.get_add_groups_wdg() )
        add_button.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_groups_top");
            var add = top.getElement(".spt_groups_add");
            var checkbox = top.getElement(".spt_include_project_checkbox");
            var checkbox_label = top.getElement(".spt_include_project_checkbox_label");
            spt.toggle_show_hide(add);
            spt.toggle_show_hide(checkbox);
            spt.toggle_show_hide(checkbox_label);
            '''
        } )

        checkbox = CheckboxWdg("Include Project Name")
        checkbox.set_option("value", "true")
        checkbox.add_class("spt_include_project_checkbox")
        checkbox.add_style("display: none")
        checkbox.add_style("margin-left: 30px")
        checkbox.set_checked()
        checkbox_label = SpanWdg(" Add group to project")
        checkbox_label.add_style("display: none")
        checkbox_label.add_class("spt_include_project_checkbox_label")
        checkbox.add(checkbox_label)
        top.add(checkbox)

        if show_add_group not in ['false','False',False]:
            show_add_group = True
        else:
            show_add_group = False

        if not show_add_group:
            add_button.add_style("visibility: hidden")
            checkbox.add_style("visibility: hidden")


        action_button = ActionButtonWdg(title="Save")
        action_button.add_style("margin-right: 10px")
        top.add(action_button)
        action_button.add_style("float: right")
        action_button.add_behavior( {
            'type': 'click_up',
            'full_name': login.get_full_name(),
            'cbjs_action': '''

            spt.app_busy.show("Saving Group Assignment")

            var top = bvr.src_el.getParent(".spt_groups_top");

            var checkbox = top.getElement(".spt_include_project_checkbox");
            var checked = checkbox.checked;

            var values = spt.api.Utility.get_input_values(top);
            var kwargs = {
                "values": values,
                "checked": checked
            }

            var cmd = 'tactic.ui.startup.GroupAssignCbk';
            var server = TacticServerStub.get();
            try {
                var ret_val = server.execute_cmd(cmd, kwargs)


                var info = ret_val.info;
                var top = bvr.src_el.getParent(".spt_groups_top");

                spt.notify.show_message("Group changes saved succesfully");

                if (!info.close_popup) {
                    spt.panel.refresh(top);
                    spt.app_busy.hide()
                    return;
                }
                else {
                    //spt.notify.show_mesage(bvr.full_name + " now belongs to the following groups: ");
                    var popup = bvr.src_el.getParent( ".spt_popup" );
                    if (popup)
                        spt.popup.close(popup);
     
                    spt.app_busy.hide()
                }

            } catch(e) {
                spt.alert(spt.exception.handler(e));
                spt.app_busy.hide()
            }
            '''
        } )



        top.add("<br/>")

        groups_div = DivWdg()
        groups_div.add_style("padding: 20px")
        top.add(groups_div)
        title = DivWdg()
        groups_div.add(title)
        title.add("<b>Groups</b>")
        title.add_style("padding: 5px")
        title.add_style("margin: 5px -15px 10px -15px")
        title.add_color("background", "background3")

        for group in groups:
            group_name = group.get_value("login_group")
            group_name_label = group.get_value("name")
            if not group_name_label:
                group_name_label = group_name
                
            description = group.get_value("description")
            if not description:
                parts = group_name.split("/")
                if len(parts) > 1:
                    description = parts[1]

            group_div = DivWdg()
            groups_div.add(group_div)
            group_div.add_style("padding: 5px")
            group_div.add_style("display: flex; flex-flow: row nowrap; align-items: flex-end")

            checkbox = CheckboxWdg("group_name")
            checkbox_div = DivWdg()
            checkbox_div.add(checkbox)
            group_div.add(checkbox_div)
            checkbox.add_attr("multiple", "true")
            checkbox.set_attr("value", group_name)
            checkbox_div.add_style("margin-right: 5px")

            if group_name in user_groups:
                checkbox.set_checked()

            name_div = DivWdg()
            group_div.add(name_div)
            name_div.add("  %s" % group_name_label)
            name_div.add_style("display: inline-block")
            name_div.add_style("margin-right: 5px")
            name_div.add_style("margin-top: 4px")

            if description:
                div = DivWdg()
                group_div.add(div)
                div.add(" (%s)" % description)
                div.add_style("opacity: 0.5")
                div.add_style("font-style: italic")
                div.add_style("word-break: break-all")
                div.add_style("white-space: nowrap")
                div.add_style("overflow: hidden")
                div.add_style("word-wrap: break-word")
                div.add_style("text-overflow: ellipsis")
                div.add_style("width: 300px")
                div.add_style("display: inline-block")
                div.add_style("margin-top: 4px")


        return top



    def get_add_groups_wdg(self):

        div = DivWdg()
        div.add_class("spt_groups_add")
        div.add_style("display: none")

        div.add_style("padding: 5px")

        title = DivWdg()
        div.add(title)
        title.add(" Add New Groups: ")
        title.add_color("background", "background3")
        title.add_style("padding: 8px")
        title.add_style("margin: -5px -5px 10px -5px")

        from tactic.ui.container import DynamicListWdg
        dynamic_list = DynamicListWdg()
        div.add(dynamic_list)


        item_div = DivWdg()
        item_div.add_style("padding-left: 20px")
        text = TextWdg("new_group")
        item_div.add(text)
        dynamic_list.add_template(item_div)


        for i in range(0,2):
            item_div = DivWdg()
            text = TextWdg("new_group")
            item_div.add_style("padding-left: 20px")
            item_div.add(text)
            dynamic_list.add_item(item_div)


        return div






class GroupAssignCbk(Command):

    def execute(self):

        web = WebContainer.get_web()
        values = self.kwargs.get("values")
        group_names = values.get("group_name")

        search_key = values.get("search_key")[0]
        login = Search.get_by_search_key(search_key)

        # find all the groups that this user current is in
        login_in_groups = LoginInGroup.get_by_login_name(login.get_code())
        current_groups = set()
        for x in login_in_groups:
            if x.get_value("login_group") not in group_names:
                if x.get_value('login_group') == 'admin':
                    current_groups.add( x.get_value("login_group") )
                else:
                    x.delete()
            else:
                current_groups.add( x.get_value("login_group") )

        for group_name in group_names:
            if not group_name:
                continue

            # don't add again
            if group_name in current_groups:
                continue

            sobject = SearchType.create("sthpw/login_in_group")
            sobject.set_value("login", login.get_code() )
            sobject.set_value("login_group", group_name)
            sobject.commit()


        project = Project.get()
        project_code = project.get_code()

        new_groups = values.get("new_group")
        for new_group in new_groups:
            if not new_group:
                continue

            # make sure the group doesn't already exist
            #login_group = LoginGroup.get_by_login_group(new_group)

            project_included = False
            user_defined_project_code = ""
            original_new_group = new_group
            is_project_specific = False
            if self.kwargs.get("checked") in [True, "true", "True"]:
                is_project_specific = True

            if new_group.find("/") == -1:
                title = new_group
                new_group = "%s/%s" % (project_code, new_group)
            else:
                parts = new_group.split("/")
                title = parts[1]
                user_defined_project_code = parts[0]
                project_included = True

            new_group = Common.get_filesystem_name(new_group)

            group = SearchType.create("sthpw/login_group")

            # the following sections contains the 4 cases possible when creating a new group
            # through the popup
            
            # if the input is (project/name) and (not project specific)
            if not is_project_specific and project_included:
                
                # Raise exception because it's contradictory data
                raise TacticException('''You've given a project code while declaring 
                    the group not project specific. You can either not use the format 
                    "project_code/group_name", or check the "Project specific" checkbox.''')

            # if the input is (project/name) and (project specific)
            elif is_project_specific and project_included:

                # first check is the user_defined_project_code is actually a project
                # if it is, then set that as the project code. If not, don't set anything

                user_defined_project = Project.get_by_code(user_defined_project_code)

                if user_defined_project:
                    group.set_value("project_code", user_defined_project_code)
                else:
                    raise TacticException('''The project code that you've given doesn't exist.
                        Please choose an existing project code. Note: the format is
                        "project_code/group_name".''')
                group.set_value("login_group", original_new_group)

            # if the input is (name) and (not project specific)
            elif not is_project_specific and not project_included:
                group.set_value("login_group", title)

            # if the input is (name) and (project specific)
            else:
                group.set_value("project_code", project_code)
                group.set_value("login_group", new_group)

            group.set_value("description", title)
            group.commit()

            self.info = {
                'close_popup': False
            }



__all__.append("GroupSummaryWdg")
class GroupSummaryWdg(BaseRefreshWdg):

    def get_display(self):

        top = self.top
        top.add_style("padding: 10px")
        top.add_color("background", "background")
        top.add_border()

        search_key = self.kwargs.get("search_key")
        login = Search.get_by_search_key(search_key)

        xx = LoginInGroup.get_by_login_name(login.get_value("login"))
        groups = []
        for x in xx:
            groups.append(x.get_value("login_group"))

        # get all of the access rules and merge

        from pyasm.web import WikiUtil

        for group_name in groups:
            group = LoginGroup.get_by_group_name(group_name)
            if not group:
                continue

            group_div = DivWdg()
            title_div = DivWdg()
            group_div.add(title_div)
            title_div.add(group_name)
            title_div.add_color("background", "background3")


            # can see projects
            """
            project_div = DivWdg()
            group_div.add(project_div)
            project_div.add("Projects:<br/>")
            project_div.add("fickle3<br/>")

            project_div.add("&nbsp;&nbsp;Links:<br/>")
            project_div.add("&nbsp;&nbsp;Client Home:<br/>")

            project_div.add("big_test22<br/>")
            """


            top.add(group_div)
            access_rules = group.get_xml_value("access_rules")
            access_rules_str = access_rules.to_string()
            access_rules_str = WikiUtil().convert(access_rules_str)
            group_div.add("<pre>%s</pre>" % access_rules_str)


        return top







class SecurityWdg(BaseRefreshWdg):
    '''This secuirty widget allows for the configuration of security'''

    def get_args_keys(self):
        return {
        }


    def get_section_wdg(self, title, description, image, behavior):

        section_wdg = DivWdg()
        section_wdg.set_round_corners()
        section_wdg.add_border()
        #section_wdg.add_style("width: 225px")
        #section_wdg.add_style("height: 200px")
        section_wdg.add_style("width: 200px")
        section_wdg.add_style("height: 145px")
        section_wdg.add_style("overflow: hidden")
        section_wdg.add_style("margin: 10px")
        section_wdg.add_style("box-shadow: 0px 0px 10px rgba(0,0,0,0.1)")

        title_wdg = DivWdg()
        section_wdg.add(title_wdg)
        title_wdg.add(title)
        title_wdg.add_style("height: 25px")
        title_wdg.add_style("padding: 5px")
        title_wdg.add_style("font-weight: bold")
        title_wdg.add_style("text-align: center")
        title_wdg.add_color("background", "background", -10)

        section_wdg.add_color("background", "background")
        section_wdg.add_behavior( {
        'type': 'hover',
        'add_color_modifier': -3,
        'cb_set_prefix': 'spt.mouse.table_layout_hover',
        } )

        section_wdg.add_behavior( {
        'type': 'click',
        'cbjs_action': '''
        bvr.src_el.setStyle("box-shadow", "0px 0px 15px rgba(0,0,0,0.5)");
        '''
        } )

        section_wdg.add_behavior( {
        'type': 'mouseenter',
        'cbjs_action': '''
        bvr.src_el.setStyle("box-shadow", "0px 0px 10px rgba(0,0,0,0.3)");
        ''',
        } )

        section_wdg.add_behavior( {
        'type': 'mouseleave',
        'cbjs_action': '''
        bvr.src_el.setStyle("box-shadow", "0px 0px 10px rgba(0,0,0,0.1)");
        ''',
        } )


        desc_div = DivWdg()
        desc_div.add(description)
        desc_div.add_style("text-align: center")
        desc_div.add_style("padding: 5px 10px 10px 10px")
        desc_div.add_style("font-size: 1.1em")

        div = DivWdg()
        section_wdg.add(div)
        div.add_style("padding: 3px")
        div.add_style("margin: 10px")
        #div.add_style("width: 209px")
        #div.add_style("height: 64px")
        div.add_style("text-align: center")
        div.add(image)
        #div.set_box_shadow("1px 1px 1px 1px")
        section_wdg.add(desc_div)
        div.add_style("overflow: hidden")

        section_wdg.add_behavior( behavior )
        section_wdg.add_class("hand")

        return section_wdg


    def get_display(self):

        project = Project.get()
        project_code = project.get_code()


        top = DivWdg()
        top.add_border()
        top.add_style("padding: 10px")
        top.add_color("color", "color")
        top.add_gradient("background", "background", 0, -5)
        top.add_class("spt_dashboard_top")


        title = DivWdg()
        title.add("Security")
        top.add(title)

        from tactic.ui.widget import TitleWdg
        #subtitle = TitleWdg(name_of_title='Security Tools',help_alias='manage-security')
        #top.add(subtitle)

        title.add_style("font-size: 18px")
        title.add_style("font-weight: bold")
        title.add_style("text-align: center")
        title.add_style("padding: 10px")
        title.add_style("margin: -10px -10px 10px -10px")
        title.add_gradient("background", "background3", 5, -10)




        from .misc_wdg import MainShelfWdg
        shelf_wdg = MainShelfWdg(top_class='spt_dashboard_top', list_class='spt_dashboard_list', height=207)
        top.add(shelf_wdg)

        outer = DivWdg()
        top.add(outer)
        outer.add_style("overflow-y: hidden")

        div = DivWdg()
        outer.add(div)
        div.add_class("spt_dashboard_list")
        div.add_style("overflow-x: auto")
        div.add_style("width: 100%")
        #div.add_behavior( {
        #    'type': 'load',
        #    'cbjs_action': '''
        #    var size = bvr.src_el.getParent().getSize();
        #    alert(size.x);
        #    bvr.src_el.setStyle("width", size.x);
        #    '''
        #} )
        div.add_style("margin-bottom: 20px")
        div.center()
        div.add_border()


        # create a bunch of panels
        table = Table()
        div.add(table)
        table.add_color("color", "color")
        table.add_style("margin-bottom: 20px")
        table.center()
        table.add_row()



        #
        """
        td = table.add_cell()
        td.add_style("padding: 3px")
        td.add_style("vertical-align: top")
        title = "Add Users to Project"
        image = IconWdg('', IconWdg.USER_32)
        description = '''Add users to the groups from this project.'''

        behavior = {
        'type': 'click_up',
        'cbjs_action': '''
        var class_name = 'tactic.ui.startup.UserSecurityWdg';
        var kwargs = {};

        var top = bvr.src_el.getParent(".spt_dashboard_top");
        spt.tab.set_tab_top(top);
        spt.tab.add_new("user_security", "User Security", class_name, kwargs);
        '''
        }


        users_wdg = self.get_section_wdg(title, description, image, behavior)
        td.add(users_wdg)
        """


        # 
        td = table.add_cell()
        td.add_style("padding: 3px")
        td.add_style("vertical-align: top")
        title = "Project Security"
        description = '''Project security determines which project each group can see.'''
        image = IconWdg('', IconWdg.LOCK_32_01)
        behavior = {
        'type': 'click_up',
        'cbjs_action': '''
        var class_name = 'tactic.ui.startup.ProjectSecurityWdg';
        var kwargs = {};

        var top = bvr.src_el.getParent(".spt_dashboard_top");
        spt.tab.set_tab_top(top);
        spt.tab.add_new("project_security", "Project Security", class_name, kwargs);
        '''
        }
        config_wdg = self.get_section_wdg(title, description, image, behavior)
        td.add(config_wdg)



        #
        td = table.add_cell()
        td.add_style("vertical-align: top")
        td.add_style("padding: 3px")
        title = "Link Security"
        #image = IconWdg('', IconWdg.SECURITY_32_21, width=32)
        image = IconWdg('Link Security', 'FA_LINK', width=32)
        description = '''Link security determines which side bar links are visible to each group.'''

        behavior = {
        'type': 'click_up',
        'cbjs_action': '''
        var class_name = 'tactic.ui.startup.LinkSecurityWdg';
        var kwargs = {
            help_alias: 'link_security'  
        };
        var top = bvr.src_el.getParent(".spt_dashboard_top");
        spt.tab.set_tab_top(top);
        spt.tab.add_new("link_security", "Link Security", class_name, kwargs);
 

        '''


        }
        gear_menu_security_wdg = self.get_section_wdg(title, description, image, behavior)
        td.add(gear_menu_security_wdg)

        #
        td = table.add_cell()
        td.add_style("vertical-align: top")
        td.add_style("padding: 3px")
        title = "Gear Menu Security"
        image = IconWdg('', IconWdg.SECURITY_32_21, width=32) # Icon needs to be changed
        image = IconWdg('', "FA_GEAR", width=32)
        description = '''Gear Menu security determines which gear menu items each group can see.'''

        behavior = {
        'type': 'click_up',
        'cbjs_action': '''
        var class_name = 'tactic.ui.startup.GearMenuSecurityWdg';
        var kwargs = {};
        var top = bvr.src_el.getParent(".spt_dashboard_top");
        spt.tab.set_tab_top(top);
        spt.tab.add_new("gear_menu_security", "Gear Menu Security", class_name, kwargs);
 

        '''


        }
        pipeline_wdg = self.get_section_wdg(title, description, image, behavior)
        td.add(pipeline_wdg)

        #
        td = table.add_cell()
        td.add_style("padding: 3px")
        td.add_style("vertical-align: top")
        title = "sType Security"
        #image = "<img src='/context/icons/64x64/report_64.png'/>"
        image = IconWdg('', IconWdg.SECURITY_32_18)
        description = '''sType security provides low level security for all items.'''

        behavior = {
        'type': 'click_up',
        'cbjs_action': '''
        var class_name = 'tactic.ui.startup.SearchTypeSecurityWdg';
        var kwargs = {};

        var top = bvr.src_el.getParent(".spt_dashboard_top");
        spt.tab.set_tab_top(top);
        spt.tab.add_new("stype_security", "sType Security", class_name, kwargs);
        '''
        }

        stype_security_wdg = self.get_section_wdg(title, description, image, behavior)
        td.add(stype_security_wdg)


        #
        td = table.add_cell()
        td.add_style("padding: 3px")
        td.add_style("vertical-align: top")
        title = "Process Security"
        #image = "<img src='/context/icons/64x64/report_64.png'/>"
        #image = IconWdg('', IconWdg.SECURITY_32_20)
        image = IconWdg('', 'FA_PROJECT_DIAGRAM', width=32)
        description = '''Process security provides low level security for all processes.'''

        behavior = {
        'type': 'click_up',
        'cbjs_action': '''
        var class_name = 'tactic.ui.startup.ProcessSecurityWdg';
        var kwargs = {};

        var top = bvr.src_el.getParent(".spt_dashboard_top");
        spt.tab.set_tab_top(top);
        spt.tab.add_new("process_security", "Process Security", class_name, kwargs);
        '''
        }

        process_security_wdg = self.get_section_wdg(title, description, image, behavior)
        td.add(process_security_wdg)

        # Adding Task Security Wdg
        td = table.add_cell()
        td.add_style("padding: 3px")
        td.add_style("vertical-align: top")
        title = "Task Security"
        #image = "<img src='/context/icons/64x64/report_64.png'/>"
        #image = IconWdg('', IconWdg.SECURITY_32_20)
        image = IconWdg('', 'FA_TASKS', width=32)
        description = '''Task security customizes the visibility of task status.'''

        behavior = {
        'type': 'click_up',
        'cbjs_action': '''
        var class_name = 'tactic.ui.startup.TaskSecurityWdg';
        var kwargs = {};

        var top = bvr.src_el.getParent(".spt_dashboard_top");
        spt.tab.set_tab_top(top);
        spt.tab.add_new("task_security", "Task Security", class_name, kwargs);
        '''
        }

        process_security_wdg = self.get_section_wdg(title, description, image, behavior)
        td.add(process_security_wdg)

        #
        td = table.add_cell()
        td.add_style("padding: 3px")
        td.add_style("vertical-align: top")
        title = "Groups"
        #image = "<img src='/context/icons/64x64/report_64.png'/>"
        #image = IconWdg('', IconWdg.SECURITY_32_17)
        image = IconWdg('', 'FA_USERS', width=32)
        description = '''Task security customizes the visibility of task status.'''
        description = '''List of user groups.'''

        behavior = {
        'type': 'click_up',
        'cbjs_action': '''
        var class_name = 'tactic.ui.startup.SecurityGroupListWdg';
        var kwargs = {};

        var top = bvr.src_el.getParent(".spt_dashboard_top");
        spt.tab.set_tab_top(top);
        spt.tab.add_new("groups", "Group List", class_name, kwargs);
        '''
        }

        groups_wdg = self.get_section_wdg(title, description, image, behavior)
        td.add(groups_wdg)



        #
        """
        td = table.add_cell()
        td.add_style("padding: 3px")
        td.add_style("vertical-align: top")
        title = "User List"
        image = "<img src='/context/icons/64x64/report_64.png'/>"
        description = '''Lists of all the users.'''

        behavior = {
        'type': 'click_up',
        'cbjs_action': '''
        var class_name = 'tactic.ui.panel.ViewPanelWdg';
        var kwargs = {
            search_type: 'sthpw/login',
            view: 'table'
        };

        var top = bvr.src_el.getParent(".spt_dashboard_top");
        spt.tab.set_tab_top(top);
        spt.tab.add_new("manage_users", "Users", class_name, kwargs);
        '''
        }

        users_wdg = self.get_section_wdg(title, description, image, behavior)
        td.add(users_wdg)
        """





        # add a tab widget
        from tactic.ui.container import TabWdg
        config_xml = '''
        <config>
        <tab>
        <element name="groups" title="Group List">
            <display class='tactic.ui.startup.SecurityGroupListWdg'>
            </display>
        </element>
        </tab>
        </config>
        '''
        tab = TabWdg(show_add=False, config_xml=config_xml)
        top.add(tab)


        return top




__all__.append("SecurityGroupListWdg")
class SecurityGroupListWdg(BaseRefreshWdg):

    def get_display(self):
        top = self.top
        view = self.kwargs.get("view")
        expression = self.kwargs.get("expression")
        insert_view = self.kwargs.get("custom_insert_view")
        edit_view = self.kwargs.get("custom_edit_view")
        show_refresh = self.kwargs.get("show_refresh")
        show_keyword_search = self.kwargs.get("show_keyword_search")
        show_save  = self.kwargs.get("show_save")
        show_insert = self.kwargs.get("show_insert")
        show_gear = self.kwargs.get("show_gear")
        show_search_limit = self.kwargs.get("show_search_limit")
        show_search = self.kwargs.get("show_search")
        show_column_manager = self.kwargs.get("show_column_manager")
        show_context_menu = self.kwargs.get("show_context_menu")
        show_expand = self.kwargs.get("show_expand")
        show_layout_switcher = self.kwargs.get("show_layout_switcher")
        show_help = self.kwargs.get("show_help")

        if not view:
            view = "startup"

        if not insert_view:
            insert_view = "insert"

        if not edit_view:
            edit_view = "edit"

        '''
        show_all_groups = True
        if show_all_groups:
            search = Search("sthpw/login_group")
            search.add_order_by("project_code")
            search.add_order_by("login_group")
            groups = search.get_sobjects()
        else:
            groups = LoginGroup.get_by_project()
        '''
        
        from tactic.ui.panel import ViewPanelWdg
        layout = ViewPanelWdg(
            search_type='sthpw/login_group',
            view=view,
            simple_search_view='simple_search',
            expand_on_load=True,
            expression=expression,
            insert_view=insert_view,
            edit_view=edit_view,
            show_refresh=show_refresh,
            show_keyword_search=show_keyword_search,
            show_save=show_save,
            show_insert=show_insert,
            show_gear=show_gear,
            show_search_limit=show_search_limit,
            show_search=show_search,
            show_column_manager=show_column_manager,
            show_context_menu=show_context_menu,
            show_expand=show_expand,
            show_layout_switcher=show_layout_switcher,
            show_help=show_help
        )
        top.add(layout)

        return top




__all__.append("SecurityCheckboxElementWdg")

from tactic.ui.common import SimpleTableElementWdg
class SecurityCheckboxElementWdg(SimpleTableElementWdg):

    def preprocess(self):
        self.all = False

        self.security_type = Container.get("SecurityWdg:security_type")


    def handle_td(self, td):
        sobject = self.get_current_sobject()
        value = sobject.get_value(self.get_name())
        code = sobject.get_code()

        if code == "*" and value:
             self.all = True


        name = self.get_name()
        self.access_level = sobject.get_value("%s:access_level" % name, no_exception=True)
        if not self.access_level:
            from pyasm.security import Login
            self.access_level = Login.get_default_security_level()
        #Login.get_security_level_group(access_level)
        self.project_code = sobject.get_value("%s:project_code" % name, no_exception=True)

        # FIXME: assumed knowledge of default for access_level
        is_set = False
        if self.security_type == 'project' and self.access_level in ['min', 'low', 'medium', 'high']:
            if self.project_code and sobject.get_value("code") == self.project_code:
                is_set = True
            else:
                is_set = False
        elif self.security_type == 'link' and self.access_level in ['high']:
            is_set = True
        elif self.security_type == 'gear_menu' and self.access_level in ['high']:
            is_set = True
        elif self.security_type == 'search_type' and self.access_level in ['min', 'low', 'medium','high']:
            is_set = True
        elif self.security_type == 'process' and self.access_level in ['low', 'medium','high']:
            is_set = True


        if is_set:
            td.add_color("background", "background3", [5, 5, 5])
        else:
            if self.all == True:
                td.add_color("background", "background3")
            elif value:
                td.add_color("background", "background3", [-20, 20, -20])

        td.add_style("opacity: 0.6")



 
    def handle_th(self, th, index):
        th.add_attr("spt_input_type", "inline")


    def handle_layout_behaviors(self, layout):
        name = Common.get_filesystem_name(self.get_name())
        layout.add_relay_behavior( {
        'type': 'click',
        #'propagate_evt': True,
        'bvr_match_class': 'spt_format_checkbox_%s' %name.replace("/","_") ,

        'cbjs_action': '''
        var layout = bvr.src_el.getParent(".spt_layout");
        var value_wdg = bvr.src_el;
        var checkbox = value_wdg.getElement(".spt_input");
        spt.table.set_layout(layout);
        if (checkbox) {
            spt.table.accept_edit(checkbox, checkbox.checked, false)
        }
        '''
        } )





    def get_display(self):

        div = DivWdg()
        div.add_style("text-align: center")
        div.add_style("min-width: 40px")

        safe_name = Common.get_filesystem_name(self.get_name())
        div.add_class('spt_format_checkbox_%s' % safe_name.replace("/","_"))

        sobject = self.get_current_sobject()
        name = self.get_name()
        value = sobject.get_value(name)





        self.access_level = sobject.get_value("%s:access_level" % name, no_exception=True)
        if not self.access_level:
            from pyasm.security import Login
            self.access_level = Login.get_default_security_level()

        self.project_code = sobject.get_value("%s:project_code" % name, no_exception=True)

        # FIXME: assumed knowledge of default for access_level
        is_set = False
        if self.security_type == 'project' and self.access_level in ['min', 'low', 'medium', 'high']:
            if self.project_code and sobject.get_value("code") == self.project_code:
                is_set = True
            else:
                is_set = False
 
        elif self.security_type == 'link' and self.access_level in ['high']:
            is_set = True
        elif self.security_type == 'gear_menu' and self.access_level in ['high']:
            is_set = True
        elif self.security_type == 'search_type' and self.access_level in ['min', 'low', 'medium', 'high']:
            is_set = True
        elif self.security_type == 'process' and self.access_level in ['low', 'medium', 'high']:
            is_set = True


        checkbox = CheckboxWdg("whatever")
        checkbox.add_class("spt_checkbox")

        if is_set:
            icon = IconWdg("Set by access level [%s]" % self.access_level, IconWdg.CHECK)
            div.add(icon)
            div.add_style("padding-top: 3px")

        elif value:
            checkbox.set_checked()
            div.add(checkbox)
        elif self.all:
            icon = IconWdg("ALL is set", IconWdg.CHECK)
            div.add(icon)
            div.add_style("padding-top: 3px")

        else:
            div.add(checkbox)

        #if self.get_name().find("client") != -1:
        #    icon = IconWdg("All projects", IconWdg.STAR, width=8)
        #    div.add(icon)

        return div


__all__.append("SecurityAddGroupToProjectInputWdg")
__all__.append("SecurityAddGroupToProjectAction")
from pyasm.widget import BaseInputWdg
class SecurityAddGroupToProjectInputWdg(BaseInputWdg):

    def get_display(self):

        div = DivWdg()
        checkbox = CheckboxWdg(self.get_input_name())
        checkbox.set_checked()
        div.add(checkbox)

        return div

from pyasm.command import DatabaseAction
class SecurityAddGroupToProjectAction(DatabaseAction):

    def execute(self):
        value = self.get_value()
        sobject = self.sobject
        project = Project.get()
        project_code = project.get_code()

        builder = SecurityBuilder(group=sobject)
        builder.add_project(project_code)
        if value:
            sobject.set_value("access_rules", builder.to_string() )



class BaseSecurityWdg(BaseRefreshWdg):

    def get_security_type(self):
        raise Exception("Need to override get_security_type()")

    def get_save_cbk(self):
        raise Exception("Need to override get_save_cbk()")



    def get_value(self, name):
        web = WebContainer.get_web()
        value = web.get_form_value(name)
        if not value:
            value = self.kwargs.get(name)
        return value


    def get_groups(self):
        search = Search("sthpw/login_group")
        filter = self.kwargs.get("filter")
        if filter:
            search.add_filter("login_group", filter)

        #if self.__class__.__name__ in ['ProjectSecurityWdg','UserSecurityWdg']:
        if self.__class__.__name__ in ['ProjectSecurityWdg']:
            project_only = self.kwargs.get("project_only")
            project_only = True
            if project_only in [True, 'true']:
                groups = LoginGroup.get_by_project()
                group_names = [x.get_value("login_group") for x in groups]
                search.add_op("begin")
                search.add_filters("login_group", group_names)
                search.add_filter("project_code", "NULL", op="is", quoted=False)
                search.add_filter("project_code", "")
                search.add_op("or")
        else:
            groups = LoginGroup.get_by_project()


            ignore = self.kwargs.get("ignore_groups")
            if ignore:
                ignore = ignore.split(",")
            else:
                ignore = []


            group_names = []
            for group in groups:
                login_group = group.get_value("login_group")
                if login_group in ignore:
                    continue

                group_names.append(login_group)


            search.add_filters("login_group", group_names)


        groups = search.get_sobjects()

        return groups



    def get_display(self):

        top = self.top
        top.add_class("spt_security_top")
        self.set_as_panel(top)
        #top.add_border()

        top.add_color("background", "background")

        Container.put("SecurityWdg:security_type", self.get_security_type())

        group_names = []
        groups = []
        from tactic.ui.panel import TableLayoutWdg


        groups = self.get_groups()
        group_names = [x.get_value("login_group") for x in groups]

        config_xml = []
        config_xml.append('''<config><table edit='false'>''')


        filter = []

        columns = self.get_display_columns()
        for column in columns:
            config_xml.append('''<element name='%s' edit='false'/>''' % column)

        if not groups:
            config_xml.append('''<element name='%s' edit='false'/>''' % "No Groups in this project")

        for group_name in group_names:
            if filter and group_name not in filter:
                continue

            if group_name == 'admin':
                continue

            """
            config_xml.append('''
            <element name='_%s' title='%s'>
              <display widget='format'>
                <format>Checkbox</format>
              </display>
            </element>
            ''' % (group_name, group_name) )
            """


            group_title = group_name.title()
            group_title = group_title.replace("_", " ")


            config_xml.append('''
            <element name='_%s' title='%s' edit='false'>
              <display class='tactic.ui.startup.SecurityCheckboxElementWdg'>
              </display>
            </element>
            ''' % (group_name, group_title) )




        config_xml.append('''</table></config>''')
        config_xml = "\n".join(config_xml)

        from pyasm.widget import WidgetConfig
        config = WidgetConfig.get(view="table", xml=config_xml)


        from tactic.ui.widget import ButtonRowWdg, ButtonNewWdg
        button_row = ButtonRowWdg()
        top.add(button_row)
        button_row.add_style("float: left")
        button_row.add_style("padding: 5px")

        if self.get_security_type() in ['project', 'user']:
            from tactic.ui.input import LookAheadTextInputWdg
            if self.get_security_type() == 'project':
                search_type = 'sthpw/project'
                column = ['title']
            else:
                search_type = 'sthpw/login'
                #column = ['login','first_name','last_name']
                column = ['login']

            custom_cbk = {}
            custom_cbk['enter'] = '''
                var top = bvr.src_el.getParent(".spt_security_top");
                var keywords = bvr.src_el.value;
                spt.panel.refresh(top, {keyword: keywords});
             
            '''

            text = LookAheadTextInputWdg(icon="BS_SEARCH", name='keyword', search_type=search_type, column=column, mode='keyword', custom_cbk=custom_cbk)
            search_div = DivWdg()
            top.add(search_div)
            search_div.add_style("padding-top: 5px")

            value = self.get_value("keyword")
            if value:
                text.set_value(value)

            search_div.add(text)
            search_div.add_style("margin-left: 100px")
            search_div.add_style("width: 300px")


        top.add("<br clear='all'/>")


 
        refresh_button = ButtonNewWdg(tip="Refresh", icon="FA_SYNC")
        button_row.add(refresh_button)
        refresh_button.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_security_top");
            spt.panel.refresh(top);
            '''

        } )



        
        save_button = ButtonNewWdg(tip="Save Changes", icon="FA_SAVE")
        button_row.add(save_button)
        save_button.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_security_top");
            var layout = top.getElement(".spt_layout");
            spt.table.set_layout(layout);

            spt.table.save_changes( { refresh: false } );
            spt.panel.refresh(top);
            '''

        } )



        show_add = self.kwargs.get("show_add")
        if show_add in [True, 'true']:
            project_code = Project.get_project_code()

            add_button = ButtonNewWdg(tip="Refresh", icon="FA_PLUS")
            button_row.add(add_button)
            add_button.add_behavior( {
                'type': 'click_up',
                'project_code': project_code,
                'cbjs_action': '''
                var class_name = 'tactic.ui.panel.EditWdg';
                var kwargs = {
                    search_type: 'sthpw/login_group',
                    view: 'project_edit',
                    extra_data: {
                        project_code: bvr.project_code,
                    },

                }

                spt.panel.load_popup("Add New Group", class_name, kwargs);
                '''

            } )




        sobjects = self.get_sobjects(group_names)

        self.set_access_levels(sobjects, group_names)

        # these are virtual sobjects, don't show search limit to avoid pagination 

        group_elements = self.get_group_elements()

        layout = TableLayoutWdg(
            search_type='sthpw/virtual',
            view='table',
            show_shelf=False,
            show_search_limit="false",
            config_xml=config_xml,
            save_class_name=self.get_save_cbk(),
            init_load_num = -1,
            expand_on_load=True,
            show_context_menu=False,
            # group_elements=group_elements,
        )
        layout.add_style("height: calc(100% - 42px)")
        layout.set_sobjects(sobjects)
        top.add(layout)

        return top



    def get_display_columns(self):
        return ['preview', 'title']

    def get_group_elements(self):
        return []



    def set_access_levels(self, sobjects, group_names):
        # set access levels
        access_levels = {}
        project_codes = {}
        for sobject in sobjects:
            for group_name in group_names:
                if access_levels.get(group_name) == None:
                    group = LoginGroup.get_by_group_name(group_name)

                    access_level = group.get_value("access_level")
                    access_levels[group_name] = access_level

                    project_code = group.get_value("project_code")
                    project_codes[group_name] = project_code

                # make up some arbitrary attribute to store access level
                # of the group.
                attr = "_%s:access_level" % group_name
                sobject.set_value(attr, access_levels[group_name]) 
                attr = "_%s:project_code" % group_name
                sobject.set_value(attr, project_codes[group_name]) 



    def get_sobjects(self, group_names):
        # get the project sobjects
        search = Search("sthpw/project")
        search.add_filters("code", ['sthpw','admin','unittest'], op='not in')

        keyword = self.get_value("keyword")
        if keyword:
            search.add_keyword_filter("title", keyword)

        search.add_order_by("title")
        projects = search.get_sobjects()

        if not keyword:
            sobject = SearchType.create("sthpw/virtual")
            sobject.set_value("title", "ALL PROJECTS")
            sobject.set_value("_extra_data", {"is_all": True})
            sobject.set_value("id", 1)
            sobject.set_value("code", "*")
            projects.insert(0, sobject)


        # process all of the groups and find out which projects
        security = Environment.get_security()

        rules_dict = {}

        for project in projects:
            for group_name in group_names:

                access_rules = rules_dict.get(group_name)
                if access_rules == None:
                    group = LoginGroup.get_by_group_name(group_name)
                    access_rules = group.get_xml_value("access_rules")
                    rules_dict[group_name] = access_rules

                node = access_rules.get_node("rules/rule[@group='project' and @code='%s']" % project.get_code())

                if node is not None:
                    project.set_value("_%s" % group_name, True)
                else:
                    project.set_value("_%s" % group_name, False)

        return projects



class ProjectSecurityWdg(BaseSecurityWdg):

    def get_security_type(self):
        return "project"


    def get_save_cbk(self):
        return 'tactic.ui.startup.ProjectSecurityCbk'


    def get_display_columns(self):
        return ['preview', 'title']




class UserSecurityWdg(ProjectSecurityWdg):

    def get_security_type(self):
        return "user"


    def get_save_cbk(self):
        return 'tactic.ui.startup.UserSecurityCbk'


    def get_display_columns(self):
        return ['preview', 'login', 'first_name', 'last_name']




    def get_sobjects(self, group_names):
        # get the project sobjects
        search = Search("sthpw/login")
        search.add_filters("code", ['admin'], op='not in')

        keyword = self.get_value('keyword')
        if keyword:
            search.add_filter("login", keyword)
        sobjects = search.get_sobjects()

        """
        if not keyword:
            sobject = SearchType.create("sthpw/login")
            sobject.set_value("title", "ALL USERS")
            sobject.set_value("_extra_data", {"is_all": True})
            sobject.set_value("id", 1)
            sobject.set_value("code", "*")
            sobject.set_value("login", "*")
            sobjects.insert(0, sobject)
        """

        # process all of the groups and find out which sobjects
        security = Environment.get_security()

        project = Project.get()
        project_code = project.get_code()

        rules_dict = {}


        # get all of the login for the given groups
        search = Search("sthpw/login_in_group")
        search.add_filters("login_group", group_names)
        login_in_group_objs = search.get_sobjects()
        group_data = {}
        for login_in_group in login_in_group_objs:
            group = login_in_group.get_value("login_group")
            login = login_in_group.get_value("login")
            data = group_data.get(group)
            if not data:
                data = set()
                group_data[group] = data
            data.add(login)


        for sobject in sobjects:
            for group_name in group_names:

                login = sobject.get_value("login")

                data = group_data.get(group_name)
                is_in_group = False
                if data:
                    is_in_group = login in data

                if is_in_group:
                    sobject.set_value("_%s" % group_name, True)
                else:
                    sobject.set_value("_%s" % group_name, False)


        return sobjects





class SearchTypeSecurityWdg(ProjectSecurityWdg):

    def get_security_type(self):
        return "search_type"


    def get_save_cbk(self):
        return 'tactic.ui.startup.SearchTypeSecurityCbk'


    def get_sobjects(self, group_names):
        # get the project sobjects
        sobjects = Project.get().get_search_types()

        sobject = SearchType.create("sthpw/virtual")
        sobject.set_value("title", "ALL PROJECTS")
        sobject.set_value("_extra_data", {"is_all": True})
        sobject.set_value("id", 1)
        sobject.set_value("code", "*")
        sobjects.insert(0, sobject)



        # process all of the groups and find out which sobjects
        security = Environment.get_security()

        rules_dict = {}

        for sobject in sobjects:
            for group_name in group_names:

                access_rules = rules_dict.get(group_name)
                if access_rules == None:
                    group = LoginGroup.get_by_group_name(group_name)
                    access_rules = group.get_xml_value("access_rules")
                    rules_dict[group_name] = access_rules

                node = access_rules.get_node("rules/rule[@group='search_type' and @code='%s']" % sobject.get_code())

                title = sobject.get_value('title')
                if not title:
                    st = sobject.get_value('search_type')
                    sobject.set_value("title", st)
                
                if node is not None:
                    sobject.set_value("_%s" % group_name, True)
                else:
                    sobject.set_value("_%s" % group_name, False)


        return sobjects

class GearMenuSecurityWdg(ProjectSecurityWdg):
    '''Control Gear Menu visibility'''
    def get_security_type(self):
        return "gear_menu"

    def get_save_cbk(self):
        return 'tactic.ui.startup.GearMenuSecurityCbk'

    def get_display_columns(self):
        return ['submenu', 'label']

    def get_sobjects(self, group_names):

        all_gear_menu_names = GearMenuSecurityWdg.get_all_menu_names()
        rules_dict = {}

        project = Project.get()
        project_code = project.get_code()
        
        sobjects = []

        for key,value in all_gear_menu_names:
            
            submenu = key
            
            for label in value.get('label'):
                sobject = SearchType.create("sthpw/virtual")
                
                if submenu == "ALL MENU ITEMS":
                    sobject.set_value("_extra_data", {"is_all": True})
                    submenu = '*'

                title_wdg = DivWdg()
                title_wdg.add(label)
                sobject.set_value("id", 1)
                sobject.set_value("code", submenu)
                sobject.set_value("submenu", submenu)
                sobject.set_value("label", title_wdg)
                sobject.set_value("_extra_data", {"label": label, "submenu": submenu})

                for group_name in group_names:

                    access_rules = rules_dict.get(group_name)

                    if access_rules == None:
                        group = LoginGroup.get_by_group_name(group_name)
                        access_rules = group.get_xml_value("access_rules")
                        rules_dict[group_name] = access_rules

                    path = "rules/rule[@group='gear_menu' and @submenu='%s' and @label='%s' and @project='%s']" % (submenu, label, project_code)
                    node = access_rules.get_node(path)

                    if node is not None:
                        sobject.set_value("_%s" % group_name, True)
                    else:
                        sobject.set_value("_%s" % group_name, False)

                sobjects.append(sobject)
        return sobjects

    def get_all_menu_names(cls):
        all_gear_menu_names = {'ALL MENU ITEMS':{'label': ['*'],'order': 0},
                               'Edit': {'label': ['Retire Selected Items','Delete Selected Items','Show Server Transaction Log','Undo Last Server Transaction','Redo Last Server Transaction'],'order': 1},
                               'File': {'label': ['Export All ...','Export Selected ...','Export Matched ...','Export Displayed ...','Import CSV','Ingest Files','Check-out Files'], 'order': 2},
                               'Clipboard': {'label': ['Copy Selected','Paste','Connect','Append Selected','Show Clipboard Contents'], 'order': 3},
                               'View': {'label': ['Column Manager','Create New Column','Save Current View','Save a New View','Edit Current View','Edit Config XML'], 'order': 4},
                               'Print': {'label': ['Print Selected','Print Displayed','Print Matched'], 'order': 5},
                               'Chart': {'label': ['Chart Items','Chart Selected'], 'order': 6},
                               'Tasks': {'label': ['Show Tasks','Add Tasks to Selected','Add Tasks to Matched'], 'order': 7},
                               'Notes': {'label': ['Show Notes'], 'order': 8},
                               'Check-ins': {'label': ['Show Check-in History'], 'order': 9},
                               'Pipelines': {'label': ['Show Pipeline Code','Edit Pipelines'], 'order': 10}
                               }
        all_gear_menu_names = sorted(
                all_gear_menu_names.items(),
                #key=lambda (x,y):y['order']
                key=lambda pair: pair[1]['order']
        )
        return all_gear_menu_names
    get_all_menu_names = classmethod(get_all_menu_names)



class LinkSecurityWdg(ProjectSecurityWdg):

    def get_security_type(self):
        return "link"


    def get_save_cbk(self):
        return 'tactic.ui.startup.LinkSecurityCbk'


    def get_display_columns(self):
        show_name = self.kwargs.get("show_name")
        show_description = self.kwargs.get("show_description")

        columns = ['title']

        if show_name not in [False, 'false']:
            columns.append('name')

        if show_description in [True, 'true']:
            columns.append('description')

        return columns


    def get_group_elements(self):
        return ['category']


    def get_info(self, config, names, links, titles, descriptions, icons, level):

        element_names = config.get_element_names()
        for element_name in element_names:
            if not element_name:
                print("WARNING: Empty element name found in Link security")
                print(config.get_xml().to_string())
                continue

            names.append(element_name)

            display_options = config.get_display_options(element_name)
            attrs = config.get_element_attributes(element_name)
            title = attrs.get("title")
            if not title:
                title = Common.get_display_title(element_name)

            description = attrs.get("description")
            if not description:
                description = ""


            links.append(element_name)
            titles.append(title)
            descriptions.append(description)

            icon = DivWdg()
            icons.append(icon)
            icon.add_style("float: left")
            icon.add("&nbsp;"*level*7)

            display_handler = config.get_display_handler(element_name)

            if attrs.get("icon"):
                icon_str = attrs.get('icon').upper()
                icon.add( IconWdg("Link", icon_str ))
            elif display_handler == 'LinkWdg':
                icon.add( IconWdg("Link", IconWdg.VIEW) )
            elif display_handler == 'SeparatorWdg':
                icon.add( "&nbsp;<b style=''>---</b> &nbsp; " )
            else:
                icon.add( IconWdg("Folder", IconWdg.FOLDER) )

            if display_handler not in ['LinkWdg', 'SeparatorWdg']:
                options = config.get_display_options(element_name)
                folder_view = options.get('view')
                if not folder_view:
                    folder_view = element_name
                # usually folder_view = element_name , but it could be manually changed 
                sub_config = SideBarBookmarkMenuWdg.get_config( "SideBarWdg", folder_view)
                self.get_info(sub_config, names, links, titles, descriptions, icons, level+1)


    def get_sobjects(self, group_names):
        #from pyasm.widget import WidgetConfig, WidgetConfigView
        #from pyasm.search import WidgetDbConfig

        base = self.kwargs.get("base")
        if not base:
            base = "project_view"

        config = SideBarBookmarkMenuWdg.get_config( "SideBarWdg", base)

        names = []
        links = []
        titles = []
        descriptions = []
        categories = []
        icons = []
        level = 0
        self.get_info(config, names, links, titles, descriptions, icons, level)
            

        rules_dict = {}

        project = Project.get()
        project_code = project.get_code()


        # not sure why these are added here. 
        my_admin_links = ['manage_my_views', 'my_preference']
        my_admin_links = []

        for my_admin_link in my_admin_links:
            names.insert(0, my_admin_link)
            titles.insert(0, my_admin_link.replace("_", " ").title())
            descriptions.insert(0, "")
            categories.insert(0, "Admin")
            icons.insert(0, "")
            links.insert(0, my_admin_link)


        names.insert(0, "*")
        links.insert(0, "*")
        titles.insert(0, "ALL LINKS")
        descriptions.insert(0, "Able to see all links")
        icons.insert(0, "")

        show_icon = self.kwargs.get("show_icon")
        if show_icon in [False, 'false']:
            show_icon = False
        else:
            show_icon = True

      
        sobjects = []
        for name, link, title, description, icon in zip(names, links, titles, descriptions, icons):

            sobject = SearchType.create("sthpw/virtual")

            if link == "*":
                sobject.set_value("_extra_data", {"is_all": True})

            title_wdg = DivWdg()

            if show_icon:
                title_wdg.add(icon)
            title_wdg.add(title)


            category = "Sidebar Links"

            sobject.set_value("id", 1)
            sobject.set_value("code", link)
            sobject.set_value("title", title_wdg)
            sobject.set_value("name", name)
            sobject.set_value("description", description)
            sobject.set_value("category", category)
            sobject.set_value("_extra_data", {"link": link})
            for group_name in group_names:

                access_rules = rules_dict.get(group_name)
                if access_rules == None:
                    group = LoginGroup.get_by_group_name(group_name)
                    access_rules = group.get_xml_value("access_rules")
                    rules_dict[group_name] = access_rules


                path = "rules/rule[@group='link' and @element='%s' and @project='%s']" % (link, project_code)
                node = access_rules.get_node(path)

                if node is not None:
                    sobject.set_value("_%s" % group_name, True)
                else:
                    sobject.set_value("_%s" % group_name, False)

            sobjects.append(sobject)
        return sobjects



class ProcessSecurityWdg(ProjectSecurityWdg):

    def get_security_type(self):
        return "process"


    def get_save_cbk(self):
        return 'tactic.ui.startup.ProcessSecurityCbk'


    def get_display_columns(self):
        return ['pipeline_code', 'process']

    def get_sobjects(self, group_names):

        pre_search = Search("sthpw/pipeline")
        sobjects = pre_search.get_sobjects()

        code_list = []
        for sobject in sobjects:
            if sobject.get("search_type") == "sthpw/task":
                code_list.append(sobject.get("code"))
        code_list.append('task')
        search = Search("config/process")
        search.add_filters("pipeline_code", code_list, op="not in")
        search.add_order_by('pipeline_code')
        search.add_order_by('process')

        #search2 = Search("sthpw/pipeline")
        #search2.add_filter("search_type", "sthpw/task")
        #search.add_relationship_search_filter(search, op='not in')
        sobjects = search.get_sobjects()
        
        #for sobj in sobjects:
        #    st = Search.eval('@GET(sthpw/pipeline.search_type)', sobjects=[sobj])
        #    sobj.set_value("_extra_data", {'search_type': st})

        sobject = SearchType.create("sthpw/virtual")
        sobject.set_value("process", "*")
        sobject.set_value("pipeline_code", "ALL")
        sobject.set_value("_extra_data", {"is_all": True})
        sobject.set_value("id", 1)
        sobject.set_value("code", "*")
        sobjects.insert(0, sobject)

    
        # process all of the groups and find out which sobjects
        security = Environment.get_security()

        rules_dict = {}

        for sobject in sobjects:
            for group_name in group_names:

                access_rules = rules_dict.get(group_name)
                if access_rules == None:
                    group = LoginGroup.get_by_group_name(group_name)
                    access_rules = group.get_xml_value("access_rules")
                    rules_dict[group_name] = access_rules

                xpath = "rules/rule[@group='process' and @process='%s']" % sobject.get_value("process")

                node = access_rules.get_node(xpath)

                if node is not None:
                    sobject.set_value("_%s" % group_name, True)
                else:
                    sobject.set_value("_%s" % group_name, False)

        return sobjects



class TaskSecurityWdg(ProjectSecurityWdg):

    def get_security_type(self):
        return "process"


    def get_save_cbk(self):
        return 'tactic.ui.startup.TaskSecurityCbk'


    def get_display_columns(self):
        return ['pipeline_code', 'process']

    def get_sobjects(self, group_names):
        pre_search = Search("sthpw/pipeline")
        sobjects = pre_search.get_sobjects()

        code_list = []
        for sobject in sobjects:
            if sobject.get("search_type") == "sthpw/task":
                code_list.append(sobject.get("code"))
        code_list.append('task')
        search = Search("config/process")
        search.add_filters("pipeline_code", code_list)
        search.add_order_by('pipeline_code')
        search.add_order_by('process')

        #search2 = Search("sthpw/pipeline")
        #search2.add_filter("search_type", "sthpw/task")
        #search.add_relationship_search_filter(search, op='not in')
        sobjects = search.get_sobjects()
        
        #for sobj in sobjects:
        #    st = Search.eval('@GET(sthpw/pipeline.search_type)', sobjects=[sobj])
        #    sobj.set_value("_extra_data", {'search_type': st})

        sobject = SearchType.create("sthpw/virtual")
        sobject.set_value("process", "*")
        sobject.set_value("pipeline_code", "ALL")
        sobject.set_value("_extra_data", {"is_all": True})
        sobject.set_value("id", 1)
        sobject.set_value("code", "*")
        sobjects.insert(0, sobject)

    
        # process all of the groups and find out which sobjects
        security = Environment.get_security()

        rules_dict = {}

        for sobject in sobjects:
            for group_name in group_names:

                access_rules = rules_dict.get(group_name)
                if access_rules == None:
                    group = LoginGroup.get_by_group_name(group_name)
                    access_rules = group.get_xml_value("access_rules")
                    rules_dict[group_name] = access_rules

                old_xpath = "rules/rule[@group='process' and @process]"
                xpath = "rules/rule[@group='process' and @pipeline]"
                node = access_rules.get_node(xpath)
                old_node = access_rules.get_node(old_xpath)
                
                if node is not None:
                    further_path = "rules/rule[@process='%s' and @pipeline='%s'] | rules/rule[@process='*' and @pipeline='*']" % (sobject.get_value("process"),sobject.get_value("pipeline_code"))
                    new_node = access_rules.get_node(further_path)

                    if new_node is not None:
                        sobject.set_value("_%s" % group_name, True)
   
                    else:
                        sobject.set_value("_%s" % group_name, False)

                else:
                    # backward compatibility
                    further_path = "rules/rule[@process='%s'] | rules/rule[@process='*']" % (sobject.get_value("process"))  
                    old_node = access_rules.get_node(further_path)

                    if old_node is not None:
                        sobject.set_value("_%s" % group_name, True)
       
                    else:
                        sobject.set_value("_%s" % group_name, False)


        return sobjects



__all__.append("ProjectSecurityCbk")
__all__.append("UserSecurityCbk")
__all__.append("GearMenuSecurityCbk")
__all__.append("LinkSecurityCbk")
__all__.append("SearchTypeSecurityCbk")
__all__.append("ProcessSecurityCbk")

class ProjectSecurityCbk(Command):
    def execute(self):

        search_keys = self.kwargs.get("search_keys")
        update_data = self.kwargs.get("update_data")
        if isinstance(update_data, six.string_types):
            update_data = jsonloads(update_data)

        extra_data = self.kwargs.get("extra_data")
        if isinstance(extra_data, six.string_types):
            extra_data = jsonloads(extra_data)


        builders = {}
        for search_key,data,extra in zip(search_keys, update_data, extra_data):

            if extra:
                is_all = extra.get("is_all")
            else:
                is_all = False

            if is_all:
                project_code = "*"
            else:
                project = Search.get_by_search_key(search_key)
                project_code = project.get_code()

            for group_name, is_insert in data.items():
                group_name = group_name.lstrip("_")

                group = LoginGroup.get_by_code(group_name)
                builder = builders.get(group_name)
                if not builder:
                    builder = SecurityBuilder(group=group)
                    builders[group_name] = builder

                if is_insert == "true":
                    builder.add_project(project_code)
                else:
                    builder.remove_project(project_code)

        for group_name, builder in builders.items():
            group_name = group_name.lstrip("_")
            group = LoginGroup.get_by_code(group_name)
            access_rules = builder.to_string()
            group.set_value("access_rules", access_rules)
            group.commit()



class UserSecurityCbk(Command):
    def execute(self):

        search_keys = self.kwargs.get("search_keys")
        update_data = self.kwargs.get("update_data")
        if isinstance(update_data, six.string_types):
            update_data = jsonloads(update_data)

        extra_data = self.kwargs.get("extra_data")
        if isinstance(extra_data, six.string_types):
            extra_data = jsonloads(extra_data)


        # get all of the login for the given groups
        search = Search("sthpw/login_in_group")
        #search.add_filters("login_group", group_names)
        login_in_group_objs = search.get_sobjects()
        login_data = {}
        for login_in_group in login_in_group_objs:
            group = login_in_group.get_value("login_group")
            login = login_in_group.get_value("login")
            data = login_data.get(login)
            if not data:
                data = set()
                login_data[login] = data
            data.add(group)

        # Add / Remove users from group
        builders = {}
        for search_key,data,extra in zip(search_keys, update_data, extra_data):

            login_obj = Search.get_by_search_key(search_key)
            login = login_obj.get_value("login")

            cur_group_names = login_data.get(login)
            if not cur_group_names:
                cur_group_names = set()

            for item in data:
                item = item.lstrip("_")
                if item in cur_group_names:
                    login_obj.remove_from_group(item)
                else:
                    login_obj.add_to_group(item)





class SearchTypeSecurityCbk(Command):
    def execute(self):

        search_keys = self.kwargs.get("search_keys")
        update_data = self.kwargs.get("update_data")
        if isinstance(update_data, six.string_types):
            update_data = jsonloads(update_data)

        extra_data = self.kwargs.get("extra_data")
        if isinstance(extra_data, six.string_types):
            extra_data = jsonloads(extra_data)


        project = Project.get()
        project_code = project.get_code()

        builders = {}
        for search_key,data,extra in zip(search_keys, update_data, extra_data):

            if extra:
                is_all = extra.get("is_all")
            else:
                is_all = False

            if is_all:
                search_type = "*"
            else:
                search_type_obj = Search.get_by_search_key(search_key)
                search_type = search_type_obj.get_value("search_type")

            for group_name, is_insert in data.items():
                group_name = group_name.lstrip("_")

                group = LoginGroup.get_by_code(group_name)
                builder = builders.get(group_name)
                if not builder:
                    builder = SecurityBuilder(group=group)
                    builders[group_name] = builder

                if is_insert == "true":
                    builder.add_search_type(search_type, project_code=project_code)
                else:
                    builder.remove_search_type(search_type, project_code=project_code)

        for group_name, builder in builders.items():
            group_name = group_name.lstrip("_")
            group = LoginGroup.get_by_code(group_name)
            access_rules = builder.to_string()
            group.set_value("access_rules", access_rules)
            group.commit()

class GearMenuSecurityCbk(Command):
    def execute(self):

        search_keys = self.kwargs.get("search_keys")
        update_data = self.kwargs.get("update_data")
        if isinstance(update_data, six.string_types):
            update_data = jsonloads(update_data)

        extra_data = self.kwargs.get("extra_data")

        if isinstance(extra_data, six.string_types):
            extra_data = jsonloads(extra_data)

        project = Project.get()
        project_code = project.get_code()

        builders = {}
        for search_key,data,extra in zip(search_keys, update_data, extra_data):
            
            label = extra.get("label")
            submenu = extra.get("submenu")
            if submenu == "ALL MENU ITEMS":
                submenu = '*'

            for group_name, is_insert in data.items():
                group_name = group_name.lstrip("_")

                group = LoginGroup.get_by_code(group_name)
                builder = builders.get(group_name)
                if not builder:
                    builder = SecurityBuilder(group=group)
                    builders[group_name] = builder

                if is_insert == "true":
                    builder.add_gear_menu(submenu, label, project_code=project_code)
                else:
                    builder.remove_gear_menu(submenu, label, project_code=project_code)

        for group_name, builder in builders.items():
            group_name = group_name.lstrip("_")
            group = LoginGroup.get_by_code(group_name)
            access_rules = builder.to_string()
            group.set_value("access_rules", access_rules)
            group.commit()

class LinkSecurityCbk(Command):
    def execute(self):

        search_keys = self.kwargs.get("search_keys")
        update_data = self.kwargs.get("update_data")
        if isinstance(update_data, six.string_types):
            update_data = jsonloads(update_data)

        extra_data = self.kwargs.get("extra_data")
        if isinstance(extra_data, six.string_types):
            extra_data = jsonloads(extra_data)

        project = Project.get()
        project_code = project.get_code()

        builders = {}
        for search_key,data,extra in zip(search_keys, update_data, extra_data):

            link = extra.get("link")

            for group_name, is_insert in data.items():
                group_name = group_name.lstrip("_")

                group = LoginGroup.get_by_code(group_name)
                builder = builders.get(group_name)
                if not builder:
                    builder = SecurityBuilder(group=group)
                    builders[group_name] = builder

                if is_insert == "true":
                    builder.add_link(link, project_code=project_code)
                else:
                    builder.remove_link(link, project_code=project_code)



        for group_name, builder in builders.items():
            group_name = group_name.lstrip("_")
            group = LoginGroup.get_by_code(group_name)
            access_rules = builder.to_string()
            group.set_value("access_rules", access_rules)
            group.commit()


    

class ProcessSecurityCbk(Command):

    def use_project(self):
        return True

    def use_pipeline(self):
        return False

    def execute(self):

        search_keys = self.kwargs.get("search_keys")
        update_data = self.kwargs.get("update_data")
        if isinstance(update_data, six.string_types):
            update_data = jsonloads(update_data)

        extra_data = self.kwargs.get("extra_data")
        if isinstance(extra_data, six.string_types):
            extra_data = jsonloads(extra_data)

        project = Project.get()
        if self.use_project():
            project_code = project.get_code()
        else:
            project_code = None

        builders = {}
        for search_key,data,extra in zip(search_keys, update_data, extra_data):

            if extra:
                is_all = extra.get("is_all")
                #st = extra.get("search_type")
            else:
                is_all = False

            pipeline_code = ""
            if is_all:
                process = "*"
                pipeline_code = "*"
            else:
                process_sobj = Search.get_by_search_key(search_key)
                process = process_sobj.get_value("process")
                if self.use_pipeline():
                    pipeline_code = process_sobj.get_value("pipeline_code")

            for group_name, is_insert in data.items():
                group_name = group_name.lstrip("_")

                group = LoginGroup.get_by_code(group_name)
                builder = builders.get(group_name)
                if not builder:
                    builder = SecurityBuilder(group=group)
                    builders[group_name] = builder

                if is_insert == "true":
                    builder.add_process(process, project_code=project_code, pipeline_code=pipeline_code)
                else:
                    builder.remove_process(process, project_code=project_code, pipeline_code=pipeline_code)


        for group_name, builder in builders.items():
            group_name = group_name.lstrip("_")
            group = LoginGroup.get_by_code(group_name)
            access_rules = builder.to_string()
            group.set_value("access_rules", access_rules)
            group.commit()



class TaskSecurityCbk(ProcessSecurityCbk):

    def use_project(self):
        return False

    def use_pipeline(self):
        return True
    



class SecurityBuilder(object):

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        group = self.kwargs.get("group")
        if group:
            self.xml = group.get_xml_value("access_rules")

        else:
            self.xml = Xml()
            self.xml.read_string("<rules/>")

        assert self.xml

        self.root = self.xml.get_root_node()


    def to_string(self):
        return self.xml.to_string()


    def add_project(self, project_code, access="allow"):
        rule = self.xml.create_element("rule")
        self.xml.set_attribute(rule, "group", "project")
        self.xml.set_attribute(rule, "code", project_code)
        self.xml.set_attribute(rule, "access", access)
        self.xml.append_child(self.root, rule)

    def remove_project(self, project_code):
        nodes = self.xml.get_nodes("rules/rule[@group='project']")
        for node in nodes:
            if self.xml.get_attribute(node, 'code') == project_code:
                self.xml.remove_child(self.root, node)





    def add_gear_menu(self, submenu, label, access="allow", project_code=None):
        if project_code:
            nodes = self.xml.get_nodes("rules/rule[@group='gear_menu' and @project='%s']" % project_code)

        else:
            nodes = self.xml.get_nodes("rules/rule[@group='gear_menu']")

        submenus = [self.xml.get_attribute(node, 'submenu') for node in nodes]
        labels = [self.xml.get_attribute(node, 'label') for node in nodes]

        if label not in labels:
            rule = self.xml.create_element("rule")
            self.xml.set_attribute(rule, "group", "gear_menu")
            self.xml.set_attribute(rule, "submenu", submenu)
            self.xml.set_attribute(rule, "label", label)
            if project_code:
                self.xml.set_attribute(rule, "project", project_code)
            self.xml.set_attribute(rule, "access", access)
            self.xml.append_child(self.root, rule)
            
    def remove_gear_menu(self, submenu, label, project_code=None):
        if project_code:
            nodes = self.xml.get_nodes("rules/rule[@group='gear_menu' and @project='%s']" % project_code)

        else:
            nodes = self.xml.get_nodes("rules/rule[@group='gear_menu']")
        for node in nodes:
            if self.xml.get_attribute(node, 'label') == label:
                self.xml.remove_child(self.root, node)
    


    def add_link(self, link, access="allow", project_code=None):
        if project_code:
            nodes = self.xml.get_nodes("rules/rule[@group='link' and @project='%s']" % project_code)
        else:
            nodes = self.xml.get_nodes("rules/rule[@group='link']")
        links = [self.xml.get_attribute(node, 'element') for node in nodes] 

        if link not in links:
            rule = self.xml.create_element("rule")
            self.xml.set_attribute(rule, "group", "link")
            self.xml.set_attribute(rule, "element", link)
            if project_code:
                self.xml.set_attribute(rule, "project", project_code)
            self.xml.set_attribute(rule, "access", access)
            self.xml.append_child(self.root, rule)


    def remove_link(self, link, project_code=None):
        if project_code:
            nodes = self.xml.get_nodes("rules/rule[@group='link' and @project='%s']" % project_code)
        else:
            nodes = self.xml.get_nodes("rules/rule[@group='link']")

        for node in nodes:
            if self.xml.get_attribute(node, 'element') == link:
                self.xml.remove_child(self.root, node)



    def add_process(self, process, access="allow", project_code=None, pipeline_code=None):
        '''check before adding a new node since the user can uncheck and check again'''

        pipeline_code_expr = ''
        if pipeline_code:
            pipeline_code_expr = "and @pipeline='%s'"%pipeline_code

        project_code_expr = ''
        if project_code:
            project_code_expr = "and @project='%s'"%project_code

        check_node = self.xml.get_node("rules/rule[@group='process' and @process='%s' %s %s]" % (process, pipeline_code_expr, project_code_expr))
        if check_node is None:
            rule = self.xml.create_element("rule")
            self.xml.set_attribute(rule, "group", "process")
            self.xml.set_attribute(rule, "process", process)
            if project_code:
                self.xml.set_attribute(rule, "project", project_code)
            if pipeline_code:
                self.xml.set_attribute(rule, "pipeline", pipeline_code)
            self.xml.set_attribute(rule, "access", access)
            self.xml.append_child(self.root, rule)


    def remove_process(self, process, project_code=None, pipeline_code=None):
        pipeline_code_expr = ''
        if pipeline_code:
            pipeline_code_expr = "and @pipeline='%s'"%pipeline_code
        
        if project_code:
            nodes = self.xml.get_nodes("rules/rule[@group='process' and @project='%s' %s]" % (project_code, pipeline_code_expr))
        else:
            # for backward comaptibilty when the concept of @pipeline doesn't exist at all 
            check_node = self.xml.get_node("rules/rule[@pipeline]")
            if check_node is not None:
                nodes = self.xml.get_nodes("rules/rule[@group='process' %s]" % pipeline_code_expr)
            else:
                nodes = self.xml.get_nodes("rules/rule[@group='process']")
                
        if not nodes and process =='*':
            nodes = self.xml.get_nodes("rules/rule[@group='process' and @process='*']")

        for node in nodes:
            if self.xml.get_attribute(node, 'process') == process:
                self.xml.remove_child(self.root, node)




    def add_search_type(self, search_type, access="allow", project_code=None):
        rule = self.xml.create_element("rule")
        self.xml.set_attribute(rule, "group", "search_type")
        self.xml.set_attribute(rule, "code", search_type)
        if project_code:
            self.xml.set_attribute(rule, "project", project_code)
        self.xml.set_attribute(rule, "access", access)
        self.xml.append_child(self.root, rule)


    def remove_search_type(self, search_type, project_code=None):
        if project_code:
            nodes = self.xml.get_nodes("rules/rule[@group='search_type' and @project='%s']" % project_code)
        else:
            nodes = self.xml.get_nodes("rules/rule[@group='search_type']")

        for node in nodes:
            if self.xml.get_attribute(node, 'code') == search_type:
                self.xml.remove_child(self.root, node)




    def add_builtin(self):
        pass



if __name__ == '__main__':


    builder = SecurityBuilder()

    builder.add_project("fickle3")
    builder.add_project("big_test22")

    print(builder.to_string())


