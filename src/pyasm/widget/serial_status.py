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

    def init(my):
        my.post_ajax_script = None

    def preprocess(my):
        my.post_ajax_script = None

    def set_post_ajax_script(my, script):
        my.post_ajax_script = script


    def get_display(my):

        sobject = my.get_current_sobject()
        search_key = sobject.get_search_key()
        value = sobject.get_value(my.name)
        my.select = ActionSelectWdg("status_%s" % search_key)

        empty = my.get_option("empty")
        if empty:
            my.select.set_option("empty", empty )

        pipeline_code = my.get_option("pipeline")

        widget = Widget()
        my.select.set_id("status_%s" % search_key)

        setting = my.get_option("setting")
        if setting:
            my.select.set_option("setting", setting )
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

            my.select.set_option("values", "|".join(allowed_processes) )

            if not value and processes:
                value = processes[0]

            # add the item if it is an obsolete status, alert
            # the user to change to the newly-defined statuses
            if value not in processes:
                my.select.append_option(value, value)
                my.select.set_class('action_warning')

        my.select.set_value( value )

        # TODO: this is a little cumbersome to know all this simply to
        # execute a command using ajax
        """ 
        div_id = widget.generate_unique_id('simple_status_wdg')
        cmd = AjaxLoader(div_id)
        marshaller = cmd.register_cmd("SimpleStatusCmd")
        marshaller.set_option('search_key', search_key)
        marshaller.set_option('attr_name',  my.name)
    
        my.select.add_event("onchange", cmd.get_on_script(True) )
        """

        js_action = "TacticServerCmd.execute_cmd('pyasm.widget.SimpleStatusCmd', '',\
                {'search_key': '%s', 'attr_name': '%s'}, {'value': bvr.src_el.value});" %(search_key, my.name)

        # build the search key
        #search_key = "%s|%s" % (my.search_type, my.search_id)
        
        bvr = {'type': 'change', 'cbjs_action': js_action}
        if my.post_ajax_script:
            bvr['cbjs_postaction'] = my.post_ajax_script

        my.select.add_behavior(bvr)
        div = DivWdg(my.select)
        div.add_style('float: left')
        widget.add(div)
       
        return widget

   

        

class SimpleStatusCmd(Command):
    
    def __init__(my, **kwargs):
        super(SimpleStatusCmd,my).__init__(**kwargs)
        my.search_key = my.kwargs.get('search_key')
        my.attr_name = my.kwargs.get('attr_name')
        my.users = []
        my.sobject = None

    def get_title(my):
        return "SimpleStatusCmd"

    def set_search_key(my, search_key):
        my.search_key = search_key

    def set_attr_name(my, attr_name):
        my.attr_name = attr_name

    def check(my):
        return True


    def execute(my):

        web = WebContainer.get_web()
        value = web.get_form_value('value')
        if my.search_key == None or value == None or my.attr_name == None:
            raise CommandExitException()


        sobject = Search.get_by_search_key(my.search_key)
        old_value = sobject.get_value(my.attr_name)
        sobject.set_value(my.attr_name, value)
        sobject.commit()

        # setting target attributes if sobject is a task
        if sobject.get_search_type_obj().get_base_key() == Task.SEARCH_TYPE:
            task = sobject

            # FIXME: not sure what this if for???
            my.users = [task.get_value("assigned")]

            process_name = task.get_value('process')


            task_description = task.get_value("description")

            my.parent = task.get_parent()
            # it should be task, notification will get the parent in the 
            # email trigger logic
            my.sobject = task
            code = my.parent.get_code()
            name = my.parent.get_name()
            my.info['parent_centric'] = True
            my.description = "%s set to '%s' for %s (%s), task: %s, %s" % (\
                my.attr_name.capitalize(), value, code, name, process_name, task_description)


            # set the states of the command
            pipeline = Pipeline.get_by_sobject(my.parent)
            process = pipeline.get_process(process_name)
            completion = task.get_completion()

            if pipeline and process:
                my.set_process(process_name)
                my.set_pipeline_code( pipeline.get_code() )
                if completion == 100:
                    my.set_event_name("task/approved")
                else:
                    my.set_event_name("task/change")
                    


        else:
            my.sobject = sobject
            code = my.sobject.get_code()

            my.description = "%s set to '%s' for %s" % (\
                my.attr_name.capitalize(), value, code)

            process_name = "None"
            my.info['parent_centric'] = False

        my.sobjects.append(my.sobject)
       
        # set the information about this command
        my.info['to'] = value
        my.info['process'] = process_name
        

       
        # if this is successful, the store it in the status_log
        #StatusLog.create(sobject,value,old_value)


   
    def get_info_keys(my):
        return ['to', 'process']


class SerialStatusWdg(BaseTableElementWdg):
    '''widget for serial approval process.  only 1 process can
    be "in_progress" at a time'''
    CONNECTION_VIEW = 'connection'
    SIMPLE_VIEW = 'simple'
    STATUS_CHECK = 'status_check'
    STATUS_CMD_INPUT = 'serial_status_input'
    TRIGGER = 'set_status'

    def init(my):
        WebContainer.register_cmd("pyasm.widget.SerialStatusCmd")

        my.status_attr = None
        my.web = WebContainer.get_web()
        my.icon_web_dir = my.web.get_icon_web_dir()
        

    def get_title(my):
        wdg = IconSubmitWdg(my.TRIGGER, icon=IconWdg.TABLE_UPDATE_ENTRY, long=True)
        wdg.set_text("Set Status")
        return wdg
       
    
    def get_prefs(my):
        from pyasm.flash.widget import FlashStatusViewFilter
        return FlashStatusViewFilter()
    
    def set_status_attr(my, status_attr):
        my.status_attr = status_attr


    def get_display(my):
        
        my.cb_name = my.generate_unique_id("status")
        # get the sobject and relevent parameters
        sobject = my.get_current_sobject()
      
        # start drawing
        div = HtmlElement.div()
        div.set_style("height: 100%;")

        is_simple = my.web.get_form_value("status_view_filter") == my.SIMPLE_VIEW
      
        div.add(my.get_status_table(sobject, is_simple))
        
        # if it is the last widget in the TableWdg
        if my.get_current_index() == len(my.sobjects) - 1:
            hidden_wdg = HiddenWdg(my.STATUS_CMD_INPUT, '|'.join(my.get_input()) )  
            div.add(hidden_wdg, name=my.STATUS_CMD_INPUT)
            
        return div
   
    def get_input(my):
        return Container.get("SerialStatusWdg:" + my.STATUS_CMD_INPUT)
        
    def store_input(my, value):
        hidden = my.get_input()
        if not hidden:
            Container.put("SerialStatusWdg:" + my.STATUS_CMD_INPUT, [value])
        else:
            hidden.append(value)
                 
        
    def get_status_table(my, sobject, is_simple=False):
       
        search_type = sobject.get_search_type()
        
        my.store_input(my.cb_name)
      
        # get the status attribute
        if my.status_attr == None:
            status_attr = sobject.get_attr(my.get_name())
        else:
            status_attr = my.status_attr
        
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
                "%s|%s" % (search_type,my.name), "edit"):
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
                my._draw_status_row(table, sobject, process, is_forward)
                index += 1
            return table    

        else:
            forwards = pipeline.get_forward_connects(current)
            for forward in forwards:
                my._draw_status_row(table, sobject, forward, is_forward=True)

            backwards = pipeline.get_backward_connects(current)
            for backward in backwards:
                my._draw_status_row(table, sobject, backward, is_forward=False)
                
            return table
    
   


    def _draw_status_row(my, table, sobject, process, is_forward):
        table.add_row()
    
        search_type = sobject.get_search_type()
        id = sobject.get_id()
        
        widget = Widget()

        if is_forward:
            widget.add( "<img src='%s/common/arrow_up.gif'>" % my.icon_web_dir )
        else:
            widget.add( "<img src='%s/common/arrow_down.gif'>" % my.icon_web_dir )
            
        checkbox = CheckboxWdg(my.cb_name)
        checkbox.set_id(my.generate_unique_id('cb'))
        value = "%s|%s|%s" % (search_type, id, process.get_name())
        checkbox.set_option("value", value)
        
        status_chk_event = my.generate_unique_id(my.STATUS_CHECK)
        checkbox.add_event_caller("onClick", status_chk_event)
        
        event = WebContainer.get_event_container()
        event.add_listener(status_chk_event, "a=get_elements('%s');\
            a.check_me('%s');" % (my.cb_name, checkbox.get_id()))
        
        table.add_cell(checkbox)

        widget.add(SpanWdg(process.get_name(),css='small'))
        td = table.add_click_cell(checkbox, data=widget, event_name=status_chk_event)
        td.add_class('nowrap')





class SerialStatusCmd(Command):

    def get_title(my):
        return SerialStatusWdg.TRIGGER


    def check(my):
        web = WebContainer.get_web()
        if web.get_form_value(SerialStatusWdg.TRIGGER) != "":
            return True

    def execute(my):

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
            my.sobject = search.get_sobject()
            
            status_attr = my.sobject.get_attr(column)

            cur_status = status_attr.get_current_process()
            if cur_status == status:
                continue

            status_attr.set_status(status)
           
            update_column = 'time_update'
            if update_column in my.sobject.get_attr_names():
                my.sobject.set_value(update_column, Sql.get_timestamp_now(), quoted=False)
            my.sobject.commit()

           
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
            Trigger.call(my, status)


class StatusUpdateAction(DatabaseAction):
    '''simple class to update the task dependencies'''

    def check(my):
        '''check for empty status, skips if found'''
        if not my.get_value():
            return False
        return True

    def execute(my):
        prev_value = my.sobject.get_value(my.get_name())

        super(StatusUpdateAction,my).execute()

        value = my.sobject.get_value(my.get_name())

        # record the change if it is different
        #if prev_value != value:
            # if this is successful, the store it in the status_log
            #StatusLog.create(my.sobject,value,prev_value)


