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

__all__ = ['MayaBuilder']


import os, sys, urllib

try:
    import xmlrpclib
except:
    from xmlrpc import client as xmlrpclib

from xml.dom.minidom import parseString

from pyasm.application.common import SessionBuilder

from .maya_environment import MayaEnvironment
from .maya_app import Maya, MayaNodeNaming
from .maya_anim_file import MayaAnimFile


class MayaBuilder(SessionBuilder):
    '''builds a maya file'''

    def import_file(self, node_name, path, instantiation='import', use_namespace=True):
        if node_name and self.app.node_exists(node_name):
            print("WARNING: Node '%s' already exists" % node_name)

        naming = MayaNodeNaming(node_name)
        
        # if there is no instance name, then just import without namespaces
        if not use_namespace:
            old_nodes = self.app.get_top_nodes()

            if instantiation == 'reference':
                # reference needs the node_name as a namespace
                # but it can't be the same as a node already in the session
                created_node = self.app.import_reference(path, node_name)
            else:
                # import works with the default namespace
                created_node = self.app.import_file(path)

           
            new_nodes = self.app.get_top_nodes()
            created_nodes = [val for val in new_nodes if val not in old_nodes]
            if not created_nodes:
                created_nodes = []

            # select all the created nodes, so that it can be added to a
            # set if necessary
            self.app.select_none()
            for created_node in created_nodes:
                self.app.select_add(created_node)
        else:
            instance = naming.get_instance()
            asset_code = naming.get_asset_code()

            # the namespace is the instance name
            namespace = instance

            self.app.add_namespace(namespace)
            self.app.set_namespace(namespace)

            contents = self.app.get_namespace_contents()

            # remove namespace if empty
            self.app.set_namespace()
            if contents == None:
                self.app.remove_namespace(namespace)

            # get all of the namespaces
            old = self.app.get_all_namespaces()
            old_nodes = self.app.get_top_nodes()
            sets = self.app.get_sets()
            if sets:
                old_nodes.extend(sets)

            # import file into namespace
            if instantiation == 'reference':
                self.app.import_reference(path,namespace)
            else:
                self.app.import_file(path,namespace)

                # set the user environment
                sandbox_dir = self.get_sandbox_dir()
                basename = os.path.basename(path)
                # DON'T set the project or rename the file
                #self.app.set_user_environment(sandbox_dir, basename)




            # get the two differences to find out which namespace was created
            new = self.app.get_all_namespaces()
            diff = [val for val in new if val not in old]
            if not diff:
                raise Exception("No namespaces created")


            new_nodes = self.app.get_top_nodes()
            sets = self.app.get_sets()
            if sets:
                new_nodes.extend(sets)
            created_nodes = [val for val in new_nodes if val not in old_nodes]

            # get the top node for this asset
            created_node = None
            for created_node in created_nodes:
                # choose the node that contains the asset code
                if created_node.find(":%s" % asset_code) != -1:
                    break

            # select newly created attr
            if created_node:
                self.app.select(created_node)

        return created_node



    def import_anim(self, node_name, path, created_node=""):

        node_naming = self.app.get_node_naming(node_name)
        instance = node_naming.get_instance()

        select = node_name

        # select the node that was created if the variable exists
        if created_node != ""  and created_node != node_name:
            select = created_node

        # check to see if this node_name has a corresponding interface
        interface = "%s_interface" % select
        if self.app.node_exists( interface ):
            select = interface

        # select the node
        self.app.select(select)

        # parse the animation
        anim = MayaAnimFile(path)
        anim.parse()

        # put the animation data into a temp file
        tmp = "%s/temp.anim" % self.get_tmpdir()
        file2 = open(tmp, "w")
        file2.write( anim.get_anim(instance) )
        file2.close()

        # import the file just created
        self.app.import_anim(tmp)
        self.app.import_static(anim.get_static(instance), node_name)

       



