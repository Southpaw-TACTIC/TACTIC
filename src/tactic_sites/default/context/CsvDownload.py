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

__all__ = ['CsvDownload']


from pyasm.web import AppServer
from pyasm.widget import UploadServerWdg

# get the import to this project's modules
from pyasm.web import get_site_import
exec( get_site_import(__file__) )


class CsvDownload(AppServer):

    def get_page_widget(self):
        #import cherrypy
        #print "heaaders: ", cherrypy.response.headers
        return "wowowo"




