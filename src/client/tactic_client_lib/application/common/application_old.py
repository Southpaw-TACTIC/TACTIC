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

    def __init__(my, init=True):

        my.buffer_flag = False
        my.buffer = None

        my.verbose = False


    def message(my, message):
        print message


    def start_buffer(my):
        '''starts a buffer which redirects commands to a buffer'''
        my.buffer_flag = True
        my.buffer = []

    def end_buffer(my):
        my.buffer_flag = False

    def get_buffer(my):
        return my.buffer

    def set_verbose(my, flag=True):
        my.verbose = flag




    def cleanup(my):
        '''Note: necessary in Houdini'''
        pass


    def get_node_data(my, node_name):
        return NodeData(node_name)

    # Common operations
    #   These abstract and interface to appplication version so that
    # implementations can made.  As few basic operations as possible
    # into the application are defined to simplify porting.
    def is_tactic_node(my, node):
        raise AppException("Function: 'is_tactic_node()' must be overriden")

    def set_project(my, project_dir):
        raise AppException("Function: 'set_project()' must be overriden")

    def get_project(my):
        raise AppException("Function: 'get_project()' must be overriden")

    def get_var(my):
        raise AppException("Function: 'get_var()' must be overriden")

    def get_node_type(my, node_name):
        raise AppException("Function: 'get_node_type()' must be overriden")
    
    def get_children(my, node_name):
        pass
    
    # action functions
    def set_attr(my, node, attr, value, attr_type=""):
        pass

    def select(my, node):
        raise AppException("Function: 'select()' must be overriden")

    def select_add(my, node):
        pass
    
    def select_none(my):
        pass

    def select_restore(my, nodes):
        pass
        
    def select_hierarchy(my, node): 
        pass

    
    # interaction with files
    def import_file(my, path, namespace=":"):
        '''import a file into the session'''
        pass


    def import_reference(my, path, namespace=":"):
        '''load using renferences'''
        pass

    def replace_reference(my, node_name, path, top_reference=True):
        '''load using renferences'''
        pass



    def is_reference(my, instance):
        '''detect whether an instance is a reference or not'''
        pass

    def is_keyed(my, node_name, attr):
        '''detect whether an instance is keyed or not'''
        pass

    def import_static(my, buffer, node_name):
        '''import unkeyed values'''
        pass
        
    def import_anim(my, path, namespace=":"):
        '''load in animation'''
        pass


    def export_anim(my, path, namespace=":"):
        '''export the animation'''


    def save(my, path, file_type=None):
        '''save the file'''
        raise AppException("Function: 'save()' must be overriden")

    def load(my, path):
        '''load the file'''
        raise AppException("Function: 'load()' must be overriden")

    def rename(my, path):
        '''rename the file'''
        # this is harmless if it doesn't do anything
        pass


    def export_node(my, node_name, context, dir=None, filename="", preserve_ref=None):
        '''export a top node'''
        pass

    def save_node(my, node_name, dir=None):
        '''use file/save for a particular node (saves whole file instead
        of using export'''
        pass

    def get_file_path(my):
        '''returns the path of the last save filename'''
        raise AppException("Function: 'get_file_path()' must be overriden")



    # namespace commands
    def set_namespace(my, namespace=":"):
        pass

    def add_namespace(my, namespace):
        pass

    def remove_namespace(my, namespace):
        pass

    def namespace_exists(my, namespace):
        pass

    def get_namespace_info(my):
        pass


    def get_namespace_contents(my):
        '''retrieves the contents of the current namespace'''
        return []

    def get_all_namespaces(my):
        return []



    def rename_node(my, node_name, new_name):
        pass



    # set functions
    def get_sets(my):
        return []

    def is_set(my, node_name):
        if node_name in my.get_sets():
            return True
        else:
            return False


    def create_set(my, node_name):
        pass
        
    def add_to_set(my, set_name, node_name):
        pass

    def get_nodes_in_set(my, set_name):
        pass





    # information retrieval functions.  Requires an open Maya session
    def node_exists(my,node):
        pass

    def get_nodes_by_type(my, type):
        pass



    def get_selected_node(my):
        nodes = my.get_selected_nodes()
        if nodes:
            return nodes[0]
        else:
            return None


    def get_selected_nodes(my):
        pass


    def get_selected_top_nodes(my):
        raise AppException("Function: 'get_selected_top_nodes()' must be overriden")


    def get_top_nodes(my):
        raise AppException("Function: 'get_top_nodes()' must be overriden")



    def get_reference_nodes(my, top_node, recursive=False):
        '''gets all of the references under a single dag node'''
        return []


    def get_reference_path(my, node):
        pass




    def add_node(my, type, node_name, unique=False):
        '''return name of node added'''
        pass


    # attributes
    def add_attr(my, node, attribute, type="long"):
        pass


    def attr_exists(my, node, attribute):
        '''return True or False'''
        raise AppException("Function: 'attr_exists()' must be overriden")


    def get_attr(my, node, attribute):
        pass

    def get_attr_type(my, node, attribute):
        pass

    def get_all_attrs(my, node):
        pass

    def get_attr_default(my, node, attr):
        pass

    # layers
    def get_all_layers(my):
        return []


    def get_layer_nodes(my):
        '''gets all of the TACTIC nodes in a layer'''
        return []


    def set_user_environment(my, sandbox_dir, basename):
        '''gives the opportunity to let TACTIC set the user envrionment based
        on the sandbox dir.  It is safe not to use this for a given application
        '''
        pass




class AppException(Exception):
    '''Used by different applications for raising exceptions'''
    pass

