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

    def __init__(my, app_node_name):
        my.app_node_name = app_node_name

        my.data = {}

        from application import Application
        my.app = Application.get()

        my.init()


    def init(my):
        xml = my.app.get_attr(my.app_node_name, my.ATTR_NAME)
        if xml == "":
            xml = "<node/>"

        # FIXME: this is for XSI
        xml = xml.replace("\\n", "\n")

        my.dom = None
        try:
            my.dom = parseString(xml)

        except Exception, e:
            print "Warning: node '%s' has invalid tacticNodeData" % my.app_node_name
            my.clear()
            

    
    def clear(my):
        '''clears the dom by creating an empty one'''
        xml = "<node/>"
        my.dom = parseString(xml)

    def add_node(my, node_name):
        root = my.dom.documentElement
        node = my.dom.createElement(node_name)
        root.appendChild(node)
        return node
        

    def _get_node(my, node_name):
        root = my.dom.documentElement
        nodes = root.childNodes
        for node in nodes:
            if node.__class__.__name__ == "Text":
                continue
            if node.nodeName == node_name:
                return node


    def get_attr(my, node_name, attr):
        node = my._get_node(node_name)
        if not node:
            return ""
        value = node.getAttribute(attr)
        if not value:
            return ""
        else:
            return value


    def set_attr(my, node_name, attr, value):
        node = my._get_node(node_name)
        if not node:
            node = my.add_node(node_name)
        node.setAttribute(attr,value)


    def commit(my):
        xml = my.dom.toxml()
        xml = xml.replace("\n", "\\n")
        xml = xml.replace('"', "'")

        my.app.add_attr(my.app_node_name, my.ATTR_NAME, "string")
        my.app.add_attr(my.app_node_name, my.ATTR_NAME2, "string")
        my.app.set_attr(my.app_node_name, my.ATTR_NAME, xml, "string" )
        my.app.set_attr(my.app_node_name, my.ATTR_NAME2, xml , "string")



    def dump(my):
        print my.dom.toxml()

   
    def create(my):
        '''create the necessary attributes if they do not exists'''
        if not my.app.attr_exists(my.app_node_name, my.ATTR_NAME):
            my.app.add_attr(my.app_node_name, my.ATTR_NAME, type="string")
            
        if not my.app.attr_exists(my.app_node_name, my.ATTR_NAME2):
            my.app.add_attr(my.app_node_name, my.ATTR_NAME2, type="string")


        # initialize the data
        my.init()



    def get_ref_node(my):
        node = my._get_node("ref")
        return node


        



