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

from __future__ import print_function


__all__ = [ 'TopWdg', 'TitleTopWdg']

import types
import os

import six
basestring = six.string_types


from pyasm.common import Common, Container, Environment, jsondumps, jsonloads, Config
from pyasm.biz import Project, ProjectSetting
from pyasm.web import WebContainer, Widget, HtmlElement, DivWdg, BaseAppServer, Palette, SpanWdg
from pyasm.widget import IconWdg
from pyasm.search import Search
from pyasm.security import Site

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.container import PopupWdg
from tactic.ui.app import TacticCopyrightNoticeWdg, GoogleAnalyticsWdg
from tactic.ui.widget import IconButtonWdg

from .js_includes import JSIncludes


class TopWdg(Widget):

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        super(TopWdg, self).__init__()



    def init(self):
        self.body = HtmlElement("body")
        Container.put("TopWdg::body", self.body)

        self.top = DivWdg()
        self.body.add(self.top)
        self.top.add_class("spt_top")
        Container.put("TopWdg::top", self.top)


        self.body.add_attr("ondragover", "return false;")
        self.body.add_attr("ondragleave", "return false;")
        self.body.add_attr("ondrop", "return false;")

        self.body.add_behavior( {
            'type': 'load',
            'cbjs_action': '''

            var el = bvr.src_el;

            el.spt_window_active = true;

            if (document.addEventListener) {
                document.addEventListener("visibilitychange", function() {
                    el.spt_window_active = ! document.hidden;
                } );
            }
            else {
                window.onfocus = function() {
                    bvr.src_el.spt_window_active = true;
                }

                window.onblur = function() {
                    bvr.src_el.spt_window_active = false;
                }
            }

            '''
        } )

        self.add_top_behaviors()



        
        click_div = DivWdg()
        self.top.add(click_div)
        click_div.add_behavior( {
        'type': 'load',
        'cbjs_action': '''
        spt.body = {};

        spt.body.is_active = function() {
            return document.id(document.body).spt_window_active;
        }

        spt.body.focus_elements = [];
        spt.body.add_focus_element = function(el) {
            spt.body.focus_elements.push(el);
        }

        spt.body.remove_focus_element = function(el) {
            var index = spt.body.focus_elements.indexOf(el);
            if (index != -1) {
                spt.body.focus_elements.splice(index, 1);
            }
        }

        // find all of the registered popups and close them
        // NOTE: logic can handle more than 1 focus element should it happen ...
        spt.body.hide_focus_elements = function(evt) {
            var mouse = evt.client;
            var target = evt.target;

            var targets = [];
            var count = 0;
            while (target) {
                targets.push(target);
                if (spt.has_class(target, 'spt_activator')) {
                    act_el = target.dialog;
                    if (act_el) {
                        targets.push(act_el);
                        break;
                    }
                }


                // if target is an smenu, then return
                if (spt.has_class(target, 'SPT_SMENU')) {
                    return;
                }



                target = target.parentNode;
                if (count == 100) {
                    alert("Too many to close.");
                    break;
                }

            }


            var dialog = evt.target.getParent(".MooDialog");
            if (dialog) {
                targets.push(dialog);
            }

            var hitEls = [];
            // find out if any of the parents of target is the focus element
            for (var i = 0; i < spt.body.focus_elements.length; i++) {
                var el = spt.body.focus_elements[i];
                var hit = false;

                if (spt.has_class(el, 'spt_popup_top')) {
                    continue;
                }

                for (var j = 0; j < targets.length; j++) {
                    var target = targets[j];
                    if (target == el) {
                         hit = true;
                         break;
                         
                    }
                }
        
                if (hit) {
                    hitEls.push(el);
                    continue;
                }
                else {
                    if ( el.isVisible() && el.on_complete ) {
                        el.on_complete(el);
                    }
                    else {
                        spt.hide(el);
                    }
      
                }
            }

            spt.body.focus_elements = hitEls;

        }
        //bvr.src_el.addEvent("mousedown", spt.body.hide_focus_elements);
        document.id(document.body).addEvent("mousedown", spt.body.hide_focus_elements);

        '''
        } )

        web = WebContainer.get_web()

        # ensure that any elements that force the default menu over any TACTIC right-click context menus has the
        # 'force_default_context_menu' flag reset for the next right click that occurs ...
        #
        self.body.add_event( "oncontextmenu", "spt.force_default_context_menu = false;" )




    def add_top_behaviors(self):
        self.body.add_relay_behavior( {
            'type': 'click',
            'bvr_match_class': 'tactic_popup',
            'cbjs_action': '''
            var view = bvr.src_el.getAttribute("view");
            if (!view) {
                spt.alert("No view found");
            }

            var target = bvr.src_el.getAttribute("target");
            var title = bvr.src_el.getAttribute("title");

            var class_name = 'tactic.ui.panel.CustomLayoutWdg';
            var args = {
                view: view,  
            }
            var kwargs = {};

            var popup_args_keys = ["width", "height", "resize", "on_close", "allow_close", "top_class"];

            var kwargs = {};

            var popup_args_keys = ["width", "height", "resize", "on_close", "allow_close", "top_class"];

            var kwargs = {};

            var popup_args_keys = ["width", "height", "resize", "on_close", "allow_close", "top_class"];

            var attributes = bvr.src_el.attributes;
            for (var i = 0; i < attributes.length; i++) {
                var name = attributes[i].name;
                if (name == "class") {
                    continue;
                }
                
                var value = attributes[i].value;

                if (popup_args_keys.indexOf(name) > -1) kwargs[name] = value;
                else args[name] = value;
            }

            var popup = spt.panel.load_popup(title, class_name, args, kwargs);
            popup.activator = bvr.src_el;
            '''
        } )


        self.body.add_relay_behavior( {
            'type': 'click',
            'bvr_match_class': 'tactic_load',
            'cbjs_action': '''


            var target_class = bvr.src_el.getAttribute("target");
            if (! target_class ) {
                target_class = "spt_content";
            }

            if (target_class.indexOf(".") != "-1") {
                var parts = target_class.split(".");
                var top = bvr.src_el.getParent("."+parts[0]);
                var target = top.getElement("."+parts[1]);  
            }
            else {
                var target = document.id(document.body).getElement("."+target_class);
            }


            var class_name = bvr.src_el.getAttribute("class_name");
            var kwargs = {};
            if (!class_name) {
                var class_name = 'tactic.ui.panel.CustomLayoutWdg';
                var view = bvr.src_el.getAttribute("view");
                if (!view) {
                    spt.alert("No view found");
                    return;
                }
                kwargs["view"] = view;
            }


            var attributes = bvr.src_el.attributes;
            for (var i = 0; i < attributes.length; i++) {
                var name = attributes[i].name;
                if (name == "class") {
                    continue;
                }
                var value = attributes[i].value;
                kwargs[name] = value;
            }

            spt.panel.load(target, class_name, kwargs);

            var scroll = bvr.src_el.getAttribute("scroll");
            if (scroll == "top") {
                window.scrollTo(0,0);
            }

            '''
        } )



        self.body.add_relay_behavior( {
            'type': 'click',
            'bvr_match_class': 'tactic_link',
            'cbjs_action': '''
            var href = bvr.src_el.getAttribute("href");
            if (!href) {
                spt.alert("No href defined for this link");
                return;
            }
            var target = bvr.src_el.getAttribute("target");
            if (!target) {
                target = "_self";
            }
            window.open(href, target);
            '''
        } )





        self.body.add_relay_behavior( {
            'type': 'click',
            'bvr_match_class': 'tactic_refresh',
            'cbjs_action': '''
            var target_class = bvr.src_el.getAttribute("target");
            if (!target_class) {
                var target = bvr.src_el;
            }
            else if (target_class.indexOf(".") != "-1") {
                var parts = target_class.split(".");
                var top = bvr.src_el.getParent("."+parts[0]);
                var target = top.getElement("."+parts[1]);  
            }
            else {
                var target = document.id(document.body).getElement("."+target_class);
            }

            var kwargs = {};
            var attributes = bvr.src_el.attributes;
            for (var i = 0; i < attributes.length; i++) {
                var attr_name = attributes[i].name;
                if (attr_name == "class") {
                    continue;
                }
                var value = attributes[i].value;
                kwargs[attr_name] = value;
            }


            spt.panel.refresh_element(target, kwargs);
            '''
            } )



        self.body.add_relay_behavior( {
            'type': 'click',
            'bvr_match_class': 'tactic_new_tab',
            'cbjs_action': '''

            var view = bvr.src_el.getAttribute("view")
            var search_key = bvr.src_el.getAttribute("search_key")
            var expression = bvr.src_el.getAttribute("expression")

            var name = bvr.src_el.getAttribute("name");
            var title = bvr.src_el.getAttribute("title");

            if (!name) {
                name = title;
            }

            if (!title) {
                title = name;
            }

            if (!title && !name) {
                title = name = "Untitled";
            }


            if (expression) {
                var server = TacticServerStub.get();
                var sss = server.eval(expression, {search_keys: search_key, single: true})
                search_key = sss.__search_key__;
            }


            spt.tab.set_main_body_tab()

            if (view) {
                var cls = "tactic.ui.panel.CustomLayoutWdg";
                var kwargs = {
                    view: view
                }
            }
            else if (search_key) {
                var cls = "tactic.ui.tools.SObjectDetailWdg";
                var kwargs = {
                    search_key: search_key
                }
            }


            var attributes = bvr.src_el.attributes;
            for (var i = 0; i < attributes.length; i++) {
                var attr_name = attributes[i].name;
                if (attr_name == "class") {
                    continue;
                }
                var value = attributes[i].value;
                kwargs[attr_name] = value;
            }


            try {
                spt.tab.add_new(name, title, cls, kwargs);
            } catch(e) {
                spt.alert(e);
            }
            '''
            } )



        self.body.add_relay_behavior( {
            'type': 'click',
            'bvr_match_class': 'tactic_submit',
            'cbjs_action': '''
            var command = bvr.src_el.getAttribute("command");
            var kwargs = {
            }
            var server = TacticServerStub.get();
            try {
                server.execute_cmd(command, kwargs);
            } catch(e) {
                spt.alert(e);
            }
            '''
            } )


        self.body.add_relay_behavior( {
            'type': 'mouseenter',
            'bvr_match_class': 'tactic_hover',
            'cbjs_action': '''
            var bgcolor = bvr.src_el.getStyle("background");
            bvr.src_el.setAttribute("spt_bgcolor", bgcolor);
            bvr.src_el.setStyle("background", "#EEE");
            '''
            } )

        self.body.add_relay_behavior( {
            'type': 'mouseleave',
            'bvr_match_class': 'tactic_hover',
            'cbjs_action': '''
            var bgcolor = bvr.src_el.getAttribute("spt_bgcolor");
            if (!bgcolor) bgcolor = "";
            //var bgcolor = ""
            bvr.src_el.setStyle("background", bgcolor);
            '''
            } )


        self.body.add_relay_behavior( {
            'type': 'click',
            'bvr_match_class': 'tactic_not_implemented',
            'cbjs_action': '''
            spt.alert("Feature is not yet implemented");
            '''
            } )



        self.body.set_unique_id()
        self.body.add_smart_style( "tactic_load", "cursor", "pointer" )


        # check version of the database
        project = Project.get()
        version = project.get_value("last_version_update")
        release = Environment.get_release_version()
        #if version < release:
        # FIXME: can't do this ... TACTIC cannot be running when the database
        # is upgrading.
        if False:
            try:
                from pyasm.security import Site
                site = Site.get_site()
                install_dir = Environment.get_install_dir()
                cmd = '''python "%s/src/bin/upgrade_db.py" -f -s "%s" --quiet --yes &''' % (install_dir, site)
                print("cmd: ", cmd)
                os.system(cmd)
                pass
            except Exception as e:
                print("WARNING: ", e)








    def get_body(self):
        return self.body

    def get_top(self):
        return self.top




    def get_display(self):

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
        widget.add( self.get_copyright_wdg() )
        widget.add(html)

        # handle redirect
        request_url = web.get_request_url().get_info().path
        if request_url in ["/tactic/Index", "/Index", "/"]:
            # if we have the root path name, provide the ability for the site to
            # redirect
            from pyasm.security import Site
            site_obj = Site.get()
            redirect = site_obj.get_site_redirect()
            if redirect:
                widget.add('''<meta http-equiv="refresh" content="0; url=%s">''' % redirect)
                return widget






        # create the header
        head = HtmlElement("head")
        html.add(head)


        head.add('<meta http-equiv="Content-Type" content="text/html;charset=UTF-8"/>\n')
        head.add('<meta http-equiv="X-UA-Compatible" content="IE=edge"/>\n')
 
        # Add the tactic favicon
        head.add('<link rel="shortcut icon" href="/context/favicon.ico" type="image/x-icon"/>')


        # add the css styling
        head.add(self.get_css_wdg())

        # add the title in the header
        project = Project.get()
        project_code = project.get_code()
        project_title = project.get_value("title")

        if web.is_admin_page():
            is_admin = " - Admin"
        else:
            is_admin = ""

        if project_code == 'admin':
            head.add("<title>TACTIC Site Admin</title>\n" )
        else:
            head.add("<title>%s%s</title>\n" % (project_title, is_admin) )


        # add the javascript libraries
        head.add( JavascriptImportWdg() )

        # add google analytics
        head.add(GoogleAnalyticsWdg())


        # add the body
        body = self.body
        html.add( body )

 
        top = self.top

        # Add a NOSCRIPT tag block here to provide a warning message on browsers where 'Enable JavaScript'
        # is not checked ... TODO: clean up and re-style to make look nicer
        top.add( '''
        <NOSCRIPT>
        <div style="border: 2px solid black; background-color: #FFFF99; color: black; width: 600px; height: 70px; padding: 20px;">
        <img src="%s" style="border: none;" /> <b>Javascript is not enabled on your browser!</b>
        <p>This TACTIC powered, web-based application requires JavaScript to be enabled in order to function. In your browser's options/preferences, please make sure that the 'Enable JavaScript' option is checked on, click OK to accept the settings change, and then refresh this web page.</p>
        </div>
        </NOSCRIPT>
        ''' % ( IconWdg.get_icon_path("ERROR") ) )




        # add the content
        content_div = DivWdg()
        top.add(content_div)
        Container.put("TopWdg::content", content_div)




        # add a dummy button for global behaviors
        from tactic.ui.widget import ButtonNewWdg, IconButtonWdg
        ButtonNewWdg(title="DUMMY", icon=IconWdg.FILM)
        IconButtonWdg(title="DUMMY", icon=IconWdg.FILM)
        # NOTE: it does not need to be in the DOM.  Just needs to be
        # instantiated
        #content_div.add(button)

        from tactic.ui.widget import CalendarWdg
        cal_wdg = CalendarWdg(css_class='spt_calendar_template_top')
        cal_wdg.top.add_style('display: none')
        top.add(cal_wdg)
        cal_wdg.add_class("SPT_TEMPLATE")


        if self.widgets:
            content_wdg = self.get_widget('content')
        else:
            content_wdg = Widget()
            self.add(content_wdg)

        content_div.add( content_wdg )
        
        # add a calendar wdg

        if web.is_admin_page():
            from .tactic_branding_wdg import TacticCopyrightNoticeWdg
            branding = TacticCopyrightNoticeWdg(show_license_info=True)
            top.add(branding)


        # add the admin bar
        security = Environment.get_security()
        if not web.is_admin_page() and security.check_access("builtin", "view_site_admin", "allow"):

            admin_bar = DivWdg()
            top.add(admin_bar)

            admin_bar.add_class("spt_admin_bar")
            admin_bar.add_class("hand")
            #admin_bar.add_style("display: none")
            admin_bar.add(HtmlElement.style('''
            .spt_admin_bar { 
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 0px 0px 0px 15px;
                position: fixed;
                top: 0px;
                left: 0px;
                height: 20px;
                opacity: 0.1;
                width: 100%;
                background-color: rgb(0, 0, 0);
                color: rgb(255, 255, 255);
                z-index: 1000;
                box-shadow: rgba(0, 0, 0, 0.1) 0px 5px 5px;A

                overflow: hidden;
                font-size: 0.8em;
            }
            
            .spt_admin_bar:hover {
                opacity: 1.0;
            }

            .spt_admin_bar_left {
                display: flex;
                align-items: center;
            }
            .spt_admin_bar_right {
                display: flex;
                align-items: center;
            }

            '''))

            admin_bar_left = DivWdg(css="spt_admin_bar_left")
            admin_bar.add(admin_bar_left)
            admin_bar_right = DivWdg(css="spt_admin_bar_right")
            admin_bar.add(admin_bar_right)

            
            # home
            icon_div = DivWdg()
            admin_bar_left.add(icon_div)
            icon_button = IconButtonWdg(icon="FA_HOME", title="Go to index", size=14)
            icon_div.add(icon_button)
            icon_button.add_behavior( {
                'type': 'click_up',
                'cbjs_action': '''
                window.location.href="/";
                '''
            } )

            # remove
            icon_div = DivWdg()
            admin_bar_right.add(icon_div)
            icon_button = IconButtonWdg(title="Remove Admin Bar", icon="FA_TIMES", size=14)
            icon_div.add(icon_button)
            icon_button.add_behavior( {
                'type': 'click_up',
                'cbjs_action': '''
                var parent = bvr.src_el.getParent(".spt_admin_bar");
                spt.behavior.destroy_element(parent);
                '''
            } )

            # sign-out
            icon_div = DivWdg()
            admin_bar_right.add(icon_div)
            icon_button = IconButtonWdg(title="Sign Out", icon="FA_SIGN_OUT_ALT", size=14)
            icon_div.add(icon_button)
            icon_button.add_behavior( {
                'type': 'click_up',
                'cbjs_action': '''
                var ok = function(){
                    var server = TacticServerStub.get();
                    server.execute_cmd("SignOutCmd", {login: bvr.login} );

                    window.location.href="/";
                }
                spt.confirm("Are you sure you wish to sign out?", ok )
                '''
            } )

            admin_bar_left.add("<div><b>ADMIN >></b></div>")

            admin_bar.add_behavior( {
                'type': 'listen',
                'event_name': 'close_admin_bar',
                'cbjs_action': '''
                spt.behavior.destroy_element(bvr.src_el);
                '''
            } )

            project_code = Project.get_project_code()
            site_root = web.get_site_root()
            admin_bar.add_behavior( {
                'type': 'click_up',
                'site_root': site_root,
                'project_code': project_code,
                'cbjs_action': '''
                var url = "/"+bvr.site_root+"/"+bvr.project_code+"/admin/link/_startup";
                window.open(url);
                '''
            } )





        # Add the script editor listener
        load_div = DivWdg()
        top.add(load_div)
        load_div.add_behavior( {
        'type': 'listen',
        'event_name': 'show_script_editor',
        'cbjs_action': '''
        var js_popup_id = "TACTIC Script Editor";
        var js_popup = document.id(js_popup_id);
        if( js_popup ) {
            spt.popup.toggle_display( js_popup_id, false );
        }
        else {
            spt.panel.load_popup(js_popup_id, "tactic.ui.app.ShelfEditWdg", {}, {"load_once": true} );
        }
        '''} )


        # deal with the palette defined in /index which can override the palette

        # tactic_kbd is only true for standard TACTIC index
        tactic_kbd = True
        palette_key = None

        hash = self.kwargs.get("hash")
        if isinstance(hash, tuple) and len(hash) > 0:
            key = hash[0]
            if key == "link":
                key = "index"
        elif hash == ():
            key = "index"
        else:
            key = None
        
        url = None
        if key:
            search = Search("config/url")
            search.add_filter("url", "/%s/%%"%key, "like")
            search.add_filter("url", "/%s"%key)
            search.add_where("or")
            url = search.get_sobject()
            
        
        if url:
            xml = url.get_xml_value("widget")

            palette_key = xml.get_value("element/@palette")

            # Assume no TACTIC kbd functions for custom index
            tactic_kbd = False
            if xml.get_value("element/@tactic_kbd") in [True, "true"]:
                tactic_kbd = True

         
        if not palette_key:
            web = WebContainer.get_web()
            if web.is_admin_page():
                palette_key = 'AQUA'
                #palette_key = 'SILVER'

        if palette_key:
            from pyasm.web import Palette
            palette = Palette.get()
            palette.set_palette(palette_key)

        else:
            from pyasm.web import Palette
            palette = Palette.get()
            palette_key = palette.get_theme()
            if palette_key == "default":
                palette_key = "AQUA"

        colors = palette.get_colors()
        colors = jsondumps(colors)

        script = HtmlElement.script('''
            var env = spt.Environment.get();
            env.set_colors(%s);
            env.set_palette('%s');
            ''' % (colors, palette_key)
        )
        top.add(script)

        
        if tactic_kbd == True:
            body.add_event('onload', 'spt.onload_startup(admin=true)')
        else:
            body.add_event('onload', 'spt.onload_startup(admin=false)')
        


        env = Environment.get()
        client_handoff_dir = env.get_client_handoff_dir(include_ticket=False, no_exception=True)
        client_asset_dir = env.get_client_repo_dir()

        login = Environment.get_login()
        user_name = login.get_value("login")
        user_id = login.get_id()
        login_groups = Environment.get_group_names()

    
        from pyasm.security import Site
        from pyasm.prod.biz import ProdSetting
        from pyasm.biz import PrefSetting

        site = Site.get_site()


        master_enabled = Config.get_value("master", "enabled")
        forwarding_type = Config.get_value("master", "forwarding_type")
        if forwarding_type == "xmlrpc_only":
            master_enabled = "false"
        
        master_site = Config.get_value("master", "site")
        master_project_code = Config.get_value("master", "project_code")
        
        master_url = Config.get_value("master", "url")
        master_url = master_url + "/tactic/default/Api/"
        
        security = Environment.get_security()
        ticket = security.get_ticket()
        if ticket:
            login_ticket = ticket.get_value("ticket")
        else:
            login_ticket = ""
        
        user_timezone = PrefSetting.get_value_by_key('timezone')

        kiosk_mode = Config.get_value("look", "kiosk_mode")
        if not kiosk_mode:
            kiosk_mode = 'false'
        
        script = '''
        var env = spt.Environment.get();
        '''
        
        script += '''env.set_site('%s');''' % site
        script += '''env.set_project('%s');''' % Project.get_project_code()
        script += '''env.set_user('%s');''' % user_name
        script += '''env.set_user_id('%s');''' % user_id
        script += '''
        var login_groups = '%s'.split('|');
        env.set_login_groups(login_groups);
        ''' % '|'.join(login_groups)
        script += '''env.set_client_handoff_dir('%s');''' % client_handoff_dir
        script += '''env.set_client_repo_dir('%s');''' % client_asset_dir
        script += '''env.set_kiosk_mode('%s'); ''' % kiosk_mode

        if master_enabled in ['true', True]:
            script += '''
            env.set_master_enabled('%s');
            env.set_master_url('%s');
            env.set_master_login_ticket('%s');
            env.set_master_project_code('%s');
            env.set_master_site('%s');
            ''' % (master_enabled, master_url, login_ticket, master_project_code, master_site)

        script += '''env.set_user_timezone('%s');''' % user_timezone
        

       
        script = HtmlElement.script(script)
        top.add(script)


        # add in some global switches
        remove_bvr_attrs = ProjectSetting.get_value_by_key("feature/remove_bvr_attrs")
        if remove_bvr_attrs == "true":
            script = HtmlElement.script('''
            spt.behavior.remove_bvr_attrs = true;
            ''')
            top.add(script)



        # add a global container for commonly used widgets
        div = DivWdg()
        top.add(div)
        div.set_id("global_container")

        # add in the app busy widget
        # find out if there is an override for this
        search = Search("config/url")
        search.add_filter("url", "/app_busy")
        url = search.get_sobject()
        if url:
            busy_div = DivWdg()
            div.add(busy_div)

            busy_div.add_class( "SPT_PUW" )
            busy_div.add_styles( "display: none; position: absolute; z-index: 1000" )

            busy_div.add_class("app_busy_msg_block")
            busy_div.add_style("width: 300px")
            busy_div.add_style("height: 100px")
            busy_div.add_style("padding: 20px")
            busy_div.add_color("background", "background3")
            busy_div.add_border()
            busy_div.set_box_shadow()
            busy_div.set_round_corners(20)
            busy_div.set_attr("id","app_busy_msg_block")



            # put the custom url here

            title_wdg = DivWdg()
            busy_div.add(title_wdg)
            title_wdg.add_style("font-size: 20px")
            title_wdg.add_class("spt_app_busy_title")
            busy_div.add("<hr/>")
            msg_div = DivWdg()
            busy_div.add(msg_div)
            msg_div.add_class("spt_app_busy_msg")
 

        else:
            from .page_header_wdg import AppBusyWdg
            div.add( AppBusyWdg() )


        # popup parent
        popup = DivWdg()
        popup.set_id("popup")
        div.add(popup)

        # create another general popup
        popup_div = DivWdg()
        popup_div.add_class("SPT_TEMPLATE")
        popup_div.set_id("popup_container")
        popup_div.add_class("spt_panel")
        popup = PopupWdg(id="popup_template",destroy_on_close=True)
        popup_div.add(popup)
        div.add(popup_div)


        inner_html_div = DivWdg()
        inner_html_div.set_id("inner_html")
        div.add(inner_html_div)


        # add in a global color
        from tactic.ui.input import ColorWdg
        color = ColorWdg()
        div.add(color)

        # add in a global notify wdg
        from .notify_wdg import NotifyWdg
        widget.add(NotifyWdg())

        from tactic.ui.app import DynamicUpdateWdg
        widget.add( DynamicUpdateWdg() )


        return widget




    def get_copyright_wdg(self):
        widget = Widget()

        from datetime import datetime
        today = datetime.today()
        year = datetime.year

        # add the copyright information
        widget.add( "<!--   -->\n")
        widget.add( "<!-- Copyright (c) %s, Southpaw Technology - All Rights Reserved -->\n" % year)
        widget.add( "<!--   -->\n")

        return widget


    def get_css_wdg(self):

        widget = Widget()

        web = WebContainer.get_web()
        context_url = web.get_context_url().to_string()

        skin = web.get_skin()

        version = Environment.get_release_version()

        ui_library = ProjectSetting.get_value_by_key("feature/ui_library") or "bootstrap_material"
        
        css_library = ProjectSetting.get_value_by_key("feature/css_library") or "bootstrap_material"


        widget.add('''
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
        ''')

        # JQuery
        """
        widget.add('''
<script src="https://code.jquery.com/jquery-3.4.1.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jqueryui/1.11.4/jquery-ui.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js" integrity="sha384-UO2eT0CpHqdSJQ6hJty5KVphtPhzWj9WO1clHTMGa3JDZwrnQq4sF86dIHNDz0W1" crossorigin="anonymous"></script>
        ''')
        """
        widget.add('''
<script src="/context/spt_js/jquery/jquery-3.4.1.min.js"></script>
<script src="/context/spt_js/jquery/jquery-ui.min.js"></script>
<script src="/context/spt_js/jquery/popper.min.js" integrity="sha384-UO2eT0CpHqdSJQ6hJty5KVphtPhzWj9WO1clHTMGa3JDZwrnQq4sF86dIHNDz0W1" crossorigin="anonymous"></script>
        ''')
 

        # add form io
        """
        widget.add('''
<!-- Form builder -->
<link rel='stylesheet' href='https://unpkg.com/formiojs@latest/dist/formio.full.min.css'>
<script src='https://unpkg.com/formiojs@latest/dist/formio.full.min.js'></script>
        ''')
        """
        widget.add('''
<!-- Form builder -->
<link rel='stylesheet' href='/context/spt_js/formio/formio.full.min.css'>
<script src='/context/spt_js/formio/formio.full.min.js'></script>
        ''')
 


        if ui_library == "bootstrap":
            widget.add('''
<script src="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js" integrity="sha384-JjSmVgyd0p3pXB1rRibZUAYoIIy6OrQ6VrjIEaFf/nJGzIxFDsf4x0xIM+B07jRM" crossorigin="anonymous"></script>
''')

        else:
            """
<script src="https://unpkg.com/bootstrap-material-design@4.1.1/dist/js/bootstrap-material-design.js" integrity="sha384-CauSuKpEqAFajSpkdjv3z9t8E7RlpJ1UP0lKM/+NdtSarroVKu069AlsRPKkFBz9" crossorigin="anonymous"></script>
            """

            widget.add('''
<!-- Material Design for Bootstrap fonts and icons -->
<link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Roboto:300,400,500,700|Material+Icons" />

<!-- Material Design for Bootstrap JS -->
<script src="/context/spt_js/bootstrap_material_design/bootstrap-material-design-4.1.1.js" integrity="sha384-CauSuKpEqAFajSpkdjv3z9t8E7RlpJ1UP0lKM/+NdtSarroVKu069AlsRPKkFBz9" crossorigin="anonymous"></script>



           ''')


            self.body.add('''
<script>$(document).ready(function() { $('body').bootstrapMaterialDesign(); });</script>
            ''')

            
        if css_library == "default":
            Container.append_seq("Page:css", "%s/spt_js/bootstrap/css/bootstrap.min.css?ver=%s" % (context_url, version))
            
        elif css_library == "bootstrap":
            widget.add('''
<!-- Bootstrap CSS -->
<link rel='stylesheet' href='https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css'>
            ''')
        
        elif css_library == "bootstrap_material":
            """
            widget.add('''
<link rel="stylesheet" href="https://unpkg.com/bootstrap-material-design@4.1.1/dist/css/bootstrap-material-design.min.css" integrity="sha384-wXznGJNEXNG1NFsbm0ugrLFMQPWswR3lds2VeinahP8N0zJw9VWSopbjv2x7WCvX" crossorigin="anonymous" />
            ''')
            """

            # Right now, we have no way to determine a theme (just a palette), however, the
            # dark css file is able to accomodate both due to var(--palette...) ussge
            # We'll keep the file separate until there is more confidence that they
            # can be the same file
            theme = "DARK"
            if theme == "DARK":
                bootstrap_material_css = "/context/spt_js/bootstrap_material_design/bmd-bs-dark.css"
                widget.add('''<link rel="stylesheet" href="%s"/>''' % bootstrap_material_css)
            elif theme == "LIGHT":
                bootstrap_material_css = "/context/spt_js/bootstrap_material_design/bmd-bs-light.css"
                widget.add('''<link rel="stylesheet" href="%s"/>''' % bootstrap_material_css)
            else:
                widget.add('''
                <link rel="stylesheet" href="/context/spt_js/bootstrap_material_design/bootstrap-material-design-4.1.1.min.css" integrity="sha384-wXznGJNEXNG1NFsbm0ugrLFMQPWswR3lds2VeinahP8N0zJw9VWSopbjv2x7WCvX" crossorigin="anonymous" />
                ''')



        
        else:
            Container.append_seq("Page:css", css_library)
            
        Container.append_seq("Page:css", "%s/spt_js/font-awesome-5.12.0/css/all.css?ver=%s" % (context_url, version))



        # add the color wheel css (DEPRECATED)
        #Container.append_seq("Page:css", "%s/spt_js/mooRainbow/Assets/mooRainbow.css" % context_url)
        Container.append_seq("Page:css", "%s/spt_js/mooDialog/css/MooDialog.css" % context_url)
        Container.append_seq("Page:css", "%s/spt_js/mooScrollable/Scrollable.css" % context_url)

        # first load context css
        Container.append_seq("Page:css", "%s/style/layout.css" % context_url)



        # video js
        Container.append_seq("Page:css", "%s/spt_js/video/video-js.css" % context_url)


        # get all of the registered css file
        css_files = Container.get_seq("Page:css")
        for css_file in css_files:
            widget.add('<link rel="stylesheet" href="%s" type="text/css" />\n' % css_file )

        # custom js files to include
        includes = Config.get_value("install", "include_css")
        includes = includes.split(",")
        for include in includes:
            include = include.strip()
            if include:
                widget.add('<link rel="stylesheet" href="%s" type="text/css" />\n' % include )



        includes = ProjectSetting.get_value_by_key("css_libraries")
        includes = includes.split(",")
        for include in includes:
            include = include.strip()
            if include:
                widget.add('<link rel="stylesheet" href="%s" type="text/css" />\n' % include )

        return widget


class JavascriptImportWdg(BaseRefreshWdg):

    def get_display(self):

        web = WebContainer.get_web()
        context_url = web.get_context_url().to_string()
        js_url = "%s/javascript" % context_url
        spt_js_url = "%s/spt_js" % context_url    # adding new core "spt" javascript library folder

        version = Environment.get_release_version()

        # add some third party libraries
        third_party = JSIncludes.third_party
        security = Environment.get_security()

        Container.append_seq("Page:js", "%s/load-image.min.js" % spt_js_url)
        Container.append_seq("Page:js", "%s/rrule/rrule.js" % spt_js_url)
        Container.append_seq("Page:js", "%s/moment.min.js" % spt_js_url)
        Container.append_seq("Page:js", "%s/moment-timezone.min.js" % spt_js_url)
        Container.append_seq("Page:js", "%s/html2canvas.js" % spt_js_url)
       
        # TESTING
        # viewer.js from pdfjs may not be needed in the future. For now,
        # it was added for KYC, which requires this. (added 2019-02)
        #Container.append_seq("Page:js", "/plugins/pdfjs/build/pdf.js")
        #Container.append_seq("Page:js", "/plugins/pdfjs/web/viewer.js")

        if not web.is_admin_page():
            use_require = ProjectSetting.get_value_by_key("js_libraries/require")
            if use_require == "true":
                Container.append_seq("Page:js", "%s/require.js" % spt_js_url)

            use_jquery = ProjectSetting.get_value_by_key("js_libraries/jquery")
            if use_jquery == "true":
                Container.append_seq("Page:js", "%s/jquery.js" % spt_js_url)


        for include in JSIncludes.third_party:
            Container.append_seq("Page:js", "%s/%s" % (spt_js_url,include))


        all_js_path = JSIncludes.get_compact_js_filepath()

        if os.path.exists( all_js_path ):
            Container.append_seq("Page:js", "%s/%s" % (context_url, JSIncludes.get_compact_js_context_path_suffix()))
        else:
            #for include in JSIncludes.legacy_core:
            #    Container.append_seq("Page:js", "%s/%s" % (js_url,include))

            for include in JSIncludes.spt_js:
                Container.append_seq("Page:js", "%s/%s" % (spt_js_url,include))

            #for include in JSIncludes.legacy_app:
            #    Container.append_seq("Page:js", "%s/%s" % (js_url,include))


        includes = ProjectSetting.get_value_by_key("js_libraries")
        if includes == "__NONE__":
            pass
        elif includes:
            includes = includes.split(",")
            for include in includes:
                include = include.strip()
                if include:
                    Container.append_seq("Page:js", include)
        else:
            # custom js files to include
            includes = Config.get_value("install", "include_js")
            includes = includes.split(",")
            for include in includes:

                include = include.strip()
                if include:
                    Container.append_seq("Page:js", include)



        widget = Widget()


        js_files = Container.get("Page:js")
        for js_file in js_files:
            widget.add('<script src="%s?ver=%s" ></script>\n' % (js_file,version) )

        return widget



class TitleTopWdg(TopWdg):

    '''Top used in title page for logins.  This does not include any of the
    js libraries or other common TACTIC functionaity'''
    
    def init(self):
        self.body = HtmlElement("body")

        web = WebContainer.get_web()
        self.body.add_color("color", "color")


        #if web.is_title_page():
        #    self.body.add_gradient("background", "background", 0, -20)
        #else:
        #    self.body.add_gradient("background", "background", 0, -15)
        self.body.add_color("background", "background")

        self.body.add_style("background-attachment: fixed !important")
        #self.body.add_style("min-height: 1200px")
        self.body.add_style("height: 100%")
        self.body.add_style("width: 100%")
        self.body.add_style("margin: 0px")
        self.body.add_style("overflow: auto")


    def get_display(self):

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
        widget.add( self.get_copyright_wdg() )
        widget.add(html)


        # create the header
        head = HtmlElement("head")
        html.add(head)

        head.add('<meta http-equiv="Content-Type" content="text/html;charset=UTF-8"/>\n')
        head.add('<meta http-equiv="X-UA-Compatible" content="IE=edge"/>\n')

        # Add the tactic favicon
        head.add('<link rel="shortcut icon" href="/context/favicon.ico" type="image/x-icon"/>')

        # add the css styling
        head.add(self.get_css_wdg())

        # add the title in the header
        try:
            project = Project.get()
        except Exception as e:
            print("ERROR: ", e)
            # if the project doesn't exist, then use the admin project
            project = Project.get_by_code("admin")
        project_code = project.get_code()
        project_title = project.get_value("title")

        if project_code == 'admin':
            head.add("<title>TACTIC</title>\n" )
        else:
            head.add("<title>%s</title>\n" % project_title )

        # add google analytics
        head.add(GoogleAnalyticsWdg())

        # add the body
        body = self.body
        html.add( body )

        body.add("<form id='form' style='margin-bottom: 0px' name='form' method='post' enctype='multipart/form-data'>\n")

        for content in self.widgets:
            body.add(content)

        body.add("</form>\n")

        if web.is_admin_page():
            from .tactic_branding_wdg import TacticCopyrightNoticeWdg
            copyright = TacticCopyrightNoticeWdg()
            body.add(copyright)

        return widget





__all__.extend( ['IndexWdg', 'SitePage', 'SiteXMLRPC'] )
from pyasm.search import SearchType
from pyasm.web import WebContainer, AppServer
from pyasm.prod.service import BaseXMLRPC
from pyasm.common import SecurityException


class IndexWdg(Widget):
    # This is the outside wrapper for an HTML5 application

    def __init__(self, hash=""):
        self.hash = hash
        self.top = DivWdg()
        super(IndexWdg, self).__init__()

    def get_display(self):

        top = self.top
        top.set_id('top_of_application')

        from tactic.ui.panel import HashPanelWdg 
        splash_div = HashPanelWdg.get_widget_from_hash("/splash", return_none=True)
        if not splash_div:

            splash_div = DivWdg()
            splash_div.add_style('text-align: center')
            splash_div.add('<img src="/context/icons/common/indicator_snake.gif" border="0"/>')
            splash_div.add("&nbsp; &nbsp;")
            project = Project.get()
            title = project.get_value("title")
            if not title:
                title = "TACTIC"

            splash_div.add('''Loading "%s" ....'''% title)
            splash_div.add_style("font-size: 1.5em")
            splash_div.add_style("margin: 200 0 500 0")


        splash_div.add_behavior( {
            'type': 'load',
            'hash': self.hash,
            'cbjs_action': '''
            if (bvr.hash) {
                spt.hash.hash = "/" + bvr.hash;
            }
            else {
                spt.hash.hash = "/index";
            }
            spt.hash.set_index_hash("link/_startup");
            '''
        } )


        top.add(splash_div)

        return top





class SitePage(AppServer):
    def __init__(self, context=None):
        super(SitePage,self).__init__()
        self.project_code = context
        self.custom_url = None


    def set_templates(self):

        project_code = WebContainer.get_web().get_full_context_name()
        if project_code == "default":
            project_code = Project.get_default_project()


        try:
            SearchType.set_global_template("project", project_code)
        except SecurityException as e:
            print("WARNING: ", e)





    def get_application_wdg(self):

        page = None

        try:
            project = Project.get()
        except Exception as e:
            Project.set_project("sthpw")
            from pyasm.widget import Error404Wdg
            page = Error404Wdg()
            page.set_message(e.__str__())
            page.status = ''


        application = self.get_top_wdg()

        # get the main page widget
        # NOTE: this needs to happen after the body is put in a Container
        if not page:
            page = self.get_page_widget()
        page.set_as_top()
        if isinstance(page, basestring):
            page = StringWdg(page)

        application.add(page, 'content')


        return application




    def get_page_widget(self):
        try:
            hash = self.hash
        except:
            hash = None
        if hash:
            hash = "/".join(hash)
        else:
            hash = None

        # default index widget
        index = IndexWdg(hash=hash)

        return index


    def get_top_wdg(self):
        ''' A custom widget can replace TopWdg per custom URL or per project.
         1. If a custom url specifies a top class through the top_wdg_cls attribute, 
            then this class is used.
         2. If no custom url is specified, and a project top class is specified
            through the ProjectSetting key top_wdg_cls, this class is used 
            except for TACTIC admin pages.
         3. The default widget used is tactic.ui.app.TopWdg.'''


        top_wdg_cls = None
       
        if not self.hash and not self.custom_url:
            search = Search("config/url")
            search.add_filter("url", "/index")
            self.custom_url = search.get_sobject()



        # TEST Using X-SendFile
        #if self.hash and self.hash[0] == 'ASSETS':
        #    self.top = XSendFileTopWdg(hash=self.hash)
        #    return self.top

        # REST API
        if self.hash and self.hash[0] == 'REST':
            handler = 'tactic.protocol.APIRestHandler' 
            hash = "/".join(self.hash)
            hash = "/%s" % hash
            self.top = CustomTopWdg(url=None, hash=hash, handler=handler)
            return self.top




        
        if self.custom_url:
            xml = self.custom_url.get_xml_value("widget")
            index = xml.get_value("element/@index")
            admin = xml.get_value("element/@admin")
            top_wdg_cls = xml.get_value("element/@top_wdg_cls")
            widget = xml.get_value("element/@widget")
            bootstrap = xml.get_value("element/@bootstrap")
            if index == 'true' or admin == 'true':
                pass
            elif widget == 'true':
                hash = "/".join(self.hash)
                hash = "/%s" % hash
                self.top = CustomTopWdg(url=self.custom_url, hash=hash)
                return self.top
 
        if not top_wdg_cls:
            if self.hash and self.hash[0] == "admin":
                pass
            else:
                from pyasm.biz import ProjectSetting
                top_wdg_cls = ProjectSetting.get_value_by_key("top_wdg_cls")
        
        if top_wdg_cls:
            self.top = Common.create_from_class_path(top_wdg_cls, {}, {'hash': self.hash})
        else:
            from tactic.ui.app import TopWdg
            self.top = TopWdg(hash=self.hash)
        
        return self.top



class BootstrapIndexWdg(BaseRefreshWdg):

    def get_display(self):

        top = Widget()
        from tactic.ui.panel import CustomLayoutWdg
        #widget = CustomLayoutWdg(view="bootstrap.basic.test_mootools", is_top=True)
        widget = CustomLayoutWdg(view="bootstrap.themes.jumbotron.main2", is_top=True)
        #widget = CustomLayoutWdg(view="bootstrap.basic.test2", is_top=True)
        top.add(widget)
        return top



class CustomTopWdg(BaseRefreshWdg):

    def get_display(self):

        # Custom URLs have the ability to send out different content types
        url = self.kwargs.get("url")

        web = WebContainer.get_web()

        #content_type = self.kwargs.get("content_type")
        #print("content_type: ", content_type)

        hash = self.kwargs.get("hash")
        ticket = web.get_form_value("ticket")
        method = web.get_request_method()
        headers = web.get_request_headers()
        accept = headers.get("Accept")
        if url:
            expression = url.get_value("url")
            # extract values from custom url
            kwargs = Common.extract_dict(hash, expression)
        else:
            kwargs = {}
       
        
        # Does the URL listen to specific Accept values?
        # or does it enforce a return content type ... and how does one
        # know what exactly is supported?  Accept is kind of complicated.
        # Easier to put in as a paramenter ... but should accept both

        # get the widget designated for hash
        kwargs['Accept'] = accept
        kwargs['Method'] = method

        handler = self.kwargs.get("handler")
        if handler:
            hash_widget = Common.create_from_class_path(handler, [], kwargs)
        else:
            from tactic.ui.panel import HashPanelWdg 
            hash_widget = HashPanelWdg.get_widget_from_hash(hash, kwargs=kwargs)
 
        # Really, the hash widget should determine what is returned, but
        # should take the Accept into account.  It is not up to this
        # class to determine what is or isn't implemented, nor is it the
        # responsibility of this class to convert the data.  So, it
        # returns whatever is given.
        try:
            custom_accept = hash_widget.get_content_type()
            accept = custom_accept
        except AttributeError as e:
            pass

        widget = Widget()
        #
        # Example implementation of custom script, run by hash_widget
        #
        if accept == "application/json":
            value = hash_widget.get_display()
            value = jsondumps(value)
            web.set_content_type(accept)

        elif accept == "application/xml":
            from pyasm.common import Xml
            value = hash_widget.get_display()
            if isinstance(value, basestring):
                xml = Xml(value)
                value = xml.to_string()
            elif isinstance(value, Xml):
                value = value.to_string()
            web.set_content_type(accept)


        elif accept == "plain/text":
            from pyasm.common import Xml
            value = hash_widget.get_display()
            value = str(value)

            web.set_content_type(accept)

        else:
            # return text/html
            value = DivWdg()
            if isinstance(hash_widget, basestring):
                value.add(hash_widget)
            else:
                value.add(hash_widget.get_display())
            current_type = web.get_content_type()
            if not current_type:
                web.set_content_type("text/html")

        widget.add(value)

        return widget



class XSendFileTopWdg(BaseRefreshWdg):

    def get_display(self):

        web = WebContainer.get_web()
        response = web.get_response()

        # get info from url
        site_obj = Site.get()
        path = web.get_request_path()
        path_info = site_obj.break_up_request_path(path)
        site = path_info.get("site")
        project_code = path_info.get("project_code")


        # find the relative path
        hash = self.kwargs.get("hash")
        parts = hash[1:]
        rel_path = "/".join(parts)

        #rel_path = "asset/Fantasy/Castle/54d45150c61251f65687d716cc3951f1_v001.jpg"


        # construct all of the paths
        asset_dir = web.get_asset_dir()
        base_dir = "%s/%s" % (asset_dir, project_code)
        path = "%s/%s" % (base_dir, rel_path)
        filename = os.path.basename(rel_path)



        # determine the mimetype automatically
        import mimetypes
        base, ext = os.path.splitext(path)
        ext = ext.lower()
        mimetype = mimetypes.types_map[ext]

        headers = response.headers
        response.headers['Content-Type'] = mimetype

        response.headers['Content-Disposition'] = 'inline; filename={0}'.format(filename)

        use_xsendfile = True
        if use_xsendfile:
            response.headers['X-Sendfile'] = path
            return Widget(path)

        else:

            response.headers['Content-Transfer-Encoding'] = 'BINARY'

            widget = Widget()
            f = open(path, 'rb')
            data = f.read()
            f.close()

            widget.add(data)
            return widget

        #import base64
        #data64 = base64.b64encode(data)
        #widget.add(data64)
        #return widget



class SiteXMLRPC(BaseXMLRPC):
    def set_templates(self):
        context = WebContainer.get_web().get_full_context_name()
        SearchType.set_global_template("project", context)







