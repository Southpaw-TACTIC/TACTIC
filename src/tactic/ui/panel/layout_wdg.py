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
__all__ = ["AddPredefinedColumnWdg"]

import types
import random
import re
from pyasm.common import Environment, TacticException, Common, Container, Xml, Date, UserException, Config, jsonloads, jsondumps
from pyasm.command import Command
from pyasm.search import Search, SearchKey, SObject, SearchType, WidgetDbConfig, Sql, SqlException
from pyasm.web import *
from pyasm.biz import *   # Project is part of pyasm.biz

from pyasm.widget import TextWdg, TextAreaWdg, SelectWdg, \
                         WidgetConfigView, WidgetConfig, CheckboxWdg, SearchLimitWdg, IconWdg, \
                         EditLinkWdg, FilterSelectWdg, ProdIconButtonWdg, IconButtonWdg, HiddenWdg,\
                         SwapDisplayWdg, HintWdg


# DEPRECATED: use FastTableLayoutWdg


from pyasm.prod.biz import ProdSetting
#from pyasm.widget import SimpleTableElementWdg

from tactic.ui.common import BaseRefreshWdg, BaseTableElementWdg, SimpleTableElementWdg
from tactic.ui.container import PopupWdg, HorizLayoutWdg,  SmartMenu
from tactic.ui.widget import DgTableGearMenuWdg, TextBtnSetWdg, CalendarInputWdg, DynByFoundValueSmartSelectWdg
#from tactic.ui.table import TypeTableElementWdg
from tactic.ui.container import Menu, MenuItem, SmartMenu

from tactic.ui.common import BaseConfigWdg


import random, sys, traceback




# DEPRECATED and renamed now with prefix Old
"""
class OldTableLayoutWdg(BaseConfigWdg):
    INSERT_ROW = 0
    EDIT_ROW = 1
    GROUP_WEEKLY = "weekly"
    GROUP_MONTHLY = "monthly"

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
            raise WidgetException("Must define a search type")
        my.view = kwargs.get('view')
        if not my.view:
            my.view = 'table'

        my.search_view = kwargs.get('search_view')
        my.search_key = kwargs.get("search_key")

        # DEPRECATED: Do not use
        if not my.view:
            my.view = kwargs.get('config_base')


        my.show_search_limit = kwargs.get('show_search_limit')
        if my.show_search_limit == "false":
            my.show_search_limit = False
        elif my.kwargs.get('expression'):
            my.show_search_limit = False
        else:
            my.show_search_limit = True

        my.is_refresh = kwargs.get('is_refresh') == 'true'
        my.aux_info = kwargs.get('aux_info')
        my.vertical_text = kwargs.get('vertical_text') == 'true'

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
            # handle element names explicitly set
            my.element_names = my.kwargs.get("element_names")
            if my.element_names:
                config = WidgetConfigView.get_by_search_type(search_type=my.search_type, view=my.view)
                if type(my.element_names) in types.StringTypes:
                    my.element_names = my.element_names.split(",")
                
                config_xml = "<config><custom layout='OldTableLayoutWdg'>"
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

        super(OldTableLayoutWdg,my).__init__(search_type=my.search_type, config_base=my.view, config=config)

        my.view_attributes = my.config.get_view_attributes()

        # my.parent_key is used to determine the parent for inline add-new-items purposes
        my.parent_key = my.kwargs.get("parent_key")
        my.parent_path = my.kwargs.get("parent_path")
        my.state = my.kwargs.get("state")
        my.state = BaseRefreshWdg.process_state(my.state)
        my.exp_sobjects = []
        if not my.parent_key:
            my.parent_key = my.state.get("parent_key")

        if my.parent_key == 'self':
            my.parent_key = my.search_key

        if not my.parent_key:
            # generate it. parent_key could be none if the expression evaluates to None
            expression = my.kwargs.get('expression')
            if expression:
                if my.search_key and my.search_key != "%s":
                    start_sobj = Search.get_by_search_key(my.search_key)
                else:
                    start_sobj = None

                my.exp_sobjects = Search.eval(expression, start_sobj, list=True)

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
                   
                if my.exp_sobjects and related_type:
                    # Even if these expression driven sobjects have more than 1 parent.. we can only take 1 parent key
                    # for insert popup purpose.. This doesn't affect the search though since with expression, the search logic
                    # doesn't go through the regular Search
                    related = my.exp_sobjects[0].get_related_sobject(related_type)
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


        if not my.show_search_limit:
            my.search_limit = None
        else:
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



    #
    # Define a standard format for widgets
    #

    def get_kwargs(my):
        return my.kwargs


    def get_table_id(my):
        return my.table_id


    '''external settings which populate the widget'''
    def get_args_keys(cls):
        return cls.ARGS_KEYS
    get_args_keys = classmethod(get_args_keys)

    ARGS_KEYS = {

        "search_type": {
            'description': "Search type that this panel works with",
            'type': 'TextWdg',
            'order': 0,
            'category': 'Required'
        },
        "view": {
            'description': "View to be displayed",
            'type': 'TextWdg',
            'order': 1,
            'category': 'Required'
        },
      
        'css': 'CSS class style to use for the body of the table',

        'parent_key': '(Advanced) Set a specific parent for the search. This can be set as "self" to indicate the search_key is the parent_key. ',
        'state': {
            'description': 'INTERNAL. specifies a set of state data for new inserts',
            'category': 'internal'
        },
        'do_search': {
            'description': 'INTERNAL: By default, the TableLayoutWdg will handle the search itself.  However, certain widgets may wish to turn this functionality off because they are supplying the search (internally used by ViewPanelWdg)',
            'category': 'internal'
        },

        'order_by': 'Add an explicit order by in the search',
        'expression': {
            'description': 'Use an expression to drive the search.  The expression must return SObjects',
             'category': 'Display',
             'type': 'TextAreaWdg',
             'order': '092'
        },


        # Display options
        'width': {
            'description': 'Define an initial overall width for the table',
            'category': 'Display',
             'order': '08'
        },
        'schema_default_view': {
            'description': 'INTERNAL. Flag to show whether this is generated straight from the schema',
            'category': 'internal'
        },
        
        "show_search": {
            'description': "determines whether or not to show the search widget",
            'type': 'SelectWdg',
            'values': 'true|false',
            'order': 05,
            'category': 'Display'
        },

        'show_search_limit': {
            'description': 'Flag to determine whether or not to show the search limit',
            'category': 'Display',
            'type': 'SelectWdg',
            'values': 'true|false',
             'order': '05a'
        },
        'show_select': {
            'description': 'Flag to determine whether or not to show row_selection',
            'category': 'Display',
            'type': 'SelectWdg',
            'values': 'true|false',
             'order': '06'
        },
        'show_refresh': {
            'description': 'Flag to determine whether or not to show the refresh icon',
            'category': 'Display',
            'type': 'SelectWdg',
            'values': 'true|false',
            'order': '03'
        },
        'show_gear': {
            'description': 'Flag to determine whether or not to show the gear menu',
            'category': 'Display',
            'type': 'SelectWdg',
            'values': 'true|false',
            'order': '01'
        },
        'show_insert': {
            'description': 'Flag to determine whether or not to show the insert button',
            'category': 'Display',
            'type': 'SelectWdg',
            'values': 'true|false',
            'order': '02'
        },
        'insert_view': {
            'description': 'Specify a custom insert view other than [insert]',
            'category': 'Display',
            'type': 'TextWdg',
         
            'order': '02a'
        },
         'edit_view': {
            'description': 'Specify a custom edit view other than [edit]',
            'category': 'Display',
            'type': 'TextWdg',
         
            'order': '02b'
        },
        'insert_mode': {
            'description': 'aux|inline|popup|none - set the insert mode of the table',
            'category': 'Display',
            'type': 'SelectWdg',
            'values': 'aux|inline|popup|none',
             'order': '07'
        },

        'mode': {
            'description':  'set the mode of the table. It defaults to empty.',
            'category': 'Display',
            'type': 'SelectWdg',
            'empty': 'true',
            'values': 'simple|insert',
            'order': '091'
        },
        'search_limit': 'An overriding search limit. A value < 0 means no limit affecting the search',

        'config_xml': 'Explicitly define the xml widget config',
        'element_names': 'Explicitly set the element names to be drawn',

        # INTERNAL. For refreshing a set of rows
        'search_key': 'explicitly set an sobject',
        'selected_search_keys': 'explicitly set a list of sobjects',

        #'inline_search': 'true|false determines whether to show an inline search or not',
        'search_class': 'specify a custom search class',

        'aux_info': {
            'description': 'auxilliary info for the drawing of this Table',
            'category': 'internal'
        },
        'filter': 'filter data override',
        'filter_xml': 'custom filter xml if not using the default',

        # DEPRECATED: here for backwards compatibility
        'table_id': {
            'description': 'DEPRECATED. Dom element id of the table',
            'category': 'deprecated'
        },
        'id': {
            'description': 'DEPRECATED. Dom element id of the table',
            'category': 'deprecated'
        },
        'search_view': {
            'description': "DEPRECATED. View of the Search if specified. This is used by search widget to draw customized views.",
            'category': 'deprecated'
        },
        'config_base': {
            'description': 'DEPRECATED. View of the search type to be displayed. Same as view',
            'category': 'deprecated'
        },
        'parent_path': {
            'descriptions': 'DEPRECATED. sets the path from the parent to the current search_type',
            'category': 'deprecated'
        },



    }

    def get_alias_for_search_type(my, search_type):
        if search_type == 'config/naming':
            my.help_alias = 'project-automation-file-naming'
        elif search_type == 'sthpw/clipboard':
            my.help_alias = 'clipboard'
        return my.help_alias

    def handle_args(my, kwargs):
        # verify the args
        args_keys = my.get_args_keys()
        for key in kwargs.keys():
            if not args_keys.has_key(key):
                #raise WidgetException("Key [%s] not in accepted arguments" % key)
                pass
        '''
        web = WebContainer.get_web()
        args_keys = my.get_args_keys()
        for key in args_keys.keys():
            if not kwargs.has_key(key):
                value = web.get_form_value(key)
                kwargs[key] = value
        '''    


    def set_items_found(my, number):
        my.items_found = number

    def set_search_wdg(my, search_wdg):
        my.search_wdg = search_wdg

    def get_table(my):
        return my.table


    def get_default_display_handler(cls, element_name):
        #return "tactic.ui.panel.TypeTableElementWdg"
        return "tactic.ui.common.SimpleTableElementWdg"

    get_default_display_handler = classmethod(get_default_display_handler)


    def get_default_display_wdg(cls, element_name, display_options, element_type, kbd_handler=True):
        from tactic.ui.table import TypeTableElementWdg
        element = TypeTableElementWdg()
        element.set_options(display_options)
        element.set_option("type", element_type)
        return element
    get_default_display_wdg = classmethod(get_default_display_wdg)



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
        # passed in filter overrides
        if state_filter:
            filter_data.set_data(state_filter)
        values = filter_data.get_values_by_prefix("group")
        order = WebContainer.get_web().get_form_value('order')

        # user-override order has top priority
        if order:
            search.add_order_by(order)
        if values:
            group_values = values[0]

            # the group element is always ordered first
            my.group_element = group_values.get("group")
            

            if my.group_element == 'true':
                my.group_element = True
            elif my.group_element:
                # used in Fast Table
                my.group_interval = group_values.get("interval")
            else:
                my.group_element = False

            my.order_element = group_values.get("order")
            if my.order_element:
                direction = 'asc' 
                if my.order_element.find(" desc") != -1:
                    tmp_order_element = my.order_element.replace(" desc", "")
                    direction = 'desc'
                elif my.order_element.find(" asc") != -1:
                    tmp_order_element = my.order_element.replace(" asc", "")
                    direction = 'asc'
                else:
                    tmp_order_element = my.order_element

                widget = my.get_widget(tmp_order_element)
                try:
                    widget.alter_order_by(search, direction)
                except AttributeError:
                    # NOTE: in case it's a comma separated element, direction applies for both columns
                    search.add_order_by(tmp_order_element, direction)

            my.show_retired_element = group_values.get("show_retired")
            if my.show_retired_element == "true":
                search.set_show_retired(True)

        
        # user chosen order is top priority
        if order:
            my.order_element = order
            if not values:
                direction = 'asc' 
                if my.order_element.find(" desc") != -1:
                    tmp_order_element = my.order_element.replace(" desc", "")
                    direction = 'desc'
                else:
                    tmp_order_element = my.order_element

                widget = my.get_widget(tmp_order_element)
                try:
                    widget.alter_order_by(search, direction)
                except AttributeError:
                    search.add_order_by(my.order_element, direction)

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
                    except ValueError:
                        pass
                limit = my.search_limit.get_stated_limit()

            my.chunk_num = my.kwargs.get("chunk_num")

            #print "init count: ", count
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

            # alter the search
            my.search_limit.set_search(search)
            my.search_limit.alter_search(search)
            

    def handle_search(my):
        '''method where the table handles it's own search on refresh'''
        if my.is_sobjects_explicitly_set():
            return

        if not my.is_refresh and my.kwargs.get("do_initial_search") in ['false', False]:
            return

        # if an expression exists, then this rules the search
        expression = my.kwargs.get('expression')
        if expression:
            if my.exp_sobjects:
                sobjects = my.exp_sobjects
            else:
                if my.search_key and my.search_key != "%s":
                    start_sobj = Search.get_by_search_key(my.search_key)
                else:
                    start_sobj = None

                sobjects = Search.eval(expression, start_sobj, list=True)
            my.items_found = len(sobjects)

            # re-create a search to satistfy the alter_search()
            # it's not efficient though, could be improved if Search.eval
            # returns a search instead
            

            # only do this alter_search if search_limit is visible
            if my.search_limit:
                search = Search(my.search_type)
                
                ids = SObject.get_values(sobjects, 'id')
                search.add_filters('id', ids)
                #search.add_enum_order_by('id', ids)

                if my.search_limit:
                    my.search_limit.set_search(search)
                my.alter_search(search)
                my.sobjects = search.get_sobjects()
                my.element_process_sobjects(search)
            else:
                my.sobjects = sobjects
                my.element_process_sobjects(None)

            return


        # don't set the view here, it affects the logic in SearchWdg
        from tactic.ui.app import SearchWdg
        filter_xml = ''
        if my.kwargs.get('filter'):
            filter_xml = my.kwargs.get('filter')
        
        # turn on user_override since the user probably would alter the saved search 
        limit = my.kwargs.get('search_limit')
        custom_search_view = my.kwargs.get('custom_search_view')
        if not custom_search_view:
            custom_search_view = ''

        if not my.search_wdg:
            my.search_wdg = my.kwargs.get("search_wdg")
        if not my.search_wdg:
            my.search_wdg = SearchWdg(search_type=my.search_type, state=my.state, filter=filter_xml, view=my.search_view, user_override=True, parent_key=None, limit=limit, custom_search_view=custom_search_view)

        search = my.search_wdg.get_search()
        if my.no_results:
            search.set_null_filter()

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
        for xx in filter_data.data:
            class_name =  xx.get('class_name')
            prefix = xx.get('prefix')
            if class_name:
                handler = Common.create_from_class_path(class_name)
                handler.alter_search(search)


        if my.parent_key and my.parent_key != "%s":
            parent = Search.get_by_search_key(my.parent_key)
            if not parent:
                my.sobjects = []
                my.items_found = 0
                return
            # TODO: this parent path is a bit of a hack to make tables that
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
        # allow widgets to alter the search
        #for widget in my.widgets:
        #    widget.alter_search(search)


        # MMS -
        # FIXME: provide an opportunity to process the sobjects
        if my.view == "terminal_report":
            my.process_sobjects()

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

    def get_aux_info(my):
        return my.aux_info


    def get_data_row_smart_context_menu_details(my):
        spec_list = [ { "type": "title", "label": 'Item "{display_label}"' }]
        if my.view_editable:
            edit_view = my.kwargs.get("edit_view")
            
            if not edit_view or edit_view == 'None':
                edit_view = "edit"

            spec_list.append( {
                "type": "action",
                "label": "Edit",
                "icon": IconWdg.EDIT,
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
                        //spt.app_busy.show(bvr.description, file);                   
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
                                kwargs = {mode: 'upload', checkin_mode: 'auto'};
                            }
                            else {
                                kwargs = {mode: 'upload'};
                            }
                            server.simple_checkin( search_key, context, file);
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
                    if (!context)
                        context = tbody.getAttribute("spt_icon_context");
                    if (!context)
                        context = "icon";

                    // set the form
                    spt.html5upload.set_form( $(bvr.upload_id) );
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
                                var kwargs = {mode: 'uploaded'};  
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
            bvr_cb["upload_id"] = my.upload_id
            spec_list.append( {
                "type": "action",
                "label": "Change Preview Image",
                "icon": IconWdg.PHOTOS,
                "bvr_cb": bvr_cb,
                "hover_bvr_cb": {
                    'activator_add_look_suffix': 'hilite',
                    'target_look_order': [
                        'dg_row_retired_selected', 'dg_row_retired', my.look_row_selected, my.look_row ] 
                    }
            } )


            bvr_cb2 = bvr_cb.copy()
            bvr_cb2["description"] = "Checking in new file ..."
            bvr_cb2["context"] = "publish"
            spec_list.append( {
                "type": "action",
                "label": "Check in New File",
                "upload_id": my.upload_id,
                "icon": IconWdg.PHOTOS,
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

                { "type": "action", "label": "Retire", "icon": IconWdg.RETIRE,
                    "enabled_check_setup_key" : "is_not_retired",
                    "hide_when_disabled" : True,
                    "bvr_cb": { 'cbjs_action': 'spt.dg_table.drow_smenu_retire_cbk(evt,bvr);' },
                    "hover_bvr_cb": { 'activator_add_look_suffix': 'hilite',
                                      'target_look_order': [ 'dg_row_retired_selected', 'dg_row_retired',
                                                             my.look_row_selected, my.look_row ] }
                },

                { "type": "action", "label": "Delete", "icon": IconWdg.DELETE,
                    "bvr_cb": { 'cbjs_action': 'spt.dg_table.drow_smenu_delete_cbk(evt,bvr);' },
                    "hover_bvr_cb": { 'activator_add_look_suffix': 'hilite',
                                      'target_look_order': [ 'dg_row_retired_selected', 'dg_row_retired',
                                                             my.look_row_selected, my.look_row ] }
                }])

        spec_list.extend( [

                { "type": "separator" },

                { "type": "action", "label": "Item Audit Log", "icon": IconWdg.CONTENTS,
                    "bvr_cb": { 'cbjs_action': "spt.dg_table.drow_smenu_item_audit_log_cbk(evt, bvr);" },
                    "hover_bvr_cb": { 'activator_add_look_suffix': 'hilite',
                                      'target_look_order': [ 'dg_row_retired_selected', 'dg_row_retired',
                                                             my.look_row_selected, my.look_row ] }
                },

                { "type": "title", "label": 'All Table Items' },

                { "type": "action", 
                    "label": "Save All Changes",
                    "icon": IconWdg.DB,
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


    def get_layout_version(my):
        return "1"


    def get_display(my):

        # FIXME: is this necessary - it was moved to the __init__
        my.view_attributes = my.config.get_view_attributes()

        # Handle security ... get overall sobject security access ...
        #
        # Different security types
        #
        # group: search_type, 
        #
        security = Environment.get_security()

        # check edit permission
        default_access = my.view_attributes.get('access')

        if not default_access:
            default_access = 'edit'

        project_code = Project.get_project_code()

        key = {
            'search_type': my.search_type,
            'project': project_code
        }

        my.edit_permission = security.check_access("sobject", key, "edit", default=default_access)

        # if a search key has been explicitly set without expression, use that
        expression = my.kwargs.get('expression') 
        matched_search_key = False
        if my.search_key:
            base_search_type = SearchKey.extract_base_search_type(my.search_key)
        else:
            base_search_type = ''
        if my.search_type == base_search_type:
            matched_search_key = True
        # if there is no parent_key and  search_key doesn't belong to search_type, just do a general search
        if my.search_key and matched_search_key and not expression:
            sobject = Search.get_by_search_key(my.search_key)
            
            my.sobjects = [sobject]
            my.items_found = len(my.sobjects)

        elif my.kwargs.get("selected_search_keys"):
            # DEPRECATED: selected_search_keys is deprecated, use search_keys
            # if this is provided then build the list of sobjects to show in table from the list
            # of search keys provided in this kwarg parameter value ...
            sel_skey_list = my.kwargs.get("selected_search_keys")
            for skey in sel_skey_list:
                sobj = Search.get_by_search_key( skey )
                my.sobjects.append( sobj )
            my.items_found = len(my.sobjects)

        elif my.kwargs.get("do_search") != "false":
            my.handle_search()


        mode = my.kwargs.get("mode") 


        # check if the view is editable before drawing smart context menu
        # NOTE: there is also access='deny' or 'allow' you can set
        view_editable = my.view_attributes.get("edit")
        if view_editable in ['false', False]:
            my.view_editable = False
        else:
            my.view_editable = True

        if my.is_refresh:
            top_wdg = Widget()
        else:
            top_wdg = my.top
            top_wdg.add_class("spt_table_top")
            top_wdg.add_class("spt_layout")

            # add a fudge factor to handle hidden row alignment
            if my.kwargs.get("__hidden__"):
                if mode == 'simple':
                    top_wdg.add_style("margin-top: -1px")
                else:
                    top_wdg.add_style("margin-top: -6px")
                    top_wdg.add_style("margin-right: -5px")


            save_inputs = my.kwargs.get("save_inputs")
            if save_inputs:
                top_wdg.add_attr("spt_save_inputs", save_inputs)
                #top_wdg.add_behavior( {
                #"type": "function",
                #'cbjs_action': '''
                #var parent = bvr.src_el.getParent(".spt_search_top");
                #var cousin = parent.getElement(".spt_search_filter");
                #return [cousin];
                #''')

                
            # this makes parent_key always available on refresh.. It's needed for inline insert to update parent
            my.kwargs['parent_key'] = my.parent_key
            my.set_as_panel(top_wdg)

            top_wdg.add_style("margin-left: 0px")
            top_wdg.set_id("%s_layout" % my.table_id)
            top_wdg.add_style("display: block")

            top_wdg.add_behavior( {
                'type': 'load',
                'cbjs_action': my.get_onload_js()
            } )
 

        if mode != "simple":
            #if mode == 'insert':
            #    my.kwargs['show
            #else:
            #    top_wdg.add( my.get_action_wdg() )

            if mode == 'insert':
                #my.kwargs['show_gear'] = "false"
                my.kwargs['show_search'] = "false"

            action_wdg = my.get_action_wdg()
            top_wdg.add( action_wdg )


        # this should be added for all modes to allow table editing
        # thru context menu
        info_div = my.get_context_menu_info_wdg()
        top_wdg.add(info_div) 

        # -- GROUP SPAN - this is to show hidden elements for ordering and
        # grouping
        group_span = SpanWdg()
        group_span.add_style("display: none")
        group_span.add_class("spt_table_search")
        group_span.add(my.get_group_wdg() )
        top_wdg.add(group_span)


        # allow generators to add widgets as needed
        new_widgets = []
        for i, widget in enumerate(my.widgets ):
            attrs = my.config.get_element_attributes(widget.get_name())
            gen_expr = attrs.get("generator")
            gen_list = attrs.get("generator_list")
            generator = widget.get_name()

            list = None
            if gen_expr:
                # TODO: this communication needs to be formalized.  Currently
                # this is used in MMS to generate employee columns for a
                # given supervisor
                vars = Container.get("Message:search_vars")
                parser = ExpressionParser()
                list = parser.eval(gen_expr, vars=vars)
            elif gen_list:
                list = gen_list.split("|")
                

            if list != None:
                import copy
                for result in list:
                    new_widget = copy.copy(widget)
                    new_widget.set_name(result)
                    new_widget.set_title( None )
                    new_widget.set_sobjects( my.sobjects )
                    new_widgets.append(new_widget)
                    new_widget.set_generator(generator)
                # FIXME: this should not be displayed???
                if not list:
                    new_widgets.append(widget)

            else:
                new_widgets.append(widget)
        my.widgets = new_widgets
        

        # set the state
        for i, widget in enumerate( my.widgets ):
            widget.set_state(my.state)


        table_width_set = False
        for i, widget in enumerate( my.widgets ):
            # set the type
            widget_type = my.config.get_type( widget.get_name() )
            widget.type = widget_type

            if not table_width_set and widget.width:
                table_width_set = True


        my.aux_wdg = my.get_aux_wdg()
        top_wdg.add( my.aux_wdg )

        top_wdg.add( my.search_container_wdg )

        # set up the table
        table = my.table
        if not table_width_set:
            table.set_max_width()



        # add a wrapper div around the table to be the parent container for the smart menus for the table
        table_wrapper_div = DivWdg()


        # set up hidden div to hold validation behaviors only for the edit widgets that have
        # validations configured on them ...
        #
        validations_div = DivWdg()
        validations_div.add_class("spt_table_validations")
        validations_div.add_styles("display: none;")

        table_wrapper_div.add(validations_div)


        table_wrapper_div.add(table)
        table_wrapper_div.add_class("spt_table_wrapper_div")

        # add in hidden arrows for column reorder (arrow left and right to indicate which side to reorder to)
        reorder_arrow_left = DivWdg()
        reorder_arrow_left.set_id( "dg_table_reorder_arrow_left" )
        reorder_arrow_left.add( "<img src='/context/themes/dark/images/column_reorder_arrow_left.png' />" )
        reorder_arrow_left.add_styles( "display: none; width: 15px; height: 14px; position: absolute;" )
        reorder_arrow_left.add_class("SPT_PUW")

        reorder_arrow_right = DivWdg()
        reorder_arrow_right.set_id( "dg_table_reorder_arrow_right" )
        reorder_arrow_right.add( "<img src='/context/themes/dark/images/column_reorder_arrow_right.png' />" )
        reorder_arrow_right.add_styles( "display: none; width: 15px; height: 14px; position: absolute;" )
        reorder_arrow_right.add_class("SPT_PUW")

        table_wrapper_div.add( reorder_arrow_left )
        table_wrapper_div.add( reorder_arrow_right )



        # add an upload_wdg
        from tactic.ui.input import Html5UploadWdg
        upload_wdg = Html5UploadWdg()
        table_wrapper_div.add(upload_wdg)
        my.upload_id = upload_wdg.get_upload_id()



        # will add data row/cell context menus next (to replace the context menu in the select box column)
        # add an upload_wdg
        menus_in = {
            'DG_HEADER_CTX': [ my.get_smart_header_context_menu_data() ],
            'DG_DROW_SMENU_CTX': [ my.get_data_row_smart_context_menu_details() ]
        }
        SmartMenu.attach_smart_context_menu( table_wrapper_div, menus_in, False )

        top_wdg.add(table_wrapper_div)


        table.set_id(my.table_id)
        table.add_style("display: table")
        table.set_attr("spt_view", my.view)
        table.set_attr("spt_search_type", my.search_type)
        my.search_class = my.kwargs.get('search_class')
        table.set_attr("spt_search_class", my.search_class)
        my.simple_search_view = my.kwargs.get('simple_search_view')
        table.set_attr("spt_simple_search_view", my.simple_search_view)

        table.add_behavior( { "type": "smart_drag",
                              "bvr_match_class": "SPT_DRAG_COLUMN_RESIZE",
                              'ignore_default_motion': 'false',
                              "cbjs_setup": 'spt.dg_table.resize_column_setup( evt, bvr, mouse_411 );',
                              "cbjs_motion": 'spt.dg_table.resize_column_motion( evt, bvr, mouse_411 );'
                             } )



        # add the header row
        table_header_row = table.add_row(css="maq_view_table_header")
        #table_header_row = table.add_row()
        table_header_row.add_style("height: 20px")


        # Table takes on the color of the background
        table_header_row.add_color("color", "color", +5)

        if my.kwargs.get("__hidden__"):
            table_header_row.add_gradient("background", "background", -5, -10)
        else:
            table_header_row.add_gradient("background", "background", -20)


        # prepend the row select widget
        my.show_row_select = my.kwargs.get("show_select")
        if my.show_row_select not in ['false', False]:
            my.show_row_select = True
        else:
            my.show_row_select = False
        if my.show_row_select:
            # row_select_wdg does not have a name
            row_select_wdg = RowSelectWdg(my.table_id)
            row_select_wdg.width = '30px'
        else:
            from pyasm.widget import PlaceHolderElementWdg
            row_select_wdg = PlaceHolderElementWdg()
            row_select_wdg.width = '0px'

        my.widgets.insert(0, row_select_wdg)
        #top_wdg.add(row_select_wdg.get_title() )

        # get all the attributes
        for widget in my.widgets:
            name = widget.get_name()
            if name and name != "None":
                attrs = my.config.get_element_attributes(name)
                my.attributes.append(attrs)

            else:
                my.attributes.append({})


        my.edit_permission_columns = {}

        # check the security for the elements in a config
        element_names = my.config.get_element_names()
        for i, widget in enumerate(my.widgets):
            element_name = widget.get_name()
            default_access = my.attributes[i].get('access')
            # set the width even for refresh mode
            width = my.attributes[i].get('width')
            widget.width = width
            widget.view_attributes = my.view_attributes

            if not default_access:
                default_access = 'edit'

            key = {
                'search_type': my.search_type,
                'key': element_name, 
                'project': project_code

            }
            if not security.check_access('element',key,"view",default=default_access):
                my.widgets.remove(widget)

            elif not my.edit_permission or not security.check_access('element',key,"edit",default=default_access):
                my.edit_permission_columns[element_name] = False
            else:
                my.edit_permission_columns[element_name] = True


        # set the sobjects to all the widgets then preprocess
        for widget in my.widgets:
            widget.set_sobjects(my.sobjects)
            # NOTE: This sets up a circular reference
            widget.set_parent_wdg(my)

            # preprocess the elements
            widget.preprocess()
 
            

        # TEST: fixed header
        '''
        new_table = Table()
        top_wdg.add(new_table)        
        new_table_tr = new_table.add_row(css="maq_view_table_header")
        new_table_tr.add_color("color", "color", +5)
        new_table_tr.add_gradient("background", "background", -20)
        new_table.add_style("width: 850px")
        new_table.add_style("position: fixed")
        #new_table.add_style("top: 180px")
        new_table.add_style("top: 0px")
        new_table.add_style("left: 220px")
        for i, widget in enumerate(my.widgets):
            if not widget.is_in_column():
                continue
            th = my.add_header_wdg(new_table, widget, i, num_wdg )
        '''

        layout_version = my.get_layout_version() 

        # build all of the cell edits
        edit_wdgs = {}
        if my.edit_permission and my.view_editable:
            for j, widget in enumerate(my.widgets):
                name = widget.get_name()
                if not name:
                    continue

                # first check if the widget is actually editable
                editable = widget.is_editable()
               
                if editable == True:
                    editable = my.attributes[j].get("edit")
                    editable = editable != "false"
                elif editable == 'optional':
                    editable = my.attributes[j].get("edit")
                    editable = editable == "true"


                if j != 0 and editable == True:
                    edit = CellEditWdg(x=j, element_name=name, search_type=my.search_type, state=my.state, layout_version=layout_version)
                    edit_wdgs[name] = edit
                    # now set up any validations on this edit cell,
                    # if any have been configured on it
                    from tactic.ui.app import ValidationUtil
                    v_util = ValidationUtil( widget=edit.get_display_wdg() )
                    validation_bvr = v_util.get_validation_bvr()
                    if validation_bvr:
                        v_div = DivWdg()
                        v_div.add_class("spt_validation_%s" % name)
                        v_div.add_behavior( validation_bvr )
                        validations_div.add( v_div )




        # add all of the headers
        num_wdg = len(my.widgets)
        for i, widget in enumerate(my.widgets):
            if not widget.is_in_column():
                continue

            name = widget.get_name()
            edit_wdg = edit_wdgs.get(name)
            if edit_wdg:
                edit_wdg = edit_wdg.get_display_wdg()

            th = my.add_header_wdg(table, widget, i, num_wdg, edit_wdg )

            # give the opportunity for widgets to put in global
            # behaviors
            widget.handle_layout_behaviors(my.table)       






        # add the insert and edit row dummy sobjects
        empty_sobject = SearchType.create(my.search_type)
        my.sobjects.insert(0, empty_sobject)
        # add in default values set in the config
        # FIXME: not really sure if this is the best way to do this?
        # This should probably be formalized somehow
        for name, edit_wdg in edit_wdgs.items():
            display_wdg = edit_wdg.get_display_wdg()
            default = display_wdg.get_option("default")
            # FIXME: this likely is not the place for this, but this check
            # is placed here for a default of "now" for a calendar widget
            if display_wdg.__class__.__name__ == 'CalendarInputWdg' \
                    and default == 'now':
                import datetime
                default = datetime.datetime.now()
            if default:
                empty_sobject.set_value(name, default)

        my.sobjects.insert(0, empty_sobject)


        # Test adding double widgets
        new_widgets = []
        new_attributes = []
        for i, widget in enumerate(my.widgets):
            try:
                num_cols = widget.get_num_cols()
            except:
                num_cols = 1

            attributes = my.attributes[i]

            for j in range(0, num_cols):
                new_widgets.append(widget)
                new_attributes.append(attributes)
        my.widgets = new_widgets
        my.attributes = new_attributes
                



        # get the color maps
        color_config = WidgetConfigView.get_by_search_type(my.search_type, "color")
        color_xml = color_config.configs[0].xml
        color_maps = {}
        #print color_xml.to_string()
        for widget in my.widgets:
            name = widget.get_name()
            xpath = "config/color/element[@name='%s']/colors" % name
            text_xpath = "config/color/element[@name='%s']/text_colors" % name
            bg_color_node = color_xml.get_node(xpath)
            bg_color_map = color_xml.get_node_values_of_children(bg_color_node)

            text_color_node = color_xml.get_node(text_xpath)
            text_color_map = color_xml.get_node_values_of_children(text_color_node)
            
            # use old weird query language
            query = bg_color_map.get("query")
            query2 = bg_color_map.get("query2")
            if query:
                bg_color_map = {}

                search_type, match_col, color_col = query.split("|")
                search = Search(search_type)
                sobjects = search.get_sobjects()

                # match to a second atble
                if query2:
                    search_type2, match_col2, color_col2 = query2.split("|")
                    search2 = Search(search_type2)
                    sobjects2 = search2.get_sobjects()
                else:
                    sobjects2 = []

                for sobject in sobjects:
                    match = sobject.get_value(match_col)
                    color_id = sobject.get_value(color_col)

                    for sobject2 in sobjects2:
                        if sobject2.get_value(match_col2) == color_id:
                            color = sobject2.get_value(color_col2)
                            break
                    else:
                        color = color_id


                    bg_color_map[match] = color

            color_maps[name] = bg_color_map, text_color_map


        from tactic.ui.table import SObjectGroupUtil
        group_util = SObjectGroupUtil()


        # handle the case with no results (first 2 sobjects are insert and edit)
        #if False:
        if len(my.sobjects) <= 2:
            tbody = table.add_tbody()
            tbody.add_class("spt_empty_tbody")
            tr, td = table.add_row_cell()
            #td.add_style("border: solid 1px #5a5e5d")
            td.add_style("border-style: solid")
            td.add_style("border-width: 1px")
            td.add_color("border-color", "table_border", default="border")
            td.add_color("color", "color")
            td.add_color("background", "background", -7)

            if not my.is_refresh and my.kwargs.get("do_initial_search") in ['false', False]:
                msg = DivWdg("<i>- Initial search set to no results -</i>")
            else:
                msg = DivWdg("<i>- No items found -</i>")
            msg.add_style("text-align: center")
            msg.add_style("font-weight: bold")
            msg.add_style("margin: 10px")
            msg.add_style("font-size: 1.0em")
            td.add(msg)

            tbody = table.close_tbody()



        current_group_id = None

        # Add the data rows
        #
        # Note: there are some special rows at the beginning.  These rows
        # correspond to special functionality of the table and are generally
        # hidden
        #
        # row #1: hidden row, which provides the template widgets to create
        #   newly inserted rows
        # row #2: contains all of the templates for editability of the cells
        #
        for row, sobject in enumerate(my.sobjects):
            if mode == 'tbody' and row in [my.INSERT_ROW, my.EDIT_ROW]:
                continue
            # with access rule and process_sobjects(), it's forseeable to get a None sobject passed in
            if not sobject:
                continue
            # Add a grouping element

            if my.group_element and row not in [my.INSERT_ROW, my.EDIT_ROW]:

                if my.group_element in [True, 'True']:
                    widget = my.get_widget(my.order_element)
                elif my.group_element:
                    widget = my.get_widget(my.group_element)

                    # if the widget is not in the view, then get it from
                    # the config
                    if not widget:
                        widget = my.config.get_display_widget(my.group_element)
                        widget.set_sobjects(my.sobjects)
                else:
                    widget = None

               
                if widget and widget.is_groupable():
                    widget.set_current_index(row)
                    group_util.set_sobject(sobject)
                    group_util.set_widget(widget)

                    group_wdg = group_util.get_group_wdg()
                    if group_wdg:

                        # add a bottom element.  We need to put row-1 here
                        # because we are already at the next row
                        my.add_group_bottom(table, row-1)
                        my.group_sobjects = []


                        tbody = table.add_tbody()
                        tbody.add_class('spt_table_group')
                        if my.group_element == True:
                            tbody.add_attr('spt_element_name', my.order_element)
                        else:
                            tbody.add_attr('spt_element_name', my.group_element)
                        border = tbody.get_color("border")
                        tbody.add_style('border-left: solid %s 1px' % border)
                        tbody.add_style('border-right: solid %s 1px' % border)
                        tbody.add_style('border-bottom: solid %s 1px' % border)
                        tbody.add_class("hand")

                        tr, td = table.add_row_cell()

                        #swap = SwapDisplayWdg()
                        #td.add(swap)
                        #swap.add_style("float: left")


                        td.add(group_wdg)
                        tr.add_color("background", "background", -25)
                        tr.add_color("color", "color")

                        table.close_tbody()

                        # provide the opportunity for the widget to handle
                        # the grouping tbody, tr and td
                        widget.handle_group_table(table, tbody, tr, td)

                        current_group_id = random.randint(0, 100000)
                        td.add_behavior( {
                        'type': 'click_up',
                        'current_group_id': current_group_id,
                        'cbjs_action': '''
                        var table = bvr.src_el.getParent(".spt_table");
                        var rows = table.getElements(".spt_group_" + bvr.current_group_id);
                        for (var i = 0; i < rows.length; i++) {
                            spt.toggle_show_hide( rows[i] );
                        }
                        '''
                        } )


                    # add in a new sobjct to this group
                    my.group_sobjects.append(sobject)
               

            tbody = table.add_tbody()
            tbody.add_class("spt_table_tbody")
            if current_group_id:
                tbody.add_class("spt_group_%s" % current_group_id)

            # add the refresh attibute
            refresh = my.view_attributes.get("refresh")
            tbody.add_attr("spt_refresh", refresh)

            tbody.set_attr("spt_show_select", my.kwargs.get("show_select"))

            #search_key = SearchKey.get_by_sobject(sobject)
            search_key = SearchKey.get_by_sobject(sobject, use_id=True)

            # add a unique id
            if sobject.is_insert():
                # this is not exactly unique.. Edit ROW uses the same id
                row_id = "%s_INSERT_ROW" % (my.table_id)
            else:
                row_id = "%s|%s" % (my.table_id, search_key)
            tbody.set_id(row_id)


            # add a refresh listener
            behavior = {
                'type': 'listen',
                'event_name': 'update|%s' % search_key,
                'cbjs_action': 'spt.panel.refresh(bvr.src_el)'
                
                #'cbjs_action': 'spt.panel.refresh("%s")' % row_id
            }
            tbody.add_behavior(behavior)

            #tbody.add_style("border: solid blue")
            tbody.add_style("display", "table-row-group")

            display_value = sobject.get_display_value(long=True)
            icon_context = sobject.get_icon_context()

            # set some attributes
            tbody.add_attr("spt_class_name", "tactic.ui.panel.OldTableLayoutWdg")
            tbody.add_attr("spt_search_type", sobject.get_base_search_type())
            tbody.add_attr("spt_search_key", search_key)
            tbody.add_attr("spt_display_value", display_value)
            tbody.add_attr("spt_view", my.view)
            tbody.add_attr("spt_table_id", my.table_id)
            tbody.set_attr("spt_mode", "tbody")
            tbody.set_attr("spt_parent_key", my.parent_key)
            tbody.add_attr("spt_icon_context", icon_context)

            # this is needed for updating a row for a brand new search type where a config is not defined yet
            tbody.set_attr("spt_element_names", ','.join(my.element_names))

            my.row_ids[search_key] = row_id



            if row in [my.INSERT_ROW, my.EDIT_ROW]:
                tbody.add_style("display: none")
                #pass
            if row == my.INSERT_ROW:
                tbody.add_class("spt_insert_tbody")
            if row == my.EDIT_ROW:
                tbody.add_class("spt_edit_tbody")


            # Add the previous row.  Widgets have the opportunity to add
            # to the previous row.
            #my._add_prev_row(table, row)


            # add the main row
            tr = table.add_row()

            # Introduce a concept of protected rows for plugins
            # FIXME: row editable does not work yet
            my.current_sobject = sobject
            my.handle_tr(tr)

            tr.add_class("spt_table_tr")
            tr.add_class("spt_table_row")
            tr.add_attr("spt_search_key", sobject.get_search_key(use_id=True) )

            # Set the data row TR element as the local activator for the Data Row Smart Context Menu
            SmartMenu.assign_as_local_activator( tr, 'DG_DROW_SMENU_CTX' )


            # determine if the client OS is a TOUCH DEVICE
            web = WebContainer.get_web()
            is_touch_device = web.is_touch_device()


            # Set the row look and behaviors for hover and select based on whether or not the row is retired or not
            if sobject.get_value("s_status", no_exception=True) == "retired":
                tr.add_looks( 'dg_row_retired' )

                # only do row highlight if we are not on a touch device (no mouse hover on touch device)
                if not is_touch_device:
                    tr.add_behavior( {'type': 'hover', 'add_look_suffix': 'hilite',
                                        'target_look_order': [ 'dg_row_retired_selected', 'dg_row_retired' ] } )
                tr.add_behavior( {'type': 'select', 'add_looks': 'dg_row_retired_selected'} )
            else:

                tr.add_looks( my.look_row )

                palette = tr.get_palette()


                # only do row highlight if we are not on a touch device (no mouse hover on touch device)
                if not is_touch_device:
                    #tr.add_behavior( {
                    #    'type': 'hover',
                    #    'add_look_suffix': 'hilite',
                    #    'target_look_order': [ my.look_row_selected, my.look_row ]
                    #} )

                    tr.add_behavior( {
                        'type': 'hover',
                        'cb_set_prefix': 'spt.mouse.table_layout_hover',
                        'hover_class': 'spt_table_tr',
                        'add_color_modifier': -5,
                    } )




                #tr.add_behavior( {
                #    'type': 'select',
                #    'add_looks': my.look_row_selected,
                #} )

                tr.add_color("color", "color")

                # selection colors
                hilite = palette.color("background", -30)
                tr.add_behavior( {
                    'type': 'select',
                    'add_color': hilite
                } )

                # set the background color and remember it
                if row % 2:
                    background = tr.add_color("background", "background")
                else:
                    #background = tr.add_color("background", "background", -2)
                    background = tr.add_color("background", "background", -7)
                tr.add_attr("spt_background", background)



            # make sure the edit and insert rows are not displayed and have
            # the appropriate tags
            if row == my.INSERT_ROW:
                tr.add_class("spt_insert_row")
                #tr.add_style("display: none")
            if row == my.EDIT_ROW:
                tr.add_class("spt_edit_row")
                #tr.add_style("display: none")

            tr.add_style('min-height: %spx' % my.min_cell_height)
            tr.add_style('height: %spx' % my.min_cell_height)
            tr.add_style('vertical-align: top')


            row_idx = row * 2

            for j, widget in enumerate(my.widgets):
                widget.set_current_index(row)

                if not widget.is_in_column():
                    continue

                td = table.add_cell()
                td.add_class("spt_table_td")
                if j == 0:
                    td.add_color("background-color", "background", -10)

                name = widget.get_name()
                td.add_attr("spt_element_name", name)

                # hide this row select column
                if j == 0 and not my.show_row_select:
                    td.add_style("display: none")
                    continue

                edit = None
                editable = my.attributes[j].get("edit")
                if editable == None:
                    editable = widget.is_editable()
                else:
                    editable = editable != "false"

                if my.edit_permission_columns.get(name) == False:
                    editable = False

                edit = edit_wdgs.get(name)
                if j != 0 and edit and my.edit_permission and my.view_editable and editable:
                        
                    edit.set_sobject(sobject)
                    values = edit.get_values()
                    column = edit.get_column()
                    value = values.get('main')
                    if not value:
                        value = ''
                    # just put in the first value for now
                    if type(value) in types.StringTypes:
                        value = value.replace('"', '&quot;')


                    # FIXME FIXME FIXME FIXME FIXME FIXME FIXME FIXME FIXME FIXME FIXME FIXME FIXME
                    # FIXME: big fat hack to get mms working
                    if sobject.get_base_search_type() == 'MMS/subtask' and widget.get_name() == 'discipline':
                        value = Search.eval("@GET(MMS/subtask_product.MMS/product_type.MMS/discipline.id)", sobject)
                        #print 'WARNING: Setting hardcoded input value!!!!', value


                    #if widget.__class__.__name__ in [ "ForeignKeyElementWdg", "ExpressionElementWdg" ]:
                        # provide the td to this widget to that it can set the 'spt_input_value' for this td
                        # within its '.get_display()' method, where its value is actually obtained ...
                    #    widget.set_td( td )
                    td.add_attr("spt_input_value", value)
                    td.add_attr("spt_input_column", column)

                    td.add_attr("spt_input_type", edit.get_element_type())
                    
                    # add dependent value
                    #dependent_attrs = edit.get_dependent_attrs()
                    #if dependent_attrs:
                    #    dependent_values = [sobject.get_value(x) for x in dependent_attrs]
                    #    td.add_attr("spt_dependent_value", ','.join(dependent_values))
                    behavior = {
                        'type': 'click_up',
                        'mouse_btn': 'LMB',
                        'cbjs_action': 'spt.dg_table.select_cell_for_edit_cbk(evt, bvr)',
                        'table_id': my.table_id,
                        #'col': j,
                        #'row': row
                    }
                    td.add_behavior(behavior)
                    td.add_class("SPT_CELL_EDIT");
                    td.set_attr("spt_row", row);
                    td.set_attr("spt_col", j);

                    # indicator that a cell is editable
                    td.add_event( "onmouseover", "$(this).setStyle('background-image', " \
                                      "'url(/context/icons/silk/page_white_edit.png)')" )
                    td.add_event( "onmouseout",  "$(this).setStyle('background-image', '')")
                    td.add_styles( "background-repeat: no-repeat; background-position: bottom right")


                # add the widget - have to use buffer display because the
                # same widget is used for all the rows
                if row == my.INSERT_ROW:
                    if j!= 0 and not (my.edit_permission and my.view_editable and editable):
                        # show that this insert field is not editable
                        td.add_color("background-color", "background", [5,-5,-5])
                        td.add_event( "onmouseover", "$(this).setStyle('background-image', 'url(/context/icons/custom/no_edit.png)')" )
                        td.add_event( "onmouseout",  "$(this).setStyle('background-image', '')")
                        td.add_styles( "background-repeat: no-repeat; background-position: bottom right")




                    else:
                        # if there is a default specified, then set the insert
                        # column to have a changed value
                        edit = edit_wdgs.get(name)
                        if edit:
                            default = edit.get_display_wdg().get_option("default")
                            if default:
                                td.add_class("spt_value_changed")


                if row == my.EDIT_ROW:
                    if edit:
                        td.add( edit.get_buffer_display() )
                        td.add_attr("spt_input_type", edit.get_element_type())

                        # MMS
                        # FIXME: add this to the options
                        project_code = Project.get_project_code()
                        if project_code == 'MMS':
                            if widget.get_name() == "subtask_letter":
                                td.add_attr("spt_edit_script", "643MMS")
                            elif widget.get_name() == "subtask_labor":
                                td.add_attr("spt_edit_script", "661MMS")
                            elif widget.get_name() == "shift":
                                td.add_attr("spt_edit_script", "804MMS")

                    else:
                        td.add( "&nbsp;" )
                else:

                    # actually draw the widget

                    div = DivWdg()
                    td.add(div)

                    div.add_style('padding', '3px')
                    #div.add_style("width: 100%")
                    div.add_style("height: 100%")
                    if my.widgets[j-1].get_name() == widget.get_name():
                        widget.column_index = 1
                    else:
                        widget.column_index = 0

                    # handle word wrap
                    is_word_wrap = False
                    if is_word_wrap:
                        buffer = widget.get_buffer_display()

                        if isinstance(widget, SimpleTableElementWdg):
                            td.add_attr('title', buffer)
                            if len(buffer) > 50:
                                buffer = buffer[:50]
                                buffer = "%s ..." % buffer

                        inner = DivWdg()
                        div.add(inner)
                        div.add_style('width', '1px')
                        #div.add_style('width', '100%')
                        td.add_style('overflow: hidden')
                        inner.add_style("width: 100%")
                        inner.add_style("white-space: nowrap")

                        inner.add( buffer )
                    else:
                        existing_state = widget.get_state()
                        if existing_state == None:
                            existing_state = {}
                        existing_state['search_key'] = search_key
                        existing_state['parent_key'] = my.parent_key
                        widget.set_state(existing_state)

                        # ensure that the errors is trapped in the cell
                        try:
                            div.add( widget.get_buffer_display() )
                        except Exception, e:
                            # fail with controlled error
                            print "Error: ", e
                            # print the stacktrace
                            tb = sys.exc_info()[2]
                            stacktrace = traceback.format_tb(tb)
                            stacktrace_str = "".join(stacktrace)
                            print "-"*50
                            print stacktrace_str
                            print e
                            print "-"*50
                            
                            from pyasm.widget import ExceptionWdg
                            error_wdg = ExceptionWdg(e)
                            div.add(error_wdg)
                          
                            # reset the top_layout
                            WidgetSettings.set_value_by_key('top_layout','')
                    

  

    
                td.add_class('cell_left')
                td.add_color('border-color', 'table_border', default='border')
                #td.add_style("border: none")
                td.set_attr("col_idx", j*2)



                # add a color based on the color map if color is not set to false
                disable_color = my.attributes[j].get("color") == 'false'
                bg_color = None
                text_color = None

                if not disable_color:
                    try:
                        widget_value = widget.get_value()
                        if not isinstance(widget_value, basestring):
                            widget_value = str(widget_value)
                        bg_color_map, text_color_map = color_maps.get(name)
                        if bg_color_map:
                            bg_color = bg_color_map.get(widget_value)
                            if bg_color:
                                td.add_style("background-color", bg_color)
                        if text_color_map:
                            text_color = text_color_map.get(widget_value)
                            if text_color:
                                td.add_style("color", text_color)
                    except Exception, e:
                        print 'WARNING: problem when getting widget value for color mapping on widget [%s]: ' % widget, "message=[%s]" % e.message.encode('utf-8')




                # check for any validation scripts
                # QUESTION: is this used anymore?
                validate_path = widget.get_option("validate")
                if validate_path:
                    td.add_attr("spt_validate_path", validate_path)
                validate_regex = widget.get_option("validate_regex")
                if validate_regex:
                    td.add_attr("spt_validate_regex", validate_regex)
                validate_msg = widget.get_option("validate_msg")
                if validate_msg:
                    td.add_attr("spt_validate_msg", validate_msg)



                    
                

                # provide an opportunity for widgets to affect the table
                widget.handle_tr(tr)
                widget.handle_td(td)


                # add an extra cell for resizing
                td = table.add_cell(css="cell_right")
                td.add_color('border-color', 'table_border', default='border')
                #td.add_style("border: none")

                # add the css that is used on the td
                try:
                    widget._add_css_style(td, 'css_')
                except:
                    pass
 
                td.set_attr("col_idx", (j*2) + 1)


                if j == 0 and not my.show_row_select:
                    td.add_style("display: none")

                # allow resize except for first column (the select box column)
                if j > 0:
                    td.add_class("SPT_DRAG_COLUMN_RESIZE")
                    td.add_styles("cursor: col-resize;")

                if bg_color:
                    td.add_style("background-color: %s" % bg_color)




            # add the hidden rows
            my._add_hidden_rows(table)

            # close the surrounding tbody
            table.close_tbody()

            # if we are in tbody mode, just return the tbody
            if mode == "tbody":
                return tbody


            my.tbodies.append(tbody)


      
        # get the desired limit
        if my.search_limit:
            limit = my.search_limit.get_stated_limit()
        else:
            limit = 20


        my.chunk_iterations = (limit-1) / my.chunk_size
        if my.chunk_iterations:
            if my.chunk_num == 0:
                behavior = {
                    'type': 'load',
                    'cbjs_action': '''
                    setTimeout(function() {
                    var server = TacticServerStub.get();
                    var widget_class = 'tactic.ui.panel.OldTableLayoutWdg';
                    var args = {
                        search_type: '%s',
                        view: '%s',
                        search_view: '%s',
                        mode: 'chunk',
                        do_search: 'true',
                        table_id: '%s'
                    };


                    var iterations = %s;
                    var chunk_limit = %s;
                    var table = bvr.src_el;
                    var top = table.getParent(".spt_view_panel");
                    var json_values = {};
                    if (top) {
                        search_wdg = top.getElement(".spt_search");
                        var json_values = spt.dg_table.get_search_values(search_wdg);
                    }
                    for( var c=1; c < iterations+1; c++ ) {
                        args['chunk_num'] = c;
                        args['chunk_limit'] = chunk_limit;
                        var msg = "Getting %s more entries ("+c+" of "+iterations+")";
                        spt.app_busy.show("Searching", msg);
                        var html = server.get_widget(widget_class, {args:args, values: json_values});
                        var tmp = document.createElement("div");
                        spt.behavior.replace_inner_html(tmp, html);
                        var children = tmp.getElements(".spt_table_tbody");
                        var length = children.length;
                        if (length <= 2 ) {
                            break;
                        }
                        for (var i = 0; i < children.length; i++) {
                            table.appendChild( children[i] );
                        }
                        //main.appendChild(tmp);

                        // check for cancel
                        //if (spt.app_busy.is_cancelled() == true)  {
                        //    break;
                        //}

                    }
                    spt.app_busy.hide();
                    }, 10);

                    ''' % (my.search_type, my.view, my.search_view, my.table_id, my.chunk_iterations, limit, my.chunk_size),
                }
                #print behavior
                table.add_behavior( behavior )
            else:
                widget = HtmlElement("table")
                for tbody in my.tbodies:
                    widget.add(tbody)
                return widget

        # add last group bottom
        if my.group_element and row not in [my.INSERT_ROW, my.EDIT_ROW]:
            my.add_group_bottom(table, my.group_sobjects)

        my.add_table_bottom(table)

        tr.add_style("border: solid 1px %s" % tr.get_color("table_border", default="border"))


        return top_wdg




    def add_table_bottom(my, table):

        # add in a bottom row
        all_null = True
        bottom_wdgs = []
        for widget in my.widgets:
            bottom_wdg = widget.get_bottom_wdg()
            bottom_wdgs.append(bottom_wdg)
            if bottom_wdg:
                all_null = False



        if not all_null:
            tbody = table.add_tbody()
            tbody.add_class('spt_table_bottom')
            border_color = tbody.add_color("border-color", "border")
            tbody.add_style("border: solid 1px %s" % border_color)
            tbody.add_color("color", "color")

            tr = table.add_row()
            tr.add_color("background", "background", -20)

            for i, bottom_wdg in enumerate(bottom_wdgs):
                element_name = my.widgets[i].get_name()
                td = table.add_cell()
                td.add_class("spt_table_td")
                td.add_attr("spt_element_name", element_name)
                div = DivWdg()
                div.add_style("min-height: 20px")
                td.add(div)
                if bottom_wdg:
                    div.add(bottom_wdg)
                else:
                    div.add("")

                div.add_style("margin-right: 7px")

                # add the resize
                td = table.add_cell()
                #td.add_style("background-color: #333")
                td.add_class("SPT_DRAG_COLUMN_RESIZE")
                td.add_styles("cursor: col-resize;")


            table.close_tbody()




    def add_group_bottom(my, table, row):
        if row in [my.INSERT_ROW, my.EDIT_ROW]:
            return

        # add in a bottom row
        all_null = True
        bottom_wdgs = []
        for j, widget in enumerate(my.widgets):
            bottom_wdg = widget.get_group_bottom_wdg(my.group_sobjects)
            bottom_wdgs.append(bottom_wdg)
            if bottom_wdg:
                all_null = False


        if not all_null:
            tbody = table.add_tbody()
            tbody.add_class('spt_table_bottom')
            #tbody.add_style("border: solid 1px #5a5e5d")

            tr = table.add_row()
            #tr.add_style("border: solid 1px %s" % tr.get_color("table_border", default="border"))
            tr.add_color("background", "background", -10)
            tr.add_color("color", "color")

            for i, bottom_wdg in enumerate(bottom_wdgs):
                element_name = my.widgets[i].get_name()
                td = table.add_cell()
                td.add_class("spt_table_td")
                td.add_attr("spt_element_name", element_name)
                div = DivWdg()
                div.add_style("min-height: 20px")
                td.add(div)
                if bottom_wdg:
                    div.add(bottom_wdg)
                else:
                    div.add("")

                div.add_style("margin-right: 7px")

                # add the resize
                td = table.add_cell()
                td.add_class("SPT_DRAG_COLUMN_RESIZE")
                td.add_styles("cursor: col-resize;")


            table.close_tbody()





    def add_header_wdg(my, table, widget, widget_idx, num_wdg, edit_wdg):

        # if show_row_select is false, then we do not display this row
        if not my.show_row_select and widget_idx == 0:
            th = table.add_header()
            th.add_style("display: none")
            th = table.add_header()
            th.add_style("display: none")
            return
        

        element_name = widget.get_name()
        
        # create and id header
        th = table.add_header()
        th.add_class("spt_table_th")
        

        # add the order by icon
        th.add_style("vertical-align: top")
        #my.vertical_text = True
        if my.vertical_text:
            #th.add_styles('-moz-transform: rotate(270deg); writing-mode: tb-rl; text-align: right; height: 140px;')
            pass

        # DEPRECATED
        #if widget_idx != 0:
        #    th.add_style("padding-left: 3px")

        width = widget.width
        autofit = my.view_attributes.get('autofit')
        if width:
            th.add_style("width: %s" % width)
           
        cell_idx = widget_idx * 2

        if my.kwargs.get("mode") == "insert" and element_name:
            # FIXME: centralize this
            search = Search(my.search_type)

            info = search.get_column_info().get(element_name)
            if info:
                is_nullable = info.get('nullable')
            
                if not is_nullable:
                    required_div = DivWdg()
                    required_div.add_style("height: 0px")
                    required_div.add_style("color: red")
                    required_div.add_style("position: relative")
                    required_div.add_style("text-align: right")
                    required_div.add("*")
                    th.add(required_div)

        if widget_idx > 0:
            th.set_attr('SPT_ACCEPT_DROP', 'DgTableColumnReorder')

        # add the content
        div = DivWdg()
        th.add(div)

        div.add_styles( "padding-top: 4px; padding-bottom: 4px; " \
                        "background-repeat: no-repeat; background-position: top center;" )

        sortable = my.attributes[widget_idx].get("sortable") != "false"
        if widget_idx != 0 and sortable:
            if my.order_element == element_name:
                div.add_styles("background-image: url(/context/icons/common/order_array_down_1.png);")
            elif my.order_element == "%s desc" % element_name:
                div.add_styles("background-image: url(/context/icons/common/order_array_up_1.png);")

        if not my.vertical_text:
            # FIXME: little bit hackery because vertical align doesn't work as
            # expected on divs
            t = Table()
            t.add_style("margin-top: -8px")
            t.add_color("color", "color")
            t.add_style("font-weight: bold")
            t.add_style("height: 100%")
            t.add_style("width: 100%")
            th.add(t)
            t.add_row()
            td = t.add_cell()
            td.add_style('overflow: hidden')

            div = DivWdg()
            td.add(div)
            div.add_style("width: 1px")

            inner = DivWdg()
            inner.add_style("padding-left: 2px")
            div.add(inner)
            inner.add_style("width: 100%")
            inner.add(widget.get_title())
            inner.add_style("white-space: nowrap")

        else:
            # not sure what to do about vertical text!!
            div.add( widget.get_title() )

        div.add_class( "SPT_DTS" )



        # setup each header cell (except the select box column) as a smart context menu activator for the
        # 'DG_HEADER_CTX' sub-set of smart menus for the table ...
        # 
        if widget_idx != 0:
            #th.set_attr("spt_element_name", element_name)
            SmartMenu.assign_as_local_activator( th, 'DG_HEADER_CTX' )

            if widget.is_groupable():
                # embed info in the TH for whether or not the column is groupable
                th.set_attr("spt_widget_is_groupable","true")


            #if widget.has_related():
            try:
                if edit_wdg and edit_wdg.get_related_type():
                    #print "RT [%s]", edit_wdg.get_related_type(), edit_wdg.name
                    th.set_attr("spt_widget_has_related","true")
                    th.set_attr("spt_related_type",edit_wdg.get_related_type())
            except:
                pass

            if widget.is_sortable():
                # embed info in the TH for whether or not the column is sortable
                th.set_attr("spt_widget_is_sortable","true")

            if widget.is_searchable():
                # embed info in the TH for whether or not the column is locally searchable
                th.set_attr("spt_widget_is_searchable","true")
                th.set_attr("spt_searchable_search_type", widget.get_searchable_search_type())

        # provide an opportunity for the widget to affect the header
        widget.handle_th(th, cell_idx)

        # this comes after handle_th in case it needs to override the min-width: 20px default
        # make sure if a width is set, it will extend outside the client width of the table
        if width and autofit =='false':
            th.add_style("min-width: %s" % width)


        header_option_wdg = widget.get_header_option_wdg()
        if header_option_wdg:
            my.handle_header_option_wdg(th, header_option_wdg)


        th.add_class('cell_left header_cell_main')
        #th.add_color("border-color", "border", -15)
        #th.add_color('border-color', 'table_border', default='border')
        th.add_color('border-color', 'background', -15)
        th.add_class("SPT_DTS")
        th.set_attr("col_idx", str(cell_idx))
        th.set_attr("spt_element_name", element_name)
        # for Local Search
        th.set_attr("spt_display_class", widget.__class__.__name__)
        

        th.set_attr("selected", "no")

        # Now specify that the column header will accept a drop from a draggable header for column re-ordering ...
        #
        # NOTE: the SPT_ACCEPT_DROP attribute can specify more than one drop code in its string value ...
        #       to accept more than one drop code, separate multiple codes with commas. Also note that
        #       the convention for a drop code is single camel-case word with no special characters
        #

        # Add column re-order for all columns except first one (the row select column) ... Also only add the
        # ability to accept a re-order for columns except row select column
        if widget_idx > 0:

            # Add an overloaded 'drag' behavior ... Drag and Drop behavior for column re-ordering functionality using
            # click drag LMB, but also Click behavior for ordering the column using straight LMB click
            # (NO more SHIFT+LMB on column header to drag!)
            behavior = {
                "type": 'drag',
                "drag_el": 'drag_ghost_copy',
                "drop_code": 'DgTableColumnReorder',   # can only specify single drop code for each drag behavior
                "cb_set_prefix": "spt.dg_table.drag_header_for_reorder",
                "cbjs_action_onnomotion": ";"
            }

            th.add_behavior(behavior)

            th.add_behavior( {
                'type': 'double_click',
                'cbjs_action': '''
                bvr.src_el.setStyle("width", "");
                '''
            } )

        try:
            generator = widget.get_generator()
            if generator:
                th.add_attr("spt_generator_element", generator)
        except AttributeError, e:
            print "WARNING: class [%s] does not have get_generator() method" % widget.__class__.__name__



        # now add the resize for the cell ...
        th = table.add_header(css="cell_right")
        #th.add_color("border-color", "border", -15)
        #th.add_color('border-color', 'table_border', default='border')
        th.add_color('border-color', 'background', -15)
        th.set_attr('col_idx', str(cell_idx+1))


        th.add_behavior( {
        'type': 'hover',
        'cbjs_action_over': '''
            bvr.src_el.setStyle("background", "#0F0");
        ''',
        'cbjs_action_out': '''
            bvr.src_el.setStyle("background", "");
        '''
        } )




        # allow resize except for first column (the select box column)
        if widget_idx > 0:
            th.add_class("header_cell_resize")
            th.add_class("SPT_DRAG_COLUMN_RESIZE")
            th.add_styles("width: 6px;")
        else:
            th.add_styles("width: 0px;")


        return th



    def handle_header_option_wdg(my, th, widget):
        div = DivWdg()
        th.add(div)
        div.add_style("position: absolute")
        div.add_style("display: none")
        div.add_style("padding: 5px")
        div.add_class('spt_table_header_option_top')
        div.add_border()
        div.add_color("background", "background", -5)
        div.add_color("color", "color")
        div.add_style("margin-left: 0px")
        div.add_style("margin-top: -4px")
        div.add_style("z-index: 150")
        div.add_style("min-height: 20px")
        div.add_style("min-width: 40px")

        div.add(widget)

        div.add_behavior( {
        'type': 'hover',
        'cbjs_action_over': '''
        spt.show(bvr.src_el);
        ''',
        'cbjs_action_out': '''
        var el = bvr.src_el.getElement(".spt_table_header_option_top");
        spt.hide(bvr.src_el);
        '''
        } )


        # put the behaviors on the header
        th.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        var el = bvr.src_el.getElement(".spt_table_header_option_top");
        spt.toggle_show_hide(el);
        '''
        } ) 

        th.add_behavior( {
        'type': 'hover',
        'cbjs_action_over': '''
        ''',
        'cbjs_action_out': '''
        var el = bvr.src_el.getElement(".spt_table_header_option_top");
        spt.hide(el);
        '''
        } )




        return div



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
            "label": "Order By (Ascending)",
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
            "hover_bvr_cb": { 'activator_add_looks': 'dg_header_cell_hilite',
                              'affect_activator_relatives' : [ 'spt.get_next_same_sibling( @, null )' ] }
        } )

        # Order By (Descending) menu item ...
        menu_data.append( {
            "type": "action",
            "label": "Order By (Descending)",
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
            "hover_bvr_cb": { 'activator_add_looks': 'dg_header_cell_hilite',
                              'affect_activator_relatives' : [ 'spt.get_next_same_sibling( @, null )' ] }
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
            "hover_bvr_cb": { 'activator_add_looks': 'dg_header_cell_hilite',
                              'affect_activator_relatives' : [ 'spt.get_next_same_sibling( @, null )' ] }
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
            "hover_bvr_cb": { 'activator_add_looks': 'dg_header_cell_hilite',
                              'affect_activator_relatives' : [ 'spt.get_next_same_sibling( @, null )' ] }
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
                '''%OldTableLayoutWdg.GROUP_WEEKLY
            },
            "hover_bvr_cb": { 'activator_add_looks': 'dg_header_cell_hilite',
                              'affect_activator_relatives' : [ 'spt.get_next_same_sibling( @, null )' ] }
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
                '''%OldTableLayoutWdg.GROUP_MONTHLY
            },
            "hover_bvr_cb": { 'activator_add_looks': 'dg_header_cell_hilite',
                              'affect_activator_relatives' : [ 'spt.get_next_same_sibling( @, null )' ] }
        } )    

      
        menu_data.append( {
            "type": "separator"
        } )


        # TEST
        # TEST
        # TEST
        # This assumes that the way to add an item is to use edit widget.
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
                    'args' : {'search_type': search_type_obj.get_base_key()},
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
                "hover_bvr_cb": { 'activator_add_looks': 'dg_header_cell_hilite',
                                  'affect_activator_relatives' : [ 'spt.get_next_same_sibling( @, null )' ] }
            } )


            menu_data.append( {
                "type": "separator"
             } )

        
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
            "hover_bvr_cb": { 'activator_add_looks': 'dg_header_cell_hilite',
                              'affect_activator_relatives' : [ 'spt.get_next_same_sibling( @, null )' ]
                      }
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
                    ''',
                }
            } )


            menu_data.append( {
                "type": "action",
                "label": "Create New Column",
                "bvr_cb": {
                    'args' : {'search_type': search_type_obj.get_base_key()},
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
                "hover_bvr_cb": { 'activator_add_looks': 'dg_header_cell_hilite',
                                  'affect_activator_relatives' : [ 'spt.get_next_same_sibling( @, null )' ] }
            } )


            menu_data.append( {
                "type": "separator"
            } )

        

        # Remove Grouping menu item ...
        menu_data.append( {
            "type": "action",
            "label": "Remove Grouping",
            "bvr_cb": {
                'cbjs_action':
                    '''
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



    def _add_prev_row(my, table, idx):
        # skip the first two rows
        if idx in [my.INSERT_ROW, my.EDIT_ROW]:
            return

        prev_sobj = None
        if idx > 2:
            prev_sobj = my.sobjects[idx-1]

        for widget in my.widgets:
            # set the index here instead
            widget.set_current_index(idx)
            #prev_row_wdg = widget.get_prev_row_wdg(table, prev_sobj)
            #if prev_row_wdg:
            #    table.add_row()
            #    table.add_cell("&nbsp", css="cell_left")
            #    tr, td = table.add_row_cell(prev_row_wdg, css="cell_left")
            #    td.add_style("padding: 3px")

            widget.add_prev_row(table, prev_sobj)


    def _add_hidden_rows(my, table):
        # add the hidden rows
        hidden_row_wdgs = []
        for widget in my.widgets:
             
            if widget.__class__.__name__ == "HiddenRowToggleWdg":
                hidden_row_wdgs.append(widget)
            elif widget.__class__.__name__ == "CustomXmlWdg" and \
                    widget.get_child_widget_class() == "HiddenRowToggleWdg":
                hidden_row_wdgs.append( widget.get_child_widget() )

        rows = table.add_hidden_row(hidden_row_wdgs) 
        # it could be empty list
        if rows:
            for tr,td in rows:
                #tr.add_style('display: none')
                tr.add_class("spt_table_tr_hidden")
                tr.add_color("color", "color")
                tr.add_color("background", "background")
                td.add_class("spt_table_td_hidden")

                color = td.get_color("table_border", default="border")
                td.add_style("border-style: solid")
                td.add_style("border-width: 0 1px 0 1px")
                td.add_style("border-color:  %s" % color)
                
            


    # menu_tag_suffix is 'MAIN' or 'SUB1' or 'SUB2', etc
    #
    def get_action_gear_menu(my):
        return { 'menu_tag_suffix': 'MAIN', 'width': 200, 'opt_spec_list': [
            { "type": "action", "label": "Launch JS Logger",
                    "bvr_cb": {'cbjs_action': "spt.js_log.show();"} },

            { "type": "action", "label": "Command cbk",
                    "bvr_cb": {'cbjs_action': "spt.ctx_menu.option_clicked_cbk( evt, bvr );",
                               'options': {'inner_cbk': 'spt.ctx_menu.test'}},
                    "hover_bvr_cb": {'activator_mod_styles':
                                        'background-color: black; color: blue; border: 1px solid red;'} },

            { "type": "action", "label": "Open",
                    "bvr_cb": {'cbjs_action': "alert('Open File clicked!');"},
                    "icon": IconWdg.LOAD },

            { "type": "action", "label": "Make activator_el RED",
                    # -- NOTE: the example below shows how to get to the activator_el ... just use the convenience
                    #          function 'spt.semnu.get_activator(bvr)' ... you just need to provide the call
                    #          with the bvr. This works for sub-menus as well.
                    "bvr_cb": {'cbjs_action': "spt.smenu.get_activator(bvr).setStyle('background','#FF0000');"} },

            { "type": "separator" },

            { "type": "toggle", "label": "Use Silky Smooth Work-flow", "state": True },
            { "type": "toggle", "label": "Have a Not Cool Day!", "state": False },

            { "type": "action", "label": "Get Information!",
                    "bvr_cb": {'cbjs_action': "spt.js_log.show();"},
                    "icon": IconWdg.INFO }
        ] }




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
        div.add_style("overflow: hidden")
        div.add_style("padding-top: 3px")
        div.add_style("padding-right: 8px")
        div.add_color("color", "color")
        #div.add_gradient("background", "background")
        div.add_color("background", "background",-8)
        if not my.kwargs.get("__hidden__"):
            div.add_border()
            div.add_style("margin-left: -1px")
            div.add_style("margin-right: -1px")
        else:
            div.add_style("border-width: 0px 0px 0px 1px")
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



        # add gear menu here!
        if my.kwargs.get("show_gear") != "false":
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
                table_id=my.get_table_id(),
                search_type=my.search_type, view=my.view,
                parent_key=my.parent_key,
                cbjs_post_delete=cbjs_post_delete, show_delete=show_delete,
                custom_menus=custom_gear_menus,
                show_retired=show_retired, embedded_table=embedded_table )

            my.gear_menus = btn_dd.get_menu_data()
            div.add(btn_dd)

        else:
            my.gear_menus = None
            btn_dd = Widget()



        spacing_divs = []
        for i in range(0, 5):
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
        num_div = DivWdg()
        num_div.add_color("color", "color")
        num_div.add_style("float: left")
        num_div.add_style("margin-top: 0px")
        num_div.add_style("font-size: 10px")
        num_div.add_style("padding: 5px")
        
        # -- SEARCH LIMIT DISPLAY
        # show items found even if hiding search limit tool
        #if my.show_search_limit:
        if my.items_found == 0 and my.search:
            my.items_found = my.search.get_count()

        if my.items_found == 1:
            num_div.add( "%s item found" % my.items_found)
        else:
            num_div.add( "%s items found" % my.items_found)
        num_div.add_style("margin-right: 0px")
        num_div.add_border(style="none")
        num_div.set_round_corners(6)
        



        # -- PAGINATION TOOLS
        limit_span = DivWdg()
        limit_span.add_style("margin-top: 4px")
        if my.search_limit:
            search_limit_button = IconButtonWdg("Pagination", IconWdg.ARROWHEAD_DARK_DOWN)
            num_div.add(search_limit_button)
            from tactic.ui.container import DialogWdg
            dialog = DialogWdg()
            limit_span.add(dialog)
            dialog.set_as_activator(num_div)
            dialog.add_title("Search Limit")
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
            limit_div.add_style("width: 250px")
            #limit_div.add_style("height: 50px")

            #limit_span.add(my.search_limit)




        search_button_row = my.get_search_button_row_wdg()
        layout_wdg = None
        column_wdg = None
        show_column_wdg = my.kwargs.get('show_column_manager') 
        show_layout_wdg = my.kwargs.get('show_layout_switcher') 
        if not show_column_wdg =='false':
            column_wdg = my.get_column_manager_wdg()
        if not show_layout_wdg =='false':
            layout_wdg = my.get_layout_wdg()
        
        help_alias = my.get_alias_for_search_type(my.search_type)
        from tactic.ui.app import HelpButtonWdg
        help_wdg = HelpButtonWdg(alias=help_alias, use_icon=True)
        help_wdg.add_style("margin-top: -2px")


        wdg_list = []
        if button_row_wdg.get_num_buttons() != 0:
            wdg_list.append( { 'wdg': button_row_wdg } )

        if my.show_search_limit:
            wdg_list.append( { 'wdg': spacing_divs[0] } )
            wdg_list.append( { 'wdg': num_div } )
            wdg_list.append( { 'wdg': limit_span } )
        else:
            wdg_list.append( { 'wdg': num_div } )


        from tactic.ui.widget import ButtonRowWdg
        button_row_wdg = ButtonRowWdg(show_title=True)
        if search_button_row:
            button_row_wdg.add(search_button_row)
            if my.filter_num_div:
                wdg_list.append( { 'wdg': my.filter_num_div } )
            

        if column_wdg:
            button_row_wdg.add(column_wdg)

        if layout_wdg:
            button_row_wdg.add(layout_wdg)


        if button_row_wdg.get_num_buttons() != 0:
            wdg_list.append( { 'wdg': spacing_divs[1] } )
            wdg_list.append( { 'wdg': button_row_wdg } )


        show_quick_add = my.kwargs.get("show_quick_add")
        if show_quick_add in ['true',True]:
            quick_add_button_row = my.get_quick_add_wdg()
            wdg_list.append( { 'wdg': spacing_divs[2] } )
            wdg_list.append( { 'wdg': quick_add_button_row } )

        # add the help widget
        wdg_list.append( { 'wdg': spacing_divs[4] } )
        wdg_list.append( { 'wdg': help_wdg } )

        horiz_wdg = HorizLayoutWdg( widget_map_list = wdg_list, spacing = 4, float = 'left' )
        xx = DivWdg()
        xx.add(horiz_wdg)
        div.add(xx)

        if my.kwargs.get("__hidden__"):
            scale = 0.8
            #scale = 1
        else:
            scale = 1

        # Different browsers seem to have a lot of trouble with this
        web = WebContainer.get_web()
        browser = web.get_browser()
        import os
        if browser == 'Qt' and os.name != 'nt':
            height = "41px"
        elif scale != 1:
            xx.set_scale(scale)
            xx.add_style("float: left")
            xx.add_style("margin-left: -25")
            xx.add_style("margin-top: -5")
            height = "32px"
        else:
            height = "41px"

        #div.add( horiz_wdg )

        # FIXME: for now put a minimum width so that the buttons stay on the
        # same line
        outer = DivWdg()
        outer.add(div)
        outer.add_style("min-width: 100px")
        #outer.add_style("width: 300px")
        outer.add_style("overflow: hidden")
        outer.add_class("spt_resizable")

        div.add_style("min-width: 800px")
        div.add_style("height: %s" % height)

        return outer

    def get_context_menu_info_wdg(my):
        '''this is used to notify the context menu something has changed in the table. It has been simplified from the previous set of TextBtnSetWdg'''
        # There is some dependencies to have this exist in the page:
        # ie: spt.dg_table.drow_smenu_setup_cbk
        # putting it in, but hidden for now
        commit_div = DivWdg()
        
        commit_div.add_style("display: none")

        # It is just a placeholder
        commit_btn_top_el = DivWdg('Save')
      
        commit_btn_top_el.add_class("spt_table_commit_btn")
        commit_btn_top_el.add_style("display: none")
        # this id is for spt.dg_table._toggle_commit_btn()
        commit_btn_top_el.set_id('%s_commit_btn'%my.table_id)

        commit_div.add( commit_btn_top_el )
        
        return commit_div


    def get_insert_mode_action_wdg(my):

        div = DivWdg() 
        color = div.get_color("border")
        div.add_style("border-color: %s" % color)
        div.add_style("border-width: 1px 1px 0 1px")
        div.add_style("border-style: solid")
        div.add_style("height: 22px")

        div.add_style("padding-top: 8px")
        div.add_style("padding-bottom: 8px")
        div.add_style("padding-right: 8px")
        div.add_color("color", "color")
        div.add_gradient("background", "background")

        div.add_style("margin-top: -2px")
        div.add_style("width: 100%")


        show_insert = my.get_show_insert()

        commit_label = 'Save'

        # only suitable for widgets that exist in multiple tables in
        # a page like NoteSheetWdg
        show_commit_all = my.kwargs.get("show_commit_all")
        commit_all_label = 'Save All'  # was previously labeled 'commit all'

        # Add commit and insert, "+", buttons
        buttons_list = []
        if show_commit_all:
            commit_all_event = 'commit_all'
            div.add_named_listener(commit_all_event, 'spt.dg_table.update_row(evt, bvr)')

            buttons_list.append(
                {'label': commit_all_label , 'tip': 'Save Changes from all Tables', 'width': '20px',
                    'bvr': { 'cbjs_action': 'spt.named_events.fire_event("%s", {});' %commit_all_event,
                             'table_id': my.table_id}
                }
            )
        buttons_list.append(
            {'label': commit_label, 'tip': 'Save Changes',
                'bvr': { 'cbjs_action': 'spt.dg_table.update_row(evt, bvr)',
                         'table_id': my.table_id}
            }
        )
        if show_insert not in ["false", False]:
            buttons_list.append(
            {'label': '+', 'tip': 'Add Another Item',
                'bvr': { 'cbjs_action': "spt.dg_table.add_item_cbk(evt, bvr)" }
            }
            )
        commit_add_btns = TextBtnSetWdg( float="right", buttons=buttons_list,
                                         spacing=6, size='small', side_padding=4 )
        commit_btn_top_el = commit_add_btns.get_btn_top_el_by_label(commit_label)
        commit_btn_top_el.add_class("spt_table_commit_btn")
        commit_btn_top_el.add_styles("display: none;")

        commit_btn_top_el.add_behavior( {'type': 'show',
                                         'cbjs_action': 'spt.widget.btn_wdg.set_btn_width( bvr.src_el );'} );


        commit_all_btn_top_el = commit_add_btns.get_btn_top_el_by_label(commit_all_label)
        # "save all" (previously "commit all") button is not always generated (see above),
        # so first check to see if it exists before adding styles and classes to it ...
        if commit_all_btn_top_el:
            commit_all_btn_top_el.add_class("spt_table_commit_btn")
            commit_all_btn_top_el.add_styles("display: none;")

        div.add( commit_add_btns )

        if my.kwargs.get("show_refresh") != 'false':
            # Add in button to allow the refresh of the table ...
            from tactic.ui.widget import SingleButtonWdg
            refresh_button = SingleButtonWdg(title="Refresh List", icon=IconWdg.REFRESH)

            refresh_button.add_behavior( {
                    'type': 'click',
                    'cbjs_action': '''
                    bvr.panel = bvr.src_el.getParent('.spt_table_top');
                    spt.dg_table.search_cbk(evt, bvr);
                    '''
                } )
            refresh_div = DivWdg()
            div.add(refresh_div)
            refresh_div.add_style("margin: -2px 5px 0px 5px")
            refresh_div.add_style("float: left")
            refresh_div.add(refresh_button)

        # add number found
        num_div = DivWdg()
        num_div.add_style("float: left")
        num_div.add_style("margin-left: 5px")
        num_div.add_style("margin-right: 10px")
        num_div.add_style("margin-top: 3px")

        if my.items_found == 0 and my.search:
            my.items_found = my.search.get_count()
        if my.items_found:
            num_div.add( "%s item(s) found" % my.items_found)
            div.add(num_div)

        # add minimum pagination if there are more than 10 items
        # to avoid unnecessary drawing in insert mode which
        # is supposed to be a bit simpler
        limit_span = DivWdg()
        div.add(limit_span)
        limit_span.add_style("float: left")
        limit_span.add_style("margin-top: -2px")
        limit_span.add_class("spt_table_search")
        if my.items_found > 10 and my.search_limit:
            limit_span.add(my.search_limit)
            refresh_script = '''bvr.panel = bvr.src_el.getParent('.spt_panel'); spt.dg_table.search_cbk(evt, bvr);'''
            my.search_limit.set_refresh_script(refresh_script)

        return div



    def get_button_row_wdg(my):
        '''draws the button row in the shelf'''
        from tactic.ui.widget.button_new_wdg import ButtonRowWdg, ButtonNewWdg

        button_row_wdg = ButtonRowWdg(show_title=True)

        if my.kwargs.get("show_refresh") != 'false':
            button = ButtonNewWdg(title='Refresh', icon=IconWdg.REFRESH)
            button_row_wdg.add(button)
            my.run_search_bvr = my.kwargs.get('run_search_bvr')
            if my.run_search_bvr:
                button.add_behavior(my.run_search_bvr)
            else:
                button.add_behavior( {
                'type': 'click_up',
                'cbjs_action':  'spt.dg_table.search_cbk(evt, bvr);'
            } )


        # add an item button
        show_insert = my.view_attributes.get("insert")
        # if edit_permission on the sobject is not allowed then
        # we don't allow insert
        show_save = True

        if my.edit_permission == False:
            show_insert = False
            show_save = False

        if show_insert in [ '', None ]:
            show_insert = my.kwargs.get("show_insert")

        # Save button
        save_button = ButtonNewWdg(title='Save Current Table', icon=IconWdg.SAVE, is_disabled=False)

        
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
       
        #from tactic.ui.container import Menu, MenuItem, SmartMenu
        if show_insert not in ["false", False]:
            #button = ButtonNewWdg(title='Add New Item', icon=IconWdg.PLUS_ADD)

            insert_view = my.kwargs.get("insert_view")
            
            if not insert_view or insert_view == 'None':
                insert_view = "insert"

            button = ButtonNewWdg(title='Add New Item (Shift-Click to add in page)', icon=IconWdg.ADD)
            button_row_wdg.add(button)
            button.add_behavior( {
                'type': 'click_up',
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
            # no need for app_busy.. since it's built-in to search_cbk()
            button.add_behavior( {
                'type': 'listen',
                'event_name': 'search_table_%s' % my.table_id,
                'cbjs_action': '''
                    var top = bvr.src_el.getParent(".spt_layout");
                    var version = top.getAttribute("spt_version");
                    if (version == "2") {
                        spt.table.set_layout(top);
                        spt.table.run_search();
                    }
                    else {
                        spt.dg_table.search_cbk( {}, {src_el: bvr.src_el} );
                    } 
                '''
            } )




            button.add_behavior( {
                'type': 'click_up',
                'modkeys': 'SHIFT',
                'cbjs_action': '''
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


            button.set_show_arrow_menu(True)
            menu = Menu(width=180)
            menu_item = MenuItem(type='title', label='Actions')
            menu.add(menu_item)
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
                    kwargs = {
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

           
            button_row_wdg.add(save_button)


        elif show_save:
            button_row_wdg.add(save_button)


        button = ButtonNewWdg(title='Expand Table', icon=IconWdg.ARROW_OUT, show_menu=False, is_disabled=False)
        button_row_wdg.add(button)
        button.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        var layout = bvr.src_el.getParent(".spt_layout");

        var version = layout.getAttribute("spt_version");
        var headers;
        var table = null;
        if (version == '2') {

            spt.table.set_layout(layout);
            table = spt.table.get_table();
            var table_id = table.getAttribute('id');
            headers = table.getElements(".spt_table_header_" + table_id);
        }
        else {
            table = spt.get_cousin( bvr.src_el, '.spt_table_top', '.spt_table' );
            headers = layout.getElements(".spt_table_th");
        }

        var width = table.getStyle("width");
        if (width == '100%') {
            table.setStyle("width", "");
        }
        else {
            table.setStyle("width", "100%");
        }


        for ( var i = 1; i < headers.length; i++) {
            var element_name = headers[i].getAttribute("spt_element_name");
            if (element_name == 'preview') {
                continue;
            }

            if (width == '100%') {
                headers[i].setStyle("width", "1px");
            }
            else {
                headers[i].setStyle("width", "");
            }

        }
        '''
        } )

           

        if my.kwargs.get("show_gear") != "false":
            button = ButtonNewWdg(title='More Options', icon=IconWdg.GEAR, show_arrow=True)
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
    
        if show_search and (my.is_refresh or search_dialog_id):
            div = DivWdg()
            my.table.add_attr("spt_search_dialog_id", search_dialog_id)
            button = ButtonNewWdg(title='View Advanced Search', icon=IconWdg.ZOOM, show_menu=False, show_arrow=False)
            #button.add_style("float: left")
            div.add(button)


            button.add_behavior( {
                'type': 'click_up',
                'dialog_id': search_dialog_id,
                'cbjs_action': '''
                var offset = bvr.src_el.getPosition();

                var size = bvr.src_el.getSize();
                var dialog = $(bvr.dialog_id);
                if (dialog) {
                    offset = {x:offset.x-250, y:offset.y+size.y+10};

                    var body = $(document.body);
                    var scroll_top = body.scrollTop;
                    var scroll_left = body.scrollLeft;
                    offset.y = offset.y - scroll_top;
                    offset.x = offset.x - scroll_left;


                    var body = $(document.body);
                    dialog.position({position: 'upperleft', relativeTo: body, offset: offset});
                    spt.toggle_show_hide(dialog);
                }

                '''
            } )


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
        layout = ButtonNewWdg(title='Switch Layout', icon=IconWdg.VIEW, show_arrow=True)

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

        #div = DivWdg()
        #button = SingleButtonWdg(title='Column Manager', icon=IconWdg.COLUMNS, show_arrow=False)
        #div.add(button)
        #div.add_style("margin-top: -8px")
        button = ButtonNewWdg(title='Column Manager', icon=IconWdg.COLUMNS, show_arrow=False)

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
                    table = panel.getElement('.spt_table');
                    element_names = spt.dg_table.get_element_names(table); 
                }
                bvr.args.element_names = element_names;

                var class_name = 'tactic.ui.panel.AddPredefinedColumnWdg';

                var popup = spt.panel.load_popup(bvr.args.title, class_name, bvr.args);
                popup.activator = bvr.src_el;
                ''',
            } )

        #return div
        return button



    def get_aux_wdg(my):

        aux_div = DivWdg()
        aux_div.add_style("display: none")
        aux_div.add_style("padding: 10px")
        aux_div.add_class("spt_table_aux")
        aux_div.add_color("border-color", "table_border", default="border")
        aux_div.add_style("border-width: 0 1 0 1" )
        aux_div.add_style("border-style: solid" )
        aux_div.add_color("background", "background" )
        aux_div.add_color("color", "color" )

        aux_rounded = DivWdg()

        aux_div.add(aux_rounded)

        aux_title = DivWdg()
        aux_title.add_class("spt_table_aux_title")
        aux_title.add_class("maq_search_bar")
        aux_rounded.add(aux_title)
        aux_rounded.add("<br/>")
        aux_content = DivWdg()
        aux_content.add_class("spt_table_aux_content")
        aux_rounded.add(aux_content)
        return aux_div



    def handle_tr(my, tr):
        return
        '''
        # FIXME: row_editable is not used
        keys = {
            'config/widget_config?project=plugin&code=PHOTOSHOP01': '',
            'config/widget_config?project=plugin&code=2PLUGIN': '',
        }

        sobject = my.current_sobject
        search_key = SearchKey.get_by_sobject(sobject)
        if keys.get(search_key) != None:
            tr.add_style("background: #334")
            tr.set_attr("title", "Protected by plugin [%s]" % "photoshop")
            my.row_editable = False
        else:
            my.row_editable = True
        '''

    def is_expression_element(my, element_name):
        from tactic.ui.table import ExpressionElementWdg
        widget = my.get_widget(element_name)
        return isinstance(widget, ExpressionElementWdg)



    def get_onload_js(my):
        return r'''
        spt.dom.load_js( ["dg_table.js"], function() {
            spt.dom.load_js( ["dg_table_action.js"], function() {
                spt.dom.load_js( ["dg_table_editors.js"], function() {} )
            } );
        } );
        '''
"""



__all__.append("SwitchLayoutMenu")
__all__.append('CellEditWdg')
__all__.extend(["CellWdg"])
__all__.extend(["EditColumnDefinitionWdg", "EditColumnDefinitionCbk"])


class SwitchLayoutMenu(object):

    def __init__(my, **kwargs):
        my.kwargs = kwargs

        my.search_type = my.kwargs.get("search_type")
        activator = my.kwargs.get("activator")
        my.view = my.kwargs.get("view")

        menu = Menu(width=180, allow_icons=True)
        menu_item = MenuItem(type='title', label='Switch Layout')
        menu.add(menu_item)

        config = WidgetConfigView.get_by_search_type(my.search_type, "table")
        default_element_names = config.get_element_names()


        views = ['table', 'tile', 'list', 'content', 'navigate', 'schedule', 'checkin', 'tool', 'browser', 'card', 'overview']
        labels = ['Table', 'Tile', 'List', 'Content', 'Navigator', 'Task Schedule', 'Check-in', 'Tools', 'File Browser', 'Card', 'Overview']

        # this is fast table biased
        if my.kwargs.get("is_refresh") in ['false', False]:
            class_names = [
                'tactic.ui.panel.ViewPanelWdg',
                'tactic.ui.panel.ViewPanelWdg',
                'tactic.ui.panel.ViewPanelWdg',
                'tactic.ui.panel.ViewPanelWdg',
                'tactic.ui.panel.ViewPanelWdg',
                'tactic.ui.panel.ViewPanelWdg',
                'tactic.ui.panel.ViewPanelWdg',
                'tactic.ui.panel.ViewPanelWdg',
                'tactic.ui.panel.ViewPanelWdg',
                'tactic.ui.panel.ViewPanelWdg',
                'tactic.ui.panel.ViewPanelWdg',
            ]
        else:
            class_names = [
                'tactic.ui.panel.FastTableLayoutWdg',
                'tactic.ui.panel.TileLayoutWdg',
                'tactic.ui.panel.FastTableLayoutWdg',
                'tactic.ui.panel.FastTableLayoutWdg',
                'tactic.ui.panel.FastTableLayoutWdg',
                'tactic.ui.panel.FastTableLayoutWdg',
                'tactic.ui.panel.FastTableLayoutWdg',
                'tactic.ui.panel.tool_layout_wdg.ToolLayoutWdg',
                'tactic.ui.panel.tool_layout_wdg.RepoBrowserLayoutWdg',
                'tactic.ui.panel.tool_layout_wdg.CardLayoutWdg',
                'tactic.ui.panel.FastTableLayoutWdg',
            ]


        layouts = [
            'table',
            'tile',
            'default',
            'default',
            'default',
            'default',
            'default',
            'tool',
            'browser',
            'card',
            'default',
        ]

        element_names = [
            default_element_names,
            [],
            ['name'],
            ['preview','code','name','description'],
            ['show_related','detail','code','description'],
            ['preview','code','name','description','task_pipeline_vertical','task_edit','notes'],
            ['preview','code','name','general_checkin','file_list', 'history','description','notes'],
            ['name','description','detail', 'file_list','general_checkin'],
            [],
            [],
            ['preview','name','task_pipeline_report','summary','completion'],
	    ]

        if not SearchType.column_exists(my.search_type, 'name'):
            element_names = [
            default_element_names,
            [],
            ['code'],
            ['preview','code','description'],
            ['show_related','detail','code','description'],
            ['preview','code','description','task_pipeline_vertical','task_edit','notes'],
            ['preview','code','general_checkin','file_list', 'history','description','notes'],
            [],
            [],
            [],
            ['preview','code','task_pipeline_report','summary','completion'],
	    ]



        # add in the default
        #views.insert(0, my.view)
        #labels.insert(0, my.view)
        #class_names.insert(0, 'tactic.ui.panel.FastTableLayoutWdg')
        #layouts.insert(0, "tile")
        #element_names.insert(0, None)

        cbk = my.kwargs.get("cbk")
        if not cbk:
            cbk = '''
            var activator = spt.smenu.get_activator(bvr);
            var top = activator.getParent(".spt_view_panel_top");
            if (!top) {
                alert("Error: spt_view_panel_top not found");
                return;
            }

          
            var table_top = top.getElement(".spt_table_top");
            var table = table_top.getElement(".spt_table_table");

            var layout = top.getAttribute("spt_layout");
            var layout_el = top.getElement(".spt_layout");

            var version = layout_el.getAttribute("spt_version");
            if (version =='2') {
                var table = table_top.getElement(".spt_table_table");
            } else {
                var table = table_top.getElement(".spt_table");
            }

            
            
            top.setAttribute("spt_layout", layout);
            var last_view = top.getAttribute("spt_view");
            top.setAttribute("spt_last_view", last_view);
            top.setAttribute("spt_view", bvr.view);
            table_top.setAttribute("spt_class_name", bvr.class_name);
            table_top.setAttribute("spt_view", bvr.view);
            
            table.setAttribute("spt_view", bvr.view);
            spt.dg_table.search_cbk( {}, {src_el: bvr.src_el, element_names: bvr.element_names, widths:[]} );


            /* TEST to have elements update tab ...
            // if this is actually in a tab, record this on the tab
            spt.tab.set_tab_top_from_child(activator);
            var header = spt.tab.get_selected_header();
            var element_name = header.getAttribute("spt_element_name");
            spt.tab.set_attribute(element_name, "layout", bvr.view);
            */


            '''


        from layout_util import LayoutUtil

        for i, view in enumerate(views):
            #data = LayoutUtil.get_layout_data(search_type=my.search_type, layout=view)
            #layout = view
            #class_name = data.get("class_name")
            #element_names = data.get("element_names")
            #label = data.get("label")

            # TODO: use old method for now until we can ensure the stability
            # of the new method
            class_name = class_names[i]
            element_name_list = element_names[i]
            layout = layouts[i]
            label = labels[i]

            menu_item = MenuItem(type='action', label=label)
            if my.view == views[i]:
                menu_item.set_icon(IconWdg.DOT_GREEN)
            menu.add(menu_item)
            menu_item.add_behavior( {
            'type': 'click_up',
            'view': view,
            'class_name': class_name,
            'element_names': element_name_list,
            'layout': layout,
            'search_type': my.search_type,
            'cbjs_action': cbk
            } )


        menus = [menu.get_data()]
        SmartMenu.add_smart_menu_set( activator, { 'DG_BUTTON_CTX': menus } )
        SmartMenu.assign_as_local_activator( activator, "DG_BUTTON_CTX", True )





# Cell Editing and Display
class CellEditWdg(BaseRefreshWdg):
    '''Widget which allows the editing of a cell'''

    def get_args_keys(my):
        return {
        'search_type': 'the search type of table',
        'element_name': 'element name that this widget represents',
        'x': 'the x index of the element',
        'y': 'the y index of the element',

        'state': 'specifies a set of state data for new inserts',
        'layout_version': '1 or 2'
        }



    def get_display_wdg(my):
        '''get the display widget that is contained in the cell edit'''
        return my.display_wdg


    def init(my):
        element_name = my.kwargs['element_name']
        search_type = my.kwargs['search_type']
        layout_version = my.kwargs['layout_version']

        configs = Container.get("CellEditWdg:configs")
        if not configs:
            configs = {}
            Container.put("CellEditWdg:configs", configs)
        key = "%s" % (search_type)
        my.config = configs.get(key)
        if not my.config:

            # create one
            view = "edit"

            my.config = WidgetConfigView.get_by_search_type(search_type, view)
            configs[key] = my.config

            # add an override if it exists
            view = "edit_item"
            #view = "test_edit"

            db_config = WidgetDbConfig.get_by_search_type(search_type, view)
            if db_config:
                my.config.get_configs().insert(0, db_config)

        my.sobject = None


        # create the edit widget
        try:
            # FIXME: This doesn't look right.. the type can only be display or action, not edit
            my.display_wdg = my.config.get_widget(element_name, "edit")
        except ImportError, e:
            print "WARNING: create widget", str(e)
            my.display_wdg = SimpleTableElementWdg()
            my.display_wdg.add("No edit defined")



        state = my.kwargs.get('state')
        state['search_type'] = search_type
        if my.display_wdg:
            my.display_wdg.set_state(state)

            if layout_version == '1':
                my.add_edit_behavior(my.display_wdg)
			

        # find the type of this element
        my.element_type = my.config.get_type(element_name)
        if not my.element_type:
            # NOTE: this should be centralized!
            if element_name.endswith('_date'):
                my.element_type = 'date'
            elif element_name.endswith('_time'):
                my.element_type = 'time'

        # ask the edit widget!
        if not my.element_type:
            try:
                my.element_type = my.display_wdg.get_type()
            except AttributeError, e:
                pass
                

        # otherwise, base it on the database type
        if not my.element_type:
            my.element_type = SearchType.get_tactic_type(search_type, element_name)

        

    def add_edit_behavior(cls, widget):
        '''this is only applicable in the old TableLayoutWdg''' 
        # add some special behavior for certain widgets ... custom ones will
        # have to implement their own
        from pyasm.widget import SelectWdg

        # table rows have a right click context override ... allow edit widgets to force the default right
        # click contexxt menu in order to be able to copy, cut and paste using right click menu ...
        #
        widget.force_default_context_menu()
        

        if (isinstance(widget, SelectWdg) or isinstance(widget, DynByFoundValueSmartSelectWdg)):
            web = WebContainer.get_web()
            
             
            if web.is_IE():
                # TODO: the click event does not work for IE8.  There is still
                # an issue that select the previous value selects.  This
                # is lost somewhere.
                event = 'change'
                widget.add_behavior( { 'type': event,
                   'cbjs_action': 'spt.dg_table.edit_cell_cbk( bvr.src_el, spt.kbd.special_keys_map.ENTER);'} );
            else:
                event = 'click'
                widget.add_behavior( { 'type': event,
                   'cbjs_action': 'spt.dg_table.select_wdg_clicked( evt, bvr.src_el );' } )

            #behavior = {
            #    'type': 'keyboard',
            #    'kbd_handler_name': 'DgTableSelectWidgetKeyInput'
            #}
            #widget.add_behavior( behavior )

        elif (isinstance(widget, CheckboxWdg)):
            widget.add_event("onclick", "spt.dg_table.edit_cell_cbk( this, spt.kbd.special_keys_map.ENTER)" );
            behavior = {
                'type': 'keyboard',
                'kbd_handler_name': 'DgTableMultiLineTextEdit'
            }
            widget.add_behavior(behavior)
        elif (isinstance(widget, TextAreaWdg)):
           behavior = {
               'type': 'keyboard',
               'kbd_handler_name': 'DgTableMultiLineTextEdit'
           }
           widget.add_behavior( behavior )
          
        elif (isinstance(widget, TextWdg)):
           behavior = {
               'type': 'keyboard',
               'kbd_handler_name': 'DgTableMultiLineTextEdit'
           }
           widget.add_behavior(behavior)


    add_edit_behavior = classmethod(add_edit_behavior)


    def get_display_wdg(my):
        return my.display_wdg



    def get_element_type(my):
        return my.element_type

    #def get_dependent_attrs(my):
    #    return my.dependent_attrs

    def set_sobject(my, sobject):
        my.sobject = sobject



    def get_display(my):
        element_name = my.kwargs['element_name']

        div = DivWdg()
        div.set_id("CellEditWdg_%s" % element_name)
        div.add_class("spt_edit_widget")
        div.add_style("position: absolute")
        div.add_style("z-index: 50")
        div.add_attr("spt_element_name", element_name)

        if not element_name:
            return widget

        try:
            element_attrs = my.config.get_element_attributes(element_name)
            edit_script = element_attrs.get("edit_script")
            if edit_script:
                div.add_attr("edit_script", edit_script)

            display = my.display_wdg.get_buffer_display()
            div.add(display)
            #div.add(my.display_wdg)
        except Exception, e:
            print "WARNING in CellEditWdg: ", e
            my.display_wdg = TextWdg(element_name)
            my.display_wdg.set_value('Error in widget')
          
            display = my.display_wdg.get_buffer_display()
            div.add(display)
            

        # NOTE: this seems redundant, buffer display is already called at
        # this point
        if not my.sobject:
            my.sobject = my.kwargs.get('sobject')
        my.display_wdg.set_sobject(my.sobject)

        return div



    def get_values(my):
        '''method to get a data structure which can be used to populate the
        widget on the client side.  Generally the widgets are drawn unpopulated,
        so this information is need to dynamically load the informations'''
        assert my.sobject

        column = my.get_column()

        values = {}

        # main element
        if my.sobject.has_value(column):
            value = my.sobject.get_value(column)
            if my.element_type == 'time' and value and type(value) in types.StringTypes:
                # FIXME: this should use date util
                try:
                    tmp, value = value.split(" ")
                except Exception, e:
                    value = "00:00:00"

            values['main'] = value

        return values


    def get_column(my):
        '''special method to get the column override to add the data to'''
        element_name = my.kwargs['element_name']
        display_options = my.config.get_display_options(element_name)
        column = display_options.get("column")
        if not column:
            column = element_name
        return column
        

        
class CellWdg(BaseRefreshWdg):

    def get_display(my):
        web = WebContainer.get_web()

        search_key = my.kwargs.get('search_key')
        cmd = CellCmd(search_key=search_key)
        Command.execute_cmd(cmd)

        search_key = SearchKey.build_by_sobject(cmd.sobject)

        div = DivWdg()
        div.add_attr("spt_search_key", search_key )

        # Don't need to return the value because the how row is refreshed
        #div.add(cmd.value)
        div.add("&nbsp;")

        return div


class CellCmd(Command):

    def get_title(my):
        return "Table Cell Edit"

    def execute(my):
        web = WebContainer.get_web()

        search_key = my.kwargs.get('search_key')
        my.sobject = Search.get_by_search_key(search_key)

        element_name = web.get_form_value("element_name")
        value = web.get_form_value(element_name)
        if not value:
            value = web.get_form_value("main")
        if not value:
            value = web.get_form_value("name")
        my.sobject.set_value(element_name, value)
        my.sobject.commit()

        my.description = "Changed attribute [%s]" % element_name

        my.value = value




class RowCmd(Command):
    def execute(my):
        web = WebContainer.get_web()

        search_key = my.kwargs.get('search_key')
        sobject = Search.get_by_search_key(search_key)

        element_name = web.get_form_value("element_name")
        value = web.get_form_value(element_name)
        if not value:
            value = web.get_form_value("main")
        if not value:
            value = web.get_form_value("name")
        sobject.set_value(element_name, value)
        sobject.commit()

        my.value = value






from pyasm.widget import BaseTableElementWdg

class RowSelectWdg(BaseTableElementWdg):
    '''The Table Element which contains just a checkbox for selection'''
    def __init__(my, table_id, name=None, value=None):
       # Require "table_id" to be specified ... must be unique per table
        super(RowSelectWdg, my).__init__(name, value)
        my.table_id = table_id

        # Needed for MMS_COLOR_OVERRIDE ...
        web = WebContainer.get_web()
        my.skin = web.get_skin()



    def handle_th(my, th, cell_idx=None):

        th.set_id("maq_select_header")
        th.add_looks('dg_row_select_box')
        th.add_behavior( {'type': 'select', 'add_looks': 'dg_row_select_box_selected'} )

        th.set_attr('col_idx', str(cell_idx))
        th.add_style('width: 30px')
        th.add_style('min-width: 30px')

        th.add_behavior( {'type': 'click_up', 'mouse_btn':'LMB', 'modkeys':'',
                          'target_class': ('%s_row_target' % my.table_id),
                          'cbjs_action': 'spt.dg_table.select_deselect_all_rows(evt, bvr)'} )



    def get_title(my):
        return "&nbsp;"


    def handle_tr(my, tr):
        sobject = my.get_current_sobject()
        tr.set_attr( "spt_search_key", SearchKey.build_by_sobject(sobject, use_id=True) )


    def handle_td(my, td):

        # handle drag of row
        td.add_class("SPT_DRAG_ROW")
        td.add_class("SPT_DTS")

        td.add_style('width: 30px')
        td.add_style('min-width: 30px')

        # set the color of the row select
        td.add_color("background-color", "background", -10)

        i = my.get_current_index()
        sobject = my.get_current_sobject()

        row_id_str = "%s_select_td_%s" % (my.table_id, str(i+1))
        
        # prevent insert/edit rows getting selected for select all functions
        if sobject.is_insert():
            td.add_class( 'SPT_ROW_NO_SELECT')

        td.add_class( 'SPT_ROW_SELECT_TD cell_left' )
        # add this to specify the parent table
        td.add_class( 'SPT_ROW_SELECT_TD_%s' % my.table_id)

        td.add_looks( 'dg_row_select_box' )
        td.add_behavior( {
            'type': 'select',
            'add_looks': 'dg_row_select_box_selected'
        } )
        td.set_id( row_id_str )

        # determine if the client OS is a TOUCH DEVICE
        web = WebContainer.get_web()
        is_touch_device = web.is_touch_device()

        if is_touch_device:
            pass
        else:
            # click with no modifiers does select single (i.e. deselects all others) if not already selected,
            # or do nothing if already selected (this is behavior found in Mac OS X Finder) ...
            #td.add_behavior( { 'type': 'click_up', 'cbjs_action': 'spt.dg_table.select_single_row_cbk( evt, bvr );' } )
            td.add_behavior( {
                'type': 'click_up',
                'cbjs_action': 'spt.dg_table.select_row( bvr.src_el );'
            } )

            # SHIFT_LMB ... does block select, behaves like Mac OS X Finder
            td.add_behavior( { 'type': 'click_up', 'modkeys': 'SHIFT',
                               'cbjs_action': 'spt.dg_table.select_rows_cbk( evt, bvr );' } )

            # CTRL_LMB ... toggle select
            td.add_behavior( { 'type': 'click_up', 'modkeys': 'CTRL',
                               'cbjs_action':  'spt.dg_table.select_row( bvr.src_el );' } )

            # Drag will allow the dragging of items from a table onto anywhere else!
            td.add_behavior( { 'type': 'smart_drag', 'drag_el': 'drag_ghost_copy',
                               'use_copy': 'true',
                               'use_delta': 'true', 'dx': 10, 'dy': 10,
                               'drop_code': 'DROP_ROW',
                               'cbjs_pre_motion_setup': 'if (spt.drop) {spt.dg_table_action.sobject_drop_setup( evt, bvr );}',
                               'copy_styles': 'background: #393950; color: #c2c2c2; border: solid 1px black;' \
                                                ' text-align: left; padding: 10px;'
                               } )

        td.set_attr("selected", "no")


    def get_display(my):
        x = DivWdg()
        x.add_style("min-width: 24px")
        x.add_style("width: 24px")

        sobject = my.get_current_sobject()
        if sobject.is_insert():
            icon = IconWdg("New", IconWdg.NEW)
            x.add_style("padding: 2 0 0 4")
            x.add(icon)
        else:
            x.add("&nbsp;")


        return x





class AddPredefinedColumnWdg(BaseRefreshWdg):

    def get_args_keys(my):
        return {
            "element_names": "list of the element_names",
            "search_type": "search_type to list all the possible columns",
            "popup_id": "id to assign to the popup this widget creates",
            "target_id": "the id of the panel where the table is"
        }


    def get_columns_wdg(my, title, element_names, is_open=False):

        # hardcode to insert at 3, this will be overridden on client side
        widget_idx = 3

        content_wdg = DivWdg()
        content_wdg.add_class("spt_columns")
        content_wdg.add_style("margin-bottom: 5px")
        content_wdg.add_style("font-size: 1.0em")

        web = WebContainer.get_web()
        browser = web.get_browser()


        title_wdg = DivWdg()
        content_wdg.add(title_wdg)
        title_wdg.add_style("padding: 10px 3px")
        title_wdg.add_color("background", "background3")
        title_wdg.add_color("color", "color")
        title_wdg.add_style("margin: 0px -10px 5px -10px")


        swap = SwapDisplayWdg.get_triangle_wdg(is_open)
        title_wdg.add(swap)

        title_wdg.add_class("hand")
        title_wdg.add(title)


        cbjs_action = '''
            var top = bvr.src_el.getParent('.spt_columns');
            var content = top.getElement('.spt_columns_list');
            spt.toggle_show_hide(content);
        '''


        behavior = {
            'type': 'click_up',
            'cbjs_action': '''
            %s
            %s
            ''' % (cbjs_action, swap.get_swap_script() )
        }
        title_wdg.add_behavior(behavior)
        swap.add_action_script(cbjs_action)


        title_wdg.add_style("margin-bottom: 3px")
        title_wdg.add_style("font-weight: bold")
        title_wdg.add_style("font-size: 12px")

        elements_wdg = DivWdg()
        elements_wdg.add_class("spt_columns_list")
        content_wdg.add(elements_wdg)
        if not is_open:
            elements_wdg.add_style("display: none")



        #num_elements = len(element_names)
        #if num_elements > 10:
        #    elements_wdg.add_style("max-height: 200")
        #    elements_wdg.add_style("height: 200")
        #    elements_wdg.add_style("overflow-y: auto")
        #    elements_wdg.add_style("overflow-x: hidden")
        #elements_wdg.add_border()
        #elements_wdg.add_style("margin: -5 -11 10 -11")


        if not element_names:
            menu_item = DivWdg()
            menu_item.add("&nbsp;&nbsp;&nbsp;&nbsp;<i>-- None Found --</i>")
            elements_wdg.add(menu_item)
            return content_wdg

        search_type = my.kwargs.get("search_type")
        search_type_obj = SearchType.get(search_type)
        table = search_type_obj.get_table()
        project_code = Project.get_project_code()

        security = Environment.get_security()

        for element_name in element_names:
            menu_item = DivWdg(css='hand')
            menu_item.add_class("spt_column")
            menu_item.add_style("height: 28px")

            checkbox = CheckboxWdg("whatever")
            if browser == 'Qt':
                checkbox.add_style("margin: -3px 5px 8px 0px")
            else:
                checkbox.add_style("margin-top: 1px")
            # undo the click.. let the div bvr take care of the toggling
            checkbox.add_behavior({'type':'click', 'cbjs_action': 'bvr.src_el.checked=!bvr.src_el.checked;'})
            if element_name in my.current_elements:
                checkbox.set_checked()

            checkbox.add_style("height: 16px")
            checkbox = DivWdg(checkbox)
            checkbox.add_style("float: left")

            attrs = my.config.get_element_attributes(element_name)

            default_access = attrs.get("access")
            if not default_access:
                default_access = "allow"

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
            is_viewable = security.check_access('element', access_keys, "view", default=default_access)
            is_editable = security.check_access('element', access_keys, "edit", default=default_access)
            if not is_viewable and not is_editable:
                continue



            help_alias = attrs.get("help");
            if help_alias:
                menu_item.add_attr("spt_help", help_alias)
            else:
                menu_item.add_attr("spt_help", "%s_%s" % (table, element_name))


            title = attrs.get("title")
            if not title:
                title = Common.get_display_title(element_name)
            title = title.replace("\n", " ")
            title = title.replace("\\n", " ")

            if len(title) > 45:
                title = "%s ..." % title[:42]
            else:
                title = title


            full_title = "%s <i style='opacity: 0.5'>(%s)</i>" % ( title, element_name)
            display_title = full_title
            


            #menu_item.add_attr("title", full_title)
            menu_item.add(checkbox)
            menu_item.add("&nbsp;&nbsp;")
            menu_item.add(display_title)
            menu_item.add_behavior({
            'type': "click_up", 
            'cbjs_action': '''

            var panel;
            var popup = bvr.src_el.getParent(".spt_popup");
            if (popup) {
                var panel = popup.panel;
                if (!panel) {
                    var activator = popup.activator;
                    if (activator) {
                        panel = activator.getParent(".spt_panel");
                    }
                }
            }

            if (!panel) {
                panel = $('%s');
            }

            if (!panel) {
                spt.alert('Please re-open the Column Manager');
                return;
            }
            var table = panel.getElement(".spt_table");
            spt.dg_table.toggle_column_cbk(table,'%s','%s');
            cb = bvr.src_el.getElement('input[type=checkbox]');
            cb.checked=!cb.checked;
            ''' % (my.target_id, element_name, widget_idx )
            })


            # mouse over colors
            color = content_wdg.get_color("background", -15)
            menu_item.add_event("onmouseover", "this.style.background='%s'" % color)
            menu_item.add_event("onmouseout", "this.style.background=''")

            elements_wdg.add(menu_item)


        return content_wdg




    def get_display(my):
        top = my.top
        top.add_style("width: 400px")

        search_type = my.kwargs.get("search_type")
        search_type_obj = SearchType.get(search_type)


        #my.current_elements = ['asset_library', 'code']
        my.current_elements = my.kwargs.get('element_names')
        if not my.current_elements:
            my.current_elements = []



        my.target_id = my.kwargs.get("target_id")



        #popup_wdg = PopupWdg(id=my.kwargs.get("popup_id"), opacity="0", allow_page_activity="true", width="400px")
        #title = "Column Manager (%s)" % search_type
        #popup_wdg.add(title, "title")

        # hardcode to insert at 3, this will be overridden on client side
        widget_idx = 3

        top.add_color("background", "background")
        top.add_border()

        shelf_wdg = DivWdg()
        top.add(shelf_wdg)
        #context_menu.add(shelf_wdg)
        shelf_wdg.add_style("padding: 5px 5px 0px 5px")


        from tactic.ui.app import HelpButtonWdg
        help_button = HelpButtonWdg(alias='main')
        shelf_wdg.add(help_button)
        help_button.add_style("float: right")


        context_menu = DivWdg()
        top.add(context_menu)
        context_menu.add_class("spt_column_manager")

        context_menu.add_style("padding: 0px 10px 10px 10px")
        #context_menu.add_border()
        context_menu.add_color("color", "color")
        context_menu.add_style("max-height: 500px")
        context_menu.add_style("overflow-y: auto")
        context_menu.add_style("overflow-x: hidden")



        from tactic.ui.widget import ActionButtonWdg
        add_button = ActionButtonWdg(title="Add")
        shelf_wdg.add(add_button)
        shelf_wdg.add("<br clear='all'/>")

        title = my.kwargs.get("title")
        add_button.add_behavior( {
            'type': 'click_up',
            'title': title,
            'search_type': search_type,
            'cbjs_action': '''
            var class_name = 'tactic.ui.startup.column_edit_wdg.ColumnEditWdg';
            var kwargs = {
                search_type: bvr.search_type
            }
            spt.panel.load_popup(bvr.title, class_name, kwargs);
            '''
        } )



        my.config = WidgetConfigView.get_by_search_type(search_type, "definition")

        predefined_element_names = ['preview', 'edit_item', 'delete', 'notes', 'notes_popup', 'task', 'task_edit', 'task_schedule', 'task_pipeline_panels', 'task_pipeline_vertical', 'task_pipeline_report', 'task_status_history', 'task_status_summary', 'completion', 'file_list', 'group_completion', 'general_checkin_simple', 'general_checkin', 'explorer', 'show_related', 'detail', 'notes_sheet', 'work_hours', 'history', 'summary', 'metadata']
        predefined_element_names.sort()


        # define a finger menu
        finger_menu, menu = my.get_finger_menu()
        context_menu.add(finger_menu)

        menu.set_activator_over(context_menu, "spt_column", top_class='spt_column_manager', offset={'x':10,'y':0})
        menu.set_activator_out(context_menu, "spt_column", top_class='spt_column_manager')




        defined_element_names = []
        for config in my.config.get_configs():
            if config.get_view() != 'definition':
                continue
            file_path = config.get_file_path()
            #print "file_path: ", file_path
            if file_path and file_path.endswith("DEFAULT-conf.xml") or file_path == 'generated':
                continue

            element_names = config.get_element_names()
            for element_name in element_names:
                if element_name not in defined_element_names:
                    defined_element_names.append(element_name)

        column_info = SearchType.get_column_info(search_type)
        columns = column_info.keys()
        for column in columns:
            if column == 's_status':
                continue
            if column not in defined_element_names:
                defined_element_names.append(column)

        #definition_config = my.config.get_definition_config()
        #if definition_config:
        #    defined_element_names = definition_config.get_element_names()
        #else:
        #    #defined_element_names = my.config.get_element_names()
        #    defined_element_names = []

        defined_element_names.sort()
        title = 'Custom Widgets'
        context_menu.add( my.get_columns_wdg(title, defined_element_names, is_open=True) )



        # Add custom layout widgets
        search = Search("config/widget_config")
        search.add_filter("widget_type", "column")
        configs = search.get_sobjects()
        if configs:
            element_names = [x.get_value("view") for x in configs]

            title = "Custom Layout Columns"
            context_menu.add( my.get_columns_wdg(title, element_names) )



        # Add predefined columns
        def_db_config = WidgetDbConfig.get_by_search_type("ALL", "definition")
        if def_db_config:
            element_names = def_db_config.get_element_names()
            predefined_element_names.extend(element_names)

        title = "Built-in Widgets"
        context_menu.add( my.get_columns_wdg(title, predefined_element_names) )



        # schema defined columns for foreign keys
        element_names = []
        view_schema_columns = True
        if view_schema_columns:

            # get the database columns
            schema = Schema.get()
            xml = schema.get_xml_value("schema")
            connects = xml.get_nodes("schema/connect[@from='%s']" % search_type)


            for connect in connects:
                to_search_type = Xml.get_attribute(connect, 'to')
                to_search_type_obj = SearchType.get(to_search_type, no_exception=True)
                if not to_search_type_obj:
                    continue


                column = Xml.get_attribute(connect, 'from_col')
                implied_foreign_key = False
                if not column:
                    column = SearchType.get_foreign_key(to_search_type)
                    implied_foreign_key = True


                element_names.append(column)


            #context_menu.add(HtmlElement.br())
            #title = "Schema Columns"
            #context_menu.add( my.get_columns_wdg(title, element_names) )


 
 

        # check to see if the user is allowed to add db_columns
        default = "deny"
        group = "db_columns"

        view_db_columns = True
        #if view_db_columns:
        security = Environment.get_security()
        if security.check_access("builtin", "view_site_admin", "allow"):

            # get the database columns
            column_info = SearchType.get_column_info(search_type)
            columns = column_info.keys()

            columns.sort()
            context_menu.add( my.get_columns_wdg("Database Columns", columns) )

 
        #popup_wdg.add(context_menu, "content")
        #return popup_wdg
        return top


    def get_finger_menu(my):

        # handle finger menu
        top_class = "spt_column_manager"
        from tactic.ui.container import MenuWdg, MenuItem
        menu = MenuWdg(mode='horizontal', width = 25, height=20, top_class=top_class)


        menu_item = MenuItem('action', label=IconWdg("Show Help", IconWdg.HELP_BUTTON))
        menu.add(menu_item)
        menu_item.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            if (!spt.help) return;
            spt.help.set_top();
            var menu = spt.table.get_edit_menu(bvr.src_el);
            var activator = menu.activator_el; 
            var help_alias = activator.getAttribute("spt_help");
            spt.help.load_alias(help_alias);
            '''
        } )

        # finger menu container
        widget = DivWdg()
        widget.add_class(top_class)
        widget.add_styles('position: absolute; display: none; z-index: 1000')
        widget.add(menu)

        return widget, menu

 





class EditColumnDefinitionWdg(BaseRefreshWdg):

    def get_args_keys(my):
        return {
            "search_type": "search_type to list all the possible columns",
            "view": "view of the config",
            "element_name": "name of the element_name",
            "popup_id": "id to assign to the popup this widget creates",
            "refresh": "is this a refresh"
        }




    def set_as_panel(my, widget):
        widget.add_class("spt_panel")

        widget.add_attr("spt_class_name", Common.get_full_class_name(my) )
        for name, value in my.kwargs.items():
            widget.add_attr("spt_%s" % name, value)

       


    def init(my):
        my.error = None
        refresh = my.kwargs.get("refresh")



    def get_display(my):

        search_type = my.kwargs.get("search_type")
        view = my.kwargs.get("view")
        
        element_name = my.kwargs.get("element_name")
        refresh = my.kwargs.get("refresh")

      

        widget = DivWdg()   
        # get the definition of the config element
        # try the db first
        config_view = WidgetConfigView.get_by_search_type(search_type, view)
        node = config_view.get_element_node(element_name, True) 
       
        if not node:
            config_string = "<No definition>"
        else:
            config_string = config_view.get_xml().to_string(node)

        content_wdg = DivWdg()

        if my.error:
            content_wdg.add(my.error)

        content_wdg.set_id("EditColumnDefinitionWdg_panel")
        my.set_as_panel(content_wdg)

        # display definition
        content_wdg.add("Table Display")
        content_wdg.add("<br/>")
        text = TextAreaWdg('display_definition')
        text.set_option("rows", "10")
        text.set_option("cols", "65")
        text.set_value(config_string)
        content_wdg.add(text)


        # get the EDIT definition of the config element
        config_view = WidgetConfigView.get_by_search_type(search_type, "edit")
        node = config_view.get_element_node(element_name, True)
        if not node:
            config_string = "<No definition>"
        else:
            config_string = config_view.get_xml().to_string(node)


        content_wdg.add("<br/><br/>")

        # edit definition
        content_wdg.add("<br/>")

        swap = SwapDisplayWdg.get_triangle_wdg()
        text = TextAreaWdg('edit_definition')

        # if it is not processed in the Cbk, may as well grey it out
        text.add_class('look_smenu_disabled')
        text.set_option("rows", "10")
        text.set_option("cols", "65")
        text.set_value(config_string)

        title = SpanWdg('Edit Panel Display (View only)')
        div = DivWdg(text)
        SwapDisplayWdg.create_swap_title(title, swap, div)
        content_wdg.add(swap)
        content_wdg.add(title)
        content_wdg.add(div)

        #switch = DivWdg()
        #switch.add("Switch all others [%s] columns?" % element_name)
        #content_wdg.add(switch)
        content_wdg.add( HtmlElement.hr() )
        
        behavior_edit = {
            'type': 'click_up',
            'cbjs_action': 'spt.dg_table_action.edit_definition_cbk(evt, bvr)',
            'options': {
                'search_type': search_type,
                'element_name': element_name
            }
            #'values': "spt.api.Utility.get_input(spt.popup.get_popup(bvr.src_el) , 'save_view');"

           

        }
        behavior_cancel = {
            'type': 'click_up',
            'cbjs_action': "spt.popup.destroy( spt.popup.get_popup( bvr.src_el ) );"
        }
        button_list = [{'label':  "Save" , 'bvr': behavior_edit},
                {'label':  "Cancel", 'bvr': behavior_cancel}]        
        edit_close = TextBtnSetWdg( buttons=button_list, spacing =6, size='large', \
                align='center',side_padding=10)

       
        default_view = 'definition'
        select=  SelectWdg('save_view', label='Save for: ')
        select.set_persist_on_submit()
        select.add_empty_option('-- Select --', '')
        select.set_option('labels', [default_view, 'current view'])
        select.set_option('values',[default_view,view])

        content_wdg.add(select)

        from pyasm.widget import HintWdg
        help = HintWdg('If saved for definition, it affects the display in all the views for this search type.')
        content_wdg.add(help)
        content_wdg.add(HtmlElement.br(2))
        content_wdg.add(edit_close)

        # FIXME: is there a way to avoid this??
        if refresh:
            return content_wdg

        
        widget.add(content_wdg)

        return widget



class EditColumnDefinitionCbk(Command):

    def get_title(my):
        return "Edit Column Definition"

    def execute(my):
        search_type = my.kwargs.get('search_type')
        element_name = my.kwargs.get('element_name')
        #view = my.kwargs.get('view')

        search_type = SearchType.get(search_type).get_base_key()

        web = WebContainer.get_web()
        display_config = web.get_form_value("display_definition")
        save_view = web.get_form_value("save_view")

        default_view = "definition"
        if not save_view:
            save_view = default_view
        # FIXME: taken from client API (set_config_definition() )
        # ... should centralize
        config_search_type = "config/widget_config"
        search = Search(config_search_type)
        search.add_filter("search_type", search_type)
        search.add_filter("view", save_view)
        config = search.get_sobject()
        if not config:
            if save_view != 'definition':
                # raise exception 'cuz the user should save out a view first
                raise UserException('You should save out a view first before editing the column definition for this specific view [%s]' % save_view)

            config = SearchType.create(config_search_type)
            config.set_value("search_type", search_type )
            config.set_value("view", save_view )

            # create a new document
            xml = Xml()
            xml.create_doc("config")
            root = xml.get_root_node()
            view_node = xml.create_element( save_view )
            #root.appendChild(view_node)
            xml.append_child(root, view_node)

            config.set_value("config", xml.to_string())
            
            config._init()


        # update the definition
        config.append_xml_element(element_name, display_config)
            
        config.commit_config()

        my.add_description("Saved column definition [%s] for [%s] in view [%s]" %(element_name, search_type, save_view)) 
        # update the edit definition
        #edit_definition = web.get_form_value("edit_definition")
        #edit_view = "edit_definition"
        #edit_config = my.get_config(search_type, edit_view)
        #edit_config.append_xml_element(element_name, edit_definition)
        #edit_config.commit_config()



    def get_config(my, search_type, view):

        # FIXME: taken from client API (set_config_definition() )
        # ... should centralize
        config_search_type = "config/widget_config"
        search = Search(config_search_type)
        search.add_filter("search_type", search_type)
        search.add_filter("view", view)
        config = search.get_sobject()
        if not config:
            

            config = SearchType.create(config_search_type)
            config.set_value("search_type", search_type )
            config.set_value("view", view )

            # create a new document
            xml = Xml()
            xml.create_doc("config")
            root = xml.get_root_node()
            view_node = xml.create_element(view)
            #root.appendChild(view_node)
            xml.append_child(root, view_node)

            config.set_value("config", xml.to_string())
            config._init()

        return config


