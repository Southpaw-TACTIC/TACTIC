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
from pyasm.security import Sudo

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.container import SmartMenu

from pyasm.biz import Project, ExpressionParser, Subscription
from tactic.ui.table import ExpressionElementWdg, PythonElementWdg
from tactic.ui.common import BaseConfigWdg
from tactic.ui.widget import ActionButtonWdg

from pyasm.biz import ProjectSetting

from .base_table_layout_wdg import BaseTableLayoutWdg

import six
basestring = six.string_types


class TableLayoutWdg(BaseTableLayoutWdg):
    SCROLLBAR_WIDTH = 8 

    #CATEGORY_KEYS = {
    #    '_order': ['Required', 'Misc']
    #}


    ARGS_KEYS = {
        "mode": {
            'description': "Determines whether to draw with widgets or just use the raw data",
            'type': 'SelectWdg',
            'values': 'widget|raw',
            'order': '00',
            'category': 'Misc'
        },

        "search_type": {
            'description': "search type that this panels works with",
            'type': 'TextWdg',
            'order': '01',
            'category': 'Required'
        },
        "view": {
            'description': "view to be displayed",
            'type': 'TextWdg',
            'order': '02',
            'category': 'Required',
            'default': 'table',
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
            'order': '00',
            'category': 'Optional'
        },
        "show_shelf": {
            'description': "Determines whether or not to show the action shelf",
            'type': 'SelectWdg',
            'values': 'true|false',
            'order': '01',
            'category': 'Optional'
        },
        "show_header": {
            'description': "Determines whether or not to show the table header",
            'type': 'SelectWdg',
            'values': 'true|false',
            'order': '02',
            'category': 'Optional'
        },
        "show_select": {
            'description': "Determine whether to show the selection checkbox for each row",
            'type': 'SelectWdg',
            'values': 'true|false',
            'order': '03',
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
        'show_search': {
            'description': 'Flag to determine whether or not to show the advanced Search button',
            'category': 'Optional',
            'type': 'SelectWdg',
            'values': 'true|false',
            'order': '18'
        },
        'advanced_search': {
            'description': '(DEPRECATED) Use show_search instead',
            'category': 'Optional',
            'type': 'SelectWdg',
            'values': 'true|false',
            'order': '18'
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
            'category': 'Display',
            #'default': 'true',
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
            'category': 'Optional',
            'order': '16'
        },

        "show_help": {
            'description': 'Determine whether or not to display the help button in shelf',
            'category': 'Optional',
            'type': 'SelectWdg',
            'values': 'true|false',
            'order': '17'
        }


    }

    GROUP_COLUMN_PREFIX = "__group_column__"



    def get_kwargs_keys(cls):
        return ['select_color', 'js_load', "extra_columns"]
    get_kwargs_keys = classmethod(get_kwargs_keys)




    def has_config(self):
        return True




    def get_layout_version(self):
        return "2"


    def remap_display_handler(self, display_handler):
        if display_handler == "HiddenRowToggleWdg":
            return "tactic.ui.table.HiddenRowElementWdg"
        elif display_handler == "pyasm.widget.HiddenRowToggleWdg":
            return "tactic.ui.table.HiddenRowElementWdg"

    def remap_sobjects(self):
        # find all the distinct search types in the sobjects
        if not self.search_type.startswith("sthpw/sobject_list"):
            return

        # don't remap if it's the default table view when the user is
        # viewing raw data
        if self.view == 'table':
            return

        search_types_dict = {}
        for row, sobject in enumerate(self.sobjects):

            if sobject.is_insert():
                continue

            # it is possible that, even though self.search_type is "sobject_list",
            # that an individual sobject is not of this type ... this is
            # true on updates or other searches where search_keys are given
            if sobject.get_search_type() != "sthpw/sobject_list":
                continue

            search_type = sobject.get_value("search_type")
            if not search_type:
                print("WARNING: sobject_list entry [%s] has no search_type" % sobject.get_id())
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
            except SearchException as e:
                # it may have been deleted
                # show it as is, without remapping
                print(str(e))
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
                    self.sobjects[row] = parent
                else:
                    # FIXME: what if this sobject does not exist anymore???
                    deleted[row] = sobject



        rows = deleted.keys()
        rows.sort()
        rows.reverse()

        #for row in rows:
            #sobject = deleted[row]
            #self.sobjects.pop(row)
        # we want to show the dangling sobject_list item so user can delete them
        # only available when not in refresh
        if self.search_wdg:
            search = self.search_wdg.get_search()
            total_count = search.get_count()
            # NOTE: this logic is only effective if the deleted/invalid is found
            # in this page being drawn
        else:
            total_count = len(self.sobjects)

        total_count -= len(rows)
        self.items_found = total_count


    def process_groups(self):

        self.widget_summary_option = {}
        self.group_values = {}
        self.group_ids = {}
        self.group_rows = []
        self.group_widgets = []
        self.level_name = ''
        self.level_spacing = 20

        self.is_on = True
        self.grouping_data = False

        self.group_mode = self.kwargs.get("group_mode")
        if not self.group_mode:
            self.group_mode = "top"

        # boolean for if there are real-time evaluated grouping data store in __group_column__<idx>
        self._grouping_data = {}
        self.group_by_time = {}

        # set some grouping parameters
        self.current_groups = []
        if self.group_element:
            if self.group_element in [True, False, '']: # Backwards compatibiity
                self.group_columns = []
            else:
                self.group_columns = self.group_element.split(',')
        else:
            self.group_columns = self.kwargs.get("group_elements")
            if not self.group_columns or self.group_columns == ['']: # Backwards compatibility
                self.group_columns = []
            if isinstance(self.group_columns, basestring):
                if not self.group_columns.startswith('['):
                    self.group_columns = self.group_columns.split(',')
                else:
                    eval(self.group_columns)


        #self.group_columns = ['timestamp']
        #self.group_interval = TableLayoutWdg.GROUP_WEEKLY
        if not self.group_columns:
            from tactic.ui.filter import FilterData
            filter = self.kwargs.get("filter")
            values = {}
            if filter and filter != 'None':

                filter_data = FilterData(filter)
                values_list = filter_data.get_values_by_prefix("group")
                if values_list:
                    values = values_list[0]

            if values.get("group"):
                self.group_columns = [values.get("group")]
                self.group_interval = values.get("interval")

        self.is_grouped = len(self.group_columns) > 0

        # store the group elements in the dom
        #self.table.add_attr("spt_group_elements", ",".join(self.group_columns))
        self.group_info.add_attr("spt_group_elements", ",".join(self.group_columns))

        # grouping preprocess , check the type of grouping
        if self.is_grouped and self.sobjects:
            search_type = self.sobjects[0].get_search_type()
            for group_column in self.group_columns:
                element_type = SearchType.get_tactic_type(self.search_type, group_column)
                self.group_by_time[group_column] = element_type in ['time', 'date', 'datetime']


        # initialize group_values
        for i, col in enumerate(self.group_columns):
            group_value_dict = {}
            self.group_values[i] = group_value_dict





    def check_access(self):
        '''check access for each element'''
        self.edit_permission_columns = {}
        filtered_widgets = []

        project_code = Project.get_project_code()
        security = Environment.get_security()
        for i, widget in enumerate(self.widgets):
            element_name = widget.get_name()
            # get all the attributes
            if element_name and element_name != "None":
                attrs = self.config.get_element_attributes(element_name)
                widget.set_attributes(attrs)
            else:
                attrs = {}

            self.attributes.append(attrs)


            # defined access for this view
            def_default_access = attrs.get('access')
            if not def_default_access:
                def_default_access = 'edit'


            # check security access
            access_key2 = {
                'search_type': self.search_type,
                'project': project_code
            }
            access_key1 = {
                'search_type': self.search_type,
                'key': element_name,
                'project': project_code

            }
            access_keys = [access_key1, access_key2]
            is_viewable = security.check_access('element', access_keys, "view", default=def_default_access)
            is_editable = security.check_access('element', access_keys, "edit", default=def_default_access)

            # hide columns with hidden="true", except when this is a temporary table for dynamic operations
            is_hidden = (self.kwargs.get("temp") != True) and (attrs.get("hidden") in ['true', True])

            is_viewable = is_viewable and (not is_hidden)

            if not is_viewable:
                # don't remove while looping, it disrupts the loop
                #self.widgets.remove(widget)
                self.attributes.pop()
            elif not is_editable:
                self.edit_permission_columns[element_name] = False
                filtered_widgets.append(widget)
            else:
                self.edit_permission_columns[element_name] = True
                filtered_widgets.append(widget)

        # reassign the widgets that pass security back to self.widgets
        self.widgets = filtered_widgets




    def _process_search_args(self):

        # this is different name from the old table selected_search_keys
        search_keys = self.kwargs.get("search_keys")

        # if a search key has been explicitly set without expression, use that
        expression = self.kwargs.get('expression')
        matched_search_key = False
        if self.search_key:
            base_search_type = SearchKey.extract_base_search_type(self.search_key)
        else:
            base_search_type = ''

        if self.search_type == base_search_type:
            matched_search_key = True
        if search_keys and search_keys != '[]':
            if isinstance(search_keys, basestring):
                if search_keys == "__NONE__":
                    search_keys = []
                else:
                    search_keys = search_keys.split(",")

            # keep the order for precise redrawing/ refresh_rows purpose
            if not search_keys:

                self.sobjects = []
            else:
                try:
                    sudo = Sudo()
                    self.sobjects = Search.get_by_search_keys(search_keys, keep_order=True)
                finally:
                    sudo.exit()

            self.items_found = len(self.sobjects)
            # if there is no parent_key and  search_key doesn't belong to search_type, just do a general search
        elif self.search_key and matched_search_key and not expression:
            sobject = Search.get_by_search_key(self.search_key)
            if sobject:
                self.sobjects = [sobject]
                self.items_found = len(self.sobjects)


        elif self.kwargs.get("do_search") != "false":
            self.handle_search()

        elif self.kwargs.get("sobjects"):
            self.sobjects = self.kwargs.get("sobjects")





    def get_display(self):


        # fast table should use 0 chunk size
        self.chunk_size = 0

        self.timer = 0

        self.edit_permission = True

        view_editable = self.view_attributes.get("edit")
        if not view_editable:
            view_editable = self.kwargs.get("edit")
        if view_editable in ['false', False]:
            self.view_editable = False
        else:
            self.view_editable = True


        admin_edit = self.kwargs.get("admin_edit")
        if admin_edit in ['false', False]:
            self.view_editable = False
        else:
            is_admin = Environment.get_security().is_admin()
            if is_admin:
                self.view_editable = True


        self.color_maps = self.get_color_maps()

        from pyasm.web import WebContainer
        web = WebContainer.get_web()
        self.browser = web.get_browser()

        self.error_columns = set()


        self.expand_on_load = self.kwargs.get("expand_on_load")

        if self.expand_on_load in [False, 'false']:
            self.expand_on_load = False
        else:
            self.expand_on_load = True


        self.sobject_levels = []


        # Make this into a function.  Former code is kept here for now.
        self._process_search_args()

        # set some grouping parameters
        self.process_groups()


        if self.kwargs.get('temp') != True:
            self.sobjects = self.order_sobjects(self.sobjects, self.group_columns)
            self.remap_sobjects()

        for sobject in self.sobjects:
            self.sobject_levels.append(0)

        self.edit_config_xml = self.kwargs.get("edit_config_xml")

        # Force the mode to widget because raw does work with FastTable
        # anymore (due to fast table constantly asking widgets for info)
        #self.mode = self.kwargs.get("mode")
        #if self.mode != 'raw':
        #    self.mode = 'widget'
        self.mode = 'widget'


        top = self.top
        self.set_as_panel(top)
        top.add_class("spt_sobject_top")
        top.add_class("spt_layout_top")


        # NOTE: still need to set an id for Column Manager
        top.set_id("%s_layout" % self.table_id)

        inner = DivWdg()
        top.add(inner)
        inner.add_color("background", "background")
        inner.add_color("color", "color")
        # NOTE: this is not the table and is called this for backwards
        # compatibility
        if self.kwargs.get("is_inner") not in ['true', True]:
            inner.add_class("spt_layout")
        inner.add_class("spt_table")
        inner.add_class("spt_layout_inner")


        has_extra_header = self.kwargs.get("has_extra_header")
        if has_extra_header in [True, "true"]:
            inner.add_attr("has_extra_header", "true")


        # add some basic styles
        style_div = HtmlElement("style")
        top.add(style_div)
        style_div.add('''
            .spt_layout .spt_cell_edit {

                padding: 3px 8px;
                vertical-align: middle;

                background-repeat: no-repeat;
                background-position: bottom right;
            }
        ''')




        if self.extra_data:
            if not isinstance(self.extra_data, basestring):
                inner.set_json_attr("spt_extra_data", self.extra_data)
            else:
                inner.add_attr("spt_extra_data", self.extra_data)

        if self.default_data:
            if not isinstance(self.default_data, basestring):
                inner.set_json_attr("spt_default_data", self.default_data)
            else:
                inner.add_attr("spt_default_data", self.default_data)



        save_class_name = self.kwargs.get("save_class_name")
        if save_class_name:
            inner.add_attr("spt_save_class_name", save_class_name)

        # The version of the table so that external callbacks
        # can key on this
        inner.add_attr("spt_version", "2")
        inner.add_style("position: relative")

        inner.add(self.group_info)


        if self.kwargs.get('temp') != True:

            if not Container.get_dict("JSLibraries", "spt_html5upload"):
                # add an upload_wdg
                from tactic.ui.input import Html5UploadWdg
                upload_wdg = Html5UploadWdg()
                inner.add(upload_wdg)
                self.upload_id = upload_wdg.get_upload_id()
                inner.add_attr('upload_id',self.upload_id)

            # get all client triggers
            exp = "@SOBJECT(config/client_trigger['event','EQ','%s$'])" %self.search_type
            client_triggers = Search.eval(exp)


            # set unique to True to prevent duplicated event registration when opening
            # multiple tables listens to event like accept|sthpw/task
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
                'event_name': 'update_row|%s' %self.search_type,
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
        self.validations_div = DivWdg()
        self.validations_div.add_class("spt_table_validations")
        self.validations_div.add_styles("display: none;")
        inner.add(self.validations_div)


        self.check_access()

        # set the sobjects to all the widgets then preprocess
        if self.mode == 'widget':
            for widget in self.widgets:
                widget.set_sobjects(self.sobjects)
                widget.set_parent_wdg(self)
                # preprocess the elements
                widget.preprocess()

                self.widget_summary_option[widget] = widget.get_option("total_summary")



        if self.kwargs.get("show_shelf") not in ['false', False]:
            # draws the row of buttons to insert and refresh
            action = self.get_action_wdg()
            inner.add(action)
        # get all the edit widgets
        if self.view_editable and self.edit_permission:
            self.edit_wdgs = self.get_edit_wdgs()
            edit_div = DivWdg()
            edit_div.add_class("spt_edit_top")
            edit_div.add_style("display: none")
            edit_div.add_border()
            inner.add(edit_div)
            for name, edit_wdg in self.edit_wdgs.items():
                # each BaseInputWdg knows about this FastTableLayoutWdg
                edit_display = edit_wdg.get_display_wdg()
                if edit_display:
                    edit_display.set_parent_wdg(self)
                edit_div.add(edit_wdg)
        else:
            self.edit_wdgs = {}


        # -- GROUP SPAN - this is to show hidden elements for ordering and
        # grouping
        group_span = DivWdg()
        group_span.add_style("display: none")
        group_span.add_class("spt_table_search")
        group_span.add(self.get_group_wdg() )
        inner.add(group_span)

        info = self.search_limit.get_info()
        if info.get("count") == None:
            info["count"] = len(self.sobjects)

        search_limit_mode = self.kwargs.get('search_limit_mode')
        if not search_limit_mode:
            search_limit_mode = 'bottom'

        if self.kwargs.get("show_search_limit") not in ['false', False] and search_limit_mode in ['top','both']:
            from tactic.ui.app import SearchLimitSimpleWdg
            limit_wdg = SearchLimitSimpleWdg(
                count=info.get("count"),
                search_limit=info.get("search_limit"),
                current_offset=info.get("current_offset")
            )
            inner.add(limit_wdg)


        # handle column widths
        column_widths = self.kwargs.get("column_widths")
        if not column_widths:
            column_widths = []
        else:
            if isinstance(column_widths, basestring):
                column_widths = column_widths.split(",")



        if not self.is_refresh and self.kwargs.get("do_initial_search") in ['hidden']:
            inner.set_style("display: none")



        self.element_names = self.config.get_element_names()

        for i, widget in enumerate(self.widgets):

            default_width = self.kwargs.get("default_width")
            if not default_width:
                default_width = widget.get_width()
            else:
                default_width = int(default_width)

            if not default_width:
                default_width = -1

            width = self.attributes[i].get("width")

            if i >= len(column_widths):
                # default width
                if width:
                    column_widths.append(width)
                else:
                    column_widths.append(default_width)

            elif not column_widths[i]:
                column_widths[i] = default_width


        # resize the widths so that the last one is free
        expand_full_width = True
        default_width = 120
        min_width = 45
        #expand_full_width = False

        for i, item_width in enumerate(reversed(column_widths)):

            if item_width == "auto":
                continue

            if isinstance(item_width, basestring):
                if item_width.endswith("px"):
                    item_width = item_width.replace("px", "")
                    item_width = int(float(item_width))
                elif item_width.endswith("%"):
                    continue
                else:
                    try:
                        item_width = int(float(item_width))
                    except:
                        item_width = -1
            if i == 0 and expand_full_width:
                column_widths[-(i+1)] = -1
            elif item_width == -1:
                column_widths[-(i+1)] = default_width
            elif item_width < min_width:
                column_widths[-(i+1)] = min_width



        self.kwargs["column_widths"] = column_widths


        sticky_header = self.kwargs.get("sticky_header")
        if sticky_header in [False, 'false']:
            sticky_header = False
        else:
            sticky_header = True

        #inner.add_style("width: 100%")

        if sticky_header:

            h_scroll = DivWdg()
            h_scroll.add_class("spt_table_horizontal_scroll")
            h_scroll.add_class("d-none d-sm-flex")
            inner.add(h_scroll)
            h_scroll.add_style("overflow-x: hidden")
            h_scroll.add_style("overflow-y: auto")
            h_scroll.add_style("height: 100%")
            h_scroll.add_style("flex-direction: column")
 
            scroll = DivWdg()
            h_scroll.add(scroll)


            # TODO: Remove this padding
            padding = DivWdg()
            #scroll.add(padding)
            padding.add_class("spt_header_padding")
            padding.add_style("width", "8px")
            padding.add_style("display", "none")

            padding.add_style("background", "#F5F5F5")
            #padding.add_style("float", "right")
            padding.add_style("position: absolute")
            padding.add_style("right: 0px")



            self.header_table = Table()
            scroll.add(self.header_table)



            self.header_table.add_class("spt_table_with_headers")
            self.header_table.set_id("spt_table_with_headers")
            self.header_table.set_unique_id()
            self.handle_headers(self.header_table)

            scroll = DivWdg()
            scroll.add_class("spt_table_scroll")
            scroll.add_style("height: 100%")
            h_scroll.add(scroll)
            
            """
            height = self.kwargs.get("height")
            if height:
                try:
                    height = int(height)
                    height = str(height) + "px"
                except ValueError:
                    pass
                scroll.add_style("height: %s" % height)
          

            window_resize_offset = self.kwargs.get("window_resize_offset")
            if window_resize_offset:
                scroll.add_class("spt_window_resize")
                scroll.add_attr("spt_window_resize_offset", window_resize_offset)

            window_resize_xoffset = self.kwargs.get("window_resize_xoffset")
            if window_resize_xoffset:
                scroll.add_attr("spt_window_resize_xoffset", window_resize_xoffset)
            """


            # sync header to this scroll
            # FIXME: this does not work with locked columns as the locked columns have their own
            # scrollbar
            scroll.add_attr( "onScroll", '''document.id(this).getParent('.spt_layout').getElement('.spt_table_with_headers').setStyle('margin-left', -this.scrollLeft);''')
            # Scroll event not implemented in behaviors yet
            """
            scroll.add_behavior( {
                'type': 'scroll',
                'cbjs_action': '''
                console.log(bvr.src_el.scrollLeft);
                '''
            } )
            """

            scroll.add_style("overflow-y: auto")
            scroll.add_style("overflow-x: auto")
            scroll.add_style("position: relative")

            # Moo scrollbar
            """
            scroll.add_style("overflow-y: hidden")
            scroll.add_behavior( {
                'type': 'load',
                'cbjs_action': '''
                new Scrollable(bvr.src_el, null);
                '''
            } )
            """



            """
            if not height and self.kwargs.get("__hidden__") not in [True, 'True', 'true']:
                # set to browser height
                scroll.add_behavior( {
                    'type': 'load',
                    'cbjs_action': '''
                    var y = window.getSize().y;
                    bvr.src_el.setStyle('height', y);
                    '''
                    } )
            """


            table = self.table
            table.add_class("spt_table_table")
            font_size = self.kwargs.get("font_size")
            if font_size:
                table.add_style("font-size: %s" % font_size)
                self.header_table.add_style("font-size: %s" % font_size)
            scroll.add(table)
            self.scroll = scroll

            table.add_color("color", "color")

            self.header_table.add_style("table-layout", "fixed")
            if self.kwargs.get("fixed_table") not in [False, 'false']:
                self.table.add_style("table-layout", "fixed")

            self.table.add_style("margin-top: -1px")

        else:
            table = self.table
            self.header_table = table

            # TEST scroll of the table
            scroll = DivWdg()
            inner.add(scroll)
            scroll.add_style("width: 100%")
            scroll.add_style("overflow-x: auto")
            scroll.add(table)

            #inner.add(table)

            table.add_class("spt_table_table")
            table.add_class("spt_table_with_headers")
            table.add_color("color", "color")

            self.handle_headers(self.header_table)

            inner.add_style("overflow-x: auto")

        table.set_id(self.table_id)


        # TEST TEST TEST
        from .mobile_wdg import MobileTableWdg
        mobile_wdg = MobileTableWdg(table_id=self.table_id)
        inner.add(mobile_wdg)


        # generate dictionary of subscribed search_keys to affect context menu
        self.subscribed_search_keys = {}
        login = Environment.get_login().get("login")
        subscribed = Subscription.get_by_search_type(login, self.search_type)
        for item in subscribed:
            item_search_key = item.get("message_code")
            self.subscribed_search_keys[item_search_key] = True

        # set up the context menus
        show_context_menu = self.kwargs.get("show_context_menu")
        if show_context_menu in ['false', False]:
            show_context_menu = False
        elif show_context_menu == 'none':
            pass
        else:
            show_context_menu = True

        admin_edit = self.kwargs.get("admin_edit")
        if admin_edit in ['false', False]:
            show_context_menu = False
        else:
            is_admin = Environment.get_security().is_admin()
            if is_admin:
                show_context_menu = True


        temp = self.kwargs.get("temp")

        if temp != True:
            menus_in = {}
            if show_context_menu:
                menus_in['DG_HEADER_CTX'] = [ self.get_smart_header_context_menu_data() ]
                menus_in['DG_DROW_SMENU_CTX'] = [ self.get_data_row_smart_context_menu_details() ]
            elif show_context_menu == 'none':
                div.add_event('oncontextmenu', 'return false;')
            if menus_in:
                SmartMenu.attach_smart_context_menu( inner, menus_in, False )


        for widget in self.widgets:
            #if self.kwargs.get('temp') != True:
            widget.handle_layout_behaviors(table)
            self.drawn_widgets[widget.__class__.__name__] = True



        # FIXME: this is needed because table gets the
        # class spt_table (which is also on inner).  This is done in
        # __init__ and needs to be fixed
        table.add_attr("spt_view", self.kwargs.get("view") )
        table.set_attr("spt_search_type", self.search_type)


        # provide an opportunity to table
        self.handle_table_behaviors(table)



        # draw 4 (even) rows initially by default
        has_loading = False
        init_load_num = self.kwargs.get('init_load_num')

        if not init_load_num:
            init_load_num = 4
        elif init_load_num == 'null':
            init_load_num = 4
        else:
            init_load_num = int(init_load_num)

        # override init_load_num if group column has group_bottom
        if self.has_group_bottom() or self.has_bottom_wdg():
            init_load_num = -1

        # check the widgets if there are any that can't be async loaded
        for widget in self.widgets:
            if not widget.can_async_load():
                init_load_num = -1
                break

        # minus 1 since row starts at 0
        init_load_num -= 1

        chunk_size = 20

        # group stack
        gstack = []

        document_mode = self.kwargs.get("document_mode") or False

        # TEST javascript loading of rows
        #self.js_load = True
        if self.js_load == True:

            data_div = DivWdg()
            inner.add(data_div)
            data_div.add_class("spt_data")

            data = []
            for i, sobject in enumerate(self.sobjects):
                sobject_dict = {}
                data.append(sobject_dict)

                sobject_dict['__search_key__'] = sobject.get_search_key()
                sobject_dict['__search_key_v1__'] = sobject.get_search_key(use_id=True)
                sobject_dict['__display_value__'] = sobject.get_display_value()


                # allow each widget to add values it needs to the sobject
                for widget in self.widgets:
                    widget.set_current_index(i)
                    element_name = widget.get_name()

                    sobject_data = widget.get_data(sobject)
                    sobject_dict[element_name] = sobject_data




            data_str = jsondumps(data)
            data_str = data_str.replace('"', "&quot;")

            data_div.add_attr("spt_data", data_str)

            if self.num_lock_columns:
                expand_table = "free"
            else:
                expand_table = "full"


            data_div.add_behavior( {
                'type': 'load',
                'expand_table': expand_table,
                'cbjs_action': '''
                var data_str = bvr.src_el.getAttribute("spt_data");
                var data = JSON.parse(data_str);
                bvr.src_el.removeAttribute("spt_data");
                spt.table.load_data(data);
                spt.table.expand_table(bvr.expand_table);
                '''
            } )

            self.sobjects = []





        for row, sobject in enumerate(self.sobjects):

            # TEST: check if this sobject is a group
            if document_mode in [True, 'true']:

                if sobject.get_value("is_group", no_exception=True):

                    self.is_grouped = False
                    group_level = sobject.get_value("group_level")
                    group_value = sobject.get_value("title")
                    children = sobject.get_value("children", no_exception=True)


                    # FIXME: need to eliminate these
                    self.group_columns = ['L1','L2']
                    group_column = "L1"
                    last_value = group_value

                    #self.group_columns = []
                    #group_column = None
                    #last_value = None

                    tr = self.handle_group(table, group_level, sobject, group_column, group_value, last_value)

                    tr.group_level = group_level
                    tr.set_attr("spt_group_level", group_level)

                    if children:
                        tr.set_attr("spt_children", children)


                    # keep track of the group stack
                    if group_level < len(gstack):
                        gstack = gstack[:group_level-1]
                    gstack.append(tr)

                    continue

                else:
                    for item in gstack:
                        item.sobjects.append(sobject)


            else:

                # generate group rows dynamically
                if self.is_grouped:
                    self.handle_groups(table, row, sobject)
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




            # draw the sobject row
            level = len(self.group_columns) + self.sobject_levels[row]
            self.handle_row(table, sobject, row, level)


        undo_queue_save = ProjectSetting.get_value_by_key("table_layout/undo_queue/save") or "false"
        undo_queue_refresh = ProjectSetting.get_value_by_key("table_layout/undo_queue/refresh") or "false"

        table.add_behavior({
            'type': 'load',
            'undo_queue_save': undo_queue_save,
            'undo_queue_refresh': undo_queue_refresh,
            'cbjs_action': '''
                spt.table.undo_queue_save = bvr.undo_queue_save;
                spt.table.undo_queue_refresh = bvr.undo_queue_refresh;
            '''
        })


        # dynamically load rows
        if has_loading:
            table.add_behavior( {
            'type': 'load',
            'chunk': chunk_size,
            'expand_on_load': self.expand_on_load,
            'unique_id': self.get_table_id(),
            'cbjs_action': '''
            var layout = bvr.src_el.getParent(".spt_layout");
            spt.table.set_layout(layout);
            var rows = layout.getElements(".spt_loading");

            var loaded_event = "loading|" + bvr.unique_id;
            var loading_event = "loading_pending|" + bvr.unique_id;

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
                spt.named_events.fire_event(loading_event, {});
                count += 1;
                var rows = jobs[count];
                if (! rows || rows.length == 0) {
                    spt.named_events.fire_event(loaded_event, {});
                    // run at the end of last load
                    if (bvr.expand_on_load) {
                        spt.table.set_layout(layout);
                        spt.table.expand_table("full");
                    }
                    return;
                }
                spt.table.apply_undo_queue();
                
                spt.table.refresh_rows(rows, null, null, {on_complete: func, json: search_dict, refresh_bottom: false});
                if (bvr.expand_on_load) {
                    spt.table.expand_table("full");
                }
            }
            func();

            '''
            } )
        elif not temp:
            table.add_behavior( {
            'type': 'load',
            'unique_id': self.get_table_id(),
            'expand_on_load': self.expand_on_load,
            'cbjs_action': '''
                var unique_id = "loading|"+bvr.unique_id;
                spt.named_events.fire_event(unique_id, {});
                if (bvr.expand_on_load) {
                    spt.table.expand_table("full");
                }
                // Not sure why we need a set timeout here ...
                setTimeout( function() {
                    spt.table.apply_undo_queue();
                }, 0 );

            '''
            } )



        if not self.sobjects:
            self.handle_no_results(table)

        # refresh columns have init_load_num = -1 and temp = True
        if init_load_num < 0 or temp != True:
            self.add_table_bottom(table)
            self.postprocess_groups(self.group_rows)


            # extra stuff to make it work with ViewPanelWdg
            if self.kwargs.get("is_inner") not in ['true', True]:
                top.add_class("spt_table_top")

            class_name = Common.get_full_class_name(self)
            top.add_attr("spt_class_name", class_name)

            self.table.add_class("spt_table_content")
            inner.add_attr("spt_search_type", self.kwargs.get('search_type'))
            inner.add_attr("spt_view", self.kwargs.get('view'))

            # extra ?? Doesn't really work to keep the mode
            inner.add_attr("spt_mode", self.mode)
            top.add_attr("spt_mode", self.mode)



            # add a hidden insert table
            inner.add( self.get_insert_wdg() )

            # add a hidden group insert table
            group_insert_wdg = self.get_group_insert_wdg()
            inner.add( group_insert_wdg )


            # this simple limit provides pagination and should always be drawn. Visible where applicable
            if self.kwargs.get("show_search_limit") not in ['false', False] and search_limit_mode in ['bottom','both']:
                from tactic.ui.app import SearchLimitSimpleWdg
                limit_wdg = SearchLimitSimpleWdg(
                    count=info.get("count"),
                    search_limit=info.get("search_limit"),
                    current_offset=info.get("current_offset"),
                )
                inner.add(limit_wdg)

            self.total_count = info.get("count")
            inner.add_attr("total_count", self.total_count)

        if self._use_bootstrap():
            top.add(self.get_bootstrap_styles())
        else:
            top.add(self.get_styles())

        if self.kwargs.get("is_refresh") == 'true':
            return inner
        else:
            return top


    def get_bootstrap_styles(self):
        styles = HtmlElement.style("""
                
        .spt_layout_inner {
            display: flex;
            flex-direction: column;
            height: 100%;
            position: relative;
            border-style: solid; 
            border-width: 0px;
        }

        @media (min-width: 576px)
            .d-sm-flex {
                display: flex! important;
            }
        }

        """)

        return styles

    def get_styles(self):

        styles = HtmlElement.style('''

            .spt_layout_top .spt_group_td_inner {
                align-items: center;
            }

            ''')

        return styles


    def _get_simplified_time(self, group_value):
        if group_value in ['', None, '__NONE__']:
            return group_value
        group_value = str(group_value)
        if self.group_interval == BaseTableLayoutWdg.GROUP_WEEKLY:
            # put in the week
            timestamp = parser.parse(group_value)
            # days was 7, but 6 seems to count the day on the start of a week accurately
            timestamp = list(rrule.rrule(rrule.WEEKLY, byweekday=0, dtstart=timestamp-timedelta(days=6, hours=0), count=1))
            timestamp = timestamp[0]
            timestamp = datetime(timestamp.year,timestamp.month,timestamp.day)
            timestamp.strftime("%Y %b %d")

            group_value = timestamp.strftime("%Y-%m-%d")

        elif self.group_interval == BaseTableLayoutWdg.GROUP_MONTHLY:
            timestamp = parser.parse(group_value)
            timestamp = datetime(timestamp.year,timestamp.month,1)

            group_value = timestamp.strftime("%Y %m")
        else: # the default group by a regular timestamp
            group_value = timestamp = parser.parse(group_value)
            group_value = timestamp.strftime("%Y-%m-%d")

        return group_value

    def _time_test(self, group_value):
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

    def _set_eval_value(self, sobject, group_column, group_value, idx):
        '''set the evaluated value for an sobject with an index-named column'''
        sobject.set_value("%s%s"%(self.GROUP_COLUMN_PREFIX, idx), group_value, temp=True)
        self._grouping_data[group_column] =  "%s%s"%(self.GROUP_COLUMN_PREFIX, idx)

    def order_sobjects(self, sobjects, group_columns):
        '''pre-order the sobjects if group_columns is defined, recursively'''
        if not self.group_columns:
            # post ordering for PythonElementWdg only
            if self.order_widget:
                tmp_order_element, direction  = self.get_order_element(self.order_element)
                if not isinstance(self.order_widget, PythonElementWdg):
                    return sobjects
                sobject_dict = {}
                self.order_widget.preprocess()
                reverse = direction == 'desc'
                for idx, sobject in enumerate(sobjects):
                    order_value = self.order_widget.get_result(sobject)
                    sobject_dict[sobject] = order_value

                sobjects = sorted(sobjects, key=sobject_dict.__getitem__, reverse=reverse)
            return sobjects
        self.group_dict = {}

        # identify group_column
        group_col_type_dict = {}
        for i, group_column in enumerate(group_columns):
            is_expr = re.search("^(@|\$|{@|{\$)", group_column)
            if is_expr:
                group_col_type_dict[group_column] = 'inline_expression'
            elif self.is_expression_element(group_column):
                widget = self.get_widget(group_column)
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
                widget = self.get_widget(group_column)
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
                        time_test = self._time_test(group_value)

                    if time_test == True:
                        self.group_by_time[group_column] = True
                        if group_value:
                            group_value = self._get_simplified_time(group_value)

                    if not group_value:
                        group_value = "__NONE__"

                    self._set_eval_value(sobject, group_column, group_value, i)

                elif isinstance(group_col_type_dict.get(group_column), ExpressionElementWdg):
                    widget = group_col_type_dict[group_column]


                    expr = widget.kwargs.get('expression')
                    group_value = widget._get_result(sobject, expr)

                    if not time_test:
                        time_test = self._time_test(group_value)
                    else:
                        self.group_by_time[group_column] = True

                    if self.group_interval and group_value:
                        group_value = self._get_simplified_time(group_value)
                    elif isinstance(group_value, basestring):
                        group_value = group_value.encode('utf-8')
                    else:
                        group_value = str(group_value)

                    if not group_value:
                        group_value = "__NONE__"

                    self._set_eval_value(sobject, group_column, group_value, i)
                elif isinstance(group_col_type_dict.get(group_column), PythonElementWdg):
                    widget = group_col_type_dict[group_column]

                    group_value = widget.get_result(sobject)
                    if not time_test:
                        time_test = self._time_test(group_value)
                    else:
                        self.group_by_time[group_column] = True

                    if self.group_interval and group_value:
                        group_value = self._get_simplified_time(group_value)
                    elif isinstance(group_value, basestring):
                        group_value = group_value.encode('utf-8')
                    else:
                        group_value = str(group_value)


                    if not group_value:
                        group_value = "__NONE__"

                    self._set_eval_value(sobject, group_column, group_value, i)

                elif self.group_by_time.get(group_column):  # self.group_interval
                    group_value = sobject.get_value(group_column, no_exception=True)
                    group_value = self._get_simplified_time(group_value)
                else:
                    group_value = sobject.get_value(group_column, no_exception=True)
                if not group_value:
                    group_value = "__NONE__"

                if i==0:
                    # this preps for ordering according to the first grouped column
                    # this is called recursively
                    sobject_list = self.group_dict.get(group_value)

                    if sobject_list == None:
                        sobject_list = [sobject]
                        self.group_dict[group_value] = sobject_list
                    else:
                        sobject_list.append(sobject)




        # extend back into an ordered list
        sobject_sorted_list = []
        reverse=False
        # TODO: check this dict self.group_dict

        if True in self.group_by_time.values():
            reverse = True
        elif self.order_element and self.order_element.endswith(' desc'):
            reverse = True

        sobjects = Common.sort_dict(self.group_dict, reverse=reverse)
        for sobject in sobjects:
            sub_group_columns = group_columns[1:]
            ordered_sobject = self.order_sobjects(sobject, sub_group_columns)
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




    def handle_table_behaviors(self, table):



        security = Environment.get_security()
        project_code = Project.get_project_code()
        self.handle_load_behaviors(table)

        # add the search_table_<table_id> listener used by widgets
        # like Add Task to Selected
        if self.kwargs.get('temp') != True:
            table.add_behavior( {
                'type': 'listen',
                'event_name': 'search_table_%s' % self.table_id,
                'cbjs_action': '''
                    var top = bvr.src_el.getParent(".spt_layout");
                    var version = top.getAttribute("spt_version");
                    spt.table.set_layout(top);
                    spt.table.run_search();
                '''
            } )



        element_names = self.element_names
        column_widths = self.kwargs.get("column_widths")
        if not column_widths:
            column_widths = []




        # set all of the column widths in javascript
        if self.kwargs.get('temp') != True:
            table.add_behavior( {
                'type': 'load',
                'element_names': self.element_names,
                'column_widths': column_widths,
                'cbjs_action': '''

                var column_widths = bvr.column_widths;

                var layout = bvr.src_el.getParent(".spt_layout");
                spt.table.set_layout(layout);

                for (var i = 0; i < bvr.element_names.length; i++) {
                    var name = bvr.element_names[i];
                    var width = column_widths[i];
                    if (width == -1) {
                        continue;
                    }
                    spt.table.set_column_width(name, width);
                }


                '''
            } )


        # all for collapsing of columns
        """
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
        """



        # column resizing behavior
        self.header_table.add_smart_styles("spt_resize_handle", {
            "position": "absolute",
            "height": "100px",
            "margin-top": "-3px",
            "right": "-1px",
            "width": "5px",
            "cursor": "e-resize",
            "background-color": ''
        } )



        self.header_table.add_relay_behavior( {
            'type': 'mouseover',
            'drag_el': '@',
            'bvr_match_class': 'spt_resize_handle',
            "cbjs_action": '''
            bvr.src_el.setStyle("background", "#333");
            '''
        } )

        self.header_table.add_relay_behavior( {
            'type': 'mouseout',
            'drag_el': '@',
            'bvr_match_class': 'spt_resize_handle',
            "cbjs_action": '''
            bvr.src_el.setStyle("background", "");
            '''
        } )






        resize_cbjs = self.kwargs.get("resize_cbjs") or ""

        self.header_table.add_behavior( {
            'type': 'smart_drag',
            'drag_el': '@',
            'bvr_match_class': 'spt_resize_handle',
            'ignore_default_motion': 'true',
            'resize_cbjs': resize_cbjs,
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
        table.add_relay_behavior( {
            'type': 'click',
            'bvr_match_class': 'spt_table_select',
            'cbjs_action': '''
                if (evt.shift == true) return;

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


        table.add_relay_behavior( {
        'type': 'click',
        'bvr_match_class': 'spt_table_select',
        #'modkeys': 'SHIFT',
        'cbjs_action': '''
        if (evt.shift != true) return;

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
        table.add_behavior( {
            'type': 'load',
            'cbjs_action': '''
            bvr.src_el.addEvent('mouseover:relay(.spt_cell_edit)',
                function(event, src_el) {

                    src_el.setStyle("background-repeat", "no-repeat");
                    src_el.setStyle("background-position", "bottom right");

                    if (src_el.hasClass("spt_cell_never_edit")) {
                    }
                    else if (src_el.hasClass("spt_cell_insert_no_edit")) {
                        src_el.setStyle("background-image", "url(/context/icons/custom/no_edit.png)" );
                    }
                    else {
                    }

                } )

            bvr.src_el.addEvent('mouseout:relay(.spt_cell_edit)',
                function(event, src_el) {
                    src_el.setStyle("background-image", "" );
                } )
            '''
        } )

        # row highlighting


        if self.kwargs.get("show_row_highlight") not in [False, 'false']:
            table.add_behavior( {
            'type': 'load',
            'cbjs_action': '''
            bvr.src_el.addEvent('mouseover:relay(.spt_table_row)',
                function(event, src_el) {
                    // remember the original color
                    src_el.addClass("spt_row_hover");
                    src_el.setAttribute("spt_hover_background", src_el.getStyle("background-color"));
                    spt.mouse.table_layout_hover_over({}, {src_el: src_el, add_color_modifier: -5});
                } )

            bvr.src_el.addEvent('mouseout:relay(.spt_table_row)',
                function(event, src_el) {
                    src_el.removeClass("spt_row_hover");
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


        cell_styles = {}


        show_border = self.kwargs.get("show_border")
        if show_border in ['horizontal']:
            cell_styles["border-bottom"] = "solid 1px %s" % border_color
            cell_styles["padding"] = "3px"
            select_styles["border-bottom"] = "solid 1px %s" % border_color

        elif show_border not in [False, "false", "none"]:
            cell_styles["border"] = "solid 1px %s" % border_color
            cell_styles["padding"] = "3px"
            select_styles["border"] = "solid 1px %s" % border_color



        table.add_smart_styles("spt_table_select", select_styles)
        table.add_smart_styles("spt_cell_edit", cell_styles)


        is_editable = self.kwargs.get("is_editable")

        # Edit behavior
        if is_editable in [False, 'false']:
            is_editable = False
        else:
            is_editable = True

        # Check user access
        access_keys = self._get_access_keys("edit",  project_code)
        if security.check_access("builtin", access_keys, "edit"):
            is_editable = True
        else:
            is_editable = False
            self.view_editable = False


        if is_editable:
            table.add_relay_behavior( {
                'type': 'click',
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
            'type': 'click',
            'bvr_match_class': 'spt_group_row_collapse',
            'cbjs_action': '''
            spt.table.set_table(bvr.src_el);
            var row = bvr.src_el.getParent(".spt_group_row");
            spt.table.collapse_group(row);
            '''
        } )


        if self.kwargs.get("show_group_highlight") not in [False, 'false']:
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






    def get_insert_wdg(self):
        '''Fake a table for inserting'''
        #self.group_columns = []
        self.edit_wdgs = {}
        table = Table()
        table.add_style("display: none")
        table.add_class("spt_table_insert_table")

        insert_sobject = SearchType.create(self.search_type)

        # set the sobjects to all the widgets then preprocess
        for widget in self.widgets:
            widget.set_sobjects([insert_sobject])
            #widget.set_layout_wdg(table)
            widget.set_parent_wdg(self)
            # preprocess the elements if not in widget mode
            # it has been done otherwise
            if self.mode != 'widget':
                widget.preprocess()


        row = self.handle_row(table, insert_sobject, row=0)
        row.add_class("SPT_TEMPLATE")
        row.add_class("spt_table_insert_row spt_clone")
        # to make focusable
        row.add_attr('tabIndex','-1')

        row.remove_class("spt_table_row")

        return table


    def get_group_insert_wdg(self):
        '''Fake a table for inserting'''
        self.edit_wdgs = {}
        table = Table()
        table.add_style("margin-top: 20px")
        table.add_style("display: none")
        table.add_class("spt_table_group_insert_table")

        insert_sobject = SearchType.create(self.search_type)

        # set the sobjects to all the widgets then preprocess
        """
        for widget in self.widgets:
            widget.set_sobjects([insert_sobject])
            #widget.set_layout_wdg(table)
            widget.set_parent_wdg(self)
            # preprocess the elements if not in widget mode
            # it has been done otherwise
            if self.mode != 'widget':
                widget.preprocess()
        """


        insert_sobject.set_value("name", "New Group")


        group_level = 0
        group_column = "test"
        group_value = "New Group"
        last_value = "New Group"
        row = self.handle_group(table, group_level, insert_sobject, group_column, group_value, last_value, is_template=True)

        row.add_class("spt_table_group_insert_row spt_clone")
        # to make focusable
        row.add_attr('tabIndex','-1')

        row.remove_class("spt_table_group_row")

        self.postprocess_groups( [row] )

        return table








    def handle_headers(self, table, hidden=False):

        # FIXME: for some reason, this is neeeded on the chunk loading
        #if self.kwargs.get('temp') == True:
        #    return

        # Add the headers
        tr = table.add_row()
        tr.add_class("spt_table_header_row")
        tr.add_class("SPT_DTS")

        if hidden:
            tr.add_style("display: none")


        autofit = self.view_attributes.get("autofit") != 'false'

        show_header = self.kwargs.get("show_header")
        if show_header not in ['false', False]:
            show_header = True
        else:
            show_header = False


        if not show_header:
            tr.add_style("display: none")



        if self.kwargs.get("__hidden__") == True:
            tr.add_color("background", "background", -8)
            border_color = table.get_color("table_border", default="border")
        else:
            tr.add_color("background", "background", -2)
            border_color = table.get_color("table_border", 0, default="border")
            tr.add_color("color", "color", 8)

        #SmartMenu.assign_as_local_activator( tr, 'DG_HEADER_CTX' )


        if self.kwargs.get("show_select") not in [False, 'false']:
            self.handle_select_header(table, border_color)

        # this comes from refresh
        widths = self.kwargs.get("column_widths")

        # boolean to determine if there is any width set for any columns
        width_set = False

        lock_width = 0


        for i, widget in enumerate(self.widgets):
            name = widget.get_name()

            th = table.add_header()
            if widths:
                if widths[i] != -1:
                    th.add_style("width", widths[i])
                    th.add_attr("last_width", widths[i])


            th.add_style("padding: 3px")

            if i < self.num_lock_columns:
                th.add_style("position: absolute")

                width = widths[i]
                if isinstance(width, basestring):
                    width = int(width.replace("px",""))
                th.add_style("left: %spx" % lock_width)
                th.add_attr("spt_lock_width", lock_width)
                th.add_style("background: #F9F9F9")
                th.add_style("z-index: 1")
                th.add_class("spt_table_cell_fixed")


                lock_width += width


            # this is meant for views that haven't been saved to default
            # to fit the whole screen
            th.add_style("text-align: left")
            # The smart menu has to be put on the header and not the
            # row to get row specific info.
            SmartMenu.assign_as_local_activator( th, 'DG_HEADER_CTX' )

            th.add_class("spt_table_header")
            th.add_class("spt_table_header_%s" %self.table_id)
            th.add_attr("spt_element_name", name)


            show_border = self.kwargs.get("show_border")
            if show_border not in [False, "false", 'horizontal']:
                th.add_style("border: solid 1px %s" % border_color)
            elif show_border == 'horizontal':
                th.add_style("border-width: 0px 0px 1px 0px")
                th.add_style("border-style: solid")
                th.add_style("border-color: %s" % border_color)

            edit_wdg = self.edit_wdgs.get(name)
            if edit_wdg:
                th.add_attr("spt_input_type", edit_wdg.get_element_type())

            inner_div = DivWdg()
            th.add(inner_div)
            inner_div.add_style("position: relative")
            inner_div.add_style("width: auto")
            inner_div.add_class("spt_table_header_inner")
            #inner_div.add_style("overflow: hidden")

            inner_div.add_style("min-width: 20px")
            inner_div.add_style("margin-top: 4px")
            inner_div.add_style("margin-bottom: 4px")


            header_height = "30px"
            inner_div.add_style("min-height: %s" % header_height)



            # handle the sort arrow
            sortable = self.attributes[i].get("sortable") != "false"
            if sortable:

                if self.order_element == name or self.order_element == "%s asc" % name:
                    th.add_styles("background-image: url(/context/icons/common/order_array_down_1.png);")
                elif self.order_element == "%s desc" % name:
                    th.add_styles("background-image: url(/context/icons/common/order_array_up_1.png);")

            # Qt webkit ignores these
            # This is fixed in PySide 1.1.2.  Need to update OSX version
            # before commenting this all out
            th.add_style("background-repeat: no-repeat")
            th.add_style("background-position: bottom center")
            th.add_style("vertical-align: top")
            th.add_style("overflow: hidden")



            # handle resizeble element
            resize_div = DivWdg()
            inner_div.add(resize_div)
            resize_div.add("&nbsp;")
            resize_div.add_class("spt_resize_handle")
            resize_div.add_style("position: absolute")
            resize_div.add_style("top: -10px")
            resize_div.add_style("right: -3px")
            resize_div.add_style("width: 3px")



            header_div = DivWdg()
            inner_div.add(header_div)
            header_div.add_style("padding: 1px 3px 1px 3px")
            header_div.add_class("spt_table_header_content")

            if self.kwargs.get("wrap_headers") not in ["true", True]:
                header_div.add_style("width: 10000%")
                #header_div.add_style("white-space: nowrap")


            reorder_cbjs = self.kwargs.get("reorder_cbjs") or ""

            # put reorder directly here
            behavior = {
                "type": 'drag',
                #"drag_el": 'drag_ghost_copy',
                "drag_el": '@',
                "drop_code": 'DgTableColumnReorder',   # can only specify single drop code for each drag behavior
                "reorder_cbjs": reorder_cbjs,
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
            element_type = SearchType.get_tactic_type(self.search_type, name)
            if element_type in ['time', 'date', 'datetime'] or widget.is_time_groupable():
                th.set_attr("spt_widget_is_time_groupable","true")

            if self.mode == 'widget':
                value = widget.get_title()
                if isinstance(value, six.string_types):
                    d = DivWdg()
                    d. add_style("margin-top: 6px")
                    d.add(value)
                    value = d
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

        has_extra_header = self.kwargs.get("has_extra_header")
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




    def has_group_bottom(self):
        '''return True if group_column has group_bottom'''
        if not self.group_columns:
            return False

        for widget in self.widgets:
            if widget.get_name() == self.group_columns[0]:
                expression = widget.get_option("group_bottom")
                if expression:
                    return True

        return False


    def has_bottom_wdg(self):
        '''return True if a widget has bottom widget defined'''
        for widget in self.widgets:

            if widget.get_bottom_wdg():
                return True

        return False

    def postprocess_groups(self, group_rows):

        # The problem is that often a group bottom cannot be calculated
        # until all the widgets have been drawn.

        has_widgets = None
        group_rows_summary_dict = {}
        widget_summary_dict = {}
        last_group_level = -1
        # reversed for ease of tallying
        group_rows.reverse()

        group_level = 0
        for idx, group_row in enumerate(group_rows):
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

                group_label_view = self.kwargs.get("group_label_view")
                group_label_class = self.kwargs.get("group_label_class")
                # Common.create_from_class_path(group_label_class, args, kwargs)


                # this is set in handle_group
                group_value = td.group_value
                group_div = td.group_div


                if group_div:
                    if not group_label_view and group_value == '__NONE__':
                        label = '---'
                    else:
                        group_label_expr = self.kwargs.get("group_label_expr")
                        group_label_link = self.kwargs.get("group_label_link")

                        if group_label_expr:
                            label = Search.eval(group_label_expr, sobjects, single=True)
                        elif group_label_view:

                            extra_data = self.kwargs.get("extra_data") or {}
                            if isinstance(extra_data, basestring):
                                try:
                                    extra_data = jsonloads(extra_data)
                                except:
                                    extra_data = {}


                            from tactic.ui.panel import CustomLayoutWdg
                            label = CustomLayoutWdg(
                                    search_type=self.search_type,
                                    view=group_label_view,
                                    group_value=group_value,
                                    sobjects=sobjects,
                                    group_level=group_level,
                                    **extra_data

                            )
                        elif group_label_class:
                            extra_data = self.kwargs.get("extra_data") or {}
                            if isinstance(extra_data, basestring):
                                try:
                                    extra_data = jsonloads(extra_data)
                                except:
                                    extra_data = {}

                            extra_data["search_type"] = self.search_type
                            extra_data["group_value"] = group_value
                            extra_data["sobjects"] = sobjects
                            extra_data["group_level"] = group_level

                            label = Common.create_from_class_path(group_label_class, {}, extra_data)
                        else:
                            label = Common.process_unicode_string(group_value)


                    group_div.add(label)



            # TODO: need to look this over. It currently messes up the table structure
            # since a group is a row-cell.
            # This adds widgets to a group item.  It would useful to tread a "group"
            # as an sobject and display just like the other sobjects
            group_widgets = []
            has_widgets = False

            if not widget_summary_dict:
                # assignmenet
                widget_summary_dict = {}

            """
            group_rows_summary_dict[group_level] = widget_summary_dict

            for widget in self.widgets:

                # ideally, it's more efficient for the widget to return a tuple. Some old ones may not
                tmp = widget.get_group_bottom_wdg(sobjects)
                option = self.widget_summary_option.get(widget)

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
            if group_level < len(self.group_columns) - 1:
                for wdg_idx, wdg in enumerate(self.widgets):

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

            """


            # reset when reaching the top level
            if group_level == 0:
                widget_summary_dict = {}
                group_rows_summary_dict[group_level] = widget_summary_dict

            elif group_level < last_group_level:
                for k, v in widget_summary_dict.items():
                    group_sum, total = v
                    widget_summary_dict[k] = (0, total)

            last_group_level = group_level



    def add_table_bottom(self, table):
        '''override the same method in BaseTableLayoutWdg to add a bottom row. this does not
           call handle_row() as it is simpler'''
        # add in a bottom row
        all_null = True
        bottom_wdgs = []
        for widget in self.widgets:
            bottom_wdg = widget.get_bottom_wdg()
            bottom_wdgs.append(bottom_wdg)
            if bottom_wdg:
                all_null = False



        if not all_null:

            tr = table.add_row()
            # don't use spt_table_row which is meant for regular row
            tr.add_class('spt_table_bottom_row')
            tr.add_color("background", "background", -3)
            if self.group_columns:
                last_group_column = self.group_columns[-1]
                tr.add_class("spt_group_%s" % self.group_ids.get(last_group_column))
                td = table.add_cell()

            #td = table.add_cell("&nbsp;")

            if self.kwargs.get("show_select") not in [False, 'false']:
                td = table.add_cell()
            # add in a selection td
            #if self.kwargs.get("show_select") not in [False, 'false']:
            #    self.handle_select(table, None)

            for i, bottom_wdg in enumerate(bottom_wdgs):
                element_name = self.widgets[i].get_name()
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





    def handle_groups(self, table, row, sobject):
        '''called per sobject, decide to draw a grouping folder if conditions are met'''

        if self.kwargs.get('temp') == True:
            return


        if row == 0:
            self.group_summary = []

            spacing = len(self.group_columns) * 20

            tr = table.add_row()
            tr.add_class("spt_table_hidden_group_row")
            if spacing:
                td = table.add_cell()
                td.add_style("width", "%spx" %spacing)
                td.add_style("width: %spx" % spacing)
                td.add_style("max-width: %spx" % spacing)
            if self.kwargs.get("show_select") not in [False, 'false']:
                td = table.add_cell()
                td.add_style("width", "30px")
                td.add_style("min-width", "30px")
                td.add_style("max-width", "30px")
            for widget in self.widgets:
                td = table.add_cell()
                td.add_class("spt_table_hidden_group_td")
                td.add_attr("spt_element_name", widget.get_name())



        last_group_column = None

        for i, group_column in enumerate(self.group_columns):
            group_values = self.group_values[i]

            eval_group_column =  self._grouping_data.get(group_column)
            if eval_group_column:
                group_column = eval_group_column

            group_value = sobject.get_value(group_column, no_exception=True)
            if self.group_by_time.get(group_column): #self.group_interval:
                #group_value = sobject.get_value(group_column, no_exception=True)
                group_value = self._get_simplified_time(group_value)
            if not group_value:
                group_value = "..."

            last_value = group_values.get(group_column)



            # break groups by a "/" delimiter
            if isinstance(group_value, six.string_types) and group_value.find("/"):
                parts = group_value.split("/")
                if not parts[0].endswith(" "):
                    group_value = parts[0]




            # if this is the first row or the group value has changed,
            # then create a new group
            if last_value == None or group_value != last_value:

                if last_value != None:
                    # group summary
                    if self.group_mode in ["bottom", "both"]:
                        tr, td = table.add_row_cell()
                        tr.set_sobjects(self.group_summary)
                        tr.add_style("background", "#EEF")
                        tr.add_class("spt_table_group_row")

                        self.group_summary = []
                        self.group_rows.append(tr)

                        tr, td = table.add_row_cell()
                        td.add("&nbsp;")
                        tr.add_border(size=1)

                if self.group_mode in ["top", "both"]:
                    self.handle_group(table, i, sobject, group_column, group_value, last_value)


                group_values[group_column] = group_value

                last_group_column = group_column
                # clear the next dict to facilate proper grouping in the next major group
                next_dict = self.group_values.get(i+1)
                if next_dict:
                    next_dict = {}
                    self.group_values[i+1] = next_dict


            # add the sobject to the current group summary.  This is how the group knows
            # what sobjects belong to it
            self.group_summary.append(sobject)



        # put the sobjects in each sub group for group summary calculation
        if self.group_rows:
            group_level = self.group_rows[-1].group_level

            last_group_level = 100
            for group_row in reversed(self.group_rows):
                group_level = group_row.group_level

                if group_level < last_group_level:
                    group_row.get_sobjects().append(sobject)
                    if group_level == 0:
                        break

                last_group_level = group_level






    def handle_group(self, table, i, sobject, group_column, group_value, last_value, is_template=False):
        '''Draw a toggle and folder for this group'''
        # we have a new group
        tr, td = table.add_row_cell()
        tr.add_class('unselectable')
        if i != 0 and not self.is_on:
            tr.add_style("display: none")

        tr.add_class("spt_table_row_item")
        tr.add_class("spt_table_group_row")


        if sobject.get_search_key():
            tr.add_attr("spt_search_key", sobject.get_search_key(use_id=True))
            tr.add_attr("spt_search_key_v2", sobject.get_search_key())

        unique_id = tr.set_unique_id()

        if not is_template and self.group_mode in ["top"]:
            self.group_rows.append(tr)


        if group_value != last_value:
            tr.group_level = i

        tr.set_attr("spt_group_level", i)

        title = ""


        # TEST TEST TEST
        document_mode = self.kwargs.get("document_mode") or False
        if document_mode in [True, 'true']:
            tr.add_behavior( {
                'type': 'drag',
                "drag_el": '@',
                "cb_set_prefix": 'spt.document.drag_row'
            } )



        # if grouped by time
        if self.group_by_time.get(group_column):
            label = Common.process_unicode_string(group_value)
            if self.group_interval == BaseTableLayoutWdg.GROUP_WEEKLY:
                title = 'Week  %s' %label
            elif self.group_interval == BaseTableLayoutWdg.GROUP_MONTHLY:
                # order by number, but convert to alpha title
                labels = label.split(' ')
                if len(labels)== 2:
                    timestamp = datetime(int(labels[0]),int(labels[1]),1)
                    title = timestamp.strftime("%Y %b")
        else:

            # TEST - Add button
            extra_data = self.extra_data or {}
            extra_data = extra_data.copy()

            for group_level, item in self.group_values.items():
                for x, y in item.items():
                    if y == "__NONE__":
                        continue
                    extra_data[x] = y

            extra_data[group_column] = group_value


            show_group_insert = self.kwargs.get("show_group_insert") or True
            show_group_insert = False
            if show_group_insert:

                td.add_style("position: relative")

                add_div = DivWdg()
                td.add(add_div)
                add_div.add_style("display: inline-block")
                add_div.add_style("position: absolute")
                add_div.add_style("right: 0px")
                #add_div.add_style("margin: 3px 8px 3px 5px")
                add_div.add_style("width: 30px")
                add_div.add_style("padding: 5px")
                add_div.add_class("tactic_hover")
                add_div.add_style("text-align: center")
                add_div.add_style("box-sizing: border-box")
                add_div.add_style("z-index: 10")
                add_div.add_class("hand")
                add_div.add("<i class='fa fa-plus' style='opacity: 0.5'> </i>")
                save_event = add_div.get_unique_event("edit")
                add_div.add_behavior( {
                    "type": "click",
                    "search_type": self.search_type,
                    "extra_data": extra_data,
                    "save_event": save_event,
                    "cbjs_action": '''
                    var class_name = 'tactic.ui.panel.EditWdg';

                    var kwargs = {
                        view: 'edit',
                        search_type: bvr.search_type,
                        default: bvr.extra_data,
                        extra_data: bvr.extra_data,
                        save_event: bvr.save_event,
                    }
                    spt.panel.load_popup("Insert", class_name, kwargs);

                    '''
                } )


                add_div.add_behavior( {
                    'type': 'listen',
                    'event_name': save_event,
                    'cbjs_action': '''
                    var layout = bvr.src_el.getParent(".spt_layout");
                    spt.table.set_layout(layout);
                    spt.table.do_search();
                    '''

                } )

                add_div.add_behavior( {
                    "type": "clickX",
                    "search_type": self.search_type,
                    "extra_data": extra_data,
                    "cbjs_action": '''

                    var layout = bvr.src_el.getParent(".spt_layout");
                    spt.table.set_layout(layout);
                    var group_el = bvr.src_el.getParent(".spt_group_row");
                    var new_row = spt.table.add_new_item({row: group_el});
                    new_row.extra_data = bvr.extra_data;

                    '''
                } )





        title_div = DivWdg()
        title_div.add(title)
        title_div.add_class("spt_table_group_title")


        # add the group value to this td ... only store widget if it wasn't
        # handled by the time grouping
        td.group_value = group_value
        if not title:
            td.group_div = title_div
        else:
            td.group_div = None


        self.group_widgets.append(title_div)

        # FIXME: need to move this somewhere else
        height = 30
        font_size = 12
        padding = 10
        extra_data = self.kwargs.get("extra_data") or {}
        open_icon = "FA_FOLDER_OPEN"
        closed_icon = "FA_FOLDER"
        group_icon_styles = ""
        if extra_data and isinstance(extra_data, basestring):
            try:
                extra_data = jsonloads(extra_data)
            except:
                print("WARNING: bad extra_data!!!")
                print(extra_data)
                extra_data = {}

            min_height = extra_data.get("min_height")
            if min_height:
                if isinstance(min_height, basestring):
                    min_height = min_height.replace("px", "")
                    min_height = int(min_height)
                height = min_height + 10

            font_size = extra_data.get("font_size") or font_size
            padding = extra_data.get("group_level_padding") or padding


            if extra_data.get("group_icons"):
                icons = extra_data.get("group_icons")
                icons = icons.split(",")
                open_icon = icons[0]
                if len(icons) == 1:
                    closed_icon = icons[0]
                else:
                    closed_icon = icons[1]

        table.add_style("font-size: %spx" % font_size)

        from tactic.ui.widget.swap_display_wdg import SwapDisplayWdg
        #swap = SwapDisplayWdg(title=title_div, is_on=self.is_on)
        swap = SwapDisplayWdg(is_on=self.is_on)


        swap.add_class("spt_group_row_collapse")
        open_div = IconWdg("OPEN", open_icon)
        closed_div = IconWdg("CLOSED", closed_icon)
        swap.set_display_wdgs(open_div, closed_div)
        swap.add_style("margin-left: 5px")
        swap.add_style("line-height: %s" % height)
        swap.set_behavior_top(self.table)

        collapse_default = self.kwargs.get("collapse_default")
        if collapse_default in [True, 'true']:
            collapse_level = self.kwargs.get("collapse_level") or -1
            swap.add_behavior({
                'type': 'load',
                'collapse_level': collapse_level,
                'cbjs_action': '''
                if (bvr.collapse_level != -1) {
                    var row = bvr.src_el.getParent(".spt_group_row");
                    var group_level = row.getAttribute("spt_group_level");
                    if (group_level != bvr.collapse_level) return;
                }
                bvr.src_el.getElement(".spt_group_row_collapse").click();
                '''
                })

        title_div.add_style("width: 100%")

        # build the inner flex layout
        td_inner = DivWdg()
        td_inner.add_style("width: 100%")
        td_inner.add_style("box-sizing: border-box")
        td.add(td_inner)
        td_inner.add_style("display: flex")
        td_inner.add_class("spt_group_td_inner")

        td_inner.add(swap)
        td_inner.add(title_div)



        td.add_style("height: %spx" % height)
        td.add_style("padding-left: %spx" % (i*padding+3))

        border_color = tr.get_color("table_border")
        tr.add_border(size="1px 0px 1px 0px", color=border_color)
        #tr.add_style("background", "#EEF")

        tr.add_attr("spt_unique_id", unique_id)
        tr.add_class("spt_group_row")





        # for group collapse js function
        tr.add_attr('idx', i)

        tr.add_attr("spt_group_name", group_value)


        if i != 0 and self.group_columns:
            last_group_column = self.group_columns[-1]
            tr.add_class("spt_group_%s" % self.group_ids.get(last_group_column))

        self.group_ids[group_column] = unique_id

        tr.add_color("background", "background", -3 )
        tr.add_color("color", "color")

        return tr



    def handle_row(self, table, sobject, row, level=0):

        # add the new row
        tr = table.add_row()
        if not self.is_on:
            tr.add_style("display: none")

        # remember the original background colors
        bgcolor1 = table.get_color("background")
        #bgcolor2 = table.get_color("background", -1)
        bgcolor2 = bgcolor1
        table.add_attr("spt_bgcolor1", bgcolor1)
        table.add_attr("spt_bgcolor2", bgcolor2)

        tr.add_class("spt_table_row_item")
        tr.add_class("spt_table_row")
        # to tag it with the current table to avoid selecting nested table contents when they are present
        tr.add_class("spt_table_row_%s" %self.table_id)
        if self.parent_key:
            tr.add_attr("spt_parent_key", self.parent_key )

        if self.connect_key:
            tr.add_attr("spt_connect_key", self.connect_key )

        security = Environment.get_security()
        project_code = Project.get_project_code()
        access_keys = self._get_access_keys("retire_delete",  project_code)
        if security.check_access("builtin", access_keys, "allow") or security.check_access("search_type", self.search_type, "delete"):
            search_key = sobject.get_search_key(use_id=True)

            # These are not yet used, commenting out for now
            #ret_api_key = tr.generate_api_key("retire_sobject", inputs=[search_key], attr="ret")
            #del_api_key = tr.generate_api_key("delete_sobject", inputs=[search_key], attr="del")
            #reac_api_key = tr.generate_api_key("reactivate_sobject", inputs=[search_key], attr="reac")


        # TEST TEST TEST
        document_mode = self.kwargs.get("document_mode") or False
        if document_mode in [True, 'true']:
            tr.add_behavior( {
                'type': 'drag',
                "drag_el": '@',
                "cb_set_prefix": 'spt.document.drag_row'
            } )

            tr.add_behavior({
                'type': 'click',
                'cbjs_action': '''

                 var row = bvr.src_el;
                 row.addClass("spt_table_selected");

                 var item = bvr.src_el.getElement(".spt_document_item");
                 var pipeline_code = item.getAttribute("spt_pipeline_code");
                 var title = item.getAttribute("spt_title");
                 var event = "pipeline_" + pipeline_code + "|click";

                 var temp = {
                     "pipeline_code": pipeline_code,
                     "title" : title,
                 }

                 var kwargs = {};
                 kwargs.options = temp;

                 spt.named_events.fire_event(event, kwargs);
                 spt.command.clear();
                 spt.pipeline.fit_to_canvas();

                 '''
                 })



        min_height = 25

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

            min_height = extra_data.get("min_height") or min_height


        tr.add_style("min-height: %spx" % min_height)
        tr.add_style("height: %spx" % min_height)

        tr.add_attr("spt_group_level", level)

        tr.add_attr("spt_search_key", sobject.get_search_key(use_id=True) )
        tr.add_attr("spt_search_key_v2", sobject.get_search_key() )
        #tr.add_attr("spt_search_type", sobject.get_base_search_type() )

        display_value = sobject.get_display_value(long=True)
        tr.add_attr("spt_display_value", display_value)
        if self.subscribed_search_keys.get(sobject.get_search_key()):
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


        self.is_insert = sobject.is_insert()



        # handle the grouping
        #for group_column in self.group_columns:
        #    tr.add_class("spt_group_%s" % self.group_ids.get(group_column))
        if self.group_columns:
            last_group_column = self.group_columns[-1]
            tr.add_class("spt_group_%s" % self.group_ids.get(last_group_column))


        # add in a selection td
        if self.kwargs.get("show_select") not in [False, 'false']:
            self.handle_select(table, sobject)

        lock_width = 0

        for i, widget in enumerate(self.widgets):

            element_name = widget.get_name()

            td = table.add_cell()
            td.add_class("spt_cell_edit")
            td.add_style("overflow: hidden")

            if sobject.is_insert():
                onload_js = widget.get_onload_js()
                if onload_js:
                    td.add_behavior( {
                        'type': 'load',
                        'cbjs_action': '''
                        try {
                            bvr.src_el.loadXYZ = function(element_name,cell, sobject) { %s }
                        }
                        catch(e) {
                            console.log("Error in load code for column");
                        }
                        ''' % onload_js
                    } )



            widths = self.kwargs.get("column_widths")
            if widths and widths[i] != -1:
                td.add_style("width", widths[i])
                td.add_attr("last_width", widths[i])
            else:
                td.add_style("width", "auto")
                td.add_attr("last_width", widths[i])


            # TEST
            if i < self.num_lock_columns:
                td.add_style("position: absolute")
                td.add_style("background: inherit")
                td.add_style("background-color: inherit")


                if i == self.num_lock_columns-1:
                    td.add_style("border-right: solid 2px #CCC")
                    #td.add_style("border-left: none")

                td.add_style("left: %spx" % lock_width)
                td.add_attr("spt_lock_width", lock_width)
                td.add_style("z-index: 10")
                td.add_class("spt_table_cell_fixed")


                self.expand_on_load = False



                # NOTE: widths must obviously exist, but there is a check before to see if it does

                cur_width = widths[0]
                if isinstance(cur_width, basestring):
                    cur_width = int(cur_width.replace("px",""))
                lock_width += cur_width




                if sobject.is_insert():
                    load_div = DivWdg()
                    self.top.add(load_div)

                    load_div.add_behavior( {
                        'type': 'load',
                        'lock_columns': self.num_lock_columns,
                        'cbjs_action': '''
                        var el = bvr.src_el;
                        if (el.processed == true) return;

                        el.processed = true;

                        var lock_columns = bvr.lock_columns;

                        var top = bvr.src_el.getParent(".spt_layout_top");
                        var layout = top.getElement(".spt_layout");
                        spt.table.set_layout(layout);
                        spt.table.expand_table("free");

                        var table = spt.table.get_table();
                        var header_table = layout.getElement(".spt_table_with_headers");
                        var table_scroll = layout.getElement(".spt_table_scroll");

                        table_scroll.setStyle("position", "relative");


                        // removed fixed layout for now
                        table.setStyle("table-layout", "fixed")
                        header_table.setStyle("table-layout", "fixed")


                        var table_els = table.getElements(".spt_table_cell_fixed");
                        table_els.forEach( function(el) {
                            el.setStyle("position", "absolute");
                            el.setStyle("background", "inherit");
                        } );

                        header_table.setStyle("width", "max-content");
                        table.setStyle("width", "max-content");

                        // sync all of the row heights

                        var resize_heights = function() {

                            if (!layout.isVisible()) return;
                            spt.table.set_layout(layout);
                            
                            var rows = spt.table.get_all_rows();
                            for (var i = 0; i < rows.length; i++) {

                                var height = rows[i].getSize().y;

                                var table_els = rows[i].getElements(".spt_table_cell_fixed");
                                for (var j = 0; j < table_els.length; j++) {
                                    if (table_els[j].scrollHeight > height) {
                                        height = table_els[j].scrollHeight;
                                    }
                                }
                                for (var j = 0; j < table_els.length; j++) {
                                    table_els[j].setStyle("height", height);
                                }
                                rows[i].setStyle("height", height);
                            }
                        }
                        resize_heights();

                        var interval_id = setInterval( function(e) {
                            resize_heights()
                        }, 1000);
                        bvr.src_el.height_interval_id = interval_id;



                        var header_els = header_table.getElements(".spt_table_cell_fixed");
                        header_els.forEach( function(el) {
                            el.setStyle("position", "absolute");
                            //var height = "35px";
                            //el.setStyle("height", height);

                        } );



                        var offset = 120*lock_columns;
                        header_table.setStyle("margin-left", offset);
                        table.setStyle("margin-left", offset);



                        var scroll = document.id(document.createElement("div"));
                        scroll.addClass("spt_horizontal_scroll");
                        scroll.inject(table_scroll, "after");
                        var scroll_content = document.id(document.createElement("div"));
                        scroll_content.inject(scroll);
                        scroll_content.innerHTML = "hello";

                        scroll.setStyle("position", "relative");
                        scroll.setStyle("width", "100%");
                        scroll.setStyle("background", "blue");
                        scroll.setStyle("height", "17px");
                        //scroll.setStyle("margin-top", "-17px");
                        scroll.setStyle("overflow-x", "scroll");
                        scroll.setStyle("overflow-y", "hidden");

                        scroll.setStyle("z-index", "2");
                        table_scroll.setStyle("z-index", "1");

                        setTimeout( function() {
                            var size = table_scroll.getSize().x;
                            scroll.setStyle("width", size);

                            var size2 = table_scroll.scrollWidth;
                            var size2 = header_table.getSize().x;
                            scroll_content.setStyle("width", size2+offset+100);

                            if (size2 <= size) {
                                //scroll.setStyle("display", "none");
                            }

                        }, 1000);

                        // remove the scrollbars
                        table_scroll.setStyle("overflow-x", "hidden");

                        //scroll.setStyle("border", "solid 2px green");
                        //scroll.scrollLeft = 30;
                        scroll.onscroll = function(e) {
                            header_table.setStyle("margin-left", -scroll.scrollLeft+offset);
                            table.setStyle("margin-left", -scroll.scrollLeft+offset);
                        }


                        // add an observer to the layout
                        /*
                        var callback = function() {
                            var size = header_table.getSize();
                            scroll_content.setStyle("width", size.x+120);
                            //var size = layout.getSize();
                            //scroll.setStyle("width", size.x);
                        }
                        var observer = new ResizeObserver(callback);
                        observer.observe(header_table);
                        layout.setStyle("border", "solid 1px red");
                        */


                        '''
                    } )

                    load_div.add_behavior( {
                        'type': 'unload',
                        'lock_columns': self.num_lock_columns,
                        'cbjs_action': '''
                        var interval_id = bvr.src_el.height_interval_id = interval_id;
                        clearTimeout(interval_id);
                        '''
                    } )

            # Qt webkit ignores these
            if self.browser == 'Qt':
                td.add_style("background-repeat: no-repeat")
                td.add_style("background-position: bottom right")
                td.add_style("vertical-align: top")

            # add spacing
            if level and element_name == self.level_name:
                td.add_style("padding-left: %spx" % (level*self.level_spacing))

            if self.mode == 'widget':
                widget.set_current_index(row)

                try:
                    if element_name in self.error_columns:
                        td.add(IconWdg("Error Found: see above", IconWdg.WARNING, True) )
                    else:
                        html = widget.get_buffer_display()
                        if not html:
                            html = "<div style='height: 14px'>&nbsp;</div>"
                        td.add(html)
                except Exception as e:

                    self.error_columns.add(element_name)

                    from pyasm.widget import ExceptionWdg
                    error_wdg = ExceptionWdg(e)
                    td.add(error_wdg)

                    # reset the top_layout
                    from pyasm.web import WidgetSettings
                    WidgetSettings.set_value_by_key('top_layout','')


            else:
                value = sobject.get_value(element_name, no_exception=True)
                td.add(value)


            self.name = widget.get_name()
            self.value = sobject.get_value(element_name, no_exception=True)

            if not self.is_insert and self.mode == 'widget':
                self.handle_color(td, widget, i)

                # provide an opportunity for the widget to affect the td and tr
                widget.handle_tr(tr)
                widget.handle_td(td)
            elif self.is_insert:
                widget.handle_tr(tr)
                widget.handle_td(td)

            is_editable = True
            # Check if view is editable first, if not, skip checking each column
            if self.view_editable:
                if not widget.is_editable():
                    is_editable = False
                else:
                    security = Environment.get_security()
                    if not security.check_access('element', {'name': element_name}, "edit", default='edit'):
                        is_editable = False


            # This is only neccesary if the table is editable
            if self.view_editable:

                edit = self.edit_wdgs.get(element_name)

                # insert rows have no edits defined yet
                if self.is_insert:
                    if not is_editable:
                        td.add_class("spt_cell_insert_no_edit")

                elif not edit or not is_editable:
                    td.add_class("spt_cell_no_edit")


                #get the value from the widget, else use self.value
                if edit:
                    edit.set_sobject(sobject)
                    values = edit.get_values()
                    column = edit.get_column()
                    value = values.get('main')
                    if not value and value != False:
                        value = ''
                else:
                    value = self.value

                ## add timezone conversion
                ##if not SObject.is_day_column(element_name):
                ##    element_type = SearchType.get_tactic_type(self.search_type, element_name)

                ##    if element_type in ['time', 'datetime']:
                ##        value = widget.get_timezone_value(value)

                if isinstance(value, basestring):
                    value = value.replace('"', '&quot;')


                elif isinstance(value, bool):
                    value = str(value).lower()

                elif isinstance(value, dict) or isinstance(value, list):
                    import json
                    value = json.dumps(value, indent=2, sort_keys=True)
                    value = value.replace('"', "&quot;")


                if value == None:
                    value = ""

                if td.get_attr("spt_input_value") == None:
                    td.add_attr("spt_input_value", value)
                #td.add_attr("spt_input_column", column)
            else:
                td.add_class("spt_cell_no_edit")



            # if this is an insert, then set the element name
            if self.is_insert:
                td.add_attr("spt_element_name", element_name)

        #tr.add_attr("ondragenter", "return false")
        tr.add_attr("ondragover", "spt.table.dragover_row(event, this); return false;")
        tr.add_attr("ondragleave", "spt.table.dragleave_row(event, this); return false;")
        tr.generate_api_key("insert", inputs=[self.search_type, {"name": "__API_UNKNOWN__"}], attr="insert")
        tr.generate_api_key("simple_checkin", inputs=["__API_UNKNOWN__", "__API_UNKNOWN__", "__API_UNKNOWN__", {"mode": "uploaded", "use_handoff_dir": False}], attr="checkin")
        tr.add_attr("ondrop", "spt.table.drop_row(event, this); return false;")


        # TEST: loading values dynamically using javascript
        """
        tr.add_behavior( {
            'type': 'load',
            'sobject': sobject.get_sobject_dict(),
            'cbjs_action': '''

            setTimeout( function() {

            var cells = bvr.src_el.getElements(".spt_update_cellX");
            for (var i = 0; i < cells.length; i++) {
                if (cells[i].update) {
                    cells[i].update(bvr.sobject);
                }
            }

            }, 500);
            '''

        } )
        """


        return tr





    def get_color_maps(self):

        # get the color maps
        from pyasm.widget import WidgetConfigView
        color_config = WidgetConfigView.get_by_search_type(self.search_type, "color")
        color_xml = color_config.configs[0].xml
        self.color_maps = {}
        for widget in self.widgets:
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
                try:
                    sudo = Sudo()
                    search = Search(search_type)
                    sobjects = search.get_sobjects()
                finally:
                    sudo.exit()

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

            self.color_maps[name] = bg_color_map, text_color_map
        return self.color_maps


    def handle_color(self, td, widget, index):

        # add a color based on the color map if color is not set to false
        disable_color = self.attributes[index].get("color") == 'false'
        if disable_color:
            return

        bg_color = None
        text_color = None

        if self.name is None:
            name = widget.get_name()
        else:
            name = self.name

        try:
            if self.value is None:
                value = widget.get_value()
            else:
                value = self.value

            if not isinstance(value, basestring):
                value = str(value)
            bg_color_map, text_color_map = self.color_maps.get(name)
            if bg_color_map:
                bg_color = bg_color_map.get(value)
                if bg_color:
                    td.add_style("background-color", bg_color)
            if text_color_map:
                text_color = text_color_map.get(value)
                if text_color:
                    td.add_style("color", text_color)
        except Exception as e:
            print('WARNING: problem when getting widget value for color mapping on widget [%s]: ' % widget, "message=[%s]" % e.message.encode('utf-8'))


    def handle_select_header(self, table, border_color=None):

        show_border = self.kwargs.get("show_border")
        if not border_color:
            border_color = table.get_color("table_border", 0, default="border")

        if self.group_columns:
            spacing = len(self.group_columns) * 20
            th = table.add_cell()
            th.add_style("min-width: %spx" % spacing)
            th.add_style("width: %spx" % spacing)
            th.add_style("max-width: %spx" % spacing)

            if show_border not in [False, "false", 'horizontal']:
                th.add_style("border", "solid 1px %s" % border_color)
            elif show_border == 'horizontal':
                th.add_style("border-width: 0px 0px 1px 0px")
                th.add_style("border-style: solid")
                th.add_style("border-color: %s" % border_color)



        th = table.add_cell()
        if show_border not in [False, "false", 'horizontal']:
            th.add_style("border", "solid 1px %s" % border_color)
        elif show_border == 'horizontal':
            th.add_style("border-width: 0px 0px 1px 0px")
            th.add_style("border-style: solid")
            th.add_style("border-color: %s" % border_color)




        #th.add_looks( 'dg_row_select_box' )
        th.add_class('look_dg_row_select_box')
        th.add_class( 'spt_table_header_select' )
        th.add_style('width: 30px')
        th.add_style('min-width: 30px')
        th.add_style('max-width: 30px')
        th.add_style('text-align', 'center')

        th.add(self.get_select_wdg())
        th.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        spt.table.set_table(bvr.src_el);
        var cell = bvr.src_el;

        if (cell.hasClass("look_dg_row_select_box") ) {
            cell.addClass("look_dg_row_select_box_selected");
            cell.removeClass("look_dg_row_select_box");
            spt.table.select_all_rows();
         
            //BMD
            checkbox = cell.getElement("input");
            if (checkbox) checkbox.checked = true;
        }
        else {
            cell.removeClass("look_dg_row_select_box_selected");
            cell.addClass("look_dg_row_select_box");
            spt.table.unselect_all_rows();
            
            //BMD
            checkbox = cell.getElement("input");
            if (checkbox) checkbox.checked = false;
        }

        '''
        } )



    def get_select_wdg(self):
        checkbox_container = DivWdg()
        checkbox_container.add_style("position", "relative")
        checkbox_container.add_style("top", "-4px")

        checkbox = DivWdg(css="checkbox spt_table_checkbox")
        checkbox_container.add(checkbox)
        label = HtmlElement("label")
        label.add_behavior({
            'type': 'load',
            'cbjs_action': '''
            
            bvr.src_el.addEventListener("click", function(e) {
                e.preventDefault();
            })
            '''
        })

        checkbox.add(label)
        check = HtmlElement("input")
        label.add(check)
        check.add_attr("type", "checkbox")
        check.add_behavior({
            'type': 'load',
            'cbjs_action': '$(bvr.src_el).bmdCheckbox()'
        })

        return checkbox_container

        

    def handle_select(self, table, sobject):
        # FIXME: this confilicts with another "is_grouped"
        #self.is_grouped = self.kwargs.get("is_grouped")
        #if self.is_grouped or self.group_columns:

        show_border = self.kwargs.get("show_border")

        if self.group_columns or True:
            spacing = len(self.group_columns) * 20
            if spacing:
                td = table.add_cell("&nbsp;")
                td.add_style("min-width: %spx" % spacing)
                td.add_style("width: %spx" % spacing)
                td.add_style("max-width: %spx" % spacing)

                if show_border not in [False, "false"]:
                    border_color = table.get_color("table_border", 0, default="border")
                    td.add_style("border-bottom", "solid 1px %s" % border_color)


        td = table.add_cell()
        td.add_class("spt_table_select")
        td.add_class('look_dg_row_select_box')
        td.add_class( 'SPT_DTS' )
        
        td.add_style("text-align", "center")
        
        td.add(self.get_select_wdg())
        
        
        if self.subscribed_search_keys.get(sobject.get_search_key()):
            td.add_border(direction="right", color="#ecbf7f", size="2px")

        if sobject and sobject.is_insert():
            icon_div = DivWdg()
            icon_div.add_class("spt_select_new")
            #icon = IconWdg("New", IconWdg.NEW)
            icon = IconWdg("New", "BS_ASTERISK")
            icon_div.add(icon)
            #td.add_style("padding: 1 0 0 10")
            icon_div.add_style("float: left")
            icon_div.add_style("margin-left: 7px")
            td.add(icon_div)

        return




    def get_edit_wdgs(self):
        # build all of the cell edits
        edit_wdgs = {}

        if self.edit_permission and self.view_editable:
            for j, widget in enumerate(self.widgets):
                name = widget.get_name()
                if not name:
                    continue

                # first check if the widget is actually editable
                editable = widget.is_editable()

                if editable == True:
                    editable = self.attributes[j].get("edit")
                    editable = editable != "false"
                elif editable == 'optional':
                    editable = self.attributes[j].get("edit")
                    editable = editable == "true"

                # finally check security after checking config attrs
                if self.edit_permission_columns.get(name) == False:
                    editable = False

                if editable == True:
                    from .layout_wdg import CellEditWdg
                    edit = CellEditWdg(x=j, element_name=name, search_type=self.search_type, state=self.state, layout_version=self.get_layout_version(), config_xml=self.edit_config_xml)
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
                        self.validations_div.add( v_div )


        return edit_wdgs


    def get_onload_js(self):
        return r'''
        spt.dom.load_js( ["dg_table.js"], function() {
            spt.dom.load_js( ["dg_table_action.js"], function() {
                spt.dom.load_js( ["dg_table_editors.js"], function() {} )
            } );
        } );
        '''




    def handle_load_behaviors(self, table):


        select_color = self.kwargs.get("select_color")
        if not select_color:
            select_color = table.get_color("background3")

        shadow_color = table.get_color("shadow")


        if self.kwargs.get('temp') != True:
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



        if self.kwargs.get("load_init_js") in [False, 'false']:
            return

        if Container.get_dict("JSLibraries", "spt_table"):
            return


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

spt.table.get_group_elements = function() {
    var layout = spt.table.layout;
    var group_info = layout.getElement(".spt_table_group_info");

    // not supported by some layouts (ie tile)
    if (!group_info) {
        return [];
    }


    var group_elements = group_info.getAttribute("spt_group_elements");
    if (group_elements) {
        return group_elements.split(",");
    }
    else {
        return [];
    }
}



spt.table.set_layout = function(layout) {
    if (!layout) {
        //spt.alert("Layout is null on spt.table.set_layout()");
        return;
    }

    spt.table.layout = layout;
    var table = layout.getElement(".spt_table_table");
    spt.table.last_table = table;
    spt.table.element_names = null;

    /*
    var data = layout.getAttribute("spt_data");
    if (data) {
        data = JSON.parse(data);
    }
    else {
        data = {};
    }
    spt.table.data = data;
    */


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



// filter methods

spt.table.add_filter = function(element, filter_type) {

    var element = document.id(element);
    var container = element.getParent(".spt_filter_container");
    var filter = element.getParent(".spt_filter_container_with_op");
    var op = filter.getElement(".spt_op");

    var op_value;
    if (op == null) {
        op_value = 'and';
    } else {
        op_value = op.getAttribute("spt_op");
    }

    // get template
    var filter_top = element.getParent(".spt_filter_top");
    var filter_template = filter_top.getElement(".spt_filter_template_with_op");

    var filter_templates = filter_top.getElements(".spt_filter_template_with_op");
    for (var i = 0; i < filter_templates.length; i++) {
        var filter_template_type = filter_templates[i].getAttribute("spt_filter_type")
        if (filter_template_type == filter_type) {
            filter_template = filter_templates[i];
            break;
        }

    }

    var filter_options = filter_top.getElement(".spt_filter_options");
    var filters = filter_options.getElements(".spt_filter_type_wdg");
    // clear the value in the textbox if any
    for (var k=0; k< filters.length; k++){
        input = filters[k].getElement("input");
        // hidden used for expression
        if (input && input.getAttribute('type') !='hidden' ) input.value ='';
    }



    // clone the filter
    var new_filter = spt.behavior.clone(filter_template);
    new_filter.addClass("spt_filter_container_with_op");
    new_filter.inject(filter, "after");
    var display = new_filter.getElement(".spt_op_display");

    var top = element.getParent(".spt_search");
    var filter_mode = top.getElement(".spt_search_filter_mode").value;
    if (filter_mode == 'custom') {
        display.innerHTML = op_value;
    }

    // make this into a new search filter
    var children = new_filter.getElements(".spt_filter_template");
    for (var i=0; i<children.length; i++) {
        var child = children[i];
        child.addClass("spt_search_filter");
    }
    var children = new_filter.getElements(".spt_op_template");
    for (var i=0; i<children.length; i++) {
        var child = children[i];
        child.addClass("spt_op");

        child.setAttribute("spt_op", op_value);
    }
}




spt.table.remove_filter = function(element) {

    var element = document.id(element);
    var container = element.getParent(".spt_filter_container");
    //var search_filter = element.getParent(".spt_search_filter")
    var search_filter = element.getParent(".spt_filter_container_with_op")

    var all_filters = container.getElements(".spt_filter_container_with_op");
    if (all_filters.length == 1) {
        return;
    }

    if (all_filters[0] == search_filter) {
        // have to destoy the spacing and op for the first filter
        var second_filter = all_filters[1];
        var op = second_filter.getElement(".spt_op");
        op.destroy();
        var spacing = second_filter.getElement(".spt_spacing");
        spacing.destroy();
    }

    container.removeChild( search_filter );

}








// Preview methods


spt.table.dragover_row = function(evt, el) {
    var top = document.id(el);
    top.setStyle("border", "dashed 1px blue");
    top.setStyle("background", "rgba(0,0,255,0.05)");
    top.setStyle("opacity", "0.3")
}


spt.table.dragleave_row = function(evt, el) {
    var top = document.id(el);
    top.setStyle("border", "solid 1px #BBB");
    top.setStyle("background", "");
    top.setStyle("opacity", "1.0")
}


// drop_row does NOT drop a row from the table
// It refers to the action of DROPPING A ROW INTO the table
spt.table.drop_row = function(evt, el) {
    evt.stopPropagation();
    evt.preventDefault();

    evt.dataTransfer.dropEffect = 'copy';
    var files = evt.dataTransfer.files;

    var top = document.id(el);
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
            var insert_key = el.getAttribute("SPT_INSERT_API_KEY");
            server.set_api_key(insert_key);
            var sobject = server.insert(search_type, {name: filename})
            server.clear_api_key();
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
                    var checkin_key = el.getAttribute("SPT_CHECKIN_API_KEY");
                    server.set_api_key(checkin_key);
                    server.simple_checkin( search_key, context, filename, kwargs);
                    server.clear_api_key();
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
                        img = document.id(img);
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
        var search_key = rows[i].getAttribute("spt_search_key_v2");
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

    // remove last row because it is the insert
    if (rows.length > 0 && rows[rows.length-1].hasClass("spt_table_insert_row")) {
        rows.pop();
    }


    return rows;
}


spt.table.get_first_row = function(embedded) {
    var table = spt.table.get_table();
    if (table) {
        var row = table.getElement(".spt_table_row");
        return row;
    }
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


spt.table.get_group_by_search_key = function(search_key, options) {
    var rows = spt.table.get_group_rows();
    var parent_group_key = null;
    if (options) {
        parent_group_key = options.parent_group_key;
    }
    var under_parent;
    for (var i = 0; i < rows.length; i++) {
        var row_search_key = rows[i].getAttribute("spt_search_key_v2");

        if (parent_group_key) {
            under_parent = under_parent ? true : parent_group_key == row_search_key;
        } else {
            under_parent = true;
        }

        if (search_key == row_search_key && under_parent) {
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
    var cell = row.getElement(".spt_table_select");
    if (cell) {
        cell.removeClass("look_dg_row_select_box");
        cell.addClass("look_dg_row_select_box_selected");
        
        //BMD
        checkbox = cell.getElement("input");
        if (checkbox) checkbox.checked=true;
    }
    
    var current_color = row.getAttribute("spt_last_background");
    if (!current_color){
        current_color = row.getAttribute("spt_hover_background");
        if (!current_color){
            current_color = row.getStyle("background-color");
        }
    }
    
    if (!spt.has_class(row,'spt_table_selected')) {

        row.setAttribute("spt_last_background", current_color);
        row.setStyle("background-color", spt.table.select_color);
        row.setStyle("font-weight", "700");
        row.setAttribute("spt_background", spt.table.select_color);
        row.addClass("spt_table_selected");
    }
    spt.table.last_selected_row = row;
}


spt.table.unselect_row = function(row) {
    var cell = row.getElement(".spt_table_select");
    if (cell) {
        cell.removeClass("look_dg_row_select_box_selected");
        cell.addClass("look_dg_row_select_box");
        
        //BMD
        checkbox = cell.getElement("input");
        if(checkbox) checkbox.checked=false;

    }
    row.setStyle("background-color", row.getAttribute("spt_last_background"));
    row.setStyle("font-weight", "normal");
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


spt.table.hide_selected = function() {
    var rows = spt.table.get_selected_rows();
    for ( var i = 0; i < rows.length; i++ ) {
        rows[i].setStyle("display", "none");
    }
    spt.table.unselect_all();
}




spt.table.add_hidden_row = function(row, class_name, kwargs) {
    var clone = document.createElement("tr");
    clone.addClass("spt_hidden_row");
    var color = row.getAttribute("spt_hover_background");
    clone.setStyle("background", color);

    var children = row.getChildren();
    var num_children = children.length;
    var html = '<img src="/context/icons/common/indicator_snake.gif" border="0"/>';
    clone.innerHTML = "<td class='spt_hidden_row_cell' colspan='"+num_children+"'> "+html+" Loading ...</td>";
    clone.inject(row, "after");

    var hidden_row = clone.getElement(".spt_hidden_row_cell");
    hidden_row.setStyle("height", "50px");
    hidden_row.setStyle("font-size", "14px");
    hidden_row.setStyle("font-weight", "bold");
    hidden_row.setStyle("padding-bottom", "10px");

    // position the arrow
    var src_el = kwargs.src_el;
    kwargs.src_el = "";
    var pos = src_el.getPosition(row);
    var dx = pos.x - 30;

    var server = TacticServerStub.get();

    if (spt.table.last_table.hasOwnProperty('hidden_zindex'))
        spt.table.last_table.hidden_zindex += 1;
    else
        spt.table.last_table.hidden_zindex = 100;



    // New popup test
    var on_complete = function(widget_html) {
        hidden_row.setStyle("padding-left", "32px");
        hidden_row.setStyle("font-size", "12px");
        hidden_row.setStyle("font-weight", "normal");
        hidden_row.setStyle("min-width", "300px");

        var shadow_color = spt.table.shadow_color;

        var border_color = "var(--spt_palette_table_border)";

        // test make the hidden row sit on top of the table
        widget_html = "<div class='spt_hidden_content_top' style='border: solid 1px "+border_color+"; position: relative; z-index:" + spt.table.last_table.hidden_zindex + "; box-shadow: 0px 0px 15px "+shadow_color+"; background: "+color+"; margin-right: 20px; margin-top: 14px; overflow: hidden; min-width: 300px'>" +

          "<div class='spt_hidden_content_pointer' style='border-left: 13px solid transparent; border-right: 13px solid transparent; border-bottom: 14px solid "+color+";position: absolute; top: -14px; left: "+dx+"px'></div>" +
          "<div style='border-left: 12px solid transparent; border-right: 12px solid transparent; border-bottom: 13px solid "+color+";position: absolute; top: -13px; left: "+(dx+1)+"px'></div>" +

          "<div class='spt_remove_hidden_row' style='position: absolute; right: 3px; top: 3px; z-index: 50'><i class='hand fa fa-remove'> </i></div>" +
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
    //}

    //server.async_get_widget(class_name, kwargs);
    var class_name = kwargs.dynamic_class;
    server.get_widget(class_name, {args: kwargs}, on_complete);
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
            fx.start('margin-top', -size.y-100);
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
spt.table.add_rows = function(row, search_type, level, expression, kwargs) {

    if (!row.hasClass("spt_table_row_item") ) {
        row = row.getParent(".spt_table_row_item");
    }

    if (!kwargs) {
        kwargs = {}
    }

    var server = TacticServerStub.get();

    var search_key = row.getAttribute("spt_search_key");

    var kwargs = spt.table.get_refresh_kwargs(row);

    // find the number of tds in the row
    td_count = row.getChildren().length;

    var load_tr = document.createElement("tr");
    var load_td = document.createElement("td");
    load_td.setAttribute("colspan", td_count);
    load_tr.appendChild(load_td);


    var message = kwargs.message;
    if (!message) {
        message = "Loading ("+search_type+") ...";
    }

    load_td.innerHTML = message;


    load_tr.inject(row, "after");
    load_td.setStyle("padding", "5px");


    kwargs['expression'] = expression;


    // make some adjustments
    kwargs['search_type'] = search_type;
    kwargs['search_key'] = search_key;
    kwargs['level'] = level;
    kwargs['group_level'] = level;
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
            for (var i = 0; i < new_rows.length; i++) {
                new_rows[i].inject(row, "after");
                // remap the parent
                new_rows[i].setAttribute("spt_parent_key", search_key);

                var parts = search_key.split("?");
                new_rows[i].setAttribute("spt_parent_type", parts[0]);

                new_rows[i].setAttribute("spt_level", level);
                new_rows[i].setAttribute("spt_group_level", level);
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

    var class_name = 'tactic.ui.panel.TableLayoutWdg';
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



spt.table.add_extra_action = function(row, action, data) {
    var extra_action = row.extra_action;
    if (typeof(extra_action) == 'undefined') {
        extra_action = {};
        row.extra_action = extra_action;
    }
    extra_action[action] = data;
    return extra_action;
}




spt.table.add_new_row = function(kwargs) {
    return spt.table.add_new_item(kwargs);
}



spt.table.add_row = function(kwargs) {
    return spt.table.add_new_item(kwargs);
}

spt.table.add_new_item = function(kwargs) {

    if (typeof(kwargs) == 'undefined') {
        kwargs = {};
    }

    var layout = spt.table.get_layout();
    //var table = layout.getElement(".spt_table_insert_table")
    //var insert_row = table.getElement(".spt_table_insert_row");
    var insert_row = spt.table.get_insert_row();

    var search_type = layout.getAttribute("spt_search_type");

    var table = spt.table.get_table();
    if (kwargs.row) {
        var row = kwargs.row;
        var position = "after";
    }
    else if (kwargs.insert_location == 'bottom') {
        var rows = spt.table.get_all_rows();
        if (rows.length == 0) {
            var row = table.getElement(".spt_table_header_row");
        }
        else {
            var row = rows[rows.length-1];
        }
        var position = "after";

    }
    else {
        var row = table.getElement(".spt_table_row");
        var position = "before";
    }




    var clone = spt.behavior.clone(insert_row);

    // add extra data
    var inner = layout.getElement(".spt_layout_inner");
    if (inner) {
        var default_data = inner.getAttribute("spt_default_data");
    }
    else {
        var default_data = layout.getAttribute("spt_default_data");
    }
    if (default_data) {
        clone.extra_data = JSON.parse(default_data);
    }



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

    // fire a client event
    var tableId = spt.table.layout.getAttribute("spt_table_id");

    var event = "insert|tableId|"+tableId;
    spt.named_events.fire_event(event, {src_el: clone});

    var event = "insertX|"+search_type;
    spt.named_events.fire_event(event, {src_el: clone});

    // find the no items row
    no_items = table.getElement(".spt_table_no_items");
    if (no_items != null) {
        no_items.destroy();
    }

    return clone;

}




spt.table.add_new_group = function(kwargs) {

    if (typeof(kwargs) == 'undefined') {
        kwargs = {};
    }

    var layout = spt.table.get_layout();
    var table = layout.getElement(".spt_table_group_insert_table")
    var insert_row = table.getElement(".spt_table_group_insert_row");

    var search_type = layout.getAttribute("spt_search_type");

    var row;
    var position;
    var insert_location = kwargs.insert_location;
    if (!insert_location) insert_location = "bottom";

    var table = spt.table.get_table();
    if (kwargs.row) {
        row = kwargs.row;
        if (insert_location == "top") {
            position = "before"
        } else {
            position = "after";
        }
    }
    else if (insert_location == 'bottom') {
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
        row = table.getElement(".spt_table_row_item");
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

    }
    else {
        // should specify a class under td to avoid selecting td within td
        /*
        var clone_cells = clone.getElements("td.spt_cell_edit");
        var cells = row.getElements("td.spt_cell_edit");
        for (var i = 0; i < cells.length; i++) {
            var cell = cells[i];
            var clone_cell = clone_cells[i];
            var size = cell.getSize();
            if (clone_cell)
                clone_cell.setStyle("width", size.x);
        }
        */

        clone.inject(row, position);

    }


    var headers = spt.table.get_headers();

    var group_level = kwargs.group_level;
    if (!group_level) {
        group_level = 0;
    }
    var padding_multiplier = kwargs.padding_multiplier ? kwargs.padding_multiplier : 10

    var td = clone.getElement("td");
    td.setAttribute("colspan", headers.length);
    td.setStyle("padding-left", padding_multiplier*group_level+3);

    clone.setAttribute("spt_group_level", group_level);

    spt.remove_class(clone, 'spt_clone');

    // fire a client event
    var options = {insert_location: insert_location};
    var event = "insertX|"+search_type;
    spt.named_events.fire_event(event, {src_el: clone, options: options});

    // fire a client event
    var event = "insertY|"+search_type;
    spt.named_events.fire_event(event, {src_el: clone, options: options});

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



    if (cell.hasClass("spt_cell_no_edit")) {
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



    // Remove the first child
    // NOTE: this relies on a widget that has all components under the first
    // child.
    var first_child = document.id(cell.firstChild);

    // get the size before the edit widget is added
    var size = cell.getSize();

    if (first_child == null) {
        var tmp = document.id(document.createElement("span"));
        tmp.innerHTML = "";
        spt.table.last_data_wdg = tmp;
    }
    else if ( first_child.nodeName == '#text') {
        var tmp = document.id(document.createElement("span"));
        tmp.innerHTML = first_child.nodeValue;
        spt.table.last_data_wdg = tmp;
    }
    else {
        spt.table.last_data_wdg = first_child;
    }


    // clear the cell and remember it
    var html = cell.innerHTML;
    cell.innerHTML = '';
    cell.html = html;


    // code to find the edit_wdg internally
    var edit_wdg = spt.table._find_edit_wdg(cell, edit_wdg);
    if (edit_wdg == null) {
        return;
    }



    cell.setStyle("position", "relative");
    cell.setStyle("overflow", "");


    // add the edit to the DOM
    var layout = spt.table.get_layout();
    var table = spt.table.get_table();
    layout.appendChild(edit_wdg);
    spt.body.add_focus_element(edit_wdg);

    // store a reference to the cell it represents
    edit_wdg.cell = cell;
    edit_wdg.html = html;
    edit_wdg.addClass("spt_edit_widget");

    edit_wdg.on_complete = function() {
        spt.behavior.replace_inner_html( this.cell, this.html );
        spt.behavior.destroy_element(this);

        // reset last table values
        spt.table.last_cell = null;
        spt.table.last_data_wdg = null;
        spt.table.last_edit_wdg = null;
    }

    //cell.appendChild(edit_wdg);

    edit_wdg.setStyle("position", "absolute");
    edit_wdg.position( {
        position: {x: 0, y:0},
        relativeTo: cell,
        position: "upperLeft",
        offset: {x: 1, y: 1}
    } );

    edit_wdg.setStyle("margin", "-1px");
    edit_wdg.setStyle("z-index", 500);




    // code here to adjust the size of the edit widget
    spt.table.alter_edit_wdg(cell, edit_wdg, size);


    // put a dummy element in there to fill the space
    var dummy = document.id(document.createElement("div"));
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
        alert(edit_script);

        var get_edit_wdg_code = edit_script;
        var get_edit_wdg_script = spt.CustomProject.get_script_by_path(get_edit_wdg_code);

        edit_wdg = document.id(document.createElement("div"));
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
        //TODO: why is key = None?
        if (!key || key == 'None') {
            key = cell.getAttribute("spt_input_key");
            if (!key) {
                key = cell.getAttribute("spt_input_value");
            }
        }

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
    clone.setStyle("background-color", "var(--spt_palette_background)");
    clone.setStyle("box-shadow", "0px 0px 15px rgba(0,0,0,0.1)");

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
        if (size.y > 500) {
            input.setStyle( "height", '500px');
            input.setStyle( "position", 'relative');
            input.setStyle( "display", 'block');
        }
        else if (size.y > 100) {
            input.setStyle( "height", size.y+'px');
        }
        else
            input.setStyle( "height", '100px');

        if (size.x > 250)
            input.setStyle( "width", size.x+'px');
        else
            input.setStyle( "width", '250px');

        input.setStyle('font-family', 'courier new');
        input.setStyle('font-size', '1.1em');
        input.setStyle('padding', '5px');

        // inline text areas should be resizable in both directions
        input.setStyle('resize', 'both');

        input.value = value;
    }
    else if (input != null && input.type == "password") {
        input.setStyle( "width", size.x+'px');
        input.setStyle( "height", size.y+'px');
        input.value = ""
    }
    else if (input.nodeName == "INPUT") {
        set_focus = true;


        if (input.type != "color") {
            input.setStyle( "width", size.x+'px');
            input.setStyle( "height", size.y+'px');


            if (size.y > 500) {
                input.setStyle( "height", '500px');
            }
        }


        input.value = value;
        // for calendar input
        if (spt.has_class(input, 'spt_calendar_input')){
            accept_event = 'change';
            input.setStyle( "width", size.x+125 + 'px');

            // set the calendar to the current value
            if (value) {
                var parts = value.split(" ");
                var date_values = parts[0].split('-');
                var time_values = parts[1].split(':');
            }
            else {
                var date_values = [""];
                var time_values = [""];
            }
            spt.api.Utility.set_input_values(edit_wdg, time_values[0], '.spt_time_hour');
            spt.api.Utility.set_input_values(edit_wdg, time_values[1], '.spt_time_minute');


            setTimeout( function() {
                var cal_top = input.getParent('.spt_calendar_input_top');
                var cal = cal_top.getElement(".spt_calendar_top");
                if (cal) {
                    spt.panel.refresh(cal, {year: date_values[0], month: date_values[1]});
                }
            }, 0);

        }
        else if (input.type == "color") {
            accept_event = "change";
            set_focus = false;
            let text = input.getParent(".spt_color_top").getElement(".spt_color_text");
            text.addEvent("change", function() {
                input.value = text.value;
                spt.table.accept_edit(edit_wdg, input.value, true, {input: input});
            } )
            text.value = value;
            input.setAttribute("value", value);
            input.click();

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
        input.setStyle("min-width", "150px");
        input.setStyle("width", "auto");
        input.setStyle("overflow", "auto");
        input.setStyle("border", "solid 1px #DDD");

        edit_wdg.setStyle("position", "absolute");
        edit_wdg.setStyle("margin-right", "-3px");
        edit_wdg.setStyle("min-width", "140px");

        set_focus = true;
        accept_event = 'change';

        if( input.options.length > select_size_to_set ) {
            // only set to the configured select element size if actual
            // number of options is larger
            input.size = select_size_to_set;
        } else {
            input.size = input.options.length;
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
        try {
            input.setSelectionRange(0,0);
        }
        catch(e) {}

    }



    if (accept_event == 'blur') {
        input.addEvent("blur", function() {
            // to make checkbox aware of its checked state
            if (input.type =='checkbox')
               input.value = input.checked;
            spt.table.accept_edit(edit_wdg, input.value, true, {input: input});
        });
    }
    else if (accept_event) {
        input.addEvent(accept_event, function() {
            spt.table.accept_edit(edit_wdg, input.value, true, {input: input});
        });
    }
    else {
        input.addEvent("click", function() {
            spt.table.accept_edit(edit_wdg, input.value, true, {input: input});
        });
    }


    var els = input.getElements("option");
    els.forEach( function(el) {
        el.addEvent("mouseover", function(e) { el.setStyle("background", "var(--spt_palette_background3)") } );
        el.addEvent("mouseout", function(e) { el.setStyle("background", "") } );
    } );


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



// special function which opens a new tab
// accepted attributes: view, search_key and expression
spt.table.open_link = function(bvr) {

    var view = bvr.src_el.getAttribute("view");
    var search_key = bvr.src_el.getAttribute("search_key");
    var expression = bvr.src_el.getAttribute("expression");
    var widget_key = bvr.src_el.getAttribute("SPT_WIDGET_KEY");

    var name = bvr.src_el.getAttribute("name");
    var title = bvr.src_el.getAttribute("title");

    if (!name) {
        name = title;
    }

    if (!title) {
        title = name;
    }

    if (!title && !name) {
        title = name = "Untitled";
    }


    if (expression) {
        var server = TacticServerStub.get();
        var api_key = bvr.src_el.getAttribute("SPT_API_KEY");
        server.set_api_key(api_key);
        var sss = server.eval(expression, {search_keys: search_key, single: true})
        search_key = sss.__search_key__;
        server.clear_api_key();

        if (sss.name) {
            title = sss.name;
        }
        else {
            title = sss.code;
        }
        name = sss.code;
    }


    spt.tab.set_main_body_tab()

    if (view) {
        var cls = "tactic.ui.panel.CustomLayoutWdg";
        var kwargs = {
            view: view,
            search_key: search_key
        }
    }
    else if (search_key) {
        var cls = "tactic.ui.tools.SObjectDetailWdg";
        var kwargs = {
            search_key: search_key
        }
    }

    cls = widget_key;
    try {
        spt.tab.add_new(name, title, cls, kwargs);
    } catch(e) {
        spt.alert(e);
    }

}




spt.table.get_changed_rows = function(embedded) {
    if (typeof(embedded) == 'undefined')
        embedded = false;
    var table = spt.table.get_table();
    var css = embedded ? ".spt_table_row" : ".spt_table_row_" + table.getAttribute('id');
    var rows = table.getElements(css + ".spt_row_changed");
    return rows;
}



spt.table.get_changed_cells = function() {
    var table = spt.table.get_table();
    var cells = table.getElements(".spt_cell_changed");
    return cells;
}



spt.table.has_changes = function() {

    var changed_rows = spt.table.get_changed_rows();
    if (changed_rows.length > 0) {
        return true;
    }

    var insert_rows = spt.table.get_insert_rows();
    if (insert_rows.length > 0) {
        return true;
    }

    return false;
}


spt.table.get_changed_search_keys = function() {
    var rows = spt.table.get_changed_rows();

    var search_keys = [];
    for (var i = 0; i < rows.length; i++) {
        var search_key = rows[i].getAttribute("spt_search_key_v2");
        search_keys.push(search_key);
    }
    return search_keys;
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
        edited_cell = edit_wdg.cell;
        if (!edited_cell) {
            edit_wdg_top = edit_wdg.getParent(".spt_edit_widget");
            // if this is not inline
            if (edit_wdg_top) {
                edited_cell = edit_wdg_top.cell;
            }
        }

        // for inline cells
        if (!edited_cell) {
            edited_cell = edit_wdg.getParent(".spt_cell_edit");
        }
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



    // store updates globally as an undo queue
    var layout = spt.table.get_layout();
    var layout_top = layout.getParent(".spt_layout_top");
    var undo_queue  = layout_top.undo_queue;
    if (!undo_queue) {
        undo_queue = [];
        layout_top.undo_queue = undo_queue;
    }

    // empty the redo queue
    layout_top.redo_queue = [];




    if (!ignore_multi && selected_rows.length > 0 && changed && in_selected_row) {
        // get all of the cells with the same element_name
        var index = spt.table.get_column_index_by_cell(edited_cell);

        for (var i = 0; i < selected_rows.length; i++) {
            var cell = selected_rows[i].getElements(".spt_cell_edit")[index];
            var old_html = cell.innerHTML;

            var undo = spt.table._accept_single_edit(cell, new_value);
            undo_queue.push(undo);

            if (set_display) {
                cell.innerHTML = "";
                cell.setStyle("overflow", "hidden");
                spt.table.set_display(cell, display_value, input_type);
            }

            if (undo) {
                undo.old_html = old_html;
                undo.new_html = edited_cell.innerHTML;
            }

        }

    }
    else {
        var undo = kwargs.undo;
        if (!undo) {
            undo = {};
        }

        var undo = spt.table._accept_single_edit(edited_cell, new_value, undo);
        if (undo) {
            undo_queue.push(undo);
        }


        if (set_display) {
            edited_cell.innerHTML = "";
            edited_cell.setStyle("overflow", "hidden");

            if (!changed && edit_wdg.html) {
                spt.behavior.replace_inner_html(edited_cell, edit_wdg.html);
            }
            else {
                spt.table.set_display(edited_cell, display_value, input_type);
            }
        }

        if (undo) {
            undo.cell = edited_cell;
            undo.old_html = edited_cell.html;
            undo.new_html = edited_cell.innerHTML;
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
        // find an inner element
        var update_el = el.getElement(".spt_label");
        if (update_el) {
            update_el.innerHTML = value;
        } else {
            el.innerHTML = value;
        }
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

spt.table._accept_single_edit = function(cell, new_value, undo) {
    var old_value = cell.getAttribute("spt_input_value");

    if (old_value != new_value) {

        // remember the original value
        var orig_value = cell.getAttribute("spt_orig_input_value");
        if (!orig_value) {
            cell.setAttribute("spt_orig_input_value", old_value);
        }


        // set the new_value
        cell.setAttribute("spt_input_value", new_value);


        var row = spt.table.get_row_by_cell(cell);
        var search_key = row.getAttribute("spt_search_key_v2");
        var element_name = spt.table.get_element_name_by_cell(cell);

        if (!undo) {
            undo = {};
        }


        undo.cell = cell;
        undo.old_value = old_value;
        undo.new_value = new_value;
        undo.search_key = search_key;
        undo.element_name = element_name;
        undo.cbjs_action = null;
        undo.saved = false;


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
        return undo;
    }
}


spt.table.undo_last = function() {
    var layout = spt.table.get_layout();
    var layout_top = layout.getParent(".spt_layout_top");

    var undo_queue = layout_top.undo_queue;
    var last_undo = undo_queue.pop();
    if (!last_undo) {
        spt.alert("No more changes to undo");
        return;
    }


    // push this undo into the redo queue
    var redo_queue = layout_top.redo_queue;
    redo_queue.push(last_undo);


    var undo_type = last_undo.type;
    if (undo_type && last_undo.undo) {
        last_undo.undo();
        return;
    }


    var cell = last_undo.cell;

    // FIXME: orig_value should be the value before any changes
    var orig_value = cell.getAttribute("spt_orig_input_value");

    var new_value = last_undo.old_value;

    cell.innerHTML = last_undo.old_html;
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

}



spt.table.redo_last = function() {
    var layout = spt.table.get_layout();
    var layout_top = layout.getParent(".spt_layout_top");

    var redo_queue = layout_top.redo_queue;
    var last_redo = redo_queue.pop();
    if (!last_redo) {
        spt.alert("No more changes to redo");
        return;
    }

    // push this redo into the undo queue
    var undo_queue = layout_top.undo_queue;
    undo_queue.push(last_redo);



    var undo_type = last_redo.type;
    if (undo_type) {
        last_redo.redo();
        return;
    }



    var cell = last_redo.cell;

    // FIXME: orig_value should be the value before any changes
    var orig_value = cell.getAttribute("spt_orig_input_value");

    var new_value = last_redo.new_value;
    cell.innerHTML = last_redo.new_html;
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
}


spt.table.apply_undo_queue = function(undo_queue) {
    if (spt.table.undo_queue_refresh == "false"){
        return;
    }
    var layout = spt.table.get_layout();
    var layout_top = layout.getParent(".spt_layout_top");
    // sometimes layout_top is null

    if (!layout_top) {
        return;
    }
    var undo_queue = layout_top.undo_queue;
    if (!undo_queue) {
        return;
    }

    for (var i = 0; i < undo_queue.length; i++) {
        var undo = undo_queue[i];
        var search_key = undo.search_key;
        var element_name = undo.element_name;

        var row = spt.table.get_row_by_search_key(search_key);
        if (!row) {
            continue;
        }

        var cell = spt.table.get_cell(element_name, row);
        if (!cell) {
            continue;
        }

        var undo_type = undo.type;
        if (undo_type) {
            undo.redo();
            return;
        }

        // get the original value.  If there is no original value, then
        // set it so it can be used for future changes in this undo queue

        var orig_value = cell.getAttribute("spt_input_value");
        if (!orig_value){
            continue;
        }
        var new_value = undo.new_value;

        // remap to the new cell
        undo.cell = cell;

        if (orig_value == new_value) {
            cell.removeClass("spt_cell_changed");
            row.removeClass("spt_row_changed");
            var statuses_color = JSON.parse(cell.getAttribute("spt_colors"));
            var status = cell.getAttribute("spt_input_value");
            var cell_color = statuses_color[status];

            if (cell_color == null) {
                continue;
            }
            cell.setStyle("background-color", cell_color);
            row.setStyle("background-color", 'white');
            row.setAttribute("spt_background", 'white');
        }
        else {
            cell.innerHTML = undo.new_html;
            //cell.setAttribute("spt_input_value", undo.new_value);
            cell.addClass("spt_cell_changed");
            row.addClass("spt_row_changed");
            spt.table.set_changed_color(row, cell);
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

    var rows = spt.table.get_changed_rows();

    // insert rows appear to be included now
    /*
    var insert_rows = spt.table.get_insert_rows();
    for (var i = 0; i < insert_rows.length; i++) {
        rows.push(insert_rows[i]);
    }
    */

    var insert_data = [];
    var update_data = [];
    var search_keys = [];
    var web_data = [];
    var extra_data = [];
    var extra_action = [];

    var parent_key = null;
    var connect_key = null;



    var search_keys = []


    // collapse updates from undo_queue for be classified by search_type
    var use_undo_queue = spt.table.undo_queue_save;

    if (use_undo_queue == "true") {

        var layout = spt.table.get_layout();
        var layout_top = layout.getParent(".spt_layout_top")
        var undo_queue = layout_top.undo_queue;

        var updates = {};
        var extra_updates = {};

        for (var i = 0; i < undo_queue.length; i++) {
            var action = undo_queue[i];
            var saved = action.saved;
            if (saved == true){
                continue;
            }
            var search_key = action.search_key;
            var element_name = action.element_name;

            var action_type = action.type;

            if (!action_type) {
                var item_data = updates[search_key];
                if (!item_data) {
                    item_data = {};
                    updates[search_key] = item_data;
                }

                var value = action.new_value;
                item_data[element_name] = value;
                extra_item_data = [null];
            }
            else {
                updates[search_key] = action.get_data();
                extra_updates[search_key] = action.get_extra_data();
            }

            action.saved = true;


        }

        // break into two lists as required by save command
        var update_data = [];
        for (var search_key in updates) {

            search_keys.push(search_key);

            extra_action.push(null);

            update_data.push( updates[search_key] );
            extra_data.push(extra_updates[search_key]);

        };

    }



    else {


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

            // get extra action
            var extra_action_row = rows[i].extra_action;
            if (extra_action_row) {
                extra_action.push(extra_action_row);
            }
            else {
                extra_action.push(null);
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
    }



    if (search_keys.length == 0) {
        spt.alert("No changes have been made");
        return;
    }

    var element_names = spt.table.get_element_names();
    element_names = element_names.join(",");

    // actually do the update
    var server = TacticServerStub.get_master();

    // use the edit command to understand what do do with the update data
    var layout = spt.table.get_layout()
    var class_name = layout.getAttribute("spt_save_class_name");
    if (class_name == null) {
        class_name = 'tactic.ui.panel.EditMultipleCmd';
    }



    var layout_top = layout.getParent(".spt_layout_top")
    var edit_view = null;
    if (layout_top) {
        var edit_view = layout_top.getAttribute("spt_edit_view");
    }
    if (!edit_view) {
        var edit_view = "edit_item";
    }


    var config_xml = layout.getAttribute("spt_config_xml");

    var kwargs2 = {
        parent_key: parent_key,
        search_keys: search_keys,
        view: edit_view,
        element_names: element_names,
        input_prefix: '__NONE__',
        update_data: JSON.stringify(update_data),
        extra_data: JSON.stringify(extra_data),
        extra_action: JSON.stringify(extra_action),
        connect_key: connect_key,
        trigger_mode: kwargs.trigger_mode,
        config_xml: config_xml,
    }


    // add to the values here for gantt and inline elements
    web_data = JSON.stringify(web_data);

    var search_top = null;
    var table = spt.table.get_table();

    var search_dict = {};
    var view_panel = table.getParent('.spt_view_panel[table_id=' + table.id + ']' );
    if (view_panel) {
        search_top = view_panel.getElement('.spt_search');
        search_dict = spt.table.get_search_values(search_top);

    }

    var layout_top = table.getParent(".spt_layout_top");
    var expand_on_load = true;
    if (layout_top) {
        expand_on_load = layout_top.getProperty("spt_expand_on_load");
    }

    try {
        var result = server.execute_cmd(class_name, kwargs2, {'web_data': web_data});
        var info = result.info;
        if (info) {
            // temp set the search keys in the row
            for (var index = 0; index < rows.length; index++) {
                rows[index].setAttribute("spt_search_key_v2", search_keys[index])
            }

            var rtn_search_keys = info.search_keys;
            if (!rtn_search_keys) {
                rtn_search_keys = search_keys;
            }

            if (do_refresh ) {
                var kw = {refresh_bottom : true, json: search_dict, expand_on_load: expand_on_load};
                spt.table.refresh_rows(rows, rtn_search_keys, web_data, kw);
            }
        }


    } catch(e) {
        spt.error(spt.exception.handler(e));
    }

    // fire an event
    if (search_keys) {
        var search_key = search_keys[0];
        var parts = server.split_search_key(search_key);
        var tmps = parts[0].split('?');
        var search_type = tmps[0];
        var event = "update|" + search_type;

        var input = {
            kwargs: kwargs2,
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


    var on_complete = kwargs.on_complete;
    if (on_complete) {
        on_complete(search_keys);
    }


    return search_keys;
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
    var order_by = table_top.getAttribute("spt_order_by");

    var group_elements = spt.table.get_group_elements();

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
        config_xml: config_xml,
        order_by: order_by
    }

    return kwargs
}





spt.table.refresh_rows = function(rows, search_keys, web_data, kw) {

    // put some protection here
    if (!rows) return;
    if (rows.length == 0) return;
    if (!rows[0]) return;


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

    var expand_on_load = kw.expand_on_load;
    if (expand_on_load == null) expand_on_load = true;

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

    //var extra_data = layout_el.getAttribute("spt_extra_data");
    var inner = layout_el.getElement(".spt_layout_inner");
    if (inner) {
        var extra_data = inner.getAttribute("spt_extra_data");
    }
    else {
        var extra_data = layout_el.getAttribute("spt_extra_data");
    }


    var table_top = layout_el.getParent('.spt_table_top');
    //note: sometimes table_top is null
    if (table_top) {
        if (!config_xml) config_xml = table_top.getAttribute("spt_config_xml");
        var show_select = table_top.getAttribute("spt_show_select");
        var document_mode = table_top.getAttribute("spt_document_mode");
    }
    else {
        var show_select = null;
        var document_mode = false;
    }

    //var show_select = table_top ? table_top.getAttribute("spt_show_select") : true;

    var server = TacticServerStub.get();

    var group_elements = spt.table.get_group_elements();

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
        document_mode: document_mode,
        element_names: element_names,
        group_elements: group_elements,
        config_xml: config_xml,
        expand_on_load: expand_on_load,
        extra_data: extra_data
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

            var dummy = document.createElement("div");
            // behaviors are only process when in the actual dom
            //spt.behavior.replace_inner_html(dummy, widget_html);
            dummy.innerHTML = widget_html;
            
            // HACK for tile layout 
            dummy = spt.behavior.clone(dummy);

            if (['false', "False", false].indexOf(expand_on_load) > -1) {
                spt.table.expand_table();
            }



            var new_rows = dummy.getElements(".spt_table_row");
            // the insert row is not included here any more
            for (var i = 0; i < new_rows.length; i++) {
                // remove the hidden row, if there is one
                if (!rows[i]) continue;

                spt.table.remove_hidden_row( rows[i] );

                // replace the new row
                new_rows[i].inject( rows[i], "after" );


                // now create new behaviors for new innerHTML under "el" element ...
                var bvr_el_list = new_rows[i].getElements( ".SPT_BVR" );
                spt.behavior._construct_behaviors( bvr_el_list );

                // destroy the old row
                rows[i].destroy();


            }


            var header_table = spt.table.get_header_table();
            var header_row = header_table.getElement(".spt_table_header_row");
            var headers = header_row.getElements(".spt_table_header");

            var row = spt.table.get_first_row();

            if (row) {
                var cells = row.getElements(".spt_cell_edit");

                // set the row widths to that of the header
                for (var i = 0; i < cells.length; i++) {
                    var width = headers[i].getStyle("width");
                    cells[i].setStyle("width", width);
                }
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


    var group_elements = spt.table.get_group_elements();

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
    //spt.behavior.replace_inner_html(data, widget_html);
    data.innerHTML = widget_html;

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

    // Add edit widgets to table layout template
    var layout_edit_top = layout.getElement(".spt_edit_top");
    var data_edit_top = data.getElement(".spt_edit_top");
    var data_edit_wdgs;
    if (data_edit_top){
        data_edit_wdgs = data_edit_top.getElements(".spt_edit_widget");
    }

    // add the headers
    var cells = data_header_row.getElements(".spt_table_header");
    for (var j = 0; j < cells.length; j++) {

         if (mode=='add') {
             header_row.appendChild(cells[j]);
             if (data_edit_wdgs && data_edit_wdgs[j]) {
                layout_edit_top.appendChild(data_edit_wdgs[j]);
             }
         }
         else if (mode=='refresh') {
             var idx = col_indices[j];
             var tgt_cell = header_row.getElements(".spt_table_header")[idx];
             cells[j].inject(tgt_cell, "after");
             tgt_cell.destroy();
         }

         spt.behavior.init_behaviors(cells[j]);
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


    // add the cells
    for ( var i = 0; i < rows.length; i++ ) {
        if (i == data_rows.length) {
            spt.alert("Not enough data to fill all rows");
            break;
        }

        var cells = data_rows[i].getElements(".spt_cell_edit");

        if (i == 0 ) {
            var cur_cells = rows[i].getElements(".spt_cell_edit");
            var last_cell = cur_cells[cur_cells.length-1];
            var header_cell = spt.table.get_header_by_cell(last_cell);
            var element_name = header_cell.getAttribute("spt_element_name");
            spt.table.set_column_width(element_name, 100);

        }

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
            spt.behavior.init_behaviors(cells[j]);
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

                    spt.behavior.init_behaviors(cells[j]);
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


    var group_rows = spt.table.get_group_rows();
    for (var i = 0; i < group_rows.length; i++) {
        var row = group_rows[i];
        var td = row.getElement("td");
        var colspan = td.getAttribute("colspan");
        colspan = parseInt(colspan);
        td.setAttribute("colspan", colspan-1);
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


    // get the rows after the group
    var last_row = group_row;
    var idx = last_row.getAttribute('idx')
    var reg_row = false;
    var previous_state = 'open';

    if (group_row.getAttribute("spt_table_state") == 'closed') {
        group_row.setAttribute("spt_table_state", "open");
        show = true;
    }
    else {
        group_row.setAttribute("spt_table_state", "closed");
        show = false;
    }

   var sub_row = last_row.getNext();

   var group_level = last_row.getAttribute("spt_group_level")

   if (group_level) {
        group_level = parseInt(group_level);

    }
    else {
       group_level = 0;
    }

    while(1) {
        var row = last_row.getNext();



        if (row == null) {
            break;
        }

       var row_level = row.getAttribute("spt_group_level")

       if (row_level) {
          row_level = parseInt(row_level);

       }
       else {

           row_level = 0;
       }

        var break_cond =  idx == '0' ?  row.getAttribute('idx') == idx : row.getAttribute('idx') < idx ;
        var break_cond2 = row.getAttribute('idx') == idx


        if (row_level <= group_level) {

           break;

        }

        reg_row = true;

        if (show) {

           if (row.getAttribute('spt_table_state') == 'closed') {

              spt.show(row);
              previous_state = 'closed';

           }

           else if (row.getAttribute('spt_table_state') == 'open') {

                 previous_state = 'open';

                 spt.show(row);

           }

           else {

                if (previous_state == 'closed') {
                   spt.hide(row);

                }

                else {
                   spt.show(row);
                }


           }


        }
        else  {
            spt.hide(row);
        }


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


/**
 *
 * Get child rows in the form of nested tuples and lists
 *
 * @return array    tuple, in the form of (group, list of children)
 *
 * e.g.
 *
 * (src_el,
 *     [(group,
 *         [(group,
 *             [row]),
 *         row,
 *         row]),
 *     row,
 *     (group,
 *         [row])
 * ])
 *
 */


spt.table.get_child_rows = function(src_el) {
    if (!src_el.hasClass("spt_table_row_item")) {
        var row = src_el.getParent(".spt_table_row_item");
    } else {
        var row = src_el;
    }

    if (!row.hasClass("spt_table_group_row") && !row.hasClass("spt_group_row")) {
        return row;
    } else {
        var top_level = row.getAttribute("spt_group_level");
        var tuple = [src_el, []];
        var stack = [tuple];
        while (true) {
            var group_level = row.getAttribute("spt_group_level");
            var next = row.getNext(".spt_table_row_item");
            if (!next || next.getAttribute("spt_group_level") <= top_level) {
                break;
            }

            if (next.getAttribute("spt_group_level") <= parseInt(group_level)) {
                var diff = parseInt(group_level) - next.getAttribute("spt_group_level");
                for (let i=0; i<diff+1; i++) {
                    stack.pop();
                }
            }

            if (!next.hasClass("spt_table_group_row")) var new_item = next;
            else var new_item = [next, []];

            var curr_tuple = stack[stack.length-1];
            var curr_list = spt.table.get_child_rows_tuple(curr_tuple, true);
            curr_list.push(new_item);

            stack.push(new_item);

            row = next;
        }
        return tuple;
    }
}

/**
 *
 * Get child rows in the form of nested tuples and lists
 *
 *
 * @param array    tuple, in the form of (group, list of children)
 *                        see spt.table.get_child_rows for an example
 * @param boolean  attribute    determines whether the first or second part of the tuple is returned
 *                              true: list of children is returned
 *                              false: group is returned
 *
 */

spt.table.get_child_rows_tuple = function(tuple, attribute) {
    if (tuple.length != 2) spt.alert("Child row tuples must contain 2 elements");

    if (attribute) return tuple[1]
    else return tuple[0]
}


spt.table.get_parent_groups = function(src_el, level) {

    if (!src_el.hasClass("spt_table_row_item")) {
        var row = src_el.getParent(".spt_table_row_item");
    } else {
        var row = src_el;
    }

    if (row == null) {
        return [];
    }

    var group_level = row.getAttribute("spt_group_level");
    var group_parents = [];
    var lowest_group_level = group_level;

    while (true) {
         // get previous group
        var row = row.getPrevious(".spt_table_row_item");
        if (!row)
            break;
        // check if level is greater than lowest level reached
        if ( row.getAttribute("spt_group_level") >= lowest_group_level ){
            continue;
        }
        // set new lowest_group_level, check if its equal to level
        lowest_group_level = row.getAttribute("spt_group_level");
        if (level && level == row.getAttribute("spt_group_level")) {
            return row;
        } else if (!level) {
            group_parents.push(row);
        }
    }

    return group_parents;
}




// setting width of columns

spt.table.set_column_width = function(element_name, width) {
    var table = spt.table.get_table();
    var header_table = spt.table.get_header_table();

    var row = spt.table.get_first_row();
    if (!row)
        return;

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

        // ignore floating columns
        if (header.getStyle("position", "absolute")) {
            continue;
        }

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


    }

    var curr_header = spt.table.get_header_by_cell(cell);
    if (total_width) {
        /*
        header_table.setStyle("width", total_width);
        table.setStyle("width", total_width);
        subtable = table.getElement(".spt_table_table");
        if (subtable) {
            subtable.setStyle("width", total_width);

        }
        */
    }

    curr_header.setStyle("width", width);
    curr_header.setAttribute("last_width", width);
    cell.setStyle("width", width);
    cell.setAttribute("last_width", width);



    var insert_cell = spt.table.get_insert_row_cell(element_name);
    if (insert_cell)
        insert_cell.setStyle("width", width);

}



spt.table.set_column_widths = function(widths) {

    var element_names = spt.table.get_element_names();
    if (Number.isInteger(widths) ) {
        var width = widths;
        widths = [];
        element_names.forEach( function(element_name) {
            widths.push(width);
        } );
    }


    var index = 0;
    widths.forEach( function(width) {
        var element_name = element_names[index];
        spt.table.set_column_width(element_name, width);

        index += 1;
    } )

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



// aligne the column widths between the header and the first row
spt.table.align_column_widths = function() {
    var header_table = spt.table.get_header_table();
    var header_row = header_table.getElement(".spt_table_header_row");
    var headers = header_row.getElements(".spt_table_header");

    var row = spt.table.get_first_row();
    if (!row)
        return;

    var cells = row.getElements(".spt_cell_edit");

    // set the row widths to that of the header
    for (var i = 0; i < cells.length; i++) {
        var width = headers[i].getStyle("width");
        cells[i].setStyle("width", width);
    }
}

spt.table.expand_table = function(mode) {

    if (!mode) {
        mode = "full";
    }

    var layout = spt.table.get_layout();
    var version = layout.getAttribute("spt_version");
    var headers;
    var table = null;
    var subtable = null;
    var header_table = null;

    spt.table.set_layout(layout);
    table = spt.table.get_table();

    // if there is a subtable, then use that instead
    var subtable = table.getElement(".spt_table_table");

    var expand_last_column = true;
    if (subtable) {
        table = subtable;
        expand_last_column = false;
    }

    headers = spt.table.get_headers();
    header_table = spt.table.get_header_table();


    var layout_width = layout.getSize().x;
    var width = header_table.getStyle("width");

    // don't set the width of each column, this is simpler
    if ( mode == "free") {

        if (header_table) {

            var total_width = 0;

            // remove the widths of all the cells
            var cells = header_table.getElements("th");
            cells.forEach( function(cell) {

                var last_width = cell.getAttribute("last_width");

                // if this is the last cell
                if (expand_last_column && cell == cells[cells.length-1] && total_width < layout_width - 120) {
                    cell.setStyle("width", layout_width-total_width)
                }

                else if (last_width && last_width != "-1") {
                    cell.setStyle("width", last_width);
                }
                else {
                    var size = cell.getSize();
                    if (size.x) {
                        cell.setStyle("width", size.x);
                    }
                    else {
                        cell.setStyle("width", "100px");
                    }
                }

                var size = cell.getSize();
                total_width += size.x;
            })
            //header_table.setStyle("width", "0px");
            header_table.setStyle("width", "max-content");


        }
        if (table) {

            var total_width = 0;

            var rows = spt.table.get_all_rows();
            rows.forEach( function(row) {
                var cells = row.getElements(".spt_cell_edit");
                cells.forEach( function(cell){

                    var last_width = cell.getAttribute("last_width");

                    if (cell.hasClass("spt_table_select") ) {
                        return;
                    }


                    // if this is the last cell
                    if (expand_last_column && cell == cells[cells.length-1] && total_width < layout_width - 120) {
                        cell.setStyle("width", layout_width-total_width)
                    }
                    else if (last_width && last_width != "-1") {
                        cell.setStyle("width", last_width);
                    }
                    else {
                        var size = cell.getSize();
                        if (size.x) {
                            cell.setStyle("width", size.x);
                        }
                        else {
                            cell.setStyle("width", "100px");
                        }
                    }

                    var size = cell.getSize();
                    total_width += size.x;

                })
            })


            //table.setStyle("width", "0px");
            table.setStyle("width", "max-content");



        }
    }
    else {

        if (header_table) {
            header_table.setStyle("width", "100%");

            // remove the widths of all the cells
            var cells = header_table.getElements("th");
            cells.forEach( function(cell) {
                var last_width = cell.getAttribute("last_width");
                if (!last_width) {
                    cell.setStyle("width", "");
                }
           })

        }
        if (table) {
            table.setStyle("width", "100%");

            var rows = spt.table.get_all_rows();
            rows.forEach( function(row) {
                var cells = row.getElements("spt_cell_edit");
                cells.forEach( function(cell) {

                    if (cell.hasClass("spt_table_select") ) {
                        return;
                    }

                    var last_width = cell.getAttribute("last_width");
                    if (!last_width) {
                      cell.setStyle("width", "");
                    }
                })
            })

        }


        /*
        if (subtable) {
            subtable.setStyle("width", "100%");

            var rows = spt.table.get_all_rows();
            rows.forEach( function(row) {
              var cells = row.getElements("td");
              cells.forEach( function(cell){
                  cell.setStyle("width", "");
              })
            })

        }
        */


        layout.setStyle("width", "100%");


    }


    // adjust for windows scrollbar
    if (spt.browser.os_is_Windows() && table) {
        var div = layout.getElement(".spt_header_padding");
        if (div) {
            spt.behavior.destroy_element(div);
        }


        var header_size = header_table.getSize();
        var table_size = table.getSize();

        if (header_size.x > table_size.x) {
            header_parent = header_table.getParent();
            header_parent.setStyle("margin-right", "8px");

            var div = document.createElement("div");
            div.setStyle("width", "8px");
            div.innerHTML = "&nbsp;";
            div.addClass("spt_header_padding");

            var height = header_parent.getStyle("height");
            div.setStyle("height", height);
            div.setStyle("background", "#F5F5F5");
            div.setStyle("position", "absolute")
            div.setStyle("right", "0px")


            div.setStyle("box-sizing", "border-box");
            div.setStyle("border-right", "solid 1px #DDD")

            div.inject(header_parent, "before");
        }
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
    spt.table.set_layout(layout);

    spt.table.expand_table("free");


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
}

spt.table.drag_resize_header_action = function(evt, bvr, mouse_411) {
    spt.table.smallest_size = -1;
    spt.table.resize_div = null;

    spt.table.drag_init();

    var resize_cbjs = bvr.resize_cbjs || "";
    Function("evt", "bvr", "mouse_411", "'use strict';" + resize_cbjs)(evt, bvr, mouse_411);
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
    clone.setStyle("z-index", "100");
    clone.setStyle("left", mouse_411.curr_x-layout_pos.x+5);
    clone.setStyle("top", mouse_411.curr_y-layout_pos.y+5);
    clone.setStyle("width", size.x);
    clone.setStyle("max-width", "200px");
    clone.setStyle("min-height", "30px");
    clone.setStyle("background", "#CCC");
    clone.setStyle("border", "solid 1px black");


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
    //clone.setStyle("top", clone_pos.y+5);

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
            handle.setStyle("background-color", "#333");
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

    spt.table.expand_table("free");

    var reorder_cbjs = bvr.reorder_cbjs || "";
    Function("evt", "bvr", "mouse_411", "'use strict';" + reorder_cbjs)(evt, bvr, mouse_411);
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
        'search_key': search_key,
        'input_prefix': 'edit',
        'view': edit_view,
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

spt.table.delete_rows = function(rows, args) {
    if (!args) args = {};

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

    var on_post_delete = args.on_post_delete;
    if (!on_post_delete) {
        on_post_delete = function() {
            var on_complete = function(id) {
                spt.behavior.destroy_element(document.id(id));
                spt.table.align_column_widths();
            }
            for (var i = 0; i < rows.length; i++) {
                var row = rows[i];
                row.addClass("spt_removed");
                if (layout.getAttribute("spt_version") == "2") {
                    spt.table.remove_hidden_row(row);
                }
                Effects.fade_out(row, 500, on_complete);
            }

            spt.table.align_column_widths();

        }
    }

    popup.spt_on_post_delete = on_post_delete;

    return;
}


spt.table.remove_rows = function(rows, args) {
    if (!args) args = {};

    var layout = spt.table.get_layout();
    var on_complete = function(id) {
        spt.behavior.destroy_element(document.id(id));
    }
    for (var i = 0; i < rows.length; i++) {
        var row = rows[i];
        row.addClass("spt_removed");
        if (layout.getAttribute("spt_version") == "2") {
            spt.table.remove_hidden_row(row);
        }
        if (args.no_animation) spt.behavior.destroy_element(row);
        else Effects.fade_out(row, 500, on_complete);
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

                if (action == 'retire') {
                    var retire_key = selected_rows[i].getAttribute("SPT_RET_API_KEY");
                    server.set_api_key(retire_key);
                    server.retire_sobject(search_key);
                } else if (action == 'delete') {
                    var del_key = selected_rows[i].getAttribute("SPT_DEL_API_KEY");
                    server.set_api_key(del_key);
                    server.delete_sobject(search_key);
                }
                server.clear_api_key();
            }
        }
        catch(e) {
            // TODO: do nicer error message for user
            spt.alert("Error: " + spt.exception.handler(e));
            server.abort();
            aborted = true;
        }

        server.finish()

        spt.table.align_column_widths();

        if( ! aborted ) {
            if( show_retired ) {
                spt.table.refresh_rows(selected_rows);
            }
            else {
                for (var i=0; i < selected_rows.length; i++)
                {
                    var row = selected_rows[i];
                    on_complete = "spt.behavior.destroy_element(document.id(id))"
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



// Search methods

spt.table.save_search = function(search_view, kwargs) {

    if (!kwargs) {
        kwargs = {};
    }

    var layout = spt.table.get_layout();
    var search_type = layout.getAttribute("spt_search_type");

    var top = layout.getParent(".spt_view_panel");
    var search_top = top.getElement(".spt_search");

    var json_values = spt.table.get_search_values(search_top);


    var options = {
        'search_type': search_type,
        'display': 'block',
        'view': search_view,
        'unique': kwargs.unique,
        'personal': kwargs.personal
    };

    // replace the search widget
    var server = TacticServerStub.get();

    var class_name = "tactic.ui.app.SaveSearchCbk";
    server.execute_cmd(class_name, options, json_values);

}



spt.table.load_search = function(search_view, kwargs) {
    var layout = spt.table.get_layout();
    var search_type = layout.getAttribute("spt_search_type");

    // maybe easier just to refresh the entire widget with a new
    // search
    var top = layout.getParent(".spt_view_panel_top");
    top.setAttribute("spt_search_view", search_view);

    // keep any changes that have been made to the element names
    var element_names = spt.table.get_element_names();
    element_names = element_names.join(",");
    top.setAttribute("spt_element_names", element_names);

    spt.panel.refresh(top, {}, { callback: function() {
        var layout = top.getElement(".spt_layout");
        spt.table.set_layout(layout);
    } } );

    return;
}



/*
 * Saving views
 */



// Callback that gets executed when "Save My/Project View As" is selected
spt.table.save_view_cbk = function(table_id, login) {
   
    var table = document.id(table_id);
    var top = table.getParent(".spt_view_panel");
    // it may not always be a View Panel top
    if (!top) top = table.getParent(".spt_table_top");
    
    //var search_wdg = top.getElement(".spt_search");

    // TODO: Will this break on embedded tables now?????  Maybe not
    // because the first instance is probably what we want ... however,
    // a little tenous
    //var view_info = top.getElement(".spt_save_top");
    var view_info = top.getElement(".spt_new_view_top");

    var values;
    if (view_info != null) {
        values = spt.api.Utility.get_input_values(view_info , null, false);
    }
    else {
        // NOTE: this is deprecated
        var aux_content = top.getElement(".spt_table_aux_content")
        values = spt.api.Utility.get_input_values(aux_content , null, false);
    }
    // rename view
    var new_view = values["save_view_name"];
    var new_title = values["save_view_title"];
    var same_as_title = values["same_as_title"] == 'on';
    //var save_a_link = values["save_a_link"] == 'on';
  
    var save_mode = values['save_mode'];
    if (!save_mode) {
        var save_project_views = values['save_project_views'] == 'on';
        if (save_project_views) {
            save_mode = 'save_project_views';
        }
        var save_my_views = values['save_my_views'] == 'on';
        if (save_my_views) {
            save_mode = 'save_my_views';
        }
        var save_view_only = values['save_view_only'] == 'on';
        if (save_view_only) {
            save_mode = 'save_view_only';
        }
    }

    if (same_as_title) {
        new_view = new_title;
    }

    if (spt.input.has_special_chars(new_view)) {
        spt.alert("The name contains special characters. Do not use empty spaces.");  
        return;
    }
    if (new_view == "") {
        spt.alert("Empty view name not permitted");
        return;
    }
    
    if ((/^(saved_search|link_search)/i).test(new_view)) {
        spt.alert('view names starting with these words [saved_search, link_search] are reserved.');
        return;
    }
    var table = document.getElementById(table_id);
    if (!table) {
        spt.alert('This command requires a Table in the main viewing area');
        return;
    }
    var table_search_type = table.getAttribute("spt_search_type");
    var table_view = table.getAttribute("spt_view");
    var last_element = top.getAttribute("spt_element_name");


    var kwargs = {'login' : login, 'new_title' : new_title, 
        'element_name': new_view,
        'last_element_name': last_element,
        'save_mode': save_mode,
    } 

    spt.app_busy.show( 'Saving View', new_title );
    var rtn = spt.table.save_view(table_id, table_view, kwargs);
    spt.app_busy.hide();

    if (!rtn)
        return;
    
    return true;
}

//verify matching spt_view
// NOTE: this is not really used anymore
spt.table.is_embedded = function(table){
    var top = table.getParent(".spt_view_panel");
    // top is null if it's a pure Table Layout
    if (!top) return false;

    var panel_table_view = top.getAttribute('spt_view');
    var table_view = table.getAttribute('spt_view');
    var panel_search_type = top.getAttribute("spt_search_type");
    var table_search_type = table.getAttribute("spt_search_type");
     
    var is_embedded = false;
    if (panel_table_view != table_view || panel_search_type != table_search_type) {
        //spt.alert('Embedded table view saving not supported yet');
        is_embedded = true;
       
    }
    return is_embedded;
}

spt.table.simple_save_view = function (table, view_name, kwargs) {
    try {
        if (typeOf(table) == "string") {
            table = document.id(table);
        }

        var top = table.getParent(".spt_view_panel");
        var layout = top ? top.getAttribute('spt_layout'): null;
        var search_wdg = kwargs.search_top? kwargs.search_top :  (top ? top.getElement(".spt_search"): null);

        // save search view
        if (search_wdg) {
            var search_view = 'link_search:'+ view_name;
            // auto generate a new search for this view
            search_wdg.setAttribute("spt_search_view", search_view);
            spt.table.save_search(search_wdg, search_view, {});
        }


        // save view

        //raw and static_table layout has no checkbox in the first row
        var first_idx = 1;
        if (['raw_table','static_table'].contains(layout))
            first_idx = 0;

        spt.dg_table.get_size_info(table, view_name, null, first_idx, {extra_data: kwargs.extra_data, save_definitions: true});

    } catch(e) {
        spt.alert(spt.exception.handler(e));
        return false;
    }
    return true;
}

spt.table.save_view = function(table, new_view, kwargs) {

    var server;
    try {
        if (typeOf(table) == "string") {
            table = document.id(table);
        }

        var top = table.getParent(".spt_view_panel");
        var search_wdg = top ? top.getElement(".spt_search"): null;

        var save_mode = kwargs['save_mode'];
 
        if (spt.table.is_embedded(table)) {
            //spt.alert('Embedded table view saving not supported yet');
            var login = kwargs.login;
            spt.dg_table.get_size_info(table, new_view, login);
            return false;
        }
        
        var table_search_type = table.getAttribute("spt_search_type");


        var dis_options = {};


        var login = kwargs.login;
        var save_as_personal = (save_mode == 'save_my_views') ? true : false;


        var side_bar_view = 'project_view';
        if (save_as_personal) {
            side_bar_view = 'my_view_' + login;
        }

        // start a transaction
        var server = TacticServerStub.get();
        var title = side_bar_view + " updated from: " + new_view;
        server.start({"title": "Saving View", "description": "Saving View: " +  title});
      
        var element_name = new_view;
        var unique = kwargs.unique;

        // Save My View allows to save over the current view if it is already a personal view
        // or if the user is admin, he can save over anything
        if (kwargs.element_name ) {
            element_name = kwargs.element_name;
        }
        var new_title = kwargs.new_title;


        var last_element_name = kwargs.last_element_name;

        // If it is saving as a new personal view, we try to append login name
        if (save_as_personal) {
            //only do this to search_view to make it easier to retrieve a search for my_view_<user>
            if (login && !(/\./).test(element_name) ) {
                element_name = login + '.' + element_name;
            }
        }

        var custom_search_view = null;
        if (search_wdg) {
            var search_view = 'link_search:'+ element_name;
            // auto generate a new search for this view
            search_wdg.setAttribute("spt_search_view", search_view);
            spt.table.save_search(search_wdg, search_view, {'unique': kwargs.unique, 'personal': save_as_personal});

            custom_search_view = search_wdg.getAttribute('spt_custom_search_view');
        }
        // add to the project views
        var search_type = "SideBarWdg";
        var class_name = "LinkWdg";
       
        var simple_search_view = top ? top.getAttribute('spt_simple_search_view'): null;
        var insert_view = top ? top.getAttribute('spt_insert_view'): null;
        var edit_view = top ? top.getAttribute('spt_edit_view'): null;
        var layout = top ? top.getAttribute('spt_layout'): null;
      
      
        dis_options['search_type'] = table_search_type;
        dis_options['view'] = element_name;
        dis_options['search_view'] = search_view;
        if (custom_search_view)
            dis_options['custom_search_view'] = custom_search_view;
        if (simple_search_view)
            dis_options['simple_search_view'] = simple_search_view;
        if (insert_view)
            dis_options['insert_view'] = insert_view;
        if (edit_view)
            dis_options['edit_view'] = edit_view;
        if (layout)
            dis_options['layout'] = layout;
        
        // redefine kwargs
        var kwargs = {};
        kwargs['login'] = null;
        if (save_as_personal) 
            kwargs['login'] = login;
        kwargs['class_name'] = class_name; 
        kwargs['display_options'] = dis_options;
        
        kwargs['unique'] = unique;


        // these are the server oprations


        // Copy the value of the "icon" attribute from the previous XML widget
        // config.
        var icon = null;
        if (last_element_name) {
            var widget_config_before = server.get_config_definition(search_type, "definition", last_element_name);
            // Skip if there is no previous matching XML widget config.
            if (widget_config_before != "") {
                xmlDoc = spt.parse_xml(widget_config_before);
                var elem_nodes = xmlDoc.getElementsByTagName("element");

                if (elem_nodes.length > 0) {
                    var attr_node = elem_nodes[0].getAttributeNode("icon")

                    // Skip if there is no icon to copy over from the old link.
                    if (attr_node != null) {
                        icon = attr_node.nodeValue;
                    }

                    // keep title
                    if ( save_mode == 'save_view_only' ) {
                        var title_node = elem_nodes[0].getAttributeNode("title")
                        if (title_node)
                            new_title = title_node.nodeValue;
                    }

                }
            }
        }


        if (new_title)
            kwargs['element_attrs'] = {'title': new_title, 'icon': icon}; 

        // add the definiton to the list
        var info = server.add_config_element(search_type, "definition", element_name, kwargs);
        var unique_el_name = info['element_name'];
        
        //raw and static_table layout has no checkbox in the first row
        var first_idx = 1;
        if (['raw_table','static_table'].contains(layout))
            first_idx = 0;

        // create the view for this table
        spt.dg_table.get_size_info(table, unique_el_name, kwargs.login, first_idx);
         
        //if (side_bar_view && save_a_link) {
        if (save_mode != 'save_view_only') {
            var kwargs2 = save_as_personal ? {'login': login } : {};
           
            server.add_config_element(search_type, side_bar_view, unique_el_name, kwargs2);
        }
        server.finish();

        spt.panel.refresh("side_bar");
    } catch(e) {
        if (server) server.abort();
        
        spt.alert(spt.exception.handler(e));
        return false;
    }
    return true;
    
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
        var panel;
        var top_class = search_top.getAttribute("spt_top_class");
        if (top_class) {
            var top = search_top.getParent("." + top_class);
            if (top) {
                panel = top.getElement(".spt_view_panel");
            }
        }
        panel = panel? panel : search_top.getParent(".spt_view_panel");

        if (panel) {
            var table_searches = panel.getElements(".spt_table_search");
            for (var i = 0; i < table_searches.length; i++) {
                var table_search = table_searches[i];
                var values = spt.api.Utility.get_input_values(table_search,null,false);
                new_values.push(values);
            }
        }
    }

    // convert to json
    var json_values = JSON.stringify(new_values);
    return json_values;

}



spt.table.save_search = function(search_wdg, search_view, kwargs) {

    var json_values = spt.table.get_search_values(search_wdg);

    // build the search view
    var search_type = search_wdg.getAttribute("spt_search_type");

    /*
    var view_text = document.id('save_search_text');
    if (search_view == undefined) {
        search_view = view_text.value;
    }
    */
    if (search_view == "") {
        search_view = search_wdg.getAttribute("spt_search_view");
    }

    if (search_view == "") {
        spt.alert("No name specified for saved search");
        return;
    }


    var options = {
        'search_type': search_type,
        'display': 'block',
        'view': search_view,
        'unique': kwargs.unique,
        'personal': kwargs.personal
    };

    // replace the search widget
    var server = TacticServerStub.get();

    var class_name = "tactic.ui.app.SaveSearchCbk";
    server.execute_cmd(class_name, options, json_values);

    /*
    if (document.id('save_search_wdg'))
        document.id('save_search_wdg').style.display = 'none';
    */


}






/*
 * Export to CSV tools
 */

spt.table.export = function(mode) {

    var bvr = {};
    bvr.mode = mode;

    var layout = spt.table.get_layout();
    var table = spt.table.get_table();

    var search_type = table.get("spt_search_type");
    var view = table.get("spt_view");
    var search_values_dict;
    spt.table.set_layout(layout);
    var header = spt.table.get_header_row();
    // include header input for widget specific settings
    var header_inputs = spt.api.Utility.get_input_values(header, null, false);
    search_values_dict = header_inputs;


    var element_names = spt.table.get_element_names();

    var search_class = table.get("spt_search_class") || "";

    var tmp_bvr = {};

    var search_view;
    // init the args to be passed to CsvExportWdg
    tmp_bvr.args = {
        'table_id': table.get('id'),
        'search_type': search_type,
        'selected_search_keys': '',
        'view': view,
        'element_names': element_names,
        'search_class': search_class,
        'mode': bvr.mode,
        'search_view': search_view
    };

    var title = '';
    var sel_search_keys = [];
    if( bvr.mode=='export_all' ) {
        tmp_bvr.args.is_export_all = true;
        title = 'Export All items from "' + search_type + '" list ';
    }
    else if (bvr.mode=='export_matched') {
        title = 'Export Matched items from "' + search_type + '" list ';
        var top = table.getParent(".spt_view_panel");

        var search_wdg;
        if (top) {
            search_wdg = top.getElement(".spt_search");
            var matched_search_type = search_type == top.getAttribute('spt_search_type');
            var simple_search_view  = top.getAttribute('spt_simple_search_view');
            search_view = search_wdg.getAttribute("spt_view");
            tmp_bvr.args.search_view = search_view;
            tmp_bvr.args.simple_search_view = simple_search_view;
        }
        if (!top || !search_wdg || !matched_search_type) {
            spt.alert('The search box is not found. Please use "Export Selected, Export Displayed" instead')
            return;
        }

        var search_values = spt.table.get_search_values(search_wdg);
        search_values_dict['json'] = search_values;

    }
    else if (bvr.mode=='export_displayed') {
        title = 'Export displayed items from "' + search_type + '" list ';
        var tbodies = table.getElements(".spt_table_row");
        for (var k=0; k < tbodies.length; k++) {
            if (tbodies[k].getStyle('display') == 'none'){
                continue;
            }
            var sk = tbodies[k].getAttribute('spt_search_key');


            sel_search_keys.push(sk);
        }
        if( sel_search_keys.length == 0 ) {
            spt.alert('No rows displayed for exporting to CSV ... skipping "Export Displayed" action.');
            return;
        }
    }

    else {
        title = 'Export Selected items from "' + search_type + '" list ';
        var selected_rows = spt.table.get_selected_rows();
        var sel_search_keys = [];

        related_views = []
        for (var c=0; c < selected_rows.length; c++) {
            search_key = selected_rows[c].getAttribute("spt_search_key");
            sel_search_keys.push(search_key);

            var parent_table = selected_rows[c].getParent('.spt_table');
            var parent_view = parent_table.getAttribute('spt_view');
            if (! related_views.contains(parent_view))
                related_views.push(parent_view);
        }

        if( sel_search_keys.length == 0 ) {
            spt.alert('No rows selected for exporting to CSV ... skipping "Export Selected" action.');
            return;
        }
        if (related_views.length > 1) {
            spt.alert('More than 1 type of item is selected ... skipping "Export Selected" action.');
            return;
        }
        tmp_bvr.args.related_view = related_views[0];
    }


    var view_name = '';

    title += "in [" + view + "] view";

    tmp_bvr.options = {
        'title': title + " to CSV",
        'class_name': 'tactic.ui.widget.CsvExportWdg',
        'popup_id' : 'Export CSV'
    };
    tmp_bvr.args.selected_search_keys = sel_search_keys;
    tmp_bvr.values = search_values_dict;


    var popup = spt.popup.get_widget( {}, tmp_bvr );

    // add the search_values_dict to the popup
    popup.values_dict = search_values_dict;

}




/*
 * Dynamically load data rows through javascript
 */

spt.table.sobjects = [];

spt.table.load_data = function(sobjects) {

  if(sobjects) {
      spt.table.sobjects = sobjects;
  }
  else {
      sobjects = spt.table.sobjects;
  }

  var r_sobjects = sobjects.reverse();

  for (var i = 0; i < r_sobjects.length; i++) {

    var sobject = sobjects[i];
    var row = spt.table.add_new_item();
    var insert_row = spt.table.get_insert_row();

    // a bunch of code to dynamically "reverse" the insert state of the row
    row.setAttribute("spt_search_key", sobject.__search_key_v1__);
    row.setAttribute("spt_search_key_v2", sobject.__search_key__);
    row.setAttribute("spt_display_value", sobject.__display_value__);

    var new_el = row.getElement(".spt_select_new");
    if (new_el) new_el.destroy();


    row.setStyle("background", "#FFF");
    row.removeClass("spt_table_insert_row");
    row.addClass("spt_table_row");

/* Remove behaviors ... note this should be done on the original source.
    var bvrs = row.getElements(".SPT_BVR");
    for (var j = 0; j < bvrs.length; j++) {
        bvrs[j].removeAttribute("spt_bvr_list");
        bvrs[j].removeAttribute("spt_bvr_type_list");
        bvrs[j].removeClass("SPT_BVR");
    }
*/

    var cells = row.getElements(".spt_cell_edit");
    var insert_cells = row.getElements(".spt_cell_edit");

    for (var j = 0; j < cells.length; j++) {
        var cell = cells[j];
        var insert_cell = insert_cells[j];

        var element_name = cell.getAttribute("spt_element_name");
        var value = sobject[element_name];


        if (insert_cell.loadXYZ) {
            try {
                insert_cell.loadXYZ(element_name, cell, sobject);
            }
            catch(e) {
                console.log("Error in load data for element ["+element_name+"]");
            }
            //continue;
        }

        else if (element_name == "preview") {
            var img = cell.getElement("img");
            if (!value || value == "__no_preview__") {
                value = "/context/icons/common/no_image.png";
            }
            if (value) {
                img.setAttribute("src", value);
            }
            continue;
        }
        else {
            if (value)
                cell.getFirst().innerHTML = value;
        }


        if (value) {
            cell.setAttribute("spt_input_value",value);
        }
    }
  }

}



spt.table.clear_table = function() {
    var rows = spt.table.get_all_rows();
    for (var i = 0; i < rows.length; i++) {
        spt.behavior.destroy(rows[i]);
    }
}


spt.table.sort_sobjects = function(sobjects, column) {
    sobjects.sort( function(a,b) {
        a_value = a[column];
        b_value = b[column];
        if (a_value == null) return 1;
        if (b_value == null) return -1;

        if (a_value < b_value)
           return 1;
        if (a_value > b_value)
           return -1;
        return 0;
    } )

}







// Tools


spt.table.open_ingest_tool = function(search_type) {
    var class_name = 'tactic.ui.tools.IngestUploadWdg';
    var kwargs = {
        search_type: search_type
    };
    spt.panel.load_popup("Ingest "+search_type, class_name, kwargs);
}


// Document export (imported from document api)
spt.table.export_document = function(kwargs) {

    if (!kwargs) {
        kwargs = {};
    }

    max_group_level = kwargs.max_group_level;
    if (typeof(max_group_level) == 'undefined') {
        max_group_level = -1;
    }


    var min_group_level = kwargs.min_group_level;
    if (typeof(min_group_level) == 'undefined') {
        min_group_level = 0;
    }


    var table = spt.table.get_table()
    var rows = table.getElements(".spt_table_row_item");

    var document = {};
    document['type'] = 'table';

    // may not be necessary outside of PipeLineWdg?
    document['new_group_count'] = 0;

    var content = [];
    document['content'] = content;

    for (var i = 0; i < rows.length; i++) {

        var row = rows[i];

        // Check for clone row
        if (row.hasClass("spt_clone")) {
            break;
        }

        // Check for dynamic row
        if (row.getAttribute("spt_dynamic") == "true") continue;
        if (row.getAttribute("spt_deleted") == "true") continue;

        var group_level = row.getAttribute("spt_group_level");
        if (max_group_level != -1 && group_level > max_group_level) {
            continue;
        }
        if (group_level < min_group_level) {
            continue;
        }





        var item = {};

        if (row.hasClass("spt_table_group_row")) {
            var row_type = "group";
        }
        else if (row.hasClass("spt_table_row")) {
            var row_type = "item";
        }
        else if (row.hasClass("spt_table_insert_row")) {
            var row_type = "item";
            item["new"] = true;
        }
        else if (row.hasClass("spt_table_group_insert_row")) {
            var row_type = "group";
            item["new"] = true;
        }


        var children = row.getAttribute("spt_children");
        if (children) {
            item["children"] = children;
        }


        if (!group_level) {
            group_level = 0;
        }
        item["group_level"] = parseInt(group_level);

        if (row_type == "group") {
            if (row.getAttribute("spt_deleted") == "true") {
                break;
            }

            item["type"] = "group";

            var swap_top = row.getElement(".spt_swap_top");
            var state = swap_top.getAttribute("spt_state");
            item["state"] = state;

            var title_wdg = row.getElement(".spt_table_group_title");
            if (title_wdg) {
                var label_wdg = title_wdg.getElement(".spt_group_label");
                if (label_wdg) {
                    item["title"] = label_wdg.innerHTML;
                }
                else {
                    item["title"] = title_wdg.innerHTML;
                }
            }
        } else {

            if (kwargs.mode == "report") {
                var element_names = spt.table.get_element_names();
                var cells = row.getElements(".spt_cell_edit");
                var index = 0;
                var data = {};
                data["id"] = i;
                cells.forEach( function(cell) {
                    var element_name = element_names[index];
                    var value = cell.getAttribute("spt_report_value");
                    if (value == null) {
                        value = cell.getAttribute("spt_input_value");
                    }
                    data[element_name] = value;
                    index += 1;
                } );
                item["type"] = "sobject";
                item["sobject"] = data;
            }
            else {
                var search_key = row.getAttribute("spt_search_key_v2");
                item["type"] = "sobject";
                item["search_key"] = search_key;
            }


        }

        content.push(item);

    }


    // export state

    var layout = spt.table.get_layout();
    var els = layout.getElements(".spt_state_save");

    if (els.length != 0) {
        document.state = {};
    }

    for (var i = 0; i < els.length; i++) {
        var el = els[i];
        var state_name = el.getAttribute("spt_state_name");
        var state_data = el.getAttribute("spt_state_data");
        if (state_data != null) {
            state_data = JSON.parse(state_data);
        }
        else {
            state_data = {};
        }

        document.state[state_name] = state_data;
    }
    return document
}







            '''

        if self.kwargs.get('temp') != True:
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

            spt.table.data = {};

            spt.table.select_color = bvr.select_color;
            spt.table.shadow_color = bvr.shadow_color;
            %s
            spt.table.set_table(bvr.src_el);

            ''' %cbjs_action


        hidden_row_color = table.get_color("background3")

        table.add_behavior( {
            'type': 'load',
            'cbjs_action': self.get_onload_js()
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

    def test_relationship(self):
        search = Search("ut/asset")
        search.add_id_filter(357)
        sobject = search.get_sobject()

        related = sobject.get_related_sobjects("ut/asset")
        for sobject in related:
            print("related: ", sobject.get_value("name"))


        return


        # TODO:
        # try: many to many
        search = Search("ut/asset")
        sobjects = search.get_sobjects()
        related = Search.get_related_by_sobjects(sobjects, "ut/asset")
        for key, sobjects in related.items():
            print("relatedx: ", key, sobjects)



    def handle_sub_search(self):

        self.test_relationship()

        self.sobject_levels = []

        # main data structure
        levels_sobjects = []

        #search = Search("ut/asset")
        #search.add_id_filter(357)
        #self.sobjects = search.get_sobjects()

        current_sobjects = self.sobjects

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
                    break


                current_sobjects = []
                for name, items in level_sobjects_dict.items():
                    current_sobjects.extend(items)

            if done:
                break


        sobject_list = []

        # go through each top level sobject and find the children
        level = 0
        for sobject in self.sobjects:
            sobject_list.append(sobject)
            self.sobject_levels.append(level)

            self._collate_levels(sobject, sobject_list, levels_sobjects, level)

        self.sobjects = sobject_list




    def _collate_levels(self, sobject, sobject_list, levels_sobjects, level):

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
                self.sobject_levels.append(level)

            self._collate_levels(related_sobject, sobject_list, levels_sobjects, level+1)




# DEPRECATED: Old name
class FastTableLayoutWdg(TableLayoutWdg):
    pass


class TableGroupManageWdg(BaseRefreshWdg):

    def get_args_keys(self):
        return {
            "element_names": "list of the element_names",
            "search_type": "search_type to list all the possible columns",
            "target_id": "the id of the panel where the table is"
        }

    def init(self):
        self.group_columns = self.kwargs.get('group_by')
        self.group_columns = self.group_columns.split(',')

    def get_columns_wdg(self, title, element_names, is_open=False):

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

        search_type = self.kwargs.get("search_type")
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

            if element_name in self.group_columns:
                grouped_elements.insert(self.group_columns.index(element_name), menu_item )

            attrs = self.config.get_element_attributes(element_name)

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

        # save.add_styles("position: absolute; left: 420; top: 425")

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




    def get_display(self):
        top = self.top
        top.add_style("width: 580px")

        search_type = self.kwargs.get("search_type")
        search_type_obj = SearchType.get(search_type)


        #self.current_elements = ['asset_library', 'code']
        self.current_elements = self.kwargs.get('element_names')
        if not self.current_elements:
            self.current_elements = []



        self.target_id = self.kwargs.get("target_id")



        #popup_wdg = PopupWdg(id=self.kwargs.get("popup_id"), opacity="0", allow_page_activity="true", width="400px")
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






        self.config = WidgetConfigView.get_by_search_type(search_type, "definition")





        defined_element_names = []
        for config in self.config.get_configs():
            if config.get_view() != 'definition':
                continue
            file_path = config.get_file_path()
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
        context_menu.add( self.get_columns_wdg(title, defined_element_names, is_open=True) )




        return top
