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

from pyasm.web import AppServer

# get the import to this project's modules
from pyasm.web import get_site_import
exec( get_site_import(__file__) )

class Index(AppServer):

    def get_page_widget(my):
        return IndexWdg()

    def get_top_wdg(my):
        from tactic.ui.app import TopWdg
        my.top = TopWdg()
        body = my.top.get_body()
        body.add_class("body_login")
        return my.top

