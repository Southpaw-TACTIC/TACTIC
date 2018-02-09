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

__all__ = ['WidgetAppServer']

# DEPRECATED

import cStringIO, os, re

from pyasm.common import Container
from web_container import WebContainer
from app_server import BaseAppServer

class AppServerException(Exception):
    pass


class WidgetAppServer(BaseAppServer):
    '''A simple application server without security restrictions.'''
    def _get_display(self):
        web = WebContainer.get_web()
        web.set_form_value("ajax", "true")

        return super(WidgetAppServer, self)._get_display()




