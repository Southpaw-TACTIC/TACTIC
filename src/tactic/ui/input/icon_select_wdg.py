###########################################################
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
__all__ = ["IconSelectWdg"]

import os, types
import math

from pyasm.web import DivWdg, HtmlElement
from pyasm.widget import HiddenWdg, TextWdg, BaseInputWdg, IconWdg
from tactic.ui.widget import TextBtnWdg, TextBtnSetWdg, IconChooserWdg, ActionButtonWdg

class IconSelectWdg(BaseInputWdg):

    def get_display(my):
        my.icon_string = my.get_value("icon")
        my.icon_label = my.get_value("label")

        top = DivWdg()
        top.add_class("spt_icon_chooser_top")

        # FIXME: this is being generated every time .... where to put is?
        icon_chooser = IconChooserWdg( is_popup=True )
        top.add( icon_chooser )

        icon_entry_text = TextWdg(my.get_input_name())
        icon_entry_text.set_option("size", "30")
        #icon_entry_text.set_attr("disabled", "disabled")
        icon_entry_text.add_class( "SPT_ICON_ENTRY_TEXT" )


        button = ActionButtonWdg(title='Choose', tip='Click to select an icon')

        icon_img = HtmlElement.img()
        icon_img.add_class( "SPT_ICON_IMG" )

        if my.icon_string:
            # icon_path = IconWdg.icons.get(my.icon_string)
            icon_path = IconWdg.get_icon_path(my.icon_string)
            if icon_path:
                # icon = IconWdg( my.icon_string, icon_path, right_margin='0px' )
                icon_img.set_attr("src", icon_path)
            else:
                icon_img.set_attr("src", IconWdg.get_icon_path("TRANSPARENT"))

            icon_entry_text.set_value( my.icon_string )
        else:
            icon_entry_text.set_value( "" )
            icon_img.set_attr("src", IconWdg.get_icon_path("TRANSPARENT"))


        named_event_name = "ICON_CHOOSER_SELECTION_MADE"
        icon_entry_text.add_behavior( {'type': 'listen', 'event_name': named_event_name,
           'cbjs_action': '''
                var top = $("IconChooserPopup");
                var chooser = spt.get_element(top, ".SPT_ICON_CHOOSER_WRAPPER_DIV");
                //var chooser = spt.get_cousin( bvr.src_el,
                //    ".spt_icon_chooser_top", ".SPT_ICON_CHOOSER_WRAPPER_DIV" );

                var icon_name = chooser.getProperty("spt_icon_selected");
                var icon_path = chooser.getProperty("spt_icon_path");
                // bvr.src_el.innerHTML = icon_name;
                bvr.src_el.value = icon_name;
                if( spt.is_hidden( bvr.src_el ) ) { spt.show( bvr.src_el ); }
                var img_el = spt.get_cousin( bvr.src_el,
                    ".spt_icon_chooser_top", ".SPT_ICON_IMG" );
                if( icon_path ) {
                    img_el.setProperty("src", icon_path);
                } else {
                    img_el.setProperty("src","/context/icons/common/transparent_pixel.gif");
                }
           ''' } )

        top.add_behavior( {'type': 'click_up', 'cbjs_action': 'spt.popup.open( "IconChooserPopup", false);' } )

        #top.add( my.icon_label )
        spacing = "<img src='%s' style='width: %spx;' />" % (IconWdg.get_icon_path("TRANSPARENT"), 3)

        #button.add_behavior( {'type': 'click_up', 'cbjs_action': 'spt.popup.open( "IconChooserPopup", false);' } )
        #top.add( button )
        #button.add_style("float: right")
        #button.add_style("margin-top: -3px")

        top.add( icon_img )
        top.add( spacing )
        top.add( icon_entry_text )



        return top


