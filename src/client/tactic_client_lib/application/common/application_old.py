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


__all__ = ['Application', 'AppException']

import sys, types

from node_data import NodeData
from app_environment import AppException


class Application(object):
    '''base class defining interface for 3D applications'''

    def __init__(self, init=True):

        self.buffer_flag = False
        self.buffer = None

        self.verbose = False


    def message(self, message):
        print message


    def start_buffer(self):
        '''starts a buffer which redirects commands to a buffer'''
        self.buffer_flag = True
        self.buffer = []

    def end_buffer(self):
        self.buffer_flag = False

    def get_buffer(self):
        return self.buffer

    def set_verbose(self, flag=True):
        self.verbose = flag




    def cleanup(self):
        '''Note: necessary in Houdini'''
        pass


    def get_node_data(self, node_name):
        return NodeData(node_name)

    # Common operations
    #   These abstract and interface to appplication version so that
    # implementations can made.  As few basic operations as possible
    # into the application are defined to simplify porting.
    def is_tactic_node(self, node):
        raise AppException("Function: 'is_tactic_node()' must be overriden")

    def set_project(self, project_dir):
        raise AppException("Function: 'set_project()' must be overriden")

    def get_project(self):
        raise AppException("Function: 'get_project()' must be overriden")

    def get_var(self):
        raise AppException("Function: 'get_var()' must be overriden")

    def get_node_type(self, node_name):
        raise AppException("Function: 'get_node_type()' must be overriden")
    
    def get_children(self, node_name):
        pass
    
    # action functions
    def set_attr(self, node, attr, value, attr_type=""):
        pass

    def select(self, node):
        raise AppException("Function: 'select()' must be overriden")

    def select_add(self, node):
        pass
    
    def select_none(self):
        pass

    def select_restore(self, nodes):
        pass
        
    def select_hierarchy(self, node): 
        pass

    
    # interaction with files
    def import_file(self, path, namespace=":"):
        '''import a file into the session'''
        pass


    def import_reference(self, path, namespace=":"):
        '''load using renferences'''
        pass

    def replace_reference(self, node_name, path, top_reference=True):
        '''load using renferences'''
        pass



    def is_reference(self, instance):
        '''detect whether an instance is a reference or not'''
        pass

    def is_keyed(self, node_name, attr):
        '''detect whether an instance is keyed or not'''
        pass

    def import_static(self, buffer, node_name):
        '''import unkeyed values'''
        pass
        
    def import_anim(self, path, namespace=":"):
        '''load in animation'''
        pass


    def export_anim(self, path, namespace=":"):
        '''export the animation'''


    def save(self, path, file_type=None):
        '''save the file'''
        raise AppException("Function: 'save()' must be overriden")

    def load(self, path):
        '''load the file'''
        raise AppException("Function: 'load()' must be overriden")

    def rename(self, path):
        '''rename the file'''
        # this is harmless if it doesn't do anything
        pass


    def export_node(self, node_name, context, dir=None, filename="", preserve_ref=None):
        '''export a top node'''
        pass

    def save_node(self, node_name, dir=None):
        '''use file/save for a particular node (saves whole file instead
        of using export'''
        pass

    def get_file_path(self):
        '''returns the path of the last save filename'''
        raise AppException("Function: 'get_file_path()' must be overriden")



    # namespace commands
    def set_namespace(self, namespace=":"):
        pass

    def add_namespace(self, namespace):
        pass

    def remove_namespace(self, namespace):
        pass

    def namespace_exists(self, namespace):
        pass

    def get_namespace_info(self):
        pass


    def get_namespace_contents(self):
        '''retrieves the contents of the current namespace'''
        return []

    def get_all_namespaces(self):
        return []



    def rename_node(self, node_name, new_name):
        pass



    # set functions
    def get_sets(self):
        return []

    def is_set(self, node_name):
        if node_name in self.get_sets():
            return True
        else:
            return False


    def create_set(self, node_name):
        pass
        
    def add_to_set(self, set_name, node_name):
        pass

    def get_nodes_in_set(self, set_name):
        pass





    # information retrieval functions.  Requires an open Maya session
    def node_exists(self,node):
        pass

    def get_nodes_by_type(self, type):
        pass



    def get_selected_node(self):
        nodes = self.get_selected_nodes()
        if nodes:
            return nodes[0]
        else:
            return None


    def get_selected_nodes(self):
        pass


    def get_selected_top_nodes(self):
        raise AppException("Function: 'get_selected_top_nodes()' must be overriden")


    def get_top_nodes(self):
        raise AppException("Function: 'get_top_nodes()' must be overriden")



    def get_reference_nodes(self, top_node, recursive=False):
        '''gets all of the references under a single dag node'''
        return []


    def get_reference_path(self, node):
        pass




    def add_node(self, type, node_name, unique=False):
        '''return name of node added'''
        pass


    # attributes
    def add_attr(self, node, attribute, type="long"):
        pass


    def attr_exists(self, node, attribute):
        '''return True or False'''
        raise AppException("Function: 'attr_exists()' must be overriden")


    def get_attr(self, node, attribute):
        pass

    def get_attr_type(self, node, attribute):
        pass

    def get_all_attrs(self, node):
        pass

    def get_attr_default(self, node, attr):
        pass

    # layers
    def get_all_layers(self):
        return []


    def get_layer_nodes(self):
        '''gets all of the TACTIC nodes in a layer'''
        return []


    def set_user_environment(self, sandbox_dir, basename):
        '''gives the opportunity to let TACTIC set the user envrionment based
        on the sandbox dir.  It is safe not to use this for a given application
        '''
        pass




class AppException(Exception):
    '''Used by different applications for raising exceptions'''
    pass

