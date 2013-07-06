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

__all__ = ['CheckinWdg', 'AssetCheckinWdg','InstanceCheckinWdg','ShotCheckinWdg', 'CustomCheckinWdg']

import binascii, re

from pyasm.widget import *
from pyasm.prod.biz import *
from pyasm.prod.load import *
from pyasm.web import *
from pyasm.search import SObject
from pyasm.biz import Project
from tactic.ui.panel import TableLayoutWdg
from tactic.ui.common import BaseRefreshWdg
from tactic.ui.widget import TextBtnWdg, ActionButtonWdg


#from asset_filter_wdg import ContextFilterWdg, ProcessFilterWdg
from tactic.ui.input import ShotNavigatorWdg
from pyasm.biz import Pipeline, Snapshot
from pyasm.common import Container, Common, Xml
from pyasm.search import Search
from tactic.ui.common import BaseRefreshWdg

from connection_select_wdg import ConnectionSelectWdg
from loader_wdg import IntrospectWdg

class CheckinWdg(BaseRefreshWdg):
    PUBLISH_BUTTON = 'Publish'

    
    ARGS_KEYS = {

        "search_type": {
            'description': "search type that this panel works with",
            'type': 'TextWdg',
            'order': 0,
            'category': 'Required'
        },
      

        "texture_search_type": {
            'description': "texture search type this panel works with",
            'type': 'TextWdg',
            'order': 2,
            'category': 'Optional'
        }
    }

    def init(my):
        name = ""
        my.context_select = None
        my.current_sobject = None
        my.search_type = my.kwargs.get('search_type')
        my.texture_search_type = my.kwargs.get('texture_search_type')
 
    def get_context_data(my, search_type='', process=''):
        '''get the labels and values of contexts that can be checked in with this widget'''

        # TODO: this also shows input contexts ... it should only show output
        # contexts
        if not search_type:
            search_type = 'prod/asset'

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
        button.add_style("float", "left")
        
        table = Table()
        table.set_max_width()
        table.add_row()

        td = table.add_cell(button)
      
        return table
    get_introspect_wdg = staticmethod(get_introspect_wdg)


  

    def get_process_wdg(my, search_type):
        '''this should appear in front of the context_filter_wdg'''
        div = FloatDivWdg()
        div.add_style('padding-right','10px')

        # give the opportunity to force the process
        process = my.kwargs.get("process")
        if process:
            # add a dummy widget for retrieving the value later
            my.process_select = SelectWdg("%s_process" % search_type)
            my.process_select.set_value(process)
            process_div = DivWdg()
            process_div.add_style("font-size: 14px")
            process_div.add("Process: %s" % process)
            div.add(process_div)
            return div
            
        from pyasm.prod.web import ProcessSelectWdg
        my.process_select = ProcessSelectWdg(label='Process: ', \
            search_type=search_type, css='', has_empty=False, \
            name="%s_process" %my.search_type)

        my.process_select.add_empty_option('- Select -')
        my.process_select.set_persistence()
        my.process_select.add_behavior({'type' : 'change',
            'cbjs_action': '%s;%s'%(my.process_select.get_save_script(),\
                    my.process_select.get_refresh_script())
           })
        
        div.add(my.process_select)
        return div

    def get_context_filter_wdg(my):
        '''drop down which selects which context to checkin'''
        # add a filter
        # use a regular SelectWdg with submit instead of FilterSelectWdg
        filter_div = FloatDivWdg("Context:")
        select_name = "%s_context" %my.search_type
        select = SelectWdg(select_name)
        
        select.add_behavior({'type' : 'change',
            'cbjs_action': "var top=spt.get_parent_panel(bvr.src_el); spt.panel.refresh(top, {'%s': bvr.src_el.value}, true)"%select_name})
        labels, values = my.get_context_data()
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
        web.set_form_value("%s_context" % my.search_type, context)

        select.set_value( context )

        # set it to a instance variable
        my.context_select = select

        filter_div.add(select)

        # if specified, add a sub_context
        settings = ProdSetting.get_value_by_key("%s/sub_context" % context,\
                my.search_type)
        filter_div.add( "/ ")
        sub_context = None
        if settings:
            sub_context = SelectWdg("%s_sub_context" %my.search_type)
            sub_context.set_option("values", settings)
            sub_context.set_submit_onchange()
            sub_context.add_empty_option("<- Select ->")
            help = HintWdg('Change this selection list by modifying the Project Setting with the key [%s/sub_context]' %context)
             
        else:
            # provide a text field
            sub_context = TextWdg("%s_sub_context" %my.search_type)
            sub_context.set_attr('size','10') 
            help = HintWdg('Add a Project Setting with the key [%s/sub_context] to turn this into a selection list' %context)

            
        sub_context.set_persistence()
        # saves the subcontext value
        sub_context.add_behavior({'type': 'change',
                'cbjs_action': sub_context.get_save_script()})
        filter_div.add( sub_context )
        filter_div.add( help )
        my.sub_context_select = sub_context
        filter_div.add_style('padding-right','10px')

        return filter_div


    def get_file_type_wdg(my):
        '''drop down which selects which file type to export to'''
        # add a filter
        div = DivWdg()

        filter_div = FloatDivWdg(HtmlElement.b("File Type:"), width="15em")
        div.add(filter_div)

        select = SelectWdg("file_type")
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
        #select.set_value( WidgetSettings.get_wdg_value(my,"file_type") )
        select.set_persistence()

        div.add(select)
        return div

    def get_connection_option(my):
        '''display just the Connection Type select'''
        main_div = DivWdg()
        div = FloatDivWdg(width='15em')
        
        div.add(HtmlElement.b("Connection Type: "))
        main_div.add( div)
        main_div.add( FloatDivWdg(ConnectionSelectWdg()) )
        #main_div.add_style('width: 150px')

        app = WebContainer.get_web().get_selected_app()
        span = SpanWdg(app, css='small')
        icon = IconWdg(icon=eval("IconWdg.%s"%app.upper()), width='13px')
        icon_div = FloatDivWdg(SpanWdg(app, css='small'), width='90px')
        icon_div.add(icon)
        main_div.add(icon_div)
        return main_div

    def get_snapshot_type_wdg(my):
        hidden = HiddenWdg("checkin_snapshot_type", "asset")
        return hidden

    def get_export_method_wdg(my):
        '''Checkbox that determines whether to use export or file/save'''
        is_unchecked = True
        default_cb = None
        div = DivWdg(css='spt_input_group')

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

 
    def get_auto_version_wdg(my):

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

    def get_handoff_wdg(my):
        div = DivWdg()
        title = FloatDivWdg(HtmlElement.b('Use handoff dir:'), width = '15em')
        div.add(title)
        #div.add_style('float','right')
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
        elif use_handoff_dir == 'optional':
            
            hidden = CheckboxWdg('use_handoff_dir', label='use handoff dir', css='med')
            hidden.set_persistence()
            #hidden.set_default_checked()
            if hidden.is_checked(False):
                hidden.set_checked()

            icon = None
        else:
            icon = IconWdg(icon=IconWdg.UPLOAD2, css='small')
            icon.set_attr('title','Use upload')
            hidden.set_value('false')
        if icon:
            #icon.add_style('display', 'inline')
            div.add_style('margin', '6px 0 6px 0')
            div.add(icon)

        div.add(hidden)

        return div


    def get_save_wdg(my, sobject=None):
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
        context = my.context_select.get_value(for_display=True)
        sub_context = my.sub_context_select.get_value()
        if sub_context:
            context = "%s/%s" % (context, sub_context)

        # Build sandbox_dir with a fake snapshot
        process = my.process_select.get_value()
        if not process or process.count(','):
            return HtmlElement.i("No process selected")

        snapshot = Snapshot.get_latest_by_sobject(sobject, context)
        version = ''

        virtual_snapshot = Snapshot.create_new()
        virtual_snapshot_xml = '<snapshot process=\'%s\'><file type=\'%s\'/></snapshot>' % (process, type)
        virtual_snapshot.set_value("snapshot", virtual_snapshot_xml)
        virtual_snapshot.set_value("process", process)
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
        env_button.add_behavior({'type': "click_up",
            'cbjs_action': "app_set_user_environment('%s','%s', bvr)" % (sandbox_dir,file_name)         })
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
        button = IconButtonWdg("Save in sandbox as %s" % mod_file_name, IconWdg.SAVE, False)
        button.add_event("onclick", "app_save_sandbox_file('%s');" % path)
        button.add_class('small')
        span.add(button)
        return span

    def get_reference_option(my):
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

    def get_currency_wdg(my):
        '''Checkbox that determines whether this check is to be the current'''
        div = DivWdg(css='spt_input_group')
        title = FloatDivWdg(HtmlElement.b('Set as Current:'), width = '15em')
        div.add(title)


        span = SpanWdg(css="med")
        checkbox = CheckboxWdg("currency")

        
        checkbox.set_persistence()
        if checkbox.is_checked(False):
            checkbox.set_checked()
        
        span.add(checkbox)
        
        div.add(span)

     
        return div


    def get_checkin_as_wdg(my):
        '''Checkbox that determines whether to use export or file/save'''
        is_unchecked = True
        default_cb = None
        div = DivWdg(css='spt_input_group')

        title = FloatDivWdg(HtmlElement.b("Check in as:"), width="15em")
        div.add(title)

        for value in ['Version', 'Revision']:
            span = SpanWdg(css="med")
            checkbox = CheckboxWdg("checkin_as")
            
            checkbox.set_option("value", value)
            checkbox.set_persistence()
            if value == 'Version':
                default_cb = checkbox
            if checkbox.is_checked():
                is_unchecked = False
            checkbox.add_behavior({'type': 'click_up', 
                    'propagate_evt': True,
                     "cbjs_action": "spt.toggle_checkbox(bvr, '.spt_ui_options', 'checkin_as')"}) 
            span.add(checkbox)
            span.add(value)
            div.add(span)

        if is_unchecked:
            default_cb.set_checked()
        return div

    def get_texture_option(my, show_texture_match=True, app='Maya'):
        '''Checkbox that determines different texture options'''
        is_unchecked = True
        default_cb = None

        div = DivWdg(css='spt_input_group')
        float_div = FloatDivWdg(HtmlElement.b("Texture: "), width='15em')
        div.add(float_div)

        tex_handle = ProdSetting.get_value_by_key('handle_texture_dependency')
        if not tex_handle:
            ProdSetting.create('handle_texture_dependency', 'true', 'string',\
                description='handle texture dependency')
        
        label = 'handling texture'
        if app=='Maya':
            label = 'handling texture and geo cache'

        if tex_handle == 'optional':
            
            hidden = CheckboxWdg('handle_texture_dependency', label=label, css='med')
            hidden.set_persistence()
            hidden.set_default_checked()
            if hidden.is_checked(False):
                hidden.set_checked()
        elif tex_handle == 'true':
            hidden = HiddenWdg('handle_texture_dependency', 'true')
            span = SpanWdg(IconWdg(icon=IconWdg.CHECK))
            span.add('%s enabled'%label)
            span.add_style('padding-left: 12px')
            div.add(span)
        else:
            hidden = HiddenWdg('handle_texture_dependency', 'false')
            span = SpanWdg(IconWdg(icon=IconWdg.INVALID))
            span.add('%s disabled'%label)
            span.add_style('padding-left: 12px')
            div.add(span)
         
        #hidden.set_value(tex_handle)
        div.add(hidden)

        if app == 'Maya' or not show_texture_match or tex_handle not in ['true','optional']:
            return div

        match_span = SpanWdg('Match method:', css='small')
        match_span.add_style('border-left: 1px solid #888')
        match_span.add_style('margin-left: 12px')

        div.add(match_span)
        for value in ['md5', 'file_name']:
            span = SpanWdg(css="med")
            checkbox = CheckboxWdg("texture_match")
            
            checkbox.set_option("value", value)
            checkbox.set_persistence()
            if value == 'md5':
                default_cb = checkbox
            if checkbox.is_checked():
                is_unchecked = False
            checkbox.add_behavior({'type': 'click_up', 
                    'propagate_evt': True,
                     "cbjs_action": "spt.toggle_checkbox(bvr, '.spt_ui_options', 'texture_match')"}) 
            span.add(checkbox)
            span.add(value)
            match_span.add(span)

        if is_unchecked:
            default_cb.set_checked()

        return div
    
    def get_handler_input(my, asset, process_name):
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

    def handle_unknown_instance(my, table, instance):
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


class AssetCheckinWdg(CheckinWdg):

    def init(my):
        super(AssetCheckinWdg, my).init()
        my.is_refresh = my.kwargs.get('is_refresh') =='true'

    def list_references(my):
        '''lists whether references can be checked in with this widget'''
        return False
    
    def get_context_data(my):
        process = my.process_select.get_value()
        labels, values = super(AssetCheckinWdg,my).get_context_data(\
            my.search_type, process)

        return labels, values



    def get_display(my):
        my.search_type = my.kwargs.get('search_type')
        my.texture_search_type = my.kwargs.get('texture_search_type')
        assert my.search_type

        my.is_refresh = my.kwargs.get('is_refresh') =='true'
      
        if not my.is_refresh:
            top = DivWdg(css='spt_view_panel')
            my.set_as_panel(top)
        else:
            top = Widget() 


        # add an outside box
        div = DivWdg(css="maq_search_bar")
        div.add_color("background", "background2", -15)
        top.add(div)
        div.add_style("margin: 5px")

        div.add_style("padding: 10px")
        div.add_style("font_style: bold")



        from app_init_wdg import PyMayaInit, PyXSIInit, PyHoudiniInit
        if WebContainer.get_web().get_selected_app() == 'Maya':
            app = PyMayaInit()
        elif WebContainer.get_web().get_selected_app() == 'XSI':
            app = PyXSIInit()
        elif WebContainer.get_web().get_selected_app() == 'Houdini':
            app = PyHoudiniInit()
        div.add(app)



        #div.add(help)

        process_div = DivWdg()
        process_div.add_style("padding-left: 10px")
        div.add(process_div)
        process_div.add( my.get_process_wdg(my.search_type))
        process_div.add( my.get_context_filter_wdg() )
        process_div.add(HtmlElement.br(clear="all")) 


        div.add( HtmlElement.br() )
        checkin_options = DivWdg(css='spt_ui_options')
        checkin_options.add_style("padding: 10px")

        swap = SwapDisplayWdg()
        #swap.set_off()
        title = SpanWdg("Check-in Options")
        SwapDisplayWdg.create_swap_title(title, swap, checkin_options, is_open=False)
        div.add(swap)
        div.add(title)

        app_name = WebContainer.get_web().get_selected_app()
        checkin_options.add( my.get_file_type_wdg() )
        checkin_options.add( my.get_snapshot_type_wdg() )
        checkin_options.add(HtmlElement.br(1)) 
        checkin_options.add( my.get_export_method_wdg() )
        checkin_options.add( my.get_checkin_as_wdg() )

        #my.add( my.get_render_icon_wdg() )

        # For different export methods
        checkin_options.add( my.get_currency_wdg() )

        checkin_options.add( my.get_reference_option())
        checkin_options.add( my.get_auto_version_wdg())
        
        checkin_options.add( my.get_texture_option(app=app_name))
        checkin_options.add( my.get_handoff_wdg())
        checkin_options.add( my.get_connection_option())
        checkin_options.add(HtmlElement.br())

        if not my.context_select.get_value(for_display=True):
            my.add(DivWdg('A context must be selected.', css='warning'))
            return

        div.add(checkin_options)
      
        
        #my.add(HtmlElement.br())
        top.add( my.get_introspect_wdg() )
        top.add(HtmlElement.br(2))
        # create the interface
        table = Table()
        table.set_max_width()
        #table.set_class("table")
        table.add_color('background','background2')
        tr = table.add_row(css='smaller')
        tr.add_style('text-align','left')
        tr.add_color('background','background2', -15)
        tr.add_style('height','3.5em')
        table.add_header("&nbsp;")
        table.add_header("&nbsp;")
        th = table.add_header("Instance")
        th.add_style('text-align: left')
        table.add_header(my.get_checkin())
        table.add_header("Sandbox")
        

        # get session and handle case where there is no session
        my.session = SessionContents.get()
        if my.session == None:
            instance_names = []
            asset_codes = []
            node_names = []
        else:
            instance_names = my.session.get_instance_names()
            asset_codes = my.session.get_asset_codes()
            node_names = my.session.get_node_names()

        # get all of the possible assets based on the asset codes
        search = Search(my.search_type)
        search.add_filters("code", asset_codes)
        assets = search.get_sobjects()
        assets_dict = SObject.get_dict(assets, ["code"])

        if my.session:
            top.add("Current Project: <b>%s</b>" % my.session.get_project_dir() )
        else:
            top.add("Current Project: Please press 'Introspect'")


        count = 0
        for i in range(0, len(node_names) ):
            node_name = node_names[i]
            if not my.session.is_tactic_node(node_name) and \
                not my.session.get_node_type(node_name) in ['transform','objectSet']:
                    continue
            instance_name = instance_names[i]

            # backwards compatible:
            try:
                asset_code = asset_codes[i]
            except IndexError, e:
                asset_code = instance_name

            # skip if this is a reference
            if my.list_references == False and \
                    my.session.is_reference(node_name):
                continue

            table.add_row()


            # check that this asset exists
            asset = assets_dict.get(asset_code)
            if not asset:
                continue
            # list items if it is a set
            if my.search_type =='prod/asset' and asset.get_asset_type() in ["set", "section"]:
                my.current_sobject = asset
                my.handle_set( table, instance_name, asset, instance_names)
                count +=1
            # if this asset is in the database, then allow it to checked in
            if asset:
                if my.session.get_snapshot_code(instance_name, snapshot_type='set'):
                    continue

                # hack remember this
                my.current_sobject = asset
                my.handle_instance(table, instance_name, asset, node_name)

            else:
                table.add_blank_cell()
                table.add_cell(instance_name)


            count += 1

        if count == 0:
            table.add_row_cell("<center><h2>No assets in session to checkin</h2></center>")

        top.add(table)

        if not my.session:
            return


        non_tactic_nodes = my.session.get_instance_names(is_tactic_node=False)
        title = HtmlElement.b("Unknown List")
        swap = SwapDisplayWdg.get_triangle_wdg()

        div = DivWdg(id="unknown list")
        
        top.add(swap)
        top.add(title)

        SwapDisplayWdg.create_swap_title( title, swap, div) 
        unknown_table = Table()
        unknown_table.set_max_width()
        unknown_table.add_color('background','background2')
        div.add(unknown_table)

        
        for instance in non_tactic_nodes:
            my.handle_unknown_instance(unknown_table, instance)
        
        top.add(div)
        return top

   


    def get_checkin(my):
        '''the button which initiates the checkin'''
        # create the button with the javascript function
        widget = Widget()
        #button = TextBtnWdg(label=my.PUBLISH_BUTTON, size='large', width='100', side_padding='20', vert_offset='-5')
        button = ActionButtonWdg(title=my.PUBLISH_BUTTON, tip='Publish the selected assets')
        button.add_style('margin-bottom: 10px')
        #button.get_top_el().add_class('smaller')
        hidden = HiddenWdg(my.PUBLISH_BUTTON, '')
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
        exec( "%s.handle_input(button, my.search_type, my.texture_search_type)" % server_cbk)

        return widget




      

  
    

    


    def get_render_icon_wdg(my):
        '''Checkbox determines whether to create icon'''
        div = DivWdg()
        div.add("Create Icon: ")
        checkbox = CheckboxWdg("render")
        checkbox.set_persistence()
        div.add(checkbox)
        return div


    def handle_set(my, table, instance_name,  asset,  session_instances):
        asset_code = asset.get_code()
        
        # get all of the reference instances from the latest published
        snapshot = Snapshot.get_latest_by_sobject(asset, "publish")
        # if there is no publish snapshot, then this is definitely not
        # a set, so handle it like an instance
        if not instance_name in session_instances:
            return
        if not snapshot:
            my.handle_instance(table, instance_name, asset)
            return


        xml = snapshot.get_xml_value("snapshot")

        # skip if none are in session
        set_instances = xml.get_values("snapshot/ref/@instance")

        # TODO should get it based on the set's asset code so that
        # if the sesssion's set is older, it will still work
        session_set_items = my.session._get_data().get_nodes_attr(\
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

        my.handle_instance(table, instance_name, asset)
    
        # display all of the set instance that are in session
        for set_instance in set_instances_in_session:

            ref_snapshot = snapshot.get_ref_snapshot("instance",
                set_instance)
            ref_asset = ref_snapshot.get_sobject()

            # backwards compatible
            if set_instance.find(":") != -1:
                print "WARNING: snapshot '%s' has deprecated maya instance names" % snapshot.get_code()
                set_instance, tmp = set_instance.split(":")

            my.handle_instance(table, set_instance, ref_asset, publish=False)

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

            my.handle_missing_instance(table, set_instance, ref_asset)

        if set_instances_not_in_session:
            table.add_row_cell("&nbsp;")


    def handle_instance(my, table, instance, asset, node_name='', publish=True, allow_ref_checkin=False):

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
            td.add("< %s node >" % my.session.get_node_type(instance_name))
            table.add_blank_cell()
            return 

        # get the pipeline for this asset and handlers for the pipeline
        process_name = my.process_select.get_value() 
        handler_hidden = my.get_handler_input(asset, process_name)
        pipeline = Pipeline.get_by_sobject(asset) 
        



        # TEST: switch this to using node name instead, if provided
        if node_name:
            instance_node = my.session.get_node(node_name)
        else:
            instance_node = my.session.get_node(instance)

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
        if  my.search_type =='prod/asset' and asset.get_asset_type() in ['set','section']:
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

        # it should add once regardless in case there are duplicated references
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
            table.add_cell(my.get_save_wdg(my.current_sobject) )

        elif publish:
            textarea = TextAreaWdg()
            textarea.set_persist_on_submit()
            textarea.set_name("%s_description" % instance)
            textarea.set_attr("cols", "35")
            textarea.set_attr("rows", "2")
            table.add_cell(textarea)
            table.add_cell(my.get_save_wdg(my.current_sobject) )
        else:
            table.add_blank_cell()
            table.add_blank_cell()



    def handle_missing_instance(my, table, instance, asset):

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

  
    



class InstanceCheckinWdg(AssetCheckinWdg):

    SEARCH_TYPE = "prod/shot_instance"
   
    def get_context_data(my):
        # may use a prod/shot_instance search_type if it gets created
        process = my.process_select.get_value()
        labels, values = CheckinWdg.get_context_data(my, "prod/shot", process)
        return labels, values



    def list_references(my):
        '''lists whether references can be checked in with this widget'''
        return True


    def get_display(my):
        if not my.is_refresh:
            widget = DivWdg()
            my.set_as_panel(widget)
        else:
            widget = Widget() 

        # get session and handle case where there is no session
        my.session = SessionContents.get()
        node_name_dict = {}

        if my.session == None:
            session_instances = []
            asset_codes = []
            node_names = []
        else:
            session_instances = my.session.get_instance_names(is_tactic_node=True)
            asset_codes = my.session.get_asset_codes()
            node_names = my.session.get_node_names(is_tactic_node=True)
            for idx, node_name in enumerate(node_names):
                node_name_dict[session_instances[idx]] = node_name
        
        # display the ui
        div = DivWdg(css='filter_box')
         
        div.add_color("background", "background2", -15)
        div.add_style("margin: 5px")
        div.add_style("padding: 10px")
        div.add_style("font_style: bold")
        shot_navigator = ShotNavigatorWdg(refresh_mode='true', shot_search_type=my.search_type, sequence_search_type=my.sequence_search_type)
        div.add(shot_navigator)

        refresh_button = IconButtonWdg("Refresh", icon=IconWdg.REFRESH)
        refresh_button.add_behavior({'type': 'click', 
            'cbjs_action':  "var top=bvr.src_el.getParent('.spt_panel');spt.panel.refresh(top, {}, true)"})
        
        div.add(SpanWdg(refresh_button, css='small'))
        widget.add(div)
        
        shot = shot_navigator.get_shot()

        # TODO: add selected to shot
        '''
        add_selected = SubmitWdg("Add Selected To Shot")
        add_selected.add_event("onclick", "introspect_select()")
        add_selected.add_style("float", "right")
        my.add(add_selected)
        my.add("<br/>")
        '''


        if not session_instances:
            # it only warns if there is nothing loaded at all
            widget.add(DivWdg("No shot instances found in session!", css='warning'))
            return widget 
        
        div.add(HtmlElement.br(2))
        div.add( my.get_process_wdg(my.search_type)) 
        div.add( my.get_context_filter_wdg() )
        div.add(HtmlElement.br(2))

        # For different export methods
        title = SpanWdg("Check in Options")
        sub_div = DivWdg(css='spt_ui_options')
        sub_div.add_style('padding-left: 20px')
        export_wdg = my.get_export_method_wdg()
        sub_div.add(HtmlElement.br())
        sub_div.add(export_wdg)

        sub_div.add( my.get_handoff_wdg())
        sub_div.add( my.get_connection_option())
        sub_div.add(HtmlElement.br(2))

        swap = SwapDisplayWdg()
        SwapDisplayWdg.create_swap_title(title, swap, sub_div, is_open=False)
        div.add(swap)
        div.add(title)
        div.add(sub_div)

        if not my.context_select.get_value(for_display=True):
            widget.add(DivWdg('A context must be selected.', css='warning'))
            return widget
       
        widget.add( my.get_introspect_wdg() )
        widget.add(HtmlElement.br())
        # create the interface
        table = Table(css='')
        table.add_color('background','background2')
        table.set_max_width()
        tr = table.add_row(css='smaller')
        tr.add_style('height','3.5em')
        tr.add_style('text-align','left')
        tr.add_color('background','background2', -15)

        table.add_header("&nbsp;")
        table.add_header("Icon")

        table.add_header("Instance")
        th = table.add_header(my.get_checkin(), css='right_content')

        table.add_header("&nbsp;")
        if not shot:
            widget.add(HtmlElement.b("Please select a shot or create a shot first in the Admin area!") )
            return widget

        if my.session:
            widget.add("Current Project: <b>%s</b>" % my.session.get_project_dir() )
        else:
            widget.add("Current Project: Please press 'Introspect'")


        # go through the instances in the shot
        instances = shot.get_all_instances(include_parent=True) 
        instances = ShotInstance.filter_instances(instances, shot.get_code()) 
        

        for instance in instances:

            # HACK: remember the instance
            my.current_sobject = instance
                      
            asset = instance.get_asset()
            if not asset:
                continue
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
                    my.handle_instance(table, instance_name, asset, allow_ref_checkin=True)
                    continue


                xml = snapshot.get_xml_value("snapshot")

                # skip if none are in session
                set_instances = xml.get_values("snapshot/ref/@instance")

                session_set_items = my.session._get_data().get_nodes_attr("session/node[@set_snapshot_code='%s']"\
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

                    my.handle_instance(table, set_instance, ref_asset, allow_ref_checkin=True)

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

                    my.handle_missing_instance(table, set_instance, ref_asset)

                if set_instances_not_in_session:
                    table.add_row_cell("&nbsp;")
                continue  

            else:
                if instance_name != "cull" and \
                        not instance_name in session_instances:
                    continue
                # this for regular anim publish instances
                node_name = node_name_dict.get(instance_name)
                my.handle_instance(table, instance_name, asset, node_name=node_name, \
                    allow_ref_checkin=True)
        
        widget.add(table)

        shot_instance_names = [ instance.get_code() for instance in instances]

        title = HtmlElement.b("Unknown List")
        swap = SwapDisplayWdg.get_triangle_wdg()

        div = DivWdg(id="unknown list")
        
        widget.add(swap)
        widget.add(title)

        SwapDisplayWdg.create_swap_title( title, swap, div) 
        unknown_table = Table(css='table')
        unknown_table.set_max_width()
        div.add(unknown_table)

        widget.add(div)
        for instance in session_instances:
            if instance not in shot_instance_names:
                my.handle_unknown_instance(unknown_table, instance)
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

        return widget

    


    def get_checkin(my):

        widget = Widget()
        #button = TextBtnWdg(label=my.PUBLISH_BUTTON, size='large', width='100', side_padding='20', vert_offset='-5')
        #button.get_top_el().add_class('smaller')
        button = ActionButtonWdg(title=my.PUBLISH_BUTTON, tip='Publish selected asset instances')
        button.add_style('margin: 0 0 10px 0')
        hidden = HiddenWdg(my.PUBLISH_BUTTON, '')
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
        server_cbk = "pyasm.prod.web.AnimCheckinCbk"
        #TODO: make other Publish Buttons call their own handle_input function
        exec( Common.get_import_from_class_path(server_cbk) )
        exec( "%s.handle_input(button, my.search_type)" % server_cbk)

        return widget

     



    def handle_introspect(my):
        span = SpanWdg()
        button = IntrospectWdg()
        button.add_style("float", "right")
        span.add(button)
    
        # FIXME: commented out for now
        #button = IntrospectSelectWdg()
        #button.add_style("float", "right")
        #span.add(button)

        span.add_style("float", "right")
        my.add(span)



    def get_export_method_wdg(my):
        '''Checkbox that determines whether to use export or file/save'''
        is_unchecked = True
        default_cb = None
        div = DivWdg(css='spt_input_group')
        div.add_style('clear','left')
        title = FloatDivWdg(HtmlElement.b('Export Method:'), width = '15em')
        div.add(title)

        export_options = ['Export']
        export_options.append("Pipeline")


        for value in export_options:
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
        return div






class InstanceNode:

    def __init__(my, node_name):
        my.node_name = node_name

        if node_name.find(":") != -1:
            # handle bad instance names safely (no crash)
            tmp = node_name.split(":")
            my.namespace, my.asset_code = (tmp[0], tmp[1])
        else:
            my.namespace = ""
            my.asset_code = node_name

    def get_asset(my):
        asset = Asset.get_by_code(my.asset_code)
        return asset

    def get_asset_code(my):
        return my.asset_code


    def get_instance(my):
        return my.namespace
        



 
class ShotCheckinWdg(CheckinWdg):

    PUBLISH_BUTTON = "Publish"
    PUBLISH_SET_BUTTON = "Publish Set"
   
    def init(my):
        my.is_refresh = my.kwargs.get('is_refresh') =='true'
        my.search_type = my.kwargs.get('search_type')
        if not my.search_type:
            my.search_type = 'prod/shot'

        my.sequence_search_type = my.kwargs.get('sequence_search_type')
        if not my.sequence_search_type:
            my.sequence_search_type = my.search_type.replace('shot','sequence')

        my.texture_search_type = my.kwargs.get('texture_search_type')
        assert my.search_type

    def get_process_data(my):
        is_group_restricted = False
        from pyasm.prod.web import ProcessFilterWdg
        if ProcessFilterWdg.has_restriction():
            is_group_restricted = True
        labels, values = Pipeline.get_process_select_data(my.search_type, \
             project_code=Project.get_project_code(), is_group_restricted=is_group_restricted)
        return labels, values

    def get_context_data(my):
        # may use a prod/shot_instance search_type if it gets created
        process = my.process_select.get_value()
        labels, values = CheckinWdg.get_context_data(my, my.search_type , process)
        return labels, values

    def get_display(my):
        # add an outside box
        
        if not my.is_refresh:
            div = DivWdg()
            my.set_as_panel(div)
        else:
            div = Widget() 

        from app_init_wdg import PyMayaInit, PyXSIInit, PyHoudiniInit
        if WebContainer.get_web().get_selected_app() == 'Maya':
            app = PyMayaInit()
        elif WebContainer.get_web().get_selected_app() == 'XSI':
            app = PyXSIInit()
        elif WebContainer.get_web().get_selected_app() == 'Houdini':
            app = PyHoudiniInit()

        process = my.kwargs.get("process")

        filter_div = DivWdg(css="filter_box")

        filter_div.add_color("background", "background2", -15)
        filter_div.add_style("margin-top: 10px")
        filter_div.add_style("padding: 5px")
        filter_div.add_style("font_style: bold")
        div.add(filter_div)

        # the load and publish function are dependent on the shot_id element
        # of this Shot Navigator
        shot_navigator = ShotNavigatorWdg(refresh_mode='true', shot_search_type=my.search_type, sequence_search_type=my.sequence_search_type)
        filter_div.add(shot_navigator)


        refresh_button = IconButtonWdg("Refresh", icon=IconWdg.REFRESH)
        refresh_button.add_behavior({'type': 'click', 
            'cbjs_action':  "var top=bvr.src_el.getParent('.spt_panel');spt.panel.refresh(top, {}, true)"})
        
        filter_div.add(SpanWdg(refresh_button, css='small'))

        filter_div.add(HtmlElement.br(2))

        shot = shot_navigator.get_shot()


        if not shot:
            filter_div.add(HtmlElement.br())
            filter_div.add(SpanWdg("No shot has been created or selected.", css='med'))
            return div
        
      
        div.add("<br/>")

        div.add(my.get_publish_wdg(shot))


        return div

    def get_texture_option(my, show_texture_match=True, app='Maya'):
        '''Checkbox that determines different texture options'''
        is_unchecked = True
        default_cb = None

        div = DivWdg()    
        if app == 'XSI':
            hidden = HiddenWdg('handle_texture_dependency', 'false')
        else:

            float_div = FloatDivWdg(HtmlElement.b("Texture: "), width='16em')
            div.add(float_div)
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
    
    def get_publish_wdg(my, shot):
        ''' get the publish area widget '''
        widget = Widget()
        

        title = DivWdg("Publish Shot", css='maq_search_bar spt_ui_options')
        title.add_color("background", "background2", -15)
        title.add_style('padding: 10px')
        widget.add(title)

        

        mode_span = SpanWdg(HtmlElement.b(' Mode: '))
        title.add_style('padding-bottom: 12px')
        select = SelectWdg("publish_mode")
        #select.set_persistence()
        select.add_behavior({'type': 'change', 
            'cbjs_action': select.get_save_script()})
        #select.add_style('background-color: #565f50')

        values = ['shot']
        app_name = WebContainer.get_web().get_selected_app()
        #if app_name == 'Maya':
        #    values = ['shot','shot_set']

        select.set_option('values', values)
        select.set_option('default', 'shot')
        select.add_event('onchange', "if (this.value=='shot') {set_display_on('shot_publish');\
            set_display_off('shot_set_publish');} else {set_display_off('shot_publish');\
            set_display_on('shot_set_publish');}")
        mode_span.add(select)
        
        title.add(mode_span)
        
        swap = SwapDisplayWdg()

        option_title = SpanWdg("Check-in Options")
        # sub div
        div = DivWdg()
        div.add_style('padding-left: 20px')
        title.add(HtmlElement.br())

        title.add( HtmlElement.br() )
        SwapDisplayWdg.create_swap_title(option_title, swap, div, is_open=False)

        title.add( my.get_process_wdg(my.search_type))
        title.add( my.get_context_filter_wdg() )

        title.add( HtmlElement.br() )
        title.add( HtmlElement.br() )
        title.add(swap)
        title.add(option_title)
        title.add(div)
        title.add(HtmlElement.br())
        
        div.add( HtmlElement.br() )
        div.add( my.get_checkin_as_wdg() )
        #div.add( HtmlElement.br() )
        div.add( my.get_currency_wdg() )

        if not my.context_select.get_value(for_display=True):
            widget.add(DivWdg('A context must be selected.', css='warning'))
            return widget

        div.add(HtmlElement.br())

        options_div = my.get_reference_option()
        div.add(options_div)
        
        div.add( my.get_auto_version_wdg()) 
        div.add(HtmlElement.br())
        div.add( my.get_texture_option(False, app=app_name))

        div.add( my.get_handoff_wdg())
        div.add( my.get_connection_option())

        widget.add( my.get_introspect_wdg())
        widget.add(HtmlElement.br(2))
        # draw shot set publish (disabled for now)
        #if app_name == 'Maya':
        #    widget.add(my.get_shot_set_publish_wdg(shot, select.get_value()))

        # draw regular shot publish
        widget.add(my.get_shot_publish_wdg(shot, select.get_value()))

        process_name = my.process_select.get_value() 
        handler_input = my.get_handler_input(shot, process_name)
        div.add(handler_input)
        
        return widget
        
    def get_shot_publish_wdg(my, shot, mode):
        widget = Widget()
        #button = TextBtnWdg(label=my.PUBLISH_BUTTON, size='large', width='100', side_padding='20', vert_offset='-5')
        #button.get_top_el().add_class('smaller')
        button = ActionButtonWdg(title=my.PUBLISH_BUTTON, tip='Publish this shot')
        button.add_style('margin: 0 10px 10px 0')
        hidden = HiddenWdg(my.PUBLISH_BUTTON, '')
        button.add( hidden )
       
        widget.add(button)

        # custom defined 
        server_cbk = "pyasm.prod.web.ShotCheckinCbk"
        #TODO: make other Publish Buttons call their own handle_input function
        exec( Common.get_import_from_class_path(server_cbk) )
        exec( "%s.handle_input(button, my.search_type, my.texture_search_type)" % server_cbk)


        """
        button = ProdIconButtonWdg(my.PUBLISH_BUTTON)
        button.add_style('font-size', '1.0em')
        hidden = HiddenWdg(my.PUBLISH_BUTTON, '')
        button.add(hidden)
        status_sel = SelectWdg('checkin_status', label='Status: ')
        status_sel.set_option('setting', 'checkin_status')
        status_sel.add_empty_option('-- Checkin Status --')
        status_sel.set_persist_on_submit()
        """
    
        
        table = Table(css="")
        table.add_color('background','background2')
        tr = table.add_row(css='smaller')
        tr.add_style('height','3.5em')
        tr.add_style('text-align','left')
        tr.add_color('background','background2', -15)
        
        table.add_header('&nbsp;')
        table.add_header('&nbsp;')
        #th = table.add_header(status_sel)
        th = table.add_header(widget)
        #th.add_style('colspan','3')

        textarea = TextAreaWdg()
        textarea.set_persist_on_submit()
        textarea.set_name("%s_description" % shot.get_code() )
        textarea.set_attr("cols", "35")
        textarea.set_attr("rows", "3")

        table.add_row()
        table.add_blank_cell()
        table.add_cell(textarea)

        table.add_cell( my.get_save_wdg(shot) )

        div = DivWdg(id="shot_publish")
        if not mode or mode == 'shot':
            div.add_style('display: block')
        else:
            div.add_style('display: none')


        my.session = SessionContents.get()
        if my.session:
            div.add("Current Project: <b>%s</b>" % my.session.get_project_dir() )
        else:
            div.add("Current Project: Please press 'Introspect'")

        div.add(table)
        return div

    def get_shot_set_publish_wdg(my, shot, mode):
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

       
        button = ProdIconButtonWdg(my.PUBLISH_SET_BUTTON)
        button.add_style('font-size', '1.0em')
        hidden = HiddenWdg(my.PUBLISH_SET_BUTTON, '')
        button.add(hidden)

        # custom defined 
        server_cbk = "pyasm.prod.web.ShotSetCheckinCbk"
        exec( Common.get_import_from_class_path(server_cbk) )
        exec( "%s.handle_input(button, my.search_type)" % server_cbk)

        # add the command that this button executes
        '''
        WebContainer.register_cmd(server_cbk)

        from pyasm.command import Command
        cmd = eval("%s()" % server_cbk)
        Command.execute_cmd(cmd)
        '''
 

        table = Table(css="")
        table.add_color('background','background2')
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
                    my.handle_instance(session, table, node_name, shot)

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
        table.add_cell( my.get_save_wdg(shot) )


        div.add(table)
        widget.add(div)
        return widget

    def handle_instance(my, session, table, instance, shot, publish=True, allow_ref_checkin=False):

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
                     "cbjs_action": "spt.toggle_checkbox(bvr, '.spt_ui_options', 'shot_set_instances')"}) 
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
      

       

class SObjectCheckinWdg(CheckinWdg):

    def init(my):
        super(SObjectCheckinWdg, my).init()

    def get_display(my):
        my.add( my.get_introspect_wdg() )

        my.add( my.get_process_wdg(my.search_type))
        my.add( my.get_context_filter_wdg() )
        my.add(HtmlElement.br(2)) 
        my.add( my.get_file_type_wdg() )
        my.add( my.get_snapshot_type_wdg() )
        my.add(HtmlElement.br(2)) 
        my.add( my.get_export_method_wdg() )
        my.add( my.get_checkin_as_wdg() )
        #my.add( my.get_render_icon_wdg() )

        # For different export methods
        my.add( my.get_currency_wdg() )

        my.add( my.get_reference_option())
        if not my.context_select.get_value(for_display=True):
            my.add(DivWdg('A context must be selected.', css='warning'))
            return
        
        my.add(HtmlElement.br())


        # add the table
        my.add( my.get_instance_select_wdg() )

        if not my.session:
            return

        non_tactic_nodes = my.session.get_instance_names(is_tactic_node=False)
        title = HtmlElement.b("Unknown List")
        swap = SwapDisplayWdg.get_triangle_wdg()

        div = DivWdg(id="unknown list")
        
        my.add(swap)
        my.add(title)

        SwapDisplayWdg.create_swap_title( title, swap, div) 
        unknown_table = Table(css='table')
        unknown_table.set_max_width()
        div.add(unknown_table)

        
        for instance in non_tactic_nodes:
            my.handle_unknown_instance(unknown_table, instance)
        
        my.add(div)

        return super(SObjectCheckinWdg, my).get_display()

    def get_instance_select_wdg(my):

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
        my.session = SessionContents.get()
        if my.session == None:
            asset_codes = []
            node_names = []
        else:
            sobject_codes = my.session.get_asset_codes()
            node_names = my.session.get_node_names()

        # get all of the possible assets based on the asset codes
        search = Search(my.search_type)
        search.add_filters("code", sobject_codes)
        sobjects = search.get_sobjects()
        sobjects_dict = SObject.get_dict(sobjects, ["code"])

        # show the current project
        if my.session:
            my.add("Current Project: <b>%s</b>" % my.session.get_project_dir() )
        else:
            my.add("Current Project: Please press 'Introspect'")


        count = 0
        for i, node_name in enumerate(node_names):
            if not my.session.is_tactic_node(node_name) and \
                not my.session.get_node_type(node_name) in ['transform','objectSet']:
                    continue

            table.add_row()

            sobject_code = sobject_codes[i]
            sobject = sobjects_dict.get(sobject_code)
            if not sobject:
                continue

            my.handle_instance(table, sobject, node_name)
            count += 1

        if not count:
            table.add_row_cell("<center><h2>No assets in session to checkin</h2></center>")

        return table



    def handle_instance(my, table, sobject, node_name):

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
            table.add_cell(my.get_save_wdg(sobject) )

        else:
            textarea = TextAreaWdg()
            textarea.set_persist_on_submit()
            textarea.set_name("%s_description" % node_name)
            textarea.set_attr("cols", "35")
            textarea.set_attr("rows", "2")
            table.add_cell(textarea)
            table.add_cell(my.get_save_wdg(sobject) )



class CustomCheckinWdg(AssetCheckinWdg):
    '''AssetCheckinWdg is search type independent. so CustomCheckinWdg can just make use of it'''
