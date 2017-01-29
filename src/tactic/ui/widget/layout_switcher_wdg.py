###########################################################
#
# Copyright (c) 2015, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#

__all__ = ['LayoutSwitcherWdg']


from pyasm.common import Common
from pyasm.web import DivWdg, Table, HtmlElement
from pyasm.widget import WidgetConfig, IconWdg

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.widget import IconButtonWdg

class LayoutSwitcherWdg(BaseRefreshWdg):

    def has_config(cls):
        return True
    has_config = classmethod(has_config)

    def set_as_activator(my):
        pass

    def get_display(my):

        top = my.top
        top.add_class("spt_switcher_top")
        
        '''
        This supports supports two menu definitions:
        menu - specifies a view for SideBarWdg which will be ingected as menu 
        config_xml - specifies menu entries. For example:

        <display class="tactic.ui.widget.LayoutSwitcherWdg">
          <!-- config_xml -->
          <config>
            <!-- Menu item 1 -->
            <element name="my_tasks_default" title="My Tasks" target=spt_my_tasks_table_top">
              <display class="tactic.ui.panel.ViewPanelWdg">
                <search_type>sthpw/task</search_type>
                <show_shelf>false</show_shelf>
                <view>my_tasks_default</view>
              </display>
            </element>
            <!-- Menu item 2 -->
            <element ... >
              <display ... >
              </display>
            </element>
          </config>
        </display>

        target - specifies target div to load views when using "menu" kwarg
        use_href - updates address bar hash (this is TODO)
        '''
        
        menu = my.kwargs.get("menu")
        config_xml = my.kwargs.get("config_xml")
        target = my.kwargs.get("target")
        # TODO: use_href to go to specific layout switcher view
        # use_href = my.kwrags.get("use_href")
        
        # Layout switcher button displays menu and assumes right hand position of screen

        #from pyasm.web import WidgetSettings
        #key = "layout_switcher"
        #first_title = WidgetSettings.get_value_by_key(key)
        #if not first_title:
        #    first_title = "Switch Layout"
        first_title = "Switch Layout"




        mode = "button"
        if mode == "button":
            activator = DivWdg("<button class='btn btn-default dropdown-toggle' style='width: 160px'><span class='spt_title'>%s</span> <span class='caret'></span></button>" % first_title)
        else:
            activator = IconButtonWdg( name="Layout Switcher", icon="BS_TH_LIST")

        top.add(activator)
        activator.add_class("spt_switcher_activator")
        activator.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var activator = bvr.src_el;
            var top = activator.getParent(".spt_switcher_top");
            var menu = top.getElement(".spt_switcher_menu");
            
            if (top.hasClass("spt_selected")) {
                top.removeClass("spt_selected");
                menu.setStyle("display", "none");    
            } else {
                top.addClass("spt_selected");
                menu.setStyle("display", "");
                var pos = activator.getPosition();
                var button_size = activator.getSize();
                var menu_size = menu.getSize();
                var offset = {
                    x: button_size.x - menu_size.x,
                    y: button_size.y
                }
                menu.position({position: 'upperleft', relativeTo: activator, offset: offset});

                var pointer = menu.getElement(".spt_popup_pointer");
                pointer.setStyle("margin-left", menu_size.x - button_size.x);

            } 
            '''
        } )
            
        # menu_wdg 
        menu_wdg = DivWdg()
        top.add(menu_wdg)
        menu_wdg.add_color("background", "background")
        menu_wdg.add_border()
        menu_wdg.add_class("spt_switcher_menu")
        menu_wdg.add_style("display: none")
        menu_wdg.add_style("margin-top", "20px")
        menu_wdg.add_style("position", "absolute")
        menu_wdg.add_style("z-index", "101")
        menu_wdg.add_behavior( {
            'type': 'mouseleave',
            'cbjs_action': '''
            var menu = bvr.src_el;
            var top = menu.getParent(".spt_switcher_top");
            top.removeClass("spt_selected");
            menu.setStyle("display", "none")
            '''
        } )

        border_color = menu_wdg.get_color("border")
        
        # Pointer under activator
        pointer_wdg = DivWdg()
        menu_wdg.add(pointer_wdg)
        pointer_wdg.add('''
            <div class="spt_first_arrow_div"> </div>
            <div class="spt_second_arrow_div"> </div>
        ''')
        pointer_wdg.add_class("spt_popup_pointer")

        style = HtmlElement.style('''
            .spt_switcher_menu .spt_popup_pointer {
                z-index: 10;
                position: absolute;
                top: -15px;
                right: 15px;
            }

            .spt_switcher_menu .spt_first_arrow_div {
                border-color: rgba(0, 0, 0, 0) rgba(0, 0, 0, 0) %s;
                top: -15px;
                z-index: 1;
                border-width: 0 15px 15px;
                height: 0;
                width: 0;
                border-style: dashed dashed solid;
                left: 15px;
            }

            .spt_switcher_menu .spt_second_arrow_div{
                border-color: rgba(0, 0, 0, 0) rgba(0, 0, 0, 0) #fff;
                z-index: 1;
                border-width: 0 15px 15px;
                height: 0;
                width: 0;
                border-style: dashed dashed solid;
                margin-top: -14px;
                position: absolute;
            }
        ''' % border_color)
        pointer_wdg.add(style)
 
        if menu:
            from tactic.ui.panel import SimpleSideBarWdg
            simple_sidebar = SimpleSideBarWdg(view=menu, search_type="SidebarWdg", target=target) 
            menu_wdg.add(simple_sidebar)
        else:
            style = my.get_style()
            top.add(style)
            
            my.view = 'tab'
            config = WidgetConfig.get(view=my.view, xml=config_xml)
            element_names = config.get_element_names()

            for element_name in element_names:

                item_div = DivWdg()
                menu_wdg.add(item_div)
                item_div.add_class("spt_switcher_item")
                item_div.add_class("tactic_hover")

                attrs = config.get_element_attributes(element_name)
                title = attrs.get("title")
                if not title:
                    title = Common.get_display_title(element_name)

                item_div.add(title)
                item_div.add_attr("spt_title", title)

                target = attrs.get("target")
                if not target:
                    target = "spt_content"

                display_class = config.get_display_handler(element_name)
                display_options = config.get_display_options(element_name)

                key = "layout_switcher"

                item_div.add_behavior( {
                    'type': 'click_up',
                    'display_class': display_class,
                    'display_options': display_options,
                    'element_name': element_name,
                    'target': target,
                    'key': key,
                    'cbjs_action': '''
                    var menu_item = bvr.src_el;
                    var top = menu_item.getParent(".spt_switcher_top");
                    var menu = menu_item.getParent(".spt_switcher_menu");
                    
                    // Get target class
                    var target_class = bvr.target;
                    if (target_class.indexOf(".") != -1) {
                        var parts = target_class.split(".");
                        target_class = parts[1]; 
                        target_top_class = parts[0];
                    }
                    else {
                        target_top_class = null;
                    }
                
                    if (target_top_class) {
                        var target_top = bvr.src_el.getParent("."+target_top_class);
                    }
                    else {
                        var target_top = $(document.body);
                    }
                    var target = target_top.getElement("."+target_class);
                    if (target) {
                        spt.panel.load(target, bvr.display_class, bvr.display_options);
                    }

                    menu.setStyle("display", "none");
                    top.removeClass("spt_selected");

                    var title = bvr.src_el.getAttribute("spt_title");

                    var title_el = top.getElement(".spt_title");
                    if (title_el)
                        title_el.innerHTML = title


                    //var server = TacticServerStub.get()
                    //server.set_widget_setting(bvr.key, bvr.element_name);

                    '''
                } )
        
        return top


    def get_style(my):
        '''Default style used when menu switcher is defined from config_xml'''

        style = HtmlElement.style('''

.spt_switcher_menu {
  padding: 0px 0px;
  border: solid 1px #CCC;
  width: 200px;
  height: auto;
  right: 5px;
  background: #FFF;
  text-align: center;
}

.spt_switcher_menu .spt_switcher_item {
  padding: 10px 0px;
  cursor: pointer;
}

        ''')

        return style
