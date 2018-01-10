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
    def __init__(my, search_type, config_base, input_prefix='', config=None):

        if type(search_type) in types.StringTypes:
            my.search_type_obj = SearchType.get(search_type)
            my.search_type = search_type
        elif isinstance(search_type, SearchType):
            my.search_type_obj = search_type
            my.search_type = my.search_type_obj.get_base_key() 
        elif inspect.isclass(search_type) and issubclass(search_type, SObject):
            my.search_type_obj = SearchType.get(search_type.SEARCH_TYPE)
            my.search_type = my.search_type_obj.get_base_key()
        else:
            raise LayoutException('search_type must be a string or an sobject')
        my.config = config
        my.config_base = config_base
        my.input_prefix = input_prefix
        my.element_names = []
        my.element_titles = []

        # Layout widgets compartmentalize their widgets in sections for drawing
        my.sections = {}

        super(BaseConfigWdg,my).__init__() 

    def get_default_display_handler(cls, element_name):
        raise Exception("Must override 'get_default_display_handler()'")
    get_default_display_handler = classmethod(get_default_display_handler)


    def get_config_base(my):
        return my.config_base

    def get_view(my):
        return my.config_base
        

    def init(my):

        # create all of the display elements
        if not my.config:
            my.config = WidgetConfigView.get_by_search_type(my.search_type_obj,my.config_base)
        my.element_names = my.config.get_element_names()
        my.element_titles = my.config.get_element_titles()  

        # TODO: should probably be all the attrs
        my.element_widths = my.config.get_element_widths()  

        invisible_elements = ProdSetting.get_seq_by_key("invisible_elements", my.search_type_obj.get_base_search_type() )

        simple_view = FilterCheckboxWdg('show_simple_view')
        
        # to register the checkbox toggle if it happens
        simple_view.is_checked(False)
        
        value = WidgetSettings.get_wdg_value(simple_view, 'show_simple_view')
        # account for on or on||on
        simple_view_checked = 'on' in value
        
        is_edit = my.config_base in ['edit','insert','insert_multi','insert_template','edit_template'] or my.input_prefix == 'edit'


        # go through each element name and construct the handlers
        for idx, element_name in enumerate(my.element_names):

            # check to see if these are removed for this production
            if element_name in invisible_elements:
                continue

            simple_element = None


            # build based on display widget
            display_handler = my.config.get_display_handler(element_name)
            if not display_handler:
                # else get it from default of this type
                display_handler = my.get_default_display_handler(element_name)

            #try:
            if not display_handler:
                element = my.config.get_display_widget(element_name)
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
            title = my.element_titles[idx]

            element.set_title(title)

            # TODO: should convert this to ATTRS or someting like that.  Not
            # just width
            element.width = my.element_widths[idx]

            if my.input_prefix:
                element.set_input_prefix(my.input_prefix)


            # get the display options
            display_options = my.config.get_display_options(element_name)
            for key in display_options.keys():
                element.set_option(key, display_options.get(key))

            my.add_widget(element,element_name)

            # layout widgets also categorize their widgets based on type
            if element_name == "Filter":
                section_name = 'filter'
            else:
                section_name = 'default'
            section = my.sections.get(section_name)
            if not section:
                section = []
                my.sections[section_name] = section
            section.append(element)


        # initialize all of the child widgets
        super(BaseConfigWdg,my).init()



    def rename_widget(my,name, new_name):
        widget = my.get_widget(name)
        widget.set_name(new_name)

    def remove_widget(my,name):
        widget = my.get_widget(name)
        try:
            my.widgets.remove(widget)
        except:
            print("WARNING: cannot remove widget")



# DEPRECATED
        
class TableWdg(BaseConfigWdg, AjaxWdg):

    ROW_PREFIX = 'table_row_'
    def __init__(my, search_type, config_base="table", css='table', header_css=None, config=None, is_dynamic=False):
        if not config_base:
            config_base = "table"

        # set the search type
        web = WebContainer.get_web()
        web.set_form_value("search_type", search_type)

        my.table = Table()
        my.table.is_dynamic(is_dynamic)
        my.widget_id = None
        my.table_id = None
        my.table.set_class(css)
        my.set_id(search_type)
        my.header_flag = True
        my.show_property = True
        my.header_css = header_css
        my.aux_data = []
        my.row_ids = {}

        my.content_height = 0
        my.content_width = ''
        my.no_results_wdg = HtmlElement.h2("Search produced no results")
        my.retired_filter = RetiredFilterWdg()
        limit_label = '%s_showing' %search_type
        limit_count = '%s_limit'%search_type
        my.search_limit_filter = SearchLimitWdg(name=limit_count, label=limit_label, limit=20)
        my.search_limit_filter_bottom = SearchLimitWdg(name=limit_count, label=limit_label, limit=20)
        my.search_limit_filter_bottom.set_style( SearchLimitWdg.SIMPLE )
   
        # This must be executed after the defaults to ensure that base
        # classes and ajax refreshes can override the above default settings
        super(TableWdg,my).__init__(search_type, config_base, config=config)

        my.order_by_wdg = HiddenWdg(my.get_order_by_id())
        my.order_by_wdg.set_persistence()

        my.refresh_mode = None

        # the sql statement that created this table
        my.sql_statement = None


    def set_id(my, id):
        my.table_id = id
        my.table.set_id(id)

    def get_order_by_id(my):
        return "order_by_%s" % my.search_type.replace("/","_")


    def set_no_results_wdg(my, wdg):
        my.no_results_wdg = wdg

    def set_refresh_mode(my, refresh_mode):
        assert refresh_mode in ['table', 'page']
        my.refresh_mode = refresh_mode

    def set_sql_statement(my, statement):
        my.sql_statement = statement


    def set_search_limit(my, limit):
        ''' minimum 20 as defined in SearchLimitWdg'''
        my.search_limit_filter.set_limit(limit)
        my.search_limit_filter_bottom.set_limit(limit)

    def set_aux_data(my, new_list):
        ''' this should be a list of dict corresponding to each sobject 
            in the TableWdg as auxilliary data'''

        if my.aux_data:
            for idx, item in enumerate(my.aux_data):
                new_dict = new_list[idx]
                for new_key, new_value in new_dict.items():
                    item[new_key] = new_value
        else:
            my.aux_data = new_list
       

    # DEPRECATED: use set_show_header
    def set_header_flag(my,flag):
        my.header_flag = flag

    def set_show_header(my,flag):
        my.header_flag = flag

    def set_show_property(my, flag):
        my.show_property = flag


    def check_security(my):
        widgets_to_remove = []
        for widget in my.widgets:
            try:
                # set the table first
                widget.set_parent_wdg(my)
                widget.check_security()
            except SecurityException:
                widgets_to_remove.append(widget)

        for widget in widgets_to_remove:
            my.widgets.remove(widget)


    def get_default_display_handler(cls, element_name):
        #return "DynamicTableElementWdg"
        return "tactic.ui.common.SimpleTableElementWdg"
    get_default_display_handler = classmethod(get_default_display_handler)

    def set_content_width(my, width):
        my.content_width = width

    def set_content_height(my, height):
        my.content_height = height

    def alter_search(my, search):
        if my.retired_filter.get_value() == 'true':
            search.set_show_retired(True)

        order_by = my.order_by_wdg.get_value()
        if order_by:
            success = search.add_order_by(order_by)
            if not success:
                my.order_by_wdg.set_value('default')


        # filters
        filters = my.sections.get("filter")
        if filters:
            for filter in filters:
                filter.alter_search(search)

        
        # IMPORTANT: search limit must come last
        my.search_limit_filter.alter_search(search)   
        my.search_limit_filter_bottom.alter_search(search)   

    def do_search(my):
        '''Perform any searches that were created in the init function.
        Returns a list of SObjects'''
        # if no search is defined in this class, then skip this
        # it does not inherit its parent's search until its parent
        # has obtained its search_objects
        if my.search != None:
            my.alter_search( my.search )
            my.sobjects = my.search.get_sobjects()


        # set the sobjects from this search
        if my.search != None:
            my.set_sobjects( my.sobjects, my.search )


    def init_cgi(my):
        web = WebContainer.get_web()
        search = Search(my.search_type)
        search_ids = web.get_form_value("search_ids")
        statement = web.get_form_value("statement")
        show_property = web.get_form_value("show_property")
        if show_property:
            if show_property == "True":
                my.show_property = True
            else:
                my.show_property = False

        if statement:
            sobjects = search.get_sobjects(statement=statement)
            my.set_sobjects( sobjects )


    def get_hide_column_wdg(my):
        return Widget()

        if not my.table_id:
            table_id = "table_%s" % my.widget_id
        else:
            table_id = my.table_id

        table = my.table
        table.set_id(table_id)
        div = DivWdg()

        popup = SpanWdg(css="popup")
        popup.add_style("display: none")
        popup.add_style("position: absolute")
        popup.set_id("popup_%s" % table_id)
        table = Table()
        for i, widget in enumerate(my.widgets):
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


    def add_table_refresher(my, div):
        web = WebContainer.get_web()

        ajax = AjaxLoader()
        if ajax.is_refresh() and my.is_top:
            # reuse the id
            my.widget_id = ajax.get_refresh_id()
        else:
            # generate a new one
            unique = my.generate_unique_id('table', is_random=True)
            my.widget_id = "%s|%s" % (unique, my.search_type)

        div.add_style("display: block")
        div.set_id(my.widget_id)
        ajax.set_display_id(my.widget_id)
        args = [my.search_type, my.config_base]

        # try to reproduce the sql statement the produced the current contents
        if my.search:
            # use the search, if available ... best source
            ajax.set_option("statement", my.search.get_statement() )
        elif my.sql_statement:
            ajax.set_option("statement", my.sql_statement )
        else:
            # if not, then refresh the whole page, because we can't reproduce
            # the sql statements
            my.refresh_mode = "page"


        ajax.set_option("show_property", my.show_property )
        ajax.set_load_class("pyasm.widget.TableWdg", args)
        if not (ajax.is_refresh() and my.is_top):
            event_container = WebContainer.get_event_container()
            # if refresh mode is "table", then this table updates on every data
            # update
            if my.refresh_mode == "table":
                event_name = event_container.DATA_INSERT
                event_container.add_listener(event_name, ajax.get_refresh_script(show_progress=False) )
            elif my.refresh_mode == "page":
                event_name = event_container.DATA_INSERT
                event_container.add_refresh_listener(event_name)
            else:
                event_name = "refresh|%s" % my.search_type_obj.get_base_key()
                event_container.add_listener(event_name, ajax.get_refresh_script(show_progress=False) )
       



    def get_display(my):

        web = WebContainer.get_web()
        table = my.table

        # create the main div
        div = DivWdg()

        # create the filter div
        filters = my.sections.get("filter")
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
                my.widgets.remove(filter)



        # make it so that the TableWdg is reloadble
        my.add_table_refresher(div)
        

        if my.content_width:
            table.set_attr('width', my.content_width)
        else:
            # set a separate width for IE, which can't draw tables properly
            table.set_max_width()



        # go through each widget and detect if they are hidden or not
        #hidden = web.get_form_values("hidden_table_rows")
        #widgets_to_remove = []
        #for widget in my.widgets:
        #    if widget.name in hidden:
        #        widgets_to_remove.append(widget)
        #for widget in widgets_to_remove:
        #    my.widgets.remove(widget)

        # add columns
        for widget in my.widgets:
            # set the table
            widget.set_parent_wdg(my)

            col = table.add_col()
            width = widget.get_option("width")
            if width:
                col.set_attr("width", width)

        # allow widgets preprocess to preprocess information for all of the
        # rows
        for widget in my.widgets:
            widget.preprocess()

        # get the prefs before the header but display afterwards
        pref_widgets = []

        for widget in my.widgets:
            pref_widgets.append( widget.get_prefs() )
           
 
        # add the headers
        app_css = ''
        if WebContainer.get_web().get_app_name() != 'Browser':
            app_css = 'smaller'
        app_css = '%s %s' %(app_css, my.header_css)

        # if the header is being shown
        if my.header_flag:
            tr = table.add_row(css=app_css)
            # this prevents button in this row shifting all the elements 
            # when clicked
            tr.add_style('height','2.8em')
            order_value = my.order_by_wdg.get_value(for_display=True)


            for widget in my.widgets:
                title = widget.get_title()
                th_css = ''
                if widget.name == order_value:
                    th_css = 'ordered'
                th = table.add_header(title, th_css)


            # add a row for UI controls
            #tr = table.add_row(css=app_css)
            #for widget in my.widgets:
            #    #controls = widget.get_control_wdg()
            #    controls = widget.get_title()
            #    controls = '&nbsp;'
            #    th = table.add_cell(controls, css=th_css)


        # add hidden prefs row        
        prefs_row_id = my.generate_unique_id('hidden_row_prefs')
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
        for i in range(0, len(my.sobjects)):
            # AuxDataWdg allows a NoneType in the array
            if my.sobjects[i] == None:
                continue

            my._add_prev_row(table, i)

            # add a tbody with an event container
            tbody = table.add_tbody()

            ajax = AjaxLoader()
            unique = my.generate_unique_id('tbody', is_random=True)
            search_key = my.sobjects[i].get_search_key()
            tbody_id = "%s|%s" % (unique,search_key)
            
            # used for some TableElementWdg
            my.row_ids[search_key] = tbody_id
            tbody.set_id(tbody_id)
            ajax.set_display_id(tbody_id)
            args = [my.search_type, my.config_base]
            ajax.set_load_class("pyasm.widget.layout_wdg.TbodyWdg", args)
            ajax.set_option("sthpw_edit", my.sobjects[i].get_search_key() )
            if not ajax.is_refresh():
                event_container = WebContainer.get_event_container()
                event_name = "refresh|%s" % my.sobjects[i].get_search_key()
                event_container.add_listener(event_name, ajax.get_refresh_script(show_progress=False) )
            #event_container = WebContainer.get_event_container()
            #event_name = "refresh|%s" % my.sobjects[i].get_search_key()
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
            #tr_id = "tr|%s" % my.sobjects[i].get_search_key()
            tr_id = "%s%s" % (my.ROW_PREFIX, my.sobjects[i].get_search_key())
            tr.set_id(tr_id)
            ajax = AjaxLoader()
            ajax.set_display_id(tr_id)
            args = [my.search_type, my.config_base]
            ajax.set_load_class("pyasm.widget.TrWdg", args)
            ajax.set_option("sthpw_edit", my.sobjects[i].get_search_key() )
            if not ajax.is_refresh():
                event_container = WebContainer.get_event_container()
                event_name = "refresh|%s" % my.sobjects[i].get_search_key()
                event_container.add_listener(event_name, ajax.get_refresh_script(show_progress=False) )
            ''' 

            tr.add_style("border-top: 0px")
            #tr.add_class("table")
            if my.sobjects[i].is_retired():
                 tr.add_class("retired_row")
            tr.add_style("display", "table-row")
            row_id = "%s%s" % (my.ROW_PREFIX, my.sobjects[i].get_search_key())
            tr.set_id(row_id)

            hidden_row_wdgs = []
            for widget in my.widgets:
                 
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
        if len(my.sobjects) == 0:
            num_cols = len(my.widgets)

            table.add_row()

            td = table.add_cell(my.no_results_wdg)
            td.set_style("text-align: center")
            td.set_attr("colspan", num_cols)

        else:
            table.add_row()
            for widget in my.widgets:
                bottom_html = widget.get_bottom()
                td = table.add_cell(bottom_html)
                # the hidden widget can be used to store data or support the widget
                div.add(widget.get_hidden())

        # add the property div only if show_property is True
        if my.show_property:
            property_div = DivWdg(css='right smaller')
            property_div.add(SpanWdg('count: %s' %len(my.sobjects), css='small'))

            # add a hidden widget for purposes of storing ordering information
            property_div.add(my.order_by_wdg)
            order_span = SpanWdg('order: ')
            if my.search:
                order_span.add_tip('%s' %','.join(my.search.get_order_bys()))
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
            property_div.add(my.get_hide_column_wdg())


            # add csv export
            filename = "%s_%s.csv" % (my.search_type.replace("/","_"), my.config_base)
            url = WebContainer.get_web().get_widget_url()
            url.set_option("dynamic_file", "true")
            url.set_option("widget", "pyasm.widget.CsvDownloadWdg")
            url.set_option("search_type", my.search_type)
            url.set_option("view", my.config_base)
            url.set_option("filename", filename)

            # remember all of the sobject keys
            # TODO: need to make this a post request so that we can store
            # any number of search_ids
            search_ids = [str(x.get_id()) for x in my.sobjects ]
            url.set_option("search_ids", "|".join(search_ids) )

            export.add_event("onclick", "document.location='%s'" % url.to_string() )


            # TEST Pic lens plugin
            #export = IconButtonWdg("Start PicLens Player", IconWdg.PICLENS, False)
            #property_div.add(export)
            url = WebContainer.get_web().get_widget_url()
            url.set_option("dynamic_file", "true")
            url.set_option("widget", "pyasm.widget.PicLensRssWdg")
            url.set_option("search_type", my.search_type)
            # remember all of the sobject keys
            # TODO: need to make this a post request so that we can store
            # any number of search_ids
            search_ids = [str(x.get_id()) for x in my.sobjects ]
            url.set_option("search_ids", "|".join(search_ids) )

            #export.add_event("onclick", "PicLensLite.start()")

            # FIXME: it appears that the link tag makes an http so the
            # display image library is called for every refresh.
            property_div.add('''
            <script type="text/javascript" src="/context/javascript/piclens.js"></script>
            <link rel="alternate" href="%s" type="application/rss+xml" title="" id="gallery" />
            ''' % url.to_string())






            div.add(property_div)
            if my.search: 
                property_div.add(my.retired_filter)
                property_div.add(my.search_limit_filter)


        div.add(table)
        my.add_table_inputs(div)

        if my.search:
            bottom_div = DivWdg()
            bottom_div.set_style("text-align: right")
            bottom_div.add(my.search_limit_filter_bottom)
            div.add(bottom_div)

        # set content height
        if my.content_height:
            div.add_style("height: %spx" % my.content_height)
            div.add_style("overflow: auto")
        return div

    def add_table_inputs(my, widget):      
        ''' add some inputs used by DynamicTableElementWdg'''
        hidden = HiddenWdg('skey_DynamicTableElementWdg')
        widget.add(hidden)
        hidden = HiddenWdg('attr_DynamicTableElementWdg')
        widget.add(hidden)
        hidden = HiddenWdg('update_DynamicTableElementWdg')
        widget.add(hidden)

    def _add_prev_row(my, table, idx):
        prev_sobj = None
        if idx > 0:
            prev_sobj = my.sobjects[idx-1]
           
        for widget in my.widgets:
            # set the index here instead
            widget.set_current_index(idx)
            widget.add_prev_row(table, prev_sobj)   


class TableElementHideCmd(Command):

    def set_search_type(my, search_type):
        my.search_type = search_type

    def execute(my):
        web = WebContainer.get_web()
        invisible = web.get_form_value("invisible")
        if not invisible:
            return

        ProdSetting.add_value_by_key("invisible_elements", invisible, my.search_type)

        title = SearchType.get(my.search_type).get_title()

        my.description = "Hid column %s for %s" % (invisible, title)


      

class TbodyWdg(TableWdg, AjaxWdg):
    '''A widget that represents a section of a TableWdg used to replace a tbody in a table'''
   
    def __init__(my, search_type, config_base="tbody", css=None, header_css=None):
        if not config_base:
            config_base = "table"
        my.search_ids = None 

        TableWdg.__init__(my, search_type, config_base)
        AjaxWdg.__init__(my)

    def init_cgi(my):
        edit_ids = my.web.get_form_values('sthpw_edit')

        # these may contain search_keys
        my.search_ids = []
        for edit_id in edit_ids:
            if edit_id.count("|") == 1:
                search_type, edit_id = edit_id.split("|",1)
            my.search_ids.append(edit_id)
            
    def get_display(my):
        if not my.search_ids or my.search_ids == ['']:
            return ''

        tbody = Tbody()
    
        for widget in my.widgets:
            # set the parent wdg
            widget.set_parent_wdg(my)

        if not my.sobjects:
            my.sobjects = Search.get_by_id(my.search_type, my.search_ids)
        
        for widget in my.widgets:
            widget.set_sobjects(my.sobjects)

        # allow widgets preprocess to preprocess information for all of the
        # rows
        for widget in my.widgets:
            widget.preprocess()
 
        # add the rows for each sobject
        for i in range(0, len(my.sobjects)):
            # AuxDataWdg allows a NoneType in the array
            if my.sobjects[i] == None:
                continue
            #my._add_prev_row(tbody, i)
            
            tr = tbody.add_row()
            tr.add_style("border-top: 0px")
            tr.add_style("display", "table-row")
            
            tr.set_id("%s%s" % (my.ROW_PREFIX, my.sobjects[i].get_search_key()) )

            hidden_row_wdgs = []
            for widget in my.widgets:
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
        if len(my.sobjects) == 0:
            num_cols = len(my.widgets)

            tbody.add_row()

            td = tbody.add_cell("Search produced no results")
            td.set_style("text-align: center")
            td.set_attr("colspan", num_cols)

       
        return tbody



class TrWdg(TbodyWdg):
    '''A widget that represents a row of a TableWdg used to replace a tr in a table'''
    def get_display(my):
        if not my.search_ids or my.search_ids == ['']:
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
            

            if my.sobjects:
                tr.set_id("%s%s" % (my.ROW_PREFIX, my.sobjects[i].get_search_key()) )
        for widget in my.widgets:
            # set the parent wdg
            widget.set_parent_wdg(my)

        if not my.sobjects:
            my.sobjects = Search.get_by_id(my.search_type, my.search_ids)
        
        for widget in my.widgets:
            widget.set_sobjects(my.sobjects)

        # allow widgets preprocess to preprocess information for all of the
        # rows
        for widget in my.widgets:
            widget.preprocess()
 

        
     
       
        
        hidden_row_wdgs = []
        for widget in my.widgets:
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
        if len(my.sobjects) == 0:
            num_cols = len(my.widgets)

            td = HtmlElement.td()
            td.add("Search produced no results")
            td.set_style("text-align: center")
            td.set_attr("colspan", num_cols)
      
        return tr





class LayoutWdg(DivWdg):
    def __init__(my, search_type):
        super(LayoutWdg,my).__init__()
        my.layout_cells = {}


    def get_display(my):

        table = Table()

        my.set_layout(table)

        for cell_name, cell in my.layout_cells.items():
            my.set_content(cell_name, cell)

        my.add(table)

        return super(LayoutWdg,my).get_display()

    
    def set_cell( my, td, title ):
        my.layout_cells[title] = td

            
    def set_layout(my, table):
        table.add_row()
        td = table.add_cell()
        my.set_cell(td, 'header')

        table.add_row()
        td = table.add_cell()
        td.add_style("width: 150px")
        td.set_attr("valign", "top")
        my.set_cell(td, 'left')

        td = table.add_cell()
        td.add_style("padding", "5px")
        my.set_cell(td, 'right')



    def set_content(my,cell_name,cell):
        function = "get_cell_%s" % cell_name
        try:
            # test existance of functions
            wdg = eval( "my.%s" % function )
        except AttributeError:
            wdg = function
        else:
            wdg = eval( "my.%s()" % function )

        cell.add( wdg )







class SObjectLayoutWdg(BaseConfigWdg):
    def __init__(my, search_type):
        super(SObjectLayoutWdg,my).__init__(search_type,"layout")

        my.layout_cells = {}


    def get_default_display_handler(cls, element_name):
        return "SimpleTableElementWdg"
    get_default_display_handler = classmethod(get_default_display_handler)


    def get_display(my):

        div = HtmlElement.div()

        index = 0
        for sobject in my.sobjects:

            table = Table()
            table.add_style("border-style: solid")
            table.add_style("border-width: 1px")
            table.add_style("margin-bottom: 15px")

            my.set_layout(table)

            for cell_name, cell in my.layout_cells.items():
                my.set_content(sobject, cell_name, cell)

            div.add(table)

            index += 1

        my.add(div)

        return super(SObjectLayoutWdg,my).get_display()


            
    def set_layout(my, table):
        table.add_row()
        td = table.add_cell()
        td.set_attr("colspan", "2")
        td.add_style("background-color", "#f0f0f0")
        my.layout_cells['title'] = td

        table.add_row()
        td = table.add_cell()
        my.layout_cells['icon'] = td

        td = table.add_cell()
        td.set_attr("valign", "top")
        td.add_style("width", "400px")
        my.layout_cells['discussion'] = td



    def set_content(my,sobject,cell_name,cell):
        function = "get_cell_%s" % cell_name
        try:
            # test existance of functions
            wdg = eval( "my.%s" % function )
        except AttributeError:
            wdg = function
        else:
            wdg = eval( "my.%s(sobject)" % function )

        cell.add( wdg )





class EditWdg(BaseConfigWdg):

    CLOSE_WDG = "close_wdg"

    def __init__(my, search_type,base_config="edit", input_prefix='edit',config=None, default_action_handler=None):
        my.current_id = -1
        if not default_action_handler:
            my.default_action_handler = "pyasm.command.EditCmd"
        else:   
            my.default_action_handler = default_action_handler

        super(EditWdg,my).__init__(search_type,base_config, input_prefix=input_prefix,config=config)

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


    def set_default_action_handler(my, handler):
        my.default_action_handler = handler


    def get_default_action_handler(my):
        web = WebContainer.get_web()
        action = web.get_form_value("action")
        if action:
            return action
        else:
            return my.default_action_handler


    def init(my):
        super(EditWdg,my).init()
        web = WebContainer.get_web()

        # if we have edit/close and it's error-free, then do nothing
        #if my.is_error_free(web):
        #    return

        id = web.get_form_value("search_id")
        if id == "" or id == "-1":
            my.mode = "insert"
        else:
            my.mode = "edit"

        # this can be set to True to force a full page refresh instead of an
        # event refresh
        my.refresh_mode = web.get_form_value("refresh_mode")

       
        # get the edit command
        edit_action_handler = my.get_default_action_handler()
        WebContainer.register_cmd(edit_action_handler)

        # for Edit/Next ... remember last sobject edited
        my.last_sobject = None




    def do_search(my):
        '''this widget has its own search mechanism'''

        web = WebContainer.get_web()
        
        # get the sobject that is to be edited
        id = web.get_form_value("search_id")

        # if no id is given, then create a new one for insert
        search = None
        sobject = None
        search_type_base = SearchType.get(my.search_type).get_base_key()
        if my.mode == "insert":
            sobject = SObjectFactory.create(my.search_type)
            my.current_id = -1
            # prefilling default values if available
            url_dict = web.get_form_value("url_dict")
            if url_dict:
                url_list = url_dict.split('||')
                for x in url_list:
                    key, value = x.split(':', 1)
                    sobject.set_value(key, value)
        else:
            search = Search(my.search_type)

            # figure out which id to search for
            if web.get_form_value("do_edit") == "Edit/Next":
                search_ids = web.get_form_value("%s_search_ids" %search_type_base)
                if search_ids == "":
                    my.current_id = id
                else:
                    search_ids = search_ids.split("|")
                    next = search_ids.index(str(id)) + 1
                    if next == len(search_ids):
                        next = 0
                    my.current_id = search_ids[next]

                    last_search = Search(my.search_type)
                    last_search.add_id_filter( id )
                    my.last_sobject = last_search.get_sobject()

            else:
                my.current_id = id

            search.add_id_filter( my.current_id )
            sobject = search.get_sobject()

        if not sobject:
            raise EditException("No SObject found")

        # set all of the widgets to contain this sobject
        my.set_sobjects( [sobject], search )
       

    def is_error_free(my, web):
        ''' if it is instructed to close and is error-free , return True'''
        if web.get_form_value(my.CLOSE_WDG) and\
            not Container.get("cmd_report").get_errors():
            return True

        return False

    def add_header(my, table, title):
        th = table.add_header( my.mode.capitalize() + " - " + title )
        th.set_attr("colspan", "2")
        
    def add_hidden_inputs(my, div):
        pass

    def get_display(my):

        web = WebContainer.get_web()
        event_container = WebContainer.get_event_container()

        layout = web.get_form_value("layout")
        if not layout:
            layout = "default"
       
        div = HtmlElement.div()

        # remember the action
        edit_action_handler = my.get_default_action_handler()
        div.add( HiddenWdg("action",edit_action_handler) )

        my.iframe = WebContainer.get_iframe(layout)
        if web.get_form_value("do_edit") == "Edit/Next" and my.last_sobject:
            search_key = my.last_sobject.get_search_key()
            refresh_script = "window.parent.%s" % event_container.get_event_caller("refresh|%s" % search_key )
            div.add(HtmlElement.script(refresh_script))


        elif my.is_error_free(web):
            
            # multi-edit always refreshes table
            selected_keys = web.get_form_value(EditCheckboxWdg.CB_NAME)
            if my.refresh_mode == "page" or web.is_IE():
                refresh_script = "window.parent.%s" % event_container.get_refresh_caller()
            elif selected_keys or my.mode == "insert":
                refresh_script = "window.parent.%s" % event_container.get_event_caller("refresh|%s" % my.search_type )
                refresh_script = "%s;window.parent.%s" % (refresh_script, event_container.get_data_insert_caller())
            elif my.mode == "edit":
                search_key = my.sobjects[0].get_search_key()
                refresh_script = "window.parent.%s" % event_container.get_event_caller("refresh|%s" % search_key )
                #print(refresh_script)
            else:
                refresh_script = "window.parent.%s" % event_container.get_refresh_caller()

            undo_script = "window.parent.%s" % event_container.get_event_caller("SiteMenuWdg_refresh")

            off_script = "window.parent.%s" % my.iframe.get_off_script()

            script = HtmlElement.script('''
            %s
            %s
            %s
            ''' % (off_script, refresh_script, undo_script )  )
            return script
        

        search_type_obj = SearchType.get(my.search_type)
        title = search_type_obj.get_title()

        div.add( HiddenWdg("search_type",my.search_type) )
        div.add( HiddenWdg("search_id",my.current_id).get_display() )
        div.add( HiddenWdg(my.CLOSE_WDG) )
        my.add_hidden_inputs(div)        

        table = Table(css='edit')
        table.center()
        
        table.add_row()
        my.add_header(table, title)
        
        security = Environment.get_security()

        # go through each widget and draw it
        for widget in my.widgets:
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
            if my.mode == "edit" and edit_all == 'true':
                table.add_cell( EditAllWdg(widget), css="right_content" )
            elif my.mode == "insert" and insert_multi == 'true':
                table.add_cell( InsertMultiWdg(widget), css="right_content" )
            else:
                table.add_blank_cell()

        table.add_row_cell( my.get_action_html() )

        div.add( table )
        # add the warning menu for the iframe
        div.add( WarningMenuWdg())
        help_menu = HelpMenuWdg()

        div.add(help_menu.get_panel())
        return div



    def get_action_html(my):
        
        edit = SubmitWdg("do_edit", "%s/Next" % my.mode.capitalize() )
        edit_continue = SubmitWdg("do_edit", "%s/Close" % my.mode.capitalize() )
        
        edit_continue.add_event("onclick", "document.form.%s.value='true'" %my.CLOSE_WDG)
        
        # call an edit event
        event = WebContainer.get_event("sthpw:submit")
        edit.add_event( "onclick", event.get_caller() )
        #edit_continue.add_event( "onclick", event.get_caller() )

        # create a cancel button to close the window
        cancel = ButtonWdg(_("Cancel"))
        iframe_close_script = "window.parent.%s" % my.iframe.get_off_script() 
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
    def get_action_html(my):
        
        edit = SubmitWdg("do_edit", "%s/Next" % my.mode.capitalize() )
        edit_continue = SubmitWdg("do_edit", "%s/Close" % my.mode.capitalize() )
        
        edit_continue.add_event("onclick", "document.form.%s.value='true'" %my.CLOSE_WDG)
        
        # call an edit event
        event = WebContainer.get_event("sthpw:submit")
        edit.add_event( "onclick", event.get_caller() )
        #edit_continue.add_event( "onclick", event.get_caller() )

        # create a cancel button to close the window
        cancel = ButtonWdg(_("Cancel"))
        iframe_close_script = "window.parent.%s" % my.iframe.get_off_script() 
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
    def __init__(my, search_type, base_config="edit", input_prefix='edit',config=None, commit=False):
        super(PublishWdg, my).__init__(search_type, base_config, input_prefix=input_prefix,config=config)
        my.commit_flag = commit

    

class IconLayoutWdg(BaseConfigWdg):

    def __init__(my, search_type):
        super(IconLayoutWdg,my).__init__(search_type,"asset")
        my.category_col = None
        my.shot_edit_flag = True

    def set_category(my, category):
        my.category_col = category

    def set_show_edit(my, show_edit_flag):
        my.show_edit_flag = show_edit_flag


    def alter_search(my, search):
        if my.category_col != None:
            search.add_order_by(my.category_col)


    def get_display(my):

        # preprocess through all of the sobjects to find the categories
        # to be displayed
        #categories = []
        #for sobject in my.sobjects:
        #    category = sobject.get_value( my.category_col )
        #    if category not in categories:
        #        categories.append(category)

        num_cols = 4
        num_sobjects = len(my.sobjects)

        web = WebContainer.get_web()

        table = Table()
        table.set_attr("cellspacing", "0")

        # set a separate width for IE, which can't draw tables properly
        if web.is_IE():
            table.add_style("width", "100%")
        else:
            table.add_style("width", "95%")


        my.last_category = None
        col_count = 0
        for i in range(0, num_sobjects):

            sobject = my.sobjects[i]

            # handle category
            if my.category_col != None:
                category = sobject.get_value( my.category_col )

                if my.last_category == None or category != my.last_category:
                    # fill in the rest
                    if my.last_category != None:
                        for i in range(col_count, num_cols):
                            td = table.add_cell("&nbsp;")

                    my.add_category(table, category )
                    table.add_row()

                    col_count = 0
                    my.last_category = category

                elif col_count == num_cols:
                    table.add_row()
                    col_count = 0
            else:
                if col_count == num_cols:
                    table.add_row()
                    col_count = 0


            td = table.add_cell()
            td.add( my.get_sobject_wdg(sobject) )

            col_count += 1

        return table.get_display()




    def get_sobject_wdg(my, sobject):

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

        if my.show_edit_flag:
            update = UpdateWdg("update")
            update.set_sobject(sobject)
            td.add(update)

        return table



    def add_category(my, table, category):

        if category == "":
            category = "No category"

        table.add_row()

        div = HtmlElement.div()
        div.add_style("font-weight", "bold")
        div.add_style("font-size", "1.2em")
        div.add_style("padding-left", "3px")
        div.add_style("padding-bottom", "3px")


        if my.show_edit_flag:
            insert = InsertLinkWdg(my.search_type)
            insert.add_style("float", "right")
            div.add(insert)

        div.add(category)

        cell = table.add_cell(div)

        cell.set_attr("colspan", 4)
        table.add_row()


class EditAllWdg(Widget):

    ELEMENT_NAME = "edit_all_element"
    EDIT_ALL = "edit_all"
        
    def __init__(my, widget):
        my.edit_element = widget
        super(EditAllWdg, my).__init__()
        
    def class_init(my):
        my.add(HiddenWdg(my.ELEMENT_NAME))
        my.add(HiddenWdg(my.EDIT_ALL))
        WebContainer.register_cmd('pyasm.command.EditAllCmd')
        
    def init(my):
       
        icon = IconSubmitWdg(my.EDIT_ALL, icon=IconWdg.EDIT_ALL, add_hidden=False)
        icon.add_event("onclick", "document.form.elements['%s'].value='%s';"\
            % (my.ELEMENT_NAME, my.edit_element.name))
        icon.add_event("onclick", "document.form.%s.value='true'" %EditWdg.CLOSE_WDG)
        icon.add_class('hand')

        my.add(icon)

class InsertMultiWdg(Widget):

    ELEMENT_NAME = "insert_multi_element"
    INSERT_MULTI = "insert_multi"
        
    def __init__(my, widget):
        my.edit_element = widget
        super(InsertMultiWdg, my).__init__()
        
    def class_init(my):
        my.add(HiddenWdg(my.ELEMENT_NAME))
        my.add(HiddenWdg(my.INSERT_MULTI))
        WebContainer.register_cmd('pyasm.command.InsertMultiCmd')
        
    def init(my):
        icon = IconSubmitWdg(my.INSERT_MULTI, icon=IconWdg.INSERT_MULTI, add_hidden=False)
        icon.add_event("onclick", "document.form.elements['%s'].value='%s';"\
            % (my.ELEMENT_NAME, my.edit_element.name))
        icon.add_event("onclick", "document.form.%s.value='true'" %EditWdg.CLOSE_WDG)
        icon.add_class('hand')

        my.add(icon)
