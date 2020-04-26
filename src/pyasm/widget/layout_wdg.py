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

__all__ = [
'EditException',
'TableException',
'LayoutException',
'BaseConfigWdg',
'TableWdg',
'TbodyWdg',
'TrWdg',
'LayoutWdg',
'SObjectLayoutWdg',
'EditWdg',
'InsertWdg',
'EditAllWdg',
'IconLayoutWdg',
'TableElementHideCmd',
'PublishWdg',
'InsertMultiWdg'
]


import string, sys, types

from pyasm.command import Command
from pyasm.prod.biz import ProdSetting
from pyasm.common import *
from pyasm.search import *
from pyasm.web import *
from icon_wdg import IconWdg, IconSubmitWdg
from web_wdg import InsertLinkWdg, HintWdg, WarningMenuWdg, HelpMenuWdg
from input_wdg import *
from file_wdg import *
from table_element_wdg import *
from search_limit_wdg import *
from widget_config import *
import inspect


class EditException(TacticException):
    pass

class TableException(TacticException):
    pass


class LayoutException(TacticException):
    pass
    
class BaseConfigWdg(HtmlElement):
    def __init__(self, search_type, config_base, input_prefix='', config=None):

        if type(search_type) in types.StringTypes:
            self.search_type_obj = SearchType.get(search_type)
            self.search_type = search_type
        elif isinstance(search_type, SearchType):
            self.search_type_obj = search_type
            self.search_type = self.search_type_obj.get_base_key() 
        elif inspect.isclass(search_type) and issubclass(search_type, SObject):
            self.search_type_obj = SearchType.get(search_type.SEARCH_TYPE)
            self.search_type = self.search_type_obj.get_base_key()
        else:
            raise LayoutException('search_type must be a string or an sobject')
        self.config = config
        self.config_base = config_base
        self.input_prefix = input_prefix
        self.element_names = []
        self.element_titles = []

        # Layout widgets compartmentalize their widgets in sections for drawing
        self.sections = {}

        super(BaseConfigWdg,self).__init__() 

    def get_default_display_handler(cls, element_name):
        raise Exception("Must override 'get_default_display_handler()'")
    get_default_display_handler = classmethod(get_default_display_handler)


    def get_config_base(self):
        return self.config_base

    def get_view(self):
        return self.config_base
        

    def init(self):

        # create all of the display elements
        if not self.config:
            self.config = WidgetConfigView.get_by_search_type(self.search_type_obj,self.config_base)
        self.element_names = self.config.get_element_names()
        self.element_titles = self.config.get_element_titles()  

        # TODO: should probably be all the attrs
        self.element_widths = self.config.get_element_widths()  

        invisible_elements = ProdSetting.get_seq_by_key("invisible_elements", self.search_type_obj.get_base_search_type() )

        simple_view = FilterCheckboxWdg('show_simple_view')
        
        # to register the checkbox toggle if it happens
        simple_view.is_checked(False)
        
        value = WidgetSettings.get_wdg_value(simple_view, 'show_simple_view')
        # account for on or on||on
        simple_view_checked = 'on' in value
        
        is_edit = self.config_base in ['edit','insert','insert_multi','insert_template','edit_template'] or self.input_prefix == 'edit'


        # go through each element name and construct the handlers
        for idx, element_name in enumerate(self.element_names):

            # check to see if these are removed for this production
            if element_name in invisible_elements:
                continue

            simple_element = None


            # build based on display widget
            display_handler = self.config.get_display_handler(element_name)
            if not display_handler:
                # else get it from default of this type
                display_handler = self.get_default_display_handler(element_name)

            #try:
            if not display_handler:
                element = self.config.get_display_widget(element_name)
            else:
                element = WidgetConfig.create_widget( display_handler )
            #except ImportError, e:
            #    # FIXME: not sure what to do with an import error here
            #    element = SimpleTableElementWdg()


            # only create simple_element if it is not edit and not FuncionalTableElement
            """ # disable DynamicTableElementWdg even in simple view
            if simple_view_checked and not is_edit and \
                not isinstance(element, FunctionalTableElement):
                simple_display_handler = "DynamicTableElementWdg"
                simple_element = WidgetConfig.create_widget( simple_display_handler )
            """
            # skip the empty elements like ThumbWdg
            if simple_element and not element.is_simple_viewable():
                continue
            # make simple_element the element if it exists
            if simple_element:
                element = simple_element
            # if the element failed to create, then continue
            if element == None:
                continue


            element.set_name(element_name)
            title = self.element_titles[idx]

            element.set_title(title)

            # TODO: should convert this to ATTRS or someting like that.  Not
            # just width
            element.width = self.element_widths[idx]

            if self.input_prefix:
                element.set_input_prefix(self.input_prefix)


            # get the display options
            display_options = self.config.get_display_options(element_name)
            for key in display_options.keys():
                element.set_option(key, display_options.get(key))

            self.add_widget(element,element_name)

            # layout widgets also categorize their widgets based on type
            if element_name == "Filter":
                section_name = 'filter'
            else:
                section_name = 'default'
            section = self.sections.get(section_name)
            if not section:
                section = []
                self.sections[section_name] = section
            section.append(element)


        # initialize all of the child widgets
        super(BaseConfigWdg,self).init()



    def rename_widget(self,name, new_name):
        widget = self.get_widget(name)
        widget.set_name(new_name)

    def remove_widget(self,name):
        widget = self.get_widget(name)
        try:
            self.widgets.remove(widget)
        except:
            print("WARNING: cannot remove widget")



# DEPRECATED
        
class TableWdg(BaseConfigWdg, AjaxWdg):

    ROW_PREFIX = 'table_row_'
    def __init__(self, search_type, config_base="table", css='table', header_css=None, config=None, is_dynamic=False):
        if not config_base:
            config_base = "table"

        # set the search type
        web = WebContainer.get_web()
        web.set_form_value("search_type", search_type)

        self.table = Table()
        self.table.is_dynamic(is_dynamic)
        self.widget_id = None
        self.table_id = None
        self.table.set_class(css)
        self.set_id(search_type)
        self.header_flag = True
        self.show_property = True
        self.header_css = header_css
        self.aux_data = []
        self.row_ids = {}

        self.content_height = 0
        self.content_width = ''
        self.no_results_wdg = HtmlElement.h2("Search produced no results")
        self.retired_filter = RetiredFilterWdg()
        limit_label = '%s_showing' %search_type
        limit_count = '%s_limit'%search_type
        self.search_limit_filter = SearchLimitWdg(name=limit_count, label=limit_label, limit=20)
        self.search_limit_filter_bottom = SearchLimitWdg(name=limit_count, label=limit_label, limit=20)
        self.search_limit_filter_bottom.set_style( SearchLimitWdg.SIMPLE )
   
        # This must be executed after the defaults to ensure that base
        # classes and ajax refreshes can override the above default settings
        super(TableWdg,self).__init__(search_type, config_base, config=config)

        self.order_by_wdg = HiddenWdg(self.get_order_by_id())
        self.order_by_wdg.set_persistence()

        self.refresh_mode = None

        # the sql statement that created this table
        self.sql_statement = None


    def set_id(self, id):
        self.table_id = id
        self.table.set_id(id)

    def get_order_by_id(self):
        return "order_by_%s" % self.search_type.replace("/","_")


    def set_no_results_wdg(self, wdg):
        self.no_results_wdg = wdg

    def set_refresh_mode(self, refresh_mode):
        assert refresh_mode in ['table', 'page']
        self.refresh_mode = refresh_mode

    def set_sql_statement(self, statement):
        self.sql_statement = statement


    def set_search_limit(self, limit):
        ''' minimum 20 as defined in SearchLimitWdg'''
        self.search_limit_filter.set_limit(limit)
        self.search_limit_filter_bottom.set_limit(limit)

    def set_aux_data(self, new_list):
        ''' this should be a list of dict corresponding to each sobject 
            in the TableWdg as auxilliary data'''

        if self.aux_data:
            for idx, item in enumerate(self.aux_data):
                new_dict = new_list[idx]
                for new_key, new_value in new_dict.items():
                    item[new_key] = new_value
        else:
            self.aux_data = new_list
       

    # DEPRECATED: use set_show_header
    def set_header_flag(self,flag):
        self.header_flag = flag

    def set_show_header(self,flag):
        self.header_flag = flag

    def set_show_property(self, flag):
        self.show_property = flag


    def check_security(self):
        widgets_to_remove = []
        for widget in self.widgets:
            try:
                # set the table first
                widget.set_parent_wdg(self)
                widget.check_security()
            except SecurityException:
                widgets_to_remove.append(widget)

        for widget in widgets_to_remove:
            self.widgets.remove(widget)


    def get_default_display_handler(cls, element_name):
        #return "DynamicTableElementWdg"
        return "tactic.ui.common.SimpleTableElementWdg"
    get_default_display_handler = classmethod(get_default_display_handler)

    def set_content_width(self, width):
        self.content_width = width

    def set_content_height(self, height):
        self.content_height = height

    def alter_search(self, search):
        if self.retired_filter.get_value() == 'true':
            search.set_show_retired(True)

        order_by = self.order_by_wdg.get_value()
        if order_by:
            success = search.add_order_by(order_by)
            if not success:
                self.order_by_wdg.set_value('default')


        # filters
        filters = self.sections.get("filter")
        if filters:
            for filter in filters:
                filter.alter_search(search)

        
        # IMPORTANT: search limit must come last
        self.search_limit_filter.alter_search(search)   
        self.search_limit_filter_bottom.alter_search(search)   

    def do_search(self):
        '''Perform any searches that were created in the init function.
        Returns a list of SObjects'''
        # if no search is defined in this class, then skip this
        # it does not inherit its parent's search until its parent
        # has obtained its search_objects
        if self.search != None:
            self.alter_search( self.search )
            self.sobjects = self.search.get_sobjects()


        # set the sobjects from this search
        if self.search != None:
            self.set_sobjects( self.sobjects, self.search )


    def init_cgi(self):
        web = WebContainer.get_web()
        search = Search(self.search_type)
        search_ids = web.get_form_value("search_ids")
        statement = web.get_form_value("statement")
        show_property = web.get_form_value("show_property")
        if show_property:
            if show_property == "True":
                self.show_property = True
            else:
                self.show_property = False

        if statement:
            sobjects = search.get_sobjects(statement=statement)
            self.set_sobjects( sobjects )


    def get_hide_column_wdg(self):
        return Widget()

        if not self.table_id:
            table_id = "table_%s" % self.widget_id
        else:
            table_id = self.table_id

        table = self.table
        table.set_id(table_id)
        div = DivWdg()

        popup = SpanWdg(css="popup")
        popup.add_style("display: none")
        popup.add_style("position: absolute")
        popup.set_id("popup_%s" % table_id)
        table = Table()
        for i, widget in enumerate(self.widgets):
            table.add_row()
            checkbox = CheckboxWdg("%s_column_%s" % (table_id,i) )
            checkbox.set_checked()
            checkbox.add_event("onclick", "var v=this.checked;toggle_column_display('%s', %s, v)" % (table_id, i) )
            table.add_cell( checkbox )
            table.add_cell( widget.title )
        popup.add(table)
        div.add(popup)

        span = SpanWdg("press me", css='hand')
        span.add_event("onclick", "toggle_display('popup_%s')" % table_id)
        div.add(span)

        return div


    def add_table_refresher(self, div):
        web = WebContainer.get_web()

        ajax = AjaxLoader()
        if ajax.is_refresh() and self.is_top:
            # reuse the id
            self.widget_id = ajax.get_refresh_id()
        else:
            # generate a new one
            unique = self.generate_unique_id('table', is_random=True)
            self.widget_id = "%s|%s" % (unique, self.search_type)

        div.add_style("display: block")
        div.set_id(self.widget_id)
        ajax.set_display_id(self.widget_id)
        args = [self.search_type, self.config_base]

        # try to reproduce the sql statement the produced the current contents
        if self.search:
            # use the search, if available ... best source
            ajax.set_option("statement", self.search.get_statement() )
        elif self.sql_statement:
            ajax.set_option("statement", self.sql_statement )
        else:
            # if not, then refresh the whole page, because we can't reproduce
            # the sql statements
            self.refresh_mode = "page"


        ajax.set_option("show_property", self.show_property )
        ajax.set_load_class("pyasm.widget.TableWdg", args)
        if not (ajax.is_refresh() and self.is_top):
            event_container = WebContainer.get_event_container()
            # if refresh mode is "table", then this table updates on every data
            # update
            if self.refresh_mode == "table":
                event_name = event_container.DATA_INSERT
                event_container.add_listener(event_name, ajax.get_refresh_script(show_progress=False) )
            elif self.refresh_mode == "page":
                event_name = event_container.DATA_INSERT
                event_container.add_refresh_listener(event_name)
            else:
                event_name = "refresh|%s" % self.search_type_obj.get_base_key()
                event_container.add_listener(event_name, ajax.get_refresh_script(show_progress=False) )
       



    def get_display(self):

        web = WebContainer.get_web()
        table = self.table

        # create the main div
        div = DivWdg()

        # create the filter div
        filters = self.sections.get("filter")
        if filters:
            filter_div = DivWdg(css="filter_box")
            div.add(filter_div)
            div.add_style("text-align: center")

            for filter in filters:

                span = SpanWdg(css="med")
                span.add("%s: " % filter.get_name())
                span.add(filter)
                filter_div.add(span)

                # HACK: remove the filter widgets
                self.widgets.remove(filter)



        # make it so that the TableWdg is reloadble
        self.add_table_refresher(div)
        

        if self.content_width:
            table.set_attr('width', self.content_width)
        else:
            # set a separate width for IE, which can't draw tables properly
            table.set_max_width()



        # go through each widget and detect if they are hidden or not
        #hidden = web.get_form_values("hidden_table_rows")
        #widgets_to_remove = []
        #for widget in self.widgets:
        #    if widget.name in hidden:
        #        widgets_to_remove.append(widget)
        #for widget in widgets_to_remove:
        #    self.widgets.remove(widget)

        # add columns
        for widget in self.widgets:
            # set the table
            widget.set_parent_wdg(self)

            col = table.add_col()
            width = widget.get_option("width")
            if width:
                col.set_attr("width", width)

        # allow widgets preprocess to preprocess information for all of the
        # rows
        for widget in self.widgets:
            widget.preprocess()

        # get the prefs before the header but display afterwards
        pref_widgets = []

        for widget in self.widgets:
            pref_widgets.append( widget.get_prefs() )
           
 
        # add the headers
        app_css = ''
        if WebContainer.get_web().get_app_name() != 'Browser':
            app_css = 'smaller'
        app_css = '%s %s' %(app_css, self.header_css)

        # if the header is being shown
        if self.header_flag:
            tr = table.add_row(css=app_css)
            # this prevents button in this row shifting all the elements 
            # when clicked
            tr.add_style('height','2.8em')
            order_value = self.order_by_wdg.get_value(for_display=True)


            for widget in self.widgets:
                title = widget.get_title()
                th_css = ''
                if widget.name == order_value:
                    th_css = 'ordered'
                th = table.add_header(title, th_css)


            # add a row for UI controls
            #tr = table.add_row(css=app_css)
            #for widget in self.widgets:
            #    #controls = widget.get_control_wdg()
            #    controls = widget.get_title()
            #    controls = '&nbsp;'
            #    th = table.add_cell(controls, css=th_css)


        # add hidden prefs row        
        prefs_row_id = self.generate_unique_id('hidden_row_prefs')
        action = "toggle_display('%s')" % prefs_row_id
        tr = table.add_row(css='hand prefs_row')
        tr.add_style('line-height: 1px')
        tr.add_event('onclick', action)
        
       
        for k in range (0, table.max_cols):
            td = None
            if not pref_widgets[k]:       
                td = table.add_blank_cell()
            else:
                td = table.add_cell(IconWdg('Show Prefs.', icon=IconWdg.PREF))
                td.add_style("text-align: center")
                            
        
        prefs_tr = table.add_row()
        prefs_tr.add_style('display: none')
        prefs_tr.set_id(prefs_row_id)
        
        for pref_widget in pref_widgets:
            table.add_cell( pref_widget )
            
        # add the rows for each sobject
        for i in range(0, len(self.sobjects)):
            # AuxDataWdg allows a NoneType in the array
            if self.sobjects[i] == None:
                continue

            self._add_prev_row(table, i)

            # add a tbody with an event container
            tbody = table.add_tbody()

            ajax = AjaxLoader()
            unique = self.generate_unique_id('tbody', is_random=True)
            search_key = self.sobjects[i].get_search_key()
            tbody_id = "%s|%s" % (unique,search_key)
            
            # used for some TableElementWdg
            self.row_ids[search_key] = tbody_id
            tbody.set_id(tbody_id)
            ajax.set_display_id(tbody_id)
            args = [self.search_type, self.config_base]
            ajax.set_load_class("pyasm.widget.layout_wdg.TbodyWdg", args)
            ajax.set_option("sthpw_edit", self.sobjects[i].get_search_key() )
            if not ajax.is_refresh():
                event_container = WebContainer.get_event_container()
                event_name = "refresh|%s" % self.sobjects[i].get_search_key()
                event_container.add_listener(event_name, ajax.get_refresh_script(show_progress=False) )
            #event_container = WebContainer.get_event_container()
            #event_name = "refresh|%s" % self.sobjects[i].get_search_key()
            #event_container.add_listener(event_name, ajax.get_refresh_script(show_progress=False) )

            # -- Reverted to previous row highlight code ... removed use of new UI behavior mechanism ...
            tr = table.add_row()
            if WebContainer.get_web().get_selected_app() != 'Browser':
                tr.add_event("onmouseover", "this.className='over'")
                tr.add_event("onmouseout", "this.className='out'")

            # FIXME: this does not work because our ajax refreshing of a widget
            # does not replace, but puts it under.  With tbody, this is harmless
            # but with tr, you get the undesirable effect of putting all the
            # refreshed cells in the first cell of the original table
            '''
            tr = HtmlElement.tr()
            tr = table.add_row(tr=tr)
            #tr_id = "tr|%s" % self.sobjects[i].get_search_key()
            tr_id = "%s%s" % (self.ROW_PREFIX, self.sobjects[i].get_search_key())
            tr.set_id(tr_id)
            ajax = AjaxLoader()
            ajax.set_display_id(tr_id)
            args = [self.search_type, self.config_base]
            ajax.set_load_class("pyasm.widget.TrWdg", args)
            ajax.set_option("sthpw_edit", self.sobjects[i].get_search_key() )
            if not ajax.is_refresh():
                event_container = WebContainer.get_event_container()
                event_name = "refresh|%s" % self.sobjects[i].get_search_key()
                event_container.add_listener(event_name, ajax.get_refresh_script(show_progress=False) )
            ''' 

            tr.add_style("border-top: 0px")
            #tr.add_class("table")
            if self.sobjects[i].is_retired():
                 tr.add_class("retired_row")
            tr.add_style("display", "table-row")
            row_id = "%s%s" % (self.ROW_PREFIX, self.sobjects[i].get_search_key())
            tr.set_id(row_id)

            hidden_row_wdgs = []
            for widget in self.widgets:
                 
                # custom handle security exceptions
                if widget.__class__.__name__ == "HiddenRowToggleWdg":
                    hidden_row_wdgs.append(widget)
                elif widget.__class__.__name__ == "CustomXmlWdg" and \
                        widget.get_child_widget_class() == "HiddenRowToggleWdg":
                    hidden_row_wdgs.append( widget.get_child_widget() )
                try:
                    # have to bake the widget in a new buffer
                    WebContainer.push_buffer()
                    # this calls the widget.display(), not Widget.display()
                    widget.explicit_display()
                    buffer = WebContainer.pop_buffer()
                    value = buffer.getvalue()
                    if value:
                        td = table.add_cell( value )
                    else:
                        td = table.add_blank_cell()

                    #td.add_event("onmouseover", "this.style.background = 'yellow'")
                    #td.add_event("onmouseout", "this.style.background = '#333'")


                    widget.handle_tr(tr)
                    widget.handle_td(td)


                # make sure the security exception does not hide the whole
                # table
                except SecurityException as e:
                    #table.add_cell("Security Denied: '%s'" % widget.__class__.__name__)
                    table.add_blank_cell()
                    pass
              
            
            table.add_hidden_row(hidden_row_wdgs) 
                           
        # display something if no records are found
        if len(self.sobjects) == 0:
            num_cols = len(self.widgets)

            table.add_row()

            td = table.add_cell(self.no_results_wdg)
            td.set_style("text-align: center")
            td.set_attr("colspan", num_cols)

        else:
            table.add_row()
            for widget in self.widgets:
                bottom_html = widget.get_bottom()
                td = table.add_cell(bottom_html)
                # the hidden widget can be used to store data or support the widget
                div.add(widget.get_hidden())

        # add the property div only if show_property is True
        if self.show_property:
            property_div = DivWdg(css='right smaller')
            property_div.add(SpanWdg('count: %s' %len(self.sobjects), css='small'))

            # add a hidden widget for purposes of storing ordering information
            property_div.add(self.order_by_wdg)
            order_span = SpanWdg('order: ')
            if self.search:
                order_span.add_tip('%s' %','.join(self.search.get_order_bys()))
            if order_value:
                order_span.add(order_value)
            else:
                order_span.add('default')
            property_div.add(order_span)

            simple_cb = FilterCheckboxWdg('show_simple_view', label='Simple View', css='med')
            simple_cb.add_event('onclick',"get_elements('show_simple_view').toggle_all(this)")
            property_div.add(simple_cb)

            # add the csv export button
            from icon_wdg import IconButtonWdg
            export = IconButtonWdg("CSV Export", IconWdg.SAVE, False)
            property_div.add(export)

            # add the hide column widget
            property_div.add(self.get_hide_column_wdg())


            # add csv export
            filename = "%s_%s.csv" % (self.search_type.replace("/","_"), self.config_base)
            url = WebContainer.get_web().get_widget_url()
            url.set_option("dynamic_file", "true")
            url.set_option("widget", "pyasm.widget.CsvDownloadWdg")
            url.set_option("search_type", self.search_type)
            url.set_option("view", self.config_base)
            url.set_option("filename", filename)

            # remember all of the sobject keys
            # TODO: need to make this a post request so that we can store
            # any number of search_ids
            search_ids = [str(x.get_id()) for x in self.sobjects ]
            url.set_option("search_ids", "|".join(search_ids) )

            export.add_event("onclick", "document.location='%s'" % url.to_string() )


            # TEST Pic lens plugin
            #export = IconButtonWdg("Start PicLens Player", IconWdg.PICLENS, False)
            #property_div.add(export)
            url = WebContainer.get_web().get_widget_url()
            url.set_option("dynamic_file", "true")
            url.set_option("widget", "pyasm.widget.PicLensRssWdg")
            url.set_option("search_type", self.search_type)
            # remember all of the sobject keys
            # TODO: need to make this a post request so that we can store
            # any number of search_ids
            search_ids = [str(x.get_id()) for x in self.sobjects ]
            url.set_option("search_ids", "|".join(search_ids) )

            #export.add_event("onclick", "PicLensLite.start()")

            # FIXME: it appears that the link tag makes an http so the
            # display image library is called for every refresh.
            property_div.add('''
            <script type="text/javascript" src="/context/javascript/piclens.js"></script>
            <link rel="alternate" href="%s" type="application/rss+xml" title="" id="gallery" />
            ''' % url.to_string())






            div.add(property_div)
            if self.search: 
                property_div.add(self.retired_filter)
                property_div.add(self.search_limit_filter)


        div.add(table)
        self.add_table_inputs(div)

        if self.search:
            bottom_div = DivWdg()
            bottom_div.set_style("text-align: right")
            bottom_div.add(self.search_limit_filter_bottom)
            div.add(bottom_div)

        # set content height
        if self.content_height:
            div.add_style("height: %spx" % self.content_height)
            div.add_style("overflow: auto")
        return div

    def add_table_inputs(self, widget):      
        ''' add some inputs used by DynamicTableElementWdg'''
        hidden = HiddenWdg('skey_DynamicTableElementWdg')
        widget.add(hidden)
        hidden = HiddenWdg('attr_DynamicTableElementWdg')
        widget.add(hidden)
        hidden = HiddenWdg('update_DynamicTableElementWdg')
        widget.add(hidden)

    def _add_prev_row(self, table, idx):
        prev_sobj = None
        if idx > 0:
            prev_sobj = self.sobjects[idx-1]
           
        for widget in self.widgets:
            # set the index here instead
            widget.set_current_index(idx)
            widget.add_prev_row(table, prev_sobj)   


class TableElementHideCmd(Command):

    def set_search_type(self, search_type):
        self.search_type = search_type

    def execute(self):
        web = WebContainer.get_web()
        invisible = web.get_form_value("invisible")
        if not invisible:
            return

        ProdSetting.add_value_by_key("invisible_elements", invisible, self.search_type)

        title = SearchType.get(self.search_type).get_title()

        self.description = "Hid column %s for %s" % (invisible, title)


      

class TbodyWdg(TableWdg, AjaxWdg):
    '''A widget that represents a section of a TableWdg used to replace a tbody in a table'''
   
    def __init__(self, search_type, config_base="tbody", css=None, header_css=None):
        if not config_base:
            config_base = "table"
        self.search_ids = None 

        TableWdg.__init__(self, search_type, config_base)
        AjaxWdg.__init__(self)

    def init_cgi(self):
        edit_ids = self.web.get_form_values('sthpw_edit')

        # these may contain search_keys
        self.search_ids = []
        for edit_id in edit_ids:
            if edit_id.count("|") == 1:
                search_type, edit_id = edit_id.split("|",1)
            self.search_ids.append(edit_id)
            
    def get_display(self):
        if not self.search_ids or self.search_ids == ['']:
            return ''

        tbody = Tbody()
    
        for widget in self.widgets:
            # set the parent wdg
            widget.set_parent_wdg(self)

        if not self.sobjects:
            self.sobjects = Search.get_by_id(self.search_type, self.search_ids)
        
        for widget in self.widgets:
            widget.set_sobjects(self.sobjects)

        # allow widgets preprocess to preprocess information for all of the
        # rows
        for widget in self.widgets:
            widget.preprocess()
 
        # add the rows for each sobject
        for i in range(0, len(self.sobjects)):
            # AuxDataWdg allows a NoneType in the array
            if self.sobjects[i] == None:
                continue
            #self._add_prev_row(tbody, i)
            
            tr = tbody.add_row()
            tr.add_style("border-top: 0px")
            tr.add_style("display", "table-row")
            
            tr.set_id("%s%s" % (self.ROW_PREFIX, self.sobjects[i].get_search_key()) )

            hidden_row_wdgs = []
            for widget in self.widgets:
                widget.set_current_index(i)
                # custom handle security exceptions
                if widget.__class__.__name__ == "HiddenRowToggleWdg":
                    hidden_row_wdgs.append(widget)
                try:
                    # have to bake the widget in a new buffer
                    WebContainer.push_buffer()
                    # this calls the widget.display(), not Widget.display()
                    widget.explicit_display()
                    buffer = WebContainer.pop_buffer()
                    value = buffer.getvalue()
                    if value:
                        td = tbody.add_cell( value )
                    else:
                        td = tbody.add_blank_cell()

                    widget.handle_tr(tr)
                    widget.handle_td(td)

                # make sure the security exception does not hide the whole tbody
                
                except SecurityException as e:
                    tbody.add_blank_cell()
                    pass
            
            tbody.add_hidden_row(hidden_row_wdgs) 
                           
        # display something if no records are found
        if len(self.sobjects) == 0:
            num_cols = len(self.widgets)

            tbody.add_row()

            td = tbody.add_cell("Search produced no results")
            td.set_style("text-align: center")
            td.set_attr("colspan", num_cols)

       
        return tbody



class TrWdg(TbodyWdg):
    '''A widget that represents a row of a TableWdg used to replace a tr in a table'''
    def get_display(self):
        if not self.search_ids or self.search_ids == ['']:
            return ''

        # set the index to 0
        i = 0
        ajax = AjaxLoader()
        if ajax.is_refresh():
            tr = HtmlElement.tr()
        else:
            tr = HtmlElement.tr()
            tr.add_style("border-top: 0px")
            tr.add_style("display", "table-row")
            

            if self.sobjects:
                tr.set_id("%s%s" % (self.ROW_PREFIX, self.sobjects[i].get_search_key()) )
        for widget in self.widgets:
            # set the parent wdg
            widget.set_parent_wdg(self)

        if not self.sobjects:
            self.sobjects = Search.get_by_id(self.search_type, self.search_ids)
        
        for widget in self.widgets:
            widget.set_sobjects(self.sobjects)

        # allow widgets preprocess to preprocess information for all of the
        # rows
        for widget in self.widgets:
            widget.preprocess()
 

        
     
       
        
        hidden_row_wdgs = []
        for widget in self.widgets:
            widget.set_current_index(i)
            try:
                # have to bake the widget in a new buffer
                WebContainer.push_buffer()
                # this calls the widget.display(), not Widget.display()
                widget.explicit_display()
                buffer = WebContainer.pop_buffer()
                value = buffer.getvalue()
                if value:
                    td = HtmlElement.td( value )
                else:
                    td = HtmlElement.td("&nbsp;")
                tr.add(td)

                widget.handle_tr(tr)
                widget.handle_td(td)

            # make sure the security exception does not hide the whole tbody
            
            except SecurityException as e:
                td = HtmlElement.td()
                td.add("&nbsp;")
                pass
        
                           
        # display something if no records are found
        if len(self.sobjects) == 0:
            num_cols = len(self.widgets)

            td = HtmlElement.td()
            td.add("Search produced no results")
            td.set_style("text-align: center")
            td.set_attr("colspan", num_cols)
      
        return tr





class LayoutWdg(DivWdg):
    def __init__(self, search_type):
        super(LayoutWdg,self).__init__()
        self.layout_cells = {}


    def get_display(self):

        table = Table()

        self.set_layout(table)

        for cell_name, cell in self.layout_cells.items():
            self.set_content(cell_name, cell)

        self.add(table)

        return super(LayoutWdg,self).get_display()

    
    def set_cell( self, td, title ):
        self.layout_cells[title] = td

            
    def set_layout(self, table):
        table.add_row()
        td = table.add_cell()
        self.set_cell(td, 'header')

        table.add_row()
        td = table.add_cell()
        td.add_style("width: 150px")
        td.set_attr("valign", "top")
        self.set_cell(td, 'left')

        td = table.add_cell()
        td.add_style("padding", "5px")
        self.set_cell(td, 'right')



    def set_content(self,cell_name,cell):
        function = "get_cell_%s" % cell_name
        try:
            # test existance of functions
            wdg = eval( "self.%s" % function )
        except AttributeError:
            wdg = function
        else:
            wdg = eval( "self.%s()" % function )

        cell.add( wdg )







class SObjectLayoutWdg(BaseConfigWdg):
    def __init__(self, search_type):
        super(SObjectLayoutWdg,self).__init__(search_type,"layout")

        self.layout_cells = {}


    def get_default_display_handler(cls, element_name):
        return "SimpleTableElementWdg"
    get_default_display_handler = classmethod(get_default_display_handler)


    def get_display(self):

        div = HtmlElement.div()

        index = 0
        for sobject in self.sobjects:

            table = Table()
            table.add_style("border-style: solid")
            table.add_style("border-width: 1px")
            table.add_style("margin-bottom: 15px")

            self.set_layout(table)

            for cell_name, cell in self.layout_cells.items():
                self.set_content(sobject, cell_name, cell)

            div.add(table)

            index += 1

        self.add(div)

        return super(SObjectLayoutWdg,self).get_display()


            
    def set_layout(self, table):
        table.add_row()
        td = table.add_cell()
        td.set_attr("colspan", "2")
        td.add_style("background-color", "#f0f0f0")
        self.layout_cells['title'] = td

        table.add_row()
        td = table.add_cell()
        self.layout_cells['icon'] = td

        td = table.add_cell()
        td.set_attr("valign", "top")
        td.add_style("width", "400px")
        self.layout_cells['discussion'] = td



    def set_content(self,sobject,cell_name,cell):
        function = "get_cell_%s" % cell_name
        try:
            # test existance of functions
            wdg = eval( "self.%s" % function )
        except AttributeError:
            wdg = function
        else:
            wdg = eval( "self.%s(sobject)" % function )

        cell.add( wdg )





class EditWdg(BaseConfigWdg):

    CLOSE_WDG = "close_wdg"

    def __init__(self, search_type,base_config="edit", input_prefix='edit',config=None, default_action_handler=None):
        self.current_id = -1
        if not default_action_handler:
            self.default_action_handler = "pyasm.command.EditCmd"
        else:   
            self.default_action_handler = default_action_handler

        super(EditWdg,self).__init__(search_type,base_config, input_prefix=input_prefix,config=config)

    def get_default_display_handler(cls, element_name):
        # FIXME: should use type from database
        if element_name == "timestamp":
            column_type = "timestamp"
        elif element_name == "description":
            column_type = "text"
        else:
            column_type = "normal"


        if column_type == "timestamp":
            return "pyasm.widget.CalendarWdg"
        elif column_type == "text":
            return "pyasm.widget.TextAreaWdg"
        else:
            return "pyasm.widget.TextWdg"

    get_default_display_handler = classmethod(get_default_display_handler)


    def set_default_action_handler(self, handler):
        self.default_action_handler = handler


    def get_default_action_handler(self):
        web = WebContainer.get_web()
        action = web.get_form_value("action")
        if action:
            return action
        else:
            return self.default_action_handler


    def init(self):
        super(EditWdg,self).init()
        web = WebContainer.get_web()

        # if we have edit/close and it's error-free, then do nothing
        #if self.is_error_free(web):
        #    return

        id = web.get_form_value("search_id")
        if id == "" or id == "-1":
            self.mode = "insert"
        else:
            self.mode = "edit"

        # this can be set to True to force a full page refresh instead of an
        # event refresh
        self.refresh_mode = web.get_form_value("refresh_mode")

       
        # get the edit command
        edit_action_handler = self.get_default_action_handler()
        WebContainer.register_cmd(edit_action_handler)

        # for Edit/Next ... remember last sobject edited
        self.last_sobject = None




    def do_search(self):
        '''this widget has its own search mechanism'''

        web = WebContainer.get_web()
        
        # get the sobject that is to be edited
        id = web.get_form_value("search_id")

        # if no id is given, then create a new one for insert
        search = None
        sobject = None
        search_type_base = SearchType.get(self.search_type).get_base_key()
        if self.mode == "insert":
            sobject = SObjectFactory.create(self.search_type)
            self.current_id = -1
            # prefilling default values if available
            url_dict = web.get_form_value("url_dict")
            if url_dict:
                url_list = url_dict.split('||')
                for x in url_list:
                    key, value = x.split(':', 1)
                    sobject.set_value(key, value)
        else:
            search = Search(self.search_type)

            # figure out which id to search for
            if web.get_form_value("do_edit") == "Edit/Next":
                search_ids = web.get_form_value("%s_search_ids" %search_type_base)
                if search_ids == "":
                    self.current_id = id
                else:
                    search_ids = search_ids.split("|")
                    next = search_ids.index(str(id)) + 1
                    if next == len(search_ids):
                        next = 0
                    self.current_id = search_ids[next]

                    last_search = Search(self.search_type)
                    last_search.add_id_filter( id )
                    self.last_sobject = last_search.get_sobject()

            else:
                self.current_id = id

            search.add_id_filter( self.current_id )
            sobject = search.get_sobject()

        if not sobject:
            raise EditException("No SObject found")

        # set all of the widgets to contain this sobject
        self.set_sobjects( [sobject], search )
       

    def is_error_free(self, web):
        ''' if it is instructed to close and is error-free , return True'''
        if web.get_form_value(self.CLOSE_WDG) and\
            not Container.get("cmd_report").get_errors():
            return True

        return False

    def add_header(self, table, title):
        th = table.add_header( self.mode.capitalize() + " - " + title )
        th.set_attr("colspan", "2")
        
    def add_hidden_inputs(self, div):
        pass

    def get_display(self):

        web = WebContainer.get_web()
        event_container = WebContainer.get_event_container()

        layout = web.get_form_value("layout")
        if not layout:
            layout = "default"
       
        div = HtmlElement.div()

        # remember the action
        edit_action_handler = self.get_default_action_handler()
        div.add( HiddenWdg("action",edit_action_handler) )

        self.iframe = WebContainer.get_iframe(layout)
        if web.get_form_value("do_edit") == "Edit/Next" and self.last_sobject:
            search_key = self.last_sobject.get_search_key()
            refresh_script = "window.parent.%s" % event_container.get_event_caller("refresh|%s" % search_key )
            div.add(HtmlElement.script(refresh_script))


        elif self.is_error_free(web):
            
            # multi-edit always refreshes table
            selected_keys = web.get_form_value(EditCheckboxWdg.CB_NAME)
            if self.refresh_mode == "page" or web.is_IE():
                refresh_script = "window.parent.%s" % event_container.get_refresh_caller()
            elif selected_keys or self.mode == "insert":
                refresh_script = "window.parent.%s" % event_container.get_event_caller("refresh|%s" % self.search_type )
                refresh_script = "%s;window.parent.%s" % (refresh_script, event_container.get_data_insert_caller())
            elif self.mode == "edit":
                search_key = self.sobjects[0].get_search_key()
                refresh_script = "window.parent.%s" % event_container.get_event_caller("refresh|%s" % search_key )
                #print(refresh_script)
            else:
                refresh_script = "window.parent.%s" % event_container.get_refresh_caller()

            undo_script = "window.parent.%s" % event_container.get_event_caller("SiteMenuWdg_refresh")

            off_script = "window.parent.%s" % self.iframe.get_off_script()

            script = HtmlElement.script('''
            %s
            %s
            %s
            ''' % (off_script, refresh_script, undo_script )  )
            return script
        

        search_type_obj = SearchType.get(self.search_type)
        title = search_type_obj.get_title()

        div.add( HiddenWdg("search_type",self.search_type) )
        div.add( HiddenWdg("search_id",self.current_id).get_display() )
        div.add( HiddenWdg(self.CLOSE_WDG) )
        self.add_hidden_inputs(div)        

        table = Table(css='edit')
        table.center()
        
        table.add_row()
        self.add_header(table, title)
        
        security = Environment.get_security()

        # go through each widget and draw it
        for widget in self.widgets:
            # check security on widget
            if not security.check_access( "sobject|column",\
                widget.get_name(), "edit"):
                continue
            
            if isinstance(widget, HiddenWdg):
                div.add(widget)
                continue

            table.add_row()

            show_title = (widget.get_option("show_title") != "false")
            if show_title:
                title = widget.get_title()
                #if title == None:
                #    continue
                table.add_cell(title)

            

            
            
          
            if not show_title:
                table.add_row_cell( widget )
                continue
            else:
                table.add_cell( widget )
                hint = widget.get_option("hint")
                if hint:
                    table.add_data( HintWdg(hint) ) 
            edit_all = widget.get_option("edit_all")
            insert_multi = widget.get_option("insert_multi")
            if self.mode == "edit" and edit_all == 'true':
                table.add_cell( EditAllWdg(widget), css="right_content" )
            elif self.mode == "insert" and insert_multi == 'true':
                table.add_cell( InsertMultiWdg(widget), css="right_content" )
            else:
                table.add_blank_cell()

        table.add_row_cell( self.get_action_html() )

        div.add( table )
        # add the warning menu for the iframe
        div.add( WarningMenuWdg())
        help_menu = HelpMenuWdg()

        div.add(help_menu.get_panel())
        return div



    def get_action_html(self):
        
        edit = SubmitWdg("do_edit", "%s/Next" % self.mode.capitalize() )
        edit_continue = SubmitWdg("do_edit", "%s/Close" % self.mode.capitalize() )
        
        edit_continue.add_event("onclick", "document.form.%s.value='true'" %self.CLOSE_WDG)
        
        # call an edit event
        event = WebContainer.get_event("sthpw:submit")
        edit.add_event( "onclick", event.get_caller() )
        #edit_continue.add_event( "onclick", event.get_caller() )

        # create a cancel button to close the window
        cancel = ButtonWdg(_("Cancel"))
        iframe_close_script = "window.parent.%s" % self.iframe.get_off_script() 
        cancel.add_event("onclick", iframe_close_script)

        div = DivWdg(css='centered')
        
        div.center()
        web = WebContainer.get_web()
        selected_keys = web.get_form_value(EditCheckboxWdg.CB_NAME)
        if not selected_keys:
            div.add(SpanWdg(edit, css='med'))
            div.add(SpanWdg(edit_continue, css='med'))
        div.add(SpanWdg(cancel, css='med'))

        return div
    
class InsertWdg(EditWdg):
    ''' Almost like the EditWdg, but with a different logic for hiding the 
        Insert/Close button'''
    def get_action_html(self):
        
        edit = SubmitWdg("do_edit", "%s/Next" % self.mode.capitalize() )
        edit_continue = SubmitWdg("do_edit", "%s/Close" % self.mode.capitalize() )
        
        edit_continue.add_event("onclick", "document.form.%s.value='true'" %self.CLOSE_WDG)
        
        # call an edit event
        event = WebContainer.get_event("sthpw:submit")
        edit.add_event( "onclick", event.get_caller() )
        #edit_continue.add_event( "onclick", event.get_caller() )

        # create a cancel button to close the window
        cancel = ButtonWdg(_("Cancel"))
        iframe_close_script = "window.parent.%s" % self.iframe.get_off_script() 
        cancel.add_event("onclick", iframe_close_script)

        div = DivWdg(css='centered')
        
        div.center()
        web = WebContainer.get_web()
        
        insert_multi = web.get_form_value(UpdateWdg.INSERT_MULTI)
        if not insert_multi:
            div.add(SpanWdg(edit, css='med'))
            div.add(SpanWdg(edit_continue, css='med'))
        div.add(SpanWdg(cancel, css='med'))

        return div

class PublishWdg(EditWdg):
    ''' a dialog widget for manual publishing '''
    def __init__(self, search_type, base_config="edit", input_prefix='edit',config=None, commit=False):
        super(PublishWdg, self).__init__(search_type, base_config, input_prefix=input_prefix,config=config)
        self.commit_flag = commit

    

class IconLayoutWdg(BaseConfigWdg):

    def __init__(self, search_type):
        super(IconLayoutWdg,self).__init__(search_type,"asset")
        self.category_col = None
        self.shot_edit_flag = True

    def set_category(self, category):
        self.category_col = category

    def set_show_edit(self, show_edit_flag):
        self.show_edit_flag = show_edit_flag


    def alter_search(self, search):
        if self.category_col != None:
            search.add_order_by(self.category_col)


    def get_display(self):

        # preprocess through all of the sobjects to find the categories
        # to be displayed
        #categories = []
        #for sobject in self.sobjects:
        #    category = sobject.get_value( self.category_col )
        #    if category not in categories:
        #        categories.append(category)

        num_cols = 4
        num_sobjects = len(self.sobjects)

        web = WebContainer.get_web()

        table = Table()
        table.set_attr("cellspacing", "0")

        # set a separate width for IE, which can't draw tables properly
        if web.is_IE():
            table.add_style("width", "100%")
        else:
            table.add_style("width", "95%")


        self.last_category = None
        col_count = 0
        for i in range(0, num_sobjects):

            sobject = self.sobjects[i]

            # handle category
            if self.category_col != None:
                category = sobject.get_value( self.category_col )

                if self.last_category == None or category != self.last_category:
                    # fill in the rest
                    if self.last_category != None:
                        for i in range(col_count, num_cols):
                            td = table.add_cell("&nbsp;")

                    self.add_category(table, category )
                    table.add_row()

                    col_count = 0
                    self.last_category = category

                elif col_count == num_cols:
                    table.add_row()
                    col_count = 0
            else:
                if col_count == num_cols:
                    table.add_row()
                    col_count = 0


            td = table.add_cell()
            td.add( self.get_sobject_wdg(sobject) )

            col_count += 1

        return table.get_display()




    def get_sobject_wdg(self, sobject):

        table = Table()
        td = table.add_cell()

        thumb = ThumbWdg("files")
        thumb.set_sobject(sobject)
        td.add(thumb)

        from annotate_wdg import AnnotateLink
        annotate = AnnotateLink("annotate")
        annotate.set_sobject(sobject)
        td.add(annotate)

        from sbell import AssetDetailLink
        detail = AssetDetailLink("detail")
        detail.set_sobject(sobject)
        td.add(detail)

        if self.show_edit_flag:
            update = UpdateWdg("update")
            update.set_sobject(sobject)
            td.add(update)

        return table



    def add_category(self, table, category):

        if category == "":
            category = "No category"

        table.add_row()

        div = HtmlElement.div()
        div.add_style("font-weight", "bold")
        div.add_style("font-size", "1.2em")
        div.add_style("padding-left", "3px")
        div.add_style("padding-bottom", "3px")


        if self.show_edit_flag:
            insert = InsertLinkWdg(self.search_type)
            insert.add_style("float", "right")
            div.add(insert)

        div.add(category)

        cell = table.add_cell(div)

        cell.set_attr("colspan", 4)
        table.add_row()


class EditAllWdg(Widget):

    ELEMENT_NAME = "edit_all_element"
    EDIT_ALL = "edit_all"
        
    def __init__(self, widget):
        self.edit_element = widget
        super(EditAllWdg, self).__init__()
        
    def class_init(self):
        self.add(HiddenWdg(self.ELEMENT_NAME))
        self.add(HiddenWdg(self.EDIT_ALL))
        WebContainer.register_cmd('pyasm.command.EditAllCmd')
        
    def init(self):
       
        icon = IconSubmitWdg(self.EDIT_ALL, icon=IconWdg.EDIT_ALL, add_hidden=False)
        icon.add_event("onclick", "document.form.elements['%s'].value='%s';"\
            % (self.ELEMENT_NAME, self.edit_element.name))
        icon.add_event("onclick", "document.form.%s.value='true'" %EditWdg.CLOSE_WDG)
        icon.add_class('hand')

        self.add(icon)

class InsertMultiWdg(Widget):

    ELEMENT_NAME = "insert_multi_element"
    INSERT_MULTI = "insert_multi"
        
    def __init__(self, widget):
        self.edit_element = widget
        super(InsertMultiWdg, self).__init__()
        
    def class_init(self):
        self.add(HiddenWdg(self.ELEMENT_NAME))
        self.add(HiddenWdg(self.INSERT_MULTI))
        WebContainer.register_cmd('pyasm.command.InsertMultiCmd')
        
    def init(self):
        icon = IconSubmitWdg(self.INSERT_MULTI, icon=IconWdg.INSERT_MULTI, add_hidden=False)
        icon.add_event("onclick", "document.form.elements['%s'].value='%s';"\
            % (self.ELEMENT_NAME, self.edit_element.name))
        icon.add_event("onclick", "document.form.%s.value='true'" %EditWdg.CLOSE_WDG)
        icon.add_class('hand')

        self.add(icon)
