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

__all__ = ['PipelineToolWdg', 'PipelineToolCanvasWdg', 'PipelineEditorWdg', 'PipelinePropertyWdg','PipelineSaveCbk', 'ConnectorInfoWdg', 'ProcessInfoWdg']

import re
from tactic.ui.common import BaseRefreshWdg

from pyasm.common import Environment
from pyasm.biz import Pipeline, Project
from pyasm.command import Command
from pyasm.web import DivWdg, WebContainer, Table, SpanWdg, HtmlElement
from pyasm.search import Search, SearchType, SearchKey, SObject
from tactic.ui.panel import FastTableLayoutWdg

from pyasm.widget import ProdIconButtonWdg, IconWdg, TextWdg, CheckboxWdg, HiddenWdg, SelectWdg, TextAreaWdg

from tactic.ui.container import DialogWdg, TabWdg, SmartMenu, Menu, MenuItem, ResizableTableWdg
from tactic.ui.widget import ActionButtonWdg, SingleButtonWdg, IconButtonWdg
from tactic.ui.input import TextInputWdg, ColorInputWdg
from pipeline_canvas_wdg import PipelineCanvasWdg
from client.tactic_client_lib import TacticServerStub

class PipelineToolWdg(BaseRefreshWdg):
    '''This is the entire tool, including the sidebar and tabs, used to
    edit the various pipelines that exists'''

    def init(my):
        # to display pipelines of a certain search_type on load
        my.search_type = my.kwargs.get('search_type')
        my.search_key = my.kwargs.get('search_key')

    def get_display(my):

        top = my.top
        my.set_as_panel(top)
        top.add_class("spt_pipeline_tool_top")
        #top.add_style("margin-top: 10px")

        inner = DivWdg()
        top.add(inner)

        #table = Table()
        table = ResizableTableWdg()

        #table.add_style("width: 100%")

        table.add_color("background", "background")
        table.add_color("color", "color")
        inner.add(table)

        my.save_event = top.get_unique_event()

        cbjs_action = '''
        var el = bvr.firing_element;
        var edit_top = el.getParent(".spt_edit_top")

        var values = spt.api.get_input_values(edit_top, null, false);

        var group_name = values['edit|code'];
        var color = values['edit|color'];

        var top = bvr.src_el;
        var wrapper = top.getElement(".spt_pipeline_wrapper");
        spt.pipeline.init_cbk(wrapper);
        var group = spt.pipeline.get_group(group_name);
        if (group) {
            group.set_color(color);
        }

        var list = top.getElement(".spt_pipeline_list");
        spt.panel.refresh(list);

        var start = top.getElement(".spt_pipeline_editor_start");
        start.setStyle("display", "none");

        // TODO: group name is NULL ... need to get code of newly created pipeline
        spt.pipeline.clear_canvas();
        spt.pipeline.import_pipeline(group);

        '''

        inner.add_behavior( {
        'type': 'listen',
        'event_name': my.save_event,
        'cbjs_action': cbjs_action
        } )


        # only for new pipeline creation so that it gets clicked on after the UI refreshes
        save_new_cbjs_action = '''
        %s
        var server = TacticServerStub.get();
        var latest_pipeline_code = server.eval("@GET(sthpw/pipeline['@ORDER_BY','timestamp desc'].code)", {'single': true});
       
        spt.pipeline.remove_group("default");
        spt.named_events.fire_event('pipeline_' + latest_pipeline_code + '|click', bvr);
        '''%cbjs_action


        save_new_event = '%s_new' %my.save_event
        inner.add_named_listener(save_new_event,  save_new_cbjs_action)


        # only for editing pipelines for a particular Stype when the UI refreshes
        load_event = '%s_load' %my.save_event
       
        

        table.add_row()
        left = table.add_cell()
        left.add_style("width: 200px")
        left.add_style("min-width: 200px")
        left.add_style("vertical-align: top")
        left.add_border()

        pipeline_list = PipelineListWdg(save_event=my.save_event, save_new_event=save_new_event )
        left.add(pipeline_list)



        right = table.add_cell()
        right.add_border()

        pipeline_wdg = PipelineEditorWdg(height=my.kwargs.get('height'), width=my.kwargs.get('width'), save_new_event=save_new_event)
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
        msg_div.add("Select a pipeline<br/><br/>or<br/><br/>Create a new one")
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
        info = table.add_cell()
        #info.add_style("display: none")
        info.add_class("spt_pipeline_tool_info")
        info.add_class("spt_panel") 
        info.add_style("width: 400px")
        info.add_style("min-width: 400px")
        info.add_border()
        info_wdg = DivWdg()
        info.add(info_wdg)

        """
        from tactic.ui.panel import EditWdg
        search = Search("config/process")
        search.add_filter("process", process)
        process_sobj = search.get_sobject()
        search_key = process_sobj.get_search_key()
        kwargs = {
                'search_key': search_key,
                'show_header': False,
                'width': '400px',
        }
        edit_wdg = ProcessInfoWdg(**kwargs)
        info_wdg.add(edit_wdg)
        """



        show_info_tab = my.kwargs.get("show_info_tab")
        show_info_tab = True
        if show_info_tab in ['false', False]:
            show_info_tab = False
        else:
            show_info_tab = True
      
        if show_info_tab:
            tr = table.add_row()
            td = table.add_cell()
            td.add_attr("colspan", "3")
            bottom = DivWdg()
            td.add(bottom)

            bottom.add_style("min-height: 200px")

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
            tab = TabWdg(config_xml=config_xml, extra_menu=my.get_extra_tab_menu())
            bottom.add(tab)


            # add onload action at the very end
            if my.search_type:
                load_cbjs_action = '''
                var server = TacticServerStub.get();
                var pipeline_codes = server.eval("@GET(sthpw/pipeline['search_type','%s'].code)");
                
                var src_el = spt.get_element(document, '.spt_pipeline_list');
                var firing_el = src_el;
                for (var k=0; k<pipeline_codes.length; k++)
                    spt.named_events.fire_event('pipeline_' + pipeline_codes[k] + '|click', bvr);

                '''%( my.search_type)


                bottom.add_behavior({
                          'type':'load',
                          'cbjs_action':  load_cbjs_action})

            elif my.search_key:
                load_cbjs_action = '''
                var server = TacticServerStub.get();
                var so = server.get_by_search_key('%s');
                if (so)
                    spt.named_events.fire_event('pipeline_' + so.code + '|click', bvr);

                '''%( my.search_key)


                bottom.add_behavior({
                          'type':'load',
                          'cbjs_action':  load_cbjs_action})


        if my.kwargs.get("is_refresh"):
            return inner
        else:
            return top




    def get_extra_tab_menu(my):
        menu = Menu(width=180)

        menu_item = MenuItem(type='title', label='Raw Data')
        menu.add(menu_item)

        menu_item = MenuItem(type='action', label='Show Site Wide Pipelines')
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
        spt.tab.add_new("site_wide_pipeline", "Site Wide Pipelines", class_name, kwargs);

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

        
    def init(my):
        my.save_event = my.kwargs.get("save_event")

        my.save_new_event = my.kwargs.get("save_new_event")

    def get_display(my):

        top = my.top
        top.add_class("spt_pipeline_list")
        my.set_as_panel(top)
        top.add_style("position: relative")

        title_div = DivWdg()


        button = ActionButtonWdg(title="+", tip="Add a new pipeline", size='small')
        button.add_style("position: absolute")
        button.add_style("top: 5px")
        button.add_style("right: 5px")

        button.add_behavior( {
        'type': 'click_up',
        'save_event': my.save_new_event,
        'cbjs_action': '''
        var class_name = 'tactic.ui.panel.EditWdg';
        var kwargs = {
            search_type: 'sthpw/pipeline',
            view: 'insert',
            show_header: false,
            single: true,
            save_event: bvr.save_event
        }
        spt.api.load_popup("Add New Pipeline", class_name, kwargs);
        '''
        } )



        title_div.add(button)

        top.add(title_div)
        title_div.add_style("height: 30px")
        title_div.add_style("padding-left: 5px")
        title_div.add_style("padding-top: 10px")
        title_div.add_color("background", "background", -10)
        title_div.add("<b>Pipeline</b>")



        top.add("<br/>")

        pipelines_div = DivWdg()
        top.add(pipelines_div)
        pipelines_div.add_class("spt_resizable")
        pipelines_div.add_style("overflow-x: hidden")
        pipelines_div.add_style("min-height: 290px")
        pipelines_div.add_style("min-width: 200px")
        pipelines_div.add_style("width: 200px")
        pipelines_div.add_style("height: auto")

        inner = DivWdg()
        inner.add_class("spt_pipeline_list_top")
        inner.add_style("width: 300px")
        inner.add_style("height: 290px")
        pipelines_div.add(inner)


        # add in a context menu
        menu = my.get_pipeline_context_menu()
        menus = [menu.get_data()]
        menus_in = {
            'PIPELINE_CTX': menus,
        }
        from tactic.ui.container.smart_menu_wdg import SmartMenu
        SmartMenu.attach_smart_context_menu( pipelines_div, menus_in, False )


        project_code = Project.get_project_code()





        # template pipeline
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


        pipeline_div = my.get_pipeline_wdg(pipeline)
        inner.add(pipeline_div)


        inner.add("<br/>")






        # project_specific pipelines
        from pyasm.widget import SwapDisplayWdg
        swap = SwapDisplayWdg(on_event_name='proj_pipe_on', off_event_name='proj_pipe_off')
        # open by default
        inner.add(swap)
        swap.add_style("float: left")


        title = DivWdg("<b>Project Pipelines</b>")
        title.add_style("padding-bottom: 2px")
        title.add_style("padding-top: 3px")
        inner.add(title)
        #inner.add(HtmlElement.br())
        content_div = DivWdg()
        content_div.add_styles('padding-left: 8px; padding-top: 6px') 
        SwapDisplayWdg.create_swap_title(title, swap, content_div, is_open=True)
        inner.add(content_div)
        try:
            #search = Search("config/pipeline")
            #pipelines = search.get_sobjects()
            search = Search("sthpw/pipeline")
            search.add_op("begin")
            search.add_filter("project_code", project_code)

            search.add_op("begin")
            search.add_filter("search_type", "sthpw/task", op="!=")
            # This pretty weird that != does not find NULL values
            search.add_filter("search_type", "NULL", op='is', quoted=False)
            search.add_op("or")
            search.add_op("and")
            search.add_filter("code", "%s/__TEMPLATE__" % project_code, op="!=")
            pipelines = search.get_sobjects()
            for pipeline in pipelines:
                if pipeline.get_value("parent_process"):
                    continue

                # build each pipeline menu item
                pipeline_div = my.get_pipeline_wdg(pipeline)
                content_div.add(pipeline_div)

            if not pipelines:
                no_items = DivWdg()
                no_items.add_style("padding: 3px 0px 3px 20px")
                content_div.add(no_items)
                no_items.add("<i>-- No Items --</i>")

        except:
            none_wdg = DivWdg("<i>&nbsp;&nbsp;-- No Items --</i>")
            none_wdg.add_style("font-size: 11px")
            none_wdg.add_color("color", "color", 20)
            none_wdg.add_style("padding", "5px")
            content_div.add( none_wdg )

        inner.add("<br clear='all'/>")

        # task status pipelines
        swap = SwapDisplayWdg()
        inner.add(swap)
        swap.add_style("float: left")

        title = DivWdg("<b>Task Status Pipelines</b>")
        title.add_style("padding-bottom: 2px")
        title.add_style("padding-top: 3px")
        inner.add(title)
        content_div = DivWdg()
        content_div.add_styles('padding-left: 8px; padding-top: 6px') 
        SwapDisplayWdg.create_swap_title(title, swap, content_div, is_open=True)
        inner.add(content_div)

        search = Search("sthpw/pipeline")
        search.add_filter("project_code", project_code)
        search.add_op("begin")
        search.add_filter("search_type", "sthpw/task")
        #search.add_filter("search_type", "NULL", op='is', quoted=False)
        search.add_op("or")
        search.add_filter("code", "%s/__TEMPLATE__" % project_code, op="!=")
        pipelines = search.get_sobjects()

        colors = {}
        for pipeline in pipelines:
            pipeline_div = my.get_pipeline_wdg(pipeline)
            content_div.add(pipeline_div)
            colors[pipeline.get_code()] = pipeline.get_value("color")

        if not pipelines:
            no_items = DivWdg()
            no_items.add_style("padding: 3px 0px 3px 20px")
            content_div.add(no_items)
            no_items.add("<i>-- No Items --</i>")



        inner.add("<br clear='all'/>")

        # misc status pipelines
        swap = SwapDisplayWdg()
        inner.add(swap)
        swap.add_style("float: left")

        title = DivWdg("<b>Misc Pipelines</b>")
        title.add_style("padding-bottom: 2px")
        title.add_style("padding-top: 3px")
        inner.add(title)
        content_div = DivWdg()
        content_div.add_styles('padding-left: 8px; padding-top: 6px') 
        SwapDisplayWdg.create_swap_title(title, swap, content_div, is_open=True)
        inner.add(content_div)

        search = Search("sthpw/pipeline")
        search.add_filter("project_code", project_code)
        search.add_op("begin")
        search.add_filter("search_type", "NULL", op='is', quoted=False)
        search.add_op("or")
        search.add_filter("code", "%s/__TEMPLATE__" % project_code, op="!=")
        pipelines = search.get_sobjects()

        colors = {}
        for pipeline in pipelines:
            pipeline_div = my.get_pipeline_wdg(pipeline)
            content_div.add(pipeline_div)
            colors[pipeline.get_code()] = pipeline.get_value("color")

        if not pipelines:
            no_items = DivWdg()
            no_items.add_style("padding: 3px 0px 3px 20px")
            content_div.add(no_items)
            no_items.add("<i>-- No Items --</i>")




        inner.add("<br clear='all'/>")



        # site-wide  pipelines
        search = Search("sthpw/pipeline")
        search.add_filter("project_code", "NULL", op="is", quoted=False)
        pipelines = search.get_sobjects()

        swap = SwapDisplayWdg()

        title = DivWdg()
        inner.add(swap)
        swap.add_style("margin-top: -2px")
        inner.add(title)
        swap.add_style("float: left")
        title.add("<b>Site Wide Pipelines</b><br/>")
      
        site_wide_div = DivWdg()
        site_wide_div.add_styles('padding-left: 8px; padding-top: 6px') 
        SwapDisplayWdg.create_swap_title(title, swap, site_wide_div, is_open=False)

        colors = {}
        inner.add(site_wide_div)
        site_wide_div.add_class("spt_pipeline_list_site")

        for pipeline in pipelines:
            pipeline_div = my.get_pipeline_wdg(pipeline)
            site_wide_div.add(pipeline_div)
            colors[pipeline.get_code()] = pipeline.get_value("color")

        # this is done in spt.pipeline.first_init() already
        """
        inner.add_behavior( {
        'type': 'load',
        'colors': colors,
        'cbjs_action': '''
        var top = bvr.src_el.getParent(".spt_pipeline_tool_top");
        var wrapper = top.getElement(".spt_pipeline_wrapper");
        spt.pipeline.init_cbk(wrapper);
        var data = spt.pipeline.get_data();
        data.colors = bvr.colors;
        '''
        } )
        """

        return top




    def get_pipeline_wdg(my, pipeline):
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
        
        # remove weird symbols in description
        description = re.sub(r'\W', '', description)
        
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
        'title': title,
        'event_name': 'pipeline_%s|click' % pipeline_code,
        'cbjs_action': '''
        //var src_el = bvr.firing_element;
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

            // check if the group already exists
            /*
            var group_name = bvr.pipeline_code;
            var group = spt.pipeline.get_group(bvr.pipeline_code);
            if (group != null) {

                // if it already exists, then select all from the group
                spt.pipeline.select_nodes_by_group(group_name);
                spt.pipeline.fit_to_canvas(group_name);
                return;

            }
            */


            var start_el = top.getElement(".spt_pipeline_editor_start")
            start_el.setStyle("display", "none")

            spt.pipeline.clear_canvas();

            spt.pipeline.import_pipeline(bvr.pipeline_code);


            // add to the current list
            var value = bvr.pipeline_code;
            var title = bvr.title;

            
            var text = top.getElement(".spt_pipeline_editor_current2");
            //text.value = title;
            var html = "<span class='hand spt_pipeline_link' spt_pipeline_code='"+bvr.pipeline_code+"'>"+bvr.title+"</span>";
            text.innerHTML = html;

            spt.pipeline.set_current_group(value);


        };


        var current_group_name = spt.pipeline.get_current_group();
        var group_name = bvr.pipeline_code;
        if (editor_top && editor_top.hasClass("spt_has_changes")) {
            spt.confirm("Current pipeline has changes.  Do you wish to continue without saving?", ok, null); 
        }
        else if (current_group_name == group_name) {
            spt.confirm("Reload current pipeline?", ok, null); 
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

        search_type = pipeline.get_value("search_type")
        if search_type:
            span = SpanWdg()
            span.add_style("font-size: 11px")
            span.add_style("opacity: 0.75")
            pipeline_div.add(span)
            span.add(" (%s)" % search_type)

        pipeline_div.add("<br clear='all'/>")

        pipeline_div.add_attr("spt_element_name", pipeline_code)
        from tactic.ui.container.smart_menu_wdg import SmartMenu
        SmartMenu.assign_as_local_activator( pipeline_div, 'PIPELINE_CTX' )

        return pipeline_div




    def get_pipeline_context_menu(my):

        menu = Menu(width=180)
        menu.set_allow_icons(False)
        menu.set_setup_cbfn( 'spt.dg_table.smenu_ctx.setup_cbk' )


        menu_item = MenuItem(type='title', label='Actions')
        menu.add(menu_item)

        """
        menu_item = MenuItem(type='action', label='Copy to Project')
        menu_item.add_behavior( {
            'cbjs_action': '''
            spt.alert('Not implemented');
            '''
        } )
        menu.add(menu_item)
        """


        

        menu_item = MenuItem(type='action', label='Edit Data')
        menu_item.add_behavior( {
            'cbjs_action': '''
            var activator = spt.smenu.get_activator(bvr);
            var code = activator.getAttribute("spt_pipeline");
            var search_type = 'sthpw/pipeline';
            var kwargs = {
                'search_type': search_type,
                'code': code,
                'view': 'pipeline_edit_tool',
                'save_event': '%s'
            };
            var class_name = 'tactic.ui.panel.EditWdg';
            spt.panel.load_popup("Edit Pipeline", class_name, kwargs);
            ''' % my.save_event
        } )
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

            spt.confirm("Confirm to delete pipeline ["+name+"]", ok);
            '''
        } )
        menu.add(menu_item)




        return menu




class PipelineToolCanvasWdg(PipelineCanvasWdg):

    def get_node_behaviors(my):
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


    def get_canvas_behaviors(my):
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




    def get_node_context_menu(my):

        menu = super(PipelineToolCanvasWdg, my).get_node_context_menu()


        project_code = Project.get_project_code()

        menu_item = MenuItem(type='title', label='Details')
        menu.add(menu_item)

        """
        menu_item = MenuItem(type='action', label='Edit Properties')
        menu.add(menu_item)
        menu_item.add_behavior( {
            'cbjs_action': '''
            var node = spt.smenu.get_activator(bvr);
            spt.named_events.fire_event('pipeline|show_properties', {src_el: node});

            '''
        } )
        """


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
                 spt.info("Process entry does not exist. Try saving this pipeline first.");
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


        menu_item = MenuItem(type='action', label='Show Processes')
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

        var top = node.getParent(".spt_pipeline_tool_top");
        spt.tab.top = top.getElement(".spt_tab_top");
        spt.tab.add_new("processes", "Processes", class_name, kwargs);
        '''
        } )




        menu_item = MenuItem(type='action', label='Edit Task Status Pipeline')
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


        spt.confirm("Confirm to create a custom task status pipeline", ok)

        '''
        } )



        return menu



class PipelineInfoWdg(BaseRefreshWdg):
    def get_display(my):

        process = my.kwargs.get("process")
        pipeline_code = my.kwargs.get("pipeline_code")

        top = my.top

        if not pipeline_code:
            return top

        pipeline = Search.get_by_code("sthpw/pipeline", pipeline_code)

        if not process:
            return top


        search_type = pipeline.get_value("search_type")

        top.add_style("padding: 20px 0px")
        top.add_color("background", "background")
        top.add_style("min-width: 300px")


        title_wdg = DivWdg()
        title_wdg.add_style("margin: -20px 0px 10px 0px")
        top.add(title_wdg)
        title_wdg.add("Pipeline: %s" % pipeline.get("name"))
        title_wdg.add_style("font-size: 1.2em")
        title_wdg.add_style("font-weight: bold")
        title_wdg.add_color("background", "background", -5)
        title_wdg.add_style("padding: 15px 10px")


        # sobject count
        if search_type:
            search = Search(search_type)
            search.add_filter("pipeline_code", pipeline.get_code())
            sobject_count = search.get_count()


        return top




class ConnectorInfoWdg(BaseRefreshWdg):

    def get_display(my):
        
        top = my.top
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
        
        pipeline_code = my.kwargs.get("pipeline_code")
        pipeline = Pipeline.get_by_code(pipeline_code)

        from_node = my.kwargs.get("from_node")
        to_node = my.kwargs.get("to_node")
        left_process = pipeline.get_process(from_node)
        right_process = pipeline.get_process(to_node)
        
        # If either the left process or right process do not exist,
        # display empty pane.
        if not left_process or not right_process:
            info_wdg = DivWdg()
            info_wdg.add_style("margin: 10px")
            info_wdg.add("Save your pipeline to edit connector properties.") 
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

        """
        connects = pipeline.get_output_connects(from_node)
        for connect in connects:
            to = connect.get_to()
            if to == to_node:
                break;

        from_attr = connect.get_attr("from_attr")
        if not from_attr:
            from_attr = "output"
        to_attr = connect.get_attr("to_attr")
        if not to_attr:
            to_attr = "input"

        """


        left_selected = my.kwargs.get("from_attr")
        if not left_selected:
            left_selected = "output"
        right_selected = my.kwargs.get("to_attr")
        if not right_selected:
            right_selected = "input"

 
        table.add_row()

        # handle output
        left = table.add_cell()
        left.add_style("vertical-align: top")
        left.add_style("width: 150px")
        left.add_class("spt_connect_column_top")
        left.add_class("spt_dts")
        left.add_style("padding: 5px")
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
            'kwargs': my.kwargs,
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_pipeline_info_top");
            var info_top = bvr.src_el.getParent(".spt_pipeline_connector_info");
            var input = spt.api.get_input_values(info_top, null, false);

            console.log(input);

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

    def get_display(my):

        node_type = my.kwargs.get("node_type")


        pipeline_code = my.kwargs.get("pipeline_code")
        pipeline = Pipeline.get_by_code(pipeline_code)
        search_type = pipeline.get("search_type")


        top = my.top
        top.add_class(".spt_process_info_top")
        
        widget = None

        if search_type == "sthpw/task":
            widget = TaskStatusInfoWdg(**my.kwargs)

        elif node_type == 'approval':
            widget = ApprovalInfoWdg(**my.kwargs)

        if node_type == 'action':
            widget = ActionInfoWdg(**my.kwargs)

        if node_type == 'condition':
            widget = ConditionInfoWdg(**my.kwargs)

        if node_type == 'hierarchy':
            widget = HierarchyInfoWdg(**my.kwargs)

        if node_type == 'dependency':
            widget = DependencyInfoWdg(**my.kwargs)

        if node_type == 'progress':
            widget = ProgressInfoWdg(**my.kwargs)

        if node_type == 'unknown':
            widget = UnknownInfoWdg(**my.kwargs)

        if node_type == 'progress':
            widget = ProgressInfoWdg(**my.kwargs)

        if not widget:
            widget = DefaultInfoWdg(**my.kwargs)

        top.add(widget)

        return top




class BaseInfoWdg(BaseRefreshWdg):


    def get_input_output_wdg(my, pipeline, process):
            
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




    def get_title_wdg(my, process, node_type, show_node_type_select=True):

        title_wdg = DivWdg()
        title_wdg.add_style("margin: -20px 0px 10px 0px")
        title_wdg.add("%s" % (process))
        title_wdg.add_style("font-size: 1.2em")
        title_wdg.add_style("font-weight: bold")
        title_wdg.add_color("background", "background", -5)
        title_wdg.add_style("padding: 15px 10px")


        if not show_node_type_select:
            select = HiddenWdg("node_type")
            title_wdg.add(select)
            if node_type == "node":
                select.set_value("manual")
            else:
                select.set_value(node_type)
    

        else:


            select = SelectWdg("node_type")
            title_wdg.add(select)
            select.set_option("values", [
                'manual',
                'action',
                'condition',
                'approval',
                'hierarchy',
                # Not supported yet
                'dependency',
                'progress'
            ])
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
            select.add_style("float: right")
            select.add_style("margin-top: -5px")

        return title_wdg





class DefaultInfoWdg(BaseInfoWdg):


    def get_display(my):
        process = my.kwargs.get("process")
        pipeline_code = my.kwargs.get("pipeline_code")
        node_type = my.kwargs.get("node_type")

        top = my.top

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



        title_wdg = my.get_title_wdg(process, node_type)
        top.add( title_wdg )


        search = Search("config/process")
        search.add_filter("process", process)
        search.add_filter("pipeline_code", pipeline_code)

        process_sobj = search.get_sobject()



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


        process_code = process_sobj.get_value("code")

        # triggers
        search = Search("config/trigger")
        search.add_filters("process", [process,process_code])
        trigger_count = search.get_count()


        # notifications
        search = Search("sthpw/notification")
        search.add_project_filter()
        search.add_filter("process", process)
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


        table = Table()
        top.add(table)
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



        has_tasks = True
        if has_tasks:
            div = DivWdg()
            top.add(div)
            div.add_style("padding: 10px")
            div.add("<br/><hr/><br/>")
            div.add("<b>Task setup</b><br/>")
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
                var popup = spt.panel.load_popup("Task Setup for ["+bvr.process+"]", class_name, kwargs);
                var nodes = spt.pipeline.get_selected_nodes();
                var node = nodes[0];
                spt.pipeline_properties.show_properties2(popup, node);
                '''
            } )


        has_checkins = True
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



        #show error message if the node has not been registered 
        """
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
           
        else:
            from tactic.ui.panel import EditWdg
            edit = EditWdg(
                    search_type="config/process",
                    show_header=False,
                    width="400px",
                    #view="pipeline_tool_edit",
                    search_key=process_sobj.get_search_key(),
            )
            top.add(edit)

            top.add("<br clear='all'/>")
        """



        return top








class ActionInfoWdg(BaseInfoWdg):


    def get_display(my):

        top = my.top
        top.add_style("padding: 20px 0px")

        process = my.kwargs.get("process")
        pipeline_code = my.kwargs.get("pipeline_code")
        node_type = my.kwargs.get("node_type")

        pipeline = Pipeline.get_by_code(pipeline_code)


        # get the process sobject
        search = Search("config/process")
        search.add_filter("pipeline_code", pipeline_code)
        search.add_filter("process", process)
        process_sobj = search.get_sobject()


        event = "process|action"

        language = ""

        # get the trigger
        script = None
        if process_sobj:
            search = Search("config/trigger")
            search.add_filter("process", process_sobj.get_code())
            search.add_filter("event", event)
            trigger = search.get_sobject()

            # get the custom script 
            if trigger:
                script_path = trigger.get("script_path")

                if script_path:
                    parts = script_path.split("/")
                    folder = "/".join(parts[:-1])
                    title = parts[-1]

                    search = Search("config/custom_script")
                    search.add_filter("folder", folder)
                    search.add_filter("title", title)
                    custom_script = search.get_sobject()
                    if custom_script:
                        script = custom_script.get("script")
                        language = custom_script.get("language")


        title_wdg = my.get_title_wdg(process, node_type)
        top.add(title_wdg)

        """
        title_wdg = DivWdg()
        title_wdg.add_style("margin: -20px 0px 10px 0px")
        top.add(title_wdg)
        title_wdg.add("%s: %s" % (node_type.title(), process))
        title_wdg.add_style("font-size: 1.2em")
        title_wdg.add_style("font-weight: bold")
        title_wdg.add_color("background", "background", -5)
        title_wdg.add_style("padding: 15px 10px")
        """



        input_output_wdg = my.get_input_output_wdg(pipeline, process)
        top.add(input_output_wdg)


        form_wdg = DivWdg()
        top.add(form_wdg)
        form_wdg.add_style("padding: 10px")

        is_admin = Environment.get_security().is_admin()

        if node_type == "action":

            form_wdg.add("<b>Action:</b><br/>")
            form_wdg.add("This will be the automatically executed action for this process.")
            form_wdg.add("<br/>")
            form_wdg.add("<br/>")

            if is_admin:
                form_wdg.add("Language:")
                select = SelectWdg("language")
                form_wdg.add(select)
                select.set_option("labels", "Python|Javascript")
                select.set_option("values", "python|server_js")
                select.set_value(language)
                form_wdg.add("<br/>")
                form_wdg.add("Script:<br/>")
            else:
                form_wdg.add("Javascript:<br/>")


            text = TextAreaWdg(name="on_action")
            text.add_class("form-control")
            if script:
                text.set_value(script)
            text.add_style("height: 300px")
            text.add_style("width: 100%")
            form_wdg.add(text)
            form_wdg.add("<br/>")




        else:
            form_wdg.add("<b>Check Condition</b><br/>")
            form_wdg.add("This will be executed on the completion event of an input process.  The condition check should either return True or False or a list of the output streams.")

            script_path = "Big/Test"

            form_wdg.add("<br/>")
            form_wdg.add("<br/>")


            if is_admin:
                form_wdg.add("Language:")
                select = SelectWdg("language")
                form_wdg.add(select)
                select.set_option("labels", "Python|Javascript")
                select.set_option("values", "python|server_js")
                select.set_value(language)
                form_wdg.add("<br/>")
                form_wdg.add("Script:<br/>")
            else:
                form_wdg.add("Javascript:<br/>")



            """
            edit = ActionButtonWdg(title="Edit")
            form_wdg.add(edit)
            edit.add_style("float: right")
            edit.add_style("margin: 5px 0px")
            edit.add_behavior( {
            'type': 'click_up',
            'script_path': script_path,
            'cbjs_action': '''
            var class_name = 'tactic.ui.app.ScriptEditorWdg';

            var kwargs = {
                script_path: bvr.script_path
            };
            spt.panel.load_popup("TACTIC Script Editor", class_name, kwargs);

            '''
            } )
            """

            text = TextAreaWdg(name="on_action")
            form_wdg.add(text)
            text.add_class("form-control")
            text.add_style("height: 300px")
            text.add_style("width: 100%")
            if script:
                text.set_value(script)

            form_wdg.add("<br/>")



        save = ActionButtonWdg(title="Save")
        save.add_style("float: right")
        top.add(save)
        save.add_behavior( {
            'type': 'click_up',
            'pipeline_code': pipeline_code,
            'process': process,
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_pipeline_info_top");
            var input = spt.api.get_input_values(top, null, false);

            var server = TacticServerStub.get();
            var class_name = 'tactic.ui.tools.ProcessInfoCmd';
            var kwargs = {
                node_type: 'action',
                pipeline_code: bvr.pipeline_code,
                process: bvr.process,
                on_action: input.on_action,
                on_action_class: input.on_action_class,
                language: input.language,
            }

            server.execute_cmd(class_name, kwargs);

            '''
        } )




        return top




    def get_process_triggers(my):

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


        save = ActionButtonWdg(title="Save")
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

    def get_display(my):

        process = my.kwargs.get("process")
        pipeline_code = my.kwargs.get("pipeline_code")
        node_type = my.kwargs.get("node_type")

 

        search = Search("config/process")
        search.add_filter("pipeline_code", pipeline_code)
        search.add_filter("process", process)
        process_sobj = search.get_sobject()


        workflow = process_sobj.get_json_value("workflow")
        if not workflow:
            workflow = {}



        top = my.top
        top.add_style("padding: 20px 0px")
        top.add_class("spt_approval_info_top")

        process = my.kwargs.get("process")
        pipeline_code = my.kwargs.get("pipeline_code")
        node_type = my.kwargs.get("node_type")


        pipeline = Pipeline.get_by_code(pipeline_code)


        title_wdg = my.get_title_wdg(process, node_type)
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

    def get_display(my):

        process = my.kwargs.get("process")
        pipeline_code = my.kwargs.get("pipeline_code")
        node_type = my.kwargs.get("node_type")

 

        search = Search("config/process")
        search.add_filter("pipeline_code", pipeline_code)
        search.add_filter("process", process)
        process_sobj = search.get_sobject()
        workflow = {}
        if process_sobj:
            workflow = process_sobj.get_json_value("workflow")
        if not workflow:
            workflow = {}



        top = my.top
        top.add_style("padding: 20px 0px")
        top.add_class("spt_approval_info_top")

        process = my.kwargs.get("process")
        pipeline_code = my.kwargs.get("pipeline_code")
        node_type = my.kwargs.get("node_type")


        pipeline = Pipeline.get_by_code(pipeline_code)


        title_wdg = my.get_title_wdg(process, node_type)
        top.add(title_wdg)




        input_output_wdg = my.get_input_output_wdg(pipeline, process)
        top.add( input_output_wdg )

        form_wdg = DivWdg()
        top.add(form_wdg)
        form_wdg.add_style("padding: 15px")

        form_wdg.add("Set a default person that will be assigned to the %s task." % process)

        form_wdg.add("<br/>")
        form_wdg.add("<br/>")

        from tactic.ui.input import LookAheadTextInputWdg
        text = LookAheadTextInputWdg(
                name="assigned",
                search_type="sthpw/login",
                column="login"
        )
        form_wdg.add(text)
        text.add_style("width: 100%")
        if workflow.get("assigned"):
            text.set_value(workflow.get("assigned"))


        form_wdg.add("<br/>")
        form_wdg.add("<br/>")


        save = ActionButtonWdg(title="Save", color="primary")

        save.add_style("float: right")
        form_wdg.add(save)
        save.add_behavior( {
            'type': 'click_up',
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

    def get_display(my):

        process = my.kwargs.get("process")
        pipeline_code = my.kwargs.get("pipeline_code")
        node_type = my.kwargs.get("node_type")

        top = my.top
        top.add_style("padding: 20px 0px")

 
        title_wdg = my.get_title_wdg(process, node_type)
        top.add(title_wdg)

        return top


class DependencyInfoWdg(BaseInfoWdg):

    def get_display(my):

        process = my.kwargs.get("process")
        pipeline_code = my.kwargs.get("pipeline_code")
        node_type = my.kwargs.get("node_type")


        search = Search("config/process")
        search.add_filter("pipeline_code", pipeline_code)
        search.add_filter("process", process)
        process_sobj = search.get_sobject()




        top = my.top
        top.add_style("padding: 20px 0px")
        top.add_class("spt_dependency_top")

 
        title_wdg = my.get_title_wdg(process, node_type)
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

    def get_display(my):

        process = my.kwargs.get("process")
        pipeline_code = my.kwargs.get("pipeline_code")
        node_type = my.kwargs.get("node_type")


        search = Search("config/process")
        search.add_filter("pipeline_code", pipeline_code)
        search.add_filter("process", process)
        process_sobj = search.get_sobject()




        top = my.top
        top.add_style("padding: 20px 0px")
        top.add_class("spt_progress_top")

 
        title_wdg = my.get_title_wdg(process, node_type)
        top.add(title_wdg)


        settings_wdg = DivWdg()
        top.add(settings_wdg)
        settings_wdg.add_style("padding: 0px 10px")


        workflow = process_sobj.get_json_value("workflow")
        if not workflow:
            workflow = {}

        related_search_type = workflow.get("search_type")
        related_process = workflow.get("process")
        related_status = workflow.get("status")
        related_scope = workflow.get("scope")
        related_wait = workflow.get("wait")


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
        settings_wdg.add("<b>Listen to events of search type:</b>")
        select = SelectWdg("related_search_type")
        settings_wdg.add(select)
        if related_search_type:
            select.set_value(related_search_type)
        select.set_option("values", values)
        select.set_option("labels", labels)
        select.add_empty_option("-- Select --")
        settings_wdg.add("<span style='opacity: 0.6'>This process will track the progress of the sobjects of the selected search type.</span>")
        settings_wdg.add("<br/>")


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




        search_type = "vfx/shot"


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

    def get_display(my):

        process = my.kwargs.get("process")
        pipeline_code = my.kwargs.get("pipeline_code")
        node_type = my.kwargs.get("node_type")



        top = my.top
        top.add_style("padding: 20px 0px")

        top.add_class("spt_status_top")
 
        title_wdg = my.get_title_wdg(process, node_type, show_node_type_select=False)
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




__all__.append("ProcessInfoCmd")
class ProcessInfoCmd(Command):

    def execute(my):

        node_type = my.kwargs.get("node_type")

        if node_type in ["action", "condition"]:
            return my.handle_action()

        if node_type == 'dependency':
            return my.handle_dependency()

        if node_type == 'status':
            return my.handle_status()

        if node_type == 'approval':
            return my.handle_approval()


        if node_type == 'progress':
            return my.handle_progress()





    def handle_action(my):

        on_action = my.kwargs.get("on_action")
        on_action_class = my.kwargs.get("on_action_class")
        if not on_action and not on_action_class:
            return


        pipeline_code = my.kwargs.get("pipeline_code")
        process = my.kwargs.get("process")
        is_admin = Environment.get_security().is_admin()
        if is_admin:
            language = my.kwargs.get("language")
        else:
            language = "server_js"

        pipeline = Pipeline.get_by_code(pipeline_code)

        search = Search("config/process")
        search.add_filter("pipeline_code", pipeline_code)
        search.add_filter("process", process)
        process_sobj = search.get_sobject()


        event = "process|action"

        folder = "_triggers/%s" % pipeline.get_code()
        title = process_sobj.get_code()

        # check to see if the trigger already exists
        search = Search("config/trigger")
        search.add_filter("process", process_sobj.get_code())
        search.add_filter("event", event)
        trigger = search.get_sobject()
        if not trigger:
            trigger = SearchType.create("config/trigger")
            trigger.set_value("event", event)
            trigger.set_value("process", process_sobj.get_code())
            trigger.set_value("mode", "same process,same transaction")

        if on_action:
            trigger.set_value("script_path", "%s/%s" % (folder, title))
        else:
            trigger.set_value("class_name", on_action_class)
        trigger.commit()

        if on_action:
            # check to see if the script already exists
            search = Search("config/custom_script")
            search.add_filter("folder", folder)
            search.add_filter("title", "%s" % title)
            script = search.get_sobject()
            if not script:
                script = SearchType.create("config/custom_script")
                script.set_value("folder", folder)
                script.set_value("title", "%s" % title)

            script.set_value("language", language)
            script.set_value("script", on_action)
            script.commit()


    def handle_dependency(my):

        pipeline_code = my.kwargs.get("pipeline_code")
        process = my.kwargs.get("process")

        pipeline = Pipeline.get_by_code(pipeline_code)

        search = Search("config/process")
        search.add_filter("pipeline_code", pipeline_code)
        search.add_filter("process", process)
        process_sobj = search.get_sobject()


        related_search_type = my.kwargs.get("related_search_type")
        related_process = my.kwargs.get("related_process")
        related_status = my.kwargs.get("related_status")
        related_scope = my.kwargs.get("related_scope")
        related_wait = my.kwargs.get("related_wait")

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


    def handle_approval(my):
        pipeline_code = my.kwargs.get("pipeline_code")
        process = my.kwargs.get("process")
        assigned = my.kwargs.get("assigned")

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

    def handle_approval(my):

        pipeline_code = my.kwargs.get("pipeline_code")
        process = my.kwargs.get("process")

        pipeline = Pipeline.get_by_code(pipeline_code)
        
        search = Search("config/process")
        search.add_filter("pipeline_code", pipeline_code)
        search.add_filter("process", process)
        process_sobj = search.get_sobject()

        if not process_sobj:
            return

        direction = my.kwargs.get("direction")
        status = my.kwargs.get("status")
        mapping = my.kwargs.get("mapping")
        color = my.kwargs.get("color")
        assigned = my.kwargs.get("assigned")

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



    def handle_progress(my):

        pipeline_code = my.kwargs.get("pipeline_code")
        process = my.kwargs.get("process")

        pipeline = Pipeline.get_by_code(pipeline_code)
        search_type = pipeline.get_value("search_type")

        search = Search("config/process")
        search.add_filter("pipeline_code", pipeline_code)
        search.add_filter("process", process)
        process_sobj = search.get_sobject()


        related_search_type = my.kwargs.get("related_search_type")
        related_process = my.kwargs.get("related_process")
        if not related_process:
            related_process = process
        related_scope = my.kwargs.get("related_scope")
        if not related_scope:
            related_scope = "local"

        workflow = process_sobj.get_json_value("workflow")
        if not workflow:
            workflow = {}

        if related_search_type:
            workflow['search_type'] = related_search_type
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

    def get_display(my):
        top = my.top
        my.set_as_panel(top)
        top.add_class("spt_pipeline_editor_top")

        my.save_new_event = my.kwargs.get("save_new_event")


        inner = DivWdg()
        top.add(inner)


        inner.add(my.get_shelf_wdg() )


        my.width = my.kwargs.get("width")
        if not my.width:
            #my.width = "1300"
            my.width = "auto"
        my.height = my.kwargs.get("height")
        if not my.height:
            my.height = 600


        
        canvas_top = DivWdg()
        inner.add(canvas_top)
        canvas_top.add_class("spt_pipeline_wrapper")
        canvas_top.add_style("position: relative")
        canvas = my.get_canvas()
        my.unique_id = canvas.get_unique_id()
        canvas_top.add(canvas)



        div = DivWdg()
        inner.add(div)

        pipeline_str = my.kwargs.get("pipeline")
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
        event_name = "%s|node_create" % my.unique_id

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

        node.click();
        '''
        } )


        # open connection dialog everytime a connection is made
        event_name = "%s|node_rename" % my.unique_id

        # Note this goes through every node, every time?
        div.add_behavior( {
        'type': 'listen',
        'event_name': event_name,
        'cbjs_action': '''
        var node = bvr.firing_element;
        var data = bvr.firing_data;

        var old_name = data.old_name;
        var name = data.name;

        // rename the process on the server
        var group_name = spt.pipeline.get_current_group();
        var process = server.eval("@SOBJECT(config/process['process','"+old_name+"']['pipeline_code','"+group_name+"'])", {single: true});

        server.update(process, {process: name});

        // select the node
        node.click();

        spt.named_events.fire_event('pipeline|change', {});
        '''
        } )
 


        if my.kwargs.get("is_refresh") == 'true':
            return inner
        else:
            return top


    def get_shelf_wdg(my):
 
        shelf_wdg = DivWdg()
        shelf_wdg.add_style("padding: 5px")
        shelf_wdg.add_style("margin-bottom: 5px")
        shelf_wdg.add_style("overflow-x: hidden")
        shelf_wdg.add_style("min-width: 400px")

        show_shelf = my.kwargs.get("show_shelf")
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


        button_div = my.get_buttons_wdg();
        button_div.add_style("float: left")
        shelf_wdg.add(button_div)

        shelf_wdg.add(spacing_divs[0])

        #group_div = my.get_pipeline_select_wdg();
        #group_div.add_style("float: left")
        #group_div.add_style("margin-top: 1px")
        #group_div.add_style("margin-left: 10px")
        #shelf_wdg.add(group_div)
        #shelf_wdg.add(spacing_divs[1])

        button_div = my.get_zoom_buttons_wdg();
        button_div.add_style("margin-left: 10px")
        button_div.add_style("margin-right: 15px")
        button_div.add_style("float: left")
        shelf_wdg.add(button_div)

        # Show schema for reference.  This does not work very well.
        # Disabling
        """
        shelf_wdg.add(spacing_divs[2])

        button_div = my.get_schema_buttons_wdg();
        button_div.add_style("margin-left: 10px")
        button_div.add_style("float: left")
        shelf_wdg.add(button_div)
        """

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


    def get_canvas(my):
        is_editable = my.kwargs.get("is_editable")
        canvas = PipelineToolCanvasWdg(height=my.height, width=my.width, is_editable=is_editable)
        return canvas



    def get_buttons_wdg(my):
        from pyasm.widget import IconWdg
        from tactic.ui.widget.button_new_wdg import ButtonNewWdg, ButtonRowWdg

        button_row = ButtonRowWdg(show_title=True)

        project_code = Project.get_project_code()


        # Do we even need a refresh button?
        """
        button = ButtonNewWdg(title="REFRESH", icon="BS_REFRESH")
        button_row.add(button)

        button.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
            var editor_top = bvr.src_el.getParent(".spt_pipeline_editor_top");
            var ok = function () { 
                editor_top.removeClass("spt_has_changes");
                spt.panel.refresh(editor_top); 
            }
            if (editor_top && editor_top.hasClass("spt_has_changes")) {
                spt.confirm("Current pipeline has changes.  Do you wish to continue?", ok, null);
            } else {
                ok();
            }
        '''
        } )
        """


        button = ButtonNewWdg(title="Save Current Pipeline", icon="BS_SAVE")
        button_row.add(button)

        button.add_behavior( {
        'type': 'click_up',
        'project_code': project_code,
        'save_event': my.save_new_event,
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
            spt.api.load_popup("Add New Pipeline", class_name, kwargs);
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



        //spt.panel.refresh(editor_top);

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
        

        menu_item = MenuItem(type='action', label='Save as Site Wide Pipeline')
        menu.add(menu_item)
        # no project code here
        menu_item.add_behavior( {
            'cbjs_action': '''
        var act = spt.smenu.get_activator(bvr);
        
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
                default: {
                    pipeline: xml
                }
            }
            spt.api.load_popup("Add New Pipeline", class_name, kwargs);
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
        '''
        } )

        menu_item = MenuItem(type='action', label='Save All Pipelines')
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
                spt.app_busy.show("Saving All Pipelines ["+group_name+"]",null);
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
            spt.confirm("Saving all pipelines does not make new pipelines project specific. Continue?", ok, cancel );
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



        menu_item = MenuItem(type='action', label='Add Sub-pipeline')
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

        # TEST TEST TEST 
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

        spt.pipeline.delete_selected();

        var nodes = spt.pipeline.get_selected_nodes();
        for (var i = 0; i < nodes.length; i++) {
            spt.pipeline.remove_node(nodes[i]);
        }
        '''
        } )



        return button_row


    def get_zoom_buttons_wdg(my):
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



    def get_schema_buttons_wdg(my):
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





    def get_pipeline_select_wdg(my):
        div = DivWdg()
        div.add_style("padding: 3px")

        pipeline_select = SelectWdg("current_pipeline")
        #div.add(pipeline_select)
        pipeline_select.add_style("display: table-cell")
        pipeline_select.add_class("spt_pipeline_editor_current")
        pipeline_select.set_option("values", "default")
        pipeline_select.set_option("labels", "-- New Pipeline --")

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

    def get_display(my):
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
        triggers_wdg = my.get_triggers_wdg( None, FilterData() )
        list_wdg.add_template(triggers_wdg)

        search = Search("config/trigger")
        triggers = search.get_sobjects()

        top.add("Items Found: %s" % len(triggers) )

        for trigger in triggers:
            data = trigger.get_value("data")
            filter_data = FilterData(data)

            triggers_wdg = my.get_triggers_wdg(trigger, filter_data)
            div = DivWdg()
            div.add(triggers_wdg)
            div.add_style("padding: 10px")
            list_wdg.add_item(div)

        top.add(list_wdg)

        return top


    def get_triggers_wdg(my, trigger, filter_data=None):
        div = DivWdg()
        div.add_class("spt_triggers")

        trigger_info = filter_data.get_values_by_index("trigger")
        my.process_name = trigger_info.get("process")
        if not my.process_name:
            my.process_name = my.kwargs.get("process")
        if not my.process_name:
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
        trigger_div.add( HiddenWdg("process", my.process_name) )


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
    def execute(my):

        data_str = my.kwargs.get("data")
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
            trigger.set_value("description", "Status change trigger defined by pipeline")

            trigger.set_value("mode", "same process,same transaction")

        trigger.set_value("data", jsondumps(data_str) )
        trigger.commit()







class PipelinePropertyWdg(BaseRefreshWdg):

    def get_display(my):
        div = DivWdg()
        div.add_class("spt_pipeline_properties_top")
        div.add_style("min-width: 500px")

        process = my.kwargs.get("process")
        pipeline_code = my.kwargs.get("pipeline_code")


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
        properties = ['group', "completion", "task_pipeline", 'assigned_login_group', 'supervisor_login_group',\
                'duration', 'bid_duration']


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
        'cbjs_action': my.get_onload_js()
        } )

        
        # group
        # Making invisible to ensure that it still gets recorded if there.
        tr = table.add_row()
        tr.add_style("display: none")
        td = table.add_cell('Group: ')
        td.add_style("width: 250px")
        td.add_attr("title", "Nodes can grouped together within a pipeline")
        #td.add_style("width: 200px")
        text_name = "spt_property_group"
        text = TextWdg(text_name)
        text.add_class(text_name)
        #text.add_event("onBlur", "spt.pipeline_properties.set_properties()")

        th = table.add_cell(text)
        th.add_style("height: 30px")
        
        # completion (visibility depends on sType)
        table.add_row(css='spt_property_status_completion')
        td = table.add_cell('Completion (0 to 100):')
        td.add_attr("title", "Determines the completion level that this node represents.")

        text_name = "spt_property_completion"
        text = TextWdg(text_name)
        text.add_class(text_name)
        #text.add_event("onBlur", "spt.pipeline_properties.set_properties()")

        th = table.add_cell(text)
        th.add_style("height: 30px")
        
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
        td = table.add_cell('Task Status Pipeline')
        td.add_attr("title", "The task status pipeline determines all of the statuses that occur within this process")

        text_name = "spt_property_task_pipeline"
        select = SelectWdg(text_name)
        #select.append_option('<< sthpw/task pipelines >>', '')

        
        for pipeline in task_pipelines:
            select.append_option(pipeline.get_value('code'), pipeline.get_value('code'))
        
        select.add_empty_option('-- Select --')
        select.add_class(text_name)
        #select.add_event("onBlur", "spt.pipeline_properties.set_properties()")

        th = table.add_cell(select)
        th.add_style("height: 40px")
        
        # The search needed for the login_group select widgets
        login_group_search = Search('sthpw/login_group')
        
        # assigned_login_group
        table.add_row()
        td = table.add_cell('Assigned Login Group:')
        td.add_attr("title", "Used for limiting the users displayed when this process is chosen in a task view.")

        text_name = "spt_property_assigned_login_group"
        select = SelectWdg(text_name)
        select.set_search_for_options(login_group_search, 'login_group', 'login_group')
        select.add_empty_option('-- Select --')
        select.add_class(text_name)
        #select.add_event("onBlur", "spt.pipeline_properties.set_properties()")

        th = table.add_cell(select)
        th.add_style("height: 40px")
        
        # supervisor_login_group
        table.add_row()
        td = table.add_cell('Supervisor Login Group:')
        td.add_attr("title", "Used for limiting the supervisors displayed when this process is chosen in a task view.")
        text_name = "spt_property_supervisor_login_group"
        select = SelectWdg(text_name)
        select.set_search_for_options(login_group_search, 'login_group', 'login_group')
        select.add_empty_option('-- Select --')
        select.add_class(text_name)
        #select.add_event("onBlur", "spt.pipeline_properties.set_properties()")

        th = table.add_cell(select)
        th.add_style("height: 40px")
        
        # duration
        table.add_row()
        td = table.add_cell('Default Duration:')
        td.add_attr("title", "The default duration determines the starting duration of a task that is generated for this process")

        text_name = "spt_property_duration"
        text = TextWdg(text_name)
        text.add_style("width: 40px")
        text.add_class(text_name)
        #text.add_event("onBlur", "spt.pipeline_properties.set_properties()")

        th = table.add_cell(text)
        th.add_style("height: 40px")
        th.add(" days")

        # bid duration in hours
        table.add_row()
        td = table.add_cell('Default Bid Duration:')
        td.add_attr("title", "The default bid duration determines the estimated number of hours will be spent on this task.")

        text_name = "spt_property_bid_duration"
        text = TextWdg(text_name)
        text.add_style("width: 40px")
        text.add_class(text_name)
        #text.add_event("onBlur", "spt.pipeline_properties.set_properties()")

        th = table.add_cell(text)
        th.add_style("height: 40px")
        th.add(" hours")
        
        # Color
        table.add_row()
        td = table.add_cell('Color:')
        td.add_attr("title", "Used by various parts of the interface to show the color of this process.")

        text_name = "spt_property_color"
        text = TextWdg(text_name)
        color = ColorInputWdg(text_name)
        color.set_input(text)
        text.add_class(text_name)
        #text.add_event("onBlur", "spt.pipeline_properties.set_properties()")

        td = table.add_cell(color)
        th.add_style("height: 40px")

        # label
        table.add_row()
        td = table.add_cell('Label:')

        text_name = "spt_property_label"
        text = TextWdg(text_name)
        text.add_class(text_name)
        #text.add_event("onChange", "spt.pipeline_properties.set_properties()")

        td = table.add_cell(text)
        td.add_style("height: 40px")

        tr, td = table.add_row_cell()

        button = ActionButtonWdg(title="Save", tip="Confirm properties change. Remember to save pipeline at the end.")
        td.add("<hr/>")
        td.add(button)
        button.add_style("float: right")
        button.add_style("margin-right: 20px")
        td.add("<br clear='all'/>")
        td.add("<br clear='all'/>")
        button.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        var top = bvr.src_el.getParent(".spt_pipeline_properties_top");
        var node = spt.pipeline.get_selected_node();
        if (!node) {
            alert("No node selected");
            return;
        }
        spt.pipeline_properties.set_properties2(top, node);


        var top = bvr.src_el.getParent(".spt_popup");
        spt.popup.close(top);

        spt.named_events.fire_event('pipeline|change', {});
        '''
        } )



        return div

    def get_onload_js(my):
        return r'''

spt.pipeline_properties = {};

// DEPRECATED
spt.pipeline_properties.set_properties = function(node) {

    console.log(node);

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
        console.log(values)
        console.log(node_name)
        var group = spt.pipeline.get_current_group();
        console.log(group);
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
        if (typeof(value) == 'undefined') {
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

spt.pipeline_properties.set_properties2 = function(prop_top, node) {

    var properties = ['group', 'completion', 'task_pipeline', 'assigned_login_group', 'supervisor_login_group','duration', 'bid_duration','color', 'label'];

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
    def get_title(my):
        return "Save a pipeline"

    def execute(my):
        pipeline_sk = my.kwargs.get('search_key')

        pipeline_xml = my.kwargs.get('pipeline')
        pipeline_color = my.kwargs.get('color')
        project_code = my.kwargs.get('project_code')

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
        process_names = pipeline.get_process_names()
        search = Search("config/process")
        search.add_filter("pipeline_code", pipeline_code)
        process_sobjs = search.get_sobjects()
        existing_names = SObject.get_values(process_sobjs, 'process')

        pipeline.on_insert()
        
        my.description = "Updated pipeline [%s]" % pipeline_code
        
        """
        count = 0
        for process_name in process_names:

            exists = False
            for process_sobj in process_sobjs:
                # if it already exist, then update
                if process_sobj.get_value("process") == process_name:
                    exists = True
                    break
            if not exists:
                process_sobj = SearchType.create("config/process")
                process_sobj.set_value("pipeline_code", pipeline_code)
                process_sobj.set_value("process", process_name)
            
            attrs = pipeline.get_process_attrs(process_name)
            color = attrs.get('color')
            if color:
                process_sobj.set_value("color", color)

            process_sobj.set_value("sort_order", count)
            process_sobj.commit()
            count += 1


        # delete obsolete
        obsolete = set(existing_names) - set(process_names)
        if obsolete:
            for obsolete_name in obsolete:
                for process_sobj in process_sobjs:
                    # delete it
                    if process_sobj.get_value("process") == obsolete_name:
                        process_sobj.delete()
                        break

        """




class ProcessCopyCmd(Command):
    '''Deep process copy'''

    def execute(my):

        pipeline_code = my.kwargs.get("pipeline_code")
        process = my.kwargs.get("process")


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

    def execute(my):
        pass


