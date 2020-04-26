###########################################################
#
# Copyright (c) 2009, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#
__all__ = ['IntrospectWdg', 'IntrospectFilterWdg', 'IntrospectSelectWdg']

from pyasm.web import DivWdg, SpanWdg
from pyasm.widget import HiddenWdg, CheckboxWdg
from tactic.ui.common import BaseRefreshWdg

from pyasm.biz import Snapshot
from pyasm.search import Search, SearchType
from pyasm.prod.web import ProdIconSubmitWdg
from pyasm.prod.biz import SessionContents


'''
Sample data structure:

<session>
<node asset_code="chr001" instance="|chr001|bob" name="|chr001|bob:chr001" namespace="|chr001|bob" reference="true" tactic_node="true" type="transform">
    <ref asset_code="chr001" instance="bob" name="bob:chr001" namespace="bob" reference="true" tactic_node="true" type="transform"/> 
</node>
</session>

'''



class IntrospectWdg(BaseRefreshWdg):
    '''a widget that does introspection to analyze/update what 
        assets(versions) are loaded in the session of the app'''

    def init(self):
        self.top = DivWdg()

    def add_style(self, name, value=None):
        self.top.add_style(name, value)

    def get_display(self):

        button = ProdIconSubmitWdg("Introspect", long=True)
        button.add_style("height: 14px")
        button.add_style("font-size: 0.8em")
        #self.add_style("padding: 3px 10px 2px 10px")
        button.add_behavior({
            'type': "click",
            'cbjs_action': "introspect(bvr)"
        })

        self.top.add(button)
        return self.top




class IntrospectFilterWdg(BaseRefreshWdg):
    '''a widget that filters based on the snapshots that exist in the session
    from introspection'''

    def init(self):
        self.top = DivWdg()

    def add_style(self, name, value=None):
        self.top.add_style(name, value)

    def get_display(self):

        search_wdg = DivWdg()
        search_wdg.add_class("spt_table_search")
        prefix = HiddenWdg("prefix", "introspect")
        search_wdg.add(prefix)

        hidden = HiddenWdg("introspect", "true")
        search_wdg.add(hidden)

        class_name = HiddenWdg("class_name", "tactic.ui.cgapp.IntrospectWdg")
        search_wdg.add(class_name)

        checkbox = CheckboxWdg("search")
        search_wdg.add("Session Filter: ")
        search_wdg.add(checkbox)

        self.top.add(search_wdg)

        return self.top


    def alter_search(self, search):
        print "Introspect alter_search"

        # see if any of the filters have a class handler defined
        from tactic.ui.filter import FilterData
        filter_data = FilterData.get_from_cgi()
        values = filter_data.get_values_by_index("introspect", 0)

        do_search = values.get('search')
        if not do_search:
            return
            



        #search.add_filter("code", "chr002")
        session = SessionContents.get()

        node_names = session.get_node_names()

        snapshot_codes = session.get_snapshot_codes()
        snapshot_search = Search("sthpw/snapshot")
        snapshot_search.add_filters("code", snapshot_codes)
        snapshots = snapshot_search.get_sobjects()

        state_search_type = self.kwargs.get("search_type")


        # get ids
        ids = []
        for snapshot in snapshots:
            search_type = snapshot.get_value("search_type")
            if state_search_type:
                search_type_obj = SearchType.get(search_type)
                key = search_type_obj.get_base_key()
                print "compare: ", key, state_search_type
                if key != state_search_type:
                    continue

            id = snapshot.get_value("search_id")
            ids.append(id)

        print "ids: ", ids
        if ids:
            search.add_filters("id", ids)




class IntrospectSelectWdg(ProdIconSubmitWdg):
    '''a widget that does selected introspection to analyze/update 
        what assets(versions) are loaded in the session of the app'''

    def __init__(self):
        super(IntrospectSelectWdg, self).__init__("Introspect Select", long=True)
        self.add_style("height: 14px")
        self.add_style("font-size: 0.8em")
        self.add_event("onclick", "introspect_select()")

 


