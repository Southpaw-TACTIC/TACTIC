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

__all__ = ['ReportsWdg']

from pyasm.common import Environment, Common, Xml
from pyasm.search import Search, SearchType
from pyasm.web import DivWdg, HtmlElement, SpanWdg, Table, Widget
from pyasm.widget import IconWdg, ThumbWdg
from pyasm.biz import Project

import os

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.widget import SingleButtonWdg, IconButtonWdg
from tactic.ui.container import Menu, MenuItem, SmartMenu

class ReportsWdg(BaseRefreshWdg):
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
        section_wdg.add_class("spt_report_top")
        section_wdg.add_style("width: 200px")
        section_wdg.add_style("height: 100px")
        section_wdg.add_style("overflow: hidden")
        section_wdg.add_style("margin: 10px")
        section_wdg.set_box_shadow("0px 0px 10px")

        title_wdg = DivWdg()
        section_wdg.add(title_wdg)
        title_wdg.add(title)
        title_wdg.add_style("height: 20px")
        title_wdg.add_style("padding: 3px")
        title_wdg.add_style("margin-top: 3px")
        title_wdg.add_style("font-weight: bold")
        title_wdg.add_gradient("background", "background")


        button = IconButtonWdg(title="Options", icon=IconWdg.ARROWHEAD_DARK_DOWN)
        title_wdg.add(button)
        button.add_style("float: right")

        # set up menus
        menu = my.get_menu()
        SmartMenu.add_smart_menu_set( button, { 'MENU_ITEM': menu } )
        SmartMenu.assign_as_local_activator( button, "MENU_ITEM", True )


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



    def get_menu(my):
        menu = Menu(width=180)
        menu_item = MenuItem(type='title', label='Actions')
        menu.add(menu_item)


        menu_item = MenuItem(type='action', label='View')
        menu_item.add_behavior( {
            'cbjs_action': '''
            var activator = spt.smenu.get_activator(bvr);
            var report_top = activator.getParent(".spt_report_top");
            var kwargs = report_top.kwargs;
            var class_name = report_top.class_name;
            var element_name = report_top.element_name;

            spt.tab.set_main_body_tab();
            spt.tab.add_new(element_name, element_name, class_name, kwargs);
            '''
        } )
        menu.add(menu_item)



        menu_item = MenuItem(type='action', label='Show Definition')
        menu_item.add_behavior( {
            'cbjs_action': '''
            var activator = spt.smenu.get_activator(bvr);
            var report_top = activator.getParent(".spt_report_top");
            var xml = report_top.xml;
            console.log(xml);
            alert(xml);
            '''
        } )
        menu.add(menu_item)


        menu_item = MenuItem(type='separator')
        menu.add(menu_item)


        menu_item = MenuItem(type='action', label='Add to Side Bar')
        menu_item.add_behavior( {
            'cbjs_action': '''
            var activator = spt.smenu.get_activator(bvr);
            var top = activator.getParent(".spt_tab_top");
            spt.tab.top = top;

            var header = activator;
            var title = header.getAttribute("spt_title");

            var report_top = activator.getParent(".spt_report_top");
            var kwargs = report_top.kwargs;
            var class_name = report_top.class_name;
            var element_name = report_top.element_name;

            var element_name = element_name.replace(/ /g, "_");
            element_name = element_name.replace(/\//g, "_");

            var kwargs = {
                class_name: 'LinkWdg',
                display_options: kwargs,
                element_attrs: {
                    title: title
                }
            }

            try {
                spt.app_busy.show("Adding Side Bar Link ["+element_name+"]");
                var server = TacticServerStub.get();
                server.start({description:"Added Side Bar Link ["+element_name+"]"});
                var info = server.add_config_element("SideBarWdg", "definition", element_name, kwargs);
                var info = server.add_config_element("SideBarWdg", "project_view", element_name, {});

                server.finish();
                spt.panel.refresh("side_bar");
                spt.app_busy.hide();
            }
            catch(e) {
                server.abort();
                alert(e);
                spt.app_busy.hide();
                throw(e);
            }

            '''
        } )
        menu.add(menu_item)

        return menu




    def get_display(my):

        top = DivWdg()
        top.add_border()
        top.add_style("padding: 10px")
        top.add_color("color", "color")
        top.add_gradient("background", "background", 0, -5)
        #top.add_style("height: 550px")

        top.add_class("spt_reports_top")
        my.set_as_panel(top)

        inner = DivWdg()
        top.add(inner)


        title = DivWdg()
        title.add("Reports")
        title.add_style("font-size: 18px")
        title.add_style("font-weight: bold")
        title.add_style("text-align: center")
        title.add_style("padding: 10px")
        title.add_style("margin: -10px -10px 0px -10px")

        inner.add(title)
        title.add_gradient("background", "background3", 5, -10)


        from tactic.ui.widget import TitleWdg
        subtitle = TitleWdg(name_of_title='List of Built in Reports',help_alias='main')
        inner.add(subtitle)
        inner.add("<br/>")

        button_div = DivWdg()
        inner.add(button_div)
        button_div.add_class("spt_buttons_top")
        button_div.add_style("margin-top: -5px")
        button_div.add_style("margin-bottom: 30px")
        button_div.add_border()

        button_div.add_style("margin-top: -15px")
        button_div.add_style("margin-bottom: 0px")
        button_div.add_style("width: 100%")
        button_div.add_style("height: 33px")
        button_div.add_color("background", "background2")
        button_div.add_style("margin-left: auto")
        button_div.add_style("margin-right: auto")


        button = SingleButtonWdg(title="Collapse", icon=IconWdg.HOME)
        button_div.add(button)
        button.add_style("float: left")
        button.add_style("left: 5px")
        button.add_style("top: 5px")


        # FIXME: get home for the user
        #home = 'tactic.ui.startup.ContentCreatorWdg'
        home = 'tactic.ui.startup.MainWdg'


        button.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            spt.tab.set_main_body_tab();
            var class_name = 'tactic.ui.startup.MainWdg';
            var kwargs = {
                help_alias: 'main'
                };
            spt.tab.add_new("_startup", "Startup", class_name, kwargs);

            '''
        } )



        """
        button = SingleButtonWdg(title="Collapse", icon=IconWdg.ARROW_UP)
        button_div.add(button)
        button.add_class("spt_collapse")
        inner.add(button_div)
        button.add_style("float: left")
        button.add_style("left: 5px")
        button.add_style("top: 5px")

        button.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_reports_top");
            var element = top.getElement(".spt_reports_list");

            var buttons = bvr.src_el.getParent(".spt_buttons_top");
            expand = buttons.getElement(".spt_expand");
            new Fx.Tween(element).start('margin-top', "-400px");
            expand.setStyle("display", "");
            bvr.src_el.setStyle("display", "none");
            '''
        } )

        button = SingleButtonWdg(title="Expand", icon=IconWdg.ARROW_DOWN)
        button.add_style("display: none")
        button.add_class("spt_expand")
        button_div.add(button)
        button.add_style("left: 5px")
        button.add_style("top: 5px")
        inner.add(button_div)
        button.add_style("float: left")
        button.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_reports_top");
            var element = top.getElement(".spt_reports_list");

            var buttons = bvr.src_el.getParent(".spt_buttons_top");
            collapse = buttons.getElement(".spt_collapse");
            new Fx.Tween(element).start('margin-top', "0px");
            collapse.setStyle("display", "");
            bvr.src_el.setStyle("display", "none");
            '''
        } )
        """



        reports = []

        # read the config file
        from pyasm.widget import WidgetConfig
        tmp_path = __file__
        dir_name = os.path.dirname(tmp_path)
        file_path="%s/../config/reports-conf.xml" % (dir_name)
        config = WidgetConfig.get(file_path=file_path, view="definition")

        category = my.kwargs.get('category')

        # get all of the configs from the database
        if not category or category in ["custom_reports", "custom_charts"]:
            search = Search("config/widget_config")
            search.add_op("begin")
            if category == "custom_reports":
                search.add_filter("widget_type", "report")
            elif category == "custom_charts":
                search.add_filter("widget_type", "chart")
            elif not category:
                search.add_filters("widget_type", ["chart","report"])

            search.add_op("or")
            db_configs = search.get_sobjects()
        else:
            db_configs = []


        element_names = my.kwargs.get("element_names")
        if element_names is None:
            element_names = config.get_element_names()



        project = Project.get()

        for element_name in element_names:
            key = {'project': project.get_code(), 'element': element_name}
            key2 = {'project': project.get_code(), 'element': '*'}
            key3 = {'element': element_name}
            key4 = {'element': '*'}
            keys = [key, key2, key3, key4]
            if not top.check_access("link", keys, "view", default="deny"):
                continue

            attrs = config.get_element_attributes(element_name)
            report_data = {}
            kwargs = config.get_display_options(element_name)
            class_name = kwargs.get('class_name')

            # the straight xml definition contains the sidebar class_name
            # with LinkWdg ... we shouldn't use this, so build the
            # element from scratch
            #xml = config.get_element_xml(element_name)
            from pyasm.search import WidgetDbConfig
            xml = WidgetDbConfig.build_xml_definition(class_name, kwargs)

            report_data['class_name'] = class_name
            report_data['kwargs'] = kwargs
            report_data['title'] = attrs.get("title")
            report_data['description'] = attrs.get("description")
            report_data['image'] = attrs.get("image")
            report_data['xml'] = xml

            reports.append(report_data)



        for db_config in db_configs:
            element_name = db_config.get_value("view")
            key = {'project': project.get_code(), 'element': element_name}
            key2 = {'project': project.get_code(), 'element': '*'}
            key3 = {'element': element_name}
            key4 = {'element': '*'}
            keys = [key, key2, key3, key4]
            if not top.check_access("link", keys, "view", default="deny"):
                continue

            report_data = {}
            view = db_config.get_value("view")
            kwargs = {
                'view': view
            }
            parts = view.split(".")
            title = Common.get_display_title(parts[-1])

            xml = db_config.get_value("config")

            report_data['class_name'] = "tactic.ui.panel.CustomLayoutWdg"
            report_data['kwargs'] = kwargs
            report_data['title'] = title
            report_data['description'] = title
            report_data['image'] = None
            report_data['xml'] = xml
            report_data['widget_type'] = db_config.get_value("widget_type")
            if report_data['widget_type'] == 'report':
                report_data['category'] = "custom_reports"
            elif report_data['widget_type'] == 'chart':
                report_data['category'] = "custom_charts"


            reports.append(report_data)





        """
        report_data = {
            'title': 'Tasks Completed This Week',
            'class_name': 'tactic.ui.panel.ViewPanelWdg',
            'kwargs': {
                    'search_type': 'sthpw/task',
                    'view': 'table'
                },
        }
        reports.append(report_data)
        """
        if category == 'list_item_reports' or not category:
            search_types = Project.get().get_search_types()
            for search_type in search_types:
                base_key = search_type.get_base_key()

                key = {'project': project.get_code(), 'code': base_key}
                key2 = {'project': project.get_code(), 'code': '*'}
                key3 = {'code': base_key}
                key4 = {'code': '*'}
                keys = [key, key2, key3, key4]
                if not top.check_access("search_type", keys, "view", default="deny"):
                    continue


                if not SearchType.column_exists(base_key, "pipeline_code"):
                    continue

                thumb_div = DivWdg()
                image = thumb_div
                thumb_div.add_border()
                thumb_div.set_box_shadow("1px 1px 1px 1px")
                thumb_div.add_style("width: 60px")

                thumb = ThumbWdg()
                thumb_div.add(thumb)
                thumb.set_sobject(search_type)
                thumb.set_icon_size(60)

                report_data = {
                    'title': '%s Workflow Status' % search_type.get_title(),
                    'description': 'Number of items in each process',
                    'class_name': 'tactic.ui.report.stype_report_wdg.STypeReportWdg',
                    'kwargs': {
                        'search_type': base_key
                    },
                    'image': thumb_div
                }
                reports.append(report_data)

 
                report_data = {
                    'title': '%s Labor Cost Report' % search_type.get_title(),
                    'description': 'Labor Cost Breakdown for each Item',
                    'class_name': 'tactic.ui.panel.ViewPanelWdg',
                    'kwargs': {
                        'search_type': search_type.get_code(),
                        'view': "table",
                        'show_header': False,
                        'mode': 'simple',
                        'element_names': "preview,code,title,cost_breakdown,bid_hours,bid_cost,actual_hours,actual_cost,overbudget,variance"
                    },
                    'image': IconWdg("", IconWdg.REPORT_03)
                }
                reports.append(report_data)



        table2 = Table()
        inner.add(table2)
        table2.add_style("width: 100%")


        categories_div = DivWdg()
        td = table2.add_cell(categories_div)
        td.add_style("vertical-align: top")
        td.add_style("width: 200px")
        td.add_color("background", "background3")
        td.add_border()

        #categories_div.add_style("margin: -1px 0px 0px -1px")
        categories_div.add_style("padding-top: 10px")
        #categories_div.add_style("float: left")
        categories_div.add_color("color", "color3")


        categories = config.get_all_views()
        categories.insert(-1, "list_item_reports")
        categories.insert(-1, "custom_charts")
        categories.insert(-1, "custom_reports")

        table_div = DivWdg()
        td = table2.add_cell(table_div)
        td.add_style("vertical-align: top")
        table_div.add_class("spt_reports_list")
        table_div.add_border()
        table_div.add_color("background", "background", -5)

        table_div.add_style("min-height: 500px")



        for i, category in enumerate(categories):

            if i == len(categories) - 1:
                categories_div.add("<hr/>")


            config.set_view(category)
            element_names = config.get_element_names()

            if category == "definition":
                title = "All Reports"
            else:
                title = Common.get_display_title(category)


            category_div = DivWdg()
            categories_div.add(category_div)
            category_div.add(title)
            category_div.add_style("padding: 5px")
            category_div.add_class("hand")

            category_div.add_behavior( {
            'type': 'click_up',
            'category': category,
            'element_names': element_names,
            'class_name': Common.get_full_class_name(my),
            'cbjs_action': '''
            var kwargs = {
                is_refresh: true,
                category: bvr.category,
                element_names: bvr.element_names
            }

            //spt.panel.refresh(top, kwargs);
            var top = bvr.src_el.getParent(".spt_reports_top");
            spt.panel.load(top, bvr.class_name, kwargs);
            '''
            } )

            bgcolor = category_div.get_color("background3", -10)
            category_div.add_behavior( {
            'type': 'mouseover',
            'bgcolor': bgcolor,
            'cbjs_action': '''
            bvr.src_el.setStyle("background", bvr.bgcolor);
            '''
            } )
            category_div.add_behavior( {
            'type': 'mouseout',
            'bgcolor': bgcolor,
            'cbjs_action': '''
            bvr.src_el.setStyle("background", "");
            '''
            } )








        # create a bunch of panels
        table = Table()
        table_div.add(table)
        table.add_color("color", "color")
        table.add_style("margin-top: 20px")
        table.center()
        table_div.add_style("margin: -3px -3px -1px -2px")


        if not reports:
            tr = table.add_row()
            td = table.add_cell()
            td.add("There are no reports defined.")
            td.add_style("padding: 50px")

            if my.kwargs.get("is_refresh") in ['true', True]:
                return inner
            else:
                return top



        for i, report in enumerate(reports):

            #if i == 0 or i%4 == 0:
            if i%3 == 0:
                tr = table.add_row()

            td = table.add_cell()
            td.add_style("vertical-align: top")
            td.add_style("padding: 3px")
            title = report
            #description = '''The schema is used to layout the basic components of your project.  Each component represents a list of items that you use in your business everyday.'''

            description = report.get("title")

            # Each node will contain a list of "items" and will be stored as a table in the database.'''

            class_name = report.get("class_name")
            kwargs = report.get("kwargs")
            title = report.get("title")
            description = report.get("description")
            widget_type = report.get("widget_type")

            image = report.get("image")
            icon = report.get("icon")
            xml = report.get("xml")

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
                """
                import random
                num = random.randint(0,3)
                if num == 1:
                    image = IconWdg("Bar Chart", IconWdg.GRAPH_BAR_01)
                elif num == 2:
                    image = IconWdg("Bar Chart", IconWdg.GRAPH_LINE_01)
                else:
                    image = IconWdg("Bar Chart", IconWdg.GRAPH_BAR_02)
                """

                if widget_type == "chart":
                    image = IconWdg("Chart", IconWdg.GRAPH_BAR_02)
                else:
                    image = IconWdg("No Image", IconWdg.WARNING)
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

            spt.tab.set_main_body_tab();
            //var top = bvr.src_el.getParent(".spt_reports_top");
            //spt.tab.set_tab_top(top);
            spt.tab.add_new(bvr.title, bvr.title, bvr.class_name, bvr.kwargs);
            '''
            }
            schema_wdg = my.get_section_wdg(title, description, image, behavior)

            schema_wdg.add_behavior( {
            'type': 'load',
            'title': title,
            'class_name': class_name,
            'xml': xml,
            'kwargs': kwargs,
            'cbjs_action': '''
                var report_top = bvr.src_el;
                report_top.kwargs = bvr.kwargs;
                report_top.class_name = bvr.class_name;
                report_top.element_name = bvr.title;
                report_top.xml = bvr.xml;
            '''
            } )

            td.add(schema_wdg)


        inner.add("<br/>")



        #from tactic.ui.container import TabWdg
        #tab = TabWdg(show_add=False)
        #inner.add(tab)

        if my.kwargs.get("is_refresh") in ['true', True]:
            return inner
        else:
            return top


__all__.append("BigTableTest")
class BigTableTest(BaseRefreshWdg):

    def get_display(my):
        top = my.top
        top.add_class("top")

        top.add( '''

<table style=''>
<tr>
<th class='first' style='width: 250px; background: #0F0'>Header</th>
<th class='second' style='width: 250px; background: #0F0'>Header</th>
</tr>
</table>

<div class='div' style='overflow-y: hidden'>
<table class='content' style='margin-top: -10px'>
<tbody style='background: #F00'>
<tr>
<td class='first' style='width: 250px'>horse !!!! horse !!!! horse !!!!</td>
<td class='second' style='width: 250px'>horse</td>
</tr>
<tr><td>cow</td></tr>
<tr><td>pig</td></tr>
<tr><td>chicken</td></tr>
<tr><td>goat</td></tr>
</tbody>
</table>
</div>
        ''')

        for x in ['first', 'second']:
            top.add_relay_behavior( {
                'type': 'mouseup',
                'bvr_match_class': x,
                'cbjs_action': '''
                var top = bvr.src_el.getParent(".top");
                var headers = top.getElements("." + bvr.bvr_match_class);

                var header = bvr.src_el;
                var width = header.getStyle("width");
                console.log("width: " + width);
                width = width.replace("px", "");
                width = parseInt(width);
                width = width - 5;
                console.log("width: " + width);

                for (var i = 0; i < headers.length; i++) {
                    headers[i].setStyle("width", width);
                }
                '''
            } )



        top.add_behavior( {
            'type': 'wheel',
            'cbjs_action': '''
            var content = bvr.src_el.getElement(".content");
            var margin = content.getStyle("margin-top");
            margin = margin.replace("px", "");
            margin = parseInt(margin);
            if (evt.wheel < 0) {
                margin += -10;
            }
            else {
                margin -= -10;
            }

            if (margin > 0) {
                margin = 0;
            }
            content.setStyle("margin-top", margin);


            '''
        } )



        return top


