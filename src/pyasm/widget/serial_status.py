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

__all__ = ['SimpleStatusWdg','SimpleStatusCmd','SerialStatusWdg','SerialStatusCmd', 'StatusUpdateAction']

from pyasm.common import Marshaller, Container, Environment, Common
from pyasm.search import SObjectAttr, Sql
from pyasm.biz import StatusAttr2, StatusEnum, SimpleStatusAttr,\
    HierarchicalStatusAttr, Task, Pipeline, StatusLog
from pyasm.web import *
from pyasm.search import SObjectFactory, Search, SObject
from pyasm.command import Trigger, EmailTrigger, Command, CommandExitException, DatabaseAction
from pyasm.security import *

from input_wdg import *
from icon_wdg import IconWdg
from table_element_wdg import *

from web_wdg import IconSubmitWdg




class SimpleStatusWdg(BaseTableElementWdg):

    def init(self):
        self.post_ajax_script = None

    def preprocess(self):
        self.post_ajax_script = None

    def set_post_ajax_script(self, script):
        self.post_ajax_script = script


    def get_display(self):

        sobject = self.get_current_sobject()
        search_key = sobject.get_search_key()
        value = sobject.get_value(self.name)
        self.select = ActionSelectWdg("status_%s" % search_key)

        empty = self.get_option("empty")
        if empty:
            self.select.set_option("empty", empty )

        pipeline_code = self.get_option("pipeline")

        widget = Widget()
        self.select.set_id("status_%s" % search_key)

        setting = self.get_option("setting")
        if setting:
            self.select.set_option("setting", setting )
        else:
            if pipeline_code:
                pipeline = Pipeline.get_by_code(pipeline_code)
            else:
                if sobject.has_value('pipeline_code'):
                    pipeline_code = sobject.get_value('pipeline_code')
                if isinstance(sobject, Task):
                    if not pipeline_code:
                        pipeline_code = 'task'
                pipeline = Pipeline.get_by_code(pipeline_code)
                if not pipeline:
                    return "No pipeline"
                """
                status_attr = sobject.get_attr("status")
                if status_attr:
                    pipeline = status_attr.get_pipeline()
                else:
                    return "No pipeline"
                """
            processes = pipeline.get_process_names()
            allowed_processes = []
            security = Environment.get_security()

            # has to allow it if it has already been set
            for process in processes:
                if value == process or security.check_access("process_select", process, access='view'):
                    allowed_processes.append(process)

            self.select.set_option("values", "|".join(allowed_processes) )

            if not value and processes:
                value = processes[0]

            # add the item if it is an obsolete status, alert
            # the user to change to the newly-defined statuses
            if value not in processes:
                self.select.append_option(value, value)
                self.select.set_class('action_warning')

        self.select.set_value( value )

        # TODO: this is a little cumbersome to know all this simply to
        # execute a command using ajax
        """ 
        div_id = widget.generate_unique_id('simple_status_wdg')
        cmd = AjaxLoader(div_id)
        marshaller = cmd.register_cmd("SimpleStatusCmd")
        marshaller.set_option('search_key', search_key)
        marshaller.set_option('attr_name',  self.name)
    
        self.select.add_event("onchange", cmd.get_on_script(True) )
        """

        js_action = "TacticServerCmd.execute_cmd('pyasm.widget.SimpleStatusCmd', '',\
                {'search_key': '%s', 'attr_name': '%s'}, {'value': bvr.src_el.value});" %(search_key, self.name)

        # build the search key
        #search_key = "%s|%s" % (self.search_type, self.search_id)
        
        bvr = {'type': 'change', 'cbjs_action': js_action}
        if self.post_ajax_script:
            bvr['cbjs_postaction'] = self.post_ajax_script

        self.select.add_behavior(bvr)
        div = DivWdg(self.select)
        div.add_style('float: left')
        widget.add(div)
       
        return widget

   

        

class SimpleStatusCmd(Command):
    
    def __init__(self, **kwargs):
        super(SimpleStatusCmd,self).__init__(**kwargs)
        self.search_key = self.kwargs.get('search_key')
        self.attr_name = self.kwargs.get('attr_name')
        self.users = []
        self.sobject = None

    def get_title(self):
        return "SimpleStatusCmd"

    def set_search_key(self, search_key):
        self.search_key = search_key

    def set_attr_name(self, attr_name):
        self.attr_name = attr_name

    def check(self):
        return True


    def execute(self):

        web = WebContainer.get_web()
        value = web.get_form_value('value')
        if self.search_key == None or value == None or self.attr_name == None:
            raise CommandExitException()


        sobject = Search.get_by_search_key(self.search_key)
        old_value = sobject.get_value(self.attr_name)
        sobject.set_value(self.attr_name, value)
        sobject.commit()

        # setting target attributes if sobject is a task
        if sobject.get_search_type_obj().get_base_key() == Task.SEARCH_TYPE:
            task = sobject

            # FIXME: not sure what this if for???
            self.users = [task.get_value("assigned")]

            process_name = task.get_value('process')


            task_description = task.get_value("description")

            self.parent = task.get_parent()
            # it should be task, notification will get the parent in the 
            # email trigger logic
            self.sobject = task
            code = self.parent.get_code()
            name = self.parent.get_name()
            self.info['parent_centric'] = True
            self.description = "%s set to '%s' for %s (%s), task: %s, %s" % (\
                self.attr_name.capitalize(), value, code, name, process_name, task_description)


            # set the states of the command
            pipeline = Pipeline.get_by_sobject(self.parent)
            process = pipeline.get_process(process_name)
            completion = task.get_completion()

            if pipeline and process:
                self.set_process(process_name)
                self.set_pipeline_code( pipeline.get_code() )
                if completion == 100:
                    self.set_event_name("task/approved")
                else:
                    self.set_event_name("task/change")
                    


        else:
            self.sobject = sobject
            code = self.sobject.get_code()

            self.description = "%s set to '%s' for %s" % (\
                self.attr_name.capitalize(), value, code)

            process_name = "None"
            self.info['parent_centric'] = False

        self.sobjects.append(self.sobject)
       
        # set the information about this command
        self.info['to'] = value
        self.info['process'] = process_name
        

       
        # if this is successful, the store it in the status_log
        #StatusLog.create(sobject,value,old_value)


   
    def get_info_keys(self):
        return ['to', 'process']


class SerialStatusWdg(BaseTableElementWdg):
    '''widget for serial approval process.  only 1 process can
    be "in_progress" at a time'''
    CONNECTION_VIEW = 'connection'
    SIMPLE_VIEW = 'simple'
    STATUS_CHECK = 'status_check'
    STATUS_CMD_INPUT = 'serial_status_input'
    TRIGGER = 'set_status'

    def init(self):
        WebContainer.register_cmd("pyasm.widget.SerialStatusCmd")

        self.status_attr = None
        self.web = WebContainer.get_web()
        self.icon_web_dir = self.web.get_icon_web_dir()
        

    def get_title(self):
        wdg = IconSubmitWdg(self.TRIGGER, icon=IconWdg.TABLE_UPDATE_ENTRY, long=True)
        wdg.set_text("Set Status")
        return wdg
       
    
    def get_prefs(self):
        from pyasm.flash.widget import FlashStatusViewFilter
        return FlashStatusViewFilter()
    
    def set_status_attr(self, status_attr):
        self.status_attr = status_attr


    def get_display(self):
        
        self.cb_name = self.generate_unique_id("status")
        # get the sobject and relevent parameters
        sobject = self.get_current_sobject()
      
        # start drawing
        div = HtmlElement.div()
        div.set_style("height: 100%;")

        is_simple = self.web.get_form_value("status_view_filter") == self.SIMPLE_VIEW
      
        div.add(self.get_status_table(sobject, is_simple))
        
        # if it is the last widget in the TableWdg
        if self.get_current_index() == len(self.sobjects) - 1:
            hidden_wdg = HiddenWdg(self.STATUS_CMD_INPUT, '|'.join(self.get_input()) )  
            div.add(hidden_wdg, name=self.STATUS_CMD_INPUT)
            
        return div
   
    def get_input(self):
        return Container.get("SerialStatusWdg:" + self.STATUS_CMD_INPUT)
        
    def store_input(self, value):
        hidden = self.get_input()
        if not hidden:
            Container.put("SerialStatusWdg:" + self.STATUS_CMD_INPUT, [value])
        else:
            hidden.append(value)
                 
        
    def get_status_table(self, sobject, is_simple=False):
       
        search_type = sobject.get_search_type()
        
        self.store_input(self.cb_name)
      
        # get the status attribute
        if self.status_attr == None:
            status_attr = sobject.get_attr(self.get_name())
        else:
            status_attr = self.status_attr
        
        #if isinstance(status_attr, StatusAttr2):
        #    raise Exception("Please convert to SimpleStatusAttr")
       
        # get the pipeline
        if not isinstance(status_attr, SimpleStatusAttr) and \
                not isinstance(status_attr, HierarchicalStatusAttr):
            return "No Pipeline Defined"
        else:
            pipeline = status_attr.get_pipeline()


        current = status_attr.get_current_process()

        # find the in_progress widget to determine the current status
        title = status_attr.get_web_display()
        
        table = Table()
        table.set_class("embed")

        # find the completion
        percent = status_attr.get_percent_completion()
        table.add_row_header("%s (%s%%)" % (title,percent))

        security = WebContainer.get_security()
        if not security.check_access("sobject|column", \
                "%s|%s" % (search_type,self.name), "edit"):
            return table
        
   
        # draw the different modes
        if is_simple:
            processes = pipeline.get_processes()
            index = 0
            for process in processes:
                # skip current process
                if process == current:
                    continue
                is_forward = pipeline.get_index(current.get_name()) > index
                self._draw_status_row(table, sobject, process, is_forward)
                index += 1
            return table    

        else:
            forwards = pipeline.get_forward_connects(current)
            for forward in forwards:
                self._draw_status_row(table, sobject, forward, is_forward=True)

            backwards = pipeline.get_backward_connects(current)
            for backward in backwards:
                self._draw_status_row(table, sobject, backward, is_forward=False)
                
            return table
    
   


    def _draw_status_row(self, table, sobject, process, is_forward):
        table.add_row()
    
        search_type = sobject.get_search_type()
        id = sobject.get_id()
        
        widget = Widget()

        if is_forward:
            widget.add( "<img src='%s/common/arrow_up.gif'>" % self.icon_web_dir )
        else:
            widget.add( "<img src='%s/common/arrow_down.gif'>" % self.icon_web_dir )
            
        checkbox = CheckboxWdg(self.cb_name)
        checkbox.set_id(self.generate_unique_id('cb'))
        value = "%s|%s|%s" % (search_type, id, process.get_name())
        checkbox.set_option("value", value)
        
        status_chk_event = self.generate_unique_id(self.STATUS_CHECK)
        checkbox.add_event_caller("onClick", status_chk_event)
        
        event = WebContainer.get_event_container()
        event.add_listener(status_chk_event, "a=get_elements('%s');\
            a.check_me('%s');" % (self.cb_name, checkbox.get_id()))
        
        table.add_cell(checkbox)

        widget.add(SpanWdg(process.get_name(),css='small'))
        td = table.add_click_cell(checkbox, data=widget, event_name=status_chk_event)
        td.add_class('nowrap')





class SerialStatusCmd(Command):

    def get_title(self):
        return SerialStatusWdg.TRIGGER


    def check(self):
        web = WebContainer.get_web()
        if web.get_form_value(SerialStatusWdg.TRIGGER) != "":
            return True

    def execute(self):

        web = WebContainer.get_web()
        
        # get the input names
        input_names = web.get_form_value(SerialStatusWdg.STATUS_CMD_INPUT).split('|')
        
        values = []
        for input_name in input_names:
            value = web.get_form_value(input_name)
            if value:
                values.append(web.get_form_value(input_name))
            
       
        # FIXME: HARDCODED Value for status column!!!!
        column = "status"

        for value in values:
            # get the sobject to be updated
            search_type,id,status = value.split("|")
            search = Search(search_type)
            search.add_id_filter(id)
            self.sobject = search.get_sobject()
            
            status_attr = self.sobject.get_attr(column)

            cur_status = status_attr.get_current_process()
            if cur_status == status:
                continue

            status_attr.set_status(status)
           
            update_column = 'time_update'
            if update_column in self.sobject.get_attr_names():
                self.sobject.set_value(update_column, Sql.get_timestamp_now(), quoted=False)
            self.sobject.commit()

           
            # if this is successful, the store it in the status_log
            status_log = SObjectFactory.create("sthpw/status_log")
            status_log.set_value("login", Environment.get_user_name() )
            status_log.set_value("search_type", search_type)
            status_log.set_value("search_id", id)
            #status_log.set_value("status", "%s to %s" % (cur_status, status) )
            status_log.commit()
            status_log.set_value("from_status", cur_status)
            status_log.set_value("to_status", status)

            # Call the finaled trigger
            Trigger.call(self, status)


class StatusUpdateAction(DatabaseAction):
    '''simple class to update the task dependencies'''

    def check(self):
        '''check for empty status, skips if found'''
        if not self.get_value():
            return False
        return True

    def execute(self):
        prev_value = self.sobject.get_value(self.get_name())

        super(StatusUpdateAction,self).execute()

        value = self.sobject.get_value(self.get_name())

        # record the change if it is different
        #if prev_value != value:
            # if this is successful, the store it in the status_log
            #StatusLog.create(self.sobject,value,prev_value)


