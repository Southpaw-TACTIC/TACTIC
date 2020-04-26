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
from pyasm.prod.service import BaseSthpwWdg

# get the import to this project's modules
from pyasm.web import get_site_import
exec( get_site_import(__file__) )


class WidgetServer(AppServer):
    '''wrapper class to load in Widgets dynamically'''

    def get_page_widget(self):
        return BaseSthpwWdg()



