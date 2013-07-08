##########################################################
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

__all__ = ['WebEnvironmentException', 'WebEnvironment']

import os

from pyasm.common import Environment, Config, Marshaller, System
from pyasm.biz import PrefSetting, Project
from web_container import WebContainer

from widget import Url, WidgetSettings
from palette import Palette

class WebEnvironmentException(Exception):
    pass


class WebEnvironment(Environment):
    '''abstract class that defines an interface for access to web
    functionality.  This protects the framework from the various
    implementations such as webware, mod_python, twisted, etc'''
    ARG_NAME = 'args'


    def get_form_keys(my):
        raise WebEnvironmentException("must override [get_form_keys] method")

    def get_form_args(my, arg_name=None):
        '''it assumes that name=value pairs are separated by ||
        returns a dict with form_parm_name as key mapped to its value'''

        if arg_name == None:
            arg_name = WebEnvironment.ARG_NAME
        args_string = my.get_form_value(arg_name)
        if args_string.strip() == '':
            return {}
        pairs = args_string.split("||")
        args = {}
        for pair in pairs:
            name, value = pair.split("=",1)
            args[name] = value
        return args
    
    def set_form_value(my, name, value):
        """ returns a string list of the values of a form element"""
        raise WebEnvironmentException("must override [set_form_value] method")


    def get_form_values(my, name):
        """ returns a string list of the values of a form element"""
        raise WebEnvironmentException("must override [get_form_values] method")


    def get_form_value(my, name):
        """returns the string value of the form element"""
        raise WebEnvironmentException("must override [get_form_value] method")


    def get_int_form_value(my, name):
        value = my.get_form_value(name)
        try:
            int_value = int(value)
        except:
            int_value = 0
        return int_value

    def get_sobject_from_form(my):
        search_type = my.get_form_value("search_type")
        search_id = my.get_form_value("search_id")
        from pyasm.search import Search
        sobject = Search.get_by_id(search_type, search_id)
        return sobject



    def set_cookie(my, name, value):
        """set a cookie"""
        raise WebEnvironmentException("must override [set_cookie] method")

    def get_cookie(my, name):
        """get a cookie"""
        raise WebEnvironmentException("must override [get_cookie] method")


    def get_env(my, env_var):
        raise WebEnvironmentException("must override [get_env] method")

    def get_app_name(my):
        ''' determine what app tactic is running in '''
        user_agent = my.get_env("HTTP_USER_AGENT")

        if not user_agent:
            return ""

        if user_agent.find("Maya") != -1:
            return "Maya"
        elif user_agent.find("Houdini") != -1:
            return "Houdini"
        elif user_agent.find("xmlrpclib") != -1:
            return "XMLRPC"
        else:
            return "Browser"

    def get_selected_app(my):
        '''Make Maya the default'''
        app = WidgetSettings.get_value_by_key('app|select')
        if app == 'Maya':
            return 'Maya'
        elif app == 'Houdini':
            return 'Houdini'
        elif app == 'XSI':
            return 'XSI'
        else:
            return 'Maya'


    def get_app_name_by_uri(my):
        ''' determine what app tactic is running in '''
        uri = my.get_env("REQUEST_URI")
        if not uri:
            app = "Browser"
        elif uri.find("Maya") != -1:
            app = "Maya"
        elif uri.find("Houdini") != -1:
            app = "Houdini"
        elif uri.find("XSI") != -1:
            app = "XSI"
        else:
            # try the user agent
            app = my.get_app_name()
            #return "Browser"

        return app

    
    def get_app_server_name(my):
        return os.getenv("TACTIC_APP_SERVER")


    # tactic standard directories
    def get_icon_web_dir(my):
        return "/context/icons"


    def get_http_host(my):
        host = my.get_env("HTTP_HOST")
        return host

    def get_base_url(my):
        host = my.get_http_host()

        # see if there is a protocol defined
        protocol = Config.get_value("security", "protocol")
        if not protocol:
            protocol = "http"

        # FIXME: not sure about this.
        if host == "127.0.0.1":
            base_url = Config.get_value("install", "base_url")
        else:
            base_url = "%s://%s" % (protocol, host)

        return Url(base_url)

    
    def get_context_url(my):
        '''this is used to get the .js and .css files'''
        url = Url("/context")
        return url


    def get_site_root(my):
        return "tactic"


    def get_site_url(my):
        site_root = my.get_site_root()
        url = Url("/%s" % site_root)
        return url


    def get_site_context_url(my):
        site_url = my.get_site_url()
        site_url.append_to_base( my.get_context_name() )
        return site_url


    def get_project_url(my):
        site_url = my.get_site_url()
        project_code = Project.get_project_code()
        site_url.append_to_base( project_code )
        return site_url



    def get_request_host(my):
        ip = my.get_env("HTTP_X_FORWARDED_FOR")
        if not ip:
            ip = my.get_env("REMOTE_ADDR") 

        if not ip:
            raise TacticException('Client IP cannot be found!')
            
        return ip


    def is_admin_page(my):
        project_code = Project.get_project_code()
        request_url = my.get_request_url()
        request_str = request_url.to_string()
        if request_str.endswith("/%s/admin" % project_code) or \
                request_str.endswith("/admin/Index"):
            return True
        else:
            return False


    def is_title_page(my):
        project_code = Project.get_project_code()
        return project_code == 'admin' and my.get_request_url().to_string().endswith("/tactic/Index")


    def get_request_url(my):
        request_uri = my.get_env("REQUEST_URI")
        query_string = ""
        if request_uri.find("?") != -1:
            request_uri, query_string = request_uri.split("?", 1)

        if request_uri.endswith("/"):
            request_uri = "%sIndex" % request_uri

        url = Url(request_uri)

        # break up the query string
        if query_string != "":
            pairs = query_string.split("&")
            for pair in pairs:
                tmp = pair.split("=")
                name = tmp[0]
                if len(tmp) == 2:
                    value = tmp[1]
                else:
                    value = ""
                url.set_option(name,value)
        
        return url



    def get_client_api_url(my):
        '''get the url for upload server'''
        base_url = my.get_base_url()
        site_root = my.get_site_root()
        base_url.append_to_base( "/%s/default/Api" % site_root)
        return base_url.to_string()


    def get_upload_url(my):
        '''get the url for upload server'''
        base_url = my.get_base_url()
        site_root = my.get_site_root()
        if my.get_app_server_name() == "webware":
            base_url.append_to_base( "/%s/default/UploadServer" % site_root)
        else:
            base_url.append_to_base( "/%s/default/UploadServer/" % site_root)
        return base_url.to_string()



    def get_copy_base_url(my):
        
        return Config.get_value("checkin","copy_base_url")
       


    def get_widget_url(my):

        url = my.get_site_url()
        url.append_to_base( "default" )
        
        project_code = Project.get_project_code()
        url.set_option("project", project_code)

        url.append_to_base("WidgetServer/")
        return url


    def get_context_dir(my):
        return '%s/src/context' % Environment.get_install_dir()

    def get_local_dir(my):
        '''get the local asset directory on the client machine'''
        user_agent = my.get_env("HTTP_USER_AGENT")
        if user_agent.startswith("Houdini"):
            dir = Config.get_value("checkin", "win32_local_base_dir")

        elif user_agent.find("Windows") != -1:
            dir = Config.get_value("checkin", "win32_local_base_dir")
        else:
            dir = Config.get_value("checkin", "linux_local_base_dir")

        return dir

    def get_browser(my):
        '''determines which browser we are running'''
        user_agent = my.get_env("HTTP_USER_AGENT")

        if not user_agent:
            return ""

        if user_agent.find("MSIE") != -1:
            browser = "IE"
        elif user_agent.find("Qt") != -1:
            browser = "Qt"
        elif user_agent.find("WebKit") != -1:
            browser = "Webkit"
        elif user_agent.find("Mozilla") != -1:
            browser = "Mozilla"
        else:
            browser = "Mozilla"

        return browser


    def is_IE(my):
        if my.get_browser() == "IE":
            return True
        else:
            return False


    # define the context information
    def get_context_name(my):
        '''this includes all of the subdirectories as well as the main
        context'''
        raise EnvironmentException("Must override this method")

    def get_full_context_name(my):
        '''Same as get_context_name().  This is DEPRECATED'''
        return my.get_context_name()



    # overridden from envirnoment
    def get_command_key(my):
        command_key = my.get_form_value("form_key")
        return command_key


    # adding support for touch devices
    def is_touch_device(my):
        if my.get_client_os() in [ 'apple_ios', 'android' ]:
            return True
        return False


    def get_client_os(my):
        user_agent = my.get_env("HTTP_USER_AGENT")
        if not user_agent:
            return os.name

        if user_agent.find("Windows") != -1:
            return "nt"
        elif user_agent.find("like Mac OS X") != -1:
            return "apple_ios"
        elif user_agent.find("Mac OS X") != -1:
            return "osx"
        elif user_agent.find("Linux") != -1:
            return "linux"
        elif user_agent.find("Android") != -1:
            return "android"
        else: # default
            # FIXME: why are we defaulting to NT? If anything an unknown OS will probably be unix/linux based
            #        and not Windows based ... we should really default to 'linux'. But not changing this at
            #        this time.
            #
            # default to nt (should raise exception)
            return "nt"
        

    def get_skin(my):
        # DEPRECATED: replaced by palettes

        # TODO: prod setting shouldn't be in prod!!!
        from pyasm.prod.biz import ProdSetting
        web = WebContainer.get_web()
        skin = web.get_form_value("skin")

        # look at users preferences
        if not skin:
            skin = PrefSetting.get_value_by_key("skin")

        # if skin isn't found in user preference settings then look for it
        # in the projects/config XML file ...
        if not skin:
            skin = Config.get_value("look", "skin")

        if not skin:
            skin = "dark"

        # MMS-TACTIC ... allow for 'MMS' skin to be returned for use in overriding some colors (MMS is a copy of
        # 'dark' skin)
        if skin == 'MMS':
            return 'MMS'

        return "dark"




    def get_palette(cls):
        return Palette.get()
    get_palette = classmethod(get_palette)



    def get_top_class_name(cls):
        project = Project.get()
        class_name = project.get_value("top_class_name", no_exception=True)
        if not class_name:
            class_name = Config.get_value("install", "top_class_name")
        if not class_name:
            class_name = 'tactic.ui.app.PageNavContainerWdg'
        return class_name
    get_top_class_name = classmethod(get_top_class_name)


    # TODO: not in use yet
    def get_header_class_name(cls):
        project = Project.get()
        class_name = project.get_value("header_class_name", no_exception=True)
        if not class_name:
            class_name = Config.get_value("install", "header_class_name")
        if not class_name:
            class_name = 'tactic.ui.app.PageNavContainerWdg'
        return class_name
    get_header_class_name = classmethod(get_header_class_name)






