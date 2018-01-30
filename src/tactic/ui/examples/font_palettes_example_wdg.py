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
__all__ = ["FontPalettesExampleWdg"]

from pyasm.web import DivWdg, HtmlElement, SpanWdg, Table, WebContainer
from pyasm.widget import SelectWdg, WidgetConfig, IconWdg

from base_example_wdg import BaseExampleWdg


class FontPalettesExampleWdg(BaseExampleWdg):

    def get_example_title(self):
        return "Font Palette Reference"


    def get_example_description(self):
        return "Listing of Font Palettes and examples of how they will appear in the interface. You can switch " \
                "between font palettes with various style modifiers -- normal, bold, italic, bold + italic."


    def get_example_display(self):

        font_div = DivWdg()

        font_div.add_styles( "background: #CCCCCC; color: #000000; border: 3px solid black; width: 750px;" )


        font_table = Table()
        font_table.add_styles( "margin-top: 6px;" )
        font_table.add_row()

        ft_style = "border: 1px solid black; border-collapse: collapse; padding: 3px; " \
                   "color: #000000; cursor: pointer; %s"

        td = font_table.add_cell()
        td.add_styles( "border: 0px; border-collapse: collapse; padding: 0px; width: 6px; background: #CCCCCC;" )
        td.add( "&nbsp;" )

        td = font_table.add_cell()
        td.set_id("SPT_FONT_EXAMPLE_BTN")
        td.add_styles( ft_style % "background: #CCCCCC;" )
        td.add( "normal" )
        td.add_behavior( { 'type': 'click_up',
                           'cbjs_action': '$("SPT_FONT_EXAMPLE").setStyle("display","block"); ' \
                                        '$("SPT_FONT_EXAMPLE_ITALIC").setStyle("display","none"); ' \
                                        '$("SPT_FONT_EXAMPLE_BOLD").setStyle("display","none"); ' \
                                        '$("SPT_FONT_EXAMPLE_BOLD_ITALIC").setStyle("display","none"); ' \
                                        '$("SPT_FONT_EXAMPLE_BTN").setStyle("background","#CCCCCC"); ' \
                                        '$("SPT_FONT_EXAMPLE_ITALIC_BTN").setStyle("background","#777777"); ' \
                                        '$("SPT_FONT_EXAMPLE_BOLD_BTN").setStyle("background","#777777"); ' \
                                        '$("SPT_FONT_EXAMPLE_BOLD_ITALIC_BTN").setStyle("background","#777777"); ' } )

        td = font_table.add_cell()
        td.add_styles( "border: 0px; border-collapse: collapse; padding: 0px; width: 6px; background: #CCCCCC;" )
        td.add( "&nbsp;" )

        td = font_table.add_cell()
        td.set_id("SPT_FONT_EXAMPLE_ITALIC_BTN")
        td.add_styles( ft_style % "background: #777777;" )
        td.add( "<i>italic</i>" )
        td.add_behavior( { 'type': 'click_up',
                           'cbjs_action': '$("SPT_FONT_EXAMPLE").setStyle("display","none"); ' \
                                        '$("SPT_FONT_EXAMPLE_ITALIC").setStyle("display","block"); ' \
                                        '$("SPT_FONT_EXAMPLE_BOLD").setStyle("display","none"); ' \
                                        '$("SPT_FONT_EXAMPLE_BOLD_ITALIC").setStyle("display","none"); ' \
                                        '$("SPT_FONT_EXAMPLE_BTN").setStyle("background","#777777"); ' \
                                        '$("SPT_FONT_EXAMPLE_ITALIC_BTN").setStyle("background","#CCCCCC"); ' \
                                        '$("SPT_FONT_EXAMPLE_BOLD_BTN").setStyle("background","#777777"); ' \
                                        '$("SPT_FONT_EXAMPLE_BOLD_ITALIC_BTN").setStyle("background","#777777"); ' } )

        td = font_table.add_cell()
        td.add_styles( "border: 0px; border-collapse: collapse; padding: 0px; width: 6px; background: #CCCCCC;" )
        td.add( "&nbsp;" )

        td = font_table.add_cell()
        td.set_id("SPT_FONT_EXAMPLE_BOLD_BTN")
        td.add_styles( ft_style % "background: #777777;" )
        td.add( "<b>bold</b>" )
        td.add_behavior( { 'type': 'click_up',
                           'cbjs_action': '$("SPT_FONT_EXAMPLE").setStyle("display","none"); ' \
                                        '$("SPT_FONT_EXAMPLE_ITALIC").setStyle("display","none"); ' \
                                        '$("SPT_FONT_EXAMPLE_BOLD").setStyle("display","block"); ' \
                                        '$("SPT_FONT_EXAMPLE_BOLD_ITALIC").setStyle("display","none"); ' \
                                        '$("SPT_FONT_EXAMPLE_BTN").setStyle("background","#777777"); ' \
                                        '$("SPT_FONT_EXAMPLE_ITALIC_BTN").setStyle("background","#777777"); ' \
                                        '$("SPT_FONT_EXAMPLE_BOLD_BTN").setStyle("background","#CCCCCC"); ' \
                                        '$("SPT_FONT_EXAMPLE_BOLD_ITALIC_BTN").setStyle("background","#777777"); ' } )

        td = font_table.add_cell()
        td.add_styles( "border: 0px; border-collapse: collapse; padding: 0px; width: 6px; background: #CCCCCC;" )
        td.add( "&nbsp;" )

        td = font_table.add_cell()
        td.set_id("SPT_FONT_EXAMPLE_BOLD_ITALIC_BTN")
        td.add_styles( ft_style % "background: #777777;" )
        td.add( "<b><i>bold italic</i></b>" )
        td.add_behavior( { 'type': 'click_up',
                           'cbjs_action': '$("SPT_FONT_EXAMPLE").setStyle("display","none"); ' \
                                        '$("SPT_FONT_EXAMPLE_ITALIC").setStyle("display","none"); ' \
                                        '$("SPT_FONT_EXAMPLE_BOLD").setStyle("display","none"); ' \
                                        '$("SPT_FONT_EXAMPLE_BOLD_ITALIC").setStyle("display","block"); ' \
                                        '$("SPT_FONT_EXAMPLE_BTN").setStyle("background","#777777"); ' \
                                        '$("SPT_FONT_EXAMPLE_ITALIC_BTN").setStyle("background","#777777"); ' \
                                        '$("SPT_FONT_EXAMPLE_BOLD_BTN").setStyle("background","#777777"); ' \
                                        '$("SPT_FONT_EXAMPLE_BOLD_ITALIC_BTN").setStyle("background","#CCCCCC"); ' } )

        font_div.add( font_table )


        font_palettes = [ 'fnt_title_1', 'fnt_title_2', 'fnt_title_3', 'fnt_title_4', 'fnt_title_5',
                          'fnt_text', 'fnt_text_small', 'fnt_serif', 'fnt_code' ]

        font_modifiers = [ 'fnt_italic', 'fnt_bold', 'fnt_bold fnt_italic' ]

        font_example_div = DivWdg()
        font_example_div.set_id( "SPT_FONT_EXAMPLE" )
        for fnt_pal in font_palettes:
            font_palette_div = DivWdg()
            font_palette_div.add_looks( fnt_pal )
            font_palette_div.add_styles( "color: black; padding-top: 10px; padding-left: 10px;" )
            font_palette_div.add( 'Here is example TEXT showing text that is given font palette "' + fnt_pal + '"' )
            font_example_div.add( font_palette_div )
        font_div.add( font_example_div )

        for fnt_mod in font_modifiers:
            fm_name = fnt_mod.replace(" ","_")
            font_example_div = DivWdg()
            font_example_div.set_id( "SPT_FONT_EXAMPLE_%s" % fm_name.upper().replace("FNT_","") )
            font_example_div.add_styles( "display: none;" )
            for fnt_pal in font_palettes:
                font_palette_div = DivWdg()
                font_palette_div.add_looks( "%s %s" % (fnt_pal,fnt_mod) )
                font_palette_div.add_styles( "color: black; padding-top: 10px; padding-left: 10px;" )
                font_palette_div.add( 'Here is example TEXT showing text that is given font palette "' + fnt_pal + '"' )
                font_example_div.add( font_palette_div )
            font_div.add( font_example_div )

        font_div.add( '<br/><br/>' )
        return font_div


