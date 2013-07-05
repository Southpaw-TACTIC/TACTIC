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

__all__ = ['SObjectDetailElementWdg']

from pyasm.common import Environment
from pyasm.search import SearchKey
from pyasm.web import DivWdg
from pyasm.widget import IconWdg

from tactic.ui.widget import IconButtonWdg

from tactic.ui.common import BaseTableElementWdg

class SObjectDetailElementWdg(BaseTableElementWdg):
    '''The element widget that displays according to type'''

    ARGS_KEYS = {
    'use_parent': {
        'description': 'Display the parent of this sobject for the detail',
        'type': 'SelectWdg',
        'values': 'true|false',
        'category': 'Options'
    }
    }
 
    def __init__(my, **kwargs):
        my.widget = None
        super(SObjectDetailElementWdg, my).__init__(**kwargs)

    def set_widget(my, widget):
        my.widget = widget

    def get_display(my):

        sobject = my.get_current_sobject()

        use_parent = my.get_option("use_parent")
        use_parent = use_parent in ['true', True]
        #if use_parent in ['true', True]:
        #    sobject = sobject.get_parent()
        #    if not sobject:
        #        return DivWdg()

        my.search_key = SearchKey.get_by_sobject(sobject)
    
        div = DivWdg()
        div.add_class("hand")
        #div.add_style("width: 100%")
        #div.add_style("height: 100%")

        target_id = "main_body"

        title = "Show Item Details"
        if my.widget:
            widget = my.widget
        else:
            widget = IconButtonWdg(title=title, icon=IconWdg.ZOOM)


        code = sobject.get_code()


        widget.add_behavior( {
        'type': 'click_up',
        'search_key': my.search_key,
        'use_parent': use_parent,
        'code': code,
        'cbjs_action': '''
        spt.tab.set_main_body_tab();
        var class_name = 'tactic.ui.tools.SObjectDetailWdg';
        var kwargs = {
            search_key: bvr.search_key,
            use_parent: bvr.use_parent
        };


        var mode = 'xxx';
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
            var title = "Detail ["+bvr.code+"]";
            spt.tab.add_new(element_name, title, class_name, kwargs);
        }
        '''
        } )


        #link_wdg = my.get_link_wdg(target_id, title, widget)
        #div.add( link_wdg )
        div.add(widget)

        return div


    """
    def get_link_wdg(my, target_id, title, widget=None):

        sobject = my.get_current_sobject()

        path = "/%s" % my.search_key
        options = {
            'path': path,
            'class_name': 'tactic.ui.panel.SObjectPanelWdg',
            #'class_name': 'tactic.ui.panel.SearchTypePanelWdg',
            'search_key': my.search_key
        }

        security = Environment.get_security()
        if not security.check_access("url", path, "view"):
            return
        options['path'] = path
        

        view_link_wdg = DivWdg(css="hand")
        view_link_wdg.add_style( "padding-top: 5px" )

        if widget:
            view_link_wdg.add(widget)
        else:
            view_link_wdg.add(title)


        # put in a default class name
        if not options.get('class_name'):
            options['class_name'] = "tactic.ui.panel.ViewPanelWdg"

        # put in a default search
        if not options.get('filters'):
            options['filters'] = '0';

        behavior = {
            'type':         'click_up',
            'cbfn_action':  'spt.side_bar.display_link_cbk',
            'target_id':    target_id,
            'is_popup':     'true',
            'options':      options,
        }
        view_link_wdg.add_behavior( behavior )

        # use shift click to open up in a popup
        behavior = {
            'type':         'click_up',
            'mouse_btn':    'LMB',
            'modkeys':      'SHIFT',
            'cbfn_action':  'spt.side_bar.display_link_cbk',
            'target_id':    target_id, # FIXME: has to be here for now
            'title':        sobject.get_code(),
            'is_popup':     'false',
            'options':      options,
        }
        view_link_wdg.add_behavior( behavior )

 

        return view_link_wdg
    """


