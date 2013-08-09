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
__all__ = ["EmbedWdg"]

from pyasm.common import Environment
from pyasm.web import DivWdg, HtmlElement, SpanWdg

from tactic.ui.common import BaseRefreshWdg

import os


class EmbedWdg(BaseRefreshWdg):

    def get_args_keys(my):
        return {
            }

    def add_style(my, name, value=None):
        my.top.add_style(name, value)


    def add_class(my, name):
        my.top.add_class(name)



    def get_display(my):

        top = my.top

        src = my.kwargs.get("src")
        file = my.kwargs.get("file")
        if file:
            src = file.get_web_path()


        height = my.kwargs.get("height")
        width = my.kwargs.get("width")


        #div = DivWdg()
        #top.add(div)
        div = top
        div.add_style("margin-left: auto")
        div.add_style("margin-right: auto")
        div.add_style("text-align: center")
        if height:
            div.add_style("height", height)
        if width:
            div.add_style("width", width)


        parts = os.path.splitext(src)
        ext = parts[1]
        ext = ext.lower()

        if ext in ['.png', '.jpeg', '.jpg', '.gif']:
            embed = HtmlElement.img(src)
        else:
            embed = HtmlElement.embed(src)
        div.add(embed)

        embed.add_behavior( {
            'type': 'click_up',
            'src': src,
            'cbjs_action': '''
            window.open(bvr.src);
            '''
        } )
        embed.add_class("hand")




        #embed.set_box_shadow("1px 1px 1px 1px")
        embed.add_style("height", "100%")
        #embed.add_style("width", "100%")

        return top

    
