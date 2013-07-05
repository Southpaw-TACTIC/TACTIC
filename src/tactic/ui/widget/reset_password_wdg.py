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
__all__ = ["ResetPasswordWdg", "ResetPasswordCmd"]

import random
import hashlib

from pyasm.web import DivWdg, HtmlElement, SpanWdg, Table, Widget, WebContainer
from pyasm.widget import HiddenWdg, TextWdg, IconWdg
from tactic.ui.common import BaseRefreshWdg
from pyasm.command import Command
from pyasm.common import TacticException
from pyasm.security import Batch, Login


class ResetPasswordWdg(BaseRefreshWdg):


    MSG = 'reset_msg'
    RESET_MSG = 'Reset completed.'

    def get_display(my):

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

        td = table2.add_header('After reset, the new password will be sent to your registered email address.')
        td.add_color('color','color', + 80)
        table2.add_row_cell('&nbsp;')
        # build the button manually
        from tactic.ui.widget import ActionButtonWdg
        button = ActionButtonWdg(tip='Reset Password', title='Reset')
        button.add_style('margin: auto')
        button.add_event('onclick',"document.form.elements['reset_password'].value='true'; document.form.submit()")
        table2.add_row()
        td = table2.add_cell(button)
        hidden = HiddenWdg('reset_password')
        td.add(hidden)
       
        #th.add_class('center_content')
        
        table2.add_row()
    

        div.add(HtmlElement.br())
        div.add(table)

        div.add( HtmlElement.spacer_div(1,14) )
        div.add(table2)
        #div.add(HiddenWdg(my.LOGIN_MSG))

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

    def check(my):
        web = WebContainer.get_web()
        my.login = web.get_form_value("login")
        if my.login =='admin':
            error_msg = "You cannot reset admin password."
            web.set_form_value(ResetPasswordWdg.MSG, error_msg)
            raise TacticException(error_msg)
            return False
        return True

    def is_undoable(cls):
        return False
    is_undoable = classmethod(is_undoable)
              
    def execute(my):
        # Since this is not called with Command.execute_cmd
        my.check()

        web = WebContainer.get_web()

        reset_on = my.kwargs.get('reset') == True
        if reset_on:
            security = WebContainer.get_security()
            #Batch()
            login = Login.get_by_login(my.login)
            if not login:
                web.set_form_value(ResetPasswordWdg.MSG, 'This user [%s] does not exist or has been disabled. Please contact the Administrator.'%my.login)
                return
            email = login.get_value('email')
            if not email:
                web.set_form_value(ResetPasswordWdg.MSG, 'This user [%s] does not have an email entry for us to email you the new password. Please contact the Administrator.'%my.login)
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
                    sender_email = admin.get_value('email')
                else:
                    sender_email = 'support@southpawtech.com'

                recipient_emails = [email]
                email_msg =  'Your TACTIC password has been reset. The new password is:\n%s\nYou can change your password once you log in by going to Edit My Account at the top right corner.'%auto_password
                email_cmd = EmailTriggerTestCmd(sender_email=sender_email, recipient_emails=recipient_emails, msg= email_msg, subject='TACTIC password change')
            
                email_cmd.execute()
            except TacticException, e:
                
                msg = "Failed to send an email for your new password. Reset aborted."
                web.set_form_value(ResetPasswordWdg.MSG, msg)
                raise 
            else:
                encrypted = hashlib.md5(auto_password).hexdigest()
                login.set_value('password', encrypted)
                login.commit()
                web.set_form_value(ResetPasswordWdg.MSG, 'A new password has been sent to your email address. Please check your email.')


                
            # handle windows domains
            #if my.domain:
            #    my.login = "%s\\%s" % (my.domain, my.login)

            web.set_form_value(ResetPasswordWdg.MSG, msg)

     
