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
#
__all__ = ["PageHeaderWdg", "ProjectLoginEditWdg", "ProjectSelectWdg", "PasswordEditWdg", 'AppBusyWdg', 'ProjectCreateWdg']

import re
from pyasm.common import Environment, TacticException, Common, Config
from pyasm.search import Search, SearchKey
from pyasm.web import *
from pyasm.biz import *   # Project is part of pyasm.biz
from pyasm.widget import ThumbWdg, SelectWdg, ButtonWdg, TextWdg, CheckboxWdg, IconWdg, PasswordWdg, HiddenWdg, HintWdg, RadioWdg


from tactic.ui.common import BaseRefreshWdg
from tactic.ui.container import PopupWdg, SmartMenu, Menu, MenuItem
from tactic.ui.widget import PageHeaderGearMenuWdg, TextBtnWdg, ActionButtonWdg
from tactic.ui.input import UploadButtonWdg

class PageHeaderWdg(Widget):

    def __init__(self, title='page_header', show_project=True):
        super(PageHeaderWdg,self).__init__(title)
        self.title = title

        self.show_project = show_project
        if self.show_project in ['false', False]:
            self.show_project = False
        else:
            self.show_project = True
      


    def get_display(self):

        web = WebContainer.get_web()

        
        tactic_header = Table()
        tactic_header.add_row()
        tactic_header.add_color("color", "color2")


        # tactic logo and release info
        #skin = web.get_skin()
        #src = '/context/skins/' + skin + '/images/tactic_logo.png'
        src = '/context/tactic_logo.png'
        img = HtmlElement.img(src)
        img.add_class('hand')
        img.add_attr('title', 'Go to home page')
        img.add_behavior({'type': 'click_up', 'cbjs_action': "window.location='/tactic/'"})

        rel_div = DivWdg()
        rel_div.add("&nbsp;"*3)
        rel_div.add("Release: %s" %Environment.get_release_version() )
        rel_div.add_style("font-size: 9px")
        # Need this to override the above color in add_looks
        rel_div.add_color("color", "color2")

        tactic_wdg = Table()

        tactic_wdg.add_style("width: 180px")
        tactic_wdg.add_row()
        td = tactic_wdg.add_cell( img )
        td.set_style("width:100px")
        tactic_wdg.add_row()
        td = tactic_wdg.add_cell( rel_div )
        td.set_style("text-align: left") 

        td = tactic_header.add_cell( tactic_wdg )
       
        # add the project thumb and title
        project = Project.get()

        if self.show_project:
            thumb_div = DivWdg()
            td = tactic_header.add_cell( thumb_div )
            thumb_div.add_style("height: 28px")
            thumb_div.add_style("overflow: hidden")
            thumb_div.add_border(modifier=-10)
            thumb_div.add_style("-moz-border-radius: 3px")

            thumb = ThumbWdg()
            thumb_div.add(thumb)
            thumb.set_sobject(project)
            thumb.set_icon_size("45")
            td.set_style("vertical-align: top; padding-right:14px;padding-left: 3px")

            from pyasm.security import Site
            site = Site.get().get_site()
            if site:
                title = "%s : %s " % (site, project.get_value("title"))
            else:
                title = project.get_value("title")
            td = tactic_header.add_cell( title )
            #td.add_looks( "fnt_title_1" )
            td.add_style("font-size: 20px")
            td.add_style("white-space: nowrap")
            td.add_style("padding-left: 14px")

            # project selection 
            td = tactic_header.add_cell()
            project_div = DivWdg()
            project_div.add_style("margin-top: -5px")
            project_div.add(ProjectSelectWdg() )
            td.add( project_div )
            td.set_style("padding-left: 14px")
             

            # Global Actions Gear Menu (contains links to Documentation) ...
            action_bar_btn_dd = PageHeaderGearMenuWdg()
            action_div = DivWdg(action_bar_btn_dd)
            action_div.add_style("margin-top: -5px")
            td = tactic_header.add_cell( action_div )

            if PrefSetting.get_value_by_key('subscription_bar') == 'true':
                from message_wdg import SubscriptionBarWdg
                sub = SubscriptionBarWdg(mode='popup')
                tactic_header.add_cell(sub)

        # user login

        # user
        user = Environment.get_login()
        full_name = user.get_full_name()
        user_div = SpanWdg( HtmlElement.b( "%s&nbsp;&nbsp;" % full_name) , css='hand')       
        user_div.set_style("padding-right:10px")

        # signout
        login = Environment.get_security().get_login()
        search_key = SearchKey.get_by_sobject(login)
        span = SpanWdg()
        span.add( user_div )
        user_div.add_attr('spt_nudge_menu_vert', '20')
       
        td = tactic_header.add_cell(span)       
        td.set_style("width:100%; text-align:right; white-space: nowrap")



        from tactic.ui.widget import SingleButtonWdg
        button = SingleButtonWdg(title='My Account', icon="BS_USER", show_arrow=True)
        button_div = DivWdg(button)
        button_div.add_style("margin-top: -5px")
        button.add_attr('spt_nudge_menu_horiz', '-80')
        button.add_attr('spt_nudge_menu_vert', '10')

        td = tactic_header.add_cell(button_div)
    

        menus = self.get_smart_menu()
        # TODO: this part seems redundant to attach to both
        SmartMenu.add_smart_menu_set(user_div, [menus])
        SmartMenu.assign_as_local_activator(user_div, None, True)

        SmartMenu.add_smart_menu_set(button, [menus])
        SmartMenu.assign_as_local_activator(button, None, True)

   


        td.set_style("width:100%;")
        button = SingleButtonWdg(title='Help', icon=IconWdg.HELP_BUTTON, show_arrow=False)
        #button.add_behavior( {
        #'type': 'click_up',
        #'cbjs_action': '''
        #window.open("/doc/")
        #'''
        #} )

        button.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        spt.named_events.fire_event("show_help")
        '''
        } )


        from tactic.ui.container import DialogWdg
        help_dialog = DialogWdg(z_index=900, show_pointer=False)
        td.add(help_dialog)
        help_dialog.add_title("Help")
        help_dialog.add_class("spt_help")


        # container for help
        help_div = DivWdg()
        help_dialog.add(help_div)

        from .help_wdg import HelpWdg
        help_wdg = HelpWdg()
        help_div.add(help_wdg)


        button_div = DivWdg(button)
        button_div.add_style("margin-top: -5px")
        td = tactic_header.add_cell(button_div)
        td.set_style("width:100%; text-align:right; white-space: nowrap")


        # Layout the Main Header Table
        main_div = DivWdg()

        # TEST: NEW LAYOUT
        if Config.get_value("install", "layout") == "fixed":
            main_div.add_style("position: fixed")
            main_div.add_style("z-index: 100")
            main_div.add_style("width: 100%")

        license = Environment.get_security().get_license()

        if not license.is_licensed():
            from tactic.ui.app import LicenseManagerWdg
            license_manager = LicenseManagerWdg(use_popup=True)
            main_div.add(license_manager)

        

        # create the header table
        tactic_header_div = DivWdg()
        tactic_header_div.add(tactic_header)
        tactic_header_div.add_gradient("background", "background2", 10, -10)

        main_div.add(tactic_header_div)

        main_div.add( self.get_js_popup() )


        """
        main_div.add( HelpPopupWdg() )

        # FIXME: is this even used at all?
        action_bar_popup = PopupWdg( id="ActionBarWdg_popup", allow_page_activity=True, width="636px" )
        action_bar_popup.add_title( "TACTIC&trade; Action Bar" )
        action_bar_popup.add( ActionBarWdg() )
        main_div.add( action_bar_popup )
        """

        # FIXME(?): does this CommonPopup need to be at z_start=300? By default popups will be at z_start=200
        popup = PopupWdg( id="CommonPopup", allow_page_activity=True, width="600px", z_start=300 )
        popup.add('Tools', 'title')

        main_div.add( popup )

        
        return main_div


    def get_smart_menu(cls):

        user = Environment.get_login()
        display_name = user.get("display_name")
        if not display_name:
            display_name = user.get_value("login")

        menu_data = []

        menu_data.append( {
            "type": "title", "label": "Account (%s)" % display_name
        } )

        menu_data.append( {
            "type": "action",
            "label": "Edit My Account",
            "bvr_cb": {
                'cbjs_action': '''
                 var server = TacticServerStub.get();
                    var ticket = server.get_login_ticket();
                    var kwargs = {
                       ticket: ticket,
                       view: 'edit_account',
                       mode: 'edit'
                    }
                    var class_name = 'tactic.ui.app.ProjectLoginEditWdg';

                    spt.panel.load_popup("My Account", class_name, kwargs);
                ''' 
            }
        } )

        menu_data.append( { 'type': 'separator' } )

        menu_data.append( {
            "type": "action",
            "label": "Sign Out",
            "bvr_cb": {
                'cbjs_action': '''
                 var ok = function(){
                 var server = TacticServerStub.get();
                    var login = spt.Environment.get().get_user();
                    server.execute_cmd("SignOutCmd", {login: login} );
                    //var href = document.location.href;
                    //var parts = href.split("#");
                    //window.location.href=parts[0];
                    document.location = "/";
                    }
                 spt.confirm("Are you sure you wish to sign out?", ok )
                ''' 
            } 
        } )
 

        return { 'menu_tag_suffix': 'MAIN', 'width': 120 , 'opt_spec_list': menu_data, 'allow_icons': False }

    get_smart_menu = classmethod(get_smart_menu)


    def get_js_popup(self):

        # Add in javascript logger console pop-up ...
        # This is particularly useful for being able to print out debug info in javascript when testing
        # and debugging in IE or in FF without Firebug (where console.log is not defined)
        #
        js_popup_id = "WebClientOutputLogPopupWdg"
        js_popup = PopupWdg(id=js_popup_id, allow_page_activity=True, width="630px")

        js_popup.add("TACTIC&trade; Web Client Output Log", "title")

        js_content_div = DivWdg()

        button = ButtonWdg("Clear")
        button.add_style("margin: 5 10")
        button.add_event("onclick", "document.id('spt_js_log_output_div').innerHTML = ''")
        js_content_div.add(button)
        js_content_div.add( HtmlElement.hr() )

        js_div = DivWdg(id="spt_js_log_output_div")
        js_div.add_style("background: #000000")
        js_div.add_style("font-family: Courier, Fixed, serif")
        js_div.add_style("font-size: 11px")
        js_div.add_style("padding: 3px")
        js_div.add_style("color: #929292")
        js_div.add_style("width: 600px")
        js_div.add_style("height: 400px")
        js_div.add_style("overflow: auto")

        # Get user preference for the Web Client Output Console logging level ...
        log_level = PrefSetting.get_value_by_key("js_logging_level")
        if not log_level:
            log_level = "WARNING"  # set js logging level to 'WARNING' as a default!
            PrefSetting.create("js_logging_level",log_level)

        js_div.set_attr("spt_log_level", log_level)
        js_content_div.add( js_div )

        js_popup.add( js_content_div, 'content' )

        return js_popup



class ProjectLoginEditWdg(BaseRefreshWdg):

    def get_display(self):
        from tactic.ui.panel import EditWdg
        from pyasm.security import Sudo

        user = Environment.get_login()
        search_key = user.get_search_key()
        self.kwargs['search_key'] = search_key

        edit = EditWdg(
            search_type="sthpw/login",
            search_key=search_key,
            mode="edit",
        ) 

        sudo = Sudo()
        try:
            edit.get_buffer_display()
        finally:
            sudo.exit()

        return edit


class ProjectSelectWdg(BaseRefreshWdg):


    def get_activator(self, menus):
        from tactic.ui.widget import SingleButtonWdg, IconButtonWdg
        icon = self.kwargs.get("icon")
        if icon:
            button = IconButtonWdg(title='Open Project', icon=icon)
        else:
            button = SingleButtonWdg(title='Open Project', icon="BS_FOLDER_OPEN", show_arrow=True)
        
        smenu_set = SmartMenu.add_smart_menu_set( button, { 'BUTTON_MENU': menus } )
        SmartMenu.assign_as_local_activator( button, "BUTTON_MENU", True )
        
        return button

    def get_projects(self):
        allowed = Project.get_user_projects()
        allowed_codes = [x.get_code() for x in allowed]

        search = Search("sthpw/project")
        search.add_filters("code", allowed_codes)
        # ignore some builtin projects
        search.add_where("\"code\" not in ('admin','sthpw','unittest')")
        search.add_op("begin")
        search.add_filter("is_template", True, op='!=')
        search.add_filter("is_template", 'NULL', quoted=False, op='is')
        search.add_op("or")
        projects = search.get_sobjects()

        return projects


    def get_display(self):
        widget = DivWdg(id='ProjectSelectWdg', css='spt_panel')
        widget.set_attr('spt_class_name', 'tactic.ui.app.ProjectSelectWdg') 

        menus = self._get_project_menus()

        button = self.get_activator(menus)
        widget.add(button)
   
        return widget
   

    def _add_project_menu(self, menu, project, site=None):
        if isinstance(project, dict):
            project_code = project.get("code")
            title = project.get("title")
        else:
            project_code = project.get_value("code")
            title = project.get_value("title")

        menu_item = MenuItem(type='action', label=title)

        web = WebContainer.get_web()
        browser = web.get_browser()
        if not site:
            site = web.get_site_root()
        
        url = "/%s/%s" % (site, project_code)

        if browser != 'Qt':

            menu_item.add_behavior( {
                'type': 'click_up',
                'project_code': project_code,
                'url': url,
                'cbjs_action': '''
                    window.open(bvr.url);
                '''
            } )

        else:
            menu_item.add_behavior( {
                'project_code': project_code,
                'url': url,
                'cbjs_action': '''
                    spt.app_busy.show("Jumping to Project ["+bvr.project_code+"]", "");
                    document.location = bvr.url;
                '''
            } )

        menu.add(menu_item)


    def _get_project_menus(self):
        menus = []
        menu = Menu(width=240)
        menus.append(menu)
        menu.set_allow_icons(False)
        
        
        projects = self.get_projects()

        show_create = self.kwargs.get("show_create")
        if show_create in [False, 'false']:
            show_create = False
        else:
            show_create = True


        security = Environment.get_security()
        if show_create and (security.check_access("builtin", "view_site_admin", "allow", default="deny") or security.check_access("builtin", "create_projects", "allow", default="deny")):
            menu_item = MenuItem(type='title', label='Project Action')
            menu.add(menu_item)

            menu_item = MenuItem(type='action', label='Create New Project')
            menu.add(menu_item)
            menu_item.add_behavior( {
            'cbjs_action': '''
                var env = spt.Environment.get();
                var project = env.get_project();
                if (project == 'admin') {
                    spt.tab.set_main_body_top();
                    var class_name = 'tactic.ui.app.ProjectCreateWdg';
                    spt.tab.add_new("create_project", "Create Project", class_name);
                }
                else {
                    var site = spt.Environment.get().get_site();
                    var url = site ? "/tactic/" + site + "/admin/link/create_project" : "/tactic/admin/link/create_project";
                    document.location = url;
                }
            '''
            } )


            search = Search("config/url")
            search.add_filter("url", "/index")
            url = search.get_sobject()
            if url:
                menu_item = MenuItem(type='action', label='Open Index')
                menu.add(menu_item)
                menu_item.add_behavior( {
                'cbjs_action': '''
                    var env = spt.Environment.get();
                    var project = env.get_project();
                    //document.location = "/tactic/" + project + "/";
                    window.open('/tactic/'+project+'/');
                '''
                } )




        menu_item = MenuItem(type='title', label='Open Project')
        menu.add(menu_item)




        search = Search("sthpw/project")
        search.add_column("category", distinct=True)
        categories = [x.get_value("category") for x in search.get_sobjects() ]
        for category in categories:
            if category == '':
                continue

            # FIXME: a little inefficient, but should be ok for now
            category_projects = []
            for project in projects:
                if project.get_value("category") != category:
                    continue

                project_code = project.get_code()
                key = {'code': project_code}
                if not security.check_access("project", project_code, "view"):
                    continue
                
                category_projects.append(project)

            if category_projects:
                suffix = Common.clean_filesystem_name(category)
                label = "%s (%s)" % (category, len(category_projects))
                menu_item = MenuItem(type='submenu', label=label)
                menu_item.set_submenu_tag_suffix(suffix)
                menu.add(menu_item)

                submenu = Menu(width=200, menu_tag_suffix=suffix)
                menus.append(submenu)
                for project in category_projects:
                    self._add_project_menu(submenu, project)


        from pyasm.security import get_security_version
        security_version = get_security_version()

        for project in projects:
            if project.get_value("category") != "":
                continue

            project_code = project.get_code()
            if security_version >= 2:
                key = { "code": project_code }
                key2 = { "code": "*" }
                keys = [key, key2]
                default = "deny"
                if not security.check_access("project", keys, "allow", default=default):
                    continue
            else:
                if not security.check_access("project", project_code, "view", default="allow"):
                    continue

            self._add_project_menu(menu, project)



        if not projects:
            menu_item = MenuItem(type='action', label="- No Projects Created -")
            menu_item.add_behavior( {
            'cbjs_action': '''
            '''
            } )
            menu.add(menu_item)




        if security.check_access("builtin", "view_site_admin", "allow") or security.check_access("builtin", "view_template_projects", "allow"):
            search = Search("sthpw/project")
            #search.add_filter("is_template", 'true', quoted=False)
            search.add_filter("is_template", True)
            projects = search.get_sobjects()

            if projects:
                menu_item = MenuItem(type='title', label="Template Projects")
                menu.add(menu_item)

           

            for project in projects:
                project_code = project.get_code()
                if security_version >= 2:
                    key = { "code": project_code }
                    key2 = { "code": "*" }
                    keys = [key, key2]
                    default = "deny"
                    if not security.check_access("project", keys, "allow", default=default):
                        continue
                else:
                    if not security.check_access("project", project_code, "view", default="allow"):
                        continue

                menu_item = MenuItem(type='action', label=project.get_value("title"))
                menu_item.add_behavior( {
                'project_code': project_code,
                'cbjs_action': '''
                spt.app_busy.show("Jumping to Project ["+bvr.project_code+"]", "");
                document.location = '/projects/%s/'
                ''' % project_code
                } )
                menu.add(menu_item)


        if security.check_access("builtin", "view_site_admin", "allow", default="deny") or security.check_access("builtin", "create_projects", "allow", default="deny"):
            menu_item = MenuItem(type='title', label="Admin")
            menu.add(menu_item)
            project = Project.get_by_code("admin")
            self._add_project_menu(menu, project)

        return menus






class ProjectCreateWdg(BaseRefreshWdg):

    def get_display(self):
        top = self.top
        self.set_as_panel(top)
        top.add_behavior( {
            'type': 'load',
            'cbjs_action': '''
            spt.named_events.fire_event("side_bar|hide")
            '''
        } )
        top.add_style("width: 100%")
        top.add_color("background", "background", -10)
        top.add_style("padding-top: 10px")
        top.add_style("padding-bottom: 50px")
        top.add_class("spt_project_top")

        inner = DivWdg()
        top.add(inner)
        inner.add_style("width: 80%")
        inner.add_style("max-width: 800px")
        inner.add_style("margin: 10px auto")
        inner.add_style("padding: 30px")
        inner.add_color("color", "color")
        inner.add_color("background", "background")
        inner.add_style("border: solid 1px %s" % inner.get_color("border") )
        inner.add_style("border-radius: 10px")
        inner.add_style("box-shadow: 0px 0px 15px rgba(0,0,0,0.1)")


        from tactic.ui.container import WizardWdg


        title = DivWdg()
        title.add("Create A New Project")

        wizard = WizardWdg(title=title, width="100%")
        inner.add(wizard)


        help_button = ActionButtonWdg(title="?", tip="Create Project Help", size='s', color="secondary")
        title.add(help_button)
        help_button.add_style("float: right")
        help_button.add_style("margin-top: -20px")
        help_button.add_style("margin-right: -10px")
        help_button.add_behavior({
            'type': 'click_up',
            'cbjs_action': '''
            spt.help.set_top();
            spt.help.load_alias("create-new-project");
            '''
        })




        info_page = DivWdg()
        wizard.add(info_page, 'Info')
        info_page.add_class("spt_project_top")
        info_page.add_style("font-size: 12px")
        info_page.add_color("background", "background")
        info_page.add_color("color", "color")
        info_page.add_style("padding: 20px")



        from tactic.ui.input import TextInputWdg

        info_page.add("<b>Project Title:</b> &nbsp;&nbsp;")
    
        text = TextInputWdg(name="project_title")
        text.add_behavior( {
            'type': 'blur',
            'cbjs_action': '''
            if (bvr.src_el.value == '') {
                spt.alert("You must enter a project title");
                return;
            }
        '''})

        #text = TextInputWdg(title="project_title")
        info_page.add(text)
        text.add_style("width: 100%")
        info_page.add(HtmlElement.br(3))
        span = DivWdg()
        info_page.add(span)
        span.add_style("padding: 20px 20px 20px 20px")
        span.add(IconWdg("INFO", "FAR_LIGHTBULB"))
        span.add_color("background", "background3")
        span.add(" The project title can be descriptive and contain spaces and special characters.")
        info_page.add("<br/><br/><br/>")
        text.add_behavior( {
        'type': 'change',
        'cbjs_action': '''
        var title = bvr.src_el.value;
        if (title.length > 100) {
            spt.alert("Title cannot exceed 100 characters.");
            return;
        }
        var code = spt.convert_to_alpha_numeric(title);
        code = code.substring(0,30);
        var top = bvr.src_el.getParent(".spt_project_top");
        var code_el = top.getElement(".spt_project_code");
        code_el.value = code;
        '''
        } )


        info_page.add("<b>Project Code: &nbsp;&nbsp;</b>")
        text = TextInputWdg(name="project_code")
        #text = TextInputWdg(title="project_code")
        text.add_behavior( {
            'type': 'blur',
            'cbjs_action': '''
            var value = bvr.src_el.value;
            var code = spt.convert_to_alpha_numeric(value);
            bvr.src_el.value = code;
            
            if (code == '') {
                spt.alert("You must enter a project code.");
                return;
            }
            if (spt.input.has_special_chars(code)) {
                spt.alert("Project code cannot contain special characters.");
                return;
            }
        
            if (code.test(/^\d/)) {
                spt.alert("Project code cannot start with a number.");
                return;
            }
            if (code.length > 30) {
                 spt.alert("Project code cannot exceed 30 characters.");
                return;
            }
       
            '''
        } )


        info_page.add(text)
        text.add_style("width: 100%")
        text.add_class("spt_project_code")
        info_page.add(HtmlElement.br(4))

        span = DivWdg()
        info_page.add(span)
        span.add_style("padding: 20px 20px 20px 20px")
        span.add(IconWdg("INFO", "FAR_LIGHTBULB"))
        span.add_color("background", "background3")
        span.add(" The project code is a very important key that will tie many components of the project together.")
        span.add("<br/><br/>")
        span.add("* Note: the project code must contain only alphanumeric characters [A-Z]/[0-9] and only an '_' as a separator")
        info_page.add(span)

        info_page.add("<br/>"*2)


        projects = Project.get_all_projects()

        info_page.add("<b>Is Main Project? </b>")

        checkbox = CheckboxWdg("is_main_project")
        checkbox.add_style("height: 16px")
        checkbox.add_style("width: 16px")
        checkbox.add_style("margin-left: 8px")
        default_project_code = Project.get_default_project()
        info_page.add(checkbox)
        if default_project_code:
            default_project = Project.get_by_code(default_project_code)
        else:
            default_project = None

        if default_project:
            default_title = default_project.get_value("title")
            info_span = SpanWdg()
            info_page.add(info_span)
            info_span.add("%sCurrent: %s (%s)" % ("&nbsp;"*3, default_title, default_project_code))
            info_span.add_style("font-size: 0.9em")
            info_span.add_style("font-style: italic")
        else:
            if len(projects) == 0:
                checkbox.set_checked()

        info_page.add("<br/>"*2)

        span = DivWdg()
        info_page.add(span)
        span.add_style("padding: 20px 20px 20px 20px")
        span.add(IconWdg("INFO", "FAR_LIGHTBULB"))
        span.add_color("background", "background3")
        span.add(" A TACTIC installation can have multiple projects, but one can be designated as the main project.  This project will appear at the root of the url. This is meant for building custom project launcher which is based on a main project.")
        span.add("<br/>"*2)
        span.add("* Note: TACTIC may need to be restarted in order for this to take effect")
        info_page.add(span)

        info_page.add("<br/>")









        # add an icon for this project
        image_div = DivWdg()
        wizard.add(image_div, 'Preview Image')
        image_div.add_class("spt_image_top")
        image_div.add_color("background", "background")
        image_div.add_color("color", "color")
        image_div.add_style("padding: 20px")


        image_div.add("<b>Project Image: </b>")
        image_div.add("<br/>"*3)
        on_complete = '''var server = TacticServerStub.get();
        var file = spt.html5upload.get_file(); 
        if (file) { 

            var top = bvr.src_el.getParent(".spt_image_top");
            var text = top.getElement(".spt_image_path");
            var display = top.getElement(".spt_path_display");
            var check_icon = top.getElement(".spt_check_icon");

            var server = TacticServerStub.get();
            var ticket = spt.Environment.get().get_ticket();


            display.innerHTML = "Uploaded: " + file.name;
            display.setStyle("padding", "10px");
            check_icon.setStyle("display", "");
          
          
            var filename = file.name;
            /*filename = spt.path.get_filesystem_name(filename);*/
            var kwargs = {
                ticket: ticket,
                filename: filename
            };
            try {
                var ret_val = server.execute_cmd("tactic.command.CopyFileToAssetTempCmd", kwargs);
                var info = ret_val.info;
                var path = info.web_path;
                text.value = info.lib_path;
                display.innerHTML = display.innerHTML + "<br/><br/><div style='text-align: center'><img style='width: 80px;' src='"+path+"'/></div>";
            }
            catch(e) {
                spt.alert(spt.exception.handler(e));
            }
            spt.app_busy.hide();
            }
        else {
            spt.alert('Error: file object cannot be found.') 
        }
            spt.app_busy.hide();
        '''
        button = UploadButtonWdg(title="Browse", on_complete=on_complete, color="secondary") 
        button.add_style("margin-left: 280px")
        image_div.add(button)


        text = HiddenWdg("project_image_path")
        text.add_class("spt_image_path")
        image_div.add(text)

        check_div = DivWdg()
        image_div.add(check_div)
        check_div.add_class("spt_check_icon")
        check_icon = IconWdg("Image uploaded", "FA_CHECK")
        check_div.add(check_icon)
        check_div.add_style("display: none")
        check_div.add_style("float: left")
        check_div.add_style("padding-top: 8px")

        path_div = DivWdg()
        image_div.add(path_div)
        path_div.add_class("spt_path_display")

        image_div.add(HtmlElement.br(3))
        span = DivWdg()
        image_div.add(span)
        span.add_style("padding: 20px 20px 20px 20px")
        span.add_color("background", "background3")
        span.add(IconWdg("INFO", "FAR_LIGHTBULB"))
        span.add(" The project image is a small image that will be used in various places as a visual representation of this project.")

        info_page.add("<br/><br/>")





        # get all of the template projects that are installed
        copy_div = DivWdg()
        wizard.add(copy_div, "Template")
        copy_div.add_style("padding-top: 20px")





        template = ActionButtonWdg(title="Manage", tip="Manage Templates", color="secondary")
        copy_div.add(template)
        template.add_style("float: right")
        template.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
                var class_name = 'tactic.ui.app.ProjectTemplateWdg'
                spt.panel.load_popup("Templates", class_name)
            '''
        } )




        copy_div.add("<b>Copy From Template: &nbsp;&nbsp;</b>")



        search = Search("sthpw/project")
        search.add_filter("is_template", True)
        template_projects = search.get_sobjects()
        values = [x.get_value("code") for x in template_projects]
        labels = [x.get_value("title") for x in template_projects]


        # find all of the template projects installed
        template_dir = Environment.get_template_dir()
        import os
        if not os.path.exists(template_dir):
            paths = []
        else:
            paths = os.listdir(template_dir);


            file_values = []
            file_labels = []
            for path in paths:
                if path.endswith("zip"):
                    orig_path = '%s/%s'%(template_dir, path)
                    path = path.replace(".zip", "")
                    parts = path.split("-")
                    plugin_code = parts[0]

                    # skip if there is a matching project in the database
                    #match_project = plugin_code.replace("_template", "")
                    
                    match_project = plugin_code
                    old_style_plugin_code = re.sub( '_template$', '', plugin_code)

                    if match_project in values:
                        continue
                    elif old_style_plugin_code in values:
                        continue

                    label = "%s (from file)" % Common.get_display_title(match_project)

                    # for zip file, we want the path as well
                    value = '%s|%s'%(plugin_code, orig_path)
                    file_values.append(value)
                    file_labels.append(label)

            if file_values:
                values.extend(file_values)
                labels.extend(file_labels)


        values.insert(0, "_empty")
        labels.insert(0, "- Empty Project -")

        select = SelectWdg("project_source")
        copy_div.add(select)
        select.set_option("values", values)
        select.set_option("labels", labels)
        #select.add_empty_option("-- Select --")

        select.add_behavior( {
        'type': 'change',
        'cbjs_action': '''
        var value = bvr.src_el.value;
        var top = bvr.src_el.getParent(".spt_project_top");
        var type = top.getElement(".spt_custom_project_top");
        var namespace_option = top.getElement(".spt_custom_namespace_top");

        var theme_el = top.getElement(".spt_theme_top");

        if (bvr.src_el.value == "_empty") {
            spt.show(type);
            spt.show(namespace_option);

            spt.show(theme_el);

        }
        else {
            spt.hide(type);
            spt.hide(namespace_option);

            spt.hide(theme_el);
        }
        '''
        } )



        copy_div.add(HtmlElement.br(3))
        span = DivWdg()
        copy_div.add(span)
        span.add_style("padding: 20px 20px 20px 20px")
        span.add(IconWdg("INFO", "FAR_LIGHTBULB"))
        span.add_color("background", "background3")
        span.add(" This will use the selected project template as a basis and copy all of the configuration elements.  Only template projects should be copied.")

        #copy_div.add(HtmlElement.br(2))
        #span = DivWdg("This will create an empty project with no predefined configuration.")
        #copy_div.add(span)

        #
        # Theme
        #
        theme_div = DivWdg()
        theme_div.add_class("spt_theme_top")
        theme_div.add_style("padding: 10px")
        theme_div.add_style("margin-top: 20px")
        copy_div.add(theme_div)
        theme_div.add("<b>Theme: </b>&nbsp; ")
        theme_div.add_style('padding-right: 6px')

        theme_select = SelectWdg('project_theme')
        theme_div.add(theme_select)



        # look in the plugins for all of the themes?
        from pyasm.biz import PluginUtil
        plugin_util = PluginUtil()
        data = plugin_util.get_plugins_data("theme")

        builtin_dir = Environment.get_builtin_plugin_dir()
        plugin_util = PluginUtil(base_dir=builtin_dir)

        data2 = plugin_util.get_plugins_data("theme")

       
        data = dict(list(data.items()) + list(data2.items()))

        themes = list(data.keys())
        themes.sort()




        theme_select.set_option("values", themes)
        theme_select.add_empty_option('- No Theme -')
        default_theme = "TACTIC/default_theme"
        theme_select.set_value(default_theme)

        theme_select.add_behavior( {
            'type': 'change',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_project_top");
            var img_div = top.getElement(".spt_project_theme_div");
            var theme = bvr.src_el.value;

            var img_els = img_div.getElements(".spt_project_theme_image");
            for (var i = 0; i < img_els.length; i++) {
                if (theme == img_els[i].getAttribute("spt_theme") ) {
                    img_els[i].setStyle("display", "");
                }
                else {
                    img_els[i].setStyle("display", "none");
                }
            }
            '''
        } )

        theme_img_div = DivWdg()
        theme_div.add(theme_img_div)
        theme_img_div.add_class("spt_project_theme_div")

        for theme in themes:
            theme_item = DivWdg()
            theme_item.add_style("margin: 15px")
            theme_img_div.add(theme_item)
            theme_item.add_attr("spt_theme", theme)
            theme_item.add_class("spt_project_theme_image")
            if theme != default_theme:
                theme_item.add_style("display: none")

            table = Table()
            theme_item.add(table)
            table.add_row()

            if Environment.is_builtin_plugin(theme):
                theme_img = HtmlElement.img(src="/tactic/builtin_plugins/%s/media/screenshot.jpg" % theme)
            else:
                theme_img = HtmlElement.img(src="/tactic/plugins/%s/media/screenshot.jpg" % theme)
            theme_img.add_border()
            theme_img.set_box_shadow("1px 1px 1px 1px")
            theme_img.add_style("margin: 20px 10px")
            theme_img.add_style("width: 240px")

            plugin_data = data.get(theme)

            description = plugin_data.get("description")
            if not description:
                description = "No Description"

            table.add_cell(theme_img)
            table.add_cell( description )



        theme_img_div.add_style("text-align: center")
        theme_img_div.add_style("margin: 10px")

 

        #
        # namespace
        #
        ns_div = DivWdg()
        ns_div.add_class("spt_custom_namespace_top")
        ns_div.add_style("padding: 10px")
        copy_div.add(ns_div)
        ns_div.add("<br/>")
        ns = HtmlElement.b("Namespace:")
        ns.add_style('padding-right: 6px')
        ns_div.add(ns)

        text = TextWdg('custom_namespace')
        text.add_class("spt_custom_namespace")
        text.add_behavior( {
            'type': 'blur',
            'cbjs_action': '''
                 var project_namespace = bvr.src_el.value;
                 if (['sthpw','prod'].contains(project_namespace)) 
                    spt.alert('Namespace [' + project_namespace + '] is reserved.');

                 if (project_namespace.strip()=='') 
                    spt.alert('A "default" namespace will be used if you leave it empty.');
            
            '''})

        ns_div.add(text)

        hint = HintWdg('This will be used as the prefix for your sTypes. You can use your company name for instance')
        ns_div.add(hint)

        # is_template
        is_template_div = DivWdg()
        #is_template_div.add_style('display: none')

        is_template_div.add_class("spt_custom_project_top")
        is_template_div.add_style("padding: 10px")
        copy_div.add(is_template_div)
        is_template_div.add("<br/>")
        is_template_div.add("<b>Is this project a template: </b>")

        text = CheckboxWdg("custom_is_template")
        text.add_class("spt_custom_is_template")
        is_template_div.add(text)

        is_template_div.add(HtmlElement.br(2))
        span = DivWdg("Template projects are used as a blueprint for generating new projects.")
        is_template_div.add(span)



        # Disabling for now ... advanced feature and may not be necessary
        #stypes_div = self.get_stypes_div()
        #is_template_div.add(stypes_div)








        last_page = DivWdg()
        wizard.add(last_page, "Complete")

        last_page.add_style("padding-top: 80px")
        last_page.add_style("padding-left: 30px")

        item = DivWdg()
        last_page.add(item)
        cb = RadioWdg('jump_project', label='Jump to New Project')
        cb.set_option("value", "project")
        #cb.set_option('disabled','disabled')
        cb.add_style("height: 18px")
        cb.add_style("width: 18px")
        cb.add_style("margin-right: 5px")
        item.add(cb)
        item.add_style("display: flex")
        item.add_style("align-items: center")




        last_page.add(HtmlElement.br(2))

        item = DivWdg()
        last_page.add(item)
        cb = RadioWdg('jump_project', label='Jump to Project Admin')
        cb.set_option("value", "admin")
        cb.add_class("form-control")
        cb.add_style("height: 18px")
        cb.add_style("width: 18px")
        cb.add_style("margin-right: 5px")
        item.add(cb)
        item.add_style("display: flex")
        item.add_style("align-items: center")


        last_page.add(HtmlElement.br(2))

        item = DivWdg()
        last_page.add(item)
        cb = RadioWdg('jump_project', label='Create Another Project')
        cb.set_option("value", "new")
        cb.add_class("form-control")
        cb.add_style("height: 18px")
        cb.add_style("width: 18px")
        cb.add_style("margin-right: 5px")
        item.add(cb)
        item.add_style("display: flex")
        item.add_style("align-items: center")





        last_page.add(HtmlElement.br(5))


        button_div = DivWdg()

        create_button = ActionButtonWdg(title="Create >>", tip="Create new project")
        wizard.add_submit_button(create_button)
        #button_div.add(create_button)
        create_button.add_style("float: right")

        create_button.add_behavior({
        'type': "click_up",
        'cbjs_action': '''
        var top = bvr.src_el.getParent(".spt_project_top");
        var values = spt.api.Utility.get_input_values(top, null, null, null, {cb_boolean: true});

        var project_code = values['project_code'][0];
        if (project_code == '') {
            spt.alert("You must enter a project code.");
            return;
        }
        if (spt.input.has_special_chars(project_code)) {
            spt.alert("Project code cannot contain special characters.");
            return;
        }
        
        if (project_code.test(/^\d/)) {
            spt.alert("Project code cannot start with a number.");
            return;
        }
        if (values['project_title'] == '') {
            spt.alert("You must enter a project title");
            return;
        }

        var project_source = values.project_source[0];

        var project_image_path = values['project_image_path'][0];

        var project_theme = values['project_theme'][0];

        var options = {
            'project_code': project_code,
            'project_title': values['project_title'][0],
            'project_image_path': project_image_path,
            'project_theme': project_theme,
        }

        //'copy_pipelines': values['copy_pipelines'][0]

        var class_name;
        var busy_title;
        var busy_msg;
        var use_transaction;
        if (project_source == '') {
            spt.alert("Please select a template to copy or select create an empty project");
            return;
        }
        else if (project_source != '_empty') {
            busy_title = "Copying Project"; 
            busy_msg = "Copying project ["+project_source+"] ...";
            use_transaction = false;

            class_name = 'tactic.command.ProjectTemplateInstallerCmd';
            if (project_source.test(/\|/)) {
                var tmps = project_source.split('|');
                project_source = tmps[0];
                var path = tmps[1];
                options['path'] = path;
            }
            options['template_code'] = project_source;
            options['force_database'] = true;

        }
        else {
            class_name = "tactic.command.CreateProjectCmd";
            busy_title = "Creating New Project"; 
            busy_msg = "Creating new project based on project info ...";
            use_transaction = true;

            // use project code as the project type if namespace is not specified
            var project_namespace = values['custom_namespace'][0];
            if (['sthpw','prod'].contains(project_namespace)) {
                spt.alert('Namespace [' + project_namespace + '] is reserved.');
                return;
            }
            options['project_type'] =  project_namespace ? project_namespace : project_code
            var is_template = values['custom_is_template'];
            if (is_template) {
                options['is_template'] = is_template[0];
            }
            // This has been commented out in the UI
            //options['project_stype'] = values['project_stype'].slice(1);


            var is_main_project = values['is_main_project'];
            if (is_main_project) {
                options['is_main_project'] = is_main_project[0];
            }

        }

        // Display app busy pop-up until create project command
        // has completed executing.
        spt.app_busy.show( busy_title, busy_msg ); 

        setTimeout( function() {

            var ret_val = '';
            var server = TacticServerStub.get();
            try {
                ret_val = server.execute_cmd(class_name, options, {}, {use_transaction: true});
            }
            catch(e) {
                spt.app_busy.hide();
                spt.alert("Error: " + spt.exception.handler(e));
                return;
                throw(e);
            }
            spt.api.Utility.clear_inputs(top);

            var env = spt.Environment.get();
            var site = env.get_site();
            if (site) {
                site = site + "/";
            }
            else {
                site = "";
            }


            // show feedback at the end
            var jump = values['jump_project'][0];
            if (jump == 'project' || jump == 'admin') {
                var location;
                if (jump == 'admin') {
                    location = "/tactic/" + site + project_code + "/admin";
                }
                else if (project_theme) {
                    location = "/tactic/" + site + project_code + "/";
                }
                else {
                    location = "/tactic/" + site + project_code + "/admin/link/_startup";
                }
                setTimeout( function() {
                    document.location = location;
                    }, 1000);
            }
            else { 
                // Refresh header
                spt.panel.refresh(top);
                setTimeout( function() {
                    spt.panel.refresh('ProjectSelectWdg');
                }, 2800);


                spt.app_busy.hide();
            }

            // don't hide because it gives the false impression that nothing
            // happened as it waits for the timeout
            //spt.app_busy.hide();
        }, 0 );

        '''


        })


        cancel_script = self.kwargs.get("cancel_script")
        if cancel_script:
            cancel_button = ActionButtonWdg(title="Cancel")
            cancel_button.add_style("float: left")

            cancel_button.add_behavior({
                'type': "click_up",
                'cbjs_action': cancel_script
            })

            button_div.add(cancel_button)

            create_button.add_style("margin-right: 15px")
            create_button.add_style("margin-left: 75px")


        button_div.add("<br clear='all'/>")

        last_page.add(button_div)


        inner.add(HtmlElement.br())
   
        return top


    def get_stypes_div(self):
        div = DivWdg()
        #div.add("<hr/>")
        div.add_style("margin-top: 15px")

        title_div = DivWdg()
        title_div.add("<b>Add Custom Types</b>")
        div.add(title_div)
        title_div.add_style("margin-bottom: 10px")

        div.add("A project will manage one or more types of assets (Searchable Types or sTypes).  Here, extra custom sTypes, such as Shots, Assets, Artwork, etc. can be quickly defined that will be added to the new project. You can add more later in the Schema Editor.<br/>")
        from tactic.ui.container import DynamicListWdg
        dynlist_wdg = DynamicListWdg()
        div.add(dynlist_wdg)

        template_div = DivWdg()
        template_div.add_style("margin-top: 5px")
        template_div.add_style("margin-left: 10px")
        template_div.add("Type: ")
        text = TextWdg("project_stype")
        template_div.add(text)

        dynlist_wdg.add_template(template_div)

        first_div = DivWdg()
        first_div.add_style("margin-top: 5px")
        first_div.add_style("margin-left: 10px")
        first_div.add("Type: ")
        text = TextWdg("project_stype")
        first_div.add(text)
        dynlist_wdg.add_item(first_div)


        return div




class AppBusyWdg(BaseRefreshWdg):

    def get_display(self):

        div = DivWdg()
        div.add_class( "SPT_PUW" )
        div.add_styles( "display: none; position: absolute; z-index: 1000" )
        div.set_attr("id","app_busy_msg_block")

        rc_div = DivWdg()
        rc_div.add_style("width: 350px")
        rc_div.add_style("height: 70px")
        rc_div.add_gradient("background", "background3", -30, range=-20)
        rc_div.add_color("color", "color3")
        rc_div.add_style("padding: 10px")
        rc_div.set_round_corners(10)

        # get a subdued glow effect or shadow , depending on the background
        rc_div.set_box_shadow()
        rc_div.add_border(modifier=-10)
        div.add( rc_div )


        # close button
        close_wdg = SpanWdg()
        icon = IconWdg("Close", IconWdg.DIALOG_CLOSE)
        close_wdg.add( icon )
        close_wdg.add_style("float: right")
        close_wdg.add_class("hand")

        close_wdg.add_behavior({
            'type': 'click',
            'cbjs_action': '''
            spt.app_busy.hide();
            '''
        })

        rc_div.add(close_wdg)

        spinner_img = HtmlElement.img()
        spinner_img.set_attr("src","/context/icons/common/app_busy_spinner.gif")
        spinner_img.add_styles("text-decoration: none; padding: none; margin: none; float: left;")

        rc_div.add(spinner_img)
        rc_div.add_style( "color: #FFF")

        title_span = SpanWdg()
        title_span.add_class("spt_app_busy_title")
        title_span.add_style("margin-left: 15px")
        title_span.add_style("font-size: 14px")
        title_span.add("--Add Title--")
        rc_div.add(title_span)

        rc_div.add( "<br/>" )

        msg_span = SpanWdg()
        msg_span.add_class("spt_app_busy_msg")
        msg_span.add_styles("margin-left: 15px;")
        msg_span.add("... add message ...")
        rc_div.add(msg_span)

        return div



class PasswordEditWdg(BaseRefreshWdg):

    PASSWORD = 'password'
    OLD_PASSWORD = 'old password'    

    def get_display(self):

        div = DivWdg(id='password_edit')
        self.set_as_panel(div)

        div.add_style("padding: 10px")
        div.add_border()
        div.add_color("color", "color")
        div.add_color("background", "background")
        div.add_style("width: 400px")

        table = Table()
        table.add_color("color", "color")

        table.set_max_width()
        #table.add_class('collapse')
        #table.set_style("margin: auto; margin-top: 40px")
        
        table.add_row()
        td = table.add_cell( "Old Password:" )
        td.add_style('padding-left: 30px')
        password = PasswordWdg(self.OLD_PASSWORD)
        table.add_cell( password )
        table.add_row()
        td = table.add_cell( "New Password:" )
        td.add_style('padding-left: 30px')
        password = PasswordWdg(self.PASSWORD)
        table.add_cell( password )
        table.add_row()
        td = table.add_cell( "Re-enter Password:" )
        td.add_style('padding-left: 30px')

        table.add_cell( PasswordWdg("password re-enter") )
        table.add_row()
        table.add_blank_cell()
        
        table.add_row()
        button = TextBtnWdg(label="OK", size='small', horiz_align='center')

        login = Environment.get_security().get_login()
        button.add_behavior({'type': 'click_up', 
            'cbjs_action': '''try {
            var ret_val = TacticServerCmd.execute_cmd('PasswordEditCmd','password_edit', {'search_key': '%s'});
            var div = spt.get_cousin(bvr.src_el, '.spt_popup', '.spt_cmd_response');
            div.innerHTML = ret_val['description'];

            setTimeout(function(){ spt.popup.close(bvr.src_el.getParent('.spt_popup'));}, 2500);
            }
            catch(e) {
                spt.alert('Error: ' + spt.exception.handler(e));
            }

            ''' % SearchKey.get_by_sobject(login),
            }) 
        td = table.add_cell( button )
        #td.add_class('center_content')
        td.set_attr('colspan','2')

        div.add(table)
        response_div = DivWdg(css='spt_cmd_response center_content')
        response_div.add_style('color','#F0C956') 
        div.add(response_div)
        return div


