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

import js_includes

from pyasm.common import Common, Container, Environment, jsondumps, jsonloads, Config
from pyasm.biz import Project, ProjectSetting
from pyasm.web import WebContainer, Widget, HtmlElement, DivWdg, BaseAppServer, Palette, SpanWdg
from pyasm.widget import IconWdg
from pyasm.search import Search
from pyasm.security import Site

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.container import PopupWdg
from tactic.ui.app import TacticCopyrightNoticeWdg
from tactic.ui.widget import IconButtonWdg



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

            // find out if any of the parents of target is the focus element
            for (var i = 0; i < spt.body.focus_elements.length; i++) {
                var el = spt.body.focus_elements[i];
                var hit = false;

                for (var j = 0; j < targets.length; j++) {
                    var target = targets[j];
                    if (target == el) {
                         hit = true;
                         break;
                         
                    }
                }
        
                if (hit)
                    break;
                else {
                    if ( el.isVisible() && el.on_complete ) {
                        el.on_complete(el);
                    }
                    else {
                        spt.hide(el);
                    }
      
                }
            }
            if (!hit)
                spt.body.focus_elements = [];

        }
        //bvr.src_el.addEvent("mousedown", spt.body.hide_focus_elements);
        document.id(document.body).addEvent("mousedown", spt.body.hide_focus_elements);

        '''
        } )

        web = WebContainer.get_web()
        self.body.add_color("color", "color")

        #if web.is_title_page():
        #    self.body.add_gradient("background", "background", 0, -20)
        #else:
        #    self.body.add_gradient("background", "background", 0, -15)
        self.body.add_color("background", "background")

        self.body.add_style("background-attachment: fixed !important")
        self.body.add_style("margin: 0px")
        self.body.add_style("padding: 0px")


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
            var kwargs = {
                view: view,  
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


            spt.panel.load_popup(title, class_name, kwargs);
            '''
        } )


        self.body.add_relay_behavior( {
            'type': 'click',
            'bvr_match_class': 'tactic_load',
            'cbjs_action': '''

            var view = bvr.src_el.getAttribute("view");
            if (!view) {
                spt.alert("No view found");
            }

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



            var class_name = 'tactic.ui.panel.CustomLayoutWdg';
            var kwargs = {
                view: view,  
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
            if (target_class.indexOf(".") != "-1") {
                var parts = target_class.split(".");
                var top = bvr.src_el.getParent("."+parts[0]);
                var target = top.getElement("."+parts[1]);  
            }
            else {
                var target = document.id(document.body).getElement("."+target_class);
            }

            spt.panel.refresh(target);
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



        # add the body
        body = self.body
        html.add( body )
        body.add_event('onload', 'spt.onload_startup(this)')


        top = self.top

        # Add a NOSCRIPT tag block here to provide a warning message on browsers where 'Enable JavaScript'
        # is not checked ... TODO: clean up and re-style to make look nicer
        top.add( """
        <NOSCRIPT>
        <div style="border: 2px solid black; background-color: #FFFF99; color: black; width: 600px; height: 70px; padding: 20px;">
        <img src="%s" style="border: none;" /> <b>Javascript is not enabled on your browser!</b>
        <p>This TACTIC powered, web-based application requires JavaScript to be enabled in order to function. In your browser's options/preferences, please make sure that the 'Enable JavaScript' option is checked on, click OK to accept the settings change, and then refresh this web page.</p>
        </div>
        </NOSCRIPT>
        """ % ( IconWdg.get_icon_path("ERROR") ) )




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



        if self.widgets:
            content_wdg = self.get_widget('content')
        else:
            content_wdg = Widget()
            self.add(content_wdg)

        content_div.add( content_wdg )
        
        # add a calendar wdg
        
        from tactic.ui.widget import CalendarWdg
        cal_wdg = CalendarWdg(css_class='spt_calendar_template_top')
        cal_wdg.top.add_style('display: none')
        content_div.add(cal_wdg)

        if web.is_admin_page():
            from tactic_branding_wdg import TacticCopyrightNoticeWdg
            branding = TacticCopyrightNoticeWdg(show_license_info=True)
            top.add(branding)


        # add the admin bar
        security = Environment.get_security()
        if not web.is_admin_page() and security.check_access("builtin", "view_site_admin", "allow"):

            div = DivWdg()
            top.add(div)
            top.add_style("padding-top: 21px")

            div.add_class("spt_admin_bar")



            # home
            icon_div = DivWdg()
            div.add(icon_div)
            icon_div.add_style("float: left")
            icon_div.add_style("margin-right: 10px")
            icon_div.add_style("margin-top: -3px")
            icon_button = IconButtonWdg(title="Home", icon="BS_HOME")
            icon_div.add(icon_button)
            icon_button.add_behavior( {
                'type': 'click_up',
                'cbjs_action': '''
                window.location.href="/";
                '''
            } )



            div.add_style("height: 15px")
            div.add_style("padding: 3px 0px 3px 15px")
            #div.add_style("margin-bottom: -5px")
            div.add_style("position: fixed")
            div.add_style("top: 0px")
            div.add_style("left: 0px")
            div.add_style("opacity: 0.7")
            div.add_style("width: 100%")
            #div.add_gradient("background", "background2", 20, 10)
            div.add_style("background-color", "#000")
            div.add_style("color", "#FFF")
            div.add_style("z-index", "1000")
            div.add_class("hand")
            div.set_box_shadow("0px 5px 5px")

            # remove
            icon_div = DivWdg()
            div.add(icon_div)
            icon_div.add_style("float: right")
            icon_div.add_style("margin-right: 10px")
            icon_div.add_style("margin-top: -3px")
            icon_button = IconButtonWdg(title="Remove Admin Bar", icon="BS_REMOVE")
            icon_div.add(icon_button)
            icon_button.add_behavior( {
                'type': 'click_up',
                'cbjs_action': '''
                var parent = bvr.src_el.getParent(".spt_admin_bar");
                bvr.src_el.getParent(".spt_top").setStyle("padding-top", "0px");
                spt.behavior.destroy_element(parent);
                '''
            } )

            # sign-out
            icon_div = DivWdg()
            div.add(icon_div)
            icon_div.add_style("float: right")
            icon_div.add_style("margin-right: 5px")
            icon_div.add_style("margin-top: -3px")
            icon_button = IconButtonWdg(title="Sign Out", icon="BS_LOG_OUT")
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



            div.add("<b>ADMIN >></b>")


            div.add_behavior( {
                'type': 'listen',
                'event_name': 'close_admin_bar',
                'cbjs_action': '''
                bvr.src_el.getParent(".spt_top").setStyle("padding-top", "0px");
                spt.behavior.destroy_element(bvr.src_el);
                '''
            } )

            div.add_behavior( {
                'type': 'mouseover',
                'cbjs_action': '''
                bvr.src_el.setStyle("opacity", 0.85)
                //new Fx.Tween(bvr.src_el).start('height', "30px");
                '''
            } )
            div.add_behavior( {
                'type': 'mouseout',
                'cbjs_action': '''
                bvr.src_el.setStyle("opacity", 0.7)
                //new Fx.Tween(bvr.src_el).start('height', "15px");
                '''
            } )
            project_code = Project.get_project_code()
            site_root = web.get_site_root()
            div.add_behavior( {
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
        if self.kwargs.get("hash") == ():
            key = "index"
            search = Search("config/url")
            search.add_filter("url", "/%s/%%"%key, "like")
            search.add_filter("url", "/%s"%key)
            search.add_where("or")
            url = search.get_sobject()
            if url:
                xml = url.get_xml_value("widget")
                palette_key = xml.get_value("element/@palette")

                # look up palette the expression for index
                from pyasm.web import Palette
                palette = Palette.get()

                palette.set_palette(palette_key)
                colors = palette.get_colors()
                colors = jsondumps(colors)

                script = HtmlElement.script('''
                    var env = spt.Environment.get();
                    env.set_colors(%s);
                    env.set_palette('%s');
                    ''' % (colors, palette_key)
                )
                top.add(script)


        env = Environment.get()
        client_handoff_dir = env.get_client_handoff_dir(include_ticket=False, no_exception=True)
        client_asset_dir = env.get_client_repo_dir()

        login = Environment.get_login()
        user_name = login.get_value("login")
        user_id = login.get_id()
        login_groups = Environment.get_group_names()

    
        from pyasm.security import Site
        site = Site.get_site()
       
        kiosk_mode = Config.get_value("look", "kiosk_mode")
        if not kiosk_mode:
            kiosk_mode = 'false'
        # add environment information
        script = HtmlElement.script('''
        var env = spt.Environment.get();
        env.set_site('%s');
        env.set_project('%s');
        env.set_user('%s');
        env.set_user_id('%s');
        var login_groups = '%s'.split('|');
        env.set_login_groups(login_groups);
        env.set_client_handoff_dir('%s');
        env.set_client_repo_dir('%s');
        env.set_kiosk_mode('%s');

        ''' % (site, Project.get_project_code(), user_name, user_id, '|'.join(login_groups), client_handoff_dir,client_asset_dir, kiosk_mode))
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
            from page_header_wdg import AppBusyWdg
            div.add( AppBusyWdg() )


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


        inner_html_div = DivWdg()
        inner_html_div.set_id("inner_html")
        div.add(inner_html_div)


        # add in a global color
        from tactic.ui.input import ColorWdg
        color = ColorWdg()
        div.add(color)

        # add in a global notify wdg
        from notify_wdg import NotifyWdg
        widget.add(NotifyWdg())

        from tactic.ui.app import DynamicUpdateWdg
        widget.add( DynamicUpdateWdg() )


        return widget




    def get_copyright_wdg(self):
        widget = Widget()

        # add the copyright information
        widget.add( "<!--   -->\n")
        widget.add( "<!-- Copyright (c) 2005-2014, Southpaw Technology - All Rights Reserved -->\n")
        widget.add( "<!--   -->\n")

        return widget


    def get_css_wdg(self):

        widget = Widget()

        web = WebContainer.get_web()
        context_url = web.get_context_url().to_string()

        skin = web.get_skin()

        version = Environment.get_release_version()

        # Bootstrap
        use_bootstrap = True
        if use_bootstrap:
            Container.append_seq("Page:css", "%s/spt_js/bootstrap/css/bootstrap.min.css?ver=%s" % (context_url, version))


        Container.append_seq("Page:css", "%s/spt_js/font-awesome-4.7.0/css/font-awesome.css?ver=%s" % (context_url, version))



        # add the color wheel css
        Container.append_seq("Page:css", "%s/spt_js/mooRainbow/Assets/mooRainbow.css" % context_url)
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
                print("include: ", include)
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
        third_party = js_includes.third_party
        security = Environment.get_security()

        Container.append_seq("Page:js", "%s/load-image.min.js" % spt_js_url)

        if not web.is_admin_page():
            Container.append_seq("Page:js", "%s/require.js" % spt_js_url)
            use_jquery = ProjectSetting.get_value_by_key("js_libraries/jquery")
            if use_jquery == "true":
                Container.append_seq("Page:js", "%s/jquery.js" % spt_js_url)


        for include in js_includes.third_party:
            Container.append_seq("Page:js", "%s/%s" % (spt_js_url,include))

        all_js_path = js_includes.get_compact_js_filepath()

        if os.path.exists( all_js_path ):
            Container.append_seq("Page:js", "%s/%s" % (context_url, js_includes.get_compact_js_context_path_suffix()))
        else:
            #for include in js_includes.legacy_core:
            #    Container.append_seq("Page:js", "%s/%s" % (js_url,include))

            for include in js_includes.spt_js:
                Container.append_seq("Page:js", "%s/%s" % (spt_js_url,include))

            #for include in js_includes.legacy_app:
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
        self.body.add_style("margin: 0px")


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

        # add the body
        body = self.body
        html.add( body )

        body.add("<form id='form' name='form' method='post' enctype='multipart/form-data'>\n")

        for content in self.widgets:
            body.add(content)

        body.add("</form>\n")

        if web.is_admin_page():
            from tactic_branding_wdg import TacticCopyrightNoticeWdg
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
        top.add_style("height: 100%")
        top.add_style("width: 100%")
        top.add_style("overflow-x: auto")
        top.add_style("overflow-y: auto")

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
        if type(page) in types.StringTypes:
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
            elif bootstrap == 'true':
                widget = BootstrapIndexWdg()
                return widget
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







