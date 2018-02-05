############################################################
#
#    Copyright (c) 2011, Southpaw Technology
#                        All Rights Reserved
#
#    PROPRIETARY INFORMATION.  This software is proprietary to
#    Southpaw Technology, and is not to be reproduced, transmitted,
#    or disclosed in any way without written permission.
#
#

__all__ = ['SyncFilter']


import tacticenv

from pyasm.common import Environment, Xml, TacticException
from pyasm.biz import Project
from pyasm.search import SearchType, Search
from pyasm.security import AccessManager

import os, codecs


class SyncFilter(object):

    def __init__(self, **kwargs):
        self.kwargs = kwargs

        self.log = self.kwargs.get("transaction")
        self.rules = self.kwargs.get("rules")
        self.message = ""


    def execute(self):
        log = self.log
        rules = self.rules

        # Give rules.  Only notes will get through
        # we need heirarchical rules.  This will ensure that only notes
        # for project/assets will pass
        # Here, the second one is much more difficult to do.
        rulesXXX = '''
        <rule group='heirarchy' key='project/asset.sthpw/note' access='allow'/>
        <rule group='heirarchy' key="project/asset.sthpw/note['assigned','beth']" access='allow'/>"
        '''

        access_manager = AccessManager()
        access_manager.add_xml_rules(rules)


        # filter out project
        namespace = log.get_value("namespace")
        key1 = { 'code': namespace }
        key2 = { 'code': '*' }
        keys = [key1, key2]
        if not access_manager.check_access("project", keys, "allow", default="deny"):
            self.filtered_xml = Xml()
            self.filtered_xml.read_string("<transaction/>")
            self.message = "Transaction prevented due to project restriction"
            return


        # filter the transaction against the security model
        xml = log.get_xml_value("transaction")

        self.filtered_xml = Xml()
        self.filtered_xml.create_doc("transaction")
        root2 = self.filtered_xml.get_root_node()

        nodes = xml.get_nodes("transaction/*")
        num_nodes = len(nodes)
        count = 0


        for node in nodes:
            if Xml.get_node_name(node) ==  "sobject":
                search_type = xml.get_attribute(node, "search_type")
                parts = search_type.split("?")
                search_type = parts[0]

                # filter search types
                key1 = { 'code': search_type }
                key2 = { 'code': "*" }
                keys = [ key1, key2 ]
                if not access_manager.check_access("search_type", keys, "allow", default="deny"):
                    continue

                # check hierachical rule
                parent_type = xml.get_attribute(node, "parent_type")
                key = "%s.%s" % (parent_type, search_type)
                
                self.filtered_xml.append_child(root2, node)
                count += 1
                
            else:
                self.filtered_xml.append_child(root2, node)
                count += 1

        if len(nodes) != 0 and len(self.filtered_xml.get_nodes("transaction/*")) == 0:
            self.message = "All actions filtered due to security restrictions (%s actions)" % num_nodes



    def get_filtered_xml(self):
        return self.filtered_xml

    def get_message(self):
        return self.message


if __name__ == '__main__':

    from pyasm.security import Batch
    Batch(project_code='new_project')

    filter = SyncFilter()
    filter.execute()




