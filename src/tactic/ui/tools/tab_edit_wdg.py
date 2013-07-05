###########################################################
#
# Copyright (c) 2009, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#
__all__ = ["TabEditWdg", "TabElementDefinitionWdg"]

from pyasm.web import DivWdg
from pyasm.search import Search
from pyasm.widget import WidgetConfig
from tactic.ui.common import BaseRefreshWdg
from tactic.ui.container import ResizableTableWdg


class TabEditWdg(BaseRefreshWdg):


    def get_config(my):

        my.view = my.kwargs.get("view")
        my.view = 'tab_config_whatever'

        search = Search("config/widget_config")
        search.add_filter("category", "TabWdg")
        config_sobj = search.get_sobject()
        if config_sobj:
            config_xml = config_sobj.get_value("config")
        else:
            config_xml = '''
            <config>
              <tab>
              </tab>
            </config>'''
        config = WidgetConfig.get(view=my.view, xml=config_xml)

        return config



    def get_display(my):
        top = my.top
        my.set_as_panel(top)
        top.add_color("background", "background")
        top.add_border()
        top.add_class("spt_tab_edit_top")

        my.config = my.get_config()


        table = ResizableTableWdg()
        top.add(table)
        table.add_color("color", "color")

        table.add_row()

        left = table.add_cell()
        left.add(my.get_elements_wdg() )
        left.add_style("width: 200px")
        left.add_border()
        left.add_color("background", "background3")
        left.add_color("color", "color3")


        right = table.add_cell()
        right.add_border()


        title_wdg = DivWdg()
        right.add(title_wdg)
        title_wdg.add("Definition")
        title_wdg.add_style("padding: 5px")
        title_wdg.add_gradient("background", "background", -10)


        right_div = DivWdg()
        right.add(right_div)
        right_div.add_style("width: 500px")
        right_div.add_class("spt_tab_edit_content")


        return top



    def get_elements_wdg(my):

        div = DivWdg()
        div.add_style("min-width: 200px")
        div.add_style("min-height: 500px")

        title_wdg = DivWdg()
        div.add(title_wdg)
        title_wdg.add("Elements")
        title_wdg.add_style("padding: 5px")
        title_wdg.add_gradient("background", "background", -10)

        #element_names = ['Checkin', 'Checkout']
        element_names = my.config.get_element_names()

        elements_wdg = DivWdg()
        div.add(elements_wdg)
        elements_wdg.add_style("padding: 5px")


        view = 'tab_config_whatever'


        hover = div.get_color("background", -10)

        for element_name in element_names:
            element_div = DivWdg()
            elements_wdg.add(element_div)
            element_div.add(element_name)
            element_div.add_style("padding: 3px")

            element_div.add_behavior( {
                'type': 'hover',
                'hover': hover,
                'cbjs_action_over': '''bvr.src_el.setStyle("background", bvr.hover)''',
                'cbjs_action_out': '''bvr.src_el.setStyle("background", "")'''
            } )
            element_div.add_class("hand")

            element_div.add_behavior( {
                'type': 'click_up',
                'view': view,
                'element_name': element_name,
                'cbjs_action': '''
                var top = bvr.src_el.getParent(".spt_tab_edit_top");
                var content = top.getElement(".spt_tab_edit_content");
                var class_name = 'tactic.ui.tools.tab_edit_wdg.TabElementDefinitionWdg';
                var kwargs = {
                  view: bvr.view,
                  element_name: bvr.element_name
                };

                spt.panel.load(content, class_name, kwargs);
                '''
            } )


        return div


class TabElementDefinitionWdg(BaseRefreshWdg):

    def get_config(my):

        my.view = my.kwargs.get("view")

        search = Search("config/widget_config")
        search.add_filter("category", "TabWdg")
        config_sobj = search.get_sobject()
        config_xml = config_sobj.get_value("config")
        config = WidgetConfig.get(view=my.view, xml=config_xml)

        return config



    def get_display(my):

        top = my.top

        my.config = my.get_config()

        element_name = my.kwargs.get("element_name")

        if not element_name:
            widget_key = ''
            display_class = ''
            display_options = {}
        else:
            widget_key = my.config.get_widget_key(element_name)
            display_class = my.config.get_display_handler(element_name)
            display_options = my.config.get_display_options(element_name)


        from tactic.ui.manager import WidgetClassSelectorWdg
        # add the widget information
        from tactic.ui.manager import WidgetClassSelectorWdg
        class_labels = ['Table with Search Layout', 'Custom Layout', 'Edit Layout', 'Tile Layout', 'Free Form', '-- Class Path --']
        class_values = ['view_panel', 'custom_layout', 'edit_layout', 'tile_layout', 'freeform_layout', '__class__']
        default_class='view_panel'



        widget_class_wdg = WidgetClassSelectorWdg(widget_key=widget_key, display_class=display_class, display_options=display_options,class_labels=class_labels,class_values=class_values, prefix='option', default_class=default_class)
        top.add(widget_class_wdg)

        return top




