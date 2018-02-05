###########################################################
#
# Copyright (c) 2005, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
# AUTHOR:
#     Remko Noteboom
#
#

from pyasm.web import *
from pyasm.widget import *

class HeaderWdg(Widget):

    def init(self):
        table = Table()
        table.add_style("width: 100%")

        div = self.get_header_wdg()
        table.add_cell(div)

        login = WebContainer.get_login()
        info_wdg = Table()
        tr, td = info_wdg.add_row_cell( login.get_full_name() )
        td.add_style("text-align: right")
        tr, td = info_wdg.add_row_cell( SignOutLinkWdg() )
        td.add_style("text-align: right")
        #tr, td = info_wdg.add_row_cell( ChangePasswordLinkWdg() )
        #td.add_style("text-align: right")
        info_wdg.add_style("float: right")


        table.add_cell( info_wdg )

        self.add(table)



    def get_header_wdg(self):
        web = WebContainer.get_web()
        context = web.get_context_url()
        div = DivWdg()
        div.add( "<h3>Sample Tactic Site</h3>")
        return div

