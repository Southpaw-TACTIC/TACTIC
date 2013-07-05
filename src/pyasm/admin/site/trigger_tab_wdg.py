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

__all__ = ["TriggerTabWdg"]

from pyasm.web import Widget
from pyasm.widget import TabWdg, TableWdg, SObjectGroupWdg
from pyasm.admin import *
from pyasm.biz import Notification, GroupNotification, TriggerSObj, \
    CommandSObj, TriggerInCommand



class TriggerTabWdg(Widget):

    def init(my):
        tab = TabWdg(css=TabWdg.SMALL)
        tab.set_tab_key("trigger_tab")
        my.handle_tab(tab)
        my.add(tab)


    def handle_tab(my, tab):
        tab.add( CommandWdg, "Commands" )
        tab.add( TriggerWdg, "Triggers" )
        tab.add( my.get_trigger_in_command_wdg, "Command Triggers")


    def get_trigger_in_command_wdg(my):
       return SObjectGroupWdg(Trigger, CommandSObj, TriggerInCommand)


