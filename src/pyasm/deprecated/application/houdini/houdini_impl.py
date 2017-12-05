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

__all__ = ['HoudiniImpl']
import re
from pyasm.application.common import NodeData

from houdini import Houdini, HoudiniEnvironment, HoudiniNodeNaming


class HoudiniImpl(object):
    '''class which holds the specifics for an example Maya implementation.
    It uses namespaces where the node_name has the following format:
        instance:asset_code
    '''
    def __init__(my):
        my.env = HoudiniEnvironment.get()
        my.app = Houdini.get()


    def dump_interface(my, node_name):
        '''Dump animation from an node '''
        # export the selected node
        file_path = "%s/%s.tmp.cmd" % (my.env.get_tmpdir(),node_name)
        my.app.export_anim(file_path, node_name)
        return file_path

    def get_save_dir(my):
        dir = my.env.get_tmpdir()
        return dir

    def start_progress(my, title, visible, step):
        return ProgressBar()

    def get_snapshot_code(my, node_name, snapshot_type):
        '''This function gets the snapshot_code that was used to load this
        asset'''
        node_data = NodeData(node_name)
        snapshot_code = node_data.get_attr("%s_snapshot" % snapshot_type,"code")
        return snapshot_code


    def get_snapshot_attr(my, node_name, snapshot_type, attr):
        '''This function gets the snapshot_code that was used to load this
        asset'''
        node_data = NodeData(node_name)
        snapshot_code = node_data.get_attr("%s_snapshot" % snapshot_type, attr)
        return snapshot_code


    def get_textures_from_instance(my, node_name):
        '''extracts external file path references from a maya file'''
        '''NOTE: this is not currently used because there is no simple
        way in Maya to determine which file node belongs to which assets'''

        texture_nodes = []
        texture_paths = []
        
        return texture_nodes, texture_paths


 
    def get_textures_from_path(my, path):
        # find all of the textures in the extracted file
        '''NOTE: this is not currently used in Houdini'''
        current_node = None

        texture_nodes = []
        texture_paths = []

        return texture_nodes, texture_paths


    def get_textures_from_session(my, node_name):
        return my.app.get_file_references(node_name)


    def get_global_texture_dirs(my):
        return []

    def import_file(my, node_name, path, is_reference=False):

        # import file into namespace
        if is_reference == True:
            created_node = my.app.import_reference(path,node_name)
        else:
            created_node = my.app.import_file(path,node_name)

        # select newly created attr
        my.app.select(created_node)

        return created_node


    def get_geo_paths(my):
        return []

        # File group functions
    def is_file_group(my, path):
        hou_pat = re.compile('\$F\d+')
        if hou_pat.search(path):
            return True
        return False

    def get_file_range(my, path):
        #TODO: figure out file range
        start = 1
        end = 100
        by = 1
       
        return '%s-%s/%s' %(start, end, by)


    def get_tactic_file_group_path(my, path):
        '''get TACTIC compatible notation ####.jpg given app's path'''
        new_str = path
        def replace_str(m):
            groups = m.groups()
            pad = groups[0]
            return '#'*int(pad)
        
       
        xsi_pat = re.compile('\$F(\d+)')
        new_str = xsi_pat.sub(replace_str, path)  

        return new_str

    def get_app_file_group_path(my, file_name, file_range):
        '''get the group path notation specific for the application'''
        pat = re.compile('\.(#+)\.')
        m = pat.search(file_name)
        new_str = file_name
        if m:
            group = m.groups()[0]
            frame_start, frame_end, frame_by = Common.get_file_range(file_range)
            replace_str = '.$F%s.'% (len(group))
            
            new_str = pat.sub(replace_str, file_name)
        return new_str


class ProgressBar(object):
    ''' A progress bar used in Houdini '''
    def __init__(my, progress_bar=None, title=None, visible=None, step=None): 
        ''' @params
            progress_bar- Houdini's progress bar
            title- title
            visible- visibility
            step- number of steps in this process '''
        
    def increment(my):
        pass

    def set_message(my, message):
        pass

    def stop(my):
        pass
