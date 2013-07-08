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

__all__ = ['Flash', 'FlashException']


from pyasm.application.common import Application

from subprocess import *
import os



class FlashException(Exception):
    pass


class FlashNodeNaming(object):
    def __init__(my, node_name=None):
        # chr001_joe_black
        my.node_name = node_name
        my.namespace = ''

        if node_name:
            if my.node_name.find("_") != -1:
                my.has_namespace_flag = True
                my.asset_code, my.namespace = node_name.split("_",1)
            else:
                my.has_namespace_flag = False
                my.asset_code = my.namespace = node_name

    def get_asset_code(my):
        return my.asset_code

    def set_asset_code(my, asset_code):
        my.asset_code = asset_code

    # DEPRECATED
    def get_instance(my):
        return my.namespace

    # DEPRECATED
    def set_instance(my, namespace):
        my.has_namespace_flag = True
        my.namespace = namespace


    def get_namespace(my):
        return my.namespace

    def set_namespace(my, namespace):
        my.has_namespace_flag = True
        my.namespace = namespace


    def get_node_name(my):
        return my.build_node_name()


    def build_node_name(my):
        if my.asset_code == my.namespace:
            return my.asset_code
        else:
            return "%s_%s" % (my.asset_code, my.namespace)


    def has_instance(my):
        return my.has_namespace_flag
        
    def has_namespace(my):
        return my.has_namespace_flag





class Flash(Application):
    FLASH_EXE = "C:/Program Files/Macromedia/Flash 8/Flash.exe"

    '''interface to connect to flash on the client side'''
    def __init__(my):
        from flash_environment import FlashEnvironment
        from flash_info import FlashInfo
        my.env = FlashEnvironment.get()
        my.is_initialized = False
        my.info = FlashInfo.get()
        
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
      
        my.sandbox_path = my.info.get_sandbox_dir()
        my.log_path = my.info.get_log_path() 
        my.publish_dir =  my.info.get_publish_dir() 

        # load the appropriate jsfl files
        jsfl = my.get_jsfl(my.load_jsfl, "include", "common.jsfl", my.info.get_tmp_dir())
        jsfl_list.append(jsfl)

        my.is_initialized == True

        return jsfl_list

    def get_workspace_dir(my):
        tactic_dir = my.env.get_tmpdir()
        return "%s/sandbox" % tactic_dir


    def get_var(my, name):
        return name


    # undefined in Application
    def get_node_naming(my, node_name=None):
        return FlashNodeNaming(node_name)




    def run_flash(my, exec_path=None):
        '''execute a non blocking flash session'''

        if not exec_path:
            tmp_dir = my.env.get_tmpdir()
            exec_path = "%s/run.jsfl" % tmp_dir
           
            file = open(exec_path, "wb")
            file.write("x=1")
            file.close()

        print exec_path

        # run flash
        pid = Popen([my.FLASH_EXE, exec_path])
        print pid
        #os.system(exec_path)

        # sleep for 1 second
        import time
        time.sleep(1)

    def load(my, path, asset_code):
        ''' just open the file in simple mode '''
        my.import_file(asset_code, path, instantiation='import', load_mode='simple', use_namespace=False)


    def import_file(my, node_name, path, instantiation='import', load_mode='merge', use_namespace=True):

        jsfl_list = my.init()
        # initialize the session
        prefix_mode = ""
        jsfl = my.get_jsfl(my.load_jsfl, "init_session", load_mode, prefix_mode, my.log_path, my.sandbox_path)
        jsfl_list.append(jsfl)

        # for image/audio import, load_mode='import'
        if instantiation =='import_media':
            # load file
            jsfl = my.get_jsfl(my.load_jsfl, "import_asset", path, None, node_name)
            jsfl_list.append(jsfl)
        else:
            # load file
            jsfl = my.get_jsfl(my.load_jsfl, "load_asset", path, None, node_name)
            jsfl_list.append(jsfl)

        # execute all of the jsfl commands
        jsfl_final = "\n".join(jsfl_list)
        print jsfl_final
        my.run_jsfl(jsfl_final)

    def close_files(my):
        jsfl_list = my.init()
        jsfl = my.get_jsfl(my.load_jsfl, "close_docs")
        print "JSFL ", jsfl
        my.run_jsfl(jsfl)

    def run_jsfl(my, jsfl):
        tmp_dir = my.env.get_tmpdir()
        exec_path = "%s/exec.jsfl" % tmp_dir

        file = open(exec_path, "w")
        file.write(jsfl)
        file.close()

        os.system(exec_path)



        



    def get_jsfl(my, load_path, function, *args):
        '''get the jsfl string that runs a specific jsfl command'''
        jsfl = "fl.runScript('file:///%s', '%s'" % (load_path, function)
        new_args = []
        for x in args:
            if x:
                x = "'%s'" % x
            else:
                x = "null"
            new_args.append(x)
        #args = ["'%s'" % x for x in args]

        if args:
            jsfl += ", "
            jsfl += ", ".join(new_args)
        jsfl += ")"
        return jsfl


    def download_jsfl(my, file_name):
        server_url = my.env.get_server_url()
        jsfl_url = server_url + "/context/JSFL/" + file_name

        local_dir = my.env.get_tmpdir()

        jsfl_to_path = local_dir + "/JSFL"
        print "jsfl_to_path: ", jsfl_to_path

        my.download(jsfl_url, jsfl_to_path)

        if not os.path.exists(jsfl_to_path):
            raise FlashException("Failed to download: %s" % file_name)


    def download(my, url, to_dir="", skip_if_exists=False):
        import urllib, urllib2
        filename = os.path.basename(url)

        # download to the current project
        if not to_dir:
            to_dir = my.get_workspace_dir()
            # for now, put everything in scenes
            to_dir = "%s/scenes" % to_dir

        # make sure the directory exists
        if not os.path.exists(to_dir):
            os.makedirs(to_dir)


        to_path = "%s/%s" % (to_dir, filename)

        # check if this file is already downloaded.  if so, skip
        if skip_if_exists and os.path.exists(to_path):
            print "skipping '%s', already exists" % to_path
            return to_path

        file = open(to_path, "wb")
        req = urllib2.Request(url)
        #try:
        #    resp = urllib2.urlopen(req)
        #    print "write!!"
        #    file.write( resp.read() )
        #    file.close()
        #except urllib2.URLError, e:
        #    raise Exception('%s - %s' % (e,url))
        f = urllib.urlopen(url)
        file = open(to_path, "wb")
        file.write( f.read() )
        file.close()
        f.close()


        return to_path





    # static functions
    def get():
        '''get the central on stored in the flash environment'''
        from flash_environment import FlashEnvironment
        env = FlashEnvironment.get()
        return env.get_app()
    get = staticmethod(get)




