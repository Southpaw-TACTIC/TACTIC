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

    def get_display(my):

        top = my.top
        top.add_style("width: 600px")
        top.add_style("height: 400px")




        return top


class ScrollbarWdg(BaseRefreshWdg):

    def get_display(my):

        top = my.top

        width = 8 
        top.add_style("width: %s" % width)
        top.add_color("background", "background3")
        top.add_style("position: relative")
        top.add_style("margin: 3px 5px")

        top.add_behavior( {
            'type': 'load',
            'cbjs_action': my.get_onload_js()
        } )

        # FIXME: spt_content is hard coded
        top.add_behavior( {
        'type': 'load',
        'cbjs_action': '''
        var parent = bvr.src_el.getParent(".spt_content");
        var size = parent.getSize();
        bvr.src_el.setStyle("height", size.y);
        '''
        } )


        bar = DivWdg()
        bar.add_class("spt_scrollbar")
        top.add(bar)
        bar.add_style("width: %s" % width)
        bar.add_style("height: 30px")
        bar.add_border()
        top.add_color("background", "background")
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



    def get_onload_js(my):

        return r'''

spt.scrollbar = {};

spt.scrollbar.mouse_start_y = null;
spt.scrollbar.el_start_y = null;

spt.scrollbar.drag_setup = function(evt, bvr, mouse_411) {
    spt.scrollbar.mouse_start_y = mouse_411.curr_y;
    var src_el = spt.behavior.get_bvr_src( bvr );
    var pos_y = parseInt(src_el.getStyle("top").replace("px", ""));
    spt.scrollbar.el_start_y = pos_y;
}


spt.scrollbar.drag_motion = function(evt, bvr, mouse_411) {
    var src_el = spt.behavior.get_bvr_src( bvr );
    var dy = mouse_411.curr_y - spt.scrollbar.mouse_start_y;
    var pos_y = spt.scrollbar.el_start_y + dy;
    if (pos_y < 0) {
        return;
    }
    bvr.src_el.setStyle("top", pos_y);
}


        '''




