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

__all__ = ['TitleWdg']

from pyasm.common import Environment
from tactic.ui.common import BaseRefreshWdg
from pyasm.web import DivWdg 

class TitleWdg(BaseRefreshWdg):

    def __init__(self, **kwargs):

        self.kwargs = kwargs
        self.name_of_title = kwargs.get("name_of_title")
        if not self.name_of_title:
            self.name_of_title = '&nbsp'

        self.help_alias = kwargs.get("help_alias")
        if not self.help_alias:
            self.help_alias = 'main'

    def get_display(self):

        title = DivWdg()
        title.add(self.name_of_title)

        title.add_style("padding: 5px")
        title.add_style("margin: -10px -10px 10px -10px")
        title.add_style("font-weight: bold")
        title.add_style("font-size: 14px")
        #title.add_gradient("background", "background", -10)
        title.add_color("background", "background", -3)
        title.add_color("color", "color", -10)
        if self.help_alias:
            title.add_style('height: 20px')
        title.add_border()

        from tactic.ui.app import HelpButtonWdg
        help_wdg = HelpButtonWdg(alias=self.help_alias)

        help_wdg.add_style("float: right")
        help_wdg.add_style("margin-top: -5px")
        title.add(help_wdg)
        return title 
