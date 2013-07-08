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
__all__ = ["PopWindowWdg","ResizeScrollWdg"]

from pyasm.web import DivWdg, HtmlElement, WebContainer
from pyasm.widget import IconWdg

from tactic.ui.common import BaseRefreshWdg


class PopWindowWdg(BaseRefreshWdg):

    def get_args_keys(my):
        return {
                'top_id': 'Element ID for top popup window element',
                'title': 'Text for Title Bar banner',
                'width': 'Width of content area',
                'height': 'Height of content area'
        }


    def init(my):

        raise Exception("DEPRECATED")

        my.z_start = 200
        my.top_id = my.kwargs.get('top_id')
        my.title = my.kwargs.get('title')
        if not my.title:
            my.title = "-- No Title --"

        # defaults for content size ...
        my.content_width = 400
        my.content_height = 200

        width = my.kwargs.get('width')
        height = my.kwargs.get('height')
        if width:
            if type(width) == str:
                my.content_width = int( width.replace('px','') )
            else:
                my.content_width = width
        if height:
            if type(height) == str:
                my.content_height = int( height.replace('px','') )
            else:
                my.content_height = height

        my.added_widgets = []


    def set_style(my, new_style_str):
        return ("overflow: hidden; border-width: 0px; padding: 0px; margin: 0px; %s" % new_style_str)


    def add(my, wdg):
        my.added_widgets.append( wdg )


    def get_display(my):

        is_IE = WebContainer.get_web().is_IE()

        cw = my.content_width
        ch = my.content_height

        title_h = 20 # title bar height

        shd_w = 8  # drop shadow width
        shd_h = 8  # drop shadow height

        full_w = cw + (2 * shd_w)
        full_h = ch + title_h + (2 * shd_h)

        border_sz = 1 # border size for inside content area


        # top DIV element for this widget ...
        popwin_div = DivWdg()
        if my.top_id:
            popwin_div.set_id( my.top_id )
        popwin_div.add_class("SPT_PWIN_TOP_DIV SPT_RSW_OUTER_TOP SPT_PUW spt_popup spt_pwin_DX spt_pwin_DY")
        popwin_div.set_z_start( my.z_start )
        popwin_div.add_styles( my.set_style( "display: none; position: absolute; top: 200px; left: 300px; " \
                                             "width: %spx; height: %spx;" % (full_w, full_h)) )

        left_div = DivWdg()
        left_div.add_class("spt_pwin_A spt_pwin_DY")
        left_div.add_styles( my.set_style("float: left; width: %spx; height: %spx;" % (shd_w, full_h)) )

        center_div = DivWdg()
        center_div.add_class("spt_pwin_B spt_pwin_DX spt_pwin_DY")
        center_div.add_styles( my.set_style("float: left; width: %spx; height: %spx;" % (cw, full_h)) )

        right_div = DivWdg()
        right_div.add_class("spt_pwin_C spt_pwin_DY")
        right_div.add_styles( my.set_style("float: left; width: %spx; height: %spx;" % (shd_w, full_h)) )

        popwin_div.add( left_div )
        popwin_div.add( center_div )
        popwin_div.add( right_div )

        # Do LEFT side ...
        #
        lt_div = DivWdg()
        lm_div = DivWdg()
        lb_div = DivWdg()

        lt_div.add_styles( my.set_style("width: %spx; height: %spx;" % (shd_w, shd_h)) )
        lt_div.add_class("css_shadow_top_left spt_pwin_A_1")

        adj_h = ch + title_h
        if not is_IE:
            adj_h = adj_h + (2 * border_sz)
        lm_div.add_styles( my.set_style("width: %spx; height: %spx;" % (shd_w, adj_h)) )
        lm_div.add_class("css_shadow_left spt_pwin_A_2 spt_pwin_DY")

        lb_div.add_styles( my.set_style("width: %spx; height: %spx;" % (shd_w, shd_h)) )
        lb_div.add_class("css_shadow_bottom_left spt_pwin_A_3")

        left_div.add( lt_div )
        left_div.add( lm_div )
        left_div.add( lb_div )

        # Do Center/Middle bit ...
        #
        center_top_div = DivWdg()
        center_resize_scroll_wdg = ResizeScrollWdg( width=cw, height=ch, scroll_bar_size_str='thick',
                                                    scroll_expansion='outside', affects_outside_flag=True,
                                                    exclude_top_border=True )
        for wdg in my.added_widgets:
            center_resize_scroll_wdg.add( wdg )

        center_bottom_div = DivWdg()

        center_top_div.add_styles( my.set_style("width: %spx; height: %spx;" % (cw, shd_h)) )
        center_top_div.add_class("css_shadow_top spt_pwin_B_1 spt_pwin_DX")


        center_title_div = DivWdg()
        center_title_div.add_class("spt_pwin_B_title SPT_PWIN_TITLE_BAR spt_pwin_DX")

        center_title_div.add_behavior( { 'type':'drag', 'drag_el': 'spt.popup.get_popup(@);',
                                         'options': {'z_sort': 'bring_forward'} } )

        border_adj_cw = cw
        if not is_IE:
            border_adj_cw = cw - (2 * border_sz)

        center_title_div.add_styles( my.set_style("cursor: move; border: %spx solid black; " \
                                                  "background-color: #202020; color: white; width: %spx; " \
                                                  "height: %spx;" % \
                                                  (border_sz, border_adj_cw, title_h)) )

        title_div = DivWdg()
        title_div.add_styles( "width: 100%; height: 100%; padding: 4px;" )
        title_div.add( my.title )

        center_title_div.add( title_div )

        center_bottom_div.add_styles( my.set_style("width: %spx; height: %spx;" % (cw, shd_h)) )
        center_bottom_div.add_class("css_shadow_bottom spt_pwin_B_3 spt_pwin_DX")

        center_div.add( center_top_div )
        center_div.add( center_title_div )
        center_div.add( center_resize_scroll_wdg )
        center_div.add( center_bottom_div )


        # Do RIGHT side ...
        #
        rt_div = DivWdg()
        rm_div = DivWdg()
        rb_div = DivWdg()

        rt_div.add_styles( my.set_style("width: %spx; height: %spx;" % (shd_w, shd_h)) )
        rt_div.add_class("css_shadow_top_right spt_pwin_C_1")

        adj_h = ch + title_h
        if not is_IE:
            adj_h = adj_h + (2 * border_sz)
        rm_div.add_styles( my.set_style("width: %spx; height: %spx;" % (shd_w, adj_h)) )
        rm_div.add_class("css_shadow_right spt_pwin_C_2 spt_pwin_DY")

        rb_div.add_styles( my.set_style("width: %spx; height: %spx;" % (shd_w, shd_h)) )
        rb_div.add_class("css_shadow_bottom_right spt_pwin_C_3")

        right_div.add( rt_div )
        right_div.add( rm_div )
        right_div.add( rb_div )


        return popwin_div



class ResizeScrollWdg(BaseRefreshWdg):

    def get_args_keys(my):
        return {
                'width': 'Width of content area',
                'height': 'Height of content area',
                'scroll_bar_size_str': 'String value of either "thin", "medium", "thick", to define which size of' \
                                       ' scroll bar size to generate. Defaults to "medium". ' \
                                       'PopWindowWdg to use "thick".',
                'scroll_expansion': 'String value that is either "inside" or "outside" - for direction from content' \
                                    ' area border to expand in when scroll bars appear. Defaults to "inside".',
                'no_resize': 'set to True if you do not want resize, and just want scroll bars. Defaults to False.',
                'affects_outside_flag': 'set to True if scroll bars and resizing affects immediately surrounding' \
                                        ' elements, like usage in PopWindowWdg. Defaults to False.',
                'exclude_top_border': 'if True then the drawing of a top border is skipped. Defaults to False.',
                'min_content_w': 'Integer number in pixels for minimum content width. Defaults to 150.',
                'min_content_h': 'Integer number in pixels for minimum content height. Defaults to 100.',
                'max_content_w': 'Integer number in pixels for maximum content width. Defaults to 0, meaning' \
                                 ' no maximum content width.',
                'max_content_h': 'Integer number in pixels for maximum content height. Defaults to 0, meaning' \
                                 ' no maximum content height.',
                'set_max_to_content_size': 'Set to True if you want max size to be maximum resize dimensions to' \
                                           ' be same as the content dimensions.'
        }


    def init(my):

        # defaults for content size ...
        my.content_width = 0
        my.content_height = 0

        width = my.kwargs.get('width')
        height = my.kwargs.get('height')
        if width:
            if type(width) == str:
                my.content_width = int( width.replace('px','') )
            else:
                my.content_width = width
        if height:
            if type(height) == str:
                my.content_height = int( height.replace('px','') )
            else:
                my.content_height = height


        my.affects_outside_flag = False
        if my.kwargs.get('affects_outside_flag'):
            my.affects_outside_flag = True

        my.scroll_bar_size_str = "medium"
        if my.kwargs.get('scroll_bar_size_str'):
            my.scroll_bar_size_str = my.kwargs.get('scroll_bar_size_str')

        my.scroll_expansion = "inside"
        if my.kwargs.get('scroll_expansion'):
            my.scroll_expansion = my.kwargs.get('scroll_expansion')

        my.exclude_top_border = my.kwargs.get('exclude_top_border')
        my.no_resize = my.kwargs.get('no_resize')

        my.min_content_w = my.kwargs.get('min_content_w')
        if not my.min_content_w:
            my.min_content_w = 150
        my.min_content_h = my.kwargs.get('min_content_h')
        if not my.min_content_h:
            my.min_content_h = 100

        my.max_content_w = my.kwargs.get('max_content_w')
        if not my.max_content_w:
            my.max_content_w = 0
        my.max_content_h = my.kwargs.get('max_content_h')
        if not my.max_content_h:
            my.max_content_h = 0

        my.set_max_to_content_size = my.kwargs.get('set_max_to_content_size')

        my.added_widgets = []


    def _get_scroll_bar_pixel_size(my):

        size_map = { 'thin': 8, 'medium': 12, 'thick': 16 }
        pixel_sz = size_map.get('medium')
        if size_map.get( my.scroll_bar_size_str ):
            pixel_sz = size_map.get( my.scroll_bar_size_str )
        return pixel_sz


    def set_style(my, new_style_str):
        return ("overflow: hidden; border-width: 0px; padding: 0px; margin: 0px; %s" % new_style_str)


    def add(my, wdg):
        my.added_widgets.append( wdg )


    def get_display(my):

        is_IE = WebContainer.get_web().is_IE()

        cw = my.content_width
        ch = my.content_height

        title_h = 20 # title bar height

        shd_w = 8  # drop shadow width
        shd_h = 8  # drop shadow height

        full_w = cw + (2 * shd_w)
        full_h = ch + title_h + (2 * shd_h)

        resize_sz = 4  # resize control size (width of resize bar)
        if my.no_resize:
            resize_sz = 1
        scroll_sz = my._get_scroll_bar_pixel_size()

        in_cw = cw - resize_sz
        in_ch = ch - resize_sz

        border_sz = 1 # border size for inside content area

        border_adj_cw = cw
        border_adj_ch = ch

        border_adj_in_cw = in_cw
        border_adj_in_ch = in_ch

        if not is_IE:
            border_adj_in_cw = in_cw - border_sz  # only using left border, so only one to subtract
            if not my.exclude_top_border:
                border_adj_in_ch = in_ch - border_sz
                border_adj_ch = ch - border_sz

        top_div = DivWdg()
        top_div.add_styles( my.set_style("width: %spx; height: %spx;" % (cw, ch)) )

        top_div.add_behavior( {
            'type': 'load',
            'cbjs_action': my.get_onload_js()
        } )




        top_div.add_class("spt_pwin_B_2 SPT_RSW_TOP spt_pwin_DX spt_pwin_DY")
        if not my.affects_outside_flag:
            top_div.add_class("SPT_RSW_OUTER_TOP")

        top_div.set_attr("spt_min_content_w","%d" % my.min_content_w)
        top_div.set_attr("spt_min_content_h","%d" % my.min_content_h)

        top_div.set_attr("spt_max_content_w","%d" % my.max_content_w)
        top_div.set_attr("spt_max_content_h","%d" % my.max_content_h)

        top_div.set_attr("spt_set_max_to_content_size","false")
        if my.set_max_to_content_size:
            top_div.set_attr("spt_set_max_to_content_size","true")

        top_div.set_attr("spt_scroll_size", scroll_sz)
        top_div.set_attr("spt_scroll_expansion", my.scroll_expansion)

        top_div.set_attr("spt_content_w", cw)
        top_div.set_attr("spt_content_h", ch)

        B2_i = DivWdg()
        B2_i.add_class("spt_pwin_B_2_i spt_pwin_DX spt_pwin_DY spt_popup_content")
        if not my.exclude_top_border:
            B2_i.add_styles( "border-top: 1px solid black;" )

        B2_ii = DivWdg()
        B2_ii.add_class("spt_pwin_B_2_ii spt_controls_DY spt_pwin_DX")

        B2_i.add_styles( my.set_style("width: %spx; height: %spx;" % (cw, border_adj_in_ch)) )
        B2_ii.add_styles( my.set_style("width: %spx; height: %spx;" % (cw, resize_sz)) )

        top_div.add( B2_i )
        top_div.add( B2_ii )

        # ---------------------------------------------------------------------------------------------------------
        # -- COMMENTED OUT CODE below ... here for reference ... this worked in all browsers except IE (providing a
        # -- visual floating handle at bottom right of ResizeScrollWdg for resizing in both dimensions ...
        # -- disabling this as it totally messes up in IE
        #
        # if not my.no_resize:
        #     resize_bvr = {
        #         "type": 'drag',
        #         "cb_set_prefix": "spt.resize_scroll.drag_resize"
        #     }
        #     resize_img = HtmlElement.img()
        #     resize_img.set_attr("src","/context/icons/common/corner_resize_icon.png")
        #     resize_img.add_class("SPT_PWIN_RESIZE_IMG")
        #     resize_img.add_styles("position: absolute; right: 2px; bottom: 2px; cursor: se-resize;")
        #
        #     resize_img.add_behavior( resize_bvr )
        #     top_div.add( resize_img )  # requires top_div to have "position: relative;"
        # ---------------------------------------------------------------------------------------------------------


        # NOTE: IE includes border in clientHeight/clientWidth of div so don't need to compensate for pixel border
        #       in specifying width and height ... however all other browsers you need to adjust by subtracting
        #       2 from width and 2 from height for a 1 pixel border all arond

        B2_i_a = DivWdg()  # this is the content div
        B2_i_a.add_class("spt_pwin_B_2_i_a SPT_RSW_CONTENT_BOX spt_pwin_DX spt_pwin_DY")
        B2_i_a.add_behavior( {'type': 'wheel', 'cbfn_action': 'spt.resize_scroll.wheel_scroll'} )
        B2_i_a.add_behavior( {'type': 'load', 'cbjs_action': 'spt.resize_scroll.adjust_for_scroll( bvr.src_el );'} )

        content_styles = [
                # commenting out: presumption to want a color here?
                #"background-color: #666666;",
                "border-left: %spx solid black;" % border_sz,
                "border-right: none;",
                "border-bottom: none;",
                "border-top: none;",
                "float: left;",
                "width: %spx;" % border_adj_in_cw,
                "height: %spx;" % border_adj_in_ch
        ]
        B2_i_a.add_styles( my.set_style( ' '.join( content_styles ) ) )


        actual_contents = DivWdg()
        actual_contents.add_class("SPT_RSW_CONTENTS")
        actual_contents.add_styles("float: left;")  # apparently the only way to shrink-wrap across browsers!

        panning_bvr = {'type': 'panning_scroll',
                       'cbjs_motion': 'spt.resize_scroll.adjust_scroll_draggables( bvr.src_el );',
                       'cbjs_action': 'spt.resize_scroll.adjust_scroll_draggables( bvr.src_el );'
                      }
        actual_contents.add_behavior( panning_bvr )

        for wdg in my.added_widgets:
            actual_contents.add( wdg )

        B2_i_a.add( actual_contents )


        B2_i_b = DivWdg()  # this is the RIGHT CONTROLS [vertical scroll bar]
        B2_i_b.add_class("spt_pwin_B_2_i_b SPT_CONTROLS_RIGHT spt_controls_DX spt_pwin_DY")
        B2_i_b.add_styles( my.set_style("background-color: #444; float: left; width: %spx; " \
                                        "height: %spx;" % (resize_sz, border_adj_in_ch)) )

        y_scroll = DivWdg()
        y_scroll.add_class("SPT_SCROLL_Y spt_pwin_DY")
        y_scroll_w = scroll_sz
        if not is_IE:
            y_scroll_w -= 1
        y_scroll.add_styles( my.set_style("background-color: #949494; float: left; width: %spx; " \
                                         
                                          "display: none; " \
                                          "height: %spx;" % (y_scroll_w, border_adj_in_ch)) )
        y_scroll_drag = DivWdg()
        y_scroll_drag.add_class("SPT_SCROLL_Y_DRAG")

        # 336699 = menu highlight blue, 434343 = mid-grey of dark skin/theme
        y_scroll_drag.add_styles(" left: 0px; top: 0px;"\
                    "border-top: 1px outset #ccc; " \
                    "border-left: 1px outset #ccc; " \
                    "border-right: 1px solid #333; " \
                    "border-bottom: 1px solid #333; " \
                    )  # scroll bar color
        y_scroll_drag.add_behavior({'type': 'drag', 'cbfn_motion': 'spt.resize_scroll.drag_y_scroll_draggable_motion'})
        y_scroll_drag.add_color('background', 'background2', -30)

        y_scroll.add( y_scroll_drag )
        B2_i_b.add( y_scroll )


        x_resize = DivWdg()
        x_resize.add_class("SPT_RESIZE_X spt_pwin_DY")
        x_resize.add_styles( my.set_style("float: left; width: %spx; " \
                                          "height: %spx;" % (resize_sz, border_adj_in_ch)) )
        x_resize.add_color('background','background2')
        if not my.no_resize:
            x_resize.add_styles( "cursor: e-resize;" );
            x_resize.add_behavior( {"type": 'drag', "cb_set_prefix": "spt.resize_scroll.drag_x_resize"} )
        B2_i_b.add( x_resize )


        B2_i.add( B2_i_a )
        B2_i.add( B2_i_b )


        B2_ii_a = DivWdg()  # this is the BOTTOM CONTROLS [horizontal scroll bar]
        B2_ii_a.add_class("spt_pwin_B_2_ii_a SPT_CONTROLS_BOTTOM spt_controls_DY spt_pwin_DX")
        B2_ii_a.add_styles( my.set_style("background-color: black; float: left; width: %spx; " \
                                         "height: %spx;" % (in_cw, resize_sz)) )



        x_scroll = DivWdg()
        x_scroll.add_class("SPT_SCROLL_X spt_pwin_DX")
        x_scroll_h = scroll_sz
        x_scroll_w = in_cw
        if not is_IE:
            x_scroll_h -= 1
            x_scroll_w -= 1
        x_scroll.add_styles( my.set_style("background-color: #949494; float: left; width: %spx; " \
                                         
                                          "display: none; " \
                                          "height: %spx;" % (x_scroll_w, x_scroll_h)) )
        x_scroll_drag = DivWdg()
        x_scroll_drag.add_class("SPT_SCROLL_X_DRAG")

        # 336699 = menu highlight blue, 434343 = mid-grey of dark skin/theme
        x_scroll_drag.add_styles("background-color: #434343; left: 0px; top: 0px;"\
                 "border-top: 1px outset #ccc; " \
                 "border-left: 1px outset #ccc; " \
                 "border-right: 1px solid #333; " \
                 "border-bottom: 1px solid #333; " \
                                          )  # scroll bar color
        x_scroll_drag.add_behavior({'type': 'drag', 'cbfn_motion': 'spt.resize_scroll.drag_x_scroll_draggable_motion'})
        x_scroll_drag.add_color('background', 'background2', -30)
        
        x_scroll.add( x_scroll_drag )
        B2_ii_a.add( x_scroll )

        y_resize = DivWdg()
        y_resize.add_class("SPT_RESIZE_Y spt_pwin_DX")
        y_resize.add_styles( my.set_style("float: left; width: %spx; " \
                                          "height: %spx;" % (in_cw, resize_sz)) )
        y_resize.add_color('background','background2')

        if not my.no_resize:
            y_resize.add_styles( "cursor: s-resize;" )
            y_resize.add_behavior( {"type": 'drag', "cb_set_prefix": "spt.resize_scroll.drag_y_resize"} )
        B2_ii_a.add( y_resize )


        B2_ii_b = DivWdg()  # this is the resize handle
        B2_ii_b.add_class("spt_pwin_B_2_ii_b SPT_RESIZE_HANDLE spt_controls_DX spt_controls_DY")
        if my.no_resize:
            B2_ii_b.add_styles( my.set_style("background-color: black; float: left; " \
                                             "overflow: hidden; position: relative; " \
                                             "width: %spx; height: %spx;" % (resize_sz, resize_sz)) )
        else:
        #{
            # RESIZE control in X and Y ...
            resize_bvr = {
                "type": 'drag',
                "cb_set_prefix": "spt.resize_scroll.drag_resize"
            }

            if not is_IE:
                resize_sz -= 2

            B2_ii_b.add_styles( my.set_style("background-color: #434343; float: left; cursor: se-resize; " \
                                             "border-top: 1px solid black; " \
                                             "border-bottom: 1px solid black; " \
                                             "border-left: 1px solid black; " \
                                             "border-right: 1px solid black; " \
                                             "overflow: visible; " \
                                             "position: relative; " \
                                             "width: %spx; height: %spx;" % (resize_sz, resize_sz)) )

            # also make sure that the resize handle div has the resize behavior (along with the resize_img)
            B2_ii_b.add_behavior( resize_bvr );

            resize_img = HtmlElement.img()
            resize_img.set_attr("src","/context/icons/common/corner_resize_icon.png")
            resize_img.add_class("SPT_PWIN_RESIZE_IMG")
            resize_img.add_styles("cursor: se-resize;")
            resize_img.add_styles("position: absolute; top: 0px; left: 0px;")

            B2_ii_b.add( resize_img )
        #}

        B2_ii.add( B2_ii_a )
        B2_ii.add( B2_ii_b )

        return top_div


    def get_onload_js(my):
        return r'''


spt.popwin = {};
spt.resize_scroll = {};


spt.resize_scroll.resize = function( activating_el, dx, dy )
{
    var rsw_top_el = activating_el.getParent(".SPT_RSW_TOP");

    var content_box_el = rsw_top_el.getElement(".SPT_RSW_CONTENT_BOX");
    var content_el = content_box_el.getElement(".SPT_RSW_CONTENTS");

    var cb_w = content_box_el.clientWidth;
    var cb_h = content_box_el.clientHeight;

    var min_content_w = parseInt( rsw_top_el.getProperty("spt_min_content_w") );
    var min_content_h = parseInt( rsw_top_el.getProperty("spt_min_content_h") );

    var max_content_w = parseInt( rsw_top_el.getProperty("spt_max_content_w") );
    var max_content_h = parseInt( rsw_top_el.getProperty("spt_max_content_h") );

    var content_w = rsw_top_el.getProperty("spt_content_w");
    var content_h = rsw_top_el.getProperty("spt_content_h");
    if( content_w ) { content_w = parseInt( content_w ); }
    else { content_w = 0; }
    if( content_h ) { content_h = parseInt( content_h ); }
    else { content_h = 0; }

    display_content_w = spt.get_render_display_width( content_el );
    display_content_h = spt.get_render_display_height( content_el );

    if( ! content_w ) {
        content_w = display_content_w;
    }
    if( ! content_h ) {
        content_h = display_content_h;
    }

    var set_max_to_content_size = rsw_top_el.getProperty("spt_set_max_to_content_size");
    if( spt.is_TRUE( set_max_to_content_size ) ) {
        max_content_w = display_content_w;
        max_content_h = display_content_h;
    }

    var scr_left = content_box_el.scrollLeft;
    var scr_top = content_box_el.scrollTop;

    var top_el = rsw_top_el.getParent(".SPT_PWIN_TOP_DIV");
    if( ! top_el ) {
        top_el = rsw_top_el;
    }

    if( max_content_w && (cb_w + dx > max_content_w) ) {
        dx = max_content_w - cb_w;
    }
    var modify_w = false;
    if( dx && (cb_w+dx) >= min_content_w ) {
        modify_w = true;
        if( max_content_w && (cb_w + dx > max_content_w) ) {
            modify_w = false;
        }
    }
    if( modify_w ) {
        var dx_el_list = top_el.getElements(".spt_pwin_DX");
        if( top_el.hasClass("spt_pwin_DX") ) {
            dx_el_list.push( top_el );
        }
        for( var c=0; c < dx_el_list.length; c++ ) {
            var el = dx_el_list[c];
            var el_w = parseInt( el.getStyle("width") );
            el.setStyle("width", (el_w+dx) + "px");
        }

        if( scr_left && dx > 0 && cb_w + dx + scr_left > max_content_w ) {
            var new_scr_left = scr_left - dx;
            if( new_scr_left < 0 ) {
                new_scr_left = 0;
            }
            content_box_el.scrollLeft = new_scr_left;
        }
    }

    if( max_content_h && (cb_h + dy > max_content_h) ) {
        dy = max_content_h - cb_h;
    }
    var modify_h = false;
    if( dy && (cb_h+dy) >= min_content_h ) {
        modify_h = true;
        if( max_content_h && (cb_h + dy > max_content_h) ) {
            modify_h = false;
        }
    }
    if( modify_h ) {
        var dy_el_list = top_el.getElements(".spt_pwin_DY");
        if( top_el.hasClass("spt_pwin_DY") ) {
            dy_el_list.push( top_el );
        }
        for( var c=0; c < dy_el_list.length; c++ ) {
            var el = dy_el_list[c];
            var el_h = parseInt( el.getStyle("height") );
            el.setStyle("height", (el_h+dy) + "px");
        }

        if( scr_top && dy > 0 && cb_h + dy + scr_top > max_content_h ) {
            var new_scr_top = scr_top - dy;
            if( new_scr_top < 0 ) {
                new_scr_top = 0;
            }
            content_box_el.scrollTop = new_scr_top;
        }
    }

    spt.resize_scroll.adjust_scroll_draggables( activating_el );
}


// spt.resize_scroll.drag_resize_setup = function( evt, bvr, mouse_411 )
// {
// }


spt.resize_scroll.drag_resize_motion = function( evt, bvr, mouse_411 )
{
    var dx = mouse_411.curr_x - mouse_411.last_x;
    var dy = mouse_411.curr_y - mouse_411.last_y;

    spt.resize_scroll.resize( bvr.src_el, dx, dy );
}


spt.resize_scroll.drag_resize_action = function( evt, bvr, mouse_411 )
{
    spt.resize_scroll.adjust_for_scroll( bvr.src_el );
}


// spt.resize_scroll.drag_x_resize_setup = function( evt, bvr, mouse_411 )
// {
// }


spt.resize_scroll.drag_x_resize_motion = function( evt, bvr, mouse_411 )
{
    var dx = mouse_411.curr_x - mouse_411.last_x;
    var dy = 0;

    spt.resize_scroll.resize( bvr.src_el, dx, dy );
}


spt.resize_scroll.drag_x_resize_action = function( evt, bvr, mouse_411 )
{
    spt.resize_scroll.adjust_for_scroll( bvr.src_el );
}



// spt.resize_scroll.drag_y_resize_setup = function( evt, bvr, mouse_411 )
// {
// }


spt.resize_scroll.drag_y_resize_motion = function( evt, bvr, mouse_411 )
{
    var dx = 0;
    var dy = mouse_411.curr_y - mouse_411.last_y;

    spt.resize_scroll.resize( bvr.src_el, dx, dy );
}


spt.resize_scroll.drag_y_resize_action = function( evt, bvr, mouse_411 )
{
    spt.resize_scroll.adjust_for_scroll( bvr.src_el );
}



spt.resize_scroll.drag_x_scroll_draggable_motion = function( evt, bvr, mouse_411 )
{
    var rsw_top_el = bvr.src_el.getParent(".SPT_RSW_TOP");
    var dx = mouse_411.curr_x - mouse_411.last_x;

    var content_box = rsw_top_el.getElement(".SPT_RSW_CONTENT_BOX");
    var contents = content_box.getElement(".SPT_RSW_CONTENTS");
    var scr_x_drag_div = rsw_top_el.getElement(".SPT_SCROLL_X_DRAG");

    var cw = spt.get_render_display_width( contents );
    var cb_w = content_box.clientWidth;
    var sd_w = scr_x_drag_div.clientWidth;
    var sd_off_x = parseInt( scr_x_drag_div.getStyle("margin-left") );

    if( cb_w >= cw ) {
        return;
    }

    var max_off_x = cb_w - sd_w;
    var new_off_x = sd_off_x + dx;
    if( new_off_x < 0 ) { new_off_x = 0; }
    if( new_off_x > max_off_x ) { new_off_x = max_off_x; }

    // now map it back to the full scrollTop ...
    var new_scr_left = Math.floor( (1.0 * (new_off_x / cb_w) * cw) + 0.5 );
    content_box.scrollLeft = new_scr_left;

    // and set offset for the scroll draggable too ...
    scr_x_drag_div.setStyle("margin-left", new_off_x+"px");
}


spt.resize_scroll.drag_y_scroll_draggable_motion = function( evt, bvr, mouse_411 )
{
    var rsw_top_el = bvr.src_el.getParent(".SPT_RSW_TOP");
    var dy = mouse_411.curr_y - mouse_411.last_y;

    var content_box = rsw_top_el.getElement(".SPT_RSW_CONTENT_BOX");
    var contents = content_box.getElement(".SPT_RSW_CONTENTS");
    var scr_y_drag_div = rsw_top_el.getElement(".SPT_SCROLL_Y_DRAG");

    var ch = spt.get_render_display_height( contents );
    var cb_h = content_box.clientHeight;
    var sd_h = scr_y_drag_div.clientHeight;
    var sd_off_y = parseInt( scr_y_drag_div.getStyle("margin-top") );

    if( cb_h >= ch ) {
        return;
    }

    var max_off_y = cb_h - sd_h;
    var new_off_y = sd_off_y + dy;
    if( new_off_y < 0 ) { new_off_y = 0; }
    if( new_off_y > max_off_y ) { new_off_y = max_off_y; }

    // now map it back to the full scrollTop ...
    var new_scr_top = Math.floor( (1.0 * (new_off_y / cb_h) * ch) + 0.5 );
    content_box.scrollTop = new_scr_top;

    // and set offset for the scroll draggable too ...
    scr_y_drag_div.setStyle("margin-top", new_off_y+"px");
}


spt.resize_scroll.adjust_scroll_x_draggable = function( activating_el )
{
    var rsw_top_el = activating_el.getParent(".SPT_RSW_TOP");
    var content_box = rsw_top_el.getElement(".SPT_RSW_CONTENT_BOX");
    var contents = content_box.getElement(".SPT_RSW_CONTENTS");

    var cw = spt.get_render_display_width( contents );
    var cb_w = content_box.clientWidth;

    var scroll_x_div = rsw_top_el.getElement(".SPT_SCROLL_X")
    var scroll_x_drag_div = rsw_top_el.getElement(".SPT_SCROLL_X_DRAG")

    // adjust size of scroll draggable ...
    var w = 1.0 * (cb_w / cw) * cb_w;
    if( w < 6 ) {
        w = 6;
    }
    scroll_x_drag_div.setStyle("width",w+"px");
    scroll_x_drag_div.setStyle("height","40px");

    // adjust offset of scroll draggable ...
    var s_left = 1.0 * (content_box.scrollLeft / cw) * cb_w;
    scroll_x_drag_div.setStyle("margin-left", s_left+"px");
}


spt.resize_scroll.adjust_scroll_y_draggable = function( activating_el )
{
    var rsw_top_el = activating_el.getParent(".SPT_RSW_TOP");
    var content_box = rsw_top_el.getElement(".SPT_RSW_CONTENT_BOX");
    var contents = content_box.getElement(".SPT_RSW_CONTENTS");

    var ch = spt.get_render_display_height( contents );
    var cb_h = content_box.clientHeight;

    var scroll_y_div = rsw_top_el.getElement(".SPT_SCROLL_Y")
    var scroll_y_drag_div = rsw_top_el.getElement(".SPT_SCROLL_Y_DRAG")

    // adjust size of scroll draggable ...
    var h = 1.0 * (cb_h / ch) * cb_h;
    if( h < 6 ) {
        h = 6;
    }
    scroll_y_drag_div.setStyle("width","40px");
    scroll_y_drag_div.setStyle("height",h+"px");

    // compensate for a display artifact in Opera browser
    if( spt.browser.is_Opera() ) {
        scroll_y_div.setStyle("height", cb_h+"px");
    }

    // adjust offset of scroll draggable ...
    var s_top = 1.0 * (content_box.scrollTop / ch) * cb_h;
    scroll_y_drag_div.setStyle("margin-top", s_top+"px");
}


spt.resize_scroll.adjust_scroll_draggables = function( activating_el )
{
    spt.resize_scroll.adjust_scroll_x_draggable( activating_el );
    spt.resize_scroll.adjust_scroll_y_draggable( activating_el );
}


spt.resize_scroll.adjust_for_scroll = function( activating_el )
{
    var rsw_top_el = activating_el.getParent(".SPT_RSW_TOP");
    var content_box = rsw_top_el.getElement(".SPT_RSW_CONTENT_BOX");
    var contents = content_box.getElement(".SPT_RSW_CONTENTS");

    var cw = spt.get_render_display_width( contents );
    var ch = spt.get_render_display_height( contents );

    var cb_w = content_box.clientWidth;
    var cb_h = content_box.clientHeight;

    var scroll_x_div = rsw_top_el.getElement(".SPT_SCROLL_X")
    var scroll_x_drag_div = rsw_top_el.getElement(".SPT_SCROLL_X_DRAG")
    var scroll_y_div = rsw_top_el.getElement(".SPT_SCROLL_Y")
    var scroll_y_drag_div = rsw_top_el.getElement(".SPT_SCROLL_Y_DRAG")

    var scroll_bar_sz = parseInt( rsw_top_el.getProperty("spt_scroll_size") );

    var is_scroll_x_shown = true;
    if( spt.is_hidden(scroll_x_div) ) {
        is_scroll_x_shown = false;
    }
    var is_scroll_y_shown = true;
    if( spt.is_hidden(scroll_y_div) ) {
        is_scroll_y_shown = false;
    }

    var top_el = rsw_top_el;
    if( ! top_el.hasClass("SPT_RSW_OUTER_TOP") ) {
        top_el = rsw_top_el.getParent(".SPT_RSW_OUTER_TOP");
    }
    var scroll_expansion = rsw_top_el.getProperty("spt_scroll_expansion");

    var dy_adjust = 0;
    if( cw > cb_w ) {
        if( ! is_scroll_x_shown ) {
            // display x scroll ...
            dy_adjust = scroll_bar_sz;
            spt.resize_scroll.adjust_control_size( top_el, "DY", dy_adjust );

            spt.show( scroll_x_div );
            is_scroll_x_shown = true;
        }
        spt.resize_scroll.adjust_scroll_x_draggable( activating_el );
    } else {
        if( is_scroll_x_shown ) {
            // hide x scroll ...
            dy_adjust = 0 - scroll_bar_sz;
            spt.resize_scroll.adjust_control_size( top_el, "DY", dy_adjust );
            spt.hide( scroll_x_div );
            is_scroll_x_shown = false;
        }
    }

    if( dy_adjust ) {
        if( scroll_expansion == "outside" ) {
            var dy_el_list = top_el.getElements(".spt_pwin_DY");
            dy_el_list.push( top_el );
            for( var c=0; c < dy_el_list.length; c++ ) {
                var el = dy_el_list[c];
                if( el.className.contains("_B_2_i_") || el.className.contains("_B_2_i ") ) {
                    continue;
                }
                var el_h = parseInt( el.getStyle("height") );
                el.setStyle("height", (el_h+dy_adjust) + "px");
            }
        }
        else if( scroll_expansion == "inside" ) {
            var dy_el_list = rsw_top_el.getElements(".spt_pwin_DY");
            dy_el_list.push( rsw_top_el );
            for( var c=0; c < dy_el_list.length; c++ ) {
                var el = dy_el_list[c];
                if( el.className.contains("_B_2_i_") || el.className.contains("_B_2_i ") ) {
                    var el_h = parseInt( el.getStyle("height") );
                    el.setStyle("height", (el_h-dy_adjust) + "px");
                }
            }
        }
        else {
            log.warning("WARNING: unknown scroll_expansion value found ('" +  scroll_expansion + "')");
        }
    }

    var dx_adjust = 0;
    if( ch > cb_h ) {
        if( ! is_scroll_y_shown ) {
            // display y scroll ...
            dx_adjust = scroll_bar_sz;
            spt.resize_scroll.adjust_control_size( top_el, "DX", dx_adjust );

            spt.show( scroll_y_div );
            is_scroll_y_shown = true;
        }
        spt.resize_scroll.adjust_scroll_y_draggable( activating_el );
    } else {
        if( is_scroll_y_shown ) {
            // hide y scroll ...
            dx_adjust = 0 - scroll_bar_sz;
            spt.resize_scroll.adjust_control_size( top_el, "DX", dx_adjust );
            spt.hide( scroll_y_div );
            is_scroll_y_shown = false;
        }
    }

    if( dx_adjust ) {
        if( scroll_expansion == "outside" ) {
            var dx_el_list = top_el.getElements(".spt_pwin_DX");
            dx_el_list.push( top_el );
            for( var c=0; c < dx_el_list.length; c++ ) {
                var el = dx_el_list[c];
                if( el.className.contains("_B_2_i_a ") || el.className.contains("_B_2_ii_a ") ) {
                    continue;
                }
                if( el.hasClass("SPT_SCROLL_X") || el.hasClass("SPT_RESIZE_Y") ) {
                    continue;
                }
                var el_w = parseInt( el.getStyle("width") );
                el.setStyle("width", (el_w+dx_adjust) + "px");
            }
        }
        else if( scroll_expansion == "inside" ) {
            var dx_el_list = rsw_top_el.getElements(".spt_pwin_DX");
            dx_el_list.push( rsw_top_el );
            for( var c=0; c < dx_el_list.length; c++ ) {
                var el = dx_el_list[c];
                if( el.className.contains("_B_2_i_a ") || el.className.contains("_B_2_ii_a ") ) {
                    var el_w = parseInt( el.getStyle("width") );
                    el.setStyle("width", (el_w-dx_adjust) + "px");
                }
            }
        }
        else {
            log.warning("WARNING: unknown scroll_expansion value found ('" +  scroll_expansion + "')");
        }
    }

    var resize_img = top_el.getElement(".SPT_PWIN_RESIZE_IMG");
    if( resize_img ) {
        if( is_scroll_x_shown && is_scroll_y_shown ) {
            resize_img.setStyle("right","2px");
            resize_img.setStyle("bottom","2px");
        } else {
            resize_img.setStyle("right","4px");
            resize_img.setStyle("bottom","4px");
        }
    }
}


spt.resize_scroll.adjust_control_size = function( rsw_top_el, DX_or_DY, size_adj )
{
    var top_el = rsw_top_el;
    if( ! top_el.hasClass("SPT_RSW_OUTER_TOP") ) {
        top_el = rsw_top_el.getParent(".SPT_RSW_OUTER_TOP");
    }

    var el_list = top_el.getElements( ".spt_controls_" + DX_or_DY );
    var dim = "height";
    if( DX_or_DY == 'DX' ) {
        dim = "width";
    }
    for( var c=0; c < el_list.length; c++ ) {
        var el = el_list[c];
        el.setStyle( dim, parseInt(el.getStyle(dim)) + size_adj + "px" );
    }
}


spt.resize_scroll.wheel_scroll = function( evt, bvr, mouse_411 )
{
    var content_box = bvr.src_el;   // expects bvr to be assigned on the element with class "SPT_RSW_CONTENT_BOX"
    var contents = content_box.getElement(".SPT_RSW_CONTENTS");

    var ch = spt.get_render_display_height( contents );
    var cb_h = content_box.clientHeight;
    if( cb_h >= ch ) {
        return;
    }

    var max_scroll_top = ch - cb_h;

    var scroll_top = content_box.scrollTop;
    var delta = 30;
    if( evt.wheel < 0 ) {
        scroll_top += delta;
    } else {
        scroll_top -= delta;
    }

    if( scroll_top < 0 ) { scroll_top = 0; }
    if( scroll_top > max_scroll_top ) { scroll_top = max_scroll_top; }

    content_box.scrollTop = scroll_top;
    spt.resize_scroll.adjust_for_scroll( bvr.src_el );
}









        '''

