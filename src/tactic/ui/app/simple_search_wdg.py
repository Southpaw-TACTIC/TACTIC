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

# 

__all__ = ['SimpleSearchExampleWdg', 'SimpleSearchWdg']

from pyasm.common import Common, Container, TacticException, jsonloads
from pyasm.search import Search, SearchKey, SearchType
from pyasm.biz import ExpressionParser, Project
from pyasm.web import DivWdg, HtmlElement, Table
from pyasm.widget import HiddenWdg, WidgetConfigView
from pyasm.common import Xml

from tactic.ui.filter import FilterData, BaseFilterElementWdg
from tactic.ui.common import BaseTableElementWdg, BaseRefreshWdg
from tactic.ui.widget import TextBtnSetWdg, ActionButtonWdg

from tactic.ui.filter import KeywordFilterElementWdg


class SimpleSearchExampleWdg(BaseRefreshWdg):

    def get_args_keys(my):
        return {
        'search_type': 'search type for this search widget',
        'search_view': 'view for the search',
        'prefix': 'the prefix used to find the input data'
        }


    def get_display(my):
        top = DivWdg()
        my.set_as_panel(top)

        search_class = 'tactic.ui.app.simple_search_wdg.SimpleSearchWdg'

        # for now add a table layout wdg
        from tactic.ui.panel import ViewPanelWdg
        my.view = 'manage'
        my.search_type = my.kwargs.get("search_type")
        table = ViewPanelWdg(search_type=my.search_type, view=my.view, search_class=search_class)
        top.add(table)

        return top



class SimpleSearchWdg(BaseRefreshWdg):

    SEARCH_COLS = ['keyword','keywords','key','name','description','code']

    def get_args_keys(my):
        return {
        'search_type': 'search type for this search widget',
        'run_search_bvr': 'run search bvr when clicking on Search',
        'prefix': 'the prefix used to find the input data'
        }


    def init(my):

        my.prefix = my.kwargs.get('prefix')
        if not my.prefix:
            my.prefix = 'simple_search'

        my.content = None

        my.prefix = 'simple'
        my.search_type = my.kwargs.get("search_type")
        # this is needed for get_config() to search properly
        my.base_search_type = Project.extract_base_search_type(my.search_type)
        my.column_choice = None
        

    def handle_search(my):
        my.search = Search(my.search_type)
        my.alter_search(my.search)
        return my.search

    def get_search(my):
        return my.search




    
    def alter_search(my, search):
        '''
        from tactic.ui.filter import BaseFilterElementWdg
        config = my.get_config()
        element_names = config.get_element_names()
        for element_name in element_names:
            widget = config.get_display_widget(element_name)

            if isinstance(widget, BaseFilterElementWdg):
                widget.alter_search(search)

        '''


        from tactic.ui.panel import CustomLayoutWdg

        # define a standard search action
        from tactic.ui.filter import FilterData
        filter_data = FilterData.get()
        config = my.get_config()

        data_list = filter_data.get_values_by_prefix(my.prefix)
        search_type = search.get_search_type()
      
        my.column_choice = my.get_search_col(search_type)


        element_data_dict = {}
        for data in data_list:
            handler = data.get("handler")
            element_name = data.get("element_name")
            if not element_name:
                continue

            element_data_dict[element_name] = data



        element_names = config.get_element_names()
        if not element_names:
            element_names = ['keywords']

        for element_name in element_names:

            widget = config.get_display_widget(element_name)
            if not widget:
                
                widget = KeywordFilterElementWdg(column=my.column_choice)
                widget.set_name(element_name)

            data = element_data_dict.get(element_name)
            if not data:
                data = {}
            widget.set_values(data)

            if isinstance(widget, KeywordFilterElementWdg):
                if not data.get("keywords") and my.kwargs.get("keywords"):
                    widget.set_value("value", my.kwargs.get("keywords"))
            widget.alter_search(search)

        return




    def set_content(my, content):
        my.content = content

    def get_top(my):
        top = my.top
        top.add_color("background", "background", -5)
        top.add_style("margin-bottom: -2px")
        top.add_class("spt_filter_top")

        table = Table()
        top.add(table)

        tr, td = table.add_row_cell()



        # add the load wdg
        show_saved_search = True
        if show_saved_search:
            saved_button = ActionButtonWdg(title='Saved', tip='Load Saved Searches')
            saved_button.add_behavior( {
                #'type': 'load',
                'search_type': my.search_type,
                'cbjs_action': '''
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
            td.add(saved_button)
            saved_button.add_style("float: right")
            saved_button.add_style("margin: 10px")




        clera_button = ActionButtonWdg(title='Clear', tip='Clear all of the filters' )
        td.add(clera_button)
        clera_button.add_style("float: right")
        clera_button.add_style("margin: 10px")
        clera_button.add_behavior( {
        'type': 'click',
        'cbjs_action': '''
        spt.api.Utility.clear_inputs(bvr.src_el.getParent(".spt_filter_top"));
        '''
        } )

        title_div = DivWdg()
        td.add(title_div)
        title_div.add("<div style='font-size: 16px'>Search Criteria</div>")
        title_div.add("<div>Select filters to refine your search</div>")
        title_div.add_style("padding: 20px 0px 0px 20px")

        table.add_style("margin-left: auto")
        table.add_style("margin-right: auto")
        table.add_style("margin-bottom: 15px")
        table.add_style("width: 100%")


        tr = table.add_row()

        if not my.content:
            my.content = DivWdg()
            my.content.add("No Content")

        td = table.add_cell()
        td.add(my.content)
        #my.content.add_style("margin: -2 -1 0 -1")


        show_search = my.kwargs.get("show_search")
        if show_search in [False, 'false']:
            show_search = False
        else:
            show_search = True

        if show_search:
            search_wdg = my.get_search_wdg()
            table.add_row()
            search_wdg.add_style("float: left")

            search_wdg.add_style("padding-top: 6px")
            search_wdg.add_style("padding-left: 10px")
            search_wdg.add_style("height: 33px")

            td = table.add_cell()
            td.add(search_wdg)
            td.add_style("padding: 5px 20px")
            #td.add_border()
            #td.add_color("background", "background", -10)



        hidden = HiddenWdg("prefix", my.prefix)
        top.add(hidden)
        # this cannot be spt_search as it will confuse spt.dg_table.search_cbk() 
        top.add_class("spt_simple_search")

        return top


    def get_config(my):


        my.view = my.kwargs.get("search_view")
        config = my.kwargs.get("search_config")

        if not my.view:
            my.view = 'custom_filter'
        #view = "custom_filter"

        project_code = Project.extract_project_code(my.search_type)

        search = Search("config/widget_config", project_code=project_code )
        search.add_filter("view", my.view)
        search.add_filter("search_type", my.base_search_type)
        config_sobjs = search.get_sobjects()

        from pyasm.search import WidgetDbConfig
        config_sobj = WidgetDbConfig.merge_configs(config_sobjs)

        if config_sobj:
            #config_xml = config_sobj.get("config")
            config_xml = config_sobj.get_xml().to_string()
            config_xml = Common.run_mako(config_xml)

        elif config:
            config_xml = '''
            <config>
            <custom_filter>%s
            </custom_filter>
            </config>
            ''' % config
        else:
            config_xml = '''
            <config>
            <custom_filter>
            </custom_filter>
            </config>
            '''
            # use the one defined in the default config file
            file_configs = WidgetConfigView.get_configs_from_file(my.base_search_type, my.view)
            if file_configs:
                config = file_configs[0]
                xml_node = config.get_view_node()
                if xml_node is not None:
                    xml = Xml(config.get_xml().to_string())
                    config_xml = '<config>%s</config>' %xml.to_string(node=xml_node)

            
        from pyasm.widget import WidgetConfig
        config = WidgetConfig.get(view=my.view, xml=config_xml)

        return config




    def get_display(my):

        element_data_dict = {}

        config = my.get_config()
        element_names = config.get_element_names()
        content_wdg = DivWdg()




        if not element_names:
            element_names = ['keywords']

        my.set_content(content_wdg)

        
        # this is somewhat duplicated logic from alter_search, but since this is called 
        # in ViewPanelWdg, it's a diff instance and needs to retrieve again
        filter_data = FilterData.get()

        filter_view = my.kwargs.get("filter_view")
        if filter_view:
            search = Search("config/widget_config")
            search.add_filter("view", filter_view)
            search.add_filter("category", "search_filter")
            search.add_filter("search_type", my.search_type)
            filter_config = search.get_sobject()
            if filter_config:
                filter_xml = filter_config.get_xml_value("config")
                filter_value = filter_xml.get_value("config/filter/values")
                if filter_value:
                    data_list = jsonloads(filter_value)

        else:
            data_list = filter_data.get_values_by_prefix(my.prefix)



        for data in data_list:
            handler = data.get("handler")
            element_name = data.get("element_name")
            if not element_name:
                continue

            element_data_dict[element_name] = data

        elements_wdg = DivWdg()
        content_wdg.add(elements_wdg)
        elements_wdg.add_color("color", "color")
        elements_wdg.add_style("padding-top: 10px")
        elements_wdg.add_style("padding-bottom: 15px")

        #elements_wdg.add_color("background", "background3", 0)
        elements_wdg.add_color("background", "background", -3)
        elements_wdg.add_border()



        if len(element_names) == 1:
            elements_wdg.add_style("border-width: 0px 0px 0px 0px" )
            elements_wdg.add_style("padding-right: 50px" )
        else:
            elements_wdg.add_style("border-width: 0px 0px 0px 0px" )

        table = Table()
        table.add_color("color", "color")
        elements_wdg.add(table)
        table.add_class("spt_simple_search_table")
        
        columns = my.kwargs.get("columns")
        if not columns:
            columns = 2
        else:
            columns = int(columns) 
       
        num_rows = int(len(element_names)/columns)+1
        tot_rows = int(len(element_names)/columns)+1
        project_code = Project.get_project_code()
        # my.search_type could be the same as my.base_search_type
        full_search_type = SearchType.build_search_type(my.search_type, project_code)


        visible_rows = my.kwargs.get("visible_rows")
        if visible_rows:
            visible_rows = int(visible_rows)
            num_rows = visible_rows
        else:
            visible_rows = 0

        titles = config.get_element_titles() 
        row_count = 0
        for i, element_name in enumerate(element_names):
            attrs = config.get_element_attributes(element_name)
            if i % columns == 0:

                if visible_rows and row_count == visible_rows:
                    tr, td = table.add_row_cell("+ more ...")
                    td.add_class("hand")
                    td.add_class("SPT_DTS")
                    td.add_class("spt_toggle")
                    td.add_style("padding-left: 10px")

                    td.add_behavior( {
                        'type': 'click_up',
                        'visible_rows': visible_rows,
                        'cbjs_action': '''
                        var top = bvr.src_el.getParent(".spt_simple_search_table");
                        var expand = true;
                        var rows = top.getElements(".spt_simple_search_row");
                        for (var i = 0; i < rows.length; i++) {
                            var row = rows[i];
                            if (row.getStyle("display") == "none") {
                                row.setStyle("display", "");
                            }
                            else {
                                row.setStyle("display", "none");
                                expand = false;
                            }
                        }
                        var spacer = top.getElements(".spt_spacer");
                        var cell = top.getElement(".spt_toggle");
                        if (expand) {
                            spacer.setStyle("height", (rows.length+bvr.visible_rows)*20);
                            cell.innerHTML = "- less ...";
                        }
                        else {
                            spacer.setStyle("height", bvr.visible_rows*20);
                            cell.innerHTML = "+ more ...";
                        }

                        '''
                    } )


                tr = table.add_row()
                if visible_rows and row_count >= visible_rows:

                    tr.add_class("spt_simple_search_row")
                    tr.add_style("display: none")
                    tr.add_style("height: 0px")

                row_count += 1

            icon_td = table.add_cell()
            title_td = table.add_cell()
            element_td =table.add_cell()


            # show the title
            title_td.add_style("text-align: left")
            title_td.add_style("padding-right: 5px")
            title_td.add_style("min-width: 60px")


            element_wdg = DivWdg()
            if attrs.get('view') == 'false':
                element_wdg.add_style('display: none')
            element_td.add(element_wdg)

            #title_td.add_style("border: solid 1px red")
            #element_td.add_style("border: solid 1px blue")
            #element_wdg.add_style("border: solid 1px yellow")


            if i >= 0  and i < columns -1 and len(element_names) > 1:
                spacer = DivWdg()
                spacer.add_class("spt_spacer")
                spacer.add_style("border-style: solid")
                spacer.add_style("border-width: 0 0 0 0")
                #spacer.add_style("height: %spx" % (num_rows*20))
                spacer.add_style("height: %spx" % (num_rows*20))
                spacer.add_style("width: 10px")
                spacer.add_style("border-color: %s" % spacer.get_color("border") )
                spacer.add("&nbsp;")
                td = table.add_cell(spacer)
                td.add_attr("rowspan", tot_rows)

            #element_wdg.add_color("color", "color3")
            #element_wdg.add_color("background", "background3")
            #element_wdg.set_round_corners()
            #element_wdg.add_border()

            element_wdg.add_style("padding: 4px 10px 4px 5px")
            element_wdg.add_class("spt_table_search")
            element_wdg.add_style("margin: 1px")
            element_wdg.add_style("min-height: 20px")
            element_wdg.add_style("min-width: 250px")

            # this is done at get_top()
            #element_wdg.add_class("spt_search")
            element_wdg.add( HiddenWdg("prefix", my.prefix))

            display_handler = config.get_display_handler(element_name)
            element_wdg.add( HiddenWdg("handler", display_handler))


            element_wdg.add( HiddenWdg("element_name", element_name))
        

            from pyasm.widget import ExceptionWdg
            try:
                widget = config.get_display_widget(element_name)
                if widget:
                    widget.set_title(titles[i])

            except Exception, e:
                element_wdg.add(ExceptionWdg(e))
                continue


            if not widget:
                # the default for KeywordFilterElementWdg is mode=keyword
                if not my.column_choice:
                    my.column_choice = my.get_search_col(my.search_type)
                widget = KeywordFilterElementWdg(column=my.column_choice)
                widget.set_name(element_name)
                


            from pyasm.widget import IconWdg
            icon_div = DivWdg()
            icon_td.add(icon_div)
            icon_div.add_style("width: 20px")
            icon_div.add_style("margin-top: -2px")
            icon_div.add_style("padding-left: 6px")
            icon_div.add_class("spt_filter_top")


            widget.set_show_title(False)
            #element_wdg.add("%s: " % title)
            data = element_data_dict.get(element_name)

			
            view_panel_keywords = my.kwargs.get("keywords")
            #user data takes precedence over view_panel_keywords
            if isinstance(widget, KeywordFilterElementWdg):
                if view_panel_keywords:
                    widget.set_value("value", view_panel_keywords)
            if data:
                widget.set_values(data)

                
           
			    
                    

            if isinstance(widget, KeywordFilterElementWdg) and not full_search_type.startswith('sthpw/sobject_list'):
                widget.set_option('filter_search_type', full_search_type)
            try:
                if attrs.get('view') != 'false':
                    title_td.add(widget.get_title_wdg())

                element_wdg.add(widget.get_buffer_display())
            except Exception, e:
                element_wdg.add(ExceptionWdg(e))
                continue
                


            icon = IconWdg("Filter Set", "BS_ASTERISK")
            #icon.add_style("color", "#393")
            icon_div.add(icon)
            icon.add_class("spt_filter_set")
            icon.add_attr("spt_element_name", element_name)

            if not widget.is_set():
                icon.add_style("display: none")



        #elements_wdg.add("<br clear='all'/>")
        top = my.get_top()
        return top



    def get_search_wdg(my):
        search_div = DivWdg()

        if my.kwargs.get('run_search_bvr'):
            run_search_bvr = my.kwargs.get('run_search_bvr')
        else:
            run_search_bvr = {
                'type':         'click_up',
                'cbjs_action':  'spt.dg_table.search_cbk(evt, bvr)',
                'new_search':   True,
                'panel_id':     my.prefix
            }

        button = ActionButtonWdg(title='Search', tip='Run search with this criteria' )
        search_div.add(button)
        #button.add_style("margin-top: -7px")
        button.add_behavior( run_search_bvr )

        return search_div



    def get_search_col(cls, search_type, simple_search_view=''):
        '''Get the appropriate keyword search col based on column existence in this sType'''
        if simple_search_view:
            from pyasm.widget import WidgetConfigView
            config = WidgetConfigView.get_by_search_type(search_type, simple_search_view)
            # assume the keyword filter is named "keyword"
            options = config.get_display_options('keywords')
            column = options.get('column')
           
            if column:
                return column

        for col in cls.SEARCH_COLS:
            if SearchType.column_exists(search_type, col):
                return col

        return cls.SEARCH_COLS[-1]

    get_search_col = classmethod(get_search_col)

    def get_hint_text(cls, search_type, simple_search_view=''):
        '''Get the hint text for keyword search col defined from widget_config'''
        if simple_search_view:
            from pyasm.widget import WidgetConfigView
            config = WidgetConfigView.get_by_search_type(search_type, simple_search_view)
            # assume the keyword filter is named "keyword"
            options = config.get_display_options('keyword')
            hint_text = options.get('hint_text')
            if hint_text:
                return hint_text
        
        return ""

    get_hint_text = classmethod(get_hint_text)
