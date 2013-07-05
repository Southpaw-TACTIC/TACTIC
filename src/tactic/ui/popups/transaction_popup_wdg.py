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
__all__ = ["TransactionPopupWdg"]


from pyasm.common import Environment, Config
from pyasm.biz import Project
from pyasm.web import *

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.container import PopupWdg
#from tactic.ui.activator import ButtonForDropdownMenuWdg

from pyasm.admin import UndoLogWdg
from pyasm.widget import IconWdg
from tactic.ui.widget import TextBtnSetWdg, ActionButtonWdg, ButtonNewWdg, ButtonRowWdg

import datetime

class TransactionPopupWdg(BaseRefreshWdg):

    def init(my):
        pass


    def get_args_keys(my):
        return {
        }

    def get_buttons(my):
        button_div = DivWdg()


        button_row = ButtonRowWdg()
        button_div.add(button_row)
        button_row.add_style("float: left")
        button_row.add_style("padding-top: 5px")
        button_row.add_style("padding-bottom: 3px")
        button_row.add_style("padding-right: 5px")
        button_row.add_style("padding-left: 5px")

        button = ButtonNewWdg(title="Refresh", icon=IconWdg.REFRESH)
        button_row.add(button)
        button.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            spt.app_busy.show("Refreshing");
            var top = bvr.src_el.getParent(".spt_undo_log_top");
            spt.panel.refresh(top)
            spt.app_busy.hide();
            '''
        } )


        button = ButtonNewWdg(title="Undo the last transaction", icon=IconWdg.UNDO)
        button_row.add(button)
        button.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            spt.undo_cbk(evt, bvr);
            spt.panel.refresh('UndoLogWdg');
            '''
        } )



        button = ButtonNewWdg(title="Redo the last transaction", icon=IconWdg.REDO)
        button_row.add(button)
        button.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            spt.redo_cbk(evt, bvr);
            spt.panel.refresh('UndoLogWdg');
            '''
        } )


        return button_div


    def get_display(my):
        content_div = DivWdg()
        my.set_as_panel(content_div)
        content_div.add_class("spt_undo_log_top")
        content_div.add_style("width: 800px")

 
        from tactic.ui.app import HelpButtonWdg
        help_button = HelpButtonWdg(alias="tactic-undo")
        content_div.add(help_button)
        help_button.add_style("float: right")
        help_button.add_style("margin-top: 5px")
        help_button.add_style("margin-right: 5px")


        buttons = content_div.add(my.get_buttons())
        content_div.add(buttons)

        undo_wdg = UndoLogWdg()
        undo_wdg.set_id('UndoLogWdg')
        content_div.add(undo_wdg)

        return content_div





