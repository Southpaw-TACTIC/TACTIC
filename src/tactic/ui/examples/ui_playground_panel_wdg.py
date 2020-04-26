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
__all__ = ["UiPlaygroundPanelWdg"]

import os, types

from pyasm.common import Xml, Common
from pyasm.search import Search
from pyasm.web import DivWdg, HtmlElement, SpanWdg, Table, WebContainer
from pyasm.widget import SelectWdg, WidgetConfig, IconWdg

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.container import ContextMenuWdg, DropdownMenuWdg, SubMenuWdg, PopupWdg
from tactic.ui.examples import *


class UiPlaygroundPanelWdg(BaseRefreshWdg):

    '''Panel to test out UI widget prototypes'''

    def get_args_keys(self):
        return {'get_example_chooser': 'if "true" then return example chooser content and not playground panel'}


    def init(self):
        self.get_example_chooser = self.kwargs.get('get_example_chooser')


    def _get_example_widget_classes(self):
        return [
            EfficientTableExampleWdg,
            SearchClassTagExamplesWdg,
            KeyboardHandlerExampleWdg,
            FontPalettesExampleWdg,
            AllMenuExamplesWdg,
            SptFxSliderExampleWdg,
            BehaviorHandoffExampleWdg,
            DomEventListenExampleWdg,
            NamedEventListenExampleWdg,
            PanningScrollExampleWdg,
            ClientSideAddBehaviorExampleWdg,
            DevSandbox01Wdg,
            DevSandbox02Wdg,
            DevSandbox03Wdg
        ]


    def get_display(self):

        if self.get_example_chooser == 'true':
            return self.get_example_chooser_content()

        div = DivWdg()
        div.set_id("UiPlaygroundPanelWdg")

        title = "UI Playground"
        title_wdg = DivWdg()
        title_wdg.add_looks("fnt_title_2")
        title_wdg.add(title)
        div.add(title_wdg)

        div.add(HtmlElement.hr())

        div.add( '<br/>' )
        click_chooser = DivWdg()
        click_chooser.add_looks("fnt_text")
        click_chooser.add( " UI Examples List Popup" )
        click_chooser.add_class("SPT_DTS")
        click_chooser.add_styles("cursor: pointer; padding: 6px; width: 130px; background-color: black;")

        click_chooser.add_behavior( {'type': 'click_up',
                                     'cbfn_action': 'spt.popup.get_widget',
                                     'options': { 'title': 'TACTIC&trade; UI Examples',
                                                  'width': '400px',
                                                  'popup_id': 'UiExamplesChooserPopup',
                                                  'popup_parent_id': 'UiPlaygroundPanelWdg',
                                                  'class_name': 'tactic.ui.panel.ui_playground_panel_wdg.' \
                                                                'UiPlaygroundPanelWdg'
                                                  },
                                     'args': { 'get_example_chooser': 'true' }
                                     } )


        div.add( click_chooser )
        div.add( '<br/>' )

        example_display_div = DivWdg()
        example_display_div.add_styles( "padding: 10px;" )
        example_display_div.set_id("UiExampleDisplayDiv")

        div.add( example_display_div )

        div.add( '<br/>' )
        div.add( '<br/>' )

        return div


    def get_example_chooser_content(self):
        choice_list_div = DivWdg()
        choice_list_div.set_id("UiExampleChoiceList")
        choice_list_div.add_styles( "background: #202020; color: #999999; border: 1px solid black; " \
                                    "border-top: 0px;" )

        example_wdg_classes = self._get_example_widget_classes()

        choice_list_div.add( "<br/>" )

        for ex_wdg_class in example_wdg_classes:
            ex_wdg = ex_wdg_class()

            ex_title = ex_wdg.get_example_title()
            ex_desc  = ex_wdg.get_example_description()
            ex_class_path = Common.get_full_class_name( ex_wdg )

            ex_div = DivWdg()
            ex_div.add_styles( "color: #999999; padding: 8px; padding-left: 20px; cursor: pointer;" )
            ex_div.add_class("SPT_DTS")
            ex_div.add_behavior( {'type': 'click_up',
                                  'cbjs_action': 'spt.ui_play.show_example("%s");' % ex_class_path } )
            ex_div.add( ex_title )
            choice_list_div.add( ex_div )

        choice_list_div.add( "<br/>" )
        return choice_list_div


