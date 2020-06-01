###########################################################
#
# Copyright (c) 2020, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#
from pyasm.web import DivWdg, HtmlElement
from pyasm.biz import Project, ProjectSetting
from pyasm.search import Search
from pyasm.common import Environment
from pyasm.web import DivWdg

from tactic.ui.bootstrap_app import BootstrapIndexWdg, BootstrapTopNavWdg



__all__ = ['VFXIndexWdg', 'VFXTopNavWdg']

class VFXIndexWdg(BootstrapIndexWdg):

    def _get_tab_save_state(self):
        return "vfx_main_body_tab_state"

    def _get_top_nav_xml(self):

        class_name = 'TACTIC.vfx.VFXTopNavWdg'

        return """
            <element name="top_nav">
              <display class="%s">
              </display>
            </element>""" % class_name


class VFXTopNavWdg(BootstrapTopNavWdg):
   
    def get_logo_div(self):

        div = super(VFXTopNavWdg, self).get_logo_div()

        div.add(''' <div style="margin-left: 10px; font-size: 22px")>VFX</div>''')

        return div
