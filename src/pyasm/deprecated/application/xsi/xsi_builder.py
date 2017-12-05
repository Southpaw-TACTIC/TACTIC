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

__all__ = ['XSIBuilder']


from xsi_environment import XSIEnvironment
from xsi import XSI, XSINodeNaming

from pyasm.application.common import SessionBuilder

class XSIBuilder(SessionBuilder):
    '''builds a xsi session file'''

    def import_file(my, node_name, path, instantiation='import', use_namespace=True):

        naming = XSINodeNaming(node_name)

        # if there is no node_name name, then just import without namespaces
        if not naming.has_instance():
            # import file into namespace
            if instantiation == 'reference':
                created_node = my.app.import_reference(path)
            else:
                created_node = my.app.import_file(path)

        else:
            # import file into namespace
            if instantiation == 'reference':
                created_node = my.app.import_reference(path,node_name)
            else:
                created_node = my.app.import_file(path,node_name)

        # FIXME: created node name is not always node_name
        # select newly created node
        my.app.select(created_node)

        return created_node



    def import_anim(my, node_name, path, created_node=""):
        my.app.import_anim(path, node_name)


    def set_attr(my, node_name, node):
        '''set attribute for the current app'''
        attr = node.getAttribute("attr")
        value = node.getAttribute("value")
        attr_type = node.getAttribute("type")
        
        file_range = node.getAttribute("file_range")
        extra_data = {"file_range": file_range}
        my.app.set_attr(node_name,attr,value,attr_type, extra_data)





