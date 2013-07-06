###########################################################
#
# Copyright (c) 2005, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
# AUTHOR:
#     Remko Noteboom
#
#

_all__ = ["NodeData"]


from xml.dom.minidom import parseString


class NodeData:
    '''class which tactic specific data on the node
    '''
    ATTR_NAME = "tacticNodeData"

    def __init__(my, node_name):
        my.node_name = node_name

        # get the attribute info
        from common import TacticInfo
        my.info = TacticInfo.get()
        my.app = my.info.get_app()
        xml = my.app.get_attr(node_name, my.ATTR_NAME)

        print xml

        try:
            dom = parseString(xml)
            root = dom.documentElement
            nodes = root.childNodes
        except Exception, e:
            print "Warning: node '%s' has invalid tacticNodeData" % node_name
        


    def get_value(my, name):
        return "pig"




