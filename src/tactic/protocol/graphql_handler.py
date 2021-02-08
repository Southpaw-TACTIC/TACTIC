###########################################################
#
# Copyright (c) 2021, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#

__all__ = ['BaseGraphQLHandler']

from pyasm.common import jsonloads
from tactic.ui.common import BaseRefreshWdg

import re

class BaseGraphQLHandler(BaseRefreshWdg):

    def get_display(self):

        method = self.kwargs.get("Method")
        if not method:
            raise Exception("No method specified")

        if method == "GET":
            ret_val = self.GET()
        elif method == "POST":
            ret_val = self.POST()
        elif method == "PUT":
            ret_val = self.PUT()
        elif method == "DELETE":
            ret_val = self.PUT()
        else:
            ret_val = self.GET()

        return ret_val



    def GET(self):
        pass

    def POST(self):
        return self.GET()

    def PUT(self):
        pass

    def DELETE(self):
        pass

