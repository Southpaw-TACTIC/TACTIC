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

    def get_args_keys(self):
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


    def init(self):
        self.show_option = False
        self.label = self.kwargs.get('label')
        self.tip = self.kwargs.get('tip')
        self.size = self.kwargs.get('size')
        self.width = self.kwargs.get('width')
        self.side_padding = self.kwargs.get('side_padding')
        
        if self.side_padding:
            self.side_padding = int(self.side_padding)
        else:
            self.side_padding = 0

        # self.top_el = SpanWdg()
        self.top_el = DivWdg()
        self.top_el.add_styles( "cursor: pointer; white-space: nowrap;" )
        self.top_el.add_class( "SPT_TextBtnWdg_TOP" )

        # Add tool tip if provided ...
        if self.tip:
            # not sure why the tool-tip only shows up if you provide the text in the 'title' (2nd) argument and not
            # the 'message' (first) argument ...
            self.top_el.add_tip( "", self.tip )

        self.horiz_align = self.kwargs.get('horiz_align')
        if not self.horiz_align:
            self.horiz_align = 'none'  # default to no alignment

        self.horiz_offset = self.kwargs.get('horiz_offset')
        if type(self.horiz_offset) == int:
            self.horiz_offset = "%spx" % self.horiz_offset
        if not self.horiz_offset:
            self.horiz_offset = "0px"

        self.vert_offset = self.kwargs.get('vert_offset')
        if type(self.vert_offset) == int:
            self.vert_offset = "%spx" % self.vert_offset
        if not self.vert_offset:
            self.vert_offset = "0px"


        self.div_right = DivWdg()
        

    def get_label(self):
        return self.label


    def get_top_el(self):
        return self.top_el


    def add_behavior(self, bvr):
        self.top_el.add_behavior( bvr )

    def add(self, widget):
        self.top_el.add( widget )

    def get_display(self): 

        web = WebContainer.get_web()
        skin = web.get_skin()

        # default to 'small' size ...
        h = 16
        fnt_sz = 11

        if self.size == 'medium':
            h = 18
            fnt_sz = 13
        elif self.size == 'large':
            h = 20
            fnt_sz = 15

        w = (h / 2) - 1

        self.top_el.add_styles( "height: %spx;" % (h) )

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
        span = SpanWdg(self.label)

        # this is better fixed. Bold fonts don't look good 
        span.add_style('font-weight: 100')
        span.add_style('vertical-align: middle')

        div_mid.add( span )
        div_mid.add( spacer )

        if self.show_option:
            bgi_close = '_options.png)'
            w += 10
        
        self.div_right.add_styles( "%(bgi_open)s%(pos)s%(bgi_close)s;" %
                                    {'bgi_open': bgi_open, 'pos': 'right', 'bgi_close': bgi_close} )
        self.div_right.add_styles("float: left; height: %spx; width: %spx;" % (h, w) )
        self.top_el.add( div_left )
        self.top_el.add( div_mid )
        self.top_el.add( self.div_right )

        self.top_el.add_styles("overflow: hidden;")
        if self.horiz_align == 'center':
            self.top_el.add_styles("margin: auto;")   # margin: auto -- used for centering in non-IE brwsrs
        elif self.horiz_align == 'left':
            self.top_el.add_styles("margin-left: %s;" % self.horiz_offset)

        if self.vert_offset:
            self.top_el.add_styles("margin-top: %s;" % self.vert_offset)

        if self.width:
            if type(self.width) == str:
                self.width.replace("px","")
            self.top_el.add_styles("width: %spx" % self.width)
        else:
            self.top_el.add_behavior({'type': 'load', 'cbjs_action': 'spt.widget.btn_wdg.set_btn_width( bvr.src_el );' })

        return self.top_el

class TextOptionBtnWdg(TextBtnWdg):
    '''This comes with a small arrow on the side which can be used to attach to 
       a smart menu for instance'''

    def init(self):
        super(TextOptionBtnWdg, self).init()
        self.show_option = True
        

    def get_option_widget(self):
        return self.div_right

class TextBtnSetWdg(BaseRefreshWdg):

    def get_args_keys(self):
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


    def init(self):
        self.float = self.kwargs.get("float")
        self.align = self.kwargs.get("align")
        self.buttons = self.kwargs.get("buttons")
        self.spacing = self.kwargs.get("spacing")
        self.size = self.kwargs.get("size")
        self.side_padding = self.kwargs.get("side_padding")

        self.button_widgets = []

        for btn_map in self.buttons:
            width = 0
            if btn_map.has_key("width"):
                width = btn_map.get("width")
            txt_btn = TextBtnWdg( label = btn_map.get("label"),
                                  tip = btn_map.get("tip"),
                                  size = self.size,
                                  width = width,
                                  side_padding = self.side_padding )
            if btn_map.has_key("bvr"):
                bvr = {}
                if not bvr.has_key("type"):
                    bvr = {'type':'click_up'}
                bvr.update( btn_map.get("bvr") )
                txt_btn.add_behavior( bvr )

            self.button_widgets.append( txt_btn )


    def get_btn_by_label(self, label):

        for btn_wdg in self.button_widgets:
            if btn_wdg.get_label() == label:
                return btn_wdg
        return None


    def get_btn_top_el_by_label(self, label):

        for btn_wdg in self.button_widgets:
            if btn_wdg.get_label() == label:
                return btn_wdg.get_top_el()
        return None


    def get_display(self):
        
        table = Table()
        table.add_row()

        count = 0
        for btn_wdg in self.button_widgets:
            td = table.add_cell()
            if self.spacing and count:
                td.add_styles( "padding-left: %spx;" % self.spacing )
            count += 1
            td.add( btn_wdg )

        if self.float:
            table.add_styles("float: %s;" % self.float)
        if self.align:
            if self.align == "left":
                table.push_left()
            elif self.align == "right":
                table.push_right()
            elif self.align == "center":
                table.center()

        return table



