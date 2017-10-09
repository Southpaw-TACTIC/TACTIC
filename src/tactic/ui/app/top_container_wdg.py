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
__all__ = ["TopContainerWdg"]


import types

from pyasm.common import Xml, Common, Config, Container, Environment
from pyasm.biz import Project
from pyasm.search import Search
from pyasm.web import DivWdg, WebEnvironment
from pyasm.widget import WidgetConfig, Error403Wdg

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.panel import CustomLayoutWdg


class TopContainerWdg(BaseRefreshWdg):

    def get_display(my):

        top = DivWdg()

        hash = my.kwargs.get("hash")
        pathname = my.kwargs.get("pathname")

        Container.put("url_hash", hash)

        security = Environment.get_security()
        is_admin = security.check_access("builtin", "view_site_admin", "allow")
        if hash == "/admin" and not is_admin:
            hash = "/index"

        if not hash:
            widget = my.get_default_wdg()
            top.add(widget)

        # This would provide a way to get the default index widget.
        #elif hash == "/projects":
        #    widget = my.get_default_wdg()
        #    from tactic_sites.default.modules import IndexWdg
        #    top.add( IndexWdg() )
        else:
            from tactic.ui.panel import HashPanelWdg

            project_code = Project.get_project_code()
            if project_code == 'admin' and hash == '/index':
                widget = my.get_default_wdg()

            else:
                from pyasm.security import Site
                widget = HashPanelWdg.get_widget_from_hash(hash, return_none=True)

            if not widget:
                if hash == "/index":
                    widget = my.get_default_wdg()
                elif hash == '/admin':
                    widget = my.get_default_wdg()
                else:
                    widget = HashPanelWdg.get_widget_from_hash("/index", return_none=True)


            top.add(widget)


        return top



    def get_default_wdg(my):
        top_class_name = WebEnvironment.get_top_class_name()
        kwargs = {}
        widget = Common.create_from_class_path(top_class_name, [], kwargs) 
        return widget


