
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

    def check(my):
        return True

    def is_undoable(cls):
        return False
    is_undoable = classmethod(is_undoable)

    def reenable_user(my, login_sobject, delay):
        from tactic.command import SchedulerTask, Scheduler
        class EnableUserTask(SchedulerTask):
            def execute(my):
                Batch()
                reset_attempts = 0
                login_sobject = my.kwargs.get('sobject')
                login_sobject.set_value("license_type", "user")
                login_sobject.set_value("login_attempt", reset_attempts)
                login_sobject.commit(triggers=False)

        scheduler = Scheduler.get()
        task = EnableUserTask(sobject=login_sobject, delay=delay)
        scheduler.add_single_task(task, delay)
        scheduler.start_thread()

              
    def execute(my):

        from pyasm.web import WebContainer
        web = WebContainer.get_web()

        from pyasm.widget import WebLoginWdg
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

        login_sobject = None
        if SearchType.column_exists("sthpw/login", "upn"):
            search = Search("sthpw/login")
            search.add_filter('upn',my.login)
            login_sobject = search.get_sobject()
        if not login_sobject:
            search2 = Search("sthpw/login")              
            search2.add_filter('login',my.login)
            login_sobject = search2.get_sobject()

        # FIXME: need to only be able to do this if admin password is empty
        if verify_password:
            if login_sobject and login_sobject.get_value("login") == "admin":
                login_sobject.set_password(verify_password)

        try:
            security.login_user(my.login, my.password, domain=my.domain)
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
            if max_attempts >0:
                login_attempt = login_sobject.get_value('login_attempt')

                login_attempt = login_attempt+1
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

                    my.reenable_user(login_sobject, delay)

                
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



