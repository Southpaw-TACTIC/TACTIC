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

__all__ = ['ParallelStatusWdg', 'ParallelStatusEditWdg', 'ParallelStatusEditLoadWdg']

from pyasm.common import Environment, Common, Date
from pyasm.search import Search, SObject, SearchKey, SearchType
from pyasm.biz import Pipeline, StatusAttr, StatusEnum, Task
from pyasm.web import Table, HtmlElement, DivWdg, SpanWdg, Widget, WebContainer, AjaxLoader

from table_element_wdg import BaseTableElementWdg
from input_wdg import *
from shadowbox_wdg import IframeWdg
from statistic_wdg import CompletionBarWdg
from web_wdg import HintWdg, SwapDisplayWdg
from input_wdg import BaseInputWdg, CheckboxWdg

import re

class ParallelStatusWdg(BaseTableElementWdg):

    def init(my):
        my.bar_select = None
        my.label_select = None
        my.include_sub_task = None

        my.statistics = {}
        my.statistics2 = {}
        my.processes_order = []
        my.completed_processes = []


        my.label_select_value = "reg"
        my.desc_checkbox_value = "off"
        my.bar_select_value = "1"
        my.include_sub_task_value = False
        
        my.process_names = None
        my.recurse = False
        my.pipeline_code = None
        my.data = {}
        my.max_count = 0

    def is_editable(my):
        return False

    def set_process_names(my, process_names):
        my.process_names = process_names

    def set_pipeline(my, pipeline):
        my.pipeline_code = pipeline.get_code()

    def set_pipeline_code(my, pipeline_code):
        my.pipeline_code = pipeline_code

    def set_recurse(my, recurse=True):
        my.recurse = recurse

    def set_data(my, data):
        my.data = data

    def set_label_format(my, label_format):
        assert label_format in ['reg', 'small', 'abbr', 'none']
        my.label_select_value = label_format


    def preprocess(my):
        
        if my.sobjects:
            tasks = Task.get_by_sobjects(my.sobjects, my.process_names)
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
                status_attr = task.get_attr("status")
                process_count = len(status_attr.get_pipeline().get_processes())
                if process_count > my.max_count:
                    my.max_count = process_count

    def get_title(my):
        return "Task Status"


        
    def get_prefs(my):
        div = DivWdg('Bar Size: ')
        my.bar_select = FilterSelectWdg('progress_bar_size')
        bar_sizes = [x*2 + 1 for x in xrange(6)]
        my.bar_select.set_option('values', bar_sizes)
        my.bar_select.set_option('default', '3')
        div.add(my.bar_select)
        my.bar_select_value = my.bar_select.get_value()
        
        my.label_select = FilterSelectWdg('Label_Format')
        my.label_select_value = my.label_select.get_value()
        my.label_select.set_option('values', 'reg|small|abbr')
        my.label_select.set_option('default', 'reg')
        
        span = SpanWdg('Label Format: ', css='small')
        span.add(my.label_select)
        div.add(span) 

        my.desc_checkbox = FilterCheckboxWdg("Show Description", \
            'Show Description: ', css='small')
        my.desc_checkbox_value = my.desc_checkbox.get_value()

        div.add(my.desc_checkbox)

        my.include_sub_task = FilterCheckboxWdg("include_sub_task", \
            label="include sub tasks", css='small')
        my.include_sub_task_value = my.include_sub_task.is_checked()
        div.add(my.include_sub_task)
        return div


    def set_data(my, data):
        my.data = data

    def get_display(my):
        my.task_per_process_dict = {}
        
        # get the sobject and relevent parameters
        sobject = my.get_current_sobject()
        search_type = sobject.get_search_type()

        if my.pipeline_code:
            pipeline = Pipeline.get_by_code(my.pipeline_code)
        else:
            pipeline = Pipeline.get_by_sobject(sobject, allow_default=True)

        if not pipeline:
            # while default is auto-generated, an empty pipeline code will trigger this
            Environment.add_warning('missing pipeline code', \
                "Pipeline code is empty for [%s]" %sobject.get_code())
            return
        if my.include_sub_task_value:
            my.recurse = True

        processes = pipeline.get_processes(recurse=my.recurse)
        # filter out process names
        if my.process_names != None:
            filtered_processes = []
            for process in processes:
                if process.get_name() in my.process_names:
                    filtered_processes.append(process)

            processes = filtered_processes 


        # draw the proceses
        top = DivWdg()


        action = DivWdg()
        action.add_style("float: right")

        top.add(action)



        table = Table()
        table.add_style("font-size: 11px")
        top.add(table)

        #if my.max_count:
        #    percent_width = float(len(processes)) / float(my.max_count+1) * 100
        #else:
        #    percent_width = 100

        # we want them more squeezed together when in abbr mode
        if my.label_select_value != 'abbr':
            percent_width = 100
            table.add_style("width: %d%%" % percent_width)
        tr = table.add_row()
        
        for process in processes:
            completion_wdg = my.get_completion(sobject, process,\
                len(processes))
            if not completion_wdg:
                continue
            td = table.add_cell( completion_wdg )
            td.add_style('border-width: 0px')


        
        tr = table.add_row(css='underline')
        tr.add_color("color", "color")
        
        label_format = my.get_option("label_format")
        if not label_format:
            label_format =  my.label_select_value
       

        tup_list = my._get_labels(processes, label_format, show_sub_pipeline=my.is_ajax()) 
        style = ''
        for i, tup in enumerate(tup_list):
            name, process = tup
            span = SpanWdg()    
            child_pipeline = process.get_child_pipeline()
            if child_pipeline:
                
                title = SpanWdg()
                title.add("[%s]" % name)
                title.add_style("margin-left: -5px")

                swap = SwapDisplayWdg.get_triangle_wdg()
                content_id =  '%s_%s' %(sobject.get_search_key(), child_pipeline.get_id())
                content_id = my.generate_unique_id(content_id)
                content = DivWdg(id=content_id)

                SwapDisplayWdg.create_swap_title(title, swap, content)

                dyn_load = AjaxLoader(display_id=content_id)

                args_dict = {'search_type': sobject.get_search_type()}
                args_dict['search_id'] = sobject.get_id()
                args_dict['pipeline_skey'] = child_pipeline.get_search_key()
                dyn_load.set_load_method('_get_child_wdg')
                dyn_load.set_load_class('pyasm.widget.ParallelStatusWdg', load_args=args_dict)
                dyn_load.add_element_name('cal_sub_task')
                on_script = dyn_load.get_on_script(load_once=True)

                swap.add_action_script(on_script, "set_display_off('%s')" %content_id)

                script = "if ($(%s).getStyle('display')=='none') {%s}" \
                    %(swap.swap1_id, on_script)
                title.add_event('onclick', script)
                

                span.add(swap)
                span.add(title)
                span.add(HtmlElement.br())
                span.add(HtmlElement.br())
              
                span.add(content)

            else:
                span.add(name)
                if my.task_per_process_dict.get(process) == 0:
                    span.add_class('unused')

            if label_format == 'small' or label_format == 'abbr':
                span.add_class('smaller')
            if not label_format == "none":
                table.add_cell(span)


        return top


    def _get_child_wdg(my):
        ''' this method is called thru ajax '''
        web = WebContainer.get_web()
        args = web.get_form_args()
        
        # get the args in the URL
        search_type = args['search_type']
        search_id = args['search_id']
        pipeline_search_key = args['pipeline_skey']
        sobject = Search.get_by_id(search_type, search_id)
        child_pipeline = Search.get_by_search_key(pipeline_search_key)
        status_wdg = ParallelStatusWdg()
        status_wdg.set_sobject(sobject)
        status_wdg.set_pipeline(child_pipeline)
        status_wdg.preprocess()
        return status_wdg

    def get_bottom(my):
        if my.get_option("report") == "false":
            return Widget()

        table = Table()
        table.add_row_cell("Report")
        table.add_row()
        table.add_blank_cell()
        table.add_cell("# Tasks")
        table.add_cell("Completion")
        

        for process in my.processes_order:
            my._draw_stat_row(table, process)
           
        return table


    def _draw_stat_row(my, table, process):
        table.add_row()
        if process.is_from_sub_pipeline():
            name = process.get_full_name()
        else:
            name = process.get_name()
        table.add_cell(name)

        total_tasks = my.statistics2.get(process)
        if not total_tasks:
            total_percentage = 0
        else:
            total_percentage = my.statistics.get(process) / total_tasks

        completion = CompletionBarWdg(total_percentage, 50)

        table.add_cell( str(total_tasks) )
        table.add_cell( completion )
    
    def _get_labels(my, processes, label_format, show_sub_pipeline=False):
        '''return a tuple of label, process'''
        process_names = []
        if show_sub_pipeline:
            if label_format == 'abbr':
                for process in processes:
                    tup = process.get_name()[0:3], process
                    process_names.append(tup)
            else:
                for process in processes:
                    tup = process.get_name(), process
                    process_names.append(tup)
            return process_names

        if label_format == 'abbr':
            for process in processes:
                if not process.is_from_sub_pipeline():
                    tup = process.get_name()[0:3], process
                    process_names.append(tup)
        else:
            for process in processes:
                if not process.is_from_sub_pipeline():
                    tup = process.get_name(), process
                    process_names.append(tup)
                    
        return process_names



    def get_completion(my, sobject, process, processes_count):
        '''get the completion of a particular task'''
        # get the tasks
        search_type = sobject.get_search_type()
        search_id = sobject.get_id()
        tasks = my.data.get("%s|%s" % (search_type,search_id) )
        if not tasks:
            tasks = []

       
        # filter the process
        my.tasks = []
        for task in tasks:
            task_value = task.get_value("process")
            if task_value != process.get_name() \
                    and task_value != process.get_full_name():
                continue
            my.tasks.append(task)
        # record no. of tasks per process
        my.task_per_process_dict[process] = len(my.tasks)
        
       
        task_percent = 0
        

        for task in my.tasks:
            status_attr = task.get_attr("status")
            percent = status_attr.get_percent_completion()
            
            # this adjustment has to be done after the bar is drawn
            if percent < 0:
                percent = 0
            task_percent += percent

        if my.tasks:
            task_percent /= len(my.tasks)
       
        total_percent = my.statistics.get(process)
        if not total_percent:
            total_percent = 0

        total_tasks = my.statistics2.get(process)
        if not total_tasks:
            total_tasks = 0


        my.statistics[process] = total_percent + task_percent
        my.statistics2[process] = total_tasks + len(my.tasks)
        if process not in my.processes_order:
            my.processes_order.append(process)

        # if this is a subpipeline and not in ajax mode(subpipe drawing)
        if process.is_from_sub_pipeline() and not my.is_ajax():
            return None

        # draw the widget

        bars = DivWdg()
        # each bar is 10px wide, but just add 2px for safety factor
        #bars_width = 12 * len(my.tasks)
        #if bars_width:
        #    bars.add_style('width', '%spx' %bars_width)
        if my.max_count == 0:
            my.max_count = 6
        for task in my.tasks:
            status_attr = task.get_attr("status")
            percent = status_attr.get_percent_completion()
            bars.add(my._get_bar(percent, my.max_count, task))
 
        return bars



    def _get_bar(my, percent, proc_count, task):
        '''get a vertical bar indicating the progress of a task '''
        sobject = my.get_current_sobject()
        bar = DivWdg()
        if my.desc_checkbox_value == "on":
            bar.add_style('margin-right: 20px')
        else:
            bar.add_style('width: 10px')
        bar.add_style('float: left')
        cur_percent = 100.0
        increment = 100.0 / proc_count
        
        # get some task info
        assigned = 'unassigned'
        process = task.get_value('process')
        if task.get_value('assigned').strip():
            assigned = task.get_value('assigned')
            
        task_desc = task.get_value('description')
        if not task_desc:
            task_desc = 'n/a'

        start_date = task.get_value("bid_start_date")
        end_date = task.get_value("bid_end_date")
        if start_date:
            start_date = Date(db_date=start_date, show_warning=False).get_display_date()
        else:
            start_date = "?"
        if end_date:
            end_date = Date(db_date=end_date, show_warning=False).get_display_date()
        else:
            end_date = "?"

        # remove some spacing characters
        task_desc = re.sub('(\n|\r|\t)', ' ', task_desc)
        task_desc = re.sub('"', "'", task_desc)
        task_status = task.get_value('status')

        display_percent = percent
        if percent < 0:
            task_status = "%s <font color=red>(obsolete)</font>" % task_status
            display_percent = 0
      
        msg =  '<b>%s</b><br/><hr>%s<br/><span style=padding-left:1em>desc: %s</span><br/>' \
            '<span style=padding-left:1em>status:%s (%s%%)</span><br/>'\
            '<span style=padding-left:1em>%s - %s</span>'\
            % (process, assigned, task_desc, task_status, display_percent, start_date, end_date)
       
        if WebContainer.get_web().get_browser() == "IE":
            bar.add_event('onmouseover', "hint_bubble.show(event, '%s')" %msg)
        else:
            bar.add_tip(msg)



        from pyasm.widget import IconWdg
        end_date = task.get_value("bid_end_date")
        end_date = Date(db_date=end_date, show_warning=False)
        now_date = Date(show_warning=False)
        if now_date.get_utc() > end_date.get_utc() and percent != 100:
            alert_color = "#f00"
        else:
            alert_color = None


        for x in xrange(proc_count):
            cur_percent -= increment
            div = DivWdg()
            content = '&nbsp;'
            # unidentified status probably
            if percent < 0:
                content = '&mdash;'
                div.add_style('text-decoration: blink')
        
            div.add(content)
            div.add_style('width: 10px')
            if cur_percent < percent or cur_percent == 0:
                if alert_color:
                    div.add_style("background-color: %s" % alert_color)
                else:
                    div.add_style("background-color: %s" % my._get_color_code(percent))


            bar_height = my.get_option("bar_height")
            if not bar_height:
                bar_height = my.bar_select_value
            if not bar_height:
                bar_height = '3'
            div.add_style("height: %spx" % bar_height)
            # IE needs to set the font size to reduce the overall size
            div.add_style("font-size: %spx" % bar_height )
            if sobject.is_retired():
                div.add_class('task_status_bar_retired')
            else:
                if my.label_select_value == "abbr":
                    div.add_style("margin: -1px")

                #div.add_class("task_status_bar")
                #div.add_style("margin-top: 2px")
                div.add_border()
           
            
            bar.add(div)

        if my.desc_checkbox_value == "on":
            span = SpanWdg(task_desc)
            span.add_style('font-size: 0.8em')
            bar.add( span )
       
        return bar


    def _get_color_code(my, percent):
        ''' get a color code based on percentage of task completion '''
        color = "#ddd"
        if percent > 80:
            color = "#b5e868"
        elif percent > 50:
            color = "#e8e268"
        elif percent > 30:
            color = "#e8c268"
        elif percent > 10:
            color = "#e86868"
       
        return color

    def handle_td(my, td):
        td.add_style('vertical-align','bottom')



class ParallelStatusEditWdg(BaseTableElementWdg):

    def is_editable(my):
        return False

    def get_display(my):
        parent = my.get_current_sobject()
        parent_key = SearchKey.get_by_sobject(parent)

        div = DivWdg()

        from pyasm.widget import IconButtonWdg, IconWdg
        icon = IconButtonWdg("Add Task", IconWdg.ADD)
        div.add(icon)
        #div.add("Add Tasks")
        div.add_class("hand")
        div.add_behavior( {
            "type": "click_up",
            "parent_type": parent.get_base_search_type(),
            "cbfn_action": "spt.dg_table.add_tasks_cbk",
        } )

        content = DivWdg()
        content.add_class("content")
        div.add(content)


        return div



from tactic.ui.common import BaseRefreshWdg
class ParallelStatusEditLoadWdg(BaseRefreshWdg):

    ARGS_KEYS = {
        'search_key': {
        'description': 'parent of the tasks to be found',
	'type': 'TextWdg',
        'category': 'internal'
        },
        'expression': {
        'description': 'expression to control the type of tasks to get',
	'type': 'TextWdg',
        'category': '2.Display'
	}
    }


    def get_display(my):
        parent_key = my.kwargs.get("search_key")
       
        assert(parent_key)

        parent = SearchKey.get_by_search_key(parent_key)

        parent_type = parent.get_base_search_type()

        # this is for backwards compatibility for ProcessSelectWdg
        web = WebContainer.get_web()
        web.set_form_value("parent_search_type", parent_type);

        div = DivWdg()
        if my.kwargs.get("__hidden__"):
            div.add_style("margin-top: -2px")
            div.add_style("margin-left: 0px")

        if parent.get_code() == '-1':
            div.add('You can only add task for an existing item.')
            return div


        from tactic.ui.panel import TableLayoutWdg, FastTableLayoutWdg

        expression = my.kwargs.get('expression')
        if not expression:
            expression = ''
        # title is used for panel refresh overlay
        table = FastTableLayoutWdg(
            search_type="sthpw/task", view="inline_add_item",
            mode="insert", search_key=parent_key,
            state={'search_key': parent_key},
            expression=expression, title='Task Edit',
            __hidden__=my.kwargs.get("__hidden__"))

        div.add(table)

        return div


"""

__all__.append("TaskGearElementWdg")
from tactic.ui.common import BaseRefreshWdg
from tactic.ui.container import SmartMenu
class TaskGearElementWdg(BaseTableElementWdg):
    '''Gear Menu for Page Header'''

    def init(my):
        pass


    def get_args_keys(my):
        return {
        }


    def handle_td(my, td):
        td.add_class("spt_input_inline")
        td.add_attr("spt_input_type", "gantt")
        td.add_attr("spt_input_column", my.get_name())


    def get_display(my):


        top = DivWdg()
        top.add_class("spt_task_gear_top")

        #hidden = HiddenWdg(my.get_name())
        #top.add(hidden)


        # use a checkbox instead

        checkbox = CheckboxWdg(my.get_name())

        top.add_behavior( {
            "type": "click_up",
            "cbjs_action": '''
            var checkbox = bvr.src_el.getElement(".spt_input");
            checkbox.setStyle("border", "solid 1px blue");
            checkbox.checked = true;

           '''
        } )

        top.add(checkbox)
        return top

#            var td = checkbox.getParent(".spt_table_td");
#            spt.dg_table.edit.widget = td.getElement('.spt_task_gear_top');
#
#            spt.dg_table_action.set_commitable(spt.dg_table.edit.widget, checkbox);
 


        menus = [ my.get_main_menu(), my.get_edit_menu() ]

        btn_dd = DivWdg()
        btn_dd.add_styles("width: 36px; height: 18px; padding: none; padding-top: 1px;")

        btn_dd.add( "<img src='/context/icons/common/transparent_pixel.gif' alt='' " \
                    "title='TACTIC Actions Menu' class='tactic_tip' " \
                    "style='text-decoration: none; padding: none; margin: none; width: 4px;' />" )
        btn_dd.add( "<img src='/context/icons/silk/cog.png' alt='' " \
                    "title='TACTIC Actions Menu' class='tactic_tip' " \
                    "style='text-decoration: none; padding: none; margin: none;' />" )
        btn_dd.add( "<img src='/context/icons/silk/bullet_arrow_down.png' alt='' " \
                    "title='TACTIC Actions Menu' class='tactic_tip' " \
                    "style='text-decoration: none; padding: none; margin: none;' />" )

        btn_dd.add_behavior( { 'type': 'hover',
                    'mod_styles': 'background-image: url(/context/icons/common/gear_menu_btn_bkg_hilite.png); ' \
                                    'background-repeat: no-repeat;' } )
        smenu_set = SmartMenu.add_smart_menu_set( btn_dd, { 'DG_TABLE_GEAR_MENU': menus } )
        SmartMenu.assign_as_local_activator( btn_dd, "DG_TABLE_GEAR_MENU", True )

        top.add(btn_dd)
        return top


    def get_main_menu(my):
        return { 'menu_tag_suffix': 'MAIN', 'width': 160, 'opt_spec_list': [
            #{ "type": "submenu", "label": "Edit", "submenu_tag_suffix": "EDIT" },
            { "type": "action", "label": "Add Pipeline Tasks",
                "bvr_cb": {'cbjs_action': '''
                var activator = spt.smenu.get_activator(bvr);
                var td = activator.getParent(".spt_table_td");
                var hidden = td.getElement(".spt_input");
                spt.dg_table.edit.widget = td.getElement('.spt_task_gear_top');
                hidden.value = "true";
                spt.dg_table_action.set_commitable(spt.dg_table.edit.widget, hidden);
                '''
                }
            },


        ] }


    def get_edit_menu(my):
        return {
            'menu_tag_suffix': 'EDIT', 'width': 160, 'opt_spec_list': [

                { "type": "title", "label": "Edit" },

                { "type": "action", "label": "Undo Transaction",
                    "bvr_cb": {'cbjs_action': "spt.undo_cbk();"}
                },

                { "type": "action", "label": "Redo Transaction",
                    "bvr_cb": {'cbjs_action': "spt.redo_cbk();"}
                },

                { "type": "action", "label": "Show Transaction Log",
                    "bvr_cb": {
                        'cbjs_action': "spt.popup.get_widget(evt, bvr)",
                        'options': {
                            'class_name': 'tactic.ui.popups.TransactionPopupWdg',
                            'title': 'Transaction Log',
                            'popup_id': 'TransactionLog_popup'
                        }
                    }
                }

        ] }


"""
