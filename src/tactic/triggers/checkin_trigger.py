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
__all__ = ["CheckinTrigger"]


from pyasm.command import Trigger
from tactic.command import PythonCmd


class CheckinTrigger(Trigger):

    def get_args_keys(self):
        return {
        }

    def get_display(self):
        script_path = self.get_option("script_path")
        script_code = self.get_option("script_code")

        from tactic.command import PythonCmd
        if script_path:
            cmd = PythonCmd(script_path=script_path, values=self.values, search=search, show_title=self.show_title)
        elif script_code:
            cmd = PythonCmd(script_code=script_code, values=self.values, search=search, show_title=self.show_title)

        cmd.execute()



