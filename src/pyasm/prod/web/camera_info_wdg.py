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

__all__ = ['CameraInfoWdg']

from pyasm.web import *
from pyasm.widget import *


class CameraInfoWdg(BaseTableElementWdg):


    def get_display(self):
        sobject = self.get_current_sobject()

        table = Table()
        table.add_style("width: 400px")

        table.add_row()
        table.add_header("Lab Roll")
        table.add_cell( sobject.get_value("lab_roll") )
        table.add_header("Aspect Ratio")
        table.add_cell( sobject.get_value("aspect_ratio") )
        table.add_header("Slate")
        table.add_cell( sobject.get_value("slate") )

        table.add_row()
        table.add_header("Cam Roll")
        table.add_cell( sobject.get_value("roll") )
        table.add_header("Perf")
        table.add_cell( sobject.get_value("perf") )
        table.add_header("Take")
        table.add_cell( sobject.get_value("take") )

        return table





