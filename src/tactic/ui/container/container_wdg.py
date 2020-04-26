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
__all__ = ["LabeledHidableWdg", "RoundedCornerDivWdg", "HorizLayoutWdg"]

from pyasm.web import *
from pyasm.widget import IconWdg

from tactic.ui.common import BaseRefreshWdg, CornerGenerator


class LabeledHidableWdg(DivWdg):

    def __init__(self, name="", label="", label_align="", content_align=""):
        super(LabeledHidableWdg,self).__init__(name)
        self.added_content_list = []
        self.label = label
        self.label_align = label_align
        self.content_align = content_align
        self.width_str = None
        self.content_height_str = None


    def add(self, content):
        self.added_content_list.append( content )


    def set_dimensions(self, width_str=None, content_height_str=None):
        self.width_str = width_str
        self.content_height_str = content_height_str


    def set_label(self, label):
        self.label = label
        
    """ 
    #TODO: make use of this old vertical slide animation by dynamically adding a js file 
    def get_onload_js(self):
        return '''spt.onload.load_jsfile("/context/spt_js/fx_anim.js", "js")'''
    """

    def get_display(self):
        
        if self.width_str:
            self.add_style("width",self.width_str)

        label_div = HtmlElement.div()
        #label_div.add_behavior({'type': 'load',
        #    'cbjs_action': self.get_onload_js()})

        if self.label_align:
            label_div.add_style("text-align: " + self.label_align)

        label_span = HtmlElement.span()
        label_span.add_color("color", "color")
        label_span.add_class("SPT_BVR spt_labeledhidable_label")
        label_span.add(self.label)

        hidable_div = HtmlElement.div()
        # hidable_div.set_attr("id", hidable_id)
        hidable_id = hidable_div.set_unique_id(prefix="spt_hidable")
        if self.content_height_str:
            hidable_div.add_style("height",self.content_height_str)

        if self.added_content_list:
            for i in range(len(self.added_content_list)):
                hidable_div.add( self.added_content_list[i] )
        else:
            hidable_div.add("&nbsp;")

        """
        #NOT USED right now
        label_span.add_behavior( {'type': 'click_up', 'cbfn_action': 'spt.fx.slide_anim_cbk',
                                  'dst_el': hidable_id, 'options': {'direction': 'vert'}} )

        label_span.add_behavior( {'type':'hover', 'hover_class': 'spt_labeledhidable_label_hover'} )
        """
        label_div.add( label_span )

        self.add_widget( label_div )
        self.add_widget( hidable_div )

        return super(LabeledHidableWdg,self).get_display()



class RoundedCornerDivWdg(DivWdg):

    def __init__(self, name="", hex_color_code="2F2F2F", corner_size=""):
        super(RoundedCornerDivWdg,self).__init__(name)

        self.added_content_list = []

        self.hex_color_code = hex_color_code
        if self.hex_color_code.startswith("#"):
            self.hex_color_code = self.hex_color_code.replace("#", "")

        self.corner_size = corner_size
        self.width_str = None
        self.height_str = None
        self.content_height_str = None

        self.content_div = DivWdg()
        #self.content_div.add_style("display: block")
        #self.content_div.add_sytle("float: left")  # float left to ensure shrink wrapping

        if not self.corner_size:
            self.corner_size = "5px"


    def get_content_wdg(self):
        return self.content_div


    def set_dimensions(self, width_str=None, content_height_str=None, height_str=None):
        self.width_str = width_str
        self.height_str = height_str
        self.content_height_str = content_height_str


    def add(self, content):
        self.added_content_list.append( content )


    def get_display(self):
        if self.added_content_list:
            for i in range(len(self.added_content_list)):
                self.content_div.add( self.added_content_list[i] )

        #if self.width_str:
        #    self.content_div.add_style('width: %s' % self.width_str)
        #if self.height_str:
        #    self.content_div.add_style('height: %s' % self.height_str)
        #if self.content_height_str:
        #    self.content_div.add_style('height: %s' % self.content_height_str)

        self.add_widget(self.content_div)
        #self.add_color("background", "background")
        self.add_style( 'background-color: #%s' % self.hex_color_code )
        self.set_round_corners(5)
        self.add_style("padding: 5px")
        return super(RoundedCornerDivWdg, self).get_display()



    def get_display2(self):

        if not CornerGenerator.color_exists(self.hex_color_code):
            CornerGenerator.generate(self.hex_color_code)

        # set up the table
        table = Table(css="spt_rounded_div")
        table.add_style("border: none")
        if self.width_str:
            table.add_style('width: %s' % self.width_str)
        if self.height_str:
            table.add_style('height: %s' % self.height_str)

        img_suffix = ''

        top_row = table.add_row()
        td1 = table.add_cell(css="spt_rounded_div")
        td1.add_style( 'width: %s' % self.corner_size )
        td1.add_style( 'min-width: %s' % self.corner_size )
        td1.add_style( 'height: %s' % self.corner_size )
        td1.add_style( 'background-image: url("/context/ui_proto/roundcorners/rc_%s/rc_%s_%sx%s_TL%s.png")' %
                        (self.hex_color_code,self.hex_color_code,self.corner_size,self.corner_size,img_suffix) )

        td2 = table.add_cell(css="spt_rounded_div")
        td2.add_style( 'height: %s' % self.corner_size )
        td2.add_style( 'font-size: 1px' )
        td2.add_style( 'background-color: #%s' % self.hex_color_code )

        td3 = table.add_cell(css="spt_rounded_div")
        td3.add_style( 'width: %s' % self.corner_size )
        td3.add_style( 'min-width: %s' % self.corner_size )
        td3.add_style( 'height: %s' % self.corner_size )
        td3.add_style( 'background-image: url("/context/ui_proto/roundcorners/rc_%s/rc_%s_%sx%s_TR%s.png")' %
                        (self.hex_color_code,self.hex_color_code,self.corner_size,self.corner_size,img_suffix) )

        content_row = table.add_row()
        td1 = table.add_cell(css="spt_rounded_div")
        td1.add_style( 'background-color: #%s' % self.hex_color_code )

        td2 = table.add_cell(css="spt_rounded_div")
        td2.add_style( 'background-color: #%s' % self.hex_color_code )

        # -- DO NOT SET THE HEIGHT OR WIDTH OF THE contents cell ... this needs to resize with the size
        # -- of its contents ... commenting out the next two lines.
        #
        # td2.add_style( 'height: %s' % self.corner_size )
        # td2.add_style( 'max-height: %s' % self.corner_size )

        td3 = table.add_cell(css="spt_rounded_div")
        td3.add_style( 'background-color: #%s' % self.hex_color_code )
        if self.content_height_str:
            td2.add_style( 'height: %s' % self.content_height_str )

        td2.add(self.content_div)
        td2.add_style( 'vertical-align: top')
        if self.added_content_list:
            for i in range(len(self.added_content_list)):
                self.content_div.add( self.added_content_list[i] )
        #else:
        #    self.content_div.add("&nbsp;")

        bottom_row = table.add_row()
        td1 = table.add_cell(css="spt_rounded_div")
        td1.add_style( 'width: %s' % self.corner_size )
        td1.add_style( 'height: %s' % self.corner_size )
        td1.add_style( 'background-image: url("/context/ui_proto/roundcorners/rc_%s/rc_%s_%sx%s_BL%s.png")' %
                        (self.hex_color_code,self.hex_color_code,self.corner_size,self.corner_size,img_suffix) )

        td2 = table.add_cell(css="spt_rounded_div")
        td2.add_style( 'background-color: #%s' % self.hex_color_code )

        td3 = table.add_cell(css="spt_rounded_div")
        td3.add_style( 'width: %s' % self.corner_size )
        td3.add_style( 'height: %s' % self.corner_size )
        td3.add_style( 'background-image: url("/context/ui_proto/roundcorners/rc_%s/rc_%s_%sx%s_BR%s.png")' %
                        (self.hex_color_code,self.hex_color_code,self.corner_size,self.corner_size,img_suffix) )

        self.add_widget(table)

        return super(RoundedCornerDivWdg, self).get_display()




__all__.append('EmptyWdg')
class EmptyWdg(BaseRefreshWdg):

    def get_display(self):
        top = self.top;
        top.add_class("spt_empty_top");
        return top






class HorizLayoutWdg(BaseRefreshWdg):

    def get_args_keys(self):
        return {
        'widget_map_list': 'List of widget defining dictionaries, in this format ... {"wdg": wdg, "style": style_str}',
        'spacing': 'The width in between widgets',
        'float': 'Float positioning ... float "left", float "right" or not defined'
        }


    def get_display(self):
        self.widget_map_list = self.kwargs.get("widget_map_list")
        self.spacing = self.kwargs.get("spacing")
        self.float = self.kwargs.get("float")

        div = DivWdg()
        if self.float:
            div.add_styles("float: %s;" % self.float)

        table = Table()
        table.add_row()

        count = 0
        for wdg_map in self.widget_map_list:
            td = table.add_cell()
            if self.spacing and count:
                td.add_styles( "padding-left: %spx;" % self.spacing )
            count += 1
            td.add( wdg_map.get('wdg') )
            if wdg_map.get('style'):
                td.add_styles( wdg_map.get('style') )

        div.add( table )
        return div



