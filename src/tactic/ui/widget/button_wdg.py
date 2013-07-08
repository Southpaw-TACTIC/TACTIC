###########################################################
#
# Copyright (c) 2009, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#
__all__ = ["TextBtnWdg","TextBtnSetWdg","TextOptionBtnWdg"]

from pyasm.web import DivWdg, HtmlElement, SpanWdg, Table, WebContainer
from pyasm.widget import SelectWdg, WidgetConfig, IconWdg

from tactic.ui.common import BaseRefreshWdg


class TextBtnWdg(BaseRefreshWdg):

    def get_args_keys(my):
        return {
            'label': 'Button label text.',
            'tip': 'Hover tool-tip text (not implemented yet).',
            'size': 'This is either: small (16px high), or medium (20px high) ...  or large, for now.',
            'side_padding': 'This is the padding to place on each side of the text in the button.',
            'width': 'The width for the whole button - best if this is specified.',
            'horiz_align': 'Horizontal alignment ... "none", "left" or "center" ... defaults to "none"',
            'horiz_offset': 'Used only with horiz_align of "left" or "right" ... distance from left or right',
            'vert_offset': 'Vertical Offset'
        }


    def init(my):
        my.show_option = False
        my.label = my.kwargs.get('label')
        my.tip = my.kwargs.get('tip')
        my.size = my.kwargs.get('size')
        my.width = my.kwargs.get('width')
        my.side_padding = my.kwargs.get('side_padding')
        
        if my.side_padding:
            my.side_padding = int(my.side_padding)
        else:
            my.side_padding = 0

        # my.top_el = SpanWdg()
        my.top_el = DivWdg()
        my.top_el.add_styles( "cursor: pointer; white-space: nowrap;" )
        my.top_el.add_class( "SPT_TextBtnWdg_TOP" )

        # Add tool tip if provided ...
        if my.tip:
            # not sure why the tool-tip only shows up if you provide the text in the 'title' (2nd) argument and not
            # the 'message' (first) argument ...
            my.top_el.add_tip( "", my.tip )

        my.horiz_align = my.kwargs.get('horiz_align')
        if not my.horiz_align:
            my.horiz_align = 'none'  # default to no alignment

        my.horiz_offset = my.kwargs.get('horiz_offset')
        if type(my.horiz_offset) == int:
            my.horiz_offset = "%spx" % my.horiz_offset
        if not my.horiz_offset:
            my.horiz_offset = "0px"

        my.vert_offset = my.kwargs.get('vert_offset')
        if type(my.vert_offset) == int:
            my.vert_offset = "%spx" % my.vert_offset
        if not my.vert_offset:
            my.vert_offset = "0px"


        my.div_right = DivWdg()
        

    def get_label(my):
        return my.label


    def get_top_el(my):
        return my.top_el


    def add_behavior(my, bvr):
        my.top_el.add_behavior( bvr )

    def add(my, widget):
        my.top_el.add( widget )

    def get_display(my): 

        web = WebContainer.get_web()
        skin = web.get_skin()

        # default to 'small' size ...
        h = 16
        fnt_sz = 11

        if my.size == 'medium':
            h = 18
            fnt_sz = 13
        elif my.size == 'large':
            h = 20
            fnt_sz = 15

        w = (h / 2) - 1

        my.top_el.add_styles( "height: %spx;" % (h) )

        t_styles = "color: #c2c2c2; border: 0px; border-collapse: collapse; padding: 0px"
        bgi_open = "background-image: url(/context/themes/%(skin)s/images/text_btn/%(skin)s_btn_h%(h)s_" % \
                    {'skin': skin, 'h': h}
        bgi_close = ".png)"

        # pos_list = [ 'left', 'middle', 'right' ]
        spacer = HtmlElement.img( IconWdg.get_icon_path("TRANSPARENT") )
        spacer.add_styles( "width: 2px;" )

        div_left = DivWdg()
        div_left.add_styles( "%(bgi_open)s%(pos)s%(bgi_close)s;" %
                                    {'bgi_open': bgi_open, 'pos': 'left', 'bgi_close': bgi_close} )
        div_left.add_styles("float: left; height: %spx; width: %spx;" % (h, w) )

        div_mid = DivWdg()
        div_mid.add_styles( "%(bgi_open)s%(pos)s%(bgi_close)s;" %
                                    {'bgi_open': bgi_open, 'pos': 'middle', 'bgi_close': bgi_close} )
        div_mid.add_styles("float: left; height: %spx; width: auto;" % (h) )
        div_mid.add_styles("color: #c2c2c2;")
        div_mid.add_styles("vertical-align: middle")
        # move the text lower by 1 px
        div_mid.add_style('padding-top: 1px')

        div_mid.add_styles( "font-family: Arial, Helvetica, sans-serif; font-size: %spx;" % fnt_sz )
        div_mid.add( spacer )
        span = SpanWdg(my.label)

        # this is better fixed. Bold fonts don't look good 
        span.add_style('font-weight: 100')
        span.add_style('vertical-align: middle')

        div_mid.add( span )
        div_mid.add( spacer )

        if my.show_option:
            bgi_close = '_options.png)'
            w += 10
        
        my.div_right.add_styles( "%(bgi_open)s%(pos)s%(bgi_close)s;" %
                                    {'bgi_open': bgi_open, 'pos': 'right', 'bgi_close': bgi_close} )
        my.div_right.add_styles("float: left; height: %spx; width: %spx;" % (h, w) )
        my.top_el.add( div_left )
        my.top_el.add( div_mid )
        my.top_el.add( my.div_right )

        my.top_el.add_styles("overflow: hidden;")
        if my.horiz_align == 'center':
            my.top_el.add_styles("margin: auto;")   # margin: auto -- used for centering in non-IE brwsrs
        elif my.horiz_align == 'left':
            my.top_el.add_styles("margin-left: %s;" % my.horiz_offset)

        if my.vert_offset:
            my.top_el.add_styles("margin-top: %s;" % my.vert_offset)

        if my.width:
            if type(my.width) == str:
                my.width.replace("px","")
            my.top_el.add_styles("width: %spx" % my.width)
        else:
            my.top_el.add_behavior({'type': 'load', 'cbjs_action': 'spt.widget.btn_wdg.set_btn_width( bvr.src_el );' })

        return my.top_el

class TextOptionBtnWdg(TextBtnWdg):
    '''This comes with a small arrow on the side which can be used to attach to 
       a smart menu for instance'''

    def init(my):
        super(TextOptionBtnWdg, my).init()
        my.show_option = True
        

    def get_option_widget(my):
        return my.div_right

class TextBtnSetWdg(BaseRefreshWdg):

    def get_args_keys(my):
        return {
            'float': 'Choice of "right" (float right), "left" (float left), or not defined',
            'align': 'Margin alignment of button set ... choice of "left", "right" or "center" ... if not defined ' \
                     'then margins are not provided for the button set top element',
            'buttons': 'List of dictionaries outlining information for each button',
            'spacing': 'The amount of space between buttons',
            'size': 'This is either: small (16px high), or medium (20px high) ... for now (passed down to buttons)',
            'side_padding': 'This is the padding to place on each side of the text in the button (passed down to' \
                            ' buttons)'
        }


    def init(my):
        my.float = my.kwargs.get("float")
        my.align = my.kwargs.get("align")
        my.buttons = my.kwargs.get("buttons")
        my.spacing = my.kwargs.get("spacing")
        my.size = my.kwargs.get("size")
        my.side_padding = my.kwargs.get("side_padding")

        my.button_widgets = []

        for btn_map in my.buttons:
            width = 0
            if btn_map.has_key("width"):
                width = btn_map.get("width")
            txt_btn = TextBtnWdg( label = btn_map.get("label"),
                                  tip = btn_map.get("tip"),
                                  size = my.size,
                                  width = width,
                                  side_padding = my.side_padding )
            if btn_map.has_key("bvr"):
                bvr = {}
                if not bvr.has_key("type"):
                    bvr = {'type':'click_up'}
                bvr.update( btn_map.get("bvr") )
                txt_btn.add_behavior( bvr )

            my.button_widgets.append( txt_btn )


    def get_btn_by_label(my, label):

        for btn_wdg in my.button_widgets:
            if btn_wdg.get_label() == label:
                return btn_wdg
        return None


    def get_btn_top_el_by_label(my, label):

        for btn_wdg in my.button_widgets:
            if btn_wdg.get_label() == label:
                return btn_wdg.get_top_el()
        return None


    def get_display(my):
        
        table = Table()
        table.add_row()

        count = 0
        for btn_wdg in my.button_widgets:
            td = table.add_cell()
            if my.spacing and count:
                td.add_styles( "padding-left: %spx;" % my.spacing )
            count += 1
            td.add( btn_wdg )

        if my.float:
            table.add_styles("float: %s;" % my.float)
        if my.align:
            if my.align == "left":
                table.push_left()
            elif my.align == "right":
                table.push_right()
            elif my.align == "center":
                table.center()

        return table



