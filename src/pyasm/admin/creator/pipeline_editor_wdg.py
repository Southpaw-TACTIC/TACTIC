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

__all__ = ['PipelineEditorWdg', 'PipelineConnectionWdg', 'PipelineEditCmd', 
        'PipelineConnectEditCmd', 'PipelineConnectInsertCmd']

from pyasm.search import Search, SObject, Sql
from pyasm.common import *
from pyasm.biz import Pipeline, Project
from pyasm.web import *
from pyasm.widget import *
from pyasm.command import *
from pyasm.common import Xml
from pyasm.search import DbContainer, AlterTableUndo, SearchType
from pyasm.prod.web import ProdIconButtonWdg, ProjectFilterWdg

import re


# DEPRECATED

class PipelineEditorWdg(Widget):

    REORDER = "Reorder_View"
    CURRENT_PIPELINE = "Current_Pipeline"
    AUTO_CONNECT = "Forward Connect"
    UPDATE = "Update Pipeline"

    EDIT_ACTION = "edit_action"
    EDITED_CONTEXT = "edited_context"
    CUR_CONTEXT = "cur_context"
    FROM_PROCESS = "from_process"
    TO_PROCESS = "to_process"

    NEW_FROM_PROCESS = "new_from_process"
    NEW_TO_PROCESS = "new_to_process"
    NEW_CONTEXT = "new_context"

    def __init__(my):
       
        my.pipeline = None
        my.script_div = Widget()
        my.row_ids = []
        super(PipelineEditorWdg,my).__init__()

    def init(my):
        
        WebContainer.register_cmd("pyasm.admin.creator.PipelineEditCmd")

        my.add(HelpItemWdg('Pipelines tab', '/doc/general/pipeline.html', is_link=True))

        script = HtmlElement.script("""
        function remove_attr(name) {
            var rtn = remove_item("This will remove the process [" + name + "] from the pipeline.")
            return rtn
            }
        function remove_pipe(pipe_name) {
            var rtn = remove_item("This will remove the pipeline [" + pipe_name + "].")         
            return rtn
            }
        function remove_item(msg) {
            var agree = confirm( msg + " Are you sure?")
            if (agree)
                return true
            else
                return false
        }
        """)
        my.add(script)


        div = DivWdg(css="admin_section")
        my.add(div) 
        # set my.pipeline
        div.add( my._get_title_wdg() )

        div.add(HtmlElement.h3("Create a Pipeline"))
         
        div.add( my._get_create_pipe_wdg() )
        div.add(HtmlElement.br(2))
        
        div.add( my._get_create_attr_wdg() )

        div.add(HtmlElement.br())
        div.add(HiddenWdg(my.REORDER)) 
        
        div.add(HtmlElement.br())
       
        if not my.pipeline or not Pipeline.get_by_name(my.pipeline):
            return
        
        div.add(HtmlElement.h3("Edit a Pipeline"))
       
        div.add( my._get_views_attr_wdg(my.pipeline) )
     

        # setup script has to be added before the main script div
        setup_script = HtmlElement.script('SET_DHTML(CURSOR_MOVE,TRANSPARENT, "%s")' \
            % ('","'.join(my.row_ids)))
        my.add(setup_script)
        my.add(my.script_div)
        my.script_div.add(HtmlElement.script('''
        
var dy;
var top_elem_y;
var cur_y;
var cur_x;
var view;
var Elts;

// Array intended to reflect the order of the draggable items

function my_PickFunc()
{
    // Store position of the item about to be dragged
    // so we can interchange positions of items when the drag operation ends
    cur_y = dd.obj.y;
    cur_x = dd.obj.x;
    //alert('name ' + dd.obj.name)
    obj = document.getElementById(dd.obj.name)
    view = obj.getAttribute('view')
    Elts = eval(view + "_Elts")
    top_elem_y = dd.elements[Elts[0].id].y
    if (Elts[1])
        dy = dd.elements[Elts[1].id].y - top_elem_y
    else
        dy = top_elem_y
   
}
    
function my_DragFunc()
{
}

function my_DropFunc()
{
    // Calculate the snap position which is closest to the drop coordinates
    var y = dd.obj.y+dy/2;
    
    y = Math.max(top_elem_y, Math.min(y - (y-top_elem_y)%dy, top_elem_y + (Elts.length-1)*dy));
    // Index of the new position within the spatial order of all items
    
    var i = (y-top_elem_y)/dy;
    
    var old_i
    
    for (var k = 0; k < Elts.length; k++)
    {
        if (Elts[k] == dd.obj)
            old_i = k
    }
                
    if (i >= old_i)
    {
        for (k=old_i; k <= i; k++)
        {
            Elts[k].moveTo(cur_x, Elts[k].y -dy)
            Elts[k] = Elts[k+1]
        }
    }
    else
    {
        for (k=old_i; k >= i; k--)
        {
            Elts[k].moveTo(cur_x, Elts[k].y +dy)
            Elts[k] = Elts[k-1]
        }
    }
    // Let the dropped item snap to position
    dd.obj.moveTo(cur_x, y);
    
    // Update the array according to the changed succession of items
    Elts[i] = dd.obj;
    var Elts_id = new Array()
    for (k=0; k<Elts.length; k++)
        Elts_id[k] = Elts[k].id
    document.getElementsByName(view + "_Elts")[0].value = Elts_id.join(',')
    my_auto_fill(view, Elts_id)
     
}

/* 
    Auto-fill the forward links if the checkbox 'auto link' is checked
    forward link's name has a pattern <pipe_name>_<process>_flink 
*/
function my_auto_fill(pipe_name, Elts_id)
{
    var cb = document.getElementsByName('auto_link')[0]
    if (!cb.checked)
        return
    for (var i=0; i < Elts_id.length; i++)
    {
        text = document.getElementsByName(Elts_id[i] + '_flink')[0]
        if ((i+1) < Elts_id.length)
        {
            id = Elts_id[i+1].replace(pipe_name + '_' , '')
            text.value = id
        }
        else
            text.value = ''
        
    }    
           
}        
    
        '''))

        return




    def _get_views_attr_wdg(my, pipeline):
        Pipeline.clear_cache()
        pipe = Pipeline.get_by_name(pipeline)
       
        div = DivWdg()
        div.add_style('margin-left','2em')
        div.add(HtmlElement.br())
        table = Table()
        table.add_row()
        table.add_cell( my._get_list_attr_wdg(pipe) )

        table.add_row()
        table.add_blank_cell()
        
        table.add_row()
        table.add_cell( my._get_connect_div(pipe) )
    
        div.add(table)


        return div






    def _get_title_wdg(my):

        # create the select widget for the asset type
       
        project_filter = ProjectFilterWdg()
        select = FilterSelectWdg(PipelineEditCmd.CURRENT_PIPELINE)
        select.add_empty_option(select.SELECT_LABEL)
        #select.set_persistence()
        search = Search( Pipeline.SEARCH_TYPE )
     
        project_codes = project_filter.get_values()
        if project_codes and project_codes[0]:
            where = Project.get_project_filter(project_codes)
            search.add_where(where)
       
        search.add_order_by('code')
        select.set_search_for_options(search,"code", "code")
       
        title = DivWdg( css='filter_box')
        size = project_filter.get_navigator().attrs.get('size')
        if size > 2:
            size = int(size) +2
            title.add_style('height','%sem' %size)
        else:
            title.add_style('height', '2em')

        
        filter_div = DivWdg() 
        span = SpanWdg(project_filter, css='med')
        filter_div.add(span)
        
        filter_div.set_style('float: left;margin-left: 1em')
        filter_div.add(HtmlElement.b("Current Pipeline: "))
        filter_div.add(select)



 
        title.add(filter_div)
        # The refresh button is necessary for getting the right config for 
        # search type
        
        
        my.pipeline = select.get_value()
        if my.pipeline and not \
            WebContainer.get_web().get_form_value(PipelineEditCmd.REMOVE_PIPELINE):
                
            remove_button = IconSubmitWdg(PipelineEditCmd.REMOVE_PIPELINE, \
                IconWdg.DELETE, long=True)
            remove_button.add_event('onclick', "if (!remove_pipe('%s')) \
                    return false;" % (my.pipeline))
            remove_button.set_text("Remove %s" % my.pipeline)
            remove_button.add_style('color: #c97061')
            remove_span = DivWdg(remove_button)
            remove_span.set_style('float: right; margin: 4px 6px 0 0')
            
            title.add(remove_span)
            update_wdg = UpdateWdg()
            update_wdg.set_name("update")
            update_wdg.set_iframe_width(100)
            pipeline = Pipeline.get_by_code(my.pipeline, allow_default=True)
            if pipeline:
                update_wdg.set_sobject(pipeline)
            
            title.add(update_wdg)
        
        return title



    def _get_current_view_wdg(my):

        div = DivWdg()

        # set the current view
        current_view = view_current.get_value()
        if current_view == "":
            current_view = "default"

        my.current_config = None
        for config in my.configs:
            if config.get_value("view") == current_view:
                my.current_config = config
        if my.current_config == None:
            my.current_config = my.configs[0]

        return div



    def _get_list_attr_wdg(my, pipe):

        pipe_name = pipe.get_code()
        attr_div = DivWdg(HiddenWdg("%s_Elts" % pipe_name))
        
        # display all of the templates
        title_div = DivWdg(css='cell_header')
        title_div.set_style("width: 100em; margin: 2em 1em 2em 2em")
        attr_div.add(title_div)
        title_div.add(DivWdg("&nbsp;", css='sm_cell'))
        title_div.add(DivWdg("Process", css='med_cell'))

        button = IconSubmitWdg(my.AUTO_CONNECT, icon=IconWdg.CONNECT, long=True)
        script = ["if (!confirm('This will reset any advanced connections for this pipeline. Proceed?')) return false"]
        script.append("get_elements('%s').set_value('%s')"%(my.REORDER, pipe_name))
        button.add_event('onclick', ';'.join(script) )
        flink_div = DivWdg( css='lg_cell')
        flink_div.add(button)

        # add hint
        hint = HintWdg('You can drag and drop the processes below and click on [Forward Connect] to establish the basic connections.<br/>'\
                'Further connection settings can be set in the section [Connections] at the bottom.')
        flink_div.add(hint)
        auto_fill = CheckboxWdg('auto_link')
        auto_fill.set_checked()
        auto_fill_span = SpanWdg(auto_fill, css='med')
        auto_fill_span.add("auto link")
        flink_div.add(auto_fill_span)
        title_div.add(flink_div)
        title_div.add(DivWdg("Completion", css ='med_cell'))

        title_div.add(DivWdg("Task Pipeline", css ='med_cell'))
        title_div.add(DivWdg("Group", css ='med_cell'))

        reorder = IconSubmitWdg(my.UPDATE, IconWdg.REFRESH, long=True) 
        reorder.add_event('onmousedown', \
            "get_elements('%s').set_value('%s')"%(my.REORDER, pipe_name))
        title_div.add(DivWdg(reorder, css='sm_cell'))
        #title_div.add(DivWdg("&nbsp;", css='sm_cell'))
        attr_div.add(HtmlElement.br())
        process_names = []
        if pipe:
            process_names = pipe.get_process_names()
        row_ids = []
        for process_name in process_names:
            
            row_div = DivWdg()
            row_div.set_style("position: absolute; margin-left: 2em")
            attr_div.add(row_div)
            attr_div.add(HtmlElement.br(2))
            #process_name = process_name.replace(" ", "_")
            row_id = '%s_%s' %(pipe_name, process_name)
            row_ids.append(row_id)  
            row_div.set_id(row_id) 
            row_div.set_attr('view', pipe_name)
            row_div.add_style('width','75em')
 
          
            sub_div = DivWdg("&nbsp;", css='sm_cell')
            row_div.add(sub_div)


            # add the attribute name
            row_div.add(DivWdg(process_name, css='med_cell'))

            # add the connections
            f_link = '&nbsp;'
            f_connects = pipe.get_forward_connects(process_name)
            if f_connects:
                f_link = ', '.join(f_connects) 
            text = TextWdg('%s_%s_flink' %(pipe_name, process_name))
            text.set_attr('size','40')
            text.set_value(f_link)
            text.set_attr('readonly','readonly')
            text.add_class('disabled')
            row_div.add(DivWdg(text, css='lg_cell'))

            # add the completion (optional)
            completion = pipe.get_process(process_name).get_completion()
            sel = SelectWdg('%s_%s_completion' %(pipe_name, process_name))
            sel_values = []
            for x in xrange(11):
                sel_values.append(x * 10)
            sel.add_empty_option(sel.SELECT_LABEL, '')
            sel.set_option('values', sel_values)
            sel.set_option('labels', ['%s%%'%val for val in sel_values])
            sel.set_value(completion)
            
            row_div.add(DivWdg(sel, css='med_cell'))

            

            # add the task pipeline dropdown (optional)
            task_pipes = Pipeline.get_by_search_type('sthpw/task')
            task_pipe = pipe.get_process(process_name).get_task_pipeline(default=False)
            task_pipe_codes = SObject.get_values(task_pipes, 'code')
            task_sel = SelectWdg('%s_%s_taskpipe' %(pipe_name, process_name))
            task_sel.set_option('values', task_pipe_codes)
            task_sel.add_empty_option('-- default --', '')
            task_sel.set_value(task_pipe)
            row_div.add(DivWdg(task_sel, css='med_cell'))
            
            # add the group info
            group_info = ''
            pipe_group_info = pipe.get_group(process_name)
            if pipe_group_info:
                group_info = pipe_group_info
            
            text = TextWdg('%s_%s_group' %(pipe_name, process_name))
            text.set_attr('size','20')
            text.set_value(group_info)
            row_div.add(DivWdg(text, css='med_cell'))
            
            # add the remove button
            remove_button = IconSubmitWdg("Remove_%s_%s" % (pipe_name, process_name), \
                IconWdg.DELETE, False)
            remove_button.add_event('onclick', "if (!remove_attr('%s')) return false;\
                document.form.%s.value='%s'" \
                %(process_name, PipelineEditCmd.REMOVE_ATTR, process_name))
            # can't do this now
            #process_name,eremove_button.set_attr("onsubmit","javascript:return remove_attr()")
            remove_div = DivWdg(remove_button, css='med_cell')
            remove_div.add_style('margin-left','1em')
            row_div.add(remove_div)

       
        

        if row_ids:
            my.row_ids.extend(row_ids)
        
            order_script = HtmlElement.script("var %s_Elts = [%s] "\
                % (pipe_name, ', '.join(["dd.elements['%s']" %id for id in row_ids])))
            my.script_div.add(order_script)
        return attr_div

    def _get_connect_div(my, pipe):

        main_div = DivWdg()
        main_div.add_style('display', 'block')

        div = DivWdg(id='connect_content')
        

        swap = SwapDisplayWdg.get_triangle_wdg()
        top_title_div = DivWdg(swap, css='cell_header', id='pipe_connections')
        top_title_div.set_style("width: 100em; margin-left: 2em")
        top_title_div.add('Connections (advanced)')

        
        title_div = DivWdg()
        
        main_div.add(top_title_div)
       
        main_div.add(div)
        main_div.add(HtmlElement.br(2))

        SwapDisplayWdg.create_swap_title(top_title_div, swap, div)

        div.add(HtmlElement.br(2))
        title_div.set_style("width: 80em; margin-left: 2em")
        title_div.add(DivWdg('&nbsp;', css='sm_cell'))
        title_div.add(DivWdg('<b>From</b>', css='med_cell'))
        title_div.add(DivWdg('<b>To</b>', css='med_cell'))
        title_div.add(DivWdg('<b>Context</b>', css='med_cell'))

        hint = HintWdg('You can insert a new connection here. <br/>For existing connections, only 1 connection can be updated at a time.') 
        title_div.add(DivWdg(hint, css='sm_cell'))

        div.add(title_div)
        div.add(HtmlElement.br(2))

        create_title = DivWdg(HtmlElement.b('Create a New Connection:'))
        create_title.add_style('margin-left', '4em')
        div.add(create_title) 

        div.add(HtmlElement.br())
        div.add(HiddenWdg(my.EDIT_ACTION, ''))
        div.add(HiddenWdg(my.EDITED_CONTEXT, ''))
        div.add(HiddenWdg(my.CUR_CONTEXT, ''))
        div.add(HiddenWdg(my.TO_PROCESS, ''))
        div.add(HiddenWdg(my.FROM_PROCESS, ''))

        # add the Insert connect row
        text = TextWdg(my.NEW_FROM_PROCESS)
        text.add_class('insert')
        #text.add_style('background-color', '#E2EBD8')
        row_div = DivWdg(DivWdg(text, css='med_cell'))
        row_div.add_style("margin-left: 6em")
        div.add(row_div)

        text = TextWdg(my.NEW_TO_PROCESS)
        #text.add_style('background-color', '#E2EBD8')
        row_div.add(DivWdg(text, css='med_cell'))

        text = TextWdg(my.NEW_CONTEXT)
        #text.add_style('background-color', '#E2EBD8')
        row_div.add(DivWdg(text, css='med_cell'))

        
        icon = ProdIconButtonWdg('Insert')
        icon.add_style('padding: 3px 13px 3px 13px')
        icon.add_class('insert')
        icon_div = DivWdg(icon, css='med_cell')

        connect_wdg = PipelineConnectionWdg()
        connect_wdg.init_pipeline(pipe)

        add_cmd = my._get_insert_cmd()
        progress = add_cmd.generate_div()
        progress.add_style('float','right')
        progress.add_style('margin','-12px 0 0 40px')

        icon_div.add(progress)

        post_script = [connect_wdg.get_refresh_script(show_progress=False)
                ]
        # add SiteMenu refresh

        event_container = WebContainer.get_event_container()
        caller = event_container.get_event_caller(SiteMenuWdg.EVENT_ID)
        post_script.append(caller)

        progress.set_post_ajax_script(';'.join(post_script))
        script = add_cmd.get_on_script()
        icon.add_event('onclick', script)

        row_div.add(icon_div)
        row_div.add(HtmlElement.br(2))


        
            
        edit_title = DivWdg(HtmlElement.b('Edit Connections:'))
        edit_title.add_style('margin-left', '4em')
        div.add(edit_title)
        div.add(HtmlElement.br())
        div.add(connect_wdg)

        return main_div
        

    def _get_insert_cmd(my):
        cmd = AjaxCmd()
        cmd.register_cmd('pyasm.admin.creator.PipelineConnectInsertCmd')
        cmd.add_element_name(my.CURRENT_PIPELINE)
        cmd.add_element_name(my.NEW_CONTEXT)
        cmd.add_element_name(my.NEW_FROM_PROCESS)
        cmd.add_element_name(my.NEW_TO_PROCESS)
        return cmd

    def _get_create_pipe_wdg(my):
        control_div = DivWdg()
        
        control_div.set_style('height: 4em; margin-left: 2em')
           
        view_input = TextWdg("pipe_name")
        desc_input = TextWdg("pipe_desc")
        desc_input.set_attr('size', '24') 
        view_submit = IconSubmitWdg(PipelineEditCmd.CREATE_PIPELINE, icon=IconWdg.CREATE, long=True)
        pipe_search_type = SelectWdg("pipe_search_type")    
        search = Search( SearchType.SEARCH_TYPE )
        filter = search.get_regex_filter("search_type", "^sthpw/.*", "NEQ")
        filter = "%s or search_type ='sthpw/task'" %filter
        search.add_where(filter)
        search.add_order_by("search_type")

        pipe_search_type.set_search_for_options(search, "search_type", "get_label()")
        pipe_search_type.add_empty_option(label='-- Select Search Type --')
        
        name_span = SpanWdg("Name: ", css='small')
        name_span.add_style('padding-left: 12px')
        name_span.add(view_input)
        
        search_type_span = SpanWdg('Search Type: ', css='small')
        search_type_span.add(pipe_search_type)
        hint = HintWdg('Search Type represents a basic entity (SObject) defined in Tactic. '\
                'e.g. a 3D Asset') 
        search_type_span.add(hint)
        desc_span = SpanWdg('Desc: ', css='small')
        desc_span.add(desc_input)
        
        add_div = SpanWdg(HtmlElement.b('1. Create a new pipeline'))
        add_div.add(HtmlElement.br())

        add_div.add(name_span)
        add_div.add(search_type_span)
        add_div.add(desc_span)
        add_div.add(view_submit)
        
        control_div.add(add_div)
        
        return control_div

    def _get_create_attr_wdg(my):

        attr_div = DivWdg()
        title = DivWdg(HtmlElement.b('2. Add process to currently selected pipeline'))
        title.set_style('float: clear; margin-left: 2em; height: 1em') 
        attr_div.add(title)
        attr_div.add(HtmlElement.br())
        # custom attributes
        name_input = TextWdg("attr_name")
        
        submit_input = IconSubmitWdg(PipelineEditCmd.ADD_ATTR, icon=IconWdg.ADD, long=True)
        process_span = SpanWdg("Process: ", css='small') 
        process_span.add_style('padding-left: 34px')
        attr_div.add(process_span)
        attr_div.add(name_input)
        
        attr_div.add(SpanWdg(submit_input, css='small'))
        attr_div.add(HiddenWdg(PipelineEditCmd.REMOVE_ATTR))
       

        return attr_div

class PipelineConnectionWdg(AjaxWdg):

    ID = 'PipelineConnection'
    def __init__(my,name=None, value=None ):
        my.pipe = None
        my.hidden = None
        super(PipelineConnectionWdg, my).__init__()

    def init_pipeline(my, pipe):
        my.pipe = pipe
        my.set_ajax_top_id(my.ID)
        my.init_setup()

    def init_cgi(my):
        # get the pipe
        pipe_name = my.web.get_form_value(PipelineEditorWdg.CURRENT_PIPELINE)
        my.pipe = Pipeline.get_by_name(pipe_name)

    def init_setup(my):
        my.hidden = HiddenWdg(PipelineEditorWdg.CURRENT_PIPELINE, my.pipe.get_name())
        my.add_ajax_input(my.hidden)

    def get_display(my):
        
        my.set_ajax_top_id(my.ID)

        widget = DivWdg(id=my.ID)
        widget.add_style('display: block')
        
        if my.is_from_ajax():
            widget = Widget()
            my.init_setup()
        #widget.add(my.hidden)
        
        connects = my.pipe._get_connects()
        for connect in connects:
            row_div = DivWdg()
            row_div.set_style("margin-left: 6em")
           
            from_process = connect.get_from()
            from_div = DivWdg(from_process, css='med_cell')
            row_div.add(from_div)
            
            to_process = connect.get_to()
            to_div = DivWdg(to_process, css='med_cell')
            row_div.add(to_div)

            # add the context (optional)
            context_name = '%s_context_%s' %(my.pipe.get_name(), Widget.generate_unique_id())
            text = TextWdg(context_name)
            context = connect.get_context(from_xml=True)
            text.set_value(context)
            row_div.add(DivWdg(text, css='med_cell'))

            # add the update context butondiv.add(HtmlElement.br(2)) 
            icon = ProdIconButtonWdg('update')

            script = ["get_elements('%s').set_value('update')" %(PipelineEditorWdg.EDIT_ACTION)]
            script.append("get_elements('%s').set_value('%s')" %(PipelineEditorWdg.CUR_CONTEXT, context))
            script.append("get_elements('%s').set_value('%s')" %(PipelineEditorWdg.FROM_PROCESS, from_process))
            script.append("get_elements('%s').set_value('%s')" %(PipelineEditorWdg.TO_PROCESS, to_process))
            script.append("var new_val=get_elements('%s').get_value(); get_elements('%s').set_value(new_val)" \
                %(context_name, PipelineEditorWdg.EDITED_CONTEXT))

            cmd = my._get_edit_cmd()
            progress = cmd.generate_div()
            progress.add_style('float','right')
            progress.add_style('margin','-12px 0 0 40px')
            icon_div= FloatDivWdg(icon, width=80)
            icon_div.add( progress)
            script.append(cmd.get_on_script())
            icon.add_event('onclick', ';'.join(script))


            # set post_ajax script
            event_container = WebContainer.get_event_container()
            post_script = [event_container.get_event_caller(SiteMenuWdg.EVENT_ID)]
            post_script.append(my.get_refresh_script(show_progress=False))
            
            progress.set_post_ajax_script(';'.join(post_script))

            row_div.add(DivWdg(icon_div, css='med_cell'))


            # add delete icon
            script = ["get_elements('%s').set_value('delete')" %(PipelineEditorWdg.EDIT_ACTION)]
            script.append("get_elements('%s').set_value('%s')" %(PipelineEditorWdg.CUR_CONTEXT, context))
            script.append("get_elements('%s').set_value('%s')" %(PipelineEditorWdg.FROM_PROCESS, from_process))
            script.append("get_elements('%s').set_value('%s')" %(PipelineEditorWdg.TO_PROCESS, to_process))
            del_icon = IconButtonWdg('Remove connection', icon=IconWdg.DELETE)

            cmd = my._get_edit_cmd()
            progress = cmd.generate_div()
            script.append(cmd.get_on_script(show_progress=False))
            
            # set post_ajax script
            progress.set_post_ajax_script(';'.join(post_script))

            del_icon.add_event('onclick', ';'.join(script))
            del_div = DivWdg(del_icon, css='sm_cell')
            del_div.add(progress)
            row_div.add(del_div)

            row_div.add(HtmlElement.br(2))
            widget.add(row_div)

        return widget
 
    def _get_edit_cmd(my):

        cmd = AjaxCmd()
        cmd.register_cmd('pyasm.admin.creator.PipelineConnectEditCmd')
        cmd.add_element_name(PipelineEditorWdg.CURRENT_PIPELINE)
        cmd.add_element_name(PipelineEditorWdg.EDIT_ACTION)
        cmd.add_element_name(PipelineEditorWdg.EDITED_CONTEXT)
        cmd.add_element_name(PipelineEditorWdg.CUR_CONTEXT)
        cmd.add_element_name(PipelineEditorWdg.FROM_PROCESS)
        cmd.add_element_name(PipelineEditorWdg.TO_PROCESS)

        return cmd

class PipelineConnectInsertCmd(Command):

    def get_title(my):
        return "Add New Connection"

    def check(my):
        web = WebContainer.get_web()

        my.pipeline = web.get_form_value(PipelineEditorWdg.CURRENT_PIPELINE)
        if not my.pipeline and not web.get_form_value(my.CREATE_PIPELINE):
            raise CommandExitException("No pipeline has been selected.")

        my.new_context = web.get_form_value(PipelineEditorWdg.NEW_CONTEXT)
        my.new_to_process = web.get_form_value(PipelineEditorWdg.NEW_TO_PROCESS)
        my.new_from_process =web.get_form_value(PipelineEditorWdg.NEW_FROM_PROCESS)

        # should start with a word character
        pat = re.compile(r'^\w+')
        check_context = True
        if my.new_context: 
            check_context = pat.match(my.new_context)
        if not check_context or not pat.match(my.new_to_process)\
            or not pat.match(my.new_from_process):
                raise UserException('The value should start with a alpha-numeric character')
                return False
        return True

    def execute(my):
        
        my.add_connect(my.new_from_process, my.new_to_process, my.new_context)


    def add_connect(my, new_from_process, new_to_process, new_context):
        ''' add a new connect '''
        pipe = Pipeline.get_by_name(my.pipeline)
        
        xml = pipe.get_xml_value("pipeline")

        root = xml.get_root_node()

        element = xml.create_element("connect")
        Xml.set_attribute(element, "from", new_from_process)
        Xml.set_attribute(element, "to", new_to_process)
        # context can be empty
        if new_context:
            Xml.set_attribute(element, "context", new_context)

        # make sure the connections with the same from process stick together
        ref_child = xml.get_node("pipeline/connect[@from='%s']" % (new_from_process)) 
        if ref_child:
            Xml.insert_after(root, element, ref_child)
        else:
            root.appendChild(element)
        # commit the changes
        pipe.set_value("pipeline", xml.get_xml())
        pipe.set_value("code", my.pipeline)
        pipe.set_value('timestamp', Sql.get_timestamp_now(), quoted=False )
        pipe.commit()
        my.add_description('from [%s] to [%s] context [%s]' \
            %(new_from_process, new_to_process, new_context))

class PipelineConnectEditCmd(Command):

    
    def get_title(my):
        return "Alter Connection Attributes"

    def check(my):
        web = WebContainer.get_web()

        my.pipeline = web.get_form_value(PipelineEditorWdg.CURRENT_PIPELINE)
        if not my.pipeline and not web.get_form_value(my.CREATE_PIPELINE):
            raise CommandExitException("No pipeline has been selected.")

        my.new_context = web.get_form_value(PipelineEditorWdg.EDITED_CONTEXT)
        my.cur_context = web.get_form_value(PipelineEditorWdg.CUR_CONTEXT)
        my.from_process = web.get_form_value(PipelineEditorWdg.FROM_PROCESS)
        my.to_process = web.get_form_value(PipelineEditorWdg.TO_PROCESS)
        my.action = web.get_form_value( PipelineEditorWdg.EDIT_ACTION )

        if my.action == 'delete':
            return True


        if not my.new_context and not my.cur_context:
            raise UserException('There is nothing to update')
        
        if my.new_context == my.cur_context:
            raise UserException('The context has not changed since last update.')

        # should start with a word character
        pat = re.compile(r'^\w+')
        if my.new_context and not pat.match(my.new_context):
            raise UserException('Please enter a valid context before clicking [update]. [%s] is not valid'\
                %my.new_context)
        pat = re.compile(r'\W+')
        if my.new_context and pat.search(my.new_context):
            raise UserException("Invalid characters found in [%s]" %my.new_context)
        return True

    def execute(my):
       
        if my.action == 'delete':
            my.del_connect(my.from_process, my.to_process, my.cur_context)
        else:
            my.set_attr('context', my.from_process, my.to_process, my.cur_context, my.new_context)

    def del_connect(my, from_process, to_process, cur_context):
        pipe = Pipeline.get_by_name(my.pipeline)
        xml = pipe.get_xml_value("pipeline") 

        node = my._get_node(xml, from_process, to_process, cur_context)
        node.parentNode.removeChild(node)

        pipe.set_value('pipeline', xml.get_xml())
        pipe.set_value('timestamp',Sql.get_timestamp_now(), quoted=False)
        pipe.commit()
        my.add_description("Remove connection from [%s] to [%s]" %(from_process, to_process))

    def set_attr(my, attr_name, from_process, to_process, cur_context, new_context):

        pipe = Pipeline.get_by_name(my.pipeline)
        xml = pipe.get_xml_value("pipeline") 
        node = my._get_node(xml, from_process, to_process, cur_context)
        if not new_context:
            Xml.del_attribute(node, attr_name)
        else:
            Xml.set_attribute(node, attr_name, new_context)
        pipe.set_value('pipeline', xml.get_xml())
        pipe.set_value('timestamp',Sql.get_timestamp_now(), quoted=False)
        pipe.commit()
        my.add_description("Modify connection from [%s] to [%s]" %(from_process, to_process))
    
    def _get_node(my, xml, from_process, to_process, cur_context):
        
        # find the node that has these attr_names
        
        node = xml.get_node("pipeline/connect[@from='%s' and @to='%s' and @context='%s']" \
                    % (from_process, to_process, cur_context))
        if not node:
             node = xml.get_node("pipeline/connect[@from='%s' and @to='%s']" \
                    % (from_process, to_process))
        
        # if it doesn't exist, then add it
        if node == None:
            raise CommandExitException("Node not found with from_process[%s] and to_process[%s]" \
                %(from_process, to_process))

        return node

class PipelineEditCmd(Command):
    ADD_ATTR = "Add_Process"
    REMOVE_ATTR = "Remove_Element"
    CREATE_PIPELINE = "Create_Pipeline"
    REMOVE_PIPELINE = "Remove_Pipeline"
    CURRENT_PIPELINE = "Current_Pipeline"
    
    def get_title(my):
        return "Alter Attribute"

    def check(my):
        return True

    def execute(my):
        web = WebContainer.get_web()

        my.pipeline = web.get_form_value(my.CURRENT_PIPELINE)
        if not my.pipeline and not web.get_form_value(my.CREATE_PIPELINE):
            raise CommandExitException("No pipeline has been selected.")

        # depending on what was submitted, perform the appropriate action
        if web.get_form_value(my.ADD_ATTR) != "":
            attr_name = web.get_form_value("attr_name").strip()
            my._add_node(attr_name)


        elif web.get_form_value(my.REMOVE_ATTR) != "":
            my._remove_attr()


        elif web.get_form_value(my.CREATE_PIPELINE) != "":
            pipe_name = web.get_form_value("pipe_name")

            pipe_desc = web.get_form_value("pipe_desc")
            pipe_search_type = web.get_form_value("pipe_search_type")
            
            pat = re.compile(r".*(!|\+|-|_|\*|/)+.*")
            m = pat.search(pipe_name)
            if m:
                raise UserException("[%s] is not allowed in the name of a pipeline." %m.group(1))

            if not pipe_search_type:
                raise UserException("Please select a search type this pipeline is \
                associated with. e.g. If it is made for a 3d asset, select 'prod/asset'")
            
            if pipe_name:
                my._add_pipeline(pipe_name,  pipe_desc, pipe_search_type)
        elif web.get_form_value(my.REMOVE_PIPELINE) != "":
            my._remove_pipe()

    
        # reorder and update
        elif web.get_form_value(PipelineEditorWdg.UPDATE):
            my._switch_elems()
            my._update_elems()

        # basic connection
        elif web.get_form_value(PipelineEditorWdg.AUTO_CONNECT):
            my._switch_elems()
            my._auto_connect()    



    def _add_pipeline(my, pipe_name, pipe_desc, pipe_search_type):
        ''' add a pipeline '''
        Pipeline.create( pipe_name, pipe_desc, pipe_search_type)
        my.add_description('Created pipeline [%s]' %pipe_name)
        WebContainer.get_web().set_form_value(PipelineEditorWdg.CURRENT_PIPELINE, pipe_name)
        WebContainer.get_web().set_form_value('project_filter', '')
        return



   



    def _add_node(my, attr_name):

        if attr_name == "":
            raise CommandExitException("process_name is empty")

        pipe = Pipeline.get_by_name(my.pipeline)
        if not pipe:
            raise CommandException("No valid pipeline to add process to")

        xml = pipe.get_xml_value("pipeline")

        # find the node that has this attr_name
        node = xml.get_node("pipeline/process[@name='%s']" % attr_name)
        # if it doesn't exist, then add it
        if node != None:
            raise CommandExitException("Process [%s] already exists" % attr_name)

        # create a new element for the table
        table = xml.get_root_node()

        element = xml.create_element("process")
        Xml.set_attribute(element,"name", attr_name)

        table.appendChild(element)

        # commit the changes
        pipe.set_value("pipeline", xml.get_xml())
        pipe.set_value("code", my.pipeline)
        pipe.set_value('timestamp', Sql.get_timestamp_now(), quoted=False)
        pipe.commit()
        my.add_description("Added process [%s] for %s" %(attr_name, my.pipeline))




    def _remove_pipe(my):
        ''' remove the current pipeline '''
        web = WebContainer.get_web()
        pipe_name = web.get_form_value(my.CURRENT_PIPELINE)
        if pipe_name:
            pipe = Pipeline.get_by_name(pipe_name)
            if pipe:
                pipe.delete()
                Pipeline.clear_cache()
                my.add_description("Removed pipeline '%s'." % (pipe_name) )
          

    def _remove_attr(my):

        web = WebContainer.get_web()

        attr_name = web.get_form_value(my.REMOVE_ATTR)
        if not attr_name:
            raise CommandExitException("No attrs selected to remove")

        pipe = Pipeline.get_by_name(my.pipeline)
        xml = pipe.get_xml_value("pipeline")
        
        # find the node that has this attr_name
        node = xml.get_node("pipeline/process[@name='%s']" % attr_name)
        if node != None:
            # remove element
            table = xml.get_root_node()
            table.removeChild(node)

        pipe.set_value("pipeline", xml.get_xml() )
        pipe.set_value('timestamp', Sql.get_timestamp_now(), quoted=False)
        pipe.commit()


    def _auto_connect(my):
        ''' do basic connection, it will remove other attributes like context if it exists'''
        web = WebContainer.get_web()
        pipe_name = web.get_form_value(PipelineEditorWdg.REORDER)
        Pipeline.clear_cache()

        pipe = Pipeline.get_by_name(pipe_name)
       
        
        keys = web.get_form_keys()
        flink_map = {}
        flink_pat = '(%s_)(.*)(_flink$)'% pipe_name
        flink_p = re.compile(flink_pat)
        xml = pipe.get_xml_value("pipeline")

        for key in keys:
            flink_m = flink_p.match(key)
            value = web.get_form_value(key).strip()
            if flink_m:
                values = [value]
                from_proc = flink_m.group(2)
                if ',' in value:
                    values = value.split(',')
                for val in values:  
                    process_list = flink_map.get(from_proc)
                    if not process_list:
                        process_list = []
                        flink_map[from_proc] = process_list
                    process_list.append((from_proc, val.strip()))

        my.__process_nodes(xml, pipe, flink_map)

    def _update_elems(my):
        ''' look for params named "<pipeline>_<process_name>_flink " 
            and "<pipeline>_<process_name>_completion '''
        web = WebContainer.get_web()
        pipe_name = web.get_form_value(PipelineEditorWdg.REORDER)
        keys = web.get_form_keys()
        attr_name = ""

        pipe = Pipeline.get_by_name(pipe_name)
        keys = web.get_form_keys()
        

        completion_pat = '(%s_)(.*)(_completion$)'% pipe_name
        completion_p = re.compile(completion_pat)


        taskpipe_pat = '(%s_)(.*)(_taskpipe$)'% pipe_name
        taskpipe_p = re.compile(taskpipe_pat)

        group_pat = '(%s_)(.*)(_group$)'% pipe_name
        group_p = re.compile(group_pat)
        
        xml = pipe.get_xml_value("pipeline")

        for key in keys:
            # add the completion info
            completion_m = completion_p.match(key)
            completion_val = web.get_form_value(key)
            my.__update_node_attr(completion_m, xml, 'completion', completion_val)
       
            # add the task pipe info
            taskpipe_m = taskpipe_p.match(key)
            taskpipe_val = web.get_form_value(key)
            my.__update_node_attr(taskpipe_m, xml, 'task_pipeline', taskpipe_val)

            # add the group info
            group_m = group_p.match(key)
            group_val = web.get_form_value(key)
            my.__update_node_attr(group_m, xml, 'group', group_val)
        
        pipe.set_value('pipeline', xml.get_xml())
        pipe.set_value('timestamp',Sql.get_timestamp_now(), quoted=False)
        pipe.commit()
        
        my.add_description("Update elements in '%s'" % (pipe_name) )

    def __update_node_attr(my, match, xml, attr_name, attr_val):
        if match:
            # get the node that has this process_name
            node = xml.get_node("pipeline/process[@name='%s']|pipeline/pipeline[@name='%s']" \
                % (match.group(2), match.group(2)))
            attr_val = attr_val.strip()
            if attr_val:
                Xml.set_attribute(node, attr_name, attr_val)
            else:
                Xml.del_attribute(node, attr_name)



                    
    def __process_nodes(my, xml, pipe, value_map):
        '''updates the connection info a group of nodes'''
        nodes = xml.get_nodes("pipeline/connect")
        root_node = xml.get_root_node()
        processes = pipe.get_process_names() 

        # clear the connections first
        for node in nodes:
            root_node.removeChild(node)
        
        # process from other pipeline is allowed 
        ''' 
        for key, value in value_map:
            if value and value not in processes:
                raise UserException('Invalid process [%s] entered!' %value)
        '''
        # this assumes all the from processes originates from this pipeline
        for process in processes:
            connection_list = value_map.get(process)
            for from_proc, to_proc in connection_list:
                if to_proc:
                    # add connection
                    connect_node = xml.create_element('connect')
                    Xml.set_attribute(connect_node, 'from', from_proc)
                    Xml.set_attribute(connect_node, 'to', to_proc)
                    root_node.appendChild(connect_node)
       
        pipe.set_value("pipeline", xml.get_xml() )
        pipe.set_value("timestamp", Sql.get_timestamp_now(), quoted=False)
        pipe.commit()

        my.add_description("Auto Connection for '%s'." % pipe.get_name ) 
            
    def _switch_elems(my):
        ''' look for params named "<pipeline>_Elts" '''
        web = WebContainer.get_web()

        keys = web.get_form_keys()
        attr_name = ""
        pipeline = web.get_form_value(PipelineEditorWdg.REORDER)

        for key in keys:
            if key == ("%s_Elts" % pipeline) and web.get_form_value(key).strip():
                attr_name = web.get_form_value(key)
                
        
        pat = '(%s_)(.*)'% pipeline
        p = re.compile(pat)
                  
        elem_ids = attr_name.split(",")
        attr_names = []
        for elem_id in elem_ids:
            m = p.match(elem_id)
            if not m:
                return CommandExitException("matching failed")
            attr_names.append(elem_id.replace(m.group(1), ""))

        if not attr_names:
            return CommandExitException("No attrs selected to reorder")

        pipe = Pipeline.get_by_name(pipeline)
        if not pipe:
            return
        xml = pipe.get_xml_value("pipeline")


        # reorder the nodes
        nodes = xml.get_nodes("pipeline/process")
        attr_names.reverse()
        
        for attr_name in attr_names:
            for node in nodes:
                if Xml.get_attribute(node, "name") == attr_name:
                    parent = node.parentNode
                    node.parentNode.insertBefore(node, parent.firstChild)
                    break

        pipe.set_value("pipeline", xml.get_xml() )
        pipe.set_value("timestamp", Sql.get_timestamp_now(), quoted=False)
        pipe.commit()

        my.add_description("Order switch for processes in '%s'." % (pipeline) )
          











