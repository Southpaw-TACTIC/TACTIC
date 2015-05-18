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

__all__ = ['workflow_init']

import tacticenv


from pyasm.command import Trigger, Command
from pyasm.search import SearchType, Search, SObject
from pyasm.biz import Pipeline, Task
from tactic.command import PythonCmd



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




class ProcessPendingTrigger(BaseProcessTrigger):

    def execute(my):
        # set all task to pending

        pipeline = my.input.get("pipeline")
        process = my.input.get("process")
        sobject = my.input.get("sobject")

        process_obj = pipeline.get_process(process)
        node_type = process_obj.get_type()

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
            if action or action_path:
                kwargs = {
                    'sobject': sobject,
                    'pipeline': pipeline,
                    'process': process
                }
                if action:
                    cmd = PythonCmd(code=action, **kwargs)
                else:
                    cmd = PythonCmd(script_path=script_path, **kwargs)
                ret_val = cmd.execute()

            Trigger.call(my, "process|complete", my.input)




            



    def handle_condition_node(my, sobject, pipeline, process, triggers):

        action = triggers.get("on_action")
        action_path = triggers.get("on_action_path")
        if action or action_path:
            kwargs = {
                'sobject': sobject,
                'pipeline': pipeline,
                'process': process
            }
            if action:
                cmd = PythonCmd(code=action, **kwargs)
            else:
                cmd = PythonCmd(script_path=script_path, **kwargs)
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





def workflow_init():

    event = "process|pending"
    trigger = SearchType.create("sthpw/trigger")
    trigger.set_value("event", event)
    trigger.set_value("class_name", ProcessPendingTrigger)
    trigger.set_value("mode", "same process,same transaction")
    Trigger.append_static_trigger(trigger)



    event = "process|complete"
    trigger = SearchType.create("sthpw/trigger")
    trigger.set_value("event", event)
    trigger.set_value("class_name", ProcessCompleteTrigger)
    trigger.set_value("mode", "same process,same transaction")
    Trigger.append_static_trigger(trigger)

    event = "process|action"
    trigger = SearchType.create("sthpw/trigger")
    trigger.set_value("event", event)
    trigger.set_value("class_name", ProcessActionTrigger)
    trigger.set_value("mode", "same process,same transaction")
    Trigger.append_static_trigger(trigger)


    event = "process|revise"
    trigger = SearchType.create("sthpw/trigger")
    trigger.set_value("event", event)
    trigger.set_value("class_name", ProcessReviseTrigger)
    trigger.set_value("mode", "same process,same transaction")
    Trigger.append_static_trigger(trigger)






