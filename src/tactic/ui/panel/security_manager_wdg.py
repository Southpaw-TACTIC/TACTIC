###########################################################
#
# Copyright (c) 2005-2009, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#
__all__ = ["SecurityManagerButtonWdg", "SecurityManagerWdg"]

import os, types

from pyasm.common import Common, Environment
from pyasm.search import SearchKey
from pyasm.web import DivWdg, WebContainer, HtmlElement
from pyasm.security import Login, AccessManager, AccessRuleBuilder
from pyasm.command import Command
from pyasm.widget import CheckboxWdg, BaseTableElementWdg, IconWdg, IconButtonWdg, ProdIconButtonWdg, HiddenWdg

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.widget import ActionButtonWdg


class SecurityManagerButtonWdg(BaseTableElementWdg):

    def get_display(my):


        div = DivWdg()

        sobject = my.get_current_sobject()
        search_key = SearchKey.get_by_sobject(sobject)

        if sobject.is_admin():
            return "ADMIN"

        icon = IconButtonWdg("Global Permissions", IconWdg.EDIT)

        icon.add_behavior( {
            "type": "click_up",
            "cbjs_action": "spt.popup.get_widget(evt, bvr)",
            "options": {
                "class_name": "tactic.ui.panel.SecurityManagerWdg",
                "title": "Permisssion Manager",
                "popup_id": "Permission Manager"

            },
            "args": {
                "search_key": search_key
            }
        } )

        div.add(icon)

        return div


permission_list = [
    {'group': 'Interface View Permissions'},
    {'key':'view_side_bar', 'title': 'View Side Bar', 'default': 'allow'},
    {'key':'view_site_admin', 'title': 'View Site Admin'},
    {'key':'view_script_editor', 'title': 'View Script Editor'},
    {'key':'side_bar_schema', 'title': 'View Side Bar Schema'},
    {'key':'view_save_my_view', 'title': 'View and Save My Views', 'default': 'allow'},
    {'key':'view_private_notes', 'title': 'View Private Notes'},
    {'key':'view_column_manager', 'title': 'View Column Manager'},
    {'key':'view_template_projects', 'title': 'View Template Projects', 'default': 'deny'},
    {'group': 'Data Manipuation Permissions'},
    {'key':'create_projects', 'title': 'Create Projects', 'description': 'The gives the user the permission to create projects'},
    {'key':'export_all_csv', 'title': 'Export All CSV'},
    {'key':'import_csv', 'title': 'Import CSV'},
    {'key':'retire_delete', 'title': 'Retire and Delete'},
    {'key':'edit', 'title': 'Edit'}
]


        

class SecurityManagerWdg(BaseRefreshWdg):
    '''Panel to manage global security settings'''

    def get_args_keys(my):
        return {
        'search_key': 'the search key of the sobject to be operated on',
        'update': 'true|false determines whether to update or not'
        }


    def init(my):
        my.search_key = my.kwargs.get("search_key")
        my.update = my.kwargs.get("update")
        my.description = ''
        if my.update == "true":
            cmd = SecurityManagerCbk()
            cmd.set_search_key(my.search_key)
            Command.execute_cmd(cmd)
            my.description = cmd.get_description()


    def get_display(my):
        div = DivWdg()
       
      
        div.add_class("spt_security")
        div.add_attr("id", "SecurityManagerWdg")
        div.add_attr("spt_class_name", Common.get_full_class_name(my) )
        div.add_attr("spt_search_key", my.search_key)
        div.add_attr("spt_update", "true")

        project_div = DivWdg()
        project_div.add_color("background", "background")
        project_div.add_color("color", "color")
        project_div.add_style("padding: 10px")
        project_div.add_border()
        project_div.add_style("width: 300px")

        group = SearchKey.get_by_search_key(my.search_key)

        title = DivWdg()
        title.add_class("maq_search_bar")
        name = group.get_value("login_group")
        title.add("Global security settings for %s" % name)

        project_div.add(title)



        access_rules = group.get_xml_value("access_rules")
        access_manager = AccessManager()
        access_manager.add_xml_rules(access_rules)


        group = "builtin"
        global_default_access = "deny"


        list_div = DivWdg()
        list_div.add_style("color: #222")
        for item in permission_list:
            if item.get('group'):
                group_div = DivWdg()
                list_div.add(group_div)
                group_div.add_style("margin-top: 10px")
                group_div.add_style("font-weight: bold")
                group_div.add(item.get('group'))
                group_div.add("<hr/>")
                continue

            item_div = DivWdg()
            list_div.add(item_div)
            item_div.add_style("margin-top: 5px")

            key = item.get('key')
            item_default = item.get('default')
            if item_default:
                default_access = item_default
            else:
                default_access = global_default_access

            allowed = access_manager.check_access(group, key, "allow", default=default_access)

            checkbox = CheckboxWdg("rule")
            if allowed:
                checkbox.set_checked()
            checkbox.set_option("value", key)

            item_div.add(checkbox)


            item_div.add_style("color: #222")
            item_div.add(item.get('title') )

            

        project_div.add(list_div)

        project_div.add("<hr>")

        #close_script = "spt.popup.close(bvr.src_el.getParent('.spt_popup'))"

        save_button = ActionButtonWdg(title="Save", tip="Save Security Settings")
        save_button.add_behavior( {
            "type": "click_up",
            "cbjs_action": "el=bvr.src_el.getParent('.spt_security');spt.panel.refresh(el);"        } )

        save_button.add_style("margin-left: auto")
        save_button.add_style("margin-right: auto")
        project_div.add(save_button)


            
        div.add(project_div)
        if my.update == "true":
            div.add(HtmlElement.br())
            div.add(HtmlElement.b(my.description))
 
        return div



class SecurityManagerCbk(Command):
    '''Panel to manage global security settings'''

    def check(my):
        return True

    def set_search_key(my, search_key):
        my.search_key = search_key

    def execute(my):

        search_key = my.search_key
        assert search_key

        sobject = SearchKey.get_by_search_key(search_key)
        xml = sobject.get_xml_value("access_rules")

        from pyasm.security import AccessRuleBuilder
        builder = AccessRuleBuilder(xml=xml)

        web = WebContainer.get_web()
        rules = web.get_form_values("rule")


        # sync the rules
        group = "builtin"
        group_default = 'deny'
        builder.add_default_rule(group, group_default)
        default_attr = builder.get_default(group)
        for item in permission_list:
            key = item.get('key')
            if key in rules:
                if default_attr == 'deny':
                    access = "allow"
                    builder.add_rule(group, key, access)
                else:
                    builder.remove_rule(group, key)
            else:
                if default_attr == 'deny':
                    builder.remove_rule(group, key)
                else:
                    access = "deny"
                    builder.add_rule(group, key, access)

        new_rules = builder.to_string()
        sobject.set_value("access_rules", new_rules)
        sobject.commit()
        my.add_description('Built-in access rules updated sucessfully!')


