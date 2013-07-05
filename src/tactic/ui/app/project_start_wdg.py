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

__all__ = ['ProjectStartWdg']

from pyasm.common import Environment, Common
from pyasm.search import Search
from pyasm.web import DivWdg, HtmlElement, SpanWdg, Table, Widget
from pyasm.widget import IconWdg

import os

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.widget import SingleButtonWdg

class ProjectStartWdg(BaseRefreshWdg):
    '''This is the welcome widget widget will appear on creation of a new
    project
    '''

    def get_args_keys(my):
        return {
        }


    def get_main_section_wdg(my, title, description, image, behavior):

        section_wdg = DivWdg()
        section_wdg.set_round_corners()
        section_wdg.add_border()
        section_wdg.add_style("width: 225px")
        #section_wdg.add_style("height: 200px")
	section_wdg.add_style("height: 310px")
        section_wdg.add_style("overflow: hidden")
        section_wdg.add_style("margin: 10px")
        section_wdg.set_box_shadow("1px 1px 2px 2px")


        title_wdg = DivWdg()
        section_wdg.add(title_wdg)
        title_wdg.add(title)
        title_wdg.add_style("height: 20px")
        title_wdg.add_style("padding: 3px")
        title_wdg.add_style("margin-top: 3px")
        title_wdg.add_style("font-weight: bold")
        title_wdg.add_gradient("background", "background")

        section_wdg.add_color("background", "background")
        section_wdg.add_behavior( {
        'type': 'hover',
        'add_color_modifier': -5,
        'cb_set_prefix': 'spt.mouse.table_layout_hover',
        } )

        desc_div = DivWdg()
        desc_div.add(description)
        desc_div.add_style("padding: 0px 10px 10px 5px")


        div = DivWdg()
        section_wdg.add(div)
        div.add_style("padding: 3px")
        div.add_style("margin: 5px")
        div.add_style("width: 210px")
        #div.add_style("height: 64px")
        div.add_style("height: 170px")
	div.add_style("text-align: center")
        div.add(image)
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
        section_wdg.set_box_shadow("1px 1px 1px 1px")

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
        div.add_style("padding: 3px")
        div.add_style("margin: 5px")
        div.add_style("width: 65px")
        div.add_style("height: 50px")
        div.add_style("float: left")
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
        top.add_color("background", "background")


        title = DivWdg()
        title.add("Advanced Project Setup Tools")
        title.add_style("font-size: 18px")
        title.add_style("font-weight: bold")
        title.add_style("text-align: center")
        title.add_style("padding: 10px")
        title.add_style("margin: -10px -10px 10px -10px")

        top.add(title)
        from tactic.ui.widget import TitleWdg
        subtitle = TitleWdg(name_of_title='',help_alias='project-startup-configuration')
        top.add(subtitle)

        title.add_gradient("background", "background3", 5, -10)
        top.add("<br/>")


        content = DivWdg()
        top.add(content)

	

        """
        desc = DivWdg()
        content.add(desc)
        desc.add_style("text-align: left")
        desc.add_style("padding-left: 15px")
        desc.center()
        desc.add("The following tools are used for advanced project configuration.<br/><br/>")
        desc.add_style("width: 600px")
        """

        button_div = DivWdg()
        button = SingleButtonWdg(title="Collapse", icon=IconWdg.HOME)
        button_div.add(button)
        button_div.add_style("float: left")
	button_div.add_style("margin-top: -10px")
        button.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            spt.tab.set_main_body_tab();
            var class_name = 'tactic.ui.startup.MainWdg';
            var kwargs = {
                help_alias: 'project-startup-configuration'
            };
            spt.tab.add_new("_startup", "Startup", class_name, kwargs);
        
            '''
        }) 
        content.add(button_div)

        table = Table()
        content.add(table)
        table.add_color("color", "color")
        table.add_row()
        table.center()



        # Schema Editor
        td = table.add_cell()
        td.add_style("vertical-align: top")
        td.add_style("padding: 3px")
        title = "Create Schema"

        description = '''The schema is a collection of nodes that layout the basic components of a project. Each node represents a separate list of items (sType) used in this project: ie Assets, Shots, Artwork, etc.'''

	#image = "<img src='/context/icons/64x64/schema_64.png'/>"
	image = "<img src='/context/images/getting_started_schema.png'/>"
        behavior = {
        'type': 'click_up',
        'cbjs_action': '''
        spt.tab.set_main_body_tab();
        var class_name = 'tactic.ui.tools.SchemaToolWdg';
        var kwargs = {
            help_alias: 'project-schema'    
        };
        spt.tab.add_new("create_schema", "Create Schema", class_name, kwargs);
        '''
        }
        schema_wdg = my.get_main_section_wdg(title, description, image, behavior)
        td.add(schema_wdg)


        # Workflow
        td = table.add_cell()
        td.add_style("vertical-align: top")
        td.add_style("padding: 3px")
        title = "Create Workflow"
        image = "<img src='/context/images/getting_started_pipeline.png'/>"

        description = "Pipelines define how particular items of an sType will move through its lifecycle. Creating pipelines will also allow you to set up automatic triggers and notifications for each process."

        behavior = {
        'type': 'click_up',
        'cbjs_action': '''
        spt.tab.set_main_body_tab();
        var class_name = 'tactic.ui.tools.PipelineToolWdg';
        var kwargs = {
            help_alias: 'project-workflow'
        };
        spt.tab.add_new("create_workflow", "Create Workflow", class_name, kwargs);
        '''
        }
        pipeline_wdg = my.get_main_section_wdg(title, description, image, behavior)
        td.add(pipeline_wdg)


        # Sidebar
        td = table.add_cell()
        td.add_style("padding: 3px")
        td.add_style("vertical-align: top")
        title = "Manage Side Bar"

	#image = "<img src='/context/icons/64x64/sidebar_64.png'/>"
        image = "<img src='/context/images/getting_started_sidebar.png'/>"

	description = "The Side Bar can be easily configured to show specific views of your project to each user."
        behavior = {
        'type': 'click_up',
        'cbjs_action': '''
        spt.tab.set_main_body_tab();
        var class_name = 'tactic.ui.panel.ManageViewPanelWdg';
        var kwargs = {
            help_alias: 'managing-sidebar'
        };
        spt.tab.add_new("manage_project_views", "Manage Side Bar", class_name, kwargs);
        '''
        }

        side_bar_wdg = my.get_main_section_wdg(title, description, image, behavior)
        td.add(side_bar_wdg)


 
        tr = table.add_row()

        # Manage View
        td = table.add_cell()
        td.add_style("padding: 3px")
        td.add_style("vertical-align: top")
        title = "Manage Views"

        image = IconWdg("Manage Views", IconWdg.LIST_01)
        div = DivWdg(image)
        image = div

        description = "Manage the views within the project."
        behavior = {
        'type': 'click_up',
        'cbjs_action': '''
        spt.tab.set_main_body_tab();
        var class_name = 'tactic.ui.manager.ViewManagerWdg';
        var kwargs = {
            help_alias: 'view-manager'
            };
        spt.tab.add_new("manage_views", "Manage Views", class_name, kwargs);
        '''
        }

        manage_view_wdg = my.get_small_section_wdg(title, description, image, behavior)
        td.add(manage_view_wdg)



        # Naming Conventions
        td = table.add_cell()
        td.add_style("padding: 3px")
        td.add_style("vertical-align: top")
        title = "Naming Conventions"

        image = IconWdg("Naming Conventions", IconWdg.FOLDERS_01)
        div = DivWdg(image)
        image = div

        description = "Setup custom Directory and File naming conventions."
        behavior = {
        'type': 'click_up',
        'cbjs_action': '''
        spt.tab.set_main_body_tab();
        var class_name = 'tactic.ui.panel.ViewPanelWdg';
        var kwargs = {
	    'view': 'table',
            'search_type': 'config/naming',
            help_alias: 'project-automation-file-naming'
	};
        spt.tab.add_new("naming_conventions", "Naming Conventions", class_name, kwargs);
        '''
        }

        naming_wdg = my.get_small_section_wdg(title, description, image, behavior)
        td.add(naming_wdg)




        # Manage Search Types 
	td = table.add_cell()
        td.add_style("padding: 3px")
        td.add_style("vertical-align: top")
        title = "Manage Database (sTypes)"

        image = IconWdg("Manage Database", IconWdg.DASHBOARD_02)
        div = DivWdg(image)
        image = div

        description = "Manage the sType tables in the Database."
        behavior = {
        'type': 'click_up',
        'cbjs_action': '''
          spt.tab.set_main_body_tab();
          var class_name = 'tactic.ui.app.SearchTypeToolWdg';
          var kwargs = {
                help_alias: 'stype-register'  
          };
          spt.tab.add_new("stype_manager", "Manage sTypes", class_name, kwargs);
        '''
        }

        stype_wdg = my.get_small_section_wdg(title, description, image, behavior)
        td.add(stype_wdg)


        tr = table.add_row()




        # Script Editor 
        td = table.add_cell()
        td.add_style("padding: 3px")
        td.add_style("vertical-align: top")
        title = "Script Editor"

        image = IconWdg("Script Editor", IconWdg.SCRIPT_EDITOR_01)
        div = DivWdg(image)
        image = div

        description = "Edit and Create custom Python and Javascipt tools, triggers and scripts."
        behavior = {
        'type': 'click_up',
        'cbjs_action': '''
        
	var title = "TACTIC Script Editor"
	var class_name = "tactic.ui.app.ShelfEditWdg"
        spt.panel.load_popup(title, class_name, {}, {"load_once": true} )
        
        '''
        }

        script_editor_wdg = my.get_small_section_wdg(title, description, image, behavior)
        td.add(script_editor_wdg)




        # Project Settings
        td = table.add_cell()
        td.add_style("padding: 3px")
        td.add_style("vertical-align: top")
        title = "Project Settings"

        image = IconWdg("Project Settings", IconWdg.CONFIGURE_02)
        div = DivWdg(image)
        image = div

        description = "Setting for the current project."
        behavior = {
        'type': 'click_up',
        'cbjs_action': '''
        spt.tab.set_main_body_tab();
        var class_name = 'tactic.ui.panel.ViewPanelWdg';
        var kwargs = {
	    'view': 'table',
            'search_type': 'prod/prod_setting',
            help_alias: 'main'            
	};
        spt.tab.add_new("project_settings", "Project Settings", class_name, kwargs);
        '''
        }

        prod_settings_wdg = my.get_small_section_wdg(title, description, image, behavior)
        td.add(prod_settings_wdg)


        # Widget Config
        td = table.add_cell()
        td.add_style("padding: 3px")
        td.add_style("vertical-align: top")
        title = "Widget Config"

        image = IconWdg("Widget Config", IconWdg.WIDGET_CONFIG_01)
        div = DivWdg(image)
        image = div

        description = "Modify the base widget configurations for the project."
        behavior = {
        'type': 'click_up',
        'cbjs_action': '''
        spt.tab.set_main_body_tab();
        var class_name = 'tactic.ui.panel.ViewPanelWdg';
        var kwargs = {
	    'view': 'table',
            'search_type': 'config/widget_config',
            help_alias: 'tactic-widgets'
	};
        spt.tab.add_new("widget_config", "Widget Config", class_name, kwargs);
        '''
        }

        config_wdg = my.get_small_section_wdg(title, description, image, behavior)
        td.add(config_wdg)



        # Quicklinks

        tr, td = table.add_row_cell()
        td.add_style("font-size: 14px")
        td.add("<br/>")


        div = DivWdg()
        title = DivWdg()
        div.add(title)
        div.add_color("background", "background")
        div.add_style("margin: 0px 10px 15px 10px")


        title.add("Quick Links")
        title.add_style("font-size: 16px")
        title.add_style("padding: 5px")
        title.add_gradient("background", "background")
        title.add_border()
        title.set_round_corners(corners=['TL','TR'])

        content_wdg = DivWdg()
        div.add(content_wdg)
        content_wdg.add_border()
        content_wdg.add_style("padding: 20px")

        content_wdg.add("<div style='font-size: 12px'>The following links will help you find out more information on how to set-up or use TACTIC.</div>")
        content_wdg.add("<hr/>")

        hover = title.get_color("background", -10)


        link_div = DivWdg()
        link_div.add_style("padding: 10px")
        content_wdg.add(link_div)
        icon = IconWdg("TACTIC Documentation", IconWdg.JUMP)
        link_div.add(icon)

        link = HtmlElement.href("TACTIC Documentation", "/doc/", target="_blank")
        link.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            spt.help.set_top();
            spt.help.load_alias("main");
            '''
        } )

        link.add_behavior( {
        'type': 'hover',
        'color': hover,
        'cbjs_action_over': '''
        bvr.src_el.setStyle("background", bvr.color);
        ''',
        'cbjs_action_out': '''
        bvr.src_el.setStyle("background", "");
        '''
        } )
        link_div.add(link)
        link.add_color("color", "color")
        link_div.add("<br/>"*2)

        icon = IconWdg("Southpaw Web Site", IconWdg.JUMP)
        link_div.add(icon)
        link = HtmlElement.href("Southpaw Web Site", "http://www.southpawtech.com", target="_blank")
        link_div.add(link)
        link.add_color("color", "color")
        link.add_behavior( {
        'type': 'hover',
        'color': hover,
        'cbjs_action_over': '''
        bvr.src_el.setStyle("background", bvr.color);
        ''',
        'cbjs_action_out': '''
        bvr.src_el.setStyle("background", "");
        '''
        } )


        link_div.add("<br/>"*2)


        icon = IconWdg("TACTIC Community", IconWdg.JUMP)
        link_div.add(icon)
        link = HtmlElement.href("TACTIC Community", "http://community.southpawtech.com", target="_blank")
        link_div.add(link)
        link.add_color("color", "color")
        link.add_behavior( {
        'type': 'hover',
        'color': hover,
        'cbjs_action_over': '''
        bvr.src_el.setStyle("background", bvr.color);
        ''',
        'cbjs_action_out': '''
        bvr.src_el.setStyle("background", "");
        '''
        } )


        td.add(div)


        return top



    def get_totals_wdg(my):
        div = DivWdg()
        

        div.add("Number of Pipelines: 3<br/>") 
        div.add("Number of Search Types: 6<br/>") 
        div.add("Number of Naming Conventions: 4<br/>") 
        div.add("Number of Triggers: 8<br/>") 


        return div




