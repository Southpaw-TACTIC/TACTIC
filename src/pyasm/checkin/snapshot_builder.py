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

__all__ = ['SnapshotBuilder']

import os

from pyasm.common import *
from pyasm.biz import Snapshot

class SnapshotBuilder(Base):
    '''utility class which help creates snapshots'''

    def __init__(my, xml=None):
        if not xml:
            my.xml = Xml()
            my.xml.create_doc("snapshot")
        else:
            my.xml = xml
        my.root_node = my.xml.get_root_node()


    def get_root_node(my):
        return my.root_node

    def add_root_attr(my, name, value):
        ''' add attribute to the root node. i.e. <snapshot>'''
        Xml.set_attribute(my.root_node, name, value)

    def add_node(my, node_name, data, parent=None):
        node = my.xml.create_element(node_name)
        for name, value in data.items():
            Xml.set_attribute(node,name,value)
            
        if parent == None:
            #my.root_node.appendChild(node)
            my.xml.append_child(my.root_node, node)
        else:
            #parent.appendChild(node)
            my.xml.append_child(parent, node)

        return node


    def copy_node(my, node, parent):
        if parent == None:
            #my.root_node.appendChild(node)
            my.xml.append_child(my.root_node, node)
        else:
            #parent.appendChild(node)
            my.xml.append_child(parent, node)
        return node
       




    def _add_file_node(my, file_code, name, info={}):
        file_node = my.xml.create_element("file")
        Xml.set_attribute(file_node, "file_code", file_code)
        Xml.set_attribute(file_node, "name", name)

        for key,value in info.items():
            Xml.set_attribute(file_node, key, value)

        #my.root_node.appendChild(file_node)
        my.xml.append_child(my.root_node, file_node)
        return file_node


    def add_file(my, file_object, info={}):
        file_code = file_object.get_code()
        file_name = file_object.get_file_name()
        return my._add_file_node(file_code, file_name, info)





    def add_ref(my, sobject, context, version, instance_name=None, parent=None, type='ref', node_name = '', snapshot_code=None, level=None, tag='main'):

        assert type in ['ref', 'input_ref', 'cache']

        data = {}
        data['search_type'] = sobject.get_search_type()
        data['search_id'] = sobject.get_id()
        data['version'] = str(version)
        data['context'] = context

        if level:
            data['level_type'] = level.get_search_type()
            data['level_id'] = level.get_id()

        if snapshot_code:
            data['snapshot_code'] = snapshot_code

        if tag:
            data['tag'] = tag
            
            
        # extraneous information
        if instance_name != None:
            data['instance'] = instance_name

	    # FIXME: sometimes node is used in this ref level when set externally
        # why is it inconsistent!
        if node_name:
            data['node_name'] = node_name

        return my.add_node(type, data, parent)


    def add_unknown_ref(my, file_path, parent=None):
        type = "unknown_ref"
        data = {}
        data['path'] = file_path
        return my.add_node(type, data, parent)




    def add_ref_by_snapshot(my, snapshot, instance_name=None, parent=None, type='ref', node_name='', tag='main'):
        sobject = snapshot.get_sobject()
        context = snapshot.get_value("context")
        version = snapshot.get_value("version")

        level = snapshot.get_level()

        snapshot_code = snapshot.get_code()

        return my.add_ref( sobject, context, version, instance_name, parent, type, node_name, snapshot_code=snapshot_code, level=level, tag=tag )


    def add_ref_by_snapshot_code(my, snapshot_code, instance_name=None, parent=None, type='ref', node_name='', tag='main'):
        snapshot = Snapshot.get_by_code(snapshot_code)
        if not snapshot:
            Environment.add_warning("Reference not found", "Found reference to snapshot [%s] which no longer exists in the Tactic database" % snapshot_code)
            return
            
        return my.add_ref_by_snapshot(snapshot, instance_name, parent, type, node_name, tag=tag)


    def add_ref_by_file_path(my, file_path, type='ref', node_name='', tag='main'):
        '''add a reference based on the file name.  If the file is unique, then
        a reference can be found based on the file name'''
        from pyasm.biz import File
        filename = os.path.basename(file_path)
        file = File.get_by_filename(filename, padding=4)
        if not file:
            Environment.add_warning("Unknown File Reference", "File reference [%s] does not exist in database" % file_path)
            my.add_unknown_ref(file_path)

            return
        else:
            snapshot_code = file.get_value("snapshot_code")
            return my.add_ref_by_snapshot_code(snapshot_code, type=type, node_name=node_name, tag=tag)




    def add_fref_by_snapshot(my, snapshot, instance_name=None, parent=None, node_name=''):
        sobject = snapshot.get_sobject()
        context = snapshot.get_value("context")
        version = snapshot.get_value("version")

        data = {}
        data['search_type'] = sobject.get_search_type()
        data['search_id'] = sobject.get_id()
        data['version'] = str(version)
        data['context'] = context

        if instance_name != None:
            data['instance'] = instance_name

        if node_name:
            data['node_name'] = instance_name


        return my.add_node("fref", data, parent)




    def get_xml(my):
        return my.xml

    def to_string(my):
        return my.xml.to_string()


