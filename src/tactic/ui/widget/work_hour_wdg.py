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

__all__ = ['WorkHourWdg']

from tactic.ui.common import BaseRefreshWdg

from pyasm.web import DivWdg
from pyasm.search import Search, SearchType
from tactic.ui.panel import TableLayoutWdg

class WorkHourWdg(BaseRefreshWdg):
    '''Special widget to add work hours'''

    def get_display(self):

        top = DivWdg()
        self.set_as_panel(top)

        sobject = SearchType.create("sthpw/virtual")
        sobject.set_value("mon", "3")
        sobject.set_value("tue", "2")
        sobject.set_value("wed", "5")

        config = '''
        <week>
            <element name="week"/>
            <element name="parent"/>
            <element name="category"/>
            <element name="description"/>
            <element name="mon"/>
            <element name="tue"/>
            <element name="wed"/>
            <element name="thu"/>
            <element name="fri"/>
            <element name="total"/>
        </week>
        '''

        table = TableLayoutWdg(search_type='sthpw/virtual', view='week')
        top.add(table)

        return top








