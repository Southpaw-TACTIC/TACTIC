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

__all__ = ["EnvironmentException", "Environment"]

import tacticenv

import sys, os

from common import *
from container import *
from base import *
from config import *
from system import *
from common_exception import TacticWarning, TacticException

class EnvironmentException(Exception):
    pass


class Environment(Base):
    """class which encapsulates the environment the framework is running
    under"""

    # global function for all threads.
    IS_INITIALIZED = False

    def __init__(my):
        my.initialize_python_path()

        if not Environment.IS_INITIALIZED:
            my.initialize()
            Environment.IS_INITIALIZED = True
       

    def initialize_python_path(my):
        # add some paths
        paths = Config.get_value("services", "python_path", no_exception=True)
        paths_list = paths.split("|")
        for path in paths_list:
            sys.path.append(path)

    def initialize(my):
        '''Initializes the enviroment outside environment Tactic.  This is
        can be used for both the web environment and the batch environment'''

        # skips if TACTIC_CLEANUP is not true
        if not os.environ.get("TACTIC_CLEANUP") == 'true':
            return
      

        # is tactic configured/installed?
        is_installed = False
        if is_installed:
            # get the config file and read it for errors
            config_path = my.get_config_path()
            if not os.path.exists(config_path):
                raise EnvironmentException("Config file [%s] does not exist" % config_path)

            install_dir = my.get_install_dir()
            if not os.path.exists(install_dir):
                raise EnvironmentException("Install dir [%s] does not exist" % install_dir)

            site_dir = my.get_site_dir()
            if not os.path.exists(site_dir):
                raise EnvironmentException("Site dir [%s] does not exist" % site_dir)

            asset_dir = my.get_asset_dir()
            if not os.path.exists(asset_dir):
                raise EnvironmentException("Asset dir [%s] does not exist" % asset_dir)


        # create all of the temp directories
        # TODO: is this relevant for batch processes
        tmp_dir = my.get_tmp_dir()
        dirs = []
        dirs.append("%s/upload" % tmp_dir)
        dirs.append("%s/download" % tmp_dir)
        dirs.append("%s/cache" % tmp_dir)
        dirs.append("%s/upload" % tmp_dir)
        dirs.append("%s/temp" % tmp_dir)
        plugin_dir = my.get_plugin_dir()
        dirs.append(plugin_dir)

        for dir in dirs:
            System().makedirs(dir)
            try:
                os.chmod(dir, 0770)
            except OSError, e:
                print "WARNING: cannot chmod: ", e


        # remove the sidebar cache
        sidebar_cache_dir = "%s/cache/side_bar" % tmp_dir
        if os.path.exists(sidebar_cache_dir):
            import shutil
            shutil.rmtree(sidebar_cache_dir)

        os.environ['TACTIC_CLEANUP'] = "false"
        """
        # remove the round corner images
        corner_dir = "%s/src/context/ui_proto/roundcorners" % install_dir
        if os.path.exists(corner_dir):
            import shutil
            shutil.rmtree(corner_dir)

        """



    def get_python_exec(cls):
        python = Config.get_value("services", "python")
        if not python:
            python = "python"
        return python
    get_python_exec = classmethod(get_python_exec)


    def get_transfer_mode(my):
        repo_dir = Config.get_value("checkin", "win32_client_repo_dir")
        if repo_dir:
            transfer_mode = 'client_repo'
        else:
            transfer_mode = 'web'

        return transfer_mode



    # methods that should be overridden by implementation of the
    # environment
    def get_context_name(my):
        '''get the path for configruation file for the framework'''
        raise EnvironmentException("This function must be overridden")


    def get_command_key(my):
        '''Every command executed gets a unique key.  This key is checked
        to ensure that commands are not executed twice (ie refresh on
        a web page'''
        return Common.generate_random_key()


    ###########
    # Static environment functions
    #############


    def is_first_run():
        data_dir = Environment.get_data_dir()
        return os.path.exists("%s/first_run" % data_dir)
    is_first_run = staticmethod(is_first_run)



    def get_sobject_database():
        database = Config.get_value("database", "sobject_database")
        if not database:
            database = "sthpw"
        return database
    get_sobject_database = staticmethod(get_sobject_database)


    def has_tactic_database():
        # Determine if there is a TACTIC database in this AppServer
        if os.environ.get("TACTIC_DATABASE") == "false":
            return False
        else:
            return True
    has_tactic_database = staticmethod(has_tactic_database)


    def get_client_os(cls):
        return os.name
    get_client_os = classmethod(get_client_os)


    def get_config_dir():
        '''get the dir for configuration file for the framework'''
        return Config.get_config_dir()
    get_config_dir = staticmethod(get_config_dir)

    def get_config_path():
        '''get the path for configuration file for the framework'''
        return Config.get_config_path()
    get_config_path = staticmethod(get_config_path)


    def get_licence_dir():
        '''get the path of the license directory'''
        return Config.get_config_dir()
    get_license_dir = staticmethod(get_licence_dir)

 
    def get_install_dir():
        '''get the installation directory for the entire framework'''
        #return Config.get_value("install","install_dir")
        return os.environ["TACTIC_INSTALL_DIR"]
    get_install_dir = staticmethod(get_install_dir)


    def get_site_dir():
        '''get the site dir'''
        #return Config.get_value("install","site_dir")
        return os.environ["TACTIC_SITE_DIR"]
    get_site_dir = staticmethod(get_site_dir)

    def get_app_server():
        '''get the app server'''
        server = os.environ.get("TACTIC_APP_SERVER")
        if not server:
            server = 'batch'
        return server
    get_app_server = staticmethod(get_app_server)

    def set_app_server(app_server):
        os.environ["TACTIC_APP_SERVER"] = app_server
    set_app_server = staticmethod(set_app_server)



    def get_tmp_dir():
        '''get the temporary dir'''
        tmp_dir = Config.get_value("install","tmp_dir")
        if not tmp_dir:
            data_dir = os.environ.get("TACTIC_DATA_DIR")
            if data_dir:
                tmp_dir = "%s/temp" % data_dir
            else:
                tmp_dir = ""


        if not tmp_dir:
            raise TacticException("No tmp_dir defined")
        return tmp_dir
    get_tmp_dir = staticmethod(get_tmp_dir)


    def get_upload_dir(ticket=None):
        '''get the upload dir which relies on the ticket info'''
        tmpdir = Environment.get_tmp_dir()
        #web = Environment.get_env_object()
        #ticket = web.get_cookie("login_ticket")
        security = Environment.get_security()
        if not ticket:
            ticket = security.get_ticket_key()
        upload_dir = "%s/upload/%s" % (tmpdir, ticket)

        # make the directory if it does not exist 
        System().makedirs(upload_dir)

        return upload_dir
    get_upload_dir = staticmethod(get_upload_dir)



    def get_plugin_dir(cls):
        # override
        base_plugin_dir = Config.get_value("install","plugin_dir")
        if not base_plugin_dir:
            data_dir = cls.get_data_dir()
            base_plugin_dir = "%s/plugins" % data_dir

        return base_plugin_dir
    get_plugin_dir = classmethod(get_plugin_dir)


    def get_template_dir(cls):
        data_dir = cls.get_data_dir()
        base_template_dir = "%s/templates" % data_dir
        return base_template_dir
    get_template_dir = classmethod(get_template_dir)




    def get_client_handoff_dir(my, ticket=None, no_exception=False, include_ticket=True):
       
        if my.get_client_os() == "nt":
            base_handoff_dir = Config.get_value("checkin", "win32_client_handoff_dir", no_exception=True)
        else:
            base_handoff_dir = Config.get_value("checkin", "linux_client_handoff_dir", no_exception=True)


        if not base_handoff_dir:
            data_dir = my.get_data_dir()
            base_handoff_dir = "%s/%s" % (data_dir, "handoff")
            


        if include_ticket and not ticket:
            security = Environment.get_security()
            ticket = security.get_ticket_key()

        if no_exception == False and not base_handoff_dir:
            raise TacticException("No handoff directory defined in TACTIC config file")

        if include_ticket:
            handoff_dir = "%s/%s" % (base_handoff_dir, ticket)
        else:
            handoff_dir = base_handoff_dir

        # can't create this because it may be different on the server
        #if not os.path.exists(handoff_dir):
        #    System().makedirs(handoff_dir)
        #    os.chmod(handoff_dir, 0777)
        return handoff_dir



    def get_server_handoff_dir(my, ticket=None, include_ticket=True):
        if not ticket:
            security = Environment.get_security()
            ticket = security.get_ticket_key()

        if os.name == "nt":
            base_handoff_dir = Config.get_value("checkin", "win32_server_handoff_dir",\
                no_exception=True)
        else:
            base_handoff_dir = Config.get_value("checkin", "linux_server_handoff_dir",\
                no_exception=True)

        # if not, then it's the same as the client
        if not base_handoff_dir:
            handoff_dir = my.get_client_handoff_dir(ticket, include_ticket=include_ticket)
        else:
            if include_ticket:
                handoff_dir = "%s/%s" % (base_handoff_dir, ticket)
            else:
                handoff_dir = base_handoff_dir

        return handoff_dir



    def get_sandbox_dir():
        from pyasm.biz import PrefSetting
        base_dir = PrefSetting.get_value_by_key("sandbox_base_dir")
        if not base_dir:

            if Environment.get_env_object().get_client_os() =='nt':
                base_dir = Config.get_value("checkin","win32_sandbox_dir")
                if base_dir == "":
                    base_dir = Config.get_value("checkin","win32_local_base_dir")
                    base_dir += "/sandbox"
            else:
                base_dir = Config.get_value("checkin","linux_sandbox_dir")
                if base_dir == "":
                    base_dir = Config.get_value("checkin","linux_local_base_dir")
                    base_dir += "/sandbox"

        return base_dir
    get_sandbox_dir = staticmethod(get_sandbox_dir)


    def get_data_dir(manual=False):
        '''get the data directory. If manual is True, it will try to retrieve the manually set value instead of the Container'''
        # cache the data dir
        data_dir = ''
        if not manual:
            data_dir = Container.get("Environment:data_dir")
            if data_dir:
                return data_dir

        install_dir = Environment.get_install_dir()
        dirs = install_dir.split('/')
        dirs.pop()
        base_dir = '/'.join(dirs) 
        if hasattr(tacticenv, 'get_data_dir'):
            # verify user-defined data dir is under the base dir for Linux and ProgramData for Windows
            data_dir = tacticenv.get_data_dir()
            if not data_dir:
                # choose some arbitrary default
                if os.name == 'nt':
                    data_dir = 'C:/ProgramData/Tactic/Data'
                else:    
                    install_dir = Environment.get_install_dir()
                    dirs = install_dir.split('/')
                    dirs.pop()
                    data_dir = '%s/tactic_data' % base_dir
            else:
                data_dir = data_dir.replace("\\", "/")
     
            Container.put("Environment:data_dir", data_dir)

            return data_dir

        elif not manual:
            # this is consistent with install.py
            if os.name == 'nt':
                data_dir = 'C:/ProgramData/Tactic/Data'
            else:    
                install_dir = Environment.get_install_dir()
                dirs = install_dir.split('/')
                dirs.pop()
                data_dir = '%s/tactic_data' % base_dir
            
            Container.put("Environment:data_dir", data_dir)
            return data_dir


    get_data_dir = staticmethod(get_data_dir)



    def get_upgrade_dir(cls):
        '''get update base directory'''
        install_dir = cls.get_install_dir()
        return "%s/src/pyasm/search/upgrade" % install_dir
    get_upgrade_dir = classmethod(get_upgrade_dir)




    def get_asset_dir(file_object=None):
        '''get base asset directory'''
        asset_dir = Config.get_value("checkin","asset_base_dir")

        if file_object:
            base_dir_alias = file_object.get_value('base_dir_alias')
            if base_dir_alias:
                alias_dict = Config.get_value("checkin", "base_dir_alias", sub_key=base_dir_alias)
                asset_dir = alias_dict.get("asset_base_dir")

        if not asset_dir:
            data_dir = Environment.get_data_dir()
            if data_dir:
                asset_dir = "%s/assets" % data_dir

        return asset_dir

    get_asset_dir = staticmethod(get_asset_dir)

    
    def get_win32_client_repo_dir(cls):
        '''get base asset directory'''
        # FIXME: assumes windows client!!!
        return Config.get_value("checkin","win32_client_repo_dir")
    get_win32_client_repo_dir = classmethod(get_win32_client_repo_dir)



    def get_client_repo_dir(cls):
        '''get base asset directory'''
        # FIXME: assumes windows client!!!
        return Config.get_value("checkin","win32_client_repo_dir")
    get_client_repo_dir = classmethod(get_client_repo_dir)



    def get_base_url(my):
        '''get the url to access tactic'''
        # first assume localhost
        from pyasm.web import Url
        return Url("http://localhost")





    def get_security():
        return Container.get("Environment:security")
    get_security = staticmethod(get_security)

    def set_security(security):
        Container.put("Environment:security", security)
    set_security = staticmethod(set_security)


    def get_ticket():
        '''get the upload dir which relies on the ticket info'''
        security = Environment.get_security()
        ticket = security.get_ticket_key()
        return ticket
    get_ticket = staticmethod(get_ticket)



    def get_login():
        security = Environment.get_security()
        assert security
        return security.get_login()
    get_login = staticmethod(get_login)

    def get_user_name():
        login = Environment.get_login()
        if login:
            return login.get_login()
        else:
            return None
    get_user_name = staticmethod(get_user_name)

    def get_group_names():
        security = Environment.get_security()
        assert security
        return security.get_group_names()
    get_group_names = staticmethod(get_group_names)

 


    def get_app_name():
        return "Browser"
    get_app_name = staticmethod(get_app_name)


    def set_env_object(env_object):
        '''Stores the main environment container.  This is primarily
        used to get information that has specific implementations in
        the environment running.   For example, the main config path
        differs depending on whether a batch program is run, or whether
        the context is through the web
        '''
        Container.put("Environment:object", env_object)
    set_env_object = staticmethod(set_env_object)

    def get_env_object():
        env_object = Container.get("Environment:object")
        if env_object == None:
            raise EnvironmentException("Environment not initialised")
        return env_object
    get_env_object = staticmethod(get_env_object)


    def get():
        env_object = Container.get("Environment:object")
        if env_object == None:
            raise EnvironmentException("Environment not initialised")
        return env_object
    get = staticmethod(get)



    def has_env_object():
        return Container.has("Environment:object")
    has_env_object = staticmethod(has_env_object)


    def get_warning():
        return Container.get_seq('widget_warning')
    get_warning = staticmethod(get_warning)

    def add_warning(label, warning, type=''):
        # for now print it out
        print "WARNING: %s - %s, type[%s]" % (label, warning, type)
        warning = TacticWarning(label, warning, type)
        return Container.append_seq('widget_warning', warning)
    add_warning = staticmethod(add_warning)



    def get_release_version(cls):
        install_dir = cls.get_install_dir()
        path = "%s/VERSION" % install_dir
        if not os.path.exists(path):
            cls.add_warning("Release Version Error", "Cannot open file: %s" % path)
            return "???"

        file = open(path, 'r')
        line = file.readline()
        file.close()
        if not line:
            cls.add_warning("Release Version Error", "Cannot determine release version in file: %s" % path)
            return "???"
        #version = lines[0]
        version = line.strip()
        return version

    get_release_version = classmethod(get_release_version)



    def get_release_api_version(cls):
        install_dir = cls.get_install_dir()
        path = "%s/src/context/VERSION_API" % install_dir
        if not os.path.exists(path):
            cls.add_warning("Server API Version Error", "Cannot open file: %s" % path)
            return "???"

        file = open(path, 'r')
        line = file.readline()
        file.close()
        if not line:
            cls.add_warning("Server API Version Error", "Cannot determine release version in file: %s" % path)
            return "???"
        #version = lines[0]
        version = line.strip()
        return version

    get_release_api_version = classmethod(get_release_api_version)











