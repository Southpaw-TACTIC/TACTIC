############################################################
#
#    Copyright (c) 2010, Southpaw Technology
#                        All Rights Reserved
#
#    PROPRIETARY INFORMATION.  This software is proprietary to
#    Southpaw Technology, and is not to be reproduced, transmitted,
#    or disclosed in any way without written permission.
#
#

__all__ = ['DynamicListWdg']


from tactic.ui.common import BaseRefreshWdg

from pyasm.web import DivWdg
from pyasm.widget import CheckboxWdg, HiddenWdg, IconWdg, IconButtonWdg


class DynamicListWdg(BaseRefreshWdg):

    ARGS_KEYS = {
    'show_enabled': 'determines whether or not to show enabled checkboxes'
    }

    def init(my):
        my.items = []
        my.template = None

        my.show_enabled = my.kwargs.get('show_enabled')
        if my.show_enabled in ['true', True]:
            my.show_enabled = True
        else:
            my.show_enabled = False


    def add_item(my, item):
        my.items.append(item)

    def add_template(my, template):
        my.template = template

    def get_display(my):
        #assert my.template


        top = DivWdg()
        top.add_class("spt_list_top")

        if my.template:
            template_wdg = my.get_item_wdg(my.template, is_template=True)
            top.add(template_wdg )

        for item in my.items:
            item_wdg = my.get_item_wdg(item)
            top.add( item_wdg )

        return top



    def get_item_wdg(my, item, is_template=False):
        item_div = DivWdg()
        item_div.add_style("margin-top: 3px")

        if is_template == True:
            item_div.add_style("display: none")
            #item_div.add_style("border: solid 1px blue")
            item_div.add_class("spt_list_template_item")
        else:
            item_div.add_class("spt_list_item")

        outer = DivWdg()
        outer.add_style("float: left")
        outer.add_style("text-align: left")
        outer.add(item)


        if my.show_enabled:
            checkbox = CheckboxWdg("enabled")
            checkbox.add_style("float: left")
            checkbox.set_checked()
        else:
            checkbox = HiddenWdg("enabled")
        item_div.add(checkbox)

        #item_div.add(item)
        item_div.add(outer)


        add_wdg = DivWdg()
        add_wdg.add_class("hand")
        add_wdg.add_class("SPT_DTS")
        add_wdg.add("(+)")
        #from tactic.ui.widget import IconButtonWdg
        #button = IconButtonWdg(title="Add Entry", icon=IconWdg.ADD)
        #add_wdg.add(button)
        #button.add_behavior( {
        add_wdg.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_list_top");
            var template = top.getElement(".spt_list_template_item");
            var new_item = spt.behavior.clone(template);
            var item = bvr.src_el.getParent(".spt_list_item");
            new_item.removeClass("spt_list_template_item");
            new_item.addClass("spt_list_item")
            new_item.setStyle("display", "")
            //new_item.inject(top, 'bottom');
            new_item.inject(item, 'after');
            '''
        } )
        add_wdg.add_style("float: left")
        add_wdg.add_style("margin: 3px")
        item_div.add(add_wdg)



        remove_wdg = DivWdg()
        remove_wdg.add_class("hand")
        remove_wdg.add_class("SPT_DTS")
        remove_wdg.add("(-)")
        #button = IconButtonWdg(title="Remove Entry", icon=IconWdg.DELETE)
        #remove_wdg.add(button)
        #button.add_behavior( {
        remove_wdg.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_list_top");
            var items = top.getElements(".spt_list_item");
            if (items.length > 1) {
                var item = bvr.src_el.getParent(".spt_list_item");
                item.destroy();
            }
            '''
        } )
        remove_wdg.add_style("float: left")
        remove_wdg.add_style("margin: 3px")
        item_div.add(remove_wdg)
        item_div.add("<br clear='all'/>")

        return item_div


    def get_values_script(my):
        save_button = IconButtonWdg("Save Settings", IconWdg.SAVE)
        save_button.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            get_values = function() {
                var top = bvr.src_el.getParent(".spt_list_top");
                var elements = bvr.src_el.getElements(".spt_list_items");
                var data = [];
                for (var i=0; i<elements.length; i++) {
                    var values = spt.api.get_input_values(elements[i]);
                    data.push(values)
                }
                return data;
            }
            '''
        } )
        content_div.add(save_button)



