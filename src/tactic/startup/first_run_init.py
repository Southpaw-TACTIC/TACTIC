###########################################################
#
# Copyright (c) 2005-2008, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#



__all__ = ['FirstRunInit']

import tacticenv

from pyasm.common import Common, Config, Environment, Common, TacticException, Container

import os, shutil
import sys

# This will also set some paths
from pyasm.common import Environment, Config

tactic_install_dir = tacticenv.get_install_dir()
tactic_site_dir = tacticenv.get_site_dir()

sys.path.insert(0, "%s/src" % tactic_install_dir)
sys.path.insert(0, "%s/src/plugins" % tactic_install_dir)
sys.path.insert(0, "%s/tactic_sites" % tactic_install_dir)
sys.path.insert(0, tactic_site_dir)




class FirstRunInit(object):
    def execute(self):
        self.copy_start()

        # check to see if there is a server code
        server_code = Config.get_value("install", "server")
        #if not server_code:
        #    # generate one
        #    server_code = Common.generate_alphanum_key(3)
        #    Config.set_value("install", "server", server_code)
        #    Config.save_config()


    def copy_start(self):

        data_dir = Environment.get_data_dir(manual=True)

        # check to see if the data folder already exists
        print("\n")
        print("Data Directory [%s]" % data_dir)
        install_dir = Environment.get_install_dir()

        # find criteria for initializing
        initialize = False
        if data_dir and not os.path.exists(data_dir):
            initialize = True

        if data_dir and not os.path.exists("%s/config" % data_dir):
            initialize = True


        if initialize:
            # copy the template over.  This should exist even if it is not used
            print("... not found: initializing\n")
            install_data_path = "%s/src/install/start" % (install_dir)
            if os.path.exists(install_data_path):
                dirnames = os.listdir(install_data_path)
                for dirname in dirnames:
                    to_dir = "%s/%s" % (data_dir, dirname)
                    if os.path.exists(to_dir):
                        print("WARNING: path [%s] exists ... skipping copying" % to_dir)
                        continue
                    print("Copying to [%s]" % to_dir)
                    from_dir = "%s/%s" % (install_data_path, dirname)
                    shutil.copytree(from_dir, to_dir)
            else:
                shutil.copytree(install_data_path, data_dir)


            # create the dist folder
            to_dir = "%s/dist" % (data_dir)
            if not os.path.exists(to_dir):
                os.makedirs(to_dir)


            # copy the appropriate config file
            if os.name == 'nt':
                filename = 'standalone_win32-conf.xml'
            else:
                filename = 'standalone_linux-conf.xml'
            install_config_path = "%s/src/install/config/%s" % (install_dir,filename)
            to_config_path = "%s/config/tactic-conf.xml" % data_dir

            if not os.path.exists(to_config_path):
                dirname = os.path.dirname(to_config_path)
                if not os.path.exists(dirname):
                    os.makedirs(dirname)
                shutil.copy(install_config_path, to_config_path)

        # some backwards compatibility issues
        old_config_path = "%s/config/tactic_linux-conf.xml" % data_dir
        if os.path.exists(old_config_path):
            new_config_path = "%s/config/tactic-conf.xml" % data_dir
            shutil.move(old_config_path, new_config_path)



        config_path = Config.get_config_path()
        config_exists = False
        if os.path.exists(config_path):
            config_exists = True

        # insert the plugin path to run get_asset_dir()
        plugin_dir = Environment.get_plugin_dir()
        sys.path.insert(0, plugin_dir)

        asset_dir = Environment.get_asset_dir()
        print("Asset Directory [%s]" % asset_dir)

        tmp_dir = Environment.get_tmp_dir()
        print("Temp Directory [%s]" % tmp_dir)

        # check if there is a config path already exists. If it does,
        # then don't do anything further.  This is likely a previous
        # installation
        if config_exists:
            print("Config path [%s]" % config_path)
            return
        else:
            # if there is no config, retrieve data_dir in non-manual mode
            data_dir = Environment.get_data_dir()
            f = open("%s/first_run" % data_dir, 'w')
            f.write("")
            f.close()

        return




