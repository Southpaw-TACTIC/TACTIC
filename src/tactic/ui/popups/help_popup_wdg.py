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
__all__ = ["HelpPopupWdg"]

from pyasm.web import *

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.container import PopupWdg
from tactic.ui.activator import ButtonForDropdownMenuWdg

from pyasm.widget import ButtonWdg


class HelpPopupWdg(BaseRefreshWdg):

    def init(self):
        pass


    def get_args_keys(self):
        return {
        }


    def get_display(self):
        popup = PopupWdg( id="HelpPopupWdg", allow_page_activity=True, width="600px" )
        popup.add("TACTIC&trade; Help", "title")

        content_div = DivWdg()

        inner_div = DivWdg()
        inner_div.set_style("background: #2f2f2f; color: #000000; border: 1px solid #000000; padding: 2px;")

        # TEMP ...
        inner_div.add( "Under Construction!" );

        # Finished generating tools for Action Bar ...
        content_div.add(inner_div)

        popup.add(content_div, 'content')
        return popup


