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

    def get_args_keys(self):
        return {
        'search_type': 'search type for this search widget',
        'search_view': 'view for the search',
        'prefix': 'the prefix used to find the input data'
        }


    def get_display(self):
        top = DivWdg()
        self.set_as_panel(top)

        search_class = 'tactic.ui.app.simple_search_wdg.SimpleSearchWdg'

        # for now add a table layout wdg
        from tactic.ui.panel import ViewPanelWdg
        self.view = 'manage'
        self.search_type = self.kwargs.get("search_type")
        table = ViewPanelWdg(search_type=self.search_type, view=self.view, search_class=search_class)
        top.add(table)

        return top



class SimpleSearchWdg(BaseRefreshWdg):

    SEARCH_COLS = ['keyword','keywords','key','name','description','code']

    def get_args_keys(self):
        return {
        'search_type': 'search type for this search widget',
        'run_search_bvr': 'run search bvr when clicking on Search',
        'prefix': 'the prefix used to find the input data'
        }


    def init(self):

        self.prefix = self.kwargs.get('prefix')
        if not self.prefix:
            self.prefix = 'simple_search'

        self.content = None

        self.prefix = 'simple'
        self.search_type = self.kwargs.get("search_type")
        # this is needed for get_config() to search properly
        self.base_search_type = Project.extract_base_search_type(self.search_type)
        self.column_choice = None
        

    def handle_search(self):
        self.search = Search(self.search_type)
        self.alter_search(self.search)
        return self.search

    def get_search(self):
        return self.search




    
    def alter_search(self, search):
        '''
        from tactic.ui.filter import BaseFilterElementWdg
        config = self.get_config()
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
        config = self.get_config()

        data_list = filter_data.get_values_by_prefix(self.prefix)
        search_type = search.get_search_type()
      
        self.column_choice = self.get_search_col(search_type)


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
                
                widget = KeywordFilterElementWdg(column=self.column_choice)
                widget.set_name(element_name)

            data = element_data_dict.get(element_name)
            if not data:
                data = {}
            widget.set_values(data)

            if isinstance(widget, KeywordFilterElementWdg):
                if not data.get("keywords") and self.kwargs.get("keywords"):
                    widget.set_value("value", self.kwargs.get("keywords"))
            widget.alter_search(search)

        return




    def set_content(self, content):
        self.content = content

    def get_top(self):
        top = self.top
        top.add_color("background", "background", -5)
        top.add_style("margin-bottom: -2px")
        top.add_class("spt_filter_top")

        table = Table()
        top.add(table)

        tr, td = table.add_row_cell()


        td.add_class("spt_simple_search_title")


        # add the load wdg
        show_saved_search = True
        if show_saved_search:
            saved_button = ActionButtonWdg(title='Saved', tip='Load Saved Searches')
            saved_button.add_class("spt_simple_search_save_button")
            saved_button.add_behavior( {
                #'type': 'load',
                'search_type': self.search_type,
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




        clear_button = ActionButtonWdg(title='Clear', tip='Clear all of the filters' )
        td.add(clear_button)
        clear_button.add_class("spt_simple_search_clear_button")
        clear_button.add_style("float: right")
        clear_button.add_style("margin: 10px")
        clear_button.add_behavior( {
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

        if not self.content:
            self.content = DivWdg()
            self.content.add("No Content")

        td = table.add_cell()
        td.add(self.content)
        #self.content.add_style("margin: -2 -1 0 -1")


        show_search = self.kwargs.get("show_search")
        if show_search in [False, 'false']:
            show_search = False
        else:
            show_search = True

        show_search = True
        if show_search:
            search_wdg = self.get_search_wdg()
            table.add_row()
            search_wdg.add_style("float: right")
            search_wdg.add_class("spt_simple_search_button")

            search_wdg.add_style("padding-top: 6px")
            search_wdg.add_style("padding-left: 10px")
            search_wdg.add_style("height: 33px")

            td = table.add_cell()
            td.add(search_wdg)
            td.add_style("padding: 5px 10px")
            #td.add_border()
            #td.add_color("background", "background", -10)



        hidden = HiddenWdg("prefix", self.prefix)
        top.add(hidden)
        # this cannot be spt_search as it will confuse spt.dg_table.search_cbk() 
        top.add_class("spt_simple_search")

        return top


    def get_config(self):


        self.view = self.kwargs.get("search_view")
        config = self.kwargs.get("search_config")

        if not self.view:
            self.view = 'custom_filter'
        #view = "custom_filter"

        project_code = Project.extract_project_code(self.search_type)

        search = Search("config/widget_config", project_code=project_code )
        search.add_filter("view", self.view)
        search.add_filter("search_type", self.base_search_type)
        config_sobjs = search.get_sobjects()

        from pyasm.search import WidgetDbConfig
        config_sobj = WidgetDbConfig.merge_configs(config_sobjs)

        if config_sobj:
            #config_xml = config_sobj.get("config")
            config_xml = config_sobj.get_xml().to_string()
            config_xml = config_xml.replace("&lt;", "<")
            config_xml = config_xml.replace("&gt;", ">")
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
            file_configs = WidgetConfigView.get_configs_from_file(self.base_search_type, self.view)
            if file_configs:
                config = file_configs[0]
                xml_node = config.get_view_node()
                if xml_node is not None:
                    xml = Xml(config.get_xml().to_string())
                    config_xml = '<config>%s</config>' %xml.to_string(node=xml_node)

            
        from pyasm.widget import WidgetConfig
        config = WidgetConfig.get(view=self.view, xml=config_xml)

        return config




    def get_display(self):

        element_data_dict = {}

        config = self.get_config()
        element_names = config.get_element_names()

        content_wdg = DivWdg()
        content_wdg.add_class("spt_simple_search_top")

        onload_js = DivWdg()
        content_wdg.add(onload_js)
        onload_js.add_behavior( {
            'type': 'load',
            'cbjs_action': self.get_onload_js()
        } )




        if not element_names:
            element_names = ['keywords']

        self.set_content(content_wdg)

        
        # this is somewhat duplicated logic from alter_search, but since this is called 
        # in ViewPanelWdg, it's a diff instance and needs to retrieve again
        filter_data = FilterData.get()

        filter_view = self.kwargs.get("filter_view")
        if filter_view:
            search = Search("config/widget_config")
            search.add_filter("view", filter_view)
            search.add_filter("category", "search_filter")
            search.add_filter("search_type", self.search_type)
            filter_config = search.get_sobject()
            if filter_config:
                filter_xml = filter_config.get_xml_value("config")
                filter_value = filter_xml.get_value("config/filter/values")
                if filter_value:
                    data_list = jsonloads(filter_value)

        else:
            data_list = filter_data.get_values_by_prefix(self.prefix)



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
        
        columns = self.kwargs.get("columns")
        if not columns:
            columns = 2
        else:
            columns = int(columns) 
       
        num_rows = int(len(element_names)/columns)+1
        tot_rows = int(len(element_names)/columns)+1
        project_code = Project.get_project_code()
        # self.search_type could be the same as self.base_search_type
        full_search_type = SearchType.build_search_type(self.search_type, project_code)


        visible_rows = self.kwargs.get("visible_rows")
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
            element_td = table.add_cell()

            # need to add these to all the elements because it is all separated
            # by table tds
            icon_td.add_class("spt_element_item")
            icon_td.add_attr("spt_element_name", element_name)
            title_td.add_class("spt_element_item")
            title_td.add_attr("spt_element_name", element_name)
            element_td.add_class("spt_element_item")
            element_td.add_attr("spt_element_name", element_name)

            # show the title
            title_td.add_style("text-align: left")
            title_td.add_style("padding-right: 5px")
            title_td.add_style("min-width: 60px")



            element_wdg = DivWdg()
            if attrs.get('view') == 'false':
                element_wdg.add_style('display: none')
            element_td.add(element_wdg)



            if i >= 0  and i < columns -1 and len(element_names) > 1:
                spacer = DivWdg()
                spacer.add_class("spt_spacer")
                spacer.add_style("border-style: solid")
                spacer.add_style("border-width: 0 0 0 0")
                #spacer.add_style("height: %spx" % (num_rows*20))
                spacer.add_style("height: %spx" % (num_rows*10))
                spacer.add_style("width: 10px")
                spacer.add_style("border-color: %s" % spacer.get_color("border") )
                spacer.add("&nbsp;")
                td = table.add_cell(spacer)
                td.add_attr("rowspan", tot_rows)

            element_wdg.add_style("padding: 4px 10px 4px 5px")
            element_wdg.add_class("spt_table_search")
            element_wdg.add_style("margin: 1px")
            element_wdg.add_style("min-height: 20px")
            element_wdg.add_style("min-width: 250px")

            # this is done at get_top()
            #element_wdg.add_class("spt_search")
            element_wdg.add( HiddenWdg("prefix", self.prefix))

            display_handler = config.get_display_handler(element_name)
            element_wdg.add( HiddenWdg("handler", display_handler))


            element_wdg.add( HiddenWdg("element_name", element_name))
        

            from pyasm.widget import ExceptionWdg
            try:
                widget = config.get_display_widget(element_name)
                if widget:
                    widget.set_title(titles[i])

            except Exception as e:
                element_wdg.add(ExceptionWdg(e))
                continue


            if not widget:
                # the default for KeywordFilterElementWdg is mode=keyword
                if not self.column_choice:
                    self.column_choice = self.get_search_col(self.search_type)
                widget = KeywordFilterElementWdg(column=self.column_choice)
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

			
            view_panel_keywords = self.kwargs.get("keywords")
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
            except Exception as e:
                element_wdg.add(ExceptionWdg(e))
                continue
                


            icon = IconWdg("Filter Set", "BS_ASTERISK")
            #icon.add_style("color", "#393")
            icon_div.add(icon)
            icon.add_class("spt_filter_set")
            icon.add_class("hand")
            icon.add_attr("spt_element_name", element_name)

            icon.add_behavior( {
                'type': 'click',
                'cbjs_action': '''
                var element_name = bvr.src_el.getAttribute("spt_element_name");
                spt.simple_search.clear_element(element_name);
                '''

            } )

            if not widget.is_set():
                icon.add_style("display: none")

            else:
                color = icon_div.get_color("background", -10)
                icon_td.add_style("background-color", color)
                title_td.add_style("background-color", color)
                element_td.add_style("background-color", color)



        #elements_wdg.add("<br clear='all'/>")
        top = self.get_top()
        return top



    def get_search_wdg(self):
        search_div = DivWdg()

        if self.kwargs.get('run_search_bvr'):
            run_search_bvr = self.kwargs.get('run_search_bvr')
        else:
            run_search_bvr = {
                'type':         'click_up',
                'cbjs_action':  '''
                spt.simple_search.hide();
                spt.dg_table.search_cbk(evt, bvr);
                ''',
                'new_search':   True,
                'panel_id':     self.prefix
            }


        title = "Apply"

        button = ActionButtonWdg(title=title, tip='Run search with this criteria' )
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




    def get_onload_js(self):
        return r'''

spt.simple_search = {};

spt.simple_search.get_top = function() {
    var layout = spt.table.get_layout();
    var panel = layout.getParent(".spt_view_panel_top");
    var top = panel.getElement(".spt_simple_search");
    return top;
}


spt.simple_search.show = function() {
    var top = spt.simple_search.get_top();
    if (top) {
        top.setStyle("display", "");
        spt.body.add_focus_element(top);
    }
}

spt.simple_search.hide = function() {
    var top = spt.simple_search.get_top();
    if (top) {
        top.setStyle("display", "none");
    }
}


spt.simple_search.show_elements = function(element_names) {

    var top = spt.simple_search.get_top();

    var items = top.getElements(".spt_element_item")

    for (var i = 0; i < items.length; i++) {
        var element_name = items[i].getAttribute("spt_element_name");
        if (element_names.indexOf(element_name) != -1) {
            items[i].setStyle("display", ""); 
        }
        else {
            items[i].setStyle("display", "none"); 
        }
    }


}


spt.simple_search.has_element = function(element_name) {

    var flag = false;

    var top = spt.simple_search.get_top();
    if (!top) {
        return false;
    }

    var items = top.getElements(".spt_element_item")
    for (var i = 0; i < items.length; i++) {
        var item_element_name = items[i].getAttribute("spt_element_name");
        if (element_name == item_element_name) {
            flag = true;
            break
        }
    }

    return flag;
}



spt.simple_search.clear_element = function(element_name) {
    var top = spt.simple_search.get_top();

    var items = top.getElements(".spt_element_item")
    for (var i = 0; i < items.length; i++) {
        var item_element_name = items[i].getAttribute("spt_element_name");
        if (element_name == item_element_name) {
            spt.api.Utility.clear_inputs(items[i]);
            items[i].setStyle("background-color", "");

            var asterix = items[i].getElement(".spt_filter_set");
            if (asterix) {
                asterix.setStyle("display", "none");
            }
        }
    }
}



spt.simple_search.show_all_elements = function() {

    var top = spt.simple_search.get_top();
    var items = top.getElements(".spt_element_item")
    for (var i = 0; i < items.length; i++) {
        items[i].setStyle("display", ""); 
    }
}

spt.simple_search.hide_all_elements = function() {

    var top = spt.simple_search.get_top();
    var items = top.getElements(".spt_element_item")
    for (var i = 0; i < items.length; i++) {
        items[i].setStyle("display", "none"); 
    }
}

spt.simple_search.set_position = function(position) {
    var top = spt.simple_search.get_top();

    top.setStyle("top", position.y);
    top.setStyle("left", position.x);
}


spt.simple_search.show_title = function() {
    var top = spt.simple_search.get_top();
    var title_el = top.getElement(".spt_simple_search_title");
    title_el.setStyle("display", "");
}


spt.simple_search.hide_title = function() {
    var top = spt.simple_search.get_top();
    var title_el = top.getElement(".spt_simple_search_title");
    title_el.setStyle("display", "none");
}




        '''







