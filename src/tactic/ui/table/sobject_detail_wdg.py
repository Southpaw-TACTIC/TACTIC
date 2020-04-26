###########################################################
#
# Copyright (c) 2005-2008, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#

__all__ = ['SObjectDetailElementWdg', 'SObjectTaskStatusElementWdg', 'TaskDetailPanelElementWdg']

from pyasm.common import Environment
from pyasm.search import SearchKey
from pyasm.web import DivWdg, HtmlElement
from pyasm.widget import IconWdg

from tactic.ui.widget import IconButtonWdg

from tactic.ui.common import BaseTableElementWdg

class SObjectDetailElementWdg(BaseTableElementWdg):
    '''The element widget that displays according to type'''

    ARGS_KEYS = {
    'tab_element_names': {
        "description": "List of element names that will be in the tab",
        'category': 'Options',
        'order': 1

    },
    'use_parent': {
        'description': 'Display the parent of this sobject for the detail',
        'type': 'SelectWdg',
        'values': 'true|false',
        'category': 'Options',
        'order': 2
    },
    'show_task_process': {
        'description': 'Determine if Add Note widget only shows the processes of existing tasks',
        'category': 'Options',
        'type': 'SelectWdg',
        'values': 'true|false',
        'order': 3
    },
    'show_default_elements': {
        "description": "Determine if the default element names should be hidden",
        'category': 'Options',
        'type': 'SelectWdg',
        'values': 'true|false',
        'order': 4
    }

    }
 
    def __init__(self, **kwargs):
        self.widget = None
        super(SObjectDetailElementWdg, self).__init__(**kwargs)

    def init(self):
        self.show_task_process = self.kwargs.get('show_task_process')

    def set_widget(self, widget):
        self.widget = widget

    def get_width(self):
        return 50




    def get_display(self):

        sobject = self.get_current_sobject()

        use_parent = self.get_option("use_parent")
        use_parent = use_parent in ['true', True]
        #if use_parent in ['true', True]:
        #    sobject = sobject.get_parent()
        #    if not sobject:
        #        return DivWdg()

        self.search_key = SearchKey.get_by_sobject(sobject)
    
        div = DivWdg()
        div.add_class("hand")
        target_id = "main_body"

        mode = self.get_option("mode")
        #mode = "link"

        title = "Show Item Details"
        if self.widget:
            widget = self.widget
        elif mode == "link":
            widget = HtmlElement.href()
            column = self.get_option("link_column")
            if not column:
                column = "code"
            widget.add( sobject.get_value(column) )
            widget.add_style('text-decoration: underline')
        else:
            #widget = IconButtonWdg(title=title, icon=IconWdg.ZOOM)
            widget = IconButtonWdg(title=title, icon="BS_SEARCH")
            div.add_style("width: 26px")
            div.add_style("margin-left: auto")
            div.add_style("margin-right: auto")



        code = sobject.get_code()
        name = sobject.get_value("name", no_exception=True)
        if not name:
            name = code


        search_type_obj = sobject.get_search_type_obj()
        title = search_type_obj.get_title()
        if not title:
            title = "Detail"
        title = _(title)


        tab_element_names = self.kwargs.get("tab_element_names") or ""
        detail_view = self.kwargs.get("detail_view") or ""
        
        show_default_elements = "true"
        if self.kwargs.get("show_default_elements") in ['false', False]:
            show_default_elements = "false"

        widget.add_behavior( {
        'type': 'click_up',
        'search_key': self.search_key,
        'use_parent': use_parent,
        'tab_element_names': tab_element_names,
        'detail_view': detail_view,
        'show_task_process': self.show_task_process,
        'show_default_elements': show_default_elements,
        'code': code,
        'name': name,
        'label': title,
        'cbjs_action': '''
        spt.tab.set_main_body_tab();
        var class_name = 'tactic.ui.tools.SObjectDetailWdg';
        var kwargs = {
            search_key: bvr.search_key,
            use_parent: bvr.use_parent,
            tab_element_names: bvr.tab_element_names,
            show_task_process: bvr.show_task_process,
            detail_view: bvr.detail_view,
            show_default_elements: bvr.show_default_elements
        };

        var mode = '';
        var layout = bvr.src_el.getParent(".spt_tool_top");
        if (layout != null) {
            mode = 'tool'
        }

        if (mode == 'tool') {
            spt.app_busy.show("Loading ...");
            var layout = bvr.src_el.getParent(".spt_tool_top");
            var element = layout.getElement(".spt_tool_content");
            spt.panel.load(element, class_name, kwargs);
            spt.app_busy.hide();
        }
        else {
            var element_name = "detail_"+bvr.code;
            var title = bvr.label + " ["+bvr.name+"]";
            spt.tab.add_new(element_name, title, class_name, kwargs);
        }
        '''
        } )


        #link_wdg = self.get_link_wdg(target_id, title, widget)
        #div.add( link_wdg )
        div.add(widget)

        return div




class SObjectTaskStatusElementWdg(SObjectDetailElementWdg):
    '''The element widget that displays a button which when clicked will open up
    a detail view of a task'''

    ARGS_KEYS = {
    }
 

    def get_display(self):

        sobject = self.get_current_sobject()

        self.search_key = SearchKey.get_by_sobject(sobject)
    
        div = DivWdg()
        div.add_class("hand")

        title = "Show Item Details"
        if self.widget:
            widget = self.widget
        else:
            widget = IconButtonWdg(title=title, icon="BS_SEARCH")


        code = sobject.get_code()
        name = sobject.get_value("name", no_exception=True)
        if not name:
            name = code


        search_type_obj = sobject.get_search_type_obj()
        title = search_type_obj.get_title()
        if not title:
            title = "Detail"
        title = _(title)


        tab_element_names = self.kwargs.get("tab_element_names") or ""
        detail_view = self.kwargs.get("detail_view") or ""

        widget.add_behavior( {
        'type': 'click_up',
        'search_key': self.search_key,
        'label': title,
        'code': code,
        'name': name,
        'cbjs_action': '''
        spt.tab.set_main_body_tab();
        var class_name = 'tactic.ui.tools.SObjectTaskStatusDetailWdg';
        var kwargs = {
            search_key: bvr.search_key,
        };

        var mode = '';
        var layout = bvr.src_el.getParent(".spt_tool_top");
        if (layout != null) {
            mode = 'tool'
        }

        if (mode == 'tool') {
            spt.app_busy.show("Loading ...");
            var layout = bvr.src_el.getParent(".spt_tool_top");
            var element = layout.getElement(".spt_tool_content");
            spt.panel.load(element, class_name, kwargs);
            spt.app_busy.hide();
        }
        else {
            var element_name = "detail_"+bvr.code;
            var title = bvr.label + " ["+bvr.name+"]";
            spt.tab.add_new(element_name, title, class_name, kwargs);
        }
        '''
        } )


        div.add(widget)

        return div


class TaskDetailPanelElementWdg(SObjectDetailElementWdg):
    '''The element widget that displays according to type'''

    ARGS_KEYS = {
    }
 

    def get_display(self):

        sobject = self.get_current_sobject()

        self.search_key = SearchKey.get_by_sobject(sobject)
    
        div = DivWdg()
        div.add_class("hand")

        title = "Show Item Details"
        if self.widget:
            widget = self.widget
        else:
            widget = IconButtonWdg(title=title, icon="BS_SEARCH")


        code = sobject.get_code()
        name = sobject.get_value("name", no_exception=True)
        if not name:
            name = code


        widget.add_behavior( {
        'type': 'click_up',
        'search_key': self.search_key,
        'code': code,
        'name': name,
        'cbjs_action': '''
        spt.tab.set_main_body_tab();
        var class_name = 'tactic.ui.tools.TaskDetailPanelWdg';
        var kwargs = {
            search_key: bvr.search_key,
        };

        var mode = '';
        var layout = bvr.src_el.getParent(".spt_tool_top");
        if (layout != null) {
            mode = 'tool'
        }

        if (mode == 'tool') {
            spt.app_busy.show("Loading ...");
            var layout = bvr.src_el.getParent(".spt_tool_top");
            var element = layout.getElement(".spt_tool_content");
            spt.panel.load(element, class_name, kwargs);
            spt.app_busy.hide();
        }
        else {
            var element_name = "detail_"+bvr.code;
            var title = "Detail ["+bvr.name+"]";
            spt.tab.add_new(element_name, title, class_name, kwargs);
        }
        '''
        } )


        div.add(widget)

        return div



