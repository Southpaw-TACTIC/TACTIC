###########################################################
#
# Copyright (c) 2014, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#


__all__ = ['ArrowWdg']


from pyasm.web import DivWdg

from tactic.ui.common import BaseRefreshWdg



class ArrowWdg(BaseRefreshWdg):

    def get_display(my):

        top = my.top

        offset_x = my.kwargs.get("offset_x")
        if not offset_x:
            offset_x = 30

        offset_y = my.kwargs.get("offset_y")
        if not offset_y:
            offset_y = 0


        size = my.kwargs.get("size")
        if not size:
            size = 15 

        color = my.kwargs.get("color")
        if not color:
            color = top.get_color("background")

        border_color = my.kwargs.get("border_color")
        if not border_color:
            border_color = top.get_color("border")

 
        offset_y -= size

        a = DivWdg() 
        top.add(a)
        a.add(" ")

        a.add_style("border-color: rgba(0, 0, 0, 0) rgba(0, 0, 0, 0) %s" % border_color)
        a.add_style("border-style: dashed dashed solid")
        a.add_style("border-width: 0 %spx %spx" % (size, size))
        a.add_style("height: 0")
        a.add_style("left: %spx" % offset_x)
        a.add_style("position: absolute")
        a.add_style("top: %spx" % offset_y)
        a.add_style("width: 0")
        a.add_style("z-index: 1")

        b = DivWdg() 
        top.add(b)
        b.add(" ")
        b.add_style("border-color: rgba(0, 0, 0, 0) rgba(0, 0, 0, 0) %s" % color)
        b.add_style("border-style: dashed dashed solid")
        b.add_style("border-width: 0 %spx %spx" % (size, size))
        b.add_style("height: 0")
        b.add_style("left: %spx" % offset_x)
        b.add_style("position: absolute")
        b.add_style("top: %spx" % (offset_y+1))
        b.add_style("width: 0")
        b.add_style("z-index: 1")

        #b.set_style( """border-color: rgba(0, 0, 0, 0) rgba(0, 0, 0, 0) #FFFFFF; border-style: dashed dashed solid; border-width: 0 8px 8px; height: 0; left: 30px; position: absolute; top: -7px; width: 0; z-index: 1;""")

        return top




