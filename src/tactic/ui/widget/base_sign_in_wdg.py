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
__all__ = ["BaseSignInWdg", "NewPasswordWdg2", "ResetPasswordWdg2"]

import random
import hashlib

from pyasm.web import DivWdg, HtmlElement, SpanWdg, Table, Widget, WebContainer
from pyasm.widget import HiddenWdg, TextWdg, IconWdg, PasswordWdg
from tactic.ui.common import BaseRefreshWdg
from tactic.ui.widget import ActionButtonWdg
from pyasm.command import Command
from pyasm.common import TacticException
from pyasm.security import Batch, Login



class BaseSignInWdg(Widget):


    def __init__(self, **kwargs):
        self.kwargs = kwargs
        # hidden is for inline login when a session expires
        self.hidden = kwargs.get('hidden') in  [True, 'True']
        super(BaseSignInWdg,self).__init__("div")


    def get_styles(self):

        styles = HtmlElement.style('''

        .tactic-container {
            position: relative;

            display: flex;
            flex-direction: column;
            align-items: center;

            margin: 0px;
            padding: 25px;

            border: 1px solid #ccc;
            border-radius: 3px;
            box-shadow: 0px 2px 4px rgba(0,0,0,0.1);
            background: white;

            font-size: 10px;
        }

        .content-container {
            margin-top: 40px;
            width: 100%;
        }

        .sign-in-text {
            position: absolute;
            top: 100px;
            font-size: 18px;
            margin: 10px 0;
            background: white;
            z-index: 2;
            padding: 0 10px;
            color: #666;
        }

        .sign-in-line {
            position: absolute;
            width: 100%;
            height: 1px;
            background: #ccc;
            top: 120px;
        }

        .sign-in-input {
            position: relative;
            width: 100%;
        }

        .board-man-gets-PAID {
            styl: paid;
            board: man;
            board: man;
            board: mans;
            gets: paid;
            styl: board;
            man: kawhi;
        }

        .sign-in-input .label {
            position: absolute; 
            top: -6;
            left: 8;
            
            padding: 0 5px;
            
            background: white;
            font-weight: normal;
            color: #aaa;
            font-size: 12px;
        }

        .sign-in-input input {
            color: black;
            width: 100%;
            padding: 16px;
            border: 1px solid #ccc;
            border-radius: 3px;
            margin-bottom: 20px;
            font-size: 16px;
        }

        .sign-in-btn {
            align-self: flex-end;
            background: #ccc;
            color: white;
            padding: 10px 16px;
            font-size: 14px;
            border-radius: 3px;
            box-shadow: 0px 2px 4px 0px #bbb;
        }

        .sign-in-btn:hover {
            background: #aaa;
        }

        .bottom-container {
            display: flex;
            justify-content: space-between;
            width: 100%;
        }

        .msg-container {
            display: flex;
            align-items: center;
            align-self: start;
            color: red;
        }

        .msg-container i {
            margin-right: 5px;
        }

        .floating-back-btn {
            position: absolute;
            top: 105;
            left: 10;

            display: flex;
            align-items: center;
            padding: 5px;
            box-shadow: 0px 2px 4px 0px #ccc;
            border-radius: 15px;
            background: #ccc;
            overflow: hidden;
            width: 20px;
            height: 20px;

            font-size: 14px;
            color: white;
            cursor: hand;
            
            transition: width 0.25s;
        }

        .floating-back-btn:hover {
            width: 120px;
        }

        .floating-back-btn .fa {
            margin-left: 3px;
        }

        .floating-back-btn span {
            width: 100px;
            position: absolute;
            left: 20;
        }

        .spt_tactic_background {
            margin: auto auto;
            width: 400px;
            text-align: center;
        }

        .spt_login_screen {
            width: 100%;
            height: 85%;
        }

        ''')

        return styles
        

    def get_display(self):
        override_logo = self.kwargs.get('override_logo') == "true"
        override_company_name = self.kwargs.get('override_company_name') == "true"
            
        box = DivWdg()
        box.add_class("spt_tactic_background")

        box.add_event("onkeyup", "tactic_login(event)")
        script = HtmlElement.script('''function tactic_login(e) {
                if (!e) var e = window.event;
                if (e.keyCode == 13) {
                    document.form.submit();
                }}
                ''')
        
        div = DivWdg()
        box.add(div)
        div.add_class("tactic-container")
        div.add_class("centered")


        if override_logo:
            div.add("<div class='spt_tactic_logo'></div>")
        else:
            div.add("<img src='/context/icons/logo/TACTIC_logo_white.png'/>")


        #div.add_style("padding-top: 95px")
        sthpw = SpanWdg("SOUTHPAW TECHNOLOGY INC", css="login_sthpw")
        sthpw.add_styles("margin-top: 4; color: #ccc;")
        if override_company_name:
            sthpw.add_class("spt_login_company")
            #sthpw.add_style("color: #CCCCCC")
        
        div.add( sthpw )
        div.add( HtmlElement.br() )

        div.add("<div class='sign-in-line'></div>")

        title = self.kwargs.get("title")
        if title:
            div.add("<div class='sign-in-text'>%s</div>" % title)

        div.add( HtmlElement.br() )

        back_btn = DivWdg("<i class='fa fa-chevron-left'></i>")
        div.add(back_btn)
        back_btn.add_class("floating-back-btn")
        back_btn.add("<span>Back to login</span>")

        hidden = HiddenWdg('back_to_login')
        back_btn.add(hidden)
        back_btn.add_event('onclick',"document.form.elements['back_to_login'].value='true'; document.form.submit()")

        ####### CONTENT #######
        content_container = DivWdg()
        div.add(content_container)
        content_container.add_class("content-container")

        content_container.add(self.get_content())


        widget = Widget()
        #widget.add( HtmlElement.br(3) )
        table = Table()
        table.add_class('spt_login_screen')
        if self.hidden:
            table.add_style('display','none')
            table.add_style('top','0px')
            table.add_style('position','absolute')


        table.add_row()
        td = table.add_cell()
        td.add_style("vertical-align: middle")
        td.add_style("text-align: center")
        td.add_style("background: transparent")
        td.add(box)
        widget.add(table)

        styles = self.get_styles()
        widget.add(styles)
        
        return widget


    def get_content(self):

        return ""



class ResetPasswordWdg2(BaseSignInWdg):

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

            .reset-container .msg-container {
                margin: 20 0;
                color: #666;
                font-size: 12px;
                text-align: left;
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


        # build the button manually
        email_reset_btn = DivWdg('Reset via Email')
        div.add(email_reset_btn)
        email_reset_btn.add_class('sign-in-btn email-reset-btn hand')
        email_reset_btn.add_attr('title', 'Reset via Email')
        email_reset_btn.add_event('onclick',"document.form.elements['send_code'].value='true'; document.form.submit()")

        hidden = HiddenWdg('send_code')
        div.add(hidden)
    
        #div.add(HiddenWdg(self.LOGIN_MSG))
        code_div = DivWdg()
        div.add(code_div)
        code_div.add_class("spt_code_div")

        code_div.add("<div class='msg-container'>A code was sent to %s email. Please enter the code to reset your password:</div>" % login_name)
        
        code_container = DivWdg()
        code_div.add(code_container)
        code_container.add_class("sign-in-input")
        code_container.add("<div class='label'>Code</div>")

        code_wdg = TextWdg("code")
        code_container.add(code_wdg)

        next_button = DivWdg('Next')
        code_div.add(next_button)
        next_button.add_class('sign-in-btn hand')
        next_button.add_attr('title', 'Next')
        next_button.add_event("onclick", "document.form.elements['reset_password'].value='true'; document.form.submit()")

        hidden = HiddenWdg('reset_password')
        code_div.add(hidden)

        div.add(self.get_content_styles())
        
        return div



class NewPasswordWdg2(BaseSignInWdg):


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

        div.add(self.get_content_styles())

        return div





