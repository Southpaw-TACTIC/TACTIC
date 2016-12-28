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

__all__ = ["PipelineException", "Process", "ProcessConnect", "Pipeline", "ProjectPipeline", "Context"]

import types

from pyasm.common import Container, Base, Xml, Environment, Common, XmlException
from pyasm.search import SObject, Search, SearchType, Sql, DbContainer, SqlException
from pyasm.security import LoginGroup

from project import Project
from prod_setting import ProdSetting

class PipelineException(Exception):
    pass




class Process(Base):

    def __init__(my, node):
        my.node = node
        my.parent_pipeline_code = None
        my.parent_pipeline = None
        my.child_pipeline = None
        my.is_sub_pipeline_process = False
        #my.status_enum = None

    def __str__(my):
        return my.get_name()

    def get_node(my):
        return my.node


    def get_attributes(my):
        return Xml.get_attributes(my.node)

    def set_attribute(my, name, value):
        return Xml.set_attribute(my.node, name, value)


    def get_attribute(my, name):
        return Xml.get_attribute( my.node, name )



    def get_name(my):
        return Xml.get_attribute( my.node, "name" )


    # DEPRECATED
    def get_full_name(my):
        if my.parent_pipeline_code:
            return "%s/%s" % (my.parent_pipeline_code, my.get_name())
        else:
            return my.get_name()

    def get_type(my):
        node_type = Xml.get_attribute( my.node, "type" )
        if node_type == "auto":
            node_type = "action"
        if not node_type:
            node_type = "manual"
        return node_type

    def get_group(my):
        return Xml.get_attribute( my.node, "group" )

    def get_color(my):
        color = Xml.get_attribute( my.node, "color" )
        return color

    def get_label(my):
        return Xml.get_attribute( my.node, "label" )


    '''DEPRECATED'''
    def set_parent_pipeline_code(my, pipeline_code):
        '''FIXME: a pipeline may have multi parents'''
        my.parent_pipeline_code = pipeline_code

    '''DEPRECATED'''
    def set_parent_pipeline(my, pipeline):
        my.parent_pipeline = pipeline

    '''DEPRECATED'''
    def set_sub_pipeline_process(my, is_sub_pipe):
        my.is_sub_pipeline_process = is_sub_pipe

    '''DEPRECATED'''
    def is_from_sub_pipeline(my):
        return my.is_sub_pipeline_process

    '''DEPRECATED'''
    def set_child_pipeline(my, pipeline):
        my.child_pipeline = pipeline
   
    '''DEPRECATED'''
    def is_pipeline(my):
        return my.child_pipeline != None

    '''DEPRECATED'''
    def get_parent_pipeline(my):
        return my.parent_pipeline

    '''DEPRECATED'''
    def get_child_pipeline2(my):
        return my.child_pipeline

    '''DEPRECATED'''
    def get_child_pipeline(my):
        return my.child_pipeline


        
    def get_task_pipeline(my, default=True):
        ''' assuming the child pipeline is task related '''
        task_pipeline_code = Xml.get_attribute( my.node, "task_pipeline" )
        node_type = Xml.get_attribute(my.node, "type")
        if node_type == "approval":
            return "approval"
        elif node_type == "dependency":
            return "dependency"
        elif node_type == "progress":
            return "progress"

        if not task_pipeline_code and default:
            return "task"
        else:
            return task_pipeline_code




    def get_completion(my):
        return Xml.get_attribute( my.node, "completion" )

    def get_handler(my):
        return Xml.get_attribute( my.node, "handler" )


    def get_action_nodes(my, scope="dependent"):
        action_nodes = []
        nodes = Xml.get_children(my.node)
        for node in nodes:
            node_name = Xml.get_node_name(node)
            if node_name == "action":
                node_scope = Xml.get_attribute(node, "scope")
                if scope and node_scope != scope:
                    continue

                action_nodes.append(node)
        return action_nodes


    def get_action_node(my, event_name, scope="dependent"):
        nodes = Xml.get_children(my.node)
        for node in nodes:
            node_name = Xml.get_node_name(node)
            if node_name == "action":
                node_event = Xml.get_attribute(node, "event")
                if node_event != event_name:
                    continue

                node_scope = Xml.get_attribute(node, "scope")
                if scope and node_scope != scope:
                    continue

                return node
        
    def get_action_handler(my, event_name, scope="dependent"):
        action_node = my.get_action_node(event_name, scope=scope)
        if action_node is None:
            return None
        action_handler = Xml.get_attribute(action_node, "class")
        return action_handler



    def get_action_options(my, event_name, scope="dependent"):
        options = {}
        action_node = my.get_action_node(event_name, scope=scope)
        if action_node is None:
            return options

        nodes = Xml.get_children(action_node)
        for node in nodes:
            name = Xml.get_node_name(node)
            if name == "#text":
                continue
            value = Xml.get_node_value(node)
            options[name] = value

        return options



class ProcessConnect(Base):

    def __init__(my, node):
        my.node = node

    def get_from_expression(my, name):
        return Xml.get_attribute(my.node, name)

    def get_attr(my, name):
        return Xml.get_attribute(my.node, name)

    def get_to(my):
        return Xml.get_attribute(my.node, "to")

    def get_from(my):
        return Xml.get_attribute(my.node, "from")

    def get_name(my):
        return Xml.get_attribute(my.node, "name")

    def get_title(my):
        return Xml.get_attribute(my.node, "title")



    def get_to_pipeline(my):
        return Xml.get_attribute(my.node, "to_pipeline")

    def get_from_pipeline(my):
        return Xml.get_attribute(my.node, "from_pipeline")

    def get_to_expression(my):
        return Xml.get_attribute(my.node, "to_expression")

    def get_from_expression(my):
        return Xml.get_attribute(my.node, "from_expression")

    def get_context(my, from_xml=False):
        # if the context is not specified, use the "from" process
        context = Xml.get_attribute(my.node, "context")

        if from_xml:
            return context
        
        if not context:
            process = Xml.get_attribute(my.node, "from")

            # if the from process contains a /, then use the main context
            if process.find("/") != -1:
                parts = process.split("/")
                process = parts[1]
            context = process
                
        return context


class Pipeline(SObject):
    '''Represents a pipeline of process and their relationships'''
    SEARCH_TYPE = "sthpw/pipeline"
    def __init__(my, search_type="sthpw/pipeline", columns=None, result=None, fast_data=None):
        super(Pipeline,my).__init__(search_type, columns, result, fast_data=fast_data)


        my.processes = []
        my.recursive_processes = []
        my.connects = {}
        my.pipeline_dict = {}
        #if columns != None:
            # putting no exception here to ensure that this can be put into
            # a select widget which no uses distinct for the value column
        xml_str = my.get_value("pipeline", no_exception=True)

        # don't cache a potential empty xml when Pipeline.create() is call
        if xml_str:
            my.set_pipeline(xml_str, cache=False)

        my.process_sobjects = None


    def get_defaults(my):
        '''The default, if not specified is to set the current project'''
        defaults = {}

        project_code = Project.get_project_code()
        defaults['project_code'] = project_code

        my.on_insert()

        return defaults

 

    def on_insert(my):
        '''Function that should be run on insert/update. It's already automatically called during insert.
        On update, the caller needs to call this explicitly. It checks the search type
        this pipeline is associated with and if there is no pipeline code
        column, then update it.  It updates the process table also.'''
        search_type = my.get_value('search_type')
        my.update_process_table(search_type=search_type)

        # don't do anything for task sType
        if search_type =='sthpw/task':
            return


        if not search_type:
            return

        if ProdSetting.get_value_by_key('autofill_pipeline_code') != 'false':
            try:
                columns = SearchType.get_columns(search_type)
                if not 'pipeline_code' in columns:
                    # add the pipeline code column
                    from pyasm.command import ColumnAddCmd
                    cmd = ColumnAddCmd(search_type, "pipeline_code", "varchar")
                    cmd.execute()
            except SqlException, e:
                print "Error creating column [pipeline_code] for %" %search_type 
                pass

            # go through all of the sobjects and set all the empty ones
            # to the new pipeline
            search = Search(search_type)
            search.add_op("begin")
            search.add_filter("pipeline_code", "NULL", op='is', quoted=False)
            search.add_filter("pipeline_code", "")
            search.add_op("or")
            sobject_ids = search.get_sobject_ids()
            
            if sobject_ids:
                # this is much faster and memory efficient
                db_resource = SearchType.get_db_resource_by_search_type(search_type)
                sql = DbContainer.get(db_resource)
                tbl = search.get_table()
                sobject_ids = [str(x) for x in sobject_ids]
                pipeline_code =  my.get_value("code")
                sql.do_update('''UPDATE "%s" SET "pipeline_code" = '%s' WHERE id in (%s) ''' %(tbl, pipeline_code, ','.join(sobject_ids)))
            """
            for sobject in sobjects:    
                if not sobject.get_value("pipeline_code"):
                    sobject.set_value("pipeline_code", my.get_value("code") )
                    sobject.commit(triggers=False)
            """

    def update_process_table(my, search_type=None):
        ''' make sure to update process table'''

        template = my.get_template_pipeline()
        if template:
            if template.get_code() == my.get_code():
                template_processes = []
            else:
                template_processes = template.get_process_names()
        else:
            template_processes = []


        process_names = my.get_process_names()
        pipeline_code = my.get_code()

        search = Search("config/process")
        search.add_filter("pipeline_code", pipeline_code)
        process_sobjs = search.get_sobjects()
        existing_names = SObject.get_values(process_sobjs, 'process')

        pipeline_has_updates = False
        count = 1
        for process_name in process_names:

            exists = False
            for process_sobj in process_sobjs:
                # if it already exist, then update
                if process_sobj.get_value("process") == process_name:
                    exists = True
                    break


            if not exists:
                process_sobj = SearchType.create("config/process")

                # default to (main) for non-task status pipeline
                if search_type and search_type != 'sthpw/task':
                    process_sobj.set_value('subcontext_options', '(main)')
                process_sobj.set_value("pipeline_code", pipeline_code)
                process_sobj.set_value("process", process_name)


            # copy information over from the template
            if process_name in template_processes:
                template_attrs = template.get_process_attrs(process_name)
                process = my.get_process(process_name)
                for name, value in template_attrs.items():
                    if name in ['xpos', 'ypos', 'name']:
                        continue
                    process.set_attribute(name, value)
                    pipeline_has_updates = True



                search = Search("config/process")
                search.add_filter("process", process_name)
                # NEED ANOTHER FILTER for templates here
                search.add_filter("pipeline_code", "%/__TEMPLATE__", op="like")

                # copy certain values from the template
                template_process = search.get_sobject()
                for name, value in template_process.get_data().items():
                    if not value:
                        continue
                    if name in ['checkin_mode']:
                        process_sobj.set_value(name, value)


            
            attrs = my.get_process_attrs(process_name)
            color = attrs.get('color')
            if color:
                process_sobj.set_value("color", color)

            process_sobj.set_value("sort_order", count)
            process_sobj.commit()
            count += 1


        if pipeline_has_updates:
            my.set_value("pipeline", my.get_pipeline_xml().to_string())
            my.commit()


        # delete obsolete
        obsolete = set(existing_names) - set(process_names)
        if obsolete:
            for obsolete_name in obsolete:
                for process_sobj in process_sobjs:
                    # delete it
                    if process_sobj.get_value("process") == obsolete_name:
                        process_sobj.delete()
                        break



    def get_name(my, long=False):
        '''this is the old function, kept for backward-compatibility'''
        #TODO: remove this function here
        return my.get_code()


    def set_pipeline(my, pipeline_xml, cache=True):
        '''set the pipeline externally'''
        # cache according to pipeline code, which will share the same xml object
        if my.is_insert():
            cache = False

        search_key = my.get_search_key()

        xml_dict = Container.get("Pipeline:xml")
            
        if xml_dict == None:
            xml_dict = {}
            Container.put("Pipeline:xml", xml_dict)

        my.xml = xml_dict.get(search_key)
        
        if my.xml == None:
            my.xml = Xml()
            if cache:
                xml_dict[search_key] = my.xml

            if not pipeline_xml:
                pipeline_xml = "<pipeline/>"

            try:
                my.xml.read_string(pipeline_xml)
            except XmlException, e:
                my.xml.read_string("<pipeline/>")

        # clear these again when set externally
        my.processes = []
        my.recursive_processes = []

        # create the process and pipelines
        process_nodes = my.xml.get_nodes("pipeline/process | pipeline/pipeline")
        for node in process_nodes:
            node_name = my.xml.get_node_name(node)
            process = Process(node)
            process.set_parent_pipeline_code(my.get_code())
            my.processes.append(process)

            if node_name == "pipeline":
                name = Xml.get_attribute(node, "name")
                
                # prevent infinite loop
                if name == my.get_code():
                    continue
                    
                child = Pipeline.get_by_code(name)
                if not child:
                    continue
                my.pipeline_dict[name] = child
                process.set_child_pipeline(child)


    

    def get_pipeline_xml(my):
        return my.xml

    def to_string(my):
        return my.xml.to_string()


    def get_process(my, name):
        '''returns a Process object'''
        if type(name) not in types.StringTypes:
            name = name.get_name()

        # first try the top level
        for process in my.processes:
            if process.get_name() == name:
                return process

        # Then iterate.  This may be slow
        processes = my.get_processes(recurse=True)

        for process in processes:
            if process.get_full_name() == name:
                return process
        return None
        #raise PipelineException( "Pipeline '%s' does not have process '%s'" % \
        #    (my.get_name(),name) )


    def get_processes(my, recurse=False, type=None):
        '''returns all the Process objects in this pipeline'''

        if type and isinstance(type, basestring):
            types = [type]
        else:
            types = type

        if recurse:
            if my.recursive_processes:
                return my.recursive_processes
            else:
                # add child processes
                for process in my.processes:

                    if types and process.get_type() not in types:
                        continue

                    my.recursive_processes.append(process)

                    child_pipeline = process.get_child_pipeline()
                    if not child_pipeline:
                        continue

                    child_processes = child_pipeline.get_processes(recurse=recurse)
                    for x in child_processes:
                        x.set_sub_pipeline_process(True)
                    my.recursive_processes.extend(child_processes)
                return my.recursive_processes

        else:
            if types:
                ret_processes = []
                for process in my.processes:
                    if process.get_type() not in types:
                        continue
                    ret_processes.append(process)
                return ret_processes
            else:
                return my.processes



    def get_process_attrs(my, name):    
        process = my.get_process(name)
        if process:
            return process.get_attributes()
        else:
            return {}


    def get_process_names(my,recurse=False, type=None):
        '''returns all the Process names in this pipeline'''

        if type and isinstance(type, basestring):
            types = [type]
        else:
            types = type

        processes = my.get_processes(recurse, type=types)
        if recurse:
            process_names = []
            for process in processes:
                if types and process.get_type() not in types:
                    continue

                if process.is_from_sub_pipeline():
                    process_names.append(process.get_full_name()) 
                else:
                    process_names.append(process.get_name())
            return process_names
        else:
            return [process.get_name() for process in processes]


    def get_process_sobject(my, process):
        # search all processes and cache all of the sobject locally
        if my.process_sobjects == None:

            search = Search("config/process")        
            search.add_filter("pipeline_code", my.get_code())
            sobjects = search.get_sobjects()

            my.process_sobjects = {}

            for process_sobject in sobjects:
                # prevent changing variable process
                pcs = process_sobject.get("process")
                my.process_sobjects[pcs] = process_sobject


        process_sobject = my.process_sobjects.get(process)
        return process_sobject


    def get_process_sobjects(my):

        process_name = "dummy"

        my.get_process_sobject(process_name)

        return my.process_sobjects




    def get_index(my, name):
        index = 0
        for process in my.processes:
            if process.get_name() == name:
                return index
            index += 1



   
    def _get_connects(my, process="", direction='from'):

        if direction == "from": 
            opposite = "to"
        else:
            opposite = "from"

        if not process:
            connect_nodes = my.xml.get_nodes("pipeline/connect")
        else:
            connect_nodes = my.xml.get_nodes(\
                "pipeline/connect[@%s='%s' or @%s='*']" % (direction, process, direction))
        connects = []
        for node in connect_nodes:
            opposite_name = Xml.get_attribute(node, opposite)
            full_name = "%s/%s" % (my.get_name(), opposite_name)
            if process == opposite_name or process == full_name:
                continue
            connects.append( ProcessConnect(node) )
        return connects


    def get_input_processes(my, process, type=None, to_attr=None):
        connects = my._get_connects(process, direction='to')
        processes= []
        for connect in connects:

            if to_attr:
                connect_to_attr = connect.get_attr("to_attr")
                if connect_to_attr != to_attr:
                    continue

            from_connect = connect.get_from()
            process = my.get_process(from_connect)
            if process:
                if type and process.get_type() != type:
                    continue
                processes.append(process)

        return processes


    def get_output_processes(my, process, type=None, from_attr=None):
        connects = my._get_connects(process, direction="from")
        if not connects:
            return []

        processes = []
        for connect in connects:
            # make sure there are no empty contexts
            to = connect.get_to()

            if from_attr:
                connect_from_attr = connect.get_attr("from_attr")
                if connect_from_attr != from_attr:
                    continue


            to_pipeline = connect.get_to_pipeline()
            if to_pipeline:
                pipeline = Pipeline.get_by_code(to_pipeline)
                process = pipeline.get_process(to)

                if type and process.get_type() != type:
                    continue

                if process:
                    processes.append(process)

            else:
                process = my.get_process(to)
                if process:
                    processes.append(process)
            
        return processes
 


    def get_output_contexts(my, process, show_process=False):
        connects = my._get_connects(process, direction="from")
        if not connects:
            if show_process:
                data = (None, process)
            else:
                data = process
            return [data]

        contexts = []
        for connect in connects:
            # make sure there are no empty contexts
            context = connect.get_context()
            if not context:
                context = connect.get_to()
            
            if show_process:
                data = (connect.get_to(), context)
            else:
                data = context
            contexts.append(data)

        
        return contexts
 
    def get_input_contexts(my, process, show_process=False):
        connects = my._get_connects(process, direction='to')
        contexts = []
        for connect in connects:
            # make sure there are no empty contexts
            context = connect.get_context()
            if not context:
                context = connect.get_from()
            if show_process:
                data = (connect.get_from(), context)
            else:
                data = context
            contexts.append(data)

        return contexts
 
    def get_group(my, process_name):
        process = my.get_process(process_name)
        return process.get_group()



    def get_input_connects(my, process):
        connects = my._get_connects(process, direction="to")
        if not connects:
            return []
        else:
            return connects


    def get_output_connects(my, process):
        connects = my._get_connects(process, direction="from")
        if not connects:
            return []
        else:
            return connects



    # DEPRECATED
    def get_forward_connects(my, process):
        connects = my._get_connects(process)
        process_names = []
        for connect in connects:
            process_names.append(connect.get_to())

        return process_names


    # DEPRECATED
    def get_backward_connects(my, process):
        connects = my._get_connects(process, direction='to')

        process_names = []
        for connect in connects:
            process_names.append(connect.get_from())

        return process_names


    def get_all_contexts(my):
        connects = my._get_connects()

        contexts = []
        for connect in connects:
            context = connect.get_context()
            if context not in contexts:
                contexts.append(context)

        return contexts


    #
    # support for new pipeline methods
    #
    def get_input_snapshots(my, sobject, process_name, input_name, version='latest'):
        '''gets the snapshots of the input'''
        assert version in ['latest', 'current']

        process_node = my.xml.get_node( "pipeline/process[@name='%s']/input[@name='%s']" % (process_name, input_name))

        search_type = Xml.get_attribute(process_node, "search_type")
        context = Xml.get_attribute(process_node, "context")
        filter = Xml.get_attribute(process_node, "filter")


        # get the sobjects
        sobjects = sobject.get_all_children(search_type)

        # get the snapshots
        search = Search("sthpw/snapshot")
        search.add_filter('context', context)
        #if version == 'latest':
        #    search.add_filter("is_latest", 1)
        #elif version == 'current':
        #    search.add_filter("is_current", 1)


        # build filters for search_type, search_id combinations
        filters = []
        for sobject in sobjects:
            filter = "(\"search_type\" = '%s' and \"search_id\" = %s)" % (sobject.get_search_type(), sobject.get_id() )
            filters.append(filter)
        
        search.add_where( "( %s )" % " or ".join(filters) )

        snapshots = search.get_sobjects()
        return snapshots



    #
    # Static methods
    #

    def create(name, desc, search_type, xml=None, code=None):
        '''will only create if it does not exist, otherwise it just updates'''

        if code:
            sobject = Pipeline.get_by_code(code)
        else:
            sobject = None

        if sobject == None:
            #sobject = Pipeline( Pipeline.SEARCH_TYPE )
            sobject = SearchType.create( Pipeline.SEARCH_TYPE )
        else:
            return sobject

        if not xml:
            xml = Xml()
            xml.create_doc('pipeline')

        if isinstance(xml, basestring):
            xml_string = xml
            xml = Xml()
            xml.read_string(xml_string)

        sobject.set_value("pipeline", xml.get_xml())
        sobject.set_pipeline(xml.to_string())

        sobject.set_value('timestamp', Sql.get_default_timestamp_now(), quoted=False )
        if code:
            sobject.set_value('code', code.strip())
        sobject.set_value('name', name.strip())
        sobject.set_value('search_type', search_type)
        sobject.set_value('description', desc)
        sobject.commit()



        process_names = sobject.get_process_names()

        for i, process_name in enumerate(process_names):
            process = SearchType.create("config/process")
            process.set_value("pipeline_code", sobject.get_code() )
            process.set_value("process", process_name)
            process.set_value("sort_order", i)
            process.set_value("subcontext_options", "(main)")
            process.commit()


        return sobject

    create = staticmethod(create)
    
    def get_by_code(cls, code, allow_default=False):
        '''it is fatal not to have a pipeline, so put a default'''
        if not code:
            return None

        # first look at project specific pipeline
        pipeline = Search.get_by_code("config/pipeline", code)

        if not pipeline:
            pipeline = super(Pipeline,cls).get_by_code(code)

        if not pipeline:
            if code == 'task':
                # Create a default task pipeline
                pipeline = SearchType.create("sthpw/pipeline")
                pipeline.set_value("code", "task")
                from pyasm.biz import Task
                xml = Task.get_default_task_xml()
                pipeline.set_value("pipeline", xml)
                pipeline.set_pipeline(xml)
                pipeline.set_value("search_type", "sthpw/task")
                


            elif code == 'approval':
                # Create a default task approval pipeline
                pipeline = SearchType.create("sthpw/pipeline")
                pipeline.set_value("code", "approval")
                from pyasm.biz import Task
                xml = Task.get_default_approval_xml()
                pipeline.set_value("pipeline", xml)
                pipeline.set_pipeline(xml)
                pipeline.set_value("search_type", "sthpw/task")


            elif code == 'dependency':
                pipeline = SearchType.create("sthpw/pipeline")
                pipeline.set_value("code", "dependency")
                from pyasm.biz import Task
                xml = Task.get_default_dependency_xml()
                pipeline.set_value("pipeline", xml)
                pipeline.set_pipeline(xml)
                pipeline.set_value("search_type", "sthpw/task")
            
            elif code == 'progress':
                pipeline = SearchType.create("sthpw/pipeline")
                pipeline.set_value("code", "progress")
                from pyasm.biz import Task
                xml = Task.get_default_dependency_xml()
                pipeline.set_value("pipeline", xml)
                pipeline.set_pipeline(xml)
                pipeline.set_value("search_type", "sthpw/task")





        if not pipeline and allow_default:
            search = Search(cls)
            search.add_filter('code', 'default')
            pipeline = search.get_sobject()
            if not pipeline:
                
                pipeline = cls.create('default',  \
                    'default pipeline', '')

                xml = pipeline.get_xml_value("pipeline")

                # create a default process for the table
                root = xml.get_root_node()
                element = xml.create_element("process")
                Xml.set_attribute(element,"name", "default_process")
                Xml.append_child(root, element)

                pipeline.set_value('pipeline', xml.get_xml())
                pipeline.commit()
                
                # set the pipeline
                pipeline.set_pipeline(pipeline.get_value('pipeline'))
                Environment.add_warning("pipeline autogenerated", \
                    "[default] pipeline has just been created.")
        # Sometimes, a pipeline is instantiated without calling set_pipeline()
        # to be looked into
        if pipeline and not pipeline.get_processes():
            pipeline.set_pipeline(pipeline.get_value('pipeline'))
        return pipeline
    get_by_code = classmethod(get_by_code)
    

    # DEPRECATED
    def get_by_name(name):
        ''' for backward-compatibility, name has been renamed as code '''
        return Pipeline.get_by_code(name)
    get_by_name = staticmethod(get_by_name)

    def get_by_search_type(cls, search_type, project_code=''):
        # make sure this is a be search type
        assert search_type
        search_type_obj = SearchType.get(search_type)
        if not search_type_obj:
            return []
        search_type = search_type_obj.get_base_key()

        cache_key = "%s|%s" % (search_type, project_code)


        # commenting out until we have a full implementation of
        # project pipelines
        """
        search = Search("config/pipeline")
        if search_type:
            search.add_filter("search_type", search_type)
        search.add_project_filter(project_code)
        pipelines = cls.get_by_search(search, cache_key, is_multi=True)
        """

        
        search = Search("sthpw/pipeline")
        if search_type:
            search.add_filter("search_type", search_type)
        search.add_project_filter(project_code)
        pipelines = cls.get_by_search(search, cache_key, is_multi=True)
        if not pipelines:
            return []
        for pipe in pipelines:
            code = pipe.get_code()
            cls.cache_sobject('sthpw/pipeline|%s' %code, pipe)
        return pipelines
    get_by_search_type = classmethod(get_by_search_type)

    def get_process_name_dict(search_type, project_code='', is_group_restricted=False, sobject=None):
        '''get process names for pipelines with a particular search type'''
        pipes = []
        if sobject:
            pipe_code = sobject.get_value('pipeline_code', no_exception=True)
            if pipe_code:
                pipe = Pipeline.get_by_code(pipe_code)
                if pipe:
                    pipes = [pipe]

        if not pipes: 
            pipes = Pipeline.get_by_search_type(search_type, project_code)
        
            
        process_name_dict = {}

        my_group_names = LoginGroup.get_group_names()
        if pipes:
            for pipe in pipes:

                visible_process_names = []
                process_names = pipe.get_process_names(recurse=True)
                if is_group_restricted: 
                    for process_name in process_names:
                        group_name = pipe.get_group(process_name)
                        if group_name and group_name not in my_group_names:
                            continue
                        else:
                            visible_process_names.append(process_name)
                else:
                    visible_process_names.extend(process_names)   

                process_name_dict[pipe.get_code()] = visible_process_names

        return process_name_dict
    get_process_name_dict = staticmethod(get_process_name_dict)


    def get_default():
        return Pipeline.get_by_code("default")
    get_default = staticmethod(get_default)


    def get_process_select_data(search_type, extra_process=[], project_code='', is_filter=False, is_group_restricted=False, sobject=None ):
        '''get a tuple of data used for the SelectWdg'''
        context_dict = Pipeline.get_process_name_dict(search_type, project_code, is_group_restricted, sobject=sobject)
        labels = []
        values = []
        keys = context_dict.keys()
        keys.sort()
        process_values = Common.sort_dict(context_dict)
        for idx, value in enumerate(process_values):
            key = keys[idx]
            labels.append('&lt;&lt; %s &gt;&gt;' %key)
            if is_filter:
                # add all the process names in this pipeline into the value
                values.append(','.join(value))
            else:
                values.append('')
            # extra process may not be needed   
            if extra_process:
                value.extend(extra_process)
            
            if len(context_dict) > 1 and idx < len(context_dict)-1 :
                value.append('')

            values.extend(value)
            labels.extend(value)
        return labels, values
    get_process_select_data = staticmethod(get_process_select_data)


    def get_by_sobject(sobject, allow_default=False):
        ''' get the pipeline of the sobject'''
        pipeline_name = ''
        if not sobject:
            return None
        if sobject.has_value("pipeline_code"):
            pipeline_name = sobject.get_value("pipeline_code")
        elif sobject.has_value("pipeline"):
            pipeline_name = sobject.get_value("pipeline")
        pipeline = Pipeline.get_by_code( pipeline_name, allow_default=allow_default )
        return pipeline

    get_by_sobject = staticmethod(get_by_sobject)



    def get_template_pipeline(cls, search_type=None):
        search = Search("sthpw/pipeline")
        search.add_filter("name", "VFX Processes")
        pipeline = search.get_sobject()
        return pipeline
    get_template_pipeline = classmethod(get_template_pipeline)




    def create_pipeline_xml(cls, statuses, process_types=[], process_xpos=[], process_ypos=[]):
        '''create regular pipeline with process_types, xpos, ypos or plain task status pipeline'''
        if not statuses:
            statuses = []

        xml = []

        xml.append('''<pipeline>''')
        
        if process_types:

            for i, status in enumerate(statuses):

                if status == '':
                    continue

                process_type = process_types[i]

                if len(process_xpos) > i:
                    xpos = process_xpos[i]
                else:
                    xpos = None
                if len(process_ypos) > i:
                    ypos = process_ypos[i]
                else:
                    ypos = None

                if xpos and ypos:
                    xml.append('''  <process name="%s" type="%s" xpos="%s" ypos="%s"/>''' % (status, process_type, xpos, ypos))
                else:
                    xml.append('''  <process name="%s" type="%s"/>''' % (status, process_type))
        else:
            for status in statuses:
                if status == '':
                    continue
                xml.append('''  <process name="%s"/>''' % status)

        

        last_status = None
        for i, status in enumerate(statuses):
            if status == '':
                continue

            if i == 0 or last_status == None:
                last_status = status
                continue


            xml.append('''  <connect from="%s" to="%s"/>''' % (last_status,status))
            last_status = status

        xml.append('''</pipeline>''')
        return "\n".join(xml)

    create_pipeline_xml = classmethod(create_pipeline_xml)













class ProjectPipeline(Pipeline):

    def get_defaults(my):
        defaults = {}

        my.on_insert()

        return defaults






class Context(Base):
    '''Given a search_type and process, this class gives context info'''
    def __init__(my, search_type, process):

        my.search_type = search_type
        my.process = process

    def get_context_list(my):
        '''Get the list of contexts that can be checked in with this the search_type
            and process'''
        pipelines = Pipeline.get_by_search_type(my.search_type, Project.get_project_code() )

        if not pipelines:
            return []
        # account for sub-pipeline
        if '/' in my.process:
            my.process = my.process.split('/', 1)[1]
        contexts = []
        for pipeline in pipelines:
            pipeline_contexts = []
            pipeline_processes = pipeline.get_process_names()
            if my.process:
                if my.process not in pipeline_processes:
                    continue
                pipeline_contexts = pipeline.get_output_contexts(my.process)
            else:
                pipeline_contexts = pipeline.get_all_contexts()
            for context in pipeline_contexts:
                # for now, cut out the sub_context, until the pipeline
                # completely defines the sub contexts as well
                if context.find("/") != -1:
                    parts = context.split("/")
                    context = parts[0]

                if context not in contexts:
                    contexts.append(context)


        return contexts


