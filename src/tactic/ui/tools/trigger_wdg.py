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

__all__ = ['TriggerToolWdg', 'TriggerDetailWdg',
'StatusTriggerEditWdg', 'NotificationTriggerEditWdg',
'PythonScriptTriggerEditWdg', 'PythonClassTriggerEditWdg',
'StatusTriggerEditCbk', 'NotificationTriggerEditCbk',
'PythonScriptTriggerEditCbk', 'PythonClassTriggerEditCbk',
'TriggerParentStatusEditWdg', 'TriggerParentStatusEditCbk',

'TriggerCreateWdg', 'TriggerCreateCbk',
'TriggerCompleteWdg', 'TriggerCompleteCbk',
'TriggerDateWdg', 'TriggerDateCbk',

'EventTriggerEditWdg'
]

from tactic.ui.common import BaseRefreshWdg

from pyasm.common import jsondumps, jsonloads, Common, Environment, TacticException
from pyasm.biz import Notification, CustomScript, Pipeline, Project
from pyasm.web import DivWdg, WebContainer, Table, HtmlElement, SpanWdg
from pyasm.command import Command
from pyasm.search import Search, SearchType, SearchKey
from tactic.ui.panel import TableLayoutWdg

from pyasm.widget import ProdIconButtonWdg, IconWdg, IconButtonWdg, TextWdg, CheckboxWdg, HiddenWdg, SelectWdg, TextAreaWdg, RadioWdg
from tactic.ui.container import ResizableTableWdg, TabWdg
from tactic.ui.container import GearMenuWdg, Menu, MenuItem
from tactic.ui.widget import ActionButtonWdg, IconButtonWdg
from tactic.ui.input import TextInputWdg, LookAheadTextInputWdg

import os

class TriggerToolWdg(BaseRefreshWdg):
    
    FOLDER_PREFIX  = '_triggers'

    def get_display(self):

        search_key = self.kwargs.get("search_key")
        if not search_key:
            web = WebContainer.get_web()
            search_key = web.get_form_value("search_key")
        if search_key:
            current_trigger = SearchKey.get_by_search_key(search_key)
        else:
            current_trigger = None


        # pipeline mode is default
        self.mode = self.kwargs.get("mode")
        if not self.mode:
            self.mode = 'pipeline'

        #self.mode = "pipeline"

        top = DivWdg()
        top.add_class("spt_trigger_top")
        self.set_as_panel(top)

        inner = DivWdg()
        top.add(inner)

        if self.mode == 'pipeline':
            self.pipeline_code = self.kwargs.get("pipeline_code")
            self.process = self.kwargs.get("process")
            # Is this necessary?
            if self.process:
                top.add_attr("spt_process", self.process)

            top.add_attr("spt_pipeline_code", self.pipeline_code)
            self.title = self.process
            self.search_type = self.kwargs.get("search_type")

            search = Search("config/process")
            search.add_filter("pipeline_code", self.pipeline_code)
            search.add_filter("process", self.process)
            self.process_sobj = search.get_sobject()


        else:
            self.pipeline_code = ''
            self.process =''
            self.search_type = self.kwargs.get("search_type")
            top.add_attr("spt_search_type", self.search_type)
            self.title = self.search_type


        table = ResizableTableWdg()
        #table.add_style("width: 100%")
        table.add_color("background", "background")
        table.add_color("color", "color")
        inner.add(table)


        table.add_row()
        left = table.add_cell()
        left.add_style("width: 200px")
        left.add_style("min-width: 250px")
        left.add_style("vertical-align: top")
        left.add_style("border: solid 1px %s" % left.get_color("border") )
        left.add_color("color", "color3")
        left.add_color("background", "background")

        title_div = DivWdg()
        left.add(title_div)
        title_div.add_style("display: flex")
        title_div.add_style("align-items: center")
        title_div.add_style("justify-content: flex-end")

        title_div.add_style("height: 30px")
        title_div.add_style("padding: 5px 8px")
        title_div.add_color("background", "background")
        title_div.add_style("min-width: 150px")


        from tactic.ui.app import HelpButtonWdg
        help_button = HelpButtonWdg(alias="project-automation-triggers|project-automation-notifications", use_icon=True)

        add_button = IconButtonWdg(icon="FA_PLUS", size='small', name='Add a new trigger')
        add_button.add_behavior( {
        'type': 'click_up',
        'kwargs': {
            'mode': self.mode,
            'search_type': self.search_type,
            'pipeline_code': self.pipeline_code,
            'process': self.process
        },
        'cbjs_action': '''
        var top = bvr.src_el.getParent(".spt_trigger_top");
        var content = top.getElement(".spt_trigger_content");

        var class_name = 'tactic.ui.tools.TriggerDetailWdg';
        spt.panel.load(content, class_name, bvr.kwargs);
        '''
        } )

        title_div.add(add_button)
        title_div.add(help_button)

        left.add("<br clear='all'/>")


        triggers_div = DivWdg()
        left.add(triggers_div)
        triggers_div.add_style("margin: 0px 5px")
        triggers_div.add_style("min-height: 400px")
        left.add_color("background", "background", -3)
        
        self.process_code = ''
        # find the triggers
        search = Search("config/trigger")
        if self.mode == 'pipeline':
            if self.process_sobj:
                search.add_op('begin')
            search.add_filter("process", self.process)
            if self.process_sobj:
                self.process_code = self.process_sobj.get_code()
                search.add_filter("process", self.process_code)
                search.add_op("or")
        else:
            search.add_op('begin')
            search.add_filter("event", "%%|%s" % self.search_type, op='like')
            search.add_filter("search_type", self.search_type)
            search.add_op("or")


        triggers = search.get_sobjects()
        triggers_div.add("<b>Triggers</b><hr/>")
        if triggers:

            cur_trigger = triggers[0]

            for i, trigger in enumerate(triggers):
                trigger_div = self.get_trigger_wdg(trigger, i+1)
                triggers_div.add(trigger_div)
                trigger_div.add("<br clear='all'/>")
        else:
            triggers_div.add("<i style='opacity: 0.5'>No Triggers Defined</i><br/>")
            triggers_div.add("<br clear='all'/>")


        triggers_div.add("<br/>")

        triggers_div.add("<b>Notifications</b><hr/>")
        search = Search("sthpw/notification")
        if self.mode == 'pipeline':
            if self.process_sobj:
                search.add_op('begin')
            search.add_filter("process", self.process)
            if self.process_sobj:
                search.add_filter("process", self.process_sobj.get_code())
                search.add_op("or")
        else:
            search.add_op('begin')
            search.add_filter("event", "%%|%s" % self.search_type, op='like')
            search.add_filter("search_type", self.search_type)
            search.add_op("or")

        search.add_project_filter()
        triggers = search.get_sobjects()

        for i, trigger in enumerate(triggers):
            trigger_div = self.get_trigger_wdg(trigger, i+1)
            triggers_div.add(trigger_div)
            trigger_div.add("<br clear='all'/>")

        if not triggers:
            triggers_div.add("<i style='opacity: 0.5'>No Notifications Defined</i><br/>")
            triggers_div.add("<br clear='all'/>")

        """
        triggers_div.add("<b>Site Triggers</b><hr/>")
        search = Search("sthpw/trigger")
        triggers = search.get_sobjects()
        for trigger in triggers:
            trigger_div = self.get_trigger_wdg(trigger)
            triggers_div.add(trigger_div)
            trigger_div.add("<br clear='all'/>")
        if not triggers:
            triggers_div.add("<i>None Defined</i><br/>")
            triggers_div.add("<br clear='all'/>")
        """


        right = table.add_cell()
        right.add_class("spt_trigger_content")
        right.add_style("vertical-align: top")
        right.add_style("padding: 10px 20px 20px 20px")
        right.add_style("min-width: 500px")
        #right.add_style("border: solid 1px %s" % right.get_color("border") )

        right_div = DivWdg()
        right.add(right_div)
        right_div.add_style("width: 500px")
        right_div.add("&nbsp;")

        if current_trigger:
            kwargs = {
                'mode': self.mode,
                'trigger': current_trigger,
                'pipeline_code': self.pipeline_code,
                'process': self.process,
                'search_type': self.search_type,
            }

            right.add( TriggerDetailWdg(**kwargs) )
        else:

            div = DivWdg()
            right.add(div)

            div.add_style("height: 100px")
            div.add_style("width: 300px")
            div.add_color("background", "background3")
            div.add_color("color", "color3")
            div.add_border()
            div.center()
            div.add_style("margin-top: 50px")
            div.add_style("padding-top: 75px")

            div.add_style("text-align: center")
            div.add("<b>No Triggers Selected</b>")


        if self.kwargs.get("is_refresh") in [True, 'true']:
            return inner
        else:
            return top



    def get_trigger_wdg(self, trigger, index=1):
        trigger_div = DivWdg()
        trigger_div.add_style("padding: 3px 3px 3px 12px")
        trigger_div.add_class("hand")

        hover = trigger_div.get_color("background", -20)

        trigger_div.add_behavior( {
        'type': 'hover',
        'hover': hover,
        'cbjs_action_over': '''
            bvr.src_el.setStyle("background", bvr.hover);
        ''',
        'cbjs_action_out': '''
            bvr.src_el.setStyle("background", "");
        '''
        } )


        trigger_code = trigger.get_code()
        description = trigger.get_value("description")
        if not description:
            description = '-- no description --'

        title = trigger.get_value("title", no_exception=True)
        if not title:
            title = "<i style='opacity: 0.7'>%s</i>" % trigger.get_code()


        trigger_div.add_attr("title", description)

        #checkbox = CheckboxWdg(trigger_code)
        #trigger_div.add(checkbox)
        trigger_div.add("%s. %s" % (index, title))

        if trigger.get_value("process") == self.process:
            trigger_div.add(" <i style='opacity: 0.5'>(global)</i>")
        else:
            trigger_div.add(" <i style='opacity: 0.5'>(local)</i>")

        search_key = SearchKey.get_by_sobject(trigger)

        trigger_div.add_behavior( {
        'type': 'click_up',
        'kwargs': {
            'mode': self.mode,
            'search_type': self.search_type,
            'search_key': search_key,
            'pipeline_code': self.pipeline_code,
            'process': self.process
        },
        'cbjs_action': '''
        var top = bvr.src_el.getParent(".spt_trigger_top");
        var content = top.getElement(".spt_trigger_content");

        var class_name = 'tactic.ui.tools.TriggerDetailWdg';
        spt.panel.load(content, class_name, bvr.kwargs);
        '''
        } )
        return trigger_div



class TriggerDetailWdg(BaseRefreshWdg):

    def get_display(self):
        self.search_key = self.kwargs.get("search_key")
        if self.search_key:
            trigger = Search.get_by_search_key(self.search_key)
        else:
            trigger = self.kwargs.get("trigger")


        # Determine the mode for this widget. 
        self.mode = self.kwargs.get("mode")
        assert self.mode


        # get some info about where this trigger should be defined
        if self.mode == 'pipeline':
            self.pipeline_code = self.kwargs.get("pipeline_code")
            self.process = self.kwargs.get("process")

            self.pipeline = Pipeline.get_by_code(self.pipeline_code)

            if self.process:
                self.process_obj = self.pipeline.get_process(self.process)
            else:
                self.process_obj = None

            if self.process_obj:
                process_type = self.process_obj.get_type()
            else:
                process_type = None


            search = Search("config/process")
            search.add_filter("pipeline_code", self.pipeline_code)
            search.add_filter("process", self.process)
            self.process_sobj = search.get_sobject()


            #self.search_type = ""
            self.search_type = self.kwargs.get("search_type")
            if not self.search_type:
                self.search_type = self.pipeline.get_value("search_type")

        else:
            self.pipeline = None
            # search_type is process from schema editor ...
            self.search_type = self.kwargs.get("search_type")
            self.pipeline_code = ""
            self.process = None
            self.pipeline = None
            self.process_obj = None
            self.process_sobj = None


        top = DivWdg()
        top.add_class("spt_trigger_detail_top")

        top.add( self.get_add_trigger_wdg(trigger) )

        return top


    def get_add_trigger_wdg(self, trigger):

        div = DivWdg()

        
        #button = ActionButtonWdg(title='Save')
        #button.add_style("float: right")
        #button.add_style("margin-top: -8px")
        #div.add(button)
        button_bvr = {
        'type': 'click_up',
        'cbjs_action': '''

        spt.app_busy.show("Saving Trigger");
        var top = bvr.src_el.getParent(".spt_trigger_top");
        var detail_top = bvr.src_el.getParent(".spt_trigger_detail_top");
        var content = detail_top.getElement(".spt_trigger_add_top");
        
        var values = spt.api.Utility.get_input_values(detail_top, null, false);
        var pipeline_code = top.getAttribute("spt_pipeline_code");
        var process = top.getAttribute("spt_process");
        var search_type = top.getAttribute("spt_search_type");


        values.pipeline_code = pipeline_code;
        values.process = process;

        var event = values.event;
        
        // skip sending thru search_type for checkin type event
        if (!event.test(/^checkin/)) {
            values.search_type = search_type;
        }
  
        var cbk = content.getAttribute("spt_trigger_add_cbk");
        if (cbk == null || cbk == '') {
            alert("Please select an event and an action");
            spt.app_busy.hide();
            return;
        }

        var server = TacticServerStub.get();
        try{
            var data = server.execute_cmd(cbk, values);
            var search_key = data.info.search_key;
            spt.panel.refresh(top, {search_key: search_key} );
        }
        catch(e){
            spt.error(spt.exception.handler(e));
        }
        spt.app_busy.hide();
        '''
        } 
        #button.add_behavior( button_bvr )


        if not trigger:
            if self.process:
                div.add("<b>Add a new trigger for process [%s]</b><hr/>" % self.process)
            else:
                div.add("<b>Add a new trigger</b><hr/>" )
            event = ''
            code = ''
            description = ''
            search_key = ''
            event = ''
            title = ''

            scope = "local"

        else:
            event = trigger.get_value("event")
            code = trigger.get_code()
            description = trigger.get_value("description")
            search_key = SearchKey.get_by_sobject(trigger)
            title = trigger.get_value("title", no_exception=True)


            if self.process:
                div.add("<b>Edit existing trigger for process [%s]</b><hr/>" % self.process)
            else:
                div.add("<b>Edit existing trigger</b><hr/>")

            if trigger.get_value("process") == self.process:
                scope = "global"
            else:
                scope = "local"

            """
            title = trigger.get_value("title")
            desc = trigger.get_value("description")
            if not desc:
                div.add("Trigger: &nbsp; &nbsp; %s<br/>" % title )
            else:
                div.add("Trigger: &nbsp; &nbsp; %s - %s<br/>" % (title, desc))
            """



        # determine trigger type
        if not trigger:
            trigger_type = ''
        elif isinstance(trigger, Notification):
            trigger_type = 'notification'
        else:
            class_name = trigger.get_value("class_name")

            script_path = trigger.get_value("script_path")

            data = trigger.get_json_value("data")
            if data and isinstance(data,dict):
                class_path = data.get("class_path")
                if class_path:
                    class_name = class_path
            else:
                class_name = None
                class_path = None

            # TODO: should use trigger_type in database
            if class_name == 'tactic.command.PipelineTaskStatusTrigger' and not script_path:
                trigger_type = 'task_status'
            elif class_name == 'tactic.command.PipelineParentStatusTrigger' and not script_path:
                trigger_type = 'parent_status'
            elif class_name == 'tactic.command.PipelineTaskStatusTrigger' and script_path:
                trigger_type = 'custom_script'
            elif class_name == 'tactic.command.PipelineTaskCreateTrigger':
                trigger_type = 'task_create'
            elif class_name == 'tactic.command.PipelineTaskDateTrigger':
                trigger_type = 'task_date'

            elif class_name:
                trigger_type = 'python_class'
            elif script_path:
                trigger_type = 'custom_script'
            else:
                trigger_type = 'task_status'



        hidden = HiddenWdg("search_key")
        div.add(hidden)
        hidden.set_value( search_key )
        div.add("<br/>")

        content_div = DivWdg()
        div.add(content_div)
        content_div.add_style("height: 380px")
        content_div.add_style("overflow-y: auto")
        content_div.add_style("padding: 0px 10px")
        content_div.add_style("margin: 0px -20px")

        table = Table()
        content_div.add(table)
        table.add_style("width: 100%")
        table.add_color("color", "color")



        tr = table.add_row()
        td = table.add_cell()
        td.add_style("padding-bottom: 5px")
        # This is labeled as name, but is really title in the database.
        # The column in the database should have been called "name"
        td.add("Name:<br/>")
        title_text = TextInputWdg(name="title")
        title_text.add_style("margin-bottom: 10px")
        title_text.set_value(title)
        title_text.add_style("width: 100%")
        td.add(title_text)
 


        tr = table.add_row()
        td = table.add_cell()
        td.add_style("padding-bottom: 15px")
        td.add("Description:<br/>")
        desc_text = TextAreaWdg("description")
        desc_text.add_style("margin-bottom: 10px")
        desc_text.add_class("form-control")
        desc_text.add_style("width: 100%")
        desc_text.add_style("height: 60px")
        desc_text.set_value(description)
        td.add(desc_text)


        # TODO: not sure if this is necessary ... maybe should always be local
        # unless you create it from scratch in the TableLayout
        if self.mode == "pipeline":
            tr, td = table.add_row_cell()
            td.add("Scope:<br/>")
            radio = RadioWdg("scope")
            radio.set_option("value", "local")
            td.add(radio)
            if scope == "local":
                radio.set_checked()
            td.add(" Local to pipeline<br/>")
            radio = RadioWdg("scope")
            radio.set_option("value", "global")
            if scope == "global":
                radio.set_checked()
            td.add(radio)
            td.add(' All "%s" processes<br/>' % self.process)
            td.add("<br/>")


       
        table.add_row()
        tr, td = table.add_row_cell()
        td.add("<b>Event: </b>")
        td.add_style("padding-top", "20px")
        td.add("<hr/>")


        # Higher level triggers
        if self.mode == 'pipeline':
            event_labels = [
                'A new note is added',
                'A task status is changed',
                'A task is assigned',
                'A note is added or modified'
            ]
            
            #event_labels.append('Files are checked out')

            event_values = [
                'insert|sthpw/note',
                'change|sthpw/task|status',
                'change|sthpw/task|assigned',
                'change|sthpw/note'
            ]
            if self.search_type:
                event_labels.append('Files are checked in')
                event_values.append("checkin|%s"%self.search_type)
        else:
            event_labels = [
                'An item is added',
                'An item is updated',
                'A new note is added',
                'A task status is changed',
                'A task is assigned',
            ]
            event_labels.append('Files are checked in')
            #event_labels.append('Files are checked out')


            event_values = [
                'insert|%s' % self.search_type,
                'update|%s' % self.search_type,
                'insert|sthpw/note',
                'change|sthpw/task|status',
                'change|sthpw/task|assigned',
            ]
            event_values.append('checkin|%s' % self.search_type)
            #event_values.append('checkout|%s' % self.search_type)




        event_labels.append("Custom event")
        event_values.append("__custom__")

        #table.add_row()
        #td = table.add_cell()

        tr, td = table.add_row_cell()
        td.add_color("color", "color")
        td.add_style("padding: 10px")
        td.add("When:&nbsp;&nbsp;&nbsp;")

        #td = table.add_cell()

        select = SelectWdg("event")
        td.add(select)
        select.add_class("spt_trigger_event")
        select.set_option("values", event_values)
        select.set_option("labels", event_labels)
        select.add_empty_option("-- Choose event --")

        if event and event not in event_values:
            select.set_value("__custom__")
            custom_event = event
            event = '__custom__'
        else:
            select.set_value(event)
            custom_event = ''

        select.add_behavior( {
        'type': 'change',
        'kwargs': {
            'mode': self.mode,
            'pipeline_code': self.pipeline_code,
            'process': self.process,
            'search_type': self.search_type,
        },
        'cbjs_action': '''
        var top = bvr.src_el.getParent(".spt_trigger_detail_top");
        var content = top.getElement(".spt_trigger_event_top");

        var event = bvr.src_el.value;
        if (!event) {
            spt.info('Please choose an event.');
            return;
        }
        bvr.kwargs.event = event;
        var trigger_wdg = 'tactic.ui.tools.EventTriggerEditWdg';

        spt.panel.load(content, trigger_wdg, bvr.kwargs)
        '''
        } )



        #tr, td = table.add_row_cell()
        #td.add("Search Type (from pipeline): %s" % self.search_type)

        event_div = DivWdg()
        event_div.add_style("width: 100%")
        event_div.add_class("spt_trigger_event_top")
        event_div.set_parent(td)
        #event_div.add_color("color", "color")
        #event_div.add_color("background", "background", -5)
        #event_div.add_border()
        #event_div.add_style("padding: 5px")
        #event_div.add_style("margin: 10px")

        kwargs = self.kwargs.copy()
        kwargs['trigger'] = trigger
        kwargs['event'] = event
        kwargs['custom_event'] = custom_event

        event_wdg = EventTriggerEditWdg(**kwargs)
        event_wdg.set_parent(event_div)




        # Handle the action
        if self.mode == 'pipeline':
            trigger_labels = [
                'Send a notification',
                'Update parent status',
                'Update another task status',
                'Create another task',
                'Set actual task date',
            ]
            trigger_values = [
                'notification',
                'parent_status',
                'task_status',
                'task_create',
                'task_date',
            ]

        else:
            trigger_labels = [
                'Send a notification',
                #'Create a task for each process',
                #'Add a note',
                #'Set task complete',
                #'Delete versions',
            ]
            #TODO: enable task_complete
            trigger_values = [
                'notification',
                #'task_create_all',
                #'note_insert',
                #'task_complete',
                #'version_delete',
            ]

        

        security = Environment.get_security()
        is_admin = security.is_admin()

        if is_admin:
            trigger_labels.extend( [
                'Run Python/Server JS code',
                'Run Python trigger'
            ] )
            
            trigger_values.extend( [
                'custom_script',
                'python_class'
            ] )

        else:
            trigger_labels.extend( [
                'Run Server JS code'
            ] )
            
            trigger_values.extend( [
                'custom_script'
            ] )


        
        #trigger_edit = TaskCompleteTestWdg()
        #trigger_values.append(trigger_edit.get_trigger_type())


        


        #Action Area in Trigger Setting

        tr, td = table.add_row_cell()

        title = DivWdg()
        td.add(title)
        title.add("Action:")
        title.add_style("font-weight: bold")
        title.add_style("padding: 20 0 0 0")
        td.add("<hr/>")

        table.add_row()
        #td = table.add_cell()
        tr, td = table.add_row_cell()
        td.add_color("color", "color")
        td.add_style("padding: 10px")

        # Select box in Action Area 
            
        td.add("Do the following: ")
        
        #td = table.add_cell()
        # Action Select
        select = SelectWdg("trigger")
        select.set_option("labels", trigger_labels)
        select.set_option("values", trigger_values)
        if trigger_type:
            select.set_value(trigger_type)

        if isinstance(trigger, Notification):
            select.set_value("notification")
        elif trigger and trigger.get_value("script_path"):
            select.set_value("custom_script")

        # get the process sobject
        search = Search("config/process")
        search.add_filter("pipeline_code", self.pipeline_code)
        search.add_filter("process", self.process)
        process_sobj = search.get_sobject()
        
        # you can't always get a process_sobj
        self.process_code = ''
        if process_sobj:
            self.process_code = process_sobj.get_code()

        select.add_empty_option("-- Choose action --")
        td.add(select)
        
        trigger_sk = ''
        if trigger:
            trigger_sk = trigger.get_search_key()
            
        select.add_behavior( {
        'type': 'change',
        'kwargs': {
            'pipeline_code': self.pipeline_code,
            'process': self.process,
            'process_code': self.process_code,
            'search_key': trigger_sk
        },
        'cbjs_action': '''
        var top = bvr.src_el.getParent(".spt_trigger_detail_top");
        var content = top.getElement(".spt_trigger_add_top");
        var event_el = top.getElement(".spt_trigger_event");

        var event = event_el.value;
        bvr.kwargs['event'] = event;
         
        var trigger_type = bvr.src_el.value;
        var trigger_wdg;
        var trigger_cbk;
        if (trigger_type == "notification") {
            trigger_wdg = 'tactic.ui.tools.NotificationTriggerEditWdg';
            trigger_cbk = 'tactic.ui.tools.NotificationTriggerEditCbk';
        }
        else if (trigger_type == "parent_status") {
            trigger_wdg = 'tactic.ui.tools.TriggerParentStatusEditWdg';
            trigger_cbk = 'tactic.ui.tools.TriggerParentStatusEditCbk';
        }

        else if (trigger_type == "task_status") {
            trigger_wdg = 'tactic.ui.tools.StatusTriggerEditWdg';
            trigger_cbk = 'tactic.ui.tools.StatusTriggerEditCbk';
        }
        else if (trigger_type == "task_create") {
            trigger_wdg = 'tactic.ui.tools.TriggerCreateWdg';
            trigger_cbk = 'tactic.ui.tools.TriggerCreateCbk';
        }
        else if (trigger_type == "task_complete") {
            trigger_wdg = 'tactic.ui.tools.TriggerCompleteWdg';
            trigger_cbk = 'tactic.ui.tools.TriggerCompleteCbk';
        }
        else if (trigger_type == "task_date") {
            trigger_wdg = 'tactic.ui.tools.TriggerDateWdg';
            trigger_cbk = 'tactic.ui.tools.TriggerDateCbk';
        }
        else if (trigger_type == "custom_script") {
            trigger_wdg = 'tactic.ui.tools.PythonScriptTriggerEditWdg';
            trigger_cbk = 'tactic.ui.tools.PythonScriptTriggerEditCbk';
        }
        else if (trigger_type == "python_class") {
            trigger_wdg = 'tactic.ui.tools.PythonClassTriggerEditWdg';
            trigger_cbk = 'tactic.ui.tools.PythonClassTriggerEditCbk';
        }
        else {
            spt.behavior.replace_inner_html(content, "");
            content.setAttribute("spt_trigger_add_cbk", "");
            return;
        }

        spt.panel.load(content, trigger_wdg, bvr.kwargs)
        content.setAttribute("spt_trigger_add_cbk", trigger_cbk);

        '''
        } )

        td.add(HtmlElement.br(2))

        trigger_div = DivWdg()
        td.add(trigger_div)
        trigger_div.add_class("spt_trigger_add_top")
        #trigger_div.add_style("padding: 5px")
        #trigger_div.add_border()
        #trigger_div.add_color("background", "background", -5)
        #trigger_div.add_style("margin: 10px")

        kwargs = self.kwargs.copy()
        kwargs['trigger'] = trigger


        # determine detail widget to display
        if trigger_type == "notification":
            trigger_wdg = NotificationTriggerEditWdg(**kwargs)
            trigger_cbk = "tactic.ui.tools.NotificationTriggerEditCbk"

        elif trigger_type == "parent_status":
            trigger_wdg = TriggerParentStatusEditWdg(**kwargs)
            trigger_cbk = "tactic.ui.tools.TriggerParentStatusEditCbk"

        elif trigger_type == "task_status":
            trigger_wdg = StatusTriggerEditWdg(**kwargs)
            trigger_cbk = "tactic.ui.tools.StatusTriggerEditCbk"

        elif trigger_type == "task_create":
            trigger_wdg = TriggerCreateWdg(**kwargs)
            trigger_cbk = "tactic.ui.tools.TriggerCreateCbk"

        elif trigger_type == "task_date":
            trigger_wdg = TriggerDateWdg(**kwargs)
            trigger_cbk = "tactic.ui.tools.TriggerDateCbk"

        elif trigger_type == "custom_script":
            trigger_wdg = PythonScriptTriggerEditWdg(**kwargs)
            trigger_cbk = "tactic.ui.tools.PythonScriptTriggerEditCbk"

        elif trigger_type == "python_class":
            trigger_wdg = PythonClassTriggerEditWdg(**kwargs)
            trigger_cbk = "tactic.ui.tools.PythonClassTriggerEditCbk"

        else:
            trigger_wdg = DivWdg()
            #trigger_wdg.add("<i>-- No Details --</i>")
            trigger_cbk = ''

        trigger_div.add_attr("spt_trigger_add_cbk", trigger_cbk)
        trigger_div.add_attr("spt_class_name", Common.get_full_class_name(trigger_wdg))
        if trigger:
            trigger_div.add_attr("spt_search_key", trigger.get_search_key())
        trigger_div.add(trigger_wdg)




        button_div = DivWdg()
        button_div.add("<br/><hr/>")
        div.add(button_div)


        # FIXME: this does not delete the python script
        delete_button = ActionButtonWdg(title='Remove', tip='Remove the current trigger')
        button_div.add(delete_button)
        delete_button.add_style("float: left")
        delete_button.add_behavior( {
        'type': 'click_up',
        'search_key': search_key,
        'cbjs_action': '''
        if (! confirm( "Are you sure you wish to delete this trigger?") ) {
            return;
        }
        var server = TacticServerStub.get();
        server.delete_sobject(bvr.search_key);

        var top = bvr.src_el.getParent(".spt_trigger_top");
        spt.panel.refresh(top);
        '''
        } )


        button = ActionButtonWdg(title='Save')
        button.add_style("float: right")
        button_div.add(button)
       
        button.add_behavior(button_bvr)



        #from tactic.ui.panel import EditWdg
        #edit = EditWdg(search_type='config/trigger')
        #edit.set_sobject(trigger)
        #div.add(edit)


        return div




    def get_trigger_context_menu(self):
        menu = Menu(width=180)
        menu.set_allow_icons(False)
        menu.set_setup_cbfn( 'spt.smenu_ctx.setup_cbk' )


        menu_item = MenuItem(type='title', label='Actions')
        menu.add(menu_item)

        menu_item = MenuItem(type='action', label='Delete')
        menu_item.add_behavior( {
            'cbjs_action': '''
            var activator = spt.smenu.get_activator(bvr);
            '''
        } )
        menu.add(menu_item)

        return menu





class BaseTriggerEditWdg(BaseRefreshWdg):

    def get_trigger_type(self):
        pass

    def get_display_class(self):
        return Common.get_full_class_name(self)

    def get_callback_class(self):
        pass

    def get_display(self):
        return "No Display Defined"



class TaskCompleteTestWdg(BaseTriggerEditWdg):

    def get_trigger_type(self):
        return "task_complete"

    #def get_display_class(self):
    #    return 'tactic.ui.tools.TriggerCompleteWdg'

    def get_callback_class(self):
        return 'tactic.ui.tools.TriggerCompleteCbk'

    def get_display(self):
        return "TaskCompleteTestWdg"




class EventTriggerEditWdg(BaseRefreshWdg):
    ''' This class displays options for a chosen event'''
    def get_display(self):
        top = DivWdg()

        process = self.kwargs.get("process")
        pipeline_code = self.kwargs.get("pipeline_code")
        search_type = self.kwargs.get("search_type")

        if search_type:
            search = Search("sthpw/pipeline")
            search.add_filter("search_type", search_type)
            if pipeline_code:
                search.add_filter('code', pipeline_code)
            pipeline = search.get_sobject()
        else:
            pipeline = Pipeline.get_by_code(pipeline_code)

            if not pipeline:
                top.add("<br/>The pipeline [%s] does not exist.  If this pipeline is on your canvas, please save first.<br/>" % pipeline_code)
                return top


        event = self.kwargs.get("event")
        if not event:
            return top



        trigger = self.kwargs.get("trigger")
        if trigger:
            data = trigger.get_value("data", no_exception=True)
            if data:
                try:
                    data = jsonloads(data)
                except:
                    data = {}
                if not isinstance(data, list):
                    data = [data]
            else:
                data = []
        else:
            data = []

        if event == '__custom__':
            top.add("Event name: &nbsp;&nbsp;")
            text = TextInputWdg(name="custom_event")
            top.add(text)

            custom_event = self.kwargs.get("custom_event")
            if custom_event:
                text.set_value(custom_event)

            text.add_style("width: 200px")
            top.add_style("padding: 10px")


        #elif event.startswith("change|sthpw/task|status") and process:
        elif event.startswith("change|sthpw/task|status"):

            if process:
                process_obj = pipeline.get_process(process)
                if not process_obj:
                    top.add("<br/>The process item [%s] does not exist. You may need to save your pipeline first.<br/>" % process)
                    return top

                task_pipeline_code = process_obj.get_task_pipeline()
                task_pipeline = Pipeline.get_by_code(task_pipeline_code)
                if not task_pipeline:
                    task_pipeline_code='task'
                    task_pipeline = Pipeline.get_by_code(task_pipeline_code)
                task_statuses = task_pipeline.get_processes()
            elif search_type:
                # get all the processes for this search type
                pipelines = Pipeline.get_by_search_type(search_type)

                task_pipeline_code = "task"
                task_pipeline = Pipeline.get_by_code(task_pipeline_code)
                task_statuses = task_pipeline.get_processes()


                #outputs = pipeline.get_output_processes(process)
                #outputs = [x.get_name() for x in outputs]
                #inputs = pipeline.get_input_processes(process)
                #inputs = [x.get_name() for x in inputs]



            top.add("To: ")

            status = SelectWdg("src_status")
            status.set_option("values", task_statuses)
            
            for item in data:
                src_status = item.get("src_status")
                if src_status:
                    status.set_value(src_status)
                elif task_statuses:
                    status.set_value(task_statuses[-1])
                break

            top.add(status)
            top.add("<br/>")
            top.add_style("padding: 10px 0px")

        elif event.startswith("checkin|") and not process:
            # search_type mode does not have a process
            if trigger:
                if isinstance(trigger, Notification):
                    listen_process = trigger.get_value("process", no_exception=True)
                else:
                    listen_process = trigger.get_value("listen_process", no_exception=True)
            
            else:
                listen_process = None
            
            top.add_style("padding: 10px 0px")

            if not pipeline:
                return top
            inputs = pipeline.get_process_names()
            inputs = [str(x) for x in inputs]
            
            """  
            top.add("In the following process: <br/><br/>")
            checkbox = CheckboxWdg("this_process")
            process_div.add(checkbox)
            if not listen_process or listen_process == process:
                checkbox.set_checked()
            process_div.add(" this process")

            process_div.add("&nbsp;"*3 + " or " + "&nbsp;"*3)

            """
            span = SpanWdg('to')
            span.add_style('padding: 8px')

            process_div = DivWdg(span)
            process_div.add_style("margin-left: 6px")
            top.add(process_div)
            
            select = SelectWdg("listen_process")
            process_div.add(select)
            select.set_option("values", inputs)
            select.set_option("labels", inputs)
            select.add_empty_option("-- Select a Process --")
            
            if listen_process:
                select.set_value(listen_process)



        return top






class StatusTriggerEditWdg(BaseRefreshWdg):

    def get_display(self):
        trigger = self.kwargs.get("trigger")
        if trigger:
            self.data = trigger.get_value("data")
            if not self.data:
                self.data = {}
            else:
                try:
                    self.data = jsonloads(self.data)
                except:
                    self.data = {}
            if isinstance(self.data, dict):
                self.data = [self.data]
        else:
            self.data = []

        status_div = DivWdg()


        process = self.kwargs.get("process")
        pipeline_code = self.kwargs.get("pipeline_code")
        self.pipeline = Pipeline.get_by_code(pipeline_code)

        processes = self.pipeline.get_process_names()



        #use_parent = True
        #search_type = self.pipeline.get_value("search_type")
        #print("search_type: ", search_type)
        #from pyasm.biz import Schema
        #schema = Schema.get()
        #related_types  = schema.get_related_search_types(search_type)





        outputs = self.pipeline.get_output_processes(process)
        outputs = [x.get_name() for x in outputs]
        inputs = self.pipeline.get_input_processes(process)
        inputs = [x.get_name() for x in inputs]

        status_div.add("This process<br/>")
        process_div = self.get_process_div(process)
        status_div.add(process_div)
        if process in processes:
            processes.remove(process)



        if inputs:
            status_div.add("<br/>Inputs:<br/>")
        for input in inputs:
            process_div = self.get_process_div(input)
            status_div.add(process_div)
            if input in processes:
                processes.remove(input)

        if outputs:
            status_div.add("<br/>Outputs:<br/>")
        for output in outputs:
            process_div = self.get_process_div(output)
            status_div.add(process_div)
            if output in processes:
                processes.remove(output)

        if processes:
            status_div.add("<br/>Others:<br/>")
        for process in processes:
            process_div = self.get_process_div(process)
            status_div.add(process_div)





        status_div.add("<br/>")
      
        return status_div



    def get_process_div(self, process):
        process_div = DivWdg()
        process_div.add_style("padding: 8px 5px")

        checkbox = CheckboxWdg("dst_process")
        process_div.add(checkbox)
        checkbox.add_attr("spt_is_multiple", "true")
        checkbox.add_style("margin: 5px 8px 8px -8px")

        is_checked = False
        dst_status = ''
        for data in self.data:
            if data.get('dst_process') == process:
                checkbox.set_checked()
                dst_status = data.get('dst_status')
                is_checked = True
                break
        checkbox.set_option("value", process)
        process_div.add('Set "%s" status ' % process)


        task_pipeline = None
        process_obj = self.pipeline.get_process(process)
        if process_obj:
            task_pipeline_code = process_obj.get_task_pipeline()
            task_pipeline = Pipeline.get_by_code(task_pipeline_code)

        if not task_pipeline:
            task_pipeline_code='task'
            task_pipeline = Pipeline.get_by_code(task_pipeline_code)
        task_statuses = task_pipeline.get_processes()


        statuses = []
        for task_status in task_statuses:
            statuses.append(task_status.get_name())

        process_div.add(" to ")

        status_select = SelectWdg("dst_status")
        status_select.add_attr("spt_is_multiple", "true")
        if is_checked:
            status_select.set_value(dst_status )
        elif statuses:
            status_select.set_value(statuses[0])
        
        process_div.add(status_select)
        status_select.set_option("values", statuses)
        status_select.add_style("margin-top: 5px")
        status_select.add_style("margin-left: 15px")

        return process_div





class BaseTriggerEditCbk(Command):

    def get_trigger(self):
        # Create the trigger from the options


        scope = self.kwargs.get("scope")


        search_key = self.kwargs.get("search_key")

        event = self.kwargs.get("event")
        if event == '__custom__':
            event = self.kwargs.get("custom_event")


        pipeline_code = self.kwargs.get("pipeline_code")
        process = self.kwargs.get("process")
        listen_process = self.kwargs.get("listen_process")
        search_type = self.kwargs.get("search_type")

        code = self.kwargs.get("code")
        title = self.kwargs.get("title")
        description = self.kwargs.get("description") 



        if search_key:
            trigger = Search.get_by_search_key(search_key)
            if trigger.get_base_search_type() != 'config/trigger':
                trigger.delete()
                trigger = SearchType.create("config/trigger")
        else:
            trigger = SearchType.create("config/trigger")


        if code:
            trigger.set_value("code", code)

        trigger.set_value("event", event)
        trigger.set_value("title", title)
        trigger.set_value("description", description)


        if process:
            if scope == "local":
                pipeline_code = self.kwargs.get("pipeline_code")
                search = Search("config/process")
                search.add_filter("pipeline_code", pipeline_code)
                search.add_filter("process", process)
                process_sobj = search.get_sobject()
                trigger.set_value("process", process_sobj.get_code())
            else:
                trigger.set_value("process", process)


        if listen_process:
            trigger.set_value("listen_process", listen_process)

        if search_type:
            trigger.set_value("search_type", search_type)
        else: 
            if event.startswith('checkin'):
                trigger.set_value("search_type", "")



        class_name = self.get_class_name()
        if class_name:
            trigger.set_value("class_name", class_name)
            trigger.set_value("script_path", "")
        else:
            trigger.set_value("class_name", "")
            trigger.set_value("script_path", "")



        trigger.set_value("mode", 'same process,same transaction')

        return trigger






class StatusTriggerEditCbk(BaseTriggerEditCbk):


    def get_class_name(self): 
        class_name = 'tactic.command.PipelineTaskStatusTrigger'
        return class_name


    def execute(self):


        self.process = self.kwargs.get("process")
        self.src_status = self.kwargs.get("src_status")
        
        dst_statuses = self.kwargs.get("dst_status")
        dst_processes = self.kwargs.get("dst_process")
        self.dst_statuses = []
        self.dst_processes = []
        for tmp_status, tmp_process in zip(dst_statuses, dst_processes):
            if tmp_process:
                self.dst_statuses.append(tmp_status)
                self.dst_processes.append(tmp_process)
                

        # Build a data structure for this.  Use a very simple one-to-one
        # rule/action setup
        data_list = []
        for i, dst_process in enumerate(self.dst_processes):
            dst_status = self.dst_statuses[i]
            data = {
                "src_process": self.process,
                "src_status": self.src_status,
                "dst_process": dst_process,
                "dst_status": dst_status
            }
            data_list.append(data)

        data = jsondumps(data_list)


        trigger = self.get_trigger()


        trigger.set_value("data", str(data))
        trigger.commit()


        search_key = SearchKey.get_by_sobject(trigger)
        self.info['search_key'] = search_key





class TriggerParentStatusEditWdg(BaseRefreshWdg):

    def get_display(self):
        div = DivWdg()

        process = self.kwargs.get("process")

        column_values = []
        trigger = self.kwargs.get("trigger")
        if trigger:
            data = trigger.get_value("data")
            data = jsonloads(data)
        else:
            data = {}


        dst_status = data.get("dst_status") or ""

        labels = ['Pending', 'In Progress', 'Complete', 'Approved']
        values = labels

        div.add("To Status:")
        select = SelectWdg("dst_status")
        div.add(select)
        select.set_option("labels", labels)
        select.set_option("values", values)
        select.set_value(dst_status)
        div.add("<br/>")


        return div





class TriggerParentStatusEditCbk(BaseTriggerEditCbk):

    def get_class_name(self): 
        class_name = 'tactic.command.PipelineParentStatusTrigger'
        return class_name


    def execute(self):

        self.process = self.kwargs.get("process")
        dst_status = self.kwargs.get("dst_status")

        data = {
            'dst_status': dst_status
        }


        trigger = self.get_trigger()

        trigger.set_value("data", jsondumps(data))
        trigger.commit()


        search_key = SearchKey.get_by_sobject(trigger)
        self.info['search_key'] = search_key








class TriggerCreateWdg(BaseRefreshWdg):

    def get_display(self):
        top = DivWdg()

        process = self.kwargs.get("process")
        pipeline_code = self.kwargs.get("pipeline_code")
        outputs =[]
        
        #in case there is no pipeline_code or process passed in
        if pipeline_code:
            pipeline = Pipeline.get_by_code(pipeline_code)
            if pipeline:
                outputs = pipeline.get_output_processes(process)
            outputs = [x.get_name() for x in outputs]

        trigger = self.kwargs.get("trigger")
        output_values = []
        if trigger:
            data = trigger.get_value("data")
            data = jsonloads(data)
            output_values = data.get("output")
            if not output_values:
                output_values = []



        outputs_div = DivWdg()
        top.add(outputs_div)
        outputs_div.add("Create output tasks for the following processes:")
        outputs_div.add("<br/>"*2)
        for output in outputs:
            output_div = DivWdg()
            outputs_div.add(output_div)
            checkbox = CheckboxWdg("output")
            checkbox.set_option("value", output)
            checkbox.add_attr("spt_is_multiple", "true")

            if output in output_values:
                checkbox.set_checked()

            output_div.add(checkbox)
            output_div.add(output)

        return top




class TriggerCompleteWdg(BaseRefreshWdg):

    def get_display(self):
        top = DivWdg()

        process = self.kwargs.get("process")
        pipeline_code = self.kwargs.get("pipeline_code")

        top.add(pipeline_code)
        return top

        """
        pipeline = Pipeline.get_by_code(pipeline_code)
        outputs = pipeline.get_output_processes(process)
        outputs = [x.get_name() for x in outputs]

        trigger = self.kwargs.get("trigger")
        output_values = []
        if trigger:
            data = trigger.get_value("data")
            data = jsonloads(data)
            output_values = data.get("output")
            if not output_values:
                output_values = []



        outputs_div = DivWdg()
        top.add(outputs_div)
        outputs_div.add("Create output tasks for the following processes:")
        outputs_div.add("<br/>"*2)
        for output in outputs:
            output_div = DivWdg()
            outputs_div.add(output_div)
            checkbox = CheckboxWdg("output")
            checkbox.set_option("value", output)

            if output in output_values:
                checkbox.set_checked()

            output_div.add(checkbox)
            output_div.add(output)

        return top
        """



class TriggerCompleteCbk(BaseTriggerEditCbk):
    def execute(self):
        pass






       

class TriggerDateWdg(BaseRefreshWdg):

    def get_display(self):
        top = DivWdg()

        process = self.kwargs.get("process")

        column_values = []
        trigger = self.kwargs.get("trigger")
        if trigger:
            data = trigger.get_value("data")
            data = jsonloads(data)
            column_values = data.get("column")
            if not column_values:
                column_values = []


        columns = ['actual_start_date', 'actual_end_date']

        columns_div = DivWdg()
        top.add(columns_div)
        columns_div.add("Set the following actual date:")
        columns_div.add("<br/>"*2)
        for column in columns:
            column_div = DivWdg()
            column_div.add_style("padding: 5px")
            columns_div.add(column_div)
            radio = RadioWdg("column")
            radio.set_option("value", column)

            if column in [column_values]:
                radio.set_checked()

            name = Common.get_display_title(column)
            column_div.add(radio)
            column_div.add(name)

        return top



class TriggerDateCbk(BaseTriggerEditCbk):

    def get_class_name(self): 
        class_name = 'tactic.command.PipelineTaskDateTrigger'
        return class_name



    def execute(self):

        src_status = self.kwargs.get("src_status")
        column = self.kwargs.get("column")

        trigger = self.get_trigger()

        data = {
            'src_status': src_status,
            'column': column
        }
        trigger.set_value("data", jsondumps(data))

        trigger.commit()

        search_key = SearchKey.get_by_sobject(trigger)
        self.info['search_key'] = search_key










class TriggerCreateCbk(BaseTriggerEditCbk):

    def get_class_name(self): 
        class_name = 'tactic.command.PipelineTaskCreateTrigger'
        return class_name



    def execute(self):

        outputs = self.kwargs.get("output")
        if isinstance(outputs, basestring) and outputs:
            outputs = [outputs]
        elif isinstance(outputs, list):
            outputs = [p for p in outputs if p]
        else:
            outputs = []
            
        data = {
            'output': outputs
        }
        
        src_status =  self.kwargs.get("src_status")
        if src_status:
            data["src_status"] = src_status
        
        trigger = self.get_trigger()
        trigger.set_value("data", jsondumps(data))
        trigger.commit()

        search_key = SearchKey.get_by_sobject(trigger)
        self.info['search_key'] = search_key



class NotificationTriggerEditWdg(BaseRefreshWdg):
    def get_display(self):
        trigger = self.kwargs.get("trigger")
        if not trigger:
            search_key = self.kwargs.get("search_key")
            if search_key:
                trigger = Search.get_by_search_key(search_key)

        if trigger and isinstance(trigger, Notification):
            event = trigger.get_value("event")
            subject = trigger.get_value("subject")
            message = trigger.get_value("message")
            mail_to = trigger.get_value("mail_to")
            mail_cc = trigger.get_value("mail_cc")

            data = trigger.get_json_value("data") or {}
        else:
            event = ''
            subject = ''
            message = ''
            mail_to = ''
            mail_cc = ''

            data = {}

        # search of the notification object
        search_key = self.kwargs.get("search_key")


        notification_div = DivWdg()
        notification_div.add_class("spt_notification_top")

        hidden = HiddenWdg("search_key")
        hidden.set_value(search_key)
        notification_div.add(hidden)


        is_custom = False
        if event:
            cmd = NotificationGetTemplateCbk(event=event)
            cmd.execute()
            info = cmd.get_info()
            default_subject = info.get("subject")
            default_message = info.get("message")

            if message == '' and subject == '':
                is_custom = False
                message = default_message
                subject = default_subject

            elif message != default_message or subject != default_subject:
                is_custom = True
            else:
                message = default_message
                subject = default_subject
                is_custom = False


        if message == '' and subject == '':
            is_custom = False

        notification_div.add("Use Default Message: ")
        checkbox = CheckboxWdg("default")

        if not is_custom: 
            checkbox.set_checked()


        #checkbox = ActionButtonWdg(title="Set", tip="Set Default Email")
        notification_div.add(checkbox)
        checkbox.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var trigger_top = bvr.src_el.getParent(".spt_trigger_top");
            var event_el = trigger_top.getElement(".spt_trigger_event");


            var top = bvr.src_el.getParent(".spt_notification_top");
            var message = top.getElement(".spt_notification_message");
            var subject = top.getElement(".spt_notification_subject");
            var body = top.getElement(".spt_notification_body");

            var class_name = 'tactic.ui.tools.NotificationGetTemplateCbk';
            var kwargs = {
                event: event_el.value
            }
            var server = TacticServerStub.get();
            var ret_val = server.execute_cmd(class_name, kwargs);
            var data = ret_val.info;

            if (bvr.src_el.checked) {
                if ( (subject.value != '' && body.value != '') && 
                  (subject.value != data.subject || body.value != data.message))
              {
                    if (!confirm("Default subject or message is different from entered values.  Are you sure you wish to replace?")) {
                        return;
                    }
                }
                subject.value = data.subject;
                body.value = data.message;

            }
            else {
                message.setStyle("display", "");
                //subject.value = '';
                //body.value = '';
            }

            '''
        } )


        notification_div.add("<br/>")
        notification_div.add("<br/>")


        message_div = DivWdg()
        notification_div.add(message_div)
        if not is_custom:
            message_div.add_style("display: none")
        message_div.add_class("spt_notification_message")

        message_div.add("Subject: <br/>")
        subject_text = TextWdg("subject")
        subject_text.set_value(subject)
        subject_text.add_style("width: 500px")
        subject_text.add_class("spt_notification_subject")
        message_div.add(subject_text)

        message_div.add("<br/>")
        message_div.add("<br/>")

        message_div.add("Message: <br/>")
        """
        select = SelectWdg("add_expression")
        message_div.add(select)
        select.add_empty_option("-- Add Expression --")
        expr_values = [
            '{$LOGIN}',
            '{@GET(.description)}',
            '{$TODAY}'
        ]
        expr_labels = [
            'Me - {$LOGIN}',
            'Description - {$GET(.description)}',
            'Today - {$TODAY}'
        ]
        select.set_option("values", expr_values)
        select.set_option("labels", expr_labels)
        select.add_behavior( {
        'type': 'change',
        'cbjs_action': '''
        var top = bvr.src_el.getParent(".spt_notification_top");
        var body = top.getElement(".spt_notification_body");
        body.value = body.value + bvr.src_el.value;
        '''
        } )
        """
        body_text = TextAreaWdg("body")
        body_text.add_class("spt_notification_body")
        
        if message:
            body_text.set_value(message)
        body_text.add_behavior({'type':'load',
            'message': message,
            'cbjs_action': '''if (bvr.message)
                                bvr.src_el.value = bvr.message'''})

        body_text.add_style("width: 500px")
        body_text.add_style("height: 250px")
        message_div.add(body_text)


        message_div.add("<br/>")


        notification_div.add("Mail To: <br/>")
        to_text = TextAreaWdg("mail_to")
        to_text.add_class("form-control")
        to_text.set_value(mail_to)
        to_text.add_style("width: 100%")
        notification_div.add(to_text)

        notification_div.add("<br/>")
        notification_div.add("Mail Cc: <br/>")
        cc_text = TextAreaWdg("mail_cc")
        cc_text.add_class("form-control")
        cc_text.set_value(mail_cc)
        cc_text.add_style("width: 100%")
        notification_div.add(cc_text)


        notification_div.add("<br/>")

        notification_div.add("Generate Temporary Login Ticket: &nbsp;")
        checkbox = CheckboxWdg("login_ticket_create")
        notification_div.add(checkbox)

        if data.get("login_ticket_create"):
            checkbox.set_option("checked", "true")


        return notification_div




__all__.append("NotificationGetTemplateCbk")
class NotificationGetTemplateCbk(Command):

    def execute(self):

        event = self.kwargs.get("event")
        search_type = self.kwargs.get("search_type")

        if event.startswith("insert|")and not event.startswith("insert|sthpw/"):
            event = "insert"
        elif event.startswith("update|")and not event.startswith("update|sthpw/"):
            event = "update"
        elif event.startswith("change|")and not event.startswith("change|sthpw/"):
            event = "change"


        path = __file__
        dirname = os.path.dirname(path)
        path = "%s/mail_templates.py" % (dirname)

        f = open(path, 'r')
        contents = f.read()
        f.close()

        templates = eval(contents)

        mail = templates.get(event)
        if not mail:
            mail = {
                'subject': '',
                'message': ''
            }

        self.info = mail




class NotificationTriggerEditCbk(Command):

    def execute(self):
        notification = None

        search_key = self.kwargs.get("search_key")
        if search_key:
            notification = Search.get_by_search_key(search_key) 
            # verify if this is a trigger search_key or notification search_key
            # it could be a trigger search_key when editing an existing trigger
            if not isinstance(notification, Notification):
                notification = None
        process = self.kwargs.get("process")
        scope = self.kwargs.get("scope")
        listen_process = self.kwargs.get("listen_process")
        search_type = self.kwargs.get("search_type")
        use_default = self.kwargs.get("default") == 'on'

        login_ticket_create = self.kwargs.get("login_ticket_create") == "on"

        title = self.kwargs.get("title")
        description = self.kwargs.get('description')

        event = self.kwargs.get("event")

        if event == '__custom__':
            event = self.kwargs.get("custom_event")
        assert event
        subject = self.kwargs.get("subject")
        message = self.kwargs.get("body")
        mail_to = self.kwargs.get("mail_to")
        mail_cc = self.kwargs.get("mail_cc")

        project_code = Project.get_project_code()

        if not notification:
            notification = SearchType.create("sthpw/notification")

        notification.set_value("event", event)
        notification.set_value("title", title)

        # listen process takes precesdencce
        if listen_process:
            notification.set_value("process", listen_process)
        elif process:
            if scope == "local":
                pipeline_code = self.kwargs.get("pipeline_code")
                search = Search("config/process")
                search.add_filter("pipeline_code", pipeline_code)
                search.add_filter("process", process)
                process_sobj = search.get_sobject()
                notification.set_value("process", process_sobj.get_code())
            else:
                notification.set_value("process", process)
        if search_type:
            notification.set_value("search_type", search_type)

        if use_default:
            cmd = NotificationGetTemplateCbk(event=event)
            cmd.execute()
            info = cmd.get_info()
            subject = info.get("subject")
            message = info.get("message")


        notification.set_value("subject", subject)
        notification.set_value("description", description)
        notification.set_value("message", message)
        notification.set_value("mail_to", mail_to)
        notification.set_value("mail_cc", mail_cc)
        notification.set_value("project_code", project_code)


        data = notification.get_json_value("data") or {}

        # unfortunately, notifications have a different filter method than
        # normal triggers ... this needs to made all consistent at some point
        src_status = self.kwargs.get("src_status")
        if src_status:
            rules = '''<rules>
<rule>@GET(.status) == '%s'</rule>
</rules>''' % src_status
            notification.set_value("rules", rules)

            # Build a data structure for this.  Use a very simple one-to-one
            # rule/action setup
            data["src_process"] = process
            data["src_status"] = src_status



        data["login_ticket_create"] = login_ticket_create;
        notification.set_json_value("data", data)


        notification.commit()

        search_key = SearchKey.get_by_sobject(notification)
        self.info['search_key'] = search_key






class PythonScriptTriggerEditWdg(BaseRefreshWdg):

    def get_display(self):
        
     
        is_admin = Environment.get_security().is_admin()
        """
        if not is_admin:
            div = DivWdg()
            div.add_style("width: 300px")
            div.add_style("padding: 6px")
            div.add_style("text-align: center")
            div.add_style("margin: 2px auto")
            div.add_color("background", "background3")
            div.add_border()
            div.add("Only admin can create python scripts")
        """

        web = WebContainer.get_web()
        div = DivWdg()
        div.add_class("spt_python_script_trigger_top")
        trigger = self.kwargs.get("trigger")

        event = None
        trigger_code = ''
        if not trigger:
            search_key = self.kwargs.get("search_key")
            # event from web takes precedence
            event = web.get_form_value('event')
            if not event:
                event = self.kwargs.get("event")

            if search_key and search_key !='null':
                trigger = Search.get_by_search_key(search_key)

        language = ''
        if trigger:
            trigger_code = trigger.get_code()
            # event could be switched by the user before saving
            # only get it from the trigger sobj as a last resort
            if not event:
                event = trigger.get_value("event")
            script_path = self.kwargs.get("script_path")
            if not script_path:
                script_path = trigger.get_value("script_path", no_exception=True)
            script_sobj = None
            if script_path:
                script_sobj = CustomScript.get_by_path(script_path)
            if not script_sobj:
                script = ''
            else:
                script = script_sobj.get_value("script")
                language = script_sobj.get_value("language")



        else:
            script_path = ''
            script_sobj = None
            script = ''


        self.add_script_wdg(div, script_path, is_admin, trigger_code, language)

        edit_button = ActionButtonWdg(title="Script Editor", tip="Open Script Editor", color="secondary")
        edit_button.add_style("float: right")
        edit_button.add_style("padding: 5px 0px")
        div.add(edit_button)
        edit_button.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var class_name = 'tactic.ui.app.ScriptEditorWdg'
            spt.panel.load_popup("TACTIC Script Editor", class_name);
            '''
        } )

        div.add(HtmlElement.br(2))

      

        return div


    def add_script_wdg(self, div, script_path, is_admin, trigger_code, language):


        # This referes to a class that doesn't exist
        return

        if is_admin:
            div.add("Language:")
            select = SelectWdg("language")
            div.add(select)
            select.set_option("labels", "Python|Server JS")
            select.set_option("values", "python|server_js")
            select.set_value(language)
            div.add("<br/>")
        else:
            title_div = DivWdg("Language: Server JS")
            title_div.add_style('margin-bottom: 6px')

            div.add(title_div)
            hidden = HiddenWdg('language','server_js')
            div.add(hidden)



        config_xml = []
        config_xml.append('''
        <config>
        <tab>
        ''')

        expected_script_path = "%s/%s" %(TriggerToolWdg.FOLDER_PREFIX, trigger_code)
        config_xml.append('''
        <element name='script_path'>
          <display class='tactic.ui.tools.ScriptEditWdg'>
              <script_path>%s</script_path>
              <is_admin>%s</is_admin>
              <expected_script_path>%s</expected_script_path>
              <show_language>false</show_language>
          </display>
        </element>
        '''%(script_path,  str(is_admin).lower(), expected_script_path))
        
        config_xml.append('''
        </tab>
        </config>
        ''')
        config_xml = "".join(config_xml)

        tab = TabWdg(config_xml=config_xml, width="400px", show_add=False)
        div.add(tab)

class PythonScriptTriggerEditCbk(BaseTriggerEditCbk):

    def get_class_name(self): 
        return None



    def execute(self):

        scope = self.kwargs.get("scope")
        language = self.kwargs.get("language")

        trigger = self.get_trigger()

        # Get the trigger code
        trigger_code = self.kwargs.get('code')
        if not trigger_code:
            trigger_code = trigger.get_value("code")
            if not trigger_code:
                # if a code does not exist yet
                trigger.commit()
                trigger_code = trigger.get_value("code")

        search_type = self.kwargs.get("search_type")

        script = self.kwargs.get("script")
        script_path = ''
        # Get the script path or script
        script_path_folder = self.kwargs.get("script_path_folder")
        script_path_title = self.kwargs.get("script_path_title")
        if script_path_folder and script_path_title:
            script_path = '%s/%s'%(script_path_folder, script_path_title)
        elif not script:
            # saving from Create New
            script = self.kwargs.get('script_new')
        
        
        if not script:
            raise TacticException("Your script is empty. Please save a valid script.")

        if not script_path:
            script_path = trigger.get_value("script_path")
        
        # If script path is defined, then save script to script path.
        # Otherwise, create a new script path entry.
        # TODO: fix the auto-gen script path to be _triggers/<pipeline_code>/<process_code>
        # maybe, but certain triggers are not pipeline or process  related
        if not script_path:
            script_path = "%s/%s" % (TriggerToolWdg.FOLDER_PREFIX, trigger.get_code())

        # Save or create a new custom script
        script_sobj = CustomScript.get_by_path(script_path)
        if not script_sobj:
            script_sobj = SearchType.create("config/custom_script")

        dirname = os.path.dirname(script_path)
        title = os.path.basename(script_path)
        script_sobj.set_value("folder", dirname)
        script_sobj.set_value("title", title)
        script_sobj.set_value("script", script) 
        script_sobj.set_value("language", language) 
        script_sobj.commit()

        # Update the trigger
        trigger.set_value("code", trigger_code)

        event = self.kwargs.get("event")
        if event == "change|sthpw/task|status":
            src_status = self.kwargs.get("src_status")
            src_process = self.kwargs.get("process")
            data = {
                'src_status': src_status,
                'src_process': src_process
            }
            data = jsondumps(data)
            trigger.set_value("script_path", script_path)
            trigger.set_value("data", data)
            trigger.set_value("class_name", "tactic.command.PipelineTaskStatusTrigger")
        else:
            trigger.set_value("class_name", "")
            trigger.set_value("data", "")
            trigger.set_value("script_path", script_path)

        trigger.commit()
        
        search_key = SearchKey.get_by_sobject(trigger)
        self.info['search_key'] = search_key



class PythonClassTriggerEditWdg(BaseRefreshWdg):

    def get_display(self):

        is_admin = Environment.get_security().is_admin()
        """
        if not is_admin:
            div = DivWdg()
            div.add_style("width: 300px")
            div.add_style("padding: 30px")
            div.add_style("text-align: center")
            div.add_style("margin: 20px auto")
            div.add_color("background", "background3")
            div.add_border()
            div.add("Only administrators can create python class triggers.")
            return div


        """
        div = DivWdg()
        div.add_class("spt_python_class_top")

        trigger = self.kwargs.get("trigger")
        if not trigger:
            search_key = self.kwargs.get("search_key")
            if search_key:
                trigger = Search.get_by_search_key(search_key)

        class_name = ''
        if trigger:
            class_name = trigger.get_value("class_name")
            if class_name == "tactic.command.PipelineTaskStatusTrigger":
                data = trigger.get_json_value("data")
                if data and isinstance(data, dict):
                    class_path = data.get("class_path")
                    if class_path:
                        class_name = class_path

        div.add("This will run the following python class as a server side trigger.  The class path should be in the Python path and the class should be derived from pyasm.command.Trigger<br/><br/>")
        div.add("Python Class Path: <br/>")
        
        class_path_text = TextWdg("class_path")
        div.add(class_path_text)
        if class_name:
            class_path_text.set_value("class_name")
        class_path_text.add_class("spt_python_class_text")
        class_path_text.add_class("form-control")
        class_path_text.add_styles("width: 70%; margin: 5px 5px 5px 0px;")
        class_path_text.add_styles("display: inline-block; float: left;")
        class_path_text.set_value(class_name)


        test_button = ActionButtonWdg(title="Test", tip="Click to test if the class can be found")
        div.add(test_button)
        test_button.add_style("display: inline-block")
        test_button.add_style("margin: 5px")
        test_button.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        var top = bvr.src_el.getParent(".spt_python_class_top");
        var el = top.getElement(".spt_python_class_text");
        var class_path = el.value;
        if (class_path == "") {
            spt.alert("Please enter a class path first");
            return;
        }

        var server = TacticServerStub.get();
        var ret_val = server.class_exists(class_path);
        if (ret_val) {
            spt.alert("Class exists");
        }
        else {
            spt.alert("Could not find class");
        }
        '''
        } )
        test_button.add_style("margin-top: -5px")

        div.add("<br/>"*2)

        return div


class PythonClassTriggerEditCbk(BaseTriggerEditCbk):

    def get_class_name(self):
        return None

    def execute(self):

        trigger = self.get_trigger()

        class_path = self.kwargs.get("class_path")  
        event = self.kwargs.get("event")
        
        if event == "change|sthpw/task|status":
            data = {'class_path': class_path}
            src_status = self.kwargs.get("src_status")
            src_process = self.kwargs.get("process")
            if src_status:
                data['src_status'] = src_status
            if src_process:
                data['src_process'] = src_process
            data = jsondumps(data)
            trigger.set_value("data", data)
            trigger.set_value("class_name", "tactic.command.PipelineTaskStatusTrigger")
        else:
            trigger.set_value("class_name", class_path)
 
        trigger.commit()
        
        search_key = SearchKey.get_by_sobject(trigger)
        self.info['search_key'] = search_key

