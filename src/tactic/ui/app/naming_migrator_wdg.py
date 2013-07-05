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

__all__ = ['NamingMigratorCmd']

from pyasm.common import Environment, Common
from pyasm.web import DivWdg, HtmlElement, SpanWdg, Table, Widget
from pyasm.widget import TextAreaWdg, ButtonWdg, TextWdg, HiddenWdg, ProdIconButtonWdg

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.container import PopupWdg

import os

class NamingMigratorWdg(BaseRefreshWdg):
    '''This is the ui to the NamingMigrator command which migrates a set of
    snapshots from the old path to a new path as specified by the current
    naming'''


    def get_display(my):
        top = DivWdg()
        my.set_as_panel(top)

        top.add("Search Type: ")
        search_type_text = TextWdg("search_type")
        top.add(search_type_text)

        test_button = ProdIconButtonWdg("Test")
        top.add(test_button)
        test_button.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_panel");
            var values = spt.api.get_input_values(top, null, false);
            var search_type = values['search_type'][0];
            cmd = 'tactic.command.NamingMigratorCmd';
            server = TacticServerStub.get();
            server.execute_cmd(cmd, values)
            '''
        } )

        return top



