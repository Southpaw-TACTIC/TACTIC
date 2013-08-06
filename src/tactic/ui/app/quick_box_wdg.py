###########################################################
#
# Copyright (c) 2012, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#

__all__ = [ 'QuickBoxWdg']

import types
import os

import js_includes

from pyasm.common import Container, Environment
from pyasm.biz import Project
from pyasm.web import WebContainer, Widget, HtmlElement, DivWdg, BaseAppServer
from pyasm.widget import IconWdg

from tactic.ui.common import BaseRefreshWdg


class QuickBoxWdg(BaseRefreshWdg):

    def get_section_wdg(my, title, description, image, behavior):

        section_wdg = DivWdg()
        section_wdg.set_round_corners()
        section_wdg.add_border()
        section_wdg.add_style("width: 120px")
        section_wdg.add_style("height: 100px")
        section_wdg.add_style("overflow: hidden")
        section_wdg.add_style("margin: 5px")
        section_wdg.set_box_shadow("0px 0px 10px")

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

        """
        desc_div = DivWdg()
        desc_div.add(description)
        desc_div.add_style("padding: 5px 10px 10px 5px")
        """

        div = DivWdg()
        section_wdg.add(div)
        div.add_style("margin-top: 20px")
        div.center()
        div.add_style("width: 32px")
        div.add(image)

        section_wdg.add_behavior( behavior )
        section_wdg.add_class("hand")
        section_wdg.add_attr('title', description)

        return section_wdg



    def get_display(my):

        top = my.top
        top.add_style("position: absolute")
        top.add_style("top: 300")
        top.add_style("left: 600")
        top.add_style("display: none")
        top.set_id("spt_hot_box")
        top.add_style("margin: 0 auto")

        top.add_behavior( {
            'type': 'listen',
            'event_name': 'hotbox|toggle',
            'cbjs_action': '''
            var size = $(window).getSize();
            bvr.src_el.setStyle("left", size.x/2-300);
            bvr.src_el.setStyle("top", size.y/2-200);
            if (bvr.src_el.getStyle("display") == "none") {
                spt.show(bvr.src_el);
                spt.body.add_focus_element(bvr.src_el);
                spt.popup.show_background();
            }
            else {
                spt.hide(bvr.src_el);
                spt.popup.hide_background();
            }
            '''
        } )

        top.add_behavior( {
            'type': 'listen',
            'event_name': 'hotbox|close',
            'cbjs_action': '''
            spt.hide(bvr.src_el);
            spt.popup.hide_background();
            '''
        } )



        div = DivWdg()
        top.add(div)
        div.add_style("width: 630px")
        div.add_style("height: 400px")
        div.add_style("opacity: 0.8")
        div.add_gradient("background", "background3", 10)
        div.add_style("position: fixed")
        div.add_style("z-index: 1000")
        #div.set_box_shadow("2px 2px 4px 4px")
        div.set_box_shadow(color="#000")
        div.set_round_corners(25)
        div.add_border()

        content_wdg = DivWdg()
        content_wdg.add_style("position: fixed")
        top.add(content_wdg)
        content_wdg.add_style("padding: 20px 50px 50px 50px")
        content_wdg.add_style("z-index: 1001")


        close_wdg = DivWdg()
        content_wdg.add(close_wdg)
        icon = IconWdg('Close Quick Links', IconWdg.POPUP_WIN_CLOSE)
        close_wdg.add(icon)
        #close_wdg.add_style("position: fixed")
        close_wdg.add_style("float: right")
        close_wdg.add_style("margin-top: -5px")
        close_wdg.add_style("margin-right: -40px")
        close_wdg.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            spt.named_events.fire_event("hotbox|close");
            '''
        } )
        close_wdg.add_class("hand")



        """
        image = "FLOW_CHART_02"
        image = eval("IconWdg('', IconWdg.%s)" % image)
        behavior = {
            'type': 'click_up',
            'cbjs_action': '''
            document.location = "/tactic/admin/#/link/create_project";
            spt.named_events.fire_event("hotbox|close");
            '''
        }
        section = my.get_section_wdg("Create Project", "Project Creation Wizard", image, behavior)
        section.add_style("float: left")
        content_wdg.add(section)
        """






        image = "FLOW_CHART_02"
        image = eval("IconWdg('', IconWdg.%s)" % image)
        behavior = {
            'type': 'click_up',
            'cbjs_action': '''
            spt.tab.set_main_body_tab();

            var class_name = 'tactic.ui.startup.MainWdg';
            spt.tab.add_new("Project Startup", "Project Startup", class_name);
            spt.named_events.fire_event("hotbox|close");
            '''
        }
        section = my.get_section_wdg("Configuration", "Lots of Config Goodies", image, behavior)
        section.add_style("float: left")
        content_wdg.add(section)



        image = "USER_32"
        image = eval("IconWdg('', IconWdg.%s)" % image)
        behavior = {
            'type': 'click_up',
            'cbjs_action': '''
            spt.tab.set_main_body_tab();
            var class_name = 'tactic.ui.startup.UserConfigWdg';
            spt.tab.add_new("Users", "Users", class_name);
            spt.named_events.fire_event("hotbox|close");
            '''
        }
        section = my.get_section_wdg("Users", "Users", image, behavior)
        section.add_style("float: left")
        content_wdg.add(section)





        image = "LOCK_32_01"
        image = eval("IconWdg('', IconWdg.%s)" % image)
        behavior = {
            'type': 'click_up',
            'cbjs_action': '''
            spt.tab.set_main_body_tab();
            var class_name = 'tactic.ui.startup.SecurityWdg';
            spt.tab.add_new("Security", "Security", class_name);
            spt.named_events.fire_event("hotbox|close");
            '''
        }
        section = my.get_section_wdg("Security", "Security", image, behavior)
        section.add_style("float: left")
        content_wdg.add(section)


	image = "<img width='32' src='/context/icons/64x64/layout_64.png'/>"
        behavior = {
            'type': 'click_up',
            'cbjs_action': '''
            spt.tab.set_main_body_tab();

            var class_name = 'tactic.ui.tools.CustomLayoutEditWdg';
            var args = { };
            spt.tab.add_new("custom_layout_editor", "Custom Layout Editor", class_name, args);
            spt.named_events.fire_event("hotbox|close");
            '''
        }
        section = my.get_section_wdg("Custom Layout", "Create Custom Interfaces", image, behavior)
        section.add_style("float: left")
        content_wdg.add(section)



        content_wdg.add("<br clear='all'/>")
        content_wdg.add("<br clear='all'/>")


        image = "FLOW_CHART_01"
        image = eval("IconWdg('', IconWdg.%s)" % image)
        behavior = {
            'type': 'click_up',
            'cbjs_action': '''
            spt.tab.set_main_body_tab();
            var class_name = 'tactic.ui.app.ProjectStartWdg';
            spt.tab.add_new("advanced_project_setup", "Advanced Project Setup", class_name);
            spt.named_events.fire_event("hotbox|close");
            '''
        }
        section = my.get_section_wdg("Advanced Setup", "Advanced Setup", image, behavior)
        section.add_style("float: left")
        content_wdg.add(section)



        image = "FLOW_CHART_01"
        image = eval("IconWdg('', IconWdg.%s)" % image)
        behavior = {
            'type': 'click_up',
            'cbjs_action': '''
            spt.tab.set_main_body_tab();
            var class_name = 'tactic.ui.tools.SchemaToolWdg';
            var kwargs = {
                help_alias: 'project-schema'    
            };
            spt.tab.add_new("project_schema", "Project Schema", class_name, kwargs);
            spt.named_events.fire_event("hotbox|close");
            
            '''
        }
        section = my.get_section_wdg("Project Schema", "Project Schema", image, behavior)
        section.add_style("float: left")
        content_wdg.add(section)



        image = "FLOW_CHART_03"
        image = eval("IconWdg('', IconWdg.%s)" % image)
        behavior = {
            'type': 'click_up',
            'cbjs_action': '''
            spt.tab.set_main_body_tab();
            var class_name = 'tactic.ui.tools.PipelineToolWdg';
            var kwargs = {
                help_alias: 'project-workflow'
            };
            spt.tab.add_new("project_workflow", "Project Workflow", class_name, kwargs);

            spt.named_events.fire_event("hotbox|close");
            '''
        }
        section = my.get_section_wdg("Project Workflow", "Project Workflow", image, behavior)
        section.add_style("float: left")
        content_wdg.add(section)



        image = "ADVANCED_32"
        image = eval("IconWdg('', IconWdg.%s)" % image)
        behavior = {
            'type': 'click_up',
            'cbjs_action': '''
            spt.tab.set_main_body_tab();

            var class_name = 'tactic.ui.panel.ViewPanelWdg';
            var args = { search_type: 'config/widget_config',
                        simple_search_view: 'simple_filter',
                        view : 'table'};
            spt.tab.add_new("Widget Config", "Widget Config", class_name, args);
            spt.named_events.fire_event("hotbox|close");
            '''
        }
        section = my.get_section_wdg("Widget Config", "Advanced editing of widget configuration", image, behavior)
        section.add_style("float: left")
        content_wdg.add(section)



        content_wdg.add("<br clear='all'/>")
        content_wdg.add("<br clear='all'/>")

        image = "PLUGIN_32"
        image = eval("IconWdg('', IconWdg.%s)" % image)
        behavior = {
            'type': 'click_up',
            'cbjs_action': '''
            spt.tab.set_main_body_tab();

            var class_name = 'tactic.ui.app.PluginWdg';
            var args = {
            };
            spt.tab.add_new("Plugin Manager", "Plugin Manager", class_name, args);
            spt.named_events.fire_event("hotbox|close");
            '''
        }
        section = my.get_section_wdg("Plugin Manager", "Tool to load and unload plugins.", image, behavior)
        section.add_style("float: left")
        content_wdg.add(section)




        image = "CONFIGURE_03"
        image = eval("IconWdg('', IconWdg.%s)" % image)
        behavior = {
            'type': 'click_up',
            'cbjs_action': '''
            spt.tab.set_main_body_tab();

            var class_name = 'tactic.ui.panel.ManageViewPanelWdg';
            var args = {
            };
            spt.tab.add_new("Side Bar Manager", "Side Bar Manager", class_name, args);
            spt.named_events.fire_event("hotbox|close");
            '''
        }
        section = my.get_section_wdg("Side Bar Manager", "Tool to manage links and folders for the side bar.", image, behavior)
        section.add_style("float: left")
        content_wdg.add(section)





        #image = "CONFIGURE_03"
        #image = eval("IconWdg('', IconWdg.%s)" % image)
	image = "<img width='32' src='/context/icons/64x64/layout_64.png'/>"
        behavior = {
            'type': 'click_up',
            'cbjs_action': '''
            spt.tab.set_main_body_tab();

            var class_name = 'tactic.ui.tools.RepoBrowserWdg';
            var args = {
                open_depth: 0,
                depth: 0,
            };
            spt.tab.add_new("File Browser", "File Browser", class_name, args);
            spt.named_events.fire_event("hotbox|close");
            '''
        }
        section = my.get_section_wdg("File Browser", "Browser.", image, behavior)
        section.add_style("float: left")
        content_wdg.add(section)










        """
        image = "SHARE_32"
        image = eval("IconWdg('', IconWdg.%s)" % image)
        behavior = {
            'type': 'click_up',
            'cbjs_action': '''
            spt.tab.set_main_body_tab();

            var class_name = 'tactic.ui.startup.ShareWdg';
            var args = {
            };
            spt.tab.add_new("Shares", "Shares", class_name, args);
            spt.named_events.fire_event("hotbox|close");
            '''
        }
        section = my.get_section_wdg("Share Manager", "Tool to share project with other TACTIC installs.", image, behavior)
        section.add_style("float: left")
        content_wdg.add(section)
        """




        return top
   


