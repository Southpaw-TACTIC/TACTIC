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
__all__ = ["SearchWdg","SearchBoxPopupWdg", "LocalSearchWdg", "SaveSearchCbk","LoadSearchWdg"]

import os, types

from pyasm.common import Xml, Common, Environment, XmlException, UserException, Container, SetupException, jsonloads
from pyasm.command import Command
from pyasm.prod.biz import ProdSetting
from pyasm.search import Search, SearchType, SObject, SearchInputException, DbContainer, SearchException
from pyasm.web import Widget, DivWdg, HtmlElement, SpanWdg, Table, WebContainer, WidgetSettings
from pyasm.widget import SelectWdg, FilterSelectWdg, WidgetConfig, TextWdg, ButtonWdg, IconWdg, HiddenWdg, SwapDisplayWdg, IconButtonWdg, ProdIconButtonWdg, HintWdg, WidgetConfigView
from tactic.ui.common import BaseRefreshWdg
from tactic.ui.container import RoundedCornerDivWdg, PopupWdg, HorizLayoutWdg
from tactic.ui.filter import FilterData
from tactic.ui.widget import TextBtnSetWdg, ActionButtonWdg
from tactic.ui.input import TextInputWdg

from .advanced_search import AdvancedSearchSaveWdg, AdvancedSearchSavedSearchesWdg, AdvancedSearchSaveButtonsWdg
#from search_limit_wdg import SearchLimitWdg


class SearchBoxPopupWdg(BaseRefreshWdg):

    def get_args_keys(self):
        '''External settings which populate the widget.  There are 3 ways to
        define which searches exist.
            1) specify the filters, 
            2) specify the view,
            3) specify whether to use the last saved search
        '''
        return {
            'search_type': 'The search_type that this search is operating on',
            'view':     'The stored view for the data',
            'parent_key': 'Provides ability to search by a single parent key',
            'filter': 'manaual data structure for filter',
            'state': 'the surrounding state'
        }

    def init(self):
        self.search_type = self.kwargs.get('search_type')
        self.search_view = self.kwargs.get('view')
        self.custom_filter_view = self.kwargs.get('custom_filter_view')
        self.parent_key  = self.kwargs.get('parent_key')
        self.filter  = self.kwargs.get('filter')
        self.state  = self.kwargs.get('state')

        # 
        filter_view = self.kwargs.get("filter_view")
        filter_view = "job_filter"

        
        self.state = BaseRefreshWdg.process_state(self.state)

        self.search_wdg = SearchWdg(search_type=self.search_type, view=self.search_view, parent_key=self.parent_key, display=True, filter=self.filter, custom_filter_view=self.custom_filter_view, state=self.state)
        self.search = self.search_wdg.get_search()

    def get_search(self):
        return self.search


    def get_display(self):
        sbox_popup_id = 'SearchBoxPopupWdg'

        search_container = DivWdg()
        search_container.set_id( "%s_search" % sbox_popup_id)
        search_container.add_style("display", "block")
        search_container.set_attr("spt_search_type", self.search_type)
        search_container.set_attr("spt_search_view", self.search_view)

        search_container.add(self.search_wdg)

        sbox_popup = PopupWdg(id=sbox_popup_id, allow_page_activity=True, width="720px")
        sbox_popup.add("TACTIC Search Box Window", "title")

        sbox_popup.add( search_container, 'content' )
        return sbox_popup





class SearchWdg(BaseRefreshWdg):

    def get_args_keys(self):
        '''External settings which populate the widget.  There are 3 ways to
        define which searches exist.
            1) specify the filters, 
            2) specify the view,
            3) specify whether to use the last saved search
        '''
        return {
        'search_type': 'The search_type that this search is operating on',
        'display': 'Boolean. The initial display mode of the search.  it is none by default',
        'view':     'The stored view for the data. Saved Search',
        'parent_key': 'Provides ability to search by a single parent key',
        #'popup_embedded': 'Boolean, if True then this widget is generated for a Popup window (so now open close)',

        'filter': 'manaual data structure for filter',
        'use_last_search': 'Boolean to determine if the last search is read or not',
        'state': 'the surrounding state of the search',
        'user_override': 'if True, current search data overrides what is in the search_view',

        'limit': 'an overriding search limit. < 0 means no limit',
        'run_search_bvr' : 'Run Search behavior',
        'custom_filter_view' : 'Provide a custom filter area',
        'custom_search_view' : 'Provide a custom search view'
        }



    def get_default_filter_config(self):

        filter_view = self.kwargs.get('filter_view') or ""

        default_filter_view = self.kwargs.get("default_filter_view")
        if default_filter_view:
            config_view = WidgetConfigView.get_by_search_type(self.search_type, view=default_filter_view)
            return config_view 

        
        
        custom_filter_view = self.kwargs.get('custom_filter_view')
        if not custom_filter_view:
            custom_filter_view=''

        config = []
        config.append("<config>\n")
        config.append("<filter>\n")


        """
        config.append('''
        <element name='Keywords'>
          <display class='tactic.ui.filter.SObjectSearchFilterWdg'>
            <search_type>%s</search_type>
            <prefix>quick</prefix>
          </display>
        </element>
        ''' % self.search_type)
        """

        """
        config.append('''
        <element name='Keywords'>
          <display class='tactic.ui.app.AdvancedSearchKeywordWdg'>
            <search_type>%s</search_type>
            <prefix>quick</prefix>
          </display>
        </element>
        ''' % self.search_type)
        """


        # Simple search
        """
        simple_search_view = "task_filter"
        config.append('''
        <element name='Simple'>
          <display class='tactic.ui.app.SimpleSearchWdg'>
            <prefix>custom</prefix>
            <search_type>%s</search_type>
            <mode>custom</mode>
            <show_title>false</show_title>
            <show_search>false</show_search>
            <search_view>%s</search_view>
          </display>
        </element>
        ''' % (self.search_type, simple_search_view) )
        """




        config.append('''
        <element name='Custom'>
          <display class='tactic.ui.filter.GeneralFilterWdg'>
            <prefix>custom</prefix>
            <search_type>%s</search_type>
            <mode>custom</mode>
            <custom_filter_view>%s</custom_filter_view>
          </display>
        </element>
        ''' % (self.search_type, custom_filter_view) )


        
        show_general_filters = self.kwargs.get("show_general_filters") or "true"
        security = Environment.get_security()
        if security.is_admin():
            show_general_filters = "true"

        default_filter_type = self.kwargs.get("default_filter") or ""
        config.append('''
        <element name='Search Parameters'>
          <display class='tactic.ui.filter.GeneralFilterWdg'>
             <prefix>main_body</prefix>
             <search_type>%s</search_type>
             <modeX>sobject</modeX>
             <mode>child</mode>
            <filter_view>%s</filter_view>
            <show_general_filters>%s</show_general_filters>
            <default_filter>%s</default_filter>
           </display>
        </element>
        ''' % (self.search_type, filter_view, show_general_filters, default_filter_type) )


        """
        config.append('''
        <element name='Advanced2'>
          <display class='tactic.ui.filter.GeneralFilterWdg'>
            <prefix>children</prefix>
            <search_type>%s</search_type>
            <mode>child</mode>
            <filter_view>%s</filter_view>
          </display>
        </element>
        ''' % (self.search_type, filter_view))
        """




        config.append("</filter>\n")
        config.append("</config>\n")

        config = ''.join(config)

        config_xml = Xml()
        config_xml.read_string(config)
        config = WidgetConfig.get(xml=config_xml, view='filter')
        return config


    def get_num_filters_enabled(self):
        return self.num_filters_enabled


    def init(self):
        self.user_override = self.kwargs.get('user_override') in ['true', True]

        custom_search_view = self.kwargs.get('custom_search_view')
        if not custom_search_view or not custom_search_view.strip():
            custom_search_view = 'search'

        # create a search for this search widget
        self.search_type = self.kwargs.get('search_type')

        self.search = self.kwargs.get("search")
        if not self.search or self.search in ['None']:
            self.search = Search(self.search_type)
        self.config = None

        # determine whether or not to use the last search.  If any kind of
        # state has been set, then ignore the last_search
        self.use_last_search = True
        parent_key = self.kwargs.get('parent_key')
        if parent_key in ['None']:
            parent_key = None
        state = self.kwargs.get('state')
        if parent_key or state or self.kwargs.get('use_last_search') in [False, 'false']:
            self.use_last_search = False
       
        self.prefix_namespace = self.kwargs.get('prefix_namespace')


        # NOTE: this is still hard coded
        self.prefix = 'main_body'
        # if we are asking for a specific saved search
        save = self.kwargs.get('save')


        self.view = self.kwargs.get('view')

        # get the config from a specific location

        # if the view is specified, use this view with the values
        # specified explicitly in this view
        self.config = None

        # see if a filter is explicitly passed in
        filter = self.kwargs.get('filter')
        self.filter = filter
        
        self.limit = self.kwargs.get('limit')
        self.run_search_bvr = self.kwargs.get('run_search_bvr')

        # get from search view
     
        # filter can be either dict(data) or a list or
        # xml(filter wdg definition)
        if filter:
            if isinstance(filter, str):
                filter = jsonloads(filter)

            if isinstance(filter, dict):
                self.config = self.get_default_filter_config()
                filter_data = FilterData([filter])
                filter_data.set_to_cgi()
            elif isinstance(filter, list):
                self.config = self.get_default_filter_config()
                filter_data = FilterData(filter)
                filter_data.set_to_cgi()
        
            else:
                
                try:
                    filter_data = None

                    # TODO: remove this. This is for backward compatibilty
                    self.config = WidgetConfig.get(xml=filter, view='filter')
                    filter_data = FilterData.get()
                    if not filter_data.get_data():
                        # use widget settings
                        key = SearchWdg._get_key(self.search_type, self.view)

                        data = WidgetSettings.get_value_by_key(key)
                        if data:
                            filter_data = FilterData(data)
                        filter_data.set_to_cgi()

                except XmlException as e:
                    print("WARNING: non-xml filter detected!!")


        
        # NOTE: this is only used to maintain backwards compatibility
        # plus it is needed for link_search, which contains the filter_config
        # (old way of doing it)
        if not self.config:
            search_view = custom_search_view
            config_view = WidgetConfigView.get_by_search_type(self.search_type, view=search_view)
            # get the self.config first for the display of SearchWdg
            # then get the filter data below if there is any
            if config_view.get_config().has_view(search_view):
                self.config = config_view.get_config()   

            try:
                search = Search('config/widget_config')
                search.add_filter("view", self.view)
                search.add_filter("search_type", self.search_type)
                config_sobjs = search.get_sobjects()
                from pyasm.search import WidgetDbConfig
                config_sobj = WidgetDbConfig.merge_configs(config_sobjs)
                #config_sobj = config_sobjs[0]
            except SearchException as e:
                print("WARNING: ", e)
                config_sobj = None


            if config_sobj:
                config_xml = config_sobj.get_xml_value("config")

                if not config_view.get_config().has_view(self.view):
                    # make sure it does have the old way of storing filter
                    # elements instead of just filter data
                    if config_xml.get_nodes("config/filter/element"):
                        self.config = WidgetConfig.get(xml=config_xml, view='filter')
                    
                #self.config = self.get_default_filter_config()

                # set the form variables for the filters
                data = config_xml.get_value("config/filter/values")
                # link_search with specific search params takes precesdence
                # TODO: make a distinction between search definition and alter
                # search data provided by user
                if data and not self.user_override:
                    filter_data = FilterData(data)
                    filter_data.set_to_cgi()
                else:    
                    self.set_filter_data(self.search_type, self.view)

            else:
                if self.use_last_search: 
                    self.set_filter_data(self.search_type, self.view)
        
        if not self.config:
            # get the approprate filter definition
            self.config = self.get_default_filter_config()
            if self.use_last_search: 
                self.set_filter_data(self.search_type, self.view)


        if not self.config:
            return


        self.num_filters_enabled = 0

        # create the filters
        self.filters = []
        security = Environment.get_security()
        element_names = self.config.get_element_names()
        #element_names = ["Keywords", "Related"]

        extra_options = {
            "search_type": self.search_type,
        }

        for element_name in element_names:
            filter = self.config.get_display_widget(element_name, extra_options=extra_options)

            if filter and filter.is_visible():
                self.filters.append(filter)


        # make sure there is at least one filter defined
        #assert self.filters

        # just for drawing purpose
        if self.kwargs.get('skip_search') == True:
            return

        try:
            self.alter_search()
            set_persistent_search = ProdSetting.get_value_by_key("set_persistent_search")
            if set_persistent_search != "false":
               self.set_persistent_value()

        except SearchInputException as e:
            self.clear_search_data(self.search_type)
            raise SearchInputException("%s If this problem persists, this view may contain invalid data in &lt; values &gt;. Clean up the data in Widget Config for the view [%s]."%( e.__str__(), self.view)) 
        except:
            self.clear_search_data(self.search_type)
            raise
        
            
     

    def set_persistent_value(self):
        filter_data = FilterData.get_from_cgi()

        json = filter_data.serialize()
        # use widget settings instead
        # Using solely TableLayoutWdg will result in having no search view
        if self.view:
            key = SearchWdg._get_key(self.search_type, self.view)
            WidgetSettings.set_value_by_key(key, json)
        #value = WidgetSettings.get_value_by_key(key)
        #print("value: ", value)
        return




    def get_last_filter_config(search_type):

        # get the last search
        view = "saved_search:%s" % search_type

        search = Search('config/widget_config')
        search.add_filter("view", view)
        search.add_filter("search_type", search_type)
        search.add_user_filter()
        config_sobj = search.get_sobject()
        config = None
        if config_sobj:
            config_xml = config_sobj.get_xml_value("config")
            config = WidgetConfig.get(xml=config_xml, view='filter')
        return config
    get_last_filter_config = staticmethod(get_last_filter_config)


    def get_search(self):
        return self.search


    def alter_search(self, search=None):

        if not search:
            search = self.search
            if self.limit:
                try:
                    limit = int(self.limit)
                except ValueError:
                    limit = 50
            else:
                limit = 50
            if limit > 0:
                search.set_limit(limit)
       

        # if a parent key was added
        parent_key = self.kwargs.get('parent_key')
        if parent_key in ['None']:
            parent_key = None
        if parent_key:
            parent = Search.get_by_search_key(parent_key)
            search.add_parent_filter(parent)

        self.state = self.kwargs.get('state')
        self.state = BaseRefreshWdg.process_state(self.state)
        
        if self.state:
            parent_type = self.state.get('parent_type')
            if parent_type:
                search.add_filter("search_type", parent_type)


            

        filter_data = FilterData.get()
        data = filter_data.get_data()
        filter_mode = None
        prefix = "filter_mode"
        if self.prefix_namespace:
            prefix = '%s_%s' %(self.prefix_namespace, prefix)
        values = FilterData.get().get_values_by_index(prefix, 0)
        
        if values:
            filter_mode = values.get('filter_mode')
        if not filter_mode:
            filter_mode = 'and'

        # handle the showing of retired
        show_retired = False
        search.set_show_retired(show_retired)

        # add all the filters
        for filter in self.filters:
            filter.set_filter_mode(filter_mode)
            filter.set_state(self.state)
            filter.alter_search(search)

            self.num_filters_enabled += filter.get_num_filters_enabled()


    def set_as_panel(self, widget):
        widget.add_class("spt_panel")

        widget.add_attr("spt_class_name", Common.get_full_class_name(self) )

        for name, value in self.kwargs.items():
            widget.add_attr("spt_%s" % name, value)


    def get_styles(self):

        styles = HtmlElement.style('''

            .spt_search_top {
                position: relative;
                overflow: visible;
            }

            .spt_search_top .spt_search_container {
                display: flex;
            }

            .spt_search_top .spt_search_filters {
                min-width: 800px;
            }

            .spt_search_top .spt_saved_searches_top {
                width: 191px;
            }

            .spt_search_top .overlay {
                position: absolute;
                top: 0;

                width: 100%;
                height: 100%;

                background-color: transparent;
                transition: 0.5s;
            }

            .spt_search_top .overlay.visible {
                background-color: rgba(0,0,0,0.4);
            }

            .spt_search_top .spt_save_top {
                position: absolute;
                top: 0px;
                right: -1003px;

                width: 100%;
                height: 100%;
                transition: 0.25s;
            }

            .spt_search_top .spt_save_top.visible {
                right: 0px;
            }

            .spt_search_top .spt_search_num_filters {
                display: none
            }

            .spt_search_top .spt_match_filter {
                display: flex;
                align-items: center;

                padding: 5px 10px;
            }

            .spt_search_top .spt_match_filter select{
                margin: 0 5px;
            }


            ''')

        return styles


    def get_display(self):
        
        
        # if no filters are defined, then display nothing
        if not self.filters:
            return Widget()


        top_class = self.kwargs.get("top_class")

        top = self.top
        top.add_class("spt_search_top")
        # TODO: expand on this
       
        top.add_behavior({
            'type': 'load',
            'cbjs_action': self.get_onload_js()
        })
        
        top.add_relay_behavior({
            'type': 'click',
            'bvr_match_class': 'spt_search_filter',
            'cbjs_action': '''
            
            let top = bvr.src_el.getParent('.spt_search_top');
            top.addClass('spt_has_changes');

            '''
        })

        container = DivWdg()
        top.add(container)
        container.add_class("spt_search_container")

        filter_top = DivWdg()
        container.add(filter_top)
        filter_top.add_color("color", "color")
        self.set_as_panel(filter_top)

        hide_saved_searches = self.kwargs.get("hide_saved_searches")

        if hide_saved_searches not in ['true', True]:
            # Saved Searches
            saved_item_action = self.kwargs.get("saved_item_action")
            saved_searches = AdvancedSearchSavedSearchesWdg(search_type=self.search_type, saved_item_action=saved_item_action, top_class=top_class)
            container.add(saved_searches)

            # Save widget
            overlay = DivWdg()
            top.add(overlay)
            overlay.add_class("overlay")
            overlay.add_style("display: none")

            save_top = AdvancedSearchSaveWdg(search_type=self.search_type)
            top.add(save_top)

        # Styles
        top.add(self.get_styles())

        # this id should be removed
        filter_top.set_id("%s_search" % self.prefix)
        filter_top.add_class("spt_search")
        # TODO: expand on this


        for name, value in self.kwargs.items():
            filter_top.set_attr("spt_%s" % name, value)




        display = self.kwargs.get('display')
       

        # Add a number of filters indicator
        div = DivWdg()
        div.add_class("spt_search_num_filters")
        div.add_style("float: right")
        div.add_style("font-size: 0.9em")
        div.add_style("margin: 0 10 0 10")
        #search_summary.add(div)
        filter_top.add(div)

        if self.num_filters_enabled:
            msg = "[%s] filter/s" % self.num_filters_enabled
            icon = IconWdg(msg, IconWdg.DOT_GREEN)
            div.add(icon)
            div.add("%s" % msg)


        filter_div = DivWdg()
        filter_div.set_id("search_filters")
        filter_div.add_class("spt_search_filters")




        # TODO: disabling for now
        # add the action buttons
        #action_wdg =  self.get_action_wdg()
        #action_wdg.add_style("text-align: right")
        #filter_div.add( action_wdg )
        # add the top
        display_str = 'block'
        if not display:
            display_str = 'none'
        filter_div.add_style("display: %s" % display_str)

        prefix = "filter_mode"
        if self.prefix_namespace:
            prefix = '%s_%s' %(self.prefix_namespace, prefix)
        hidden = HiddenWdg("prefix", prefix)

        match_div = DivWdg()
        match_div.add(hidden)
        match_div.add_class('spt_search_filter')
        match_div.add_class("spt_match_filter")

        palette =  match_div.get_palette()
        bg_color = palette.color('background')
        light_bg_color =  palette.color('background', modifier=+10)

        match_div.add("Match")

        select = SelectWdg("filter_mode")
        select.add_style("width: 110px")

        select.add_class("spt_search_filter_mode")
        select.set_persist_on_submit(prefix)
        select.remove_empty_option() 
        # for Local search, leave out compound search for now
        if self.kwargs.get('prefix_namespace'):
            select.set_option("labels", "all|any")
            select.set_option("values", "and|or")
        else:
            select.set_option("labels", "all|any|Compound")
            select.set_option("values", "and|or|custom")
        select.add_style("height: 25px")
        #select.set_option("labels", "all|any")
        #select.set_option("values", "and|or")

        select.add_behavior( {
        'type': 'change',
        'cbjs_action': '''
        var display = bvr.src_el.value == 'custom';;

        var top = bvr.src_el.getParent(".spt_search");
        var ops = top.getElements(".spt_op");
        for (var i = 0; i < ops.length; i++) {
            var op = ops[i];
            var element = op.getElement(".spt_op_display");
            var value = op.getAttribute("spt_op");
            if (display) {
                element.innerHTML = value;
                var level = op.getAttribute("spt_level");
                if (level == 1) {
                    element.setStyle("background", "%s")
                    element.setStyle("padding", "4px")
                }
            } else {
                element.innerHTML = '&nbsp;';
                element.setStyle("background", "%s")
                element.setStyle("padding", "1px")
            }
        }
        ''' %(light_bg_color, bg_color)
        } )

        match_div.add(select)

        match_div.add("of the following rules")

        match_div.add_color("color", "color2")

        filter_div.add( match_div)
        filter_div.add_style("padding-top: 5px")

        filters_div = DivWdg()

        security = Environment.get_security()

        # add all the filters
        num_filters = len(self.filters)
        for i, filter in enumerate(self.filters):
            element_name = filter.get_name()

            if not security.check_access("search", element_name, "view"):
                continue

            # no need to create it again    
            #filter = self.config.get_display_widget(element_name)
            div = DivWdg()
            div.add_color("background", "background")
            filters_div.add(div)


            div.add_color("color", "color", +5)
            if i == 0:
                div.add_style("margin-top: -10px -1px -1px -1px")
            else:
                div.add_style("margin-top: -1px -1px -1px -1px")
            div.add_style("height: 18px")

            div.add_style("padding: 8px 5px")
            div.add_style("white-space: nowrap")

            class_suffix = element_name.replace(' ', '_')

            if num_filters > 1: 
                div.add_class("hand")
                cbjs_action = 'var el=spt.get_cousin(bvr.src_el,".spt_search",".spt_filter_%s");spt.simple_display_toggle(el);' % class_suffix
                div.add_behavior( {
                    'type': 'click_up',
                    'cbjs_action': cbjs_action
                } )
                if element_name in ["Parent", 'Children']:
                    swap = SwapDisplayWdg.get_triangle_wdg()
                else:
                    swap = SwapDisplayWdg.get_triangle_wdg()
                    swap.set_off()
                swap.add_action_script(cbjs_action)


                div.add_event("onclick", swap.get_swap_script() )
                div.add(swap)
            else:
                div.add_style("padding: 8px 10px")

            div.add_class("SPT_DTS")
            div.add(element_name)


            div = DivWdg()
            div.add_class("spt_filter_%s" % class_suffix)

            if element_name in ["Parent", 'Children']:
                div.add_style("display: none")
            else:
                div.add_style("display: block")

            div.add_color("background", "background")
            div.add_style("padding: 10px 8px")
            div.add_style("margin-top: -1px")
            div.add(filter)
            filters_div.add(div)

        filter_div.add(filters_div)

        buttons_div = DivWdg()
        search_action = self.kwargs.get("search_action")
        save_mode = "save_as" if self.filter else "save"
        search_wdg = AdvancedSearchSaveButtonsWdg(prefix=self.prefix, search_action=search_action, mode=save_mode, search_type=self.search_type, top_class=top_class, hide_save_buttons=hide_saved_searches)
        buttons_div.add(search_wdg)
        filter_div.add(buttons_div)

        # show_action = self.kwargs.get("show_action")
        # if show_action in ['bottom_only', 'top_bottom']:

        #     buttons_div = DivWdg()

        #     buttons_div.add_style("margin-top: 7px")
        #     buttons_div.add_style("margin-bottom: 7px")
        #     search_wdg = self.get_search_wdg()
        #     search_wdg.add_style("margin: 15px auto")
        #     buttons_div.add(search_wdg)
        #     filter_div.add(buttons_div)

        # else:
        #     spacing_div = DivWdg()
        #     spacing_div.add_style("height: 8px")
        #     spacing_div.add_color("background", "background")
        #     spacing_div.add_style("margin: -1px")
        #     filters_div.add(spacing_div)

        filter_top.add(filter_div)


        if self.kwargs.get("is_refresh"):
            return filter_top
        else:
            return top



    def get_save_wdg(self):

        div = DivWdg()
        div.add("Save current search as: ")

        text = TextWdg("save_search_text")
        text.set_id("save_search_text")
        div.add(text)



        save_button = ButtonWdg("Save Search")
        behavior = {
            'cbjs_action':  'spt.table.save_search();'
        }
        save_button.add_behavior( behavior )


        cancel_button = ButtonWdg("Cancel")
        cancel_button.add_event("onclick", "document.id('save_search_wdg').style.display = 'none'")

        div.add(HtmlElement.hr())
        button_div = DivWdg()
        button_div.add_style("text-align: center")
        button_div.add(save_button)
        button_div.add("&nbsp;&nbsp;")
        button_div.add(cancel_button)
        div.add(button_div)

        return div



    def get_action_wdg(self):

        filter_div = DivWdg()

        select = SelectWdg("filter_action")
        select.add_empty_option("-- search action --")
        select.add_style("text-align: right")
        select.set_option("labels", "Retrieve Search|Save Search")
        select.set_option("values", "retrieve|save")
        select.add_event("onchange", "spt.dg_table.search_action_cbk(this)")
        filter_div.add(select)

        return filter_div


    # DEPRECATED?
    def get_search_wdg(self):
        filter_div = DivWdg()
        filter_div.add_style("width: 300px")

        search_button = ActionButtonWdg(title='Search', tip='Run search with this criteria')

        if self.run_search_bvr:
            run_search_bvr = self.run_search_bvr
        else:
            run_search_bvr = {
                'type':         'click_up',
                'new_search':   True,
                'cbjs_action':  'spt.dg_table.search_cbk(evt, bvr)',
                'panel_id':     self.prefix,
                
            }

        search_button.add_behavior( run_search_bvr )

       
        # add a listener for other widgets to call Run Search
        listen_bvr = run_search_bvr.copy()
        listen_bvr['type'] = 'listen'
        listen_bvr['event_name'] = 'search_%s' %self.search_type

        # needed for CgApp loader
        search_button.add_behavior( listen_bvr )

        clear_button = ActionButtonWdg(title='Clear', tip='Clear all search criteria')
        clear_button.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        spt.api.Utility.clear_inputs(bvr.src_el.getParent(".spt_search"), '.spt_input:not(select.spt_search_filter_mode)');
        '''
        } )



        # add the load wdg
        saved_button = ActionButtonWdg(title='Saved', tip='Load Saved Searches')
        saved_button.add_behavior( {
            #'type': 'load',
            'search_type': self.search_type,
            'cbjs_action': '''
            // close the search
            var popup = bvr.src_el.getParent(".spt_popup");
            spt.popup.close(popup);

            var class_name = 'tactic.ui.app.LoadSearchWdg';
            var kwargs = {
                search_type: bvr.search_type
            }
            var layout = spt.table.get_layout();
            var panel = layout.getParent(".spt_view_panel_top");
            var popup = spt.panel.load_popup("Saved Searches", class_name, kwargs);
            popup.activator = panel;
            '''
        } )

        save_button = ActionButtonWdg(title='Save')
        save_button.add_behavior( {
            'search_type': self.search_type,
            'cbjs_action': '''
            
            let top = bvr.src_el.getParent(".spt_search_top");
            let overlay = top.getElement(".overlay");
            let saveTop = top.getElement(".spt_save_top");

            overlay.setStyle("display", "");
            overlay.addClass("visible");
            saveTop.addClass("visible");
            saveTop.getElement(".spt_save_title").innerText = bvr.src_el.innerText;
            
            '''
        } )


        filter_div.add(search_button)
        search_button.add_style("float: left")
        filter_div.add(clear_button)
        clear_button.add_style("float: left")
        filter_div.add(saved_button)
        saved_button.add_style("float: left")
        filter_div.add(save_button)

        return filter_div


    def get_onload_js(self):
        
        return r'''

if (typeof(spt.advanced_search) == "undefined") spt.advanced_search = {};

spt.advanced_search.top = bvr.src_el;

spt.advanced_search.get_top = function() {
    return spt.advanced_search.top;
}

spt.advanced_search.set_top = function(top) {
    spt.advanced_search.top = top;
}

spt.advanced_search.generate_json = function() {
    var search_top = spt.advanced_search.get_top();
    var new_values = [];
    if (search_top) {
        var search_containers = search_top.getElements('.spt_search_filter')
        for (var i = 0; i < search_containers.length; i++) {
            var values = spt.api.Utility.get_input_values(search_containers[i],null, false);
            new_values.push(values);
        }
        var ops = search_top.getElements(".spt_op");       // special code for ops
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
            modes.push(op_mode);        }
        var values = {
            prefix: 'search_ops',
            levels: levels,
            ops: op_values,
            modes: modes
        };
        new_values.push(values);    
    }    // convert to json
    
    return new_values;

}

spt.advanced_search.get_filter_values = function(search_top) {
    // get all of the search input values
    var new_values = [];
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
    return new_values;
}   





/* Keyword widget */

spt.advanced_search.keywords = spt.advanced_search.keywords || {};
spt.advanced_search.keywords.recent_searches = bvr.recent_searches;

spt.advanced_search.keywords.add_keyword = function(display) {
    let search_top = spt.advanced_search.get_top();
    
    let tagsContainer = search_top.getElement(".spt_search_tags");
    let tagTemplate = tagsContainer.getElement(".spt_template_item");

    let clone = spt.behavior.clone(tagTemplate);
    let textDiv = clone.getElement(".spt_search_tag_label");
    textDiv.innerText = "#"+display;
    textDiv.setAttribute("spt_value", display);
    clone.setAttribute("spt_value", display);
    clone.removeClass("spt_template_item");
    tagsContainer.appendChild(clone);

    tagsContainer.removeClass("empty");

    let textInput = search_top.getElement(".spt_text_input");
    let validator = search_top.getElement(".spt_validation_indicator");
    textInput.value = "";
    validator.setStyle("display", "none");

    // extract and set keywords
    spt.advanced_search.keywords.set_keywords();
}

spt.advanced_search.keywords.extract_keywords = function() {
    let search_top = spt.advanced_search.get_top();
    
    let tagsContainer = search_top.getElement(".spt_search_tags");
    let items = tagsContainer.getElements(".spt_search_tag_item");
    let keywords = [];

    items.forEach(function(item){
        if (item.hasClass("spt_template_item")) return;
        keywords.push(item.getAttribute("spt_value"));
    })

    return keywords;
}

spt.advanced_search.keywords.set_keywords = function() {
    let search_top = spt.advanced_search.get_top();
    
    let keywords = spt.advanced_search.keywords.extract_keywords();
    let keywordsStorage = search_top.getElement(".spt_keywords");
    keywordsStorage.value = keywords.join(",");
}

spt.advanced_search.keywords.add_recent = function(value) {
    let search_top = spt.advanced_search.get_top();
    
    let server = TacticServerStub.get();
    let classname = "tactic.ui.app.SaveCurrentSearchCmd";
    let kwargs = {
        search_type: spt.advanced_search.keywords.search_type,
        value: value,
    }

    server.p_execute_cmd(classname, kwargs)
    .then(function(ret_val){
        spt.advanced_search.keywords.recent_searches.push(value);

        let recents = search_top.getElement(".spt_recent_searches");
        let template = recents.getElement(".spt_template_item");

        let clone = spt.behavior.clone(template);
        let labelDiv = clone.getElement(".spt_recent_search_label");
        clone.setAttribute("spt_value", value)
        labelDiv.innerText = value;
        clone.removeClass("spt_template_item");

        recents.appendChild(clone);
    });
}

spt.advanced_search.keywords.remove_recent = function(item) {
    let value = item.getAttribute("spt_value");

    let server = TacticServerStub.get();
    let classname = "tactic.ui.app.DeleteRecentSearchCmd";
    let kwargs = {
        search_type: spt.advanced_search.keywords.search_type,
        value: value
    }

    server.p_execute_cmd(classname, kwargs)
    .then(function(ret_val){
        let arr = spt.advanced_search.keywords.recent_searches;
        arr.splice(arr.indexOf(value), 1);
        item.remove();
    });;
}


/* saved search widget */

spt.advanced_search.saved = spt.advanced_search.saved || {};

spt.advanced_search.saved.add_item = function(key, label, value) {
    let search_top = spt.advanced_search.get_top();
    
    let container = search_top.getElement(".spt_saved_searches_container");
    let categoryContainer = container.querySelector("div.spt_saved_searches_item[spt_category='"+key+"']");
    let template = categoryContainer.getElement(".spt_saved_search_item.spt_template_item");

    let clone = spt.behavior.clone(template);
    let labelDiv = clone.getElement(".spt_saved_search_label");
    labelDiv.innerText = label;

    clone.setAttribute("spt_category", key);
    clone.setAttribute("spt_value", value);
    clone.removeClass("spt_template_item");
    clone.removeClass("spt_saved_search_item_template");
    categoryContainer.appendChild(clone);
}

spt.advanced_search.saved.create_item = function(key, label, value) {
    spt.advanced_search.saved.labels[key].push(label);
    spt.advanced_search.saved.values[key].push(value);
}

spt.advanced_search.saved.delete_item = function(key, label) {
    let index = spt.advanced_search.saved.labels[key].indexOf(label);
    spt.advanced_search.saved.labels[key].splice(index, 1);
    spt.advanced_search.saved.values[key].splice(index, 1);
}

spt.advanced_search.saved.load_items = function(key) {
    let search_top = spt.advanced_search.get_top();

    let container = search_top.getElement(".spt_saved_searches_container");
    let selected = container.getElement(".spt_saved_searches_item.selected");
    let categoryContainer = container.querySelector("div.spt_saved_searches_item[spt_category='"+key+"']");
    if (selected) selected.removeClass("selected");
    categoryContainer.addClass("selected");
}

spt.advanced_search.saved.clear_items = function() {
    let search_top = spt.advanced_search.get_top();
    
    let container = search_top.getElement(".spt_saved_searches_container");
    let items = container.getElements(".spt_saved_search_item");

    items.forEach(function(item){
        if (item.hasClass("spt_template_item")) return;
        item.remove();
    });
}


spt.advanced_search.saved.toggle_dropdown = function(display) {
    let search_top = spt.advanced_search.get_top();
    let dropdown = search_top.getElement(".spt_search_categories_dropdown");

    if (display) 
        dropdown.setStyle("display", display);
    else
        spt.toggle_show_hide(dropdown);
}

spt.advanced_search.saved.get_values = function(key) {
    return spt.advanced_search.saved.values[key];
}

spt.advanced_search.saved.get_labels = function(key) {
    return spt.advanced_search.saved.labels[key];
}

spt.advanced_search.saved.get_selected = function() {
    let search_top = spt.advanced_search.get_top();
    
    return search_top.getElement(".spt_saved_search_item.selected");
}

        '''



    def _get_key(search_type, view):
        '''get the key for widget settings of the search filter data'''
        if not view:
            key = "last_search:%s" % (search_type)
        else:
            key = "last_search:%s:%s" % (search_type, view)
        return key
    _get_key = staticmethod(_get_key)

    def set_filter_data(search_type, view=None):
        '''set filter data based on some saved search values in wdg_settings'''

        filter_data = FilterData.get()
        if not filter_data.get_data():
            # use widget settings
            key = SearchWdg._get_key(search_type, view)
            data = WidgetSettings.get_value_by_key(key)
            if data:
              
                try:
                    filter_data = FilterData(data)
                    filter_data.set_to_cgi()
                except SetupException as e:
                    print("This filter data is causing error:", data)
                    print(e)


    set_filter_data = staticmethod(set_filter_data)

    def clear_search_data(search_type, view=None):
        DbContainer.abort_thread_sql(force=True)
        key = SearchWdg._get_key(search_type, view)
        WidgetSettings.set_value_by_key(key, '')
    clear_search_data = staticmethod(clear_search_data)





class LoadSearchWdg(BaseRefreshWdg):

    def get_display(self):

        search_type = self.kwargs.get("search_type")

        div = self.top

        div.add("List of Saved Searches: ")
        div.add(HtmlElement.br(2))
        div.add_style("margin: 20px")
        div.add_style("width: 400px")
        div.add_class("spt_saved_search_top")
        
        try:
            search = Search("config/widget_config")
            search.add_op("begin")
            search.add_filter("view", 'saved_search:%', op="like")
            search.add_filter("category", 'search_filter')
            search.add_op("or")
            search.add_op("begin")
            search.add_user_filter()
            search.add_filter("login", "NULL", op="is", quoted=False)
            search.add_op("or")
            search.add_filter("search_type", search_type)
            configs = search.get_sobjects()
        except SearchException as e:
            print("WARNING: ", e)
            configs = []
        except:
            SearchWdg.clear_search_data(search_type)
            raise

        """
        from tactic.ui.panel import TableLayoutWdg
        element_names = ['view','name','description','delete']
        table = TableLayoutWdg(
                search_type=search_type,
                element_names=element_names,
                search=search,
                show_shelf=False,
                show_border=False,
                show_search_limit=False,
                height="auto",

        )
        div.add(table)
        """

        values = [x.get("view") for x in configs]
        labels = [x.get("title") or x.get("view") for x in configs]

        select = SelectWdg("saved_search")
        div.add(select)
        select.set_id("saved_search")
        select.add_class("spt_saved_search_input")
        select.add_empty_option("-- Select --")
        select.set_option("values", values)
        select.set_option("labels", labels)

        retrieve_button = ActionButtonWdg(title="Load")
        behavior = {
            'type':         'click',
            #'cbjs_action':  'spt.dg_table.retrieve_search_cbk(evt, bvr);'
            'cbjs_action':  '''
            var top = bvr.src_el.getParent(".spt_saved_search_top")
            var input = top.getElement(".spt_saved_search_input");
            var value = input.value;
            if (!value) {
                spt.alert("Please select a saved search to load.");
                return;
            }

            var popup = bvr.src_el.getParent(".spt_popup");
            var activator = popup.activator;
            var layout = activator.getElement(".spt_layout");
            spt.table.set_layout(layout);

            spt.table.load_search(value);
            '''
        }
        retrieve_button.add_behavior( behavior )
        retrieve_button.add_style("display: inline-block")


        remove_button = ActionButtonWdg(title="Remove")
        remove_button.add_behavior( {
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_saved_search_top")
            var input = top.getElement(".spt_saved_search_input");
            var value = input.value;
            if (!value) {
                spt.alert("Please select a saved search to remove.");
                return;
            }

            spt.alert("Remove: " + value);



            '''
        } )
        remove_button.add_style("display: inline-block")



        cancel_button = ActionButtonWdg(title="Cancel")
        cancel_button.add_behavior( {
            'cbjs_action': '''
            var popup = bvr.src_el.getParent(".spt_popup");
            spt.popup.close(popup);
            '''
        } )
        cancel_button.add_style("display: inline-block")

        div.add("<br/>")
        button_div = DivWdg()
        button_div.add_style("text-align: center")
        button_div.add(retrieve_button)
        button_div.add("&nbsp;&nbsp;")
        button_div.add(remove_button)
        button_div.add("&nbsp;&nbsp;")
        button_div.add(cancel_button)
        div.add(button_div)



        div.add("<hr/>")

        save_div = DivWdg()
        div.add(save_div)
        save_div.add("Save Current Search")
        save_div.add("<br/>")
        save_div.add("<br/>")

        text = TextInputWdg(name="new_search_name")
        save_div.add(text)
        text.add_class("spt_new_search_name")

        save_div.add("<br/>")


        save_button = ActionButtonWdg(title="Save Search", width="200")
        save_div.add(save_button)
        save_button.add_behavior( {
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_saved_search_top");
            var input = top.getElement(".spt_new_search_name");
            var value = input.value;
            if (!value) {
                spt.alert("No view name specified");
                return;
            }
            spt.table.save_search(value, {personal: true});

            spt.notify.show_message("Search saved");

            var popup = bvr.src_el.getParent(".spt_popup");
            spt.popup.close(popup);
            '''
        } )
        save_button.add_style("display: inline-block")

        return div







class LocalSearchWdg(SearchWdg):
    '''Search for a specific column (TableElementWdg)'''

    def init(self):
        self.searchable_search_type = self.kwargs.get('searchable_search_type')
        super(LocalSearchWdg, self).init()
        # self.search_type remains as the one in the main_body used for retrieving data in WidgetSettings

    def get_search_wdg(self):
        filter_div = DivWdg()

        #self.main_src_el_id = self.kwargs.get('main_src_el_id')
        buttons_list = [
                {'label': 'Run Local Search', 'tip': 'Run search with this criteria' },
                {'label': 'Clear', 'tip': 'Clear all search criteria',
                    'bvr': {'cbjs_action': 'spt.api.Utility.clear_inputs(bvr.src_el.getParent(".spt_search"))'} }
        ]

        txt_btn_set = TextBtnSetWdg( buttons=buttons_list, spacing=6, size='small', side_padding=4 )
        run_search_bvr = {
            'type':         'click_up',
            'cbjs_action':  'spt.dg_table.local_search_cbk(evt, bvr);',
            'panel_id':     self.prefix,
            'prefix_namespace': self.prefix_namespace
            
        }
        txt_btn_set.get_btn_by_label('Run Local Search').add_behavior( run_search_bvr )

        filter_div.add( txt_btn_set )
        return filter_div

    def get_default_filter_config(self):
        custom_filter_view = self.kwargs.get('custom_filter_view')
        config = '''
        <config>
        <filter>
          <element name='Filter'>
            <display class='tactic.ui.filter.GeneralFilterWdg'>
              <prefix>%(prefix_namespace)s_main_body</prefix>
              <search_type>%(search_type)s</search_type>
              <mode>sobject</mode>
            </display>
          </element>
        </filter>
        </config>
        ''' % {'search_type': self.searchable_search_type, 'prefix_namespace': self.prefix_namespace  }
        config_xml = Xml()
        config_xml.read_string(config)
        config = WidgetConfig.get(xml=config_xml, view='filter')
        return config

class SaveSearchCbk(Command):

    def get_args_keys(self):
        return {
        'search_type': 'search_type',
        'view': 'view',
        'unique': 'make sure this is unique'
        }


    def check_unique(self):
        search = Search('config/widget_config')
        search.add_filter("view", self.view)
        search.add_filter("search_type", self.search_type)
        search.add_user_filter()
        config_sobj = search.get_sobject()
        if config_sobj and self.unique:
            view = self.view.replace('link_search:', '')
            raise UserException('This view [%s] already exists' %view)
        return True
    
    def init(self):
        # handle the default
        config = self.kwargs.get('config')
        self.search_type = self.kwargs.get("search_type")
        self.view = self.kwargs.get("view")
        self.unique = self.kwargs.get('unique') == True
        assert(self.search_type)
        if self.unique:
            self.check_unique()
        self.personal = self.kwargs.get('personal')


    def execute(self):
        self.init()

        # create the filters
        self.filters = []

        config = "<config>\n"
        config += "<filter>\n"

        # get all of the serialized versions of the filters
        filter_data = FilterData.get()
        json = filter_data.serialize()
        value_type = "json"
        config += "<values type='%s'>%s</values>\n" % (value_type, json)
        config += "</filter>\n"
        config += "</config>\n"
        

        # format the xml
        xml = Xml()
        xml.read_string(config)


        if not self.view:
            saved_view = "saved_search:%s" % self.search_type
        else:
            saved_view = self.view
        #    if self.view.startswith("saved_search:"):
        #        saved_view = self.view
        #    else:
        #        saved_view = "saved_search:%s" % self.view

        # use widget config instead
        search = Search('config/widget_config')
        search.add_filter("view", saved_view)
        search.add_filter("search_type", self.search_type)
        if self.personal:
            search.add_user_filter()
        config = search.get_sobject()

        if not config:
            config = SearchType.create('config/widget_config')
            config.set_value("view", saved_view)
            config.set_value("search_type", self.search_type)
            if self.personal:
                config.set_user()

        config.set_value("category", "search_filter")
        config.set_value("config", xml.to_string())
        config.commit()


