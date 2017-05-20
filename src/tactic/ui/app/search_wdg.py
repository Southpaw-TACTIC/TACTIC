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
__all__ = ["SearchWdg","SearchBoxPopupWdg", "LocalSearchWdg", "SaveSearchCbk"]

import os, types

from pyasm.common import Xml, Common, Environment, XmlException, UserException, Container, SetupException
from pyasm.command import Command
from pyasm.search import Search, SearchType, SObject, SearchInputException, DbContainer, SearchException
from pyasm.web import Widget, DivWdg, HtmlElement, SpanWdg, Table, WebContainer, WidgetSettings
from pyasm.widget import SelectWdg, FilterSelectWdg, WidgetConfig, TextWdg, ButtonWdg, IconWdg, HiddenWdg, SwapDisplayWdg, IconButtonWdg, ProdIconButtonWdg, HintWdg, WidgetConfigView
from tactic.ui.common import BaseRefreshWdg
from tactic.ui.container import RoundedCornerDivWdg, PopupWdg, HorizLayoutWdg
from tactic.ui.filter import FilterData
from tactic.ui.widget import TextBtnSetWdg
from tactic.ui.widget import ActionButtonWdg

#from search_limit_wdg import SearchLimitWdg


class SearchBoxPopupWdg(BaseRefreshWdg):

    def get_args_keys(my):
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

    def init(my):
        my.search_type = my.kwargs.get('search_type')
        my.search_view = my.kwargs.get('view')
        my.custom_filter_view = my.kwargs.get('custom_filter_view')
        my.parent_key  = my.kwargs.get('parent_key')
        my.filter  = my.kwargs.get('filter')
        my.state  = my.kwargs.get('state')
        
        my.state = BaseRefreshWdg.process_state(my.state)

        my.search_wdg = SearchWdg(search_type=my.search_type, view=my.search_view, parent_key=my.parent_key, display=True, filter=my.filter, custom_filter_view=my.custom_filter_view, state=my.state)
        my.search = my.search_wdg.get_search()

    def get_search(my):
        return my.search


    def get_display(my):
        sbox_popup_id = 'SearchBoxPopupWdg'

        search_container = DivWdg()
        search_container.set_id( "%s_search" % sbox_popup_id)
        search_container.add_style("display", "block")
        search_container.set_attr("spt_search_type", my.search_type)
        search_container.set_attr("spt_search_view", my.search_view)

        search_container.add(my.search_wdg)

        sbox_popup = PopupWdg(id=sbox_popup_id, allow_page_activity=True, width="720px")
        sbox_popup.add("TACTIC Search Box Window", "title")

        sbox_popup.add( search_container, 'content' )
        return sbox_popup





class SearchWdg(BaseRefreshWdg):

    def get_args_keys(my):
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



    def get_default_filter_config(my):
        custom_filter_view = my.kwargs.get('custom_filter_view')

        if not custom_filter_view:
            custom_filter_view=''

        config = []
        config.append("<config>\n")
        config.append("<filter>\n")

        config.append('''
        <element name='Keywords'>
          <display class='tactic.ui.filter.SObjectSearchFilterWdg'>
            <search_type>%s</search_type>
            <prefix>quick</prefix>
          </display>
        </element>
        ''' % my.search_type)

        config.append('''
        <element name='Custom'>
          <display class='tactic.ui.filter.GeneralFilterWdg'>
            <prefix>custom</prefix>
            <search_type>%s</search_type>
            <mode>custom</mode>
            <custom_filter_view>%s</custom_filter_view>
          </display>
        </element>
        ''' % (my.search_type, custom_filter_view) )


        config.append('''
        <element name='Filter'>
          <display class='tactic.ui.filter.GeneralFilterWdg'>
             <prefix>main_body</prefix>
             <search_type>%s</search_type>
             <mode>sobject</mode>
           </display>
        </element>
        ''' % my.search_type)

        """
        config.append('''
        <element name='Filter2'>
          <display class='tactic.ui.filter.GeneralFilterWdg'>
             <prefix>filter2</prefix>
             <search_type>%s</search_type>
             <mode>sobject</mode>
           </display>
        </element>
        ''' % my.search_type)
        """

        """
        config.append('''
        <element name='Parent'>
          <display class='tactic.ui.filter.GeneralFilterWdg'>
            <prefix>parent</prefix>
            <search_type>%s</search_type>
            <mode>parent</mode>
          </display>
        </element>
        ''' % my.search_type)
        """


        config.append('''
        <element name='Related'>
          <display class='tactic.ui.filter.GeneralFilterWdg'>
            <prefix>children</prefix>
            <search_type>%s</search_type>
            <mode>child</mode>
          </display>
        </element>
        ''' % my.search_type)


        """
        config.append('''
        <element name='Related'>
          <display class='tactic.ui.filter.GeneralFilterWdg'>
            <prefix>related</prefix>
            <search_type>%s</search_type>
            <mode>child</mode>
          </display>
        </element>
        ''' % my.search_type)
        """




        config.append("</filter>\n")
        config.append("</config>\n")

        config = ''.join(config)

        config_xml = Xml()
        config_xml.read_string(config)
        config = WidgetConfig.get(xml=config_xml, view='filter')
        return config


    def get_num_filters_enabled(my):
        return my.num_filters_enabled


    def init(my):

        my.user_override = my.kwargs.get('user_override') in ['true', True]

        custom_search_view = my.kwargs.get('custom_search_view')
        if not custom_search_view or not custom_search_view.strip():
            custom_search_view = 'search'

        # create a search for this search widget
        my.search_type = my.kwargs.get('search_type')

        my.search = my.kwargs.get("search")
        if not my.search:
            my.search = Search(my.search_type)
        my.config = None

        # determine whether or not to use the last search.  If any kind of
        # state has been set, then ignore the last_search
        my.use_last_search = True
        parent_key = my.kwargs.get('parent_key')
        state = my.kwargs.get('state')
        if parent_key or state or my.kwargs.get('use_last_search') in [False, 'false']:
            my.use_last_search = False
       
        my.prefix_namespace = my.kwargs.get('prefix_namespace')


        # NOTE: this is still hard coded
        my.prefix = 'main_body'
        # if we are asking for a specific saved search
        save = my.kwargs.get('save')


        my.view = my.kwargs.get('view')

        # get the config from a specific location

        # if the view is specified, use this view with the values
        # specified explicitly in this view
        my.config = None

        # see if a filter is explicitly passed in
        filter = my.kwargs.get('filter')
        my.limit = my.kwargs.get('limit')
        my.run_search_bvr = my.kwargs.get('run_search_bvr')

        # get from search view
     
        # filter can be either dict(data) or a list or
        # xml(filter wdg definition)
        if filter:
            if type(filter) == types.DictType:
                my.config = my.get_default_filter_config()
                filter_data = FilterData([filter])
                filter_data.set_to_cgi()
            elif type(filter) == types.ListType:
                my.config = my.get_default_filter_config()
                filter_data = FilterData(filter)
                filter_data.set_to_cgi()
        
            else:
                
                try:
                    filter_data = None

                    # TODO: remove this. This is for backward compatibilty
                    my.config = WidgetConfig.get(xml=filter, view='filter')
                    filter_data = FilterData.get()
                    if not filter_data.get_data():
                        # use widget settings
                        key = SearchWdg._get_key(my.search_type, my.view)

                        data = WidgetSettings.get_value_by_key(key)
                        if data:
                            filter_data = FilterData(data)
                        filter_data.set_to_cgi()

                except XmlException, e:
                    print("WARNING: non-xml filter detected!! %s" % filter0)

        
        # NOTE: this is only used to maintain backwards compatibility
        # plus it is needed for link_search: which contains the filter_config (old way of doing it)
        if not my.config:# and my.view:
            """
            if ':' in my.view: # avoid view of a SearchWdg like link_search:<search_type>:<view>
                search_view = custom_search_view
            else:
                search_view = my.view
            """
            search_view = custom_search_view
            config_view = WidgetConfigView.get_by_search_type(my.search_type, view=search_view)
            # get the my.config first for the display of SearchWdg
            # then get the filter data below if there is any
            if config_view.get_config().has_view(search_view):
                my.config = config_view.get_config()   

            try:
                search = Search('config/widget_config')
                search.add_filter("view", my.view)
                search.add_filter("search_type", my.search_type)
                config_sobjs = search.get_sobjects()
                from pyasm.search import WidgetDbConfig
                config_sobj = WidgetDbConfig.merge_configs(config_sobjs)
                #config_sobj = config_sobjs[0]
            except SearchException, e:
                print("WARNING: ", e)
                config_sobj = None


            if config_sobj:
                config_xml = config_sobj.get_xml_value("config")

                if not config_view.get_config().has_view(my.view):
                    # make sure it does have the old way of storing filter
                    # elements instead of just filter data
                    if config_xml.get_nodes("config/filter/element"):
                        my.config = WidgetConfig.get(xml=config_xml, view='filter')
                    
                #my.config = my.get_default_filter_config()

                # set the form variables for the filters
                data = config_xml.get_value("config/filter/values")
                # link_search with specific search params takes precesdence
                # TODO: make a distinction between search definition and alter
                # search data provided by user
                if data and not my.user_override:
                    filter_data = FilterData(data)
                    filter_data.set_to_cgi()
                else:    
                    my.set_filter_data(my.search_type, my.view)

            else:
                if my.use_last_search: 
                    my.set_filter_data(my.search_type, my.view)
        if not my.config:
            # get the approprate filter definition
            my.config = my.get_default_filter_config()
            if my.use_last_search: 
                my.set_filter_data(my.search_type, my.view)


        if not my.config:
            return


        my.num_filters_enabled = 0

        # create the filters
        my.filters = []
        security = Environment.get_security()
        element_names = my.config.get_element_names()
        #element_names = ["Keywords", "Related"]

        for element_name in element_names:
            filter = my.config.get_display_widget(element_name)

            if filter and filter.is_visible():
                my.filters.append(filter)

        # make sure there is at least one filter defined
        #assert my.filters

        # just for drawing purpose
        if my.kwargs.get('skip_search') == True:
            return

        try:
            my.alter_search()
            my.set_persistent_value()

        except SearchInputException, e:
            my.clear_search_data(my.search_type)
            raise SearchInputException("%s If this problem persists, this view may contain invalid data in &lt; values &gt;. Clean up the data in Widget Config for the view [%s]."%( e.__str__(), my.view)) 
        except:
            my.clear_search_data(my.search_type)
            raise
        
            
     

    def set_persistent_value(my):
        filter_data = FilterData.get_from_cgi()

        json = filter_data.serialize()
        # use widget settings instead
        # Using solely TableLayoutWdg will result in having no search view
        if my.view:
            key = SearchWdg._get_key(my.search_type, my.view)
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


    def get_search(my):
        return my.search


    def alter_search(my, search=None):

        if not search:
            search = my.search
            if my.limit:
                try:
                    limit = int(my.limit)
                except ValueError:
                    limit = 50
            else:
                limit = 50
            if limit > 0:
                search.set_limit(limit)
       

        # if a parent key was added
        parent_key = my.kwargs.get('parent_key')
        if parent_key:
            parent = Search.get_by_search_key(parent_key)
            search.add_parent_filter(parent)

        my.state = my.kwargs.get('state')
        my.state = BaseRefreshWdg.process_state(my.state)
        
        if my.state:
            parent_type = my.state.get('parent_type')
            if parent_type:
                search.add_filter("search_type", parent_type)


            

        filter_data = FilterData.get()
        data = filter_data.get_data()
        filter_mode = None
        prefix = "filter_mode"
        if my.prefix_namespace:
            prefix = '%s_%s' %(my.prefix_namespace, prefix)
        values = FilterData.get().get_values_by_index(prefix, 0)
        
        if values:
            filter_mode = values.get('filter_mode')
        if not filter_mode:
            filter_mode = 'and'

        # handle the showing of retired
        show_retired = False
        search.set_show_retired(show_retired)

        # add all the filters
        for filter in my.filters:
            filter.set_filter_mode(filter_mode)
            filter.set_state(my.state)
            filter.alter_search(search)

            my.num_filters_enabled += filter.get_num_filters_enabled()


    def set_as_panel(my, widget):
        widget.add_class("spt_panel")

        widget.add_attr("spt_class_name", Common.get_full_class_name(my) )

        for name, value in my.kwargs.items():
            widget.add_attr("spt_%s" % name, value)


    def get_display(my):
        # if no filters are defined, then display nothing
        if not my.filters:
            return Widget()

        filter_top = DivWdg()
        filter_top.add_color("color", "color")
        filter_top.add_color("background", "background", -5)
        filter_top.add_style("padding: 5px")
        filter_top.add_style("min-width: 800px")
        filter_top.add_border()
        my.set_as_panel(filter_top)


        # TEST link to help for search widget
        help_button = ActionButtonWdg(title="?", tip="Search Documentation", size='small')
        filter_top.add(help_button)
        help_button.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            spt.help.set_top();
            spt.help.load_alias("search-quickstart|what-is-searching|search-interface|search-compound|search-expressions");
            '''
        } )
        help_button.add_style("float: right")


        # this id should be removed
        filter_top.set_id("%s_search" % my.prefix)
        filter_top.add_class("spt_search")


        for name, value in my.kwargs.items():
            filter_top.set_attr("spt_%s" % name, value)

        #filter_top.add(my.statement)
        popup = my.get_retrieve_wdg()
        filter_top.add(popup)
        popup = my.get_save_wdg()
        filter_top.add(popup)

        display = my.kwargs.get('display')
       

        # Add a number of filters indicator
        div = DivWdg()
        div.add_class("spt_search_num_filters")
        div.add_style("float: right")
        div.add_style("font-size: 0.9em")
        div.add_style("margin: 0 10 0 10")
        #search_summary.add(div)
        filter_top.add(div)

        if my.num_filters_enabled:
            msg = "[%s] filter/s" % my.num_filters_enabled
            icon = IconWdg(msg, IconWdg.DOT_GREEN)
            div.add(icon)
            div.add("%s" % msg)


        filter_div = DivWdg()
        filter_div.set_id("search_filters")
        filter_div.add_class("spt_search_filters")


        # TODO: disabling for now
        # add the action buttons
        #action_wdg =  my.get_action_wdg()
        #action_wdg.add_style("text-align: right")
        #filter_div.add( action_wdg )
        # add the top
        display_str = 'block'
        if not display:
            display_str = 'none'
        filter_div.add_style("display: %s" % display_str)

        search_wdg = my.get_search_wdg()

        prefix = "filter_mode"
        if my.prefix_namespace:
            prefix = '%s_%s' %(my.prefix_namespace, prefix)
        hidden = HiddenWdg("prefix", prefix)

        match_div = DivWdg()
        match_div.add(hidden)
        match_div.add_class('spt_search_filter') 

        palette =  match_div.get_palette()
        bg_color = palette.color('background')
        light_bg_color =  palette.color('background', modifier=+10)
        

        select = SelectWdg("filter_mode")
        select.add_style("width: 110px")

        select.add_class("spt_search_filter_mode")
        select.set_persist_on_submit(prefix)
        select.remove_empty_option() 
        # for Local search, leave out compound search for now
        if my.kwargs.get('prefix_namespace'):
            select.set_option("labels", "Match all|Match any")
            select.set_option("values", "and|or")
        else:
            select.set_option("labels", "Match all|Match any|Compound")
            select.set_option("values", "and|or|custom")
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
        match_div.add_color("color", "color2")
        #match_div.add(" on the following")
        #hint = HintWdg( "An 'AND' operation is always applied to each category below. " \
        #                "This controls only the filters within each category." )
        #match_div.add(hint)
        #match_div.add('<br/>')
        #match_div.add_style("padding-top: 5px")

        filter_div.add( search_wdg)
        search_wdg.add_style("float: left")
        filter_div.add( match_div)


        filter_div.add(HtmlElement.br())

        filters_div = DivWdg()
        filters_div.add_style("margin: 0 -6 0 -6")

        security = Environment.get_security()

        # add all the filters
        for filter in my.filters:
            element_name = filter.get_name()

            if not security.check_access("search", element_name, "view"):
                continue

            # no need to create it again    
            #filter = my.config.get_display_widget(element_name)
            div = DivWdg()
            filters_div.add(div)

            div.add_class("hand")
            class_suffix = element_name.replace(' ', '_')
            cbjs_action = 'var el=spt.get_cousin(bvr.src_el,".spt_search",".spt_filter_%s");spt.simple_display_toggle(el);' % class_suffix
            div.add_behavior( {
                'type': 'click_up',
                'cbjs_action': cbjs_action
            } )
            div.add_color("color", "color", +5)
            #div.add_gradient("background", "background", -5, -5)
            div.add_style("margin-top: -1px")
            div.add_style("height: 18px")

            div.add_border()
            div.add_style("padding: 8px 5px")
            div.add_style("white-space: nowrap")

            
            if element_name in ["Parent", 'Children']:
                swap = SwapDisplayWdg.get_triangle_wdg()
            else:
                swap = SwapDisplayWdg.get_triangle_wdg()
                swap.set_off()
            swap.add_action_script(cbjs_action)


            div.add_event("onclick", swap.get_swap_script() )
            div.add(swap)
            div.add_class("SPT_DTS")
            div.add(element_name)

            div = DivWdg()
            div.add_class("spt_filter_%s" % class_suffix)

            if element_name in ["Parent", 'Children']:
                div.add_style("display: none")
            else:
                div.add_style("display: block")

            #div.add_style("background-color: #333")
            div.add_color("background", "background")
            div.add_border()
            div.add_style("padding: 10px 8px")
            div.add_style("margin-top: -1px")
            #div.add_style("margin-left: 20px")
            #div.add_style("width: 660")
            div.add(filter)
            filters_div.add(div)

        filter_div.add(filters_div)

        buttons_div = DivWdg()
        buttons_div.add_style("margin-top: 7px")
        buttons_div.add_style("margin-bottom: 7px")
        search_wdg = my.get_search_wdg()
        search_wdg.add_style("margin: 15px auto")
        buttons_div.add(search_wdg)
        filter_div.add(buttons_div)


        filter_top.add(filter_div)

        return filter_top


    def get_retrieve_wdg(my):

        # add the popup
        popup = PopupWdg(id='retrieve_search_wdg')
        popup.add("Retrieve Saved Search", "title")

        div = DivWdg()
        div.add("List of Saved Searches: ")
        div.add(HtmlElement.br(2))
        
        try:
            search = Search("config/widget_config")
            search.add_where("\"view\" like 'saved_search:%'")
            search.add_filter("search_type", my.search_type)
            configs = search.get_sobjects()
        except SearchException, e:
            print("WARNING: ", e)
            configs = []
        except:
            my.clear_search_data(my.search_type)
            raise
        views = SObject.get_values(configs, "view")

        select = SelectWdg("saved_search")
        select.set_id("saved_search")
        select.add_empty_option("-- Select --")
        #select.set_option("query", "config/widget_config|view|view")
        select.set_option("values", views)
        #select.set_option("query_filter", "\"view\" like 'saved_search:%'")
        div.add(select)

        retrieve_button = ButtonWdg("Retrieve Search")
        behavior = {
            'type':         'click',
            'cbjs_action':  'spt.dg_table.retrieve_search_cbk(evt, bvr);'
        }
        retrieve_button.add_behavior( behavior )



        cancel_button = ButtonWdg("Cancel")
        cancel_button.add_event("onclick", "$('retrieve_search_wdg').style.display = 'none'")

        div.add(HtmlElement.hr())
        button_div = DivWdg()
        button_div.add_style("text-align: center")
        button_div.add(retrieve_button)
        button_div.add("&nbsp;&nbsp;")
        button_div.add(cancel_button)
        div.add(button_div)

        popup.add(div, "content")

        return popup


    def get_save_wdg(my):

        # add the popup
        popup = PopupWdg(id='save_search_wdg')
        popup.add("Save Search", "title")


        div = DivWdg()
        div.add("Save current search as: ")

        text = TextWdg("save_search_text")
        text.set_id("save_search_text")
        div.add(text)



        save_button = ButtonWdg("Save Search")
        behavior = {
            'type':         'click',
            'mouse_btn':    'LMB',
            'cbjs_action':  'spt.dg_table.save_search_cbk(evt, bvr);'
        }
        save_button.add_behavior( behavior )


        cancel_button = ButtonWdg("Cancel")
        cancel_button.add_event("onclick", "$('save_search_wdg').style.display = 'none'")

        div.add(HtmlElement.hr())
        button_div = DivWdg()
        button_div.add_style("text-align: center")
        button_div.add(save_button)
        button_div.add("&nbsp;&nbsp;")
        button_div.add(cancel_button)
        div.add(button_div)

        popup.add(div, "content")

        return popup


    def get_action_wdg(my):

        filter_div = DivWdg()

        select = SelectWdg("filter_action")
        select.add_empty_option("-- search action --")
        select.add_style("text-align: right")
        select.set_option("labels", "Retrieve Search|Save Search")
        select.set_option("values", "retrieve|save")
        select.add_event("onchange", "spt.dg_table.search_action_cbk(this)")
        filter_div.add(select)

        return filter_div


    def get_search_wdg(my):
        filter_div = DivWdg()
        filter_div.add_style("width: 200px")

        search_button = ActionButtonWdg(title='Search', tip='Run search with this criteria')

        if my.run_search_bvr:
            run_search_bvr = my.run_search_bvr
        else:
            # cbjs works better than cbfn here
            run_search_bvr = {
                'type':         'click_up',
                'new_search':   True,
                'cbjs_action':  'spt.dg_table.search_cbk(evt, bvr)',
                'panel_id':     my.prefix,
                
            }

        search_button.add_behavior( run_search_bvr )

       
        # add a listener for other widgets to call Run Search
        listen_bvr = run_search_bvr.copy()
        listen_bvr['type'] = 'listen'
        listen_bvr['event_name'] = 'search_%s' %my.search_type

        # needed for CgApp loader
        search_button.add_behavior( listen_bvr )

        clear_button = ActionButtonWdg(title='Clear', tip='Clear all search criteria')
        clear_button.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        spt.api.Utility.clear_inputs(bvr.src_el.getParent(".spt_search"), '.spt_input:not(select.spt_search_filter_mode)');
        '''
        } )
        #    {'label': 'Clear', 'tip': 'Clear all search criteria', 'width': 45,
        #        'bvr': {'cbjs_action': 'spt.api.Utility.clear_inputs(bvr.src_el.getParent(".spt_search"))'} }
        #]
        #txt_btn_set = TextBtnSetWdg(buttons=buttons_list, spacing=6, size='small', side_padding=4 )

        filter_div.add(search_button)
        search_button.add_style("float: left")
        filter_div.add(clear_button)
        clear_button.add_style("float: left")
        filter_div.add("<br clear='all'/>")

        return filter_div

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
                except SetupException, e:
                    print("This filter data is causing error:", data)
                    print(e)


    set_filter_data = staticmethod(set_filter_data)

    def clear_search_data(search_type, view=None):
        DbContainer.abort_thread_sql(force=True)
        key = SearchWdg._get_key(search_type, view)
        WidgetSettings.set_value_by_key(key, '')
    clear_search_data = staticmethod(clear_search_data)   




class LocalSearchWdg(SearchWdg):
    '''Search for a specific column (TableElementWdg)'''

    def init(my):
        my.searchable_search_type = my.kwargs.get('searchable_search_type')
        super(LocalSearchWdg, my).init()
        # my.search_type remains as the one in the main_body used for retrieving data in WidgetSettings

    def get_search_wdg(my):
        filter_div = DivWdg()

        #my.main_src_el_id = my.kwargs.get('main_src_el_id')
        buttons_list = [
                {'label': 'Run Local Search', 'tip': 'Run search with this criteria' },
                {'label': 'Clear', 'tip': 'Clear all search criteria',
                    'bvr': {'cbjs_action': 'spt.api.Utility.clear_inputs(bvr.src_el.getParent(".spt_search"))'} }
        ]

        txt_btn_set = TextBtnSetWdg( buttons=buttons_list, spacing=6, size='small', side_padding=4 )
        run_search_bvr = {
            'type':         'click_up',
            'cbjs_action':  'spt.dg_table.local_search_cbk(evt, bvr);',
            'panel_id':     my.prefix,
            'prefix_namespace': my.prefix_namespace
            
        }
        txt_btn_set.get_btn_by_label('Run Local Search').add_behavior( run_search_bvr )

        filter_div.add( txt_btn_set )
        return filter_div

    def get_default_filter_config(my):
        custom_filter_view = my.kwargs.get('custom_filter_view')
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
        ''' % {'search_type': my.searchable_search_type, 'prefix_namespace': my.prefix_namespace  }
        config_xml = Xml()
        config_xml.read_string(config)
        config = WidgetConfig.get(xml=config_xml, view='filter')
        return config

class SaveSearchCbk(Command):

    def get_args_keys(my):
        return {
        'search_type': 'search_type',
        'view': 'view',
        'unique': 'make sure this is unique'
        }


    def check_unique(my):
        search = Search('config/widget_config')
        search.add_filter("view", my.view)
        search.add_filter("search_type", my.search_type)
        search.add_user_filter()
        config_sobj = search.get_sobject()
        if config_sobj and my.unique:
            view = my.view.replace('link_search:', '')
            raise UserException('This view [%s] already exists' %view)
        return True
    
    def init(my):
        # handle the default
        config = my.kwargs.get('config')
        my.search_type = my.kwargs.get("search_type")
        my.view = my.kwargs.get("view")
        my.unique = my.kwargs.get('unique') == True
        assert(my.search_type)
        if my.unique:
            my.check_unique()
        my.personal = my.kwargs.get('personal')


    def execute(my):
        my.init()

        # create the filters
        my.filters = []
        """
        for element_name in my.config.get_element_names():
            
            filter = my.config.get_display_widget(element_name)
            my.filters.append(filter)

        # make sure there is at least one filter defined
        assert my.filters

        """
        config = "<config>\n"
        config += "<filter>\n"

        # get all of the serialized versions of the filters
        """
        for filter in my.filters:
            config += filter.serialize() + "\n"
        """
        filter_data = FilterData.get()
        json = filter_data.serialize()
        value_type = "json"
        config += "<values type='%s'>%s</values>\n" % (value_type, json)
        config += "</filter>\n"
        config += "</config>\n"
        

        # format the xml
        xml = Xml()
        xml.read_string(config)


        if not my.view:
            saved_view = "saved_search:%s" % my.search_type
        else:
            saved_view = my.view
        #    if my.view.startswith("saved_search:"):
        #        saved_view = my.view
        #    else:
        #        saved_view = "saved_search:%s" % my.view

        # use widget config instead
        search = Search('config/widget_config')
        search.add_filter("view", saved_view)
        search.add_filter("search_type", my.search_type)
        if my.personal:
            search.add_user_filter()
        config = search.get_sobject()

        if not config:
            config = SearchType.create('config/widget_config')
            config.set_value("view", saved_view)
            config.set_value("search_type", my.search_type)
            if my.personal:
                config.set_user()

        config.set_value("config", xml.to_string())
        config.commit()


