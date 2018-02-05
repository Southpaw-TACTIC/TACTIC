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


__all__ = ['WeekWdg']

from pyasm.web import Table, DivWdg


from tactic.ui.common import BaseRefreshWdg

class WeekWdg(BaseRefreshWdg):

    def get_display(self):
        top = self.top
        top.add_style("padding: 20px")
        top.add_color("background", "background")

        start_date = 'xxx' 
        end_date = 'xxx'

        days = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday']

        start_time = '06:00'
        end_time = '21:00'

        table = Table()
        top.add(table)

        table.add_row()
        table.add_header()
        for day in days:
            td = table.add_header(day)

        for hour in xrange(6, 21):
            tr = table.add_row()

            td = table.add_cell()
            td.add("%0.2d:00" % hour)
            td.add_color("background", "background3")

            for day in days:
                td = table.add_cell()

                day_div = DivWdg()
                td.add(day_div)
                day_div.add_style("width: 100px")
                day_div.add_style("height: 50px")
                day_div.add_border()



            day_div = DivWdg()



        return top


