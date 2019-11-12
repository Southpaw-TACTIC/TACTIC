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

__all__ = ['PanelWdg', 'SavePanelCmd', 'UserPanelSelectWdg', 'UserPanelCreatorWdg', 'UserPanelCreatorCmd']

import tacticenv

from pyasm.common import Common, Xml, Environment
from pyasm.search import Search, SObject, SearchType
from pyasm.web import DivWdg, ButtonWdg, HtmlElement
from pyasm.widget import WidgetConfig
from pyasm.command import Command

from pyasm.security import Sudo

from tactic.ui.container import SmartMenu
from tactic.ui.common import BaseRefreshWdg
from tactic.ui.widget import ActionButtonWdg

import six


class PanelWdg(BaseRefreshWdg):

    def get_display(self):

        self.view = self.kwargs.get("view")

        top = self.top
        top.add_class("spt_panel_layout_top")
        self.set_as_panel(top)

        inner = DivWdg()
        top.add(inner)

        inner.add_behavior( {
            'type': 'load',
            'cbjs_action': self.get_onload_js()
        } )


        is_owner = True
        #is_owner = False


        if is_owner:
            shelf = DivWdg()
            inner.add(shelf)
            shelf.add_style("display: flex")
            #shelf.add_style("float: right")
            #shelf.add_style("margin-top: -50px")
            shelf.add_style("font-size: 9px")

            shelf.add_class("spt_shelf")

            style = HtmlElement.style()
            shelf.add(style)
            style.add('''
            .spt_panel_layout_top .spt_shelf .btn {
                font-size: 12px;
                height: 30px;
                margin: 3px 5px;
            }
            ''')




            """
            btn = ButtonWdg()
            btn.add_class("btn btn-default")
            shelf.add(btn)
            btn.add_behavior( {
                'type': 'click',
                'cbjs_action': '''
                var top = bvr.src_el.getParent(".spt_panel_layout_top");
                var content_els = top.getElements(".spt_panel_content");
                content_els.forEach( function(el) {
                    el.setStyle("display", "none");
                    
                } )
                '''
            } )
            btn.add("Hide Content")


            btn = ButtonWdg()
            btn.add_class("btn btn-default")
            shelf.add(btn)
            btn.add_behavior( {
                'type': 'click',
                'cbjs_action': '''
                var top = bvr.src_el.getParent(".spt_panel_layout_top");
                var content_els = top.getElements(".spt_panel_content");
                content_els.forEach( function(el) {
                    el.setStyle("display", "");
                    
                } )
                '''
            } )
            btn.add("Show Content")
            """


            btn = ButtonWdg()
            shelf.add(btn)
            btn.add("Add Panel")
            btn.add_class("btn btn-default")

            btn.add_behavior( {
                'type': 'click',
                'view': self.view,
                'cbjs_action': '''
                var top = bvr.src_el.getParent(".spt_panel_layout_top");

                var panel_container = top.getElement(".spt_panel_container");
                var template = panel_container.getElement(".SPT_TEMPLATE");
                var clone = spt.behavior.clone(template);
                clone.inject(template, "after");
                clone.setStyle("display", "");
                clone.removeClass("SPT_TEMPLATE");
                '''
            } )





            btn = ButtonWdg()
            shelf.add(btn)
            btn.add("Save Panels")
            btn.add_class("btn btn-default")

            btn.add_behavior( {
                'type': 'click',
                'view': self.view,
                'cbjs_action': '''
                var top = bvr.src_el.getParent(".spt_panel_layout_top");

                var panels = top.getElements(".spt_panel_content");

                var server = TACTIC.get();

                var kwargs = {};
                kwargs.view = bvr.view;

                var data = [];
                kwargs.data = data;

                for (var i = 0; i < panels.length; i++) {
                    var panel = panels[i];
                    var content = panel.getElement(".spt_panel");
                    if (content == null) {
                        continue;
                    }
                    var class_name = content.getAttribute("spt_class_name");
                    var options = spt.panel.get_element_options(content);

                    var data_item = {};
                    data.push(data_item);
                    data_item.class_name = class_name;
                    data_item.options = options;

                    element_name = "panel_" + i;
                    data_item.element_name = element_name;

                }

                var class_name = "tactic.ui.container.SavePanelCmd";
                server.p_execute_cmd(class_name, kwargs)
                .then( function() {
                    spt.notify.show_message("Panel Layout Saved");
                } );

                '''
            } )


            btn = ButtonWdg()
            shelf.add(btn)
            btn.add("Edit Layout")
            btn.add_class("btn btn-default")

            btn.add_behavior( {
                'type': 'click',
                'cbjs_action': '''

                var top = bvr.src_el.getParent(".spt_panel_layout_top");
                var panel_top = top.getElement(".spt_panel_container");

                var panels = panel_top.getElements(".spt_panel_top");

                if (panel_top.hasClass("spt_edit_mode")) {
                    panel_top.setStyle("transform", "scale(1.0)");
                    panel_top.removeClass("spt_edit_mode");

                    panels.forEach( function(panel) {
                        var drag = panel.getElement(".spt_drag");
                        drag.setStyle("display", "none");
                    } )

                    panel_top.setStyle("border", "none");
                    panel_top.setStyle("padding", "0px");
                    panel_top.setStyle("background", "transparent");
                }
                else {
                    panel_top.setStyle("transform", "scale(0.33)");
                    panel_top.setStyle("transform-origin", "top");
                    panel_top.addClass("spt_edit_mode");


                    panels.forEach( function(panel) {
                        var drag = panel.getElement(".spt_drag");
                        drag.setStyle("display", "");
                    } )

                    panel_top.setStyle("border", "solid 10px #DDD");
                    panel_top.setStyle("padding", "30px");
                    panel_top.setStyle("background", "#999");
                }
                '''
            } )








        # Define some views that are pages.  Panels are views that are self
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

        """
        grid = self.kwargs.get("grid")
        if not grid:
            grid = config.get_view_attribute("grid")

        if grid:
            if isinstance(grid, six.string_types):
                if grid == "custom":
                    grid = (2,2)
                else:
                    grid = [int(x) for x in grid.split("x")]

        else:
            grid = (3,1)
        """



        table = DivWdg() 
        inner.add(table)
        table.add_style("margin: 0px 0px 20px 0px")
        table.add_style("box-sizing: border-box")

        table.add_style("position: relative")

        element_names = config.get_element_names()

        index = 0

        row = DivWdg()
        table.add(row)
        row.add_class("row")
        row.add_style("box-sizing: border-box")
        row.add_style("display: flex")
        row.add_style("flex-wrap: wrap")
        #row.add_style("justify-content: space-between")

        row.add_class("spt_panel_container")

        element_name = element_names.insert(0, "TEMPLATE")

        for element_name in element_names:
            col = DivWdg()
            row.add(col)

            col.add_style("box-sizing: border-box")
            col.add_style("overflow: auto")
            col.add_style("min-width: 200px")

            # TODO: max-width should be set by the widget
            col.add_style("max-width: 50%")

            col.add_class("spt_panel_top")

            outer = DivWdg()
            col.add(outer)
            outer.add_class("spt_outer")
            outer.add_style("position: relative")
            outer.add_style("overflow: hidden")

            drag = DivWdg()
            outer.add(drag)
            drag.add_class("spt_drag")
            drag.add_style("position: absolute")
            drag.add_style("display: none")
            drag.add_style("top: 0px")
            drag.add_style("left: 0px")
            drag.add_style("height: 100%")
            drag.add_style("width: 100%")
            drag.add_style("background: #000")
            drag.add_style("opacity: 0.05")
            drag.add_style("z-index: 200")

            drag.add_behavior( {
            'type': 'drag',
            "drag_el": '@.getParent(".spt_panel_top")',
            "cb_set_prefix": 'spt.panel_container.drag'
            } )

            #outer.add_style("pointer-events: none")



            if is_owner:
                header = DivWdg()
                outer.add(header)
                header.add_class("spt_header")

                menu_wdg = DivWdg()
                header.add(menu_wdg)
                menu_wdg.add_style("float: right")
                menu_wdg.add("<i class='fa fa-bars'> </i>")
                menu_wdg.add_class("hand")
                menu_wdg.add_style("margin: 0px 5px")

                menu_wdg.add_behavior( {
                    'type': 'click',
                    'cbjs_action': '''
                    var top = bvr.src_el.getParent(".spt_header");
                    var menu = top.getElement(".spt_menu_top");
                    menu.setStyle("display", "");
                    spt.body.add_focus_element(menu);

                    '''
                } )

                menu = self.get_action_menu()
                menu.add_style("position: absolute")
                menu.add_style("display: none")
                menu.add_style("right: 5px")
                menu.add_style("top: 30px")
                header.add(menu)



            element = None
            title = None

            if index == 0:
                # Skip the template
                title = "TEMPLATE"
                col.add_class("SPT_TEMPLATE")
                col.add_style("display: none")


            elif index < len(element_names):
                element_name = element_names[index]
                #element_name = "%s,%s" % (x,y)

                element = config.get_display_widget(element_name)
                title = config.get_element_title(element_name)
                if not title:
                    title = Common.get_display_title(element_name)

            if not element:
                element = DivWdg()
                element.add("No content")
                element.add_style("height: 30px")
                element.add_style("width: 80%")
                element.add_style("text-align: center")
                element.add_style("margin: 10px")
                element.add_style("padding: 5px")
                element.add_style("box-sizing: border-box")
                element.add_border()

                element.add_behavior( {
                    'type': 'click',
                    'cbjs_action': '''
                    alert("No content");
                    '''
                } )
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
                title_div = DivWdg()
                header.add(title_div)
                title_div.add_style("width: 100px")

                if title:
                    title_div.add(title)
                else:
                    title_div.add("Panel: %s,%s" % (x, y))


                title_div.add_behavior( {
                'type': 'drag',
                "drag_el": '@.getParent(".spt_panel_top")',
                "cb_set_prefix": 'spt.panel_container.drag'
                } )

                outer.add("<hr/>")

            content = DivWdg()
            outer.add(content)
            content.add_class("spt_panel_content")
            content.add_style("min-height: 200px")
            content.add_style("min-width: 200px")
            content.add_style("margin: 5px")
            content.add_style("box-sizing: border-box")

            outer.add_style("border: solid 1px #DDD")
            outer.add_style("border-radius: 3px")
            outer.add_style("padding: 10px")
            outer.add_style("margin: 0px 10px 15px 10px")
            outer.add_style("background: #FFF")


            content.add_style("max-height: 400px;")
            content.add_style("overflow: auto")

            content.add(element)

            index += 1


            if is_owner:
                outer.add_style("position: relative")
                resize_div = DivWdg()
                resize_div.add('''<img title="Resize" border="0" src="/context/icons/custom/resize.png" style="margin-right: 3px">''')
                outer.add(resize_div)
                resize_div.add_style("position: absolute")
                resize_div.add_style("bottom: 1px")
                resize_div.add_style("right: -2px")


                resize_div.add_behavior( {
                'type': 'drag',
                "drag_el": '@.getParent(".spt_panel_top")',
                "cb_set_prefix": 'spt.panel_container.resize_drag'
                } )



        if self.kwargs.get("is_refresh"):
            return inner
        else:
            return top



    def get_action_menu(self):

        menu = DivWdg()
        menu.add_style("width: 180")
        menu.add_style("background", "#FFF")
        menu.add_style("border: solid 1px #DDD")
        menu.add_style("box-shadow: 0px 0px 15px rgba(0,0,0,0.1)")
        menu.add_style("z-index: 1000")
        menu.add_style("text-align: center")

        menu.add_class("spt_menu_top")

        style = HtmlElement.style()
        menu.add(style)
        style.add('''
        .spt_panel_layout_top .spt_menu_top .spt_menu_item {
            padding: 10px;
            border-bottom: solid 1px #DDD;
            cursor: pointer;
        }
        ''')


        menu.add_relay_behavior( {
            'type': 'mouseenter',
            'bvr_match_class': 'spt_menu_item',
            'cbjs_action': '''
            bvr.src_el.setStyle("background", "#EEE");
            '''
        } )
        menu.add_relay_behavior( {
            'type': 'mouseleave',
            'bvr_match_class': 'spt_menu_item',
            'cbjs_action': '''
            bvr.src_el.setStyle("background", "");
            '''
        } )


        """
        menu_item = DivWdg()
        menu_item.add_class("spt_menu_item")
        menu_item.add("Create New Panel")
        menu.add(menu_item)
        menu_item.add_behavior( {
            'type': 'click',
            'cbjs_action': '''
            var class_name = 'tactic.ui.container.panel_wdg.UserPanelCreatorWdg';
            var kwargs = {
            }
            spt.panel.load_popup("Panel Creator", class_name, kwargs);
            '''
        } )
        """


        login = Environment.get_user_name()
        view_filter = "pages.%s.%%" % login


        if len(self.pages) > 5:


            menu_item = DivWdg()
            menu_item.add_class("spt_menu_item")
            menu.add(menu_item)
            menu_item.add("Load Content")
            menu_item.add_behavior( {
                'cbjs_action': '''
                var class_name = 'tactic.ui.container.panel_wdg.UserPanelSelectWdg';
                var kwargs = {
                    view: bvr.page,
                }
                var popup = spt.panel.load_popup("Load Panel", class_name, kwargs);
                popup.activator = bvr.src_el;

                '''
            } )

        else:

            for page in self.pages:
                menu_item = DivWdg()
                menu_item.add(page)
                menu_item.add_class("spt_menu_item")
                menu_item.add_behavior( {
                    'page': page,
                    'cbjs_action': '''
                    var top = bvr.src_el.getParent(".spt_panel_top");
                    var content = top.getElement(".spt_panel_content");

                    var class_name = 'tactic.ui.panel.CustomLayoutWdg';
                    var kwargs = {
                        view: bvr.page,
                    }
                    spt.panel.load(content, class_name, kwargs);

                    '''
                } )
                menu.add(menu_item)




        """
        menu_item = DivWdg()
        menu_item.add_class("spt_menu_item")
        menu_item.add("Edit Panel")
        menu.add(menu_item)
        menu_item.add_behavior( {
            'type': 'click',
            'view_filter': view_filter,
            'cbjs_action': '''
            spt.tab.set_main_body_tab();
            title = "Panel Editor";
            var class_name = 'tactic.ui.tools.CustomLayoutEditWdg';
            var kwargs = {
                view_filter: bvr.view_filter
            }
            spt.tab.add_new(title, title, class_name, kwargs);
            '''
        } )
        """



        menu_item = DivWdg()
        menu_item.add_class("spt_menu_item")
        menu.add(menu_item)
        menu_item.add("Reload Panel")
        menu_item.add_behavior( {
            'type': 'click',
            'cbjs_action': '''
            var activator = spt.smenu.get_activator(bvr);
            var top = activator.getParent(".spt_panel_top");
            var content = top.getElement(".spt_panel_content");
            spt.panel.refresh(content);
            '''
        } )




        menu_item = DivWdg()
        menu_item.add_class("spt_menu_item")
        menu.add(menu_item)
        menu_item.add("Save Layout")
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






        menu_item = DivWdg()
        menu.add(menu_item)
        menu_item.add("<< Move Left")
        menu_item.add_class("spt_menu_item")
        menu_item.add_behavior( {
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_panel_top");
            var prev = top.getPrevious();
            if (prev) {
                top.inject(prev, "before");
            }
            '''
        } )



        menu_item = DivWdg()
        menu.add(menu_item)
        menu_item.add("Move Right >>")
        menu_item.add_class("spt_menu_item")
        menu_item.add_behavior( {
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_panel_top");
            var next = top.getNext();
            if (next) {
                top.inject(next, "after");
            }
            '''
        } )






        menu_item = DivWdg()
        menu.add(menu_item)
        menu_item.add("Remove Panel")
        menu_item.add_class("spt_menu_item")
        menu_item.add_behavior( {
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_panel_top");
            spt.behavior.destroy_element(top);

            '''
        } )


        return menu





    def get_onload_js(self):

        return '''
spt.panel_container = {};

spt.panel_container.top = null;
spt.panel_container.container_top = null;
spt.panel_container.clone = null;
spt.panel_container.start_pos = null;
spt.panel_container.mouse_start_pos = null;
spt.panel_container.drop_on_el = null;

spt.panel_container.drag_setup = function(evt, bvr, mouse_411) {
    var panel_top = bvr.src_el.getParent(".spt_panel_top");
    spt.panel_container.top = panel_top;

    var top = bvr.src_el.getParent(".spt_panel_container");
    spt.panel_container.container_top = top;

    var start_pos = panel_top.getPosition(top);

    if (top.hasClass("spt_edit_mode")) {
        start_pos.x *= 3;
        start_pos.y *= 3;
    }

    spt.panel_container.start_pos = start_pos;
    spt.panel_container.mouse_start_pos = {x: mouse_411.curr_x, y: mouse_411.curr_y};

    var clone = spt.behavior.clone(panel_top);
    spt.panel_container.clone = clone;

    var size = panel_top.getSize();

    panel_top.setStyle("opacity", "0.3");

    top.appendChild(clone);
    clone.setStyle("position", "absolute");
    clone.setStyle("z-index", "1000");

    var outer = clone.getElement(".spt_outer");
    outer.setStyle("box-shadow", "0px 0px 15px rgb(0,0,0,0.1)");

    clone.setStyle("pointer-events", "none");
    clone.setStyle("overflow", "hidden");

    clone.setStyle("width", size.x);
    clone.setStyle("height", size.y);
    clone.setStyle("min-width", size.x);
    clone.setStyle("min-height", size.y);
    clone.setStyle("max-width", size.x);
    clone.setStyle("max-height", size.y);

    clone.setStyle("top", start_pos.y);
    clone.setStyle("left", start_pos.x);

    top.setStyle("cursor", "move");

}

spt.panel_container.drag_motion = function(evt, bvr, mouse_411) {
    var mouse_pos = {x: mouse_411.curr_x, y: mouse_411.curr_y};

    var dx = mouse_pos.x - spt.panel_container.mouse_start_pos.x;
    var dy = mouse_pos.y - spt.panel_container.mouse_start_pos.y;

    var top = spt.panel_container.container_top;
    if (top.hasClass("spt_edit_mode")) {
        dx = dx * 3;
        dy = dy * 3;
    }

    var clone = spt.panel_container.clone;

    var start_pos = spt.panel_container.start_pos;
    clone.setStyle("left", start_pos.x + dx);
    clone.setStyle("top", start_pos.y + dy);

    var last_drop_on_el = spt.panel_container.drop_on_el;
    
    var drop_on_el = spt.get_event_target(evt);
    if (!drop_on_el.hasClass("spt_panel_top")) {
        drop_on_el = drop_on_el.getParent(".spt_panel_top");
    }
    if (drop_on_el) {
        spt.panel_container.drop_on_el = drop_on_el;
        drop_on_el.setStyle("border-right", "solid 3px blue");
    }


    if (last_drop_on_el && last_drop_on_el != drop_on_el) {
        last_drop_on_el.setStyle("border-right", "");
    }

}

spt.panel_container.drag_action = function(evt, bvr, mouse_411) {

    var panel_top = spt.panel_container.top;
    var drop_on_el = spt.panel_container.drop_on_el;
    if (drop_on_el) {
        panel_top.inject(drop_on_el, "after");
    }


    panel_top.setStyle("pointer-events", "");
    panel_top.setStyle("z-index", "0");
    panel_top.setStyle("opacity", "1.0");

    var clone = spt.panel_container.clone;
    spt.behavior.destroy_element(clone);


    var last_drop_on_el = spt.panel_container.drop_on_el;
    last_drop_on_el.setStyle("border-right", "");


    var top = bvr.src_el.getParent(".spt_panel_container");
    top.setStyle("cursor", "");
}




spt.panel_container.resize_drag_setup = function(evt, bvr, mouse_411) {
    var panel_top = bvr.src_el.getParent(".spt_panel_top");
    var top = panel_top.getElement(".spt_panel_content");
    spt.panel_container.top = top;

    var start_size = top.getSize();
    spt.panel_container.start_size = start_size;

    spt.panel_container.mouse_start_pos = {x: mouse_411.curr_x, y: mouse_411.curr_y};
}

spt.panel_container.resize_drag_motion = function(evt, bvr, mouse_411) {
    var mouse_pos = {x: mouse_411.curr_x, y: mouse_411.curr_y};

    var dx = mouse_pos.x - spt.panel_container.mouse_start_pos.x;
    var dy = mouse_pos.y - spt.panel_container.mouse_start_pos.y;

    var top = spt.panel_container.top;
    var start_size = spt.panel_container.start_size;

    top.setStyle("width", start_size.x + dx);
    top.setStyle("height", start_size.y + dy);

}

spt.panel_container.resize_drag_action = function(evt, bvr, mouse_411) {
}
        '''



class SavePanelCmd(Command):

    def execute(self):

        sudo = Sudo()

        data = self.kwargs.get("data")

        view = self.kwargs.get("view")

        search = Search("config/widget_config")
        search.add_filter("view", view)
        config = search.get_sobject()

        if not config:
            config = SearchType.create("config/widget_config")
            config.set_value("view", view)

        # reset the xml and commit
        config_xml = '''<config>
<%s>
</%s>
</config>''' % (view, view)

        config.set_value("config", config_xml)
        config.commit()

        # because setting the xml doesn't reset the sobject properly, we have
        # to re-search the sobject ... will have to fix later
        search = Search("config/widget_config")
        search.add_filter("view", view)
        config = search.get_sobject()


        # add all of the config items
        for item in data:
            print(item)
            name = item.get("element_name")

            class_name = item.get("class_name")
            display_options = item.get("options")

            config.append_display_element(name, cls_name=class_name, options=display_options)

        # have to set the value manually
        config_str = config.get_xml().to_string(pretty=True,tree=True)

        # for some reason the xml is not formatted properly.  Create a new xml object
        # to format it
        xml = Xml()
        xml.read_string(config_str)
        config_str = xml.to_string()

        config.set_value("config", config_str)
        config.commit()







class UserPanelSelectWdg(BaseRefreshWdg):

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
            page_div.add_style("box-sizing: border-box")
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




class UserPanelCreatorWdg(BaseRefreshWdg):

    def get_display(self):

        top = self.top
        top.add_style("width: 600px")
        top.add_style("height: 600px")
        top.add_style("margin: 20px")
        top.add_class("spt_page_creator_top")

        top.add("<div style='font-size: 16px'>Panel Creator</div>")

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

 


        button = ActionButtonWdg(title="Save Panel", width=150)
        button_div.add(button)
        button.add_behavior( {
            'type': 'click',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_page_creator_top");
            var values = spt.api.get_input_values(top, null, false);

            var class_name = 'tactic.ui.container.panel_wdg.UserPanelCreatorCmd';
            var server = TacticServerStub.get();
            server.execute_cmd(class_name, values);

            var popup = bvr.src_el.getParent(".spt_popup");
            spt.popup.close(popup);

            '''
        } )
        button.add_style("display: inline-block")

 
        return top


class UserPanelCreatorCmd(Command):

    def execute(self):

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
            raise Exception("Panel with name [%s] already exists" % name)


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
    print(xml.to_string())

