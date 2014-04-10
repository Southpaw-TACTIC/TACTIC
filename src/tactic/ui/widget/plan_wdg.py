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
        inner.add_class("spt_container")



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

    var container = bvr.src_el.getParent(".spt_container");
    var size = container.getSize();

    var mouse = evt.client;
    var container_pos = container.getPosition();
    mouse = {x: mouse.x - container_pos.x, y: mouse.y - container_pos.y};


    var scale = bvr.src_el.getAttribute("spt_scale");
    if (!scale) {
        scale = 1.0;
    }
    scale = parseFloat(scale);

    var mult = 0.95;

    var scale;
    if (evt.wheel > 0) {
        scale = scale/mult;
    }
    else {
        scale = scale*mult;
    }


    //spt.drag.zoom(bvr.src_el, scale, mouse);

    var px = mouse.x - ( mouse.x - container_pos.x ) * (scale*size.x) / size.x;
    var py = mouse.y - ( mouse.y - container_pos.y ) * (scale*size.y) / size.y;

    bvr.src_el.setStyle("width", (scale*100)+"%");
    bvr.src_el.setStyle("height", (scale*100)+"%");
    bvr.src_el.setStyle("left", px);
    bvr.src_el.setStyle("top", py);
    bvr.src_el.setAttribute("spt_scale", scale);

}


spt.drag.dblclick = function(evt, bvr) {

    // dblclick

    if (spt.drag.is_dragging == true) {
    }
    else {

    var container = bvr.src_el.getParent(".spt_container");

    // find out current position of src
    var container_pos = container.getPosition();
    var pos = bvr.src_el.getPosition(container);
    var size = bvr.src_el.getSize();
    var mouse = evt.client;
    mouse = {x: mouse.x - container_pos.x, y: mouse.y - container_pos.y};

    var scale = 5;
    var px = mouse.x - ( mouse.x - pos.x ) * (scale*size.x) / size.x;
    var py = mouse.y - ( mouse.y - pos.y ) * (scale*size.y) / size.y;

    var mid = scale * (1 + scale) / 2 * 100;


    var width = bvr.src_el.getStyle("width");
    //width = parseInt(width.replace("%",""));

    if (width == '100%' ) {
        new Fx.Tween(bvr.src_el, {duration: 500, unit: '%'}).start('width', (scale*100) + '%');
        new Fx.Tween(bvr.src_el, {duration: 500, unit: '%'}).start('height', (scale*100) + '%');
        new Fx.Tween(bvr.src_el, {duration: 500}).start('top', py);
        new Fx.Tween(bvr.src_el, {duration: 500}).start('left', px);

        /*
        new Fx.Morph(bvr.src_el, {duration: 500}).start({
            'width': size.x * scale,
            'height': size.y * scale,
            'top': py,
            'left': px
        });
        */
    }
    else {
        new Fx.Tween(bvr.src_el, {duration: 500, unit: '%'}).start('width', '100%');
        new Fx.Tween(bvr.src_el, {duration: 500, unit: '%'}).start('height', '100%');
        new Fx.Tween(bvr.src_el, {duration: 500}).start('top', 0);
        new Fx.Tween(bvr.src_el, {duration: 500}).start('left', 0);
    }

    }

}


spt.drag.zoom = function(content, scale, mouse) {

    var container = content.getParent(".spt_container");

    // find out current position of src
    var pos = content.getPosition(container);
    //var size = content.getSize();
    var size = container.getSize();

    // This is to find the position relative to the container, however,
    // mouse should already have that in this case
    //var container_pos = container.getPosition();
    //mouse = {x: mouse.x - container_pos.x, y: mouse.y - container_pos.y};

    var px = mouse.x - ( mouse.x - pos.x ) * (scale*size.x) / size.x;
    var py = mouse.y - ( mouse.y - pos.y ) * (scale*size.y) / size.y;

    var mid = scale * (1 + scale) / 2 * 100;

    var width = content.getStyle("width");
    //width = parseInt(width.replace("%",""));

    if (width == '100%' ) {
        new Fx.Tween(content, {duration: 1500, unit: '%'}).start('width', (scale*100) + '%');
        new Fx.Tween(content, {duration: 1500, unit: '%'}).start('height', (scale*100) + '%');
        new Fx.Tween(content, {duration: 1500}).start('top', py);
        new Fx.Tween(content, {duration: 1500}).start('left', px);

        /*
        new Fx.Morph(content, {duration: 1500}).start({
            'width': size.x * scale,
            'height': size.y * scale,
            'top': py,
            'left': px
        });
        */
    }
    else {
        new Fx.Tween(content, {duration: 1500, unit: '%'}).start('width', '100%');
        new Fx.Tween(content, {duration: 1500, unit: '%'}).start('height', '100%');
        new Fx.Tween(content, {duration: 1500}).start('top', 0);
        new Fx.Tween(content, {duration: 1500}).start('left', 0);
    }
}

    ''' 
