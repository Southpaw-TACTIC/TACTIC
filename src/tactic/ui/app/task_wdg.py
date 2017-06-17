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

__all__ = ['AddTaskWdg', 'AddTaskCbk']

from pyasm.biz import Task
from pyasm.common import TacticException
from pyasm.command import Command
from pyasm.search import SObject, SearchKey, Search, SearchType
from pyasm.web import DivWdg, FloatDivWdg, SpanWdg, HtmlElement, WebContainer, Widget, Table
from pyasm.widget import CheckboxWdg, HintWdg, SelectWdg, IconWdg
from tactic.ui.common import BaseRefreshWdg
from tactic.ui.widget import ActionButtonWdg

class AddTaskWdg(BaseRefreshWdg):
    '''A Widget that allows bulk adding of tasks for selected sobjects'''

    ARGS_KEYS= {
                'search_key_list': 'list of search keys selected',
                'mode': 'matched or selected',
                'table_id': 'id of the table this is run on'
        }


    def init(my):
        my.mode = my.kwargs.get('mode')

        my.search_type = my.kwargs.get('search_type')
        my.view = my.kwargs.get('view')
        my.search_class = my.kwargs.get('search_class')
        my.search_view = my.kwargs.get('search_view')
        my.simple_search_view = my.kwargs.get('simple_search_view')
        my.table_id = my.kwargs.get('table_id')
        
        my.is_refresh = my.kwargs.get('is_refresh')

    
    def check(my):
        if my.mode == 'matched':
            from tactic.ui.panel import FastTableLayoutWdg
            table = FastTableLayoutWdg(search_type=my.search_type, view=my.view,\
                show_search_limit='false', search_limit=-1, search_view=my.search_view, \
                simple_search_view=my.simple_search_view, search_class=my.search_class)
            table.handle_search()
            search_objs = table.sobjects
            my.search_key_list = SearchKey.get_by_sobjects(search_objs, use_id=True)
            return True
        else:
            my.search_key_list = my.kwargs.get('search_key_list')
            if my.search_key_list and isinstance(my.search_key_list, basestring):
                my.search_key_list = eval(my.search_key_list)

    def get_display(my):
        my.check()
        if my.is_refresh:
            div = Widget()
        else:
            div = DivWdg()
            my.set_as_panel(div)
            div.add_style('padding','6px')
            min_width = '400px'
            div.add_style('min-width', min_width)
            div.add_color('background','background')
            div.add_class('spt_add_task_panel')
            div.add_style("padding: 20px")


        from tactic.ui.app import HelpButtonWdg
        help_button = HelpButtonWdg(alias="creating-tasks")
        div.add(help_button)
        help_button.add_style("float: right")
        help_button.add_style("margin-top: -5px")

        if not my.search_key_list:
            msg_div = DivWdg()
            msg_table = Table()
            msg_div.add(msg_table)
            msg_table.add_row()
            msg_table.add_cell( IconWdg("No items selected", IconWdg.WARNING) )
            msg_table.add_cell('Please select at least 1 item to add tasks to.')

            msg_div.add_style('margin: 10px')
            msg_table.add_style("font-weight: bold")
            div.add(msg_div)
            return div

        msg_div = DivWdg()
        msg_div.add_style('margin-left: 4px')
        div.add(msg_div, 'info')
        msg_div.add('Total: %s item/s to add tasks to' %len(my.search_key_list))
        div.add(HtmlElement.br())
        hint = HintWdg('Tasks are added according to the assigned pipeline.')
        msg_div.add(" &nbsp; ")
        msg_div.add(hint)
        msg_div.add(HtmlElement.br())
        
        
        option_div = DivWdg(css='spt_ui_options')
        #option_div.add_style('margin-left: 12px')
        
        sel = SelectWdg('pipeline_mode', label='Create tasks by: ')
        sel.set_option('values', ['simple process','context', 'standard'])
        sel.set_option('labels', ['process','context', 'all contexts in process'])
        sel.set_persistence()
        sel.add_behavior({'type':'change',
                 'cbjs_action': 'spt.panel.refresh(bvr.src_el)'}) 
        
        option_div.add(sel)

        value = sel.get_value()
        # default to simple process
        if not value:
            value = 'simple process'
        msg = ''
        if value not in ['simple process','context','standard']:
            value = 'simple process'
        
        if value == 'context':
            msg = 'In context mode, a single task will be created for each selected context.'
        elif value == 'simple process':
            msg = 'In process mode, a single task will be created for each selected process.'

        elif value == 'standard':
            msg = 'In this mode, a task will be created for all contexts of each selected process.'

        option_div.add(HintWdg(msg))
        div.add(option_div)
        div.add(HtmlElement.br())

        title = DivWdg('Assigned Pipelines')
        title.add_style('padding: 6px')
        title.add_color('background','background2')
        title.add_color('color','color', +120)
        div.add(title)
    
        content_div = DivWdg()
        content_div.add_style('min-height', '150px')
        div.add(content_div)
        content_div.add_border()
        
        filtered_search_key_list = []
        for sk in my.search_key_list:
            id = SearchKey.extract_id(sk)
            if id=='-1':
                continue
            filtered_search_key_list.append(sk)

        sobjects = SearchKey.get_by_search_keys(filtered_search_key_list)
        skipped = []
        pipeline_codes = []
        for sobject in sobjects:
            if isinstance(sobject, Task):
                msg_div = DivWdg('WARNING: Creation of task for [Task] is not allowed.')
                msg_div.add_style('margin-left: 10px')
                div.add(msg_div, 'info')
                return div
            pipeline_code = sobject.get_value('pipeline_code', no_exception=True)
            if not pipeline_code:
                skipped.append(sobject)
            if pipeline_code not in pipeline_codes:
                pipeline_codes.append(pipeline_code)
       

        pipelines = Search.get_by_code('sthpw/pipeline', pipeline_codes)
        if pipelines == None:
            pipelines = []
        #if not pipelines:
        #    msg_div = DivWdg('WARNING: No Pipelines found for selected.')
        #    msg_div.add_style('margin-left: 10px')
        #    div.add(msg_div, 'info')
        #    return div

        # expand the width according to num of pipelines
        content_div.add_style('min-width', len(pipelines)*250)
        mode_cb = SelectWdg('pipeline_mode') 
        mode_cb.set_persistence()
        mode = mode_cb.get_value()
        if 'context' == mode:
            mode = 'context'
        else:   
            mode = 'process'

        show_subpipeline = True
        min_height = '150px'



        # create a temp default pipeline
        if not pipelines:
            pipeline = SearchType.create("sthpw/pipeline")
            pipeline.set_value("code", "__default__")
            pipeline.set_value("pipeline", '''
<pipeline>
    <process name='publish'/>
</pipeline>
            ''')
            # FIXME: HACK to initialize virtual pipeline
            pipeline.set_pipeline(pipeline.get_value("pipeline"))
            pipelines = [pipeline]

        for pipeline in pipelines:
            name = pipeline.get_value("name")
            if not name:
                name = pipeline.get_code()
            span = SpanWdg("Pipeline: %s" % name)
            span.add_style('font-weight: bold')
            v_div = FloatDivWdg(span)
            v_div.add_style('margin: 20px')
            v_div.add_style('min-height', min_height)
            v_div.add(HtmlElement.br(2))
            content_div.add(v_div)    
            processes = pipeline.get_processes(recurse=show_subpipeline, type=['manual','approval'])

            cb_name = '%s|task_process'  %pipeline.get_code()
            master_cb = CheckboxWdg('master_control')
            master_cb.set_checked()
            master_cb.add_behavior({'type': 'click_up',
                'propagate_evt': True,
                'cbjs_action': '''
                    var inputs = spt.api.Utility.get_inputs(bvr.src_el.getParent('.spt_add_task_panel'),'%s');
                    for (var i = 0; i < inputs.length; i++)
                        inputs[i].checked = bvr.src_el.checked;
                        ''' %cb_name})
            toggle_div = DivWdg()
            toggle_div.add(SpanWdg(master_cb, css='small'))
            label = HtmlElement.i('toggle all')
            label.add_style('color: #888')
            toggle_div.add_styles('border-bottom: 1px solid #888; width: 170px')
            toggle_div.add(label)
            v_div.add(toggle_div)
            process_names = []

            for process in processes:
                process_labels = []
                if process.is_from_sub_pipeline():
                    process_name  = process.get_full_name()
                else:
                    process_name  = process.get_name()

                process_label = process.get_label()
                if not process_label:
                    process_label = ''
                if mode =='context':
                    contexts =  pipeline.get_output_contexts(process.get_name())
                    
                    labels = contexts
                    if process.is_from_sub_pipeline():
                        labels = ['%s/%s'%(process.parent_pipeline_code, x) for x in contexts]
                    
                    for x in labels: 
                        process_labels.append(process_label)
                    
                    # prepend process to contexts in this mode to ensure uniqueness
                    contexts = ['%s:%s' %(process_name, x) for x in contexts]
                else:
                    contexts = [process_name]
                    labels = contexts
                
                    process_labels.append(process_label)

                for idx, context in enumerate(contexts):
                    cb = CheckboxWdg(cb_name)
                    cb.set_checked()
                    cb.set_option('value', context)
                    v_div.add(SpanWdg(cb, css='small'))
                    if mode == 'context':
                        span = SpanWdg(process_name, css='med')
                        #span.add_color('color','color')
                        v_div.add(span)
                    v_div.add(SpanWdg(labels[idx]))
                    process_label = process_labels[idx]
                    if process_label:
                        v_div.add(SpanWdg("(%s)" %process_label, css='small'))
                    v_div.add(HtmlElement.br())
        
       
        content_div.add("<br clear='all'/>")

        skipped = [] 

        if True:
            div.add("<br/>")
            btn = ActionButtonWdg(title='Add Tasks')
            btn.add_behavior({'type' : 'click_up',
            'post_event': 'search_table_%s'% my.table_id,
            'cbjs_action': '''
            spt.dg_table.add_task_selected(bvr);
            ''',
            'search_key_list': my.search_key_list
            })
            cb = CheckboxWdg('skip_duplicated', label='Skip Duplicates')
            cb.set_checked()
            option_div =DivWdg(cb)
            option_div.add_style('width', '130px')
            option_div.add_style('align: left')
            div.add(option_div)
            div.add(HtmlElement.br())
            btn.add_style("float: right")
            div.add(btn)
            div.add(HtmlElement.br(clear="all"))


        if skipped:
            content_div.add(HtmlElement.br())
            skip_div = DivWdg('Missing pipeline code (Skipped)')
            skip_div.add_style('text-decoration: underline')
            content_div.add(skip_div)
            content_div.add(HtmlElement.br())
            item_div = DivWdg()
            item_div.add_style('margin-left: 10px')
            content_div.add(item_div)
        for skip in skipped:
            item_div.add(skip.get_code())
            item_div.add(HtmlElement.br())



        return div

class AddTaskCbk(Command):
    '''Callback to add tasks to multiple sobjects according to their corresponding pipelines'''

    def check(my):
        return True
    
    def execute(my):
        my.search_key_list = my.kwargs.get('search_key_list')
        web = WebContainer.get_web()
        skip_duplicated = web.get_form_value('skip_duplicated') == 'on'
        pipeline_mode = web.get_form_value('pipeline_mode')

        sobjects = SearchKey.get_by_search_keys(my.search_key_list)
        count = 0
        offset = 0
        for sobject in sobjects:
            if isinstance(sobject, Task):
                raise TacticException('Creation of task for [Task] is not allowed')
            sk = SearchKey.get_by_sobject(sobject)
            if not sobject.has_value('pipeline_code'):
                #raise TacticException('Creation of task is not allowed for item with no pipeline_code attribute.')
                pipeline_code = '__default__'
                sobject.set_value("pipeline_code", pipeline_code)
            else:
                pipeline_code = sobject.get_value('pipeline_code')
            input_name = '%s|task_process'% pipeline_code
            
            contexts = []
            process_names = web.get_form_values(input_name)
            process_names = [name for name in process_names if name]
            if pipeline_mode == 'context':
                # when pipeline_mode is context, we only specify contexts
                # in add_initial_tasks
                contexts = process_names[:]
                process_names = []
            tasks = Task.add_initial_tasks(sobject, sobject.get_value('pipeline_code'),
                    processes=process_names, contexts=contexts, skip_duplicate=skip_duplicated, mode=pipeline_mode, start_offset=offset)

            count += len(tasks)
            offset += 5
        my.add_description("%s Tasks added in total." % count)



