###########################################################
#
# Copyright (c) 2005-2012, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#

__all__ = ['PluginUtil']

from pyasm.common import Environment, Xml

import os

class PluginUtil(object):
    '''A series of methods concerning plugins'''

    def __init__(self, **kwargs):
        self.base_dir = kwargs.get("base_dir")
        if not self.base_dir:
            self.base_dir = Environment.get_plugin_dir()


    def get_plugin_data(self, reldir):

        manifest_path = "%s/%s/manifest.xml" % (self.base_dir, reldir)
        xml = Xml()
        xml.read_file(manifest_path)
        node = xml.get_node("manifest/data")
        data = xml.get_node_values_of_children(node)

        return data




    def get_plugins_data(self, plugin_type=None):

        plugins_data = {}
        for root, dirnames, basenames in os.walk(self.base_dir):
            # for windows
            root = root.replace("\\", "/")
            reldir = root.replace(self.base_dir + "/", "")
            if "manifest.xml" in basenames:

                manifest_path = "%s/manifest.xml" % root
                xml = Xml()
                xml.read_file(manifest_path)

                node = xml.get_node("manifest/data")
                data = xml.get_node_values_of_children(node)

                if plugin_type and not data.get("type") == plugin_type:
                    continue

                plugins_data[reldir] = data


        return plugins_data



