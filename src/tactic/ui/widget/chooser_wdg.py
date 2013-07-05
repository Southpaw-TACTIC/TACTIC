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
__all__ = ["IconChooserWdg"]

import os, types
import math

from pyasm.web import DivWdg, HtmlElement, SpanWdg, Table, WebContainer
from pyasm.widget import IconWdg

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.container import PopupWdg, RoundedCornerDivWdg



class IconChooserWdg(BaseRefreshWdg):

    '''Tool for choosing a single Icon from set of TACTIC icons'''

    def get_args_keys(my):
        return {
            'is_popup': 'if "true" then return as a full popup, otherwise return inner div'
        }


    def init(my):
        is_popup = my.kwargs.get('is_popup')
        if is_popup in [ 1, True, 'true', 'TRUE', 'True' ]:
            my.is_popup = True
        else:
            my.is_popup = False


    def get_display(my):

        if my.is_popup:
            icon_chooser_popup_id = "IconChooserPopup"
            icon_chooser_popup = PopupWdg(id=icon_chooser_popup_id, allow_page_activity=False, width="760px")
            icon_chooser_popup.add("Icon Chooser", "title")

        orig_icon_list = IconWdg.icons.keys()
        icon_list = ['-- No Icon --']
        do_not_list = [ 'MAYA', 'HOUDINI', 'PROGRESS', 'CLIP_PLAY', 'XSI', 'CLIP_PAUSE', 'CHECK_OUT_LG','CHECK_OUT','PUBLISH_LG' ]

        for k in orig_icon_list:
            if k in do_not_list:
                continue
            icon_list.append(k)

        icon_list.sort()
        icon_list_len = float(len(icon_list))

        num_cols = 5
        num_rows = int( math.ceil( icon_list_len / float(num_cols) ) )

        chooser_wrapper_div = DivWdg()
        chooser_wrapper_div.add_class( "SPT_ICON_CHOOSER_WRAPPER_DIV" )

        chooser_bkg_rc = RoundedCornerDivWdg(hex_color_code="949494",corner_size="10")
        chooser_bkg_rc.set_dimensions( width_str='740px', content_height_str='520px' )

        table = Table()
        for r in range(num_rows):
            table.add_row()
            for c in range(num_cols):
                td = table.add_cell()
                td.add_styles("color: black; overflow: hidden; width: 140px; max-width: 140px; height: 20px;")
                td.add_styles("border: 1px solid transparent; cursor: pointer;")
                td.add_behavior( {'type': 'hover', 'mod_styles': 'background-color: #555555;'} )

                if c > 0:
                    td.add_styles("border-left-color: black;")

                idx = int( c * num_rows + r )
                if idx < icon_list_len:
                    icon_name = icon_list[ idx ]
                    icon_path = ''
                    if icon_name != '-- No Icon --':
                        icon_path = IconWdg.get_icon_path(icon_name)
                        icon = IconWdg( icon_name, icon_path )
                        td.add(icon)
                    text_span = SpanWdg()
                    text_span.add_looks( "fnt_code" )
                    text_span.add_styles( "font-size: 10px" )
                    if len(icon_name) > 16:
                        text_span.add( "%s..." % icon_name[:15] )
                    else:
                        text_span.add( icon_name )
                    td.add( text_span )
                    if icon_name == '-- No Icon --':
                        icon_name = ''
                    td.add_class( "SPT_ICON_SELECT_%s" % icon_name )
                    if my.is_popup:
                        cbjs_action = '''
                            var cwd = bvr.src_el.getParent(".SPT_ICON_CHOOSER_WRAPPER_DIV");
                            cwd.setProperty("spt_icon_selected", "%s");
                            cwd.setProperty("spt_icon_path", "%s");
                            spt.popup.close( spt.popup.get_popup( bvr.src_el ) );
                            spt.named_events.fire_event("%s",bvr);
                        ''' % (icon_name, icon_path,"ICON_CHOOSER_SELECTION_MADE")
                    else:
                        cbjs_action = '''
                            var cwd = bvr.src_el.getParent(".SPT_ICON_CHOOSER_WRAPPER_DIV");
                            cwd.setProperty("spt_icon_selected", "%s");
                            cwd.setProperty("spt_icon_path", "%s");
                            spt.hide( cwd );
                            spt.named_events.fire_event("%s",bvr);
                        ''' % (icon_name, icon_path,"ICON_CHOOSER_SELECTION_MADE")
                        pass
                    td.add_behavior( {'type': 'click_up', 'cbjs_action': cbjs_action} )

        chooser_bkg_rc.add( table )
        chooser_wrapper_div.add( chooser_bkg_rc )


        if my.is_popup:
            icon_chooser_popup.add(chooser_wrapper_div, "content")
            return icon_chooser_popup


        return div


