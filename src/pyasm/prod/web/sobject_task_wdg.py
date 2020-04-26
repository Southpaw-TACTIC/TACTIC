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


__all__ = ['SObjectTaskWdg', 'MilestoneTaskWdg']

# diplays all of the tasks associated with an sobject


from pyasm.search import Search
from pyasm.web import *
from pyasm.widget import *
from pyasm.prod.biz import *



class SObjectTaskWdg(Widget):


    def init(self):
        web = WebContainer.get_web()

        args = web.get_form_args()
        search_type = args['search_type']
        search_id = args['search_id']

        # get the sobject
        sobject = Search.get_by_id(search_type, search_id)

        # get the tasks
        snapshot_type = "sthpw/task" 
        search = Search(snapshot_type)

        self.add_filter(search, sobject)

        search.add_order_by("timestamp desc")
        snapshots = search.do_search()

        div = HtmlElement.div()
        div.add_style("float: right")
        div.add_style("width: 95%")

        div.add(self.get_table(sobject,snapshots) )
        self.add(div)


    def add_filter(self, search, sobject):
        search.add_filter("search_type", sobject.get_search_type() )
        search.add_filter("search_id", sobject.get_id() )



    def get_table(self, sobject, snapshots):

        div = HtmlElement.div()
        div.add_style("float: right")
        div.add_style("width: 95%")
        table = TableWdg("sthpw/task")
        table.set_sobjects(snapshots)
        div.add(table)
        return div



class MilestoneTaskWdg(SObjectTaskWdg):

    def add_filter(self, search, sobject):
        search.add_filter("milestone_code", sobject.get_code() )


    def get_table(self, sobject, snapshots):

        div = HtmlElement.div()
        div.add_style("float: right")
        table = TableWdg("sthpw/task", "self_task")
        table.set_sobjects(snapshots)
        div.add(table)
        return div



