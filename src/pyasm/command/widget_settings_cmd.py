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

    def __init__(self, key=None, widget_name=None, value=None):
        super(WidgetSettingsCmd,self).__init__()
        #self.search_type = "sthpw/wdg_settings"
        self.key = key
        self.widget_name = widget_name
        self.value = value

    def is_undoable(cls):
        return False
    is_undoable = classmethod(is_undoable)


    def set_key(self, key):
        self.key = key
        
    def set_widget_name(self, widget_name):
        self.widget_name = widget_name

    def set_value(self, value):
        self.value = value

    def get_title(self):
        return "Widget Settings"

    def check(self):
        if self.key and self.widget_name and self.value:
            return True
        
    def execute(self):
       
        settings_key = "%s|%s" % (self.key, self.widget_name)
     
        from pyasm.web import WidgetSettings
        settings = WidgetSettings.get_by_key(settings_key)
        if not settings:
            return
        self.description = "Widget settings '%s'='%s'" % (settings_key, self.value)
     
        if settings.get_value("data") != self.value:
            settings.set_value("data", self.value)
            settings.commit()
        
    def check_security(self):
        '''give the command a callback that allows it to check security'''
        return True



