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
__all__ = ['IndexWdg']

from pyasm.web import *
from pyasm.widget import *
from pyasm.biz import Project
from pyasm.flash.widget import *
from pyasm.flash.site import MainTabWdg
from pyasm.search import *

class IndexWdg(Widget):
    
    def init(my):
        project_name =  Project.get_project_name()
        exec("from sites.%s.modules import HeaderWdg" % project_name, \
            globals(), locals())

        my.add( HeaderWdg() )

        undo_redo = SpanWdg()
        undo_redo.set_style("float: right")
        undo_redo.add_style("margin", "5px 5px")
        undo_redo.add(UndoButtonWdg())
        undo_redo.add(RedoButtonWdg())
        undo_redo.add(IconRefreshWdg())
        undo_redo.add(HelpMenuWdg()) 

        my.add( undo_redo )

        tab = MainTabWdg()

        my.add(tab)



