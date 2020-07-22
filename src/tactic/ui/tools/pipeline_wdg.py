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

__all__ = ['PipelineToolWdg', 'PipelineToolCanvasWdg', 'PipelineEditorWdg', 'PipelinePropertyWdg','PipelineSaveCbk',
'ConnectorInfoWdg', 'BaseInfoWdg', 'ProcessInfoWdg', 'PipelineInfoWdg', 'ProcessInfoCmd', 'ScriptSettingsWdg', 'PipelineDocumentWdg', 'PipelineDocumentItem', 'PipelineDocumentGroupLabel', 'PipelineDocumentItemWdg', 'PipelineSaveCmd', 'PipelinePropertyCbk', 'SessionalProcess', 'NewProcessInfoCmd', 'PipelineListWdg', 'NewConnectorInfoWdg']

import re
import os
import ast
import six
from tactic.ui.common import BaseRefreshWdg

from pyasm.common import Environment, Common, jsonloads
from pyasm.biz import Task, Pipeline, Project, ProjectSetting
from pyasm.command import Command
from pyasm.web import DivWdg, WebContainer, Table, SpanWdg, HtmlElement
from pyasm.search import Search, SearchType, SearchKey, SObject
from pyasm.security import Sudo
from tactic.ui.panel import FastTableLayoutWdg
from pyasm.widget import SwapDisplayWdg

from pyasm.widget import ProdIconButtonWdg, IconWdg, TextWdg, CheckboxWdg, HiddenWdg, SelectWdg, TextAreaWdg


from tactic.ui.container import DialogWdg, TabWdg, SmartMenu, Menu, MenuItem, ResizableTableWdg
from tactic.ui.widget import ActionButtonWdg, SingleButtonWdg, IconButtonWdg, ButtonNewWdg
from tactic.ui.widget.button_new_wdg import ButtonNewWdg, ButtonRowWdg
from tactic.ui.input import TextInputWdg, ColorInputWdg, LookAheadTextInputWdg, ColorContainerWdg
from tactic.ui.panel import DocumentWdg, DocumentItemWdg, DocumentSaveCmd
from tactic.ui.app import AceEditorWdg

from client.tactic_client_lib import TacticServerStub

from .pipeline_canvas_wdg import PipelineCanvasWdg

class PipelineToolWdg(BaseRefreshWdg):
    '''This is the entire tool, including the sidebar and tabs, used to
    edit the various pipelines that exists'''

    ARGS_KEYS = {
        "pipeline": {
            'description': "Code of pipeline that will display on load. If no code is specified, shows message to create new pipeline.",
            'type': 'TextWdg',
            'order': 0,
            'category': 'Display'
        },
        "show_help": {
            'description': "Show or hide help button.",
            'type': 'SelectWdg',
            'order': 2,
            'category': 'Display',
            'values': 'true|false',
            'labels': 'True|False',
            'default': 'true'
        },
        "show_gear": {
            'description': "Show or hide gear menu button.",
            'type': 'SelectWdg',
            'order': 3,
            'category': 'Display',
            'values': 'true|false',
            'labels': 'True|False',
            'default': 'true'
        },
        "show_save": {
            'description': "Show or hide save button.",
            'type': 'SelectWdg',
            'order': 4,
            'category': 'Display',
            'values': 'true|false',
            'labels': 'True|False',
            'default': 'true'
        },
        "show_wrench": {
            'description': "Show or hide wrench node panel toggle button.",
            'type': 'SelectWdg',
            'order': 5,
            'category': 'Display',
            'values': 'true|false',
            'labels': 'True|False',
            'default': 'true'
        },
        "left_sidebar_default": {
            'description': "Default display for left sidebar.",
            'type': 'SelectWdg',
            'order': 6,
            'category': 'Display',
            'values': 'nodes|pipelines',
            'labels': 'Node Types|Pipelines',
            'default': 'pipelines'
        },

    }

    def init(self):
        # to display pipelines of a certain search_type on load
        self.search_type = self.kwargs.get('search_type')
        self.search_key = self.kwargs.get('search_key')


    def get_styles(self):

        styles = HtmlElement.style()
        background = styles.get_color("background")
        color = styles.get_color("color")
        colors = {
                "color": color,
                "background": background,
                "border": styles.get_color("table_border")
        }

        styles.add('''

            .spt_pipeline_tool_left {
                width: 200px;
                height: 100%%;
                position: absolute;
                left: 0px;
                transition: .25s;
                border: 1px solid %(border)s;
                border-width: 0px 1px 1px 1px;
            }

            .spt_pipeline_tool_right {
                width: calc(100%% - 200px);
                height: 100%%;
                padding: 0 2px;
                overflow-x: hidden;
                overflow-y: auto;
                position: relative;
                margin-left: 200px;
                transition: .25s;
            }

            .spt_pipeline_editor_start {
                height: 100%%;
                width: 100%%;
                display: flex;
                justify-content: center;
                align-items: center;
            }

            .spt_pipeline_tool_info {
                width: 400px;
                position: absolute;
                right: -400px;
                transition: 0.25s;
                top: 33px;
                bottom: 0px;
                border: 1px solid %(border)s;
                padding: 20px 0;
                border-width: 1px 0px 1px 1px;
                background: %(background)s;
                overflow-y: auto;
                z-index: 150;
            }

            .spt_pipeline_tool_top .search-results {
                position: absolute;
                right: 9;
                height: 144px;
                width: 163px;
                background: %(background)s;
                border: 1px solid %(border)s;
                box-shadow: 0px 2px 4px 0px #ccc;
                z-index: 1000;
                top: 29;
                overflow-y: auto;
            }

            .spt_pipeline_tool_top .search-result {
                width: 100%%;
                height: 32px;
                border-bottom: 1px solid %(border)s;
                display: flex;
                align-items: center;
                padding: 7px 6px;
                overflow-x: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
                display: block;
            }

            .spt_pipeline_tool_top .search-result.hovered {
                background: #eee;
            }

            .spt_pipeline_tool_top .search-result.selected {
                background: #eee;
            }

            .spt_pipeline_tool_top .search-result.search-result-template {
                display: none;
            }

            .spt_pipeline_tool_left_header {
                display: flex;
                align-items: center;
                font-size: 14px;
                color: #7E7E7E;
                margin-left: 5px;
            }

            .spt_pipeline_tool_left_header select {
                margin: 5px;
            }

            .spt_app_template_input_container {
                position: absolute;
                width: 200px;
                height: 60px;
                background: %(background)s;
                box-shadow: 0px 2px 4px 0px #ccc;
                border: 1px solid %(border)s;
                border-radius: 3px;
                padding: 5px;
                font-size: 10px;
                color: #7e7e7e;
            }

            .spt_pipeline_tool_top .spt_pipeline_toolbar {
                border: 1px solid %(border)s;
                border-width: 0 0 1 0;
                height: 33px;

                display: flex;
                align-items: center;
            }

            .spt_pipeline_tool_top .spt_hide_sidebar {
                padding: 5px;
                height: 100%%;
                border-right: 1px solid %(border)s;
            }

            .spt_pipeline_tool_top .toolbar-icon:hover {
                background: #eee;
            }

            .spt_pipeline_tool_top .full-centered {
                display: flex;
                align-items: center;
                justify-content: center;
            }

            .spt_pipeline_tool_top .toolbar-icon {
                width: 20px;
                color: grey;
            }

            .spt_pipeline_tool_top .spt_show_sidebar {
                height: 26px;
                border: 1px solid %(border)s;
                position: absolute;
                left: 3px;
                top: 1px;
                background: %(background)s;
            }

            .spt_pipeline_tool_top .spt_pipeline_type_search {
                border: 0px;
                height: 100%%;
                padding: 6px 8px;
                width: 100%%;
                border-right: 1px solid %(border)s;
            }

            .spt_pipeline_tool_top .spt_toolbar_content:not(.selected) {
                display: none;
            }

            .spt_pipeline_tool_top .document-icon {
                width: 18px;
                height: 18px;
                font-size: 11px;
            }

            .spt_pipeline_tool_top .floating-icon {
                background: %(background)s;
                color: grey;
                border-radius: 2px;
                border: 1px solid %(border)s;
            }

            .spt_pipeline_tool_top_container {
                display: flex;
                height: 100%%;
                width: 100%%;
                overflow: hidden;
                background: %(background)s;
                position: relative;
            }

            .spt_pipeline_list_top {
                height: calc(100%% - 33px);
                overflow-y: auto;

            }

            .spt_pipeline_nodes {
                overflow-y: auto;
                height: calc(100%% - 33px);
            }

            ''' % colors)

        return styles


    def get_display(self):

        top = self.top
        self.set_as_panel(top)
        top.add_class("spt_pipeline_tool_top")
        top.add_behavior({
            "type": "listen",
            "event_name": "delete|sthpw/pipeline",
            "cbjs_action": '''
            var on_complete = function() {
                window.onresize();
            }
            spt.panel.refresh_element(bvr.src_el, {}, {callback: on_complete});

            '''
        })

        inner = DivWdg()
        inner.add(self.get_styles())
        top.add(inner)

        top.add_behavior( {
            'type': 'load',
            'cbjs_action': '''
            // Resize canvas
            if (window.onresize) {
                window.onresize();
            }

            '''
        } )

        show_pipelines = self.kwargs.get("show_pipeline_list")


        if True:
            container = DivWdg()
            container.add_class("spt_pipeline_tool_top_container")

            inner.add(container)

            if show_pipelines not in [False, 'false']:
                left = DivWdg()
                container.add(left)
                left.add_class("spt_pipeline_tool_left")

            right = DivWdg()
            right.add_class("spt_pipeline_tool_right")
            container.add(right)

            info = DivWdg()
            container.add(info)


            node_results = DivWdg()
            container.add(node_results)
            node_results.add_class("spt_node_search_results")
            node_results.add_class("search-results")
            node_results.add_style("display: none")

            node_result_template = DivWdg()
            node_results.add(node_result_template)
            node_result_template.add_class("spt_node_search_item")
            node_result_template.add_class("search-result-template")
            node_result_template.add_class("search-result")
            node_result_template.add_class("hand")

            node_result_template.add_behavior({
                'type': 'mouseenter',
                'cbjs_action': '''

                bvr.src_el.addClass("hovered");

                '''
                })

            node_result_template.add_behavior({
                'type': 'mouseleave',
                'cbjs_action': '''

                bvr.src_el.removeClass("hovered");

                '''
                })


            node_results.add_behavior({
                'type': 'load',
                'cbjs_action': '''

                bvr.src_el.on_complete = function(el) {
                    el.setStyle("display", "none");
                    var top = el.getParent(".spt_pipeline_tool_top");
                    top.getElement(".spt_node_search").blur();
                }

                '''
                })

            pipeline_code = self.kwargs.get("pipeline") or "__WIDGET_UNKNOWN__"
            inputs = {
                    "pipeline_code": pipeline_code,
                    "process": "__WIDGET_UNKNOWN__",
                    "node_type": '__WIDGET_UNKNOWN__',
                    "properties": "__WIDGET_UNKNOWN__",
                }
            widget_key = container.generate_widget_key('tactic.ui.tools.ProcessInfoWdg', inputs=inputs, attr="info")
            container.add_relay_behavior({
                'type': 'click',
                'bvr_match_class': 'spt_node_search_result',
                'widget_key': widget_key,
                'cbjs_action': '''

                var top = bvr.src_el.getParent(".spt_pipeline_tool_top");
                spt.pipeline.set_top(top.getElement(".spt_pipeline_top"));

                var inp = top.getElement(".spt_node_search");
                inp.value = bvr.src_el.innerText;

                var node = spt.pipeline.get_node_by_name(bvr.src_el.innerText);
                spt.pipeline.fit_to_node(node);

                // reuse code instead?
                spt.pipeline.select_single_node(node);

                // zoom up
                spt.pipeline.set_scale(1.25);

                var properties = spt.pipeline.get_node_properties(node);

                var node_name = spt.pipeline.get_node_name(node);
                var group_name = spt.pipeline.get_current_group();
                var info = top.getElement(".spt_pipeline_tool_info");
                if (!info) return;

                var node_type = spt.pipeline.get_node_type(node);
                if (node.hasClass("spt_pipeline_unknown")) {
                    node_type = "unknown";
                }

                var class_name = bvr.widget_key;
                var kwargs = {
                    pipeline_code: group_name,
                    process: node_name,
                    node_type: node_type,
                    properties: properties
                }
                document.activeElement.blur();
                spt.pipeline.set_info_node(node);

                var callback = function() {
                    spt.named_events.fire_event('pipeline|show_info', {});
                }
                spt.panel.load(info, class_name, kwargs, {}, {callback: callback});

                var results = bvr.src_el.getParent(".spt_node_search_results");
                results.on_complete(results);

                '''
                })





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

                let start_el = top.getElement(".spt_pipeline_editor_start");
                spt.pipeline.hide_start(start_el);

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

                // used to show sidebar here? doesnt seem like it affect anything

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

        let start = top.getElement(".spt_pipeline_editor_start");
        spt.pipeline.hide_start(start_el);

        spt.pipeline.clear_canvas();
        spt.pipeline.import_pipeline(group_name);

        '''

        } )


        self.settings = self.kwargs.get('settings') or []
        if self.settings and isinstance(self.settings, basestring):
            self.settings = self.settings.split("|")




        if show_pipelines not in [False, 'false']:

            expression = self.kwargs.get("expression")

            # TOOLBAR--------------
            toolbar = DivWdg()
            left.add(toolbar)
            toolbar.add_class("spt_pipeline_toolbar")

            collapse_button = DivWdg()
            toolbar.add(collapse_button)
            collapse_button.add_class("full-centered spt_hide_sidebar toolbar-icon hand")
            collapse_button.add("<i class='fa fa-caret-left'></i>")

            collapse_button.add_behavior({
                'type': 'click',
                'cbjs_action': '''

                var toolTop = bvr.src_el.getParent(".spt_pipeline_tool_top");
                var left = toolTop.getElement(".spt_pipeline_tool_left");
                var right = toolTop.getElement(".spt_pipeline_tool_right");

                right.addClass("spt_left_toggle");

                left.setStyle("margin-left", "-21%");
                left.setStyle("opacity", "0");
                right.setStyle("margin-left", "0px");
                right.setStyle("width", "100%");
                left.gone = true;
                setTimeout(function(){
                    left.setStyle("z-index", "-1");
                }, 250);

                var show_icon = toolTop.getElement(".spt_show_sidebar");
                show_icon.setStyle("display", "");

                '''})

            show_button = DivWdg()
            container.add(show_button)
            show_button.add_class("full-centered spt_show_sidebar toolbar-icon hand")
            show_button.add("<i class='fa fa-caret-right'></i>")
            show_button.add_style("display: none")
            show_button.add_behavior({
                'type': 'click',
                'cbjs_action': '''

                var toolTop = bvr.src_el.getParent(".spt_pipeline_tool_top");
                var left = toolTop.getElement(".spt_pipeline_tool_left");
                var right = toolTop.getElement(".spt_pipeline_tool_right");

                right.removeClass("spt_left_toggle");

                left.setStyle("margin-left", "0px");
                left.setStyle("opacity", "1");
                right.setStyle("margin-left", "200px");
                right.setStyle("width", "calc(100% - 200px)");
                left.gone = false;
                setTimeout(function(){
                    left.setStyle("z-index", "");
                }, 250);

                bvr.src_el.setStyle("display", "none");

                '''})

            #### document toolbar content
            toolbar_icons = DivWdg()
            toolbar.add(toolbar_icons)
            toolbar_icons.add_class("spt_toolbar_icons spt_toolbar_content")

            toggle_button = PipelineDocumentGroupLabel.get_button_wdg("spt_pipeline_toggle_btn", "Toggle Workflow List", "fa-list-ul")
            toolbar_icons.add(toggle_button)
            toggle_button.add_style("margin: 0 3px")

            list_kwargs = {
                "save_event": save_event,
                "save_new_event": save_new_event,
                "settings": self.settings,
                "expression": expression
            }
            toolbar_icons.generate_widget_key("tactic.ui.tools.PipelineListWdg", inputs=list_kwargs, attr="doc")
            toolbar_icons.generate_widget_key("tactic.ui.tools.PipelineDocumentWdg", attr="list")
            toggle_button.add_behavior({
                'type': 'click',
                'widget_key': widget_key,
                'cbjs_action': '''

                var top = bvr.src_el.getParent(".spt_pipeline_tool_top");
                var left = top.getElement(".spt_pipeline_tool_left");
                var content = left.getElement(".spt_pipeline_tool_left_content");
                var icon = bvr.src_el.getParent(".spt_toolbar_content");
                var list_widget_key = icon.getAttribute("SPT_LIST_WIDGET_KEY");
                var doc_widget_key = icon.getAttribute("SPT_DOC_WIDGET_KEY");

                if (content.getAttribute("mode") == "list") {
                    content.setAttribute("mode", "document");
                    var class_name = list_widget_key || 'tactic.ui.tools.PipelineDocumentWdg';
                    spt.panel.load(content, class_name);
                } else if (content.getAttribute("mode") == "document") {
                    content.setAttribute("mode", "list");
                    var class_name = doc_widget_key || 'tactic.ui.tools.PipelineListWdg';
                    spt.panel.load(content, class_name, content.list_kwargs);
                }

                '''
            })

            #### process select toolbar content
            type_search = HtmlElement.text()
            toolbar.add(type_search)
            type_search.add_class("spt_pipeline_type_search spt_toolbar_content")
            type_search.add_attr("placeholder", "Search for process nodes...")

            type_search.add_behavior({
                'type': 'keyup',
                'cbjs_action': '''

                var top = bvr.src_el.getParent(".spt_pipeline_tool_top");
                var typeTop = top.getElement(".spt_process_select_top");
                var containers = typeTop.getElements(".spt_custom_node_container");

                containers.forEach(function(container) {
                    if (container.getAttribute("spt_node_type").contains(bvr.src_el.value))
                        container.setStyle("display", "");
                    else
                        container.setStyle("display", "none")
                });


                '''
                })

            # --------------

            pipeline_list_top = DivWdg()
            left.add(pipeline_list_top)
            pipeline_list_top.add_class("spt_pipeline_list_top")



            pipeline_list_content = DivWdg()
            pipeline_list_top.add(pipeline_list_content)
            pipeline_list_content.add_class("spt_pipeline_tool_left_content")

            pipeline_list_content.add_behavior({
                'type': 'load',
                'list_kwargs': list_kwargs,
                'cbjs_action': '''

                bvr.src_el.list_kwargs = bvr.list_kwargs;

                '''
                })


            pipeline_list = PipelineDocumentWdg()
            pipeline_list_content.add_attr("mode", "document")

            # By default, show pipeline document
            pipeline_list_content.add(pipeline_list)

            process_type_widget = PipelineProcessTypeWdg()
            process_type_widget.add_class("spt_pipeline_nodes")
            left.add(process_type_widget)


            sidebar_default = self.kwargs.get("left_sidebar_default")
            if not sidebar_default:
                sidebar_default == "pipelines"

            if sidebar_default == "nodes":
                pipeline_list_top.add_style("display", "none")

                type_search.add_class("selected")
            else:
                process_type_widget.add_style("display: none")

                toolbar_icons.add_class("selected")







        width = "100%"
        show_gear=self.kwargs.get('show_gear')
        show_help = self.kwargs.get('show_help') or True
        show_wrench = self.kwargs.get("show_wrench")
        show_save = self.kwargs.get("show_save")
        pipeline_wdg = PipelineEditorWdg(
            height=self.kwargs.get('height'),
            width=width,
            save_new_event=save_new_event,
            show_gear=show_gear,
            show_help=show_help,
            show_wrench=show_wrench,
            show_save=show_save,
            pipeline_code=pipeline_code
        )

        pipeline_wdg.add_style("display", "none")
        right.add(pipeline_wdg)

        start_div = DivWdg()
        start_div.add_class("spt_pipeline_editor_start")
        right.add(start_div)

        msg_div = HtmlElement.p()
        msg_div.add_class("lead")
        msg_div.add("Select a workflow or create a new one")

        start_div.add(msg_div)




        # NOTE: the canvas in PipelineCanvasWdg requires a set size ... it does not respond
        # well to sizes like 100% or auto.  Unless this is fixed, we cannot have a table
        # responsively respond to a changing window size.

        #info.add_style("display: none")
        info.add_class("spt_pipeline_tool_info")
        info.add_class("spt_panel")

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


        inner.add_behavior( {
        'type': 'listen',
        'event_name': 'pipeline|show_info',
        'cbjs_action': '''

        var top = bvr.src_el.getParent(".spt_pipeline_tool_top");
        top.hot_key_state = false;
        var info = top.getElement(".spt_pipeline_tool_info");
        info.setStyle("right", "0px");
        var top = bvr.src_el.getParent(".spt_pipeline_top");


        var input = bvr.src_el.getElement(".spt_hot_key");

        input.blur();

        '''

        } )


        inner.add_behavior( {
        'type': 'listen',
        'event_name': 'pipeline|hide_info',
        'cbjs_action': '''

        var top = bvr.src_el.getParent(".spt_pipeline_tool_top");
        var info = top.getElement(".spt_pipeline_tool_info");
        info.setStyle("right", "-400px");

        '''

        } )


        app_template_input_container = DivWdg()
        right.add(app_template_input_container)
        app_template_input_container.add_class("spt_app_template_input_container")

        app_template_input_container.add("Default Template")

        app_template_input = TextInputWdg(name="default_template", height="34", width="100%")
        app_template_input_container.add(app_template_input)

        app_template_input_container.add_style("display", "none")
        app_template_input_container.add_behavior({
            'type': 'load',
            'cbjs_action': '''

            bvr.src_el.on_complete = function() {
                spt.hide(bvr.src_el);
            }

            '''
            })


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
        if self.settings and isinstance(self.settings, six.string_types):
            self.settings = self.settings.split("|")


    def get_display(self):

        top = self.top
        top.add_class("spt_pipeline_list")
        self.set_as_panel(top)
        top.add_style("padding: 0px 0px")

        title_div = DivWdg()

        button = ActionButtonWdg(title="+", tip="Add a new workflow", size='small')

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
        pipelines_div.add_style("width: 100%")
        pipelines_div.add_style("height: auto")

        inner = DivWdg()
        pipelines_div.add(inner)
        inner.add_class("spt_pipeline_list_top")

        inner.add_style("display: flex")
        inner.add_style("flex-direction: column")

        inner.add_style("width: 100%")
        inner.add_style("height: auto")


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
                    if search.column_exists("parent_code"):
                        search.add_filter("parent_code", "NULL", quoted=False, op="is")

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
                if search.column_exists("parent_code"):
                    search.add_filter("parent_code", "NULL", quoted=False, op="is")

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

        except Exception as e:
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
            search.add_op("begin")
            search.add_filter("type", "template", op="!=")
            search.add_filter("type", "NULL", op='is', quoted=False)
            search.add_op("or")
            pipelines = search.get_sobjects()

            if pipelines:

                title = DivWdg()
                inner.add(title)
                title.add_style("display: flex")
                title.add_style("align-items: center")

                swap = SwapDisplayWdg()
                title.add(swap)

                title.add("<div><b>Task Status Workflows</b> <i>(%s)</i></div>" % len(pipelines))
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

                title = DivWdg()
                inner.add(title)

                title.add_style("display: flex")
                title.add_style("align-items: center")

                swap = SwapDisplayWdg()
                title.add(swap)


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

                title = DivWdg()
                inner.add(title)

                title.add_style("display: flex")
                title.add_style("align-items: center")

                swap = SwapDisplayWdg()
                title.add(swap)

                title.add("<b>Templates</b> <i>(%s)</i><br/>" % len(pipelines))


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

        color = pipeline_div.get_color("background", -10)
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
            spt.pipeline.hide_start(start_el);

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

            //spt.named_events.fire_event('pipeline|hide_info', {});

            editor_top.removeClass("spt_has_changes");


            spt.command.clear();


        };

        var save = function(){
            editor_top.removeClass("spt_has_changes");
            var wrapper = editor_top.getElement(".spt_pipeline_wrapper");
            spt.pipeline.init_cbk(wrapper);

            var group_name = spt.pipeline.get_current_group();

            var data = spt.pipeline.get_data();
            var color = data.colors[group_name];

            var group = spt.pipeline.get_group(group_name);
            var default_template = data.default_templates[group_name];
            var node_index = group.get_data("node_index");
            var pipeline_data = {
                default_template: default_template,
                node_index: node_index
            };

            server = TacticServerStub.get();
            spt.app_busy.show("Saving project-specific pipeline ["+group_name+"]",null);

            var xml = spt.pipeline.export_group(group_name);
            var search_key = server.build_search_key("sthpw/pipeline", group_name);
            try {
                var args = {
                    search_key: search_key,
                    pipeline: xml,
                    color: color,
                    project_code: bvr.project_code,
                    pipeline_data: pipeline_data
                };
                server.execute_cmd('tactic.ui.tools.PipelineSaveCbk', args);
            } catch(e) {
                spt.alert(spt.exception.handler(e));
            }

            spt.named_events.fire_event('pipeline|save', {});

            spt.app_busy.hide();

            editor_top.removeClass("spt_has_changes");

            spt.command.clear();

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

        color = pipeline_div.get_color("background", -20)

        style = HtmlElement.style()
        pipeline_div.add(style)
        style.add('''
        .spt_pipeline_tool_left .spt_pipeline_selected {
            background: %s;
        }
        ''' % color)


        pipeline_div.add_behavior( {'type': 'click_up',

            'event': 'pipeline_%s|click' %pipeline_code,
            'cbjs_action': '''
             var top = bvr.src_el.getParent(".spt_pipeline_list_top");
             var items = top.getElements(".spt_pipeline_selected");

             if (items){
                 for (var i=0; i<items.length; i++) {
                     items[i].removeClass("spt_pipeline_selected");
                 }
             }

             bvr.src_el.addClass("spt_pipeline_selected");
             spt.named_events.fire_event(bvr.event, bvr);
             spt.command.clear();
             spt.pipeline.fit_to_canvas();

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
        div = DivWdg()
        inputs =  {
            'process': "__WIDGET_UNKNOWN__",
            'node_type': "__WIDGET_UNKNOWN__",
            'pipeline_code': '__WIDGET_UNKNOWN__',
            'properties': "__WIDGET_UNKNOWN__"
            }
        widget_key = div.generate_widget_key('tactic.ui.tools.ProcessInfoWdg', inputs=inputs)

        behavior = {
        'type': 'click_up',
        'widget_key': widget_key,
        'cbjs_action': '''
        spt.pipeline.init(bvr);
        var node = bvr.src_el;

        var properties = spt.pipeline.get_node_properties(node);

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

        var class_name = bvr.widget_key;
        var kwargs = {
            pipeline_code: group_name,
            process: node_name,
            node_type: node_type,
            properties: properties
        }
        document.activeElement.blur();
        spt.pipeline.set_info_node(node);
        //spt.pipeline.fit_to_node(node);

        var callback = function() {
            spt.named_events.fire_event('pipeline|show_info', {});
        }
        spt.panel.load(info, class_name, kwargs, {}, {callback: callback});

        '''
        }


        return [behavior]


    def get_canvas_behaviors(self):

        div = DivWdg()
        inputs = {
            'to_type': '__WIDGET_UNKNOWN__',
            'pipeline_code': '__WIDGET_UNKNOWN__',
            'from_type': '__WIDGET_UNKNOWN__',
            'from_node': '__WIDGET_UNKNOWN__',
            'to_node': '__WIDGET_UNKNOWN__'
        }
        widget_key = div.generate_widget_key('tactic.ui.tools.NewConnectorInfoWdg', inputs=inputs)
        behavior = {
        'type': 'click_up',
        'widget_key': widget_key,
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

            to_attr = connector.get_attr("to_attr");
            from_attr = connector.get_attr("from_attr");
            draw_attr = true;

            connector.is_selected = true;
            connector.draw_spline(draw_attr);

            var from_node = connector.get_from_node();
            var to_node = connector.get_to_node();

            var group_name = spt.pipeline.get_current_group();

            var class_name = bvr.widget_key;
            var kwargs = {
                pipeline_code: group_name,
                from_node: from_node.spt_name,
                from_type: from_node.spt_type,
                from_attr: from_attr,
                to_node: to_node.spt_name,
                to_type: to_node.spt_type,
                to_attr: to_attr,
            }
            var callback = function() {
                spt.named_events.fire_event('pipeline|show_info', {});
            }
            spt.panel.load(info, class_name, kwargs, {}, {callback: callback});
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
        top.add( self.get_default_template_wdg(pipeline) )


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
            'type': 'load',
            'cbjs_action': '''

            var node = spt.pipeline.get_info_node();

            var data = spt.pipeline.get_data();
            var group_name = spt.pipeline.get_current_group();
            var desc = data.descriptions[group_name] || "";
            bvr.src_el.value = desc;

            '''
        } )

        text.add_behavior( {
            'type': 'blur',
            'search_key': pipeline.get_search_key(),
            'cbjs_action': '''
            var desc = bvr.src_el.value;
            var node = spt.pipeline.get_info_node();

            var group_name = spt.pipeline.get_current_group();
            var group = spt.pipeline.get_group(group_name);
            group.set_description(desc);

            spt.named_events.fire_event('pipeline|change', {});
            '''
        } )

        return desc_div




    def get_color_wdg(self, pipeline):
        color = pipeline.get_value("color")
        div = DivWdg()
        div.add_class("spt_color_wdg")
        div.add_style("margin: 10px 10px 20px 10px")
        div.add("<div><b>Color:</b></div>")

        container = ColorContainerWdg()
        div.add(container)

        color_wdg = container.get_color_wdg()

        color_wdg.add_behavior( {
            'type': 'load',
            'cbjs_action': '''

            var data = spt.pipeline.get_data();
            var group_name = spt.pipeline.get_current_group();
            var group = spt.pipeline.get_group(group_name);
            color = group.get_color();

            bvr.src_el.value = color;

            '''
        } )

        color_wdg.add_behavior( {
            'type': 'change',
            'cbjs_action': '''
            var color = bvr.src_el.value;
            //bvr.src_el.setStyle("background", color);

            var top = bvr.src_el.getParent(".spt_pipeline_tool_top");
            var wrapper = top.getElement(".spt_pipeline_wrapper");
            spt.pipeline.init_cbk(wrapper);

            var group_name = spt.pipeline.get_current_group();
            var group = spt.pipeline.get_group(group_name);
            group.set_color(color);

            spt.named_events.fire_event('pipeline|change', {});

            '''
        } )

        div.add(HtmlElement.style('''

            .spt_color_wdg .spt_color_container {
                width: 100%;
            }

            '''))


        return div



    def get_default_template_wdg(self, pipeline):
        # get template from data column
        data = pipeline.get_json_value("data", no_exception=True) or {}
        default_template = data.get("default_template") or ""

        div = DivWdg()
        div.add_class("spt_app_template_wdg")
        div.add_style("margin: 10px 10px 20px 10px")
        div.add("<div><b>Default Template:</b></div>")

        text = TextInputWdg(name="default_template")
        div.add(text)
        text.set_value(default_template)

        text.add_behavior( {
            'type': 'load',
            'cbjs_action': '''

            var group_name = spt.pipeline.get_current_group();
            var data = spt.pipeline.get_data();
            default_template = data.default_templates[group_name];

            if (default_template)
                bvr.src_el.value = default_template;

            '''
        } )

        text.add_behavior( {
            'type': 'blur',
            'cbjs_action': '''

            var default_template = bvr.src_el.value;
            var group_name = spt.pipeline.get_current_group();
            var group = spt.pipeline.get_group(group_name);
            group.set_data("default_template", default_template);

            spt.named_events.fire_event('pipeline|change', {});

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

        from_type = self.kwargs.get("from_type")
        to_type = self.kwargs.get("to_type")

        #info_wdg = DivWdg()
        #top.add(info_wdg)
        #info_wdg.add("From <b>%s</b> to <b>%s</b>" % (from_node, to_node))
        #info_wdg.add_style("margin: 10px")


        table = Table()
        top.add(table)
        table.add_style("width: 100%")
        table.add_style("margin: 0px 5px 5px 10px")

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
        text.add_behavior({
            'type': 'blur',
            'kwargs': self.kwargs,
            'cbjs_action': '''

            var value = bvr.src_el.value

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

            connector.set_attr("from_attr", value);

            '''
            })

        left.add("<br/>"*3)
        left.add("Standard Attributes")
        left.add("<hr/>")


        out_attrs = ['output','yes','no','true','false']

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

        text.add_behavior({
            'type': 'blur',
            'kwargs': self.kwargs,
            'cbjs_action': '''

            var value = bvr.src_el.value

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

            connector.set_attr("to_attr", value);

            '''
            })

        right.add("<br/>"*3)
        right.add("<hr/>")



        in_attrs = ['input','review']

        right_div = DivWdg()
        right.add(right_div)
        for attr in in_attrs:
            attr_div = DivWdg()
            right_div.add(attr_div)
            attr_div.add(attr)
            attr_div.add_style("padding: 3px")




        save = ActionButtonWdg(title="Save")
        save.add_style("float: right")
        #top.add(save)
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


class NewConnectorInfoWdg(BaseRefreshWdg):

    def get_styles(self):

        styles = HtmlElement.style('''

            .spt_pipeline_connector_info {
               min-width: 300px;
            }

            .spt_pipeline_connector_info .spt_info_header {
                text-transform: uppercase;
                color: #333;
                font-size: 1.2em;
                padding: 5px;
                border-bottom: 1px solid #ccc;
                background: #eee;
            }

            .spt_pipeline_connector_info .spt_info_content_node_labels {
                display: flex;
                justify-content: space-between;
                padding: 5px;
            }

            .spt_pipeline_connector_info .spt_info_content_node_labels div{
                font-weight: bold;
            }

            .spt_pipeline_connector_info .spt_info_content_nodes {
                display: flex;
                justify-content: space-between;
            }

            .spt_pipeline_connector_info .spt_info_content_node {
                display: flex;
                justify-content: center;
                align-items: center;
                min-width: 100px;
                height: 36px;
                font-size: 10px;
                border: 1px solid #ccc;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }

            .spt_pipeline_connector_info .spt_info_content_node.from-node {
                border-width: 1px 1px 1px 0;
                border-radius: 0 3px 3px 0;
            }

            .spt_pipeline_connector_info .spt_info_content_node.to-node {
                border-width: 1px 0 1px 1px;
                border-radius: 3px 0px 0px 3px;
            }

            .spt_pipeline_connector_info .spt_info_content_line {
                margin: 0 50px;
                height: 30px;
                border: 1px solid #ccc;
                border-width: 0 1px 1px 1px;
                border-radius: 0 0 3px 3px;

                position: relative;
            }

            .spt_pipeline_connector_info .spt_info_content_arrow {
                position: absolute;
                left: 145px;
                bottom: -9px;

                color: #ccc;
                font-size: 13px;
            }

            .spt_pipeline_connector_info .spt_info_content_inputs {
                display: grid;
                grid-template-columns: 50% 50%;
                margin-top: 20px;
            }

            .spt_pipeline_connector_info .spt_info_content_input_column {
                display: flex;
                align-items: center;
                flex-direction: column;
            }

            .spt_pipeline_connector_info .spt_text_container {
                width: 150px;
                font-size: 10px;
                color: #ccc;
            }

            .spt_pipeline_connector_info .spt_attributes_container {
                width: 170px;
                margin-top: 10px;
            }

            .spt_pipeline_connector_info .spt_stream_attribute.spt_stream_attribute_template {
                display: none;
            }

            .spt_pipeline_connector_info .spt_stream_attribute {
                color: white;
                border-radius: 8px;
                display: inline-block;
                padding: 3px 8px 2px;
                margin: 3px 4px;
                cursor: hand;

                position: relative;
            }

            .spt_pipeline_connector_info .spt_info_content_input_column[spt_column='left'] .spt_stream_attribute {
                background: green;
            }

            .spt_pipeline_connector_info .spt_info_content_input_column[spt_column='right'] .spt_stream_attribute {
                background: red;
            }

            .spt_pipeline_connector_info .spt_info_content_input_column[spt_column='left'] .spt_stream_attribute:hover {
                background: darkgreen;
            }

            .spt_pipeline_connector_info .spt_info_content_input_column[spt_column='right'] .spt_stream_attribute:hover {
                background: darkred;
            }

            .spt_pipeline_connector_info .spt_close_wdg {

            }



            ''')

        return styles


    def get_display(self):

        top = self.top
        top.add_class("spt_pipeline_connector_info")
        top.add_behavior({
            'type': 'load',
            'kwargs': self.kwargs,
            'cbjs_action': self.get_onload_js()
            })

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


        title_wdg = DivWdg()
        top.add(title_wdg)
        title_wdg.add_class("spt_info_header")
        title_wdg.add("Connector")

        top.add("<br/>")


        self.from_node = self.kwargs.get("from_node")
        self.to_node = self.kwargs.get("to_node")

        from_type = self.kwargs.get("from_type")
        to_type = self.kwargs.get("to_type")

        left_selected = self.kwargs.get("from_attr")
        if not left_selected:
            left_selected = "output"
        right_selected = self.kwargs.get("to_attr")
        if not right_selected:
            right_selected = "input"


        content = self.get_content_header()
        top.add(content)
        content.add_class("spt_info_content")

        # node connector thing
        content_header = DivWdg()
        content.add(content_header)

        # inputs
        content_inputs = DivWdg()
        content.add(content_inputs)
        content_inputs.add_class("spt_info_content_inputs")

        ##### left -------------------------------------------

        left = DivWdg()
        content_inputs.add(left)
        left.add_class("spt_info_content_input_column")
        left.add_attr("spt_column", "left")

        text_container = DivWdg()
        left.add(text_container)
        text_container.add_class("spt_text_container")

        text = TextInputWdg(name="left", width=150)
        text_container.add(text)
        text.add_class("spt_output_attr")
        if left_selected:
            text.set_value(left_selected)
        text.add_behavior({
            'type': 'blur',
            'cbjs_action': '''

            var top = bvr.src_el.getParent(".spt_pipeline_connector_info");
            var value = bvr.src_el.value;

            var connector = top.connector;
            if (!connector) return;

            connector.set_attr("from_attr", value);

            '''
            })

        text_container.add("Output Stream")

        left_attributes = ['output','yes','no','true','false']
        attributes_container = self.get_attributes_container(left_attributes)
        left.add(attributes_container)

        ##### right -------------------------------------------

        right = DivWdg()
        content_inputs.add(right)
        right.add_class("spt_info_content_input_column")
        right.add_attr("spt_column", "right")

        text_container = DivWdg()
        right.add(text_container)
        text_container.add_class("spt_text_container")

        text = TextInputWdg(name="right", width=150)
        text_container.add(text)
        text.add_class("spt_input_attr")
        if right_selected:
            text.set_value(right_selected)

        text.add_behavior({
            'type': 'blur',
            'cbjs_action': '''

            var top = bvr.src_el.getParent(".spt_pipeline_connector_info");
            var value = bvr.src_el.value;

            var connector = top.connector;
            if (!connector) return;

            connector.set_attr("to_attr", value);

            '''
            })

        text_container.add("Input Stream")

        right_attributes = ['input','review']
        attributes_container = self.get_attributes_container(right_attributes)
        right.add(attributes_container)

        top.add(self.get_styles())

        return top


    def get_content_header(self):

        content_header = DivWdg()
        content_header.add_class("spt_info_content_header")

        ##### node labels

        node_labels_wdg = DivWdg()
        content_header.add(node_labels_wdg)
        node_labels_wdg.add_class("spt_info_content_node_labels")

        from_node_label = DivWdg("Incoming node")
        node_labels_wdg.add(from_node_label)
        to_node_label = DivWdg("Outgoing node")
        node_labels_wdg.add(to_node_label)

        ##### nodes

        nodes_wdg = DivWdg()
        content_header.add(nodes_wdg)
        nodes_wdg.add_class("spt_info_content_nodes")

        from_node_wdg = DivWdg(self.from_node)
        from_node_wdg.add_class("spt_info_content_node")
        from_node_wdg.add_class("from-node")
        from_node_wdg.add_attr("title", self.from_node)

        to_node_wdg = DivWdg(self.to_node)
        to_node_wdg.add_class("spt_info_content_node")
        to_node_wdg.add_class("to-node")
        from_node_wdg.add_attr("title", self.to_node)

        nodes_wdg.add(from_node_wdg)
        nodes_wdg.add(to_node_wdg)

        ##### line

        line_wdg = DivWdg()
        content_header.add(line_wdg)
        line_wdg.add_class("spt_info_content_line")

        arrow = DivWdg(">")
        line_wdg.add(arrow)
        arrow.add_class("spt_info_content_arrow")

        return content_header


    def get_attributes_container(self, attributes):

        attributes_container = DivWdg()
        attributes_container.add_class("spt_attributes_container")

        attribute_wdg = DivWdg()
        attributes_container.add(attribute_wdg)
        attribute_wdg.add_class("spt_stream_attribute spt_stream_attribute_template")

        attribute_wdg.add_behavior({
            'type': 'click',
            'cbjs_action': '''

            var top = bvr.src_el.getParent(".spt_pipeline_connector_info");
            var column =  bvr.src_el.getParent(".spt_info_content_input_column");
            var inp = column.getElement(".spt_text_input_wdg");
            let value = bvr.src_el.getAttribute("spt_attribute");

            inp.value = value;

            var connector = top.connector;
            if (!connector) return;

            var side = column.getAttribute("spt_column");
            if (side == "right")
                connector.set_attr("to_attr", value);
            else
                connector.set_attr("from_attr", value);

            '''
            })

        ####### WIP #######
        close_button = DivWdg("<i class='fa fa-times'></i>")
        #attribute_wdg.add(close_button)
        close_button.add_class('spt_close_wdg')
        close_button.add_behavior({
            'type': 'mouseenter',
            'cbjs_action': '''



            '''
            })

        add_wdg = DivWdg()
        #attributes_container.add(add_wdg)
        add_wdg.add_class("spt_add_attribute")
        ####### WIP #######


        attributes_container.add_behavior({
            'type': 'load',
            'attributes': attributes,
            'cbjs_action': '''

            let attributes = bvr.attributes;
            let template = bvr.src_el.getElement(".spt_stream_attribute_template");

            attributes.forEach(function(attribute){
                var clone = spt.behavior.clone(template);
                clone.innerHTML += attribute;
                clone.removeClass("spt_stream_attribute_template");
                clone.setAttribute("spt_attribute", attribute)
                bvr.src_el.appendChild(clone);
            })

            '''
            })

        return attributes_container


    def get_onload_js(self):

        return '''

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

        bvr.src_el.connector = connector;

        '''




class ProcessInfoWdg(BaseRefreshWdg):

    def get_display(self):

        node_type = self.kwargs.get("node_type")

        top = self.top
        top.add_class("spt_process_info_top container")
        top.add_behavior({
            'type': 'unload',
            'cbjs_action': '''
                document.activeElement.blur();
            '''
            })
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

    def set_as_section_top(self, widget):
        widget.add_class("spt_section_top")
        SessionalProcess.add_relay_session_behavior(widget)


    def get_description_wdg(self):
        desc_div = DivWdg()

        desc_div.add_class("form-group")

        text = TextAreaWdg()
        text.set_unique_id()

        desc_div.add("<label class='bmd-label-floating' for='%s'>Description</label>" % text.get_id())
        desc_div.add(text)

        text.add_behavior( {
            'type': 'load',
            'cbjs_action': '''

            var node = spt.pipeline.get_info_node();
            if (node) {
                var desc = spt.pipeline.get_node_kwarg(node, "description");
                if (desc) bvr.src_el.value = desc;
            }

            '''
        } )

        text.add_behavior( {
            'type': 'blur',
            'cbjs_action': '''

            var node = spt.pipeline.get_info_node();
            if (node) {
                var desc = bvr.src_el.value;
                spt.pipeline.set_node_kwarg(node, "description", desc);

                spt.named_events.fire_event('pipeline|change', {});
            }

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


        title_wdg = DivWdg()

        form_group = DivWdg()
        title_wdg.add(form_group)

        form_group.add_class("form-group")

        title_edit_text = TextInputWdg(name="process", height="30px")
        title_edit_text.set_unique_id()

        form_group.add('<label for="%s" class="bmd-label-floating">Process name</label>' % title_edit_text.get_id())
        form_group.add(title_edit_text)

        title_edit_text.add_class("spt_title_edit")

        title_edit_text.add_behavior( {
            'type': 'load',
            'cbjs_action': '''

            var node = spt.pipeline.get_info_node();
            var name = spt.pipeline.get_node_name(node);
            bvr.src_el.value = name;

            '''
        } )

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

            var node = spt.pipeline.get_info_node();

            if (!bvr.src_el.value) {
                spt.alert("Node name cannot be empty");
                bvr.src_el.value = spt.pipeline.get_node_name(node);
                return;
            }

            spt.pipeline.set_node_name(node, bvr.src_el.value);
            spt.pipeline.set_node_property(node, "name", bvr.src_el.value);

            // Add edited flag
            spt.named_events.fire_event('pipeline|change', {});

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

            form_group = DivWdg()
            title_wdg.add(form_group)

            form_group.add_class("form-group")

            select = SelectWdg("node_type")
            select.set_unique_id()

            form_group.add("<label class='bmd-label-floating' for='%s'>Node Type</label>" % select.get_id())
            form_group.add(select)

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

            if node_type == "node":
                select.set_value("manual")
            else:
                select.set_value(node_type)

            select.add_behavior( {
                'type': 'change',
                'cbjs_action': '''

                var server = TacticServerStub.get();

                var node_type = bvr.src_el.value;

                // change node_type
                var node = spt.pipeline.get_selected_node();
                var process = spt.pipeline.get_node_name(node);

                node.setStyle("box-shadow", "0px 0px 15px rgba(255,0,0,0.5)");

                var pos = spt.pipeline.get_position(node);

                var group = spt.pipeline.get_group_by_node(node);
                for (var i = 0; i < group.nodes.length; i++) {
                    if (node == group.nodes[i]) {
                        group.nodes.splice(i, 1);
                        break;
                    }
                }


                var properties = spt.pipeline.get_node_properties(node) || {};

                spt.pipeline.set_info_node(new_node);
                properties.type = node_type;

                var new_node = spt.pipeline.add_node(process, pos.x, pos.y, {node_type: node_type, properties: properties});


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

                // select the new node
                spt.pipeline.select_single_node(new_node);


                spt.named_events.fire_event('pipeline|change', {});

                '''
            } )

        return title_wdg



    def get_default_kwargs(self):

        return {}


    def get_default_properties(self):

        return {}


    def initialize_session_behavior(self, info):

        kwargs = self.get_default_kwargs()
        properties = self.get_default_properties()

        info.add_behavior({
            'type': 'load',
            'kwargs': kwargs,
            'properties': properties,
            'cbjs_action': '''

            var node = spt.pipeline.get_info_node();

            var version = spt.pipeline.get_node_kwarg(node, 'version');
            if (version && version != 1)
                return;

            var properties = spt.pipeline.get_node_properties(node);
            Object.assign(bvr.properties, properties);
            spt.pipeline.set_node_properties(node, bvr.properties);

            var kwargs = spt.pipeline.get_node_kwargs(node);
            Object.assign(bvr.kwargs, kwargs);
            spt.pipeline.set_node_kwargs(node, bvr.kwargs);

            '''
        })


    def add_session_behavior(self, input_wdg, input_type, top_class, arg_name):

        # On load behavior, displays sessional value
        load_behavior = {
            'type': 'load',
            'arg_name': arg_name
        }

        cbjs_action_default = '''

        var node = spt.pipeline.get_info_node();
        var version = spt.pipeline.get_node_kwarg(node, 'version');
        if (version && version != 1)
            return;

        var toolTop = bvr.src_el.getParent(".spt_pipeline_tool_top");
        spt.pipeline.set_top(toolTop.getElement(".spt_pipeline_top"));

        '''

        load_behavior['cbjs_action'] = cbjs_action_default + '''
        spt.pipeline.set_input_value_from_kwargs(node, bvr.arg_name, bvr.src_el);
        '''

        if input_type == "select":
            load_behavior['cbjs_action'] = cbjs_action_default + '''
            spt.pipeline.set_select_value_from_kwargs(node, bvr.arg_name, bvr.src_el);
            '''
        elif input_type == "radio":
            load_behavior['cbjs_action'] = cbjs_action_default + '''
            spt.pipeline.set_radio_value_from_kwargs(node, bvr.arg_name, bvr.src_el);
            '''
        elif input_type == "checkbox":
            load_behavior['cbjs_action'] = cbjs_action_default + '''
            spt.pipeline.set_checkbox_value_from_kwargs(node, bvr.arg_name, bvr.src_el);
            '''

        input_wdg.add_behavior(load_behavior)


        # On change behavior, stores sessional value
        change_behavior = {
            'top_class': top_class,
            'arg_name': arg_name,
            'cbjs_action': '''
            var node = spt.pipeline.get_info_node();
            var version = spt.pipeline.get_node_kwarg(node, 'version');
            if (version && version != 1)
                return;

            var toolTop = bvr.src_el.getParent(".spt_pipeline_tool_top");
            spt.pipeline.set_top(toolTop.getElement(".spt_pipeline_top"));

            var top = bvr.src_el.getParent("."+bvr.top_class);
            var input = spt.api.get_input_values(top, null, false);

            spt.pipeline.set_node_kwarg(node, bvr.arg_name, input[bvr.arg_name]);

            node.has_changes = true;

            spt.named_events.fire_event('pipeline|change', {});
            '''
        }

        if input_type == "text":
            change_behavior['type'] = 'blur'
        elif input_type in ["select", "radio", "color"]:
            change_behavior['type'] = 'change'
        elif input_type == "checkbox":
            change_behavior['type'] = 'change'
            change_behavior['cbjs_action'] = '''
            var node = spt.pipeline.get_info_node();
            var version = spt.pipeline.get_node_kwarg(node, 'version');
            if (version && version != 1)
                return;

            var toolTop = bvr.src_el.getParent(".spt_pipeline_tool_top");
            spt.pipeline.set_top(toolTop.getElement(".spt_pipeline_top"));

            var top = bvr.src_el.getParent("."+bvr.top_class);
            var input = spt.api.get_input_values(top, null, false);

            var value = true;
            if (input[bvr.arg_name] != "on") value = false;

            spt.pipeline.set_node_kwarg(node, bvr.arg_name, value);

            node.has_changes = true;

            spt.named_events.fire_event('pipeline|change', {});
            '''

        input_wdg.add_behavior(change_behavior)


class DefaultInfoWdg(BaseInfoWdg):
    '''Process info panel for manual nodes.'''


    def get_display(self):
        process = self.kwargs.get("process")
        pipeline_code = self.kwargs.get("pipeline_code")
        node_type = self.kwargs.get("node_type")
        properties = self.kwargs.get("properties")

        process_code = properties.get("process_code") or ""
        search = Search("config/process")
        search.add_filter("code", process_code)

        self.process_sobj = search.get_sobject()
        process_sobj = self.process_sobj

        self.workflow  = {}
        if process_sobj:
            self.workflow  = process_sobj.get_json_value("workflow")
        if not self.workflow:
            self.workflow  = {}

        top = self.top
        self.initialize_session_behavior(top)

        if not pipeline_code:
            return top

        pipeline = Search.get_by_code("sthpw/pipeline", pipeline_code)

        if not process:
            return top


        top.add_class("spt_pipeline_info_top")

        search_type = pipeline.get_value("search_type")

        title_wdg = self.get_title_wdg(process, node_type)
        top.add( title_wdg )

        top.add("<p>A manual process is a process where work is done by a person.  The status of the process is determined by tasks added to this process which must be manually set to complete when finished<p>")


        desc_div = self.get_description_wdg()
        top.add(desc_div)


        button = ActionButtonWdg(title="Task Setup", size="block")
        top.add(button)
        button.add_behavior( {
            'type': 'click_up',
            'kwargs': self.kwargs,
            'cbjs_action': '''
            var toolTop = bvr.src_el.getParent(".spt_pipeline_tool_top");
            spt.pipeline.set_top(toolTop.getElement(".spt_pipeline_top"));

            var class_name = "tactic.ui.tools.PipelinePropertyWdg";
            var popup = spt.panel.load_popup("Task Setup", class_name, bvr.kwargs);
                popup.activator = bvr.src_el;

                var nodes = spt.pipeline.get_selected_nodes();
                var node = nodes[0];
                //spt.pipeline_properties.show_properties2(popup, node);
                '''
        } )




        setting = ProjectSetting.get_value_by_key("feature/process/task_detail")
        if setting in ["true"]:

            # FIXME: this does not belong here

            from spt.modules.workflow import TaskButtonDetailSettingWdg, TaskDetailSettingWdg
            #detail_wdg = TaskDetailSettingWdg(
            detail_wdg = TaskButtonDetailSettingWdg(
                    **self.kwargs
            )

            #detail_wdg = self.get_detail_wdg()
            top.add(detail_wdg)
            detail_wdg.add_style("margin: 10px")

            new_task_detail = ProjectSetting.get_value_by_key("new_task_detail") == "true"
            if new_task_detail:
                detail_wdg.add_behavior({
                    'type': 'load',
                    'cbjs_action': '''

                    var node = spt.pipeline.get_info_node();
                    var task_detail = spt.pipeline.get_node_kwarg(node, 'task_detail');

                    if (!task_detail) {
                        var defaults = {
                            app: "custom_view",
                            app0: "overview",
                            custom_view: "",
                            data_process: "",
                            data_process0: "",
                            display_mode: "tab",
                            form_html: "",
                            kwargs: "",
                            kwargs0: "",
                            mode: "app",
                            num_apps: "1",
                            template_view: "inherit",
                            title: "",
                            title0: "Overview",
                            view: ""
                        }
                        spt.pipeline.set_node_kwarg(node, 'task_detail', defaults);
                    }

                    '''
                    })


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


    def get_default_kwargs(self):

        kwargs = super(DefaultInfoWdg, self).get_default_kwargs()

        task_creation = False if self.workflow.get("task_creation") == False else True
        autocreate_task = True if self.workflow.get("autocreate_task") == True else False
        kwargs["task_creation"] = task_creation
        kwargs["autocreate_task"] = autocreate_task

        if not self.process_sobj:
            return kwargs

        process_sobj = self.process_sobj
        description = process_sobj.get_value("description")
        kwargs["description"] = description

        return kwargs



class ScriptSettingsWdg(BaseRefreshWdg):

    def get_display(self):

        action = self.kwargs.get("action") or "create_new"
        is_refresh = self.kwargs.get("is_refresh") == 'true'

        is_admin = Environment.get_security().is_admin()

        div = self.top
        self.set_as_panel(div)
        div.add_class("spt_script_edit")

        if not action:
            return div

        inner = DivWdg()
        div.add(inner)

        SessionalProcess.add_relay_session_behavior(inner)

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

        inner.add(script_wdg)


        # Execute mode

        form_wdg = DivWdg()
        inner.add(form_wdg)
        form_wdg.add_class("form-group")

        execute_mode = self.kwargs.get("execute_mode")

        cmd_text = SelectWdg(name="execute_mode")
        cmd_text.set_option("labels", "In Process|Blocking Separate Process|Non-Blocking Separate Process|Queued")
        cmd_text.set_option("values", "same process,same transaction|separate process,blocking|separate process,non-blocking|separate process,queued")
        if execute_mode:
            cmd_text.set_value(execute_mode)

        cmd_text.set_unique_id()
        form_wdg.add('<label class="bmd-label-floating" for="%s">Execute Mode</label>' % cmd_text.get_id())
        form_wdg.add(cmd_text)

        self.add_session_behavior(cmd_text, "select", "spt_action_info_top", "execute_mode")

        if is_refresh:
            return inner
        else:
            return div



    def get_command_script_wdg(self, on_action_class):

        form_wdg = DivWdg()
        form_wdg.add_class("form-group")

        form_wdg.add('<label class="bmd-label-floating">Python Command Class</label>')

        cmd_text = TextInputWdg(name="on_action_class")
        if on_action_class:
            cmd_text.set_value(on_action_class)

        form_wdg.add(cmd_text)

        self.add_session_behavior(cmd_text, "text", "spt_action_info_top", "on_action_class")

        return form_wdg



    def get_existing_script_wdg(self, script_path, script, language, is_admin):

        div = DivWdg()

        script_path_folder = ''
        script_path_title = ''

        if script_path:
            script_path_folder, script_path_title = os.path.split(script_path)

        script_obj = None
        if script_path:
            script_obj = Search.eval("@SOBJECT(config/custom_script['folder','%s']['title','%s'])"%(script_path_folder, script_path_title), single=True)

        script_path_form = DivWdg()
        div.add(script_path_form)
        script_path_form.add_class("form-group")

        script_path_div = DivWdg()
        script_path_form.add('<label class="bmd-label-floating">Script Path</label>')
        script_path_form.add(script_path_div)
        script_path_div.add_class("input-group")

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

                var toolTop = bvr.src_el.getParent(".spt_pipeline_tool_top");
                spt.pipeline.set_top(toolTop.getElement(".spt_pipeline_top"));

                // Set the node script_path_folder, reset the script_path_title
                var node = spt.pipeline.get_info_node();
                var script_path_folder = bvr.src_el.value;
                spt.pipeline.set_node_multi_kwarg(node, "script_path_folder", script_path_folder);

                var top = bvr.src_el.getParent(".spt_script_edit");
                var script_title_el = top.getElement(".spt_script_path_title");
                script_title_el.value = "";
                spt.pipeline.set_node_multi_kwarg(node, "script_path_title", "");

                spt.named_events.fire_event('pipeline|change', {});

            }, 250);

            '''
        } )

        self.add_session_behavior(script_path_folder_text, "text", "spt_action_info_top", "script_path_folder")


        slash = DivWdg('/')
        slash.add_styles('font-size: 1.7em; margin: 4px 5px 0 3px; float: left')
        script_path_div.add(slash)
        script_path_folder_text.add_styles("width: 120px; float: left")
        if script_obj:
            script_path_folder_text.set_value(script_path_folder)

        script_path_title_text = LookAheadTextInputWdg(name="script_path_title", search_type="config/custom_script", column="title", filters=filters, width='190')
        script_path_title_text.add_class("spt_script_path_title")

        script_path_div.add(script_path_title_text)

        script_path_title_text.add_style("float: left")
        if script_obj:
            script_path_title_text.set_value(script_path_title)
        script_path_title_text.add_behavior( {
            'type': 'blur',
            'cbjs_action': '''

            /* On blur of script path title input, if script obj exists,
            load script into ace editor and set node kwargs.
            Else, clear ace editor and clear node kwargs. */

            setTimeout( function() {

                // Get the script code and language
                var script_path_title = bvr.src_el.value;
                var top = bvr.src_el.getParent(".spt_script_edit");
                var script_path_folder = top.getElement(".spt_script_path_folder").value;
                if (script_path_folder && script_path_title) {
                    var server = TacticServerStub.get();
                    var script = server.eval("@GET(config/custom_script['folder', '" + script_path_folder + "'].code)", {single: true});
                    var language = server.eval("@GET(config/custom_script['folder', '" + script_path_folder + "'].language)", {single: true});
                } else {
                    return;
                }

                var buttons_div = top.getElement(".spt_script_edit_buttons");
                spt.show(buttons_div);

                var script_language = top.getElement(".spt_script_language");
                var editor = top.getElement(".spt_ace_editor_top");

                if (script_path_folder && script_path_title) {
                    var toolTop = bvr.src_el.getParent(".spt_pipeline_tool_top");
                    spt.pipeline.set_top(toolTop.getElement(".spt_pipeline_top"));

                    if (script) {
                        // Show language, show editor, set script in ace editor, set node kwargs
                        script_language.innerText = language;
                        editor.setStyle("display", "");

                        var node = spt.pipeline.get_info_node();
                        spt.pipeline.set_node_multi_kwarg(node, "script", script);
                        //spt.pipeline.set_input_value_from_kwargs(node, "script", editor);
                    } else {
                        // Reset language, Hide editor, reset ace editor, set node kwargs
                        script_language.innerText = "";
                        editor.setStyle("display", "none");

                        var node = spt.pipeline.get_info_node();
                        spt.pipeline.set_node_multi_kwarg(node, "script", "");
                        //spt.pipeline.set_input_value_from_kwargs(node, "script", editor);

                        spt.alert("No script found.");
                    }
                    spt.named_events.fire_event('pipeline|change', {});
                }


            }, 250);

            '''
        } )

        self.add_session_behavior(script_path_title_text, "text", "spt_action_info_top", "script_path_title")

        script_path_div.add_relay_behavior( {
            'type': "mouseup",
            'bvr_match_class': 'spt_input_text_result',
            'cbjs_action': '''

            var node = spt.pipeline.get_info_node();
            var version = spt.pipeline.get_node_kwarg(node, 'version');
            if (version && version != 1)
                return;

            var textTop = bvr.src_el.getParent(".spt_input_text_top");
            var textInput = textTop.getElement(".spt_text_input_wdg");
            var name = textInput.getAttribute("name");

            var toolTop = bvr.src_el.getParent(".spt_pipeline_tool_top");
            spt.pipeline.set_top(toolTop.getElement(".spt_pipeline_top"));

            var top = bvr.src_el.getParent(".spt_action_info_top");
            var input = spt.api.get_input_values(top, null, false);

            spt.pipeline.set_node_multi_kwarg(node, name, input[name]);

            spt.named_events.fire_event('pipeline|change', {});

            '''
        } )

        if language == "python":
            div.add("<p>Language: <b class='spt_script_language'>Python</b></p>")
        else:
            div.add("<p>Language: <b class='spt_script_language'>Server Javascript</b></p>")


        edit_label = "Click to enable Edit"

        enable_edit_button = DivWdg()

        script_editor = DivWdg()
        div.add(script_editor)
        script_editor.add_class("spt_script_editor")
        script_editor.add(enable_edit_button)

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


        ###############################################################

        script_text = TextAreaWdg("script")
        script_text.set_option("read_only", "true")
        script_text.add_class("form-control")
        script_text.add_class("spt_python_script_text")
        script_editor.add_style("display", "none")
        script_editor.add(script_text)

        if script_obj:
            script = script_obj.get_value("script")
            script_text.set_value(script)
        else:
            script_editor.add_style("display: none")


        self.add_session_behavior(script_text, "text", "spt_action_info_top", "script")
        script_editor.add_behavior({
            'type': 'load',
            'cbjs_action': '''
            var toolTop = bvr.src_el.getParent(".spt_pipeline_tool_top");
            spt.pipeline.set_top(toolTop.getElement(".spt_pipeline_top"));

            var node = spt.pipeline.get_info_node();

            var top = bvr.src_el.getParent(".spt_script_edit");
            var el = top.getElement(".spt_python_script_text");
            if (el.value) spt.pipeline.set_node_multi_kwarg(node, "script", el.value);

            var kwargs = spt.pipeline.get_node_multi_kwargs(node);

            if (kwargs.script) bvr.src_el.setStyle("display", "");
            else bvr.src_el.setStyle("display", "none");

            '''
        })

        # TO be removed
        #################################################################

        script = None
        if script_obj:
            script = script_obj.get_value("script")

        unique_id = Common.generate_random_key()

        script_ace_editor = AceEditorWdg(
            width="100%",
            language=language,
            code=script,
            show_options=False,
            editor_id=unique_id,
            dynamic_height=True,
            show_bottom=False,
            form_element_name="script"
        )

        if not script:
            script_ace_editor.add_style("display", "none")

        script_ace_editor.add_class("form-group")

        div.add(script_ace_editor)





        return div



    def get_new_script_wdg(self, is_admin):

        div = DivWdg()


        if is_admin:
            form_wdg = DivWdg()
            div.add(form_wdg)
            form_wdg.add_class("form-group")

            select = SelectWdg("language")
            select.set_option("labels", "Python|Server Javascript")
            select.set_option("values", "python|server_js")
            select.set_unique_id()

            form_wdg.add('<label class="bmd-label-floating" for="%s">Lanuage</label>' % select.get_id())
            form_wdg.add(select)

            self.add_session_behavior(select, "select", "spt_action_info_top", "language")
        else:
            div.add("<p>Language: <b class='spt_script_language'>Server Javascript</b></p>")


        ########################################
        # REMOVE
        script_text = TextAreaWdg("script")
        script_text.add_style('padding-top: 10px')
        script_text.add_class("form-control")
        script_text.add_class("spt_python_script_text")

        script_text.add_style("height: 300px")
        script_text.add_style("width: 100%")

        self.add_session_behavior(script_text, "text", "spt_action_info_top", "script")

        script_text.add_style("display", "none")
        div.add(script_text)
        ####################################

        language = self.kwargs.get("language")
        if not language:
            language = "javascript"


        script = self.kwargs.get("script")
        if not script:
            script = ("// Enter script here\n"
            "var server = TACTIC.get();")

        unique_id = Common.generate_random_key()
        script_ace_editor = AceEditorWdg(
            width="100%",
            language=language,
            code=script,
            show_options=False,
            editor_id=unique_id,
            dynamic_height=True,
            show_bottom=False,
            form_element_name="script"
        )

        script_ace_editor.add_class("form-group")

        div.add(script_ace_editor)

        return div


    def add_session_behavior(self, input_wdg, input_type, top_class, arg_name):

        # On load behavior, displays sessional value
        load_behavior = {
            'type': 'load',
            'arg_name': arg_name
        }

        cbjs_action_default = '''

        var toolTop = bvr.src_el.getParent(".spt_pipeline_tool_top");
        spt.pipeline.set_top(toolTop.getElement(".spt_pipeline_top"));

        var node = spt.pipeline.get_info_node();

        var version = spt.pipeline.get_node_kwarg(node, 'version');
        if (version && version != 1)
            return;

        '''

        load_behavior['cbjs_action'] = cbjs_action_default + '''
        spt.pipeline.set_input_value_from_kwargs(node, bvr.arg_name, bvr.src_el);
        '''

        if input_type == "select":
            load_behavior['cbjs_action'] = cbjs_action_default + '''
            spt.pipeline.set_select_value_from_kwargs(node, bvr.arg_name, bvr.src_el);
            '''
        elif input_type == "radio":
            load_behavior['cbjs_action'] = cbjs_action_default + '''
            spt.pipeline.set_radio_value_from_kwargs(node, bvr.arg_name, bvr.src_el);
            '''
        elif input_type == "checkbox":
            load_behavior['cbjs_action'] = cbjs_action_default + '''
            spt.pipeline.set_checkbox_value_from_kwargs(node, bvr.arg_name, bvr.src_el);
            '''

        input_wdg.add_behavior(load_behavior)


        change_behavior = {
            'top_class': top_class,
            'arg_name': arg_name,
        }

        change_cbjs_action = """
            var node = spt.pipeline.get_info_node();
            var version = spt.pipeline.get_node_kwarg(node, 'version');
            if (version && version != 1)
                return;

            var toolTop = bvr.src_el.getParent(".spt_pipeline_tool_top");
            spt.pipeline.set_top(toolTop.getElement(".spt_pipeline_top"));

            var top = bvr.src_el.getParent("."+bvr.top_class);
            var input = spt.api.get_input_values(top, null, false);

            spt.pipeline.set_node_multi_kwarg(node, bvr.arg_name, input[bvr.arg_name]);

            spt.named_events.fire_event('pipeline|change', {});
        """

        if input_type == "ace_editor":
            change_behavior['cbjs_action'] = """



            """
        else:
            change_behavior['cbjs_action'] = change_cbjs_action
            if input_type == "text":
                change_behavior['type'] = 'blur'
            elif input_type == "select":
                change_behavior['type'] = 'change'
            elif input_type == "radio":
                change_behavior['type'] = 'change'

        input_wdg.add_behavior(change_behavior)





class ActionInfoWdg(BaseInfoWdg):

    def get_display(self):

        process = self.kwargs.get("process")
        pipeline_code = self.kwargs.get("pipeline_code")
        node_type = self.kwargs.get("node_type")
        properties = self.kwargs.get("properties")

        process_code = properties.get("process_code")
        search = Search("config/process")
        search.add_filter("code", process_code)

        self.process_sobj = search.get_sobject()
        process_sobj = self.process_sobj

        workflow = {}
        if process_sobj:
            workflow = process_sobj.get_json_value("workflow")
        if not workflow:
            workflow = {}
        self.workflow = workflow


        event = "process|action"


        settings = properties.get("settings") or {}
        default = settings.get("default") or {}
        # get the trigger
        self.script = default.get("script") or ""
        self.language = default.get("language") or ""
        self.script_path = ""
        self.process_code = ""
        self.on_action_class = ""
        self.action = ""
        self.execute_mode = ""

        """
        if process_sobj:
            raise
            process_code = process_sobj.get_code()
            search = Search("config/trigger")
            search.add_filter("process", process_code)
            search.add_filter("event", event)
            trigger = search.get_sobject()
            trigger = trigger
            # get the custom script
            if trigger:
                self.script_path = trigger.get("script_path")
                self.on_action_class = trigger.get("class_name")
                self.execute_mode = trigger.get("mode")

                if self.script_path:
                    self.action = "script_path"
                elif self.on_action_class:
                    self.action = "command"
                else:
                    self.action = "create_new"



                if self.script_path:
                    folder, title = os.path.split(self.script_path)

                    search = Search("config/custom_script")
                    search.add_filter("folder", folder)
                    search.add_filter("title", title)
                    custom_script = search.get_sobject()
                    if custom_script:
                        self.script = custom_script.get("script")
                        self.language = custom_script.get("language")
        """


        if not self.action:
            self.action = "create_new"

        top = self.top
        top.add_class('spt_action_info_top')
        self.initialize_session_behavior(top)


        title_wdg = self.get_title_wdg(process, node_type)
        top.add(title_wdg)


        # FIXME: Add description for condition node.
        top.add("<p>A action process is an automated process which can execute a script or command when called from a previous process.</p>")

        desc_div = self.get_description_wdg()
        top.add(desc_div)

        form_top = DivWdg()
        form_top.add_class("spt_section_top")
        form_top.add_class("spt_form_top")
        top.add(form_top)

        form_wdg = DivWdg()
        form_top.add(form_wdg)
        form_wdg.add_class("form-group")

        select = SelectWdg("action")
        select.add_class("spt_action_select")
        select.set_unique_id()

        if node_type == "action":
            label = '<label class="bmd-label-floating" for="%s">Action Source</label>' % select.get_id()
            form_wdg.add(label)
            form_wdg.add(select)
            help_text = "This will be the automatically executed action for this process."
            form_wdg.add('<span class="bmd-help">%s</span>' % help_text)

        else:
            label = '<label class="bmd-label-floating" for="%s">Condition Source</label>' % select.get_id()
            form_wdg.add(label)
            form_wdg.add(select)
            help_text = "This will be executed on the completion event of an input process.  The condition check should either return True or False or a list of the output streams."
            form_wdg.add('<span class="bmd-help">%s</span>' % help_text)


        SessionalProcess.add_relay_session_behavior(form_wdg, post_processing='''

            var top = bvr.src_el.getParent(".spt_form_top");
            var script_el = top.getElement(".spt_script_edit");
            var toolTop = bvr.src_el.getParent(".spt_pipeline_tool_top");
            spt.pipeline.set_top(toolTop.getElement(".spt_pipeline_top"));

            var value = data.action || "create_new";

            var on_save = function(kwargs) {
                var data = kwargs.default || {};
                if (data.action != "script_path" && data.action != "create_new") return kwargs;

                var script_path_folder = data.script_path_folder;
                var script_path_title = data.script_path_title;
                var script_path = (script_path_folder && script_path_title) ? script_path_folder + "/" + script_path_title : '';

                var popup = false
                var test = script_path ? spt.CustomProject.get_script_by_path(script_path, popup) : true;
                if (!test) {
                    spt.error('Invalid script path [' + script_path + '] is specified.');
                    return {
                        is_error: true
                    };
                }

                // either (script_path && script) or script_new
                var script = data.script;
                if (script_path && !script) {
                    spt.error('You have most likely specified an invalid script path since the script content is empty.');
                    return {
                        is_error: true
                    };
                }

                data.script_path = script_path;
                data.script = script;

                return kwargs;
            }

            spt.pipeline.add_node_on_save(node, "script", on_save);

            spt.panel.refresh_element(script_el, {action: value});

        ''')



        options = []
        labels = []


        labels.append("Use Existing Script")
        options.append("script_path")
        labels.append("Create New Script")
        options.append("create_new")

        is_admin = Environment.get_security().is_admin()
        if is_admin:
            labels.append("Use Python Command Class")
            options.append("command")

        select.set_option("labels", labels)
        select.set_option("values", options)
        if self.action:
            select.set_value(self.action)

        select.add_behavior( {
            'type': 'load',
            'cbjs_action': '''
            var node = spt.pipeline.get_info_node();
            var version = spt.pipeline.get_node_kwarg(node, 'version');
            if (version == 2)
                return;

            var top = bvr.src_el.getParent(".spt_form_top");
            var script_el = top.getElement(".spt_script_edit");

            var toolTop = bvr.src_el.getParent(".spt_pipeline_tool_top");
            spt.pipeline.set_top(toolTop.getElement(".spt_pipeline_top"));

            var node = spt.pipeline.get_info_node();
            spt.pipeline.set_input_value_from_kwargs(node, "action", bvr.src_el);
            var value = bvr.src_el.value;
            spt.pipeline.select_node_multi_kwargs(node, value, "action", value);

            var on_save = function(kwargs) {
                if (kwargs.action != "script_path" && kwargs.action != "create_new") return kwargs;

                var script_path_folder = kwargs.script_path_folder;
                var script_path_title = kwargs.script_path_title;
                var script_path = (script_path_folder && script_path_title) ? script_path_folder + "/" + script_path_title : '';

                var popup = false
                var test = script_path ? spt.CustomProject.get_script_by_path(script_path, popup) : true;
                if (!test) {
                    spt.error('Invalid script path [' + script_path + '] is specified.');
                    return {
                        is_error: true
                    };
                }

                // either (script_path && script) or script_new
                var script = kwargs.script;
                if (script_path && !script) {
                    spt.error('You have most likely specified an invalid script path since the script content is empty.');
                    return {
                        is_error: true
                    };
                }

                kwargs.script_path = script_path;
                kwargs.script = script;

                return kwargs;
            }

            spt.pipeline.add_node_on_save(node, "script", on_save);

            spt.panel.refresh_element(script_el, {action: bvr.src_el.value});
        '''})

        form_wdg.add_relay_behavior( {
            'type': 'change',
            'bvr_match_class': 'spt_action_select',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_form_top");
            var script_el = top.getElement(".spt_script_edit");
            var value = bvr.src_el.value;

            var toolTop = bvr.src_el.getParent(".spt_pipeline_tool_top");
            spt.pipeline.set_top(toolTop.getElement(".spt_pipeline_top"));

            var node = spt.pipeline.get_info_node();
            var version = spt.pipeline.get_node_kwarg(node, 'version');
            if (!version || version == '1')
                spt.pipeline.select_node_multi_kwargs(node, value, "action", value);

            spt.named_events.fire_event('pipeline|change', {});

            spt.panel.refresh_element(script_el, {action: value});
            '''
        } )


        script_wdg = ScriptSettingsWdg(
            action=self.action,
            on_action_class=self.on_action_class,
            script_path=self.script_path,
            script=self.script,
            language=self.language,
            execute_mode=self.execute_mode
        )
        form_top.add(script_wdg)

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


    def get_default_kwargs(self):

        kwargs = super(ActionInfoWdg, self).get_default_kwargs()

        kwargs["execute_mode"] = self.execute_mode
        if self.action == "create_new":
            kwargs['language'] = self.language
            kwargs['script'] = self.script
        elif self.action == "command":
            kwargs['on_action_class'] = self.on_action_class
        elif self.action == "script_path":
            script_path_folder = ""
            script_path_title = ""

            if self.script_path:
                script_path_folder, script_path_title = os.path.split(self.script_path)
            kwargs['script_path_folder'] = script_path_folder
            kwargs['script_path_title'] = script_path_title

        description = ""
        if self.process_sobj:
            process_sobj = self.process_sobj
            description = process_sobj.get_value("description")

        return {
            "multi": "true",
            "selected": self.action,
            "description": description,
            self.action: kwargs
        }




class UnknownInfoWdg(BaseInfoWdg):

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
        properties = self.kwargs.get("properties")

        process_code = properties.get("process_code")
        search = Search("config/process")
        search.add_filter("code", process_code)

        self.process_sobj = search.get_sobject()
        process_sobj = self.process_sobj


        workflow = {}
        if process_sobj:
            workflow = process_sobj.get_json_value("workflow")
        if not workflow:
            workflow = {}
        self.workflow = workflow

        top = self.top
        top.add_class("spt_approval_info_top")
        self.initialize_session_behavior(top)

        top.add_class("spt_section_top")

        SessionalProcess.add_relay_session_behavior(top)


        pipeline = Pipeline.get_by_code(pipeline_code)


        title_wdg = self.get_title_wdg(process, node_type)
        top.add(title_wdg)


        info_div = DivWdg()
        top.add(info_div)
        info_div.add("An approval process is used a specific user will have the task to approve work down in the previous processes.")
        info_div.add_style("margin: 10px 10px 20px 10px")



        desc_div = self.get_description_wdg()
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
                var toolTop = bvr.src_el.getParent(".spt_pipeline_tool_top");
                spt.pipeline.set_top(toolTop.getElement(".spt_pipeline_top"));

                var class_name = "tactic.ui.tools.PipelinePropertyWdg";
                var kwargs = {
                    pipeline_code: bvr.pipeline_code,
                    process: bvr.process
                }
                var popup = spt.panel.load_popup("Task Setup", class_name, kwargs);
                popup.activator = bvr.src_el;

                var nodes = spt.pipeline.get_selected_nodes();
                var node = nodes[0];
                //spt.pipeline_properties.show_properties2(popup, node);
                '''
            } )


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

            new_task_detail = ProjectSetting.get_value_by_key("new_task_detail") == "true"
            if new_task_detail:
                detail_wdg.add_behavior({
                    'type': 'load',
                    'cbjs_action': '''

                    var node = spt.pipeline.get_info_node();
                    var task_detail = spt.pipeline.get_node_kwarg(node, 'task_detail');

                    if (!task_detail) {
                        var defaults = {
                            app: "custom_view",
                            app0: "overview",
                            app1: "review_assets",
                            custom_view: "",
                            data_process: "",
                            data_process0: "",
                            data_process1: "",
                            display_mode: "tab",
                            form_html: "",
                            kwargs: "",
                            kwargs0: "",
                            kwargs1: "",
                            mode: "app",
                            num_apps: "2",
                            template_view: "inherit",
                            title: "",
                            title0: "Overview",
                            title1: "Review Assets",
                            view: ""
                        }
                        spt.pipeline.set_node_kwarg(node, 'task_detail', defaults);
                    }

                    '''
                    })


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


        form_wdg.add("<br/>")
        form_wdg.add("<br/>")

        self.add_session_behavior(text, "text", "spt_approval_info_top", "assigned")

        form_wdg.add_relay_behavior( {
            'type': "mouseup",
            'bvr_match_class': 'spt_input_text_result',
            'cbjs_action': '''

            var node = spt.pipeline.get_info_node();
            var version = spt.pipeline.get_node_kwarg(node, 'version');
            if (version && version != 1)
                return;

            var toolTop = bvr.src_el.getParent(".spt_pipeline_tool_top");
            spt.pipeline.set_top(toolTop.getElement(".spt_pipeline_top"));

            var top = bvr.src_el.getParent(".spt_approval_info_top");
            var input = spt.api.get_input_values(top, null, false);

            spt.pipeline.set_node_kwarg(node, "assigned", input["assigned"]);

            node.has_changes = true;

            spt.named_events.fire_event('pipeline|change', {});

            '''
        } )

        return top


    def get_default_kwargs(self):

        workflow = self.workflow
        assigned = workflow.get("assigned")

        kwargs = super(ApprovalInfoWdg, self).get_default_kwargs()
        kwargs["assigned"] = assigned

        task_creation = False if self.workflow.get("task_creation") == False else True
        autocreate_task = True if self.workflow.get("autocreate_task") == True else False
        kwargs["task_creation"] = task_creation
        kwargs["autocreate_task"] = autocreate_task

        if not self.process_sobj:
            return kwargs

        process_sobj = self.process_sobj
        description = process_sobj.get_value("description")
        kwargs["description"] = description

        return kwargs


class ConditionInfoWdg(ActionInfoWdg):
    pass


class HierarchyInfoWdg(BaseInfoWdg):

    def get_display(self):

        process = self.kwargs.get("process")
        pipeline_code = self.kwargs.get("pipeline_code")
        node_type = self.kwargs.get("node_type")
        properties = self.kwargs.get("properties")

        process_code = properties.get("process_code")
        search = Search("config/process")
        search.add_filter("code", process_code)

        self.process_sobj = search.get_sobject()

        self.workflow = {}
        if self.process_sobj:
            self.workflow = self.process_sobj.get_json_value("workflow")
        if not self.workflow:
            self.workflow = {}

        top = self.top
        top.add_class("spt_hierarchy_top")
        self.initialize_session_behavior(top)

        top.add_class("spt_section_top")

        SessionalProcess.add_relay_session_behavior(top)


        pipeline = Pipeline.get_by_code(pipeline_code)
        search_type = pipeline.get_value("search_type")


        title_wdg = self.get_title_wdg(process, node_type)
        top.add(title_wdg)


        info_div = DivWdg()
        top.add(info_div)
        info_div.add("A hierarchy process is a process that references a sub-workflow.")
        info_div.add_style("margin: 10px 10px 20px 10px")




        top.add( self.get_description_wdg() )

        settings_wdg = DivWdg()
        top.add(settings_wdg)
        settings_wdg.add_style("padding: 10px")


        search = Search("sthpw/pipeline")
        search.add_filter("search_type", search_type)
        search.add_filter("code", pipeline_code, op="!=")
        subpipelines = search.get_sobjects()

        values = [x.get("code") for x in subpipelines]
        labels = [x.get("name") for x in subpipelines]

        settings_wdg.add("<b>Points to a sub Workflow:</b>")
        select = SelectWdg("subpipeline")
        settings_wdg.add(select)
        select.set_option("values", values)
        select.set_option("labels", labels)
        select.add_empty_option("-- Select --")

        self.add_session_behavior(select, "select", "spt_hierarchy_top", "subpipeline")


        settings_wdg.add("<span style='opacity: 0.6'>Reference another workflow</span>")

        settings_wdg.add("<br/>")
        settings_wdg.add("<br/>")


        # auto create sb tasks
        values = ["subtasks_only", "top_only", "all", "none"]
        labels = ["Create SubTasks Only", "Top Task Only", "Both Top and SubTasks", "No Tasks"]

        settings_wdg.add("<b>Task Creation:</b>")
        select = SelectWdg("task_creation")
        settings_wdg.add(select)
        select.set_option("values", values)
        select.set_option("labels", labels)


        self.add_session_behavior(select, "select", "spt_hierarchy_top", "task_creation")


        settings_wdg.add("<span style='opacity: 0.6'>Determine whether tasks of the referenced workflow are created when generating an inital schedule</span>")
        settings_wdg.add("<br/>")
        settings_wdg.add("<br/>")


        return top


    def get_default_kwargs(self):

        kwargs = super(HierarchyInfoWdg, self).get_default_kwargs()
        if not self.process_sobj:
            return kwargs

        process_sobj = self.process_sobj
        subpipeline = process_sobj.get_value("subpipeline_code")

        workflow = self.workflow

        task_creation = "subtasks_only"
        if workflow.get("default"):
            task_creation = workflow.get("default").get("task_creation")

        kwargs["subpipeline"] = subpipeline
        kwargs["task_creation"] = task_creation

        if not self.process_sobj:
            return kwargs

        process_sobj = self.process_sobj
        description = process_sobj.get_value("description")
        kwargs["description"] = description

        return kwargs



class DependencyInfoWdg(BaseInfoWdg):

    def get_display(self):

        process = self.kwargs.get("process")
        pipeline_code = self.kwargs.get("pipeline_code")
        node_type = self.kwargs.get("node_type")
        properties = self.kwargs.get("properties")

        process_code = properties.get("process_code")
        search = Search("config/process")
        search.add_filter("code", process_code)

        self.process_sobj = search.get_sobject()

        self.workflow = {}
        if self.process_sobj:
            self.workflow = self.process_sobj.get_json_value("workflow")
        if not self.workflow:
            self.workflow = {}


        top = self.top
        top.add_class("spt_dependency_top")

        top.add_class("spt_section_top")


        title_wdg = self.get_title_wdg(process, node_type)
        top.add(title_wdg)


        settings_wdg = DivWdg()
        top.add(settings_wdg)
        settings_wdg.add_style("padding: 10px")

        SessionalProcess.add_relay_session_behavior(settings_wdg)


        # FIXME: HARD CODED
        search_type = "vfx/asset"
        search_type = "workflow/job"

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
        settings_wdg.add("<b>Send Message to Related Items::</b>")
        select = SelectWdg("related_search_type")
        settings_wdg.add(select)
        select.set_option("values", values)
        select.set_option("labels", labels)
        select.add_empty_option("-- Select --")
        settings_wdg.add("<span style='opacity: 0.6'>This will send a message to the selected items</span>")
        settings_wdg.add("<br/>")


        # notify all search types
        from pyasm.widget import RadioWdg

        scope_div = DivWdg()
        settings_wdg.add(scope_div)
        scope_div.add_style("margin: 15px 25px")

        radio = RadioWdg("related_scope")
        radio.add_attr("value", "local")
        scope_div.add(radio)
        radio.set_checked()
        scope_div.add(" Only Related Items<br/>")

        radio = RadioWdg("related_scope")
        radio.add_attr("value", "global")
        scope_div.add(radio)
        scope_div.add(" All Items")
        scope_div.add("<br/>")

        search = Search("sthpw/pipeline")
        search.add_filter("search_type", search_type)
        related_pipelines = search.get_sobjects()



        # workflows list
        values = set()
        labels = set()
        for related_pipeline in related_pipelines:
            values.add(related_pipeline.get_code())
            labels.add(related_pipeline.get_value("name"))
        values = list(values)
        labels = list(labels)

        settings_wdg.add("<br/>")
        settings_wdg.add("<b>To Workflow</b>")
        select = SelectWdg("related_pipeline_code")
        settings_wdg.add(select)
        select.set_option("values", values)
        select.set_option("labels", labels)
        select.add_empty_option("-- Select --")

        settings_wdg.add("<span style='opacity: 0.6'>Determines which process to connect to</span>")
        settings_wdg.add("<br/>")





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
        settings_wdg.add(select)
        select.set_option("values", values)
        select.add_empty_option("-- Select --")

        settings_wdg.add("<span style='opacity: 0.6'>Determines which process to connect to</span>")
        settings_wdg.add("<br/>")






        settings_wdg.add("<br/>")
        settings_wdg.add("<b>With Status</b>")
        select = SelectWdg("related_status")
        settings_wdg.add(select)
        select.set_option("values", "Pending|Action|Complete")
        select.add_empty_option("-- Select --")


        settings_wdg.add("<span style='opacity: 0.6'>Determines which status to set the process to.</span>")
        settings_wdg.add("<br/>")





        settings_wdg.add("<br/>")
        settings_wdg.add("<b>Wait</b>")
        select = SelectWdg("related_wait")
        settings_wdg.add(select)
        select.set_option("labels", "No|Yes")
        select.set_option("values", "false|true")
        #select.add_empty_option("-- Select --")


        settings_wdg.add("<span style='opacity: 0.6'>Determines if this process will wait until it receives a complete signal (from another dependency) or set to complete automatically")
        settings_wdg.add("<br/>")


        settings_wdg.add("<br clear='all'/>")


        return top




    def get_default_kwargs(self):

        kwargs = super(DependencyInfoWdg, self).get_default_kwargs()

        workflow = self.workflow
        kwargs["related_search_type"] = workflow.get("search_type")
        kwargs["related_process"] = workflow.get("process")
        kwargs["related_status"] = workflow.get("status")
        kwargs["related_scope"] = workflow.get("scope")
        kwargs["related_wait"] = workflow.get("wait")

        if not self.process_sobj:
            return kwargs

        process_sobj = self.process_sobj
        description = process_sobj.get_value("description")
        kwargs["description"] = description

        return kwargs




class ProgressInfoWdg(BaseInfoWdg):

    def get_display(self):

        process = self.kwargs.get("process")
        pipeline_code = self.kwargs.get("pipeline_code")
        node_type = self.kwargs.get("node_type")
        properties = self.kwargs.get("properties")

        process_code = properties.get("process_code")
        search = Search("config/process")
        search.add_filter("code", process_code)

        project_code = Project.get_project_code()

        self.process_sobj = search.get_sobject()
        process_sobj = self.process_sobj


        workflow = {}
        if process_sobj:
            workflow = process_sobj.get_json_value("workflow")
        if not workflow:
            workflow = {}
        self.workflow = workflow

        related_search_type = workflow.get("search_type")
        related_pipeline_code = workflow.get("pipeline_code")
        related_process = workflow.get("process")
        related_status = workflow.get("status")
        related_scope = workflow.get("scope")
        related_wait = workflow.get("wait")

        top = self.top
        top.add_class("spt_progress_top")
        self.initialize_session_behavior(top)


        top.add_behavior({
            'type': 'load',
            'project_code': project_code,
            'related_pipeline_code': related_pipeline_code,
            'related_process': related_process,
            'cbjs_action': '''

            var node = spt.pipeline.get_info_node();
            var version = spt.pipeline.get_node_kwarg(node, 'version');
            if (version && version != 1)
                return;

            var toolTop = bvr.src_el.getParent(".spt_pipeline_tool_top");
            spt.pipeline.set_top(toolTop.getElement(".spt_pipeline_top"));
            bvr.src_el.build_option = function(value, label) {
                var option = document.createElement("option")
                option.value = value;
                option.innerText = label;
                return option;
            }
            bvr.src_el.add_options = function(select, values, labels) {
                if (values.length != labels.length) {
                    spt.alert("value and label lists must have the same length");
                    return;
                }
                for (var i=0; i<values.length; i++) {
                    var value = values[i];
                    var label = labels[i];
                    var option = bvr.src_el.build_option(value, label);
                    select.appendChild(option);
                }
            }
            bvr.src_el.load_pipeline_options = function(src_el) {
                var node = spt.pipeline.get_info_node();
                var related_search_type = src_el.value || spt.pipeline.get_node_kwarg(node, "related_search_type");
                var related_pipeline_code = spt.pipeline.get_node_kwarg(node, "related_pipeline_code") || bvr.related_pipeline_code;
                var server = TacticServerStub.get();
                var expression = "@SOBJECT(sthpw/pipeline['search_type', '" + related_search_type + "']['project_code', '" + bvr.project_code + "'])"
                var pipeline_sobjs = server.eval(expression);
                var top = src_el.getParent(".spt_progress_top");
                var select = top.querySelectorAll("select[name='related_pipeline_code']")[0];
                select.innerHTML = "<option value=''>-- any --</option>";
                for (var i=0; i<pipeline_sobjs.length; i++) {
                    var pipeline_sobj = pipeline_sobjs[i];
                    var value = pipeline_sobj.code;
                    var label = pipeline_sobj.name + " (" + pipeline_sobj.search_type + ")";
                    var option = top.build_option(value, label);
                    select.appendChild(option);
                    if (value == related_pipeline_code) select.value = related_pipeline_code;
                }
                bvr.src_el.load_process_options(select);
            }
            bvr.src_el.load_process_options = function(src_el) {
                var node = spt.pipeline.get_info_node();
                var related_pipeline_code = src_el.value || spt.pipeline.get_node_kwarg(node, "related_pipeline_code");
                var related_process = spt.pipeline.get_node_kwarg(node, "related_process") || bvr.related_process;
                var server = TacticServerStub.get();
                var expression = "@SOBJECT(config/process['pipeline_code', '" + related_pipeline_code + "'])";
                var process_sobjs = server.eval(expression);
                var top = src_el.getParent(".spt_progress_top");
                var select = top.querySelectorAll("select[name='related_process']")[0];
                select.innerHTML = "<option value=''>-- any --</option>";
                for (var i=0; i<process_sobjs.length; i++) {
                    var process_sobj = process_sobjs[i];
                    var value = process_sobj.code;
                    var label = process_sobj.process;
                    var option = top.build_option(value, label);
                    select.appendChild(option);
                    if (value == related_process) select.value = related_process;
                }
            }
            '''
            })


        top.add_behavior({
            'type': 'load',
            'project_code': project_code,
            'related_pipeline_code': related_pipeline_code,
            'related_process': related_process,
            'cbjs_action': '''

            var node = spt.pipeline.get_info_node();
            var version = spt.pipeline.get_node_kwarg(node, 'version');
            if (version != 2)
                return;

            var toolTop = bvr.src_el.getParent(".spt_pipeline_tool_top");
            spt.pipeline.set_top(toolTop.getElement(".spt_pipeline_top"));

            bvr.src_el.build_option = function(value, label) {
                var option = document.createElement("option")
                option.value = value;
                option.innerText = label;
                return option;
            }

            bvr.src_el.add_options = function(select, values, labels) {
                if (values.length != labels.length) {
                    spt.alert("value and label lists must have the same length");
                    return;
                }

                for (var i=0; i<values.length; i++) {
                    var value = values[i];
                    var label = labels[i];
                    var option = bvr.src_el.build_option(value, label);
                    select.appendChild(option);
                }
            }

            bvr.src_el.load_pipeline_options = function(src_el) {
                var node = spt.pipeline.get_info_node();
                var data = spt.pipeline.get_node_kwarg(node, "progress") || {};
                var related_search_type = src_el.value || data.related_search_type;
                var related_pipeline_code = data.related_pipeline_code || bvr.related_pipeline_code;

                var server = TacticServerStub.get();
                var expression = "@SOBJECT(sthpw/pipeline['search_type', '" + related_search_type + "']['project_code', '" + bvr.project_code + "'])"
                var pipeline_sobjs = server.eval(expression);

                var top = src_el.getParent(".spt_progress_top");
                var select = top.querySelectorAll("select[name='related_pipeline_code']")[0];
                select.innerHTML = "<option value=''>-- any --</option>";

                for (var i=0; i<pipeline_sobjs.length; i++) {
                    var pipeline_sobj = pipeline_sobjs[i];
                    var value = pipeline_sobj.code;
                    var label = pipeline_sobj.name + " (" + pipeline_sobj.search_type + ")";
                    var option = top.build_option(value, label);
                    select.appendChild(option);

                    if (value == related_pipeline_code) select.value = related_pipeline_code;
                }
                bvr.src_el.load_process_options(select);
            }

            bvr.src_el.load_process_options = function(src_el) {
                var node = spt.pipeline.get_info_node();
                var data = spt.pipeline.get_node_kwarg(node, "progress") || {};
                var related_pipeline_code = src_el.value || data.related_pipeline_code;
                var related_process = data.related_process || bvr.related_process;

                var server = TacticServerStub.get();
                var expression = "@SOBJECT(config/process['pipeline_code', '" + related_pipeline_code + "'])";
                var process_sobjs = server.eval(expression);

                var top = src_el.getParent(".spt_progress_top");
                var select = top.querySelectorAll("select[name='related_process']")[0];
                select.innerHTML = "<option value=''>-- any --</option>";

                for (var i=0; i<process_sobjs.length; i++) {
                    var process_sobj = process_sobjs[i];
                    var value = process_sobj.code;
                    var label = process_sobj.process;
                    var option = top.build_option(value, label);
                    select.appendChild(option);

                    if (value == related_process) select.value = related_process;
                }
            }




            '''
            })

        top.add_class("spt_section_top")

        SessionalProcess.add_relay_session_behavior(top, pre_processing='''

            var searchTypeSelect = bvr.src_el.getElement("select[name='related_search_type']")
            bvr.src_el.load_pipeline_options(searchTypeSelect);
            var pipelineSelect = bvr.src_el.getElement("select[name='related_pipeline_code']")
            bvr.src_el.load_process_options(pipelineSelect);

            ''')


        title_wdg = self.get_title_wdg(process, node_type)
        top.add(title_wdg)


        settings_wdg = DivWdg()
        top.add(settings_wdg)
        settings_wdg.add_style("padding: 0px 10px")


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
        settings_wdg.add("<b>Start Workflow for Related Items::</b>")
        select = SelectWdg("related_search_type")
        settings_wdg.add(select)
        select.set_option("values", values)
        select.set_option("labels", labels)
        select.add_empty_option("-- Select --")
        settings_wdg.add("<span style='opacity: 0.6'>This process will track the progress of the items of the selected search type.</span>")
        settings_wdg.add("<br/>")


        self.add_session_behavior(select, "select", "spt_progress_top", "related_search_type")

        select.add_behavior( {
            'type': 'load',
            'project_code': project_code,
            'cbjs_action': '''

            var node = spt.pipeline.get_info_node();
            var version = spt.pipeline.get_node_kwarg(node, 'version');
            if (version && version != 1)
                return;

            var top = bvr.src_el.getParent(".spt_progress_top");
            top.load_pipeline_options(bvr.src_el);

            '''
        } )

        select.add_behavior( {
            'type': 'change',
            'cbjs_action': '''

            var top = bvr.src_el.getParent(".spt_progress_top");
            top.load_pipeline_options(bvr.src_el);

            '''
        } )



        settings_wdg.add("Expression")
        text = TextInputWdg(name="expression")
        settings_wdg.add(text)
        settings_wdg.add("<span style='opacity: 0.6'>Expression to find related items</span>")


        from pyasm.widget import RadioWdg

        settings_wdg.add("<br/>")
        settings_wdg.add("<b>Scope by which items to track:</b>")

        scope_div = DivWdg()
        settings_wdg.add(scope_div)
        scope_div.add_style("margin: 15px 25px")

        radio = RadioWdg("related_scope")
        radio.add_attr("value", "local")
        scope_div.add(radio)
        radio.set_checked()
        scope_div.add(" Only Related Items<br/>")

        self.add_session_behavior(radio, "radio", "spt_progress_top", "related_scope")

        radio = RadioWdg("related_scope")
        radio.add_attr("value", "global")
        scope_div.add(radio)
        scope_div.add(" All Items")
        scope_div.add("<br/>")

        self.add_session_behavior(radio, "radio", "spt_progress_top", "related_scope")




        search = Search("sthpw/pipeline")
        search.add_filter("search_type", related_search_type)
        search.add_project_filter()
        related_pipelines = search.get_sobjects()



        labels = ["%s (%s)" % (x.get_value("name"), x.get_value("search_type")) for x in related_pipelines]
        values = [x.get_value("code") for x in related_pipelines]



        settings_wdg.add("<br/>")
        settings_wdg.add("<b>Listen to Workflow</b>")
        select = SelectWdg("related_pipeline_code")
        settings_wdg.add(select)
        select.set_option("values", values)
        select.set_option("labels", labels)
        select.add_empty_option("-- %s --" % "any")
        settings_wdg.add("<span style='opacity: 0.6'>Determines which workflow to track.</span>")

        self.add_session_behavior(select, "select", "spt_progress_top", "related_pipeline_code")

        select.add_behavior( {
            'type': 'change',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_progress_top");
            top.load_process_options(bvr.src_el);

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
        settings_wdg.add(select)
        select.set_option("values", values)
        select.add_empty_option("-- %s --" % process)
        settings_wdg.add("<span style='opacity: 0.6'>Determines which process to track.  If empty, it will use the same process name.</span>")
        settings_wdg.add("<br/>")


        self.add_session_behavior(select, "select", "spt_progress_top", "related_process")

        settings_wdg.add("<br clear='all'/>")


        return top


    def get_default_kwargs(self):

        kwargs = super(ProgressInfoWdg, self).get_default_kwargs()

        workflow = self.workflow
        kwargs["related_search_type"] = workflow.get("search_type")
        kwargs["related_pipeline_code"] = workflow.get("pipeline_code")
        kwargs["related_process"] = workflow.get("process")
        kwargs["related_status"] = workflow.get("status")
        kwargs["related_scope"] = workflow.get("scope")
        kwargs["related_wait"] = workflow.get("wait")

        if not self.process_sobj:
            return kwargs

        process_sobj = self.process_sobj
        description = process_sobj.get_value("description")
        kwargs["description"] = description

        return kwargs



class TaskStatusInfoWdg(BaseInfoWdg):

    def get_display(self):

        process = self.kwargs.get("process")
        pipeline_code = self.kwargs.get("pipeline_code")
        node_type = self.kwargs.get("node_type")
        properties = self.kwargs.get("properties")

        process_code = properties.get("process_code")
        search = Search("config/process")
        search.add_filter("code", process_code)

        self.process_sobj = search.get_sobject()

        self.workflow = {}
        if self.process_sobj:
            self.workflow = self.process_sobj.get_json_value("workflow")
        if not self.workflow:
            self.workflow = {}

        top = self.top
        top.add_class("spt_status_top")
        top.add_class("spt_section_top")

        self.initialize_session_behavior(top)

        SessionalProcess.add_relay_session_behavior(top)

        top.add_behavior({
            'type': 'load',
            'cbjs_action': '''
            var toolTop = bvr.src_el.getParent(".spt_pipeline_tool_top");
            spt.pipeline.set_top(toolTop.getElement(".spt_pipeline_top"));

            var node = spt.pipeline.get_info_node();

            spt.pipeline.set_node_property(node, "type", "status");
            node.spt_node_type = "status";

            '''

            })

        title_wdg = self.get_title_wdg(process, node_type, show_node_type_select=False)
        top.add(title_wdg)

        color = Task.get_default_color(process)

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
        self.add_session_behavior(select, "select", "spt_status_top", "mapping")
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
        self.add_session_behavior(select, "select", "spt_status_top", "direction")
        select.set_option("values", values)
        select.set_option("labels", labels)

        settings_wdg.add("<br/>")

        div = DivWdg("to Status:")
        div.add_style('padding-bottom: 2px')
        settings_wdg.add(div)
        text = TextInputWdg(name="status")
        self.add_session_behavior(text, "text", "spt_status_top", "status")
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

        container = ColorContainerWdg(name="color")
        settings_wdg.add(container)

        color_wdg = container.get_color_wdg()

        color_wdg.add_behavior( {
            'type': 'load',
            'cbjs_action': '''

            var toolTop = bvr.src_el.getParent(".spt_pipeline_tool_top");
            spt.pipeline.set_top(toolTop.getElement(".spt_pipeline_top"));

            var node = spt.pipeline.get_info_node();
            var color = spt.pipeline.get_node_property(node, "color");
            bvr.src_el.value = color;

            '''
        } )

        color_wdg.add_behavior( {
            'type': 'change',
            'cbjs_action': '''

            var toolTop = bvr.src_el.getParent(".spt_pipeline_tool_top");
            spt.pipeline.set_top(toolTop.getElement(".spt_pipeline_top"));

            var node = spt.pipeline.get_info_node();
            var color = bvr.src_el.value;
            spt.pipeline.set_node_property(node, "color", color);

            spt.named_events.fire_event('pipeline|change', {});

            '''
        } )

        # settings_wdg.add(color_div)
        # color_input = ColorInputWdg("color")
        # color_input.add_behavior( {
        #     'type': 'load',
        #     'cbjs_action': '''

        #     var toolTop = bvr.src_el.getParent(".spt_pipeline_tool_top");
        #     spt.pipeline.set_top(toolTop.getElement(".spt_pipeline_top"));

        #     var node = spt.pipeline.get_info_node();
        #     var color = spt.pipeline.get_node_property(node, "color");
        #     bvr.src_el.value = color;
        #     bvr.src_el.setStyle("background", color);

        #     '''
        # } )

        # color_input.add_behavior( {
        #     'type': 'blur',
        #     'cbjs_action': '''

        #     var toolTop = bvr.src_el.getParent(".spt_pipeline_tool_top");
        #     spt.pipeline.set_top(toolTop.getElement(".spt_pipeline_top"));

        #     var node = spt.pipeline.get_info_node();
        #     var color = bvr.src_el.value;
        #     spt.pipeline.set_node_property(node, "color", color);

        #     spt.named_events.fire_event('pipeline|change', {});

        #     '''
        # } )
        # color_input.set_value(color)
        # settings_wdg.add(color_input)

        settings_wdg.add("<br/>")

        save_button = ActionButtonWdg(title="Save", color="primary")
        #settings_wdg.add(save_button)
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



    def get_default_kwargs(self):

        direction = self.workflow.get("direction")
        to_status = self.workflow.get("status")
        mapping = self.workflow.get("mapping")

        return {
            "direction": direction,
            "status": to_status,
            "mapping": mapping
        }


    def get_default_properties(self):

        process = self.kwargs.get("process")
        if self.process_sobj:
            color = self.process_sobj.get_value("color")
        else:
            color = Task.get_default_color(process)

        return {
            "color": color
        }




class ProcessInfoCmd(Command):

    def execute(self):
        node_type = self.kwargs.get("node_type")

        if node_type in ["manual", "node"]:
            return self.handle_manual()

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

        # Get custom save cmd via node_type
        from pyasm.command import CustomProcessConfig
        try:
            cmd = CustomProcessConfig.get_save_handler(node_type, self.kwargs)
            return cmd.execute()
        except Exception as e:
            print
            print("Failed saving node for node type [%s]:" % node_type)
            print(e)
            print
            return self.handle_default()


    def set_description(self, process_sobj):
        description = self.kwargs.get("description")
        if description or description == "":
            process_sobj.set_value("description", description)


    def handle_default(self):


        pipeline_code = self.kwargs.get("pipeline_code")
        process = self.kwargs.get("process")

        search = Search("config/process")
        search.add_filter("pipeline_code", pipeline_code)
        search.add_filter("process", process)
        process_sobj = search.get_sobject()

        description = self.kwargs.get("description")
        if not description:
            return

        process_sobj.set_value("description", description)

        process_sobj.commit()




    def handle_manual(self):

        pipeline_code = self.kwargs.get("pipeline_code")
        process = self.kwargs.get("process")

        search = Search("config/process")
        search.add_filter("pipeline_code", pipeline_code)
        search.add_filter("process", process)
        process_sobj = search.get_sobject()

        self.set_description(process_sobj)
        process_sobj.commit()

        cbk_classes = self.kwargs.get("_cbk_classes") or []

        handled = set()
        for cbk_class in cbk_classes:
            if cbk_class in handled:
                continue
            cmd = Common.create_from_class_path(cbk_class, {}, self.kwargs)
            cmd.execute()
            handled.add(cbk_class)



    def handle_action(self):

        is_admin = Environment.get_security().is_admin()

        action = self.kwargs.get("action") or "create_new"
        script = self.kwargs.get("script")
        script_path = self.kwargs.get("script_path")
        on_action_class = self.kwargs.get("on_action_class")


        # version 1 command handling
        version_str = self.kwargs.get('version') or 1
        version = int(version_str)
        command = self.kwargs.get("command")
        if version == 1 and command:
            action = command.get("action") or "create_new"
            script = command.get("script")
            script_path = command.get("script_path")
            on_action_class = command.get("on_action_class")


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

        from .trigger_wdg import TriggerToolWdg

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
                trigger.set_value("script_path", "NULL", quoted=False)

            trigger.set_value("class_name", "NULL", quoted=False)




        if execute_mode:
            trigger.set_value("mode", execute_mode)


        trigger.commit()

        if script:


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

        self.set_description(process_sobj)
        process_sobj.commit()



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

        color = Task.get_default_color(process)

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
        self.add_session_behavior(select, "select", "spt_status_top", "mapping")
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
        self.add_session_behavior(select, "select", "spt_status_top", "direction")
        select.set_option("values", values)
        select.set_option("labels", labels)

        settings_wdg.add("<br/>")

        div = DivWdg("to Status:")
        div.add_style('padding-bottom: 2px')
        settings_wdg.add(div)
        text = TextInputWdg(name="status")
        self.add_session_behavior(text, "text", "spt_status_top", "status")
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

        container = ColorContainerWdg(name="color")
        settings_wdg.add(container)

        color_wdg = container.get_color_wdg()

        color_wdg.add_behavior( {
            'type': 'load',
            'cbjs_action': '''

            var toolTop = bvr.src_el.getParent(".spt_pipeline_tool_top");
            spt.pipeline.set_top(toolTop.getElement(".spt_pipeline_top"));

            var node = spt.pipeline.get_info_node();
            var color = spt.pipeline.get_node_property(node, "color");
            bvr.src_el.value = color;

            '''
        } )

        color_wdg.add_behavior( {
            'type': 'change',
            'cbjs_action': '''

            var toolTop = bvr.src_el.getParent(".spt_pipeline_tool_top");
            spt.pipeline.set_top(toolTop.getElement(".spt_pipeline_top"));

            var node = spt.pipeline.get_info_node();
            var color = bvr.src_el.value;
            spt.pipeline.set_node_property(node, "color", color);

            spt.named_events.fire_event('pipeline|change', {});

            '''
        } )

        return top



    def get_default_kwargs(self):

        direction = self.workflow.get("direction")
        to_status = self.workflow.get("status")
        mapping = self.workflow.get("mapping")

        return {
            "direction": direction,
            "to_status": to_status,
            "mapping": mapping
        }


    def get_default_properties(self):

        process = self.kwargs.get("process")
        if self.process_sobj:
            color = self.process_sobj.get_value("color")
        else:
            color = Task.get_default_color(process)

        return {
            "color": color
        }




class ProcessInfoCmd(Command):

    def execute(self):
        node_type = self.kwargs.get("node_type")

        if node_type in ["manual", "node"]:
            return self.handle_manual()

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

        # Get custom save cmd via node_type
        from pyasm.command import CustomProcessConfig
        try:
            cmd = CustomProcessConfig.get_save_handler(node_type, self.kwargs)
            return cmd.execute()
        except Exception as e:
            print
            print("Failed saving node for node type [%s]:" % node_type)
            print(e)
            print
            return self.handle_default()


    def set_description(self, process_sobj):
        description = self.kwargs.get("description")
        if description or description == "":
            process_sobj.set_value("description", description)


    def handle_default(self):


        pipeline_code = self.kwargs.get("pipeline_code")
        process = self.kwargs.get("process")

        search = Search("config/process")
        search.add_filter("pipeline_code", pipeline_code)
        search.add_filter("process", process)
        process_sobj = search.get_sobject()

        description = self.kwargs.get("description")
        if not description:
            return

        process_sobj.set_value("description", description)

        process_sobj.commit()




    def handle_manual(self):

        pipeline_code = self.kwargs.get("pipeline_code")
        process = self.kwargs.get("process")

        search = Search("config/process")
        search.add_filter("pipeline_code", pipeline_code)
        search.add_filter("process", process)
        process_sobj = search.get_sobject()

        self.set_description(process_sobj)
        process_sobj.commit()

        cbk_classes = self.kwargs.get("_cbk_classes") or []

        handled = set()
        for cbk_class in cbk_classes:
            if cbk_class in handled:
                continue
            cmd = Common.create_from_class_path(cbk_class, {}, self.kwargs)
            cmd.execute()
            handled.add(cbk_class)

        settings = process_sobj.get_json_value("workflow") or {}
        node_type = settings.get("node_type") or "manual"
        if node_type in ['manual', 'approval', 'action', 'condition', 'hierarchy', 'progress', 'dependency']:
            return

        # Get custom save cmd via node_type
        from pyasm.command import CustomProcessConfig
        try:
            cmd = CustomProcessConfig.get_save_handler(node_type, self.kwargs)
        except:
            cmd = None
        if cmd:
            return cmd.execute()



    def handle_action(self):

        is_admin = Environment.get_security().is_admin()

        action = self.kwargs.get("action") or "create_new"
        script = self.kwargs.get("script")
        script_path = self.kwargs.get("script_path")
        on_action_class = self.kwargs.get("on_action_class")


        # version 1 command handling
        version_str = self.kwargs.get('version') or 1
        version = int(version_str)
        command = self.kwargs.get("command")
        if version == 1 and command:
            action = command.get("action") or "create_new"
            script = command.get("script")
            script_path = command.get("script_path")
            on_action_class = command.get("on_action_class")


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

        from .trigger_wdg import TriggerToolWdg

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
                trigger.set_value("script_path", "NULL", quoted=False)

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

        self.set_description(process_sobj)
        process_sobj.commit()



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
        self.set_description(process_sobj)
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
        self.set_description(process_sobj)
        process_sobj.commit()

        cbk_classes = self.kwargs.get("_cbk_classes") or []

        handled = set()
        for cbk_class in cbk_classes:
            if cbk_class in handled:
                continue
            cmd = Common.create_from_class_path(cbk_class, {}, self.kwargs)
            cmd.execute()
            handled.add(cbk_class)


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
        self.set_description(process_sobj)
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
        if subpipeline_code:
            process_sobj.set_value("subpipeline_code", subpipeline_code)
        process_sobj.commit()

        task_creation = self.kwargs.get("task_creation") or "subtasks_only"
        data['task_creation'] = task_creation

        process_sobj.set_value("workflow", data)
        self.set_description(process_sobj)
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
        self.set_description(process_sobj)
        process_sobj.commit()




class NewProcessInfoCmd(Command):


    def execute(self):

        self.pipeline_code = self.kwargs.get("pipeline_code")
        self.process = self.kwargs.get("process")
        self.pipeline = Pipeline.get_by_code(self.pipeline_code)

        search = Search("config/process")
        search.add_filter("pipeline_code", self.pipeline_code)
        search.add_filter("process", self.process)
        self.process_sobj = search.get_sobject()
        if not self.process_sobj:
            print("Process does not exist")
            return
        self.workflow = self.process_sobj.get_json_value("workflow") or {}

        description = self.kwargs.get("description")
        if description or description == "":
            self.process_sobj.set_value("description", description)

        # custom behavior depending on type
        node_type = self.kwargs.get("node_type")
        if node_type in ["action", "condition"]:
            self.handle_action()
        elif node_type == 'hierarchy':
            self.handle_hierarchy()
        elif node_type == 'progress':
            self.handle_progress()
        elif node_type == 'status':
            self.handle_status()


        # set node workflow data
        workflow = {}
        self.filtered_keys = set(['process', 'pipeline_code', 'None'])
        workflow = self.populate_workflow(workflow, self.kwargs)

        self.process_sobj.set_json_value("workflow", workflow)

        self.process_sobj.commit()

        # custom callback classes
        cbk_classes = self.kwargs.get("_cbk_classes") or []
        handled = set()
        for cbk_class in cbk_classes:
            if cbk_class in handled:
                continue
            cmd = Common.create_from_class_path(cbk_class, {}, self.kwargs)
            cmd.execute()
            handled.add(cbk_class)

        if node_type in ['manual', 'approval', 'action', 'condition', 'hierarchy', 'progress', 'dependency']:
            return

        # Get custom save cmd via node_type
        from pyasm.command import CustomProcessConfig
        cmd = CustomProcessConfig.get_save_handler(node_type, self.kwargs)
        if cmd:
            return cmd.execute()



    def populate_workflow(self, workflow, data):

        for key in data:
            value = data.get(key)
            is_empty = value == None or value == ""
            unwanted_keys = key.startswith('_') or key in self.filtered_keys

            if (is_empty or unwanted_keys):
                continue

            if (isinstance(value, dict)):
                value = self.populate_workflow({}, value)

            workflow[key] = value

        return workflow



    def handle_action(self):
        is_admin = Environment.get_security().is_admin()

        action_kwargs = self.kwargs.get("default") or {}
        action = action_kwargs.get("action") or "create_new"
        script = action_kwargs.get("script")
        script_path = action_kwargs.get("script_path")
        on_action_class = action_kwargs.get("on_action_class")
        execute_mode = action_kwargs.get("execute_mode")

        if is_admin:
            language = action_kwargs.get("language")
            if not language:
                language = "python"
        else:
            language = "server_js"

        event = "process|action"

        from .trigger_wdg import TriggerToolWdg

        folder = "%s/%s" % (TriggerToolWdg.FOLDER_PREFIX, self.pipeline_code)
        title = self.process_sobj.get_code()

        # check to see if the trigger already exists
        search = Search("config/trigger")
        search.add_filter("event", event)
        search.add_filter("process", self.process_sobj.get_code())
        trigger = search.get_sobject()
        if not trigger:
            # create a new one
            trigger = SearchType.create("config/trigger")
            trigger.set_value("event", event)
            trigger.set_value("process", self.process_sobj.get_code())

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
                trigger.set_value("script_path", "NULL", quoted=False)

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


    def handle_hierarchy(self):

        hierarchy_kwargs = self.kwargs.get("hierarchy") or {}
        subpipeline_code = hierarchy_kwargs.get("subpipeline")

        if not subpipeline_code:
            default = self.kwargs.get("default")
            if default:
                subpipeline_code = default.get("subpipeline")

        if subpipeline_code:
            self.process_sobj.set_value("subpipeline_code", subpipeline_code)


    def handle_progress(self):

        progress_kwargs = self.kwargs.get("progress") or {}
        search_type = self.pipeline.get_value("search_type")

        related_search_type = progress_kwargs.get("related_search_type")
        related_process = progress_kwargs.get("related_process")
        if not related_process:
            progress_kwargs['related_process'] = self.process
        related_scope = progress_kwargs.get("related_scope")
        if not related_scope:
            progress_kwargs['related_scope'] = "local"

        # find a related trigger
        old_kwargs = self.workflow.get("progress") or {}
        trigger_code = old_kwargs.get('trigger_code')
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
        trigger.set_value("description", "Listener for [%s] from [%s]" % (self.process, search_type))
        trigger.set_value("mode", "same process,same transaction")
        trigger.set_value("process", related_process)

        data = {
                "process_code": self.process_sobj.get_code(),
                "pipeline_code": self.pipeline_code,
                "search_type": search_type,
        }
        trigger.set_json_value("data", data)
        trigger.commit()

        trigger_code = trigger.get_code()
        progress_kwargs['trigger_code'] = trigger_code

        self.kwargs['progress'] = progress_kwargs


    def handle_status(self):

        status_kwargs = self.kwargs.get("default") or {}

        color = status_kwargs.get("color")
        if color:
            self.process_sobj.set_value("color", color)

        mapping = status_kwargs.get("mapping")
        if mapping:
            self.kwargs['mapping'] = mapping

        direction = status_kwargs.get("direction")
        if direction:
            self.kwargs['direction'] = direction

        status = status_kwargs.get("status")
        if status:
            self.kwargs['status'] = status


class PipelineEditorWdg(BaseRefreshWdg):
    '''This is the pipeline on its own, with various buttons and interface
    to help in building the pipelines.  It contains the PipelineCanvasWdg'''

    def get_styles(self):

        styles = HtmlElement.style('''

            .spt_pipeline_editor_top .spt_pipeline_editor_shelf .search-box {
                float: right;
                margin: 3px;
                height: 26px;
                padding: 2px 6px;
                width: 164px;
                border: 1px solid #ccc;
            }

            .spt_pipeline_editor_top {
                overflow: auto;
                width: 100%;
                height: 100%;
            }

            .spt_pipeline_editor_inner_top {
                width: 100%;
                height: 100%;
            }

            .spt_pipeline_wrapper {
                height: calc(100% - 33px);
            }

            .spt_has_changes .spt_hit_wdg.spt_save_button {
                background: var(--spt_palette_background2);
            }


            ''')

        return styles


    def get_display(self):
        top = self.top
        self.set_as_panel(top)
        top.add_class("spt_pipeline_editor_top")

        has_change_action = '''
            bvr.src_el.addClass("spt_has_changes");
        '''

        top.add_named_listener('pipeline|change', has_change_action)

        self.save_new_event = self.kwargs.get("save_new_event")
        self.show_gear = self.kwargs.get("show_gear")

        inner = DivWdg()
        top.add(inner)
        inner.add_class("spt_pipeline_editor_inner_top")

        inner.add(self.get_styles())

        shelf_wdg = self.get_shelf_wdg()
        inner.add(shelf_wdg)

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
        // var server = TacticServerStub.get();
        // server.get_unique_sobject( "config/process", data );

        // save the pipeline when a new node is added
        // spt.named_events.fire_event('pipeline|save_button', bvr );

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
            let focused = document.querySelector(":focus");
            if (focused) focused.blur();

            spt.named_events.fire_event('pipeline|hide_info', {});

        ''' } )




        if self.kwargs.get("is_refresh") == 'true':
            return inner
        else:
            return top

    def get_node_search_wdg(self):

        node_search_wdg = DivWdg()

        node_search = HtmlElement.text()
        node_search_wdg.add(node_search)

        node_search.add_class("spt_node_search")
        node_search.add_class("search-box")
        node_search.add_attr("placeholder", "Find node by name")


        node_search.add_behavior({
            'type': 'click_up',
            'cbjs_action': '''

            var top = bvr.src_el.getParent(".spt_pipeline_tool_top");
            var results = top.getElement(".spt_node_search_results");

            results.setStyle("display", "");
            spt.body.add_focus_element(results);

            '''
            })


        node_search.add_behavior({
            'type': 'keyup',
            'cbjs_action': '''

            var key = evt.key;

            var top = bvr.src_el.getParent(".spt_pipeline_tool_top");
            var results = top.getElement(".spt_node_search_results");
            var template = results.getElement(".search-result-template");

            results.setStyle("display", "");
            spt.body.add_focus_element(results);

            var oldItems = results.getElements(".spt_node_search_result");

            if (key == "down") {
                // down selection

                var selectedItem = results.getElement(".selected");
                if (selectedItem) {
                    var nextItem = selectedItem.nextSibling;
                    if (nextItem) if (nextItem.hasClass("search-result-template")) nextItem = nextItem.nextSibling;
                    selectedItem.removeClass("selected");
                }

                if (!nextItem) nextItem = oldItems[0];
                if (!nextItem) return;

                nextItem.addClass("selected");
                nextItem.scrollIntoView(false);

            } else if (key == "up") {
                // up selection

                var selectedItem = results.getElement(".selected");
                if (selectedItem) {
                    var nextItem = selectedItem.previousSibling;
                    if (nextItem) if (nextItem.hasClass("search-result-template")) nextItem = nextItem.previousSibling;
                    selectedItem.removeClass("selected");
                }

                if (!nextItem) nextItem = oldItems[oldItems.length-1];
                if (!nextItem) return;

                nextItem.addClass("selected");
                nextItem.scrollIntoView(false);

            } else if (key == "enter") {
                // check if theres a selected item, if so click

                var selectedItem = results.getElement(".selected");
                if (selectedItem) selectedItem.click();

            } else if (key == "esc") {
                // blur search

                bvr.src_el.blur();
                results.on_complete(results);

            } else {
                // Load in new search results

                oldItems.forEach(function(oldItem){
                    oldItem.remove();
                });

                spt.pipeline.set_top(top.getElement(".spt_pipeline_top"));
                var nodes = spt.pipeline.get_all_nodes();

                nodes.forEach(function(node){
                    var title = node.getAttribute("title");
                    if (!title.toLowerCase().contains(bvr.src_el.value.toLowerCase())) return;

                    var item = spt.behavior.clone(template);
                    item.removeClass("search-result-template");
                    item.addClass("spt_node_search_result");
                    item.innerText = title;
                    results.appendChild(item);
                });



            }

            '''
        })


        if self.kwargs.get("show_help") not in ['false', False]:

            help_button = HtmlElement.button("?")
            node_search_wdg.add(help_button)
            help_button.add_class("btn-default btn spt_label hand btn-sm")
            help_button.add_behavior( {
                'type': 'click_up',
                'cbjs_action': '''
                spt.help.set_top();
                spt.help.load_alias("project-workflow|project-workflow-introduction|pipeline-process-options");
                '''
            } )

        return node_search_wdg



    def get_shelf_wdg(self):

        shelf_wdg = DivWdg()
        shelf_wdg.add_class("spt_pipeline_editor_shelf")
        shelf_wdg.add_class("d-flex justify-content-between")

        # FIXME: Would prefer not to hardcode height
        shelf_wdg.add_style("height: 33px")

        show_shelf = self.kwargs.get("show_shelf")
        show_shelf = True
        if show_shelf in ['false', False]:
            show_shelf = False
        else:
            show_shelf = True
        if not show_shelf:
            shelf_wdg.add_style("display: none")


        show_gear = self.kwargs.get("show_gear")
        button_div = self.get_buttons_wdg(show_gear)
        shelf_wdg.add(button_div)

        button_div = self.get_zoom_buttons_wdg()
        shelf_wdg.add(button_div)

        """
        button_div = self.get_schema_buttons_wdg();
        button_div.add_style("margin-left: 10px")
        button_div.add_style("float: left")
        shelf_wdg.add(button_div)
        """


        node_search_wdg = self.get_node_search_wdg()
        shelf_wdg.add(node_search_wdg)

        return shelf_wdg


    def get_canvas(self):
        node_types = [
            'manual',
            'action',
            'condition',
            'approval',
            'hierarchy',
            'dependency',
            'progress',
            'status'
        ]


        search = Search("config/widget_config")
        search.add_filter("category", "workflow")
        configs = search.get_sobjects()
        for config in configs:
            node_types.append(config.get_value("view"))

        is_editable = self.kwargs.get("is_editable")
        canvas = PipelineToolCanvasWdg(height=self.height, width=self.width, is_editable=is_editable,
            use_mouse_wheel=True, node_types=node_types)
        return canvas



    def get_buttons_wdg(self, show_gear):


        button_row = DivWdg()

        project_code = Project.get_project_code()

        if self.kwargs.get("show_wrench") not in [False, "false"]:
            button = ButtonNewWdg(title="Add node", icon="FA_WRENCH", sub_icon="FA_PLUS")
            button_row.add(button)

            button.add_behavior({
                'type': 'click',
                'cbjs_action': '''
                    spt.process_tool.toggle_side_bar(bvr.src_el);
                '''
            } )


        if self.kwargs.get("show_save") not in [False, "false"]:
            button = self.get_save_button()
            button_row.add(button)



        expr = "@GET(sthpw/pipeline['code','like','%/__TEMPLATE__'].config/process.process)"
        processes = Search.eval(expr)
        processes.sort()



        button = ButtonNewWdg(title="Delete Selected", icon="FA_TRASH")
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
            button = ButtonNewWdg(title="Extra View", icon="FA_COG", show_arrow=True)
            button_row.add(button)

            tab = PipelineTabWdg()
            menu = tab.get_extra_tab_menu()

            menus = [menu.get_data()]
            SmartMenu.add_smart_menu_set( button.get_button_wdg(), { 'DG_BUTTON_CTX': menus } )
            SmartMenu.assign_as_local_activator( button.get_button_wdg(), "DG_BUTTON_CTX", True )


        button = ButtonNewWdg(title="Show workflow info", icon="FA_INFO")
        button_row.add(button)
        div = DivWdg()
        widget_key = div.generate_widget_key('tactic.ui.tools.PipelineInfoWdg', inputs={'pipeline_code': '__WIDGET_UNKNOWN__'})
        button.add_behavior({
            'type': 'click',
            "widget_key": widget_key,
            'cbjs_action': '''

            var toolTop = bvr.src_el.getParent(".spt_pipeline_tool_top");
            spt.pipeline.set_top(toolTop.getElement(".spt_pipeline_top"));
            var info = toolTop.getElement(".spt_pipeline_tool_info");

            if (!info) return;

            var nodes = spt.pipeline.get_all_nodes();
            for (var i=0; i<nodes.length; i++) {
                var node = nodes[i];
                spt.pipeline.unselect_node(node);
            }

            var group_name = spt.pipeline.get_current_group();

            var class_name = bvr.widget_key;
            var kwargs = {
                pipeline_code: group_name,
            }

            var callback = function() {
                spt.named_events.fire_event('pipeline|show_info', {});
            }
            spt.panel.load(info, class_name, kwargs, {}, {callback: callback});


            '''

            })

        preview_button = ButtonNewWdg(title="Workflow Schedule Preview", icon="FA_EYE")
        tmp_div = DivWdg()
        pipeline_code = self.kwargs.get("pipeline") or "__WIDGET_UNKNOWN__"
        inputs = {
            'nodes_properties': "__WIDGET_UNKNOWN__",
            'pipeline_code': pipeline_code,
            'pipeline_xml': '__WIDGET_UNKNOWN__'
            }
        widget_key = tmp_div.generate_widget_key("tactic.ui.table.WorkflowSchedulePreviewWdg", inputs=inputs)
        preview_button.add_behavior({
            'type': 'click',
            'widget_key': widget_key,
            'cbjs_action': '''
            var toolTop = bvr.src_el.getParent('.spt_pipeline_tool_top');
            spt.pipeline.set_top(toolTop.getElement(".spt_pipeline_top"));
            var pipeline_code = spt.pipeline.get_current_group();
            var pipeline_xml = spt.pipeline.export_group(pipeline_code);
            var nodes = spt.pipeline.get_all_nodes();
            var widget_key = bvr.widget_key;
            var nodes_properties = {};
            for (var i=0; i<nodes.length; i++) {
                var node_name = spt.pipeline.get_node_name(nodes[i]);
                nodes_properties[node_name] = spt.pipeline.get_node_kwargs(nodes[i]);
            }
            args = {
                pipeline_code: pipeline_code,
                pipeline_xml: pipeline_xml,
                nodes_properties: nodes_properties
            }
            kwargs = {
                width: 900
            }
            spt.panel.load_popup("Workflow Schedule Preview", widget_key, args, kwargs);
            '''
        })

        button_row.add(preview_button)

        button_row.add_class("d-flex")

        return button_row

    def get_save_button(self):

        project_code = Project.get_project_code()

        button = ButtonNewWdg(title="Save Current Workflow", icon="FA_SAVE")
        button.add_class("spt_save_button")
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
        var toolTop = bvr.src_el.getParent(".spt_pipeline_tool_top");
        spt.pipeline.set_top(toolTop.getElement(".spt_pipeline_top"));

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
            var description = data.descriptions[group_name];

            var group = spt.pipeline.get_group(group_name);
            var default_template = data.default_templates[group_name];
            var node_index = group.get_data("node_index");
            var pipeline_data = {
                default_template: default_template,
                node_index: node_index
            };

            var nodes = spt.pipeline.get_nodes_by_group(group_name);
            var node_kwargs = {};
            for (var i=0; i<nodes.length; i++) {
                var node = nodes[i];

                if (!node.has_changes) {
                    continue;
                }

                var name = spt.pipeline.get_node_name(node);
                name = name.replace(/&/g, "&amp;amp;");
                var kwargs = spt.pipeline.get_node_kwargs(node);
                var node_description = kwargs.description;
                var on_saves = node.on_saves;
                var version = kwargs.version;

                if (kwargs.multi) kwargs = spt.pipeline.get_node_multi_kwargs(node);
                if (on_saves) {
                    for (var key in on_saves) {
                        var on_save = on_saves[key];
                        kwargs = on_save(kwargs);

                        if (kwargs.is_error) return;
                    }
                }

                kwargs.description = node_description;
                kwargs.version = version;
                node_kwargs[name] = kwargs;
            }

            server = TacticServerStub.get();
            spt.app_busy.show("Saving project-specific pipeline ["+group_name+"]",null);

            try {
                var xml = spt.pipeline.export_group(group_name);
            } catch (err) {
                spt.alert("Error while parsing xml: " + err);
                return;
            }

            var search_key = server.build_search_key("sthpw/pipeline", group_name);
            try {
                var args = {
                    search_key: search_key,
                    pipeline:xml,
                    color:color,
                    description: description,
                    project_code: bvr.project_code,
                    node_kwargs: node_kwargs,
                    pipeline_data: pipeline_data
                };
                server.execute_cmd('tactic.ui.tools.PipelineSaveCbk', args);
                spt.named_events.fire_event('pipeline|save', {});

                // reset all of the changes on the node
                for (var i=0; i<nodes.length; i++) {
                    var node = nodes[i];
                    node.has_changes = false;
                }

                spt.notify.show_message("Saved");



            } catch(e) {
                spt.alert(spt.exception.handler(e));
            }

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

        return button

    def get_zoom_buttons_wdg(self):

        button_row = DivWdg()
        button_row.add_class("d-flex")

        button = ButtonNewWdg(title="Undo", icon="FA_UNDO", show_out=False)
        button_row.add(button)
        button.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        spt.command.undo_last();
        '''
        } )


        button = ButtonNewWdg(title="Redo", icon="FA_REDO", show_out=False)
        button_row.add(button)
        button.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        spt.command.redo_last();
        '''
        } )

        button = ButtonNewWdg(title="Zoom In", icon="FA_SEARCH_PLUS", show_out=False)
        button_row.add(button)
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



        button = ButtonNewWdg(title="Zoom Out", icon="FA_SEARCH_MINUS", show_out=False)
        button_row.add(button)

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
        select.add_class("form-control")
        select.set_option("labels", ["10%", "25%", "50%", "75%", "100%", "125%", "150%", "----", "Fit To Canvas"])
        select.set_option("values", ["0.1", "0.25", "0.50", "0.75", "1.0", "1.25", "1.5", "", "fit_to_canvas"])
        select.add_empty_option("Zoom")
        button_row.add(select)
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

        process = self.kwargs.get("process")
        pipeline_code = self.kwargs.get("pipeline_code")
        node_type = self.kwargs.get("node_type")
        properties = self.kwargs.get("properties") or {}

        process_code = properties.get("process_code") or ""
        search = Search("config/process")
        search.add_filter("code", process_code)

        self.process_sobj = search.get_sobject()
        process_sobj = self.process_sobj

        pipeline = Search.get_by_code("sthpw/pipeline", pipeline_code)

        workflow = {}
        if process_sobj:
            workflow = process_sobj.get_json_value("workflow")
        if not workflow:
            workflow = {}
        self.workflow = workflow

        div = DivWdg()
        div.add_class("spt_pipeline_properties_top")
        div.add_class("spt_section_top")

        SessionalProcess.add_relay_session_behavior(div, "properties")

        div.add_style("min-width: 500px")
        self.initialize_session_behavior(div)

        div.add_behavior( {
            'type': 'load',
            'cbjs_action': '''
            var on_save = function(kwargs) {
                var cbk_class = "tactic.ui.tools.PipelinePropertyCbk";
                if (kwargs._cbk_classes) {
                    if (!kwargs._cbk_classes.contains(cbk_class)) {
                        kwargs._cbk_classes.push(cbk_class);
                    }
                }
                else kwargs._cbk_classes = [cbk_class];

                return kwargs;
            }

            var node = spt.pipeline.get_info_node();
            spt.pipeline.add_node_on_save(node, "pipeline_property", on_save);
            '''
            } )


        from tactic.ui.app import HelpButtonWdg
        help_button = HelpButtonWdg(alias='pipeline-process-options|project-workflow-introduction')
        div.add( help_button )
        help_button.add_style("margin-top: 2px")
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
        title_div.add_color("background", "background", -13)
        title_div.add_class("spt_property_title")
        if not process:
            title_div.add("Process: <i>--None--</i>")
        else:
            title_div.add("Process: %s" % process)
        title_div.add_style("font-weight: bold")
        title_div.add_style("padding: 10px 5px")


        # add a no process message
        no_process_wdg = DivWdg()
        no_process_wdg.add_class("spt_pipeline_properties_no_process")
        div.add(no_process_wdg)
        no_process_wdg.add( "No process node or connector selected")
        no_process_wdg.add_style("padding: 30px")



        # get a list of known properties
        if node_type == "approval":
            properties = ['group', "completion", 'task_pipeline', 'assigned_group', 'duration', 'bid_duration', 'color']
        else:
            properties = ['group', "completion", "task_pipeline", 'assigned_group', 'supervisor_group', 'duration', 'bid_duration', 'color']


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



        # table.add_behavior( {
        # 'type': 'load',
        # 'cbjs_action': self.get_onload_js()
        # } )


        # group
        # Making invisible to ensure that it still gets recorded if there.
        tr = table.add_row()
        tr.add_style("display: none")
        td = table.add_cell('Group: ')
        td.add_style("width: 250px")
        td.add_attr("title", "Nodes can grouped together within a workflow")
        #td.add_style("width: 200px")
        text_name = "group"
        text = TextWdg(text_name)
        text.add_class(text_name)
        self.add_session_behavior(text, "text", "spt_pipeline_properties_top", text_name)

        if "completion" in properties:
            th = table.add_cell(text)
            th.add_style("height: 30px")

            # completion (visibility depends on sType)
            table.add_row(css='status_completion')
            td = table.add_cell('Completion (0 to 100):')
            td.add_attr("title", "Determines the completion level that this node represents.")

            text_name = "completion"
            text = TextInputWdg(name=text_name, type="number")
            text.add_class(text_name)
            self.add_session_behavior(text, "text", "spt_pipeline_properties_top", text_name)

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
            table.add_row(css='task_status_pipeline')
            td = table.add_cell('Task Status Workflow')
            td.add_attr("title", "The task status workflow determines all of the statuses that occur within this process")

            text_name = "task_pipeline"
            select = SelectWdg(text_name)


            for pipeline in task_pipelines:
                label = '%s (%s)' %(pipeline.get_value('name'), pipeline.get_value('code'))
                select.append_option(label, pipeline.get_value('code'))

            select.add_empty_option('-- Select --')
            select.add_class(text_name)
            self.add_session_behavior(select, "select", "spt_pipeline_properties_top", text_name)

            th = table.add_cell(select)
            th.add_style("height: 40px")



        # The search needed for the login_group select widgets

        from pyasm.security import Sudo
        sudo = Sudo()
        try:
            login_group_search = Search('sthpw/login_group')
        finally:
            sudo.exit()

        # assigned_group
        table.add_row()
        td = table.add_cell('Assigned Group:')
        td.add_attr("title", "Used for limiting the users displayed when this process is chosen in a task view.")

        text_name = "assigned_group"
        select = SelectWdg(text_name)
        select.set_search_for_options(login_group_search, 'login_group', 'login_group')
        select.add_empty_option('-- Select --')
        select.add_class(text_name)
        self.add_session_behavior(select, "select", "spt_pipeline_properties_top", text_name)

        th = table.add_cell(select)
        th.add_style("height: 40px")

        if "supervisor_group" in properties:
            # supervisor_group
            table.add_row()
            td = table.add_cell('Supervisor Group:')
            td.add_attr("title", "Used for limiting the supervisors displayed when this process is chosen in a task view.")
            text_name = "supervisor_group"
            select = SelectWdg(text_name)
            select.set_search_for_options(login_group_search, 'login_group', 'login_group')
            select.add_empty_option('-- Select --')
            select.add_class(text_name)
            self.add_session_behavior(select, "select", "spt_pipeline_properties_top", text_name)

            th = table.add_cell(select)
            th.add_style("height: 40px")

        # duration
        table.add_row()
        td = table.add_cell('Default Start to End Duration:')
        td.add_attr("title", "The default duration determines the starting duration of a task that is generated for this process")

        text_name = "duration"
        text = TextWdg(text_name)
        text.add_style("width: 40px")
        text.add_class(text_name)
        text.add_style("text-align: center")
        self.add_session_behavior(text, "text", "spt_pipeline_properties_top", text_name)

        th = table.add_cell(text)
        th.add_style("height: 40px")
        th.add(" days")

        # bid duration in hours
        table.add_row()
        td = table.add_cell('Expected Work Hours:')
        td.add_attr("title", "The default bid duration determines the estimated number of hours will be spent on this task.")

        text_name = "bid_duration"
        text = TextWdg(text_name)
        text.add_style("width: 40px")
        text.add_class(text_name)
        text.add_style("text-align: center")
        self.add_session_behavior(text, "text", "spt_pipeline_properties_top", text_name)

        th = table.add_cell(text)
        th.add_style("height: 40px")
        th.add(" hours")

        # task creation
        table.add_row()
        td = table.add_cell('Task Creation:')
        td.add_attr("title", "Determines if node creates a task.")

        text_name = "task_creation"
        check = CheckboxWdg(text_name)
        self.add_session_behavior(check, "checkbox", "spt_pipeline_properties_top", text_name)

        th = table.add_cell(check)
        th.add_style("height: 40px")

        # autocreate task
        table.add_row()
        td = table.add_cell('Autocreate task:')
        td.add_attr("title", "Creates task when message sent to node.")

        text_name = "autocreate_task"
        check = CheckboxWdg(text_name)
        self.add_session_behavior(check, "checkbox", "spt_pipeline_properties_top", text_name)

        th = table.add_cell(check)
        th.add_style("height: 40px")

        # ---- Divider -----
        tr, td = table.add_row_cell()
        td.add("<hr/>")

        # Color
        table.add_row()
        td = table.add_cell('Color:')
        td.add_attr("title", "Used by various parts of the interface to show the color of this process.")

        text_name = "color"
        color = ColorContainerWdg(name=text_name)
        color_wdg = color.get_color_wdg()
        self.add_session_behavior(color_wdg, "color", "spt_pipeline_properties_top", text_name)

        color_wdg.add_behavior( {
            'type': 'load',
            'cbjs_action': '''

            var node = spt.pipeline.get_info_node();
            var toolTop = node.getParent(".spt_pipeline_tool_top");
            spt.pipeline.set_top(toolTop.getElement(".spt_pipeline_top"));

            var color = spt.pipeline.get_node_property(node, "color");
            bvr.src_el.value = color;

            '''
        } )

        color_wdg.add_behavior( {
            'type': 'change',
            'cbjs_action': '''

            var node = spt.pipeline.get_info_node();
            var toolTop = node.getParent(".spt_pipeline_tool_top");
            spt.pipeline.set_top(toolTop.getElement(".spt_pipeline_top"));

            var color = bvr.src_el.value;
            spt.pipeline.set_node_property(node, "color", color);

            var color1 = spt.css.modify_color_value(color, +10);
            var color2 = spt.css.modify_color_value(color, -10);

            if (spt.pipeline.get_node_type(node) == "condition") {
                angle = 225;
            } else {
                angle = 180;
            }

            node.getElement(".spt_content").setStyle("background", "linear-gradient("+angle+"deg, "+color1+", 70%, "+color2+")");

            spt.named_events.fire_event('pipeline|change', {});

            '''
        } )

        # text = TextWdg(text_name)
        # color = ColorInputWdg(text_name)
        # color.set_input(text)
        # text.add_class(text_name)
        # self.add_session_behavior(text, "text", "spt_pipeline_properties_top", text_name)
        # text.add_behavior( {
        #     'type': 'load',
        #     'cbjs_action': '''

        #     var node = spt.pipeline.get_info_node();
        #     var properties = spt.pipeline.get_node_kwarg(node, "properties");
        #     if (properties) {
        #         var color = properties.color;
        #         if (color)
        #             bvr.src_el.setStyle("background", color);
        #     }

        #     '''
        # } )

        td = table.add_cell(color)
        th.add_style("height: 40px")

        # label
        table.add_row()
        td = table.add_cell('Label:')

        text_name = "label"
        text = TextWdg(text_name)
        text.add_class(text_name)
        self.add_session_behavior(text, "text", "spt_pipeline_properties_top", text_name)

        td = table.add_cell(text)
        td.add_style("height: 40px")

        tr, td = table.add_row_cell()

        # button = ActionButtonWdg(title="Save", tip="Confirm properties change. Remember to save workflow at the end.", color="primary", width=200)
        # td.add("<hr/>")
        # td.add(button)
        # #button.add_style("float: right")
        # #button.add_style("margin-right: 20px")
        # button.add_style("margin: 15px auto")
        # td.add("<br clear='all'/>")
        # td.add("<br clear='all'/>")
        # button.add_behavior( {
        # 'type': 'click_up',
        # 'properties': properties,
        # 'cbjs_action': '''
        # var top = bvr.src_el.getParent(".spt_pipeline_properties_top");
        # var node = spt.pipeline.get_selected_node();
        # if (!node) {
        #     alert("No node selected");
        #     return;
        # }
        # spt.pipeline_properties.set_properties2(top, node, bvr.properties);


        # var top = bvr.src_el.getParent(".spt_popup");
        # spt.popup.close(top);

        # spt.named_events.fire_event('pipeline|change', {});

        # spt.named_events.fire_event('pipeline|save_button', bvr );
        # '''
        # } )



        return div



    def initialize_session_behavior(self, info):


        kwargs = self.get_default_kwargs()
        info.add_behavior({
            'type': 'load',
            'kwargs': kwargs,
            'cbjs_action': '''

            var node = spt.pipeline.get_info_node();
            var version = spt.pipeline.get_node_kwarg(node, 'version');

            if (version && version != 1) {
                var settings = spt.pipeline.get_node_property(node, 'settings');
                if (settings.properties) return;
                settings['properties'] = bvr.kwargs;
                spt.pipeline.set_node_kwargs(node, settings);
            } else {
                var kwargs = spt.pipeline.get_node_kwargs(node);
                Object.assign(bvr.kwargs, kwargs);
                spt.pipeline.set_node_kwargs(node, bvr.kwargs);
            }


            '''
        })



    def get_default_kwargs(self):

        # FIXME: find better way to detect default, not using color
        if (not self.workflow.get("task_creation") and not self.workflow.get("color")):
            task_creation = True
        else:
            task_creation = self.workflow.get("task_creation")

        autocreate_task = True if self.workflow.get("autocreate_task") == True else False

        return {
            "group": self.workflow.get("group"),
            "completion": self.workflow.get("completion"),
            "task_pipeline": self.workflow.get("task_pipeline"),
            "assigned_group": self.workflow.get("assigned_group"),
            "supervisor_group": self.workflow.get("supervisor_group"),
            "duration": self.workflow.get("duration"),
            "bid_duration": self.workflow.get("bid_duration"),
            "color": self.workflow.get("color"),
            "label": self.workflow.get("label"),
            "task_creation": task_creation,
            "autocreate_task": autocreate_task
        }



    def add_session_behavior(self, input_wdg, input_type, top_class, arg_name):

        # On load behavior, displays sessional value
        load_behavior = {
            'type': 'load',
            'arg_name': arg_name,
            'cbjs_action': '''
            var node = spt.pipeline.get_info_node();
            spt.pipeline.set_input_value_from_kwargs(node, bvr.arg_name, bvr.src_el);
            '''
        }

        cbjs_action_default = '''

        var node = spt.pipeline.get_info_node();
        var version = spt.pipeline.get_node_kwarg(node, 'version');
        var properties = spt.pipeline.get_node_kwargs(node).properties;
        '''

        load_behavior['cbjs_action'] = cbjs_action_default + '''
        spt.pipeline.set_input_value_from_kwargs(node, bvr.arg_name, bvr.src_el);
        '''
        if input_type == "select":
            load_behavior['cbjs_action'] = cbjs_action_default + '''
            spt.pipeline.set_select_value_from_kwargs(node, bvr.arg_name, bvr.src_el, properties);
            '''
        elif input_type == "radio":
            load_behavior['cbjs_action'] = cbjs_action_default + '''
            spt.pipeline.set_radio_value_from_kwargs(node, bvr.arg_name, bvr.src_el, properties);
            '''
        elif input_type == "checkbox":
            load_behavior['cbjs_action'] = cbjs_action_default + '''
            spt.pipeline.set_checkbox_value_from_kwargs(node, bvr.arg_name, bvr.src_el, properties);
            '''

        input_wdg.add_behavior(load_behavior)


        # On change behavior, stores sessional value
        change_behavior = {
            'top_class': top_class,
            'arg_name': arg_name,
            'cbjs_action': '''
            var node = spt.pipeline.get_info_node();
            var version = spt.pipeline.get_node_kwarg(node, 'version');
            if (version && version != 1)
                return;

            var popup = bvr.src_el.getParent(".spt_popup");
            var activator = popup.activator;
            var toolTop = activator.getParent(".spt_pipeline_tool_top");
            spt.pipeline.set_top(toolTop.getElement(".spt_pipeline_top"));

            var top = bvr.src_el.getParent("."+bvr.top_class);
            var input = spt.api.get_input_values(top, null, false);

            spt.pipeline.set_node_kwarg(node, bvr.arg_name, input[bvr.arg_name]);

            node.has_changes = true;

            spt.named_events.fire_event('pipeline|change', {});
            '''
        }

        if input_type == "text":
            change_behavior['type'] = 'blur'
        elif input_type in ["select", "radio", "color"]:
            change_behavior['type'] = 'change'
        elif input_type == "checkbox":
            change_behavior['type'] = 'change'
            change_behavior['cbjs_action'] = '''
            var node = spt.pipeline.get_info_node();
            var version = spt.pipeline.get_node_kwarg(node, 'version');

            var popup = bvr.src_el.getParent(".spt_popup");
            var activator = popup.activator;
            var toolTop = activator.getParent(".spt_pipeline_tool_top");
            spt.pipeline.set_top(toolTop.getElement(".spt_pipeline_top"));

            var top = bvr.src_el.getParent("."+bvr.top_class);
            var input = spt.api.get_input_values(top, null, false);

            var value = true;
            if (input[bvr.arg_name] != "on") value = false;

            if (version && version != 1) {
                var settings = spt.pipeline.get_node_property(node, 'settings');
                settings['properties'][bvr.arg_name] = value;
                spt.pipeline.set_node_kwargs(node, settings);
            } else {
                spt.pipeline.set_node_kwarg(node, bvr.arg_name, value);
            }

            node.has_changes = true;

            spt.named_events.fire_event('pipeline|change', {});
            '''

        input_wdg.add_behavior(change_behavior)



class PipelinePropertyCbk(Command):

    def execute(self):

        if self.kwargs.get('version') == 2:
            return

        process = self.kwargs.get("process")
        pipeline_code = self.kwargs.get("pipeline_code")
        pipeline = Search.get_by_code("sthpw/pipeline", pipeline_code)

        search = Search("config/process")
        search.add_filter("pipeline_code", pipeline_code)
        search.add_filter("process", process)
        process_sobj = search.get_sobject()

        process_code = process_sobj.get_code()

        workflow = process_sobj.get_json_value("workflow") or {}

        values = self.kwargs or {}

        for name, value in values.items():
            workflow[name] = value


        process_sobj.set_json_value("workflow", workflow)
        process_sobj.commit()





class PipelineSaveCbk(Command):
    '''Callback executed when the Save button or other Save menu items are pressed in Project Workflow'''
    def get_title(self):
        return "Save a pipeline"

    def execute(self):
        pipeline_sk = self.kwargs.get('search_key')

        pipeline_xml = self.kwargs.get('pipeline')
        pipeline_color = self.kwargs.get('color')
        pipeline_desc = self.kwargs.get('description')
        project_code = self.kwargs.get('project_code')
        timestamp = self.kwargs.get("timestamp")

        default_template = self.kwargs.get("default_template")
        pipeline_data = self.kwargs.get("pipeline_data") or {}

        from pyasm.common import Xml
        xml = Xml()
        xml.read_string(pipeline_xml)
        process_nodes = xml.get_nodes("pipeline/process")
        settings_list = []

        for node in process_nodes:
            settings_str = xml.get_attribute(node, "settings")

            settings = {}
            if settings_str:
                try:
                    settings = jsonloads(settings_str)
                    if type(settings) == unicode:
                        settings = jsonloads(settings)
                except:
                    process_name = xml.get_attribute(node, "name")
                    print("WARNING: Setting for process %s not saved." % process_name )

            settings_list.append(settings)

            xml.del_attribute(node, "settings")

        pipeline_xml = xml.to_string()
        server = TacticServerStub.get(protocol='local')
        data =  {'pipeline':pipeline_xml, 'color':pipeline_color}
        if pipeline_desc:
            data['description'] = pipeline_desc
        if project_code:
            # force a pipeline to become site-wide
            if project_code == '__SITE_WIDE__':
                project_code = ''
            data['project_code'] = project_code
        if timestamp:
            data['timestamp'] = timestamp

        if SearchType.column_exists("sthpw/pipeline", "data"):
            data['data'] = pipeline_data

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


        self.check_duplicates(process_nodes, xml)

        self.description = "Updated workflow [%s]" % pipeline_code

        node_kwargs = self.kwargs.get("node_kwargs") or {}


        for i in range(len(process_nodes)):
            node = process_nodes[i]

            process = None
            process_code = xml.get_attribute(node, "process_code")
            process_name = xml.get_attribute(node, "name")

            if process_code:
                process = Search.get_by_code("config/process", process_code)


            # try to find it by name
            if not process:
                search = Search("config/process")
                search.add_filter("process", process_name)
                search.add_filter("pipeline_code", pipeline_code)
                process = search.get_sobject()


            # else create a new one
            if not process:
                process = SearchType.create("config/process")
                process.set_value("process", process_name)
                process.set_value("pipeline_code", pipeline_code)

            # set the process code
            xml.set_attribute(node, "process_code", process.get_code())

            curr_settings = settings_list[i]

            subpipeline_code = None
            if curr_settings:
                subpipeline_code = curr_settings.pop("subpipeline_code", None)
            if subpipeline_code or subpipeline_code == "":
                process.set_value("subpipeline_code", subpipeline_code)

            node_type = xml.get_attribute(node, "type")

            if curr_settings:
                workflow = process.get_json_value("workflow", default={})

                # On change of node type, clear the workflow data
                orig_node_type = workflow.get("node_type")
                if orig_node_type and orig_node_type != node_type:
                    workflow = curr_settings
                else:
                    workflow.update(curr_settings)
                workflow['node_type'] = node_type
                process.set_value("workflow", workflow)

            process.commit()

            if node_type:
                kwargs = node_kwargs.get(process_name) or {}
                if len(kwargs) > 0:
                    kwargs['process'] = process_name
                    kwargs['node_type'] = node_type
                    kwargs['pipeline_code'] = pipeline_code

                    version_str = kwargs.get('version') or 1
                    version = int(version_str)

                    if version is 1:
                        cmd = ProcessInfoCmd(**kwargs)
                        cmd.execute()
                    elif version is 2:
                        cmd = NewProcessInfoCmd(**kwargs)
                        cmd.execute()



    def check_duplicates(self, nodes, xml):
        process_set = set()

        for node in nodes:
            process_name = xml.get_attribute(node, "name")
            if process_name in process_set:
                raise ValueError('The workflow cannot have duplicate process names.')
            else:
                process_set.add(process_name)




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




class PipelineDocumentWdg(BaseRefreshWdg):

    def get_document(self):
        content = [{
            "type": "group",
            "state": "on",
            "group_level": 0,
            "title": "Workflows",
        }]
        content += self.get_default_content()

        document = {
            'type': 'table',
            'content': content
        }

        return document


    def get_default_content(self):
        project_code = self.kwargs.get("project_code") or Project.get_project_code()

        return [{
            "type": "group",
            "state": "on",
            "group_level": 1,
            "title": "Uncategorized"
        },
        {
            "type": "sobject",
            "group_level": 2,
            "expression": "@SEARCH(sthpw/pipeline['begin']['category', 'is', 'NULL']['category', 'Uncategorized']['or']['@ORDER_BY','timestamp desc']['project_code', '%s'])" % (project_code)
        }]



    def get_styles(self):

        styles = HtmlElement.style('''

            .vertical-centered, .full-centered, .full-gapped {
                display: flex;
                align-items: center;
            }

            .full-centered {
                justify-content: center;
            }

            .full-gapped {
                justify-content: space-between;
            }

            .spt_pipeline_document {
                overflow: auto;
            }

            .spt_pipeline_document .group-label {
                padding-top: 1px;
            }

            /* general icons styles in PipelineToolWdg*/

            .spt_pipeline_document .floating-icon .fa-file,  .spt_pipeline_document .floating-icon .fa-copy{
                color: green;
            }

            .spt_pipeline_document .floating-icon .fa-trash {
                color: red;
            }

            .spt_pipeline_document .document-group-content {
                padding: 0px 3px;
                width: 100%;
            }

            .spt_pipeline_document .document-group-label {
                overflow: hidden;
                text-overflow: ellipsis;
            }

            .spt_pipeline_document .document-item-content {
                min-height: 28px;
                padding: 4px 10px 4px 10px;
                width: 100%;
            }

            .spt_pipeline_document .document-item-input {
                border: none;
            }

            .spt_pipeline_document .spt_document_count {
                margin-left: 5px;
                color: darkred;
                text-decoration: underline;
                font-weight: bold;
            }

            ''')

        return styles


    def get_display(self):

        top = self.top
        top.add_class("spt_pipeline_document")
        top.add_style("height: 100%")

        project_code = Project.get_project_code()
        top.add_attr("spt_project_code", project_code)

        search_type = "sthpw/pipeline"
        top.add_attr("spt_search_type", search_type)

        # find document
        document = None

        search = Search("config/widget_config")
        search.add_filter("view", "document")
        search.add_filter("search_type", search_type)
        search.add_filter("category", "%s library" % project_code)
        config = search.get_sobject()

        if config:
            document = config.get_json_value("config")
            content = document.get("content")
            content += self.get_default_content()
            document['content'] = content

        # if no document found, use default
        if not document:
            document = self.get_document()

        group_label_view = "workflow.manage.group_label"
        group_label_class = "tactic.ui.tools.PipelineDocumentGroupLabel"
        element_names = ["document_item"]

        document_wdg = DocumentWdg(
            search_type=search_type,
            #element_names=element_names,
            #group_label_view = group_label_view,
            group_label_class = group_label_class,
            show_header=False,
            show_shelf=False,
            show_select=False,
            show_context_menu=False,
            show_search_limit=False,
            #show_row_highlight=False,
            show_group_highlight=False,
            expand_on_load=False,
            collapse_default=True,
            collapse_level=1,
            show_border="horizontal",
            height="auto",
            width="100%",
            view="table",
            #drag_action_script="spme/workflow_document_drag_action",
            config_xml='''<config>
                <table>
                    <element name="document_item" edit="false">
                        <display class="tactic.ui.tools.PipelineDocumentItemWdg">

                        </display>
                    </element>
                </table>
            </config>''',
            extra_data={
                "min_height": 14,
                "single_line": "true",
            },
        )
        top.add(document_wdg)

        document_wdg.set_document(document)

        top.add(self.get_styles())
        self.add_item_behaviors(top)

        return top


    def add_item_behaviors(self, el):

        el.add_behavior({
            'type': 'listen',
            'event_name': 'reorderX|sthpw/pipeline',
            'cbjs_action': '''

            var server = TacticServerStub.get_master();

            var on_complete = function() {
                var projectCode = bvr.src_el.getAttribute("spt_project_code");
                var searchType = bvr.src_el.getAttribute("spt_search_type");
                var doc = spt.document.export();
                var document_cmd = "tactic.ui.panel.DocumentSaveCmd"
                var document_kwargs = {
                    view: "document",
                    document: doc,
                    search_type: searchType,
                    project_code: projectCode,
                }
                server.p_execute_cmd(document_cmd, document_kwargs);
            }

            var src_el = bvr.firing_element;

            if (src_el.hasClass("spt_table_group_row")) {
                on_complete();
                return;
            } else {
                var search_key = src_el.getAttribute("spt_search_key_v2");

                var categoryGroup = spt.table.get_parent_groups(src_el, 1);
                var category = categoryGroup.getAttribute("spt_group_name");

                var kwargs = {
                    category: category
                }

                server.update(search_key, kwargs, {}, on_complete);

            }


            '''
        })



        el.add_relay_behavior({
            'type': 'blur',
            'bvr_match_class': 'spt_document_input',
            'cbjs_action': '''

            var layout = bvr.src_el.getParent(".spt_layout");
            spt.table.set_layout(layout);

            var top = bvr.src_el.getParent(".spt_document_item");
            var row = bvr.src_el.getParent(".spt_table_row_item");
            var name = bvr.src_el.value;

            if (name == "") {
                spt.table.remove_rows([row]);
                spt.notify.show_message("Workflows require a name");
            } else {
                var parent_group = spt.table.get_parent_groups(bvr.src_el, 1);
                if (!parent_group || parent_group.length == 0) return;
                var category = parent_group.getAttribute("spt_group_name");

                var server = TacticServerStub.get();
                var cmd = "tactic.ui.tools.PipelineSaveCmd";
                var kwargs = {
                    name: name,
                    category: category,
                };

                server.p_execute_cmd(cmd, kwargs)
                .then(function(ret_val) {
                    var search_key = ret_val.info.search_key;

                    row.setAttribute("spt_search_key", search_key);
                    row.setAttribute("spt_search_key_v2", search_key);

                    spt.notify.show_message('Workflow created');

                    var documentTop = top.getParent(".spt_pipeline_document");
                    var projectCode = documentTop.getAttribute("spt_project_code");
                    var searchType = documentTop.getAttribute("spt_search_type");

                    var doc = spt.document.export();

                    var document_cmd = "tactic.ui.panel.DocumentSaveCmd"
                    var document_kwargs = {
                        view: "document",
                        document: doc,
                        search_type: searchType,
                        project_code: projectCode,
                    }

                    server.p_execute_cmd(document_cmd, document_kwargs)
                    .then(function(ret_val){
                        top.removeClass("spt_unsaved_item");
                        var on_complete = function() {
                            var refreshedRow = spt.table.get_row_by_search_key(search_key);
                            refreshedRow.setAttribute("spt_group_level", 2);
                            var documentItem = refreshedRow.getElement(".spt_document_item");
                            documentItem.click();
                        }
                        spt.table.refresh_rows([row], null, {}, {on_complete, on_complete});
                    });

                });
            }


            '''

            })



class PipelineDocumentItem(BaseRefreshWdg):


    def get_display(self):
        sobject = self.kwargs.get("sobject")

        label = ""
        pipeline_code = ""
        if sobject:
            label = sobject.get_value("name") or sobject.get_value("code")
            pipeline_code = sobject.get_value("code")

        top = self.top

        top.add_class("spt_document_item")
        top.add_class("vertical-centered")
        top.add_attr("spt_pipeline_code", pipeline_code)
        top.add_attr("spt_title", label)

        top.add_behavior({
            'type': 'listen',
            'event_name': 'pipeline_%s|click' % pipeline_code,
            'project_code': Project.get_project_code(),
            'cbjs_action': '''

            if (bvr.src_el.hasClass("spt_unsaved_item")) {
                var input = bvr.src_el.getElement(".spt_document_input");
                input.focus();
                return;
            }

            var layout = bvr.src_el.getParent(".spt_layout");
            spt.table.set_layout(layout);
            spt.table.unselect_all_rows();
            var row = bvr.src_el.getParent(".spt_table_row_item");
            spt.table.select_row(row);

            var pipeline_code = bvr.firing_data.pipeline_code;
            var title = bvr.firing_data.title;

            var top = null;
            // they could be different when inserting or just clicked on
            top = bvr.src_el.getParent(".spt_pipeline_tool_top");
            if (!top) {
                top = spt.get_element(document, '.spt_pipeline_tool_top');
            }

            // clear search
            if (top) {
                var info = top.getElement(".spt_node_search");
                if (info) info.value = "";
            }

            // dont load again if pipeline already loaded
            if (top.pipeline_code == pipeline_code) return;
            top.pipeline_code = pipeline_code;

            var editor_top = top.getElement(".spt_pipeline_editor_top");

            var ok = function () {
                spt.named_events.fire_event('pipeline|hide_info', {});

                editor_top.removeClass("spt_has_changes");

                var wrapper = top.getElement(".spt_pipeline_wrapper");
                spt.pipeline.init_cbk(wrapper);

                var start_el = top.getElement(".spt_pipeline_editor_start")
                spt.pipeline.hide_start(start_el);

                spt.pipeline.clear_canvas();

                spt.pipeline.import_pipeline(pipeline_code);


                // add to the current list
                var value =  bvr.firing_data.pipeline_code;
                var title = bvr.firing_data.title;


                var text = top.getElement(".spt_pipeline_editor_current2");

                var html = "<span class='hand spt_pipeline_link' spt_title='" + title + "' spt_pipeline_code='" + value + "'>" + title + "</span>";


                var breadcrumb = bvr.breadcrumb;
                if (breadcrumb) {
                    text.innerHTML = breadcrumb + " / " + html;
                }
                else {
                    text.innerHTML = html;
                }

                spt.pipeline.set_current_group(value);

                editor_top.removeClass("spt_has_changes");


                spt.command.clear();


            };

            var save = function(){
                editor_top.removeClass("spt_has_changes");
                var wrapper = editor_top.getElement(".spt_pipeline_wrapper");
                spt.pipeline.init_cbk(wrapper);

                var group_name = spt.pipeline.get_current_group();

                var data = spt.pipeline.get_data();
                var color = data.colors[group_name];

                var group = spt.pipeline.get_group(group_name);
                var default_template = data.default_templates[group_name];
                var node_index = group.get_data("node_index");
                var pipeline_data = {
                    default_template: default_template,
                    node_index: node_index
                };

                server = TacticServerStub.get();
                spt.app_busy.show("Saving project-specific pipeline ["+group_name+"]",null);

                var xml = spt.pipeline.export_group(group_name);
                var search_key = server.build_search_key("sthpw/pipeline", group_name);
                try {
                    var args = {
                        search_key: search_key,
                        pipeline: xml,
                        color: color,
                        project_code: bvr.project_code,
                        pipeline_data: pipeline_data
                    };
                    server.execute_cmd('tactic.ui.tools.PipelineSaveCbk', args);
                    spt.named_events.fire_event('pipeline|save', {});

                    editor_top.removeClass("spt_has_changes");
                    spt.command.clear();
                } catch(e) {
                    spt.alert(spt.exception.handler(e));
                }

                spt.app_busy.hide();
            }


            var current_group_name = spt.pipeline.get_current_group();
            var group_name = pipeline_code;
            if (editor_top && editor_top.hasClass("spt_has_changes")) {
                spt.confirm("Current workflow has changes.  Do you wish to continue without saving?", save, ok, {okText: "Save", cancelText: "Don't Save"});
            } else {
                ok();
            }


            '''

        })

        open_wdg = DivWdg()
        top.add(open_wdg)
        open_wdg.add_class("spt_document_item_open")
        open_wdg.add_class("document-item-open document-item-content vertical-centered hand")

        label_wdg = DivWdg()
        open_wdg.add(label_wdg)
        label_wdg.add_class("spt_document_label")
        label_wdg.add_class("document-group-label")
        label_wdg.add(label)

        input_wdg = HtmlElement.text()
        top.add(input_wdg)
        input_wdg.add_class("spt_document_input")
        input_wdg.add_class("document-item-input document-item-content vertical-centered")
        input_wdg.add_attr("placeholder", "Enter a name...")
        input_wdg.add_style("display: none")

        return top



class PipelineDocumentItemWdg(DocumentItemWdg):


    def handle_td(self, td):
        sobject = self.get_current_sobject()
        group_level = sobject.get_value("group_level", no_exception=True)
        if group_level:
            group_level = int(group_level)
        else:
            group_level = 0

        name = sobject.get_value("name", no_exception=True) or "N/A"

        margin = group_level*12

        td.add_style("overflow: hidden")
        td.add_style("text-overflow: ellipsis")
        td.add_style("padding: 0px 0px 0px %spx" % margin)
        td.add_attr("data-toggle", "tooltip")
        td.add_attr("title", name)



    def get_display(self):
        sobject = self.get_current_sobject()
        search_key = sobject.get_search_key()

        from tactic.ui.panel import CustomLayoutWdg
        if sobject.is_insert():
            layout = PipelineDocumentItem()
        else:
            layout = PipelineDocumentItem(sobject=sobject, search_key=search_key)

        return layout



class PipelineDocumentGroupLabel(BaseRefreshWdg):


    def get_display(self):
        label = self.kwargs.get("group_value")

        uncategorized = False
        if label == "Uncategorized":
            uncategorized = True

        group_level = self.kwargs.get("group_level")

        add_btn_title = "Add New Category" if group_level == 0 else "Add New Workflow"
        add_btn_icon = "fa-plus" if group_level == 0 else "fa-file"
        delete_display = "none" if group_level == 0 or uncategorized else ""

        top = self.top
        top.add_behavior({
            'type': 'load',
            'uncategorized': uncategorized,
            'cbjs_action': '''

            if (bvr.uncategorized) {
                var row = bvr.src_el.getParent(".spt_table_row_item");
                row.setAttribute("spt_dynamic", true);

                var tuple = spt.table.get_child_rows(row);
                var children = spt.table.get_child_rows_tuple(tuple, true);
                 children.forEach(function(child) {
                    child.setAttribute("spt_dynamic", true);
                });
            }

            '''
        })

        top.add_class("spt_pipeline_group_label")
        top.add_class("group-label full-gapped")
        top.add_attr("spt_group_level", group_level)
        top.add_attr("spt_value", label)

        label_wdg = self.get_label_wdg(uncategorized, label)
        top.add(label_wdg)

        input_wdg = self.get_input_wdg()
        top.add(input_wdg)

        delete_btn = self.get_delete_wdg(delete_display)
        top.add(delete_btn)

        add_btn = self.get_add_wdg(add_btn_title, add_btn_icon)
        top.add(add_btn)

        return top


    def get_label_wdg(self, uncategorized, label):

        label_wdg = DivWdg()
        label_wdg.add_class("spt_document_label")
        label_wdg.add_class("document-group-content")
        label_wdg.add("<span class='spt_group_label'>%s</span>" % label)
        label_wdg.add("<span class='spt_document_count'></span>")

        label_wdg.add_behavior({
            'type': 'click_up',
            'uncategorized': uncategorized,
            'cbjs_action': '''

            var group_el = bvr.src_el.getParent(".spt_group_row");
            var group_level = group_el.getAttribute("spt_group_level");

            if (group_level == 0 || bvr.uncategorized) return;

            var top = bvr.src_el.getParent(".spt_pipeline_group_label");
            spt.document.item.toggle_edit(top);

            '''

            })

        label_wdg.add_behavior({
            'type': 'load',
            'cbjs_action': '''

            var row = bvr.src_el.getParent(".spt_group_row");
            if (row.getAttribute("spt_group_level") != 1) return;

            var count_div = bvr.src_el.getElement(".spt_document_count");
            var count = 0;

            while (row.nextElementSibling && row.nextElementSibling.getAttribute("spt_group_level") != 1) {
                var row = row.nextElementSibling;
                if (row.hasClass("spt_table_row"))
                    count++;
            }

            count_div.innerText = count;

            '''
            })

        return label_wdg


    def get_input_wdg(self):

        input_wdg = HtmlElement.text("name")
        input_wdg.add_class("spt_document_input")
        input_wdg.add_class("document-group-content vertical-centered")
        input_wdg.add_attr("placeholder", "Enter a name...")
        input_wdg.add_style("display: none")

        input_wdg.add_behavior({
            'type': 'blur',
            'cbjs_action': '''

            var top = bvr.src_el.getParent(".spt_pipeline_group_label");
            var input = top.getElement(".spt_document_input");

            if (top.hasClass("spt_unsaved_group")) {
                var label = top.getElement(".spt_group_label");
                label.innerText = "";

                if (input.value == "") input.value = spt.document.item.generate_name();
            }

            var changed = spt.document.item.close_edit(top);
            // save document
            if (changed) {
                if (top.hasClass("spt_unsaved_group")) {
                    top.removeClass("spt_unsaved_group");
                    spt.document.item.new_group_count++;
                }

                var documentTop = top.getParent(".spt_pipeline_document");
                var projectCode = documentTop.getAttribute("spt_project_code");
                var searchType = documentTop.getAttribute("spt_search_type");
                var doc = spt.document.export();
                var view = "document";

                var server = TacticServerStub.get();
                var kwargs = {
                    view: view,
                    document: doc,
                    search_type: searchType,
                    project_code: projectCode,
                }
                var cmd = "tactic.ui.panel.DocumentSaveCmd";

                server.p_execute_cmd(cmd, kwargs);
            }

            '''

            })


        input_wdg.add_behavior({
            'type': 'keyup',
            'cbjs_action': '''

            var key = evt.key;
            var top = bvr.src_el.getParent(".spt_pipeline_group_label");

            spt.document.item.keyup_behavior(top, key);

            '''

            })

        return input_wdg



    def get_add_wdg(self, add_btn_title, add_btn_icon):
        add_btn = self.get_button_wdg("spt_add_btn", add_btn_title, add_btn_icon)
        add_btn.add_style("margin: 0 3px")


        add_mode = "form"

        if add_mode == "form":
            cbjs_insert = '''

            var info = spt.edit.edit_form_cbk(evt, bvr);
            spt.notify.show_message("Insert item complete.");

            var popup = bvr.src_el.getParent(".spt_popup");
            var src_el = popup.activator;

            // Add row to table
            var layout = src_el.getParent(".spt_layout");
            spt.table.set_layout(layout);

            var group_el = src_el.getParent(".spt_group_row");
            var row = spt.table.add_new_item({row: group_el});
            row.setAttribute("spt_group_level", 2);
            if (group_el.getAttribute("spt_group_name") == "Uncategorized")
                row.setAttribute("spt_dynamic", "true");

            var rowTop = row.getElement(".spt_document_item");
            rowTop.addClass("spt_unsaved_item");

            var td = row.getElement("td");

            td.setStyle("overflow", "hidden");
            td.setStyle("text-overflow", "ellipsis");
            td.setStyle("padding", "0");
            td.setAttribute("data-toggle", "tooltip");

            // Save document
            var server = TacticServerStub.get();
            var search_key = info.sobject.__search_key__;

            row.setAttribute("spt_search_key", search_key);
            row.setAttribute("spt_search_key_v2", search_key);

            spt.notify.show_message('Workflow created');

            var documentTop = rowTop.getParent(".spt_pipeline_document");
            var projectCode = documentTop.getAttribute("spt_project_code");
            var searchType = documentTop.getAttribute("spt_search_type");

            var doc = spt.document.export();

            var document_cmd = "tactic.ui.panel.DocumentSaveCmd"
            var document_kwargs = {
                view: "document",
                document: doc,
                search_type: searchType,
                project_code: projectCode,
            }
            server.p_execute_cmd(document_cmd, document_kwargs)
            .then(function(ret_val){
                rowTop.removeClass("spt_unsaved_item");
                var on_complete = function() {
                    var refreshedRow = spt.table.get_row_by_search_key(search_key);
                    refreshedRow.setAttribute("spt_group_level", 2);
                    var documentItem = refreshedRow.getElement(".spt_document_item");
                    documentItem.click();
                    var cellEdit = refreshedRow.getElement(".spt_cell_edit");
                    cellEdit.setStyle("padding", "0px 0px 0px 24px");
                }
                spt.table.refresh_rows([row], null, {}, {on_complete, on_complete});
            });



            '''

            add_btn.add_behavior({
                'type': 'click',
                'cbjs_insert': cbjs_insert,
                'cbjs_action': '''

                var layout = bvr.src_el.getParent(".spt_layout");
                spt.table.set_layout(layout);

                var group_el = bvr.src_el.getParent(".spt_group_row");
                var group_level = group_el.getAttribute("spt_group_level");

                if (group_level == 0) {
                    var new_row = spt.table.add_new_group({row: group_el, group_level: 1});

                    let focused = document.querySelector(":focus");
                    if (focused) focused.blur();
                    var group_name = spt.document.item.generate_name();

                    var server = TacticServerStub.get();
                    var group_key = server.build_search_key("sthpw/virtual", group_name);
                    new_row.setAttribute("spt_search_key_v2", group_key);

                    groupTop = new_row.getElement(".spt_pipeline_group_label");
                    groupTop.addClass("spt_unsaved_group");
                    groupLabel = groupTop.getElement(".spt_group_label").innerText = group_name;

                    addBtn = groupTop.getElement(".spt_add_btn");
                    addBtn.title = "Add New Workflow";

                    addIcon = addBtn.getElement("i");
                    addIcon.removeClass("fa-plus");
                    addIcon.addClass("fa-file");

                    deleteBtn = groupTop.getElement(".spt_delete_btn");
                    deleteBtn.setStyle("display", "");

                    spt.document.item.toggle_edit(groupTop);
                } else {
                    var row = bvr.src_el.getParent(".spt_group_row");
                    var category = row.getAttribute("spt_group_name");

                    cbjs_insert = bvr.cbjs_insert;

                    var class_name = 'tactic.ui.panel.EditWdg';
                    var kwargs = {
                        search_type: 'sthpw/pipeline',
                        view: 'insert',
                        show_header: false,
                        single: true,
                        cbjs_insert: cbjs_insert,
                        extra_data: {
                            category: category
                        }
                    }
                    var popup = spt.panel.load_popup("Add New Workflow", class_name, kwargs);
                    popup.activator = bvr.src_el;
                }

                '''
                })
        else:
            add_btn.add_behavior({
                'type': 'click',
                'cbjs_action': '''

                var layout = bvr.src_el.getParent(".spt_layout");
                spt.table.set_layout(layout);

                var group_el = bvr.src_el.getParent(".spt_group_row");
                var group_level = group_el.getAttribute("spt_group_level");

                if (group_level == 0) {
                    var new_row = spt.table.add_new_group({row: group_el, group_level: 1});

                    let focused = document.querySelector(":focus");
                    if (focused) focused.blur();
                    var group_name = spt.document.item.generate_name();

                    var server = TacticServerStub.get();
                    var group_key = server.build_search_key("sthpw/virtual", group_name);
                    new_row.setAttribute("spt_search_key_v2", group_key);

                    groupTop = new_row.getElement(".spt_pipeline_group_label");
                    groupTop.addClass("spt_unsaved_group");
                    groupLabel = groupTop.getElement(".spt_group_label").innerText = group_name;

                    addBtn = groupTop.getElement(".spt_add_btn");
                    addBtn.title = "Add New Workflow";

                    addIcon = addBtn.getElement("i");
                    addIcon.removeClass("fa-plus");
                    addIcon.addClass("fa-file");

                    deleteBtn = groupTop.getElement(".spt_delete_btn");
                    deleteBtn.setStyle("display", "");

                    spt.document.item.toggle_edit(groupTop);
                } else {
                    var group_el = bvr.src_el.getParent(".spt_group_row");
                    var row = spt.table.add_new_item({row: group_el});
                    row.setAttribute("spt_group_level", 2);

                    rowTop = row.getElement(".spt_document_item");
                    rowTop.addClass("spt_unsaved_item");

                    var td = row.getElement("td");

                    td.setStyle("overflow", "hidden")
                    td.setStyle("text-overflow", "ellipsis")
                    td.setStyle("padding", "0")
                    td.setAttribute("data-toggle", "tooltip")

                    var open = row.getElement(".spt_document_item_open");
                    var input = row.getElement(".spt_document_input");

                    open.setStyle("display", "none");
                    input.setStyle("display", "");
                    input.focus();
                    input.setSelectionRange(0, input.value.length);
                }

                '''

            })

        return add_btn



    def get_delete_wdg(self, delete_display):
        delete_btn = self.get_button_wdg("spt_delete_btn", "Delete Category and Workflows", "fa-trash")
        delete_btn.add_style("display", delete_display)

        delete_btn.add_behavior({
            'type': 'mouseenter',
            'cbjs_action': '''

            var layout = bvr.src_el.getParent(".spt_layout");
            spt.table.set_layout(layout);

            var row = bvr.src_el.getParent(".spt_table_row_item");
            var tuple = spt.table.get_child_rows(row);
            var children = spt.table.get_child_rows_tuple(tuple, true);

            children.forEach(function(child) {
                var item = child.getElement(".spt_cell_edit");
                item.setStyle("background", "red");
                item.setStyle("color", "white");
            });

            '''

            })


        delete_btn.add_behavior({
            'type': 'mouseleave',
            'cbjs_action': '''

            var layout = bvr.src_el.getParent(".spt_layout");
            spt.table.set_layout(layout);

            var row = bvr.src_el.getParent(".spt_table_row_item");
            var tuple = spt.table.get_child_rows(row);
            var children = spt.table.get_child_rows_tuple(tuple, true);

            children.forEach(function(child) {
                var item = child.getElement(".spt_cell_edit");
                item.setStyle("background", "");
                item.setStyle("color", "");
            });

            '''

            })


        delete_btn.add_behavior({
            'type': 'click',
            'cbjs_action': '''

            var layout = bvr.src_el.getParent(".spt_layout");
            spt.table.set_layout(layout);

            var documentTop = bvr.src_el.getParent(".spt_pipeline_document");
            var projectCode = documentTop.getAttribute("spt_project_code");
            var searchType = documentTop.getAttribute("spt_search_type");
            var view = "document";

            var kwargs = {
                view: view,
                search_type: searchType,
                project_code: projectCode,
            }

            var row = bvr.src_el.getParent(".spt_table_row_item");
            var tuple = spt.table.get_child_rows(row);
            var children = spt.table.get_child_rows_tuple(tuple, true);

            if (children.length == 0) {
                spt.table.remove_rows([row], {no_animation: true});

                var server = TacticServerStub.get();
                var doc = spt.document.export();
                kwargs.document = doc;
                var cmd = "tactic.ui.panel.DocumentSaveCmd";

                server.p_execute_cmd(cmd, kwargs);
            } else {
                var on_post_delete = function() {
                    for (var i = 0; i < children.length; i++) {
                        var child = children[i];
                        child.addClass("spt_removed");
                        if (layout.getAttribute("spt_version") == "2") {
                            spt.table.remove_hidden_row(child);
                        }
                        spt.behavior.destroy_element(child);
                    }
                    spt.behavior.destroy_element(row);

                    var server = TacticServerStub.get();
                    var doc = spt.document.export();
                    kwargs.document = doc;
                    var cmd = "tactic.ui.panel.DocumentSaveCmd";

                    server.p_execute_cmd(cmd, kwargs)
                    .then(function(ret_val) {
                        // TODO: this is just a workaround. By default, the view seems
                        // to get refreshed with the old doc. Hence, the deleted
                        // group (category) didn't get removed from the UI.
                        spt.panel.refresh(documentTop);
                    });
                }

                spt.table.delete_rows(children, {on_post_delete: on_post_delete});
            }

            '''

            })

        return delete_btn



    def get_button_wdg(btn_class, title, fa_class):

        button_wdg = DivWdg()
        button_wdg.add_class(btn_class)
        button_wdg.add_class("floating-icon hand")
        button_wdg.add_attr("title", title)

        fa_icon = HtmlElement.i()
        button_wdg.add(fa_icon)
        fa_icon.add_class("fa")
        fa_icon.add_class(fa_class)
        fa_icon.add_class("document-icon full-centered")

        button_wdg.add_behavior({
            'type': 'mouseenter',
            'cbjs_action': '''

            var icon = bvr.src_el.getElement("i");
            var color = icon.getStyle("color")

            if (color == "white") return;

            icon.setStyle("background", color);
            icon.setStyle("color", "white");

            '''

        })


        button_wdg.add_behavior({
            'type': 'mouseleave',
            'cbjs_action': '''

            var icon = bvr.src_el.getElement("i");
            var color = icon.getStyle("background");

            if (color == "white") return;

            icon.setStyle("color", color);
            icon.setStyle("background", "white");

            '''

        })

        return button_wdg

    get_button_wdg = staticmethod(get_button_wdg)



class PipelineSaveCmd(Command):

    def execute(self):
        category = self.kwargs.get("category")
        name = self.kwargs.get("name")

        pipeline = SearchType.create("sthpw/pipeline")
        pipeline.set_value("name", name)
        pipeline.set_value("category", category)
        pipeline.commit()

        self.info['search_key'] = pipeline.get_search_key()





__all__.append("PipelineProcessTypeWdg")
class PipelineProcessTypeWdg(BaseRefreshWdg):


    def get_display(self):

        top = self.top

        top.add_class("spt_process_select_top")

        # get all of the custom process node types
        search = Search("config/widget_config")
        search.add_filter("category", "workflow")
        search.add_order_by("view")
        custom_nodes = search.get_sobjects()


        # base nodes
        base_nodes = ["manual", "action", "condition", "approval", "hierarchy", "dependency"]
        base_nodes.reverse()
        for base in base_nodes:
            node = SearchType.create("config/widget_config")
            node.set_value("view", base)
            node.set_value("config", '''<config>
            <%s>
    <element name="node">
      <display class="tactic.ui.tools.BaseNodeWdg"/>
    </element>
    <element name="info">
    </element>
    <element name="process">
    </element>
            </%s>
            </config>
            ''' % (base, base))
            node.xml = node.get_xml_value("config")

            custom_nodes.insert(0, node)




        custom_div = DivWdg()
        top.add(custom_div)
        #custom_div.add_style("display: flex")
        #custom_div.add_style("flex-wrap: wrap")
        #custom_div.add_style("flex-direction: column")
        custom_div.add_style("height: 100%")

        version_2_enabled = ProjectSetting.get_value_by_key("version_2_enabled") != "false"

        custom_div.add_relay_behavior( {
            'type': 'click',
            'bvr_match_class': 'spt_custom_node',
            'version_2_enabled': version_2_enabled,
            'cbjs_action': '''
            var node_type = bvr.src_el.getAttribute("spt_node_type")
            var node = spt.pipeline.add_node(null, 10, 10, {node_type: node_type} );
            // BACKWARDS COMPATIBILITY
            if (bvr.version_2_enabled)
                spt.pipeline.set_node_kwarg(node, "version", 2);

            //spt.pipeline.fit_to_node(node);

            spt.pipeline.unselect_all_nodes();
            spt.pipeline.unselect_all_connectors();
            spt.pipeline.select_node(node);
            '''
        } )

        custom_div.add_behavior( {
            'type': 'load',
            'version_2_enabled': version_2_enabled,
            'cbjs_action': '''

spt.process_tool = {};

spt.process_tool.item_clone = null;
spt.process_tool.item_pos = null;
spt.process_tool.mouse_pos = null;
spt.process_tool.item_top = null;

spt.process_tool.item_drag_setup = function(evt, bvr, mouse_411) {
    var el = bvr.src_el.getElement(".spt_custom_node");
    var clone = spt.behavior.clone(el);
    clone.setStyle("position", "absolute");
    clone.setStyle("background", "#FFF");
    clone.setStyle("z-index", "1000");
    clone.setStyle("pointer-events", "none");
    clone.inject(bvr.src_el);

    var top = bvr.src_el.getParent(".spt_process_select_top")
    spt.process_tool.item_top = top;

    spt.process_tool.mouse_pos = {x: mouse_411.curr_x, y: mouse_411.curr_y};
    spt.process_tool.item_pos = clone.getPosition(top);

    spt.process_tool.item_clone = clone;
}

spt.process_tool.item_drag_motion = function(evt, bvr, mouse_411) {
    var orig_pos = spt.process_tool.mouse_pos;
    var item_pos = spt.process_tool.item_pos;
    var top = spt.process_tool.item_top;

    var dx = mouse_411.curr_x - orig_pos.x;
    var dy = mouse_411.curr_y - orig_pos.y;

    var width = spt.process_tool.item_clone.getWidth();
    var height = spt.process_tool.item_clone.getHeight();

    var scroll_el = top.getParent(".spt_popup_content");
    if (scroll_el) {
        var scroll = {x: 0, y: scroll_el.scrollTop};
        var new_pos = {x: item_pos.x+dx-scroll.x+0.5*width, y: item_pos.y+dy-2*scroll.y+0.5*height};
    }
    else {
        scroll_el = top;
        var scroll = {x: 0, y: scroll_el.scrollTop};
        var new_pos = {x: Math.abs(item_pos.x)+dx-scroll.x+0.5*width, y: item_pos.y+dy-scroll.y+0.5*height};
    }

    spt.process_tool.item_clone.position( new_pos, {relativeTo: top} );
    //spt.process_tool.item_clone.setStyle("top", item_pos.x+dx);
    //spt.process_tool.item_clone.setStyle("left", item_pos.y+dy);
}

spt.process_tool.item_drag_action = function(evt, bvr, mouse_411) {

    var clone_pos = spt.process_tool.item_clone.getPosition();
    spt.behavior.destroy( spt.process_tool.item_clone );
    spt.process_tool.item_top = null;

    var orig_pos = spt.process_tool.mouse_pos;
    var dx = mouse_411.curr_x - orig_pos.x;
    var dy = mouse_411.curr_y - orig_pos.y;
    if (Math.abs(dx) < 5 || Math.abs(dy) < 5) {
        return;
    }


    var drop_on_el = spt.get_event_target(evt);
    if (! drop_on_el.hasClass(".spt_pipeline_top") ) {
        var parent = drop_on_el.getParent(".spt_pipeline_top");
        if (!parent) {
            return;
        }
    }


    var node_type = bvr.src_el.getAttribute("spt_node_type");

    var pos = spt.pipeline.get_mouse_position(mouse_411);
    var new_node = spt.pipeline.add_node(null, pos.x, pos.y, {node_type: node_type});
    // BACKWARDS COMPATIBILITY
    if (bvr.version_2_enabled)
        spt.pipeline.set_node_kwarg(new_node, "version", 2);
    new_node.has_changes = true;
    var new_pos = spt.pipeline.get_position(new_node);

    var selected = spt.pipeline.get_selected_nodes();
    for (var i = 0; i < selected.length; i++) {
        var pos = selected[i].getPosition();
        var pos = spt.pipeline.get_position(selected[i]);

        var group_name = spt.pipeline.get_current_group();
        var group = spt.pipeline.get_group(group_name);
        if (pos.x < new_pos.x) {
            var connector = spt.pipeline.connect_nodes(selected[i], new_node);
            group.add_connector(connector);
        }
        else {
            var connector = spt.pipeline.connect_nodes(new_node, selected[i]);
            group.add_connector(connector);
        }
    }

    spt.pipeline.unselect_all_nodes();
    spt.pipeline.select_node(new_node);


}


spt.process_tool.toggle_side_bar = function(activator) {

    var toolTop = activator.getParent(".spt_pipeline_tool_top");
    var left = toolTop.getElement(".spt_pipeline_tool_left");

    var toolbar = left.getElement(".spt_pipeline_toolbar");
    var search = toolbar.getElement(".spt_pipeline_type_search");
    var document = toolbar.getElement(".spt_toolbar_icons");

    var el1 = left.getElement(".spt_pipeline_list_top");
    var el2 = left.getElement(".spt_pipeline_nodes");

    if (el1.getStyle("display") == "none") {
        el1.setStyle("display", "");
        el2.setStyle("display", "none");
        search.removeClass("selected");
        document.addClass("selected");
    }
    else {
        el1.setStyle("display", "none");
        el2.setStyle("display", "");
        document.removeClass("selected");
        search.addClass("selected");
        search.focus();
    }

}


spt.process_tool.show_side_bar = function(activator) {

    var toolTop = bvr.src_el.getParent(".spt_pipeline_tool_top");
    var left = toolTop.getElement(".spt_pipeline_tool_left");
    var right = toolTop.getElement(".spt_pipeline_tool_right");

/*

    left.setStyle("margin-left", "0px");
    left.setStyle("opacity", "1");
    right.setStyle("margin-left", "250px");
    left.gone = false;
    setTimeout(function(){
        left.setStyle("z-index", "");
    }, 250);

    bvr.src_el.setStyle("display", "none")


    left.setStyle("margin-left", "-250px");
    left.setStyle("opacity", "0");
    right.setStyle("margin-left", "0px");
    left.gone = true;
    setTimeout(function(){
        left.setStyle("z-index", "-1");
    }, 250);

    var show_icon = toolTop.getElement(".spt_show_sidebar");
    show_icon.setStyle("display", "");

*/

}


            '''
        } )

        for i, custom_node in enumerate(custom_nodes):

            view = custom_node.get_value("view")
            element_names = custom_node.get_element_names()
            display_options = {
                    'node_type': view
            }
            description = custom_node.get("description") or ""

            node_container = DivWdg()
            node_scale = DivWdg()
            node_container.add(node_scale)

            node_container.add_style("width: 80px")
            node_container.add_style("height: 60px")
            node_container.add_style("overflow: hidden")
            node_container.add_style("position: relative")
            node_container.add_style("border: 1px solid #eee")



            node_scale.add_style("transform-origin: top left")
            node_scale.add_class("spt_node_scale")

            style = HtmlElement.style()
            style.add('''
            .spt_node_scale {
                position: absolute;
                top: 50%;
                left: 50%;
            }
            ''')
            node_scale.add(style)

            # node_scale.add_style("margin-top: 12px")
            # node_scale.add_style("margin-left: 20px")

            node_wdg = None
            if (view in ['approval', 'condition', 'hierarchy', 'dependency', 'progress', 'action', 'manual']):
                pipeline_canvas_wdg = PipelineCanvasWdg(add_node_behaviors=False, height=self.kwargs.get("height"))

                if (view == 'approval'):
                    node_wdg = pipeline_canvas_wdg.get_approval_node("approval")
                elif (view == 'condition'):
                    node_wdg = pipeline_canvas_wdg.get_condition_node("condition")
                    # node_wdg.add_style("margin: 12px auto auto 12px !important")
                elif (view == 'action'):
                    node_wdg = pipeline_canvas_wdg.get_node("action", node_type="action")
                elif (view == 'hierarchy'):
                    node_wdg = pipeline_canvas_wdg.get_node("hierarchy", node_type="hierarchy")
                elif (view == 'dependency'):
                    node_wdg = pipeline_canvas_wdg.get_node("dependency", node_type="dependency")
                elif (view == 'progress'):
                    node_wdg = pipeline_canvas_wdg.get_node("progress", node_type="progress")
                else:
                    node_wdg = pipeline_canvas_wdg.get_node("manual", node_type="manual")

                description = pipeline_canvas_wdg.get_node_description(view)

                node_wdg.add_class("spt_custom_node")
            else:
                node_wdg = custom_node.get_display_widget("node", display_options)

            if (view == 'asset_check') or (view == 'expression') or (view == 'simple_condition'):
                node_scale.add_style("transform: scale(0.5, 0.5) translate(-50%, -50%)")
            else:
                node_wdg.add_style("transform: translate(-50%, -50%)")
                node_scale.add_style("transform: scale(0.5, 0.5)")

            node_scale.add(node_wdg)
            node_wdg.add_style("z-index: 0")



            item_div = DivWdg()
            custom_div.add(item_div)
            item_div.add_class("spt_custom_node")
            item_div.add_class("spt_custom_node_container")
            item_div.add_color("background", "background")

            item_div.add_style("border-radius: 3px")
            item_div.add_style("text-align: center")
            item_div.add_style("box-shadow: 0px 0px 5px rgba(0,0,0,0.1)")

            item_div.add_attr("spt_node_type", view)


            content_div = DivWdg()
            item_div.add(content_div)
            content_div.add_style("display: flex")
            content_div.add_style("align-items: middle")

            content_div.add(node_container)

            data_div = DivWdg()
            content_div.add(data_div)
            data_div.add_style("width: 80%")
            data_div.add_style("overflow-y: auto")

            title_div = DivWdg()
            #item_div.add(title_div)
            data_div.add(title_div)
            title_div.add(Common.get_display_title(view).upper())
            title_div.add_style("padding: 3px 10px")
            title_div.add_style("background: #EEE")
            title_div.add_style("text-align: center")
            title_div.add_style("border-bottom: solid 1px #DDD")
            title_div.add_style("font-weight: 500")


            data_div.add_style("font-size: 0.8em")

            data_div.add("<div style='padding: 3px'>%s</div>" % description)
            #data_div.add_style("padding: 3px")

            item_div.add_class("hand")
            item_div.add_class("tactic_hover")

            item_div.add_style("border: solid 1px #DDD")
            item_div.add_style("margin: 3px 5px")

            item_div.add_behavior( {
            "type": 'drag',
            "mouse_btn": 'LMB',
            "cb_set_prefix": 'spt.process_tool.item_drag'
            } )


        return top



class SessionalProcess:

    def add_relay_session_behavior(section, section_name='default', pre_processing='', post_processing=''):

        # session api
        section.add_behavior({
            'type': 'load',
            'section_name': section_name,
            'cbjs_action': '''

            var top = bvr.src_el.hasClass("spt_section_top") ? bvr.src_el : bvr.src_el.getParent(".spt_section_top");
            if (!top) return;

            let node = spt.pipeline.get_info_node();
            
            top.update_data = function(replace) {
                var kwargs = spt.pipeline.get_node_kwargs(node);
                var version = kwargs.version;

                if (version != 2)
                    return;

                node.has_changes = true;
                var inputs = spt.api.get_input_values(top, null, false);
                var section_name = top.getAttribute("section_name") || bvr.section_name;
                // for refreshed panels (shouldn't need this but just in this case)

                if (replace) {
                    var values = kwargs[section_name] || {};

                    Object.keys(inputs).forEach(function(key) {
                        values[key] = inputs[key];
                    })

                    spt.pipeline.set_node_kwarg(node, section_name, values);
                } else {
                    spt.pipeline.set_node_kwarg(node, section_name, inputs);
                }

                spt.named_events.fire_event('pipeline|change', {});
            }
        '''})

        # data loading and processing
        section.add_behavior({
            'type': 'load',
            'section_name': section_name,
            'cbjs_action': '''

            var node = spt.pipeline.get_info_node();
            var version = spt.pipeline.get_node_kwarg(node, 'version');
            if (version != 2)
                return;

            var top = bvr.src_el.hasClass("spt_section_top") ? bvr.src_el : bvr.src_el.getParent(".spt_section_top");
            if (!top) return;

            // for refreshed panels (shouldn't need this but just in this case)
            var section_name = top.getAttribute("section_name") || bvr.section_name;
            var data = spt.pipeline.get_node_kwarg(node, section_name) || {};

            top.pre_processing = function() {
                %s
            }

            top.load_section = function() {
                var data = spt.pipeline.get_node_kwarg(node, section_name) || {};
                spt.api.Utility.set_input_values2(top, data);
            }

            top.post_processing = function() {
                %s
            }

            top.pre_processing();
            top.load_section();
            top.post_processing();

            ''' % (pre_processing, post_processing)
            })




        # on change(blur, change) - replace section data
        section.add_relay_behavior({
            'type': 'blur',
            'bvr_match_class': 'spt_input',
            'cbjs_action': '''

                var top = bvr.src_el.getParent(".spt_section_top");
                if (top) {
                    var section = top.getAttribute("section_name");
                    if (section != "task_detail") {
                        top.update_data();
                    } else {
                        spt.task_detail.set_top(top);
                        var content = top.getElement(".spt_app_content_top");
                        var index = content.getAttribute("index");
                        spt.task_detail.update_data(content, index);
                    }
                    
                }

        '''})

        section.add_relay_behavior({
            'type': 'change',
            'bvr_match_class': 'ace_text-input',
            'cbjs_action': '''

            var top = bvr.src_el.getParent(".spt_section_top");
            if (top) {
                var section = top.getAttribute("section_name");
                if (section != "task_detail") {
                    top.update_data();
                } else {
                    spt.task_detail.set_top(top);
                    var content = top.getElement(".spt_app_content_top");
                    var index = content.getAttribute("index");
                    spt.task_detail.update_data(content, index);
                }
                
            }

        '''})

        section.add_relay_behavior({
            'type': 'change',
            'bvr_match_class': 'spt_input',
            'cbjs_action': '''

            var top = bvr.src_el.getParent(".spt_section_top");
            if (top) {
                var section = top.getAttribute("section_name");
                if (section != "task_detail") {
                    top.update_data();
                } else {
                    spt.task_detail.set_top(top);
                    var content = top.getElement(".spt_app_content_top");
                    var index = content.getAttribute("index");
                    spt.task_detail.update_data(content, index);
                }
            }
        '''})

    add_relay_session_behavior = staticmethod(add_relay_session_behavior)






