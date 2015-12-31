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

    def __init__(my):
        super(FlashBuilder,my).__init__()
        my.info = FlashInfo.get()

        my.is_initialized = False



    def init(my):
        jsfl_list = []

        if my.is_initialized:
            return jsfl_list

        # instantiate the session
        #server = my.env.get_server_url()
        server = "http://fugu"

        my.info.download("%s/context/JSFL/common.jsfl" % server)
        my.load_jsfl = my.info.download("%s/context/JSFL/load2.jsfl" % server)
        my.publish_jsfl = my.info.download("%s/context/JSFL/publish2.jsfl" % server)
        my.render_jsfl = my.info.download("%s/context/JSFL/render.jsfl" % server)
        #my.sandbox_path = "C:/sthpw/sandbox"
        #my.log_path = "C:/sthpw/temp/actionLog.txt"
        my.sandbox_path = my.info.get_sandbox_dir()
        my.log_path = my.info.get_log_path() 
        my.publish_dir =  my.info.get_publish_dir() 
        # load the appropriate jsfl files
        jsfl = my.app.get_jsfl(my.load_jsfl, "include", "common.jsfl", my.info.get_tmp_dir())
        jsfl_list.append(jsfl)

        my.is_initialized == True

        return jsfl_list

    def check_existence(my, tactic_node_name):
        ''' check if this node exist '''
        pass
    
    def load_file(my, path, node_name):
        my.app.load(path, node_name)

    def import_file(my, node_name, path, instantiation='import', use_namespace=True):

        my.app.import_file( node_name, path, instantiation, load_mode='merge',use_namespace=True)

        #my.render()

        # initialize the session
        load_mode="merge"
        #load_mode="simple"
        prefix_mode = ""
        jsfl = my.app.get_jsfl(my.load_jsfl, "init_session", load_mode, prefix_mode,\
            my.log_path, my.sandbox_path)
        jsfl_list.append(jsfl)

    def publish_file(my, asset_code, node_name):

        # for flash asset code is node name
        jsfl_list = my.init()
        jsfl = my.app.get_jsfl(my.publish_jsfl, "publish_asset", asset_code,\
            my.publish_dir, my.log_path)
        jsfl_list.append(jsfl)
        # execute all of the jsfl commands
        jsfl_final = "\n".join(jsfl_list)
        print jsfl_final
        my.app.run_jsfl(jsfl_final)

    def close_files(my):
        my.app.close_files()

    def render(my):

        jsfl_list = my.init()

        tmp_dir = my.env.get_tmp_dir()

        # render
        file_format = "png"
        render_dir = "%s/render" % tmp_dir
        prefix = ""

        jsfl = my.app.get_jsfl(my.render_jsfl, "render_layer", prefix, file_format, render_dir, my.log_path)
        jsfl_list.append(jsfl)

        jsfl_final = "\n".join(jsfl_list)
        print "jsfl_final: ", jsfl_final

        my.app.run_jsfl(jsfl_final)






