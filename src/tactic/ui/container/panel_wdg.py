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

import tacticenv

from pyasm.search import Search, SObject
from pyasm.web import DivWdg

from tactic.ui.container import SmartMenu
from tactic.ui.common import BaseRefreshWdg


class PanelWdg(BaseRefreshWdg):

    def get_display(my):

        top = my.top
        top.add_class("spt_panel_layout_top")
        my.set_as_panel(top)

        inner = DivWdg()
        top.add(inner)


        grid = my.kwargs.get("grid")
        if grid:
            if isinstance(grid, basestring):
                grid = [int(x) for x in grid.split("x")]
        else:
            grid = (4,2)

        view = my.kwargs.get("view")


        # Define some views that pages.  Pages are views that are self
        # contained and do not require arguments.  They are often created
        # by users
        search = Search("config/widget_config")
        search.add_column("view")
        search.add_filter("category", "CustomLayoutWdg")
        search.add_filter("view", "pages.%", op="like")
        sobjects = search.get_sobjects()
        my.pages = SObject.get_values(sobjects, "view")


        config_xml = my.kwargs.get("config_xml")

        config_xml = '''
        <config>
        <elements>
          <element name="0,0">
            <display class="tactic.ui.panel.CustomLayoutWdg">
              <view>pages.test1</view>
            </display>
          </element>

          <element name="1,0">
            <display class="tactic.ui.panel.StaticTableLayoutWdg">
                <search_type>sthpw/login_group</search_type>
                <element_names>login_group</element_names>
                <show_shelf>false</show_shelf>
            </display>
          </element>

          <element name="2,0">
            <display class="tactic.ui.panel.CustomLayoutWdg">
              <view>test.search</view>
            </display>
          </element>

 
          <element name="1,1">
            <display class="tactic.ui.panel.StaticTableLayoutWdg">
                <search_type>sthpw/login_group</search_type>
                <element_names>login_group</element_names>
                <show_shelf>false</show_shelf>
            </display>
          </element>
        </elements>
        </config>
        '''

        from pyasm.widget import WidgetConfig
        config = WidgetConfig.get(view="elements", xml=config_xml)




        table = DivWdg() 
        inner.add(table)
        table.add_style("margin: 20px")
        table.add_style("box-sizing: border-box")


        menu = my.get_action_menu()
        #SmartMenu.add_smart_menu_set( top, { 'BUTTON_MENU': menu } )


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


                menu_wdg = DivWdg()
                col.add(menu_wdg)
                menu_wdg.add_style("float: right")
                menu_wdg.add("+ Add View")
                menu_wdg.add_class("hand")

                SmartMenu.add_smart_menu_set( menu_wdg, { 'BUTTON_MENU': menu } )
                SmartMenu.assign_as_local_activator( menu_wdg, "BUTTON_MENU", True )

                print x,y
                col.add("Panel: %s,%s" % (x, y))
                col.add("<hr/>")

                content = DivWdg()
                col.add(content)
                content.add_class("spt_panel_content")

                element_name = "%s,%s" % (x,y)

                element = config.get_display_widget(element_name)
                if element:
                    content.add(element)

        if my.kwargs.get("is_refresh"):
            return inner
        else:
            return top



    def get_action_menu(my):

        from menu_wdg import Menu, MenuItem
        menu = Menu(width=180)
        menu_item = MenuItem(type='title', label='Actions')
        menu.add(menu_item)

        menu_item = MenuItem(type='action', label="Reload Page")
        menu.add(menu_item)
        menu_item = MenuItem(type='action', label="Remove Row")
        menu.add(menu_item)
        menu_item = MenuItem(type='action', label="Remove Column")
        menu.add(menu_item)
        menu_item = MenuItem(type='action', label="Save Layout")
        menu.add(menu_item)

        menu_item.add_behavior( {
            'type': 'click',
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
                console.log(class_name);
            }

            '''
        } )



        menu_item = MenuItem(type='title', label='Pages')
        menu.add(menu_item)
        for page in my.pages:

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

        for item in ['1x1','2x1','3x1','1x2','2x2','3x2','4x2','Custom']:

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

