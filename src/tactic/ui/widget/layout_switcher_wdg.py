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
from pyasm.web import WidgetSettings, DivWdg, Table, HtmlElement, SpanWdg
from pyasm.widget import WidgetConfig, IconWdg

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.widget import IconButtonWdg, ActionButtonWdg, ButtonNewWdg

from mako import exceptions



class LayoutSwitcherWdgOld(BaseRefreshWdg):

    def init(self):

        self.outer_wdg = DivWdg()
        self.menu_wdg = DivWdg()
        self.outer_wdg.add(self.menu_wdg)


    def has_config(cls):
        return True
    has_config = classmethod(has_config)

    def set_as_activator(self):
        pass

    def get_styles(self):

        styles = '''

            .spt_switcher_top .dropdown-toggle {
                width: 100%;
            }
            
            '''
            
        menu = self.menu
        if not menu:
            styles += '''
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
                    padding: 10px 5px;
                    cursor: pointer;
                }
                .spt_switcher_menu .spt_task_count {
                    margin-left: 5px;
                }
            '''


        return HtmlElement.style(styles)

    def get_activator(self):
        title = self.title
        mode = self.mode
        badge_count = self.badge_count
        color = self.color 
        background = self.background 

        
        if mode == "button":
            if badge_count:
                activator = DivWdg("<button class='btn btn-%s dropdown-toggle'><span class='spt_title'>%s</span> <span class='spt_task_count badge badge-dark spt_update'>%s</span> <span class='caret'></span></button>" % (color, title, badge_count))
            else:
                activator = DivWdg("<button class='btn btn-%s dropdown-toggle'><span class='spt_title'>%s</span> <span class='caret'></span></button>" % (color, title))
        elif mode == "div":
            if badge_count:
                activator = DivWdg("<button class='btn dropdown-toggle' style='background: %s; color: %s; font-weight: bold'><span class='spt_title'>%s</span> <span class='spt_task_count badge badge-dark spt_update'>%s</span> <span class='caret'></span></button>" % (background, color, title, badge_count))
            else:
                activator = DivWdg("<button class='btn dropdown-toggle' style='background: %s; color: %s; font-weight: bold'><span class='spt_title'>%s</span> <span class='caret'></span></button>" % (background, color, title))

        else:
            activator = IconButtonWdg( name="Layout Switcher", icon="BS_TH_LIST")
        
        activator.add_behavior( {
            'type': 'click_upX',
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

                spt.body.add_focus_element(menu);

                var pointer = menu.getElement(".spt_switcher_popup_pointer");
                pointer.setStyle("margin-left", menu_size.x - button_size.x);

            } 
            '''
        } )

        return activator
    
    def get_menu_wdg(self):    
        menu_wdg = self.menu_wdg
        menu_wdg.add_color("color", "color")
        menu_wdg.add_color("background", "background")
        menu_wdg.add_border("solid 1px %s" % menu_wdg.get_color("border"))
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
            <div class="spt_switcher_first_arrow_div"> </div>
            <div class="spt_switcher_second_arrow_div"> </div>
        ''')
        pointer_wdg.add_class("spt_switcher_popup_pointer")

        style = HtmlElement.style('''
            .spt_switcher_menu .spt_switcher_popup_pointer {
                z-index: 10;
                position: absolute;
                top: -15px;
                right: 15px;
            }

            .spt_switcher_menu .spt_switcher_first_arrow_div {
                border-color: rgba(0, 0, 0, 0) rgba(0, 0, 0, 0) %s;
                top: -15px;
                z-index: 1;
                border-width: 0 15px 15px;
                height: 0;
                width: 0;
                border-style: dashed dashed solid;
                left: 15px;
            }

            .spt_switcher_menu .spt_switcher_second_arrow_div{
                border-color: rgba(0, 0, 0, 0) rgba(0, 0, 0, 0) #fff;
                z-index: 1;
                border-width: 0 15px 15px;
                height: 0;
                width: 0;
                border-style: dashed dashed solid;
                margin-top: -14px;
                position: absolute;
                left: 0px;
                top: 15px;
            }
        ''' % border_color)
        pointer_wdg.add(style)

        return menu_wdg

    def get_menu_item(self):
        return DivWdg()
        
    def get_menu_item_bvr(self):
        
        return """
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
                var target_top = document.id(document.body);
            }
            var target = target_top.getElement("."+target_class);
            if (target) {
                var widget_key = bvr.src_el.getAttribute("SPT_WIDGET_KEY");
                spt.panel.load(target, widget_key, bvr.display_options);
            }

            menu.setStyle("display", "none");
            top.removeClass("spt_selected");

            var title = bvr.src_el.getAttribute("spt_title");
            var badge_count = bvr.src_el.getAttribute("badge_count");

            var title_el = top.getElement(".spt_title");
            if (title_el && !bvr.hidden)
                title_el.innerHTML = title
            
            var badge_el = top.getElement(".spt_task_count");
            if (badge_el && !bvr.hidden){
                badge_el.innerHTML = badge_count;
            }

            if (bvr.save_state) {
                var server = TacticServerStub.get()
                server.set_widget_setting(bvr.save_state, bvr.element_name);
            }
        """


    def get_outer_wdg(self):
        return self.outer_wdg

    def get_display(self):

        top = self.top
        top.add_class("spt_switcher_top")

        '''
        This supports supports two menu definitions:
        menu - specifies a view for SideBarWdg which will be ingected as menu 
        config_xml - specifies menu entries. For example:

        <display class="tactic.ui.widget.LayoutSwitcherWdg">
          <!-- config_xml -->
          <config>
            <!-- Menu item 1 -->
            <element name="self_tasks_default" title="My Tasks" target=spt_my_tasks_table_top">
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
        
        self.menu = self.kwargs.get("menu")
        config_xml = self.kwargs.get("config_xml")
        target = self.kwargs.get("target")

        #default
        default_layout = self.kwargs.get("default_layout")

        # find the save state value, if state is to be saved
        save_state = self.kwargs.get("save_state")

        if save_state in [False, 'false']:
            save_state = None
            show_first = False
        else:
            show_first = True

        state_value = None
        if save_state:
            state_value = WidgetSettings.get_value_by_key(save_state)
        elif default_layout:
            state_value = default_layout

        title = self.kwargs.get("title")
        if not title and state_value:
            title = state_value
        if not title:
            title = "Switch Layout"
        self.title = title
        
        self.mode = self.kwargs.get("mode")
        self.badge_count = self.kwargs.get("badge_count") or ""
        self.color = self.kwargs.get("color") or "default"
        self.background = self.kwargs.get("background") or "transparent"

        activator = self.get_activator()
        top.add(activator)
        activator.add_class("spt_switcher_activator")

        outer_wdg = self.get_outer_wdg()
        top.add(outer_wdg)
            
        # menu_wdg 
        menu_wdg = self.get_menu_wdg()

        # build menu
        if self.menu:
            from tactic.ui.panel import SimpleSideBarWdg
            simple_sidebar = SimpleSideBarWdg(view=self.menu, search_type="SidebarWdg", target=target) 
            menu_wdg.add(simple_sidebar)
        else:
            self.view = 'tab'
            config = WidgetConfig.get(view=self.view, xml=config_xml)
            element_names = config.get_element_names()

            if not element_names:
                outer_wdg.add_style("display: none")

            if not state_value:
                if not element_names:
                    state_value = ""
                else:
                    state_value = element_names[0]

            state_value_hidden = False
            default_title = None

            for element_name in element_names:

                attrs = config.get_element_attributes(element_name)
                css_class = attrs.get("class")
                hidden = attrs.get("hidden") == "true"

                title = attrs.get("title")
                if not title:
                    title = Common.get_display_title(element_name)

                if not default_title and not hidden:
                    default_title = title

                item_div = self.get_menu_item()
                menu_wdg.add(item_div)

                item_div.add_style("display: flex")
                item_div.add_style("justify-content: space-between")
                item_div.add_style("align-items: center")
                item_div.add_style("flex-wrap: nowrap")

                
                if css_class:
                    item_div.add_class(css_class)
                
                if hidden:
                    item_div.add_style("display: none")
                
                for name, value in attrs.items():
                    if name in ['title', 'class']:
                        continue
                    item_div.add_attr(name, value)
                
                item_div.add_class("spt_switcher_item")
                item_div.add_class("tactic_hover")

                item_div.add("<div>%s</div>" % title)
                item_div.add_attr("spt_title", title)

                badge_count = attrs.get("badge_count")
                if badge_count:
                    badge = DivWdg(badge_count)
                    badge.add_class("badge badge-dark")
                    badge.add_class("spt_task_count")
                    item_div.add(badge)

                target = attrs.get("target")
                if not target:
                    target = "spt_content"

                display_class = config.get_display_handler(element_name)
                display_options = config.get_display_options(element_name)

                if show_first != False:
                    if element_name == state_value:
                        state_value_hidden = True
                        item_div.add_behavior( {
                            'type': 'load',
                            'cbjs_action': '''
                                bvr.src_el.click();
                            '''
                        } )

                if display_class:
                    item_div.generate_widget_key(display_class, inputs=display_options)
                    item_div.add_behavior( {
                        'type': 'click_up',
                        'element_name': element_name,
                        'target': target,
                        'save_state': save_state,
                        'display_options': display_options,
                        'hidden': hidden,
                        'cbjs_action': self.get_menu_item_bvr()
                    } )

        top.add(self.get_styles())
            
        return top



#class LayoutSwitcherWdg(LayoutSwitcherWdgOld):
#    pass

class LayoutSwitcherWdg(LayoutSwitcherWdgOld):
   
    def get_styles(self):
        return HtmlElement.style("""

        .spt_switcher_top.dropdown{
            display: block !important;
        }

        """)


    def init(self):

        self.top.add_class("dropdown")

        self.outer_wdg = DivWdg()
        self.menu_wdg = self.outer_wdg

        self.dropdown_id = Common.generate_random_key()

    def get_activator(self):
        
        if self.mode == "icon":
            activator = ButtonNewWdg(
                title=self.title, 
                icon="FA_TABLE",
                dropdown_id=self.dropdown_id
            )
            return activator
        
        
        
        title = """
            <span class='spt_title'>%s</span>
            <span class='badge badge-dark spt_task_count'>%s</span>
        """ % (self.title, self.badge_count) 
        
        activator = ActionButtonWdg(
            title=title, 
            dropdown_id=self.dropdown_id,
            btn_class="btn btn-secondary dropdown-toggle"
        )
        return activator 
   
    def get_menu_wdg(self):
        menu_wdg = self.menu_wdg

        menu_wdg.add_class("dropdown-menu")
        menu_wdg.set_attr("aria-labelledfor", self.dropdown_id)
        
        return menu_wdg
    
    def get_menu_item(self):
        item = HtmlElement("a")
        item.add_class("dropdown-item hand")
        return item
    
    def get_menu_item_bvr(self):
        
        return """
            var menu_item = bvr.src_el;
            var top = menu_item.getParent(".spt_switcher_top");
            //var menu = menu_item.getParent(".spt_switcher_menu");
            
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
                var target_top = document.id(document.body);
            }
            
            if (!target_top) return;

            var target = target_top.getElement("."+target_class);
            if (target) {
                var widget_key = bvr.src_el.getAttribute("SPT_WIDGET_KEY");
                spt.panel.load(target, widget_key, bvr.display_options);
            }

            top.removeClass("spt_selected");

            var title = bvr.src_el.getAttribute("spt_title");
            var badge_count = bvr.src_el.getAttribute("badge_count");

            var title_el = top.getElement(".spt_title");
            if (title_el && !bvr.hidden) {
                title_el.innerHTML = title
            } 
            
            var badge_el = top.getElement(".spt_task_count");
            if (badge_el && !bvr.hidden){
                badge_el.innerHTML = badge_count;
            }

            if (bvr.save_state) {
                var server = TacticServerStub.get()
                server.set_widget_setting(bvr.save_state, bvr.element_name);
            }
        """




