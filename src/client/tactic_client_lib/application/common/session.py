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

__all__ = ['Session']

import os, sys, urllib, xmlrpclib
from xml.dom.minidom import parseString
from xml.dom.minidom import getDOMImplementation

from tactic_node_util import TacticNodeUtil
from node_data import NodeData
from application import Application


class Session(object):
    '''helper class to introspect the session'''

    def __init__(my):
        my.xml = None
        my.doc = None
        my.root = None

        from tactic_client_lib import TacticServerStub
        my.server = TacticServerStub.get()

        # TODO: pull this out of here!!!
        my.util = TacticNodeUtil()
        my.app = Application.get()

    def introspect(my):
        '''introspect the session and create a session xml from it'''
        # create an xml document
        xml_impl = getDOMImplementation()
        my.doc = xml_impl.createDocument(None, "session", None)
        my.root = my.doc.documentElement

        # go through the tactic
        tactic_nodes = my.util.get_all_tactic_nodes() 
        tactic_nodes.sort()
        for tactic_node in tactic_nodes:

            node_data = NodeData(tactic_node)
            ref_node = node_data.get_ref_node()

            # set some more info on the ref node
            ref_node.setAttribute("tactic_node", tactic_node)
            my.root.appendChild(ref_node)

        my.xml = my.doc.toprettyxml()
        return my.xml


    def get_last(my, pid=None):
        '''Get the last sesson recorded from the last session.  This is useful
        for applications that do not have direct access to the application and
        must go through the database to get this information'''

        # get more info
        if not pid:
            pid = os.getpid()
        login = my.server.get_login()

        search_type = "prod/session_contents"
        filters = []
        filters.append( ["pid", pid] )
        filters.append( ["login", login] )
        limit = 1
        order_bys = ['timestamp desc']
        sessions = my.server.query(search_type, filters, order_bys=order_bys, limit=limit)

        if sessions:
            session = sessions[0]
            my.xml = session.get('session')

            my.doc = parseString(my.xml)
            my.root = my.doc.documentElement

            return sessions
        else:
            my.doc = None
            my.root = None
            my.xml = None
            return None




    def get_snapshots(my):
        '''gets the snapshots that are in the session'''

        # create an xml document
        my.root = my.doc.documentElement

        snapshot_codes = []
        for node in my.root.childNodes:
            if node.nodeName != "ref":
                continue
            snapshot_code = node.getAttribute("snapshot_code")
            snapshot_codes.append(snapshot_code)

        filters = []
        filters.append( ['code', snapshot_codes] )

        snapshots = my.server.query("sthpw/snapshot", filters )
        return snapshots





    def commit(my, xml=None):
        '''commit this to the database'''

        if not xml:
            xml = my.xml

        # get more info
        pid = os.getpid()
        login = my.server.get_login()

        #data = { 'pid': pid, 'login': login, 'data': xml }
        #my.server.insert( search_type, data)

        my.server.commit_session(xml, pid)
        







