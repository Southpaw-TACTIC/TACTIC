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

        activator = IconButtonWdg( name="Layout Switcher", icon="BS_SEARCH")
        top.add(activator)

        activator.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_switcher_top");
            var menu = top.getElement(".spt_switcher_menu");
            menu.setStyle("display", "");
            var pos = bvr.src_el.getPosition();

            menu.position({x: 0, y: 35}, pos);
            '''
        } )


        style = HtmlElement.style('''

.spt_switcher_button {
  float: right;
  padding: 5px;
  cursor: pointer;
}


.spt_switcher_top {
  position: relative;
}

.spt_switcher_menu {
  margin-top: 15px;
  padding: 0px 0px;
  border: solid 1px #CCC;
  width: 200px;
  height: auto;
  position: absolute;
  right: 5px;
  background: #FFF;
  z-index: 2;
  text-align: center;

}

.spt_switcher_menu .spt_switcher_item {
  padding: 10px 0px;
  cursor: pointer;
}


.spt_switcher_menu .spt_popup_pointer{
  z-index: 10;
  margin-top: -15px;
}

.spt_switcher_menu .spt_first_arrow_div{
    border-color: rgba(0, 0, 0, 0) rgba(0, 0, 0, 0) #ccc;
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

        ''')
        top.add(style)

        config_xml = my.kwargs.get("config_xml")
        my.view = 'tab'

        config = WidgetConfig.get(view=my.view, xml=config_xml)
        element_names = config.get_element_names()


        menu_wdg = DivWdg()
        top.add(menu_wdg)
        menu_wdg.add_class("spt_switcher_menu")

        menu_wdg.add_style("display: none")

        pointer_wdg = DivWdg()
        menu_wdg.add(pointer_wdg)
        pos = 10 
        pointer_wdg.add_style("margin-left: %spx" % pos)
        pointer_wdg.add_class("spt_popup_pointer")
        pointer_wdg.add('''
            <div class="spt_first_arrow_div"> </div>
            <div class="spt_second_arrow_div"> </div>
        ''')

        #menu_wdg.add("<br clear='all'/>")

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


            target = attrs.get("target")
            if not target:
                target = "spt_content"


            item_div.add_class("tactic_load")

            display_class = config.get_display_handler(element_name)
            display_options = config.get_display_options(element_name)

            item_div.add_behavior( {
                'type': 'click_up',
                'class_name': display_class,
                'display_options': display_options,
                'target': target,
                'cbjs_action': '''
                var class_name = bvr.class_name;
                var kwargs = bvr.display_options;

                var target_class = bvr.target;
                if (! target_class ) {
                    target_class = "spt_content";
                }

                if (target_class.indexOf(".") != "-1") {
                    var parts = target_class.split(".");
                    var top = bvr.src_el.getParent("."+parts[0]);
                    var target = top.getElement("."+parts[1]);  
                }
                else {
                    var target = $(document.body).getElement("."+target_class);
                }

                spt.panel.load(target, bvr.class_name, bvr.display_options);

                var top = bvr.src_el.getParent(".spt_switcher_menu");
                top.setStyle("display", "none");

                
                '''
            } )



        """ 
        menu_wdg.add( '''
        <div class="spt_switcher_menu" style="display: block">
          <div style="margin-left: 155px;" class="spt_popup_pointer">
            <div class="spt_first_arrow_div"> </div>
            <div class="spt_second_arrow_div"> </div>
          </div>
          <br clear="all"/>
          <div class="spt_switcher_item tactic_load tactic_hover" view="hr.employee.my_documents">Tile</div>
          <hr style="margin: 0px 10px;"/>
          <div class="spt_switcher_item tactic_load tactic_hover" view="hr.employee.my_documents" layout="default">Table</div>
          <hr style="margin: 0px 10px;"/>
          <div class="spt_switcher_item tactic_load tactic_hover" view="hr.employee.my_profile">My Profile</div>
        </div>
        ''')
        """

        return top



