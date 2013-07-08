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

__all__ = ['FlashAssetInfoWdg', 'FlashLayerInfoWdg','FlashActionWdg', 
            'FlashShotLayerInfoWdg', 'FlashLoadWdg',
            'FlashLayerActionWdg', 'FlashShotInstanceActionWdg']

from pyasm.biz import File, Template, Snapshot
from pyasm.web import *
from pyasm.widget import *
from pyasm.flash import FlashAsset, FlashLayer, FlashShot, FlashLoad, FlashDownload, FlashImport
        
from flash_input_wdg import FlashAssetCheckboxWdg

from pyasm.search import Search, SObject
from pyasm.common import Xml, Common, Container 
from pyasm.prod.web import SObjectFilePublishWdg
import re



class FlashAssetInfoWdg(BaseTableElementWdg):
    '''widget to display the code, name and description in one column'''

    def init(my):
        my.expand_wdg = ExpandableTextWdg()
        my.expand_wdg.set_id('fl_asset_desc_max_text_length')

    def get_prefs(my):
       
        return my.expand_wdg.get_prefs()

    def get_display(my):
        my.sobject = my.get_current_sobject()

        table = Table(css='embed')
        table.add_col(css='large')
        table.add_col()
        my._add_code(table)
        my._add_name(table)
        my._add_description(table)
    
        return table
    
    def _add_code(my, table):
        table.add_row()
        table.add_cell(HtmlElement.i("Code:"))
        table.add_cell( "<b>%s</b>" % my.sobject.get_value("code") )

    def _add_name(my, table):
        name = my.sobject.get_value("name", no_exception=True)
        if not name:
            return
        table.add_row()
        table.add_cell(HtmlElement.i("Name:"))
        table.add_cell( name )

    def _add_description(my, table):
        table.add_row()
        table.add_cell(HtmlElement.i("Description:"))
        if not my.sobject.has_value("description"):
            table.add_blank_cell()
            return
        desc = my.sobject.get_value("description")
       
        my.expand_wdg.set_value(desc)
        table.add_cell(my.expand_wdg)

class FlashLayerInfoWdg(FlashAssetInfoWdg):
    
    def _add_code(my, table):
        pass


class FlashShotLayerInfoWdg(FlashAssetInfoWdg):
    '''Element to display layer info in a shot'''

    def get_prefs(my):
        
        my.text = FilterTextWdg('shot_layer_info_height',\
                label='Max height: ', is_number=True)
        my.text.set_option('default','100')
        my.text.set_attr('size', '2')
        widget = Widget()
        widget.add(my.text)
        widget.add('px')
        return widget

    def get_display(my):
        my.sobject = my.get_current_sobject()

        layers = my.sobject.get_all_children("prod/layer")

        div = DivWdg()
        div.set_style('width: 100px; overflow: auto; max-height: %spx' %my.text.get_value())
        table = Table(css='embed')
        for layer in layers:
            table.add_row()
            table.add_cell( layer.get_value("name") )
        div.add(table)
        return div
    





class FlashLoadWdg(AjaxWdg):
    ''' the single loading button for flash'''
    def init(my):
        my.flash_sobj = None
        my.flash_snapshot = None
        my.main_div = None

        my.load_mode = None

    def init_cgi(my):
        # get the sobject
        keys = my.web.get_form_keys()
        search_key = ''
        
        for key in keys:
            if key.startswith('skey_FlashLoadWdg_'):
                search_key = my.web.get_form_value(key)
                break

        if search_key:
            sobject = Search.get_by_search_key(search_key)
            my.flash_sobj = sobject
            my.init_setup()
            

    def init_setup(my):
        ''' set up the ajax top and the ajax command '''
        div_id = 'main_div_%s' %my.flash_sobj.get_id()
        my.main_div = DivWdg(id=div_id)
        my.set_ajax_top(my.main_div)
       
        # register the inputs first
        hidden = HiddenWdg('skey_FlashLoadWdg_%s' %my.flash_sobj.get_id())
        my.add_ajax_input(hidden)   

    def set_sobject(my, sobject):
        my.flash_sobj = sobject
        my.init_setup()

    def set_snapshot(my, snap):
        my.flash_snapshot = snap


    def set_load_mode(my, load_mode):
        my.load_mode = load_mode


    def get_display(my):   
        # load msg
        load = SpanWdg("", css='small')
        load.set_style("font-size: 8px")
        load.set_id("load_progress_%s" %my.flash_sobj.get_id())   
            
        flash_load = FlashLoad(my.flash_sobj, my.flash_snapshot)
        if my.load_mode:
            flash_load.set_load_mode(my.load_mode)
        flash_load.set_load_msg_id(load.get_id())
        load_script = flash_load.get_script()

        button = IconButtonWdg("load", IconWdg.LOAD)
        
        # set up event
        event_name = "%s_%s" %(my.flash_sobj.get_search_key(), FlashActionWdg.LOAD_ACTION)
        #button.add_event_caller("onclick", event_name)
        #event = WebContainer.get_event_container()
        behavior = {
            'type': 'click_up',
            'cb_fire_named_event': event_name
        }
        button.add_behavior(event_name)

        
        # always replace the last callback
        #event.add_listener( event_name, load_script, True )
        behavior = {
            'type': 'listen',
            'event_name': event_name,
            'cbjs_action': load_script
        }
        button.add_behavior(behavior)

        my.main_div.add(button)
        my.main_div.add(load)

        hidden = HiddenWdg('skey_FlashLoadWdg_%s' %my.flash_sobj.get_id(),\
            my.flash_sobj.get_search_key())
        my.main_div.add(hidden)
        
        return my.main_div

        
        
class FlashActionWdg(BaseTableElementWdg):

    LOAD_ACTION = 'load'
    DOWNLOAD_ACTION = 'download'
    PUBLISH_ACTION = 'publish'
    IMPORT_ACTION = 'import'
    LOAD_MODE = 'load_mode'
    PREFIX_MODE = 'prefix_mode'
    TMPL_SEARCH_TYPE = FlashAsset.SEARCH_TYPE
       
    def __init__(my):
        my.import_type = ''
        super(FlashActionWdg, my).__init__()

    def get_prefs(my):
        ''' load as a separate file or into a file'''
        div = DivWdg()
        span = SpanWdg("Load Mode: ", css='small')
        select = FilterSelectWdg('flash_asset_load_mode')

        select.set_id(my.LOAD_MODE)
        
        select.set_option("values", "simple|merge")    
        select.set_option("labels", "Simple|Merge")
        select.get_value()
        span.add(select)
      

        folderless = CheckboxWdg(my.PREFIX_MODE)
        # setting default on will turn it on everytime the page reloads
        #folderless.set_option('default','on')
        folderless.set_submit_onchange()
        folderless.set_persistence()
        value = folderless.get_value()
        
        folder_span = SpanWdg(folderless)
        folder_span.add("detect by prefix")

        div.add(span)
        div.add(HtmlElement.br(2))
     
        div.add(folder_span)
        div.add(HtmlElement.br())
        div.add(my._get_import_pref())

        return div
        
    def _get_import_pref(my):
        import_pref_select = FilterSelectWdg('flash_import_mode',\
            label='Import Mode:')
        import_pref_select.set_option('values', [FlashImport.TYPE_1, FlashImport.TYPE_2])
        import_pref_select.set_option('default', FlashImport.TYPE_2)

        #IMPORTANT! get the value here or the default would not work as the 
        # buffer gets pushed
        my.import_type = import_pref_select.get_value()
        return import_pref_select

    def get_title(my):
        cb_name = my.get_checkbox_name()
        span = DivWdg()
        span.add_style('width','60px')
        
        load = IconButtonWdg("multi load", IconWdg.LOAD)
        load.add_style("padding-right", "10px")
        load.add_event("onclick", "pyflash.multi_action('%s','%s')"\
             % (FlashActionWdg.LOAD_ACTION, cb_name))
        load_dis = load.get_buffer_display()
        
        span.add(load_dis)
        hidden = HiddenWdg("upload_description",'')
        span.add(hidden)

        swf_view = my._get_swf_view().get_buffer_display()
        span.add(swf_view)

        float_span = SpanWdg(load_dis, css='med')

        download = IconButtonWdg("multi download", IconWdg.DOWNLOAD)
        download.add_style("padding-right", "8px")
        download.add_event("onclick", "pyflash.multi_action('%s','%s')"\
             % (FlashActionWdg.DOWNLOAD_ACTION, cb_name))
        download_dis = download.get_buffer_display()

        float_span.add(download_dis)

        float_span.add(swf_view)
        WebContainer.get_float_menu().add(float_span)
        
        
        return span

    def preprocess(my):
        my._init_snapshots() 
        
        
    def _get_swf_view(my):
        swf_view = PopupWindowLinkWdg(FlashAsset.SEARCH_TYPE,\
                widget='pyasm.flash.widget.FlashSwfViewWdg', element_list=[FlashAssetCheckboxWdg.CB_NAME])
        swf_view.set_button(IconButtonWdg("show time", icon=IconWdg.MOVIE_VIEW, long=False))
       
        return swf_view 
        


    def _init_snapshots(my):
        '''preselect all of the snapshots'''
        snapshots = Snapshot.get_latest_by_sobjects(my.sobjects)
        my.snapshot_dict = SObject.get_dict(snapshots,\
            key_cols=['search_type','search_id'])



    def get_template(my, search_type=None):
        ''' get the template sobject '''
        #TODO: this can be merged with get_template() in flash.py
        if not search_type:
            search_type = my.TMPL_SEARCH_TYPE

        key = "Template:%s"
            
        template = Container.get(key)
        if template != None:
            return template
        else:
            template = Template.get_latest(search_type)
            if not template:
                    Container.put(key, "")
            else:
                    Container.put(key, template)

            return template 


        
    def get_checkbox_name(my):
        from pyasm.flash.widget import FlashAssetCheckboxWdg
        return FlashAssetCheckboxWdg.CB_NAME

   
        
    def get_display(my):
        my.div = DivWdg()
        
        my.div.add_style("font-size: 0.7em")
         
        sobject = my.get_current_sobject()
        if not sobject:
            web = WebContainer.get_web()
            search_type = web.get_form_value("search_type")
            search_id = web.get_form_value("search_id")
            sobject = Search.get_by_id(search_type, search_id)
  
        if sobject.is_general_asset():

            import_span = SpanWdg("", css='small')
            import_span.set_style("font-size: 8px")
            import_span.set_id("import_progress_%s" %sobject.get_id())
            flash_snap = my.snapshot_dict.get(sobject.get_search_key())
            my.add_import_wdg(sobject, flash_snap, import_span)
            my.div.add(HtmlElement.br(2))
            # an upload/copy widget
            my.add_upload_wdg(sobject)
            #NOTE: download only is setup if this asset is not importable
            
        else:
            my.load_wdg = FlashLoadWdg()

            if my.get_option("load_mode"):
                my.load_wdg.set_load_mode(my.get_option("load_mode"))

            my.load_wdg.set_sobject(sobject)
            flash_snap = my.snapshot_dict.get(sobject.get_search_key())
            my.load_wdg.set_snapshot(flash_snap) 
            my.div.add(my.load_wdg)
            my.div.add(HtmlElement.br(2))
            # just setting up download for Float menu, does not draw
            my.add_download_wdg(sobject, flash_snap)

            publish = SpanWdg("", css='small')
            publish.set_style("font-size: 8px")
            publish.set_id(publish.generate_unique_id("pub_progress"))
     
            if my.get_option("publish") != "false":
                my.add_publish_wdg(sobject, publish)
      
            if my.get_option("wip") != "false":
                my.add_wip_wdg(sobject)

        return my.div



    def add_publish_wdg(my, sobject, publish_msg):
        code = sobject.get_value('code')
        button = IconButtonWdg("publish", IconWdg.PUBLISH)
        
        # FIXME: HOW TO HANDLE THIS with new event mechanism?
        # set up event
        event_name = "%s_%s" %(sobject.get_search_key(), FlashActionWdg.PUBLISH_ACTION)
        event = WebContainer.get_event_container()
        function = event.get_event_caller(event_name)

        # escape the single quotes for function
        button.add_event("onclick", "comment_bubble.show(event, '%s', '%s')" \
            % (code, Common.escape_quote(function)))



        # get the ajax load
        from pyasm.web import AjaxCmd
        ajax = AjaxCmd("publish_%s" % sobject.get_id() )
        ajax.register_cmd("pyasm.flash.FlashAssetPublishCmd")
        ajax.add_element_name("upload_description")
        ajax.add_element_name("upload_files")
        ajax.set_option("search_type", sobject.get_search_type() )
        ajax.set_option("search_id", sobject.get_id() )
        div = ajax.generate_div()
        my.div.add(div)

        on_script = ajax.get_on_script(show_progress=False)

        thumb_script = ThumbWdg.get_refresh_script(sobject) 
        post_publish_script = [thumb_script]
        
        post_publish_script.append(my.load_wdg.get_refresh_script(show_progress=False))

        caller = event.get_event_caller(SiteMenuWdg.EVENT_ID)
        # update the SiteMenuWdg
        post_publish_script.append(caller)
        
        div.set_post_ajax_script(';'.join(post_publish_script))

       
        #event.add_listener(event_name,  "if(pyflash.publish('%s','%s')==false) return;%s" \
        #    % (code, publish_msg.get_id(), on_script ) )
        behavior = {
            'type': 'listen',
            'event_name': event_name,
            'cbjs_action': "if(pyflash.publish('%s','%s')==false) return;%s" \
                % (code, publish_msg.get_id(), on_script )
        }
        my.div.add_behavior(behavior)
        

        
        my.div.add(button)
        my.div.add(publish_msg)
        my.div.add(HtmlElement.br())
  
    def add_download_wdg(my, sobject, snapshot):
        ''' just set it up for multi_action float menu
            no visible widgets are drawn here'''
        download = FlashDownload(sobject, snapshot)
        download.set_progress_msg_id("%s_%s" \
            %(FlashDownload.PROGRESS_MSG_ID, sobject.get_id()))

        # set up event
        event_name = "%s_%s" %(sobject.get_search_key(), FlashActionWdg.DOWNLOAD_ACTION)
        #event = WebContainer.get_event_container()
        #event.add_listener(event_name,  download.get_script())
        behavior = {
            'type': 'listen',
            'event_name': event_name,
            'cbjs_action': download.get_script()
        }
        my.div.add_behavior(behavior)
 
       

    def add_wip_wdg(my, sobject):
        ''' open the sandbox in explorer '''
        #code = sobject.get_value('code')
        code = sobject.get_code()
        sandbox_path = sobject.get_sandbox_dir()
        
        button = IconButtonWdg("sandbox", IconWdg.WIP)
        button.add_event('onclick', "pyflash.open_exp('%s')" %(sandbox_path))
        my.div.add(HtmlElement.br())
        my.div.add(button)
        
            
    def _get_file_info(my, sobject):
        ''' return the web url and the file name with flash sobject'''
        snapshot = web_dir = None
        if sobject:
            snapshot = my.snapshot_dict.get(sobject.get_search_key())
            if not snapshot:
                snapshot = Snapshot.get_latest_by_sobject(sobject)
                
            web_dir = sobject.get_remote_web_dir()
       
        if snapshot:
            fla = snapshot.get_name_by_type(".fla")
            fla_file_name = snapshot.get_file_name_by_type(".fla")
            fla_link = "%s/%s" % (web_dir, fla_file_name)
            return fla_link, fla      

        else:
            return None, None



    def add_upload_wdg(my, sobject):
        code = sobject.get_value('code')
        '''
        # this code is for enabling file copy instead of file upload 
        copy_wdg = SObjectFilePublishWdg(sobject)
        my.div.add(copy_wdg)
        '''
        button = PublishLinkWdg(sobject.get_search_type(), \
            sobject.get_id(), config_base="upload_background")
        button.set_style('padding: 0px')
        my.div.add(button)
   


    def add_import_wdg(my, sobject, snapshot, import_msg):
        '''widget to import files other than an .fla into flash (png, etc)'''
        
        import_script = FlashImport(sobject, snapshot)
        import_script.set_load_msg_id(import_msg.get_id())

        script = import_script.get_script(file_type=my.import_type)

        import_button = IconButtonWdg('import', icon=IconWdg.IMPORT)
        if not import_script.is_importable():
            import_button = IconButtonWdg('download', icon=IconWdg.DOWNLOAD)
            # set up event
            event_name = "%s_%s" %(sobject.get_search_key(), FlashActionWdg.DOWNLOAD_ACTION)
            #event = WebContainer.get_event_container()
            #event.add_listener(event_name,  script)
            #import_button.add_event('onclick', event.get_event_caller(event_name))
            behavior = {
                "type": "click_up",
                'cb_fire_named_event': event_name
            }
            import_button.add_behavior(behavior)
        else:
            import_button.add_event('onclick', script)
        my.div.add(import_button)    
        my.div.add(import_msg)

    def get_default_template(my, name):
        url = WebContainer.get_web().get_base_url()
        base = url.to_string()
        tmpl_fla_link = "%s/context/template/%s" %(base, name)
        return tmpl_fla_link, name
       
    
class FlashShotInstanceActionWdg(FlashActionWdg):
   
    def get_prefs(my):
        ''' load as a separate file or into a file'''
        span = SpanWdg("Load Mode: ", css='small')
        select = FilterSelectWdg('flash_asset_load_mode')

        select.set_id(my.LOAD_MODE)
        
        select.set_option("values", "simple|merge")    
        select.set_option("labels", "Simple|Merge")
        select.get_value()
        span.add(select)
      
        span.add(my._get_import_pref())

        return span
   
    def get_checkbox_name(my):
        from pyasm.flash.widget import FlashShotInstanceCheckboxWdg
        return FlashShotInstanceCheckboxWdg.CB_NAME
    
    def get_title(my):
        cb_name = my.get_checkbox_name()
        span = SpanWdg(css='small')
        
        load = IconButtonWdg("multi load instances", IconWdg.LOAD)
        load.add_style("padding-right", "10px")
        load.add_event("onclick", "pyflash.multi_action('%s','%s')"\
             % (FlashActionWdg.LOAD_ACTION, cb_name))
        span.add(load)
        return span


    def preprocess(my):
        my._init_snapshots()  
        

    
    def get_display(my):
        my.div = DivWdg()
        
        my.div.add_style("font-size: 0.7em")
         
        sobject = my.get_current_sobject().get_reference('flash/asset')  
        
        if sobject.is_general_asset():
            # an upload/copy widget
            my.add_upload_wdg(sobject)
            my.div.add(HtmlElement.br(2))

            import_span = SpanWdg("", css='small')
            import_span.set_style("font-size: 8px")
            import_span.set_id(import_span.generate_unique_id("import_progress"))
            flash_snap = my.snapshot_dict.get(sobject.get_search_key())
            my.add_import_wdg(sobject, flash_snap, import_span)
        else:
            my.load_wdg = FlashLoadWdg()
            my.load_wdg.set_sobject(sobject)

            if my.get_option("load_mode"):
                my.load_wdg.set_load_mode(my.get_option("load_mode"))
            
            my.div.add(my.load_wdg)
            
            my.div.add(HtmlElement.br(2))

            publish = SpanWdg("", css='small')
            publish.set_style("font-size: 8px")
            publish.set_id(publish.generate_unique_id("pub_progress"))
            
        return my.div.get_display()
   


class FlashLayerActionWdg(FlashActionWdg):
   
    # this is used for publishing, FlashShot.SEARCH_TYPE is used for loading
    TMPL_SEARCH_TYPE = FlashLayer.SEARCH_TYPE
    
    def get_title(my):
        cb_name = my.get_checkbox_name()
        span = SpanWdg(css='small')
        
        load = IconButtonWdg("multi load layers", IconWdg.LOAD)
        load.add_style("padding-right", "10px")
        load.add_event("onclick", "pyflash.multi_action('%s','%s')"\
             % (FlashActionWdg.LOAD_ACTION, cb_name))
        
        publish = IconButtonWdg("multi publish", IconWdg.PUBLISH)
        function = "pyflash.multi_action('%s','%s')"\
             % (FlashActionWdg.PUBLISH_ACTION, cb_name)
        publish.add_event("onclick", "comment_bubble.show(event, 'multi-layers', '%s')" \
            % Common.escape_quote(function) )
            
        load_dis = load.get_buffer_display()
        publish_dis = publish.get_buffer_display()
       
        span.add(load_dis)
        span.add(publish_dis)
        hidden = HiddenWdg("upload_description",'')
        hidden.set_persistence() 
        hidden.get_value()
        span.add(hidden)   

        float_span = SpanWdg(load_dis, css='med')
        float_span.add(publish_dis)
        WebContainer.get_float_menu().add(float_span)

        my._init_snapshots() 
        return span
    
    def get_prefs(my):
        div = DivWdg()
        '''
        pub_span = SpanWdg("Max publish time:", css='small')
        txt = TextWdg("max_publish_time")
        txt.set_persistence()
        txt.add_event('onblur','document.form.submit()')
        txt.set_option('size','2')
        value = txt.get_value()
        if not value:
            txt.set_value(10)
            value = 10
        div.add(HtmlElement.script("pyflash.max_publish_time = '%s'"\
            %(int(value)*1000)))
        div.add(pub_span)
        div.add(txt)
        div.add("s")
        '''
        folderless = CheckboxWdg(my.PREFIX_MODE)
        # setting default on will turn it on everytime the page reloads
        #folderless.set_option('default','on')
        folderless.set_submit_onchange()
        folderless.set_persistence()
        value = folderless.get_value()
        
        folder_span = SpanWdg(folderless)
        folder_span.add("detect by prefix")
        div.add(HtmlElement.br())
        div.add(folder_span)
        
        return div


    def get_checkbox_name(my):
        from pyasm.flash.widget import FlashLayerCheckboxWdg
        return FlashLayerCheckboxWdg.CB_NAME


    def add_load_wdg(my, sobject, load_msg):
        #TODO: this is too database intensive
        web_dir = sobject.get_web_dir()

        web = WebContainer.get_web()
        local_dir = web.get_local_dir() + "/download"

        xml = sobject.get_xml_value("snapshot")

        layer_name = sobject.get_value('name')
        fla_link, fla = my._get_file_info(sobject)
        to_path = "%s/%s" % (local_dir,fla)
        
        tmpl_fla_link, tmpl_fla = my._get_file_info(my.get_template(FlashShot.SEARCH_TYPE))
        if tmpl_fla_link == None:
            tmpl_fla_link, tmpl_fla = my.get_default_template("flash-layer_default.fla")

        shot_code = sobject.get_value('shot_code')
        
        # name tmpl file
        tmpl_fla = "%s.fla" % shot_code
        tmpl_to_path = "%s/%s" % (local_dir,tmpl_fla)
        
        
        button = IconButtonWdg("load", IconWdg.LOAD)
        
        # set up event
        event_name = "%s_%s" %(sobject.get_search_key(), FlashActionWdg.LOAD_ACTION)
        button.add_event_caller("onclick", event_name)
        #event = WebContainer.get_event_container()
        #event.add_listener(event_name, "pyflash.load_layer('%s','%s','%s',"\
        #   "'%s','%s','%s','%s')" \
        #   % ( fla_link, to_path, layer_name, tmpl_fla_link, tmpl_to_path, \
        #   load_msg.get_id(), my.PREFIX_MODE) )
        behavior = {
            'type': 'listen',
            'cbfn_action': "pyflash.load_layer('%s','%s','%s',"\
                "'%s','%s','%s','%s')" \
                % ( fla_link, to_path, layer_name, tmpl_fla_link, tmpl_to_path, \
                load_msg.get_id(), my.PREFIX_MODE)
        }
        my.div.add_behavior(behavior)
          

        my.div.add(button)
        my.div.add(load_msg)
    

    def add_publish_wdg(my, sobject, publish_msg):
        layer_name = sobject.get_value('name')
        shot_code = sobject.get_value('shot_code')

        fla_link, fla = my._get_file_info(my.get_template())

        if fla_link == None:
            # put a failsafe template
            url = WebContainer.get_web().get_base_url()
            base = url.to_string()
            fla_link = "%s/context/template/flash-layer_default.fla" % base
            fla = "flash-layer_default.fla"
       
        
        button = IconButtonWdg("publish layer", IconWdg.PUBLISH)
        
        # set up event
        event_name = "%s_%s" %(sobject.get_search_key(), FlashActionWdg.PUBLISH_ACTION)
        #button.add_event_caller("onclick", event_name)
        event = WebContainer.get_event_container()
        function = '%s;document.form.submit();' \
            %event.get_event_caller(event_name)
        # escape the single quotes for function
        button.add_event("onclick", "comment_bubble.show(event, '%s', '%s')" \
            % (layer_name, Common.escape_quote(function)))
        
        event.add_listener(event_name, "pyflash.publish_layer('%s', '%s', '%s', '%s', '%s', '%s')" \
                % (shot_code, layer_name, fla_link, fla, publish_msg.get_id(), my.PREFIX_MODE) )
             
        span = SpanWdg(publish_msg)    
        my.div.add(button)
        my.div.add(span)
     
    def add_upload_wdg(my, sobject):
        pass

    def add_import_wdg(my, sobject, snap):
        pass
    



class FlashShotActionWdg(FlashActionWdg):

    def get_checkbox_name(my):
        from pyasm.flash.widget import FlashShotCheckboxWdg
        return FlashLayerCheckboxWdg.CB_NAME

    def _get_swf_view(my):
        
        swf_view = PopupWindowLinkWdg(FlashShot.SEARCH_TYPE,\
                widget='pyasm.flash.widget.FlashSwfViewWdg', element_list=[FlashShotCheckboxWdg.CB_NAME])
        swf_view.set_button(IconButtonWdg("show time", icon=IconWdg.MOVIE_VIEW, long=False))
       
        return swf_view
