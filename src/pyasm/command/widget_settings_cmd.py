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

__all__ = ["WidgetSettingsCmd"]

from command import *

class WidgetSettingsCmd(Command):

    def __init__(my, key=None, widget_name=None, value=None):
        super(WidgetSettingsCmd,my).__init__()
        #my.search_type = "sthpw/wdg_settings"
        my.key = key
        my.widget_name = widget_name
        my.value = value

    def is_undoable(cls):
        return False
    is_undoable = classmethod(is_undoable)


    def set_key(my, key):
        my.key = key
        
    def set_widget_name(my, widget_name):
        my.widget_name = widget_name

    def set_value(my, value):
        my.value = value

    def get_title(my):
        return "Widget Settings"

    def check(my):
        if my.key and my.widget_name and my.value:
            return True
        
    def execute(my):
       
        settings_key = "%s|%s" % (my.key, my.widget_name)
     
        from pyasm.web import WidgetSettings
        settings = WidgetSettings.get_by_key(settings_key)
        if not settings:
            return
        my.description = "Widget settings '%s'='%s'" % (settings_key, my.value)
     
        if settings.get_value("data") != my.value:
            settings.set_value("data", my.value)
            settings.commit()
        
    def check_security(my):
        '''give the command a callback that allows it to check security'''
        return True



