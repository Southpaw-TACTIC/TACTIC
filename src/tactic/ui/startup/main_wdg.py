###########################################################
#
# Copyright (c) 2010, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#

__all__ = ['MainWdg']

from pyasm.common import Environment, Common
from pyasm.search import Search
from pyasm.biz import Project
from pyasm.web import DivWdg, HtmlElement, SpanWdg, Table, Widget
from pyasm.widget import IconWdg, TextWdg

import os

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.widget import ActionButtonWdg, IconButtonWdg
from tactic.ui.app import SearchWdg

class MainWdg(BaseRefreshWdg):
    '''This is the welcome widget widget will appear on creation of a new
    project
    '''

    def get_args_keys(my):
        return {
        }

    def init(my):
        # clear the widget settings of last_search:sthpw/sobject_list
        SearchWdg.clear_search_data('sthpw/sobject_list')

    def get_main_section_wdg(my, title, description, image, behavior):

        section_wdg = DivWdg()
        section_wdg.set_round_corners()
        section_wdg.add_border()
        section_wdg.add_style("width: 225px")
        section_wdg.add_style("height: 180px")
        section_wdg.add_style("overflow: hidden")
        section_wdg.add_style("margin: 10px")
        section_wdg.set_box_shadow()

        title_wdg = DivWdg()
        section_wdg.add(title_wdg)
        title_wdg.add(title)
        title_wdg.add_style("height: 20px")
        title_wdg.add_style("padding: 3px")
        title_wdg.add_style("margin-top: 3px")
        title_wdg.add_style("font-weight: bold")
        title_wdg.add_style("text-align: center")
        title_wdg.add_gradient("background", "background")

        section_wdg.add_color("background", "background")
        section_wdg.add_behavior( {
        'type': 'hover',
        'add_color_modifier': -3,
        'cb_set_prefix': 'spt.mouse.table_layout_hover',
        } )

        shadow = section_wdg.get_color("shadow")

        section_wdg.add_behavior( {
        'type': 'click',
        'shadow': shadow,
        'cbjs_action': '''
        bvr.src_el.setStyle("box-shadow", "0px 0px 5px " + bvr.shadow);
        '''
        } )
        section_wdg.add_behavior( {
        'type': 'mouseout',
        'shadow': shadow,
        'cbjs_action': '''
        bvr.src_el.setStyle("box-shadow", "0px 0px 15px " + bvr.shadow);
        ''',
        } )





        desc_div = DivWdg()
        desc_div.add(description)
        desc_div.add_style("padding: 5px 10px 10px 10px")
        #desc_div.add_style("font-size: 1.5em")
	#desc_div.add_style("font-weight: bold")	

        div = DivWdg()
        section_wdg.add(div)
        div.add_style("padding: 3px")
        div.add_style("margin: 10px")
        div.add_style("width: 209px")
        div.add_style("height: 64px")
	div.add_style("text-align: center")
        div.add(image)
	#div.set_box_shadow("1px 1px 1px 1px")
        section_wdg.add(desc_div)
        div.add_style("overflow: hidden")

        section_wdg.add_behavior( behavior )
        section_wdg.add_class("hand")

        return section_wdg


    def get_small_section_wdg(my, title, description, image, behavior):

        section_wdg = DivWdg()
        section_wdg.set_round_corners()
        section_wdg.add_border()
        section_wdg.add_style("width: 225px")
        section_wdg.add_style("height: 100px")
        section_wdg.add_style("overflow: hidden")
        section_wdg.add_style("margin: 10px")
        section_wdg.set_box_shadow("0px 0px 5px")

        title_wdg = DivWdg()
        section_wdg.add(title_wdg)
        title_wdg.add(title)
        title_wdg.add_style("height: 20px")
        title_wdg.add_style("padding: 3px")
        title_wdg.add_style("margin-top: 3px")
        title_wdg.add_style("font-weight: bold")
        title_wdg.add_gradient("background", "background")

        section_wdg.add_color("background", "background")
        #section_wdg.add_gradient("background", "background", 0, -3)
        section_wdg.add_behavior( {
        'type': 'hover',
        'add_color_modifier': -5,
        'cb_set_prefix': 'spt.mouse.table_layout_hover',
        } )

        desc_div = DivWdg()
        desc_div.add(description)
        desc_div.add_style("padding: 5px 10px 10px 5px")


        div = DivWdg()
        section_wdg.add(div)
        div.add_style("padding: 5px")
        div.add_style("margin: 5px")
        div.add_style("width: 65px")
        div.add_style("height: 50px")
        div.add_style("float: left")
	div.add_style("text-align: center")
        div.add(image)
        section_wdg.add(desc_div)
        div.add_style("overflow: hidden")

        section_wdg.add_behavior( behavior )
        section_wdg.add_class("hand")

        return section_wdg



    def get_display(my):

        top = DivWdg()
        top.add_border()
        top.add_style("padding: 10px")
        top.add_color("color", "color")
        top.add_gradient("background", "background", 0, -5)
        #top.add_style("height: 550px")

        top.add_behavior( {
            'type': 'load',
            'cbjs_action': '''
            spt.named_events.fire_event("side_bar|hide_now", {} );
            '''
        } )


        project = Project.get()
        title = DivWdg()
        title.add("Project Startup and Configuration")
        title.add_style("font-size: 18px")
        title.add_style("font-weight: bold")
        title.add_style("text-align: center")
        title.add_style("padding: 10px")
        title.add_style("margin: -10px -10px 10px -10px")

        top.add(title)
        title.add_gradient("background", "background3", 5, -10)


        shelf = DivWdg()
        top.add(shelf)
        shelf.add_style("margin-left: -8px")
        shelf.add_style("width: 130px")

        button_div = DivWdg()
        shelf.add(button_div)
        button_div.add_style("float: left")
        button_div.add_style("margin-top: -3px")

        security = Environment.get_security()
        view_side_bar = security.check_access("builtin", "view_side_bar", "allow", default='allow')
        if view_side_bar:
            button = IconButtonWdg(title="Side Bar", icon=IconWdg.ARROW_LEFT)
            button_div.add(button)
            shelf.add("Toggle Side Bar")
            shelf.add_attr("title", "Toggle Side Bar (or press '1')")
            button.add_behavior( {
                'type': 'click_up',
                'cbjs_action': '''
                spt.named_events.fire_event("side_bar|toggle");
                '''
            } )
            shelf.add_behavior( {
                'type': 'click_up',
                'cbjs_action': '''
                spt.named_events.fire_event("side_bar|toggle");
                '''
            } )
            shelf.add_class("hand")
        else:
            shelf.add("&nbsp;")


        search_wdg = DivWdg()
        search_wdg.add_class("spt_main_top")
        top.add(search_wdg)
        search_wdg.add_style("padding: 10px")
        search_wdg.add_style("margin: 10px auto")
        search_wdg.add_style("width: 430px")
        search_wdg.add("Search: ")
        search_wdg.add("&nbsp;"*3)


        custom_cbk = {}
        custom_cbk['enter'] = '''
            var top = bvr.src_el.getParent(".spt_main_top");
            var search_el = top.getElement(".spt_main_search");
            var keywords = search_el.value;

            if (keywords != '') {
                var class_name = 'tactic.ui.panel.ViewPanelWdg';
                var kwargs = {
                    'search_type': 'sthpw/sobject_list',
                    'view': 'result_list',
                    'keywords': keywords,
                    'simple_search_view': 'simple_filter',
                    //'show_shelf': false,
                }
                spt.tab.set_main_body_tab();
                spt.tab.add_new("Search Results", "Search Results", class_name, kwargs);
            }
        '''


        from tactic.ui.input import TextInputWdg, LookAheadTextInputWdg
        #text = TextInputWdg(name="search")
        text = LookAheadTextInputWdg(name="search", custom_cbk=custom_cbk, width='280')
        #text = TextWdg("search")
        text.add_class("spt_main_search")
        text.add_style("width: 290px")
        search_wdg.add(text)
        search_wdg.add_style("font-weight: bold")
        search_wdg.add_style("font-size: 16px")


        button = ActionButtonWdg(title="Search")
        #search_wdg.add(button)
        button.add_style("float: right")
        #button.add_style("margin-top: -28px")

        icon_div = DivWdg()
        search_wdg.add(icon_div)
        icon_div.add_style("width: 38px")
        icon_div.add_style("height: 27px")
        icon_div.add_style("padding-top: 3px")
        icon_div.add_style("padding-left: 4px")
        icon_div.add_style("text-align: center")
        #icon_div.add_gradient("background", "background3", 15, -10)
        icon_div.add_color("background", "background3", 10)
        over_color = icon_div.get_color("background3", 0)
        out_color = icon_div.get_color("background3", 10)
        icon_div.set_round_corners(5)
        icon_div.set_box_shadow("1px 1px 1px 1px")
        icon = IconWdg("Search", IconWdg.SEARCH_32, width=24)
        icon_div.add(icon)
        icon_div.add_style("float: right")
        icon_div.add_style("margin-top: -5px")
        button = icon_div
        icon_div.add_class("hand")
        icon_div.add_behavior( {
            'type': 'mouseover',
            'color': over_color,
            'cbjs_action': '''
            bvr.src_el.setStyle("background", bvr.color);
            '''
        } )
        icon_div.add_behavior( {
            'type': 'mouseout',
            'color': out_color,
            'cbjs_action': '''
            bvr.src_el.setStyle("background", bvr.color);
            bvr.src_el.setStyle("box-shadow", "1px 1px 1px 1px #999");
            bvr.src_el.setStyle("margin-top", "-5");
            bvr.src_el.setStyle("margin-right", "0");
            '''
        } )
        icon_div.add_behavior( {
            'type': 'click',
            'color': out_color,
            'cbjs_action': '''
            bvr.src_el.setStyle("box-shadow", "0px 0px 1px 1px #999");
            bvr.src_el.setStyle("margin-top", "-3");
            bvr.src_el.setStyle("margin-right", "-2");
            '''
        } )
        icon_div.add_behavior( {
            'type': 'click_up',
            'color': out_color,
            'cbjs_action': '''
            bvr.src_el.setStyle("box-shadow", "1px 1px 1px 1px #999");
            bvr.src_el.setStyle("margin-top", "-5");
            bvr.src_el.setStyle("margin-right", "0");
            '''
        } )





        button.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_main_top");
            var search_el = top.getElement(".spt_main_search");
            var keywords = search_el.value;

            if (keywords == '') {
                return;
            }

            var class_name = 'tactic.ui.panel.ViewPanelWdg';
            var kwargs = {
                'search_type': 'sthpw/sobject_list',
                'view': 'result_list',
                'keywords': keywords,
                'simple_search_view': 'simple_filter',
                //'show_shelf': false,
            }
            spt.tab.set_main_body_tab();
            spt.tab.add_new("Search Results", "Search Results", class_name, kwargs);
            '''
        } )

        #desc = DivWdg()
        #top.add(desc)
        #desc.add("Dashboard")
        #desc.add_style("width: 600px")


        # create a bunch of panels
        table = Table()
        table.add_color("color", "color")
        table.add_style("margin-bottom: 20px")
        table.center()
        top.add(table)
        table.add_row()

        #security = Environment.get_security()
        #if not security.check_access("builtin", "view_site_admin", "allow"):

         

        td = table.add_cell()
        td.add_style("padding: 3px")
        td.add_style("vertical-align: top")
        title = "Configuration"
        #description = '''All TACTIC projects can be uniquely designed and managed using our configuration tools.'''
        description = '''Configure a Project from start to finish.'''
	image = "<img src='/context/icons/64x64/configuration_64.png'/>"
        behavior = {
            'type': 'click_up',
            'cbjs_action': '''
            spt.tab.set_main_body_tab();
            var class_name = 'tactic.ui.startup.ProjectConfigWdg';
            var kwargs = {
                help_alias: 'project-startup-configuration'
                };
            spt.tab.add_new("configuration", "Configuration", class_name, kwargs);
            '''
        }
        config_wdg = my.get_main_section_wdg(title, description, image, behavior)
        td.add(config_wdg)



        # Manage Users
        td = table.add_cell()
        td.add_style("vertical-align: top")
        td.add_style("padding: 3px")
        title = "Manage Users and Security"
        image = "<img src='/context/icons/64x64/dashboard_64.png'/>"
        image = DivWdg()
        image_link = "<div style='margin-bottom: -64px'><img src='/context/icons/64x64/lock_64.png'/></div>"
        image.add(image_link)

        image1 = IconWdg("Manage Users", IconWdg.USER_32)
        image2 = IconWdg("Manage Users", IconWdg.USER_32)
        image3 = IconWdg("Manage Users", IconWdg.USER_32)
        image4 = IconWdg("Manage Users", IconWdg.USER_32)
        image.add(image1)
        image.add(image2)
        image.add("<br/>")
        image.add(image3)
        image.add(image4)
        description = '''Manage users that can access the system'''

        behavior = {
        'type': 'click_up',
        'cbjs_action': '''
        spt.tab.set_main_body_tab();
        var class_name = 'tactic.ui.startup.UserConfigWdg';
        var kwargs = {
            help_alias: 'project-startup-manage-users'
            };
        spt.tab.add_new("user", "Users", class_name, kwargs);
        '''
        }
        manage_users_wdg = my.get_main_section_wdg(title, description, image, behavior)
        td.add(manage_users_wdg)



        # custom layout editor 
        td = table.add_cell()
        td.add_style("padding: 3px")
        td.add_style("vertical-align: top")
        title = "Custom Layouts"
        description = '''Create interfaces using the Custom Layout Editor.'''
	image = "<img src='/context/icons/64x64/layout_64.png'/>"
        behavior = {
            'type': 'click_up',
            'cbjs_action': '''
            spt.tab.set_main_body_tab();
            var class_name = 'tactic.ui.tools.CustomLayoutEditWdg';
            var kwargs = {
                help_alias: 'project-startup-configuration'
                };
            spt.tab.add_new("custom_layout_editor", "Custom Layout Editor", class_name, kwargs);
            '''
        }
        config_wdg = my.get_main_section_wdg(title, description, image, behavior)
        td.add(config_wdg)





        """
        # Manage Security
        td = table.add_cell()
        td.add_style("vertical-align: top")
        td.add_style("padding: 3px")
        title = "Manage Security"
        image = "<img src='/context/icons/64x64/lock_64.png'/>"
        description = '''Configure User Group security for Projects, Links and more'''

        behavior = {
        'type': 'click_up',
        'cbjs_action': '''
        var class_name = 'tactic.ui.startup.SecurityWdg';
        var kwargs = {
            help_alias: 'manage-security'
            };
        spt.tab.set_main_body_tab();
        spt.tab.add_new("security", "Security", class_name, kwargs);
        '''
        }
        security_wdg = my.get_main_section_wdg(title, description, image, behavior)
        td.add(security_wdg)
        """



        """
        table.add_row()
        # Lists
        td = table.add_cell()
        td.add_style("padding: 3px")
        td.add_style("vertical-align: top")
        title = "Lists of Items"
        image = IconWdg("Lists", IconWdg.SEARCH_TYPE_32)
        description = '''View all of the lists items for this project'''
        behavior = {
            'type': 'click_up',
            'cbjs_action': '''
            spt.tab.set_main_body_tab();
            var class_name = 'tactic.ui.startup.HomeWdg';
            var kwargs = {
                help_alias: 'main'
                };
            spt.tab.add_new("lists", "Lists", class_name, kwargs);
            '''
        }
        lists_wdg = my.get_small_section_wdg(title, description, image, behavior)
        td.add(lists_wdg)
        """


        """
        # Dashboards
        td = table.add_cell()
        td.add_style("vertical-align: top")
        td.add_style("padding: 3px")
        title = "Dashboards"
        image = IconWdg("Dashboards", IconWdg.DASHBOARD_02)
        #image = "<img src='/context/icons/64x64/dashboard_64.png'/>"
        description = '''Dashboards display key project data in single views.'''

        behavior = {
        'type': 'click_up',
        'cbjs_action': '''
        var class_name = 'tactic.ui.startup.dashboards_wdg.DashboardsWdg';
        var kwargs = {
            help_alias: 'project-startup-dashboards'
            };
        spt.tab.set_main_body_tab();
        spt.tab.add_new("dashboards", "Dashboards", class_name, kwargs);
        '''
        }
        dashboard_wdg = my.get_small_section_wdg(title, description, image, behavior)
        td.add(dashboard_wdg)
        """

        """
        # Reports
        td = table.add_cell()
        td.add_style("padding: 3px")
        td.add_style("vertical-align: top")
        title = "Reports"
        image = IconWdg("Reports", IconWdg.GRAPH_LINE_03)
        #image = "<img src='/context/icons/64x64/report_64.png'/>"
        #description = '''TACTIC provides a number of predefined reports for real-time analytics.'''
        description = '''A number of predefined reports for real-time project analytics.'''

        behavior = {
          'type': 'click_up',
          'cbjs_action': '''
            var class_name = 'tactic.ui.startup.reports_wdg.ReportsWdg';
            var kwargs = {
                help_alias: 'main'
                };
            spt.tab.set_main_body_tab();
            spt.tab.add_new("reports", "Reports", class_name, kwargs);
          '''
        }

        report_wdg = my.get_small_section_wdg(title, description, image, behavior)
        td.add(report_wdg)
        """



        tr = table.add_row()

        # Plugins
        td = table.add_cell()
        td.add_style("vertical-align: top")
        td.add_style("padding: 3px")
        title = "Plugin Manager"
        image = IconWdg("Plugins Manager", IconWdg.PLUGIN_32)
        #image = "<img src='/context/icons/64x64/dashboard_64.png'/>"
        description = '''Upload, install, remove and create TACTIC plugins.'''

        behavior = {
        'type': 'click_up',
        'cbjs_action': '''
        var class_name = 'tactic.ui.app.PluginWdg';
        spt.tab.set_main_body_tab();
        spt.tab.add_new("plugin_manager", "Plugin Manager", class_name, kwargs);
        '''
        }
        plugin_wdg = my.get_small_section_wdg(title, description, image, behavior)
        td.add(plugin_wdg)



        # Examples
        td = table.add_cell()
        td.add_style("vertical-align: top")
        td.add_style("padding: 3px")
        title = "Tools"
        image = IconWdg("Tools", IconWdg.SHARE_32)
        #image = "<img src='/context/icons/64x64/dashboard_64.png'/>"
        description = '''A collection of example views.'''

        behavior = {
        'type': 'click_up',
        'cbjs_action': '''
        var class_name = 'tactic.ui.startup.ToolsWdg';
        spt.tab.set_main_body_tab();
        spt.tab.add_new("tools", "Tools", class_name, kwargs);
        '''
        }
        share_wdg = my.get_small_section_wdg(title, description, image, behavior)
        td.add(share_wdg)





        # Share
        """
        td = table.add_cell()
        td.add_style("vertical-align: top")
        td.add_style("padding: 3px")
        title = "Shares"
        image = IconWdg("Shares", IconWdg.SHARE_32)
        #image = "<img src='/context/icons/64x64/dashboard_64.png'/>"
        description = '''Share project with other TACTIC installs.'''

        behavior = {
        'type': 'click_up',
        'cbjs_action': '''
        var class_name = 'tactic.ui.startup.ShareWdg';
        spt.tab.set_main_body_tab();
        spt.tab.add_new("shares", "Shares", class_name, kwargs);
        '''
        }
        share_wdg = my.get_small_section_wdg(title, description, image, behavior)
        td.add(share_wdg)
        """


        # Advanced
        td = table.add_cell()
        td.add_style("vertical-align: top")
        td.add_style("padding: 3px")
        title = "Advanced Setup"
        image = IconWdg("Advanced", IconWdg.ADVANCED_32)
        #image = "<img src='/context/icons/64x64/dashboard_64.png'/>"
        description = '''A set of advanced configuration tools.'''

        behavior = {
        'type': 'click_up',
        'cbjs_action': '''
        var class_name = 'tactic.ui.app.ProjectStartWdg';
        spt.tab.set_main_body_tab()
        spt.tab.add_new("project_setup", "Project Setup", class_name)
        '''
        }
        share_wdg = my.get_small_section_wdg(title, description, image, behavior)
        td.add(share_wdg)




        """
        td = table.add_cell()
        td.add_style("vertical-align: top")
        td.add_style("padding: 3px")
	title = "Documentation"

        description = '''TACTIC Documentation.
        * Project Setup Documentation<br/>
        <br/>
        * End User Documentation<br/>
        <br/>
        * Developer Documentation<br/>
        <br/>
        * System Administrator Documentation<br/>
        <br/>
        '''
        image = "<img src='/context/images/getting_started_pipeline.png'/>"
        behavior = {
        'type': 'click_up',
        'cbjs_action': '''
        spt.help.load_alias("main")
        '''
        }
        doc_wdg = my.get_section_wdg(title, description, image, behavior)
        td.add(doc_wdg)
        """





        tr, td = table.add_row_cell()
        td.add_style("font-size: 14px")
        td.add("<br/>")

        from misc_wdg import QuickLinksWdg
        quick_links_wdg = QuickLinksWdg()
        td.add(quick_links_wdg)
        
        #td = table.add_cell()
        #totals_wdg = my.get_totals_wdg()
	#td.add(totals_wdg)

        return top



    def get_totals_wdg(my):
        div = DivWdg()
        

        div.add("Number of Pipelines: 3<br/>") 
        div.add("Number of Search Types: 6<br/>") 
        div.add("Number of Naming Conventions: 4<br/>") 
        div.add("Number of Triggers: 8<br/>") 


        return div




