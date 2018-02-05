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

__all__ = ['LoaderElementWdg']

import types, re

from pyasm.common import Container, Xml
from pyasm.biz import Project, Snapshot
from pyasm.web import Table, HtmlElement, SpanWdg, DivWdg, WebContainer
from pyasm.widget import CheckboxWdg, ThumbWdg, IconWdg, SwapDisplayWdg, ProdIconButtonWdg
from pyasm.search import SearchKey
from tactic.ui.common import BaseTableElementWdg

from pyasm.prod.biz import SessionContents
from pyasm.prod.load import ProdLoaderContext

from tactic.ui.filter import FilterData
from version_wdg import VersionWdg

class LoaderElementWdg(BaseTableElementWdg):
    '''Snapshot loader for any search type'''
    CB_NAME = "load_snapshot"
    REF_CB_NAME = "replace_ref"
    
    # this PREFIX corresponds to the one set in LoadOptionsWdg
    #PREFIX = "asset"
  
    def init_kwargs(self):
        self.search_type = self.kwargs.get('search_type')
        self.shot_search_type = self.kwargs.get('shot_search_type')
        self.mode = self.kwargs.get("mode")

        if not self.mode:
            self.mode = "output"

    def get_load_script(cls, search_type):
        #load_script = "execute_client_callback('ClientLoadCbk')"
        load_script = "load_selected_snapshots_cbk('%s', '%s_%s', bvr) " \
            %(search_type, search_type, cls.CB_NAME)
        return load_script
    get_load_script = classmethod(get_load_script)


    def get_process_data(self):
        '''get the list of processes that can be checked in with this widget'''
        labels, values = Pipeline.get_process_select_data(self.search_type, \
            extra_process=['publish'], project_code=Project.get_project_code())
        
        return labels, values

   
    def get_title(self):
        mode = self.get_option("mode")
        title = SpanWdg()
       
        #loader = LoaderButtonWdg()
        #loader.set_load_script( self.get_load_script() )
        #return loader
        search_type = self.get_search_type()
        cb_name = '%s_%s' %(search_type, self.CB_NAME)
        master_cb = CheckboxWdg('master_control')
        master_cb.add_behavior({'type': 'click_up',
            'propagate_evt': True,
            'cbjs_action': '''
                var inputs = spt.api.Utility.get_inputs(bvr.src_el.getParent('.spt_table'),'%s','.spt_latest_%s');
                for (var i = 0; i < inputs.length; i++)
                    inputs[i].checked = bvr.src_el.checked;
                    ''' %(cb_name, mode)})
        title.add(master_cb)

        if mode == "input":
            title.add("Receive")
        else:
            title.add("Deliver")
        return title
    
    def preprocess(self):
        # get the session, by default asset_mode = False, but we set it to True
        self.session = SessionContents.get(asset_mode=True)
    
        # add some action buttons
        #mode = self.get_option("mode")
        

    def get_process(self):
        '''Get from the ProcessFilterWdg in SObjectLoadWdg,
            otherwise get from FilterData'''

        process = ''

        # Ususally there is no pipeline defined for prod/shot_instance
        # so get from prod/shot
        search_type = self.search_type
        if search_type =='prod/shot_instance':
            search_type = 'prod/shot'

        state = Container.get("global_state")
        if state:
            process = state.get('process')
        else:
            
            # get it from FilterData
            data = FilterData.get()
            values = data.get_values_by_prefix('view_action_option')
            if values:
                process = values[0].get('load_%s_process' %search_type)

        if not process:
            from pyasm.prod.web import ProcessFilterWdg
            process_filter = ProcessFilterWdg(None, search_type)
            process = process_filter.get_value()
        return process


    def get_snapshot(self, mode):
        ''' get the snapshot depending on the mode i.e. input, output'''
        dict = self.get_current_aux_data()
        output_snapshots = input_snapshots = None
        # the check for key is needed since snapshot can be None
        if dict and dict.has_key('%s_snapshots' %mode):
            if mode == 'output':
                output_snapshots = dict.get('%s_snapshots' %mode)
            else:
                input_snapshots = dict.get('%s_snapshots' %mode)
        else:
            sobject = self.get_current_sobject()
            process = self.get_process()
            loader = ProdLoaderContext()
            if self.shot_search_type:
                loader.set_shot_search_type(self.shot_search_type)
            
            output_snapshots = loader.get_output_snapshots(sobject, process)
            input_snapshots = loader.get_input_snapshots(sobject, process)
            # this is for sharing with AssetLoaderWdg
            # should only be called once per sobject
            idx = self.get_current_index()
            self.insert_aux_data(idx, {'output_snapshots': output_snapshots, \
                'input_snapshots': input_snapshots})

        if mode == 'output':
            return output_snapshots
        else:
            return input_snapshots



    def get_namespace(self, sobject, snapshot):
        ''' this is actually the namespace in Maya and node name in Houdini'''
        if not sobject:
            return ""

        naming = Project.get_naming("node") 
        naming.set_sobject(sobject)
        naming.set_snapshot(snapshot)
        instance = naming.get_value()
        return instance   


    def get_asset_code(self):
        asset_code = ''
        sobject = self.get_current_sobject()
        if sobject.has_value("asset_code"):
            asset_code = sobject.get_value("asset_code")
        else:
            asset_code = sobject.get_code()

        return asset_code
    
    def get_node_name(self, snapshot, asset_code, namespace):
        ''' if possible get the node name from snapshot which is more accurate'''
        node_name = snapshot.get_node_name()
        if not node_name:
            # FIXME: put in proper application detector
            app_name = WebContainer.get_web().get_selected_app() 
            if app_name == "Maya":
                from pyasm.application.maya import MayaNodeNaming
                naming = MayaNodeNaming()
            elif app_name == "XSI":
                from pyasm.application.xsi import XSINodeNaming
                naming = XSINodeNaming()
            else:
                from pyasm.application.houdini import HoudiniNodeNaming
                naming = HoudiniNodeNaming()
            naming.set_asset_code(asset_code)
            naming.set_namespace(namespace)

            node_name = naming.build_node_name()
        return node_name


    def get_session_asset_mode(self):
        '''For assets, this is true.  For instances, this is false'''
        return True



    def get_display(self):
        self.init_kwargs()
        sobject = self.get_current_sobject()

        table = Table(css='minimal')
        table.add_color("color", "color")
        table.add_style("font-size: 0.9em")

       
        
        snapshots = self.get_snapshot(self.mode)
        for snapshot in snapshots:
            table.add_row()

            value = self.get_input_value(sobject, snapshot)

            current_version = snapshot.get_value("version")
            current_context = snapshot.get_value("context")
            current_revision = snapshot.get_value("revision", no_exception=True)
            current_snapshot_type = snapshot.get_value("snapshot_type")

            # hack hard coded type translation
            if current_snapshot_type == "anim_export":
                current_snapshot_type = "anim"

            # ignore icon context completely
            if current_context == "icon":
                table.add_blank_cell()
                table.add_cell("(---)")
                return table

            checkbox = CheckboxWdg('%s_%s' %(self.search_type, self.CB_NAME))
            
            # this is added back in for now to work with 3.7 Fast table
            checkbox.add_behavior({'type': 'click_up',
            'propagate_evt': True})

            checkbox.add_class('spt_latest_%s' %self.mode)
            checkbox.set_option("value", value )
            table.add_cell( checkbox )

            load_all = False
            if load_all:
                checkbox.set_checked()


            # add the file type icon
            xml = snapshot.get_snapshot_xml()
            file_name = xml.get_value("snapshot/file/@name")
            icon_link = ThumbWdg.find_icon_link(file_name)
            image = HtmlElement.img(icon_link)
            image.add_style("width: 15px")
            table.add_cell(image)

            namespace = self.get_namespace(sobject, snapshot) 
            asset_code = self.get_asset_code()
          
            # force asset mode = True   
            self.session.set_asset_mode(asset_mode=self.get_session_asset_mode())
            node_name = self.get_node_name(snapshot, asset_code, namespace)
            # get session info
            session_context = session_version = session_revision = None
            if self.session:
                
                session_context = self.session.get_context(node_name, asset_code, current_snapshot_type)
                session_version = self.session.get_version(node_name, asset_code, current_snapshot_type)
                session_revision = self.session.get_revision(node_name, asset_code,current_snapshot_type)


                # Maya Specific: try with namespace in front of it for referencing
                referenced_name = '%s:%s' %(namespace, node_name)
                if not session_context or not session_version:
                    session_context = self.session.get_context(referenced_name, asset_code, current_snapshot_type)
                    session_version = self.session.get_version(referenced_name, asset_code, current_snapshot_type)
                    session_revision = self.session.get_revision(referenced_name, asset_code, current_snapshot_type)

            from version_wdg import CurrentVersionContextWdg, SubRefWdg

            version_wdg = CurrentVersionContextWdg()
            data = {'session_version': session_version, \
                'session_context': session_context,  \
                'session_revision': session_revision,  \
                'current_context': current_context, \
                'current_version': current_version, \
                'current_revision': current_revision }
            version_wdg.set_options(data)
            
            table.add_cell(version_wdg, "no_wrap")
            td = table.add_cell(HtmlElement.b("(%s)" %current_context))
            td.add_tip("Snapshot code: %s" % snapshot.get_code())
            #table.add_cell(snapshot.get_code() )

            #if snapshot.is_current():
            #    current = IconWdg("current", IconWdg.CURRENT)
            #    table.add_cell(current)
            #else:
            #    table.add_blank_cell()


            # handle subreferences
            has_subreferences = True
            xml = snapshot.get_xml_value("snapshot")
            refs = xml.get_nodes("snapshot/file/ref")
            if self.mode == "output" and refs:
                table.add_row()
                td = table.add_cell()
                swap = SwapDisplayWdg.get_triangle_wdg()
                td.add(swap)
                td.add("[ %s reference(s)" % len(refs))
                #td.add_style("text-align: right")

                sub_ref_wdg = SubRefWdg()
                sub_ref_wdg.set_info(snapshot, self.session, namespace)
                swap.add_action_script( sub_ref_wdg.get_on_script(), "toggle_display('%s')" % sub_ref_wdg.get_top_id() )

                status = sub_ref_wdg.get_overall_status()
                td.add(SpanWdg(VersionWdg.get(status), css='small_left'))
                td.add(']')
             
                td.add( sub_ref_wdg )
                td.add_style('padding-left: 10px')



        #else:
        if not snapshots:
            table.add_row()
            table.add_blank_cell()
            table.add_cell("(---)")

        return table


    def get_bottom_wdg(self):
        if self.get_option('mode') =='input':
            return 
        web = WebContainer.get_web()
        if web.get_selected_app() not in ['XSI','Maya']:
            return
        div = DivWdg(css='spt_outdated_ref')
       

        refs = self.session.get_data().get_nodes("session/node/ref")
        snap_codes = []
        snap_contexts = []
        sobjects = []
        session_data_dict = {}
        asset_codes = []
        current_snapshots = []
        node_names = []
        session_versions = []
        for ref in refs:
            snap_code = Xml.get_attribute(ref, "asset_snapshot_code")
            node_name = Xml.get_attribute(ref, "name")
            version = Xml.get_attribute(ref, "asset_snapshot_version")
            asset_code = Xml.get_attribute(ref, "asset_code")
            if snap_code in snap_codes:
                continue
            snap_codes.append(snap_code)
            snap_contexts.append(Xml.get_attribute(ref, "asset_snapshot_context"))
            asset_codes.append(asset_code)
            session_data_dict[snap_code] = version, node_name  
        
        
        # must search one by one
        warnings=[]
        for idx, snap_code in enumerate(snap_codes):
            snapshot = Snapshot.get_by_code(snap_code)
            if not snapshot:
                continue
            search_type = snapshot.get_value('search_type')
            search_id = snapshot.get_value('search_id')
            sk = SearchKey.build_search_key(search_type, search_id, column='id')
            current_snapshot = Snapshot.get_snapshot(search_type, search_id, context=snap_contexts[idx], version=0)
            if not current_snapshot:
                warnings.append("Current version for [%s] context [%s] not found" %(sk, snap_contexts[idx]))
                continue
            session_version, node_name  = session_data_dict.get(snap_code)
            if session_version and int(current_snapshot.get_version()) > int(session_version):
                current_snapshots.append(current_snapshot)
                sobjects.append(current_snapshot.get_sobject())
                node_names.append(node_name)
                session_versions.append(int(session_version))
        

        title = DivWdg('Outdated References')
        title.add_style('text-decoration','underline')
        div.add(title)

        # draw the nodes to be udpated
        for idx, current_snap in enumerate(current_snapshots):
            
            cb = CheckboxWdg(self.REF_CB_NAME)
            cb.add_class('spt_ref')
            cb.add_style('display: none')
            sobj = sobjects[idx]
            node_name = node_names[idx]
            session_version = session_versions[idx]
            snapshot = current_snap
            cb_value = self.get_input_value(sobj, snapshot)
            items = cb_value.split('|')
            items[-1] = node_name
            cb_value = '|'.join(items)
            cb.set_option('value', cb_value)
            div.add(cb)
            div.add('%0.1d. %s v%0.3d -> v%0.3d\n' \
                %(idx+1, node_name, session_version, snapshot.get_version()))
            div.add(HtmlElement.br())

        for warning in warnings:
            div.add(SpanWdg(warning, css='warning'))
        div.add(HtmlElement.br())

        if current_snapshots:
            # add the button
            prefix = self.search_type
            #input_name = '%s_%s' %(self.search_type, self.CB_NAME)
            update_button = ProdIconButtonWdg("Update all references")
            update_button.add_behavior({'type': "click_up",\
            'cbjs_action': '''var cousins = bvr.src_el.getParent('.spt_outdated_ref').getElements('.spt_ref');
                             cousins.each( function(x) {x.checked=true;}); py_replace_reference(bvr, '%s','%s')'''
                    % (prefix, self.REF_CB_NAME)})
            div.add( SpanWdg(update_button, css='small'))
       
        div.add(HtmlElement.br(2))
        return div


    def get_input_value(self, sobject, snapshot):
        #This is for generic custom loading

        #from pyasm.search import SearchKey
        #value = SearchKey.build_by_sobject(snapshot)
        namespace = self.get_namespace(sobject,snapshot)
        snap_node_name = snapshot.get_node_name()

        # in case there is space , fill it with
        if snap_node_name:
            snap_node_name = snap_node_name.replace(' ', '_')

        value = "%s|%s|%s|%s" % (snapshot.get_code(), snapshot.get_context(), \
            namespace, snap_node_name)
       
        # differnt checkbox for for prod/shot_instance
        if sobject and sobject.get_base_search_type()=='prod/shot_instance':
            shot = sobject.get_shot()
            instance = sobject.get_value('name')
            value = "%s|%s|%s|%s|%s|%s" % (snapshot.get_code(), shot.get_code(), \
                instance, snapshot.get_context(), namespace, snap_node_name)
            

        return value



    def get_smart_menu(cls, search_type):
        prefix = search_type

        menu_data = []

        menu_data.append( {
            "type": "title", "label": "Actions"
        } )

        # Load and reference options
        load_script = cls.get_load_script(search_type)
        input_name = '%s_%s' %(search_type, cls.CB_NAME)
        menu_data.append( {
            "type": "action",
            "label": "Reference",
            "bvr_cb": {
                'instantiation': 'reference',
                'cbjs_action': '''
                %s
                ''' % load_script
            }
        } )

        menu_data.append( {
            "type": "action",
            "label": "Import",
            "bvr_cb": {
                'instantiation': 'import',
                'cbjs_action': '''
                %s
                ''' % load_script
            } 
        } )
 

        menu_data.append( {
            "type": "action",
            "label": "Open",
            "bvr_cb": {
                'instantiation': 'open',
                'cbjs_action': '''
                %s
                '''% load_script
            } 
        } )
 

        menu_data.append( { 'type': 'separator' } )


        # Update Reference
        menu_data.append( {
            "type": "action",
            "label": "Update Reference",
            "bvr_cb": {
                'cbjs_action':
                    '''
                    py_replace_reference(bvr, '%s', '%s')
                    '''% (prefix, input_name)
            },
            "hover_bvr_cb": { 'activator_add_looks': 'dg_header_cell_hilite',
                              'affect_activator_relatives' : [ 'spt.get_next_same_sibling( @, null )' ] }
        } )

        # Update Reference Selected
        menu_data.append( {
            "type": "action",
            "label": "Update Selected Reference",
            "bvr_cb": {
                'cbjs_action':
                    '''
                    py_replace_reference_selected(bvr, '%s','%s')
                    '''% (prefix, input_name)
            },
            "hover_bvr_cb": { 'activator_add_looks': 'dg_header_cell_hilite',
                              'affect_activator_relatives' : [ 'spt.get_next_same_sibling( @, null )' ] }
        } )


        return { 'menu_tag_suffix': 'MAIN', 'width': 200, 'opt_spec_list': menu_data, 'allow_icons': False }

    get_smart_menu = classmethod(get_smart_menu)

 

