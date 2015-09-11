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

__all__ = ["Task", "Timecard", "Milestone"]

import types
import re
from pyasm.common import Xml, Environment, Common
from pyasm.search import SObject, Search, SearchType, SObjectValueException
from prod_setting import ProdSetting
from pipeline import Pipeline
from pyasm.common import Environment, Date
from project import Project
from status import StatusLog

from datetime import datetime
from dateutil import parser



TASK_PIPELINE = '''
<pipeline type="serial">
  <process completion="0" color="#ecbf7f" name="Assignment"/>
  <process completion="10" color="#8ad3e5" name="Pending"/>
  <process completion="20" color="#e9e386" name="In Progress"/>
  <process completion="20" color="#a96ccf" name="Waiting"/>
  <process completion="30" color="#a96ccf" name="Need Assistance"/>
  <process completion="80" color="#e84a4d" name="Revise"/>
  <process completion="80" color="#e84a4d" name="Reject"/>
  <process completion="100" color="#a3d991" name="Complete"/>
  <process completion="100" color="#a3d991" name="Approved"/>
</pipeline>
'''


APPROVAL_PIPELINE = '''
<pipeline type="serial">
  <process completion="10" color="#8ad3e5" name="Pending"/>
  <process completion="50" color="#e84a4d" name="Reject"/>
  <process completion="100" color="#a3d991" name="Approved"/>
  <connect to="Reject" from="Pending"/>
  <connect to="Approved" from="Pending"/>
</pipeline>

'''


default_xml = Xml()
default_xml.read_string(TASK_PIPELINE)

OTHER_COLORS = {
    "Complete": "#a3d991",
    "Done":     "#a3d991",
    "Final":    "#a3d991",
    "Revise":   "#e84a4d",
    "Reject":   "#e84a4d",
    "Ready":    "#a3d991",
    "In_Progress":"#e9e386",
}



class Task(SObject):

    SEARCH_TYPE = "sthpw/task"

    def get_search_columns():
        return ['code','description']
    get_search_columns = staticmethod(get_search_columns)

    def get_required_columns():
        '''for csv import'''
        return ['search_type', 'search_id', 'process', 'project_code', 'pipeline_code']
    get_required_columns = staticmethod(get_required_columns)


    def get_default_task_xml():
        global TASK_PIPELINE

        from pyasm.web import Palette
        palette = Palette.get()
        xml = Xml()
        xml.read_string(TASK_PIPELINE)
        nodes = Xml.get_nodes(xml, "pipeline/process")
        for node in nodes:
            process = Xml.get_attribute(node, "name")
            color = Task.get_default_color(process)
            if color:
                Xml.set_attribute(node, "color", color)

        return xml.to_string()
    get_default_task_xml = staticmethod(get_default_task_xml)


    def get_default_approval_xml():
        global APPROVAL_PIPELINE

        from pyasm.web import Palette
        palette = Palette.get()
        xml = Xml()
        xml.read_string(APPROVAL_PIPELINE)
        nodes = Xml.get_nodes(xml, "pipeline/process")
        for node in nodes:
            process = Xml.get_attribute(node, "name")
            color = Task.get_default_color(process)
            if color:
                Xml.set_attribute(node, "color", color)

        return xml.to_string()
    get_default_approval_xml = staticmethod(get_default_approval_xml)





    def get_default_color(process):
        global default_xml
        global OTHER_COLORS
        node = default_xml.get_node("pipeline/process[@name='%s']" % process.title())
        if node is None:
            return OTHER_COLORS.get(process.title())
        color = default_xml.get_attribute(node, "color")
        if not color:
            color = OTHER_COLORS.get(process.title())

        from pyasm.web import Palette
        theme = Palette.get()
        if theme == 'dark':
            color = Common.modify_color(color, -50)

        return color
    get_default_color = staticmethod(get_default_color)



    def get_status_colors():

        status_colors = {}

        task_pipelines = Search.eval("@SOBJECT(sthpw/pipeline['search_type','sthpw/task'])")
        task_pipelines.append( Pipeline.get_by_code("task") )
        task_pipelines.append( Pipeline.get_by_code("approval") )
        if task_pipelines:
            for task_pipeline in task_pipelines:
                processes = task_pipeline.get_processes()
                pipeline_code = task_pipeline.get_code()
                status_colors[pipeline_code] = {}
                for process in processes:
                    process_dict = status_colors.get(pipeline_code)
                    color = process.get_color()
                    if not color:
                        color = Task.get_default_color(process.get_name())

                    process_dict[process.get_name()] = color

        return status_colors

    get_status_colors = staticmethod(get_status_colors)




    def get_default_processes():
        nodes = default_xml.get_nodes("pipeline/process")
        process_names = [ Xml.get_attribute(x, 'name') for x in nodes ]
        return process_names
    get_default_processes = staticmethod(get_default_processes)

    def add_static_triggers(cls):
        # event sthpw/trigger
        from pyasm.command import Trigger
        event = "change|sthpw/task"
        trigger = SearchType.create("sthpw/trigger")
        trigger.set_value("event", event)
        #trigger.set_value("mode", "same process,same transaction")
        trigger.set_value("class_name", "tactic.command.RelatedTaskUpdateTrigger")
        Trigger.append_static_trigger(trigger)


        event = "change|sthpw/task|status"
        trigger = SearchType.create("sthpw/trigger")
        trigger.set_value("event", event)
        #trigger.set_value("mode", "same process,same transaction")
        trigger.set_value("class_name", "tactic.command.TaskCompleteTrigger")
        Trigger.append_static_trigger(trigger)

    add_static_triggers = classmethod(add_static_triggers)



    def get_defaults(my):
        '''specifies the defaults for this sobject'''
        pipeline_code =''
        task_process = my.get_value("process")
        parent = None
        if task_process:
            # TODO: this is slow.  Need presearch all of the parents
            parent = my.get_parent()
            if parent:
                parent_pipeline_code = parent.get_value('pipeline_code', no_exception=True)
                pipeline = Pipeline.get_by_code(parent_pipeline_code)
                if pipeline:
                    attributes = pipeline.get_process_attrs(task_process)
                    pipeline_code = attributes.get('task_pipeline')
                    if not pipeline_code:
                        node_type = attributes.get('type')
                        if node_type == "approval":
                            pipeline_code = "approval"
                        elif node_type == "task":
                            pipeline_code = "approval"




        if not pipeline_code:
            pipeline_code = 'task'

        # in case it's a subpipeline
        context = task_process
        context=my._add_context_suffix(context,task_process,parent)

        # then use the project as a parent
        project = Project.get()
        search_type = "sthpw/project"
        search_id = project.get_id()


        defaults = {
            "pipeline_code": pipeline_code,
            "project_code": Project.get_project_code(), 
            "context": context,
            "search_type": search_type,
            "search_id": search_id
        }

        if SearchType.column_exists("sthpw/task", "search_code"):
            search_code = project.get_code()
            defaults['search_code'] = search_code

        return defaults



    # Not sure why we need to have this restriction.  This restriction
    # could be put on a specific UI, but not at the lowest level.
    #def validate(my):
    #    for column in ['search_type', 'context']:
    #        if not my.get_value(column):
    #            raise SObjectValueException('%s cannot be empty for task.'%column)

    def _add_context_suffix(my,context,task_process,parent):

        if '/' in task_process:
            context = task_process.split('/')[1]


        if parent and context == task_process:
            tasks = Task.get_by_sobject(parent, task_process)

            subcontext = None
            for task in tasks:
                task_context = task.get_value("context")
                if not task_context.startswith("%s/" % context):
                    continue

                parts = task_context.split("/")
                if len(parts) == 1:
                    subcontext = None
                    continue

                subcontext = parts[1]
            try:
                if subcontext == None:
                    num = 1
                else:
                    num = int(subcontext)
                    num += 1
            except:
                num = 0

            if num:
                context = "%s/%0.3d" % (context, num)
        return context


    def get_pipeline(my):
        # for now assume the "task" pipeline if none found
        pipe_code = my.get_value("pipeline_code")
        if not pipe_code:
            pipe_code = "task"

        pipeline = Pipeline.get_by_code(pipe_code)
        if not pipeline:
            pipeline = SearchType.create("sthpw/pipeline")
            pipeline.set_value("code", pipe_code)
            pipeline.set_value("pipeline", Task.get_default_task_xml())

        return pipeline

    def get_completion(my):
        pipeline = my.get_pipeline()
        status = my.get_value("status")
        if not status:
            return 0
        process = pipeline.get_process(status)
        if not process:
            return 0

        completion = process.get_completion()
        if completion:
            return int(completion)
        else:
            return 100



    def get_name(my, long=False):
        return "%s (%s)" % (my.get_value("process"), my.get_id())
   

    def get_assigned(my):
        return my.get_value('assigned')

    def get_supervisor(my):
        return my.get_value('supervisor')

    def get_process(my):
        return my.get_value('process')


    def build_update_description(my, is_insert):
        if is_insert:
            action = "Inserted task "
        else:
            action = "Updated task "

        process = my.get_value("process")
        description = my.get_value("description")

        if my.get_value("s_status") == "__TEMPLATE__":
            msg = "Created template task: %s, %s" % (process, description)
        else:
            try:
                parent = my.get_parent()
            except Exception, e:
                print "WARNING: ", e
                parent = Project.get()
            if not parent:
                msg = "%s in %s: %s" % (action, process, description)
            else:
                msg = "%s in %s for %s (%s): %s" % (action, process, parent.get_code(), parent.get_name(), description)

        return msg


    def get_dependent_tasks(my):
        search = Search(Task)
        search.add_filter("depend_id", my.get_id() )
        tasks = search.get_sobjects()
        return tasks


    tasks_updated = None

    def update_dependent_tasks(my, top=True):
        '''for purposes of dependent tasks'''
        if top:
            Task.tasks_updated = []
            Task.tasks_updated.append(my.get_id())

        # get the dependent tasks
        tasks = my.get_dependent_tasks()

        bid_start_date = my.get_value("bid_start_date")
        bid_end_date = my.get_value("bid_end_date")

        bid_duration_unit = ProdSetting.get_value_by_key("bid_duration_unit")
        if not bid_duration_unit:
            bid_duration_unit = 'hour'

        # if there is no end date specified, return
        if not bid_end_date:
            bid_duration = my.get_value("bid_duration")
            if bid_duration and bid_start_date:
                date = Date(db=bid_start_date)
                bid_duration = float(bid_duration)
                if bid_duration_unit == 'minute':
                    date.add_minutes(bid_duration)
                else:
                    date.add_hours(bid_duration)
                bid_end_date = date.get_db_time()
            else:
                return



        for task in tasks:

            # prevent circular dependency if for some reason they occur.
            if task.get_id() in Task.tasks_updated:
                Environment.add_warning("Circular dependency", "Circular dependency with task '%s'" % task.get_id() )
                continue


            Task.tasks_updated.append(my.get_id())

            # if the dependency is fixed, update the d
            #mode = task.get_value("mode")
            mode = "depend"

            # put the start date as the end date
            if mode == "depend":

                # add one day to the end date to get the start date
                date = Date(db=bid_end_date)
                date.add_days(1)
                bid_start_date = date.get_db_time()
                task.set_value("bid_start_date", bid_start_date )

                # check if there is a duration in hours to this date
                bid_duration = task.get_value("bid_duration")
                if bid_duration:
                    bid_duration = int(bid_duration)

                    date = Date(db=bid_start_date)
                    if bid_duration_unit == 'minute':
                        date.add_minutes(bid_duration)
                    else:
                        date.add_hours(bid_duration)
                    
                    bid_end_date = date.get_db_time()

                    task.set_value("bid_end_date", bid_end_date)


                task.commit()

                task.update_dependent_tasks(False)




    def get_input_tasks(my):

        process = my.get_value("process")
        parent = my.get_parent()

        # get the pipeline
        pipeline_code = parent.get_value("pipeline_code", no_exception=True)
        if not pipeline_code:
            return []

        pipeline = Pipeline.get_by_code(pipeline_code)
        if not pipeline:
            return []

        processes = pipeline.get_input_processes(process)
        if not processes:
            return []

        tasks = []

        process_names = [x.get_name() for x in processes]

        search = Search("sthpw/task")
        search.add_filters("process", process_names)
        search.add_parent_filter(parent)
        tasks = search.get_sobjects()

        return tasks


    def get_output_tasks(my, type=None):

        process = my.get_value("process")
        parent = my.get_parent()

        # get the pipeline
        pipeline_code = parent.get_value("pipeline_code", no_exception=True)
        if not pipeline_code:
            return []

        pipeline = Pipeline.get_by_code(pipeline_code)
        if not pipeline:
            return []

        processes = pipeline.get_output_processes(process, type=type)
        if not processes:
            return []

        tasks = []

        process_names = [x.get_name() for x in processes]

        search = Search("sthpw/task")
        search.add_filters("process", process_names)
        search.add_parent_filter(parent)
        tasks = search.get_sobjects()

        return tasks







    # Static methods

    def get_by_sobjects(sobjects, process=None, order=True):

        if not sobjects:
            return []


        # quickly go through the sobjects to determine if their search types
        # are the same
        multi_stypes = False
        for sobject in sobjects:
            if sobject.get_search_type() != sobjects[0].get_search_type():
                multi_stypes = True
                break

        
        search = Search( Task.SEARCH_TYPE )
        if multi_stypes:
            # sort this into a dictionary and make multiple calls to 
            # search.add_relationship_filters
            # use the first sobject as a sample
            sobjects_dict = {}
            for sobject in sobjects:
                st = sobject.get_search_type()
                sobj_list = sobjects_dict.get(st)
                if sobj_list == None:
                    sobjects_dict[st] = [sobject]
                else:
                    sobj_list.append(sobject)

        
            search.add_op('begin')
            for key, sobj_list in sobjects_dict.items():
                search.add_op('begin')
                search.add_relationship_filters(sobj_list)
                search.add_op('and')
            search.add_op('or')



        else:

            from pyasm.biz import Schema
            schema = Schema.get()

            # FIXME: why doesn't the ops work here?
            filters = []
            search.add_relationship_filters(sobjects)
            """
            for sobject in sobjects:
                search_type = sobject.get_search_type()
                attrs = schema.get_relationship_attrs("sthpw/task", search_type)
                attrs = schema.resolve_relationship_attrs(attrs, "sthpw/task", search_type)
                search_code = sobject.get_value(attrs.get("to_col"))
                #search_code = sobject.get_value("code")
                #search.add_filter('search_type', search_type)
                #search.add_filter('search_id', search_id, quoted=False)
                #search.add_op("and")
                if attrs.get("from_col") == "search_code":
                    filters.append("search_type = '%s' and search_code = '%s'" % (search_type, search_code))
                else:
                    filters.append("search_type = '%s' and search_id = %s" % (search_type, search_code))
            search.add_where(" or ".join(filters))
            """

        search.add_order_by("search_type")

        search.add_order_by("search_code")
        search.add_order_by("search_id")



        # get the pipeline of the sobject
        pipeline = Pipeline.get_by_sobject(sobject)
        if order:
            if pipeline:
                process_names = pipeline.get_process_names(True)
                search.add_enum_order_by("process", process_names)
            else:
                search.add_order_by("process")

            search.add_order_by("id")

        if process:
           
            if isinstance(process, basestring):
                search.add_filter("process", process)
            else:
                search.add_filters("process", process)

        tasks = search.get_sobjects()
        return tasks
    get_by_sobjects = staticmethod(get_by_sobjects)


    def get_by_sobject(sobject, process=None, order=True):
        return Task.get_by_sobjects([sobject], process, order)
    get_by_sobject = staticmethod(get_by_sobject)


    def create(cls, sobject, process, description="", assigned="", supervisor="",\
            status=None, depend_id=None, project_code=None, pipeline_code='', \
            start_date=None, end_date=None, context='', bid_duration=8):


        task = SearchType.create( cls.SEARCH_TYPE )
        task.set_parent(sobject)

        task.set_value("process", process )
        task.set_value("description", description )
        if assigned:
            task.set_value("assigned", assigned)
        if supervisor:
            task.set_value("supervisor", supervisor)

        if not project_code:
            project_code = sobject.get_project_code()
        task.set_value("project_code", project_code )
        task.set_value("pipeline_code", pipeline_code) 

        if not status:
            pipeline = task.get_pipeline()
            process_names = pipeline.get_process_names()
            if process_names:
                status = process_names[0]

        if status:
            task.set_value("status", status)

        if bid_duration:
            task.set_value("bid_duration", bid_duration)


        if start_date:
            task.set_value("bid_start_date", start_date)
        if end_date:
            task.set_value("bid_end_date", end_date)
        # auto map context as process as the default
        if not context:
            context = process
        task.set_value("context", context)
        # DEPRECATED
        if depend_id:
            task.set_value("depend_id", depend_id)

        # created by 
        if task.has_value('login'):
            user = Environment.get_user_name()
            task.set_value('login', user)

        task.commit(triggers=True)
        # log the status creation event
        StatusLog.create(task, status)

        return task
    create = classmethod(create)


    def sort_tasks(tasks):
        '''sort tasks by asset/shot's pipeline'''
        if not tasks:
            return tasks
        # reorder the tasks per shot
        sorted_tasks = []

        all_shot_tasks = {} 
        key_order = []
        for task in tasks:
            id = task.get_value("search_id")
            search_type = task.get_value("search_type")
            
            key = '%s|%s' %(search_type, id)
            shot_tasks = all_shot_tasks.get(key)
            if not shot_tasks:
                shot_tasks = []
                all_shot_tasks[key] = shot_tasks

            shot_tasks.append(task)

            if key not in key_order:
                key_order.append(key)
           
        
        for key in key_order:
            shot_tasks = all_shot_tasks.get(key)
            shot_tasks = Task.sort_shot_tasks(shot_tasks)

            sorted_tasks.extend(shot_tasks)


        return sorted_tasks

    sort_tasks = staticmethod(sort_tasks)


    # FIXME: what is the difference between this function and sort_tasks above?
    def sort_shot_tasks( tasks):
        ''' sort task by pipeline. It can be for assets or shots'''
        # first sort by pipeline

        # get the pipeline of the first task
        sobject = tasks[0].get_parent()
        if not sobject:
            return tasks

        pipeline = Pipeline.get_by_sobject(sobject)
        if not pipeline:
            return tasks


        # assign a number value to each process in the pipeline
        processes = pipeline.get_process_names()
        process_dict = {}
        count = 0
        for process in processes:
            process_dict[process] = count
            count += 1

        def process_compare(x,y):
            x_process = x.get_value("process")
            y_process = y.get_value("process")
            x_value = process_dict.get(x_process)
            y_value = process_dict.get(y_process)
            return cmp(x_value, y_value)

        tasks.sort(process_compare)
        return tasks

    sort_shot_tasks = staticmethod(sort_shot_tasks)


    def add_initial_tasks(sobject, pipeline_code=None, processes=[], contexts=[], skip_duplicate=True, mode='standard',start_offset=0,assigned=None):
        '''add initial tasks based on the pipeline of the sobject'''
        from pipeline import Pipeline

        def _get_context(existing_task_dict, process_name, context=None):
            existed = False
            if not existing_task_dict:
                if context:
                    context = context
                else:
                    context = process_name
            else:

                compare_key = "%s:%s" %(process_name, context)
                max_num = 0
                for item in existing_task_dict.keys():
                    item_stripped = re.sub('/\d+$', '', item)
                    
                    #if item.startswith(compare_key):
                    if item_stripped == compare_key:
                        existing_context = item.replace('%s:'%process_name,'')
                        suffix = existing_context.split('/')[-1]
                        try:    
                            num = int(suffix)
                        except:
                            num = 0
                          
                        if num > max_num:
                            max_num = num

                        existed = True
            
         
                if existed:
                    context = "%s/%0.3d" % (context, max_num+1)
            

            return context
        # get pipeline
        if not pipeline_code:
            pipeline_code = sobject.get_value("pipeline_code")

        if pipeline_code in ['', '__default__']:
            pipeline = SearchType.create("sthpw/pipeline")
            pipeline.set_value("code", "__default__")
            pipeline.set_value("pipeline", '''
<pipeline>
    <process name='publish'/>
</pipeline>
            ''')
            # FIXME: HACK to initialize virtual pipeline
            pipeline.set_pipeline(pipeline.get_value("pipeline"))
 

        else:
            pipeline = Pipeline.get_by_code(pipeline_code)

        if not pipeline:
            print "WARNING: pipeline '%s' does not exist" %  pipeline_code
            return []

        #TODO: add recursive property here 
        if processes:
            process_names = processes
        else:
            process_names = pipeline.get_process_names(recurse=True, type=["node","approval"])


        # remember which ones already exist
        existing_tasks = Task.get_by_sobject(sobject, order=False)
    
        existing_task_dict = {}
        for x in existing_tasks:
            key1 = '%s:%s' %(x.get_value('process'),x.get_value("context"))
            existing_task_dict[key1] = True
            # for backward compatibility, if the process has been created, we will skip later below
            # we may remove this in the future
            #key2 = '%s' %(x.get_value('process'))
            #existing_task_dict[key2] = True

        # create all of the tasks
        description = ""
        tasks = []

        start_date = Date()
        start_date.add_days(start_offset)
        
        bid_duration_unit = ProdSetting.get_value_by_key("bid_duration_unit")
        if not bid_duration_unit:
            bid_duration_unit = 'hour'

        # that's the date range in 5 days (not hours)
        default_duration = 5
        default_bid_duration = 8
        if bid_duration_unit == 'minute':
            default_bid_duration = 60
        last_task = None

        # this is the explicit mode for creating task for a specific process:context combo
        if mode=='context':
            for context_combo in contexts:
                process_name, context = context_combo.split(':')               

                # depend_id is None since these are arbitrary tasks
                depend_id = None

                # first check if it already exists when skip_duplicate is True
                key1 = '%s:%s' %(process_name, context)
                task_existed = False
                for item in existing_task_dict:
                    if item.startswith(key1):
                        task_existed = True
                        break
                if skip_duplicate and task_existed:
                    continue
                process_obj = pipeline.get_process(process_name)
                if not process_obj:
                    continue

                context=_get_context(existing_task_dict,process_name, context)
                pipe_code = process_obj.get_task_pipeline()

                attrs = process_obj.get_attributes()
                duration = attrs.get("duration")
                if duration:
                    duration = int(duration)
                else:
                    duration = default_duration

                bid_duration = attrs.get("bid_duration")
                if not bid_duration:
                    bid_duration = default_bid_duration
                else:
                    bid_duration = int(bid_duration)


                end_date = start_date.copy()
                # for a task to be x days long, we need duration x-1.
                end_date.add_days(duration-1)

                
                start_date_str = start_date.get_db_date()
                end_date_str = end_date.get_db_date()

                # Create the task
                last_task = Task.create(sobject, process_name, description, depend_id=depend_id, pipeline_code=pipe_code, start_date=start_date_str, end_date=end_date_str, context=context, bid_duration=bid_duration, assigned=assigned)
                
                # this avoids duplicated tasks for process connecting to multiple processes 
                new_key = '%s:%s' %(last_task.get_value('process'), last_task.get_value("context") )
                existing_task_dict[new_key] = True
                # for backward compatibility, if the process has been created, we will skip later below

                tasks.append(last_task)
                start_date = end_date.copy()
                # start the day after
                start_date.add_days(1)

            return tasks

        
        for process_name in process_names:
            if last_task:
                depend_id = last_task.get_id()
            else:
                depend_id = None
            process_obj = pipeline.get_process(process_name)
            if not process_obj:
                continue
            attrs = process_obj.get_attributes()
            duration = attrs.get("duration")
            if duration:
                duration = int(duration)
            else:
                duration = default_duration
            bid_duration = attrs.get("bid_duration")
            if not bid_duration:
                bid_duration = default_bid_duration
            else:
                bid_duration = int(bid_duration)

            end_date = start_date.copy()
            if duration >= 1:
                # for a task to be x days long, we need duration x-1.
                end_date.add_days(duration-1)

            # output contexts could be duplicated from 2 different outout processes
            if mode == 'simple process':
                output_contexts = [process_name]
            else:
                output_contexts = pipeline.get_output_contexts(process_obj.get_name(), show_process=False)
            pipe_code = process_obj.get_task_pipeline()

            start_date_str = start_date.get_db_date()
            end_date_str = end_date.get_db_date()
            for context in output_contexts:

                # first check if it already exists when skip_duplicate is True
                key1 = '%s:%s' %(process_name, context)
                task_existed = False
                for item in existing_task_dict:
                    if item.startswith(key1):
                        task_existed = True
                        break
                if skip_duplicate and task_existed:
                    continue
                if contexts and context not in contexts:
                    continue
                context = _get_context(existing_task_dict, process_name, context)
                last_task = Task.create(sobject, process_name, description, depend_id=depend_id, pipeline_code=pipe_code, start_date=start_date_str, end_date=end_date_str, context=context, bid_duration=bid_duration,assigned=assigned)
                 
                # this avoids duplicated tasks for process connecting to multiple processes 
                new_key = '%s:%s' %(last_task.get_value('process'), last_task.get_value("context") )
                existing_task_dict[new_key] = True
                # for backward compatibility, if the process has been created, we will skip later below

                tasks.append(last_task)

            start_date = end_date.copy()
            # start the day after
            start_date.add_days(1)

        return tasks

    add_initial_tasks = staticmethod(add_initial_tasks)
            







class Timecard(SObject):

    SEARCH_TYPE = "sthpw/timecard"
    
    def get(cls, search_key, week, year, desc=None, login=None, project=None):

        search = Search(cls.SEARCH_TYPE)
        if search_key:
            search_type, search_id = search_key.split("|")
            search.add_filter('search_type',search_type)
            search.add_filter('search_id',search_id)
        if desc: # some general timecards are for minor stuff
            search.add_filter('description', desc)

        if week:
            search.add_filter('week', week)
        if year:
            search.add_filter('year', year)
        # get the current user if not specified    
        if not login:
            login = Environment.get_user_name()
        search.add_filter('login', login)

        if not project:
            project = Project.get_project_name()
        search.add_filter('project_code', project)
  
        # try getting from cache
        key = '||'.join([Timecard._get_key(search_key), str(Timecard._get_key(year)),\
            str(Timecard._get_key(week)),\
            Timecard._get_key(login), Timecard._get_key(project)])

        cached = cls.get_cached_obj(key)
        if cached != None:
            return cached
        
        sobjs = search.get_sobjects()
        
        dict = cls.get_cache_dict()

        dict[key] = sobjs
        
        return sobjs

    get = classmethod(get)
   
    def get_registered_hours(search_key, week, weekday, year, desc=None, login=None, project=None):
        ''' get the total registered hours for the week. ADD YEAR!!!'''
        timecards = Timecard.get(search_key, week, year, desc, login, project)
        
        hours = SObject.get_values(timecards, weekday, unique=False)
        
        reg_hours = 0.0
        for hour in hours:
            if hour:
                reg_hours += float(hour)
        
        return reg_hours

    get_registered_hours = staticmethod(get_registered_hours)

    # static methods
    def _get_key(value):
        ''' return a string 'NONE' if it is None'''
        if not value:
            return "NONE"
        else:
            return value

    _get_key = staticmethod(_get_key)  




class Milestone(SObject):

    def get_defaults(my):

        defaults = super(Milestone, my).get_defaults()

        project_code = my.get_value("project_code")
        if not project_code:
            project_code = Project.get_project_code()
            defaults['project_code'] = project_code


        return defaults





