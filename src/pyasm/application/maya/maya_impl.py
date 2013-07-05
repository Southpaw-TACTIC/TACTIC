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

__all__ = ['MayaImpl']

import re, os

from pyasm.application.common import NodeData

from maya_app import Maya, MayaNodeNaming
from maya_environment import MayaEnvironment
from maya_parser import *


class MayaImpl(object):
    '''class which holds the specifics for an example Maya implementation
    for certain actions.
    '''
    def __init__(my):
        my.env = MayaEnvironment.get()
        my.app = Maya.get()


    def dump_interface(my, node_name, mode='anim'):
        '''Dump animation from an node.  Here the animExport plugin is
        used, however it should be noted that to export an animation,
        keyframes have to put on the node.  The animation can be on one
        of two places, either the interface node, with the naming convention
        <asset_code>_interface or the top node if the interface does not exist
        '''
        interface = "%s_interface" % node_name

        naming = my.app.get_node_naming(node_name)
        instance = naming.get_instance()
        asset_code = naming.get_asset_code()

        #  select the interface
        has_interface = my.app.node_exists(interface)
        if has_interface:
            node_name = interface
        my.app.select(node_name)

       
        if mode == 'anim':
            # export the selected node
            file_path = "%s/%s.tmp.anim" % (my.env.get_tmpdir(),instance)
            anim_file = my.app.export_anim(file_path)
        elif mode == 'static':
            file_path = "%s/%s.tmp.static" % (my.env.get_tmpdir(),instance)
            attrs = my.app.get_all_attrs(node_name)
            omitted = ['tacticNodeData','notes']
            file = open(file_path, "w")
            
            for attr in attrs:
                if attr in omitted or my.app.is_keyed(node_name, attr):
                    continue
                #print "attr: ", attr
                #print "... value: ", my.app.get_attr(node_name,attr)
                #print "... default: ", my.app.get_attr_default(node_name,attr)
                file.write('%s -type %s -default %s -value %s \n' %(attr,\
                    my.app.get_attr_type(node_name,attr), \
                    my.app.get_attr_default(node_name,attr), \
                    my.app.get_attr(node_name,attr)))
            file.close()
      
        return file_path


    def get_save_dir(my):
        dir = my.env.get_tmpdir()
        return dir

    def start_progress(my, title, visible, step):
        pass

    def get_snapshot_code(my, node_name, snapshot_type):
        '''This function gets the snapshot_code that was used to load this
        asset'''
        return my.get_snapshot_attr(node_name, snapshot_type, "code")


    def get_snapshot_attr(my, node_name, snapshot_type, attr):
        '''This function gets the attr of the snapshot that was used to load this
        asset'''
        node_data = NodeData(node_name)
        snapshot_attr = node_data.get_attr("%s_snapshot" % snapshot_type, attr)
        return snapshot_attr




    def get_textures_from_session(my, node_name):
        '''extracts external texture references from a maya session'''
        '''NOTE: there is no simple
        way in Maya to determine which file node belongs to which assets.
        Instead, the maya file is parsed and the texture paths are extracted
        from there'''

        texture_nodes = []
        texture_paths = []
        texture_attrs = []

        if node_name.find(":") == -1:
            asset_code = node_name
            namespace = node_name
        else:
            namespace, asset_code = node_name.split(":")


        nodes = my.app.get_nodes_by_type("file")
        if nodes == None:
            return texture_nodes, texture_paths, texture_attrs

        for node in nodes:
            # filter only nodes for this asset
            # FIXME: this relies on naming conventions of the file node
            # otherwise it will miss it
            if not node.startswith("%s_" % asset_code) \
               and not node.startswith("%s:" % namespace):
                continue

            attr = "ftn"
            texture_attrs.append(attr)

            texture_path = my.app.get_attr(node, attr)

            # make sure you only grab each texture once
            if texture_path not in texture_paths:
                texture_nodes.append(node)
                texture_paths.append(texture_path)

        return texture_nodes, texture_paths, texture_attrs



    def get_textures_from_path(my, path):
        parser = MayaParser(path)
      
        # add some filters
        texture_filter = MayaParserTextureFilter()
        dir_list = my.get_global_texture_dirs()
        if dir_list:
            texture_filter.set_global_dirs(dir_list)
        parser.add_filter(texture_filter)

        texture_edit_filter = MayaParserTextureEditFilter()
        parser.add_filter(texture_edit_filter)

        parser.parse()

        texture_nodes, texture_paths, texture_attrs = texture_filter.get_textures()
        texture_nodes2, texture_paths2, texture_attrs2 = texture_edit_filter.get_textures()

        return texture_nodes+texture_nodes2, texture_paths+texture_paths2, texture_attrs+texture_attrs2

        #return texture_filter.get_textures()

    def get_global_texture_dirs(my):
        ''' get global texture dirs if MayaMan is installed'''
        dir_list = my.app.mel('MayaManInfo -sp "texture"')
        if dir_list:
            dir_list = list(dir_list)
            # remove trailing forward slash, if applicable
            dir_list = [x.rstrip('/') for x in dir_list]
            return dir_list 
        else:
            return []

    def get_geo_paths(my):
        '''return all of the paths concerning geo files'''
        paths = []

        geo_nodes = my.app.mel("ls -type cacheFile")
        if not geo_nodes:
            return paths

        for geo_node in geo_nodes:
            geo_paths = my.app.mel('cacheFile -q -f "%s"' % geo_node)
            for geo_path in geo_paths:
                if geo_path not in paths:
                    paths.append(geo_path)

        paths.sort()

        return paths

    def get_geo_from_session(my, node_name):
        '''return all of the (node, path) concerning geo files as list'''
        cache_info = []
        paths = []
        geo_nodes = my.app.mel("ls -type cacheFile")
        if not geo_nodes:
            return []
        
        node_shapes = []
        if my.app.node_exists(node_name):
            node_shapes = my.app.get_children(node_name, full_path=False, type='shape', recurse=True)
        #node_shapes = my.app.mel('listRelatives -type shape "%s"'%node_name)
        if node_shapes:
            node_shapes = list(node_shapes)
        else:
            node_shapes = []
        for geo_node in geo_nodes:
            cache_shape = ''
            cache_shapes = my.app.mel('cacheFile -q -cnm "%s"' % geo_node)
            # skip if not related to this node_name
            # we only support single cache shape for now
            if cache_shapes:
                cache_shape = cache_shapes[0] 
            if cache_shape not in node_shapes:
                continue
            geo_paths = my.app.mel('cacheFile -q -f "%s"' % geo_node)
            for geo_path in geo_paths:
                if geo_path not in paths:
                    cache_info.append((geo_node, geo_path))
                    paths.append(geo_path)
                    
        cache_info = sorted(cache_info)
        return cache_info

    def set_user_environment(my, sandbox_dir, basename):

        # for now, rename to this file
        new_file_name = "%s/%s" % (sandbox_dir, basename)
        my.app.rename( new_file_name )

        dirs = sandbox_dir.split("/")
        if dirs[-1] == "scenes":
            dirs = dirs[:-1]
            project_dir = "/".join(dirs)
        else:
            project_dir = sandbox_dir

        my.app.set_project(project_dir)
        my.app.mel('sp_setLocalWorkspaceCallback "%s" "directory"' % project_dir)

        workspace_path = "%s/workspace.mel" % project_dir
        if os.path.exists(workspace_path):
            my.app.mel('source "%s"' % workspace_path)

        current_title = my.app.get_window_title()
        title_header = current_title.split(":")[0]
        my.app.set_window_title( '%s:  %s' % (title_header, new_file_name) )


class ProgressBar(object):
    ''' A progress bar used in Maya '''
    def __init__(my, progress_bar=None, title=None, visible=None, step=None):
        ''' @params
            progress_bar- Maya's progress bar
            title- title
            visible- visibility
            step- number of steps in this process '''
        
    def increment(my):
        pass

    def set_message(my, message):
        pass

    def stop(my):
        pass
