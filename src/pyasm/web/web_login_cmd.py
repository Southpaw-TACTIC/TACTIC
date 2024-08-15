
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

from pyasm.common import Config, SecurityException, Common
from pyasm.command import Command
from pyasm.security import Security, Sudo, Site
from pyasm.web import WebContainer
from pyasm.search import Search, SearchType

from datetime import datetime, timedelta

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


    def get_message(self):
        from pyasm.widget import WebLoginWdg
        from pyasm.web import WebContainer
        web = WebContainer.get_web()
        return web.get_form_value(WebLoginWdg.LOGIN_MSG)


    def execute(self):

        from pyasm.widget import WebLoginWdg
        from pyasm.web import WebContainer
        web = WebContainer.get_web()

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

        self.two_factor_code = web.get_form_value("two_factor_code")


        if self.login == "" and self.password == "":
            web.set_form_value(WebLoginWdg.LOGIN_MSG, \
                "Username and password are empty")
            return False
        if self.login == "":
            web.set_form_value(WebLoginWdg.LOGIN_MSG, \
                "Username is empty")
            return False
        if self.password == "":
            #web.set_form_value(WebLoginWdg.LOGIN_MSG, \
            #    "Password is empty")
            return False

        security = WebContainer.get_security()

        # handle windows domains
        #if self.domain:
        #    self.login = "%s\\%s" % (self.domain, self.logia)


        verify_password = web.get_form_value("verify_password")

        if verify_password:
            if verify_password != self.password:
                web.set_form_value(WebLoginWdg.LOGIN_MSG, \
                    "Passwords do not match.")
                return False

        # check to see if the login exists in the database
        login_sobject = None
        sudo = Sudo()
        Site.set_site("default")
        try:
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
        finally:
            sudo.exit()
            Site.pop_site()




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


            requires_2fa = Security.requires_2fa()
            if requires_2fa == True and not self.two_factor_code:
                if not login_sobject:
                    raise SecurityException("User does not exist")

                # commented out on 2022-07-21. We are passing the exception to the UI.
                # first check that the password is correct
                # try:
                #     security.login_user(login, self.password, domain=self.domain, test=True)
                # except:
                #     # suppress the real error
                #     raise SecurityException("Need two factor code")
                # first check that the password is correct
                security.login_user(login, self.password, domain=self.domain, test=True)


                # email recipients
                recipient = []

                # email user code
                generated_code = Common.randint(0, 999999)
                generated_code = "%0.6d" % generated_code

                # store code in user
                Site.set_site("default")
                sudo = Sudo()
                try:
                    sthpw_login_sobject = Search.get_by_code("sthpw/login", login)
                    #print("email:", sthpw_login_sobject.get("email"))
                    email_address = sthpw_login_sobject.get("email")
                    if email_address:
                        recipient.append(email_address)

                    data = sthpw_login_sobject.get_json_value("data") or {}
                    data["two_factor_code"] = generated_code
                    expiry = datetime.now() + timedelta(minutes=2)
                    data["two_factor_expiry"] = expiry
                    sthpw_login_sobject.set_value("data", data)
                    sthpw_login_sobject.commit()
                finally:
                    Site.pop_site()
                    sudo.exit()

                subject = "Two Factor Authentication"
                message = '''
                This is your 2FA login verification code: %s
                ''' % (generated_code)
                #print(message)
                self.send_email(recipient, subject, message)

                raise SecurityException("Need two factor code")





            security.login_user(login, self.password, domain=self.domain, two_factor_code=self.two_factor_code)






        except SecurityException as e:
            print("FAILED")
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



    def send_email(self, emails, subject, message):

        from pyasm.command import EmailHandler, SendEmail
        from pyasm.common import TacticException

        print('subject: ', subject)
        print('message: ')
        print(message)

        try:
            from pyasm.security import Login
            from pyasm.biz import ProjectSetting

            sender_email = None
            sender_name = None

            sender_email = ProjectSetting.get_value_by_key("mail_user")
            sender_name = ProjectSetting.get_value_by_key("mail_name")

            # getting sender from tactic config
            if not sender_email:
                sender_email = Config.get_value("services", "mail_user")
                sender_name = Config.get_value("services", "mail_name")


            admin = Login.get_by_login('admin')
            if admin and not sender_email:
                sender_email = admin.get_value('email')
                sender_name = admin.get_value("display_name")

            if not sender_email:
                sender_email = 'support@southpawtech.com'
                sender_name = "Client Portal"

            recipient_emails = emails

            email_cmd = SendEmail(sender_email=sender_email, recipient_emails=recipient_emails, msg=message, subject=subject, sender_name=sender_name)
            email_cmd.execute()

        except TacticException as e:
            msg = 'Failed to send an email.'
            print("ERROR:", e)
            print(msg)
            raise

