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



