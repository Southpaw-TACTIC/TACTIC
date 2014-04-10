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

__all__ = ['PlanWdg']

from pyasm.web import DivWdg, HtmlElement

from tactic.ui.common import BaseRefreshWdg


class PlanWdg(BaseRefreshWdg):

    def get_display(my):

        top = my.top

        inner = DivWdg()
        top.add(inner)

        inner.add_behavior( {
            'type': 'load',
            'cbjs_action': my.get_onload_js()
        } )

        width = "100%"
        height = "100%"

        inner.add_style("width: %s" % width)
        inner.add_style("height: %s" % height)
        inner.add_style("overflow: hidden")



        content = DivWdg()
        inner.add(content)
        content.add_class("spt_content")
        content.add_style("width: %s" % width)
        content.add_style("height: %s" % height)
        content.add_style("position: relative")

        content.add_behavior( {
            'type': 'load',
            'cbjs_action': '''
            spt.drag.load(bvr.src_el);
            '''
        } )
        content.add_behavior( {
            'type': 'wheel',
            'cbjs_action': '''
            spt.drag.wheel(evt, bvr);
            '''
        } )

        inner.add_relay_behavior( {
            'type': 'dblclick',
            'bvr_match_class': 'spt_content',
            'cbjs_action': '''
            spt.drag.dblclick(evt, bvr);
            '''
        } )


        src = my.kwargs.get("src")
        if not src:
            src = DivWdg()
            src.add("No Content")

        img = HtmlElement.img(src=src)
        content.add(img)
        img.add_style("width: 100%")
        img.add_style("height: 100%")


        return top



    def get_onload_js(my):

        return r'''

spt.drag = {};
spt.drag.is_dragging = false;
spt.drag.should_drag = true;


spt.drag.load = function(el) {
    var x = el.makeDraggable({
        onStart: function(draggable) {
            if (!spt.drag.should_drag) {
                x.stop();
                spt.drag.should_drag = true;
                return;
            }
            console.log("start: " + spt.drag.is_dragging);
            spt.drag.is_dragging = true;
        },
        onDrag: function(draggable) {
            console.log("dragging");
        },
        onDrop: function(draggable, droppable){
            spt.drag.is_dragging = false;
            console.log("drop");
        }
    });
}


spt.drag.wheel = function(evt, bvr) {

    var pos = bvr.src_el.getPosition();
    var size = bvr.src_el.getSize();
    if (size.x == 0) {
        size = bvr.src_el.getParent().getSize();
    }
    console.log(size);
    var mouse = evt.client;

    var mult = 0.9;

    var scale;
    if (evt.wheel > 0) {
        scale = 1/mult;
    }
    else {
        scale = mult;
    }
    console.log(scale);

    size = {x: size.x*scale, y: size.y*scale};
    var px = mouse.x - ( mouse.x - pos.x ) * (scale*size.x) / size.x;
    var py = mouse.y - ( mouse.y - pos.y ) * (scale*size.y) / size.y;

    bvr.src_el.setStyle("width", size.x);
    bvr.src_el.setStyle("height", size.y);
    bvr.src_el.setStyle("left", px);
    bvr.src_el.setStyle("top", py);

}


spt.drag.dblclick = function(evt, bvr) {

    // dblclick

    if (spt.drag.is_dragging == true) {
    }
    else {

    // find out current position of src
    var pos = bvr.src_el.getPosition();
    var size = bvr.src_el.getSize();
    var mouse = evt.client;

    var scale = 5;
    var px = mouse.x - ( mouse.x - pos.x ) * (scale*size.x) / size.x;
    var py = mouse.y - ( mouse.y - pos.y ) * (scale*size.y) / size.y;

    var mid = scale * (1 + scale) / 2 * 100;


    var width = bvr.src_el.getStyle("width");
    //width = parseInt(width.replace("%",""));

    if (width == '100%' ) {
        new Fx.Tween(bvr.src_el, {duration: 1500, unit: '%'}).start('width', (scale*100) + '%');
        new Fx.Tween(bvr.src_el, {duration: 1500, unit: '%'}).start('height', (scale*100) + '%');
        new Fx.Tween(bvr.src_el, {duration: 1500}).start('top', py);
        new Fx.Tween(bvr.src_el, {duration: 1500}).start('left', px);

        /*
        new Fx.Morph(bvr.src_el, {duration: 1500}).start({
            'width': size.x * scale,
            'height': size.y * scale,
            'top': py,
            'left': px
        });
        */
    }
    else {
        new Fx.Tween(bvr.src_el, {duration: 1500, unit: '%'}).start('width', '100%');
        new Fx.Tween(bvr.src_el, {duration: 1500, unit: '%'}).start('height', '100%');
        new Fx.Tween(bvr.src_el, {duration: 1500}).start('top', 0);
        new Fx.Tween(bvr.src_el, {duration: 1500}).start('left', 0);
    }

    }

}

    ''' 
