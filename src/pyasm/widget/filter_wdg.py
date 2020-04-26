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

__all__ = ['BaseFilterWdg', 'GeneralFilterWdg', 'HierarchicalFilterWdg',
        'ProcessContextWdg']

from pyasm.common import Environment, Container
from pyasm.search import SearchType, Search
from pyasm.biz import Schema, Pipeline, Project
from pyasm.web import Widget, DivWdg, HtmlElement, Table, SpanWdg, WebContainer, AjaxWdg, FloatDivWdg
from input_wdg import HiddenWdg, TextWdg, PasswordWdg, SelectWdg, FilterSelectWdg, CheckboxWdg
from pyasm.prod.biz import ProdSetting
from web_wdg import HintWdg

class BaseFilterWdg(Widget):
    '''represents the base filter'''
    def alter_search(self, search):
        pass




class GeneralFilterWdg(BaseFilterWdg):
    '''Represents a very generic filter matching a column to a value'''

    def init(self):
        self.column_select = SelectWdg("%s_column" % self.name)
        self.relation_select = SelectWdg("%s_relation" % self.name)
        self.value_text = TextWdg("%s_value" % self.name)

        self.columns = []

    def set_columns(self, columns):
        self.columns = columns

    def set_columns_from_search_type(self, search_type):
        self.columns = SearchType.get(search_type).get_columns(show_hidden=False)


    def get_display(self):

        if not self.columns:
            print self.options
            search_type = self.options.get("search_type")
            if search_type:
                self.set_columns_from_search_type(search_type)

        if not self.columns:
            self.columns = []

        span = SpanWdg()

        self.column_select.set_option("values", self.columns)
        self.column_select.set_persist_on_submit()
        span.add(self.column_select)

        relations = ["is", "is not", "contains", "does not contain", "is empty"]
        self.relation_select.set_option("values", relations)
        self.relation_select.set_persist_on_submit()
        span.add(self.relation_select)

        self.value_text.set_persist_on_submit()
        span.add(self.value_text)

        return span


    def alter_search(self, search):

        value = self.value_text.get_value()
        column = self.column_select.get_value()
        relation = self.relation_select.get_value()

        if relation == "is empty":
            search.add_where("(\"%s\" = '' or \"%s\" is NULL)" % (column, column) )
            return

        if not value or not column or not relation:
            return

        if relation == "is":
            search.add_filter(column, value)
        elif relation == "is not":
            search.add_where("\"%s\" != '%s'" % (column, value) )
        elif relation == "contains":
            search.add_regex_filter(column, value, op="EQI")
        elif relation == "does not contain":
            search.add_regex_filter(column, value, op="NEQI")
        elif relation == "is empty":
            search.add_where("(\"%s\" = '' or %s is NULL)" % (column, column) )


class HierarchicalFilterWdg(BaseFilterWdg):
    '''A filter that takes the hierarchical schema into account'''

    def init(self):
        self.schema = Schema.get()
        if not self.schema:
            self.parent_type = None
            self.select = None
            return

        web = WebContainer.get_web()
        self.search_type = web.get_form_value("filter|search_type")
        if not self.search_type:
            search_type = self.options.get("search_type")

        self.parent_type = self.schema.get_parent_type(self.search_type)
        if not self.parent_type:
            self.select = None
        else:
            self.select = FilterSelectWdg("filter|%s" % self.parent_type)

    def get_parent_type(self):
        return self.parent_type


    def get_display(self):

        widget = Widget()

        if not self.select:
            return widget

        if not self.schema:
            Environment.add_warning("No schema defined")
            widget.add("No schema defined")
            return widget


        if not self.search_type:
            Environment.add_warning("HierarchicalFilterWdg: Cannot find current search_type")
            widget.add("Cannot find current search_type")
            return widget

        span = SpanWdg(css="med")
        parent_type = self.get_parent_type()
        if parent_type:
            parent_type_obj = SearchType.get(parent_type)
            span.add("%s: " % parent_type_obj.get_value("title"))

        # assume that there is a code in the parent
        self.select.add_empty_option("-- Select --")
        self.select.set_option("query", "%s|code|code" % self.parent_type)
        span.add(self.select)

        widget.add(span)

        return widget


    def alter_search(self, search):
        if not self.select:
            return
        if not self.parent_type:
            return
        if not self.schema:
            return

        parent_code = self.select.get_value()
        parent = Search.get_by_code(self.parent_type, parent_code)
        if not parent:
            return
        parent.children_alter_search(search, self.search_type)

class ProcessContextWdg(AjaxWdg):
    '''A schema search type driven process/context select widget'''
    PUBLISH_TYPE = "asset"
    RELATED_SEARCH_TYPE = "related_search_type"
    def init(self):
        ''' initializes a few variables ''' 
        self.search_type = ''
        self.process = ''
        self.related_search_type = ''
        self.related_search_type_wdg = None

    def init_cgi(self):
        #keys = self.web.get_form_keys()
        self.search_type = self.web.get_form_value('search_type')
        self.related_search_type = self.web.get_form_value(self.RELATED_SEARCH_TYPE)
        self.process = self.web.get_form_value("%s_process" %self.PUBLISH_TYPE)
        #if self.search_type:
        self.add_inputs()

    def set_search_type(self, search_type):
        self.search_type = search_type
        self.add_inputs()

    def add_inputs(self):
        ''' register the inputs '''
        hidden = HiddenWdg("%s_process" %self.PUBLISH_TYPE, self.process)
        self.add_ajax_input(hidden)
        hidden = HiddenWdg("search_type" ,self.search_type)
        self.add_ajax_input(hidden)
        self.related_search_type_wdg = HiddenWdg(self.RELATED_SEARCH_TYPE ,self.related_search_type)
        self.add_ajax_input(self.related_search_type_wdg)
        
        div_id='process_context_wdg'
        self.main_div = DivWdg(id=div_id)
        self.set_ajax_top(self.main_div)

    def get_display(self):
        search_type = self.search_type
        related_search_type = self.related_search_type_wdg.get_value()
        if related_search_type:
            search_type = related_search_type
        hier_sel = self.get_hier_sel(search_type)
        selected_related_search_type = hier_sel.get_value()
        
        process_wdg = self.get_process_wdg(search_type)
        context_wdg = self.get_context_wdg(search_type)
        widget = self.main_div
        if self.is_from_ajax(True):
            widget = Widget()
        else:
            self.set_ajax_top(widget)
        
        hidden = HiddenWdg("search_type" ,search_type)
        widget.add(hidden)
        
        hier_sel.add_event('onchange', self.get_refresh_script(show_progress=False))
        widget.add(hier_sel)
        #Tooltip doesn't work too well
        #hint = HintWdg('Related search type you can optionally select to drive the process')
       
        widget.add(HtmlElement.br(2))
        widget.add(process_wdg)
        
        widget.add(context_wdg)
        return widget

    def get_hier_sel(self, search_type):
        sel = SelectWdg(self.RELATED_SEARCH_TYPE, label='Related Search Type: ')
        sel.add_empty_option()
        schema = Schema.get()
        search_type_list = [search_type]
        if schema:
            parent_search_type = schema.get_parent_type(search_type)
            if parent_search_type:
                search_type_list.append(parent_search_type)
            child_types = schema.get_child_types(search_type)
            search_type_list.extend(child_types)

        sel.set_option('values', search_type_list)

        sel.set_value(self.related_search_type)
        return sel
        
    def get_process_wdg(self, search_type):
        '''this should appear in front of the context_filter_wdg'''
        from pyasm.prod.web import ProcessSelectWdg
        self.process_select = ProcessSelectWdg(label='Process: ', \
            search_type=search_type, css='', has_empty=False, \
            name="%s_process" %self.PUBLISH_TYPE)

        self.process_select.add_empty_option('- Select -')
        self.process_select.set_event('onchange',\
                self.get_refresh_script(show_progress=False))
        self.process_select.set_value(self.process)
        #self.process_select.set_persistence()
        #self.process_select.set_submit_onchange()
        # this is only applicable in Shot Tab
        '''
        filter = Container.get('process_fitter')
        if filter:
            self.process_select.set_value(filter.get_value())
        '''
        div = DivWdg(self.process_select)
        div.add_style('padding-right','10px')
        return div

    def get_context_wdg(self, search_type):
        '''drop down which selects which context to checkin'''
        # add a filter
        # use a regular SelectWdg with submit instead of FilterSelectWdg
        filter_div = FloatDivWdg("Context / subcontext:")
        select = SelectWdg("publish_context")
        labels, values = self.get_context_data(search_type, self.process)
        select.set_option("values", "|".join(values))
        select.set_option("labels", "|".join(labels))
        select.append_option('publish','publish')
        select.add_style("font-size: 0.8em")
        select.add_style("margin: 0px 3px")

        # explicitly set the value
        current = select.get_value()
        if current in values:
            context = current
        elif values:
            context = values[0]
        else:
            context = ""
 
        web = WebContainer.get_web()
        web.set_form_value("publish_context", context)

        select.set_value( context )

        # set it to a instance variable
        self.context_select = select

        filter_div.add(select)

        # if specified, add a sub_context
        base_search_type = SearchType(search_type).get_base_key()
        settings = ProdSetting.get_value_by_key("%s/sub_context" % context,\
                base_search_type)
        filter_div.add( "/ ")
        sub_context = None
        if settings:
            sub_context = SelectWdg("publish_sub_context")
            sub_context.set_option("values", settings)
            sub_context.set_submit_onchange()
            sub_context.add_empty_option("<- Select ->")
        else:
            # provide a text field
            sub_context = TextWdg("publish_sub_context")
            sub_context.set_attr('size','10') 
        sub_context.set_persistence()
        filter_div.add( sub_context )
        self.sub_context_select = sub_context
        #filter_div.add_style('padding-right','10px')

        return filter_div


    def get_context_data(self, search_type='', process=''):
        '''get the labels and values of contexts that can be checked in with this widget'''

        # TODO: this also shows input contexts ... it should only show output
        # contexts
        if not search_type:
            search_type = self.search_type

    

        pipelines = Pipeline.get_by_search_type(search_type, Project.get_project_code() )

        
        if not pipelines:
            return [], []
        # account for sub-pipeline
        if '/' in process:
            process = process.split('/', 1)[1]
        contexts = []
        for pipeline in pipelines:
            pipeline_contexts = []
            pipeline_processes = pipeline.get_process_names()
            if process:
                if process not in pipeline_processes:
                    continue
                pipeline_contexts = pipeline.get_output_contexts(process)
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

        labels = contexts
        values = contexts


        return labels, values




