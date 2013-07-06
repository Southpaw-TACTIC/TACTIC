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

__all__ = ['FlashShotInstanceAdderWdg', 'FlashLayerInstanceAdderWdg', 'FlashEpisodePlannerWdg', 'FlashLayerStageWdg', 'EpisodePlannerCbk']

from pyasm.web import *
from pyasm.widget import *
from pyasm.search import *
from pyasm.biz import *
from pyasm.flash import *
from pyasm.prod.biz import *
from pyasm.prod.web import *

class FlashAssetFilter(DivWdg):

    def init(my):
        nav = EpisodeNavigatorWdg(name="initial_episode")
        nav.add_none_option()
        my.episode_code = nav.get_value()
        my.add(nav)

        text_wdg = TextWdg("asset_search")
        text_wdg.set_persist_on_submit()
        text_wdg.add_style('margin-bottom: 3px')
        my.asset_search = text_wdg.get_value()
        my.add(SpanWdg(text_wdg, css='med'))


    def alter_search(my, search):
        has_filter = False
        if my.episode_code != "":
            search.add_filter("episode_code", my.episode_code)
            has_filter = True
        if my.asset_search != "":
            my.asset_search = my.asset_search.lower()
            columns = my.get_search_columns()
            expr = [Search.get_regex_filter(x, my.asset_search) for x in columns]
            filter = "(%s)" %" or ".join(expr)
            search.add_where(filter)
            has_filter = True
        #if not has_filter:
        #    search.add_where("NULL")

    def get_search_columns(my):
        return ['code','name','description']

class FlashEpisodeFilterWdg(EpisodeFilterWdg):
    pass

class FlashEpisodeShotNavigatorFilter(EpisodeShotFilterWdg):
   
    def alter_search(my, search):
        if my.get_value() != "":
            search.add_filter("shot_code", my.get_value())



class FlashShotInstanceAdderWdg(ShotInstanceAdderWdg):

    CONTAINER_NAME = 'Shots'
    BUTTON_LABEL = "Populate with Assets"
    LOAD_MODE = 'load_mode'
    PREFIX_MODE = 'prefix_mode'

    def get_left_filter(my, search=None):
        widget = Widget()
        asset_filter = AssetFilterWdg()
        asset_filter.alter_search(search)
        widget.add(asset_filter)

        widget.add( HtmlElement.br(2) )

        instance_filter = EpisodeInstanceFilterWdg()
        instance_filter.alter_search(search)
        widget.add(instance_filter)
        
        use_epi = FilterCheckboxWdg( EpisodeInstanceFilterWdg.OPTION_NAME,\
            label='Filter by Episode Planner')
        widget.add(use_epi)
        return widget



    def get_right_filter(my, search):
        filter = FlashEpisodeFilterWdg()
        filter.add_none_option()
        return filter

    def get_action_wdg(my):

        main_div = DivWdg(css="filter_box center_content")
        div = DivWdg()
        main_div.add(div)
        div.add_style('height', '16px')
        div.add_style('margin', '3px 0 3px 0')
        
        div.add(HtmlElement.b("Action: "))
        add_button = IconSubmitWdg(my.ADD_BUTTON, IconWdg.ADD, long=True)
        div.add(add_button)
        remove_button = IconSubmitWdg("Remove from %s" % my.CONTAINER_NAME, IconWdg.DELETE, long=True)
        div.add(remove_button)
        
        # register the add commands
        # TODO: make into ajax:
        for cbk in my.get_action_cbk():
            WebContainer.register_cmd(cbk)

        stage_button = IconSubmitWdg(my.BUTTON_LABEL, long=True)
        div.add(SpanWdg(stage_button, css='large'))
        
        # add a hint
        hint = HintWdg('To populate a shot with assets, you need to first [Add Assets] to the shot. ' \
                'Then you can check the checkbox for the shot and click on [%s]' % my.BUTTON_LABEL)
        div.add(hint)

        div.add(HiddenWdg(my.LOAD_MODE, 'merge'))
        folderless = HiddenWdg(my.PREFIX_MODE, 'true')
        folderless.set_attr('checked','1')
        div.add(folderless)
        div.add(FlashShotStageWdg())
        
        return main_div


class FlashEpisodePlannerWdg(SequencePlannerWdg):
    ADD_BUTTON = "Add Assets to Episode"
    def get_left_filter(my, search):
        return AssetFilterWdg()

    def get_action_wdg(my):

        main_div = DivWdg(css="filter_box center_content")
        div = DivWdg()
        div.add_style('height', '16px')
        div.add_style('margin', '3px 0 3px 0')
        
        main_div.add(my.get_view_select())
        main_div.add(div)

        div.add(HtmlElement.b("Action: "))
        add_button = IconSubmitWdg(my.ADD_BUTTON, IconWdg.ADD, long=True)
        div.add(add_button)
      

        WebContainer.register_cmd("pyasm.flash.widget.EpisodePlannerCbk")

        return main_div

class EpisodePlannerCbk(SequencePlannerCbk):
    
    def check(my):
        web = WebContainer.get_web()
        if web.get_form_value(FlashEpisodePlannerWdg.ADD_BUTTON) != "":
            return True
        
        return False

class FlashLayerInstanceAdderWdg(ShotInstanceAdderWdg):

    CONTAINER_NAME = 'Layers'
    BUTTON_LABEL = "Populate with Assets"
    LOAD_MODE = 'load_mode'
    PREFIX_MODE = 'prefix_mode'
    
    def get_left_search_type(my):
        return "prod/asset"

    def get_right_search_type(my):
        return "prod/layer"
    
    def get_left_filter(my, search):
        return FlashAssetFilter()

    def get_right_filter(my, search):
        filter = FlashEpisodeShotNavigatorFilter()
        filter.add_none_option()
        return filter
   
    def get_action_cbk(my):
        return ["pyasm.prod.web.LayerInstanceAdderCbk", \
                "pyasm.prod.web.LayerInstanceRemoverCbk"]
   
    def get_action_wdg(my):

        div = DivWdg(css="filter_box")
        div.add(HtmlElement.b("Action: "))
        add_button = SubmitWdg("Add Assets")
        div.add(add_button)
        remove_button = SubmitWdg("Remove from %s" % my.CONTAINER_NAME)
        div.add(remove_button)
       
        # add the staging button
        stage_button = SubmitWdg(my.BUTTON_LABEL)
        stage_button.add_style('background-color: #e6edbe')
        div.add(SpanWdg(stage_button, css='large'))
        for cbk in my.get_action_cbk():
            WebContainer.register_cmd(cbk)

        div.add(HiddenWdg(my.LOAD_MODE, 'merge'))
        folderless = HiddenWdg(my.PREFIX_MODE, 'true')
        folderless.set_attr('checked','1')
        div.add(folderless)
        div.add(FlashLayerStageWdg())

        return div




class FlashSObjectStageWdg(Widget):
    ''' This widget draws all the script required for the staging process
        for flash layers '''
    BUTTON_LABEL = "Populate with Assets"
    LOAD_MODE = "load_mode"
      
    def check(my):
        web = WebContainer.get_web()
        if web.get_form_value(my.BUTTON_LABEL) != "":
            return True


    def get_publish_command(my):
        pass

    def get_search_type(my):
        return FlashLayer.SEARCH_TYPE

    def get_checkbox_name(my):
        return LayerCheckboxWdg.CB_NAME

    def get_container_sobjects(my, container):

        layer_insts = LayerInstance.get_all_by_layer(container)
        asset_codes = SObject.get_values(layer_insts, 'asset_code', unique=True)
        search = Search( FlashAsset.SEARCH_TYPE )
        search.add_filters('code', asset_codes)
        sobjs = search.get_sobjects()

        return sobjs

       
  
    def init(my):

        if not my.check():
            return
        my.add(GeneralAppletWdg())

        my.flash = Flash()

        web = WebContainer.get_web()

        # create the necessary hidden widgets which the upload appliet
        # will look at
        search_type_wdg = HiddenWdg("search_type", my.get_search_type())
        my.add(search_type_wdg)
        uploaded_wdg = HiddenWdg(SObjectUploadCmd.FILE_NAMES)
        my.add(uploaded_wdg)
        description = HiddenWdg(SObjectUploadCmd.PUBLISH_COMMENT)
        my.add(description)
        value = uploaded_wdg.get_value()

        # register the command
        WebContainer.register_cmd( my.get_publish_command() )

        # get all of the selected
        selected = web.get_form_values(my.get_checkbox_name())
        if not selected:
            return
        containers = []
        for select in selected:
            container = Search.get_by_search_key(select)
            containers.append(container)

        # close all of the documents in the fl
        BaseAppServer.add_onload_script( my.flash.get_close_docs() )

        use_container = True

        # get the container assets
        for container in containers:

            sobjs = my.get_container_sobjects(container)
            if not sobjs:
                continue
           
            # start with container.
            if use_container:
                my.add_load_script(container, no_alerts=True)

            for sobj in sobjs:
                my.add_load_script(sobj, no_alerts=True)

            # publish after load
            my.add_stage_script(container) 

            my.close_docs()

            BaseAppServer.add_onload_script( \
                "document.form.elements['%s'].value = 'Populate assets in layers [%s]';" % (SObjectUploadCmd.PUBLISH_COMMENT, container.get_code() ) )

            ajax = AjaxCmd()
            ajax.register_cmd( my.get_publish_command() )
            # FiXME: some privileged knowledge here
            ajax.add_element_name("upload_files")
            ajax.set_option( "search_type", my.get_search_type() )
            BaseAppServer.add_onload_script( ajax.get_on_script() )
            
        BaseAppServer.add_onload_script("Common.pause(1000);document.form.upload_files.value = '';document.form.submit()")
        #BaseAppServer.add_onload_script("document.form.elements['%s'].value \
        #    = 'Populate assets in layers [%s]'; \
        #    document.form.submit()" % (SObjectUploadCmd.PUBLISH_COMMENT, \
        #    ', '.join(SObject.get_values(containers, 'id', unique=True))))
           


    def close_docs(my):
        BaseAppServer.add_onload_script("pyflash.close_docs()")


    def add_load_script(my, sobject, no_alerts=False):
        script = ''
        if sobject.is_general_asset():
            flash_import = FlashImport(sobject)
            flash_import.set_load_msg_id('')
            script = flash_import.get_stage_script()
        else:
            flash_load = FlashLoad(sobject)
            flash_load.set_load_msg_id('')
            script = flash_load.get_script()
            if no_alerts and script.startswith("alert"):
                return

        BaseAppServer.add_onload_script(script)


 
    def add_stage_script(my, container):
        '''rename the layers in flash and publish it as a new version
        of this layer'''

        flash_stage = FlashStage(container)
        stage_script = flash_stage.get_script()
        BaseAppServer.add_onload_script( stage_script )






class FlashLayerStageWdg(FlashSObjectStageWdg):

    def get_publish_command(my):
        return "pyasm.flash.FlashLayerPublishCmd"

    def get_search_type(my):
        return FlashLayer.SEARCH_TYPE

    def get_checkbox_name(my):
        return LayerCheckboxWdg.CB_NAME

    def get_container_sobjects(my, container):

        layer_insts = LayerInstance.get_all_by_layer(container)
        asset_codes = SObject.get_values(layer_insts, 'asset_code', unique=True)
        search = Search( FlashAsset.SEARCH_TYPE )
        search.add_filters('code', asset_codes)
        sobjs = search.get_sobjects()

        return sobjs



class FlashShotStageWdg(FlashSObjectStageWdg):

    def get_publish_command(my):
        return "pyasm.flash.FlashShotPublishCmd"

    def get_search_type(my):
        return FlashShot.SEARCH_TYPE

    def get_checkbox_name(my):
        return ShotCheckboxWdg.CB_NAME

    def get_container_sobjects(my, container):
        layer_insts = ShotInstance.get_all_by_shot(container)
        asset_codes = SObject.get_values(layer_insts, 'asset_code', unique=True)
        search = Search( FlashAsset.SEARCH_TYPE )
        search.add_filters('code', asset_codes)
        sobjs = search.get_sobjects()

        return sobjs



