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
__all__ = ['AppShotPanelWdg', 'AppAssetInstancePanelWdg']

from pyasm.common import Xml, Container
from pyasm.web import Widget, DivWdg, HtmlElement, SpanWdg, WebContainer, Table
from pyasm.widget import SelectWdg, FilterSelectWdg, WidgetConfig, HiddenWdg, IconWdg, SwapDisplayWdg, TableWdg

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.panel import TableLayoutWdg, ViewPanelWdg
from tactic.ui.app import SearchWdg
from tactic.ui.filter import FilterData
from connection_select_wdg import ConnectionSelectWdg
from pyasm.prod.biz import ShotInstance, Shot, SessionContents, ProdSetting
from pyasm.search import Search
from pyasm.prod.web import ProcessFilterWdg

class AppShotPanelWdg(BaseRefreshWdg):
    '''Main panel for Shot Loader'''

    ARGS_KEYS = {
        "search_type": {
            'description': "search type that this panel works with",
            'type': 'TextWdg',
            'order': 0,
            'category': 'Required'
        },
        "view": {
            'description': "view to be displayed",
            'type': 'TextWdg',
            'value': 'load',
            'order': 1,
            'category': 'internal'
        },

        "asset_search_type": {
            'description': "asset search type this panel works with",
            'type': 'TextWdg',
            'order': 2,
            'category': 'Optional'
        },

        "instance_search_type": {
            'description': "instance search type this panel works with",
            'type': 'TextWdg',
            'order': 3,
            'category': 'Optional'
        },

        "simple_search_view": {
            'description': "simple search view used in this panel",
            'type': 'TextWdg',
            'order': 4,
            'category': 'Optional'
        }
    
        
    }
    

    def init(self):
        self.view = self.kwargs.get('view')
        self.simple_search_view = self.kwargs.get('simple_search_view')
        self.search_type = self.kwargs.get('search_type')
        self.asset_search_type = self.kwargs.get('asset_search_type')
        if not self.asset_search_type:
            self.asset_search_type = 'prod/asset'
        self.instance_search_type = self.kwargs.get('instance_search_type')
        if not self.instance_search_type:
            self.instance_search_type = 'prod/shot_instance'

        #self.load_script = self.kwargs.get('load_script')
        #self.load_script_path = self.kwargs.get('load_script_path')
        self.is_refresh = self.kwargs.get('is_refresh')=='true'
        self.state = Container.get_full_dict("global_state")
        self.process = self.state.get("process")

        values = FilterData.get().get_values_by_index('shot_filter', 0)
        self.shot_code = values.get('shot_code')
        #self.shot_code = None
    
   

    def get_display(self):

        # just refresh the whole thing 
        widget = DivWdg()
        
        outer_widget = DivWdg(css='spt_view_panel')
        search_div = DivWdg()
        search_bvr = {
            'type':         'click_up',
            'cbjs_action':  'spt.dg_table.search_cbk(evt, bvr)',
            'override_class_name': 'tactic.ui.cgapp.AppShotPanelWdg',
            'override_target': 'bvr.src_el.getParent(".spt_app_shot_panel")',
            'extra_args': {'instance_search_type': self.instance_search_type,
                        'asset_search_type': self.asset_search_type}
            #'panel_id':     'main_body_search'
            
        }

        # WARNING: this is made just for main search box and  won't be compatible with the simple search wdg
        search_wdg = SearchWdg(search_type=self.search_type, custom_search_view='search_shot_loader', parent_key='', filter=''\
            , display='block', custom_filter_view='', state=None, run_search_bvr=search_bvr)

        #from tactic.ui.app.simple_search_wdg import SimpleSearchWdg
        #search_wdg = SimpleSearchWdg(search_type=self.search_type, search_view=self.simple_search_view, state=None, run_search_bvr=search_bvr)
        search_div.add( HtmlElement.spacer_div(1,10) )
        search_div.add(search_wdg)

        # if there is result, it could only be one shot
        search = search_wdg.get_search()
        shots = search.get_sobjects()

        # avoid getting a shot when no shot is selected
        if not self.shot_code and len(shots) == 1:
            self.shot_code = shots[0].get_code()
        
        outer_widget.add(search_div)

        self.set_as_panel(outer_widget, class_name='spt_panel spt_view_panel spt_app_shot_panel')
        #show_shot_panel = False
        #if show_shot_panel:
        panel = ViewPanelWdg( search_type=self.search_type, \
                 inline_search=True, show_search='false', show_refresh='false', view=self.view, \
                run_search_bvr=search_bvr, simple_search_view=self.simple_search_view)
        panel.set_sobjects(shots)

        widget.add(panel)
         
        show_instances_in_shot = ProdSetting.get_value_by_key("show_instances_in_shot_panel")
        if show_instances_in_shot != "false":

            widget.add(HtmlElement.h3("Asset Instances in Shot [%s]" %self.shot_code))
            widget.add(HtmlElement.br(2))
            asset_inst_panel = AppAssetInstancePanelWdg(search_type=self.search_type, instance_search_type=self.instance_search_type, asset_search_type=self.asset_search_type, shot_code=self.shot_code, show_search='false')
            widget.add(asset_inst_panel)
        outer_widget.add(widget)
        return outer_widget

class AppAssetInstancePanelWdg(BaseRefreshWdg):
    '''A Panel for loading assset instances in shot'''

    ARGS_KEYS = {
        "search_type": {
            'description': "search type that this panel works with",
            'type': 'TextWdg',
            'order': 0,
            'category': 'Required'
        },
        "view": {
            'description': "view to be displayed",
            'type': 'TextWdg',
            'value': 'load',
            'order': 1,
            'category': 'internal'
        },

        "asset_search_type": {
            'description': "asset search type this panel works with",
            'type': 'TextWdg',
            'order': 2,
            'category': 'Optional'
        },

        "instance_search_type": {
            'description': "instance search type this panel works with",
            'type': 'TextWdg',
            'order': 3,
            'category': 'Optional'
        },


        "show_search": {
            'description': "whether to show the search button in the UI",
            'type': 'SelectWdg',
            'order': 4,
            'values': 'true|false',
            'category': 'Optional'
        }
    }
   

    def init(self):
        shot_code = self.kwargs.get('shot_code')
        self.search_type = self.kwargs.get('search_type')
        self.asset_search_type = self.kwargs.get('asset_search_type')
        self.instance_search_type = self.kwargs.get('instance_search_type')
       
            #shot_code = web.get_form_value('shot_code')
        self.shot = None
        if shot_code:
            search = Search(self.search_type)
            search.add_filter('code', shot_code)
            self.shot = search.get_sobject()

        self.show_search = self.kwargs.get('show_search') != 'false'

        self.is_refresh = self.kwargs.get('is_refresh')=='true'
    
    def get_display(self):
        
        widget = DivWdg()
        self.set_as_panel(widget, class_name='spt_view_panel spt_panel spt_app_asset_inst_panel')
        
        parent_search_type= self.search_type
        
        if self.show_search:
            # Have to limit this search to just its parent.. cuz if the target is prod/shot_instance
            # and its parent search is ShotFilterWdg, it's hard to isolate what shot has been selected
            search_bvr = {
                'type':         'click_up',
                'cbjs_action':  'spt.dg_table.search_cbk(evt, bvr)',
                'override_class_name': 'tactic.ui.cgapp.AppAssetInstancePanelWdg',
                'override_target': "bvr.src_el.getParent('.spt_app_asset_inst_panel')"
            }

            search_wdg = SearchWdg(search_type=parent_search_type, view='search_shot_loader', parent_key='', filter=''\
            , display='block', custom_filter_view='', state=None, run_search_bvr=search_bvr)
            widget.add( HtmlElement.spacer_div(1,10) )
            widget.add(search_wdg)


            # if there is result, it could only be one shot
            search = search_wdg.get_search()
            shots = search.get_sobjects()
            
            if not self.shot and len(shots) == 1:
                self.shot= shots[0]

        # create the asset table
        table_id = "main_body_asset_instance_table" 
              
        if not self.shot:
            return widget
        # get any parent shots
        parent_code = self.shot.get_value("parent_code")
        shot_code = self.shot.get_code()

        # add the search make sure set elements are not shown
        search = Search(self.instance_search_type)
        if parent_code != "":
            search.add_filters(self.shot.get_foreign_key(), [shot_code,parent_code] )
        else:
            search.add_filter(self.shot.get_foreign_key(), shot_code )

        search.add_where("\"type\" in ('set_item', 'asset')")
        search.add_order_by('asset_code')
        
        instances = search.get_sobjects()

        # if parent shot and current shot has the same instance, hide the 
        # parent's one
        
        top_instances = []
        for instance in instances:
            if instance.get_value('type') != 'set_item':
                top_instances.append(instance)

        #instances = ShotInstance.filter_instances(instances, shot_code)
        top_instances = ShotInstance.filter_instances(top_instances, shot_code)
        # TODO: just add asset name to the ShotInstance table
        # get the original asset names

        aux_data = ShotInstance.get_aux_data(top_instances, self.asset_search_type)

        values = FilterData.get().get_values_by_index('view_action_option', 0)
        state = {}
        
        if not self.show_search:
            if values:
                state['process'] = values.get('load_%s_process'% parent_search_type)
            else:
                process_filter = ProcessFilterWdg(None, parent_search_type)
                state['process'] = process_filter.get_value()

        Container.put("global_state", state)
        
        from tactic.ui.cgapp import CGAppLoaderWdg
        cg_wdg = CGAppLoaderWdg(view='load', search_type=self.instance_search_type)
        widget.add(cg_wdg)

        if not top_instances:
            widget.add('No Asset Instances in Shot.')
        else:
            asset_table = TableLayoutWdg(table_id = table_id, search_type=self.instance_search_type,\
                view="load", inline_search=False, aux_info = aux_data, mode='simple')

            #asset_table = ViewPanelWdg( search_type=search_type,  inline_search=False, \
            #        show_general_search=False, view='load', state=state, mode='simple') 

            asset_table.set_sobjects(top_instances)
            widget.add(asset_table)

            shot_inst_names = [inst.get_code() for inst in instances]
            
            self.add_unassigned_instances(widget, shot_inst_names)
        return widget

    def add_unassigned_instances(self, widget, shot_inst_names):
        ''' add the unassigned instances into a SwapDisplayWdg '''
        info = []
        session = SessionContents.get()
        if not session:
            return ""

        tactic_nodes = session.get_instance_names(is_tactic_node=True)
        non_tactic_nodes = session.get_node_names(is_tactic_node=False)

        """
        title = HtmlElement.b('Unassigned instances')
        widget.add(title)

                  # this is just a filler for now, can be any sobjects
        snapshots = []
        for tactic_node in tactic_nodes:
            if tactic_node not in shot_inst_names:
                session_version = session.get_version(tactic_node) 
                session_snap = session.get_snapshot(tactic_node)
                if session_snap:
                    snapshots.append(session_snap)
                    info.append({'session_version': session_version, 'instance':\
                    tactic_node})

        div = DivWdg(id="unassigned_table")

        SwapDisplayWdg.create_swap_title( title, swap, div) 
        table = TableWdg('sthpw/snapshot', 'session_items')
        table.set_show_property(False)
        table.set_aux_data(info)
        table.set_sobjects(snapshots)
        div.add(table)
        widget.add(div)
        widget.add(HtmlElement.br())

        """
        # Add other non-tactic nodes
        swap2 = SwapDisplayWdg.get_triangle_wdg()
  
        title2 = HtmlElement.b('Other Nodes')
        div2 = DivWdg(id="other_node_div")
        
        widget.add(swap2)
        widget.add(title2)

        SwapDisplayWdg.create_swap_title( title2, swap2, div2) 
        hidden_table = Table(css='table')
        div2.add(hidden_table)
        hidden_table.set_max_width()
        for node in non_tactic_nodes:
            hidden_table.add_row()
            hidden_table.add_cell(node)
            hidden_table.add_blank_cell()

        widget.add(div2)

