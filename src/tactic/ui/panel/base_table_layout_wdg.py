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
from pyasm.search import SearchType, Search, SqlException, SearchKey, SObject
from pyasm.web import WebContainer, Table, DivWdg, SpanWdg, Widget
from pyasm.widget import WidgetConfig, WidgetConfigView, IconWdg, IconButtonWdg, HiddenWdg
from pyasm.biz import ExpressionParser

from tactic.ui.common import BaseConfigWdg, BaseRefreshWdg
from tactic.ui.container import Menu, MenuItem, SmartMenu
from tactic.ui.container import HorizLayoutWdg
from tactic.ui.widget import DgTableGearMenuWdg, ActionButtonWdg
from layout_wdg import SwitchLayoutMenu

import random, types, re




class BaseTableLayoutWdg(BaseConfigWdg):

    GROUP_WEEKLY = "weekly"
    GROUP_MONTHLY = "monthly"


    def can_inline_insert(my):
        return True

    def can_save(my):
        return True

    def can_expand(my):
        return True
    def get_expand_behavior(my):
        return None

    def can_add_columns(my):
        return True

    def can_select(my):
        return True

    def can_use_gear(my):
        return True






    def __init__(my, **kwargs):

        # get the them from cgi
        my.handle_args(kwargs)
        my.kwargs = kwargs

        my.help_alias = 'views-quickstart|what-are-views'
        mode = kwargs.get("mode")

        # required args
        my.table_id = kwargs.get('table_id')
        if not my.table_id:
            my.table_id = kwargs.get('id')
        if not my.table_id:
            num = random.randint(0,10000)
            my.table_id = "main_body_table_%s"%num
        if mode == 'insert':
            my.table_id = "%s_insert" %my.table_id

        my.table_id = my.table_id.replace(" ", "_")

        my.target_id = kwargs.get('target_id')
        if not my.target_id:
            my.target_id = "main_body"

            
        my.search_type = kwargs.get('search_type')
        if not my.search_type:
            raise TacticException("Must define a search type")
        my.view = kwargs.get('view')
        if not my.view:
            my.view = 'table'

        my.search_view = kwargs.get('search_view')
        my.search_key = kwargs.get("search_key")
        my.ingest_data_view = kwargs.get("ingest_data_view")

        # DEPRECATED: Do not use
        if not my.view:
            my.view = kwargs.get('config_base')


        my.show_search_limit = kwargs.get('show_search_limit')
        if my.show_search_limit == "false":
            my.show_search_limit = False
        #elif my.kwargs.get('expression'):
            #my.show_search_limit = False
        else:
            my.show_search_limit = True

        my.is_refresh = kwargs.get('is_refresh') == 'true'
        my.aux_info = kwargs.get('aux_info')
        my.vertical_text = kwargs.get('vertical_text') == 'true'

        my.order_widget = None
        my.group_element = ""
        my.group_interval = ""
        my.group_sobjects = []
        my.order_element = ""
        my.show_retired_element = ""

        my.element_names = []

        # handle config explicitly set
        config = my.kwargs.get("config")
        config_xml = my.kwargs.get("config_xml")
        my.config_xml = config_xml
        if config_xml:
            # get the base configs
            config = WidgetConfigView.get_by_search_type(search_type=my.search_type, view=my.view)
            extra_config = WidgetConfig.get(view=my.view, xml=config_xml)
            config.get_configs().insert(0, extra_config)

        elif not config:
            custom_column_configs = WidgetConfigView.get_by_type("column") 
            
            # handle element names explicitly set
            my.element_names = my.kwargs.get("element_names")
            if my.element_names:
                config = WidgetConfigView.get_by_search_type(search_type=my.search_type, view=my.view)
                if type(my.element_names) in types.StringTypes:
                    my.element_names = my.element_names.split(",")
                    my.element_names = [x.strip() for x in my.element_names]
                
                config_xml = "<config><custom layout='TableLayoutWdg'>"
                for element_name in my.element_names:
                    config_xml += "<element name='%s'/>" % element_name
                config_xml += "</custom></config>"
                # my.view is changed for a reason, since a dynamic config supercedes all here
                # We don't want to change the overall view ... just the
                # top level config
                #my.view = "custom"
                #extra_config = WidgetConfig.get(view=my.view, xml=config_xml)
                extra_config = WidgetConfig.get(view="custom", xml=config_xml)
                config.get_configs().insert(0, extra_config)



            else:
                config = WidgetConfigView.get_by_search_type(search_type=my.search_type, view=my.view)
            
            config.get_configs().extend( custom_column_configs )
        #
        # FIXME: For backwards compatibility. Remove this
        #
        my.aux_data = []
        my.row_ids = {}

        # there is this whole assumption that search_type is set in the
        # form values
        web = WebContainer.get_web()
        web.set_form_value("search_type", my.search_type)
        web.set_form_value("ref_search_type", my.search_type)

        my.attributes = []

        super(BaseTableLayoutWdg,my).__init__(search_type=my.search_type, config_base=my.view, config=config)

        my.view_attributes = my.config.get_view_attributes()

        # my.parent_key is used to determine the parent for inline add-new-items purposes
        my.parent_key = my.kwargs.get("parent_key")
        my.parent_path = my.kwargs.get("parent_path")
        my.checkin_context = my.kwargs.get("checkin_context")
        my.checkin_type = my.kwargs.get("checkin_type")
        if not my.checkin_type:
            my.checkin_type = 'auto'
        my.state = my.kwargs.get("state")
        my.state = BaseRefreshWdg.process_state(my.state)
        my.expr_sobjects = []
        if not my.parent_key:
            my.parent_key = my.state.get("parent_key")

        if my.parent_key == 'self':
            my.parent_key = my.search_key

        if not my.parent_key:
            # generate it. parent_key could be none if the expression evaluates to None
            expression = my.kwargs.get('expression')
            if expression:
                if my.search_key and (my.search_key not in ["%s", 'None']):
                    start_sobj = Search.get_by_search_key(my.search_key)
                else:
                    start_sobj = None

                my.expr_sobjects = Search.eval(expression, start_sobj, list=True)

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
                
                if not related_type and my.search_key:
                    # this is needed for single search type expression
                    related_type = SearchKey.extract_search_type(my.search_key)
                   
                if my.expr_sobjects and related_type:
                    # Even if these expression driven sobjects have more than 1 parent.. we can only take 1 parent key
                    # for insert popup purpose.. This doesn't affect the search though since with expression, the search logic
                    # doesn't go through the regular Search
                    related = my.expr_sobjects[0].get_related_sobject(related_type)
                    if related:
                        my.parent_key = SearchKey.get_by_sobject(related, use_id=True)
                elif related_type and my.search_key and related_type in my.search_key:
                    # the expression table could start out empty
                    my.parent_key = my.search_key

                   
            else:
                my.parent_key = my.search_key


        if my.parent_key == "__NONE__":
            my.parent_key = ""
            my.no_results = True
        else:
            my.no_results = False

        # clear if it is None
        if not my.parent_key:
             my.parent_key = ''



        # handle a connect key
        my.connect_key = my.kwargs.get("connect_key")
    

        my.table = Table()
        my.table.set_id(my.table_id)


        # this unique id is used to find quickly find elements that
        # are children of this table
        my.table.add_attr("unique_id", my.table_id)

        my.table.add_class("spt_table")
        mode = my.kwargs.get("mode")
        
        # this makes Task edit content not refreshing properly, commented out 
        # for now
        #if mode != "insert":
        my.table.add_class("spt_table_content")

        width = kwargs.get('width')
        if width:
            my.table.add_style("width: %s" % width)

        my.min_cell_height = kwargs.get('min_cell_height')
        if not my.min_cell_height:
            my.min_cell_height = my.state.get("min_cell_height")
        if not my.min_cell_height:
            my.min_cell_height = "20"

        my.simple_search_view = my.kwargs.get("simple_search_view")
        # Always instantiate the search limit for the pagination at the bottom
        
        from tactic.ui.app import SearchLimitWdg
        my.search_limit = SearchLimitWdg()

        my.items_found = 0

        my.tbodies = []
        my.chunk_num = 0
        my.chunk_size = 100
        my.chunk_iterations = 0

        my.search_wdg = None

        # Needed for MMS_COLOR_OVERRIDE ...
        web = WebContainer.get_web()
        my.skin = web.get_skin()

        # Set up default row looks ...
        my.look_row = 'dg_row'
        my.look_row_hilite = 'dg_row_hilite'
        my.look_row_selected = 'dg_row_selected'
        my.look_row_selected_hilite = 'dg_row_selected_hilite'

        # MMS_COLOR_OVERRIDE ...
        if my.skin == 'MMS':
            my.look_row = 'mms_dg_row'
            my.look_row_hilite = 'mms_dg_row_hilite'
            my.look_row_selected = 'mms_dg_row_selected'
            my.look_row_selected_hilite = 'mms_dg_row_selected_hilite'


        my.palette = web.get_palette()

        my.search_container_wdg = DivWdg()
        # a dictionary of widget class name and boolean True as they are drawn
        my.drawn_widgets = {}

    def get_aux_info(my):
        return my.aux_info

    def get_kwargs(my):
        return my.kwargs



    def get_table_id(my):
        return my.table_id

    def get_table(my):
        return my.table

    def get_view(my):
        return my.view

    def set_items_found(my, number):
        my.items_found = number
    
    def set_search_wdg(my, search_wdg):
        my.search_wdg = search_wdg


    def is_expression_element(my, element_name):
        from tactic.ui.table import ExpressionElementWdg
        widget = my.get_widget(element_name)
        return isinstance(widget, ExpressionElementWdg)





    def get_alias_for_search_type(my, search_type):
        if search_type == 'config/naming':
            my.help_alias = 'project-automation-file-naming'
        elif search_type == 'sthpw/clipboard':
            my.help_alias = 'clipboard'
        return my.help_alias



    def handle_args(my, kwargs):
        # verify the args
        #args_keys = my.get_args_keys()
        args_keys = my.ARGS_KEYS
        for key in kwargs.keys():
            if not args_keys.has_key(key):
                #raise TacticException("Key [%s] not in accepted arguments" % key)
                pass



    def get_order_element(my, order_element):
        direction = 'asc'
        if order_element.find(" desc") != -1:
            tmp_order_element = order_element.replace(" desc", "")
            direction = 'desc'
        elif my.order_element.find(" asc") != -1:
            tmp_order_element = order_element.replace(" asc", "")
            direction = 'asc'
        else:
            tmp_order_element = order_element
            
        return tmp_order_element, direction

    def alter_search(my, search):
        '''give the table a chance to alter the search'''
       
        from tactic.ui.filter import FilterData
        filter_data = FilterData.get_from_cgi()


        # solution for state filter grouping or what not
        # combine the 2 filters from kwarg and state
        state_filter = ''
        if my.state.get('filter'):
            state_filter = my.state.get('filter')
        if my.kwargs.get('filter'): 
            state_filter = '%s%s' %(state_filter, my.kwargs.get('filter') )

        if my.kwargs.get('op_filters'):
            search.add_op_filters(my.kwargs.get("op_filters"))


        # passed in filter overrides
        values = filter_data.get_values_by_prefix("group")
        order = WebContainer.get_web().get_form_value('order')
        
        # user-chosen order has top priority
        if order:
            my.order_element = order
            if not values:
                tmp_order_element, direction  = my.get_order_element(my.order_element)
                
                widget = my.get_widget(tmp_order_element)
                my.order_widget = widget
                try:
                    widget.alter_order_by(search, direction)
                except AttributeError:
                    search.add_order_by(my.order_element, direction)

        if values:

            group_values = values[0]

            # the group element is always ordered first
            my.group_element = group_values.get("group")

            if my.group_element == 'true':
                my.group_element = True
            elif my.group_element:
                # used in Fast Table
                my.group_interval = group_values.get("interval")
                # order by is no longer coupled with group by
                # it can be turned on together in the context menu Group and Order by
            else:
                my.group_element = False

            my.order_element = group_values.get("order")

            if my.order_element:
                tmp_order_element, direction  = my.get_order_element(my.order_element)
                widget = my.get_widget(tmp_order_element)
                my.order_widget = widget
                try:
                    widget.alter_order_by(search, direction)
                except AttributeError:
                    search.add_order_by(tmp_order_element, direction)

            my.show_retired_element = group_values.get("show_retired")
            if my.show_retired_element == "true":
                search.set_show_retired(True)


        order_by = my.kwargs.get('order_by')
        if order_by:
            search.add_order_by(order_by)
            # if nothing is set by user or filter data, use this kwarg
            if not my.order_element:
                my.order_element = order_by

        # make sure the search limit is the last filter added so that the counts
        # are correct
        if my.search_limit:
            limit = my.kwargs.get("chunk_limit")
            if not limit:
                limit = my.kwargs.get('search_limit')
                if limit:
                    try:
                        limit = int(limit)
                        my.search_limit.set_limit(limit)
                    except ValueError, e:
                        pass
                stated_limit = my.search_limit.get_stated_limit()
                if stated_limit:
                    limit = stated_limit
                if not limit:
                    limit = 100
            """
            my.chunk_num = my.kwargs.get("chunk_num")

            if my.chunk_num:
                my.chunk_num = int(my.chunk_num)
            else:
                my.chunk_num = 0

            # if the total to be display after this chunk is greater than
            # the limit, then reduce to fit the limit
            total = (my.chunk_num+1)*my.chunk_size
            if total > limit:
                diff = limit - (total-my.chunk_size)
                #my.search_limit.set_chunk(diff, my.chunk_num)
                my.search_limit.set_chunk(my.chunk_size, my.chunk_num, diff)
            else:
                my.search_limit.set_chunk(my.chunk_size, my.chunk_num)
            """
            # alter the search
            my.search_limit.set_search(search)
            my.search_limit.alter_search(search)




    def handle_search(my):
        '''method where the table handles it's own search on refresh'''


        from tactic.ui.app.simple_search_wdg import SimpleSearchWdg
        my.keyword_column = SimpleSearchWdg.get_search_col(my.search_type, my.simple_search_view)


        if my.is_sobjects_explicitly_set():
            return

        if not my.is_refresh and my.kwargs.get("do_initial_search") in ['false', False]:
            return


        expr_search = None
        expression = my.kwargs.get('expression')
        if my.expr_sobjects:
            if isinstance(my.expr_sobjects[0], Search):
                expr_search = my.expr_sobjects[0]
            else:
                # this is not so efficient: better to use @SEARCH,
                # but we support in anyway, just in case
                expr_search = Search(my.search_type)
                ids = SObject.get_values(my.expr_sobjects, 'id')
                expr_search.add_filters('id', ids)

        elif expression:
            # if the expr_sobjects is empty and there is an expression, this
            # means that the expression evaluated to no sobjects
            # which means the entire search is empty
            my.sobjects = []
            return



        # don't set the view here, it affects the logic in SearchWdg
        filter_json = ''
        if my.kwargs.get('filter'):
            filter_json = my.kwargs.get('filter')
            
        # turn on user_override since the user probably would alter the saved search 
        limit = my.kwargs.get('search_limit')
        custom_search_view = my.kwargs.get('custom_search_view')
        if not custom_search_view:
            custom_search_view = ''

        run_search_bvr = my.kwargs.get('run_search_bvr')

        #my.search_wdg = None
        if not my.search_wdg:
            my.search_wdg = my.kwargs.get("search_wdg")
        if not my.search_wdg:
            from tactic.ui.app import SearchWdg
            # if this is not passed in, then create one
            # custom_filter_view and custom_search_view are less used, so excluded here
            my.search_wdg = SearchWdg(search_type=my.search_type, state=my.state, filter=filter_json, view=my.search_view, user_override=True, parent_key=None, run_search_bvr=run_search_bvr, limit=limit, custom_search_view=custom_search_view)

        
        search = my.search_wdg.get_search()


        from tactic.ui.filter import FilterData
        filter_data = FilterData.get_from_cgi()

        keyword_values = filter_data.get_values_by_prefix("keyword")

        if keyword_values:

            keyword_value = keyword_values[0].get('value')
            if keyword_value:
                from tactic.ui.filter import KeywordFilterElementWdg
                keyword_filter = KeywordFilterElementWdg(column=my.keyword_column, mode="keyword")
                keyword_filter.set_values(keyword_values[0])
                keyword_filter.alter_search(search)


        if my.no_results:
            search.set_null_filter()

        if expr_search:
            search.add_relationship_search_filter(expr_search)


        if my.connect_key == "__NONE__":
            search.set_null_filter()
        elif my.connect_key:
            # get all of the connections of this src
            from pyasm.biz import SObjectConnection
            src_sobjects = Search.get_by_search_key(my.connect_key)
            dst_sobjects = src_sobjects.get_connections(context='task')
            ids = [x.get_id() for x in dst_sobjects]
            search.add_filters("id", ids)



        # add an exposed search
        simple_search_view = my.kwargs.get('simple_search_view')
        if simple_search_view:
            my.search_class = "tactic.ui.app.simple_search_wdg.SimpleSearchWdg"
        else:
            # add a custom search class
            my.search_class = my.kwargs.get('search_class')
            simple_search_view = my.kwargs.get("search_view")
    

        
        if my.search_class and my.search_class not in  ['None','null']:
            kwargs = {
                "search_type": my.search_type,
                "search_view": simple_search_view,
                "keywords": my.kwargs.get("keywords")
            }
            simple_search_wdg = Common.create_from_class_path(my.search_class, kwargs=kwargs)
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

        # re-get parent key from kwargs because my.parent is retrieved
        # This only is used if an expression is not used.  Otherwise, the
        # search_key is applied to the expression
        parent_key = None
        if not expression:
            parent_key = my.kwargs.get("search_key")
        if not parent_key:
            parent_key = my.kwargs.get("parent_key")
        if parent_key and parent_key != "%s" and parent_key not in ["__NONE__", "None"]:
            print "parent_key: ", parent_key
            parent = Search.get_by_search_key(parent_key)
            if not parent:
                my.sobjects = []
                my.items_found = 0
                return
            # NOTE: this parent path is a bit of a hack to make tables that
            # are not immediate relations to still be accessed
            if my.parent_path:
                logs = Search.eval("@SOBJECT(%s)" % my.parent_path, parent, list=True)
                if logs:
                    search.add_filters("id", [x.get_id() for x in logs] )
                else:
                    search.set_null_filter()

            else:
                search.add_relationship_filter(parent)

        try:
            my.alter_search(search)
            my.items_found = search.get_count()
            my.sobjects = search.get_sobjects()
        except SqlException, e:
            my.search_wdg.clear_search_data(search.get_base_search_type())


    	my.element_process_sobjects(search)





    def element_process_sobjects(my, search):
        # give each widget a chance to alter the order post search
        for widget in my.widgets:
            try:
                sobjects = widget.process_sobjects(my.sobjects, search)
            except Exception, e:
                #print str(e)
                pass
            else:
                if sobjects:
                    my.sobjects = sobjects

    def process_sobjects(my):
        '''provides the opportunity to post-process the search'''
        class_name = 'mms.TerminalSearchWdg'
        search = Common.create_from_class_path(class_name)
        sobjects = search.process_sobjects(my.sobjects)
        if sobjects != None:
            my.sobjects = sobjects
        
    def set_as_panel(my, widget):
        widget.add_class("spt_panel")
        widget.add_attr("spt_class_name", Common.get_full_class_name(my) )
        for name, value in my.kwargs.items():
            if value == None:
                continue
            if not isinstance(value, basestring):
                value = str(value)
            # replace " with ' in case the kwargs is a dict
            value = value.replace('"', "'")
            widget.add_attr("spt_%s" % name, value)

        # add view attributes
        if my.view_attributes:
            value = jsondumps(my.view_attributes)
            # replace " with ' in case the kwargs is a dict
            value = value.replace('"', "'")
            widget.add_attr("spt_view_attrs" , value)



    def get_show_insert(my):
        show_insert = my.view_attributes.get("insert")
        # if edit_permission on the sobject is not allowed then we don't
        # allow insert
        if my.edit_permission == False:
            show_insert = False

        if show_insert in [ '', None ]:
            show_insert = my.kwargs.get("show_insert")

        if show_insert in ['false', False]:
            show_insert = False
        else:
            show_insert = True


        return show_insert





    def get_action_wdg(my):

        # determine from the view if the insert button is visible
        show_insert = my.get_show_insert()
        show_retired = my.view_attributes.get("retire")
        show_delete = my.view_attributes.get("delete")

        from tactic.ui.widget import TextBtnWdg, TextBtnSetWdg

        div = DivWdg() 
        div.add_class("SPT_DTS")
        #div.add_style("overflow: hidden")
        div.add_style("padding-top: 3px")
        div.add_style("padding-right: 8px")
        div.add_color("color", "color")
        #div.add_gradient("background", "background")
        div.add_color("background", "background",-3)

        if not my.kwargs.get("__hidden__"):
            #div.add_style("margin-left: -1px")
            #div.add_style("margin-right: -1px")

            #div.add_border()
            div.add_style("border-width: 1px 1px 0px 1px")
            div.add_style("border-style: solid")
            div.add_style("border-color: %s" % div.get_color("border"))
            div.add_style("border-color: #BBB")

        else:
            div.add_style("border-width: 0px 0px 0px 0px")
            div.add_style("border-style: solid")
            div.add_style("border-color: %s" % div.get_color("table_border"))
        #div.add_color("background", "background3")


        # the label on the commit button
        commit_label = 'Save'

        # Look for custom gear menu items from configuration ...
        custom_gear_menus = None

        try:
            search = Search('config/widget_config')
            search.add_filter("view", "gear_menu_custom")
            search.add_filter("search_type", my.search_type)
            config_sobj = search.get_sobject()
        except Exception, e:
            print "WARNING: When trying to find config: ", e
            config_sobj = None

        if config_sobj:
            config_xml = config_sobj.get_xml_value("config")
            stmt = 'custom_gear_menus = %s' % config_xml.get_value("config/gear_menu_custom").strip()
            try:
                exec stmt
            except:
                custom_gear_menus = "CONFIG-ERROR"



        # add gear menu here
        my.view_save_dialog = None
        if my.can_use_gear() and my.kwargs.get("show_gear") not in ["false", False]:
            # Handle configuration for custom script (or straight javascript script) on "post-action on delete"
            # activity ...
            cbjs_post_delete = ''

            if my.kwargs.get("post_delete_script"):
                post_delete_script = my.kwargs.get("post_delete_script")
                # get the script code from the custom_script table of the project ...
                prj_code = Project.get_project_code()
                script_s_key = "config/custom_script?project=%s&code=%s" % (prj_code, post_delete_script)
                custom_script_sobj = Search.get_by_search_key( script_s_key )
                if not custom_script_sobj:
                    print 'Did NOT find a code="%s" custom_script entry for post DG table save' % (post_delete_script)
                cbjs_post_delete = custom_script_sobj.get_value('script')

            if my.kwargs.get("post_delete_js"):
                cbjs_post_delete = my.kwargs.get("post_delete_js")

            embedded_table =  my.kwargs.get("__hidden__") == 'true'
           
            btn_dd = DgTableGearMenuWdg(
                layout=my,
                table_id=my.get_table_id(),
                search_type=my.search_type, view=my.view,
                parent_key=my.parent_key,
                cbjs_post_delete=cbjs_post_delete, show_delete=show_delete,
                custom_menus=custom_gear_menus,
                show_retired=show_retired, embedded_table=embedded_table,
                ingest_data_view = my.ingest_data_view
            )

            my.gear_menus = btn_dd.get_menu_data()
            my.view_save_dialog = btn_dd.get_save_dialog()
            div.add(btn_dd)

        else:
            my.gear_menus = None
            btn_dd = Widget()


        column = "keywords"
        simple_search_mode = my.kwargs.get("simple_search_mode")
        
        show_keyword_search = my.kwargs.get("show_keyword_search")
        if show_keyword_search in [True, 'true']:
            show_keyword_search = True
        else:
            show_keyword_search = False

        # TEST: on by default
        show_keyword_search = True

        show_search = my.kwargs.get("show_search") != 'false'

       
        if show_search and show_keyword_search:
            keyword_div = DivWdg()
            keyword_div.add_class("spt_table_search")
            hidden = HiddenWdg("prefix", "keyword")
            keyword_div.add(hidden)

            from tactic.ui.filter import FilterData
            filter_data = FilterData.get_from_cgi()
            values_list = filter_data.get_values_by_prefix("keyword")
            if values_list:
                values = values_list[0]
            else:
                values = {}

            from tactic.ui.app.simple_search_wdg import SimpleSearchWdg
            my.keyword_column = SimpleSearchWdg.get_search_col(my.search_type, my.simple_search_view)

            from tactic.ui.filter import KeywordFilterElementWdg
            keyword_filter = KeywordFilterElementWdg(
                    column=my.keyword_column,
                    mode="keyword",
                    filter_search_type=my.search_type,
                    icon="",
                    width="75",
                    show_partial=False,
                    show_toggle=True
            )
            keyword_filter.set_values(values)
            keyword_div.add(keyword_filter)
            keyword_div.add_style("margin-top: 0px")
            keyword_div.add_style("height: 30px")
            keyword_div.add_style("margin-left: -6px")

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
                        var simple_search = top.getElement(".spt_simple_search");
                        if (simple_search) {
                            simple_search.setStyle("display", "");
                            spt.body.add_focus_element(simple_search);
                        }
                    }

                   

                    '''
                } )

            """
            # this make clicking on the Search not work when the focus is on text input
            keyword_div.add_relay_behavior( {
                'type': 'blur',
                'bvr_match_class': "spt_text_input",
                'cbjs_action': '''
                
                var el = bvr.src_el;
                
                el.setStyle("width", "75px");

                '''
            } )
            """

        else:
            keyword_div = None



        spacing_divs = []
        for i in range(0, 6):
            spacing_div = DivWdg()
            spacing_divs.append(spacing_div)
            spacing_div.add_style("height: 32px")
            spacing_div.add_style("width: 2px")
            spacing_div.add_style("margin: 0 7 0 7")
            spacing_div.add_style("border-style: solid")
            spacing_div.add_style("border-width: 0 0 0 1")
            spacing_div.add_style("border-color: %s" % spacing_div.get_color("border"))


        # -- Button Rows
        button_row_wdg = my.get_button_row_wdg()
        button_row_wdg.add_style("margin-top: 0px")
        button_row_wdg.add_style("margin-left: 3px")


        # -- ITEM COUNT DISPLAY
        # add number found
        if my.show_search_limit:
            num_div = DivWdg()
            num_div.add_color("color", "color")
            num_div.add_style("float: left")
            num_div.add_style("margin-top: 0px")
            num_div.add_style("font-size: 10px")
            num_div.add_style("padding: 5px")
            
            # -- SEARCH LIMIT DISPLAY
            if my.items_found == 0:
                if my.search:
                    my.items_found = my.search.get_count()
                elif my.sobjects:
                    my.items_found = len(my.sobjects)

           
            if my.items_found == 1:
                num_div.add( "%s %s" % (my.items_found, _("item found")))
            else:
                num_div.add( "%s %s" % (my.items_found, _("items found")))
            num_div.add_style("margin-right: 0px")
            num_div.add_border(style="none")
            num_div.set_round_corners(6)
        else:
            num_div = None
        



        # -- PAGINATION TOOLS
        limit_span = DivWdg()
        limit_span.add_style("margin-top: 4px")
        if my.show_search_limit:
            search_limit_button = IconButtonWdg("Pagination", IconWdg.ARROWHEAD_DARK_DOWN)
            num_div.add(search_limit_button)
            from tactic.ui.container import DialogWdg
            dialog = DialogWdg()
            #limit_span.add(dialog)
            dialog.set_as_activator(num_div, offset={'x':0,'y': 0})
            dialog.add_title("Search Range")
            num_div.add_class("hand")
            color = num_div.get_color("background3", -5)
            num_div.add_behavior( {
                'type': 'mouseover',
                'color': color,
                'cbjs_action': '''
                bvr.src_el.setStyle("background", bvr.color);
                '''
            } )
            num_div.add_behavior( {
                'type': 'mouseout',
                'cbjs_action': '''
                bvr.src_el.setStyle("background", "");
                '''
            } )


            limit_div = DivWdg()
            limit_div.add_class("spt_table_search")
            limit_div.add(my.search_limit)
            dialog.add(limit_div)
            limit_div.add_color("color", "color")
            limit_div.add_color("background", "background")
            limit_div.add_style("width: 300px")
            #limit_div.add_style("height: 50px")

            #limit_span.add(my.search_limit)




        search_button_row = my.get_search_button_row_wdg()
        save_button = my.get_save_button()
        layout_wdg = None
        column_wdg = None
        
        show_column_wdg = my.kwargs.get('show_column_manager') 
        show_layout_wdg = my.kwargs.get('show_layout_switcher') 
        
        if not show_column_wdg =='false' and my.can_add_columns():
            column_wdg = my.get_column_manager_wdg()
        if not show_layout_wdg =='false':
            layout_wdg = my.get_layout_wdg()

        show_expand = my.kwargs.get("show_expand")
        if show_expand in ['false', False]:
            show_expand = False
        else:
            show_expand = True
        #if show_expand in ['true', True]:
        #    show_expand = True
        #else:
        #    show_expand = False
        if not my.can_expand():
            show_expand = False
 
        expand_wdg = None
        if show_expand:
            from tactic.ui.widget.button_new_wdg import ButtonNewWdg

            button = ButtonNewWdg(title='Expand Table', icon='BS_FULLSCREEN', show_menu=False, is_disabled=False)
            
            expand_behavior = my.get_expand_behavior()
            if expand_behavior:
                button.add_behavior( expand_behavior )
            else:
                button.add_behavior( {
                'type': 'click_up',
                'cbjs_action': '''
                var layout = bvr.src_el.getParent(".spt_layout");

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


        help_alias = my.get_alias_for_search_type(my.search_type)
        from tactic.ui.app import HelpButtonWdg
        if HelpButtonWdg.exists():
            help_wdg = HelpButtonWdg(alias=help_alias, use_icon=True)
            help_wdg.add_style("margin-top: -2px")
        else:
            help_wdg = None


        wdg_list = []








        if keyword_div:
            wdg_list.append( {'wdg': keyword_div} )
            keyword_div.add_style("margin-left: 20px")


        if my.kwargs.get("show_refresh") != 'false':
            button_div = DivWdg()
            #button = ActionButtonWdg(title='Search', icon=IconWdg.REFRESH_GRAY)
            if show_search:
                search_label = 'Search'
            else:
                search_label = 'Refresh'
            button = ActionButtonWdg(title=search_label)
            my.run_search_bvr = my.kwargs.get('run_search_bvr')
            if my.run_search_bvr:
                button.add_behavior(my.run_search_bvr)
            else:
                button.add_behavior( {
                'type': 'click_up',
                'cbjs_action':  'spt.dg_table.search_cbk(evt, bvr)'
            } )

            button_div.add(button)
            button_div.add_style("margin-left: -6px")
            wdg_list.append({'wdg': button_div})


        if save_button:
            wdg_list.append( {'wdg': save_button} )
            wdg_list.append( { 'wdg': spacing_divs[3] } )


        if button_row_wdg.get_num_buttons() != 0:
            wdg_list.append( { 'wdg': button_row_wdg } )

        if my.show_search_limit:
            wdg_list.append( { 'wdg': spacing_divs[0] } )
            if num_div:
                wdg_list.append( { 'wdg': num_div } )
            wdg_list.append( { 'wdg': limit_span } )
        else:
            if num_div:
                wdg_list.append( { 'wdg': num_div } )

        wdg_list.append( { 'wdg': spacing_divs[1] } )

        from tactic.ui.widget import ButtonRowWdg
        button_row_wdg = ButtonRowWdg(show_title=True)
        extra_row_wdg = ButtonRowWdg(show_title=True)

        if search_button_row:
            button_row_wdg.add(search_button_row)
            if my.filter_num_div:
                wdg_list.append( { 'wdg': my.filter_num_div } )
            

        if column_wdg:
            button_row_wdg.add(column_wdg)

        if layout_wdg:
            button_row_wdg.add(layout_wdg)

        if button_row_wdg.get_num_buttons() != 0:
            wdg_list.append( { 'wdg': button_row_wdg } )
        
        if expand_wdg:
            wdg_list.append( { 'wdg': spacing_divs[0] } )
            wdg_list.append( { 'wdg': extra_row_wdg } )
            extra_row_wdg.add(expand_wdg)



        show_quick_add = my.kwargs.get("show_quick_add")
        if show_quick_add in ['true',True]:
            quick_add_button_row = my.get_quick_add_wdg()
            wdg_list.append( { 'wdg': spacing_divs[2] } )
            wdg_list.append( { 'wdg': quick_add_button_row } )


        # add the help widget
        if help_wdg:
            wdg_list.append( { 'wdg': spacing_divs[4] } )
            wdg_list.append( { 'wdg': help_wdg } )


        shelf_wdg = my.get_shelf_wdg()
        if shelf_wdg:
            wdg_list.append( { 'wdg': spacing_divs[5] } )
            wdg_list.append( { 'wdg': shelf_wdg } )

        
        horiz_wdg = HorizLayoutWdg( widget_map_list = wdg_list, spacing = 4 )
        xx = DivWdg()
        xx.add(horiz_wdg)
        div.add(xx)

        if my.kwargs.get("__hidden__"):
            scale = 0.8
        else:
            scale = 1


        outer = DivWdg()

        # Different browsers seem to have a lot of trouble with this
        web = WebContainer.get_web()
        browser = web.get_browser()
        import os
        if browser == 'Qt' and os.name != 'nt':
            height = "41px"
        elif scale != 1:
            xx.add_style("position: absolute")
            xx.add_color("backgroud","background")
            xx.set_scale(scale)
            xx.add_style("float: left")
            xx.add_style("margin-left: -25")
            xx.add_style("margin-top: -5")
            div.add_style("opacity: 0.6")
            height = "32px"
        else:
            height = "41px"
            div.add_style("opacity: 0.6")


        outer.add(div)
        if my.show_search_limit:
            outer.add(dialog)
        if my.view_save_dialog:
            outer.add(my.view_save_dialog)

        outer.add_style("min-width: 750px")
        #outer.add_style("width: 300px")
        #outer.add_style("overflow: hidden")
        #outer.add_class("spt_resizable")

        #div.add_style("min-width: 800px")
        div.add_style("height: %s" % height)
        div.add_style("margin: 0px -1px 0px -1px")

        
        

        div.add_behavior( {
            'type': 'mouseenter',
            'cbjs_action': '''
            bvr.src_el.setStyle("opacity", 1.0);
            '''
        } )
        div.add_behavior( {
            'type': 'mouseleave',
            'cbjs_action': '''
            bvr.src_el.setStyle("opacity", 0.6);
            '''
        } )




        return outer



    def get_shelf_wdg(my):
        return None



    def get_save_button(my):
        show_save = True

        if my.edit_permission == False:
            show_save = False

        if not my.can_save():
            show_save = False

        if not show_save:
            return

        # Save button
        from tactic.ui.widget.button_new_wdg import ButtonNewWdg
        save_button = ButtonNewWdg(title='Save', icon="BS_SAVE", show_menu=False, show_arrow=False)
        #save_button.add_style("display", "none")
        save_button.add_class("spt_save_button")
        # it needs to be called save_button_top for the button to re-appear after its dissapeared

        #save_button_top.add_class("btn-primary")
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






    def get_button_row_wdg(my):
        '''draws the button row in the shelf'''
        from tactic.ui.widget.button_new_wdg import ButtonRowWdg, ButtonNewWdg


        shelf_elements = my.kwargs.get("shelf_elements")
        if shelf_elements:
            shelf_elements = shelf_elements.split(",")


        button_row_wdg = ButtonRowWdg(show_title=True)

        """
        if my.kwargs.get("show_refresh") != 'false':
            button = ButtonNewWdg(title='Refresh', icon=IconWdg.REFRESH_GRAY)
            button_row_wdg.add(button)
            my.run_search_bvr = my.kwargs.get('run_search_bvr')
            if my.run_search_bvr:
                button.add_behavior(my.run_search_bvr)
            else:
                button.add_behavior( {
                'type': 'click_up',
                'cbjs_action':  'spt.dg_table.search_cbk(evt, bvr)'
            } )
        """


        # add an item button
        show_insert = my.view_attributes.get("insert")
        # if edit_permission on the sobject is not allowed then
        # we don't allow insert
        show_save = True

        if my.edit_permission == False:
            show_insert = False
            show_save = False

        if not my.can_save():
            show_save = False

        if show_insert in [ '', None ]:
            show_insert = my.kwargs.get("show_insert")

   
        #from tactic.ui.container import Menu, MenuItem, SmartMenu
        if show_insert not in ["false", False]:
            insert_view = my.kwargs.get("insert_view")
            
            if not insert_view or insert_view == 'None':
                insert_view = "insert"

            search_type_obj = SearchType.get(my.search_type)
            search_type_title = search_type_obj.get_value("title")

            #button = ButtonNewWdg(title='Add New Item (Shift-Click to add in page)', icon=IconWdg.ADD_GRAY)
            button = ButtonNewWdg(title='Add New Item (Shift-Click to add in page)', icon="BS_PLUS")
            button_row_wdg.add(button)
            button.add_behavior( {
                'type': 'click_up',
                'view': insert_view,
                'title': search_type_title,
                'table_id': my.table_id,
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
                  save_event: 'search_table_' + bvr.table_id,
                  show_header: false,
                };
                spt.panel.load_popup('Add Item to ' + bvr.title, 'tactic.ui.panel.EditWdg', kwargs);
                '''%my.parent_key

            } )



            if my.can_inline_insert():
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
                    'table_id': my.table_id,
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
                    '''%my.parent_key
                } )




            button.set_show_arrow_menu(True)
            menu = Menu(width=180)
            menu_item = MenuItem(type='title', label='Actions')
            menu.add(menu_item)

            if my.can_inline_insert():
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
                'event_name': 'search_table_%s' % my.table_id,
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
                      save_event: bvr.event_name
                    };
                    spt.panel.load_popup('Single-Insert', 'tactic.ui.panel.EditWdg', kwargs);
                '''%(my.parent_key, insert_view)
            } )

            menu.add(menu_item)
            #menu_item = MenuItem(type='separator')
            #menu.add(menu_item)
            menu_item = MenuItem(type='action', label='Add Multiple Items')
            menu_item.add_behavior( {
                'event_name': 'search_table_%s' % my.table_id,
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
                '''%(my.parent_key, insert_view)
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
            save_button = ButtonNewWdg(title='Save Current Table', icon="BS_SAVE", is_disabled=False)
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


        
        



        if my.can_use_gear() and my.kwargs.get("show_gear") not in ["false", False]:
            #button = ButtonNewWdg(title='More Options', icon=IconWdg.GEAR, show_arrow=True)
            button = ButtonNewWdg(title='More Options', icon="G_SETTINGS_GRAY", show_arrow=True)
            button_row_wdg.add(button)

            smenu_set = SmartMenu.add_smart_menu_set( button.get_button_wdg(), { 'BUTTON_MENU': my.gear_menus } )
            SmartMenu.assign_as_local_activator( button.get_button_wdg(), "BUTTON_MENU", True )
       
        return button_row_wdg




    def get_search_button_row_wdg(my):
        from tactic.ui.widget.button_new_wdg import ButtonRowWdg, ButtonNewWdg, SingleButtonWdg

        my.filter_num_div = None
        # Search button
        search_dialog_id = my.kwargs.get("search_dialog_id")
        show_search = my.kwargs.get("show_search") != 'false'
        if show_search and search_dialog_id:
            div = DivWdg()
            my.table.add_attr("spt_search_dialog_id", search_dialog_id)
            #button = ButtonNewWdg(title='View Advanced Search', icon=IconWdg.ZOOM, show_menu=False, show_arrow=False)
            button = ButtonNewWdg(title='View Advanced Search', icon="BS_SEARCH", show_menu=False, show_arrow=False)
            #button.add_style("float: left")
            div.add(button)


            # TEST ADDING SAVED SEARCHES
            """
            button_row_wdg = ButtonRowWdg(show_title=True)
            div.add(button_row_wdg)
            button = ButtonNewWdg(title='View Advanced Search', icon=IconWdg.ZOOM, show_menu=False, show_arrow=False)
            button_row_wdg.add(button)
            layout = ButtonNewWdg(title='Change Layout', icon=IconWdg.VIEW, show_arrow=True)
            button_row_wdg.add(layout)
            """


            button.add_behavior( {
                'type': 'click_up',
                'dialog_id': search_dialog_id,
                'cbjs_action': '''
                var dialog = $(bvr.dialog_id);
                if (!dialog) {
                    return;
                }

                var offset = bvr.src_el.getPosition();
                var size = bvr.src_el.getSize();
                offset = {x:offset.x-265, y:offset.y+size.y+10};

                var body = $(document.body);
                var scroll_top = body.scrollTop;
                var scroll_left = body.scrollLeft;
                offset.y = offset.y - scroll_top;
                offset.x = offset.x - scroll_left;

                dialog.position({position: 'upperleft', relativeTo: body, offset: offset});
                
                spt.toggle_show_hide(dialog);

                if (spt.is_shown(dialog))
                    spt.body.add_focus_element(dialog);

                '''
            } )


            """
            button.set_show_arrow_menu(True)
            menu = Menu(width=180)
            menu_item = MenuItem(type='title', label='Saved Searches')
            menu.add(menu_item)
            menu_item = MenuItem(type='action', label='Fast Ugly Search')
            menu.add(menu_item)
            menu_item.add_behavior( {
                'cbjs_action': '''
                var activator = spt.smenu.get_activator(bvr);
                spt.dg_table.search_cbk( {}, {src_el: activator, expression: "@SOBJECT(project/asset['@LIMIT','2'])"} );
                '''
            } )
            menus = [menu.get_data()]
            SmartMenu.add_smart_menu_set( button.get_arrow_wdg(), { 'DG_BUTTON_CTX': menus } )
            SmartMenu.assign_as_local_activator( button.get_arrow_wdg(), "DG_BUTTON_CTX", True )
            """


            my.filter_num_div = DivWdg()
            #div.add(my.filter_num_div)
            my.filter_num_div.add_color("color", "color")

            if my.search_wdg:
                num_filters = my.search_wdg.get_num_filters_enabled()
            else:
                num_filters = 0
            icon = IconWdg( "Filters enabled", IconWdg.GREEN_LIGHT )
            my.filter_num_div.add("&nbsp;"*4)
            my.filter_num_div.add(icon)
            my.filter_num_div.add("%s filter(s)" % num_filters)
            if not num_filters:
                my.filter_num_div.add_style("display: none")
            else:
                div.add_style("width: 120px")

            #return div
            return button
        else:
            return None




    def get_layout_wdg(my):

        from tactic.ui.widget.button_new_wdg import ButtonNewWdg
        #layout = ButtonNewWdg(title='Switch Layout', icon=IconWdg.VIEW, show_arrow=True)
        layout = ButtonNewWdg(title='Switch Layout', icon="BS_TH", show_arrow=True)

        SwitchLayoutMenu(search_type=my.search_type, view=my.view, activator=layout.get_button_wdg())
        return layout



    def get_quick_add_wdg(my):
        from tactic.ui.widget.button_new_wdg import ButtonRowWdg, ButtonNewWdg

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





    def get_column_manager_wdg(my):

        security = Environment.get_security()
        if not security.check_access("builtin", "view_column_manager", "allow"):
            return None

        from tactic.ui.widget.button_new_wdg import SingleButtonWdg, ButtonNewWdg

        #button = ButtonNewWdg(title='Column Manager', icon=IconWdg.COLUMNS, show_arrow=False)
        button = ButtonNewWdg(title='Column Manager', icon="BS_TH_LIST", show_arrow=False)

        search_type_obj = SearchType.get(my.search_type)

        button.add_behavior( {
            'type': 'click_up',
            'class_name': 'tactic.ui.panel.AddPredefinedColumnWdg',
            "args": {
                'title': 'Column Manager',
                'search_type': my.search_type,
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

                var class_name = 'tactic.ui.panel.AddPredefinedColumnWdg';

                var popup = spt.panel.load_popup(bvr.args.title, class_name, bvr.args);
                popup.activator = bvr.src_el;
                popup.panel = panel;
                ''',
            } )

        #return div
        return button



    def get_group_wdg(my):

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
        if my.group_element:
            group_input.set_value(my.group_element)

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
        if my.order_element:
            order_input.set_value(my.order_element)
        group_div.add(order_input)

        show_retired_input = HiddenWdg("show_retired")
        show_retired_input.add_class("spt_search_show_retired")
        if my.show_retired_element:
            show_retired_input.set_value(my.show_retired_element)
        group_div.add(show_retired_input)


        return group_div




    def get_smart_header_context_menu_data(my):

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
            #"hover_bvr_cb": { 'activator_add_looks': 'dg_header_cell_hilite',
            #                  'affect_activator_relatives' : [ 'spt.get_next_same_sibling( @, null )' ] }
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
            #"hover_bvr_cb": { 'activator_add_looks': 'dg_header_cell_hilite',
            #                  'affect_activator_relatives' : [ 'spt.get_next_same_sibling( @, null )' ] }
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
                    'search_type': my.search_type,
                    'target_id': my.target_id
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
        menu_data.append( {
            "type": "action",
            "enabled_check_setup_key" : "is_searchable",
            "hide_when_disabled" : True,
            "label": "Local Search",
            "bvr_cb": {
                'cbjs_action': '''var activator = spt.smenu.get_activator(bvr);
                                bvr.options.title = 'Local Search (' + activator.getProperty("spt_element_name").capitalize() + ')';
                                bvr.options.popup_id =  bvr.options.title;
                                bvr.args.prefix_namespace = activator.getProperty("spt_display_class");
                                bvr.args.searchable_search_type =  activator.getProperty("spt_searchable_search_type");
                                spt.popup.get_widget(evt, bvr);
                                ''',
                'options' : {'class_name' : 'tactic.ui.app.LocalSearchWdg' },
                            
                'args' : {'use_last_search': True,  
                          'display' : True,
                          'search_type': my.search_type
                          }
            
            }
        } )
       

        # Edit Column Definition menu item ...
        search_type_obj = SearchType.get(my.search_type)

        security = Environment.get_security()
        if security.check_access("builtin", "view_site_admin", "allow"):

            menu_data.append( {
                "type": "action",
                "label": "Edit Column Definition",
                "bvr_cb": {
                    #'args' : {'search_type': search_type_obj.get_base_key()},
                    'args' : {'search_type': my.search_type},
                    'options': {
                        'class_name': 'tactic.ui.manager.ElementDefinitionWdg',
                        'popup_id': 'edit_column_defn_wdg',
                        'title': 'Edit Column Definition'
                    },
                    'cbjs_action':
                        '''
                        var activator = spt.smenu.get_activator(bvr);
                        bvr.args.element_name = activator.getProperty("spt_element_name");

                        bvr.args.view = activator.getParent('.spt_table').getAttribute('spt_view');
                        //bvr.args.is_insert = true;
                        var popup = spt.popup.get_widget(evt,bvr);
                        popup.activator = activator;
                        '''
                },
                #"hover_bvr_cb": { 'activator_add_looks': 'dg_header_cell_hilite',
                #                  'affect_activator_relatives' : [ 'spt.get_next_same_sibling( @, null )' ] }
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

        # Column Manager menu item ...
        if security.check_access("builtin", "view_column_manager", "allow"):
            menu_data.append( {
            "type": "action",
            "label": "Column Manager",
            "bvr_cb": {
                "args": {
                    'title': 'Column Manager',
                    'search_type': my.search_type,
                    'target_id': my.target_id
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
                    'args' : {'search_type': my.search_type},
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

        

        group_columns = my.kwargs.get("group_elements")
        
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
                 'setup_cbfn':  'spt.dg_table.smenu_ctx.setup_cbk' }




    def get_data_row_smart_context_menu_details(my):
        spec_list = [ { "type": "title", "label": 'Item "{display_label}"' }]
        if my.view_editable:
            edit_view = my.kwargs.get("edit_view")
            
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
                        'dg_row_retired_selected', 'dg_row_retired', my.look_row_selected, my.look_row ] 
                    }
                }
            )

            search_type = my.search_type

            # get the browser
            web = WebContainer.get_web()
            browser = web.get_browser()
            if browser in ['Qt']:
                use_html5 = False
            else:
                use_html5 = True

            if not use_html5:
                bvr_cb = {
                'cbjs_action': r'''

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
                        var snapshot = server.get_by_search_key(search_key);
                        var snapshot_code = snapshot.code;
                        if (search_key.search('sthpw/snapshot')!= -1){                       
                            var kwargs = {file_type:'icon', mode: 'upload', create_icon: 'True'};                        
                            server.add_file( snapshot_code, file, kwargs );                                              
                        }
                        else {
                            file = file.replace(/\\/g, "/");
                            var parts = file.split("/");
                            var filename = parts[parts.length-1];
                            var kwargs;
                            if (context != "icon") {
                                context = context + "/" + filename;
                                kwargs = {mode: 'upload', checkin_type: 'auto'};
                            }
                            else {
                                kwargs = {mode: 'upload'};
                            }
                            server.simple_checkin( search_key, context, file, kwargs);
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

                    '''
                }

            else:

                bvr_cb = {
                'cbjs_action': r'''

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
                        spt.html5upload.set_form( $(bvr.upload_id) );
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
                                var snapshot = server.get_by_search_key(search_key);
                                var snapshot_code = snapshot.code;
                                var kwargs = {file_type:'icon', mode: 'uploaded', create_icon: 'True'};  
                                server.add_file( snapshot_code, file, kwargs );                                              
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
                                    context = context + "/" + filename;
                                    kwargs = {mode: 'uploaded', checkin_type: 'auto'};
                                }
                                else {
                                    kwargs = {mode: 'uploaded'};
                                    
                                }
                                server.simple_checkin( search_key, context, file, kwargs);
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

                        spt.app_busy.show("Uploading", label +  percent + "%");
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

                    '''

                }

            bvr_cb["description"] = "Checking in preview ..."
            bvr_cb["mode"] = "icon"
            # set a dummy
            if Container.get_dict("JSLibraries", "spt_html5upload"):
                my.upload_id = '0'
            bvr_cb["upload_id"] = my.upload_id
            spec_list.append( {
                "type": "action",
                "label": "Change Preview Image",
                #"icon": IconWdg.PHOTOS,
                "bvr_cb": bvr_cb,
                "hover_bvr_cb": {
                    'activator_add_look_suffix': 'hilite',
                    'target_look_order': [
                        'dg_row_retired_selected', 'dg_row_retired', my.look_row_selected, my.look_row ] 
                    }
            } )

            bvr_cb2 = bvr_cb.copy()
            bvr_cb2["description"] = "Checking in new file ..."
            bvr_cb2["context"] = "publish",
            bvr_cb2["checkin_context"] = my.checkin_context,
            bvr_cb2["mode"] = "file"
            bvr_cb2["checkin_type"] =  my.checkin_type
            spec_list.append( {
                "type": "action",
                "label": "Check in New File",
                "upload_id": my.upload_id,
                "mode": "file",
                #"icon": IconWdg.PHOTOS,
                "bvr_cb": bvr_cb2,
                "hover_bvr_cb": {
                    'activator_add_look_suffix': 'hilite',
                    'target_look_order': [
                        'dg_row_retired_selected', 'dg_row_retired', my.look_row_selected, my.look_row ] 
                    }
            } )







        security = Environment.get_security()
        if security.check_access("builtin", "retire_delete", "allow"):
        
            spec_list.extend( [{ "type": "separator" },
                
                { "type": "action", "label": "Reactivate", "icon": IconWdg.CREATE,
                    "enabled_check_setup_key" : "is_retired",
                    "hide_when_disabled" : True,
                    "bvr_cb": { 'cbjs_action': 'spt.dg_table.drow_smenu_reactivate_cbk(evt,bvr);' },
                    "hover_bvr_cb": { 'activator_add_look_suffix': 'hilite',
                                      'target_look_order': [ 'dg_row_retired_selected', 'dg_row_retired',
                                                             my.look_row_selected, my.look_row ] }
                },

                { "type": "action", "label": "Retire",
                    #"icon": IconWdg.RETIRE,
                    "enabled_check_setup_key" : "is_not_retired",
                    "hide_when_disabled" : True,
                    "bvr_cb": { 'cbjs_action': 'spt.dg_table.drow_smenu_retire_cbk(evt,bvr);' },
                    "hover_bvr_cb": { 'activator_add_look_suffix': 'hilite',
                                      'target_look_order': [ 'dg_row_retired_selected', 'dg_row_retired',
                                                             my.look_row_selected, my.look_row ] }
                },

                { "type": "action", "label": "Delete",
                    #"icon": IconWdg.DELETE,
                    "bvr_cb": { 'cbjs_action': 'spt.dg_table.drow_smenu_delete_cbk(evt,bvr);' },
                    "hover_bvr_cb": { 'activator_add_look_suffix': 'hilite',
                                      'target_look_order': [ 'dg_row_retired_selected', 'dg_row_retired',
                                                             my.look_row_selected, my.look_row ] }
                }])

        subscribe_label = 'Item'
        if my.search_type in ['sthpw/task','sthpw/note','sthpw/snapshot']:
            subscribe_label = 'Parent'
        elif my.search_type.startswith('sthpw') or my.search_type.startswith('config'): 
            subscribe_label = None
       
        if subscribe_label:
            spec_list.extend( [

                    { "type": "separator" },

                    { "type": "action", "label": "Item Audit Log",
                        #"icon": IconWdg.CONTENTS,
                        "bvr_cb": { 'cbjs_action': "spt.dg_table.drow_smenu_item_audit_log_cbk(evt, bvr);" },
                        "hover_bvr_cb": { 'activator_add_look_suffix': 'hilite',
                                          'target_look_order': [ 'dg_row_retired_selected', 'dg_row_retired',
                                                                 my.look_row_selected, my.look_row ] }
                    },
                    
                    { "type": "action", "label": "Subscribe to %s"%subscribe_label,
                        #"icon": IconWdg.PICTURE_EDIT,
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
                        } catch(e) {
                            spt.info(spt.exception.handler(e));
                        }
     
                        ''' },
                        "hover_bvr_cb": { 'activator_add_look_suffix': 'hilite',
                                          'target_look_order': [ 'dg_row_retired_selected', 'dg_row_retired',
                                                                 my.look_row_selected, my.look_row ] }
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




        version = my.get_layout_version()

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

    def get_layout_version(my):
        return "2"

