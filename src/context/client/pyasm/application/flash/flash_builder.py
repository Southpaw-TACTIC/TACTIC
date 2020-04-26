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

__all__ = ['FlashBuilder']


import os, sys, urllib, xmlrpclib
from xml.dom.minidom import parseString

from pyasm.application.common import SessionBuilder

from flash_environment import FlashEnvironment
from flash_info import FlashInfo
from flash import Flash


class FlashBuilder(SessionBuilder):
    '''builds a flash file'''

    def __init__(self):
        super(FlashBuilder,self).__init__()
        self.info = FlashInfo.get()

        self.is_initialized = False



    def init(self):
        jsfl_list = []

        if self.is_initialized:
            return jsfl_list

        # instantiate the session
        #server = self.env.get_server_url()
        server = "http://fugu"

        self.info.download("%s/context/JSFL/common.jsfl" % server)
        self.load_jsfl = self.info.download("%s/context/JSFL/load2.jsfl" % server)
        self.publish_jsfl = self.info.download("%s/context/JSFL/publish2.jsfl" % server)
        self.render_jsfl = self.info.download("%s/context/JSFL/render.jsfl" % server)
        #self.sandbox_path = "C:/sthpw/sandbox"
        #self.log_path = "C:/sthpw/temp/actionLog.txt"
        self.sandbox_path = self.info.get_sandbox_dir()
        self.log_path = self.info.get_log_path() 
        self.publish_dir =  self.info.get_publish_dir() 
        # load the appropriate jsfl files
        jsfl = self.app.get_jsfl(self.load_jsfl, "include", "common.jsfl", self.info.get_tmp_dir())
        jsfl_list.append(jsfl)

        self.is_initialized == True

        return jsfl_list

    def check_existence(self, tactic_node_name):
        ''' check if this node exist '''
        pass
    
    def load_file(self, path, node_name):
        self.app.load(path, node_name)

    def import_file(self, node_name, path, instantiation='import', use_namespace=True):

        self.app.import_file( node_name, path, instantiation, load_mode='merge',use_namespace=True)

        #self.render()

        # initialize the session
        load_mode="merge"
        #load_mode="simple"
        prefix_mode = ""
        jsfl = self.app.get_jsfl(self.load_jsfl, "init_session", load_mode, prefix_mode,\
            self.log_path, self.sandbox_path)
        jsfl_list.append(jsfl)

    def publish_file(self, asset_code, node_name):

        # for flash asset code is node name
        jsfl_list = self.init()
        jsfl = self.app.get_jsfl(self.publish_jsfl, "publish_asset", asset_code,\
            self.publish_dir, self.log_path)
        jsfl_list.append(jsfl)
        # execute all of the jsfl commands
        jsfl_final = "\n".join(jsfl_list)
        print jsfl_final
        self.app.run_jsfl(jsfl_final)

    def close_files(self):
        self.app.close_files()

    def render(self):

        jsfl_list = self.init()

        tmp_dir = self.env.get_tmp_dir()

        # render
        file_format = "png"
        render_dir = "%s/render" % tmp_dir
        prefix = ""

        jsfl = self.app.get_jsfl(self.render_jsfl, "render_layer", prefix, file_format, render_dir, self.log_path)
        jsfl_list.append(jsfl)

        jsfl_final = "\n".join(jsfl_list)
        print "jsfl_final: ", jsfl_final

        self.app.run_jsfl(jsfl_final)






