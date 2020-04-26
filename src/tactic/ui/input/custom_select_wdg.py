###########################################################
#
# Copyright (c) 2005-2008, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#

__all__ = ['CustomSelectWdg']

from pyasm.common import Date, Common
from pyasm.web import Table, DivWdg, SpanWdg, WebContainer, Widget
from pyasm.widget import IconWdg, IconButtonWdg, BaseInputWdg, TextWdg, HiddenWdg
from tactic.ui.common import BaseRefreshWdg

import random

class CustomSelectWdg(BaseInputWdg):

    ARGS_KEYS = {
    }


    def __init__(self, name=None, **kwargs):
        if not name:
            name = kwargs.get("name")
        self.top = DivWdg()
        self.input = None
        self.kwargs = kwargs
        super(CustomSelectWdg, self).__init__(name)


    """
    def add_style(self, name, value=None):
        self.top.add_style(name, value)

    def set_input(self, input):
        self.input = input
        self.input.set_name(self.get_input_name() )

    def get_input(self):
        return self.input

    def add(self, widget):
        self.top.add(widget)

    """



    def get_display(self):
        top = self.top
        top.add_class("spt_input_top")
        top.add_style("position: relative")
        top.add_style("width: 150px")
        top.add_style("margin-top: -1px")
        top.add_style("margin-left: -1px")
        top.add_color("background", "background", -20)
        top.add_border()


        title = "Big"
        div = DivWdg()
        top.add(div)
        icon_div = DivWdg()
        div.add(icon_div)
        icon_div.add_style("width: 20px")
        icon_div.add_style("height: 21px")
        icon_div.add_style("padding-left: 3px")
        icon_div.add_style("margin: -3 6 0 -3")
        icon_div.add_color("background", "background", [+15, 0, 0])
        icon_div.add_style("float: left")
        icon_div.add_style("opacity: 0.5")
        icon = IconWdg("Select", IconWdg.FILM)
        icon_div.add(icon)

        div.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        var top = bvr.src_el.getParent(".spt_input_top");
        var content = spt.get_element( top, ".spt_input_content");

        spt.toggle_show_hide(content);
        spt.body.add_focus_element(content);

        content.position(top);
        '''
        } )



        div.add(title)
        div.add_class("hand")
        div.add_style("padding: 3px")
 




        #top.add( TextWdg("hello") )

        select_div = DivWdg()
        top.add(select_div)
        select_div.add_style("position: absolute")
        select_div.add_class("spt_input_content")
        select_div.add_color("background", "background")
        select_div.add_style("top: 0px")
        select_div.add_style("left: 0px")

        select_div.add_style("display: none")
        select_div.add_style("z-index: 1000")
        select_div.set_box_shadow()
        select_div.add_border()
        select_div.add_class("SPT_PUW")


        for title in ("Big", "Fat", "Cow", "Horse", "Donkeys"):
            div = DivWdg()
            select_div.add(div)

            icon_div = DivWdg()
            div.add(icon_div)
            icon_div.add_style("width: 20px")
            icon_div.add_style("height: 21px")
            icon_div.add_style("margin: -3 6 0 -3")
            icon_div.add_color("background", "background", [+15, 0, 0])
            icon_div.add_style("float: left")
            icon_div.add_style("opacity: 0.5")
            icon_div.add("&nbsp;")


            div.add(title)
            div.add_class("hand")
            div.add_style("padding: 3px")
            div.add_style("width: 100px")
            hover = div.get_color("background", [-30, -30, 20])
            div.add_behavior( {
            'type': 'hover',
            'hover': hover,
            'cbjs_action_over': '''
            bvr.src_el.setStyle("background", bvr.hover);
            ''',
            'cbjs_action_out': '''
            bvr.src_el.setStyle("background", "");
            '''
            } )


            div.add_behavior( {
                'type': 'click_up',
                'value': title,
                'cbjs_action': '''
                bvr.src_el.setStyle("background", "");
                var top_el = spt.get_parent(bvr.src_el, ".spt_input_top");
                var value_wdg = top_el.getElement(".spt_input_data");

                var content = spt.get_parent(bvr.src_el, ".spt_input_content");
                spt.hide(content);

                value_wdg.value = bvr.value;
                spt.dg_table.simple_edit_cell_cbk(top_el);
                '''
            } )

        # generally, some real input widget is needed store and transport
        # the data
        input = HiddenWdg(self.get_input_name() )
        input.add_class("spt_input_data")
        input.add_class("SPT_NO_RESIZE")
        input.add_behavior( {
        'type': 'change',
        'cbjs_action': '''
        var top_el = bvr.src_el.getParent(".spt_input_top");
        var value_wdg = top_el.getElement(".spt_input_data");
        spt.dg_table.edit.widget = top_el;
        spt.dg_table.inline_edit_cell_cbk( value_wdg );
        '''
        } )
        top.add(input)


        return top




