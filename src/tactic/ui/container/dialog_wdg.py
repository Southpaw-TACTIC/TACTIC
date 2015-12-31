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

        # NOTE: not yet implemented. Refer to PopupWdg
        my.allow_page_activity = False
        if my.kwargs.get('allow_page_activity'):
            my.allow_page_activity = True

        my.content_wdg = DivWdg()
        # spt_dialog_id is already set at the spt_dialog_top level
        #my.content_wdg.set_attr("spt_dialog_id", my.name)
        my.title_wdg = Widget()

        my.offset = {'x':0, 'y':0}

        my.widget = DivWdg()

        title = my.kwargs.get("title")
        if title:
            my.title_wdg.add(title)




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

        # add class to state it's an activator
        widget.add_class('spt_activator')
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
            var init_offset = {x: bvr.offset.x, y: bvr.offset.y + 5};
            var offset = {
                x: pos.x + bvr.offset.x,
                y: pos.y + size.y + bvr.offset.y + 10
            };
            
            var dialog = $(bvr.dialog_id);
            if (dialog) {
                var target = evt.target;
                var in_dialog = target.getParent('.spt_dialog_top');
                
                var body = $(document.body); 
                var scroll_top = body.scrollTop; 
                var scroll_left = body.scrollLeft; 
                offset.y = offset.y - scroll_top; 
                offset.x = offset.x - scroll_left; 
                dialog.position({position: 'upperleft', relativeTo: body, offset: offset});
                // avoid toggle when the dialog is a child of the activator
                if (!in_dialog)
                    spt.toggle_show_hide(dialog);

                // reposition if offscreen for offset x only
                var size = dialog.getSize();
                var pos = dialog.getPosition();
                var win_size = $(document.body).getSize();
              
                var dx = pos.x + size.x - (win_size.x + scroll_left);
                if (dx > 0) {
                    offset.x -= dx
                    dialog.position({position: 'upperleft', relativeTo: body, offset: offset});
                    //dialog.setStyle("left", win_size.x - size.x +scroll_left- 5);
                }

                // adjust the pointer
                /*
                var pointer = dialog.getElement(".spt_popup_pointer");
                if (pointer) {
                    pointer_pos = pointer.getPosition();
                    pointer.position({position: 'upperleft', relativeTo: bvr.src_el, offset: init_offset } );
                }
                */
            }
            bvr.src_el.dialog = dialog;
            spt.body.add_focus_element(dialog);
        '''
        } )


    def get_unique_id(my):
        return my.name


    def add_class(my, class_name):
        my.widget.add_class(class_name)


    def add_attr(my, name, value):
        my.widget.add_attr(name, value)


    def get_display(my):

        widget = my.widget
        widget.set_box_shadow()

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

        widget.add_behavior( {
        'type': 'listen',
        'event_name': '%s|dialog_close' % my.name,
        'cbjs_action': my.get_cancel_script()
        } )


        offset = my.kwargs.get("offset")
        if not offset:
            offset = my.offset





        show_header = True
        show_resize = False


        drag_div = DivWdg()
        if show_header:
            widget.add(drag_div)



        show_pointer = my.kwargs.get("show_pointer")
        if show_pointer not in [False, 'false']:
            from tactic.ui.container import ArrowWdg
            offset_x = 15 - offset.get('x')
            offset_y = offset.get("y")
            arrow = ArrowWdg(
                    offset_x=offset_x,
                    offset_y=offset_y,
                    color=widget.get_color("background", -10)
            )
            arrow.add_class("spt_popup_pointer")
            arrow.add_style("z-index: 10")
            widget.add(arrow)


        # create the 'close' button ...
        close_wdg = SpanWdg()
        close_wdg.add( IconWdg("Close", "BS_REMOVE") )
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
        anchor_wdg.add_style("margin: 5px 5px 3px 1px")
        anchor_wdg.add( IconWdg("Anchor Dialog", "BS_PUSHPIN") )
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
        #drag_div.add_looks("popup")

        drag_div.add_style("text-align: left")
        drag_div.add_class("spt_popup_width")
        drag_div.add_style("border-style: solid")
        drag_div.add_color("border-color", "border")
        drag_div.add_style("border-size: 0 0 1 0")


        drag_handle_div = DivWdg(id='%s_title' %my.name)
        drag_div.add( drag_handle_div )
        drag_handle_div.add_style("padding: 3px;")
        #drag_handle_div.add_gradient("background", "background", +10)
        drag_handle_div.add_color("background", "background", -10)
        drag_handle_div.add_color("color", "color")
        drag_handle_div.add_style("padding: 8px 5px 8px 8px")

        drag_handle_div.add_behavior({
            'type': 'double_click',
            'cbjs_action': my.get_cancel_script()
        })


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


        # add the content
        content_div = DivWdg()
        
        title_wdg = my.title_wdg
        if not title_wdg:
            title_wdg = "No Title"
            # if the title is empty, just don't show
        if my.kwargs.get("show_title") in [False, 'false']:
            drag_div.add_style("display: none")


        drag_handle_div.add(title_wdg)
        drag_handle_div.add_class("spt_popup_title")
        drag_handle_div.add_style("font-weight: bold")


        widget.add(content_div)
        content_div.add_color("color", "color")
        content_div.add_color( "background", "background" )

        content_div.set_id("%s_content" % my.name)
        content_div.add_class("spt_popup_content")
        content_div.add_class("spt_dialog_content")
        content_div.add_style("overflow: hidden")
        content_div.add_style("display: block")
        #content_div.add_style("padding: 5px")

        view = my.kwargs.get("view")
        view_kwargs = my.kwargs.get("view_kwargs")
        if not view_kwargs:
            view_kwargs = {}
        if view:
            from tactic.ui.panel import CustomLayoutWdg
            my.add( CustomLayoutWdg(view=view,view_kwargs=view_kwargs) )

        if not my.content_wdg:
            my.content_wdg = "No Content"

        content_div.add(my.content_wdg)


        # add the resize icon
        if show_resize:
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



