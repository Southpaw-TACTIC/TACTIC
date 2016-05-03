###########################################################
#
# Copyright (c) 2010, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#
__all__ = ['PipelineTaskStatusTrigger', 'PipelineTaskTrigger', 'PipelineTaskDateTrigger', 'PipelineTaskCreateTrigger', 'RelatedTaskUpdateTrigger', 'TaskCreatorTrigger', 'TaskCompleteTrigger']

import tacticenv

from pyasm.common import Common, Xml, jsonloads, Container
from pyasm.biz import Task
from pyasm.web import Widget, WebContainer, WidgetException
from pyasm.command import Command, CommandException, Trigger
from pyasm.security import Sudo

from pyasm.biz import Pipeline, Task
from pyasm.search import Search, SObject, SearchKey

class PipelineTaskStatusTrigger(Trigger):
    # if the "ingest" task is set to "Approved",
    # then set the "work" task to "Pending"
    SAMPLE_DATA = {
        'src_process':  'ingest',
        'src_status':   'Approved',
        'dst_process':  'work',
        'dst_status':   'Pending',
    }


    def execute(my):
        trigger_sobj = my.get_trigger_sobj()
        data = trigger_sobj.get_value("data")
        data = jsonloads(data)

        data_list = data
        if isinstance(data, dict):
            data_list = [data]
        src_task = my.get_caller()
        for data in data_list:
            # get the src task caller
            dst_task = None
            # it could be the FileCheckin Command
            if not isinstance(src_task, SObject):
                input = my.get_input()
                snapshot = input.get('snapshot')

                if not snapshot:
                    continue
                if isinstance(snapshot, dict):
                    snapshot = SearchKey.get_by_search_key(snapshot.get('__search_key__'))
                src_process = data.get('src_process')
                
                src_task = Search.eval("@SOBJECT(parent.sthpw/task['process','%s'])"%src_process,\
                    sobjects=snapshot, single=True)
                if not src_task:
                    continue

            # make sure the caller process is the same as the source process
            if src_task.get_value("process") != data.get("src_process"):
                continue

            #conditionx = "@GET(.status) != 'Approved'"
            #result = Search.eval(conditionx, src_task)
            #print "result: ", result







            # make sure that the appropriate status was set
            src_status = data.get("src_status")
            if src_status and src_task.get_value("status") != src_status:
                continue

            dst_process = data.get("dst_process")
            dst_status = data.get("dst_status")

            sobject = src_task.get_parent()
            tasks = Task.get_by_sobject(sobject)

            updated_tasks = []
            use_parent = data.get("use_parent")
            if use_parent in [True,'true']:
                parent = sobject.get_parent()
                parent_tasks = Task.get_by_sobject(parent, dst_process)

                condition = data.get("condition")
                if not condition:
                    condition = "all"

                if condition == "all":
                    condition_met = True
                    for task in tasks:
                        if src_task.get_value("status") != src_status:
                            condition_met = False

                elif condition == "any":
                    condition_met = False
                    for task in tasks:
                        if task.get_value("status") == src_status:
                            condition_met = True
                            break

                if condition_met:
                    for task in parent_tasks:
                        if task.get_value("process") == dst_process:
                            updated_tasks.append(task)

            else:
                for task in tasks:
                    if task.get_value("process") == dst_process:
                        updated_tasks.append(task)


            for task in updated_tasks:
                if task.get_value("process") == dst_process:
                    task.set_value("status", dst_status)
                    task.commit()


            """
            # find the task with the appropriate process
            if src_task.get_value("process") == dst_process:
                dst_task = src_task

            # get the output and input tasks
            if not dst_task:
                output_tasks = src_task.get_output_tasks()

                for task in output_tasks:
                    if task.get_value("process") == dst_process:
                        dst_task = task
                        break

            if not dst_task:
                input_tasks = src_task.get_input_tasks()
                for task in input_tasks:
                    if task.get_value("process") == dst_process:
                        dst_task = task
                        break

            if not dst_task:
                continue

            dst_status = data.get("dst_status")

            dst_task.set_value("status", dst_status)
            dst_task.commit()


            """

class PipelineTaskTrigger(Trigger):
    '''This is the trigger that is executed on a change'''

    ARGS_KEYS = {
    }


    def execute(my):

        trigger_sobj = my.get_trigger_sobj()
        data = trigger_sobj.get_value("data")
        #data = """[
        #{ "prefix": "rule", "name": "status", "value": "Approved" },
        #{ "prefix": "rule", "name": "pipeline" "value": "model" },
        #{ "prefix": "action", "type": "output", "name": "status", "value": "Pending" }
        #]
        #"""

        data = jsonloads(data)
        print "data: ", data
        from tactic.ui.filter import FilterData
        filter_data = FilterData(data)

        task = my.get_caller()

        # check that the process is correct
        trigger_info = filter_data.get_values_by_index("trigger")
        process = trigger_info.get("process")

        if task.get_value("process") != process:
            return



        parent = None

        rules = filter_data.get_values_by_prefix("rule")

        # go through each rule and determine if this trigger applies
        is_valid = True
        for rule in rules:
            attribute = rule.get('name')
            value = rule.get('value')

            if attribute in ['status']:
                # if condition does not match
                if task.get_value(attribute) != value:
                    is_valid = False

            elif attribute in ['pipeline']:
                attribute = 'pipeline_code'
                if parent == None:
                    parent = task.get_parent()
                    if parent == None:
                        continue

                if parent.get_value(attribute) != value:
                    is_valid = False

            else:
                is_valid = False

        if not is_valid:
            return



        # update the data

        #input = my.get_input()
        #update_data = input.get('update_data')
        #status = update_data.get('status')
        #search_key = input.get('search_key')
        #task = Search.get_by_search_key(search_key)


        # get the next process tasks
        output_tasks = task.get_output_tasks()
        input_tasks = task.get_input_tasks()
        actions = filter_data.get_values_by_prefix("action")
        #print "actions: ", actions

        for action in actions:
            type = action.get("type")
            attribute = action.get('name')
            value = action.get('value')

            if type == 'output':
                for output_task in output_tasks:
                    #output_status = output_task.get_value("status")
                    output_task.set_value(attribute, value)
                    output_task.commit()


            elif type == 'input':
                for output_task in output_tasks:
                    print "a : ", attribute, value
                    
                    #output_status = output_task.get_value("status")
                    output_task.set_value(attribute, value)
                    output_task.commit()


            elif type == 'process':
                process = action.get("process")

                for input_task in input_tasks:
                    task_process = input_task.get_value("process")
                    if task_process == process:
                        input_task.set_value(attribute, value)
                        input_task.commit()
                        break

                for output_task in output_tasks:
                    task_process = output_task.get_value("process")
                    if task_process == process:
                        output_task.set_value(attribute, value)
                        output_task.commit()
                        break
                


class PipelineTaskDateTrigger(Trigger):
    '''This is the trigger that is executed on a change'''

    ARGS_KEYS = {
    }


    def execute(my):

        trigger_sobj = my.get_trigger_sobj()
        data = trigger_sobj.get_value("data")
        #data = """
        #{ "columns": [column1, column2]
        #"""

        data = jsonloads(data)

        column = data.get('column')
        src_status = data.get('src_status')
        
        task = my.get_caller()
        if task.get_value("status") != src_status:
            return

        task.set_now(column)
        task.commit()






   

class RelatedTaskUpdateTrigger(Trigger):
    '''This is called on every task change.  It syncronizes tasks with
    the same context'''
    def execute(my):

        sudo = Sudo()

        input = my.get_input()
        search_key = input.get("search_key")
        update_data = input.get("update_data")
        mode = input.get("mode")
        if mode in ['insert','delete','retire']:
            return

        task = Search.get_by_search_key(search_key)

        process = task.get_value("process")
        context = task.get_value("context")
        parent = task.get_parent()

        # find all of the tasks with the same parent and same context
        search = Search("sthpw/task")
        search.add_parent_filter(parent)
        search.add_filter("process", process)
        search.add_filter("context", context)
        tasks = search.get_sobjects()

        trigger_dict = Container.get('RelatedTaskUpdateTrigger')
        if not trigger_dict:
            trigger_dict = {}

        for attr, value in update_data.items():
            # skip assigned as this is the only difference between related tasks
            if attr == 'assigned':
                continue
            # update_data could have the post-conversion value None
            if value == None:
                value = ''

            for task in tasks:
                task_search_key = task.get_search_key()
                # skip the current one
                if task_search_key == search_key or trigger_dict.get(task_search_key):
                    continue
                task.set_value(attr, value)
                trigger_dict[task_search_key] = True
                Container.put('RelatedTaskUpdateTrigger', trigger_dict)
                # this should run trigger where applicable
                task.commit(triggers=True)

        del sudo







class PipelineTaskCreateTrigger(Trigger):
    
    def execute(my):
        input = my.get_input()

        search_key = input.get("search_key")
        task = Search.get_by_search_key(search_key)
        parent = task.get_parent()
        if not parent:
            return

        # get the definition of the trigger
        trigger_sobj = my.get_trigger_sobj()
        data = trigger_sobj.get_value("data")
        try:
            data = jsonloads(data)
        except:
            data = {}

        # check against source status if present 
        src_status = data.get("src_status")
        if src_status:
            task_status = task.get_value("status")
            if task_status != src_status:
                return

        process_names = data.get("output")
        if not process_names:
            return

        # only create new task if another of the same
        # process does not already exist
        search = Search("sthpw/task")
        search.add_filters("process", process_names)
        search.add_parent_filter(parent)
        search.add_project_filter()
        tasks = search.get_sobjects()
        existing_processes = [x.get_value("process") for x in tasks]
       
        for process in process_names:
            if process in existing_processes:    
                continue
            else:
                Task.create(parent, process, start_date=None, end_date=None)
          






class TaskCreatorTrigger(Trigger):
    '''This is executed on every insert of an sobject'''


    def has_been_called(my, prev_called_triggers):
        return False

    def execute(my):

        input = my.get_input()
       
        search_key = input.get("search_key")
        update_data = input.get("update_data")

        if not search_key or search_key.startswith('sthpw/'):
            return

        mode = input.get("mode")
        if mode not in ['insert']:
            return


        sobject = my.get_caller()
        pipeline_code = sobject.get_value("pipeline_code", no_exception=True)

        if not pipeline_code:
            return

        from pyasm.biz import Pipeline, Task
        from pyasm.search import SearchType

        pipeline = Pipeline.get_by_code(pipeline_code)
        if not pipeline:
            return

        if pipeline.get_value("autocreate_tasks", no_exception=True) not in ['true', True]:
            return

        #import time
        #start = time.time()
        Task.add_initial_tasks(sobject, pipeline_code=pipeline_code, skip_duplicate=True, mode='standard')

        #print "intial_tasks ...", search_key, time.time() - start





class TaskCompleteTrigger(Trigger):
    '''This trigger is executed to state "officially" that the task is complete'''
    def execute(my):

        input = my.get_input()

        sobject = my.get_caller()

        if isinstance(sobject, Task):
            task = sobject
        else:
            process = input.get("process")
            raise Exception("Not supported yet")



        # get the task process
        process = task.get_value("process")
        status = task.get_value("status")


        pipeline_code = task.get_value("pipeline_code")
        if not pipeline_code:
            pipeline_code = 'task'

        task_pipeline = Pipeline.get_by_code(pipeline_code)
        if not task_pipeline:
            return
        # get the last process
        statuses = task_pipeline.get_process_names()
        if not statuses:
            return 


        completion_statuses = []
        for status in statuses:
            status_obj = task_pipeline.get_process(status)
            attrs = status_obj.get_attributes()
            completion = attrs.get("completion")
            if completion == "100":
                completion_statuses.append(status)

        if not completion_statuses:
            completion_statuses.append(statuses[-1])

        is_complete = False

        update_data = input.get('update_data')
        if update_data.get("status") in completion_statuses:
            is_complete = True


        if is_complete == True:
            #task.set_value("is_complete", True)
            if not task.get_value("actual_end_date"):
                task.set_now("actual_end_date")
                my.add_description('Internal Task Complete Trigger')
                task.commit(triggers=False)



