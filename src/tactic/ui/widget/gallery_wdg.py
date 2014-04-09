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


__all__ = ['GalleryWdg']

from pyasm.web import HtmlElement, DivWdg, Table
from pyasm.widget import TextWdg, IconWdg

from tactic.ui.common import BaseRefreshWdg



class GalleryWdg(BaseRefreshWdg):

    def get_display(my):

        top = my.top

        inner = DivWdg()
        top.add(inner)
        inner.add_style("position: fixed")
        inner.add_style("top: 0")
        inner.add_style("left: 0")
        inner.add_style("width: 100%")
        inner.add_style("height: 100%")
        inner.add_style("background: rgba(0,0,0,0.5)")
        inner.add_style("z-index: 1000")
        inner.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            spt.behavior.destroy_element(bvr.src_el);
            '''
        } )


        icon = IconWdg(title="Previous", icon=IconWdg.G_LEFT)
        inner.add(icon)
        icon = IconWdg(title="Next", icon=IconWdg.G_RIGHT)
        inner.add(icon)


        scroll = DivWdg()
        inner.add(scroll)
        scroll.set_box_shadow()

        width = my.kwargs.get("width")
        height = my.kwargs.get("height")
        if not width:
            width = 640
        scroll.add_style("width: %s" % width)
        if height:
            scroll.add_style("height: %s" % height)
        scroll.add_style("overflow-x: hidden")
        scroll.add_style("overflow-y: hidden")
        scroll.add_style("background: #000")

        #scroll.add_style("position: absolute")
        scroll.add_style("margin-left: auto")
        scroll.add_style("margin-right: auto")



        paths = my.kwargs.get("paths")
        paths = [
            'http://192.168.0.191/assets/test/store/The%20Boxter_v001.jpg',
            'http://192.168.0.191/assets/test/store/Another%20one_v001.jpg',
            'http://192.168.0.191/assets/test/store/Whatever_v001.jpg'
        ]



        total_width = width * len(paths)

        content = DivWdg()
        scroll.add(content)
        content.add_class("spt_gallery_scroll")

        content.add_style("width: %s" % total_width)

        scroll.add_behavior( {
            'type': 'load',
            'cbjs_action': '''
            bvr.src_el.getElement(".spt_input").focus();
            '''
        } )
 
        scroll.add_behavior( {
            'type': 'mouseenter',
            'cbjs_action': '''
            bvr.src_el.getElement(".spt_input").focus();
            '''
        } )
        scroll.add_behavior( {
            'type': 'mouseleave',
            'cbjs_action': '''
            bvr.src_el.getElement(".spt_input").blur();
            '''
        } )



        input = TextWdg("keydown")
        content.add(input)
        input.add_style("position: absolute")
        input.add_style("left: -5000px")

        input.add_behavior( {
            'type': 'keydown',
            'cbjs_action': '''
            var key = evt.key;
            var top = bvr.src_el.getParent(".spt_gallery_scroll");
            var pos = top.getStyle("margin-left");
            pos = parseInt(pos.replace("px", ""))

            var width = 640;

            if (key == "left") {
                new Fx.Tween(top,{duration: 250}).start("margin-left", pos+width);
            }
            else if (key == "right") {
                new Fx.Tween(top,{duration: 250}).start("margin-left", pos-width);
            }

            '''
        } )




        content.add_behavior({
            'type': 'load',
            'cbjs_action': '''
            // find all of the widths of the images

            '''
        } )
        for path in paths:
            path_div = DivWdg()
            content.add(path_div)
            path_div.add_style("float: left")

            path_div.add_style("width: %s" % width)
            if height:
                path_div.add_style("height: %s" % height)

            img = HtmlElement.img(path)
            path_div.add(img)
            img.add_style("width: 100%")
            #img.add_style("height: 100%")


        return top



