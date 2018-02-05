###########################################################
#
# Copyright (c) 2005-2008, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#

__all__ = ['ProxyWdg']

from tactic_client_lib import TacticServerStub

from tactic.ui.common import BaseRefreshWdg

class ProxyWdg(BaseRefreshWdg):

    def get_display(self):

        class_name = self.kwargs.get("class_name")
        server_name = self.kwargs.get("server")
        kwargs = self.kwargs.get("kwargs")

        server = TacticServerStub.get(protocol='xmlrpc')
        server.set_server(server_name)
        widget = server.get_widget(class_name, kwargs)
        return widget








