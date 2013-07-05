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

__all__ = ["Authenticate", 'TacticAuthenticate', 'LdapAuthenticate']

import hashlib

from pyasm.common import SecurityException, Config
from security import Login

class Authenticate(object):

    def __init__(my):
        my.login = None

    def get_login(my):
        return my.login

    def get_mode(my):
        '''determines the mode of the authentication process. There are 3 types
        of authentications modes:

        default: gets the user info from the sthpw/login search type
        cache: gets the user info from an outside source on every login
        autocreate: gets the user info from an outside source once and uses
            this information from then on

        The active directory module uses cache mode while the internal
        TACTIC authentication module uses default.  "autocreate" is not used
        very often.
        '''
        return 'default'

    def verify(my, login_name, password):
        '''Method to authenticate the user with a given login name and a
        given password

        @params:
        login_name: string value of the login.  Note that the login will
            contain a windows domain. ie: login_name = 'domain\foo'
        passwod: string value of the password
        '''
        # This function must be override and must return True to authenticate
        raise SecurityException("Custom Authenticate class must override verify method")


    def add_user_info(my, login, password=None):
        ''' sets all the information about the user'''
        # EXAMPLES
        #login.set_value("first_name", user.get_value("login") )
        #login.set_value("last_name", "")
        #login.set_value("email", "")
        pass


    # DEPRECATED as of 2.5
    def authenticate(my, login, password):
        # This function must be override and must return True to authenticate
        raise SecurityException("Must override authenticate method")



#
# The default authentication class
#
class TacticAuthenticate(Authenticate):
    '''Authenticate using the TACTIC database'''

    def verify(my, login_name, password):

        #encrypted = md5.new(password).hexdigest()
        encrypted = hashlib.md5(password).hexdigest()

        # get the login sobject from the database
        my.login = Login.get_by_login(login_name)
        if not my.login:
            raise SecurityException("Login/Password combination incorrect")

        # encrypt and check the password
        if encrypted != my.login.get_value("password"):
            raise SecurityException("Login/Password combination incorrect")
        return True


    def add_user_info(my, login, password):
        #encrypted = md5.new(password).hexdigest()
        encrypted = hashlib.md5(password).hexdigest()
        login.set_value("password", encrypted)
        


    # DEPRECATED
    def authenticate(my, login, password):
        # encrypt and check the password
        #encrypted = md5.new(password).hexdigest()
        encrypted = hashlib.md5(password).hexdigest()
        if encrypted != login.get_value("password"):
            raise SecurityException("Login/Password combination incorrect")
        return True



#
# Some examples of custom authentication classes
#
class UnixAuthenticate(Authenticate):
    '''Authenticate using Unix logins'''
    pass


class LdapAuthenticate(Authenticate):
    '''Authenticate using LDAP logins'''

    def verify(my, login_name, password):
        path = Config.get_value("checkin", "ldap_path")
        server = Config.get_value("checkin", "ldap_server")
        assert path, server

        path = path.replace("{login}", login_name)

        import ldap

        try:
            l = ldap.open(server)
            l.simple_bind_s(path, password)
            return True
        except:
            raise SecurityException("Login/Password combination incorrect")




