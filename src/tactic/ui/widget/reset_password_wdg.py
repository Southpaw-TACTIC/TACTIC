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
__all__ = ["ResetPasswordWdg", "NewResetPasswordWdg", "ResetPasswordCmd", "NewPasswordCmd"]

import random
import hashlib

from pyasm.web import DivWdg, HtmlElement, SpanWdg, Table, Widget, WebContainer
from pyasm.widget import HiddenWdg, TextWdg, IconWdg
from tactic.ui.common import BaseRefreshWdg
from tactic.ui.widget import ActionButtonWdg
from pyasm.command import Command
from pyasm.common import TacticException
from pyasm.security import Batch, Login


class NewResetPasswordWdg(BaseRefreshWdg):


    def get_styles(self):

        styles = HtmlElement.style('''

        .password-inputs {
            display: flex;
            flex-direction: column;
            align-items: center;
            margin-top: 10px;   
        }

        input[type="password"] {
           margin-bottom: 10px;
        }	

        ''')

        return styles


    def get_display(self):
        
        web = WebContainer.get_web()
        login_name = web.get_form_value('login')
        hidden = HiddenWdg('login', login_name)
        box = DivWdg(css='login')

        if web.is_IE():
            box.add_style("margin-top: 150px")
            box.add_style("margin-bottom: 150px")
        else:
            box.add_style("margin-top: auto")
            box.add_style("margin-bottom: auto")
        box.add_style("text-align: center")

        div = DivWdg()
        div.add_style("margin: 0px 0px")
        div.add_class("centered")



        div.add_style("padding-top: 95px")

        sthpw = SpanWdg("SOUTHPAW TECHNOLOGY INC", css="login_sthpw")
        sthpw.add_style("color: #CCCCCC")
        div.add( sthpw )
        div.add( HtmlElement.br() )
        div.add(hidden)
        box.add(div)


        # hidden element in the form to pass message that this was not
        # actually a typical submitted form, but rather the result
        # of a login page
        div.add( HiddenWdg("is_from_login", "yes") )
        div.add_style("font-size: 10px")

        login_div = DivWdg()
        div.add(login_div)
        login_div.add_class("password-inputs")

        password_input = HtmlElement.text()
        login_div.add(password_input)
        password_input.add_attr("name", "my_password")
        password_input.add_attr("placeholder", "Password")
        password_input.add_attr("type", "password")

        confirm_password_input = HtmlElement.text()
        login_div.add(confirm_password_input)
        confirm_password_input.add_attr("name", "confirm_password")
        confirm_password_input.add_attr("placeholder", "Confirm Password")
        confirm_password_input.add_attr("type", "password")

        reset_button = ActionButtonWdg(tip='Reset Password', title='Reset')
        login_div.add(reset_button)
        reset_button.add_style("margin: 0 auto")
        reset_button.add_event("onclick", "document.form.elements['new_password'].value='true'; document.form.submit()")

        hidden = HiddenWdg("new_password")
        login_div.add(hidden)

        widget = Widget()
        #widget.add( HtmlElement.br(3) )
        table = Table()
        table.add_style("width: 100%")
        table.add_style("height: 85%")
        table.add_row()
        td = table.add_cell()
        td.add_style("vertical-align: middle")
        td.add_style("text-align: center")
        td.add_style("background: transparent")
        td.add(box)
        widget.add(table)

        widget.add(self.get_styles())

        return widget


class NewPasswordCmd(Command):


    def check(self):
        web = WebContainer.get_web()
        self.login = web.get_form_value("login")
        if self.login =='admin':
            error_msg = "You are not allowed to reset admin password."
            web.set_form_value(ResetPasswordWdg.MSG, error_msg)
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
            web.set_form_value(ResetPasswordWdg.MSG, 'This user [%s] does not exist or has been disabled. Please contact the Administrator.'%self.login)
            return  

        if password == confirm_password:
            encrypted = hashlib.md5(password).hexdigest()
            login.set_value('password', encrypted)
            login.commit()
        else:
            web.set_form_value(ResetPasswordWdg.MSG, 'The entered passwords do not match.')
            return



class ResetPasswordWdg(BaseRefreshWdg):


    MSG = 'reset_msg'
    RESET_MSG = 'Reset completed.'

    def get_display(self):
        
        web = WebContainer.get_web()
        login_name = web.get_form_value('login')
        hidden = HiddenWdg('login', login_name)
        box = DivWdg(css='login')

        if web.is_IE():
            box.add_style("margin-top: 150px")
            box.add_style("margin-bottom: 150px")
        else:
            box.add_style("margin-top: auto")
            box.add_style("margin-bottom: auto")
        box.add_style("text-align: center")
     
        div = DivWdg()
        div.add_style("margin: 0px 0px")
        div.add_class("centered")



        div.add_style("padding-top: 95px")


        sthpw = SpanWdg("SOUTHPAW TECHNOLOGY INC", css="login_sthpw")
        sthpw.add_style("color: #CCCCCC")
        div.add( sthpw )
        div.add( HtmlElement.br() )
        div.add(hidden)
        box.add(div)


        # hidden element in the form to pass message that this was not
        # actually a typical submitted form, but rather the result
        # of a login page
        div.add( HiddenWdg("is_from_login", "yes") )
        div.add_style("font-size: 10px")

        table = Table(css="login")
        table.center()
        table.set_attr("cellpadding", "3px")
        table.add_row()



        table2 = Table(css="login")
        table2.center()
        table2.add_style("width: 240px")

        table2.add_row()

        td = table2.add_header('A code will be sent to the email address for [ %s ].'%login_name)
        td.add_color('color','color', + 80)
        table2.add_row_cell('&nbsp;')
        # build the button manually
        button = ActionButtonWdg(tip='Send Code', title='Send Code')
        button.add_style('margin: auto')
        button.add_event('onclick',"document.form.elements['send_code'].value='true'; document.form.submit()")
        table2.add_row()
        td = table2.add_cell(button)
        hidden = HiddenWdg('send_code')
        td.add(hidden)

        #th.add_class('center_content')

        table2.add_row()


        div.add(HtmlElement.br())
        div.add(table)

        div.add( HtmlElement.spacer_div(1,14) )
        div.add(table2)
        #div.add(HiddenWdg(self.LOGIN_MSG))
        code_div = DivWdg()
        div.add(code_div)
        code_div.add_style("margin: 20 0")

        input_div = HtmlElement.text()
        code_div.add(input_div)
        input_div.add_attr('name', 'code')
        input_div.add_style('margin-bottom: 10px')

        next_button = ActionButtonWdg(tip='Next', title='Next')
        code_div.add(next_button)
        next_button.add_style("margin: 0 auto")
        next_button.add_event("onclick", "document.form.elements['reset_password'].value='true'; document.form.submit()")

        hidden = HiddenWdg('reset_password')
        code_div.add(hidden)

        #box.add(script)

        widget = Widget()
        #widget.add( HtmlElement.br(3) )
        table = Table()
        table.add_style("width: 100%")
        table.add_style("height: 85%")
        table.add_row()
        td = table.add_cell()
        td.add_style("vertical-align: middle")
        td.add_style("text-align: center")
        td.add_style("background: transparent")
        td.add(box)
        widget.add(table)
        
        return widget



class ResetPasswordCmd(Command):

    def check(self):
        web = WebContainer.get_web()
        self.login = web.get_form_value("login")
        if self.login =='admin':
            error_msg = "You are not allowed to reset admin password."
            web.set_form_value(ResetPasswordWdg.MSG, error_msg)
            raise TacticException(error_msg)
            return False
        return True

    def is_undoable(cls):
        return False
    is_undoable = classmethod(is_undoable)
              
    def execute(self):
        # Since this is not called with Command.execute_cmd
        self.check()

        web = WebContainer.get_web()

        reset_on = self.kwargs.get('reset') == True
        if reset_on:
            security = WebContainer.get_security()
            #Batch()
            login = Login.get_by_login(self.login, use_upn=True)
            if not login:
                web.set_form_value(ResetPasswordWdg.MSG, 'This user [%s] does not exist or has been disabled. Please contact the Administrator.'%self.login)
                return
            email = login.get_value('email')
            if not email:
                web.set_form_value(ResetPasswordWdg.MSG, 'This user [%s] does not have an email entry for us to email you the new password. Please contact the Administrator.'%self.login)
                return

        
            # auto pass generation
            unique_code = ''.join([ random.choice('abcdefghijklmno12345') for i in xrange(0, 5)])
            auto_password = unique_code
            
            msg = ResetPasswordWdg.RESET_MSG
            
            # send the email
            try:
                from pyasm.command import EmailTriggerTestCmd

                admin = Login.get_by_login('admin')
                if admin:
                    sender_email = admin.get_full_email()
                    if not sender_email:
                        from pyasm.common import Config
                        sender_email = Config.get_value("services", "mail_default_admin_email")
                    else:
                        sender_email = 'support@southpawtech.com'
                recipient_emails = [email]
                email_msg = 'Your TACTIC password reset code is:\n\n%s' % auto_password
                email_cmd = EmailTriggerTestCmd(sender_email=sender_email, recipient_emails=recipient_emails, msg= email_msg, subject='TACTIC password change')

                data = login.get_json_value("data")
                data['temporary_code'] = auto_password
                login.set_json_value('data', data)
                login.commit()

                email_cmd.execute()

            except TacticException as e:
                msg = "Failed to send an email for your new password. Reset aborted."
                web.set_form_value(ResetPasswordWdg.MSG, msg)
                raise 
                
            # handle windows domains
            #if self.domain:
            #    self.login = "%s\\%s" % (self.domain, self.login)

            web.set_form_value(ResetPasswordWdg.MSG, msg)

     
