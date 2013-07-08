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

__all__ = ['UploadServer']


from pyasm.web import AppServer
from pyasm.widget import UploadServerWdg

# get the import to this project's modules
from pyasm.web import get_site_import
exec( get_site_import(__file__) )


class UploadServer(AppServer):

    def get_page_widget(my):
        return UploadServerWdg()




