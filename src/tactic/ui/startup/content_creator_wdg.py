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

__all__ = ['ContentCreatorWdg', 'ExamplesWdg', 'ToolsWdg']

from pyasm.common import Environment, Common
from pyasm.search import Search
from pyasm.biz import Project
from pyasm.web import DivWdg, HtmlElement, SpanWdg, Table, Widget
from pyasm.widget import IconWdg, TextWdg

import os

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.widget import ActionButtonWdg, IconButtonWdg

from misc_wdg import QuickLinksWdg, TitleWdg



class ToolsWdg(BaseRefreshWdg):
    '''This is the welcome widget widget will appear on creation of a new
    project
    '''

    def get_args_keys(my):
        return {
        }


    def get_section_wdg(my, title, description, image, behavior):

        section_wdg = DivWdg()
        section_wdg.set_round_corners()
        section_wdg.add_border()
        section_wdg.add_style("width: 200px")
        section_wdg.add_style("height: 215px")
        section_wdg.add_style("overflow: hidden")
        section_wdg.add_style("margin: 10px")
        #section_wdg.set_box_shadow("2px 2px 2px 2px")
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

        shadow_color = section_wdg.get_color("shadow")

        section_wdg.add_behavior( {
        'type': 'click',
        'cbjs_action': '''
        bvr.src_el.setStyle("box-shadow", "0px 0px 5px %s");
        ''' % shadow_color
        } )
        section_wdg.add_behavior( {
        'type': 'mouseout',
        'cbjs_action': '''
        bvr.src_el.setStyle("box-shadow", "0px 0px 15px %s");
        ''' % shadow_color
        } )





        desc_div = DivWdg()
        desc_div.add(description)
        desc_div.add_style("padding: 5px 10px 10px 10px")
        desc_div.add_style("font-size: 1.1em")

        div = DivWdg()
        section_wdg.add(div)
        div.add_style("padding: 3px")
        div.add_style("margin: 10px")
        #div.add_style("width: 209px")
        div.add_style("height: 64px")
	div.add_style("text-align: center")
        div.add(image)
	#div.set_box_shadow("1px 1px 1px 1px")
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

        #top.add_behavior( {
        #    'type': 'load',
        #    'cbjs_action': '''
        #    spt.named_events.fire_event("side_bar|hide_now", {} );
        #    '''
        #} )


        project = Project.get()

        title = TitleWdg(title='Tools')
        top.add(title)


        shelf = DivWdg()
        top.add(shelf)
        shelf.add_style("margin-left: -8px")
        shelf.add_style("width: 130px")

        button_div = DivWdg()
        shelf.add(button_div)
        button_div.add_style("float: left")
        button_div.add_style("margin-top: -3px")

        """
        security = Environment.get_security()
        view_side_bar = security.check_access("builtin", "view_side_bar", "allow", default='allow')
        if view_side_bar:
            button = IconButtonWdg(title="Side Bar", icon=IconWdg.ARROW_LEFT)
            button_div.add(button)
            shelf.add("Toggle Side Bar")
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
                    'view': 'table',
                    'keywords': keywords,
                    'simple_search_view': 'simple_search',
                    //'show_shelf': false,
                }
                spt.tab.set_main_body_tab();
                spt.tab.add_new("Search Results", "Search Results", class_name, kwargs);
            }
        '''


        from tactic.ui.input import TextInputWdg, LookAheadTextInputWdg
        #text = TextInputWdg(name="search")
        text = LookAheadTextInputWdg(name="search", custom_cbk=custom_cbk)
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
                'view': 'table',
                'keywords': keywords,
                'simple_search_view': 'simple_search',
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



        td = table.add_cell()
        td.add_style("vertical-align: top")
        td.add_style("padding: 3px")
        title = "Themes"
        image = "<img src='/context/icons/64x64/dashboard_64.png'/>"
        description = '''Themes define the look and feel of a project.'''

        behavior = {
        'type': 'click_up',
        'cbjs_action': '''
        var class_name = 'tactic.ui.startup.themes_wdg.ThemesWdg';
        var kwargs = {
            help_alias: 'project-startup-dashboards'
            };
        spt.tab.set_main_body_tab();
        spt.tab.add_new("themes", "Themes", class_name, kwargs);
        '''
        }
        dashboard_wdg = my.get_section_wdg(title, description, image, behavior)
        td.add(dashboard_wdg)





        td = table.add_cell()
        td.add_style("vertical-align: top")
        td.add_style("padding: 3px")
        title = "Dashboards"
        image = "<img src='/context/icons/64x64/dashboard_64.png'/>"
        description = '''Dashboards display key project data in single views. Drill down further to work on tasks, make status changes or add notes.'''


        # read the config file
        #from pyasm.widget import WidgetConfig
        #tmp_path = __file__
        #dir_name = os.path.dirname(tmp_path)
        #file_path="%s/../config/dashboard-conf.xml" % (dir_name)
        #config = WidgetConfig.get(file_path=file_path, view="definition")



        # FIXME: this bypasses the link security 
        #element_name = "dashboards"
        #attrs = config.get_element_attributes(element_name)
        #dashboard_data = {}
        #kwargs = config.get_display_options(element_name)
        #class_name = kwargs.get('class_name')

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
        dashboard_wdg = my.get_section_wdg(title, description, image, behavior)
        td.add(dashboard_wdg)





        td = table.add_cell()
        td.add_style("padding: 3px")
        td.add_style("vertical-align: top")
        title = "Reports"
        image = "<img src='/context/icons/64x64/report_64.png'/>"
        description = '''TACTIC provides a number of predefined reports that project managers can access instantly to get real-time analytics.'''


        behavior = {
        'type': 'click_up',
        'cbjs_action': '''
        var class_name = 'tactic.ui.startup.reports_wdg.ReportsWdg';
        var kwargs = {};
        spt.tab.set_main_body_tab();
        spt.tab.add_new("reports", "Reports", class_name, kwargs);
        //spt.panel.load_popup("Reports", class_name, kwargs);
        '''
        }

        side_bar_wdg = my.get_section_wdg(title, description, image, behavior)
        td.add(side_bar_wdg)








        td = table.add_cell()
        td.add_style("padding: 3px")
        td.add_style("vertical-align: top")
        title = "Lists of Items"
        description = '''View all of the lists items for this project<br/><br/>
        '''
        image = "<img src='/context/icons/48x48/search_type_48.png'/>"
        #image = "<img src='/context/images/getting_started_pipeline.png'/>"
        behavior = {
        'type': 'click_up',
        'cbjs_action': '''
        spt.tab.set_main_body_tab();
        var class_name = 'tactic.ui.startup.HomeWdg';
        var kwargs = {};
        spt.tab.add_new("lists", "Lists", class_name, kwargs);
        '''
        }
        config_wdg = my.get_section_wdg(title, description, image, behavior)
        td.add(config_wdg)




        tr, td = table.add_row_cell()
        td.add_style("font-size: 14px")
        td.add("<br/>"*2)


        quick_links_wdg = QuickLinksWdg()
        td.add(quick_links_wdg)


        return top



    def get_totals_wdg(my):
        div = DivWdg()
        

        div.add("Number of Pipelines: 3<br/>") 
        div.add("Number of Search Types: 6<br/>") 
        div.add("Number of Naming Conventions: 4<br/>") 
        div.add("Number of Triggers: 8<br/>") 


        return div



class ExamplesWdg(ToolsWdg):
    pass

class ContentCreatorWdg(ToolsWdg):
    pass




