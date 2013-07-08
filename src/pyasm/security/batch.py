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
from security import Security

class Batch(Environment):
    '''Environment object that is used for batch operations'''
    def __init__(my, project_code=None, login_code=None):
        my.set_app_server("batch")

        super(Batch,my).__init__()

        my.login_code = login_code

        # clear the main container
        Container.create()

        # set this as the environment
        if not project_code:
            my.context = my.get_default_context()
        else:
            my.context = project_code

        Environment.set_env_object( my )

        # set up the security object
        security = Security()
        Environment.set_security(security)

        my._do_login()
        site_dir = Environment.get_site_dir()
        if site_dir not in sys.path:
            sys.path.insert(0, site_dir)

        # set the project
        from pyasm.biz import Project

        if my.context == "batch":
            Project.set_project("admin")
        else:
            Project.set_project(my.context)

        DbContainer.commit_thread_sql()


    def _do_login(my):
        security = Environment.get_security()
        security.login_as_batch(my.login_code)


    def __del__(my):
        # ensure that database connections are always closed
        if DbContainer:
            DbContainer.close_all()

    def get_default_context(my):
        return "batch"
        

    # context methods
    def set_context(my, context):
        my.context = context

    def get_context_name(my):
        return my.context


    def get_command_key(my):
        return Common.generate_random_key()





class XmlRpcInit(Environment):
    '''Used to authenticate using a ticket from an xmlrpc client'''

    def __init__(my, ticket):
        super(XmlRpcInit,my).__init__()

        my.set_app_server("xmlrpc")

        my.ticket = ticket

        # clear the main container
        #Container.clear()

        Environment.set_env_object( my )

        # set up the security object
        security = Security()
        Environment.set_security(security)

        my._do_login()


    def _do_login(my):

        security = Environment.get_security()
        ticket = security.login_with_ticket(my.ticket)

        if not ticket:
            raise SecurityException("Cannot login with key: %s. Session may have expired." % my.ticket)


class XmlRpcLogin(Environment):
    '''Used to login in a user from an xmlrpc client'''

    def __init__(my, login_name, password=None):
        super(XmlRpcLogin,my).__init__()

        my.set_app_server("xmlrpc")

        # If the tag <force_lowercase_login> is set to "true"
        # in the TACTIC config file,
        # then force the login string argument to be lowercase.
        # This tag is false by default.        
        my.login_name = login_name
        if Config.get_value("security","force_lowercase_login") == "true":
            my.login_name = my.login_name.lower()
        
        my.password = password

        # clear the main container
        #Container.clear()

        Environment.set_env_object( my )

        # set up the security object
        security = Security()
        Environment.set_security(security)

        my._do_login()


    def _do_login(my):

        security = Environment.get_security()

        require_password = Config.get_value("security", "api_require_password")
        api_password = Config.get_value("security", "api_password")

        # the xmlrpc login can be overridden to not require a password
        if require_password == "false":
            security.login_user_without_password(my.login_name, expiry="NULL")
        elif api_password:
            if api_password == my.password:
                security.login_user_without_password(my.login_name, expiry="NULL")
            else:
                # if api password is incorrect, still try and authenticate with
                # user's password
                security.login_user(my.login_name, my.password, expiry="NULL")

        else:        
            security.login_user(my.login_name, my.password, expiry="NULL")

        if not security.is_logged_in():
            raise SecurityException("Cannot login as user: %s." % my.login_name)





class TacticInit(Environment):
    '''Environment object that is used for Tactic Initiation'''
    def __init__(my, ticket=None):

        super(TacticInit,my).__init__()

        my.ticket = ticket

        # create the main container
        Container.create()

        Environment.set_env_object( my )

        # set up the security object
        security = Security()
        Environment.set_security(security)
     
