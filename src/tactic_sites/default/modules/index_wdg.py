#############################################################
#
#    Copyright (c) 2005, Southpaw Technology
#                        All Rights Reserved
#
#    PROPRIETARY INFORMATION.  This software is proprietary to
#    Southpaw Technology, and is not to be reproduced, transmitted,
#    or disclosed in any way without written permission.
#
#
#

__all__ = ['IndexWdg', 'IndexWdg2']

from pyasm.common import Environment, Config, Common, Container
from pyasm.search import Search
from pyasm.web import Widget, Table, DivWdg, HtmlElement, WebContainer, BaseAppServer
from pyasm.widget import TableWdg, ThumbWdg, TacticLogoWdg

from tactic.ui.widget import ActionButtonWdg

import os


class IndexWdg(Widget):
    def get_display(my):
        div = DivWdg()
        class_path = Common.get_full_class_name(my)

        from tactic.ui.panel import HashPanelWdg
        try:
            widget = HashPanelWdg.get_widget_from_hash("/index", return_none=True)
            div.add(widget)
        except:
            widget = None


        if not widget:
            class_path = class_path.replace("IndexWdg", "IndexWdg2")
            kwargs = {}
            div.add_behavior( {
                'type': 'load',
                'class_path': class_path,
                'kwargs': kwargs,
                'cbjs_action': 'spt.panel.load(bvr.src_el, bvr.class_path, bvr.kwargs)'
            } )
        return div



class IndexWdg2(Widget):
    def get_display(my):


        web = WebContainer.get_web()
        palette = web.get_palette()

        widget = DivWdg()
        widget.add_style("width: 100%")
        widget.add_style("text-align: center")

        from tactic.ui.app import PageHeaderWdg
        header = PageHeaderWdg(show_project=False)
        widget.add( header )

        security = Environment.get_security()


        search = Search("sthpw/project")
        search.add_where("\"code\" not in ('sthpw', 'admin', 'unittest')")
        search.add_where("\"type\" not in ('resource')")
        # hide template projects
        if security.check_access("builtin", "view_site_admin", "allow") or security.check_access("builtin", "view_template_projects", "allow"):
            pass
        else:
            search.add_op("begin")
            search.add_filter("is_template", True, op='!=')
            search.add_filter("is_template", 'NULL', quoted=False, op='is')
            search.add_op("or")

        search.add_order_by("category")

        projects = search.get_sobjects()
        
        num = len(projects)
        # sort by project
        if num < 5:
            columns = 1
            icon_size = 90
            width = 500
        elif num < 15:
            columns = 2
            icon_size = 60
            width = 700
        else:
            columns = 3
            icon_size = 45
            width = 800

        div = DivWdg()

        div.add_style("margin-left: auto")
        div.add_style("margin-right: auto")
        #div.add_style("width: 520px")
        div.center()
        widget.add(div)

        #logo = TacticLogoWdg()
        #div.add(logo)
        div.add("<br/>"*3)

        bg_color = palette.color("background")
        #div.add_color("color", "color")

        from tactic.ui.container import RoundedCornerDivWdg
        div = RoundedCornerDivWdg(hex_color_code=bg_color,corner_size="10")
        div.set_dimensions( width_str='%spx' % width, content_height_str='50px' )
        div.add_border()
        div.add_style("overflow: hidden")
        div.set_box_shadow()

        div.add_style("margin-left: auto")
        div.add_style("margin-right: auto")
        div.add_style("width: %spx" % width)
        table = Table()
        table.set_max_width()
        table.add_style("margin-left: auto")
        table.add_style("margin-right: auto")
        table.add_style("background-color: %s" % bg_color)
        table.add_color("color", "color")

        tr, td = table.add_row_cell()
        logo_div = DivWdg()
        logo_div.add_gradient("background", "background3", -5, -10)
        td.add(logo_div)
        logo = TacticLogoWdg()
        logo_div.add(logo)
        logo_div.add_style("margin: -6 -6 6 -6")


        app_name = WebContainer.get_web().get_app_name()
        security = Environment.get_security() 

        last_category = None
        has_category = False
        index = 0 

        # if TACTIC has not been set up, show the configuration page
        # FIXME: what is the requirement for is_installed?
        config_path = Config.get_config_path()
        if not os.path.exists(config_path):
            is_installed = False
        else:
            is_installed = True
        #is_installed = True



        # filter out projects due to security
        filtered = []
        for i, project in enumerate(projects):

            from pyasm.security import get_security_version
            security_version = get_security_version()
            if security_version >= 2:
                key = { "code": project.get_code() }
                key2 = { "code": "*" }
                keys = [key, key2]
                default = "deny"
                if not security.check_access("project", keys, "allow", default=default):
                    continue
            else:

                if not security.check_access("project", project.get_code(), "view", default="allow"):
                    continue

            filtered.append(project)

        projects = filtered





        if not is_installed:
            tr, td = table.add_row_cell()

            #from tactic.ui.startup import DbConfigWdg
            #td.add(DbConfigWdg())

            title_div = DivWdg()
            td.add(title_div)
            title_div.add_style("padding: 5px")
            title_div.add_style("font-weight: bold")
            title_div.add("Getting Started ...")
            title_div.add_gradient("background", "background", -10)

            projects_div = DivWdg()
            projects_div.add_style("padding: 20px")
            td.add(projects_div)
            projects_div.add_style("text-align: center")
            projects_div.add("Welcome to TACTIC ...<br/>")
            projects_div.add_style("font-size: 22px")


            msg_div = DivWdg()
            td.add(msg_div)
            msg_div.add("Configure TACTIC to connect to an external database and set up asset folders.<br/><br/>")
            msg_div.add_style("text-align: center")


            action = ActionButtonWdg(title='Confgure', size='medium')
            action.add_style("margin-left: auto")
            action.add_style("margin-right: auto")
            td.add(action)
            action.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            document.location = "/tactic/admin/#/link/configure";
            '''
            } )


            msg_div = DivWdg()
            td.add(msg_div)
            msg_div.add("<br/><br/>Or start using TACTIC with default configuration with an internal database.<br/><br/>")

            msg_div.add_style("text-align: center")
            action = ActionButtonWdg(title='Start >>', size='medium')
            action.add_style("margin-left: auto")
            action.add_style("margin-right: auto")
            td.add(action)
            action.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            document.location = "/tactic";
            '''
            } )


            msg_div = DivWdg()
            td.add(msg_div)
            msg_div.add("<br/><br/><br/>")
            msg_div.add_style("text-align: center")



        elif projects:
            num_projets = 0
            for i, project in enumerate(projects):

                category = project.get_value("category")
                if category is not None and category != last_category:

                    table.add_row()
                    tr, td = table.add_row_cell()
                    category_div = DivWdg()
                    td.add(category_div)
                    if has_category and not category:
                        category_div.add("&nbsp;")
                    else:
                        category_div.add(category)
                    category_div.add_style("padding: 8px")
                    category_div.add_style("font-size: 16px")
                    category_div.add_style("font-weight: bold")
                    category_div.add_color("color", "color")
                    category_div.add_gradient("background", "background3",0, -10)
                    category_div.add_color("color", "color3")
                    #category_div.set_round_corners()
                    if last_category == None:
                        category_div.add_style("margin: -6 -6 6 -6")
                    else:
                        category_div.add_style("margin: 15 -6 0 -6")
                    table.add_row()
                    has_category = True
                    index = 0

                index += 1
                last_category = category


                thumb = ThumbWdg()
                thumb.set_name("snapshot")
                thumb.set_sobject(project)
                thumb.set_show_clipboard(False)
                thumb.set_has_img_link(False)
                thumb.set_icon_size(icon_size)
             
                code = project.get_code()
                title = project.get_value("title")
                # Restrict the length of project name
                if len(title) >= 36:
                    title = title[:36] + "..."
                if app_name != 'Browser':
                    href = HtmlElement.href(HtmlElement.h2(title), ref='/tactic/%s/%s'\
                        %(code, app_name))
                    img_href = HtmlElement.href(thumb, ref='/tactic/%s/%s'\
                        %(code, app_name))

                    link = '/tactic/%s/%s' % (code, app_name)
                else:
                    href = HtmlElement.href(HtmlElement.h2(title), ref="/tactic/%s/" % code)
                    img_href = DivWdg(thumb)
                    img_href.add_behavior( {
                        'type': 'click_up',
                        'code': code,
                        'cbjs_action': '''
                        document.location = '/tactic/'+bvr.code+'/';
                        '''
                    } )
                
                    link = '/tactic/%s/' % code

                href = href.get_buffer_display()
                if (index-1) % columns == 0:
                    table.add_row()
               
                td = table.add_cell()
                img_div = DivWdg()
                img_div.add(img_href)
                img_div.add_style("margin-right: 20px")
                img_div.add_style("float: left")
                img_div.add_border()
                #img_div.set_round_corners()
                img_div.set_box_shadow("0px 1px 5px")

                project_div = DivWdg()
                td.add(project_div)
                td.add_style("width: 230px")
                project_div.add_style("font-size: 16px")
                project_div.add_style("font-weight: bold")
                project_div.add_style("vertical-align: middle")
                project_div.add(img_div)
                #project_div.add(href)
                project_div.add(title)
                if project.get_value("is_template") == True:
                    project_div.add("<br/><i style='opacity: 0.5; font-size: 12px'>(template)</i>")
                project_div.add_style("height: %spx" % (icon_size-10))

                project_div.add_style("padding: 8px 10px 2px 20px")
                
                project_div.add_color("background", "background")
                project_div.add_behavior( {
                'type': 'hover',
                'add_color_modifier': -3,
                'cb_set_prefix': 'spt.mouse.table_layout_hover',
                } )
                project_div.set_round_corners()
                project_div.add_class("hand")

                project_div.add_behavior( {
                'type': 'click_up',
                'link': link,
                'title': title,
                'cbjs_action': '''
                document.location = bvr.link;
                '''
                } )

        elif not security.check_access("builtin", "view_site_admin", "allow", default="deny") and not security.check_access("builtin", "create_projects", "allow", default="deny"):
            tr, td = table.add_row_cell()

            msg_div = DivWdg()
            td.add(msg_div)
            from pyasm.widget import IconWdg
            icon = IconWdg("WARNING", IconWdg.WARNING)
            msg_div.add(icon)
            msg_div.add("You are not permitted to view any projects")
            msg_div.add_style("font-size: 16px")
            msg_div.add_style("text-align: center")
            msg_div.add_style("font-weight: bold")
            msg_div.add_style("margin: 50px")
            msg_div.add("<br/>"*2)
            msg_div.add("Please click to Sign Out:<br/>")
            action = ActionButtonWdg(title='Sign Out >>', size='m')
            msg_div.add(action)
            action.add_style('margin: 5px auto')
            action.add_style('text-align: center')
            web = WebContainer.get_web()
            action.add_behavior( {
                'type': 'click_up',
                'login': web.get_user_name(),
                'cbjs_action': '''
                var server = TacticServerStub.get();
                server.execute_cmd("SignOutCmd", {login: bvr.login} );
                window.location.href='/';
                '''
            } )

        else:
            tr, td = table.add_row_cell()

            title_div = DivWdg()
            td.add(title_div)
            title_div.add_style("padding: 10px")
            title_div.add_style("margin: -8px -6px 20px -6px")
            title_div.add_style("font-weight: bold")
            title_div.add("Getting Started ...")
            title_div.add_gradient("background", "background", -10)

            projects_div = DivWdg()
            projects_div.add_style("padding: 20px")
            td.add(projects_div)
            projects_div.add_style("text-align: center")
            projects_div.add("No Projects have been created ...<br/><br/>")
            projects_div.add_style("font-size: 22px")

            action = ActionButtonWdg(title='Create Project >>', size='large')
            action.add_style("margin-left: auto")
            action.add_style("margin-right: auto")
            projects_div.add(action)
            action.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            document.location = "/tactic/admin/link/create_project";
            '''
            } )


        if security.check_access("builtin", "view_site_admin", "allow"):
            admin_div = DivWdg()
            #href = HtmlElement.href(HtmlElement.h2('Admin Site'), ref='/tactic/admin/')
            #admin_div.add(href)
            #admin_div.add_border()
            admin_div.add_style("font-size: 16px")
            admin_div.add_style("font-weight: bold")
            admin_div.add_style("height: 30px")

            link_div = DivWdg()
            link_div.add_class("hand")
            admin_div.add(link_div)
            link_div.add("Go to Admin Site")
            link_div.add_style("text-align: center")
            link_div.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            document.location = '/tactic/admin/';
            '''
            } )
            tr, td = table.add_row_cell()
            td.add("<hr/><br/>")
            td.add(admin_div)


        div.add(table)
        widget.add(div)
        # Note sure what this is for
        #BaseAppServer.add_onload_script('spt.first_load=false')
        div.add_behavior( {
            'type': 'load',
            'cbjs_action': '''spt.first_load=false'''
        } )
        return widget


