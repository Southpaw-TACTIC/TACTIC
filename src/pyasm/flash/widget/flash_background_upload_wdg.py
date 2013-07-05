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

__all__ = ['FlashBackgroundUploadWdg']

from pyasm.web import Table, DivWdg
from pyasm.widget import BaseInputWdg, SelectWdg


class FlashBackgroundUploadWdg(BaseInputWdg):

    def get_display(my):

        div = DivWdg()
        table = Table()
        table.set_class("minimal")
        table.add_style("font-size: 0.8em")
        table.add_row()
        table.add_cell("File")
        table.add_cell('<input type="file" name="%s"/>' % (my.get_input_name())
        )
        table.add_row()
        table.add_cell("Context")

        select = SelectWdg("%s|context" % my.get_input_name() )
        select.set_option("values", "publish|roughDesign|colorFinal|colorKey")
        table.add_cell(select)

        table.add_row()
        table.add_cell("Description")
        table.add_cell('<textarea name="%s|description"></textarea>' % my.get_input_name())
        div.add(table)

        return div



