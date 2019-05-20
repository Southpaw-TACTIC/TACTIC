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

from pyasm.common import SecurityException, Config, Common
from security import Login
from drupal_password_hasher import DrupalPasswordHasher



class Authenticate(object):

    def __init__(self):
        self.login = None

    def get_login(self):
        return self.login

    def get_mode(self):
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

    def verify(self, login_name, password):
        '''Method to authenticate the user with a given login name and a
        given password

        @params:
        login_name: string value of the login.  Note that the login will
            contain a windows domain. ie: login_name = 'domain\foo'
        passwod: string value of the password
        '''
        # This function must be override and must return True to authenticate
        raise SecurityException("Custom Authenticate class must override verify method")


    def add_user_info(self, login, password=None):
        ''' sets all the information about the user'''
        # EXAMPLES
        #login.set_value("first_name", user.get_value("login") )
        #login.set_value("last_name", "")
        #login.set_value("email", "")
        pass


    # DEPRECATED as of 2.5
    def authenticate(self, login, password):
        # This function must be override and must return True to authenticate
        raise SecurityException("Must override authenticate method")


    def postprocess(self, login, ticket):
        pass



#
# The default authentication class
#
class TacticAuthenticate(Authenticate):
    '''Authenticate using the TACTIC database'''

    def verify(self, login_name, password):

        # get the login sobject from the database
        self.login = Login.get_by_login(login_name, use_upn=True)
        if not self.login:
            raise SecurityException("Login/Password combination incorrect")

        user_encrypted = sef.login.get_value("password")

        if user_encrypted.startswith("$S$"):
            salt = user_encrypted[4:12]
            iter_code = user_encrypted[3]
            #salt = Common.generate_alphanum_key(num_digits=8, mode='alpha')
            #iter_code = 'D'
            encrypted = DrupalPasswordHasher().encode(password, salt, iter_code)
        else:
            encrypted = hashlib.md5(password).hexdigest()

        # encrypt and check the password
        if encrypted != user_encrypted:
            raise SecurityException("Login/Password combination incorrect")
        return True


    def add_user_info(self, login, password):

        mode = Config.get_value("security", "authenticate_encryption")
        if mode == "drupal":
            salt = Common.generate_alphanum_key(num_digits=8, mode='alpha')
            iter_code = 'D'
            encrypted = DrupalPasswordHasher().encode(password, salt, iter_code)
        else:
            encrypted = hashlib.md5(password).hexdigest()

        login.set_value("password", encrypted)
        

    # DEPRECATED
    def authenticate(self, login, password):
        raise Exception("TacticAuthenticate.authenticate() is DEPRECATED")
        
        # encrypt and check the password
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

    def verify(self, login_name, password):
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




