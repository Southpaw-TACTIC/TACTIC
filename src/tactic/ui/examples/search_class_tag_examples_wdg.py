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
__all__ = ["SearchClassTagExamplesWdg"]

from pyasm.web import DivWdg

from tactic.ui.container import PopupWdg

from base_example_wdg import BaseExampleWdg


class SearchClassTagExamplesWdg(BaseExampleWdg):

    def get_example_title(self):
        return "Javascript Search Clas Tag Examples"


    def get_example_description(self):
        return "These are a number of examples showing how to use the numerous 'spt.' convenience wrappers " \
                "that provide functionality for searching for elements by class tag."


    def get_example_display(self):

        div = DivWdg()
        div.add_class("SPT_SEARCH_CLASS_TAG_EXAMPLE")

        div.add( "<br/><br/>" )

        tt_div = DivWdg()
        tt_div.add_styles("padding: 4px; width: 250px; text-align: center; border: 1px solid white;")
        tt_div.add("DIV in page with class 'SPT_FIND_ME_DIV'")
        tt_div.add_class( "SPT_FIND_ME_DIV" )

        tt_popup = PopupWdg( id="test_popup", allow_page_activity=True, width="600px" )
        tt_popup.add_title("Test Popup")

        tt_div_p = DivWdg()
        tt_div_p.add_class("SPT_FIND_ME_POPUP")
        tt_div_p.add( "DIV in POPUP with class 'SPT_FIND_ME_POPUP'" )

        tt_btn_p = DivWdg()
        tt_btn_p.add_styles( "border: solid 1px white; padding: 4px; width: 200px; text-align: center; cursor: pointer;" )
        tt_btn_p.add( "find 'SPT_FIND_ME_DIV'" )
        tt_btn_p.add_behavior( { 'type': 'click_up',
                                 'cbjs_action': 'var tmp_el = spt.get_cousin( bvr.src_el, ' \
                                                 '".SPT_SEARCH_CLASS_TAG_EXAMPLE", ".SPT_FIND_ME_DIV", [] ); ' \
                                                 'spt.ui_play.set_bg_to_next_basic_color( tmp_el ); '
                                                 } )

        tt_popup.add( tt_div_p )

        tt_popup.add( "<br/><br/>" )
        tt_popup.add( tt_btn_p )

        tt_div.add( tt_popup )
        div.add( tt_div )
        div.add( "<br/><br/>" )


        tt_div2 = DivWdg()
        tt_div2.add_styles( "border: solid 1px white; padding: 4px; width: 100px; text-align: center; cursor: pointer;" )
        tt_div2.add( "launch popup" )
        tt_div2.add_behavior( { 'type': 'click_up', 'cbjs_action': 'spt.popup.open( "%s" );' % 'test_popup' } )

        div.add( tt_div2 )
        div.add( "<br/><br/>" )


        tt_div3 = DivWdg()
        tt_div3.add_styles( "border: solid 1px white; padding: 4px; width: 100px; text-align: center; cursor: pointer;" )
        tt_div3.add( "find in popup" )
        tt_div3.add_behavior( { 'type': 'click_up',
                                'cbjs_action': 'var tmp_el = spt.get_cousin( bvr.src_el, ' \
                                                '".SPT_SEARCH_CLASS_TAG_EXAMPLE", ".SPT_FIND_ME_POPUP", [] ); ' \
                                                'spt.ui_play.set_bg_to_next_basic_color( tmp_el ); '
                                                } )

        div.add( tt_div3 )

        div.add( "<br/><br/>" )

        return div


