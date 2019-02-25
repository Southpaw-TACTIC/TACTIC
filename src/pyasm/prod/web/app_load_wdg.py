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

__all__ = ['SObjectLoadWdg', 'MayaLoadWdg', 'MayaAnimLoadWdg', 'MayaLayerLoadWdg', 'LoadOptionsWdg', 'ShotLoadOptionsWdg', 'MayaNamespaceWdg']


from pyasm.search import *
from pyasm.web import *
from pyasm.widget import *

from asset_filter_wdg import *
from shot_navigator_wdg import *
from prod_wdg import *
from pyasm.prod.biz import *
from pyasm.biz import *
from pyasm.common import Container



class SObjectLoadWdg(Widget):

    LOAD_TYPE = "asset"

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        super(SObjectLoadWdg,self).__init__(self)

    def get_display(self):
        # create the asset tab
        widget = Widget()
        self.search_type = self.options.get("search_type")
        if not self.search_type:
            self.search_type = self.kwargs.get("search_type")

        assert self.search_type

        # the filter for searching assets
        div = DivWdg(css="filter_box")


        # add the possibility of a custom callback
        callback = self.options.get('callback')
        if callback:
            hidden = HiddenWdg("callback", callback)
            div.add(hidden)


        # or add the possiblity of a switch mode
        pipeline_type = "load"
        hidden = HiddenWdg("pipeline_type", pipeline_type)


        #sobject_filter = GeneralFilterWdg("%s_filter" % self.search_type)
        #sobject_filter.set_columns_from_search_type(self.search_type)
        #div.add(sobject_filter)

        process_filter = ProcessFilterWdg(self.get_context_data(), self.LOAD_TYPE)
        span = SpanWdg(process_filter, css='med')
        div.add(span)
        widget.add(div)
        """
        # add button to introspect
        button = IntrospectWdg()
        button.add_style("float", "right")
        widget.add( button )
        widget.add(HtmlElement.br())
        """

        # load options for diff search type
        if self.search_type == 'prod/shot':
            load_options = ShotLoadOptionsWdg()
        elif self.search_type == 'prod/shot_instance':
            load_options = AnimLoadOptionsWdg()
        elif self.search_type == 'prod/asset':
            load_options = LoadOptionsWdg()
        else:
            load_options = LoadOptionsWdg()

        widget.add(load_options)


        #table = TableWdg(self.search_type, "load")
        #widget.add(table)

        # add the search
        #search = Search(self.search_type)
        #sobject_filter.alter_search(search)
        #process_filter.alter_search(search)
        #table.set_search(search)
        #table.do_search()

        return widget



    def get_context_data(self):
        '''get the list of contexts that can be checked in with this widget'''
        labels, values = Pipeline.get_process_select_data(self.search_type, \
            project_code=Project.get_project_code())
        
        return labels, values




class MayaLoadWdg(Widget):

    LOAD_TYPE = "asset"

    def __init__(self, **kwargs):
        super(MayaLoadWdg,self).__init__(self)

    def init(self):
        # create the asset tab
        widget = Widget()
        asset_type = "prod/asset"

        # the filter for searching assets
        div = DivWdg(css="filter_box")

        asset_filter = AssetFilterWdg()
        div.add(asset_filter)
        process_filter = ProcessFilterWdg(self.get_process_data(), self.LOAD_TYPE)
        div.add(process_filter)
        hint = HintWdg('Selecting a process allows you to see the input (left) and output (right) deliverables for each asset below.')
        div.add(hint)
        widget.add(div)
        

        # add button to introspect
        button = IntrospectWdg()
        button.add_style("float", "right")
        widget.add( button )
        widget.add(HtmlElement.br())

        # load options for assets
        load_options = LoadOptionsWdg()
        widget.add(load_options)

        # add the search
        asset_table = TableWdg(asset_type, "load")
        widget.add(asset_table)
        search = Search(asset_type)
        widget.set_search(search)

        self.add(widget)

    def get_process_data(self):
        '''get the list of process that can be checked in with this widget'''
        is_group_restricted = False
        if ProcessFilterWdg.has_restriction():
            is_group_restricted = True
        labels, values = Pipeline.get_process_select_data('prod/asset', \
            project_code=Project.get_project_code(), is_group_restricted=is_group_restricted)
        
        return labels, values
    

class MayaAnimLoadWdg(MayaLoadWdg):

    LOAD_TYPE = "anim"
    
    def init(self):
        self.show_load_options = True
        self.show_process_filter = True
        self.show_shot_selector = True 

    def set_show_shot_selector(self, flag):
        self.show_shot_selector = flag

    def set_show_load_options(self, flag):
        self.show_load_options = flag


    def set_show_process_filter(self, flag):
        self.show_process_filter = flag

    def get_process_data(self):
        '''get the list of process that can be checked in with this widget'''
        labels, values = Pipeline.get_process_select_data('prod/shot', \
            project_code=Project.get_project_code())
        
        return labels, values 
    
    def get_display(self):

        div = DivWdg(css="filter_box")
        shot_navigator = ShotNavigatorWdg()
        if self.show_shot_selector:
            div.add(shot_navigator)
            refresh_button = IconButtonWdg("Refresh", icon=IconWdg.REFRESH)
            refresh_button.add_behavior({
                'type': 'click', 
                'cbjs_action':  "var top=bvr.src_el.getParent('.spt_main_panel');spt.panel.refresh(top, {}, true)"})
            div.add(refresh_button)


        if self.show_process_filter:
            div.add(HtmlElement.br(2))
            process_filter = ProcessFilterWdg(self.get_process_data(), self.LOAD_TYPE)
            
            div.add(process_filter)
        if div.widgets:
            self.add(div)
            


        shot = shot_navigator.get_shot()
        if not shot:
            self.add(HtmlElement.h3("Please select a shot"))
            return
        shot_code = shot.get_code()


        #table = TableWdg(shot.SEARCH_TYPE, "manage", css="minimal")
        #table.set_show_property(False)
        #table.set_show_header(False)
        #table.set_sobject(shot)
        #self.add(table)


        # get any parent shots
        parent_code = shot.get_value("parent_code")

        # shot load options
        if self.show_load_options:
            load_options = AnimLoadOptionsWdg()
            self.add(load_options)
        
        from prod_checkin_wdg import MayaCheckinWdg
        self.add(MayaCheckinWdg.get_introspect_wdg())

        # create the asset table
        asset_type = ShotInstance.SEARCH_TYPE
        asset_table = TableWdg(asset_type, "load")
        
        # add the search make sure set elements are not shown
        search = Search(asset_type)
        if parent_code != "":
            search.add_filters(shot.get_foreign_key(), [shot_code,parent_code] )
        else:
            search.add_filter(shot.get_foreign_key(), shot_code )

        search.add_where("\"type\" in ('set_item', 'asset')")
        search.add_order_by('asset_code')
        
        instances = search.get_sobjects()

        # if parent shot and current shot has the same instance, hide the 
        # parent's one
        
        top_instances = []
        for instance in instances:
            if instance.get_value('type') != 'set_item':
                top_instances.append(instance)

        instances = ShotInstance.filter_instances(instances, shot_code)
        top_instances = ShotInstance.filter_instances(top_instances, shot_code)
        asset_table.set_sobjects(top_instances)

        # TODO: just add asset name to the ShotInstance table
        # get the original asset names

        aux_data = ShotInstance.get_aux_data(top_instances)
        asset_table.set_aux_data(aux_data)
        
        self.add(asset_table)

        shot_inst_names = [inst.get_code() for inst in instances]
        
        self.add_unassigned_instances(shot_inst_names)
        return super(MayaAnimLoadWdg,self).get_display()

    

    def add_unassigned_instances(self, shot_inst_names):
        ''' add the unassigned instances into a SwapDisplayWdg '''
        swap = SwapDisplayWdg.get_triangle_wdg()
        self.add(swap)

        title = HtmlElement.b('Unassigned instances')
        self.add(title)

        session = SessionContents.get()
        if not session:
            return ""

        tactic_nodes = session.get_instance_names(is_tactic_node=True)
        non_tactic_nodes = session.get_node_names(is_tactic_node=False)
        info = []
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
        self.add(div)
        self.add(HtmlElement.br())

        # Add other non-tactic nodes
        swap2 = SwapDisplayWdg.get_triangle_wdg()
  
        title2 = HtmlElement.b('Other Nodes')
        div2 = DivWdg(id="other_node_div")
        
        self.add(swap2)
        self.add(title2)

        SwapDisplayWdg.create_swap_title( title2, swap2, div2) 
        hidden_table = Table(css='table')
        div2.add(hidden_table)
        hidden_table.set_max_width()
        for node in non_tactic_nodes:
            hidden_table.add_row()
            hidden_table.add_cell(node)
            hidden_table.add_blank_cell()

        self.add(div2)
         
    

class MayaLayerLoadWdg(MayaLoadWdg):

    LOAD_TYPE = "layer"

    def get_process_data(self):
        '''get the list of processs that can be checked in with this widget'''
        labels, values = Pipeline.get_process_select_data('prod/shot', \
            project_code=Project.get_project_code())
        
        return labels, values 
    
    def init(self):

        div = DivWdg(css="filter_box")
      
        div.add(ProcessFilterWdg(self.get_process_data(), self.LOAD_TYPE))
        self.add(div)
        
        button = IntrospectWdg()
        button.add_style("float", "right")
        self.add(button)


        shot_navigator = ShotNavigatorWdg()
        self.add(shot_navigator)
        shot = shot_navigator.get_shot()


        # create the layer tab
        layer_tab = DivWdg()
        layer_type = "prod/layer"

        load_options = LoadOptionsWdg()
        self.add(load_options)

        layer_table = TableWdg(layer_type, "load")
        layer_tab.add(layer_table)

        # add the search
        search = Search(layer_type)
        shot_code = -1
        if shot:
            shot_code = shot.get_code()
        #search.add_filter("shot_code", shot_code )
        layers = search.get_sobjects()
        layer_tab.set_sobjects(layers)

        self.add(layer_table)






class LoadOptionsWdg(Widget):

    def init(self):
        self.prefix = "asset"
        self.hide_proxy = False
        self.hide_connection = False
        self.hide_instantiation = False
        self.hide_dependencies = False

    def set_prefix(self, prefix):
        self.prefix = prefix


    def get_element_name(self, name):
        if self.prefix:
            return "%s_%s" % (self.prefix, name)
        else:
            return name

    def get_default_setting(self):
        '''get default setting for options'''
        setting = {'instantiation': 'reference',
                'connection': 'http',
                'texture_dependency': 'as checked in'}
        return setting

    def get_display(self):
    
        widget = Widget()
        
        div = DivWdg()
        div.set_unique_id()
        table = Table()
        div.add(table)
        table.add_style("margin: 5px 15px")

        swap = SwapDisplayWdg()
        swap.set_off()
        title = SpanWdg("Loading Options")
        SwapDisplayWdg.create_swap_title(title, swap, div, is_open=True)

        widget.add(swap)
        widget.add(title)
        widget.add(div)

        if not self.hide_instantiation:
            table.add_row()
            table.add_blank_cell()
            div = DivWdg(HtmlElement.b("Instantiation: "))
            table.add_cell(div)
            div = self.get_instantiation_wdg()
            table.add_cell(div)


        setting = self.get_default_setting()
        default_instantiation = setting.get('instantiation')
        default_connection = setting.get('connection')
        default_dependency = setting.get('texture_dependency')

        if not self.hide_connection:
            table.add_row()
            table.add_blank_cell()
            con_div = DivWdg(HtmlElement.b("Connection: "))
            table.add_cell(con_div)
            td = table.add_cell()

            is_unchecked = True
            default_cb = None
            for value in ['http', 'file system']:
                name = self.get_element_name("connection")
                checkbox = CheckboxWdg( name )
                id = checkbox.generate_unique_id()
                checkbox.set_id(id)
                checkbox.set_option("value", value)
                checkbox.set_persistence()
                if value == default_connection:
                    default_cb = checkbox
                if checkbox.is_checked():
                    is_unchecked = False
                checkbox.add_behavior({'type': 'click_up', 
                    'propagate_evt': True,
                    "cbjs_action": "get_elements('%s').check_me('%s');" %(name,id)}) 
                span = SpanWdg(checkbox, css='small')
                span.add(value)

                td.add(span)
            if is_unchecked:
                default_cb.set_checked()
        """
        if not self.hide_proxy:
            table.add_row()
            table.add_cell( HtmlElement.b("Proxy: ")) 

            proxy = CheckboxWdg( self.get_element_name("load_proxy") )
            proxy.set_option("value", "yes")
            proxy.set_persistence(self)

            span = SpanWdg(proxy, css='small')
            span.add("set_assets")

            td = table.add_cell()
            td.add(span)

            table.add_row()
            tex_span = SpanWdg(HtmlElement.b("Textures: "), css='med')
            table.add_cell(tex_span)


            # TODO: Add in none when it works
            #for value in ['none', 'low', 'high']:
            td = table.add_cell()
            for value in ['low', 'high']:
                name = self.get_element_name("textures")
                checkbox = CheckboxWdg( name )
                id = checkbox.generate_unique_id()
                checkbox.set_id(id)
                checkbox.set_option("value", value)
                checkbox.set_persistence()
                checkbox.add_event('onclick',"get_elements('%s').check_me('%s')" %(name,id) )
                span = SpanWdg(checkbox, css='small')
                span.add(value)
                td.add(span)

        """


        if not self.hide_dependencies:
            table.add_row()
            table.add_blank_cell()
            div = DivWdg(HtmlElement.b("Texture Dependencies: "))
            table.add_cell(div)
            td = table.add_cell()
            
            is_unchecked = True
            default_cb = None
            for value in ['as checked in', 'latest', 'current']:
                name = self.get_element_name("dependency")
                checkbox = CheckboxWdg( name )
                id = checkbox.generate_unique_id()

                
                checkbox.set_id(id)
                checkbox.set_option("value", value)
                checkbox.set_persistence()
                checkbox.add_behavior({'type': 'click_up', 
                    'propagate_evt': True,
                    "cbjs_action": "get_elements('%s').check_me('%s');" %(name,id)}) 
                if value == default_dependency:
                    default_cb = checkbox
                if checkbox.is_checked():
                    is_unchecked = False

                span = SpanWdg(checkbox, css='small')
                span.add(value)
                td.add(span)
            if is_unchecked:
                default_cb.set_checked()

        return widget

    def get_instantiation_wdg(self):
        setting = self.get_default_setting()
        default_instantiation = setting.get('instantiation')

        div = DivWdg()
        is_unchecked = True
        default_cb = None
        for value in self.get_instantiation_options():
            name = self.get_element_name("instantiation")
            checkbox = CheckboxWdg( name )
            if value == default_instantiation:
                default_cb = checkbox
            
            id = checkbox.generate_unique_id()
            checkbox.set_id(id)
            checkbox.set_option("value", value)
            checkbox.set_persistence()
            if checkbox.is_checked():
                is_unchecked = False
            checkbox.add_behavior({'type': 'click_up', 
                    'propagate_evt': True,
                    "cbjs_action": "get_elements('%s').check_me('%s');" %(name,id)}) 
            span = SpanWdg(checkbox, css='small')
            span.add(value)
            div.add(span)
        if is_unchecked:
            default_cb.set_checked()
        return div

    def get_instantiation_options(self):
        options = ['reference', 'import', 'open']
        if WebContainer.get_web().get_selected_app() == 'Houdini':
            options = ['reference']
        
        return options

class AnimLoadOptionsWdg(LoadOptionsWdg):

    def __init__(self):
        super(AnimLoadOptionsWdg,self).__init__()
        # this should match the PREFIX in InstanceLoaderWdg
        self.prefix = "instance"
        self.hide_proxy = True
        self.hide_dependencies = True


    def get_instantiation_options(self):
        return ['reference', 'import', 'open']

class ShotLoadOptionsWdg(LoadOptionsWdg):

    def __init__(self):
        super(ShotLoadOptionsWdg,self).__init__()
        self.prefix = "shot"

    def get_instantiation_options(self):
        options = ['reference', 'import', 'open']
        if WebContainer.get_web().get_selected_app() == 'Houdini':
            options = ['import', 'open']
        elif WebContainer.get_web().get_selected_app() == 'XSI':
            options = ['open']
        return options

    def get_default_setting(self):
        '''get default setting for options'''
        setting = {'instantiation': 'open',
                'connection': 'http',
                'texture_dependency': 'as checked in'}
        return setting

   

class MayaNamespaceWdg(Widget):

    NS_SELECT = 'namespace'
    def init(self):

        intro = IntrospectWdg()
        intro.add_style("float", "right")
        
        session = SessionContents.get()
        if not session:
            row_div = DivWdg(intro)
            row_div.add("Click on Introspect to start")
            self.add(row_div)
            return
            
        namespace_dict = session.get_namespace()
        current = namespace_dict.get('current')
        namespaces = namespace_dict.get('child')
        
        if 'UI' in namespaces:
            namespaces.remove('UI')
        div = DivWdg()
        
        row_div = DivWdg()
        ns_span = SpanWdg('Namespace: ')
        ns_select = SelectWdg(self.NS_SELECT)
        ns_span.add(ns_select)
        ns_select.append_option('%s (current)' %current, current)
        
        if namespaces:
            ns_select.set_option('values', '|'.join(namespaces))
        
        # append root namespace if not found
        if ':' not in namespaces and ':' not in current:
            ns_select.append_option(':',':')
        
        add_node = ProdIconButtonWdg('Assign Selected', long=True)
        add_node.add_event('onclick', "add_node_to_namespace('%s')" \
            %self.NS_SELECT )

        set_node = ProdIconSubmitWdg('Set Namespace', long=True)
        set_node.add_event('onclick', "set_namespace('%s')" \
            %self.NS_SELECT )
        
        
        

        hint = HintWdg("After selecting the top node of objects in the session,"\
                " click on [ Assign Selected ]")
        row_div.add(intro)
        row_div.add(ns_span)
        row_div.add(HtmlElement.br(2))
        row_div.add(set_node)
        row_div.add(add_node)
        row_div.add(hint)

        row_div.add(HtmlElement.br(2))
        # TODO: add these add/remove namespace functions
        '''
        insert = IconButtonWdg('insert', icon=IconWdg.INSERT, long=True)
        insert_txt = TextWdg('new_namespace')
        remove = IconButtonWdg('remove', icon=IconWdg.DELETE, long=True )
        remove_div = DivWdg(remove)
        
        row_div.add(insert)
        row_div.add(insert_txt)
        row_div.add(HtmlElement.br(2))
        row_div.add(remove_div)
        '''
        div.add(row_div)
        self.add(div)


        hidden = HiddenWdg("namespace_info")
        self.add(hidden)
        insert = ProdIconButtonWdg('Contents')
        insert.add_event("onclick", "get_namespace_contents()" )
        self.add(insert)

        
        contents = hidden.get_value().split("\t")

        table = Table()
       
        for content in contents:
            table.add_row()
            table.add_cell(content)
        self.add(table)


