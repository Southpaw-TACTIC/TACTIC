###########################################################
#
# Copyright (c) 2005-2008, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#

__all__ = ['LoaderButtonWdg']


from pyasm.web import Widget, DivWdg, FloatDivWdg
from pyasm.widget import TextWdg

from tactic.ui.container import SmartMenu
from tactic.ui.widget import TextOptionBtnWdg


class LoaderButtonWdg(Widget):

    LOAD_BUTTON_ID = "load_id"

    def init(my):
        my.load_script = ""
        my.smart_menu_data = None

    def set_load_script(my, load_script):
        my.load_script = load_script

    def set_smart_menu(my, data):
        my.smart_menu_data = data

    def get_display(my):
        assert my.load_script

        widget = DivWdg()
        widget.add_style('float', 'right')

        load_button = TextOptionBtnWdg(label='   Load   ', size='medium')
        load_button.get_top_el().add_style('float', 'left')
        load_button.get_top_el().set_id(my.LOAD_BUTTON_ID)
        load_button.add_behavior(
                {'type': "click_up",
                "cbjs_action":
                "setTimeout(function() {%s}, 200) "% my.load_script
                })
        widget.add(load_button)
        arrow_button = load_button.get_option_widget()
        #widget.add(arrow_button)
        suffix = "ASSET_LOADER_FUNCTIONS"
        menus_in = [ my.smart_menu_data ]


        SmartMenu.add_smart_menu_set( arrow_button,  menus_in)
        SmartMenu.assign_as_local_activator(arrow_button, None, True)

        #SmartMenu.attach_smart_context_menu( load_button, menus_in, False )
        x_div = FloatDivWdg("x")
        x_div.add_color('color','color')
        x_div.add_style('margin-right: 6px')
        widget.add(x_div)
        multiplier = TextWdg()
        multiplier.set_id("load_multiplier")
        multiplier.set_option("size", "1.5")
        multiplier.add_style("font-size: 0.8em")
        multiplier.add_style("float: left")
        multiplier.add_class("load_multiplier")
        widget.add( multiplier )
        return widget

