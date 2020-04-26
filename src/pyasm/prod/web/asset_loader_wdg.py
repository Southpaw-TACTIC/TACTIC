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

__all__ = ['SnapshotLoaderButtonWdg', 'SnapshotLoaderWdg', 'AssetLoaderWdg', 'InstanceLoaderWdg', 'LayerLoaderWdg', 'ShotLoaderWdg', 'SubRefWdg']

from pyasm.search import Search, SObject
from pyasm.web import *
from pyasm.widget import *
from pyasm.prod.biz import *
from pyasm.prod.load import *
from version_wdg import *
from prod_wdg import ProdIconButtonWdg
from prod_context import *
from pyasm.application.maya import MayaNodeNaming
from pyasm.application.houdini import HoudiniNodeNaming
from pyasm.application.xsi import XSINodeNaming

from tactic.ui.filter import FilterData
from tactic.ui.container import SmartMenu
from tactic.ui.widget import TextOptionBtnWdg
from pyasm.biz import Snapshot, Project

class SnapshotLoaderButtonWdg(Widget):

    LOAD_BUTTON_ID = "load_id"

    def init(self):
        self.load_script = ""
        self.smart_menu_data = None

    def set_load_script(self, load_script):
        self.load_script = load_script
        
    def set_smart_menu(self, data):
        self.smart_menu_data = data

    def get_display(self):
        assert self.load_script

        widget = DivWdg()
        widget.add_style('float', 'right')

        load_button = TextOptionBtnWdg(label='   Load   ', size='medium')
        load_button.get_top_el().add_style('float', 'left')
        load_button.get_top_el().set_id(self.LOAD_BUTTON_ID)
        load_button.add_behavior(
                {'type': "click_up", 
                "cbjs_action":
                "setTimeout(function() {%s}, 200) "% self.load_script
                })  
        widget.add(load_button)
        arrow_button = load_button.get_option_widget()
        #widget.add(arrow_button)
        suffix = "ASSET_LOADER_FUNCTIONS"
        menus_in = [ self.smart_menu_data ]

        SmartMenu.add_smart_menu_set( arrow_button,  menus_in)
        SmartMenu.assign_as_local_activator(arrow_button, None, True)

        #SmartMenu.attach_smart_context_menu( load_button, menus_in, False )
        x_div = FloatDivWdg("x")
        x_div.add_style('margin-right: 6px')
        widget.add(x_div)
        multiplier = TextWdg()
        multiplier.set_id("load_multiplier")
        multiplier.set_option("size", "1.5")
        multiplier.add_style("font-size: 0.8em")
        multiplier.add_style("float: left")
        multiplier.add_class("load_multiplier")
        widget.add( multiplier )

        return widget



from tactic.ui.common import BaseRefreshWdg
class SnapshotLoaderWdg(BaseRefreshWdg):

    CB_NAME = "search_key"
    REF_CB_NAME = "replace_ref"
    LOAD_BUTTON_ID = "load_id"
    # this PREFIX corresponds to the one set in LoadOptionsWdg
    PREFIX = "asset"


    def init(self):
        parent_key = self.kwargs.get("parent_key")
        self.parent = Search.get_by_search_key(parent_key)
        self.search_type = self.parent.get_search_type()
        self.search_id = self.parent.get_id()



    def set_cb_name(self):
        self.name = self.CB_NAME


    def get_load_script(self):
        load_script = "execute_client_callback('ClientLoadCbk')"
        return load_script



    def get_process_data(self):
        '''get the list of processes that can be checked in with this widget'''
        labels, values = Pipeline.get_process_select_data('prod/asset', \
            extra_process=['publish'], project_code=Project.get_project_code())
        
        return labels, values

   
    def get_title(self):
        mode = self.get_option("mode")
        if mode == "input":
            return "Input"
        else:
            return "Output"

        #loader = SnapshotLoaderButtonWdg()
        #loader.set_load_script( self.get_load_script() )
        #return loader

    
    def preprocess(self):
        # get the session, by default asset_mode = False, but we set it to True
        self.session = SessionContents.get(asset_mode=True)
    
        # add some action buttons
        mode = self.get_option("mode")
        if mode != "input":
            # float item is related to the output snapshot
            self.add_float_items() 
        

    def get_process(self):
        process_select = Container.get('process_filter')
        process = ''
        if process_select:
            process = process_select.get_value()
        else:
            # get it from FilterData
            data = FilterData.get()
            values = data.get_values_by_prefix('view_action_option')
            if values:
                process = values[0].get('load_asset_process')

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
                naming = MayaNodeNaming()
            elif app_name == "XSI":
                naming = XSINodeNaming()
            else:
                naming = HoudiniNodeNaming()
            naming.set_asset_code(asset_code)
            naming.set_namespace(namespace)

            node_name = naming.build_node_name()
        return node_name


    def get_session_asset_mode(self):
        '''For assets, this is true.  For instances, this is false'''
        return True



    def get_display(self):

        sobject = self.get_current_sobject()

        table = Table(css='minimal')
        table.add_style("font-size: 0.9em")

        mode = self.get_option("mode")
        if not mode:
            mode = "output"
        
        snapshots = self.get_snapshot(mode)
        for snapshot in snapshots:
            table.add_row()

            value = self.get_input_value(sobject, snapshot)

            latest_version = snapshot.get_value("version")
            latest_context = snapshot.get_value("context")
            latest_revision = snapshot.get_value("revision", no_exception=True)
            latest_snapshot_type = snapshot.get_value("snapshot_type")

            # hack hard coded type translation
            if latest_snapshot_type == "anim_export":
                latest_snapshot_type = "anim"

            # ignore icon context completely
            if latest_context == "icon":
                table.add_blank_cell()
                table.add_cell("(---)")
                return table

            checkbox = CheckboxWdg(self.CB_NAME)
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
                
                session_context = self.session.get_context(node_name, asset_code, latest_snapshot_type)
                session_version = self.session.get_version(node_name, asset_code, latest_snapshot_type)
                session_revision = self.session.get_revision(node_name, asset_code, latest_snapshot_type)


                # Maya Specific: try with namespace in front of it for referencing
                referenced_name = '%s:%s' %(namespace, node_name)
                if not session_context or not session_version:
                    session_context = self.session.get_context(referenced_name, asset_code, latest_snapshot_type)
                    session_version = self.session.get_version(referenced_name, asset_code, latest_snapshot_type)
                    session_revision = self.session.get_revision(referenced_name, asset_code, latest_snapshot_type)


            version_wdg = LatestVersionContextWdg()
            data = {'session_version': session_version, \
                'session_context': session_context,  \
                'session_revision': session_revision,  \
                'latest_context': latest_context, \
                'latest_version': latest_version, \
                'latest_revision': latest_revision }
            version_wdg.set_options(data)
            
            table.add_cell(version_wdg, "no_wrap")
            td = table.add_cell(HtmlElement.b("(%s)" %latest_context))
            td.add_tip("Snapshot code: %s" % snapshot.get_code())
            #table.add_cell(snapshot.get_code() )

            if snapshot.is_current():
                current = IconWdg("current", IconWdg.CURRENT)
                table.add_cell(current)
            else:
                table.add_blank_cell()


            # handle subreferences
            has_subreferences = True
            xml = snapshot.get_xml_value("snapshot")
            refs = xml.get_nodes("snapshot/file/ref")
            if mode == "output" and refs:
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


    def get_bottom(self):
        if self.get_option('mode') =='input':
            return 
        web = WebContainer.get_web()
        if web.get_selected_app() not in ['XSI','Maya']:
            return
        div = DivWdg( css='spt_outdated_ref')
       

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
            current_snapshot = Snapshot.get_snapshot(search_type, search_id, context=snap_contexts[idx], version=0)
            if not current_snapshot:
                warnings.append("Current version for [%s|%s] context [%s] not found" %(search_type, search_id, snap_contexts[idx]))
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
            prefix = self.PREFIX 
            update_button = ProdIconButtonWdg("Update all references")
            update_button.add_behavior({'type': "click_up",\
            'cbjs_action': '''var cousins = bvr.src_el.getParent('.spt_outdated_ref').getElements('.spt_ref');
                             cousins.each( function(x) {x.checked=true;}); py_replace_reference('%s','%s')'''
                    % (prefix, self.REF_CB_NAME)})
            div.add( SpanWdg(update_button, css='small'))
        
        return div


    def get_input_value(self, sobject, snapshot):
        from pyasm.search import SearchKey
        value = SearchKey.build_by_sobject(snapshot)
        return value



    def add_float_items(self):
        # these float items are applicable to 3d assets
        prefix = self.PREFIX 
        float_span = SpanWdg()
        select_button = IconButtonWdg("Select", IconWdg.SELECT, long=False)
        select_button.add_event("onclick", "py_select('%s')" % prefix)
        float_span.add( SpanWdg(select_button, css='small') )

        delete_button = IconButtonWdg("Delete", IconWdg.DELETE, long=False)
        delete_button.add_event("onclick", "py_delete('%s')" % prefix)
        float_span.add( SpanWdg(delete_button, css='small') )
        
        if WebContainer.get_web().get_selected_app() != 'XSI':
            replace_button = IconButtonWdg("Replace", IconWdg.REPLACE, long=False)
            replace_button.add_event("onclick", "py_update('%s')" % prefix)
            float_span.add( SpanWdg(replace_button, css='small') )
       
        update_button = IconButtonWdg("Update", IconWdg.UPDATE, long=False)
        update_button.add_event("onclick", "py_replace_reference('%s')" % prefix)
        float_span.add( SpanWdg(update_button, css='small') )

        update_sel_button = IconButtonWdg("Update Selected", IconWdg.UPDATE, long=False)
        update_sel_button.add('s')
        update_sel_button.add_event("onclick", "py_replace_reference_selected('%s')" % prefix)
        float_span.add( SpanWdg(update_sel_button, css='small') )

        #if not Container.get('SnapshotAction'):
        #    self.add_snapshot_action(float_span)


       

    def get_smart_menu(self):
        prefix = self.PREFIX

        menu_data = []

        menu_data.append( {
            "type": "title", "label": "Extra Functions"
        } )

        # Update Reference
        menu_data.append( {
            "type": "action",
            "label": "Update Reference",
            "bvr_cb": {
                'cbjs_action':
                    '''
                    py_replace_reference('%s')
                    '''% prefix
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
                    py_replace_reference_selected('%s')
                    '''% prefix
            },
            "hover_bvr_cb": { 'activator_add_looks': 'dg_header_cell_hilite',
                              'affect_activator_relatives' : [ 'spt.get_next_same_sibling( @, null )' ] }
        } )
        return { 'menu_tag_suffix': 'MAIN', 'width': 200, 'opt_spec_list': menu_data, 'allow_icons': False }
    


class AssetLoaderWdg(SnapshotLoaderWdg):

    CB_NAME = "load_snapshot"  

    def get_load_script(self):
        load_script = "load_selected_snapshots_cbk('%s', '%s', bvr) " \
            %(self.PREFIX, self.CB_NAME)
        return load_script

    def get_input_value(self, sobject, snapshot):
        namespace = self.get_namespace(sobject,snapshot)
        snap_node_name = snapshot.get_node_name()
        value = "%s|%s|%s|%s" % (snapshot.get_code(), snapshot.get_context(), \
            namespace, snap_node_name)
        return value



 
class InstanceLoaderWdg(AssetLoaderWdg):
  
    PREFIX = 'instance'
    CB_NAME = 'instance'  
    def get_session_asset_mode(self):
        '''For assets, this is true.  For instances, this is false'''
        return False

    def get_load_script(self):
        load_script = "load_selected_snapshots_cbk('%s','%s', bvr) " \
            %(self.PREFIX, self.CB_NAME)
        return load_script


    def preprocess(self):
        # get the session, by default asset_mode = False
        self.session = SessionContents.get(asset_mode=False)
    
        # add some action buttons
        mode = self.get_option("mode")
        if mode != "input":
            # float item is related to the output snapshot
            self.add_float_items() 

    def get_title(self):
        mode = self.get_option("mode")
        if mode == "input":
            return "Input"


        widget = Widget()

        float_menu = WebContainer.get_float_menu()
        icon = float_menu.get_icon()
        widget.add(SpanWdg(icon, css='small'))

        #widget.add(super(AssetLoaderWdg,self).get_title())
        self.shot = ProdContext.get_shot()

        load_button = ProdIconButtonWdg("Load", long=True)
        load_button.set_id(self.LOAD_BUTTON_ID)
        prefix = self.PREFIX
        load_button.add_behavior({"type": "click_up", \
            "cbjs_action":
            "setTimeout(function() { load_selected_snapshots_cbk('%s', '%s', bvr)}, 200)" \
            % (prefix, self.CB_NAME)
            })
        widget.add(load_button)

        update_button = ProdIconButtonWdg("Update", long=True)
        update_button.add_event("onclick", "setTimeout(function() {py_replace_reference('%s','%s')}, 200)" % \
            (prefix, self.CB_NAME))
        widget.add(update_button)

        # get the session
        self.session = SessionContents.get()
        
        return widget

   
    def get_node_name(self, snapshot, asset_code, namespace):
        ''' if possible get the node name from snapshot which is more accurate'''
        # don't use snapshot's node name since it's not correct in initial version for a new context 
        #node_name = snapshot.get_node_name()
        node_name = ''
        if not node_name:
            naming = MayaNodeNaming()
            app_name = WebContainer.get_web().get_selected_app()
            if app_name == "Maya":
                naming = MayaNodeNaming()
            elif app_name == "XSI":
                naming = XSINodeNaming()
            elif app_name == "Houdini":
                naming = HoudiniNodeNaming()
            naming.set_asset_code(asset_code)
            naming.set_namespace(namespace)

            node_name = naming.build_node_name()
        return node_name


    def get_input_value(self, sobject, snapshot):
        ''' value of the loading checkbox''' 
        # use the naming
        naming = Project.get_naming("node")
        naming.set_sobject(sobject)
        naming.set_snapshot(snapshot)
        namespace = naming.get_value()
        instance = sobject.get_name()
        snap_node_name = snapshot.get_node_name()

        """
        # Currently, web state object is not rebuilt.
        shot_id = self.search_id
        if not shot_id:
            shot_id = WebState.get().get_state("shot_id")

        if shot_id == "":
            shot_id = WebContainer.get_web().get_form_value("shot_id")
        if shot_id == "":
            raise WidgetException("No shot found value passed in")
        """

         
        #shot = self.parent.get_shot()

        shot_code = self.parent.get_value("shot_code")

        value = "%s|%s|%s|%s|%s|%s" % (snapshot.get_code(), shot_code, \
                instance, snapshot.get_context(), namespace, snap_node_name)
        return value



    def add_float_items(self):
        # these float items are applicable to instances assigned to a shot
        prefix = self.PREFIX
        float_span = SpanWdg()
        select_button = IconButtonWdg("Select", IconWdg.SELECT, long=False)
        select_button.add_event("onclick", "py_select('%s')" %prefix)
        float_span.add( SpanWdg(select_button, css='small') )

        delete_button = IconButtonWdg("Delete", IconWdg.DELETE, long=False)
        delete_button.add_event("onclick", "py_delete('%s')" %prefix)
        float_span.add( SpanWdg(delete_button, css='small') )

        replace_button = IconButtonWdg("Replace", IconWdg.REPLACE, long=False)
        replace_button.add_event("onclick", "py_update('%s')" %prefix)
        float_span.add( SpanWdg(replace_button, css='small') )

        update_button = IconButtonWdg("Update", IconWdg.UPDATE, long=False)
        update_button.add_event("onclick", "py_replace_reference('%s')" %prefix)
        float_span.add( SpanWdg(update_button, css='small') )

        update_sel_button = IconButtonWdg("Update Selected", IconWdg.UPDATE, long=False)
        update_sel_button.add('s')
        update_sel_button.add_event("onclick", "py_replace_reference_selected('%s')" % prefix)
        float_span.add( SpanWdg(update_sel_button, css='small') )

        #self.add_snapshot_action(float_span)

        WebContainer.get_float_menu().add(float_span) 
        WebContainer.get_float_menu().set_title('Shot Instances')

class LayerLoaderWdg(InstanceLoaderWdg):

    
    def get_input_value(self, sobject, snapshot):

        instance = sobject.get_value("name")

        # the sobject must have a shot code
        shot_code = sobject.get_value("shot_code")
        shot = Shot.get_by_code(shot_code)
        snap_node_name = snapshot.get_node_name()
        
        value = "%s|%s|%s|%s|%s" % (snapshot.get_code(), shot_code, \
                instance, snapshot.get_context, snap_node_name())
        return value


    def get_snapshot(self, mode):

        sobject = self.get_current_sobject()

        # get the current shot (Should probably use WebState)
        web = WebContainer.get_web()
        # Currently, web state object is not rebuilt.
        shot_id = WebState.get().get_state("shot_id")
        if shot_id == "":
            shot_id = WebContainer.get_web().get_form_value("shot_id")
        if shot_id == "":
            raise WidgetException("No shot found value passed in")

        # TODO: this code is old, to be updated
        '''
        shot = Shot.get_by_id(shot_id) 
        if not shot:
            return None
            
        context = self.get_process()
        loader = ProdLoaderContext()
        snapshot = loader.get_snapshot_by_sobject( sobject, context )
        '''
        snapshots = []
        return snapshots



class ShotLoaderWdg(AssetLoaderWdg): 

    LOAD_BUTTON_ID = 'load_shot_id'
    PREFIX = 'shot'
    CB_NAME = "shot"  
    def get_process_data(self):
        '''get the list of contexts that can be checked in with this widget'''
        labels, values = Pipeline.get_process_select_data('prod/shot', \
            project_code=Project.get_project_code())
        
        return labels, values 
  

    def add_float_items(self):
        pass
   

    def get_title(self):
        mode = self.get_option("mode")
        if mode == "input":
            return "Input"

        widget = SpanWdg()
        #widget.add(super(AssetLoaderWdg,self).get_title())
        
        widget.set_attr("nowrap", "1")
        load_button = ProdIconButtonWdg("Load Shot")
        load_button.set_id(self.LOAD_BUTTON_ID) 
        prefix = self.PREFIX
        load_button.add_behavior(
                {'type': "click_up", 
                "cbjs_action":
                "setTimeout(function() {load_selected_snapshots_cbk('%s', '%s', bvr)}, 200) " \
                % (prefix, self.CB_NAME) \
                })
        widget.add(load_button)

        #multiplier = HiddenWdg()
        #multiplier.set_id("load_multiplier")
        #multiplier.set_value("1")
        #widget.add( multiplier )
        # xsi doesn't reference shot in now
        if WebContainer.get_web().get_selected_app() != 'XSI':
            update_button = ProdIconButtonWdg("Update", long=True)
           
            prefix = self.PREFIX
            update_button.add_event("onclick", "setTimeout( function() {py_replace_reference('%s','%s')}, 200)" % \
                (prefix, self.CB_NAME))

            widget.add(update_button)


        # Get the session. This overrides what is run in preprocess()
        self.session = SessionContents.get(asset_mode=True)

        return widget




class SubRefWdg(AjaxWdg):
    '''Widget that draws the hierarchical references of the asset of interest'''
    CB_NAME = "load_snapshot"

    def init(self):
        self.version_wdgs = []

    def set_info(self, snapshot, session, namespace):
        self.session = session
        self.snapshot = snapshot
        self.namespace = namespace

        # handle ajax settings
        self.widget = DivWdg()
        self.set_ajax_top(self.widget)
        self.set_ajax_option("namespace", self.namespace)
        self.set_ajax_option("snapshot_code", self.snapshot.get_code())

    def init_cgi(self):
        web = WebContainer.get_web()
        snapshot_code = web.get_form_value("snapshot_code")
        namespace = web.get_form_value("namespace")

        snapshot = Snapshot.get_by_code(snapshot_code)
        session = SessionContents.get(asset_mode=True)

        self.set_info(snapshot, session, namespace)

    def get_version_wdgs(self):
        '''get a list of version wdgs'''
        if self.version_wdgs:
            return self.version_wdgs
        xml = self.snapshot.get_xml_value("snapshot")
        refs = xml.get_nodes("snapshot/file/ref")
        if not refs:
            return self.version_wdgs

       
        # handle subreferences
        for ref in refs:

            instance = Xml.get_attribute(ref, "instance")
            node_name = Xml.get_attribute(ref, "node_name")
            snapshot = Snapshot.get_ref_snapshot_by_node(ref, mode='current')
            if not snapshot:
                print "WARNING: reference in snapshot [%s] does not exist" % self.snapshot.get_code()
                continue

            #checkin_snapshot = Snapshot.get_ref_snapshot_by_node(ref)

            parent = snapshot.get_parent()
                
            asset_code = parent.get_code()

            # namespace = "veryron_rig"
            # node_name = "stool_model:furn001"
            # instance =  "stool_model"
            
            # HACK: if node name was not specified, then try to guess it
            # (for backwards compatibility)
            if not node_name: 
                node_name = self.get_node_name(snapshot, asset_code, self.namespace)
                # HACK
                parts = node_name.split(":")
                parts.insert(1, instance)
                node_name = ":".join(parts)
                print "WARNING: node_name not given: using [%s]" % node_name


            # Add the current namespace to the node 
            # in session
            checked_node_name = node_name

            # FIXME: this is Maya-specific and meant for referencing a shot
            '''
            if app_name == 'Maya':
                
                if not node_name.startswith("%s:" % self.namespace):
                    node_name = "%s:%s" % (self.namespace, node_name)
            elif app_name == "XSI":
                pass
            ''' 
            # get the latest information
            latest_version = snapshot.get_value("version")
            latest_context = snapshot.get_value("context")
            latest_revision = snapshot.get_value("revision", no_exception=True)
            latest_snapshot_type = snapshot.get_value("snapshot_type")


            # get the session information
            self.session.set_asset_mode(False)
            session_context = self.session.get_context(node_name, asset_code, latest_snapshot_type)
            session_version = self.session.get_version(node_name, asset_code, latest_snapshot_type)
            session_revision = self.session.get_revision(node_name, asset_code, latest_snapshot_type)
            #print "session: ", session_version, session_context, session_revision
            # add to outdated ref list here
            version_wdg = LatestVersionContextWdg()
            data = {'session_version': session_version, \
                'session_context': session_context,  \
                'session_revision': session_revision,  \
                'latest_context': latest_context, \
                'latest_version': latest_version, \
                'latest_revision': latest_revision,\
                'asset_code': asset_code,\
                'node_name': checked_node_name ,\
                'sobject': parent,\
                'snapshot': snapshot}

            version_wdg.set_options(data)
            self.version_wdgs.append(version_wdg)

            # This only adds when it is being drawn with the corresponding process selected
            # so not that useful, commented out for now.
            #if version_wdg.get_status() not in [ VersionWdg.NOT_LOADED, VersionWdg.UPDATED]:
            #    SubRefWdg.add_outdated_ref(version_wdg)

        return self.version_wdgs

    def get_display(self):

        assert self.snapshot
        assert self.session
        assert self.namespace

        widget = self.widget
        

        if not self.is_ajax():
            return widget
 
        #widget.add_style("border-style: solid")
        #widget.add_style("padding: 10px")
        #widget.add_style("position: absolute")
        #widget.add_style("margin-left: 50px")
        widget.add_style("text-align: left")
        table = Table()
        
        version_wdgs = self.get_version_wdgs()

        for version_wdg in version_wdgs:
            # draw the info
            table.add_row()
            #checkbox = CheckboxWdg(self.CB_NAME)
            #checkbox.set_option("value", "cow" )
            #table.add_cell( checkbox )

            td = table.add_cell(version_wdg)
            td.set_attr("nowrap", "1")
            latest_context = version_wdg.get_option('latest_context')
            table.add_cell(HtmlElement.b("(%s)" % latest_context))
            table.add_cell(version_wdg.get_option('asset_code'))
            node_name = version_wdg.get_option('node_name')
            table.add_cell(node_name.split(":")[0])

        widget.add("<hr size='1'>")
        widget.add("References")
        widget.add(table)

        return widget


    def get_overall_status(self):
        version_wdgs = self.get_version_wdgs()
        all_updated = True
        is_loaded = False
        for wdg in version_wdgs:
            status = wdg.get_status()
            if status != VersionWdg.NOT_LOADED:
                is_loaded = True
            if wdg.get_status() != VersionWdg.UPDATED:
                all_updated = False
                # don't use break as we need the info of all the subrefs
                continue
                
        
        if not is_loaded:
            return VersionWdg.NOT_LOADED
        elif all_updated == False:
            return VersionWdg.OUTDATED
        else: 
            return VersionWdg.UPDATED

    def get_node_name(self, snapshot, asset_code, namespace):
        ''' if possible get the node name from snapshot which is more accurate'''
        node_name = snapshot.get_node_name()

        if not node_name:
            naming = MayaNodeNaming()
            app_name = WebContainer.get_web().get_selected_app() 
            if app_name == "Maya":
                naming = MayaNodeNaming()
            elif app_name == "XSI":
                naming = XSINodeNaming()
            elif app_name == "Houdini":
                naming = HoudiniNodeNaming()
            naming.set_asset_code(asset_code)
            naming.set_namespace(namespace)

            node_name = naming.build_node_name()
        return node_name

    def add_outdated_ref(version_wdg):
        Container.append_seq('SubRef_outdated', version_wdg)
    add_outdated_ref = staticmethod(add_outdated_ref)

    def get_outdated_ref():
        return Container.get('SubRef_outdated')
    get_outdated_ref = staticmethod(get_outdated_ref)

