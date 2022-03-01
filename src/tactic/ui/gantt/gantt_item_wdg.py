###########################################################
#
# Copyright (c) 2017, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#


__all__ = [ "BaseGanttItemWdg", "BaseGanttRowWdg", "BaseGanttRangeWdg" ]



from pyasm.common import jsonloads, jsondumps, SPTDate
from pyasm.search import Search
from pyasm.command import Command, DatabaseAction
from pyasm.web import DivWdg, HtmlElement
from pyasm.search import Search, SearchType
from pyasm.widget import IconButtonWdg
from pyasm.prod.biz import ProdSetting

from tactic.ui.common import BaseRefreshWdg

import dateutil
from dateutil.relativedelta import *
from dateutil import parser
from datetime import datetime, timedelta


import six
basestring = six.string_types


class BaseGanttRowWdg(BaseRefreshWdg):

    def init(self):

        self.set_as_panel(self.top)

        self.search_key = self.kwargs.get("search_key")
        if self.search_key:
            self.sobject = Search.get_by_search_key(self.search_key)
        else:
            self.sobject = self.kwargs.get("sobject")
            self.search_key = self.sobject.get_search_key()


        self.search_type = self.sobject.get_base_search_type()

        start_date = self.kwargs.get("start_date")
        end_date = self.kwargs.get("end_date")

        if not start_date:
            start_date = datetime.today().strftime('%Y-%m-%d')
        if not end_date:
            end_date = datetime.today().strftime('%Y-%m-%d')

        start_date = parser.parse(start_date)
        self.start_date = SPTDate.convert(start_date)
        end_date = parser.parse(end_date)
        self.end_date = SPTDate.convert(end_date)


        self.percent_per_day = self.kwargs.get("percent_per_day")
        if isinstance(self.percent_per_day, basestring):
            self.percent_per_day = float(self.percent_per_day)

        self.nobs_mode = self.kwargs.get("nobs_mode")

    def get_milestone_wdg(cls, sobject, color="#FFF", accent="#333", size=10):

        top = DivWdg()
        top.add_class("spt_milestone")
        border_color = top.get_color("border")

        top.add_style("height: 100%")

        inner = DivWdg()
        top.add(inner)
        inner.add_class("spt_milestone_display")
        inner.add_style("height: %s" % size)
        inner.add_style("width: %s" % size)
        inner.add_style("background: %s" % color)
        inner.add_style("border: solid 1px %s" % border_color)
        inner.add_style("transform: rotate(45deg)")
        inner.add_style("margin-top: 3px")

        inner.add_attr("spt_hover_color", accent)

        return top

    get_milestone_wdg = classmethod(get_milestone_wdg)





    def get_percent(self, start_date, end_date):
        # calculates the percentage position of a date based on the
        # min/max range
        if isinstance(start_date, basestring):
            start_date = parser.parse(start_date)
        if isinstance(end_date, basestring):
            end_date = parser.parse(end_date)

        if not start_date:
            start_date = datetime.today()
        if not end_date:
            end_date = datetime.today()

        diff = end_date - start_date

        days = float(diff.days) + float(diff.seconds)/(24*3600)
        return self.percent_per_day * days



# Backwards compatibiltity
class BaseGanttItemWdg(BaseGanttRowWdg):
    pass
    

"""
class MultiGanttItemWdg(BaseRefreshWdg):

    def get_display(self):

        widgets = self.kwargs.get("widgets")

        top = self.top

        for item in widget_kwargs:

            class_name = item[0]
            kwargs = item[1]

            widget = Common.create_from_class_path(class_name, [], kwargs)
            top.add(widget)


        return top
"""



class BaseGanttRangeWdg(BaseRefreshWdg):

    def get_percent(self, start_date, end_date):
        # calculates the percentage position of a date based on the
        # min/max range
        if isinstance(start_date, basestring):
            start_date = parser.parse(start_date)
        if isinstance(end_date, basestring):
            end_date = parser.parse(end_date)

        if not start_date:
            start_date = datetime.today()
        if not end_date:
            end_date = datetime.today()

        diff = end_date - start_date

        days = float(diff.days) + float(diff.seconds)/(24*3600)
        return self.percent_per_day * days




    def get_display(self):

        pass













