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

# 

__all__ = ['YearlyReportWdg', 'YearlyReportFilterWdg']

from pyasm.common import Date, Common, Container, TacticException
from pyasm.search import Search, SearchKey, SearchType
from pyasm.biz import ExpressionParser
from pyasm.web import Table, DivWdg, SpanWdg, WebContainer
from pyasm.widget import IconWdg, IconButtonWdg, BaseTableElementWdg, TextWdg
from tactic.ui.common import BaseRefreshWdg
from tactic.ui.filter import FilterData, BaseFilterElementWdg


# DEPRECATED: this is an mms specific report


class YearlyReportFilterWdg(BaseFilterElementWdg):

    def alter_search(self, search):
        pass


    def get_display(self):
        div = SpanWdg()
        div.add(" is ")
        text = TextWdg("year")
        value = self.values.get("year")
        if value:
            text.set_value(value)
        div.add(text)
        return div

 


class YearlyReportWdg(BaseTableElementWdg):

    def get_display(self):
        filter_data = FilterData.get_from_cgi()
        values = filter_data.get_values("custom", "year")

        year = 0
        for value in values:
            if value:
                try:
                    year = int(value)
                except:
                    pass
        if not year:
            date = Date()
            year = int(date.get_year())

        sobject = self.get_current_sobject()
        id = sobject.get_id()

        column = self.get_option("column")
        month = int( self.get_option('month') )

        end_year = year
        end_month = month + 1
        if end_month > 12:
            end_month = 1
            end_year += 1



        search_type = 'MMS/personal_time_log'

        if year:

            search = Search(search_type)
            search.add_filter('login_id', id)
            search.add_filter('work_performed_date', '%s-%0.2d-01' % (year,month), '>')
            search.add_filter('work_performed_date', '%s-%0.2d-01' % (end_year,end_month), '<')

            sobjects = search.get_sobjects()
        else:
            sobjects = []


        if sobjects:
            parser = ExpressionParser()
            sum = parser.eval("@SUM(%s.%s)" % (search_type,column),sobjects=sobjects)
        else:
            sum = 0

        div = DivWdg()
        div.add(sum)
        return div





