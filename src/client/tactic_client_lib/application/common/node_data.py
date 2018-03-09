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

_all__ = ["NodeData"]

from xml.dom.minidom import parseString
from xml.dom.minidom import getDOMImplementation



class NodeData(object):
    '''class which stores tactic specific data on the node'''
    ATTR_NAME = "tacticNodeData"
    ATTR_NAME2 = "notes"

    def __init__(self, app_node_name):
        self.app_node_name = app_node_name

        self.data = {}

        from application import Application
        self.app = Application.get()

        self.init()


    def init(self):
        xml = self.app.get_attr(self.app_node_name, self.ATTR_NAME)
        if xml == "":
            xml = "<node/>"

        # FIXME: this is for XSI
        xml = xml.replace("\\n", "\n")

        self.dom = None
        try:
            self.dom = parseString(xml)

        except Exception, e:
            print "Warning: node '%s' has invalid tacticNodeData" % self.app_node_name
            self.clear()
            

    
    def clear(self):
        '''clears the dom by creating an empty one'''
        xml = "<node/>"
        self.dom = parseString(xml)

    def add_node(self, node_name):
        root = self.dom.documentElement
        node = self.dom.createElement(node_name)
        root.appendChild(node)
        return node
        

    def _get_node(self, node_name):
        root = self.dom.documentElement
        nodes = root.childNodes
        for node in nodes:
            if node.__class__.__name__ == "Text":
                continue
            if node.nodeName == node_name:
                return node


    def get_attr(self, node_name, attr):
        node = self._get_node(node_name)
        if not node:
            return ""
        value = node.getAttribute(attr)
        if not value:
            return ""
        else:
            return value


    def set_attr(self, node_name, attr, value):
        node = self._get_node(node_name)
        if not node:
            node = self.add_node(node_name)
        node.setAttribute(attr,value)


    def commit(self):
        xml = self.dom.toxml()
        xml = xml.replace("\n", "\\n")
        xml = xml.replace('"', "'")

        self.app.add_attr(self.app_node_name, self.ATTR_NAME, "string")
        self.app.add_attr(self.app_node_name, self.ATTR_NAME2, "string")
        self.app.set_attr(self.app_node_name, self.ATTR_NAME, xml, "string" )
        self.app.set_attr(self.app_node_name, self.ATTR_NAME2, xml , "string")



    def dump(self):
        print self.dom.toxml()

   
    def create(self):
        '''create the necessary attributes if they do not exists'''
        if not self.app.attr_exists(self.app_node_name, self.ATTR_NAME):
            self.app.add_attr(self.app_node_name, self.ATTR_NAME, type="string")
            
        if not self.app.attr_exists(self.app_node_name, self.ATTR_NAME2):
            self.app.add_attr(self.app_node_name, self.ATTR_NAME2, type="string")


        # initialize the data
        self.init()



    def get_ref_node(self):
        node = self._get_node("ref")
        return node


        



