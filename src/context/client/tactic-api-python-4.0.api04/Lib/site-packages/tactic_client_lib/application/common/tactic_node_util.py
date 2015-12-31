###########################################################
#
# Copyright (c) 2005-2008, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#

__all__ = ['TacticNodeUtil']


import xmlrpclib, os, shutil

from node_data import NodeData


# importing 8.5 maya module
try:
    import maya
except:
    print("WARNING: module MayaApplication requires 'maya' module")


class TacticNodeUtil(object):
    '''This class encapsulates functionality needed interact with information
    to communicate with any application.'''

    def __init__(my):
        import maya.standalone
        maya.standalone.initialize( name='python' )
        import maya.cmds, maya.mel

        from tactic_client_lib.application.maya import Maya
        my.app = Maya()
     

    def is_tactic_node(my, node_name):
        '''Determines whether a particular node is a tactic node'''
        pass

   

    def get_all_tactic_nodes(my):
        '''Gets all of the Tactic nodes in the session
        @return
        a list of all tactic node names
        '''

        tactic_nodes = []
        nodes = my.app.get_nodes_by_name("tactic_*")

        # go through each node an make sure that the attribute
        # exists
        for node in nodes:
            if my.is_tactic_node(node):
                tactic_nodes.append(node)

        return tactic_nodes


    def is_tactic_node(my, node_name):
        '''determines whether the given node is a tactic node
        '''
        attribute = "tacticNodeData"
        exists = my.mel("attributeExists %s %s" % (attribute, node_name))
        if not exists:
            return False
        else:
            return True



        
                

    #
    # action functions
    #
    def create_default_node(my, node_name, search_key=None, context=None):
        '''Creates a default template structure when loading a context
        that has no snapshots associated with it
        
        @params 
        node_name: the name of the node to be created
        search_key: a search_key representing the sobject that this node belongs
            to

        @return
        the name of the tactic node created
        '''

        # create the node
        type = "transform"
        node_name = my.app.add_node(node_name, type)

        # create the tactic node
        tactic_type = "transform"
        tactic_node_name = "tactic_%s" % node_name
        tactic_node_name = my.app.add_node(tactic_node_name, tactic_type)


        # add the tacticNodeData attribute and record the search type
        node_data = NodeData(tactic_node_name)
        if search_key:
            node_data.set_attr("ref", "search_key", search_key)
        if context:
            node_data.set_attr("ref", "context", context)
        node_data.commit()

        # attache the tactic node to the node
        my.mel("parent %s %s" % (tactic_node_name, node_name) )

        return tactic_node_name



    def add_snapshot_to_node(my, tactic_node_name, snapshot):
        snapshot_code = snapshot.get('code')
        search_type = snapshot.get('search_type')
        search_id = snapshot.get('search_id')
        context = snapshot.get('context')
        version = snapshot.get('version')
        revision = snapshot.get('revision')
        
        node_data = NodeData(tactic_node_name)
        node_data.set_attr("ref", "snapshot_code", snapshot_code)
        node_data.set_attr("ref", "search_type", search_type)
        node_data.set_attr("ref", "search_id", search_id)
        node_data.set_attr("ref", "context", context)
        node_data.set_attr("ref", "version", version)
        node_data.set_attr("ref", "revision", revision)

        node_data.commit()



    def get_search_key(my, tactic_node_name):
        '''gets the snapshot data on a particular tactic node
        <node>
          <ref context='model' version='3' search_type='prod/asset?project=bar' search_id='4'/>
        </node>

        '''
        node_data = NodeData(tactic_node_name)
        search_type = node_data.get_attr("ref", "search_key")
        return search_type

    def get_context(my, tactic_node_name):
        '''gets the snapshot data on a particular tactic node
        <node>
          <ref context='model' version='3' search_type='prod/asset?project=bar' search_id='4'/>
        </node>

        '''
        node_data = NodeData(tactic_node_name)
        search_type = node_data.get_attr("ref", "context")
        return search_type









    def mel(my, cmd, verbose=None):
        '''Excecute a mel command (TEMPORARY - use maya specific)'''
        return maya.mel.eval(cmd)






class SnapshotXml(object):
    '''Series of utilities to parse the snapshot xml'''
    
    def __init__(my, snapshot_xml):
        my.snapshot_xml = snapshot_xml





