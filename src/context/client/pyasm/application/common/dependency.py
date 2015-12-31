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


__all__ = ['Dependency']

import sys, types

from base_app_info import BaseAppInfo


class Dependency(object):
    '''class which handles the texture depedencies in a file or session'''

    def __init__(my, node_name, file_type, path=""):

        my.file_type = file_type
        my.path = path

        my.info = BaseAppInfo.get()
        my.impl = my.info.get_app_implementation()
        my.app = my.info.get_app()


        my.node_name = node_name

        my.texture_paths = []
        my.texture_nodes = []
        my.texture_attrs = []

        my.dependent_paths = []


    def get_texture_info(my):
        return my.texture_paths, my.texture_nodes, my.texture_attrs


    def execute(my):
        assert my.file_type

        my.app.message("path [%s] [%s]" % (my.app.APPNAME, my.file_type) )

        # find all of the textures in the extracted file
        if my.app.APPNAME == "maya":
            if my.file_type == "mayaAscii":
                # handle the textures
                my.texture_nodes, my.texture_paths, my.texture_attrs = \
                    my.impl.get_textures_from_path(path)

                # remember all of the geo paths
                my.geo_paths = my.impl.get_geo_paths()
                for geo_path in my.geo_paths:
                    my.dependent_paths.append(geo_path)
            else:
                my.texture_nodes, my.texture_paths, my.texture_attrs = \
                    my.impl.get_textures_from_session(my.node_name)
                print my.texture_nodes, my.texture_paths, my.texture_attrs



        elif my.app.APPNAME == "houdini":
            my.texture_nodes, my.texture_paths, my.texture_attrs = \
                my.app.get_file_references(my.node_name)

        elif my.app.APPNAME == "xsi":
            if my.file_type == "dotXSI":
                my.texture_nodes, my.texture_paths, my.texture_attrs = \
                    my.impl.get_textures_from_path(my.path)
            else:
                my.texture_nodes, my.texture_paths, my.texture_attrs = \
                    my.impl.get_textures_from_session(my.node_name)


        # add all of the texture paths
        for texture_path in my.texture_paths:
            # FIXME: all of the texture paths are uploaded!!!, even if
            # they are identical
            my.dependent_paths.append(texture_path)

        return my.dependent_paths


