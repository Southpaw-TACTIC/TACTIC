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

__all__ = ['Config']

from pyasm.web import AppServer

from pyasm.search import Search
from pyasm.web import DivWdg, Widget, HtmlElement

from tactic.ui.startup import DbConfigWdg

# get the import to this project's modules
from pyasm.web import get_site_import
exec( get_site_import(__file__) )

class Config(AppServer):

    def get_page_widget(my):

        div = DivWdg()

        from tactic.ui.app import PageHeaderWdg
        div.add(PageHeaderWdg())

        search = Search("sthpw/login")
        sobjects = search.get_sobjects()

        config_wdg = DbConfigWdg()
        div.add(config_wdg)



        return div


