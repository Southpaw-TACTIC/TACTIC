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

import os, sys, urllib, xmlrpclib
from xml.dom.minidom import parseString
from xml.dom.minidom import getDOMImplementation

from pyasm.application.common import BaseAppInfo, NodeData


class MayaIntrospect:

    def __init__(my):
        my.info = BaseAppInfo.get()
        my.app = my.info.get_app()
        my.impl = my.info.get_app_implementation()
        my.mode = "all"

        my.session_xml = None

    def get_session_xml(my):
        return my.session_xml
        


    def set_mode(my, mode):
        my.mode = mode

    def execute(my):

        node_names = []

        # find out which nodes are of interest
        if my.mode == "select":
            top_nodes = my.app.get_selected_top_nodes()
        else:
            top_nodes = my.app.get_top_nodes()


        # go through each top level node
        for top_node in top_nodes:
            if top_node in ['persp', 'top', 'front', 'side']:
                continue
            node_names.append(top_node)


        node_names.extend( my.app.get_sets() )


        # sort the node_names
        node_names.sort()

        user = my.info.get_user()


        # get the pid of this process
        pid = os.getpid()

        # create an xml document
        impl = getDOMImplementation()
        doc = impl.createDocument(None, "session", None)
        root = doc.documentElement

        for node_name in node_names:
            xml_node = doc.createElement("node")

            node_naming = my.app.get_node_naming(node_name)

            Xml.set_attribute(xml_node, "instance", node_naming.get_instance() )
            Xml.set_attribute(xml_node, "asset_code", node_naming.get_asset_code() )
            Xml.set_attribute(xml_node, "name", node_name)

            for snapshot_type in ("asset", "anim", "set", "shot"):
                snapshot_code = my.impl.get_snapshot_code(node_name, \
                    snapshot_type)
                snapshot_version = my.impl.get_snapshot_attr(node_name, \
                    snapshot_type, "version")
                snapshot_context = my.impl.get_snapshot_attr(node_name, \
                    snapshot_type, "context")


                if snapshot_code != "":
                    Xml.set_attribute(xml_node, "%s_snapshot_code" % snapshot_type, 
                        snapshot_code )
                    Xml.set_attribute(xml_node, "%s_snapshot_version" % snapshot_type, snapshot_version )
                    Xml.set_attribute(xml_node, "%s_snapshot_context" % snapshot_type, snapshot_context )



            #node_data = NodeData(node_name)
            #version = node_data.get_attr("snapshot", "version")
            #if version == None:
            #    version = ""
            #Xml.set_attribute(xml_node, "version", str(version) )

            # find out if this is a reference
            is_reference = my.app.is_reference(node_name)
            if is_reference:
                Xml.set_attribute(xml_node, "reference", "true")
            else:
                Xml.set_attribute(xml_node, "reference", "false")

            root.appendChild(xml_node)

        my.session_xml = root.toprettyxml()





