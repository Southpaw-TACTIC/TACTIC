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

__all__ = ['Workflow', 'BaseProcessTrigger', 'ProcessStatusTrigger']

import tacticenv

from pyasm.common import Common, Config, jsondumps, TacticException
from pyasm.command import Trigger, Command
from pyasm.search import SearchType, Search, SObject
from pyasm.biz import Pipeline, Task


PREDEFINED = [
        'pending',
        'in_progress',
        'action',
        'complete',
        'approved',
        'reject',
        'revise',
        'error',
]



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


        event = "process|custom"
        trigger = SearchType.create("sthpw/trigger")
        trigger.set_value("event", event)
        trigger.set_value("class_name", ProcessCustomTrigger)
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


        if pipeline.get_value("use_workflow", no_exception=True) in [False, "false"]:
            return



        process_name = task.get_value("process")
        status = task.get_value("status")
        if status.lower() in PREDEFINED:
            status = status.lower()

        # handle the approve case (which really means complete)
        if status == "approved":
            status = "complete"

        process = pipeline.get_process(process_name)
        if not process:
            # we don't have enough info here
            return

        node_type = process.get_type()
        process_name = process.get_name()


        if status in PREDEFINED:
            event = "process|%s" % status
        else:
            event = "process|custom"

        output = {
            'sobject': sobject,
            'pipeline': pipeline,
            'process': process_name,
            'status': status
        }
        Trigger.call(task, event, output=output)




class ProcessStatusTrigger(Trigger):

    def execute(my):
        process = my.input.get("process")
        pipeline_code = my.input.get("pipeline")
        status = my.input.get("status")
        sobject = my.input.get("sobject")

        pipeline = Pipeline.get_by_code(pipeline_code)

        # related process
        trigger_sobj = my.get_trigger_sobj()
        data = trigger_sobj.get_json_value("data")
        related_process_code = data.get("process_code")
        related_type = data.get("search_type")
        related_pipeline_code = data.get("pipeline_code")

        related_pipeline = Pipeline.get_by_code(related_pipeline_code)

        related_process_sobj = Search.get_by_code("config/process", related_process_code)
        related_process = related_process_sobj.get("process")
        

        # get the related sobject
        related_sobjects = Search.eval("@SOBJECT(%s)" % related_type, sobject)

        for related_sobject in related_sobjects:

            # inputs are reversed
            kwargs = {
                'sobject': related_sobject,
                'process': related_process,
                'pipeline': related_pipeline,
                'status': status,
                'related_sobject': sobject,
                'related_pipeline': pipeline,
                'related_process': process,
            }



            event = "process|%s" % status
            Trigger.call(my, event, kwargs)




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
        if not process_sobj:
            raise TacticException('Process item [%s] has not been created. Please save your pipeline in the Project Workflow Editor to refresh the processes.'%process)



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

            process_code = process_sobj.get_code()
            triggers = Trigger.call(my, event, kwargs, process=process_code)
            if triggers:
                ret_val = triggers[0].get_ret_val()



        # announce callback has been called for any listeners
        search_type = pipeline.get_value("search_type")
        event = "workflow|%s" % search_type
        process_code = process_sobj.get_code()
        Trigger.call(my, event, kwargs, process=process_code)

        search_type = pipeline.get_value("search_type")
        event = "workflow|%s" % search_type
        Trigger.call(my, event, kwargs, process=process)


        return ret_val



    def build_trigger_input(my):
        # create a package for the trigger

        pipeline = my.input.get("pipeline")
        process = my.input.get("process")
        sobject = my.input.get("sobject")
        status = my.input.get("status")



        kwargs = {
            'sobject': sobject,
            'pipeline': pipeline,
            'process': process,
            'status': status
        }
        input = {
            'sobject': sobject.get_sobject_dict(),
            'pipeline': pipeline.to_string(),
            'process': process,
            'status': status,
            'inputs': [x.get_name() for x in pipeline.get_input_processes(process)],
            'outputs': [x.get_name() for x in pipeline.get_output_processes(process)],
        }
        return kwargs, input



    def log_message(my, sobject, process, status):

        # need to use API for now
        key = "%s|%s|status" % (sobject.get_search_key(), process)
        from tactic_client_lib import TacticServerStub
        server = TacticServerStub.get()
        server.log_message(key, status)



    def notify_listeners(my, sobject, process, status):

        # find all of the nodes that are listening to this status
        event = "%s|%s|%s" % (sobject.get_search_key(), process, status)
        #Trigger.call(my, event, my.input)

        # or 

        search = Search("sthpw/process")
        search.add_filter("type", "listen")
        search.add_filter("key", event)
        process_sobjs = search.get_sobjects()

        # we have all of the processes that are listening

        for process_sobj in process_sobjs:

            # for each process, we need to find the related sobjects



            # so what exactly does this do ...
            # shouldn't this use triggers?
            pipeline_code = process_sobj.get_value("pipeline_code")
            pipeline = Pipeline.get_by_code(pipeline_code)

            # find all of the related sobjects
            process_obj = pipeline.get_process(process)
            related_search_type = process_obj.get_attribute("search_type")
            related_status = process_obj.get_attribute("status")
            related_process = process_obj.get_attribute("process")
            related_scope = process_obj.get_attribute("scope")

            # get the node's triggers
            if not related_search_type:
                search = Search("config/process")        
                search.add_filter("process", my.process)
                search.add_filter("pipeline_code", pipeline.get_code())
                process_sobj = search.get_sobject()

                workflow = process_sobj.get_json_value("workflow", {})
                related_search_type = workflow.get("search_type")
                related_proces = workflow.get("proces")
                related_status = workflow.get("status")
                related_scope = workflow.get("scope")




    def check_complete_inputs(my):

        # Check dependencies
        caller_sobject = my.input.get("related_sobject")
        if not caller_sobject:
            return True


        related_pipeline = my.input.get("related_pipeline")
        related_process = my.input.get("related_process")
        related_search_type = caller_sobject.get_base_search_type()

        pipeline = my.input.get("pipeline")
        process = my.input.get("process")
        sobject = my.input.get("sobject")


        # find related sobjects
        #related_sobjects = sobject.get_related_sobjects(related_search_type)
        related_sobjects = Search.eval("@SOBJECT(%s)" % related_search_type, sobject)
        if not related_sobjects:
            return True

        # get the message status from each of these
        keys = []
        for related_sobject in related_sobjects:
            # ignore the caller as we know that is complete
            if related_sobject.get_search_key() == caller_sobject.get_search_key():
                continue

            key = "%s|%s|status" % (related_sobject.get_search_key(), related_process)
            keys.append(key)

        # get the statuses
        search = Search("sthpw/message")
        search.add_filters("code", keys)
        message_sobjects = search.get_sobjects()


        complete = {}

        # find the status
        for message_sobject in message_sobjects:
            status = message_sobject.get_value("message")
            if status in ["complete"]:
                complete[message_sobject.get_code()] = True


        # some backwards compatibility to figure out if the related sobject is "complete"
        if False and len(message_sobjects) < len(keys):
            # look at the overall status
            for related_sobject in related_sobjects:
                key = "%s|%s|status" % (related_sobject.get_search_key(), related_process)
                overall_status = related_sobject.get_value("status", no_exception=True)
                if overall_status.lower() == "complete":
                    complete[key] = True

                else:
                    related_tasks = Search.eval("@SOBJECT(sthpw/task['process','%s'])" % related_process, related_sobject)
                    for related_task in related_tasks:
                        related_status = related_task.get_value("status")
                        if related_status.lower() == "complete":
                            complete[key] = True


        # the caller is implied to be complete
        key = "%s|%s|status" % (caller_sobject.get_search_key(), related_process)
        complete[key] = True

        is_complete = True
        print "complete: ", complete
        for related_sobject in related_sobjects:
            key = "%s|%s|status" % (related_sobject.get_search_key(), related_process)
            if not complete.get(key):
                is_complete = False
                break


        print "    is complete: ", is_complete

        return is_complete








class BaseWorkflowNodeHandler(BaseProcessTrigger):

    def __init__(my, **kwargs):
        super(BaseWorkflowNodeHandler, my).__init__(**kwargs)
        my.input = kwargs.get("input")

        my.pipeline = my.input.get("pipeline")
        my.process = my.input.get("process")
        my.sobject = my.input.get("sobject")

        if my.process.find(".") != -1:
            parts = my.process.split(".")
            my.process = parts[-1]
            my.process_parts = parts[:-1]
        else:
            my.process_parts = []


    def check_inputs(my):
        pipeline = my.input.get("pipeline")
        process = my.input.get("process")
        sobject = my.input.get("sobject")

        #print "check_input: ", process

        # first check the inputs.  If there is only one input, then
        # skip this check
        input_processes = pipeline.get_input_processes(process)
        if len(input_processes) <= 1:
            return True


        # check all of the input processes to see if they are all complete
        complete = True
        for input_process in input_processes:
            key = "%s|%s|status" % (sobject.get_search_key(), input_process.get_name())
            message_sobj = Search.get_by_code("sthpw/message", key)
            if message_sobj:
                message = message_sobj.get_json_value("message")
                if message != "complete":
                    complete = False
                    break
            else:
                # look for some other means to determine if this is done
                search = Search("sthpw/task")
                search.add_parent_filter(sobject)
                search.add_filter("process", input_process.get_name())
                task = search.get_sobject()
                if task:
                    task_status = task.get("status")
                    if status.lower() != "complete":
                        complete = False
                        break


        if not complete:
            return False
        else:
            return True




    def handle_pending(my):

        # DISABLE for now
        #if not my.check_inputs():
        #    return

        print "pending: ", my.process

        # simply calls action
        my.log_message(my.sobject, my.process, "pending")
        my.set_all_tasks(my.sobject, my.process, "pending")
        my.run_callback(my.pipeline, my.process, "pending")

        Trigger.call(my, "process|action", output=my.input)


    def handle_action(my):

        my.log_message(my.sobject, my.process, "in_progress")
        my.set_all_tasks(my.sobject, my.process, "in_progress")
        my.run_callback(my.pipeline, my.process, "action")

        Trigger.call(my, "process|complete", output=my.input)


    def handle_complete(my):


        print "complete: ", my.process
 
        # run a nodes complete trigger
        status = "complete"
        my.log_message(my.sobject, my.process, status)
        my.set_all_tasks(my.sobject, my.process, "complete")
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

        my.log_message(my.sobject, my.process, "reject")
        my.run_callback(my.pipeline, my.process, "reject")

        # set all tasks in the process to revise
        my.set_all_tasks(my.sobject, my.process, "reject")

        process_obj = my.pipeline.get_process(my.process)

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

        my.log_message(my.sobject, my.process, "revise")
        my.run_callback(my.pipeline, my.process, "revise")
        # set all tasks in the process to revise
        my.set_all_tasks(my.sobject, my.process, "revise")

        process_obj = my.pipeline.get_process(my.process)

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

    def handle_pending(my):

        # DISABLE for now
        #if not my.check_inputs():
        #    return

        print "pending: ", my.process

        # simply calls action
        my.log_message(my.sobject, my.process, "pending")


        search = Search("config/process")        
        search.add_filter("process", my.process)
        search.add_filter("pipeline_code", my.pipeline.get_code())
        process_sobj = search.get_sobject()

        workflow = process_sobj.get_json_value("workflow")
        if workflow.get("autocreate_task") in ['true', True]:
            autocreate_task = True
        else:
            autocreate_task = False


        # check to see if the tasks exist and if they don't then create one
        if autocreate_task:
            tasks = Task.get_by_sobject(my.sobject, process=my.process)
            if not tasks:
                Task.add_initial_tasks(my.sobject, processes=[my.process], status="pending")
            else:
                my.set_all_tasks(my.sobject, my.process, "pending")
        else:
            my.set_all_tasks(my.sobject, my.process, "pending")


        my.run_callback(my.pipeline, my.process, "pending")

        Trigger.call(my, "process|action", output=my.input)


    def handle_action(my):
        my.log_message(my.sobject, my.process, "in_progress")
        # does nothing
        pass



class WorkflowActionNodeHandler(BaseWorkflowNodeHandler):

    def handle_action(my):
        print "action: ", my.process

        my.log_message(my.sobject, my.process, "in_progress")

        process_obj = my.pipeline.get_process(my.process)

        # get the node's triggers
        search = Search("config/process")        
        search.add_filter("process", my.process)
        search.add_filter("pipeline_code", my.pipeline.get_code())
        process_sobj = search.get_sobject()

        #process_sobj = my.pipeline.get_process_sobject(my.process)


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
            from tactic.command import PythonCmd
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
        my.log_message(my.sobject, my.process, "pending")

        search = Search("config/process")        
        search.add_filter("process", my.process)
        search.add_filter("pipeline_code", my.pipeline.get_code())
        process_sobj = search.get_sobject()

        assigned = None
        if process_sobj:
            workflow = process_sobj.get_json_value("workflow", {})
            if workflow:
                assigned = workflow.get("assigned")
     

        # check to see if the tasks exist and if they don't then create one
        tasks = Task.get_by_sobject(my.sobject, process=my.process)
      
        if not tasks:
            tasks = Task.add_initial_tasks(my.sobject, processes=[my.process], assigned=assigned)
        else:
            my.set_all_tasks(my.sobject, my.process, "pending")


        Trigger.call(my, "process|action", my.input)


    def handle_action(my):
        my.log_message(my.sobject, my.process, "action")
        # does nothing
        pass




class WorkflowHierarchyNodeHandler(BaseWorkflowNodeHandler):

    def handle_pending(my):
        my.log_message(my.sobject, my.process, "pending")

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



class WorkflowDependencyNodeHandler(BaseWorkflowNodeHandler):

    def handle_revise(my):
        return my._handle_dependency("revise")

    def handle_reject(my):
        return my._handle_dependency("reject")



    def handle_action(my):
        return my._handle_dependency()


    def _handle_dependency(my, status=None):
        if status:
            my.log_message(my.sobject, my.process, status)
            my.set_all_tasks(my.sobject, my.process, status)
            my.run_callback(my.pipeline, my.process, status)
        else:
            my.log_message(my.sobject, my.process, "in_prgress")
            my.set_all_tasks(my.sobject, my.process, "in_progress")
            my.run_callback(my.pipeline, my.process, "action")


        pipeline = my.input.get("pipeline")
        process = my.input.get("process")
        sobject = my.input.get("sobject")

        process_obj = pipeline.get_process(process)
        related_search_type = process_obj.get_attribute("search_type")
        related_status = process_obj.get_attribute("status")
        related_process = process_obj.get_attribute("process")
        related_scope = process_obj.get_attribute("scope")
        related_wait = process_obj.get_attribute("wait")

        # get the node's triggers
        if not related_search_type:
            search = Search("config/process")        
            search.add_filter("process", process)
            search.add_filter("pipeline_code", pipeline.get_code())
            process_sobj = search.get_sobject()

            workflow = process_sobj.get_json_value("workflow", {})
            related_search_type = workflow.get("search_type")
            related_process = workflow.get("process")
            related_status = workflow.get("status")
            related_scope = workflow.get("scope")
            related_wait = workflow.get("wait")



        if not related_search_type:
            print "WARNING: no related search_type found"
            return


        if not related_process:
            print "WARNING: no related process found"
            return



        # override related_status with status passed in
        if status:
            related_status = status


        if related_search_type.startswith("@"):
            expression = related_search_type
        else:
            expression = "@SOBJECT(%s)" % related_search_type

        #expression = '@SOBJECT(vfx/asset_in_shot.vfx/shot)'

        if related_scope == "global":
            related_sobjects = Search.eval(expression)
        else:
            related_sobjects = Search.eval(expression, sobjects=[sobject])


        for related_sobject in related_sobjects:

            # if the related_sobject is already complete, don't do anything
            key = "%s|%s|status" % (related_sobject.get_search_key(), related_process)
            message_sobj = Search.get_by_code("sthpw/message", key)
            if message_sobj:
                value = message_sobj.get_value("message")
                if related_status.lower() in ["revise", "reject"]:
                    pass
                elif value == "complete" and value not in ['revise', 'reject']:
                    continue


            # This is for unittests which don't necessarily commit changes
            related_sobject = Search.get_by_search_key(related_sobject.get_search_key())

            related_pipeline = Pipeline.get_by_sobject(related_sobject)
            if not related_process:
                # get the first one
                related_processes = related_pipeline.get_processes()
                related_process = related_processes[0]


            if related_status in ["in_progress", "In Progress"]:
                event = "process|action"
            else:
                if related_status.lower() in PREDEFINED:
                    event = "process|%s" % related_status.lower()
                else:
                    event = "process|%s" % related_status


            # inputs are reversed as it sends the message
            input = {
                'sobject': related_sobject,
                'pipeline': related_pipeline,
                'process': related_process,
                'related_sobject': sobject,
                'related_pipeline': pipeline,
                'related_process': process,
            }

            Trigger.call(my, event, input)


        if status not in ['revise','reject'] and related_wait in [False, 'false', None]:
            event = "process|complete"
            Trigger.call(my, event, my.input)





class WorkflowInputNodeHandler(BaseWorkflowNodeHandler):
    def handle_pending(my):
        # fast track to complete
        Trigger.call(my, "process|complete", output=my.input)


class WorkflowOutputNodeHandler(BaseWorkflowNodeHandler):

    def handle_pending(my):
        # fast track to complete
        Trigger.call(my, "process|complete", output=my.input)


    def handle_complete(my):
        my.log_message(my.sobject, my.process, "complete")

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
        my.log_message(my.sobject, my.process, "action")

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

        from tactic.command import PythonCmd

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
        my.log_message(my.sobject, my.process, "complete")
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
        elif node_type in ["manual", "node", "progress"]:
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
        elif node_type == "dependency":
            handler = WorkflowDependencyNodeHandler(input=my.input)
            return handler.handle_pending()



        # Make sure the below is completely deprecated
        assert(False)



 

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
        elif node_type in ["manual", "node","progress"]:
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
        elif node_type == "dependency":
            handler = WorkflowDependencyNodeHandler(input=my.input)
            return handler.handle_action()
 


        # Make sure the below is completely deprecated
        assert(False)





class ProcessCompleteTrigger(BaseProcessTrigger):

    def get_status(my):
        return "complete"

    def execute(my):



        process = my.input.get("process")
        sobject = my.input.get("sobject")
        pipeline = my.input.get("pipeline")



        if not my.check_complete_inputs():
            my.log_message(sobject, process, "in_progress")
            return

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
        elif node_type in ["manual", "node","progress"]:
            handler = WorkflowManualNodeHandler(input=my.input)
        elif node_type == "hierarchy":
            handler = WorkflowHierarchyNodeHandler(input=my.input)
        elif node_type == "input":
            handler = WorkflowInputNodeHandler(input=my.input)
        elif node_type == "output":
            handler = WorkflowOutputNodeHandler(input=my.input)
        elif node_type == "condition":
            handler = WorkflowConditionNodeHandler(input=my.input)
        elif node_type == "dependency":
            handler = WorkflowDependencyNodeHandler(input=my.input)


        if handler:
            return handler.handle_complete()


        # Make sure the below is completely deprecated
        assert(False)




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


        if node_type == "dependency":
            handler = WorkflowDependencyNodeHandler(input=my.input)
            return handler.handle_reject()


        my.run_callback(pipeline, process, "reject")

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
        pipeline = my.input.get("pipeline")
        process = my.input.get("process")
        sobject = my.input.get("sobject")

        if process.find(".") != -1:
            parts = process.split(".")
            process = parts[-1]

        process_obj = pipeline.get_process(process)
        node_type = process_obj.get_type()

        if node_type == "dependency":
            handler = WorkflowDependencyNodeHandler(input=my.input)
            return handler.handle_revise()


        process = my.input.get("process")
        sobject = my.input.get("sobject")
        pipeline = my.input.get("pipeline")

        my.log_message(sobject, process, my.get_status())

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





class ProcessCustomTrigger(BaseProcessTrigger):

    def execute(my):
        process = my.input.get("process")
        sobject = my.input.get("sobject")
        pipeline = my.input.get("pipeline")

        status = my.input.get("status")
        if status.lower() in PREDEFINED:
            status = status.lower()


        my.log_message(sobject, process, status)

        # FIXME: this causes an infinite loop
        #my.set_all_tasks(sobject, process, status)

        # FIXME: not sure about this "custom"
        my.run_callback(pipeline, process, "custom")


        process_obj = pipeline.get_process(process)
        if not process_obj:
            print "No process_obj [%s]" % process
            return

        status_pipeline_code = process_obj.get_task_pipeline()
        status_pipeline = Pipeline.get_by_code(status_pipeline_code)
        if not status_pipeline:
            print "No custom status pipeline [%s]" % process
            return

        status_processes = status_pipeline.get_process_names()

        status_obj = status_pipeline.get_process(status)
        if not status_obj:
            print "No status [%s]" % status
            return


        direction = status_obj.get_attribute("direction")
        to_status = status_obj.get_attribute("status")
        mapping = status_obj.get_attribute("mapping")
        if not to_status and not mapping:
            search = Search("config/process")        
            search.add_filter("pipeline_code", status_pipeline.get_code())
            search.add_filter("process", status)
            process_sobj = search.get_sobject()
            if process_sobj:
                workflow = process_sobj.get_json_value("workflow", {})
                direction = workflow.get("direction")
                to_status = workflow.get("status")
                mapping = workflow.get("mapping")

        if to_status and to_status.lower() in PREDEFINED:
            to_status = to_status.lower()

        #print "direction: ", direction
        #print "to_status: ", to_status


        if mapping:
            mapping = mapping.lower()
            event = "process|%s" % mapping
            Trigger.call(my.get_caller(), event, output=my.input)
        elif to_status:

            if direction == "current":
                processes = [processes_obj]
            elif direction == "input":
                processes = pipeline.get_input_processes(process)
            else:
                processes = pipeline.get_output_processes(process)


            if to_status in PREDEFINED:
                event = "process|%s" % to_status
            else:
                event = "process|custom"

            for process in processes:
                process_name = process.get_name()
                output = {
                    'sobject': sobject,
                    'pipeline': pipeline,
                    'process': process_name,
                    'status': to_status,
                }
                Trigger.call(my, event, output)

        else:
            # Do nothing
            pass



 





