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

    def __init__(my, **kwargs):
        my.login_name = ''
        super(SignOutCmd, my).__init__(**kwargs)

    def is_undoable(cls):
        return False
    is_undoable = classmethod(is_undoable)

    def get_title(my):
        return "Sign Out Command"


    def set_login_name(my, login_name):
        my.login_name = login_name

    def check(my):
        return True

    def execute(my):

        if not my.login_name:
            my.login_name = my.kwargs.get('login');

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



    def check_security(my):
        '''give the command a callback that allows it to check security'''
        return True


class PasswordEditCmd(Command):
    '''encrypts the entered password with md5 encryption'''

    def get_title(my):
        return "Password Change"

    def init(my):
        my.old_password = ''
        my.password = ''
        my.re_enter = ''

    def check(my):
        search_key = my.kwargs.get('search_key')
        my.sobject = SearchKey.get_by_search_key(search_key)
        
        from pyasm.web import WebContainer
        web = WebContainer.get_web()

        my.old_password = web.get_form_value("old password")
        if isinstance(my.old_password, list):
            my.old_password = my.old_password[0]
        #encrypted = md5.new(my.old_password).hexdigest()
        encrypted = hashlib.md5(my.old_password).hexdigest()
        
        if encrypted != my.sobject.get_value('password'):
            raise UserException('Old password is incorrect.')
        my.password = web.get_form_value("password")
        if isinstance(my.password, list):
            my.password = my.password[0]


        if my.sobject == None:
            return UserException("Current user cannot be determined.")

        my.re_enter = web.get_form_value("password re-enter")
        if isinstance(my.re_enter, list):
            my.re_enter = my.re_enter[0]
        if my.re_enter != "" and my.re_enter != my.password:
            raise UserException( "Passwords must match. Please fill in the re-enter.")

        return True

    def execute(my):
        assert my.sobject != None

        if my.password == "":
            if my.sobject.is_insert():
                raise UserException("Empty password.  Go back and re-enter")
            else:
                return
        
        # encrypt the password
        #encrypted = md5.new(my.password).hexdigest()
        encrypted = hashlib.md5.new(my.password).hexdigest()
        my.sobject.set_value("password", encrypted)

        my.sobject.commit()

        my.description = "Password changed for [%s]." %my.sobject.get_value('login')
