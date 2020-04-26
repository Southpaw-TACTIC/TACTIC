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

__all__ = ['PublishLogWdg', 'PublishBrowserWdg']

from pyasm.search import *
from pyasm.web import *
from pyasm.widget import TableWdg
from pyasm.biz import *
from pyasm.common import Environment

from asset_filter_wdg import *
from prod_input_wdg import *
from tactic.ui.common import BaseRefreshWdg

class PublishLogWdg(BaseRefreshWdg):
    ''' A widget used to display publish/checkin log '''

    def init(self):
        self.publish_search_type = self.kwargs.get('publish_search_type')
        self.snapshot_filter_enabled = self.kwargs.get('snapshot_filter_enabled')

    def get_search_wdg(self):
        if not self.publish_search_type:
            self.publish_search_type = ''
        search_type = "sthpw/snapshot"
        from tactic.ui.app import SearchWdg

        # provide a view, so it will not automatically get the last saved search instead
        # we need to differentiate between client and dailies search
        state = {'publish_search_type': self.publish_search_type,
                'snapshot_filter_enabled': self.snapshot_filter_enabled}
        search_wdg = SearchWdg(search_type=search_type, view='search', state=state)
    
        
        return search_wdg

    def get_display(self):
        # create the asset tab
        widget = DivWdg(css="spt_view_panel")
        self.set_as_panel(widget) 
        search_wdg = self.get_search_wdg()
        widget.add(search_wdg)
        widget.add(HtmlElement.br())
        search = search_wdg.get_search()

        
        # the filter for searching assets
        #div = DivWdg(css="filter_box")
        #snap_filter = SnapshotFilterWdg()
        #div.add(snap_filter)
        #widget.add(div)

        table_id = "main_body_table" 
        from tactic.ui.panel import TableLayoutWdg
        snap_table = TableLayoutWdg(table_id=table_id, search_type=Snapshot.SEARCH_TYPE, \
                view="log", inline_search=True)
        snap_table.alter_search(search)
        widget.add(snap_table)

        
        search.add_order_by("timestamp desc")
        sobjects = search.get_sobjects()
        #search.add_filter("login", Environment.get_login().get_login())
        #widget.set_search(search)
        snap_table.set_sobjects(sobjects, search)

        return widget


class PublishBrowserWdg(BaseRefreshWdg):
    ''' A widget used to display publish/checkin log '''

    def init(self):
        self.search_type = self.kwargs.get('search_type')
        self.search_id = self.kwargs.get('search_id')
        self.is_refresh = self.kwargs.get('is_refresh') =='true'

    def get_display(self):
        
        if not self.is_refresh:
            widget = DivWdg()
            self.set_as_panel(widget)
        else:
            widget = Widget() 


        sobject = Search.get_by_id(self.search_type, self.search_id)
        if sobject:
            search_type = sobject.get_base_search_type()
        else:
            widget.add('sobject not found with [%s,%s]' %(self.search_type, self.search_id))
            return widget

        # the filter for searching assets
        div = DivWdg(css="filter_box")
        filter = ProcessSelectWdg(label = 'Process: ', search_type=search_type,\
                css='med', has_empty=True)
        filter.set_persistence()
        filter.add_behavior({'type' : 'change',
            'cbjs_action': '%s;%s'%(filter.get_save_script(), filter.get_refresh_script())
            })
        div.add(filter)

        # note assuming process == context here
        contexts = filter.get_values()
        if contexts:
            contexts = contexts[0].split(",")
        else:
            contexts = None
        widget.add(div)


        snap_table = TableWdg(Snapshot.SEARCH_TYPE, "publish_browser")
        widget.add(snap_table)

        # add the search
        search = Search(Snapshot.SEARCH_TYPE)
        search.add_order_by("version desc")
        search.add_sobject_filter(sobject)
        if contexts:
            search.add_filters("context", contexts)

        snap_table.set_sobjects(search.get_sobjects())
        snap_table.set_search(search)

        return widget









