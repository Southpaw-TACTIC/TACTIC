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
'BaseTableElementWdg',
'PlaceHolderElementWdg',
'FunctionalTableElement',
'SimpleTableElementWdg',
'DynamicTableElementCmd',
'DynamicTableElementWdg',
'WrapperTableElementWdg',
'ArrayTableElementWdg',
'CheckTableElementWdg',
'DateWdg',
'DateYearTimeWdg',
'DateTimeWdg',
'UpdateWdg',
'SubmissionLinkTableElement',
'RenderLinkTableElement',
'FileAppendLinkTableElement',
'SimpleInfoWdg',
'XmlWdg',
'NameWdg',
'HiddenRowToggleWdg',
'GroupTableElement',
'SObjectAttachTableElement',
'TableAddWdg',
'CheckboxColWdg',
'EditCheckboxWdg',
'ExpandableTextWdg',
'AuxDataWdg',
'WikiElementWdg',
'SearchTypeElementWdg',
'PublishTableElement',
'SObjectLinkElementWdg',
'SObjectExplorerWdg',
]

import re, time, types
from dateutil import parser
from datetime import datetime

from pyasm.common import Container, Xml, XmlException, SecurityException, Environment, Date, UserException, Common, SPTDate, jsondumps, jsonloads
from pyasm.biz import Snapshot
from pyasm.command import Command
from pyasm.search import SearchType, Search, SObject, SearchException, SearchKey
from pyasm.web import *

from .input_wdg import CheckboxWdg, HiddenWdg, TextWdg, PopupMenuWdg
from .web_wdg import *
from .icon_wdg import IconWdg, IconButtonWdg
from .input_wdg import FilterTextWdg

import six
basestring = six.string_types

 
class BaseTableElementWdg(HtmlElement):
    def __init__(self, name=None, value=None, **kwargs):

        self.kwargs = kwargs
        self.options = {} 
        for key, kw_value in kwargs.items():
            self.set_option(key, kw_value)
            
        super(BaseTableElementWdg,self).__init__("div")
        self.name = name
        self.value = value
        self.web = WebContainer.get_web()
        self.is_preprocessed = False

        # NOTE: this should really be put in with  list of attrs
        self.width = 0
        self.view_attributes = {}
        self.attributes = {}

        self.state = {}

        self.generator_element = None

        # NOTE: not sure what the different between these two are
        self.parent_wdg = None
        self.layout_wdg = None

        self.filter_data = {}


    def handle_layout_behaviors(self, layout):
        '''This is the place where a top layout widget is added, allowing
        for global level behaviors to be added'''
        pass



    def preprocess(self):
        '''This gets called once for each column.  It allows widgets to
        get data from the database and preprocess it for all of the rows
        simultaneously, which is often much faster than doing it row by row
        '''
        pass


    def set_filter_data(self, filter_data):
        self.filter_data = filter_data

    def get_filter_data(self):
        return self.filter_data

    def get_args_keys(cls):
        return {}
    get_args_keys = classmethod(get_args_keys)


    def can_async_load(cls):
        return True
    can_async_load = classmethod(can_async_load)


    def get_width(self):
        return self.width


    # This should be a widget that is very high up in the hierarchy
    # where global behaviors can be put in
    def set_layout_wdg(self, widget):
        self.layout_wdg = widget

    def get_layout_wdg(self):
        return self.layout_wdg


    def set_state(self, state):
        '''Set the state for this table element'''
        self.state = state

    def get_state(self):
        '''get the state for this table element'''
        return self.state


    def is_editable(cls):
        '''Determines whether this element is editable'''
        return False
    is_editable = classmethod(is_editable)


    def is_searchable(self):
        '''Determines whether this element is searchable'''
        return False

    def get_required_columns(self):
        '''Determines the required columns for this widget to work'''
        return []


    def get_generator(self):
        '''returns whether this widget is generated'''
        return self.generator_element

    def set_generator(self, element_name):
        '''sets whether this widget is generated'''
        self.generator_element = element_name




    def is_simple_viewable(self):
        return True

    def is_in_column(self):
        '''determines whether this element is actually displayed in the
        table column.  This is useful for widgets that are used for
        categories and do not occupy a column in the table'''
        return True



    def get_title(self):
        '''Returns a widget containing the title to be displayed for this
        column'''
        if self.title:
            title = self.title
            title = title.replace(r'\n','<br/>')

            if self.title.find("->") != -1:
                parts = self.title.split("->")
                title = parts[-1]

        else:
            title = self.name

            if self.name.find("->") != -1:
                parts = self.name.split("->")
                title = parts[-1]


            if not title:
                title = ""

            else:
                title = Common.get_display_title(title)

        title = _(title)

        from pyasm.web import DivWdg
        div = DivWdg()
        div.add_attr("title", title)
        div.add_style("margin-top", "6px")
        div.add(title)

        return div





    def get_header_option_wdg(self):
        return None

    def get_control_wdg(self):
        return Widget()

   
    def get_hidden(self):
        '''Returns a widget containing hidden elements or data to support this wBaseTableElementWdg'''
        return ''

   
    def get_edit_wdg(self): 
        '''widget that defines if this should be ordered''' 
   
        sobject = self.get_current_sobject() 
        value = sobject.get_value(self.name) 
   
        popup = PopupMenuWdg("edit_%s_%s" % (sobject.get_id(), value ) ) 
        from .input_wdg import TextAreaWdg 
        div = TextAreaWdg() 
        popup.add( div ) 
             
        return popup 


    def get_text_value(self):
        '''this should be called for CSV export to minimize ambiguity'''
        widget = self.get_simple_display()
        if isinstance(widget, Widget):
            value = widget.get_text_value()
        else:
            value = widget
        return value



    # functions that for a standard way for an widget to deliver data
    def get_data(self, sobject):
        name = self.name
        return sobject.get_value(name, no_exception=True)


    def get_onload_js(self):
        return




    def get_simple_display(self):
        '''provide a simple display of this table element'''
        sobject = self.get_current_sobject()
        widget = SimpleTableElementWdg()
        widget.set_sobject(sobject)
        widget.set_name(self.name)
        return widget


    
    def get_prefs(self):
        '''Returns a widget for the hidden prefs bar in the table widget'''
        return None
    

    def get_bottom(self):
        '''Returns the widget placed in the bottom row of the table'''
        return None

    def get_bottom_wdg(self):
        '''Returns the widget placed in the bottom row of the table'''
        return None

    def get_group_bottom_wdg(self, group_sobjects):
        '''Returns the bottom widget placed in the bottom row of the group'''
        return None



    def set_name(self, name):
        self.name = name

    

    def set_parent_wdg(self, parent_wdg):
        '''Sets which table widget this widget belongs to'''
        self.parent_wdg = parent_wdg

    def get_parent_wdg(self):
        '''gets which table widget this widget belongs to'''
        return self.parent_wdg


    def get_parent_view(self):
        '''gets which table widget this widget belongs to'''
        if self.parent_wdg:
            return self.parent_wdg.get_view()
        else:
            return ''

    def get_name(self):
        return self.name

    #def get_style(self):
    #    return "text-align: left"

    def set_value(self, value):
        '''explicitly set the value outside of the sobject'''
        self.value = value


    def get_value(self, name=None):
        '''convenience function for getting the value of the current sobject'''

        if self.value:
            return self.value
        
        sobject = self.get_current_sobject()
        if not sobject:
            return ''
        
        if not name:
            name = self.name
        value = sobject.get_value(name, no_exception=True)
        return value
    
        '''
        attr = sobject.get_attr(self.name)
        if attr:
            return attr.get_value()
        else:
            return ""
        '''

    def get_timezone_value(self, value):
        '''given a datetime value, try to convert to timezone specified in the widget.
           If not specified, use the My Preferences time zone'''
        timezone = self.get_option('timezone')
        if not timezone:
            from pyasm.biz import PrefSetting
            timezone = PrefSetting.get_value_by_key('timezone')
        
        if timezone in ["local", '']:
            value = SPTDate.convert_to_local(value)
        else:
            value = SPTDate.convert_to_timezone(value, timezone)
        
        return value

    def set_option(self, key, value):
        self.options[key] = value

    def set_options(self, dict):
        for key, value in dict.items():
            self.set_option(key, value)


    def get_option(self, key):
        '''gets the value of the specified option'''
        value = self.options.get(key)
        if value == None: # allow 0
            return ""
        else:
            return value

    def get_current_aux_data(self):
        if self.parent_wdg.aux_data:
            idx = self.get_current_index()
            if len(self.parent_wdg.aux_data) <= idx:
                return None
            return self.parent_wdg.aux_data[idx]
        else:
            return None
    
    def insert_aux_data(self, idx, new_dict):
        ''' insert a dict to the aux data of the TableWdg '''
        if self.parent_wdg.aux_data and len(self.parent_wdg.aux_data) > idx :
            item = self.parent_wdg.aux_data[idx]
            for new_key, new_value in new_dict.items():
                item[new_key] = new_value
        else:
            self.parent_wdg.aux_data.insert(idx, new_dict)


    def set_attributes(self, attrs):
        '''set attributes dict like access, width, or edit'''
        self.attributes = attrs

    def handle_tr(self, tr):
        pass

    def handle_th(self, th, cell_index=None):
        pass

    def handle_td(self, td):
        pass

    def add_prev_row(self, table, prev_sobj):
        pass

    #def get_prev_row_wdg(self, table, prev_sobj):
    #    return None


    def is_searchable(self):
        return False

    def get_searchable_search_type(self):
        '''get the searchable search type for local search'''
        return ''
    #
    # Grouping methods
    #
    def get_sort_prefix(self):
        return None
    def is_sortable(self):
        return True
    def is_groupable(self):
        return False
    def is_time_groupable(self):
        return False

    def get_group_wdg(self, prev_sobj):
        return None
    def is_new_group(self, prev_sobj, sobject):
        return None
    def handle_group_table(self, table, tbody, tr, td):
        return

    def get_config_base(self):
        '''get the config base of the parent wdg'''
        if self.parent_wdg:
            return self.parent_wdg.get_config_base()
        else:
            return ''

    def get_search_type(self):
        '''get the search_type of the parent wdg'''
        if self.parent_wdg:
            return self.parent_wdg.search_type
        else:
            return ''


    def alter_order_by(self, search, direction=''):
        '''handle order by??'''
        order_by = self.get_option("order_by")

        if order_by:
            search.add_order_by(order_by, direction)
        else:
            search.add_order_by(self.get_name(), direction)

        # some order by's require a specific where clause in order to filter
        # down a join sufficiently.
        order_by_where = self.get_option("order_by_where")
        if order_by_where:
            search.add_where(order_by_where)

    def process_sobjects(self, sobjects, search=None):
        '''a chance to do advanced ordering/grouping of sobjects post search'''
        return sobjects



class PlaceHolderElementWdg(BaseTableElementWdg):
    '''empty table element wdg'''
    def get_display(self):
        return ""




class SimpleTableElementWdg(BaseTableElementWdg):
    '''This is the default table element widget.  It simply takes the value
    of the sobject draws it as a string'''

    def is_editable(self):
        '''Determines whether this element is editable'''
        return True

    def is_groupable(self):
        return True

    def get_text_value(self):
        value = self.get_value()
        return value
       

    def get_simple_display(self):
        value = self.get_value()
        if self.name == "timestamp":
            value = Date(value).get_display_time()
        else:
            value = str(value)

        return value

    def get_display(self):
        value = self.get_value()
        if isinstance(value, basestring):
            wiki = WikiUtil()
            value = wiki.convert(value) 
        if self.name == "timestamp":
            value = Date(value).get_display_time()
        else:
            if not isinstance(value, basestring):
                value_wdg = DivWdg()
                value_wdg.add_style("float: right")
                value_wdg.add_style("padding-right: 3px")
                value_wdg.add(str(value))
                return value_wdg
        return value




class FunctionalTableElement(BaseTableElementWdg):

    def __init__(self, name=None, value=None, **kwargs):
        super(FunctionalTableElement, self).__init__(name, value, **kwargs)
        self.functional = True

class DynamicTableElementCmd(Command):
    ''' commit a new value to a sobject's attribute'''

    def get_title(self):
        return 'DynamicTableElementCmd'

    def check(self):
        web = WebContainer.get_web()
        search_key = web.get_form_value('skey_DynamicTableElementWdg')
        self.attr = web.get_form_value('attr_DynamicTableElementWdg')
        self.update = web.get_form_value('update_DynamicTableElementWdg')
        if search_key:
            self.sobject = Search.get_by_search_key(search_key)

        if not self.sobject or not self.attr or self.update != 'update':
            return False

        elem_name = '%s_%s_%s' %(DynamicTableElementWdg.ELEM_PREFIX, search_key, self.attr)
        self.new_value = web.get_form_value(elem_name)
        return True

    def get_title(self):
        return "DynamicTableElementCmd"

    def execute(self):
        #TODO: this does not handle multi attr field like CustomInfoWdg
        if not self.sobject.has_value(self.attr):
            raise UserException("[%s] does not have attribute [%s]. This may be a multi-attribute\
                property." %(self.sobject.get_code(), self.attr))
        
        self.sobject.set_value(self.attr, self.new_value)
        self.sobject.commit()
        self.add_description(self.sobject.get_update_description())

class DynamicTableElementWdg(BaseTableElementWdg, AjaxWdg):
    '''This is the dynamic table element widget. 
        It allows inline editing where applicable'''

    ELEM_PREFIX = "simple_elem"
    def __init__(self,name=None, value=None ):
        self.sobject = None
        self.search_key = ''
        self.attr = ''
        self.update = ''
        self.element_name = name
        self.view = ''
        self.config = None
        self.element = None
        super(DynamicTableElementWdg, self).__init__()
       
    def set_name(self, name):
        self.name = name
        self.element_name = name

    def init_setup(self):
        self.reset_ajax()
        # these inputs are added in TableWdg 
        hidden = HiddenWdg('skey_DynamicTableElementWdg')
        self.add_ajax_input(hidden)
        hidden = HiddenWdg('attr_DynamicTableElementWdg')
        # add the search_key input
        self.add_ajax_input(hidden)
        hidden = HiddenWdg('update_DynamicTableElementWdg')
        self.add_ajax_input(hidden)

        self.set_ajax_option("element_name", self.element_name)
        #view = 'edit'
        if not self.is_from_ajax(check_name=True):
            self.view = self.parent_wdg.get_view()
        self.set_ajax_option("view", self.view)


    
    def init_cgi(self):
        # get the sobject
        self.search_key = self.web.get_form_value('skey_DynamicTableElementWdg')
        self.attr = self.web.get_form_value('attr_DynamicTableElementWdg')
        if self.search_key:
            self.sobject = Search.get_by_search_key(self.search_key)
            self.set_sobject(self.sobject)
        self.update = self.web.get_form_value('update_DynamicTableElementWdg')
        self.element_name = self.web.get_form_value("element_name")
        self.view = self.web.get_form_value("view")

    def preprocess(self):
        if not self.sobjects:
            return
        # this indirectly says whether this is ajax or not
        if not self.view:
            self.view = self.parent_wdg.get_view()
        sobject = self.sobjects[0]
        from .widget_config import WidgetConfig, WidgetConfigView
        if sobject:
            self.config = WidgetConfigView.get_by_search_type(\
                sobject.get_search_type_obj().get_base_key(), self.view)

        else:
            return

        # check self.config
        display_handler = self.config.get_display_handler(self.element_name)

        if display_handler:
            self.element = WidgetConfig.create_widget(display_handler)
            self.element.set_name(self.element_name)
            display_options = self.config.get_display_options(self.element_name)
            for key in display_options.keys():
                self.element.set_option(key, display_options.get(key))
            # preprocess first
            self.element.set_sobjects(self.sobjects)
            self.element.set_parent_wdg(self.parent_wdg)
            self.element.preprocess()

            #div.add(element.get_simple_display())
        #else:
            #div.add(value) 
        self.is_preprocessed = True

    def get_display(self):
        if not self.is_preprocessed:
            self.preprocess()
        
        value = ''
        #widget = DivWdg()
        widget = Widget()

        #self.sobject = self.get_current_sobject()
        #self.attr = self.get_name()

        #print(self.name)
        #print("is_ajax: ", self.is_ajax())
        #print("is_from_ajax: ", self.is_from_ajax())
        #print("-"*20)
        if not self.is_ajax() or not self.is_from_ajax():
            self.sobject = self.get_current_sobject()
            self.attr = self.get_name()

        if not self.sobject:
            return 'Invalid search key [%s]' %self.search_key
        display_id = "%s_%s_%s"%( self.ELEM_PREFIX,\
                 self.sobject.get_search_key(), self.attr)

        # this order is important: 1. reset ajax 2. set_ajax_top_id
        self.init_setup()
        self.set_ajax_top_id(display_id)
        is_ajax = False
        if self.is_from_ajax(check_name=True):
            is_ajax = True
            value = self.sobject.get_value(self.attr, no_exception=True)
            value = str(value)
            self.set_value(value)
            if self.update == 'swap':
                div = self.get_edit_wdg(display_id, value) 
                widget.add(div)
            else:
                widget = self.get_normal_display(widget, display_id, is_ajax) 
        else:
            widget = self.get_normal_display(widget, display_id, is_ajax) 

        return widget


    def get_normal_display(self, widget, display_id, is_ajax):
        '''draw it normally'''
        self.name = self.element_name
        value = self.get_value()
        value = str(value)
        if not value or value == "initial task":
            value = "<i style='color: #bbb'>--</i>"
        if not is_ajax:
            widget = SpanWdg(id=display_id )
            widget.add_style('display', 'block')
        
        div = SpanWdg()
        # this script locates which elem is to be swapped
        #if self.sobject.has_value(self.attr):
        div.add_class('hand')
        script = ["Table.locate_elem('%s','%s', 'swap');" %(self.sobject.get_search_key(), self.attr)]
        script.append(self.get_refresh_script(show_progress=False))
        div.add_event('onclick', ';'.join(script))

        from .widget_config import WidgetConfig, WidgetConfigView
        if not self.config:
            self.config = WidgetConfigView.get_by_search_type(self.sobject.get_search_type_obj().get_base_key(), self.view)

        # check self.config
        display_handler = self.config.get_display_handler(self.element_name)

        if display_handler:
            # AuxDataWdg allows None for sobject, so self.element could be None
            if not self.element:
                self.element = WidgetConfig.create_widget(display_handler)
                self.element.set_name(self.element_name)
                self.element.set_parent_wdg(self.parent_wdg)
                self.element.preprocess()

            display_options = self.config.get_display_options(self.element_name)
            for key in display_options.keys():
                self.element.set_option(key, display_options.get(key))

            self.element.set_sobjects(self.sobjects)
            # BaseTableElementWdg and AuxDataWdg requires the knowledge of index
            self.element.set_current_index(self.get_current_index())

            div.add(self.element.get_simple_display())
        else:
            div.add(value) 

        widget.add(div)

        return widget

    def get_edit_wdg(self, display_id, value):
        ''' get the editing widget '''
        from .widget_config import WidgetConfig, WidgetConfigView
        config = WidgetConfigView.get_by_search_type(self.sobject.get_search_type_obj().get_base_key(), "edit")
        edit_handler = config.get_display_handler(self.element_name)
        element = Widget()
        width = len(value)
        if edit_handler:
            element = WidgetConfig.create_widget(edit_handler)
            element.set_name(display_id)
            element.set_input_prefix("")
            display_options = config.get_display_options(self.element_name)
            for key in display_options.keys():
                element.set_option(key, display_options.get(key))

            element.set_sobject(self.sobject)
            element.set_value(value)
        else:
            element = TextWdg(display_id)
            element.set_value(value)
            if width > 100:
                width = 100
            element.set_attr('size', width)

        # add OK
        from pyasm.prod.web import ProdIconButtonWdg

        icon = ProdIconButtonWdg('ok')
        cmd = self.get_cmd(display_id) 
        div = cmd.generate_div()

        post_script = [self.get_refresh_script()]

        # that seems a bit long
        caller = WebContainer.get_event_container().get_event_caller(SiteMenuWdg.EVENT_ID)
        post_script.append(caller)
        div.set_post_ajax_script(';'.join(post_script))
        # this script locates which elem is to be updated
        script = ["Table.locate_elem('%s','%s', 'update');" %(self.sobject.get_search_key(), self.attr)]
        script.append(cmd.get_on_script(show_progress=False))
       
        icon.add_event('onclick', ';'.join(script))

        # add Cancel
        cancel = ProdIconButtonWdg('x')
        script[0] = "Table.locate_elem('%s','%s', 'cancel');" %(self.sobject.get_search_key(), self.attr)
        cancel.add_event('onclick', ';'.join(script))

        div_cont = DivWdg(element, css='popup_wdg')
        div_cont.add_style('display','block')
        div_cont.add_style('opacity', '0.7')
        div_cont.add_style("padding: 5 10 10 5")
        div_cont.add(HtmlElement.br(2))
        div_cont.add(icon)
        div_cont.add(cancel)
        div_cont.add(div)
        return div_cont

    def get_cmd(self, display_id):
        ''' get the Ajax Cmd '''
        cmd = AjaxCmd()
        cmd.set_display_id('cmd_%s' %display_id)
        cmd.register_cmd('DynamicTableElementCmd')
        cmd.add_element_name(display_id)
        cmd.add_element_name('skey_DynamicTableElementWdg')
        cmd.add_element_name('attr_DynamicTableElementWdg')
        cmd.add_element_name('update_DynamicTableElementWdg')
        return cmd


class WrapperTableElementWdg(BaseTableElementWdg):
    '''Wrapper class for normal widgets'''
    def __init__(self,name=None, value=None, widget=None):
        self.embedded_widget = widget

    def get_display(self):
        return self.embedded_widget


class ArrayTableElementWdg(BaseTableElementWdg):
    def get_simple_display(self):
        return self.get_display()

    def get_display(self):
        value = self.get_value()
        value = value.strip("||")
        value = value.replace("||", ", ")
        return value

class CheckTableElementWdg(BaseTableElementWdg):
    def get_simple_display(self):
        return self.get_value()

    def get_display(self):
        value = self.get_value()
        if value in ['on', 'True',  'true']:
            return IconWdg("checked", IconWdg.CHECK)
        else:
            return "&nbsp;"



class DateWdg(SimpleTableElementWdg):
    '''Simple date widget that displays the date as Oct 23, 1994'''
    def get_display(self):
        timestamp = self.get_value()
        if timestamp == "":
            return "No date"
        p = re.compile(r'-| |:')
        time_seq = p.split(str(timestamp))
        try:
            time_seq = [int(float(x)) for x in time_seq]
        except ValueError:
            return timestamp
        
        time_seq.extend( [0,1,-1] )

        pattern = self.get_option("pattern")
        if not pattern:
            pattern = "%b %d, %Y"


        return time.strftime(pattern, tuple(time_seq) )

    def get_simple_display(self):
        return self.get_display()



class DateYearTimeWdg(SimpleTableElementWdg):
    '''Simple date widget that displays the date as Oct 23, 1994 - 5:20'''
    def get_display(self):
        timestamp = self.get_value()
        if timestamp:
            timestamp = parser.parse(timestamp)
            return timestamp.strftime("%b %d, %Y - %H:%M")
        else:
            return ""




    def get_simple_display(self):
        return self.get_display()

class DateTimeWdg(SimpleTableElementWdg):
    '''Simple date widget that displays the date as Oct 23 - 5:20'''
    def get_display(self):
        timestamp = self.get_value()
        if timestamp:
            timestamp = parser.parse(timestamp)
            return timestamp.strftime("%b %d - %H:%M")
        else:
            return ""


    def get_simple_display(self):
        return self.get_display()


class UpdateWdg(FunctionalTableElement):

    INSERT_MULTI = 'insert_multi'

    def __init__(self,name=None, value=None):
        super(UpdateWdg, self).__init__(name, value)
        self.iframe_width = 70

    def create_required_columns(self, name):
        return

    def get_title(self):
         
        widget = Widget()
        if self.sobjects:
            sobject = self.sobjects[0]
            if sobject:
                edit = EditLinkWdg( sobject.get_search_type(), 0 )
                edit.set_sobjects( self.sobjects )
                widget.add(edit.get_hidden())

        insert = None
        if self.get_option("insert") == "false":
            return ''


        insert_view = self.get_option("insert_view")
        if not insert_view:
            insert_view = "insert"

        iframe_width = self.get_option("iframe_width")
        if iframe_width:
            try:
                self.set_iframe_width(int(iframe_width))
            except ValueError:
                pass
        
        search_type = None
        if self.search:
            search_type = self.search.get_search_type()
        elif self.sobjects:
            search_type = self.get_current_sobject().get_search_type()
        elif self.parent_wdg:
            search_type = self.parent_wdg.search_type
        
        if search_type:
            insert = InsertLinkWdg(search_type, config_base=insert_view)
            if self.get_option("refresh_mode"):
                insert.set_refresh_mode( self.get_option("refresh_mode") )
            insert.set_id('%s_insert_s'%search_type)
            insert.set_iframe_width(self.iframe_width)
        else:
            insert = StringWdg("UpdateWdg")
        
        widget.add(insert)
        if self.get_option("insert_multi"):
            hidden = HiddenWdg(self.INSERT_MULTI)
            widget.add(hidden) 

            if search_type:
                insert_multi = InsertLinkWdg(search_type, text='Insert Multi', config_base='insert_multi')    
                insert_multi.set_id('%s_insert_m'%search_type)
                insert_multi.add_style('display', 'none')
                widget.add(insert_multi)
            swap = SwapDisplayWdg()
            swap.add_tip('Toggle Insert Mode')
            swap.set_display_widgets('S', 'M')
            script = "swap_display('%s_insert_m','%s_insert_s'); var x=$('%s_insert_m'); if (x.getStyle('display')=='inline') get_elements('insert_multi').set_value('insert_multi'); else get_elements('insert_multi').set_value('')" % (search_type, search_type, search_type)
            swap.add_action_script(script)
            widget.add(swap)
        return widget


    def check_security(self):
        # Check security for update
        security = WebContainer.get_security()
        if self.search != None:
            search_type = self.search.get_search_type()
        elif self.get_current_sobject() != None:
            search_type = self.get_current_sobject().get_search_type()
        elif self.parent_wdg:
            search_type = self.parent_wdg.search_type
        else:
            raise SecurityException()

        if not security.check_access("sobject", search_type, "edit"):
            raise SecurityException("No edit access for [%s]" % search_type)


    def set_iframe_width(self, width):
        self.iframe_width = width

    def get_display(self):
        sobject = self.get_current_sobject()
        if not sobject:
            return ''

        id = sobject.get_id()
        widget = Widget()

        # this option filters by user so that it only appears if the user
        # has their name tagged to it.
        if self.get_option("user_filter") == "true":
            user = WebContainer.get_user_name()
            if sobject.has_value("login"):
                sobject_user = sobject.get_value("login")
                if user != sobject_user:
                    return widget

        config_base = self.get_option("edit_view")
        if not config_base:
            config_base = "edit"

        

        if self.get_option("edit") != "false":
            edit = EditLinkWdg( sobject.get_search_type(), id, config_base=config_base )
            edit.set_iframe_width(self.iframe_width)
            if self.get_option("refresh_mode"):
                edit.set_refresh_mode( self.get_option("refresh_mode") )
            edit.set_sobjects( self.sobjects )
            widget.add(edit) 

        search_type = sobject.get_search_type()
        sobj_code = sobject.get_code()
        sobj_name = sobject.get_name()

        if self.get_option("retire") != "false" and sobject.has_value("s_status"):
            if sobject.get_value("s_status") == "retired":
                retire = ReactivateLinkWdg( search_type, id, sobj_name )
            else:
                retire = RetireLinkWdg( search_type, id, sobj_name )
            widget.add(retire)

        if self.get_option("delete") == "true":
            security = WebContainer.get_security()
            if security.check_access("sobject", search_type, "edit"):
                delete = DeleteLinkWdg( search_type, id, sobj_name, sobject=sobject )
                widget.add(delete)
        return widget
        
class SubmissionLinkTableElement(FunctionalTableElement):

    def get_hidden(self):
        from pyasm.prod.web import BinSelectWdg
        widget = Widget()
        hidden = HiddenWdg(BinSelectWdg.SELECT_NAME)
        widget.add(hidden)
        hidden = HiddenWdg('client_bin_select')
        widget.add(hidden)
        return widget

    def get_display(self):
        sobject = self.get_current_sobject()
        if not sobject or sobject.get_id() == -1:
            return ''
        id = sobject.get_id()
        widget = Widget()
        submit = SubmissionLinkWdg( sobject.get_search_type(), id )
        submit.set_refresh_mode('page')
        widget.add(submit)

        return widget

class RenderLinkTableElement(FunctionalTableElement):

    def get_display(self):
        sobject = self.get_current_sobject()
        if not sobject:
            return ''
        id = sobject.get_id()
        widget = Widget()
        submit = RenderLinkWdg( sobject.get_search_type(), id )
        widget.add(submit)

        return widget




class FileAppendLinkTableElement(FunctionalTableElement):

    def get_display(self):
        sobject = self.get_current_sobject()
        if not sobject:
            return ''
        id = sobject.get_id()
        widget = Widget()
        checkin = FileAppendLinkWdg( sobject.get_search_type(), id )
        widget.add(checkin)

        return widget


class SimpleInfoWdg(BaseTableElementWdg):
    def get_title(self):
        return "Info"

    def get_display(self):
        sobject = self.get_current_sobject()

        columns = "login|description".split("|")

        html = Html()

        for column in columns:
            title = column.replace("_", " ")
            title = title.capitalize()
            value = sobject.get_value(column)
            html.writeln( "%s : %s<br/>" % (title,value) )

        return html.getvalue()



class XmlWdg(BaseTableElementWdg):
    '''Display raw xml data using the <pre> tag'''

    def is_editable(self):
        return True

    def get_width(self):
        return "600px"

    def get_display(self):
        sobject = self.get_current_sobject()
        value = sobject.get_value( self.get_name() )
        value = self.get_value()

        if not isinstance(value, basestring):
            value = jsondumps(value)

        elif value.startswith("zlib:"):
            value = Common.decompress_transaction(value)

        widget = DivWdg()
        widget.add_style("min-width: 300px")
        widget.add_style("width: auto")
        widget.add_style("overflow-x: hidden")
        widget.add_style("overflow-y: auto")
        widget.add_style("max-height: 600px")

        # parse the xml to see if it is valid
        try:
            Xml(string=value)
        except XmlException as e:
          
            widget.add( IconWdg("XML Parse Error", IconWdg.ERROR) )
            span = SpanWdg()
            span.add_style('color: #f44')
            span.add( "Error parsing xml [%s]:" % e.__str__() )
            widget.add(span)

        value = Xml.to_html(value)
        pre = HtmlElement.pre(value)
        pre.add_style("font-size", "1.0em")
        #pre.add_attr("wrap", "true")
        #pre.add_style("white-space", "pre-line")
        widget.add(pre)
        return widget


    def get_text_value(self):
        value = self.get_value()
        return value


    def handle_header(self, th):
        th.add_attr("spt_input_type", "xml")


    def get_simple_display(self):
        return self.get_display()

class WikiElementWdg(BaseTableElementWdg):
    '''Display the value in the database as wiki (not really implemented yet)'''

    def get_display(self):
        sobject = self.get_current_sobject()
        value = sobject.get_value( self.get_name() )

        wiki = WikiUtil()
        value = wiki.convert(value)
        return value

    def get_simple_display(self):
        return self.get_display()

    def is_editable(self):
        return True






class NameWdg(BaseTableElementWdg):
    '''Displays the full name of a person by combining name_first and name_last
    '''
    def get_title(self):
        return "Full Name"


    def get_display(self):
        sobject = self.get_current_sobject()
        first = sobject.get_value("name_first")
        last = sobject.get_value("name_last")
        return first + " " + last



class HiddenRowToggleWdg(FunctionalTableElement):
    '''toggles a hidden row element'''
    OPEN_EVENT_PREFIX = 'open_sesame'
    CLOSE_EVENT_PREFIX = 'close_sesame'
    ON_EVENTS = 'toggle_on_events_'
    OFF_EVENTS = 'toggle_off_events_'


    ARGS_KEYS = {
    'dynamic_class': {
        'description': 'The sub widget to display',
        'type': 'recursive',
        'category': 'SubWidget'
    },
    'icon': {
        'description': "Icon to use",
        'type': 'TextWdg',
        'category': 'Display'
    },
    'icon_tip': {
        'description': "Tip for an icon. If unset, it's based on element name",
        'type': 'TextWdg',
        'category': 'Display'
    }


    }

    def get_args_keys(cls):
        '''external settings which populate the widget'''
        return cls.ARGS_KEYS
    get_args_keys = classmethod(get_args_keys)


    """
    def __init__(self, **kwargs):
      
        self.col_name = kwargs.get('col_name')
        self.is_control = kwargs.get('is_control')
        self.auto_index = kwargs.get('auto_index')
        self.arg_dict = None
        self.name = None
        super(HiddenRowToggleWdg,self).__init__()
    """

    def is_editable(self):
        return False

        
    def init(self):
        self.col_name = None
        self.is_control = False
        self.auto_index = False
        self.arg_dict = None
        if self.auto_index:
            self.current_index = self.generate_unique_id()
            
        self.on_event_name = HiddenRowToggleWdg.OPEN_EVENT_PREFIX
        self.off_event_name = HiddenRowToggleWdg.CLOSE_EVENT_PREFIX  


    def handle_th(self, th, xx=None):

        th.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        var el = bvr.src_el.getElement(".spt_hidden_row_multi");
        spt.toggle_show_hide(el);
        '''
        } ) 

        th.add_behavior( {
        'type': 'hover',
        'cbjs_action_over': '''
        //var el = bvr.src_el.getElement(".spt_hidden_row_multi");
        //spt.show(el);
        ''',
        'cbjs_action_out': '''
        var el = bvr.src_el.getElement(".spt_hidden_row_multi");
        spt.hide(el);
        '''
        } )

    def get_title(self):
        div = DivWdg()
        div.add_class("spt_hidden_row_top")

        title_div = DivWdg()
        div.add(title_div)
        title_div.add(super(HiddenRowToggleWdg,self).get_title())
        title_div.add_style("float: left")

        if self.get_option("multi") == 'false':
            div.add("<br clear='all'/>")
            return div



        multi_div = DivWdg()
        multi_div.add_style("z-index: 150")
        div.add(multi_div)
        multi_div.add_style("position: absolute")
        multi_div.add_style("display: none")
        multi_div.add_style("padding: 3px")
        multi_div.add_class('spt_hidden_row_multi')
        multi_div.add_border()
        multi_div.add_color("background", "background")
        multi_div.add_color("color", "color")
        multi_div.add_style("margin-left: 0px")
        multi_div.add_style("margin-top: 15px")

        multi_div.add("Mutiple open/close:")



        multi_div.add_behavior( {
        'type': 'hover',
        'cbjs_action_over': '''
        spt.show(bvr.src_el);
        ''',
        'cbjs_action_out': '''
        var el = bvr.src_el.getElement(".spt_hidden_row_multi");
        spt.hide(bvr.src_el);
        '''
        } )



        table = Table()
        multi_div.add(table)
        table.add_row()

        icon = IconButtonWdg("Open Selected", IconWdg.TOGGLE_ON)
        icon.add_class("hand")
        table.add_cell(icon)

        # use the col_idx to locate the event names
        icon.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var table = bvr.src_el.getParent(".spt_table");
            var table_id = table.getAttribute("id");
            var rows = spt.dg_table.get_selected(table_id);
            var th = bvr.src_el.getParent(".header_cell_main");
            var src_idx = th.getAttribute("col_idx");
            for (var i=0; i<rows.length; i++) {
                var top = rows[i].getElement('td[col_idx=' + src_idx + ']');
                var event_name = top.getAttribute("spt_on_event_name");
                spt.named_events.fire_event(event_name, {});
            }
            if (rows.length == 0) {
                alert("No rows selected")
            }
            '''
        } )


        icon = IconButtonWdg("Close Selected", IconWdg.TOGGLE_OFF)
        icon.add_class("hand")
        table.add_cell(icon)
        icon.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var table = bvr.src_el.getParent(".spt_table");
            var table_id = table.getAttribute("id");
            var rows = spt.dg_table.get_selected(table_id);
            var th = bvr.src_el.getParent(".header_cell_main");
            var src_idx = th.getAttribute("col_idx");
            for (var i=0; i<rows.length; i++) {
                var top = rows[i].getElement('td[col_idx=' + src_idx + ']');
                var event_name = top.getAttribute("spt_off_event_name");
                spt.named_events.fire_event(event_name, {});
            }
            if (rows.length == 0) {
                alert("No rows selected")
            }
            '''
        } )
        return div
       

    def handle_td(self, td):
        on_name, off_name = self.__get_event_name()
        #td.add_class("spt_notes_sheet")
        td.add_attr("spt_on_event_name", on_name)
        td.add_attr("spt_off_event_name", off_name)
        



    def get_display(self):

        top = DivWdg()

        sobject = self.get_current_sobject()
        if sobject.is_insert():
            top.add_style("opacity: 0.4")
            
            icon = IconWdg("", IconWdg.INFO_CLOSED_SMALL)
            top.add(icon)
            return top

        icon_tip = self.get_option('icon_tip')
        if not icon_tip:
            icon_tip = super(HiddenRowToggleWdg,self).get_title()
        
        icon_tip_on = "Expand %s" % icon_tip
        icon_tip_off = "Hide %s" % icon_tip

        on_name, off_name = self.__get_event_name()
        swap = SwapDisplayWdg(on_name, off_name, icon_tip_on, icon_tip_off)
        icon_name = self.get_option('icon')
        #icon_name = "FILM"
        icon = None
        if icon_name:
            icon = IconWdg(icon_tip, eval("IconWdg.%s" % icon_name))

            action = "spt.toggle_show_hide('hidden_row_%s')" % (self.get_toggle_id())   
            SwapDisplayWdg.create_swap_title(icon, swap, div=None, action_script=action)


            table = Table()
            table.add_row()
            table.add_cell(swap)
            td = table.add_cell(icon)
            icon.add_style("margin-left: -10px")
            top.add(table)
        else:
            top.add(swap)
        
            if self.is_control:
                self.add_stored_events('onclick', swap)
            else:
                action = "spt.toggle_show_hide('hidden_row_%s')" % (self.get_toggle_id())   
                swap.add_action_script(action)
       
        return top
    
    def set_static_content(self, widget):
        self.set_option('static', widget)
    
    # it expects an arg dictionary or key=value string with a '|' delimiter
    def set_dynamic_content(self, widget_class, arg_dict):
        assert isinstance(widget_class, basestring)
        self.set_option('dynamic', widget_class)   
        self.arg_dict = arg_dict

    def get_hidden_row_wdg(self):
        # new and dynamic_class make use of get_widget
        # and not the deprecated Ajax class
        dynamic_class = self.get_option("dynamic_class")
        new = self.get_option("new")
        
        # add in an empty row
        dynamic = self.get_option("dynamic")
        static = self.get_option("static")
        div = None
        if new:
            display_id = Widget.generate_unique_id( base='new_display', \
                    wdg='DyanmicLoaderWdg', is_random=True)
            div = DivWdg(id = display_id)
            parent_key = SearchKey.get_by_sobject(  self.get_current_sobject() )

            options = self.options.copy()
            # remove the unnecesary new, title_icon key
            options.pop('new')
            if "title_icon" in options:
                options.pop('title_icon')
            options['search_key'] = parent_key
            on_script = "spt.panel.load('%s', '%s', bvr.args, {}, false);"%(display_id, new)

            
            # set up a listener
            event = WebContainer.get_event_container()
            on_name, off_name = self.__get_event_name()

            off_script = ';'
            sobject = self.get_current_sobject()
            if sobject:
                search_type = sobject.get_search_type()
                search_id = sobject.get_id()
            args =  {'search_type': search_type, 
                        'search_id': search_id,
                        'pipeline_code': sobject.get_value('pipeline_code', no_exception=True)
                     }
            args.update(options)
            behavior = {
                'type': 'listen',
                'event_name': on_name,
                'cbjs_preaction': 'var tmp_tr = bvr.src_el.getParent("tr"); if( tmp_tr ) { spt.show( tmp_tr ); }',
                'cbjs_action': on_script,
                'args': args
            }
            div.add_behavior( behavior )
            behavior = {
                'type': 'listen',
                'event_name': off_name,
                'cbjs_preaction': 'var tmp_tr = bvr.src_el.getParent("tr"); if( tmp_tr ) { spt.hide( tmp_tr ); }',
                'cbjs_action': off_script
            }
            div.add_behavior( behavior )
            
        elif dynamic != "":
            assert static == ""
            ajax = AjaxLoader()
            div = ajax.generate_div()
            
            if self.arg_dict != None:
                ajax.set_load_class(dynamic, self.arg_dict)
                
            else:    
                # get search object info (this is meant for generic history 
                # search with config file)
                sobject = self.get_current_sobject()
                if sobject != None:
                    search_type = sobject.get_search_type()
                    search_id = sobject.get_id()
    
                    # get dynamic class option 
                    ajax.set_load_class(dynamic, "search_type=%s||search_id=%s" % (search_type, search_id) )
            
            # set up a listener
            event = WebContainer.get_event_container()
            on_name, off_name = self.__get_event_name()
            #event.add_listener(on_name, ajax.get_on_script())
            #event.add_listener(off_name, ajax.get_off_script())

            on_script = ajax.get_on_script()
            off_script = ajax.get_off_script()

            behavior = {
                'type': 'listen',
                'event_name': on_name,
                'cbjs_preaction': 'var tmp_tr = bvr.src_el.getParent("tr"); if( tmp_tr ) { spt.show( tmp_tr ); }',
                'cbjs_action': on_script
            }
            div.add_behavior( behavior )
            behavior = {
                'type': 'listen',
                'event_name': off_name,
                'cbjs_preaction': 'var tmp_tr = bvr.src_el.getParent("tr"); if( tmp_tr ) { spt.hide( tmp_tr ); }',
                'cbjs_action': off_script
            }
            div.add_behavior( behavior )


        # test a new dynamic
        elif dynamic_class != "":
            assert static == ""
            div = DivWdg()
            div.add_class("spt_hidden_row_top")
            #div.add_class(".spt_table_div_hidden")

            # set up a listener
            event = WebContainer.get_event_container()
            on_name, off_name = self.__get_event_name()


            parent_key = SearchKey.get_by_sobject( self.get_current_sobject(), use_id=True )
            options = self.options.copy()
            options['search_key'] = parent_key
                

            off_script = ""

            behavior = {
                'type': 'listen',
                'event_name': on_name,
                'options': options,
                'class_name': dynamic_class, 
                'cbjs_preaction': '''
                var tmp_tr = bvr.src_el.getParent("tr");
                if( tmp_tr ) {
                    spt.show( tmp_tr );
                }
                ''',
                'cbjs_action': '''
                spt.panel.is_refreshing = true;
                spt.panel.show_progress(bvr.src_el);
                var kwargs = bvr.options;
                kwargs.__hidden__ = 'true';
                setTimeout( function() {
                    spt.panel.load(bvr.src_el, bvr.class_name, kwargs, {}, false);
                    spt.panel.is_refreshing = false;
                }, 10 );
                '''
            }
            div.add_behavior( behavior )
            behavior = {
                'type': 'listen',
                'event_name': off_name,
                'cbjs_preaction': 'var tmp_tr = bvr.src_el.getParent("tr"); if( tmp_tr ) { spt.hide( tmp_tr ); }',
                'cbjs_action': off_script
            }
            div.add_behavior( behavior )



        elif static != "":
            # Note: at the moment, this requires a widget with no arguments
            
            if isinstance(static, basestring):
                div = eval(static)
            else:
                div = static
            if self.auto_index:
                static.set_id(self.get_toggle_id())
        else:
            div = DivWdg()
            
        #div.add_style("width: 97%")
        if WebContainer.get_web().is_IE():
            div.add_style("margin-left: 30px")
        else:
            div.add_style("margin-top: 0px")
            div.add_style("margin-left: 29px")
            div.add_style("margin-bottom: -2px")
            div.add_style("margin-right: -2px")
        return div
    
    # add the stored events to the master control
    def add_stored_events(self, event_type, swap_wdg, on_event_list=None, off_event_list=None):
        
        on_wdg = swap_wdg.get_on_widget()
        off_wdg = swap_wdg.get_off_widget()
                
        if on_event_list == None:
            on_event_list = self._get_toggle_events(True)
            
        if off_event_list == None:
            off_event_list = self._get_toggle_events(False)
            
        for item in on_event_list:
            on_wdg.add_event_caller(event_type, item)
        
        for item in off_event_list:
            off_wdg.add_event_caller(event_type, item)    
            
    # get a unique toggle id        
    def get_toggle_id(self):
        if self.col_name == None:
            self.col_name = self.generate_unique_id('col', is_random=True)
        
        return '%s_%s' %(self.col_name, self.current_index)
    
    # store the on and off event in a container
    def store_event(self):
        on_event_name, off_event_name = self.__get_event_name()
       
        self._store_toggle_event(on_event_name, True)
        self._store_toggle_event(off_event_name, False)
            
    def _store_toggle_event(self, event_name, is_on):
        
        key = self.__get_key(is_on)
        event_list = Container.get(key)
        if event_list == None:
            event_list = []
            Container.put(key, event_list)
        event_list.append(event_name)
       
        
    # get all the stored toggle events ( on or off )
    # preferrably this should be called after all the events desired have been stored
    def _get_toggle_events(self, is_on):
        list = Container.get(self.__get_key(is_on))
        if list == None:
            return []
        else:
            return list
        
    # get the key event name which maps to various listeners    
    def __get_key(self, is_on):
        if is_on:
            key = HiddenRowToggleWdg.ON_EVENTS
        else:
            key = HiddenRowToggleWdg.OFF_EVENTS
    
        if self.col_name != None: 
            key += self.col_name
            
        return key
    
    def __get_event_name(self):
        on_name = "%s_%s" % (self.on_event_name, self.get_toggle_id())
        off_name = "%s_%s" % (self.off_event_name, self.get_toggle_id())
                   
        return on_name, off_name
    
    
    
class GroupTableElement(BaseTableElementWdg):
    '''shows a grouping of a particular sobject'''

    def get_title(self):
        return "&nbsp;&nbsp;"

    def is_simple_viewable(self):
        return False

    def _is_new_item(self, prev_sobj, sobj):
        '''check if this task belong to a new parent ''' 
        if not prev_sobj:
            return True

        prev_value = prev_sobj.get_value(self.column)
        sobj_value = sobj.get_value(self.column)

        # compare search key here 
        if prev_value == sobj_value:
            return False
        else:
            return True

 
    def add_prev_row(self, table, prev_sobj):

        web = WebContainer.get_web()
        self.column = self.get_option("column")
        if not self.column:
            self.column = web.get_form_value(self.parent_wdg.get_order_by_id() )


        sobject = self.get_current_sobject()

        if self._is_new_item(prev_sobj, sobject):
            widget = Widget()
            value = sobject.get_value(self.column)
            span = SpanWdg(value)
            span.add_style("font-weight: bold")
            span.add_style("font-size: 1.1em")
            #span.add_style("color: #f99")

            widget.add( span )

            table.add_row()
            tr, td = table.add_row_cell(widget)

            td.add_class("task_header_row")

           

    
    
class SObjectAttachTableElement(BaseTableElementWdg):
    '''shows which sobject this sobject is attached to'''

    def init(self):
        self.last_search_key = None
        self.swaps = []
        self.row_ids = []
        self.empty = True


    def get_simple_display(self):
        sobject = self.get_current_sobject()
        parent = sobject.get_parent()
        return parent.get_code()
        

    def preprocess(self):
        sobject = self.get_current_sobject()
        if not sobject:
            self.ref_sobj_dict = {}
            return
        search_ids = SObject.get_values(self.sobjects, 'search_id', unique=True)
        search_types = SObject.get_values(self.sobjects, 'search_type', unique=True)
        # if there is more than one search_type, then go get each parent
        # individually
        if search_types > 1:
            ref_sobjs = []
            for tmp_sobj in self.sobjects:
                try:
                    ref_sobj = tmp_sobj.get_parent()
                    if ref_sobj:
                        ref_sobjs.append(ref_sobj)
                    else:
                        warning = "Dangling reference: %s" % tmp_sobj.get_search_key()
                        Environment.add_warning(warning, warning)
                except SearchException as e:
                    # skips unknown search_type/project
                    print(e.__str__())
                    pass

        else:
            search_type = sobject.get_value("search_type")
            ref_sobjs = []
            try:
                ref_sobjs = Search.get_by_id(search_type, search_ids)
            except SearchException as e:
                # skips unknown search_type/project
                print(e.__str__())
                pass

        # TODO: None defaults to search_key, should be empty
        self.ref_sobj_dict = SObject.get_dict(ref_sobjs, None)

        # when drawn as part of a TbodyWdg, we want to disable the calculation
        # of most things so that it will not try to display a prev row
        if self.get_option('disable') == 'true':
            self.ref_sobj_dict = None
            self.empty = True
  
        self.is_preprocessed = True

    def handle_td(self, td):
        td.add_class("task_spacer_column")
        td.add_style("font-weight: bold")
        if self.empty:
            td.add_style("border-top: 0px")

    def _is_new_item(self, prev_sobj, sobj):
        '''check if this task belong to a new parent ''' 
        if not prev_sobj:
            return True
        prev_ref_sobj = self.get_ref_obj(prev_sobj.get_value('search_type'), \
                prev_sobj.get_value('search_id'))
        ref_sobj = self.get_ref_obj(sobj.get_value('search_type'), \
                sobj.get_value('search_id'))
             
        if not prev_ref_sobj or not ref_sobj:
            return False
        # compare search key here 
        if prev_ref_sobj.get_search_key() == ref_sobj.get_search_key():
            return False
        else:
            return True



    def get_redirect_wdg(self, sobject):
        # redirect
        from icon_wdg import IconButtonWdg
        from tab_wdg import TabWdg
        button = IconButtonWdg("Jump", icon=IconWdg.JUMP)
        base_search_type = sobject.get_base_search_type()
        if base_search_type == 'prod/asset':
            location = { "main_tab": "Asset Pipeline", "asset_pipeline_tab": "Artist (3D Assets)" }
        elif base_search_type == 'flash/asset':
            location = { "main_tab": "Asset Pipeline", "asset_pipeline_tab": "Artist (Asset)" }
        elif base_search_type == 'flash/shot':
            location = { "main_tab": "Scene Pipeline", "shot_pipeline_tab": "Scene" }
        else:
            location = { "main_tab": "Shot Pipeline", "shot_pipeline_tab": "Artist (Shots)" }

        script = TabWdg.get_redirect_script(location, is_child=False)

        context = WebContainer.get_web().get_context_name()
        project_code = sobject.get_project_code()
        if context != project_code:
            script = "%s;f=document.form;f.method='GET';f.is_form_submitted.value='init';f.action='/tactic/%s';f.submit()" % (script, project_code)
            button.add_event("onclick", script)
        else:
            
            button.add_event("onclick", "%s;document.form.submit(); "% script)

        span = SpanWdg(button)
        return span


           
    def add_prev_row(self, table, prev_sobj):
        sobject = self.get_current_sobject()
       
        if self._is_new_item(prev_sobj, sobject):
            table.close_tbody() 
            widget = Widget()
           
            label = "Attach"
            label_option = self.get_option("label")
            if label_option:
                label = label_option 
            
            search_type = sobject.get_value("search_type")
            search_id = sobject.get_value("search_id")
            search_key = "%s|%s" % (search_type, search_id)
           
            ref_sobj = self.get_ref_obj(sobject.get_value('search_type'), \
                    sobject.get_value('search_id')) 
            
            if not ref_sobj:
                return "Undetermined parent"


            # this only works because we call get_buffer_display() at the bottom
            web_state = WebState.get()
            web_state.add_state("edit|parent", search_key)

            if self.get_option('insert') != 'false':
                insert = InsertLinkWdg("sthpw/task", long=False, text=label)
                insert.add_style('float: left')
                widget.add( insert )
           
            from pyasm.widget import ThumbWdg
            thumb = ThumbWdg()
            thumb.set_icon_size(40)
            thumb.set_sobject(ref_sobj)
            widget.add(FloatDivWdg(thumb))
            name_span = FloatDivWdg(ref_sobj.get_code(), css='larger')
            name_span.add_style('margin-left: 20px')
            widget.add(name_span)

            name_span.add( self.get_redirect_wdg(ref_sobj) )


            if ref_sobj.has_value("name"):
                name_span.add( " - " )
                name_span.add( ref_sobj.get_value("name") )

            status = ref_sobj.get_value("status", no_exception=True)
            if status:
                widget.add(SpanWdg('&nbsp;', 'small'))
                widget.add( SpanWdg("(status:%s)" % ref_sobj.get_value("status")) )
            # FIXME: not sure about the layout here
            if ref_sobj.has_value("pipeline_code"):
                pipeline_code = ref_sobj.get_value("pipeline_code")
                widget.add(SpanWdg('&nbsp;', 'small'))
                widget.add( SpanWdg("(pipeline:%s)" % pipeline_code ) )
            
            
            if ref_sobj.has_value("description"):
                widget.add(SpanWdg('&nbsp;', 'small'))
                description_wdg = ExpandableTextWdg("description")
                description_wdg.set_max_length(200)
                description_wdg.set_sobject(ref_sobj)
                widget.add( description_wdg )
                
            content = widget.get_buffer_display()

            # clear this web state set earlier so future widgets don't inherit
            # it.
            web_state.add_state("edit|parent", "")


            # add a swap display
            swap = SwapDisplayWdg()
            swap.add_style('float: left')
            self.swaps.insert(0, swap)
            
            swap.set_display_widgets(IconWdg(icon=IconWdg.INFO_OPEN), IconWdg(icon=IconWdg.INFO_CLOSED))


            if self.get_option("status_history") == "true":
                tr = table.add_row()
                td = table.add_cell(swap)
                td.set_attr("colspan", "6")
            else:
                tr, td = table.add_row_cell(swap)

            td.add_class("task_header_row")
            td.add(content)

            if self.get_option("status_history") == "true":
                from gantt_wdg import StatusHistoryGanttWdg
                gantt_wdg = StatusHistoryGanttWdg()
                gantt_wdg.get_prefs()
                gantt_wdg.set_sobject(sobject.get_parent())
                td = table.add_cell(gantt_wdg)
                td.add_class("task_header_row")


            # insert the tbody here
            tbody = table.add_tbody()
            tbody.set_id("table_tbody_%s" % sobject.get_value('search_id'))
            
        
    def get_ref_obj(self, search_type, search_id):
        key = "%s|%s" % (search_type, search_id)
        ref_sobject = self.ref_sobj_dict.get(str(key))
        if not ref_sobject:
            try:
                ref_sobject = Search.get_by_id(search_type, search_id)
                if not ref_sobject:
                    return None
            except SearchException as e:
                print(e.__str__())
                return None

        return ref_sobject
            
    def get_display(self):

        if not self.ref_sobj_dict:
            return None
        label = "Attach"
        label_option = self.get_option("label")
        if label_option:
            label = label_option 
      
        from layout_wdg import TableWdg
        
        sobject = self.get_current_sobject()
        
        search_type = sobject.get_value("search_type")
        search_id = sobject.get_value("search_id")
        search_key = "%s|%s" % (search_type, search_id)

        # get row_id from table
        table_row_ids = self.parent_wdg.row_ids
        row_id = table_row_ids.get(sobject.get_search_key())
        if self.last_search_key and self.last_search_key == search_key:
            self.empty = True
            self.row_ids.append(row_id)
            # if it is the last one
            if self.get_current_index() == len(self.sobjects)-1:
                self._add_action_script()  
        else:
            self.empty = False
            if self.last_search_key:
                self._add_action_script() 

            self.last_search_key = search_key
            self.row_ids = [row_id]
            if self.get_current_index() == len(self.sobjects)-1:
                self._add_action_script()  

        return "&nbsp;"
      

    def _add_action_script(self):
        if not self.swaps:
            return
        swap = self.swaps.pop()
        swap.add_action_script("set_display_off('%s')" %"','".join(self.row_ids), \
                "set_display_on('%s')" %"','".join(self.row_ids))





class TableAddWdg(BaseTableElementWdg):

    def get_title(self):
        self.total_cost = 0.0
        self.total_hours = 0.0
        return super(TableAddWdg,self).get_title()


    def get_display(self):
        sobject = self.get_current_sobject()
        value = sobject.get_value(self.name)

        assigned = sobject.get_value("assigned")
        if assigned == "remko":
            rate = 50.0
        else:
            rate = 35.0

        if value != "":
            self.total_hours += float(value)
            self.total_cost += ( float(value) * rate )

        return value


    def get_bottom(self):
        return "%s hours ($%0.2f)" % (self.total_hours, self.total_cost)



class CheckboxColWdg(FunctionalTableElement):
    '''widget to display a checkbox in the column'''
    
    def set_cb_name(self):
        cb_name = self.name
        if not cb_name:
            cb_name = self.get_option("cb_name")
        if cb_name:
            return cb_name
        raise WidgetException("Every CheckboxColWdg should have a unique name,\
                not @name defined in <sobject>-conf.xml")
  
    def get_title(self):
        self.set_cb_name()
        widget = CheckboxWdg()
        widget.add_event("onclick", \
            "var a=get_elements('%s');a.toggle_all(this);" %(self.name))
        return widget
   
    def get_extra_attrs(self):
        return []

    def get_columns(self):
        '''can override this to return a list \
           of sobject's column names as identifier for value. Otherwise 
           search_key is used 
        '''
        return []
   
    def get_sobject(self):
        return self.get_current_sobject()
   

    def get_display(self):
        self.sobject = self.get_sobject()
        self.set_cb_name()
        widget = CheckboxWdg(self.name)

        if self.get_option("persist_on_submit") == "true":
            widget.set_persist_on_submit()

        if self.get_columns():
            cb_value = []
            for col in self.get_columns():
                cb_value.append(str(self.sobject.get_value(col)))
            widget.set_option('value', '|'.join(cb_value))    
        else:
            widget.set_option('value', self.sobject.get_search_key())
        extra_attrs = self.get_extra_attrs()
        if extra_attrs:
            for attr, sobj_attr in extra_attrs:
                widget.set_option(attr, self.sobject.get_value(sobj_attr))
                
        return widget


class EditCheckboxWdg(CheckboxColWdg):
    '''widget to display a checkbox in the column with selectiall control
        This one is used for the edit-all function'''
    
    CB_NAME = 'sthpw_edit'
    def set_cb_name(self):
        self.name = self.CB_NAME

    def get_columns(self):
        return ['id']

class ExpandableTextWdg(BaseTableElementWdg):
    ''' a widget that expands when the user clicks on the swap arrow '''
    MAX_LENGTH = 40
    PREF_MAX_LENGTH = "max_text_length"
      
    def init(self):
        self.max_length_txt = None
        self.id = None

    def is_editable(self):
        return True
 
        
    def get_prefs(self):
        search_type = None
        if not self.id:
            if self.parent_wdg:
                search_type = self.parent_wdg.search_type
                self.id = '%s_%s' %(search_type, self.PREF_MAX_LENGTH)
            else:
                self.id = self.PREF_MAX_LENGTH
        
        self.max_length_txt = FilterTextWdg(self.id, 'Max length: ', css='small')
        self.max_length_txt.set_unit('chars')
       
        self.max_length_txt.set_option('size','2')
        self.max_length_txt.set_option('default', self.MAX_LENGTH)
        return self.max_length_txt
     
    
    def set_id(self, id):
        ''' this sets the id for the prefs textbox'''
        self.id = id

    def set_max_length(self, length):
        ''' this is used when prefs is not used '''
        self.set_option(self.PREF_MAX_LENGTH, length)
        
    def get_display(self):
        
        self.text = self.get_value()
        max_length = self.MAX_LENGTH
        
        pref_length = ''

        # if a pref widget is drawn, use it, otherwise, use the display option
        # or if nothing is found, use the default
        if self.max_length_txt:
            pref_length = self.max_length_txt.get_value()
       
        # match a number
        if re.match('\d+', str(pref_length)):
            max_length = int(pref_length)
        elif self.get_option(self.PREF_MAX_LENGTH):
            max_length = int(self.get_option(self.PREF_MAX_LENGTH))
       
        widget = Widget()

        if len(self.text) > max_length:
            widget.add(self.text[0:max_length]) 
            more_desc = DivWdg(self.text[max_length:], css='hidden')
            more_desc.add_style('display','none')
            more_desc_id = more_desc.generate_unique_id('fl_desc')
            more_desc.set_id(more_desc_id)
            swap = SwapDisplayWdg(widget.generate_unique_id('expand'), \
                widget.generate_unique_id('collapse'))
            swap.add_action_script("set_display_on('%s');" \
                % more_desc_id, "set_display_off('%s')" % more_desc_id)
           
            icon1 = IconWdg('open', IconWdg.INFO_CLOSED_SMALL)
            icon2 = IconWdg('close', IconWdg.INFO_OPEN_SMALL)
            swap.set_display_widgets(icon1, icon2)

            widget.add(SpanWdg(swap, css='small')) 
            widget.add(more_desc)
            
        else:
            widget.add(self.text)

        return widget

class AuxDataWdg(BaseTableElementWdg):
    ''' a widget that assumes having its aux data, a list of dict, set '''
     
   
    def get_display(self):
        aux_data = self.get_current_aux_data()
        
        if aux_data:
            return aux_data.get(self.name)
        else:
            return ''

    def get_simple_display(self):
        return self.get_display()

class SearchTypeElementWdg(BaseTableElementWdg):
    '''display the title of the search type rather than the confusing string'''

    def is_editable(self):
        return True
    
    def preprocess(self):
        from pyasm.biz import Note
        self.info = {}
    
        submission_id_list = []
        search_type = ''
        for sobject in self.sobjects:
            if not isinstance(sobject, Note):
                continue
            if sobject.get_value('search_type').startswith('prod/submission'):
                submission_id_list.append(sobject.get_value('search_id'))
                search_type = sobject.get_value('search_type')
                
        submission_id_list = sorted(set(submission_id_list))
        submissions = Search.get_by_id(search_type, submission_id_list)
        self.info = SObject.get_dict(submissions)
        
        from .file_wdg import ThumbWdg
        self.thumb = ThumbWdg()
        self.thumb.set_show_filename(True)
        self.thumb.set_icon_size(30)
        self.thumb.set_image_link_order(['main','web'])
        self.thumb.set_sobjects(submissions)
        self.thumb.preprocess()
            
    
    def get_display(self):
        sobject = self.get_current_sobject()
        value = sobject.get_value(self.get_name())
        widget = Widget()
        thumb = None
        try:
            search_type = SearchType.get(value)
            title = "%s" % (search_type.get_title())
            if sobject.get_value('search_type').startswith('prod/submission')\
                    and self.get_option('filename')=='true':
                id = sobject.get_value('search_id')
                parent = self.info.get(str(id))
                self.thumb.set_sobject(parent)
                thumb = self.thumb
                

        except SearchException:
            title = "--"
        widget.add(title)
        if thumb:
            widget.add(thumb.get_display())
        return widget



class PublishTableElement(BaseTableElementWdg):
    ''' Publish link for files predefined or arbitrary '''

    def get_title(self):
        option = self.get_option('multi_publish')
        if option and self.parent_wdg:
            search_type = self.parent_wdg.search_type
            publish_link = PublishLinkWdg(search_type, -1,\
                icon=IconWdg.PUBLISH_MULTI,  config_base='multi_publish', text='Multi Publish')
            publish_link.set_iframe_width(70)
            return publish_link
        else:
            return super(PublishTableElement, self).get_title()
        
    def get_display(self):
        sobject = self.get_current_sobject()
        if sobject:
            publish_link = PublishLinkWdg(sobject.get_search_type(), sobject.get_id())
            publish_link.set_iframe_width(70)
            return publish_link
        else:
            return ''




class SObjectLinkElementWdg(BaseTableElementWdg):
    def get_display(self):
        sobject = self.get_current_sobject()
        search_type = sobject.get_base_search_type()
        search_id = sobject.get_id()
        view = self.get_option("view")
        action = self.get_option("action")
        
        edit = EditLinkWdg( search_type, search_id, config_base=view, action=action )
        return edit



class SObjectExplorerWdg(BaseTableElementWdg):
    def get_title(self):
        widget = Widget()
        return widget

    def get_display(self):
        # explore button
        sobject = self.get_current_sobject()
        snapshot = Snapshot.get_latest_by_sobject(sobject, "publish")
        if not snapshot:
            return "&nbsp;"
        dir = snapshot.get_client_lib_dir(file_type='main')
        open_button = IconButtonWdg( "Explore: %s" % dir, IconWdg.LOAD, False)
        open_button.add_event("onclick", "var applet = spt.Applet.get(); applet.open_explorer('%s')" % dir)
        open_button.add_class('small')
        return open_button


