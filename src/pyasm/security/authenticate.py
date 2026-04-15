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

import hashlib, sys

from pyasm.common import SecurityException, Config, Common
from .security import Login
from .drupal_password_hasher import DrupalPasswordHasher

from datetime import datetime, timedelta


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


    def reset_password(self, login, password):
        """reset the password
        """
        raise SecurityException("Must override reset_password method")



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

        if self.login:
            password_expiry = Config.get_value("security", "password_expiry")
            password_expiry = password_expiry.strip()
            if password_expiry and not self.login.check_password_expiry():
                raise SecurityException("Password expired. Please reset by clicking on Forgot your password link.")

            invalid_login_attempts = Config.get_value("security", "invalid_login_attempts")
            invalid_login_attempts = invalid_login_attempts.strip()
            if invalid_login_attempts and not self.login.check_invalid_logins(int(invalid_login_attempts)):
                raise SecurityException("Too many login attempts. Please reset your password.")


        user_encrypted = self.login.get_value("password")

        if user_encrypted.startswith("$S$"):
            salt = user_encrypted[4:12]
            iter_code = user_encrypted[3]
            #salt = Common.generate_alphanum_key(num_digits=8, mode='alpha')
            #iter_code = 'D'
            encrypted = DrupalPasswordHasher().encode(password, salt, iter_code)
        else:
            # kept here for backwards compatibility
            encrypted = hashlib.md5(password.encode()).hexdigest()

        # encrypt and check the password
        if encrypted != user_encrypted:
            self.increment_login_attempt(self.login)
            raise SecurityException("Login/Password combination incorrect")
        self.increment_login_attempt(self.login, reset=True)

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

    def reset_password(self, login, password):
        """reset the password
        """
        encrypted = Login.encrypt_password(password)
        login.set_value('password', encrypted)

        # previous passwords
        data = login.get("data") or {}
        previous_passwords = []
        if data:
            previous_passwords = data.get("previous_passwords")
            if not previous_passwords:
                previous_passwords = []

        previous_passwords.append(encrypted)
        if len(previous_passwords) > 3:
            previous_passwords.pop(0)
        data["previous_passwords"] = previous_passwords

        # password expiry
        password_expiry_days = 90
        password_expiry = Config.get_value("security", "password_expiry")
        password_expiry = password_expiry.strip()
        if password_expiry:
            try:
                password_expiry_days = int(password_expiry)
            except:
                raise Exception("Check password_expiry config value.")
        expiry = datetime.now() + timedelta(days=password_expiry_days)
        data["password_expiry"] = expiry

        # invalid_login_attempt reset
        data["invalid_logins"] = 0

        login.set_value("data", data)
        login.commit()


    def increment_login_attempt(self, login, reset=False):
        """This will increment the login attempt count by 1.
        If reset is true, it will set the count to 0.
        """
        invalid_login_attempts = Config.get_value("security", "invalid_login_attempts")
        invalid_login_attempts = invalid_login_attempts.strip()
        if not invalid_login_attempts:
            return


        data = login.get("data") or {}
        invalid_logins = 0
        if data:
            invalid_logins = data.get("invalid_logins")
            # ask Remko. how to check. This is what I saw at 2 factor expiry:
            # != "__NONE___"
            if invalid_logins:
                invalid_logins = int(invalid_logins)
                invalid_logins += 1
            else:
                invalid_logins = 1
            if reset:
                invalid_logins = 0
        data["invalid_logins"] = invalid_logins
        login.set_value("data", data)
        login.commit()



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


"""
class LdapADAuthenticate(Authenticate):
    '''Authenticate using LDAP Active Directory logins'''

    def verify(self, login_name, password):

        import ldap

        server = Config.get_value("security", "ldap_server")
        bind_dn = Config.get_value("security", "bind_dn")
        bind_password = Config.get_value("security", "bind_password")
        base_dn = Config.get_value("security", "base_dn")

        scope = ldap.SCOPE_SUBTREE
        filter = "(&(objectClass=*)(sAMAccountName=%s))" % login_name
        attrs = ['*']


        try:
            l = ldap.initialize(server)
            l.protocol_version = 3
            l.set_option(ldap.OPT_REFERRALS, 0)
            l.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, 0)

            l.simple_bind_s(bind_dn, bind_password) # we are going to bind with a service account

            r = l.search(base_dn, scope, filter)

            Type, user = l.result(r,60)

            name, attrs = user[0]

            if hasattr(attrs, 'has_key') and attrs.has_key('distinguishedName'):
                distinguishedName = attrs['distinguishedName'][0]
                l.simple_bind_s(distinguishedName, password)

            return True

        except Exception as e:
            raise SecurityException("Login/Password combination incorrect: 203")

"""


