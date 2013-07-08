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

__all__ = ['HoudiniBuilder']


from houdini_environment import HoudiniEnvironment
from houdini import Houdini, HoudiniNodeNaming

from pyasm.application.common import SessionBuilder

class HoudiniBuilder(SessionBuilder):
    '''builds a houdini session file'''

    def import_file(my, node_name, path, instantiation='import',use_namespace=True):

        naming = HoudiniNodeNaming(node_name)

        # if there is no node_name name, then just import without namespaces
        if not naming.has_instance():
            # import file into namespace
            if instantiation=='reference':
                created_node = my.app.import_reference(path)
            else:
                created_node = my.app.import_file(path)

        else:
            instance = naming.get_instance()
            asset_code = naming.get_asset_code()

            # import file into namespace
            if instantiation=='reference':
                created_node = my.app.import_reference(path,node_name)
            else:
                created_node = my.app.import_file(path,node_name)


        # select newly created node
        my.app.select(created_node)


        return created_node



    def import_anim(my, node_name, path, created_node=""):
        my.app.import_anim(path, node_name)


    def handle_mel(my, cmd_str):
        print "WARNING: mel: ", cmd_str

    def set_attr(my, node_name, node, current_node_name):
        '''set attribute for the current app'''
        attr = node.getAttribute("attr")
        value = node.getAttribute("value")
        attr_type = node.getAttribute("type")

        if current_node_name:
            node_name_parts = node_name.split('/')
            # /obj/<hou node name>
            node_name_parts[2] = current_node_name
            node_name = '/'.join(node_name_parts)
        my.app.set_attr(node_name,attr,value,attr_type)




