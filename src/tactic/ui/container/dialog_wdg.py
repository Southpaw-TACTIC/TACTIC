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
__all__ = ["TestDialogWdg", "DialogWdg"]

from pyasm.web import *
from pyasm.widget import IconWdg, IconButtonWdg, SelectWdg, ProdIconButtonWdg, TextWdg

from tactic.ui.common import BaseRefreshWdg

import random

class TestDialogWdg(BaseRefreshWdg):
    def get_display(my):
        top = DivWdg()
        top.add_class("spt_top")

        dialog = DialogWdg()
        dialog_id = dialog.get_id()

        # create the button
        button = DivWdg()
        button.add_style("padding: 5px")
        button.add_style("width: 30px")
        button.add_style("text-align: center")
        button.add_style("float: left")
        button.add_gradient("background", "background")
        button.add_border()
        top.add(button)
        icon = IconWdg("Press Me", IconWdg.ZOOM)
        icon.add_style("float: left")
        button.add(icon)
        icon = IconWdg("Press Me", IconWdg.INFO_OPEN_SMALL)
        icon.add_style("margin-left: -9px")
        button.add(icon)
        button.add_behavior( {
        'type': 'click_up',
        'dialog_id': dialog_id,
        'cbjs_action': '''
        var pos = bvr.src_el.getPosition();
        var el = $(bvr.dialog_id);
        el.setStyle("left", pos.x+1);
        el.setStyle("top", pos.y+32);
        el.setStyle("display", "");
        '''
        } )

        # defined the dialog
        top.add(dialog)
        dialog.add_title("Search Limit")

        table = Table()
        table.add_color("color", "color2")
        dialog.add(table)
        table.add_row()
        td = table.add_cell()
        td.add("Search Limit: ")

        td = table.add_cell()
        select = SelectWdg("search_limit")
        select.set_option("values", "5|10|20|50|100|200|Custom")
        td.add(select)

        save_button = ProdIconButtonWdg("Save")
        td.add(save_button)
        cancel_script = dialog.get_cancel_script();
        save_button.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        var dialog_top = bvr.src_el.getParent(".spt_dialog_top");
        var values = spt.api.get_input_values(dialog_top);

        var top = spt.get_parent(bvr.src_el, ".spt_top");
        var input = top.getElement(".spt_search_limit");
        input.value = values.search_limit;
        %s
        ''' % cancel_script
        } )


        text = TextWdg("search_limit")
        text.add_class("spt_search_limit")
        top.add(text)

        return top


class DialogWdg(BaseRefreshWdg):

    def init(my):
        my.name = my.kwargs.get('id')
        if not my.name:
            num = random.randint(0, 10000)
            my.name = 'dialog%s' % num

        my.allow_page_activity = False
        if my.kwargs.get('allow_page_activity'):
            my.allow_page_activity = True

        my.content_wdg = DivWdg()
        my.content_wdg.set_attr("spt_dialog_id", my.name)
        my.title_wdg = Widget()

        my.offset = {'x':0, 'y':0}

        my.widget = DivWdg()

    def get_id(my):
        return my.name


    def get_cancel_script(my):

        #TODO: when the add_named_listener is fixed, will add these closing function into the listener
        cbjs_action = '''
            var popup=spt.popup.get_popup( bvr.src_el );
            spt.named_events.fire_event('preclose_' + popup.id, {});
        '''

        cbjs_action = '%s; spt.popup.close( spt.popup.get_popup( popup ) );'% cbjs_action
        
        return cbjs_action

    def get_show_script(my):
        cbjs_action = 'spt.popup.open( spt.popup.get_popup( bvr.src_el ) );'
        return cbjs_action


    def add_title(my, widget):
        my.title_wdg.add(widget)

    def add(my, widget, name=None):
        if name == 'content':
            my.content_wdg = widget
        elif name == 'title':
            my.title_wdg = widget
        else:
            my.content_wdg.add(widget, name)

    def set_as_activator(my, widget, offset=None):

        if isinstance(widget, BaseRefreshWdg):
            try:
                widget.add_behavior
            except:
                widget = widget.get_top_wdg()

        if offset:
            my.offset = offset

        dialog_id = my.get_id()
        widget.add_behavior( {
        'type': 'click_up',
        'dialog_id': dialog_id,
        'offset': my.offset,
        'cbjs_action': '''
            var pos = bvr.src_el.getPosition();
            var size = bvr.src_el.getSize();
            var offset = {
                x: pos.x + bvr.offset.x,
                y: pos.y + size.y + bvr.offset.y + 5
            };
            var dialog = $(bvr.dialog_id);
            if (dialog) {
                var body = $(document.body); 
                var scroll_top = body.scrollTop; 
                var scroll_left = body.scrollLeft; 
                offset.y = offset.y - scroll_top; 
                offset.x = offset.x - scroll_left; 

                dialog.position({position: 'upperleft', relativeTo: body, offset: offset});
                spt.toggle_show_hide(dialog);
            }
        '''
        } )


    def get_unique_id(my):
        return my.name


    def add_class(my, class_name):
        my.widget.add_class(class_name)



    def get_display(my):

        # This is the absolute outside of a popup, including the drop shadow
        widget = my.widget

        widget.add_class("spt_dialog_top")
        widget.add_class("spt_popup")

        z_index = my.kwargs.get("z_index")
        if not z_index:
            z_index = "500"
        widget.add_style("z-index: %s" % z_index)


        web = WebContainer.get_web()

        widget.set_id(my.name)
        widget.add_attr("spt_dialog_id", my.name);
        if my.kwargs.get("display") not in [True, "true"]:
            widget.add_style("display: none")

        widget.add_style("position: absolute")
        #widget.add_style("position: fixed")
        widget.add_style("left: 400px")
        widget.add_style("top: 100px")


        widget.add_behavior( {
        'type': 'listen',
        'event_name': '%s|dialog_close' % my.name,
        'cbjs_action': my.get_cancel_script()
        } )


        offset = my.kwargs.get("offset")
        if not offset:
            offset = my.offset


        show_pointer = my.kwargs.get("show_pointer")
        if show_pointer not in [False, 'false']:
            pointer_wdg = DivWdg()
            pointer_wdg.add_class("spt_popup_pointer")
            widget.add(pointer_wdg)
            pointer_wdg.add_style("position: absolute")
            pointer_wdg.add_style("float: left")
            pointer_wdg.add("/\\")
            pointer_wdg.add_style("left: %s" % (15-offset.get('x')))
            #pointer_wdg.add_style("left: 15")
            pointer_wdg.add_style("top: -10")
            pointer_wdg.add_style("height: 11")
            pointer_wdg.add_style("color", "black")
            pointer_wdg.add_color("background", "background")



        table = Table()
        widget.add(table)

        # Top Row of Shadow table ...
        '''
        table.add_row()
        td = table.add_cell()
        td.add_class("css_shadow_td css_shadow_top_left SPT_POPUP_SHADOW")

        td = table.add_cell()
        td.add_class("css_shadow_td css_shadow_top SPT_POPUP_SHADOW")

        td = table.add_cell()
        td.add_class("css_shadow_td css_shadow_top_right SPT_POPUP_SHADOW")
        '''


        # Middle (Content) Row of Shadow table ...
        table.add_row()

        td = table.add_cell()
        td.add_class("css_shadow_td css_shadow_left SPT_POPUP_SHADOW")

        content_td = table.add_cell()
        content_td.add_class("css_shadow_td")

        td = table.add_cell()
        td.add_class("css_shadow_td css_shadow_right SPT_POPUP_SHADOW")


        # Bottom Row of Shadow table ...
        table.add_row()

        td = table.add_cell()
        td.add_class("css_shadow_td css_shadow_bottom_left SPT_POPUP_SHADOW")

        td = table.add_cell()
        td.add_class("css_shadow_td css_shadow_bottom SPT_POPUP_SHADOW")

        td = table.add_cell()
        td.add_class("css_shadow_td css_shadow_bottom_right SPT_POPUP_SHADOW")


        drag_div = DivWdg()
        content_td.add(drag_div)

        # create the 'close' button ...
        close_wdg = SpanWdg()
        close_wdg.add( IconWdg("Close", IconWdg.POPUP_WIN_CLOSE) )
        close_wdg.add_style("float: right")
        close_wdg.add_class("hand")
        close_wdg.add_style("margin: 3px 1px 3px 1px")

        close_wdg.add_behavior({
            'type': 'click_up',
            'cbjs_action': my.get_cancel_script()
        })

        drag_div.add(close_wdg)


        anchor_wdg = SpanWdg()
        drag_div.add(anchor_wdg)
        anchor_wdg.add_style("margin: 3px 1px 3px 1px")
        anchor_wdg.add( IconWdg("Anchor Dialog", IconWdg.POPUP_ANCHOR) )
        anchor_wdg.add_style("float: right")
        anchor_wdg.add_class("hand")

        anchor_wdg.add_behavior({
            'type': 'click_up',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_dialog_top");
            var position = top.getStyle("position");
            if (position == 'fixed') {
                top.setStyle("position", "absolute");
                bvr.src_el.setStyle("opacity", "1.0");
            }
            else {
                top.setStyle("position", "fixed");
                bvr.src_el.setStyle("opacity", "0.5");
            }
            '''
        })







        width = my.kwargs.get("width")
        if not width:
            width = "100px"
        if width:
            drag_div.add_style("min-width: %s" % width)

        # style
        drag_div.add_looks("popup")

        drag_div.add_style("text-align: left")
        drag_div.add_class("spt_popup_width")

        drag_handle_div = DivWdg(id='%s_title' %my.name)
        drag_div.add( drag_handle_div )
        drag_handle_div.add_looks("popup_dragbar fnt_bold")
        drag_handle_div.add_style("padding: 3px;")
        drag_handle_div.add_gradient("background", "background", +10)
        drag_handle_div.add_color("color", "color")


        # add the drag capability
        drag_handle_div.add_behavior( {
        'type':'smart_drag',
        'drag_el': 'spt.popup.get_popup(@);',
        'options': {'z_sort': 'bring_forward'},
        'ignore_default_motion': 'false',
        'cbjs_setup': '''
            var pointer = bvr.drag_el.getElement(".spt_popup_pointer");
            if (pointer) {
                spt.hide(pointer);
            }
        '''
        } )


        
        title_wdg = my.title_wdg
        if not title_wdg:
            title_wdg = "No Title"
        drag_handle_div.add(title_wdg)
        drag_handle_div.add_class("spt_popup_title")


        # add the content
        content_div = DivWdg()
        drag_div.add(content_div)
        content_div.add_color("color", "color2")
        content_div.add_gradient( "background", "background2" )

        content_div.set_id("%s_content" % my.name)
        content_div.add_class("spt_popup_content")
        content_div.add_class("spt_dialog_content")
        content_div.add_style("overflow: hidden")
        content_div.add_style("display: block")
        #content_div.add_style("padding: 5px")
        if not my.content_wdg:
            my.content_wdg = "No Content"

        content_div.add(my.content_wdg)


        # add the resize icon
        icon = IconWdg( "Resize", IconWdg.RESIZE_CORNER )
        icon.add_style("cursor: nw-resize")
        icon.add_style("z-index: 1000")
        icon.add_class("spt_popup_resize")
        icon.add_style("float: right")
        icon.add_style("margin-top: -25px")
        icon.add_style("margin-right: 5px")
        icon.add_behavior( {
        'type': 'drag',
        "drag_el": '@',
        "cb_set_prefix": 'spt.popup.resize_drag'
        } )
        widget.add(icon)



        return widget



