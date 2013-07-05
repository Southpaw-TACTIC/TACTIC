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

__all__ = ['FlashPipelineEditorWdg', 'ProcessPropertiesWdg', 'GetPipelineXml', 'CommitPipelineXmlCmd', 'PipelineCreatorElementWdg', 'PipelineTaskTriggerCommitCbk', 'TriggerListWdg']

import urllib
import re

from pyasm.common import Xml, Common, jsonloads, jsondumps, TacticException
from pyasm.command import Command
from pyasm.biz import Pipeline, Schema
from pyasm.search import Search, SearchType
from pyasm.web import WebContainer, Widget, DivWdg, HtmlElement, Table, SpanWdg
from pyasm.widget import TableWdg, BaseTableElementWdg, IconButtonWdg, IconWdg, ProgressWdg, HeaderWdg, PopupWdg, SwfEmbedWdg, TextWdg, HiddenWdg, SelectWdg


from tactic.ui.common import BaseRefreshWdg
class FlashPipelineEditorWdg(BaseRefreshWdg):

    def get_args_keys(my):
        return {
        "search_type": "search_type of the pipeline",
        "search_id":  "search_id of the pipeline"
        }


    def get_display(my):
        web = WebContainer.get_web()

        search_type = my.kwargs.get("search_type")
        if not search_type:
            search_type = web.get_form_value("search_type")

        search_id = my.kwargs.get("search_id")
        if not search_type:
            search_id = web.get_form_value("search_id")


        sobject = Search.get_by_id(search_type, search_id)

        if sobject.get_base_search_type() == "sthpw/pipeline":
            pipeline_code = sobject.get_code()
        elif sobject.get_base_search_type() == "sthpw/schema":
            pipeline_code = sobject.get_code()
        else:
            pipeline_code = sobject.get_value('pipeline_code')



        div = DivWdg()
        my.set_as_panel(div)
        div.add_class("spt_pipeline_top")
        div.add_style("min-width: 800px")
        div.add_style("min-height: 400px")

        #header = HeaderWdg()
        #div.add(header)

        table = Table() 
        #table.set_dynamic()
        table.set_max_width()

        # show top row detailing pipeline
        #sobject_table = TableWdg(search_type, "pipeline")
        #sobject_table.set_show_property(False)
        # use new style table
        from tactic.ui.panel import TableLayoutWdg
        sobject_table = TableLayoutWdg(search_type=search_type, view="pipeline", mode='simple')
        sobject = Search.get_by_code(search_type, pipeline_code)
        sobject_table.set_sobjects([sobject])

        table.add_row()
        td = table.add_cell()
        td.add( sobject_table )

        # show menu buttons
        table.add_row()
        td = table.add_cell()

        help_div = DivWdg()
        help_div.add( SpanWdg("[pipeline editor quick help]", css='med') )
        help_div.add_behavior( {
            'type': 'click_up',
            'mouse_btn': 'LMB',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_pipeline_top");
            bvr.dst_el = top.getElement(".spt_pipeline_quick_help_notes");
            spt.fx_anim.toggle_slide_el({}, bvr)
            ''',
            'dst_el': 'pipeline_editor_quick_help_notes',
            'slide_direction': 'vertical'
        } )
        help_div.add_style( "cursor: default" )
        help_div.add_style( "padding-top: 8px" )
        help_div.add_style( "padding-bottom: 8px" )

        help_slide_div = DivWdg()
        help_slide_div.set_attr( "id", "pipeline_editor_quick_help_notes" )
        help_slide_div.add_class( "spt_pipeline_quick_help_notes" )

        help_txt = '''
<p>When mouse is on the canvas:</p>
<UL>
    <LI> CTRL-LMB-Drag: this will pan the pipeline around 
    <LI> + (plus): Zoom in 
    <LI> - (minus): Zoom out 
    <LI> DELETE: deletes the selected nodes 
    <LI> LMB: Select none 
    <LI> LMB-Drag: Select under a selection box 
</UL>
<p>When mouse is over a node:</p>
<UL>
    <LI> LMB: select 
    <LI> CTRL-LMB or LMB top left corner: rename node 
    <LI> LMB-Drag: move the position of the selected node
</UL>
<p>NOTES:</p>
<OL>
<LI> If some actions are not working (e.g. panning) it is recommended that you uninstall then reinstall your Flash plugin
<LI> On Mac OS X use the Apple "Command key" instead of the "CTRL" key for operations listed above
</OL>
<BR/>
<BR/>
'''
        help_slide_div.add(help_txt)
        help_slide_div.add_style( "display: none" )
        help_slide_div.add_style( "padding-left: 10px" )

        td.add_style("vertical-align: top")
        td.add( my.get_menu_wdg() )
        td.add( help_div )
        td.add( help_slide_div )

        table.add_row()

        content_td = table.add_cell()
        content_td.add_style("width: 100%")
        content_td.add_style("height: 100%")
        content_td.add_style("border-style: solid")
        content_td.add_style("border-width: 1px")

        progress = ProgressWdg()
        content_td.add(progress)

        swf = SwfEmbedWdg()
        swf.set_code(pipeline_code)

        swf_div = DivWdg()
        swf_div.add_class("spt_pipeline_top")
        swf_div.add_attr("spt_pipeline_code", pipeline_code)
        swf_div.add(swf)
        #swf_div.add_style("z-index: -1")
        content_td.add(swf_div)

        from pyasm.alpha.sobject_navigator_wdg import PipelinePropertyWdg, PipelineContextWdg


        from tactic.ui.container import PopupWdg
        popup = PopupWdg(id='pipeline_editor_info', allow_page_activity=True, z_start=500)
        popup_content = DivWdg()
        popup_content.set_id("spt_pipeline_properties")
        popup_content.add("<div class='maq_search_bar'><span class='spt_pipeline_node' id='node'></span></div>" )
        property_wdg = PipelinePropertyWdg()
        popup_content.add(property_wdg)

        context_wdg = PipelineContextWdg()
        popup_content.add(context_wdg)
        popup.add("Node Properties" ,"title")
        popup.add(popup_content,"content")

        # add some properties from the database
        wrapper = DivWdg()
        wrapper.add_class("spt_pipeline_process_properties")
        popup.add(wrapper)
        more_properties_wdg = ProcessPropertiesWdg(pipeline_code=pipeline_code)
        wrapper.add(more_properties_wdg)

        div.add(popup)


        div.add("<h2 style='text-align: left;'>Pipeline Editor</h2>")
        div.add(table)




        return div


    def get_menu_wdg(my):
        div = DivWdg()
        div.add_style("padding: 5px")

        create_button = IconButtonWdg( "Create", IconWdg.CREATE, True)
        create_button.add_event("onclick", "pipeline_creator.create_node('process')")
        div.add( create_button )

        commit_button = IconButtonWdg( "Save", IconWdg.SAVE, True)
        commit_button.add_event("onclick", "pipeline_creator.do_commit()")
        div.add( commit_button )

        clear_button = IconButtonWdg( "Clear", IconWdg.CREATE, True)
        clear_button.add_event("onclick", "if (confirm('Are you sure you wish to clear the canvas')) pipeline_creator.clear_nodes()")
        div.add( clear_button )

        info_button = IconButtonWdg( "Properties", IconWdg.INFO, True)
        info_button.add_event("onclick", "$('pipeline_editor_info').setStyle('display','')");

        div.add(info_button)


        """
        div.add("||||")

        trigger_button = IconButtonWdg( "Triggers", IconWdg.INFO, True)
        div.add(trigger_button)
        trigger_button.add_behavior( {
            "type" : "click_up",
            "cbjs_action": '''
            var pipeline_code = 'project';
            var process = 'asset';
            var process = spt.pipeline.get_current_process();
            var title = "Pipeline Triggers";

            var kwargs = {
            process: process
            };
            spt.api.load_popup(title, 'pyasm.admin.creator.TriggerListWdg', kwargs);

            '''
        })



        info_button = IconButtonWdg( "Bids", IconWdg.INFO, True)
        info_button.add_behavior( {
            "type" : "click_up",
            "cbjs_action": '''
            var pipeline_code = 'project';
            var process = 'asset';
            var process = spt.pipeline.get_current_process();
            var category = pipeline_code + "/" + process;
            var title = "Pipeline Bid";

            var kwargs = {
            search_type: 'config/bid',
            view: 'table',
            expression: "@SOBJECT(config/bid['category','"+category+"'])"
            };
            spt.api.load_popup(title, 'tactic.ui.panel.TableLayoutWdg', kwargs);

            '''
        })
        div.add(info_button)


        info_button = IconButtonWdg( "Naming", IconWdg.INFO, True)
        div.add(info_button)
        info_button = IconButtonWdg( "Tasks", IconWdg.INFO, True)
        div.add(info_button)
        info_button = IconButtonWdg( "Notes", IconWdg.INFO, True)
        div.add(info_button)
        info_button = IconButtonWdg( "Checkins", IconWdg.INFO, True)
        div.add(info_button)
        """


        return div





class ProcessPropertiesWdg(BaseRefreshWdg):
    ARGS_KEYS = {
    'process': "The process in the pipeline that is to be displayed"
    }

    def get_display(my):
        top = DivWdg()
        my.set_as_panel(top)

        process_wdg = my.get_process_wdg()
        top.add( process_wdg )


        my.process_name = my.kwargs.get("process")
        triggers_wdg = TriggerListWdg(process=my.process_name)
        top.add(triggers_wdg)


        return top


    def get_process_wdg(my):
        div = DivWdg()

        pipeline_code = my.kwargs.get("pipeline_code")
        assert(pipeline_code)

        my.process_name = my.kwargs.get("process")
        if not my.process_name:
            div.add("No process selected")
            return div


        search = Search("config/process")
        search.add_filter("pipeline_code", pipeline_code)
        search.add_filter("process", my.process_name)
        process = search.get_sobject()
        if not process:
            div.add("Process sobject for [%s] not found" % my.process_name)
            return div

        title_div = DivWdg()
        title_div.add("Custom Properties")
        title_div.add_class("maq_search_bar")
        div.add(title_div)


        from pyasm.widget import WidgetConfigView
        config = WidgetConfigView.get_by_search_type("config/process","edit")

        data = process.get_data()
        from pyasm.web import Table
        properties_div = DivWdg()
        properties_div.add_style("padding: 5px")
        table = Table()
        properties_div.add(table)
        for item, value in data.items():
            if item in ['timestamp','id','code','sort_order','s_status','pipeline_code','process']:
                continue

            edit_wdg = config.get_display_widget("item")
            if value == None:
                value = ''
            edit_wdg.set_value(value)

            table.add_row()
            table.add_cell("%s: " % item)
            table.add_cell(edit_wdg)

        
        div.add(properties_div)


        #from tactic.ui.panel import TableLayoutWdg
        #table = TableLayoutWdg(search_type='config/process', view='table', mode='simple')
        #table.set_sobjects([process])
        #div.add(table)


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
            print "No data supplied"
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






class GetPipelineXml(Widget):
    def get_display(my):

        web = WebContainer.get_web()

        code = web.get_form_value("pipeline_code")

        search_type = web.get_form_value("search_type")
        if not search_type:
            search_type = "sthpw/pipeline"

        if search_type == 'sthpw/pipeline':

            column = "pipeline"
            if not code:
                return "<pipeline/>"

        else:
            column = "schema"
            if not code:
                return "<schema/>"

        pipeline = Search.get_by_code(search_type, code)
        xml_string = pipeline.get_value(column)
        #print xml_string
        return xml_string

        
"""
#TO BE REMOVED
class CommitPipelineXml(Widget):
    def get_display(my):
        from pyasm.web import WebContainer
        web = WebContainer.get_web()
        web.set_content_type('text/plain')

        return "&err=ErrorME&function=1234"
        #return
        cmd = CommitPipelineXmlCmd()
        Command.execute_cmd(cmd)

        #print "Error ME"
"""
class CommitPipelineXmlCmd(Command):

    def get_title(my):
        return "Update Pipeline"

    def execute(my):
        web = WebContainer.get_web()

        xml_string = my.kwargs.get('xml')
        xml = Xml(string=xml_string)

        pipeline_code = my.kwargs.get("pipeline_code")
        pipeline = Pipeline.get_by_code(pipeline_code)
        if pipeline:
            pipeline.set_value("pipeline", xml.to_string())
            pipeline.set_pipeline(xml.to_string())
        else:
            # HACK: to handle schema
            pipeline = Schema.get_by_code(pipeline_code)
            pipeline.set_value("schema", xml.to_string())

        pattern = '[\+%\-\s\?#\$|/]'
        err_msg = 'Empty space or special characters found in'
        if isinstance(pipeline, Pipeline):
            search_type = pipeline.get_value('search_type')
            # task pipeline process can have spaces
            if search_type == 'sthpw/task':
                pattern = '[\+%\-\?#\$|/]'
            process_names = pipeline.get_process_names()
            contexts = pipeline.get_all_contexts()
            for context in contexts:
                print context
                if re.search(pattern, context):
                    raise TacticException('%s context [%s]'%(err_msg, context))

            for name  in process_names:
                if re.search(pattern, name):
                    raise TacticException('%s process [%s]'%(err_msg, name))
        pipeline.commit()

        # make sure there is a process sobject
        search = Search("config/process")
        search.add_filter("pipeline_code", pipeline_code)
        process_sobjs = search.get_sobjects()

        count = 0
        for process_name in process_names:

            exists = False
            for process_sobj in process_sobjs:
                # if it already exist, then skip
                if process_sobj.get_value("process") == process_name:
                    exists = True
                    break
            if not exists:
                process_sobj = SearchType.create("config/process")
                process_sobj.set_value("pipeline_code", pipeline_code)
                process_sobj.set_value("process", process_name)

            process_sobj.set_value("sort_order", count)
            process_sobj.commit()
            count += 1



        my.description = "Updated pipeline [%s]" % pipeline_code





 


class PipelineCreatorElementWdg(BaseTableElementWdg):

    def get_display(my):

        sobject = my.get_current_sobject()
        search_type = sobject.get_search_type()
        search_id = sobject.get_id()
        pipeline_code = sobject.get_code()

        widget = Widget()

        button = IconButtonWdg("Open Project Workflow", IconWdg.JUMP)


        button.add_behavior( {
            'type': 'click_up',
            'kwargs': {
                'search_type': search_type,
                'search_id': search_id,
            },
            'cbjs_action': '''
                var class_name = "tactic.ui.tools.PipelineToolWdg";
                spt.tab.add_new("old_pipeline_editor", "Project Workflow",  class_name, bvr.kwargs);
            '''
        } )
        button.add_behavior( {
            'type': 'click_up',
            'modkeys': 'SHIFT',
            'kwargs': {
                'search_type': search_type,
                'search_id': search_id,
            },
            'cbjs_action': '''
                var class_name = "tactic.ui.tools.PipelineToolWdg";
                spt.panel.load_popup("Project-Workflow", class_name, bvr.kwargs);
            '''
        } )
        widget.add(button)

        #web = WebContainer.get_web()
        #url = web.get_widget_url()
        #url.set_option("widget", "pyasm.admin.creator.FlashPipelineEditorWdg")
        #url.set_option("search_type", search_type)
        #url.set_option("search_id", search_id)
        #link = HtmlElement.href(button, url.to_string())
        #link.set_attr("target", "_blank")
        #widget.add(link)


        return widget





