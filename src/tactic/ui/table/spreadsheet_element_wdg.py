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


__all__ = ['SpreadsheetElementWdg']

from pyasm.common import TacticException, FormatValue, jsonloads

from tactic.ui.common import SimpleTableElementWdg
from pyasm.web import DivWdg


class SpreadsheetElementWdg(SimpleTableElementWdg):

    ARGS_KEYS = {
    'column': {
        'description': 'The column from which a runnint total should be calculated from.',
        'category': 'Options'
    },
    'format': {
        'description': 'The template with which to forman resulting value.',
        'category': 'Options'
    },

    }

    def is_sortable(my):
        return False

    def is_editable(my):
        return True

    def init(my):
        my.total = 0


    def get_value(my):
        return my.total


    def get_text_value(my):
        column = my.get_option("column")
        sobject = my.get_current_sobject()
        sobj_value = sobject.get_value(column)
        if sobj_value:
            my.total += sobj_value

        return my.total

    def get_display(my):

        top = my.top

        sobjects = my.sobjects
        sobject = my.get_current_sobject()
        index = my.get_current_index()


        column = my.get_option("column")
        sobject = my.get_current_sobject()
        sobj_value = sobject.get_value(column)
        if sobj_value:
            my.total += sobj_value


        format_str = my.get_option('format')
        if format_str:
            format = FormatValue()
            #display = format.get_format_value(value, "$#,###.##")
            display = format.get_format_value(my.total, format_str)
        else:
            display = my.total


        value_div = DivWdg()
        top.add(value_div)
        value_div.add_style("float: right")
        value_div.add(display)

        name = my.get_name()
        sobject.set_value(name, my.total)
        #sobject.commit()

        return top


    def test(my):

        # Neeed a way to refer to another colum spreadsheet style

        # This will get the cost from the previous sobject
        expr = "@GET(sobject[$INDEX-1].cost)"



        # or do we have a special keyword
        expr = "@COLOR(palette.color, [10, -10, 10])"






