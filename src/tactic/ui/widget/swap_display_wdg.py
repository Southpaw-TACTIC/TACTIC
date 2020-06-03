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
__all__ = ["SwapDisplayWdg", "TestSwapWdg"]

from pyasm.web import DivWdg, HtmlElement, SpanWdg, Table
from pyasm.widget import IconWdg

from tactic.ui.common import BaseRefreshWdg

import six
basestring = six.string_types


class SwapDisplayWdg(BaseRefreshWdg):
    '''This swap display is a very light version which makes use of
    relay behaviors to significantly reduce the number of behaviors
    required'''

    def init(self):
        self.on_wdg = None
        self.off_wdg = None
        self.title_wdg = None
        self.behavior_top = None
        self.content_id = None
        self.inner = DivWdg()

    def set_default_wdg(self):
        theme = DivWdg().get_theme()
        if theme == "default":
            self.on_wdg = IconWdg('open', IconWdg.ARROWHEAD_DARK_DOWN)
            self.off_wdg = IconWdg('closed', IconWdg.ARROWHEAD_DARK_RIGHT)
        else:
            self.on_wdg = IconWdg('open', IconWdg.INFO_OPEN_SMALL)
            self.off_wdg = IconWdg('closed', IconWdg.INFO_CLOSED_SMALL)

            self.on_wdg = IconWdg('open', "FA_ANGLE_DOWN", size=12)
            self.off_wdg = IconWdg('closed', "FA_ANGLE_RIGHT", size=12)


    def set_display_wdgs(self, on_wdg, off_wdg):
        self.on_wdg = on_wdg
        self.off_wdg = off_wdg

    def set_on(self, flag=True):
        self.kwargs["is_on"] = flag

    def set_off(self, flag=False):
        self.kwargs["is_on"] = flag

    def set_title_wdg(self, title):
        self.title_wdg = title

    def set_content_id(self, content_id):
        self.content_id = content_id

    def set_behavior_top(self, behavior_top):
        self.behavior_top = behavior_top

    def handle_top(cls, top):

        behavior = {
            'type': 'click',
            'bvr_match_class': 'spt_swap_top',
            'cbjs_action': '''
            var top = bvr.src_el;

            var on = top.getElement(".SPT_SWAP_ON");
            var off = top.getElement(".SPT_SWAP_OFF");

            var state = top.getAttribute("spt_state");
            if (state == 'on') 
                state = 'off';
            else 
                state = 'on';
            if (state == 'on') {
                spt.show(on);
                spt.hide(off);
                top.setAttribute("spt_state", "on");
            }
            else {
                spt.show(off);
                spt.hide(on);
                top.setAttribute("spt_state", "off");
            }


            var content_id = top.getAttribute("spt_content_id");
            if (content_id) {
                if (state == 'on') {
                    spt.show( content_id )
                }
                else {
                    spt.hide( content_id )
                }
            }

            '''
        }
        #top.add_behavior(behavior)
        top.add_relay_behavior(behavior)

    handle_top = classmethod(handle_top)


    def add_behavior(self, behavior):
        self.top.add_behavior(behavior)

    def add_class(self, class_name):
        self.inner.add_class(class_name)

    def add_attr(self, name, value):
        self.inner.add_attr(name, value)





    def get_display(self):
        top = self.top
        top.add_class("hand")

        inner = self.inner
        top.add(inner)
        inner.add_class("spt_swap_top")

        table = DivWdg()
        table.add_style("display: flex")
        table.add_style("align-items: center")
        inner.add(table)
        table.add_style("width: 100%")
        table.add_class("SPT_DTS")

        title = self.kwargs.get("title")

        # determine whether this widget is on or off
        is_on = self.kwargs.get("is_on")
        if is_on in [True, "true"]:
            is_on = True
        else:
            is_on = False

        if not self.on_wdg or not self.off_wdg:
            self.set_default_wdg()


        # add the content id
        if self.content_id:
            inner.add_attr("spt_content_id", self.content_id)


        # add the behaviors
        if not self.behavior_top:
            self.handle_top(top)

        on_div = DivWdg()
        table.add(on_div)
        on_div.add_class("SPT_SWAP_ON")


        off_div = DivWdg()
        table.add(off_div)
        off_div.add_class("SPT_SWAP_OFF")

        if is_on:
            off_div.add_style("display: none")
            inner.add_attr("spt_state", "on")
        else:
            on_div.add_style("display: none")
            inner.add_attr("spt_state", "off")


        on_div.add( self.on_wdg )
        off_div.add( self.off_wdg )

        on_div.add_style("margin-left: 5px")
        on_div.add_style("margin-right: 3px")
        off_div.add_style("margin-left: 5px")
        off_div.add_style("margin-right: 3px")


        # handle an icon
        icon_str = self.kwargs.get("icon")
        if icon_str and isinstance(icon_str, basestring):
            icon_div = DivWdg()

            from tactic.ui.widget import IconButtonWdg

            if icon_str.startswith("BS_"):
                icon = IconButtonWdgWdg(name=title, icon=icon_str, size=12 )
                icon_div.add_style("margin: -2px 10px 0px 10px")
            else:
                icon = IconButtonWdg(name=title, icon=icon_str )
                icon_div.add_style("margin-left: -8px")

            icon_div.add(icon)
            table.add(icon_div)

        elif icon_str:
            table.add(icon_str)
            #icon_str.add_style("margin-left: -6px")

        else:
            show_border = self.kwargs.get("show_border")
            if show_border in [True, 'true']:

                on_div.add_style("border: solid 1px %s" % on_div.get_color("border") )
                on_div.add_style("border-radius: 20px")
                on_div.add_style("padding: 5px 3px")


                off_div.add_style("border: solid 1px %s" % off_div.get_color("border") )
                off_div.add_style("border-radius: 20px")
                off_div.add_style("padding: 5px 3px")



        if self.title_wdg:
            table.add(self.title_wdg)
        else:
            table.add(title)



        return top


class TestSwapWdg(BaseRefreshWdg):

        def get_display(self):

            top = self.top
            top.add_color("background", "background")
            top.add_style("padding: 5px")
            top.add_border()

            SwapDisplayWdg.handle_top(top)

            top.add_relay_behavior( {
                'type': 'click',
                'bvr_match_class': 'spt_swap_top',
                'cbjs_action': '''var top = bvr.src_el;
                if (['on', null].contains(top.getAttribute("spt_state")))
                    spt.alert('clicked open')
                '''
            } )




            for title in ['First', 'Second', 'Third', 'Fourth', 'Fifth', 'Sixth', 'Seventh']:
                swap = SwapDisplayWdg(title=title, icon='FILM')
                top.add(swap)
                swap.set_behavior_top(top)


                # handle hover behavior
                hover = top.get_color("background", -10)
                behavior = {
                    'type': 'hover',
                    'bvr_match_class': 'spt_swap_top',
                    'hover': hover,
                    'cbjs_action_over': '''bvr.src_el.setStyle('background', bvr.hover)''',
                    'cbjs_action_out': '''bvr.src_el.setStyle('background', '')''',
                }
                swap.add_behavior(behavior)




                content = DivWdg()
                unique_id = content.set_unique_id("content")
                swap.set_content_id(unique_id)

                content.add("This is content!!!!")
                top.add(content)
                content.add_style("display: none")


            return top


