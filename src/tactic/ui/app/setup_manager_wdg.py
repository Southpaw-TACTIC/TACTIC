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

__all__ = ['SetupManagerWdg']

import os

from pyasm.common import Environment, Config
from pyasm.web import DivWdg, HtmlElement, WebContainer, Table, Widget
from pyasm.widget import IconWdg, HiddenWdg, PasswordWdg, SelectWdg, TextWdg, ProdIconSubmitWdg
from pyasm.command import Command, CommandException
from pyasm.search import FileUndo
from pyasm.security import CryptoKey

from tactic.ui.common import BaseRefreshWdg


# DEPRECATED

class SetupManagerWdg(BaseRefreshWdg):

    def get_args_keys(self):
        return {
            "error": "Any error that may exists"
        }

    def init(self):
        pass
 

    def get_display(self):
        try:
            cmd = DatabaseManagerCbk()
            cmd.execute()
        except CommandException as e:
            error = str(e)
        else:
            error = None

        div = DivWdg()
        div.add_class("spt_database_manager_top")

        """
        security = Environment.get_security()
        if not security.is_logged_in():
            # if there is no database connection, then a user must login as
            # admin 
            div.add( self.get_login_wdg() )
            return div

        #security = Environment.get_security().get_login()
        #print(security)
        error_for_user = DatabaseErrorWdg()
        div.add(error_for_user)
        return div
        """



        from tactic.ui.container import PopupWdg
        popup = PopupWdg(id="DatabaseManagerWdg", width="500px", allow_page_activity="false", display='true', zstart=10000, allow_close='false')
        popup.add("Database Manager", "title")

        content = DivWdg()
        content.add_style("background: #333")
        content.add_style("padding: 10px")
        content.add_style("border: solid 1px black")
        content.add_style("font-size: 1.2em")
        
        icon = IconWdg("Setup Manager", IconWdg.CREATE)
        content.add(icon)
        content.add("<b>TACTIC Database Manager</b>")
        content.add("<hr/>")
        content.add("<br/>")
        
        if not error:
            error = self.kwargs.get("error")
        if error:
            error_div = DivWdg()
            error_div.add_style("border: solid 1px #000")
            error_div.add_style("padding: 20px")
            icon = IconWdg("Setup Manager", IconWdg.ERROR)
            error_div.add(icon)
            error_div.add("ERROR: ")
            error_div.add(error)

            content.add(error_div)
            content.add("<br/>")
            content.add("<br/>")


        content.add( "<b>Please contact your Adminstrator.</b>" )

        """
        vendor = Config.get_value("database", "vendor")
        server = Config.get_value("database", "server")
        user = Config.get_value("database", "user")

        from pyasm.search import DbPasswordUtil
        password = DbPasswordUtil.get_password()

        table = Table(css="table")
        table.add_style("width: 100%")

        table.add_row()
        table.add_cell("Vendor: ")
        select = SelectWdg("database_vendor")
        select.set_option("values", "PostgreSQL|Oracle")
        select.set_value(server)
        table.add_cell(select)

        table.add_row()
        table.add_cell("Server: ")
        text = TextWdg("database_server")
        text.set_value(server)
        table.add_cell(text)

        table.add_row()
        table.add_cell("User: :")
        text = TextWdg("database_user")
        text.set_value(user)
        table.add_cell(text)

        table.add_row()
        table.add_cell("Password: :")
        td = table.add_cell()
        password = PasswordWdg("database_password")
        td.add(password)

        table.add_row()
        table.add_cell("Confirm Password :")
        td = table.add_cell()
        password = PasswordWdg("password2")
        td.add(password)


        content.add(table)
        content.add("<hr/>")

        from pyasm.widget import ProdIconSubmitWdg, ProdIconButtonWdg
        test = ProdIconButtonWdg("Test")
        test.add_event("onclick", "var top=$(this).getParent('.spt_database_manager_top');var values=spt.api.Utility.get_input_values();var server=TacticServerStub.get();var user=values.database_user[0];var result=server.test_database_connection('localhost', {user:user})")
        #test.add_behavior( {
        #    'type': 'click_up',
        #    'cbjs_action': "alert('cow')"
        #} )

        submit = ProdIconSubmitWdg("Save")
        submit.add_event("onclick", "document.form.submit()")

        cancel = ProdIconSubmitWdg("Cancel")
        cancel.add_event("onclick", "document.form.cancel()")

        button_div = DivWdg()
        button_div.add_style("text-align: center")
        button_div.add(test)
        button_div.add(submit)
        button_div.add(cancel)
        content.add(button_div)
        """



        popup.add(content, "content")
        div.add(popup)
        #div.add(content)

        return div



    def get_login_wdg(self):
        from pyasm.widget import WebLoginWdg, BottomWdg
        widget = WebLoginWdg()
        return widget






class DatabaseManagerCbk(object):

    def execute(self):
        web = WebContainer.get_web()

        xml_string = Config.get_xml_data().to_string()

        keys = web.get_form_keys()
        for key in keys:
            value = web.get_form_value(key)

            is_config_key = key.find("/") != -1

            if key == "database/password":
                self.handle_password()

            elif is_config_key:
                module_name, key = key.split("/")
                Config.set_value(module_name, key, value )


        xml_string2 = Config.get_xml_data().to_string()

        if xml_string2 != xml_string:
            Config.save_config()

    def handle_password(self):

        web = WebContainer.get_web()
        first = web.get_form_value("database/password")
        second = web.get_form_value("password2")

        if not first or not second:
            return

        if first != second:
            raise CommandException("Passwords do not match")

        if first.find(" ") != -1:
            raise CommandException("Password cannot contain spaces or special characters")

        from pyasm.search import DbPasswordUtil
        DbPasswordUtil.set_password(first)





class DatabaseErrorWdg(Widget):

    LOGIN_MSG = 'login_message'
    def get_display(self):

        
        div = DivWdg()
        div.add_style("margin: 0px 0px")
        div.add_class("centered")

        div.add(HtmlElement.br(7))

        table = Table(css="login")
        table.center()
        table.set_attr("cellpadding", "3px")
        table.add_row()

        div.add(table)

        error_div = DivWdg()
        error_div.add_class("maq_search_bar")
        error_div.add_style("font-size: 1.5em")
        error_div.add_style("padding: 5px")
        error_div.add_style("margin: 0 5px 0 5px")
        error_div.add_style("text-align: center")
        icon = IconWdg("Database Error", IconWdg.ERROR)
        error_div.add(icon)
        error_div.add("Databsae Error")
        table.add_cell( error_div)

        error = self.get_error()
        table.add_row()
        td = table.add_cell( "<b>%s</b>" % error )
        td.add_style("padding: 5px 20px 5px 20px")
        table.add_row()
        td = table.add_cell( "<b>Please contact your Admistrator. In the meantime, you can login with 'admin'</b>" )
        td.add_style("padding: 5px 20px 5px 20px")
        table.add_row()
        table.add_row()
        OK = ProdIconSubmitWdg('Return to Login')

        return div



    def get_error(self):
        return "ERROR: Lost connection to the database"

