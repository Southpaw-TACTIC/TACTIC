###########################################################
#
# Copyright (c) 2015, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#

__all__ = ['Workflow']

import tacticenv


from pyasm.command import Trigger, Command
from pyasm.search import SearchType, Search, SObject
from pyasm.biz import Pipeline, Task
from tactic.command import PythonCmd


class Workflow(object):

    def init(my):
        # initialize the triggers for the workflow

        event = "process|pending"
        trigger = SearchType.create("sthpw/trigger")
        trigger.set_value("event", event)
        trigger.set_value("class_name", ProcessPendingTrigger)
        trigger.set_value("mode", "same process,same transaction")
        Trigger.append_static_trigger(trigger)

        event = "process|action"
        trigger = SearchType.create("sthpw/trigger")
        trigger.set_value("event", event)
        trigger.set_value("class_name", ProcessActionTrigger)
        trigger.set_value("mode", "same process,same transaction")
        Trigger.append_static_trigger(trigger)


        event = "process|complete"
        trigger = SearchType.create("sthpw/trigger")
        trigger.set_value("event", event)
        trigger.set_value("class_name", ProcessCompleteTrigger)
        trigger.set_value("mode", "same process,same transaction")
        Trigger.append_static_trigger(trigger)

        event = "process|revise"
        trigger = SearchType.create("sthpw/trigger")
        trigger.set_value("event", event)
        trigger.set_value("class_name", ProcessReviseTrigger)
        trigger.set_value("mode", "same process,same transaction")
        Trigger.append_static_trigger(trigger)

        event = "process|error"
        trigger = SearchType.create("sthpw/trigger")
        trigger.set_value("event", event)
        trigger.set_value("class_name", ProcessErrorTrigger)
        trigger.set_value("mode", "same process,same transaction")
        Trigger.append_static_trigger(trigger)

        # by default a stataus change to a trigger calls the node's trigger
        event = "change|sthpw/task|status"
        trigger = SearchType.create("sthpw/trigger")
        trigger.set_value("event", event)
        trigger.set_value("class_name", TaskStatusChangeTrigger)
        trigger.set_value("mode", "same process,same transaction")
        Trigger.append_static_trigger(trigger)



class TaskStatusChangeTrigger(Trigger):

    def execute(my):

        # find the node in the pipeline
        task = my.get_caller()
        sobject = task.get_parent()
        if not sobject:
            return

        pipeline = Pipeline.get_by_sobject(sobject)
        if not pipeline:
            return

        process_name = task.get_value("process")
        status = task.get_value("status")

        process = pipeline.get_process(process_name)
        node_type = process.get_type()
        process_name = process.get_name()

        event = "process|%s" % status.lower()
        print "event: ", event
        output = {
            'sobject': sobject,
            'pipeline': pipeline,
            'process': process,
        }
        Trigger.call(task, event, output=output)

        




#
# Built in process triggers
#


class BaseProcessTrigger(Trigger):


    def set_all_tasks(my, sobject, process, status):
        tasks = Task.get_by_sobject(sobject, process=process)
        for task in tasks:
            task.set_value("status", status)
            task.commit()
 

    def run_callback(my, process, key):
        # get the node triggers
        search = Search("config/process")        
        search.add_filter("process", process)
        process_sobj = search.get_sobject()
        triggers = {}
        if process_sobj:
            triggers = process_sobj.get_json_value("trigger")
        if not triggers:
            triggers = {}

        ret_val = {}

        action = triggers.get(key)
        action_path = triggers.get("%s_path" % key)
        if action or action_path:
            kwargs = my.input
            if action:
                cmd = PythonCmd(code=action, **kwargs)
            else:
                cmd = PythonCmd(script_path=script_path, **kwargs)
            ret_val = cmd.execute()

        return ret_val



    def build_trigger_input(my):
        # create a package for the trigger

        pipeline = my.input.get("pipeline")
        process = my.input.get("process")
        sobject = my.input.get("sobject")



        kwargs = {
            'sobject': sobject,
            'pipreine': pipeline,
            'process': process
        }
        input = {
            'sobject': sobject.get_sobject_dict(),
            'pipeline': pipeline.to_string(),
            'process': process,
            'inputs': [x.get_name() for x in pipeline.get_input_processes(process)],
            'outputs': [x.get_name() for x in pipeline.get_output_processes(process)],
        }
        return kwargs, input



class ProcessPendingTrigger(BaseProcessTrigger):

    def execute(my):
        # set all task to pending

        pipeline = my.input.get("pipeline")
        process = my.input.get("process")
        sobject = my.input.get("sobject")

        process_obj = pipeline.get_process(process)
        node_type = process_obj.get_type()

        my.run_callback(process, "on_pending")

        if node_type == None or node_type != "manual":
            my.set_all_tasks(sobject, process, "pending")

        if node_type in ["auto", "condition"]:
            Trigger.call(my, "process|action", output=my.input)


 

class ProcessActionTrigger(BaseProcessTrigger):

    def execute(my):

        # get the pipeline
        pipeline = my.input.get("pipeline")
        process = my.input.get("process")
        sobject = my.input.get("sobject")

        my.set_all_tasks(sobject, process, "in_progress")


        # get the node's triggers
        search = Search("config/process")        
        search.add_filter("process", process)
        process_sobj = search.get_sobject()
        triggers = {}
        if process_sobj:
            triggers = process_sobj.get_json_value("trigger")
        if not triggers:
            triggers = {}




        process_obj = pipeline.get_process(process)
        node_type = process_obj.get_type()

        if node_type == "condition":
            my.handle_condition_node(sobject, pipeline, process, triggers)

        elif node_type == "approval":
            my.handle_condition_node(sobject, pipeline, process, triggers)

        elif node_type == "auto":

            action = triggers.get("action")
            action_path = triggers.get("action_path")
            kwargs, input = my.build_trigger_input()
            if action or action_path:
                if action:
                    cmd = PythonCmd(code=action, input=input, **kwargs)
                else:
                    cmd = PythonCmd(script_path=script_path, input=input, **kwargs)
                ret_val = cmd.execute()
            else:
                # or call a trigger
                print "input: ", my.input
                Trigger.call(my, "process|action", input, process=process_sobj.get_code())

            Trigger.call(my, "process|complete", my.input)




            



    def handle_condition_node(my, sobject, pipeline, process, triggers):

        action = triggers.get("on_action")
        action_path = triggers.get("on_action_path")
        if action or action_path:
            kwargs, input = my.build_trigger_input()
            if action:
                cmd = PythonCmd(code=action, input=input, **kwargs)
            else:
                cmd = PythonCmd(script_path=script_path, input=input, **kwargs)
            ret_val = cmd.execute()

        else:
            ret_val = True

        # run the completion trigger for this node
        Trigger.call(my, "process|complete", my.input)


        if ret_val == True:
            success_cbk = triggers.get("on_success")
            if success_cbk:
                cmd = PythonCmd(code=success_cbk, sobject=sobject)
                cmd.execute()
                return
            else:
                event = "process|complete"
                direction = "output"
                attr = "success"

        elif ret_val == False:
            fail_cbk = triggers.get("on_fail")
            if fail_cbk:
                cmd = PythonCmd(code=fail_cbk, sobject=sobject)
                cmd.execute()
                return
            else:
                event = "process|revise"
                direction = "output"
                attr = "fail"

        else:
            event = "process|pending"
            if isinstance(ret_val, basestring): 
                # for now, we just support a single ret value
                ret_val = [ret_val]

            for attr in ret_val: 
                output_processes = pipeline.get_output_processes(process, from_attr=attr)

                for output_process in output_processes:
                    output_process_name = output_process.get_name()
                    output = {
                        'sobject': sobject,
                        'pipeline': pipeline,
                        'process': output_process_name,
                    }
                    Trigger.call(my, event, output)

            return


        # by default, go back to incoming or outcoming
        if direction == "input":
            processes = pipeline.get_input_processes(process, to_attr=attr)
        else:
            processes = pipeline.get_output_processes(process, from_attr=attr)


        # or use connection attrs
        #processes = pipeline.get_output_processes(process, attr="success")
        #processes = pipeline.get_input_processes(process, attr="fail")



        for process in processes:
            process_name = process.get_name()
            output = {
                'sobject': sobject,
                'pipeline': pipeline,
                'process': process_name,
            }
            Trigger.call(my, event, output)





class ProcessCompleteTrigger(BaseProcessTrigger):

    def execute(my):

        process = my.input.get("process")
        sobject = my.input.get("sobject")
        pipeline = my.input.get("pipeline")

        # run a nodes complete trigger
        #event = "process|complete|%s" % process
        #Trigger.call(my, event, output=my.input)
        my.run_callback(process, "on_complete")

        process_obj = pipeline.get_process(process)
        node_type = process_obj.get_type()

        if node_type in ["auto"]:
            # call the process|pending event for all output processes
            output_processes = pipeline.get_output_processes(process)
            for output_process in output_processes:
                output_process = output_process.get_name()

                output = {
                    'pipeline': pipeline,
                    'sobject': sobject,
                    'process': output_process
                }

                event = "process|pending"
                Trigger.call(my, event, output)



class ProcessReviseTrigger(BaseProcessTrigger):

    def execute(my):
        process = my.input.get("process")
        my.run_callback(process, "on_revise")



class ProcessErrorTrigger(BaseProcessTrigger):

    def execute(my):
        process = my.input.get("process")
        sobject = my.input.get("sobject")
        pipeline = my.input.get("pipeline")
 
        print "Error: Failed to process [%s] on sobject [%s]" % (process, sobject.get_search_key() )

        # TODO: send a message so that those following this sobject will be notified






