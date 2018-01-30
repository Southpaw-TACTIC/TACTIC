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


__all__ = ['NotificationSelectWdg', 'SearchTypeSelectWdg', 'PipelineSelectWdg',
        'TaskStatusElementWdg', 'TaskStatusSelectWdg','SObjectStatusElementWdg',
        'SelectCalendarInputWdg']

from pyasm.web import Widget, DivWdg, HtmlElement
from pyasm.widget import SelectWdg, TextWdg
from pyasm.search import Search, SearchType, SObject, SearchException
from pyasm.biz import Project, Pipeline, Task
from pyasm.common import Environment


class NotificationSelectWdg(SelectWdg):
    ''' a select of notification codes '''
    def __init__(self,  name='notification_select', css=''):
        super(NotificationSelectWdg, self).__init__(name)
        
    def init(self):
        search = Search(CommandSObj)
        search.add_column('notification_code')
        search.add_group_by('notification_code')
        self.set_search_for_options(search, 'notification_code','notification_code')
      

class SearchTypeSelectWdg(SelectWdg):
    ''' a select of production search types, so no sthpw search types'''
    (ALL, CURRENT_PROJECT, ALL_BUT_STHPW) = range(3)

    def __init__(self,  name='search_type_select', label='', css='', mode=None):
        self.mode = mode
        super(SearchTypeSelectWdg, self).__init__(name,  label=label, css=css)

    def get_display(self):
        
        #defining init is better than get_display() for this kind of SelectWdg
        search = Search( SearchType.SEARCH_TYPE )
        
        if self.mode == None or self.mode == self.ALL_BUT_STHPW:
            # always add the login / login group search types
            filter = search.get_regex_filter("search_type", "login|task|note|timecard|trigger|milestone", "EQ")
            no_sthpw_filter = search.get_regex_filter("search_type", "^(sthpw).*", "NEQ")   
            search.add_where('%s or %s' %(filter, no_sthpw_filter))
        elif self.mode == self.CURRENT_PROJECT:
            project = Project.get()
            project_code = project.get_code()
            #project_type = project.get_project_type().get_type()
            project_type = project.get_value("type")
            search.add_where("\"namespace\" in ('%s','%s') " % (project_type, project_code))

        
        search.add_order_by("search_type")

        search_types = search.get_sobjects()
        values = SObject.get_values(search_types, 'search_type')
        labels = [ x.get_label() for x in search_types ]
        values.append('CustomLayoutWdg')
        labels.append('CustomLayoutWdg')
        self.set_option('values', values)
        self.set_option('labels', labels)
        #self.set_search_for_options(search, "search_type", "get_label()")
        self.add_empty_option(label='-- Select Search Type --')

        return super(SearchTypeSelectWdg, self).get_display()

from pyasm.widget import BaseInputWdg
class PipelineSelectWdg(SelectWdg):

    def get_display(self):

        widget = DivWdg()

        pipeline_code = self.get_option('pipeline')
        pipeline = Pipeline.get_by_code(pipeline_code)
        if not pipeline:
            widget.add("No pipeline defined")
            return widget
            

        processes = pipeline.get_process_names()

        widget.add_style("border: solid 1px blue")
        widget.add_style("position: absolute")
        widget.add_style("top: 300")
        widget.add_style("left: -500")

        for process in processes:

            #inputs = pipeline.get_input_processes(process)
            outputs = pipeline.get_output_processes(process)

            div = DivWdg()
            widget.add(div)
            div.add_class("spt_input_option")
            div.add_attr("spt_input_key", process)

            #if not outputs:
            #    # then we can't go anywhere, so just add a message
            #    text = ""
            #    div.add(text)
            #    continue

            values = []
            #values.extend( [str(x) for x in inputs] )
            values.append(process)
            values.extend( [str(x) for x in outputs] )


            select = SelectWdg(self.get_input_name())
            select.set_value(process)
            select.add_empty_option('-- Select --')
            select.set_option("values", values)
            div.add(select)

            from tactic.ui.panel import CellEditWdg
            CellEditWdg.add_edit_behavior(select)


        return widget


from tactic.ui.common import SimpleTableElementWdg
class TaskStatusElementWdg(SimpleTableElementWdg):

    ARGS_KEYS = {
    'edit_scope': {
        'description': 'Determines who can edit the status.',
        'order': 0,
        'category': 'Options',
        'type': 'SelectWdg',
        'values': 'all|assigned',
        'default': 'all',
    },
    }

    def preprocess(self):

        self.set_option("empty", "true")

        # This assumes the parent is the same
        sobject = self.get_current_sobject()
        self.parent = None
        if sobject:
            try:
                self.parent = sobject.get_parent()
            except SearchException as e:
            
                if e.__str__().find('not registered') != -1:
                    pass     
                elif e.__str__().find('does not exist for database') != -1:
                    pass    
                else:
                    raise

            except Exception as e:
                print "Exception: ", e




    def add_value_update(self, value_wdg, sobject, name):

        if sobject.get_base_search_type() == "sthpw/task":
            colors = sobject.get_status_colors()

            # FIXME: use the default colors
            colors = colors.get("task")
        else:
            colors = {
                    'complete': '#FBB'
            }

        value_wdg.set_json_attr("spt_colors", colors)

        value_wdg.add_update( {
            'search_key': sobject.get_search_key(),
            'column': name,
            'interval': 4,
            'cbjs_action': '''
            var parent = bvr.src_el.getParent(".spt_cell_edit");
            var colors = JSON.parse( bvr.src_el.getAttribute("spt_colors") );
            var value = bvr.value;
            var color = colors[value];
            parent.setStyle("background", color);
            bvr.src_el.innerHTML = value;
            parent.setAttribute("spt_input_value", value);
            '''
        } )
 




    def handle_td(self, td):
        sobject = self.get_current_sobject()

        edit_scope = self.get_option("edit_scope")
        if edit_scope == "assigned":
            login = Environment.get_user_name()
            user = Environment.get_login()
            security = Environment.get_security()
            if not security.is_admin() and login != sobject.get_value("assigned"):
                td.add_class("spt_cell_no_edit")

 
        # find the pipeline code of the task
        pipeline_code = sobject.get_value('pipeline_code', no_exception=True)
        parent_pipeline_code = ''
        if self.parent:
            parent_pipeline_code = self.parent.get_value('pipeline_code', no_exception=True)

        if sobject.get_base_search_type() == "sthpw/snapshot":
            pipeline_code = "snapshot"

        # if not find the pipeline of the parent and match the process
        if not pipeline_code:
            task_process = sobject.get_value("process")
            if task_process:

                parent = self.parent
                if parent:
                    parent_pipeline_code = parent.get_value('pipeline_code', no_exception=True)
                    pipeline = Pipeline.get_by_code(parent_pipeline_code)
                    if pipeline:
                        attributes = pipeline.get_process_attrs(task_process)
                        pipeline_code = attributes.get('task_pipeline')


        value = self.get_value()
        color = Task.get_default_color(value)
        
        # If task status  pipeline is chosen, 
        # use color attribute from status (process)
        if pipeline_code:
            td.set_attr("spt_pipeline_code", pipeline_code)

            pipeline = Pipeline.get_by_code(pipeline_code)
            
            if pipeline:
                #attributes = pipeline.get_process_attrs(value)
                #color = attributes.get("color")
                process = pipeline.get_process(value)
                if process:
                    color = process.get_color()
                    if not color: 
                        process_sobject = pipeline.get_process_sobject(value)
                        if process_sobject:
                            color = process_sobject.get_value("color") 

        if color:
           td.add_style("background-color: %s" % color)


        if parent_pipeline_code:
            td.set_attr("spt_parent_pipeline_code", parent_pipeline_code)
        super(TaskStatusElementWdg, self).handle_td(td)



class TaskStatusSelectWdg(SelectWdg):
    def __init__(self, name=None):
        super(TaskStatusSelectWdg,self).__init__(name)
        self.is_preprocess = False
   
    

    def preprocess(self):
        '''determine if this is for EditWdg or EDIT ROW of a table'''
        # get the number of task pipelines needed for EditWdg, which is one
        # for the EDIT ROW , there could be more than 1

        self.task_mapping = {}
        from tactic.ui.panel import EditWdg
        if hasattr(self, 'parent_wdg') and isinstance(self.get_parent_wdg(), EditWdg):
            task = self.get_current_sobject()
            task_pipe_code = task.get_value('pipeline_code', no_exception=True)

            # if the current task has no pipeline, then search for
            # any task pipeline
            if not task_pipe_code:
                # just use the default
                task_pipe_code = 'task'
            
            pipeline = Pipeline.get_by_code(task_pipe_code)
            if not pipeline:
                pipeline = Pipeline.get_by_code('task')
            self.task_pipelines = [pipeline]
        else:


            # get all of the pipelines for tasks
            search = Search('sthpw/pipeline')
            search.add_regex_filter('search_type', 'sthpw/task')
            self.task_pipelines = search.get_sobjects()

            # get all of the pipelines for the current search_type
            search_type = self.state.get("search_type")
            
            search = Search('sthpw/pipeline')
            if search_type:
                search.add_filter('search_type', search_type)
            self.sobject_pipelines = search.get_sobjects()
            # insert the default task pipeline if not overridden in the db
            #default_task_found = False
            pipeline_codes = SObject.get_values(self.task_pipelines, 'code')
           
            
            #if not default_task_found:
            default_pipe = Pipeline.get_by_code('task')
            self.task_pipelines.append(default_pipe)
            default_pipe = Pipeline.get_by_code('approval')
            self.task_pipelines.append(default_pipe)
            default_pipe = Pipeline.get_by_code('progress')
            self.task_pipelines.append(default_pipe)
            default_pipe = Pipeline.get_by_code('milestone')
            self.task_pipelines.append(default_pipe)
            default_pipe = Pipeline.get_by_code('snapshot')
            self.task_pipelines.append(default_pipe)
            
            
            self.task_mapping = {}

            # the following works for insert but on edit, it should read from pipeline_code attribute
            for pipeline in self.sobject_pipelines:
                processes = pipeline.get_process_names()
                for process in processes:
                    attrs = pipeline.get_process_attrs(process)
                    task_pipeline = attrs.get('task_pipeline')
                    
                    if task_pipeline:
                        key = '%s|%s' %(pipeline.get_code(), process)
                        self.task_mapping[key] = task_pipeline

          


        self.is_preprocess = True


    def get_display(self):
        if not self.is_preprocess:
            self.preprocess()

        widget = DivWdg()
        widget.add_class('spt_input_top')

        # add a callback to determine the input key
        widget.add_attr('spt_cbjs_get_input_key', "return spt.dg_table.get_status_key(cell_to_edit, edit_cell)")

        # add a data structure mapping, processes to task pipelines
        #data = {
        #    "model": "task_model",
        #    "texture": "task_texture",
        #    "rig":  "task_rig"
        #}
        
        if self.task_mapping:
            json_str = HtmlElement.get_json_string(self.task_mapping)
            widget.add_attr('spt_task_pipeline_mapping', json_str)

        for pipeline in self.task_pipelines:
            div = DivWdg()
            widget.add(div)
            div.add_class("spt_input_option")

            div.add_attr("spt_input_key", pipeline.get_code())
         
            # if there is not task_pipeline_code, create a virtual one:
            if not pipeline:
                status_names = ['Pending', 'In Progress', 'Complete']
            else:
                status_names = pipeline.get_process_names()


            allowed_statuses = []
            security = Environment.get_security()
            cur_value = ''
            cur_sobject = self.get_current_sobject()
            if cur_sobject:
                cur_value = cur_sobject.get_value('status')

            #processes = ['Synopsis', 'First Draft', 'Second Draft', 'Final']
            processes = [None]
            for process in processes:

                for status in status_names:
                    # not all statuses can be shown, if there are access rules
                    # TODO: remove this status in 4.1
                    if cur_value == status or security.check_access("process_select", status, access='view', default='deny'):

                        if process:
                            allowed_statuses.append("%s / %s" % (process, status))
                        else:
                            allowed_statuses.append(status)
                        continue


                    # use the new access rule process here
                    access_key = [
                        {'process': '*' ,'pipeline':  pipeline.get_code()},
                        {'process': '*' ,'pipeline':  '*'},
                        {'process': status , 'pipeline':  pipeline.get_code()}
                        ]

                    if security.check_access('process', access_key, "view", default="deny"):
                        if process:
                            allowed_statuses.append("%s / %s" % (process, status))
                        else:
                            allowed_statuses.append(status)

                if process: 
                    allowed_statuses.append("---")

            select = SelectWdg(self.get_input_name())
            select.add_empty_option('-- Select --')
            if cur_value in allowed_statuses:
                select.set_value( cur_value )
            select.set_option("values", allowed_statuses)
            # only old table layout has behaviors at the widget level
            if self.behaviors:
                from tactic.ui.panel import CellEditWdg
                CellEditWdg.add_edit_behavior(select)

            div.add(select.get_buffer_display())
        
        return widget



class SObjectStatusElementWdg(SimpleTableElementWdg):

    def handle_td(self, td):
        sobject = self.get_current_sobject()

        value = self.get_value()
        color = Task.get_default_color(value)

        if color:
           td.add_style("background-color: %s" % color)

        super(SObjectStatusElementWdg, self).handle_td(td)




__all__.append('DependentSelectWdg')
class DependentSelectWdg(SelectWdg):
    '''Contains a number of SelectWdg which can be use based on the key
    of another element'''

    def get_value(self):
        if not self.sobjects:
            return ''

        sobject = self.sobjects[0]
        return sobject.get_value(self.get_name())



    def get_display(self):
        query = self.get_option("query")
        depend_col = self.get_option("dependency")

        # for example
        # FIXME: this has to be fleshed out ... it's a little too complicated
        # at the moment!!!
        query = "MMS/product_type|id|product_name"
        depend_col = "discipline_id"
        depend_element = 'discipline'

        top = DivWdg()
        top.add_class("spt_input_top")

        top.add_attr("spt_cbjs_get_input_key", "var value=spt.dg_table.get_element_value(cell_to_edit, '%s');return value" % depend_element)

        top.add_style("background: black")

        # get all of the sobjects
        search_type, value_col, label_col = query.split("|")
        search = Search(search_type)
        sobjects = search.get_sobjects()

        # arrange the sobjects according to keys
        selections = {}
        for sobject in sobjects:
            depend_value = sobject.get_value(depend_col)
            selection_list = selections.get(depend_value)
            if not selection_list:
                selection_list = []
                selections[depend_value] = selection_list

            selection_list.append(sobject)
            

        # put in a default
        default_div = DivWdg()
        default_div.add_class("spt_input_option")
        default_div.add_attr("spt_input_key", "default")
        default_div.add("No options for selected [%s]" % depend_element)
        top.add(default_div)



        # add  list of possible select statements
        for key, selection_list in selections.items():

            div = DivWdg()
            div.add_class("spt_input_option")
            div.add_attr("spt_input_key", key)

            values = []
            labels = []
            for sobject in selection_list:
                values.append(sobject.get_value(value_col))
                labels.append(sobject.get_value(label_col))

            select = SelectWdg(self.get_input_name())
            select.add_empty_option('-- Select --')
            select.set_option("values", values)
            select.set_option("labels", labels)
            div.add(select)

            from tactic.ui.panel import CellEditWdg
            CellEditWdg.add_edit_behavior(select)

            top.add(div)

        return top



__all__.append('DynLoadSelectWdg')
from tactic.ui.common import BaseRefreshWdg
class DynLoadSelectWdg(BaseRefreshWdg):
    '''Dynamically load a select widget'''

    def get_value(self):
        if not self.sobjects:
            return ''

        sobject = self.sobjects[0]
        return sobject.get_value(self.get_name())



    def get_display(self):

        top = DivWdg()
        top.add_class("spt_input_top")


        div = DivWdg()
        div.add_class("spt_input_option")
        key = 'main'
        div.add_attr("spt_input_key", key)


        query = self.kwargs.get("query");
        query_filter = self.kwargs.get("query_filter");

        input_name = self.kwargs.get("name");

        select = SelectWdg(input_name)
        select.add_empty_option('-- Select --')

        values = self.kwargs.get("values")
        if values:
            select.set_option("values", values)
            labels = self.kwargs.get("labels")
            if labels:
                select.set_option("labels", labels)
        else:
            select.set_option("query", query)
            select.set_option("query_filter", query_filter)

        div.add(select)

        from tactic.ui.panel import CellEditWdg
        CellEditWdg.add_edit_behavior(select)

        top.add(div)

        return top








__all__.append('ComboSelectWdg')
class ComboSelectWdg(SelectWdg):
    def get_display(self):
        return ''

        search_types = 'MMS/discipline.MMS/product_type'.split(".")

        top = DivWdg()
        parents = None
        for search_type in search_types:

            if not parents:
                search = Search(search_type)
                sobjects = search.get_sobjects()

                columns = search.get_columns()
                column = columns[1]

                select = SelectWdg(search_type)
                select.set_option("values", [x.get_id() for x in sobjects] )
                select.set_option("labels", [x.get_value(column) for x in sobjects] )
                top.add(select)
            else:
                for parent in parents:

                    search = Search(search_type)
                    search.add_relationship_filter(parent)
                    sobjects = search.get_sobjects()

                    if not sobjects:
                        continue

                    columns = search.get_columns()
                    column = columns[1]


                    values = [x.get_id() for x in sobjects]
                    labels = [x.get_value(column) for x in sobjects]


                    select = SelectWdg(search_type)
                    select.add_attr("spt_input_key", parent.get_id() )
                    select.set_option("values", values )
                    select.set_option("labels", labels )
                    top.add(select)

            parents = sobjects
        return top


class SelectCalendarInputWdg(SelectWdg):
    '''Contains a select and a CalendarInputWdg. When the calendar key matches,
       you can click again to access the CalendarInputWdg'''
  
    ARGS_KEYS = SelectWdg.ARGS_KEYS.copy()
    ARGS_KEYS.update({
        'calendar_key': {
            'description': "The value that makes the Calendar visible",
            'type': 'TextWdg',
            'order': 4,
            'category': 'Required'
           
            }
        })

    def init(self):
        self.calendar_key = self.kwargs.get('calendar_key')

    def get_display(self):
        from calendar_wdg import CalendarInputWdg
        top = DivWdg()
        top.add_class("spt_input_top")

        if not self.calendar_key:
            self.calendar_key = 'read'

        top.add_attr("spt_cbjs_get_input_key", \
            "var value=spt.dg_table.get_element_value(cell_to_edit, '%s'); return value" %self.get_name())

        #top.add_style("background: black")

        # put in a default
        default_sel = SelectWdg(self.get_name())
        for key, value in self.kwargs.items():
            default_sel.set_option(key, value)

      
        sel_div = DivWdg(css='spt_input_option')
        sel_div.add_attr("spt_input_key", "default")
        #default_div.add("No options for selected [%s]" % depend_element)
        sel_div.add(default_sel)
        top.add(sel_div)
      

        cal = CalendarInputWdg(self.get_name())


        cal_div = DivWdg(css='spt_input_option')
        cal_div.add_attr("spt_input_key", self.calendar_key)
        cal_div.add(cal)

        from tactic.ui.panel import CellEditWdg
        CellEditWdg.add_edit_behavior(default_sel)

        top.add(cal_div)

        return top
 

