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

__all__ = ["BaseSthpwWdg"]

from pyasm.common import *
from pyasm.biz import Project
from pyasm.web import *
from pyasm.widget import CmdReportWdg


class BaseSthpwWdg(Widget):
    '''This is actually the widget server ... named a long time ago'''

    def init(self):
        
        web = WebContainer.get_web()

        project_code = web.get_form_value("project")
        if project_code:
            Project.set_project(project_code)

        method = web.get_form_value("method")
        widget_class = web.get_form_value("widget")
        if widget_class == "":
            return
       
        arg_type = web.get_form_value("arg_type")
        if arg_type == "dict" and not method:
            args = web.get_form_args()
            exec(Common.get_import_from_class_path(widget_class))
            widget = eval("%s.init_dynamic(args)" % widget_class)
        elif method:
            widget = Common.create_from_method(widget_class, method)
        else:
            widget_args = web.get_form_values(WebEnvironment.ARG_NAME)
            widget = Common.create_from_class_path(widget_class, widget_args)

        # tell the widget that it is the top widget
        widget.set_as_top()

        self.add(widget)






