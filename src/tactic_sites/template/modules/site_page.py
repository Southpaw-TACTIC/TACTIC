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

__all__ = ["SitePage", "SiteXMLRPC"]

from pyasm.prod.service import *

from pyasm.search import SearchType
from pyasm.web import WebContainer, AppServer


class SitePage(AppServer):

    def set_templates(self):
        context = WebContainer.get_web().get_full_context_name()
        SearchType.set_global_template("project", context)



class SiteXMLRPC(BaseXMLRPC):
    def set_templates(self):
        context = WebContainer.get_web().get_full_context_name()
        SearchType.set_global_template("project", context)
