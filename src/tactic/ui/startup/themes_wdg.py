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

__all__ = ['ThemesWdg']

from pyasm.common import Environment, Common
from pyasm.search import Search
from pyasm.web import DivWdg, HtmlElement, SpanWdg, Table, Widget
from pyasm.widget import IconWdg

import os

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.container import Menu, MenuItem, SmartMenu

from reports_wdg import ReportsWdg
class ThemesWdg(ReportsWdg):

    def get_args_keys(my):
        return {
        }


    def get_display(my):

        top = DivWdg()
        top.add_border()
        top.add_style("padding: 10px")
        top.add_color("color", "color")
        top.add_color("background", "background")

        top.add_class("spt_reports_top")


        title = DivWdg()
        title.add("Themes")
        title.add_style("font-size: 18px")
        title.add_style("font-weight: bold")
        title.add_style("text-align: center")
        title.add_style("padding: 10px")
        title.add_style("margin: -10px -10px 10px -10px")
        title.add_gradient("background", "background3", 5, -10)
        top.add(title)

        from tactic.ui.widget import TitleWdg
        subtitle = TitleWdg(name_of_title='List of Themes',help_alias='project-startup-themes')
        top.add(subtitle)

        top.add("<br/>")

        themes = []

        # read the config file
        """
        from pyasm.widget import WidgetConfig
        tmp_path = __file__
        dir_name = os.path.dirname(tmp_path)
        file_path="%s/../config/themes-conf.xml" % (dir_name)
        config = WidgetConfig.get(file_path=file_path, view="definition")
        element_names = config.get_element_names()

        
        for element_name in element_names:
            attrs = config.get_element_attributes(element_name)
            theme_data = {}
            kwargs = config.get_display_options(element_name)
            class_name = kwargs.get('class_name')

            theme_data['class_name'] = class_name
            theme_data['kwargs'] = kwargs
            theme_data['title'] = attrs.get("title")
            theme_data['description'] = attrs.get("description")
            theme_data['image'] = attrs.get("image")

            themes.append(theme_data)
        """



        # get all of the configs from the database
        search = Search("config/widget_config")
        search.add_filter("widget_type", "theme")
        db_configs = search.get_sobjects()

        for db_config in db_configs:
            theme_data = {}
            view = db_config.get_value("view")
            kwargs = {
                'view': view
            }
            #parts = view.split(".")
            #title = Common.get_display_title(parts[-1])
            title = view
            title = title.replace(".", " ")
            title = title.replace("_", " ")
            title = Common.get_display_title(title)

            xml = db_config.get_value("config")

            theme_data['class_name'] = "tactic.ui.panel.CustomLayoutWdg"
            theme_data['kwargs'] = kwargs
            theme_data['view'] = view
            theme_data['title'] = title
            theme_data['description'] = title
            theme_data['image'] = None
            theme_data['xml'] = xml
            theme_data['widget_type'] = db_config.get_value("widget_type")

            themes.append(theme_data)




        if not themes:
            no_themes_div = DivWdg()
            top.add(no_themes_div)
            no_themes_div.add_style("margin-left: auto")
            no_themes_div.add_style("margin-right: auto")
            no_themes_div.add_style("width: 400px")
            no_themes_div.add_style("height: 50px")
            no_themes_div.add_style("text-align: center")
            no_themes_div.add_style("padding: 50px 50px")
            no_themes_div.add_style("margin-top: 100px")
            no_themes_div.add_style("margin-bottom: 100px")
            no_themes_div.add_style("font-weight: bold")
            no_themes_div.add_border()
            no_themes_div.add_color("background", "background3")


            no_themes_div.add("No themes activated in thie project")


            return top





        # create a bunch of panels
        table = Table()
        top.add(table)
        table.add_color("color", "color")
        table.add_style("margin-bottom: 20px")
        table.center()


        # get all of the /index URLs
        search = Search("config/url")
        search.add_filter("url", "/index")
        indexes = search.get_sobjects()
        current_view = None
        for index in indexes:
            widget_xml = index.get_xml_value("widget")
            current_view = widget_xml.get_value("element/display/view")
        


        for i, theme in enumerate(themes):

            if i == 0 or i%4 == 0:
                tr = table.add_row()

            td = table.add_cell()
            td.add_style("vertical-align: top")
            td.add_style("padding: 3px")

            description = theme.get("title")

            # Each node will contain a list of "items" and will be stored as a table in the database.'''

            class_name = theme.get("class_name")
            kwargs = theme.get("kwargs")
            title = theme.get("title")
            description = theme.get("description")
            xml = theme.get("xml") or ""
            view = theme.get("view")

            #if current_view == view.replace(".", "/"):
            #    td.add("CURRENT")

 
            image = theme.get("image")
            icon = theme.get("icon")

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
                #image = IconWdg("Bar Chart", IconWdg.WARNING)
                image = IconWdg("Bar Chart", IconWdg.DASHBOARD_02)
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
            spt.tab.set_main_body_tab();
            //spt.tab.set_tab_top(top);
            var kwargs = {};
            spt.tab.add_new(bvr.title, bvr.title, bvr.class_name, bvr.kwargs);
            '''
            }
            schema_wdg = my.get_section_wdg(title, description, image, behavior)


            schema_wdg.add_behavior( {
            'type': 'load',
            'title': title,
            'class_name': class_name,
            'view': view,
            'xml': xml,
            'kwargs': kwargs,
            'cbjs_action': '''
                var report_top = bvr.src_el;
                report_top.kwargs = bvr.kwargs;
                report_top.class_name = bvr.class_name;
                report_top.element_name = bvr.title;
                report_top.view = bvr.view;
                report_top.xml = bvr.xml;
            '''
            } )

            td.add(schema_wdg)



        #from tactic.ui.container import TabWdg
        #tab = TabWdg(show_add=False)
        #top.add(tab)



        return top



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
            alert(xml);
            '''
        } )
        menu.add(menu_item)


        menu_item = MenuItem(type='separator')
        menu.add(menu_item)



        widget_def = '''
<element name='index' palette="BLACK">
  <display class='tactic.ui.panel.CustomLayoutWdg'>
    <view>VIEW</view>
  </display>
</element>
        '''


        menu_item = MenuItem(type='action', label='Set as Project Theme')
        menu_item.add_behavior( {
            'type': 'click_up',
            'widget_def': widget_def,
            'cbjs_action': '''
            var activator = spt.smenu.get_activator(bvr);
            var report_top = activator.getParent(".spt_report_top");
            var kwargs = report_top.kwargs;
            var class_name = report_top.class_name;
            var element_name = report_top.element_name;
            var view = report_top.view;

            if (!confirm("Change theme to ["+view+"]?")) {
                return;
            }

            var widget_def = bvr.widget_def;
            widget_def = widget_def.replace(/VIEW/, view);

            var data = {
                url: '/index',
                description: 'Index Page',
                widget: widget_def
            }

            var server = TacticServerStub.get();
            var url = server.eval("@SOBJECT(config/url['url','/index'])", {single:true});
            if (url) {
                server.update(url, data);
            }
            else {
                server.insert('config/url', data);
            }

            '''
        } )
        menu.add(menu_item)

        return menu

