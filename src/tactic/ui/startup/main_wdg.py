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

__all__ = ['MainWdg', 'SectionWdg']

from pyasm.common import Environment, Common
from pyasm.search import Search
from pyasm.biz import Project
from pyasm.web import DivWdg, HtmlElement, SpanWdg, Table, Widget
from pyasm.widget import IconWdg, TextWdg

import os

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.widget import ActionButtonWdg, IconButtonWdg
from tactic.ui.app import SearchWdg



class SectionWdg(BaseRefreshWdg):

    def get_display(self):

        title = self.kwargs.get("title")
        description = self.kwargs.get("description")
        image = self.kwargs.get("image")
        behavior = self.kwargs.get("behavior")

        return self.get_main_section_wdg(title, description, image, behavior)

    def get_main_section_wdg(self, title, description, image, behavior, img_height="64px"):

        section_wdg = DivWdg()
        #section_wdg.set_round_corners()
        section_wdg.add_border()
        section_wdg.add_style("width: 225px")
        section_wdg.add_style("height: 225px")
        section_wdg.add_style("overflow: hidden")
        section_wdg.add_style("margin: -5px 5px 10px 5px")
        #section_wdg.add_style("margin: 10px")
        #section_wdg.set_box_shadow()

        title_wdg = DivWdg()
        section_wdg.add(title_wdg)
        title_wdg.add(title)
        title_wdg.add_style("height: 20px")
        title_wdg.add_style("padding: 3px")
        title_wdg.add_style("margin-top: 3px")
        title_wdg.add_style("font-weight: bold")
        title_wdg.add_style("text-align: center")
        title_wdg.add_color("background", "background", -5)

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
        bvr.src_el.setStyle("box-shadow", "0px 0px 10px " + bvr.shadow);
        '''
        } )

        section_wdg.add_behavior( {
        'type': 'mouseenter',
        'shadow': shadow,
        'cbjs_action': '''
        //bvr.src_el.setStyle("box-shadow", "0px 0px 10px " + bvr.shadow);
        ''',
        } )



        section_wdg.add_behavior( {
        'type': 'mouseleave',
        'shadow': shadow,
        'cbjs_action': '''
        bvr.src_el.setStyle("box-shadow", "0px 0px 0px " + bvr.shadow);
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
        div.add_style("height: %s" % img_height)
        div.add_style("text-align: center")
        div.add(image)
        #div.set_box_shadow("1px 1px 1px 1px")
        section_wdg.add(desc_div)
        div.add_style("overflow: hidden")

        section_wdg.add_behavior( behavior )
        section_wdg.add_class("hand")

        return section_wdg


    def get_small_section_wdg(self, title, description, image, behavior):

        section_wdg = DivWdg()
        #section_wdg.set_round_corners()
        section_wdg.add_border()
        section_wdg.add_style("width: 225px")
        section_wdg.add_style("height: 100px")
        section_wdg.add_style("overflow: hidden")
        section_wdg.add_style("margin: 10px")
        #section_wdg.set_box_shadow("0px 0px 5px")

        title_wdg = DivWdg()
        section_wdg.add(title_wdg)
        title_wdg.add(title)
        title_wdg.add_style("height: 20px")
        title_wdg.add_style("padding: 3px")
        title_wdg.add_style("margin-top: 3px")
        title_wdg.add_style("font-weight: bold")
        title_wdg.add_color("background", "background", -5)

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



from pyasm.common import SecurityException

class MainWdg(BaseRefreshWdg):
    '''This is the welcome widget widget will appear on creation of a new
    project
    '''

    def admin_only(self):
        return True


    def get_args_keys(self):
        return {
        }

    def init(self):
        # clear the widget settings of last_search:sthpw/sobject_list
        SearchWdg.clear_search_data('sthpw/sobject_list')
        super(MainWdg,self).init()



    def get_main_section_wdg(self, title, description, image, behavior):
        section_wdg = SectionWdg()
        return section_wdg.get_main_section_wdg(title, description, image, behavior)

    def get_small_section_wdg(self, title, description, image, behavior):
        section_wdg = SectionWdg()
        return section_wdg.get_small_section_wdg(title, description, image, behavior)


    def get_display(self):

        top = DivWdg()
        #top.add_border()
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


        title = DivWdg()
        title.add_style("font-size: 25px")
        title.add("Project Startup and Configuration")
        top.add(title)
        top.add("<hr/>")



        project = Project.get()
        title = DivWdg()
        title.add("Project Startup and Configuration")
        title.add_style("font-size: 18px")
        title.add_style("font-weight: bold")
        title.add_style("text-align: center")
        title.add_style("padding: 10px")
        title.add_style("margin: -10px -10px 10px -10px")

        #top.add(title)
        title.add_gradient("background", "background3", 5, -10)

        """
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
            button = IconButtonWdg(title="Side Bar", icon="FA_ANGLE_LEFT")
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
        """



        search_wdg = Table()
        #top.add(search_wdg)
        search_wdg.add_row()

        search_wdg.add_class("spt_main_top")
        search_wdg.add_style("padding: 10px")
        search_wdg.add_style("margin: 20px auto")
        search_wdg.add_style("width: 430px")

        td = search_wdg.add_cell("Search: ")
        td.add_style("vertical-align: top")
        td.add_style("padding-top: 8px")


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
        text = LookAheadTextInputWdg(name="search", custom_cbk=custom_cbk, width='280', height='42px')
        #text = TextWdg("search")
        text.add_class("spt_main_search")
        text.add_style("width: 290px")

        search_wdg.add_cell(text)
        search_wdg.add_style("font-weight: bold")
        search_wdg.add_style("font-size: 16px")


        icon_div = DivWdg()
        td = search_wdg.add_cell(icon_div)
        td.add_style("vertical-align: top")
        icon_div.add_style("width: 38px")
        icon_div.add_style("height: 27px")
        icon_div.add_style("padding-top: 7px")
        icon_div.add_style("padding-left: 4px")
        icon_div.add_style("text-align: center")
        icon_div.add_color("background", "background3", 10)
        over_color = icon_div.get_color("background3", 0)
        out_color = icon_div.get_color("background3", 10)
        icon_div.set_round_corners(5)
        icon_div.set_box_shadow("1px 1px 1px 1px")
        icon = IconWdg("Search", IconWdg.SEARCH_32, width=24)
        icon_div.add(icon)
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
        table.add_style("margin: 0px auto")
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
        description = '''Configure various aspects of a project.'''
        image = "<img src='/context/icons/64x64/configuration_64.png'/>"
        behavior = {
            'type': 'click_up',
            'cbjs_action': '''
            spt.tab.set_main_body_tab();
            var class_name = 'tactic.ui.startup.ProjectConfigWdg';
            var kwargs = {
                help_alias: 'project-startup-configuration'
                };
            spt.tab.add_new("project_configuration", "Configuration", class_name, kwargs);
            '''
        }
        config_wdg = self.get_main_section_wdg(title, description, image, behavior)
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
        spt.tab.add_new("manage_user", "Manage Users", class_name, kwargs);
        '''
        }
        manage_users_wdg = self.get_main_section_wdg(title, description, image, behavior)
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
        config_wdg = self.get_main_section_wdg(title, description, image, behavior)
        td.add(config_wdg)




        tr = table.add_row()

        # Plugins
        td = table.add_cell()
        td.add_style("vertical-align: top")
        td.add_style("padding: 3px")
        title = "Manage Plugins"
        #image = IconWdg("Manage Plugins", IconWdg.PLUGIN_32)
        #image = "<img src='/context/icons/64x64/dashboard_64.png'/>"
        image = IconWdg("Manage Plugins", "FAS_PLUG", size=32)
        description = '''Upload, install, remove and create TACTIC plugins.'''

        behavior = {
        'type': 'click_up',
        'cbjs_action': '''
        var class_name = 'tactic.ui.app.PluginWdg';
        spt.tab.set_main_body_tab();
        spt.tab.add_new("plugins", "Manage Plugin", class_name, kwargs);
        '''
        }
        plugin_wdg = self.get_small_section_wdg(title, description, image, behavior)
        td.add(plugin_wdg)



        # Examples
        td = table.add_cell()
        td.add_style("vertical-align: top")
        td.add_style("padding: 3px")
        title = "Views"
        #image = IconWdg("Views", IconWdg.SHARE_32)
        #image = "<img src='/context/icons/64x64/dashboard_64.png'/>"
        image = IconWdg("Views", "FAS_COLUMNS", size=32)
        description = '''A collection of example views.'''

        behavior = {
        'type': 'click_up',
        'cbjs_action': '''
        var class_name = 'tactic.ui.startup.ToolsWdg';
        spt.tab.set_main_body_tab();
        spt.tab.add_new("tools", "Tools", class_name, kwargs);
        '''
        }
        share_wdg = self.get_small_section_wdg(title, description, image, behavior)
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
        share_wdg = self.get_small_section_wdg(title, description, image, behavior)
        td.add(share_wdg)
        """


        # Advanced
        td = table.add_cell()
        td.add_style("vertical-align: top")
        td.add_style("padding: 3px")
        title = "Advanced Setup"
        #image = IconWdg("Advanced", IconWdg.ADVANCED_32)
        #image = "<img src='/context/icons/64x64/dashboard_64.png'/>"
        image = IconWdg("Views", "FAS_UNIVERSITY", size=32)
        description = '''A set of advanced configuration tools.'''

        behavior = {
        'type': 'click_up',
        'cbjs_action': '''
        var class_name = 'tactic.ui.app.ProjectStartWdg';
        spt.tab.set_main_body_tab()
        spt.tab.add_new("project_setup", "Project Setup", class_name)
        '''
        }
        share_wdg = self.get_small_section_wdg(title, description, image, behavior)
        td.add(share_wdg)




        tr, td = table.add_row_cell()
        td.add_style("font-size: 14px")
        td.add("<br/>")

        from .misc_wdg import QuickLinksWdg
        quick_links_wdg = QuickLinksWdg()
        td.add(quick_links_wdg)
        
        #td = table.add_cell()
        #totals_wdg = self.get_totals_wdg()
	#td.add(totals_wdg)

        return top



    def get_totals_wdg(self):
        div = DivWdg()
        

        div.add("Number of Pipelines: 3<br/>") 
        div.add("Number of Search Types: 6<br/>") 
        div.add("Number of Naming Conventions: 4<br/>") 
        div.add("Number of Triggers: 8<br/>") 


        return div




