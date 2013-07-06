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

__all__ = ['HomeWdg']

from pyasm.common import Environment, Common
from pyasm.biz import Project
from pyasm.search import Search
from pyasm.web import DivWdg, HtmlElement, SpanWdg, Table, Widget
from pyasm.widget import IconWdg, ThumbWdg

from tactic.ui.widget import SingleButtonWdg

import os

from tactic.ui.common import BaseRefreshWdg

class HomeWdg(BaseRefreshWdg):

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
        desc_div.add_style("padding: 0px 10px 10px 5px")


        div = DivWdg()
        section_wdg.add(div)
        div.add_style("padding: 3px")
        div.add_style("margin: 5px")
        #div.add_style("width: 210px")
        #div.add_style("height: 170px")
        #div.add_style("width: 80px")
        div.add_style("height: 50px")
        div.add_style("float: left")
        div.add(image)
        section_wdg.add(desc_div)
        div.add_style("overflow: hidden")

        section_wdg.add_behavior( behavior )
        section_wdg.add_class("hand")

        return section_wdg



    def get_section_wdg2(my, title, description, image, behavior):

        section_wdg = DivWdg()
        section_wdg.set_round_corners()
        section_wdg.add_border()
        section_wdg.add_style("width: 200px")
        section_wdg.add_style("height: 175px")
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
        #div.add_style("width: 210px")
        #div.add_style("height: 170px")
        div.add_style("width: 105px")
        div.add_style("height: 85px")
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
        #top.add_style("height: 550px")

        top.add_class("spt_reports_top")


        title = DivWdg()
        title.add("Searchable Lists")
        title.add_style("font-size: 18px")
        title.add_style("font-weight: bold")
        title.add_style("text-align: center")
        title.add_style("padding: 10px")
        title.add_style("margin: -10px -10px 0px -10px")

        top.add(title)
        title.add_gradient("background", "background3", 5, -10)
        top.add("<br/>")

        button_div = DivWdg()
        top.add(button_div)
        button = SingleButtonWdg(title="Collapse", icon=IconWdg.ARROW_UP)
        button_div.add(button)
        top.add(button_div)
        button.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_reports_top");
            var element = top.getElement(".spt_reports_list");
            spt.toggle_show_hide(element)

            '''
        } )

        #desc = DivWdg()
        #top.add(desc)
        #desc.add("Dashboard")
        #desc.add_style("width: 600px")

        reports = []

        # read the config file
        """
        from pyasm.widget import WidgetConfig
        tmp_path = __file__
        dir_name = os.path.dirname(tmp_path)
        file_path="%s/../config/reports-conf.xml" % (dir_name)
        config = WidgetConfig.get(file_path=file_path, view="definition")
        element_names = config.get_element_names()

        for element_name in element_names:
            print "element_name: ", element_name
            attrs = config.get_element_attributes(element_name)
            report_data = {}
            kwargs = config.get_display_options(element_name)
            class_name = kwargs.get('class_name')

            report_data['class_name'] = class_name
            report_data['kwargs'] = kwargs
            report_data['title'] = attrs.get("title")
            report_data['description'] = attrs.get("description")

            reports.append(report_data)
        """

        project = Project.get()
        project_code = project.get_code()
        search_type_objs = project.get_search_types()

        filtered = [] 
        for search_type_obj in search_type_objs:
            search_type = search_type_obj.get_value("search_type")

            # FIXME: this code is also present 
            from pyasm.security import get_security_version
            security_version = get_security_version()
            if security_version >= 2 and not search_type.startswith("sthpw/") and not search_type.startswith("config/"):
                security = Environment.get_security()

                table = search_type_obj.get_value("table_name")

                default = "deny"
                key  = { "element": "%s_list" % table }
                key2 = { "element": "%s_list" % table, "project": project_code }
                key3 = { "element": "*" }
                key4 = { "element": "*", "project": project_code }
                keys = [key, key2, key3, key4]
                if not security.check_access("link", keys, "view", default=default):
                    continue

                key = { "code": search_type }
                key2 = { "code": "*" }
                keys = [key, key2]
                if not security.check_access("search_type", keys, "view", default=default):
                    continue
                

                filtered.append(search_type_obj)


        search_type_objs = filtered

        for search_type_sobj in search_type_objs:
            description = search_type_sobj.get_value("description")
            search_type = search_type_sobj.get_value("search_type")



            search = Search(search_type)
            count = search.get_count()

            title_div = DivWdg()
            items_div = DivWdg()
            title_div.add(items_div)
            items_div.add_style("font-size: 9px")
            items_div.add_style("font-weight: italic")
            items_div.add_style("float: right")
            items_div.add("%s item/s" % count)
            title_div.add(search_type_sobj.get_title())

            description_div = DivWdg()
            description_div.add(description)
            description_div.add_style("padding: 5px")
            if not description:
                description_div.add("<br/>(No description)")
                description_div.add_style("font-style: italic")
                description_div.add_style("opacity: 0.3")


            report_data = {
                'title': search_type_sobj.get_title(),
                'title_wdg': title_div,
                'class_name': 'tactic.ui.panel.ViewPanelWdg',
                'kwargs': {
                        'search_type': search_type,
                        'view': 'table',
                        'simple_search_view': 'simple_search'
                    },
                'description': description_div,
                'search_type': search_type_sobj
            }
            reports.append(report_data)


        # create a bunch of panels
        list_div = DivWdg()
        top.add(list_div)
        list_div.add_class("spt_reports_list")


        table = Table()
        list_div.add(table)
        table.add_color("color", "color")
        table.add_style("margin-bottom: 5px")
        table.center()

        top.add("<br clear='all'/>")


        for i, report in enumerate(reports):

            if i == 0 or i%4 == 0:
                tr = table.add_row()

            td = table.add_cell()
            td.add_style("vertical-align: top")
            td.add_style("padding: 3px")

            class_name = report.get("class_name")
            kwargs = report.get("kwargs")
            title = report.get("title")
            description = report.get("description")

            #image = "<img src='/context/images/getting_started_schema.png'/>"
            image = "<img src='/context/images/getting_started_pipeline.png'/>"


            thumb_div = DivWdg()
            image = thumb_div
            thumb_div.add_border()
            thumb_div.set_box_shadow("1px 1px 1px 1px")

            thumb = ThumbWdg()
            thumb_div.add(thumb)
            thumb.set_sobject(report.get("search_type"))
            thumb.set_icon_size(60)




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
            title_wdg = report.get("title_wdg")
            schema_wdg = my.get_section_wdg(title_wdg, description, image, behavior)
            td.add(schema_wdg)



        from tactic.ui.container import TabWdg
        tab = TabWdg(show_add=False)
        top.add(tab)



        return top



    def get_totals_wdg(my):
        div = DivWdg()

        div.add("Number of Pipelines: 3<br/>") 
        div.add("Number of Search Types: 6<br/>") 
        div.add("Number of Naming Conventions: 4<br/>") 
        div.add("Number of Triggers: 8<br/>") 


        return div




