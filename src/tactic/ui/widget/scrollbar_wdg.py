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

__all__ = ['ScrollbarWdg', 'TestScrollbarWdg']

from tactic.ui.common import BaseRefreshWdg

from pyasm.web import DivWdg


class TestScrollbarWdg(BaseRefreshWdg):

    def get_display(self):

        top = self.top
        top.add_style("width: 600px")
        top.add_style("height: 400px")




        return top


class ScrollbarWdg(BaseRefreshWdg):

    def get_display(self):

        top = self.top
        top.add_class("spt_scrollbar_top")

        content = self.kwargs.get("content")
        content_class = self.kwargs.get("content_class")
        if not content_class:
            content_class = "spt_content"


        width = 8 
        top.add_style("width: %s" % width)
        top.add_style("position: absolute")
        top.add_style("top: 0px")
        top.add_style("right: 0px")

        top.add_color("background", "background")
        top.add_style("margin: 3px 5px")
        top.add_style("opacity: 0.0")

        top.add_behavior( {
            'type': 'load',
            'cbjs_action': self.get_onload_js()
        } )


        top.add_behavior( {
        'type': 'load',
        'content_class': content_class,
        'cbjs_action': '''
        var parent = bvr.src_el.getParent("." + bvr.content_class);
        var size = parent.getSize();
        bvr.src_el.setStyle("height", size.y);

        var scrollbar = parent.getElement(".spt_scrollbar_top");

        parent.addEvent("mouseenter", function() {
            new Fx.Tween(scrollbar, {duration: 250}).start("opacity", 1.0);
        } );
        parent.addEvent("mouseleave", function() {
            new Fx.Tween(scrollbar, {duration: 250}).start("opacity", 0.0);
        } );


        parent.addEvent("keypress", function(evt) {
            new Fx.Tween(scrollbar, {duration: 250}).start("opacity", 0.0);
            console.log(evt);
        } );

        parent.addEvent("mousewheel", function(evt) {
            evt.stopPropagation();
            spt.scrollbar.content = parent;
            if (evt.wheel == 1) {
                spt.scrollbar.scroll(15)
            }
            else {
                spt.scrollbar.scroll(-15)
            }
        } );



        '''
        } )



        bar = DivWdg()
        bar.add_class("spt_scrollbar")
        bar.add_class("hand")
        top.add(bar)
        bar.add_style("width: %s" % width)
        bar.add_style("height: 30px")
        bar.add_style("border: solid 1px black")
        bar.add_color("background", "background3")
        #bar.add_border()
        bar.add_style("border-radius: 5")
        bar.add_style("position: absolute")
        bar.add_style("top: 0px")


        top.add_behavior( {
            'type': 'smart_drag',
            'bvr_match_class': 'spt_scrollbar',
            'ignore_default_motion' : True,
            "cbjs_setup": 'spt.scrollbar.drag_setup( evt, bvr, mouse_411 );',
            "cbjs_motion": 'spt.scrollbar.drag_motion( evt, bvr, mouse_411 );'
        } )


        



        return top



    def get_onload_js(self):

        return r'''

spt.scrollbar = {};

spt.scrollbar.mouse_start_y = null;
spt.scrollbar.el_start_y = null;
spt.scrollbar.top = null;
spt.scrollbar.content = null;

spt.scrollbar.drag_setup = function(evt, bvr, mouse_411) {
    spt.scrollbar.mouse_start_y = mouse_411.curr_y;
    var src_el = spt.behavior.get_bvr_src( bvr );
    var pos_y = parseInt(src_el.getStyle("top").replace("px", ""));
    spt.scrollbar.el_start_y = pos_y;

    spt.scrollbar.content = $("spt_SCROLL");
    spt.scrollbar.top = src_el.getParent(".spt_scrollbar_top")


}


spt.scrollbar.drag_motion = function(evt, bvr, mouse_411) {
    var src_el = spt.behavior.get_bvr_src( bvr );
    var dy = mouse_411.curr_y - spt.scrollbar.mouse_start_y;
    var pos_y = spt.scrollbar.el_start_y + dy;
    if (pos_y < 0) {
        return;
    }
    var content = spt.scrollbar.content;

    var content_size = spt.scrollbar.content.getSize();
    var top_size = spt.scrollbar.top.getSize();
    var bar_size = src_el.getSize();
    if (pos_y > top_size.y - bar_size.y - 5) {
        return;
    }

    bvr.src_el.setStyle("top", pos_y);
    //var content = bvr.src_el.getParent(".spt_content");
    content.setStyle("margin-top", -dy);
}


spt.scrollbar.scroll = function(dy) {
    spt.scrollbar.content = $("spt_SCROLL");
    var content = spt.scrollbar.content;
    var pos_y = parseInt(content.getStyle("margin-top").replace("px", ""));
    content.setStyle("margin-top", pos_y + dy);

}




        '''




