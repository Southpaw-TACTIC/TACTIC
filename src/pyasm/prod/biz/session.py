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

__all__ = ['SessionContents']

import types

from pyasm.common import *
from pyasm.search import *
from pyasm.biz import Snapshot


class SessionContents(SObject):

    SEARCH_TYPE = "prod/session_contents"

    def __init__(my, search_type, columns=None, result=None, remote=False, fast_data=None):
        super(SessionContents,my).__init__(search_type, columns, result, remote, fast_data)
        my.data_xml = None
        my.nodes = None
        my.asset_mode = False


    def set_asset_mode(my, asset_mode=True):
        my.asset_mode = asset_mode


    def is_tactic_node(my, node_name):
        if type(node_name) in types.StringTypes:
            node = my.get_node(node_name)
        else:
            node = node_name

        value = Xml.get_attribute(node, "tactic_node")
        if value == "false":
            return False
        else:
            return True


    def get_node_type(my, node_name):
        node = my.get_node(node_name)
        value = Xml.get_attribute(node, "type")
        return value



    def get_version(my, node_name, asset_code=None, type='asset'):
        node = None
       
        if my.asset_mode:
            #node = my.get_node_by_asset_code(asset_code, node_name)
            node = my.get_node_by_asset_code(asset_code)
        elif node_name:
            node = my.get_node(node_name)
        else:
            raise SObjectException('Both node_name and snapshot are None')
            
        if node is None:
            return 0
        version = Xml.get_attribute(node, "%s_snapshot_version" %type)
        if version in [None, "None", ""]:
            return 0
        return int(version)


    def get_asset_version(my, node_name, asset_code=None):
        return my.get_version(node_name, asset_code=None, type='asset')

    def get_set_version(my, node_name, asset_code=None):
        return my.get_version(node_name, asset_code=None, type='set')

    def get_shot_version(my, node_name, asset_code=None):
        return my.get_version(node_name, asset_code=None, type='shot')

    def get_anim_version(my, node_name, asset_code=None):
        return my.get_version(node_name, asset_code=None, type='anim')
    
    def get_context(my, node_name, asset_code=None, type='asset'):

        node = None

        if my.asset_mode:
            node = my.get_node_by_asset_code(asset_code)
        elif node_name:
            node = my.get_node(node_name)

        else:
            raise SObjectException('Both node_name and asset_code are None')

        if node is None:
            return ""

        return Xml.get_attribute(node, "%s_snapshot_context" %type)


    def get_asset_context(my, node_name, asset_code=None):
        return my.get_context(node_name, asset_code=None, type='asset')

    def get_set_context(my, node_name, asset_code=None):
        return my.get_context(node_name, asset_code=None, type='set')

    def get_shot_context(my, node_name, asset_code=None):
        return my.get_context(node_name, asset_code=None, type='shot')

    def get_anim_context(my, node_name, asset_code=None):
        return my.get_context(node_name, asset_code=None, type='anim')


    def get_revision(my, node_name, asset_code=None, type='asset'):

        node = None

        if my.asset_mode:
            node = my.get_node_by_asset_code(asset_code)
        elif node_name:
            node = my.get_node(node_name)

        else:
            raise SObjectException('Both node_name and asset_code are None')

        if node is None:
            return ""


        return Xml.get_attribute(node, "%s_snapshot_revision" %type)


    def get_asset_revision(my, node_name, asset_code=None):
        return my.get_revision(node_name, asset_code=None, type='asset')

    def get_set_revision(my, node_name, asset_code=None):
        return my.get_revision(node_name, asset_code=None, type='set')

    def get_shot_revision(my, node_name, asset_code=None):
        return my.get_revision(node_name, asset_code=None, type='shot')

    def get_anim_revision(my, node_name, asset_code=None):
        return my.get_revision(node_name, asset_code=None, type='anim')




    def is_reference(my, node_name):
        node = my.get_node(node_name)
        if node == None:
            return 0
        is_reference = Xml.get_attribute(node, "reference")
        if is_reference == "false":
            return False
        else:
            return True


    def get_snapshot_code(my, node_name, snapshot_type="asset"):
        node = my.get_node(node_name)
        if node is None:
            return ""

        snapshot_code = Xml.get_attribute(node, "%s_snapshot_code" % snapshot_type)
        return snapshot_code


    def get_snapshot(my, node_name, snapshot_type="asset"):
        ''' use this only if the info is not already in the
            session_contents table'''
        snapshot_code = my.get_snapshot_code(node_name, snapshot_type)
        if snapshot_code == "":
            return None
        return Snapshot.get_by_code(snapshot_code)


    def get_snapshot_codes(my, snapshot_type="asset"):
        '''get all of the snapshots for this session'''
        xml = my._get_data()
        xpath = "session/node/@asset_snapshot_code"
        snapshot_codes = xml.get_values(xpath)
        return snapshot_codes



    def get_node(my, node_name):
        xml = my._get_data()
        node = my.nodes.get(node_name)
        #node = xml.get_node("session/node[@name='%s']" % node_name)
        # Backwards compatibility: if not, try instance
        #if node is None:
        #    nodes = xml.get_nodes("session/node[@instance='%s']" % node_name)
        #    for node in nodes:
        #        if my.is_tactic_node(node):
        #            return node


        return node




    def get_node_by_asset_code(my, asset_code, node_name=None):
        '''a less stringent way of finding if an asset exists in a session 
            node_name name is not mandatory'''
        xml = my._get_data()
        xpath = "session/node[@asset_code='%s' and @tactic_node='true']" % asset_code
        if node_name:
            xpath ="session/node[@asset_code='%s' and @name='%s' and @tactic_node='true']" \
                % (asset_code, node_name)
        node = xml.get_node(xpath)
        if node is not None:
            return node

    def get_node_by_snapshot(my, snapshot):
        # this is used for finding if a node defined in asset_history is loaded
        # node_name name is not used
        xml = my._get_data()
        
        type = snapshot.get_value('snapshot_type')
        if type == 'anim_export':
            type = 'anim'
        node = xml.get_node("session/node[@%s_snapshot_code='%s']" % \
                (type, snapshot.get_code()) )
        if node is not None:
            return node

    def get_namespace(my):
        # this is used for finding if a node defined in asset_history is loaded
        # node_name name is not used
        xml = my._get_data()
        dict = {}
        current = xml.get_nodes_attr("session/namespace[@current='true']", 'name')
        if current:
            dict['current'] = current[0]
            names = xml.get_nodes_attr("session/namespace", 'name')
            names.remove(current[0])
            dict['child'] = names
        return dict

    def get_node_name(my, snapshot_code, namespace):
        xml = my._get_data()
        snapshot = Snapshot.get_by_code(snapshot_code)
        type = snapshot.get_type()
        if type == 'anim_export':
            type = 'anim'
        node = xml.get_node("session/node[@%s_snapshot_code='%s' and @namespace='%s']"\
            % (type, snapshot.get_code(), namespace  ))
        if node is not None:
            return Xml.get_attribute(node, 'name')
        else:
            return ''

    def get_node_names(my, is_tactic_node=None):
        xml = my._get_data()
        if is_tactic_node == None:
            node_names = xml.get_values("session/node/@name")
        elif is_tactic_node == True:
            node_names = xml.get_nodes_attr("session/node[@tactic_node='true']", 'name')
        elif is_tactic_node == False:
            node_names = xml.get_nodes_attr("session/node[@tactic_node='false']", 'name')
        return node_names

    def get_instance_names(my, is_tactic_node=None):
        xml = my._get_data()
        if is_tactic_node == None:
            instances = xml.get_values("session/node/@instance")
        elif is_tactic_node == True:
            instances = xml.get_nodes_attr("session/node[@tactic_node='true']", 'instance')
        elif is_tactic_node == False:
            instances = xml.get_nodes_attr("session/node[@tactic_node='false']", 'instance')
           
        return instances

    
    def get_asset_codes(my):
        xml = my._get_data()
        asset_codes = xml.get_values("session/node/@asset_code")
        return asset_codes


    def get_file_name(my):
        xml = my._get_data()
        file_name = xml.get_value("session/file/@name")
        return file_name

    def get_project_dir(my):
        xml = my._get_data()
        project_dir = xml.get_value("session/project/@dir")
        return project_dir


    def get_data(my):
        my.data_xml = my._get_data()
        return my.data_xml




    def _get_data(my):
        if not my.data_xml:
            my.data_xml = my.get_xml_value("data")

            # store all of the nodes in a data structure
            my.nodes = {}
            children = my.data_xml.get_nodes("session/node")
            for child in children:
                
                name = Xml.get_attribute(child, "name")
                my.nodes[name] = child

                # only store tactic nodes for the instance
                instance = Xml.get_attribute(child, "instance")
                is_tactic_node = Xml.get_attribute(child, "tactic_node")
                if is_tactic_node == "true":
                    my.nodes[instance] = child

            # record all of the subrefs as well
            children = my.data_xml.get_nodes("session/node/ref")
            for child in children:
                name = Xml.get_attribute(child, "name")
                my.nodes[name] = child

                # only store tactic nodes for the instance
                instance = Xml.get_attribute(child, "instance")
                is_tactic_node = Xml.get_attribute(child, "tactic_node")
                if is_tactic_node == "true":
                    my.nodes[instance] = child


 
        return my.data_xml

    #
    # static functions
    #
    def get(cls, pid=0, asset_mode=False):
        user_name = Environment.get_user_name()
        search = Search(cls.SEARCH_TYPE)
        search.add_filter("login", user_name)
        if pid:
            search.add_filter("pid", pid)
        search.add_order_by("timestamp desc")
        session = search.get_sobject()

        # if one doesn't exist, create it
        if pid and not session:
            session = SObjectFactory.create(cls.SEARCH_TYPE)
            session.set_value("login", user_name)
            session.set_value("data", "<session/>")
            session.set_value("pid", pid)
            session.commit()

        if not session:
            session = SObjectFactory.create(cls.SEARCH_TYPE)
            return session
        else:
            # set instance variable here
            session.asset_mode = asset_mode
            return session
    get = classmethod(get)







