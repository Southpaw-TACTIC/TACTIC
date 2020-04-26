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
    def __init__(self, node_name=None):
        # chr001_joe_black
        self.node_name = node_name
        self.namespace = ''

        if node_name:
            if self.node_name.find("_") != -1:
                self.has_namespace_flag = True
                self.asset_code, self.namespace = node_name.split("_",1)
            else:
                self.has_namespace_flag = False
                self.asset_code = self.namespace = node_name

    def get_asset_code(self):
        return self.asset_code

    def set_asset_code(self, asset_code):
        self.asset_code = asset_code

    # DEPRECATED
    def get_instance(self):
        return self.namespace

    # DEPRECATED
    def set_instance(self, namespace):
        self.has_namespace_flag = True
        self.namespace = namespace


    def get_namespace(self):
        return self.namespace

    def set_namespace(self, namespace):
        self.has_namespace_flag = True
        self.namespace = namespace


    def get_node_name(self):
        return self.build_node_name()


    def build_node_name(self):
        if self.asset_code == self.namespace:
            return self.asset_code
        else:
            return "%s_%s" % (self.asset_code, self.namespace)


    def has_instance(self):
        return self.has_namespace_flag
        
    def has_namespace(self):
        return self.has_namespace_flag





class Flash(Application):
    FLASH_EXE = "C:/Program Files/Macromedia/Flash 8/Flash.exe"

    '''interface to connect to flash on the client side'''
    def __init__(self):
        from flash_environment import FlashEnvironment
        from flash_info import FlashInfo
        self.env = FlashEnvironment.get()
        self.is_initialized = False
        self.info = FlashInfo.get()
        
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
      
        self.sandbox_path = self.info.get_sandbox_dir()
        self.log_path = self.info.get_log_path() 
        self.publish_dir =  self.info.get_publish_dir() 

        # load the appropriate jsfl files
        jsfl = self.get_jsfl(self.load_jsfl, "include", "common.jsfl", self.info.get_tmp_dir())
        jsfl_list.append(jsfl)

        self.is_initialized == True

        return jsfl_list

    def get_workspace_dir(self):
        tactic_dir = self.env.get_tmpdir()
        return "%s/sandbox" % tactic_dir


    def get_var(self, name):
        return name


    # undefined in Application
    def get_node_naming(self, node_name=None):
        return FlashNodeNaming(node_name)




    def run_flash(self, exec_path=None):
        '''execute a non blocking flash session'''

        if not exec_path:
            tmp_dir = self.env.get_tmpdir()
            exec_path = "%s/run.jsfl" % tmp_dir
           
            file = open(exec_path, "wb")
            file.write("x=1")
            file.close()

        print exec_path

        # run flash
        pid = Popen([self.FLASH_EXE, exec_path])
        print pid
        #os.system(exec_path)

        # sleep for 1 second
        import time
        time.sleep(1)

    def load(self, path, asset_code):
        ''' just open the file in simple mode '''
        self.import_file(asset_code, path, instantiation='import', load_mode='simple', use_namespace=False)


    def import_file(self, node_name, path, instantiation='import', load_mode='merge', use_namespace=True):

        jsfl_list = self.init()
        # initialize the session
        prefix_mode = ""
        jsfl = self.get_jsfl(self.load_jsfl, "init_session", load_mode, prefix_mode, self.log_path, self.sandbox_path)
        jsfl_list.append(jsfl)

        # for image/audio import, load_mode='import'
        if instantiation =='import_media':
            # load file
            jsfl = self.get_jsfl(self.load_jsfl, "import_asset", path, None, node_name)
            jsfl_list.append(jsfl)
        else:
            # load file
            jsfl = self.get_jsfl(self.load_jsfl, "load_asset", path, None, node_name)
            jsfl_list.append(jsfl)

        # execute all of the jsfl commands
        jsfl_final = "\n".join(jsfl_list)
        print jsfl_final
        self.run_jsfl(jsfl_final)

    def close_files(self):
        jsfl_list = self.init()
        jsfl = self.get_jsfl(self.load_jsfl, "close_docs")
        print "JSFL ", jsfl
        self.run_jsfl(jsfl)

    def run_jsfl(self, jsfl):
        tmp_dir = self.env.get_tmpdir()
        exec_path = "%s/exec.jsfl" % tmp_dir

        file = open(exec_path, "w")
        file.write(jsfl)
        file.close()

        os.system(exec_path)



        



    def get_jsfl(self, load_path, function, *args):
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


    def download_jsfl(self, file_name):
        server_url = self.env.get_server_url()
        jsfl_url = server_url + "/context/JSFL/" + file_name

        local_dir = self.env.get_tmpdir()

        jsfl_to_path = local_dir + "/JSFL"
        print "jsfl_to_path: ", jsfl_to_path

        self.download(jsfl_url, jsfl_to_path)

        if not os.path.exists(jsfl_to_path):
            raise FlashException("Failed to download: %s" % file_name)


    def download(self, url, to_dir="", skip_if_exists=False):
        import urllib, urllib2
        filename = os.path.basename(url)

        # download to the current project
        if not to_dir:
            to_dir = self.get_workspace_dir()
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




