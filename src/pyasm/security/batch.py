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

__all__ = ['Batch', 'XmlRpcInit', 'XmlRpcLogin', 'TacticInit']

import os, sys

from pyasm.common import Environment, Container, Config, Common, SecurityException

from pyasm.search import DbContainer
from security import Security, Site

class Batch(Environment):
    '''Environment object that is used for batch operations'''
    def __init__(self, project_code=None, login_code=None, site=None):
        self.set_app_server("batch")

        if not site:
            # if not explicitly set, keep the current site
           site = Site.get_site() 


        plugin_dir = Environment.get_plugin_dir()
        if plugin_dir not in sys.path:
            sys.path.insert(0, plugin_dir)

        super(Batch,self).__init__()

        self.login_code = login_code

        # clear the main container
        Container.create()

        if site:
            Site.set_site(site)

        # set this as the environment
        if not project_code:
            self.context = self.get_default_context()
        else:
            self.context = project_code

        Environment.set_env_object( self )

        # set up the security object
        security = Security()
        Environment.set_security(security)

        self._do_login()
        site_dir = Environment.get_site_dir()
        if site_dir not in sys.path:
            sys.path.insert(0, site_dir)

        # set the project
        from pyasm.biz import Project

        if self.context == "batch":
            Project.set_project("admin")
        else:
            Project.set_project(self.context)

        self.initialize_python_path()


        # start workflow engine
        #from pyasm.command import Workflow
        #Workflow().init()

        DbContainer.commit_thread_sql()



    def _do_login(self):
        security = Environment.get_security()
        security.login_as_batch(self.login_code)


    def __del__(self):
        # ensure that database connections are always closed
        if DbContainer:
            DbContainer.close_all()

    def get_default_context(self):
        return "batch"
        

    # context methods
    def set_context(self, context):
        self.context = context

    def get_context_name(self):
        return self.context


    def get_command_key(self):
        return Common.generate_random_key()





class XmlRpcInit(Environment):
    '''Used to authenticate using a ticket from an xmlrpc client'''

    def __init__(self, ticket, site=None):
        super(XmlRpcInit,self).__init__()


        if not site:
            # if not explicitly set, keep the current site
           site = Site.get_site() 

        self.set_app_server("xmlrpc")

        self.ticket = ticket


        # clear the main container
        #Container.clear()

        Environment.set_env_object( self )

        # set up the security object
        security = Security()
        Environment.set_security(security)


        if site:
            Site.set_site(site)

        self._do_login()


    def _do_login(self):

        allow_guest = Config.get_value("security", "allow_guest")
        if allow_guest == 'true':
            allow_guest = True
        else:
            allow_guest = False

        security = Environment.get_security()
        login = security.login_with_ticket(self.ticket, allow_guest=allow_guest)

        if not login:
            raise SecurityException("Cannot login with key: %s. Session may have expired." % self.ticket)


class XmlRpcLogin(Environment):
    '''Used to login in a user from an xmlrpc client'''

    def __init__(self, login_name, password=None):
        super(XmlRpcLogin,self).__init__()

        self.set_app_server("xmlrpc")

        # If the tag <force_lowercase_login> is set to "true"
        # in the TACTIC config file,
        # then force the login string argument to be lowercase.
        # This tag is false by default.        
        self.login_name = login_name
        if Config.get_value("security","force_lowercase_login") == "true":
            self.login_name = self.login_name.lower()
        
        self.password = password

        # clear the main container
        #Container.clear()

        Environment.set_env_object( self )

        # set up the security object
        security = Security()
        Environment.set_security(security)

        self._do_login()


    def _do_login(self):

        security = Environment.get_security()

        require_password = Config.get_value("security", "api_require_password")
        api_password = Config.get_value("security", "api_password")

        site = Site.get()
        allow_guest =  site.allow_guest()

        # the xmlrpc login can be overridden to not require a password
        if require_password == "false" or (allow_guest and self.login_name == "guest"):
            security.login_user_without_password(self.login_name, expiry="NULL")
        elif api_password:
            if api_password == self.password:
                security.login_user_without_password(self.login_name, expiry="NULL")
            else:
                # if api password is incorrect, still try and authenticate with
                # user's password
                security.login_user(self.login_name, self.password, expiry="NULL")
        elif self.login_name == "guest":
                security.login_user_without_password(self.login_name)
        else:        
            security.login_user(self.login_name, self.password, expiry="NULL")

        if not security.is_logged_in():
            raise SecurityException("Cannot login as user: %s." % self.login_name)





class TacticInit(Environment):
    '''Environment object that is used for Tactic Initiation'''
    def __init__(self, ticket=None):

        super(TacticInit,self).__init__()

        self.ticket = ticket

        # create the main container
        Container.create()

        Environment.set_env_object( self )

        # set up the security object
        security = Security()
        Environment.set_security(security)
     
