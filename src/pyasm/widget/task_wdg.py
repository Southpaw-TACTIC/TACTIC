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


__all__ = ['TaskSObjectEditCmd','TaskAssetCreateSelectWdg', 'TaskSObjectSelectWdg', 'TaskProcessSelectWdg',
    'SObjectTaskTableElement', 'TaskWarningTableElement', 'TaskExtraInfoWdg',
    'TaskParentInputWdg', 'TaskParentSpacingTableElement',
    'UserAssignWdg', 'UserAssignContainerWdg', 'UserAssignCommand']


from pyasm.common import *
from pyasm.search import SearchType, Search, SearchKey, SearchException
from pyasm.web import *
from pyasm.command import *
from pyasm.search import Search
from pyasm.biz import Task, Pipeline, SimpleStatusAttr

from pyasm.web import HtmlElement, WidgetSettings 

from table_element_wdg import ExpandableTextWdg, DateWdg, SimpleTableElementWdg
from input_wdg import BaseInputWdg, SelectWdg, HiddenWdg, FilterCheckboxWdg, FilterSelectWdg, MultiSelectWdg 
from serial_status import SimpleStatusWdg
from icon_wdg import IconWdg, IconButtonWdg
from web_wdg import *
from timecard_wdg import *
from statistic_wdg import CalendarBarWdg
from creator_wdg import CreateSelectWdg

# FIXME: this is a circular import which fails on batch scripts.
# In order to fix, we have to move the classes that use the new
# BaseTableElementWdg to the tactic.ui.widget directory.
# Leaving them here for now because a lot of these are old classes and some
# are deprecated.
try:
    from tactic.ui.common import BaseTableElementWdg
except:
    from table_element_wdg import BaseTableElementWdg

def get_search_type():
    web = WebContainer.get_web()
    search_type = web.get_form_value("parent_search_type")
    if not search_type:
        search_type = web.get_form_value("search_type")
    return search_type



class TaskSObjectEditCmd(DatabaseAction):

    def execute(my):
        value = my.get_value()
        if value == "":
            return

        search_type, search_id = value.split("|")

        my.sobject.set_value("search_type", search_type)
        my.sobject.set_value("search_id", search_id)


class TaskAssetCreateSelectWdg(CreateSelectWdg):
    ''' Create a list of asset for multi task creations'''  
    
    def init_setup(my):
       
        hidden = HiddenWdg(my.DELETE_MODE)
        my.add_ajax_input(hidden)
        hidden = HiddenWdg(my.NEW_ITEM)
        my.add_ajax_input(hidden)
        hidden = HiddenWdg(my.NEW_ITEM_LABEL)
        my.add_ajax_input(hidden)
        hidden = HiddenWdg("code_col")
        my.add_ajax_input(hidden)
        if not my.is_from_ajax():
            hidden.set_value(my.get_option('code_col'))
        my.add(hidden)

        hidden = HiddenWdg('ref_search_type')
        my.add_ajax_input(hidden)
        if not my.is_from_ajax():
            hidden.set_value(my.web.get_form_value('ref_search_type'))
        my.add(hidden)
        hidden = HiddenWdg('search_id')
        my.add_ajax_input(hidden)
       
        if my.is_from_ajax():
            col_name = my.web.get_form_value('col_name')
        else:
            col_name = my.get_name()
        my.col_name = HiddenWdg('col_name', col_name)
        my.add_ajax_input(my.col_name)

        my.select_items = HiddenWdg('%s|%s' %(col_name, my.SELECT_ITEMS))
        my.add_ajax_input(my.select_items)

    def get_delimiter(my):
        return '||'    

    def get_search_key(my):
        search_key = '%s|%s' % (my.web.get_form_value('ref_search_type'), \
            my.web.get_form_value('search_id'))
        return search_key

    def get_item_list(my, items):
        my.select = SelectWdg(my.SELECT_NAME)
        my.select.set_attr("size", '%s' %(len(items)+1))
        if items == ['']:
            return my.select
        my.select.set_option('values', items)
        code_col = my.web.get_form_value('code_col')
        labels = []
        # assume they are all the same search type
        search_ids = [item.split("|", 1)[1] for item in items]
        search_type = ''
        if items:
            search_type = items[0].split('|', 1)[0]
        if search_type and search_ids: 
            sobjs =  Search.get_by_id(search_type, search_ids)
            for sobj in sobjs:
                name = sobj.get_name()
                code = sobj.get_code()
                if code_col and sobj.has_value(code_col):
                    code = sobj.get_value(code_col) 
                if name == code:
                    labels.append(code)
                else:
                    labels.append('%s - %s' %(code, name))
        
        my.select.set_option('labels', labels)
        return my.select

    def get_type_select(my, item_type):
        return FloatDivWdg('&nbsp;', width=100)

    def draw_widgets(my, widget, delete_widget, item_span):
        '''actually drawing the widgets'''
        widget.add(item_span)
        widget.add(HtmlElement.br(2))
        widget.add(SpanWdg(my.select, css='med'))
        widget.add(delete_widget)
        widget.add(HtmlElement.br(2))
        

    def get_sequence_wdg(my):
        text_span = SpanWdg('New item ')
        current = my.get_my_sobject()
        search_type = get_search_type()
        select = SelectWdg(my.NEW_ITEM)
        select.set_option('web_state', my.get_option('web_state') )
        
        # get all of the options for this search type
        search = Search(search_type)
        search.add_order_by("code")
        sobjects = search.get_sobjects()
        if not sobjects:
            raise SetupException("No Assets defined.  Please create assets to add tasks to")

        values = [x.get_search_key() for x in sobjects]

        labels = []
           
        code_col = my.web.get_form_value('code_col')
        
        for x in sobjects:
            name = x.get_name()
            code = x.get_code()
            if code_col and x.has_value(code_col):
                code = x.get_value(code_col) 
            if name == code:
                labels.append(code)
            else:
                labels.append("%s - %s" % (code, name) )

        select.set_option("values", values)
        select.set_option("labels", labels)
        # transfer the options
        for key, value in my.options.items():
            select.set_option(key, value)
        
        # extra code not needed here. setting web_state to true in the config
        # is sufficient, still not perfect yet.
        if not current:
            pass
        else:
            search_key = "%s|%s" % (current.get_value("search_type"), current.get_value("search_id") )
            select.set_value(search_key)

        button = my.get_sequence_button()
        text_span.add(select)
        text_span.add(button)
        return text_span

    def get_sequence_button(my):
        # add button
        widget = Widget()
        from pyasm.prod.web import ProdIconButtonWdg
        add = ProdIconButtonWdg('Add')
        script = ["append_item('%s','%s')" % (my.SELECT_NAME, my.NEW_ITEM )]
        script.append( my.get_refresh_script() )
        add.add_event('onclick', ';'.join(script))
        widget.add(add)

        hint = HintWdg('Add one or more items to the list.', title='Tip') 
        widget.add(hint)
        return widget

class TaskSObjectSelectWdg(BaseInputWdg):

    def get_display(my):

        current = my.get_current_sobject()
        parent_search_type = current.get_value('search_type')
        if not parent_search_type:
            return "No parent type"


        search_type = parent_search_type
        web = WebContainer.get_web()

        is_edit = not current.is_insert()
        # start a search
        search = Search(search_type)

        widget = Widget()
        # avoid a search key == '|'
        parent_search_key = ''
        if is_edit and current.get_value("search_type"):
            parent_search_key = "%s|%s" % (current.get_value("search_type"), current.get_value("search_id") )
        #parent_search_key = web.get_form_value("edit|parent")

        my.categorize(widget, search_type, search)
         
        select = SelectWdg(my.get_input_name())
        widget.add(select)
        select.set_option('web_state', my.get_option('web_state') )

        search.add_order_by("code")
        sobjects = [] 
        
        if is_edit:
            if parent_search_key: 
                sobjects = [Search.get_by_search_key(parent_search_key)]
        else:
            sobjects = search.get_sobjects()
        
        # Task planner task don't have a parent
        if not sobjects and search_type !='sthpw/task':
            span = SpanWdg("No Parents Defined. Parents for this task should be inserted first.")
            span.add_style("color: #f44")
            widget.add(span)
            return widget

        values = [x.get_search_key() for x in sobjects]

        labels = []
        code_col = my.get_option('code_col')
        
        for x in sobjects:
            name = x.get_name()
            code = x.get_code()
            if code_col and x.has_value(code_col):
                code = x.get_value(code_col) 
            if name == code:
                labels.append(code)
            else:
                labels.append("%s - %s" % (code, name) )

        select.set_option("values", values)
        select.set_option("labels", labels)
        # transfer the options
        for key, value in my.options.items():
            select.set_option(key, value)
        
        # extra code not needed here. setting web_state to true in the config
        # is sufficient, still not perfect yet.
        if current.is_insert():
            pass
        else:
            select.set_value(parent_search_key)
        return widget


    def categorize(my, widget, search_type, search):
        '''categorize parents based on search_type'''
        # FIXME: this should not be here.  This is a general class for all
        # search types, not just prod/asset
        if my.get_option('read_only') != 'true':
            if search_type == "prod/asset":
                lib_select = FilterSelectWdg('parent_lib')
                lib_select.persistence = False
                search2 = Search("prod/asset_library")
                lib_select.set_search_for_options( search2, "code", "title" )
                lib_select.add_empty_option("-- Any --")
                widget.add(lib_select) 
                # get all of the options for this search type
                parent_lib = lib_select.get_value()
                if parent_lib:
                    search.add_filter('asset_library', parent_lib)
            elif search_type == "prod/shot":
                lib_select = FilterSelectWdg('parent_lib')
                lib_select.persistence = False
                search2 = Search("prod/sequence")
                lib_select.set_search_for_options( search2, "code", "code" )
                lib_select.add_empty_option("-- Any --")
                
                widget.add(lib_select)

                # get all of the options for this search type
                parent_lib = lib_select.get_value()
                if parent_lib:
                    search.add_filter('sequence_code', parent_lib)
            elif search_type == 'prod/texture':
                lib_select = FilterSelectWdg('parent_lib')
                lib_select.persistence = False
                search2 = Search("prod/texture")
                search2.add_column('category')
                search2.add_group_by("category")
                lib_select.set_search_for_options( search2, "category", "category" )
                lib_select.add_empty_option("-- Any --")
                widget.add(lib_select)

                # get all of the options for this search type
                parent_lib = lib_select.get_value()
                if parent_lib:
                    search.add_filter('category', parent_lib)
#
# TODO: this class is poorly named.  It should be AssetProcessSelectWdg
#
# This should be DEPRECATED!!
#
class TaskProcessSelectWdg(SelectWdg):

    def get_display(my):

        current = my.get_current_sobject()
        search_type = get_search_type()

        parent_key = WebContainer.get_web().get_form_value("edit|asset")
        if parent_key != "":
            parent = Search.get_by_search_key(parent_key)

            # get all of the options for this search type
            status_attr_name = "status"
            status_attr = parent.get_attr(status_attr_name)
            pipeline = status_attr.get_pipeline()
        else:
            # FIXME: make this general by looking at the current asset
            pipeline = Pipeline.get_by_name("flash_shot")

        processes = pipeline.get_process_names()
        my.set_option("values", "|".join(processes) )

        return super(TaskProcessSelectWdg,my).get_display()




class SObjectTaskTableElement(BaseTableElementWdg, AjaxWdg):
    '''lists all the tasks with the timeline as a table element'''
    PROCESS_FILTER_NAME = "process_filter"

    def init(my):
        my.sobject = None
        my.process_completion_dict = {}
        #super(SObjectTaskTableElement, my).__init__()
        my.data = {}
        my.calendar_bar = CalendarBarWdg()
        my.calendar_bar.set_option('width','100')
        my.is_refresh = False
        if my.kwargs.get('is_refresh')=='true':
            my.is_refresh = True
            my.init_cgi()

    def is_sortable(my):
        return False

    def is_searchable(my):
        return True

    def get_searchable_search_type(my):
        '''get the searchable search type for local search'''
        return 'sthpw/task'

    def alter_task_search(my, search, prefix='children', prefix_namespace='' ):
        from tactic.ui.filter import FilterData, BaseFilterWdg, GeneralFilterWdg
        filter_data = FilterData.get()
        parent_search_type = get_search_type()
        
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
            
            search.add_op('begin')
            GeneralFilterWdg.alter_sobject_search( search, values_list, prefix)
            if filter_mode != 'custom': 
                search.add_op(filter_mode)
        
        
        return search

    def preprocess(my):
        if my.sobjects:
            try:
                search = Search(Task) 
                search_ids = [x.get_id() for x in my.sobjects]
                search.add_filters("search_id", search_ids)
                search_type = my.sobjects[0].get_search_type()
                search.add_filter("search_type", search_type)
                
                # go thru children of main search
                search = my.alter_task_search(search, prefix='children')
                # go thru Local Search
                search = my.alter_task_search(search, prefix='main_body', prefix_namespace=my.__class__.__name__)

                sobj = my.sobjects[0]
                pipeline = Pipeline.get_by_sobject(sobj) 
                if pipeline:
                    process_names = pipeline.get_process_names(True)
                    search.add_enum_order_by("process", process_names)
                else:
                    search.add_order_by("process")

                search.add_order_by("id")
                tasks = search.get_sobjects()
                # create a data structure
                for task in tasks:
                    search_type = task.get_value("search_type")
                    search_id = task.get_value("search_id")
                    search_key = "%s|%s" % (search_type, search_id)

                    sobject_tasks = my.data.get(search_key)
                    if not sobject_tasks:
                        sobject_tasks = []
                        my.data[search_key] = sobject_tasks
                    sobject_tasks.append(task)
            except:
                from tactic.ui.app import SearchWdg
                parent_search_type = get_search_type()
                SearchWdg.clear_search_data(parent_search_type)
                raise

    def get_prefs(my):
        from pyasm.prod.web import UserFilterWdg
        if UserFilterWdg.has_restriction():
            return ''
        else:
            widget = Widget()
            cb = FilterCheckboxWdg('show_all_tasks', label='show all tasks')
            sub_cb = FilterCheckboxWdg('show_sub_tasks', label='show sub tasks')
            widget.add(cb)
            widget.add(sub_cb)
            return widget

        

    def get_title(my):
        # create the calendar
        widget = Widget()
    
        my.calendar_bar.set_user_defined_bound(False) 

        widget.add(my.calendar_bar.get_calendar())
        widget.add( super(SObjectTaskTableElement,my).get_title() )

        assign_cont = UserAssignContainerWdg() 
        widget.add(assign_cont)

        widget.add(my.calendar_bar.get_show_cal_script())
        return widget

    def init_cgi(my):
        #if not my.is_ajax(check_name=True):
        #    return
        my.data = {}
        # get the sobject
        keys = my.web.get_form_keys()
        search_key = ''
        for key in keys:
            if key.startswith('skey_SObjectTaskTableElement_'):
                search_key = my.web.get_form_value(key)
        if search_key:
            my.sobject = Search.get_by_search_key(search_key)
            my.sobjects = [my.sobject]
    
        # adding the CalendarBarWdg
        my.calendar_bar = CalendarBarWdg()
        my.calendar_bar.set_option('width','100')
        my.calendar_bar.set_option('bid_edit', my.get_option('bid_edit'))
        my.calendar_bar.set_user_defined_bound(False)

        # run preprocess
        my.preprocess()
        my.add(my.calendar_bar.get_calendar())

    def init_setup(my, widget):
        my.reset_ajax()
        
        hidden = HiddenWdg('skey_SObjectTaskTableElement_%s' \
            %my.sobject.get_id(), my.sobject.get_search_key())
        widget.add(hidden)
        
        # add the search_key input
        my.add_ajax_input(hidden)
       
        # add the filter inputs
        hidden = HiddenWdg('task_status')
        my.add_ajax_input(hidden)
        hidden = HiddenWdg('show_assigned_only')
        my.add_ajax_input(hidden)
        hidden = MultiSelectWdg('user_filter')
        my.add_ajax_input(hidden)
        hidden = HiddenWdg('show_all_tasks')
        my.add_ajax_input(hidden)
        hidden = HiddenWdg('show_sub_tasks')
        my.add_ajax_input(hidden)
        # put the display option in here
        #hidden = HiddenWdg('doption_SObjectTaskTableElement')
        #my.add_ajax_input(hidden)

  
    def get_display(my):

        web = WebContainer.get_web()
        
        # this needs to be a BaseInputWdg since UserFilterWdg is hideable
        user_filter = FilterSelectWdg("user_filter")
        user_filter = user_filter.get_values()
     
        #login = Environment.get_security().get_login()
        #user = login.get_value("login")

        if my.is_refresh:
            widget = Widget()
            my.init_cgi()
        else:
            my.sobject = my.get_current_sobject()
            widget = DivWdg(id="task_elem_%s"% my.sobject.get_id())
            widget.add_class('spt_task_panel')
            try:
                my.set_as_panel(widget)
            except:
                pass
       
        #TODO: remove this
        my.init_setup(widget)
        #my.set_ajax_top(widget)
        
        table = Table(css="minimal")
        table.add_style("width: 100%")

        # get all of the tasks related to this sobject
        search_type = my.sobject.get_search_type()
        search_id = my.sobject.get_id()
        if my.data:
            tasks = my.data.get("%s|%s" % (search_type,search_id) )
        else:
            tasks = Task.get_by_sobject(my.sobject)
            my.data[my.sobject.get_search_key()] = tasks
        if not tasks:
            tasks = []


        task_statuses_filter = web.get_form_values("task_status")
        show_sub_tasks = False
        if not task_statuses_filter:
            # NOTE: Not sure if this is correct!!
            # have to do this because it is impossible to tell if a checkbox
            # is empty or not there.  This is used for pages that do not have
            # tasks_status checkboxes
            show_all_tasks = True
        else:
            cb = FilterCheckboxWdg('show_all_tasks') 
            show_all_tasks = cb.is_checked(False)

            sub_cb = FilterCheckboxWdg('show_sub_tasks') 
            show_sub_tasks = sub_cb.is_checked(False)
        # trim down the process list
        """
        if not show_sub_tasks:
            process_list = [x for x in process_list if "/" not in x]
        """
        pipeline = Pipeline.get_by_sobject(my.sobject)

        # retrieve the pipeline   
        if not pipeline:
            td = table.add_cell("<br/><i>No pipeline</i>")
            td.add_style("text-align: center")
            return table

        # store completion per process first in a dict
        # reset it first
        my.process_completion_dict = {}
        for task in tasks:
            task_process = task.get_value("process")
            status_attr = task.get_attr('status')
            percent = status_attr.get_percent_completion()
            
            my.store_completion(task_process, percent)

        security = WebContainer.get_security()
        me = Environment.get_user_name()

        

        for task in tasks:
            has_valid_status = True
            task_pipeline = task.get_pipeline()
            task_statuses = task_pipeline.get_process_names()
            task_process = task.get_value("process")

            # Commenting this out.  It is not very meaningful in 2.5 ...
            # we need a better mechanism.  The end result of this code
            # is that "admin" never sees any tasks
            #if security.check_access("public_wdg", "SObjectTaskTableElement|unassigned", "deny", is_match=True):
            #    assignee = task.get_value("assigned")
            #    if assignee != me:
            #        continue


            if not show_all_tasks:
                """
                if process_list and task_process not in process_list:
                    continue
                """
                # skip sub tasks
                if not show_sub_tasks and '/' in task_process:
                    continue

                task_status = task.get_value("status")
                if task_status not in task_statuses:
                    has_valid_status = False

                if has_valid_status  and task_status \
                        and task_status not in task_statuses_filter:
                    continue
                # the first one shouldn't be empty
                if user_filter and user_filter[0] and task.get_value("assigned") not in  user_filter:
                    continue
                
            table.add_row()

            
            #link = "%s/Maya/?text_filter=%s&load_asset_process=%s" % (web.get_site_context_url().to_string(), my.sobject.get_code(), task_process)
            #icon = IconButtonWdg("Open Loader", IconWdg.LOAD, False)
            #table.add_cell( HtmlElement.href(icon, link, target='maya') )

            td = table.add_cell(css='no_wrap')

            description = task.get_value("description")
            expand = ExpandableTextWdg()
            expand.set_max_length(50)
            expand.set_value(description)
            assigned = task.get_value("assigned").strip()

            status_wdg = SimpleStatusWdg()
            status_wdg.set_sobject(task)
            status_wdg.set_name("status")
            # refresh myself on execution of SimpleStatusCmd
            #post_scripts = my.get_refresh_script(show_progress=False)
            post_scripts = '''var panel = bvr.src_el.getParent('.spt_task_panel');
                              var search_top = spt.get_cousin(bvr.src_el, '.spt_view_panel','.spt_search');
                              var search_val = spt.dg_table.get_search_values(search_top);
                              var values = spt.api.Utility.get_input_values(panel);
                              values['json'] = search_val;
                              spt.panel.refresh(panel, values);'''
            status_wdg.set_post_ajax_script(post_scripts)
    
            if assigned:
                user_info = UserExtraInfoWdg(assigned).get_buffer_display()
            else:
                user_info = HtmlElement.i(" unassigned").get_buffer_display()

            info_span = SpanWdg()
            
            info_span.add(TaskExtraInfoWdg(task))
            info_span.add("- ")
            
            info_span.add("&nbsp;[%s]" % user_info)


            if UserAssignWdg.has_access() and my.get_option('supe')=='true':
                my._add_user_assign_wdg(task, info_span, widget) 

            td.add( info_span )

            #--------------

            my.calendar_bar.set_sobject(task)
            # set always recalculate since each task is set individually
            my.calendar_bar.set_always_recal(True)

            #---------------

            td.add_color('color','color')
            td.add(HtmlElement.br())
            if description:
                td.add(expand)
                td.add(HtmlElement.br())
            td.add(status_wdg)

            if my.last_process_finished(pipeline, task_process): 
                dot = IconWdg(icon=IconWdg.DOT_GREEN)
                dot.add_tip("All dependent processs complete")
                dot.add_style('float','left')
                dot.add_style('display','block')
                td.add(dot)
            else:
                dot = IconWdg(icon=IconWdg.DOT_RED)
                dot.add_tip("Dependent process in progress")
                dot.add_style('float','left')
                dot.add_style('display','block')
                td.add(dot)

            
            
            date_display = None
            if my.get_option('simple_date') == 'true':
                start_wdg = DateWdg()
                start_wdg.set_option("pattern", "%b %d")
                start_wdg.set_name('bid_start_date')
                start_wdg.set_sobject(task)
                end_wdg = DateWdg()
                end_wdg.set_name('bid_end_date')
                end_wdg.set_option("pattern", "%b %d")
                end_wdg.set_sobject(task)
                date_display = '%s - %s' %(start_wdg.get_buffer_display(), \
                    end_wdg.get_buffer_display())
            else:
                my.calendar_bar.set_sobject(task)
                # set always recalculate since each task is set individuallly
                my.calendar_bar.set_always_recal(True)

                my.calendar_bar.set_option("width", "40")
                my.calendar_bar.set_option("bid_edit", my.get_option('bid_edit'))
                date_display = my.calendar_bar.get_buffer_display()
            
            #td = table.add_cell(date_display, css='smaller')
            td.add(FloatDivWdg(date_display, float='right', css='smaller')) 
                
            #td.set_style("width: 120; padding-left: 15px")

            # This uses the parallel status widget to display status of
            # dependent tasks
            dependent_processes = pipeline.get_input_contexts(task_process)


            from parallel_status import ParallelStatusWdg
            dep_status_div = DivWdg()
            dep_status_div.add_style("padding-right: 10px")
            dep_status_wdg = ParallelStatusWdg()
            dep_status_wdg.set_process_names(dependent_processes)
            dep_status_wdg.set_label_format("abbr")
            dep_status_wdg.set_sobject(my.sobject)
            
            #dep_status_wdg.preprocess()
            dep_status_wdg.set_data(my.data)
            dep_status_div.add(dep_status_wdg)
            td.add(dep_status_div)
            #td.add_style("border-style: solid")
            #td.add_style("border-bottom: 1px")
            #td.add_style("border-color: #999")
            td.add_style("padding: 3px 0 3px 0")

        
        widget.add(table)
       
        return widget

    def _add_user_assign_wdg(my, task, info_span, widget):
        ''' add a user assignment icon '''
        icon = IconWdg('assign', icon=IconWdg.ASSIGN)
        icon.add_class('hand') 
        assign = UserAssignWdg(check_name=True)
        assign.set_task(task)

        # UserAssignWdg will take care of filtering duplicated refresh scripts
        # eventually it is added into this widget below via assign.get_post_data()
        assign.set_post_ajax_script(my.get_refresh_script(show_progress=False)) 

        script = []
        script.append("Common.follow_click(event, '%s', 12, -15)" \
            % UserAssignContainerWdg.CONTAINER_ID)
        script.append( "set_display_on('%s')" \
            % UserAssignContainerWdg.CONTAINER_ID)
        script.append(assign.get_refresh_script())
        
        icon.add_event('onclick', ';'.join(script))
        info_span.add(icon)
        widget.add(assign.get_post_data())

    def _has_assign_wdg_access(my):
        ''' check if the user can see this user assignment wdg '''
        security = Environment.get_security()
        group_names = security.get_group_names()
        access_manager = security.get_access_manager()

        if my.get_option('supe') == 'true':
            for group in group_names:
                if security.check_access("UserAssignWdg", group, "view"):
                    return True

        return False
    
    def store_completion(my, process, percent):
        ''' store the completion percentage per process in a dict'''
        status_list = my.process_completion_dict.get(process)
        if not status_list:
            status_list = []
            my.process_completion_dict[process] = status_list
        status_list.append(percent)

    def last_process_finished(my, pipeline, task_process, is_subpipeline=False):
        ''' find if the last process is finished '''
        if not pipeline:
            return True
        last_processes = pipeline.get_backward_connects(task_process)
        # TODO: use get_input_processes
        #last_processes = pipeline.get_input_processes(task_process)

        # subpipeline scenario
        if task_process.find("/") != -1:
            pipeline_code, process = task_process.split("/", 1)
            pipeline = Pipeline.get_by_code(pipeline_code)
            return my.last_process_finished(pipeline, process, is_subpipeline=True)
        # the first process of the pipe should be green-lit
        if not last_processes:
            return True
        for process in last_processes:
    
            # if the process is from another pipeline
            # TODO: disabling for now
            
            
            full_process = process
            if is_subpipeline:
                full_process = '%s/%s' %(pipeline.get_code(), process)
            complete_list = my.process_completion_dict.get(full_process)
            

            # skip processes that have no tasks
            # count is a safe-guard in case pipeline.get_backward_connects()
            # does not return None or [] in the future by accident
            # so the limit for a pipeline is 60 processes for now.
            count = 0
            while not complete_list and last_processes and count < 60:
                count = count + 1
                last_processes =  pipeline.get_backward_connects(process)
                for process in last_processes:
                    full_process = process
                    if is_subpipeline:
                        full_process = '%s/%s' %(pipeline.get_code(), process)
                    complete_list = my.process_completion_dict.get(full_process)

            # previous processes have no tasks assigned, in other words, they are finished    
            if not complete_list:
                return True

            for item in complete_list:
                if item != 100:
                    return False
        return True
       



class TaskWarningTableElement(BaseTableElementWdg):

    def get_title(my):
        return "&nbsp;"

    def get_display(my):
        sobject = my.get_current_sobject()

        bid_start_time = str(sobject.get_value("bid_start_date"))
        bid_end_time = str(sobject.get_value("bid_end_date"))

        if bid_start_time == "":
            return "&nbsp;"
            

        now = Date().get_db_time()

        status = sobject.get_value("status")


        if status == "Pending" and now > bid_start_time:
            icon_wdg = IconWdg( "Start date has passed", IconWdg.ERROR )
            return icon_wdg

        if not bid_end_time:
            return "&nbsp;"

        if status != "Final" and now > bid_end_time:
            icon_wdg = IconWdg( "End date has passed", IconWdg.ERROR )
            return icon_wdg


        return "&nbsp;"



class TaskExtraInfoWdg(ExtraInfoWdg):

    def __init__(my, task=None):
        my.task = task 
        my.height = 150
        super(TaskExtraInfoWdg,my).__init__()

    def init(my):
        assert my.task
        super(TaskExtraInfoWdg, my).init()
        # create the visible element
        icon = IconWdg('Time Card', icon=IconWdg.TIME)
        my.add(icon)
        my.add(HtmlElement.b(my.task.get_process()))
       
        my.time_card = TimecardWdg()
        my.time_card.set_task(my.task)

        from pyasm.security import Login

        # create the content
        content = DivWdg()
        content.add_style('width','46em')
        

        # customize the extra info widget
        my.set_class('timecard_main')
        my.set_content(content)
        my.set_mouseout_flag(False)
        
        my.login = Login.get_by_login(my.task.get_assigned())
        title = FloatDivWdg()
        login_name = 'unassigned'
        my.is_other = False
        if my.login:
            login_name = my.login.get_full_name()
            if my.login.get_login() == Environment.get_login().get_login():
                icon = IconWdg(icon=IconWdg.REFRESH)
                icon.add_class('hand')
                icon.add_event('onclick', my.time_card.get_refresh_script())
                title.add(icon)
            else:
                my.is_other = True
            
        title.add("Time card - %s" % login_name)
        
        content.add(title)
        content.add(CloseWdg(my.get_off_script())) 
        content.add(HtmlElement.br(2))
        content.add(my.time_card, 'time')
        
        if not my.login:
            div = DivWdg(HtmlElement.b('Time card cannot be entered for unassigned task.'))
            content.set_widget(div, 'time')
            my.height = 60
        elif my.is_other:
            div = DivWdg(HtmlElement.b('Time card cannot be entered for other users [%s].'\
                %login_name))
            content.set_widget(div, 'time')
            my.height = 60
            


    def get_mousedown_script(my):
        
        script = [super(TaskExtraInfoWdg,my).get_mousedown_script(height=my.height)]
        if my.login and not my.is_other:
            script.append(my.time_card.get_refresh_script())
            
        return ';'.join(script)



# Series of task manipulation widgets and callbacks

class TaskParentSpacingTableElement(SimpleTableElementWdg):

    def preprocess(my):
        pass

    def handle_td(my, td):
        sobject = my.get_current_sobject()
        parent = None
        if sobject.is_insert():
            parent_key = my.state.get('parent_key')
            if parent_key:
                parent = SearchKey.get_by_search_key(parent_key)
        else:
            try:
                parent = sobject.get_parent()
            except SObjectSecurityException, e:
                pass
            except SearchException, e:
                if e.__str__().find('not registered') != -1:
                    pass
                elif e.__str__().find('does not exist for database') != -1:
                    pass    
                else:
                    raise
            process = sobject.get_value('process')

            current_value = sobject.get_value(my.get_name())
            if current_value:
                value = '%s||%s'%(process, current_value)

                td.add_attr("spt_input_value",  value)


        if parent:
            td.set_attr("spt_pipeline_code", parent.get_value("pipeline_code", no_exception=True))

    def get_display(my):
        sobject = my.get_current_sobject()

        context = sobject.get_value("context")
        div = DivWdg()
        div.set_attr("nowrap", "1")
        div.set_attr("tab", "0")
        div.set_attr("context", context)
        div.set_id("task_process_%s" % sobject.get_id() )

        if context.find("/") != -1:
            context, subcontext = context.split("/", 1)

        div.add(context)
        return div


"""
class TaskMoveCbk(Callback):

    def execute(my):

        web = WebContainer.get_web()

        direction = web.get_form_value("task_move_direction")

        task = Task.get_by_id(1013)

        if direction == "up":
            my.move_task_up(task)


    def move_task_up(my, task):

        # get all of the tasks of this sobject
        sobject = task.get_parent()
        tasks = Task.get_by_sobject(sobject)

"""




class TaskParentInputWdg(SelectWdg):

    def get_display(my):

        web = WebContainer.get_web()
        task = my.get_current_sobject()
        id = task.get_id()

        if task.is_insert():
            return HtmlElement.i("Dependency on insert not supported yet.")

        # get the sobject
        sobject = task.get_parent()
        if not sobject:
            return "No parent"

        tmp_tasks = Task.get_by_sobject(sobject)
        tasks = []
        for tmp_task in tmp_tasks:
            # skip the task self
            if tmp_task.get_id() == id:
                continue

            # prevent direct circular dependencies
            if tmp_task.get_value("depend_id") == id:
                continue

            tasks.append(tmp_task)


        ids = [x.get_id() for x in tasks]
        labels = []
        for task in tasks:
            process = task.get_value("process")
            description = task.get_value("description")
            if len(description) > 30:
                description = description[0:30]+"..."
            label = "%s - %s" % (process, description)
            labels.append(label)

        my.set_option("empty", "true")
        my.set_option("labels", labels)
        my.set_option("values", ids)
        

        return super(TaskParentInputWdg,my).get_display()


class ClipboardCopyTaskCmd(DatabaseAction):

    def get_display(my):

        clipboard_items = Clipboard.get_all()
        column = "depend_id"

        for item in clipboard_items:
            #item.set_value("
            pass











class UserAssignContainerWdg(DivWdg):
    '''this is the container for UserAssignWdg'''

    CONTAINER_ID = "user_assign_cont_wdg_id"

    def __init__(my):
        super(UserAssignContainerWdg, my).__init__(id=\
                my.CONTAINER_ID, css= "popup_wdg")

    
    def get_display(my):
        my.add_style('display: none')
        my.add_style('width: 180px')
        my.add_style('padding: 6px 6px 6px 6px')

        content_div = DivWdg(id = UserAssignWdg.USER_ASSIGN_WDG_ID)
        content_div.add_style('display: none')
        

        close = DivWdg('x', css='hand')
        close.set_style('float: right; padding-top: 1px')
        close.add_event('onclick', UserAssignContainerWdg.get_off_script())
        
        my.add(close)
        my.add(content_div)

        super(UserAssignContainerWdg, my).get_display()

    def get_off_script():
        return "Effects.fade_out('%s')" % UserAssignContainerWdg.CONTAINER_ID
    get_off_script = staticmethod(get_off_script)


class UserAssignWdg(AjaxWdg):
    ''' this is a dynamically generated popup widget for assigning user to task'''
    USER_ASSIGN_WDG_ID = "user_assign_wdg_id"
    ASSIGNMENT_ID = "assignment_id"
    TARGET_TASK_ID ='UserAssignWdg_target_search_key'

    def init(my):
        ''' initializes a few variables ''' 
        my.task = None
        my.main_div = None
        my.post_script = None
        my.post_script_dict = {}

    def init_cgi(my):
        ''' get the sobject '''
        keys = my.web.get_form_keys()
        search_key = ''

        for key in keys:
            # only one is expected
            if key.startswith('skey_UserAssignWdg_'):
                search_key = my.web.get_form_value(key)
                break
            
        if search_key:
            sobject = Search.get_by_search_key(search_key)
            my.task = sobject
            my.init_setup()

    def init_setup(my):
        '''set the ajax top and register some inputs'''
        div_id = my.USER_ASSIGN_WDG_ID
        my.main_div = DivWdg(id=div_id)
        
        my.set_ajax_top(my.main_div)
        
        # register the inputs first
        hidden = HiddenWdg('skey_UserAssignWdg_%s' %my.task.get_id())
        my.add_ajax_input(hidden)

        hidden = HiddenWdg('post_script_UserAssignCommand_%s' %my.task.get_value('search_id'))
        my.add_ajax_input(hidden)

        hidden = HiddenWdg(my.TARGET_TASK_ID)
        my.add_ajax_input(hidden)
        

    def set_task(my, task):
        my.task = task
        my.init_setup()

    def set_post_ajax_script(my, script):
        my.post_script = script

    def get_display(my):
        # add the popup
        div = my.main_div
       
        cmd = my.get_cmd()

        my.attached_sobj = my.task.get_parent()

        # assign post ajax script since this widget is dynamically generated
        hidden = HiddenWdg('post_script_UserAssignCommand_%s' % my.attached_sobj.get_id())
        my.post_script = [hidden.get_value()]

        # add SiteMenu refresh

        event_container = WebContainer.get_event_container()
        caller = event_container.get_event_caller(SiteMenuWdg.EVENT_ID)
        my.post_script.append(caller)

        progress = cmd.generate_div()
        progress.set_post_ajax_script(';'.join(my.post_script))
        
        from pyasm.prod.web import UserSelectWdg

        filter = UserSelectWdg(my.ASSIGNMENT_ID, label = 'assign to: ')
        #filter.persistence = False

        script = [cmd.get_on_script(show_progress=False)]
        script.append(UserAssignContainerWdg.get_off_script())

        filter.set_event('onchange', ';'.join(script))
        filter.add_empty_option('-- unassigned --', '')

        status = my.task.get_value('assigned')
        filter.set_value(status)
        div.add(filter)
        div.add(progress)

        div.add(HiddenWdg(my.TARGET_TASK_ID, my.task.get_search_key()))
        my.add(div)

        return super(UserAssignWdg, my).get_display()

    def get_cmd(my):

        cmd = AjaxCmd('UserAssignCmd')
        cmd.register_cmd('pyasm.widget.UserAssignCommand')
        cmd.add_element_name(my.ASSIGNMENT_ID)
        cmd.add_element_name(my.TARGET_TASK_ID)
    
        return cmd

    def get_post_data(my):
        ''' get the post data for this AjaxWdg'''
        widget = Widget()
        hidden = HiddenWdg('skey_UserAssignWdg_%s' %my.task.get_id(), my.task.get_search_key())
        widget.add(hidden)
        
        key = 'post_script_UserAssignCommand_%s' % my.task.get_value('search_id')            
        # avoid duplication
        dict_key = 'UserAssignCommand_ps:%s' %Environment.get_user_name()
        if not Container.get_dict(dict_key, key):
            hidden = HiddenWdg(key, my.post_script)
            widget.add(hidden)
            Container.put_dict(dict_key, key, my.post_script)
        
        return widget


class UserAssignCommand(Command):
   
    def get_title(my):
        return "User Assignment"

    def check(my):
        return True

    def execute(my):
        web = WebContainer.get_web()
        user_name = web.get_form_value(UserAssignWdg.ASSIGNMENT_ID)
       
        task = None 
        task_search_key = web.get_form_value(UserAssignWdg.TARGET_TASK_ID)
        if task_search_key:
            task = Search.get_by_search_key(task_search_key)
        if task:
            task.set_value('assigned', user_name)
            task.commit()

        sobject_code = task.get_parent().get_code()
        my.sobjects = [task]
        my.add_description("Assign [%s] to task in process [%s] for [%s]" \
            %(user_name, task.get_process(), sobject_code))
