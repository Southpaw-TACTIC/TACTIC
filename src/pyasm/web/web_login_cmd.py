
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
from pyasm.web import WebContainer
from pyasm.search import Search, SearchType

class WebLoginCmd(Command):

    def check(self):
        return True

    def is_undoable(cls):
        return False
    is_undoable = classmethod(is_undoable)

    def reenable_user(self, login_sobject, delay):
        from tactic.command import SchedulerTask, Scheduler
        class EnableUserTask(SchedulerTask):
            def execute(self):
                Batch()
                reset_attempts = 0
                login_sobject = self.kwargs.get('sobject')
                login_sobject.set_value("license_type", "user")
                login_sobject.set_value("login_attempt", reset_attempts)
                login_sobject.commit(triggers=False)

        scheduler = Scheduler.get()
        task = EnableUserTask(sobject=login_sobject, delay=delay)
        scheduler.add_single_task(task, delay)
        scheduler.start_thread()


    def is_logged_in(self):
        security = WebContainer.get_security()
        return security.is_logged_in()

              
    def execute(self):

        from pyasm.web import WebContainer
        web = WebContainer.get_web()

        from pyasm.widget import WebLoginWdg
        # If the tag <force_lowercase_login> is set to "true"
        # in the TACTIC config file,
        # then force the login string argument to be lowercase.
        # This tag is false by default.
        self.login = web.get_form_value("login")
        if Config.get_value("security","force_lowercase_login") == "true":
            self.login = self.login.lower()

        password = web.get_form_value("password")
        self.password = password

        self.domain = web.get_form_value("domain")




        
        
        if self.login == "" and self.password == "":
            web.set_form_value(WebLoginWdg.LOGIN_MSG, \
                "Username and password are empty") 
            return False
        if self.login == "":
            web.set_form_value(WebLoginWdg.LOGIN_MSG, \
                "Username is empty") 
            return False
        if self.password == "":
            web.set_form_value(WebLoginWdg.LOGIN_MSG, \
                "Password is empty") 
            return False
        
        security = WebContainer.get_security()

        # handle windows domains
        #if self.domain:
        #    self.login = "%s\\%s" % (self.domain, self.login)


        verify_password = web.get_form_value("verify_password")

        if verify_password:
            if verify_password != self.password:
                web.set_form_value(WebLoginWdg.LOGIN_MSG, \
                    "Passwords do not match.") 
                return False

        # check to see if the login exists in the database
        login_sobject = None
        if SearchType.column_exists("sthpw/login", "upn"):
            search = Search("sthpw/login")
            search.add_filter('upn',self.login)
            login_sobject = search.get_sobject()
        if not login_sobject:
            search2 = Search("sthpw/login")              
            search2.add_filter('login',self.login)
            login_sobject = search2.get_sobject()
        if not login_sobject:
            search2 = Search("sthpw/login")              
            search2.add_filter('email',self.login)
            login_sobject = search2.get_sobject()


        # FIXME: need to only be able to do this if admin password is empty
        if verify_password:
            if login_sobject and login_sobject.get_value("login") == "admin":
                login_sobject.set_password(verify_password)

        try:
            # always use the login column regardless of what the user entered
            if login_sobject:
                login = login_sobject.get_value("login")
            else:
                login = self.login

            security.login_user(login, self.password, domain=self.domain)
        except SecurityException, e:
            msg = str(e)
            if not msg:
                msg = "Incorrect username or password"
            web.set_form_value(WebLoginWdg.LOGIN_MSG, msg)


            max_attempts=-1
            try:
                max_attempts = int(Config.get_value("security", "max_login_attempt"))
            except:
                pass

            if max_attempts > 0:
                login_attempt = 0
                if login_sobject:
                    login_attempt = login_sobject.get_value('login_attempt')

                    login_attempt = login_attempt + 1
                    login_sobject.set_value('login_attempt', login_attempt)

                if login_attempt == max_attempts:
                    #set license_Type to disabled and set off the thread to re-enable it
                    login_sobject.set_value('license_type', 'disabled')
                    disabled_time = Config.get_value("security", "account_lockout_duration")
                    if not disabled_time:
                        disabled_time = "30 minutes"


                    delay,unit = disabled_time.split(" ",1)
                    if "minute" in unit:
                        delay = int(delay)*60
                    
                    elif "hour" in unit:
                        delay =int(delay)*3600
                    
                    elif "second" in unit:
                        delay = int(delay)
                    else:
                        #make delay default to 30 min
                        delay = 30*60

                    self.reenable_user(login_sobject, delay)

                if login_sobject: 
                    login_sobject.commit(triggers=False)
            
        if security.is_logged_in():

            # set the cookie in the browser
            web = WebContainer.get_web()
            ticket = security.get_ticket()
            if ticket:
                web.set_cookie("login_ticket", ticket.get_value("ticket"))


            login = security.get_login()
            if login.get_value("login") == "admin" and verify_password:
                login.set_password(verify_password)



