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

    def __init__(self, node_name, file_type, path=""):

        self.file_type = file_type
        self.path = path

        self.info = BaseAppInfo.get()
        self.impl = self.info.get_app_implementation()
        self.app = self.info.get_app()


        self.node_name = node_name

        self.texture_paths = []
        self.texture_nodes = []
        self.texture_attrs = []

        self.dependent_paths = []


    def get_texture_info(self):
        return self.texture_paths, self.texture_nodes, self.texture_attrs


    def execute(self):
        assert self.file_type

        self.app.message("path [%s] [%s]" % (self.app.APPNAME, self.file_type) )

        # find all of the textures in the extracted file
        if self.app.APPNAME == "maya":
            if self.file_type == "mayaAscii":
                # handle the textures
                self.texture_nodes, self.texture_paths, self.texture_attrs = \
                    self.impl.get_textures_from_path(path)

                # remember all of the geo paths
                self.geo_paths = self.impl.get_geo_paths()
                for geo_path in self.geo_paths:
                    self.dependent_paths.append(geo_path)
            else:
                self.texture_nodes, self.texture_paths, self.texture_attrs = \
                    self.impl.get_textures_from_session(self.node_name)
                print self.texture_nodes, self.texture_paths, self.texture_attrs



        elif self.app.APPNAME == "houdini":
            self.texture_nodes, self.texture_paths, self.texture_attrs = \
                self.app.get_file_references(self.node_name)

        elif self.app.APPNAME == "xsi":
            if self.file_type == "dotXSI":
                self.texture_nodes, self.texture_paths, self.texture_attrs = \
                    self.impl.get_textures_from_path(self.path)
            else:
                self.texture_nodes, self.texture_paths, self.texture_attrs = \
                    self.impl.get_textures_from_session(self.node_name)


        # add all of the texture paths
        for texture_path in self.texture_paths:
            # FIXME: all of the texture paths are uploaded!!!, even if
            # they are identical
            self.dependent_paths.append(texture_path)

        return self.dependent_paths


