
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

__all__ = ['WebLoginCmd']

from pyasm.common import Config, SecurityException
from pyasm.command import Command


class WebLoginCmd(Command):

    def check(my):
        return True

    def is_undoable(cls):
        return False
    is_undoable = classmethod(is_undoable)
              
    def execute(my):

        from pyasm.web import WebContainer
        web = WebContainer.get_web()

        # If the tag <force_lowercase_login> is set to "true"
        # in the TACTIC config file,
        # then force the login string argument to be lowercase.
        # This tag is false by default.
        my.login = web.get_form_value("login")
        if Config.get_value("security","force_lowercase_login") == "true":
            my.login = my.login.lower()
        my.password = web.get_form_value("password")
        my.domain = web.get_form_value("domain")

        if my.login == "" and my.password == "":
            return False

        
        if my.login == "" or  my.password == "":
            web.set_form_value(WebLoginWdg.LOGIN_MSG, \
                "Empty username or password") 
            return False
        
        security = WebContainer.get_security()

        # handle windows domains
        #if my.domain:
        #    my.login = "%s\\%s" % (my.domain, my.login)

        verify_password = web.get_form_value("verify_password")
        if verify_password:
            if verify_password != my.password:
                web.set_form_value(WebLoginWdg.LOGIN_MSG, \
                    "Passwords do not match.") 
                return False

            my.password = Login.get_default_password()

        try:
            security.login_user(my.login, my.password, domain=my.domain)
        except SecurityException, e:
            msg = str(e)
            if not msg:
                msg = "Incorrect username or password"

            from pyasm.widget import WebLoginWdg
            web.set_form_value(WebLoginWdg.LOGIN_MSG, msg)

        if security.is_logged_in():

            # set the cookie in the browser
            web = WebContainer.get_web()
            ticket = security.get_ticket()
            if ticket:
                web.set_cookie("login_ticket", ticket.get_value("ticket"))


            login = security.get_login()
            if login.get_value("login") == "admin" and verify_password:
                login.set_password(verify_password)


