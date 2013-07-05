###########################################################
#
# Copyright (c) 2005, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
# AUTHOR:
#     Remko Noteboom
#
#

from pyasm.web import Widget, WebContainer, HtmlElement
from pyasm.widget import UndoButtonWdg, RedoButtonWdg, IconRefreshWdg
from pyasm.admin import *

from header_wdg import *
from main_tab_wdg import *


class BaseIndexWdg(Widget):

    def init(my):

        web = WebContainer.get_web()

        my.add(HeaderWdg())

        undo_redo = HtmlElement.span()
        undo_redo.add_style("float", "right")
        undo_redo.add_style("margin", "5px 5px")
        undo_redo.add(UndoButtonWdg())
        undo_redo.add(RedoButtonWdg())
        undo_redo.add(IconRefreshWdg())

        my.add_widget( undo_redo )

        tab = MainTabWdg()
        my.add(tab)




