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

from .common import *
from .container import *
from .base import *
from .config import *
from .system import *
from .common_exception import TacticWarning, TacticException

class EnvironmentException(Exception):
    pass



class Environment(Base):
    """class which encapsulates the environment the framework is running
    under"""

    # global function for all threads.
    IS_INITIALIZED = False

    def __init__(self):
        self.initialize_python_path()

        if not Environment.IS_INITIALIZED:
            self.initialize()
            Environment.IS_INITIALIZED = True

        # set the temp dir
        import tempfile
        tmp_dir = Config.get_value("install", "tmp_dir")
        if tmp_dir:
            tempfile.tempdir = "%s/temp" % tmp_dir



       

    def initialize_python_path(self):
        # add some paths
        paths = Config.get_value("services", "python_path", no_exception=True)
        paths_list = paths.split("|")
        for path in paths_list:
            sys.path.append(path)

        # insert the plugin path
        plugin_dir = Environment.get_plugin_dir()
        if plugin_dir not in sys.path:
            sys.path.insert(0, plugin_dir)


    def initialize(self):
        '''Initializes the enviroment outside environment Tactic.  This is
        can be used for both the web environment and the batch environment'''

        # skips if TACTIC_CLEANUP is not true
        if not os.environ.get("TACTIC_CLEANUP") == 'true':
            return
      

        # is tactic configured/installed?
        is_installed = False
        if is_installed:
            # get the config file and read it for errors
            config_path = self.get_config_path()
            if not os.path.exists(config_path):
                raise EnvironmentException("Config file [%s] does not exist" % config_path)

            install_dir = self.get_install_dir()
            if not os.path.exists(install_dir):
                raise EnvironmentException("Install dir [%s] does not exist" % install_dir)

            # DEPRECATED
            #site_dir = self.get_site_dir()
            #if not os.path.exists(site_dir):
            #    raise EnvironmentException("Site dir [%s] does not exist" % site_dir)

            asset_dir = self.get_asset_dir()
            if not os.path.exists(asset_dir):
                raise EnvironmentException("Asset dir [%s] does not exist" % asset_dir)


        # create all of the temp directories
        # TODO: is this relevant for batch processes
        tmp_dir = self.get_tmp_dir()
        dirs = []
        dirs.append("%s/upload" % tmp_dir)
        dirs.append("%s/download" % tmp_dir)
        dirs.append("%s/handoff" % tmp_dir)
        dirs.append("%s/cache" % tmp_dir)
        dirs.append("%s/upload" % tmp_dir)
        dirs.append("%s/temp" % tmp_dir)
        plugin_dir = self.get_plugin_dir()
        dirs.append(plugin_dir)

        for dir in dirs:
            System().makedirs(dir)
            try:
                os.chmod(dir, 0o775)
            except OSError as e:
                print("WARNING: cannot chmod: ", e)


        # remove the sidebar cache
        sidebar_cache_dir = "%s/cache/side_bar" % tmp_dir
        if os.path.exists(sidebar_cache_dir):
            import shutil
            try:
                shutil.rmtree(sidebar_cache_dir)
            except Exception as e:
                print("Error deleting cache files:", e)

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


    def get_transfer_mode(self):
        repo_dir = Config.get_value("checkin", "win32_client_repo_dir")
        if repo_dir:
            transfer_mode = 'client_repo'
        else:
            transfer_mode = 'web'

        return transfer_mode



    # methods that should be overridden by implementation of the
    # environment
    def get_context_name(self):
        '''get the path for configruation file for the framework'''
        raise EnvironmentException("This function must be overridden")


    def get_command_key(self):
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



    def get_tmp_dir(include_ticket=False):
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


        if include_ticket:
            security = Environment.get_security()
            ticket = security.get_ticket_key()
            if not ticket:
                raise Exception("No ticket found")
            tmp_dir = "%s/temp/%s" % (tmp_dir, ticket)

            # only if a ticket is needed, the make the directory
            if not os.path.exists(tmp_dir):
                os.makedirs(tmp_dir)

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



    def get_builtin_plugin_dir(cls):
        install_dir = cls.get_install_dir()
        builtin_plugin_dir = "%s/src/plugins" % install_dir
        return builtin_plugin_dir
    get_builtin_plugin_dir = classmethod(get_builtin_plugin_dir)


    def get_plugin_dir(cls):
        base_plugin_dir = Config.get_value("install","plugin_dir")
        if not base_plugin_dir:
            data_dir = cls.get_data_dir()
            base_plugin_dir = "%s/plugins" % data_dir

        return base_plugin_dir
    get_plugin_dir = classmethod(get_plugin_dir)



    def is_builtin_plugin(src, plugin_code):
        # Use this simple rule for now
        if plugin_code.startswith("TACTIC"):
            return True
        else:
            return False
    is_builtin_plugin = classmethod(is_builtin_plugin)


    def get_dist_dir(cls):
        data_dir = cls.get_data_dir()
        base_dist_dir = "%s/dist" % data_dir
        return base_dist_dir
    get_dist_dir = classmethod(get_dist_dir)




    def get_template_dir(cls):
        data_dir = cls.get_data_dir()
        base_template_dir = "%s/templates" % data_dir
        return base_template_dir
    get_template_dir = classmethod(get_template_dir)




    def get_client_handoff_dir(self, ticket=None, no_exception=False, include_ticket=True):
        if Environment.get_env_object().get_client_os() =='nt':
            base_handoff_dir = Config.get_value("checkin", "win32_client_handoff_dir", no_exception=True)
        else:
            base_handoff_dir = Config.get_value("checkin", "linux_client_handoff_dir", no_exception=True)


        if not base_handoff_dir:
            tmp_dir = self.get_tmp_dir()
            base_handoff_dir = "%s/%s" % (tmp_dir, "handoff")
                

        if no_exception == False and not base_handoff_dir:
            raise TacticException("No handoff directory defined in TACTIC config file")


        if include_ticket and not ticket:
            security = Environment.get_security()
            ticket = security.get_ticket_key()


        if include_ticket:
            handoff_dir = "%s/%s" % (base_handoff_dir, ticket)
        else:
            handoff_dir = base_handoff_dir

        # can't create this because it may be different on the server
        #if not os.path.exists(handoff_dir):
        #    System().makedirs(handoff_dir)
        #    os.chmod(handoff_dir, 0777)
        return handoff_dir



    def get_server_handoff_dir(self, ticket=None, include_ticket=True):
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
            handoff_dir = self.get_client_handoff_dir(ticket, include_ticket=include_ticket)
        else:
            if include_ticket:
                handoff_dir = "%s/%s" % (base_handoff_dir, ticket)
            else:
                handoff_dir = base_handoff_dir

        return handoff_dir



    def get_sandbox_dir(alias=None):

        from pyasm.biz import PrefSetting
        base_dir = PrefSetting.get_value_by_key("sandbox_base_dir")
        client_os = Environment.get_env_object().get_client_os()

        if not base_dir:

            if alias:
                if client_os == "nt":
                    alias_dict = Config.get_dict_value("checkin", "win32_sandbox_dir")
                else:
                    alias_dict = Config.get_dict_value("checkin", "linux_sandbox_dir")

                if not alias_dict:
                    alias_dict = Config.get_dict_value("checkin", "sandbox_dir")

                base_dir = alias_dict.get("default")

        if not base_dir:
            if client_os == "nt":
                base_dir = "C:/tactic/sandbox"
            else:
                base_dir = "/tmp/snadbox"


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


    def get_asset_dirs(cls):
        alias_dict = Config.get_dict_value("checkin", "asset_base_dir")

        # add in an implicit plugin dir
        if not alias_dict.get("plugins"):
            alias_dict['plugins'] = cls.get_plugin_dir()

        # for backwards compatibility:
        alias_dict2 = Config.get_dict_value("checkin", "base_dir_alias")
        if alias_dict2:
            for key,value in alias_dict2.items():
                alias_dict[key] = value

        return alias_dict
    get_asset_dirs = classmethod(get_asset_dirs)

    def get_asset_dir(cls, file_object=None, alias=None):
        '''get base asset directory'''

        if file_object:
            alias = file_object.get_value('base_dir_alias')

        if not alias:
            alias = "default"


        from pyasm.security import Site
        asset_dir = Site.get().get_asset_dir(file_object=file_object,alias=alias)
        if asset_dir:
            return asset_dir


        alias_dict = cls.get_asset_dirs()
        asset_dir = alias_dict.get(alias)

        if not asset_dir:
            data_dir = Environment.get_data_dir()
            if data_dir:
                asset_dir = "%s/assets" % data_dir


        return asset_dir

    get_asset_dir = classmethod(get_asset_dir)


    def get_web_dirs(cls):

        alias_dict = Config.get_dict_value("checkin", "web_base_dir")

        # add in an implicit plugin dir
        if not alias_dict.get("plugins"):
            alias_dict['plugins'] = "/plugins"

        # for backwards compatibility:
        alias_dict2 = Config.get_dict_value("checkin", "base_dir_alias")
        if alias_dict2:
            for key,value in alias_dict2.items():
                alias_dict[key] = value

        return alias_dict
    get_web_dirs = classmethod(get_web_dirs)


    def get_web_dir(cls, file_object=None, alias=None):
        '''get base web directory'''

        if file_object:
            alias = file_object.get_value('base_dir_alias')

        if not alias:
            alias = "default"

        from pyasm.security import Site
        site = Site.get()
        web_dir = site.get_web_dir(file_object=file_object,alias=alias)
        if web_dir:
            return web_dir


        alias_dict = cls.get_web_dirs()
        web_dir = alias_dict.get(alias)

        if not web_dir:
            web_dir = "/assets"

        return web_dir
    get_web_dir = classmethod(get_web_dir)


    
    def get_win32_client_repo_dir(cls):
        '''get base asset directory'''
        # FIXME: assumes windows client!!!
        return Config.get_value("checkin","win32_client_repo_dir")
    get_win32_client_repo_dir = classmethod(get_win32_client_repo_dir)



    def get_client_repo_dir(cls):
        '''get base client repo directory'''
        if Environment.get_env_object().get_client_os() =='nt':
            return Config.get_value("checkin","win32_client_repo_dir")
        else:
            return Config.get_value("checkin","linux_client_repo_dir")
    get_client_repo_dir = classmethod(get_client_repo_dir)



    def get_base_url(cls):
        '''get the url to access tactic'''
        # first assume localhost
        from pyasm.web import Url
        server = Config.get_value("install", "hostname")
        return Url("http://%s" % server)
    get_base_url = classmethod(get_base_url)




    def get_security():
        return Container.get("Environment:security")
    get_security = staticmethod(get_security)

    def set_security(security):
        Container.put("Environment:security", security)

    set_security = staticmethod(set_security)

    def set_security_list(security_list):
        Container.put("Environment:security_list", security_list)
    set_security_list = staticmethod(set_security_list)


    def get_ticket():
        '''get the upload dir which relies on the ticket info'''
        security = Environment.get_security()
        if not security:
            return ""
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
        print("WARNING: %s - %s, type[%s]" % (label, warning, type))
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



    def get_api_mode(cls):
        # let the site override
        from pyasm.security import Site
        api_mode = Site.get().get_api_mode()

        # else use the config
        if not api_mode:
            api_mode = Config.get_value("security", "api_mode")

        if not api_mode:
            api_mode = "open"

        return api_mode

    get_api_mode = classmethod(get_api_mode)





