###########################################################
#
# Copyright (c) 2009, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#


__all__ = ['ProcessInputWdg', 'SubContextInputWdg', 'SubContextAction']

from pyasm.search import Search, SearchKey
from pyasm.biz import Pipeline
from pyasm.web import WebContainer, Widget, DivWdg
from pyasm.widget import BaseInputWdg, SelectWdg, TextWdg, IconButtonWdg, IconWdg
from pyasm.command import DatabaseAction
from tactic.ui.panel import EditWdg
from pyasm.common import UserException, TacticException


class ProcessInputWdg(BaseInputWdg):
    '''This widget display a drop down for processes.  It is
    primarily used as the input widget for adding a process
    onto a task base on the parent's pipeline. With the context option set to true,
    it acts as a context display instead'''



    def get_display(my):
        show_context = my.get_option('context') == 'true'

        top = DivWdg()
        # put in a js callback to determine the to use.
        top.add_class("spt_input_top")


        context_list = []

        my.pipeline_codes = []
        my.pipelines = []
        my.in_edit_wdg = False

        parent_key = my.get_option("parent_key")
        if not parent_key:
            state = my.get_state()
            parent_key = state.get("parent_key")


        if parent_key:
            parent = Search.get_by_search_key(parent_key)
            pipeline_code = parent.get_value("pipeline_code", no_exception=True)
            if pipeline_code:
                top.add_attr("spt_cbjs_get_input_key", "return '%s'" % pipeline_code)

        else:
            # This is quite slow, but it works
            #top.add_attr("spt_cbjs_get_input_key", "var server=TacticServerStub.get(); var parent_key = cell_to_edit.getParent('.spt_table_tbody').getAttribute('spt_parent_key'); var parent = server.get_by_search_key(parent_key); return parent.pipeline_code")

            # ProcessElementWdg's handle_td() sets the spt_pipeline_code attribute
            top.add_attr("spt_cbjs_get_input_key", "return cell_to_edit.getAttribute('spt_pipeline_code')")



        # This is only executed for the popup edit widget
        if hasattr(my, 'parent_wdg') and isinstance(my.get_parent_wdg(), EditWdg):
            my.in_edit_wdg = True
            sobject = my.get_current_sobject()
            parent = sobject.get_parent()
            if not parent:
                parent_key = my.get_option('parent_key')
                if parent_key:
                    parent = SearchKey.get_by_search_key(parent_key)

            if parent:
                if not parent.has_value('pipeline_code'):

                    name = my.get_input_name()
                    text = TextWdg(name)
                    top.add(text)

                    sobject = my.get_current_sobject()
                    name = my.get_name()
                    value = sobject.get_value(name)
                    text.set_value(value)

                    return top
                    #raise TacticException('[%s] needs a pipeline_code attribute to insert task.'%parent.get_code())
                
                pipe_code = parent.get_value('pipeline_code')
                if pipe_code:
                    my.pipeline_codes  = [pipe_code]
                    my.pipelines = [Pipeline.get_by_code(pipe_code)]
        else:

            # just get all of the pipelines
            # Cannot use expression here, because entries are added to the
            # result ... this causes further queries to return with the
            # added entries
            #my.pipelines = Search.eval("@SOBJECT(sthpw/pipeline)")
            search = Search("sthpw/pipeline")
            my.pipelines = search.get_sobjects()

            my.pipeline_codes = [x.get_code() for x in my.pipelines]

            # add the default
            my.pipeline_codes.append("")
            my.pipelines.append(None)


        for i, pipeline_code in enumerate(my.pipeline_codes):
            pipeline = my.pipelines[i]
            div = DivWdg()
            top.add(div)
            div.add_class("spt_input_option")
            div.add_attr("spt_input_key", pipeline_code)

            name = my.get_input_name()

            # If the pipeline code is empty, make it free form (for now)
            if not pipeline_code:
                text = TextWdg(name)
                div.add(text)
                continue


            
            select = SelectWdg(name)
            select.add_empty_option("-- Select a %s --" % my.get_name() )

            # TODO: make spt.dg_table.select_wdg_clicked keyboard action free so it won't interfere with
            # normal usage of the select
            if not my.in_edit_wdg:
                select.add_behavior( { 'type': 'click',
                   'cbjs_action': 'spt.dg_table.select_wdg_clicked( evt, bvr.src_el );'
                } )
            

            # get the sub-pipeline processes as well
            processes = pipeline.get_processes(recurse=True)
            values = []
            labels = []
            for process in processes:
                is_sub_pipeline = False
                if process.is_from_sub_pipeline():
                    process_name  = process.get_full_name()
                    is_sub_pipeline = True
                else:
                    process_name  = process.get_name()

                # show context instead
                if show_context:
                    output_contexts = pipeline.get_output_contexts(process.get_name())
                    for context in output_contexts:
                        values.append(context)
                        if is_sub_pipeline:
                            #label = process_name
                            label = context
                        else:
                            label = context
                        labels.append(label)
                else:
                    values.append(process_name)
                    labels.append(process_name)

            select.set_option("values", values) 
            select.set_option("labels", labels) 
            
            div.add(select)

            # there is only 1 select for EditWdg
            if hasattr(my, 'parent_wdg') and isinstance(my.get_parent_wdg(), EditWdg):
                sobject = my.get_current_sobject()
                # this could be either process or context
                name = my.get_name()
                value = sobject.get_value(name)
                # special case to append a context with subcontext so it will stay selected in EditWdg
                if name == 'context' and value.find('/') != -1:
                    select.append_option(value, value)
                if value:
                    select.set_value(value)



        return top


#DEPRECATED
"""
class ProcessContextInputWdg(BaseInputWdg):
    '''This widget display a drop down for process context pairs.  It is
    primarily used as the input widget for adding a process/context combo
    onto a task base on a the parents pipeline'''

  
    def get_display(my):

        sobject = my.get_current_sobject()
        parent = sobject.get_parent()

        my.pipelines = []
        my.is_edit = False
        from tactic.ui.panel import EditWdg
        if hasattr(my, 'parent_wdg') and isinstance(my.get_parent_wdg(), EditWdg):
            if parent:
                pipeline_code = parent.get_value('pipeline_code')
                if pipeline_code:
                    my.pipelines = [Pipeline.get_by_code(pipeline_code)]
        else:
            my.pipelines = Search.eval("@SOBJECT(sthpw/pipeline)")
        my.pipeline_codes = [x.get_code() for x in my.pipelines]

         

        top = DivWdg()

        # put in a js callback to determine the to use.
        top.add_class("spt_input_top")

        # HACK! This isn't very well constructed
        top.add_attr("spt_cbjs_get_input_key", "return cell_to_edit.getAttribute('spt_pipeline_code')")

        context_list = []
        for i, pipeline_code in enumerate(my.pipeline_codes):
            pipeline = my.pipelines[i]

            div = DivWdg()
            div.add_class("spt_input_option")
            div.add_attr("spt_input_key", pipeline_code)

            
            name = my.get_input_name()
            select = SelectWdg(name)
            select.add_empty_option("-- Select a %s --" % my.get_name() )


            # FIXME: is this necessary?  If so, we should centralize it.
            select.add_behavior( { 'type': 'click',
               'cbjs_action': 'spt.dg_table.select_wdg_clicked( evt, bvr.src_el ); '
            } )
            
            #behavior = {
            #    'type': 'keyboard',
            #    'kbd_handler_name': 'DgTableSelectWidgetKeyInput',
            #}
            #select.add_behavior( behavior )

            # get the sub-pipeline processes as well
            processes = pipeline.get_processes(recurse=True)
            values = []
            labels = []
            for process in processes:
                if process.is_from_sub_pipeline():
                    process_name  = process.get_full_name()
                else:
                    process_name  = process.get_name()
                values.append("[label]")
                labels.append("--------------")
                values.append("[label]")
                labels.append("[%s]" % process_name)

                output_contexts = pipeline.get_output_contexts(process.get_name(), show_process=True)

                # put in the contexts
                for context in output_contexts:
                    out_process, out_context = context
                    context_list.append(out_context)
                    value = "%s||%s" % (process_name, out_context)
                    if value in values:
                        continue

                    values.append(value)
                    #labels.append("--> %s (%s)" % (out_process, out_context))
                    if process_name == out_context:
                        labels.append(out_context)
                    else:
                        labels.append("%s (from %s)" % (out_context, process_name))

                #values.append("%s||%s" % (process, "foo") )
                #labels.append("--> %s" % "foo")

            select.set_option("values", values) 
            select.set_option("labels", labels) 
            
            div.add(select)
            # there is only 1 select for EditWdg
            if hasattr(my, 'parent_wdg') and isinstance(my.get_parent_wdg(), EditWdg):
                process = sobject.get_value('process')
                context_value = sobject.get_value(my.get_name())
                if context_value:
                    # check if this context is predefined, if not, just use the base context part
                    if context_value not in context_list and context_value.find('/') != -1:
                        context_value, subcontext = context_value.split('/',1)
                    select.set_value('%s||%s'%(process, context_value))
            top.add(div)



        return top

"""
#DEPRECATED
"""
class ProcessContextAction(DatabaseAction):

    def execute(my):

        value = my.get_value()

        web = WebContainer.get_web()

        process = None
        if value.find("||") == -1:
            # we only have a process select, so process = context
            # prevent wiping out process
            if value:
                process = value
            context = value
        else:
            process, context = value.split("||")


        # WARNING! Do not try to uncomment this to try to accomodate 
        # for existing subcontext when changing context. It will inherit
        # double subcontext if the context happens to be in a format like
        # context/subcontext. It makes sense to wipe out the old subcontext anyways.
        '''
        old_context = my.sobject.get_value("context")
        if old_context.find("/") != -1:
            base, subcontext = old_context.split("/", 1)
        else:
            subcontext = ""
        if subcontext:
            context = "%s/%s" % (context, subcontext)
        '''
        if process:
            my.sobject.set_value("process", process)
        my.sobject.set_value("context", context)

"""
class SubContextInputWdg(TextWdg):


    def get_display(my):
        sobject = my.get_current_sobject()
        context = ''
        if sobject:
            context = sobject.get_value("context")
       
        if hasattr(my, 'parent_wdg') and isinstance(my.get_parent_wdg(), EditWdg):
            # FIXME: this is added for EditWdg where the KeyboardHandler captures the key and won't let user type
            behavior = {
                    'type': 'keyboard',
                    'kbd_handler_name': 'DgTableMultiLineTextEdit'
                }
            my.add_behavior(behavior)
        if not context or context.find("/") == -1:
            return  super(SubContextInputWdg, my).get_display()


        base, subcontext = context.split("/", 1)
        my.set_value(subcontext)
               
        return super(SubContextInputWdg, my).get_display()


class SubContextAction(DatabaseAction):

    def execute(my):
        # do nothing
        pass

    def postprocess(my):

        sobject = my.sobject
    

        subcontext = my.get_value()
        context = sobject.get_value("context")
        
        # if it is a simple context and no subcontext provided, return
        if not subcontext and context.find('/') == -1:
            return

        
        # replace the new subcontext
        
        # if existing context is empty, raise UserException
        # avoid value like '/subcontext'

        if not context:
            raise UserException('A context should be filled in first before entering a subcontext.')

        if context.find("/") != -1:
            context, old_subcontext = context.split("/", 1)

        if subcontext.strip():
            context = "%s/%s" % (context, subcontext)
        elif subcontext.strip() == '':
            # the case of removing the subcontext
            context = context
        
        my.sobject.set_value("context", context)
        my.sobject.commit()





