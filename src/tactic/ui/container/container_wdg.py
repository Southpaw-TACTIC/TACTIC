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



