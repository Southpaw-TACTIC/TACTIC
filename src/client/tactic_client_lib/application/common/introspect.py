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

__all__ = ['Introspect']

import os, sys, urllib, xmlrpclib
from xml.dom.minidom import parseString
from xml.dom.minidom import getDOMImplementation

from tactic_node_util import TacticNodeUtil
from node_data import NodeData
from application import Application


class Introspect(object):
    '''helper class to introspect the session'''

    def __init__(my):
        # TODO: pull this out of here!!!
        my.util = TacticNodeUtil()
        my.app = Application.get()

    def execute(my):


        # create an xml document
        xml_impl = getDOMImplementation()
        doc = xml_impl.createDocument(None, "session", None)
        root = doc.documentElement

        # go through the tactic
        tactic_nodes = my.util.get_all_tactic_nodes() 
        tactic_nodes.sort()
        for tactic_node in tactic_nodes:
            node_data = NodeData(tactic_node)
            ref_node = node_data.get_ref_node()
            root.appendChild(ref_node)

        my.xml = doc.toxml()
        return my.xml


    def commit(my, xml=None):

        if not xml:
            xml = my.xml

        from tactic_client_lib import TacticServerStub
        my.server = TacticServerStub.get()

        search_type = "prod/session_contents"

        # get more info
        pid = os.getpid()
        login = my.server.get_login()

        data = { 'pid': pid, 'login': login, 'data': xml }

        my.server.insert( search_type, data)
        







