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

from pyasm.web import *

# get the import to this project's modules
from pyasm.web import get_site_import
exec( get_site_import(__file__) )

from pyasm.prod.site import MayaTabWdg
from pyasm.widget import HeaderWdg



class Maya(SitePage):

    def get_page_widget(self):
        return MayaPage()


class MayaPage(Widget):

    def init(self):
        self.add( HeaderWdg() )
        self.add( MayaTabWdg() )
