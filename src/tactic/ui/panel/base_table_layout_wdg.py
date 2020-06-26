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


__all__ = ["BaseTableLayoutWdg"]

from pyasm.common import Common, Environment, jsondumps, jsonloads, Container, TacticException
from pyasm.search import SearchType, Search, SqlException, SearchKey, SObject, DbContainer
from pyasm.web import WebContainer, Table, DivWdg, SpanWdg, Widget, HtmlElement
from pyasm.widget import WidgetConfig, WidgetConfigView, IconWdg, IconButtonWdg, HiddenWdg
from pyasm.biz import ExpressionParser, Project, ProjectSetting
from pyasm.security import Sudo

from tactic.ui.common import BaseConfigWdg, BaseRefreshWdg
from tactic.ui.container import Menu, MenuItem, SmartMenu
from tactic.ui.container import HorizLayoutWdg
from tactic.ui.widget import DgTableGearMenuWdg, ActionButtonWdg, ButtonNewWdg

from .layout_wdg import SwitchLayoutMenu

import types, re

import six
basestring = six.string_types



class BaseTableLayoutWdg(BaseConfigWdg):

    GROUP_WEEKLY = "weekly"
    GROUP_MONTHLY = "monthly"


    def can_inline_insert(self):
        return True

    def can_save(self):
        return True

    def can_expand(self):
        return True
    def get_expand_behavior(self):
        return None

    def can_add_columns(self):
        return True

    def can_select(self):
        return True

    def can_use_gear(self):
        return True



    def __init__(self, **kwargs):

        # get the them from cgi
        self.handle_args(kwargs)
        self.kwargs = kwargs

        self.help_alias = 'views-quickstart|what-are-views'
        mode = kwargs.get("mode")

        # required args
        self.table_id = kwargs.get('table_id')
        if not self.table_id:
            self.table_id = kwargs.get('id')
        if not self.table_id:
            num = Common.randint(0,10000)
            self.table_id = "main_body_table_%s"%num
        if mode == 'insert':
            self.table_id = "%s_insert" %self.table_id

        self.table_id = self.table_id.replace(" ", "_")

        self.target_id = kwargs.get('target_id')
        if not self.target_id:
            self.target_id = "main_body"

            
        self.search_type = kwargs.get('search_type')
        if not self.search_type:
            raise TacticException("Must define a search type")
        self.view = kwargs.get('view')
        if not self.view or self.view == "None":
            self.view = 'table'

        self.do_search = True
        self.search = None
        self.search_view = kwargs.get('search_view')
        self.search_key = kwargs.get("search_key")
        self.ingest_data_view = kwargs.get("ingest_data_view") or ""
        self.ingest_custom_view = kwargs.get("ingest_custom_view") or ""

        # DEPRECATED: Do not use
        if not self.view:
            self.view = kwargs.get('config_base')


        #self.show_search_limit = kwargs.get('show_search_limit')
        #if self.show_search_limit in ["false", False]:
        #    self.show_search_limit = False
        #else:
        #    self.show_search_limit = True
        self.show_search_limit = self.get_setting("search_limit")

        self.is_refresh = kwargs.get('is_refresh') == 'true'
        self.aux_info = kwargs.get('aux_info')
        self.vertical_text = kwargs.get('vertical_text') == 'true'

        self.order_widget = None
        self.group_element = ""
        self.group_interval = ""
        self.group_sobjects = []
        self.order_element = ""
        self.show_retired_element = ""

        self.num_lock_columns = kwargs.get("num_lock_columns") or 0
        if self.num_lock_columns:
            self.num_lock_columns = int(self.num_lock_columns)

        self.js_load = kwargs.get("js_load") or False
        if self.js_load in ['true', True]:
            self.js_load = True
        else:
            self.js_laod = False



        self.group_info = DivWdg()
        self.group_info.add_class("spt_table_group_info")


        self.element_names = []

        # handle config explicitly set
        config = self.kwargs.get("config")
        config_xml = self.kwargs.get("config_xml")
        config_code = self.kwargs.get("config_code")
        self.config_xml = config_xml

        if config_xml:
            # get the base configs
            config = WidgetConfigView.get_by_search_type(search_type=self.search_type, view=self.view)
            extra_config = WidgetConfig.get(view=self.view, xml=config_xml)
            config.get_configs().insert(0, extra_config)

        elif config_code:
            config_sobj = Search.get_by_code("config/widget_config", config_code)
            view = config_sobj.get_value("view")
            config = WidgetConfigView(search_type=None, view=view, configs=[config_sobj])



        elif not config:
            custom_column_configs = WidgetConfigView.get_by_type("column") 
            
            # handle element names explicitly set
            self.element_names = self.kwargs.get("element_names")
            if self.element_names:
                config = WidgetConfigView.get_by_search_type(search_type=self.search_type, view=self.view)
                if isinstance(self.element_names, basestring):
                    self.element_names = self.element_names.split(",")
                    self.element_names = [x.strip() for x in self.element_names]
                
                config_xml = "<config><custom layout='TableLayoutWdg'>"
                for element_name in self.element_names:
                        config_xml += "<element name='%s'/>" % element_name
                config_xml += "</custom></config>"
                # self.view is changed for a reason, since a dynamic config supercedes all here
                # We don't want to change the overall view ... just the
                # top level config
                #self.view = "custom"
                #extra_config = WidgetConfig.get(view=self.view, xml=config_xml)
                extra_config = WidgetConfig.get(view="custom", xml=config_xml)
                config.get_configs().insert(0, extra_config)



            else:
                config = WidgetConfigView.get_by_search_type(search_type=self.search_type, view=self.view)
            
            config.get_configs().extend( custom_column_configs )
        #
        # FIXME: For backwards compatibility. Remove this
        #
        self.aux_data = []
        self.row_ids = {}

        # there is this whole assumption that search_type is set in the
        # form values
        web = WebContainer.get_web()
        web.set_form_value("search_type", self.search_type)
        web.set_form_value("ref_search_type", self.search_type)

        self.attributes = []

        super(BaseTableLayoutWdg,self).__init__(search_type=self.search_type, config_base=self.view, config=config)

        self.view_attributes = self.config.get_view_attributes()

        # self.parent_key is used to determine the parent for inline add-new-items purposes
        self.parent_key = self.kwargs.get("parent_key")
        self.parent_path = self.kwargs.get("parent_path")
        self.checkin_context = self.kwargs.get("checkin_context")
        self.checkin_type = self.kwargs.get("checkin_type")
        if not self.checkin_type:
            self.checkin_type = 'auto'
        self.state = self.kwargs.get("state")
        self.state = BaseRefreshWdg.process_state(self.state)
        self.expr_sobjects = []
        if not self.parent_key:
            self.parent_key = self.state.get("parent_key")

        if self.parent_key == 'self':
            self.parent_key = self.search_key

        if not self.parent_key:
            # generate it. parent_key could be none if the expression evaluates to None
            expression = self.kwargs.get('expression')
            if expression:
                if self.search_key and (self.search_key not in ["%s", 'None']):
                    start_sobj = Search.get_by_search_key(self.search_key)
                else:
                    start_sobj = None
                try:
                    sudo = Sudo()
                    self.expr_sobjects = Search.eval(expression, start_sobj, list=True)
                finally:
                    sudo.exit()
                parser = ExpressionParser() 
                related = parser.get_plain_related_types(expression)

                related_type = None
                if len(related) > 1:
                    # find the second last search_type in the expr
                    m = re.match("^(\w+/\w+)", related[-2])
                    if m:
                        related_type = m.groups()[0]
                    else:
                        related_type = None
                
                if not related_type and self.search_key:
                    # this is needed for single search type expression
                    related_type = SearchKey.extract_search_type(self.search_key)
                  
                if self.expr_sobjects and related_type and not isinstance(self.expr_sobjects[0], Search):
                    # Even if these expression driven sobjects have more than 1 parent.. we can only take 1 parent key
                    # for insert popup purpose.. This doesn't affect the search though since with expression, the search logic
                    # doesn't go through the regular Search
                    related = self.expr_sobjects[0].get_related_sobject(related_type)
                    if related:
                        self.parent_key = SearchKey.get_by_sobject(related, use_id=True)

                elif related_type and self.search_key and related_type in self.search_key:
                    # the expression table could start out empty
                    self.parent_key = self.search_key

                   
            else:
                self.parent_key = self.search_key


        if self.parent_key == "__NONE__":
            self.parent_key = ""
            self.no_results = True
        else:
            self.no_results = False

        # clear if it is None
        if not self.parent_key:
             self.parent_key = ''



        # handle a connect key
        self.connect_key = self.kwargs.get("connect_key")
    

        self.table = Table()
        self.table.set_id(self.table_id)


        # this unique id is used to find quickly find elements that
        # are children of this table
        self.table.add_attr("unique_id", self.table_id)

        self.table.add_class("spt_table")
        mode = self.kwargs.get("mode")
        
        # this makes Task edit content not refreshing properly, commented out 
        # for now
        #if mode != "insert":
        self.table.add_class("spt_table_content")

        width = kwargs.get('width')
        if width:
            self.table.add_style("width: %s" % width)

        self.min_cell_height = kwargs.get('min_cell_height')
        if not self.min_cell_height:
            self.min_cell_height = self.state.get("min_cell_height")
        if not self.min_cell_height:
            self.min_cell_height = "20"

        self.simple_search_view = self.kwargs.get("simple_search_view")
        # Always instantiate the search limit for the pagination at the bottom
        
        from tactic.ui.app import SearchLimitWdg
        self.search_limit = SearchLimitWdg()

        self.items_found = 0

        self.tbodies = []
        self.chunk_num = 0
        self.chunk_size = 100
        self.chunk_iterations = 0

        self.search_wdg = None

        # Needed for MMS_COLOR_OVERRIDE ...
        web = WebContainer.get_web()
        self.skin = web.get_skin()

        # Set up default row looks ...
        self.look_row = 'dg_row'
        self.look_row_hilite = 'dg_row_hilite'
        self.look_row_selected = 'dg_row_selected'
        self.look_row_selected_hilite = 'dg_row_selected_hilite'

        # MMS_COLOR_OVERRIDE ...
        #if self.skin == 'MMS':
        #    self.look_row = 'mms_dg_row'
        #    self.look_row_hilite = 'mms_dg_row_hilite'
        #    self.look_row_selected = 'mms_dg_row_selected'
        #    self.look_row_selected_hilite = 'mms_dg_row_selected_hilite'


        self.palette = web.get_palette()

        self.search_container_wdg = DivWdg()
        # a dictionary of widget class name and boolean True as they are drawn
        self.drawn_widgets = {}

    def get_aux_info(self):
        return self.aux_info

    def get_kwargs(self):
        return self.kwargs



    def get_table_id(self):
        return self.table_id

    def get_table(self):
        return self.table

    def get_view(self):
        return self.view

    def set_items_found(self, number):
        self.items_found = number
    
    def set_search_wdg(self, search_wdg):
        self.search_wdg = search_wdg


    def is_expression_element(self, element_name):
        from tactic.ui.table import ExpressionElementWdg
        widget = self.get_widget(element_name)
        return isinstance(widget, ExpressionElementWdg)





    def get_alias_for_search_type(self, search_type):
        if search_type == 'config/naming':
            self.help_alias = 'project-automation-file-naming'
        elif search_type == 'sthpw/clipboard':
            self.help_alias = 'clipboard'
        return self.help_alias



    def handle_args(self, kwargs):
        # verify the args
        #args_keys = self.get_args_keys()
        args_keys = self.ARGS_KEYS
        for key in kwargs.keys():
            if key not in args_keys:
                #raise TacticException("Key [%s] not in accepted arguments" % key)
                pass



    def get_order_element(self, order_element):
        direction = 'asc'
        if order_element.find(" desc") != -1:
            tmp_order_element = order_element.replace(" desc", "")
            direction = 'desc'
        elif self.order_element.find(" asc") != -1:
            tmp_order_element = order_element.replace(" asc", "")
            direction = 'asc'
        else:
            tmp_order_element = order_element
            
        return tmp_order_element, direction

    def alter_search(self, search):
        '''give the table a chance to alter the search'''
       
        from tactic.ui.filter import FilterData
        filter_data = FilterData.get_from_cgi()


        # solution for state filter grouping or what not
        # combine the 2 filters from kwarg and state
        state_filter = ''
        if self.state.get('filter'):
            state_filter = self.state.get('filter')
        if self.kwargs.get('filter'): 
            state_filter = '%s%s' %(state_filter, self.kwargs.get('filter') )

        if self.kwargs.get('op_filters'):
            search.add_op_filters(self.kwargs.get("op_filters"))

        values = filter_data.get_values_by_prefix("group")
        order = WebContainer.get_web().get_form_value('order')

        # user-chosen order has top priority
        if order:
            self.order_element = order
            if not values:
                tmp_order_element, direction = self.get_order_element(self.order_element)
                
                widget = self.get_widget(tmp_order_element)
                self.order_widget = widget
                try:
                    widget.alter_order_by(search, direction)
                except AttributeError:
                    search.add_order_by(self.order_element, direction)


        # passed in filter overrides
        if values:

            group_values = values[0]

            # the group element is always ordered first
            self.group_element = group_values.get("group")

            if self.group_element == 'true':
                self.group_element = True
            elif self.group_element:
                # used in Fast Table
                self.group_interval = group_values.get("interval")
                # order by is no longer coupled with group by
                # it can be turned on together in the context menu Group and Order by
            else:
                self.group_element = False

            self.order_element = group_values.get("order")

            if self.order_element:
                tmp_order_element, direction  = self.get_order_element(self.order_element)
                widget = self.get_widget(tmp_order_element)
                self.order_widget = widget
                try:
                    widget.alter_order_by(search, direction)
                except AttributeError:
                    tmp_order_element_list = tmp_order_element.split(".")
                    if 'parent' in tmp_order_element_list:
                        i = tmp_order_element_list.index('parent')
                        sobject = search.get_sobjects()[0]
                        parent = sobject.get_parent()
                        parent_search_type = parent.get_search_type()
                        
                        parent_search_type = parent_search_type + "." + tmp_order_element_list[1 + i]

                        search.add_order_by(parent_search_type, direction)
                    else:
                        search.add_order_by(tmp_order_element, direction)

            self.show_retired_element = group_values.get("show_retired")
            if self.show_retired_element == "true":
                search.set_show_retired(True)




        order_by = self.kwargs.get('order_by')
        if order_by:
            search.add_order_by(order_by)
            # if nothing is set by user or filter data, use this kwarg
            if not self.order_element:
                self.order_element = order_by

        # make sure the search limit is the last filter added so that the counts
        # are correct
        if self.search_limit:
            limit = self.kwargs.get("chunk_limit")
            if not limit:
                limit = self.kwargs.get('search_limit')
                if limit:
                    try:
                        limit = int(limit)
                        self.search_limit.set_limit(limit)
                    except ValueError as e:
                        pass
                stated_limit = self.search_limit.get_stated_limit()
                if stated_limit:
                    limit = stated_limit
                if not limit:
                    limit = 100
            """
            self.chunk_num = self.kwargs.get("chunk_num")

            if self.chunk_num:
                self.chunk_num = int(self.chunk_num)
            else:
                self.chunk_num = 0

            # if the total to be display after this chunk is greater than
            # the limit, then reduce to fit the limit
            total = (self.chunk_num+1)*self.chunk_size
            if total > limit:
                diff = limit - (total-my.chunk_size)
                #self.search_limit.set_chunk(diff, self.chunk_num)
                self.search_limit.set_chunk(self.chunk_size, self.chunk_num, diff)
            else:
                self.search_limit.set_chunk(self.chunk_size, self.chunk_num)
            """
            # alter the search
            self.search_limit.set_search(search)
            self.search_limit.alter_search(search)


    def handle_search(self):
        '''method where the table handles it's own search on refresh'''


        from tactic.ui.app.simple_search_wdg import SimpleSearchWdg
        self.keyword_column = SimpleSearchWdg.get_search_col(self.search_type, self.simple_search_view)


        if self.is_sobjects_explicitly_set():
            return

        if not self.is_refresh and self.kwargs.get("do_initial_search") in ['false', False, 'hidden']:
            return






        expr_search = None
        expression = self.kwargs.get('expression')
        if self.expr_sobjects:
            if isinstance(self.expr_sobjects[0], Search):
                expr_search = self.expr_sobjects[0]
            else:
                # this is not so efficient: better to use @SEARCH,
                # but we support in anyway, just in case
                try:
                    sudo = Sudo()

                    expr_search = Search(self.search_type)
                    ids = SObject.get_values(self.expr_sobjects, 'id')
                    expr_search.add_filters('id', ids)
                finally: 
                    sudo.exit()

        elif expression:
            # if the expr_sobjects is empty and there is an expression, this
            # means that the expression evaluated to no sobjects
            # which means the entire search is empty
            self.sobjects = []
            return


        # Not sure if filter_view should ever be simple_search_view (this is how it was before)
        filter_view = self.kwargs.get('filter_view') or self.simple_search_view


        # don't set the view here, it affects the logic in SearchWdg
        filter_json = ''
        if self.kwargs.get('filter'):
            filter_json = self.kwargs.get('filter')
            
        # turn on user_override since the user probably would alter the saved search 
        limit = self.kwargs.get('search_limit')
        custom_search_view = self.kwargs.get('custom_search_view')
        if not custom_search_view:
            custom_search_view = ''

        run_search_bvr = self.kwargs.get('run_search_bvr')

        #self.search_wdg = None
        if not self.search_wdg:
            self.search_wdg = self.kwargs.get("search_wdg")
        if not self.search_wdg:
            search = self.kwargs.get("search")

            try:
                sudo = Sudo()

                from tactic.ui.app import SearchWdg
                # if this is not passed in, then create one
                # custom_filter_view and custom_search_view are less used, so excluded here
                self.search_wdg = SearchWdg(search=search, search_type=self.search_type, state=self.state, filter=filter_json, view=self.search_view, user_override=True, parent_key=None, run_search_bvr=run_search_bvr, limit=limit, custom_search_view=custom_search_view, filter_view=filter_view)
            finally:
                sudo.exit()
        
        search = self.search_wdg.get_search()
        self.search = search



        from tactic.ui.filter import FilterData
        filter_data = FilterData.get_from_cgi()


        keywords = self.kwargs.get('keywords')
        if keywords:
            keywords_columns = self.kwargs.get('keywords_columns')
            if not keywords_columns:
                keywords_column = 'keywords'
                search.add_text_search_filter(keywords_column, keywords)
            else:
                search.add_text_search_filters(keywords_columns, keywords)

        else:

            keyword_values = filter_data.get_values_by_prefix("keyword")

            if keyword_values:
                cross_db = None
                if self.search_type and self.simple_search_view:
                    search_config = WidgetConfigView.get_by_search_type(search_type=self.search_type, view=self.simple_search_view)
                    if search_config:
                        xml = search_config.configs[0].xml
                        cross_db_node = xml.get_node("config/%s/element[@name='keywords']/display/cross_db" % self.simple_search_view)
                        if cross_db_node is not None:
                            cross_db = xml.get_node("config/%s/element[@name='keywords']/display/cross_db" % self.simple_search_view).text

                keyword_value = keyword_values[0].get('value')
                if cross_db:
                    keyword_values[0]['partial'] = "on"
                if keyword_value:
                    from tactic.ui.filter import KeywordFilterElementWdg
                    keyword_filter = KeywordFilterElementWdg(
                            column=self.keyword_column,
                            mode="keyword",
                            cross_db=cross_db
                    )
                    keyword_filter.set_values(keyword_values[0])
                    keyword_filter.alter_search(search)


        if self.no_results:
            search.set_null_filter()


        if expr_search:
            search.add_relationship_search_filter(expr_search)


        if self.connect_key == "__NONE__":
            search.set_null_filter()
        elif self.connect_key:
            # get all of the connections of this src
            from pyasm.biz import SObjectConnection
            src_sobjects = Search.get_by_search_key(self.connect_key)
            dst_sobjects = src_sobjects.get_connections(context='task')
            ids = [x.get_id() for x in dst_sobjects]
            search.add_filters("id", ids)



        # add an exposed search
        simple_search_view = self.kwargs.get('simple_search_view')
        simple_search_config = self.kwargs.get('simple_search_config')
        if simple_search_view:
            self.search_class = "tactic.ui.app.simple_search_wdg.SimpleSearchWdg"
        elif simple_search_config:
            self.search_class = "tactic.ui.app.simple_search_wdg.SimpleSearchWdg"
            simple_search_view = None
        else:
            # add a custom search class
            self.search_class = self.kwargs.get('search_class')
            simple_search_view = self.kwargs.get("search_view")
    

        
        if self.search_class and self.search_class not in  ['None','null']:
            kwargs = {
                "search_type": self.search_type,
                "search_view": simple_search_view,
                "keywords": self.kwargs.get("keywords"),
                "show_saved_search": self.kwargs.get("show_saved_search"),
            }

            if simple_search_config:
                kwargs['search_config'] = simple_search_config

            simple_search_wdg = Common.create_from_class_path(self.search_class, kwargs=kwargs)
            simple_search_wdg.alter_search(search)


        # see if any of the filters have a class handler defined
        from tactic.ui.filter import FilterData
        filter_data = FilterData.get_from_cgi()
        for item in filter_data.data:
            class_name =  item.get('class_name')
            prefix = item.get('prefix')
            if class_name:
                handler = Common.create_from_class_path(class_name)
                handler.alter_search(search)

        # re-get parent key from kwargs because self.parent is retrieved
        # This only is used if an expression is not used.  Otherwise, the
        # search_key is applied to the expression
        parent_key = None
        if not expression:
            parent_key = self.kwargs.get("search_key")
        if not parent_key:
            parent_key = self.kwargs.get("parent_key")
        if parent_key and parent_key != "%s" and parent_key not in ["__NONE__", "None"]:
            parent = Search.get_by_search_key(parent_key)
            if not parent:
                self.sobjects = []
                self.items_found = 0
                return
            # NOTE: this parent path is a bit of a hack to make tables that
            # are not immediate relations to still be accessed
            if self.parent_path:
                logs = Search.eval("@SOBJECT(%s)" % self.parent_path, parent, list=True)
                if logs:
                    search.add_filters("id", [x.get_id() for x in logs] )
                else:
                    search.set_null_filter()

            else:
                search.add_relationship_filter(parent)

        try:
            self.alter_search(search)
            self.items_found = search.get_count()

            if self.do_search == True:
                self.sobjects = search.get_sobjects()

        except SqlException as e:
            self.search_wdg.clear_search_data(search.get_base_search_type())

        self.element_process_sobjects(search)






    def element_process_sobjects(self, search):
        # give each widget a chance to alter the order post search
        for widget in self.widgets:
            try:
                sobjects = widget.process_sobjects(self.sobjects, search)
            except Exception as e:
                #print(str(e))
                pass
            else:
                if sobjects:
                    self.sobjects = sobjects

    def process_sobjects(self):
        '''provides the opportunity to post-process the search'''
        class_name = 'mms.TerminalSearchWdg'
        search = Common.create_from_class_path(class_name)
        sobjects = search.process_sobjects(self.sobjects)
        if sobjects != None:
            self.sobjects = sobjects
        
    def set_as_panel(self, widget):
        widget.add_class("spt_panel")
        widget.add_attr("spt_class_name", Common.get_full_class_name(self) )
        for name, value in self.kwargs.items():
            if value == None:
                continue
            if isinstance(value, bool):
                if value == True:
                    value = 'true'
                else:
                    value = 'false'
            if not isinstance(value, basestring):
                value = str(value)
            # replace " with ' in case the kwargs is a dict
            value = value.replace('"', "'")
            widget.add_attr("spt_%s" % name, value)

        # add view attributes
        if self.view_attributes:
            value = jsondumps(self.view_attributes)
            # replace " with ' in case the kwargs is a dict
            value = value.replace('"', "'")
            widget.add_attr("spt_view_attrs" , value)



    def get_show_insert(self):
        show_insert = self.view_attributes.get("insert") or True

        # if edit_permission on the sobject is not allowed then we don't
        # allow insert
        if self.edit_permission == False:
            show_insert = False

        if show_insert:
            show_insert = self.get_setting("insert")

        return show_insert



    def set_default_off(self):

        if self.kwargs.get("set_shelf_defailt") == "off":

            settings = {
                    "show_insert": False,
                    "show_expand": False,

            }

        shelf_elements = self.kwargs.get("shelf_elements")
        if shelf_elements:
            shelf_elements = shelf_elements.split(",")



    def get_setting(self, name):
        settings = self.kwargs.get("settings") or {}

        """
        settings = {
            "gear": {
                    'Tasks': ['Show Tasks'],
                    'Edit': ['Retire Selected Items', 'Delete Selected Items'],
                    'View': ['Save a New View'],
            },
            #"save": True
            #"search_limit": True,
            #"expand": True,
            #"insert": True,
            "layour_switcher": True,
        }
        #settings = None
        #settings = "save|insert|search|keyword_search"
        """


        settings_default = {
            'header_background': True
        }



        if isinstance(settings, basestring):
            settings = settings.split("|")

        if isinstance(settings, list):
            new_settings = {}
            for item in settings:
                new_settings[item] = True
            settings = new_settings

        if 'gear' in settings and settings.get("gear") == True:
            gear_settings = self.kwargs.get("gear_settings")
            if isinstance(gear_settings, basestring):
                if gear_settings.startswith("{") and gear_settings.endswith("}"):
                    # HACK:
                    gear_settings = gear_settings.replace("'", '"')
                    gear_settings = jsonloads(gear_settings)
                else:
                    gear_settings = gear_settings.split("|")

            if isinstance(gear_settings, list):
                new_gear_settings = {}
                for item in gear_settings:
                    new_gear_settings[item] = True
                gear_settings = new_gear_settings

            if not gear_settings:
                gear_settings = {}

            settings["gear"] = gear_settings


        default = True
        if name in ["gear"]:
            default = True
        elif name in ['header_background']:
            default = True



        value = None
        if settings:
            if settings.get(name) in [None, False, "false"]:
                # if not in settings, then the default is false
                default = False
            if name not in settings:
                value = settings_default.get(name)
            else:
                value = settings.get(name)


        # some special settings if the value is False
        if value in [False, None]:
            show_name = "show_%s" % name

            if default == True:
                if self.kwargs.get(show_name) not in ['false', False]:
                    value = True
                else:
                    value = False

            else:
                if self.kwargs.get(show_name) not in ['true', True]:
                    value = False
                else:
                    value = True


        return value


    def get_shelf_styles(self):


        style = HtmlElement.style("""
        
            .SPT_DTS { 
                color: #000;
                padding-top: 2px;
                padding-right: 8px;
                background: #fcfcfc;
            }
      
            .spt_search_limit_activator {
                border-radius: 6px;
                font-size: 10px;
                vertical-align: middle;
                color: rgb(0, 0, 0);
                border-width: 1px;
                padding: 5px;
                border-color: rgb(187, 187, 187);
                border-style: none;
                margin: 0px 10px;
                display: inline-block;
            
            }

            .spt_table_search_limit {
                color: #000;
                width: 300px;
                background: #FFFFFF;
            }

        """)

        return style


    def get_bootstrap_shelf_styles(self):

        return HtmlElement.style(""" 

            .spt_table_action_wdg {
                 background: var(--spt_palette_background2);
            }
            
        """)


    def get_action_wdg(self):

        
        # add the ability to put in a custom shelf
        shelf_view = self.kwargs.get("shelf_view")

        # determine from the view if the insert button is visible
        show_insert = self.get_show_insert()
        show_retired = self.view_attributes.get("retire")
        show_delete = self.view_attributes.get("delete")


        from tactic.ui.widget import TextBtnWdg, TextBtnSetWdg

        div = DivWdg() 
        div.add_class("spt_table_action_wdg")
        div.add_class("SPT_DTS")

        if self._use_bootstrap():
            div.add(self.get_bootstrap_shelf_styles())
        else:
            div.add(self.get_shelf_styles())

        # the label on the commit button
        commit_label = 'Save'

        # Look for custom gear menu items from configuration ...
        custom_gear_menus = None

        try:
            search = Search('config/widget_config')
            search.add_filter("view", "gear_menu_custom")
            search.add_filter("search_type", self.search_type)
            config_sobj = search.get_sobject()
        except Exception as e:
            print("WARNING: When trying to find config: ", e)
            config_sobj = None

        if config_sobj:
            config_xml = config_sobj.get_xml_value("config")
            stmt = 'custom_gear_menus = %s' % config_xml.get_value("config/gear_menu_custom").strip()
            try:
                exec(stmt)
            except:
                custom_gear_menus = "CONFIG-ERROR"


        # add gear menu here
        self.view_save_dialog = None
        show_gear = self.get_setting("gear")
        if self.can_use_gear() and show_gear:
            # Handle configuration for custom script (or straight javascript script) on "post-action on delete"
            # activity ...
            cbjs_post_delete = ''

            if self.kwargs.get("post_delete_script"):
                post_delete_script = self.kwargs.get("post_delete_script")
                # get the script code from the custom_script table of the project ...
                prj_code = Project.get_project_code()
                script_s_key = "config/custom_script?project=%s&code=%s" % (prj_code, post_delete_script)
                custom_script_sobj = Search.get_by_search_key( script_s_key )
                if not custom_script_sobj:
                    print('Did NOT find a code="%s" custom_script entry for post DG table save' % (post_delete_script))
                cbjs_post_delete = custom_script_sobj.get_value('script')

            if self.kwargs.get("post_delete_js"):
                cbjs_post_delete = self.kwargs.get("post_delete_js")

            embedded_table =  self.kwargs.get("__hidden__") == 'true'

            gear_settings = self.get_setting("gear")
            if not gear_settings:
                gear_settings = self.get_setting("gear_settings")

           
            btn_dd = DgTableGearMenuWdg(
                menus=gear_settings,
                layout=self,
                table_id=self.get_table_id(),
                search_type=self.search_type, view=self.view,
                parent_key=self.parent_key,
                cbjs_post_delete=cbjs_post_delete,
                show_delete=show_delete,
                custom_menus=custom_gear_menus,
                show_retired=show_retired, embedded_table=embedded_table,
                ingest_data_view= self.ingest_data_view,
                ingest_custom_view= self.ingest_custom_view
            )

            self.gear_menus = btn_dd.get_menu_data()
            self.view_save_dialog = btn_dd.get_save_dialog()
            div.add(btn_dd)

        else:
            self.gear_menus = None
            btn_dd = Widget()


        column = "keywords"
        simple_search_mode = self.kwargs.get("simple_search_mode")




        div.add_style("display: flex")
        div.add_style("align-items: center")



        title_wdg = self.get_title_wdg()
        if title_wdg:
            div.add(title_wdg)



        # default to true
        show_keyword_search = self.get_setting("keyword_search")
        if show_keyword_search:
            from tactic.ui.filter import FilterData
            filter_data = FilterData.get_from_cgi()

            keyword_div = DivWdg()
            keyword_div.add_class("spt_table_search")
            hidden = HiddenWdg("prefix", "keyword")
            keyword_div.add(hidden)


            keywords = self.kwargs.get("keywords")
            if keywords:
                values = {
                    "value": keywords
                }

            else:

                values_list = filter_data.get_values_by_prefix("keyword")
                if values_list:
                    values = values_list[0]
                else:
                    values = {}


            from tactic.ui.app.simple_search_wdg import SimpleSearchWdg
            self.keyword_column = SimpleSearchWdg.get_search_col(self.search_type, self.simple_search_view)
            self.keyword_hint_text = SimpleSearchWdg.get_hint_text(self.search_type, self.simple_search_view)

            show_toggle = False
            if simple_search_mode == "hidden":
                show_toggle = True

            from tactic.ui.filter import KeywordFilterElementWdg
            keyword_filter = KeywordFilterElementWdg(
                    column=self.keyword_column,
                    mode="keyword",
                    filter_search_type=self.search_type,
                    icon="",
                    show_partial=False,
                    show_toggle=show_toggle,
                    hint_text=self.keyword_hint_text,
            )
            keyword_filter.set_values(values)
            keyword_div.add(keyword_filter)

            keyword_div.add_behavior( {
                'type': 'click_up',
                'cbjs_action': '''
                var el = bvr.src_el.getElement(".spt_text_input");
                el.setStyle("width", "230px");
                el.focus();
                el.select();
                '''})

            if simple_search_mode != 'inline':
                keyword_div.add_relay_behavior( {
                    'type': 'click',
                    'bvr_match_class': 'spt_search_toggle',
                    'cbjs_action': '''
                    var top = bvr.src_el.getParent(".spt_view_panel_top");
                    if (top) {
                        var pos = bvr.src_el.getPosition(top);
                        pos.y += 35;
                        spt.simple_search.set_position(pos);
                        spt.simple_search.show_all_elements();
                        spt.simple_search.show_title();
                        spt.simple_search.show();
                    }

                   

                    '''
                } )


        else:
            keyword_div = None


        # -- Button Rows
        button_row_wdg = self.get_button_row_wdg()


        # -- ITEM COUNT DISPLAY
        # add number found
        if self.show_search_limit:
            
            # -- SEARCH LIMIT DISPLAY
            if self.items_found == 0:
                try:
                    if self.search:
                        
                        self.items_found = self.search.get_count()
                    elif self.sobjects:
                        self.items_found = len(self.sobjects)
                except SqlException:
                    DbContainer.abort_thread_sql()

                    self.items_found = 0

            if self.items_found == 1:
                title = "%s %s" % (self.items_found, _("item found"))
            else:
                title = "%s %s" % (self.items_found, _("items found"))
           
            
            num_div = ActionButtonWdg(title=title, btn_class='btn dropdown-toggle')
            num_div.add_class("spt_search_limit_activator")
            
            #HACK
            num_div.add_style("height", "32px")

            from tactic.ui.container import DialogWdg
            dialog = DialogWdg()
            dialog.set_as_activator(num_div.get_button_wdg(), offset={'x':0,'y': 0})
            dialog.set_as_activator(num_div.get_collapsible_wdg(), offset={'x':0,'y': 0})
            dialog.add_title("Search Range")
            
            limit_div = DivWdg()
            limit_div.add_class("spt_table_search")
            limit_div.add_class("spt_table_search_limit")
            limit_div.add(self.search_limit)
            dialog.add(limit_div)
        
        else:
            num_div = None




        search_button_row = self.get_search_button_row_wdg()
        save_button = self.get_save_button()
        layout_wdg = None
        column_wdg = None
        
        show_column_wdg = self.get_setting("column_manager")
        show_layout_wdg = self.get_setting('layout_switcher')
        
        if show_column_wdg and self.can_add_columns():
            column_wdg = self.get_column_manager_wdg()
        if show_layout_wdg:
            layout_wdg = self.get_layout_wdg()


        show_expand = self.get_setting("expand")

        if not self.can_expand():
            show_expand = False
        # DISABLE as it doesn't make any sense any more
        show_expand = False
 
        expand_wdg = None
        if show_expand:
            button = ButtonNewWdg(title='Expand Table', icon='FA_ARROWS_H', show_menu=False, is_disabled=False)
            
            expand_behavior = self.get_expand_behavior()
            if expand_behavior:
                button.add_behavior( expand_behavior )
            else:
                button.add_behavior( {
                'type': 'click_up',
                'cbjs_action': '''
                var layout = bvr.src_el.getParent(".spt_layout");

                spt.table.set_layout(layout);
                spt.table.expand_table();
                return;

                var version = layout.getAttribute("spt_version");
                var headers;
                var table = null;
                var header_table = null;
                if (version == '2') {
                    spt.table.set_layout(layout);
                    table = spt.table.get_table();
                    headers = spt.table.get_headers();
                    header_table = spt.table.get_header_table();

                }
                else {
                    table = spt.get_cousin( bvr.src_el, '.spt_table_top', '.spt_table' );
                    header_table = table;
                    headers = layout.getElements(".spt_table_th");
                }
                var width = table.getStyle("width");
               
                // don't set the width of each column, this is simpler
                if (width == '100%') {
                    if (header_table) {
                        var orig_width = header_table.getAttribute('orig_width');
                        if (orig_width) {
                            header_table.setStyle("width", orig_width);
                            table.setStyle("width", orig_width);
                            layout.setStyle("width", orig_width);

                        } else {
                            header_table.setStyle("width", "");
                            table.setStyle("width", "");
                        }
                    } else 
                        table.setStyle("width", "");
                        
                }
                else {
                    table.setStyle("width", "100%");
                    if (header_table) {
                        header_table.setAttribute("orig_width", header_table.getSize().x);
                        header_table.setStyle("width", "100%");
                    }
                    layout.setStyle("width", "100%");
                }
               
                '''
                } )
            expand_wdg = button

        show_help = self.kwargs.get("show_help")
        if show_help in ["", None]:
            if Project.get().is_admin():
                show_help = True
            else:
                show_help = False


        help_wdg = None

        if show_help not in ['false', False]:
            help_alias = self.get_alias_for_search_type(self.search_type)
            from tactic.ui.app import HelpButtonWdg
            if HelpButtonWdg.exists():
                help_wdg = HelpButtonWdg(alias=help_alias, use_icon=True)
                help_wdg.add_style("margin-top: -2px")

        

        wdg_list = []
        

        badge_view = self.kwargs.get("badge_view")
        if badge_view and badge_view.strip():
            from tactic.ui.panel import CustomLayoutWdg
            widget = CustomLayoutWdg(view=badge_view, panel_kwargs=self.kwargs)
            if widget:
                wdg_list.append( { 'wdg': widget } )
            else:
                print("WARNING: badge view '%s' not defined" % badge_view)
 

        if keyword_div:
            wdg_list.append( {
                'mobile_display': True,
                'wdg': keyword_div
            } )

       
        if self.get_setting("refresh"):
            if self.get_setting("keyword_search"):
                button_div = ButtonNewWdg(title='Search', icon="FA_REFRESH")
            else:
                button_div = ButtonNewWdg(title='Refresh', icon="FA_SYNC")
               
            self.run_search_bvr = self.kwargs.get('run_search_bvr')
            if self.run_search_bvr:
                button_div.add_behavior(self.run_search_bvr)
            else:
                button_div.add_behavior( {
                'type': 'click_up',
                'cbjs_action':  '''
                var tableTop = bvr.src_el.getParent('.spt_table_top');
                var tableSearch = tableTop.getElement(".spt_table_search");
                var hidden_el = tableSearch.getElement(".spt_text_value");

                var src_el = tableSearch.getElement(".spt_text_input_wdg");
                src_el.setAttribute("spt_input_value", src_el.value);
                hidden_el.setAttribute("spt_input_value", src_el.value);
                hidden_el.value = src_el.value;

                spt.dg_table.search_cbk({}, {src_el: src_el});
                '''
            } )

            wdg_list.append({
                'wdg': button_div,
                'mobile_display': True
            })



        if save_button:
            wdg_list.append( {'wdg': save_button} )


        show_collection_tool = self.kwargs.get("show_collection_tool")

        if show_collection_tool not in ["false", False] and SearchType.column_exists(self.search_type, "_is_collection"):
            from .collection_wdg import CollectionAddWdg
            collection_div = CollectionAddWdg(search_type=self.search_type, parent_key=self.parent_key)
            wdg_list.append( {'wdg': collection_div} )
        

        if button_row_wdg.get_num_buttons() != 0:
            wdg_list.append( { 'wdg': button_row_wdg } )
            
        if self.show_search_limit:
            
            if num_div:
                wdg_list.append( { 'wdg': num_div } )
        else:
            if num_div:
                wdg_list.append( { 'wdg': num_div } )

        if search_button_row:
            wdg_list.append( { 
                'wdg': search_button_row,
                'mobile_display': True
            } )
            if self.filter_num_div:
                wdg_list.append( { 'wdg': self.filter_num_div } )
            
        if column_wdg:
            wdg_list.append( { 'wdg': column_wdg } )

        if layout_wdg:
            wdg_list.append( { 'wdg': layout_wdg} )

        if expand_wdg:
            wdg_list.append( { 'wdg': expand_wdg } )


        show_quick_add = self.kwargs.get("show_quick_add")
        if show_quick_add in ['true',True]:
            quick_add_button_row = self.get_quick_add_wdg()
            wdg_list.append( { 'wdg': quick_add_button_row } )


        # add the help widget
        if help_wdg:
            wdg_list.append( { 'wdg': help_wdg } )


        shelf_wdg = self.get_shelf_wdg()
        if shelf_wdg:
            wdg_list.append( { 'wdg': shelf_wdg } )


        # add a custom layout widget
        custom_shelf_view = self.kwargs.get("shelf_view")
        if custom_shelf_view and custom_shelf_view.strip():
            from tactic.ui.panel import CustomLayoutWdg
            widget = CustomLayoutWdg(view=custom_shelf_view, panel_kwargs=self.kwargs)
            if widget:
                wdg_list.append( { 'wdg': widget } )
            else:
                print("WARNING: shelf view '%s' not defined" % custom_shelf_view)

        custom_shelf_view = "_layout_shelf"
        if custom_shelf_view:
            config = WidgetConfigView.get_by_search_type(self.search_type, custom_shelf_view)
            if config:
                element_names = config.get_element_names()
                if element_names:
                    widget = config.get_display_widget(element_names[0])
                    wdg_list.append( { 'wdg': widget } )
                else:
                    print("WARNING: shelf view '%s' not defined" % custom_shelf_view)
 



        
        xx = DivWdg()
        xx.add_class("navbar") 
        xx.add_class("spt_base_table_action_wdg")

        xx.add_style("flex-wrap: nowrap")
        xx.add_style("box-shadow: none")
        xx.add_style("width: 100%")
        xx.add_style("box-sizing: border-box")
        xx.add_style("z-index: 2")

        left_div = DivWdg()
        left_div.add_class("d-flex")

        from tactic.ui.widget import BootstrapButtonRowWdg
        collapse_div = BootstrapButtonRowWdg() 

        last_widget = None
        for item in wdg_list:
            widget = item.get('wdg')

            if item.get("mobile_display") == True:
                left_div.add(widget)
            else:
                collapse_div.add(widget)
            
            last_widget = widget
        
        xx.add(left_div)
        xx.add(collapse_div)
        div.add(xx)

        if self.kwargs.get("__hidden__"):
            scale = 0.8
        else:
            scale = 1


        outer = DivWdg()

        # Different browsers seem to have a lot of trouble with this
        web = WebContainer.get_web()
        browser = web.get_browser()
        import os
        if browser == 'Qt' and os.name != 'nt':
            height = "38px"
        elif scale != 1:
            #xx.add_style("position: absolute")
            xx.add_color("backgroud","background")
            xx.set_scale(scale)
            xx.add_style("float: left")
            xx.add_style("margin-left: -25")
            xx.add_style("margin-top: -5")


        outer.add(div)
        if self.show_search_limit:
            outer.add(dialog)
        if self.view_save_dialog:
            outer.add(self.view_save_dialog)

        outer.add_style("white-space: nowrap")
        
        return outer




    def get_title_wdg(self):

        title = self.kwargs.get("title")
        description = self.kwargs.get("description")
        title_view = self.kwargs.get("title_view")
        if not title and not description and not title_view:
            return


        title = title.upper()

        title_box_wdg = DivWdg()
        title_box_wdg.add_style("padding: 0px 6px 0px 10px")
        title_box_wdg.add_style("box-sizing: border-box")

        title_box_wdg.add_style("float: left")


        if title_view:
            from .custom_layout_wdg import CustomLayoutWdg
            title_wdg = CustomLayoutWdg(view=title_view)
            title_box_wdg.add(title_wdg)


        if title:
            title_wdg = DivWdg()
            title_box_wdg.add(title_wdg)
            title_wdg.add(title)
            title_wdg.add_style("font-size: 1.2em")
            title_wdg.add_style("font-weight: bold")

        if description:
            title_box_wdg.add("<br/>")
            title_box_wdg.add(description)
            title_box_wdg.add("<br/>")

        return title_box_wdg



    def get_shelf_wdg(self):
        return None



    def get_save_button(self, mode="icon"):
        show_save = self.get_setting("save")

        if self.edit_permission == False or not self.view_editable:
            show_save = False

        if not self.can_save():
            show_save = False

        if not show_save:
            return

        # Save button
        if mode == "icon":
            save_button = ButtonNewWdg(title='Save', icon="FA_SAVE", show_menu=False, show_arrow=False)
        else:
            save_button = ActionButtonWdg(title='Save', show_menu=False, show_arrow=False)
            #save_button_top.add_class("btn-primary")

        save_button.add_class("spt_save_button")

        # it needs to be called save_button_top for the button to re-appear after its dissapeared

        save_button.add_style("margin-left: 10px")

        
        save_button.add_behavior({
        'type': 'click_up',
        'update_current_only': True,
        'cbjs_action': '''
        var top = bvr.src_el.getParent(".spt_layout");
        var version = top.getAttribute("spt_version");
        if (version == "2") {
            var dummy = top.getElement('.spt_button_row');
            if (dummy) dummy.focus();

            spt.table.set_layout(top);
            spt.table.save_changes();
        }
        else {
            spt.dg_table.update_row(evt, bvr)
        }
        var save_button = bvr.src_el.getElement(".spt_save_button");
        if (save_button) {
            save_button.setStyle("display", "none");
        }
        ''',
        })

        return save_button






    def get_button_row_wdg(self):
        '''draws the button row in the shelf'''
        from tactic.ui.widget.button_new_wdg import ButtonRowWdg

        button_row_wdg = ButtonRowWdg(show_title=True)

        # add an item button
        show_insert = self.get_show_insert()
        if show_insert:
            insert_view = self.kwargs.get("insert_view")
            if not insert_view or insert_view == 'None':
                insert_view = "insert"

            search_type_obj = SearchType.get(self.search_type)
            search_type_title = search_type_obj.get_value("title")

            button = ButtonNewWdg(title='Add New Item', icon="FA_PLUS")

            button_row_wdg.add(button)
            button.add_behavior( {
                'type': 'click_up',
                'view': insert_view,
                'title': search_type_title,
                'parent_key': self.parent_key,
                'table_id': self.table_id,
                #'cbjs_action': "spt.dg_table.add_item_cbk(evt, bvr)"
                'cbjs_action': '''
                var top = bvr.src_el.getParent(".spt_table_top");
                var table = top.getElement(".spt_table");
                var search_type = top.getAttribute("spt_search_type");

                // NOTE: not sure if this condition is good enough to
                // separate a custom view from an insert view
                if (bvr.view && bvr.view.contains(".")) {
                    var class_name = 'tactic.ui.panel.CustomLayoutWdg';
                }
                else {
                    var class_name = 'tactic.ui.panel.EditWdg';
                }

                var kwargs = {
                  search_type: search_type,
                  parent_key: bvr.parent_key,
                  view: bvr.view,
                  mode: 'insert',
                  //num_columns: 2,
                  save_event: 'search_table_' + bvr.table_id,
                  show_header: false,
                };
                spt.panel.load_popup('Add new ' + bvr.title, class_name, kwargs);
                '''

            } )



            if self.can_inline_insert():
                button.add_behavior( {
                    'type': 'click_up',
                    'modkeys': 'SHIFT',
                    'cbjs_action': '''

                    //bvr.src_el.click();

                    var top = bvr.src_el.getParent(".spt_layout");
                    var version = top.getAttribute("spt_version");
                    if (version == "2") {
                        spt.table.set_layout(top);
                        spt.table.add_new_item();
                    }
                    else {
                        spt.dg_table.add_item_cbk(evt, bvr)
                    }
                    '''
                } )

            else:
                button.add_behavior( {
                    'type': 'click_up',
                    'modkeys': 'SHIFT',
                    'view': insert_view,
                    'table_id': self.table_id,
                    #'cbjs_action': "spt.dg_table.add_item_cbk(evt, bvr)"
                    'cbjs_action': '''
                    var top = bvr.src_el.getParent(".spt_table_top");
                    var table = top.getElement(".spt_table");
                    var search_type = top.getAttribute("spt_search_type")
                    var kwargs = {
                      search_type: search_type,
                      parent_key: '%s',
                      view: bvr.view,
                      mode: 'insert',
                      //num_columns: 2,
                      save_event: 'search_table_' + bvr.table_id
                     
                    };
                    spt.panel.load_popup('Add Single Item', 'tactic.ui.panel.EditWdg', kwargs);
                    '''%self.parent_key
                } )




            button.set_show_arrow_menu(True)
            menu = Menu(width=180)
            menu_item = MenuItem(type='title', label='Actions')
            menu.add(menu_item)

            if self.can_inline_insert():
                menu_item = MenuItem(type='action', label='Add New Item (in Page)')
                menu_item.add_behavior( {
                    'cbjs_action': '''
                    var activator = spt.smenu.get_activator(bvr);
                    var top = activator.getParent(".spt_layout");
                    var version = top.getAttribute("spt_version");
                    if (version == "2") {
                        spt.table.set_layout(top);
                        spt.table.add_new_item();
                    }
                    else {
                        var new_bvr = {
                            src_el: activator
                        }
                        spt.dg_table.add_item_cbk(evt, new_bvr);
                    }
                    '''
                } )
                menu.add(menu_item)

            menu_item = MenuItem(type='action', label='Add New Item (Form)')
            menu_item.add_behavior( {
                'event_name': 'search_table_%s' % self.table_id,
                'cbjs_action': '''
                    var activator = spt.smenu.get_activator(bvr);
                    var top = activator.getParent(".spt_table_top");
                    var table = top.getElement(".spt_table");
                    var search_type = top.getAttribute("spt_search_type")
                    kwargs = {
                      search_type: search_type,
                      parent_key: '%s',
                      mode: 'insert',
                      view: '%s',
                      save_event: bvr.event_name,
                    };
                    spt.panel.load_popup('Single-Insert', 'tactic.ui.panel.EditWdg', kwargs);
                '''%(self.parent_key, insert_view)
            } )

            menu.add(menu_item)
            #menu_item = MenuItem(type='separator')
            #menu.add(menu_item)
            menu_item = MenuItem(type='action', label='Add Multiple Items')
            menu_item.add_behavior( {
                'event_name': 'search_table_%s' % self.table_id,
                'cbjs_action': '''
                    var activator = spt.smenu.get_activator(bvr);
                    var top = activator.getParent(".spt_table_top");
                    var table = top.getElement(".spt_table");
                    var search_type = top.getAttribute("spt_search_type")
                    var kwargs = {
                      search_type: search_type,
                      parent_key: '%s',
                      mode: 'insert',
                      single: 'false',
                      view: '%s',
                      save_event: bvr.event_name
                    };
                    spt.panel.load_popup('Multi-Insert', 'tactic.ui.panel.EditWdg', kwargs);
                '''%(self.parent_key, insert_view)
            } )
            menu.add(menu_item)


            # collection
            if SearchType.column_exists(self.search_type, "_is_collection"):
                menu_item = MenuItem(type='action', label='Add New Collection')
                menu_item.add_behavior( {
                    'cbjs_action': '''
                        var activator = spt.smenu.get_activator(bvr);
                        var top = activator.getParent(".spt_table_top");
                        var table = top.getElement(".spt_table");
                        var search_type = top.getAttribute("spt_search_type")
                        kwargs = {
                          search_type: search_type,
                          parent_key: '%s',
                          mode: 'insert',
                          view: '%s',
                          save_event: bvr.event_name,
                          show_header: false,
                          default: {
                            _is_collection: true
                          }
                        };
                        spt.panel.load_popup('Add New Collection', 'tactic.ui.panel.EditWdg', kwargs);
                    ''' % (self.parent_key, insert_view)

                } )
                menu.add(menu_item)





            menu_item = MenuItem(type='action', label='Edit Multiple Items (NA)')
            menu_item.add_behavior( {
                'cbjs_action': '''
                alert('Not implemented')
                '''
            } )
            #menu.add(menu_item)
            #menu_item = MenuItem(type='separator')
            #menu.add(menu_item)
 


            menus = [menu.get_data()]
            SmartMenu.add_smart_menu_set( button.get_arrow_wdg(), { 'DG_BUTTON_CTX': menus } )
            SmartMenu.assign_as_local_activator( button.get_arrow_wdg(), "DG_BUTTON_CTX", True )

        # NOTE: Changed to a button 
        #if show_save:
        if False:

            # Save button
            #save_button = ButtonNewWdg(title='Save Current Table', icon=IconWdg.SAVE_GRAY, is_disabled=False)
            save_button = ButtonNewWdg(title='Save Current Table', icon="FA_SAVE", is_disabled=False)
            save_button_top = save_button.get_top()
            save_button_top.add_style("display", "none")
            save_button_top.add_class("spt_save_button")

            
            save_button.add_behavior({
            'type': 'click_up',
            'update_current_only': True,
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_layout");
            var version = top.getAttribute("spt_version");
            if (version == "2") {
                var dummy = top.getElement('.spt_button_row');
                if (dummy) dummy.focus();

                spt.table.set_layout(top);
                spt.table.save_changes();
            }
            else {
                spt.dg_table.update_row(evt, bvr)
            }
            ''',
            })


            button_row_wdg.add(save_button)


        
        



        if self.can_use_gear() and self.get_setting("gear"):
            button = ButtonNewWdg(title='More Options', icon="FA_COG")
            button_row_wdg.add(button)

            smenu_set = SmartMenu.add_smart_menu_set( button.get_button_wdg(), { 'BUTTON_MENU': self.gear_menus } )
            SmartMenu.assign_as_local_activator( button.get_button_wdg(), "BUTTON_MENU", True )
            
            smenu_set = SmartMenu.add_smart_menu_set( button.get_collapsible_wdg(), { 'BUTTON_MENU': self.gear_menus } )
            SmartMenu.assign_as_local_activator( button.get_collapsible_wdg(), "BUTTON_MENU", True )
      

        return button_row_wdg




    def get_search_button_row_wdg(self):
        from tactic.ui.widget.button_new_wdg import ButtonRowWdg, SingleButtonWdg

        self.filter_num_div = None
        # Search button
        search_dialog_id = self.kwargs.get("search_dialog_id")

        show_search = None
        show_search1 = self.get_setting("search")
        show_search2 = self.get_setting("show_search")
        if show_search1 or show_search2:
            show_search = True

        if show_search is None:
            # advanced_search is deprecated as of 4.7 (use "search")
            show_search = self.get_setting("advanced_search")

        if show_search and search_dialog_id:
            
            if self.search_wdg:
                num_filters = self.search_wdg.get_num_filters_enabled()
            else:
                num_filters = 0
            
            if num_filters > 0:
                title = "%s filters" % num_filters
            else:
                title = "View Advanced Search"
            
            div = DivWdg()
            self.table.add_attr("spt_search_dialog_id", search_dialog_id)
            button = ButtonNewWdg(title=title, icon="FA_SEARCH", show_menu=False, show_arrow=False)
            button.add_class("spt_table_search_button")
            div.add(button)
            
            if num_filters > 0:
                button.add_class("text-primary")



            button.add_behavior( {
                'type': 'click',
                'dialog_id': search_dialog_id,
                'cbjs_action': '''
                var dialog = document.id(bvr.dialog_id);
                if (!dialog) {
                    return;
                }

                var offset = bvr.src_el.getPosition();
                var size = bvr.src_el.getSize();
                offset = {x:offset.x-265, y:offset.y+size.y+5};

                var body = document.id(document.body);
                var scroll_top = body.scrollTop;
                var scroll_left = body.scrollLeft;
                offset.y = offset.y - scroll_top;
                offset.x = offset.x - scroll_left;

                // correct viewport left and top clipping
                var rect = body.getBoundingClientRect();
                var pointer = dialog.getElement(".spt_popup_pointer");
                var left = offset.x + rect.x;
                if (left < 8) {
                    offset.x = offset.x - left + 8;
                    if (pointer) {
                        pointer.hide();
                    }
                }

                var top = offset.y + rect.y;
                if (top < 0) {
                    offset.y = offset.y - top;
                    if (pointer) {
                        pointer.hide();
                    }
                }

                dialog.position({position: 'upperleft', relativeTo: body, offset: offset});

                spt.toggle_show_hide(dialog);

                if (spt.is_shown(dialog))
                    spt.body.add_focus_element(dialog);

                '''
            } )


            return button
        else:
            return None




    def get_layout_wdg(self):

        layout = ButtonNewWdg(title='Switch Layout', icon="FA_TABLE")
        custom_views = self.kwargs.get("layout_switcher_custom_views") or None
        default_views = self.kwargs.get("default_views") or None
        view = self.view


        if isinstance(custom_views, basestring):
            custom_views = jsonloads(custom_views)
        
        if isinstance(custom_views, dict):
            if view not in custom_views.keys():
                for key, val in custom_views.items():
                    if view in val:
                        view = val[0]
                        break
                
        button_wdg = layout.get_button_wdg()
        collapsible_wdg = layout.get_collapsible_wdg()

        SwitchLayoutMenu(search_type=self.search_type, view=view, custom_views=custom_views, default_views=default_views, activator=button_wdg)

        SwitchLayoutMenu(search_type=self.search_type, view=view, custom_views=custom_views, default_views=default_views, activator=collapsible_wdg)
        return layout



    def get_quick_add_wdg(self):
        from tactic.ui.widget.button_new_wdg import ButtonRowWdg

        button_row = ButtonRowWdg()

        button = ButtonNewWdg(title='Toggle Tasks', icon=IconWdg.EDIT)
        button_row.add(button)
        button.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            spt.app_busy.show("Adding Tasks column to table");
            var layout = bvr.src_el.getParent(".spt_layout");
            var table = layout.getElement(".spt_table");
            var version = layout.getAttribute("spt_version");
            if (version == "2") {
                spt.table.set_table(table);
                spt.table.add_columns(["task_edit", "task_status_edit"]);
            } 
            else {
                spt.dg_table.toggle_column_cbk(table,'task_status_edit','1');
            }
            spt.app_busy.hide();
            '''
        } )




        button = ButtonNewWdg(title='Toggle Notes', icon=IconWdg.NOTE)
        button_row.add(button)
        button.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            spt.app_busy.show("Adding Tasks column to table");
            var layout = bvr.src_el.getParent(".spt_layout");
            var table = layout.getElement(".spt_table");
            var version = layout.getAttribute("spt_version");
            if (version == "2") {
                spt.table.set_table(table);
                spt.table.add_columns(["notes"]);
            } 
            else {
                spt.dg_table.toggle_column_cbk(table,'notes','1');
            }
            spt.app_busy.hide();
            '''
        } )


        button = ButtonNewWdg(title='Toggle Check-in', icon=IconWdg.PUBLISH)
        button_row.add(button)
        button.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            spt.app_busy.show("Adding Tasks column to table");
            var layout = bvr.src_el.getParent(".spt_layout");
            var table = layout.getElement(".spt_table");
            var version = layout.getAttribute("spt_version");
            if (version == "2") {
                spt.table.set_table(table);
                spt.table.add_columns(["file_list","history","general_checkin"]);
            } 
            else {
                spt.dg_table.toggle_column_cbk(table,'general_checkin','1');
            }
            spt.app_busy.hide();
            '''
        } )


        return button_row





    def get_column_manager_wdg(self):

        security = Environment.get_security()
        project_code = Project.get_project_code()

        access_keys = self._get_access_keys("view_column_manager",  project_code)

        if not security.check_access("builtin", access_keys, "allow"):
            return None

        from tactic.ui.widget.button_new_wdg import SingleButtonWdg

        #button = ButtonNewWdg(title='Column Manager', icon=IconWdg.COLUMNS, show_arrow=False)
        button = ButtonNewWdg(title='Column Manager', icon="FA_COLUMNS", show_arrow=False)

        search_type_obj = SearchType.get(self.search_type)


        extra_element_names = self.kwargs.get("extra_element_names") or []
        if isinstance(extra_element_names, basestring):
            extra_element_names = extra_element_names.split(",")

        button.add_behavior( {
            'type': 'click_up',
            'class_name': 'tactic.ui.panel.AddPredefinedColumnWdg',
            "args": {
                'title': 'Column Manager',
                'search_type': self.search_type,
                'extra_element_names': extra_element_names,
            },
            'cbjs_action': '''
                var table = bvr.src_el.getParent('.spt_table');
                var panel = bvr.src_el.getParent('.spt_panel');
                bvr.args.target_id = panel.getAttribute('id');

                var layout = bvr.src_el.getParent(".spt_layout");
                var element_names;
                if (layout.getAttribute("spt_version") == "2") {
                    spt.table.set_layout(layout);
                    element_names = spt.table.get_element_names();
                }
                else {
                    element_names = spt.dg_table.get_element_names(table); 
                }
                bvr.args.element_names = element_names;

                var popup = spt.panel.load_popup(bvr.args.title, bvr.class_name, bvr.args);
                popup.activator = bvr.src_el;
                popup.panel = panel;
                ''',
            } )

        #return div
        return button



    def get_group_wdg(self):

        from tactic.ui.filter import FilterData
        filter_data = FilterData.get_from_cgi()
        values_list = filter_data.get_values_by_prefix("group")
        if values_list:
            values = values_list[0]
        else:
            values = {}

        group_div = SpanWdg()
        group_div.add_class("spt_search_filter")

        hidden = HiddenWdg("prefix", "group")
        group_div.add(hidden)

        # add a grouping element
        group_input = HiddenWdg("group")
        group_input.add_class("spt_search_group")
        if self.group_element:
            group_input.set_value(self.group_element)

        group_interval_input = HiddenWdg("interval")
        group_interval_input.add_class("spt_search_group_interval")
        interval_value = values.get('interval')
        if interval_value:
            group_interval_input.set_value(interval_value)
            
        group_div.add(group_input)
        group_div.add(group_interval_input)
        
        # add an order by element
        order_input = HiddenWdg("order")
        order_input.add_class("spt_search_order")
        if self.order_element:
            order_input.set_value(self.order_element)
        group_div.add(order_input)

        show_retired_input = HiddenWdg("show_retired")
        show_retired_input.add_class("spt_search_show_retired")
        if self.show_retired_element:
            show_retired_input.set_value(self.show_retired_element)
        group_div.add(show_retired_input)


        return group_div




    def get_smart_header_context_menu_data(self):

        menu_data = []

        menu_data.append( {
            "type": "title", "label": '"{element_name}" Column'
        } )

        # Order By (Ascending) menu item ...
        menu_data.append( {
            "type": "action",
            "label": '{sort_prefix} Order By (Ascending)',
            "enabled_check_setup_key" : "is_sortable",
            "bvr_cb": {
                'cbjs_action':
                    '''
                    var activator = spt.smenu.get_activator(bvr);
                    var search_order_el = activator.getParent(".spt_table_top").getElement(".spt_search_order");
                    order_by = activator.getProperty("spt_order_by");
                    if (!order_by) {
                        order_by = activator.getProperty("spt_element_name");
                    }
                    order_by = order_by + " asc";
                    search_order_el.value = order_by
                    spt.dg_table.search_cbk( {}, {src_el: search_order_el} );
                    '''
            },
            #"hover_bvr_cb": { 'activator_add_looks': 'dg_header_cell_hilite',
            #                  'affect_activator_relatives' : [ 'spt.get_next_same_sibling( @, null )' ] }
        } )

        # Order By (Descending) menu item ...
        menu_data.append( {
            "type": "action",
            "label": "{sort_prefix} Order By (Descending)",
            "enabled_check_setup_key" : "is_sortable",
            "bvr_cb": {
                'cbjs_action':
                '''
                var activator = spt.smenu.get_activator(bvr);
                var search_order_el = activator.getParent(".spt_table_top").getElement(".spt_search_order");
                order_by = activator.getProperty("spt_order_by");
                if (!order_by) {
                    order_by = activator.getProperty("spt_element_name");
                }
                order_by = order_by + " desc";
                search_order_el.value = order_by


                spt.dg_table.search_cbk( {}, {src_el: search_order_el} );
                '''
            },
            #"hover_bvr_cb": { 'activator_add_looks': 'dg_header_cell_hilite',
            #                  'affect_activator_relatives' : [ 'spt.get_next_same_sibling( @, null )' ] }
        } )

        menu_data.append( {
            "type": "separator"
        } )
        
        # Group By menu item ...
        menu_data.append( {
            "type": "action",
            "label": "Group and Order By",
            "enabled_check_setup_key" : "is_groupable|is_sortable",
            "bvr_cb": {
                'cbjs_action':
                '''
                var activator = spt.smenu.get_activator(bvr);

                if( spt.is_TRUE( activator.getProperty("spt_widget_is_groupable") ) ) {
                    var test = activator.getParent(".spt_layout").getElements(".spt_search_group");

                    var search_group_el = activator.getParent(".spt_layout").getElement(".spt_search_group");
                    var group_by = activator.getProperty("spt_element_name");
                    search_group_el.value = group_by;

                    var search_order_el = activator.getParent(".spt_layout").getElement(".spt_search_order");
                    var order_by = activator.getProperty("spt_element_name");
                    search_order_el.value = order_by;


                    var search_group_int_el = activator.getParent(".spt_layout").getElement(".spt_search_group_interval");
                    search_group_int_el.value = '';

                    spt.dg_table.search_cbk( {}, {src_el: search_group_el} );
                }
                '''
            },
        } )
      

        menu_data.append( {
            "type": "action",
            "label": "Group By",
            "enabled_check_setup_key" : "is_groupable",
            "bvr_cb": {
                'cbjs_action':
                '''
                var activator = spt.smenu.get_activator(bvr);

                if( spt.is_TRUE( activator.getProperty("spt_widget_is_groupable") ) ) {

                    var search_group_el = activator.getParent(".spt_layout").getElement(".spt_search_group");
                    var group_by = activator.getProperty("spt_element_name");
                    search_group_el.value = group_by;


                    var search_group_int_el = activator.getParent(".spt_layout").getElement(".spt_search_group_interval");
                    search_group_int_el.value = '';

                    var search_order_el = activator.getParent(".spt_layout").getElement(".spt_search_order");
                    var order_by = search_order_el.value
                    if (!order_by) {
                        search_order_el.value = group_by;
                    }

                    spt.dg_table.search_cbk( {}, {src_el: search_group_el} );
                }
                '''
            },
        } )
 
        # Group By Week Optional menu item ...
        menu_data.append( {
            "type": "action",
            "label": "Group By Week",
            "enabled_check_setup_key" : "is_time_groupable",
            "bvr_cb": {
                'cbjs_action':
                '''
                var activator = spt.smenu.get_activator(bvr);

                if( spt.is_TRUE( activator.getProperty("spt_widget_is_time_groupable") ) ) {

                    var search_group_el = activator.getParent(".spt_layout").getElement(".spt_search_group");
                    var group_by = activator.getProperty("spt_element_name");
                    search_group_el.value = group_by;

                    var search_group_int_el = activator.getParent(".spt_layout").getElement(".spt_search_group_interval");
                    search_group_int_el.value = '%s';

                    spt.dg_table.search_cbk( {}, {src_el: search_group_int_el} );
                }
                '''%BaseTableLayoutWdg.GROUP_WEEKLY
            },
            #"hover_bvr_cb": { 'activator_add_looks': 'dg_header_cell_hilite',
            #                  'affect_activator_relatives' : [ 'spt.get_next_same_sibling( @, null )' ] }
        } )    

        # Group By Week Optional menu item ...
        menu_data.append( {
            "type": "action",
            "label": "Group By Month",
            "enabled_check_setup_key" : "is_time_groupable",
            "bvr_cb": {
                'cbjs_action':
                '''
                var activator = spt.smenu.get_activator(bvr);

                if( spt.is_TRUE( activator.getProperty("spt_widget_is_time_groupable") ) ) {

                    var search_group_el = activator.getParent(".spt_layout").getElement(".spt_search_group");
                    var group_by = activator.getProperty("spt_element_name");
                    search_group_el.value = group_by;

                    var search_group_int_el = activator.getParent(".spt_layout").getElement(".spt_search_group_interval");
                    search_group_int_el.value = '%s';

                    spt.dg_table.search_cbk( {}, {src_el: search_group_int_el} );
                }
                '''%BaseTableLayoutWdg.GROUP_MONTHLY
            },
            #"hover_bvr_cb": { 'activator_add_looks': 'dg_header_cell_hilite',
            #                  'affect_activator_relatives' : [ 'spt.get_next_same_sibling( @, null )' ] }
        } )    

        # Group Advanced menu item ...
        menu_data.append( {
            "type": "action",
            "label": "Group (Advanced)",

            
            "bvr_cb": {
                "args": {
                    'title': 'Group - Advanced',
                    'search_type': self.search_type,
                    'target_id': self.target_id
                },

                'cbjs_action':
                '''
                var activator = spt.smenu.get_activator(bvr);


                    var search_group_el = activator.getParent(".spt_layout").getElement(".spt_search_group");
                    //var group_by = activator.getProperty("spt_element_name");
                    var group_by = search_group_el.value;

                    var activator = spt.smenu.get_activator(bvr);
                    var table = activator.getParent('.spt_table');
                    var panel = activator.getParent('.spt_panel');
                    var layout = activator.getParent('.spt_layout');
                   

                    if (layout.getAttribute("spt_version") == "2") {
                        spt.table.set_layout(layout);
                        element_names = spt.table.get_element_names();
                    }
                    else {
                        element_names = spt.dg_table.get_element_names(table); 
                    }
                    bvr.args.element_names = element_names;
                    
                    bvr.args.group_by = group_by;


                    var class_name = 'tactic.ui.panel.TableGroupManageWdg';
                    var popup = spt.panel.load_popup(bvr.args.title, class_name, bvr.args);
                    popup.activator = activator;
                    popup.panel = panel;
                '''
            },
            #"hover_bvr_cb": { 'activator_add_looks': 'dg_header_cell_hilite',
            #                  'affect_activator_relatives' : [ 'spt.get_next_same_sibling( @, null )' ] }
        } )    
      
        menu_data.append( {
            "type": "separator"
        } )


        # NOTE: This assumes that the way to add an item is to use edit widget.
        # This is not true for pipeline processes, for example.
        menu_data.append( {
        "type": "action",
        "label": "Add New Related Item",
        "enabled_check_setup_key" : "has_related",
        "hide_when_disabled" : True,
        "bvr_cb": {
        'cbjs_action':
        '''
        var activator = spt.smenu.get_activator(bvr);
        var search_type = activator.getProperty("spt_related_type");
        var class_name = "tactic.ui.panel.EditWdg";
        var kwargs = {
            search_type: search_type,
            mode: 'insert',
        };
        spt.panel.load_popup("Add Item", class_name, kwargs);
        ''',
        }
        } )

        menu_data.append( {
        "type": "action",
        "label": "View Related Items",
        "enabled_check_setup_key" : "has_related",
        "hide_when_disabled" : True,
        "bvr_cb": {
        'cbjs_action':
        '''
        var activator = spt.smenu.get_activator(bvr);
        var search_type = activator.getProperty("spt_related_type");
        var class_name = "tactic.ui.panel.TableLayoutWdg";
        var kwargs = {
            search_type: search_type,
            mode: 'table'
        };
        spt.tab.set_main_body_tab();
        spt.tab.add_new("related_items", "Related Items", class_name, kwargs);
        '''
        }
        } )






        # Add column-based search ...
        # DEPRECATED: we used the simple search widget for this
        """
        kwargs = {
            "args": {'use_last_search': True,  
                     'display' : True,
                     'search_type': self.search_type
                    },
            "values": {}
        }
        div = DivWdg()
        widget_key = div.generate_widget_key('tactic.ui.app.LocalSearchWdg', inputs=kwargs)
        menu_data.append( {
            "type": "action",
            "enabled_check_setup_key" : "is_searchable",
            "hide_when_disabled" : True,
            "label": "Local Search",
            "bvr_cb": {
                'cbjs_action': '''
                var activator = spt.smenu.get_activator(bvr);
                bvr.options.title = 'Local Search (' + activator.getProperty("spt_element_name").capitalize() + ')';
                bvr.options.popup_id =  bvr.options.title;
                bvr.args.prefix_namespace = activator.getProperty("spt_display_class");
                bvr.args.searchable_search_type =  activator.getProperty("spt_searchable_search_type");
                spt.popup.get_widget(evt, bvr);
                ''',
                'options' : {'class_name' : widget_key },
                'args' : {
                    'use_last_search': True,
                    'display' : True,
                    'search_type': self.search_type
                }
            }
        } )
        """
       

        # Edit Column Definition menu item ...
        search_type_obj = SearchType.get(self.search_type)

        security = Environment.get_security()
        if security.check_access("builtin", "view_site_admin", "allow"):
            kwargs = {
                'search_type': self.search_type,
                'element_name': '__WIDGET_UNKNOWN__',
                'view': '__WIDGET_UNKNOWN__'
            }
            div = DivWdg()
            widget_key = div.generate_widget_key('tactic.ui.manager.ElementDefinitionWdg', inputs=kwargs)

            menu_data.append( {
                "type": "action",
                "label": "Edit Column Definition",
                "bvr_cb": {
                    'args' : {'search_type': self.search_type},
                    'options': {
                        'class_name': widget_key,
                        'popup_id': 'edit_column_defn_wdg',
                        'title': 'Edit Column Definition'
                    },
                    'cbjs_action':
                        '''
                        var activator = spt.smenu.get_activator(bvr);
                        bvr.args.element_name = activator.getProperty("spt_element_name");

                        bvr.args.view = activator.getParent('.spt_table').getAttribute('spt_view');
                        var popup = spt.popup.get_widget(evt,bvr);
                        popup.activator = activator;
                        '''
                },
            } )

            """
            menu_data.append( {
                "type": "action",
                "label": "Show Help",
                "bvr_cb": {
                    'cbjs_action':
                        '''
                        var activator = spt.smenu.get_activator(bvr);
                        spt.help.set_top()
                        spt.help.load_alias("calendar-wdg");
                        '''
                } 
            } )
            """


            menu_data.append( {
                "type": "separator"
             } )
            """
            menu_data.append( {
                "type": "action",
                "label": "Edit Column Definition",
                "bvr_cb": {
                    'args' : {'search_type': search_type_obj.get_base_key()},
                    'options': {
                        'class_name': 'tactic.ui.panel.EditColumnDefinitionWdg',
                        
                        'popup_id': 'edit_column_defn_wdg',
                        'title': 'Edit Column Definition'
                    },
                    'cbjs_action':
                        '''
                        var activator = spt.smenu.get_activator(bvr);
                        bvr.args.element_name = activator.getProperty("spt_element_name");
                        bvr.args.view = spt.smenu.get_activator(bvr).getParent('.spt_table').getAttribute('spt_view');
                        var popup = spt.popup.get_widget(evt,bvr);
                        popup.activator = activator;
                        '''
                },
                #"hover_bvr_cb": { 'activator_add_looks': 'dg_header_cell_hilite',
                #                  'affect_activator_relatives' : [ 'spt.get_next_same_sibling( @, null )' ] }
            } )
            """

        
        # Remove Column menu item ...
        menu_data.append( {
            "type": "action",
            "label": "Remove Column",
            "bvr_cb": {
                'options': {},  # need to have the options hash available, but it's key/values are added dynamically
                'cbjs_action':
                    '''
                    var activator = spt.smenu.get_activator(bvr);

                    var layout = activator.getParent(".spt_layout");
                    var version = layout.getAttribute("spt_version");
                    if (version == "2") {
                        var element_name = activator.getProperty("spt_element_name");
                        spt.table.set_layout(layout);
                        spt.table.remove_column(element_name);
                    }
                    else {
                        bvr.options.element_name = activator.getProperty("spt_element_name");
                        bvr.options.element_idx = parseInt(activator.getProperty("col_idx")) / 2;
                        spt.dg_table.remove_column_cbk(evt,bvr);
                    }


                    '''
            },
            #"hover_bvr_cb": { 'activator_add_looks': 'dg_header_cell_hilite',
            #                  'affect_activator_relatives' : [ 'spt.get_next_same_sibling( @, null )' ] }
        } )
        
       
      

        menu_data.append( {
            "type": "title", "label": "Table Columns &amp; Contents"
        } )
        project_code = Project.get_project_code()

        access_keys = self._get_access_keys("view_column_manager",  project_code)
        # Column Manager menu item ...
        if security.check_access("builtin", access_keys, "allow"):
            menu_data.append( {
            "type": "action",
            "label": "Column Manager",
            "bvr_cb": {
                "args": {
                    'title': 'Column Manager',
                    'search_type': self.search_type,
                    'target_id': self.target_id
                },
                'cbjs_action': '''
                    var activator = spt.smenu.get_activator(bvr);
                    var table = activator.getParent('.spt_table');
                    var panel = activator.getParent('.spt_panel');
                    var layout = activator.getParent('.spt_layout');
                    bvr.args.target_id = panel.getAttribute('id');

                    if (layout.getAttribute("spt_version") == "2") {
                        spt.table.set_layout(layout);
                        element_names = spt.table.get_element_names();
                    }
                    else {
                        element_names = spt.dg_table.get_element_names(table); 
                    }
                    bvr.args.element_names = element_names;

                    var class_name = 'tactic.ui.panel.AddPredefinedColumnWdg';
                    var popup = spt.panel.load_popup(bvr.args.title, class_name, bvr.args);
                    popup.activator = activator;
                    popup.panel = panel;
                    ''',
                }
            } )


            menu_data.append( {
                "type": "action",
                "label": "Create New Column",
                "bvr_cb": {
                    #'args' : {'search_type': search_type_obj.get_base_key()},
                    'args' : {'search_type': self.search_type},
                    'options': {
                        'class_name': 'tactic.ui.manager.ElementDefinitionWdg',
                        'popup_id': 'edit_column_defn_wdg',
                        'title': 'Create New Column'
                    },
                    'cbjs_action':
                        '''
                        var activator = spt.smenu.get_activator(bvr);
                        bvr.args.element_name = activator.getProperty("spt_element_name");
                        bvr.args.view = spt.smenu.get_activator(bvr).getParent('.spt_table').getAttribute('spt_view');
                        bvr.args.is_insert = true;
                        var popup = spt.popup.get_widget(evt,bvr);
                        popup.activator = activator;
                        '''
                },
                #"hover_bvr_cb": { 'activator_add_looks': 'dg_header_cell_hilite',
                #                  'affect_activator_relatives' : [ 'spt.get_next_same_sibling( @, null )' ] }
            } )


            menu_data.append( {
                "type": "separator"
            } )

        

        group_columns = self.kwargs.get("group_elements")
        
        # Remove Grouping menu item ...
        menu_data.append( {
            "type": "action",
            "label": "Remove Grouping",
            "bvr_cb": {
                "group_elements": group_columns,
                'cbjs_action':
                    '''
                    if (bvr.group_elements) {
                        spt.info('[' + bvr.group_elements +  '] has been defined for this view for grouping. Only user-controlled grouping is removed. ');
                    }
                    var activator = spt.smenu.get_activator(bvr);
                    var el = activator.getParent(".spt_layout").getElement(".spt_search_group");
                    el.value = "";
                    spt.dg_table.search_cbk( {}, {src_el:el} );
                    '''
            }
        } )

        # Show Retired menu item ...
        menu_data.append( {
            "type": "action",
            "label": "Show Retired",
            "bvr_cb": {
                'cbjs_action':
                    '''
                    var activator = spt.smenu.get_activator(bvr);
                    var el = activator.getParent(".spt_layout").getElement(".spt_search_show_retired");
                    el.value = "true";
                    spt.dg_table.search_cbk( {}, {src_el:el} );
                    '''
            }
        } )

        # Hide Retired menu item ...
        menu_data.append( {
            "type": "action",
            "label": "Hide Retired",
            "bvr_cb": {
                'cbjs_action':
                    '''
                    var activator = spt.smenu.get_activator(bvr);
                    var el = activator.getParent(".spt_layout").getElement(".spt_search_show_retired");
                    el.value = "";
                    spt.dg_table.search_cbk( {}, {src_el:el} )
                    '''
            }
        } )

        
        return { 'menu_tag_suffix': 'MAIN', 'width': 200, 'opt_spec_list': menu_data, 'allow_icons': False,
                 'setup_cbfn':  'spt.smenu_ctx.setup_cbk' }




    def get_data_row_smart_context_menu_details(self):
        security = Environment.get_security()
        project_code = Project.get_project_code()
        spec_list = [ { "type": "title", "label": 'Item "{display_label}"' }]
        if self.view_editable:
            
            access_keys = self._get_access_keys("edit",  project_code)
            if security.check_access("builtin", access_keys, "edit"):

                edit_view = self.kwargs.get("edit_view")
                if not edit_view or edit_view == 'None':
                    edit_view = "edit"
            
                spec_list.append( {
                    "type": "action",
                    "label": "Edit",
                    #"icon": IconWdg.EDIT,
                    "bvr_cb": {
                        'edit_view': edit_view,
                        'cbjs_action': '''
                        var activator = spt.smenu.get_activator(bvr);
                        var layout = activator.getParent(".spt_layout");
                        if (layout.getAttribute("spt_version") == "2") {
                            spt.table.set_layout(layout);
                            spt.table.row_ctx_menu_edit_cbk(evt, bvr);
                        }
                        else {
                            spt.dg_table.drow_smenu_edit_row_context_cbk(evt, bvr);
                        }
                        '''
                    },
                    "hover_bvr_cb": {
                        'activator_add_look_suffix': 'hilite',
                        'target_look_order': [
                            'dg_row_retired_selected', 'dg_row_retired', self.look_row_selected, self.look_row ] 
                        }
                    }
                )

            search_type = self.search_type


            format_context = ProjectSetting.get_value_by_key("checkin/format_context", search_type=search_type)
            if format_context in ['false', "False", False]:
                format_context = 'false'
            else:
                format_context = 'true'


            # get the browser
            web = WebContainer.get_web()
            browser = web.get_browser()
            if browser in ['Qt']:
                use_html5 = False
            else:
                use_html5 = True
            
            div = DivWdg()
            search_api_key = div.generate_api_key("get_by_search_key", inputs=["__API_UNKNOWN__"], attr=False)
            add_api_key = div.generate_api_key("add_file", inputs=["__API_UNKNOWN__", "__API_UNKNOWN__", {"file_type": 'icon', "mode": 'upload', "create_icon": 'True'}], attr=False)
            checkin_api_key = div.generate_api_key("simple_checkin", inputs=["__API_UNKNOWN__", "__API_UNKNOWN__", "__API_UNKNOWN__", {"mode": 'uploaded', 'use_handoff_dir': False, 'checkin_type': 'auto'}], attr=False)
            
            if not use_html5:
                
                bvr_cb = {
                'cbjs_action': r'''

                    var format_context = %s;

                    var activator = spt.smenu.get_activator(bvr);
                    var layout = activator.getParent(".spt_layout");
                    var version = layout.getAttribute("spt_version");

                    var search_key;

                    var tbody;
                    if (version == "2") {
                        spt.table.set_layout(layout);
                        tbody = activator;
                    }
                    else {
                        tbody = activator.getParent('.spt_table_tbody');
                    }
                    
                    search_key = tbody.getAttribute("spt_search_key");
                    
                    var context = bvr.context;
                    if (!context)
                        context = tbody.getAttribute("spt_icon_context");
                    if (!context)
                        context = "icon";


                    var applet = spt.Applet.get();
                    var files = applet.open_file_browser();

                    if (files.length == 0) {
                        spt.alert("Please select a valid image file.");
                        spt.app_busy.hide();
                        return;
                    }

                    var file = files[0];

                    if (file.test(/,/)) {
                        spt.alert('Comma , is not allowed in file name.');
                        spt.app_busy.hide();
                        return;
                    }
                    else if (!file) {
                        spt.alert('A file must be selected.');
                        spt.app_busy.hide();
                        return;
                    }
                    spt.app_busy.show("Uploading preview image ...", file);


                    var server = TacticServerStub.get();
                    try {
                        spt.app_busy.show(bvr.description, file);
                        var search_api_key = '%s';
                        server.set_api_key(search_api_key);
                        var snapshot = server.get_by_search_key(search_key);
                        server.clear_api_key();
                        var snapshot_code = snapshot.code;
                        if (search_key.search('sthpw/snapshot')!= -1){
                            var kwargs = {file_type:'icon', mode: 'upload', create_icon: 'True'};
                            var add_api_key = '%s';
                            server.set_api_key(add_api_key);
                            server.add_file( snapshot_code, file, kwargs );
                            server.clear_api_key();
                        }
                        else {
                            file = file.replace(/\\/g, "/");
                            var parts = file.split("/");
                            var filename = parts[parts.length-1];
                            var kwargs;
                            if (context != "icon") {
                                if (format_context) context = context + "/" + filename;
                                else context = String(context);

                                kwargs = {mode: 'upload', checkin_type: 'auto'};
                            }
                            else {
                                kwargs = {mode: 'upload'};
                            }
                            var checkin_api_key = '%s';
                            server.set_api_key(checkin_api_key);
                            server.simple_checkin( search_key, context, file, kwargs);
                            server.clear_api_key();
                        }
                    } catch(e) {
                        var error_str = spt.exception.handler(e);
                        alert( "Checkin Error: " + error_str );
                    }

                    if (version == "2") {
                        spt.table.refresh_rows([activator]);
                    }

                    var update_event = "update|" + search_key;
                    spt.named_events.fire_event(update_event);
                    spt.app_busy.hide();

                    ''' % (format_context, search_api_key, add_api_key, checkin_api_key)
                }

            else:

                bvr_cb = {
                'cbjs_action': r'''

                    var format_context = %s;

                    var activator = spt.smenu.get_activator(bvr);
                    var layout = activator.getParent(".spt_layout");
                    var version = layout.getAttribute("spt_version");

                    var search_key;

                    var tbody;
                    if (version == "2") {
                        spt.table.set_layout(layout);
                        tbody = activator;
                    }
                    else {
                        tbody = activator.getParent('.spt_table_tbody');
                    }
                    
                    search_key = tbody.getAttribute("spt_search_key");
                     
                    var context = bvr.context;
                    // there are 2 modes: file, icon
                    if (bvr.mode == 'icon') {
                        if (!context)
                            context = tbody.getAttribute("spt_icon_context");
                        if (!context)
                            context = "icon";
                    }
                    // set the form
                    
                    if (!spt.html5upload.form) {
                        spt.html5upload.set_form( document.id(bvr.upload_id) );
                    }
                    spt.html5upload.clear();

                    var server = TacticServerStub.get();
                    // set an action for completion
                    var upload_complete = function() {

                        var file = spt.html5upload.get_file();
                        if (file) {
                            file = file.name;
                        }
                        else {
                            server.abort();
                            spt.alert("File object cannot be found. Exit");
                            spt.app_busy.hide();
                            return;
                        }
                        
                        var has_error = false;

                        try {
                            
                            if (search_key.search('sthpw/snapshot')!= -1){
                                var search_api_key = '%s';
                                server.set_api_key(search_api_key);
                                var snapshot = server.get_by_search_key(search_key);
                                server.clear_api_key();
                                var snapshot_code = snapshot.code;
                                var kwargs = {file_type:'icon', mode: 'uploaded', create_icon: 'True'};
                                var add_api_key = '%s';
                                server.set_api_key(add_api_key);
                                server.add_file( snapshot_code, file, kwargs );
                                server.clear_api_key();
                            }
                            else {

                                file = file.replace(/\\/g, "/");
                                var parts = file.split("/");
                                var filename = parts[parts.length-1];
                                var kwargs;

                                if (spt.get_typeof(bvr.checkin_context)=='array')
                                    bvr.checkin_context= bvr.checkin_context[0];
                                
                                //checkin_context would override the default context
                                if (bvr.checkin_context) 
                                    context = bvr.checkin_context;

                                if (bvr.mode != "icon" && bvr.checkin_type=='auto') {
                                    if (format_context) context = context + "/" + filename;
                                    else context = String(context);
                                    kwargs = {mode: 'uploaded', checkin_type: 'auto'};
                                }
                                else {
                                    kwargs = {mode: 'uploaded'};
                                    
                                }
                                var checkin_api_key = '%s';
                                server.set_api_key(checkin_api_key);
                                server.simple_checkin( search_key, context, file, kwargs);
                                server.clear_api_key();
                            }
                        } catch(e) {
                            var error_str = spt.exception.handler(e);
                            spt.alert( "Checkin Error: " + error_str );
                            has_error = true;
                            server.abort();
                        }


                        spt.html5upload.clear();
                        if (!has_error) {
                            server.finish();
                            if (version == "2") {
                                spt.table.refresh_rows([activator]);
                            }

                            var update_event = "update|" + search_key;
                            spt.named_events.fire_event(update_event);
                            var codes = server.split_search_key(search_key);

                            spt.notify.show_message("Check-in of [" + file + "] finished for [" + codes[1] + "].");
                        }
                        spt.app_busy.hide();

                    }


                    var percent_complete = function(evt) {
                        var percent = Math.round(evt.loaded * 100 / evt.total);

                        var file = spt.html5upload.get_file()
                        var label = file ? (file.name + ": ") : ''

                        spt.app_busy.show("Uploading", label +  percent + "%%");
                    }

                    try {
                       
                        var onchange = function() {
                                
                            server.start({'title':' Check-in', 'description': bvr.description + ' ' + search_key}); 
                            spt.html5upload.events['start'] = true;

                            spt.html5upload.upload_file( {
                              ticket: server.get_transaction_ticket(),
                              upload_complete: upload_complete,
                              upload_progress: percent_complete
                              
                            } );
                        };

                        spt.html5upload.select_file( onchange );
                            

                    }
                    catch(e) {
                        spt.alert("Check-in Failed: "+e);
                        spt.app_busy.hide();
                    }

                    ''' % (format_context, search_api_key, add_api_key, checkin_api_key)

                }

            bvr_cb["description"] = "Checking in preview ..."
            bvr_cb["mode"] = "icon"
            # set a dumself
            if Container.get_dict("JSLibraries", "spt_html5upload"):
                self.upload_id = '0'
            bvr_cb["upload_id"] = self.upload_id
            spec_list.append( {
                "type": "action",
                "label": "Change Preview Image",
                #"icon": IconWdg.PHOTOS,
                "bvr_cb": bvr_cb,
                "hover_bvr_cb": {
                    'activator_add_look_suffix': 'hilite',
                    'target_look_order': [
                        'dg_row_retired_selected', 'dg_row_retired', self.look_row_selected, self.look_row ] 
                    }
            } )

            bvr_cb2 = bvr_cb.copy()
            bvr_cb2["description"] = "Checking in new file ..."
            bvr_cb2["context"] = "publish",
            bvr_cb2["checkin_context"] = self.checkin_context,
            bvr_cb2["mode"] = "file"
            bvr_cb2["checkin_type"] =  self.checkin_type
            spec_list.append( {
                "type": "action",
                "label": "Check in New File",
                "upload_id": self.upload_id,
                "mode": "file",
                "bvr_cb": bvr_cb2,
                "hover_bvr_cb": {
                    'activator_add_look_suffix': 'hilite',
                    'target_look_order': [
                        'dg_row_retired_selected', 'dg_row_retired', self.look_row_selected, self.look_row ] 
                    }
            } )







        
        access_keys = self._get_access_keys("retire_delete",  project_code)
        if security.check_access("builtin", access_keys, "allow") or security.check_access("search_type", self.search_type, "delete"):
        
            spec_list.extend( [{ "type": "separator" },
                
                { "type": "action", "label": "Reactivate", "icon": IconWdg.CREATE,
                    "enabled_check_setup_key" : "is_retired",
                    "hide_when_disabled" : True,
                    "bvr_cb": { 'cbjs_action': 'spt.dg_table.drow_smenu_reactivate_cbk(evt,bvr);' },
                    "hover_bvr_cb": { 'activator_add_look_suffix': 'hilite',
                                      'target_look_order': [ 'dg_row_retired_selected', 'dg_row_retired',
                                                             self.look_row_selected, self.look_row ] }
                },

                { "type": "action", "label": "Retire",
                    #"icon": IconWdg.RETIRE,
                    "enabled_check_setup_key" : "is_not_retired",
                    "hide_when_disabled" : True,
                    "bvr_cb": { 'cbjs_action': 'spt.dg_table.drow_smenu_retire_cbk(evt,bvr);' },
                    "hover_bvr_cb": { 'activator_add_look_suffix': 'hilite',
                                      'target_look_order': [ 'dg_row_retired_selected', 'dg_row_retired',
                                                             self.look_row_selected, self.look_row ] }
                },

                { "type": "action", "label": "Delete",
                    #"icon": IconWdg.DELETE,
                    "bvr_cb": { 'cbjs_action': 'spt.dg_table.drow_smenu_delete_cbk(evt,bvr);' },
                    "hover_bvr_cb": { 'activator_add_look_suffix': 'hilite',
                                      'target_look_order': [ 'dg_row_retired_selected', 'dg_row_retired',
                                                             self.look_row_selected, self.look_row ] }
                }])

        subscribe_label = 'Item'
        if self.search_type in ['sthpw/task','sthpw/note','sthpw/snapshot']:
            subscribe_label = 'Parent'
        elif self.search_type.startswith('sthpw') or self.search_type.startswith('config'): 
            subscribe_label = None
       
        if subscribe_label:
            spec_list.extend( [

                    { "type": "separator" },

                    { "type": "action", "label": "Item Audit Log",
                        #"icon": IconWdg.CONTENTS,
                        "bvr_cb": { 'cbjs_action': "spt.dg_table.drow_smenu_item_audit_log_cbk(evt, bvr);" },
                        "hover_bvr_cb": { 'activator_add_look_suffix': 'hilite',
                                          'target_look_order': [ 'dg_row_retired_selected', 'dg_row_retired',
                                                                 self.look_row_selected, self.look_row ] }
                    },
                    
                    { "type": "action", "label": "Subscribe to %s"%subscribe_label,
                        #"icon": IconWdg.PICTURE_EDIT,
                        "enabled_check_setup_key": "is_not_subscribed",
                        "hide_when_disabled": True,
                        "bvr_cb": { 'cbjs_action': '''
                        var activator = spt.smenu.get_activator(bvr);
                        var layout = activator.getParent(".spt_layout");
                        var version = layout.getAttribute("spt_version");

                        var search_key;

                        var tbody;
                        if (version == "2") {
                            spt.table.set_layout(layout);
                            tbody = activator;
                        }
                        else {
                            tbody = activator.getParent('.spt_table_tbody');
                        }
                        
                        var search_key = tbody.getAttribute("spt_search_key");
                        var server = TacticServerStub.get();
                        // search_key here is "id" based: need code based
                        var sobject = server.get_by_search_key(search_key);
                        var temps = server.split_search_key(search_key);
                        var st = temps[0];
                        
                        if (['sthpw/note','sthpw/snapshot','sthpw/task'].contains(st))
                            search_key = server.build_search_key(sobject.search_type, sobject.search_code);
                        else
                            search_key = sobject.__search_key__;
                       
                        try {
                            var sub = server.subscribe(search_key, {category: "sobject"} );
                            spt.notify.show_message('Subscribed to [' + sub.message_code + ']');
                            spt.table.refresh_rows([activator]);
                        } catch(e) {
                            spt.info(spt.exception.handler(e));
                        }
     
                        ''' },
                        "hover_bvr_cb": { 'activator_add_look_suffix': 'hilite',
                                          'target_look_order': [ 'dg_row_retired_selected', 'dg_row_retired',
                                                                 self.look_row_selected, self.look_row ] }
                    },

                    { "type": "action", "label": "Unsubscribe from %s"%subscribe_label,
                        #"icon": IconWdg.PICTURE_EDIT,
                        "enabled_check_setup_key": "is_subscribed",
                        "hide_when_disabled": True,
                        "bvr_cb": { 'cbjs_action': '''
                        var activator = spt.smenu.get_activator(bvr);
                        var layout = activator.getParent(".spt_layout");
                        var version = layout.getAttribute("spt_version");

                        var search_key;

                        var tbody;
                        if (version == "2") {
                            spt.table.set_layout(layout);
                            tbody = activator;
                        }
                        else {
                            tbody = activator.getParent('.spt_table_tbody');
                        }
                        
                        var search_key = tbody.getAttribute("spt_search_key");
                        var server = TacticServerStub.get();
                        // search_key here is "id" based: need code based
                        var sobject = server.get_by_search_key(search_key);
                        var temps = server.split_search_key(search_key);
                        var st = temps[0];
                        
                        if (['sthpw/note','sthpw/snapshot','sthpw/task'].contains(st))
                            search_key = server.build_search_key(sobject.search_type, sobject.search_code);
                        else
                            search_key = sobject.__search_key__;
                       
                        try {
                            server.unsubscribe(search_key);
                            spt.notify.show_message('Unsubscribed from [' + search_key + ']');
                            spt.table.refresh_rows([activator]);
                        } catch(e) {
                            spt.info(spt.exception.handler(e));
                        }
     
                        ''' },
                        "hover_bvr_cb": { 'activator_add_look_suffix': 'hilite',
                                          'target_look_order': [ 'dg_row_retired_selected', 'dg_row_retired',
                                                                 self.look_row_selected, self.look_row ] }
                    }

                    ])   

        spec_list.extend( [

                { "type": "title", "label": 'All Table Items' },

                { "type": "action", 
                    "label": "Save All Changes",
                    #"icon": IconWdg.DB,
                    "enabled_check_setup_key" : "commit_enabled",
                    "bvr_cb": { 'cbjs_action':
                    '''
                    var activator = spt.smenu.get_activator(bvr);
                    var layout = activator.getParent(".spt_layout");
                   

                    if (layout.getAttribute("spt_version") == "2") {
                        var dummy = layout.getElement('.spt_table_insert_row');
                        if (dummy) dummy.focus();
                        
                        spt.table.row_ctx_menu_save_changes_cbk(evt, bvr);
                    }
                    else {
                        spt.dg_table.drow_smenu_update_row_context_cbk(evt, bvr)
                    }
                    '''
                    }
                }
                ])




        version = self.get_layout_version()

        if version == "2":
            return { 'menu_tag_suffix': 'MAIN', 'width': 200,
                'opt_spec_list' : spec_list,
                'setup_cbfn':  'spt.table.row_ctx_menu_setup_cbk'
            }
        else:
            return { 'menu_tag_suffix': 'MAIN', 'width': 200,
                'opt_spec_list' : spec_list,
                'setup_cbfn':  'spt.dg_table.drow_smenu_setup_cbk'
            }


    def get_default_display_handler(cls, element_name):
        return "tactic.ui.common.SimpleTableElementWdg"
    get_default_display_handler = classmethod(get_default_display_handler)

    def get_layout_version(self):
        return "2"

    def _get_access_keys(self, key, project_code):
        '''get access keys for a builtin rule'''
        access_key1 = {
            'key': key,
            'project': project_code
        }

        access_key2 = {
            'key': key
        }
        access_keys = [access_key1, access_key2]
        return access_keys


    def handle_no_results(self, table):
        ''' This creates an empty html table when the TableLayout has no entries.
        There are two helper functions, add_no_results_bvr and add_no_results_style
        which can be overridden to support custom behaviors and appearances.'''

        no_results_mode = self.kwargs.get('no_results_mode')

        if no_results_mode == 'compact':

            tr, td = table.add_row_cell()
            tr.add_class("spt_table_no_items")
            msg = DivWdg("<i style='font-weight: bold; font-size: 14px'>- No items found -</i>")
            msg.add_style("text-align: center")
            msg.add_style("padding: 5px")
            msg.add_style("opacity: 0.5")
            td.add(msg)
            return

        table.add_style("width: auto")

        tr, td = table.add_row_cell()

        self.add_no_results_bvr(tr)

        tr.add_class("spt_table_no_items")
        td.add_style("border-style: solid")
        td.add_style("border-width: 1px")
        td.add_color("border-color", "table_border", default="border")
        td.add_color("color", "color")
        td.add_color("background", "background", -3)
        td.add_style("min-height: 250px")
        td.add_style("overflow: hidden")

        self.add_no_results_style(td)

        msg_div = DivWdg()
        td.add(msg_div)
        msg_div.add_style("text-align: center")
        msg_div.add_style("margin-left: auto")
        msg_div.add_style("margin-right: auto")
        msg_div.add_style("margin-top: -260px")
        msg_div.add_style("margin-bottom: 20px")
        msg_div.add_style("box-shadow: 0px 0px 10px rgba(0,0,0,0.1)")
        msg_div.add_style("width: 400px")
        msg_div.add_style("height: 100px")


        if not self.is_refresh and self.kwargs.get("do_initial_search") in ['false', False]:
            msg = DivWdg("<i>-- Initial search set to no results --</i>")
        else:

            no_results_msg = self.kwargs.get("no_results_msg")

            msg = DivWdg("<i style='font-weight: bold; font-size: 14px'>- No items found -</i>")
            #msg.set_box_shadow("0px 0px 5px")
            if no_results_msg:
                msg.add("<br/>"*2)
                msg.add(no_results_msg)

            else:
                msg.add("<br/>"*2)
                msg.add("Alter filters for new search.")

        msg_div.add(msg)

        msg.add_style("padding-top: 20px")
        msg.add_style("padding-bottom: 20px")
        msg.add_style("height: 100%")
        msg.add_color("background", "background3")
        msg.add_color("color", "color3")
        msg.add_border()

        msg_div.add("<br clear='all'/>")
        td.add("<br clear='all'/>")



    def add_no_results_bvr(self, tr):
        ''' This adds a default drag and drop behavior to an empty table.
        Override it in classes that extend BaseTableLayoutWdg to handle
        custom drag/drop behaviors '''

        tr.add_attr("ondragover", "spt.table.dragover_row(event, this); return false;")
        tr.add_attr("ondragleave", "spt.table.dragleave_row(event, this); return false;")
        tr.add_attr("ondrop", "spt.table.drop_row(event, this); return false;")


    def add_no_results_style(self, td):
        ''' This adds the default styling to an empty table.
        Override it in classes that extend BaseTableLayoutWdg if you
        want something different'''

        for i in range(0, 10):
            div = DivWdg()
            td.add(div)
            div.add_style("height: 30px")

            if i % 2:
                div.add_color("background", "background")
            else:
                div.add_color("background", "background", -3)
