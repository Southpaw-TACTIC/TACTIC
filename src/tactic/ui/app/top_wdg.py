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

__all__ = [ 'TopWdg', 'TitleTopWdg' ]

import types
import os

import js_includes

from pyasm.common import Container, Environment
from pyasm.biz import Project
from pyasm.web import WebContainer, Widget, HtmlElement, DivWdg, BaseAppServer
from pyasm.widget import IconWdg

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.container import PopupWdg
from tactic.ui.app import TacticCopyrightNoticeWdg



class TopWdg(Widget):
    
    def init(my):
        my.body = HtmlElement("body")


        # FIXME: DISABLING until we can find out why this disables
        # all checkboxes!
        my.body.add_behavior( {
        'type': 'load',
        'cbjs_action': '''
        spt.body = {};
        spt.body.focus_elements = [];

        spt.body.add_focus_element = function(el) {
            spt.body.focus_elements.push(el);
        }

        '''
        } )

        """
        my.body.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        // find all of the registered popups and close them
        for (var i = 0; i < spt.body.focus_elements.length; i++) {
            var el = spt.body.focus_elements[i];
            spt.hide(el);
        }
        spt.body.focus_elements = [];
        evt.stopPropagation();
        '''
        } )
        """

        web = WebContainer.get_web()
        my.body.add_color("color", "color")

        if web.is_title_page():
            my.body.add_gradient("background", "background", 0, -20)
        else:
            my.body.add_gradient("background", "background", 0, -15)

        my.body.add_style("background-attachment: fixed !important")
        #my.body.add_style("min-height: 1200px")
        my.body.add_style("height: 100%")
        my.body.add_style("margin: 0px")


        # ensure that any elements that force the default menu over any TACTIC right-click context menus has the
        # 'force_default_context_menu' flag reset for the next right click that occurs ...
        #
        my.body.add_event( "oncontextmenu", "spt.force_default_context_menu = false;" )




    def get_body(my):
        return my.body


    def get_display(my):

        web = WebContainer.get_web()

        widget = Widget()
        html = HtmlElement("html")

        is_xhtml = False
        if is_xhtml:
            web.set_content_type("application/xhtml+xml")
            widget.add('''<?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE html 
    PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
            ''')
            html.add_attr("xmlns", "http://www.w3.org/1999/xhtml")
            #html.add_attr("xmlns:svg", "http://www.w3.org/2000/svg")


        # add the copyright
        widget.add( my.get_copyright_wdg() )
        widget.add(html)


        # create the header
        head = HtmlElement("head")
        html.add(head)

        head.add('<meta http-equiv="Content-Type" content="text/html;charset=UTF-8"/>\n')
        head.add('<meta http-equiv="X-UA-Compatible" content="IE=edge"/>\n')

        # Add the tactic favicon
        head.add('<link rel="shortcut icon" href="/context/favicon.ico" type="image/x-icon"/>')

        # add the css styling
        head.add(my.get_css_wdg())

        # add the title in the header
        project = Project.get()
        project_code = project.get_code()
        project_title = project.get_value("title")

        if project_code == 'admin':
            head.add("<title>TACTIC</title>\n" )
        else:
            head.add("<title>%s</title>\n" % project_title )

        # add the body
        body = my.body
        html.add( body )


        # Add a NOSCRIPT tag block here to provide a warning message on browsers where 'Enable JavaScript'
        # is not checked ... TODO: clean up and re-style to make look nicer
        body.add( """
        <NOSCRIPT>
        <div style="border: 2px solid black; background-color: #FFFF99; color: black; width: 600px; height: 70px; padding: 20px;">
        <img src="%s" style="border: none;" /> <b>Javascript is not enabled on your browser!</b>
        <p>This TACTIC powered, web-based application requires JavaScript to be enabled in order to function. In your browser's options/preferences, please make sure that the 'Enable JavaScript' option is checked on, click OK to accept the settings change, and then refresh this web page.</p>
        </div>
        </NOSCRIPT>
        """ % ( IconWdg.get_icon_path("ERROR") ) )

        
        # add the javascript libraries
        head.add( JavascriptImportWdg() )

        # add the content
        if my.widgets:
            content_wdg = my.get_widget('content')
        else:
            content_wdg = Widget()
            my.add(content_wdg)
        body.add( content_wdg )

        body.add_event('onload', 'spt.onload_startup(this)')


        from tactic_branding_wdg import TacticCopyrightNoticeWdg
        branding = TacticCopyrightNoticeWdg(show_license_info=True)
        body.add(branding)

        # Add the script editor listener
        load_div = DivWdg()
        body.add(load_div)
        load_div.add_behavior( {
        'type': 'listen',
        'event_name': 'show_script_editor',
        'cbjs_action': '''
        var js_popup_id = "TACTIC Script Editor";
        var js_popup = $(js_popup_id);
        if( js_popup ) {
            spt.popup.toggle_display( js_popup_id, false );
        }
        else {
            spt.panel.load_popup(js_popup_id, "tactic.ui.app.ShelfEditWdg", {}, {"load_once": true} );
        }
        '''} )




        env = Environment.get()
        client_handoff_dir = env.get_client_handoff_dir(include_ticket=False, no_exception=True)
        client_asset_dir = env.get_client_repo_dir()

        login = Environment.get_login()
        user_name = login.get_value("login")
        user_id = login.get_id()
        login_groups = Environment.get_group_names()
       
        # add environment information
        script = HtmlElement.script('''
        var env = spt.Environment.get();
        env.set_project('%s');
        env.set_user('%s');
        env.set_user_id('%s');
        var login_groups = '%s'.split('|');
        env.set_login_groups(login_groups);
        env.set_client_handoff_dir('%s');
        env.set_client_repo_dir('%s');

        ''' % (Project.get_project_code(), user_name, user_id, '|'.join(login_groups), client_handoff_dir,client_asset_dir ))
        body.add(script)


        # add global containers
        # FIXME: need to add some registration process for this
        div = DivWdg()
        div.set_id("global_container")

        # @@@
        from page_header_wdg import AppBusyWdg
        div.add( AppBusyWdg() )


        body.add(div)

        # popup parent
        popup = DivWdg()
        popup.set_id("popup")
        div.add(popup)

        # create another general popup
        popup_div = DivWdg()
        popup_div.set_id("popup_container")
        popup_div.add_class("spt_panel")
        popup = PopupWdg(id="popup_template",destroy_on_close=True)
        popup_div.add(popup)
        div.add(popup_div)


        # popup parent
        inner_html_div = DivWdg()
        inner_html_div.set_id("inner_html")
        div.add(inner_html_div)



        # error parent
        # DEPRECATED
        #error_popup = PopupWdg(id="error_popup", width="80%")
        #error = DivWdg()
        #error.set_id("error_container")
        #error_popup.add("Error", "title")
        #error_popup.add(error, "content")
        #div.add(error_popup)


        # add in the swf upload button
        #upload_div = DivWdg()
        #upload_div.set_id("global_upload")
        #upload_div.add_style("display: block")
        #from tactic.ui.widget import GlobalUploadWdg
        #upload = GlobalUploadWdg(key="global_upload")
        #upload_div.add(upload)
        #div.add(upload_div)


        # add in a global color
        from tactic.ui.input import ColorWdg
        color = ColorWdg()
        div.add(color)


        from notify_wdg import NotifyWdg
        widget.add(NotifyWdg())


        return widget




    def get_copyright_wdg(my):
        widget = Widget()

        # add the copyright information
        widget.add( "<!--   -->\n")
        widget.add( "<!-- Copyright (c) 2005-2009, Southpaw Technology - All Rights Reserved -->\n")
        widget.add( "<!--   -->\n")

        return widget


    def get_css_wdg(my):

        widget = Widget()

        web = WebContainer.get_web()
        context_url = web.get_context_url().to_string()

        skin = web.get_skin()

        #Container.append_seq("Page:css", "%s/style/layout2.css" % context_url)
        #return widget

        # first load context css
        Container.append_seq("Page:css", "%s/style/layout.css" % context_url)


        # DEPRECATED: still needed for Maya Loader!
        # --- SKIN CSS ...
        #
        #Container.append_seq("Page:css", "%s/skins/%s/style/main.css" % (context_url, skin))

        # test styles for use in UI prototyping pages ..
        Container.append_seq("Page:css", "%s/ui_proto/ui_proto_test.css" % context_url)


        # DEPRECATED: use palette
        # This is still used for the drop shadow for popups
        # --- NEW THEME CSS ...
        #
        Container.append_seq("Page:css", "%s/themes/_common_/common.css" % context_url)
        Container.append_seq("Page:css", "%s/themes/_common_/font_standard.css" % context_url)
        Container.append_seq("Page:css", "%(c_url)s/themes/%(skin)s/%(skin)s_main.css" % {'c_url': context_url, 'skin': skin})



        # add the color wheel css
        Container.append_seq("Page:css", "%s/spt_js/mooRainbow/Assets/mooRainbow.css" % context_url)
        Container.append_seq("Page:css", "%s/spt_js/mooDialog/css/MooDialog.css" % context_url)

        # TESTING
        #Container.append_seq("Page:css", "%s/spt_js/CodeMirror-2.2/lib/codemirror.css" % context_url)
        #Container.append_seq("Page:css", "%s/spt_js/CodeMirror-2.2/theme/eclipse.css" % context_url)

        # Another test
        #Container.append_seq("Page:css", "%s/spt_js/vi/vi.css" % context_url)


        # get all of the registered css file
        css_files = Container.get_seq("Page:css")
        for css_file in css_files:
            widget.add('<link rel="stylesheet" href="%s" type="text/css" />\n' % css_file )

        
        return widget


class JavascriptImportWdg(BaseRefreshWdg):

    def get_display(my):

        web = WebContainer.get_web()
        context_url = web.get_context_url().to_string()
        js_url = "%s/javascript" % context_url
        spt_js_url = "%s/spt_js" % context_url    # adding new core "spt" javascript library folder

        version = Environment.get_release_version()

        # add some third party libraries
        third_party = js_includes.third_party
        security = Environment.get_security()

        # FIXME: this logic should not be located here.
        # no reason to have the edit_area_full.js
        if not security.check_access("builtin", "view_script_editor", "allow") and security.check_access("builtin", "view_site_admin", "allow"):
            if "edit_area/edit_area_full.js" in third_party:
                third_party.remove("edit_area/edit_area_full.js")


        for include in js_includes.third_party:
            Container.append_seq("Page:js", "%s/%s" % (spt_js_url,include))

        all_js_path = js_includes.get_compact_js_filepath()

        if os.path.exists( all_js_path ):
            Container.append_seq("Page:js", "%s/%s" % (context_url, js_includes.get_compact_js_context_path_suffix()))
        else:
            for include in js_includes.legacy_core:
                Container.append_seq("Page:js", "%s/%s" % (js_url,include))

            for include in js_includes.spt_js:
                Container.append_seq("Page:js", "%s/%s" % (spt_js_url,include))

            for include in js_includes.legacy_app:
                Container.append_seq("Page:js", "%s/%s" % (js_url,include))


        #Container.append_seq("Page:js", "http://webplayer.unity3d.com/download_webplayer-3.x/3.0/uo/UnityObject.js")
        #Container.append_seq("Page:js", "/context/spt_js/UnityObject.js")


        widget = DivWdg()
        widget.set_id("javascript")
        my.set_as_panel(widget)

        js_files = Container.get("Page:js")
        for js_file in js_files:
            widget.add('<script src="%s?ver=%s" ></script>\n' % (js_file,version) )


        return widget



class TitleTopWdg(TopWdg):
    
    def init(my):
        my.body = HtmlElement("body")

        web = WebContainer.get_web()
        my.body.add_color("color", "color")

        if web.is_title_page():
            my.body.add_gradient("background", "background", 0, -20)
        else:
            my.body.add_gradient("background", "background", 0, -15)

        my.body.add_style("background-attachment: fixed !important")
        #my.body.add_style("min-height: 1200px")
        my.body.add_style("height: 100%")
        my.body.add_style("margin: 0px")


    def get_display(my):

        web = WebContainer.get_web()

        widget = Widget()
        html = HtmlElement("html")
        html.add_attr("xmlns:v", 'urn:schemas-microsoft-com:vml')

        is_xhtml = False
        if is_xhtml:
            web.set_content_type("application/xhtml+xml")
            widget.add('''<?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE html 
    PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
            ''')
            html.add_attr("xmlns", "http://www.w3.org/1999/xhtml")
            #html.add_attr("xmlns:svg", "http://www.w3.org/2000/svg")


        # add the copyright
        widget.add( my.get_copyright_wdg() )
        widget.add(html)


        # create the header
        head = HtmlElement("head")
        html.add(head)

        head.add('<meta http-equiv="Content-Type" content="text/html;charset=UTF-8"/>\n')
        head.add('<meta http-equiv="X-UA-Compatible" content="IE=edge"/>\n')

        # Add the tactic favicon
        head.add('<link rel="shortcut icon" href="/context/favicon.ico" type="image/x-icon"/>')

        # add the css styling
        head.add(my.get_css_wdg())

        # add the title in the header
        project = Project.get()
        project_code = project.get_code()
        project_title = project.get_value("title")

        if project_code == 'admin':
            head.add("<title>TACTIC</title>\n" )
        else:
            head.add("<title>%s</title>\n" % project_title )

        # add the body
        body = my.body
        html.add( body )


        # Add a NOSCRIPT tag block here to provide a warning message on browsers where 'Enable JavaScript'
        # is not checked ... TODO: clean up and re-style to make look nicer
        body.add( """
        <NOSCRIPT>
        <div style="border: 2px solid black; background-color: #FFFF99; color: black; width: 600px; height: 70px; padding: 20px;">
        <img src="%s" style="border: none;" /> <b>Javascript is not enabled on your browser!</b>
        <p>This TACTIC powered, web-based application requires JavaScript to be enabled in order to function. In your browser's options/preferences, please make sure that the 'Enable JavaScript' option is checked on, click OK to accept the settings change, and then refresh this web page.</p>
        </div>
        </NOSCRIPT>
        """ % ( IconWdg.get_icon_path("ERROR") ) )

        
        # add the javascript libraries
        #head.add( JavascriptImportWdg() )

        body.add("<form id='form' name='form' method='post' enctype='multipart/form-data'>\n")

        for content in my.widgets:
            body.add(content)

        body.add("</form>\n")

        from tactic_branding_wdg import TacticCopyrightNoticeWdg
        copyright = TacticCopyrightNoticeWdg()
        body.add(copyright)

        return widget





__all__.extend( ['IndexWdg', 'SitePage', 'SiteXMLRPC'] )
from pyasm.search import SearchType
from pyasm.web import WebContainer, AppServer
from pyasm.prod.service import BaseXMLRPC


class IndexWdg(Widget):

    def __init__(my, hash=""):
        my.hash = hash
        super(IndexWdg, my).__init__()

    def init(my):
        top = DivWdg()
        top.set_id('top_of_application')

        msg_div = DivWdg()
        msg_div.add_style('text-align: center')
        msg_div.add('<img src="/context/icons/common/indicator_snake.gif" border="0"/>')
        msg_div.add("&nbsp; &nbsp;")
        msg_div.add("Loading TACTIC ....")
        msg_div.add_style("font-size: 1.5em")

        msg_div.add_behavior( {
            'type': 'load',
            'hash': my.hash,
            'cbjs_action': '''
            if (bvr.hash) {
                spt.hash = "/" + bvr.hash;
            }
            else {
                spt.hash = "/index";
            }
            '''
        } )

        msg_div.add_style("margin: 200 0 500 0")
        top.add(msg_div)

        my.add(top)
        return


class SitePage(AppServer):
    def __init__(my):
        super(SitePage,my).__init__()

    def set_templates(my):
        context = WebContainer.get_web().get_full_context_name()
        SearchType.set_global_template("project", context)

    def get_page_widget(my):
        try:
            hash = my.hash
        except:
            hash = None
        if hash:
            hash = "/".join(hash)
        else:
            hash = None
        index = IndexWdg(hash=hash)
        return index


class SiteXMLRPC(BaseXMLRPC):
    def set_templates(my):
        context = WebContainer.get_web().get_full_context_name()
        SearchType.set_global_template("project", context)







