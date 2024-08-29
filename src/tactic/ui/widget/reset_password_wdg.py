###########################################################
#
# Copyright (c) 2009, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#
__all__ = ["CodeConfirmationWdg", "NewPasswordWdg", "NewPasswordCmd", "ResetOptionsWdg", "ResetOptionsCmd", "SendPasswordResetCmd"]

import random
import hashlib

from pyasm.web import DivWdg, HtmlElement, SpanWdg, Table, Widget, WebContainer
from pyasm.widget import HiddenWdg, TextWdg, IconWdg, PasswordWdg, BaseSignInWdg
from tactic.ui.common import BaseRefreshWdg, Environment
from tactic.ui.widget import ActionButtonWdg
from pyasm.command import Command
from pyasm.common import TacticException, Config, Common
from pyasm.security import Batch, Login


class NewPasswordWdg(BaseSignInWdg):


    def get_content_styles(self):

        styles = HtmlElement.style('''

        .password-inputs {
            display: flex;
            flex-direction: column;
        }

        .password-inputs .sign-in-btn {
            align-self: center;
        }

        ''')

        return styles


    def get_content(self):

        web = WebContainer.get_web()
        login_name = web.get_form_value('login')
        hidden = HiddenWdg('login', login_name)

        div = DivWdg()
        div.add_style("margin: 0px 0px")
        div.add(hidden)


        # hidden element in the form to pass message that this was not
        # actually a typical submitted form, but rather the result
        # of a login page
        div.add( HiddenWdg("is_from_login", "yes") )
        div.add_style("font-size: 10px")

        login_div = DivWdg()
        div.add(login_div)
        login_div.add_class("password-inputs")

        password_container = DivWdg()
        login_div.add(password_container)
        password_container.add_class("sign-in-input")
        password_container.add("<div class='label'>Password</div>")

        password_wdg = PasswordWdg("my_password")
        password_container.add(password_wdg)

        confirm_password_container = DivWdg()
        login_div.add(confirm_password_container)
        confirm_password_container.add_class("sign-in-input")
        confirm_password_container.add("<div class='label'>Confirm Password</div>")

        confirm_password_wdg = PasswordWdg("confirm_password")
        confirm_password_container.add(confirm_password_wdg)

        reset_button = DivWdg('Reset')
        login_div.add(reset_button)
        reset_button.add_class("sign-in-btn hand")
        reset_button.add_attr('title', 'Reset Password')
        reset_button.add_event("onclick", "document.form.elements['new_password'].value='true'; document.form.submit()")

        hidden = HiddenWdg("new_password")
        login_div.add(hidden)

        msg = web.get_form_value(CodeConfirmationWdg.MSG)
        if msg:
            err_msg_container = DivWdg()
            div.add(err_msg_container)
            err_msg_container.add_class("msg-container")

            err_msg_container.add("<i class='fa fa-exclamation-circle'></i><span>%s</span>" % msg)

        div.add(self.get_content_styles())

        return div


class NewPasswordCmd(Command):


    def check(self):
        web = WebContainer.get_web()
        self.login = web.get_form_value("login")
        if self.login =='admin':
            error_msg = "You are not allowed to reset admin password."
            web.set_form_value("is_err", "true")
            web.set_form_value(BaseSignInWdg.RESET_MSG_LABEL, error_msg)
            raise TacticException(error_msg)
            return False
        return True


    def execute(self):
        self.check()

        web = WebContainer.get_web()

        password = web.get_form_value("my_password")
        confirm_password = web.get_form_value("confirm_password")

        login = Login.get_by_login(self.login, use_upn=True)
        if not login:
            web.set_form_value("is_err", "true")
            web.set_form_value(BaseSignInWdg.RESET_MSG_LABEL, 'This user [%s] does not exist or has been disabled. Please contact the Administrator.'%self.login)
            return

        if password == confirm_password:
            code = web.get_form_value('code')

            if login:
                data = login.get_json_value('data')


                # if admin, just raise an exception.
                if login == 'admin':
                    # admin can't reset passwd.
                    raise SecurityException("Admin can't reset passwd.")

                # need to get the authenticate class
                auth_class = Config.get_value("security", "authenticate_class", no_exception=True)
                if not auth_class:
                    auth_class = "pyasm.security.TacticAuthenticate"
                #print("auth_class:", auth_class)

                if data:
                    temporary_code = data.get('temporary_code')
                    if code == temporary_code:
                        # for password complexity and previous passwords check
                        password_complexity = Config.get_value("security", "password_complexity", no_exception=True)
                        if password_complexity in ['true', 'True']:
                            if not login.check_previous_passwords(password):
                                web.set_form_value("is_err", "true")
                                web.set_form_value(BaseSignInWdg.RESET_MSG_LABEL, 'You cannot reuse previous passwords.')
                                return
                            if not Login.validate_password(password):
                                web.set_form_value("is_err", "true")
                                web.set_form_value(BaseSignInWdg.RESET_MSG_LABEL, 'Your password does not meet standards. It must have at least one number, one UPPERCASE and one lowercase character. It must also have at least one special character and be a minimum of 8 characters long.')
                                return

                        # call reset_password from the auth_class
                        authenticate = Common.create_from_class_path(auth_class)
                        authenticate.reset_password(login, password)
        else:
            web.set_form_value("is_err", "true")
            web.set_form_value(BaseSignInWdg.RESET_MSG_LABEL, 'The entered passwords do not match.')
            return



class CodeConfirmationWdg(BaseSignInWdg):

    MSG = 'reset_msg'
    RESET_MSG = 'Reset completed.'

    def get_content_styles(self):

        styles = HtmlElement.style('''

            .reset-container {
                display: flex;
                flex-direction: column;
            }

            .sign-in-btn.email-reset-btn {
                align-self: flex-start;
            }

            .code-msg-container {
                margin: 20 0;
                color: #666;
                font-size: 12px;
                text-align: left;
            }

            .msg-user {
                text-decoration: underline;
            }

            .spt_code_div {
                display: flex;
                flex-direction: column;
            }

            ''')

        return styles


    def get_content(self):

        web = WebContainer.get_web()
        login_name = web.get_form_value('login')
        hidden = HiddenWdg('login', login_name)

        div = DivWdg()
        div.add_style("margin: 0px 0px")

        div.add(hidden)

        # hidden element in the form to pass message that this was not
        # actually a typical submitted form, but rather the result
        # of a login page
        div.add( HiddenWdg("is_from_login", "yes") )
        div.add_style("font-size: 10px")
        div.add_class("reset-container")

        div.add("<div class='code-msg-container'>A code was sent to <span class='msg-user'>%s</span>'s email. Please enter the code to reset your password:</div>" % login_name)

        code_container = DivWdg()
        div.add(code_container)
        code_container.add_class("sign-in-input")
        code_container.add("<div class='label'>Code</div>")

        code_wdg = TextWdg("code")
        code_container.add(code_wdg)

        bottom_container = DivWdg()
        div.add(bottom_container)
        bottom_container.add_class("bottom-container")

        resend_container = DivWdg()
        bottom_container.add(resend_container)

        next_button = DivWdg('Next')
        bottom_container.add(next_button)
        next_button.add_class('sign-in-btn hand')
        next_button.add_attr('title', 'Next')
        next_button.add_event("onclick", "document.form.elements['reset_password'].value='true'; document.form.submit()")

        hidden = HiddenWdg('reset_password')
        div.add(hidden)

        msg = web.get_form_value(CodeConfirmationWdg.MSG)
        if msg:
            err_msg_container = DivWdg()
            div.add(err_msg_container)
            err_msg_container.add_class("msg-container")

            err_msg_container.add("<i class='fa fa-exclamation-circle'></i><span>%s</span>" % msg)


            resend_container.add_class("forgot-password-container")
            hidden = HiddenWdg('resend_code')
            resend_container.add(hidden)

            access_msg = "Resend email"
            js = '''document.form.elements['resend_code'].value='true'; document.form.submit()'''
            link = HtmlElement.js_href(js, data=access_msg)
            link.add_color('color','color', 60)
            resend_container.add(link)


        div.add(self.get_content_styles())

        return div



class ResetOptionsWdg(BaseSignInWdg):

    MSG = 'reset_msg'
    RESET_MSG = 'Reset completed.'

    def get_content_styles(self):

        styles = HtmlElement.style('''

            .reset-container {
                display: flex;
                flex-direction: column;
            }

            .sign-in-btn.email-reset-btn {
                align-self: flex-start;
            }

            ''')

        return styles


    def get_content(self):

        web = WebContainer.get_web()
        login_name = web.get_form_value('login')

        div = DivWdg()
        div.add_style("margin: 0px 0px")

        # hidden element in the form to pass message that this was not
        # actually a typical submitted form, but rather the result
        # of a login page
        div.add( HiddenWdg("is_from_login", "yes") )
        div.add_style("font-size: 10px")
        div.add_class("reset-container")

        reset_div = DivWdg()
        div.add(reset_div)
        reset_div.add_class("spt_reset_div")

        name_container = DivWdg()
        reset_div.add(name_container)
        name_container.add_class("sign-in-input")
        name_container.add("<div class='label'>Name</div>")

        name_wdg = TextWdg("login")
        name_container.add(name_wdg)
        if login_name:
            name_wdg.set_value(login_name)

        # build the button manually
        email_reset_btn = DivWdg('Reset via Email')
        reset_div.add(email_reset_btn)
        email_reset_btn.add_class('sign-in-btn hand')
        email_reset_btn.add_attr('title', 'Reset via Email')
        email_reset_btn.add_event('onclick',"document.form.elements['send_code'].value='true'; document.form.submit()")

        hidden = HiddenWdg('send_code')
        div.add(hidden)

        msg = web.get_form_value(CodeConfirmationWdg.MSG)
        if msg:
            err_msg_container = DivWdg()
            div.add(err_msg_container)
            err_msg_container.add_class("msg-container")

            err_msg_container.add("<i class='fa fa-exclamation-circle'></i><span>%s</span>" % msg)

        div.add(self.get_content_styles())

        return div



class ResetOptionsCmd(Command):

    def is_undoable(cls):
        return False
    is_undoable = classmethod(is_undoable)

    def execute(self):
        web = WebContainer.get_web()
        url = web.get_base_url()
        url.append_to_base(web.get_site_context_url().to_string())
        cmd = SendPasswordResetCmd(login=web.get_form_value("login"), project_url=url, reset=True)

        try:
            cmd.execute()
            web.set_form_value(BaseSignInWdg.RESET_MSG_LABEL, BaseSignInWdg.RESET_COMPLETE_MSG)
        except TacticException as e:
            web.set_form_value(BaseSignInWdg.RESET_MSG_LABEL, e)



class SendPasswordResetCmd(Command):

    def execute(self):

        self.login = self.kwargs.get("login")
        if self.login =='admin':
            error_msg = "You are not allowed to reset admin password."
            raise TacticException(error_msg)

        reset = (self.kwargs.get('reset') in ["true", True]) or False

        login = Login.get_by_login(self.login, use_upn=True)
        if not login:
            error_msg = 'This user [%s] does not exist or has been disabled. Please contact the Administrator.' % self.login
            raise TacticException(error_msg)

        upn = login.get_value("upn")
        if not upn:
            upn = self.login

        email = login.get_value('email')
        if not email:
            error_msg = 'This user [%s] does not have an email entry for us to email you the new password. Please contact the Administrator.' % self.login
            raise TacticException(error_msg)

        # auto pass generation
        unique_code = ''.join([ random.choice('abcdefghijklmnopqrstuvwxyz123456789') for i in range(0, 10)])
        auto_password = unique_code

        # send the email
        try:
            from pyasm.command import EmailTriggerTestCmd
            from pyasm.biz import ProjectSetting, Project
            from pyasm.common import Config
            from pyasm.security import Sudo

            sudo = Sudo()
            try: 
                # if the project is default or admin, we are not going to set it
                # from web context.
                if Project.get_project_code() in ['default', 'admin']:
                    current_project = WebContainer.get_web().get_context_name()
                    Project.set_project(current_project)
                application = ProjectSetting.get_value_by_key("application")
                sender_email = ProjectSetting.get_value_by_key("mail_user") 
            finally:
                sudo.exit()
                
            if not application:
                application = "TACTIC"

            if not sender_email:
                sender_email = Config.get_value("services", "mail_default_admin_email")
            if not sender_email:
                sender_email = Config.get_value("services", "mail_user")
            admin = Login.get_by_login('admin')
            if admin and not sender_email:
                sender_email = admin.get_value("email")
                
            recipient_emails = [email]

            url = self.kwargs.get("project_url")
            if not url:
                url = WebContainer.get_web().get_project_url()

            ongoing_url = url.to_string()
            url.set_option("reset_password", "true")
            url.set_option("login", self.login)
            url.set_option("code", auto_password)
            url = url.to_string()
            if reset:
                email_msg = 'Your %s password reset code is:\n\n%s\n\nYou may use the following URL to set a new password:\n\n%s' % (application, auto_password, url)
                subject = '%s password change' % (application)
            else:
                email_msg = "Welcome to %s. Your user name is [%s]. Visit the following URL to set a password. Password will expire after 90 days. \n\nPassword Requirements: \n- Can't be identical to User ID. \n- Must contain at least one number. \n- Must contain at least one uppercase and one lowercase character. \n- Must contain at least one special symbol. \n- Must be a minimum of 8 characters long. \n\n This password setup link is for one-time use only: \n%s \n\nFor ongoing access use the following URL: \n%s" % (application, upn, url, ongoing_url)
                subject = '%s invitation' % (application)
            email_cmd = EmailTriggerTestCmd(sender_email=sender_email, recipient_emails=recipient_emails, msg= email_msg, subject=subject)

            data = login.get_json_value("data", default={})
            data['temporary_code'] = auto_password
            login.set_json_value('data', data)
            login.commit()

            email_cmd.execute()

        except TacticException as e:
            if reset:
                error_msg = "Failed to send an email for your new password. Reset aborted."
            else:
                error_msg = "Failed to send an invitation email. Please check the email address."
            raise TacticException(error_msg)
