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


    def get_args_keys(my):
        
        return {'allow_close': 'Allow user to close it when he is done in the Admin site'}

    def init(my):
        my.allow_close = 'false'
        if my.kwargs.get('allow_close') == 'true':
            my.allow_close = 'true'

 

    def get_display(my):

        use_popup = my.kwargs.get("use_popup")
        if use_popup in [True, 'true']:
            use_popup = True
        else:
            use_popup = False


        div = DivWdg()
        content = my.get_content()
        content.add_style("width: 600px")
        content.add_style("margin-left: auto")
        content.add_style("margin-right: auto")
        
        from tactic.ui.container import PopupWdg
        if use_popup:
            popup = PopupWdg(id="LicenseManagerWdg", width="500px", allow_page_activity="false", display='true', zstart=10000, allow_close=my.allow_close)
            popup.add("License Manager", "title")

            popup.add(content, "content")
            div.add(popup)


            behavior = {
                'type': 'load',
                'cbjs_action': '''
                var el = $(LicenseManagerWdg);
                el.setStyle("display","");
                //var parent = el.getParent(".spt_panel");
                //parent.setStyle("left: 0px");
                //parent.setStyle("margin-right: auto");
                '''
            }
            div.add_behavior(behavior)

        else:
            div.add(content)
            content.add_style("height: 500px")




        return div


    def get_content(my):

        content = DivWdg()
        content.add_style("font-size: 1.2em")
        content.add_color("background", "background")
        content.add_color("color", "color")
        content.add_style("padding: 20px")
        content.add_border()
       
        license = Environment.get_security().get_license()
        error_msg = license.get_message()

        if error_msg.startswith("Cannot find license file"):
            first_error = True
        else:
            first_error = False

        if first_error:
            message = my.get_welcome_wdg(error_msg)
            content.add(message)
            content.add_style("width: 700px")
            content.add_gradient("background", "background", 0, -10)


        elif error_msg:
            icon = IconWdg("License Error", IconWdg.ERROR)
            content.add(icon)
            content.add("<b>License Error</b>")
            content.add("<hr/>")
            content.add("<br/>")
            content.add("The TACTIC License Manager has encountered the following error:")
            content.add("<br/>")

            pre = DivWdg()
            pre.add_style("width: 300px")
            pre.add_style("border: solid black 1px")
            pre.add_style("margin: 20px")
            pre.add_style("margin-left: auto")
            pre.add_style("margin-right: auto")
            pre.add_style("padding: 20px")
            pre.add_style("background: grey")
            pre.add_style("color: black")
            pre.add(error_msg)
            content.add(pre)

            behavior = {
            'type': 'load',
            'cbjs_action': "setInterval(\"spt.alert('%s. Please notify the administrator.')\", 600000)" %error_msg}
            content.add_behavior(behavior)
 

        content.add( my.get_license_info_wdg() )


        security = Environment.get_security()
        if security.is_admin():
            if not first_error: 
                content.add("<hr/>")
                content.add("<br/>")
                content.add("Please verify the license or upload a new one:")
                content.add("<br/>"*2)
                upload = LicenseUploadWdg()
                content.add(upload)
        else:
            content.add("Please notify the site administrator to check the license or upload a new one.")
            content.add("<br/><hr/>")


        return content


    def get_license_info_wdg(my):
        div = DivWdg()

        license = Environment.get_security().get_license()
        if not license.is_licensed():
            return div

        title = DivWdg()
        div.add(title)
        title.add("License Manager")
        title.add_color("background", "background3")
        title.add_style("font-size: 14px")
        title.add_style("font-weight: bold")
        title.add_style("padding: 10px")
        title.add_border()
        title.add_style("margin: -21px -21px 20px -21px")

        div.add("<br/>")


        msg = DivWdg()
        div.add(msg)
        msg.add("The following describes the details of the installed license:<br/><br/>")


        div.add("TACTIC Version: ")
        version = license.get_data("tactic_version")
        if version == "ALL":
            version = "ALL (Open Source)"
        div.add(version)
        div.add(HtmlElement.br(2))


        company = license.get_data("company")
        div.add("Licensed To: ")
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
        div.add(company)
        div.add(HtmlElement.br(2))

        div.add("Max Users: ")
        div.add(license.get_data("max_users") )
        div.add(HtmlElement.br(2))

        div.add("Current Users: ")
        div.add(license.get_current_users() )
        div.add(HtmlElement.br(2))

        div.add("Expiry Date: ")
        expiry_date = license.get_data("expiry_date")
        if not expiry_date:
            expiry_date = "Permanent"
        div.add(expiry_date)
        div.add(HtmlElement.br(2))

        return div




    def get_welcome_wdg(my, error_msg):
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
    def get_args_keys(my):
        return {
        'key': 'the key to the this upload widget'
        }
        
    def get_display(my):
        key = "LicenseManager"

        div = DivWdg()
        div.set_id(key)
        div.add_class("spt_upload")


        # override the column
        # SWF upload is deprecated
        """
        column_input = HiddenWdg("file_name")
        div.add(column_input)

        # the button div that will get replaced by the swf
        wrapper_div = DivWdg()
        wrapper_div.add_style("padding: 5px")
        wrapper_div.add_style("float: left")
        button_div = DivWdg()
        wrapper_div.add(button_div)
        div.add(wrapper_div)

        button_id = "%sButton" % key
        button_div.set_id(button_id)
        button_div.add_class("spt_upload_button")
        button_div.add_style("display: block")

 
        # add a upload button so it does not require edit_pressed
        from tactic.ui.widget import TextBtnWdg
        install_div = DivWdg()
        install_div.add_style("padding: 8px")
        install_button = TextBtnWdg(label="Install License", size='medium')
        behavior = {
            'type': 'click_up',
            'key': key,
            'cbjs_action': "spt.Upload.upload_cbk(bvr)"
        }
        install_button.add_behavior(behavior)
        install_div.add(install_button)
        div.add(install_div)

        div.add("<br/>")

        # add a stats widget
        stats_div = DivWdg()
        stats_div.add_style("float: right")
        stats_div.add_class("spt_upload_stats")
        div.add(stats_div)


        from tactic.ui.widget import UploadProgressWdg
        upload_progress = UploadProgressWdg()
        div.add(upload_progress)


        # add the onload behavior for this widget to initialize the swf
        load_div = DivWdg()
        behavior = {
            'type': 'load',
            'cbfn_action': "spt.Upload.setup_cbk",
            'key': key,
            'settings': {
                'upload_complete_handler':  'spt.Upload.license_complete',
            }
        }
        load_div.add_behavior(behavior)
        div.add(load_div)
        """


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

    def get_title(my):
        return "Renew License"


    def check(my):
        return True

    def get_web(my):
        from pyasm.web import WebContainer
        web = WebContainer.get_web()
        return web

    def execute(my):
        web = my.get_web()
        keys = web.get_form_keys()
        file_name = my.kwargs.get("file_name")

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

        my.add_description('Renewed license file')
        security = Environment.get_security()
        security.reread_license()

