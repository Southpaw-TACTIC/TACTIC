###########################################################
#
# Copyright (c) 2010, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#

__all__ = ['ProjectSetupWdg']

from pyasm.web import DivWdg, Table
from pyasm.widget import SwapDisplayWdg, CheckboxWdg
from tactic.ui.common import BaseRefreshWdg


class ProjectSetupWdg(BaseRefreshWdg):
    '''Widget that manages the entire project overview'''

    def get_display(my):

        top = DivWdg()
        top.add_class("spt_project_top")
        my.set_as_panel(top)


        inner = DivWdg()
        top.add(inner)
        inner.add_style("padding: 10px")
        inner.add_color("background", "background")

        inner.add("In this project, I want to manage: <br/><br/>")


        categories = ['Project Management', 'Asset Management', 'Budgets and Expenses', 'Ticketing']

        category_items = {
        'Project Management': [
            'Tasks', 'Work Hours', 'Project Tasks', 'Scheduling', 'Task Pipelines'
        ],
        'Asset Management': [
            'Central Asset Library'
        ],
        'Budgets and Expenses': [
            'Expense List'
        ],
        'Ticketing': [
            'Tickets',
            'Sprints',
            'Burn Down',
        ],
        }


        categories_div = DivWdg()
        inner.add(categories_div)

        for category in categories:
            category_div = DivWdg()
            categories_div.add(category_div)
            category_div.add(category)

            items = category_items.get(category)
            for item in items:
                item_div = DivWdg()
                category_div.add(item_div)

                item_div.add("&nbsp;"*5)

                checkbox = CheckboxWdg()
                item_div.add(checkbox)
                item_div.add(item)

            category_div.add_style("margin-bottom: 5px")


        return top


        


