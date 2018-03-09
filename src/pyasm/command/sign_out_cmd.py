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

__all__ = ["SignOutCmd", "PasswordEditCmd"]


from pyasm.common import Environment, UserException
from command import *
from pyasm.search import SearchKey

import hashlib
class SignOutCmd(Command):
    '''Sign out command'''

    def __init__(self, **kwargs):
        self.login_name = ''
        super(SignOutCmd, self).__init__(**kwargs)

    def is_undoable(cls):
        return False
    is_undoable = classmethod(is_undoable)

    def get_title(self):
        return "Sign Out Command"


    def set_login_name(self, login_name):
        self.login_name = login_name

    def check(self):
        return True

    def execute(self):

        if not self.login_name:
            self.login_name = self.kwargs.get('login');

        # invalidate the ticket
        security = Environment.get_security()
        ticket = security.get_ticket()

        if ticket == None:
            return


        login_name = ticket.get_value("login")
        print "Signing out: ", login_name

        # expire the ticket

        from pyasm.security import Site
        site = Site.get()
        if site:
            Site.set_site("default")

        try:
            from pyasm.search import Sql, DbContainer
            sql = DbContainer.get("sthpw")
            ticket.set_value("expiry", sql.get_timestamp_now(), quoted=False)
            ticket.commit()
        except:
            if site:
                Site.pop_site()



    def check_security(self):
        '''give the command a callback that allows it to check security'''
        return True


class PasswordEditCmd(Command):
    '''encrypts the entered password with md5 encryption'''

    def get_title(self):
        return "Password Change"

    def init(self):
        self.old_password = ''
        self.password = ''
        self.re_enter = ''

    def check(self):
        search_key = self.kwargs.get('search_key')
        self.sobject = SearchKey.get_by_search_key(search_key)
        
        from pyasm.web import WebContainer
        web = WebContainer.get_web()

        self.old_password = web.get_form_value("old password")
        if isinstance(self.old_password, list):
            self.old_password = self.old_password[0]
        #encrypted = md5.new(self.old_password).hexdigest()
        encrypted = hashlib.md5(self.old_password).hexdigest()
        
        if encrypted != self.sobject.get_value('password'):
            raise UserException('Old password is incorrect.')
        self.password = web.get_form_value("password")
        if isinstance(self.password, list):
            self.password = self.password[0]


        if self.sobject == None:
            return UserException("Current user cannot be determined.")

        self.re_enter = web.get_form_value("password re-enter")
        if isinstance(self.re_enter, list):
            self.re_enter = self.re_enter[0]
        if self.re_enter != "" and self.re_enter != self.password:
            raise UserException( "Passwords must match. Please fill in the re-enter.")

        return True

    def execute(self):
        assert self.sobject != None

        if self.password == "":
            if self.sobject.is_insert():
                raise UserException("Empty password.  Go back and re-enter")
            else:
                return
        
        # encrypt the password
        #encrypted = md5.new(self.password).hexdigest()
        encrypted = hashlib.md5.new(self.password).hexdigest()
        self.sobject.set_value("password", encrypted)

        self.sobject.commit()

        self.description = "Password changed for [%s]." %self.sobject.get_value('login')
