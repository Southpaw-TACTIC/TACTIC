###########################################################
#
# Copyright (c) 2009, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#
__all__ = ["PythonRestHandler"]

from pyasm.common import Environment, jsondumps

from tactic.ui.common import BaseRefreshWdg
from tactic.command import PythonCmd

import os


class PythonRestHandler(BaseRefreshWdg):

    def get_args_keys(my):
        return {
        }


    def get_display(my):

        script_path = my.kwargs.get("script_path")
        if not script_path:
            return {}

        python_cmd = PythonCmd(**my.kwargs)

        ret_val = python_cmd.execute()

        return ret_val





    
