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
__all__ = ["DevSandbox01Wdg"]

from pyasm.web import DivWdg, HtmlElement, SpanWdg, Table, WebContainer
from pyasm.widget import SelectWdg, WidgetConfig, IconWdg

from base_example_wdg import BaseExampleWdg


class DevSandbox01Wdg(BaseExampleWdg):

    def get_example_title(my):
        # UI prototype sandbox for Remko
        return "::: Developer UI Sandbox 01 - Remko :::"


    def get_example_description(my):
        return "This is a prototyping and testing sandbox widget container (#1) for Remko."


    def get_example_display(my):

        div = DivWdg()

        div.add_styles("background: black; padding: 10px; width: 400px;")
        div.add( "Sandbox for Remko -- replace contents here with own UI prototypes and tests." )

        return div


