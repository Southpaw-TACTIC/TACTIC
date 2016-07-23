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


class SwapDisplayWdg(BaseRefreshWdg):
    '''This swap display is a very light version which makes use of
    relay behaviors to significantly reduce the number of behaviors
    required'''

    def init(my):
        my.on_wdg = None
        my.off_wdg = None
        my.title_wdg = None
        my.behavior_top = None
        my.content_id = None
        my.inner = DivWdg()

    def set_default_wdg(my):
        theme = DivWdg().get_theme()
        if theme == "default":
            my.on_wdg = IconWdg('open', IconWdg.ARROWHEAD_DARK_DOWN)
            my.off_wdg = IconWdg('closed', IconWdg.ARROWHEAD_DARK_RIGHT)
        else:
            my.on_wdg = IconWdg('open', IconWdg.INFO_OPEN_SMALL)
            my.off_wdg = IconWdg('closed', IconWdg.INFO_CLOSED_SMALL)

    def set_display_wdgs(my, on_wdg, off_wdg):
        my.on_wdg = on_wdg
        my.off_wdg = off_wdg

    def set_on(my, flag=True):
        my.kwargs["is_on"] = flag

    def set_off(my, flag=False):
        my.kwargs["is_on"] = flag

    def set_title_wdg(my, title):
        my.title_wdg = title

    def set_content_id(my, content_id):
        my.content_id = content_id

    def set_behavior_top(my, behavior_top):
        my.behavior_top = behavior_top

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


    def add_behavior(my, behavior):
        my.top.add_behavior(behavior)

    def add_class(my, class_name):
        my.inner.add_class(class_name)

    def add_attr(my, name, value):
        my.inner.add_attr(name, value)





    def get_display(my):
        top = my.top
        top.add_class("hand")

        inner = my.inner
        top.add(inner)
        inner.add_class("spt_swap_top")

        table = Table()
        inner.add(table)
        table.add_color("color", "color")
        table.add_class("SPT_DTS")
        table.add_row()
        td = table.add_cell()

        title = my.kwargs.get("title")

        # determine whether this widget is on or off
        is_on = my.kwargs.get("is_on")
        if is_on in [True, "true"]:
            is_on = True
        else:
            is_on = False

        if not my.on_wdg or not my.off_wdg:
            my.set_default_wdg()


        # add the content id
        if my.content_id:
            inner.add_attr("spt_content_id", my.content_id)


        # add the behaviors
        if not my.behavior_top:
            my.handle_top(top)

        on_div = DivWdg()
        td.add(on_div)
        on_div.add_class("SPT_SWAP_ON")


        off_div = DivWdg()
        td.add(off_div)
        off_div.add_class("SPT_SWAP_OFF")

        if is_on:
            off_div.add_style("display: none")
            inner.add_attr("spt_state", "on")
        else:
            on_div.add_style("display: none")
            inner.add_attr("spt_state", "off")


        on_div.add( my.on_wdg )
        off_div.add( my.off_wdg )


        # handle an icon
        icon_str = my.kwargs.get("icon")
        if icon_str and isinstance(icon_str, basestring):
            icon_div = DivWdg()
            icon = IconWdg(title, eval("IconWdg.%s" % icon_str) )
            icon_div.add(icon)
            td = table.add_cell(icon_div)
            icon_div.add_style("margin-left: -6px")

        elif icon_str:
            td = table.add_cell(icon_str)
            icon_str.add_style("margin-left: -6px")

        else:
            show_border = my.kwargs.get("show_border")
            if show_border in [True, 'true']:
                on_div.add_border()
                off_div.add_border()

            on_div.add_style("width: 16")
            on_div.add_style("height: 16")
            on_div.add_style("overflow: hidden")
            off_div.add_style("width: 16")
            off_div.add_style("height: 16")
            off_div.add_style("overflow: hidden")


        if my.title_wdg:
            td = table.add_cell(my.title_wdg)
        else:
            td = table.add_cell(title)



        return top


class TestSwapWdg(BaseRefreshWdg):

        def get_display(my):

            top = my.top
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


