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

__all__ = ['DashboardsWdg']

from pyasm.common import Environment, Common
from pyasm.search import Search
from pyasm.web import DivWdg, HtmlElement, SpanWdg, Table, Widget
from pyasm.widget import IconWdg

import os

from tactic.ui.common import BaseRefreshWdg

class DashboardsWdg(BaseRefreshWdg):
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
        section_wdg.add_style("height: 100px")
        section_wdg.add_style("overflow: hidden")
        section_wdg.add_style("margin: 5px")
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

        top.add_class("spt_reports_top")


        title = DivWdg()
        title.add("Dashboards")
        title.add_style("font-size: 18px")
        title.add_style("font-weight: bold")
        title.add_style("text-align: center")
        title.add_style("padding: 10px")
        title.add_style("margin: -10px -10px 10px -10px")
        title.add_gradient("background", "background3", 5, -10)
        top.add(title)

        from tactic.ui.widget import TitleWdg
        subtitle = TitleWdg(name_of_title='List of Dashboards',help_alias='project-startup-dashboards')
        top.add(subtitle)

        top.add("<br/>")

        dashboards = []

        # read the config file
        from pyasm.widget import WidgetConfig
        tmp_path = __file__
        dir_name = os.path.dirname(tmp_path)
        file_path="%s/../config/dashboard-conf.xml" % (dir_name)
        config = WidgetConfig.get(file_path=file_path, view="definition")
        element_names = config.get_element_names()

        
        for element_name in element_names:
            attrs = config.get_element_attributes(element_name)
            dashboard_data = {}
            kwargs = config.get_display_options(element_name)
            class_name = kwargs.get('class_name')

            dashboard_data['class_name'] = class_name
            dashboard_data['kwargs'] = kwargs
            dashboard_data['title'] = attrs.get("title")
            dashboard_data['description'] = attrs.get("description")
            dashboard_data['image'] = attrs.get("image")

            dashboards.append(dashboard_data)
        

        # create a bunch of panels
        table = Table()
        top.add(table)
        table.add_color("color", "color")
        table.add_style("margin-bottom: 20px")
        table.center()


        for i, dashboard in enumerate(dashboards):

            if i == 0 or i%4 == 0:
                tr = table.add_row()

            td = table.add_cell()
            td.add_style("vertical-align: top")
            td.add_style("padding: 3px")
            title = dashboard

            description = dashboard.get("title")

            # Each node will contain a list of "items" and will be stored as a table in the database.'''

            class_name = dashboard.get("class_name")
            kwargs = dashboard.get("kwargs")
            title = dashboard.get("title")
            description = dashboard.get("description")


 
            image = dashboard.get("image")
            icon = dashboard.get("icon")

            if image:
                div = DivWdg()
                if isinstance(image, basestring):
                    image = image.upper()
                    image = eval("IconWdg('', IconWdg.%s)" % image)
                    div.add_style("margin-left: 15px")
                    div.add_style("margin-top: 5px")
                else:
                    image = image
                div.add(image)
                image = div

            elif icon:
                icon = icon.upper()
                image = eval("IconWdg('', IconWdg.%s)" % icon)

            else:
                div = DivWdg()
                image = IconWdg("Bar Chart", IconWdg.WARNING)
                div.add_style("margin-left: 15px")
                div.add_style("margin-top: 5px")
                div.add(image)
                image = div



            behavior = {
            'type': 'click_up',
            'title': title,
            'class_name': class_name,
            'kwargs': kwargs,
            'cbjs_action': '''

            var top = bvr.src_el.getParent(".spt_reports_top");
            //spt.tab.set_main_body_tab();
            spt.tab.set_tab_top(top);
            var kwargs = {};
            spt.tab.add_new(bvr.title, bvr.title, bvr.class_name, bvr.kwargs);
            '''
            }
            schema_wdg = my.get_section_wdg(title, description, image, behavior)
            td.add(schema_wdg)



        from tactic.ui.container import TabWdg
        tab = TabWdg()
        top.add(tab)



        return top



    def get_totals_wdg(my):
        div = DivWdg()

        div.add("Number of Pipelines: 3<br/>") 
        div.add("Number of Search Types: 6<br/>") 
        div.add("Number of Naming Conventions: 4<br/>") 
        div.add("Number of Triggers: 8<br/>") 


        return div




