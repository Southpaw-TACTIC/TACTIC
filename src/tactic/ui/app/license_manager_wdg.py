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

__all__ = ['LicenseManagerWdg', 'RenewLicenseCbk']

import os

from pyasm.common import Environment, TacticException
from pyasm.web import DivWdg, HtmlElement, SpanWdg
from pyasm.widget import IconWdg, HiddenWdg
from pyasm.command import Command
from pyasm.search import FileUndo
from pyasm.security import License

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.input import UploadButtonWdg



class LicenseManagerWdg(BaseRefreshWdg):


    def get_args_keys(self):
        
        return {'allow_close': 'Allow user to close it when he is done in the Admin site'}

    def init(self):
        self.allow_close = 'false'
        if self.kwargs.get('allow_close') == 'true':
            self.allow_close = 'true'

 

    def get_display(self):

        use_popup = self.kwargs.get("use_popup")
        if use_popup in [True, 'true']:
            use_popup = True
        else:
            use_popup = False


        div = DivWdg()
        content = self.get_content()
        content.add_style("width: 600px")
        content.add_style("margin-left: auto")
        content.add_style("margin-right: auto")
        
        from tactic.ui.container import PopupWdg
        if use_popup:
            popup = PopupWdg(id="LicenseManagerWdg", width="500px", allow_page_activity="false", display='true', zstart=10000, allow_close=self.allow_close)
            popup.add("License Manager", "title")

            popup.add(content, "content")
            div.add(popup)


            behavior = {
                'type': 'load',
                'cbjs_action': '''
                var el = document.id("LicenseManagerWdg");
                el.setStyle("display","");
                '''
            }
            div.add_behavior(behavior)

        else:
            div.add(content)
            content.add_style("height: 500px")




        return div


    def get_content(self):

        content = DivWdg()
        content.add_style("font-size: 1.2em")
        content.add_color("background", "background")
        content.add_color("color", "color")
        content.add_style("padding: 20px")
       
        license = Environment.get_security().get_license()
        error_msg = license.get_message()

        if error_msg.startswith("Cannot find license file"):
            self.first_error = True
        else:
            self.first_error = False

        if self.first_error:
            message = self.get_welcome_wdg(error_msg)
            content.add(message)
            content.add_style("width: auto")
            content.add_gradient("background", "background", 0, -3)


        elif error_msg:
            icon = IconWdg("License Error", IconWdg.ERROR)
            content.add(icon)
            content.add("<b>License Error</b>")
            content.add("<hr/>")
            content.add("<br/>")
            content.add("The TACTIC License Manager has encountered the following error:")
            content.add("<br/>")

            pre = DivWdg()
            pre.add_style("text-align: center")
            pre.add_style("width: 300px")
            pre.add_style("border: solid black 1px")
            pre.add_style("margin: 20px auto")
            pre.add_style("padding: 20px")
            pre.add_style("color: black")
            pre.add(error_msg)
            content.add(pre)

            behavior = {
            'type': 'load',
            'cbjs_action': "setInterval(\"spt.alert('%s. Please notify the administrator.')\", 600000)" %error_msg}
            content.add_behavior(behavior)
 

        content.add( self.get_license_info_wdg() )


        security = Environment.get_security()
        if security.is_admin():
            if not self.first_error: 
                content.add("<hr/>")
                content.add("<br/>")
                content.add("Please verify the license or upload a new one:")
                content.add("<br/>"*2)

                upload_div = DivWdg()
                content.add(upload_div)
                upload_div.add_style("width: 100px")
                upload_div.add_style("margin: 0px auto")

                upload = LicenseUploadWdg()
                upload_div.add(upload)
                upload_div.add_style("text-align: center")
        else:
            content.add("Please notify the site administrator to check the license or upload a new one.")
            content.add("<br/><hr/>")


        return content


    def get_license_info_wdg(self):
        div = DivWdg()

        license = Environment.get_security().get_license()
        if self.first_error:
            return div
        #if not license.is_licensed():
        #    return div

        msg = DivWdg()
        div.add(msg)
        msg.add("The following describes the details of the installed license:<br/><br/>")


        info_wdg = DivWdg()
        div.add(info_wdg)
        info_wdg.add_style("margin: 10px 30px")
        info_wdg.add_style("font-size: 12px")

        version = license.get_data("tactic_version")
        if version:
            info_wdg.add("TACTIC Version: ")
            if version == "ALL":
                version = "ALL (Open Source)"
            info_wdg.add(version)
            info_wdg.add(HtmlElement.br(2))


        company = license.get_data("company")
        info_wdg.add("Licensed To: ")
        if company.find("Southpaw EPL") != -1:
            company = SpanWdg("<a name='license'>Eclipse Public License v1.0</a> &nbsp;")
            icon = IconWdg("EPL v1.0", IconWdg.ZOOM)
            company.add(icon)
            company.add_class("hand")
            company.add_behavior( {
                'type': 'click_up',
                'cbjs_action': '''
                    spt.help.load_alias("license")
                '''
            } )
        info_wdg.add(company)
        info_wdg.add(HtmlElement.br(2))

        info_wdg.add("Max Users: ")
        info_wdg.add(license.get_data("max_users") )
        info_wdg.add(HtmlElement.br(2))

        info_wdg.add("Current Users: ")
        info_wdg.add(license.get_current_users() )
        info_wdg.add(HtmlElement.br(2))

        info_wdg.add("Expiry Date: ")
        expiry_date = license.get_data("expiry_date")
        if not expiry_date:
            expiry_date = "Permanent"
        info_wdg.add(expiry_date)
        info_wdg.add(HtmlElement.br(2))

        return div




    def get_welcome_wdg(self, error_msg):
        div = DivWdg()
        div.add_style("text-align: center")
        div.add_style("padding: 20px")

        title = DivWdg()
        div.add(title)
        title.add("Welcome to TACTIC!")
        title.add_style("font-size: 24px")
        title.add_style("font-weight: bold")

        div.add("<br/>")

        started = DivWdg()
        div.add(started)
        started.add("Please browse for a valid license file.")
        started.add_style("font-size: 18px")

        div.add("<br/>")

        upload_div = DivWdg()
        upload_div.add_style("text-align: center")
        upload_div.add_style("width: 100px")
        upload_div.add_style("margin: 0px auto")
        div.add(upload_div)
        upload = LicenseUploadWdg()
        upload_div.add(upload)

        div.add("<br/>")
        msg = DivWdg()
        div.add(msg)
        msg.add_style("text-align: left")
        msg.add_style("font-size: 11px")
        msg.add("If you do not have a valid TACTIC license or have any issues with the installation, please contact us at support@southpawtech.com")


        return div




class LicenseUploadWdg(BaseRefreshWdg):
    def get_args_keys(self):
        return {
        'key': 'the key to the this upload widget'
        }
        
    def get_display(self):
        key = "LicenseManager"

        div = DivWdg()
        div.set_id(key)
        div.add_class("spt_upload")

        from tactic.ui.widget import ActionButtonWdg
        #browse = ActionButtonWdg(title="Browse", tip="Click to browse for license file and renew")

        on_complete = '''var server = TacticServerStub.get();
            var file = spt.html5upload.get_file();
            if (file) {
               var file_name = file.name;
               // clean up the file name the way it is done in the server
               file_name = spt.path.get_filesystem_name(file_name);    
               var server = TacticServerStub.get();

                spt.app_busy.show("Renewing license ...");
                var cmd = 'tactic.ui.app.RenewLicenseCbk';
                var kwargs = {
                    file_name: file_name
                };
                try {
                    server.execute_cmd(cmd, kwargs);
                    spt.app_busy.hide();
                    spt.refresh_page();
                }
                catch(e) {
                    spt.alert(spt.exception.handler(e));
                }
               spt.notify.show_message("License renewal ["+file_name+"] successful");
            }
            else  {
              alert('Error: file object cannot be found.')
            }
            spt.app_busy.hide();'''

        browse = UploadButtonWdg(title="Browse", tip="Click to browse for license file and renew", on_complete=on_complete)
        browse.add_style("margin-left: auto")
        browse.add_style("margin-right: auto")
        div.add(browse)
       
        info_div = DivWdg()
        div.add(info_div)
        info_div.add_class("spt_license_info")




        return div



class RenewLicenseCbk(Command):
    ''' Renew License Callback'''

    INPUT_NAME="Renew_License"
    BUTTON_NAME = "Renew License"

    def get_title(self):
        return "Renew License"


    def check(self):
        return True

    def get_web(self):
        from pyasm.web import WebContainer
        web = WebContainer.get_web()
        return web

    def execute(self):
        web = self.get_web()
        keys = web.get_form_keys()
        file_name = self.kwargs.get("file_name")

        # process and get the uploaded files
        dir = Environment.get_upload_dir()
        license_file = "%s/%s" % (dir, file_name)
        if not os.path.exists(license_file):
            raise TacticException("Error retrieving the license file in [%s]"%license_file)

        std_name = 'tactic-license.xml'

        head, file_name = os.path.split(license_file)
        # no restrictions for license file
        #if file_name != std_name:
        #    raise TacticException("License file name should be named tactic-license.xml. The file given is [%s]" %file_name)

        license_dir = Environment.get_license_dir()
        current_license = "%s/%s" %(license_dir, std_name)
        if os.path.exists(current_license):
            FileUndo.remove(current_license)
        FileUndo.move(license_file, current_license)

        self.add_description('Renewed license file')
        security = Environment.get_security()
        security.reread_license()

