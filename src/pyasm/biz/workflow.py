##########################################################
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

__all__ = ['Workflow', 'BaseProcessTrigger']

import tacticenv

from pyasm.common import Common, Config
from pyasm.command import Trigger, Command
from pyasm.search import SearchType, Search, SObject

from pipeline import Pipeline
from task import Task

class Workflow(object):

    def init(my, startup=False):

        #workflow = Config.get_value("services", "workflow")
        #if workflow not in [True, 'true']:
        #    return

        print "Starting Workflow Engine"

        # initialize the triggers for the workflow
        event = "process|pending"
        trigger = SearchType.create("sthpw/trigger")
        trigger.set_value("event", event)
        trigger.set_value("class_name", ProcessPendingTrigger)
        trigger.set_value("mode", "same process,same transaction")
        Trigger.append_static_trigger(trigger, startup=startup)

        event = "process|action"
        trigger = SearchType.create("sthpw/trigger")
        trigger.set_value("event", event)
        trigger.set_value("class_name", ProcessActionTrigger)
        trigger.set_value("mode", "same process,same transaction")
        Trigger.append_static_trigger(trigger, startup=startup)


        event = "process|complete"
        trigger = SearchType.create("sthpw/trigger")
        trigger.set_value("event", event)
        trigger.set_value("class_name", ProcessCompleteTrigger)
        trigger.set_value("mode", "same process,same transaction")
        Trigger.append_static_trigger(trigger, startup=startup)

        event = "process|approved"
        trigger = SearchType.create("sthpw/trigger")
        trigger.set_value("event", event)
        trigger.set_value("class_name", ProcessApproveTrigger)
        trigger.set_value("mode", "same process,same transaction")
        Trigger.append_static_trigger(trigger, startup=startup)


        event = "process|reject"
        trigger = SearchType.create("sthpw/trigger")
        trigger.set_value("event", event)
        trigger.set_value("class_name", ProcessRejectTrigger)
        trigger.set_value("mode", "same process,same transaction")
        Trigger.append_static_trigger(trigger, startup=startup)



        event = "process|revise"
        trigger = SearchType.create("sthpw/trigger")
        trigger.set_value("event", event)
        trigger.set_value("class_name", ProcessReviseTrigger)
        trigger.set_value("mode", "same process,same transaction")
        Trigger.append_static_trigger(trigger, startup=startup)

        event = "process|error"
        trigger = SearchType.create("sthpw/trigger")
        trigger.set_value("event", event)
        trigger.set_value("class_name", ProcessErrorTrigger)
        trigger.set_value("mode", "same process,same transaction")
        Trigger.append_static_trigger(trigger, startup=startup)

        # by default a stataus change to a trigger calls the node's trigger
        event = "change|sthpw/task|status"
        trigger = SearchType.create("sthpw/trigger")
        trigger.set_value("event", event)
        trigger.set_value("class_name", TaskStatusChangeTrigger)
        trigger.set_value("mode", "same process,same transaction")
        Trigger.append_static_trigger(trigger, startup=startup)



class TaskStatusChangeTrigger(Trigger):

    def execute(my):

        """
        key = "enable_workflow_engine"
        from prod_setting import ProdSetting
        setting = ProdSetting.get_value_by_key(key)
        if setting not in [True, 'true']:
            return
        """


        # find the node in the pipeline
        task = my.get_caller()
        sobject = task.get_parent()
        if not sobject:
            return

        pipeline = None

        process_code = task.get_value("process_code", no_exception=True)
        if process_code:
            process_sobj = Search.get_by_code("config/process", process_code)
            if process_sobj:
                pipeline_code = process_sobj.get_value("pipeline_code")
                pipeline = Pipeline.get_by_code("sthpw/pipeline", pipeline_code) 

        if not pipeline:
            pipeline = Pipeline.get_by_sobject(sobject)



        if not pipeline:
            return

        process_name = task.get_value("process")
        status = task.get_value("status")

        # handle the approve case (which really means complete)
        if status.lower() == "approved":
            status = "complete"

        process = pipeline.get_process(process_name)
        if not process:
            # we don't have enough info here
            return

        node_type = process.get_type()
        process_name = process.get_name()

        event = "process|%s" % status.lower()
        output = {
            'sobject': sobject,
            'pipeline': pipeline,
            'process': process_name,
        }
        Trigger.call(task, event, output=output)





#
# Built in process triggers
#


class BaseProcessTrigger(Trigger):


    def set_all_tasks(my, sobject, process, status):
        tasks = Task.get_by_sobject(sobject, process=process)
        title = status.replace("-", " ")
        title = title.replace("_", " ")
        title = Common.get_display_title(title)
        for task in tasks:
            task.set_value("status", title)
            task.commit()
 

    def run_callback(my, pipeline, process, status):

        # get the node triggers
        # TODO: make this more efficient
        search = Search("config/process")        
        search.add_filter("pipeline_code", pipeline.get_code())
        search.add_filter("process", process)
        process_sobj = search.get_sobject()

        #print "callback process: ", process, pipeline.get_code()
        assert(process_sobj)


        triggers = {}
        if process_sobj:
            triggers = process_sobj.get_json_value("workflow")
        if not triggers:
            triggers = {}

        ret_val = None

        action = triggers.get("on_%s" % status)
        js_action = triggers.get("cbjs_%s" % status)
        action_path = triggers.get("on_%s_path" % status)

        kwargs, input = my.build_trigger_input()
        if action or action_path:
            from tactic.command import PythonCmd
            if action:
                cmd = PythonCmd(code=action, input=input, **kwargs)
            else:
                cmd = PythonCmd(script_path=script_path, input=input, **kwargs)

            ret_val = cmd.execute()

        elif js_action:
            from tactic.command import JsCmd
            if action:
                cmd = JsCmd(code=action, input=input, **kwargs)
            else:
                cmd = JsCmd(script_path=script_path, input=input, **kwargs)

            ret_val = cmd.execute()
        else:
            # or call a trigger
            event = "process|%s" % status

            # how to get the value here?
            process_code = process_sobj.get_code()
            triggers = Trigger.call(my, event, kwargs, process=process_code)
            if triggers:
                ret_val = triggers[0].get_ret_val()

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




class BaseWorkflowNodeHandler(BaseProcessTrigger):

    def __init__(my, **kwargs):
        super(BaseWorkflowNodeHandler, my).__init__(**kwargs)
        my.input = kwargs.get("input")

        # create a package for the trigger
        my.pipeline = my.input.get("pipeline")
        my.process = my.input.get("process")
        my.sobject = my.input.get("sobject")

        if my.process.find(".") != -1:
            parts = my.process.split(".")
            my.process = parts[-1]
            my.process_parts = parts[:-1]
        else:
            my.process_parts = []






    def handle_pending(my):
        # simply calls action
        my.set_all_tasks(my.sobject, my.process, "pending")
        my.run_callback(my.pipeline, my.process, "pending")
        Trigger.call(my, "process|action", output=my.input)


    def handle_action(my):
        my.set_all_tasks(my.sobject, my.process, "in_progress")
        my.run_callback(my.pipeline, my.process, "action")
        Trigger.call(my, "process|complete", output=my.input)


    def handle_complete(my):
 
        # run a nodes complete trigger
        status = "complete"
        my.run_callback(my.pipeline, my.process, status)

        process_obj = my.pipeline.get_process(my.process)

        # call the process|pending event for all output processes
        output_processes = my.pipeline.get_output_processes(my.process)
        for output_process in output_processes:
            output_process = output_process.get_name()

            if my.process_parts:
                output_process = "%s.%s" % (my.process_parts[0], output_process)

            output = {
                'pipeline': my.pipeline,
                'sobject': my.sobject,
                'process': output_process
            }

            event = "process|pending"
            Trigger.call(my, event, output)


    def handle_reject(my):

        process_obj = pipeline.get_process(my.process)

        my.run_callback(my.pipeline, my.process, "revise")

        # set all tasks in the process to revise
        my.set_all_tasks(my.sobject, my.process, "revise")


        # send revise single to previous processes
        input_processes = pipeline.get_input_processes(my.process)
        for input_process in input_processes:
            input_process = input_process.get_name()

            if my.process_parts:
                input_process = "%s.%s" % (my.process_parts[0], input_process)


            input = {
                'pipeline': my.pipeline,
                'sobject': my.sobject,
                'process': input_process
            }

            event = "process|revise"
            Trigger.call(my, event, input)



    def handle_revise(my):

        process_obj = pipeline.get_process(my.process)

        my.run_callback(my.pipeline, my.process, "revise")

        # set all tasks in the process to review
        my.set_all_tasks(my.sobject, my.process, "review")


        # send revise single to previous processes
        input_processes = pipeline.get_input_processes(my.process)
        for input_process in input_processes:
            input_process = input_process.get_name()

            if my.process_parts:
                input_process = "%s.%s" % (my.process_parts[0], input_process)


            input = {
                'pipeline': my.pipeline,
                'sobject': my.sobject,
                'process': input_process
            }

            event = "process|revise"
            Trigger.call(my, event, input)



class WorkflowManualNodeHandler(BaseWorkflowNodeHandler):

    def handle_action(my):
        # does nothing
        pass



class WorkflowActionNodeHandler(BaseWorkflowNodeHandler):

    def handle_action(my):

        process_obj = my.pipeline.get_process(my.process)

        # get the node's triggers
        search = Search("config/process")        
        search.add_filter("process", my.process)
        process_sobj = search.get_sobject()
        triggers = {}
        if process_sobj:
            triggers = process_sobj.get_json_value("workflow")
        if not triggers:
            triggers = {}

        action = triggers.get("on_action")
        cbjs_action = triggers.get("cbjs_action")
        action_path = triggers.get("on_action_path")
        kwargs, input = my.build_trigger_input()
        if action or action_path:
            if action:
                cmd = PythonCmd(code=action, input=input, **kwargs)
            else:
                cmd = PythonCmd(script_path=action_path, input=input, **kwargs)

            ret_val = cmd.execute()

        elif cbjs_action:
            from tactic.command import JsCmd
            if cbjs_action:
                cmd = JsCmd(code=cbjs_action, input=input, **kwargs)
            else:
                cmd = JsCmd(script_path=script_path, input=input, **kwargs)

            ret_val = cmd.execute()
        else:
            # or call an action trigger
            Trigger.call(my, "process|action", input, process=process_sobj.get_code())

        Trigger.call(my, "process|complete", my.input)



class WorkflowApprovalNodeHandler(BaseWorkflowNodeHandler):

    def handle_pending(my):

        # check to see if the tasks exist and if they don't then create one
        tasks = Task.get_by_sobject(my.sobject, process=my.process)
        if not tasks:
            tasks = Task.add_initial_tasks(my.sobject, processes=[my.process])
        else:
            my.set_all_tasks(my.sobject, my.process, "pending")


        Trigger.call(my, "process|action", my.input)


    def handle_action(my):
        # does nothing
        pass



class WorkflowHierarchyNodeHandler(BaseWorkflowNodeHandler):

    def handle_pending(my):
        search = Search("config/process")
        search.add_filter("pipeline_code", my.pipeline.get_code())
        search.add_filter("process", my.process)
        process_sobj = search.get_sobject()
        process_code = process_sobj.get_code()



        # use child process
        subpipeline_code = process_sobj.get_value("subpipeline_code")
        if subpipeline_code:
            subpipeline = Search.get_by_code("sthpw/pipeline", subpipeline_code)
        else:
            search = Search("sthpw/pipeline")
            search.add_filter("parent_process", process_code)
            subpipeline = search.get_sobject()

        if not subpipeline:
            return


        # get the input nodes
        child_processes = subpipeline.get_processes(type=['input'])

        if not child_processes:
            child_processes = subpipeline.get_processes()

        if child_processes:
            first_process = child_processes[0]
            first_name = first_process.get_name()

            full_name = "%s.%s" % (my.process, first_name)

            input = {
                    'pipeline': subpipeline,
                    'sobject': my.sobject,
                    'process': full_name,
            }

            event = "process|pending"
            Trigger.call(my, event, input)


class WorkflowInputNodeHandler(BaseWorkflowNodeHandler):
    def handle_pending(my):
        # fast track to complete
        Trigger.call(my, "process|complete", output=my.input)


class WorkflowOutputNodeHandler(BaseWorkflowNodeHandler):

    def handle_pending(my):
        # fast track to complete
        Trigger.call(my, "process|complete", output=my.input)


    def handle_complete(my):
        my.run_callback(my.pipeline, my.process, "complete")


        search = Search("config/process")        
        search.add_filter("subpipeline_code", my.pipeline.get_code())
        if my.process_parts:
            search.add_filter("process", my.process_parts[0])
        supprocess_sobj = search.get_sobject()
        suppipeline_code = supprocess_sobj.get_value("pipeline_code")
        supprocess = supprocess_sobj.get_value("process")

        suppipeline = Search.get_by_code("sthpw/pipeline", suppipeline_code)
        output = {
            'pipeline': suppipeline,
            'sobject': my.sobject,
            'process': supprocess
        }

        event = "process|complete"
        Trigger.call(my, event, output)




class WorkflowConditionNodeHandler(BaseWorkflowNodeHandler):

    def handle_pending(my):
        # fast track to complete - no tasks
        Trigger.call(my, "process|action", output=my.input)


    def handle_action(my):
        # get the node's triggers
        search = Search("config/process")        
        search.add_filter("process", my.process)
        process_sobj = search.get_sobject()
        triggers = {}
        if process_sobj:
            triggers = process_sobj.get_json_value("workflow")
        if not triggers:
            triggers = {}

        return my.handle_condition_node(my.sobject, my.pipeline, my.process, triggers)




    def handle_condition_node(my, sobject, pipeline, process, triggers):

        ret_val = my.run_callback(pipeline, process, "action")

        # if a None return value was given, then probably no condition exists
        # yet, so just let if flow through
        if ret_val == None:
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
                event = "process|pending"
                attr = "success"
                direction = "output"
                processes = pipeline.get_output_processes(process, from_attr=attr)
                if not processes:
                    attr = None

        elif ret_val == False:

            fail_cbk = triggers.get("on_fail")
            if fail_cbk:
                cmd = PythonCmd(code=fail_cbk, sobject=sobject)
                cmd.execute()
                return
            else:
                event = "process|revise"

                # check to see if there is an output process
                attr = "fail"
                processes = pipeline.get_output_processes(process, from_attr=attr)
                if processes:
                    direction = "output"
                else:
                    direction = "input"
                    attr = None

        else:
            event = "process|pending"
            if isinstance(ret_val, basestring): 
                ret_val = [ret_val]

            output_processes = []
            for attr in ret_val: 
                outputs = pipeline.get_output_processes(process, from_attr=attr)
                if outputs:
                    output_processes.extend(outputs)

            # if there are no output attrs, then check the node names
            if not output_processes:
                outputs = pipeline.get_output_processes(process)
                for output in outputs:
                    if output.get_name() in ret_val:
                        output_processes.append(output)

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


        for process in processes:
            process_name = process.get_name()
            output = {
                'sobject': sobject,
                'pipeline': pipeline,
                'process': process_name,
            }
            Trigger.call(my, event, output)



    def handle_complete(my):
        # run a nodes complete trigger
        my.run_callback(my.pipeline, my.process, "complete")

        my.set_all_tasks(my.sobject, my.process, "complete")


###---------------------------------



class ProcessPendingTrigger(BaseProcessTrigger):

    def execute(my):
        # set all task to pending

        pipeline = my.input.get("pipeline")
        process = my.input.get("process")
        sobject = my.input.get("sobject")

        if process.find(".") != -1:
            parts = process.split(".")
            process = parts[-1]

        process_obj = pipeline.get_process(process)
        node_type = process_obj.get_type()

        if node_type == "action":
            handler = WorkflowActionNodeHandler(input=my.input)
            return handler.handle_pending()
        elif node_type == "approval":
            handler = WorkflowApprovalNodeHandler(input=my.input)
            return handler.handle_pending()
        elif node_type in ["manual", "node"]:
            handler = WorkflowManualNodeHandler(input=my.input)
            return handler.handle_pending()
        elif node_type == "hierarchy":
            handler = WorkflowHierarchyNodeHandler(input=my.input)
            return handler.handle_pending()
        elif node_type == "input":
            handler = WorkflowOutputNodeHandler(input=my.input)
            return handler.handle_pending()
        elif node_type == "output":
            handler = WorkflowOutputNodeHandler(input=my.input)
            return handler.handle_pending()
        elif node_type == "condition":
            handler = WorkflowConditionNodeHandler(input=my.input)
            return handler.handle_pending()


        # Make sure the below is completely deprecated
        assert(False)


        my.run_callback(pipeline, process, "pending")

        # NOTE: should these set the value if already complete?
        #if node_type not in ["nodeX", "manualX"]:
        #    my.set_all_tasks(sobject, process, "pending")


        if node_type in ["action", "condition"]:
            Trigger.call(my, "process|action", output=my.input)

        elif node_type in ["node", "manual"]:
            # do nothing
            pass

        elif node_type in ["approval"]:

            # check to see if the tasks exist and if they don't then create one
            tasks = Task.get_by_sobject(sobject, process=process)
            if not tasks:
                tasks = Task.add_initial_tasks(sobject, processes=[process])
            else:
                my.set_all_tasks(sobject, process, "pending")


        elif node_type in ["hierarchy"]:

            search = Search("config/process")
            search.add_filter("pipeline_code", pipeline.get_code())
            search.add_filter("process", process)
            process_sobj = search.get_sobject()
            process_code = process_sobj.get_code()



            # use child process
            subpipeline_code = process_sobj.get_value("subpipeline_code")
            if subpipeline_code:
                subpipeline = Search.get_by_code("sthpw/pipeline", subpipeline_code)
            else:
                search = Search("sthpw/pipeline")
                search.add_filter("parent_process", process_code)
                subpipeline = search.get_sobject()

            if not subpipeline:
                return


            # TODO: find the inputs
            child_processes = subpipeline.get_processes()
            if child_processes:
                first_process = child_processes[0]
                first_name = first_process.get_name()

                input = {
                        'pipeline': subpipeline,
                        'sobject': sobject,
                        'process': first_process.get_name(),
                }

                event = "process|pending"
                Trigger.call(my, event, input)



        else:
            Trigger.call(my, "process|action", output=my.input)


 

class ProcessActionTrigger(BaseProcessTrigger):

    def execute(my):

        # get the pipeline
        pipeline = my.input.get("pipeline")
        process = my.input.get("process")
        sobject = my.input.get("sobject")

        if process.find(".") != -1:
            parts = process.split(".")
            process = parts[-1]

        process_obj = pipeline.get_process(process)
        node_type = process_obj.get_type()

        if node_type == "action":
            handler = WorkflowActionNodeHandler(input=my.input)
            return handler.handle_action()
        elif node_type == "approval":
            handler = WorkflowApprovalNodeHandler(input=my.input)
            return handler.handle_action()
        elif node_type in ["manual", "node"]:
            handler = WorkflowManualNodeHandler(input=my.input)
            return handler.handle_action()
        elif node_type == "hierarchy":
            handler = WorkflowHierarchyNodeHandler(input=my.input)
            return handler.handle_action()
        elif node_type == "input":
            handler = WorkflowInputNodeHandler(input=my.input)
            return handler.handle_action()
        elif node_type == "output":
            handler = WorkflowOutputNodeHandler(input=my.input)
            return handler.handle_action()
        elif node_type == "condition":
            handler = WorkflowConditionNodeHandler(input=my.input)
            return handler.handle_action()
 


        # Make sure the below is completely deprecated
        assert(False)


        if node_type not in ["node", "manual", "approval"]:
            my.set_all_tasks(sobject, process, "in_progress")


        # get the node's triggers
        search = Search("config/process")        
        search.add_filter("process", process)
        process_sobj = search.get_sobject()
        triggers = {}
        if process_sobj:
            triggers = process_sobj.get_json_value("workflow")
        if not triggers:
            triggers = {}




        process_obj = pipeline.get_process(process)
        node_type = process_obj.get_type()

        if node_type == "condition":
            my.handle_condition_node(sobject, pipeline, process, triggers)


        # TEST
        elif node_type == "custom":

            # Where do we get this?
            handler = 'tactic.ui.tools.NotificationNodeHandler'
            cmd = Common.create_from_class_anme(handler)
            cmd.execute()

            Trigger.call(my, "process|complete", my.input)


        elif node_type == "action":
            action = triggers.get("on_action")
            cbjs_action = triggers.get("cbjs_action")
            action_path = triggers.get("on_action_path")
            kwargs, input = my.build_trigger_input()
            if action or action_path:
                if action:
                    cmd = PythonCmd(code=action, input=input, **kwargs)
                else:
                    cmd = PythonCmd(script_path=action_path, input=input, **kwargs)

                ret_val = cmd.execute()

            elif cbjs_action:
                from tactic.command import JsCmd
                if cbjs_action:
                    cmd = JsCmd(code=cbjs_action, input=input, **kwargs)
                else:
                    cmd = JsCmd(script_path=script_path, input=input, **kwargs)

                ret_val = cmd.execute()
            else:
                # or call a trigger
                Trigger.call(my, "process|action", input, process=process_sobj.get_code())

            Trigger.call(my, "process|complete", my.input)


        else:
            Trigger.call(my, "process|complete", output=my.input)



            



    def handle_condition_node(my, sobject, pipeline, process, triggers):

        ret_val = my.run_callback(pipeline, process, "action")

        # if a None return value was given, then probably no condition exists
        # yet, so just let if flow through
        if ret_val == None:
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
                event = "process|pending"
                attr = "success"
                direction = "output"
                processes = pipeline.get_output_processes(process, from_attr=attr)
                if not processes:
                    attr = None

        elif ret_val == False:

            fail_cbk = triggers.get("on_fail")
            if fail_cbk:
                cmd = PythonCmd(code=fail_cbk, sobject=sobject)
                cmd.execute()
                return
            else:
                event = "process|revise"

                # check to see if there is an output process
                attr = "fail"
                processes = pipeline.get_output_processes(process, from_attr=attr)
                if processes:
                    direction = "output"
                else:
                    direction = "input"
                    attr = None

        else:
            event = "process|pending"
            if isinstance(ret_val, basestring): 
                ret_val = [ret_val]

            output_processes = []
            for attr in ret_val: 
                outputs = pipeline.get_output_processes(process, from_attr=attr)
                if outputs:
                    output_processes.extend(outputs)

            # if there are no output attrs, then check the node names
            if not output_processes:
                outputs = pipeline.get_output_processes(process)
                for output in outputs:
                    if output.get_name() in ret_val:
                        output_processes.append(output)

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


        for process in processes:
            process_name = process.get_name()
            output = {
                'sobject': sobject,
                'pipeline': pipeline,
                'process': process_name,
            }
            Trigger.call(my, event, output)





class ProcessCompleteTrigger(BaseProcessTrigger):

    def get_status(my):
        return "complete"

    def execute(my):

        process = my.input.get("process")
        sobject = my.input.get("sobject")
        pipeline = my.input.get("pipeline")


        if process.find(".") != -1:
            parts = process.split(".")
            process = parts[-1]

        process_obj = pipeline.get_process(process)
        node_type = process_obj.get_type()

        handler = None
        if node_type == "action":
            handler = WorkflowActionNodeHandler(input=my.input)
        elif node_type == "approval":
            handler = WorkflowApprovalNodeHandler(input=my.input)
        elif node_type in ["manual", "node"]:
            handler = WorkflowManualNodeHandler(input=my.input)
        elif node_type == "hierarchy":
            handler = WorkflowHierarchyNodeHandler(input=my.input)
        elif node_type == "input":
            handler = WorkflowInputNodeHandler(input=my.input)
        elif node_type == "output":
            handler = WorkflowOutputNodeHandler(input=my.input)
        elif node_type == "condition":
            handler = WorkflowConditionNodeHandler(input=my.input)


        if handler:
            return handler.handle_complete()


        # Make sure the below is completely deprecated
        assert(False)



        status = my.get_status()

        # run a nodes complete trigger
        #event = "process|complete|%s" % process
        #Trigger.call(my, event, output=my.input)
        my.run_callback(pipeline, process, status)

        process_obj = pipeline.get_process(process)
        node_type = process_obj.get_type()


        if node_type in ["action", "condition"]:
            my.set_all_tasks(sobject, process, "complete")
            return


        if node_type not in ['output']:
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



        elif node_type in ['output']:

            search = Search("config/process")        
            search.add_filter("subpipeline_code", pipeline.get_code())
            supprocess_sobj = search.get_sobject()
            suppipeline_code = supprocess_sobj.get_value("pipeline_code")
            supprocess = supprocess_sobj.get_value("process")

            suppipeline = Search.get_by_code("sthpw/pipeline", suppipeline_code)
            output = {
                'pipeline': suppipeline,
                'sobject': sobject,
                'process': supprocess
            }

            event = "process|complete"
            Trigger.call(my, event, output)



        else:

            # if this is subpipeline and there are no output processes
            parent_process = pipeline.get_value("parent_process")
            if parent_process:
                output_processes = pipeline.get_output_processes(process)
                if not output_processes:
                    # look at the parent pipelline
                    parent_process_sobj = Search.get_by_code("config/process", parent_process)
                    parent_pipeline_code = parent_process_sobj.get_value("pipeline_code")
                    parent_pipeline = Search.get_by_code("sthpw/pipeline", parent_pipeline_code)
                    parent_process = parent_process_sobj.get_value("process")

                    output = {
                        'pipeline': parent_pipeline,
                        'sobject': sobject,
                        'process': parent_process,
                    }

                    event = "process|complete"
                    Trigger.call(my, event, output)




class ProcessApproveTrigger(ProcessCompleteTrigger):
    def get_status(my):
        return "approved"



class ProcessRejectTrigger(BaseProcessTrigger):

    def get_status(my):
        return "reject"

    def execute(my):

        process = my.input.get("process")
        sobject = my.input.get("sobject")
        pipeline = my.input.get("pipeline")

        process_obj = pipeline.get_process(process)
        node_type = process_obj.get_type()

        my.run_callback(pipeline, process, "revise")

        my.set_all_tasks(sobject, process, my.get_status())

        input_processes = pipeline.get_input_processes(process)
        for input_process in input_processes:
            input_process = input_process.get_name()

            input = {
                'pipeline': pipeline,
                'sobject': sobject,
                'process': input_process
            }

            event = "process|revise"
            Trigger.call(my, event, input)




class ProcessReviseTrigger(ProcessRejectTrigger):

    def get_status(my):
        return "revise"

    def execute(my):
        process = my.input.get("process")
        sobject = my.input.get("sobject")
        pipeline = my.input.get("pipeline")

        process_obj = pipeline.get_process(process)
        node_type = process_obj.get_type()

        my.run_callback(pipeline, process, "revise")

        if node_type in ["condition", "action", "approval"]:

            my.set_all_tasks(sobject, process, "")

            input_processes = pipeline.get_input_processes(process)
            for input_process in input_processes:
                input_process = input_process.get_name()

                input = {
                    'pipeline': pipeline,
                    'sobject': sobject,
                    'process': input_process
                }

                event = "process|revise"
                Trigger.call(my, event, input)


        else:
            my.set_all_tasks(sobject, process, my.get_status())




class ProcessErrorTrigger(BaseProcessTrigger):

    def execute(my):
        process = my.input.get("process")
        sobject = my.input.get("sobject")
        pipeline = my.input.get("pipeline")
 
        print "Error: Failed to process [%s] on sobject [%s]" % (process, sobject.get_search_key() )

        # TODO: send a message so that those following this sobject will be notified






