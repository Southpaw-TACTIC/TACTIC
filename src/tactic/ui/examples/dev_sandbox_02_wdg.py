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
__all__ = ["DevSandbox02Wdg"]

from pyasm.web import DivWdg, HtmlElement, SpanWdg, Table, WebContainer
from pyasm.widget import SelectWdg, WidgetConfig, IconWdg

from base_example_wdg import BaseExampleWdg


class DevSandbox02Wdg(BaseExampleWdg):

    def get_example_title(self):
        # UI prototype sandbox for Boris
        return "::: Developer UI Sandbox 02 - Boris :::"


    def get_example_description(self):
        return "This is a prototyping and testing sandbox widget container (#2) for Boris."


    def get_example_display(self):

        div = DivWdg(id="big_box")

        div.add_styles("background: black; padding: 10px; width: 400px;")
        div.add( "Sandbox for Boris -- replace contents here with own UI prototypes and tests." )

        from pyasm.prod.web import ProcessSelectWdg
        context_select = ProcessSelectWdg( has_empty=False,\
                search_type='prod/asset')
        context_select.set_name('sample_context')
        div.add(context_select)
        return div


