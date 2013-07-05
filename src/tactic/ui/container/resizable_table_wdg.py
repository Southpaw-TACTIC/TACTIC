############################################################
#
# Copyright (c) 2005, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#
__all__ = ["ResizableTableWdg", "TestResizableTableWdg"]


from pyasm.web import Table, DivWdg
from pyasm.widget import IconWdg
from tactic.ui.common import BaseRefreshWdg


class ResizableTableWdg(BaseRefreshWdg):
    def __init__(my, **kwargs):
        my.table = Table()
        my.table.add_style("border-collapse: collapse")
        my.table.add_style("padding: 0px")
        my.table.set_attr("cellpadding", "0px")
        my.table.set_attr("cellspacing", "0px")
        my.is_first_row = True
        my.hilight = my.table.get_color("background", -40)
        super(ResizableTableWdg, my).__init__(**kwargs)


    def set_style(my, name, value=None):
        my.table.set_style(name, value)

    def set_max_width(my):
        my.table.set_max_width()

    def add_class(my, name):
        my.table.add_class(name)

    def get_display(my):
        top = DivWdg()

        my.table.add_class("spt_resizable_table_top")


        my.table.add_behavior( {
        'type': 'load',
        'cbjs_action': my.get_onload_js()
        } )

        top.add(my.table)

        return top


    def set_keep_table_size(my):
        my.table.add_class("spt_resizable_keep_size")


    def add_color(my, color, modifier=0):
        my.table.add_color(color, modifier)

    def add_border(my, modifier=0):
        my.table.add_border(modifier=modifier)

    def add_style(my, name, value=None):
        my.table.add_style(name, value=value)




    def add_row(my, resize=True):

        # add resize row
        if not my.is_first_row and resize == True:
            tr, td = my.table.add_row_cell()
            td.add_style("height: 3px")
            td.add_style("min-height: 3px")
            td.add_style("cursor: n-resize")

            tr.add_behavior( {
            'type': 'drag',
            'cb_set_prefix': 'spt.resizable_table.row_drag'
            } )

            tr.add_behavior( {
            'type': 'hover',
            'hilight': my.hilight,
            'cbjs_action_over': '''
            var color = bvr.src_el.getStyle("background-color");
            bvr.src_el.setStyle("background-color", bvr.hilight);
            bvr.src_el.setAttribute("spt_last_background", color);
            ''',
            'cbjs_action_out': '''
            var color = bvr.src_el.getAttribute("spt_last_background");
            bvr.src_el.setStyle("background-color", color);
            '''
            } )

            icon = IconWdg("Drag to Resize", IconWdg.RESIZE_VERTICAL)
            td.add(icon)
            td.add_style("text-align: center")

        content_tr = my.table.add_row()

        my.is_first_row = False
 
        return content_tr


    def add_resize_row(my):
        tr, td = my.table.add_row_cell()
        td.add_style("height: 3px")
        td.add_style("min-height: 3px")
        td.add_style("cursor: n-resize")

        tr.add_behavior( {
        'type': 'drag',
        'cb_set_prefix': 'spt.resizable_table.row_drag'
        } )

        tr.add_behavior( {
        'type': 'hover',
        'hilight': my.hilight,
        'cbjs_action_over': '''
        var color = bvr.src_el.getStyle("background-color");
        bvr.src_el.setStyle("background-color", bvr.hilight);
        bvr.src_el.setAttribute("spt_last_background", color);
        ''',
        'cbjs_action_out': '''
        var color = bvr.src_el.getAttribute("spt_last_background");
        bvr.src_el.setStyle("background-color", color);
        '''
        } )
        icon = IconWdg("Drag to Resize", IconWdg.RESIZE_VERTICAL)
        td.add(icon)

        return tr, td


    def add_cell(my, widget=None, resize=True):
        td_content = my.table.add_cell()
        td_content.add_style("vertical-align: top")

        if not resize:
            return td_content

        # add resize cell
        td = my.table.add_cell()
        td.add_style("width: 4px")
        td.add_style("min-width: 4px")
        td.add_style("cursor: e-resize")

        icon_div = DivWdg()
        icon_div.add_style("width: 4px")
        icon_div.add_style("overflow: hidden")
        icon = IconWdg("Drag to Resize", IconWdg.RESIZE_HORIZ)
        icon_div.add(icon)
        td.add(icon_div)

        td.add_style("vertical-align: middle")

        td.add_behavior( {
        'type': 'drag',
        'cb_set_prefix': 'spt.resizable_table.cell_drag'
        } )


        td.add_behavior( {
        'type': 'hover',
        'hilight': my.hilight,
        'cbjs_action_over': '''
        var color = bvr.src_el.getStyle("background-color");
        bvr.src_el.setStyle("background-color", bvr.hilight);
        bvr.src_el.setAttribute("spt_last_background", color);
        ''',
        'cbjs_action_out': '''
        var color = bvr.src_el.getAttribute("spt_last_background");
        bvr.src_el.setStyle("background-color", color);
        '''
        } )



        if widget:
            td_content.add(widget)

        
        return td_content


    def get_onload_js(my):
        return r'''

spt.resizable_table = {}


spt.resizable_table.drag_data = {}

spt.resizable_table.cell_drag_setup = function( evt, bvr, mouse_411) {
    var mouse_x = mouse_411.curr_x;
    var mouse_y = mouse_411.curr_y;
    var sibling = bvr.src_el.getPrevious();
    var table = bvr.src_el.getParent(".spt_resizable_table_top");

    var data = spt.resizable_table.drag_data;
    data.resize_td = sibling;
    data.table = table;
    data.start_mouse_x = mouse_x;
    data.start_mouse_y = mouse_y;

    data.start_size = sibling.getSize();
    data.start_table_size = table.getSize();

    data.resize_children = data.resize_td.getElements(".spt_resizable");

}

spt.resizable_table.cell_drag_motion = function( evt, bvr, mouse_411) {
    var data = spt.resizable_table.drag_data;

    var mouse_x = mouse_411.curr_x;
    var mouse_y = mouse_411.curr_y;

    var dx = mouse_x - data.start_mouse_x;
    var dy = mouse_y - data.start_mouse_y;

    var new_width = data.start_size.x + dx;
    if (new_width < 50) {
        if (spt.browser.is_Qt()) {
            new_width = 1;
        }
        else {
            new_width = 0;
        }
    }

    data.resize_td.setStyle("width", new_width);

    if (!data.table.hasClass("spt_resizable_keep_size") ) {
        data.table.setStyle("width", data.start_table_size.x + dx);
    }

    for (var i = 0; i < data.resize_children.length; i++) {
        var child = data.resize_children[i];
        // special code for pipelines
        if (child.hasClass("spt_pipeline_resize")) {
            spt.pipeline.init(child);
            var size = spt.pipeline.get_canvas_size();
            spt.pipeline.set_size(new_width, size.y);
        }
        else {
            child.setStyle("width", new_width);
        }
    }

}



spt.resizable_table.row_drag_setup = function( evt, bvr, mouse_411) {
    var mouse_x = mouse_411.curr_x;
    var mouse_y = mouse_411.curr_y;
    var sibling = bvr.src_el.getPrevious();

    var data = spt.resizable_table.drag_data;
    data.resize_td = sibling;
    data.start_mouse_x = mouse_x;
    data.start_mouse_y = mouse_y;

    data.start_size = sibling.getSize();

    data.resize_children = data.resize_td.getElements(".spt_resizable");

}

spt.resizable_table.row_drag_motion = function( evt, bvr, mouse_411) {
    var data = spt.resizable_table.drag_data;

    var mouse_x = mouse_411.curr_x;
    var mouse_y = mouse_411.curr_y;

    var dx = mouse_x - data.start_mouse_x;
    var dy = mouse_y - data.start_mouse_y;

    var new_height = data.start_size.y + dy;
    data.resize_td.setStyle("height", new_height);

    for (var i = 0; i < data.resize_children.length; i++) {
        var child = data.resize_children[i];
        // special code for pipelines
        if (child.hasClass("spt_pipeline_resize")) {
            spt.pipeline.init(child);
            var size = spt.pipeline.get_canvas_size();
            spt.pipeline.set_size(size.x, new_height);
        }
        else {
            child.setStyle("height", new_height);
        }

    }
}



        '''


class TestResizableTableWdg(BaseRefreshWdg):

    def get_display(my):
        top = DivWdg()

        table = ResizableTableWdg()
        top.add(table)

        table.add_row()
        td = table.add_cell()
        td.add("This is the morning after")
        td.add_border()
        td.add_style("padding: 3px")
        td.add_style("min-width: 150px")
        td.add_style("width: 150px")

        td = table.add_cell()
        td.add_border()

        div = DivWdg()
        div.add_style("min-height: 200px")
        div.add_style("min-width: 200px")
        div.add("Content")
        td.add(div)


        table.add_row()
        td = table.add_cell()
        td.add_border()
        td.add_attr("colspan", "3")

        div = DivWdg()
        td.add(div)
        div.add_style("min-height: 200px")
        div.add("This is the night before")



        return top


