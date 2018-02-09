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

__all__ = ['MayaCheckinWdg', 'MayaAssetCheckinWdg','MayaAnimCheckinWdg','MayaShotCheckinWdg', 'CustomCheckinWdg']

import binascii, re

from pyasm.common import Container
from pyasm.biz import Pipeline
from pyasm.widget import *
from pyasm.prod.biz import *
from pyasm.prod.load import *
from pyasm.web import *
from pyasm.search import SObject
from shot_navigator_wdg import *
from prod_wdg import *
from pyasm.biz import Project, Snapshot
from asset_filter_wdg import ContextFilterWdg, ProcessFilterWdg
from prod_input_wdg import ProcessSelectWdg
#from tactic.ui.panel import ConnectorSelectWdg
from tactic.ui.common import BaseRefreshWdg

class MayaCheckinWdg(BaseRefreshWdg):

    def init(self):
        name = ""
        self.context_select = None
        self.current_sobject = None
        #super(MayaCheckinWdg, self).__init__(name)
        
    def get_context_data(self,search_type='', process=''):
        '''get the labels and values of contexts that can be checked in with this widget'''

        # TODO: this also shows input contexts ... it should only show output
        # contexts
        if not search_type:
            search_type = self.SEARCH_TYPE

        pipelines = Pipeline.get_by_search_type(search_type, Project.get_project_code() )

        if not pipelines:
            return [], []
        # account for sub-pipeline
        if '/' in process:
            process = process.split('/', 1)[1]
        contexts = []
        for pipeline in pipelines:
            pipeline_contexts = []
            pipeline_processes = pipeline.get_process_names()
            if process:
                if process not in pipeline_processes:
                    continue
                pipeline_contexts = pipeline.get_output_contexts(process)
            else:
                pipeline_contexts = pipeline.get_all_contexts()
            for context in pipeline_contexts:
                # for now, cut out the sub_context, until the pipeline
                # completely defines the sub contexts as well
                if context.find("/") != -1:
                    parts = context.split("/")
                    context = parts[0]

                if context not in contexts:
                    contexts.append(context)

        labels = contexts
        values = contexts

        return labels, values



    def get_introspect_wdg():
        '''the button which initiates the introspection'''
        
        button = IntrospectWdg()
        
        table = Table()
        table.set_max_width()
        table.add_row()
        table.add_cell("DEPRECATED!!: do not use this widget. Use the new one under cgapp")
        td = table.add_cell()
        #td = table.add_cell( ConnectorSelectWdg() )
        td.add_style('width: 150px')

        app = WebContainer.get_web().get_selected_app()
        span = SpanWdg(app, css='small')
        td = table.add_cell(span)
        td.add_style("padding: 2px")
        icon = IconWdg(icon=eval("IconWdg.%s"%app.upper()), width='13px')
        td.add(icon)
        td.add(button)
        button = IntrospectWdg()
        button.add_style("float", "right")
        if app == 'Maya' and not Container.get('GeneralAppletWdg'):
            td.add( GeneralAppletWdg() )
            Container.put('GeneralAppletWdg', True)
        return table
    get_introspect_wdg = staticmethod(get_introspect_wdg)


    def get_process_wdg(self, search_type):
        '''this should appear in front of the context_filter_wdg'''
        div = FloatDivWdg()
        div.add_style('padding-right','10px')

        # give the opportunity to force the process
        process = self.kwargs.get("process")
        if process:
            self.process_select = SelectWdg("%s_process" % self.PUBLISH_TYPE)
            self.process_select.set_value(process)
            div.add("Process: %s" % process)
            return div
            

        self.process_select = ProcessSelectWdg(label='Process: ', \
            search_type=search_type, css='', has_empty=False, \
            name="%s_process" %self.PUBLISH_TYPE)

        self.process_select.add_empty_option('- Select -')
        self.process_select.set_persistence()
        self.process_select.add_behavior({'type' : 'change',
            'cbjs_action': '%s;%s'%(self.process_select.get_save_script(),\
                    self.process_select.get_refresh_script())
           })
        # this is only applicable in Shot Tab
        filter = Container.get('process_fitter')
        if filter:
            self.process_select.set_value(filter.get_value())
        div.add(self.process_select)
        return div

    def get_context_filter_wdg(self):
        '''drop down which selects which context to checkin'''
        # add a filter
        # use a regular SelectWdg with submit instead of FilterSelectWdg
        filter_div = FloatDivWdg("Context:")
        select_name = "%s_context" %self.PUBLISH_TYPE
        select = SelectWdg(select_name)
        
        select.add_behavior({'type' : 'change',
            'cbjs_action': "var top=spt.get_parent_panel(bvr.src_el); spt.panel.refresh(top, {'%s': bvr.src_el.value}, true)"%select_name})
        labels, values = self.get_context_data()
        select.set_option("values", "|".join(values))
        select.set_option("labels", "|".join(labels))
        select.add_style("font-size: 0.8em")
        select.add_style("margin: 0px 3px")

        # explicitly set the value
        current = select.get_value()
        if current in values:
            context = current
        elif values:
            context = values[0]
        else:
            context = ""
 
        web = WebContainer.get_web()
        web.set_form_value("%s_context" % self.PUBLISH_TYPE, context)

        select.set_value( context )

        # set it to a instance variable
        self.context_select = select

        filter_div.add(select)

        # if specified, add a sub_context
        settings = ProdSetting.get_value_by_key("%s/sub_context" % context,\
                self.SEARCH_TYPE)
        filter_div.add( "/ ")
        sub_context = None
        if settings:
            sub_context = SelectWdg("%s_sub_context" %self.PUBLISH_TYPE)
            sub_context.set_option("values", settings)
            sub_context.set_submit_onchange()
            sub_context.add_empty_option("<- Select ->")
        else:
            # provide a text field
            sub_context = TextWdg("%s_sub_context" %self.PUBLISH_TYPE)
            sub_context.set_attr('size','10') 
            
        sub_context.set_persistence()
        # saves the subcontext value
        sub_context.add_behavior({'type': 'change',
                'cbjs_action': sub_context.get_save_script()})
        filter_div.add( sub_context )
        self.sub_context_select = sub_context
        filter_div.add_style('padding-right','10px')

        return filter_div


    def get_snapshot_type_wdg(self):
        hidden = HiddenWdg("checkin_snapshot_type", "asset")
        return hidden


 
    def get_auto_version_wdg(self):

        widget = Widget()

        div = DivWdg()
        widget.add(div)

        title = FloatDivWdg(HtmlElement.b('Version:'), width = '15em')
        div.add(title)

        cb = CheckboxWdg('auto_version', label='auto version', css='med')
        cb.set_persistence()

        # FIXME: this is required for single checkbox
        if cb.is_checked(False):
            cb.set_checked()
        div.add(cb)
        hint = HintWdg("If checked, the published will be automatically versioned up, <br/>"\
                "regardless of the current file name.")
        div.add(hint)


        # add texture dependency:
        # TODO: move from here
        div = DivWdg()
        widget.add(div)

        #title = FloatDivWdg(HtmlElement.b('Textures:'), width = '15em')
        #div.add(title)

        
        
        return widget

    def get_handoff_wdg(self):
        div = DivWdg()
        div.add_style('float','right')
        hidden = HiddenWdg('use_handoff_dir')
        use_handoff_dir = ProdSetting.get_value_by_key('use_handoff_dir')
        if not use_handoff_dir:
            # put in a default
            
            ProdSetting.create('use_handoff_dir', 'false', 'string',\
                description='Use handoff dir for Asset Checkin')
        if use_handoff_dir == 'true':
            icon = IconWdg(icon=IconWdg.HANDOFF, css='small')
            icon.set_attr('title','Use handoff')
            hidden.set_value('true')
        else:
            icon = IconWdg(icon=IconWdg.UPLOAD2, css='small')
            icon.set_attr('title','Use upload')
            hidden.set_value('false')
        icon.add_style('display', 'inline')
        #div.add(SpanWdg('Handoff Dir'))
        div.add(icon)

        div.add(hidden)

        return div


    def get_save_wdg(self, sobject=None):
        '''the button which initiates a file/save in the proper directory'''
        type = "maya"
        ext = "ma"
        # HACK: Houdini HBrowser crashes with the java plugin.  Avoid
        # this for now
        app = WebContainer.get_web().get_selected_app()
            
        if app == 'Houdini':
            type = "houdini"
            return "<i>Not implemented</i>"
        elif app == 'XSI':
            type = "xsi"
            ext = "scn"
            #return "<i>Not implemented</i>"

        session = SessionContents.get()
        if not session:
            return "No session"

        if not sobject:
            asset_codes = session.get_asset_codes()

            search = Search(Asset)
            search.add_filters("code", asset_codes)
            sobjects = search.get_sobjects()
            if not sobjects:
                return "No current sobjects"
            sobject = sobjects[0]


        asset_code = sobject.get_code()
        search_key = sobject.get_search_key()


        span = SpanWdg()
        

        #current_file_name = session.get_file_name()
        #base_name, tmp_ext = os.path.splitext(current_file_name)
        #if not current_file_name or base_name in ['Untitled','untitled']:
        current_file_name = "%s_v001.%s" % (asset_code, ext)


        # get the context and sub_context
        context = self.context_select.get_value(for_display=True)
        sub_context = self.sub_context_select.get_value()
        if sub_context:
            context = "%s/%s" % (context, sub_context)

        # Build sandbox_dir with a fake snapshot
        process = self.process_select.get_value()
        if not process or process.count(','):
            return HtmlElement.i("No process selected")

        snapshot = Snapshot.get_latest_by_sobject(sobject, context)
        version = ''

        virtual_snapshot = Snapshot.create_new()
        virtual_snapshot_xml = '<snapshot process=\'%s\'><file type=\'%s\'/></snapshot>' % (process, type)
        virtual_snapshot.set_value("snapshot", virtual_snapshot_xml)
        virtual_snapshot.set_value("context", context)
        virtual_snapshot.set_sobject(sobject)

        if snapshot:
            version = snapshot.get_value('version')
        else:
            version = 0
        virtual_snapshot.set_value('version', version+1)

        sandbox_dir = virtual_snapshot.get_sandbox_dir()
       
        file_naming = Project.get_file_naming()
        file_naming.set_sobject( sobject )
        file_naming.set_snapshot( virtual_snapshot )
        
        #node_naming = Project.get_naming("node")
        #file_name = node_naming.get_sandbox_file_name( \
        #    current_file_name, context=context,\
        #    sandbox_dir=sandbox_dir, file_naming=file_naming )
        file_name = file_naming.get_sandbox_file_name(current_file_name, context=context,\
            sandbox_dir=sandbox_dir)
        # set project button
        env_button = IconButtonWdg( "Set Project: %s" % sandbox_dir, IconWdg.SET_PROJECT, False)
        env_button.add_event("onclick", "app_set_user_environment('%s','%s')" % (sandbox_dir,file_name) )
        env_button.add_class('small')
        span.add(env_button)

        # explore button
        open_button = IconButtonWdg( "Explore: %s" % sandbox_dir, IconWdg.LOAD, False)
        open_button.add_event("onclick", "app_explore('%s')" % sandbox_dir)
        open_button.add_class('small')
        span.add(open_button)
        
       
        # save button
        path = "%s/%s" % (sandbox_dir, file_name)
        # mask the version as this is determined on client side
        pattern = re.compile( r'v(\d+)')
        mod_file_name = pattern.sub('vXXX', file_name)
        button = IconSubmitWdg("Save in sandbox as %s" % mod_file_name, IconWdg.SAVE, False)
        button.add_event("onclick", "app_save_sandbox_file('%s');introspect()" % path)
        button.add_class('small')
        span.add(button)
        return span

    def get_reference_option(self):
        div = DivWdg()
        title = FloatDivWdg(HtmlElement.b('Unknown References:'), width = '15em')
        div.add(title)

        for value in ['ignore']:
            checkbox = CheckboxWdg("unknown_ref", label=value, css='med')
            id = checkbox.generate_unique_id()
            checkbox.set_id(id)
            checkbox.set_persistence()
            checkbox.set_option("value", value)
            # FIXME: this is required for single checkbox
            if checkbox.is_checked(False):
                checkbox.set_checked()

            div.add(checkbox)

        return div

    def get_currency_wdg(self):
        '''Checkbox that determines whether this check is to be the current'''
        div = DivWdg()
        title = FloatDivWdg(HtmlElement.b('Set as Current:'), width = '15em')
        div.add(title)

 

        is_unchecked = True
        default_cb = None
        for value in ['True', 'False']:
            span = SpanWdg(css="med")
            checkbox = CheckboxWdg("currency")
            id = checkbox.generate_unique_id()
            checkbox.set_id(id)
            
            if value == 'True':
                default_cb = checkbox
            checkbox.set_option("value", value)
            checkbox.set_persistence()
            if checkbox.is_checked():
                is_unchecked = False
            checkbox.add_behavior({'type': 'click_up', 
                    'propagate_evt': True,
                    "cbjs_action": "get_elements('currency').check_me('%s');" %(id)})  
            span.add(checkbox)
            span.add(value)
            div.add(span)

        if is_unchecked:
            default_cb.set_checked()
        return div


    def get_checkin_as_wdg(self):
        '''Checkbox that determines whether to use export or file/save'''
        is_unchecked = True
        default_cb = None
        div = DivWdg()

        title = FloatDivWdg(HtmlElement.b("Check in as:"), width="15em")
        div.add(title)

        for value in ['Version', 'Revision']:
            span = SpanWdg(css="med")
            checkbox = CheckboxWdg("checkin_as")
            id = checkbox.generate_unique_id()
            checkbox.set_id(id)
            
            checkbox.set_option("value", value)
            checkbox.set_persistence()
            if value == 'Version':
                default_cb = checkbox
            if checkbox.is_checked():
                is_unchecked = False
            checkbox.add_behavior({'type': 'click_up', 
                    'propagate_evt': True,
                    "cbjs_action": "get_elements('checkin_as').check_me('%s');" %(id)})  
            span.add(checkbox)
            span.add(value)
            div.add(span)

        if is_unchecked:
            default_cb.set_checked()
        return div

    def get_texture_option(self, show_texture_match=True):
        '''Checkbox that determines different texture options'''
        is_unchecked = True
        default_cb = None

        div = DivWdg()    
        div.add(FloatDivWdg(HtmlElement.b("Texture: "), width='15em'))

        tex_handle = ProdSetting.get_value_by_key('handle_texture_dependency')
        if not tex_handle:
            ProdSetting.create('handle_texture_dependency', 'true', 'string',\
                description='handle texture dependency')
        
        if tex_handle == 'optional':
            hidden = CheckboxWdg('handle_texture_dependency', label="handle-texture", css='med')
            hidden.set_persistence()
            hidden.set_default_checked()
            if hidden.is_checked(False):
                hidden.set_checked()
        elif tex_handle == 'true':
            hidden = HiddenWdg('handle_texture_dependency', 'true')
            span = SpanWdg(IconWdg(icon=IconWdg.CHECK))
            span.add('handling enabled')
            span.add_style('padding-left: 12px')
            div.add(span)
        else:
            hidden = HiddenWdg('handle_texture_dependency', 'false')
            span = SpanWdg(IconWdg(icon=IconWdg.INVALID))
            span.add('handling disabled')
            span.add_style('padding-left: 12px')
            div.add(span)
         
        #hidden.set_value(tex_handle)
        div.add(hidden)

        app = WebContainer.get_web().get_selected_app()
        if app == 'Maya' or not show_texture_match or tex_handle not in ['true','optional']:
            return div

        match_span = SpanWdg('Match method:', css='small')
        match_span.add_style('border-left: 1px solid #888')
        match_span.add_style('margin-left: 12px')

        div.add(match_span)
        for value in ['md5', 'file_name']:
            span = SpanWdg(css="med")
            checkbox = CheckboxWdg("texture_match")
            id = checkbox.generate_unique_id()
            checkbox.set_id(id)
            
            checkbox.set_option("value", value)
            checkbox.set_persistence()
            if value == 'md5':
                default_cb = checkbox
            if checkbox.is_checked():
                is_unchecked = False
            checkbox.add_behavior({'type': 'click_up', 
                    'propagate_evt': True,
                    "cbjs_action": "get_elements('texture_match').check_me('%s')" %id})
            span.add(checkbox)
            span.add(value)
            match_span.add(span)

        if is_unchecked:
            default_cb.set_checked()

        return div
    
    def get_handler_input(self, asset, process_name):
        '''get the handler input for client side operation during checkin'''
        pipeline = Pipeline.get_by_sobject(asset)
        
        # handle the action nodes, avoid duplicate handler_hidden
        
        handler_hidden = None
        if asset.get_code() not in Container.get_seq('handler_asset'):
            Container.append_seq('handler_asset', asset.get_code() )
            handler_hidden = HiddenWdg("handler_%s" % asset.get_code() )
            handler_values = []
            if pipeline and process_name:
                process = pipeline.get_process(process_name)
                if process:
                    action_nodes = process.get_action_nodes(scope="client")
                    for action_node in action_nodes:
                        event_name = Xml.get_attribute(action_node, "event")
                        action_handler = Xml.get_attribute(action_node, "class")
                        handler_values.append("%s=%s" % (event_name, action_handler))
            handler_hidden.set_value("|".join(handler_values) )
        return handler_hidden

class MayaAssetCheckinWdg(MayaCheckinWdg):

    PUBLISH_BUTTON = 'Publish'
    PUBLISH_TYPE = "asset"
    SEARCH_TYPE = "prod/asset"
    
   

    def list_references(self):
        '''lists whether references can be checked in with this widget'''
        return False
    
    def get_context_data(self):
        process = self.process_select.get_value()
        labels, values = super(MayaAssetCheckinWdg,self).get_context_data(\
            "prod/asset", process)

        return labels, values



    def init(self):
        #help = HelpItemWdg('Checkin', 'The Checkin tab lets you publish assets in the session of their 3D applications. Among many options, you can choose to [Export] or [Save] the assets checked in the list. You can also perform incremental saves or access your sandbox for individual assets from here.')

        # add an outside box
        div = DivWdg(css="maq_search_bar")
        self.add(div)
        div.add_style("margin: 5px")

        div.add_style("padding: 10px")
        div.add_style("background: black")
        div.add_style("font_style: bold")


        #div.add(help)

        process_div = DivWdg()
        process_div.add_style("padding-left: 10px")
        div.add(process_div)
        process_div.add( self.get_process_wdg('prod/asset'))
        process_div.add( self.get_context_filter_wdg() )
        process_div.add(HtmlElement.br(clear="all")) 


        div.add( HtmlElement.br() )
        checkin_options = DivWdg()
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
        checkin_options.add( self.get_texture_option())
       
        if not self.context_select.get_value(for_display=True):
            self.add(DivWdg('A context must be selected.', css='warning'))
            return

        div.add(checkin_options)
      
        
        #self.add(HtmlElement.br())
        self.add( self.get_introspect_wdg() )
        self.add( self.get_handoff_wdg())
        self.add(HtmlElement.br(2))
        # create the interface
        table = Table()
        table.set_max_width()
        table.set_class("table")
        table.add_style('line-height','2.4em')
        table.add_row(css='smaller')
        table.add_header("&nbsp;")
        table.add_header("&nbsp;")
        table.add_header("Instance")
        table.add_header(self.get_checkin())
        table.add_header("Sandbox")
        

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
        search = Search("prod/asset")
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
            if asset.get_asset_type() in ["set", "section"]:
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

        self.add(table)

        if not self.session:
            return


        non_tactic_nodes = self.session.get_instance_names(is_tactic_node=False)
        title = HtmlElement.b("Unknown List")
        swap = SwapDisplayWdg.get_triangle_wdg()

        div = DivWdg(id="unknown list")
        
        self.add(swap)
        self.add(title)

        SwapDisplayWdg.create_swap_title( title, swap, div) 
        unknown_table = Table(css='table')
        unknown_table.set_max_width()
        div.add(unknown_table)

        
        for instance in non_tactic_nodes:
            self.handle_unknown_instance(unknown_table, instance)
        
        self.add(div)


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
        select.set_value( WidgetSettings.get_wdg_value(self,"file_type") )

        div.add(select)
        return div



    def get_checkin(self):
        '''the button which initiates the checkin'''
        # create the button with the javascript function
        widget = Widget()
        button = ProdIconButtonWdg(self.PUBLISH_BUTTON)
        hidden = HiddenWdg(self.PUBLISH_BUTTON, '')
        button.add( hidden )
        button.add_style('font-size', '1.0em')
       
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
        exec( "%s.handle_input(button)" % server_cbk)


        # add the command that this button executes
        # TODO: does this make any sense anymore?
        """
        WebContainer.register_cmd(server_cbk)

        from pyasm.command import Command
        cmd = eval("%s()" % server_cbk)
        Command.execute_cmd(cmd)
        """
        return widget




      

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
            id = checkbox.generate_unique_id()
            checkbox.set_id(id)
            
            checkbox.set_option("value", value)
            checkbox.set_persistence()
            if value == 'Export':
                default_cb = checkbox
            if checkbox.is_checked():
                is_unchecked = False
            checkbox.add_behavior({'type': 'click_up', 
                    'propagate_evt': True,
                    "cbjs_action": "get_elements('export_method').check_me('%s');" %(id)}) 
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

        if not instance_node:
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
        if asset.get_asset_type() in ['set','section']:
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
            if handler_hidden:
                td.add(handler_hidden)
        else:
            table.add_blank_cell()

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
        info_div.add(HtmlElement.br())
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


    



class MayaAnimCheckinWdg(MayaAssetCheckinWdg):

    PUBLISH_TYPE = "anim"
    SEARCH_TYPE = "prod/shot_instance"
   
    def get_context_data(self):
        # may use a prod/shot_instance search_type if it gets created
        process = self.process_select.get_value()
        labels, values = MayaCheckinWdg.get_context_data(self, "prod/shot", process)
        return labels, values



    def list_references(self):
        '''lists whether references can be checked in with this widget'''
        return True


    def init(self):


        # get session and handle case where there is no session
        self.session = SessionContents.get()
        node_name_dict = {}

        if self.session == None:
            session_instances = []
            asset_codes = []
            node_names = []
        else:
            session_instances = self.session.get_instance_names(is_tactic_node=True)
            asset_codes = self.session.get_asset_codes()
            node_names = self.session.get_node_names(is_tactic_node=True)
            for idx, node_name in enumerate(node_names):
                node_name_dict[session_instances[idx]] = node_name

        # display the ui
        div = DivWdg()
        div.add_style("margin: 5px")
        div.add_style("padding: 10px")
        div.add_style("background: black")
        div.add_style("font_style: bold")

        shot_navigator = ShotNavigatorWdg()
        div.add(shot_navigator)

        refresh_button = IconButtonWdg("Refresh", icon=IconWdg.REFRESH)
        refresh_button.add_behavior({'type': 'click', 
            'cbjs_action':  "var top=bvr.src_el.getParent('.spt_main_panel');spt.panel.refresh(top, {}, true)"})
        
        div.add(SpanWdg(refresh_button, css='small'))
        self.add(div)
        shot = shot_navigator.get_shot()

        # TODO: add selected to shot
        '''
        add_selected = SubmitWdg("Add Selected To Shot")
        add_selected.add_event("onclick", "introspect_select()")
        add_selected.add_style("float", "right")
        self.add(add_selected)
        self.add("<br/>")
        '''


        if not session_instances:
            # it only warns if there is nothing loaded at all
            self.add(DivWdg("No shot instances found in session!", css='warning'))
            return 
        
        div.add(HtmlElement.br(2))
        div.add( self.get_process_wdg('prod/shot')) 
        div.add( self.get_context_filter_wdg() )
        div.add(HtmlElement.br(2))

        # For different export methods
        title = SpanWdg("Check in Options")
        sub_div = DivWdg()
        sub_div.add_style('padding-left: 20px')
        export_wdg = self.get_export_method_wdg()
        sub_div.add(export_wdg)
        swap = SwapDisplayWdg()
        SwapDisplayWdg.create_swap_title(title, swap, sub_div, is_open=False)
        div.add(swap)
        div.add(title)
        div.add(sub_div)

        if not self.context_select.get_value(for_display=True):
            self.add(DivWdg('A context must be selected.', css='warning'))
            return
       
        self.add( self.get_introspect_wdg() )
        self.add( self.get_handoff_wdg())
        self.add(HtmlElement.br())
        # create the interface
        table = Table(css='table')
        table.set_max_width()
        table.add_row(css='smaller')
        table.add_style('line-height','2.4em')
        table.add_header("&nbsp;")
        table.add_header("Icon")

        table.add_header("Instance", css='right_content')
        th = table.add_header(self.get_checkin(), css='right_content')

        table.add_header("&nbsp;")
        if not shot:
            self.add (HtmlElement.b("Please create a shot first in the Admin area!") )
            return super(MayaAnimCheckinWdg,self).get_display()

        if self.session:
            self.add("Current Project: <b>%s</b>" % self.session.get_project_dir() )
        else:
            self.add("Current Project: Please press 'Introspect'")


        # go through the instances in the shot
        instances = shot.get_all_instances(include_parent=True) 
        instances = ShotInstance.filter_instances(instances, shot.get_code()) 
        

        for instance in instances:

            # HACK: remember the instance
            self.current_sobject = instance
                      
            asset = instance.get_asset()
            asset_code = asset.get_code()
            instance_name = instance.get_code()
            # list items if it is a set
            if asset.get_asset_type() in ["set", "section"]:

                # get all of the reference instances
                snapshot = Snapshot.get_latest_by_sobject(asset,"publish")
                # if there is no publish snapshot, then this is definitely not
                # a set, so handle it like an instance
                
                if not instance_name in session_instances:
                    continue
                if not snapshot:
                    self.handle_instance(table, instance_name, asset, allow_ref_checkin=True)
                    continue


                xml = snapshot.get_xml_value("snapshot")

                # skip if none are in session
                set_instances = xml.get_values("snapshot/ref/@instance")

                session_set_items = self.session._get_data().get_nodes_attr("session/node[@set_snapshot_code='%s']"\
                    %snapshot.get_code(), 'instance')
                
                count = 0

                set_instances_in_session = []
                set_instances_not_in_session = []
                # set_instance is actually a set_item here
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
                    continue

                thumb = ThumbWdg()
                thumb.set_name("images")
                thumb.set_icon_size(45)
                thumb.set_sobject(asset)
                
                set_div = DivWdg(thumb)
                set_div.add(SpanWdg(HtmlElement.b(instance_name), css='med'))
                th, td = table.add_row_cell(set_div)
                td.add_style("background-color: #f0f0f0")

                # display all of the set instance that are in session
                for set_instance in set_instances_in_session:
                    ref_snapshot = snapshot.get_ref_snapshot("instance",
                        set_instance)
                    # if retired, skip to next
                    if not ref_snapshot:
                        continue
                    ref_asset = ref_snapshot.get_sobject()

                    # backwards compatible
                    if set_instance.find(":") != -1:
                        print "WARNING: snapshot '%s' has deprecated maya instance names" % snapshot.get_code()
                        set_instance, tmp = set_instance.split(":")

                    self.handle_instance(table, set_instance, ref_asset, allow_ref_checkin=True)

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
                continue  

            else:
                if instance_name != "cull" and \
                        not instance_name in session_instances:
                    continue
                # this for regular anim publish instances
                node_name = node_name_dict.get(instance_name)
                self.handle_instance(table, instance_name, asset, node_name=node_name, \
                    allow_ref_checkin=True)
        
        self.add(table)

        shot_instance_names = [ instance.get_code() for instance in instances]

        title = HtmlElement.b("Unknown List")
        swap = SwapDisplayWdg.get_triangle_wdg()

        div = DivWdg(id="unknown list")
        
        self.add(swap)
        self.add(title)

        SwapDisplayWdg.create_swap_title( title, swap, div) 
        unknown_table = Table(css='table')
        unknown_table.set_max_width()
        div.add(unknown_table)

        self.add(div)
        for instance in session_instances:
            if instance not in shot_instance_names:
                self.handle_unknown_instance(unknown_table, instance)
        #TODO some culling functionalities to be added
        '''
        table.add_row()
        table.add_cell("Test: <b>Cull</b>")

        button = ButtonWdg("Add selected")
        tr, td = table.add_row_cell()
        td.add(button)
        button = ButtonWdg("Remove selected")
        td.add(button)
        '''

        

    


    def get_checkin(self):
        button = ProdIconButtonWdg(self.PUBLISH_BUTTON)
        hidden = HiddenWdg(self.PUBLISH_BUTTON, '')
        button.add(hidden)
        button.add_style('font-size', '1.0em')
        
        # custom defined 
        server_cbk = "pyasm.prod.web.AnimCheckinCbk"
        exec( Common.get_import_from_class_path(server_cbk) )
        exec( "%s.handle_input(button)" % server_cbk)

        # add the command that this button executes
        '''
        WebContainer.register_cmd(server_cbk)

        from pyasm.command import Command
        cmd = eval("%s()" % server_cbk)
        Command.execute_cmd(cmd)
        '''
 
        return button



    def handle_introspect(self):
        span = SpanWdg()
        button = IntrospectWdg()
        button.add_style("float", "right")
        span.add(button)
    
        # FIXME: commented out for now
        #button = IntrospectSelectWdg()
        #button.add_style("float", "right")
        #span.add(button)

        span.add_style("float", "right")
        self.add(span)



    def get_export_method_wdg(self):
        '''Checkbox that determines whether to use export or file/save'''
        is_unchecked = True
        default_cb = None
        div = DivWdg()
        div.add_style('clear','left')
        div.add("Export Method: ")

        export_options = ['Export']
        export_options.append("Pipeline")


        for value in export_options:
            span = SpanWdg(css="med")
            checkbox = CheckboxWdg("export_method")
            id = checkbox.generate_unique_id()
            checkbox.set_id(id)
            checkbox.set_option("value", value)
            checkbox.set_persistence()
            if value == 'Export':
                default_cb = checkbox
            if checkbox.is_checked():
                is_unchecked = False
            checkbox.add_behavior({'type': 'click_up', 
                    'propagate_evt': True,
                    "cbjs_action": "get_elements('export_method').check_me('%s');" %(id)}) 
            span.add(checkbox)
            span.add(value)
            div.add(span)

        if is_unchecked:
            default_cb.set_checked()
        return div






class MayaInstanceNode:

    def __init__(self, node_name):
        self.node_name = node_name

        if node_name.find(":") != -1:
            # handle bad instance names safely (no crash)
            tmp = node_name.split(":")
            self.namespace, self.asset_code = (tmp[0], tmp[1])
        else:
            self.namespace = ""
            self.asset_code = node_name

    def get_asset(self):
        asset = Asset.get_by_code(self.asset_code)
        return asset

    def get_asset_code(self):
        return self.asset_code


    def get_instance(self):
        return self.namespace
        



 
class MayaShotCheckinWdg(MayaCheckinWdg):

    PUBLISH_BUTTON = "Publish"
    PUBLISH_SET_BUTTON = "Publish Set"
    PUBLISH_TYPE = "shot"
    LOAD_TYPE = "shot"
    SEARCH_TYPE = "prod/shot"
   
    def init(self):
        self.is_refresh = self.kwargs.get('is_refresh') =='true'
        self.search_type = self.kwargs.get('search_type')
        if not self.search_type:
            self.search_type = 'prod/shot'

    def get_process_data(self):
        is_group_restricted = False
        if ProcessFilterWdg.has_restriction():
            is_group_restricted = True
        labels, values = Pipeline.get_process_select_data(self.SEARCH_TYPE, \
             project_code=Project.get_project_code(), is_group_restricted=is_group_restricted)
        return labels, values

    def get_context_data(self):
        # may use a prod/shot_instance search_type if it gets created
        process = self.process_select.get_value()
        labels, values = MayaCheckinWdg.get_context_data(self, "prod/shot", process)
        return labels, values

    def get_display(self):
        # add an outside box
        
        
        if not self.is_refresh:
            div = DivWdg()
            
            self.set_as_panel(div)
        else:
            div = Widget() 

        self.add(div)
        



        filter_div = DivWdg(css="filter_box")
        filter_div.add_style("margin-top: 10px")
        filter_div.add_style("padding: 5px")
        filter_div.add_style("background: black")
        filter_div.add_style("font_style: bold")
        div.add(filter_div)

       
        # the load and publish function are dependent on the shot_id element
        # of this Shot Navigator
        shot_navigator = ShotNavigatorWdg()
        filter_div.add(shot_navigator)

        process_filter = ProcessFilterWdg(self.get_process_data(), self.LOAD_TYPE)
        process_filter.get_value()

        refresh_button = IconButtonWdg("Refresh", icon=IconWdg.REFRESH)
        refresh_button.add_behavior({'type': 'click', 
            'cbjs_action':  "var top=bvr.src_el.getParent('.spt_main_panel');spt.panel.refresh(top, {}, true)"})
        
        filter_div.add(SpanWdg(refresh_button, css='small'))

        filter_div.add(HtmlElement.br(2))
        filter_div.add(process_filter)

       
        shot = shot_navigator.get_shot()



        if not shot:
            filter_div.add("No shots have been created.")
            return super(MayaShotCheckinWdg,self).get_display()

        
        # HACK: set the hidden so that it contains the shot_code
        hidden = HiddenWdg("shot_code", shot.get_code() )
        div.add(hidden)

        # bring in the animloader
        from app_load_wdg import MayaAnimLoadWdg
        from app_load_wdg import ShotLoadOptionsWdg
        #from app_load_wdg import AnimLoadOptionsWdg
        load_options = ShotLoadOptionsWdg()
        load_options.hide_proxy = True
        load_options.hide_dependencies = True
        div.add(load_options)
        
        widget = Widget()
        div.add(widget)
        widget.add( self.get_introspect_wdg() ) 
        widget.add( self.get_handoff_wdg())
        
        # try the old WarningReport here
        #widget.add( WarningReportWdg())
        # create the asset table
        shot_div = DivWdg() 
        shot_div.add_style("margin: 0px 0px 0px 20px")
        shot_table = TableWdg(self.SEARCH_TYPE, "load")
        shot_table.set_sobject(shot)
        shot_div.add(shot_table)
        widget.add(shot_div)


        widget.add("<hr/><br/>")


        # show instances

        show_instances_in_shot = ProdSetting.get_value_by_key("show_instances_in_shot_tab")
        if show_instances_in_shot != "false":

            instance_div = DivWdg()
            instance_div.add_style("margin-top: 10px")
            instance_div.add_style("padding: 10px")
            instance_div.add_style("background: black")
            instance_div.add_style("font_style: bold")
            widget.add(instance_div)


            title = DivWdg()
            #title.add_class("smaller")
            title.add("Asset Instances in Shot [ <b>%s</b> ]" %shot.get_code())
            instance_div.add(title)

           

            load_div = DivWdg()
            load_div.add_style("margin: 6px 0px 0px 16px")
            widget.add(load_div)
            anim_wdg = MayaAnimLoadWdg()
            anim_wdg.set_show_load_options(True)
            anim_wdg.set_show_process_filter(False)
            anim_wdg.set_show_shot_selector(False)
            load_div.add(anim_wdg)
            


        widget.add("<hr/><br/>")

        widget.add(self.get_publish_wdg(shot))

        
        return div

    def get_texture_option(self, show_texture_match=True, app='Maya'):
        '''Checkbox that determines different texture options'''
        is_unchecked = True
        default_cb = None

        div = DivWdg()    
        if app == 'XSI':
            hidden = HiddenWdg('handle_texture_dependency', 'false')
        else:
            div.add("Texture: ")
            hidden = FilterCheckboxWdg('handle_texture_dependency', label="handle_texture")
            hidden.set_default_checked()
       
            if hidden.is_checked(False):
                hidden.set_checked()

        tex_handle = ProdSetting.get_value_by_key('handle_texture_dependency')
        if not tex_handle:
            # put in a default
            ProdSetting.create('handle_texture_dependency', 'true', 'string',\
                description='handle texture dependency')
            
        #hidden.set_value(tex_handle)
        div.add(hidden)

        return div
    
    def get_publish_wdg(self, shot):
        ''' get the publish area widget '''
        widget = Widget()
        

        title = HtmlElement.h3("Publish Shot")
        title.add_class('smaller')
        widget.add(title)

        

        mode_span = SpanWdg(HtmlElement.b(' Mode: '))
        title.add_style('padding-bottom: 12px')
        select = SelectWdg("publish_mode")
        select.set_persistence()
        select.add_behavior({'type': 'change', 
            'cbjs_action': select.get_save_script()})
        select.add_style('background-color: #565f50')

        values = ['shot']
        app_name = WebContainer.get_web().get_selected_app()
        if app_name == 'Maya':
            values = ['shot','shot_set']

        select.set_option('values', values)
        select.set_option('default', 'shot')
        select.add_event('onchange', "if (this.value=='shot') {set_display_on('shot_publish');\
            set_display_off('shot_set_publish');} else {set_display_off('shot_publish');\
            set_display_on('shot_set_publish');}")
        mode_span.add(select)
        
        title.add(mode_span)
        
        # sub div
        div = DivWdg()
        div.add_style('padding-left: 20px')

        widget.add(div)

        div.add( self.get_process_wdg('prod/shot'))
        div.add( self.get_context_filter_wdg() )

        
        div.add( HtmlElement.br(2) )
        div.add( self.get_checkin_as_wdg() )
        div.add( self.get_currency_wdg() )

        if not self.context_select.get_value(for_display=True):
            widget.add(DivWdg('A context must be selected.', css='warning'))
            return widget

        div.add(HtmlElement.br())

        options_div = self.get_reference_option()
        div.add(options_div)
        
        div.add( self.get_auto_version_wdg()) 
        div.add(HtmlElement.br(2))
        div.add( self.get_texture_option(False, app=app_name))


        # draw shot set publish
        if app_name == 'Maya':
            div.add(self.get_shot_set_publish_wdg(shot, select.get_value()))

        # draw regular shot publish
        div.add(self.get_shot_publish_wdg(shot, select.get_value()))

        process_name = self.process_select.get_value() 
        handler_input = self.get_handler_input(shot, process_name)
        div.add(handler_input)
        
        return widget
        
    def get_shot_publish_wdg(self, shot, mode):
        button = ProdIconButtonWdg(self.PUBLISH_BUTTON)
        button.add_style('font-size', '1.0em')
        hidden = HiddenWdg(self.PUBLISH_BUTTON, '')
        button.add(hidden)
        """
        status_sel = SelectWdg('checkin_status', label='Status: ')
        status_sel.set_option('setting', 'checkin_status')
        status_sel.add_empty_option('-- Checkin Status --')
        status_sel.set_persist_on_submit()
        """
        # custom defined 
        server_cbk = "pyasm.prod.web.ShotCheckinCbk"
        exec( Common.get_import_from_class_path(server_cbk) )
        exec( "%s.handle_input(button, self.search_type)" % server_cbk)

        # add the command that this button executes
        '''
        WebContainer.register_cmd(server_cbk)

        from pyasm.command import Command
        cmd = eval("%s()" % server_cbk)
        Command.execute_cmd(cmd)
        '''
 
        
        table = Table(css="table")
        table.add_row(css='smaller')
        table.add_header("&nbsp;")
        table.add_style('line-height','2.4em') 
        table.add_header("Description")
        
        #th = table.add_header(status_sel)
        th = table.add_header(button)
        th.add_style('colspan','3')

        table.add_row()
        textarea = TextAreaWdg()
        textarea.set_persist_on_submit()
        textarea.set_name("%s_description" % shot.get_code() )
        textarea.set_attr("cols", "35")
        textarea.set_attr("rows", "3")

        table.add_blank_cell()
        table.add_cell(textarea)

        table.add_cell( self.get_save_wdg(shot) )

        div = DivWdg(id="shot_publish")
        if not mode or mode == 'shot':
            div.add_style('display: block')
        else:
            div.add_style('display: none')


        self.session = SessionContents.get()
        if self.session:
            div.add("Current Project: <b>%s</b>" % self.session.get_project_dir() )
        else:
            div.add("Current Project: Please press 'Introspect'")

        div.add(table)
        return div

    def get_shot_set_publish_wdg(self, shot, mode):
        # get session and handle case where there is no session
        widget = Widget()
        session = SessionContents.get()
        if session == None:
            instance_names = []
            asset_codes = []
            node_names = []
        else:
            instance_names = session.get_instance_names()
            asset_codes = session.get_asset_codes()
            node_names = session.get_node_names()

        title = HtmlElement.b('Shot Set Publish')
        div = DivWdg(id="shot_set_publish")
        if mode == 'shot_set':
            div.add_style('display: block')
        else:
            div.add_style('display: none')
        div.add(title)

       
        button = ProdIconButtonWdg(self.PUBLISH_SET_BUTTON)
        button.add_style('font-size', '1.0em')
        hidden = HiddenWdg(self.PUBLISH_SET_BUTTON, '')
        button.add(hidden)

        # custom defined 
        server_cbk = "pyasm.prod.web.ShotSetCheckinCbk"
        exec( Common.get_import_from_class_path(server_cbk) )
        exec( "%s.handle_input(button, self.search_type)" % server_cbk)

        # add the command that this button executes
        '''
        WebContainer.register_cmd(server_cbk)

        from pyasm.command import Command
        cmd = eval("%s()" % server_cbk)
        Command.execute_cmd(cmd)
        '''
 

        table = Table(css="table")
        table.add_row(css='smaller')
        table.add_style('line-height','2.4em') 
        table.add_header("&nbsp;")
        table.add_header("Description")
        
        th = table.add_header(button)
        th.add_style('colspan','3')
        th_end = table.add_header("&nbsp;")
        th_end.add_style('colspan','2')
     
        count = 0
        for i in range(0, len(node_names) ):
            node_name = node_names[i]
            if session.get_node_type(node_name) in ['objectSet'] and \
                node_name != shot.get_code():
                    self.handle_instance(session, table, node_name, shot)

        table.add_row()
        table.add_blank_cell()
        textarea = TextAreaWdg()
        textarea.set_persist_on_submit()
        textarea.set_name("%s_set_description" % shot.get_code())
        textarea.set_attr("cols", "35")
        textarea.set_attr("rows", "3")
        table.add_cell(textarea)
        table.add_blank_cell()
        #table.add_blank_cell()
        table.add_cell( self.get_save_wdg(shot) )


        div.add(table)
        widget.add(div)
        return widget

    def handle_instance(self, session, table, instance, shot, publish=True, allow_ref_checkin=False):

        instance_node = session.get_node(instance)
      
        
        if Xml.get_attribute(instance_node,"reference") == "true":
            is_ref = True
        else:
            is_ref = False

     
        tr = table.add_row()
       
        namespace = Xml.get_attribute(instance_node, "namespace")
        if not namespace:
            namespace = instance

        if publish and (allow_ref_checkin or not is_ref) :
            checkbox = CheckboxWdg("shot_set_instances")
            id = checkbox.generate_unique_id()
            checkbox.set_id(id) 
            checkbox.set_option("value", namespace )
            checkbox.add_behavior({'type': 'click_up', 
                    'propagate_evt': True,
                    "cbjs_action": "get_elements('shot_set_instances').check_me('%s');" %(id)})  
            checkbox.set_persist_on_submit()

            table.add_cell(checkbox)
        else:
            table.add_blank_cell()

      
        info_wdg = Widget()
        info_wdg.add(HtmlElement.b(instance))

        div = DivWdg(instance)
        div.add_style('font-size: 0.8em')
        info_wdg.add( div )
       
        
        #  by default can't checkin references
        if not allow_ref_checkin and is_ref:
            # FIXME: this is highly Maya specific
            # skip the set that represents the shot
            regex = '%s_.*:%s' %(shot.get_code(), shot.get_code())
            p = re.compile(r'%s' %regex)
            m = p.match(instance)
            if m:
                table.add_blank_cell()
                table.add_blank_cell()
            else:
                table.add_cell(info_wdg)
                td = table.add_cell()
                td.add(HtmlElement.b("Ref. instance"))

            '''
            import_button = ProdIconButtonWdg('import')
            import_button.add_event('onclick', "import_instance('%s')"  %instance)
            td.add(import_button)
            '''
            table.add_blank_cell()

        else:
            
            table.add_cell(info_wdg)
            table.add_blank_cell()
            table.add_blank_cell()
      

       

class SObjectCheckinWdg(MayaAssetCheckinWdg):

    def init(self):
        self.search_type = "prod/asset"

        self.add( self.get_introspect_wdg() )

        self.add( self.get_process_wdg(self.search_type))
        self.add( self.get_context_filter_wdg() )
        self.add(HtmlElement.br(2)) 
        self.add( self.get_file_type_wdg() )
        self.add( self.get_snapshot_type_wdg() )
        self.add(HtmlElement.br(2)) 
        self.add( self.get_export_method_wdg() )
        self.add( self.get_checkin_as_wdg() )
        #self.add( self.get_render_icon_wdg() )

        # For different export methods
        self.add( self.get_currency_wdg() )

        self.add( self.get_reference_option())
        if not self.context_select.get_value(for_display=True):
            self.add(DivWdg('A context must be selected.', css='warning'))
            return
        
        self.add(HtmlElement.br())


        # add the table
        self.add( self.get_instance_select_wdg() )

        if not self.session:
            return

        non_tactic_nodes = self.session.get_instance_names(is_tactic_node=False)
        title = HtmlElement.b("Unknown List")
        swap = SwapDisplayWdg.get_triangle_wdg()

        div = DivWdg(id="unknown list")
        
        self.add(swap)
        self.add(title)

        SwapDisplayWdg.create_swap_title( title, swap, div) 
        unknown_table = Table(css='table')
        unknown_table.set_max_width()
        div.add(unknown_table)

        
        for instance in non_tactic_nodes:
            self.handle_unknown_instance(unknown_table, instance)
        
        self.add(div)




    def get_instance_select_wdg(self):

        # create the interface
        table = Table()
        table.set_max_width()
        table.set_class("table")
        table.add_style('line-height','2.4em')
        table.add_row(css='smaller')
        table.add_header("&nbsp;")
        table.add_header("&nbsp;")
        table.add_header("Instance")

        button = ProdIconButtonWdg("DD Publish")
        button.add_event("onclick", "checkin_custom()")
        button.add_style('font-size', '1.0em')
        table.add_header(button)

        table.add_header("Sandbox")
        

        # get session and handle case where there is no session
        self.session = SessionContents.get()
        if self.session == None:
            asset_codes = []
            node_names = []
        else:
            sobject_codes = self.session.get_asset_codes()
            node_names = self.session.get_node_names()

        # get all of the possible assets based on the asset codes
        search = Search(self.search_type)
        search.add_filters("code", sobject_codes)
        sobjects = search.get_sobjects()
        sobjects_dict = SObject.get_dict(sobjects, ["code"])

        # show the current project
        if self.session:
            self.add("Current Project: <b>%s</b>" % self.session.get_project_dir() )
        else:
            self.add("Current Project: Please press 'Introspect'")


        count = 0
        for i, node_name in enumerate(node_names):
            if not self.session.is_tactic_node(node_name) and \
                not self.session.get_node_type(node_name) in ['transform','objectSet']:
                    continue

            table.add_row()

            sobject_code = sobject_codes[i]
            sobject = sobjects_dict.get(sobject_code)
            if not sobject:
                continue

            self.handle_instance(table, sobject, node_name)
            count += 1

        if not count:
            table.add_row_cell("<center><h2>No assets in session to checkin</h2></center>")

        return table




    def handle_instance(self, table, sobject, node_name):

        search_key = sobject.get_search_key()
        code = sobject.get_code()


        checkbox = CheckboxWdg("search_key")
        checkbox.set_option("value", search_key)
        checkbox.set_persist_on_submit()

        td = table.add_cell(checkbox)

        # add the thumbnail
        thumb = ThumbWdg()
        thumb.set_name("images")
        thumb.set_sobject(sobject)
        thumb.set_icon_size(60)
        table.add_cell(thumb)


        info_wdg = Widget()
        info_wdg.add(HtmlElement.b(code))

        info_div = DivWdg(node_name)
        info_div.add_style('font-size: 0.8em')
        info_wdg.add(info_div)
        table.add_cell(info_wdg)

        #  by default can't checkin references
        #if not allow_ref_checkin and is_ref:
        if 0:
            #icon = IconWdg("error", IconWdg.ERROR)
            #td = table.add_cell(icon)
            td = table.add_cell()
            td.add(HtmlElement.b("Ref. instance"))
            '''
            import_button = ProdIconButtonWdg('import')
            import_button.add_event('onclick', "import_instance('%s')"  %instance)
            td.add(import_button)
            '''
            table.add_cell(self.get_save_wdg(sobject) )

        else:
            textarea = TextAreaWdg()
            textarea.set_persist_on_submit()
            textarea.set_name("%s_description" % node_name)
            textarea.set_attr("cols", "35")
            textarea.set_attr("rows", "2")
            table.add_cell(textarea)
            table.add_cell(self.get_save_wdg(sobject) )



class CustomCheckinWdg(SObjectCheckinWdg):

    def init(self):
        self.search_type = "prod/asset"

        self.add( self.get_introspect_wdg() )
        self.add( self.get_process_wdg(self.search_type))
        self.add( self.get_context_filter_wdg() )
        self.add(HtmlElement.br(2)) 

        self.add( self.get_snapshot_type_wdg() )
        self.add(HtmlElement.br(3)) 

        # add the table
        self.add( self.get_instance_select_wdg() )

        if not self.session:
            return

        non_tactic_nodes = self.session.get_instance_names(is_tactic_node=False)
        title = HtmlElement.b("Unknown List")
        swap = SwapDisplayWdg.get_triangle_wdg()

        div = DivWdg(id="unknown list")
        
        self.add(swap)
        self.add(title)

        SwapDisplayWdg.create_swap_title( title, swap, div) 
        unknown_table = Table(css='table')
        unknown_table.set_max_width()
        div.add(unknown_table)

        
        for instance in non_tactic_nodes:
            self.handle_unknown_instance(unknown_table, instance)
        
        self.add(div)






