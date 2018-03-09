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

__all__ = ['AppSObjectCheckinWdg']

from pyasm.prod.biz import SessionContents
from tactic.ui.cgapp import CheckinWdg
#from pyasm.prod.web import MayaCheckinWdg
from pyasm.web import DivWdg, SpanWdg,  Table, HtmlElement, FloatDivWdg, WebContainer, WidgetSettings, Widget
from pyasm.widget import SwapDisplayWdg, SelectWdg, CheckboxWdg, ProdIconButtonWdg, HiddenWdg, ThumbWdg, IconWdg, TextAreaWdg
from pyasm.search import SObject, Search
from pyasm.biz import Project, Pipeline, Snapshot
from pyasm.common import Common, Xml
from tactic.ui.widget import TextBtnWdg, ActionButtonWdg

class AppSObjectCheckinWdg(CheckinWdg):

    PUBLISH_BUTTON = 'Publish'
    ARGS_KEYS = {

        "search_type": {
            'description': "search type that this panel works with",
            'type': 'TextWdg',
            'order': 0,
            'category': '1. Required'
        },
       "texture_search_type": {
            'description': "texture search type that this panel works with",
            'type': 'TextWdg',
            'order': 1,
            'category': '1. Required'
        },
        "process": {
            'description': "The process this panel is looking at e.g. {@GET(state.process)}",
            'type': 'TextWdg',
            'order': 1,
            'category': '2. Options'
        }

       }

    def list_references(self):
        '''lists whether references can be checked in with this widget'''
        return False
    
    def get_context_data(self):
        process = self.process_select.get_value()
        labels, values = super(AppSObjectCheckinWdg,self).get_context_data(\
            self.search_type, process)

        return labels, values



    def get_display(self):


        self.search_type = self.kwargs.get('search_type')
        self.texture_search_type = self.kwargs.get('texture_search_type')
        assert self.search_type

        app_name = WebContainer.get_web().get_selected_app()
        # add an outside box


        top = DivWdg(css='spt_view_panel')
        #div = DivWdg(css="maq_search_bar")
        div = DivWdg()
        div.add_color("background", "background2", -15)
        self.set_as_panel(top)

        top.add(div)
        div.add_style("margin: 5px")

        div.add_style("padding: 10px")
        
        div.add_style("font-style: bold")



        process_div = DivWdg()
        process_div.add_style("padding-left: 10px")
        div.add(process_div)
        process_div.add( self.get_process_wdg(self.search_type))
        process_div.add( self.get_context_filter_wdg() )
        process_div.add(HtmlElement.br(clear="all")) 


        div.add( HtmlElement.br() )
        checkin_options = DivWdg(css='spt_ui_options')
        checkin_options.add_style("padding: 10px")

        swap = SwapDisplayWdg()
        #swap.set_off()
        title = SpanWdg("Check in Options")
        SwapDisplayWdg.create_swap_title(title, swap, checkin_options, is_open=False)
        div.add(swap)
        div.add(title)


        checkin_options.add( self.get_file_type_wdg() )
        checkin_options.add( self.get_snapshot_type_wdg() )
        checkin_options.add(HtmlElement.br(1)) 
        checkin_options.add( self.get_export_method_wdg() )
        checkin_options.add( self.get_checkin_as_wdg() )

        #self.add( self.get_render_icon_wdg() )

        # For different export methods
        checkin_options.add( self.get_currency_wdg() )

        checkin_options.add( self.get_reference_option())
        checkin_options.add( self.get_auto_version_wdg())
        checkin_options.add( self.get_texture_option(app=app_name))
        checkin_options.add( self.get_handoff_wdg())
       
        if not self.context_select.get_value(for_display=True):
            self.add(DivWdg('A context must be selected.', css='warning'))
            return

        div.add(checkin_options)
      
        
        top.add( self.get_introspect_wdg() )
        top.add(HtmlElement.br(2))
        
        # create the interface
        table = Table()
        table.set_max_width()
        #table.set_class("table")
        table.add_color('background','background2') 
        #table.add_style('line-height','3.0em')
        #table.add_row(css='smaller')
        tr = table.add_row(css='smaller')
        tr.add_style('height', '3.5em')
        table.add_header("&nbsp;")
        table.add_header("&nbsp;")
        th = table.add_header("Instance")
        th.add_style('text-align: left')
        table.add_header(self.get_checkin())
        table.add_header("Sandbox")
        tr.add_color('background','background2', -15)
        

        # get session and handle case where there is no session
        self.session = SessionContents.get()
        if self.session == None:
            instance_names = []
            asset_codes = []
            node_names = []
        else:
            instance_names = self.session.get_instance_names()
            asset_codes = self.session.get_asset_codes()
            node_names = self.session.get_node_names()

        # get all of the possible assets based on the asset codes
        search = Search(self.search_type)
        search.add_filters("code", asset_codes)
        assets = search.get_sobjects()
        assets_dict = SObject.get_dict(assets, ["code"])

        if self.session:
            self.add("Current Project: <b>%s</b>" % self.session.get_project_dir() )
        else:
            self.add("Current Project: Please press 'Introspect'")


        count = 0
        for i in range(0, len(node_names) ):
            node_name = node_names[i]
            if not self.session.is_tactic_node(node_name) and \
                not self.session.get_node_type(node_name) in ['transform','objectSet']:
                    continue
            instance_name = instance_names[i]

            # backwards compatible:
            try:
                asset_code = asset_codes[i]
            except IndexError, e:
                asset_code = instance_name

            # skip if this is a reference
            if self.list_references == False and \
                    self.session.is_reference(node_name):
                continue

            table.add_row()


            # check that this asset exists
            asset = assets_dict.get(asset_code)
            if not asset:
                continue
           
            # list items if it is a set
            if asset.get_value('asset_type', no_exception=True) in ["set", "section"]:
                self.current_sobject = asset
                self.handle_set( table, instance_name, asset, instance_names)
                count +=1
            # if this asset is in the database, then allow it to checked in
            if asset:
                if self.session.get_snapshot_code(instance_name, snapshot_type='set'):
                    continue

                # hack remember this
                self.current_sobject = asset
                self.handle_instance(table, instance_name, asset, node_name)

            else:
                table.add_blank_cell()
                table.add_cell(instance_name)


            count += 1

        if count == 0:
            table.add_row_cell("<center><h2>No assets in session to checkin</h2></center>")

        top.add(table)

        if not self.session:
            return


        non_tactic_nodes = self.session.get_instance_names(is_tactic_node=False)
        title = HtmlElement.b("Unknown List")
        swap = SwapDisplayWdg.get_triangle_wdg()

        div = DivWdg(id="unknown list")
        
        top.add(swap)
        top.add(title)

        SwapDisplayWdg.create_swap_title( title, swap, div) 
        unknown_table = Table()
        unknown_table.add_color('background','background2')
        unknown_table.set_max_width()
        div.add(unknown_table)

        
        for instance in non_tactic_nodes:
            self.handle_unknown_instance(unknown_table, instance)
        
        top.add(div)
        return top


    def get_file_type_wdg(self):
        '''drop down which selects which file type to export to'''
        # add a filter
        div = DivWdg()

        filter_div = FloatDivWdg(HtmlElement.b("File Type:"), width="15em")
        div.add(filter_div)

        select = SelectWdg()
        select.set_name("file_type")
        select.set_id("file_type")

        app = WebContainer.get_web().get_selected_app()

        if app == 'Maya':
            select.set_option("values", "mayaAscii|mayaBinary|obj|collada")
            select.set_option("labels", "Maya Ascii (.ma)|Maya Binary (.mb)|Wavefront .obj|Collada (.dae)")
        elif app == 'Houdini':
            select.set_option("values", "otl")
            select.set_option("labels", "Houdini Digital Asset(.otl)")
        elif app == 'XSI':
            select.set_option("values", "emdl|dotXSI|obj")
            select.set_option("labels", "3D Model (.emdl)|SoftImage dotXSI (.xsi)|Wavefront .obj")
        else:
            select.set_option("values", "mayaAscii|mayaBinary|obj|collada")
            select.set_option("labels", "Maya Ascii (.ma)|Maya Binary (.mb)|Wavefront .obj|Collada (.dae)")

        select.add_style("font-size: 0.8em")
        select.add_style("margin-top: 5px")
        select.add_style("margin-right: 10px")
        select.set_persistence()
        
        div.add(select)
        return div



    def get_checkin(self):
        '''the button which initiates the checkin'''
        # create the button with the javascript function
        widget = Widget()
        #button = TextBtnWdg(label=self.PUBLISH_BUTTON, size='large', width='100', side_padding='20', vert_offset='-5')
        #button.get_top_el().add_class('smaller')
        button = ActionButtonWdg(title=self.PUBLISH_BUTTON, tip='Publish the selected assets')
        button.add_style('margin-bottom: 10px')
        #button.add_color("background", "background")

        hidden = HiddenWdg(self.PUBLISH_BUTTON, '')
        button.add( hidden )
       
        '''
        status_sel = SelectWdg('checkin_status', label='Status: ')
        status_sel.set_option('setting', 'checkin_status')
        status_sel.set_persist_on_submit()
        status_sel.add_empty_option('-- Checkin Status --')
        widget.add(status_sel)
        '''
        widget.add(button)

        # custom defined 
        server_cbk = "pyasm.prod.web.AssetCheckinCbk"
        #TODO: make other Publish Buttons call their own handle_input function
        exec( Common.get_import_from_class_path(server_cbk) )
        exec( "%s.handle_input(button, self.search_type, self.texture_search_type)" % server_cbk)

        return widget




    """  

    def get_export_method_wdg(self):
        '''Checkbox that determines whether to use export or file/save'''
        is_unchecked = True
        default_cb = None
        div = DivWdg()

        title = FloatDivWdg(HtmlElement.b("Export Method:"), width="15em")
        div.add(title)

        for value in ['Export', 'Save', 'Pipeline']:
            span = SpanWdg(css="med")
            checkbox = CheckboxWdg("export_method")
            
            checkbox.set_option("value", value)
            checkbox.set_persistence()
            if value == 'Export':
                default_cb = checkbox
            if checkbox.is_checked():
                is_unchecked = False
            checkbox.add_behavior({'type': 'click_up', 
                    'propagate_evt': True,
                    "cbjs_action": "spt.toggle_checkbox(bvr, '.spt_ui_options', 'export_method')"}) 
            span.add(checkbox)
            span.add(value)
            div.add(span)

        if is_unchecked:
            default_cb.set_checked()

        batch_cb = CheckboxWdg('use_batch', label='batch script')
        batch_cb.set_persistence()
        span = SpanWdg(batch_cb, css='med')
        span.add_style('border-left: 1px solid #888')
        div.add(span)
        return div

    
    """
    


    def get_render_icon_wdg(self):
        '''Checkbox determines whether to create icon'''
        div = DivWdg()
        div.add("Create Icon: ")
        checkbox = CheckboxWdg("render")
        checkbox.set_persistence()
        div.add(checkbox)
        return div


    def handle_set(self, table, instance_name,  asset,  session_instances):
        asset_code = asset.get_code()
        
        # get all of the reference instances from the latest published
        snapshot = Snapshot.get_latest_by_sobject(asset, "publish")
        # if there is no publish snapshot, then this is definitely not
        # a set, so handle it like an instance
        if not instance_name in session_instances:
            return
        if not snapshot:
            self.handle_instance(table, instance_name, asset)
            return


        xml = snapshot.get_xml_value("snapshot")

        # skip if none are in session
        set_instances = xml.get_values("snapshot/ref/@instance")

        # TODO should get it based on the set's asset code so that
        # if the sesssion's set is older, it will still work
        session_set_items = self.session._get_data().get_nodes_attr(\
            "session/node[@set_asset_code='%s']" %asset_code, 'instance')
        count = 0

        set_instances_in_session = []
        set_instances_not_in_session = []
        for set_instance in set_instances:

            # backwards compatible:
            tmp_set_instance = set_instance
            if set_instance.find(":") != -1:
                print "WARNING: snapshot '%s' has deprecated maya instance names" % snapshot.get_code()
                set_instance, tmp = set_instance.split(":")

            # make sure the set_instance comes from this set
            if set_instance in session_set_items:
                count += 1
                set_instances_in_session.append(tmp_set_instance)
            
            else:
                set_instances_not_in_session.append(tmp_set_instance)

        if count == 0:
            return

        self.handle_instance(table, instance_name, asset)
    
        # display all of the set instance that are in session
        for set_instance in set_instances_in_session:

            ref_snapshot = snapshot.get_ref_snapshot("instance",
                set_instance)
            ref_asset = ref_snapshot.get_sobject()

            # backwards compatible
            if set_instance.find(":") != -1:
                print "WARNING: snapshot '%s' has deprecated maya instance names" % snapshot.get_code()
                set_instance, tmp = set_instance.split(":")

            self.handle_instance(table, set_instance, ref_asset, publish=False)

        widget = Widget("&nbsp;")
        if set_instances_not_in_session:
            widget = Widget()
            widget.add(IconWdg("warning", icon=IconWdg.ERROR))
            widget.add("missing set items from last publish")
        th, td = table.add_row_cell(widget)
        

        for set_instance in set_instances_not_in_session:

            ref_snapshot = snapshot.get_ref_snapshot("instance",
                set_instance)
            ref_asset = ref_snapshot.get_sobject()

            # backwards compatible
            if set_instance.find(":") != -1:
                print "WARNING: snapshot '%s' has deprecated maya instance names" % snapshot.get_code()
                set_instance, tmp = set_instance.split(":")

            self.handle_missing_instance(table, set_instance, ref_asset)

        if set_instances_not_in_session:
            table.add_row_cell("&nbsp;")


    def handle_instance(self, table, instance, asset, node_name='', publish=True, allow_ref_checkin=False):

        # handle the case where asset is not defined
        if not asset:
            table.add_row()
            table.add_blank_cell()
            table.add_blank_cell()

            # FIXME: Maya specific
            parts = instance.split(":")
            instance_name = parts[0]
            asset_code = parts[1]

            
            if instance_name == asset_code:
                table.add_cell(instance_name)
            else:
                table.add_cell(instance)
            td = table.add_cell()
            td.add("< %s node >" % self.session.get_node_type(instance_name))
            table.add_blank_cell()
            return 

        # get the pipeline for this asset and handlers for the pipeline
        process_name = self.process_select.get_value() 
        handler_hidden = self.get_handler_input(asset, process_name)
        pipeline = Pipeline.get_by_sobject(asset) 
        



        # TEST: switch this to using node name instead, if provided
        if node_name:
            instance_node = self.session.get_node(node_name)
        else:
            instance_node = self.session.get_node(instance)

        if instance_node is None:
            return
        if Xml.get_attribute(instance_node,"reference") == "true":
            is_ref = True
        else:
            is_ref = False

        namespace = Xml.get_attribute(instance_node, "namespace")
        if not namespace:
            namespace = instance

        asset_code = asset.get_code()
        is_set = False
        if asset.get_value('asset_type', no_exception=True) in ['set','section']:
            is_set = True
            
        tr = table.add_row()
        
        if is_set:
            tr.add_class("group")

        if publish and (allow_ref_checkin or not is_ref):
            checkbox = CheckboxWdg("asset_instances")
            if is_set:
                checkbox = CheckboxWdg("set_instances")
               
            checkbox.set_option("value", "%s|%s|%s" % \
                        (namespace, asset_code, instance) )
            checkbox.set_persist_on_submit()

            td = table.add_cell(checkbox)
            
        else:
            td = table.add_blank_cell()

        # only one will be added even if there are multiple
        if handler_hidden:
            td.add(handler_hidden)

        # add the thumbnail
        thumb = ThumbWdg()
        thumb.set_name("images")
        thumb.set_sobject(asset)
        thumb.set_icon_size(60)
        table.add_cell(thumb)


        info_wdg = Widget()
        info_wdg.add(HtmlElement.b(instance))

        if not node_name:
            node_name = '%s - %s' %(asset_code, asset.get_name()) 
        info_div = DivWdg(node_name)
        info_div.add_style('font-size: 0.8em')
        info_wdg.add(info_div)
        info_div.add(HtmlElement.br(2))
        if pipeline:
            info_div.add(pipeline.get_code())
        table.add_cell(info_wdg)

        #  by default can't checkin references
        if not allow_ref_checkin and is_ref:
            #icon = IconWdg("error", IconWdg.ERROR)
            #td = table.add_cell(icon)
            td = table.add_cell()
            td.add(HtmlElement.b("Ref. instance"))
            '''
            import_button = ProdIconButtonWdg('import')
            import_button.add_event('onclick', "import_instance('%s')"  %instance)
            td.add(import_button)
            '''
            table.add_cell(self.get_save_wdg(self.current_sobject) )

        elif publish:
            textarea = TextAreaWdg()
            textarea.set_persist_on_submit()
            textarea.set_name("%s_description" % instance)
            textarea.set_attr("cols", "35")
            textarea.set_attr("rows", "2")
            table.add_cell(textarea)
            table.add_cell(self.get_save_wdg(self.current_sobject) )
        else:
            table.add_blank_cell()
            table.add_blank_cell()



    def handle_missing_instance(self, table, instance, asset):

        asset_code = asset.get_code()

        table.add_row()

        table.add_blank_cell()

        # add the thumbnail
        thumb = ThumbWdg()
        thumb.set_name("images")
        thumb.set_sobject(asset)
        thumb.set_icon_size(45)
        table.add_cell(thumb)


        info_wdg = Widget()
        info_wdg.add("<b>%s</b>" % instance)
        info_wdg.add("<div style='font-size: 0.8em'>%s</div>" % asset_code )
        table.add_cell(info_wdg)

        table.add_blank_cell()

    def handle_unknown_instance(self, table, instance):
        '''handle unassigned or non-tactic nodes'''

        table.add_row()
        table.add_blank_cell()
        icon = IconWdg("unknown", icon=IconWdg.UNKNOWN)
        table.add_cell(icon)

        info_wdg = Widget()
        info_wdg.add("<b>%s</b>" % instance)
        table.add_cell(info_wdg)
        table.add_blank_cell()
        table.add_blank_cell()


