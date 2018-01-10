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
from pyasm.common import Xml, Environment, Common, SPTDate, Config
from pyasm.search import SObject, Search, SearchType, SObjectValueException
from prod_setting import ProdSetting, ProjectSetting
from pipeline import Pipeline
from pyasm.common import Environment
from project import Project
from status import StatusLog

from datetime import datetime, timedelta
from dateutil import parser
from dateutil.relativedelta import relativedelta



TASK_PIPELINE = '''
<pipeline type="serial">
  <process completion="0" color="#ecbf7f" name="Assignment"/>
  <process completion="5" color="#a96ccf" name="Waiting"/>
  <process completion="10" color="#8ad3e5" name="Pending"/>
  <process completion="20" color="#e9e386" name="In Progress"/>
  <process completion="30" color="#a96ccf" name="Need Assistance"/>
  <process completion="80" color="#e84a4d" name="Revise"/>
  <process completion="80" color="#e84a4d" name="Reject"/>
  <process completion="80" color="#e84a4d" name="Review"/>
  <process completion="100" color="#a3d991" name="Complete"/>
  <process completion="100" color="#a3d991" name="Approved"/>
</pipeline>
'''


APPROVAL_PIPELINE = '''
<pipeline type="serial">
  <process completion="0" color="#8ad3e5" name="Waiting"/>
  <process completion="10" color="#8ad3e5" name="Pending"/>
  <process completion="50" color="#e84a4d" name="Reject"/>
  <process completion="100" color="#a3d991" name="Approved"/>
  <connect to="Reject" from="Pending"/>
  <connect to="Approved" from="Pending"/>
</pipeline>

'''

MILESTONE_PIPELINE = '''
<pipeline type="serial">
  <process completion="0" color="#8ad3e5" name="Pending"/>
  <process completion="100" color="#a3d991" name="Complete"/>
  <connect to="Pending" from="Complete"/>
</pipeline>

'''



DEPENDENCY_PIPELINE = '''
<pipeline type="serial">
  <process completion="10" color="#8ad3e5" name="Pending"/>
  <process completion="20" color="#e9e386" name="In Progress"/>
  <process completion="50" color="#e84a4d" name="Reject"/>
  <process completion="100" color="#a3d991" name="Complete"/>
</pipeline>
'''

PROGRESS_PIPELINE = '''
<pipeline type="serial">
  <process completion="10" color="#8ad3e5" name="Pending"/>
  <process completion="20" color="#e9e386" name="In Progress"/>
  <process completion="50" color="#e84a4d" name="Reject"/>
  <process completion="100" color="#a3d991" name="Complete"/>
</pipeline>
'''


SNAPSHOT_PIPELINE = '''
<pipeline type="serial">
  <process completion="20" color="#e9e386" name="In Progress"/>
  <process completion="50" color="#e84a4d" name="Reject"/>
  <process completion="100" color="#a3d991" name="Final"/>
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
    "Review":   "#e84a4d",
    "Ready":    "#a3d991",
    "In_Progress":"#e9e386",
    "Cancelled":"#DDDDDD",
    "Canceled":"#DDDDDD",
    "On Hold":"#a96ccf"
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



    def get_default_snapshot_xml():
        global SNAPSHOT_PIPELINE

        from pyasm.web import Palette
        palette = Palette.get()
        xml = Xml()
        xml.read_string(SNAPSHOT_PIPELINE)
        nodes = Xml.get_nodes(xml, "pipeline/process")
        for node in nodes:
            process = Xml.get_attribute(node, "name")
            color = Task.get_default_color(process)
            if color:
                Xml.set_attribute(node, "color", color)

        return xml.to_string()
    get_default_snapshot_xml = staticmethod(get_default_snapshot_xml)






    def get_default_dependency_xml():
        global DEPENDENCY_PIPELINE

        from pyasm.web import Palette
        palette = Palette.get()
        xml = Xml()
        xml.read_string(DEPENDENCY_PIPELINE)
        nodes = Xml.get_nodes(xml, "pipeline/process")
        for node in nodes:
            process = Xml.get_attribute(node, "name")
            color = Task.get_default_color(process)
            if color:
                Xml.set_attribute(node, "color", color)

        return xml.to_string()
    get_default_dependency_xml = staticmethod(get_default_dependency_xml)

    def get_default_progress_xml():
        global PROGRESS_PIPELINE

        from pyasm.web import Palette
        palette = Palette.get()
        xml = Xml()
        xml.read_string(PROGRESS_PIPELINE)
        nodes = Xml.get_nodes(xml, "pipeline/process")
        for node in nodes:
            process = Xml.get_attribute(node, "name")
            color = Task.get_default_color(process)
            if color:
                Xml.set_attribute(node, "color", color)

        return xml.to_string()
    get_default_progress_xml = staticmethod(get_default_progress_xml)


    def get_default_milestone_xml():
        global MILESTONE_PIPELINE

        from pyasm.web import Palette
        palette = Palette.get()
        xml = Xml()
        xml.read_string(MILESTONE_PIPELINE)
        nodes = Xml.get_nodes(xml, "pipeline/process")
        for node in nodes:
            process = Xml.get_attribute(node, "name")
            color = Task.get_default_color(process)
            if color:
                Xml.set_attribute(node, "color", color)

        return xml.to_string()
    get_default_milestone_xml = staticmethod(get_default_milestone_xml)



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
        theme = Palette.get().get_theme()
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
        context = my._add_context_suffix(context, task_process, parent)

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
                if not tasks:
                    num = 0
                elif subcontext == None:
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
            Task.tasks_updated = set()
            Task.tasks_updated.add(my.get_id())

        # get the dependent tasks
        tasks = my.get_dependent_tasks()

        pipeline = my.get_pipeline()


        use_time = False
        respect_holidays = False


        # set the start date to the next day of the previous task
        prev_task = my
        prev_task_start_date = prev_task.get_datetime_value("bid_start_date")
        prev_task_end_date = prev_task.get_datetime_value("bid_end_date")

        if not use_time:
            prev_task_start_date = SPTDate.set_noon(prev_task_start_date)
            prev_task_end_date = SPTDate.set_noon(prev_task_end_date)



        # go through each dependent task
        for task in tasks:

            # prevent circular dependency if for some reason they occur.
            if task.get_id() in Task.tasks_updated:
                Environment.add_warning("Circular dependency", "Circular dependency with task '%s'" % task.get_id() )
                continue

            Task.tasks_updated.add(my.get_id())

            # get the current length of this task
            task_start_date = task.get_datetime_value("bid_start_date")
            task_end_date = task.get_datetime_value("bid_end_date")

            # if the dates are not set, then get the length from the pipeline
            if not task_start_date or not task_end_date:
                # get the length from the pipeline
                length = timedelat(days=0)
            else:
                task_length = task_end_date - task_start_date


            # set task start to 1 day after 
            new_task_start_date = prev_task_end_date + timedelta(days=1)

            if not use_time:
                new_task_start_date = SPTDate.set_noon(new_task_start_date)


            # set the task end by maintaining the previous length
            new_task_end_date = new_task_start_date + task_length


            task.set_value("bid_start_date", new_task_start_date)
            task.set_value("bid_end_date", new_task_end_date)

            task.commit()

            # recurse to the next dependent tasks
            task.update_dependent_tasks(top=False)


        return

        """
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
        """




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
            start_date=None, end_date=None, context='', bid_duration=8, \
            task_type=None, triggers=True):


        task = SearchType.create( cls.SEARCH_TYPE )
        task.set_parent(sobject)

        task.set_value("process", process )
        if description:
            task.set_value("description", description )
        if assigned != None:
            task.set_value("assigned", assigned)

        if supervisor != None:
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
        #if not context:
        #    context = process
        # let get_defaults() set the context properly instead of auto-map
        if context:
            task.set_value("context", context)

        # DEPRECATED
        if depend_id:
            task.set_value("depend_id", depend_id)

        # created by 
        if task.has_value('login'):
            user = Environment.get_user_name()
            task.set_value('login', user)

        if task_type:
            task.set_value("task_type", task_type)

        task.commit(triggers=triggers)

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


    def add_initial_tasks(sobject, pipeline_code=None, processes=[], contexts=[],
            skip_duplicate=True, mode='standard',start_offset=0,assigned=None,
            start_date=None, schedule_mode=None, parent_process=None

        ):
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
            # HACK to initialize virtual pipeline
            pipeline.set_pipeline(pipeline.get_value("pipeline"))
 

        else:
            pipeline = Pipeline.get_by_code(pipeline_code)

        if not pipeline:
            print "WARNING: pipeline '%s' does not exist" %  pipeline_code
            return []


        # get all of the processes that will have tasks
        if processes:
            process_names = processes
        else:
            process_names = pipeline.get_process_names(recurse=True, type=["node","approval", "manual", "hierarchy"])


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

        
        bid_duration_unit = ProdSetting.get_value_by_key("bid_duration_unit")
        if not bid_duration_unit:
            bid_duration_unit = 'hour'

        # that's the date range in 5 days (not hours)
        default_duration = 3
        default_bid_duration = 8 # hours
        if bid_duration_unit == 'minute':
            default_bid_duration = 60
        last_task = None




        # this is the explicit mode for creating task for a specific process:context combo
        if mode == 'context':

            start_date= SPTDate.today()
            start_date = SPTDate.add_business_days(start_date, start_offset)

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


                # for a task to be x days long, we need duration x-1.
                end_date = SPTDate.add_business_days(start_date, duration-1)

                
                start_date_str = start_date.strftime("%Y-%m-%d")
                end_date_str = end_date.strftime("%Y-%m-%d")

                # Create the task
                last_task = Task.create(sobject, process_name, description, depend_id, pipeline_code=pipe_code, start_date=start_date_str, end_date=end_date_str, context=context, bid_duration=bid_duration, assigned=assigned)
                
                # this avoids duplicated tasks for process connecting to multiple processes 
                new_key = '%s:%s' %(last_task.get_value('process'), last_task.get_value("context") )
                existing_task_dict[new_key] = True
                # for backward compatibility, if the process has been created, we will skip later below

                tasks.append(last_task)
                # start the day after
                start_date = SPTDate.add_business_days(end_date, 1)

            return tasks







        # get all of the process_sobjects
        process_sobjects = pipeline.get_process_sobjects()

        if not start_date:
            start_date = SPTDate.today()
        else:
            if isinstance(start_date, basestring):
                start_date = parser.parse(start_date)

        # set the timestamp to be noon
        start_date = SPTDate.set_noon(start_date)

        if start_offset:
            start_date = SPTDate.add_business_days(start_date, start_offset)


        # New task generator
        use_new_generator = True
        if use_new_generator:
            task_generator = TaskGenerator()
            tasks = task_generator.execute(sobject, pipeline, start_date=start_date)
            old_generator_processes = []
        else:
            old_generator_processes = process_names



        # DEPRECATED
        for process_name in old_generator_processes:

            process_sobject = process_sobjects.get(process_name)

            process_obj = pipeline.get_process(process_name)
            if not process_obj:
                continue

            process_type = process_obj.get_type()
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


            workflow = process_sobject.get_json_value("workflow") or {}


            task_creation = workflow.get("task_creation")
            if task_creation == "none":
                continue


            if process_type in ['hierarchy']:
                subpipeline_code = process_sobject.get("subpipeline_code")

                # subtasks_only, top_only, all, none 
                subtasks = []
                if task_creation in ['subtasks_only', 'all']:

                    # create the subtasks
                    if subpipeline_code:
                        subtasks = Task.add_initial_tasks(sobject, subpipeline_code, start_date=start_date, parent_process=process_name )

                    # if we only have subtasks then remap the start date to the end
                    if task_creation == "subtasks_only":
                        if subtasks:
                            start_date = subtasks[-1].get_datetime_value("bid_end_date")
                        continue


                # for both, continue as normal, but the length is that of the sub tasks
                if subtasks:
                    diff = subtasks[-1].get_datetime_value("bid_end_date") - subtasks[0].get_datetime_value("bid_start_date")
                    duration = diff.days



            task_type = None
            if process_type in ['approval']:
                task_type = "approval"



            # depend_id is pretty much deprecated ...
            # dependencies are usually set by the workflow engine
            if last_task:
                depend_id = last_task.get_id()
            else:
                depend_id = None


            # get description
            if process_sobject:
                description = process_sobject.get("description")
            else:
                description = ""



            # check to see how many weekends there are between these two dates
            if start_date.weekday() == 5:
                start_date = start_date + timedelta(days=2)
            if start_date.weekday() == 6:
                start_date = start_date + timedelta(days=1)


            # this will produce a copy
            end_date = start_date + timedelta(days=0)

            skip_weekends = True
            if skip_weekends:
                # add duration of days that aren't weekdays
                end_date = SPTDate.add_business_days(start_date, duration)
            else:
                # for a task to be x days long, we need duration x-1.
                #end_date.add_days(duration-1)
                end_date += timedelta(days=(duration-1))





            # check to see how many weekends there are between these two dates
            if end_date.weekday() == 5:
                end_date = start_date + timedelta(days=2)
            if start_date.weekday() == 6:
                end_date = start_date + timedelta(days=1)



            # output contexts could be duplicated from 2 different outout processes
            if mode == 'simple process':
                output_contexts = [process_name]
            else:
                output_contexts = pipeline.get_output_contexts(process_obj.get_name(), show_process=False)
            pipe_code = process_obj.get_task_pipeline()

            #start_date_str = start_date.get_db_date()
            #end_date_str = end_date.get_db_date()


            for context in output_contexts:

                if parent_process:
                    full_process_name = "%s/%s" % (parent_process, process_name)
                else:
                    full_process_name = process_name

                # first check if it already exists when skip_duplicate is True
                key1 = '%s:%s' %(full_process_name, context)
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

                last_task = Task.create(sobject, full_process_name, description, depend_id=depend_id, pipeline_code=pipe_code, start_date=start_date, end_date=end_date, context=context, bid_duration=bid_duration,assigned=assigned, task_type=task_type)
                 
                # this avoids duplicated tasks for process connecting to multiple processes 
                new_key = '%s:%s' %(last_task.get_value('process'), last_task.get_value("context") )
                existing_task_dict[new_key] = True
                # for backward compatibility, if the process has been created, we will skip later below

                tasks.append(last_task)

            start_date = end_date + timedelta(days=1)


        # the default was to calculate the task dates starting from the start date
        # and move forward.

        # look at project setting
        schedule_mode = ProjectSetting.get_value_by_key("schedule/mode")

        # see if there is a global schdule mode
        if not schedule_mode:
            schedule_mode = Config.get_value("schedule", "mode")

        # We can recalculae at this point using different modes
        if schedule_mode:
            cmd = TaskAutoSchedule(sobject=sobject, tasks=tasks, mode=schedule_mode)
            cmd.execute()

            # commit all of the tasks
            for task in tasks:
                task.commit()


        return tasks

    add_initial_tasks = staticmethod(add_initial_tasks)
            



class TaskAutoSchedule(object):
    '''Class to handle various auto schedule methods'''

    def __init__(my, **kwargs):
        my.kwargs = kwargs

    def get_diff_seconds(start_date, end_date):

        if isinstance(start_date, basestring):
            start = parser.parse(start_date, fuzzy=True)
        else:
            start = start_date
        if isinstance(end_date, basestring):
            end = parser.parse(end_date, fuzzy=True)
        else:
            end = end_date
        diff = end - start

        diff = (diff.days*60*60*24) + diff.seconds
        return diff
    get_diff_seconds = staticmethod(get_diff_seconds)


    def get_diff_days(start_date, end_date):
        if isinstance(start_date, basestring):
            start = parser.parse(start_date, fuzzy=True)
        else:
            start = start_date
        if isinstance(end_date, basestring):
            end = parser.parse(end_date, fuzzy=True)
        else:
            end = end_date

        diff = end - start
        diff = float(diff.days) + float(diff.seconds) / (24*60*60)
        return diff
    get_diff_days = staticmethod(get_diff_days)




    def round_second(mydate):
        
        if isinstance(mydate, basestring):
            mydate = parser.parse(mydate, fuzzy=True)

        microS = mydate.microsecond
        new_date = mydate - relativedelta(microseconds = microS)
        
        if round(microS * 0.000001) == 1:
            new_date = new_date + relativedelta(seconds = 1)
            
        return new_date
    round_second = staticmethod(round_second)


    def set_from_end_date_schedule(my, tasks, end_date):
        # make a copy
        reverse_tasks = tasks[:]
        reverse_tasks.reverse()

        tmp_end_date = end_date

        for task in reverse_tasks:

            # use the current length
            task_start_date = task.get_datetime_value("bid_start_date")
            task_end_date = task.get_datetime_value("bid_end_date")
            diff = task_end_date - task_start_date

            tmp_start_date = tmp_end_date - diff

            task.set_value("bid_end_date", tmp_end_date)
            task.set_value("bid_start_date", tmp_start_date)

            tmp_end_date = tmp_start_date





    def set_even_schedule(my, tasks, start_date, end_date):
        '''sets an even schedule for all tasks using all 24 hours.  This is a
        simple implementation that ignores the workday and is most suited
        for jobs that usually take less than a day to complete.
        '''

        num_tasks = len(tasks)

        diff = my.get_diff_seconds(start_date, end_date)
        interval = diff / float(num_tasks)


        tmp_start_date = start_date
        for task in tasks:

            tmp_end_date = tmp_start_date + relativedelta(seconds=interval)

            #print tmp_start_date, tmp_end_date
            #print round_second(tmp_start_date), round_second(tmp_end_date)
            start = my.round_second(tmp_start_date)
            end = my.round_second(tmp_end_date)

            task.set_value("bid_start_date", start)
            task.set_value("bid_end_date", end)

            tmp_start_date = tmp_end_date




    def set_even_day_schedule(my, tasks, start_date, end_date, workday=8):
        '''sets an even day schedule which ignores time.  Each task is
        given an equal number of days.  They are allowed to overlap
        a single day'''

        tmp_start_date = start_date

        diff = my.get_diff_days(start_date, end_date)
        interval = diff / float(len(tasks))

        for task in tasks:

            tmp_end_date = tmp_start_date + relativedelta(days=interval)
            start = SPTDate.set_noon(tmp_start_date)
            end = SPTDate.set_noon(tmp_end_date)
            #diff = end - start

            task.set_value("bid_start_date", start)
            task.set_value("bid_end_date", end)

            tmp_start_date = tmp_end_date



    def execute(my):

        search_key = my.kwargs.get("search_key")
        sobject = my.kwargs.get("sobject")
        tasks = my.kwargs.get("tasks")
        mode = my.kwargs.get("mode")
        if not mode:
            return

        assert mode in ['even', 'even_day', 'from_end_date']



        if sobject:
            search_key = sobject.get_search_key()
        else:
            sobject = Search.get_by_search_key(search_key)

        if not tasks:
            tasks = Search.eval("@SOBJECT(sthpw/task)", sobject)

        if not tasks:
            return


        start_date = sobject.get_datetime_value("start_date")
        end_date = sobject.get_datetime_value("due_date")

        if mode == "even":
            my.set_even_schedule(tasks, start_date, end_date)
        elif mode == "even_day":
            my.set_even_day_schedule(tasks, start_date, end_date, workday=8)
        elif mode == "from_end_date":
            my.set_from_end_date_schedule(tasks, end_date)






class TaskGenerator(object):
    '''Class to handle various auto schedule methods'''

    def __init__(my, **kwargs):
        my.kwargs = kwargs

        my.process_tasks = {}
        my.tasks = []

 

    def execute(my, sobject, pipeline, parent_process=None, start_date=None, end_date=None):

        my.sobject = sobject

        my.pipeline = pipeline
        my.process_sobjects = pipeline.get_process_sobjects()

        my.first_start_date = start_date
        my.start_date = start_date
        my.end_date = end_date
        my.parent_process = parent_process



        # remember which ones already exist
        existing_tasks = Task.get_by_sobject(sobject, order=False)
    
        my.existing_task_set = set()
        for x in existing_tasks:
            key = '%s:%s' %(x.get_value('process'),x.get_value("context"))
            my.existing_task_set.add(key)






        # TODO: handled all of thes
        #------------------
        # create all of the tasks
        description = ""
        tasks = []
        bid_duration_unit = ProdSetting.get_value_by_key("bid_duration_unit")
        if not bid_duration_unit:
            bid_duration_unit = 'hour'

        # that's the date range in 5 days (not hours)
        default_duration = 3
        default_bid_duration = 8 # hours
        if bid_duration_unit == 'minute':
            default_bid_duration = 60
        last_task = None
        #---------------------





        my.handled_processes = set()
        my._generate_tasks()

        return my.tasks



    def _get_context(my, process_name, context=None):
        existed = False
        if not my.existing_task_set:
            if context:
                context = context
            else:
                context = process_name
        else:

            compare_key = "%s:%s" %(process_name, context)
            max_num = 0
            for item in my.existing_task_set:
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





    def _generate_tasks(my):

        process_names = my.pipeline.get_process_names()

        # find all of the processes that do not have inputs
        start_processes = []
        for process_name in process_names:
            if not my.pipeline.get_input_processes(process_name):
                start_processes.append(process_name)



        for start_process in start_processes:

            # reset the start date for each start process
            my.start_date = my.first_start_date

            my.handle_process(start_process)

            my._handle_downstream_tasks(start_process)




    def _handle_downstream_tasks(my, process):

        # we have a new pipeline
        pipeline = my.pipeline
        handled_processes = my.handled_processes
        process_sobjects = my.process_sobjects


        output_processes = pipeline.get_output_process_names(process)

        for output_process in output_processes:

            # check that all inputs have been handled
            input_processes = pipeline.get_input_process_names(output_process)
            if len(input_processes) > 1:
                # find out if all the input processes have been handled
                inputs_handled = True
                for input_process in input_processes:
                    if input_process not in my.handled_processes:
                        inputs_handled = False
                        break

                if not inputs_handled:
                    continue



            if output_process in handled_processes:
                continue



            # remap the start date from the inputs and reset the end date
            if input_processes:
                last_end_date = my.first_start_date
                for input_process in input_processes:
                    last_task = my.process_tasks.get(input_process)
                    if last_task and last_task.get_datetime_value("bid_end_date") > last_end_date:
                        last_end_date = last_task.get_datetime_value("bid_end_date")
                my.start_date = last_end_date + timedelta(days=1)
            else:
                my.start_date = my.first_start_date

            my.end_date = None



            # create the tasks
            my.handle_process(output_process)


            # add process ot the handled
            handled_processes.add(output_process)

            # go to all the downstream processes
            my._handle_downstream_tasks(output_process)



    def handle_process(my, process_name):

        # we have a new pipeline
        pipeline = my.pipeline
        handled_processes = my.handled_processes
        process_sobjects = my.process_sobjects


        process_sobject = process_sobjects.get(process_name)
        process_obj = pipeline.get_process(process_name)

        workflow = process_sobject.get_json_value("workflow") or {}
        task_creation = workflow.get('task_creation')
        if task_creation == "none":
            return


        process_type = process_obj.get_type()
        attrs = process_obj.get_attributes()


        # if this process has hierarchy, then create the subtasks
        if process_type in ['hierarchy']:
            subpipeline_code = process_sobject.get("subpipeline_code")


            # subtasks_only, top_only, all, none 
            subtasks = []
            if task_creation in ['subtasks_only', 'all']:

                # create the subtasks
                subtasks = []
                if subpipeline_code:
                    subpipeline = Pipeline.get_by_code(subpipeline_code)

                    if subpipeline:
                        generator = TaskGenerator()
                        subtasks = generator.execute(my.sobject, subpipeline, start_date=my.start_date, parent_process=process_name)


                        my.tasks.extend(subtasks)



                # if we only have subtasks then store the last task from the subtasks
                if task_creation == "subtasks_only":
                    if subtasks:
                        #my.start_date = subtasks[-1].get_datetime_value("bid_end_date")

                        # store the last task 
                        last_task = subtasks[-1]
                        my.process_tasks[process_name] = last_task


                    # don't create any further tasks
                    return



        # determine if tasks are created for this process
        task_creation = workflow.get("task_creation")
        if task_creation == "none":
            return





        num_activities = 1

        bid_duration_unit = ProdSetting.get_value_by_key("bid_duration_unit")
        if not bid_duration_unit:
            bid_duration_unit = 'hour'

        # that's the date range in 5 days (not hours)
        default_duration = 3
        default_bid_duration = 8 # hours
        if bid_duration_unit == 'minute':
            default_bid_duration = 60


        # TODO: what is this for?
        last_task = None
        contexts = []
        assigned = ""
        descripton = ""
        mode = "standard"
        skip_duplicate = True


        pipeline = my.pipeline
        process_sobjects = my.process_sobjects

        for i in range(0, num_activities):

            process_sobject = process_sobjects.get(process_name)

            process_obj = pipeline.get_process(process_name)
            if not process_obj:
                continue

            process_type = process_obj.get_type()
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


            workflow = process_sobject.get_json_value("workflow") or {}



            task_type = None
            if process_type in ['approval']:
                task_type = "approval"



            # get description
            if process_sobject:
                description = process_sobject.get("description")
            else:
                description = ""



            # check to see how many weekends there are between these two dates
            if my.start_date.weekday() == 5:
                my.start_date = my.start_date + timedelta(days=2)
            if my.start_date.weekday() == 6:
                my.start_date = my.start_date + timedelta(days=1)


            # determine the start and end date of the task
            start_date = my.start_date
            end_date = my.start_date + timedelta(days=0) # make a copy

            skip_weekends = True
            if skip_weekends:
                # add duration of days that aren't weekdays
                end_date = SPTDate.add_business_days(my.start_date, duration)
            else:
                # for a task to be x days long, we need duration x-1.
                end_date += timedelta(days=(duration-1))

            # shift the end date outside of the weekend
            if end_date.weekday() == 5:
                end_date = my.start_date + timedelta(days=2)
            if start_date.weekday() == 6:
                end_date = my.start_date + timedelta(days=1)

            

            # output contexts could be duplicated from 2 different outout processes
            if mode == 'simple process':
                output_contexts = [process_name]
            else:
                output_contexts = pipeline.get_output_contexts(process_obj.get_name(), show_process=False)
            pipeline_code = process_obj.get_task_pipeline()


            for context in output_contexts:

                if my.parent_process:
                    full_process_name = "%s/%s" % (my.parent_process, process_name)
                else:
                    full_process_name = process_name

                # first check if it already exists when skip_duplicate is True
                key1 = '%s:%s' %(full_process_name, context)
                task_existed = False
                for item in my.existing_task_set:
                    if item.startswith(key1):
                        task_existed = True
                        break
                if skip_duplicate and task_existed:
                    continue




                if contexts and context not in contexts:
                    continue
                context = my._get_context(process_name, context)

                new_task = Task.create(my.sobject, full_process_name, description, pipeline_code=pipeline_code, start_date=start_date, end_date=end_date, context=context, bid_duration=bid_duration,assigned=assigned, task_type=task_type)
                 
                # this avoids duplicated tasks for process connecting to multiple processes 
                new_key = '%s:%s' %(new_task.get_value('process'), new_task.get_value("context") )
                my.existing_task_set.add(new_key)

                my.tasks.append(new_task)
                my.process_tasks[process_name] = new_task


                # set a new end_date
                my.end_date = end_date


            # set the start date to after the end_date
            #my.start_date = my.end_date + timedelta(days=1)





    def test(my):
        start_date = parser.parse("2017-01-20")
        end_date = parser.parse("2017-02-27 12:00")
        tasks = [1,2,3,4,5,6,7]
        set_even_day_schedule(tasks, start_date, end_date)






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








