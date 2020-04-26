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

from common import *


class Introspect(object):

    def __init__(self):
        self.info = TacticInfo.get()
        self.app = self.info.get_app()
        self.impl = self.info.get_app_implementation()
        self.mode = "all"

    def set_mode(self, mode):
        self.mode = mode

    def execute(self):

        node_names = []

        # find out which nodes are of interest
        if self.mode == "select":
            top_nodes = self.app.get_selected_top_nodes()
        else:
            top_nodes = self.app.get_top_nodes()


        # go through each top level node
        for top_node in top_nodes:
            if top_node in ['persp', 'top', 'front', 'side']:
                continue
            node_names.append(top_node)

        set_names = self.app.get_sets()
        node_names.extend( set_names )

        # sort the node_names
        node_names.sort()

        user = self.info.get_user()


        # get the pid of this process
        pid = os.getpid()

        # create an xml document
        xml_impl = getDOMImplementation()
        doc = xml_impl.createDocument(None, "session", None)
        root = doc.documentElement


        # get the name of the file
        file_path = self.app.get_file_path()
        file_node = doc.createElement("file")
        file_node.setAttribute("name", os.path.basename(file_path))
        file_node.setAttribute("dir", os.path.dirname(file_path))
        root.appendChild(file_node)

        project_node = doc.createElement("project")
        project_node.setAttribute("dir", self.app.get_project() )
        root.appendChild(project_node)

        # max it drill down is 4 levels to discover tactic node
        self.process_nodes(doc, node_names, level=4)


        # add namespace info
        if self.app.name == "maya":
            
            cur_namespace = self.app.get_namespace_info('-cur')
            xml_node = doc.createElement("namespace")
            xml_node.setAttribute("name", cur_namespace)
            xml_node.setAttribute("current", "true")
            root.appendChild(xml_node)


            namespaces = self.app.get_namespace_info()
            if namespaces:
                for namespace in namespaces:
                    xml_node = doc.createElement("namespace")
                    xml_node.setAttribute("name", namespace)
                    
                    root.appendChild(xml_node)

        # dump out the xml
        xml = doc.toprettyxml()

        # inform the server of the information of this session
        server = self.info.get_xmlrpc_server()
        ticket = self.info.get_ticket()
        project_code = self.info.get_project_code()
        server.update_session(ticket, project_code, user, pid, xml)


    def process_nodes(self, doc, node_names, is_top_node=True, level=0):
        if level < 0:
            return
        
        root = doc.documentElement
        for node_name in node_names:
            #last_ns = ''
            xml_node = doc.createElement("node")
            root.appendChild(xml_node)
            self.process_node(doc, xml_node, node_name, is_top_node, level)

            # get all of the tactic sub references.
            # 
            # The problem here is that the rig can be huge, containing thousands
            # of nodes.  Currently, this method needs to go through every node
            # to find a tactic subnode.  This is extremely slow.  There is
            # no way in maya to say: give me all the nodes with the attribute
            # "tacticNodeData"
            #
            # What is needed is a much faster mechanism to find tactic nodes.
            # Alternatives:
            #   custom node: means all installations need a plugin
            #   predetermined name: this may necessary
            #
            # Can we assume that all tactic nodes have the name = asset_code 
            # as a base (not namespace)? ... no, we don't know which assets
            # may be present.
            #
            # Can we go backwards from the refence node?
            #
            find_sub_refs = True
            if find_sub_refs:
                sub_refs = self.app.get_reference_nodes(node_name, recursive=True)
                for sub_ref in sub_refs:
                    sub_node = doc.createElement("ref")
                    self.process_node(doc, sub_node, sub_ref, is_top_node=False, level=None)
                    xml_node.appendChild(sub_node)
                    '''
                    node_naming2 = self.app.get_node_naming(sub_ref)
                    instance2 = node_naming2.get_instance()

                    sub_path = self.app.get_reference_path(sub_ref)
                    sub_asset_snapshot_code = self.impl.get_snapshot_code(sub_ref,"asset")
                    sub_anim_snapshot_code = self.impl.get_snapshot_code(sub_ref,"anim")

                    sub_node = doc.createElement("ref")
                    sub_node.setAttribute("asset_snapshot_code", sub_asset_snapshot_code)
                    sub_node.setAttribute("anim_snapshot_code", sub_anim_snapshot_code)
                    sub_node.setAttribute("instance", instance2)
                    sub_node.setAttribute("node_name", sub_ref)
                    sub_node.setAttribute("path", sub_path)

                    xml_node.appendChild(sub_node)
                    '''




    def process_node(self, doc, xml_node, node_name, is_top_node=True, level=0):
        # find out if this is a reference
        is_reference = self.app.is_reference(node_name)
        if is_reference:
            xml_node.setAttribute("reference", "true")
        else:
            xml_node.setAttribute("reference", "false")



        plain_node_name = node_name

        # this if logic may be commented out for faster performance
        # but we will drop the support for referenced instances grouped under
        # non tactic nodes
        '''
        if is_reference:
            node_naming = self.app.get_node_naming(node_name)
            last_ns = node_naming.get_namespace()
            # when a node is referenced in, we should ignore that namespace
            plain_node_name = node_name.replace('%s:'%last_ns, '')
        '''
        # check if it is a tactic node
        if self.app.is_tactic_node(node_name):
            xml_node.setAttribute("tactic_node", "true")
        else:
            xml_node.setAttribute("tactic_node", "false")
            
            # check its children until it hits a node with namespace
            if ':' not in plain_node_name and not self.app.is_set(plain_node_name):
                children = self.app.get_children(node_name)
                if children:
                    if level != None:
                        level -= 1
                    self.process_nodes(doc, children, is_top_node=False, level=level)

                # all children non tactic nodes are not recorded
                # NOTE: this is critical so as not to blow up the server
                # by sending huge data structures over.
                if not is_top_node:
                    return
               

        type = self.app.get_node_type(node_name)
        if not type:
            raise Exception("Type for node '%s' is None" % node_name)
        xml_node.setAttribute("type", type)
        node_naming = self.app.get_node_naming(node_name)
        asset_code =  node_naming.get_asset_code()
        namespace = node_naming.get_instance()

        # FIXME: this namespace could be the name of the node
        # if it doesn't have a namespace
        xml_node.setAttribute("namespace", namespace)
        xml_node.setAttribute("asset_code", asset_code)
        xml_node.setAttribute("name", node_name)



        # go through the various snapshot types and set the information
        is_instance_set = False
        for snapshot_type in ("asset", "anim", "set", "shot"):
            snapshot_asset_code = ''
            # special case for set
            if snapshot_type == 'set':
                snapshot_asset_code = self.impl.get_snapshot_attr(node_name, \
                snapshot_type, "asset_code")

            # override the instance name for anim snapshots
            #if snapshot_type == 'anim':
            instance = self.impl.get_snapshot_attr(node_name, \
                snapshot_type, "instance")
            if instance:
                xml_node.setAttribute("instance", instance )
                is_instance_set = True
            elif not is_instance_set:
                xml_node.setAttribute("instance", namespace )

                
            snapshot_code = self.impl.get_snapshot_code(node_name, \
                snapshot_type)
            
            snapshot_version = self.impl.get_snapshot_attr(node_name, \
                snapshot_type, "version")
            snapshot_context = self.impl.get_snapshot_attr(node_name, \
                snapshot_type, "context")
            snapshot_revision = self.impl.get_snapshot_attr(node_name, \
                snapshot_type, "revision")

            if snapshot_asset_code:
                xml_node.setAttribute("%s_asset_code" % snapshot_type, 
                    snapshot_asset_code )
            if snapshot_code:
                xml_node.setAttribute("%s_snapshot_code" % snapshot_type, 
                    snapshot_code )
                xml_node.setAttribute("%s_snapshot_version" % snapshot_type, snapshot_version )
                xml_node.setAttribute("%s_snapshot_context" % snapshot_type, snapshot_context )
                xml_node.setAttribute("%s_snapshot_revision" % snapshot_type, snapshot_revision )



def introspect():
    introspect = Introspect()
    introspect.execute()


def introspect_select():
    introspect = Introspect()
    introspect.set_mode("select")
    introspect.execute()



if __name__ == '__main__':
    executable = sys.argv[0]
    args = sys.argv[1:]

    introspect = Introspect()
    introspect.execute()





