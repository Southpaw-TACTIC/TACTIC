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

__all__ = ['TaskElementWdg', 'TaskElementCbk', 'TaskCheckoutManageWdg','TaskCheckinManageWdg','WorkElementWdg']

import re, time, types
from dateutil import rrule
from dateutil import parser
import datetime

from pyasm.common import jsonloads, jsondumps, Common, Environment, TacticException
from pyasm.web import WebContainer, Widget, DivWdg, SpanWdg, HtmlElement, Table, FloatDivWdg, WidgetSettings
from pyasm.biz import ExpressionParser, Snapshot, Pipeline, Project, Task, Schema
from pyasm.command import DatabaseAction
from pyasm.search import SearchKey, Search, SObject, SearchException, SearchType
from pyasm.widget import IconWdg, SelectWdg, HiddenWdg, TextWdg, CheckboxWdg
from button_wdg import ButtonElementWdg


from tactic.ui.common import BaseTableElementWdg, BaseRefreshWdg
from tactic.ui.filter import FilterData, BaseFilterWdg, GeneralFilterWdg
from tactic.ui.widget import IconButtonWdg

from table_element_wdg import CheckinButtonElementWdg, CheckoutButtonElementWdg


# sort the tasks by the processes
def get_compare(processes):
    def compare(a,b):
        a_process = a.get_value('process')
        b_process = b.get_value('process')
        
        try:
            a_index = processes.index(a_process)
        except ValueError:
            a_index = -1
        try:
            b_index = processes.index(b_process)
        except ValueError:
            b_index = -1

        if a_index > -1 and b_index > -1:
            if a_index == b_index:
                # compare context if process is the same
                a_context = a.get_value('context')
                b_context = b.get_value('context')
                return cmp(a_context, b_context)
            else:
                return cmp(a_index, b_index)

        # handle cases where process is not in pipeline
        if a_index == -1 and b_index == -1:
            return cmp(a_process, b_process)
        elif a_index != -1:
            return -1
        elif b_index != -1:
            return 1

    return compare


class TaskElementWdg(BaseTableElementWdg):
    '''simple widget which display a task value in an element'''


    ARGS_KEYS = {
    'layout': {
        'description': 'Determines layout for each process',
        'type': 'SelectWdg',
        'values': 'panel|vertical|horizontal',
        'category': 'Mode',
        'order': '01'
    },


    'show_filler_tasks': {
        'description': 'Flag to determine filler tasks are shown dynamically',
        'type': 'SelectWdg',
        'values': 'true|false',
        'category': 'Mode',
        'order': '02'
    },




    'edit_status': {
        'description': 'Flag to determine whether the status is editable',
        'type': 'SelectWdg',
        'values': 'true|false',
        'category': 'Mode',
        'order': '03'
    },
    'edit_assigned': {
        'description': 'Flag for editing the assigned user of the tasks',
        'type': 'SelectWdg',
        'values': 'true|false',
        'category': 'Mode',
        'order': '04',
    },

    'show_labels': {
        'description': 'Flag for displaying the label of the tasks',
        'type': 'SelectWdg',
        'values': 'true|false',
        'category': 'Display',
        'order': '15'
    },

    'show_border': {
        'description': 'Flag for displaying a border around each task panel',
        'type': 'SelectWdg',
        'values': 'all|one-sided|none',
        'category': 'Display',
        'order': '16'
    },


    'bg_color': {
        'description': 'Different modes of displaying the background color for each process',
        'type': 'SelectWdg',
        'values': 'status|process',
        'order': '02',
        'category': "Color"
    },

    'status_color': {
        'description': 'Different modes of displaying status background color',
        'type': 'SelectWdg',
        'values': 'status|process',
        'order': '03',
        'category': "Color"
    },
    'context_color': {
        'description': 'Different modes of displaying context background color',
        'type': 'SelectWdg',
        'values': 'status|process',
        'order': '04',
        'category': "Color"
    },
    'text_color': {
        'description': 'Text color',
        'type': 'tactic.ui.input.ColorInputWdg',
        'category': "Color",
        'order': '05'
    },
    'panel_width': {
        'description': 'Select the overall width for the panel layout',
        'type': 'SelectWdg',
        'values': '35px|50px|75px|100px|125px',
        'empty': 'true',
        'category': 'Display',
        'order': '06'
    },
    'font_size': {
        'description': 'font size of the text',
        'type': 'SelectWdg',
        'values': '7|8|9|10|11|12|13|14',
        'category': 'Display',
        'empty': 'true',
        'order': '07'
    },

    'show_process': {
        'description': 'Flag for displaying the process of the tasks',
        'type': 'SelectWdg',
        'values': 'true|false',
        'order': '08',
        'category': "Display"
    },
    'show_context': {
        'description': 'Flag for displaying the context of the tasks',
        'type': 'SelectWdg',
        'values': 'true|false',
        'order': '09',
        'category': 'Display'
    },


    'show_status': {
        'description': 'Flag for displaying the status of the tasks',
        'type': 'SelectWdg',
        'values': 'true|false',
        'order': '10',
        'category': 'Display'
    },


    'show_assigned': {
        'description': 'Flag for displaying the assigned user of the tasks',
        'type': 'SelectWdg',
        'values': 'true|false',
        'order': '10',
        'category': 'Display'
    },


    'show_bid': {
        'description': 'Flag for displaying the bid duration tasks',
        'type': 'SelectWdg',
        'values': 'true|false',
        'order': '10',
        'category': 'Display'
    },




    'assigned_label_attr': {
        'description': 'A list of | separated attributes displayed as the label of the assigned, e.g. "first_name|last_name"',
        'type': 'TextWdg',
        'order': '11',
        'category': 'Display'
    },

    'assigned_values_expr': {
        'description': '''An expression controlling what login values to show, e.g. @SOBJECT(sthpw/login['department','design'])''',
        'type': 'TextWdg',
        'order': '12',
        'category': 'Display'
    },
     

    'show_dates': {
        'description': 'Flag for displaying the date range of the tasks',
        'type': 'SelectWdg',
        'values': 'true|false',
        'order': '13',
        'category': 'Display',
    },

    'show_task_edit': {
        'description': 'Flag for displaying the edit icon for each task',
        'type': 'SelectWdg',
        'values': 'true|false',
        'order': '22',
        'category': 'Display',
    },

    'task_edit_view': {
        'description': 'A custom view specified for editing the task in this widget. Defaults to edit',
        'type': 'TextWdg',
        'default': 'edit',
        'category': 'Display',
        'order': '23'
    },

    'show_add_task': {
        'description': 'Flag for displaying the add task button even if there are existing tasks. Defaults to false',
        'type': 'SelectWdg',
        'values': 'true|false',
        'category': 'Display',
        'order': '19'
    },

    'show_link_task_menu': {
        'description': 'Flag for displaying the task linking menu so one can virtually make a task shared by two or more people. Defaults to false',
        'type': 'SelectWdg',
        'values': 'true|false',
        'category': 'Display',
        'order': '20'
    },

    'show_processes_in_title': {
        'description': 'Display the processes in title. You are advised to turn on show_filler_tasks as well. Defaults to false',
        'type': 'SelectWdg',
        'values': 'true|false',
        'category': 'Display',
        'order': '21'
    },




    'task_filter': {
        'description': 'A filter on which type of tasks to display',
        'type': 'SelectWdg',
        'values': 'process_only|context_only',
        'category': 'Display',
        'order': '24'
    },

    'show_track': {
        'description': 'Flag for displaying a tip to dynamically load the information of the last status',
        'type': 'SelectWdg',
        'values': 'true|false',
        'order': '14',
        'category': 'Display',
    },

    'show_current_pipeline_only': {
        'description': 'Flag for displaying only the tasks associate with the current pipeline. Default to true.',
        'type': 'SelectWdg',
        'values': 'true|false',
        'category': 'Display',
        'order': '18'
    }
    }

    LAYOUT_WIDTH = 130

    def init(my):
        my.label_dict = {}
        my.status_colors = {}
        my.process_colors = {}
        my._startup_tips = False
        my.tasks_dict = {}
        my.permission = {}

        my.filler_cache = None
        my.sorted_processes = []


    def get_width(my):
        if my.sobjects:
            #sobject = my.sobjects[0]
            pipeline_code = my.get_pipeline_code()
            pipeline = Pipeline.get_by_code(pipeline_code)
            if not pipeline:
                pipeline = Pipeline.get_by_code("task")
            processes = pipeline.get_process_names()
            return 120 * len(processes) + 10
        else:
            return 400


    def is_editable(cls):
        '''to avoid all those CellEditWdg'''
        return False
    is_editable = classmethod(is_editable)

    def get_onload_js(my):
        return r'''
        function init_tips(elements) {
             elements.each(function(element, index) {
                var title_attr = element.get('title')
                //var message = element.get('rel')
                if (title_attr) 
                    content = title_attr.split('::');

                var title = content[0];
                var message = content[1];

                // use the element storage functionality 
                // to store the title and text for the 
                // specified element
                element.store('tip:title', title);   
                element.store('tip:text', message);
                // remove the element title
                element.title = '';
               });
        }        
        
        
        window.addEvent('domready', function() {
            var tips = spt.Tips.get('task_track');
            if (!tips) {
                tips = new Tips('', {
                showDelay: 100,
                hideDelay: 500,
                offsets: {x: -14, y: 26},
                fixed: true
            });
            }
            var selector = '.tactic_task_tip';
            var elements = $$(selector);
            init_tips(elements);
            tips.attach(elements);
            spt.Tips.set('task_track',  tips);
        });
        '''
    def startup_tips(my, ele):
        '''add load bvr to the widget at startup or refresh'''
        ele.add_behavior({'type': 'load',
            'cbjs_action': my.get_onload_js()})
        my._startup_tips = True


    def get_searchable_search_type(my):
        '''get the searchable SType for local search'''
        return 'sthpw/task'

    def alter_task_search(my, search, prefix='children', prefix_namespace='' ):
        filter_data = FilterData.get()
        parent_search_type = my.kwargs.get('search_type')
        
        if not filter_data.get_data():
            # use widget settings
            key = "last_search:%s" % parent_search_type
            data = WidgetSettings.get_value_by_key(key)
            if data:
                filter_data = FilterData(data)
            filter_data.set_to_cgi()

        
        filter_mode_prefix = 'filter_mode'
        if prefix_namespace:
            filter_mode_prefix = '%s_%s' %(prefix_namespace, filter_mode_prefix)
        
        filter_mode = 'and'
        filter_mode_value = filter_data.get_values_by_index(filter_mode_prefix, 0)
        if filter_mode_value:
            filter_mode = filter_mode_value.get('filter_mode')
       
        if prefix_namespace:
            prefix = '%s_%s' %(prefix_namespace, prefix)
        values_list = BaseFilterWdg.get_search_data_list(prefix, \
                search_type=my.get_searchable_search_type())
        
        if values_list:
            if filter_mode != 'custom': 
                search.add_op('begin')
            GeneralFilterWdg.alter_sobject_search( search, values_list, prefix, mode='child')
            if filter_mode != 'custom' and filter_mode: 
                search.add_op(filter_mode)

        
        
        return search




    def preprocess(my):
        my._get_display_options()

        web = WebContainer.get_web()
        web_data = web.get_form_values("web_data")
        if web_data:
            try:
                web_data = jsonloads(web_data[0])
            except ValueError:
                raise TacticException("Decoding JSON has failed")

        my.assignee = []
        my.assignee_labels = []
        my.assignee_dict = {}

        my.check_access()

        # deals with assignee labels if provided
        assigned = my.kwargs.get('edit_assigned')
        my.assigned_label = None
        # e.g. first_name|last_name
        my.assigned_label_attr = my.kwargs.get('assigned_label_attr')
        my.assigned_values_expr = my.kwargs.get('assigned_values_expr')
        if not my.assigned_values_expr:
            my.assigned_values_expr = "@SOBJECT(sthpw/login['@ORDER_BY','display_name'])"

        if assigned == 'true':
            if my.assigned_label_attr:
                # maybe we can apply this filter to filter out disabled users ['license_type','is','NULL']['license_type','!=','disabled']['or']
                users = Search.eval(my.assigned_values_expr)
                user_names = [x.get_value('login') for x in users]
                my.assigned_label_attr = my.assigned_label_attr.split('|')
                my.assigned_label = [x.strip() for x in my.assigned_label_attr if x]

                if my.assigned_label:
                    for user in users:
                        user_labels = [user.get_value(x) for x in my.assigned_label]
                        label = ' '.join(user_labels)
                        my.assignee_labels.append(label)
                        my.assignee_dict[user.get_value('login')] = label
                
            else:
                users = Search.eval(my.assigned_values_expr)
                user_names = SObject.get_values(users, 'login')
                display_names = SObject.get_values(users, 'display_name')
                my.assignee_labels = display_names

            my.assignee = user_names
        else:
            if my.assigned_label_attr:
                users = Search.eval(my.assigned_values_expr)
                my.assigned_label_attr = my.assigned_label_attr.split('|')
                my.assigned_label = [x.strip() for x in my.assigned_label_attr if x]

                if my.assigned_label:
                    for user in users:
                        user_labels = [user.get_value(x) for x in my.assigned_label]
                        label = ' '.join(user_labels)
                        my.assignee_labels.append(label)
                        my.assignee_dict[user.get_value('login')] = label
                


           
           
         


        my.tasks_dict = {}

        expression = my.kwargs.get("expression")
        #expression = "@SOBJECT(connect)"
        if expression:
            my.tasks_dict = Search.eval(expression, my.sobjects, dictionary=True)
        else: 
            # get all of the tasks for all of the sobjects
            search = Search("sthpw/task")
            search.add_relationship_filters(my.sobjects)
            

            # this serves a shortcut to limit what context to show
            context = my.kwargs.get("context")
            if context:
                contexts = context.split("|")
                search.add_filters("context", contexts)


            # this serves a shortcut to limit what processes to show
            process = my.kwargs.get("process")
            if process:
                processes = process.split("|")

                search.add_filters("process", processes)



            # go thru children of main search
            search = my.alter_task_search(search, prefix='children')
            search.add_order_by("id")
            tasks = search.get_sobjects()

            schema = Schema.get()

            # process the tasks
            for task in tasks:
                search_type = task.get_value("search_type")


                supprocess = my.kwargs.get("parent_process")
                if supprocess:
                    process = task.get_value("process")
                    if not process.startswith("%s." % supprocess):
                        continue




                attrs = schema.get_relationship_attrs("sthpw/task", search_type)
                attrs = schema.resolve_relationship_attrs(attrs, "sthpw/task", search_type)
                from_col = attrs.get("from_col")

                code = task.get_value(from_col)
                key = "%s|%s" % (search_type, code)

                tasks_list = my.tasks_dict.get(key)
                if tasks_list == None:
                    tasks_list = []
                    my.tasks_dict[key] = tasks_list

                tasks_list.append(task)



        pipeline_code = my.kwargs.get("pipeline_code")
        if pipeline_code:
            pipeline_codes = [pipeline_code]
        else:
            pipeline_codes = SObject.get_values(my.sobjects, 'pipeline_code', unique=True, no_exception=True)

        # pipeline_codes can have an item that is something like $PROJECT/shot.
        # when this happens, in the eval, $PROJECT is replaced by something like 'vfx'
        # because there are quotes around it, it messes up the expression 
        # So, replace $PROJECT here, and thus, getting rid of the code
        project_code = Project.get_project_code()

        if pipeline_codes:
            # prevent expression error
            pipeline_codes = [ x.replace('$PROJECT', project_code) for x in pipeline_codes ]


        
        pipelines = Search.eval("@SOBJECT(sthpw/pipeline['code','in','%s'])" % '|'.join(pipeline_codes) )

        # remember the pipelines by code
        my.pipelines_dict = {}
        for pipeline in pipelines:
            my.pipelines_dict[pipeline.get_code()] = pipeline


        # get all of the processes that appear in all the pipelines, without duplicates
        my.all_processes_set = set()
        # ^ that's what the pipeline column should display (each process in the pipeline)

        # the default pipeline is the longest pipeline in the table
        # this is so that the processes appear in the right order.
        # all other processes should follow after this
        default_pipeline = []

        
        if pipelines:
            for pipeline in pipelines:
                processes = pipeline.get_processes(type=[
                        "node",
                        "approval",
                        "hierarchy",
                        #"dependency",
                        "progress"
                ])

                # if this pipeline has more processes than the default, make this the default
                if len(processes) > len(default_pipeline):
                    default_pipeline = processes
                pipeline_code = pipeline.get_code()
                my.label_dict[pipeline_code] = {}
                for process in processes:

                    # put the processes found into a set to avoid duplicates.
                    my.all_processes_set.add(process.get_name())
                    process_dict = my.label_dict.get(pipeline_code)
                    process_dict[process.get_name()] = process.get_label() 

            # sort the processes, so that the task appears in the right order
            default_pipeline_processes = []

            # get an list of all the processes, in order
            default_pipeline_processes = [x.get_name() for x in default_pipeline]

            



            # this will add every process in default pipeline to sorted processes 
            # (in the correct order)
            for item in default_pipeline_processes:
                for process in my.all_processes_set:
                    if item == process:
                        my.sorted_processes.append(item)
            

            # add everything else not in the default pipeline after
            for process in my.all_processes_set:
                if process not in my.sorted_processes:
                    my.sorted_processes.append(process)

            # Note: my.sorted_processes should now contain all the processes found on
            # this load of this class, in order. However, if it's not the initial load,
            # not all processes may be present

            # go to the HTML and grab the list of processes stored in the header of the table.
            # this will provide a complete list of everything that's been loaded already
            if web_data and web_data[0].get("process_data"):
                process_data_json = web_data[0].get("process_data")
                try:
                    process_data_list = jsonloads(process_data_json)
                except ValueError:
                    raise TacticException("Decoding JSON has failed")
                process_data_list = process_data_list['processes']
                
                if len(process_data_list) > len(my.sorted_processes):
                    my.sorted_processes = process_data_list

                # combine this list with the newly generated list.
                for process in process_data_list:
                    if process not in my.sorted_processes:
                        my.sorted_processes.append(process)


        task_pipelines = Search.eval("@SOBJECT(sthpw/pipeline['search_type','sthpw/task'])")
        task_pipelines.append( Pipeline.get_by_code("task") )
        task_pipelines.append( Pipeline.get_by_code("approval") )
        task_pipelines.append( Pipeline.get_by_code("dependency") )
        if task_pipelines:
            for task_pipeline in task_pipelines:
                processes = task_pipeline.get_processes()
                pipeline_code = task_pipeline.get_code()
                my.status_colors[pipeline_code] = {}
                for process in processes:
                    process_dict = my.status_colors.get(pipeline_code)
                    color = process.get_color()
                    #if color:
                    process_dict[process.get_name()] = color
       
        # ensured all status_colors are filled with by cascading to task or
        # default built in color
        for task_pipeline in task_pipelines:
            task_pipeline_code = task_pipeline.get_code()
            status_colors = my.status_colors.get(task_pipeline_code)
            if status_colors:
                for key, value in status_colors.items():
                    color = value
                    if not color:
                        task_status_colors = my.status_colors.get("task")
                        color = task_status_colors.get(key)
                    if not color:
                        color = Task.get_default_color(key)
                    status_colors[key] = color
        
        
        security = Environment.get_security()
        my.allowed_statuses = []
        for pipeline_code, color_dict in my.status_colors.items():
            existing_statuses = color_dict.keys()
            # check security access

            for status in existing_statuses:
                if status in my.allowed_statuses:
                    continue
                
                access_key = [
                    {'process': '*' ,'pipeline':  pipeline_code},
                    {'process': '*' ,'pipeline':  '*'},
                    {'process': status , 'pipeline':  pipeline_code}
                    ]
                if security.check_access('process', access_key, "view", default="deny"):
                    my.allowed_statuses.append(status)

        if my.sobjects:
            # these are the items in the table being displayed. ie: shots in shot table
            search_type = my.sobjects[0].get_base_search_type()
            if search_type:
                sobj_pipelines = Search.eval("@SOBJECT(sthpw/pipeline['search_type','%s'])" %search_type)
                if sobj_pipelines:
                    for sobj_pipeline in sobj_pipelines:
                        processes = sobj_pipeline.get_processes()
                        pipeline_code = sobj_pipeline.get_code()
                        my.process_colors[pipeline_code] = {}
                        for process in processes:
                            process_dict = my.process_colors.get(pipeline_code)
                            process_dict[process.get_name()] = process.get_color()





    def handle_layout_behaviors(my, layout):

        # add the accept behavior

        layout.add_behavior( {
        "type": "load",
        "cbjs_action": '''
spt.task_element = {}

bvr.src_el.addEvent('change:relay(.spt_task_status_select)',
    function(evt, src_el) {
        spt.task_element.status_change_cbk(evt, {src_el: src_el} );
    } )

spt.task_element.status_change_cbk = function(evt, bvr) {

    // set the value of the data item
    var all_top_el = bvr.src_el.getParent(".spt_all_task_top");
    var value_wdg = all_top_el.getElement(".spt_data");

    var new_values = {}
    if (value_wdg.value) {
        new_values = JSON.decode(value_wdg.value)
    }
    new_values[bvr.src_el.name] = bvr.src_el.value

    var value = JSON.stringify(new_values);
    value_wdg.value = value


    var layout = bvr.src_el.getParent(".spt_layout");
    var version = layout.getAttribute("spt_version");
    if (version == "2") {
        spt.table.set_layout(layout);
        spt.table.accept_edit(all_top_el, value, false, {ignore_multi: true});
    }
    else {
        var cached_data = {};
        spt.dg_table.edit.widget = all_top_el;
        spt.dg_table.inline_edit_cell_cbk( value_wdg, cached_data );
    }
}
        ''' } )
      

        layout.add_smart_styles("spt_task_status_select", {
            "position": "relative",
            "font-size": "%spx" % (my.font_size-1),
            "color": "black",
            #"margin": "2px 2px 6px 0"
            } )
        # This is done per item and can't be done at the global level
        #table.add_style("spt_task_status_select", "background-color: %s" %bgColor)

        # handle adding of tasks
        layout.add_relay_behavior( {
        'type': 'mouseup',
        #'search_key_list': [sobject.get_search_key()],
        'bvr_match_class': "spt_task_element_add_task",
        'cbjs_action': '''
        var search_key = bvr.src_el.getAttribute("spt_search_key");
        bvr.search_key_list = [search_key];
        spt.dg_table.gear_smenu_add_task_selected_cbk(evt,bvr);
        '''
        } )


       

        # handle add initial tasks
        layout.add_relay_behavior( {
        "type": "mouseup",
        'bvr_match_class': "spt_task_initial_tasks",
        "cbjs_action": '''
        var all_top_el = bvr.src_el.getParent(".spt_all_task_top");
        var value_wdg = all_top_el.getElement(".spt_data");
        var value = {
            'add_initial_tasks': bvr.src_el.value
        }
        value = JSON.stringify(value);
        value_wdg.value = value;

        // set the checkbox
        if (bvr.src_el.checked == true) {
            bvr.src_el.checked = false;
        }
        else {
            bvr.src_el.checked = true;
        }

        var layout = bvr.src_el.getParent(".spt_layout");
        var version = layout.getAttribute("spt_version");
        if (version == "2") {
            spt.table.set_layout(layout);
            spt.table.accept_edit(all_top_el, value, false);
        }
        else {
            var cached_data = {};
            spt.dg_table.edit.widget = all_top_el;
            spt.dg_table.inline_edit_cell_cbk( value_wdg, cached_data );
        }
        '''
        } ) 

        
        # handle assigned selector
        layout.add_relay_behavior( {
        "type": "change",
        'bvr_match_class': "spt_task_element_assigned",
        "cbjs_action": '''
        var all_top_el = bvr.src_el.getParent(".spt_all_task_top");
        var values = spt.api.Utility.get_input_values(all_top_el,'.spt_task_status_select', false);
        var value_wdg = all_top_el.getElement(".spt_data");
        value_wdg.value = JSON.stringify(values);
        spt.dg_table.edit.widget = all_top_el;
        spt.dg_table.inline_edit_cell_cbk( value_wdg, {} );
        '''
        } ) 

        if my.show_link_task_menu:
            my.menu.set_activator_over(layout, "spt_task_element_assigned")
            #my.menu.set_activator_out(layout, "spt_all_task_top")
            my.menu.set_activator_out(layout, "spt_task_element_assigned")



    def get_pipeline_code(my):
        pipeline_code = my.kwargs.get("pipeline_code")

        if not pipeline_code:
            sobject = my.get_current_sobject()
            pipeline_code = sobject.get_value("pipeline_code", no_exception=True)

        return pipeline_code




    def get_title(my):
        
        # If for all sObjects in table, no processes
        # exists, display null title "Tasks".
        if not my.sorted_processes:
            return "Tasks"

        if my.show_processes_in_title == 'true':
            table = Table()
            table.add_style("margin-top: 4px")

            sobject = my.get_current_sobject()
            if not sobject:
                return "Tasks"
            
            if my.layout in ['horizontal','panel']:

                pipeline_code = my.get_pipeline_code()
                if pipeline_code:
                    pipeline = Pipeline.get_by_code(pipeline_code)
                    if not pipeline:
                        pipeline = Pipeline.get_by_code("task")

                    processes = pipeline.get_process_names()
                else:
                    processes = ['publish']

                
                table.add_row()



                for process in my.sorted_processes:
                    title = Common.get_display_title(process)
                    td = table.add_cell(title)
                    td.add_style("width: 117px")
                    td.add_style("text-align: center")
                    td.add_style("font-weight: bold")
                    td.add_attr("process", process)

                return table
            else:
                return "Tasks"
        else:
            return "Tasks"


    def handle_th(my, th, wdg_idx=None):
        th.add_attr('spt_input_type', 'inline')

        hidden = HiddenWdg('process_data')
        hidden.add_class('spt_process_data')

        header_data = {'processes': my.sorted_processes}
        header_data = jsondumps(header_data).replace('"', "&quot;")
        hidden.set_value(header_data, set_form_value=False )

        th.add(hidden)


        if my.show_link_task_menu:
            # handle finger menu
            my.top_class = "spt_task_status_menu"
            from tactic.ui.container import MenuWdg, MenuItem
            my.menu = MenuWdg(mode='horizontal', width = 25, height=20, top_class=my.top_class)


            menu_item = MenuItem('action', label=IconWdg("Add User", IconWdg.ADD))
            my.menu.add(menu_item)
            menu_item.add_behavior( {
                'type': 'click_up',
                'cbjs_action': '''
                var menu = spt.table.get_edit_menu(bvr.src_el);
                var activator =  menu.activator_el; 
                parent = activator.getParent();
                if (activator.name.indexOf("|DELETE") != -1) {
                    activator.name = activator.name.replace("|DELETE", "|COPY");
                    var select = parent.getElement(".spt_task_element_assigned");
                    select.name = select.name.replace("|DELETE", "|COPY");
                    parent.setStyle("opacity", "1.0");
                }
                else if (activator.name.indexOf("|COPY") != -1) {
                    var clone = spt.behavior.clone(parent);
                    clone.inject(parent, 'after');
                    var select = clone.getElement(".spt_task_element_assigned");
                    select.value = '';
                    var rnd = Math.floor(Math.random()*100001)
                    select.name = select.name + rnd;

                    spt.task_element.status_change_cbk(evt, {src_el: select});
                }
                else {
                    var clone = spt.behavior.clone(parent);
                    clone.inject(parent, 'after');
                    var select = clone.getElement(".spt_task_element_assigned");
                    select.value = '';
                    var rnd = Math.floor(Math.random()*100001)
                    //select.name = select.name + "|COPY" + rnd;
                    select.name = select.name + "_" + rnd;
                    select.name = select.name.replace("|EDIT", "|COPY");

                    spt.task_element.status_change_cbk(evt, {src_el: select});
                }
                '''
            } )



            menu_item = MenuItem('action', label=IconWdg("Remove User", IconWdg.DELETE) )
            my.menu.add(menu_item)
            menu_item.add_behavior( {
                'type': 'click_up',
                'cbjs_action': '''
                var menu = spt.table.get_edit_menu(bvr.src_el);
                var activator =  menu.activator_el; 
                parent = activator.getParent();
                parent.setStyle("opacity", "0.2");

                var select = parent.getElement(".spt_task_element_assigned");
                select.value = '';
                select.name = select.name.replace("|EDIT", "|DELETE");

                spt.task_element.status_change_cbk(evt, {src_el: activator});

                //clone_sobject(search_key, {})
                '''
            } )


            widget = DivWdg()
            widget.add_class(my.top_class)
            widget.add_styles('position: absolute; display: none; z-index: 1000')
            widget.add(my.menu)
            th.add(widget)

 


    def handle_td(my, td):
        # This is for old table
        td.add_attr('spt_input_type', 'tasks')

        # this is for new fast table
        td.add_class("spt_input_inline")


    def get_text_value(my):
        tasks = my.get_tasks()
    
        values = []
        for task in tasks:
            group = []
            group.append(task.get_value('context'))
            group.append(task.get_value('status'))
            group.append(task.get_value('assigned'))
            values.append(':'.join(group))
        return ",".join(values)
            

    def get_tasks(my, sobject=None, pipeline_code=None):
        tasks = my._get_tasks(sobject=None, pipeline_code=None)
        #tasks = my._get_tasks(sobject=None, pipeline_code="PIPELINE00110")
        return tasks

    def _get_tasks(my, sobject=None, pipeline_code=None):
        #my.preprocess()
        security = Environment.get_security()
        project_code = Project.get_project_code()

        if not sobject:
            sobject = my.get_current_sobject()

        # If this is the insert table, then there will be no tasks
        if sobject.is_insert():
            return []

        # use parent?
        #sobject = sobject.get_parent()

        search_type = sobject.get_search_type()

        schema = Schema.get()
        attrs = schema.get_relationship_attrs("sthpw/task", search_type)
        attrs = schema.resolve_relationship_attrs(attrs, "sthpw/task", search_type)
        to_col = attrs.get("to_col")
        code = sobject.get_value(to_col)
        #search_type = sobject.get_search_type()
        #search_id = sobject.get_id()
        key = "%s|%s" % (search_type, code)

        tasks = my.tasks_dict.get(key)
        if tasks == None:
            tasks = []


        # get the pipeline
        if not pipeline_code:
            pipeline_code = my.get_pipeline_code()

        if pipeline_code:
            pipeline = Pipeline.get_by_code(pipeline_code)
        else:
            pipeline = None

        if pipeline:
            processes = pipeline.get_process_names()

            supprocess = my.kwargs.get("parent_process")
            if supprocess:
                processes = ["%s.%s" % (supprocess, x) for x in processes]

            processes_remove = []
            for process in processes:
                keys = [
                        { "process": process },
                        { "process": "*" },
                        { "process": process, "project": project_code },
                        { "process": "*", "project": project_code }
                ]
                if not security.check_access("process", keys, "allow", default="deny"):
                    processes_remove.append(process)
            for process in processes_remove:
                processes.remove(process)

            # filter by current pipeline's processes
            # show_current_pipeline_only is not in task_filter since
            # process_only and show_current_pipeline_only are not mutually exclusive
            show_current_pipeline_only = my.kwargs.get('show_current_pipeline_only') != 'false'
            if show_current_pipeline_only:
                filtered_tasks = []
                for task in tasks:
                    process = task.get_value('process')
                    if process in processes:
                        filtered_tasks.append(task)
                tasks = filtered_tasks
            if my.task_filter == 'process_only':
                filtered_tasks = []
                for task in tasks:
                    if task.get_value('process') != task.get_value('context'):
                        continue
                    filtered_tasks.append(task)
                tasks = filtered_tasks
            elif my.task_filter == 'context_only':
                filtered_tasks = []
                for task in tasks:
                    if task.get_value('process') == task.get_value('context'):
                        continue
                    filtered_tasks.append(task)
                tasks = filtered_tasks

            tasks = sorted(tasks,get_compare(processes))

        else:
            def compare(a,b):
                a_context = a.get_value('process')
                b_context = b.get_value('process')
                return cmp(a_context, b_context)

            tasks = sorted(tasks,compare)





        # fill in any missing tasks
        pipeline_code = my.get_pipeline_code()
        pipeline = Pipeline.get_by_code(pipeline_code)
        show_filler_tasks = my.kwargs.get("show_filler_tasks")
        if pipeline and show_filler_tasks in ["true", True]:

            processes = pipeline.get_process_names(type=["node","approval","hierarchy","dependency"])

            if my.filler_cache == None:
                my.filler_cache = {}

            # get all of the current tasks processes
            existing_processes = [x.get_value("process") for x in tasks]


            supprocess = my.kwargs.get("parent_process")

            for process in processes:

                if supprocess:
                    full_process = "%s.%s" % (supprocess, process)
                else:
                    full_process = process

                # skip processes that already have tasks
                if full_process in existing_processes:
                    continue

                process_pipeline = pipeline
                process_obj = process_pipeline.get_process(process)

                if not process_obj:
                    #print("WARNING: process[%s] not in pipeline [%s]" % (process, pipeline.get_code()))
                    continue


                task_pipeline = process_obj.get_task_pipeline()



                task = SearchType.create("sthpw/task")
                task.set_value("process", full_process)
                task.set_value("context", full_process)
                if task_pipeline:
                    task.set_value("pipeline_code", task_pipeline)

                my.filler_cache[full_process] = task

            missing = []
            task_processes = [x.get_value("process") for x in tasks]
            for process in processes:
                if supprocess:
                    full_process = "%s.%s" % (supprocess, process)
                else:
                    full_process = process

                if full_process not in task_processes:
                    missing.append(full_process)

            search_type = sobject.get_search_type()
            search_code = sobject.get_value("code")
            for process in missing:
                task = my.filler_cache.get(process)
                # FIXME: task could be None
                if task:
                    task.set_value("search_type", search_type)
                    task.set_value("search_code", search_code)
                    tasks.append(task)
        

            tasks = sorted(tasks,get_compare(processes))

        return tasks



    def _get_display_options(my):
       
        # this is used only for horizontal layout
        # NOTE: total_width is no longer used
        my.total_width = 0
        my.panel_width = my.kwargs.get("panel_width")
        my.show_border = my.kwargs.get("show_border")
        my.show_process = my.kwargs.get("show_process")
        my.show_context = my.kwargs.get("show_context")
        my.show_task_edit = my.kwargs.get("show_task_edit")
        my.task_edit_view = my.kwargs.get("task_edit_view")

        my.show_processes_in_title = my.kwargs.get("show_processes_in_title")
        if not my.show_processes_in_title:
            my.show_processes_in_title = 'false'

        if not my.show_process:
            my.show_process = 'true'
        if not my.show_context:
            my.show_context = 'false'

        if not my.show_task_edit:
            my.show_task_edit = 'false'
        if not my.task_edit_view:
            my.task_edit_view = 'edit'


        my.show_dates = my.kwargs.get("show_dates")
        if not my.show_dates:
            my.show_dates = "true"

        my.show_status = my.kwargs.get("show_status")
        if not my.show_status:
            my.show_status = "true"
        my.show_assigned = my.kwargs.get("show_assigned")
        if not my.show_assigned:
            my.show_assigned = "true"
        my.edit_assigned = my.kwargs.get("edit_assigned")
        if not my.edit_assigned:
            my.edit_assigned = "false"
       
           

        my.text_color = my.kwargs.get('text_color')

        if not my.show_border:
            my.show_border = 'one-sided'
        
        my.show_labels = my.kwargs.get("show_labels")
        my.show_track = my.kwargs.get("show_track")
        my.show_add_task = my.kwargs.get("show_add_task") == 'true'
        my.show_link_task_menu = my.kwargs.get("show_link_task_menu") == 'true'
       
        # handle the color
        my.status_color_mode = my.kwargs.get("status_color")
        my.context_color_mode = my.kwargs.get("context_color")
        my.bg_color_mode = my.kwargs.get("bg_color")
        '''
        if not status_color_mode:
            status_color_mode = 'status'
        if not context_color_mode:
            context_color_mode = 'process'
        '''

        if not my.show_labels:
            my.show_labels = 'false'


        my.font_size = my.kwargs.get("font_size")
        if not my.font_size:
            my.font_size = 12
        else:
            my.font_size = int(my.font_size)

        my.edit_status = my.kwargs.get("edit_status") == 'true'
        my.layout = my.kwargs.get("layout")
        if not my.layout:
            my.layout = 'panel'
        if my.layout in ['horizontal','vertical']:
            if my.show_process =='true':
                if my.layout == 'vertical':
                    my.total_width += my.LAYOUT_WIDTH
                else:
                    my.total_width += 75

            if my.show_context =='true':
                my.total_width += 75 
            if my.show_dates =='true':
                if my.layout == 'vertical':
                    my.total_width += my.LAYOUT_WIDTH
                elif my.font_size < 10:
                    my.total_width += 50
                else:
                    my.total_width += 75 

            if my.show_assigned == 'true':
                if my.show_task_edit == 'true':
                    my.total_width += 250
                else:
                    my.total_width += 120
            if my.show_labels =='true':
                my.total_width += 75 
            if my.show_track =='true':
                my.total_width += 25
            # editable select takes more width
            if my.show_status == 'true':
                if my.edit_status:
                    my.total_width += 100
                else:
                    my.total_width += 75

        my.task_filter = my.kwargs.get('task_filter')



    def get_display(my):
       
        # Check if pipeline exists
        pipeline_code = my.get_pipeline_code()
        pipeline = None
        if pipeline_code:
            pipeline = Pipeline.get_by_code(pipeline_code)
        if not pipeline:
            no_pipeline_div = DivWdg()
            icon = IconWdg("WARNING", IconWdg.WARNING)
            no_pipeline_div.add(icon)
            no_pipeline_div.add("<b>You must select a pipeline to manage tasks.</b>")
            no_pipeline_div.add("<br/>"*2)
            return no_pipeline_div 
        
 
        sobject = my.get_current_sobject()
        my.tasks = my.get_tasks(sobject)

        div = DivWdg()
        div.add_style("margin: -4px auto")

        # initialize tool tips only if show track is true
        if my.show_track == 'true' and not my._startup_tips:
            my.startup_tips(div)
        div.add_class("spt_all_task_top")
        div.add_style("white-space: nowrap")
        my.width = '100px'
        # this is more for layout = panel
        if my.panel_width:
            my.width = my.panel_width

        pipeline_code = my.get_pipeline_code()

        # This should still show the tasks even if not pipeline is defined
        """
        if not pipeline_code:
            div.add_style("padding: 3px")

            icon = IconButtonWdg(icon=IconWdg.ADD, tip="Add Pipeline Tasks")
            div.add(icon)
            icon.add_style("float: right")
            icon.add_attr("spt_search_key", sobject.get_search_key() )
            icon.add_class("spt_task_element_add_task")

            div.add('<i>No pipeline defined</i>')
            div.add_style("opacity: 0.5")
            return div
        """



        parent_key =  SearchKey.get_by_sobject(sobject, use_id=True)
        from pyasm.common import Environment
        security = Environment.get_security()
        
        if sobject.is_insert():
            div.add_style("padding: 3px")
            div.add_style("opacity: 0.7")
            checkbox = CheckboxWdg("whatever")
            checkbox.add_class("spt_task_initial_tasks")
            div.add( checkbox )
            div.add( " <i>Add tasks in pipeline</i>")

        
        elif not my.tasks:
            
            show_current_pipeline_only = my.kwargs.get('show_current_pipeline_only') != 'false'
            label = Table()
            label.add_color("color", "color")
            label.add_class("hand")
            label.add_row()
            label.add_styles("opacity: 0.5;font-size: 10px;margin-left: 5px")

            if security.check_access("search_type", {"code":"sthpw/task"}, "insert", default="insert"):
                label.add_class("spt_task_element_add_task")
                label.add_attr("spt_search_key", sobject.get_search_key() )
                icon = IconWdg("Add Tasks", IconWdg.ADD)
                label.add_cell(icon)
            
                if show_current_pipeline_only:
                    td = label.add_cell('<i>No tasks for current pipeline. Click to Add</i>')
                else:
                    td = label.add_cell('<i>No tasks found. Click to Add</i>')

            else:
                if show_current_pipeline_only:
                    td = label.add_cell('<i>No tasks for current pipeline. Need permission to add.</i>')
                else:
                    td = label.add_cell('<i>No tasks found. Click to Add</i>')


            td.add_style("padding: 5px")
            td.add_style("min-width: 150px")

            div.add(label)
            div.add_style("opacity: 0.8")
        else:
            # reset to make these into lists
            items = []
            last_process_context = None
            item = None
            for idx, task in enumerate(my.tasks):
                process = task.get_value("process")
                context = task.get_value("context")
                process_context = '%s:%s' %(process, context)

                if last_process_context == None:
                    item = []
                    items.append(item)
                    item.append(task)
                elif last_process_context == process_context:
                    item.append(task)
                else:
                    item = []
                    items.append(item)
                    item.append(task)

                last_process_context = process_context


            table = Table(css='minimal')
            table.add_style("border-width: 2px")
            table.add_style('border-collapse: collapse')
            table.add_row()

            project_code = Project.get_project_code()

            last = len(items) - 1
            pipeline_code = my.kwargs.get("pipeline_code")
            if not pipeline_code:
                pipeline_code = sobject.get("pipeline_code")

            pipeline_code = pipeline_code.replace("$PROJECT", project_code)
            pipeline = Search.eval("@SOBJECT(sthpw/pipeline['code','%s'])" % pipeline_code)
            pipeline_processes = []

            if pipeline:
                pipeline_processes = pipeline[0].get_processes()


            # all the processes to be drawn so that the user can see it
            pipeline_processes_list = []

            for pipeline_process in pipeline_processes:
                pipeline_processes_list.append(pipeline_process.get_name())

            # if the sobject/pipeline has no tasks.  Items are just lists of tasks
            if not items:
                # draw a div giving a warning of no items
                error_div = DivWdg("Error. There were no tasks found. If reloading the page doesn't fix the issue, please contact the system administrator.")
                td = table.add_cell()
                td.add(error_div)

            else:
                supprocess = my.kwargs.get("parent_process")

                # go through each sorted process
                for idx, process in enumerate(my.sorted_processes):

                    if supprocess:
                        process = "%s.%s" % (supprocess, process)

                    if my.layout in ['vertical']:
                        table.add_row()
                    td = table.add_cell()
                    td.add_style("vertical-align: top")
                    last_one = False
                    if idx == last:
                        last_one = True

                    # determins whether or not the task should be displayed.
                    is_task_displayed = False

                    # go through each list of tasks
                    for task_list in items:

                        # check if this process in any of the tasks lists
                        if task_list and (process == task_list[0].get_value("process")):
                            tasks = task_list
                            is_task_displayed = True
                            break

                    if not is_task_displayed:
                        # none of the tasks lists are in the process
                        tasks = items[0]



                    if pipeline_code:
                        pipeline = my.pipelines_dict.get(pipeline_code)
                    else:
                        pipeline = None


                    #task = tasks[0]
                    #process = task.get_value("process")


                    process_obj = pipeline.get_process(process)
                    if process_obj:
                        node_type = process_obj.get_type()
                    else:
                        node_type = "node"


                    # make the task slightly opaque
                    if node_type in ['manual', 'node','approval'] and tasks[0].get_id() == -1:
                        td.add_style("opacity: 0.5")


                    if is_task_displayed or node_type in ['depndency', 'progress']:
                        
                        task_wdg = my.get_task_wdg(tasks, parent_key, pipeline_code, process, last_one)
                    else:
                        task_wdg = DivWdg()
                        task_wdg.add_style("width: 115px")
                        task_wdg.add_style("padding: 2px")


                    td.add(task_wdg)


            div.add(table)

            # add + icon at the end for convenience
            if my.show_add_task and security.check_access("search_type", {"code":"sthpw/task"}, "insert", default="insert"):
                label = table.add_cell()
                label.add_color("color", "color")
                label.add_class("spt_task_element_add_task hand")
                label.add_styles('opacity: 0.5; vertical-align: bottom; text-align: right;padding: 0 4px 4px 0')
                label.add_attr("spt_search_key", sobject.get_search_key() )
                icon = IconWdg("Add Tasks", IconWdg.ADD)
                label.add(icon)

        value_wdg = HiddenWdg('data')
        value_wdg.add_class("spt_data")
        div.add(value_wdg)




        # FIXME: this satisfies the critieria that we need a widget with a
        # name of my.get_name() and has a value.
        # in the method: spt.dg_table.accept_single_edit_cell_td
        # NOTE: this is likely no longer necessary in the new fast table
        value_wdg = HiddenWdg(my.get_name())
        value_wdg.set_value("unknown")
        div.add(value_wdg)

 
        return div


    def check_access(my):
        '''check access for each element'''
        
        
        project_code = Project.get_project_code() 
        security = Environment.get_security()
        
        element_names = ['assigned','status']
        search_type = 'sthpw/task'
        for element_name in element_names:
          
            
            def_default_access = 'edit'
            
            
            # check security access
            access_key2 = {
                'search_type': search_type,
                'project': project_code
            }
            access_key1 = {
                'search_type': search_type,
                'key': element_name, 
                'project': project_code

            }
            access_keys = [access_key1, access_key2]
            is_viewable = security.check_access('element', access_keys, "view", default=def_default_access)
            is_editable = security.check_access('element', access_keys, "edit", default=def_default_access)
            my.permission[element_name] = {'is_viewable': is_viewable, 'is_editable': is_editable}


    def get_task_wdg(my, tasks, parent_key, pipeline_code, process, last_one):

        if pipeline_code:
            pipeline = my.pipelines_dict.get(pipeline_code)
        else:
            pipeline = None

        process_obj = pipeline.get_process(process)
        if process_obj:
            node_type = process_obj.get_type()
        else:
            node_type = "node"



        div = DivWdg()
        width = my.width.replace('px','')
        panel_width = int(width) + 15
        div.add_style('width', '%spx'%panel_width)
        div.add_class("spt_task_top")
        div.add_style("float: left")
        div.add_style("white-space: nowrap")



        direction = 'bottom'
        if my.layout in ['horizontal', 'vertical']:
            div.add_style("min-height: 18px")
            div.add_style("padding-left: 8px")
            div.add_style('width', my.total_width )
            if my.layout == 'horizontal':
                direction = 'right'
        else:
            div.add_style("padding: 2px")
            div.add_style("text-align: center")
            direction = 'right'


        if node_type == "progress":


            if my.show_processes_in_title != 'true':
                title_wdg = DivWdg("<b>%s</b>" % process)
                div.add(title_wdg)

            related_type = process_obj.get_attribute("search_type")
            related_process = process_obj.get_attribute("process")

            if not related_type:
                search = Search("config/process")
                search.add_filter("pipeline_code", pipeline_code)
                search.add_filter("process", process)
                process_sobj = search.get_sobject()
                workflow = process_sobj.get_json_value("workflow")
                if workflow:
                    related_type = workflow.get("search_type")
                    related_process = workflow.get("process")

            if not related_process:
                related_process = process
     

            if not related_type:
                progress_div = DivWdg()
                div.add(progress_div)
                progress_div.add_style("font-size: 1.5em")
                progress_div.add("N/A")
                progress_div.add_style("margin: 20")
                return div




            sobject = my.get_current_sobject()



            key = "%s|%s|status" % (sobject.get_search_key(), process)
            message_sobj = Search.get_by_code("sthpw/message", key)
            if message_sobj:
                status = message_sobj.get("message")
            else:
                status = 'pending'

            display_status = Common.get_display_title(status)
            div.add("<b>%s</b>" % display_status)
            color = Task.get_default_color(status)


            div.add_behavior( {
                'type': 'click_up',
                'related_type': related_type,
                'cbjs_action': '''
                var class_name = 'tactic.ui.panel.ViewPanelWdg';
                var kwargs = {
                    search_type: 'sthpw/task',
                }
                '''
            } )


            related = sobject.get_related_sobjects(related_type)
            related_keys = ["%s|%s|status" % (x.get_search_key(), related_process) for x in related]
            search = Search("sthpw/message")
            search.add_filters("code", related_keys)
            message_sobjs = search.get_sobjects()
            total = len(related)
            count = 0
            for message_sobj in message_sobjs:
                if message_sobj.get_value("message").lower() == "complete":
                    count += 1

            from spt.ui.widgets import RadialProgressWdg
            progress_wdg = RadialProgressWdg(
                total=total,
                count=count,
                color=color
            )
            progress_div = DivWdg()
            div.add(progress_div)
            progress_div.add(progress_wdg)
            progress_div.add_style("margin: 0px auto")
            progress_div.add_style("width: 70px")


            return div


        """
        if node_type == "dependency":

            dependency_div = DivWdg()
            div.add(dependency_div)
            dependency_div.add_style("margin: 8px 0px 8px -8px")
            dependency_div.add_class("spt_dependency_top")

            dependency_div.add("H!H!H!")


            return div
        """

        if node_type == "hierarchy":

            hierarchy_div = DivWdg()
            div.add(hierarchy_div)
            hierarchy_div.add_style("margin: 8px 0px 8px -8px")
            hierarchy_div.add_class("spt_hierarchy_top")

            search = Search("config/process")
            search.add_filter("pipeline_code", pipeline_code)
            search.add_filter("process", process)
            process_sobj = search.get_sobject()
            subpipeline_code = process_sobj.get("subpipeline_code")
            #subpipeline = Pipeline.get_by_code(subpipeline_code)
            #processes = subpipeline.get_process_names()
            #num_processes = len(processes)

            from tactic.ui.widget import SwapDisplayWdg
            SwapDisplayWdg.handle_top(hierarchy_div)

            #title = "<b>%s (%s)</b>" % (process, num_processes)
            title = "<b>%s</b>" % (process)
            swap = SwapDisplayWdg(title=title)
            hierarchy_div.add(swap)



            pipeline_div = DivWdg()
            hierarchy_div.add(pipeline_div)
            pipeline_div.add_class("spt_subpipeline_content")
            pipeline_div.add_style("margin: 10px 10px")
            pipeline_div.add_style("display: none")


            unique_id = pipeline_div.set_unique_id("content")
            swap.set_content_id(unique_id)


            hierarchy_div.add_relay_behavior( {
                'type': 'click',
                'bvr_match_class': 'spt_swap_top',
                'pipeline_code': subpipeline_code,
                'process': process,
                'cbjs_action': '''
                var row = bvr.src_el.getParent(".spt_table_row");
                var search_key = row.getAttribute("spt_search_key_v2");
                //var class_name = 'tactic.ui.panel.TableLayoutWdg';
                var class_name = 'tactic.ui.table.SubPipelineTaskWdg';
                var kwargs = {
                    search_key: search_key,
                    process: bvr.process,
                    pipeline_code: bvr.pipeline_code,
                }
                //spt.table.add_hidden_row(row, class_name, kwargs);
                var top = bvr.src_el.getParent(".spt_hierarchy_top");
                var el = top.getElement(".spt_subpipeline_content");
                spt.panel.load(el, class_name, kwargs)
                '''
            } )


            return div




        # make it into a table
        table = Table()
        #table.add_attr("border", "1")
        div.add(table)
        table.add_row()
        table.add_style("width: 100%")

        if my.show_border != 'none' :
            if my.show_border == 'one-sided' and not last_one:
                div.add_border(direction=direction, color="table_border")
            elif my.show_border == 'all':
                div.add_border(color="table_border")




        # if there are multiple tasks, assume all properties are the same
        # except the assignment
        task = tasks[0]



        process = task.get_value("process")
        status = task.get_value("status")


        # handle the colors
        process_color = ''
        
        task_pipeline_code = 'task'
        if task.get_value('pipeline_code'):
            task_pipeline_code = task.get_value('pipeline_code')
        status_colors = my.status_colors.get(task_pipeline_code)
        bgColor = ''
        if not status_colors:
            status_colors = my.status_colors.get('task')
        if status_colors:
            bgColor = status_colors.get(status)



        process_colors = my.process_colors.get(pipeline_code)
        if process_colors and process_colors.has_key(process):
            tmp_color = process_colors[process]
            if tmp_color:
                process_color = tmp_color


        if my.bg_color_mode == 'status':
            div.add_style("background-color: %s" % bgColor)
        elif my.bg_color_mode == 'process':
            div.add_style("background-color: %s" % process_color)

        div.add_style("opacity: 0.75")



        
        if my.show_labels != 'false':
            context_div = DivWdg()
            if my.layout in ['horizontal',  'vertical']:
                #context_div.add_style("float: left")
                #context_div.add_style("width: 75px")
                table.add_cell(context_div)
            else:
                div.add(context_div)

            context_div.add_style("font-size: %spx" % my.font_size)
            if my.text_color:
                context_div.add_style("color", my.text_color)
            else:
                context_div.add_color("color", 'color')
            proc = task.get_value("process")
            label_dict = my.label_dict.get(pipeline_code)
            if label_dict and label_dict.has_key(proc):
                context_div.add(label_dict[proc])

        if not my.context_color_mode:
            process_color = ''
        elif my.context_color_mode == 'status':
            process_color = bgColor
        elif my.context_color_mode == 'process':
            pass

        if not my.status_color_mode:
            bgColor = ''
        elif my.status_color_mode == 'process':
            bgColor = process_color
        elif my.status_color_mode == 'status':
            pass


        process = task.get_value("process")
        if my.show_process == 'true' and (len(my.tasks) >= 1 or process != 'publish'):
            process_div = DivWdg()
            if my.layout in ['horizontal', 'vertical']:
                #process_div.add_style("float: left")
                # if the process is too long, it will cut off cleanly and
                # not bleed
                process_div.add_style("overflow: hidden")
                process_div.add_style("margin-right: 5px")
                td = table.add_cell(process_div)
                if my.layout == 'vertical':
                    td.add_style("width: %spx"%my.LAYOUT_WIDTH)
                else:
                    td.add_style("width: 75px")
            else:
                div.add(process_div)

            process_div.add_style("font-weight: bold")
            process_div.add_style("font-size: %spx" % my.font_size)
            if my.text_color:
                process_div.add_style("color", my.text_color)
            else:
                process_div.add_color("color","color")
            if process_color:
                process_div.add_style("background-color: %s" %process_color)
            process_div.add(process)
     


        if my.show_context != 'false':
            context_div = DivWdg()
            if my.layout in ['horizontal', 'vertical']:
                #context_div.add_style("float: left")
                context_div.add_style("width: 75px")
                context_div.add_style("margin-left: 5px")
                table.add_cell(context_div)
            else:
                div.add(context_div)

            context_div.add_style("font-weight: bold")
            context_div.add_style("font-size: %spx" % my.font_size)
            if my.text_color:
                context_div.add_style("color", my.text_color)
            else:
                context_div.add_color("color","color")
            if process_color:
                context_div.add_style("background-color: %s" %process_color)
            context = task.get_value("context")
            # for backward compatibility, show process if context is empty
            if not context:
                context = task.get_value("process")
            context_div.add(context)


        if my.show_dates != 'false':
            date_div = DivWdg()
            if my.layout in ['horizontal', 'vertical']:
                #date_div.add_style("float: left")
                td = table.add_cell(date_div)
                
                if my.layout == 'vertical':
                    td.add_style("width: %spx"%my.LAYOUT_WIDTH)
                else:
                    td.add_style("width: 75px")
            else:
                div.add(date_div)

            date_div.add_style("font-size: %spx" % (my.font_size-1))
            if my.text_color:
                date_div.add_style("color", my.text_color)
            else:
                date_div.add_color('color','color')
            start_date = task.get_value("bid_start_date")
            if start_date:
                start_date = parser.parse(start_date)
                start_date = start_date.strftime("%m/%d")
            end_date = task.get_value("bid_end_date")
            if end_date:
                end_date = parser.parse(end_date)
                end_date = end_date.strftime("%m/%d")

            if not start_date and not end_date:
                date_div.add("-")
            elif not end_date:
                date_div.add(start_date)
            else:
                date_div.add("%s - %s" % (start_date, end_date) )

        # follow the proper access rules defined for task
        if my.show_status != 'false':
            if (not my.edit_status or not my.permission['status']['is_editable'] ) and my.permission['status']['is_viewable']:
                status_div = DivWdg()
                status_div.add_color('color','color')
                if my.layout in ['horizontal', 'vertical']:
                    #status_div.add_style("float: left")
                    td = table.add_cell(status_div)
                    td.add_style("width: 75px")
                else:
                    # don't need to set width here so it covers the whole status
                    div.add(status_div)

                if not status:
                    status = "N/A"

                status_div.add_style("font-size: %spx" % (my.font_size))
                status_div.add_style("font-weight: bold")
                
                if bgColor:
                    status_div.add_style("background-color: %s" %bgColor)
                status_div.add(status)
             
            elif my.permission['status']['is_editable']:
                task_pipeline_code = task.get_value("pipeline_code")
                if not pipeline_code:
                    task_pipeline_code = 'task'
                task_pipeline = Pipeline.get_by_code(task_pipeline_code)
                if not task_pipeline:
                    task_pipeline = Pipeline.get_by_code("task")
                task_statuses = task_pipeline.get_process_names()
               
                filtered_statuses = [x for x in task_statuses if x in my.allowed_statuses]

                context = task.get_value("context")
                search_key = task.get_search_key()
                task_id = task.get_id()

                if task.is_insert():
                    process = task.get_value("process")
                    name = 'status|NEW|%s' % process
                else:
                    name = 'status|EDIT|%s' % task.get_id()

                select = SelectWdg(name)
                select.add_color('color','color')
                #select = SelectWdg('status_%s'%task_id)
                select.add_empty_option('-- Status --')
                select.add_attr("spt_context", context)

                if node_type in ['auto', 'condition']:
                    select.add_attr("readonly","true")

                # TODO: while convenient, this is extremely heavy
                select.add_behavior( {
                    'type': 'change',
                    'color': status_colors,
                    'cbjs_action': '''
                    var status_colors = bvr.color;
                    var value = bvr.src_el.value;
                    bvr.src_el.style.background = status_colors[value];
                    var context = bvr.src_el.getAttribute("spt_context");
                    var layout = bvr.src_el.getParent(".spt_layout");
                    spt.table.set_layout(layout);
                    var rows = spt.table.get_selected_rows();
                    for (var i = 0; i < rows.length; i++) {
                        var row = rows[i];
                        var elements = row.getElements(".spt_task_status_select");
                        for (var j = 0; j < elements.length; j++) {
                            var el = elements[j];
                            if (el == bvr.src_el) {
                                continue;
                            }

                            var el_context = el.getAttribute("spt_context");
                            if (el_context == context) {
                                el.value = value;
                                spt.task_element.status_change_cbk(evt, {src_el: el});
                            }
                        }
                    }

                    '''
                } )



                select.add_class("spt_task_status_select")
                if bgColor:
                    select.add_style("background: %s" %bgColor)


                if my.layout in ['horizontal', 'vertical']:
                    #select.add_style("float: left")
                    select.add_style("width: %spx" %my.LAYOUT_WIDTH)
                    select.add_style("margin: 2px 0px 2px 0px")
                    td = table.add_cell(select)
                    if my.layout == 'vertical':
                        select.add_style("width: %spx" %my.LAYOUT_WIDTH)
                    else:
                        select.add_style("width: 75px")

                    #td.add_style("width: 75px")

                else:
                    select.add_style("width", my.width)
                    div.add(select)
                if status and status not in filtered_statuses:
                    filtered_statuses.append(status)
                select.set_option("values", filtered_statuses)
                select.set_value(status)

                if task.is_insert():
                    update = {
                        "parent_key": task.get_parent_search_key(),
                        "expression": "@GET(sthpw/task['process','%s'].status)" % process,
                    }
                else:
                    update = {
                        "search_key": task.get_search_key(),
                        "column": "status",
                    }

                update['cbjs_postaction'] = '''
                        var element = bvr.src_el;
                        if ("createEvent" in document) {
                            var evt = document.createEvent("HTMLEvents");
                            evt.initEvent("change", false, true);
                            element.dispatchEvent(evt);
                        }
                        else {
                            element.fireEvent("onchange");
                        }
                        var top = bvr.src_el.getParent(".spt_task_top");
                        top.getParent().setStyle("opacity", 1.0);

                        '''
                select.add_update(update)

      
        assigned_div = None
        if my.show_assigned != 'false' and my.permission['assigned']['is_viewable'] :

            assigned_div = DivWdg()
            assigned_div.add_style("font-size: %spx" % (my.font_size-1))
            assigned_div.add_color('color','color')
            if my.layout in ['horizontal', 'vertical']:
                table.add_cell(assigned_div)
            else:
                div.add(assigned_div)


            for subtask in tasks:
                assigned = subtask.get_value("assigned")
                if node_type == "auto":
                    assigned_div.add("Automated")
                    assigned_div.add_style("padding: 8px")

                if node_type != "auto" and my.edit_assigned == 'true' and my.permission['assigned']['is_editable']:
                    select_div = DivWdg()
                    assigned_div.add(select_div)

                    if task.is_insert():
                        name = 'assigned|NEW|%s' % process
                    else:
                        name = 'assigned|EDIT|%s' % task.get_id()
                    select = SelectWdg(name)
                    #select = SelectWdg('assigned_%s' %subtask.get_id())
                    select_div.add(select)
                    # just use the same class name as the status select for simplicity
                    select.add_class('spt_task_status_select')
                    select.add_empty_option('-- Assigned --')
                    select.set_option('values', my.assignee) 
                    select.set_option('labels', my.assignee_labels) 
                    select.set_value(assigned)
                    select.add_class("spt_task_element_assigned")
                    select.add_style("margin: 1px 0px 1px 0px")
                    if my.layout == 'vertical':
                        select.add_style("width", '%spx'%my.LAYOUT_WIDTH)
                    else:
                        select.add_style("width", my.width)

                    if task.is_insert():
                        update = {
                            "parent_key": task.get_parent_search_key(),
                            "expression": "@GET(sthpw/task['process','%s'].assigned)" % process,
                        }
                    else:
                        update = {
                            "search_key": task.get_search_key(),
                            "column": "assigned",
                        }

                    update['cbjs_postaction'] = '''
                            var element = bvr.src_el;
                            if ("createEvent" in document) {
                                var evt = document.createEvent("HTMLEvents");
                                evt.initEvent("change", false, true);
                                element.dispatchEvent(evt);
                            }
                            else {
                                element.fireEvent("onchange");
                            }
                            var top = bvr.src_el.getParent(".spt_task_top");
                            top.getParent().setStyle("opacity", 1.0);

                            '''
                    select.add_update(update)





                else:
                    
                    assigned_label = assigned
                    if my.assigned_label:
                        assigned_label = my.assignee_dict.get(assigned)
                    if not assigned:
                        assigned = HtmlElement.i("Unassigned")
                        assigned.add_style("opacity: 0.5")
                        assigned_label = assigned
                    assigned_div.add(assigned_label)
                    assigned_div.add("<br/>")



        div.add_behavior( {
            'type': 'mouseenter',
            'cbjs_action': '''
            var els = bvr.src_el.getElements(".spt_process_buttons");
            for (var i = 0; i < els.length; i++) {
                els.setStyle("display", "");
            }
            '''
        } )

        div.add_behavior( {
            'type': 'mouseleave',
            'cbjs_action': '''
            var els = bvr.src_el.getElements(".spt_process_buttons");
            for (var i = 0; i < els.length; i++) {
                els.setStyle("display", "none");
            }
            '''
        } )



        button_div = DivWdg()
        button_div.add_style("display: none")
        button_div.add_class("spt_process_buttons")
        #button_div.add_border()
        button_table = Table()
        button_div.add(button_table)
        button_table.add_row()



        #button_table.add_style("float: right")
        if my.show_task_edit != 'false' or my.show_track == 'true':
            #div.add(button_div)

            if my.layout in ['horizontal', 'vertical']:
                td = table.add_cell(button_div)
                td.add_style("width: 70px")
            else:
                div.add(button_div)


            button_div.add_style("padding: 5px 0px")


            if my.layout in ['horizontal', 'vertical']:
                button_div.add_style("float: left")
                button_div.add_style("width: 50px")


        if my.show_task_edit != 'false':
            #edit_div.add_style('float: right')
            icon = IconButtonWdg(tip='Edit Task', icon="BS_EDIT")
            icon.add_class('hand')
            icon.add_behavior({
                'type': 'click_up',
                'view': my.task_edit_view,
                'search_key': SearchKey.get_by_sobject(task, use_id=True),
                'cbjs_edit': '''
                    spt.edit.edit_form_cbk(evt, bvr);
                    update_event = "update|%s";
                    spt.named_events.fire_event(update_event, {})
                ''' %parent_key,
                'cbjs_action': '''
                var kwargs = {
                    search_key: bvr.search_key,
                    view: bvr.view,
                    cbjs_edit: bvr.cbjs_edit
                };
                var title = 'edit_popup';
                var cls_name = 'tactic.ui.panel.EditWdg';
                spt.api.load_popup(title, cls_name, kwargs);
            '''}) 
            icon.add_style("display: inline-block")

            icon_div = DivWdg(icon)
            #icon_div.add_style("margin-top: -6px")
            icon_div.add_style("margin-right: -6px")
            button_table.add_cell(icon_div)

            # add a note
            icon = IconButtonWdg(tip='View / Add Notes', icon="BS_PENCIL")
            icon_div.add(icon)
            icon.add_style("display: inline-block")
            icon.add_class('hand')
            icon.add_behavior({
                'type': 'click_up',
                'parent_key': parent_key,
                'process': process,
                'cbjs_action': '''
                var class_name = "tactic.ui.widget.DiscussionAddNoteWdg";
                var kwargs = {
                    search_key: bvr.parent_key,
                    process: bvr.process,
                    display: 'block',
                }
                spt.panel.load_popup("Add Note ["+bvr.process+"]", class_name, kwargs);
                '''
            } )


            # view schedule
            """
            icon = IconButtonWdg(tip='User Schedule', icon="BS_USER")
            icon_div.add(icon)
            icon.add_style("display: inline-block")
            icon.add_class('hand')
            icon.add_behavior({
                'type': 'click_up',
                'parent_key': parent_key,
                'process': process,
                'cbjs_action': '''
                var login = "beth";

                var class_name = "tactic.ui.widget.TaskCalendarWdg";
                var kwargs = {
                    assigned: login
                }
                spt.tab.add_new("test", "test", class_name, kwargs);
                '''
            } )
            """






        #my.show_track = 'true'
        if my.show_track == 'true':
            icon = IconButtonWdg(tip='', icon=IconWdg.HISTORY)
            icon.add_color('color','color', +20)
            icon.add_tip('click to load...', title='show history', cls='tactic_task_tip')
         
            icon.add_behavior({'type': 'click',
                 'search_key': task.get_search_key(use_id=True),
                'cbjs_action': '''
                var tips = spt.Tips.get('task_track');
                var text_elem = tips.container.getElement('.tip-text')
                
                var slide = new Fx.Slide(text_elem);
                tips.fill(text_elem, 'loading...');
                
                var s = TacticServerStub.get();
                var result = s.eval("@SOBJECT(sthpw/status_log['@ORDER_BY','timestamp desc'])",  {search_keys: [bvr.search_key], single:true});
                
                var content = 'No record';

                if (result && result.__search_key__)
                    content = '<span>status: </span>' + result.from_status + '<br>' + '<span style="padding-left: 20px">by:</span> ' + result.login; 

                bvr.src_el.store('tip:text', content)
                tips.fill(text_elem, content);
                
                slide.hide();
                slide.slideIn();
                
                '''})

            icon_div = DivWdg(icon)
            #icon_div.add_style("margin-top: -3px")
            icon_div.add_style("margin-right: -6px")
            button_table.add_cell(icon_div)


        show_bid = my.kwargs.get("show_bid")
        if show_bid in [True, 'true']:
            bid_div = DivWdg()
            bid_div.add_style("font-size: %spx" % (my.font_size-1))
            bid_div.add_color('color','color')
            if my.layout in ['horizontal', 'vertical']:
                table.add_cell(bid_div)
            else:
                div.add(bid_div)


            for subtask in tasks:

                bid_duration = subtask.get_value("bid_duration")
                process = subtask.get_value("process")

                text_div = DivWdg()
                bid_div.add(text_div)

                if subtask.is_insert():
                    text = TextWdg('bid|NEW|%s' % process)
                else:
                    text = TextWdg('bid|EDIT|%s' %subtask.get_id())
                text_div.add(text)
                text.add_style("width: 80px")
                text.add_style("text-align: center")

                if bid_duration:
                    text.set_value(bid_duration)
                    text.add_color("color", "color3")
                    text.add_color("background", "background3")

                text.add_style("font-size: 1.2em")
                if my.layout not in ['horizontal', 'vertical']:
                    text.add_style("margin: 5px")
                text.add_style("padding: 5px")

                text.add_behavior( {
                    'type': 'focus',
                    'cbjs_action': '''
                    var value = bvr.src_el.value;
                    bvr.src_el.setAttribute("spt_last_value", value);
                    bvr.src_el.select();
                    '''
                    } )

                text.add_behavior( {
                    'type': 'blur',
                    'cbjs_action': '''
                    var text = bvr.src_el;
                    var value = text.value;

                    var last_value = text.getAttribute('spt_last_value');
                    if (value == last_value) {
                        return;
                    }

                    if (value == "") {
                        return;
                    }
                    spt.task_element.status_change_cbk(evt, {src_el: text});
                    '''
                } )




        return div




__all__.append("SubPipelineTaskWdg")
class SubPipelineTaskWdg(BaseRefreshWdg):

        def get_display(my):

            search_key = my.kwargs.get("search_key")

            sobject = Search.get_by_search_key(search_key)
            search_type = sobject.get_base_search_type()

            top = my.top

            element = TaskElementWdg()
            element.set_option("layout", "vertical")
            element.set_option("parent_process", my.kwargs.get("process"))
            element.set_option("edit_status", "true")
            element.set_option("edit_assigned", "true")
            element.set_option("status_color", "status")
            element.set_option("show_filler_tasks", "true")
            element.set_option("pipeline_code", my.kwargs.get("pipeline_code"))
            element.set_sobjects( [sobject] )
            element.set_current_index(0)
            element.preprocess()
            top.add(element)


            return top


class TaskElementCbk(DatabaseAction):

    def get_title(my):
        return "Tasks Status Changed"

    def set_sobject(my, sobject):
        my.sobject = sobject


    def postprocess(my):
        # add initial tasks
        if my.xx.get("add_initial_tasks"):
            Task.add_initial_tasks(my.sobject)



    def execute(my):
        web = WebContainer.get_web()
        if my.data != None:
            xx = my.data
        else:
            xx = web.get_form_data()
            xx = xx.get('data').get('data')
        
        
        web_data = web.get_form_value('web_data')
        
        processes = []
        if web_data:
            process_data= web_data.get('process_data')
            if process_data:
                try:
                    process_data = jsonloads(process_data)
                    processes = process_data.get('processes')
                except:
                    processes = []
            

        xx = jsonloads(xx)
        my.xx = xx

        #if my.xx.get("add_initial_tasks"):
        #    return
        task_status_ids = []
        task_assigned_ids = []
        task_bid_ids = []
        clone_ids = {}

        new_tasks_by_process = {}

        # create all of the new tasks first
        import re
        p = re.compile("(\w+)\|(\w+)\|(.*)")
        copy_p = re.compile("(\w+)\|(\w+)\|(\w+)_(\w+)")
        for key, value in xx.items():
            if key.find("|COPY") != -1:
                m = re.match(copy_p, key)
            else:
                m = re.match(p, key)
            if not m:
                continue

            groups = m.groups()

            column = groups[0]
            if column == "bid":
                column = "bid_duration"

            action = groups[1]
            if action == "NEW":
                process = groups[2]
                task = new_tasks_by_process.get(process)
                if not task:
                    # create a new task
                    task = SearchType.create("sthpw/task")
                    task.set_value("process", process)
                    task.set_parent(my.sobject)
                    new_tasks_by_process[process] = task
                task.set_value(column, value)

            elif action == "EDIT":
                task_id = groups[2]

                if column == "status":
                    task_status_ids.append(task_id)
                elif column == "bid_duration":
                    task_bid_ids.append(task_id)
                elif column == "assigned":
                    task_assigned_ids.append(task_id)
                else:
                    raise Exception("Column [%s] not supported")


            elif action.startswith('COPY'):
                task_id = groups[2]
                task = Search.get_by_id("sthpw/task", task_id)
                status = value
                clone = task.clone()
                clone.set_value("assigned", value)
                clone.commit()

            elif action == 'DELETE':
                task_id = groups[2]
                task = Search.get_by_id("sthpw/task", task_id)
                task.delete()


        # commit all of the new tasks
        tasks = {}

        processes.reverse()
        # reverse the order of the task in this dict as a list
        sorted_tasks = map(new_tasks_by_process.get, processes)
        # remove the None after mapping
        sorted_tasks = [x for x in sorted_tasks if x]
        for task in sorted_tasks:
           
            tasks[task.get_id()] = task
            task.commit()




        # then go through all updates of the changes
        for key, value in xx.items():
            m = re.match(p, key)
            if not m:
                continue

            groups = m.groups()

            column = groups[0]
            action = groups[1]

            # skip the new tasks this time
            if action == "NEW":
                continue




        # get the tasks
        if task_status_ids: 
            search = Search("sthpw/task")
            search.add_filters("id", task_status_ids)
            tasks = search.get_sobjects()

            for task in tasks:
                current_status = task.get_value("status")
                new_status = xx.get('status|EDIT|%s'%task.get_id())
                if current_status == new_status:
                    continue
                task.set_value("status", new_status)
                task.commit()


        if task_assigned_ids: 
            search = Search("sthpw/task")
            search.add_filters("id", task_assigned_ids)
            tasks = search.get_sobjects()

            for task in tasks:
                current_assigned = task.get_value("assigned")
                new_assigned = xx.get('assigned|EDIT|%s'%task.get_id())
                if current_assigned == new_assigned:
                    continue

                task.set_value("assigned", new_assigned)
                task.commit()



        if task_bid_ids: 
            search = Search("sthpw/task")
            search.add_filters("id", task_bid_ids)
            tasks = search.get_sobjects()

            for task in tasks:
                new_bid = xx.get('bid|EDIT|%s'%task.get_id())

                task.set_value("bid_duration", new_bid)
                task.commit()




__all__.append("TaskSummaryElementWdg")
class TaskSummaryElementWdg(TaskElementWdg):
    ARGS_KEYS = {
        'mode': {
            'type': 'SelectWdg',
            'category': 'Display',
            'description': 'Determines the mode to display',
            'values': 'default|minimal'
        },
    }

    def get_width(my):

        mode = my.get_option("mode")
        if mode == "minimal":
            return 100
        else:
            return 400


    def get_title(my):
        return "Task Summary"


    def get_display(my):

        mode = my.get_option("mode")
        if mode == "minimal":
            return my._get_display_miminal()
        else:
            return my._get_display_default()


    def _get_display_default(my):

        my.kwargs["show_filler_tasks"] = True

        my.tasks = my.get_tasks()
        sobject = my.get_current_sobject()

        top = my.top

        table = Table()
        top.add(table)
        table.add_row()
        table.add_style("width: 100%")
        table.add_style("font-size: 0.8em")


        table.add_relay_behavior( {
            'type': 'mouseup',
            'bvr_match_class': 'spt_task',
            'cbjs_action': '''
            var task_key = bvr.src_el.getAttribute("spt_task_key");
            var class_name = 'tactic.ui.panel.EditWdg';
            var kwargs = {
                search_key: task_key,
            }
            spt.panel.load_popup("Task Edit", class_name, kwargs);
            '''
        } )

        import re


        for task in my.tasks:
            bgColor = ''
            process = task.get_value("process").lower()
            parts = re.split( re.compile("[ -_]"), process)
            if len(parts) == 1:
                #title = parts[0][:3]
                title = parts[0]
            else:
                parts = [x[:1] for x in parts]
                title = "".join(parts)
            parts = re.split( re.compile("[ -_]"), process)
            #if len(parts) == 1:
            #    parts.append("")
            #    parts.append("")
            #else:
            #    parts.append("")
            title = "<br/>".join(parts)

            status = task.get_value("status")

            task_pipeline_code = task.get_value("pipeline_code")

            status_colors = my.status_colors.get(task_pipeline_code)
            if not status_colors:
                status_colors = my.status_colors.get('task')
            if status_colors:
                bgColor = status_colors.get(status)



            td = table.add_cell()
            td.add_attr("spt_task_key", task.get_search_key())

            td.add_behavior({
                'type': 'mouseenter',
                'cbjs_action': '''
                bvr.src_el.setStyle("background", "#EEE");
                '''
            })
            td.add_behavior({
                'type': 'mouseleave',
                'cbjs_action': '''
                bvr.src_el.setStyle("background", "");
                '''
            })

            title_div = DivWdg()
            title_div.add(title)
            title_div.add_style("max-height: 30px")
            title_div.add_style("height: 25px")
            title_div.add_style("overflow: hidden")

            td.add(title_div)
            td.add_style("text-align: center")
            div = DivWdg()
            td.add(div)
            td.add_style("padding: 0px 3px 0px 3px")
            td.add_style("min-width: 20px")
            div.add_border()
            div.set_round_corners(10)

            if not bgColor:
                bgColor = '#EEE'
                td.add_style("opacity: 0.5")
            else:
                td.add_class("spt_task")
            div.add_style("background", bgColor)

            div.add_style("width: 15px")
            div.add_style("height: 15px")
            div.add_style("margin-left: auto")
            div.add_style("margin-right: auto")

            if status:
                td.add_attr("title", "%s - %s" % (process, status))
            else:
                td.add_attr("title", "%s - N/A" % process)


        return top



    def _get_display_miminal(my):

        my.kwargs["show_filler_tasks"] = True

        my.tasks = my.get_tasks()
        sobject = my.get_current_sobject()

        top = my.top

        table = Table()
        top.add(table)
        table.add_row()
        table.add_style("width: 100%")
        table.add_style("font-size: 0.8em")


        table.add_relay_behavior( {
            'type': 'mouseup',
            'bvr_match_class': 'spt_task',
            'cbjs_action': '''
            var task_key = bvr.src_el.getAttribute("spt_task_key");
            var class_name = 'tactic.ui.panel.EditWdg';
            var kwargs = {
                search_key: task_key,
            }
            spt.panel.load_popup("Task Edit", class_name, kwargs);
            '''
        } )

        import re


        for task in my.tasks:
            bgColor = ''
            process = task.get_value("process").lower()
            parts = re.split( re.compile("[ -_]"), process)
            if len(parts) == 1:
                #title = parts[0][:3]
                title = parts[0]
            else:
                parts = [x[:1] for x in parts]
                title = "".join(parts)
            parts = re.split( re.compile("[ -_]"), process)
            #if len(parts) == 1:
            #    parts.append("")
            #    parts.append("")
            #else:
            #    parts.append("")
            title = "<br/>".join(parts)

            status = task.get_value("status")

            task_pipeline_code = task.get_value("pipeline_code")

            status_colors = my.status_colors.get(task_pipeline_code)
            if not status_colors:
                status_colors = my.status_colors.get('task')
            if status_colors:
                bgColor = status_colors.get(status)



            td = table.add_cell()
            td.add_attr("spt_task_key", task.get_search_key())

            td.add_behavior({
                'type': 'mouseenter',
                'cbjs_action': '''
                bvr.src_el.setStyle("background", "#EEE");
                '''
            })
            td.add_behavior({
                'type': 'mouseleave',
                'cbjs_action': '''
                bvr.src_el.setStyle("background", "");
                '''
            })

            td.add_style("text-align: center")
            div = DivWdg()
            td.add(div)
            td.add_style("padding: 0px 1px 0px 1px")
            div.add_border()
            div.set_round_corners(10)

            if not bgColor:
                bgColor = '#EEE'
                td.add_style("opacity: 0.5")
            else:
                td.add_class("spt_task")
            div.add_style("background", bgColor)

            div.add_style("width: 5px")
            div.add_style("height: 15px")
            #div.add_style("margin-left: auto")
            #div.add_style("margin-right: auto")

            if status:
                td.add_attr("title", "%s - %s" % (process, status))
            else:
                td.add_attr("title", "%s - N/A" % process)


        return top





class TaskCheckoutManageWdg(BaseRefreshWdg):
    ''' This has evolved to a Check out widget'''
    ARGS_KEYS = {
        #'checkin_panel_script_path': {'type': 'TextWdg',
        #    'category': '2. Display',
        #    'order': 1,
        #    'description': 'path to the check-in panel script'},
        
        #'checkin_script_path': {'type': 'TextWdg',
        #    'category': '2. Display',
        #    'order': 2,
        #    'description': 'path to the check-in script'},
        #
        'validate_script_path': {'type': 'TextWdg',
            'category': '2. Display',
            'order': 3,
            'description': 'path to the validate script'},

        #'checkout_panel_script_path': {'type': 'TextWdg',
        #    'category': '2. Display',
        #    'order': 4,
        #    'description': 'path to the check-out panel script'},

        'checkout_script_path': {'type': 'TextWdg',
            'category': '2. Display',
            'order': 5,
            'description': 'path to the check-out script'},

        'checkin_script': 'inline action to publish',
        'checkin_relative_dir': {'type': 'TextWdg',
            'order': 6,
            'category': '2. Display',
            'description':'a predefined relative dir to the sandbox to construct a preselected checkin-in path'},

        'sandbox_dir': {'type': 'TextWdg',
            'category': '2. Display',
            'order': 7,
            'description':'a virtual sandbox dir'}
        ,
        'mode': { 'type': 'SelectWdg',
            'category': '2. Display',
            'order': 8,
            'values': 'sequence|file|dir|add',
            'description': 'determines whether this widget can only check-in sequences, file, or directory'},

        'transfer_mode':  { 'type': 'SelectWdg',
            'category': '1. Required',
            'order': 0,

            'values': 'copy|move|upload',
            'description': 'determines mode of file transfer'},

        'checkin_ui_options': {'type': 'TextWdg',
            'category': '2. Display',
            'order': 91,
            'description': 'a json string of dictionary of ui options like is_current'},
        'panel_cls': {'type': 'TextWdg',
            'category': '2. Display',
            'order': 92,
            'description': 'a custom panel class overriding the default tactic.ui.widget.CheckinInfoPanelWdg'},

        'lock_process': {
            'category': '2. Display',
            'description': 'Flag for whether to allow the user to switch process',
            'order': 9,
            'type': 'SelectWdg',
            'values': 'true|false'
          },
         'show_versionless_folder': {
            'category': '2. Display',
            'description': 'Flag for whether to display the latest and current versionless folders',
            'order': 4,
            'type': 'SelectWdg',
            'values': 'true|false'
          }

        

        }

    def init(my):
        #my.checkin_script = my.kwargs.get("checkin_script")
        #my.checkin_script_path = my.kwargs.get("checkin_script_path")
        my.checkin_panel_script_path = my.kwargs.get("checkin_panel_script_path")
        my.checkout_panel_script_path = my.kwargs.get("checkout_panel_script_path")

        my.checkout_script_path = my.kwargs.get("checkout_script_path")
        my.validate_script_path = my.kwargs.get("validate_script_path")
        my.checkin_relative_dir = my.kwargs.get("checkin_relative_dir")
        if not my.checkin_relative_dir:
            my.checkin_relative_dir = ''
        
        my.lock_process = my.kwargs.get("lock_process")
        my.transfer_mode = my.kwargs.get("transfer_mode")
        my.mode = my.kwargs.get("mode")
        my.checkin_ui_options = my.kwargs.get("checkin_ui_options")
        my.panel_cls = my.kwargs.get("panel_cls")
        my.search_key = ''
        parent_key = my.kwargs.get('parent_key')
        if not parent_key:
            raise TacticException("parent_key is expected for this widget")

        sobject = SearchKey.get_by_search_key(parent_key)
        my.sobject = sobject 
        my.snapshot = None
        my.snapshot_code = ''
        my.latest_snapshot_code = ''
        my.latest_sandbox_dir = ''
        my.process = ''
        my.context = ''
        if sobject and sobject.get_base_search_type() in ['sthpw/task', 'sthpw/note']:
            my.process = sobject.get_value('process')
            my.context = sobject.get_value('context')

            my.parent = sobject.get_parent()
            if my.parent:
                my.search_key = SearchKey.get_by_sobject(my.parent)
            
            # find current snapshot for this:
            my.snapshot = Snapshot.get_current(sobject.get_value('search_type'), sobject.get_value('search_id'), context= sobject.get_value('context'))
            my.latest_snapshot = Snapshot.get_latest(sobject.get_value('search_type'), sobject.get_value('search_id'), context= sobject.get_value('context'))
            if my.latest_snapshot:
                my.latest_sandbox_dir = my.latest_snapshot.get_sandbox_dir(file_type='main')
            if my.snapshot:
                my.snapshot_code = my.snapshot.get_code()
            if my.latest_snapshot:
                my.latest_snapshot_code = my.latest_snapshot.get_code()
                
        else:
            my.process = my.get_option('process')
            my.search_key = SearchKey.get_by_sobject(sobject)
            my.parent = None


        if my.snapshot:
            sandbox_sobj = my.snapshot
        elif my.parent:
            type ='main'
            virtual_snapshot = Snapshot.create_new()
            virtual_snapshot_xml = '<snapshot process=\'%s\'><file type=\'%s\'/></snapshot>' % (my.process, type)
            virtual_snapshot.set_value("snapshot", virtual_snapshot_xml)
            virtual_snapshot.set_value("process", my.process)
            virtual_snapshot.set_value("context", my.context)
            virtual_snapshot.set_sobject(my.parent)
            sandbox_sobj = virtual_snapshot

        else:
            sandbox_sobj = sobject

        my.sandbox_dir = sandbox_sobj.get_sandbox_dir(file_type='main')
        my.sandbox_wip_dir = '%s/WIP' %my.sandbox_dir
        #my.sandbox_wip_dir = my.sandbox_dir
        my.checkout_label = my.checkout_script_path
        if not my.checkout_label:
            my.checkout_label = 'TACTIC default checkout script'
    
        my.checkin_options = {#'checkin_script': my.checkin_script, 
            'checkin_panel_script_path': my.checkin_panel_script_path,
           # 'checkin_script_path': my.checkin_script_path,
            'checkin_relative_dir': my.checkin_relative_dir,
            'validate_script_path': my.validate_script_path,
            'lock_process': my.lock_process,
            'transfer_mode': my.transfer_mode,
            'sandbox_dir': my.sandbox_dir,
            'mode': my.mode,
            'checkin_ui_options': my.checkin_ui_options,
            'panel_cls': my.panel_cls,
            'search_key': my.search_key,
            'icon_size': 'large'
        }
        
        my.checkout_options = {'checkout_script_path': my.checkout_script_path, 
            'checkout_panel_script_path': my.checkout_panel_script_path,
            'mode': my.mode,
            'process': my.process,
            'sandbox_dir': my.sandbox_dir,  
            'search_key': my.search_key,
            'icon_size': 'large'
        }
                  


    def get_display(my):

        show_versionless_folder = my.kwargs.get('show_versionless_folder') !='false'

        is_refresh = my.kwargs.get('is_refresh')=='true'
        if is_refresh:
            div = Widget()
        else:
            div = DivWdg(css='spt_checkout_top')
            div.add_styles('margin: 10px; max-width: 1000px') 
            my.set_as_panel(div)
        # add refresh icon
        refresh = IconButtonWdg(icon=IconWdg.REFRESH, tip='Refresh')
        refresh.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_checkout_top");
            spt.panel.refresh(top);
            '''
        } )
        refresh.add_style("float: right")
        div.add( refresh )
        
        
        button_div = DivWdg()
        div.add(button_div)


        table = Table()
        button_div.add(table)
        button_div.add(HtmlElement.br())
        button_div.add_color("background", "background")

        table.add_style('text-align: center')
        table.add_color("background", "background")
        table.add_color("color", "color")


        table.add_row()
        td = table.add_cell("<b>Check-out</b><br/><br/>")
        td.add_style("text-align: left")
        td.add_style("padding: 10px")


        table.set_max_width()
        col1 = table.add_col()
        col2 = table.add_col()
        col1.add_style('width: 50%')
        col2.add_style('width: 50%')

        context = my.sobject.get_value('context') 

        # label changes depending if there is such snapshot
        if my.snapshot_code:
            span2 = SpanWdg('Check-out Current [%s]' %context, css='small')
        else:
            span2 = SpanWdg('Current [%s] n/a' %context, css='small')
        table.add_row()
        table.add_cell(span2)
        if my.latest_snapshot_code:
            span = SpanWdg('Check-out Latest [%s]' %context, css='small')
        else:
            span = SpanWdg('Latest [%s] n/a'%context, css='small')
        table.add_cell(span)

        tr,td = table.add_row_cell()
        tr.add_style('height: 10px')

        table.add_row()

        checkout = CheckoutButtonElementWdg()
        checkout.set_sobject(my.sobject)
        my.checkout_options['snapshot_code'] = my.snapshot_code
        checkout.set_options(my.checkout_options)
        display = checkout.get_display()
        display.add_styles('width: 50px; margin-left: auto; margin-right: auto')


        td = table.add_cell()
        td.add(display)
        td.add_attr('title', my.checkout_label)



        checkout = CheckoutButtonElementWdg()
        #checkout.set_option('align','left')
        checkout.set_sobject(my.sobject)
        # override 2 attrs for latest
        my.checkout_options['snapshot_code'] = my.latest_snapshot_code
        if my.latest_sandbox_dir:
            my.checkout_options['sandbox_dir'] = my.latest_sandbox_dir

        checkout.set_options(my.checkout_options)
        display = checkout.get_display()
        display.add_styles('width: 50px; margin-left: auto; margin-right: auto')
        td = table.add_cell(display)
        td.add_attr('title', my.checkout_label)

        #tr,td = table.add_row_cell()
        #tr.add_style('height: 30px')



        explore_div = DivWdg()
        explore_div.add(HtmlElement.b("Folders"))
        explore_div.add("<br/><br/>")
        div.add(explore_div)
        explore_div.add_color("background", "background")
        explore_div.add_color("color", "color")
        explore_div.add_border(direction='top')
        explore_div.add_style('padding: 10px')


        table = Table()
        table.add_color("color", "color")
        explore_div.add(table)
        table.add_row()
        td = table.add_cell()
        td.add_style("width: 140px")
        td.add("Current Sandbox WIP")

        # add the path_div
        td = table.add_cell()
        my.add_open_folder(td, my.sandbox_wip_dir)

        table.add_row()
        td = table.add_cell()
        td.add("Repository")
        
        td = table.add_cell()
        client_repo_dir = ''
        # first check for current, then resort to latest
        if my.snapshot:
            client_repo_dir = my.snapshot.get_client_lib_dir()
        elif my.latest_snapshot:
            client_repo_dir = my.latest_snapshot.get_client_lib_dir()
        
        my.add_open_folder(td, client_repo_dir)

        latest_versionless_repo_dir = ''
        current_versionless_repo_dir = ''
        if show_versionless_folder:
            src_snapshot = None
            # first check for current, then resort to latest
            if my.snapshot:
                src_snapshot = my.snapshot
            elif my.latest_snapshot:
                src_snapshot = my.latest_snapshot
            
            if src_snapshot:
                latest_versionless_snapshot = Snapshot.get_versionless(src_snapshot.get_value('search_type'),\
                        src_snapshot.get_value('search_id'), src_snapshot.get_value('context'), mode='latest', create=False)
                if latest_versionless_snapshot:
                    latest_versionless_repo_dir = latest_versionless_snapshot.get_client_lib_dir()

                current_versionless_snapshot = Snapshot.get_versionless(src_snapshot.get_value('search_type'),\
                        src_snapshot.get_value('search_id'), src_snapshot.get_value('context'), mode='current', create=False)

                if current_versionless_snapshot:
                    current_versionless_repo_dir = current_versionless_snapshot.get_client_lib_dir()

                # Latest and current dir
                if latest_versionless_snapshot:
                    table.add_row()
                    td = table.add_cell("Repository - latest versionless")
                    td = table.add_cell()
                    my.add_open_folder(td, latest_versionless_repo_dir)

                if current_versionless_snapshot:
                    table.add_row()
                    td = table.add_cell("Repository - current versionless")
                    td = table.add_cell()
                    my.add_open_folder(td, current_versionless_repo_dir)






        search_type = 'sthpw/snapshot'
        view = 'checkout_tool'
        from tactic.ui.panel import TableLayoutWdg

        snapshots = [my.snapshot]
        if my.latest_snapshot:
            # if no current snapshot, just append the latset one
            if not my.snapshot:
                snapshots.append(my.latest_snapshot)
            # do a comparison if they are the same
            elif my.latest_snapshot.get_code() != my.snapshot.get_code():
                snapshots.insert(0, my.latest_snapshot)
        hist_table = TableLayoutWdg(search_type=search_type, view=view, mode='simple', do_search='false', show_row_select='false')

        search = Search("sthpw/snapshot")
        # FIXME: need process on snapshot
        #search.add_filter("process", my.process)
        search.add_filter("context", context)
        if my.parent:
            search.add_parent_filter(my.parent)
        else:
            search.add_parent_filter(sobject)

        snapshots = search.get_sobjects()
        hist_table.set_sobjects(snapshots)
        table = hist_table.get_table()
        table.add_style("font-size: smaller")
        #table.add_style("width: 500px")

        #div.add_styles('height: 300px; width: 100%; overflow: auto')
        hist_div = DivWdg()
        div.add(hist_div)
        hist_div.add_color("background", "background")
        hist_div.add_color("color", "color")
        hist_div.add_border(direction='top')
        hist_div.add_style("padding: 10px")
        hist_div.add("<b>History<b><br/><br/>")
        hist_div.add(hist_table)

        #last_div = DivWdg('Latest and Current Check-in:')
        #div.add(last_div)
        #last_div.add(hist_table)
        #div.add(HtmlElement.br())

        return div

    def add_open_folder(my, wdg, repo_dir):
        '''add open folder behavior to a wdg given a directory '''
        js = "spt.Applet.get()"
        button = IconWdg(icon=IconWdg.JUMP)
        wdg.add(button)

        wdg.add(repo_dir)

        wdg.add_class('hand')
        wdg.add_behavior({"type": "click_up", 
                "cbjs_action": "%s.makedirs('%s');%s.open_explorer('%s')" % (js, repo_dir, js, repo_dir) })

# DEPRECATED: use TaskCheckoutManageWdg
class TaskCheckinManageWdg(TaskCheckoutManageWdg):
    pass

#from tactic.ui.widget import IconButtonElementWdg
class WorkElementWdg(ButtonElementWdg):

    ARGS_KEYS = {
        #'checkin_panel_script_path': {'type': 'TextWdg',
        #    'category': 'deprecated',
        #    'order': 1,
        #    'description': 'path to the check-in panel script'},
        'checkin_script_path': {'type': 'TextWdg',
            'category': '2. Display',
            'order': 2,
            'description': 'path to the check-in script'},
        'validate_script_path': {'type': 'TextWdg',
            'category': '2. Display',
            'order': 3,
            'description': 'path to the validate script'},

       # 'checkout_panel_script_path': {'type': 'TextWdg',
       # 'category': 'deprecated',
       #     'order': 4,
       #     'description': 'path to the check-out panel script'},
        'checkout_script_path': {'type': 'TextWdg',
            'category': '2. Display',
            'order': 5,
            'description': 'path to the check-out script'},

      #  'checkin_script': 'inline action to publish',
        'checkin_relative_dir': {'type': 'TextWdg',
            'order': 6,
            'category': '2. Display',
            'description':'a predefined relative dir to the sandbox to construct a preselected checkin-in path'},

        'sandbox_dir': {'type': 'TextWdg',
            'category': '2. Display',
            'order': 7,
            'description':'a virtual sandbox dir'}
        ,
        'mode': { 'type': 'SelectWdg',
            'category': '2. Display',
            'order': 8,
            'values': 'sequence|file|dir|add',
            'description': 'determines whether this widget can only check-in sequences, file, or directory'},

        'transfer_mode':  { 'type': 'SelectWdg',
            'category': '1. Required',
            'order': 0,

            'values': 'copy|move|upload',
            'description': 'determines mode of file transfer'},

        'checkin_ui_options': {'type': 'TextWdg',
            'category': '2. Display',
            'order': 91,
            'description': 'a json string of dictionary of ui options like is_current'},
        'panel_cls': {'type': 'TextWdg',
            'category': '2. Display',
            'order': 92,
            'description': 'a custom panel class overriding the default tactic.ui.widget.CheckinInfoPanelWdg'},

        'icon': {'type': 'TextWdg',
            'category': '2. Display',
            'order': 93,
            'description': 'Icon name. defaults to WORK'},

        'show_versionless_folder': {
            'category': '2. Display',
            'description': 'Flag for whether to display the latest and current versionless folders',
            'order': 94,
            'type': 'SelectWdg',
            'values': 'true|false'
        },
            
        'lock_process': {
            'category': '2. Display',
            'description': 'Flag for whether to allow the user to switch process',
            'order': 9,
            'type': 'SelectWdg',
            'values': 'true|false'
          },
        'cbjs_action': {
            'description': 'Inline script to launch the Work area tabs',
            'type': 'TextAreaWdg',
            'order': 0

        }
        }

    def preprocess(my):
        my.kwargs['cbjs_action'] = '''
      var layout = bvr.src_el.getParent(".spt_layout");
      var version = layout.getAttribute("spt_version");
      
      var css_class = version == '2'? ".spt_table_row": ".spt_table_tbody";
      var tbody = bvr.src_el.getParent(css_class);


      var element_name = tbody.getAttribute("spt_element_name");
      var search_key = tbody.getAttribute("spt_search_key");
      var checkin_script_path = bvr.checkin_script_path;
      var checkin_ui_options = bvr.checkin_ui_options;
      var validate_script_path = bvr.validate_script_path;
      var checkout_script_path = bvr.checkout_script_path;
      var checkin_mode = bvr.mode;
      var transfer_mode = bvr.transfer_mode;
      var sandbox_dir = bvr.sandbox_dir;
      var checkin_relative_dir = bvr.checkin_relative_dir;
      var lock_process = bvr.lock_process;
      var show_versionless_folder = bvr.show_versionless_folder;


      try {
        var server = TacticServerStub.get();
        var code = server.eval( "@GET(parent.code)", {search_keys: search_key} );

        spt.tab.set_main_body_tab();
        var kwargs = {
        'search_key': search_key,
        'checkin_script_path': checkin_script_path ,
        'checkin_relative_dir': checkin_relative_dir,
        'checkin_ui_options': checkin_ui_options ,
        'validate_script_path': validate_script_path ,
        'checkout_script_path': checkout_script_path, 
        'mode': checkin_mode ,
        'transfer_mode': transfer_mode,
        'sandbox_dir': sandbox_dir,
        'lock_process': lock_process,
        'show_versionless_folder': show_versionless_folder

        }
        var title = "Task: " + code;
        var class_name = "tactic.ui.tools.sobject_wdg.TaskDetailWdg";
        spt.tab.add_new(search_key, title, class_name, kwargs);

      } catch(e) {
            spt.alert(spt.exception.handler(e));
      }
        '''
        super(WorkElementWdg,my).preprocess()


    def get_display(my):
        my.behavior = {}

        my.checkin_script_path = my.kwargs.get("checkin_script_path")
        # deprecated
        #my.checkin_script = my.kwargs.get("checkin_script")
        #my.checkin_panel_script_path = my.kwargs.get("checkin_panel_script_path")
        #my.checkout_panel_script_path = my.kwargs.get("checkout_panel_script_path")

        my.checkout_script_path = my.kwargs.get("checkout_script_path")
        my.validate_script_path = my.kwargs.get("validate_script_path")
        my.checkin_relative_dir = my.kwargs.get("checkin_relative_dir")
        if not my.checkin_relative_dir:
            my.checkin_relative_dir = ''
        
        my.lock_process = my.kwargs.get("lock_process")
        my.transfer_mode = my.kwargs.get("transfer_mode")
        my.mode = my.kwargs.get("mode")
        my.show_versionless_folder = my.kwargs.get("show_versionless_folder")
        my.checkin_ui_options = my.kwargs.get("checkin_ui_options")
        if not my.checkin_ui_options:
            my.checkin_ui_options = ''
        my.search_key = ''
        #parent_key = my.kwargs.get('parent_key')
        search_key = ''
        sobject = my.get_current_sobject()
        
        if sobject.get_id() == -1:
            return
        #my.sobject = sobject 
        my.snapshot = None
        my.snapshot_code = ''
        my.latest_snapshot_code = ''
        my.process = ''
        my.context = ''
        if sobject and sobject.get_base_search_type() in ['sthpw/task', 'sthpw/note']:
            my.process = sobject.get_value('process')
            my.context = sobject.get_value('context')
            try:
                parent = sobject.get_parent()
            except SearchException, e:
                parent = None
                if e.__str__().find('not registered') != -1:
                    pass
                elif e.__str__().find('does not exist for database') != -1:
                    pass    
                else:
                    raise
            except Exception, e:
                parent = None

            # find current snapshot for this:
            search_type = sobject.get_value("search_type")
            search_id = sobject.get_value("search_id")
            if search_type and search_id:
                snapshot = Snapshot.get_current(sobject.get_value('search_type'), sobject.get_value('search_id'), context= sobject.get_value('context'))
            else:
                snapshot = None

            if snapshot:
                snapshot_code = snapshot.get_code()

        else:
            my.process = my.get_option('process')
            parent = None


        if snapshot:
            
            sandbox_sobj = snapshot
        elif parent:
            type ='main'
            virtual_snapshot = Snapshot.create_new()
            virtual_snapshot_xml = '<snapshot process=\'%s\'><file type=\'%s\'/></snapshot>' % (my.process, type)
            virtual_snapshot.set_value("snapshot", virtual_snapshot_xml)
            virtual_snapshot.set_value("context", my.context)
            virtual_snapshot.set_value("process", my.process)
            virtual_snapshot.set_sobject(parent)
            sandbox_sobj = virtual_snapshot

        else:
            sandbox_sobj = sobject

        my.sandbox_dir = sandbox_sobj.get_sandbox_dir(file_type='main')
        #my.sandbox_wip_dir = '%s/WIP' %my.sandbox_dir
        my.sandbox_wip_dir = my.sandbox_dir
        
        my.checkout_label = my.checkout_script_path
        if not my.checkout_label:
            my.checkout_label = 'TACTIC default checkout script'
   
        my.behavior['mode'] = my.mode
        my.behavior['transfer_mode'] = my.transfer_mode
        my.behavior['sandbox_dir'] = my.sandbox_dir
        my.behavior['lock_process'] = my.lock_process
        my.behavior['checkout_script_path'] = my.checkout_script_path
        my.behavior['checkin_script_path'] = my.checkin_script_path
        my.behavior['validate_script_path'] = my.validate_script_path
        my.behavior['checkin_relative_dir'] = my.checkin_relative_dir
        my.behavior['checkin_ui_options'] = my.checkin_ui_options
        my.behavior['show_versionless_folder'] = my.show_versionless_folder
 

        return super(WorkElementWdg, my).get_display()
