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

__all__ = ["AddUserToGroupCbk", "SecurityRulesAttr"]

from pyasm.common import Xml
from pyasm.security import Login, LoginGroup
from pyasm.search import *

from command import Command



class AddUserToGroupCbk(Command):
    '''Base class for all command'''

    def get_title(my):
        return "Manage Security"

    def check(my):
        return True


    def execute(my):
        from pyasm.web import WebContainer
        web = WebContainer.get_web()

        # look for add user action
        if web.get_form_value("add_user") != "":
            my.add_user_to_group()
        elif web.get_form_value("remove_user") != "":
            my.remove_user_from_group()
        elif web.get_form_value("sobject_commit") != "":
            my.sobject_commit()
        elif web.get_form_value("url_commit") != "":
            my.url_commit()
        else:
            raise CommandExitException()



    def add_user_to_group(my):
        web = WebContainer.get_web()
        user_name = web.get_form_value("user_to_add")
        group_name = web.get_form_value("group_name")

        login = Login.get_by_login(user_name)
        login.add_to_group(group_name)

        my.description = "Added User '%s' to Group '%s'" \
            % (user_name,group_name)



    def remove_user_from_group(my):
        web = WebContainer.get_web()
        users_to_remove = web.get_form_values("users_to_remove")
        group_name = web.get_form_value("group_name")

        for user_name in users_to_remove:
            login = Login.get_by_login(user_name)
            login.remove_from_group(group_name)

        my.description = "Removed User '%s' to Group '%s'" \
            % ( ", ".join(users_to_remove), group_name)



    def sobject_commit(my):
        from pyasm.web import WebContainer
        web = WebContainer.get_web()
        group_name = web.get_form_value("group_name")
        group = LoginGroup.get_by_group_name(group_name)

        attr = SecurityRulesAttr(group,"access_rules")

        # go through each msg and process
        change_made = False
        msgs = web.get_form_values("sobject_levels")
        for msg in msgs:
            search_type, level = msg.split("|")

            try:
                attr.add_sobject_access(search_type,level)
            except CommandExitException:
                pass
            else:
                change_made = True


        msgs = web.get_form_values("attr_levels")
        for msg in msgs:
            search_type, attr_name, level = msg.split("|")

            try:
                attr.add_attr_access(search_type,attr_name,level)
            except CommandExitException:
                pass
            else:
                change_made = True



        # only commit if a change has bee made
        if change_made:
            group.set_value("access_rules", attr.get_xml() )
            group.commit()
        else:
            raise CommandExitException()


        my.description = "Modified sobject '%s' security settings" % search_type



    def url_commit(my):

        from pyasm.web import WebContainer
        web = WebContainer.get_web()
        group_name = web.get_form_value("group_name")
        group = LoginGroup.get_by_group_name(group_name)

        attr = SecurityRulesAttr(group,"access_rules")

        # go through each msg and process
        change_made = False
        msgs = web.get_form_values("url_levels")
        for msg in msgs:
            url, level = msg.split("|")

            try:
                attr.add_url_access(url,level)
            except CommandExitException:
                pass
            else:
                change_made = True

        # only commit if a change has bee made
        if change_made:
            group.set_value("access_rules", attr.get_xml() )
            group.commit()
        else:
            raise CommandExitException()


        my.description = "Modified url '%s' security settings" % url


    def check_security(my):
        '''give the command a callback that allows it to check security'''
        return True




class SecurityRulesAttr:

    def __init__(my,sobject,name):
        my.sobject = sobject
        my.name = name

        my.xml = sobject.get_xml_value(name, "rules")
        my.root = my.xml.get_root_node()


    def get_xml(my):
        return my.xml.get_xml()


    def _add_access(my, type, key, level):

        # find if a rule for this already exists
        rule = my.xml.get_node("rules/group[@key='%s']" % key)
        if rule != None:
            # if nothing has changed, continue
            access = Xml.get_attribute(rule,"access")
            if level == access:
                raise CommandExitException()
        else:
            rule = my.xml.create_element("group")
            rule.setAttributeNS(None,"key",key)

        # set the access level
        rule.setAttributeNS(None,"type",type)
        rule.setAttributeNS(None,"access",level)
        #my.root.appendChild(rule)
        Xml.append_child(my.root, rule)

        return rule



    def add_url_access(my, url, level):
        return my._add_access("url", url, level)
        

    def get_url_access(my, url):
        access = my.xml.get_value("rules/group[@key='%s']/@access" \
            % url)
        return access




    def add_sobject_access(my, search_type, level):
        return my._add_access("sobject", search_type, level)
        

    def get_sobject_access(my, search_type):
        access = my.xml.get_value("rules/group[@key='%s']/@access" \
            % search_type)
        return access



    def add_attr_access(my, search_type, attr, level):
        # find the group
        group_xpath = "rules/group[@key='%s']" % (search_type)
        group = my.xml.get_node(group_xpath)
        if group == None:
            # add the group (default to view)
            group_level = "view"
            group = my.add_sobject_access(search_type,group_level)


        # get the attr rule
        rule_xpath = "rules/group[@key='%s']/rule[@key='%s']" % (search_type,attr)
        rule = my.xml.get_node(rule_xpath )
        if rule != None:
            # if nothing has changed, continue
            access = Xml.get_attribute(rule,"access")
            if level == access:
                raise CommandExitException()
        else:
            rule = my.xml.create_element("rule")
            rule.setAttributeNS(None,"key",attr)

            #group.appendChild(rule)
            Xml.append_child(group, rule)

            #my.root.appendChild(group)
            Xml.append_child(my.root, group)


        # set the access level
        rule.setAttributeNS(None,"type","attr")
        rule.setAttributeNS(None,"access",level)



    def get_attr_access(my, search_type, attr):
        access = "rules/group[@key='%s']/rule[@key='%s']/@access" \
            % (search_type,attr)
        access = my.xml.get_value(access)
        return access








