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

__all__ = ['FlashRenderTableElementWdg', 'RenderCbk', 'FlashGenerateExecuteXml']

from pyasm.common import *
from pyasm.web import WebContainer
from pyasm.biz import Snapshot
from pyasm.widget import IconWdg, IconSubmitWdg, BaseTableElementWdg, \
    HiddenWdg, FilterSelectWdg, FloatMenuWdg
from pyasm.command import Command
from pyasm.command.remote_command import TacticDispatcher
from pyasm.web import Widget, SpanWdg, DivWdg, HtmlElement
from pyasm.search import SearchType, Search
from pyasm.flash import FlashLayerRenderCmd, FlashLayer
from pyasm.prod.web import IFrameLink
from pyasm.common import Container
from flash_input_wdg import FlashLayerCheckboxWdg, FlashShotCheckboxWdg


class FlashRenderTableElementWdg(IFrameLink):
     
    RENDER_CAM = 'flash_render_camera'
    CONTEXT_NAME = 'flash_render_context'
    def get_prefs(my):
        select = FilterSelectWdg(my.RENDER_CAM)
        search = Search(FlashLayer.SEARCH_TYPE)
        search.add_where("name ~* '.*camera.*'") 
        
        select.set_search_for_options(search, 'get_search_key()','name')
        select.add_empty_option()
        select.get_value()
        cam_span = SpanWdg(HtmlElement.b("Camera: "), css='med')
        cam_span.add(select)

        format_select = FilterSelectWdg(my.CONTEXT_NAME)
        format_select.set_option('labels', 'frame sequence|swf')
        format_select.set_option('values', \
            'FlashFinalSequenceRenderContext|FlashSwfRenderContext')
        format_select.get_value()
        format_span = SpanWdg(HtmlElement.b("Context: "), css='med')
        format_span.add(format_select)
        div = DivWdg()
        div.add(cam_span)
        div.add(HtmlElement.br())
        div.add(format_span)
        
        return div
        
        
    def get_title(my):
        widget = Widget()
        '''
        search_key_wdg = HiddenWdg('search_key')
        search_key_wdg.get_value()
        widget.add(search_key_wdg)
        '''
        WebContainer.register_cmd("pyasm.flash.widget.RenderCbk")
        if not my.get_option("no_button"):   
            render_button = IconSubmitWdg("Render", IconWdg.RENDER, True, \
            add_hidden=True)
           
            widget.add(render_button)
        else:
            widget.add("Frame Info")

        float_button = IconSubmitWdg("Render", IconWdg.RENDER, add_hidden=False)
        span = SpanWdg(float_button, css='med')
        span.add_style("border-left", "1px solid #777")
        WebContainer.get_float_menu().add(span)
        return widget


    


class XXRenderCbk(Command):
    '''initiates a render with properties'''
    
    def get_title(my):
        return "Render Submission"

    def check(my):
        web = WebContainer.get_web()
        if web.get_form_value("Render") == "":
            return False
        my.search_keys = web.get_form_values(FlashLayerCheckboxWdg.CB_NAME)
        if my.search_keys:
            return True
        else:
            return False

    def execute(my):
        from pyasm.flash.widget import FlashLayerCheckboxWdg    
        web = WebContainer.get_web()
        cam_search_key = web.get_form_value( FlashRenderTableElementWdg.RENDER_CAM)
        context_name = web.get_form_value( FlashRenderTableElementWdg.CONTEXT_NAME)
        
        sobject = Search.get_by_search_key(my.search_keys[0])
        
        render = FlashLayerRenderCmd()
        render.set_search_keys(my.search_keys)
        render.set_cam_search_key(cam_search_key)
        render.set_context_name(context_name)
        render.set_project( SearchType.get_project() )
        
        #render.execute()
        
        dispatch = TacticDispatcher()
        dispatch.set_description("Flash Render: %s" % sobject.get_code())
        dispatch.execute_slave(render)
        
	my.description = "Submitted: %s" % ", ".join(my.search_keys)





#class RenderSubmitCbk(Command):
class RenderCbk(Command):
    '''initiates a render with properties'''
    
    def get_title(my):
        return "Render Submission"

    def check(my):
        web = WebContainer.get_web()
        if web.get_form_value("Render") == "":
            return False
        my.search_keys = web.get_form_values(FlashShotCheckboxWdg.CB_NAME)

        #my.search_keys = ['flash/shot?project=flash|42']

        if my.search_keys:
            return True
        else:
            return False

    def execute(my):
        from pyasm.flash.widget import FlashLayerCheckboxWdg    
        web = WebContainer.get_web()
        cam_search_key = web.get_form_value( FlashRenderTableElementWdg.RENDER_CAM)
        # FIXME: why is this called "context"
        context_name = web.get_form_value( FlashRenderTableElementWdg.CONTEXT_NAME)

        # submit all the selected sobjects
        context = "publish"
        for search_key in my.search_keys:
            sobject = Search.get_by_search_key(search_key)

            snapshot = Snapshot.get_latest_by_sobject(sobject, context)
            if not snapshot:
                raise TacticException("No checkins of context '%s' for '%s' exists" % (context, sobject.get_code() ) )
            render = FlashGenerateExecuteXml(sobject.get_code())
            render.set_snapshot_code(snapshot.get_code())
            
            #render.execute()
           
            # store this in the appropriate queue
            dispatch = TacticDispatcher()
            dispatch.set_description("Flash Render: %s" % sobject.get_code())
            dispatch.execute_slave(render)
            
        my.description = "Submitted: %s" % ", ".join(my.search_keys)



class FlashGenerateExecuteXml(Command):

    '''This is the command stored in the queue.  It doesn't do much except
    convert the command in to an execute_xml.  This could be done on the
    callback the submitted the queue job, but the queue currently on stores
    picked TACTIC commands and not execute_xml'''

    def __init__(my, shot_code):
        # this gets pickled
        my.shot_code = shot_code
        my.execute_xml = "<execute/>"
        my.project_code = None
        my.snapshot_code = None

        super(FlashGenerateExecuteXml,my).__init__()
        

    def set_snapshot_code(my, snapshot_code):
        my.snapshot_code = snapshot_code

    def set_project(my, project_code):
        my.project_code = project_code


    def get_execute_xml(my):
        return my.execute_xml
    

    def execute(my):

        if my.project_code:
            Project.set_project(project_code)

        snapshot = Snapshot.get_by_code(my.snapshot_code)

        # get the loader implementation
        from pyasm.prod.load import ProdLoaderContext
        loader_context = ProdLoaderContext()
        loader_context.set_context(snapshot.get_value("context"))

        # pass on any message options for the loader
        #if options != "":
        #    loader_context.set_options(options)

        loader = loader_context.get_loader(snapshot)
        loader.execute()

        my.execute_xml = loader.get_execute_xml().to_string()



