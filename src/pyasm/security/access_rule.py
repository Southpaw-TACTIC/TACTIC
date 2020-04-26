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

__all__ = ["AccessRule", "AccessRuleInGroup", "AccessRuleBuilder"]

import types

from pyasm.common import *
from pyasm.search import *


# DEPRECATED

class AccessRuleException(Exception):
    pass

class AccessRule(SObject):
    '''Treat security rules as a separate handler'''
    SEARCH_TYPE = "sthpw/access_rule"

    def get_primary_key(self):
        return "code"

    def get_foreign_key(self):
        return "access_rule_code"

    def get_by_groups(groups):
        if not groups:
            return []

        access_rule_in_groups = AccessRuleInGroup.get_by_groups(groups)
        if not access_rule_in_groups:
            return []

        codes = [x.get_value("access_rule_code") for x in access_rule_in_groups]
        search = Search(AccessRule)
        search.add_filters("code", codes)

        return search.get_sobjects()

    get_by_groups = staticmethod(get_by_groups)



class AccessRuleInGroup(SObject):
    '''Treat access rules as a separate handler'''
    SEARCH_TYPE = "sthpw/access_rule_in_group"

    def get_by_groups(groups):
        if not groups:
            []

        search = Search(AccessRuleInGroup)

        group_names = [x.get_value("login_group") for x in groups]
        search.add_filters("login_group", group_names)

        return search.get_sobjects()

    get_by_groups = staticmethod(get_by_groups)





class AccessRuleBuilder(object):
    def __init__(self, xml=None):
        if not xml:
            self.xml = Xml()
            self.xml.create_doc("rules")
        else:
            if type(xml) in [types.StringType]:
                self.xml = Xml()
                self.xml.read_string(xml)
            else:
                self.xml = xml
        self.root_node = self.xml.get_root_node()


    def add_rule(self, group, key, access, unique=True):

        node = None
        if isinstance(key, dict):
            sub_paths = ["@%s='%s'"%(k,v) for k,v in key.items()]
            xpath = "rules/rule[@group='%s' and %s]" % (group, ' and '.join(sub_paths))
        else:
            xpath = "rules/rule[@group='%s' and @key='%s']" % (group,key)

            
        if unique:
            node = self.xml.get_node( xpath )
        if node is None:
            node = self.xml.create_element("rule")

        Xml.set_attribute(node, "group", group)
        if isinstance(key, dict):
            for k,v in key.items():
                Xml.set_attribute(node, k, v)
        else:
            Xml.set_attribute(node, "key", key)
        Xml.set_attribute(node, "access", access)

        #self.root_node.appendChild(node)
        Xml.append_child(self.root_node, node)

    def add_default_rule(self, group, access):
        '''add default rule'''
        node = None

        node = self.xml.get_node("rules/rule[@group='%s' and @default]" % group )
        if node == None:
            node = self.xml.create_element("rule")

        Xml.set_attribute(node, "group", group)
        Xml.set_attribute(node, "default", access)

        #self.root_node.appendChild(node)
        Xml.append_child(self.root_node, node)


    def remove_rule(self, group, key):

        node = None
        if isinstance(key, dict):
            sub_paths = ["@%s='%s'"%(k,v) for k,v in key.items()]
            xpath = "rules/rule[@group='%s' and %s]" % (group, ' and '.join(sub_paths))
        else:
            xpath = "rules/rule[@group='%s' and @key='%s']" % (group, key)

        # in case there are multiple manually inserted nodes
        nodes = self.xml.get_nodes(xpath)
        parent_node = self.xml.get_node("rules")
        for node in nodes:
            if node is not None:
                self.xml.remove_child(parent_node, node)

    def update_rule(self, xpath, update_dict):
        '''update the rule with the update_dict'''
        
        # in case there are multiple manually inserted nodes
        nodes = self.xml.get_nodes(xpath)
        parent_node = self.xml.get_node("rules")
        for node in nodes:
            if node is not None:
                for name, value in update_dict.items():
                    Xml.set_attribute(node, name, value)


    def get_default(self, group):
        '''get the default attribute'''
        node = self.xml.get_node("rules/rule[@default and @group='%s']" %group)
        if node is not None:
            return self.xml.get_attribute(node, 'default')
        else:
            return ''


    def to_string(self):
        return self.xml.to_string()


