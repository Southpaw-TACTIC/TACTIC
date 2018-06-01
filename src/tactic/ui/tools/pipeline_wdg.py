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

__all__ = ['PipelineToolWdg', 'PipelineToolCanvasWdg', 'PipelineEditorWdg', 'PipelinePropertyWdg','PipelineSaveCbk', 'ConnectorInfoWdg', 'BaseInfoWdg', 'ProcessInfoWdg', 'PipelineInfoWdg', 'ProcessInfoCmd', 'ScriptEditWdg', 'ScriptSettingsWdg']

import re
import os
from tactic.ui.common import BaseRefreshWdg

from pyasm.common import Environment, Common
from pyasm.biz import Pipeline, Project
from pyasm.command import Command
from pyasm.web import DivWdg, WebContainer, Table, SpanWdg, HtmlElement
from pyasm.search import Search, SearchType, SearchKey, SObject
from tactic.ui.panel import FastTableLayoutWdg
from pyasm.widget import SwapDisplayWdg

from pyasm.widget import ProdIconButtonWdg, IconWdg, TextWdg, CheckboxWdg, HiddenWdg, SelectWdg, TextAreaWdg

from tactic.ui.container import DialogWdg, TabWdg, SmartMenu, Menu, MenuItem, ResizableTableWdg
from tactic.ui.widget import ActionButtonWdg, SingleButtonWdg, IconButtonWdg
from tactic.ui.input import TextInputWdg, ColorInputWdg, LookAheadTextInputWdg
from pipeline_canvas_wdg import PipelineCanvasWdg
from client.tactic_client_lib import TacticServerStub

class PipelineToolWdg(BaseRefreshWdg):
    '''This is the entire tool, including the sidebar and tabs, used to
    edit the various pipelines that exists'''

    def init(self):
        # to display pipelines of a certain search_type on load
        self.search_type = self.kwargs.get('search_type')
        self.search_key = self.kwargs.get('search_key')

    def get_display(self):

        top = self.top
        self.set_as_panel(top)
        top.add_class("spt_pipeline_tool_top")
        #top.add_style("margin-top: 10px")

        inner = DivWdg()
        top.add(inner)

        show_pipelines = self.kwargs.get("show_pipeline_list")

        #table = Table()
        table = ResizableTableWdg()
        inner.add(table)
        table.add_style("width: 100%")
        table.add_color("background", "background")
        table.add_color("color", "color")



        table.add_row()
        if show_pipelines not in [False, 'false']:
            left = table.add_cell()
        right = table.add_cell()
        info = table.add_cell()


        """
        container = DivWdg()
        inner.add(container)
        container.add_style("display: flex")
        container.add_style("flex-direction: row")
        container.add_style("flex-wrap: nowrap")
        container.add_style("justify-content: center")
        container.add_style("align-items: stretch")
        container.add_style("width: 100%")
        container.add_style("height: 100%")

        if show_pipelines not in [False, 'false']:
            left = DivWdg()
            container.add(left)
            left.add_style("overflow-y: auto")
            left.add_style("overflow-x: hidden")

        right = DivWdg()
        right.add_style("flex-grow: 2")

        container.add(right)
        info = DivWdg()
        container.add(info)


        container.add_style("width: 100%")
        container.add_color("background", "background")
        """





        # create two events
        save_event = top.get_unique_event()
        #save_new_event = '%s_new' % save_event
        save_new_event = save_event

        pipeline_code = self.kwargs.get("pipeline")


        if pipeline_code:
            pipeline = Search.get_by_code("sthpw/pipeline", pipeline_code)
            if pipeline:
                pipeline_name = pipeline.get("name")
                inner.add_behavior( {
                'type': 'load',
                'pipeline_code': pipeline_code,
                'pipeline_name': pipeline_name,
                'cbjs_action': '''
                setTimeout( function() {
                var top = bvr.src_el;
                var start = top.getElement(".spt_pipeline_editor_start");
                start.setStyle("display", "none");

                var top = bvr.src_el.getParent(".spt_pipeline_tool_top");
                var wrapper = top.getElement(".spt_pipeline_wrapper");
                spt.pipeline.init_cbk(wrapper);

                spt.pipeline.clear_canvas();
                spt.pipeline.import_pipeline(bvr.pipeline_code);

                var value = bvr.pipeline_code;
                var title = bvr.pipeline_name;

                var text = top.getElement(".spt_pipeline_editor_current2");
                //text.value = title;
                var html = "<span class='hand spt_pipeline_link' spt_pipeline_code='"+bvr.pipeline_code+"'>"+title+"</span>";
                text.innerHTML = html;

                spt.pipeline.set_current_group(value);


                var info = top.getElement(".spt_pipeline_tool_info");
                if (info) {
                    var group_name = spt.pipeline.get_current_group();

                    var class_name = 'tactic.ui.tools.PipelineInfoWdg';
                    var kwargs = {
                        pipeline_code: group_name,
                    }

                    spt.panel.load(info, class_name, kwargs);
                }


                var editor_top = bvr.src_el.getParent(".spt_pipeline_editor_top");
                if (editor_top) {
                    editor_top.removeClass("spt_has_changes");
                }


                }, 0);
                '''
                } )


        inner.add_behavior( {
        'type': 'listen',
        'event_name': save_event,
        'cbjs_action': '''
        var data = bvr.firing_data;
        var search_key = data.search_key;
        var sobject = data.sobject;

        var group_name = sobject.code;
        var color = sobject.color;

        var top = bvr.src_el;
        var wrapper = top.getElement(".spt_pipeline_wrapper");
        spt.pipeline.init_cbk(wrapper);

        // refresh the sidebar
        var list = top.getElement(".spt_pipeline_list");
        spt.panel.refresh(list);

        var start = top.getElement(".spt_pipeline_editor_start");
        start.setStyle("display", "none");

        spt.pipeline.clear_canvas();
        spt.pipeline.import_pipeline(group_name);

        '''

        } )


        self.settings = self.kwargs.get('settings') or []
        if self.settings and isinstance(self.settings, basestring):
            self.settings = self.settings.split("|")




        if show_pipelines not in [False, 'false']:
            left.add_style("width: 200px")
            left.add_style("min-width: 100px")
            left.add_style("vertical-align: top")

            expression = self.kwargs.get("expression")

            pipeline_list = PipelineListWdg(save_event=save_event, save_new_event=save_new_event, settings=self.settings, expression=expression )
            left.add(pipeline_list)



        show_help = self.kwargs.get('show_help') or True
        width = self.kwargs.get("width")
        pipeline_wdg = PipelineEditorWdg(height=self.kwargs.get('height'), width=width, save_new_event=save_new_event, show_help=show_help, show_gear=self.kwargs.get('show_gear'))
        right.add(pipeline_wdg)
        pipeline_wdg.add_style("position: relative")
        pipeline_wdg.add_style("z-index: 0")
        #pipeline_wdg.add_style("opacity", 0.3)

        start_div = DivWdg()
        start_div.add_class("spt_pipeline_editor_start")
        right.add(start_div)
        start_div.add_style("position: absolute")
        start_div.add_style("height: 100%")
        start_div.add_style("width: 100%")
        start_div.add_style("top: 0px")
        start_div.add_style("background: rgba(240,240,240,0.8)")
        start_div.add_border()
        start_div.add_style("z-index: 100")

        msg_div = DivWdg()

        start_div.add(msg_div)
        msg_div.add("Select a workflow<br/><br/>or<br/><br/>Create a new one")
        msg_div.add_style("width: 300px")
        msg_div.add_style("height: 150px")
        msg_div.add_style("margin-top: 20%")
        msg_div.add_style("margin: 20% auto")
        msg_div.add_border()
        msg_div.add_color("background", "background3")
        msg_div.add_style("padding-top: 40px")
        msg_div.add_style("text-align: center")
        msg_div.add_style("font-size: 1.2em")
        msg_div.add_style("font-weight: bold")

        right.add_style("position: relative")



        # NOTE: the canvas in PipelineCanvasWdg requires a set size ... it does not respond
        # well to sizes like 100% or auto.  Unless this is fixed, we cannot have a table
        # responsively respond to a changing window size.

        #info.add_style("display: none")
        info.add_class("spt_pipeline_tool_info")
        info.add_class("spt_panel") 
        info.add_style("width: 400px")
        info.add_style("min-width: 400px")
        info.add_style("max-width: 400px")

        info_wdg = DivWdg()
        info.add(info_wdg)

        info_wdg.add_border()
        info_wdg.add_style("height: 100%")
        info_wdg.add_class("spt_resizable")

        show_info_tab = self.kwargs.get("show_info_tab")
        show_info_tab = True
        if show_info_tab in ['false', False]:
            show_info_tab = False
        else:
            show_info_tab = True



        if self.kwargs.get("is_refresh"):
            return inner
        else:
            return top




class PipelineTabWdg(BaseRefreshWdg):


    def get_display(self):
        self.search_type = self.kwargs.get('search_type')
        self.search_key = self.kwargs.get('search_key')

        config_xml = '''
        <config>
        <tab>
          <element name='pipelines'>
            <display class='tactic.ui.panel.FastTableLayoutWdg'>
                <search_type>sthpw/pipeline</search_type>
                <view>tool</view>
                <expression>@SOBJECT(sthpw/pipeline['project_code',$PROJECT])</expression>
                <show_search>false</show_search>
            </display>
          </element>
        </tab>
        </config>
        '''
        tab = TabWdg(config_xml=config_xml, extra_menu=self.get_extra_tab_menu())


        # add onload action at the very end
        if self.search_type:
            load_cbjs_action = '''
            var server = TacticServerStub.get();
            var pipeline_codes = server.eval("@GET(sthpw/pipeline['search_type','%s'].code)");
            
            var src_el = spt.get_element(document, '.spt_pipeline_list');
            var firing_el = src_el;
            for (var k=0; k<pipeline_codes.length; k++)
                spt.named_events.fire_event('pipeline_' + pipeline_codes[k] + '|click', bvr);

            '''%( self.search_type)


            tab.add_behavior({
                      'type':'load',
                      'cbjs_action':  load_cbjs_action})

        elif self.search_key:
            load_cbjs_action = '''
            var server = TacticServerStub.get();
            var so = server.get_by_search_key('%s');
            if (so)
                spt.named_events.fire_event('pipeline_' + so.code + '|click', bvr);

            '''%( self.search_key)


            tab.add_behavior({
                      'type':'load',
                      'cbjs_action':  load_cbjs_action})


        return tab




    def get_extra_tab_menu(self):
        menu = Menu(width=180)

        menu_item = MenuItem(type='title', label='Raw Data')
        menu.add(menu_item)

        menu_item = MenuItem(type='action', label='Show Site Wide Workflows')
        menu_item.add_behavior( {
        'cbjs_action': '''
        var class_name = 'tactic.ui.panel.ViewPanelWdg';
        var kwargs = {
            search_type: 'sthpw/pipeline',
            view: 'site_wide',
            show_search: 'false',
            expression: "@SOBJECT(sthpw/pipeline['project_code','is','NULL'])"
        }
        var header = spt.smenu.get_activator(bvr);
        var top = header.getParent(".spt_tab_top");
        spt.tab.set_tab_top(top);
        spt.tab.add_new("site_wide_pipeline", "Site Wide Workflows", class_name, kwargs);

        '''
        } )
        menu.add(menu_item)



        menu_item = MenuItem(type='action', label='Show Raw Processes')
        menu_item.add_behavior( {
        'cbjs_action': '''
        var class_name = 'tactic.ui.panel.ViewPanelWdg';
        var kwargs = {
            search_type: 'config/process',
            view: 'table',
        }
        var header = spt.smenu.get_activator(bvr);
        var top = header.getParent(".spt_tab_top");
        spt.tab.set_tab_top(top);
        spt.tab.add_new("processes", "Processes", class_name, kwargs);

        '''
        } )
        menu.add(menu_item)


        menu_item = MenuItem(type='action', label='Show Raw Naming')
        menu_item.add_behavior( {
        'cbjs_action': '''
        var class_name = 'tactic.ui.panel.ViewPanelWdg';
        var kwargs = {
            search_type: 'config/naming',
            view: 'table',
        }
        var header = spt.smenu.get_activator(bvr);
        var top = header.getParent(".spt_tab_top");
        spt.tab.set_tab_top(top);
        spt.tab.add_new("naming", "Naming", class_name, kwargs);

        '''
        } )
        menu.add(menu_item)

        menu_item = MenuItem(type='action', label='Show Raw Triggers')
        menu_item.add_behavior( {
        'cbjs_action': '''
        var class_name = 'tactic.ui.panel.ViewPanelWdg';
        var kwargs = {
            search_type: 'config/trigger',
            view: 'table',
        }
        var header = spt.smenu.get_activator(bvr);
        var top = header.getParent(".spt_tab_top");
        spt.tab.set_tab_top(top);
        spt.tab.add_new("trigger", "Triggers", class_name, kwargs);

        '''
        } )
        menu.add(menu_item)


        menu_item = MenuItem(type='action', label='Show Raw Notification')
        menu_item.add_behavior( {
        'cbjs_action': '''
        var class_name = 'tactic.ui.panel.ViewPanelWdg';
        var kwargs = {
            search_type: 'sthpw/notification',
            view: 'table',
        }
        var header = spt.smenu.get_activator(bvr);
        var top = header.getParent(".spt_tab_top");
        spt.tab.set_tab_top(top);
        spt.tab.add_new("notification", "Notifications", class_name, kwargs);

        '''
        } )
        menu.add(menu_item)


        return menu



class PipelineListWdg(BaseRefreshWdg):

        
    def init(self):
        self.save_event = self.kwargs.get("save_event")

        self.save_new_event = self.kwargs.get("save_new_event")

        self.settings = self.kwargs.get("settings") or []
        if self.settings and isinstance(self.settings, basestring):
            self.settings = self.settings.split("|")


    def get_display(self):

        top = self.top
        top.add_class("spt_pipeline_list")
        self.set_as_panel(top)
        top.add_style("position: relative")
        top.add_style("padding: 0px 0px")

        title_div = DivWdg()


        button = ActionButtonWdg(title="Add", tip="Add a new workflow", size='small')
        button.add_style("position: absolute")
        button.add_style("top: 5px")
        button.add_style("right: 5px")

        button.add_behavior( {
        'type': 'click_up',
        'save_event': self.save_new_event,
        'cbjs_action': '''
        var class_name = 'tactic.ui.panel.EditWdg';
        var kwargs = {
            search_type: 'sthpw/pipeline',
            view: 'insert',
            show_header: false,
            single: true,
            save_event: bvr.save_event
        }
        spt.api.load_popup("Add New Workflow", class_name, kwargs);
        '''
        } )



        title_div.add(button)

        top.add(title_div)
        title_div.add_style("height: 30px")
        title_div.add_style("padding-left: 5px")
        title_div.add_style("padding-top: 10px")
        #title_div.add_color("background", "background", -10)
        title_div.add("Workflows")
        title_div.add_style("font-size: 16px")
        title_div.add("<hr/>")



        top.add("<br/>")

        pipelines_div = DivWdg()
        top.add(pipelines_div)
        pipelines_div.add_class("spt_resizable")

        pipelines_div.add_style("overflow-x: hidden")
        pipelines_div.add_style("min-height: 290px")
        pipelines_div.add_style("min-width: 100px")
        pipelines_div.add_style("width: 200px")
        pipelines_div.add_style("height: auto")

        inner = DivWdg()
        pipelines_div.add(inner)
        inner.add_class("spt_pipeline_list_top")

        inner.add_style("display: flex")
        inner.add_style("flex-direction: column")

        inner.add_style("width: 100%")
        inner.add_style("height: auto")
        inner.add_style("max-height: 500px")


        # add in a context menu
        menu = self.get_pipeline_context_menu()
        menus = [menu.get_data()]
        menus_in = {
            'PIPELINE_CTX': menus,
        }
        from tactic.ui.container.smart_menu_wdg import SmartMenu
        SmartMenu.attach_smart_context_menu( pipelines_div, menus_in, False )


        project_code = Project.get_project_code()


        # template pipeline
        if "template" in self.settings:
            search = Search("sthpw/pipeline")
            search.add_filter("project_code", project_code)
            search.add_filter("code", "%s/__TEMPLATE__" % project_code)
            pipeline = search.get_sobject()
            if not pipeline:
                pipeline = SearchType.create("sthpw/pipeline")
                pipeline.set_value("code", "%s/__TEMPLATE__" % project_code)
                pipeline.set_project()
            pipeline.set_value("search_type", "")
            pipeline.set_value("name", "Template Processes")
            pipeline.commit()

            pipeline_div = self.get_pipeline_wdg(pipeline)
            inner.add(pipeline_div)


            inner.add("<br/>")




        # project_specific pipelines
        content_div = DivWdg()
        content_div.add_style('padding-top: 6px') 
        inner.add(content_div)

        try:
            expression = self.kwargs.get("expression")
            if expression:
                result = Search.eval(expression)
                if isinstance(result, Search):
                    search = result
                    search.add_filter("project_code", project_code)

                    search.add_op("begin")
                    search.add_filter("search_type", "sthpw/task", op="!=")
                    # This pretty weird that != does not find NULL values
                    search.add_filter("search_type", "NULL", op='is', quoted=False)
                    search.add_op("or")

                    search.add_filter("code", "%s/__TEMPLATE__" % project_code, op="!=")
                    search.add_op("begin")
                    search.add_filters("type", ["sobject","template"], op="not in")
                    search.add_filter("type", "NULL", op="is", quoted=False)
                    search.add_op("or")

                    search.add_order_by("search_type")
                    search.add_order_by("name")

                    pipelines = search.get_sobjects()
                else:
                    pipelines = result



            else:
                search = Search("sthpw/pipeline")
                search.add_filter("project_code", project_code)

                search.add_op("begin")
                search.add_filter("search_type", "sthpw/task", op="!=")
                # This pretty weird that != does not find NULL values
                search.add_filter("search_type", "NULL", op='is', quoted=False)
                search.add_op("or")

                search.add_filter("code", "%s/__TEMPLATE__" % project_code, op="!=")

                search.add_op("begin")
                search.add_filters("type", ["sobject","template"], op="not in")
                search.add_filter("type", "NULL", op="is", quoted=False)
                search.add_op("or")

                search.add_order_by("search_type")
                search.add_order_by("name")

                pipelines = search.get_sobjects()

            last_search_type = None
            for pipeline in pipelines:
                if pipeline.get_value("parent_process"):
                    continue

                search_type = pipeline.get_value("search_type")
                if not search_type:
                    continue

                if not last_search_type or last_search_type != search_type:
                    if last_search_type:
                        content_div.add("<hr/>")

                    if search_type:
                        search_type_obj = SearchType.get(search_type)
                        title = search_type_obj.get_title()
                        title = Common.pluralize(title)
                    else:
                        title = "Workflows"
                    #inner.add(title)

                    stype_div = DivWdg()
                    content_div.add(stype_div)
                    #stype_div.add_style("margin: 5px 0px 5px 5px")

                    swap = SwapDisplayWdg()
                    stype_div.add(swap)
                    swap.add_style("float: left")
                    swap.add_style("margin-top: -2px")

                    stype_div.add("<b>%s</b>" % title)

                    stype_content_div = DivWdg()
                    #stype_content_div.add_style('padding-left: 8px') 
                    stype_content_div.add_style('padding-top: 6px; padding-bottom: 3px;') 

                    SwapDisplayWdg.create_swap_title(stype_div, swap, stype_content_div, is_open=True)
                    content_div.add(stype_content_div)


                last_search_type = search_type


                # build each pipeline menu item
                pipeline_div = self.get_pipeline_wdg(pipeline)
                stype_content_div.add(pipeline_div)

            if not pipelines:
                no_items = DivWdg()
                no_items.add_style("padding: 3px 0px 3px 20px")
                content_div.add(no_items)
                no_items.add("<i>-- No Items --</i>")

        except Exception as  e:
            print("WARNING: ", e)
            none_wdg = DivWdg("<i>&nbsp;&nbsp;-- Error --</i>")
            none_wdg.add("<div>%s</div>" % str(e))
            none_wdg.add_style("font-size: 11px")
            none_wdg.add_color("color", "color", 20)
            none_wdg.add_style("padding", "5px")
            content_div.add( none_wdg )
            raise

        inner.add("<br clear='all'/>")

        # task status pipelines
        if not self.settings or "task" in self.settings:

            search = Search("sthpw/pipeline")
            search.add_filter("project_code", project_code)
            search.add_op("begin")
            search.add_filter("search_type", "sthpw/task")
            #search.add_filter("search_type", "NULL", op='is', quoted=False)
            search.add_op("or")
            search.add_filter("code", "%s/__TEMPLATE__" % project_code, op="!=")
            search.add_filter("type", "template", op="!=")
            pipelines = search.get_sobjects()

            if pipelines:

                swap = SwapDisplayWdg()
                inner.add(swap)
                swap.add_style("float: left")

                title = DivWdg("<b>Task Status Workflows</b> <i>(%s)</i>" % len(pipelines))
                title.add_style("padding-bottom: 2px")
                title.add_style("padding-top: 3px")
                inner.add(title)
                content_div = DivWdg()
                content_div.add_styles('padding-left: 8px; padding-top: 6px') 
                SwapDisplayWdg.create_swap_title(title, swap, content_div, is_open=False)
                inner.add(content_div)


                colors = {}
                for pipeline in pipelines:
                    pipeline_div = self.get_pipeline_wdg(pipeline)
                    content_div.add(pipeline_div)
                    colors[pipeline.get_code()] = pipeline.get_value("color")

                if not pipelines:
                    no_items = DivWdg()
                    no_items.add_style("padding: 3px 0px 3px 20px")
                    content_div.add(no_items)
                    no_items.add("<i>-- No Items --</i>")



                inner.add("<br clear='all'/>")






        if not self.settings or "misc" in self.settings:

            search = Search("sthpw/pipeline")
            search.add_filter("project_code", project_code)
            search.add_op("begin")
            search.add_filter("search_type", "NULL", op='is', quoted=False)
            search.add_op("or")
            search.add_filter("code", "%s/__TEMPLATE__" % project_code, op="!=")
            search.add_filter("type", "template", op="!=")
            pipelines = search.get_sobjects()

            if pipelines:

                # misc status pipelines
                swap = SwapDisplayWdg()
                inner.add(swap)
                swap.add_style("float: left")

                title = DivWdg("<b>Misc Workflows</b>")
                title.add_style("padding-bottom: 2px")
                title.add_style("padding-top: 3px")
                inner.add(title)
                content_div = DivWdg()
                content_div.add_styles('padding-top: 6px') 
                SwapDisplayWdg.create_swap_title(title, swap, content_div, is_open=True)
                inner.add(content_div)

                colors = {}
                for pipeline in pipelines:
                    pipeline_div = self.get_pipeline_wdg(pipeline)
                    content_div.add(pipeline_div)
                    colors[pipeline.get_code()] = pipeline.get_value("color")

                if not pipelines:
                    no_items = DivWdg()
                    no_items.add_style("padding: 3px 0px 3px 20px")
                    content_div.add(no_items)
                    no_items.add("<i>-- No Items --</i>")




        show_site_wide_pipelines = True

        if (not self.settings or "misc" in self.settings) and show_site_wide_pipelines:
            # site-wide  pipelines
            search = Search("sthpw/pipeline")
            search.add_filter("project_code", "NULL", op="is", quoted=False)
            pipelines = search.get_sobjects()

            if pipelines:
                inner.add("<br clear='all'/>")

                swap = SwapDisplayWdg()

                title = DivWdg()
                inner.add(swap)
                swap.add_style("margin-top: -2px")
                inner.add(title)
                swap.add_style("float: left")
                title.add("<b>Site Wide Workflows</b> <i>(%s)</i><br/>" % len(pipelines))
              
                site_wide_div = DivWdg()
                site_wide_div.add_styles('padding-top: 6px') 
                SwapDisplayWdg.create_swap_title(title, swap, site_wide_div, is_open=False)

                colors = {}
                inner.add(site_wide_div)
                site_wide_div.add_class("spt_pipeline_list_site")

                for pipeline in pipelines:
                    pipeline_div = self.get_pipeline_wdg(pipeline)
                    site_wide_div.add(pipeline_div)
                    colors[pipeline.get_code()] = pipeline.get_value("color")


        is_admin = Environment.get_security().is_admin()
        if is_admin:

            search = Search("sthpw/pipeline")
            search.add_filter("type", "template")
            pipelines = search.get_sobjects()

            if pipelines:
                inner.add("<br clear='all'/>")

                # misc status pipelines
                swap = SwapDisplayWdg()
                inner.add(swap)
                swap.add_style("float: left")

                title = DivWdg("<b>Templates</b> <i>(%s)</i>" % len(pipelines))
                title.add_style("padding-bottom: 2px")
                title.add_style("padding-top: 3px")
                inner.add(title)
                content_div = DivWdg()
                content_div.add_styles('padding-top: 6px') 
                SwapDisplayWdg.create_swap_title(title, swap, content_div, is_open=False)
                inner.add(content_div)

                colors = {}
                for pipeline in pipelines:
                    pipeline_div = self.get_pipeline_wdg(pipeline)
                    content_div.add(pipeline_div)
                    colors[pipeline.get_code()] = pipeline.get_value("color")

                if not pipelines:
                    no_items = DivWdg()
                    no_items.add_style("padding: 3px 0px 3px 20px")
                    content_div.add(no_items)
                    no_items.add("<i>-- No Items --</i>")


        return top




    def get_pipeline_wdg(self, pipeline):
        '''build each pipeline menu item'''

        pipeline_div = DivWdg()
        pipeline_div.add_class('spt_pipeline_link')
        pipeline_div.add_attr('spt_pipeline', pipeline.get_code())
        pipeline_div.add_style("padding: 3px")
        pipeline_div.add_class("hand")
        name = pipeline.get_value("name")
        description = pipeline.get_value("description")
        if not description:
            description = pipeline.get_code()
        
        pipeline_div.add_attr("title", description)

        color = pipeline_div.get_color("background", -20)
        pipeline_div.add_behavior( {
            'type': 'hover',
            'color': color,
            'cbjs_action_over': '''
            bvr.src_el.setStyle("background", bvr.color);
            ''',
            'cbjs_action_out': '''
            bvr.src_el.setStyle("background", "");
            ''',
        } )

        color_div = DivWdg()
        color_div.add_style("height: 20px")
        color_div.add_style("width: 20px")
        color_div.add_style("float: left")
        color = pipeline.get_value("color")
        if not color:
            color = ""
        color_div.add_border()
        color_div.add_style("background: %s" % color)
        pipeline_div.add(color_div)

        pipeline_code = pipeline.get_code()
        if name:
            title = name
        else:
            title = pipeline_code.split("/")[-1]
        pipeline_div.add("<div style='display: inline-block; margin-top: 3px'>&nbsp;&nbsp;&nbsp;%s</div>" % title)

        pipeline_div.add_behavior( {
        'type': 'listen',
        'pipeline_code': pipeline_code,
        'project_code': Project.get_project_code(),
        'title': title,
        'event_name': 'pipeline_%s|click' % pipeline_code,
        'cbjs_action': '''
        var top = null;
        // they could be different when inserting or just clicked on
        [bvr.firing_element, bvr.src_el].each(function(el) {
                top = el.getParent(".spt_pipeline_tool_top");
                if (top) return top;
            }
        );
        if (!top) {
            top = spt.get_element(document, '.spt_pipeline_tool_top');
        }


        var editor_top = top.getElement(".spt_pipeline_editor_top");


        var ok = function () {
            editor_top.removeClass("spt_has_changes");

            var wrapper = top.getElement(".spt_pipeline_wrapper");
            spt.pipeline.init_cbk(wrapper);

            var start_el = top.getElement(".spt_pipeline_editor_start")
            start_el.setStyle("display", "none")

            spt.pipeline.clear_canvas();

            spt.pipeline.import_pipeline(bvr.pipeline_code);


            // add to the current list
            var value = bvr.pipeline_code;
            var title = bvr.title;

            
            var text = top.getElement(".spt_pipeline_editor_current2");

            var html = "<span class='hand spt_pipeline_link' spt_pipeline_code='"+bvr.pipeline_code+"'>"+bvr.title+"</span>";


            var breadcrumb = bvr.breadcrumb;
            if (breadcrumb) {
                text.innerHTML = breadcrumb + " / " + html;
            }
            else {
                text.innerHTML = html;
            }

            spt.pipeline.set_current_group(value);



            var info = top.getElement(".spt_pipeline_tool_info");
            if (info) {
                var group_name = spt.pipeline.get_current_group();

                var class_name = 'tactic.ui.tools.PipelineInfoWdg';
                var kwargs = {
                    pipeline_code: group_name,
                }
                spt.panel.load(info, class_name, kwargs);
            }


            editor_top.removeClass("spt_has_changes");

        };

        var save = function(){
            editor_top.removeClass("spt_has_changes");
            var wrapper = editor_top.getElement(".spt_pipeline_wrapper");
            spt.pipeline.init_cbk(wrapper);

            var group_name = spt.pipeline.get_current_group();
            
            var data = spt.pipeline.get_data();
            var color = data.colors[group_name];

            server = TacticServerStub.get();
            spt.app_busy.show("Saving project-specific pipeline ["+group_name+"]",null);
            
            var xml = spt.pipeline.export_group(group_name);
            var search_key = server.build_search_key("sthpw/pipeline", group_name);
            try {
                var args = {search_key: search_key, pipeline:xml, color:color, project_code: bvr.project_code};
                server.execute_cmd('tactic.ui.tools.PipelineSaveCbk', args);
            } catch(e) {
                spt.alert(spt.exception.handler(e));
            }

            spt.named_events.fire_event('pipeline|save', {});

            spt.app_busy.hide();

            editor_top.removeClass("spt_has_changes");
        }


        var current_group_name = spt.pipeline.get_current_group();
        var group_name = bvr.pipeline_code;
        if (editor_top && editor_top.hasClass("spt_has_changes")) {
            spt.confirm("Current workflow has changes.  Do you wish to continue without saving?", save, ok, {okText: "Save", cancelText: "Don't Save"});
        //}
        //else if (current_group_name == group_name) {
        //    spt.confirm("Reload current workflow?", ok, null); 
        } else {
            ok();
        }


        '''
        } )

        
        pipeline_div.add_behavior( {'type': 'click_up',
            
            'event': 'pipeline_%s|click' %pipeline_code,
            'cbjs_action': '''
             spt.named_events.fire_event(bvr.event, bvr);
             '''
             })

        pipeline_div.add("<br clear='all'/>")

        pipeline_div.add_attr("spt_element_name", pipeline_code)
        from tactic.ui.container.smart_menu_wdg import SmartMenu
        SmartMenu.assign_as_local_activator( pipeline_div, 'PIPELINE_CTX' )

        return pipeline_div




    def get_pipeline_context_menu(self):

        menu = Menu(width=180)
        menu.set_allow_icons(False)
        menu.set_setup_cbfn( 'spt.smenu_ctx.setup_cbk' )


        menu_item = MenuItem(type='title', label='Actions')
        menu.add(menu_item)


        menu_item = MenuItem(type='action', label='Edit Data')
        menu_item.add_behavior( {
            'save_event': self.save_event,
            'cbjs_action': '''
            var activator = spt.smenu.get_activator(bvr);
            var code = activator.getAttribute("spt_pipeline");
            var search_type = 'sthpw/pipeline';
            var kwargs = {
                'search_type': search_type,
                'code': code,
                'view': 'pipeline_edit_tool',
                'edit_event': bvr.save_event,
                'title': "Save changes to Workflow (" + code + ")"
            };
            var class_name = 'tactic.ui.panel.EditWdg';
            spt.panel.load_popup("Edit Workflow Details", class_name, kwargs);
            '''
        } )
        menu.add(menu_item)

        """
        menu_item = MenuItem(type='action', label='Copy')
        menu_item.add_behavior( {
            'cbjs_action': '''
            var activator = spt.smenu.get_activator(bvr);
            var code = activator.getAttribute("spt_pipeline");
            var search_type = 'sthpw/pipeline';
            var kwargs = {
                'search_type': search_type,
                //'code': code,
                'view': 'pipeline_edit_tool',
                'edit_event': bvr.save_event,
                'title': "Save changes to Workflow (" + code + ")",
                'default': {
                    'name': '',
                    'code': '',
                }
            };
            //var class_name = 'tactic.ui.toosls.PipelineCopyCmd';
            var class_name = 'tactic.ui.panel.EditWdg';
            spt.panel.load_popup("Copy Workflow", class_name, kwargs);
            '''
        } )
        menu.add(menu_item)
        """


        menu_item = MenuItem(type='separator')
        menu.add(menu_item)
        

        menu_item = MenuItem(type='action', label='Delete')
        menu_item.add_behavior( {
            'cbjs_action': '''
            var activator = spt.smenu.get_activator(bvr);
            var top = activator.getParent(".spt_pipeline_tool_top");
            var code = activator.getAttribute("spt_pipeline");

            var server = TacticServerStub.get();
            var pipeline = server.get_by_code("sthpw/pipeline", code);
            var name = pipeline.name;
            if (!name) {
                name = pipeline.code;
            }

            var ok = function() {
                server.delete_sobject(pipeline);
                spt.panel.refresh(top);
     
            }

            spt.confirm("Confirm to delete workflow ["+name+"]", ok);
            '''
        } )
        menu.add(menu_item)




        return menu




class PipelineToolCanvasWdg(PipelineCanvasWdg):

    def get_node_behaviors(self):
        behavior = {
        'type': 'click_up',
        'cbjs_action': '''
        spt.pipeline.init(bvr);
        var node = bvr.src_el;

        var node_name = spt.pipeline.get_node_name(node);
        var group_name = spt.pipeline.get_current_group();
        var top = bvr.src_el.getParent(".spt_pipeline_tool_top");
        var info = top.getElement(".spt_pipeline_tool_info");
        if (!info) {
            return;
        }

        var node_type = spt.pipeline.get_node_type(node);
        if (node.hasClass("spt_pipeline_unknown")) {
            node_type = "unknown";
        }

        var class_name = 'tactic.ui.tools.ProcessInfoWdg';
        var kwargs = {
            pipeline_code: group_name,
            process: node_name,
            node_type: node_type
        }
        spt.panel.load(info, class_name, kwargs);

        '''
        }
 

        return [behavior]


    def get_canvas_behaviors(self):


        behavior = {
        'type': 'click_up',
        'cbjs_action': '''
        spt.pipeline.init(bvr);
        var node = bvr.src_el;
        var top = bvr.src_el.getParent(".spt_pipeline_tool_top");

        var connector = spt.pipeline.hit_test_mouse(mouse_411);
        if (connector) {

            var top = bvr.src_el.getParent(".spt_pipeline_tool_top");
            var info = top.getElement(".spt_pipeline_tool_info");
            if (!info) {
                return;
            }

            to_attr = connector.get_attr("to_attr"),
            from_attr = connector.get_attr("from_attr")
            draw_attr = true;

            connector.draw_spline(draw_attr);

            var from_node = connector.get_from_node();
            var to_node = connector.get_to_node();

            var group_name = spt.pipeline.get_current_group();

            var class_name = 'tactic.ui.tools.ConnectorInfoWdg';
            var kwargs = {
                pipeline_code: group_name,
                from_node: from_node.spt_name,
                from_attr: from_attr,
                to_node: to_node.spt_name,
                to_attr: to_attr,
            }
            spt.panel.load(info, class_name, kwargs);
            return;
        }

        return;

/*
        var prop_top = spt.get_element(top, ".spt_pipeline_properties_top");
        var connect_top = spt.get_element(top, ".spt_connector_properties_top");

        var pipeline_prop = spt.get_element(prop_top, ".spt_pipeline_properties_content");
        var no_process = spt.get_element(prop_top, ".spt_pipeline_properties_no_process");
        var connector_prop = spt.get_element(connect_top, ".spt_connector_properties_content");

        var selected = spt.pipeline.get_selected();
        
        if (selected.length > 0) {

            if  (selected[0].type == 'connector') {
                var connector = selected[0];
                var context = connector.get_attr('context');
                var text = spt.get_element(connector_prop, ".spt_connector_context");
                if (context) {
                    text.value = context;
                }
                else {
                    text.value = '';
                }
                spt.hide(prop_top);
                spt.show(connector_prop);
            }
        }
        else {
                spt.hide(pipeline_prop);
                spt.show(no_process);
                spt.hide(connector_prop);
            }
 */    
        
        '''
        }

        return [behavior]




    def get_node_context_menu(self):

        menu = super(PipelineToolCanvasWdg, self).get_node_context_menu()


        project_code = Project.get_project_code()

        menu_item = MenuItem(type='title', label='Details')
        menu.add(menu_item)


        menu_item = MenuItem(type='action', label='Edit Process Data')
        #menu.add(menu_item)
        menu_item.add_behavior( {
            'cbjs_action': '''
            var node = spt.smenu.get_activator(bvr);
            var process = node.getAttribute("spt_element_name");
            var pipeline_code = node.spt_group;

            var server = TacticServerStub.get();
            var process_sk = server.eval("@GET(config/process['process','" + process + "']['pipeline_code','" + pipeline_code + "'].__search_key__)", {single :true});
            var class_name = 'tactic.ui.panel.EditWdg';
            
            if (process_sk) {
                var kwargs = {
                    search_key: process_sk,
                    view: 'edit',
                    show_header: false
                }
                spt.panel.load_popup("Edit Process " + process, class_name, kwargs);
            }
            else {
                 spt.info("Process entry does not exist. Try saving this workflow first.");
            }
            '''
        } )




        menu_item = MenuItem(type='action', label='Show Triggers/Notifications')
        menu.add(menu_item)
        menu_item.add_behavior( {
            'cbjs_action': '''
            var node = spt.smenu.get_activator(bvr);

            var top = node.getParent(".spt_pipeline_tool_top");
            spt.tab.top = top.getElement(".spt_tab_top");

            var process = node.getAttribute("spt_element_name");
            var pipeline_code = node.spt_group;
            var search_type = spt.pipeline.get_search_type(pipeline_code);

            var class_name = 'tactic.ui.tools.trigger_wdg.TriggerToolWdg';
            var kwargs = {
                search_type: search_type,
                pipeline_code: pipeline_code,
                process: process,
            }

            element_name = 'trigger_'+process;
            title = 'Triggers ['+process+']';
            //spt.tab.add_new(element_name, title, class_name, kwargs);
            spt.panel.load_popup(title, class_name, kwargs);

            '''
        } )

        menu_item = MenuItem(type='action', label='Show Naming')
        #menu.add(menu_item)
        menu_item.add_behavior( {
            'cbjs_action': '''
            var node = spt.smenu.get_activator(bvr);

            var top = node.getParent(".spt_pipeline_tool_top");
            spt.tab.top = top.getElement(".spt_tab_top");

            var process = node.getAttribute("spt_element_name");
            var pipeline_code = node.spt_group;

            var class_name = 'tactic.ui.tools.trigger_wdg.NamingToolWdg';
            var kwargs = {
                pipeline_code: pipeline_code,
                process: process
            }

            element_name = 'naming'+process;
            title = 'Naming ['+process+']';
            spt.tab.add_new(element_name, title, class_name, kwargs);

            '''
        } )


        menu_item = MenuItem(type='action', label='Show Processes Data')
        menu.add(menu_item)
        menu_item.add_behavior( {
        'cbjs_action': '''

        var node = spt.smenu.get_activator(bvr);
        var process = node.getAttribute("spt_element_name");
        var pipeline_code = node.spt_group;

        var expr = "@SOBJECT(config/process['@ORDER_BY','sort_order']['pipeline_code','"+pipeline_code+"'])"

        var class_name = 'tactic.ui.panel.ViewPanelWdg';
        var kwargs = {
            search_type: 'config/process',
            view: 'table',
            // NOTE: order by does not work here
            expression: expr
        }

        //var top = node.getParent(".spt_pipeline_tool_top");
        //spt.tab.top = top.getElement(".spt_tab_top");
        spt.tab.set_main_body_tab();
        spt.tab.add_new("processes", "Processes", class_name, kwargs);
        '''
        } )




        menu_item = MenuItem(type='action', label='Edit Task Status Workflow')
        menu.add(menu_item)
        menu_item.add_behavior( {
        'cbjs_action': '''

        // check if there is a custom task status pipeline defined
        var node = spt.smenu.get_activator(bvr);
        var top = node.getParent(".spt_pipeline_tool_top");
        spt.pipeline.init(node);
        var group_name = node.spt_group;
        var node_name = spt.pipeline.get_node_name(node);

        // check the search type of the pluein
        var search_type = spt.pipeline.get_search_type(group_name);
        if (search_type == 'sthpw/task') {
            spt.alert("This is already a task pipeline");
            return;
        }


        var search_type = "sthpw/pipeline";

        var server = TacticServerStub.get();
        var project_code = server.get_project();
        var code = project_code + '_' + node_name;

        // get the color
        var pipeline = server.eval("@SOBJECT(sthpw/pipeline['code','"+group_name+"'])");
        var color = pipeline.color;

        var data = {
            code: code,
            search_type: 'sthpw/task',
            project_code: project_code
        };
        var task_pipeline = server.get_unique_sobject(search_type, data);

        var ok = function(){
            spt.pipeline.clear_canvas();

            var xml = task_pipeline.pipeline;
            if (xml != '') {
                spt.pipeline.import_pipeline(code);
                return;
            }

            var xml = '';
            xml += '<pipeline>\\n';
            xml += '  <process name="Pending"/>\\n';
            xml += '  <process name="In Progress"/>\\n';
            xml += '  <process name="Complete"/>\\n';
            xml += '  <connect from="Pending" to="In Progress"/>\\n';
            xml += '  <connect from="In Progress" to="Complete"/>\\n';
            xml += '</pipeline>\\n';

            server.update(task_pipeline, {pipeline: xml, color: color} );

            spt.pipeline.import_pipeline(code);

            var list = top.getElement(".spt_pipeline_list");
            spt.panel.refresh(list);
 
        }


        spt.confirm("Confirm to create a custom task status workflow", ok)

        '''
        } )



        return menu



class PipelineInfoWdg(BaseRefreshWdg):
    def get_display(self):

        pipeline_code = self.kwargs.get("pipeline_code")

        top = self.top

        if not pipeline_code:
            return top

        pipeline = Search.get_by_code("sthpw/pipeline", pipeline_code)

        if not pipeline:
            return "Workflow not found"


        search_type = pipeline.get_value("search_type")

        top.add_style("padding: 20px 0px")
        top.add_color("background", "background")
        top.add_style("min-width: 300px")


        title_wdg = DivWdg()
        title_wdg.add_style("margin: -20px 0px 10px 0px")
        top.add(title_wdg)

        name = pipeline.get("name")
        if not name:
            name = pipeline.get("code")
        title_wdg.add(name)
        title_wdg.add_style("font-size: 16px")
        #title_wdg.add_style("font-weight: bold")
        #title_wdg.add_color("background", "background", -5)
        title_wdg.add_style("padding: 15px 10px")
        title_wdg.add("<hr/>")


        top.add( self.get_description_wdg(pipeline) )
        top.add( self.get_color_wdg(pipeline) )


        # sobject count
        if search_type:
            search = Search(search_type)
            search.add_filter("pipeline_code", pipeline.get_code())
            sobject_count = search.get_count()

            table = Table()
            top.add(table)
            table.add_style('width: auto')
            table.add_style('margin: 0px 5px')

            table.add_row()
            td = table.add_cell("Item Count:")
            td.add_style("text-align: right")
            td.add_style("padding: 10px 10px")
            td = table.add_cell("<span style='margin: 5px 10px' class='badge'>%s</span>" % sobject_count)
            td.add_style("width: 250px")
            td.add_style("text-align: right")

            button = ActionButtonWdg(title="View")
            td.add(button)
            button.add_style("float: right")
            if not sobject_count:
                button.add_style("display: none")

            button.add_behavior( {
                'type': 'click_up',
                'search_type': search_type,
                'pipeline_code': pipeline_code,
                'name': name,
                'cbjs_action': '''
                var class_name = 'tactic.ui.tools.TableLayoutWdg';
                var kwargs = {
                    search_type: bvr.search_type,
                    view: 'table',
                    op_filters: [['pipeline_code',bvr.pipeline_code]],
                    show_shelf: false,
                }
                spt.tab.set_main_body_tab();
                var title = "Items ["+bvr.name+"]";
                spt.tab.add_new(title, title, class_name, kwargs);
                //spt.panel.load_popup("Items ["+bvr.process+"]", class_name, kwargs);
                '''
            } )




        return top




    def get_description_wdg(self, pipeline):
        description = pipeline.get_value("description")
        desc_div = DivWdg()
        desc_div.add_style("margin: 10px 10px 20px 10px")
        desc_div.add("<div><b>Details:</b></div>")
        text = TextAreaWdg()
        desc_div.add(text)
        text.add_style("width: 100%")
        text.add_style("height: 100px")
        text.add_style("padding: 10px")
        text.add(description)
        text.add_behavior( {
            'type': 'blur',
            'search_key': pipeline.get_search_key(),
            'cbjs_action': '''
            var desc = bvr.src_el.value;
            var server = TacticServerStub.get();
            server.update(bvr.search_key, {description: desc} );
            '''
        } )

        return desc_div




    def get_color_wdg(self, pipeline):
        color = pipeline.get_value("color")
        div = DivWdg()
        div.add_style("margin: 5px 10px 20px 5px")
        div.add("<div><b>Color:</b></div>")
        from tactic.ui.input import ColorInputWdg
        text = ColorInputWdg()
        div.add(text)
        text.add_style("width: 100%")
        text.add_style("height: 100px")
        text.add_style("padding: 10px")
        text.set_value(color)
        text.add_behavior( {
            'type': 'blur',
            'search_key': pipeline.get_search_key(),
            'cbjs_action': '''
            var color = bvr.src_el.value;
            var server = TacticServerStub.get();
            server.update(bvr.search_key, {color: color} );

            var top = bvr.src_el.getParent(".spt_pipeline_tool_top");
            var wrapper = top.getElement(".spt_pipeline_wrapper");
            spt.pipeline.init_cbk(wrapper);

            var group_name = spt.pipeline.get_current_group();
            var group = spt.pipeline.get_group(group_name);
            group.set_color(color);
 
            '''
        } )

        return div






class ConnectorInfoWdg(BaseRefreshWdg):

    def get_display(self):
        
        top = self.top
        
        pipeline_code = self.kwargs.get("pipeline_code")
        pipeline = Pipeline.get_by_code(pipeline_code)
       
        # Custom connector info wdg
        pipeline_type = pipeline.get_value("type")
        if pipeline_type:
            search = Search("config/widget_config")
            search.add_filter("category", "workflow_connector")
            search.add_filter("view", pipeline_type)
            config = search.get_sobject()
            if config:
                handler = config.get_display_widget("info", self.kwargs)
                top.add(handler)
                return top
                
        top.add_class("spt_pipeline_connector_info")

        top.add_style("padding: 20px 0px")
        top.add_color("background", "background")
        top.add_style("min-width: 300px")
        
        title_wdg = DivWdg()
        top.add(title_wdg)
        title_wdg.add_style("margin: -20px 0px 10px 0px")
        title_wdg.add("Connector")
        title_wdg.add_style("font-size: 1.2em")
        title_wdg.add_style("font-weight: bold")
        title_wdg.add_color("background", "background", -5)
        title_wdg.add_style("padding: 15px 10px")

        top.add("<br/>")
        

        from_node = self.kwargs.get("from_node")
        to_node = self.kwargs.get("to_node")
        left_process = pipeline.get_process(from_node)
        right_process = pipeline.get_process(to_node)
        
        # If either the left process or right process do not exist,
        # display empty pane.
        if not left_process or not right_process:
            info_wdg = DivWdg()
            info_wdg.add_style("margin: 10px")
            info_wdg.add("Save your workflow to edit connector properties.") 
            top.add(info_wdg)
            return top

        info_wdg = DivWdg()
        top.add(info_wdg)
        info_wdg.add("From <b>%s</b> to <b>%s</b>" % (from_node, to_node))
        info_wdg.add_style("margin: 10px")


        table = Table()
        top.add(table)
        table.add_style("width: 100%")
        table.add_style("margin: 0px -3px 5px 0px")

        tr = table.add_row()
        tr.add_style("background: #EEE")
        td = table.add_header(from_node)
        td.add_style("padding: 10px")
        td.add_style("vertical-align: top")
        td.add_style("text-align: center")

        td = table.add_cell(">>")
        td.add_style("text-align: center")

        td = table.add_header(to_node)
        td.add_style("padding: 10px")
        td.add_style("vertical-align: top")
        td.add_style("text-align: center")


        tr, td = table.add_row_cell()
        td.add("<br/>Using Attributes:")
        td.add_style("padding: 5px")


        left_selected = self.kwargs.get("from_attr")
        if not left_selected:
            left_selected = "output"
        right_selected = self.kwargs.get("to_attr")
        if not right_selected:
            right_selected = "input"

 
        table.add_row()

        # handle output
        left = table.add_cell()
        left.add_style("vertical-align: top")
        left.add_style("width: 150px")
        left.add_class("spt_connect_column_top")
        left.add_class("spt_dts")
        left.add_style("padding: px")
        #left.add_color("background", "background3")


        td = table.add_cell(">>")
        td.add_style("text-align: center")

        text = TextInputWdg(name="left")
        text.add_style("width: 150px")
        left.add(text)
        text.add_class("spt_output_attr")
        if left_selected:
            text.set_value(left_selected)

        left.add("<br/>"*3)
        left.add("Standard Attributes")
        left.add("<hr/>")



        node_type = left_process.get_type()
        if node_type in ["condition", "approval"]:
            out_attrs = ['success','fail']
        else:
            out_attrs = ['output']

        left_div = DivWdg()
        left.add(left_div)

        for attr in out_attrs:
            attr_div = DivWdg()
            left_div.add(attr_div)
            attr_div.add(attr)
            attr_div.add_style("padding: 3px")
            attr_div.add_class("spt_attr")
            attr_div.add_behavior( {
                'type': 'click_up',
                'cbjs_action': '''
                var top = bvr.src_el.getParent(".spt_pipeline_connector_info");
                var left = top.getElement(".spt_output_attr");
                left.value = bvr.src_el.innerHTML;
                '''
            } )

            attr_div.add_behavior( {
                'type': 'mouseenter',
                'cbjs_action': '''
                bvr.src_el.setStyle("background", "#EEE");
                '''
            } )


            attr_div.add_behavior( {
                'type': 'mouseleave',
                'cbjs_action': '''
                bvr.src_el.setStyle("background", "");
                '''
            } )



 

        # handle input

        right = table.add_cell()
        right.add_style("vertical-align: top")
        right.add_style("width: 150px")
        right.add_class("spt_connect_column_top")
        right.add_class("spt_dts")
        right.add_style("padding: 5px")
        #right.add_color("background", "background3")

        text = TextInputWdg(name="right")
        text.add_style("width: 150px")
        right.add(text)
        text.add_class("spt_input_attr")
        if right_selected:
            text.set_value(right_selected)

        right.add("<br/>"*3)
        right.add("<hr/>")



        node_type = right_process.get_type()
        if node_type in ["condition", "approval"]:
            in_attrs = ['input']
        else:
            in_attrs = ['input']

        right_div = DivWdg()
        right.add(right_div)
        for attr in in_attrs:
            attr_div = DivWdg()
            right_div.add(attr_div)
            attr_div.add(attr)
            attr_div.add_style("padding: 3px")




        save = ActionButtonWdg(title="Save")
        save.add_style("float: right")
        top.add(save)
        save.add_behavior( {
            'type': 'click_up',
            'kwargs': self.kwargs,
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_pipeline_info_top");
            var info_top = bvr.src_el.getParent(".spt_pipeline_connector_info");
            var input = spt.api.get_input_values(info_top, null, false);

            // find the current connector
            var pipeline_code = spt.pipeline.get_current_group();
            var group = spt.pipeline.get_group(pipeline_code);
            var connectors = group.get_connectors();
            var connector = null;
            for (var i = 0; i < connectors.length; i++) {

                from_node = connectors[i].get_from_node();
                to_node = connectors[i].get_to_node();


                if (   (from_node.spt_name == bvr.kwargs.from_node) &&
                       (to_node.spt_name == bvr.kwargs.to_node )     ) {

                    connector = connectors[i];
                    break;
               }
            }

            if (!connector) return;

            connector.set_attr("from_attr", input.left);
            connector.set_attr("to_attr", input.right);

            // export group??


            '''
        } )



        return top







class ProcessInfoWdg(BaseRefreshWdg):

    def get_display(self):

        node_type = self.kwargs.get("node_type")

        top = self.top
        top.add_class(".spt_process_info_top")
        self.set_as_panel(top)

        pipeline_code = self.kwargs.get("pipeline_code")
        pipeline = Pipeline.get_by_code(pipeline_code)
        if not pipeline:
            return "N/A"


        search_type = pipeline.get("search_type")


        
        widget = None

        if search_type == "sthpw/task":
            widget = TaskStatusInfoWdg(**self.kwargs)

        elif node_type in ['manual', 'node']:
            widget = DefaultInfoWdg(**self.kwargs)

        elif node_type == 'approval':
            widget = ApprovalInfoWdg(**self.kwargs)

        elif node_type == 'action':
            widget = ActionInfoWdg(**self.kwargs)

        elif node_type == 'condition':
            widget = ConditionInfoWdg(**self.kwargs)

        elif node_type == 'hierarchy':
            widget = HierarchyInfoWdg(**self.kwargs)

        elif node_type == 'dependency':
            widget = DependencyInfoWdg(**self.kwargs)

        elif node_type == 'progress':
            widget = ProgressInfoWdg(**self.kwargs)

        elif node_type == 'unknown':
            widget = UnknownInfoWdg(**self.kwargs)

        elif node_type == 'progress':
            widget = ProgressInfoWdg(**self.kwargs)

        else:
            from pyasm.command import CustomProcessConfig
            widget = CustomProcessConfig.get_info_handler(node_type, self.kwargs)
            #from spt.tools.youtube import YouTubeProcessInfoWdg
            #widget = YouTubeProcessInfoWdg(**self.kwargs)




        if not widget:
            widget = DefaultInfoWdg(**self.kwargs)

        top.add(widget)

        return top




class BaseInfoWdg(BaseRefreshWdg):

    def get_description_wdg(self, process_sobj):
        if not process_sobj:
            description = "N/A"
        else:
            description = process_sobj.get_value("description")

        desc_div = DivWdg()
        desc_div.add_style("margin: 20px 10px")
        desc_div.add("<div><b>Details:</b></div>")
        text = TextAreaWdg()
        desc_div.add(text)
        text.add_style("width: 100%")
        text.add_style("height: 60px")
        text.add_style("padding: 10px")
        text.add(description)

        if process_sobj:
            text.add_behavior( {
                'type': 'blur',
                'search_key': process_sobj.get_search_key(),
                'cbjs_action': '''
                var desc = bvr.src_el.value;
                var server = TacticServerStub.get();
                server.update(bvr.search_key, {description: desc} );
                '''
            } )

        return desc_div





    def get_input_output_wdg(self, pipeline, process):
            
        div = DivWdg()
        div.add_style("margin: 10px")

        input_processes = pipeline.get_input_processes(process)
        output_processes = pipeline.get_output_processes(process)

        input_list = ", ".join([x.get_name() for x in input_processes]) or "<i>None</i>"
        output_list = ", ".join([x.get_name() for x in output_processes]) or "<i>None</i>"

        input_div = DivWdg()
        div.add(input_div)
        input_div.add("Inputs: %s" % input_list)

        output_div = DivWdg()
        div.add(output_div)
        output_div.add("Outputs: %s" % output_list)

        return div




    def get_title_wdg(self, process, node_type, show_node_type_select=True):

        div = DivWdg()
        div.add_style("margin-top: -15px")

        table = Table()
        table.add_style("width: 100%")
        div.add(table)
        table.add_row()

        """
        from tactic.ui.panel import ThumbWdg2
        icon_cell = table.add_cell()
        thumb = ThumbWdg2()
        icon_cell.add(thumb)
        search = Search("config/process")
        search.add_filter("process", process)
        process_sobj = search.get_sobject()
        thumb.set_sobject(process_sobj)
        thumb.add_style("width: 45px")
        thumb.add_style("height: 45px")
        thumb.add_style("border-radius: 30px")
        thumb.add_style("border: solid 1px #DDD")
        thumb.add_style("overflow: hidden")
        """




        left = table.add_cell()
        left.add_style("vertical-align: top")
        left.add_style("padding-left: 10px")

        left.add("<b>Name: </b>")

        title_wdg = DivWdg()
        left.add(title_wdg)

        title_wdg.add_style("margin: 0px 0px 0px 0px")
        title_wdg.add_class("spt_title_top")
        title_wdg.add_style("font-size: 16px")
        title_wdg.add_style("padding: 0px 10px 0px 0px")


        title_edit_text = TextInputWdg(name="process", height="30px")
        title_wdg.add(title_edit_text)
        title_edit_text.add_class("spt_title_edit")
        title_edit_text.add_style("width: auto")
        #title_edit_text.add_style("border: none")

        title_edit_text.set_value(process)


        title_edit_text.add_behavior( {
            'type': 'focus',
            'cbjs_action': '''
            bvr.src_el.select();
            '''
        } )

        title_edit_text.add_behavior( {
            'type': 'keyup',
            'cbjs_action': '''
            if (evt.key == 'enter') {
                bvr.src_el.blur();
            }
            '''
        } )




        title_edit_text.add_behavior( {
            'type': 'blur',
            'cbjs_action': '''
            var node = spt.pipeline.get_selected_node();
            spt.pipeline.rename_node(node, bvr.src_el.value);

            '''
        } )



        if not show_node_type_select:
            select = HiddenWdg("node_type")
            title_wdg.add(select)
            if node_type == "node":
                select.set_value("manual")
            else:
                select.set_value(node_type)
    

        else:

            right = table.add_cell()
            right.add_style("vertical-align: top")

            right.add("<b>Type: </b>")

            select = SelectWdg("node_type")
            right.add(select)

            node_types = [
                'manual',
                'action',
                'condition',
                'approval',
                'hierarchy',
                'dependency',
                'progress',
            ]


            search = Search("config/widget_config")
            search.add_filter("category", "workflow")
            configs = search.get_sobjects()
            if configs:
                node_types.append('---')

            for config in configs:
                node_types.append(config.get_value("view"))

            labels = [Common.get_display_title(x) for x in node_types]

            select.set_option("values", node_types)
            select.set_option("labels", labels)


            select.add_style("width: 100px")
            if node_type == "node":
                select.set_value("manual")
            else:
                select.set_value(node_type)

            select.add_behavior( {
                'type': 'change',
                'process': process,
                'cbjs_action': '''

                var server = TacticServerStub.get();

                var node_type = bvr.src_el.value;
                var process = bvr.process;

                // change node_type
                var node = spt.pipeline.get_node_by_name(process);
                var parent = node.getParent();

                node.setStyle("box-shadow", "0px 0px 15px rgba(255,0,0,0.5)"); 

                var pos = spt.pipeline.get_position(node);

                //parent.removeChild(node);

                var group = spt.pipeline.get_group_by_node(node);
                for (var i = 0; i < group.nodes.length; i++) {
                    if (node == group.nodes[i]) {
                        group.nodes.splice(i, 1);
                        break;
                    }
                }



                var new_node = spt.pipeline.add_node(process, null, null, {node_type: node_type});
                new_node.position(pos)


                var canvas = spt.pipeline.get_canvas();
                var connectors = canvas.connectors;
                for (var i = 0; i < connectors.length; i++) {
                    var connector = connectors[i];
                    if (connector.from_node == node) {
                        connector.from_node = new_node;
                    }
                    if (connector.to_node == node) {
                        connector.to_node = new_node;
                    }
                }


                // destroy the old node
                spt.behavior.destroy_element(node);

                spt.pipeline.redraw_canvas();

                // click on the new node
                new_node.click();

                spt.named_events.fire_event('pipeline|change', {});

                '''
            } )
            select.add_style("position: relative")
            select.add_style("z-index: 10")

        div.add("<br clear='all'/>")
        div.add("<hr/>")

        return div






class DefaultInfoWdg(BaseInfoWdg):



    def get_display(self):
        process = self.kwargs.get("process")
        pipeline_code = self.kwargs.get("pipeline_code")
        node_type = self.kwargs.get("node_type")

        top = self.top

        if not pipeline_code:
            return top

        pipeline = Search.get_by_code("sthpw/pipeline", pipeline_code)

        if not process:
            return top


        top.add_class("spt_pipeline_info_top")

        search_type = pipeline.get_value("search_type")

        top.add_style("padding: 20px 0px")
        top.add_color("background", "background")
        top.add_style("min-width: 300px")



        title_wdg = self.get_title_wdg(process, node_type)
        top.add( title_wdg )


        search = Search("config/process")
        search.add_filter("process", process)
        search.add_filter("pipeline_code", pipeline_code)

        process_sobj = search.get_sobject()
        if not process_sobj:
            msg = DivWdg()
            top.add(msg)
            msg.add("No process found.  Please save")
            msg.add_style("margin: 30px auto")
            msg.add_style("text-align: center")
            msg.add_style("width: 80%")
            msg.add_style("padding: 20px")
            return top


        info_div = DivWdg()
        top.add(info_div)
        info_div.add("A manual process is a process where work is done by a person.  The status of the process is determined by tasks added to this process which must be manually set to complete when finished")
        info_div.add_style("margin: 10px 10px 20px 10px")


        desc_div = self.get_description_wdg(process_sobj)
        top.add(desc_div)



        #show error message if the node has not been registered 
        if not process_sobj:
            warning_div = DivWdg()
            #width = 16 makes the icon smaller
            warning_icon = IconWdg("Warning",IconWdg.WARNING, width=16)
            warning_msg = "This process node has not been registered in the process table, please save your changes."
           
            warning_div.add(warning_icon)
            warning_div.add(warning_msg)
            top.add(warning_div)
            warning_div.add_style("padding: 20px 30px")
            warning_div.add_style("font-size: 15px")

            return top



        has_tasks = True
        if has_tasks:
            div = DivWdg()
            top.add(div)
            div.add_style("padding: 10px")
            div.add("<b>Task Setup</b><br/>")
            div.add("Task options allow you to control various default properties of tasks.")

            process_key = process_sobj.get_search_key()

            div.add("<br/>"*2)

            button = ActionButtonWdg(title="Task Setup", size="block")
            div.add(button)
            button.add_class("btn-clock")
            button.add_behavior( {
                'type': 'click_up',
                'pipeline_code': pipeline_code,
                'process': process,
                'search_key': process_sobj.get_search_key(),
                'cbjs_action': '''
                var class_name = "tactic.ui.tools.PipelinePropertyWdg";
                var kwargs = {
                    pipeline_code: bvr.pipeline_code,
                    process: bvr.process
                }
                var popup = spt.panel.load_popup("Task Setup", class_name, kwargs);
                var nodes = spt.pipeline.get_selected_nodes();
                var node = nodes[0];
                spt.pipeline_properties.show_properties2(popup, node);
                '''
            } )




        from pyasm.biz import ProjectSetting
        setting = ProjectSetting.get_value_by_key("feature/process/task_detail")
        if setting in ["true"]:

            from spt.modules.workflow import TaskButtonDetailSettingWdg, TaskDetailSettingWdg
            #detail_wdg = TaskDetailSettingWdg(
            detail_wdg = TaskButtonDetailSettingWdg(
                    **self.kwargs
            )

            #detail_wdg = self.get_detail_wdg()
            top.add(detail_wdg)
            detail_wdg.add_style("margin: 10px")




        process_code = process_sobj.get_value("code")

        # triggers
        search = Search("config/trigger")
        search.add_filters("process", [process,process_code])
        trigger_count = search.get_count()


        # notifications
        search = Search("sthpw/notification")
        search.add_project_filter()
        search.add_filters("process", [process,process_code])
        notification_count = search.get_count()


        # naming count
        search = Search("config/naming")
        search.add_filter("context", "%s/%%" % process, op='like')
        naming_count = search.get_count()


        # sobject count
        if search_type:
            search = Search(search_type)
            search.add_filter("pipeline_code", pipeline.get_code())
            sobject_count = search.get_count()
        else:
            sobject_count = 0


        top.add("<br/><hr/>")


        depend_title_div = DivWdg()
        depend_div = DivWdg()
        top.add(depend_title_div)
        top.add(depend_div)

        swap = SwapDisplayWdg()
        depend_title_div.add(swap)
        SwapDisplayWdg.create_swap_title(depend_title_div, swap, depend_div, is_open=False)

        depend_title_div.add("<b>Process Dependencies</b><br/>")
        depend_title_div.add("&nbsp;&nbsp;&nbsp;A list of items related to this process.")
        depend_title_div.add_style("margin: 20px 10px 10px 10px")

        table = Table()
        depend_div.add(table)
        table.add_style('width: auto')
        table.add_style('margin: 0px 5px')

        table.add_row()
        td = table.add_cell("Triggers:")
        td.add_style("text-align: right")
        td.add_style("padding: 10px 10px")
        td = table.add_cell("<span style='margin: 5px 10px' class='badge'>%s</span>" %trigger_count)
        td.add_style("width: 250px")
        td.add_style("text-align: right")

        button = ActionButtonWdg(title="View")
        td.add(button)
        button.add_style("float: right")
        button.add_behavior( {
            'type': 'click_up',
            'pipeline_code': pipeline_code,
            'process': process,
            'cbjs_action': '''
            var class_name = 'tactic.ui.tools.TriggerToolWdg';
            var kwargs = {
                pipeline_code: bvr.pipeline_code,
                process: bvr.process,
            }
            spt.panel.load_popup("Triggers ["+bvr.process+"]", class_name, kwargs);
            '''
        } )

        table.add_row()
        td = table.add_cell("Notifications:")
        td.add_style("text-align: right")
        td.add_style("padding: 10px 10px")
        td = table.add_cell("<span style='margin: 5px 10px' class='badge'>%s</span>" % notification_count)
        td.add_style("text-align: right")

        button = ActionButtonWdg(title="View")
        td.add(button)
        button.add_style("float: right")
        button.add_behavior( {
            'type': 'click_up',
            'pipeline_code': pipeline_code,
            'process': process,
            'cbjs_action': '''
            var class_name = 'tactic.ui.tools.TriggerToolWdg';
            var kwargs = {
                pipeline_code: bvr.pipeline_code,
                process: bvr.process,
            }
            spt.panel.load_popup("Triggers ["+bvr.process+"]", class_name, kwargs);
            '''
        } )




        table.add_row()
        td = table.add_cell("Naming Conventions: ")
        td.add_style("text-align: right")
        td.add_style("padding: 10px 10px")
        td = table.add_cell("<span style='margin: 5px 10px' class='badge'>%s</span>" % naming_count)
        td.add_style("text-align: right")


        button = ActionButtonWdg(title="View")
        td.add(button)
        button.add_style("float: right")
        button.add_behavior( {
            'type': 'click_up',
            'pipeline_code': pipeline_code,
            'process': process,
            'cbjs_action': '''
            var class_name = 'tactic.ui.tools.TableLayoutWdg';
            var kwargs = {
                search_type: "config/naming",
                //expression: "@SOBJECT(config/naming['context','like','"+bvr.process+"'])",
                show_shelf: true,
            }
            spt.panel.load_popup("Naming Conventions ["+bvr.process+"]", class_name, kwargs);
            '''
        } )




        if search_type:
            table.add_row()
            td = table.add_cell("Item Count: ")
            td.add_style("text-align: right")
            td.add_style("padding: 10px 10px")
            td = table.add_cell("<span style='margin: 5px 10px' class='badge'>%s</span>" % sobject_count)
            td.add_style("text-align: right")


            button = ActionButtonWdg(title="View")
            td.add(button)
            button.add_style("float: right")
            button.add_behavior( {
                'type': 'click_up',
                'search_type': search_type,
                'pipeline_code': pipeline_code,
                'process': process,
                'cbjs_action': '''
                var class_name = 'tactic.ui.tools.TableLayoutWdg';
                var kwargs = {
                    search_type: bvr.search_type,
                    op_filters: [['pipeline_code',bvr.pipeline_code]],
                }
                spt.tab.set_main_body_tab();
                var title = "Items ["+bvr.process+"]";
                spt.tab.add_new(title, title, class_name, kwargs);
                //spt.panel.load_popup("Items ["+bvr.process+"]", class_name, kwargs);
                '''
            } )



        # DEPRECATED: The old check-in widget is basically not functional anymore
        has_checkins = False
        if has_checkins:
            div = DivWdg()
            top.add(div)
            div.add_style("padding: 10px")
            div.add("<br/><hr/><br/>")
            div.add("<b>Check-in setup</b><br/>")
            div.add("Advanded check-in options allow you to control exactly what kinds of checkins can occur in this process")

            div.add("<br/>"*2)

            button = ActionButtonWdg(title="Check-in Setup", size="block")
            div.add(button)
            button.add_class("btn-clock")
            button.add_behavior( {
                'type': 'click_up',
                'process': process,
                'search_key': process_sobj.get_search_key(),
                'cbjs_action': '''
                var class_name = 'tactic.ui.panel.EditWdg';
                var kwargs = {
                    search_type: "config/process",
                    show_header: false,
                    width: "400px",
                    search_key: bvr.search_key,
                    view: "checkin_setup_edit",
                }
                spt.panel.load_popup("Check-in Setup for ["+bvr.process+"]", class_name, kwargs);

                '''
            } )




        return top


# DEPRECATED
class ScriptEditWdg(BaseRefreshWdg):
    ''' Text area for Existing Script Edit '''
    def get_display(self):

        script = self.kwargs.get('script')
        script_path = self.kwargs.get('script_path')
        on_action_class = self.kwargs.get('on_action_class')
        is_admin = self.kwargs.get('is_admin') in ['true', True]

        action = self.kwargs.get("action") or "script_path"
        language = self.kwargs.get("language")

       
        div = self.top
        self.set_as_panel(div)
        div.add_class("spt_script_edit")




        # Python command class
        if action == "command":
            cmd_div = DivWdg()
            div.add(cmd_div)
            cmd_title = DivWdg("Python Command Class (eg: tactic.command.MyCommand)")
            cmd_title.add_style('margin-bottom: 3px')
            cmd_div.add_style('margin-bottom: 20px')
            cmd_div.add(cmd_title)
     
            cmd_text = TextInputWdg(name="on_action_class")
            cmd_text.add_style("width: 100%")
            if on_action_class:
                cmd_text.set_value(on_action_class)

            cmd_div.add(cmd_text)


            return div





        script_path_folder = ''
        script_path_title = ''

        if script_path:
            script_path_folder, script_path_title = os.path.split(script_path)

        script_obj = None

        if script_path:
            script_obj = Search.eval("@SOBJECT(config/custom_script['folder','%s']['title','%s'])"%(script_path_folder, script_path_title), single=True)

        script_path_div = DivWdg()
        script_path_div.add_style("width: 100%")
        script_path_div.add_style("height: 60px")
        div.add(script_path_div)
        run_title = DivWdg("Script Path (Folder / Title):")
        run_title.add_style('margin-bottom: 3px')
        script_path_div.add(run_title)
        #script_path_div.add()
        filters = ""

        if action != "script_path":
            script_path_div.add_style("display: none")


        
        if not is_admin:
            filters = '[["language","server_js"]]'
        script_path_folder_text = LookAheadTextInputWdg(name="script_path_folder", search_type="config/custom_script", column="folder", filters=filters)
        script_path_folder_text.add_class("spt_script_path_folder")
        script_path_div.add(script_path_folder_text)
   
        script_path_folder_text.add_behavior( {
            'type': 'blur',
            'cbjs_action': '''
             setTimeout( function() {

                var script_path_folder = bvr.src_el.value;
                var code;
                if (script_path_folder) {
                    var server = TacticServerStub.get();
                    code = server.eval("@GET(config/custom_script['folder', '" + script_path_folder + "'].code)", {single: true});
                }

                var top = bvr.src_el.getParent(".spt_script_edit");
                var script_path_title = top.getElement(".spt_script_path_title");
                var is_read_only = script_path_title.getAttribute('readonly');
                
                //var bkgd = script_path_title.getStyle('background');
                
                if (code) {
                    if (is_read_only) {
                        buttons_div = top.getElement(".spt_script_edit_buttons");
                        if (buttons_div.getAttribute('edit') != 'true' )
                            script_path_title.removeAttribute('readonly');
                    }
                } else {
                    script_path_title.setAttribute('readonly','readonly');
                }
             }, 250);
            '''
        } )
        slash = DivWdg('/')
        slash.add_styles('font-size: 1.7em; margin: 4px 5px 0 3px; float: left')
        script_path_div.add(slash)
        script_path_folder_text.add_styles("width: 120px; float: left")
        if script_obj:
            script_path_folder_text.set_value(script_path_folder)
        
        script_path_title_text = LookAheadTextInputWdg(name="script_path_title", search_type="config/custom_script", column="title", filters=filters, width='240')
        script_path_title_text.add_class("spt_script_path_title")

        script_path_div.add(script_path_title_text)

        script_path_title_text.add_style("float: left")
        if script_obj:
            script_path_title_text.set_value(script_path_title)
        script_path_title_text.add_behavior( {
            'type': 'blur',
            'cbjs_action': '''
             setTimeout( function() {

                var script_path_title = bvr.src_el.value;
                var top = bvr.src_el.getParent(".spt_script_edit");
                var buttons_div = top.getElement(".spt_script_edit_buttons");

                spt.show(buttons_div);

                var script_path_folder = top.getElement(".spt_script_path_folder").value;
                var script_path = script_path_folder + '/' + script_path_title;
                var el = top.getElement(".spt_python_script_text");
                var script = '';
                if (script_path_folder && script_path_title) {
                    var popup = false;
                    script = spt.CustomProject.get_script_by_path(script_path, popup);
                }
                if (script_path_folder && script_path_title) { 
                    if (script) {
                        el.value = script;
                        spt.show(el);
                    }
                    else {
                        el.value = '';
                    }
                }


                
            
             }, 250);
            '''
        } )








        can_edit = True
        if script_obj:
            script = script_obj.get_value('script')
            language = script_obj.get_value('language')
            if not is_admin and language == 'python':
                can_edit = False


        div.add("Language:")
        select = SelectWdg("language")
        div.add(select)
        select.set_option("labels", "Python|Server Javascript")
        select.set_option("values", "python|server_js")
        select.set_value(language)
        div.add("<br/>")









        # in case the script obj is deleted, it will just let you create new
        if script_path and script_obj:
            edit_mode = True
            edit_label = "Click to enable Edit"
            show_script = True

            create_edit_button = DivWdg()
            create_edit_button.add(edit_label)
            create_edit_button.add_class("hand")
            create_edit_button.add_style("text-decoration: underline")
            create_edit_button.add_style("margin-bottom: -20px")


            #create_edit_button = ActionButtonWdg(title=edit_label, tip="%s script"%edit_label, width="300")

        else:
            if on_action_class:
                show_script = False
            else:
                show_script = True

            edit_mode = False
            edit_label = "Or Create a New Script"
            script_path_title_text.set_readonly(True)

            create_edit_button = DivWdg()
            create_edit_button.add(edit_label)
            create_edit_button.add_class("hand")
            create_edit_button.add_style("text-decoration: underline")
            
            #create_edit_button = ActionButtonWdg(title=edit_label, tip="%s script"%edit_label, width="300", color="warning")
            #create_edit_button.add_style("margin: 20px auto")



        buttons_div = DivWdg(css='spt_script_edit_buttons')
        div.add(buttons_div)
        
        if (can_edit and edit_mode == True) or edit_mode == False: 
            buttons_div.add(create_edit_button)

        create_edit_button.add_behavior( {
            'type': 'click_up',
            'edit_mode': edit_mode,
            'can_edit': can_edit,

            'cbjs_action': '''
            var trigger_top = bvr.src_el.getParent(".spt_script_edit");
            var script_editor = trigger_top.getElement(".spt_python_script_text");
            var buttons_div = trigger_top.getElement(".spt_script_edit_buttons");

            if (!bvr.can_edit) {
                spt.info("You don't have the administrative right to edit this script.");
                return;
            }
            var title_input = trigger_top.getElement(".spt_script_path_title");
            var folder_input = trigger_top.getElement(".spt_script_path_folder");

            if (!bvr.edit_mode) {
                title_input.value = '';
                folder_input.value = '';
                script_editor.value = '';
            }

            // Displayor Hide the script editor
            if (bvr.edit_mode) {
                buttons_div.setAttribute('edit','true');

                script_editor.setStyle("display", "");
                // In edit mode, need to remove read only attribute and grey backround
                script_editor.removeProperty("readonly")
                script_editor.setStyle("background", "#FFFFFF");

                // made script path text field readonly
                folder_input.setAttribute('readonly','readonly');
                title_input.setAttribute('readonly','readonly');
            } else {
                script_editor.setStyle("display", "none");
                buttons_div.setStyle("display", "none");
                spt.tab.set_tab_top_from_child(bvr.src_el);
                spt.tab.add_new('create_new_script' , 'Create New', 'tactic.ui.tools.ScriptCreateWdg');
            }

            

            '''
        } )

        # expected script path should not match the existing script_path.
        # if they do, there is no point to show Create New
        expected_script_path = self.kwargs.get('expected_script_path')
        
        if script_path and script_path != expected_script_path and show_script:
            create_new_button = ActionButtonWdg(title="Create New", tip="Create New Script", width=200)
            create_new_button.add_style("margin: 10px auto")
            buttons_div.add(create_new_button)

            create_new_button.add_behavior( {
                'type': 'click_up',
                'edit_mode': False,

                'cbjs_action': '''
                trigger_top = bvr.src_el.getParent(".spt_script_edit");
                script_editor = trigger_top.getElement(".spt_python_script_text");
                buttons_div = trigger_top.getElement(".spt_script_edit_buttons");
                
                if (!bvr.edit_mode) {
                    var title_input = trigger_top.getElement(".spt_script_path_title");
                    var folder_input = trigger_top.getElement(".spt_script_path_folder");
                    title_input.value = '';
                    folder_input.value = '';
                    script_editor.value = '';
                }

                // Hide the script editor and button controls
                script_editor.setStyle("display", "none");
                buttons_div.setStyle("display", "none");

                spt.tab.set_tab_top_from_child(bvr.src_el);
                spt.tab.add_new('create_new_script' , 'Create New', 'tactic.ui.tools.ScriptCreateWdg');
                '''
            } )
      
        div.add(HtmlElement.br(2))


        script_text = TextAreaWdg("script")
        script_text.add_style('padding-top: 10px')
        if edit_mode:
            script_text.set_option("read_only", "true")
        else:    
            script_text.add_style("display", "none") 
        script_text.add_class("form-control")
        script_text.add_class("spt_python_script_text")
        div.add(script_text)
                
        if script:
            script_text.set_value(script)
        script_text.add_style("height: 300px")
        script_text.add_style("width: 100%")

        return div

# DEPRECATED
"""
class ScriptCreateWdg(BaseRefreshWdg):
    ''' Blank Text area for New Script Creation '''
    def get_display(self):

        script_path = ''
        div = DivWdg()
        div.add(HtmlElement.br())
        title = DivWdg('Add Script Code to be executed:')
        title.add_style('padding: 2px')

        div.add(title)
        div.add_style('padding: 5px')

       

        script_text = TextAreaWdg("script_new")
        script_text.add_style('padding-top: 10px')
      
        script_text.add_class("form-control")
        script_text.add_class("spt_python_script_text")
        div.add(script_text)
       
        script_text.add_style("height: 300px")
        script_text.add_style("width: 100%")

        return div
"""


class ScriptSettingsWdg(BaseRefreshWdg):

    def get_display(self):

        action = self.kwargs.get("action") or "create_new"

        is_admin = Environment.get_security().is_admin()

        div = self.top
        self.set_as_panel(div)
        div.add_class("spt_script_edit")

        if not action:
            return div



        if action == "command":
            on_action_class = self.kwargs.get("on_action_class")
            script_wdg = self.get_command_script_wdg(on_action_class)

        elif action == "create_new":
            script_wdg = self.get_new_script_wdg(is_admin)
        else:
            script_path = self.kwargs.get("script_path")
            script = self.kwargs.get("script")
            language = self.kwargs.get("language")

            script_wdg = self.get_existing_script_wdg(script_path, script, language, is_admin)

        div.add(script_wdg)



        div.add("<br/>")


        # Execute mode

        cmd_title = DivWdg("Execute Mode")
        cmd_title.add_style('margin-bottom: 3px')
        div.add(cmd_title)

        execute_mode = self.kwargs.get("execute_mode")

        cmd_text = SelectWdg(name="execute_mode")
        cmd_text.set_option("labels", "In Process|Blocking Separate Process|Non-Blocking Separate Process|Queued")
        cmd_text.set_option("values", "same process,same transaction|separate process,blocking|separate process,non-blocking|separate process,queued")
        cmd_text.add_style("width: 100%")
        if execute_mode:
            cmd_text.set_value(execute_mode)
        div.add(cmd_text)




        return div



    def get_command_script_wdg(self, on_action_class):
        cmd_div = DivWdg()
        cmd_div.add_style('margin-bottom: 20px')
        cmd_div.add_style('margin-top: 20px')

        cmd_title = DivWdg("Python Command Class (eg: tactic.command.MyCommand)")
        cmd_title.add_style('margin-bottom: 3px')
        cmd_div.add(cmd_title)
 
        cmd_text = TextInputWdg(name="on_action_class")
        cmd_text.add_style("width: 100%")
        if on_action_class:
            cmd_text.set_value(on_action_class)

        cmd_div.add(cmd_text)
        return cmd_div



    def get_existing_script_wdg(self, script_path, script, language, is_admin):

        div = DivWdg()

        script_path_folder = ''
        script_path_title = ''

        if script_path:
            script_path_folder, script_path_title = os.path.split(script_path)

        script_obj = None

        if script_path:
            script_obj = Search.eval("@SOBJECT(config/custom_script['folder','%s']['title','%s'])"%(script_path_folder, script_path_title), single=True)

        script_path_div = DivWdg()
        div.add(script_path_div)
        script_path_div.add_style("width: 100%")
        script_path_div.add_style("min-width: 400px")
        script_path_div.add_style("margin-top: 20px")
        script_path_div.add_style("margin-bottom: 20px")


        if not is_admin:
            script_path_div.add_style("display: none")


        run_title = DivWdg("Script Path (Folder / Title):")
        run_title.add_style('margin-bottom: 3px')
        script_path_div.add(run_title)
        #script_path_div.add()
        filters = ""

        
        if not is_admin:
            filters = '[["language","server_js"]]'
        script_path_folder_text = LookAheadTextInputWdg(name="script_path_folder", search_type="config/custom_script", column="folder", filters=filters)
        script_path_folder_text.add_class("spt_script_path_folder")
        script_path_div.add(script_path_folder_text)
   
        script_path_folder_text.add_behavior( {
            'type': 'blur',
            'cbjs_action': '''
             setTimeout( function() {

                var script_path_folder = bvr.src_el.value;
                var code;
                if (script_path_folder) {
                    var server = TacticServerStub.get();
                    code = server.eval("@GET(config/custom_script['folder', '" + script_path_folder + "'].code)", {single: true});
                }

                var top = bvr.src_el.getParent(".spt_script_edit");
                var script_path_title = top.getElement(".spt_script_path_title");
                var is_read_only = script_path_title.getAttribute('readonly');
                
                //var bkgd = script_path_title.getStyle('background');
                
                if (code) {
                    if (is_read_only) {
                        buttons_div = top.getElement(".spt_script_edit_buttons");
                        if (buttons_div.getAttribute('edit') != 'true' )
                            script_path_title.removeAttribute('readonly');
                    }
                } else {
                    script_path_title.setAttribute('readonly','readonly');
                }
             }, 250);
            '''
        } )
        slash = DivWdg('/')
        slash.add_styles('font-size: 1.7em; margin: 4px 5px 0 3px; float: left')
        script_path_div.add(slash)
        script_path_folder_text.add_styles("width: 120px; float: left")
        if script_obj:
            script_path_folder_text.set_value(script_path_folder)
        
        script_path_title_text = LookAheadTextInputWdg(name="script_path_title", search_type="config/custom_script", column="title", filters=filters, width='240')
        script_path_title_text.add_class("spt_script_path_title")

        script_path_div.add(script_path_title_text)

        script_path_title_text.add_style("float: left")
        if script_obj:
            script_path_title_text.set_value(script_path_title)
        script_path_title_text.add_behavior( {
            'type': 'blur',
            'cbjs_action': '''
             setTimeout( function() {

                var script_path_title = bvr.src_el.value;
                var top = bvr.src_el.getParent(".spt_script_edit");
                var buttons_div = top.getElement(".spt_script_edit_buttons");

                spt.show(buttons_div);

                var script_path_folder = top.getElement(".spt_script_path_folder").value;
                var script_path = script_path_folder + '/' + script_path_title;
                var el = top.getElement(".spt_python_script_text");
                var script = '';
                if (script_path_folder && script_path_title) {
                    var popup = false;
                    script = spt.CustomProject.get_script_by_path(script_path, popup);
                }
                if (script_path_folder && script_path_title) { 
                    if (script) {
                        el.value = script;
                        spt.show(el);
                    }
                    else {
                        el.value = '';
                    }
                }


                
            
             }, 250);
            '''
        } )

        script_path_div.add("<br clear='all'/>")

        if language == "python":
            div.add("Language: <b>Python</b>")
        else:
            div.add("Language: <b>Server Javascript</b>")

        if script_path:


            edit_label = "Click to enable Edit"

            enable_edit_button = DivWdg()
            div.add(enable_edit_button)
            enable_edit_button.add(edit_label)
            enable_edit_button.add_class("hand")
            enable_edit_button.add_style("text-decoration: underline")
            enable_edit_button.add_style("margin-top: 10px")
            enable_edit_button.add_style("margin-bottom: 3px")
            enable_edit_button.add_behavior( {
                'type': 'click',
                'cbjs_action': '''
                var top = bvr.src_el.getParent(".spt_script_edit");
                var el = top.getElement(".spt_python_script_text");
                el.removeAttribute("readonly");
                el.setStyle("background", "");
                '''
            } )


            script_text = TextAreaWdg("script")
            script_text.add_style('padding-top: 10px')
            script_text.add_style('margin-top: 10px')
            script_text.add_style('font-size: 1.2em')
            script_text.set_option("read_only", "true")
            script_text.add_style("background", "#EEE");
            script_text.add_class("form-control")
            script_text.add_class("spt_python_script_text")
            div.add(script_text)
                    
            if script:
                script_text.set_value(script)
            script_text.add_style("height: 300px")
            script_text.add_style("width: auto")


        return div



    def get_new_script_wdg(self, is_admin):

        div = DivWdg()


        if is_admin:
            div.add("Language:")
            select = SelectWdg("language")
            div.add(select)
            select.set_option("labels", "Python|Server Javascript")
            select.set_option("values", "python|server_js")

        else:
            div.add("Language: <b>Server Javascript</b>")


            div.add("<br/>")
            div.add("<br/>")
            div.add("<br/>")




        run_title = DivWdg("Enter new script_code")
        run_title.add_style('margin-bottom: 3px')
        run_title.add_style('margin-top: 10px')
        div.add(run_title)



        script_text = TextAreaWdg("script")
        script_text.add_style('padding-top: 10px')
        script_text.add_class("form-control")
        script_text.add_class("spt_python_script_text")
 
        script_text.add_style("height: 300px")
        script_text.add_style("width: auto")

        div.add(script_text)

        return div





class ActionInfoWdg(BaseInfoWdg):

    def get_display(self):

        top = self.top
        top.add_class('spt_action_info_top')
        top.add_style("padding: 20px 0px")

        process = self.kwargs.get("process")
        pipeline_code = self.kwargs.get("pipeline_code")
        node_type = self.kwargs.get("node_type")

        pipeline = Pipeline.get_by_code(pipeline_code)

        # get the pipeline
        search = Search("sthpw/pipeline")
        search.add_filter("code", pipeline_code)
        pipeline = search.get_sobject()


        # get the process sobject
        search = Search("config/process")
        search.add_filter("pipeline_code", pipeline_code)
        search.add_filter("process", process)
        process_sobj = search.get_sobject()


        event = "process|action"

        language = ""

        # get the trigger
        script = None
        script_path = ""
        process_code = ""
        on_action_class = ""
        action = ""
        execute_mode = ""

        if process_sobj:
            process_code = process_sobj.get_code()
            search = Search("config/trigger")
            search.add_filter("process", process_code)
            search.add_filter("event", event)
            trigger = search.get_sobject()
            # get the custom script 
            if trigger:
                script_path = trigger.get("script_path")
                on_action_class = trigger.get("class_name")
                execute_mode = trigger.get("mode")

                if script_path:
                    action = "script_path"
                elif on_action_class:
                    action = "command"
                else:
                    action = "create_new"


    
                if script_path:
                    folder, title = os.path.split(script_path)

                    search = Search("config/custom_script")
                    search.add_filter("folder", folder)
                    search.add_filter("title", title)
                    custom_script = search.get_sobject()
                    if custom_script:
                        script = custom_script.get("script")
                        language = custom_script.get("language")



        if not action:
            action = "create_new"



        title_wdg = self.get_title_wdg(process, node_type)
        top.add(title_wdg)



        info_div = DivWdg()
        top.add(info_div)
        info_div.add("A action process is a automated process which can execute a script or Python command when invoded from a previous process.")
        info_div.add_style("margin: 10px 10px 20px 10px")


        desc_div = self.get_description_wdg(process_sobj)
        top.add(desc_div)



        #input_output_wdg = self.get_input_output_wdg(pipeline, process)
        #top.add(input_output_wdg)


        form_wdg = DivWdg()
        top.add(form_wdg)
        form_wdg.add_style("padding: 10px")
        form_wdg.add_class("spt_form_top")

        is_admin = Environment.get_security().is_admin()

        if node_type == "action":
            form_wdg.add("<b>Action:</b><br/>")
            form_wdg.add("This will be the automatically executed action for this process.")

        else:
            form_wdg.add("<b>Check Condition</b><br/>")
            form_wdg.add("This will be executed on the completion event of an input process.  The condition check should either return True or False or a list of the output streams.")


        form_wdg.add("<br/>")
        form_wdg.add("<br/>")



        form_wdg.add("Select which action to take:")
        select = SelectWdg("action")
        form_wdg.add(select)


        options = []
        labels = []


        labels.append("Use Existing Script")
        options.append("script_path") 
        labels.append("Create New Script")
        options.append("create_new") 

        if is_admin:
            labels.append("Use Python Command Class")
            options.append("command") 
                    
        select.set_option("labels", labels)
        select.set_option("values", options)

        if action:
            select.set_value(action)
        form_wdg.add("<br/>")

        select.add_behavior( {
            'type': 'change',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_form_top");
            var script_el = top.getElement(".spt_script_edit");
            var value = bvr.src_el.value;
            spt.panel.refresh_element(script_el, {action: value});
            '''
        } )


        script_wdg = ScriptSettingsWdg(
            action=action,
            on_action_class=on_action_class,
            script_path=script_path,
            script=script,
            language=language,
            execute_mode=execute_mode,

        )
        form_wdg.add(script_wdg)


        form_wdg.add("<br clear='all'/>")

        save = ActionButtonWdg(title="Save", color="primary")
        save.add_style("float: right")
        
        top.add(save)
        top.add(HtmlElement.br(2))
        save.add_behavior( {
            'type': 'click_up',
            'pipeline_code': pipeline_code,
            'process': process,
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_action_info_top");
            var input = spt.api.get_input_values(top, null, false);
            var action = input.action;
            var script_new = input.script_new;
            var script_path_folder = input.script_path_folder;
            var script_path_title = input.script_path_title;
            var script_path = (script_path_folder && script_path_title) ? script_path_folder + "/" + script_path_title : '';

            var popup = false
            var test = script_path ? spt.CustomProject.get_script_by_path(script_path, popup) : true;
            if (!test) {
                spt.error('Invalid script path [' + script_path + '] is specified.');
                return;
            }

            // either (script_path && script) or script_new
            var script = input.script;
            if (script_new) {
                if (script_path) {
                    spt.alert('You have both script path and New script specified. Please clear either one before saving.');
                    return;
                }
                else {
                    script = script_new;
                }
            }
            if (script_path && !script) {
                spt.error('You have most likely specified an invalid script path since the script content is empty.');
                return;
            }
            var server = TacticServerStub.get();
            var class_name = 'tactic.ui.tools.ProcessInfoCmd';
            var kwargs = {
                node_type: 'action',
                action: action,
                pipeline_code: bvr.pipeline_code,
                process: bvr.process,
                script: script,
                script_path: script_path,
                on_action_class: input.on_action_class,
                execute_mode: input.execute_mode,
                script_path: script_path,
                language: input.language,
            }

            var cbk = function() {
                
                spt.panel.refresh(top);

            }
            server.execute_cmd(class_name, kwargs, {}, {on_complete: cbk});


            '''
        } )




        return top




    def get_process_triggers(self):

        form_wdg = DivWdg()


        form_wdg.add("<h2>Process Triggers</h2>")
        form_wdg.add("<hr/>")

        events = ['pending','action','complete','revise']

        form_wdg.add("Event")
        select = SelectWdg("event")
        form_wdg.add(select)
        select.set_option("values", events)

        form_wdg.add("<br/>")

        form_wdg.add("Action")
        text = TextAreaWdg(name="on_complete")
        text.add_class("form-control")
        form_wdg.add(text)
        form_wdg.add("<br/>")




        form_wdg.add("Complete")
        text = TextAreaWdg(name="on_complete")
        text.add_class("form-control")
        form_wdg.add(text)
        form_wdg.add("<br/>")


        form_wdg.add("Revise")
        text = TextAreaWdg(name="on_revise")
        text.add_class("form-control")
        form_wdg.add(text)
        form_wdg.add("<br/>")


        form_wdg.add("Pending")
        text = TextAreaWdg(name="pending")
        text.add_class("form-control")
        form_wdg.add(text)
        form_wdg.add("<br/>")


        save = ActionButtonWdg(title="Save", color="primary")
        save.add_style("float: right")
        top.add(save)
        save.add_behavior( {
            'type': 'click_up',
            'pipeline_code': pipeline_code,
            'process': process,
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_pipeline_info_top");
            var input = spt.api.get_input_values(top, null, false);

            '''
        } )

        return form_wdg




class UnknownInfoWdg(BaseInfoWdg):

    def get_display(self):

        process = self.kwargs.get("process")
        pipeline_code = self.kwargs.get("pipeline_code")
        node_type = self.kwargs.get("node_type")

 

        search = Search("config/process")
        search.add_filter("pipeline_code", pipeline_code)
        search.add_filter("process", process)
        process_sobj = search.get_sobject()


        workflow = process_sobj.get_json_value("workflow")
        if not workflow:
            workflow = {}



        top = self.top
        top.add_style("padding: 20px 0px")
        top.add_class("spt_approval_info_top")

        process = self.kwargs.get("process")
        pipeline_code = self.kwargs.get("pipeline_code")
        node_type = self.kwargs.get("node_type")


        pipeline = Pipeline.get_by_code(pipeline_code)


        title_wdg = self.get_title_wdg(process, node_type)
        top.add(title_wdg)

        msg_div = DivWdg()
        top.add(msg_div)
        msg_div.add_style("margin: 30px auto")
        msg_div.add_style("padding: 20px")
        msg_div.add_style("border: solid 1px #EEE")
        msg_div.add("This node type is not recognized")
        msg_div.add_style("text-align: center")
        msg_div.add_color("background", "background3")

        return top






class ApprovalInfoWdg(BaseInfoWdg):

    def get_display(self):

        process = self.kwargs.get("process")
        pipeline_code = self.kwargs.get("pipeline_code")
        node_type = self.kwargs.get("node_type")

 

        search = Search("config/process")
        search.add_filter("pipeline_code", pipeline_code)
        search.add_filter("process", process)
        process_sobj = search.get_sobject()
        workflow = {}
        if process_sobj:
            workflow = process_sobj.get_json_value("workflow")
        if not workflow:
            workflow = {}



        top = self.top
        top.add_style("padding: 20px 0px")
        top.add_class("spt_approval_info_top")

        process = self.kwargs.get("process")
        pipeline_code = self.kwargs.get("pipeline_code")
        node_type = self.kwargs.get("node_type")


        pipeline = Pipeline.get_by_code(pipeline_code)


        title_wdg = self.get_title_wdg(process, node_type)
        top.add(title_wdg)


        info_div = DivWdg()
        top.add(info_div)
        info_div.add("An approval process is used a specific user will have the task to approve work down in the previous processes.")
        info_div.add_style("margin: 10px 10px 20px 10px")



        desc_div = self.get_description_wdg(process_sobj)
        top.add(desc_div)





        input_output_wdg = self.get_input_output_wdg(pipeline, process)
        top.add( input_output_wdg )



        has_tasks = True
        if has_tasks:
            div = DivWdg()
            top.add(div)
            div.add_style("padding: 10px")
            div.add("<b>Task setup</b><br/>")
            div.add("Task options allow you to control various default properties of tasks.")

            if process_sobj:
                process_key = process_sobj.get_search_key()
            else:
                process_key = None

            div.add("<br/>"*2)

            button = ActionButtonWdg(title="Task Setup", size="block")
            div.add(button)
            button.add_class("btn-clock")
            button.add_behavior( {
                'type': 'click_up',
                'pipeline_code': pipeline_code,
                'process': process,
                'search_key': process_key,
                'cbjs_action': '''
                var class_name = "tactic.ui.tools.PipelinePropertyWdg";
                var kwargs = {
                    pipeline_code: bvr.pipeline_code,
                    process: bvr.process
                }
                var popup = spt.panel.load_popup("Task Setup", class_name, kwargs);
                var nodes = spt.pipeline.get_selected_nodes();
                var node = nodes[0];
                spt.pipeline_properties.show_properties2(popup, node);
                '''
            } )




        form_wdg = DivWdg()
        top.add(form_wdg)
        form_wdg.add_style("padding: 15px")

        form_wdg.add("Set a default person that will be assigned to tasks in this process.")

        form_wdg.add("<br/>")
        form_wdg.add("<br/>")

        from tactic.ui.input import LookAheadTextInputWdg
        text = LookAheadTextInputWdg(
                name="assigned",
                search_type="sthpw/login",
                value_column="login",
                column="display_name"
        )
        form_wdg.add(text)
        text.add_style("width: 100%")
        if workflow.get("assigned"):
            text.set_value(workflow.get("assigned"))


        form_wdg.add("<br/>")
        form_wdg.add("<br/>")


        #save = ActionButtonWdg(title="Save", color="primary")
        #save.add_style("float: right")
        #form_wdg.add(save)
        text.add_behavior( {
            'type': 'blur',
            'pipeline_code': pipeline_code,
            'process': process,
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_approval_info_top");
            var input = spt.api.get_input_values(top, null, false);

            var server = TacticServerStub.get();
            var class_name = 'tactic.ui.tools.ProcessInfoCmd';
            var kwargs = {
                node_type: 'approval',
                pipeline_code: bvr.pipeline_code,
                process: bvr.process,
                assigned: input.assigned,
            }


            server.execute_cmd(class_name, kwargs);


            '''
        } )

       

        return top


class ConditionInfoWdg(ActionInfoWdg):
    pass


class HierarchyInfoWdg(BaseInfoWdg):

    def get_display(self):

        process = self.kwargs.get("process")
        pipeline_code = self.kwargs.get("pipeline_code")
        node_type = self.kwargs.get("node_type")


        pipeline = Pipeline.get_by_code(pipeline_code)
        search_type = pipeline.get_value("search_type")

        top = self.top
        top.add_style("padding: 20px 0px")
        top.add_class("spt_hierarchy_top")

 
        title_wdg = self.get_title_wdg(process, node_type)
        top.add(title_wdg)


        info_div = DivWdg()
        top.add(info_div)
        info_div.add("A hierarchy process is a process that references a sub-workflow.")
        info_div.add_style("margin: 10px 10px 20px 10px")




        top.add( self.get_description_wdg(pipeline) )

        settings_wdg = DivWdg()
        top.add(settings_wdg)
        settings_wdg.add_style("padding: 10px")


        search = Search("config/process")
        search.add_filter("pipeline_code", pipeline_code)
        search.add_filter("process", process)
        process_sobj = search.get_sobject()




        workflow = process_sobj.get_json_value("workflow")
        if not workflow:
            workflow = {}


        search = Search("sthpw/pipeline")
        search.add_filter("search_type", search_type)
        search.add_filter("code", pipeline_code, op="!=")
        subpipelines = search.get_sobjects()

        values = [x.get("code") for x in subpipelines]
        labels = [x.get("name") for x in subpipelines]

        subpipeline_code = process_sobj.get_value("subpipeline_code")

        settings_wdg.add("<b>Points to a sub Workflow:</b>")
        select = SelectWdg("subpipeline")
        settings_wdg.add(select)
        if subpipeline_code:
            select.set_value(subpipeline_code)
        select.set_option("values", values)
        select.set_option("labels", labels)
        select.add_empty_option("-- Select --")
        settings_wdg.add("<span style='opacity: 0.6'>Reference another workflow</span>")

        settings_wdg.add("<br/>")
        settings_wdg.add("<br/>")


        # auto create sb tasks
        values = ["subtasks_only", "top_only", "all", "none"]
        labels = ["Create SubTasks Only", "Top Task Only", "Both Top and SubTasks", "No Tasks"]

        task_creation = workflow.get("task_creation") or "subtasks_only"

        settings_wdg.add("<b>Task Creation:</b>")
        select = SelectWdg("task_creation")
        settings_wdg.add(select)
        if task_creation:
            select.set_value(task_creation)
        select.set_option("values", values)
        select.set_option("labels", labels)
        select.add_empty_option("-- Select --")
        settings_wdg.add("<span style='opacity: 0.6'>Determine whether tasks of the referenced workflow are created when generating an inital schedule</span>")

        settings_wdg.add("<br/>")
        settings_wdg.add("<br/>")




        save_button = ActionButtonWdg(title="Save", color="primary")
        settings_wdg.add(save_button)
        save_button.add_style("float: right")
        save_button.add_style("padding-top: 3px")
        save_button.add_behavior( {
            'type': 'click_up',
            'process': process,
            'pipeline_code': pipeline_code,
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_hierarchy_top");
            var values = spt.api.get_input_values(top, null, false);
            var class_name = 'tactic.ui.tools.ProcessInfoCmd';
            var kwargs = values;
            values['node_type'] = 'hierarchy';
            values['process'] = bvr.process;
            values['pipeline_code'] = bvr.pipeline_code;

            var server = TacticServerStub.get();
            server.execute_cmd( class_name, values);
            
            '''
        } )


 
        return top


class DependencyInfoWdg(BaseInfoWdg):

    def get_display(self):

        process = self.kwargs.get("process")
        pipeline_code = self.kwargs.get("pipeline_code")
        node_type = self.kwargs.get("node_type")


        search = Search("config/process")
        search.add_filter("pipeline_code", pipeline_code)
        search.add_filter("process", process)
        process_sobj = search.get_sobject()




        top = self.top
        top.add_style("padding: 20px 0px")
        top.add_class("spt_dependency_top")

 
        title_wdg = self.get_title_wdg(process, node_type)
        top.add(title_wdg)


        settings_wdg = DivWdg()
        top.add(settings_wdg)
        settings_wdg.add_style("padding: 10px")


        workflow = process_sobj.get_json_value("workflow")
        if not workflow:
            workflow = {}

        related_search_type = workflow.get("search_type")
        related_process = workflow.get("process")
        related_status = workflow.get("status")
        related_scope = workflow.get("scope")
        related_wait = workflow.get("wait")


        # FIXME: HARD CODED
        search_type = "vfx/asset"

        project = Project.get()
        search_type_sobjs = project.get_search_types(include_multi_project=True)

        # find out which ones have pipeline_codes
        filtered_sobjs = []
        for search_type_sobj in search_type_sobjs:
            base_type = search_type_sobj.get_base_key()
            exists = SearchType.column_exists(base_type, "pipeline_code")
            if exists:
                filtered_sobjs.append(search_type_sobj)

        search_types = [x.get_base_key() for x in search_type_sobjs]
        values = [x.get_base_key() for x in filtered_sobjs]
        labels = ["%s (%s)" % (x.get_title(), x.get_base_key()) for x in filtered_sobjs]


        settings_wdg.add("<br/>")
        settings_wdg.add("<b>Notify Search Type</b>")
        select = SelectWdg("related_search_type")
        settings_wdg.add(select)
        if related_search_type:
            select.set_value(related_search_type)
        select.set_option("values", values)
        select.set_option("labels", labels)
        select.add_empty_option("-- Select --")
        settings_wdg.add("<span style='opacity: 0.6'>This will set a dependency on the stype</span>")
        settings_wdg.add("<br/>")


        # notify all search types
        from pyasm.widget import RadioWdg

        scope_div = DivWdg()
        settings_wdg.add(scope_div)
        scope_div.add_style("margin: 15px 25px")

        radio = RadioWdg("related_scope")
        radio.set_option("value", "local")
        scope_div.add(radio)
        if related_scope == "local" or not related_scope:
            radio.set_checked()
        scope_div.add(" Only Related Items<br/>")

        radio = RadioWdg("related_scope")
        radio.set_option("value", "global")
        if related_scope == "global":
            radio.set_checked()
        scope_div.add(radio)
        scope_div.add(" All Items")
        scope_div.add("<br/>")


       






        search = Search("sthpw/pipeline")
        search.add_filter("search_type", search_type)
        related_pipelines = search.get_sobjects()

        values = set()
        for related_pipeline in related_pipelines:
            related_process_names = related_pipeline.get_process_names()
            for x in related_process_names:
                values.add(x)

        values = list(values)
        values.sort()

        settings_wdg.add("<br/>")
        settings_wdg.add("<b>To Process</b>")
        select = SelectWdg("related_process")
        if related_process:
            select.set_value(related_process)
        settings_wdg.add(select)
        select.set_option("values", values)
        select.add_empty_option("-- Select --")
        settings_wdg.add("<span style='opacity: 0.6'>Determines which process to connect to</span>")
        settings_wdg.add("<br/>")



        settings_wdg.add("<br/>")
        settings_wdg.add("<b>With Status</b>")
        select = SelectWdg("related_status")
        if related_status:
            select.set_value(related_status)
        settings_wdg.add(select)
        select.set_option("values", "Pending|Action|Complete")
        select.add_empty_option("-- Select --")
        settings_wdg.add("<span style='opacity: 0.6'>Determines which status to set the process to.</span>")
        settings_wdg.add("<br/>")





        settings_wdg.add("<br/>")
        settings_wdg.add("<b>Wait</b>")
        select = SelectWdg("related_wait")
        if related_wait:
            select.set_value(related_wait)
        settings_wdg.add(select)
        select.set_option("labels", "No|Yes")
        select.set_option("values", "false|true")
        #select.add_empty_option("-- Select --")
        settings_wdg.add("<span style='opacity: 0.6'>Determines if this process will wait until it receives a complete signal (from another dependency) or set to complete automatically")
        settings_wdg.add("<br/>")




        settings_wdg.add("<br/>")

        save_button = ActionButtonWdg(title="Save", color="primary")
        settings_wdg.add(save_button)
        save_button.add_style("float: right")
        save_button.add_style("padding-top: 3px")
        save_button.add_behavior( {
            'type': 'click_up',
            'process': process,
            'pipeline_code': pipeline_code,
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_dependency_top");
            var values = spt.api.get_input_values(top, null, false);
            var class_name = 'tactic.ui.tools.ProcessInfoCmd';
            var kwargs = values;
            values['node_type'] = 'dependency';
            values['process'] = bvr.process;
            values['pipeline_code'] = bvr.pipeline_code;

            var server = TacticServerStub.get();
            server.execute_cmd( class_name, values);
            
            '''
        } )



        settings_wdg.add("<br clear='all'/>")


        return top




class ProgressInfoWdg(BaseInfoWdg):

    def get_display(self):

        process = self.kwargs.get("process")
        pipeline_code = self.kwargs.get("pipeline_code")
        node_type = self.kwargs.get("node_type")


        search = Search("config/process")
        search.add_filter("pipeline_code", pipeline_code)
        search.add_filter("process", process)
        process_sobj = search.get_sobject()




        top = self.top
        top.add_style("padding: 20px 0px")
        top.add_class("spt_progress_top")

 
        title_wdg = self.get_title_wdg(process, node_type)
        top.add(title_wdg)


        settings_wdg = DivWdg()
        top.add(settings_wdg)
        settings_wdg.add_style("padding: 0px 10px")

      
        workflow = {}
        if process_sobj:
            workflow = process_sobj.get_json_value("workflow") or {}
        
        related_search_type = workflow.get("search_type")
        related_pipeline_code = workflow.get("pipeline_code")
        related_process = workflow.get("process")
        related_status = workflow.get("status")
        related_scope = workflow.get("scope")
        related_wait = workflow.get("wait")


        # overrides
        web = WebContainer.get_web()
        if web.get_form_value("related_search_type"):
            related_search_type = web.get_form_value("related_search_type")
        if web.get_form_value("related_pipeline_code"):
            related_pipeline_code = web.get_form_value("related_pipeline_code")


        project = Project.get()
        search_type_sobjs = project.get_search_types(include_multi_project=True)

        # find out which ones have pipeline_codes
        filtered_sobjs = []
        for search_type_sobj in search_type_sobjs:
            base_type = search_type_sobj.get_base_key()
            exists = SearchType.column_exists(base_type, "pipeline_code")
            if not exists:
                exists = SearchType.column_exists(base_type, "status")
            if exists:
                filtered_sobjs.append(search_type_sobj)

        search_types = [x.get_base_key() for x in search_type_sobjs]
        values = [x.get_base_key() for x in filtered_sobjs]
        labels = ["%s (%s)" % (x.get_title(), x.get_base_key()) for x in filtered_sobjs]


        settings_wdg.add("<br/>")
        settings_wdg.add("<b>Listen to events from:</b>")
        select = SelectWdg("related_search_type")
        settings_wdg.add(select)
        if related_search_type:
            select.set_value(related_search_type)
        select.set_option("values", values)
        select.set_option("labels", labels)
        select.add_empty_option("-- Select --")
        settings_wdg.add("<span style='opacity: 0.6'>This process will track the progress of the items of the selected search type.</span>")
        settings_wdg.add("<br/>")


        select.add_behavior( {
            'type': 'change',
            'cbjs_action': '''
            var kwargs = {
                related_search_type: bvr.src_el.value
            }
            spt.panel.refresh(bvr.src_el, kwargs);
            '''
        } )


        from pyasm.widget import RadioWdg

        settings_wdg.add("<br/>")
        settings_wdg.add("<b>Scope by which items to track:</b>")

        scope_div = DivWdg()
        settings_wdg.add(scope_div)
        scope_div.add_style("margin: 15px 25px")

        radio = RadioWdg("related_scope")
        radio.set_option("value", "local")
        scope_div.add(radio)
        if related_scope == "local" or not related_scope:
            radio.set_checked()
        scope_div.add(" Only Related Items<br/>")

        radio = RadioWdg("related_scope")
        radio.set_option("value", "global")
        if related_scope == "global":
            radio.set_checked()
        scope_div.add(radio)
        scope_div.add(" All Items in List")
        scope_div.add("<br/>")




        search = Search("sthpw/pipeline")
        search.add_filter("search_type", related_search_type)
        search.add_project_filter()
        related_pipelines = search.get_sobjects()



        labels = ["%s (%s)" % (x.get_value("name"), x.get_value("search_type")) for x in related_pipelines]
        values = [x.get_value("code") for x in related_pipelines]



        settings_wdg.add("<br/>")
        settings_wdg.add("<b>Listen to Workflow</b>")
        select = SelectWdg("related_pipeline_code")
        if related_pipeline_code:
            select.set_value(related_pipeline_code)
        settings_wdg.add(select)
        select.set_option("values", values)
        select.set_option("labels", labels)
        select.add_empty_option("-- %s --" % "any")
        settings_wdg.add("<span style='opacity: 0.6'>Determines which workflow to track.</span>")

        select.add_behavior( {
            'type': 'change',
            'related_search_type': related_search_type,
            'cbjs_action': '''
            var kwargs = {
                related_search_type: bvr.related_search_type,
                related_pipeline_code: bvr.src_el.value
            }
            spt.panel.refresh(bvr.src_el, kwargs);
            '''
        } )


        settings_wdg.add("<br/>"*2)




        values = set()
        for related_pipeline in related_pipelines:
            if related_pipeline_code:
                if related_pipeline.get_code() not in related_pipeline_code:
                    continue

            related_process_names = related_pipeline.get_process_names()
            for x in related_process_names:
                values.add(x)

        values = list(values)
        values.sort()

        settings_wdg.add("<br/>")
        settings_wdg.add("<b>Listen to Process</b>")
        select = SelectWdg("related_process")
        if related_process:
            select.set_value(related_process)
        settings_wdg.add(select)
        select.set_option("values", values)
        select.add_empty_option("-- %s --" % process)
        settings_wdg.add("<span style='opacity: 0.6'>Determines which process to track.  If empty, it will use the same process name.</span>")
        settings_wdg.add("<br/>")




        settings_wdg.add("<br/>")

        save_button = ActionButtonWdg(title="Save", color="primary")
        settings_wdg.add(save_button)
        save_button.add_style("float: right")
        save_button.add_style("padding-top: 3px")
        save_button.add_behavior( {
            'type': 'click_up',
            'process': process,
            'pipeline_code': pipeline_code,
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_progress_top");
            var values = spt.api.get_input_values(top, null, false);
            var class_name = 'tactic.ui.tools.ProcessInfoCmd';
            var kwargs = values;
            values['node_type'] = 'progress';
            values['process'] = bvr.process;
            values['pipeline_code'] = bvr.pipeline_code;

            var server = TacticServerStub.get();
            server.execute_cmd( class_name, values);
            
            '''
        } )



        settings_wdg.add("<br clear='all'/>")


        return top






class TaskStatusInfoWdg(BaseInfoWdg):

    def get_display(self):

        process = self.kwargs.get("process")
        pipeline_code = self.kwargs.get("pipeline_code")
        node_type = self.kwargs.get("node_type")



        top = self.top
        top.add_style("padding: 20px 0px")

        top.add_class("spt_status_top")
 
        title_wdg = self.get_title_wdg(process, node_type, show_node_type_select=False)
        top.add(title_wdg)



        search = Search("config/process")
        search.add_filter("pipeline_code", pipeline_code)
        search.add_filter("process", process)
        process_sobj = search.get_sobject()
        workflow = {}
        color = None
        if process_sobj:
            workflow = process_sobj.get_json_value("workflow")
            color = process_sobj.get_value("color")

        if not workflow:
            workflow = {}
        if not color:
            from pyasm.biz import Task
            color = Task.get_default_color(process)
           
        direction = workflow.get("direction")
        to_status = workflow.get("status")
        mapping = workflow.get("mapping")

        settings_wdg = DivWdg()
        top.add(settings_wdg)
        settings_wdg.add_style("padding: 0px 10px")

        settings_wdg.add("<b>Task Status Action</b>")
        settings_wdg.add("<br/>")
        settings_wdg.add("<br/>")
        
        title = DivWdg("When set to this status, do the following:")
        title.add_style('padding-bottom: 12px')

        settings_wdg.add(title)

        div = DivWdg("Behave as:")
        div.add_style('padding-bottom: 2px')

        settings_wdg.add(div)
        select = SelectWdg(name="mapping")
        select.add_class('spt_task_direction')
        select.add_empty_option()
        select.set_option('values', 'Assignment|Pending|In Progress|Waiting|Need Assistance|Revise|Reject|Complete|Approved')
        if mapping:
            select.set_value(mapping)
        settings_wdg.add(select)


        settings_wdg.add(HtmlElement.br())
        sep = DivWdg("OR")
        sep.add_style('text-align: center')
        sep.add_style('margin: auto')
        settings_wdg.add(sep)
        settings_wdg.add(HtmlElement.br())

        select = SelectWdg(name="direction")
        select.add_empty_option()
        settings_wdg.add(select)
        values = ["output", "input", "process"]
        # we don't know the parent process this could be used in
        labels = ["Set output process", "Set input process", "Set this process"]
        if direction:
            select.set_value(direction)
        select.set_option("values", values)
        select.set_option("labels", labels)

        settings_wdg.add("<br/>")

        div = DivWdg("to Status:")
        div.add_style('padding-bottom: 2px')
        settings_wdg.add(div)
        text = TextInputWdg(name="status")
        if to_status:
            text.set_value(to_status)
        text.add_behavior({'type': 'blur',
            'cbjs_action': 
            
            '''var top = bvr.src_el.getParent('.spt_status_top');
            var map = top.getElement('.spt_task_direction');
            if (map.value && bvr.src_el.value) {
                bvr.src_el.value = '';
                spt.info('"Behave as" should be cleared if you want to set a custom status.');
            }'''})
                
        settings_wdg.add(text)
        text.add_style("width: 100%")

        settings_wdg.add("<br/>")
        settings_wdg.add("<hr/>")
        settings_wdg.add("<br/>")
        
        # Color
        color_div = DivWdg("<b>Color</b>:")
        color_div.add_style('padding-bottom: 2px')
        settings_wdg.add(color_div)
        color_input = ColorInputWdg("color")
        color_input.set_value(color)
        settings_wdg.add(color_input)
       
        settings_wdg.add("<br/>")

        save_button = ActionButtonWdg(title="Save", color="primary")
        settings_wdg.add(save_button)
        save_button.add_style("float: right")
        save_button.add_style("padding-top: 3px")
        save_button.add_behavior( {
            'type': 'click_up',
            'process': process,
            'pipeline_code': pipeline_code,
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_status_top");
            var values = spt.api.get_input_values(top, null, false);
            var class_name = 'tactic.ui.tools.ProcessInfoCmd';
            var kwargs = values;
            values['node_type'] = 'status';
            values['process'] = bvr.process;
            values['pipeline_code'] = bvr.pipeline_code;
            
            // Update process sObject
            var server = TacticServerStub.get();
            server.execute_cmd( class_name, values);
            
            // Update pipeline sObject xml
            color = values['color'];
            var node = spt.pipeline.get_selected_node();
            if (!node) {
                node = spt.pipeline.get_node_by_name(bvr.process);
            }
            node.properties['color'] = color;
            
            var groups = spt.pipeline.get_groups();
            for (group_name in groups) {
                var xml = spt.pipeline.export_group(group_name);
                var search_key = server.build_search_key("sthpw/pipeline", group_name);
                try {
                    // Refresh the canvas to display new color.
                    spt.pipeline.remove_group(group_name);
                    spt.pipeline.unselect_all_nodes();
                    results = server.insert_update(search_key, {'pipeline': xml}); 
                } catch(e) {
                    spt.alert(spt.exception.handler(e));
                }
                spt.pipeline.import_pipeline(group_name);
            }
            

            '''
        } )




        return top




class ProcessInfoCmd(Command):

    def execute(self):

        node_type = self.kwargs.get("node_type")

        if node_type in ["action", "condition"]:
            return self.handle_action()

        if node_type == 'dependency':
            return self.handle_dependency()

        if node_type == 'status':
            return self.handle_status()

        if node_type == 'approval':
            return self.handle_approval()

        if node_type == 'hierarchy':
            return self.handle_hierarchy()

        if node_type == 'progress':
            return self.handle_progress()





    def handle_action(self):

        is_admin = Environment.get_security().is_admin()


        action = self.kwargs.get("action") or "create_new"
        script = self.kwargs.get("script")
        script_path = self.kwargs.get("script_path")
        on_action_class = self.kwargs.get("on_action_class")

        execute_mode = self.kwargs.get("execute_mode")

        pipeline_code = self.kwargs.get("pipeline_code")
        process = self.kwargs.get("process")


        if is_admin:
            language = self.kwargs.get("language")
            if not language:
                language = "python"
        else:
            language = "server_js"

        pipeline = Pipeline.get_by_code(pipeline_code)


        search = Search("config/process")
        search.add_filter("pipeline_code", pipeline_code)
        search.add_filter("process", process)
        process_sobj = search.get_sobject()


        event = "process|action"

        from trigger_wdg import TriggerToolWdg

        folder = "%s/%s" % (TriggerToolWdg.FOLDER_PREFIX, pipeline.get_code())
        title = process_sobj.get_code()

        # check to see if the trigger already exists
        search = Search("config/trigger")
        search.add_filter("event", event)
        search.add_filter("process", process_sobj.get_code())
        trigger = search.get_sobject()
        if not trigger:
            # create a new one
            trigger = SearchType.create("config/trigger")
            trigger.set_value("event", event)
            trigger.set_value("process", process_sobj.get_code())


        if action == "command":
            trigger.set_value("script_path", "NULL", quoted=False)
            trigger.set_value("class_name", on_action_class)

        else:
            if script_path:
                folder, title = os.path.split(script_path)
            else:
                script_path = "%s/%s" % (folder, title)
            
            if script:
                trigger.set_value("script_path", script_path)
            else:
                trigger.set_value("class_name", on_action_class)

            trigger.set_value("class_name", "NULL", quoted=False)




        if execute_mode:
            trigger.set_value("mode", execute_mode)


        trigger.commit()

        if script:

            from pyasm.security import Sudo

            sudo = Sudo()
            try:

                # check to see if the script already exists
                search = Search("config/custom_script")
                search.add_filter("folder", folder)
                search.add_filter("title", "%s" % title)
                script_obj = search.get_sobject()
                if not script_obj:
                    script_obj = SearchType.create("config/custom_script")
                    script_obj.set_value("folder", folder)
                    script_obj.set_value("title", "%s" % title)

                script_obj.set_value("language", language)
                script_obj.set_value("script", script)
                script_obj.commit()

            finally:
                sudo.exit()


    def handle_dependency(self):

        pipeline_code = self.kwargs.get("pipeline_code")
        process = self.kwargs.get("process")

        pipeline = Pipeline.get_by_code(pipeline_code)

        search = Search("config/process")
        search.add_filter("pipeline_code", pipeline_code)
        search.add_filter("process", process)
        process_sobj = search.get_sobject()


        related_search_type = self.kwargs.get("related_search_type")
        related_process = self.kwargs.get("related_process")
        related_status = self.kwargs.get("related_status")
        related_scope = self.kwargs.get("related_scope")
        related_wait = self.kwargs.get("related_wait")

        workflow = process_sobj.get_json_value("workflow")
        if not workflow:
            workflow = {}

        if related_search_type:
            workflow['search_type'] = related_search_type
        if related_process:
            workflow['process'] = related_process
        if related_status:
            workflow['status'] = related_status
        if related_scope:
            workflow['scope'] = related_scope
        if related_scope:
            workflow['wait'] = related_wait

        process_sobj.set_json_value("workflow", workflow)
        process_sobj.commit()


    def handle_approval(self):
        pipeline_code = self.kwargs.get("pipeline_code")
        process = self.kwargs.get("process")
        assigned = self.kwargs.get("assigned")

        pipeline = Pipeline.get_by_code(pipeline_code)

        search = Search("config/process")
        search.add_filter("pipeline_code", pipeline_code)
        search.add_filter("process", process)
        process_sobj = search.get_sobject()

        workflow = process_sobj.get_json_value("workflow")
        if not workflow:
            workflow = {}
        if assigned:
            workflow['assigned'] = assigned
        process_sobj.set_json_value("workflow", workflow)
        process_sobj.commit()

    def handle_status(self):

        pipeline_code = self.kwargs.get("pipeline_code")
        process = self.kwargs.get("process")

        pipeline = Pipeline.get_by_code(pipeline_code)
        
        search = Search("config/process")
        search.add_filter("pipeline_code", pipeline_code)
        search.add_filter("process", process)
        process_sobj = search.get_sobject()

        if not process_sobj:
            return

        direction = self.kwargs.get("direction")
        status = self.kwargs.get("status")
        mapping = self.kwargs.get("mapping")
        color = self.kwargs.get("color")
        assigned = self.kwargs.get("assigned")

        workflow = process_sobj.get_json_value("workflow")
        if not workflow:
            workflow = {}

        if direction:
            workflow['direction'] = direction
        if status:
            workflow['status'] = status
        if mapping:
            workflow['mapping'] = mapping
   
        if color:
            process_sobj.set_value("color", color)

        if assigned:
            workflow['assigned'] = assigned

        process_sobj.set_json_value("workflow", workflow)
        process_sobj.commit()



    def handle_hierarchy(self):


        pipeline_code = self.kwargs.get("pipeline_code")
        process = self.kwargs.get("process")

        pipeline = Pipeline.get_by_code(pipeline_code)
        search_type = pipeline.get_value("search_type")

        search = Search("config/process")
        search.add_filter("pipeline_code", pipeline_code)
        search.add_filter("process", process)
        process_sobj = search.get_sobject()

        data = process_sobj.get_json_value("workflow") or {}

        subpipeline_code = self.kwargs.get("subpipeline")
        process_sobj.set_value("subpipeline_code", subpipeline_code)
        process_sobj.commit()

        task_creation = self.kwargs.get("task_creation") or "subtasks_only"
        data['task_creation'] = task_creation

        process_sobj.set_value("workflow", data)


        process_sobj.commit()
 

    def handle_progress(self):

        pipeline_code = self.kwargs.get("pipeline_code")
        process = self.kwargs.get("process")

        pipeline = Pipeline.get_by_code(pipeline_code)
        search_type = pipeline.get_value("search_type")

        search = Search("config/process")
        search.add_filter("pipeline_code", pipeline_code)
        search.add_filter("process", process)
        process_sobj = search.get_sobject()


        related_search_type = self.kwargs.get("related_search_type")
        related_pipeline_code = self.kwargs.get("related_pipeline_code")
        related_process = self.kwargs.get("related_process")
        if not related_process:
            related_process = process
        related_scope = self.kwargs.get("related_scope")
        if not related_scope:
            related_scope = "local"

        workflow = process_sobj.get_json_value("workflow")
        if not workflow:
            workflow = {}

        if related_search_type:
            workflow['search_type'] = related_search_type
        if related_pipeline_code:
            workflow['pipeline_code'] = related_pipeline_code
        if related_process:
            workflow['process'] = related_process
        if related_scope:
            workflow['scope'] = related_scope


        # find a related trigger
        trigger_code = workflow.get('trigger_code')
        trigger = None
        if trigger_code:
            search = Search("config/trigger")
            search.add_filter("code", trigger_code)
            trigger = search.get_sobject()

        if not trigger:
            trigger = SearchType.create("config/trigger")

        event = "workflow|%s" % (related_search_type)
        trigger.set_value("event", event)

        # update the trigger information
        trigger.set_value("class_name", "pyasm.command.ProcessStatusTrigger")

        # description
        trigger.set_value("description", "Listener for [%s] from [%s]" % (process, search_type))
        trigger.set_value("mode", "same process,same transaction")
        trigger.set_value("process", related_process)

        data = {
                "process_code": process_sobj.get_code(),
                "pipeline_code": pipeline_code,
                "search_type": search_type,
        }
        trigger.set_json_value("data", data)

        trigger.commit()
        trigger_code = trigger.get_code()

        workflow['trigger_code'] = trigger_code


        process_sobj.set_json_value("workflow", workflow)
        process_sobj.commit()






class PipelineEditorWdg(BaseRefreshWdg):
    '''This is the pipeline on its own, with various buttons and interface
    to help in building the pipelines.  It contains the PipelineCanvasWdg'''

    def get_display(self):
        top = self.top
        self.set_as_panel(top)
        top.add_class("spt_pipeline_editor_top")

        self.save_new_event = self.kwargs.get("save_new_event")
        self.show_gear = self.kwargs.get("show_gear")

        inner = DivWdg()
        top.add(inner)


        inner.add(self.get_shelf_wdg() )


        self.width = self.kwargs.get("width")
        if not self.width:
            #self.width = "1300"
            self.width = "auto"
        self.height = self.kwargs.get("height")
        if not self.height:
            self.height = 600


        
        canvas_top = DivWdg()
        inner.add(canvas_top)
        canvas_top.add_class("spt_pipeline_wrapper")
        canvas_top.add_style("position: relative")
        canvas_top.add_color("background", "background", -2)
        canvas = self.get_canvas()
        self.unique_id = canvas.get_unique_id()
        canvas_top.add(canvas)



        div = DivWdg()
        inner.add(div)

        pipeline_str = self.kwargs.get("pipeline")
        if pipeline_str:
            pipelines = pipeline_str.split("|")

            div.add_behavior( {
            'type': 'load',
            'pipelines': pipelines,
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_pipeline_tool_top");
            var wrapper = top.getElement(".spt_pipeline_wrapper");
            spt.pipeline.init_cbk(wrapper);

            for (var i=0; i<bvr.pipelines.length; i++) {
                spt.pipeline.import_pipeline(bvr.pipelines[i]);
            }
            '''
            } )



        # open connection dialog everytime a connection is made
        event_name = "%s|node_create" % self.unique_id

        # Note this goes through every node, every time?
        div.add_behavior( {
        'type': 'listen',
        'event_name': event_name,
        'cbjs_action': '''
        var pipeline_code = spt.pipeline.get_current_group();
        var node = bvr.firing_element;
        var node_name = node.getAttribute("spt_element_name");

        var data = {
            process: node_name,
            pipeline_code: pipeline_code
        }
        var server = TacticServerStub.get();
        server.get_unique_sobject( "config/process", data );

        // save the pipeline when a new node is added
        spt.named_events.fire_event('pipeline|save_button', bvr );

        node.click();
        '''
        } )


        # open connection dialog everytime a connection is made
        event_name = "%s|node_rename" % self.unique_id

        # Note this goes through every node, every time?
        div.add_behavior( {
        'type': 'listen',
        'event_name': event_name,
        'cbjs_action': '''
        var node = bvr.firing_element;
        var data = bvr.firing_data;

        var old_name = data.old_name;
        var name = data.name;

        var server = TacticServerStub.get();

        // rename the process on the server
        var group_name = spt.pipeline.get_current_group();
        var process = server.eval("@SOBJECT(config/process['process','"+old_name+"']['pipeline_code','"+group_name+"'])", {single: true});

        if (process) {
            server.update(process, {process: name});
        }

        // select the node
        node.click();

        spt.named_events.fire_event('pipeline|change', {});
        '''
        } )
 

        # open connection dialog everytime a connection is made
        event_name = "%s|unselect_all" % self.unique_id
        div.add_behavior( {
        'type': 'listen',
        'event_name': event_name,
        'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_pipeline_tool_top");
            var info = top.getElement(".spt_pipeline_tool_info");
            if (info) {
                var group_name = spt.pipeline.get_current_group();

                var class_name = 'tactic.ui.tools.PipelineInfoWdg';
                var kwargs = {
                    pipeline_code: group_name,
                }

                spt.panel.load(info, class_name, kwargs);
            }



        ''' } )

 


        if self.kwargs.get("is_refresh") == 'true':
            return inner
        else:
            return top


    def get_shelf_wdg(self):
 
        shelf_wdg = DivWdg()
        shelf_wdg.add_style("padding: 5px")
        shelf_wdg.add_style("margin-bottom: 5px")
        shelf_wdg.add_style("overflow-x: hidden")
        shelf_wdg.add_style("min-width: 400px")

        show_shelf = self.kwargs.get("show_shelf")
        show_shelf = True
        if show_shelf in ['false', False]:
            show_shelf = False
        else:
            show_shelf = True
        if not show_shelf:
            shelf_wdg.add_style("display: none")


        spacing_divs = []
        for i in range(0, 3):
            spacing_div = DivWdg()
            spacing_divs.append(spacing_div)
            spacing_div.add_style("height: 32px")
            spacing_div.add_style("width: 2px")
            spacing_div.add_style("margin: 0 10 0 20")
            spacing_div.add_style("border-style: solid")
            spacing_div.add_style("border-width: 0 0 0 1")
            spacing_div.add_style("border-color: %s" % spacing_div.get_color("border"))
            spacing_div.add_style("float: left")


        show_gear = self.kwargs.get("show_gear")
        button_div = self.get_buttons_wdg(show_gear);
        button_div.add_style("float: left")
        shelf_wdg.add(button_div)

        shelf_wdg.add(spacing_divs[0])

        #group_div = self.get_pipeline_select_wdg();
        #group_div.add_style("float: left")
        #group_div.add_style("margin-top: 1px")
        #group_div.add_style("margin-left: 10px")
        #shelf_wdg.add(group_div)
        #shelf_wdg.add(spacing_divs[1])

        button_div = self.get_zoom_buttons_wdg();
        button_div.add_style("margin-left: 10px")
        button_div.add_style("margin-right: 15px")
        button_div.add_style("float: left")
        shelf_wdg.add(button_div)

        # Show schema for reference.  This does not work very well.
        # Disabling
        """
        shelf_wdg.add(spacing_divs[2])

        button_div = self.get_schema_buttons_wdg();
        button_div.add_style("margin-left: 10px")
        button_div.add_style("float: left")
        shelf_wdg.add(button_div)
        """

        if self.kwargs.get("show_help") not in ['false', False]:
            help_button = ActionButtonWdg(title="?", tip="Show Workflow Editor Help", size='s')
            shelf_wdg.add(help_button)
            help_button.add_style("padding-top: 3px")
            help_button.add_behavior( {
                'type': 'click_up',
                'cbjs_action': '''
                spt.help.set_top();
                spt.help.load_alias("project-workflow|project-workflow-introduction|pipeline-process-options");
                '''
            } )



        return shelf_wdg


    def get_canvas(self):
        is_editable = self.kwargs.get("is_editable")
        canvas = PipelineToolCanvasWdg(height=self.height, width=self.width, is_editable=is_editable)
        return canvas



    def get_buttons_wdg(self, show_gear):
        from pyasm.widget import IconWdg
        from tactic.ui.widget.button_new_wdg import ButtonNewWdg, ButtonRowWdg

        button_row = ButtonRowWdg(show_title=True)

        project_code = Project.get_project_code()


        button = ButtonNewWdg(title="Save Current Workflow", icon="BS_SAVE")
        button_row.add(button)

        button.add_behavior( {
        'type': 'click',
        'cbjs_action': '''
        spt.named_events.fire_event('pipeline|save_button', bvr );
        '''
        } )


        button.add_behavior( {
        'type': 'listen',
        'event_name': 'pipeline|save_button',
        'project_code': project_code,
        'save_event': self.save_new_event,
        'cbjs_action': '''
        var editor_top = bvr.src_el.getParent(".spt_pipeline_editor_top");
        editor_top.removeClass("spt_has_changes");
        var wrapper = editor_top.getElement(".spt_pipeline_wrapper");
        spt.pipeline.init_cbk(wrapper);

        var group_name = spt.pipeline.get_current_group();
        if (group_name == 'default') {
            var xml = spt.pipeline.export_group(group_name);

            var class_name = 'tactic.ui.panel.EditWdg';

            var kwargs = {
                search_type: 'sthpw/pipeline',
                view: 'insert',
                show_header: false,
                single: true,
                'default': {
                    pipeline: xml
                },
                save_event: bvr.save_event
            }
            spt.api.load_popup("Add New Workflow", class_name, kwargs);
        }
        else {
            var data = spt.pipeline.get_data();
            var color = data.colors[group_name];

            server = TacticServerStub.get();
            spt.app_busy.show("Saving project-specific pipeline ["+group_name+"]",null);
            
            var xml = spt.pipeline.export_group(group_name);
            var search_key = server.build_search_key("sthpw/pipeline", group_name);
            try {
                var args = {search_key: search_key, pipeline:xml, color:color, project_code: bvr.project_code};
                server.execute_cmd('tactic.ui.tools.PipelineSaveCbk', args);
            } catch(e) {
                spt.alert(spt.exception.handler(e));
            }

            spt.named_events.fire_event('pipeline|save', {});
        } 


        spt.app_busy.hide();

        '''
        } )
 
        icon = button.get_icon_wdg()    
        # makes it glow
        glow_action = ''' 
        bvr.src_el.setStyles( {
            'outline': 'none', 
            'border-color': '#CF7e1B', 
            'box-shadow': '0 0 20px #CF7e1b',
            'border-radius': '20px',
        });
        '''

        icon.add_named_listener('pipeline|change', glow_action)

        unglow_action = ''' 
        bvr.src_el.setStyle('box-shadow', '0 0 0 #fff');
        '''

        icon.add_named_listener('pipeline|save', unglow_action)



        button.set_show_arrow_menu(True)
        menu = Menu(width=200)
        

        menu_item = MenuItem(type='action', label='Save as Site Wide Workflow')
        menu.add(menu_item)
        # no project code here
        menu_item.add_behavior( {
            'cbjs_action': '''

            spt.alert('This feature is disabled. Saving project-specific Workflow using the disk button is preferred.');


        /*
        var act = spt.smenu.get_activator(bvr);
        
        

        var editor_top = act.getParent(".spt_pipeline_editor_top");
        
        editor_top.removeClass("spt_has_changes");
        var wrapper = editor_top.getElement(".spt_pipeline_wrapper");

        spt.pipeline.init_cbk(wrapper);

        var group_name = spt.pipeline.get_current_group();
        if (group_name == 'default') {
            var xml = spt.pipeline.export_group(group_name);

           var class_name = 'tactic.ui.panel.EditWdg';
            var kwargs = {
                search_type: 'sthpw/pipeline',
                view: 'insert',
                show_header: false,
                single: true,
                default: {
                    pipeline: xml
                }
            }
            spt.api.load_popup("Add New Workflow", class_name, kwargs);
        }
        else {
            var data = spt.pipeline.get_data();
            var color = data.colors[group_name];

            server = TacticServerStub.get();
            spt.app_busy.show("Saving pipeline ["+group_name+"]",null);
            
            var xml = spt.pipeline.export_group(group_name);
            var search_key = server.build_search_key("sthpw/pipeline", group_name);
            try {
                var args = {search_key: search_key, pipeline:xml, color:color, project_code: '__SITE_WIDE__'};
                server.execute_cmd('tactic.ui.tools.PipelineSaveCbk', args);
            } catch(e) {
                spt.alert(spt.exception.handler(e));
            }
            spt.named_events.fire_event('pipeline|save', {});
        } 
        spt.app_busy.hide();
        */
        '''
        } )

        menu_item = MenuItem(type='action', label='Save All Workflows')
        menu.add(menu_item)
        # no project code here
        menu_item.add_behavior( {
            'cbjs_action': '''

            var cancel = null;
            var ok = function() {
            var act = spt.smenu.get_activator(bvr);
            
            var editor_top = bvr.src_el.getParent(".spt_pipeline_editor_top");
            editor_top.removeClass("spt_has_changes");
            var wrapper = editor_top.getElement(".spt_pipeline_wrapper");
            
            spt.pipeline.init_cbk(wrapper);

            server = TacticServerStub.get();
            var groups = spt.pipeline.get_groups();
            
            for (group_name in groups) {
                var data = spt.pipeline.get_data();
                var color = data.colors[group_name];

                server = TacticServerStub.get();
                spt.app_busy.show("Saving All Workflows ["+group_name+"]",null);
                var xml = spt.pipeline.export_group(group_name);
                var search_key = server.build_search_key("sthpw/pipeline", group_name);
                try {
                    var args = {search_key: search_key, pipeline:xml, color:color};
                    server.execute_cmd('tactic.ui.tools.PipelineSaveCbk', args);
                } catch(e) {
                    spt.alert(spt.exception.handler(e));
                }
            }
            spt.app_busy.hide();
            }
            spt.confirm("Saving all workflows does not make new workflows project specific. Continue?", ok, cancel );
        '''
        } )

        menus = [menu.get_data()]
        SmartMenu.add_smart_menu_set( button.get_arrow_wdg(), { 'DG_BUTTON_CTX': menus } )
        SmartMenu.assign_as_local_activator( button.get_arrow_wdg(), "DG_BUTTON_CTX", True )
 



        button = ButtonNewWdg(title="Add Process", icon="BS_PLUS")
        button_row.add(button)

        button.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        // Add edited flag
        var editor_top = bvr.src_el.getParent(".spt_pipeline_editor_top");
        editor_top.addClass("spt_has_changes");
        
        var wrapper = editor_top.getElement(".spt_pipeline_wrapper");
        spt.pipeline.init_cbk(wrapper);
        spt.pipeline.add_node();

        '''
        } )



        button.set_show_arrow_menu(True)
        menu = Menu(width=200)


        menu_item = MenuItem(type='action', label='Add Action')
        menu.add(menu_item)
        menu_item.add_behavior( {
            'cbjs_action': '''
            var act = spt.smenu.get_activator(bvr);
            var top = act.getParent(".spt_pipeline_editor_top");
            var wrapper = top.getElement(".spt_pipeline_wrapper");
            spt.pipeline.init_cbk(wrapper);
            spt.pipeline.add_node(null, null, null, {node_type: 'action'});

            top.addClass("spt_has_changes");
            '''
        } )

        menu_item = MenuItem(type='action', label='Add Condition')
        menu.add(menu_item)
        menu_item.add_behavior( {
            'cbjs_action': '''
            var act = spt.smenu.get_activator(bvr);
            var top = act.getParent(".spt_pipeline_editor_top");
            var wrapper = top.getElement(".spt_pipeline_wrapper");
            spt.pipeline.init_cbk(wrapper);
            spt.pipeline.add_node(null, null, null, {node_type: 'condition'});

            top.addClass("spt_has_changes");
            '''
        } )


        menu_item = MenuItem(type='action', label='Add Approval')
        menu.add(menu_item)
        menu_item.add_behavior( {
            'cbjs_action': '''
            var act = spt.smenu.get_activator(bvr);
            var top = act.getParent(".spt_pipeline_editor_top");
            var wrapper = top.getElement(".spt_pipeline_wrapper");
            spt.pipeline.init_cbk(wrapper);
            spt.pipeline.add_node(null, null, null, {node_type: 'approval'});

            top.addClass("spt_has_changes");
            '''
        } )



        menu_item = MenuItem(type='action', label='Add Sub-workflow')
        menu.add(menu_item)
        menu_item.add_behavior( {
            'cbjs_action': '''
            var act = spt.smenu.get_activator(bvr);
            var top = act.getParent(".spt_pipeline_editor_top");
            var wrapper = top.getElement(".spt_pipeline_wrapper");
            spt.pipeline.init_cbk(wrapper);
            spt.pipeline.add_node(null, null, null, {node_type: 'hierarchy'});

            top.addClass("spt_has_changes");
            '''
        } )
 
 
 
        menu_item = MenuItem(type='separator')
        menu.add(menu_item)

        expr = "@GET(sthpw/pipeline['code','like','%/__TEMPLATE__'].config/process.process)"
        processes = Search.eval(expr)
        processes.sort()



        #processes = [x.get("process") for x in process_sobjs]
        for process in processes:
            menu_item = MenuItem(type='action', label='Add "%s"' % process)
            menu.add(menu_item)
            menu_item.add_behavior( {
            'process': process,
            'cbjs_action': '''
            var act = spt.smenu.get_activator(bvr);
            // Add edited flag
            var editor_top = act.getParent(".spt_pipeline_editor_top");
            editor_top.addClass("spt_has_changes");
            
            var wrapper = editor_top.getElement(".spt_pipeline_wrapper");
            spt.pipeline.init_cbk(wrapper);

            var process = bvr.process;
            spt.pipeline.add_node(process);

            top.addClass("spt_has_changes");
     

            '''
            } )

        menus = [menu.get_data()]
        SmartMenu.add_smart_menu_set( button.get_arrow_wdg(), { 'DG_BUTTON_CTX': menus } )
        SmartMenu.assign_as_local_activator( button.get_arrow_wdg(), "DG_BUTTON_CTX", True )
 

 
        button = ButtonNewWdg(title="Show Notifications", icon="BS_ENVELOPE")
        button_row.add(button)

        button.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        var editor_top = bvr.src_el.getParent(".spt_pipeline_editor_top");

        spt.pipeline.load_triggers();

        editor_top.addClass("spt_has_changes");
        '''
        } )






        button = ButtonNewWdg(title="Delete Selected", icon="BS_TRASH")
        button_row.add(button)

        button.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        // Add edited flag
        var editor_top = bvr.src_el.getParent(".spt_pipeline_editor_top");
        editor_top.addClass("spt_has_changes");
            
        var wrapper = editor_top.getElement(".spt_pipeline_wrapper");
        spt.pipeline.init_cbk(wrapper);


        var nodes = spt.pipeline.get_selected_nodes();
        
        spt.pipeline.remove_nodes(nodes);
        
        // this targets connectors only
        spt.pipeline.delete_selected();
      
        '''
        } )



        if show_gear not in ['false', False]:
            button = ButtonNewWdg(title="Extra View", icon="G_SETTINGS_GRAY", show_arrow=True)
            button_row.add(button)

            menu = Menu(width=200)
            
            menu_item = MenuItem(type='action', label='TEST')
            menu.add(menu_item)
            # no project code here
            menu_item.add_behavior( {
                'cbjs_action': '''
                alert("test");
                '''
            } )


            tab = PipelineTabWdg()
            menu = tab.get_extra_tab_menu()

            menus = [menu.get_data()]
            SmartMenu.add_smart_menu_set( button.get_button_wdg(), { 'DG_BUTTON_CTX': menus } )
            SmartMenu.assign_as_local_activator( button.get_button_wdg(), "DG_BUTTON_CTX", True )
 






        return button_row


    def get_zoom_buttons_wdg(self):
        from pyasm.widget import IconWdg
        from tactic.ui.widget.button_new_wdg import ButtonNewWdg, ButtonRowWdg, IconButtonWdg, SingleButtonWdg

        button_row = DivWdg()
        #button_row.add_border()
        #button_row.set_round_corners(5)
        button_row.add_style("padding: 3px 10px 3px 5px")
        button_row.add_style("padding: 6px 10px 0px 5px")

        button = SingleButtonWdg(title="Zoom In", icon="BS_ZOOM_IN", show_out=False)
        button_row.add(button)
        button.add_style("float: left")
        button.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        var top = bvr.src_el.getParent(".spt_pipeline_editor_top");
        var wrapper = top.getElement(".spt_pipeline_wrapper");
        spt.pipeline.init_cbk(wrapper);

        var scale = spt.pipeline.get_scale();
        scale = scale * 1.05;
        spt.pipeline.set_scale(scale);
        '''
        } )



        button = SingleButtonWdg(title="Zoom Out", icon="BS_ZOOM_OUT", show_out=False)
        button_row.add(button)
        button.add_style("float: left")

        button.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        var top = bvr.src_el.getParent(".spt_pipeline_editor_top");
        var wrapper = top.getElement(".spt_pipeline_wrapper");
        spt.pipeline.init_cbk(wrapper);

        var scale = spt.pipeline.get_scale();
        scale = scale / 1.05;
        spt.pipeline.set_scale(scale);
        '''
        } )

        select = SelectWdg("zoom")
        select.add_style("width: 85px")
        select.add_style("margin-top: -3px")
        select.set_option("labels", ["10%", "25%", "50%", "75%", "100%", "125%", "150%", "----", "Fit to Current Group", "Fit To Canvas"])
        select.set_option("values", ["0.1", "0.25", "0.50", "0.75", "1.0", "1.25", "1.5", "", "fit_to_current", "fit_to_canvas"])
        select.add_empty_option("Zoom")
        button_row.add(select)
        #select.set_value("1.0")
        select.add_behavior( {
        'type': 'change',
        'cbjs_action': '''
        var top = bvr.src_el.getParent(".spt_pipeline_editor_top");
        var wrapper = top.getElement(".spt_pipeline_wrapper");
        spt.pipeline.init_cbk(wrapper);

        var value = bvr.src_el.value;
        if (value == '') {
            return;
        }
        else if (value == 'fit_to_canvas') {
            spt.pipeline.fit_to_canvas();
        }
        else if (value == 'fit_to_current') {
            var group_name = spt.pipeline.get_current_group();
            spt.pipeline.fit_to_canvas(group_name);
        }
        else {
            var scale = parseFloat(value);
            spt.pipeline.set_scale(scale);
        }
        bvr.src_el.value = '';
        '''
        } )

        return button_row



    def get_schema_buttons_wdg(self):
        from pyasm.widget import IconWdg
        from tactic.ui.widget.button_new_wdg import ButtonNewWdg, ButtonRowWdg, SingleButtonWdg

        button_row = DivWdg()
        button_row.add_style("padding-top: 5px")

        project_code = Project.get_project_code()

        button = SingleButtonWdg(title="Show Schema for Reference", icon=IconWdg.DEPENDENCY)
        button_row.add(button)
        button.add_style("float: left")
        button.add_behavior( {
        'type': 'click_up',
        'project_code': project_code,
        'cbjs_action': '''
        var top = bvr.src_el.getParent(".spt_pipeline_editor_top");
        var schema_editor = top.getElement(".spt_schema_wrapper");
        spt.pipeline.init_cbk(schema_editor);
        spt.toggle_show_hide(schema_editor);

        var group = spt.pipeline.get_group(bvr.project_code);
        if (group != null) {
            return;
        }

        spt.pipeline.import_schema( bvr.project_code );
        '''
        } )

        return button_row





    def get_pipeline_select_wdg(self):
        div = DivWdg()
        div.add_style("padding: 3px")

        pipeline_select = SelectWdg("current_pipeline")
        #div.add(pipeline_select)
        pipeline_select.add_style("display: table-cell")
        pipeline_select.add_class("spt_pipeline_editor_current")
        pipeline_select.set_option("values", "default")
        pipeline_select.set_option("labels", "-- New Workflow --")

        pipeline_select.add_behavior( {
            'type': 'change',
            'cbjs_action': '''
            // Add edited flag
            var editor_top = bvr.src_el.getParent(".spt_pipeline_editor_top");
            editor_top.addClass("spt_has_changes");
            
            var wrapper = editor_top.getElement(".spt_pipeline_wrapper");
 
            spt.pipeline.init_cbk(wrapper);

            var group_name = bvr.src_el.value;
            spt.pipeline.set_current_group(group_name);
            '''
        } )


        return div





class TriggerListWdg(BaseRefreshWdg):

    ARGS_KEYS = {
    'process': "The process in the pipeline that is to be displayed"
    }

    def get_display(self):
        top = DivWdg()
        top.add_class("spt_tiggers_top")

        title = DivWdg()
        title.add_class("maq_search_bar")
        title.add("Triggers")
        top.add(title)
        top.add("<br/>")


        #top.add( triggers_wdg )
        from pyasm.widget import IconButtonWdg, IconWdg
        save_button = IconButtonWdg("Add Trigger", IconWdg.ADD, True)
        top.add(save_button)
        save_button = IconButtonWdg("Save All Triggers", IconWdg.SAVE, True)
        save_button.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_tiggers_top");
            var triggers = top.getElements(".spt_triggers");
            for ( var j=0; j<triggers.length; j++) {
                var elements = triggers[j].getElements(".spt_list_item");
                var data = [];
                for (var i=0; i<elements.length; i++) {
                    var values = spt.api.get_input_values(elements[i],null,false);
                    data.push(values)
                }
                var server = TacticServerStub.get();
                var class_name = "pyasm.admin.creator.PipelineTaskTriggerCommitCbk";
                server.execute_cmd(class_name, {data: data} );
            }
            '''
        } )
 

        top.add(save_button)
        top.add("<hr/>")

        from tactic.ui.filter import FilterData
        from tactic.ui.container import DynamicListWdg
        list_wdg = DynamicListWdg()
        triggers_wdg = self.get_triggers_wdg( None, FilterData() )
        list_wdg.add_template(triggers_wdg)

        search = Search("config/trigger")
        triggers = search.get_sobjects()

        top.add("Items Found: %s" % len(triggers) )

        for trigger in triggers:
            data = trigger.get_value("data")
            filter_data = FilterData(data)

            triggers_wdg = self.get_triggers_wdg(trigger, filter_data)
            div = DivWdg()
            div.add(triggers_wdg)
            div.add_style("padding: 10px")
            list_wdg.add_item(div)

        top.add(list_wdg)

        return top


    def get_triggers_wdg(self, trigger, filter_data=None):
        div = DivWdg()
        div.add_class("spt_triggers")

        trigger_info = filter_data.get_values_by_index("trigger")
        self.process_name = trigger_info.get("process")
        if not self.process_name:
            self.process_name = self.kwargs.get("process")
        if not self.process_name:
            div.add("No process selected")
            return div



        title = DivWdg()
        title.add_class("maq_search_bar")
        title.add(" ")
        div.add(title)


        content_div = DivWdg()
        content_div.add_color("color", "color3")
        content_div.add_color("background", "background3")
        content_div.add_style("padding: 3px")

        trigger_div = DivWdg()
        content_div.add(trigger_div)

        trigger_div.add_class("spt_list_item")
        trigger_div.add( HiddenWdg("prefix", "trigger") )
        trigger_div.add( HiddenWdg("process", self.process_name) )


        from pyasm.widget import IconButtonWdg, IconWdg
        save_button = IconButtonWdg("Save this Trigger", IconWdg.SAVE)
        save_button.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_triggers")
            var elements = top.getElements(".spt_list_item");
            var data = [];
            for (var i=0; i<elements.length; i++) {
                var values = spt.api.get_input_values(elements[i],null,false);
                data.push(values)
            }
            var server = TacticServerStub.get();
            var class_name = "pyasm.admin.creator.PipelineTaskTriggerCommitCbk";
            server.execute_cmd(class_name, {data: data} );
            '''
        } )
        save_button.add_style("float: right")
        trigger_div.add(save_button)




        name_text = TextWdg("code")
        name_text.set_option("read_only", "true")
        if trigger:
            code = trigger.get_value("code")
            name_text.set_value(code)
            trigger_div.add("Trigger Code: ")
            trigger_div.add(name_text)
            trigger_div.add("(autogenerated)")
        else:
            new_icon = IconWdg("New Trigger", IconWdg.NEW)
            trigger_div.add(new_icon)
            trigger_div.add("New Trigger")

        title = DivWdg("When these events occur:<br/>")
        title.add_style("margin-top: 10px")
        title.add_style("margin-bottom: 10px")
        content_div.add(title)

        div.add(content_div)

        from tactic.ui.container import DynamicListWdg
        list_div = DivWdg()
        list_div.add_style("margin-left: 10px")
        list_wdg = DynamicListWdg()
        list_div.add(list_wdg)
        content_div.add(list_div)

        template_item_div = DivWdg()
        template_item_div.add( HiddenWdg("prefix", "rule") )
        type_select = SelectWdg("type")
        type_select.set_option("values", "attribute")
        type_select.set_option("labels", "Attribute")
        template_item_div.add(type_select)
        template_item_div.add(TextWdg("name") )
        template_item_div.add(" is " )
        template_item_div.add(TextWdg("value") )

        list_wdg.add_template(template_item_div)

        # rules
        rules_data = filter_data.get_values_by_prefix("rule")
        actions_data = filter_data.get_values_by_prefix("action")

        # add some empty rules if none exist
        if not rules_data:
            rules_data = [{}]
        if not actions_data:
            actions_data = [{}]


        # go through each rule
        for rule_data in rules_data:
            name = rule_data.get("name")
            value = rule_data.get("value")

            item_div = DivWdg()
            item_div.add( HiddenWdg("prefix", "rule") )
            type_select = SelectWdg("type")
            type_select.set_option("values", "attribute")
            type_select.set_option("labels", "Attribute")
            item_div.add(type_select)
            name_text = TextWdg("name")
            if name:
                name_text.set_value(name)
            item_div.add(name_text)
            item_div.add(" is " )

            value_text = TextWdg("value")
            if value:
                value_text.set_value(value)
            item_div.add(value_text)

            list_wdg.add_item(item_div)


        # actions
        title = DivWdg("Perform these actions:")
        title.add_style("margin-top: 10px")
        title.add_style("margin-bottom: 10px")
        content_div.add(title)

        template_item_div = DivWdg()
        template_item_div.add( HiddenWdg("prefix", "action") )
        type_select = SelectWdg("type")
        type_select.set_option("values", "output|input|expression")
        type_select.set_option("labels", "Set Outputs|Set Inputs|Expression")
        type_select.set_empty_option("-- Select --")
        template_item_div.add(type_select)
        template_item_div.add(TextWdg("name") )
        template_item_div.add(" to ")
        template_item_div.add(TextWdg("value") )


        list_div = DivWdg()
        list_div.add_style("margin-left: 10px")
        list_wdg = DynamicListWdg()
        list_div.add(list_wdg)
        content_div.add(list_div)

        list_wdg.add_template(template_item_div)

        for action_data in actions_data:
            name = action_data.get("name")
            value = action_data.get("value")

            item_div = DivWdg()
            item_div.add( HiddenWdg("prefix", "action") )
            type_select = SelectWdg("type")
            type_select.set_option("values", "output|input|expression")
            type_select.set_option("labels", "Set Outputs|Set Inputs|Expression")
            item_div.add(type_select)

            name_text = TextWdg("name")
            if name:
                name_text.set_value(name)
            item_div.add(name_text)
            item_div.add(" to " )

            value_text = TextWdg("value")
            if value:
                value_text.set_value(value)
            item_div.add(value_text)

            list_wdg.add_item(item_div)

 

        return div



class PipelineTaskTriggerCommitCbk(Command):
    
    def execute(self):

        data_str = self.kwargs.get("data")
        if not data_str:
            print("No data supplied")
            return
        if isinstance(data_str, basestring):
            data = jsonloads(data_str)
        else:   
            data = data_str

        from tactic.ui.filter import FilterData
        filter_data = FilterData(data)
        values = filter_data.get_values_by_index("trigger")

        code = values.get("code")
        trigger = None
        if code:
            search = Search("config/trigger")
            search.add_filter("code", code)
            trigger = search.get_sobject()

        if not trigger:
            trigger = SearchType.create("config/trigger")
            trigger.set_value("event", "update|sthpw/task|status")
            trigger.set_value("class_name", "tactic.command.PipelineTaskTrigger")
            trigger.set_value("description", "Status change trigger defined by workflow")

            trigger.set_value("mode", "same process,same transaction")

        trigger.set_value("data", jsondumps(data_str) )
        trigger.commit()







class PipelinePropertyWdg(BaseRefreshWdg):

    def get_display(self):
        div = DivWdg()
        div.add_class("spt_pipeline_properties_top")
        div.add_style("min-width: 500px")

        process = self.kwargs.get("process")
        pipeline_code = self.kwargs.get("pipeline_code")


        from tactic.ui.app import HelpButtonWdg
        help_button = HelpButtonWdg(alias='pipeline-process-options|project-workflow-introduction')
        div.add( help_button )
        help_button.add_style("margin-top: 7px")
        help_button.add_style("float: right")



        pipeline = Pipeline.get_by_code(pipeline_code)
        if not pipeline:
            attrs = {}
        else:
            attrs = pipeline.get_process_attrs(process)

        web = WebContainer.get_web()

        div.add_color('background', 'background')

        #div.set_id("properties_editor")
        #div.add_style("display", "none")


        node_type = attrs.get("type")


        title_div = DivWdg()
        div.add(title_div)
        title_div.add_style("height: 20px")
        title_div.add_color("background", "background", -13)
        title_div.add_class("spt_property_title")
        if not process:
            title_div.add("Process: <i>--None--</i>")
        else:
            title_div.add("Process: %s" % process)
        title_div.add_style("font-weight: bold")
        title_div.add_style("margin-bottom: 5px")
        title_div.add_style("padding: 5px")


        # add a no process message
        no_process_wdg = DivWdg()
        no_process_wdg.add_class("spt_pipeline_properties_no_process")
        div.add(no_process_wdg)
        no_process_wdg.add( "No process node or connector selected")
        no_process_wdg.add_style("padding: 30px")



        # get a list of known properties
        if node_type == "approval":
            properties = ['group', "completion", 'task_pipeline', 'assigned_login_group', 'duration', 'bid_duration', 'color']
        else:
            properties = ['group', "completion", "task_pipeline", 'assigned_login_group', 'supervisor_login_group', 'duration', 'bid_duration', 'color']


        # show other properties
        content = DivWdg()
        div.add(content)
        content.add_style("padding: 20px")

        table = Table()
        content.add(table)


        table.add_class("spt_pipeline_properties_content")
        table.add_color('color', 'color')
        table.add_style("width: 100%")
        table.add_row()
        #table.add_header("Property")
        #table.add_header("Value")


        if process:
            no_process_wdg.add_style("display: none")
        else:
            table.add_style("display: none")



        table.add_behavior( {
        'type': 'load',
        'cbjs_action': self.get_onload_js()
        } )

        
        # group
        # Making invisible to ensure that it still gets recorded if there.
        tr = table.add_row()
        tr.add_style("display: none")
        td = table.add_cell('Group: ')
        td.add_style("width: 250px")
        td.add_attr("title", "Nodes can grouped together within a workflow")
        #td.add_style("width: 200px")
        text_name = "spt_property_group"
        text = TextWdg(text_name)
        text.add_class(text_name)

        if "completion" in properties:
            th = table.add_cell(text)
            th.add_style("height: 30px")
            
            # completion (visibility depends on sType)
            table.add_row(css='spt_property_status_completion')
            td = table.add_cell('Completion (0 to 100):')
            td.add_attr("title", "Determines the completion level that this node represents.")

            text_name = "spt_property_completion"
            text = TextInputWdg(name=text_name, type="number")
            text.add_class(text_name)

            th = table.add_cell(text)
            th.add_style("height: 30px")


        if "task_pipeline" in properties: 
            # These searchs are needed for the task_pipeline select widget
            task_pipeline_search = Search('sthpw/pipeline')
            task_pipeline_search.add_filter('search_type', 'sthpw/task')
            task_pipeline_search.add_project_filter()
            task_pipelines = task_pipeline_search.get_sobjects()
            
            normal_pipeline_search = Search('sthpw/pipeline')
            normal_pipeline_search.add_filter('search_type', 'sthpw/task', '!=')
            normal_pipelines = normal_pipeline_search.get_sobjects()
           

            # task_pipeline  (visibility depends on sType)
            table.add_row(css='spt_property_task_status_pipeline')
            td = table.add_cell('Task Status Workflow')
            td.add_attr("title", "The task status workflow determines all of the statuses that occur within this process")

            text_name = "spt_property_task_pipeline"
            select = SelectWdg(text_name)

            
            for pipeline in task_pipelines:
                label = '%s (%s)' %(pipeline.get_value('name'), pipeline.get_value('code'))
                select.append_option(label, pipeline.get_value('code'))
            
            select.add_empty_option('-- Select --')
            select.add_class(text_name)

            th = table.add_cell(select)
            th.add_style("height: 40px")

           

        # The search needed for the login_group select widgets
        login_group_search = Search('sthpw/login_group')
        
        # assigned_login_group
        table.add_row()
        td = table.add_cell('Assigned Group:')
        td.add_attr("title", "Used for limiting the users displayed when this process is chosen in a task view.")

        text_name = "spt_property_assigned_login_group"
        select = SelectWdg(text_name)
        select.set_search_for_options(login_group_search, 'login_group', 'login_group')
        select.add_empty_option('-- Select --')
        select.add_class(text_name)

        th = table.add_cell(select)
        th.add_style("height: 40px")
       
        if "supervisor_login_group" in properties:
            # supervisor_login_group
            table.add_row()
            td = table.add_cell('Supervisor Group:')
            td.add_attr("title", "Used for limiting the supervisors displayed when this process is chosen in a task view.")
            text_name = "spt_property_supervisor_login_group"
            select = SelectWdg(text_name)
            select.set_search_for_options(login_group_search, 'login_group', 'login_group')
            select.add_empty_option('-- Select --')
            select.add_class(text_name)

            th = table.add_cell(select)
            th.add_style("height: 40px")
        
        # duration
        table.add_row()
        td = table.add_cell('Default Start to End Duration:')
        td.add_attr("title", "The default duration determines the starting duration of a task that is generated for this process")

        text_name = "spt_property_duration"
        text = TextWdg(text_name)
        text.add_style("width: 40px")
        text.add_class(text_name)
        text.add_style("text-align: center")

        th = table.add_cell(text)
        th.add_style("height: 40px")
        th.add(" days")

        # bid duration in hours
        table.add_row()
        td = table.add_cell('Expected Work Hours:')
        td.add_attr("title", "The default bid duration determines the estimated number of hours will be spent on this task.")

        text_name = "spt_property_bid_duration"
        text = TextWdg(text_name)
        text.add_style("width: 40px")
        text.add_class(text_name)
        text.add_style("text-align: center")

        th = table.add_cell(text)
        th.add_style("height: 40px")
        th.add(" hours")

        tr, td = table.add_row_cell()
        td.add("<hr/>")
        
        # Color
        table.add_row()
        td = table.add_cell('Color:')
        td.add_attr("title", "Used by various parts of the interface to show the color of this process.")

        text_name = "spt_property_color"
        text = TextWdg(text_name)
        color = ColorInputWdg(text_name)
        color.set_input(text)
        text.add_class(text_name)

        td = table.add_cell(color)
        th.add_style("height: 40px")

        # label
        table.add_row()
        td = table.add_cell('Label:')

        text_name = "spt_property_label"
        text = TextWdg(text_name)
        text.add_class(text_name)

        td = table.add_cell(text)
        td.add_style("height: 40px")

        tr, td = table.add_row_cell()

        button = ActionButtonWdg(title="Save", tip="Confirm properties change. Remember to save workflow at the end.", color="primary", width=200)
        td.add("<hr/>")
        td.add(button)
        #button.add_style("float: right")
        #button.add_style("margin-right: 20px")
        button.add_style("margin: 15px auto")
        td.add("<br clear='all'/>")
        td.add("<br clear='all'/>")
        button.add_behavior( {
        'type': 'click_up',
        'properties': properties,
        'cbjs_action': '''
        var top = bvr.src_el.getParent(".spt_pipeline_properties_top");
        var node = spt.pipeline.get_selected_node();
        if (!node) {
            alert("No node selected");
            return;
        }
        spt.pipeline_properties.set_properties2(top, node, bvr.properties);


        var top = bvr.src_el.getParent(".spt_popup");
        spt.popup.close(top);

        spt.named_events.fire_event('pipeline|change', {});

        spt.named_events.fire_event('pipeline|save_button', bvr );
        '''
        } )



        return div

    def get_onload_js(self):
        return r'''

spt.pipeline_properties = {};

// DEPRECATED
spt.pipeline_properties.set_properties = function(node) {


    if (!node) {
        // FIXME: not sure where it gets the bvr from ???
        node = bvr.src_el;
    }
    var top = node.getParent(".spt_pipeline_editor_top");
    var wrapper = top.getElement(".spt_pipeline_wrapper");
    spt.pipeline.init_cbk(wrapper);

    var prop_top = spt.get_element(top, ".spt_pipeline_properties_top");
    var connector_top = spt.get_element(top, ".spt_connector_properties_top");

    var selected_nodes = spt.pipeline.get_selected_nodes();
    var selected = spt.pipeline.get_selected();
    if (selected_nodes.length > 1) {
        spt.alert('Please select only 1 node to set property');
        return;
    }
        
    if (selected_nodes.length==1) {
        var title_el = spt.get_element(top, ".spt_property_title");
        var node_name = title_el.node_name;

        var values = spt.api.get_input_values(top, null, false);
        var group = spt.pipeline.get_current_group();
        var server = TacticServerStub.get();
        var kwargs = {
            pipeline_code: group,
            process: node_name,
            data: JSON.stringify(values)
        }
        // server.update()


        var node = spt.pipeline.get_node_by_name(node_name);
        if (node)
        {
            var properties = ['group', 'completion', 'task_pipeline', 'assigned_login_group', 'supervisor_login_group','duration', 'bid_duration','color', 'label'];

            for ( var i = 0; i < properties.length; i++ ) {
                var el = prop_top.getElement(".spt_property_" + properties[i]);
                spt.pipeline.set_node_property( node, properties[i], el.value );
            }
        }
    }
    else if (selected.length==1 && selected[0].type == 'connector') {
        var el = connector_top.getElement(".spt_connector_context");
        selected[0].set_attr('context', el.value);
        
    }
            
}



// DEPRECATED
spt.pipeline_properties.show_node_properties = function(node) {

    var top = node.getParent(".spt_pipeline_tool_top");
    var prop_top = spt.get_element(top, ".spt_pipeline_properties_top");
    var connect_top = spt.get_element(top, ".spt_connector_properties_top");

    var content = spt.get_element(prop_top, ".spt_pipeline_properties_content");
    var no_process = spt.get_element(prop_top, ".spt_pipeline_properties_no_process");
    var connector_prop = spt.get_element(connect_top, ".spt_connector_properties_content");
    spt.show(prop_top);
    spt.show(content);
    spt.hide(no_process);
    spt.hide(connector_prop);


    var node_name = spt.pipeline.get_node_name(node);
    var group = spt.pipeline.get_group_by_node(node);
    var group_name = group.get_name();

    // must set current group
    spt.pipeline.set_current_group(group_name);
    var stype = spt.pipeline.get_search_type(group_name);
    var task_pipe_tr = spt.get_element(prop_top, ".spt_property_task_status_pipeline");
    var status_completion_tr = spt.get_element(prop_top, ".spt_property_status_completion");
    if (stype && stype =='sthpw/task') { 
        spt.hide(task_pipe_tr);
        spt.show(status_completion_tr);

    }
    else {
        spt.show(task_pipe_tr);
        spt.hide(status_completion_tr);
    }

    var title = prop_top.getElement(".spt_property_title");
    title.innerHTML = "Node: " + node_name;
    title.node_name = node_name;

    var properties = ['group', 'completion', 'task_pipeline', 'assigned_login_group', 'supervisor_login_group','duration', 'bid_duration','color', 'label'];

    for ( var i = 0; i < properties.length; i++ ) {
        var el = prop_top.getElement(".spt_property_" + properties[i]);
        var value = node.properties[properties[i]];
        if (typeof(value) == 'undefined') {
            el.value = '';
        }
        else {
            el.value = node.properties[properties[i]];
            if (properties[i] == 'color')
                el.setStyle('background',el.value);
        }
    }
    // set the current pipeline
    /*
    current = top.getElement(".spt_pipeline_editor_current");
    current.value = group_name;
    */

    current = top.getElement(".spt_pipeline_editor_current2");
    //current.value = group_name;
    current.innerHTML = group_name;


}


spt.pipeline_properties.show_properties2 = function(prop_top, node) {

    var properties = ['group', 'completion', 'task_pipeline', 'assigned_login_group', 'supervisor_login_group','duration', 'bid_duration','color', 'label'];

    for ( var i = 0; i < properties.length; i++ ) {
        // get the value from the node
        var value = node.properties[properties[i]];

        // set the value on the element
        var el = prop_top.getElement(".spt_property_" + properties[i]);
        if (!el) continue;

        if (typeof(value) == 'undefined' || value == null) {
            el.value = ""
        }
        else {
            el.value = node.properties[properties[i]];
        }

        if (properties[i] == 'color') {
            el.setStyle('background',el.value);
        }
    }

}

spt.pipeline_properties.set_properties2 = function(prop_top, node, properties) {

    for ( var i = 0; i < properties.length; i++ ) {
        // get the value from the element
        var el = prop_top.getElement(".spt_property_" + properties[i]);
        var value = el.value;

        // set the value on the node
        node.properties[properties[i]] = value;
    
    }
}

        '''




class PipelineSaveCbk(Command):
    '''Callback executed when the Save button or other Save menu items are pressed in Project Workflow'''
    def get_title(self):
        return "Save a pipeline"

    def execute(self):
        pipeline_sk = self.kwargs.get('search_key')

        pipeline_xml = self.kwargs.get('pipeline')
        pipeline_color = self.kwargs.get('color')
        project_code = self.kwargs.get('project_code')

        from pyasm.common import Xml
        import json
        xml = Xml()
        xml.read_string(pipeline_xml)
        process_nodes = xml.get_nodes("pipeline/process")
        settings_list = []

        for node in process_nodes:
            settings_str = xml.get_attribute(node, "settings")

            xml.del_attribute(node, "settings")

            settings = json.loads(settings_str)
            settings_list.append(settings)


        server = TacticServerStub.get(protocol='local')
        data =  {'pipeline':pipeline_xml, 'color':pipeline_color}
        if project_code:
            # force a pipeline to become site-wide
            if project_code == '__SITE_WIDE__':
                project_code = ''
            data['project_code'] = project_code

        server.insert_update(pipeline_sk, data = data)

        Pipeline.clear_cache(search_key=pipeline_sk)
        pipeline = SearchKey.get_by_search_key(pipeline_sk)
        pipeline_code = pipeline.get_code()

        # make sure to update process table
        """
        process_names = pipeline.get_process_names()
        search = Search("config/process")
        search.add_filter("pipeline_code", pipeline_code)
        process_sobjs = search.get_sobjects()
        existing_names = SObject.get_values(process_sobjs, 'process')
        """

        pipeline.update_dependencies()
        
        self.description = "Updated workflow [%s]" % pipeline_code

        for i in range(len(process_nodes)):
            node = process_nodes[i]
            settings = settings_list[i]
            process = None
            process_code = xml.get_attribute(node, "process_code")
            process_name = xml.get_attribute(node, "name")
            if process_code:
                process = Search.get_by_code("config/process", process_code)
            
            if not process:
                process = SearchType.create("config/process")
                process.set_value("process", process_name)
                process.set_value("pipeline_code", pipeline_code)
            
            process.set_value("workflow", settings)
            subpipeline_code = settings.get("subpipeline_code")
            if subpipeline_code:
                process.set_value("subpipeline_code", subpipeline_code)
            process.commit()

            xml.set_attribute(node, "process_code", process.get_code())

        


class ProcessCopyCmd(Command):
    '''Deep process copy'''

    def execute(self):

        pipeline_code = self.kwargs.get("pipeline_code")
        process = self.kwargs.get("process")


        search = Search("config/process")
        search.add_filter("pipeline_code", pipeline_code)
        search.add_filter("process", process)
        process_sobj = search.get_sobject()

        process_code = process_sobj.get_value("code")


        # copy the process
        from tactic.command import SObjectCopyCmd
        copy_cmd = SObjectCopyCmd(sobject=process_sobj)
        copy_cmd.execute()

        new_process_sobj = SearchType.create("config/process")
        data = process_sobj.get_data()
        for name, value in data.items():
            pass


        # copy the notifications
        search = Search("config/notification")
        notifications = search.get_sobjects()


        # copy the triggers
        search = Search("config/trigger")
        search.add_filter("process", process_code)
        triggers = search.get_sobjects()

        for trigger in triggers:
            pass



        # copy custom scripts




class PipelineCopyCmd(Command):

    def execute(self):
        pass


