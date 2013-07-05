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
__all__ = ["LabeledHidableWdg", "RoundedCornerDivWdg", "PopupWdg", "HorizLayoutWdg"]

from pyasm.web import *
from pyasm.widget import IconWdg

from tactic.ui.common import BaseRefreshWdg, CornerGenerator


class LabeledHidableWdg(DivWdg):

    def __init__(my, name="", label="", label_align="", content_align=""):
        super(LabeledHidableWdg,my).__init__(name)
        my.added_content_list = []
        my.label = label
        my.label_align = label_align
        my.content_align = content_align
        my.width_str = None
        my.content_height_str = None


    def add(my, content):
        my.added_content_list.append( content )


    def set_dimensions(my, width_str=None, content_height_str=None):
        my.width_str = width_str
        my.content_height_str = content_height_str


    def set_label(my, label):
        my.label = label
        
    """ 
    #TODO: make use of this old vertical slide animation by dynamically adding a js file 
    def get_onload_js(my):
        return '''spt.onload.load_jsfile("/context/spt_js/fx_anim.js", "js")'''
    """

    def get_display(my):
        
        if my.width_str:
            my.add_style("width",my.width_str)

        label_div = HtmlElement.div()
        #label_div.add_behavior({'type': 'load',
        #    'cbjs_action': my.get_onload_js()})

        if my.label_align:
            label_div.add_style("text-align: " + my.label_align)

        label_span = HtmlElement.span()
        label_span.add_color("color", "color")
        label_span.add_class("SPT_BVR spt_labeledhidable_label")
        label_span.add(my.label)

        hidable_div = HtmlElement.div()
        # hidable_div.set_attr("id", hidable_id)
        hidable_id = hidable_div.set_unique_id(prefix="spt_hidable")
        if my.content_height_str:
            hidable_div.add_style("height",my.content_height_str)

        if my.added_content_list:
            for i in range(len(my.added_content_list)):
                hidable_div.add( my.added_content_list[i] )
        else:
            hidable_div.add("&nbsp;")

        """
        #NOT USED right now
        label_span.add_behavior( {'type': 'click_up', 'cbfn_action': 'spt.fx.slide_anim_cbk',
                                  'dst_el': hidable_id, 'options': {'direction': 'vert'}} )

        label_span.add_behavior( {'type':'hover', 'hover_class': 'spt_labeledhidable_label_hover'} )
        """
        label_div.add( label_span )

        my.add_widget( label_div )
        my.add_widget( hidable_div )

        return super(LabeledHidableWdg,my).get_display()



class RoundedCornerDivWdg(DivWdg):

    def __init__(my, name="", hex_color_code="2F2F2F", corner_size=""):
        super(RoundedCornerDivWdg,my).__init__(name)

        my.added_content_list = []

        my.hex_color_code = hex_color_code
        if my.hex_color_code.startswith("#"):
            my.hex_color_code = my.hex_color_code.replace("#", "")

        my.corner_size = corner_size
        my.width_str = None
        my.height_str = None
        my.content_height_str = None

        my.content_div = DivWdg()
        #my.content_div.add_style("display: block")
        #my.content_div.add_sytle("float: left")  # float left to ensure shrink wrapping

        if not my.corner_size:
            my.corner_size = "5px"


    def get_content_wdg(my):
        return my.content_div


    def set_dimensions(my, width_str=None, content_height_str=None, height_str=None):
        my.width_str = width_str
        my.height_str = height_str
        my.content_height_str = content_height_str


    def add(my, content):
        my.added_content_list.append( content )


    def get_display(my):
        if my.added_content_list:
            for i in range(len(my.added_content_list)):
                my.content_div.add( my.added_content_list[i] )

        #if my.width_str:
        #    my.content_div.add_style('width: %s' % my.width_str)
        #if my.height_str:
        #    my.content_div.add_style('height: %s' % my.height_str)
        #if my.content_height_str:
        #    my.content_div.add_style('height: %s' % my.content_height_str)

        my.add_widget(my.content_div)
        #my.add_color("background", "background")
        my.add_style( 'background-color: #%s' % my.hex_color_code )
        my.set_round_corners(5)
        my.add_style("padding: 5px")
        return super(RoundedCornerDivWdg, my).get_display()



    def get_display2(my):

        if not CornerGenerator.color_exists(my.hex_color_code):
            CornerGenerator.generate(my.hex_color_code)

        # set up the table
        table = Table(css="spt_rounded_div")
        table.add_style("border: none")
        if my.width_str:
            table.add_style('width: %s' % my.width_str)
        if my.height_str:
            table.add_style('height: %s' % my.height_str)

        img_suffix = ''

        top_row = table.add_row()
        td1 = table.add_cell(css="spt_rounded_div")
        td1.add_style( 'width: %s' % my.corner_size )
        td1.add_style( 'min-width: %s' % my.corner_size )
        td1.add_style( 'height: %s' % my.corner_size )
        td1.add_style( 'background-image: url("/context/ui_proto/roundcorners/rc_%s/rc_%s_%sx%s_TL%s.png")' %
                        (my.hex_color_code,my.hex_color_code,my.corner_size,my.corner_size,img_suffix) )

        td2 = table.add_cell(css="spt_rounded_div")
        td2.add_style( 'height: %s' % my.corner_size )
        td2.add_style( 'font-size: 1px' )
        td2.add_style( 'background-color: #%s' % my.hex_color_code )

        td3 = table.add_cell(css="spt_rounded_div")
        td3.add_style( 'width: %s' % my.corner_size )
        td3.add_style( 'min-width: %s' % my.corner_size )
        td3.add_style( 'height: %s' % my.corner_size )
        td3.add_style( 'background-image: url("/context/ui_proto/roundcorners/rc_%s/rc_%s_%sx%s_TR%s.png")' %
                        (my.hex_color_code,my.hex_color_code,my.corner_size,my.corner_size,img_suffix) )

        content_row = table.add_row()
        td1 = table.add_cell(css="spt_rounded_div")
        td1.add_style( 'background-color: #%s' % my.hex_color_code )

        td2 = table.add_cell(css="spt_rounded_div")
        td2.add_style( 'background-color: #%s' % my.hex_color_code )

        # -- DO NOT SET THE HEIGHT OR WIDTH OF THE contents cell ... this needs to resize with the size
        # -- of its contents ... commenting out the next two lines.
        #
        # td2.add_style( 'height: %s' % my.corner_size )
        # td2.add_style( 'max-height: %s' % my.corner_size )

        td3 = table.add_cell(css="spt_rounded_div")
        td3.add_style( 'background-color: #%s' % my.hex_color_code )
        if my.content_height_str:
            td2.add_style( 'height: %s' % my.content_height_str )

        td2.add(my.content_div)
        td2.add_style( 'vertical-align: top')
        if my.added_content_list:
            for i in range(len(my.added_content_list)):
                my.content_div.add( my.added_content_list[i] )
        #else:
        #    my.content_div.add("&nbsp;")

        bottom_row = table.add_row()
        td1 = table.add_cell(css="spt_rounded_div")
        td1.add_style( 'width: %s' % my.corner_size )
        td1.add_style( 'height: %s' % my.corner_size )
        td1.add_style( 'background-image: url("/context/ui_proto/roundcorners/rc_%s/rc_%s_%sx%s_BL%s.png")' %
                        (my.hex_color_code,my.hex_color_code,my.corner_size,my.corner_size,img_suffix) )

        td2 = table.add_cell(css="spt_rounded_div")
        td2.add_style( 'background-color: #%s' % my.hex_color_code )

        td3 = table.add_cell(css="spt_rounded_div")
        td3.add_style( 'width: %s' % my.corner_size )
        td3.add_style( 'height: %s' % my.corner_size )
        td3.add_style( 'background-image: url("/context/ui_proto/roundcorners/rc_%s/rc_%s_%sx%s_BR%s.png")' %
                        (my.hex_color_code,my.hex_color_code,my.corner_size,my.corner_size,img_suffix) )

        my.add_widget(table)

        return super(RoundedCornerDivWdg, my).get_display()



class PopupWdg(BaseRefreshWdg):
    '''Container widget which creates a popup on the screen.  This popup
    window current has a title widget and a content widget

    @usage
    popup = PopupWdg(id='name')
    popup.add("My Title", "title")
    popup.add("This is Content", "content")
    '''
    RIGHT = 'right'
    BOTTOM = 'bottom'

    def get_args_keys(my):
        return {
            'id': 'The id of the top widget',
            'width': 'The width of the popup',
            'opacity': 'Float value (0.0 to 1.0) to set opacity to, for page blocking background',
            'allow_page_activity': 'Flag to specify whether or not to use a background to block and disable page ' \
                                   ' while popup is open. This flag is False by default.',
            'z_start': 'Integer value equal to one of: 100, 200, 300, 400, 500, etc. ... this now defaults to 200 ' \
                       'which is what most popup windows should be set to.',
            'destroy_on_close': 'Boolean value, if True then the close button destroys the popup instead of just ' \
                                'hiding it.',
            'aux_position': 'position of the auxilliary panel',
            'display': 'true|false - determines whether to display the popup initially',
            'allow_close': 'true|false - determines whether this popup can be explicitly closed by the user'
        }


    def init(my):
        my.name = my.kwargs.get('id')
        if not my.name:
            my.name = 'popup'

        my.allow_page_activity = False
        if my.kwargs.get('allow_page_activity'):
            my.allow_page_activity = True

        my.z_start = 200
        if my.kwargs.get('z_start'):
            my.z_start = my.kwargs.get('z_start')


        # FIXME: make 'destroy_on_close' the default behavior for popups ... do this when there is a chance to go
        #        through and convert all uses of PopupWdg, making sure that ones that need to not be destroyed
        #        can changed appropriately. Currently default is for the popup to be hidden only on 'close'.
        #
        #        NOTE: destroy_on_close will lose the popup window's last position ... do we really want to
        #              make it the default?
        #
        my.destroy_on_close = False

        if my.kwargs.get('destroy_on_close'):
            my.destroy_on_close = True

        my.allow_close = True
        if my.kwargs.get('allow_close') == 'false':
            my.allow_close = False


        my.aux_position = my.kwargs.get('aux_position')
        if my.aux_position:
            assert my.aux_position in [my.RIGHT, my.BOTTOM]
        
        my.content_wdg = Widget()
        my.title_wdg = Widget()
        my.aux_wdg = Widget()

    def get_cancel_script(my):

        #TODO: when the add_named_listener is fixed, will add these closing function into the listener
        cbjs_action = '''
            var popup=spt.popup.get_popup( bvr.src_el );
            spt.named_events.fire_event('preclose_' + popup.id, {});
        '''

        if my.destroy_on_close:
            cbjs_action = '%s; spt.popup.destroy( popup );'% cbjs_action
        else:
            cbjs_action = '%s; spt.popup.close( spt.popup.get_popup( popup ) );'% cbjs_action
        
        return cbjs_action

    def get_show_script(my):
        cbjs_action = 'spt.popup.open( spt.popup.get_popup( bvr.src_el ) );'
        return cbjs_action

    def get_show_aux_script(my):
        cbjs_action = "spt.show('%s')" % my.get_aux_id()
        return cbjs_action

    def get_cancel_aux_script(my):
        cbjs_action = "spt.hide('%s')" % my.get_aux_id()
        return cbjs_action

    def get_aux_id(my):
        return '%s_Aux' % my.name

    def add_title(my, widget):
        my.title_wdg.add(widget)

    def add_aux(my, widget):
        my.aux_wdg.add(widget)

    def add(my, widget, name=None):
        if name == 'content':
            my.content_wdg = widget
        elif name == 'title':
            my.title_wdg = widget
        else:
            my.content_wdg.add(widget, name)
        

    def get_display(my):

        # This is the absolute outside of a popup, including the drop shadow
        widget = DivWdg()
        widget.add_class("spt_popup")


        width = my.kwargs.get("width")
        if not width:
            width = 10

        #widget.add_behavior( {
        #    'type': 'load',
        #    'cbjs_action': 'bvr.src_el.makeResizable({handle:bvr.src_el.getElement(".spt_popup_resize")})'
        #} )


        web = WebContainer.get_web()


        widget.set_id(my.name)
        if my.kwargs.get("display") == "true":
            pass
        else:
            widget.add_style("display: none")

        widget.add_style("position: absolute")
        widget.add_style("left: 400px")
        widget.add_style("top: 100px")

        table = Table()
        table.add_behavior( {
        'type': 'load',
        'width': width,
        'cbjs_action': '''
        bvr.src_el.setStyle("width", bvr.width)

        var popup = bvr.src_el.getParent(".spt_popup");
        var window_size = $(window).getSize();
        var size = bvr.src_el.getSize();
        var left = window_size.x/2 - size.x/2;
        var top = window_size.y/2 - size.y/2;
        popup.setStyle("left", left);
        //popup.setStyle("top", top);

        '''
        } )


        table.add_class("css_shadow_table")
        if web.get_browser() != 'Qt':
            widget.set_box_shadow("2px 2px 5px 5px", "#888")


        # Top Row of Shadow table ...
        table.add_row()

        if web.get_browser() == 'Qt':
            td = table.add_cell()
            td.add_class("css_shadow_td css_shadow_top_left SPT_POPUP_SHADOW")

            td = table.add_cell()
            td.add_class("css_shadow_td css_shadow_top SPT_POPUP_SHADOW")

            td = table.add_cell()
            td.add_class("css_shadow_td css_shadow_top_right SPT_POPUP_SHADOW")


            # Middle (Content) Row of Shadow table ...
            table.add_row()

            td = table.add_cell()
            td.add_class("css_shadow_td css_shadow_left SPT_POPUP_SHADOW")

        content_td = table.add_cell()
        content_td.add_class("css_shadow_td")

        if web.get_browser() == 'Qt':
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

        # FIXME: for some reason, this causes popups to stop functioning after
        # close a couple of times
        my.add_header_context_menu(drag_div)


        # create the 'close' button ...
        if my.allow_close:
            close_wdg = SpanWdg()
            close_wdg.add( IconWdg("Close", IconWdg.POPUP_WIN_CLOSE) )
            close_wdg.add_style("margin: 3px 1px 3px 1px")
            close_wdg.add_style("margin: 3px")
            close_wdg.add_style("float: right")
            close_wdg.add_class("hand")

            close_wdg.add_behavior({
                'type': 'click_up',
                'cbjs_action': my.get_cancel_script()
            })

            drag_div.add(close_wdg)


            # create the 'minimize' button ...
            minimize_wdg = SpanWdg()
            minimize_wdg.add_style("margin: 3px 1px 3px 1px")
            minimize_wdg.add( IconWdg("Minimize", IconWdg.POPUP_WIN_MINIMIZE) )
            minimize_wdg.add_style("float: right")
            minimize_wdg.add_class("hand")
            behavior = {
                'type': 'click_up',
                'cbjs_action': "spt.popup.toggle_minimize( bvr.src_el );"
            }
            minimize_wdg.add_behavior( behavior );
            drag_div.add(minimize_wdg)

        #-- TO ADD SOON -- create the 'refresh' button ...
        #   refresh_wdg = SpanWdg()
        #   refresh_wdg.add( IconWdg("Refresh Popup", IconWdg.POPUP_WIN_REFRESH) )
        #   refresh_wdg.add_style("float: right")
        #   refresh_wdg.add_class("hand")
        #   behavior = {
        #       'type': 'click_up',
        #       'cbjs_action': "spt.popup.toggle_minimize( bvr.src_el );"
        #   }
        #   refresh_wdg.add_behavior( behavior );
        #   drag_div.add(refresh_wdg)

        width = my.kwargs.get("width")
        #if not width:
        #    width = "600px"
        #if width:
        #    drag_div.add_style("width: %s" % width)
        #    content_td.add_style("width: 100%")

        # style
        drag_div.add_looks("popup fnt_text")

        drag_div.add_style("text-align: left")
        drag_div.add_class("spt_popup_width")

        drag_handle_div = DivWdg(id='%s_title' %my.name)
        drag_handle_div.add_looks("popup_dragbar fnt_text fnt_bold")
        drag_handle_div.add_style("padding: 3px;")
        drag_handle_div.add_gradient("background", "background", +10)
        drag_handle_div.add_color("color", "color")


        # add the drag capability
        drag_handle_div.add_behavior( {
            'type':'drag',
            'drag_el': 'spt.popup.get_popup(@);',
            'options': {'z_sort': 'bring_forward'}
        } )


        
        title_wdg = my.title_wdg
        if not title_wdg:
            title_wdg = DivWdg("No Title")
        else:
            title_wdg = DivWdg(title_wdg)

        drag_handle_div.add_behavior({
            'type': 'double_click',
            'cbjs_action': my.get_cancel_script()
        })


        drag_handle_div.add(title_wdg)
        drag_handle_div.add_class("spt_popup_title")


        # add a context menu
        from tactic.ui.container.smart_menu_wdg import SmartMenu
        SmartMenu.assign_as_local_activator( drag_handle_div, 'HEADER_CTX' )
        drag_handle_div.add_attr("spt_element_name", "Test Dock")



        # add the content
        content_div = DivWdg()
        content_div.add_color("color", "color2")
        #content_div.add_color("background", "background2")
        from pyasm.web.palette import Palette
        palette = Palette.get()
        color1 = palette.color("background2")

        if web.is_IE():
            content_div.add_style( "background: %s" % color1 )
        else:
            content_div.add_gradient("background", "background2")




        content_div.set_id("%s_content" % my.name)
        content_div.add_class("spt_popup_content")
        content_div.add_style("overflow: hidden")
        content_div.add_style("display: block")
        #content_div.add_style("padding: 10px")
        if not my.content_wdg:
            my.content_wdg = "No Content"

        content_div.add(my.content_wdg)

        drag_div.add( drag_handle_div )
        my.position_aux_div(drag_div, content_div)
        content_td.add(drag_div)
        widget.add(table)

        # ALWAYS make the Popup a Page Utility Widget (now processed client side)
        widget.add_class( "SPT_PUW" )

        if my.z_start:
            widget.set_z_start( my.z_start )
            widget.add_style("z-index: %s" % my.z_start)
        else:
            widget.add_style("z-index: 102")


        # add the resize icon
        icon = IconWdg( "Resize", IconWdg.RESIZE_CORNER )
        icon.add_style("cursor: nw-resize")
        icon.add_style("z-index: 1000")
        icon.add_class("spt_popup_resize")
        icon.add_style("float: right")
        icon.add_style("margin-top: -15px")
        icon.add_behavior( {
        'type': 'drag',
        "drag_el": '@',
        "cb_set_prefix": 'spt.popup.resize_drag'
        } )
        content_td.add(icon)

        return widget



    def add_header_context_menu(my, widget):
        from tactic.ui.widget import Menu, MenuItem
        menu = Menu(width=180)
        menu.set_allow_icons(False)
        menu.set_setup_cbfn( 'spt.dg_table.smenu_ctx.setup_cbk' )


        menu_item = MenuItem(type='title', label='Actions')
        menu.add(menu_item)

        menu_item = MenuItem(type='action', label='Reload')
        menu.add(menu_item)
        menu_item.add_behavior( {
            'cbjs_action': '''
            var header = spt.smenu.get_activator(bvr);
            var top = header.getParent(".spt_popup");
            var content_top = top.getElement(".spt_popup_content");
            var content = content_top.getElement(".spt_panel");
            spt.panel.refresh(content);
            '''
        } )


        menu_item = MenuItem(type='separator')
        menu.add(menu_item)

        menu_item = MenuItem(type='action', label='Dock Window')
        menu_item.add_behavior( {
            'cbjs_action': '''
            var header = spt.smenu.get_activator(bvr);
            var top = header.getParent(".spt_popup");
            var content = top.getElement(".spt_popup_content");
            var title = top.getElement(".spt_popup_title")
            var title = title.innerHTML;
            //var element_name = header.getAttribute("spt_element_name");

            spt.tab.set_main_body_tab();

            var html = content.innerHTML;

            spt.tab.add_new(title, title);
            spt.tab.load_html(title, html);

            spt.popup.close(top);
            '''
        } )
        menu.add(menu_item)


        menu_item = MenuItem(type='action', label='Open in Browser')
        menu.add(menu_item)
        menu_item.add_behavior( {
            'cbjs_action': '''
            var header = spt.smenu.get_activator(bvr);
            var top = header.getParent(".spt_popup");
            var content = top.getElement(".spt_popup_content");

            var html = content.innerHTML;
            var url = spt.Environment.get().get_server_url();
            var project = spt.Environment.get().get_project();
            var url = url + "/tactic/"+project+"/#//widget/tactic.ui.container.EmptyWdg";

            spt.app_busy.show("Copying to new browser window");
            var win = window.open(url);
            setTimeout( function() {
                var empty_el = $(win.document).getElement(".spt_empty_top");
                spt.behavior.replace_inner_html(empty_el, html);
                spt.app_busy.hide();
            }, 2000 );

            //spt.popup.close(top);
            '''
        } )







        menus = [menu.get_data()]
        menus_in = {
            'HEADER_CTX': menus,
        }
        from tactic.ui.container.smart_menu_wdg import SmartMenu
        SmartMenu.attach_smart_context_menu( widget, menus_in, False )




    def position_aux_div(my, drag_div, content_div):
        # add the aux div
        # add optional aux div
        if not my.aux_position:
            drag_div.add(content_div)
            return
        content_table = Table()
        content_table.add_row()

        aux_div = DivWdg(id=my.get_aux_id())
        aux_div.add_style("display: none")

        aux_div_content = DivWdg(id='%s_Content' %my.get_aux_id())
        aux_div_content.add(my.aux_wdg)
        aux_div.add( aux_div_content )

        if my.aux_position == my.RIGHT:
            content_table.add_cell(content_div)
            content_table.add_cell(aux_div)
            drag_div.add(content_table)
        elif my.aux_position == my.BOTTOM:
            drag_div.add(content_div)
            drag_div.add(aux_div)
        else:
            drag_div.add(content_div)
            drag_div.add(aux_div)

            

__all__.append('EmptyWdg')
class EmptyWdg(BaseRefreshWdg):

    def get_display(my):
        top = my.top;
        top.add_class("spt_empty_top");
        return top






class HorizLayoutWdg(BaseRefreshWdg):

    def get_args_keys(my):
        return {
        'widget_map_list': 'List of widget defining dictionaries, in this format ... {"wdg": wdg, "style": style_str}',
        'spacing': 'The width in between widgets',
        'float': 'Float positioning ... float "left", float "right" or not defined'
        }


    def get_display(my):
        my.widget_map_list = my.kwargs.get("widget_map_list")
        my.spacing = my.kwargs.get("spacing")
        my.float = my.kwargs.get("float")

        div = DivWdg()
        if my.float:
            div.add_styles("float: %s;" % my.float)

        table = Table()
        table.add_row()

        count = 0
        for wdg_map in my.widget_map_list:
            td = table.add_cell()
            if my.spacing and count:
                td.add_styles( "padding-left: %spx;" % my.spacing )
            count += 1
            td.add( wdg_map.get('wdg') )
            if wdg_map.get('style'):
                td.add_styles( wdg_map.get('style') )

        div.add( table )
        return div



