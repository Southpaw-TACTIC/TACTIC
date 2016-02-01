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
__all__ = ["FastTableLayoutWdg", "TableLayoutWdg", "TableGroupManageWdg"]

import os
import re
import types
import copy
from dateutil import parser, rrule
from datetime import datetime, timedelta

from pyasm.common import Common, jsonloads, jsondumps, Environment, Container
from pyasm.search import Search, SearchKey, SObject, SearchType, SearchException
from pyasm.web import DivWdg, Table, HtmlElement, WebContainer, FloatDivWdg
from pyasm.widget import ThumbWdg, IconWdg, WidgetConfig, WidgetConfigView, SwapDisplayWdg, CheckboxWdg

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.container import SmartMenu

from pyasm.biz import Project, ExpressionParser, Subscription
from tactic.ui.table import ExpressionElementWdg, PythonElementWdg
from tactic.ui.common import BaseConfigWdg
from tactic.ui.widget import ActionButtonWdg

from base_table_layout_wdg import BaseTableLayoutWdg
#class FastTableLayoutWdg(TableLayoutWdg):


class FastTableLayoutWdg(BaseTableLayoutWdg):
    SCROLLBAR_WIDTH = 17
    ARGS_KEYS = {

        "mode": {
            'description': "Determines whether to draw with widgets or just use the raw data",
            'type': 'SelectWdg',
            'values': 'widget|raw',
            'order': 00,
            'category': 'Required'
        },

        "search_type": {
            'description': "search type that this panels works with",
            'type': 'TextWdg',
            'order': 01,
            'category': 'Required'
        },
        "view": {
            'description': "view to be displayed",
            'type': 'TextWdg',
            'order': 02,
            'category': 'Required'
        },
        'search_limit': {
            'description': 'The limit of items for each page',
             'category': 'Display',
             'order': '01'
        },
        'expression': {
            'description': 'Use an expression to drive the search.  The expression must return sObjects e.g. @SOBJECT(sthpw/task)',
             'category': 'Display',
             'type': 'TextAreaWdg',
             'order': '01'
        },
        "element_names": {
            'description': "Comma delimited list of elemnent to view",
            'type': 'TextWdg',
            'order': 00,
            'category': 'Optional'
        },
        "show_shelf": {
            'description': "Determines whether or not to show the action shelf",
            'type': 'SelectWdg',
            'values': 'true|false',
            'order': 01,
            'category': 'Optional'
        },
        "show_header": {
            'description': "Determines whether or not to show the table header",
            'type': 'SelectWdg',
            'values': 'true|false',
            'order': 02,
            'category': 'Optional'
        },
        "show_select": {
            'description': "Determine whether to show the selection checkbox for each row",
            'type': 'SelectWdg',
            'values': 'true|false',
            'order': 03,
            'category': 'Optional'
        },

        'show_search_limit': {
            'description': 'Flag to determine whether or not to show the search limit',
            'category': 'Optional',
            'type': 'SelectWdg',
            'values': 'true|false',
            'order': '04'
        },
       'search_limit_mode': {
            'description': 'Determine whether to show the simple search limit at just top, bottom, or both',
            'category': 'Optional',
            'type': 'SelectWdg',
            'values': 'bottom|top|both',
            'order': '04a'
        },





        'show_column_manager': {
            'description': 'Flag to determine whether or not to show the column manager button',
            'category': 'Optional',
            'type': 'SelectWdg',
            'values': 'true|false',
            'order': '05'
        },
        'show_layout_switcher': {
            'description': 'Flag to determine whether or not to show the Switch Layout button',
            'category': 'Optional',
            'type': 'SelectWdg',
            'values': 'true|false',
            'order': '06'
        },

       'show_keyword_search': {
            'description': 'Flag to determine whether or not to show the Keyword Search button',
            'category': 'Optional',
            'type': 'SelectWdg',
            'values': 'true|false',
            'order': '07'
        },
        'show_context_menu': {
            'description': 'Flag to determine whether to show the tactic context menu, default, or none',
            'category': 'Optional',
            'type': 'SelectWdg',
            'values': 'true|false|none',
            'order': '08'
        },

        
        'checkin_context': {
            'description': 'override the checkin context for Check-in New File',
            'category': 'Optional',
            'type': 'SelectWdg',
            'empty': 'true',
            'values': 'auto|strict',
            'order': '09'
        },
         'checkin_type': {
            'description': 'override the checkin type for Check-in New File',
            'category': 'Optional',
            'type': 'TextWdg',
            'order': '10'
        },
        'ingest_data_view': {
            'description': 'a view similar to edit view that defines any data to be saved with each ingested sobject.',
            'type': 'TextWdg',
            'category': 'Optional',
            'order': '11'
        },

        'init_load_num': {
            'description': 'set the number of rows to load initially. If set to -1, it will not load in chunks',
            'type': 'TextWdg',
            'category': 'Optional',
            'order': '12'
        },

        'expand_on_load': {
            'description': 'expands the table on load, ignore column widths',
            'type': 'TextWdg',
            'category': 'Optional',
            'order': '13'
        },


        "show_border": {
            'description': "determines whether or not to show borders on the table",
            'type': 'SelectWdg',
            'values': 'true|false',
            "order": '14',
            'category': 'Display'
        },
 
 

        "temp" : {
            'description': "Determines whether this is a temp table just to retrieve data",
            'category' : 'internal'
        },

        "no_results_msg" : {
            'description': 'the message displayed when the search returns no item',
            'type': 'TextWdg',
            'category': 'Display',
            'Order': '14'
        },

        "no_results_mode" : {
            'description': 'the display modes for no results',
            'type': 'SelectWdg',
            'values': 'default|compact',
            'category': 'Display',
            'order': '15'
        },

        "show_collection_tool": {
            'description': 'determines whether to show the collection button or not',
            'type': 'SelectWdg',
            'values': 'true|false',
            'category': 'Display',
            'order': '16'
        }
        


    } 

    GROUP_COLUMN_PREFIX = "__group_column__"


    def get_layout_version(my):
        return "2"


    def remap_display_handler(my, display_handler):
        if display_handler == "HiddenRowToggleWdg":
            return "tactic.ui.table.HiddenRowElementWdg"
        elif display_handler == "pyasm.widget.HiddenRowToggleWdg":
            return "tactic.ui.table.HiddenRowElementWdg"

    def remap_sobjects(my):
        # find all the distinct search types in the sobjects
        if not my.search_type.startswith("sthpw/sobject_list"):
            return

        # don't remap if it's the default table view when the user is
        # viewing raw data
        if my.view == 'table':
            return

        search_types_dict = {}
        for row, sobject in enumerate(my.sobjects):

            if sobject.is_insert():
                continue

            # it is possible that, even though my.search_type is "sobject_list",
            # that an individual sobject is not of this type ... this is
            # true on updates or other searches where search_keys are given
            if sobject.get_search_type() != "sthpw/sobject_list":
                continue

            search_type = sobject.get_value("search_type")
            if not search_type:
                print "WARNING: sobject_list entry [%s] has no search_type" % sobject.get_id()
                continue


            search_types_list = search_types_dict.get(search_type)
            if search_types_list == None:
                search_types_list = []
                search_types_dict[search_type] = search_types_list

            search_types_list.append((row,sobject))

        deleted = {}
        for search_type, sobjects in search_types_dict.items():
            try:
                search = Search(search_type)
            except SearchException, e:
                # it may have been deleted
                # show it as is, without remapping
                print str(e)
                continue
            ids = [x.get_value("search_id") for row, x in sobjects]
            search.add_filters("id", ids)
            parents = search.get_sobjects()
            parents_dict = {}
            for parent in parents:
                parents_dict[parent.get_id()] = parent

            for row, sobject in sobjects:
                search_id = sobject.get_value("search_id")
                parent = parents_dict.get(search_id)
                if parent != None:
                    my.sobjects[row] = parent
                else:
                    # FIXME: what if this sobject does not exist anymore???
                    deleted[row] = sobject
                    


        rows = deleted.keys()
        rows.sort()
        rows.reverse()

        #for row in rows:
            #sobject = deleted[row]
            #my.sobjects.pop(row)
        # we want to show the dangling sobject_list item so user can delete them
        # only available when not in refresh
        if my.search_wdg:
            search = my.search_wdg.get_search()
            total_count = search.get_count()
            # NOTE: this logic is only effective if the deleted/invalid is found
            # in this page being drawn
        else:
            total_count = len(my.sobjects)
            
        total_count -= len(rows)
        my.items_found = total_count


    def process_groups(my):

        my.widget_summary_option = {}
        my.group_values = {}
        my.group_ids = {}
        my.group_rows = []
        my.level_name = ''
        my.level_spacing = 20

        my.is_on = True
        my.grouping_data = False

        my.group_mode = my.kwargs.get("group_mode")
        if not my.group_mode:
            my.group_mode = "top"

        # boolean for if there are real-time evaluated grouping data store in __group_column__<idx>
        my._grouping_data = {}
        my.group_by_time = {}

        # set some grouping parameters
        my.current_groups = []
        if my.group_element:
            if my.group_element in [True, False, '']: # Backwards compatibiity
                my.group_columns = []
            else:
                my.group_columns = my.group_element.split(',')
        else:
            my.group_columns = my.kwargs.get("group_elements")
            if not my.group_columns or my.group_columns == ['']: # Backwards compatibility
                my.group_columns = []
            if isinstance(my.group_columns, basestring):
                if not my.group_columns.startswith('['):
                    my.group_columns = my.group_columns.split(',')
                else:

                    eval(my.group_columns)

        #my.group_columns = ['timestamp']
        #my.group_interval = TableLayoutWdg.GROUP_WEEKLY
        if not my.group_columns:
            from tactic.ui.filter import FilterData
            filter = my.kwargs.get("filter")
            values = {}
            if filter and filter != 'None':
                
                filter_data = FilterData(filter)
                values_list = filter_data.get_values_by_prefix("group")
                if values_list:
                    values = values_list[0]

            if values.get("group"):
                my.group_columns = [values.get("group")]
                my.group_interval = values.get("interval")
        my.is_grouped = len(my.group_columns) > 0
        my.table.add_attr("spt_group_elements", ",".join(my.group_columns))

        # grouping preprocess , check the type of grouping  
        if my.is_grouped and my.sobjects:
            search_type = my.sobjects[0].get_search_type()
            for group_column in my.group_columns:
                element_type = SearchType.get_tactic_type(my.search_type, group_column)
                my.group_by_time[group_column] = element_type in ['time', 'date', 'datetime']


        # initialize group_values
        for i, col in enumerate(my.group_columns):
            group_value_dict = {}
            my.group_values[i] = group_value_dict





    def check_access(my):
        '''check access for each element'''
        my.edit_permission_columns = {}
        filtered_widgets = []
        
        project_code = Project.get_project_code() 
        security = Environment.get_security()
        for i, widget in enumerate(my.widgets):
            element_name = widget.get_name()
            # get all the attributes
            if element_name and element_name != "None":
                attrs = my.config.get_element_attributes(element_name)
                widget.set_attributes(attrs)
            else:
                attrs = {}
            
            my.attributes.append(attrs)


            # defined access for this view
            def_default_access = attrs.get('access')
            if not def_default_access:
                def_default_access = 'edit'


            # check security access
            access_key2 = {
                'search_type': my.search_type,
                'project': project_code
            }
            access_key1 = {
                'search_type': my.search_type,
                'key': element_name, 
                'project': project_code

            }
            access_keys = [access_key1, access_key2]
            is_viewable = security.check_access('element', access_keys, "view", default=def_default_access)
            is_editable = security.check_access('element', access_keys, "edit", default=def_default_access)

            if not is_viewable:
                # don't remove while looping, it disrupts the loop
                #my.widgets.remove(widget)
                my.attributes.pop()
            elif not is_editable:
                my.edit_permission_columns[element_name] = False
                filtered_widgets.append(widget)
            else:
                my.edit_permission_columns[element_name] = True
                filtered_widgets.append(widget)

        # reassign the widgets that pass security back to my.widgets
        my.widgets = filtered_widgets




    def _process_search_args(my):

        # this is different name from the old table selected_search_keys
        search_keys = my.kwargs.get("search_keys")
      
        # if a search key has been explicitly set without expression, use that
        expression = my.kwargs.get('expression') 
        matched_search_key = False
        if my.search_key:
            base_search_type = SearchKey.extract_base_search_type(my.search_key)
        else:
            base_search_type = ''

        if my.search_type == base_search_type:
            matched_search_key = True
        if search_keys and search_keys != '[]':
            if isinstance(search_keys, basestring):
                if search_keys == "__NONE__":
                    search_keys = []
                else:
                    search_keys = search_keys.split(",")

            # keep the order for precise redrawing/ refresh_rows purpose
            if not search_keys:

                my.sobjects = []
            else:
                my.sobjects = Search.get_by_search_keys(search_keys, keep_order=True)

            my.items_found = len(my.sobjects)
            # if there is no parent_key and  search_key doesn't belong to search_type, just do a general search
        elif my.search_key and matched_search_key and not expression:
            sobject = Search.get_by_search_key(my.search_key)
            if sobject: 
                my.sobjects = [sobject]
                my.items_found = len(my.sobjects)


        elif my.kwargs.get("do_search") != "false":
            my.handle_search()

        elif my.kwargs.get("sobjects"):
            my.sobjects = my.kwargs.get("sobjects")





    def get_display(my):

        # fast table should use 0 chunk size
        my.chunk_size = 0

        my.timer = 0

        my.edit_permission = True
        
        view_editable = my.view_attributes.get("edit")

        if not view_editable:
            view_editable = my.kwargs.get("edit")
        if view_editable in ['false', False]:
            my.view_editable = False
        else:
            my.view_editable = True
        my.color_maps = my.get_color_maps()

        from pyasm.web import WebContainer
        web = WebContainer.get_web()
        my.browser = web.get_browser()

        my.error_columns = set()
        
        
        my.expand_on_load = my.kwargs.get("expand_on_load")
       
        if my.expand_on_load in [False, 'false']:
            my.expand_on_load = False
        else:
            my.expand_on_load = True


        my.sobject_levels = []


        # Make this into a function.  Former code is kept here for now.
        my._process_search_args()

        # set some grouping parameters
        my.process_groups()

        if my.kwargs.get('temp') != True:
            my.sobjects = my.order_sobjects(my.sobjects, my.group_columns)
            my.remap_sobjects()

        for sobject in my.sobjects:
            my.sobject_levels.append(0)


        # Force the mode to widget because raw does work with FastTable
        # anymore (due to fast table constantly asking widgets for info)
        #my.mode = my.kwargs.get("mode")
        #if my.mode != 'raw':
        #    my.mode = 'widget'
        my.mode = 'widget'


        top = my.top
        my.set_as_panel(top)
        top.add_class("spt_sobject_top")
        top.add_class("spt_layout_top")

        # FIXME: still need to set an id for Column Manager
        top.set_id("%s_layout" % my.table_id)

        inner = DivWdg()
        top.add(inner)
        inner.add_color("background", "background")
        inner.add_color("color", "color")
        # FIXME: this is not the table and is called this for backwards
        # compatibility
        inner.add_class("spt_table")
        inner.add_class("spt_layout")
        inner.add_style("border-style", "solid")
        inner.add_style("border-width: 0px")
        inner.add_style("border-color", inner.get_color("border"))
        has_extra_header = my.kwargs.get("has_extra_header")
        if has_extra_header in [True, "true"]:
            inner.add_attr("has_extra_header", "true")


        #if my.config_xml:
        #    inner.add_attr("spt_config_xml", my.config_xml)

        save_class_name = my.kwargs.get("save_class_name")
        if save_class_name:
            inner.add_attr("spt_save_class_name", save_class_name)

        # The version of the table so that external callbacks
        # can key on this
        inner.add_attr("spt_version", "2")
        inner.add_style("position: relative")




        if my.kwargs.get('temp') != True:
            
            if not Container.get_dict("JSLibraries", "spt_html5upload"):
                # add an upload_wdg
                from tactic.ui.input import Html5UploadWdg
                upload_wdg = Html5UploadWdg()
                inner.add(upload_wdg)
                my.upload_id = upload_wdg.get_upload_id()
                inner.add_attr('upload_id',my.upload_id)
            
            # get all client triggers
            exp = "@SOBJECT(config/client_trigger['event','EQ','%s$'])" %my.search_type
            client_triggers = Search.eval(exp)

            
            # set unique to True to prevent duplicated event registration when opening multiple tables
            # listens to event like accept|sthpw/task
            for client_trigger in client_triggers:
                 inner.add_behavior( {
                'type': 'listen',
                'unique' : True,
                'event_name': client_trigger.get_value('event'),
                'script_path': client_trigger.get_value('callback'),
                'cbjs_action': '''
                if (bvr.firing_element) {
                    var layout = bvr.firing_element.getParent(".spt_layout");
                    if (layout)
                        spt.table.set_table(bvr.firing_element);
                }

                var input = bvr.firing_data;
                //var new_value = input.new_value;
                
                // 2nd arg is the args for this script
                spt.CustomProject.run_script_by_path(bvr.script_path, bvr.firing_data);
                '''
                })

            # for redraw of a row, fire update_row|project/asset
            inner.add_behavior( {
                'type': 'listen',
                'unique' : True,
                'event_name': 'update_row|%s' %my.search_type,
                'cbjs_action': '''

                var table = spt.table.get_table();
                var input = bvr.firing_data;
                if (input.search_key) {
                    var row = table.getElement('.spt_table_row[spt_search_key=' + input.search_key+ ']');
                    var sks = [input.search_key];
                    spt.table.refresh_rows([row], sks, {}) 
                }
                '''
                })


        # TEST: client trigger
        """
        inner.add_behavior( {
            'type': 'listen',
            'event_name': 'change|project/asset',
            'cbjs_action': '''
            spt.table.set_table(bvr.firing_element);

            var input = bvr.firing_data;
            var new_value = input.new_value;
            if (new_value == 'cow') {
                spt.table.add_hidden_row(input.row, "tactic.ui.widget.CalendarWdg");
                input.row.setStyle("background-color", "#0FF");
                input.row.setAttribute("spt_background", "#0FF");
            }

            '''
        } )
        """


        # set up hidden div to hold validation behaviors only for the edit widgets that have
        # validations configured on them ...
        #
        my.validations_div = DivWdg()
        my.validations_div.add_class("spt_table_validations")
        my.validations_div.add_styles("display: none;")
        inner.add(my.validations_div)


        my.check_access()

        # set the sobjects to all the widgets then preprocess
        if my.mode == 'widget':
            for widget in my.widgets:
                widget.set_sobjects(my.sobjects)
                widget.set_parent_wdg(my)
                # preprocess the elements
                widget.preprocess()
                
                my.widget_summary_option[widget] = widget.get_option("total_summary")



        #is_refresh = my.kwargs.get("is_refresh")

        if my.kwargs.get("show_shelf") not in ['false', False]:
            # draws the row of buttons to insert and refresh
            action = my.get_action_wdg()
            inner.add(action)
        # get all the edit widgets
        if my.view_editable and my.edit_permission:
            my.edit_wdgs = my.get_edit_wdgs()
            edit_div = DivWdg()
            edit_div.add_class("spt_edit_top")
            edit_div.add_style("display: none")
            edit_div.add_border()
            inner.add(edit_div)
            for name, edit_wdg in my.edit_wdgs.items():
                # each BaseInputWdg knows about this FastTableLayoutWdg
                edit_display = edit_wdg.get_display_wdg()
                if edit_display:
                    edit_display.set_parent_wdg(my)
                edit_div.add(edit_wdg)
        else:
            my.edit_wdgs = {}


        # -- GROUP SPAN - this is to show hidden elements for ordering and
        # grouping
        group_span = DivWdg()
        group_span.add_style("display: none")
        group_span.add_class("spt_table_search")
        group_span.add(my.get_group_wdg() )
        inner.add(group_span)

        info = my.search_limit.get_info()
        if info.get("count") == None:
            info["count"] = len(my.sobjects)

        search_limit_mode = my.kwargs.get('search_limit_mode') 
        if not search_limit_mode:
            search_limit_mode = 'bottom'

        if my.kwargs.get("show_search_limit") not in ['false', False] and search_limit_mode in ['top','both']:
            from tactic.ui.app import SearchLimitSimpleWdg
            limit_wdg = SearchLimitSimpleWdg(
                count=info.get("count"),
                search_limit=info.get("search_limit"),
                current_offset=info.get("current_offset")
            )
            inner.add(limit_wdg)

    
        # do not set it to 100% here, there are conditions later to change it to 100%
        table_width = my.kwargs.get("width")
        if not table_width:
            table_width= ''
        #table_width = '100%'
        table_width = ''


        # handle column widths
        column_widths = my.kwargs.get("column_widths")
        if not column_widths:
            column_widths = []
            # THIS IS WRONG: the Row Select is not part of the my.widgets
            # The first one is the selection widget
            #column_widths = [60]
            #my.kwargs["column_widths"] = column_widths


        my.element_names = my.config.get_element_names()  
       
        for i, widget in enumerate(my.widgets):
            
            default_width = my.kwargs.get("default_width")
            if not default_width:
                default_width = widget.get_width()
            else:
                default_width = int(default_width)

            if not default_width:
                default_width = 100
            
            width = my.attributes[i].get("width")

           
            if i >= len(column_widths):
                # default width
                if width:
                    column_widths.append(width)
                else:
                    column_widths.append(default_width)

            elif not column_widths[i]:
                column_widths[i] = default_width 



        # IS this needed?
        table_width = 30
        for i in range(0, len(column_widths)):
            width = column_widths[i]
            if isinstance(width, basestring):
                continue
            table_width += column_widths[i]

        #my.kwargs["column_widths"] = []
        #table_width = "100%"

        my.kwargs["column_widths"] = column_widths



        sticky_header = my.kwargs.get("sticky_header")
        if sticky_header in [False, 'false']:
            sticky_header = False
        else:
            sticky_header = True

        #inner.add_style("width: 100%")

        if sticky_header:

            h_scroll = DivWdg()
            inner.add(h_scroll)
            h_scroll.add_style("overflow-x: hidden")
            h_scroll.add_style("overflow-y: none")

            scroll = DivWdg()
            h_scroll.add(scroll)
            #scroll.add_style("overflow-y: hidden")
            #scroll.add_style("overflow-x: none")

            my.header_table = Table()
            scroll.add(my.header_table)


            my.header_table.add_class("spt_table_with_headers")
            my.header_table.set_unique_id()
            my.handle_headers(my.header_table)
            if table_width:
                my.header_table.add_style("width: %s" % table_width)

            scroll = DivWdg()
            h_scroll.add(scroll)
            height = my.kwargs.get("height")
            if height:
                scroll.add_style("height: %s" % height)

            # Always adding a scroll bar, but using margin-right to hide it
            #scroll.add_style("margin-right: -%spx" % my.SCROLLBAR_WIDTH)
            #scroll.add_style("overflow-y: scroll")
            scroll.add_style("overflow-y: auto")
            scroll.add_style("overflow-x: hidden")  
            if not height and my.kwargs.get("__hidden__") not in [True, 'True', 'true']:
                # set to browser height
                scroll.add_behavior( {
                    'type': 'load',
                    'cbjs_action': '''
                    var y = window.getSize().y;
                    bvr.src_el.setStyle('height', y);
                    '''
                    } )


            table = my.table
            table.add_class("spt_table_table")
            font_size = my.kwargs.get("font_size")
            if font_size:
                table.add_style("font-size: %s" % font_size)
                my.header_table.add_style("font-size: %s" % font_size)
            scroll.add(table)
            #my.handle_headers(table)
            if table_width:
                table.add_style("width: %s" % table_width)

            table.add_color("color", "color")

            my.header_table.add_style("table-layout", "fixed")
            my.table.add_style("table-layout", "fixed")

        else:
            table = my.table
            my.header_table = table

            # TEST scroll of the table
            scroll = DivWdg()
            inner.add(scroll)
            scroll.add_style("width: 100%")
            scroll.add_style("overflow-x: auto")
            scroll.add(table)

            #inner.add(table)

            table.add_class("spt_table_table")
            table.add_class("spt_table_with_headers")
            if table_width:
                table.add_style("width: %s" % table_width)
            table.add_color("color", "color")

            my.handle_headers(my.header_table)

            inner.add_style("overflow-x: auto")

        table.set_id(my.table_id)
        
        # generate dictionary of subscribed search_keys to affect context menu
        my.subscribed_search_keys = {}
        login = Environment.get_login().get("login")
        subscribed = Subscription.get_by_search_type(login, my.search_type)
        for item in subscribed:
            item_search_key = item.get("message_code")
            my.subscribed_search_keys[item_search_key] = True

        # set up the context menus
        show_context_menu = my.kwargs.get("show_context_menu")
        if show_context_menu in ['false', False]:
            show_context_menu = False
        elif show_context_menu == 'none':
            pass
        else:
            show_context_menu = True

        
        temp = my.kwargs.get("temp")
        
        if temp != True:
            menus_in = {}
            if show_context_menu:
                menus_in['DG_HEADER_CTX'] = [ my.get_smart_header_context_menu_data() ]
                menus_in['DG_DROW_SMENU_CTX'] = [ my.get_data_row_smart_context_menu_details() ]
            elif show_context_menu == 'none':
                div.add_event('oncontextmenu', 'return false;')
            if menus_in:
                SmartMenu.attach_smart_context_menu( inner, menus_in, False )


        for widget in my.widgets:
            #if my.kwargs.get('temp') != True:
            widget.handle_layout_behaviors(table)
            my.drawn_widgets[widget.__class__.__name__] = True
        


        # FIXME: this is needed because table gets the
        # class spt_table (which is also on inner).  This is done in
        # __init__ and needs to be fixed
        table.add_attr("spt_view", my.kwargs.get("view") )
        table.set_attr("spt_search_type", my.search_type)


        my.handle_table_behaviors(table)

     
        # draw 4 (even) rows initially by default
        has_loading = False
        init_load_num = my.kwargs.get('init_load_num')

        if not init_load_num:
            init_load_num = 4
        else:
            init_load_num = int(init_load_num)
       
        # override init_load_num if group column has group_bottom
        if my.has_group_bottom() or my.has_bottom_wdg():
            init_load_num = -1

        # check the widgets if there are any that can't be async loaded
        for widget in my.widgets:
            if not widget.can_async_load():
                init_load_num = -1
                break

        # minus 1 since row starts at 0
        init_load_num -= 1


        chunk_size = 20
        

        for row, sobject in enumerate(my.sobjects):

            # put in a group row
            if my.is_grouped:
                my.handle_groups(table, row, sobject)
            start_point = row - init_load_num
            mod = start_point % chunk_size

            if not temp and init_load_num >= 0  and row > init_load_num: 
                tr, td = table.add_row_cell()
                td.add_style("height: 30px")
                td.add_style("padding: 20px")
                td.add_style("text-align: center")
                if mod == 1:
                    td.add('<img src="/context/icons/common/indicator_snake.gif" border="0"/>')
                    td.add("Loading ...")
                
                tr.add_attr("spt_search_key", sobject.get_search_key(use_id=True))
                tr.add_class("spt_loading")
                has_loading = True
                continue


            level = len(my.group_columns) + my.sobject_levels[row]
            my.handle_row(table, sobject, row, level)


        if has_loading:
            table.add_behavior( {
            'type': 'load',
            'chunk': chunk_size,
            'expand_on_load': my.expand_on_load,
            'unique_id': my.get_table_id(),
            'cbjs_action': '''
            var layout = bvr.src_el.getParent(".spt_layout");
            spt.table.set_layout(layout);
            var rows = layout.getElements(".spt_loading");

            var unique_id = "loading|"+bvr.unique_id;

            var jobs = [];
            var count = 0;
            var chunk = bvr.chunk;
            while (true) {
                var job_item = rows.slice(count, count+chunk);
                if (job_item.length == 0) {
                    break;
                }
                jobs.push(job_item);
                count += chunk;
            }

            var count = -1;

            var view_panel = layout.getParent('.spt_view_panel');
            if (view_panel) {
                var search_top = view_panel.getElement('.spt_search');
                var search_dict = spt.table.get_search_values(search_top);
            }
            
            var func = function() {
                count += 1;
                var rows = jobs[count];
                if (! rows || rows.length == 0) {
                    spt.named_events.fire_event(unique_id, {});
                    // run at the end of last load
                    if (bvr.expand_on_load) {
                        spt.table.set_layout(layout);
                        spt.table.expand_table();
                    }

                    return;
                }

                spt.table.refresh_rows(rows, null, null, {on_complete: func, json: search_dict, refresh_bottom: false});
            }
            func();

            '''
            } )
        elif not temp:
            table.add_behavior( {
            'type': 'load',
            'unique_id': my.get_table_id(),
            'expand_on_load': my.expand_on_load,
            'cbjs_action': '''
                var unique_id = "loading|"+bvr.unique_id;
                spt.named_events.fire_event(unique_id, {});
                if (bvr.expand_on_load) {
                     spt.table.expand_table();
                }
            '''
            } )
 



        if not my.sobjects:
            my.handle_no_results(table)
            table.add_style("width: %s" % width)

        # refresh columns have init_load_num = -1 and temp = True
        if init_load_num < 0 or temp != True: 
            my.add_table_bottom(table)
            my.postprocess_groups()


            # extra stuff to make it work with ViewPanelWdg
            top.add_class("spt_table_top");
            class_name = Common.get_full_class_name(my)
            top.add_attr("spt_class_name", class_name)

            my.table.add_class("spt_table_content");
            inner.add_attr("spt_search_type", my.kwargs.get('search_type'))
            inner.add_attr("spt_view", my.kwargs.get('view'))

            # extra ?? Doesn't really work to keep the mode
            inner.add_attr("spt_mode", my.mode)
            top.add_attr("spt_mode", my.mode)



            # add a hidden insert table
            inner.add( my.get_insert_wdg() )
        
            
            # this simple limit provides pagination and should always be drawn. Visible where applicable
            if my.kwargs.get("show_search_limit") not in ['false', False] and search_limit_mode in ['bottom','both']:
                from tactic.ui.app import SearchLimitSimpleWdg
                limit_wdg = SearchLimitSimpleWdg(
                    count=info.get("count"),
                    search_limit=info.get("search_limit"),
                    current_offset=info.get("current_offset"),
                )
                inner.add(limit_wdg)

            my.total_count = info.get("count")
            inner.add_attr("total_count", my.total_count)


        if my.kwargs.get("is_refresh") == 'true':
            return inner
        else:
            return top

    
    def _get_simplified_time(my, group_value):
        if group_value in ['', None, '__NONE__']:
            return group_value
        group_value = str(group_value)
        if my.group_interval == BaseTableLayoutWdg.GROUP_WEEKLY:
            # put in the week
            timestamp = parser.parse(group_value)
            # days was 7, but 6 seems to count the day on the start of a week accurately
            timestamp = list(rrule.rrule(rrule.WEEKLY, byweekday=0, dtstart=timestamp-timedelta(days=6, hours=0), count=1))
            timestamp = timestamp[0]
            timestamp = datetime(timestamp.year,timestamp.month,timestamp.day)
            timestamp.strftime("%Y %b %d")
            
            group_value = timestamp.strftime("%Y-%m-%d")

        elif my.group_interval == BaseTableLayoutWdg.GROUP_MONTHLY:
            timestamp = parser.parse(group_value)
            timestamp = datetime(timestamp.year,timestamp.month,1)
            
            group_value = timestamp.strftime("%Y %m")
        else: # the default group by a regular timestamp
            group_value = timestamp = parser.parse(group_value)
            group_value = timestamp.strftime("%Y-%m-%d")

        return group_value

    def _time_test(my, group_value):
        ''' used to test if a column is in general storing time. Usually it's used such that when 
           a value looks like time, it will stop looking'''
        time_test = False
        if isinstance(group_value, datetime):
            time_test = True
        from time import strptime
        if not time_test and group_value:
            try:
                group_value = str(group_value)
                struct_time =  strptime(r'%Y-%m-%d %H:%M:%S')
                time_test = True
            except ValueError:
                try:
                    struct_time =  strptime(group_value, r'%Y-%m-%d')
                    time_test = True
                except ValueError:
                    pass
        return time_test

    def _set_eval_value(my, sobject, group_column, group_value, idx):
        '''set the evaluated value for an sobject with an index-named column''' 
        sobject.set_value("%s%s"%(my.GROUP_COLUMN_PREFIX, idx), group_value, temp=True)
        my._grouping_data[group_column] =  "%s%s"%(my.GROUP_COLUMN_PREFIX, idx)

    def order_sobjects(my, sobjects, group_columns):
        '''pre-order the sobjects if group_columns is defined, recursively'''
        if not my.group_columns:
            # post ordering for PythonElementWdg only
            if my.order_widget:
                tmp_order_element, direction  = my.get_order_element(my.order_element)
                if not isinstance(my.order_widget, PythonElementWdg):
                    return sobjects
                sobject_dict = {}
                my.order_widget.preprocess()
                reverse = direction == 'desc'
                for idx, sobject in enumerate(sobjects):
                    order_value = my.order_widget.get_result(sobject)
                    sobject_dict[sobject] = order_value

                sobjects = sorted(sobjects, key=sobject_dict.__getitem__, reverse=reverse)
            return sobjects
        my.group_dict = {}

        # identify group_column
        group_col_type_dict = {} 
        for i, group_column in enumerate(group_columns):
            is_expr = re.search("^(@|\$|{@|{\$)", group_column)
            if is_expr:
                group_col_type_dict[group_column] = 'inline_expression'
            elif my.is_expression_element(group_column):
                widget = my.get_widget(group_column)
                # initialize here
                widget.init_kwargs()
                widget.set_option('calc_mode', 'fast')
                widget.set_sobjects(sobjects)
                group_col_type_dict[group_column] = widget
                
                #break
                #group_value = expr_parser.eval(group_column, sobjects=[sobject],single=True)
                #group_value = sobject.get_value(group_column, no_exception=True)
           
            else:
                #group_col_type_dict[group_column] = 'normal'
                widget = my.get_widget(group_column)
                if widget:
                    widget.preprocess()
                    group_col_type_dict[group_column] = widget
       
        time_test = False
        expr_parser = ExpressionParser()
        
        for idx, sobject in enumerate(sobjects):
            for i, group_column in enumerate(group_columns):
                #group_column = '@GET(sthpw/task.bid_start_date)'
                if group_col_type_dict.get(group_column) == 'inline_expression':
                    group_value = expr_parser.eval(group_column, sobjects=[sobject],single=True)
                    if not time_test: 
                        time_test = my._time_test(group_value)
                  
                    if time_test == True: 
                        my.group_by_time[group_column] = True 
                        if group_value:
                            group_value = my._get_simplified_time(group_value)

                    if not group_value:
                        group_value = "__NONE__"
                    
                    my._set_eval_value(sobject, group_column, group_value, i)
                    
                elif isinstance(group_col_type_dict.get(group_column), ExpressionElementWdg):
                    widget = group_col_type_dict[group_column]
                   
                 
                    expr = widget.kwargs.get('expression')
                    group_value = widget._get_result(sobject, expr)

                    if not time_test: 
                        time_test = my._time_test(group_value)
                    else:
                        my.group_by_time[group_column] = True 

                    if my.group_interval and group_value:
                        group_value = my._get_simplified_time(group_value)
                    elif isinstance(group_value, basestring):
                        group_value = group_value.encode('utf-8')
                    else:
                        group_value = str(group_value)
                
                    if not group_value:
                        group_value = "__NONE__"
                    
                    my._set_eval_value(sobject, group_column, group_value, i)
                elif isinstance(group_col_type_dict.get(group_column), PythonElementWdg):
                    widget = group_col_type_dict[group_column]
                   
                    group_value = widget.get_result(sobject)
                    if not time_test: 
                        time_test = my._time_test(group_value)
                    else:
                        my.group_by_time[group_column] = True 

                    if my.group_interval and group_value:
                        group_value = my._get_simplified_time(group_value)
                    elif isinstance(group_value, basestring):
                        group_value = group_value.encode('utf-8')
                    else:
                        group_value = str(group_value)

                
                    if not group_value:
                        group_value = "__NONE__"
                   
                    my._set_eval_value(sobject, group_column, group_value, i)
                
                elif my.group_by_time.get(group_column):  # my.group_interval 
                    group_value = sobject.get_value(group_column, no_exception=True)
                    group_value = my._get_simplified_time(group_value)
                else:
                    group_value = sobject.get_value(group_column, no_exception=True)
                if not group_value:
                    group_value = "__NONE__"

                if i==0:
                    # this preps for ordering according to the first grouped column
                    # this is called recursively
                    sobject_list = my.group_dict.get(group_value)
                     
                    if sobject_list == None:
                        sobject_list = [sobject]
                        my.group_dict[group_value] = sobject_list
                    else:
                        sobject_list.append(sobject)




        # extend back into an ordered list
        sobject_sorted_list = []
        reverse=False
        # TODO: check this dict my.group_dict

        if True in my.group_by_time.values():
            reverse = True
        elif my.order_element and my.order_element.endswith(' desc'):
            reverse = True
       
        sobjects = Common.sort_dict(my.group_dict, reverse=reverse)
        for sobject in sobjects:
            sub_group_columns = group_columns[1:]
            ordered_sobject = my.order_sobjects(sobject, sub_group_columns)
            if ordered_sobject:
                sobject = ordered_sobject
            
            if isinstance(sobject, list):
                sobject = sobject
            else:
                sobject = [sobject]
            sobject_sorted_list.extend(sobject)

       
        if sobject_sorted_list:
            return sobject_sorted_list
        else:
            return sobjects
            



    def handle_table_behaviors(my, table):
        security = Environment.get_security()
        project_code = Project.get_project_code()
        my.handle_load_behaviors(table)

        # add the search_table_<table_id> listener used by widgets 
        # like Add Task to Selected
        if my.kwargs.get('temp') != True:
            table.add_behavior( {
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



        element_names = my.element_names
        column_widths = my.kwargs.get("column_widths")
        if not column_widths:
            column_widths = []

        

        if my.kwargs.get('temp') != True:
            table.add_behavior( {
                'type': 'load',
                'element_names': my.element_names,
                'column_widths': column_widths,
                'cbjs_action': '''
                var layout = bvr.src_el.getParent(".spt_layout");
                spt.table.set_layout(layout);

                // determine the widths of the screen
                var size = layout.getSize();
                var total_size = 30 + 32;
                for (var i = 0; i < bvr.column_widths.length; i++) {
                    total_size += bvr.column_widths[i];
                }

                for (var i = 0; i < bvr.element_names.length; i++) {
                    var name = bvr.element_names[i];
                    var width = bvr.column_widths[i];
                    spt.table.set_column_width(name, width);
                }

               
                '''
            } )

       


        """
        widths = my.kwargs.get("column_widths")
        #widths = []

        # if no widths are specified, then calculate the widths
        if not widths:
            table.add_behavior( {
            'type': 'load',
            'cbjs_action': '''
            setTimeout( function() {

            spt.table.set_table(bvr.src_el);
            var layout = bvr.src_el.getParent(".spt_layout");
            var layout_top = layout.getParent(".spt_layout_top");
            var width = layout_top.getSize().x;

            //layout_top.setStyle("border", "solid 1px red");

            var header_table = spt.table.get_header_table()

            // make sure the headers width are set

            var headers = spt.table.get_headers();
            var num_headers = headers.length;
            var mode = "scale";

            if (mode == "full") {
                header_table.setStyle("width", "100%")
                var width = 100 / num_headers;
                width = parseInt(width) + "%";
            }
            else {
                header_table.setStyle("width", "")
                bvr.src_el.setStyle("width", "")
                width = width / (num_headers) - 30;
            }

            if (width == 0) { return; }

            for (var i = 0; i < headers.length; i++) {
                headers[i].setStyle("width", width);
            }


            var no_items_el = layout.getElements(".spt_table_no_items");
            if (no_items_el) {
                header_table.setStyle("width", "100%")
                bvr.src_el.setStyle("width", "100%")
                return;
            }


            var row = spt.table.get_first_row();
            var cells = row.getElements(".spt_cell_edit");
            for (var i = 0; i < cells.length; i++) {
                cells[i].setStyle("width", width);
            }

            }, 100);

            '''
            } )
        """


        # all for collapsing of columns
        table.add_behavior( {
            #'type': 'double_click',
            'type': 'smart_click_up',
            'modkeys': 'SHIFT',
            'bvr_match_class': 'spt_table_header',
            'cbjs_action': '''
            spt.table.set_table(bvr.src_el);
            var element_name = bvr.src_el.getAttribute("spt_element_name");
            spt.table.toggle_collapse_column(element_name);
            '''
        } )



        # column resizing behavior
        my.header_table.add_smart_styles("spt_resize_handle", {
            "position": "absolute",
            "height": "100px",
            "margin-top": "-3px",
            "right": "-1px",
            "width": "5px",
            "cursor": "e-resize",
            "background-color": ''
        } )



        my.header_table.add_relay_behavior( {
            'type': 'mouseover',
            'drag_el': '@',
            'bvr_match_class': 'spt_resize_handle',
            "cbjs_action": '''
            bvr.src_el.setStyle("background", "#FF0");
            '''
        } )

        my.header_table.add_relay_behavior( {
            'type': 'mouseout',
            'drag_el': '@',
            'bvr_match_class': 'spt_resize_handle',
            "cbjs_action": '''
            bvr.src_el.setStyle("background", "");
            '''
        } )






        my.header_table.add_behavior( {
            'type': 'smart_drag',
            'drag_el': '@',
            'bvr_match_class': 'spt_resize_handle',
            'ignore_default_motion': 'true',
            "cbjs_setup": 'spt.table.drag_resize_header_setup(evt, bvr, mouse_411);',
            "cbjs_motion": 'spt.table.drag_resize_header_motion(evt, bvr, mouse_411)',
            "cbjs_action": 'spt.table.drag_resize_header_action(evt, bvr, mouse_411)',
        } )






        table.add_relay_behavior( {
            'type': 'mouseup',
            'bvr_match_class': 'spt_remove_hidden_row',
            'cbjs_action': '''
            spt.table.remove_hidden_row_from_inside(bvr.src_el);
            '''
        } )


        border_color = table.get_color('border', modifier=20)
        # Drag will allow the dragging of items from a table to anywhere else
        table.add_behavior( {
            'type': 'smart_drag', 'drag_el': 'drag_ghost_copy',
            'bvr_match_class': 'spt_table_select',
            'use_copy': 'true',
            'border_color': border_color,
            'use_delta': 'true', 'dx': 10, 'dy': 10,
            'drop_code': 'DROP_ROW',
            'copy_styles': 'background: #393950; color: #c2c2c2; border: solid 1px black; text-align: left; padding: 10px;',
            # don't use cbjs_pre_motion_setup as it assumes the drag el
            'cbjs_setup': '''
                if(spt.drop) {
                    spt.drop.sobject_drop_setup( evt, bvr );
                }
            ''',
            "cbjs_motion": '''
                spt.mouse._smart_default_drag_motion(evt, bvr, mouse_411);
                var target_el = spt.get_event_target(evt);
                target_el = spt.mouse.check_parent(target_el, bvr.drop_code);
                if (target_el) {
                    var orig_border_color = target_el.getStyle('border-color');
                    var orig_border_style = target_el.getStyle('border-style');
                    target_el.setStyle('border','dashed 2px ' + bvr.border_color);
                    if (!target_el.getAttribute('orig_border_color')) {
                        target_el.setAttribute('orig_border_color', orig_border_color);
                        target_el.setAttribute('orig_border_style', orig_border_style);
                    }
                }
            ''',
            "cbjs_action": '''
                if (spt.drop) {
                    spt.drop.sobject_drop_action(evt, bvr)
                }

                var dst_el = spt.get_event_target(evt);
                var src_el = spt.behavior.get_bvr_src(bvr);

                /* Keeping this around for later use */
                var dst_row = dst_el.getParent(".spt_table_row");
                var dst_search_key = dst_row.getAttribute("spt_search_key");

                var src_row = src_el.getParent(".spt_table_row");
                var src_search_key = src_row.getAttribute("spt_search_key");

            '''
        } )



        # selection behaviors
        table.add_behavior( {
        'type': 'smart_click_up',
        'bvr_match_class': 'spt_table_select',
        'cbjs_action': '''
            spt.table.set_table(bvr.src_el);
            var row = bvr.src_el.getParent(".spt_table_row");
            if (row.hasClass("spt_table_selected")) {
                spt.table.unselect_row(row);
            }
            else {
                spt.table.select_row(row);
            }
        '''
        } )


        table.add_behavior( {
        'type': 'smart_click_up',
        'bvr_match_class': 'spt_table_select',
        'modkeys': 'SHIFT',
        'cbjs_action': '''
        spt.table.set_table(bvr.src_el);
        var row = bvr.src_el.getParent(".spt_table_row");

        var rows = spt.table.get_all_rows();
        var last_selected = spt.table.last_selected_row;
        var last_index = -1;
        var cur_index = -1;
        for (var i = 0; i < rows.length; i++) {
            if (rows[i] == last_selected) {
                last_index = i;
            }
            if (rows[i] == row) {
                cur_index = i;
            }

            if (cur_index != -1 && last_index != -1) {
                break;
            }

        }
        var start_index;
        var end_index;
        if (last_index < cur_index) {
            start_index = last_index;
            end_index = cur_index;
        }
        else {
            start_index = cur_index;
            end_index = last_index;
        }

        for (var i = start_index; i < end_index+1; i++) {
            spt.table.select_row(rows[i]);
        }


        '''
        } )


        # indicator that a cell is editable

        # TEST: event delegation with MooTools
        table.add_behavior( {
            'type': 'load',
            'cbjs_action': '''
            bvr.src_el.addEvent('mouseover:relay(.spt_cell_edit)',
                function(event, src_el) {
                    if (src_el.hasClass("spt_cell_insert_no_edit")) {
                        src_el.setStyle("background-image", "url(/context/icons/custom/no_edit.png)" );
                    }
                    else if (!src_el.hasClass("spt_cell_no_edit")) {
                        src_el.setStyle("background-image", "url(/context/icons/silk/page_white_edit.png)" );
                        src_el.setStyle("background-repeat", "no-repeat" );
                        src_el.setStyle("background-position", "bottom right");
                    }

                } )

            bvr.src_el.addEvent('mouseout:relay(.spt_cell_edit)',
                function(event, src_el) {
                    src_el.setStyle("background-image", "" );
                } )
            '''
        } )

        # row highlighting

        if my.kwargs.get("show_row_highlight") not in [False, 'false']:
            table.add_behavior( {
            'type': 'load',
            'cbjs_action': '''
            bvr.src_el.addEvent('mouseover:relay(.spt_table_row)',
                function(event, src_el) {
                    // remember the original color
                    src_el.setAttribute("spt_hover_background", src_el.getStyle("background-color"));
                    spt.mouse.table_layout_hover_over({}, {src_el: src_el, add_color_modifier: -5});
                } )

            bvr.src_el.addEvent('mouseout:relay(.spt_table_row)',
                function(event, src_el) {
                    src_el.setAttribute("spt_hover_background", "");
                    spt.mouse.table_layout_hover_out({}, {src_el: src_el});
                } )
            '''
            } )


        # set styles at the table level to be relayed down
        border_color = table.get_color("table_border", default="border")


                
        select_styles = {
            "width": "30px",
            "min-width": "30px"
        }



        cell_styles = {
            "padding": "3px 8px",

            "vertical-align": "top",
            "background-repeat": "no-repeat",
            "background-position": "bottom right",
        }


        show_border = my.kwargs.get("show_border")
        if show_border not in [False, "false"]:
            cell_styles["border"] = "solid 1px %s" % border_color
            cell_styles["padding"] = "3px"
            select_styles["border"] = "solid 1px %s" % border_color




        table.add_smart_styles("spt_table_select", select_styles)
        table.add_smart_styles("spt_cell_edit", cell_styles)

        
        is_editable = my.kwargs.get("is_editable")

        # Edit behavior
        if is_editable in [False, 'false']:
            is_editable = False
        else:
            is_editable = True

        # Check user access
        access_keys = my._get_access_keys("edit",  project_code)
        if security.check_access("builtin", access_keys, "edit"):
            is_editable = True
        else: 
            is_editable = False
            my.view_editable = False
            

        if is_editable:
            table.add_behavior( {
                'type': 'smart_click_up',
                'bvr_match_class': 'spt_cell_edit',
                'cbjs_action': '''

                spt.table.set_table(bvr.src_el);
                var cell = bvr.src_el;
                // no action for the bottom row
                if (!cell.getParent('tr.spt_table_bottom_row'))
                    spt.table.show_edit(cell);
                return;
                '''
            } )


            table.add_smart_styles( "spt_table_header", {
                "background-repeat": "no-repeat",
                "background-position": "top center"
            } )





        # collapse groups
        from tactic.ui.widget.swap_display_wdg import SwapDisplayWdg
        SwapDisplayWdg.handle_top(table)

        table.add_relay_behavior( {
            'type': 'mouseup',
            'bvr_match_class': 'spt_group_row',
            'cbjs_action': '''
            spt.table.set_table(bvr.src_el);
            spt.table.collapse_group(bvr.src_el);


            '''
        } )


        # group mouse over color
        table.add_relay_behavior( {
            'type': "mouseover",
            'bvr_match_class': 'spt_group_row',
            'cbjs_action': "spt.mouse.table_layout_hover_over({}, {src_el: bvr.src_el, add_color_modifier: -5})"
        } )
        table.add_relay_behavior( {
            'type': "mouseout",
            'bvr_match_class': 'spt_group_row',
            'cbjs_action': "spt.mouse.table_layout_hover_out({}, {src_el: bvr.src_el})"
        } )




        border_color = table.get_color("table_border", -10, default="border")
        table.add_smart_styles("spt_group_row", {
            'border': 'solid 1px %s' % border_color
        } )



        # show hidden row test
        """
        table.add_behavior( {
            'type': 'smart_click_up',
            'bvr_match_class': 'spt_cell_edit',
            'cbjs_action': '''
            var row = bvr.src_el.getParent(".spt_table_row");
            var class_name = 'tactic.ui.widget.CalendarWdg';
            spt.table.add_hidden_row(row, class_name);
            '''
        } )
        """





    def get_insert_wdg(my):
        '''Fake a table for inserting'''
        #my.group_columns = []
        my.edit_wdgs = {}
        table = Table()
        table.add_style("display: none")

        insert_sobject = SearchType.create(my.search_type)

        # set the sobjects to all the widgets then preprocess
        for widget in my.widgets:
            widget.set_sobjects([insert_sobject])
            #widget.set_layout_wdg(table)
            widget.set_parent_wdg(my)
            # preprocess the elements if not in widget mode
            # it has been done otherwise
            if my.mode != 'widget':
                widget.preprocess()


        row = my.handle_row(table, insert_sobject, row=0)
        row.add_class("spt_table_insert_row spt_clone")
        # to make focusable
        row.add_attr('tabIndex','-1')

        row.remove_class("spt_table_row")

        return table





 

    def handle_headers(my, table, hidden=False):
        # Add the headers
        tr = table.add_row()
        tr.add_class("spt_table_header_row")
        #tr.add_style("display: none")
        tr.add_class("SPT_DTS")

        if hidden:
            tr.add_style("display: none")

        
        autofit = my.view_attributes.get("autofit") != 'false'

        show_header = my.kwargs.get("show_header")
        if show_header not in ['false', False]:
            show_header = True
        else:
            show_header = False


        if not show_header:
            tr.add_style("display: none")



        if my.kwargs.get("__hidden__") == True:
            tr.add_color("background", "background", -8)
            border_color = table.get_color("table_border", default="border")
        else:
            tr.add_color("background", "background", -5)
            border_color = table.get_color("table_border", 0, default="border")
       
        #SmartMenu.assign_as_local_activator( tr, 'DG_HEADER_CTX' )


        if my.kwargs.get("show_select") not in [False, 'false']:
            my.handle_select_header(table, border_color)

        # this comes from refresh
        widths = my.kwargs.get("column_widths")

        # boolean to determine if there is any width set for any columns
        width_set = False


        for i, widget in enumerate(my.widgets):
            name = widget.get_name()

            th = table.add_header()

            if widths:
                th.add_style("width", widths[i])
            th.add_style("padding: 3px")

            # this is meant for views that haven't been saved to default
            # to fit the whole screen
            th.add_style("text-align: left")
            # The smart menu has to be put on the header and not the
            # row to get row specific info.
            SmartMenu.assign_as_local_activator( th, 'DG_HEADER_CTX' )

            th.add_class("spt_table_header")
            th.add_class("spt_table_header_%s" %my.table_id)
            th.add_attr("spt_element_name", name)


            show_border = my.kwargs.get("show_border")
            if show_border not in [False, "false"]:
                th.add_style("border: solid 1px %s" % border_color)

            edit_wdg = my.edit_wdgs.get(name)
            if edit_wdg:
                th.add_attr("spt_input_type", edit_wdg.get_element_type())

            inner_div = DivWdg()
            th.add(inner_div)
            inner_div.add_style("position: relative")
            inner_div.add_style("width: auto")
            inner_div.add_class("spt_table_header_inner")
            inner_div.add_style("overflow: hidden")

            inner_div.add_style("min-width: 20px")
            inner_div.add_style("margin-top: 4px")
            inner_div.add_style("margin-bottom: 4px")

            inner_div.add_style("min-height: 30px")



            # handle the sort arrow
            sortable = my.attributes[i].get("sortable") != "false"
            if sortable:

                if my.order_element == name or my.order_element == "%s asc" % name:
                    th.add_styles("background-image: url(/context/icons/common/order_array_down_1.png);")
                elif my.order_element == "%s desc" % name:
                    th.add_styles("background-image: url(/context/icons/common/order_array_up_1.png);")

            # Qt webkit ignores these
            # This is fixed in PySide 1.1.2.  Need to update OSX version
            # before commenting this all out
            th.add_style("background-repeat: no-repeat")
            th.add_style("background-position: bottom center")
            th.add_style("vertical-align: top")



            # handle resizeble element
            resize_div = DivWdg()
            inner_div.add(resize_div)
            resize_div.add("&nbsp;")
            resize_div.add_class("spt_resize_handle")



            header_div = DivWdg()
            inner_div.add(header_div)
            header_div.add_style("padding: 1px 3px 1px 3px")
            header_div.add_class("spt_table_header_content")


            if my.kwargs.get("wrap_headers") not in ["true", True]:
                header_div.add_style("width: 10000%")
                #header_div.add_style("whitespace: nowrap")



            # put reorder directly here
            behavior = {
                "type": 'drag',
                #"drag_el": 'drag_ghost_copy',
                "drag_el": '@',
                "drop_code": 'DgTableColumnReorder',   # can only specify single drop code for each drag behavior
                "cb_set_prefix": "spt.table.drag_reorder_header",
            }

            header_div.add_behavior(behavior)
            table.set_attr('SPT_ACCEPT_DROP', 'DgTableColumnReorder')



            # embed info in the TH for whether or not the column
            # is groupable
            if widget.is_groupable():
                th.set_attr("spt_widget_is_groupable","true")


            # determine whether a widget has related items
            try:
                if edit_wdg and edit_wdg.get_related_type():
                    th.set_attr("spt_widget_has_related","true")
                    th.set_attr("spt_related_type",edit_wdg.get_related_type())
            except:
                pass

            # embed info in the TH for whether or not the column is
            # sortable
            if widget.is_sortable():
                th.set_attr("spt_widget_is_sortable","true")

            if widget.get_sort_prefix():
                th.set_attr("spt_widget_sort_prefix", widget.get_sort_prefix())


            # embed info in the TH for whether or not the column is
            # locally searchable
            if widget.is_searchable():
                th.set_attr("spt_widget_is_searchable","true")
                th.set_attr("spt_searchable_search_type", widget.get_searchable_search_type())


            # embed if this is a time related column
            element_type = SearchType.get_tactic_type(my.search_type, name)
            if element_type in ['time', 'date', 'datetime'] or widget.is_time_groupable(): 
                th.set_attr("spt_widget_is_time_groupable","true")

            if my.mode == 'widget':
                value = widget.get_title()
            else:
                element = widget.get_name()
                value = Common.get_display_title(element)

            header_div.add(value)
            if isinstance(value, basestring):
                header_div.add_style("margin-top: 6px")


            # provide an opportunity for the widget to affect its header
            widget.handle_th(th, i)

        # this is for table where the view hasn't been saved yet (auto generated or built-in)
        #if not width_set:
        #    table.add_style('width', '100%')

        has_extra_header = my.kwargs.get("has_extra_header")
        if has_extra_header in [True, "true"]:
            th = table.add_header()
            th.add_style("width: 36px")
            th.add_style("min-width: 36px")
            th.add_style("max-width: 36px")
            th.add("&nbsp;")
            th.add_style("border-style: solid")
            th.add_style("border-width: 1px")
            color = th.get_color("table_border", -10, default="border")
            th.add_style("border-color: %s" % color)




    def has_group_bottom(my):
        '''return True if group_column has group_bottom'''
        if not my.group_columns:
            return False
        
        for widget in my.widgets:
            if widget.get_name() == my.group_columns[0]:
                expression = widget.get_option("group_bottom")
                if expression:
                    return True
            
        return False


    def has_bottom_wdg(my):
        '''return True if a widget has bottom widget defined'''
        for widget in my.widgets:

            if widget.get_bottom_wdg():
                return True

        return False

    def postprocess_groups(my):

        # The problem is that often a group bottom cannot be calculated
        # until all the widgets have been drawn.

        has_widgets = None
        group_rows_summary_dict = {}
        widget_summary_dict = {}
        last_group_level = -1
        # reversed for ease of tallying 
        my.group_rows.reverse()
       
        group_level = 0
        for idx, group_row in enumerate(my.group_rows):
            sobjects = group_row.get_sobjects()
            
            if hasattr(group_row, 'group_level'):
                group_level = group_row.group_level

                if group_level != last_group_level:
                    # retrieve the last level
                    widget_summary_dict = group_rows_summary_dict.get(last_group_level)

                        
                if last_group_level < 0:
                    last_group_level = group_level
        
            group_row.add_attr("spt_table_state", "open")

            for td in group_row.get_widgets():
                #td.add_style("overflow: hidden")
                td.add_attr("colspan", "2")


            group_widgets = []
            has_widgets = False
       
            if not widget_summary_dict:
                # assignmenet
                widget_summary_dict = {}
            group_rows_summary_dict[group_level] = widget_summary_dict

            for widget in my.widgets:
                
                # ideally, it's more efficient for the widget to return a tuple. Some old ones may not
                tmp = widget.get_group_bottom_wdg(sobjects)
                option = my.widget_summary_option.get(widget)
                
                if tmp and isinstance(tmp, tuple):
                    group_widget = tmp[0]
                    result = tmp[1]
                else:
                    group_widget = tmp
                    result = 0
                
                if option != 'average':
                    summary = widget_summary_dict.get(widget) 
                    if not summary: 
                        summary = (0,0)

                    group_summary, total = summary
                    
                    if isinstance(result, basestring) and result.startswith('$'):
                        result = result[1:]
                        result = float(result)
               
                    group_summary += result
                    total += result
                    widget_summary_dict[widget] = (group_summary, total)
                
                group_widgets.append(group_widget)

                if group_widget:
                    has_widgets = True

           
            # original group widgets derived from sobjects
            if has_widgets:
                for wdg_idx, group_widget in enumerate(group_widgets):
                    td = HtmlElement.td()
                    td.add_class('spt_group_cell')
                    td.add_style("padding: 8px 3px")
                    td.add_style("overflow-x: hidden")

                    if group_widget:
                        td.add_border(color="#BBB")
                    else:
                        td.add_border(color="#BBB", size="1px 0px")

                    #group_row.add(td)
                    
                    td.add_style("padding: 3px")
                    group_row.add(td, name='td_%s'%wdg_idx)
                    td.add(group_widget)

            
            # update the group rows above the leaf group_row
            if group_level < len(my.group_columns) - 1:
                for wdg_idx, wdg in enumerate(my.widgets):
                   
                    summary = widget_summary_dict.get(wdg)
                    if summary:
                        group_summary, total = summary
                    
                    if group_level == 0:
                        div = DivWdg(total)
                    else:
                        div = DivWdg(group_summary)
                    div.add_style('text-align: right')
                    td = HtmlElement.td()
                    td.add(div)
                    td.add_class('spt_group_cell')
                    td.add_style("padding: 3px")
                    # replace the top group row summary
                    group_row.add(td, 'td_%s'%wdg_idx)

            # reset when reaching the top level
            if group_level == 0:
                widget_summary_dict = {}
                group_rows_summary_dict[group_level] = widget_summary_dict

            elif group_level < last_group_level:
                for k, v in widget_summary_dict.items():
                    group_sum, total = v
                    widget_summary_dict[k] = (0, total)
            
            last_group_level = group_level

          

    def add_table_bottom(my, table):
        '''override the same method in BaseTableLayoutWdg to add a bottom row. this does not 
           call handle_row() as it is simpler'''
        # add in a bottom row
        all_null = True
        bottom_wdgs = []
        for widget in my.widgets:
            bottom_wdg = widget.get_bottom_wdg()
            bottom_wdgs.append(bottom_wdg)
            if bottom_wdg:
                all_null = False



        if not all_null:
         
            tr = table.add_row()
            # don't use spt_table_row which is meant for regular row
            tr.add_class('spt_table_bottom_row')
            tr.add_color("background", "background", -3)
            if my.group_columns:
                last_group_column = my.group_columns[-1]
                tr.add_class("spt_group_%s" % my.group_ids.get(last_group_column))
                td = table.add_cell()

            #td = table.add_cell("&nbsp;")

            if my.kwargs.get("show_select") not in [False, 'false']:
                td = table.add_cell()
            # add in a selection td
            #if my.kwargs.get("show_select") not in [False, 'false']:
            #    my.handle_select(table, None)

            for i, bottom_wdg in enumerate(bottom_wdgs):
                element_name = my.widgets[i].get_name()
                td = table.add_cell()
                # spt_cell_edit for drag and drop, but it's really not meant for edit
                td.add_class("spt_cell_edit spt_cell_no_edit")
                td.add_attr("spt_element_name", element_name)
                div = DivWdg()
                div.add_style("min-height: 20px")
                td.add(div)
                if bottom_wdg:
                    div.add(bottom_wdg)
                #else:
                #    div.add("")

                div.add_style("margin-right: 7px")

               

 

    def handle_groups(my, table, row, sobject):
        '''called per sobject, decide to draw a grouping folder if conditions are met''' 
        if row == 0:
            my.group_summary = []

            spacing = len(my.group_columns) * 20

            tr = table.add_row()
            tr.add_class("spt_table_hidden_group_row")
            if spacing:
                td = table.add_cell()
                td.add_style("width", "%spx" %spacing)
                td.add_style("width: %spx" % spacing)
                td.add_style("max-width: %spx" % spacing)
            if my.kwargs.get("show_select") not in [False, 'false']:
                td = table.add_cell()
                td.add_style("width", "30px")
                td.add_style("min-width", "30px")
                td.add_style("max-width", "30px")
            for widget in my.widgets:
                td = table.add_cell()
                td.add_class("spt_table_hidden_group_td")
                td.add_attr("spt_element_name", widget.get_name())


        
        last_group_column = None
        
        for i, group_column in enumerate(my.group_columns):
            group_values = my.group_values[i]
            
            eval_group_column =  my._grouping_data.get(group_column)
            if eval_group_column:
                group_column = eval_group_column
            
            group_value = sobject.get_value(group_column, no_exception=True)
            if my.group_by_time.get(group_column): #my.group_interval:
                #group_value = sobject.get_value(group_column, no_exception=True)
                group_value = my._get_simplified_time(group_value)
            if not group_value:
                group_value = "__NONE__"
            
            last_value = group_values.get(group_column)
           
            # if this is the first row or the group value has changed,
            # then create a new group
            if last_value == None or group_value != last_value:

                if last_value != None:
                    # group summary
                    if my.group_mode in ["bottom", "both"]:
                        tr, td = table.add_row_cell()
                        tr.set_sobjects(my.group_summary)
                        tr.add_style("background", "#EEF")
                        tr.add_class("spt_table_group_row")

                        my.group_summary = []
                        my.group_rows.append(tr)

                        tr, td = table.add_row_cell()
                        td.add("&nbsp;")
                        tr.add_border(size=1)

                if my.group_mode in ["top", "both"]:
                    my.handle_group(table, i, sobject, group_column, group_value, last_value)
          

                group_values[group_column] = group_value
            
                last_group_column = group_column
                # clear the next dict to facilate proper grouping in the next major group
                next_dict = my.group_values.get(i+1)
                if next_dict:
                    next_dict = {}
                    my.group_values[i+1] = next_dict

            my.group_summary.append(sobject)


        # put the sobjects in each sub group for group summary calculation
        if my.group_rows:
            my.group_rows[-1].get_sobjects().append(sobject)

        

    def handle_group(my, table, i, sobject, group_column, group_value, last_value):
        '''Draw a toggle and folder for this group'''
        # we have a new group
        tr, td = table.add_row_cell()
        tr.add_class('unselectable')
        if i != 0 and not my.is_on:
            tr.add_style("display: none")

        tr.add_class("spt_table_group_row")

        unique_id = tr.set_unique_id()

        if my.group_mode in ["top"]:
            my.group_rows.append(tr)


        if group_value != last_value:
            tr.group_level = i
           
        
        if group_value == '__NONE__':
            label = '---'
        else:
            group_label_expr = my.kwargs.get("group_label_expr")
            if group_label_expr:
                label = Search.eval(group_label_expr, sobject, single=True)
            else:
                label = Common.process_unicode_string(group_value)

        title = label
        if my.group_by_time.get(group_column):
            if my.group_interval == BaseTableLayoutWdg.GROUP_WEEKLY:
                title = 'Week  %s' %label
            elif my.group_interval == BaseTableLayoutWdg.GROUP_MONTHLY:
                # order by number, but convert to alpha title
                labels = label.split(' ')
                if len(labels)== 2:
                    timestamp = datetime(int(labels[0]),int(labels[1]),1)
                    title = timestamp.strftime("%Y %b")

        from tactic.ui.widget.swap_display_wdg import SwapDisplayWdg
        swap = SwapDisplayWdg(title=title, icon='FOLDER_GRAY',is_on=my.is_on)
        swap.set_behavior_top(my.table)
        td.add(swap)
        swap.add_style("width: 800px")
        swap.add_style("font-weight: bold")

        td.add_style("height: 25px")
        td.add_style("padding-left: %spx" % (i*15))


        tr.add_border(size="1px 0px 0px 0px")
        tr.add_style("background", "#EEF")
        
        tr.add_attr("spt_unique_id", unique_id)
        tr.add_class("spt_group_row")

        # for group collapse js function
        tr.add_attr('idx', i)

        tr.add_attr("spt_group_name", group_value)


        if i != 0:
            last_group_column = my.group_columns[-1]
            tr.add_class("spt_group_%s" % my.group_ids.get(last_group_column))

        my.group_ids[group_column] = unique_id

        tr.add_color("background", "background3", 5)
        tr.add_color("color", "color3")
        



    def handle_no_results(my, table):


        no_results_mode = my.kwargs.get('no_results_mode')
        custom_drag_bvr = my.kwargs.get('custom_drag_bvr')

        # custom_drag_bvr will be set to true in other widgets if they have 
        # a drag and drop behavior defined. It is initialised to False so
        # that the default behavior will still be there to avoid having to
        # refactor every instance handle_no_results is used

        if no_results_mode == 'compact':

            tr, td = table.add_row_cell()
            tr.add_class("spt_table_no_items")
            msg = DivWdg("<i style='font-weight: bold; font-size: 14px'>- No items found -</i>")
            msg.add_style("text-align: center")
            msg.add_style("padding: 5px")
            msg.add_style("opacity: 0.5")
            td.add(msg)
            return

        table.add_style("width: 100%")


        tr, td = table.add_row_cell()

        if not custom_drag_bvr:
            tr.add_attr("ondragover", "spt.table.dragover_row(event, this); return false;")
            tr.add_attr("ondragleave", "spt.table.dragleave_row(event, this); return false;")
            tr.add_attr("ondrop", "spt.table.drop_row(event, this); return false;")



        tr.add_class("spt_table_no_items")
        td.add_style("border-style: solid")
        td.add_style("border-width: 1px")
        td.add_color("border-color", "table_border", default="border")
        #td.add_border()
        td.add_color("color", "color")
        td.add_color("background", "background", -7)
        td.add_style("min-height: 250px")
        td.add_style("overflow: hidden")

        for i in range(0, 10):
            div = DivWdg()
            td.add(div)
            div.add_style("height: 30px")
            if i % 2:
                div.add_color("background", "background")
            else:
                div.add_color("background", "background", -3)


        msg_div = DivWdg()
        td.add(msg_div)
        msg_div.add_style("text-align: center")
        msg_div.add_style("float: center")
        msg_div.add_style("margin-left: auto")
        msg_div.add_style("margin-right: auto")
        msg_div.add_style("margin-top: -260px")


        if not my.is_refresh and my.kwargs.get("do_initial_search") in ['false', False]:
            msg = DivWdg("<i>-- Initial search set to no results --</i>")
        else:

            no_results_msg = my.kwargs.get("no_results_msg")

            msg = DivWdg("<i style='font-weight: bold; font-size: 14px'>- No items found -</i>")
            #msg.set_box_shadow("0px 0px 5px")
            if no_results_msg:
                msg.add("<br/>"*2)
                msg.add(no_results_msg)

            elif my.get_show_insert():
                msg.add("<br/><br/>Click on the &nbsp;")
                icon = IconWdg("Add", "BS_PLUS")
                msg.add(icon)
                msg.add(" button to add new items")
                msg.add("<br/>")
                msg.add("or ")
                msg.add("alter search criteria for new search.")
            else:
                msg.add("<br/>"*2)
                msg.add("Alter search criteria for new search.")

        msg_div.add(msg)

        msg.add_style("padding-top: 20px")
        msg.add_style("height: 100px")
        msg.add_style("width: 400px")
        msg.add_style("margin-left: auto")
        msg.add_style("margin-right: auto")
        msg.add_color("background", "background3")
        msg.add_color("color", "color3")
        msg.add_border()

        msg_div.add("<br clear='all'/>")
        td.add("<br clear='all'/>")



    def handle_row(my, table, sobject, row, level=0):
        # add the new row
        tr = table.add_row()
        if not my.is_on:
            tr.add_style("display: none")

        # remember the original background colors
        bgcolor1 = table.get_color("background")
        bgcolor2 = table.get_color("background", -1)
        table.add_attr("spt_bgcolor1", bgcolor1)
        table.add_attr("spt_bgcolor2", bgcolor2)




        # FIXME: this should be done before preprocess (and made efficient)
        #if sobject.get_base_search_type() == 'sthpw/sobject_list':
        #    search_type = sobject.get_value("search_type")
        #    search_id = sobject.get_value("search_id")
        #    parent = Search.get_by_id(search_type, search_id)
        #    if parent:
        #        sobject = parent
        #        my.sobjects[row] = sobject


        tr.add_class("spt_table_row")
        # to tag it with the current table to avoid selecting nested table contents when they are present
        tr.add_class("spt_table_row_%s" %my.table_id)
        if my.parent_key:
            tr.add_attr("spt_parent_key", my.parent_key )

        if my.connect_key:
            tr.add_attr("spt_connect_key", my.connect_key )


        # add extra data if it exists
        extra_data = sobject.get_value("_extra_data", no_exception=True)
        if extra_data is not None and extra_data:
            tr.add_behavior( {
                'type': 'load',
                'data': extra_data,
                'cbjs_action': '''
                bvr.src_el.extra_data = bvr.data;
                '''
            } )
        tr.add_attr("spt_search_key", sobject.get_search_key(use_id=True) )
        tr.add_attr("spt_search_key_v2", sobject.get_search_key() )
        #tr.add_attr("spt_search_type", sobject.get_base_search_type() )

        display_value = sobject.get_display_value(long=True)
        tr.add_attr("spt_display_value", display_value)

        if my.subscribed_search_keys.get(sobject.get_search_key()):
            tr.set_attr("spt_is_subscribed","true")

        if sobject.is_retired():
            background = tr.add_color("background-color", "background", [20, -10, -10])
            tr.set_attr("spt_widget_is_retired","true")

        elif sobject.is_insert():
            background = tr.add_color("background-color", "background", [10, -10, -10])
        elif row % 2:
            background = tr.add_style("background-color", bgcolor1)
        else:
            background = tr.add_style("background-color", bgcolor2)




        SmartMenu.assign_as_local_activator( tr, 'DG_DROW_SMENU_CTX' )
        #SmartMenu.assign_as_local_activator( tr, 'DG_HEADER_CTX' )


        my.is_insert = sobject.is_insert()



        # handle the grouping
        #for group_column in my.group_columns:
        #    tr.add_class("spt_group_%s" % my.group_ids.get(group_column))
        if my.group_columns:
            last_group_column = my.group_columns[-1]
            tr.add_class("spt_group_%s" % my.group_ids.get(last_group_column))


        # add in a selection td
        if my.kwargs.get("show_select") not in [False, 'false']:
            my.handle_select(table, sobject)

        for i, widget in enumerate(my.widgets):
            element_name = widget.get_name()

            td = table.add_cell()
            td.add_class("spt_cell_edit")

            td.add_style("overflow: hidden")


            widths = my.kwargs.get("column_widths")
            if widths:
                td.add_style("width", widths[i])



            # Qt webkit ignores these
            if my.browser == 'Qt':
                td.add_style("background-repeat: no-repeat")
                td.add_style("background-position: bottom right")
                td.add_style("vertical-align: top")

            # add spacing
            if level and element_name == my.level_name:
                td.add_style("padding-left: %spx" % (level*my.level_spacing))

            if my.mode == 'widget':
                widget.set_current_index(row)

                try:
                    if element_name in my.error_columns:
                        td.add(IconWdg("Error Found: see above", IconWdg.WARNING, True) )
                    else:
                        html = widget.get_buffer_display()
                        if not html:
                            html = "<div style='height: 14px'>&nbsp;</div>"
                        td.add(html)
                except Exception, e:

                    my.error_columns.add(element_name)

                    from pyasm.widget import ExceptionWdg
                    error_wdg = ExceptionWdg(e)
                    td.add(error_wdg)
                  
                    # reset the top_layout
                    from pyasm.web import WidgetSettings
                    WidgetSettings.set_value_by_key('top_layout','')
 

            else:
                value = sobject.get_value(element_name, no_exception=True)
                td.add(value)


            my.name = widget.get_name()
            my.value = sobject.get_value(element_name, no_exception=True)

            if not my.is_insert and my.mode == 'widget':
                my.handle_color(td, widget, i)

                # provide an opportunity for the widget to affect the td and tr
                widget.handle_tr(tr)
                widget.handle_td(td)


            is_editable = True
            # Check if view is editable first, if not, skip checking each column
            if my.view_editable:
                if not widget.is_editable():
                    is_editable = False
                else:
                    security = Environment.get_security()
                    if not security.check_access('element', {'name': element_name}, "edit", default='edit'):
                        is_editable = False


            # This is only neccesary if the table is editable
            if my.view_editable:

                edit = my.edit_wdgs.get(element_name)

                # insert rows have no edits defined yet
                if my.is_insert:
                    if not is_editable:
                        td.add_class("spt_cell_insert_no_edit")

                elif not edit or not is_editable:
                    td.add_class("spt_cell_no_edit")


                #get the value from the widget, else use my.value
                if edit:
                    edit.set_sobject(sobject)
                    values = edit.get_values()
                    column = edit.get_column()
                    value = values.get('main')
                    if not value and value != False:
                        value = ''
                else:
                    value = my.value

                # add timezone conversion
                if not SObject.is_day_column(element_name):
                    element_type = SearchType.get_tactic_type(my.search_type, element_name)
                    
                    if element_type in ['time', 'datetime']:
                        value = widget.get_timezone_value(value)
                     

                if isinstance(value, basestring):
                    value = value.replace('"', '&quot;')


                if isinstance(value, bool):
                    value = str(value).lower()
            


                td.add_attr("spt_input_value", value)
                #td.add_attr("spt_input_column", column)
            else:
                td.add_class("spt_cell_no_edit")



            # if this is an insert, then set the element name
            if my.is_insert:
                td.add_attr("spt_element_name", element_name)

        #tr.add_attr("ondragenter", "return false")
        tr.add_attr("ondragover", "spt.table.dragover_row(event, this); return false;")
        tr.add_attr("ondragleave", "spt.table.dragleave_row(event, this); return false;")
        tr.add_attr("ondrop", "spt.table.drop_row(event, this); return false;")


        return tr





    def get_color_maps(my):

        # get the color maps
        from pyasm.widget import WidgetConfigView
        color_config = WidgetConfigView.get_by_search_type(my.search_type, "color")
        color_xml = color_config.configs[0].xml
        my.color_maps = {}
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

            my.color_maps[name] = bg_color_map, text_color_map
        return my.color_maps


    def handle_color(my, td, widget, index):

        # add a color based on the color map if color is not set to false
        disable_color = my.attributes[index].get("color") == 'false'
        if disable_color:
            return

        bg_color = None
        text_color = None

        if my.name is None:
            name = widget.get_name()
        else:
            name = my.name

        try:
            if my.value is None:
                value = widget.get_value()
            else:
                value = my.value

            if not isinstance(value, basestring):
                value = str(value)
            bg_color_map, text_color_map = my.color_maps.get(name)
            if bg_color_map:
                bg_color = bg_color_map.get(value)
                if bg_color:
                    td.add_style("background-color", bg_color)
            if text_color_map:
                text_color = text_color_map.get(value)
                if text_color:
                    td.add_style("color", text_color)
        except Exception, e:
            print 'WARNING: problem when getting widget value for color mapping on widget [%s]: ' % widget, "message=[%s]" % e.message.encode('utf-8')


    def handle_select_header(my, table, border_color=None):

        if my.group_columns:
            spacing = len(my.group_columns) * 20
            th = table.add_cell()
            th.add_style("min-width: %spx" % spacing)
            th.add_style("width: %spx" % spacing)
            th.add_style("max-width: %spx" % spacing)

        th = table.add_cell()
        #th.add_gradient("background", "background", -10)
        if not border_color:
            border_color = table.get_color("table_border", 0, default="border")



        show_border = my.kwargs.get("show_border")
        if show_border not in [False, "false"]:
            th.add_style("border", "solid 1px %s" % border_color)

        th.add_looks( 'dg_row_select_box' )
        th.add_class( 'spt_table_header_select' )
        th.add_style('width: 30px')
        th.add_style('min-width: 30px')
        th.add_style('max-width: 30px')

        th.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        spt.table.set_table(bvr.src_el);
        var cell = bvr.src_el;

        if (cell.hasClass("look_dg_row_select_box") ) {
            cell.addClass("look_dg_row_select_box_selected");
            cell.removeClass("look_dg_row_select_box");
            spt.table.select_all_rows();
        }
        else {
            cell.removeClass("look_dg_row_select_box_selected");
            cell.addClass("look_dg_row_select_box");
            spt.table.unselect_all_rows();
        }

        '''
        } )




    def handle_select(my, table, sobject):
        # FIXME: this confilicts with another "is_grouped"
        #my.is_grouped = my.kwargs.get("is_grouped")
        #if my.is_grouped or my.group_columns:

        
        if my.group_columns or True:
            spacing = len(my.group_columns) * 20
            if spacing:
                td = table.add_cell("&nbsp;")
                td.add_style("min-width: %spx" % spacing)
                td.add_style("width: %spx" % spacing)
                td.add_style("max-width: %spx" % spacing)



        td = table.add_cell()
        td.add_class("spt_table_select")
        td.add_looks( 'dg_row_select_box' )
        td.add_class( 'SPT_DTS' )
        #td.add_color("background-color", "background", -0)
        td.add_color("opacity", "0.5")
        if my.subscribed_search_keys.get(sobject.get_search_key()):
            td.add_border(direction="right", color="#ecbf7f", size="2px")

        if sobject and sobject.is_insert():
            icon_div = DivWdg()
            icon = IconWdg("New", IconWdg.NEW)
            icon_div.add(icon)
            #td.add_style("padding: 1 0 0 10")
            icon_div.add_style("float: left")
            icon_div.add_style("margin-left: 7px")
            td.add(icon_div)

        return 




    def get_edit_wdgs(my):
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

                # finally check security after checking config attrs
                if my.edit_permission_columns.get(name) == False:
                    editable = False

                if editable == True:
                    from layout_wdg import CellEditWdg
                    edit = CellEditWdg(x=j, element_name=name, search_type=my.search_type, state=my.state, layout_version=my.get_layout_version())
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
                        my.validations_div.add( v_div )


        return edit_wdgs


    def get_onload_js(my):
        return r'''
        spt.dom.load_js( ["dg_table.js"], function() {
            spt.dom.load_js( ["dg_table_action.js"], function() {
                spt.dom.load_js( ["dg_table_editors.js"], function() {} )
            } );
        } );
        '''




    def handle_load_behaviors(my, table):

        if my.kwargs.get('temp') != True:
            cbjs_action = '''
            // set the current table layout on load
            if (spt.table) {
                spt.table.set_table(bvr.src_el);
                var top = bvr.src_el.getParent(".spt_layout");
                spt.table.set_layout(top);
            }
            '''
            table.add_behavior({
                'type': 'load',
                'cbjs_action': cbjs_action
                })



        if my.kwargs.get("load_init_js") in [False, 'false']:
            return

        if Container.get_dict("JSLibraries", "spt_table"):
            return


        select_color = table.get_color("background3")
        shadow_color = table.get_color("shadow")

      
        cbjs_action =  '''

spt.table.get_total_count = function() {
     var inner = spt.table.get_layout();
     return inner.getAttribute('total_count');
}

spt.table.get_table = function() {
    return spt.table.last_table;
}

spt.table.get_header_table = function() {
    var layout = spt.table.layout;
    var table = layout.getElement(".spt_table_with_headers");
    if (!table) {
        table = spt.table.get_table();
    }
    return table;
}


spt.table.get_table_id = function() {
    return spt.table.get_table().getAttribute('id');
}

spt.table.set_table = function(table) {

    if (!table) {
        log.critical('Cannot run spt.table.set_table() with an undefined table');
     	return;
    }

    var layout = table.getParent(".spt_layout");
    spt.table.set_layout(layout);
   
}


spt.table.set_layout = function(layout) {
    spt.table.layout = layout;
    var table = layout.getElement(".spt_table_table");
    spt.table.last_table = table;
    spt.table.element_names = null;
}

spt.table.get_layout = function() {
    return spt.table.layout;
}




// Search methods
spt.table.run_search = function(kwargs) {
    if (!kwargs) {
        kwargs = {};
    }
    var table = spt.table.get_table();
    var bvr = {
        src_el: table,
        extra_args: kwargs
    }
    spt.dg_table.search_cbk( {}, bvr );
}

// Search methods
spt.table.do_search = function(kwargs) {
    return spt.table.run_search(kwargs);
}


// Preview methods


spt.table.dragover_row = function(evt, el) {
    var top = $(el);
    top.setStyle("border", "dashed 1px blue");
    top.setStyle("background", "rgba(0,0,255,0.05)");
    top.setStyle("opacity", "0.3")
}


spt.table.dragleave_row = function(evt, el) {
    var top = $(el);
    top.setStyle("border", "solid 1px #BBB");
    top.setStyle("background", "");
    top.setStyle("opacity", "1.0")
}


// drop_row does NOT drop a row from the table
// It was misnamed it refers to the action of DROPPING A ROW INTO the table
spt.table.drop_row = function(evt, el) {
    evt.stopPropagation();
    evt.preventDefault();

    evt.dataTransfer.dropEffect = 'copy';
    var files = evt.dataTransfer.files;

    var top = $(el);
    var thumb_el = top.getElement(".spt_thumb_top");
    if (thumb_el) {
        var size = thumb_el.getSize();
    }

    for (var i = 0; i < files.length; i++) {
        var size = files[i].size;
        var file = files[i];

        var filename = file.name;

        var search_key = top.getAttribute("spt_search_key");
        if (!search_key) {
            var layout = spt.table.get_layout();
            var search_type = layout.getAttribute("spt_search_type");
            var server = TacticServerStub.get();
            var sobject = server.insert(search_type, {name: filename})
            search_key = sobject.__search_key__;
        }
        var context = "publish" + "/" + filename;

        var upload_file_kwargs =  {
            files: files,
            upload_complete: function() {
                var server = TacticServerStub.get();
                var kwargs = {mode: 'uploaded'};
                spt.table.dragleave_row(evt, el);
                try {
                    server.simple_checkin( search_key, context, filename, kwargs);
                }
                catch(e) {
                    spt.alert("An error occured in the check-in: ["+e+"]");
                    return;
                }
            }
        };
        spt.html5upload.upload_file(upload_file_kwargs);


        // inline replace the image
        if (thumb_el) {
            setTimeout( function() {
                var loadingImage = loadImage(
                    file,
                    function (img) {
                        img = $(img);
                        img.setStyle("width", "100%");
                        img.setStyle("height", "");
                        thumb_el.innerHTML = "";
                        thumb_el.appendChild(img);
                        img.setSize(size);
                    },
                    {maxWidth: 240, canvas: true, contains: true}
                );
            }, 0 );
        }



    }
}


// Discovery methods


spt.table.get_element_names = function() {
    if (spt.table.element_names != null) {
        return spt.table.element_names;
    }
    var headers = spt.table.get_headers();
    var element_names = [];
    for (var i = 0; i < headers.length; i++) {
        var element_name = headers[i].getAttribute("spt_element_name");
        element_names.push(element_name);
    }
    spt.table.element_names = element_names;
    return spt.table.element_names;

}



spt.table.get_column_index = function(element_name) {
    var index = -1;

    var table = spt.table.get_header_table();

    // first find the index
    var header_row = table.getElement(".spt_table_header_row");
    var headers = header_row.getElements(".spt_table_header");
    for (var i = 0; i < headers.length; i++) {
        var header_element_name = headers[i].getAttribute("spt_element_name");
        if (element_name == header_element_name) {
            index = i;
            break;
        }
    }
    return index;
}


spt.table.get_column_index_by_cell = function(cell) {
    // get the parent row
    var row = cell.getParent(".spt_table_row");

    // it could be inline insert 
    if (!row)
        row = cell.getParent(".spt_table_insert_row");
      

    // get all of the cells
    var cells = row.getElements(".spt_cell_edit");

    var index = -1;
    for (var i = 0; i < cells.length; i++) {
        if (cells[i] == cell) {
            index = i;
            break;
        }
    }

    return index;

}



spt.table.get_element_name_by_header = function(header) {
    return header.getAttribute("spt_element_name");

}


spt.table.get_element_name_by_cell = function(cell) {

    var index = spt.table.get_column_index_by_cell(cell);
    var element_names = spt.table.get_element_names();
    return element_names[index];

}



spt.table.get_all_search_keys = function() {
    var embedded = false;
    var rows = spt.table.get_all_rows(embedded);
    
    var search_keys = [];
    // Any future custom row may not have search_key
    for (var i = 0; i < rows.length; i++) {
        if (rows[i].hasClass("spt_removed")) {
            continue;
        }
        var search_key = rows[i].getAttribute("spt_search_key");
        if (search_key)
            search_keys.push(search_key);
    }

    return search_keys;
}


spt.table.get_group_rows = function() {
    var table = spt.table.get_table();
    var gp_rows = table.getElements(".spt_group_row");
    return gp_rows;
}

spt.table.get_header_row = function() {
    var table = spt.table.get_header_table();
    var header_row = table.getElement(".spt_table_header_row");
    return header_row;
}



spt.table.get_header = function(element_name) {
    var headers = spt.table.get_headers();
    for (var i = 0; i < headers.length; i++) {
        if (headers[i].getAttribute("spt_element_name") == element_name) {
            return headers[i];
        }
    }
    return null;
}



spt.table.get_header_by_cell = function(cell) {
    var headers = spt.table.get_headers();
    var index = spt.table.get_column_index_by_cell(cell);
    return headers[index];
}



spt.table.get_headers = function() {
    var table = spt.table.get_header_table();
    if (!table)
        return [];

    var header_row = table.getElement(".spt_table_header_row");
    var headers = header_row.getElements(".spt_table_header");
    return headers
}

/* to get embedded rows, set embedded=true, default should be false */
spt.table.get_all_rows = function(embedded) {
    if (typeof(embedded) == 'undefined') 
        embedded = false;

    var table = spt.table.get_table();
    var css = embedded ? ".spt_table_row" : ".spt_table_row_" + table.getAttribute('id');
    var rows = table.getElements(css);
    return rows;
}


spt.table.get_first_row = function(embedded) {
    var table = spt.table.get_table();
    var row = table.getElement(".spt_table_row");
    return row;
}



spt.table.get_row_by_cell = function(cell) {
    var row = cell.getParent(".spt_table_row");
    if (!row) {
        row = cell.getParent(".spt_table_insert_row");
    }
    return row;
}



spt.table.get_row_by_search_key = function(search_key) {
    var rows = spt.table.get_all_rows();
    for (var i = 0; i < rows.length; i++) {
        var row_search_key = rows[i].getAttribute("spt_search_key_v2");
        if (search_key == row_search_key) {
            return rows[i];
        }
    }
    return null;
}




spt.table.get_cells = function(element_name, tr) {
    
    var table = spt.table.get_table();
    var index = spt.table.get_column_index(element_name);
    
    // get all of the cells
    var tds = [];
    var rows = tr ? [tr] : table.getElements(".spt_table_row");
    for (var i = 0; i < rows.length; i++) {
        var row_tds = rows[i].getElements(".spt_cell_edit");
        td = row_tds[index];
        tds.push(td);
    }

    return tds;
}


spt.table.get_cell = function(element_name, tr) {
    var tds = spt.table.get_cells(element_name, tr);
    if (tds.length == 0) {
        return null;
    }
    return tds[0];
}



spt.table.get_group_cells = function(element_name, tr) {
    
    var table = spt.table.get_table();
    var index = spt.table.get_column_index(element_name);
    
    // get all of the cells
    var tds = [];
    var rows = tr ? [tr] : table.getElements(".spt_table_group_row");
    for (var i = 0; i < rows.length; i++) {
        var row_tds = rows[i].getElements(".spt_group_cell");
        td = row_tds[index];
        tds.push(td);
    }

    return tds;
}



// Selection methods


spt.table.last_selected_row = null;

spt.table.select_row = function(row) {
    var cell = row.getElement(".spt_table_select")
    if (cell) {
        cell.removeClass("look_dg_row_select_box");
        cell.addClass("look_dg_row_select_box_selected");
    }

    var current_color = row.getAttribute("spt_hover_background");

    if (!current_color) {
        current_color = row.getStyle("background-color")
    }
    if (!spt.has_class(row,'spt_table_selected')) {

        row.setAttribute("spt_last_background", current_color);
        row.setStyle("background-color", spt.table.select_color);
        row.setAttribute("spt_background", spt.table.select_color);
        row.addClass("spt_table_selected");
    }
    spt.table.last_selected_row = row;
}


spt.table.unselect_row = function(row) {
    var cell = row.getElement(".spt_table_select")
    if (cell) {
        cell.removeClass("look_dg_row_select_box_selected");
        cell.addClass("look_dg_row_select_box");
    }
    row.setStyle("background-color", row.getAttribute("spt_last_background"));
    row.setAttribute("spt_background", row.getAttribute("spt_last_background"));
    row.removeClass("spt_table_selected");
    spt.table.last_selected_row = null;
}


spt.table.select_all_rows = function() {
    var rows = spt.table.get_all_rows();
    for (var i = 0; i < rows.length; i++) {
        spt.table.select_row(rows[i]);
    }
}


spt.table.unselect_all_rows = function() {
    var rows = spt.table.get_all_rows();
    for (var i = 0; i < rows.length; i++) {
        spt.table.unselect_row(rows[i]);
    }
}


spt.table.get_selected_rows = function() {
    var table = spt.table.get_table();
    if (!table) {
        log.warning("Table can't be determined. It's possible you are running this on the old table layout");
        return [];
    }
    var rows = table.getElements(".spt_table_selected");
    return rows;
}



spt.table.get_selected_search_keys = function(use_id) {
    var rows = spt.table.get_selected_rows();
    var search_keys = [];
    // if use_id is false, search_key uses code
    if (use_id == null) use_id = true;

    for (var i = 0; i < rows.length; i++) {
        var search_key = use_id ? rows[i].getAttribute("spt_search_key") : rows[i].getAttribute("spt_search_key_v2");
        search_keys.push(search_key);
    }

    return search_keys;
}

spt.table.get_selected_codes = function() {
    var rows = spt.table.get_selected_rows();
    var codes = [];
    var server = TacticServerStub.get();
    for (var i = 0; i < rows.length; i++) {
        var search_key = rows[i].getAttribute("spt_search_key_v2");
        var tmps = server.split_search_key(search_key)
        codes.push(tmps[1]);
    }
    return codes;
}




spt.table.add_hidden_row = function(row, class_name, kwargs) {
    //var clone = spt.behavior.clone(row);
    var clone = document.createElement("tr");
    clone.addClass("spt_hidden_row");
    //clone.setStyle("background", bvr.hidden_row_color);
    //var color = row.getStyle("background-color");
    var color = row.getAttribute("spt_hover_background");
    clone.setStyle("background", color);

    var children = row.getChildren();
    var num_children = children.length;
    var html = '<img src="/context/icons/common/indicator_snake.gif" border="0"/>';
    clone.innerHTML = "<td class='spt_hidden_row_cell' colspan='"+num_children+"'>"+html+" Loading ...</td>";
    clone.inject(row, "after");

    var hidden_row = clone.getElement(".spt_hidden_row_cell");
    hidden_row.setStyle("height", "50px");
    //hidden_row.setStyle("padding", "5px");
    hidden_row.setStyle("font-size", "14px");
    hidden_row.setStyle("font-weight", "bold");

    // position the arrow
    var src_el = kwargs.src_el;
    kwargs.src_el = "";
    var pos = src_el.getPosition(row);
    var dx = pos.x - 30; 



    var server = TacticServerStub.get();

    var kwargs_old = {
      'args': kwargs,
      'cbjs_action': function(widget_html) {
        hidden_row.setStyle("padding-left", "32px");
        hidden_row.setStyle("font-size", "12px");
        hidden_row.setStyle("font-weight", "normal");
        spt.behavior.replace_inner_html(hidden_row, widget_html);
        var child = hidden_row.firstChild;
        if (child) {
            hidden_row.setStyle("overflow", "hidden");
            var size = child.getSize();
            child.setStyle("margin-top", -size.y-100);
            new Fx.Tween(child, {duration: "short"}).start('margin-top', "0px");
        }
      }
    }
    if (spt.table.last_table.hasOwnProperty('hidden_zindex'))
        spt.table.last_table.hidden_zindex += 1;
    else
        spt.table.last_table.hidden_zindex = 100;
    

    // New popup test
    var kwargs = {
      'args': kwargs,
      'cbjs_action': function(widget_html) {
        hidden_row.setStyle("padding-left", "32px");
        hidden_row.setStyle("font-size", "12px");
        hidden_row.setStyle("font-weight", "normal");
        hidden_row.setStyle("min-width", "300px");

        var shadow_color = spt.table.shadow_color;

        var border_color = "#777";

        // test make the hidden row sit on top of the table
        widget_html = "<div class='spt_hidden_content_top' style='border: solid 1px "+border_color+"; position: relative; z-index:" + spt.table.last_table.hidden_zindex + "; box-shadow: 0px 0px 15px "+shadow_color+"; background: "+color+"; margin-right: 20px; margin-top: 14px; overflow: hidden; min-width: 300px'>" +

          "<div class='spt_hidden_content_pointer' style='border-left: 13px solid transparent; border-right: 13px solid transparent; border-bottom: 14px solid "+color+";position: absolute; top: -14px; left: "+dx+"px'></div>" +
          "<div style='border-left: 12px solid transparent; border-right: 12px solid transparent; border-bottom: 13px solid "+color+";position: absolute; top: -13px; left: "+(dx+1)+"px'></div>" +

          "<div class='spt_remove_hidden_row' style='position: absolute; right: 3px; top: 3px; z-index: 50'><img src='/context/icons/custom/popup_close.png'/></div>" +
          "<div class='spt_hidden_content' style='padding-top: 3px'>" + widget_html + "</div></div>";

        hidden_row.setStyle("display", "none");
        var cell = src_el.getParent('.spt_cell_no_edit');
        var elem_name = spt.table.get_element_name_by_cell(cell)
        clone.setAttribute('column', elem_name);
        spt.behavior.replace_inner_html(hidden_row, widget_html);

        var top = hidden_row.getElement(".spt_hidden_content_top");
        var pointer = hidden_row.getElement(".spt_hidden_content_pointer");
        var child = hidden_row.getElement(".spt_hidden_content");
        if (child) {
            hidden_row.setStyle("overflow", "hidden");
            var size = child.getSize();
            child.setStyle("margin-top", -size.y-100);
            var fx = new Fx.Tween(child, {
                duration: "short",
            } )
            fx.addEvent("complete", function() {
                hidden_row.firstChild.setStyle("overflow", "");
            });
            fx.start('margin-top', "0px");
            hidden_row.setStyle("display", "");

            var pos_top = top.getPosition(hidden_row);
            var pos_pointer = pointer.getPosition(hidden_row);
            var top_size = top.getSize();
            if (pos_pointer.x-top_size.x > pos_top.x) {
                top.setStyle("margin-left", pos_pointer.x-top_size.x+5);
            }
        }
      }
    }


    server.async_get_widget(class_name, kwargs);
}


spt.table.remove_hidden_row = function(row, col_name, is_hidden) {
    // if it is hidden_row, just use it as is without getting Next 
    var sibling = is_hidden ? row: row.getNext();
    if (col_name) {
        while (sibling && sibling.getAttribute('column') != col_name) {
            sibling = sibling.getNext();
        }
    }
    
    if (sibling && sibling.hasClass("spt_hidden_row")) {
        // get the first child
        var child = sibling.getElement(".spt_hidden_content");

        if (child) {
            sibling.firstChild.firstChild.setStyle("overflow", "hidden");
            var size = child.getSize();
            var fx = new Fx.Tween(child, {
                duration: "short",
            } )
            fx.addEvent("complete", function() {
                spt.table.remove_hidden_row(sibling, null, true);
                spt.behavior.destroy_element(sibling);
            });
            fx.start('margin-top', -size.y-100+"px");
        }
        else {
            spt.table.remove_hidden_row(sibling);
            spt.behavior.destroy_element(sibling);
        }
    }
}


spt.table.remove_hidden_row_from_inside = function(el) {
    var hidden_row = el.getParent(".spt_hidden_row"); 
    var col_name = hidden_row.getAttribute('column');
    
    spt.table.remove_hidden_row(hidden_row, col_name, true);
}




// add rows from search_keys
spt.table.add_rows = function(row, search_type, level) {

    var server = TacticServerStub.get();

    search_key = row.getAttribute("spt_search_key");

    var kwargs = spt.table.get_refresh_kwargs(row);

    var load_tr = document.createElement("tr");
    var load_td = document.createElement("td");
    load_tr.appendChild(load_td);
    load_td.setAttribute("colspan", "10");
    load_td.innerHTML = "Loading ("+search_type+") ...";
    load_tr.inject(row, "after");
    load_td.setStyle("padding", "5px");


    // make some adjustments
    kwargs['search_type'] = search_type;
    kwargs['search_key'] = search_key;
    delete kwargs['search_keys'];


    var kw = {
        'args': kwargs,
        'cbjs_action': function(widget_html) {
            var dummy = document.createElement("div");
            spt.behavior.replace_inner_html(dummy, widget_html);

            //load_tr.destroy();
            spt.behavior.destroy_element(load_tr);

            var new_rows = dummy.getElements(".spt_table_row");
            // the insert row is not included here any more
            //new_rows.reverse();
            for (var i = 0; i < new_rows.length; i++) {
                new_rows[i].inject(row, "after");
                // remap the parent
                new_rows[i].setAttribute("spt_parent_key", search_key);
                var parts = search_key.split("?");
                new_rows[i].setAttribute("spt_parent_type", parts[0]);

                new_rows[i].setAttribute("spt_level", level);
                var el = new_rows[i].getElement(".spt_level_listen");
                if (el) {
                    el.setStyle("margin-left", level*15);
                }
            }
            if (new_rows.length) {
                spt.table.recolor_rows();
            }

        }
    }

    var class_name = 'tactic.ui.panel.table_layout_wdg.FastTableLayoutWdg';
    server.async_get_widget(class_name, kw);
}



// editablility of the layout

spt.table.last_edit_wdgs = null;
spt.table.last_edit_wdg = null;
spt.table.last_data_wdg = null;
spt.table.last_cell = null;



spt.table.get_insert_row = function() {
    var layout = spt.table.get_layout();
    var insert_row = layout.getElement(".spt_table_insert_row");
    return insert_row;
}


spt.table.get_insert_rows = function() {
    var layout = spt.table.get_layout();
    var insert_rows = layout.getElements(".spt_table_insert_row");
    var rows = []
    for (var i=0; i < insert_rows.length; i++) {
        if (!spt.has_class(insert_rows[i], 'spt_clone'))
            rows.push(insert_rows[i])
    }
    return rows;
}

spt.table.get_insert_row_cell = function(element_name) {
    var insert_row = spt.table.get_insert_row();
    var cells = insert_row.getElements('.spt_cell_edit');
    for (var i = 0; i < cells.length; i++) {
        if (cells[i].getAttribute("spt_element_name") == element_name) {
            return cells[i];
        }
    }
    return null;
}


spt.table.set_parent_key = function(parent_key) {
    var insert_rows = spt.table.get_insert_rows()
    for (var i = 0; i < insert_rows.length; i++) {
        var row = insert_rows[i];
        row.setAttribute("spt_parent_key", parent_key)
    }
}



spt.table.set_connect_key = function(connect_key) {
    var insert_rows = spt.table.get_insert_rows()
    for (var i = 0; i < insert_rows.length; i++) {
        var row = insert_rows[i];
        row.setAttribute("spt_connect_key", connect_key)
    }
}


// regular visible data 

spt.table.get_data = function(row) {
    var data = {};
    if (row) {
        var cells = row.getElements('.spt_cell_edit'); 
        var element_names = spt.table.get_element_names();
        for (var k = 0; k < cells.length; k++) {
            var cell = cells[k];
            data[element_names[k]] = cell.getAttribute('spt_input_value');   
        }
    }
    return data   
}


spt.table.set_data = function(row, data) {
    var changed = false;
    for (a in data) {
        if (data.hasOwnProperty(a)) {
            var cell = row.getElement('td[spt_element_name=' + a + ']');
          
            var value = data[a];
            cell.innerHTML = value;
            cell.setAttribute('spt_input_value', value);
            spt.add_class(cell, 'spt_cell_changed');
            changed = true;
            spt.table.set_changed_color(row, cell);
        }
    }
    if (changed) 
        spt.add_class(row, "spt_row_changed");
}



// Extra data functions

spt.table.add_extra_value = function(row, name, value) {
    var extra_data = row.extra_data;
    if (typeof(extra_data) == 'undefined') {
        extra_data = {};
        row.extra_data = extra_data;
    }
    extra_data[name] = value;
    return extra_data;
}

spt.table.set_extra_data = function(row, data) {
    row.extra_data = data;
}


spt.table.add_insert_extra_value = function(name, value) {
    var insert_rows = spt.table.get_insert_rows()
    for (var i = 0; i < insert_rows.length; i++) {
        var row = insert_rows[i];
        spt.table.add_extra_value(row, name, value);
    }
}





spt.table.add_new_item = function(kwargs) {

    if (typeof(kwargs) == 'undefined') {
        kwargs = {};
    }

    var insert_row = spt.table.get_insert_row();

    var row;
    var position;
    var table = spt.table.get_table();
    if (kwargs.insert_location == 'bottom') {
        var rows = spt.table.get_all_rows();
        if (rows.length == 0) {
            row = table.getElement(".spt_table_header_row");
        }
        else {
            row = rows[rows.length-1];
        }
        position = "after";

    }
    else {
        row = table.getElement(".spt_table_row");
        position = "before";
    }


    var clone = spt.behavior.clone(insert_row);

    if (!row) {
        var first = table.getElement("tr");
        if (first) {
            clone.inject(first, position);
        }
        else {
            table.appendChild(clone);
        }

        /*
        var clone_cells = clone.getElements(".spt_cell_edit");
        var header = spt.table.get_header_row();
        var headers = header.getElements(".spt_table_header");
        for (var i = 0; i < headers.length; i++) {
            var header = headers[i];
            var clone_cell = clone_cells[i];
            var size = header.getSize();
            clone_cell.setStyle("width", size.x);
        }
        */


    }
    else {
        // should specify a class under td to avoid selecting td within td
        var clone_cells = clone.getElements("td.spt_cell_edit");
        var cells = row.getElements("td.spt_cell_edit");
        for (var i = 0; i < cells.length; i++) {
            var cell = cells[i];
            var clone_cell = clone_cells[i];
            var size = cell.getSize();
            if (clone_cell)
                clone_cell.setStyle("width", size.x);
        }

        clone.inject(row, position);


    }
    spt.remove_class(clone, 'spt_clone');

    // find the no items row
    no_items = table.getElement(".spt_table_no_items");
    if (no_items != null) {
        no_items.destroy();
    }
    
    return clone;
}


spt.table.get_edit_wdg = function(element_name) {
    // get the edit widgets
    var edit_wdgs;
    var layout = spt.table.get_layout();

    var edit_top = layout.getElement(".spt_edit_top");
    if (!edit_top) 
        return null;

    var edit_wdgs = edit_top.getElements(".spt_edit_widget");
    for (var i = 0; i < edit_wdgs.length; i++) {
        var edit_element_name = edit_wdgs[i].getAttribute("spt_element_name");
        if (edit_element_name == element_name) {
            return edit_wdgs[i];
        }
    }

    return null;
}



spt.table.get_edit_wdg_by_index = function(index) {
    // get the edit widgets
    var edit_wdgs;
    var layout = spt.table.get_layout();

    var edit_top = layout.getElement(".spt_edit_top");
    var edit_wdgs = edit_top.getElements(".spt_edit_widget");
    spt.table.last_edit_wdgs = edit_wdgs;

    var edit_wdg = edit_wdgs[index];

    return edit_wdg;
}




spt.table.show_edit = function(cell) {
    // If this cell is already open, then don't do anything
    if (cell == spt.table.last_cell) {
        return;
    }
    var header = spt.table.get_header_by_cell(cell);
    if (header.getAttribute("spt_input_type") == 'inline') {
        return;
    }

    // if there was another edit open, then destroy it.
    if (spt.table.last_edit_wdg) {
        spt.table.last_edit_wdg.destroy();
        // empty the last cell
        spt.table.last_cell.innerHTML = '';

        // this data wdg can be null if there is no data
        if (spt.table.last_data_wdg != null) {
            spt.table.last_cell.appendChild(spt.table.last_data_wdg);
        }
    }
    var element_name = spt.table.get_element_name_by_cell(cell);
    var edit_wdg = spt.table.get_edit_wdg(element_name);
    if (edit_wdg == null) {
        spt.table.last_cell = null;
        spt.table.last_edit_wdg = null;
        return;
    }

    

    // remove the first child
    // FIXME: should we rely on firstChild?
    var first_child = $(cell.firstChild);

    // get the size before the edit widget is added
    var size = cell.getSize();

    if (first_child == null) {
        var tmp = $(document.createElement("span"));
        tmp.innerHTML = "";
        spt.table.last_data_wdg = tmp;
    }
    else if ( first_child.nodeName == '#text') {
        var tmp = $(document.createElement("span"));
        tmp.innerHTML = first_child.nodeValue;
        spt.table.last_data_wdg = tmp;
    }
    else {
        spt.table.last_data_wdg = first_child;
    }

    // get the size before the edit widget is added
    var size = cell.getSize();

    // clear the cell
    cell.innerHTML = '';


    // code to find the edit_wdg internally
    var edit_wdg = spt.table._find_edit_wdg(cell, edit_wdg);


    // add the edit to do the dom
    cell.setStyle("position", "relative");
    cell.setStyle("overflow", "");

    cell.appendChild(edit_wdg);
    edit_wdg.setStyle("position", "absolute");
    edit_wdg.setStyle("top", "0px");
    edit_wdg.setStyle("left", "0px");
    edit_wdg.setStyle("margin", "-1px");
    edit_wdg.setStyle("z-index", 500);



    
    // code here to adjust the size of the edit widget
    spt.table.alter_edit_wdg(cell, edit_wdg, size);


    // put a dummy element in there to fill the space
    var dummy = $(document.createElement("div"));
    if (typeof(size) != 'undefined') {
        // the offset takes into account the padding (3px) and border (1px) x2
        dummy.setStyle("height", size.y-8);
    }
    dummy.innerHTML = "&nbsp;";
    cell.appendChild(dummy);



    spt.table.last_edit_wdg = edit_wdg;
    spt.table.last_cell = cell;
}


spt.table.revert_edits = function() {
    var rows = spt.table.get_changed_rows();
    for (var i = 0; i < rows.length; i++) {
        var cells = rows[i].getElements(".spt_cell_changed");
        for (var j = 0; j < cells.length; j++) {
            var cell = cells[j];
            var orig_value = cell.getAttribute("spt_orig_input_value");
            cell.innerHTML = orig_value;
            cell.setAttribute("spt_input_value", orig_value);
            cell.setStyle("background-color", "");

            cell.removeClass("spt_cell_changed");
        }

        rows[i].setStyle("background-color", "");
        rows[i].setAttribute("spt_background", "");
        rows[i].removeClass("spt_row_changed");
    }
}


spt.table.recolor_rows = function() {
    var table = spt.table.get_table();
    var bgcolor1 = table.getAttribute("spt_bgcolor1");
    var bgcolor2 = table.getAttribute("spt_bgcolor2");

    var rows = spt.table.get_all_rows();
    for (var i = 0; i < rows.length; i++) {
        if ( i % 2 ) {
            rows[i].setStyle("background-color", bgcolor1);
        }
        else {
            rows[i].setStyle("background-color", bgcolor2);
        }
    }

}



spt.table._find_edit_wdg = function(cell, edit_wdg_template) {

    var edit_wdg = null;
   
    // create one from scratch using a script
    var edit_script = edit_wdg_template.getAttribute("edit_script");
    if (edit_script != null) {

        var get_edit_wdg_code = edit_script;
        var get_edit_wdg_script = spt.CustomProject.get_script_by_path(get_edit_wdg_code);

        edit_wdg = $(document.createElement("div"));
        edit_wdg.setStyle("position", "absolute");
        edit_wdg.setStyle("margin-top", "-3px");
        edit_wdg.setStyle("margin-left", "-3px");

        eval( "var func = function() {" +get_edit_wdg_script+"}");
        edit_html = func();
        spt.behavior.replace_inner_html( edit_wdg, edit_html);
        return edit_wdg;

    }

    var edit_wdg_options = edit_wdg_template.getElements('.spt_input_option');
    if (edit_wdg_options.length == 0) {
        //var type = cell_to_edit.getAttribute("spt_input_type");
        //if (type == 'inline')
        //    return null;
        edit_wdg = edit_wdg_template;
    }
    else {
        var key = null;

        // some edit definition has specific depend attr,
        var top_wdg = edit_wdg_template.getElement(".spt_input_top");
        var cbjs_get_key = null;
        if (top_wdg) {
            cbjs_get_key = top_wdg.getAttribute("spt_cbjs_get_input_key");
        }

        // Backwards compatible variable names
        var cell_to_edit = cell;
        var edit_cell = edit_wdg_template;
        if (cbjs_get_key != null) {
            eval("key_callback = function() { " + cbjs_get_key + " }");
            key = key_callback();
        }

        // find the key in the cell (NOTE: this should be "spt_input_key"
        if (! key)
            key = cell.getAttribute("spt_input_value");

        // find the key
        var found = false;
        for (var y =0; y<edit_wdg_options.length;y++) {
            edit_wdg = edit_wdg_options[y];
            var input_key = edit_wdg.getAttribute("spt_input_key");
            if (input_key == key) {
                found = true;
                wdg_index = y;
                break;
            }
        }
        // if not found, just use the first one
        if (!found) {
            wdg_index = 0;
            edit_wdg = edit_wdg_options[0];
        }
    }


    // clone the template edit_wdg
    var clone = spt.behavior.clone(edit_wdg);
    //clone.setStyle("position", "absolute");
    //clone.setStyle("top", "0px");
    //clone.setStyle("left", "0px");

    /*
    var size = cell.getSize();
    if (typeof(size) != 'undefined') {
        clone.setStyle("margin-top", (-3)+"px");
    }
    else {
        clone.setStyle("margin-top", "-3px");
    }
    clone.setStyle("margin-left", "-3px");
    */


    return clone;

}




// adjust the edit cell depending on widget type
spt.table.alter_edit_wdg = function(edit_cell, edit_wdg, size) {

    // some edit_wdgs need no alterations
    //edit_wdg.setStyle("border", "solid 1px blue");
    if ( edit_wdg.getElement(".spt_no_alter") ) {
        return;
    }

    // this assumes there is an input that needs to altered
    var type = edit_cell.getAttribute("spt_input_type");
    var input = edit_wdg.getElement(".spt_input");


    var value = edit_cell.getAttribute("spt_input_value");
    var parse_selected_text = function(input)
    {
        var text_value = input.value;
        // this raises exceptions at times
        var sel_start = input.selectionStart;
        var sel_end = input.selectionEnd;

        if( sel_end == sel_start ) {
            return [ text_value.substr(0,sel_start), text_value.substr(sel_start) ];
        }

        var tval0 = text_value.substr( 0, sel_start );
        var tval1 = "";
        if( sel_end > sel_start ) {
            tval1 = text_value.substr( sel_end );
        }
        return [ tval0, tval1 ];
    }

    var set_focus = true;
    var accept_event = 'blur';
    var label = null;
    if (input == null) {
        return;
    }
    
    if (input.hasClass("SPT_NO_RESIZE") ) {
        // do nothing
    }
    else if (input.hasClass("SPT_NO_ACTION") ) {
        if (value) {
            input.value = value;
        }
    }
 
    else if (input.nodeName == "TEXTAREA") {
        set_focus = true;

        if (type == 'xml') {
            edit_wdg.setStyle( "min-height", '300px');
            edit_wdg.setStyle( "min-width", '300px');
        }
        if (size.y > 100)
            input.setStyle( "height", size.y+'px');
        else
            input.setStyle( "height", '100px');

        if (size.x > 250)
            input.setStyle( "width", size.x+'px');
        else
            input.setStyle( "width", '250px');
        input.setStyle('font-family', 'courier new');
        input.setStyle('font-size', '1.0em');
        input.setStyle('padding', '5px');

        input.value = value;
    }
    else if (input != null && input.type == "password") {
        input.setStyle( "width", size.x+'px');
        input.setStyle( "height", size.y+'px');
        input.value = ""
    }
    else if (input.nodeName == "INPUT") {
        set_focus = true;
        input.setStyle( "width", size.x+'px');
        input.setStyle( "height", size.y+'px');
        input.value = value;
        // for calendar input 
        if (spt.has_class(input, 'spt_calendar_input')){
            accept_event = 'change';
            input.setStyle( "width", size.x+30 + 'px');


            // **** NOT USED ****
            //edit_wdg.setStyle('background','white');
            //edit_wdg.setStyle('color','black');

            //setting date time
            //if (value && value.test( /^\d\d\d\d-\d\d-\d\d .*/ ) ) {
            if (false) {
                var parts = value.split(" ");
                var date_values = parts[0].split('-');
                var time_values = parts[1].split(':');
                spt.api.Utility.set_input_values(edit_wdg, time_values[0], '.spt_time_hour');
                spt.api.Utility.set_input_values(edit_wdg, time_values[1], '.spt_time_minute');

                var cal = edit_wdg.getElement('.spt_calendar_top');
                if (cal)
                    spt.panel.refresh(cal, {year: date_values[0], month: date_values[1]});
            }
            // -------------------




        }
        else if (input.type == "checkbox") {
            var cell_value = edit_cell.getAttribute('spt_input_value');
            if (cell_value in  {'true':1, 'True':1})
                input.checked = true;
            else
                input.checked = false;
            edit_wdg.setStyle( "width", size.x+'px');
            edit_wdg.setStyle( "height", size.y+'px');
            edit_wdg.setStyle( "text-align", 'center');
        }
 
    }
    else if (input.nodeName == "SELECT") {

        // Go through and be sure to set the default option to the one
        // with the value matching the spt_input_value of the cell you
        // are editing ...
        if( value == "[]" ) {
            value = "";
        }
        var option_list = input.getElements("option");
        for( var opt_c=0; opt_c < option_list.length; opt_c++ ) {
            var opt_el = option_list[opt_c];
            var opt_value = opt_el.getProperty("value");
            var opt_selected = opt_el.getProperty("selected");
            if( opt_selected && (value != opt_value) ) {
                opt_el.removeProperty("selected");
            }
            else if( !opt_selected && (value == opt_value) ) {
                opt_el.setProperty("selected", "selected");
            }
        }


        // Set the size of the SELECT element to be the length of all
        // the options available
        var select_size_to_set = input.options.length;

        // However, if the configuration specified a certain size for the
        // SELECT in configuration then use the size specified ...
        var spt_size = input.getProperty("spt_select_size");
        if( spt_size ) {
            select_size_to_set = parseInt( spt_size );
        }

        input.setStyle("height", "auto");
        input.setStyle("min-width", "100px");
        input.setStyle("width", "auto");

        edit_wdg.setStyle("position", "absolute");
        edit_wdg.setStyle("margin-right", "-3px");
        edit_wdg.setStyle("min-width", "100px");

        set_focus = true;
        accept_event = 'change';

        if( input.options.length > select_size_to_set ) {
            // only set to the configured select element size if actual
            // number of options is larger
            input.size = select_size_to_set;
        } else {
            input.size = input.options.length;
        }


        // FIXME: check if this is stil needed
        if( spt.browser.is_IE() ) {
            mult = 15;
            if (size.y < (input.size * mult)) {
                edit_wdg.setStyle( "height", (input.size * mult) + 'px');
            }
            else {
                edit_wdg.setStyle( "height", size.y+'px');
            }
        }
        // to avoid overlapping select in UI 
        edit_wdg.setStyle('z-index', '100' );
    } 

    else {
        edit_wdg.setStyle( "width", size.x+'px');
        edit_wdg.setStyle( "height", size.y+'px');

    }

    if (set_focus == true) {
        input.focus();
        input.value = input.value;
    }

    
       

    if (accept_event == 'blur') {
        input.addEvent("blur", function() {
            // to make checkbox aware of its checked state
            if (input.type =='checkbox')
               input.value = input.checked;
            spt.table.accept_edit(edit_wdg, input.value, true, {input: input});
        });
    }
    else {
        input.addEvent("click", function() {
            spt.table.accept_edit(edit_wdg, input.value, true, {input: input});
        });
    }


    input.addEvent("keydown", function(e) {
        var keys = ['tab','keys(control+enter)', 'enter'];
        var key = e.key;
        if (keys.indexOf(key) > -1) e.stop();

        if (key == 'tab') {
            if (input.nodeName == "SELECT") {
                spt.table.accept_edit(edit_wdg, input.value, true, {input: input});
            }
            else {
                input.blur();
            }
            // get the next cell
            var next_cell = edit_cell.getNext();
            spt.table.show_edit(next_cell);

        }
        else if (key == 'enter') {
            if (e.control == false) {
                if (input.nodeName == "SELECT") {
                    spt.table.accept_edit(edit_wdg, input.value, true, {input: input});
                }
                else {
                    input.blur();
                }
            }
            else {
                 // TODO: check if it's multi-line first 
                 //... use ctrl-ENTER for new-line, regular ENTER (RETURN) accepts value
                var tvals = parse_selected_text(input);
                input.value = tvals[0] + "\\n" + tvals[1];
                spt.set_cursor_position( input, tvals[0].length + 1 );
            
                //if (spt.browser.is_Webkit_based() ) {
                //input.value = input.value + "\\n";
                //}
            }
        }
    } )


    return;

}





spt.table.get_changed_rows = function(embedded) {
    if (typeof(embedded) == 'undefined') 
        embedded = false;
    var table = spt.table.get_table();
    var css = embedded ? ".spt_table_row" : ".spt_table_row_" + table.getAttribute('id');
    var rows = table.getElements(css + ".spt_row_changed");
    return rows;
}


spt.table.has_changes = function() {
    var changed_rows = spt.table.get_changed_rows();
    if (changed_rows.length > 0) {
        return true;
    }
    else {
        return false;
    }
}


spt.table.get_bottom_row = function() {
    var table = spt.table.get_table();
    var row = table.getElement(".spt_table_bottom_row");
    return row;
}


spt.table.accept_edit = function(edit_wdg, new_value, set_display, kwargs) {

    if (typeof(set_display) == 'undefined') {
        set_display = true;
    }
    if (!kwargs) kwargs = {};
    var new_label = null;

    // we can optionally pass in the input element
    var input = kwargs.input ? kwargs.input : null;
    if (input) {
        if (input.nodeName == "SELECT")
            new_label = input.options[input.selectedIndex].text;
    }
    var display_value = new_label ? new_label : new_value;
    var edited_cell;
    if (edit_wdg.hasClass("spt_cell_edit")) {
        edited_cell = edit_wdg;
    }
    else {
        edited_cell = edit_wdg.getParent(".spt_cell_edit");
    }

    var old_value = edited_cell.getAttribute("spt_input_value");
    
    var ignore_multi = kwargs.ignore_multi ? true : false;

    var header = spt.table.get_header_by_cell(edited_cell);

    var is_inline_wdg = header.getAttribute("spt_input_type") == 'inline' ? true : false;
    var input_type = header.getAttribute("spt_input_type");
    
    // Multi EDIT
    var selected_rows = spt.table.get_selected_rows();
    var in_selected_row = edited_cell.getParent("tr.spt_table_selected");
    
    var changed = old_value != new_value;

    if (!ignore_multi && selected_rows.length > 0 && changed && in_selected_row) {
        // get all of the cells with the same element_name
        var index = spt.table.get_column_index_by_cell(edited_cell);

        for (var i = 0; i < selected_rows.length; i++) {
            var cell = selected_rows[i].getElements(".spt_cell_edit")[index];
           
            spt.table._accept_single_edit(cell, new_value);

            if (set_display) {
                cell.innerHTML = "";
                cell.setStyle("overflow", "hidden");
                spt.table.set_display(cell, display_value, input_type);
            }
            
        }

    }
    else {
        spt.table._accept_single_edit(edited_cell, new_value);

        if (set_display) {
            edited_cell.innerHTML = "";
            edited_cell.setStyle("overflow", "hidden");
            spt.table.set_display(edited_cell, display_value, input_type);
        }

    }


    if (spt.table.last_edit_wdg) {
        spt.table.last_edit_wdg.destroy();
        
    }


    spt.table.last_cell = null;
    spt.table.last_data_wdg = null;
    spt.table.last_edit_wdg = null;
    spt.kbd.clear_handler_stack();


    var table_layout = spt.table.get_layout();
    var save_button = table_layout.getElement(".spt_save_button");
    if (save_button) {
        save_button.setStyle("display", "");
    }



}


spt.table.set_display = function( el, value, input_type ) {


    if (input_type == 'inline') {
        return;
    }

    if (input_type == 'xml' || value.substr(0,1) == '<') {

        var label = value;
        //var is_xml = label.substr(0,6) == '<?xml ';
        var is_xml = true;

        label = label.replace(/</g, "&amp;lt;");
        label = label.replace(/>/g, "&amp;gt;");


        if (value == '') {
            el.innerHTML = "<div style='padding: 3px'>&nbsp;</div>";
        }
        else if (is_xml == true) {
            el.innerHTML = "<pre>" + label + "</pre>";
        }
        else {
            label = label.replace(/\\n/g, "<br/>");
            el.innerHTML = "<div style='padding: 3px'>"+label+"</div>";
        }

    }
    else if (input_type == 'password') {
        el.innerHTML = "********************************";
        return;
    }

    else {
        el.innerHTML = value;
    }
}

spt.table.set_changed_color = function(row, cell) {
    
    cell.setAttribute("spt_orig_background", cell.getStyle("background-color"));
    row.setAttribute("spt_orig_background", row.getAttribute("spt_background"));

    // so we don't have to search for the colors
    var colors = spt.Environment.get().get_colors();
    var theme = colors.theme;

    if (theme == "dark") {
        row.setStyle("background-color", "#204411");
        cell.setStyle("background-color", "#305511");
        row.setAttribute("spt_background", "#204411");
    } 
    else {
        //color = "rgba(188, 207, 215, 1.0)";
        //color2 = "rgba(188, 207, 215, 0.6)";
        color = "rgba(207, 215, 188, 1.0)";
        color2 = "rgba(207, 215, 188, 0.6)";

        row.setStyle("background-color", color2);
        cell.setStyle("background-color", color);
        row.setAttribute("spt_background", color2);

        //row.setStyle("background-color", "#C0CC99");
        //cell.setStyle("background-color", "#909977");
        //row.setAttribute("spt_background", "#C0CC99");
    }
}

spt.table._accept_single_edit = function(cell, new_value) {
    var old_value = cell.getAttribute("spt_input_value");
    if (old_value != new_value) {

        // remember the original value
        var orig_value = cell.getAttribute("spt_orig_input_value");
        if (!orig_value) {
            cell.setAttribute("spt_orig_input_value", old_value);
        }

        // set the new_value
        cell.setAttribute("spt_input_value", new_value);

        var row = cell.getParent(".spt_table_row");
        if (!row)
            row = cell.getParent(".spt_table_insert_row");

        if (new_value == orig_value) {
            cell.removeClass("spt_cell_changed");
            row.removeClass("spt_row_changed");

            cell.setStyle("background-color", cell.getAttribute("spt_orig_background"));
            row.setStyle("background-color", row.getAttribute("spt_orig_background"));
            row.setAttribute("spt_background", row.getAttribute("spt_orig_background"));
        }
        else {
            cell.addClass("spt_cell_changed");
            row.addClass("spt_row_changed");
            spt.table.set_changed_color(row, cell);
        }

        // fire an event
        var search_key = row.getAttribute("spt_search_key");
        var parts = search_key.split("?");
        var search_type = parts[0];
        var event = "accept|" + search_type;
        var element_name = spt.table.get_element_name_by_cell(cell);
        var input = {
            'element_name': element_name,
            'search_key': search_key,
            'old_value': old_value,
            'new_value': new_value,
            'orig_value': orig_value,
            'row': row,
            'cell': cell,
        }
        bvr.options = input;

        try {
            spt.named_events.fire_event(event, bvr);
        }
        catch(e) {
            spt.alert("Error firing accept event: " + event);
        }

        // Check for any validations that need to be run on this value change ...
        //
        var table_layout = cell.getParent(".spt_layout");
        var table_validations_div = table_layout.getElement(".spt_table_validations");

        var cls_tag = "spt_validation_" + element_name

        var validation_div = table_validations_div.getElement( "." + cls_tag );
        if( validation_div ) {
            var v_bvr_list = spt.behavior.get_bvrs_by_type( "validation", validation_div );
            spt.validation.check( new_value, v_bvr_list, cell );

            // FROM OLD LOGIC: in case we need to have the validation revise the value at all (e.g. to make upper case, etc.)
            // we check for the flag to let us push the change, and if so we push the revised value back into
            // the values and labels dicts ...
            /* comment out for now
            if( '_spt_push_new_value_to_label' in cell ) {
                values[element_name] = cell.getAttribute("spt_input_value");
                labels[element_name] = cell.getAttribute("spt_input_value");
            }*/
        }
    }
}



spt.table.save_changes = function(kwargs) {
    if (!kwargs) {
        kwargs = {};
    }

    var do_refresh = true;
    if (kwargs.refresh == false) {
        do_refresh = false;
    }

    spt.app_busy.show("Saving Changes ...");
    var rows = spt.table.get_changed_rows();

    var insert_data = [];
    var update_data = [];
    var search_keys = [];
    var web_data = []; 
    var extra_data = [];

    var parent_key = null;    
    var connect_key = null;    

    for (var i = 0; i < rows.length; i++) {

        if (!parent_key)
            parent_key = rows[i].getAttribute("spt_parent_key");

        if (!connect_key)
            connect_key = rows[i].getAttribute("spt_connect_key");

        // get extra data
        var extra_data_row = rows[i].extra_data
        if (extra_data_row) {
            extra_data.push(extra_data_row);
        }
        else {
            extra_data.push(null);
        }


        var search_key = rows[i].getAttribute("spt_search_key");
        search_keys.push(search_key);
        var cells = rows[i].getElements(".spt_cell_changed");
        var data = {};
        var single_web_data = {};
        update_data.push(data);
        web_data.push(single_web_data);
        for (var j = 0; j < cells.length; j++) {
            var cell = cells[j];
            var element_name = spt.table.get_element_name_by_cell(cell);
            var value = cell.getAttribute("spt_input_value");
            data[element_name] = value;

            var header = spt.table.get_header_by_cell(cell);
            if (header.getAttribute("spt_input_type") == 'inline') {
                if (cell.getAttribute("spt_input_type") =='gantt') {
                    var gantt_values = spt.api.Utility.get_input_values(cell, '.spt_gantt_data', false);
                    single_web_data['gantt_data'] = gantt_values['gantt_data'];
                }
                else if (cell.getAttribute("spt_input_type") =='work_hour') {
                    var web_values = spt.api.Utility.get_input_values(cell, '.spt_workhour_data', false);
                    single_web_data['workhour_data'] = web_values['workhour_data'];
                }
                else if (cell.getAttribute("spt_input_type") =='tasks') {
                    var web_values = spt.api.Utility.get_input_values(header, '.spt_process_data', false);
                    single_web_data['process_data'] = web_values['process_data'];
                }
                else { // generic inline-type widget
                    var web_values = spt.api.Utility.get_input_values(cell, null, false);
                    single_web_data['inline_data'] = web_values;
                }
            }
      
                
        }
    }

    if (search_keys.length == 0) {
        spt.alert("No changes have been made");
        spt.app_busy.hide();
        return;
    }

    var element_names = spt.table.get_element_names();
    element_names = element_names.join(",");

    // actually do the update
    var server = TacticServerStub.get();

    // use the edit command to understand what do do with the update data
    var layout = spt.table.get_layout()
    var class_name = layout.getAttribute("spt_save_class_name");
    if (class_name == null) {
        class_name = 'tactic.ui.panel.EditMultipleCmd';
    }
    var kwargs = {
        parent_key: parent_key,
        search_keys: search_keys,
        view: 'edit_item',
        element_names: element_names,
        input_prefix: '__NONE__',
        update_data: JSON.stringify(update_data),
        extra_data: JSON.stringify(extra_data),
        connect_key: connect_key
    }
   

    //add to the values here for gantt and inline elements
    web_data = JSON.stringify(web_data);
    
    var search_top = null;
    var table = spt.table.get_table();
    
    var search_dict = {};
    var view_panel = table.getParent('.spt_view_panel[table_id=' + table.id + ']' );
    if (view_panel) {
        search_top = view_panel.getElement('.spt_search');
        search_dict = spt.table.get_search_values(search_top);
       
    }
    
    try {
        var result = server.execute_cmd(class_name, kwargs, {'web_data': web_data});
        var info = result.info;
        if (info) {
            search_keys = info.search_keys;
            var rtn_search_keys = info.search_keys;
            if (do_refresh ) {
                var kw = {refresh_bottom : true, json: search_dict};
                spt.table.refresh_rows(rows, rtn_search_keys, web_data, kw);
            } 
        }

       
    } catch(e) {
        spt.error(spt.exception.handler(e));
    }
    spt.app_busy.hide();

    // fire an event
    if (search_keys) {
        var search_key = search_keys[0];
        var parts = server.split_search_key(search_key);
        var tmps = parts[0].split('?');
        var search_type = tmps[0];
        var event = "update|" + search_type;
        
        var input = {
            kwargs: kwargs,
            web_data: web_data
        }
        bvr.options = input;

        try {
            spt.named_events.fire_event(event, bvr);
        }
        catch(e) {
            spt.alert("Error firing event: " + event);
        }
    }
    // reset all the edits
    spt.table.last_cell = null;
    spt.table.last_data_wdg = null;
    spt.table.last_edit_wdg = null;
    

}

spt.table.get_search_values = function(search_top) {


    // get all of the search input values
    var new_values = [];
    if (search_top) {
        var search_containers = search_top.getElements('.spt_search_filter')
        for (var i = 0; i < search_containers.length; i++) {
            var values = spt.api.Utility.get_input_values(search_containers[i],null, false);
            new_values.push(values);
        }

        var ops = search_top.getElements(".spt_op");

        // special code for ops
        var results = [];
        var levels = [];
        var modes = [];
        var op_values = [];
        for (var i = 0; i < ops.length; i++) {
            var op = ops[i];
            var level = op.getAttribute("spt_level");
            level = parseInt(level);
            var op_value = op.getAttribute("spt_op");
            results.push( [level, op_value] );
            var op_mode = op.getAttribute("spt_mode");
            levels.push(level);
            op_values.push(op_value);
            modes.push(op_mode);

        }
        var values = {
            prefix: 'search_ops',
            levels: levels,
            ops: op_values,
            modes: modes
        };
        new_values.push(values);

        // find the table/simple search as well
        var panel = search_top.getParent(".spt_view_panel");
        var table_searches = panel.getElements(".spt_table_search");
        for (var i = 0; i < table_searches.length; i++) {
            var table_search = table_searches[i];
            var values = spt.api.Utility.get_input_values(table_search,null,false);
            new_values.push(values);
        }
    }





    // convert to json
    var json_values = JSON.stringify(new_values);
    return json_values;

}


spt.table.get_refresh_kwargs = function(row) {
    var element_names = spt.table.get_element_names();
    element_names = element_names.join(",");

    var layout = spt.table.get_layout();
    var view = layout.getAttribute("spt_view");
    search_type = layout.getAttribute("spt_search_type");

    var config_xml = layout.getAttribute("spt_config_xml");
    
    var table_top = layout.getParent('.spt_table_top');
    
    var show_select = table_top.getAttribute("spt_show_select");

    var group_elements = spt.table.get_table().getAttribute("spt_group_elements");
    group_elements = group_elements.split(",");

    var current_table = spt.table.get_table(); 
    // must pass the current table id so that the row bears the class with the table id
    // there is no need to pass in variables that affects the drawing of the shelf here.
    var kwargs = {
        temp: true,
        table_id : current_table.getAttribute('id'), 
        search_type: search_type,
        view: view,
        show_shelf: false,
        show_select: show_select,
        element_names: element_names,
        group_elements: group_elements,
        config_xml: config_xml
    }

    return kwargs
}





spt.table.refresh_rows = function(rows, search_keys, web_data, kw) {
    if (typeof(search_keys) == 'undefined' || search_keys == null) {
        search_keys = [];
        for (var i = 0; i < rows.length; i++) {
            var search_key = rows[i].getAttribute("spt_search_key");
            search_keys.push(search_key);
        }
    }
    else if (typeOf(search_keys) != 'array') {
        spt.alert('search_keys should be an array or null');
        return;
    }
    if (!kw) kw = {};
    // default to update bottom row color
    if (kw['refresh_bottom'] == null) kw.refresh_bottom = true;

    

    //var layout = spt.table.get_layout();
    // this is more reliable when multi table are drawn in the same page while
    // refresh is happening
    var layout_el = rows[0].getParent(".spt_layout");
    spt.table.set_layout(layout_el);

    var class_name = layout_el.getAttribute("spt_class_name");
    var element_names = spt.table.get_element_names();
    element_names = element_names.join(",");


    var view = layout_el.getAttribute("spt_view");
    var search_type = layout_el.getAttribute("spt_search_type");
    var config_xml = layout_el.getAttribute("spt_config_xml");
    var layout = layout_el.getAttribute("spt_layout");

    
    var table_top = layout_el.getParent('.spt_table_top');
    //note: sometimes table_top is null
    var show_select = table_top ? table_top.getAttribute("spt_show_select") : true;

    var server = TacticServerStub.get();

    var group_elements = spt.table.get_table().getAttribute("spt_group_elements");
    if (group_elements) {
        group_elements = group_elements.split(",");
    }
    else {
        group_elements = [];
    }

    if (!class_name) {
        class_name = 'tactic.ui.panel.TableLayoutWdg';
    }

    var current_table = spt.table.get_table(); 
    // must pass the current table id so that the row bears the class with the table id
    // there is no need to pass in variables that affects the drawing of the shelf here.
    var kwargs = {
        temp: true,
        icon_generate_refresh: kw.icon_generate_refresh,
        table_id : current_table.getAttribute('id'), 
        search_type: search_type,
        view: view,
        layout: layout,
        search_keys: search_keys,
        show_shelf: false,
        show_select: show_select,
        element_names: element_names,
        group_elements: group_elements,
        config_xml: config_xml
    }

    if (layout == "tile") {
        kwargs['bottom_expr'] = layout_el.getAttribute("spt_bottom_expr");
        kwargs['title_expr'] = layout_el.getAttribute("spt_title_expr");
    }





    // update all of the changed rows
    if (kw['cbjs_action']) {
        kwargs = {
          'args': kwargs,
          'cbjs_action': kw['cbjs_action']
        }
    }
    else {
        kwargs = {
          'args': kwargs,
          'cbjs_action': function(widget_html) {
            //spt.behavior.replace_inner_html(hidden_row, widget_html);
            //spt.app_busy.show("Replacing changed rows ...");

            var dummy = document.createElement("div");
            spt.behavior.replace_inner_html(dummy, widget_html);

            // transfer the widths to the new row
            var widths = spt.table.get_column_widths();
            for (var element_name in widths) {
                var width = widths[element_name];
                spt.table.set_column_width(element_name, width);
            }



            var new_rows = dummy.getElements(".spt_table_row");
            // the insert row is not included here any more
            for (var i = 0; i < new_rows.length; i++) {
                // remove the hidden row, if there is one
                if (!rows[i]) continue;
                    
                spt.table.remove_hidden_row( rows[i] );

                // replace the new row
                new_rows[i].inject( rows[i], "after" );

                // destroy the old row
                rows[i].destroy();

 
            }
            
            // for efficiency, we do not redraw the whole table to calculate the
            // bottom so just change the bg color
            if (kw['refresh_bottom']) {
                var bottom_row = spt.table.get_bottom_row(); 
                if (bottom_row) {
                    // This color doesn't really fit color palette
                    //bottom_row.setStyle('background', '#E6CB81');
                }
            }


            if (kw['on_complete']) {
                var on_complete = kw['on_complete'];
                on_complete();
            }
            
            spt.app_busy.hide();

            
          }
        }
    }
    kwargs.values = {};
    if (web_data && web_data != "[{}]")
        kwargs.values = {web_data: web_data};  

    if (kw.json)
        kwargs.values['json'] = kw.json;
    server.async_get_widget(class_name, kwargs);
}





// column functions
spt.table.add_column = function(element_name) {
    spt.table.modify_columns([element_name], 'add');
}

spt.table.add_columns = function(element_names) {
    spt.table.modify_columns(element_names, 'add');
}

spt.table.refresh_column = function(element_name, values) {
    spt.table.modify_columns([element_name], 'refresh', values);
}

// add new or refresh existing columns
spt.table.modify_columns = function(element_names, mode, values) {

    if (!['add','refresh'].contains(mode)) {
        spt.error('mode has to be add or refresh');
        return;
    }

    if (!values) values = {};


    var cur_element_names = spt.table.get_element_names();
    var column_exists = false;

    for ( var i = 0; i < element_names.length; i++) {
        for ( var j = 0; j < cur_element_names.length; j++) {
            if (element_names[i] == cur_element_names[j]) {
                if (mode == 'add') {
                    spt.alert("Column ["+element_names[i]+"] already in table");
                    return;
                }
                else if (mode =='refresh') {
                    column_exists = true;
                }
            }
        }
    }
    if (mode =='refresh' && ! column_exists) {
        spt.alert("Column ["+ element_names.join(',') +"] not found in table");
        return;
    }


    try {
    var search_keys = spt.table.get_all_search_keys();
    var rows = spt.table.get_all_rows();
    var header_row = spt.table.get_header_row();
    var group_rows = spt.table.get_group_rows(); 
    var bottom_row = spt.table.get_bottom_row();
    var col_indices = [];
    for (var k=0; k<element_names.length; k++) {
        col_indices.push(spt.table.get_column_index(element_names[k]));
    }


    var layout = spt.table.get_layout();
    var table = spt.table.get_table();
    var view = layout.getAttribute("spt_view");
    var search_type = layout.getAttribute("spt_search_type");


    var group_elements = spt.table.get_table().getAttribute("spt_group_elements");
    var current_table = spt.table.get_table(); 
    // must pass the current table id so that the row bears the class with the table id
    var class_name = 'tactic.ui.panel.table_layout_wdg.TableLayoutWdg';
    //if (group_elements)
    //    element_names.push(group_elements);
        
    var kwargs = {
        temp: true,
        table_id: current_table.getAttribute('id'),
        search_type: search_type,
        view: view,
        search_keys: search_keys,
        show_shelf: false,
        element_names: element_names,
        do_search: 'false',
        group_elements: group_elements,
        init_load_num : -1
    }

    
    var server = TacticServerStub.get();

    var kwargs = { 'args': kwargs };
    
    // pass the search json for group and order_by attributes
    var search_top = null;
    var view_panel = layout.getParent('.spt_view_panel');
    if (view_panel)
        search_top = view_panel.getElement('.spt_search');

    
    var search_dict = spt.table.get_search_values(search_top);
    if (!('json' in values)) {
        values['json'] = search_dict;
    }
    



    kwargs.values = values
    var widget_html = server.get_widget(class_name, kwargs);

   
    var data = document.createElement("div");
    spt.behavior.replace_inner_html(data, widget_html);

    // FIXME: might be just faster to refresh the whole page
    var data_rows = data.getElements(".spt_table_row");
    var data_header_row = data.getElement(".spt_table_header_row");
    var data_group_rows = data.getElements(".spt_group_row");
  
    var data_bottom_row = data.getElement(".spt_table_bottom_row");
    if (!data_header_row) {
        spt.error("There may have been an error:<br/>" + widget_html, {type: 'html'});
        return;
    }

    var header_table = spt.table.get_header_table();
    var header_row = header_table.getElement(".spt_table_header_row");

    // add the headers
    var cells = data_header_row.getElements(".spt_table_header");
    for (var j = 0; j < cells.length; j++) {

         if (mode=='add') {
             header_row.appendChild(cells[j]);
         }
         else if (mode=='refresh') {
             var idx = col_indices[j];
             var tgt_cell = header_row.getElements(".spt_table_header")[idx];
             cells[j].inject(tgt_cell, "after"); 
             tgt_cell.destroy();
         }
    }
    // add bottom row
    if (bottom_row && data_bottom_row) {
        rows.push(bottom_row);
        data_rows.push(data_bottom_row);
        // data_rows and rows could be off by 1 cuz either could optionally have a bottom wdg 
        if (rows.length != data_rows.length) {
            spt.alert('mismatch of data_rows and rows in the widget. Refresh may not be correct.');
        }
    }

    // FIXME: what about insert row?
    // FIXME: assumptions about order here???
    // TODO: taking into account the insert table [.spt_table_insert_row]
   

    for ( var i = 0; i < rows.length; i++ ) {
        var cells = data_rows[i].getElements(".spt_cell_edit");
        for (var j = 0; j < cells.length; j++) {

            if (mode=='add') {
                rows[i].appendChild(cells[j]);
            }
            else if (mode=='refresh') {
                var idx = col_indices[j]
                var tgt_cell = rows[i].getElements(".spt_cell_edit")[idx];
                cells[j].inject(tgt_cell, "after"); 
                tgt_cell.destroy();
            }
        }
    }

    for ( var i = 0; i < group_rows.length; i++ ) {
        var data_group_row = data_group_rows[i];
        if (!data_group_row) continue;

        var cells = data_group_rows[i].getElements('.spt_group_cell');
        for (var j = 0; j < cells.length; j++) {
            if (mode=='refresh') {
                var idx = col_indices[j] ;
                var tgt_cell = group_rows[i].getElements(".spt_group_cell")[idx];
                if (tgt_cell) {
                    
                    cells[j].inject(tgt_cell, "after"); 
                    tgt_cell.destroy();
                }
            }
        }
    }
    
    }
    catch(e) {
        spt.alert(spt.exception.handler(e));
        throw(e)
    }
    //set original table back
    spt.table.set_table(table);
    data.destroy();
}



spt.table.remove_columns = function(columns) {
    var table = spt.table.get_table();

    var insert_row = spt.table.get_insert_row();

    for (var i = 0; i < columns.length; i++) {
        var column = columns[i];
        var header = spt.table.get_header(column);
        var cells = spt.table.get_cells(column);

        var insert_cells = insert_row.getElements(".spt_cell_edit");
        for (var j = 0; j < insert_cells.length; j++) {
            if (insert_cells[j].getAttribute("spt_element_name") == columns[i]) {
                insert_cells[j].destroy();
            }
        }


        header.destroy();
        for (var j = 0; j < cells.length; j++) {
            cells[j].destroy();
        }
    }


}


spt.table.remove_column = function(column) {
    return spt.table.remove_columns([column]);
}

spt.table.toggle_collapse_column = function(element_name) {

    var index = -1;

    var headers = spt.table.get_headers();
    var header;
    for (var i = 0; i < headers.length; i++) {
        var h_element_name = headers[i].getAttribute("spt_element_name");
        if (h_element_name == element_name) {
            header = headers[i];
            index = i;
            break;
        }
    }

    if (index == -1) {
        spt.alert("Column ["+element_name+"] is not in this table");
        return;
    }


    var is_collapsed = header.is_collapsed;

    if (is_collapsed == true) {
        header.setStyle("width", "");
        header.is_collapsed = false;
        spt.behavior.replace_inner_html(header, header.xx);
        header.xx = null;
    }
    else {
        header.setStyle("width", "3px");
        header.is_collapsed = true;
        header.xx = header.innerHTML;
        header.innerHTML = '<div style="padding: 3px" title="'+element_name+'">+</div>';
    }




    // get all of the cells
    var rows = spt.table.get_all_rows();
    var btm_row = spt.table.get_bottom_row();
    rows.push(btm_row);

    for (var i = 0; i < rows.length; i++) {
        var tds = rows[i].getElements(".spt_cell_edit");
        td = tds[index];
        if (is_collapsed == true) {
            spt.behavior.replace_inner_html(td, td.xx);
            header.xx = null;
        }
        else {
            td.xx = td.innerHTML;
            td.innerHTML = '...';
        }
    }

    var table = spt.table.get_table();
    table.setStyle("width", "");

}



// Group methods
spt.table.collapse_group = function(group_row) {

    var show = false;

    if (group_row.getAttribute("spt_table_state") == 'closed') {
        group_row.setAttribute("spt_table_state", "open");
        show = true;
    }
    else {
        group_row.setAttribute("spt_table_state", "closed");
    }

    var swap_top = group_row.getElement(".spt_swap_top");
    if (swap_top) {
        var on = swap_top.getElement(".SPT_SWAP_ON");
        var off = swap_top.getElement(".SPT_SWAP_OFF");

        spt.show(off);
        spt.hide(on);
        swap_top.setAttribute("spt_state", "off");
    }


    // get the rows after the group
    var last_row = group_row;
    var idx = last_row.getAttribute('idx')
    var reg_row = false; 
    while(1) {
        var row = last_row.getNext();
        if (row == null) {
            break;
        }
        var break_cond =  idx == '0' ?  row.getAttribute('idx') == idx : row.getAttribute('idx') < idx ;
        var break_cond2 = row.getAttribute('idx') == idx
        if ((row.hasClass("spt_group_row") && break_cond)  || row.hasClass("spt_table_bottom_row")) {
            break;
        }
        if (reg_row && break_cond2)
            break;

        reg_row = true;

        if (show)
            spt.show(row)
        else 
            spt.hide(row)
        

        last_row = row;
    }

    // FIXME: is this even needed
    group_row.setAttribute("is_collapse", "true");

}

spt.table.collapse_all_groups = function() {
    var table = spt.table.get_table();
    var group_rows = table.getElements(".spt_group_row");
    for ( var i = 0; i < group_rows.length; i++ ) {
        spt.table.collapse_group(group_rows[i]);
    }
}



spt.table.get_group_states = function() {
    var table = spt.table.get_table();

    var states = [];

    var group_rows = table.getElements(".spt_group_row");
    for ( var i = 0; i < group_rows.length; i++ ) {
        var state = group_rows[i].getAttribute("spt_table_state");
        var group_name = group_rows[i].getAttribute("spt_group_name");
        states.push( [group_name, state] );
    }

    return states;
}




// setting width of columns

spt.table.set_column_width = function(element_name, width) {
    var table = spt.table.get_table();
    var header_table = spt.table.get_header_table();

    var row = spt.table.get_first_row();
    var cell = spt.table.get_cell(element_name, row);
    if (!cell) {
        //alert("Cell for ["+element_name+"] does not exist");
        return;
    }


    // handle group
    var row = table.getElement(".spt_table_hidden_group_row");
    if (row) {
        var els = row.getElements(".spt_table_hidden_group_td");
        for (var i = 0; i < els.length; i++) {
            if (element_name == els[i].getAttribute("spt_element_name")) {
                els[i].setStyle("width", width);
                continue;
            }
            
        }
    }


    var headers = spt.table.get_headers();
    var cells = [];
    if (row)
        cells = row.getElements(".spt_cell_edit");
    var total_width = 0;
    
    // add up total_width
    // Commented out: not necessary for basic table structure
    for (var i = 0; i < headers.length; i++) {
        var header = headers[i];
        if (header.getAttribute("spt_element_name") == element_name) {
            var new_width = width + "";
            new_width = parseInt( new_width.replace("px", "") );
            total_width += new_width;
        }
        else {
            var size = header.getSize();
            total_width += size.x;
            new_width = size.x;
        }


        //header.setStyle("width", new_width);
        //if (row)
        //    cells[i].setStyle("width", new_width);
        /*
        if (new_width) {
            header.setStyle("width", new_width);
            if (row && cells.length != 0) {
                cells[i].setStyle("width", new_width);
            }
        }
        */
    }

    var curr_header = spt.table.get_header_by_cell(cell);
    if (total_width) {
        table.setStyle("width", total_width);
        header_table.setStyle("width", total_width);

        var layout = spt.table.get_layout();
        if (layout.getAttribute("has_extra_header") == "true") {
            layout_width = total_width+66;
        }
        else {
            layout_width = total_width+30;
        }
        if (layout_width < 750) layout_width = 700;

        layout.setStyle("width", layout_width);
    }

    curr_header.setStyle("width", width);
    cell.setStyle("width", width);


    var insert_cell = spt.table.get_insert_row_cell(element_name); 
    if (insert_cell)
        insert_cell.setStyle("width", width);
   
}



spt.table.get_column_widths = function() {
    var headers = spt.table.get_headers();

    var widths = {};

    for (var i = 0; i < headers.length; i++) {
        var header = headers[i];
        var element_name = header.getAttribute("spt_element_name")
        var size = header.getSize();
        var width = header.getStyle("width");
        widths[element_name] = parseInt( width.replace("px", "") );
    }

    return widths;
}



spt.table.expand_table = function() {
    var layout = spt.table.get_layout();
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
        table.setStyle("width", "");
        if (header_table)
            header_table.setStyle("width", "");
    }
    else {
        table.setStyle("width", "100%");
        if (header_table)
            header_table.setStyle("width", "100%");
        layout.setStyle("width", "100%");
    }
 
}





// Drag and drop behaviors
spt.table.drag_init = function()
{
    spt.table.last_header = null;
    spt.table.last_header_inner = null;
    spt.table.last_size = null;
    spt.table.last_table_size = null;
    spt.table.last_mouse_pos = null;
    spt.table.smallest_size = -1;
    spt.table.resize_div = null;
}
spt.table.drag_init();


spt.table.drag_resize_header_setup = function(evt, bvr, mouse_411)
{
    var src_el = spt.behavior.get_bvr_src( bvr );

    var layout = src_el.getParent(".spt_layout");
    spt.table.set_layout(layout)


    var header = src_el.getParent(".spt_table_header");

    var header_inner = src_el.getParent(".spt_table_header_inner");


    //var table = src_el.getParent(".spt_table_table");
    var header_table = spt.table.get_header_table();
    var table = spt.table.get_table();

    spt.table.last_table = table;
    spt.table.last_table_size = table.getSize();
    spt.table.last_header = header;
    spt.table.last_header_inner = header_inner;
    spt.table.last_size = header.getSize();
    spt.table.last_mouse_pos = {x: mouse_411.curr_x, y: mouse_411.curr_y};



    return;


    /*
    spt.table.smallest_size = -1;

    // set all of the header sizes
    var headers = spt.table.get_headers();
    var sizes = [];
    for (var i = 0; i < headers.length; i++ ) {
        var size = headers[i].getSize();
        sizes.push(size);
    }

    // zero out the table
    for (var i = 0; i < headers.length; i++ ) {
        headers[i].setStyle("width", "0px");
    }
    spt.table.last_table.setStyle("width", "0px");

    
    for (var i = 0; i < headers.length; i++ ) {
        headers[i].setStyle("width", sizes[i].x);
    }


    // handle the elements that scale with the table header
    spt.table.resize_div = []
    if (!header.hasClass("spt_table_scale") ) {
        return;
    }

    spt.table.resize_div.push( header.getElement(".spt_table_scale") );

    var element_name = spt.table.get_element_name_by_header(header);
    var column_cells = spt.table.get_cells(element_name);
    for ( var i = 0; i < column_cells.length; i++) {
        var el = column_cells[i].getElement(".spt_table_scale");
        if (el == null) { continue; }
        spt.table.resize_div.push( el );
    }
    */


}

spt.table.drag_resize_header_motion = function(evt, bvr, mouse_411)
{
    // hard coded offset representing the width of the resizable div
    var offset = 3;

    var dx = mouse_411.curr_x - spt.table.last_mouse_pos.x;
    var x = spt.table.last_size.x + dx;

    var element_name = spt.table.last_header.getAttribute("spt_element_name");
    spt.table.set_column_width(element_name, x);


    return;




    /* This is not needed any more
    if ( x < spt.table.smallest_size ) {
        spt.table.last_header_inner.setStyle("width", spt.table.smallest_size-offset);
    }
    else {
        spt.table.last_header_inner.setStyle("width", x-offset);
    }
    */
    spt.table.last_header_inner.setStyle("width", x-offset);

    var width = x;
    spt.table.last_header.setStyle("width", width);
    spt.table.last_header.setStyle("min-width", width);
    //spt.table.last_table.setStyle("width", spt.table.last_table_size.x + dx);
    //spt.table.last_table.setStyle("width", "0px");

    // get the size and force set it
    var size = spt.table.last_header.getSize();
    var size_inner = spt.table.last_header_inner.getSize();

    // disable this for Webkit ... it locks the table up.
    // ... however, this allows the resize to get too small
    if (!spt.browser.is_Webkit_based()) {
        if ( size_inner.x + offset < size.x) {
            spt.table.smallest_size = size.x;
        }
    }

    // scale any widgets that scale with table header
    var resize_div = spt.table.resize_div;
    for (var i=0; i < resize_div.length; i++ ) {
        resize_div[i].setStyle('width', width );
    }


}

spt.table.drag_resize_header_action = function(evt, bvr, mouse_411) {
    spt.table.smallest_size = -1;
    spt.table.resize_div = null;

    spt.table.drag_init();
}



spt.table.clone = null;
spt.table.pos = null;
spt.table.resize_handles = null;
spt.table.resize_positions = null;
spt.table.drop_index = -1;
spt.table.resize_layout = null;

spt.table.drag_reorder_header_setup = function(evt, bvr, mouse_411)
{
    var src_el = spt.behavior.get_bvr_src( bvr );
    var layout = src_el.getParent(".spt_layout");
    spt.table.set_layout(layout);
    spt.table.resize_layout = layout;

    var table = src_el.getParent(".spt_table_table");

    var cell = src_el.getParent(".spt_table_header");
    var size = cell.getSize();


    var layout_pos = layout.getPosition(document.body);


    spt.table.last_table = table;
    spt.table.pos = layout_pos;

    // create a clone
    var clone = spt.behavior.clone(bvr.src_el);
    spt.table.clone = clone;

    clone.inject(layout)

    clone.setStyle("position", "absolute");
    clone.setStyle("left", mouse_411.curr_x-layout_pos.x+5);
    clone.setStyle("top", mouse_411.curr_y-layout_pos.y+5);
    clone.setStyle("width", size.x);
    clone.setStyle("max-width", "200px");
    clone.setStyle("min-height", "30px");
    //clone.setStyle("height", size.y);
    clone.setStyle("background", "yellow");
    clone.setStyle("border", "solid 1px black");
    clone.setStyle("opacity", "0.5");


    // get the element name
    var header = bvr.src_el.getParent(".spt_table_header");
    var element_name = header.getAttribute("spt_element_name");
    clone.setAttribute("spt_element_name", element_name);

    spt.table.resize_handles = [];
    var headers = spt.table.get_headers();
    for (var i = 0; i < headers.length; i++) {
        var resize_handle = headers[i].getElement(".spt_resize_handle");
        spt.table.resize_handles.push(resize_handle);
        var pos = resize_handle.getPosition();
    }

}

spt.table.drag_reorder_header_motion = function(evt, bvr, mouse_411)
{
    var layout = spt.table.resize_layout;

    var layout_pos = spt.table.pos;
    var clone = spt.table.clone;

    var clone_pos = {
        x: mouse_411.curr_x - layout_pos.x,
        y: mouse_411.curr_y - layout_pos.y
    }

    clone.setStyle("left", clone_pos.x+5);
    clone.setStyle("top", clone_pos.y+5);

    // find out which resize handle is the closes
    var smallest_dd = -1;
    var index = -1;
    for (var i = 0; i < spt.table.resize_handles.length; i++) {
        var pos = spt.table.resize_handles[i].getPosition(layout);
        var dd = (pos.x-clone_pos.x)*(pos.x-clone_pos.x) + (pos.y-clone_pos.y)*(pos.y-clone_pos.y);
        if (smallest_dd == -1 || dd < smallest_dd) {
            smallest_dd = dd;
            index = i;
        }
    }

    for (var i = 0; i < spt.table.resize_handles.length; i++) {
        var handle = spt.table.resize_handles[i];
        if (i == index) {
            handle.setStyle("background-color", "#F00");
        }
        else {
            handle.setStyle("background-color", "");
        }
    }

    spt.table.drop_index = index;
}

spt.table.drag_reorder_header_action = function(evt, bvr, mouse_411)
{
    var clone = spt.table.clone;
    var element_name = clone.getAttribute("spt_element_name");
    clone.destroy();

    var drop_on_el = spt.get_event_target(evt);
    if( ! spt.behavior.drop_accepted( bvr, drop_on_el ) ) {
        //spt.alert("Must drop on another column to reorder");
        return;
    }

    var src_index = spt.table.get_column_index(element_name);
    var drop_index = spt.table.drop_index;
    if (src_index == drop_index || drop_index == -1) {
        return;
    }

    // reorder the header
    var headers = spt.table.get_headers();
    headers[src_index].inject(headers[drop_index], "after");

    // It's possible that layout gets reset somewhere during the drag
    var src_el = spt.behavior.get_bvr_src( bvr );
    var layout = src_el.getParent(".spt_layout");
    spt.table.set_layout(layout);


    // reorder the cells
    var rows = spt.table.get_all_rows();
    var bot_row = spt.table.get_bottom_row();
    if (bot_row)
        rows = rows.concat(bot_row);
    for (var i = 0; i < rows.length; i++) {
        var row = rows[i];
        var cells = row.getElements(".spt_cell_edit");
        var src_cell = cells[src_index];
        var drop_cell = cells[drop_index];

        src_cell.inject(drop_cell, "after");
    }

    for (var i = 0; i < spt.table.resize_handles.length; i++) {
        var handle = spt.table.resize_handles[i];
        handle.setStyle("background-color", "");
    }

    spt.table.drag_init();
}



spt.table.get_edit_menu = function(src_el) {
     var menu = src_el.getParent('.spt_menu_top');
     return menu;
}

// Callbacks

spt.table.row_ctx_menu_setup_cbk = function( menu_el, activator_el ) {

    var commit_enabled = true;
    var row_is_retired = false;
    var row_is_subscribed = false;
    var display_label = "not found";

    
    if (spt.has_class(activator_el, 'spt_table_row'))
        tr = activator_el;
    else
        tr = activator_el.getParent('tr');
    if (tr) {
        row_is_retired = tr.getAttribute('spt_widget_is_retired') == 'true';
        display_label = tr.get("spt_display_value");
        if( ! display_label ) {
            log.warning( "WARNING: [spt.table.row_ctx_menu_setup_cbk] could not find 'spt_display_value' for item. " +
                            "Use 'search_key' as display_label." );
            display_label = tr.get("spt_search_key");
        }
        row_is_subscribed = tr.getAttribute('spt_is_subscribed');
    }
   

    var setup_info = {
        'commit_enabled' : commit_enabled,
        'is_retired': row_is_retired,
        'is_not_retired': (! row_is_retired),
        'display_label': display_label,
        'is_subscribed': row_is_subscribed,
        'is_not_subscribed': (! row_is_subscribed)
    }
    return setup_info;
}


//
// Data-row Context Menu: EDIT row sobject
//
spt.table.row_ctx_menu_edit_cbk = function(evt, bvr)
{
    var activator = spt.smenu.get_activator(bvr);
    var row = activator;
    var search_key = row.getAttribute("spt_search_key");
    var search_key_info = spt.dg_table.parse_search_key( search_key );
    var edit_view = bvr.edit_view ? bvr.edit_view : 'edit';
    
    var tmp_bvr = {};
    tmp_bvr.args = {
        //'search_type': search_key_info.search_type,
        //'search_id': search_key_info.id,
        'search_key': search_key,
        'input_prefix': 'edit',
        'view': edit_view
    };

    tmp_bvr.options = {
        'title': 'Edit: ' + search_key_info.search_type,
        'class_name': 'tactic.ui.panel.EditWdg',
        'popup_id': 'edit_popup'
    };

    spt.popup.get_widget( evt, tmp_bvr );
}
//
// Data-row Context Menu: COMMIT all table changes
//
// Method to dyanmically update a row by gathering all of the stored values
// and doing an update
//
spt.table.row_ctx_menu_save_changes_cbk = function(evt, bvr)
{
    var activator = spt.smenu.get_activator(bvr);
    var row = activator;

    spt.table.set_table(activator);
    spt.table.save_changes();

}



spt.table.delete_row = function(row) {
    var rows = [row];
    return spt.table.delete_rows(rows);
}

spt.table.delete_rows = function(rows) {

    var row = rows[0];
    var layout = spt.table.get_layout();

    var search_key = row.get("spt_search_key");
    var search_key_info = spt.dg_table.parse_search_key( search_key );
    var search_type = search_key_info.search_type;


    var search_keys = [];
    for (var i = 0; i < rows.length; i++) {
        var tmp_row = rows[i];
        var search_key = tmp_row.get("spt_search_key");
        search_keys.push(search_key);
    }


    // open delete popup
    var class_name;
    if (search_type == "sthpw/search_type") { 
        class_name = 'tactic.ui.tools.DeleteSearchTypeToolWdg';
    }
    else if (search_type == "sthpw/project") { 
        class_name = 'tactic.ui.tools.DeleteProjectToolWdg';
    }
    else {
        class_name = 'tactic.ui.tools.DeleteToolWdg';
    }
    var kwargs = {
      search_keys: search_keys,
    }
    var popup = spt.panel.load_popup("Delete Item", class_name, kwargs);

    var on_post_delete = function() {
        var on_complete = function(id) {
            spt.behavior.destroy_element($(id));
        }
        for (var i = 0; i < rows.length; i++) {
            var row = rows[i];
            row.addClass("spt_removed");
            if (layout.getAttribute("spt_version") == "2") {
                spt.table.remove_hidden_row(row);
            }
            Effects.fade_out(row, 500, on_complete);
        }
    }

    popup.spt_on_post_delete = on_post_delete;

    return;
}


spt.table.remove_rows = function(rows) {
    var layout = spt.table.get_layout();
    var on_complete = function(id) {
        spt.behavior.destroy_element($(id));
    }
    for (var i = 0; i < rows.length; i++) {
        var row = rows[i];
        row.addClass("spt_removed");
        if (layout.getAttribute("spt_version") == "2") {
            spt.table.remove_hidden_row(row);
        }
        Effects.fade_out(row, 500, on_complete);
    }

}


spt.table.remove_selected = function() {
    var rows = spt.table.get_selected_rows();
    spt.table.remove_rows(rows);
}



spt.table.delete_selected = function()
{
    var selected_rows = spt.table.get_selected_rows();
    var num = selected_rows.length;
    if (num == 0) {
        spt.alert("Nothing selected to delete.");
        return;
    }

    spt.table.delete_rows(selected_rows);

    return;

}

spt.table.retire_selected = function()
{
    spt.table.operate_selected('retire');
}

spt.table.operate_selected = function(action)
{
    var selected_rows = spt.table.get_selected_rows();

    var num = selected_rows.length;
    if (num == 0) {
        spt.alert("Nothing selected to " + action);
        return;
    }

    var show_retired = action == 'retire' ? spt.dg_table.get_show_retired_flag( selected_rows[0] ) : false;
    var search_key_info = spt.dg_table.parse_search_key( selected_rows[0].getAttribute("spt_search_key") );

    var title = action.capitalize() + ' Selected Items';
    var msg = 'Retiring ' + num + '  "' + search_key_info.search_type + '" items ...';


    var msg = "Are you sure you wish to " + action + " [" + num + "] items?";

    var cancel = function() { };
      
    var ok =  function() {
        //spt.app_busy.show( title, msg );
        var aborted = false;
        var server = TacticServerStub.get();
        server.start({title: action + " ["+num+"] items"});
        var is_project = false;

        try {
            for (var i=0; i < selected_rows.length; i++)
            {
        
                var search_key = selected_rows[i].getAttribute("spt_search_key");
                if (search_key.test('sthpw/project?'))
                    is_project = true;

                if (action == 'retire')
                    server.retire_sobject(search_key);
                else if (action == 'delete')
                    server.delete_sobject(search_key);
            }
        }
        catch(e) {
            // TODO: do nicer error message for user
            spt.alert("Error: " + spt.exception.handler(e));
            server.abort();
            aborted = true;
        }

        server.finish()

        if( ! aborted ) {
            if( show_retired ) {
                spt.table.refresh_rows(selected_rows);
            }
            else {
                for (var i=0; i < selected_rows.length; i++)
                {
                    var row = selected_rows[i];
                    on_complete = "spt.behavior.destroy_element($(id))"
                    spt.dom.load_js(["effects.js"], function() {
                        Effects.fade_out(row, 300, on_complete);
                    } );
                }

            }
            if (is_project)
                setTimeout("spt.panel.refresh('ProjectSelectWdg');", 2000);
        }

        //spt.app_busy.hide();
    }
    spt.confirm(msg, ok, cancel);
}


// Tools


spt.table.open_ingest_tool = function(search_type) {
    var class_name = 'tactic.ui.tools.IngestUploadWdg';
    var kwargs = {
        search_type: search_type
    };
    spt.panel.load_popup("Ingest "+search_type, class_name, kwargs);
}





            '''

        if my.kwargs.get('temp') != True:
            cbjs_action = '''
            // set the current table on load
            // just load it once and set the table if loaded already
            if (spt.table) {
                var top = bvr.src_el.getParent(".spt_layout");
                spt.table.set_layout(top);
                return;
            }

            spt.Environment.get().add_library("spt_table");


            spt.table = {};
            spt.table.last_table = null;
            spt.table.layout = null;
            spt.table.element_names = null;

            spt.table.select_color = bvr.select_color;
            spt.table.shadow_color = bvr.shadow_color;
            %s
            spt.table.set_table(bvr.src_el);
            
            ''' %cbjs_action


        hidden_row_color = table.get_color("background3")

        table.add_behavior( {
            'type': 'load',
            'cbjs_action': my.get_onload_js()
        } )


        table.add_behavior( {
            'type': 'load',
            'hidden_row_color': hidden_row_color,
            'select_color': select_color,
            'shadow_color': shadow_color,
            'cbjs_action' : cbjs_action
        } )


    #
    # TEST TEST TEST TEST TEST
    #

    def test_relationship(my):
        search = Search("ut/asset")
        search.add_id_filter(357)
        sobject = search.get_sobject()

        related = sobject.get_related_sobjects("ut/asset")
        for sobject in related:
            print "related: ", sobject.get_value("name")


        return


        # TODO:
        # try: many to many
        search = Search("ut/asset")
        sobjects = search.get_sobjects()
        related = Search.get_related_by_sobjects(sobjects, "ut/asset")
        for key, sobjects in related.items():
            print "relatedx: ", key, sobjects



    def handle_sub_search(my):

        my.test_relationship()

        my.sobject_levels = []

        # main data structure
        levels_sobjects = []

        #search = Search("ut/asset")
        #search.add_id_filter(357)
        #my.sobjects = search.get_sobjects()

        current_sobjects = my.sobjects

        steps = ['ut/asset_in_asset', 'ut/asset']
        paths = ['', 'sub']

        for i in range(0,10):

            done = False

            for related_type, path in zip(steps, paths):

                # this gets all the collated related sobjects
                # FIXME: why do we need order by code desc?
                level_sobjects_dict = Search.get_related_by_sobjects(current_sobjects, related_type, path=path, filters=[['@ORDER_BY','code desc']])
                levels_sobjects.append(level_sobjects_dict)

                if not level_sobjects_dict:
                    done = True
                    break;


                current_sobjects = []
                for name, items in level_sobjects_dict.items():
                    current_sobjects.extend(items)

            if done:
                break


        sobject_list = []

        # go through each top level sobject and find the children
        level = 0
        for sobject in my.sobjects:
            sobject_list.append(sobject)
            my.sobject_levels.append(level)

            my._collate_levels(sobject, sobject_list, levels_sobjects, level)

        my.sobjects = sobject_list




    def _collate_levels(my, sobject, sobject_list, levels_sobjects, level):

        # put an arbitrary max for now
        if level > 10:
            return

        search_key = sobject.get_search_key()

        # find the children
        level_sobjects_dict = levels_sobjects[level]

        related_sobjects = level_sobjects_dict.get(search_key)
        if not related_sobjects:
            return
        
        # go through each related
        for related_sobject in related_sobjects:
            if related_sobject.get_base_search_type() != 'ut/asset_in_asset':
                sobject_list.append(related_sobject)
                my.sobject_levels.append(level)
           
            my._collate_levels(related_sobject, sobject_list, levels_sobjects, level+1)



    """
    def handle_sub_search2(my):

        # level 1 search
        #level1_sobjects_dict = Search.get_related_by_sobjects(my.sobjects, "sthpw/snapshot")
        level1_sobjects_dict = Search.get_related_by_sobjects(my.sobjects, "ut/asset_in_asset")

        tt = []
        for name, items in level1_sobjects_dict.items():
            tt.extend(items)

        # level 2 search
        level2_sobjects_dict = Search.get_related_by_sobjects(tt, "ut/asset", path='sub')

        tt = []
        for name, items in level2_sobjects_dict.items():
            tt.extend(items)

        # level 3 search
        level3_sobjects_dict = Search.get_related_by_sobjects(tt, "ut/asset_in_asset")

        tt = []
        for name, items in level3_sobjects_dict.items():
            tt.extend(items)

        level4_sobjects_dict = Search.get_related_by_sobjects(tt, "ut/asset", path='sub')




        new_sobjects = []
        my.sobject_levels = []

        relationship = 'code'

        for sobject in my.sobjects:
            new_sobjects.append(sobject)
            my.sobject_levels.append(0)

            if relationship == 'code':
                search_key = sobject.get_code()

            else:
                search_key = "%s&id=%s" % (sobject.get_search_type(), sobject.get_id())
            level1_sobjects = level1_sobjects_dict.get(search_key )
            if level1_sobjects:
                for i, level1_sobject in enumerate(level1_sobjects):
                    #new_sobjects.append(level1_sobject)
                    #my.sobject_levels.append(1)

                    if relationship == 'code':
                        #search_key = level1_sobject.get_code()
                        search_key = level1_sobject.get_value("b_asset_code")
                    else:
                        search_key = "%s&id=%s" % (level1_sobject.get_search_type(), level1_sobject.get_id())

                    level2_sobjects = level2_sobjects_dict.get(search_key)
                    if level2_sobjects:
                        for i, level2_sobject in enumerate(level2_sobjects):
                            new_sobjects.append(level2_sobject)
                            my.sobject_levels.append(1)


                            search_key = level2_sobject.get_value("code")
                            level3_sobjects = level3_sobjects_dict.get(search_key )
                            if level3_sobjects:
                                for i, level3_sobject in enumerate(level3_sobjects):
                                    #new_sobjects.append(level3_sobject)
                                    #my.sobject_levels.append(1)

                                    if relationship == 'code':
                                        #search_key = level3_sobject.get_code()
                                        search_key = level3_sobject.get_value("b_asset_code")
                                    else:
                                        search_key = "%s&id=%s" % (level3_sobject.get_search_type(), level3_sobject.get_id())

                                    level4_sobjects = level4_sobjects_dict.get(search_key)
                                    if level4_sobjects:
                                        for i, level4_sobject in enumerate(level4_sobjects):
                                            new_sobjects.append(level4_sobject)
                                            my.sobject_levels.append(2)


        my.sobjects = new_sobjects
        my.items_found = len(my.sobjects)
        """


class TableLayoutWdg(FastTableLayoutWdg):
    pass


class TableGroupManageWdg(BaseRefreshWdg):

    def get_args_keys(my):
        return {
            "element_names": "list of the element_names",
            "search_type": "search_type to list all the possible columns",
            "target_id": "the id of the panel where the table is"
        }

    def init(my):
        my.group_columns = my.kwargs.get('group_by')
        my.group_columns = my.group_columns.split(',')
    
    def get_columns_wdg(my, title, element_names, is_open=False):

        widget_idx = 3
        content_wdg = DivWdg()
        content_wdg.add_class("spt_columns")
        content_wdg.add_style("margin: 15px 0 15px 0")
        content_wdg.add_style("font-size: 0.85em")
        #content_wdg.add_style("position: relative")
        
        web = WebContainer.get_web()

        elements_wdg = FloatDivWdg()
        elements_wdg.add_attr('title', 'Click to add to Group Columns')
        elements_wdg.add_styles('height: 400px; max-width: 250px; overflow: auto')
        elements_wdg.add_relay_behavior( { 'type': 'mouseup', 
                                'bvr_match_class': 'spt_column',
                               "cbjs_action": '''var el = bvr.src_el;
                                                                    
                                           var top = el.getParent('.spt_group_col_top')
                                           var target = top.getElement('.spt_group_col');
                                           var cur_items = target.getElements('.spt_column');
                                           var group_names = [];
                                           for (var k=0; k < cur_items.length; k++) {
                                                group_names.push(cur_items[k].getAttribute('element'));
                                           }
                                           if (group_names.contains(el.getAttribute('element'))) {
                                                spt.info(el.getAttribute('element') + ' is already added.');
                                                
                                           }
                                           else if (cur_items.length >= 4) {
                                                spt.alert('A maximum of 4 column names is allowed.')
                                           }
                                           else {
                                               var clone = el.clone();
                                               clone.setStyle('margin-bottom','6px');
                                               spt.remove_class(clone, 'hand');
                                               var del = clone.getElement('.spt_del');
                                               spt.show(del);
                                               clone.inject(target);
                                           }'''
                               } ) 
      
        
        elements_wdg.add_class("spt_columns_list")
        content_wdg.add(elements_wdg)
        if not is_open:
            elements_wdg.add_style("display: none")




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
        
        grouped_elements = []

        for element_name in element_names:
            menu_item = DivWdg(css='hand')
            menu_item.add_class("spt_column")
            menu_item.add_style("position: relative")
            menu_item.add_attr('element', element_name)

            del_div = DivWdg('x', css='spt_del hand')
            del_div.add_styles('position: absolute; right: 0px; display: none; font-weight: 800')
            del_div.add_attr('title','remove')
            menu_item.add(del_div)
            
            if element_name in my.group_columns:
                grouped_elements.insert(my.group_columns.index(element_name), menu_item )

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
            


            menu_item.add("&nbsp;&nbsp;&nbsp;")
            #menu_item.add_attr("title", full_title)
            menu_item.add(display_title)
         

            # mouse over colors
            color = content_wdg.get_color("background", -15)
            menu_item.add_event("onmouseover", "this.style.background='%s'" % color)
            menu_item.add_event("onmouseout", "this.style.background=''")

            elements_wdg.add(menu_item)

        group_drop = FloatDivWdg()
        color = group_drop.get_color('color2')
        group_drop.add_border(color=color)
        group_title = DivWdg('Group Columns')
        group_title.add_style('font-size: 14px')
        group_title.add_style('margin-bottom', '10px')
        group_drop.add(group_title)

        group_drop.add_relay_behavior( { 'type': 'mouseup', 
                                'bvr_match_class': 'spt_del',
                               "cbjs_action": '''var el = bvr.src_el.getParent('.spt_column');
                                        spt.behavior.destroy_element(el);'''
                               } ) 
        group_drop.add_behavior( { 'type': 'load', 
                               "cbjs_action": '''var del_els = bvr.src_el.getElements('.spt_del');
                                                for (var k =0; k < del_els.length; k++)
                                                    spt.show(del_els[k]);

                                       '''
                               } ) 
        
        group_drop.add_color('background', 'background2', -7)
        group_drop.add_styles('min-width: 250px; height: 180px; padding: 12px; margin-left: 30px')
        group_drop.add_class('spt_group_col')

        #grouped_elements.reverse()
        clone_elements = copy.deepcopy(grouped_elements)
        if clone_elements:
            for clone_elem in clone_elements:
                clone_elem.remove_class('hand')
                clone_elem.add_style('margin-bottom: 6px')
                group_drop.add(clone_elem)




        save = ActionButtonWdg(title='OK', tip='Search with these Group columns')

        save.add_styles("position: absolute; left: 420; top: 425")
        
        save.add_behavior({ 'type': 'click_up',
            'cbjs_action': '''var el = spt.table.get_layout().getElement(".spt_search_group");
                              var top = bvr.src_el.getParent('.spt_group_col_top')
                              var target = top.getElement('.spt_group_col');
                              var cur_items = target.getElements('.spt_column');
                              var group_names = [];
                              for (var k=0; k < cur_items.length; k++) {
                                    group_names.push(cur_items[k].getAttribute('element'));
                              }
                              el.value = group_names;
                              var popup  =spt.popup.get_popup( bvr.src_el )
                              spt.popup.destroy(popup);
                              spt.table.run_search();
                              
                    '''})
        
        
        content_wdg.add(save)

        content_wdg.add(group_drop)




        return content_wdg


  

    def get_display(my):
        top = my.top
        top.add_style("width: 580px")

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
        context_menu.add_class("spt_group_col_top")

        context_menu.add_style("padding: 0px 10px 10px 10px")
        #context_menu.add_border()
        context_menu.add_color("color", "color")
        context_menu.add_style("height: 450px")
        context_menu.add_style("overflow-y: auto")
        context_menu.add_style("overflow-x: hidden")



       


        my.config = WidgetConfigView.get_by_search_type(search_type, "definition")

   



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

      
        defined_element_names.sort()
        title = 'Columns'
        context_menu.add( my.get_columns_wdg(title, defined_element_names, is_open=True) )



       
        return top
