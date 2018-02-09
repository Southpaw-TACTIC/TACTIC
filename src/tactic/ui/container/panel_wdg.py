###########################################################
#
# Copyright (c) 2016, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#

__all__ = ['PanelWdg', 'UserPageSelectWdg', 'UserPageCreatorWdg', 'UserPageCreatorCmd']

import tacticenv

from pyasm.common import Common, Xml, Environment
from pyasm.search import Search, SObject, SearchType
from pyasm.web import DivWdg
from pyasm.widget import WidgetConfig
from pyasm.command import Command

from tactic.ui.container import SmartMenu
from tactic.ui.common import BaseRefreshWdg
from tactic.ui.widget import ActionButtonWdg


class PanelWdg(BaseRefreshWdg):

    def get_display(self):

        top = self.top
        top.add_class("spt_panel_layout_top")
        self.set_as_panel(top)

        inner = DivWdg()
        top.add(inner)


        self.view = self.kwargs.get("view")


        # Define some views that are pages.  Pages are views that are self
        # contained and do not require arguments.  They are often created
        # by users
        search = Search("config/widget_config")
        search.add_column("view")
        search.add_filter("category", "CustomLayoutWdg")
        search.add_filter("view", "pages.%", op="like")
        sobjects = search.get_sobjects()
        self.pages = SObject.get_values(sobjects, "view")

        config = None
        is_test = False
        if self.view:
            search = Search("config/widget_config")
            search.add_filter("category", "PanelLayoutWdg")
            search.add_filter("view", self.view)
            config = search.get_sobject()

        elif is_test:
            config_xml = '''
            <config>
            <elements>
              <element name="a">
                <display class="tactic.ui.panel.CustomLayoutWdg">
                  <view>pages.test1</view>
                </display>
              </element>

              <element name="b">
                <display class="tactic.ui.panel.StaticTableLayoutWdg">
                    <search_type>sthpw/login_group</search_type>
                    <element_names>login_group</element_names>
                    <show_shelf>false</show_shelf>
                </display>
              </element>

              <element name="c">
                <display class="tactic.ui.panel.CustomLayoutWdg">
                  <view>test.search</view>
                </display>
              </element>

     
              <element name="d">
                <display class="tactic.ui.panel.StaticTableLayoutWdg">
                    <search_type>sthpw/login_group</search_type>
                    <element_names>login_group</element_names>
                    <show_shelf>false</show_shelf>
                </display>
              </element>
            </elements>
            </config>
            '''

            config = WidgetConfig.get(view="elements", xml=config_xml)


        if not config:
            config_xml = '''
            <config>
            <elements>
            </elements>
            </config>
            '''

            config = WidgetConfig.get(view="elements", xml=config_xml)


        grid = self.kwargs.get("grid")
        if not grid:
            grid = config.get_view_attribute("grid")

        if grid:
            if isinstance(grid, basestring):
                grid = [int(x) for x in grid.split("x")]

        else:
            grid = (3,1)


        is_owner = True


        table = DivWdg() 
        inner.add(table)
        table.add_style("margin: 20px")
        table.add_style("box-sizing: border-box")


        if is_owner:
            menu = self.get_action_menu()
            #SmartMenu.add_smart_menu_set( top, { 'BUTTON_MENU': menu } )

        element_names = config.get_element_names()

        index = 0
        for y in range(grid[1]):
            row = DivWdg()
            table.add(row)
            row.add_class("row")
            row.add_style("box-sizing: border-box")

            num_cols = grid[0]
            size = 12 / num_cols

            for x in range(grid[0]):
                col = DivWdg()
                row.add(col)
                col.add_class("col-sm-%s" % size)
                col.add_style("box-sizing: border-box")
                col.add_style("overflow: auto")

                col.add_class("spt_panel_top")



                if is_owner:
                    header = DivWdg()
                    col.add(header)

                    menu_wdg = DivWdg()
                    header.add(menu_wdg)
                    menu_wdg.add_style("float: right")
                    menu_wdg.add("<i class='fa fa-bars'> </i>")
                    menu_wdg.add_class("hand")

                    SmartMenu.add_smart_menu_set( menu_wdg, { 'BUTTON_MENU': menu } )
                    SmartMenu.assign_as_local_activator( menu_wdg, "BUTTON_MENU", True )


                element = None
                title = None
                if index < len(element_names):
                    element_name = element_names[index]
                    #element_name = "%s,%s" % (x,y)

                    element = config.get_display_widget(element_name)
                    title = config.get_element_title(element_name)
                    if not title:
                        title = Common.get_display_title(element_name)

                if not element:
                    element = DivWdg()
                    element.add("No content")
                    element.add_style("height: 100%")
                    element.add_style("width: 100%")
                    element.add_style("text-align: center")
                    element.add_border()
                else:
                    try:
                        element = element.get_buffer_display()
                    except:

                        element = DivWdg()
                        element.add("No content")
                        element.add_style("height: 100%")
                        element.add_style("width: 100%")
                        element.add_style("text-align: center")
                        element.add_border()



                if is_owner:
                    if title:
                        header.add(title)
                    else:
                        header.add("Panel: %s,%s" % (x, y))
                    col.add("<hr/>")

                content = DivWdg()
                col.add(content)
                content.add_class("spt_panel_content")
                content.add_style("min-height: 200px;")


                content.add(element)


                index += 1

        if self.kwargs.get("is_refresh"):
            return inner
        else:
            return top



    def get_action_menu(self):

        from menu_wdg import Menu, MenuItem
        menu = Menu(width=180)
        menu_item = MenuItem(type='title', label='Actions')
        menu.add(menu_item)

        menu_item = MenuItem(type='action', label="Create New Page")
        menu.add(menu_item)
        menu_item.add_behavior( {
            'type': 'click',
            'cbjs_action': '''
            var class_name = 'tactic.ui.container.panel_wdg.UserPageCreatorWdg';
            var kwargs = {
            }
            spt.panel.load_popup("Page Creator", class_name, kwargs);
            '''
        } )


        login = Environment.get_user_name()
        view_filter = "pages.%s.%%" % login


        menu_item = MenuItem(type='action', label="Edit Page")
        menu.add(menu_item)
        menu_item.add_behavior( {
            'type': 'click',
            'view_filter': view_filter,
            'cbjs_action': '''
            spt.tab.set_main_body_tab();
            title = "Page Editor";
            var class_name = 'tactic.ui.tools.CustomLayoutEditWdg';
            var kwargs = {
                view_filter: bvr.view_filter
            }
            spt.tab.add_new(title, title, class_name, kwargs);
            '''
        } )



        menu_item = MenuItem(type='action', label="Reload Page")
        menu.add(menu_item)
        menu_item.add_behavior( {
            'type': 'click',
            'cbjs_action': '''
            var activator = spt.smenu.get_activator(bvr);
            var top = activator.getParent(".spt_panel_top");
            var content = top.getElement(".spt_panel_content");
            spt.panel.refresh(content);
            '''
        } )




        menu_item = MenuItem(type='action', label="Save Layout")
        menu.add(menu_item)
        menu_item.add_behavior( {
            'type': 'click',
            'view': self.view,
            'cbjs_action': '''
            var activator = spt.smenu.get_activator(bvr);
            var top = activator.getParent(".spt_panel_layout_top");

            var panels = top.getElements(".spt_panel_content");

            for (var i = 0; i < panels.length; i++) {
                var panel = panels[i];
                var content = panel.getElement(".spt_panel");
                if (content == null) {
                    continue;
                }
                var class_name = content.getAttribute("spt_class_name");
                var kwargs = spt.panel.get_element_options(content);

                element_name = "panel_" + i;

                try {
                    var server = TacticServerStub.get();
                    server.add_config_element("PanelLayoutWdg", bvr.view, element_name, { class_name: class_name, display_options: kwargs, unique: false });
                }
                catch(e) {
                    alert(e);
                    throw(e);
                }

            }

            '''
        } )



        if len(self.pages) > 5:


            menu_item = MenuItem(type='action', label='Load Page')
            menu.add(menu_item)
            menu_item.add_behavior( {
                'cbjs_action': '''
                var activator = spt.smenu.get_activator(bvr);
                var class_name = 'tactic.ui.container.panel_wdg.UserPageSelectWdg';
                var kwargs = {
                    view: bvr.page,
                }
                var popup = spt.panel.load_popup("Load Page", class_name, kwargs);
                popup.activator = activator;

                '''
            } )

            #menu_item = MenuItem(type='separator')
            #menu.add(menu_item)
        else:

            menu_item = MenuItem(type='title', label='Pages')
            menu.add(menu_item)

            for page in self.pages:
                menu_item = MenuItem(type='action', label=page)
                menu_item.add_behavior( {
                    'page': page,
                    'cbjs_action': '''
                    var activator = spt.smenu.get_activator(bvr);
                    var top = activator.getParent(".spt_panel_top");
                    var content = top.getElement(".spt_panel_content");

                    var class_name = 'tactic.ui.panel.CustomLayoutWdg';
                    var kwargs = {
                        view: bvr.page,
                    }
                    spt.panel.load(content, class_name, kwargs);

                    '''
                } )
                menu.add(menu_item)


        menu_item = MenuItem(type='title', label='Layouts')
        menu.add(menu_item)

        for item in ['1x1','2x1','3x1','4x1','1x2','2x2','3x2','4x2','Custom']:

            menu_item = MenuItem(type='action', label=item)
            menu.add(menu_item)
            menu_item.add_behavior( {
                'item': item,
                'cbjs_action': '''
                var activator = spt.smenu.get_activator(bvr);
                var top = activator.getParent(".spt_panel_layout_top");
                top.setAttribute("spt_grid", bvr.item);
                spt.panel.refresh(top);
                '''
            } )


        return menu


class UserPageSelectWdg(BaseRefreshWdg):

    def get_display(self):

        top = self.top
        top.add_style("margin: 10px")


        search = Search("config/widget_config")
        search.add_column("view")
        search.add_filter("category", "CustomLayoutWdg")
        search.add_filter("view", "pages.%", op="like")
        sobjects = search.get_sobjects()
        self.pages = SObject.get_values(sobjects, "view")


        top.add("<div style='font-size: 16px'>Select page to load</div>")
        top.add("<hr/>")



        pages_div = DivWdg()
        top.add(pages_div)
        pages_div.add_style("margin: 20px")


        pages_div.add_relay_behavior( {
            'type': 'click',
            'bvr_match_class': "spt_user_page_item",
            'cbjs_action': '''
            var popup = bvr.src_el.getParent(".spt_popup");
            var activator = popup.activator;

            var page = bvr.src_el.getAttribute("spt_page");

            var top = activator.getParent(".spt_panel_top");
            var content = top.getElement(".spt_panel_content");

            var class_name = 'tactic.ui.panel.CustomLayoutWdg';
            var kwargs = {
                view: page,
            }
            spt.panel.load(content, class_name, kwargs);

            spt.popup.close(popup);


            '''
        } )

        if self.pages:
            last_parts = self.pages[0].split(".")[:-1]


        self.pages.sort()

        last_parts = []
        for count, page in enumerate(self.pages):

            page = page.replace(".", "/")

            page_div = DivWdg()
            pages_div.add(page_div)
            page_div.add_class("spt_user_page_item")
            page_div.add_style("padding: 3px")
            page_div.add_class("tactic_hover")
            page_div.add_attr("spt_page", page)
            page_div.add_class("hand")
            page_div.add_style("min-width: 400px")


            new_parts = []
            parts = page.split("/")
            parts = parts[1:]
            index = 0
            for part in parts:
                if index < len(last_parts):
                    last_part = last_parts[index]
                    if part == last_part:
                        part = "<i style='opacity: 0.0'>%s</i>" % part

                index += 1
                new_parts.append(part)
            last_parts = parts

            #parts = ["<b>%s</b>" % x for x in parts]
            display_path = "&nbsp;&nbsp;<i style='opacity: 1.0'>/</i>&nbsp;&nbsp;".join(new_parts)

            page_div.add("<div style='margin-right: 10px;display: inline-block; width: 20px; text-align: right'>%s: </div>" % count)
            page_div.add(display_path)


        return top




class UserPageCreatorWdg(BaseRefreshWdg):

    def get_display(self):

        top = self.top
        top.add_style("width: 600px")
        top.add_style("height: 600px")
        top.add_style("margin: 20px")
        top.add_class("spt_page_creator_top")

        top.add("<div style='font-size: 16px'>Page Creator</div>")

        top.add("<hr/>")

        top.add("Name: <br/>")
        top.add("<input type='text' class='form-control spt_input' name='name'/>")
        top.add("<br/>")
        top.add("Description: <br/>")
        top.add("<input type='text' class='form-control spt_input' name='description'/>")
        top.add("<br/>")

        from tactic.ui.tools import WidgetEditorWdg
        kwargs = {
            #'display_handler': 'tactic.ui.panel.TableLayoutWdg',
            'widget_key': 'table',
            'show_action': False,
        }
        editor = WidgetEditorWdg(**kwargs)
        top.add(editor)


        top.add("<hr/>")

        button_div = DivWdg()
        top.add(button_div)
        button_div.add_style("text-align: center")
        button_div.add_style("margin: 10px 0px")

        button = ActionButtonWdg(title="Cancel", width=150)
        button_div.add(button)
        button.add_behavior( {
            'type': 'click',
            'cbjs_action': '''
            var popup = bvr.src_el.getParent(".spt_popup");
            spt.popup.close(popup);
            '''
        } )
        button.add_style("display: inline-block")

 


        button = ActionButtonWdg(title="Save Page", width=150)
        button_div.add(button)
        button.add_behavior( {
            'type': 'click',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_page_creator_top");
            var values = spt.api.get_input_values(top, null, false);

            var class_name = 'tactic.ui.container.panel_wdg.UserPageCreatorCmd';
            var server = TacticServerStub.get();
            server.execute_cmd(class_name, values);

            var popup = bvr.src_el.getParent(".spt_popup");
            spt.popup.close(popup);

            '''
        } )
        button.add_style("display: inline-block")

 
        return top


class UserPageCreatorCmd(Command):

    def execute(self):

        print "kwargs: ", self.kwargs

        options = {}
        class_name = "tactic.ui.panel.CustomLayoutWdg"
        widget_key = ""
        for key, value in self.kwargs.items():
            if value == '':
                continue

            if key.startswith("xxx_option"):
                parts = key.split("|")
                option_key = parts[1]

                if option_key == "display_class":
                    class_name = value
                elif option_key == "widget_key":
                    widget_key = value
                else:
                    options[option_key] = value

            elif key.startswith("option|"):
                parts = key.split("|")
                option_key = parts[1]
                options[option_key] = value



        print "options: ", options

        name = self.kwargs.get("name")
        description = self.kwargs.get("description") or " "

        if not name:
            raise Exception("No name provided")


        name = Common.clean_filesystem_name(name)

        login = Environment.get_user_name()
        view = "pages.%s.%s" % (login, name)


        # find if this user page already exists
        search = Search("config/widget_config")
        search.add_filter("category", "CustomLayoutWg")
        search.add_filter("view", view)
        config = search.get_sobject()

        if config:
            raise Exception("Page with name [%s] already exists" % name)


        option_xml = []
        for key, value in options.items():
            option_xml.append("<%s>%s</%s>" % (key, value, key))
        option_str = "\n".join(option_xml)


        if widget_key:
            display_line = '''<display widget="%s">''' % widget_key
        else:
            display_line = '''<display class="%s">''' % class_name



        # all pages are custom layouts
        config_xml = '''<config>
  <%s>
    <html>
    <div style="margin: 20px">
      <div style="font-size: 25px">%s</div>
      <div>%s</div>
      <hr/>
      <element>
        %s
        %s
        </display>
      </element>
    </div>
    </html>
  </%s>
</config>
        ''' % (view, name, description, display_line, option_str, view)

        print "config_xml: ", config_xml

        xml = Xml()
        xml.read_string(config_xml)
        config_xml = xml.to_string()

        config = SearchType.create("config/widget_config")
        config.set_value("category", "CustomLayoutWdg")
        config.set_value("view", view)
        config.set_value("config", config_xml)

        config.commit()











if __name__ == '__main__':

    from pyasm.security import Batch
    Batch()

    from pyasm.common import Xml
    from pyasm.web import WebContainer
    WebContainer.get_buffer()


    panel = PanelWdg()
    html = panel.get_buffer_display()
    xml = Xml()
    xml.read_string(html)
    print xml.to_string()

